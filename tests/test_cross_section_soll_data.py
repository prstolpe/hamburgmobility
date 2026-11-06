"""Checks on the real data/interim/cross_section_soll.parquet (skipped until `make cross-section-soll` has run)."""

import json

import geopandas as gpd
import pandas as pd
import pytest

from config.schema.cycling_model import FACILITIES
from pipeline.lib import profile as pf
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_cycling_rules, load_design_rules, load_rules

OUT = REPO_ROOT / "data" / "interim" / "cross_section_soll.parquet"
FINAL = REPO_ROOT / "data" / "interim" / "final.parquet"

pytestmark = pytest.mark.skipif(not OUT.exists(), reason="run `make cross-section-soll` first")
P = pf.ProfileParams.from_rules(load_design_rules(), load_cycling_rules(), load_rules())


@pytest.fixture(scope="module")
def out() -> gpd.GeoDataFrame:
    return gpd.read_parquet(OUT)


def test_one_row_per_segment(out):
    final = pd.read_parquet(FINAL, columns=["segment_id"])
    assert out["segment_id"].is_unique
    assert set(out["segment_id"]) == set(final["segment_id"])
    assert out.crs == "EPSG:25832"


def test_value_domains(out):
    assert set(out["fit_class"].dropna()) <= set(pf.FIT_CLASSES)
    assert set(out["fit_class_facade"].dropna()) <= set(pf.FIT_CLASSES)
    assert set(out["cycle_side"].dropna()) <= set(pf.CYCLE_SIDES)
    assert set(out["cycle_facility_final"].dropna()) <= FACILITIES
    assert set(out["lanes_per_dir_soll"].dropna()) <= {"1", "2", "shared"}
    steps = {s for v in out["degrade_steps_applied"].dropna() for s in v.split("|")}
    assert steps <= set(P.cascade_order)
    assert set(out["cat_change_proposal"].dropna()) <= {"GOW30"}


def test_total_matches_elements(out):
    rated = out[out["total_required_m"].notna()]
    totals = rated["profile_elements"].map(lambda s: sum(e["width_m"] for e in json.loads(s)))
    assert (abs(totals - rated["total_required_m"]) < 0.05).all()


def test_fit_class_consistent_with_widths(out):
    r = out[out["fit_class"].notna()]
    fits = r["fit_class"].isin(["fits", "fits_after_degrade"])
    assert (r.loc[fits, "total_required_m"] <= r.loc[fits, "available_m"] + 1e-6).all()
    assert (r.loc[~fits, "total_required_m"] > r.loc[~fits, "available_m"]).all()
    assert r.loc[r["fit_class"] == "fits", "degrade_steps_applied"].isna().all()


def test_never_more_lanes_than_ist(out):
    num = pd.to_numeric(out["lanes_per_dir_soll"], errors="coerce")
    ist = out["lanes_per_dir_ist"]
    known = num.notna() & ist.notna()
    assert (num[known] <= ist[known]).all()


def test_gow30_and_etw_at_most_one_lane(out):
    m = out["cat_final"].isin(["GOW30"])
    assert (out.loc[m, "lanes_per_dir_soll"] == "1").all()
    e = out["cat_final"].isin(["ETW30", "ETW_ERF"])
    assert (out.loc[e, "lanes_per_dir_soll"] == "shared").all()


def test_d5_only_on_gow50(out):
    assert (out.loc[out["cat_change_proposal"].notna(), "cat_final"] == "GOW50").all()


def test_every_profile_has_trace(out):
    rated = out[out["fit_class"].notna()]
    for t in rated["rule_trace_profile"].sample(min(200, len(rated)), random_state=1):
        ids = {s["id"] for s in json.loads(t)}
        assert {"PRF-05", "PRF-06"} <= ids
