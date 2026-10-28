"""Golden cases: synthetic segments with expected category (tests/golden/*.geojson).

Structure tests check the cases; test_golden_classification runs pipeline/s05_classify.py on them.
"""

import json
from pathlib import Path

import geopandas as gpd
import pytest

from pipeline.lib.rules import all_thresholds, load_rules, referenced_features

GOLDEN_DIR = Path(__file__).parent / "golden"
GOLDEN_FILES = sorted(GOLDEN_DIR.glob("*.geojson"))
RULES = load_rules()


def _props(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert len(doc["features"]) == 1, path.name
    return doc["features"][0]["properties"]


def _features(props: dict) -> dict:
    return {k: props[k] for k in referenced_features(RULES)}


def _resolve(ref: str) -> float:
    section, name = ref.split(".", 1)
    if section == "thresholds":
        return all_thresholds(RULES)[name].value
    if section == "required_width":
        return RULES.required_width[name].value
    raise KeyError(ref)


def test_enough_cases():
    assert len(GOLDEN_FILES) >= 12


def test_case_ids_unique_and_match_filename():
    ids = [_props(p)["case_id"] for p in GOLDEN_FILES]
    assert len(ids) == len(set(ids))
    for path, case_id in zip(GOLDEN_FILES, ids):
        assert path.stem.split("_", 1)[1] == case_id


@pytest.mark.parametrize("path", GOLDEN_FILES, ids=lambda p: p.stem)
def test_geometry(path):
    gdf = gpd.read_file(path)
    assert gdf.crs.to_epsg() == 25832
    assert gdf.geometry.is_valid.all()
    assert (gdf.geom_type == "LineString").all()
    assert (gdf.length > 0).all()


@pytest.mark.parametrize("path", GOLDEN_FILES, ids=lambda p: p.stem)
def test_case_is_complete(path):
    props = _props(path)
    missing = referenced_features(RULES) - props.keys()
    assert not missing, f"missing features: {sorted(missing)}"
    assert all(v is not None for v in _features(props).values())
    assert props["expected_category"] in RULES.categories
    rule_ids = {r.id for r in RULES.classification}
    assert set(props["expected_rules"]) <= rule_ids


@pytest.mark.parametrize(
    "path", [p for p in GOLDEN_FILES if _props(p)["boundary"]], ids=lambda p: p.stem
)
def test_boundary_matches_rules(path):
    """Boundary cases record the threshold they test; a changed threshold must show up here."""
    boundary = _props(path)["boundary"]
    assert boundary["value"] == pytest.approx(_resolve(boundary["ref"])), (
        f"{boundary['ref']} changed in rules.yaml – review this golden case deliberately"
    )
    assert boundary["side"] in {"at", "below", "above"}


def test_every_rule_path_has_a_case():
    covered = {r for p in GOLDEN_FILES for r in _props(p)["expected_rules"]}
    assert {r.id for r in RULES.classification} <= covered


@pytest.mark.parametrize("path", GOLDEN_FILES, ids=lambda p: p.stem)
def test_golden_classification(path):
    from pipeline.s05_classify import classify_segment

    props = _props(path)
    result = classify_segment(_features(props), RULES)
    assert result["cat_proposed"] == props["expected_category"]
    passed = {step["id"] for step in result["rule_trace"] if step["passed"]}
    assert set(props["expected_rules"]) <= passed
