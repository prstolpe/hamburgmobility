"""Ist cycle facility per segment, computed once (rules.yaml S-FEAT-13, Review 2026-11 F26 / E9), and the parallel
cycle route of the Soll network (S-FEAT-11, F21).

S-FEAT-13 applies the rules of cycling_rules.yaml C-FAC-05 (pipeline/lib/facility.py ist_class / ist_facility):
OSM street tags (S-FEAT-10), official cycle streets, cycleway values of the street edges and the sidepaths of the
cycle graph per side. c04 (C-PRI-02), c05 (C-FAC-05) and s08 (D-DES-01, D-USE-01) read the result.

S-FEAT-11 counts a parallel route only on edges of the Soll cycle network in qualifying_cycle_categories, running in
the same direction within buffer_m, with a network path between the projections of the segment ends of at most the
P-DIR-01 detour factor times the segment length (per level as C-PRI-04 b). Every value comes from the rule files.
"""

import heapq
import json
import math
from dataclasses import dataclass

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from config.schema.cycling_model import CyclingRuleSet
from config.schema.rules_model import RuleSet
from pipeline.lib import facility as fa
from pipeline.lib.conflate import FLAT_CAP, MatchParams, candidate_pairs
from pipeline.lib.cycle_graph import TRACK_VALUES as GRAPH_TRACK_VALUES

TRACK_TAG_ONLY_FLAG = "track_tag_only"


def _missing(v) -> bool:
    return v is None or v is pd.NA or (isinstance(v, float) and math.isnan(v))


def _trace_inputs(trace) -> dict:
    try:
        return json.loads(trace)["inputs"]
    except (TypeError, ValueError, KeyError):
        return {}


# --- S-FEAT-13 inputs from the cycle graph -----------------------------------------------------------------


def segment_graph_inputs(seg_geom: gpd.GeoSeries, net: gpd.GeoDataFrame) -> pd.DataFrame:
    """Per segment_id (index of seg_geom): cycleway values and bicycle_road of its street edges, whether the cycle
    graph has a track on the carriageway (C-IMP-03 condition: cycleway track/opposite_track), and its sidepaths
    (present, open in both directions, on both sides)."""
    road = net[(net["kind"] == "road") & net["segment_id"].notna()].copy()
    side = net[(net["kind"] == "path") & net["sidepath_of"].notna() & net["sidepath_of"].isin(seg_geom.index)].copy()
    road_in = [_trace_inputs(t) for t in road["impedance_trace"]]
    road["cw"] = [set(i.get("cycleway") or []) for i in road_in]
    road["bicycle_road"] = [i.get("bicycle_road") == "yes" for i in road_in]
    side["twoway"] = side["cost_fwd"].notna() & side["cost_bwd"].notna()
    side["side"] = fa.sidepath_side(seg_geom.reindex(side["sidepath_of"]).values, side.geometry.values)
    out = pd.DataFrame(index=seg_geom.index)
    rg = road.groupby("segment_id")
    out["cycleway_values"] = rg["cw"].agg(lambda s: set().union(*s)).reindex(out.index)
    out["cycleway_values"] = out["cycleway_values"].map(lambda v: v if isinstance(v, set) else set())
    out["bicycle_road"] = rg["bicycle_road"].any().reindex(out.index).fillna(False).astype(bool)
    out["has_road_edge"] = out.index.isin(road["segment_id"])
    sg = side.groupby("sidepath_of")
    out["has_sidepath"] = out.index.isin(side["sidepath_of"])
    out["sidepath_twoway"] = sg["twoway"].any().reindex(out.index).fillna(False).astype(bool)
    out["sidepath_both_sides"] = sg["side"].agg(lambda x: {-1, 1} <= set(x)).reindex(out.index).fillna(False).astype(bool)
    out["graph_track"] = out["has_sidepath"] | out["cycleway_values"].map(lambda v: bool(v & GRAPH_TRACK_VALUES))
    return out


def _bool(v) -> bool:
    return False if _missing(v) else bool(v)


def ist_for_segment(p: fa.FacilityParams, track_facilities, *, fahrradstrasse=None, bicycle_road=False,
                    cycleway_values=(), has_sidepath=False, sidepath_twoway=False, sidepath_both_sides=False,
                    graph_track=False, cycle_track_tag=None, cycle_lane_present=None) -> dict:
    """S-FEAT-13 for one segment: Ist class and facility after C-FAC-05, separated_cycle_track_present (three-valued:
    unknown when class 'no' rests only on missing OSM data, S-FEAT-10) and the flag track_tag_only (track from the
    street tag, but neither sidepath nor carriageway track in the cycle graph)."""
    cw = set(cycleway_values or ())
    cls = fa.ist_class(p, fahrradstrasse=_bool(fahrradstrasse), bicycle_road=bool(bicycle_road), cycleway_values=cw,
                       has_sidepath=bool(has_sidepath), track_present=_bool(cycle_track_tag),
                       lane_present=_bool(cycle_lane_present))
    ist = fa.ist_facility(cls, bool(sidepath_twoway), p, bool(sidepath_both_sides))
    evidence = (_bool(fahrradstrasse) or bool(bicycle_road) or bool(cw) or bool(has_sidepath)
                or not _missing(cycle_track_tag) or not _missing(cycle_lane_present))
    track = True if ist in track_facilities else (False if evidence else None)
    tag_only = cls == "track" and not bool(graph_track)
    values = {"fahrradstrasse_official": _bool(fahrradstrasse), "bicycle_road": bool(bicycle_road), "cycleway": sorted(cw),
              "cycle_track_tag": None if _missing(cycle_track_tag) else bool(cycle_track_tag),
              "cycle_lane_present": None if _missing(cycle_lane_present) else bool(cycle_lane_present),
              "sidepath": bool(has_sidepath), "sidepath_twoway": bool(sidepath_twoway),
              "sidepath_both_sides": bool(sidepath_both_sides), "graph_track": bool(graph_track)}
    return {"cycle_osm_ist": cls, "cycle_facility_ist": ist, "separated_cycle_track_present": track,
            TRACK_TAG_ONLY_FLAG: tag_only,
            "trace": {"id": "S-FEAT-13", "result": ist, "values": {**values, "ist_class": cls,
                                                                   "separated_cycle_track_present": track}}}


def ist_frame(final: pd.DataFrame, graph: pd.DataFrame, p: fa.FacilityParams, track_facilities) -> pd.DataFrame:
    """S-FEAT-13 for every segment of final (index segment_id); graph from segment_graph_inputs."""
    rows = []
    g = graph.reindex(final.index)
    for seg, f, i in zip(final.index, final.to_dict("records"), g.to_dict("records")):
        r = ist_for_segment(p, track_facilities, fahrradstrasse=f.get("fahrradstrasse_official"),
                            bicycle_road=_bool(i.get("bicycle_road")),
                            cycleway_values=i.get("cycleway_values") if isinstance(i.get("cycleway_values"), set) else (),
                            has_sidepath=_bool(i.get("has_sidepath")), sidepath_twoway=_bool(i.get("sidepath_twoway")),
                            sidepath_both_sides=_bool(i.get("sidepath_both_sides")), graph_track=_bool(i.get("graph_track")),
                            cycle_track_tag=f.get("cycle_track_tag"), cycle_lane_present=f.get("cycle_lane_present"))
        rows.append({"segment_id": seg, **r})
    return pd.DataFrame(rows).set_index("segment_id")


# --- S-FEAT-11 parallel route of the Soll cycle network ----------------------------------------------------


@dataclass(frozen=True)
class ParallelParams:
    match: MatchParams                 # buffer_m of S-FEAT-11, angle of S-CONF-01
    min_share: float                   # S-CONF-02 min_length_share
    levels: tuple                      # ((categories, detour_max, label), ...) from the highest level down (C-PRI-04 b)
    categories: frozenset              # requirements.*.cycling == applies_to_requirement -> assessed

    @classmethod
    def from_rules(cls, rules: RuleSet, cyc: CyclingRuleSet) -> "ParallelParams":
        f11 = rules.features.rule("S-FEAT-11")
        s01 = rules.conflation.rule("S-CONF-01").thresholds
        match = MatchParams(buffer_m=f11.thresholds["buffer_m"].value, max_angle_deg=s01["max_angle_deg"].value,
                            min_overlap_share=s01["min_overlap_share"].value)
        check = next(c for c in _principle_checks(cyc) if c.get("id") == f11.detour_check)
        detour = {k: float(v) for k, v in check["thresholds"].items()}
        quals = list(f11.qualifying_cycle_categories)
        missing = [c for c in quals if c not in detour]
        if missing:
            raise ValueError(f"S-FEAT-11: {f11.detour_check} has no threshold for {missing}")
        levels = tuple((frozenset(quals[:k + 1]), detour[quals[k]], quals[k]) for k in range(len(quals)))
        cats = frozenset(c for c, req in rules.requirements.items()
                         if isinstance(req, dict) and _req_value(req.get("cycling")) == f11.applies_to_requirement)
        return cls(match, float(rules.conflation.rule("S-CONF-02").thresholds["min_length_share"].value), levels, cats)


def _req_value(entry):
    return entry.get("value") if isinstance(entry, dict) else entry


def _principle_checks(cyc: CyclingRuleSet) -> list[dict]:
    return [c for p in cyc.principles.values() for c in p["checks"]]


def _dijkstra(adj: dict, start, target, limit: float) -> float:
    dist = {start: 0.0}
    heap = [(0.0, start)]
    while heap:
        d, n = heapq.heappop(heap)
        if n == target:
            return d
        if d > dist.get(n, math.inf) or d > limit:
            continue
        for m, w in adj.get(n, ()):
            nd = d + w
            if nd < dist.get(m, math.inf) and nd <= limit:
                dist[m] = nd
                heapq.heappush(heap, (nd, m))
    return math.inf


def network_detour(seg_line, edges: pd.DataFrame, paired: list, limit_factor: float) -> float | None:
    """Network path on edges (columns node_u, node_v, length_m, geometry oriented u -> v) between the projections
    of the segment's end points onto the nearest paired edge, divided by the segment length. None without a path
    of at most limit_factor x length."""
    length = seg_line.length
    if length == 0 or not paired:
        return None
    ends = [shapely.Point(seg_line.coords[0]), shapely.Point(seg_line.coords[-1])]
    proj = []
    for pt in ends:
        e = min(paired, key=lambda k: edges.at[k, "geometry"].distance(pt))
        geom = edges.at[e, "geometry"]
        t = geom.project(pt) / geom.length * edges.at[e, "length_m"] if geom.length else 0.0
        proj.append((e, t))
    (ea, ta), (eb, tb) = proj
    limit = limit_factor * length
    if ea == eb:
        d = abs(ta - tb)
        return d / length if d <= limit else None
    adj: dict = {}

    def add(a, b, w):
        adj.setdefault(a, []).append((b, w))
        adj.setdefault(b, []).append((a, w))

    for k, u, v, w in zip(edges.index, edges["node_u"], edges["node_v"], edges["length_m"]):
        if k in (ea, eb):
            continue
        add(u, v, float(w))
    for name, (e, t) in (("A", (ea, ta)), ("B", (eb, tb))):
        w = float(edges.at[e, "length_m"])
        add(name, edges.at[e, "node_u"], t)
        add(name, edges.at[e, "node_v"], max(w - t, 0.0))
    d = _dijkstra(adj, "A", "B", limit)
    return d / length if math.isfinite(d) else None


def parallel_routes(segs: gpd.GeoDataFrame, net: gpd.GeoDataFrame, seg_names: pd.Series, pp: ParallelParams) -> pd.DataFrame:
    """S-FEAT-11 per segment of segs (index segment_id, geometry): parallel_cycle_route_present (bool), the share
    in the buffer, the passing level and its detour factor. Edges of the segment and of segments with the same
    street name (street edge or sidepath) never count."""
    quals = frozenset().union(*(lv[0] for lv in pp.levels))
    q = net[net["cycle_cat_final"].isin(quals)].copy()
    owner = q["segment_id"].where(q["kind"] == "road").fillna(q["sidepath_of"])
    q["owner_name"] = owner.map(seg_names)
    q["owner"] = owner
    q = q.reset_index(drop=True)
    out = pd.DataFrame({"parallel_cycle_route_present": False, "parallel_share": 0.0, "parallel_level": None,
                        "parallel_detour": np.nan}, index=segs.index)
    out["parallel_level"] = out["parallel_level"].astype(object)
    if segs.empty or q.empty:
        return out
    pairs = candidate_pairs(segs.geometry, q.geometry, pp.match, angle_only=True)
    pairs = pairs[pairs["passed"]]
    if pairs.empty:
        return out
    seg_name = segs.index.to_series().map(seg_names)
    same = ((q["owner"].to_numpy()[pairs["off_idx"].to_numpy()] == pairs["seg_idx"].to_numpy())
            | (q["owner_name"].to_numpy()[pairs["off_idx"].to_numpy()] == seg_name.reindex(pairs["seg_idx"]).to_numpy()))
    pairs = pairs[~same]
    tree = shapely.STRtree(q.geometry.values)
    max_factor = max(lv[1] for lv in pp.levels)
    for seg_id, grp in pairs.groupby("seg_idx"):
        line = segs.at[seg_id, "geometry"]
        union = shapely.union_all(q.geometry.iloc[grp["off_idx"]].buffer(pp.match.buffer_m, cap_style=FLAT_CAP).values)
        share = line.intersection(union).length / line.length if line.length else 0.0
        out.at[seg_id, "parallel_share"] = share
        if share < pp.min_share:
            continue
        local_idx = tree.query(line.buffer(pp.match.buffer_m + max_factor * line.length))
        local = q.iloc[local_idx]
        local = local[(local["owner"] != seg_id) & ((local["owner_name"] != seg_name.get(seg_id)) | local["owner_name"].isna())]
        paired_all = set(grp["off_idx"])
        for cats, factor, label in pp.levels:
            lv = local[local["cycle_cat_final"].isin(cats)]
            paired = [k for k in lv.index if k in paired_all]
            det = network_detour(line, lv, paired, factor)
            if det is not None:
                out.at[seg_id, "parallel_cycle_route_present"] = True
                out.at[seg_id, "parallel_level"] = label  # network down to this category
                out.at[seg_id, "parallel_detour"] = det
                break
    return out
