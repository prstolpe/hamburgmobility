"""Unit tests for pipeline/lib/profile.py and the GTFS peak-hour helpers (prompts/19).

Every threshold and width is read from the rule files through ProfileParams; inputs are built just above or below
those values, so no number is copied from the rules.
"""

import json
from pathlib import Path

import geopandas as gpd
import pytest
import shapely

from pipeline import c06_cross_section_soll as c06
from pipeline.lib import gtfs
from pipeline.lib import profile as pf
from pipeline.lib.rules import load_cycling_rules, load_design_rules, load_rules

DESIGN = load_design_rules()
CYCLING = load_cycling_rules()
P = pf.ProfileParams.from_rules(DESIGN, CYCLING, load_rules())
GTFS_DIR = Path(__file__).parent / "fixtures" / "gtfs_min"
# DTV just above / below the L-02 capacity limit for a second lane
DTV_TWO = P.second_lane_dtv * 1.1
DTV_ONE = P.second_lane_dtv * 0.9


def _ids(trace) -> list[str]:
    return [s["id"] for s in trace]


def _seg(**kw) -> pf.SegmentInput:
    base = dict(cat="GOW50", cycle_cat="HAUPT", facility="separated_oneway_both", fallback=None, cycle_width=2.5,
                peak_dir=200, peak_both=400, dtv=DTV_ONE, bus_peak_dir=0, lanes_ist=None, oneway=False,
                parking_sides=0, business=False, tram=False)
    base.update(kw)
    return pf.SegmentInput(**base)


def _elements(res, name):
    return [e for e in res.elements if e["element"] == name]


# --- lanes L-01..L-06 ---------------------------------------------------------------------------------------


@pytest.mark.parametrize("cat", ["GOW30", "ETW30", "ETW_ERF"])
def test_l01_at_most_one_lane(cat):
    r = pf.lanes_soll(cat, DTV_TWO, 0, 3, P)
    assert r.lanes == (1 if cat == "GOW30" else "shared")
    assert "L-01" in _ids(r.trace)


def test_l02_second_lane_only_above_capacity():
    assert pf.lanes_soll("GOW50", DTV_ONE, 0, None, P).lanes == 1
    two = pf.lanes_soll("GOW50", DTV_TWO, 0, None, P)
    assert two.lanes == 2 and two.median and not two.bus_lane
    assert {"L-02", "L-03"} <= set(_ids(two.trace))


def test_l04_bus_lane_instead_of_second_lane():
    r = pf.lanes_soll("GOW50", DTV_TWO, P.bus_lane_trigger, None, P)
    assert r.lanes == 1 and r.bus_lane and not r.median
    below = pf.lanes_soll("GOW50", DTV_TWO, P.bus_lane_trigger - 1, None, P)
    assert below.lanes == 2 and not below.bus_lane


def test_l04_no_bus_lane_without_capacity_need():
    assert not pf.lanes_soll("GOW50", DTV_ONE, P.bus_lane_trigger * 2, None, P).bus_lane


def test_l06_never_more_lanes_than_ist():
    r = pf.lanes_soll("GOW50", DTV_TWO, 0, 1, P)
    assert r.lanes == 1 and "lanes_capped_l06" in r.flags
    bus = pf.lanes_soll("GOW50", DTV_TWO, P.bus_lane_trigger, 1, P)
    assert bus.lanes == 1 and not bus.bus_lane


def test_missing_dtv_takes_ist_and_low_confidence():
    r = pf.lanes_soll("GOW50", None, 0, 3, P)
    assert r.lanes == P.max_lanes and r.low_confidence and "dtv_unknown" in r.flags
    assert pf.lanes_soll("GOW50", None, 0, 1, P).lanes == 1
    assert pf.lanes_soll("GOW50", None, 0, None, P).lanes == P.default_lanes["GOW50"]


def test_sw_has_no_lanes():
    r = pf.lanes_soll("SW", 60000, 0, 3, P)
    assert r.lanes is None and not r.bus_lane


# --- placement and elements -----------------------------------------------------------------------------------


def test_separated_both_sides_with_buffer():
    res = pf.evaluate_profile(_seg(), 100.0, P)
    assert res.cycle_side == "both"
    assert len(_elements(res, "cycle_track")) == 2
    assert len(_elements(res, P.cycle_elements["separated_oneway_both"]["buffer"])) == 2
    assert all(e["width_m"] == pytest.approx(2.5) for e in _elements(res, "cycle_track"))
    assert "PL-01" in _ids(res.trace)


def test_twoway_one_side_flags_pl02():
    res = pf.evaluate_profile(_seg(cat="GOW30", facility="separated_twoway", cycle_width=3.0), 100.0, P)
    assert res.cycle_side == "one" and len(_elements(res, "cycle_track")) == 1
    assert "pl02_unchecked" in res.flags


def test_cycle_lane_buffer_only_next_to_parking():
    no_parking = pf.evaluate_profile(_seg(cat="GOW30", facility="cycle_lane", cycle_width=2.0), 100.0, P)
    assert len(_elements(no_parking, "cycle_lane")) == 2 and not _elements(no_parking, "buffer_to_parking")
    parking = pf.evaluate_profile(_seg(cat="GOW30", facility="cycle_lane", cycle_width=2.0, parking_sides=1), 100.0, P)
    assert len(_elements(parking, "buffer_to_parking")) == 1


@pytest.mark.parametrize("facility", ["mixed", "cycle_street"])
def test_carriageway_facilities_have_no_cycle_element(facility):
    width = P.cycle_street_carriageway if facility == "cycle_street" else None
    res = pf.evaluate_profile(_seg(cat="ETW30", cycle_cat="HAUPT", facility=facility, cycle_width=width), 100.0, P)
    assert res.cycle_side == "carriageway"
    assert not _elements(res, "cycle_track") and not _elements(res, "cycle_lane")


def test_cycle_street_carriageway_is_cycle_width():
    res = pf.evaluate_profile(_seg(cat="ETW30", facility="cycle_street", cycle_width=4.25), 100.0, P)
    assert _elements(res, "carriageway")[0]["width_m"] == pytest.approx(4.25)


def test_optional_elements_ist_based():
    plain = pf.evaluate_profile(_seg(), 100.0, P)
    assert not _elements(plain, "parking_parallel") and not _elements(plain, "loading_zone")
    assert len(_elements(plain, "tree_strip")) == P.tree_sides
    rich = pf.evaluate_profile(_seg(parking_sides=2, business=True), 100.0, P)
    assert len(_elements(rich, "parking_parallel")) == 2
    assert len(_elements(rich, "loading_zone")) == P.loading_sides
    etw = pf.evaluate_profile(_seg(cat="ETW30", facility="mixed", cycle_width=None), 100.0, P)
    assert not _elements(etw, "tree_strip")


def test_etw_erf_has_no_sidewalks():
    res = pf.evaluate_profile(_seg(cat="ETW_ERF", facility="mixed", cycle_width=None), 100.0, P)
    assert not _elements(res, "sidewalk") and _elements(res, "shared_surface")


def test_bus_lane_and_median_elements():
    bus = pf.evaluate_profile(_seg(dtv=DTV_TWO, bus_peak_dir=P.bus_lane_trigger), 100.0, P)
    assert len(_elements(bus, "bus_lane")) == 2 and bus.bus_lane
    two = pf.evaluate_profile(_seg(dtv=DTV_TWO), 100.0, P)
    assert len(_elements(two, "median")) == 1 and len(_elements(two, "carriageway")) == 2


def test_profile_elements_order_and_total():
    res = pf.evaluate_profile(_seg(parking_sides=2), 100.0, P)
    assert [e["order"] for e in res.elements] == list(range(1, len(res.elements) + 1))
    assert res.total_required_m == pytest.approx(sum(e["width_m"] for e in res.elements))
    sides = [e["side"] for e in res.elements]
    assert sides[0] == "left" and sides[-1] == "right"
    assert res.elements[0]["element"] == "sidewalk"
    json.dumps(res.elements)


def test_oneway_has_one_direction_of_lanes():
    two = pf.evaluate_profile(_seg(cat="GOW30", facility="cycle_lane", cycle_width=2.0), 100.0, P)
    one = pf.evaluate_profile(_seg(cat="GOW30", facility="cycle_lane", cycle_width=2.0, oneway=True), 100.0, P)
    cw = lambda r: sum(e["width_m"] for e in _elements(r, "carriageway"))
    assert cw(one) < cw(two)


def test_no_profile_rules_for_sw():
    res = pf.evaluate_profile(_seg(cat="SW", facility="own_path", cycle_width=None), 100.0, P)
    assert res.fit_class is None and "no_profile_rules" in res.flags and res.elements == []


# --- fit and cascade -------------------------------------------------------------------------------------


def test_fits_without_degrade():
    seg = _seg()
    full = pf.evaluate_profile(seg, 100.0, P)
    res = pf.evaluate_profile(seg, full.total_required_m, P)
    assert res.fit_class == "fits" and res.degrade_steps_applied == []


def test_width_unknown():
    res = pf.evaluate_profile(_seg(), None, P)
    assert res.fit_class is None and "width_unknown" in res.flags and res.elements


def test_d1_removes_parking_first():
    seg = _seg(parking_sides=2)
    full = pf.evaluate_profile(seg, 100.0, P).total_required_m
    res = pf.evaluate_profile(seg, full - 0.1, P)
    assert res.fit_class == "fits_after_degrade" and res.degrade_steps_applied == ["D1"]
    assert not _elements(res, "parking_parallel")


def test_d1_skipped_without_parking_then_d2_trees():
    seg = _seg()
    full = pf.evaluate_profile(seg, 100.0, P).total_required_m
    res = pf.evaluate_profile(seg, full - 0.1, P)
    assert res.degrade_steps_applied == ["D2"]
    assert all(e["width_m"] == 0 for e in _elements(res, "tree_strip")) or not _elements(res, "tree_strip")
    assert "trees_in_parking_row" in res.flags


def test_loading_zone_kept_by_d1():
    seg = _seg(parking_sides=2, business=True)
    full = pf.evaluate_profile(seg, 100.0, P).total_required_m
    res = pf.evaluate_profile(seg, full - 0.1, P)
    assert _elements(res, "loading_zone")


def test_fallback_after_d2_before_d3():
    seg = _seg(cat="GOW30", facility="separated_oneway_both", fallback="cycle_lane", cycle_width=2.5)
    full = pf.evaluate_profile(seg, 100.0, P)
    trees = sum(e["width_m"] for e in _elements(full, "tree_strip"))
    res = pf.evaluate_profile(seg, full.total_required_m - trees - 0.1, P)
    assert res.degrade_steps_applied == ["D2", "fallback"]
    assert res.cycle_facility == "cycle_lane" and res.fit_class == "fits_after_degrade"
    assert res.cycle_width_m == pytest.approx(pf.facility_width("cycle_lane", seg, P))


def test_d3_drops_second_lane_keeps_bus_lane():
    seg = _seg(dtv=DTV_TWO)
    full = pf.evaluate_profile(seg, 100.0, P)
    no_trees = full.total_required_m - sum(e["width_m"] for e in _elements(full, "tree_strip"))
    res = pf.evaluate_profile(seg, no_trees - 0.1, P)
    assert res.degrade_steps_applied == ["D2", "D3"]
    assert res.lanes == 1 and not res.median
    bus = _seg(dtv=DTV_TWO, bus_peak_dir=P.bus_lane_trigger)
    tight = pf.evaluate_profile(bus, 1.0, P, stop_before="D5")
    assert tight.bus_lane and "D3" not in tight.degrade_steps_applied


def test_d4_minimum_widths():
    seg = _seg(cycle_width=3.0)
    full = pf.evaluate_profile(seg, 100.0, P)
    trees = sum(e["width_m"] for e in _elements(full, "tree_strip"))
    res = pf.evaluate_profile(seg, full.total_required_m - trees - 0.1, P)
    assert res.degrade_steps_applied == ["D2", "D4"]
    assert all(e["width_m"] == pytest.approx(P.sidewalk_min) for e in _elements(res, "sidewalk"))
    assert res.cycle_width_m == pytest.approx(P.floor["separated_oneway_both"])


def test_d5_proposes_gow30_without_applying():
    seg = _seg(cycle_cat="BASIS", cycle_width=2.0, dtv=P.gow30_narrow[1])
    assert pf.evaluate_profile(seg, 100.0, P).cat_change_proposal is None
    d4 = pf.evaluate_profile(seg, 1.0, P, stop_before="D5")
    assert d4.degrade_steps_applied[-1] == "D4"
    res = pf.evaluate_profile(seg, d4.total_required_m - 0.05, P)
    assert res.degrade_steps_applied[-1] == "D5" and res.fit_class == "fits_after_degrade"
    assert res.cat_change_proposal == "GOW30"
    assert any(s["id"] == "D5" and s["values"]["rule"] == "C-G30-02" for s in res.trace)
    # GOW30 itself never gets a proposal
    gow30 = pf.evaluate_profile(_seg(cat="GOW30", cycle_cat="BASIS", facility="cycle_lane", cycle_width=2.0), 1.0, P)
    assert gow30.cat_change_proposal is None and "D5" not in gow30.degrade_steps_applied


def test_d6_d7_flags_only():
    res = pf.evaluate_profile(_seg(), 1.0, P)
    assert res.fit_class == "does_not_fit"
    assert {"D6", "D7"} <= set(res.degrade_steps_applied)
    assert {"D6", "D7"} <= set(res.flags)
    off_network = pf.evaluate_profile(_seg(cycle_cat="none"), 1.0, P)
    assert "D7" not in off_network.degrade_steps_applied
    mixed = pf.evaluate_profile(_seg(cat="ETW30", facility="mixed", cycle_width=None), 1.0, P)
    assert "D6" in mixed.degrade_steps_applied and "D7" not in mixed.degrade_steps_applied


def test_every_applied_step_in_trace():
    res = pf.evaluate_profile(_seg(parking_sides=2, dtv=DTV_TWO), 1.0, P)
    traced = [s["id"] for s in res.trace if s.get("applied")]
    assert traced == res.degrade_steps_applied
    assert "PRF-05" in _ids(res.trace) and "PRF-06" in _ids(res.trace)


def test_facade_variant_has_more_room():
    seg = _seg(parking_sides=2)
    full = pf.evaluate_profile(seg, 100.0, P).total_required_m
    traffic = pf.evaluate_profile(seg, full - 1, P)
    facade = pf.evaluate_profile(seg, full + 1, P)
    assert traffic.fit_class == "fits_after_degrade" and facade.fit_class == "fits"


# --- SVG -------------------------------------------------------------------------------------------------


def test_profile_svg_scaled_and_labelled():
    res = pf.evaluate_profile(_seg(parking_sides=2), 30.0, P)
    svg = pf.profile_svg(res.elements, 30.0, "Teststraße", "GOW50 · HAUPT")
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    assert "Teststraße" in svg and "Gehweg" in svg and "Radweg" in svg
    assert svg.count("<rect") >= len([e for e in res.elements if e["width_m"] > 0])
    widths = [float(x) for x in __import__("re").findall(r'data-width-m="([0-9.]+)"', svg)]
    assert widths == pytest.approx([e["width_m"] for e in res.elements if e["width_m"] > 0])


# --- GTFS peak hour per direction ------------------------------------------------------------------------


def test_trip_start_hours():
    hours = gtfs.trip_start_hours(GTFS_DIR)
    assert hours.to_dict() == {"t1": 7, "t2": 7, "t3": 8, "t4": 7}


def test_hourly_trips_per_shape():
    feed = gtfs.load_feed(GTFS_DIR)
    day = gtfs.representative_weekday(feed)
    hist = gtfs.hourly_trips_per_shape(feed, gtfs.trip_start_hours(GTFS_DIR), day, (3, 700))
    assert hist.loc["s1", 7] == 2 and hist.loc["s1", 8] == 1
    assert hist.loc["s1"].max() == 2


def test_shape_direction():
    shape = shapely.LineString([(0, 0), (100, 0)])
    segs = gpd.GeoSeries([shapely.LineString([(10, 1), (50, 1)]), shapely.LineString([(60, -1), (20, -1)])])
    assert list(gtfs.shape_direction(segs, shape)) == [1, -1]


# --- bus matching: parallel and cache (pipeline/lib/parallel.py) -------------------------------------------


def _bus_inputs():
    from shapely.geometry import LineString
    from pipeline.lib.conflate import MatchParams
    segs = gpd.GeoSeries([LineString([(0, 0), (100, 0)]), LineString([(100, 0), (200, 0)]),
                          LineString([(0, 50), (0, 150)])], crs="EPSG:25832")
    shapes = [LineString([(-10, 1), (210, 1)]), LineString([(210, -1), (-10, -1)]), LineString([(1, 40), (1, 160)])]
    return segs, shapes, MatchParams(buffer_m=15, max_angle_deg=20, min_overlap_share=0.6)


def test_match_shapes_parallel_equals_serial(monkeypatch):
    segs, shapes, mp_ = _bus_inputs()
    monkeypatch.setenv("SFP_WORKERS", "1")
    ser = c06.match_shapes(segs, shapes, mp_, 0.5)
    monkeypatch.setenv("SFP_WORKERS", "3")
    par = c06.match_shapes(segs, shapes, mp_, 0.5)
    assert [(list(h), list(d)) for h, d in ser] == [(list(h), list(d)) for h, d in par]
    assert list(ser[0][0]) == [0, 1] and list(ser[0][1]) == [1, 1]     # with the segments
    assert list(ser[1][0]) == [0, 1] and list(ser[1][1]) == [-1, -1]   # against them
    assert list(ser[2][0]) == [2]


def test_transit_cache_key_changes_with_inputs():
    segs, _, mp_ = _bus_inputs()
    base = c06.transit_cache_key("feed.zip", 123, (3,), mp_, 0.5, segs)
    assert base == c06.transit_cache_key("feed.zip", 123, (3,), mp_, 0.5, segs)
    assert base != c06.transit_cache_key("feed.zip", 124, (3,), mp_, 0.5, segs)
    assert base != c06.transit_cache_key("feed.zip", 123, (3, 700), mp_, 0.5, segs)
    assert base != c06.transit_cache_key("feed.zip", 123, (3,), mp_, 0.6, segs)
    assert base != c06.transit_cache_key("feed.zip", 123, (3,), mp_, 0.5, segs.iloc[:2])


# --- lane overrides (overrides/lane_overrides.csv, design_rules.yaml 0.6.0, open question 129) ----------------


def _lovr(**kw):
    import pandas as pd
    from pipeline.lib import overrides as ov
    row = {"segment_id": "seg_a", "lanes_per_dir_final": "2", "bus_lane_final": "true", "reason": "Ortstermin",
           "author": "x", "date": "2026-11-07", "source": "", "review_status": "approved", **kw}
    return pd.DataFrame([row], columns=ov.LANE_COLUMNS)


def test_lane_override_replaces_lane_rules():
    r = pf.lanes_soll("GOW50", DTV_ONE, 0, 1, P, override=(2, True))
    assert r.lanes == 2 and r.bus_lane and r.median
    assert "L-OVR" in _ids(r.trace) and "L-06" not in _ids(r.trace)  # the expert decision is not capped
    shared = pf.lanes_soll("GOW50", DTV_TWO, 0, 2, P, override=("shared", False))
    assert shared.lanes == "shared" and not shared.median


def test_lane_override_validation_and_apply():
    import pytest as _pt
    from pipeline.lib import overrides as ov
    approved = ov.lane_overrides(_lovr(), ["seg_a", "seg_b"], P.max_lanes)
    assert approved == {"seg_a": (2, True)}
    assert ov.lane_overrides(_lovr(review_status="draft"), ["seg_a"], P.max_lanes) == {}
    for kw, match in (({"segment_id": "seg_x"}, "verwaist"), ({"lanes_per_dir_final": "4"}, "lanes_per_dir_final"),
                      ({"bus_lane_final": "vielleicht"}, "bus_lane_final"), ({"reason": ""}, "Begründung fehlt")):
        with _pt.raises(ov.OverrideError, match=match):
            ov.lane_overrides(_lovr(**kw), ["seg_a"], P.max_lanes)


def test_lane_override_file_has_header():
    from pipeline.lib import overrides as ov
    assert list(ov.read_overrides(ov.LANE_OVERRIDES_PATH).columns) == ov.LANE_COLUMNS
