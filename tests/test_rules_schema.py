"""Schema tests for config/rules.yaml (guide 3.4: every rule has source and source_type,
no threshold without a unit)."""

import copy

import pytest
import yaml
from pydantic import ValidationError

from config.schema.rules_model import RuleSet
from pipeline.lib.rules import (
    DEFAULT_RULES_PATH,
    all_thresholds,
    load_rules,
    referenced_features,
)


@pytest.fixture(scope="module")
def raw() -> dict:
    with open(DEFAULT_RULES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _mutated(raw: dict, mutate) -> dict:
    data = copy.deepcopy(raw)
    mutate(data)
    return data


def _rule(data: dict, rule_id: str) -> dict:
    return next(r for r in data["classification"] if r["id"] == rule_id)


def _coh(data: dict, rule_id: str) -> dict:
    return next(r for r in data["coherence"] if r["id"] == rule_id)


# --- the real file ---------------------------------------------------------------------------


def test_rules_yaml_is_valid():
    rules = load_rules()
    assert rules.meta.crs_work == "EPSG:25832"
    assert len(rules.classification) >= 8


def test_cascade_ends_with_default_rule():
    rules = load_rules()
    assert rules.classification[-1].if_ == "default"


def test_all_thresholds_have_units():
    for name, threshold in all_thresholds(load_rules()).items():
        assert threshold.unit.strip(), name


def test_referenced_features():
    # The feature names the cascade in rules.yaml 0.1.0 needs. If rules.yaml changes,
    # update this list and the golden cases together.
    assert referenced_features(load_rules()) == {
        "access_motor_only",
        "bus_route",
        "conn_score",
        "crossing_demand",
        "highway",
        "in_hvs",
        "ist_verkehrsberuhigt",
        "outside_builtup_area",
        "override_school_street",
        "pedestrian_zone",
        "school_or_kita_access_m",
        "shop_frontage_share",
        "width_p10_m",
    }


# --- the schema rejects broken files ---------------------------------------------------------


def test_valid_raw_passes(raw):
    RuleSet.model_validate(raw)


@pytest.mark.parametrize(
    "description, mutate",
    [
        ("rule without source", lambda d: _rule(d, "C-G50-01").pop("source")),
        ("rule without source_type", lambda d: _rule(d, "C-G50-01").pop("source_type")),
        ("invalid source_type", lambda d: _rule(d, "C-G50-01").update(source_type="gut_feeling")),
        ("invalid status", lambda d: _rule(d, "C-G50-01").update(status="done")),
        ("duplicate rule id", lambda d: _rule(d, "C-G50-01").update(id="C-SW-01")),
        ("duplicate id across sections", lambda d: d["coherence"][0].update(id="C-SW-01")),
        ("threshold without unit", lambda d: _rule(d, "C-GOW-01")["thresholds"]["conn_gow"].pop("unit")),
        ("threshold with empty unit", lambda d: _rule(d, "C-GOW-01")["thresholds"]["conn_gow"].update(unit=" ")),
        ("unknown category in then", lambda d: _rule(d, "C-G50-01").update(then="GOW70")),
        ("unknown applies_to", lambda d: _rule(d, "C-G50-01").update(applies_to="ETW")),
        ("unknown source reference", lambda d: _rule(d, "C-G50-01").update(source="NOT_A_SOURCE")),
        ("unknown threshold reference", lambda d: _rule(d, "C-GOW-01").update(**{"if": "conn_score >= thresholds.nope"})),
        ("unknown width reference", lambda d: _rule(d, "C-G30-02").update(**{"if": "width_p10_m < required_width.GOW99"})),
        ("cascade without default", lambda d: d["classification"].pop()),
        ("category missing", lambda d: d["categories"].pop("ETW60")),
        ("extra category", lambda d: d["categories"].update(GOW70={"label_de": "x", "speed_kmh": 70})),
        ("requirement for unknown category", lambda d: d["requirements"].update(GOW70={})),
        ("requirement without source_type", lambda d: d["requirements"]["GOW50"]["cycle_track_width_m"].pop("source_type")),
        ("number without unit", lambda d: d["requirements"]["ETW30"].update(lamp_distance={"value": 30, "source": "RAST_06", "source_type": "de_regelwerk"})),
        ("coherence rule without source_type", lambda d: d["coherence"][0].pop("source_type")),
        ("non-assumption rule without source", lambda d: d["coherence"][0].pop("source")),
        ("width without source_type", lambda d: d["required_width"]["GOW50"].pop("source_type")),
        ("width for unknown category", lambda d: d["required_width"].update(GOW70={"value": 20.0, "source_type": "assumption"})),
        ("weights do not sum to 1", lambda d: d["scores"]["conn_score"]["weights"].update(dtv_norm=0.5)),
        ("wrong working CRS", lambda d: d["meta"].update(crs_work="EPSG:4326")),
        ("version not semver", lambda d: d["meta"].update(version="v1")),
        ("unknown top-level key", lambda d: d.update(extra_section={})),
        ("network section missing", lambda d: d.pop("network")),
        ("network rule without source_type", lambda d: d["network"]["rules"][0].pop("source_type")),
        ("network rule without status", lambda d: d["network"]["rules"][0].pop("status")),
        ("network rule with bad id", lambda d: d["network"]["rules"][0].update(id="NET-1")),
        ("network rule id duplicates cascade", lambda d: d["network"]["rules"][0].update(id="C-SW-01")),
        ("network threshold without unit", lambda d: d["network"]["rules"][2]["thresholds"]["min_length_m"].pop("unit")),
        ("duplicate highway class", lambda d: d["network"]["highway_classes"]["values"].append("residential")),
        ("no highway classes", lambda d: d["network"]["highway_classes"].update(values=[])),
        ("coherence rule without status", lambda d: d["coherence"][0].pop("status")),
        ("coherence threshold without unit", lambda d: d["coherence"][0]["thresholds"]["boundary_tolerance_m"].pop("unit")),
        ("N6 with removed node_types (F09)", lambda d: _coh(d, "N6").update(node_types=[{"pair": ["GOW50", "GOW50"], "type": "x"}])),
        ("N6 rank with duplicate", lambda d: _coh(d, "N6")["category_rank"].append("SW")),
        ("N6 rank incomplete", lambda d: _coh(d, "N6")["category_rank"].remove("ETW60")),
        ("N6 with removed ist_check (F09)", lambda d: _coh(d, "N6").update(ist_check={})),
        ("N5 gate with unknown category", lambda d: _coh(d, "N5")["gate_transitions"][0].update(to=["GOW31"])),
        ("speed level without source_type", lambda d: d["discrepancy"]["speed"]["levels"][0].pop("source_type")),
        ("speed levels not ascending", lambda d: d["discrepancy"]["speed"]["levels"][1].update(min_excess_kmh=40)),
        ("speed severity above 3", lambda d: d["discrepancy"]["speed"]["levels"][2].update(severity=4)),
        ("use factors not ascending", lambda d: d["discrepancy"]["use"]["levels"][2].update(factor=1.2)),
        ("design violation for unknown check", lambda d: d["discrepancy"]["design"]["violations"][0].update(check="lamps")),
        ("design violation with bad direction", lambda d: d["discrepancy"]["design"]["violations"][0].update(direction="up")),
        ("design direction for unknown category", lambda d: d["discrepancy"]["design"]["violations"][3].update(direction={"GOW70": "flow"})),
        ("discrepancy rule without status", lambda d: d["discrepancy"]["speed"].pop("status")),
        ("discrepancy id duplicates cascade", lambda d: d["discrepancy"]["use"].update(id="C-SW-01")),
        ("unknown discrepancy type", lambda d: d["discrepancy"]["types"].update(D4="x")),
        ("risk weight without component", lambda d: d["priority"]["risk"]["components"].pop("cycle_network")),
        ("risk component without weight", lambda d: d["priority"]["risk"]["components"].update(noise="noise_norm")),
        ("risk severe weight key unknown", lambda d: d["priority"]["risk"].update(severe_weight_key="x")),
        ("risk threshold without unit", lambda d: d["priority"]["risk"]["thresholds"]["snap_m"].pop("unit")),
        ("risk rule with bad id", lambda d: d["priority"]["risk"].update(id="RISK-1")),
        # review 2026-11, P0
        ("default rule inactive", lambda d: d["classification"][-1].update(status="inactive")),
        ("category without source_type", lambda d: d["categories"]["GOW50"].pop("source_type")),
        ("category swov_crow without source", lambda d: d["categories"]["GOW50"].pop("source")),
        ("score weights without source_type", lambda d: d["scores"]["conn_score"].pop("source_type")),
        ("place_score without source_type", lambda d: d["scores"]["place_score"].pop("source_type")),
        ("priority without source_type", lambda d: d["priority"].pop("source_type")),
        ("feasibility classes with gap", lambda d: d["feasibility_classes"]["tight"].update(min=0.90)),
        ("feasibility classes overlapping", lambda d: d["feasibility_classes"]["tight"].update(max=1.05)),
        ("feasibility class min >= max", lambda d: d["feasibility_classes"]["tight"].update(min=1.0)),
        ("requirement ref outside widths_m", lambda d: d["requirements"]["GOW50"]["cycle_track_width_m"].update(ref={"value": "rules.required_width.GOW50"})),
        ("requirement ref for missing field", lambda d: d["requirements"]["GOW50"]["cycle_track_width_m"].update(ref={"ideal": "cycling_rules.widths_m.de.separated_oneway.standard"})),
    ],
)
def test_schema_rejects(raw, description, mutate):
    with pytest.raises(ValidationError):
        RuleSet.model_validate(_mutated(raw, mutate))


def test_coherence_rules():
    rules = load_rules()
    assert [r.id for r in rules.coherence] == ["N1", "N2", "N3", "N4", "N5", "N6", "N7"]
    assert all(r.status == "draft" for r in rules.coherence)
    assert rules.coherence_rule("N2").param("min_run_m") == 200
    assert rules.coherence_rule("N1").param("boundary_tolerance_m") == 50
    with pytest.raises(KeyError):
        rules.coherence_rule("N2").param("not_there")


def test_assumption_rule_may_omit_source(raw):
    # N2 in rules.yaml is source_type=assumption without a source; that is allowed.
    data = _mutated(raw, lambda d: None)
    n2 = next(c for c in data["coherence"] if c["id"] == "N2")
    assert "source" not in n2
    RuleSet.model_validate(data)


def test_conflation_rules():
    conflation = load_rules().conflation
    assert [r.id for r in conflation.rules] == ["S-CONF-01", "S-CONF-02", "S-CONF-03", "S-CONF-04"]
    for rule in conflation.rules:
        assert rule.status == "draft"
        for threshold in rule.thresholds.values():
            assert threshold.source_type == "assumption"
            assert threshold.unit.strip()
    assert conflation.rule("S-CONF-01").thresholds["buffer_m"].unit == "m"


def test_duplicate_conflation_id_rejected(raw):
    def mutate(d):
        d["conflation"]["rules"][1]["id"] = d["conflation"]["rules"][0]["id"]

    with pytest.raises(ValidationError, match="duplicate"):
        RuleSet.model_validate(_mutated(raw, mutate))


def test_conflation_rule_needs_source_unless_assumption(raw):
    def mutate(d):
        del d["conflation"]["rules"][3]["source"]  # S-CONF-04, source_type hamburg

    with pytest.raises(ValidationError, match="source missing"):
        RuleSet.model_validate(_mutated(raw, mutate))


def test_network_rules():
    network = load_rules().network
    assert [r.id for r in network.rules] == ["S-NET-01", "S-NET-02", "S-NET-03", "S-NET-04"]
    extra = network.rule("S-NET-04")
    assert set(extra.include_highway) == {"service", "track"} and extra.require_name
    assert "alley" in extra.service_values and "parking_aisle" not in extra.service_values
    assert "service" not in network.highway_classes.values
    assert {"living_street", "pedestrian"} <= set(network.highway_classes.values)
    assert network.rule("S-NET-03").thresholds["min_length_m"].unit == "m"


# --- validation (prompts/12_validation.md) ---------------------------------------------------


def _val(data: dict, rule_id: str) -> dict:
    return next(r for r in data["validation"]["rules"] if r["id"] == rule_id)


def test_validation_rules():
    rules = load_rules()
    sens = rules.validation.rule("V-SENS-01")
    assert sens.thresholds["delta"].value == pytest.approx(0.2)
    mc = rules.validation.rule("V-SENS-02")
    assert mc.runs == 500 and isinstance(mc.seed, int)
    assert set(mc.vary) == {"weights", "thresholds"}
    unc = rules.validation.rule("V-UNC-01")
    assert unc.thresholds["min_change_rate"].value == pytest.approx(0.3)
    for r in rules.validation.rules:
        assert r.source_type == "assumption"
        assert all(t.source_type == "assumption" for t in r.thresholds.values())


@pytest.mark.parametrize("description, mutate", [
    ("runs must be positive", lambda d: _val(d, "V-SENS-02").update(runs=0)),
    ("unknown vary entry", lambda d: _val(d, "V-SENS-02").update(vary=["weights", "colours"])),
    ("threshold without unit", lambda d: _val(d, "V-UNC-01")["thresholds"]["min_change_rate"].pop("unit")),
    ("duplicate id with another stage", lambda d: _val(d, "V-UNC-01").update(id="S-NET-01")),
])
def test_validation_schema_rejects(raw, description, mutate):
    with pytest.raises(ValidationError):
        RuleSet.model_validate(_mutated(raw, mutate))


# --- review 2026-11, P0: status inactive, half-open classes, provenance, requirement refs ----------------------


def test_inactive_status_is_valid(raw):
    RuleSet.model_validate(_mutated(raw, lambda d: _rule(d, "C-G50-01").update(status="inactive")))


def test_c_rur_01_is_inactive():
    """F28: no data source for outside_builtup_area; the rural branch is inactive."""
    rules = load_rules()
    rur = next(r for r in rules.classification if r.id == "C-RUR-01")
    assert rur.status == "inactive"
    assert "or in_hvs" in rur.note


def test_feasibility_classes_are_half_open():
    """F27: [min, max) without gaps or overlaps; fits is open upwards, does_not_fit downwards."""
    c = load_rules().feasibility_classes
    assert c["fits"].max is None and c["does_not_fit"].min is None
    assert c["tight"].min == c["does_not_fit"].max and c["tight"].max == c["fits"].min


def test_requirement_refs_match_widths_m():
    """F32: widths in requirements that also stand in cycling_rules widths_m carry ref: and must agree."""
    from pipeline.lib.rules import load_cycling_rules, requirement_ref_mismatches

    rules = load_rules()
    refs = [(cat, key) for cat, reqs in rules.requirements.items() for key, e in reqs.items()
            if isinstance(e, dict) and e.get("ref")]
    assert {("GOW50", "cycle_track_width_m"), ("GOW50", "buffer_to_parking_m"), ("GOW30", "cycle_lane_width_m"),
            ("GOW30", "cycle_lane_width_de_m")} <= set(refs)
    assert requirement_ref_mismatches(rules, load_cycling_rules()) == []


def test_requirement_ref_mismatch_is_reported():
    from pipeline.lib.rules import load_cycling_rules, requirement_ref_mismatches

    rules = load_rules()
    reqs = {**rules.requirements, "GOW50": {**rules.requirements["GOW50"],
            "cycle_track_width_m": {**rules.requirements["GOW50"]["cycle_track_width_m"], "value": 2.10}}}
    bad = rules.model_copy(update={"requirements": reqs})
    assert requirement_ref_mismatches(bad, load_cycling_rules()) == [
        "requirements.GOW50.cycle_track_width_m.value = 2.1, cycling_rules.widths_m.de.separated_oneway.standard = 2.0"]


def test_categories_and_weights_have_provenance():
    rules = load_rules()
    assert all(c.source_type for c in rules.categories.values())
    assert rules.scores["conn_score"].source_type == "assumption"
    assert rules.scores["place_score"].source_type == "assumption"
    assert rules.priority.source_type == "assumption"


# --- review 2026-11, package P1 (F05, F14, F25, F23) ----------------------------------------


def test_required_width_value_equals_formula():
    """Invariant V-INV-06 (F05): every required_width entry with a formula has value == evaluated formula
    (paths into design_rules.yaml D. and cycling_rules.yaml C.)."""
    from pipeline.lib.rules import load_cycling_rules, load_design_rules, required_width_formula_mismatches

    rules = load_rules()
    assert {k for k, e in rules.required_width.items() if e.formula} >= {"GOW50", "GOW50_bus", "ETW30"}
    assert required_width_formula_mismatches(rules, load_cycling_rules(), load_design_rules()) == []


def test_required_width_formula_mismatch_is_reported():
    from pipeline.lib.rules import load_cycling_rules, load_design_rules, required_width_formula_mismatches

    rules = load_rules()
    widths = {**rules.required_width, "GOW50": rules.required_width["GOW50"].model_copy(update={"value": 16.5})}
    bad = rules.model_copy(update={"required_width": widths})
    assert required_width_formula_mismatches(bad, load_cycling_rules(), load_design_rules()) == [
        "required_width.GOW50 = 16.5, formula = 17"]


def test_width_formula_rejects_unknown_path_and_code():
    from pipeline.lib.rules import evaluate_width_formula, load_cycling_rules, load_design_rules

    c, d = load_cycling_rules(), load_design_rules()
    with pytest.raises(KeyError):
        evaluate_width_formula("2*D.cross_section_allocation.elements_min_m.nothing", c, d)
    with pytest.raises(ValueError):
        evaluate_width_formula("__import__('os')", c, d)


def test_global_caveats_must_be_defaults_or_fallbacks(raw):
    data = copy.deepcopy(raw)
    conf = next(p for p in data["classification_policy"] if p["id"] == "C-CONF-01")
    conf["global_caveats"] = [*conf["global_caveats"], "no_such_feature"]
    with pytest.raises(ValidationError, match="global_caveats"):
        RuleSet.model_validate(data)


def test_crossing_demand_default_is_inactive():
    """F25 (Q2 b): the crossing_demand part of C-G30-01 is switched off until place_score is calibrated."""
    rules = load_rules()
    miss = next(p for p in rules.classification_policy if p.id == "C-MISS-01")
    assert miss.defaults["crossing_demand"].status == "inactive"
    assert "keiner Regel" in rules.scores["place_score"].note


def test_conn_score_without_in_hvs():
    """F13 (Q3 b): in_hvs only as its own trigger in C-GOW-01, not in conn_score."""
    rules = load_rules()
    assert "in_hvs" not in rules.scores["conn_score"].weights
    assert "in_hvs" in next(r for r in rules.classification if r.id == "C-GOW-01").if_


def test_gow50_cycling_requirement_without_mandatory_use():
    """F22: Benutzungspflicht is an order, not a design feature; D-DES-01 uses the same value."""
    rules = load_rules()
    value = rules.requirements["GOW50"]["cycling"]["value"]
    assert value == "separated_track_or_parallel_route"
    assert value in {v.requirement for v in rules.discrepancy.design.violations if v.check == "cycling"}

