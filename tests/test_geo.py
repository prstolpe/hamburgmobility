import geopandas as gpd
from shapely.geometry import LineString, Polygon, box

from pipeline.lib.geo import clean, keep_intersecting, parquet_safe


def test_clean_drops_exact_duplicates_with_missing_values():
    line = LineString([(0, 0), (10, 0)])
    gdf = gpd.GeoDataFrame({"a": [1.0, 1.0, None], "b": [None, None, "x"]},
                           geometry=[line, line, line], crs="EPSG:25832")
    assert len(clean(gdf)) == 2


def test_clean_repairs_invalid_geometry_and_projects():
    bowtie = Polygon([(0, 0), (1, 1), (1, 0), (0, 1)])
    gdf = gpd.GeoDataFrame({"a": [1]}, geometry=[bowtie], crs="EPSG:25832")
    assert clean(gdf).geometry.is_valid.all()
    wgs = gpd.GeoDataFrame({"a": [1]}, geometry=[LineString([(9.9, 53.5), (9.91, 53.5)])], crs="EPSG:4326")
    assert clean(wgs).crs.to_epsg() == 25832


def test_keep_intersecting_keeps_whole_features():
    line = LineString([(0, 0), (100, 0)])
    gdf = gpd.GeoDataFrame({"a": [1]}, geometry=[line], crs="EPSG:25832")
    kept = keep_intersecting(gdf, box(-1, -1, 10, 1))
    assert kept.length.iloc[0] == 100


def test_parquet_safe_serialises_mixed_columns(tmp_path):
    gdf = gpd.GeoDataFrame({"m": [{"k": 1}, 2, "x", None]}, geometry=[LineString([(0, 0), (1, 0)])] * 4,
                           crs="EPSG:25832")
    path = tmp_path / "x.parquet"
    parquet_safe(gdf).to_parquet(path)
    values = gpd.read_parquet(path)["m"]
    assert values.iloc[:3].tolist() == ['{"k": 1}', "2", "x"]
    assert values.isna().iloc[3]
