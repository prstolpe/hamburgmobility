"""Street trees and parking spaces per target cross section (prompts/26 Teil 2, design_rules.yaml trees_parking).

An estimate, not a plan: parking today from the Öffentlicher Parkraum (LBV), else OSM per side; trees from the
Straßenbaumkataster. All values from config/design_rules.yaml (section trees_parking); computed in EPSG:25832.
Missing data stays missing (None) and is never counted as zero.
"""

import math
from dataclasses import dataclass

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from config.schema.design_model import DesignRuleSet

SIDES = ("left", "right")
TREE_CLASSES = ("keep", "affected", "uncertain")


def _rule(design: DesignRuleSet, group: str, rule_id: str) -> dict:
    return next(r for r in design.trees_parking[group] if r["id"] == rule_id)


def _v(x):
    return x["value"] if isinstance(x, dict) else x


@dataclass(frozen=True)
class Params:
    assign_extra_m: float
    long_factor: float
    exclude_management: tuple
    uncertain_management: tuple
    kerb_m: dict            # orientation -> kerb length per space (parallel, perpendicular, diagonal)
    space_area_m2: dict     # orientation -> area of one space (long official areas: area / this)
    official_zero_min_length_m: float
    parking_positions: tuple
    parking_by_category: dict  # PRF-03: category -> 'none' | 'as_ist' | list of positions
    setback_m: float
    setback_cycle_track_m: float
    quantiles: tuple
    extrapolate: bool  # TP-P-04 active?
    tree_extra_m: float
    tree_no_width_max_m: float
    uncertainty_m: float
    affected: frozenset
    keep: frozenset
    uncertain: frozenset
    spacing_m: float

    @classmethod
    def from_rules(cls, design: DesignRuleSet) -> "Params":
        p1, p2 = _rule(design, "parking", "TP-P-01"), _rule(design, "parking", "TP-P-02")
        p4 = _rule(design, "parking", "TP-P-04")
        t1, t2, t3 = (_rule(design, "trees", i) for i in ("TP-T-01", "TP-T-02", "TP-T-03"))
        prf03 = next(r for r in design.profile_assignment["rules"] if r["id"] == "PRF-03")
        return cls(
            assign_extra_m=float(_v(p1["assign_extra_m"])), long_factor=float(_v(p1["long_factor"])),
            exclude_management=tuple(p1["exclude_management"]), uncertain_management=tuple(p1["uncertain_management"]),
            kerb_m={k: float(_v(v)) for k, v in p1["kerb_m_per_space"].items()},
            space_area_m2={k: float(_v(v)) for k, v in p1["space_area_m2"].items()},
            official_zero_min_length_m=float(_v(p1["official_zero_min_length_m"])),
            parking_positions=tuple(prf03["parking_positions"]),
            parking_by_category=dict(prf03["parking_by_category"]),
            setback_m=float(_v(p2["setback_m"])), setback_cycle_track_m=float(_v(p2["setback_cycle_track_m"])),
            quantiles=tuple(p4["quantiles"]), extrapolate=p4["status"] != "inactive",
            tree_extra_m=float(_v(t1["assign_extra_m"])), tree_no_width_max_m=float(_v(t1["no_width_max_m"])),
            uncertainty_m=float(_v(t2["position_uncertainty_m"])), affected=frozenset(t2["affected"]),
            keep=frozenset(t2["keep"]), uncertain=frozenset(t2["uncertain"]), spacing_m=float(_v(t3["spacing_m"])))


# --- geometry helpers ---------------------------------------------------------------------------------------


def signed_offset(line, point) -> tuple[float, float]:
    """(position along the line in m, signed distance: > 0 left of the line direction, < 0 right)."""
    t = line.project(point)
    a = line.interpolate(max(t - 0.5, 0.0))
    b = line.interpolate(min(t + 0.5, line.length))
    q = line.interpolate(t)
    cross = (b.x - a.x) * (point.y - q.y) - (b.y - a.y) * (point.x - q.x)
    d = q.distance(point)
    return t, d if cross >= 0 else -d


def nearest_assign(points: gpd.GeoSeries, seg: gpd.GeoDataFrame, max_dist: pd.Series, cap_m: float) -> pd.DataFrame:
    """Nearest segment per point within max_dist of that segment (spatial index, cap_m as search radius).
    Returns point index, segment_id, along, offset (signed, > 0 = left)."""
    idx_pt, idx_seg = seg.sindex.query(points.values, predicate="dwithin", distance=cap_m)
    if not len(idx_pt):
        return pd.DataFrame(columns=["point", "segment_id", "along", "offset"])
    d = shapely.distance(points.values[idx_pt], seg.geometry.values[idx_seg])
    cand = pd.DataFrame({"point": points.index.values[idx_pt], "seg_pos": idx_seg, "d": d})
    cand = cand[cand["d"] <= max_dist.to_numpy()[cand["seg_pos"]]]
    cand = cand.sort_values(["point", "d"]).drop_duplicates("point")
    rows = []
    geoms = seg.geometry.values
    ids = seg["segment_id"].to_numpy()
    for pt, pos in zip(cand["point"], cand["seg_pos"]):
        along, off = signed_offset(geoms[pos], points.loc[pt])
        rows.append((pt, ids[pos], along, off))
    return pd.DataFrame(rows, columns=["point", "segment_id", "along", "offset"])


# --- parking ------------------------------------------------------------------------------------------------


def usable_kerb_m(length: float, junction_start: bool, junction_end: bool, cycle_track: bool, side: str,
                  p: Params) -> float:
    """TP-P-02: kerb length minus the StVO setbacks at junction ends. Right side drives start -> end, so the end is
    "before the junction" there; on the left side the start."""
    before_end = side == "right"
    cut = 0.0
    for at_end, is_junction in ((False, junction_start), (True, junction_end)):
        if not is_junction:
            continue
        before = at_end == before_end
        cut += p.setback_cycle_track_m if (before and cycle_track) else p.setback_m
    return max(length - cut, 0.0)


def osm_spaces(position: str | None, orientation: str | None, usable: float, factor: float, p: Params) -> float | None:
    """Spaces on one side from the OSM tag: None = unknown, 0 = no parking."""
    if position is None or position == "separate":
        return None
    if position == "no" or position not in p.parking_positions:
        return 0.0
    kerb = p.kerb_m.get(orientation or "parallel", p.kerb_m["parallel"])
    return usable / kerb * factor


def official_space_count(geom, orientation: str | None, p: Params) -> float:
    """One area = one space; a long area (a row) counts area / area of one space of its orientation (TP-P-01)."""
    rect = geom.minimum_rotated_rectangle
    if rect.geom_type != "Polygon":
        return 1.0
    c = np.asarray(rect.exterior.coords)
    long_side = max(math.hypot(*(c[1] - c[0])), math.hypot(*(c[2] - c[1])))
    kind = {"längs": "parallel", "quer": "perpendicular", "schräg": "diagonal"}.get(orientation or "", "parallel")
    # a single space is at most about one parallel space long (a perpendicular space's long side is its depth)
    if long_side <= p.long_factor * p.kerb_m["parallel"]:
        return 1.0
    return max(geom.area / p.space_area_m2[kind], 1.0)


# --- cross section bands and trees --------------------------------------------------------------------------


def bands(elements: list[dict], available: float | None, mirrored: bool = False) -> list[tuple[str, float, float]]:
    """Bands (element, inner, outer) as signed offsets from the axis (> 0 = left). Centre elements around the axis,
    side elements outward in their order, unused width as 'rest' at the outer edge of both sides."""
    centre = [e for e in elements if e["side"] == "centre"]
    left = [e for e in elements if e["side"] == "left"]          # outer -> inner
    right = [e for e in elements if e["side"] == "right"]        # inner -> outer
    if mirrored:
        left, right = list(reversed(right)), list(reversed(left))
    total = sum(e["width_m"] for e in elements)
    rest = max((available or 0.0) - total, 0.0) / 2
    out = []
    wc = sum(e["width_m"] for e in centre)
    x = wc / 2
    for e in centre:                                            # from the left edge to the right edge
        out.append((e["element"], x, x - e["width_m"]))
        x -= e["width_m"]
    x = wc / 2
    for e in reversed(left):                                    # inner -> outer on the left (> 0)
        out.append((e["element"], x, x + e["width_m"]))
        x += e["width_m"]
    out.append(("rest", x, x + rest))
    x = -wc / 2
    for e in right:                                             # inner -> outer on the right (< 0)
        out.append((e["element"], x, x - e["width_m"]))
        x -= e["width_m"]
    out.append(("rest", x, x - rest))
    return out


def element_at(offset: float, bs: list[tuple[str, float, float]]) -> str:
    """Element at a signed offset; outside the profile counts as 'rest' (front gardens, verge)."""
    for el, a, b in bs:
        if min(a, b) <= offset <= max(a, b):
            return el
    return "rest"


def tree_class(element: str, p: Params) -> str:
    if element in p.affected:
        return "affected"
    if element in p.uncertain:
        return "uncertain"
    return "keep"


def classify_tree(offset: float, elements: list[dict], available: float | None, p: Params) -> tuple[bool, bool, float, bool]:
    """(surely affected, possibly affected, central estimate 0/0.5/1, in a target tree strip) over both profile
    orientations and the position uncertainty (TP-T-02): the lower count needs 'affected' in every variant, the upper
    one 'affected' or 'uncertain' in any variant; the central estimate is the share of the two orientations without
    shift in which the tree is 'affected' ('uncertain' counts as kept there)."""
    classes, central, strip = [], [], False
    for mirrored in (False, True):
        bs = bands(elements, available, mirrored)
        for shift in (-p.uncertainty_m, 0.0, p.uncertainty_m):
            el = element_at(offset + shift, bs)
            classes.append(tree_class(el, p))
            if shift == 0.0:
                central.append(tree_class(el, p) == "affected")
                strip |= el == "tree_strip"
    surely = all(c == "affected" for c in classes)
    possibly = any(c in ("affected", "uncertain") for c in classes)
    return surely, possibly, sum(central) / len(central), strip


def side_elements(elements: list[dict], name: str) -> dict[str, bool]:
    """Does the profile have the element on its left / right side?"""
    return {s: any(e["element"] == name and e["side"] == s for e in elements) for s in SIDES}


def target_parking(today: dict[str, float | None], usable: dict[str, float], elements: list[dict], factor: float,
                   p: Params, cat: str | None = None, parking_removed: bool = False,
                   position_known: dict[str, bool] | None = None) -> tuple[float | None, float | None]:
    """TP-P-03: (min, max) spaces in the target. The category decides (PRF-03 parking_by_category): none -> 0;
    as_ist -> today's spaces stay per side, at most as many as fit parallel; a list of positions -> only sides with a
    parking row in the profile (both assignments of profile sides to street sides; where the position is unknown
    today, 0 to today). Degrade step D1 (parking removed) -> 0. None as lower bound when today is unknown on a side
    that may keep parking (then only the upper bound is known)."""
    policy = p.parking_by_category.get(cat, "as_ist") if isinstance(cat, str) else "as_ist"
    if policy == "none" or parking_removed:
        return 0.0, 0.0
    cap = {s: usable[s] / p.kerb_m["parallel"] * factor for s in SIDES}
    if policy == "as_ist":
        lo = hi = 0.0
        unknown = False
        for s in SIDES:
            t = today[s]
            if t is None:
                unknown = True
                hi += cap[s]
            else:
                lo += min(t, cap[s])
                hi += min(t, cap[s])
        return (None if unknown else lo), hi
    rows = side_elements(elements, "parking_parallel")
    known = position_known or {s: True for s in SIDES}
    results = []
    for mapping in ({"left": "left", "right": "right"}, {"left": "right", "right": "left"}):
        lo = hi = 0.0
        unknown = False
        for s in SIDES:
            t = today[s]
            if rows[mapping[s]]:
                if t is None:
                    unknown = True
                    hi += cap[s]
                else:
                    kept = min(t, cap[s]) if t > 0 else cap[s]  # surely none today, a row in the target: new
                    lo += kept
                    hi += kept
            elif not known[s] and t:
                hi += min(t, cap[s])  # parking position unknown today: it may be an allowed one
        results.append((lo, hi, unknown))
    lo = min(r[0] for r in results)
    hi = max(r[1] for r in results)
    return (None if any(r[2] for r in results) else lo), hi


def new_trees(usable: dict[str, float], elements: list[dict], trees_in_strip: int, p: Params) -> float:
    """TP-T-03: target tree strips / spacing minus trees already standing in the strip band."""
    strips = side_elements(elements, "tree_strip")
    length = sum(usable[s] for s in SIDES if strips[s])
    return max(length / p.spacing_m - trees_in_strip, 0.0)


def extrapolate(per_km: pd.DataFrame, missing_km: pd.DataFrame, quantiles: tuple) -> tuple[float, float]:
    """TP-P-04: spaces on segments without data, from spaces per km of their category (quantile range)."""
    lo = hi = 0.0
    for cat, km in missing_km.groupby("cat_final")["km"].sum().items():
        vals = per_km.loc[per_km["cat_final"] == cat, "per_km"]
        if not len(vals):
            continue
        lo += km * float(vals.quantile(quantiles[0]))
        hi += km * float(vals.quantile(quantiles[1]))
    return lo, hi


def _sum(s: pd.Series) -> float:
    return float(s.sum(skipna=True))


def district_summary(out: pd.DataFrame, p: Params) -> dict[str, dict]:
    """Key figures per Bezirk and for Hamburg ("Hamburg" last). Parking: counted (all known sides), complete streets
    (both sides known) with their target and change range, and the TP-P-04 extrapolation for streets without any
    data. Trees: total, possibly affected (range), new possible."""
    complete = out["park_today_complete"].astype(bool)
    per_km = out[complete & (out["length_m"] > 0)].assign(per_km=lambda d: d["park_today"] / (d["length_m"] / 1000))
    src = out[["park_src_left", "park_src_right"]]
    official = src.isin(["official", "official_zero"]).any(axis=1)
    osm = ~official & src.eq("osm").any(axis=1)
    none = src.eq("none").all(axis=1)
    groups = [(b, out["bezirk"] == b) for b in sorted(out["bezirk"].dropna().unique())] + [("Hamburg", out["bezirk"].notna())]
    res = {}
    for name, m in groups:
        d = out[m]
        km = float(d["length_m"].sum()) / 1000
        missing = d[none[m]].assign(km=lambda x: x["length_m"] / 1000)
        lo, hi = extrapolate(per_km, missing, p.quantiles) if p.extrapolate else (None, None)
        c = d[complete[m]]
        res[name] = {
            "km": km, "share_official": float(d.loc[official[m], "length_m"].sum()) / 1000 / km if km else 0.0,
            "share_osm": float(d.loc[osm[m], "length_m"].sum()) / 1000 / km if km else 0.0,
            "share_none": float(missing["km"].sum()) / km if km else 0.0,
            "share_complete": float(d.loc[complete[m], "length_m"].sum()) / 1000 / km if km else 0.0,
            "park_counted": _sum(d["park_today_known"]), "park_today_complete": _sum(c["park_today"]),
            "park_extra_lo": lo, "park_extra_hi": hi,
            "park_target_lo": _sum(c["park_target_min"]), "park_target_hi": _sum(c["park_target_max"]),
            "park_change_lo": _sum(c["park_change_min"]), "park_change_hi": _sum(c["park_change_max"]),
            "trees_n": int(d["trees_n"].sum()), "trees_affected_lo": _sum(d["trees_affected_min"]),
            "trees_affected_hi": _sum(d["trees_affected_max"]), "trees_affected_mid": _sum(d["trees_affected_mid"]),
            "trees_new": _sum(d["trees_new"]),
        }
    return res


def _num(v, digits: int = 1):
    return None if v is None or (isinstance(v, float) and math.isnan(v)) else round(float(v), digits)


def profile_block(r) -> dict:
    """Block `trees_parking` of a segment profile (raw values; the website rounds and words them)."""
    return {
        "parking": {"today_left": _num(r.park_today_left), "today_right": _num(r.park_today_right),
                    "src_left": r.park_src_left, "src_right": r.park_src_right,
                    "today": _num(r.park_today), "today_known": _num(r.park_today_known),
                    "complete": bool(r.park_today_complete), "uncertain": _num(r.park_uncertain),
                    "target_min": _num(r.park_target_min), "target_max": _num(r.park_target_max),
                    "change_min": _num(r.park_change_min), "change_max": _num(r.park_change_max)},
        "trees": {"n": int(r.trees_n), "affected_min": _num(r.trees_affected_min, 0),
                  "affected_mid": _num(r.trees_affected_mid), "affected_max": _num(r.trees_affected_max, 0),
                  "new": _num(r.trees_new)},
    }


def rounded_summary(summary: dict[str, dict]) -> dict[str, dict]:
    return {k: {f: (None if v is None else round(v, 3) if f.startswith("share") or f == "km" else round(v))
                for f, v in d.items()} for k, d in summary.items()}
