"""Junction logic of pipeline/lib/junctions.py and pipeline/c07_junctions.py (prompts/20_junctions.md).

Values are taken from design_rules.yaml, so the tests do not copy thresholds.
"""

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import LineString, Point, box

from pipeline import c07_junctions as c07
from pipeline.lib import junctions as jn
from pipeline.lib import overrides as ov
from pipeline.lib.rules import load_design_rules, load_rules

DESIGN = load_design_rules()
P = jn.JunctionParams.from_rules(DESIGN, load_rules())
T = P.thresholds


def leg(cat, cycle_cat="none", facility=None, **kw):
    return {"cat": cat, "cycle_cat": cycle_cat, "facility": facility, **kw}


def props(legs, **kw):
    base = {"legs": legs, "entering_dtv_sum": 1000.0, "space_radius_m": T["roundabout_min_radius"] + 5,
            "tram_present": False, "signal_present_ist": False}
    return {**base, **kw}


# --- category pair (J-M-04) ------------------------------------------------------------------------------------


def test_side_street_on_main_road_is_not_a_main_road_pair():
    pair, _ = jn.category_pair([leg("GOW50"), leg("GOW50"), leg("ETW30")], P)
    assert pair == ("GOW50", "ETW30")


def test_four_arm_crossing_of_two_main_roads():
    pair, _ = jn.category_pair([leg("GOW50")] * 4, P)
    assert pair == ("GOW50", "GOW50")


def test_cycle_path_is_second_road_only_without_other_street():
    assert jn.category_pair([leg("GOW30"), leg("GOW30"), leg("cycle_path")], P)[0] == ("GOW30", "cycle_path")
    pair, flags = jn.category_pair([leg("GOW30"), leg("GOW30"), leg("ETW30"), leg("cycle_path")], P)
    assert pair == ("GOW30", "ETW30") and "cycle_path_ignored" in flags


def test_alias_maps_etw_erf():
    pair, flags = jn.category_pair([leg("ETW30"), leg("ETW30"), leg("ETW_ERF")], P)
    assert pair == ("ETW30", "ETW30") and "category_alias" in flags


# --- decision table ----------------------------------------------------------------------------------------------


def test_main_road_pair_unknown_dtv_takes_roundabout_with_low_confidence():
    r = jn.decide(props([leg("GOW50"), leg("GOW50")], entering_dtv_sum=None), P)
    assert r["junction_type_soll"] == "roundabout_single_lane_cycle_priority"
    assert "condition_unknown" in r["conflict_flags"] and r["confidence"] == "low"


def test_missing_space_with_low_dtv_is_unknown_not_signal():
    r = jn.decide(props([leg("GOW50"), leg("GOW50")], space_radius_m=None), P)
    assert r["confidence"] == "low"


def test_gow30_roundabout_falls_back_without_space():
    small = T["roundabout_min_radius"] - 1
    r = jn.decide(props([leg("GOW30"), leg("GOW30")], space_radius_m=small), P)
    assert r["junction_type_soll"] == "priority_flat_coloured"


def test_gow30_roundabout_above_capacity_is_flagged():
    r = jn.decide(props([leg("GOW30"), leg("GOW30")], entering_dtv_sum=T["roundabout_max_dtv"] + 1), P)
    assert r["junction_type_soll"] == "roundabout_single_lane_cycle_priority"
    assert "dtv_above_roundabout_max" in r["conflict_flags"]


def test_cycle_path_basis_across_gow50_has_no_row():
    r = jn.decide(props([leg("GOW50"), leg("GOW50"), leg("cycle_path", "BASIS", "own_path")]), P)
    assert r["junction_type_soll"] is None and "no_rule" in r["conflict_flags"]


def test_sw_before_everything():
    r = jn.decide(props([leg("SW"), leg("SW"), leg("GOW50", "HAUPT")], tram_present=True), P)
    assert r["junction_type_soll"] == "grade_separated_cycle" and r["rule_id"] == "J-10"


def test_cycle_street_needs_cycle_street_facility():
    plain = jn.decide(props([leg("ETW30", "HAUPT", "mixed"), leg("ETW30")]), P)
    street = jn.decide(props([leg("ETW30", "HAUPT", "cycle_street"), leg("ETW30")]), P)
    assert plain["junction_type_soll"] == "equal_right_before_left"
    assert street["junction_type_soll"] == "priority_raised"


def test_trace_lists_rows_checked_before_the_match():
    r = jn.decide(props([leg("ETW30"), leg("ETW30")]), P)
    ids = [s["id"] for s in r["rule_trace_junction"]]
    assert ids[0] == "J-M-04" and ids[-1] == "J-06"
    assert all(not s["passed"] for s in r["rule_trace_junction"][1:-1])


# --- treatment, Ist, DTV, arms -------------------------------------------------------------------------------------


def test_jc04_only_when_route_crosses_the_main_road():
    along = [leg("GOW30", "HAUPT"), leg("GOW30", "HAUPT"), leg("ETW30")]
    across = [leg("GOW30"), leg("GOW30"), leg("ETW30", "HAUPT")]
    pair = ("GOW30", "ETW30")
    assert "JC-04" not in jn.treatments("continuous_footway_exit", pair, along, P)
    assert "JC-04" in jn.treatments("continuous_footway_exit", pair, across, P)


def test_jc01_text_names_the_conflict():
    text = jn.treatment_text(["JC-01"])
    assert "SWOV" in text and "StVO" in text


@pytest.mark.parametrize("soll, ist, expected", [
    ("signal_protected", "signal", "match"),
    ("signal_protected", "none_mapped", "mismatch"),
    ("continuous_footway_exit", "none_mapped", "not_checkable"),
    ("equal_right_before_left", "signal", "mismatch"),
    ("grade_separated_cycle", "none_mapped", "mismatch"),
])
def test_ist_result(soll, ist, expected):
    assert jn.ist_result(soll, ist, P) == expected


def test_ist_type_precedence():
    assert jn.ist_type(True, True, True) == "roundabout"
    assert jn.ist_type(False, True, True) == "signal_plateau"
    assert jn.ist_type(False, False, False) == "none_mapped"


def test_entering_dtv_lower_bound_and_unknown():
    zero = {"ETW30", "ETW_ERF", "ETW60"}
    assert jn.entering_dtv([leg("GOW50", dtv=20000), leg("ETW30", dtv=None)], 0.5, zero) == (10000.0, [])
    assert jn.entering_dtv([leg("GOW50", dtv=20000), leg("GOW30", dtv=None)], 0.5, zero) == (10000.0, ["dtv_partial"])
    assert jn.entering_dtv([leg("GOW50", dtv=None), leg("ETW30", dtv=500)], 0.5, zero) == (None, ["dtv_unknown"])


def test_dual_carriageway_legs_merge_into_one_arm():
    legs = [leg("GOW50", id="a", name="X", dtv=50000, bearing=10), leg("GOW50", id="b", name="X", dtv=50000, bearing=350),
            leg("GOW50", id="c", name="X", dtv=50000, bearing=180), leg("ETW30", "HAUPT", id="d", name="Y", dtv=None, bearing=90)]
    arms = jn.merge_arms(legs, DESIGN.junctions.method_rule("J-M-02")["arm_merge_angle_deg"]["value"])
    assert [a["ids"] for a in arms] == [["a", "b"], ["c"], ["d"]]


# --- c07 building blocks -------------------------------------------------------------------------------------------


def _seg(rows):
    return pd.DataFrame(rows, columns=["segment_id", "node_u", "node_v", "length_m"])


def test_clusters_join_short_links_and_roundabouts():
    seg = _seg([("s1", 1, 2, 10.0), ("s2", 1, 3, 100), ("s3", 1, 4, 100), ("s4", 2, 5, 100), ("s5", 2, 6, 100),
                ("r1", 7, 8, 40), ("r2", 8, 9, 40), ("r3", 9, 7, 40), ("a", 7, 10, 100), ("b", 8, 11, 100), ("c", 9, 12, 100)])
    paths = pd.DataFrame({"node_u": [], "node_v": []})
    cl = c07.build_clusters(seg, paths, {"r1", "r2", "r3"}, radius=25)
    assert cl == {1: [1, 2], 7: [7, 8, 9]}


def test_cycle_path_touching_a_street_is_a_junction():
    seg = _seg([("s1", 1, 2, 100), ("s2", 2, 3, 100)])
    paths = pd.DataFrame({"node_u": [2], "node_v": [99]})
    assert c07.build_clusters(seg, paths, set(), radius=25) == {2: [2]}


def test_space_radius_fills_enclosed_islands():
    ring = box(-30, -30, 30, 30).difference(Point(0, 0).buffer(12))
    r = c07.space_radius(gpd.GeoSeries([Point(0, 20)]), gpd.GeoSeries([ring]).to_numpy(), 100, 0.5)
    assert r[0] == pytest.approx(30, abs=1)


def test_space_radius_unknown_without_traffic_area():
    r = c07.space_radius(gpd.GeoSeries([Point(0, 0)]), gpd.GeoSeries([box(500, 500, 510, 510)]).to_numpy(), 40, 0.5)
    assert pd.isna(r[0])


def test_bearing_points_away_from_centre():
    assert c07._bearing((0, 0), LineString([(0, 0), (0, 100)]), True, 40) == pytest.approx(0)
    assert c07._bearing((0, 0), LineString([(100, 0), (0, 0)]), False, 40) == pytest.approx(90)


# --- overrides -----------------------------------------------------------------------------------------------------


def _ovr(**kw):
    row = {"node_id": "123", "junction_type_final": "signal_protected", "reason": "Ortstermin", "author": "x",
           "date": "2026-11-06", "source": "", "review_status": "approved", **kw}
    return pd.DataFrame([row], columns=ov.JUNCTION_COLUMNS)


def test_junction_override_applies_only_approved():
    j = pd.DataFrame({"node_id": ["123", "456"], "junction_type_soll": ["equal_right_before_left"] * 2})
    out = ov.apply_junctions(j, _ovr())
    assert list(out["junction_type_final"]) == ["signal_protected", "equal_right_before_left"]
    assert list(out["junction_type_source"]) == ["override", "proposed"]
    draft = ov.apply_junctions(j, _ovr(review_status="draft"))
    assert list(draft["junction_type_final"]) == ["equal_right_before_left"] * 2


@pytest.mark.parametrize("kw, match", [
    ({"node_id": "999"}, "verwaist"),
    ({"junction_type_final": "magic"}, "ungültiger Knotentyp"),
    ({"reason": ""}, "Begründung fehlt"),
])
def test_junction_override_validation(kw, match):
    with pytest.raises(ov.OverrideError, match=match):
        ov.validate_junctions(_ovr(**kw), ["123"], P.types)


def test_junction_override_file_is_valid_header():
    df = ov.read_overrides(ov.JUNCTION_OVERRIDES_PATH)
    assert list(df.columns) == ov.JUNCTION_COLUMNS
