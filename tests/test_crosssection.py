"""Cross-section helpers (pipeline/lib/crosssection.py, rules S-XS-01..06).

Parameters come from config/rules.yaml, so the tests follow a recalibrated rule file.
"""

import math

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import LineString, Point, box

from pipeline.lib.crosssection import (
    XsParams,
    aggregate_widths,
    covered_extent,
    feasibility_class,
    first_hit,
    make_transects,
    near_points,
    required_widths,
)
from pipeline.lib.rules import load_rules

CRS = "EPSG:25832"


@pytest.fixture(scope="module")
def params() -> XsParams:
    return XsParams.from_rules(load_rules())


def _gs(*geoms) -> gpd.GeoSeries:
    return gpd.GeoSeries(list(geoms), crs=CRS)


# --- rules -----------------------------------------------------------------------------------


def test_crosssection_rules_in_rules_yaml():
    rules = load_rules()
    assert [r.id for r in rules.crosssection.rules] == [f"S-XS-{i:02d}" for i in range(1, 8)]  # S-XS-07 since rules.yaml 0.16.0
    assert set(rules.crosssection.rule("S-XS-02").alkis_nutzart) == {"Strassenverkehr", "Weg", "Platz"}


def test_required_widths_use_range_minimum(params):
    rules = load_rules()
    req = required_widths(rules)
    assert req["GOW50"] == rules.required_width["GOW50"].value
    assert req["GOW30_narrow"] == rules.required_width["GOW30_narrow"].range[0]
    assert set(req) == set(rules.crosssection.rule("S-XS-06").targets)


# --- S-XS-01 transects -----------------------------------------------------------------------


def test_transects_on_straight_line(params):
    line = LineString([(0, 0), (100, 0)])
    t = make_transects(_gs(line), params)
    s = params.spacing_m
    assert list(t["position_m"]) == list(np.arange(s / 2, 100, s))
    first = t.iloc[0]
    assert first["centre"].equals(Point(s / 2, 0))
    # Left half points to the left of the direction of travel (+y), each half is half_length_m long.
    assert first["left"].coords[-1] == pytest.approx((s / 2, params.half_length_m))
    assert first["right"].coords[-1] == pytest.approx((s / 2, -params.half_length_m))
    assert (t["seg_pos"] == 0).all()


def test_transects_are_perpendicular_on_diagonal(params):
    line = LineString([(0, 0), (100, 100)])
    t = make_transects(_gs(line), params)
    (x0, y0), (x1, y1) = t.iloc[1]["left"].coords
    assert (x1 - x0) * 1 + (y1 - y0) * 1 == pytest.approx(0, abs=1e-6)


def test_short_line_gets_one_transect(params):
    t = make_transects(_gs(LineString([(0, 0), (params.spacing_m * 0.8, 0)])), params)
    assert len(t) == 1


def test_near_points(params):
    centres = _gs(Point(5, 0), Point(50, 0))
    nodes = _gs(Point(0, 0))
    assert list(near_points(centres, nodes, params.node_exclusion_m)) == [True, False]


# --- S-XS-02 traffic area --------------------------------------------------------------------


def _halves(params):
    t = make_transects(_gs(LineString([(0, 0), (100, 0)])), params)
    return t["left"], t["right"]


def test_covered_extent_merges_adjacent_parcels(params):
    left, right = _halves(params)
    polys = _gs(box(-10, 0, 110, 5), box(-10, -6, 110, 0))  # two parcels sharing the centreline
    dl, end_l, ok_l = covered_extent(left, polys)
    dr, end_r, ok_r = covered_extent(right, polys)
    assert dl[0] == pytest.approx(5) and dr[0] == pytest.approx(6)
    assert not end_l[0] and not end_r[0] and ok_l[0] and ok_r[0]


def test_covered_extent_stops_at_first_gap(params):
    left, _ = _halves(params)
    polys = _gs(box(-10, -1, 110, 4), box(-10, 9, 110, 20))  # gap from 4 to 9
    d, _, _ = covered_extent(left, polys)
    assert d[0] == pytest.approx(4)


def test_covered_extent_open_and_outside(params):
    left, _ = _halves(params)
    d, end, ok = covered_extent(left, _gs(box(-10, -1, 110, 100)))
    assert end[0] and d[0] == pytest.approx(params.half_length_m)
    d, end, ok = covered_extent(left, _gs(box(-10, 2, 110, 10)))  # centre not in traffic area
    assert not ok[0] and math.isnan(d[0])


# --- S-XS-03 facades -------------------------------------------------------------------------


def test_first_hit(params):
    left, right = _halves(params)
    buildings = _gs(box(-10, 8, 110, 20), box(-10, -30, 110, -12))
    dl, in_l = first_hit(left, buildings)
    dr, _ = first_hit(right, buildings)
    assert dl[0] == pytest.approx(8) and dr[0] == pytest.approx(12) and not in_l[0]
    d, _ = first_hit(left, _gs(box(-10, -30, 110, -12)))
    assert math.isnan(d[0])  # nothing within half_length_m on this side
    d, inside = first_hit(left, _gs(box(-10, -2, 110, 3)))
    assert inside[0]


# --- S-XS-05 aggregation ---------------------------------------------------------------------


def test_aggregate_widths_and_narrow_points(params):
    w = [20.0] * 20 + [8.0, 7.0, 7.5] + [20.0] * 10
    df = pd.DataFrame({"seg_pos": 0, "position_m": np.arange(len(w)) * 20.0 + 10, "width": w})
    agg = aggregate_widths(df, params).iloc[0]
    assert agg["width_median_m"] == 20.0 and agg["width_min_m"] == 7.0
    assert agg["width_p10_m"] == pytest.approx(np.quantile(w, params.quantile))
    assert agg["n_valid"] == len(w)
    runs = agg["narrow_points"]
    assert len(runs) == 1 and runs[0]["from_m"] == 410.0 and runs[0]["to_m"] == 450.0


def test_invalid_transect_breaks_narrow_run(params):
    w = [20.0] * 20 + [8.0, np.nan, 7.5, 7.0] + [20.0] * 10
    df = pd.DataFrame({"seg_pos": 0, "position_m": np.arange(len(w)) * 20.0, "width": w})
    agg = aggregate_widths(df, params).iloc[0]
    assert agg["n_valid"] == len(w) - 1
    assert agg["narrow_points"] == []  # 8.0 | gap | 7.5, 7.0: no run of min_run


def test_aggregate_without_valid_transects(params):
    df = pd.DataFrame({"seg_pos": [0, 0], "position_m": [10.0, 30.0], "width": [np.nan, np.nan]})
    agg = aggregate_widths(df, params).iloc[0]
    assert math.isnan(agg["width_p10_m"]) and agg["n_valid"] == 0


# --- S-XS-06 feasibility ---------------------------------------------------------------------


def test_feasibility_class_boundaries():
    classes = load_rules().feasibility_classes
    fits, tight_min = classes["fits"].min, classes["tight"].min
    assert feasibility_class(fits, classes) == "fits"
    assert feasibility_class((fits + tight_min) / 2, classes) == "tight"
    assert feasibility_class(tight_min, classes) == "tight"
    assert feasibility_class(tight_min - 0.01, classes) == "does_not_fit"
    assert feasibility_class(float("nan"), classes) is None


# --- width from neighbours of the same name (S-XS-07, rules.yaml 0.16.0, open question 39) -------------------


def test_fill_width_from_same_name_neighbours():
    import numpy as np
    from pipeline.lib.crosssection import fill_from_neighbours
    df = pd.DataFrame([
        {"name": "A-Straße", "node_u": 1, "node_v": 2, "length_m": 200.0, "w": 14.0},
        {"name": "A-Straße", "node_u": 2, "node_v": 3, "length_m": 15.0, "w": np.nan},   # short junction piece
        {"name": "A-Straße", "node_u": 3, "node_v": 4, "length_m": 12.0, "w": np.nan},   # two hops away
        {"name": "A-Straße", "node_u": 4, "node_v": 5, "length_m": 50.0, "w": 11.0},
        {"name": "B-Weg", "node_u": 2, "node_v": 9, "length_m": 30.0, "w": np.nan},      # other name: stays empty
        {"name": None, "node_u": 3, "node_v": 8, "length_m": 30.0, "w": np.nan},         # no name: stays empty
    ])
    filled, from_nb = fill_from_neighbours(df, "w")
    assert filled.iloc[1] == 14.0                      # longest neighbour with a value
    assert filled.iloc[2] == 11.0                      # direct neighbour with a value wins over two hops
    assert np.isnan(filled.iloc[4]) and np.isnan(filled.iloc[5])
    assert list(from_nb) == [False, True, True, False, False, False]
    assert filled.iloc[0] == 14.0 and filled.iloc[3] == 11.0
