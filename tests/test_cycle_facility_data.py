"""Checks on the real data/interim/cycle_facility.parquet (skipped until `make cycle-facility` has run)."""

import json

import geopandas as gpd
import pandas as pd
import pytest

from config.schema.cycling_model import CYCLE_CATEGORIES, FACILITIES, IST_CLASSES, NO_CYCLE_CATEGORY
from pipeline.lib import facility as fa
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_cycling_rules

OUT = REPO_ROOT / "data" / "interim" / "cycle_facility.parquet"
FINAL = REPO_ROOT / "data" / "interim" / "final.parquet"

pytestmark = pytest.mark.skipif(not OUT.exists(), reason="run `make cycle-facility` first")
P = fa.FacilityParams.from_rules(load_cycling_rules())


@pytest.fixture(scope="module")
def out() -> gpd.GeoDataFrame:
    return gpd.read_parquet(OUT)


def test_one_row_per_segment(out):
    final = pd.read_parquet(FINAL, columns=["segment_id"])
    assert out["segment_id"].is_unique
    assert set(out["segment_id"]) == set(final["segment_id"])
    assert out.crs == "EPSG:25832"


def test_value_domains(out):
    assert set(out["cycle_facility_soll"].dropna()) <= FACILITIES
    assert set(out["cycle_facility_ist"]) <= FACILITIES
    assert set(out["cycle_osm_ist"]) <= IST_CLASSES
    assert set(out["cycle_cat_final"]) <= CYCLE_CATEGORIES | {NO_CYCLE_CATEGORY}
    assert set(out["facility_gap"]) <= {"missing", "wrong_type", "partial", "too_narrow", "none", "not_assessed"}


def test_soll_only_with_category(out):
    assert out.loc[out["cat_final"].isna(), "cycle_facility_soll"].isna().all()
    assert out.loc[out["cat_final"].notna(), "cycle_facility_soll"].notna().all()


def test_matrix_rules_s01_s02(out):
    """S-01: no cycle lane at GOW50; S-02: no cycle lane on ETW30."""
    assert not ((out["cat_final"] == "GOW50") & (out["cycle_facility_soll"] == "cycle_lane")).any()
    assert not ((out["cat_final"] == "ETW30") & (out["cycle_facility_soll"] == "cycle_lane")).any()


def test_width_never_below_floor(out):
    for fac, floor in P.floor.items():
        w = out.loc[out["cycle_facility_soll"] == fac, "cycle_width_soll_m"].dropna()
        assert (w >= floor - 1e-9).all(), fac
    assert out.loc[out["cycle_facility_soll"] == "mixed", "cycle_width_soll_m"].isna().all()
    # cycling_rules.yaml 0.7.0: own paths get the two-way path width (open question 108)
    assert out.loc[out["cycle_facility_soll"] == "own_path", "cycle_width_soll_m"].notna().all()


def test_every_row_has_a_trace(out):
    for t in out["rule_trace_facility"].sample(200, random_state=0):
        ids = {s["id"] for s in json.loads(t)}
        assert {"C-FAC-01", "C-FAC-05", "C-FAC-06"} <= ids
