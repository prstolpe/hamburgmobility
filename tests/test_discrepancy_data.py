"""Checks on the real data/interim/discrepancy.parquet (skipped until `make discrepancy` has run)."""

import json

import pandas as pd
import pytest

from pipeline.lib.accidents import AGG_COLUMNS
from pipeline.lib.manifest import REPO_ROOT

FINAL = REPO_ROOT / "data" / "interim" / "final.parquet"
OUT = REPO_ROOT / "data" / "interim" / "discrepancy.parquet"

pytestmark = pytest.mark.skipif(not OUT.exists(), reason="run `make discrepancy` first")


@pytest.fixture(scope="module")
def out() -> pd.DataFrame:
    return pd.read_parquet(OUT)


def test_segments_unchanged(out):
    final = pd.read_parquet(FINAL, columns=["segment_id", "cat_final"])
    assert list(out["segment_id"]) == list(final["segment_id"])
    assert out["cat_final"].fillna("–").equals(final["cat_final"].fillna("–"))


def test_no_single_crash_data(out):
    forbidden = {"UIDENTSTLAE", "LINREFX", "LINREFY", "XGCSWGS84", "YGCSWGS84", "UMONAT", "USTUNDE", "UWOCHENTAG"}
    assert not forbidden & set(out.columns)
    for c in AGG_COLUMNS:
        assert pd.api.types.is_numeric_dtype(out[c])


def test_only_classified_work_area_is_assessed(out):
    assessed = out["disc_trace"].notna()
    assert (assessed == (out["conflated"].astype(bool) & out["cat_final"].notna())).all()


def test_values_in_range_and_consistent(out):
    a = out[out["disc_trace"].notna()]
    for c in ("disc_speed", "disc_design", "disc_use"):
        assert a[c].dropna().between(0, 3).all()
    assert a["priority"].dropna().between(0, 3).all()
    assert a["risk"].dropna().between(0, 1).all()
    no_disc = a["disc_max"].fillna(0) == 0
    assert a.loc[no_disc, "disc_type"].isna().all()
    assert a.loc[~no_disc, "disc_type"].isin(["D1", "D2", "D3"]).all()
    assert (a.loc[a["disc_max"] == 0, "priority"] == 0).all()


def test_trace_names_all_rules(out):
    a = out[out["disc_trace"].notna()]
    for trace in a["disc_trace"].sample(min(200, len(a)), random_state=1):
        rules = [s["rule"] for s in json.loads(trace)]
        assert rules == ["D-SPD-01", "D-DES-01", "D-USE-01", "D-TYPE-01", "P-RISK-01", "priority"]


def test_crash_counts_consistent(out):
    a = out[out["disc_trace"].notna()]
    assert (a["crashes_ped"] <= a["crashes_ped_cyc"]).all() and (a["crashes_cyc"] <= a["crashes_ped_cyc"]).all()
    assert (a["crashes_ped"] + a["crashes_cyc"] >= a["crashes_ped_cyc"]).all()
    assert (a["crashes_severe_fatal"] <= a["crashes_ped_cyc"]).all()
