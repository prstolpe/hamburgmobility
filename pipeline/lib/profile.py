"""Soll cross section per street segment (prompts/19): lanes, placement, space allocation, degrade cascade.

Rules: design_rules.yaml lanes L-01..L-06, placement PL-01..PL-07, cross_section_allocation and
profile_assignment PRF-01..PRF-07; cycle widths from cycling_rules.yaml (prompt 18). Every value comes in through
ProfileParams; the functions here are pure and work on one segment.
"""

import html
import math
from dataclasses import dataclass, field, replace

from config.schema.cycling_model import NO_CYCLE_CATEGORY, CyclingRuleSet, width_ref
from config.schema.design_model import FALLBACK_STEP, DesignRuleSet
from config.schema.rules_model import RuleSet
from pipeline.lib import facility as fa
from pipeline.lib.rules import all_thresholds

FIT_CLASSES = ("fits", "fits_after_degrade", "does_not_fit")
CYCLE_SIDES = ("both", "one", "carriageway", "own_path")
# Fill step of each element (cross_section_allocation.fill_order); cycling/sidewalk elements belong to their
# minimum step and are widened in cycling_to_target_width / sidewalks_to_standard.
FILL_STEP = {"sidewalk": "sidewalks_min", "cycle_track": "cycling_min", "cycle_lane": "cycling_min",
             "bus_lane": "transit_lanes_if_required", "tram": "transit_lanes_if_required",
             "carriageway": "motor_lanes_min", "median": "motor_lanes_min", "shared_surface": "motor_lanes_min",
             "buffer_cycle_carriageway": "buffers_min", "buffer_to_parking": "buffers_min",
             "tree_strip": "trees_or_greening", "loading_zone": "loading_zones", "parking_parallel": "parking"}
LABEL_DE = {"sidewalk": "Gehweg", "cycle_track": "Radweg", "cycle_lane": "Radfahrstreifen",
            "buffer_cycle_carriageway": "Trennstreifen", "buffer_to_parking": "Sicherheitsraum", "tree_strip": "Baumstreifen",
            "parking_parallel": "Parken", "loading_zone": "Ladezone", "bus_lane": "Bus", "carriageway": "Fahrbahn",
            "median": "Mittelstreifen", "shared_surface": "Mischfläche", "tram": "Straßenbahn"}


def _num(v):
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


def _value(entry):
    return float(entry["value"] if isinstance(entry, dict) else entry)


@dataclass(frozen=True)
class ProfileParams:
    dtv_factor: float
    lane_capacity: float
    target_vc: float
    bus_lane_trigger: float
    default_lanes: dict
    max_lanes: int
    gow50_general: float
    gow50_with_bus: float
    gow50_2x1: float
    gow50_bus_cw: float
    gow30_narrow: tuple          # (lower bound of carriageway range, max_dtv)
    gow30_wide: tuple
    etw_mixed: float
    etw_mixed_bus: float
    median_min: float
    cycle_street_carriageway: float
    sidewalk_min: float
    sidewalk_std: float
    element_m: dict              # elements_min_m with plain numbers
    buffer_to_parking: float
    business_frontage: float
    sidewalk_sides: int
    no_sidewalk: frozenset
    tree_categories: frozenset
    tree_sides: int
    loading_sides: int
    parking_positions: frozenset
    cycle_elements: dict
    no_profile: frozenset
    cascade_order: tuple
    flag_only: frozenset
    fill_order: tuple
    floor: dict
    fp: fa.FacilityParams = field(repr=False)

    @property
    def second_lane_dtv(self) -> float:
        """DTV above which L-02 asks for a second lane (lane_capacity x target_vc / peak factor)."""
        return self.lane_capacity * self.target_vc / self.dtv_factor

    @classmethod
    def from_rules(cls, design: DesignRuleSet, cycling: CyclingRuleSet, rules: RuleSet) -> "ProfileParams":
        lr = {r["id"]: r for r in design.lanes.rules}
        lw = design.lanes.lane_width_m
        alloc = design.cross_section_allocation
        em = alloc["elements_min_m"]
        prf = {r["id"]: r for r in design.profile_assignment["rules"]}
        fp = fa.FacilityParams.from_rules(cycling)
        elements = {k: _value(v) for k, v in em.items() if not isinstance(v, str) and k != "sidewalk"}
        return cls(
            dtv_factor=float(lr["L-02"]["peak_h_dir_from_dtv"]["factor"]),
            lane_capacity=float(lr["L-02"]["lane_capacity_veh_h"]["value"]),
            target_vc=float(lr["L-02"]["target_vc"]["value"]),
            bus_lane_trigger=float(lr["L-04"]["bus_lane_trigger"]["value"]),
            default_lanes={k: v for k, v in design.lanes.default_per_direction.items()
                           if k not in ("source", "source_type", "note", "status")},
            max_lanes=int(prf["PRF-01"]["max_lanes_per_direction"]),
            gow50_general=float(lw["GOW50"]["general"]),
            gow50_with_bus=float(lw["GOW50"]["with_bus"]),
            gow50_2x1=_value(lw["GOW50_2x1_carriageway"]),
            gow50_bus_cw=_value(lw["GOW50_bus_carriageway"]),
            gow30_narrow=(float(lw["GOW30_narrow_profile"]["carriageway_range"][0]), float(lw["GOW30_narrow_profile"]["max_dtv"])),
            gow30_wide=(float(lw["GOW30_wide_profile"]["carriageway_range"][0]), float(lw["GOW30_wide_profile"]["max_dtv"])),
            etw_mixed=_value(lw["ETW30_mixed"]),
            etw_mixed_bus=float(lw["ETW30_mixed"]["bus"]),
            median_min=_value(lw["median_min_m"]),
            cycle_street_carriageway=_value(cycling.widths_m["project_target"]["cycle_street_carriageway"]),
            sidewalk_min=float(em["sidewalk"]["min"]),
            sidewalk_std=float(em["sidewalk"]["standard"]),
            element_m=elements,
            buffer_to_parking=float(width_ref(cycling.widths_m, prf["PRF-03"]["cycle_elements"]["cycle_lane"]["buffer_if_parking"]
                                              .removeprefix("widths_m."))),
            business_frontage=float(all_thresholds(rules)["frontage"].value),
            sidewalk_sides=int(prf["PRF-03"]["sidewalk_sides"]),
            no_sidewalk=frozenset(prf["PRF-03"]["no_sidewalk_categories"]),
            tree_categories=frozenset(prf["PRF-03"]["tree_categories"]),
            tree_sides=int(prf["PRF-03"]["tree_sides"]),
            loading_sides=int(prf["PRF-03"]["loading_sides"]),
            parking_positions=frozenset(prf["PRF-03"]["parking_positions"]),
            cycle_elements=dict(prf["PRF-03"]["cycle_elements"]),
            no_profile=frozenset(prf["PRF-04"]["no_profile_categories"]),
            cascade_order=tuple(prf["PRF-06"]["cascade_order"]),
            flag_only=frozenset(prf["PRF-06"]["flag_only_steps"]),
            fill_order=tuple(alloc["fill_order"]),
            floor=dict(fp.floor),
            fp=fp,
        )


# --- inputs -----------------------------------------------------------------------------------------------


def parking_sides(parking, p: ProfileParams) -> int:
    """Sides with parking along the carriageway from the s04 `parking` value ('lane|no' = one side), PRF-03."""
    if not isinstance(parking, str) or not parking:
        return 0
    values = set(parking.split("|"))
    if not values & p.parking_positions:
        return 0
    return 1 if "no" in values else 2


def is_business(shop_frontage_share, p: ProfileParams) -> bool:
    v = _num(shop_frontage_share)
    return v is not None and v >= p.business_frontage


def lanes_ist(lanes_in, lanes_gegen, bahnigkeit, osm_lanes) -> tuple[int | None, bool]:
    """(Ist lanes per direction, oneway) after PRF-01."""
    a, b = _num(lanes_in), _num(lanes_gegen)
    if a is not None and b is not None and max(a, b) > 0:
        oneway = min(a, b) == 0 and _num(bahnigkeit) != 2
        return int(max(a, b)), oneway
    total = _num(osm_lanes)
    if total is not None and total > 0:
        return int(math.ceil(total / 2)), False
    return None, False


@dataclass(frozen=True)
class SegmentInput:
    cat: str | None
    cycle_cat: str
    facility: str | None          # Soll facility of prompt 18 (preferred of the cell)
    fallback: str | None
    cycle_width: float | None
    peak_dir: float | None
    peak_both: float | None
    dtv: float | None
    bus_peak_dir: float | None
    lanes_ist: int | None
    oneway: bool
    parking_sides: int
    business: bool
    tram: bool


# --- lanes L-01..L-06 ---------------------------------------------------------------------------------------


@dataclass
class LanesResult:
    lanes: int | str | None
    bus_lane: bool
    median: bool
    low_confidence: bool = False
    flags: list = field(default_factory=list)
    trace: list = field(default_factory=list)


def lanes_soll(cat, dtv, bus_peak_dir, lanes_ist_dir, p: ProfileParams) -> LanesResult:
    """Car lanes per direction, bus lane and median (L-01..L-04, L-06, PRF-01)."""
    default = p.default_lanes.get(cat) if isinstance(cat, str) else None
    res = LanesResult(default, False, False)
    if default is None:
        res.trace.append({"id": "L-01", "result": None, "values": {"cat": cat, "note": "keine Fahrstreifen (SW oder ohne Kategorie)"}})
        return res
    if default == "shared" or cat == "GOW30":
        res.trace.append({"id": "L-01", "result": default, "values": {"cat": cat}})
        return res
    dtv, bus, ist = _num(dtv), _num(bus_peak_dir) or 0.0, _num(lanes_ist_dir)
    ist = None if ist is None or ist <= 0 else int(ist)
    lanes = default
    if cat == "GOW50":
        limit = p.lane_capacity * p.target_vc
        if dtv is None:
            lanes = min(ist, p.max_lanes) if ist is not None else default
            res.low_confidence = True
            res.flags.append("dtv_unknown")
            res.trace.append({"id": "L-02", "result": lanes, "values": {"dtv": None, "lanes_ist": ist, "note": "ohne DTV Ist-Wert (PRF-01)"}})
        else:
            peak = dtv * p.dtv_factor
            lanes = 2 if peak > limit else 1
            res.trace.append({"id": "L-02", "result": lanes, "values": {
                "dtv": dtv, "peak_h_dir": peak, "factor": p.dtv_factor, "limit_veh_h": limit}})
        if lanes == 2 and dtv is not None:
            take_bus = bus >= p.bus_lane_trigger
            res.trace.append({"id": "L-04", "result": take_bus, "values": {"bus_peak_h_dir": bus, "bus_lane_trigger": p.bus_lane_trigger}})
            if take_bus:
                lanes, res.bus_lane = 1, True
    if ist is not None:
        total = lanes + (1 if res.bus_lane else 0)
        capped = total > ist
        res.trace.append({"id": "L-06", "result": not capped, "values": {"lanes_soll": total, "lanes_ist": ist}})
        if capped:
            res.flags.append("lanes_capped_l06")
            if res.bus_lane:
                res.bus_lane = False
            lanes = min(lanes, ist)
    res.lanes = lanes
    res.median = lanes == 2
    if res.median:
        res.trace.append({"id": "L-03", "result": True, "values": {"lanes": lanes}})
    return res


# --- profile ------------------------------------------------------------------------------------------------


@dataclass
class _State:
    cat: str
    facility: str | None
    cycle_width: float | None
    sidewalk: float
    lanes: int | str | None
    bus_lane: bool
    median: bool
    parking_sides: int
    trees: bool
    at_floor: bool = False


def facility_width(facility, seg: SegmentInput, p: ProfileParams) -> float | None:
    """Target width of a facility for this segment (C-FAC-04 of prompt 18)."""
    return fa.target_width(facility, seg.cycle_cat, seg.peak_dir, seg.peak_both, p.fp).width


def _carriageway(st: _State, seg: SegmentInput, p: ProfileParams, flags: list) -> list[tuple[str, float]]:
    """Centre elements (PRF-04)."""
    bus = (_num(seg.bus_peak_dir) or 0) > 0 and not st.bus_lane
    if st.facility == "cycle_street":
        return [("carriageway", st.cycle_width or p.cycle_street_carriageway)]
    if st.cat == "ETW_ERF":
        return [("shared_surface", p.etw_mixed_bus if bus else p.etw_mixed)]
    if st.cat == "ETW30":
        if seg.oneway:
            return [("carriageway", p.cycle_street_carriageway)]
        return [("carriageway", p.etw_mixed_bus if bus else p.etw_mixed)]
    lane = p.gow50_with_bus if bus else p.gow50_general
    if st.cat == "GOW30":
        if seg.oneway:
            return [("carriageway", lane)]
        dtv = _num(seg.dtv)
        if dtv is None or dtv <= p.gow30_narrow[1]:
            return [("carriageway", p.gow30_narrow[0])]
        if dtv > p.gow30_wide[1] and "gow30_dtv_above_profile" not in flags:
            flags.append("gow30_dtv_above_profile")
        return [("carriageway", p.gow30_wide[0])]
    # GOW50
    n = st.lanes if isinstance(st.lanes, int) else 1
    if seg.oneway:
        return [("carriageway", n * (p.gow50_general if st.bus_lane else lane))]
    if n == 2:
        half = 2 * p.gow50_general
        return [("carriageway", half), ("median", p.median_min), ("carriageway", half)] if st.median \
            else [("carriageway", 2 * half)]
    if st.bus_lane:
        return [("carriageway", 2 * p.gow50_general)]
    return [("carriageway", p.gow50_bus_cw if bus else p.gow50_2x1)]


def _side(st: _State, seg: SegmentInput, p: ProfileParams, left: bool) -> list[tuple[str, float]]:
    """Elements of one side, outer to inner (PRF-03, PL-01..PL-03)."""
    out = []
    if st.cat not in p.no_sidewalk and (p.sidewalk_sides >= 2 or not left):
        out.append(("sidewalk", st.sidewalk))
    cell = p.cycle_elements.get(st.facility) or {}
    el, sides = cell.get("element"), cell.get("sides", 0)
    on_this_side = el is not None and (sides >= 2 or left)   # one-sided two-way track on the left
    parking_here = st.parking_sides >= 2 or (st.parking_sides == 1 and not left)
    if el == "cycle_track" and on_this_side:
        out += [("cycle_track", st.cycle_width or 0.0), (cell["buffer"], p.element_m[cell["buffer"]])]
    if st.trees and st.cat in p.tree_categories and (p.tree_sides >= 2 or not left):
        out.append(("tree_strip", p.element_m["tree_strip"]))
    if seg.business and (p.loading_sides >= 2 or not left):
        out.append(("loading_zone", p.element_m["loading_zone"]))
    if parking_here:
        out.append(("parking_parallel", p.element_m["parking_parallel"]))
    if el == "cycle_lane" and on_this_side:
        if parking_here:
            out.append(("buffer_to_parking", p.buffer_to_parking))
        out.append(("cycle_lane", st.cycle_width or 0.0))
    if st.bus_lane and (not seg.oneway or not left):
        out.append(("bus_lane", p.element_m["bus_lane"]))
    return out


def _build(st: _State, seg: SegmentInput, p: ProfileParams, flags: list) -> list[dict]:
    left = _side(st, seg, p, left=True)
    centre = _carriageway(st, seg, p, flags)
    if seg.tram:
        centre = [("tram", p.element_m["tram"])] + centre
    right = list(reversed(_side(st, seg, p, left=False)))
    rows = [(e, w, "left") for e, w in left] + [(e, w, "centre") for e, w in centre] + [(e, w, "right") for e, w in right]
    return [{"order": i + 1, "element": e, "width_m": round(float(w), 2), "side": s, "fill_step": FILL_STEP[e]}
            for i, (e, w, s) in enumerate(rows)]


def _total(elements: list[dict]) -> float:
    return round(sum(e["width_m"] for e in elements), 2)


@dataclass
class ProfileResult:
    elements: list
    total_required_m: float | None
    available_m: float | None
    fit_class: str | None
    degrade_steps_applied: list
    cat_change_proposal: str | None
    cycle_facility: str | None
    cycle_width_m: float | None
    cycle_side: str | None
    lanes: int | str | None
    bus_lane: bool
    median: bool
    low_confidence: bool
    flags: list
    trace: list


def _apply(step: str, st: _State, seg: SegmentInput, p: ProfileParams, flags: list) -> tuple[_State, dict]:
    """One cascade step; returns the new state and the trace values (PRF-06)."""
    if step == "D1":
        return replace(st, parking_sides=0), {"parking_sides": st.parking_sides, "loading_kept": seg.business}
    if step == "D2":
        has = st.trees and st.cat in p.tree_categories
        if has and "trees_in_parking_row" not in flags:
            flags.append("trees_in_parking_row")
        return replace(st, trees=False), {"tree_strip": has}
    if step == FALLBACK_STEP:
        if seg.fallback is None or st.facility != seg.facility:
            return st, {"fallback": seg.fallback}
        w = facility_width(seg.fallback, seg, p)
        if st.at_floor and w is not None and seg.fallback in p.floor:
            w = min(w, p.floor[seg.fallback])
        return replace(st, facility=seg.fallback, cycle_width=w), {"from": st.facility, "to": seg.fallback, "width": w}
    if step == "D3":
        if st.lanes == 2:
            return replace(st, lanes=1, median=False), {"lanes": 2, "bus_lane_kept": st.bus_lane}
        return st, {"lanes": st.lanes}
    if step == "D4":
        w = st.cycle_width
        floor = p.floor.get(st.facility)
        if w is not None and floor is not None:
            w = min(w, floor)
        return replace(st, cycle_width=w, sidewalk=min(st.sidewalk, p.sidewalk_min), at_floor=True), \
            {"cycle_width": w, "cycle_floor": floor, "sidewalk": p.sidewalk_min}
    if step == "D5":
        if st.cat != "GOW50":
            return st, {"cat": st.cat}
        soll = fa.soll_facility("GOW30", seg.cycle_cat, seg.dtv, seg.peak_both, False, p.fp)
        w = facility_width(soll.facility, seg, p)
        if w is not None and soll.facility in p.floor:
            w = min(w, p.floor[soll.facility])
        return replace(st, cat="GOW30", facility=soll.facility, cycle_width=w, lanes=1, bus_lane=False, median=False), \
            {"proposal": "GOW30", "rule": "C-G30-02", "facility": soll.facility, "cycle_width": w}
    raise ValueError(f"unknown cascade step {step}")


def _cycle_side(facility, p: ProfileParams):
    cell = p.cycle_elements.get(facility)
    return cell.get("cycle_side") if cell else None


def evaluate_profile(seg: SegmentInput, available, p: ProfileParams, stop_before: str | None = None) -> ProfileResult:
    """Soll profile, fit and degrade cascade of one segment (PRF-03..PRF-07)."""
    lanes = lanes_soll(seg.cat, seg.dtv, seg.bus_peak_dir, seg.lanes_ist, p)
    flags = list(lanes.flags)
    trace = list(lanes.trace)
    available = _num(available)
    if not isinstance(seg.cat, str) or seg.cat in p.no_profile:
        flags.append("no_profile_rules")
        trace.append({"id": "PRF-04", "result": None, "values": {"cat": seg.cat}})
        return ProfileResult([], None, available, None, [], None, seg.facility, seg.cycle_width,
                             _cycle_side(seg.facility, p), lanes.lanes, lanes.bus_lane, lanes.median,
                             lanes.low_confidence, flags, trace)
    st = _State(seg.cat, seg.facility, _num(seg.cycle_width), p.sidewalk_std, lanes.lanes, lanes.bus_lane,
                lanes.median, seg.parking_sides, True)
    cell = p.cycle_elements.get(seg.facility) or {}
    if cell.get("rule"):
        trace.append({"id": cell["rule"], "result": cell.get("cycle_side"), "values": {"facility": seg.facility}})
    if seg.facility == "separated_twoway":
        flags.append("pl02_unchecked")
        trace.append({"id": "PRF-07", "result": "pl02_unchecked", "values": {}})
    elements = _build(st, seg, p, flags)
    total = _total(elements)
    trace.append({"id": "PRF-03", "result": len(elements), "values": {
        "parking_sides": seg.parking_sides, "business": seg.business, "tram": seg.tram, "oneway": seg.oneway}})
    trace.append({"id": "PRF-05", "result": None if available is None else total <= available,
                  "values": {"total_required_m": total, "available_m": available}})
    applied: list[str] = []
    proposal = None
    fit = None
    if available is None:
        flags.append("width_unknown")
    else:
        fits = total <= available + 1e-9
        for step in p.cascade_order:
            if fits or step == stop_before:
                break
            if step in p.flag_only:
                # D7 only where the cycle facility takes its own width (relocating mixed traffic frees no space)
                takes_width = (p.cycle_elements.get(st.facility) or {}).get("element") is not None
                on = step != "D7" or (seg.cycle_cat not in (None, NO_CYCLE_CATEGORY) and takes_width)
                if on:
                    applied.append(step)
                    flags.append(step)
                trace.append({"id": step, "applied": on, "result": "flag" if on else None, "values": {}})
                continue
            new, values = _apply(step, st, seg, p, flags)
            new_elements = _build(new, seg, p, flags)
            new_total = _total(new_elements)
            # a step counts only if it changes the profile: narrower, or D5 (category proposal) at all
            changed = new_total < total - 1e-9 or (step == "D5" and new.cat != st.cat)
            trace.append({"id": step, "applied": changed, "result": new_total if changed else None, "values": values})
            if not changed:
                continue
            applied.append(step)
            st, elements, total = new, new_elements, new_total
            if step == "D5":
                proposal = "GOW30"
            fits = total <= available + 1e-9
        steps = [s for s in applied if s not in p.flag_only]
        fit = ("fits" if not steps else "fits_after_degrade") if fits else "does_not_fit"
        trace.append({"id": "PRF-06", "result": fit, "values": {"steps": applied, "total_required_m": total,
                                                                  "available_m": available}})
    return ProfileResult(elements, total, available, fit, applied, proposal, st.facility, st.cycle_width,
                         _cycle_side(st.facility, p), st.lanes, st.bus_lane, st.median, lanes.low_confidence, flags, trace)


def confidence(res: ProfileResult, seg: SegmentInput) -> str:
    if res.low_confidence or res.fit_class is None:
        return "low"
    if seg.lanes_ist is None or "pl02_unchecked" in res.flags:
        return "medium"
    return "high"


# --- SVG ----------------------------------------------------------------------------------------------------

_COLOURS = {"sidewalk": "#d9d4c7", "cycle_track": "#c0392b", "cycle_lane": "#e06c5a", "buffer_cycle_carriageway": "#9aa39a",
            "buffer_to_parking": "#b8beb8", "tree_strip": "#5b8c3a", "parking_parallel": "#8e9aaf", "loading_zone": "#c9a227",
            "bus_lane": "#b03a8c", "carriageway": "#555b61", "median": "#7da35a", "shared_surface": "#a39a8a", "tram": "#6b5b95"}
_PX_PER_M = 22.0


def _de(v: float) -> str:
    return f"{v:.2f}".replace(".", ",")


def profile_svg(elements: list[dict], available, title: str, subtitle: str = "") -> str:
    """Scaled cross section: one rectangle per element (width in metres), labels, available-width bracket."""
    shown = [e for e in elements if e["width_m"] > 0]
    total = sum(e["width_m"] for e in shown)
    avail = _num(available)
    span = max(total, avail or 0.0, 1.0)
    margin, top, band = 16.0, 52.0, 120.0
    width = span * _PX_PER_M + 2 * margin
    height = top + band + 70
    x0 = margin + (span - total) * _PX_PER_M / 2
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
           f'viewBox="0 0 {width:.0f} {height:.0f}" font-family="sans-serif" font-size="10">',
           f'<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="#ffffff"/>',
           f'<text x="{margin}" y="18" font-size="13" font-weight="bold">{html.escape(title)}</text>',
           f'<text x="{margin}" y="34" fill="#444">{html.escape(subtitle)}</text>']
    x = x0
    for e in shown:
        w = e["width_m"] * _PX_PER_M
        colour = _COLOURS.get(e["element"], "#cccccc")
        label = f'{LABEL_DE.get(e["element"], e["element"])} {_de(e["width_m"])}'
        out.append(f'<rect x="{x:.1f}" y="{top}" width="{w:.1f}" height="{band}" fill="{colour}" stroke="#ffffff" '
                   f'stroke-width="1" data-element="{e["element"]}" data-width-m="{e["width_m"]:.2f}"><title>{html.escape(label)} m</title></rect>')
        cx, cy = x + w / 2, top + band / 2
        fill = "#ffffff" if e["element"] in ("carriageway", "bus_lane", "cycle_track", "tree_strip", "tram") else "#222"
        if w >= 70:
            out.append(f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" dominant-baseline="middle" fill="{fill}">{html.escape(label)}</text>')
        else:
            out.append(f'<text transform="translate({cx:.1f},{cy:.1f}) rotate(-90)" text-anchor="middle" '
                       f'dominant-baseline="middle" fill="{fill}" font-size="9">{html.escape(label)}</text>')
        x += w
    y = top + band + 20
    out.append(f'<text x="{x0:.1f}" y="{y + 14:.1f}" fill="#222">Soll-Bedarf {_de(total)} m</text>')
    out.append(f'<line x1="{x0:.1f}" y1="{y}" x2="{x0 + total * _PX_PER_M:.1f}" y2="{y}" stroke="#222" stroke-width="2"/>')
    if avail is not None:
        ax = margin + (span - avail) * _PX_PER_M / 2
        y2 = y + 26
        out.append(f'<line x1="{ax:.1f}" y1="{y2}" x2="{ax + avail * _PX_PER_M:.1f}" y2="{y2}" stroke="#1f6fb2" '
                   f'stroke-width="2" stroke-dasharray="6 3"/>')
        out.append(f'<text x="{ax:.1f}" y="{y2 + 14:.1f}" fill="#1f6fb2">verfügbar (Verkehrsfläche p10) {_de(avail)} m</text>')
    out.append("</svg>")
    return "\n".join(out)
