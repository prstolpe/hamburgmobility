"""Junction arm filter (J-M-01, redesign 2026-11 package 5): a node is a junction only if it has at least min_arms arms
after the carriageways are merged (J-M-02 arm_merge), or if a standalone cycle path meets it. Points where a street
only splits into two carriageways (lane-split points) are no junctions: within pseudo_join_m of a real junction of the
same street they join it (node_id of the real junction stays), otherwise they are dropped.
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

from pipeline import c07_junctions as c07
from pipeline.lib import junction_filter as jf
from pipeline.lib.rules import load_design_rules

DESIGN = load_design_rules()
M = DESIGN.junctions.method_rule
M02 = M("J-M-02")
SEARCH = float(M("J-M-03")["search_radius_m"]["value"])


def _street(rows):
    """rows: (segment_id, node_u, node_v, coords, name, cat)"""
    return gpd.GeoDataFrame({
        "segment_id": [r[0] for r in rows], "node_u": [r[1] for r in rows], "node_v": [r[2] for r in rows],
        "geometry": [LineString(r[3]) for r in rows], "name": [r[4] for r in rows], "cat_final": [r[5] for r in rows],
        "cycle_cat": "ERSCHL", "facility": None, "dtv_official": 20000.0, "tram": False, "lanes": None, "bezirk": "X",
    }, crs="EPSG:25832").assign(length_m=lambda d: d.length)


NO_PATHS = pd.DataFrame({"edge_id": [], "node_u": [], "node_v": [], "geometry": [], "cycle_cat_final": [], "bezirk": [],
                         "name": []})

# A runs west-east and is divided between x=-50 and x=+50 (carriageways at y=+8 / y=-8); B crosses north-south at x=0.
# Nodes: 1 W split (-50,0), 2 E split (50,0), 3 (0,8), 4 (0,-8); far away: 20 a T-junction of D/E at (2200,0) and 10 a
# split point of street C at (2240,30), 50 m from it but on another street.
SEG = _street([
    ("a_w", 100, 1, [(-200, 0), (-50, 0)], "A", "GOW50"),
    ("a_n1", 1, 3, [(-50, 0), (-40, 8), (0, 8)], "A", "GOW50"),
    ("a_s1", 1, 4, [(-50, 0), (-40, -8), (0, -8)], "A", "GOW50"),
    ("a_n2", 3, 2, [(0, 8), (40, 8), (50, 0)], "A", "GOW50"),
    ("a_s2", 4, 2, [(0, -8), (40, -8), (50, 0)], "A", "GOW50"),
    ("a_e", 2, 101, [(50, 0), (200, 0)], "A", "GOW50"),
    ("b_n", 3, 102, [(0, 8), (0, 200)], "B", "GOW30"),
    ("b_m", 4, 3, [(0, -8), (0, 8)], "B", "GOW30"),
    ("b_s", 4, 103, [(0, -8), (0, -200)], "B", "GOW30"),
    ("c_w", 104, 10, [(2040, 30), (2240, 30)], "C", "GOW50"),
    ("c_n", 10, 105, [(2240, 30), (2250, 38), (2440, 38)], "C", "GOW50"),
    ("c_s", 10, 106, [(2240, 30), (2250, 22), (2440, 22)], "C", "GOW50"),
    ("t_w", 107, 20, [(2000, 0), (2200, 0)], "D", "ETW30"),
    ("t_e", 20, 108, [(2200, 0), (2400, 0)], "D", "ETW30"),
    ("t_n", 20, 109, [(2200, 0), (2200, 200)], "E", "ETW30"),
])
PARAMS = jf.FilterParams.from_rule(M("J-M-01"))


def _run(seg=SEG, paths=NO_PATHS):
    pts = c07.node_points(seg)
    clusters = c07.build_clusters(seg, paths, set(), radius=25)
    legs = c07.describe_legs(clusters, seg, paths, pts, M02, SEARCH)
    return clusters, *jf.filter_pseudo(clusters, legs, pts, PARAMS)


def test_params_come_from_the_rule_file():
    m01 = M("J-M-01")
    assert PARAMS.min_arms == m01["min_arms"]["value"] == 3
    assert PARAMS.join_m == m01["pseudo_join_m"]["value"]


def test_before_the_filter_split_points_are_junctions():
    clusters, *_ = _run()
    assert {1, 2, 3, 10, 20} <= set(clusters)


def test_split_points_join_the_real_junction_and_keep_its_id():
    _, out, stats = _run()
    assert out[3] == [1, 2, 3, 4]  # real junction (root 3) absorbs both split points
    assert 1 not in out and 2 not in out


def test_lone_split_point_is_dropped():
    _, out, stats = _run()
    assert 10 not in out and not any(10 in m for m in out.values())
    assert stats["dropped"] == [10] and sorted(stats["joined"]) == [1, 2]


def test_t_junction_stays():
    _, out, _ = _run()
    assert out[20] == [20]


def test_cycle_path_keeps_a_two_arm_node():
    paths = pd.DataFrame({"edge_id": ["p"], "node_u": [10], "node_v": [999], "geometry": [LineString([(2240, 30), (2240, 130)])],
                          "cycle_cat_final": ["BASIS"], "bezirk": ["X"], "name": [None]})
    _, out, stats = _run(paths=paths)
    assert out[10] == [10] and 10 not in stats["dropped"]


def test_split_point_of_another_street_does_not_join():
    pts = c07.node_points(SEG)
    assert pts[10].distance(pts[20]) <= PARAMS.join_m  # in range of the T-junction, but street C does not meet it
    _, out, stats = _run()
    assert 10 in stats["dropped"] and out[20] == [20]


def test_far_split_point_does_not_join():
    p = jf.FilterParams(min_arms=3, join_m=20.0)
    pts = c07.node_points(SEG)
    clusters = c07.build_clusters(SEG, NO_PATHS, set(), radius=25)
    legs = c07.describe_legs(clusters, SEG, NO_PATHS, pts, M02, SEARCH)
    out, stats = jf.filter_pseudo(clusters, legs, pts, p)
    assert out[3] == [3, 4] and sorted(stats["dropped"]) == [1, 2, 10]
