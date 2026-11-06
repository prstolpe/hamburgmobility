"""Soll junction type and cyclist treatment per junction (prompts/20_junctions.md, design_rules.yaml `junctions`).

Pure functions; pipeline/c07_junctions.py builds the junctions from the network and calls them.

- `category_pair`: through road + highest other road (J-M-04, as N6 in rules.yaml); a standalone cycle path counts
  as the second road if no other road meets the through road.
- `decide`: decision table J-01..J-11 in the order J-M-05, conditions evaluated with pipeline/lib/expr.py (Kleene
  logic for missing values), fallback J-M-05.fallback_if.
- `treatments`: JC-01..JC-05 from their applies_to clauses.
- `ist_result`: Ist vs Soll via J-M-06.ist_check.
"""

import re
from dataclasses import dataclass, field
from typing import Any

from config.schema.cycling_model import CYCLE_CATEGORIES, NO_CYCLE_CATEGORY
from config.schema.design_model import TYPE_KEYS, DesignRuleSet
from pipeline.lib import expr

CYCLE_PATH = "cycle_path"
ANY = "any"
CYCLE_STREET = "cycle_street"
# Rank of cycle categories, highest first (cycling_rules.yaml cycle_categories order).
CYCLE_RANK = {"RSV": 4, "HAUPT": 3, "BASIS": 2, "ERSCHL": 1, NO_CYCLE_CATEGORY: 0}
CONFIDENCE = ("high", "medium", "low")
_SIDE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*(?:\(([^)]*)\))?\s*$")


@dataclass(frozen=True)
class Side:
    base: str                 # road category, cycle_path or any
    cycle_cats: frozenset     # qualifier: the leg must carry one of these cycle categories
    facility: str | None      # qualifier: the leg must have this Soll facility (cycle_street)


@dataclass(frozen=True)
class Row:
    id: str
    tram: bool                # 'any with tram'
    sides: tuple              # two Side objects (empty for tram rows)
    spec: dict                # if/then/else_if/else_then/otherwise/fallback (after same_as)
    same_as: str | None


@dataclass
class JunctionParams:
    rows: dict[str, Row]
    order: list[str]
    thresholds: dict[str, float]
    rank: dict[str, int]              # road category -> rank (0 = highest), N6.category_rank
    alias: dict[str, str]
    on_unknown: str
    fallback_types: frozenset
    fallback_cond: Any
    near_threshold: float
    treatments: list[dict]
    ist_check: dict[str, dict]
    types: list[str]
    method: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def from_rules(cls, design: DesignRuleSet, rules) -> "JunctionParams":
        j = design.junctions
        thresholds = {k: float(v["value"]) for k, v in j.thresholds.items()}
        raw = {r.id: r for r in j.decision_table.rows}
        rows = {}
        for rid, r in raw.items():
            src = raw[r.same_as] if r.same_as else r
            spec = {"if": src.if_, "else_if": src.else_if, **{k: (src.model_extra or {}).get(k) for k in TYPE_KEYS}}
            spec = {k: (_compile(v, thresholds) if k in ("if", "else_if") and v else v) for k, v in spec.items()}
            rows[rid] = Row(rid, *_parse_legs(r.legs), spec=spec, same_as=r.same_as)
        m05 = j.method_rule("J-M-05")
        n6 = rules.coherence_rule("N6")
        near = None
        for p in rules.classification_policy:
            if "near_threshold" in p.thresholds:
                near = p.thresholds["near_threshold"].value
        return cls(
            rows=rows, order=list(m05["evaluation_order"]), thresholds=thresholds,
            rank={c: i for i, c in enumerate(n6.category_rank)}, alias=dict(j.method_rule("J-M-04")["category_alias"]),
            on_unknown=m05["on_unknown"], fallback_types=frozenset(m05["fallback_if"]["types"]),
            fallback_cond=_compile(m05["fallback_if"]["condition"], thresholds), near_threshold=float(near),
            treatments=list(j.cyclist_treatment), ist_check=j.method_rule("J-M-06")["ist_check"], types=list(j.types),
            method={r["id"]: r for r in j.method})


def _compile(cond: str, thresholds: dict):
    """Condition with bare threshold names -> expr AST with thresholds.<name> references."""
    text = re.sub(r"\b(" + "|".join(map(re.escape, thresholds)) + r")\b", r"thresholds.\1", cond)
    return expr.parse(text)


def _parse_legs(text: str) -> tuple[bool, tuple]:
    if text.strip() == "any with tram":
        return True, ()
    sides = []
    for part in text.split("+"):
        m = _SIDE.match(part)
        if not m:
            raise ValueError(f"legs: cannot parse {text!r}")
        base, qual = m.group(1), [q.strip() for q in (m.group(2) or "").split("|") if q.strip()]
        cats = frozenset(q for q in qual if q in CYCLE_CATEGORIES)
        fac = next((q for q in qual if q not in CYCLE_CATEGORIES), None)
        sides.append(Side(base, cats, fac))
    if len(sides) != 2:
        raise ValueError(f"legs: expected two sides in {text!r}")
    return False, tuple(sides)


# --- legs and category pair ------------------------------------------------------------------------------------


def leg_cat(leg: dict, p: JunctionParams) -> str:
    cat = leg["cat"]
    return p.alias.get(cat, cat)


def _cycle_cat(leg: dict) -> str:
    c = leg.get("cycle_cat")
    return c if c in CYCLE_RANK else NO_CYCLE_CATEGORY


def category_pair(legs: list[dict], p: JunctionParams) -> tuple[tuple[str, str] | None, list[str]]:
    """(through road, second road) after category_alias; flags category_alias, cycle_path_ignored, no_road_leg."""
    flags = []
    if any(leg["cat"] in p.alias for leg in legs):
        flags.append("category_alias")
    roads = sorted((leg_cat(leg, p) for leg in legs if leg["cat"] != CYCLE_PATH and leg_cat(leg, p) in p.rank),
                   key=p.rank.__getitem__)
    has_path = any(leg["cat"] == CYCLE_PATH for leg in legs)
    if not roads:
        return None, flags + ["no_road_leg"]
    top, rest = roads[0], list(roads)
    for _ in range(2):
        if top in rest:
            rest.remove(top)
    if rest:
        if has_path:
            flags.append("cycle_path_ignored")
        return (top, rest[0]), flags
    if has_path:
        return (top, CYCLE_PATH), flags
    return (top, top), flags


def crossing_legs(legs: list[dict], pair: tuple[str, str], p: JunctionParams) -> list[dict]:
    """Legs outside the through road: drop two legs of the top category (those with the lowest cycle category)."""
    top = pair[0]
    through = sorted((i for i, leg in enumerate(legs) if leg["cat"] != CYCLE_PATH and leg_cat(leg, p) == top),
                     key=lambda i: CYCLE_RANK[_cycle_cat(legs[i])])[:2]
    return [leg for i, leg in enumerate(legs) if i not in through]


def _side_matches(side: Side, cat: str, legs: list[dict], p: JunctionParams) -> bool:
    if side.base != ANY and side.base != cat:
        return False
    if not side.cycle_cats and side.facility is None:
        return True
    pool = [leg for leg in legs if side.base == ANY or
            (leg["cat"] == CYCLE_PATH if cat == CYCLE_PATH else leg["cat"] != CYCLE_PATH and leg_cat(leg, p) == cat)]
    return any((not side.cycle_cats or _cycle_cat(leg) in side.cycle_cats) and
               (side.facility is None or leg.get("facility") == side.facility) for leg in pool)


def row_matches(row: Row, pair: tuple[str, str], legs: list[dict], tram: bool, p: JunctionParams) -> bool:
    if row.tram:
        return bool(tram)
    a, b = row.sides
    return ((_side_matches(a, pair[0], legs, p) and _side_matches(b, pair[1], legs, p)) or
            (_side_matches(a, pair[1], legs, p) and _side_matches(b, pair[0], legs, p)))


# --- decision ----------------------------------------------------------------------------------------------------


def _ctx(values: dict, p: JunctionParams) -> expr.Context:
    return expr.Context(values, lambda ref: p.thresholds[ref.split(".", 1)[1]], p.near_threshold)


def _eval(node, values: dict, p: JunctionParams) -> tuple[bool | None, int, dict]:
    ctx = _ctx(values, p)
    r = expr.evaluate(node, ctx)
    v = None if r.value is None else bool(r.value)
    return v, r.confidence, {k: expr.clean_value(x) for k, x in ctx.used.items()}


def decide(props: dict, p: JunctionParams) -> dict:
    """Soll junction type for one junction.

    props: legs [{cat, cycle_cat, facility}], entering_dtv_sum, space_radius_m, tram_present, signal_present_ist,
    optional flags (list) from building the junction (dtv_partial, dtv_unknown, space_unknown ...).
    """
    legs = props["legs"]
    flags = list(props.get("flags") or [])
    values = {"entering_dtv_sum": props.get("entering_dtv_sum"), "space_radius_m": props.get("space_radius_m"),
              "tram_present": bool(props.get("tram_present")), "signal_present_ist": props.get("signal_present_ist"),
              "legs_count": len(legs)}
    pair, pflags = category_pair(legs, p)
    flags += pflags
    trace: list[dict] = [{"id": "J-M-04", "passed": pair is not None, "result": list(pair) if pair else None,
                          "values": {"legs": [[leg["cat"], _cycle_cat(leg), leg.get("facility")] for leg in legs]}}]
    out = {"pair": pair, "junction_type_soll": None, "rule_trace_junction": trace, "conflict_flags": flags,
           "rule_id": None, "confidence": "low"}
    if pair is None:
        return out
    tram = values["tram_present"]
    conf = expr.HIGH
    for rid in p.order:
        row = p.rows[rid]
        if not row_matches(row, pair, legs, tram, p):
            trace.append({"id": rid, "passed": False, "result": None, "values": {}})
            continue
        if row.same_as:
            trace.append({"id": rid, "passed": True, "result": f"same_as {row.same_as}", "values": {}})
        jtype, step_conf, step = _apply_row(row, values, p, flags)
        conf = min(conf, step_conf)
        trace.append({"id": row.same_as or rid, "passed": True, "result": jtype, "values": step})
        out.update(junction_type_soll=jtype, rule_id=rid)
        dtv = values["entering_dtv_sum"]
        if (jtype == "roundabout_single_lane_cycle_priority" and dtv is not None and not expr.is_missing(dtv)
                and float(dtv) > p.thresholds["roundabout_max_dtv"]):
            flags.append("dtv_above_roundabout_max")
        break
    else:
        flags.append("no_rule")
        return out
    out["confidence"] = confidence(conf, flags)
    return out


def _apply_row(row: Row, values: dict, p: JunctionParams, flags: list) -> tuple[str, int, dict]:
    """Type from if/then, else_if/else_then, otherwise; unknown conditions follow J-M-05.on_unknown."""
    spec = row.spec
    step: dict[str, Any] = {}
    conf = expr.HIGH

    def branch(cond_key: str, yes_key: str, no) -> str:
        nonlocal conf
        v, c, used = _eval(spec[cond_key], values, p)
        step[cond_key] = {"result": v, **used}
        conf = min(conf, c)
        if v is None:
            flags.append("condition_unknown")
            conf = expr.LOW
            return spec[yes_key] if p.on_unknown == "then" else spec[p.on_unknown]
        return spec[yes_key] if v else no()

    if spec.get("if") is None:
        jtype = spec["then"]
    else:
        jtype = branch("if", "then", lambda: branch("else_if", "else_then", lambda: spec["otherwise"])
                       if spec.get("else_if") is not None else spec["otherwise"])
    if spec.get("fallback") and jtype in p.fallback_types:
        v, c, used = _eval(p.fallback_cond, values, p)
        step["fallback_if"] = {"result": v, **used}
        conf = min(conf, c)
        if v is None:
            flags.append("condition_unknown")
            conf = expr.LOW
        elif v:
            jtype = spec["fallback"]
    elif spec.get("fallback"):
        step["fallback_alternative"] = spec["fallback"]
    return jtype, conf, step


def confidence(conf: int, flags: list[str]) -> str:
    if conf == expr.LOW or {"condition_unknown", "no_rule", "dtv_unknown"} & set(flags):
        return "low"
    if conf == expr.MEDIUM or {"dtv_partial", "category_alias", "space_unknown", "cycle_path_ignored"} & set(flags):
        return "medium"
    return "high"


# --- cyclist treatment -------------------------------------------------------------------------------------------


def treatments(jtype: str | None, pair: tuple[str, str] | None, legs: list[dict], p: JunctionParams) -> list[str]:
    if jtype is None or pair is None:
        return []
    out = []
    for entry in p.treatments:
        for clause in entry["applies_to"]:
            if jtype not in clause["types"]:
                continue
            cats = set(clause.get("cycle_cats", []))
            crossing = clause.get("crossing_categories")
            if crossing is not None:
                if pair[0] not in crossing:
                    continue
                pool = crossing_legs(legs, pair, p)
            else:
                pool = legs
            if cats and not any(_cycle_cat(leg) in cats for leg in pool):
                continue
            out.append(entry["id"])
            break
    return out


TREATMENT_DE = {
    "JC-01": "Kreisverkehr mit umlaufendem Radweg, Radverkehr bevorrechtigt (CROW innerorts). Zielkonflikt: SWOV-Analysen "
             "sehen die Wartepflicht für Radfahrende als sicherer; nach deutschem Recht hat der Radverkehr am Kreisverkehr "
             "nur bei fahrbahnnaher Führung Vorrang (StVO/VwV prüfen). Die Vorrangfrage ist vor der Planung zu entscheiden.",
    "JC-02": "Geschützte Kreuzung: Eckinseln, abgesetzte Furt 2–5 m, Aufstellfläche vor dem Kfz-Verkehr, indirektes Linksabbiegen.",
    "JC-03": "Radfurt in Breite des Radwegs, rot eingefärbt, aufgepflastert, wo der Radverkehr Vorrang hat.",
    "JC-04": "Mittelinsel für die Querung der Hauptstraße durch die Radroute (≥ 3,00 m HAUPT, ≥ 2,50 m BASIS).",
    "JC-05": "Freies Rechtsabbiegen für den Radverkehr an der LSA, wo sicher.",
}


def treatment_text(ids: list[str]) -> str | None:
    return " ".join(TREATMENT_DE[i] for i in ids if i in TREATMENT_DE) or None


# --- Ist ---------------------------------------------------------------------------------------------------------


def ist_type(roundabout: bool, signal: bool, plateau: bool) -> str:
    if roundabout:
        return "roundabout"
    if signal:
        return "signal_plateau" if plateau else "signal"
    return "plateau" if plateau else "none_mapped"


def ist_result(soll: str | None, ist: str, p: JunctionParams) -> str | None:
    """match | not_checkable | mismatch (None without Soll)."""
    if soll is None:
        return None
    check = p.ist_check[soll]
    if ist in check["ok"]:
        return "match"
    if ist in check["not_checkable"]:
        return "not_checkable"
    return "mismatch"


def entering_dtv(legs: list[dict], share: float, zero_cats: set) -> tuple[float | None, list[str]]:
    """J-M-02: share x DTV summed over road legs. ETW legs (zero_cats) without DTV count 0; a GOW/SW leg without DTV
    makes the sum a lower bound (dtv_partial), all GOW/SW legs without DTV make it unknown (dtv_unknown)."""
    total, major, missing = 0.0, 0, 0
    for leg in legs:
        if leg["cat"] == CYCLE_PATH:
            continue
        d = leg.get("dtv")
        major += leg["cat"] not in zero_cats
        if d is None or expr.is_missing(d):
            missing += leg["cat"] not in zero_cats
        else:
            total += share * float(d)
    if missing == 0:
        return total, []
    if missing == major:
        return None, ["dtv_unknown"]
    return total, ["dtv_partial"]


def _angle_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def merge_arms(legs: list[dict], max_angle_deg: float) -> list[dict]:
    """J-M-02 arm_merge: legs with the same street name and DTV and a bearing within max_angle_deg form one arm.

    legs need cat, cycle_cat, facility, dtv, name, bearing (degrees) and id; cycle paths are never merged.
    The arm keeps the highest category, the highest cycle category (with its facility) and ids of all its legs.
    """
    arms: list[dict] = []
    for leg in legs:
        target = None
        if leg["cat"] != CYCLE_PATH and leg.get("name") and leg.get("bearing") is not None:
            for arm in arms:
                if (arm["cat"] != CYCLE_PATH and arm.get("name") == leg["name"] and _same_dtv(arm.get("dtv"), leg.get("dtv"))
                        and _angle_diff(arm["bearing"], leg["bearing"]) <= max_angle_deg):
                    target = arm
                    break
        if target is None:
            arms.append({**leg, "ids": [leg["id"]]})
            continue
        target["ids"].append(leg["id"])
        if CYCLE_RANK[_cycle_cat(leg)] > CYCLE_RANK[_cycle_cat(target)]:
            target["cycle_cat"], target["facility"] = leg["cycle_cat"], leg.get("facility")
        target["tram"] = bool(target.get("tram")) or bool(leg.get("tram"))
    return arms


def _same_dtv(a, b) -> bool:
    ma, mb = a is None or expr.is_missing(a), b is None or expr.is_missing(b)
    return (ma and mb) or (not ma and not mb and float(a) == float(b))
