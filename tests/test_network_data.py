"""Checks on the real data/interim/segments.parquet (skipped until `make network` has run)."""

import geopandas as gpd
import pytest

from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_rules

SEGMENTS = REPO_ROOT / "data" / "interim" / "segments.parquet"

pytestmark = pytest.mark.skipif(not SEGMENTS.exists(), reason="run `make network` first")


@pytest.fixture(scope="module")
def seg() -> gpd.GeoDataFrame:
    return gpd.read_parquet(SEGMENTS)


def test_crs(seg):
    assert seg.crs == "EPSG:25832"


def test_geometries_valid_and_not_empty(seg):
    assert seg.geometry.is_valid.all()
    assert (seg["length_m"] > 0).all()


def test_ids_unique(seg):
    assert seg["segment_id"].is_unique
    assert seg["segment_id"].str.fullmatch(r"seg_[0-9a-f]{16}").all()


def test_columns(seg):
    assert {"segment_id", "osm_way_ids", "highway", "name", "length_m", "bezirk"} <= set(seg.columns)


def test_highway_classes_from_rules(seg):
    assert set(seg["highway"]) <= set(load_rules().network.highway_classes.values)
