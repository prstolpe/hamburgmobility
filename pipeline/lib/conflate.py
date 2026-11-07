"""Conflation helpers: match official lines to OSM segments (rules S-CONF-01..03 in rules.yaml).

All thresholds come in through MatchParams (from rules.yaml); there are no thresholds here.
Geometries must be in the working CRS (metres).
"""

import math
import re
from dataclasses import dataclass

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.ops import substring

from config.schema.rules_model import RuleSet

QUALITIES = ("exact", "partial", "none")
FLAT_CAP = "flat"  # official pieces do not cover beyond their ends


@dataclass(frozen=True)
class MatchParams:
    buffer_m: float
    max_angle_deg: float
    min_overlap_share: float

    @classmethod
    def from_rules(cls, rules: RuleSet) -> "MatchParams":
        t = rules.conflation.rule("S-CONF-01").thresholds
        return cls(buffer_m=t["buffer_m"].value, max_angle_deg=t["max_angle_deg"].value,
                   min_overlap_share=t["min_overlap_share"].value)


def _direction_deg(line) -> float | None:
    coords = np.asarray(line.coords)
    dx, dy = coords[-1] - coords[0]
    if dx == 0 and dy == 0:
        return None
    return math.degrees(math.atan2(dy, dx))


def angle_diff_deg(a: float, b: float) -> float:
    """Undirected angle between two directions, 0-90 degrees."""
    d = abs(a - b) % 180.0
    return min(d, 180.0 - d)


def _between(line, a, b):
    """Part of line between the projections of points a and b (None if degenerate)."""
    d0, d1 = sorted((line.project(a), line.project(b)))
    piece = substring(line, d0, d1)
    if piece.length == 0 or piece.geom_type != "LineString":
        return None
    return piece


def _local_pieces(seg, off):
    """Stretches of segment and official line that run alongside each other.

    The official line is cut at the projections of the segment ends, then the segment at the
    projections of that piece's ends. So a long or bent line is compared only where the two meet.
    """
    off_local = _between(off, shapely.Point(seg.coords[0]), shapely.Point(seg.coords[-1]))
    if off_local is None:
        return None, None
    seg_local = _between(seg, shapely.Point(off_local.coords[0]), shapely.Point(off_local.coords[-1]))
    return seg_local, off_local


def _single_line(geom):
    """Longest part of a (multi)line; official data is LineString, this guards against odd input."""
    if geom.geom_type == "LineString":
        return geom
    parts = [g for g in getattr(geom, "geoms", []) if g.geom_type == "LineString"]
    return max(parts, key=lambda g: g.length) if parts else None


def candidate_pairs(seg: gpd.GeoSeries, off: gpd.GeoSeries, params: MatchParams,
                    angle_only: bool = False) -> pd.DataFrame:
    """All (segment, official) pairs within buffer_m with overlap shares, angle and Hausdorff distance.

    passed = angle within max_angle_deg and (overlap_seg or overlap_off >= min_overlap_share);
    with angle_only=True only the angle counts (zone shares, S-CONF-02).
    """
    cols = ["seg_idx", "off_idx", "overlap_seg", "overlap_off", "angle_deg", "hausdorff_m", "passed"]
    if seg.empty or off.empty:
        return _typed_pairs([], cols)
    left = gpd.GeoDataFrame(geometry=seg.values, index=seg.index, crs=seg.crs)
    right = gpd.GeoDataFrame(geometry=off.buffer(params.buffer_m, cap_style=FLAT_CAP).values,
                             index=off.index, crs=off.crs)
    hits = gpd.sjoin(left, right, predicate="intersects", how="inner")
    rows = []
    for seg_idx, off_idx in zip(hits.index, hits["index_right"]):
        s, o = seg.loc[seg_idx], _single_line(off.loc[off_idx])
        if o is None or s.length == 0:
            continue
        o_buf = o.buffer(params.buffer_m, cap_style=FLAT_CAP)
        s_buf = s.buffer(params.buffer_m, cap_style=FLAT_CAP)
        overlap_seg = s.intersection(o_buf).length / s.length
        overlap_off = o.intersection(s_buf).length / o.length if o.length else 0.0
        seg_local, off_local = _local_pieces(s, o)
        a_seg = _direction_deg(seg_local) if seg_local is not None else None
        a_off = _direction_deg(off_local) if off_local is not None else None
        angle = angle_diff_deg(a_seg, a_off) if a_seg is not None and a_off is not None else None
        hausdorff = shapely.hausdorff_distance(seg_local, off_local) if angle is not None else None
        angle_ok = angle is not None and angle <= params.max_angle_deg
        overlap_ok = max(overlap_seg, overlap_off) >= params.min_overlap_share
        rows.append((seg_idx, off_idx, overlap_seg, overlap_off, angle, hausdorff,
                     angle_ok and (angle_only or overlap_ok)))
    return _typed_pairs(rows, cols)


def _typed_pairs(rows: list, cols: list[str]) -> pd.DataFrame:
    # Fixed dtypes so that empty results still index and group correctly.
    df = pd.DataFrame(rows, columns=cols)
    df["passed"] = df["passed"].astype(bool)
    for col in ("overlap_seg", "overlap_off", "angle_deg", "hausdorff_m"):
        df[col] = df[col].astype(float)
    return df


def _coverage(seg: gpd.GeoSeries, off: gpd.GeoSeries, pairs: pd.DataFrame, buffer_m: float) -> pd.Series:
    """Share of each segment's length inside the union of the buffers of its passed candidates."""
    out = pd.Series(0.0, index=seg.index)
    for seg_idx, group in pairs.loc[pairs["passed"]].groupby("seg_idx"):
        s = seg.loc[seg_idx]
        union = shapely.union_all(off.loc[group["off_idx"]].buffer(buffer_m, cap_style=FLAT_CAP).values)
        out.loc[seg_idx] = s.intersection(union).length / s.length if s.length else 0.0
    return out


def match_lines(seg: gpd.GeoSeries, off: gpd.GeoSeries, params: MatchParams) -> pd.DataFrame:
    """S-CONF-01: match quality and best official candidate per segment (index = seg.index).

    exact: segment covered >= min_overlap_share by passed candidates; partial: passed candidate,
    less coverage; none: no passed candidate. best_off_idx = passed candidate with the smallest
    Hausdorff distance (ties: larger overlap_seg, then lower index).
    """
    pairs = candidate_pairs(seg, off, params)
    coverage = _coverage(seg, off, pairs, params.buffer_m)
    out = pd.DataFrame(index=seg.index)
    out["n_candidates"] = pairs.groupby("seg_idx").size().reindex(seg.index, fill_value=0).astype(int)
    passed = pairs.loc[pairs["passed"]].copy()
    out["n_passed"] = passed.groupby("seg_idx").size().reindex(seg.index, fill_value=0).astype(int)
    out["coverage"] = coverage
    best = (passed.assign(_neg_overlap=-passed["overlap_seg"])
            .sort_values(["seg_idx", "hausdorff_m", "_neg_overlap", "off_idx"])
            .drop_duplicates("seg_idx").set_index("seg_idx"))
    for col in ("off_idx", "overlap_seg", "overlap_off", "angle_deg", "hausdorff_m"):
        name = "best_off_idx" if col == "off_idx" else col
        out[name] = best[col].reindex(seg.index) if not best.empty else None
    out["passed_off_idx"] = (passed.groupby("seg_idx")["off_idx"].apply(lambda s: sorted(s.tolist()))
                             .reindex(seg.index) if not passed.empty else None)
    out["passed_off_idx"] = out["passed_off_idx"].map(lambda v: v if isinstance(v, list) else [])
    out["quality"] = np.where(out["n_passed"] == 0, "none",
                              np.where(out["coverage"] >= params.min_overlap_share, "exact", "partial"))
    return out


def zone_share(seg: gpd.GeoSeries, lines: gpd.GeoSeries, params: MatchParams) -> pd.Series:
    """S-CONF-02: share of each segment's length inside the buffer of zone lines with the same direction."""
    pairs = candidate_pairs(seg, lines, params, angle_only=True)
    return _coverage(seg, lines, pairs, params.buffer_m)


def hvs_from_neighbours(df: pd.DataFrame, exclude_highways: set) -> tuple[pd.Series, pd.Series]:
    """S-CONF-04: in_hvs and its source per segment.

    exact: matched exactly to the HVS lines. neighbour: matched partially and connected over segments of the same
    street name (sharing a node) to an exactly matched one. Segments with a highway in exclude_highways
    (S-NET-04 access roads, e.g. parallel service carriageways) never belong to the HVS.
    df needs name, node_u, node_v, highway, hvs_match_quality, in_hvs."""
    ok = ~df["highway"].isin(exclude_highways)
    exact = df["in_hvs"].fillna(False).astype(bool) & ok
    cand = ok & df["name"].notna() & (df["hvs_match_quality"] == "partial")
    parent: dict = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    use = df.index[(exact | cand) & df["name"].notna()]
    for i in use:  # union segments with the same name over their end nodes
        r = df.loc[i]
        a, b = find(("seg", i)), None
        for node in (r["node_u"], r["node_v"]):
            b = find(("node", r["name"], node))
            parent[b] = a
            a = find(a)
    seeded = {find(("seg", i)) for i in df.index[exact] if pd.notna(df.loc[i, "name"])}
    use_set = set(use)
    neighbour = pd.Series([bool(cand.loc[i]) and find(("seg", i)) in seeded if i in use_set else False for i in df.index],
                          index=df.index)
    in_hvs = exact | neighbour
    source = pd.Series(np.where(exact, "exact", np.where(neighbour, "neighbour", None)), index=df.index, dtype="object")
    return in_hvs, source


# --- speeds (S-CONF-03) ----------------------------------------------------------------------

_SPEED = re.compile(r"^\s*(\d+)\s*km/h\s*$")
_SONST = re.compile(r"sonst\s*(\d+)\s*km/h")
_LEADING_SPEED = re.compile(r"^\s*(\d+)\s*km/h\s+\S")
NO_RULE = "keine Sonderregelung"


def parse_speed_kmh(text: str | None, text_values: dict | None = None) -> int | None:
    """'30 km/h' -> 30. Texts listed in text_values (S-CONF-03, e.g. '5-7 km/h') -> their value;
    variable limits and other texts -> None."""
    if not isinstance(text, str):
        return None
    if text_values and text.strip() in text_values:
        return int(text_values[text.strip()])
    m = _SPEED.match(text)
    return int(m.group(1)) if m else None


@dataclass(frozen=True)
class SpeedReading:
    regular_kmh: int | None
    conditional_kmh: int | None
    rule_text: str | None
    ambiguous: bool


def resolve_speed(speed_text: str | None, rule_text: str | None, text_values: dict | None = None) -> SpeedReading:
    """Separate the regular speed from a time-limited rule; the time-limited speed is never regular.

    'sonst N km/h': regular = N, time-limited = signed speed if it differs.
    'N km/h <time window>': time-limited = N, regular = signed speed if it differs, else unknown.
    """
    signed = parse_speed_kmh(speed_text, text_values)
    if not isinstance(rule_text, str) or not rule_text.strip() or rule_text.strip() == NO_RULE:
        return SpeedReading(signed, None, None, False)
    if m := _SONST.search(rule_text):
        regular = int(m.group(1))
        conditional = signed if signed != regular else None
        return SpeedReading(regular, conditional, rule_text, conditional is None)
    if m := _LEADING_SPEED.match(rule_text):
        conditional = int(m.group(1))
        regular = signed if signed != conditional else None
        return SpeedReading(regular, conditional, rule_text, regular is None)
    return SpeedReading(None, None, rule_text, True)
