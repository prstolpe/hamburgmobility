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
        "conn_score",
        "crossing_demand",
        "highway",
        "in_hvs",
        "ist_verkehrsberuhigt",
        "outside_builtup_area",
        "override_school_street",
        "pedestrian_zone",
        "schools_or_kitas_within_m",
        "separated_cycle_track_present",
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
        ("N6 pair with unknown category", lambda d: _coh(d, "N6")["node_types"][0].update(pair=["GOW50", "XYZ"])),
        ("N6 rank with duplicate", lambda d: _coh(d, "N6")["category_rank"].append("SW")),
        ("N6 rank incomplete", lambda d: _coh(d, "N6")["category_rank"].remove("ETW60")),
        ("N6 node type without ist_check", lambda d: _coh(d, "N6")["ist_check"].pop("roundabout")),
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
    assert [r.id for r in network.rules] == ["S-NET-01", "S-NET-02", "S-NET-03"]
    assert "service" not in network.highway_classes.values
    assert {"living_street", "pedestrian"} <= set(network.highway_classes.values)
    assert network.rule("S-NET-03").thresholds["min_length_m"].unit == "m"
