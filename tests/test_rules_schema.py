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
    ],
)
def test_schema_rejects(raw, description, mutate):
    with pytest.raises(ValidationError):
        RuleSet.model_validate(_mutated(raw, mutate))


def test_assumption_rule_may_omit_source(raw):
    # N2 in rules.yaml is source_type=assumption without a source; that is allowed.
    data = _mutated(raw, lambda d: None)
    n2 = next(c for c in data["coherence"] if c["id"] == "N2")
    assert "source" not in n2
    RuleSet.model_validate(data)
