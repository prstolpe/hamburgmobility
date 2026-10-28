"""Discrepancy ('grijze wegen') and priority per segment (rules D-SPD-01, D-DES-01, D-USE-01, D-TYPE-01, P-RISK-01).

All thresholds come from config/rules.yaml (sections discrepancy, priority). Missing Ist values are unknown,
never a violation: conditions are evaluated with three-valued logic (pipeline/lib/expr.py).
"""

import math
from functools import lru_cache
from typing import Any

import numpy as np
import pandas as pd

from config.schema.rules_model import DesignViolation, RuleSet
from pipeline.lib import expr
from pipeline.lib.features import percentile_rank, weighted_score


def _missing(v: Any) -> bool:
    return expr.is_missing(v)


def _num(v: Any) -> float | None:
    return None if _missing(v) else float(v)


# --- D-SPD-01 --------------------------------------------------------------------------------


def speed_severity(ist_kmh: Any, soll_kmh: Any, rules: RuleSet) -> dict:
    """Trace step: severity 0-3 from the excess of the Ist limit over the Soll speed; None if not checkable."""
    d = rules.discrepancy.speed
    ist, soll = _num(ist_kmh), _num(soll_kmh)
    step = {"rule": d.id, "result": None, "inputs": {"speed_ist_kmh": ist, "soll_kmh": soll}}
    if ist is None or soll is None:
        return step
    excess = ist - soll
    sev = max((lv.severity for lv in d.levels if excess >= lv.min_excess_kmh), default=0)
    step["inputs"]["excess_kmh"] = excess
    step["result"] = sev
    return step


# --- D-DES-01 --------------------------------------------------------------------------------


def _requirement_value(rules: RuleSet, category: str, check: str) -> tuple[bool, Any]:
    reqs = rules.requirements.get(category, {})
    if check not in reqs:
        return False, None
    entry = reqs[check]
    return True, entry.get("value") if isinstance(entry, dict) else entry


def applicable_violations(category: str, rules: RuleSet) -> list[DesignViolation]:
    """Design checks that apply to the category (its requirement exists and has the expected value)."""
    out = []
    for v in rules.discrepancy.design.violations:
        has, value = _requirement_value(rules, category, v.check)
        if has and (v.requirement is None or value == v.requirement):
            out.append(v)
    return out


@lru_cache(maxsize=None)
def _parsed(condition: str):
    return expr.parse(condition)


def _no_ref(name: str) -> float:
    raise expr.ExprError(f"discrepancy conditions take no references ({name})")


def design_assessment(values: dict, category: str, rules: RuleSet) -> tuple[dict, list[dict]]:
    """Trace step and violations (each with check, label, direction, inputs).

    result = number of violations capped at max_severity; None if no check applies or none was decidable.
    """
    d = rules.discrepancy.design
    vals = dict(values)
    ins, gegen = _num(values.get("lanes_official_in")), _num(values.get("lanes_official_gegen"))
    vals["lanes_per_dir_max"] = None if ins is None and gegen is None else max(x for x in (ins, gegen) if x is not None)
    checks = applicable_violations(category, rules)
    violations, unknown, decided = [], [], 0
    for v in checks:
        _, req = _requirement_value(rules, category, v.check)
        ctx = expr.Context({**vals, "requirement": req}, _no_ref, near_threshold=0.0)
        r = expr.evaluate(_parsed(v.violated_if), ctx)
        inputs = {k: expr.clean_value(x) for k, x in ctx.used.items() if k != "requirement"}
        if r.value is None:
            unknown.append(v.check)
            continue
        decided += 1
        if r.value:
            violations.append({"dimension": "design", "check": v.check, "label": v.label_de,
                               "direction": v.direction_for(category), "inputs": inputs})
    result = None if decided == 0 else min(len(violations), d.max_severity)
    step = {"rule": d.id, "result": result, "violations": [x["check"] for x in violations], "unknown": unknown,
            "inputs": {}}
    return step, violations


# --- D-USE-01 --------------------------------------------------------------------------------


def _max_dtv(rules: RuleSet, category: str, profile: str | None) -> float | None:
    profiles = rules.requirements.get(category, {}).get("profiles", {})
    if profile not in profiles:
        return None
    return profiles[profile].get("max_dtv")


def use_severity(dtv: Any, track: Any, category: str, rules: RuleSet) -> dict:
    """Trace step: severity 0-3 from DTV over the profile's max_dtv; None if not applicable or unknown."""
    u = rules.discrepancy.use
    limit = _max_dtv(rules, category, u.profile_default)
    step = {"rule": u.id, "result": None, "inputs": {"dtv": _num(dtv), "separated_cycle_track_present":
                                                     None if _missing(track) else bool(track)}}
    if limit is None:
        step["inputs"]["note"] = "keine max_dtv für die Kategorie"
        return step
    if u.profile_reported:
        step["inputs"][f"max_dtv_{u.profile_reported}"] = _max_dtv(rules, category, u.profile_reported)
    x = _num(dtv)
    if x is None:
        return step
    step["inputs"][f"max_dtv_{u.profile_default}"] = limit
    sev = max((lv.severity for lv in u.levels if x > lv.factor * limit), default=0)
    if sev == 0:
        step["result"] = 0
        return step
    if _missing(track):
        return step  # above the default limit, but the track profile (no limit) is possible
    if bool(track):
        step["inputs"]["profile"] = u.profile_if_track
        track_limit = _max_dtv(rules, category, u.profile_if_track)
        step["result"] = 0 if track_limit is None else max(
            (lv.severity for lv in u.levels if x > lv.factor * track_limit), default=0)
        return step
    step["inputs"]["profile"] = u.profile_default
    step["result"] = sev
    return step


# --- D-TYPE-01 and the whole segment ---------------------------------------------------------


def disc_type(directions: set[str]) -> str | None:
    if not directions:
        return None
    if directions == {"flow"}:
        return "D1"
    if directions == {"sparse"}:
        return "D2"
    return "D3"


def assess_segment(values: dict, category: str, rules: RuleSet) -> dict:
    """All three dimensions, type and trace for one segment with Soll category `category`."""
    soll = rules.categories[category].speed_kmh
    s_speed = speed_severity(values.get("speed_ist_kmh"), soll, rules)
    s_design, design_v = design_assessment(values, category, rules)
    s_use = use_severity(values.get("dtv_official"), values.get("separated_cycle_track_present"), category, rules)

    causes = list(design_v)
    if s_speed["result"]:
        causes.insert(0, {"dimension": "speed", "check": "speed", "label": "Tempo über Soll",
                          "direction": rules.discrepancy.speed.direction, "inputs": s_speed["inputs"]})
    if s_use["result"]:
        causes.append({"dimension": "use", "check": "dtv", "label": "Verkehrsmenge über Soll",
                       "direction": rules.discrepancy.use.direction, "inputs": s_use["inputs"]})
    directions = {c["direction"] for c in causes}
    dtype = disc_type(directions)
    sevs = [s["result"] for s in (s_speed, s_design, s_use) if s["result"] is not None]
    trace = [s_speed, s_design, s_use,
             {"rule": rules.discrepancy.type_rule.id, "result": dtype, "inputs": {"directions": sorted(directions)}}]
    return {"disc_speed": s_speed["result"], "disc_design": s_design["result"], "disc_use": s_use["result"],
            "disc_max": max(sevs) if sevs else None, "disc_type": dtype, "disc_causes": causes,
            "disc_design_unknown": s_design["unknown"], "disc_trace": trace}


# --- P-RISK-01 and priority ------------------------------------------------------------------


def crashes_per_km(weighted: pd.Series, length_m: pd.Series, rules: RuleSet) -> pd.Series:
    """Weighted crashes per km; the length is at least min_length_m."""
    min_len = rules.priority.risk.thresholds["min_length_m"].value
    km = np.maximum(pd.to_numeric(length_m, errors="coerce").astype("float64"), min_len) / 1000.0
    return pd.to_numeric(weighted, errors="coerce").astype("float64") / km


def risk_frame(df: pd.DataFrame, rules: RuleSet) -> pd.DataFrame:
    """Risk components (0-1), risk and risk_weight_available for each row of df.

    df needs crash_weighted_per_km, in_cycle_network, population_100m_norm and schools_or_kitas_within_m.
    Normalisation over the rows of df (S-FEAT-01).
    """
    risk = rules.priority.risk
    ties = rules.features.rule("S-FEAT-01").ties
    radius = risk.thresholds["school_kita_radius_m"].value
    dist = pd.to_numeric(df["schools_or_kitas_within_m"], errors="coerce").astype("float64")
    comp = pd.DataFrame(index=df.index)
    comp["crash_norm"] = percentile_rank(df["crash_weighted_per_km"], ties=ties)
    comp["in_cycle_network"] = pd.to_numeric(df["in_cycle_network"].astype("Float64"), errors="coerce").astype("float64")
    comp["population_100m_norm"] = pd.to_numeric(df["population_100m_norm"], errors="coerce").astype("float64")
    comp["school_kita_near"] = (dist <= radius).astype("float64").where(dist.notna())
    weights = {col: rules.priority.risk_weights[key] for key, col in risk.components.items()}
    missing = [c for c in weights if c not in comp.columns]
    if missing:
        raise KeyError(f"risk components without a column: {missing}")
    score, available = weighted_score(comp, weights)
    out = comp[["crash_norm", "school_kita_near"]].copy()
    out["risk"] = score
    out["risk_weight_available"] = available
    return out


def priority(max_severity: Any, risk: Any) -> float | None:
    """formula max(severity) * risk; 0 without a discrepancy, None if not checkable or risk unknown."""
    if _missing(max_severity):
        return None
    if float(max_severity) == 0:
        return 0.0
    if _missing(risk) or (isinstance(risk, float) and math.isnan(risk)):
        return None
    return float(max_severity) * float(risk)
