"""Five principles of cycle network quality (prompts/17): checks P-COH/P-DIR/P-SAF/P-COM/P-ATT, Ist and Soll.

Thresholds of the checks come from config/cycling_rules.yaml `principles`; how check values become scores
(C-PRI-01..16) from `principle_scoring`; crash assignment from config/rules.yaml P-RISK-01. Every value
comes in through PrincipleParams. Scores are 0–1, NaN = unknown. Geometries in EPSG:25832.
"""

import math
import re
from dataclasses import dataclass

import numpy as np
import pandas as pd
import shapely
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

from config.schema.cycling_model import CyclingRuleSet
from config.schema.provenance import META_KEYS
from config.schema.rules_model import RuleSet
from pipeline.lib.cycle_graph import LANE_VALUES
from pipeline.lib.cycle_network import Graph

RURAL = ("GOW80", "ETW60")
# Facilities with one direction per side (one-way intensity rule of widths_m.project_target.intensity_upgrade).
ONEWAY_FACILITIES = frozenset({"separated_oneway_both", "cycle_lane"})
_UPGRADE = re.compile(r"^\s*(oneway|twoway)\s+peak_h\s*>\s*(\d+(?:\.\d+)?)\s*$")
_WIDTH = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*(m)?\s*$")


@dataclass(frozen=True)
class PrincipleParams:
    weights: dict
    check_principle: dict        # check id -> principle
    forms: dict                  # check id -> score form
    network_only: frozenset
    unavailable: dict            # check id -> reason
    imp_condition: dict          # C-IMP id -> condition name
    by_condition: dict
    lane_upgrade: str
    sidepath_oneway: str
    sidepath_twoway: str
    matrix: dict
    satisfies: dict
    partial: dict
    partial_score: float
    detour_max: dict
    od_pairs: int
    od_seed: int
    trip_band_m: dict
    stops_max: dict
    time_loss_max: dict
    signal_delay_s: float
    give_way_delay_s: float
    lit_values: frozenset
    unlit_values: frozenset
    soll_lit: bool
    crash_snap_m: float
    crash_min_length_m: float
    required_by_facility: dict
    project_target: dict
    intensity_upgrade: tuple     # (oneway|twoway, threshold, add_m)
    smooth_surfaces: frozenset
    unpaved_surfaces: frozenset
    green_buffer_m: float
    green_nutzart: frozenset
    tree_radius_m: float
    green_target: float
    patt_dtv: float
    gap_edge_buffer_m: float
    max_changes_per_km: float
    conf_high: float
    conf_medium: float
    sens_delta: float
    top_n: int
    review_n: int
    review_seed: int

    @classmethod
    def from_rules(cls, cyc: CyclingRuleSet, road: RuleSet) -> "PrincipleParams":
        r = {x["id"]: x for x in cyc.principle_scoring["rules"]}
        checks = {c["id"]: (name, c) for name, p in cyc.principles.items() for c in p["checks"]}
        imp = cyc.routing_impedance
        cats = cyc.cycle_categories
        target = cyc.widths_m["project_target"]
        risk = road.priority.risk.thresholds
        return cls(
            weights={k: float(v) for k, v in cyc.principle_weights.items() if k not in META_KEYS},
            check_principle={cid: name for cid, (name, _) in checks.items()},
            forms=dict(r["C-PRI-01"]["score_forms"]),
            network_only=frozenset(r["C-PRI-01"]["network_only"]),
            unavailable=dict(r["C-PRI-16"]["unavailable"]),
            imp_condition={x["id"]: x["when"] for x in imp["ist_mapping"]["rules"]},
            by_condition=dict(r["C-PRI-02"]["by_condition"]),
            lane_upgrade=r["C-PRI-02"]["lane_upgrade"],
            sidepath_oneway=r["C-PRI-02"]["sidepath_oneway"],
            sidepath_twoway=r["C-PRI-02"]["sidepath_twoway"],
            matrix=cyc.separation_matrix,
            satisfies={k: frozenset(v) for k, v in r["C-PRI-03"]["satisfies"].items()},
            partial={k: frozenset(v) for k, v in r["C-PRI-03"]["partial"].items()},
            partial_score=float(r["C-PRI-03"]["partial_score"]),
            detour_max={k: float(v) for k, v in checks["P-DIR-01"][1]["thresholds"].items()},
            od_pairs=int(r["C-PRI-04"]["od_pairs_per_category"]),
            od_seed=int(r["C-PRI-04"]["seed"]),
            trip_band_m={c: (float(cats[c]["trip_length_km"]["range"][0]) * 1000, float(cats[c]["trip_length_km"]["range"][1]) * 1000)
                         for c in checks["P-DIR-01"][1]["thresholds"]},
            stops_max={k: float(v) for k, v in checks["P-DIR-02"][1]["thresholds"].items()},
            time_loss_max={k: float(v) for k, v in checks["P-DIR-03"][1]["thresholds"].items()},
            signal_delay_s=float(imp["factors"]["signal_delay_s"]),
            give_way_delay_s=float(imp["factors"]["give_way_delay_s"]),
            lit_values=frozenset(str(v) for v in r["C-PRI-06"]["lit_values"]),
            unlit_values=frozenset(str(v) for v in r["C-PRI-06"]["unlit_values"]),
            soll_lit=bool(r["C-PRI-06"]["soll_lit"]),
            crash_snap_m=float(risk["snap_m"].value),
            crash_min_length_m=float(risk["min_length_m"].value),
            required_by_facility=dict(r["C-PRI-08"]["required_by_facility"]),
            project_target=target,
            intensity_upgrade=tuple((*parse_upgrade(u["if"]), float(u["add_m"])) for u in target["intensity_upgrade"]),
            smooth_surfaces=frozenset(r["C-PRI-09"]["smooth_surfaces"]),
            unpaved_surfaces=frozenset(imp["ist_mapping"]["unpaved_surfaces"]),
            green_buffer_m=float(r["C-PRI-10"]["buffer_m"]),
            green_nutzart=frozenset(r["C-PRI-10"]["green_nutzart"]),
            tree_radius_m=float(r["C-PRI-10"]["tree_crown_radius_m"]),
            green_target=float(r["C-PRI-10"]["target_share"]),
            patt_dtv=float(checks["P-ATT-03"][1]["dtv"]),
            gap_edge_buffer_m=float(r["C-PRI-12"]["gap_edge_buffer_m"]),
            max_changes_per_km=float(r["C-PRI-12"]["max_changes_per_km"]),
            conf_high=float(r["C-PRI-13"]["high"]),
            conf_medium=float(r["C-PRI-13"]["medium"]),
            sens_delta=float(r["C-PRI-14"]["delta"]),
            top_n=int(r["C-PRI-14"]["top_n"]),
            review_n=int(r["C-PRI-15"]["review_n"]),
            review_seed=int(r["C-PRI-15"]["seed"]),
        )

    def checks_of(self, principle: str) -> list[str]:
        return [c for c, p in self.check_principle.items() if p == principle]


def _nan(v) -> bool:
    return v is None or v is pd.NA or (isinstance(v, float) and math.isnan(v))


# --- C-PRI-01 score forms ------------------------------------------------------------------------


def score(form: str, value, threshold=None) -> float:
    """Score 0–1 of one check value (C-PRI-01); NaN if the value or a needed threshold is unknown."""
    if _nan(value):
        return float("nan")
    v = float(value)
    if form == "share":
        return min(max(v, 0.0), 1.0)
    if _nan(threshold):
        return float("nan")
    t = float(threshold)
    if form == "ratio":
        return min(max(v / t, 0.0), 1.0)
    if form == "inverse_ratio":
        return 1.0 if v <= t else t / v
    if form == "excess":
        return 1.0 if v <= t else min(max(1.0 - (v - t) / (t - 1.0), 0.0), 1.0)
    raise ValueError(f"unknown score form {form!r}")


def score_array(form: str, values, thresholds) -> np.ndarray:
    v = np.asarray(values, dtype="float64")
    t = np.broadcast_to(np.asarray(thresholds, dtype="float64"), v.shape)
    return np.array([score(form, a, b) for a, b in zip(v, t)], dtype="float64")


def percentile_inverse(values) -> np.ndarray:
    """1 - percentile rank (ties share their average rank); NaN stays NaN."""
    v = pd.Series(np.asarray(values, dtype="float64"))
    return (1.0 - v.rank(pct=True, method="average")).to_numpy() if v.notna().any() else v.to_numpy()


# --- C-PRI-02/03 facilities -----------------------------------------------------------------------


def ist_facility(kind: str, imp_rule, cycleway_values, sidepath_oneway, p: PrincipleParams) -> str | None:
    """Ist facility of an edge (C-PRI-02); sidepath_oneway is None for edges that are no sidepath."""
    if kind == "path" and sidepath_oneway is not None:
        return p.sidepath_oneway if sidepath_oneway else p.sidepath_twoway
    cond = p.imp_condition.get(imp_rule)
    fac = p.by_condition.get(cond)
    if fac is None:
        return None
    if kind == "road" and fac == "mixed" and cycleway_values and set(cycleway_values) & LANE_VALUES:
        return p.lane_upgrade
    return fac


def _cell(cell) -> tuple[str | None, str | None]:
    if isinstance(cell, str):
        return cell, None
    if "all" in cell:
        return cell["all"], None
    return cell.get("preferred"), cell.get("fallback")


def soll_facility(cat_final, cycle_cat: str, p: PrincipleParams) -> tuple[str | None, str | None]:
    """(preferred, fallback) facility of the separation matrix for a road category and cycle category."""
    if not isinstance(cat_final, str):
        return None, None
    if cat_final in RURAL:
        return _cell(p.matrix["rural"][cat_final])
    row = p.matrix.get(cat_final)
    if row is None:
        return None, None
    if "all" in row:
        return _cell(row)
    return _cell(row[cycle_cat])


def edge_soll_facility(kind: str, cat_final, parent_cat, cycle_cat: str, p: PrincipleParams) -> tuple[str | None, str | None]:
    """Soll facility per edge: sidepaths after their road, other own paths own_path, roads after cat_final."""
    if kind == "path":
        if isinstance(parent_cat, str):
            return soll_facility(parent_cat, cycle_cat, p)
        return "own_path", None
    if kind == "road":
        return soll_facility(cat_final, cycle_cat, p)
    return None, None


def facility_score(ist, soll, fallback, p: PrincipleParams) -> float:
    """P-SAF-01 (C-PRI-03): 1 if Ist satisfies Soll, partial_score if partial or fallback, else 0."""
    if ist is None or soll is None:
        return float("nan")
    if ist in p.satisfies.get(soll, ()):
        return 1.0
    if ist in p.partial.get(soll, ()) or (fallback is not None and ist == fallback):
        return p.partial_score
    return 0.0


# --- C-PRI-06/08/09 width, surface, lit ------------------------------------------------------------


def parse_width(raw) -> float:
    """Metres from an OSM width value ("2", "2,5", "1.8 m", "2;3" -> smallest); NaN if not a positive number."""
    if not isinstance(raw, str) or not raw.strip():
        return float("nan")
    vals = []
    for part in raw.split(";"):
        m = _WIDTH.match(part)
        if m:
            vals.append(float(m.group(1).replace(",", ".")))
    vals = [v for v in vals if v > 0]
    return min(vals) if vals else float("nan")


def parse_upgrade(text: str) -> tuple[str, float]:
    m = _UPGRADE.match(str(text))
    if not m:
        raise ValueError(f"intensity_upgrade condition not understood: {text!r} (expected 'oneway|twoway peak_h > N')")
    return m.group(1), float(m.group(2))


def required_width(facility, cycle_cat: str, peak_dir, peak_both, p: PrincipleParams) -> float:
    """widths_m.project_target for the facility and cycle category plus intensity_upgrade; NaN if not applicable."""
    key = p.required_by_facility.get(facility)
    if key is None:
        return float("nan")
    t = p.project_target[key]
    if "value" in t:
        base = t["value"]
    elif cycle_cat in t:
        base = t[cycle_cat]
    else:
        return float("nan")
    base = float(base)
    oneway = facility in ONEWAY_FACILITIES
    for kind, thr, add in p.intensity_upgrade:
        peak = peak_dir if kind == "oneway" else peak_both
        if (kind == "oneway") == oneway and not _nan(peak) and float(peak) > thr:
            base += add
    return base


def lit_state(value, p: PrincipleParams) -> bool | None:
    if not isinstance(value, str):
        return None
    if value in p.lit_values:
        return True
    if value in p.unlit_values:
        return False
    return None


def surface_score(surface, cycle_cat: str, p: PrincipleParams) -> float:
    """P-COM-02 (C-PRI-09): RSV/HAUPT closed surface; BASIS/ERSCHL no unpaved or coarse surface."""
    if not isinstance(surface, str) or not surface:
        return float("nan")
    if cycle_cat in ("RSV", "HAUPT"):
        return 1.0 if surface in p.smooth_surfaces else 0.0
    return 0.0 if surface in p.unpaved_surfaces else 1.0


# --- C-PRI-04/05 directness ------------------------------------------------------------------------


def route_stops(nodes: list[int], edge_priority: list[bool], interior_signals: list[int],
                signal_nodes: set, priority_nodes: set) -> tuple[int, int]:
    """(signal stops, give-way stops) along a route (C-PRI-05); nodes has one more entry than the edges.

    Give way at a node without signal that touches a priority road, if one of the route edges there (at the
    route ends: the one edge) is no priority road, like the node delays of the cycle graph (C-GRAPH-05).
    """
    signals = int(sum(interior_signals)) + sum(1 for n in nodes if n in signal_nodes)
    give_way = 0
    for k, n in enumerate(nodes):
        if n in signal_nodes or n not in priority_nodes:
            continue
        at = [edge_priority[j] for j in (k - 1, k) if 0 <= j < len(edge_priority)]
        if at and not all(at):
            give_way += 1
    return signals, give_way


def time_loss_s(signals, give_way, p: PrincipleParams):
    return np.asarray(signals) * p.signal_delay_s + np.asarray(give_way) * p.give_way_delay_s


def length_graph(node_u, node_v, length) -> Graph:
    """Undirected graph over edges with their length as cost."""
    return Graph(node_u, node_v, length, np.arange(len(node_u)))


def shortest_lengths(g: Graph, sources, targets, limit: float = np.inf) -> np.ndarray:
    """Shortest path lengths (rows: sources, columns: targets); inf if unreachable or not in the graph."""
    si, ti = g.index(sources), g.index(targets)
    out = np.full((len(si), len(ti)), np.inf)
    ok = si >= 0
    if ok.any() and g.n:
        d = dijkstra(g.matrix, directed=True, indices=si[ok], limit=limit)
        d = np.atleast_2d(d)
        good_t = ti >= 0
        out[np.ix_(ok, good_t)] = d[:, ti[good_t]]
    return out


def od_sample(xy: np.ndarray, node_ids: np.ndarray, band_m: tuple[float, float], n: int, seed: int) -> list[tuple[int, int]]:
    """n random node pairs whose straight-line distance lies in band_m; reproducible for a seed."""
    rng = np.random.default_rng(seed)
    order = np.argsort(node_ids)
    xy, node_ids = np.asarray(xy)[order], np.asarray(node_ids)[order]
    tree = cKDTree(xy)
    pairs: list[tuple[int, int]] = []
    tries = 0
    while len(pairs) < n and tries < 50 * n:
        tries += 1
        a = int(rng.integers(len(xy)))
        cand = np.array(tree.query_ball_point(xy[a], band_m[1]), dtype="int64")
        if len(cand) == 0:
            continue
        d = np.hypot(*(xy[cand] - xy[a]).T)
        cand = np.sort(cand[d >= band_m[0]])
        if len(cand) == 0:
            continue
        b = int(cand[rng.integers(len(cand))])
        pairs.append((int(node_ids[a]), int(node_ids[b])))
    return pairs


# --- C-PRI-10 green ----------------------------------------------------------------------------------


def prepare_green(polys: np.ndarray, trees: np.ndarray, crown_radius_m: float) -> np.ndarray:
    """Non-overlapping green polygons: the land-use polygons plus tree crowns outside them."""
    polys = np.asarray(polys, dtype=object)
    trees = np.asarray(trees, dtype=object)
    parts = [shapely.make_valid(p) for p in polys] if len(polys) else []
    if len(trees):
        crowns = shapely.union_all(shapely.buffer(trees, crown_radius_m))
        if len(polys):
            tree_ = shapely.STRtree(polys)
            near = polys[np.unique(tree_.query(crowns, predicate="intersects"))]
            if len(near):
                crowns = shapely.difference(crowns, shapely.union_all(near))
        parts += list(shapely.get_parts(crowns))
    parts = [g for g in parts if not g.is_empty and g.area > 0]
    return np.array(parts, dtype=object)


def green_share(lines: np.ndarray, green: np.ndarray, buffer_m: float) -> np.ndarray:
    """Share of each line's buffer covered by green (green parts must not overlap each other)."""
    bufs = shapely.buffer(np.asarray(lines, dtype=object), buffer_m)
    area = np.zeros(len(bufs))
    if len(green) and len(bufs):
        bi, gi = shapely.STRtree(green).query(bufs, predicate="intersects")
        if len(bi):
            np.add.at(area, bi, shapely.area(shapely.intersection(bufs[bi], green[gi])))
    total = shapely.area(bufs)
    return np.divide(area, total, out=np.zeros_like(area), where=total > 0)


# --- aggregation, confidence, sensitivity --------------------------------------------------------------


def weighted_mean(values, weights) -> tuple[float, float]:
    """(mean over known values weighted by weights, share of the weight with a known value)."""
    v = np.asarray(values, dtype="float64")
    w = np.asarray(weights, dtype="float64")
    known = ~np.isnan(v)
    tot = w.sum()
    if not known.any() or tot <= 0:
        return float("nan"), 0.0
    return float((v[known] * w[known]).sum() / w[known].sum()), float(w[known].sum() / tot)


def principle_scores(check_scores: dict, p: PrincipleParams) -> dict:
    """Principle score = mean of its scored checks (C-PRI-01); NaN if no check has a score."""
    out = {}
    n = len(next(iter(check_scores.values())))
    for name in p.weights:
        cols = [np.asarray(check_scores[c], dtype="float64") for c in p.checks_of(name) if c in check_scores]
        if not cols:
            out[name] = np.full(n, np.nan)
            continue
        m = np.vstack(cols)
        cnt = (~np.isnan(m)).sum(axis=0)
        out[name] = np.divide(np.nansum(m, axis=0), cnt, out=np.full(n, np.nan), where=cnt > 0)
    return out


def total_score(principle: dict, weights: dict) -> np.ndarray:
    """Weighted principle scores, weights re-normalised over the principles with a score."""
    names = list(weights)
    m = np.vstack([np.asarray(principle[k], dtype="float64") for k in names])
    w = np.array([weights[k] for k in names])[:, None] * ~np.isnan(m)
    ws = w.sum(axis=0)
    return np.divide(np.nansum(m * w, axis=0), ws, out=np.full(m.shape[1], np.nan), where=ws > 0)


def confidence(known: dict, applicable: dict, p: PrincipleParams) -> np.ndarray:
    """C-PRI-13: sum of principle weight x mean data share of its applicable checks."""
    n = len(next(iter(known.values())))
    conf = np.zeros(n)
    for name, w in p.weights.items():
        cs = [c for c in p.checks_of(name) if c not in p.network_only]
        k = np.vstack([np.asarray(known[c], dtype="float64") for c in cs])
        a = np.vstack([np.asarray(applicable[c], dtype=bool) for c in cs])
        cnt = a.sum(axis=0)
        share = np.divide((k * a).sum(axis=0), cnt, out=np.ones(n), where=cnt > 0)
        conf += w * share
    return conf


def confidence_class(conf, p: PrincipleParams) -> np.ndarray:
    c = np.asarray(conf, dtype="float64")
    return np.where(c >= p.conf_high, "high", np.where(c >= p.conf_medium, "medium", "low")).astype(object)


def vary_weights(weights: dict, name: str, factor: float) -> dict:
    """weights[name] x factor; the others scaled so that the sum stays 1 (C-PRI-14)."""
    new = weights[name] * factor
    rest = 1.0 - weights[name]
    return {k: (new if k == name else v * (1.0 - new) / rest) for k, v in weights.items()}


def top_ids(values, ids, n: int) -> list:
    s = pd.Series(np.asarray(values, dtype="float64"), index=np.asarray(ids))
    return s.dropna().sort_values(ascending=False, kind="stable").head(n).index.tolist()


def top_overlap(base, variant, ids, n: int) -> int:
    return len(set(top_ids(base, ids, n)) & set(top_ids(variant, ids, n)))


def facility_changes(seq) -> int:
    """Number of changes of the facility along a route, ignoring unknown entries."""
    known = [s for s in seq if s is not None]
    return sum(1 for a, b in zip(known, known[1:]) if a != b)


def stratified_sample(df: pd.DataFrame, key: str, id_col: str, n: int, seed: int) -> pd.DataFrame:
    """n rows spread over the values of key in proportion to their counts, at least one each; reproducible."""
    if len(df) <= n:
        return df.sort_values([key, id_col])
    counts = df[key].value_counts().sort_index()
    quota = {k: 1 for k in counts.index}
    rest = n - len(quota)
    if rest > 0:
        share = (counts - 1) / (counts - 1).sum() * rest
        base = share.astype(int)
        for k in counts.index:
            quota[k] += int(base[k])
        order = (share - base).sort_values(ascending=False, kind="stable").index
        for k in order[: rest - int(base.sum())]:
            quota[k] += 1
    parts = []
    for i, (k, q) in enumerate(sorted(quota.items())):
        g = df[df[key] == k].sort_values(id_col)
        parts.append(g.sample(n=min(q, len(g)), random_state=seed + i))
    return pd.concat(parts).sort_values([key, id_col])
