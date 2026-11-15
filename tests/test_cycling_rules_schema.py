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
        _by_id(d["junctions"]["decision_table"]["rows"], "J-10b")["same_as"] = "J-99"
    _rejects(DesignRuleSet, _mutated(des, mutate), "J-99")


def test_rejects_unknown_cycle_crossing_category(des):
    # Review 2026-11 F03: J-14 cycle_crossing lists cycle categories
    def mutate(d):
        _by_id(d["junctions"]["decision_table"]["rows"], "J-14")["cycle_crossing"] = ["HAUPT", "MAIN"]
    _rejects(DesignRuleSet, _mutated(des, mutate), "cycle_crossing")


def test_rejects_treatment_flag_without_categories(des):
    # Review 2026-11 F02: JC-06 flag needs flag_cycle_cats
    def mutate(d):
        _by_id(d["junctions"]["cyclist_treatment"], "JC-06").pop("flag_cycle_cats")
    _rejects(DesignRuleSet, _mutated(des, mutate), "flag_cycle_cats")


def test_rejects_fallback_condition_for_unknown_type(des):
    def mutate(d):
        _by_id(d["junctions"]["method"], "J-M-05")["fallback_if"]["condition_by_type"]["signal_protected"] = "space_radius_m < 1"
    _rejects(DesignRuleSet, _mutated(des, mutate), "condition_by_type")


def test_rejects_missing_signal_radius(des):
    # Review 2026-11 F09: signal_radius_m moved from rules.yaml N6 to J-M-06
    def mutate(d):
        _by_id(d["junctions"]["method"], "J-M-06").pop("signal_radius_m")
    _rejects(DesignRuleSet, _mutated(des, mutate), "signal_radius_m")


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


# --- network_design (prompts/16) -------------------------------------------------------------


def _net(d: dict, rule_id: str) -> dict:
    return _by_id(d["network_design"]["rules"], rule_id)


def test_network_rule_missing(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["network_design"]["rules"].pop()), "C-NET-13")


def test_rejects_unknown_soll_factor(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _net(d, "C-NET-03")["soll_factor_by_facility"].update(mixed="fast")),
             "unknown factors")


def test_rejects_unknown_soll_factor_key(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _net(d, "C-NET-03")["soll_factor_by_category"].update(GOW99="etw30_mixed")),
             "unknown soll_factor_by_category keys")


def test_soll_factor_by_facility_covers_all_facilities(cyc):
    """F16: the Soll factor follows the facility of the matrix cell; every facility needs a factor."""
    assert set(_net(cyc, "C-NET-03")["soll_factor_by_facility"]) == FACILITIES
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _net(d, "C-NET-03")["soll_factor_by_facility"].pop("mixed")),
             "every facility")


def test_soll_factor_by_category_path_and_walking_pace(cyc):
    by_cat = _net(cyc, "C-NET-03")["soll_factor_by_category"]
    assert by_cat["path"] == "separated_track_or_cycle_street"
    assert by_cat["ETW_ERF"] == "walking_pace_area"        # F15
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _net(d, "C-NET-03")["soll_factor_by_category"].pop("path")), "path")


def test_rejects_bad_soll_levels_and_band(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _net(d, "C-NET-03").update(levels=["HAUPT"])), "levels")
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _net(d, "C-NET-06")["demand_band_factor"].update(value=0.5)),
             "demand_band_factor")


def test_rejects_unknown_factor_by_highway(cyc):
    def mut(d):
        next(r for r in d["routing_impedance"]["ist_mapping"]["rules"] if r["id"] == "C-IMP-04")["factor_by_highway"]["living_street"] = "slow"
    _rejects(CyclingRuleSet, _mutated(cyc, mut), "factor_by_highway")


def test_rejects_unknown_matrix_flag(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["separation_matrix"]["ETW_ERF"]["HAUPT"].update(flag="nope")), "unknown flag")


def test_dtv_proxy_checks(cyc):
    def proxy(d):
        return next(r for r in d["facility_assignment"]["rules"] if r["id"] == "C-FAC-02")["dtv_proxy"]
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: proxy(d)["proxy_betweenness"].update(value=80)), "percentile")
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: proxy(d).update(flag="nope")), "unknown flag")


def test_fgsv_candidate_checks(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["cycle_categories"]["RSV"]["fgsv_rsv_candidate"]["predominant_share"].update(value=1.5)),
             "predominant_share")


def test_rejects_official_and_planned_overlap(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _net(d, "C-NET-05")["planned_status"].append("Bestand")), "overlap")


def test_rejects_bonus_out_of_range(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _net(d, "C-NET-04").update(max_reduction=1.5)), "max_reduction")
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _net(d, "C-NET-05").update(multiplier=0)), "multiplier")


# --- principle_scoring (prompts/17) ----------------------------------------------------------


def _pri(d: dict, rule_id: str) -> dict:
    return _by_id(d["principle_scoring"]["rules"], rule_id)


def test_principle_scoring_rules_complete(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["principle_scoring"]["rules"].pop()), "C-PRI-16")


def test_score_forms_name_every_check(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _pri(d, "C-PRI-01")["score_forms"].pop("P-DIR-01")), "score_forms")
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _pri(d, "C-PRI-01")["score_forms"].update({"P-XXX-01": "share"})),
             "score_forms")


def test_rejects_unknown_score_form(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _pri(d, "C-PRI-01")["score_forms"].update({"P-DIR-01": "magic"})),
             "unknown score form")


def test_rejects_unknown_facility_in_mapping(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _pri(d, "C-PRI-02")["by_condition"].update(other="bike_lane")),
             "unknown facilities")
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _pri(d, "C-PRI-03")["partial"].update(mixed=["bike_lane"])),
             "unknown facility")


def test_rejects_partial_overlapping_satisfies(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _pri(d, "C-PRI-03")["partial"].update(mixed=["mixed"])), "overlaps")


def test_rejects_width_reference_outside_project_target(cyc):
    _rejects(CyclingRuleSet,
             _mutated(cyc, lambda d: _pri(d, "C-PRI-08")["required_by_facility"].update(cycle_lane="nowhere")),
             "required_by_facility")


def test_rejects_unavailable_unknown_check(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _pri(d, "C-PRI-16")["unavailable"].update({"P-XXX-09": "x"})),
             "C-PRI-16")


def test_rejects_principle_rule_without_status(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _pri(d, "C-PRI-10").pop("status")), "status")


def test_rejects_confidence_classes_out_of_order(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _pri(d, "C-PRI-13").update(medium=0.9)), "medium")


# --- facility_assignment (prompts/18) ----------------------------------------------------------


def _fac(d: dict, rule_id: str) -> dict:
    return _by_id(d["facility_assignment"]["rules"], rule_id)


def test_facility_rules_complete(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["facility_assignment"]["rules"].pop()), "C-FAC-07")


def test_rejects_width_path_not_in_widths(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _fac(d, "C-FAC-04")["floor"].update(cycle_lane="de.nowhere.min")),
             "not found")
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _fac(d, "C-FAC-04")["de_reference"].update(cycle_lane="de.cycle_lane")),
             "not a number")


def test_rejects_unknown_target_key(cyc):
    _rejects(CyclingRuleSet,
             _mutated(cyc, lambda d: _fac(d, "C-FAC-04")["target_by_facility"].update(cycle_lane="nowhere")),
             "target_by_facility")


def test_rejects_unknown_ist_class_or_facility(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _fac(d, "C-FAC-05")["to_facility"].update({"no": "bike_lane"})), "to_facility")
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _fac(d, "C-FAC-06")["missing_classes"].append("gravel")), "missing_classes")


def test_rejects_unknown_confidence_flag(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _fac(d, "C-FAC-07")["lowers_confidence"].append("magic")), "unknown flags")


def test_rejects_facility_rule_without_status(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: _fac(d, "C-FAC-03").pop("status")), "status")


# --- prompt 19: profile_assignment (design_rules.yaml) -------------------------------------------


def _prf(d, rule_id):
    return _by_id(d["profile_assignment"]["rules"], rule_id)


def test_profile_rules_complete():
    from config.schema.design_model import PROFILE_RULE_IDS
    rules = load_design_rules()
    ids = {r["id"] for r in rules.profile_assignment["rules"]}
    assert PROFILE_RULE_IDS <= ids


def test_profile_cascade_covers_all_degrade_steps():
    rules = load_design_rules()
    steps = [s["step"] for s in rules.cross_section_allocation["degrade_cascade_if_not_fit"]]
    order = _by_id(rules.profile_assignment["rules"], "PRF-06")["cascade_order"]
    assert [s for s in order if s != "fallback"] == steps


def test_rejects_unknown_cascade_step(des):
    _rejects(DesignRuleSet, _mutated(des, lambda d: _prf(d, "PRF-06")["cascade_order"].append("D9")), "D9")


def test_rejects_cycle_elements_missing_facility(des):
    _rejects(DesignRuleSet, _mutated(des, lambda d: _prf(d, "PRF-03")["cycle_elements"].pop("mixed")), "cycle_elements")


def test_rejects_unknown_profile_element(des):
    def mutate(d):
        _prf(d, "PRF-03")["cycle_elements"]["separated_twoway"]["element"] = "hover_lane"
    _rejects(DesignRuleSet, _mutated(des, mutate), "hover_lane")


def test_rejects_unknown_category_in_profile_rules(des):
    _rejects(DesignRuleSet, _mutated(des, lambda d: _prf(d, "PRF-03")["tree_categories"].append("GOW70")), "GOW70")


def test_rejects_profile_rule_missing(des):
    _rejects(DesignRuleSet, _mutated(des, lambda d: d["profile_assignment"]["rules"].pop()), "PRF-06")


# --- review 2026-11, P0: status inactive, scope, half-open intensity classes ---------------------------------


def test_inactive_rules_and_blocks():
    """F28/F33: rural matrix and PL-02 are inactive; inactive rules do not count as covered."""
    from config.schema.provenance import collect_ids
    from pipeline.lib.rules import active_rule_ids

    cycling, design = load_cycling_rules(), load_design_rules()
    assert cycling.separation_matrix["rural"]["status"] == "inactive"
    assert "or in_hvs" in cycling.separation_matrix["rural"]["note"]
    assert _by_id(design.model_dump(by_alias=True)["placement"]["rules"], "PL-02")["status"] == "inactive"
    assert _by_id(cycling.separation_matrix["rules"], "S-03")["scope"] == "rural"
    every = all_rule_ids(load_rules(), cycling, design)
    active = active_rule_ids(load_rules(), cycling, design)
    assert set(every) - set(active) == {"C-RUR-01", "PL-02"}
    assert collect_ids({"status": "inactive", "rules": [{"id": "X-01", "status": "draft"}]}, active_only=True) == []


def test_rejects_invalid_block_status(cyc):
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["separation_matrix"]["rural"].update(status="sleeping")),
             "invalid status")


def test_intensity_classes_half_open(cyc):
    """F27: intensity classes are gap-free [min, max); intensity_upgrade starts at a class boundary with >=."""
    CyclingRuleSet.model_validate(cyc)
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["demand"]["intensity_classes_peak_h"].update(
        oneway=[[0, 150], [160, 750], [750, None]])), "gap")
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["demand"]["intensity_classes_peak_h"].update(
        oneway=[[0, 150], [140, 750], [750, None]])), "overlap")
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["widths_m"]["project_target"]["intensity_upgrade"][0].update(
        {"if": "oneway peak_h > 750"})), "peak_h >= N")
    _rejects(CyclingRuleSet, _mutated(cyc, lambda d: d["widths_m"]["project_target"]["intensity_upgrade"][0].update(
        {"if": "oneway peak_h >= 700"})), "class boundary")


# --- Review 2026-11 P3 (F01, F11, F17, F18) -------------------------------------------------------------


def test_cycle_street_with_motor_traffic_matches_design_ref():
    """F18: cycle_street_carriageway.with_motor_traffic = design_rules lane_width_m.ETW30_mixed (ref)."""
    from pipeline.lib.rules import cycling_design_ref_mismatches
    cyc, des = load_cycling_rules(), load_design_rules()
    assert cycling_design_ref_mismatches(cyc, des) == []
    t = cyc.widths_m["project_target"]["cycle_street_carriageway"]
    assert t["with_motor_traffic"] == des.lanes.lane_width_m["ETW30_mixed"]["value"]


def test_high_volume_cell_points_into_rules_yaml():
    cell = load_cycling_rules().separation_matrix["GOW30"]["high_volume"]
    from pipeline.lib.principles import rules_ref
    assert isinstance(rules_ref(load_rules(), cell["dtv_above"]), (int, float))
    assert cell["fallback"] is None and cell["source_type"] == "swov_crow"
    assert cell["rule"] in {r["id"] for r in load_cycling_rules().separation_matrix["rules"]}


@pytest.mark.parametrize("key,value,match", [("fallback", "cycle_lane", "fallback"), ("dtv_above", "10000", "dtv_above"),
                                             ("flag", "", "flag")])
def test_rejects_bad_high_volume_cell(cyc, key, value, match):
    def mutate(d):
        d["separation_matrix"]["GOW30"]["high_volume"][key] = value
    _rejects(CyclingRuleSet, _mutated(cyc, mutate), match)


def test_rejects_unknown_parking_by_category(des):
    def mutate(d):
        _prf(d, "PRF-03")["parking_by_category"]["GOW30"] = ["hover_parking"]
    _rejects(DesignRuleSet, _mutated(des, mutate), "parking_by_category")


def test_cascade_d3_before_d2():
    order = _by_id(load_design_rules().profile_assignment["rules"], "PRF-06")["cascade_order"]
    assert order == ["D1", "D3", "D2", "fallback", "D4", "D5", "D6", "D7"]
