"""Checks on the real data/interim/harmonised.parquet (skipped until `make classify` has run)."""

import json

import pandas as pd
import pytest

from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_rules

IN = REPO_ROOT / "data" / "interim" / "classified.parquet"
OUT = REPO_ROOT / "data" / "interim" / "harmonised.parquet"

pytestmark = pytest.mark.skipif(not (IN.exists() and OUT.exists()), reason="run `make classify` first")


@pytest.fixture(scope="module")
def out() -> pd.DataFrame:
    return pd.read_parquet(OUT, columns=["segment_id", "conflated", "cat_cascade", "cat_proposed", "rule_trace", "rule_path"])


def test_ids_and_cascade_unchanged(out):
    inp = pd.read_parquet(IN, columns=["segment_id", "cat_proposed"])
    assert list(out["segment_id"]) == list(inp["segment_id"])
    assert out["cat_cascade"].fillna("–").equals(inp["cat_proposed"].fillna("–"))


def test_changed_segments_have_a_trace(out):
    changed = out[out["cat_cascade"].notna() & (out["cat_cascade"] != out["cat_proposed"])]
    assert len(changed) > 0
    for t, p in zip(changed["rule_trace"], changed["rule_path"]):
        assert json.loads(t)[-1]["id"] == "H-STR-01" and p.endswith("H-STR-01")


def test_locked_categories_unchanged(out):
    locked = set(load_rules().harmonisation.rule("H-STR-01").locked_categories)
    m = out["cat_cascade"].isin(locked)
    assert (out.loc[m, "cat_proposed"] == out.loc[m, "cat_cascade"]).all()
