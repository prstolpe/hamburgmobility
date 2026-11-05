"""Cycle graph (prompts/15, pipeline/lib/cycle_graph.py): way selection, one-way rules, Ist impedance
(C-IMP-01..08), node delays (C-GRAPH-04/05), ferries (C-GRAPH-03), merging and stable edge ids.

Parameters always come from config/cycling_rules.yaml; tests compare against those values.
"""

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import LineString

from pipeline.lib import cycle_graph as cg
from pipeline.lib.rules import load_cycling_rules

P = cg.GraphParams.from_rules(load_cycling_rules())
F = P.factors


# --- C-GRAPH-01 way selection ----------------------------------------------------------------


@pytest.mark.parametrize("highway, tags, in_segments, expected", [
    ("residential", {}, True, "road"),
    ("primary", {"bicycle": "no"}, True, None),
    ("motorway", {}, True, None),
    ("trunk", {"motorroad": "yes"}, True, None),
    ("trunk", {}, True, "road"),
    ("pedestrian", {}, True, None),                       # Fußgängerzone without permission
    ("pedestrian", {"bicycle": "yes"}, True, "road"),
    ("cycleway", {}, False, "path"),
    ("cycleway", {"bicycle": "no"}, False, None),
    ("footway", {}, False, None),
    ("footway", {"bicycle": "yes"}, False, "path"),
    ("path", {"bicycle": "designated"}, False, "path"),
    ("path", {}, False, None),
    ("service", {"bicycle": "yes"}, False, None),         # not in segments, not a path class
    ("residential", {"bicycle": "use_sidepath"}, True, "road"),
])
def test_way_kind(highway, tags, in_segments, expected):
    assert cg.way_kind(highway, tags, in_segments, P) == expected


# --- C-GRAPH-02 one-way ----------------------------------------------------------------------


@pytest.mark.parametrize("tags, expected", [
    ({}, (True, True)),
    ({"oneway": "yes"}, (True, False)),
    ({"oneway": "-1"}, (False, True)),
    ({"oneway": "yes", "oneway:bicycle": "no"}, (True, True)),
    ({"junction": "roundabout"}, (True, False)),
    ({"oneway": "no"}, (True, True)),
    ({"oneway": "yes", "oneway:bicycle": "yes"}, (True, False)),
])
def test_allowed_directions(tags, expected):
    assert cg.allowed_directions(tags) == expected


# --- C-IMP-01..08 Ist impedance --------------------------------------------------------------


def _imp(kind="road", highway="residential", tags=None, cat=None, speed=30, fstr=False):
    return cg.impedance(kind, highway, tags or {}, cat, speed, fstr, P)


def test_cycle_street_official_and_osm():
    assert _imp(fstr=True, cat="GOW30")[:2] == (F["separated_track_or_cycle_street"], "C-IMP-01")
    assert _imp(tags={"bicycle_road": "yes"}, speed=50, cat="GOW50")[1] == "C-IMP-01"


def test_own_path():
    assert _imp(kind="path", highway="cycleway", speed=None)[:2] == (F["separated_track_or_cycle_street"], "C-IMP-02")


def test_separated_track_but_not_separately_mapped():
    assert _imp(tags={"cycleway:right": "track"}, cat="GOW50", speed=50)[:2] == (F["gow50_separated_track"], "C-IMP-03")
    # cycleway=separate: the track is its own edge; the carriageway is mixed traffic
    assert _imp(tags={"cycleway:both": "separate"}, cat="GOW50", speed=50)[1] == "C-IMP-07"


def test_low_speed_access_road():
    assert _imp(cat="ETW30", speed=30)[:2] == (F["etw30_mixed"], "C-IMP-04")
    assert _imp(cat=None, highway="living_street", speed=10)[1] == "C-IMP-04"


def test_low_speed_main_road_with_and_without_lane():
    assert _imp(cat="GOW30", speed=30, tags={"cycleway": "lane"})[:2] == (F["gow30_cycle_lane"], "C-IMP-05")
    assert _imp(cat="GOW30", speed=30)[:2] == (F["gow30_cycle_lane"], "C-IMP-06")


def test_fast_roads_and_unknown_speed_fall_to_other():
    assert _imp(cat="GOW50", speed=50)[:2] == (F["gow50_cycle_lane_or_mixed"], "C-IMP-07")
    assert _imp(cat="ETW30", speed=None)[1] == "C-IMP-07"   # no speed known -> no low-speed rule


def test_unpaved_multiplies_and_is_traced():
    factor, rule, trace = _imp(kind="path", highway="path", tags={"surface": "sett"}, speed=None)
    assert factor == pytest.approx(F["separated_track_or_cycle_street"] * F["unpaved_or_cobbles"])
    assert rule == "C-IMP-02" and trace["rules"] == ["C-IMP-02", "C-IMP-08"]
    assert trace["inputs"]["surface"] == "sett"


# --- C-GRAPH-04/05 node delays -----------------------------------------------------------------


def test_node_delays_signal_and_give_way():
    m_per_s = P.cycling_speed_kmh / 3.6
    # node 2: signal; node 3: unsignalised, edge 2-3 is a priority road, 3-4 an access road
    u = np.array([1, 2, 3])
    v = np.array([2, 3, 4])
    priority = np.array([False, True, False])
    at_v, at_u = cg.node_delays(u, v, priority, signal_nodes={2}, params=P)
    assert at_v[0] == pytest.approx(P.signal_delay_s * m_per_s)       # 1 -> 2 into signal
    assert at_u[1] == pytest.approx(P.signal_delay_s * m_per_s)       # 3 -> 2 into signal
    assert at_u[2] == pytest.approx(P.give_way_delay_s * m_per_s)     # 4 -> 3 access road meets priority road
    assert at_v[1] == 0                                               # 2 -> 3 on the priority road itself
    assert at_v[2] == 0                                               # node 4 is a plain end


# --- merging, costs, ids ---------------------------------------------------------------------


def _edge_table(rows, coords):
    """rows: (u, v, way_id, kind, factor, fwd, bwd, segment_id)."""
    rec = []
    for u, v, w, kind, factor, fwd, bwd, sid in rows:
        rec.append({"u": u, "v": v, "way_id": w, "name": None, "highway": "residential", "kind": kind,
                    "factor": factor, "imp_rule": "C-IMP-04", "fwd_ok": fwd, "bwd_ok": bwd, "segment_id": sid,
                    "geometry": LineString([coords[u], coords[v]])})
    return gpd.GeoDataFrame(rec, geometry="geometry", crs="EPSG:25832")


COORDS = {1: (0, 0), 2: (100, 0), 3: (200, 0), 4: (200, 100)}


def test_merge_sums_costs_and_delays_per_direction():
    edges = _edge_table([(1, 2, 10, "road", 1.0, True, True, "seg_a"), (2, 3, 10, "road", 2.0, True, True, "seg_a")], COORDS)
    edges["delay_v"] = [0.0, 30.0]
    edges["delay_u"] = [5.0, 0.0]
    out = cg.merge_edges(edges)
    assert len(out) == 1
    r = out.iloc[0]
    fwd_from_1 = 100 * 1.0 + 100 * 2.0 + 30.0
    bwd_from_3 = 100 * 2.0 + 100 * 1.0 + 5.0
    if r["node_u"] == 1:
        assert (r["cost_fwd"], r["cost_bwd"]) == pytest.approx((fwd_from_1, bwd_from_3))
    else:
        assert (r["cost_fwd"], r["cost_bwd"]) == pytest.approx((bwd_from_3, fwd_from_1))
    assert r["edge_id"].startswith("ce_") and r["segment_id"] == "seg_a"


def test_merge_respects_oneway_against_digitisation():
    edges = _edge_table([(1, 2, 10, "road", 1.0, True, False, "seg_a"), (3, 2, 11, "road", 1.0, False, True, "seg_a")], COORDS)
    edges["delay_v"] = 0.0
    edges["delay_u"] = 0.0
    r = cg.merge_edges(edges).iloc[0]
    # allowed only 1 -> 2 -> 3
    allowed_dir = "cost_fwd" if r["node_u"] == 1 else "cost_bwd"
    blocked_dir = "cost_bwd" if r["node_u"] == 1 else "cost_fwd"
    assert np.isfinite(r[allowed_dir]) and np.isnan(r[blocked_dir])


def test_path_joining_mid_segment_splits_the_cycle_edge():
    edges = _edge_table([(1, 2, 10, "road", 1.0, True, True, "seg_a"), (2, 3, 10, "road", 1.0, True, True, "seg_a"),
                         (2, 4, 20, "path", 1.0, True, True, None)], {**COORDS, 4: (100, 100)})
    edges["delay_v"] = 0.0
    edges["delay_u"] = 0.0
    out = cg.merge_edges(edges)
    assert len(out) == 3
    assert (out["segment_id"] == "seg_a").sum() == 2


def test_edge_ids_stable_under_reversed_input():
    rows = [(1, 2, 10, "road", 1.0, True, True, "seg_a"), (2, 3, 10, "road", 1.0, True, True, "seg_a")]
    a = _edge_table(rows, COORDS)
    b = _edge_table([(v, u, w, k, f, bw, fw, s) for u, v, w, k, f, fw, bw, s in reversed(rows)], COORDS)
    for e in (a, b):
        e["delay_v"] = 0.0
        e["delay_u"] = 0.0
    assert cg.merge_edges(a)["edge_id"].tolist() == cg.merge_edges(b)["edge_id"].tolist()


# --- C-GRAPH-03 ferries ------------------------------------------------------------------------


def test_ferry_edge_snaps_ends_and_adds_wait():
    nodes = gpd.GeoDataFrame({"node": [1, 2]}, geometry=gpd.points_from_xy([0, 1000], [0, 0]), crs="EPSG:25832")
    ferries = gpd.GeoDataFrame({"way_id": [99], "bicycle": ["yes"]},
                               geometry=[LineString([(20, 5), (990, 0)])], crs="EPSG:25832")
    out = cg.ferry_edges(ferries, nodes, P)
    assert len(out) == 1
    r = out.iloc[0]
    assert {r["node_u"], r["node_v"]} == {1, 2}
    wait_m = P.ferry_wait_s * P.cycling_speed_kmh / 3.6
    snap_m = (20 ** 2 + 5 ** 2) ** 0.5 + 10  # pier to graph node at both ends, pushed on foot
    assert r["cost_fwd"] == pytest.approx(r["length_m"] + wait_m + snap_m)
    assert r["cost_bwd"] == pytest.approx(r["cost_fwd"])
    assert r["kind"] == "ferry" and r["edge_id"].startswith("ce_")


def test_ferry_too_far_or_without_bicycle_is_dropped():
    nodes = gpd.GeoDataFrame({"node": [1, 2]}, geometry=gpd.points_from_xy([0, 1000], [0, 0]), crs="EPSG:25832")
    far = LineString([(0, P.ferry_snap_m + 50), (1000, 0)])
    ferries = gpd.GeoDataFrame({"way_id": [1, 2], "bicycle": ["yes", "no"]},
                               geometry=[far, LineString([(0, 0), (1000, 0)])], crs="EPSG:25832")
    assert cg.ferry_edges(ferries, nodes, P).empty


# --- arcs ----------------------------------------------------------------------------------


def test_arcs_skip_blocked_directions():
    edges = gpd.GeoDataFrame({"edge_id": ["ce_a", "ce_b"], "node_u": [1, 2], "node_v": [2, 3],
                              "cost_fwd": [100.0, 50.0], "cost_bwd": [100.0, np.nan]},
                             geometry=[LineString([(0, 0), (1, 0)])] * 2, crs="EPSG:25832")
    arcs = cg.arcs(edges)
    assert len(arcs) == 3
    assert set(zip(arcs["tail"], arcs["head"])) == {(1, 2), (2, 1), (2, 3)}
