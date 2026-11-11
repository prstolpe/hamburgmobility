"""Cycle facility and width per street segment (prompts/18, rules C-FAC-01..07 in config/cycling_rules.yaml).

Soll facility from the separation matrix with the cycle street (C-FAC-02) and mixed-traffic (S-04, C-FAC-03)
checks, target width (C-FAC-04), Ist class from OSM (C-FAC-05), gap (C-FAC-06) and confidence (C-FAC-07).
Every value comes in through FacilityParams. The matrix lookup and the width rule are shared with
pipeline/lib/principles.py (FacilityParams carries the attribute names those functions read).
"""

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import shapely

from config.schema.cycling_model import NO_CYCLE_CATEGORY, CyclingRuleSet, width_ref
from config.schema.provenance import is_active
from config.schema.rules_model import RuleSet
from pipeline.lib import principles as pr


@dataclass(frozen=True)
class DtvProxy:
    """C-FAC-02 dtv_proxy (F19): without a DTV, a shortcut flag or a high betweenness makes the condition unknown."""
    shortcut_flag: str
    betweenness_attribute: str
    threshold: float
    flag: str

    @classmethod
    def from_rule(cls, rule: dict | None) -> "DtvProxy | None":
        if rule is None:
            return None
        return cls(rule["shortcut_flag"], rule["betweenness_attribute"], float(rule["proxy_betweenness"]["value"]), rule["flag"])

    def hit(self, shortcut, betweenness) -> bool:
        short = False if _missing(shortcut) else bool(shortcut)
        return short or (not _missing(betweenness) and float(betweenness) >= self.threshold)


@dataclass(frozen=True)
class FacilityParams:
    matrix: dict
    category_order: tuple
    cs_max_dtv: float
    motor_peak_share: float
    s04_max_kfz_h: float
    rural_mixed_max_dtv: float
    cs_dtv_missing_met: bool
    s04_dtv_missing_met: bool
    required_by_facility: dict     # facility -> widths_m.project_target key (name read by principles.required_width)
    project_target: dict
    intensity_upgrade: tuple       # (oneway|twoway, threshold, add_m)
    floor: dict                    # facility -> metres
    de_ref: dict
    nl_ref: dict
    ist_classes: tuple
    track_values: frozenset
    lane_values: frozenset
    shared_values: frozenset
    to_facility: dict
    twoway_track_facility: str
    satisfies: dict
    partial: dict
    missing_classes: frozenset
    not_assessed_soll: frozenset
    category_check: dict           # C-FAC-06: cat_final, soll, ist_classes (sets) and flag
    lowers_confidence: frozenset
    high_volume: dict              # road category -> principles.HighVolume (S-05, F01)
    cs_motor_traffic: bool         # C-FAC-04 cycle_street_motor_traffic (F18), read by principles.required_width
    proxy: DtvProxy | None = None  # C-FAC-02 dtv_proxy (F19)

    @classmethod
    def from_rules(cls, cyc: CyclingRuleSet, road: RuleSet | None = None) -> "FacilityParams":
        """road = config/rules.yaml (S-05 reads requirements.GOW30.profiles.wide.max_dtv); loaded if not given."""
        if road is None:
            from pipeline.lib.rules import load_rules
            road = load_rules()
        r = {x["id"]: x for x in cyc.facility_assignment["rules"]}
        pri = {x["id"]: x for x in cyc.principle_scoring["rules"]}
        s04 = next(x for x in cyc.separation_matrix["rules"] if x["id"] == "S-04")
        widths = cyc.widths_m
        target = widths["project_target"]
        c04, c05, c06 = r["C-FAC-04"], r["C-FAC-05"], r["C-FAC-06"]
        return cls(
            matrix=cyc.separation_matrix,
            category_order=tuple(r["C-FAC-01"]["category_order"]),
            cs_max_dtv=float(cyc.cycle_street["max_motor_vehicles_day"]["value"]),
            motor_peak_share=float(r["C-FAC-03"]["motor_peak_hour_share"]["value"]),
            s04_max_kfz_h=float(s04["mixed_max_kfz_h"]),
            rural_mixed_max_dtv=float(cyc.separation_matrix["mixed_rural_max_dtv"]["value"]),
            cs_dtv_missing_met=bool(r["C-FAC-02"]["dtv_missing_counts_as_met"]),
            s04_dtv_missing_met=bool(r["C-FAC-03"]["dtv_missing_counts_as_met"]),
            required_by_facility=dict(c04["target_by_facility"]),
            project_target=target,
            intensity_upgrade=tuple((*pr.parse_upgrade(u["if"]), float(u["add_m"])) for u in target["intensity_upgrade"]),
            floor={f: float(width_ref(widths, path)) for f, path in c04["floor"].items()},
            de_ref={f: float(width_ref(widths, path)) for f, path in c04["de_reference"].items()},
            nl_ref={f: float(width_ref(widths, path)) for f, path in c04["nl_reference"].items()},
            ist_classes=tuple(c05["ist_classes"]),
            track_values=frozenset(c05["track_values"]),
            lane_values=frozenset(c05["lane_values"]),
            shared_values=frozenset(c05["shared_values"]),
            to_facility=dict(c05["to_facility"]),
            twoway_track_facility=c05["twoway_track_facility"],
            satisfies={k: frozenset(v) for k, v in pri["C-PRI-03"]["satisfies"].items()},
            partial={k: frozenset(v) for k, v in pri["C-PRI-03"]["partial"].items()},
            missing_classes=frozenset(c06["missing_classes"]),
            not_assessed_soll=frozenset(c06["not_assessed_soll"]),
            category_check={**{k: frozenset(c06["category_check"][k]) for k in ("cat_final", "soll", "ist_classes")},
                            "flag": c06["category_check"]["flag"]},
            lowers_confidence=frozenset(r["C-FAC-07"]["lowers_confidence"]),
            high_volume=pr.high_volume_cells(cyc, road),
            cs_motor_traffic=pr.cycle_street_motor_traffic(cyc),
            proxy=DtvProxy.from_rule(r["C-FAC-02"].get("dtv_proxy")),
        )


def _missing(v) -> bool:
    return v is None or v is pd.NA or (isinstance(v, float) and math.isnan(v))


def _num(v):
    return None if _missing(v) else float(v)


def _add(flags: list, flag: str) -> None:
    if flag not in flags:
        flags.append(flag)


def highest_category(cats, p: FacilityParams) -> str:
    """Highest cycle category of a segment's edges (C-FAC-01); 'none' without an edge."""
    present = {c for c in cats if isinstance(c, str)}
    return next((c for c in p.category_order if c in present), NO_CYCLE_CATEGORY)


# --- C-FAC-01..03 Soll facility ---------------------------------------------------------------------------


@dataclass
class SollResult:
    facility: str | None
    fallback: str | None
    flags: list = field(default_factory=list)
    trace: list = field(default_factory=list)


def _raw_cell(cat_final: str, cycle_cat: str, p: FacilityParams):
    if cat_final in pr.RURAL:
        rural = p.matrix["rural"]
        return rural[cat_final] if is_active(rural) else None  # inactive: no data basis outside (F28)
    row = p.matrix.get(cat_final)
    if row is None:
        return None
    return row if "all" in row else row.get(cycle_cat)


def soll_facility(cat_final, cycle_cat, dtv, cyc_peak_both, space_fits_preferred, p: FacilityParams,
                  shortcut=None, betweenness=None) -> SollResult:
    """Soll facility after C-FAC-01 (matrix), C-FAC-02 (cycle street) and C-FAC-03 (S-04).

    shortcut (N4 shortcut flag) and betweenness (betweenness_norm) feed the dtv_proxy of C-FAC-02/03 (F19): without
    a DTV and with a proxy hit the condition is unknown (trace result None) and the segment gets filter_needed;
    the facility stays.
    """
    cycle_cat = cycle_cat if isinstance(cycle_cat, str) else NO_CYCLE_CATEGORY
    dtv = _num(dtv)
    res = SollResult(None, None)
    cell = _raw_cell(cat_final, cycle_cat, p) if isinstance(cat_final, str) else None
    if cell is None:
        res.trace.append({"id": "C-FAC-01", "result": None, "values": {"cat_final": cat_final, "cycle_cat": cycle_cat}})
        return res
    hv = pr.high_volume(cat_final, dtv, p)
    if hv is not None:   # S-05 (F01): before the cycle category, no fallback to a cycle lane
        _add(res.flags, hv.flag)
        values = {"cat_final": cat_final, "cycle_cat": cycle_cat, "dtv": dtv, "dtv_above": hv.dtv_above, "fallback": None}
        res.trace.append({"id": "C-FAC-01", "result": hv.facility, "values": {**values, "cell": "high_volume"}})
        if hv.rule:
            res.trace.append({"id": hv.rule, "result": hv.facility, "values": values})
        res.facility, res.fallback = hv.facility, None
        return res
    preferred, fallback = pr.soll_facility(cat_final, cycle_cat, p)
    facility = preferred
    values = {"cat_final": cat_final, "cycle_cat": cycle_cat, "preferred": preferred, "fallback": fallback,
              "space_fits_preferred": space_fits_preferred}
    if fallback is not None:
        allowed = True
        if isinstance(cell, dict) and "condition" in cell:   # ETW60: mixed only at low DTV
            values["mixed_rural_max_dtv"] = p.rural_mixed_max_dtv
            if dtv is None:
                _add(res.flags, "dtv_unknown")
            else:
                allowed = dtv <= p.rural_mixed_max_dtv
            values["fallback_allowed"] = allowed
        if space_fits_preferred is False and allowed:
            facility = fallback
        elif space_fits_preferred is None and allowed:
            _add(res.flags, "fallback_check_p19")
    if isinstance(cell, dict) and cell.get("flag"):   # e.g. haupt_through_pedestrian_area (F15)
        _add(res.flags, cell["flag"])
    res.trace.append({"id": "C-FAC-01", "result": facility, "values": values})

    motor_peak = None if dtv is None else dtv * p.motor_peak_share
    proxy_hit = dtv is None and p.proxy is not None and p.proxy.hit(shortcut, betweenness)
    proxy_values = {} if p.proxy is None or dtv is not None else {
        "dtv_proxy": proxy_hit, p.proxy.shortcut_flag: None if _missing(shortcut) else bool(shortcut),
        p.proxy.betweenness_attribute: _num(betweenness), "proxy_betweenness": p.proxy.threshold}
    if facility == "cycle_street":
        cyc = _num(cyc_peak_both)
        if dtv is None:
            ok = p.cs_dtv_missing_met
            _add(res.flags, "dtv_unknown")
            if proxy_hit:
                _add(res.flags, p.proxy.flag)
        else:
            ok = dtv <= p.cs_max_dtv and cyc is not None and cyc >= motor_peak
        res.trace.append({"id": "C-FAC-02", "result": None if proxy_hit else ok, "values": {
            "dtv": dtv, "max_motor_vehicles_day": p.cs_max_dtv, "cyc_peak_h": cyc, "motor_peak_h": motor_peak, **proxy_values}})
        if not ok:
            facility = "mixed"
            _add(res.flags, "cycle_street_blocked")
    if facility == "mixed":
        if dtv is None:
            ok = p.s04_dtv_missing_met
            _add(res.flags, "dtv_unknown")
            if proxy_hit:
                _add(res.flags, p.proxy.flag)
        else:
            ok = motor_peak <= p.s04_max_kfz_h
        res.trace.append({"id": "S-04", "result": None if proxy_hit else ok, "values": {
            "dtv": dtv, "motor_peak_hour_share": p.motor_peak_share, "motor_peak_h": motor_peak, "mixed_max_kfz_h": p.s04_max_kfz_h,
            **proxy_values}})
        if not ok:
            _add(res.flags, "mixed_over_s04")
    res.facility, res.fallback = facility, fallback
    return res


# --- C-FAC-04 width -----------------------------------------------------------------------------------------


@dataclass
class WidthResult:
    width: float | None
    de: float | None
    nl: float | None
    trace: dict


def target_width(facility, cycle_cat, peak_dir, peak_both, p: FacilityParams) -> WidthResult:
    """Target width (project_target + intensity_upgrade, at least the floor) and the DE / NL comparison values."""
    cycle_cat = cycle_cat if isinstance(cycle_cat, str) else NO_CYCLE_CATEGORY
    raw = pr.required_width(facility, cycle_cat, peak_dir, peak_both, p) if isinstance(facility, str) else float("nan")
    width = None if math.isnan(raw) else raw
    floor = p.floor.get(facility)
    if width is not None and floor is not None:
        width = max(width, floor)
    trace = {"id": "C-FAC-04", "result": width, "values": {
        "facility": facility, "cycle_cat": cycle_cat, "target": None if math.isnan(raw) else raw, "floor": floor,
        "peak_dir": _num(peak_dir), "peak_both": _num(peak_both)}}
    return WidthResult(width, p.de_ref.get(facility), p.nl_ref.get(facility), trace)


# --- C-FAC-05 Ist -------------------------------------------------------------------------------------------


def ist_class(p: FacilityParams, fahrradstrasse=False, bicycle_road=False, cycleway_values=(), has_sidepath=False,
              track_present=False, lane_present=False) -> str:
    """Ist class of a segment: first matching class of ist_classes (C-FAC-05).

    track_present / lane_present are the segment features of pipeline/s04 (separated_cycle_track_present,
    cycle_lane_present), which also cover segments without an edge in the cycle graph.
    """
    values = set(cycleway_values or ())
    hits = {
        "cycle_street": bool(fahrradstrasse) or bool(bicycle_road),
        "track": bool(values & p.track_values) or bool(has_sidepath) or bool(track_present),
        "lane": bool(values & p.lane_values) or bool(lane_present),
        "shared_lane": bool(values & p.shared_values),
        "no": True,
    }
    return next(c for c in p.ist_classes if hits[c])


def ist_facility(cls: str, sidepath_twoway: bool, p: FacilityParams, sidepath_both_sides: bool = False) -> str:
    """Facility name of an Ist class; sidepaths on one side only and open in both directions -> two-way track."""
    if cls == "track" and sidepath_twoway and not sidepath_both_sides:
        return p.twoway_track_facility
    return p.to_facility[cls]


def sidepath_side(road_geoms, path_geoms, step_m: float = 1.0) -> np.ndarray:
    """Side of each sidepath relative to its road's digitising direction: +1 left, -1 right, 0 undecided.

    Sign of the cross product of the road tangent at the projection of the sidepath midpoint.
    """
    mid = shapely.line_interpolate_point(path_geoms, 0.5, normalized=True)
    d = shapely.line_locate_point(road_geoms, mid)
    a = shapely.line_interpolate_point(road_geoms, np.maximum(d - step_m, 0.0))
    b = shapely.line_interpolate_point(road_geoms, np.minimum(d + step_m, shapely.length(road_geoms)))
    ax, ay, bx, by = shapely.get_x(a), shapely.get_y(a), shapely.get_x(b), shapely.get_y(b)
    cross = (bx - ax) * (shapely.get_y(mid) - ay) - (by - ay) * (shapely.get_x(mid) - ax)
    return np.sign(np.nan_to_num(cross)).astype(int)


# --- C-FAC-06 gap, C-FAC-07 confidence ----------------------------------------------------------------------


def facility_gap(soll, fallback, ist_cls, ist_fac, ist_width, soll_width, p: FacilityParams) -> tuple[str, bool]:
    """(gap, partial): not_assessed | missing | partial | wrong_type | too_narrow | none (C-FAC-06)."""
    if not isinstance(soll, str) or soll in p.not_assessed_soll:
        return "not_assessed", False
    partial = ist_fac in p.partial.get(soll, ()) or (fallback is not None and ist_fac == fallback)
    if ist_fac not in p.satisfies.get(soll, ()):
        if ist_cls in p.missing_classes:
            return "missing", partial
        return ("partial" if partial else "wrong_type"), partial
    w = _num(ist_width)
    if w is not None and soll_width is not None and w < soll_width:
        return "too_narrow", False
    return "none", False


def category_check(cat_final, soll, ist_cls, p: FacilityParams) -> bool:
    """C-FAC-06 category_check: cycle track on an access road whose Soll is a cycle street -> check the road category."""
    c = p.category_check
    return cat_final in c["cat_final"] and soll in c["soll"] and ist_cls in c["ist_classes"]


# rules.yaml C-G30-02 note (F06): existing track narrower than the C-FAC-04 floor of its Ist facility
TRACK_BELOW_FLOOR_FLAG = "existing_track_below_floor"


def track_below_floor(ist_class: str, ist_facility: str | None, width_ist, p: FacilityParams) -> bool:
    """F06: an existing track (C-FAC-05 class track) whose known Ist width is below the C-FAC-04 floor."""
    w = _num(width_ist)
    return ist_class == "track" and w is not None and ist_facility in p.floor and w < p.floor[ist_facility]


def confidence(cat_final, flags, p: FacilityParams) -> str:
    if not isinstance(cat_final, str):
        return "low"
    return "medium" if set(flags) & p.lowers_confidence else "high"
