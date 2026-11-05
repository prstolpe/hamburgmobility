"""Cycle demand model (prompts/15, pipeline/lib/cycle_demand.py): zones, attraction, gravity,
assignment on shortest-path trees, calibration, counter cross-sections and demand_confidence.

Parameters come from config/cycling_rules.yaml (demand_model, demand.peak_hour_share_of_day).
"""

import math

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import LineString, Point

from pipeline.lib import cycle_demand as cd
from pipeline.lib.rules import load_cycling_rules

CYC = load_cycling_rules()
P = cd.DemandParams.from_rules(CYC)


# --- C-DEM-01 zones ----------------------------------------------------------------------------


def test_zone_index_floors_to_zone_size():
    ix, iy = cd.zone_index(np.array([0.0, 499.9, 500.0, -0.1]), np.array([0.0, 0.0, 999.0, 0.0]), 500)
    assert ix.tolist() == [0, 0, 1, -1] and iy.tolist() == [0, 0, 1, 0]


def test_aggregate_keeps_sums():
    pts = pd.DataFrame({"zone": ["a", "a", "b"], "population": [10, 5, 7], "shops": [0, 2, 1]})
    z = cd.aggregate(pts, ["population", "shops"])
    assert z.loc["a", "population"] == 15 and z["population"].sum() == 22 and z["shops"].sum() == 3


# --- C-DEM-02 attraction -------------------------------------------------------------------------


def test_attraction_is_weighted_share_and_sums_to_one():
    z = pd.DataFrame({t: [1.0, 3.0] for t in P.weights}, index=["a", "b"])
    a = cd.attraction(z, P.weights)
    assert a.sum() == pytest.approx(1.0)
    assert a["b"] == pytest.approx(0.75)


def test_attraction_ignores_empty_type():
    z = pd.DataFrame({t: [1.0, 1.0] for t in P.weights}, index=["a", "b"])
    z["universities"] = 0.0
    a = cd.attraction(z, P.weights)
    assert a.sum() == pytest.approx(1.0 - P.weights["universities"])


# --- C-DEM-04 gravity ----------------------------------------------------------------------------


def test_gravity_row_is_production_constrained_inside_band():
    lo, hi = P.distance_band_km
    d_km = np.array([lo / 2, lo, (lo + hi) / 2, hi, hi * 2])
    a = np.ones(5)
    t = cd.gravity_row(100.0, a, d_km, P.beta_per_km, P.distance_band_km)
    assert t.sum() == pytest.approx(100.0)
    assert t[0] == 0 and t[4] == 0
    assert t[1] > t[2] > t[3] > 0
    assert t[1] / t[2] == pytest.approx(math.exp(P.beta_per_km * (d_km[2] - d_km[1])))


def test_gravity_row_without_destination_in_band_is_zero():
    t = cd.gravity_row(100.0, np.ones(2), np.array([0.1, 99.0]), P.beta_per_km, P.distance_band_km)
    assert t.sum() == 0


# --- C-DEM-05 assignment ---------------------------------------------------------------------------


def test_subtree_sums_accumulate_towards_root():
    # tree 0 <- 1 <- 2, 0 <- 3 ; demand at 2 and 3
    pred = np.array([-9999, 0, 1, 0])
    demand = np.array([0.0, 0.0, 5.0, 2.0])
    assert cd.subtree_sums(pred, demand).tolist() == [7.0, 5.0, 5.0, 2.0]


def _square():
    """Nodes 0..3; short route 0-1-3 (cost 2), long route 0-2-3 (cost 3); all arcs both ways."""
    pairs = [(0, 1, 1.0), (1, 3, 1.0), (0, 2, 1.5), (2, 3, 1.5)]
    tail = [a for a, b, c in pairs] + [b for a, b, c in pairs]
    head = [b for a, b, c in pairs] + [a for a, b, c in pairs]
    cost = [c for a, b, c in pairs] * 2
    return np.array(tail), np.array(head), np.array(cost)


def test_aon_puts_all_flow_on_shortest_path():
    tail, head, cost = _square()
    flows = cd.assign_od(4, tail, head, cost, origins=[0], dest_nodes=np.array([3]), od=lambda i, d: np.array([10.0]))
    on = {(int(t), int(h)): f for t, h, f in zip(tail, head, flows)}
    assert on[(0, 1)] == 10 and on[(1, 3)] == 10 and on[(0, 2)] == 0 and on[(2, 3)] == 0


def test_assignment_picks_cheapest_of_parallel_arcs():
    tail, head, cost = np.array([0, 0]), np.array([1, 1]), np.array([5.0, 2.0])
    flows = cd.assign_od(2, tail, head, cost, origins=[0], dest_nodes=np.array([1]), od=lambda i, d: np.array([3.0]))
    assert flows.tolist() == [0.0, 3.0]


def test_noise_is_reproducible_with_seed():
    a = cd.noise_factors(100, sigma=P.noise_sigma, seed=P.seed, iteration=1)
    b = cd.noise_factors(100, sigma=P.noise_sigma, seed=P.seed, iteration=1)
    c = cd.noise_factors(100, sigma=P.noise_sigma, seed=P.seed, iteration=2)
    assert np.array_equal(a, b) and not np.array_equal(a, c)
    assert (a > 0).all()


def test_aon_iteration_has_no_noise():
    assert np.array_equal(cd.noise_factors(5, sigma=P.noise_sigma, seed=P.seed, iteration=0), np.ones(5))


# --- C-DEM-06 counters and calibration -------------------------------------------------------------


def test_counter_values_use_only_undirected_stations_and_weekdays():
    stations = pd.DataFrame({"thing_id": [1, 2], "richtung": ["Keine Richtung", "Nord nach Süd"]})
    days = pd.date_range("2025-01-06", periods=14, freq="D")  # Monday + 2 weeks
    daily = pd.DataFrame({"thing_id": [1] * 14 + [2] * 14, "date": list(days.date) * 2,
                          "count": [100.0 if d.weekday() < 5 else 10.0 for d in days] * 2})
    daily.loc[0, "count"] = 0.0  # outage day
    v = cd.counter_values(stations, daily, min_valid_weekdays=5)
    assert v.index.tolist() == [1]
    assert v.loc[1, "count_weekday"] == 100.0 and v.loc[1, "n_weekdays"] == 9


def test_counter_values_drop_short_series():
    stations = pd.DataFrame({"thing_id": [1], "richtung": ["Keine Richtung"]})
    daily = pd.DataFrame({"thing_id": [1], "date": [pd.Timestamp("2025-01-06").date()], "count": [5.0]})
    assert cd.counter_values(stations, daily, min_valid_weekdays=2).empty


def test_calibration_factor_is_geometric_mean_of_ratios():
    assert cd.calibration_factor(np.array([200.0, 50.0]), np.array([100.0, 100.0])) == pytest.approx(1.0)
    assert cd.calibration_factor(np.array([300.0, 300.0]), np.array([100.0, 100.0])) == pytest.approx(3.0)


def test_calibration_ignores_zero_model():
    assert cd.calibration_factor(np.array([200.0, 50.0]), np.array([100.0, 0.0])) == pytest.approx(2.0)


def test_fit_stats():
    s = cd.fit_stats(np.array([100.0, 200.0, 400.0]), np.array([110.0, 180.0, 400.0]))
    assert s["mrd"] == pytest.approx((0.1 + 0.1 + 0.0) / 3)
    assert s["spearman"] == pytest.approx(1.0)
    assert -1 <= s["pearson_log"] <= 1


def test_cross_section_sums_parallel_edges_but_not_crossing_street():
    # road along x at y=0, separately mapped tracks at y=+-12, and a street that cuts the transect at
    # (30, 10) only 30 degrees off the transect direction (it must not count)
    edges = gpd.GeoSeries([
        LineString([(-100, 0), (100, 0)]), LineString([(-100, 12), (100, 12)]),
        LineString([(-100, -12), (100, -12)]), LineString([(-5, -50.6), (65, 70.6)])], crs="EPSG:25832")
    rows = cd.cross_section_rows(edges, Point(30, 1), P.transect_half_m, P.counter_snap_m, P.transect_min_angle_deg)
    assert sorted(rows) == [0, 1, 2]


def test_cross_section_without_edge_nearby_is_empty():
    edges = gpd.GeoSeries([LineString([(0, 0), (100, 0)])], crs="EPSG:25832")
    assert cd.cross_section_rows(edges, Point(50, P.counter_snap_m + 5), P.transect_half_m, P.counter_snap_m,
                                 P.transect_min_angle_deg) == []


# --- C-DEM-07 confidence, peak hour ------------------------------------------------------------------


def test_confidence_classes_and_precedence():
    conf = cd.confidence(near_good_counter=np.array([True, False, False, False, True]),
                         near_border=np.array([False, True, False, False, True]),
                         rural=np.array([False, False, False, False, False]),
                         flow=np.array([500.0, 500.0, 500.0, P.low_flow_day - 1, 500.0]),
                         low_flow_day=P.low_flow_day)
    assert conf.tolist() == ["hoch", "niedrig", "mittel", "niedrig", "hoch"]


def test_confidence_missing_flow_is_low():
    conf = cd.confidence(np.array([False]), np.array([False]), np.array([False]), np.array([np.nan]), P.low_flow_day)
    assert conf.tolist() == ["niedrig"]


def test_peak_hour_from_yaml_share():
    share = CYC.demand["peak_hour_share_of_day"]["value"]
    assert cd.peak_hour(np.array([1000.0]), share)[0] == pytest.approx(1000.0 * share)


def test_jobs_floor_area_excludes_and_counts_storeys():
    from shapely.geometry import box
    b = gpd.GeoDataFrame({
        "gebnutzbez": ["Gebaeude"] * 4 + ["Bauteil"],
        "rellage": [None, None, None, "Unter der Erdoberfläche", None],
        "funktion": ["Bürogebäude", "Wohnhaus", next(iter(P.mixed_use_functions)), "Bürogebäude", "Bürogebäude"],
        "anzahlgs": [3, 5, 6, 2, 1]}, geometry=[box(0, 0, 10, 10)] * 5, crs="EPSG:25832")
    a = cd.jobs_floor_area(b, P)
    assert a.tolist() == [300.0, 0.0, 100.0 * P.mixed_use_storeys, 0.0, 0.0]


def test_rapid_transit_stations_group_platforms(tmp_path):
    from pipeline.lib.gtfs import rapid_transit_stations
    (tmp_path / "routes.txt").write_text("route_id,route_type\nu,402\nbus,3\n")
    (tmp_path / "trips.txt").write_text("route_id,trip_id\nu,t1\nbus,t2\n")
    (tmp_path / "stop_times.txt").write_text("trip_id,stop_id\nt1,p1\nt1,p2\nt1,s3\nt2,b1\n")
    (tmp_path / "stops.txt").write_text(
        "stop_id,stop_name,stop_lat,stop_lon,parent_station\n"
        "st1,Station A,53.55,10.0,\np1,A Gleis 1,53.55,10.0,st1\np2,A Gleis 2,53.55,10.0,st1\n"
        "s3,Halt B,53.56,10.01,\nb1,Bus,53.57,10.02,\n")
    st = rapid_transit_stations(tmp_path, P.rapid_transit_route_types)
    assert sorted(st["station_id"]) == ["s3", "st1"]
    assert st.crs.to_epsg() == 25832
