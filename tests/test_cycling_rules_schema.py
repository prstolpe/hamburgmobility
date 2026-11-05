"""Schema tests for config/cycling_rules.yaml and config/design_rules.yaml (prompts/14).

Every rule and every number needs source_type (inherited from the nearest parent entry), a
source unless it is an assumption, a status for rules with an id, unique ids and valid categories.
"""

import copy

import pytest
import yaml
from pydantic import ValidationError

from config.schema.cycling_model import CYCLE_CATEGORIES, FACILITIES, CyclingRuleSet
from config.schema.design_model import DesignRuleSet
from config.schema.provenance import META_KEYS
from config.schema.rules_model import EXPECTED_CATEGORIES
from pipeline.lib.rules import (
    DEFAULT_CYCLING_RULES_PATH,
    DEFAULT_DESIGN_RULES_PATH,
    all_rule_ids,
    load_cycling_rules,
    load_design_rules,
    load_rules,
)


def _raw(path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def cyc() -> dict:
    return _raw(DEFAULT_CYCLING_RULES_PATH)


@pytest.fixture(scope="module")
def des() -> dict:
    return _raw(DEFAULT_DESIGN_RULES_PATH)


def _mutated(raw: dict, mutate) -> dict:
    data = copy.deepcopy(raw)
    mutate(data)
    return data


def _by_id(rows: list[dict], rule_id: str) -> dict:
    return next(r for r in rows if r.get("id") == rule_id)


# --- the real files --------------------------------------------------------------------------


def test_cycling_rules_yaml_is_valid():
    rules = load_cycling_rules()
    assert rules.meta.crs_work == "EPSG:25832"
    assert set(rules.cycle_categories) == CYCLE_CATEGORIES


def test_design_rules_yaml_is_valid():
    rules = load_design_rules()
    assert rules.meta.crs_work == "EPSG:25832"
    assert len(rules.junctions.decision_table.rows) >= 11


def test_rule_ids_unique_across_all_rule_files():
    ids = all_rule_ids(load_rules(), load_cycling_rules(), load_design_rules())
    assert len(ids) == len(set(ids)), sorted({i for i in ids if ids.count(i) > 1})


def test_facility_list_matches_matrix_note():
    note = load_cycling_rules().separation_matrix["note"]
    listed = {f.strip() for f in note.split(":", 1)[1].split("|")}
    assert listed == FACILITIES


def test_lane_defaults_cover_all_road_categories():
    defaults = load_design_rules().lanes.default_per_direction
    assert set(defaults) - META_KEYS == EXPECTED_CATEGORIES


def test_every_junction_threshold_is_used():
    rules = load_design_rules()
    text = " ".join(str(r.model_dump()) for r in rules.junctions.decision_table.rows)
    for name in rules.junctions.thresholds:
        assert name in text, name


# --- the schemas reject broken files ---------------------------------------------------------


def _rejects(model, data, match: str):
    with pytest.raises(ValidationError, match=match):
        model.model_validate(data)


def test_rejects_number_without_source_type(cyc):
    data = _mutated(cyc, lambda d: d["routing_impedance"].pop("source_type"))
    _rejects(CyclingRuleSet, data, "source_type")


def test_rejects_source_missing_for_non_assumption(cyc):
    def mutate(d):
        d["demand"]["peak_hour_share_of_day"].pop("source")
    _rejects(CyclingRuleSet, _mutated(cyc, mutate), "source missing")


def test_rejects_unknown_source(cyc):
    def mutate(d):
        d["cycle_categories"]["RSV"]["demand_trigger_cyclists_weekday"]["source"] = "NOPE_2099"
    _rejects(CyclingRuleSet, _mutated(cyc, mutate), "unknown source")


def test_rejects_rule_without_status(cyc):
    def mutate(d):
        _by_id(d["separation_matrix"]["rules"], "S-01").pop("status")
    _rejects(CyclingRuleSet, _mutated(cyc, mutate), "status")


def test_rejects_duplicate_id(cyc):
    def mutate(d):
        _by_id(d["separation_matrix"]["rules"], "S-02")["id"] = "S-01"
    _rejects(CyclingRuleSet, _mutated(cyc, mutate), "duplicate")


def test_rejects_unknown_facility(cyc):
    def mutate(d):
        d["separation_matrix"]["GOW50"]["HAUPT"] = "painted_dream"
    _rejects(CyclingRuleSet, _mutated(cyc, mutate), "facility")


def test_rejects_unknown_cycle_category_in_matrix(cyc):
    def mutate(d):
        d["separation_matrix"]["GOW30"]["VELO"] = "cycle_lane"
    _rejects(CyclingRuleSet, _mutated(cyc, mutate), "cycle categor")


def test_rejects_matrix_missing_road_category(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["separation_matrix"].pop("ETW30")), "ETW30")


def test_rejects_weights_not_matching_principles(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["principle_weights"].pop("comfort")), "principle_weights")


def test_rejects_unknown_junction_type(des):
    def mutate(d):
        _by_id(d["junctions"]["decision_table"]["rows"], "J-06")["then"] = "magic_roundabout"
    _rejects(DesignRuleSet, _mutated(des, mutate), "junction type")


def test_rejects_unknown_name_in_junction_condition(des):
    def mutate(d):
        _by_id(d["junctions"]["decision_table"]["rows"], "J-09")["if"] = "entering_dtv_sum > tunnel_min_dtv"
    _rejects(DesignRuleSet, _mutated(des, mutate), "tunnel_min_dtv")


def test_rejects_unknown_same_as(des):
    def mutate(d):
        _by_id(d["junctions"]["decision_table"]["rows"], "J-02")["same_as"] = "J-99"
    _rejects(DesignRuleSet, _mutated(des, mutate), "J-99")


def test_rejects_unknown_category_in_lane_defaults(des):
    def mutate(d):
        d["lanes"]["default_per_direction"]["GOW70"] = 1
    _rejects(DesignRuleSet, _mutated(des, mutate), "GOW70")


def test_rejects_design_number_without_source_type(des):
    def mutate(d):
        d["junctions"]["thresholds"]["turbo_max_dtv"].pop("source_type")
    _rejects(DesignRuleSet, _mutated(des, mutate), "source_type")


# --- prompt 15: cycle graph, Ist impedance mapping, demand model ------------------------------


def _imp_rules(d):
    return d["routing_impedance"]["ist_mapping"]["rules"]


def _dem(d, rule_id):
    return _by_id(d["demand_model"]["rules"], rule_id)


def test_ist_mapping_covers_every_condition(cyc):
    from config.schema.cycling_model import IMPEDANCE_CONDITIONS
    assert {r["when"] for r in _imp_rules(cyc)} == IMPEDANCE_CONDITIONS


def test_ist_mapping_ends_with_catch_all(cyc):
    plain = [r for r in _imp_rules(cyc) if "factor" in r]
    assert plain[-1]["when"] == "other"


def test_rejects_unknown_impedance_factor(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _imp_rules(d)[0].update(factor="nonsense")), "unknown factor")


def test_rejects_unknown_impedance_condition(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _imp_rules(d)[0].update(when="sunny")), "unknown condition")


def test_rejects_unknown_assignment_method(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _dem(d, "C-DEM-05").update(method="magic")), "assignment method")


def test_rejects_destination_weights_not_summing_to_one(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _dem(d, "C-DEM-02")["weights"].update(shops=0.9)), "sum to 1")


def test_rejects_unknown_destination_type(cyc):
    def mutate(d):
        w = _dem(d, "C-DEM-02")["weights"]
        w["bakeries"] = w.pop("shops")
    _rejects(CyclingRuleSet, _mutated(cyc, mutate), "destination types")


def test_rejects_reversed_distance_band(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _dem(d, "C-DEM-04").update(distance_band_km=[15, 0.5])), "distance_band_km")


def test_rejects_demand_rule_missing(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["demand_model"]["rules"].pop()), "C-DEM-07")


def test_rejects_new_section_without_source_type(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["cycle_graph"].pop("source_type")), "source_type missing")
