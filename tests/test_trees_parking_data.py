"""Checks on data/interim/trees_parking.parquet (skipped until `make trees-parking` has run)."""

import numpy as np
import pandas as pd
import pytest

from pipeline.lib import trees_parking as tp
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_design_rules

OUT = REPO_ROOT / "data" / "interim" / "trees_parking.parquet"
pytestmark = pytest.mark.skipif(not OUT.exists(), reason="run `make trees-parking` first")


@pytest.fixture(scope="module")
def out() -> pd.DataFrame:
    return pd.read_parquet(OUT)


def test_one_row_per_segment(out):
    assert out["segment_id"].is_unique


def test_missing_is_never_zero(out):
    for side in ("left", "right"):
        none = out[f"park_src_{side}"] == "none"
        assert out.loc[none, f"park_today_{side}"].isna().all()
        assert out.loc[~none, f"park_today_{side}"].notna().all()
    incomplete = ~out["park_today_complete"]
    assert out.loc[incomplete, "park_today"].isna().all()
    assert out.loc[incomplete, ["park_change_min", "park_change_max"]].isna().all().all()


def test_ranges_ordered(out):
    t = out.dropna(subset=["park_target_min", "park_target_max"])
    assert (t["park_target_min"] <= t["park_target_max"] + 1e-9).all()
    tr = out.dropna(subset=["trees_affected_min"])
    assert (tr["trees_affected_min"] <= tr["trees_affected_mid"]).all()
    assert (tr["trees_affected_mid"] <= tr["trees_affected_max"]).all()
    assert (tr["trees_affected_max"] <= tr["trees_n"]).all()


def test_no_negative_values(out):
    cols = ["park_today_left", "park_today_right", "park_target_min", "park_target_max", "trees_new", "usable_left_m"]
    assert (out[cols].fillna(0) >= 0).all().all()


def test_district_sums_match_segments(out):
    s = tp.district_summary(out, tp.Params.from_rules(load_design_rules()))
    bz = [k for k in s if k != "Hamburg"]
    assert sum(s[b]["trees_n"] for b in bz) == s["Hamburg"]["trees_n"] == int(out["trees_n"].sum())
    assert np.isclose(sum(s[b]["park_today_complete"] for b in bz), s["Hamburg"]["park_today_complete"])
