"""Unit tests for pipeline/lib/principles.py (prompts/17: five principles, Ist and Soll).

Values are taken from config/cycling_rules.yaml through PrincipleParams, so no threshold is copied here.
"""

import math

import numpy as np
import pandas as pd
import pytest
import shapely

from pipeline.lib import principles as pr
from pipeline.lib.rules import load_cycling_rules, load_rules

P = pr.PrincipleParams.from_rules(load_cycling_rules(), load_rules())
NAN = float("nan")


# --- params ------------------------------------------------------------------------------------


def test_params_cover_all_checks_and_weights():
    assert set(P.check_principle.values()) == set(P.weights)
    assert abs(sum(P.weights.values()) - 1) < 1e-9
    assert set(P.unavailable) <= set(P.check_principle)
    assert "P-COH-03" in P.network_only


def test_params_read_thresholds_from_principles():
    cyc = load_cycling_rules()
    checks = {c["id"]: c for p in cyc.principles.values() for c in p["checks"]}
    assert P.detour_max == {k: float(v) for k, v in checks["P-DIR-01"]["thresholds"].items()}
    assert P.patt_dtv == float(checks["P-ATT-03"]["dtv"])


def test_crash_parameters_come_from_risk_rule():
    risk = load_rules().priority.risk
    assert P.crash_snap_m == risk.thresholds["snap_m"].value
    assert P.crash_min_length_m == risk.thresholds["min_length_m"].value


# --- score forms -------------------------------------------------------------------------------


def test_score_share_and_ratio():
    assert pr.score("share", 0.4) == pytest.approx(0.4)
    assert pr.score("ratio", 1.0, 2.0) == pytest.approx(0.5)
    assert pr.score("ratio", 3.0, 2.0) == 1.0


def test_score_inverse_ratio():
    assert pr.score("inverse_ratio", 0.0, 1.0) == 1.0
    assert pr.score("inverse_ratio", 0.5, 1.0) == 1.0
    assert pr.score("inverse_ratio", 2.0, 1.0) == pytest.approx(0.5)


def test_score_excess_for_detour():
    t = 1.2
    assert pr.score("excess", 1.0, t) == 1.0
    assert pr.score("excess", t, t) == 1.0
    assert pr.score("excess", 1.3, t) == pytest.approx(0.5)
    assert pr.score("excess", 1.4, t) == 0.0
    assert pr.score("excess", 3.0, t) == 0.0


def test_score_unknown_stays_unknown():
    for form in ("share", "ratio", "inverse_ratio", "excess"):
        assert math.isnan(pr.score(form, NAN, 1.5))
    assert math.isnan(pr.score("ratio", 2.0, NAN))


def test_percentile_inverse():
    s = pr.percentile_inverse(np.array([0.0, 1.0, 2.0, NAN]))
    assert s[0] > s[1] > s[2]
    assert math.isnan(s[3])
    assert 0 <= np.nanmin(s) and np.nanmax(s) <= 1


def test_percentile_inverse_ties_get_same_score():
    s = pr.percentile_inverse(np.array([0.0, 0.0, 0.0, 5.0]))
    assert s[0] == s[1] == s[2] > s[3]


# --- facilities --------------------------------------------------------------------------------


def test_ist_facility_by_condition():
    assert pr.ist_facility("road", "C-IMP-01", None, None, P) == "cycle_street"
    assert pr.ist_facility("path", "C-IMP-02", None, None, P) == "own_path"
    assert pr.ist_facility("road", "C-IMP-03", ["track"], None, P) == "separated_oneway_both"
    assert pr.ist_facility("road", "C-IMP-04", None, None, P) == "mixed"
    assert pr.ist_facility("road", "C-IMP-05", ["lane"], None, P) == "cycle_lane"
    assert pr.ist_facility("road", "C-IMP-07", None, None, P) == "mixed"


def test_ist_facility_lane_on_fast_road_is_cycle_lane():
    assert pr.ist_facility("road", "C-IMP-07", ["no", "lane"], None, P) == "cycle_lane"


def test_ist_facility_sidepath_by_direction():
    assert pr.ist_facility("path", "C-IMP-02", None, True, P) == P.sidepath_oneway
    assert pr.ist_facility("path", "C-IMP-02", None, False, P) == P.sidepath_twoway


def test_ist_facility_ferry_unknown():
    assert pr.ist_facility("ferry", "C-GRAPH-03", None, None, P) is None


def test_soll_facility_from_matrix():
    assert pr.soll_facility("GOW50", "HAUPT", P) == ("separated_oneway_both", None)
    assert pr.soll_facility("GOW30", "HAUPT", P) == ("separated_oneway_both", "cycle_lane")
    assert pr.soll_facility("ETW30", "HAUPT", P) == ("cycle_street", None)
    assert pr.soll_facility("ETW30", "ERSCHL", P) == ("mixed", None)
    assert pr.soll_facility("SW", "BASIS", P) == ("own_path", None)
    assert pr.soll_facility("GOW80", "HAUPT", P) == ("separated_twoway", None)
    assert pr.soll_facility(None, "HAUPT", P) == (None, None)


def test_edge_soll_facility_paths():
    assert pr.edge_soll_facility("path", None, None, "HAUPT", P)[0] == "own_path"
    assert pr.edge_soll_facility("path", None, "GOW50", "HAUPT", P)[0] == "separated_oneway_both"
    assert pr.edge_soll_facility("road", "ETW30", None, "BASIS", P)[0] == "mixed"
    assert pr.edge_soll_facility("ferry", None, None, "HAUPT", P)[0] is None


def test_facility_score_full_partial_none():
    assert pr.facility_score("separated_oneway_both", "separated_oneway_both", None, P) == 1.0
    assert pr.facility_score("separated_twoway", "separated_oneway_both", None, P) == P.partial_score
    assert pr.facility_score("cycle_lane", "separated_oneway_both", "cycle_lane", P) == P.partial_score
    assert pr.facility_score("mixed", "separated_oneway_both", None, P) == 0.0
    assert pr.facility_score("cycle_lane", "mixed", None, P) == 0.0  # S-02: no cycle lane on ETW30
    assert math.isnan(pr.facility_score(None, "mixed", None, P))
    assert math.isnan(pr.facility_score("mixed", None, None, P))


def test_soll_facility_always_satisfies_itself():
    for soll in P.satisfies:
        assert pr.facility_score(soll, soll, None, P) == 1.0


# --- width, surface, lit -----------------------------------------------------------------------


@pytest.mark.parametrize("raw,expected", [("2", 2.0), ("2.5", 2.5), ("2,5", 2.5), ("1.8 m", 1.8), ("2;3", 2.0),
                                          ("", NAN), (None, NAN), ("narrow", NAN), ("0", NAN)])
def test_parse_width(raw, expected):
    got = pr.parse_width(raw)
    assert (math.isnan(got) and math.isnan(expected)) or got == pytest.approx(expected)


def test_required_width_from_project_target():
    cyc = load_cycling_rules()
    t = cyc.widths_m["project_target"]
    assert pr.required_width("separated_oneway_both", "HAUPT", 0, 0, P) == t["separated_oneway"]["HAUPT"]
    assert pr.required_width("separated_twoway", "RSV", 0, 0, P) == t["separated_twoway"]["RSV"]
    assert pr.required_width("cycle_street", "HAUPT", 0, 0, P) == t["cycle_street_carriageway"]["value"]


def test_required_width_not_applicable():
    assert math.isnan(pr.required_width("mixed", "HAUPT", 0, 0, P))
    assert math.isnan(pr.required_width("cycle_lane", "RSV", 0, 0, P))  # no RSV target for cycle lanes


def test_required_width_intensity_upgrade():
    base = pr.required_width("separated_oneway_both", "HAUPT", 0, 0, P)
    (kind1, thr1, add1), = [u for u in P.intensity_upgrade if u[0] == "oneway"]
    assert pr.required_width("separated_oneway_both", "HAUPT", thr1 + 1, 0, P) == pytest.approx(base + add1)
    base2 = pr.required_width("separated_twoway", "HAUPT", 0, 0, P)
    (_, thr2, add2), = [u for u in P.intensity_upgrade if u[0] == "twoway"]
    assert pr.required_width("separated_twoway", "HAUPT", 0, thr2 + 1, P) == pytest.approx(base2 + add2)
    # a one-way facility ignores the two-way trigger
    assert pr.required_width("separated_oneway_both", "HAUPT", 0, thr2 + 1, P) == base


def test_lit_state():
    assert pr.lit_state("yes", P) is True
    assert pr.lit_state("no", P) is False
    assert pr.lit_state(None, P) is None
    assert pr.lit_state("weird", P) is None


def test_surface_score_depends_on_category():
    assert pr.surface_score("asphalt", "HAUPT", P) == 1.0
    assert pr.surface_score("paving_stones", "HAUPT", P) == 0.0
    assert pr.surface_score("paving_stones", "BASIS", P) == 1.0
    assert pr.surface_score("gravel", "BASIS", P) == 0.0
    assert math.isnan(pr.surface_score(None, "RSV", P))


def test_parse_upgrade():
    assert pr.parse_upgrade("oneway peak_h > 750") == ("oneway", 750.0)
    with pytest.raises(ValueError):
        pr.parse_upgrade("if it rains")


# --- stops and detour --------------------------------------------------------------------------


def test_route_stops_signals_and_give_way():
    # nodes 1-2-3-4; node 2 signal, node 3 touches a priority road, route edges are minor roads
    nodes = [1, 2, 3, 4]
    edge_prio = [False, False, False]
    interior = [0, 1, 0]
    signals, give_way = pr.route_stops(nodes, edge_prio, interior, signal_nodes={2}, priority_nodes={3, 9})
    assert signals == 2  # node 2 and one interior signal
    assert give_way == 1


def test_route_stops_give_way_at_route_end():
    # a minor-road route that ends at a main road (node 3) waits there
    _, give_way = pr.route_stops([1, 2, 3], [False, False], [0, 0], signal_nodes=set(), priority_nodes={3, 8})
    assert give_way == 1


def test_route_stops_on_priority_road_has_no_give_way():
    signals, give_way = pr.route_stops([1, 2, 3], [True, True], [0, 0], signal_nodes=set(), priority_nodes={1, 2, 3})
    assert (signals, give_way) == (0, 0)


def test_route_stops_signal_node_is_no_give_way():
    _, give_way = pr.route_stops([1, 2, 3], [False, False], [0, 0], signal_nodes={2}, priority_nodes={2})
    assert give_way == 0


def test_time_loss():
    assert pr.time_loss_s(2, 1, P) == pytest.approx(2 * P.signal_delay_s + P.give_way_delay_s)


def test_shortest_lengths_on_toy_graph():
    # square 1-2-3-4-1 with side 100 and a diagonal 1-3 of 141
    u = np.array([1, 2, 3, 4, 1])
    v = np.array([2, 3, 4, 1, 3])
    length = np.array([100, 100, 100, 100, 141.0])
    g = pr.length_graph(u, v, length)
    d = pr.shortest_lengths(g, [1], [3, 4])
    assert d[0] == pytest.approx([141.0, 100.0])
    g_sq = pr.length_graph(u[:4], v[:4], length[:4])
    assert pr.shortest_lengths(g_sq, [1], [3])[0][0] == pytest.approx(200.0)


def test_od_sample_respects_band_and_seed():
    rng_xy = np.random.default_rng(0).uniform(0, 10_000, size=(300, 2))
    ids = np.arange(300) + 1000
    pairs = pr.od_sample(rng_xy, ids, (2000.0, 3000.0), 50, seed=42)
    assert len(pairs) == 50
    pos = {n: i for i, n in enumerate(ids)}
    for a, b in pairs:
        d = np.hypot(*(rng_xy[pos[a]] - rng_xy[pos[b]]))
        assert 2000 <= d <= 3000
    assert pairs == pr.od_sample(rng_xy, ids, (2000.0, 3000.0), 50, seed=42)


# --- green -------------------------------------------------------------------------------------


def test_green_share_counts_overlaps_once():
    line = shapely.LineString([(0, 0), (100, 0)])
    park = shapely.box(-50, 0, 150, 50)  # covers the upper half of the buffer
    trees = [shapely.Point(50, 10), shapely.Point(50, -10)]  # one inside the park, one outside
    green = pr.prepare_green(np.array([park]), np.array(trees, dtype=object), crown_radius_m=4)
    share = pr.green_share(np.array([line]), green, buffer_m=20)
    buf = line.buffer(20)
    expected = (buf.intersection(park).area + shapely.Point(50, -10).buffer(4).area) / buf.area
    assert share[0] == pytest.approx(expected, rel=1e-3)


def test_green_share_zero_without_green():
    line = shapely.LineString([(0, 0), (100, 0)])
    green = pr.prepare_green(np.array([], dtype=object), np.array([], dtype=object), crown_radius_m=4)
    assert pr.green_share(np.array([line]), green, buffer_m=20)[0] == 0.0


# --- aggregation -------------------------------------------------------------------------------


def test_length_weighted_mean_ignores_unknown():
    mean, known = pr.weighted_mean(np.array([1.0, NAN, 0.0]), np.array([100.0, 100.0, 300.0]))
    assert mean == pytest.approx(0.25)
    assert known == pytest.approx(0.8)


def test_length_weighted_mean_all_unknown():
    mean, known = pr.weighted_mean(np.array([NAN, NAN]), np.array([1.0, 1.0]))
    assert math.isnan(mean) and known == 0.0


def test_principle_and_total_scores():
    checks = {"P-SAF-01": np.array([1.0, 0.0]), "P-SAF-03": np.array([0.5, NAN]), "P-DIR-01": np.array([NAN, NAN])}
    ps = pr.principle_scores(checks, P)
    assert ps["safety"][0] == pytest.approx(0.75)
    assert ps["safety"][1] == pytest.approx(0.0)
    assert np.isnan(ps["directness"]).all()
    total = pr.total_score(ps, P.weights)
    # only safety has a score: total = safety score (weights re-normalised)
    assert total == pytest.approx(ps["safety"])


def test_unknown_lowers_confidence_not_score():
    known = {c: np.array([1.0]) for c in P.check_principle}
    applicable = {c: np.array([True]) for c in P.check_principle}
    full = pr.confidence(known, applicable, P)[0]
    known["P-COM-01"] = np.array([0.0])
    less = pr.confidence(known, applicable, P)[0]
    assert less < full
    applicable["P-COM-01"] = np.array([False])  # not applicable: no penalty
    assert pr.confidence(known, applicable, P)[0] == pytest.approx(full)


def test_unavailable_checks_cap_confidence():
    known = {c: np.array([0.0 if c in P.unavailable else 1.0]) for c in P.check_principle}
    applicable = {c: np.array([True]) for c in P.check_principle}
    assert pr.confidence(known, applicable, P)[0] < 1.0


def test_confidence_class():
    assert pr.confidence_class(np.array([P.conf_high, P.conf_medium, 0.0]), P).tolist() == ["high", "medium", "low"]


def test_vary_weights_keeps_sum():
    for name in P.weights:
        for f in (1 - P.sens_delta, 1 + P.sens_delta):
            w = pr.vary_weights(P.weights, name, f)
            assert sum(w.values()) == pytest.approx(1.0)
            assert w[name] == pytest.approx(P.weights[name] * f)


def test_top_overlap():
    ids = np.array(["a", "b", "c", "d"])
    assert pr.top_overlap(np.array([4, 3, 2, 1.0]), np.array([4, 3, 2, 1.0]), ids, 2) == 2
    assert pr.top_overlap(np.array([4, 3, 2, 1.0]), np.array([1, 2, 3, 4.0]), ids, 2) == 0


def test_facility_changes():
    assert pr.facility_changes(["mixed", "mixed", "cycle_lane", None, "cycle_lane", "mixed"]) == 2
    assert pr.facility_changes([None, None]) == 0


def test_stratified_sample_is_reproducible_and_covers_categories():
    df = pd.DataFrame({"route_id": [f"r{i}" for i in range(100)], "category": ["RSV"] * 5 + ["HAUPT"] * 45 + ["BASIS"] * 50})
    a = pr.stratified_sample(df, "category", "route_id", 20, seed=42)
    assert len(a) == 20
    assert set(a["category"]) == {"RSV", "HAUPT", "BASIS"}
    assert a["route_id"].tolist() == pr.stratified_sample(df, "category", "route_id", 20, seed=42)["route_id"].tolist()


def test_soll_not_worse_than_ist_for_build_out_checks():
    # P-SAF-01, P-COM-01, P-COM-02, P-SAF-03 are 1 in Soll wherever they apply
    assert pr.facility_score("separated_oneway_both", "separated_oneway_both", None, P) >= \
        pr.facility_score("mixed", "separated_oneway_both", None, P)
    assert pr.score("ratio", 1.0, 1.0) >= pr.score("ratio", 0.5, 1.0)


# --- golden section cases (tests/golden/cycling/s*.geojson) ----------------------------------------


def _golden_sections():
    import json
    from pathlib import Path

    for path in sorted((Path(__file__).parent / "golden" / "cycling").glob("s*.geojson")):
        yield pytest.param(json.loads(path.read_text(encoding="utf-8"))["features"][0]["properties"], id=path.stem)


@pytest.mark.parametrize("props", list(_golden_sections()))
def test_soll_facility_matches_golden_cases(props):
    """P-SAF-01 Soll lookup: preferred facility when the space fits, otherwise the fallback (prompt 18 decides space)."""
    preferred, fallback = pr.soll_facility(props["cat_final"], props["cycle_cat"] or "none", P)
    expected = preferred if props.get("space_fits_preferred", True) or fallback is None else fallback
    assert expected == props["expected_facility"]
