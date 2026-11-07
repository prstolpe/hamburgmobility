"""Cascade interpreter (pipeline/lib/classify.py) and stage helpers (pipeline/s05_classify.py) beyond the golden cases."""

import copy
import json

import pandas as pd
import pytest
import yaml
from pydantic import ValidationError

from config.schema.rules_model import RuleSet
from pipeline.lib.classify import classify_segment
from pipeline.lib.rules import DEFAULT_RULES_PATH, load_rules
from pipeline.lib.rules import all_thresholds
from pipeline.s05_classify import classification_inputs, classify_frame

RULES = load_rules()
RULES_THRESHOLDS = {n: t.value for n, t in all_thresholds(RULES).items()}

# A plain urban street with all inputs present (no fallback-dependent outcome except the policy defaults).
BASE = {
    "highway": "residential", "access_motor_only": False, "outside_builtup_area": False, "conn_score": 0.2,
    "conn_weight_available": 1.0, "in_hvs": False, "ist_verkehrsberuhigt": False, "pedestrian_zone": False,
    "override_school_street": False, "schools_or_kitas_within_m": 600.0, "shop_frontage_share": 0.1,
    "crossing_demand": "low", "separated_cycle_track_present": True, "width_p10_m": 25.0, "dtv_official": None,
}
GOW = {**BASE, "highway": "primary", "conn_score": 0.9, "in_hvs": True, "dtv_official": 8000.0}  # HVS always has a count


def run(**changes):
    return classify_segment({**BASE, **changes}, RULES)


def step(result, rule_id):
    return next(s for s in result["rule_trace"] if s["id"] == rule_id and "part" not in s)


def test_result_shape():
    r = run()
    assert set(r) == {"cat_proposed", "confidence", "confidence_reasons", "defaults_used", "rule_trace"}
    assert r["cat_proposed"] == "ETW30"
    json.dumps(r["rule_trace"])  # serialisable
    for s in r["rule_trace"]:
        assert {"id", "passed", "result", "inputs", "confidence"} <= set(s)


def test_in_hvs_fallback_makes_etw30_medium():
    r = run()
    assert r["confidence"] == "mittel"
    assert "fallback:in_hvs" in r["confidence_reasons"]


def test_defaults_for_missing_policy_inputs():
    r = run(outside_builtup_area=None, override_school_street=None, crossing_demand=None)
    assert r["cat_proposed"] == "ETW30"
    assert set(r["defaults_used"]) == {"outside_builtup_area", "override_school_street", "crossing_demand"}
    assert step(r, "C-RUR-01")["inputs"]["outside_builtup_area"] is False
    assert "fallback:outside_builtup_area" in r["confidence_reasons"]
    assert r["confidence"] == "mittel"


def test_default_is_not_used_when_value_present():
    r = run(outside_builtup_area=True, conn_score=0.9)
    assert r["cat_proposed"] == "GOW80"
    assert "outside_builtup_area" not in r["defaults_used"]


def test_missing_trigger_input_gives_gow50_low():
    # Frontage unknown, other GOW30 triggers false: C-G30-01 is unknown, not passed -> GOW50, low.
    r = classify_segment({**GOW, "shop_frontage_share": None}, RULES)
    assert r["cat_proposed"] == "GOW50"
    assert step(r, "C-G30-01")["result"] is None and step(r, "C-G30-01")["passed"] is False
    assert r["confidence"] == "niedrig"
    assert "fehlt:shop_frontage_share" in r["confidence_reasons"]


def test_missing_input_does_not_matter_when_other_part_is_true():
    r = classify_segment({**GOW, "shop_frontage_share": None, "schools_or_kitas_within_m": 50.0}, RULES)
    assert r["cat_proposed"] == "GOW30"
    assert "fehlt:shop_frontage_share" not in r["confidence_reasons"]


def test_missing_width_without_track_gives_unknown_g30_02():
    r = classify_segment({**GOW, "separated_cycle_track_present": False, "width_p10_m": None}, RULES)
    assert step(r, "C-G30-02")["result"] is None
    assert r["cat_proposed"] == "GOW50" and r["confidence"] == "niedrig"


def test_missing_width_with_track_is_still_false():
    # not track = False decides the and; width does not matter.
    r = classify_segment({**GOW, "width_p10_m": None}, RULES)
    assert step(r, "C-G30-02")["result"] is False
    assert "fehlt:width_p10_m" not in r["confidence_reasons"]


def test_missing_conn_score_in_rural_then_uses_else_branch_low():
    r = run(outside_builtup_area=True, conn_score=None)
    assert r["cat_proposed"] == "ETW60" and r["confidence"] == "niedrig"


def test_conn_score_fallback_when_weight_redistributed():
    r = classify_segment({**GOW, "in_hvs": False, "conn_weight_available": 0.8}, RULES)
    assert "fallback:conn_score" in r["confidence_reasons"]
    r = classify_segment({**GOW, "in_hvs": False, "conn_weight_available": 1.0}, RULES)
    assert "fallback:conn_score" not in r["confidence_reasons"]


def test_motorway_is_high_confidence():
    r = run(highway="motorway", access_motor_only=True)
    assert (r["cat_proposed"], r["confidence"]) == ("SW", "hoch")


def test_trace_lists_all_gow_triggers_and_rule_path():
    r = classify_segment({**GOW, "schools_or_kitas_within_m": 50.0, "separated_cycle_track_present": False,
                          "width_p10_m": 10.0}, RULES)
    passed = [s["id"] for s in r["rule_trace"] if s["passed"]]
    assert passed == ["C-GOW-01", "C-G30-01", "C-G30-02"]


def test_classify_frame_columns_and_index():
    df = pd.DataFrame([BASE, {**GOW, "shop_frontage_share": None}], index=[10, 11])
    out = classify_frame(df, RULES)
    assert list(out.index) == [10, 11]
    assert list(out["cat_proposed"]) == ["ETW30", "GOW50"]
    assert list(out["rule_path"]) == ["C-ETW-01", "C-GOW-01 → C-G50-01"]
    assert isinstance(json.loads(out["rule_trace"].iloc[0]), list)


def test_classify_frame_requires_inputs():
    with pytest.raises(KeyError):
        classify_frame(pd.DataFrame([{"highway": "residential"}]), RULES)


def test_classification_inputs_include_policy_columns():
    assert {"conn_weight_available", "outside_builtup_area", "width_p10_m"} <= set(classification_inputs(RULES))


# --- schema for classification_policy -------------------------------------------------------


@pytest.fixture(scope="module")
def raw() -> dict:
    with open(DEFAULT_RULES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_policy_needs_near_threshold(raw):
    data = copy.deepcopy(raw)
    for p in data["classification_policy"]:
        p.pop("thresholds", None)
    with pytest.raises(ValidationError, match="near_threshold"):
        RuleSet.model_validate(data)


def test_policy_needs_source_type(raw):
    data = copy.deepcopy(raw)
    del data["classification_policy"][0]["source_type"]
    with pytest.raises(ValidationError):
        RuleSet.model_validate(data)


def test_policy_ids_must_not_clash(raw):
    data = copy.deepcopy(raw)
    data["classification_policy"][0]["id"] = "C-SW-01"
    with pytest.raises(ValidationError, match="duplicate"):
        RuleSet.model_validate(data)


def test_gow30_cap_on_main_roads_only():
    # rules.yaml 0.14.0: school trigger only up to gow30_max_dtv on HVS; above -> GOW50 via C-G50-02
    cap = RULES_THRESHOLDS["gow30_max_dtv"]
    near_school = {**GOW, "schools_or_kitas_within_m": 50.0}
    assert classify_segment({**near_school, "dtv_official": cap}, RULES)["cat_proposed"] == "GOW30"
    above = classify_segment({**near_school, "dtv_official": cap + 1}, RULES)
    assert above["cat_proposed"] == "GOW50" and step(above, "C-G50-02")["passed"]
    # not a main road: no count, the cap does not apply
    off_hvs = classify_segment({**near_school, "in_hvs": False, "dtv_official": None}, RULES)
    assert off_hvs["cat_proposed"] == "GOW30"
