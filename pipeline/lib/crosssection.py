"""Cross-section helpers: transects, street-space widths, aggregation, feasibility (rules S-XS-01..06).

All parameters come in through XsParams (from rules.yaml); there are no thresholds here.
Geometries must be in the working CRS (metres).
"""

import math
from dataclasses import dataclass

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from config.schema.rules_model import RuleSet

# Numerical tolerance for touching parcels and the centre point (not a planning threshold).
GAP_TOL_M = 0.05


@dataclass(frozen=True)
class XsParams:
    simplify_m: float
    spacing_m: float
    half_length_m: float
    tangent_half_m: float
    nutzart: frozenset[str]
    node_exclusion_m: float
    quantile: float
    min_run: int

    @classmethod
    def from_rules(cls, rules: RuleSet) -> "XsParams":
        x = rules.crosssection
        t1 = x.rule("S-XS-01").thresholds
        t5 = x.rule("S-XS-05").thresholds
        return cls(
            simplify_m=t1["simplify_m"].value, spacing_m=t1["spacing_m"].value,
            half_length_m=t1["half_length_m"].value, tangent_half_m=t1["tangent_half_m"].value,
            nutzart=frozenset(x.rule("S-XS-02").alkis_nutzart),
            node_exclusion_m=x.rule("S-XS-04").thresholds["node_exclusion_m"].value,
            quantile=t5["quantile"].value, min_run=int(t5["min_run"].value),
        )


def required_widths(rules: RuleSet) -> dict[str, float]:
    """S-XS-06: required street-space width per target; for ranges the bound named in range_reference."""
    r = rules.crosssection.rule("S-XS-06")
    out = {}
    for target in r.targets:
        w = rules.required_width[target]
        if w.value is not None:
            out[target] = w.value
        else:
            out[target] = w.range[0] if r.range_reference == "min" else w.range[1]
    return out


# --- S-XS-01 transects -----------------------------------------------------------------------


def make_transects(lines: gpd.GeoSeries, params: XsParams) -> gpd.GeoDataFrame:
    """Perpendicular transects every spacing_m (first at spacing_m / 2) on the simplified lines.

    Columns: seg_pos (position of the line in `lines`), position_m, centre, left, right (halves from the
    centre, left = left of the direction of travel), geometry (whole transect).
    """
    rows = []
    simplified = lines.simplify(params.simplify_m)
    for pos, line in enumerate(simplified.to_numpy()):
        if line is None or line.is_empty or line.length == 0:
            continue
        length = line.length
        for s in np.arange(params.spacing_m / 2, length, params.spacing_m):
            a = line.interpolate(max(s - params.tangent_half_m, 0.0))
            b = line.interpolate(min(s + params.tangent_half_m, length))
            dx, dy = b.x - a.x, b.y - a.y
            norm = math.hypot(dx, dy)
            if norm == 0:
                continue
            nx, ny = -dy / norm * params.half_length_m, dx / norm * params.half_length_m
            c = line.interpolate(s)
            rows.append((pos, float(s), c, (c.x + nx, c.y + ny), (c.x - nx, c.y - ny)))
    if not rows:
        return gpd.GeoDataFrame({"seg_pos": [], "position_m": [], "centre": [], "left": [], "right": []},
                                geometry=[], crs=lines.crs)
    pos, s, centre, left_end, right_end = zip(*rows)
    centre = np.array(centre, dtype=object)
    cx = shapely.get_x(centre)
    cy = shapely.get_y(centre)
    left = shapely.linestrings([[(x, y), le] for x, y, le in zip(cx, cy, left_end)])
    right = shapely.linestrings([[(x, y), re] for x, y, re in zip(cx, cy, right_end)])
    whole = shapely.linestrings([[le, re] for le, re in zip(left_end, right_end)])
    return gpd.GeoDataFrame({
        "seg_pos": np.array(pos, dtype=int), "position_m": np.array(s),
        "centre": gpd.GeoSeries(centre, crs=lines.crs), "left": gpd.GeoSeries(left, crs=lines.crs),
        "right": gpd.GeoSeries(right, crs=lines.crs)}, geometry=whole, crs=lines.crs)


def near_points(centres: gpd.GeoSeries, points: gpd.GeoSeries, dist_m: float) -> np.ndarray:
    """S-XS-04: True where a centre lies within dist_m of any point."""
    out = np.zeros(len(centres), dtype=bool)
    if len(points) and len(centres):
        i, _ = shapely.STRtree(points.to_numpy()).query(centres.to_numpy(), predicate="dwithin", distance=dist_m)
        out[np.unique(i)] = True
    return out


# --- S-XS-02 / S-XS-03 boundaries ------------------------------------------------------------


def _pieces(halves: gpd.GeoSeries, polygons: gpd.GeoSeries):
    """(half index, start distance, end distance) of each piece of the half inside a polygon."""
    if not len(polygons) or not len(halves):
        return np.array([], int), np.array([]), np.array([])
    h = halves.to_numpy()
    i_h, i_p = shapely.STRtree(polygons.to_numpy()).query(h, predicate="intersects")
    inter = shapely.intersection(h[i_h], polygons.to_numpy()[i_p])
    idx, starts, ends = [], [], []
    for k, geom in zip(i_h, inter):
        for part in shapely.get_parts(geom):
            if part.is_empty or part.geom_type != "LineString" or part.length == 0:
                continue
            a = shapely.line_locate_point(h[k], shapely.points(part.coords[0]))
            b = shapely.line_locate_point(h[k], shapely.points(part.coords[-1]))
            idx.append(k)
            starts.append(min(a, b))
            ends.append(max(a, b))
    return np.array(idx, int), np.array(starts), np.array(ends)


def covered_extent(halves: gpd.GeoSeries, polygons: gpd.GeoSeries):
    """S-XS-02: distance from the centre to the first boundary of the connected covered stretch.

    Returns (distance, reached_end, centre_covered); distance is NaN where the centre is not covered.
    Touching polygons (gap <= GAP_TOL_M) count as one area.
    """
    n = len(halves)
    dist = np.full(n, np.nan)
    lengths = shapely.length(halves.to_numpy())
    idx, starts, ends = _pieces(halves, polygons)
    order = np.lexsort((starts, idx))
    for k in np.unique(idx):
        sel = order[idx[order] == k]
        reach = None
        for a, b in zip(starts[sel], ends[sel]):
            if reach is None:
                if a > GAP_TOL_M:
                    break
                reach = b
            elif a <= reach + GAP_TOL_M:
                reach = max(reach, b)
            else:
                break
        if reach is not None:
            dist[k] = reach
    covered = ~np.isnan(dist)
    reached_end = covered & (dist >= lengths - GAP_TOL_M)
    return dist, reached_end, covered


def first_hit(halves: gpd.GeoSeries, polygons: gpd.GeoSeries):
    """S-XS-03: distance from the centre to the first polygon along the half (NaN if none).

    Returns (distance, centre_inside); centre_inside is True where the centre lies in a polygon.
    """
    dist = np.full(len(halves), np.nan)
    idx, starts, _ = _pieces(halves, polygons)
    for k, a in zip(idx, starts):
        if np.isnan(dist[k]) or a < dist[k]:
            dist[k] = a
    inside = ~np.isnan(dist) & (dist <= GAP_TOL_M)
    return dist, inside


# --- S-XS-05 aggregation ---------------------------------------------------------------------


def _narrow_runs(positions: np.ndarray, widths: np.ndarray, p10: float, min_run: int) -> list[dict]:
    runs, current = [], []
    for s, w in list(zip(positions, widths)) + [(np.nan, np.nan)]:
        if not np.isnan(w) and w < p10:
            current.append((s, w))
            continue
        if len(current) >= min_run:
            runs.append({"from_m": float(current[0][0]), "to_m": float(current[-1][0]),
                         "min_width_m": round(float(min(w for _, w in current)), 2)})
        current = []
    return runs


def aggregate_widths(df: pd.DataFrame, params: XsParams) -> pd.DataFrame:
    """Per seg_pos: median, p10, minimum, number of valid transects and narrow points (NaN width = invalid)."""
    rows = {}
    for pos, g in df.sort_values(["seg_pos", "position_m"]).groupby("seg_pos", sort=True):
        w = g["width"].to_numpy(dtype=float)
        valid = w[~np.isnan(w)]
        if len(valid):
            p10 = float(np.quantile(valid, params.quantile))
            rows[pos] = {"width_median_m": float(np.median(valid)), "width_p10_m": p10,
                         "width_min_m": float(valid.min()), "n_valid": int(len(valid)),
                         "narrow_points": _narrow_runs(g["position_m"].to_numpy(), w, p10, params.min_run)}
        else:
            rows[pos] = {"width_median_m": np.nan, "width_p10_m": np.nan, "width_min_m": np.nan, "n_valid": 0,
                         "narrow_points": []}
    return pd.DataFrame.from_dict(rows, orient="index")


# --- S-XS-06 feasibility ---------------------------------------------------------------------


def feasibility_class(ratio: float, classes) -> str | None:
    """Class name from feasibility_classes: fits (>= fits.min), tight (>= tight.min), else does_not_fit."""
    if ratio is None or np.isnan(ratio):
        return None
    if ratio >= classes["fits"].min:
        return "fits"
    if ratio >= classes["tight"].min:
        return "tight"
    return "does_not_fit"
