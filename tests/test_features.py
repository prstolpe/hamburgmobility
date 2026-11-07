"""Feature helpers (pipeline/lib/features.py, gtfs.py, betweenness.py; rules S-FEAT-01..10).

Parameters come from config/rules.yaml, so the tests follow a recalibrated rule file.
"""

import datetime as dt
import math
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import LineString, Point, box

from pipeline.lib import gtfs
from pipeline.lib.betweenness import edge_betweenness
from pipeline.lib.features import (
    FeatureParams,
    area_weighted_sum,
    building_density,
    count_near,
    alkis_buildings,
    frontage_share,
    ist_speed,
    majority,
    nearest_distance,
    parse_osm_speed,
    percentile_rank,
    travel_speed_kmh,
    way_design,
    weighted_score,
)
from pipeline.lib.rules import load_rules, network_highways

CRS = "EPSG:25832"
GTFS_DIR = Path(__file__).parent / "fixtures" / "gtfs_min"


@pytest.fixture(scope="module")
def params() -> FeatureParams:
    return FeatureParams.from_rules(load_rules())


def _gs(*geoms) -> gpd.GeoSeries:
    return gpd.GeoSeries(list(geoms), crs=CRS)


# --- rules.yaml section features -------------------------------------------------------------


def test_feature_rules_in_rules_yaml():
    rules = load_rules()
    ids = [r.id for r in rules.features.rules]
    assert ids == [f"S-FEAT-{i:02d}" for i in range(1, 12)]  # S-FEAT-11 since rules.yaml 0.16.0
    assert rules.features.rule("S-FEAT-01").method == "percentile_rank"
    for rule in rules.features.rules:
        assert rule.status == "draft"


def test_default_speed_for_every_routed_highway_class(params):
    rules = load_rules()
    routed = set(network_highways(rules)) - set(params.exclude_highway)
    assert routed == set(params.default_speed_kmh)


# --- S-FEAT-01 normalisation -----------------------------------------------------------------


def test_percentile_rank_ties_take_lowest_rank(params):
    # S-FEAT-01 (rules.yaml 0.5.0): ties get the lowest rank, so the smallest value maps to 0.
    assert params.ties == "min"
    s = pd.Series([0.0, 0.0, 0.0, 20.0, 40.0, None])
    r = percentile_rank(s, ties=params.ties)
    assert list(r.iloc[:3]) == [0.0, 0.0, 0.0]
    assert r.iloc[3] == pytest.approx(3 / 4) and r.iloc[4] == 1.0
    assert pd.isna(r.iloc[5])


def test_percentile_rank_average_ties():
    r = percentile_rank(pd.Series([10.0, 20.0, 20.0, 40.0]), ties="average")
    assert r.iloc[0] == 0.0 and r.iloc[3] == 1.0
    assert r.iloc[1] == r.iloc[2] == pytest.approx(0.5)


def test_percentile_rank_without_spread():
    assert percentile_rank(pd.Series([5.0]), ties="min").iloc[0] == 0.0
    assert (percentile_rank(pd.Series([3.0, 3.0, 3.0]), ties="min") == 0.0).all()
    assert (percentile_rank(pd.Series([3.0, 3.0]), ties="average") == 0.5).all()
    assert percentile_rank(pd.Series([None, None], dtype="float64"), ties="min").isna().all()


def test_percentile_rank_rejects_unknown_ties():
    with pytest.raises(ValueError):
        percentile_rank(pd.Series([1.0, 2.0]), ties="max")


def test_percentile_rank_respects_mask():
    s = pd.Series([1.0, 2.0, 100.0])
    r = percentile_rank(s, mask=pd.Series([True, True, False]), ties="min")
    assert list(r.iloc[:2]) == [0.0, 1.0]
    assert pd.isna(r.iloc[2])


def test_weighted_score_redistributes_missing_weight():
    norms = pd.DataFrame({"a": [1.0, 1.0, None], "b": [0.0, None, None]})
    score, available = weighted_score(norms, {"a": 0.75, "b": 0.25})
    assert score.iloc[0] == pytest.approx(0.75)
    assert score.iloc[1] == pytest.approx(1.0)  # b missing: weight moves to a
    assert available.iloc[1] == pytest.approx(0.75)
    assert pd.isna(score.iloc[2]) and available.iloc[2] == 0.0


def test_weighted_score_needs_all_columns():
    with pytest.raises(KeyError):
        weighted_score(pd.DataFrame({"a": [1.0]}), {"a": 0.5, "b": 0.5})


# --- S-FEAT-02 / S-FEAT-09 speeds ------------------------------------------------------------


@pytest.mark.parametrize("text, expected", [("30", 30), ("50", 50), ("50 / 30", None), ("walk", None),
                                            ("none", None), (None, None), ("DE:urban", None)])
def test_parse_osm_speed(text, expected):
    assert parse_osm_speed(text) == expected


def test_travel_speed_precedence(params):
    defaults = params.default_speed_kmh
    assert travel_speed_kmh(30, "50", "primary", defaults) == (30, "official")
    assert travel_speed_kmh(None, "50", "residential", defaults) == (50, "osm")
    assert travel_speed_kmh(None, "50 / 30", "residential", defaults) == (defaults["residential"], "default")
    assert travel_speed_kmh(None, None, "pedestrian", defaults) == (None, None)


def test_ist_speed_and_conflict():
    assert ist_speed(30, "50") == (30, "official", True)
    assert ist_speed(50, "50") == (50, "official", False)
    assert ist_speed(None, "30") == (30, "osm", False)
    assert ist_speed(None, "30 / 50") == (None, None, False)
    assert ist_speed(None, None) == (None, None, False)


def test_edge_betweenness_bridge_is_highest():
    # Two triangles joined by one bridge edge (2-3): every path between them uses the bridge.
    u = [0, 1, 2, 2, 3, 4, 5]
    v = [1, 2, 0, 3, 4, 5, 3]
    b = edge_betweenness(np.array(u), np.array(v), np.ones(7))
    assert int(np.argmax(b)) == 3
    assert b[3] == pytest.approx(9.0)  # 3 x 3 node pairs


def test_edge_betweenness_uses_weights():
    # Square 0-1-2-3-0: a slow edge 0-1 pushes the 0->1 path around the square.
    u, v = np.array([0, 1, 2, 3]), np.array([1, 2, 3, 0])
    slow = edge_betweenness(u, v, np.array([10.0, 1.0, 1.0, 1.0]))
    assert slow[0] < slow[1]


def test_edge_betweenness_skips_nan_weight_edges():
    u, v = np.array([0, 1, 0]), np.array([1, 2, 2])
    b = edge_betweenness(u, v, np.array([1.0, 1.0, np.nan]))
    assert math.isnan(b[2])
    assert b[0] == pytest.approx(2.0)


# --- S-FEAT-03..06 surroundings --------------------------------------------------------------


def test_building_density_share_of_buffer():
    seg = _gs(LineString([(0, 0), (100, 0)]))
    buildings = _gs(box(0, 5, 100, 15))  # 1000 m², fully inside a 20 m buffer
    d = building_density(seg, buildings, buffer_m=20)
    assert d.iloc[0] == pytest.approx(1000 / seg.buffer(20).area.iloc[0])
    assert building_density(seg, _gs(), buffer_m=20).iloc[0] == 0.0


def test_area_weighted_sum_counts_cell_shares():
    seg = _gs(LineString([(0, 0), (100, 0)]))
    cells = gpd.GeoDataFrame({"population": [100.0, 40.0]},
                             geometry=[box(0, 0, 100, 100), box(0, 500, 100, 600)], crs=CRS)
    got = area_weighted_sum(seg, cells, "population", buffer_m=10)
    inside = seg.buffer(10).intersection(box(0, 0, 100, 100)).area.iloc[0]
    assert got.iloc[0] == pytest.approx(100 * inside / 10_000)


def test_frontage_share_and_counts(params):
    seg = _gs(LineString([(0, 0), (100, 0)]))
    buildings = gpd.GeoDataFrame(
        {"shop": [None, "bakery", None, None], "amenity": [None, None, "parking", None]},
        geometry=[box(0, 5, 10, 15), box(20, 5, 30, 15), box(40, 5, 50, 15), box(0, 500, 10, 510)], crs=CRS)
    pois = gpd.GeoDataFrame({"shop": [None], "amenity": ["cafe"]}, geometry=[Point(5, 10)], crs=CRS)
    share, n_total, n_public = frontage_share(seg, buildings, pois, params.frontage_buffer_m, params.amenity_excluded)
    # Building 1 has a cafe inside, building 2 is a shop, building 3 only parking (excluded), building 4 too far.
    assert (n_total.iloc[0], n_public.iloc[0]) == (3, 2)
    assert share.iloc[0] == pytest.approx(2 / 3)


def test_alkis_buildings_filters_type_and_position(params):
    b = gpd.GeoDataFrame(
        {"gebnutzbez": ["Gebaeude", "Gebaeude", "Bauteil", "Gebaeude"],
         "funktion": ["Wohnhaus", "Tiefgarage", "Wohnhaus", "Garage"],
         "rellage": [None, "Unter der Erdoberfläche", None, None]},
        geometry=[box(0, 0, 1, 1)] * 4, crs=CRS)
    got = alkis_buildings(b, params)
    assert list(got["funktion"]) == ["Wohnhaus", "Garage"]
    assert list(got["public"]) == [False, False]
    assert list(got["ancillary"]) == [False, True]


def test_frontage_share_with_alkis_function(params):
    seg = _gs(LineString([(0, 0), (100, 0)]))
    public_fn = sorted(params.alkis_public_functions)[0]
    raw = gpd.GeoDataFrame(
        {"gebnutzbez": ["Gebaeude"] * 4, "funktion": [public_fn, "Wohnhaus", "Wohnhaus", "Garage"],
         "rellage": [None] * 4},
        geometry=[box(0, 5, 10, 15), box(20, 5, 30, 15), box(40, 5, 50, 15), box(60, 5, 70, 15)], crs=CRS)
    b = alkis_buildings(raw, params)
    pois = gpd.GeoDataFrame({"shop": ["bakery"], "amenity": [None]}, geometry=[Point(25, 10)], crs=CRS)
    share, n_total, n_public = frontage_share(seg, b, pois, params.frontage_buffer_m, params.amenity_excluded)
    # ALKIS public use + OSM shop inside the second building; the garage is not counted at all.
    assert (n_total.iloc[0], n_public.iloc[0]) == (3, 2)
    assert share.iloc[0] == pytest.approx(2 / 3)


def test_public_function_lists_use_real_alkis_values(params):
    assert "Gebäude für Handel und Dienstleistungen" in params.alkis_public_functions
    assert "Allgemein bildende Schule" not in params.alkis_public_functions  # counted by S-FEAT-06
    assert "Garage" in params.alkis_ancillary_functions
    assert not params.alkis_public_functions & params.alkis_ancillary_functions


def test_frontage_share_zero_without_buildings(params):
    # rules.yaml 0.16.0 (open question 45): no building in the buffer = no public use, not unknown
    seg = _gs(LineString([(0, 0), (100, 0)]))
    empty = gpd.GeoDataFrame({"shop": [], "amenity": []}, geometry=[], crs=CRS)
    share, n_total, _ = frontage_share(seg, empty, empty, params.frontage_buffer_m, params.amenity_excluded)
    assert share.iloc[0] == 0.0 and n_total.iloc[0] == 0


def test_nearest_distance():
    seg = _gs(LineString([(0, 0), (100, 0)]), LineString([(0, 300), (100, 300)]))
    d = nearest_distance(seg, _gs(Point(50, 40), box(0, 380, 10, 390)))
    assert list(d.round(6)) == [40.0, 80.0]
    assert nearest_distance(seg, _gs()).isna().all()


def test_count_near():
    seg = _gs(LineString([(0, 0), (100, 0)]))
    pts = _gs(Point(10, 0), Point(50, 0.5), Point(60, 5))
    assert count_near(seg, pts, snap_m=1).iloc[0] == 2


# --- S-FEAT-10 OSM design --------------------------------------------------------------------


def test_way_design_cycleways():
    assert way_design({"cycleway:right": "track", "cycleway:left": "lane"})["separated_cycle_track_present"] is True
    assert way_design({"cycleway:both": "lane"})["cycle_lane_present"] is True
    assert way_design({"cycleway:both": "lane"})["separated_cycle_track_present"] is False
    assert way_design({"cycleway:right": "separate"})["separated_cycle_track_present"] is True
    assert way_design({"bicycle": "use_sidepath"})["separated_cycle_track_present"] is True
    assert way_design({"cycleway": "no"})["separated_cycle_track_present"] is False
    untagged = way_design({})
    assert untagged["separated_cycle_track_present"] is None and untagged["cycle_lane_present"] is None


def test_way_design_lanes_markings_surface_motorroad():
    d = way_design({"lanes": "4", "lane_markings": "no", "surface": "asphalt", "motorroad": "yes"})
    assert (d["lanes"], d["centre_line"], d["surface"], d["motorroad"]) == (4, False, "asphalt", True)
    d = way_design({"lanes": "2;3"})
    assert d["lanes"] is None and d["centre_line"] is None and d["motorroad"] is None


def test_way_design_parking_new_scheme():
    d = way_design({"parking:both": "lane", "parking:both:orientation": "diagonal"})
    assert (d["parking"], d["parking_on_carriageway"], d["parking_along_carriageway"], d["angle_parking"]) == \
        ("lane", True, True, True)
    d = way_design({"parking:left": "street_side", "parking:right": "no"})
    assert (d["parking"], d["parking_on_carriageway"], d["parking_along_carriageway"]) == ("no|street_side", False, True)


def test_way_design_parking_old_scheme():
    d = way_design({"parking:lane:both": "parallel", "parking:lane:both:parallel": "half_on_kerb"})
    assert (d["parking"], d["parking_on_carriageway"], d["angle_parking"]) == ("half_on_kerb", True, False)
    d = way_design({"parking:lane:right": "no_stopping"})
    assert (d["parking"], d["parking_along_carriageway"]) == ("no", False)
    assert way_design({})["parking"] is None


def test_majority_weighted_and_null():
    assert majority([True, False, None], [10.0, 30.0, 100.0]) is False
    assert majority(["asphalt", "sett"], [5.0, 1.0]) == "asphalt"
    assert majority([None, None], [1.0, 1.0]) is None
    assert majority([], []) is None


# --- S-FEAT-08 GTFS --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def feed() -> dict:
    return gtfs.load_feed(GTFS_DIR)


def test_active_services(feed):
    assert gtfs.active_services(feed, dt.date(2026, 1, 7)) == set()  # WK removed (holiday)
    assert gtfs.active_services(feed, dt.date(2026, 1, 13)) == {"WK", "X"}
    assert gtfs.active_services(feed, dt.date(2026, 1, 10)) == {"SA"}


def test_representative_weekday(feed):
    day = gtfs.representative_weekday(feed)
    assert day == dt.date(2026, 1, 13)
    assert day.weekday() in (1, 2, 3)


def test_bus_trips_per_shape(params, feed):
    trips, without_shape = gtfs.trips_per_shape(feed, dt.date(2026, 1, 13), params.bus_route_types)
    assert trips.to_dict() == {"s1": 4}  # t1, t2, t3 (route_type 700), t6; subway s2 excluded
    assert without_shape == 1  # t7


def test_shapes_filtered_by_id(feed):
    assert list(gtfs.shapes_gdf(feed, ["s2"]).index) == ["s2"]


def test_frequencies_rejected(tmp_path):
    for f in GTFS_DIR.iterdir():
        (tmp_path / f.name).write_text(f.read_text())
    (tmp_path / "frequencies.txt").write_text("trip_id,start_time,end_time,headway_secs\nt1,06:00:00,09:00:00,600\n")
    with pytest.raises(ValueError, match="frequencies"):
        gtfs.load_feed(tmp_path)


def test_shapes_in_work_crs(feed):
    shapes = gtfs.shapes_gdf(feed)
    assert shapes.crs == CRS
    s1 = shapes.loc["s1"].geometry
    assert s1.geom_type == "LineString"
    xs = [c[0] for c in s1.coords]
    assert xs == sorted(xs)  # ordered by shape_pt_sequence


def test_parallel_cycle_route_present():
    # S-FEAT-11 (rules.yaml 0.16.0): own cycle path or official network running parallel within buffer_m
    from pipeline.lib.conflate import MatchParams
    from pipeline.lib.features import parallel_route_present
    seg = _gs(LineString([(0, 0), (300, 0)]), LineString([(0, 1000), (300, 1000)]), LineString([(0, 2000), (0, 2300)]))
    paths = _gs(LineString([(-50, 150), (350, 150)]),   # parallel 150 m away from the first segment
                LineString([(-100, 2150), (200, 2150)]))  # crosses the third one at a right angle
    mp_ = MatchParams(buffer_m=200, max_angle_deg=20, min_overlap_share=0.6)
    assert list(parallel_route_present(seg, paths, mp_, min_share=0.5)) == [True, False, False]
