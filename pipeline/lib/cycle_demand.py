"""Cycle demand model (prompts/15): zones, attraction, gravity, assignment, calibration, confidence.

Rules C-DEM-01..07 in config/cycling_rules.yaml (demand_model); every value comes in through
DemandParams. Distances and costs in metres of perceived resistance (pipeline/lib/cycle_graph.py).
"""

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from scipy import stats as sstats
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from shapely.geometry import LineString, Point

from config.schema.cycling_model import CyclingRuleSet

# Value of `richtung` for counters without direction; they are the sum of the two directional
# counters at the same cross-section (checked 2026-11-05, docs/open_questions.md).
UNDIRECTED = "Keine Richtung"
NO_PRED = -9999  # scipy.sparse.csgraph marker for "no predecessor"
MIN_COST_M = 1e-6  # sparse graphs need positive weights
LOCAL_BEARING_M = 5.0  # half length of the piece used for a line's local direction (geometry, not a rule)


@dataclass(frozen=True)
class DemandParams:
    zone_m: float
    weights: dict
    rapid_transit_route_types: tuple
    alkis_gebnutzbez: tuple
    alkis_rellage_excluded: tuple
    excluded_functions: frozenset
    mixed_use_functions: frozenset
    mixed_use_storeys: float
    beta_per_km: float
    distance_band_km: tuple
    method: str
    iterations: int
    noise_sigma: float
    seed: int
    scope: str
    min_valid_weekdays: int
    transect_half_m: float
    transect_min_angle_deg: float
    counter_snap_m: float
    dbradplus_snap_m: float
    high_radius_m: float
    high_ratio_band: tuple
    border_m: float
    low_flow_day: float
    peak_hour_share: float

    @classmethod
    def from_rules(cls, cyc: CyclingRuleSet) -> "DemandParams":
        r = {x["id"]: x for x in cyc.demand_model["rules"]}
        return cls(
            zone_m=float(r["C-DEM-01"]["zone_m"]),
            weights={k: float(v) for k, v in r["C-DEM-02"]["weights"].items()},
            rapid_transit_route_types=tuple(int(t) for t in r["C-DEM-02"]["rapid_transit_route_types"]),
            alkis_gebnutzbez=tuple(r["C-DEM-03"]["alkis_gebnutzbez"]),
            alkis_rellage_excluded=tuple(r["C-DEM-03"]["alkis_rellage_excluded"]),
            excluded_functions=frozenset(r["C-DEM-03"]["excluded_functions"]),
            mixed_use_functions=frozenset(r["C-DEM-03"]["mixed_use_functions"]),
            mixed_use_storeys=float(r["C-DEM-03"]["mixed_use_storeys"]),
            beta_per_km=float(r["C-DEM-04"]["beta_per_km"]),
            distance_band_km=tuple(float(x) for x in r["C-DEM-04"]["distance_band_km"]),
            method=r["C-DEM-05"]["method"],
            iterations=int(r["C-DEM-05"]["iterations"]),
            noise_sigma=float(r["C-DEM-05"]["noise_sigma"]),
            seed=int(r["C-DEM-05"]["seed"]),
            scope=r["C-DEM-06"]["scope"],
            min_valid_weekdays=int(r["C-DEM-06"]["min_valid_weekdays"]),
            transect_half_m=float(r["C-DEM-06"]["transect_half_m"]),
            transect_min_angle_deg=float(r["C-DEM-06"]["transect_min_angle_deg"]),
            counter_snap_m=float(r["C-DEM-06"]["counter_snap_m"]),
            dbradplus_snap_m=float(r["C-DEM-06"]["dbradplus_snap_m"]),
            high_radius_m=float(r["C-DEM-07"]["high_radius_m"]),
            high_ratio_band=tuple(float(x) for x in r["C-DEM-07"]["high_ratio_band"]),
            border_m=float(r["C-DEM-07"]["border_m"]),
            low_flow_day=float(r["C-DEM-07"]["low_flow_day"]),
            peak_hour_share=float(cyc.demand["peak_hour_share_of_day"]["value"]),
        )

    def iteration_ids(self) -> list[int]:
        """aon: one run without noise (0); stochastic: runs 1..iterations with noise."""
        return [0] if self.method == "aon" else list(range(1, self.iterations + 1))


# --- C-DEM-01..03 zones and attraction -----------------------------------------------------------


def zone_index(x: np.ndarray, y: np.ndarray, zone_m: float) -> tuple[np.ndarray, np.ndarray]:
    """Zone column/row in a grid of zone_m (coordinates in the grid CRS, EPSG:3035)."""
    return np.floor(np.asarray(x) / zone_m).astype("int64"), np.floor(np.asarray(y) / zone_m).astype("int64")


def aggregate(points: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    """Sum of `columns` per zone (column `zone`)."""
    return points.groupby("zone")[list(columns)].sum()


def attraction(zones: pd.DataFrame, weights: dict) -> pd.Series:
    """C-DEM-02: sum over destination types of weight x the zone's share of the type's total.

    A type without any destination contributes nothing (its weight is not redistributed).
    """
    a = pd.Series(0.0, index=zones.index)
    for t, w in weights.items():
        total = zones[t].sum()
        if total > 0:
            a += w * zones[t] / total
    return a


def jobs_floor_area(buildings: gpd.GeoDataFrame, params: DemandParams) -> pd.Series:
    """C-DEM-03: floor area proxy per ALKIS building (footprint x storeys); excluded functions are 0."""
    b = buildings
    keep = b["gebnutzbez"].isin(params.alkis_gebnutzbez) & ~b["rellage"].isin(params.alkis_rellage_excluded)
    keep &= ~b["funktion"].isin(params.excluded_functions)
    storeys = pd.to_numeric(b["anzahlgs"], errors="coerce").fillna(1.0).clip(lower=1.0)
    storeys = storeys.where(~b["funktion"].isin(params.mixed_use_functions), params.mixed_use_storeys)
    return (b.geometry.area * storeys).where(keep, 0.0)


# --- C-DEM-04 gravity --------------------------------------------------------------------------


def gravity_row(production: float, attr: np.ndarray, d_km: np.ndarray, beta: float,
                band: tuple[float, float]) -> np.ndarray:
    """Trips from one origin: production split over destinations in the band by attr x exp(-beta d)."""
    lo, hi = band
    d = np.asarray(d_km, dtype="float64")
    inside = np.isfinite(d) & (d >= lo) & (d <= hi)
    w = np.where(inside, np.asarray(attr, dtype="float64") * np.exp(-beta * np.where(inside, d, 0.0)), 0.0)
    total = w.sum()
    return production * w / total if total > 0 else np.zeros_like(w)


# --- C-DEM-05 assignment -----------------------------------------------------------------------


def noise_factors(n: int, sigma: float, seed: int, iteration: int) -> np.ndarray:
    """Log-normal factors (median 1) for the resistances of one run; iteration 0 has no noise."""
    if iteration == 0:
        return np.ones(n)
    return np.random.default_rng([seed, iteration]).lognormal(mean=0.0, sigma=sigma, size=n)


def subtree_sums(pred: np.ndarray, demand: np.ndarray) -> np.ndarray:
    """Demand of each node plus all nodes below it in the shortest-path tree (pred: parent or NO_PRED)."""
    pred = np.asarray(pred)
    n = len(pred)
    has = pred >= 0
    depth = has.astype("int64")
    anc = np.where(has, pred, -1)
    while (anc >= 0).any():  # pointer jumping: hops to the root
        j = anc >= 0
        new_depth = depth.copy()
        new_depth[j] = depth[j] + depth[anc[j]]
        new_anc = anc.copy()
        new_anc[j] = anc[anc[j]]
        depth, anc = new_depth, new_anc
    s = np.asarray(demand, dtype="float64").copy()
    order = np.argsort(depth, kind="stable")
    sorted_depth = depth[order]
    for level in range(int(sorted_depth[-1]) if n else 0, 0, -1):
        lo, hi = np.searchsorted(sorted_depth, [level, level + 1])
        nodes = order[lo:hi]
        np.add.at(s, pred[nodes], s[nodes])
    return s


def assign_od(n_nodes: int, tail: np.ndarray, head: np.ndarray, cost: np.ndarray, origins: Sequence[int],
              dest_nodes: np.ndarray, od: Callable[[int, np.ndarray], np.ndarray], batch: int = 64) -> np.ndarray:
    """All-or-nothing assignment on shortest paths; returns the flow per arc (input order).

    od(i, d) gives the trips from origins[i] to dest_nodes, given the distances d (m) to them.
    Of parallel arcs (same tail and head) only the cheapest carries flow.
    """
    tail, head = np.asarray(tail, dtype="int64"), np.asarray(head, dtype="int64")
    cost = np.maximum(np.asarray(cost, dtype="float64"), MIN_COST_M)
    order = np.lexsort((cost, head, tail))
    keys_all = tail[order] * n_nodes + head[order]
    first = np.ones(len(order), dtype=bool)
    first[1:] = keys_all[1:] != keys_all[:-1]
    chosen = order[first]
    keys = keys_all[first]  # sorted
    mat = csr_matrix((cost[chosen], (tail[chosen], head[chosen])), shape=(n_nodes, n_nodes))
    flows = np.zeros(len(tail))
    origins = list(origins)
    for start in range(0, len(origins), batch):
        idx = origins[start:start + batch]
        dist, pred = dijkstra(mat, directed=True, indices=idx, return_predecessors=True)
        for row, _ in enumerate(idx):
            trips = od(start + row, dist[row, dest_nodes])
            if not np.any(trips > 0):
                continue
            demand = np.zeros(n_nodes)
            np.add.at(demand, dest_nodes, trips)
            s = subtree_sums(pred[row], demand)
            v = np.flatnonzero((pred[row] >= 0) & (s > 0))
            k = pred[row][v].astype("int64") * n_nodes + v
            flows[chosen[np.searchsorted(keys, k)]] += s[v]
    return flows


# --- C-DEM-06 counters and calibration ---------------------------------------------------------


def counter_values(stations: pd.DataFrame, daily: pd.DataFrame, min_valid_weekdays: int) -> pd.DataFrame:
    """Mean Monday–Friday count (days with count > 0) of the counters without direction; index thing_id."""
    ids = stations.loc[stations["richtung"] == UNDIRECTED, "thing_id"]
    d = daily[daily["thing_id"].isin(ids) & (daily["count"] > 0)].copy()
    d = d[pd.to_datetime(d["date"]).dt.day_of_week < 5]
    g = d.groupby("thing_id")["count"].agg(count_weekday="mean", n_weekdays="size")
    return g[g["n_weekdays"] >= min_valid_weekdays]


def calibration_factor(counts: np.ndarray, model: np.ndarray) -> float:
    """Geometric mean of count / model over cross-sections with positive values."""
    c, m = np.asarray(counts, dtype="float64"), np.asarray(model, dtype="float64")
    ok = (c > 0) & (m > 0)
    if not ok.any():
        raise ValueError("no cross-section with positive count and model value")
    return float(np.exp(np.mean(np.log(c[ok] / m[ok]))))


def fit_stats(counts: np.ndarray, cal: np.ndarray) -> dict:
    c, m = np.asarray(counts, dtype="float64"), np.asarray(cal, dtype="float64")
    ok = (c > 0) & (m > 0)
    c, m = c[ok], m[ok]
    return {"n": int(ok.sum()), "pearson": float(np.corrcoef(c, m)[0, 1]),
            "pearson_log": float(np.corrcoef(np.log(c), np.log(m))[0, 1]),
            "spearman": float(sstats.spearmanr(c, m).statistic), "mrd": float(np.mean(np.abs(m - c) / c)),
            "median_ratio": float(np.median(c / m)),
            "share_within_factor_2": float(np.mean((c / m >= 0.5) & (c / m <= 2.0)))}


def _local_direction(line: LineString, at: Point) -> np.ndarray:
    s = line.project(at)
    a = line.interpolate(max(s - LOCAL_BEARING_M, 0.0))
    b = line.interpolate(min(s + LOCAL_BEARING_M, line.length))
    v = np.array([b.x - a.x, b.y - a.y])
    norm = np.hypot(*v)
    return v / norm if norm > 0 else v


def _acute_angle_deg(u: np.ndarray, v: np.ndarray) -> float:
    c = abs(float(np.dot(u, v)))
    return math.degrees(math.acos(min(c, 1.0)))


def cross_section_rows(geoms: gpd.GeoSeries, point: Point, half_m: float, snap_m: float,
                       min_angle_deg: float) -> list[int]:
    """Row positions of the edges that a cross-section at the counter cuts.

    The cross-section is a line of 2 x half_m through the counter, perpendicular to the nearest edge
    (at most snap_m away). Edges count if they cross it at an angle of at least min_angle_deg, so a
    street that runs along the cross-section does not count. Empty if no edge is within snap_m.
    """
    cand = geoms.sindex.query(point.buffer(snap_m), predicate="intersects")
    if len(cand) == 0:
        return []
    d = shapely.distance(geoms.values[cand], point)
    if d.min() > snap_m:
        return []
    nearest = geoms.values[cand[int(np.argmin(d))]]
    t = _local_direction(nearest, point)
    nvec = np.array([-t[1], t[0]])
    transect = LineString([(point.x + nvec[0] * half_m, point.y + nvec[1] * half_m),
                           (point.x - nvec[0] * half_m, point.y - nvec[1] * half_m)])
    rows = []
    for i in geoms.sindex.query(transect, predicate="intersects"):
        line = geoms.values[i]
        cut = line.intersection(transect)
        at = cut if cut.geom_type == "Point" else cut.representative_point()
        if _acute_angle_deg(_local_direction(line, at), nvec) >= min_angle_deg:
            rows.append(int(i))
    return sorted(rows)


# --- C-DEM-07 confidence and peak hour --------------------------------------------------------


def confidence(near_good_counter: np.ndarray, near_border: np.ndarray, rural: np.ndarray, flow: np.ndarray,
               low_flow_day: float) -> np.ndarray:
    """hoch near a well fitting counter; niedrig at the border, in rural areas, at low or missing flow; else mittel."""
    flow = np.asarray(flow, dtype="float64")
    missing = np.isnan(flow)
    low = np.asarray(near_border, bool) | np.asarray(rural, bool) | missing | (np.nan_to_num(flow) < low_flow_day)
    out = np.where(np.asarray(near_good_counter, bool), "hoch", np.where(low, "niedrig", "mittel"))
    return np.where(missing, "niedrig", out).astype(object)


def peak_hour(day: np.ndarray, share: float) -> np.ndarray:
    return np.asarray(day, dtype="float64") * share
