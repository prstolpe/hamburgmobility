"""Checks on the real data/interim/validation.parquet (skipped until `make validate` has run)."""

import json

import pandas as pd
import pytest

from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_rules

DISC = REPO_ROOT / "data" / "interim" / "discrepancy.parquet"
OUT = REPO_ROOT / "data" / "interim" / "validation.parquet"

pytestmark = pytest.mark.skipif(not OUT.exists(), reason="run `make validate` first")


@pytest.fixture(scope="module")
def out() -> pd.DataFrame:
    return pd.read_parquet(OUT)


def test_covers_work_area(out):
    d = pd.read_parquet(DISC, columns=["segment_id", "conflated", "cat_final"])
    area = d[d["conflated"].astype(bool) & d["cat_final"].notna()]
    assert out["segment_id"].is_unique
    assert set(out["segment_id"]) == set(area["segment_id"])


def test_rates_and_flag_consistent(out):
    rules = load_rules()
    min_rate = rules.validation.rule("V-UNC-01").thresholds["min_change_rate"].value
    assert out["sens_change_rate"].between(0, 1).all()
    assert (out["sens_uncertain"] == (out["sens_change_rate"] >= min_rate - 1e-12)).all()
    changed = out["sens_change_rate"] > 0
    assert out.loc[changed, "sens_alt_category"].notna().all()
    assert out.loc[~changed, "sens_alt_category"].isna().all()
    assert (out["sens_alt_share"] <= out["sens_change_rate"] + 1e-12).all()


def test_oat_changes_are_json_lists(out):
    lists = out["sens_oat_changes"].map(json.loads)
    assert lists.map(lambda x: isinstance(x, list)).all()
    assert all(":" in k for ks in lists for k in ks)
