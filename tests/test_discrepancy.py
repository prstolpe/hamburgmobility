"""Discrepancy (D-SPD-01, D-DES-01, D-USE-01, D-TYPE-01) and priority (P-RISK-01) in pipeline/lib/discrepancy.py."""

import json

import numpy as np
import pandas as pd
import pytest

from pipeline.lib import discrepancy as disc
from pipeline.lib.rules import load_rules

RULES = load_rules()

# Design features all known and compliant for GOW50 (track, no lane, no parking, one lane per direction).
GOW50_OK = {"separated_cycle_track_present": True, "cycle_lane_present": False, "centre_line": True,
            "parking_along_carriageway": False, "lanes_official_in": 1, "lanes_official_gegen": 1,
            "bahnigkeit_official": 1, "speed_ist_kmh": 50, "dtv_official": 20000,
            "parallel_cycle_route_present": False}


def assess(cat, **values):
    return disc.assess_segment(values, cat, RULES)


# --- D-SPD-01 --------------------------------------------------------------------------------


@pytest.mark.parametrize("ist, soll, expected", [
    (30, 30, 0), (20, 30, 0), (40, 30, 1), (49, 30, 1), (50, 30, 2), (59, 30, 2),
    (60, 30, 3), (30, 7, 2), (20, 7, 1), (10, 7, 1), (7, 7, 0),
])
def test_speed_severity(ist, soll, expected):
    assert disc.speed_severity(ist, soll, RULES)["result"] == expected


def test_speed_boundaries_19_20_29_30():
    sev = [disc.speed_severity(30 + e, 30, RULES)["result"] for e in (19, 20, 29, 30)]
    assert sev == [1, 2, 2, 3]


@pytest.mark.parametrize("ist, soll", [(None, 30), (np.nan, 30), (pd.NA, 30), (80, None)])
def test_speed_not_checked(ist, soll):
    step = disc.speed_severity(ist, soll, RULES)
    assert step["result"] is None and step["rule"] == "D-SPD-01"


def test_sw_has_no_speed_or_design_check():
    r = assess("SW", speed_ist_kmh=100, separated_cycle_track_present=False)
    assert r["disc_speed"] is None and r["disc_design"] is None and r["disc_use"] is None
    assert r["disc_max"] is None and r["disc_type"] is None


# --- D-DES-01 --------------------------------------------------------------------------------


def test_gow50_compliant():
    r = assess("GOW50", **GOW50_OK)
    assert r["disc_design"] == 0 and r["disc_design_unknown"] == []


def test_gow50_cycle_lane_without_track_counts_twice():
    r = assess("GOW50", **{**GOW50_OK, "separated_cycle_track_present": False, "cycle_lane_present": True})
    assert r["disc_design"] == 2
    labels = [c["label"] for c in r["disc_causes"]]
    assert "kein baulicher Radweg" in labels and "Radfahr- oder Schutzstreifen" in labels


def test_design_severity_capped_at_three():
    r = assess("GOW50", **{**GOW50_OK, "separated_cycle_track_present": False, "cycle_lane_present": True,
                           "parking_along_carriageway": True, "lanes_official_in": 2})
    assert len([c for c in r["disc_causes"] if c["dimension"] == "design"]) == 4
    assert r["disc_design"] == 3


def test_median_needs_two_lanes_per_direction_and_single_carriageway():
    assert assess("GOW50", **{**GOW50_OK, "lanes_official_gegen": 2})["disc_design"] == 1
    assert assess("GOW50", **{**GOW50_OK, "lanes_official_gegen": 2, "bahnigkeit_official": 2})["disc_design"] == 0
    assert assess("GOW50", **{**GOW50_OK, "lanes_official_in": None, "lanes_official_gegen": None})[
        "disc_design_unknown"] == ["median_if_lanes_per_dir_gte"]


def test_median_not_needed_without_oncoming_lanes():
    # one direction of a dual carriageway mapped as its own segment, or a one-way street
    assert assess("GOW50", **{**GOW50_OK, "lanes_official_in": 3, "lanes_official_gegen": 0})["disc_design"] == 0
    assert assess("GOW50", **{**GOW50_OK, "lanes_official_in": 0, "lanes_official_gegen": 4})["disc_design"] == 0


def test_missing_tags_are_unknown_not_violations():
    r = assess("GOW50", speed_ist_kmh=50)
    assert r["disc_design"] is None  # nothing could be checked
    assert set(r["disc_design_unknown"]) == {"cycling", "cycle_lanes_allowed", "parking_along_carriageway",
                                             "median_if_lanes_per_dir_gte"}
    r = assess("GOW50", **{**GOW50_OK, "parking_along_carriageway": None})
    assert r["disc_design"] == 0 and r["disc_design_unknown"] == ["parking_along_carriageway"]


def test_gow30_cycling_on_carriageway_and_centre_line():
    base = {"separated_cycle_track_present": False, "cycle_lane_present": False, "centre_line": True,
            "speed_ist_kmh": 50}
    r = assess("GOW30", **base)
    assert r["disc_design"] == 2 and r["disc_speed"] == 2
    assert assess("GOW30", **{**base, "cycle_lane_present": True, "centre_line": False})["disc_design"] == 0
    # one of the two known True is enough, the other may be unknown
    assert assess("GOW30", **{**base, "separated_cycle_track_present": None, "cycle_lane_present": True,
                              "centre_line": False})["disc_design"] == 0
    # both False/unknown: not decidable
    r = assess("GOW30", **{**base, "separated_cycle_track_present": None, "centre_line": False})
    assert r["disc_design"] == 0 and r["disc_design_unknown"] == ["cycling"]


def test_etw30_track_and_lane_are_flow():
    r = assess("ETW30", separated_cycle_track_present=True, cycle_lane_present=True, speed_ist_kmh=30)
    assert r["disc_design"] == 2 and r["disc_type"] == "D1"
    assert {c["direction"] for c in r["disc_causes"]} == {"flow"}


def test_no_two_design_checks_of_one_category_share_a_feature():
    from pipeline.lib import expr

    for cat, reqs in RULES.requirements.items():
        features = []
        for v in disc.applicable_violations(cat, RULES):
            features += sorted(expr.features_in(expr.parse(v.violated_if)) - {"requirement"})
        dup = {f for f in features if features.count(f) > 1}
        assert not dup, (cat, dup)  # each Ist feature counts at most once per category


def test_every_violation_has_a_direction_for_its_categories():
    for cat in RULES.requirements:
        for v in disc.applicable_violations(cat, RULES):
            assert v.direction_for(cat) in ("flow", "sparse")


# --- D-USE-01 --------------------------------------------------------------------------------


@pytest.mark.parametrize("dtv, expected", [(9000, 0), (10000, 0), (10001, 1), (15000, 1), (15001, 2),
                                           (20000, 2), (20001, 3), (50000, 3)])
def test_use_severity_wide_profile(dtv, expected):
    assert disc.use_severity(dtv, False, "GOW30", RULES)["result"] == expected


def test_use_track_profile_has_no_limit():
    assert disc.use_severity(50000, True, "GOW30", RULES)["result"] == 0


def test_use_unknown_track_only_matters_above_limit():
    assert disc.use_severity(8000, None, "GOW30", RULES)["result"] == 0
    assert disc.use_severity(12000, None, "GOW30", RULES)["result"] is None


def test_use_reports_narrow_limit_in_trace():
    step = disc.use_severity(7000, False, "GOW30", RULES)
    assert step["result"] == 0 and step["inputs"]["max_dtv_narrow"] == 6000


@pytest.mark.parametrize("cat", ["GOW50", "ETW30", "SW", "ETW_ERF"])
def test_use_not_applicable_without_max_dtv(cat):
    assert disc.use_severity(50000, False, cat, RULES)["result"] is None


def test_use_missing_dtv():
    assert disc.use_severity(None, False, "GOW30", RULES)["result"] is None


# --- D-TYPE-01 -------------------------------------------------------------------------------


@pytest.mark.parametrize("directions, expected", [(set(), None), ({"flow"}, "D1"), ({"sparse"}, "D2"),
                                                  ({"flow", "sparse"}, "D3")])
def test_disc_type(directions, expected):
    assert disc.disc_type(directions) == expected


def test_gow50_sparse_is_d2_and_with_speed_d3():
    sparse = {**GOW50_OK, "separated_cycle_track_present": False}
    assert assess("GOW50", **sparse)["disc_type"] == "D2"
    assert assess("GOW50", **{**sparse, "speed_ist_kmh": 70})["disc_type"] == "D3"


def test_trace_is_json_and_names_rules():
    r = assess("GOW30", separated_cycle_track_present=False, cycle_lane_present=False, centre_line=False,
               speed_ist_kmh=50, dtv_official=12000)
    trace = json.loads(json.dumps(r["disc_trace"]))
    assert [s["rule"] for s in trace] == ["D-SPD-01", "D-DES-01", "D-USE-01", "D-TYPE-01"]
    assert r["disc_max"] == 2 and r["disc_type"] == "D3"  # speed (flow) + no cycle facility (sparse)


# --- P-RISK-01 and priority ------------------------------------------------------------------


def _risk_input():
    return pd.DataFrame({
        "crash_weighted_per_km": [0.0, 10.0, 20.0, 5.0],
        "in_cycle_network": pd.array([True, False, None, True], dtype="boolean"),
        "population_100m_norm": [0.5, 0.0, 1.0, np.nan],
        "schools_or_kitas_within_m": [100.0, 150.0, 151.0, np.nan],
    })


def test_risk_components_and_weights():
    out = disc.risk_frame(_risk_input(), RULES)
    assert list(out["crash_norm"]) == pytest.approx([0.0, 2 / 3, 1.0, 1 / 3])
    assert list(out["school_kita_near"].iloc[:3]) == [1.0, 1.0, 0.0] and pd.isna(out["school_kita_near"].iloc[3])
    # row 0: 0.4*0 + 0.2*1 + 0.2*0.5 + 0.2*1 = 0.5
    assert out["risk"].iloc[0] == pytest.approx(0.5)
    assert out["risk_weight_available"].iloc[0] == pytest.approx(1.0)


def test_risk_missing_component_moves_weight():
    out = disc.risk_frame(_risk_input(), RULES)
    # row 2: cycle network unknown -> (0.4*1 + 0.2*1 + 0.2*0) / 0.8
    assert out["risk_weight_available"].iloc[2] == pytest.approx(0.8)
    assert out["risk"].iloc[2] == pytest.approx(0.6 / 0.8)
    # row 3: population and school unknown -> (0.4/3 + 0.2) / 0.6
    assert out["risk"].iloc[3] == pytest.approx((0.4 / 3 + 0.2) / 0.6)


def test_risk_without_crash_data():
    df = _risk_input().assign(crash_weighted_per_km=np.nan)
    out = disc.risk_frame(df, RULES)
    assert out["crash_norm"].isna().all()
    assert out["risk_weight_available"].iloc[0] == pytest.approx(0.6)


@pytest.mark.parametrize("sev, risk, expected", [(None, 0.5, None), (0, 0.5, 0.0), (0, None, 0.0),
                                                 (2, 0.5, 1.0), (3, 1.0, 3.0), (2, None, None)])
def test_priority(sev, risk, expected):
    assert disc.priority(sev, risk) == expected


def test_crashes_per_km_uses_minimum_length():
    per_km = disc.crashes_per_km(pd.Series([2.0, 2.0, 0.0]), pd.Series([20.0, 400.0, 50.0]), RULES)
    assert list(per_km) == pytest.approx([20.0, 5.0, 0.0])  # 2 / 0.1 km, 2 / 0.4 km


# --- street summary in reports/priority_top30.md ---------------------------------------------


def test_street_summary_groups_by_name():
    from pipeline.s08_discrepancy import street_summary

    df = pd.DataFrame({
        "segment_id": ["s1", "s2", "s3", "s4", "s5"],
        "name": ["A-Straße", "A-Straße", "B-Weg", None, "C-Allee"],
        "cat_final": ["GOW30", "ETW30", "ETW30", "ETW30", "GOW50"],
        "priority": [2.0, 1.0, 1.5, 2.5, 0.0],
        "length_m": [100.0, 50.0, 80.0, 30.0, 40.0],
        "crashes_ped_cyc": [3, 1, 0, 2, 5],
        "crashes_severe_fatal": [1, 0, 0, 0, 1],
    })
    out = street_summary(df, top_ids={"s1", "s4"})
    assert list(out["name"]) == ["A-Straße", "B-Weg"]  # unnamed and priority 0 left out, sorted by max priority
    a = out.iloc[0]
    assert (a["n_segments"], a["length_m"], a["max_priority"], a["crashes_ped_cyc"], a["crashes_severe_fatal"],
            a["n_in_top"], a["cats"], a["best_segment_id"]) == (2, 150.0, 2.0, 4, 1, 1, "GOW30, ETW30", "s1")


def test_street_summary_lists_bezirke():
    """A street crossing a Bezirk border lists both Bezirke (names are unique city-wide in Hamburg)."""
    from pipeline.s08_discrepancy import street_summary

    df = pd.DataFrame({
        "segment_id": ["s1", "s2"], "name": ["A-Straße", "A-Straße"], "bezirk": ["Altona", "Eimsbüttel"],
        "cat_final": ["GOW30", "GOW30"], "priority": [2.0, 1.0], "length_m": [100.0, 50.0],
        "crashes_ped_cyc": [0, 0], "crashes_severe_fatal": [0, 0],
    })
    assert street_summary(df, top_ids=set()).iloc[0]["bezirke"] == "Altona, Eimsbüttel"


def test_gow50_without_track_but_parallel_route_is_no_violation():
    # rules.yaml 0.16.0 (open question 65): D-DES-01 "Radweg oder Parallelroute" is checkable via S-FEAT-11
    no_track = {**GOW50_OK, "separated_cycle_track_present": False}
    assert "kein baulicher Radweg" in [c["label"] for c in assess("GOW50", **no_track)["disc_causes"]]
    r = assess("GOW50", **{**no_track, "parallel_cycle_route_present": True})
    assert "kein baulicher Radweg" not in [c["label"] for c in r["disc_causes"]] and r["disc_design"] == 0
