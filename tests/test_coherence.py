"""Unit tests for pipeline/lib/coherence.py (rules N1–N7 on small synthetic networks).

Thresholds come from config/rules.yaml; the geometries are built relative to them.
"""

import geopandas as gpd
import pytest
from shapely.geometry import LineString, Point, box

from pipeline.lib import coherence as coh
from pipeline.lib.crs import WORK_CRS
from pipeline.lib.rules import load_rules


@pytest.fixture(scope="module")
def rules():
    return load_rules()


def make_segments(specs) -> gpd.GeoDataFrame:
    """specs: (segment_id, [coords], cat[, highway[, travel_speed_kmh]]). Node ids from coordinates."""
    node_ids: dict[tuple, int] = {}

    def nid(xy):
        return node_ids.setdefault(tuple(xy), len(node_ids) + 1)

    rows = []
    for spec in specs:
        sid, coords, cat, *rest = spec
        highway = rest[0] if rest else "residential"
        speed = rest[1] if len(rest) > 1 else 50.0
        line = LineString(coords)
        rows.append({"segment_id": sid, "node_u": nid(coords[0]), "node_v": nid(coords[-1]), "cat": cat,
                     "highway": highway, "travel_speed_kmh": speed, "length_m": line.length, "geometry": line})
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=WORK_CRS)


def flag_names(flags: dict, sid: str) -> set[str]:
    return {f["flag"] for f in flags.get(sid, [])}


def graph(specs, rules):
    return coh.build_graph(make_segments(specs), rules)


# --- N1 Durchgängigkeit ----------------------------------------------------------------------


def test_n1_dead_end_flagged_sw_end_ok(rules):
    g = graph([
        ("sw", [(-100, 0), (0, 0)], "SW"),
        ("g1", [(0, 0), (300, 0)], "GOW50"),
        ("g2", [(300, 0), (600, 0)], "GOW50"),
        ("e1", [(600, 0), (600, 200)], "ETW30"),
        ("e2", [(600, 0), (600, -200)], "ETW30"),
    ], rules)
    flags, ends = coh.n1_dead_ends(g, rules, area_edge_nodes=set(), city_boundary=None)
    assert flag_names(flags, "g2") == {"N1_dead_end"}
    assert "g1" not in flags
    status = {e["segment_id"]: e["status"] for e in ends}
    assert status == {"g1": "ok_sw", "g2": "dead_end"}


def test_n1_city_boundary_and_area_edge(rules):
    tol = rules.coherence_rule("N1").param("boundary_tolerance_m")
    specs = [("g1", [(0, 0), (500, 0)], "GOW30"), ("e1", [(500, 0), (500, 100)], "ETW30")]
    segs = make_segments(specs)
    g = coh.build_graph(segs, rules)
    boundary = LineString([(-tol / 2, -1000), (-tol / 2, 1000)])
    end_node = int(segs.loc[0, "node_v"])
    flags, ends = coh.n1_dead_ends(g, rules, area_edge_nodes={end_node}, city_boundary=boundary)
    assert flags == {}
    assert sorted(e["status"] for e in ends) == ["ok_city_boundary", "unknown_area_edge"]


def test_n1_continuous_ring_has_no_ends(rules):
    g = graph([("a", [(0, 0), (100, 0)], "GOW50"), ("b", [(100, 0), (100, 100)], "GOW30"),
               ("c", [(100, 100), (0, 0)], "GOW50")], rules)
    flags, ends = coh.n1_dead_ends(g, rules, area_edge_nodes=set(), city_boundary=None)
    assert flags == {} and ends == []


# --- N2 Inseln / N7 Glättung -----------------------------------------------------------------


def _line_with_middle(mid_len: float, mid_cat: str = "ETW30"):
    return [
        ("a", [(0, 0), (300, 0)], "GOW50"),
        ("m", [(300, 0), (300 + mid_len, 0)], mid_cat),
        ("b", [(300 + mid_len, 0), (600 + mid_len, 0)], "GOW50"),
        # side streets make the joints real junctions (degree 3)
        ("s1", [(300, 0), (300, 100)], "ETW30"),
        ("s2", [(300 + mid_len, 0), (300 + mid_len, -100)], "ETW30"),
    ]


def test_n2_short_island_flagged_with_smoothing(rules):
    min_run = rules.coherence_rule("N2").param("min_run_m")
    flags = coh.n2_islands(graph(_line_with_middle(min_run * 0.75), rules), rules)
    assert flag_names(flags, "m") == {"N2_island", "N7_smooth:GOW50"}
    assert {"a", "b", "s1", "s2"}.isdisjoint(flags)


def test_n2_long_run_not_flagged(rules):
    min_run = rules.coherence_rule("N2").param("min_run_m")
    assert coh.n2_islands(graph(_line_with_middle(min_run * 1.25), rules), rules) == {}


def test_n2_needs_same_category_on_both_sides(rules):
    specs = _line_with_middle(100)
    specs[2] = ("b", [(400, 0), (700, 0)], "GOW30")
    assert coh.n2_islands(graph(specs, rules), rules) == {}


def test_n2_no_continuation_around_sharp_turn(rules):
    # Middle piece turns 90° at both ends: not one street, so no island.
    specs = [
        ("a", [(0, 0), (300, 0)], "GOW50"),
        ("m", [(300, 0), (300, 100)], "ETW30"),
        ("b", [(300, 100), (600, 100)], "GOW50"),
        ("s1", [(300, 0), (600, 0)], "ETW30"),
        ("s2", [(300, 100), (0, 100)], "ETW30"),
    ]
    assert "m" not in coh.n2_islands(graph(specs, rules), rules)


def test_n2_degree_two_bend_continues(rules):
    specs = [("a", [(0, 0), (300, 0)], "GOW50"), ("m", [(300, 0), (300, 100)], "GOW30"),
             ("b", [(300, 100), (600, 100)], "GOW50")]
    assert flag_names(coh.n2_islands(graph(specs, rules), rules), "m") == {"N2_island", "N7_smooth:GOW50"}


# --- N3 Aufenthaltsbereiche ------------------------------------------------------------------


def _ring(size: float, cat="GOW50", x0=0.0):
    c = [(x0, 0), (x0 + size, 0), (x0 + size, size), (x0, size)]
    return [(f"r{i}", [c[i], c[(i + 1) % 4]], cat) for i in range(4)]


def test_n3_small_enclosed_area_flags_inner_etw(rules):
    min_ha = rules.coherence_rule("N3").param("min_area_ha")
    size = (min_ha * 0.5 * 10_000) ** 0.5
    specs = _ring(size) + [("inner", [(0, size / 2), (size / 2, size / 2)], "ETW30")]
    segs = make_segments(specs)
    work_area = box(-1000, -1000, size + 1000, size + 1000)
    areas, flags = coh.n3_areas(segs, rules, work_area=work_area, city_area=None)
    small = areas[areas["small"]]
    assert len(small) == 1 and bool(small.iloc[0]["complete"])
    assert small.iloc[0]["area_ha"] == pytest.approx(min_ha * 0.5, rel=1e-6)
    assert flag_names(flags, "inner") == {"N3_small_area"}
    assert not any(k.startswith("r") for k in flags)


def test_n3_area_without_etw_is_not_small(rules):
    # e.g. a traffic island between two carriageways
    areas, flags = coh.n3_areas(make_segments(_ring(20)), rules, work_area=box(-1000, -1000, 1000, 1000), city_area=None)
    assert flags == {}
    ring_area = areas[areas.contains(Point(10, 10))].iloc[0]
    assert not ring_area["has_etw"] and not ring_area["small"]


def test_n3_large_area_not_flagged(rules):
    min_ha = rules.coherence_rule("N3").param("min_area_ha")
    size = (min_ha * 1.5 * 10_000) ** 0.5
    specs = _ring(size) + [("inner", [(10, 10), (20, 20)], "ETW30")]
    areas, flags = coh.n3_areas(make_segments(specs), rules, work_area=box(-1000, -1000, size + 1000, size + 1000),
                                city_area=None)
    assert flags == {}
    assert not areas["small"].any()


def test_n3_area_at_work_area_edge_is_incomplete(rules):
    # Only three GOW sides; the fourth side is the edge of the work area.
    specs = [
        ("a", [(0, 0), (200, 0)], "GOW50"),
        ("b", [(200, 0), (200, 300)], "GOW50"),
        ("c", [(0, 0), (0, 300)], "GOW50"),
        ("inner", [(50, 50), (100, 100)], "ETW30"),
    ]
    areas, flags = coh.n3_areas(make_segments(specs), rules, work_area=box(-500, -500, 700, 300), city_area=None)
    assert flags == {}
    inner_area = areas[areas.contains(Point(75, 75))]
    assert len(inner_area) == 1 and not bool(inner_area.iloc[0]["complete"])


def test_n3_railway_splits_area(rules):
    # rules.yaml 0.16.0 (open question 52): railways and rivers bound areas like GOW lines
    min_ha = rules.coherence_rule("N3").param("min_area_ha")
    size = (min_ha * 1.5 * 10_000) ** 0.5      # one large area, two small halves
    specs = _ring(size) + [("left", [(10, 10), (20, 20)], "ETW30"), ("right", [(size - 20, 10), (size - 10, 20)], "ETW30")]
    rail = [LineString([(size / 2, -5), (size / 2, size + 5)])]
    work_area = box(-1000, -1000, size + 1000, size + 1000)
    _, no_rail = coh.n3_areas(make_segments(specs), rules, work_area=work_area, city_area=None)
    areas, flags = coh.n3_areas(make_segments(specs), rules, work_area=work_area, city_area=None, barriers=rail)
    assert no_rail == {}
    assert flag_names(flags, "left") == flag_names(flags, "right") == {"N3_small_area"}
    assert areas["small"].sum() == 2


# --- N4 Schleichverkehr ----------------------------------------------------------------------


def _detour(etw_len: float, highway="residential"):
    return [
        ("g1", [(0, 0), (1000, 0)], "GOW50"),
        ("g2", [(1000, 0), (1000, etw_len)], "GOW50"),
        ("g3", [(1000, etw_len), (0, etw_len)], "GOW50"),
        ("short", [(0, 0), (0, etw_len)], "ETW30", highway),
    ]


def test_n4_shortcut_over_etw_flagged(rules):
    max_etw = rules.coherence_rule("N4").param("max_etw_m")
    flags, stats = coh.n4_shortcuts(graph(_detour(max_etw * 1.5), rules), rules)
    assert flag_names(flags, "short") == {"N4_shortcut"}
    assert flags["short"][0]["inputs"]["n_od_pairs"] >= 1
    assert stats["od_nodes"] == 4 and stats["od_pairs"] == 6 and stats["flagged_pairs"] >= 1


def test_n4_short_etw_not_flagged(rules):
    max_etw = rules.coherence_rule("N4").param("max_etw_m")
    flags, stats = coh.n4_shortcuts(graph(_detour(max_etw * 0.8), rules), rules)
    assert flags == {} and stats["flagged_pairs"] == 0


def test_n4_no_gow_path_is_counted_not_flagged(rules):
    max_etw = rules.coherence_rule("N4").param("max_etw_m")
    specs = [("g1", [(0, 0), (500, 0)], "GOW50"), ("e", [(500, 0), (500, max_etw * 2)], "ETW30"),
             ("g2", [(500, max_etw * 2), (1000, max_etw * 2)], "GOW50")]
    flags, stats = coh.n4_shortcuts(graph(specs, rules), rules)
    # rules.yaml 0.16.0 (open question 54): the ETW link is flagged as a gap in the GOW network, not as a shortcut
    assert flag_names(flags, "e") == {"N4_gow_gap"} and flags["e"][0]["inputs"]["n_od_pairs"] == 4
    assert "g1" not in flags and "g2" not in flags
    assert stats["flagged_pairs"] == 0 and stats["etw_only_pairs"] == 4


def test_n4_pedestrian_ways_are_not_driven(rules):
    max_etw = rules.coherence_rule("N4").param("max_etw_m")
    flags, _ = coh.n4_shortcuts(graph(_detour(max_etw * 1.5, highway="pedestrian"), rules), rules)
    assert flags == {}


def test_segment_speed_uses_category_or_fallback(rules):
    assert coh.segment_speed_kmh("GOW30", 50.0, rules) == 30
    assert coh.segment_speed_kmh("SW", 80.0, rules) == 80.0


# --- N5 Übergänge ----------------------------------------------------------------------------


def test_n5_direct_80_to_30_flagged(rules):
    g = graph([("fast", [(0, 0), (100, 0)], "GOW80"), ("slow", [(100, 0), (200, 0)], "GOW30")], rules)
    flags, nodes = coh.n5_transitions(g, rules)
    assert flag_names(flags, "slow") == {"N5_direct_to_30"}
    assert "fast" not in flags
    assert any(n["direct_to_30"] for n in nodes)


def test_n5_sw_uses_travel_speed(rules):
    g = graph([("ramp", [(0, 0), (100, 0)], "SW", "motorway_link", 80.0),
               ("e", [(100, 0), (200, 0)], "ETW30")], rules)
    flags, _ = coh.n5_transitions(g, rules)
    assert flag_names(flags, "e") == {"N5_direct_to_30"}
    g = graph([("ramp", [(0, 0), (100, 0)], "SW", "motorway_link", 50.0),
               ("e", [(100, 0), (200, 0)], "ETW30")], rules)
    assert coh.n5_transitions(g, rules)[0] == {}


def test_n5_gate_transitions_listed_not_flagged(rules):
    g = graph([("a", [(0, 0), (100, 0)], "GOW50"), ("b", [(100, 0), (200, 0)], "GOW30"),
               ("c", [(100, 0), (100, 100)], "ETW30")], rules)
    flags, nodes = coh.n5_transitions(g, rules)
    assert flags == {}
    gates = {tuple(gt) for n in nodes for gt in n["gates"]}
    assert ("GOW50", "GOW30") in gates and ("GOW50", "ETW30") in gates and ("GOW30", "ETW30") in gates


# --- N6 ---------------------------------------------------------------------------------------
# Since rules.yaml 0.19.0 (Review 2026-11 F09) N6 reads the Soll junction type of c07; tests in tests/test_junctions.py
# and tests/test_junctions_data.py (V-INV-02).


def test_n6_has_no_own_junction_table(rules):
    n6 = rules.coherence_rule("N6")
    assert n6.source_of_truth == "design_rules.junctions.decision_table"
    assert not hasattr(coh, "n6_node_types")
    assert {"node_types", "ist_check", "thresholds"}.isdisjoint(set(n6.model_extra or {}) | ({"thresholds"} if n6.thresholds else set()))


# --- combined ---------------------------------------------------------------------------------


def test_merge_flags_keeps_order_and_ids():
    merged = coh.merge_flags({"a": [{"id": "N2", "flag": "N2_island", "inputs": {}}]},
                             {"a": [{"id": "N4", "flag": "N4_shortcut", "inputs": {}}],
                              "b": [{"id": "N4", "flag": "N4_shortcut", "inputs": {}}]})
    assert [f["flag"] for f in merged["a"]] == ["N2_island", "N4_shortcut"]
    assert list(merged) == ["a", "b"]


def test_polygonal_drops_line_slivers_from_intersections():
    """work_area ∩ city can be a GeometryCollection (polygons plus shared edges); its boundary would be None."""
    from shapely.geometry import GeometryCollection, LineString, box
    from pipeline.lib.coherence import _polygonal
    g = GeometryCollection([box(0, 0, 10, 10), LineString([(10, 0), (20, 0)]), box(30, 0, 40, 10)])
    p = _polygonal(g)
    assert p.geom_type == "MultiPolygon" and p.area == 200 and p.boundary is not None
