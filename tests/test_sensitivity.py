"""Sensitivity analysis (V-SENS-01, V-SENS-02, V-UNC-01) in pipeline/lib/sensitivity.py."""

import numpy as np
import pandas as pd
import pytest

from pipeline.lib import discrepancy as disc
from pipeline.lib import sensitivity as sens
from pipeline.lib.rules import load_rules

RULES = load_rules()

# Inner-city segment that falls to C-ETW-01 unless conn_score reaches conn_gow.
BASE = {
    "highway": "secondary", "access_motor_only": False, "outside_builtup_area": False,
    "ist_verkehrsberuhigt": False, "pedestrian_zone": False, "override_school_street": False,
    "in_hvs": False, "schools_or_kitas_within_m": 500.0, "shop_frontage_share": 0.1, "crossing_demand": None,
    "separated_cycle_track_present": True, "width_p10_m": 25.0,
    "betweenness_norm": 1.0, "bus_trips_weekday_norm": 1.0, "dtv_norm": 0.0,
}


def frame(*rows) -> pd.DataFrame:
    return pd.DataFrame([{**BASE, **r} for r in rows])


# --- parameters ------------------------------------------------------------------------------


def test_varied_parameters():
    params = {p.key: p for p in sens.varied_parameters(RULES)}
    assert params["thresholds.conn_gow"].effect == "category"
    assert params["thresholds.conn_gow"].base == pytest.approx(0.6)
    assert params["thresholds.sensitive_radius"].effect == "category"
    assert params["thresholds.frontage"].effect == "category"
    assert params["required_width.GOW50"].effect == "category"
    assert params["thresholds.near_threshold"].effect == "confidence"
    assert {k for k, p in params.items() if p.group == "conn_weight"} == {
        f"conn_score.{f}" for f in RULES.scores["conn_score"].weights}
    assert {k for k, p in params.items() if p.group == "risk_weight"} == {
        f"risk_weights.{k}" for k in RULES.priority.risk_weights}
    # only assumptions are varied; required_width entries not read by the cascade are not
    assert "required_width.GOW50_bus" not in params


def test_fixed_assumptions_lists_upstream_thresholds():
    fixed = {f["path"]: f for f in sens.fixed_assumptions(RULES)}
    assert "conflation.S-CONF-01.buffer_m" in fixed
    assert "crosssection.S-XS-01.spacing_m" in fixed
    assert fixed["conflation.S-CONF-01.buffer_m"]["value"] == 15
    assert all(f["reason"] for f in fixed.values())
    varied = {p.key for p in sens.varied_parameters(RULES)}
    assert not any(path.endswith(".conn_gow") for path in fixed) and "thresholds.conn_gow" in varied


def test_with_values_copies():
    changed = sens.with_values(RULES, {"thresholds.conn_gow": 0.48, "required_width.GOW50": 13.2,
                                       "conn_score.in_hvs": 0.3, "risk_weights.cycle_network": 0.24,
                                       "thresholds.near_threshold": 0.12})
    assert changed is not RULES
    assert RULES.classification[3].thresholds["conn_gow"].value == pytest.approx(0.6)
    assert next(r for r in changed.classification if r.id == "C-GOW-01").thresholds["conn_gow"].value == pytest.approx(0.48)
    assert changed.required_width["GOW50"].value == pytest.approx(13.2)
    assert changed.scores["conn_score"].weights["in_hvs"] == pytest.approx(0.3)
    assert changed.priority.risk_weights["cycle_network"] == pytest.approx(0.24)
    assert RULES.priority.risk_weights["cycle_network"] == pytest.approx(0.2)


def test_with_values_unknown_key():
    with pytest.raises(KeyError):
        sens.with_values(RULES, {"thresholds.nope": 1.0})


# --- classification --------------------------------------------------------------------------


def test_conn_score_recomputed_and_reweighted():
    df = frame({}, {"dtv_norm": None})
    score, share = sens.conn_score(df, RULES)
    assert score[0] == pytest.approx(0.55)  # 0.35 + 0.20
    assert share[0] == pytest.approx(1.0)
    assert score[1] == pytest.approx(0.55 / 0.8)  # weight of dtv moved to the others
    assert share[1] == pytest.approx(0.8)


def test_categories_follow_threshold():
    df = frame({})  # conn_score 0.55 < 0.6
    assert sens.categories(df, RULES).tolist() == ["ETW30"]
    lower = sens.with_values(RULES, {"thresholds.conn_gow": 0.48})
    assert sens.categories(df, lower).tolist() == ["GOW50"]


def test_categories_follow_weights():
    df = frame({})
    heavier = sens.with_values(RULES, {"conn_score.betweenness_norm": 0.42, "conn_score.bus_trips_weekday_norm": 0.24})
    # (0.42 + 0.24) / (0.42 + 0.25 + 0.24 + 0.20) = 0.595 -> still ETW30; scores are normalised by the weight sum
    assert sens.categories(df, heavier).tolist() == ["ETW30"]
    no_dtv = sens.with_values(RULES, {"conn_score.dtv_norm": 0.0, "conn_score.in_hvs": 0.0})
    assert sens.categories(df, no_dtv).tolist() == ["GOW50"]  # 0.55 / 0.55 = 1


def test_one_at_a_time_columns():
    df = frame({}, {"bus_trips_weekday_norm": 0.0})
    params = [p for p in sens.varied_parameters(RULES) if p.effect == "category"]
    out = sens.one_at_a_time(df, RULES, params, delta=0.2)
    assert set(out.columns) == {f"{p.key}:{s}" for p in params for s in ("-", "+")}
    assert out.loc[0, "thresholds.conn_gow:-"] == "GOW50"
    assert out.loc[0, "thresholds.conn_gow:+"] == "ETW30"
    assert out.loc[1, "thresholds.conn_gow:-"] == "ETW30"


# --- Monte Carlo -----------------------------------------------------------------------------


def test_sample_factors_reproducible():
    a = sens.sample_factors(50, 4, delta=0.2, seed=7)
    b = sens.sample_factors(50, 4, delta=0.2, seed=7)
    assert a.shape == (50, 4)
    assert np.array_equal(a, b)
    assert a.min() >= 0.8 and a.max() <= 1.2
    assert not np.array_equal(a, sens.sample_factors(50, 4, delta=0.2, seed=8))


def test_run_values():
    params = [sens.Param("thresholds.conn_gow", 0.6, "threshold", "category", "C-GOW-01"),
              sens.Param("conn_score.in_hvs", 0.25, "conn_weight", "category", "scores.conn_score")]
    assert sens.run_values(params, np.array([1.1, 0.8])) == pytest.approx(
        {"thresholds.conn_gow": 0.66, "conn_score.in_hvs": 0.2})


def test_monte_carlo_shape_and_seed():
    df = frame({}, {"bus_trips_weekday_norm": 0.0})
    params = [p for p in sens.varied_parameters(RULES) if p.effect == "category"]
    factors = sens.sample_factors(20, len(params), delta=0.2, seed=1)
    runs = sens.monte_carlo(df, RULES, params, factors)
    assert runs.shape == (2, 20)
    assert set(runs.iloc[0]) <= {"ETW30", "GOW50", "GOW30"}
    assert set(runs.iloc[1]) == {"ETW30"}  # conn_score 0.35 stays below 0.48
    assert runs.equals(sens.monte_carlo(df, RULES, params, factors))


def test_change_summary():
    base = pd.Series(["A", "A", "A"])
    runs = pd.DataFrame([list("AABBAAAAAA"), list("ABBBAAAAAA"), list("AAAAAAAAAA")])
    out = sens.change_summary(base, runs, min_rate=0.3)
    assert out["change_rate"].tolist() == pytest.approx([0.2, 0.3, 0.0])
    assert out["uncertain"].tolist() == [False, True, False]  # "ab 0,3"
    assert out["alt_category"].tolist() == ["B", "B", None]
    assert out["alt_share"].tolist()[:2] == pytest.approx([0.2, 0.3])


def test_oat_changes_per_segment():
    base = pd.Series(["ETW30", "ETW30"])
    oat = pd.DataFrame({"thresholds.conn_gow:-": ["GOW50", "ETW30"], "thresholds.conn_gow:+": ["ETW30", "ETW30"],
                        "thresholds.frontage:-": ["GOW30", "ETW30"]})
    assert sens.oat_changes(base, oat).tolist() == [["thresholds.conn_gow:-", "thresholds.frontage:-"], []]


# --- priority --------------------------------------------------------------------------------


def _risk_input() -> pd.DataFrame:
    return pd.DataFrame({
        "crashes_ped_cyc": [0, 2, 5, 1], "crashes_severe_fatal": [0, 1, 0, 1], "length_m": [200.0, 50.0, 400.0, 150.0],
        "in_cycle_network": [True, False, None, True], "population_100m_norm": [0.1, 0.9, 0.5, None],
        "schools_or_kitas_within_m": [100.0, 400.0, None, 20.0], "disc_max": [2, 3, 0, None],
    })


def test_risk_with_base_weights_matches_stage8():
    df = _risk_input()
    w = RULES.priority.risk_weights[RULES.priority.risk.severe_weight_key]
    weighted = df["crashes_ped_cyc"] - df["crashes_severe_fatal"] + w * df["crashes_severe_fatal"]
    expected = disc.risk_frame(df.assign(crash_weighted_per_km=disc.crashes_per_km(weighted, df["length_m"], RULES)), RULES)
    pd.testing.assert_series_equal(sens.risk(df, RULES), expected["risk"], check_names=False)


def test_priorities_and_top_stability():
    df = _risk_input()
    p = sens.priorities(df, RULES)
    assert p[2] == 0.0 and np.isnan(p[3])
    runs = pd.DataFrame({0: [0.5, 0.9, 0.0, np.nan], 1: [0.95, 0.9, 0.0, np.nan], 2: [0.3, 0.4, 0.0, np.nan]})
    base = pd.Series([0.6, 0.9, 0.0, np.nan])
    ids = pd.Series(["a", "b", "c", "d"])
    stab = sens.top_stability(base, runs, ids, top_n=1)
    assert stab["base_top"] == ["b"]
    assert stab["stay_share"] == {"b": pytest.approx(2 / 3)}
    assert stab["mean_overlap"] == pytest.approx(2 / 3)


def test_post_step_applied_after_cascade():
    df = frame({}, {})
    seen = []

    def post(cats, rules):
        seen.append(rules)
        return cats.where(cats.index != 1, "GOW30")

    assert sens.categories(df, RULES, post=post).tolist() == ["ETW30", "GOW30"]
    params = [p for p in sens.varied_parameters(RULES) if p.key == "thresholds.conn_gow"]
    oat = sens.one_at_a_time(df, RULES, params, delta=0.2, post=post)
    assert oat["thresholds.conn_gow:+"].tolist() == ["ETW30", "GOW30"]
    runs = sens.monte_carlo(df, RULES, params, sens.sample_factors(3, 1, 0.2, 1), post=post)
    assert (runs.loc[1] == "GOW30").all()


def test_parallel_runs_equal_serial_runs(monkeypatch):
    # pipeline/lib/parallel.py: same output with 1 and several workers
    df = frame({}, {"bus_trips_weekday_norm": 0.0}, {"bus_trips_weekday_norm": 0.5})
    params = [p for p in sens.varied_parameters(RULES) if p.effect == "category"]
    factors = sens.sample_factors(12, len(params), delta=0.2, seed=3)
    monkeypatch.setenv("SFP_WORKERS", "1")
    mc1, oat1 = sens.monte_carlo(df, RULES, params, factors), sens.one_at_a_time(df, RULES, params, 0.2)
    monkeypatch.setenv("SFP_WORKERS", "4")
    mc4, oat4 = sens.monte_carlo(df, RULES, params, factors), sens.one_at_a_time(df, RULES, params, 0.2)
    assert mc1.equals(mc4) and oat1.equals(oat4)
