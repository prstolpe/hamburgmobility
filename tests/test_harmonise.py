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


def test_long_gow50_between_gow30_stays():
    cats, _ = run([("GOW30", 400), ("GOW50", 250), ("GOW30", 400)])
    assert cats == ["GOW30", "GOW50", "GOW30"]


# --- step 4: GOW30 in GOW50 is kept and extended ----------------------------------------------


def test_short_gow30_in_gow50_is_extended_shorter_neighbour_first():
    cats, trace = run([("GOW50", 500), ("GOW50", 60), ("GOW30", 80), ("GOW50", 70), ("GOW50", 500)])
    # 80 + 60 (shorter neighbour) = 140 < 200 -> + 70 = 210
    assert cats == ["GOW50", "GOW30", "GOW30", "GOW30", "GOW50"]
    assert trace["s1"][0]["step"] == 4 and trace["s3"][0]["step"] == 4


def test_gow30_at_end_next_to_gow50_is_extended():
    cats, _ = run([("GOW30", 50), ("GOW50", 170), ("GOW50", 500)])
    assert cats == ["GOW30", "GOW30", "GOW50"]


def test_extension_then_island_becomes_gow30():
    # extending the 30 leaves a 50-island of 100 m between two 30 runs -> step 3 in the next pass
    cats, _ = run([("GOW30", 400), ("GOW50", 100), ("GOW50", 150), ("GOW30", 100), ("GOW50", 600)])
    assert cats[:4] == ["GOW30"] * 4


# --- what is never changed ---------------------------------------------------------------------


@pytest.mark.parametrize("middle", ["SW", "ETW_ERF"])
def test_locked_categories_untouched(middle):
    cats, _ = run([("GOW50", 300), (middle, 50), ("GOW50", 300)])
    assert cats[1] == middle


def test_locked_segments_untouched():
    cats, _ = run([("GOW30", 400), ("GOW50", 120), ("GOW30", 400)], locked={"s1"})
    assert cats == ["GOW30", "GOW50", "GOW30"]


def test_locked_segment_stops_extension():
    cats, _ = run([("GOW50", 500), ("GOW50", 60), ("GOW30", 80), ("GOW50", 70)], locked={"s1", "s3"})
    assert cats == ["GOW50", "GOW50", "GOW30", "GOW50"]


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
