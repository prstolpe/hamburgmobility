"""Checks on the real data/interim/segments_conflated.parquet (skipped until `make conflate` has run)."""

import geopandas as gpd
import pandas as pd
import pytest

from pipeline.lib.manifest import REPO_ROOT

SEGMENTS = REPO_ROOT / "data" / "interim" / "segments.parquet"
CONFLATED = REPO_ROOT / "data" / "interim" / "segments_conflated.parquet"

pytestmark = pytest.mark.skipif(not CONFLATED.exists(), reason="run `make conflate` first")


@pytest.fixture(scope="module")
def out() -> gpd.GeoDataFrame:
    return gpd.read_parquet(CONFLATED)


def test_segment_ids_unchanged(out):
    ids = pd.read_parquet(SEGMENTS, columns=["segment_id"])["segment_id"]
    assert list(out["segment_id"]) == list(ids)


def test_columns(out):
    assert {"match_quality", "in_hvs", "speed_official_kmh", "speed_conditional", "ist_verkehrsberuhigt",
            "conflation_trace"} <= set(out.columns)


def test_match_quality_only_in_work_area(out):
    assert out.loc[out["conflated"], "match_quality"].isin(["exact", "partial", "none"]).all()
    assert out.loc[~out["conflated"], "match_quality"].isna().all()


def test_main_roads_matched(out):
    main = out[out["conflated"] & out["highway"].isin(["primary", "secondary"])]
    assert (main["match_quality"] == "exact").any()
    assert main["in_hvs"].any()
