"""Coordinate reference systems used by the pipeline (see CLAUDE.md, Konventionen)."""

import geopandas as gpd
from pyproj import CRS

# All computation happens in WORK_CRS; only the export stage transforms to EXPORT_CRS.
WORK_CRS = "EPSG:25832"
EXPORT_CRS = "EPSG:4326"


def to_work_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Return gdf in the working CRS (EPSG:25832).

    Raises ValueError if gdf has no CRS: a missing CRS is never guessed.
    Input already in EPSG:25832 is returned as is; otherwise a reprojected copy is returned.
    """
    if gdf.crs is None:
        raise ValueError("GeoDataFrame has no CRS; set it explicitly before calling to_work_crs().")
    if CRS.from_user_input(gdf.crs) == CRS.from_user_input(WORK_CRS):
        return gdf
    return gdf.to_crs(WORK_CRS)
