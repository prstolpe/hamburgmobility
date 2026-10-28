"""Checks on the real data/interim/crosssection.parquet (skipped until `make crosssection` has run)."""

import json

import geopandas as gpd
import pandas as pd
import pytest

from pipeline.lib.manifest import REPO_ROOT

FEATURES = REPO_ROOT / "data" / "interim" / "features.parquet"
OUT = REPO_ROOT / "data" / "interim" / "crosssection.parquet"
SAMPLE = REPO_ROOT / "reports" / "transect_sample.geojson"

pytestmark = pytest.mark.skipif(not OUT.exists(), reason="run `make crosssection` first")


@pytest.fixture(scope="module")
def out() -> pd.DataFrame:
    return pd.read_parquet(OUT)


def test_segment_ids_unchanged(out):
    assert list(out["segment_id"]) == list(pd.read_parquet(FEATURES, columns=["segment_id"])["segment_id"])


def test_columns(out):
    assert {"width_median_m", "width_p10_m", "width_min_m", "narrow_points", "facade_width_p10_m",
            "width_ratio_GOW50", "feasibility_GOW50", "feasibility_GOW30_narrow", "feasibility_ETW30",
            "crosssection_trace", "conn_score"} <= set(out.columns)


def test_widths_only_in_work_area_and_ordered(out):
    assert out.loc[~out["conflated"], "width_p10_m"].isna().all()
    a = out.dropna(subset=["width_p10_m"])
    assert (a["width_min_m"] <= a["width_p10_m"] + 1e-9).all() and (a["width_p10_m"] <= a["width_median_m"] + 1e-9).all()


def test_feasibility_classes_valid(out):
    for col in ("feasibility_GOW50", "feasibility_GOW30_narrow", "feasibility_ETW30"):
        assert set(out[col].dropna()) <= {"fits", "tight", "does_not_fit"}
        assert out.loc[out["width_p10_m"].isna(), col].isna().all()


def test_narrow_points_json(out):
    for v in out.loc[out["conflated"], "narrow_points"].head(200):
        assert isinstance(json.loads(v), list)


def test_transect_sample_for_manual_measurement():
    g = gpd.read_file(SAMPLE)
    assert len(g) == 50 and g["transect_id"].is_unique
    assert g.crs.to_epsg() == 4326 and g["width_traffic_m"].notna().all()
