"""Golden cases of the cycle network extension (tests/golden/cycling/, prompts/14).

s*.geojson: sections with expected facility, target width (as references into cycling_rules.yaml, so no
number is copied) and lanes per direction. j*.geojson: junctions with expected target junction type.

Structure tests run now. Facility/width is evaluated by pipeline/c05_facility.py (prompt 18), lanes and bus lane by
pipeline/c06_cross_section_soll.py (prompt 19), junction type and cyclist treatment by pipeline/c07_junctions.py
(prompt 20).
"""

import importlib
import json
import re
from pathlib import Path

import geopandas as gpd
import pytest

from config.schema.cycling_model import CELL_FACILITY_KEYS, CYCLE_CATEGORIES, FACILITIES, NO_CYCLE_CATEGORY
from config.schema.provenance import META_KEYS
from config.schema.rules_model import EXPECTED_CATEGORIES
from pipeline.lib.rules import load_cycling_rules, load_design_rules

GOLDEN_DIR = Path(__file__).parent / "golden" / "cycling"
SECTION_FILES = sorted(GOLDEN_DIR.glob("s*.geojson"))
JUNCTION_FILES = sorted(GOLDEN_DIR.glob("j*.geojson"))
CYCLING = load_cycling_rules()
DESIGN = load_design_rules()
CYCLING_RAW = CYCLING.model_dump()
DESIGN_RAW = DESIGN.model_dump(by_alias=True)
_STEP = re.compile(r"([^.\[\]]+)|\[([^\]]+)\]")


def _props(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert len(doc["features"]) == 1, path.name
    return doc["features"][0]["properties"]


def resolve(ref: str):
    """Value at a dotted path in cycling_rules.yaml or design_rules.yaml.

    `[n]` indexes a list, `[ID]` picks the list entry with that rule id.
    """
    for raw in (CYCLING_RAW, DESIGN_RAW):
        node = raw
        try:
            for key, index in _STEP.findall(ref):
                if key:
                    node = node[key]
                elif index.isdigit():
                    node = node[int(index)]
                else:
                    node = next(e for e in node if e.get("id") == index)
            return node
        except (KeyError, IndexError, StopIteration, TypeError):
            continue
    raise KeyError(ref)


def expected_width(props: dict) -> float | None:
    refs = props["expected_width_refs"]
    return sum(resolve(r) for r in refs) if refs else None


def _rule_ids() -> set[str]:
    return set(CYCLING.rule_ids()) | set(DESIGN.rule_ids())


# --- structure -------------------------------------------------------------------------------


def test_enough_cases():
    assert len(SECTION_FILES) >= 10
    assert len(JUNCTION_FILES) >= 6


def test_case_ids_unique_and_match_filename():
    files = SECTION_FILES + JUNCTION_FILES
    ids = [_props(p)["case_id"] for p in files]
    assert len(ids) == len(set(ids))
    for path, case_id in zip(files, ids):
        assert path.stem.split("_", 1)[1] == case_id


@pytest.mark.parametrize("path", SECTION_FILES + JUNCTION_FILES, ids=lambda p: p.stem)
def test_geometry(path):
    gdf = gpd.read_file(path)
    assert gdf.crs.to_epsg() == 25832
    assert gdf.geometry.is_valid.all()
    assert (gdf.geom_type == ("LineString" if path.name.startswith("s") else "Point")).all()


@pytest.mark.parametrize("path", SECTION_FILES, ids=lambda p: p.stem)
def test_section_case_is_complete(path):
    props = _props(path)
    assert props["cat_final"] in EXPECTED_CATEGORIES
    assert props["cycle_cat"] in CYCLE_CATEGORIES | {NO_CYCLE_CATEGORY}
    assert props["expected_facility"] in FACILITIES
    lanes = props["expected_lanes_per_direction"]
    assert lanes is None or lanes == "shared" or (isinstance(lanes, int) and lanes >= 1)
    assert set(props["expected_rules"]) <= _rule_ids()
    for ref in props["expected_width_refs"]:
        assert isinstance(resolve(ref), (int, float)), ref


@pytest.mark.parametrize("path", JUNCTION_FILES, ids=lambda p: p.stem)
def test_junction_case_is_complete(path):
    props = _props(path)
    assert props["expected_junction_type"] in DESIGN.junctions.types
    assert len(props["legs"]) >= 2
    assert set(props["expected_rules"]) | set(props["expected_cyclist_treatment"]) <= _rule_ids()


@pytest.mark.parametrize("path", SECTION_FILES + JUNCTION_FILES, ids=lambda p: p.stem)
def test_referenced_values_exist(path):
    """refs_used names the thresholds a case was built around; a renamed or removed one shows up here."""
    for ref in _props(path)["refs_used"]:
        resolve(ref)


def test_every_matrix_row_has_a_section_case():
    covered = {_props(p)["cat_final"] for p in SECTION_FILES}
    assert EXPECTED_CATEGORIES <= covered


def test_every_matrix_facility_has_a_section_case():
    matrix = CYCLING.separation_matrix
    used = set()
    for cat, row in matrix.items():
        if cat in META_KEYS or not isinstance(row, dict):
            continue
        for cell in row.values():
            if isinstance(cell, str) and cell in FACILITIES:
                used.add(cell)
            elif isinstance(cell, dict):
                used |= {v for k, v in cell.items() if k in CELL_FACILITY_KEYS}
    assert used <= {_props(p)["expected_facility"] for p in SECTION_FILES}


def test_every_junction_row_has_a_case():
    covered = {r for p in JUNCTION_FILES for r in _props(p)["expected_rules"]}
    assert {r.id for r in DESIGN.junctions.decision_table.rows} <= covered


# --- evaluation ------------------------------------------------------------------------------------------


def _step(module: str):
    return importlib.import_module(f"pipeline.{module}")


@pytest.mark.parametrize("path", SECTION_FILES, ids=lambda p: p.stem)
def test_golden_facility_and_width(path):
    props = _props(path)
    result = _step("c05_facility").facility_for_segment(props, CYCLING)
    assert result["cycle_facility"] == props["expected_facility"]
    width = expected_width(props)
    assert result["cycle_width_m"] == (pytest.approx(width) if width is not None else None)


@pytest.mark.parametrize("path", SECTION_FILES, ids=lambda p: p.stem)
def test_golden_lanes(path):
    props = _props(path)
    result = _step("c06_cross_section_soll").lanes_for_segment(props, DESIGN, CYCLING)
    assert result["lanes_per_direction"] == props["expected_lanes_per_direction"]
    assert result["bus_lane"] == props["expected_bus_lane"]


@pytest.mark.parametrize("path", JUNCTION_FILES, ids=lambda p: p.stem)
def test_golden_junction_type(path):
    props = _props(path)
    result = _step("c07_junctions").junction_type(props, DESIGN)
    assert result["junction_type_soll"] == props["expected_junction_type"]
    fired = {step["id"] for step in result["rule_trace_junction"] if step["passed"]}
    assert set(props["expected_rules"]) <= fired
    assert set(props["expected_cyclist_treatment"]) <= set(result["cyclist_treatment"])
