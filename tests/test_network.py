"""Segmentation on small synthetic networks (guide 3.2 Stufe 2, prompts/04_network.md)."""

import geopandas as gpd
import pytest
from shapely.geometry import LineString

from pipeline.lib.network import DuplicateSegmentIdError, segment_id, segments_from_edges

SPLIT_RULE = "S-NET-03"
MIN_LENGTH_M = 400.0


def _edges(rows: list[tuple], coords: dict[int, tuple[float, float]], crs="EPSG:25832") -> gpd.GeoDataFrame:
    """rows: (u, v, way_id, highway, maxspeed[, name]); geometry is the straight line u -> v."""
    records = []
    for row in rows:
        u, v, way_id, highway, maxspeed, *rest = row
        records.append({"u": u, "v": v, "way_id": way_id, "highway": highway, "maxspeed": maxspeed,
                        "name": rest[0] if rest else None, "geometry": LineString([coords[u], coords[v]])})
    return gpd.GeoDataFrame(records, geometry="geometry", crs=crs)


def _segments(edges: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    return segments_from_edges(edges, differ=["highway"], split_attribute="maxspeed",
                               min_length_m=MIN_LENGTH_M, split_rule_id=SPLIT_RULE)


# Straight line along x, nodes every 100 m.
LINE = {i: (1000.0 + 100 * i, 2000.0) for i in range(10)}


def test_degree_two_nodes_are_merged_across_ways():
    edges = _edges([(0, 1, 11, "residential", "30", "A-Str."), (1, 2, 11, "residential", "30", "A-Str."),
                    (2, 3, 12, "residential", "30", "A-Str.")], LINE)
    seg = _segments(edges)
    assert len(seg) == 1
    row = seg.iloc[0]
    assert row.osm_way_ids == [11, 12]
    assert row.length_m == pytest.approx(300)
    assert row["name"] == "A-Str."
    assert {row.node_u, row.node_v} == {0, 3}


def test_junction_splits():
    coords = {0: (0, 0), 1: (100, 0), 2: (200, 0), 3: (100, 100)}
    edges = _edges([(0, 1, 1, "residential", "30"), (1, 2, 1, "residential", "30"),
                    (1, 3, 2, "residential", "30")], coords)
    seg = _segments(edges)
    assert len(seg) == 3
    assert sorted(seg.length_m.round(6)) == [100, 100, 100]


def test_highway_change_and_pedestrian_zone_are_own_segments():
    edges = _edges([(0, 1, 1, "residential", "30"), (1, 2, 2, "pedestrian", None),
                    (2, 3, 2, "pedestrian", None), (3, 4, 3, "tertiary", "50")], LINE)
    seg = _segments(edges).sort_values("node_u")
    assert list(seg.highway) == ["residential", "pedestrian", "tertiary"]
    assert seg.set_index("highway").loc["pedestrian", "length_m"] == pytest.approx(200)


def test_isolated_ring_is_one_segment():
    coords = {0: (0, 0), 1: (100, 0), 2: (100, 100), 3: (0, 100)}
    edges = _edges([(0, 1, 5, "residential", "30"), (1, 2, 5, "residential", "30"),
                    (2, 3, 5, "residential", "30"), (3, 0, 5, "residential", "30")], coords)
    seg = _segments(edges)
    assert len(seg) == 1
    assert seg.iloc[0].length_m == pytest.approx(400)
    assert seg.iloc[0].geometry.is_ring


def test_roundabout_with_two_exits_gets_unique_ids():
    # One closed way (id 7) with two exits: both arcs have the same way id and end nodes.
    coords = {0: (0, 0), 1: (100, 0), 2: (100, 100), 3: (0, 100), 10: (-100, 0), 12: (200, 100)}
    edges = _edges([(0, 1, 7, "tertiary", "50"), (1, 2, 7, "tertiary", "50"), (2, 3, 7, "tertiary", "50"),
                    (3, 0, 7, "tertiary", "50"), (10, 0, 8, "tertiary", "50"), (2, 12, 9, "tertiary", "50")],
                   coords)
    seg = _segments(edges)
    assert len(seg) == 4
    assert seg.segment_id.is_unique


@pytest.mark.parametrize(
    "speeds, n_expected",
    [
        (["50"] * 3 + ["30"] * 3, 2),          # 600 m with a change -> split
        (["50", "50", "30", "30"], 1),          # 400 m is not longer than 400 m -> no split
        (["50"] * 6, 1),                        # no change
        (["50", "50", None, None, "50", "50"], 1),  # missing value is not a change
        (["50", "50", None, None, "30", "30"], 2),  # 50 -> (unknown) -> 30 is a change
        (["50", "50", "30", "30", "50", "50"], 3),
    ],
)
def test_long_segments_split_on_maxspeed_change(speeds, n_expected):
    edges = _edges([(i, i + 1, 100 + i, "secondary", s) for i, s in enumerate(speeds)], LINE)
    seg = _segments(edges)
    assert len(seg) == n_expected
    assert seg.length_m.sum() == pytest.approx(100 * len(speeds))
    expected_rule = SPLIT_RULE if n_expected > 1 else None
    assert set(seg.split_rule.where(seg.split_rule.notna(), None)) == {expected_rule}


def test_split_happens_at_first_edge_with_new_value():
    edges = _edges([(i, i + 1, 100 + i, "secondary", s)
                    for i, s in enumerate(["50", "50", None, "30", "30"])], LINE)
    seg = _segments(edges).sort_values("node_u")
    assert list(seg.node_u) == [0, 3]
    assert list(seg.maxspeed_osm) == ["50", "30"]


# --- IDs -------------------------------------------------------------------------------------

GRID_ROWS = [(0, 1, 1, "residential", "30"), (1, 2, 1, "residential", "30"), (1, 3, 2, "tertiary", "50"),
             (3, 4, 2, "tertiary", "50"), (4, 5, 3, "tertiary", "30"), (2, 6, 4, "pedestrian", None)]
GRID = {0: (0, 0), 1: (100, 0), 2: (200, 0), 3: (100, 100), 4: (100, 300), 5: (100, 700), 6: (300, 0)}


def test_ids_identical_on_second_run():
    edges = _edges(GRID_ROWS, GRID)
    assert list(_segments(edges).segment_id) == list(_segments(edges).segment_id)


def test_ids_independent_of_input_order_and_direction():
    a = _segments(_edges(GRID_ROWS, GRID))
    flipped = [(v, u, *rest) for u, v, *rest in reversed(GRID_ROWS)]
    b = _segments(_edges(flipped, GRID))
    assert set(a.segment_id) == set(b.segment_id)


def test_ids_survive_sub_metre_shift():
    shifted = {k: (x + 0.2, y - 0.3) for k, (x, y) in GRID.items()}
    assert set(_segments(_edges(GRID_ROWS, GRID)).segment_id) == \
        set(_segments(_edges(GRID_ROWS, shifted)).segment_id)


def test_segment_id_function():
    a = segment_id([3, 1, 2], [(10.4, 20.0), (0.0, 0.0)])
    assert a == segment_id([1, 2, 3, 3], [(0.0, 0.0), (10.0, 20.4)])
    assert a != segment_id([1, 2], [(0.0, 0.0), (10.0, 20.0)])
    assert a.startswith("seg_") and len(a) == 20


def test_duplicate_ids_raise():
    # Two identical parallel edges (same way, same nodes, same path) cannot be told apart.
    edges = _edges([(9, 0, 2, "residential", "30"), (0, 1, 1, "residential", "30"),
                    (0, 1, 1, "residential", "30"), (1, 2, 3, "residential", "30")], LINE)
    with pytest.raises(DuplicateSegmentIdError):
        _segments(edges)


# --- geometry, CRS, length -------------------------------------------------------------------


def test_geometry_crs_and_length_sum():
    edges = _edges(GRID_ROWS, GRID)
    seg = _segments(edges)
    assert seg.crs == "EPSG:25832"
    assert seg.geometry.is_valid.all()
    assert (seg.length_m > 0).all()
    assert seg.length_m.sum() == pytest.approx(edges.length.sum())
    assert seg.segment_id.is_unique


def test_geometry_runs_from_node_u_to_node_v():
    seg = _segments(_edges(GRID_ROWS, GRID))
    for row in seg.itertuples():
        assert row.geometry.coords[0] == pytest.approx(GRID[row.node_u])
        assert row.geometry.coords[-1] == pytest.approx(GRID[row.node_v])


def test_input_without_crs_raises():
    edges = _edges(GRID_ROWS, GRID).set_crs(None, allow_override=True)
    with pytest.raises(ValueError, match="CRS"):
        _segments(edges)


def test_input_in_other_crs_is_rejected():
    edges = _edges(GRID_ROWS, GRID).set_crs("EPSG:3857", allow_override=True)
    with pytest.raises(ValueError, match="EPSG:25832"):
        _segments(edges)


# --- S-NET-04 named access ways --------------------------------------------------------------

import pandas as pd  # noqa: E402

from pipeline.lib.network import select_ways  # noqa: E402
from pipeline.lib.rules import load_rules, network_highways  # noqa: E402


def _ways(*rows) -> pd.DataFrame:
    base = {"highway": "residential", "name": "A-Weg", "service": None, "access": None, "motor_vehicle": None,
            "motorcar": None, "tags": None}
    return pd.DataFrame([{**base, **r} for r in rows])


def test_network_highways_include_access_ways():
    rules = load_rules()
    assert set(network_highways(rules)) == set(rules.network.highway_classes.values) | {"service", "track"}


@pytest.mark.parametrize("row, keep", [
    ({}, True),
    ({"highway": "residential", "name": None}, True),         # main classes do not need a name
    ({"highway": "service"}, True),                           # named, no service subtype
    ({"highway": "service", "service": "alley"}, True),
    ({"highway": "service", "service": "parking_aisle"}, False),
    ({"highway": "service", "service": "driveway"}, False),
    ({"highway": "service", "name": None}, False),            # unnamed
    ({"highway": "track"}, True),                             # no access restriction
    ({"highway": "track", "tags": '{"vehicle": "destination"}'}, True),
    ({"highway": "track", "tags": {"vehicle": "destination"}}, True),
    ({"highway": "track", "motor_vehicle": "no"}, False),
    ({"highway": "track", "access": "agricultural"}, False),
    ({"highway": "track", "motor_vehicle": "destination", "access": "no"}, True),  # most specific key wins
    ({"highway": "service", "motor_vehicle": "no"}, True),    # access check applies to track only
    ({"highway": "footway"}, False),
    ({"highway": "path"}, False),
])
def test_select_ways(row, keep):
    assert select_ways(_ways(row), load_rules()).tolist() == [keep]
