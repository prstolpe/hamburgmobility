"""Expression evaluator for rule conditions (pipeline/lib/expr.py): parsing, three-valued logic, confidence."""

import math

import numpy as np
import pandas as pd
import pytest

from pipeline.lib import expr
from pipeline.lib.expr import HIGH, LOW, MEDIUM, Context

REFS = {"thresholds.t": 0.6, "required_width.GOW50": 16.5}


def ev(text: str, near: float = 0.1, fallback: set | None = None, **values):
    ctx = Context(values, REFS.__getitem__, near, fallback or set())
    return expr.evaluate(expr.parse(text), ctx)


# --- parsing ---------------------------------------------------------------------------------


@pytest.mark.parametrize("text", [
    "highway in [motorway, motorway_link, trunk] and access_motor_only",
    "outside_builtup_area",
    "ist_verkehrsberuhigt or pedestrian_zone or override_school_street",
    "conn_score >= thresholds.t or in_hvs",
    "a <= thresholds.t or b >= thresholds.t or crossing_demand == high",
    "not a and b < required_width.GOW50",
    "(a or b) and c",
])
def test_parses(text):
    expr.parse(text)


@pytest.mark.parametrize("text", ["a >=", "a and", "x.y > 1", "a in [b", "a == ", "(a or b"])
def test_rejects_broken(text):
    with pytest.raises(expr.ExprError):
        expr.parse(text)


def test_precedence_not_and_or():
    # a or (b and not c)
    assert ev("a or b and not c", a=False, b=True, c=False).value is True
    assert ev("a or b and not c", a=False, b=True, c=True).value is False
    assert ev("(a or b) and c", a=True, b=False, c=False).value is False


def test_word_after_equals_is_literal_and_list_items_are_literals():
    assert ev("crossing_demand == high", crossing_demand="high").value is True
    assert ev("crossing_demand == high", crossing_demand="low").value is False
    assert ev("highway in [motorway, trunk]", highway="trunk").value is True
    assert ev("highway in [motorway, trunk]", highway="primary").value is False


def test_features_in():
    node = expr.parse("highway in [motorway] and not x or y >= thresholds.t or d == high")
    assert expr.features_in(node) == {"highway", "x", "y", "d"}


# --- three-valued logic (C-MISS-01) ----------------------------------------------------------


@pytest.mark.parametrize("missing", [None, float("nan"), pd.NA, np.float64("nan")])
def test_missing_comparison_is_unknown_and_low(missing):
    r = ev("x >= thresholds.t", x=missing)
    assert r.value is None
    assert r.confidence == LOW
    assert "fehlt:x" in r.reasons


def test_kleene_or():
    assert ev("a or b", a=True, b=None).value is True
    assert ev("a or b", a=False, b=None).value is None
    assert ev("a or b", a=False, b=False).value is False


def test_kleene_and():
    assert ev("a and b", a=False, b=None).value is False
    assert ev("a and b", a=True, b=None).value is None
    assert ev("a and b", a=True, b=True).value is True


def test_not_unknown_stays_unknown():
    assert ev("not a", a=None).value is None


def test_unknown_feature_key_is_missing():
    assert ev("x > 1", ).value is None


# --- confidence (C-CONF-01) ------------------------------------------------------------------


def test_near_threshold_is_low():
    assert ev("x >= thresholds.t", x=0.6).confidence == LOW       # at
    assert ev("x >= thresholds.t", x=0.55).confidence == LOW      # -8 %
    assert ev("x >= thresholds.t", x=0.66).confidence == LOW      # +10 %
    assert ev("x >= thresholds.t", x=0.53).confidence == HIGH     # -12 %
    assert ev("x < required_width.GOW50", x=15.0).confidence == LOW
    assert ev("x < required_width.GOW50", x=14.0).confidence == HIGH


def test_near_threshold_comes_from_context():
    assert ev("x >= thresholds.t", near=0.0, x=0.55).confidence == HIGH


def test_literal_comparison_has_no_near_check():
    assert ev("x < 1.0", x=0.99).confidence == HIGH


def test_fallback_is_medium():
    r = ev("in_hvs", fallback={"in_hvs"}, in_hvs=True)
    assert (r.value, r.confidence, r.reasons) == (True, MEDIUM, ["fallback:in_hvs"])


def test_true_or_takes_best_true_operand():
    # A near-threshold school distance does not matter when frontage alone is clearly true.
    r = ev("s <= thresholds.t or f >= thresholds.t", s=0.59, f=0.9)
    assert r.value is True and r.confidence == HIGH and r.reasons == []


def test_true_or_with_only_weak_operands():
    r = ev("a or b", fallback={"a"}, a=True, b=None)
    assert r.value is True and r.confidence == MEDIUM


def test_false_or_takes_worst_operand():
    r = ev("a or x >= thresholds.t", fallback={"a"}, a=False, x=0.1)
    assert r.value is False and r.confidence == MEDIUM


def test_false_and_takes_best_false_operand():
    r = ev("a and b", fallback={"a"}, a=False, b=False)
    assert r.value is False and r.confidence == HIGH


def test_unknown_result_is_low():
    r = ev("a or b", a=False, b=None)
    assert r.confidence == LOW and "fehlt:b" in r.reasons


def test_inputs_are_recorded():
    ctx = Context({"a": False, "b": None}, REFS.__getitem__, 0.1)
    expr.evaluate(expr.parse("a or b"), ctx)
    assert ctx.used == {"a": False, "b": None}


def test_clean_value():
    assert expr.clean_value(np.bool_(True)) is True
    assert expr.clean_value(np.float64(0.123456)) == 0.1235
    assert expr.clean_value(math.nan) is None
    assert expr.clean_value(pd.NA) is None
    assert expr.clean_value("x") == "x"
