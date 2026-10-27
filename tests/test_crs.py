import geopandas as gpd
import pytest
from pyproj import Transformer
from shapely.geometry import Point

from pipeline.lib.crs import WORK_CRS, to_work_crs

# A point in Hamburg (lon, lat); exact value is irrelevant, it only needs to be in the UTM 32 area.
LON, LAT = 9.99, 53.55


def _gdf(crs):
    return gpd.GeoDataFrame({"id": [1]}, geometry=[Point(LON, LAT)], crs=crs)


def test_transforms_wgs84_to_work_crs():
    result = to_work_crs(_gdf("EPSG:4326"))

    expected_x, expected_y = Transformer.from_crs(
        "EPSG:4326", "EPSG:25832", always_xy=True
    ).transform(LON, LAT)
    assert result.crs.to_epsg() == 25832
    assert result.geometry.iloc[0].x == pytest.approx(expected_x, abs=1e-6)
    assert result.geometry.iloc[0].y == pytest.approx(expected_y, abs=1e-6)


def test_work_crs_input_is_unchanged():
    gdf = gpd.GeoDataFrame(
        {"id": [1]}, geometry=[Point(565000.0, 5933000.0)], crs=WORK_CRS
    )
    result = to_work_crs(gdf)

    assert result.crs.to_epsg() == 25832
    assert result.geometry.iloc[0].equals(gdf.geometry.iloc[0])


def test_missing_crs_raises():
    with pytest.raises(ValueError):
        to_work_crs(_gdf(None))


def test_input_is_not_modified():
    gdf = _gdf("EPSG:4326")
    to_work_crs(gdf)

    assert gdf.crs.to_epsg() == 4326
    assert gdf.geometry.iloc[0].x == LON


def test_empty_gdf():
    empty = gpd.GeoDataFrame({"id": []}, geometry=[], crs="EPSG:4326")
    result = to_work_crs(empty)

    assert result.empty
    assert result.crs.to_epsg() == 25832
