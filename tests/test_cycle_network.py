"""Cycle network design (prompts/16, pipeline/lib/cycle_network.py): Soll resistance, bonuses, corridors,
RSV runs, meshes, densification, parallel rule P-ATT-03, continuity, cycle network overrides.

Small synthetic grids; all parameters come from config/cycling_rules.yaml.
"""

import json

import numpy as np
import pandas as pd
import pytest
import shapely
from shapely.geometry import LineString, Polygon, box

from pipeline.lib import cycle_network as cn
from pipeline.lib import overrides as ov
from pipeline.lib.rules import load_cycling_rules

CYC = load_cycling_rules()
P = cn.NetworkParams.from_rules(CYC)
F = CYC.routing_impedance["factors"]


# --- synthetic grid ------------------------------------------------------------------------------


def grid(n: int, step: float) -> pd.DataFrame:
    """Square grid of n x n nodes, spacing step (m); node id = row * 1000 + col."""
    rows = []
    for r in range(n):
        for c in range(n):
            if c + 1 < n:
                rows.append((r * 1000 + c, r * 1000 + c + 1, LineString([(c * step, r * step), ((c + 1) * step, r * step)])))
            if r + 1 < n:
                rows.append((r * 1000 + c, (r + 1) * 1000 + c, LineString([(c * step, r * step), (c * step, (r + 1) * step)])))
    df = pd.DataFrame(rows, columns=["node_u", "node_v", "geometry"])
    df["length_m"] = shapely.length(df["geometry"].to_numpy())
    df["cost"] = df["length_m"]
    df["demand"] = 0.0
    return df


def inputs(df: pd.DataFrame) -> cn.DesignInputs:
    return cn.DesignInputs.build(df["geometry"].to_numpy(), df["node_u"].to_numpy(), df["node_v"].to_numpy(),
                                 df["cost"].to_numpy(dtype=float), df["length_m"].to_numpy(dtype=float),
                                 df["demand"].to_numpy(dtype=float), np.ones(len(df), dtype=bool))


def ring_mask(df: pd.DataFrame, n: int) -> np.ndarray:
    """Edges on the outer ring of an n x n grid."""
    u, v = df["node_u"].to_numpy(), df["node_v"].to_numpy()
    ur, uc, vr, vc = u // 1000, u % 1000, v // 1000, v % 1000
    return ((ur == vr) & ((ur == 0) | (ur == n - 1))) | ((uc == vc) & ((uc == 0) | (uc == n - 1)))


# --- parameters -----------------------------------------------------------------------------------


def test_params_take_thresholds_from_rule_files():
    cats = CYC.cycle_categories
    assert P.rsv_trigger == cats["RSV"]["demand_trigger_cyclists_weekday"]["value"]
    assert P.rsv_min_length_m == cats["RSV"]["min_route_length_km"]["value"] * 1000
    assert P.mesh_max_m == {"HAUPT": cats["HAUPT"]["mesh_m"]["range"][1], "BASIS": cats["BASIS"]["mesh_m"]["range"][1]}
    checks = {c["id"]: c for p in CYC.principles.values() for c in p["checks"]}
    assert P.patt_dtv == checks["P-ATT-03"]["dtv"]
    assert P.patt_parallel_max_m == checks["P-ATT-03"]["parallel_max_m"]
    assert P.detour_max == checks["P-DIR-01"]["thresholds"]
    assert P.coverage_m == checks["P-COH-03"]["coverage_m"]


# --- C-NET-03..05 Soll resistance and bonuses ----------------------------------------------------


@pytest.mark.parametrize("kind, cat, ist, key", [
    ("path", None, 1.3, "separated_track_or_cycle_street"),
    ("road", "GOW50", 2.0, "gow50_separated_track"),
    ("road", "GOW30", 1.25, "gow30_cycle_lane"),
    ("road", "ETW30", 1.05, "etw30_mixed"),
    ("road", None, 2.0, None),       # no cat_final: Ist factor
    ("ferry", None, 1.0, None),
])
def test_soll_factor(kind, cat, ist, key):
    factor, used = cn.soll_factor_for(kind, cat, ist, P)
    if key is None:
        assert (factor, used) == (ist, "ist")
    else:
        assert (factor, used) == (F[key], key)


def test_soll_costs_keep_node_delays():
    length = np.array([100.0, 100.0])
    ist = np.array([2.0, 2.0])
    fwd = np.array([200.0 + 50.0, np.nan])     # 50 m delay forward, one-way
    bwd = np.array([200.0, 200.0])
    f, b = cn.soll_costs(length, ist, fwd, bwd, np.array([1.1, 1.1]))
    assert f[0] == pytest.approx(110.0 + 50.0)
    assert np.isnan(f[1])
    assert b == pytest.approx([110.0, 110.0])


def test_demand_multiplier():
    m = cn.demand_multiplier(np.array([0.0, P.rsv_trigger / 2, P.rsv_trigger * 3, np.nan]), P)
    assert m == pytest.approx([1.0, 1 - P.max_reduction / 2, 1 - P.max_reduction, 1.0])


def test_overlap_share():
    lines = np.array([LineString([(0, 0), (100, 0)]), LineString([(0, 50), (100, 50)])])
    zone = np.array([box(-5, -5, 50, 5)])
    assert cn.overlap_share(lines, zone) == pytest.approx([0.5, 0.0])
    overlapping = np.array([box(-5, -5, 50, 5), box(30, -5, 80, 5)])     # overlap counts once
    assert cn.overlap_share(lines, overlapping) == pytest.approx([0.8, 0.0])


def test_graph_prefers_cheaper_edge():
    df = pd.DataFrame({"node_u": [1, 1, 3], "node_v": [2, 3, 2], "cost": [100.0, 30.0, 30.0]})
    g = cn.Graph(df["node_u"].to_numpy(), df["node_v"].to_numpy(), df["cost"].to_numpy(), np.arange(3))
    s, t = g.index(np.array([1, 2]))
    _, pred = g.dijkstra([s])
    assert g.path(pred[0], s, t) == [1, 2]
    assert g.index(np.array([99]))[0] == -1


# --- C-NET-01/02 corridor points and pairs -------------------------------------------------------


def test_merge_points_keeps_first_in_priority_order():
    xy = np.array([[0, 0], [100, 0], [1000, 0], [1200, 0]], dtype=float)
    assert cn.merge_points(xy, 500).tolist() == [True, False, True, False]


def test_hubs_group_nearby_stations():
    xy = np.array([[0, 0], [P.hub_radius_m - 10, 0], [5000, 0]], dtype=float)
    types = [{402}, {109}, {109}]          # U and S as separate stations close together
    assert cn.hubs(xy, types, P.hub_radius_m, P.hub_min_modes).tolist() == [True, True, False]


def test_corridor_pairs_nearest_and_centre():
    xy = np.array([[0, 0], [1000, 0], [2000, 0], [50000, 0]], dtype=float)
    pairs = cn.corridor_pairs(xy, centre=0, k=1, max_m=15000)
    assert (1, 2) in pairs and (0, 1) in pairs
    assert (0, 3) in pairs            # every point with the Innenstadt, regardless of distance
    assert (2, 3) not in pairs        # nearest neighbour farther than max_m


# --- C-NET-06 RSV runs ------------------------------------------------------------------------------


def test_rsv_runs_bridge_short_gaps():
    t, gap, mn = P.rsv_trigger, P.rsv_gap_max_m, P.rsv_min_length_m
    lengths = np.array([mn / 2, gap / 2, mn / 2, gap * 2, mn / 2])
    demand = np.array([t, 0, t, 0, t])
    assert cn.rsv_mask(lengths, demand, P).tolist() == [True, True, True, False, False]


def test_rsv_runs_need_min_length():
    lengths = np.array([P.rsv_min_length_m / 3] * 2)
    assert not cn.rsv_mask(lengths, np.array([P.rsv_trigger] * 2), P).any()


# --- C-NET-07 meshes ---------------------------------------------------------------------------------


def inside(faces: np.ndarray, area: Polygon) -> np.ndarray:
    return faces[shapely.within(shapely.point_on_surface(faces), area)]


def test_mesh_side_of_square_and_barrier_split():
    boundary = box(-10, -10, 1010, 1010)
    square = np.array([LineString([(0, 0), (1000, 0), (1000, 1000), (0, 1000), (0, 0)])])
    faces = cn.mesh_faces(square, np.array([]), boundary)
    assert len(faces) == 2                 # the mesh and the strip up to the boundary
    assert cn.mesh_side(inside(faces, box(0, 0, 1000, 1000))) == pytest.approx([1000.0])
    barrier = np.array([LineString([(500, -10), (500, 1010)])])
    faces = cn.mesh_faces(square, barrier, boundary)
    sides = np.sort(cn.mesh_side(inside(faces, box(0, 0, 1000, 1000))))
    assert sides == pytest.approx([np.sqrt(500 * 1000)] * 2)


def test_mesh_side_without_excluded_area():
    face = np.array([box(0, 0, 1000, 1000)])
    park = np.array([box(0, 0, 1000, 500)])
    assert cn.mesh_side(face, park) == pytest.approx([np.sqrt(500 * 1000)])


# --- C-NET-08 densification ----------------------------------------------------------------------------


def test_split_face_connects_two_boundary_nodes_through_seed():
    df = grid(5, 200)
    inner = ~ring_mask(df, 5)
    sub_idx = np.flatnonzero(inner)
    g = cn.Graph(df["node_u"].to_numpy()[sub_idx], df["node_v"].to_numpy()[sub_idx], df["cost"].to_numpy()[sub_idx], sub_idx)
    ring_nodes = np.unique(np.concatenate([df.loc[~inner, "node_u"], df.loc[~inner, "node_v"]]))
    seed = int(df.index[(df["node_u"] == 2001) & (df["node_v"] == 2002)][0])
    route = cn.split_face(g, seed, 2001, 2002, ring_nodes)
    assert route is not None and seed in route
    nodes = cn.route_nodes(route, df["node_u"].to_numpy(), df["node_v"].to_numpy())
    assert nodes[0] in ring_nodes and nodes[-1] in ring_nodes and nodes[0] != nodes[-1]


def test_split_face_halves_are_disjoint():
    """From the far seed end, the nearest ring node is reached back through the near end; the second half must
    still leave by its own way so that the route crosses the face."""
    #   ring nodes 1 (0,0) and 2 (10,0); seed 3-4 hangs off node 3 near the ring; 4 also has a long way to ring node 5.
    rows = [(1, 3, [(0, 0), (0, 10)]), (3, 2, [(0, 10), (10, 0)]), (3, 4, [(0, 10), (0, 300)]),
            (4, 5, [(0, 300), (0, 1000)])]
    df = pd.DataFrame([(u, v, LineString(c)) for u, v, c in rows], columns=["node_u", "node_v", "geometry"])
    df["cost"] = shapely.length(df["geometry"].to_numpy())
    g = cn.Graph(df["node_u"], df["node_v"], df["cost"], np.arange(len(df)))
    route = cn.split_face(g, 2, 3, 4, np.array([1, 2, 5]))
    nodes = cn.route_nodes(route, df["node_u"].to_numpy(), df["node_v"].to_numpy())
    assert cn.chain_ok(route, df["node_u"].to_numpy(), df["node_v"].to_numpy(), nodes).all()
    assert {nodes[0], nodes[-1]} in ({1, 5}, {2, 5})


def test_split_face_falls_back_to_disjoint_paths():
    """Cheapest way from seed end 3 to the ring runs through node 5, the only other exit of seed end 4; the split
    must leave 3 by the longer way. Checks the greedy search and the disjoint-path fallback."""
    rows = [(3, 5, [(0, 10), (5, 10)]), (5, 1, [(5, 10), (5, 0)]), (4, 5, [(0, 20), (5, 10)]),
            (3, 6, [(0, 10), (-100, 10)]), (6, 2, [(-100, 10), (-100, 0)]), (3, 4, [(0, 10), (0, 20)])]
    df = pd.DataFrame([(u, v, LineString(c)) for u, v, c in rows], columns=["node_u", "node_v", "geometry"])
    df["cost"] = shapely.length(df["geometry"].to_numpy())
    g = cn.Graph(df["node_u"], df["node_v"], df["cost"], np.arange(len(df)))
    for route in (cn.split_face(g, 5, 3, 4, np.array([1, 2])), cn._disjoint_split(g, 5, 3, 4, np.array([1, 2]))):
        assert route is not None and 5 in route
        nodes = cn.route_nodes(route, df["node_u"].to_numpy(), df["node_v"].to_numpy())
        assert cn.chain_ok(route, df["node_u"].to_numpy(), df["node_v"].to_numpy(), nodes).all()
        assert {nodes[0], nodes[-1]} == {1, 2}


def test_densify_closes_oversized_meshes():
    df = grid(9, 150)                      # 1.2 km square, interior streets every 150 m
    seed = int(df.index[(df["node_u"] == 4004) & (df["node_v"] == 4005)][0])
    df.loc[seed, "demand"] = 500.0
    inp = inputs(df)
    boundary = box(-50, -50, 1250, 1250)
    res = cn.densify(inp, ring_mask(df, 9), 600, np.array([]), boundary, None, None, P)
    faces = cn.mesh_faces(inp.geom[res.net_mask], np.array([]), boundary)
    assert cn.mesh_side(inside(faces, box(0, 0, 1200, 1200))).max() <= 600
    assert res.routes and not res.gaps
    assert seed in res.routes[0]           # first split starts at the high-demand edge


def test_densify_ignores_dangling_network_edges():
    """A dead-end network branch inside the mesh is no valid end point: joining it would not split the mesh."""
    df = grid(9, 150)
    net = ring_mask(df, 9)
    dangle = ((df["node_u"] // 1000 == 4) & (df["node_v"] // 1000 == 4) & (df["node_u"] % 1000 >= 2)
              & (df["node_v"] % 1000 <= 6)).to_numpy()
    net |= dangle
    inp = inputs(df)
    boundary = box(-50, -50, 1250, 1250)
    res = cn.densify(inp, net, 600, np.array([]), boundary, None, None, P)
    faces = cn.mesh_faces(inp.geom[res.net_mask], np.array([]), boundary)
    assert cn.mesh_side(inside(faces, box(0, 0, 1200, 1200))).max() <= 600


def test_densify_skips_isolated_paths_in_mesh():
    """High-demand paths in the mesh centre that are not connected to the street grid (e.g. inside a park)
    must not block the split."""
    df = grid(9, 150)
    park = pd.DataFrame({"node_u": [9001, 9002, 9003], "node_v": [9002, 9003, 9004],
                         "geometry": [LineString([(560, 560), (640, 560)]), LineString([(640, 560), (640, 640)]),
                                      LineString([(640, 640), (560, 640)])]})
    park["length_m"] = shapely.length(park["geometry"].to_numpy())
    park["cost"], park["demand"] = park["length_m"], 5000.0
    df = pd.concat([df, park], ignore_index=True)
    net = np.r_[ring_mask(df.iloc[:-3], 9), [False] * 3]
    inp = inputs(df)
    boundary = box(-50, -50, 1250, 1250)
    res = cn.densify(inp, net, 600, np.array([]), boundary, None, None, P)
    faces = cn.mesh_faces(inp.geom[res.net_mask], np.array([]), boundary)
    assert cn.mesh_side(inside(faces, box(0, 0, 1200, 1200))).max() <= 600
    assert not res.gaps


def test_ring_connected_excludes_dead_ends_and_hanging_loops():
    df = grid(3, 100)
    extra = pd.DataFrame({"node_u": [1001, 7001, 7002, 7003], "node_v": [7001, 7002, 7003, 7001],
                          "geometry": [LineString([(100, 100), (150, 150)]), LineString([(150, 150), (170, 150)]),
                                       LineString([(170, 150), (160, 170)]), LineString([(160, 170), (150, 150)])]})
    df = pd.concat([df, extra], ignore_index=True)                       # spur to a loop hanging off node 7001
    df["length_m"] = shapely.length(df["geometry"].to_numpy())
    df["cost"], df["demand"] = df["length_m"], 0.0
    inp = inputs(df)
    allpos = np.arange(len(df))
    ring_nodes = np.array([0, 1, 2, 1000, 1002, 2000, 2001, 2002])
    mask = cn.ring_connected(inp, allpos, allpos, ring_nodes)
    assert mask.tolist() == [True] * (len(df) - 4) + [False] * 4


def test_route_chain_breaks():
    u, v = np.array([1, 2, 7, 3]), np.array([2, 3, 8, 4])
    nodes = cn.route_nodes([0, 1, 2, 3], u, v)
    assert cn.chain_ok([0, 1, 2, 3], u, v, nodes).tolist() == [True, True, False, False]


def test_seed_prefers_core_of_mesh():
    """Highest demand at the mesh edge, slightly lower in the centre: the centre edge starts the split."""
    df = grid(9, 150)
    edge_seed = int(df.index[(df["node_u"] == 1001) & (df["node_v"] == 1002)][0])
    core_seed = int(df.index[(df["node_u"] == 4004) & (df["node_v"] == 4005)][0])
    df.loc[edge_seed, "demand"], df.loc[core_seed, "demand"] = 900.0, 500.0
    res = cn.densify(inputs(df), ring_mask(df, 9), 600, np.array([]), box(-50, -50, 1250, 1250), None, None, P)
    assert core_seed in res.routes[0]


def test_densify_reports_face_without_candidates():
    df = grid(2, 1000)                     # one 1 km mesh, nothing inside
    inp = inputs(df)
    res = cn.densify(inp, np.ones(len(df), dtype=bool), 600, np.array([]), box(-50, -50, 1050, 1050), None, None, P)
    assert len(res.gaps) == 1 and res.gaps[0]["reason"] == cn.GAP_NO_CANDIDATES


# --- C-NET-09 binding ---------------------------------------------------------------------------------


def test_attach_points_routes_far_points_to_network():
    df = grid(6, 100)
    inp = inputs(df)
    g = cn.Graph(inp.node_u, inp.node_v, inp.cost, np.arange(len(df)))
    net = (df["node_u"] // 1000 == 0) & (df["node_v"] // 1000 == 0)        # bottom row
    pts = np.array([[300.0, 500.0], [200.0, 20.0]])                         # far / near
    routes = cn.attach_points(g, inp, net.to_numpy(), pts, P.binding_radius_m)
    assert len(routes) == 1
    assert inp.length[routes[0]].sum() == pytest.approx(500.0)


# --- C-NET-10 parallel rule P-ATT-03 ----------------------------------------------------------------------


def parallel_streets(offset: float, side_detour: float = 0.0) -> tuple[pd.DataFrame, list[int]]:
    """Main street y=0 from x=0..1000 in 4 edges, parallel street at y=offset joined at both ends.
    side_detour adds a bend to the parallel street (longer alternative)."""
    rows = [(i, i + 1, LineString([(i * 250, 0), ((i + 1) * 250, 0)])) for i in range(4)]
    mid = LineString([(0, offset), (500, offset + side_detour), (1000, offset)])
    rows += [(0, 10, LineString([(0, 0), (0, offset)])), (10, 11, mid), (11, 4, LineString([(1000, offset), (1000, 0)]))]
    df = pd.DataFrame(rows, columns=["node_u", "node_v", "geometry"])
    df["length_m"] = shapely.length(df["geometry"].to_numpy())
    df["cost"] = df["length_m"]
    df["demand"] = 0.0
    return df, [0, 1, 2, 3]


def test_parallel_alternative_found():
    df, run = parallel_streets(80)
    high = np.zeros(len(df), dtype=bool)
    high[run] = True
    alt = cn.parallel_alternative(inputs(df), run, 0, 4, high, P.patt_parallel_max_m, P.detour_max["HAUPT"], P.patt_max_on_main_m)
    assert alt.accepted and set(alt.edges) == {4, 5, 6} and alt.on_main_m == 0
    assert alt.detour == pytest.approx((1000 + 160) / 1000)


def test_parallel_alternative_may_cross_main_street_briefly():
    """Run on a cycle track; the side street joins the main road 20 m (or 100 m) from the track's start node."""
    def case(link_m: float):
        df, run = parallel_streets(80)
        df.loc[4, "geometry"] = LineString([(0, -link_m), (0, 80)])     # side street now starts at node 20
        df.loc[4, "node_u"] = 20
        link = pd.DataFrame({"node_u": [0], "node_v": [20], "geometry": [LineString([(0, 0), (0, -link_m)])]})
        df = pd.concat([df, link], ignore_index=True)
        df["length_m"] = shapely.length(df["geometry"].to_numpy())
        df["cost"], df["demand"] = df["length_m"], 0.0
        high = np.zeros(len(df), dtype=bool)
        high[run + [len(df) - 1]] = True                                 # the link is part of the main street
        return cn.parallel_alternative(inputs(df), run, 0, 4, high, P.patt_parallel_max_m, 2.0, P.patt_max_on_main_m)
    short = case(20)
    assert short.accepted and short.on_main_m == pytest.approx(20)
    assert not case(P.patt_max_on_main_m + 40).accepted


def test_parallel_alternative_too_far_or_too_long():
    df, run = parallel_streets(P.patt_parallel_max_m + 50)
    high = np.zeros(len(df), dtype=bool)
    high[run] = True
    assert not cn.parallel_alternative(inputs(df), run, 0, 4, high, P.patt_parallel_max_m, P.detour_max["HAUPT"],
                                       P.patt_max_on_main_m).accepted
    df, run = parallel_streets(80, side_detour=100)
    alt = cn.parallel_alternative(inputs(df), run, 0, 4, high, P.patt_parallel_max_m, P.detour_max["RSV"], P.patt_max_on_main_m)
    assert not alt.accepted and alt.detour > P.detour_max["RSV"]


def test_high_volume_runs_need_min_length():
    lengths = np.array([100.0, P.patt_min_run_m, 100.0, 50.0, 100.0])
    high = np.array([False, True, False, True, False])
    assert cn.high_volume_runs(high, lengths, P.patt_min_run_m) == [(1, 2)]


# --- C-NET-11 continuity --------------------------------------------------------------------------------


def test_smooth_raises_short_gap_between_equal_categories():
    H, B = cn.RANK["HAUPT"], cn.RANK["BASIS"]
    ranks, changes = cn.smooth_sequence(np.array([H, B, H]), np.array([500.0, P.continuity_max_gap_m, 500.0]),
                                        np.zeros(3, dtype=bool), P.continuity_max_gap_m)
    assert ranks.tolist() == [H, H, H] and changes == 0


def test_smooth_keeps_locked_and_long_gaps():
    H, B, R = cn.RANK["HAUPT"], cn.RANK["BASIS"], cn.RANK["RSV"]
    locked = np.array([False, True, False])
    ranks, changes = cn.smooth_sequence(np.array([H, B, H]), np.array([500.0, 10.0, 500.0]), locked, P.continuity_max_gap_m)
    assert ranks.tolist() == [H, B, H] and changes == 2
    ranks, changes = cn.smooth_sequence(np.array([R, H, R]), np.array([500.0, P.continuity_max_gap_m + 1, 500.0]),
                                        np.zeros(3, dtype=bool), P.continuity_max_gap_m)
    assert ranks.tolist() == [R, H, R] and changes == 2


def test_route_id_is_stable():
    a = cn.route_id("corridor", ["ce_b", "ce_a"])
    assert a == cn.route_id("corridor", ["ce_a", "ce_b"]) and a.startswith("rt_")
    assert a != cn.route_id("mesh_haupt", ["ce_a", "ce_b"])


def test_trace_is_json_with_rule_ids():
    t = cn.trace_json([{"rule": "C-NET-06", "result": "RSV", "values": {"cyc": 2500.0}}])
    assert json.loads(t)[0]["rule"] == "C-NET-06"


# --- overrides (cycle network) -------------------------------------------------------------------------------


def _ovr(rows) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=ov.CYCLE_NETWORK_COLUMNS)


def test_cycle_overrides_only_approved():
    edges = pd.DataFrame({"edge_id": ["ce_1", "ce_2"], "cycle_cat_proposed": ["HAUPT", "ERSCHL"]})
    df = _ovr([["ce_1", "BASIS", "Ortskenntnis", "a", "2026-11-06", "", "approved"],
               ["ce_2", "RSV", "Idee", "a", "2026-11-06", "", "draft"]])
    ov.validate_cycle_network(df, edges["edge_id"])
    out = ov.apply_cycle_network(edges, df)
    assert out["cycle_cat_final"].tolist() == ["BASIS", "ERSCHL"]
    assert out["cycle_cat_source"].tolist() == ["override", "proposed"]
    assert out.loc[0, "cycle_override_reason"] == "Ortskenntnis"


@pytest.mark.parametrize("row, msg", [
    (["ce_9", "BASIS", "x", "a", "2026-11-06", "", "approved"], "verwaist"),
    (["ce_1", "GOW50", "x", "a", "2026-11-06", "", "approved"], "Kategorie"),
    (["ce_1", "BASIS", "", "a", "2026-11-06", "", "approved"], "Begründung"),
    (["ce_1", "BASIS", "x", "a", "6.11.2026", "", "approved"], "Datum"),
])
def test_cycle_overrides_rejected(row, msg):
    with pytest.raises(ov.OverrideError, match=msg):
        ov.validate_cycle_network(_ovr([row]), ["ce_1"])


# --- C-NET-07 density_scaling (open question 114, decision 2026-11-07) ----------------------------------------------


def test_density_scaling_params_from_rules():
    ds = next(r for r in CYC.network_design["rules"] if r["id"] == "C-NET-07")["density_scaling"]
    assert P.mesh_ref_density == ds["reference_density_per_km2"]["value"]
    assert set(P.mesh_density_levels) == set(ds["levels"]) <= {"HAUPT", "BASIS"}


def test_mesh_limit_scales_with_residents_per_mesh():
    base, ref = 600.0, 4000.0
    face = box(0, 0, 1000, 1000)                      # 1 km²
    def limit(residents):
        pts = np.array([[500.0, 500.0]]) if residents else np.empty((0, 2))
        lim = cn.MeshLimit(base, pts, np.array([residents] if residents else [], dtype=float), ref)
        return float(lim.limits(np.array([face]), np.array([1000.0]))[0])
    assert limit(ref) == pytest.approx(base)          # Delft density -> Delft mesh
    assert limit(ref / 4) == pytest.approx(2 * base)  # quarter density -> double side (same residents per mesh)
    assert limit(ref * 4) == pytest.approx(base)      # denser never below mesh_m.max
    assert limit(0) == np.inf                         # no residents -> not split


def test_mesh_limit_without_scaling_is_constant():
    lim = cn.MeshLimit(600.0)
    assert np.all(lim.limits(np.array([box(0, 0, 10, 10)]), np.array([10.0])) == 600.0)
