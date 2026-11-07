"""Unit tests for pipeline/lib/facility.py (prompts/18): Soll facility, width, Ist class, gap, confidence.

Every threshold is read from config/cycling_rules.yaml through FacilityParams; the tests build inputs just above
or below those values, so no number is copied from the rules.
"""

import dataclasses
import math

import pytest

from pipeline.lib import facility as fa
from pipeline.lib.rules import load_cycling_rules

CYC = load_cycling_rules()
P = fa.FacilityParams.from_rules(CYC)
TARGET = CYC.widths_m["project_target"]


def _ids(trace: list[dict]) -> set[str]:
    return {step["id"] for step in trace}


# --- C-FAC-01 matrix --------------------------------------------------------------------------------------


def test_matrix_preferred_and_pending_fallback():
    r = fa.soll_facility("GOW30", "HAUPT", dtv=5000, cyc_peak_both=200, space_fits_preferred=None, p=P)
    assert r.facility == "separated_oneway_both"
    assert r.fallback == "cycle_lane"
    assert "fallback_check_p19" in r.flags


def test_matrix_fallback_when_space_does_not_fit():
    r = fa.soll_facility("GOW30", "HAUPT", dtv=5000, cyc_peak_both=200, space_fits_preferred=False, p=P)
    assert r.facility == "cycle_lane"
    assert "fallback_check_p19" not in r.flags


def test_no_flag_without_fallback():
    r = fa.soll_facility("GOW50", "BASIS", dtv=20000, cyc_peak_both=100, space_fits_preferred=None, p=P)
    assert r.facility == "separated_oneway_both" and r.fallback is None and not r.flags


def test_sw_and_missing_category():
    assert fa.soll_facility("SW", "none", None, 0, None, P).facility == "own_path"
    r = fa.soll_facility(None, "HAUPT", None, 0, None, P)
    assert r.facility is None


def test_rural_etw60_fallback_needs_low_dtv():
    lim = P.rural_mixed_max_dtv
    assert fa.soll_facility("ETW60", "BASIS", lim, 10, False, P).facility == "mixed"
    assert fa.soll_facility("ETW60", "BASIS", lim + 1, 10, False, P).facility == "separated_twoway"
    unknown = fa.soll_facility("ETW60", "BASIS", None, 10, False, P)
    assert unknown.facility == "mixed" and "dtv_unknown" in unknown.flags


def test_highest_category():
    assert fa.highest_category(["ERSCHL", "HAUPT", None], P) == "HAUPT"
    assert fa.highest_category([], P) == "none"


# --- C-FAC-02 cycle street, C-FAC-03 S-04 -------------------------------------------------------------


def test_cycle_street_met():
    dtv = P.cs_max_dtv
    r = fa.soll_facility("ETW30", "HAUPT", dtv, cyc_peak_both=dtv * P.motor_peak_share, space_fits_preferred=True, p=P)
    assert r.facility == "cycle_street" and not r.flags
    assert "C-FAC-02" in _ids(r.trace)


def test_cycle_street_too_many_motor_vehicles():
    r = fa.soll_facility("ETW30", "RSV", P.cs_max_dtv + 1, cyc_peak_both=1e6, space_fits_preferred=True, p=P)
    assert r.facility == "mixed" and "cycle_street_blocked" in r.flags


def test_cycle_street_cyclists_not_dominant():
    dtv = P.cs_max_dtv / 2
    r = fa.soll_facility("ETW30", "HAUPT", dtv, cyc_peak_both=dtv * P.motor_peak_share - 1, space_fits_preferred=True, p=P)
    assert r.facility == "mixed" and "cycle_street_blocked" in r.flags


def test_cycle_street_dtv_unknown_counts_as_met():
    r = fa.soll_facility("ETW30", "HAUPT", None, cyc_peak_both=0, space_fits_preferred=True, p=P)
    assert r.facility == "cycle_street"
    assert "dtv_unknown" in r.flags and "cycle_street_blocked" not in r.flags


def test_s04_flag_on_mixed():
    over = (P.s04_max_kfz_h + 1) / P.motor_peak_share
    r = fa.soll_facility("ETW30", "BASIS", over, cyc_peak_both=10, space_fits_preferred=True, p=P)
    assert r.facility == "mixed" and "mixed_over_s04" in r.flags
    ok = fa.soll_facility("ETW30", "BASIS", P.s04_max_kfz_h / P.motor_peak_share, 10, True, P)
    assert "mixed_over_s04" not in ok.flags
    assert "S-04" in _ids(ok.trace)


def test_s04_dtv_unknown():
    r = fa.soll_facility("ETW30", "ERSCHL", None, 10, True, P)
    assert r.facility == "mixed" and "dtv_unknown" in r.flags and "mixed_over_s04" not in r.flags


# --- C-FAC-04 width ---------------------------------------------------------------------------------------


def test_width_target_and_upgrade():
    w = fa.target_width("separated_oneway_both", "HAUPT", peak_dir=0, peak_both=0, p=P)
    assert w.width == pytest.approx(TARGET["separated_oneway"]["HAUPT"])
    kind, thr, add = next(u for u in P.intensity_upgrade if u[0] == "oneway")
    up = fa.target_width("separated_oneway_both", "HAUPT", peak_dir=thr + 1, peak_both=0, p=P)
    assert up.width == pytest.approx(TARGET["separated_oneway"]["HAUPT"] + add)


def test_width_comparison_values():
    w = fa.target_width("separated_oneway_both", "BASIS", 0, 0, P)
    assert w.de == pytest.approx(CYC.widths_m["de"]["separated_oneway"]["standard"])
    assert w.nl == pytest.approx(CYC.widths_m["nl"]["hoofdnet_oneway"]["standard"])


def test_width_never_below_floor():
    low = fa.FacilityParams.from_rules(CYC)
    target = {**low.project_target, "separated_oneway": {**low.project_target["separated_oneway"], "BASIS": 0.5}}
    low = dataclasses.replace(low, project_target=target)
    w = fa.target_width("separated_oneway_both", "BASIS", 0, 0, low)
    assert w.width == pytest.approx(CYC.widths_m["de"]["separated_oneway"]["min"])


def test_no_width_for_mixed():
    for f in ("mixed", None):
        w = fa.target_width(f, "HAUPT", 0, 0, P)
        assert w.width is None


def test_own_path_width_as_twoway_path():
    # cycling_rules.yaml 0.7.0 (open question 108): own paths get the two-way cycle path widths
    for cat in ("RSV", "HAUPT", "BASIS", "ERSCHL"):
        assert fa.target_width("own_path", cat, 0, 0, P).width == pytest.approx(TARGET["separated_twoway"][cat])


# --- C-FAC-05 Ist -----------------------------------------------------------------------------------------


@pytest.mark.parametrize("kwargs, expected", [
    ({"fahrradstrasse": True}, "cycle_street"),
    ({"bicycle_road": True, "cycleway_values": {"track"}}, "cycle_street"),
    ({"cycleway_values": {"no", "track"}}, "track"),
    ({"cycleway_values": {"separate"}}, "track"),
    ({"has_sidepath": True}, "track"),
    ({"track_present": True, "lane_present": True}, "track"),
    ({"lane_present": True}, "lane"),
    ({"cycleway_values": {"lane"}}, "lane"),
    ({"cycleway_values": {"share_busway"}}, "shared_lane"),
    ({"cycleway_values": {"no"}}, "no"),
    ({}, "no"),
])
def test_ist_class(kwargs, expected):
    assert fa.ist_class(p=P, **kwargs) == expected


def test_ist_facility_mapping():
    assert fa.ist_facility("track", sidepath_twoway=False, p=P) == "separated_oneway_both"
    assert fa.ist_facility("track", sidepath_twoway=True, p=P) == "separated_twoway"
    assert fa.ist_facility("no", sidepath_twoway=False, p=P) == "mixed"
    assert fa.ist_facility("track", sidepath_twoway=True, p=P, sidepath_both_sides=True) == "separated_oneway_both"


def test_sidepath_side():
    import shapely

    road = shapely.LineString([(0, 0), (100, 0)])
    left = shapely.LineString([(10, 5), (90, 5)])
    right = shapely.LineString([(10, -5), (90, -5)])
    assert list(fa.sidepath_side([road, road], [left, right])) == [1, -1]


# --- C-FAC-06 gap, C-FAC-07 confidence --------------------------------------------------------------------


def test_gap_missing():
    g = fa.facility_gap("separated_oneway_both", None, "no", "mixed", math.nan, 2.0, P)
    assert g == ("missing", False)


def test_gap_missing_cycle_street_is_partial():
    assert fa.facility_gap("cycle_street", None, "no", "mixed", math.nan, 4.0, P) == ("missing", True)


def test_gap_wrong_type_and_fallback():
    assert fa.facility_gap("separated_oneway_both", None, "lane", "cycle_lane", 2.0, 2.0, P) == ("wrong_type", False)
    # Ist = fallback of the matrix cell is a partial fulfilment (C-FAC-06 stage partial)
    assert fa.facility_gap("separated_oneway_both", "cycle_lane", "lane", "cycle_lane", 2.0, 2.0, P) == ("partial", True)


def test_gap_partial_track_instead_of_cycle_street():
    # cycling_rules.yaml 0.6.0: a cycle track on an ETW30 main route partly meets the cycle street (open question 125)
    for ist in ("separated_oneway_both", "separated_twoway"):
        assert ist in P.partial["cycle_street"]
        assert fa.facility_gap("cycle_street", None, "track", ist, 2.0, 4.0, P) == ("partial", True)


def test_gap_partial_twoway_instead_of_oneway():
    assert fa.facility_gap("separated_oneway_both", None, "track", "separated_twoway", 3.0, 2.0, P) == ("partial", True)


def test_category_check_flag_only_for_track_on_access_road_cycle_street():
    cats = sorted(P.category_check["cat_final"])
    assert fa.category_check(cats[0], "cycle_street", "track", P)
    assert not fa.category_check(cats[0], "cycle_street", "no", P)
    assert not fa.category_check(cats[0], "mixed", "track", P)
    assert not fa.category_check("GOW50", "cycle_street", "track", P)
    assert not fa.category_check(None, "cycle_street", "track", P)


def test_gap_too_narrow_and_none():
    assert fa.facility_gap("separated_oneway_both", None, "track", "separated_oneway_both", 1.5, 2.0, P) == ("too_narrow", False)
    assert fa.facility_gap("separated_oneway_both", None, "track", "separated_oneway_both", 2.0, 2.0, P) == ("none", False)
    assert fa.facility_gap("separated_oneway_both", None, "track", "separated_oneway_both", math.nan, 2.0, P) == ("none", False)
    assert fa.facility_gap("mixed", None, "no", "mixed", math.nan, None, P) == ("none", False)


def test_gap_not_assessed():
    assert fa.facility_gap("own_path", None, "no", "mixed", math.nan, None, P)[0] == "not_assessed"
    assert fa.facility_gap(None, None, "no", "mixed", math.nan, None, P)[0] == "not_assessed"


def test_confidence():
    assert fa.confidence("GOW50", [], P) == "high"
    assert fa.confidence("ETW30", ["dtv_unknown"], P) == "medium"
    assert fa.confidence(None, [], P) == "low"


def test_pandas_na_counts_as_missing():
    import pandas as pd

    r = fa.soll_facility("ETW30", "HAUPT", pd.NA, pd.NA, None, P)
    assert r.facility == "cycle_street" and "dtv_unknown" in r.flags
