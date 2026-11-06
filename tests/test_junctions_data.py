"""Checks on the real data/interim/junctions.parquet (skipped until `make junctions` has run)."""

import json

import geopandas as gpd
import pytest

from config.schema.design_model import IST_JUNCTION_TYPES
from pipeline.lib import junctions as jn
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_design_rules

OUT = REPO_ROOT / "data" / "interim" / "junctions.parquet"
pytestmark = pytest.mark.skipif(not OUT.exists(), reason="run `make junctions` first")
DESIGN = load_design_rules()


@pytest.fixture(scope="module")
def out() -> gpd.GeoDataFrame:
    return gpd.read_parquet(OUT)


def test_points_in_work_crs(out):
    assert out.crs == "EPSG:25832"
    assert (out.geom_type == "Point").all()
    assert out["node_id"].is_unique


def test_value_domains(out):
    types = set(DESIGN.junctions.types)
    assert set(out["junction_type_soll"].dropna()) <= types
    assert set(out["junction_type_final"].dropna()) <= types
    assert set(out["junction_type_ist"]) <= set(IST_JUNCTION_TYPES)
    assert set(out["confidence"]) <= set(jn.CONFIDENCE)
    jc = {i for v in out["cyclist_treatment"].dropna() for i in v.split("|")}
    assert jc <= {e["id"] for e in DESIGN.junctions.cyclist_treatment}


def test_missing_type_only_with_no_rule(out):
    missing = out[out["junction_type_soll"].isna()]
    assert missing["conflict_flags"].fillna("").str.contains("no_rule").all()


def test_every_row_has_a_trace(out):
    for t in out["rule_trace_junction"].sample(200, random_state=0):
        steps = json.loads(t)
        assert steps[0]["id"] == "J-M-04" and steps[-1]["id"] == "J-M-06"


def test_action_needed_matches_ist_result(out):
    assert (out["action_needed"] == (out["ist_result"] == "mismatch")).all()


def test_roundabouts_name_the_jc01_conflict(out):
    rb = out[out["cyclist_treatment"].fillna("").str.contains("JC-01")]
    assert rb["treatment_text"].str.contains("SWOV").all()


def test_priority_rank_only_for_action_needed(out):
    ranked = out[out["priority_rank"].notna()]
    assert ranked["action_needed"].all()
    assert len(ranked) == out["action_needed"].sum()


def test_no_crash_details_stored(out):
    assert not [c for c in out.columns if c.startswith("crash") and c not in ("crashes_cyc", "crashes_cyc_severe")]
