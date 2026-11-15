"""Harmonisation along streets (H-STR-01) in pipeline/lib/harmonise.py."""

import pytest

from pipeline.lib.harmonise import harmonise
from pipeline.lib.rules import load_rules

RULES = load_rules()
MIN_RUN = RULES.coherence_rule("N2").param("min_run_m")  # 200 m


def run(cats_lengths: list[tuple[str, float]], locked=()) -> tuple[list[str], dict]:
    """One stroke s0, s1, ... with the given categories and lengths; returns new categories in order and trace."""
    ids = [f"s{i}" for i in range(len(cats_lengths))]
    cats = {sid: c for sid, (c, _) in zip(ids, cats_lengths)}
    lengths = {sid: m for sid, (_, m) in zip(ids, cats_lengths)}
    new, trace = harmonise([ids], cats, lengths, RULES, locked=set(locked))
    return [new[s] for s in ids], trace


def test_rule_found():
    rule = RULES.harmonisation.rule("H-STR-01")
    assert rule.source_type == "assumption" and rule.min_run_from == "N2"
    assert {"SW", "ETW_ERF"} <= set(rule.locked_categories)
    # rules.yaml 0.24.0: sections decided by the traffic-volume cap are not harmonised
    assert "C-G50-02" in rule.locked_rules and "C-G50-02" in RULES.harmonisation.rule("H-PAIR-01").locked_rules


# --- step 1/2: ETW30 <-> GOW ------------------------------------------------------------------


def test_etw30_island_in_gow_becomes_gow():
    cats, trace = run([("GOW50", 300), ("ETW30", 80), ("GOW50", 300)])
    assert cats == ["GOW50", "GOW50", "GOW50"]
    step = trace["s1"][0]
    assert step["from"] == "ETW30" and step["to"] == "GOW50" and step["step"] == 1


def test_etw30_island_between_mixed_gow_takes_lower_speed():
    cats, _ = run([("GOW50", 300), ("ETW30", 80), ("GOW30", 300)])
    assert cats == ["GOW50", "GOW30", "GOW30"]


def test_long_etw30_run_stays():
    cats, trace = run([("GOW50", 300), ("ETW30", MIN_RUN), ("GOW50", 300)])
    assert cats == ["GOW50", "ETW30", "GOW50"] and trace == {}


def test_gow_island_in_etw30_becomes_etw30():
    cats, _ = run([("ETW30", 300), ("GOW30", 60), ("GOW50", 50), ("ETW30", 300)])
    assert cats == ["ETW30", "ETW30", "ETW30", "ETW30"]


# --- step 3: GOW50 in GOW30 -------------------------------------------------------------------


def test_gow50_island_in_gow30_becomes_gow30():
    cats, trace = run([("GOW30", 400), ("GOW50", 120), ("GOW30", 400)])
    assert cats == ["GOW30"] * 3
    assert trace["s1"][0]["step"] == 3 and trace["s1"][0]["run_m"] == pytest.approx(120)


def test_gow50_stub_at_end_next_to_gow30():
    cats, _ = run([("GOW30", 400), ("GOW50", 90)])
    assert cats == ["GOW30", "GOW30"]


GAP_CLOSE = RULES.harmonisation.rule("H-STR-01").thresholds["gap_close_m"].value  # 500 m (F07)


def test_gow50_gap_below_gap_close_between_gow30_is_closed():
    """F07: a GOW50 gap shorter than gap_close_m between two GOW30 runs becomes GOW30 (StVO gap closing)."""
    assert GAP_CLOSE > MIN_RUN
    cats, trace = run([("GOW30", 400), ("GOW50", 250), ("GOW30", 400)])
    assert cats == ["GOW30", "GOW30", "GOW30"]
    assert trace["s1"][0]["step"] == 3
    cats, _ = run([("GOW30", 400), ("GOW50", GAP_CLOSE - 1), ("GOW30", 400)])
    assert cats == ["GOW30", "GOW30", "GOW30"]


def test_long_gow50_between_gow30_stays():
    cats, _ = run([("GOW30", 400), ("GOW50", GAP_CLOSE), ("GOW30", 400)])
    assert cats == ["GOW30", "GOW50", "GOW30"]


def test_gap_close_does_not_apply_at_street_end():
    """At the end of the street only min_run_m applies (no gap between two Tempo-30 stretches)."""
    cats, _ = run([("GOW30", 400), ("GOW50", 250)])
    assert cats == ["GOW30", "GOW50"]


# --- step 4: short GOW30 in GOW50 becomes GOW50 (rules.yaml 0.24.0) ----------------------------


def test_short_gow30_in_gow50_becomes_gow50():
    cats, trace = run([("GOW50", 500), ("GOW30", 80), ("GOW30", 70), ("GOW50", 500)])
    assert cats == ["GOW50"] * 4
    assert trace["s1"][0]["step"] == 4 and trace["s1"][0]["to"] == "GOW50"


def test_gow30_stub_at_end_next_to_gow50_becomes_gow50():
    cats, _ = run([("GOW30", 50), ("GOW50", 500)])
    assert cats == ["GOW50", "GOW50"]


def test_long_gow30_in_gow50_stays():
    cats, trace = run([("GOW50", 500), ("GOW30", MIN_RUN), ("GOW50", 500)])
    assert cats == ["GOW50", "GOW30", "GOW50"] and trace == {}


# --- what is never changed ---------------------------------------------------------------------


@pytest.mark.parametrize("middle", ["SW", "ETW_ERF"])
def test_locked_categories_untouched(middle):
    cats, _ = run([("GOW50", 300), (middle, 50), ("GOW50", 300)])
    assert cats[1] == middle


def test_locked_segments_untouched():
    cats, _ = run([("GOW30", 400), ("GOW50", 120), ("GOW30", 400)], locked={"s1"})
    assert cats == ["GOW30", "GOW50", "GOW30"]


def test_locked_gow30_island_stays():
    cats, _ = run([("GOW50", 500), ("GOW30", 80), ("GOW50", 500)], locked={"s1"})
    assert cats == ["GOW50", "GOW30", "GOW50"]


def test_locked_gow50_gap_between_gow30_stays():
    """rules.yaml 0.24.0: C-G50-02 sections are locked, gap closing must not turn them into GOW30."""
    cats, _ = run([("GOW30", 400), ("GOW50", 250), ("GOW30", 400)], locked={"s1"})
    assert cats == ["GOW30", "GOW50", "GOW30"]


def test_segments_outside_strokes_keep_their_category():
    new, trace = harmonise([["a", "b", "c"]], {"a": "GOW30", "b": "GOW50", "c": "GOW30", "x": "GOW50"},
                           {"a": 400, "b": 50, "c": 400, "x": 10}, RULES)
    assert new == {"a": "GOW30", "b": "GOW30", "c": "GOW30", "x": "GOW50"}
    assert set(trace) == {"b"}


def test_stable_input_is_a_fixpoint():
    cats = [("GOW50", 300), ("ETW30", 80), ("GOW30", 120), ("GOW50", 90), ("GOW30", 500)]
    first, _ = run(cats)
    second, trace = run([(c, m) for c, (_, m) in zip(first, cats)])
    assert second == first and trace == {}


# --- H-PAIR-01: separately mapped carriageways get the same speed --------------------------------

import geopandas as gpd  # noqa: E402
from shapely.geometry import LineString  # noqa: E402

from pipeline.lib.harmonise import carriageway_pairs, pair_carriageways  # noqa: E402

PAIR = RULES.harmonisation.rule("H-PAIR-01")
MAX_DIST = PAIR.thresholds["pair_max_distance_m"].value


def seg(rows: list[tuple]) -> gpd.GeoDataFrame:
    """rows: (segment_id, name, oneway, node_u, node_v, LineString)."""
    return gpd.GeoDataFrame([dict(zip(["segment_id", "name", "oneway", "node_u", "node_v"], r[:5])) for r in rows],
                            geometry=[r[5] for r in rows], crs=25832)


def dual(offset: float = 15.0, name_b: str = "Hauptstraße", oneway_b=True, nodes_b=(3, 4)):
    return seg([("a", "Hauptstraße", True, 1, 2, LineString([(0, 0), (300, 0)])),
                ("b", name_b, oneway_b, *nodes_b, LineString([(300, offset), (0, offset)]))])


def test_pair_rule_found():
    assert PAIR.source_type == "assumption" and PAIR.status == "draft"
    assert {"pair_max_distance_m", "pair_max_angle_deg", "pair_min_overlap_share"} <= set(PAIR.thresholds)
    assert set(PAIR.locked_categories) == set(RULES.harmonisation.rule("H-STR-01").locked_categories)


def test_dual_carriageway_is_paired():
    pairs = carriageway_pairs(dual(), RULES)
    assert [(p["a"], p["b"]) for p in pairs] == [("a", "b")]
    assert pairs[0]["dist_m"] == pytest.approx(15) and pairs[0]["overlap_share"] == pytest.approx(1)


@pytest.mark.parametrize("kwargs", [
    {"offset": MAX_DIST + 1},              # too far apart
    {"name_b": "Nebenstraße"},             # different street
    {"oneway_b": False},                   # two-way road next to a one-way road
    {"oneway_b": None},                    # oneway unknown
    {"nodes_b": (2, 4)},                   # consecutive segments of one carriageway share a node
])
def test_no_pair(kwargs):
    assert carriageway_pairs(dual(**kwargs), RULES) == []


def test_crossing_short_segment_is_no_pair():
    """Close and overlapping, but at 45 degrees: a crossing or a ramp, not the other carriageway."""
    s = seg([("a", "Hauptstraße", True, 1, 2, LineString([(0, 0), (300, 0)])),
             ("b", "Hauptstraße", True, 3, 4, LineString([(130, -3), (165, 32)]))])
    assert carriageway_pairs(s, RULES) == []


def test_consecutive_segments_without_overlap_are_no_pair():
    s = seg([("a", "Hauptstraße", True, 1, 2, LineString([(0, 0), (300, 0)])),
             ("b", "Hauptstraße", True, 3, 4, LineString([(310, 10), (600, 10)]))])
    assert carriageway_pairs(s, RULES) == []


def test_pair_lower_speed_wins():
    pairs = carriageway_pairs(dual(), RULES)
    new, trace = pair_carriageways(pairs, {"a": "GOW50", "b": "GOW30"}, RULES)
    assert new == {"a": "GOW30", "b": "GOW30"}
    step = trace["a"][0]
    assert step["id"] == "H-PAIR-01" and step["from"] == "GOW50" and step["to"] == "GOW30" and step["partner"] == "b"
    assert "b" not in trace


def test_pair_equal_or_not_gow_unchanged():
    pairs = carriageway_pairs(dual(), RULES)
    for cats in ({"a": "GOW50", "b": "GOW50"}, {"a": "GOW50", "b": "ETW30"}, {"a": "SW", "b": "GOW30"}):
        new, trace = pair_carriageways(pairs, cats, RULES)
        assert new == cats and trace == {}


def test_pair_locked_gow50_raises_partner():
    """A locked GOW50 (C-G50-02 or override) cannot go down: the free GOW30 partner becomes GOW50."""
    pairs = carriageway_pairs(dual(), RULES)
    new, trace = pair_carriageways(pairs, {"a": "GOW50", "b": "GOW30"}, RULES, locked={"a"})
    assert new == {"a": "GOW50", "b": "GOW50"}
    assert trace["b"][0]["to"] == "GOW50" and trace["b"][0]["partner"] == "a" and "a" not in trace


def test_pair_both_locked_untouched():
    pairs = carriageway_pairs(dual(), RULES)
    new, trace = pair_carriageways(pairs, {"a": "GOW50", "b": "GOW30"}, RULES, locked={"a", "b"})
    assert new == {"a": "GOW50", "b": "GOW30"} and trace == {}


def test_pair_chain_propagates():
    """A long carriageway paired with two shorter ones on the other side: 30 spreads over the chain."""
    s = seg([("a", "Allee", True, 1, 2, LineString([(0, 0), (200, 0)])),
             ("b", "Allee", True, 3, 4, LineString([(400, 12), (0, 12)])),
             ("c", "Allee", True, 5, 6, LineString([(200, 0), (400, 0)]))])
    new, _ = pair_carriageways(carriageway_pairs(s, RULES), {"a": "GOW30", "b": "GOW50", "c": "GOW50"}, RULES)
    assert new == {"a": "GOW30", "b": "GOW30", "c": "GOW30"}


def test_harmonise_all_pairs_then_smooths_along_the_street():
    """The paired 30 on carriageway b leaves a short 50 stub on b's street, which H-STR-01 then closes."""
    from pipeline.lib.harmonise import harmonise_all
    s = seg([("a", "Allee", True, 1, 2, LineString([(0, 0), (300, 0)])),
             ("b", "Allee", True, 3, 4, LineString([(300, 15), (0, 15)]))])
    cats = {"a": "GOW30", "b": "GOW50", "x": "GOW30", "y": "GOW50"}
    lengths = {"a": 300, "b": 300, "x": 400, "y": 120}
    new, trace = harmonise_all([["x", "b", "y"]], carriageway_pairs(s, RULES), cats, lengths, RULES)
    assert new == {"a": "GOW30", "b": "GOW30", "x": "GOW30", "y": "GOW30"}
    assert [t["id"] for t in trace["b"]] == ["H-PAIR-01"] and [t["id"] for t in trace["y"]] == ["H-STR-01"]


def test_harmonise_all_pairing_is_not_undone_by_street_smoothing():
    """Locked GOW50 (C-G50-02) on a raises partner b; b's own street would close the 50 gap again (step 3).
    The pairing result wins: b stays GOW50, the pair stays consistent and the loop terminates."""
    from pipeline.lib.harmonise import harmonise_all
    s = seg([("a", "Allee", True, 1, 2, LineString([(0, 0), (300, 0)])),
             ("b", "Allee", True, 3, 4, LineString([(300, 15), (0, 15)]))])
    cats = {"a": "GOW50", "b": "GOW30", "x": "GOW30", "y": "GOW30"}
    lengths = {"a": 300, "b": 300, "x": 400, "y": 400}
    new, _ = harmonise_all([["x", "b", "y"]], carriageway_pairs(s, RULES), cats, lengths, RULES, locked={"a"})
    assert new["a"] == new["b"] == "GOW50"


def test_pair_chain_locked_gow50_holds_and_raises_along_the_chain():
    """b (GOW50) lies between locked a (GOW50) and c (GOW30): b is held at 50, c is raised, no pair stays mixed."""
    s = seg([("a", "Wall", True, 1, 2, LineString([(0, 0), (200, 0)])),
             ("b", "Wall", True, 3, 4, LineString([(400, 12), (0, 12)])),
             ("c", "Wall", True, 5, 6, LineString([(200, 0), (400, 0)]))])
    new, _ = pair_carriageways(carriageway_pairs(s, RULES), {"a": "GOW50", "b": "GOW50", "c": "GOW30"}, RULES, locked={"a"})
    assert new == {"a": "GOW50", "b": "GOW50", "c": "GOW50"}
