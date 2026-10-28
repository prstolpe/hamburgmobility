"""Checks on the real data/interim/classified.parquet (skipped until `make classify` has run)."""

import json

import pandas as pd
import pytest

from pipeline.lib.classify import classify_segment
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_rules
from pipeline.s05_classify import classification_inputs

IN = REPO_ROOT / "data" / "interim" / "crosssection.parquet"
OUT = REPO_ROOT / "data" / "interim" / "classified.parquet"
SAMPLE = REPO_ROOT / "reports" / "classification_sample.csv"

pytestmark = pytest.mark.skipif(not OUT.exists(), reason="run `make classify` first")


@pytest.fixture(scope="module")
def out() -> pd.DataFrame:
    return pd.read_parquet(OUT)


def test_segment_ids_unchanged(out):
    assert list(out["segment_id"]) == list(pd.read_parquet(IN, columns=["segment_id"])["segment_id"])


def test_columns(out):
    assert {"cat_proposed", "confidence", "confidence_reasons", "rule_path", "rule_trace"} <= set(out.columns)


def test_only_work_area_classified(out):
    area = out["conflated"].astype(bool)
    assert out.loc[area, "cat_proposed"].notna().all()
    assert out.loc[~area, "cat_proposed"].isna().all()
    assert out.loc[area, "confidence"].isin(["hoch", "mittel", "niedrig"]).all()


def test_hvs_is_never_etw(out):
    hvs = out["in_hvs"].fillna(False).astype(bool)
    assert not out.loc[hvs, "cat_proposed"].isin(["ETW30", "ETW_ERF", "ETW60"]).any()


def test_trace_matches_category(out):
    """Re-running a few rows gives the stored category and trace (reproducible)."""
    rules = load_rules()
    rows = out[out["conflated"].astype(bool)].sample(50, random_state=1)
    for _, r in rows.iterrows():
        again = classify_segment(r[classification_inputs(rules)].to_dict(), rules)
        assert again["cat_proposed"] == r["cat_proposed"]
        assert json.dumps(again["rule_trace"], ensure_ascii=False) == r["rule_trace"]


def test_sample_csv(out):
    s = pd.read_csv(SAMPLE)
    assert s.groupby("cat_proposed").size().max() <= 30
    assert s["orthophoto"].str.contains("MAP/LAYERIDS=").all()
    assert s["panoramax"].str.contains("#focus=map&map=").all()
