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


def test_gow30_pair_uses_j01_traffic_limits():
    # design_rules.yaml 0.4.0 (open question 134): J-03 with the DTV limits of J-01
    gow30 = [leg("GOW30"), leg("GOW30")]
    assert jn.decide(props(gow30, entering_dtv_sum=T["roundabout_max_dtv"]), P)["junction_type_soll"] == \
        "roundabout_single_lane_cycle_priority"
    turbo_space = T["turbo_min_radius"]  # Review 2026-11 F24: turbo needs its own space
    assert jn.decide(props(gow30, entering_dtv_sum=T["roundabout_max_dtv"] + 1, space_radius_m=turbo_space),
                     P)["junction_type_soll"] == "turbo_roundabout"
    high = jn.decide(props(gow30, entering_dtv_sum=T["turbo_max_dtv"] + 1), P)
    assert high["junction_type_soll"] == "signal_protected" and high["rule_id"] == "J-03"
    assert "dtv_above_roundabout_max" not in high["conflict_flags"]


def test_gow30_turbo_without_space_falls_back_to_coloured_priority():
    small = T["roundabout_min_radius"] - 1
    r = jn.decide(props([leg("GOW30"), leg("GOW30")], entering_dtv_sum=T["roundabout_max_dtv"] + 1, space_radius_m=small), P)
    assert r["junction_type_soll"] == "priority_flat_coloured"


def test_network_cycle_path_across_access_road_has_priority():
    # open question 133: J-12
    for cat in ("RSV", "HAUPT", "BASIS"):
        r = jn.decide(props([leg("ETW30"), leg("ETW30"), leg("cycle_path", cat, "own_path")]), P)
        assert r["junction_type_soll"] == "cycle_crossing_priority" and r["rule_id"] == "J-12"
    # Review 2026-11 F10: J-16 for ERSCHL paths (before: no_rule)
    r = jn.decide(props([leg("ETW30"), leg("ETW30"), leg("cycle_path", "ERSCHL", "own_path")]), P)
    assert r["junction_type_soll"] == "equal_right_before_left" and r["rule_id"] == "J-16"


def test_access_road_meets_pedestrian_zone_continuous_footway():
    # open question 135: J-13 matches the raw category ETW_ERF before category_alias
    r = jn.decide(props([leg("ETW30"), leg("ETW30"), leg("ETW_ERF")]), P)
    assert r["junction_type_soll"] == "continuous_footway_exit" and r["rule_id"] == "J-13"
    r = jn.decide(props([leg("ETW_ERF"), leg("ETW_ERF")]), P)
    assert r["junction_type_soll"] == "equal_right_before_left"
    r = jn.decide(props([leg("GOW50"), leg("GOW50"), leg("ETW_ERF")]), P)
    assert r["junction_type_soll"] == "continuous_footway_exit" and r["rule_id"] == "J-04"


def test_signal_counts_only_for_nearest_junction():
    # open question 137: a traffic light within the radius of two junctions belongs to the nearer one
    from shapely.geometry import MultiPoint
    juncs = gpd.GeoSeries([MultiPoint([(0, 0)]), MultiPoint([(20, 0)]), MultiPoint([(500, 0)])])
    sig = gpd.GeoSeries([Point(5, 0)])
    assert list(c07.nearest_hit(juncs, sig, 30.0)) == [True, False, False]
    assert list(c07.nearest_hit(juncs, gpd.GeoSeries([Point(300, 0)]), 30.0)) == [False, False, False]


@pytest.mark.parametrize("cycle_cat", ["BASIS", "ERSCHL"])
def test_cycle_path_basis_or_erschl_across_gow50(cycle_cat):
    # Review 2026-11 F10: J-15 (before: no_rule)
    def run(lanes, dtv):
        return jn.decide(props([leg("GOW50", lanes=lanes), leg("GOW50", lanes=lanes), leg("cycle_path", cycle_cat, "own_path")],
                               entering_dtv_sum=dtv), P)
    low = run(1, T["crossing_signal_min_dtv"])
    assert low["junction_type_soll"] == "cycle_crossing_refuge" and low["rule_id"] == "J-15"
    assert run(1, T["crossing_signal_min_dtv"] + 1)["junction_type_soll"] == "cycle_crossing_signal"
    assert run(2, 1000)["junction_type_soll"] == "cycle_crossing_signal"
    unknown = run(None, 1000)
    assert unknown["junction_type_soll"] == "cycle_crossing_signal" and "condition_unknown" in unknown["conflict_flags"]


def test_sw_rows_before_tram():
    # Review 2026-11 F08: SW+GOW50 is a ramp node decided like J-01 (J-10b), J-11 (tram) was removed in package 5 K8
    r = jn.decide(props([leg("SW"), leg("SW"), leg("GOW50", "HAUPT")], tram_present=True), P)
    assert r["rule_id"] == "J-10b" and r["junction_type_soll"] == "signal_protected"


def test_grade_separated_only_for_standalone_main_routes_across_sw():
    for cat in ("RSV", "HAUPT"):
        r = jn.decide(props([leg("SW"), leg("SW"), leg("cycle_path", cat, "own_path")]), P)
        assert r["junction_type_soll"] == "grade_separated_cycle" and r["rule_id"] == "J-10"
    for cat in ("BASIS", "ERSCHL"):
        r = jn.decide(props([leg("SW"), leg("SW"), leg("cycle_path", cat, "own_path")]), P)
        assert r["junction_type_soll"] == "not_applicable" and r["rule_id"] == "J-10d"


@pytest.mark.parametrize("legs, rule, jtype", [
    ([leg("SW"), leg("SW"), leg("SW")], "J-10d", "not_applicable"),
    ([leg("SW"), leg("ETW30"), leg("ETW30")], "J-10c", "signal_protected"),
    ([leg("SW"), leg("ETW_ERF")], "J-10c", "signal_protected"),
    ([leg("SW"), leg("GOW30"), leg("GOW30")], "J-10b", "roundabout_single_lane_cycle_priority"),
])
def test_ramp_rows(legs, rule, jtype):
    r = jn.decide(props(legs), P)
    assert (r["rule_id"], r["junction_type_soll"]) == (rule, jtype)


def test_legs_alternatives_are_parsed():
    tram, sides = jn._parse_legs("SW+SW|cycle_path(BASIS|ERSCHL)")
    assert not tram and [s.base for s in sides[0]] == ["SW"]
    assert [(s.base, sorted(s.cycle_cats)) for s in sides[1]] == [("SW", []), ("cycle_path", ["BASIS", "ERSCHL"])]


def test_turbo_needs_own_space():
    # Review 2026-11 F24: J-01 else_if with turbo_min_radius
    dtv = T["roundabout_max_dtv"] + 1
    gow50 = [leg("GOW50"), leg("GOW50")]
    assert jn.decide(props(gow50, entering_dtv_sum=dtv, space_radius_m=T["turbo_min_radius"]), P)["junction_type_soll"] == "turbo_roundabout"
    r = jn.decide(props(gow50, entering_dtv_sum=dtv, space_radius_m=T["turbo_min_radius"] - 1), P)
    assert r["junction_type_soll"] == "signal_protected"
    # J-03 (with fallback): turbo below turbo_min_radius takes the fallback (fallback_if.condition_by_type)
    gow30 = [leg("GOW30"), leg("GOW30")]
    r = jn.decide(props(gow30, entering_dtv_sum=dtv, space_radius_m=T["turbo_min_radius"] - 1), P)
    assert r["junction_type_soll"] == "priority_flat_coloured"


# --- J-14: cycle route crossing GOW50 (Review 2026-11 F03) ---------------------------------------------------------


def _crossing(lanes=1, route=("HAUPT", "HAUPT"), bearings=None):
    legs = [leg("GOW50", lanes=lanes), leg("GOW50", lanes=lanes),
            leg("ETW30", route[0], "mixed", lanes="shared"), leg("ETW30", route[1], "mixed", lanes="shared")]
    if bearings:
        legs = [{**lg, "bearing": b} for lg, b in zip(legs, bearings)]
    return legs


def test_route_crossing_gow50_needs_signal_with_two_lanes_or_high_volume():
    r = jn.decide(props(_crossing(lanes=2), entering_dtv_sum=8000), P)
    assert r["junction_type_soll"] == "cycle_crossing_signal" and r["rule_id"] == "J-14"
    r = jn.decide(props(_crossing(lanes=1), entering_dtv_sum=T["crossing_signal_min_dtv"] + 1), P)
    assert r["junction_type_soll"] == "cycle_crossing_signal"
    r = jn.decide(props(_crossing(lanes=1), entering_dtv_sum=T["crossing_signal_min_dtv"]), P)
    assert r["junction_type_soll"] == "continuous_footway_exit" and r["rule_id"] == "J-14"


def test_route_not_crossing_falls_back_to_j04():
    # only one route arm (route turns onto the main road), or route arms on the same side, or ERSCHL
    for legs in (_crossing(lanes=2, route=("HAUPT", "none")),
                 _crossing(lanes=2, bearings=[0, 180, 80, 100]),
                 _crossing(lanes=2, route=("ERSCHL", "ERSCHL"))):
        r = jn.decide(props(legs, entering_dtv_sum=20000), P)
        assert r["rule_id"] == "J-04" and r["junction_type_soll"] == "continuous_footway_exit"
    r = jn.decide(props(_crossing(lanes=2, bearings=[0, 180, 90, 270]), entering_dtv_sum=8000), P)
    assert r["rule_id"] == "J-14"


def test_lanes_per_direction_max():
    assert jn.lanes_per_direction_max([leg("GOW50", lanes="2"), leg("ETW30", lanes="shared"), leg("cycle_path")]) == 2
    assert jn.lanes_per_direction_max([leg("ETW30", lanes="shared")]) == 1
    assert jn.lanes_per_direction_max([leg("GOW50", lanes=None), leg("GOW50", lanes=float("nan"))]) is None


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


def test_jc01_only_single_lane_roundabout_jc06_at_turbo():
    # Review 2026-11 F02
    gow50 = [leg("GOW50"), leg("GOW50")]
    assert "JC-01" in jn.treatments("roundabout_single_lane_cycle_priority", ("GOW50", "GOW50"), gow50, P)
    turbo = jn.treatments("turbo_roundabout", ("GOW50", "GOW50"), gow50, P)
    assert "JC-01" not in turbo and "JC-06" in turbo
    assert jn.treatment_flags("turbo_roundabout", gow50, turbo, P) == []
    haupt = [leg("GOW50", "HAUPT"), leg("GOW50")]
    assert jn.treatment_flags("turbo_roundabout", haupt, turbo, P) == ["turbo_grade_sep_check"]
    basis = [leg("GOW50", "BASIS"), leg("GOW50")]
    assert jn.treatment_flags("turbo_roundabout", basis, turbo, P) == []


def test_refuge_crossing_has_median():
    assert "JC-04" in jn.treatments("cycle_crossing_refuge", ("GOW50", "cycle_path"),
                                    [leg("GOW50"), leg("GOW50"), leg("cycle_path", "ERSCHL", "own_path")], P)


def test_jc01_text_names_the_conflict():
    text = jn.treatment_text(["JC-01"])
    assert "SWOV" in text and "StVO" in text


@pytest.mark.parametrize("soll, ist, expected", [
    ("signal_protected", "signal", "match"),
    ("signal_protected", "none_mapped", "mismatch"),
    ("continuous_footway_exit", "none_mapped", "not_checkable"),
    ("equal_right_before_left", "signal", "mismatch"),
    ("grade_separated_cycle", "none_mapped", "mismatch"),
    ("cycle_crossing_refuge", "none_mapped", "not_checkable"),
    ("cycle_crossing_refuge", "signal", "mismatch"),
    ("not_applicable", "signal", "match"),
    ("not_applicable", "none_mapped", "match"),
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


def test_merged_arm_keeps_highest_lane_count():
    legs = [leg("GOW50", id="a", name="X", dtv=50000, bearing=10, lanes="1"),
            leg("GOW50", id="b", name="X", dtv=50000, bearing=350, lanes="2")]
    arms = jn.merge_arms(legs, DESIGN.junctions.method_rule("J-M-02")["arm_merge_angle_deg"]["value"])
    assert len(arms) == 1 and arms[0]["lanes"] == 2


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


# --- rule consolidation (redesign 2026-11, package 5: K2, K3, K7, K8) -----------------------------------------


def _row(rid):
    return next(r for r in DESIGN.junctions.decision_table.rows if r.id == rid)


def test_j01_covers_gow50_with_gow30_like_the_former_j02():
    """K3: J-01 takes over GOW50+GOW30; trace names J-01 with alias J-02."""
    assert "J-02" not in {r.id for r in DESIGN.junctions.decision_table.rows}
    assert (_row("J-01").model_extra or {})["aliases"] == ["J-02"]
    for dtv in (1000.0, T["roundabout_max_dtv"] + 1, T["turbo_max_dtv"] + 1):
        mixed = jn.decide(props([leg("GOW50", "HAUPT"), leg("GOW30")], entering_dtv_sum=dtv), P)
        same = jn.decide(props([leg("GOW50", "HAUPT"), leg("GOW50")], entering_dtv_sum=dtv), P)
        assert mixed["rule_id"] == "J-01" and mixed["junction_type_soll"] == same["junction_type_soll"]
        assert mixed["pair"] == ("GOW50", "GOW30")
        decided = mixed["rule_trace_junction"][-1]
        assert decided["id"] == "J-01" and decided["aliases"] == ["J-02"]
    high = jn.decide(props([leg("GOW50", "HAUPT"), leg("GOW30")], entering_dtv_sum=T["turbo_max_dtv"] + 1), P)
    assert high["junction_type_soll"] == "signal_protected"


def test_j01_does_not_swallow_other_pairs():
    assert jn.decide(props([leg("GOW30"), leg("GOW30")]), P)["rule_id"] == "J-03"
    assert jn.decide(props([leg("GOW50"), leg("ETW30")]), P)["rule_id"] != "J-01"


def test_signal_protected_gets_only_jc02():
    """K2: JC-05 is a component of JC-02; the node carries JC-02 once."""
    legs = [leg("GOW50", "HAUPT"), leg("GOW30")]
    ids = jn.treatments("signal_protected", ("GOW50", "GOW30"), legs, P)
    assert "JC-02" in ids and "JC-05" not in ids
    jc02 = next(e for e in P.treatments if e["id"] == "JC-02")
    assert jc02["aliases"] == ["JC-05"] and "freies Rechtsabbiegen" in jc02["rule"]
    assert [c["source_type"] for c in jc02["components"]] == ["assumption"]
    assert "JC-05" not in jn.TREATMENT_DE and "Rechtsabbiegen" in jn.TREATMENT_DE["JC-02"]


def test_j11_removed_and_evaluation_order_valid():
    """K8: no tram row; every remaining row is in evaluation_order exactly once."""
    assert "J-11" not in P.rows and "J-11" not in P.order and not any(r.tram for r in P.rows.values())
    assert sorted(P.order) == sorted(P.rows) and len(set(P.order)) == len(P.order)


def test_prf07_removed_and_note_moved_to_pl05():
    """K7: PRF-07 is gone; its hint lives in the note of PL-05."""
    ids = {r["id"] for r in DESIGN.profile_assignment["rules"]}
    assert "PRF-07" not in ids and "PRF-06" in ids
    pl05 = next(r for r in DESIGN.placement["rules"] if r["id"] == "PL-05")
    assert "nicht prüfbar" in pl05["note"] and "Streckenprofil" in pl05["note"]
