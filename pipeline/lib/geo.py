"""Geometry helpers shared by the fetchers."""

import json

import geopandas as gpd
from shapely.geometry import box

from pipeline.lib.crs import WORK_CRS, to_work_crs
from pipeline.lib.http import FetchError

Bbox = tuple[float, float, float, float]


def features_to_gdf(features: list[dict], crs: str = WORK_CRS) -> gpd.GeoDataFrame:
    if not features:
        return gpd.GeoDataFrame(geometry=[], crs=crs)
    return gpd.GeoDataFrame.from_features(features, crs=crs)


def tile_bboxes(area, size_m: float) -> list[Bbox]:
    """Square tiles of size_m (grid anchored at multiples of size_m) that intersect the area."""
    import math
    x0, y0, x1, y1 = area.bounds
    tiles = []
    for i in range(math.floor(x0 / size_m), math.ceil(x1 / size_m)):
        for j in range(math.floor(y0 / size_m), math.ceil(y1 / size_m)):
            t = (float(i * size_m), float(j * size_m), float((i + 1) * size_m), float((j + 1) * size_m))
            if box(*t).intersects(area):
                tiles.append(t)
    return tiles


def check_in_bbox(gdf: gpd.GeoDataFrame, bbox: Bbox, label: str) -> None:
    """Every feature must touch the requested bbox; catches swapped axes and wrong CRS."""
    if gdf.empty:
        return
    outside = ~gdf.geometry.intersects(box(*bbox).buffer(1.0))
    if outside.any():
        raise FetchError(f"{label}: {int(outside.sum())} of {len(gdf)} features outside the requested bbox "
                         f"(axis order or CRS wrong?)")


def clean(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """make_valid, drop empty geometries and exact duplicates, project to the working CRS."""
    gdf = to_work_crs(gdf)
    if gdf.empty:
        return gdf
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()
    gdf["geometry"] = gdf.geometry.make_valid()
    attrs = gdf.drop(columns="geometry")
    props = attrs.apply(lambda row: json.dumps([None if v is None or v != v else v for v in row], default=str),
                        axis=1) if attrs.shape[1] else ""
    key = gdf.geometry.to_wkb(hex=True) + "|" + props
    return gdf[~key.duplicated()].reset_index(drop=True)


def keep_intersecting(gdf: gpd.GeoDataFrame, area) -> gpd.GeoDataFrame:
    """Keep whole features that intersect the area (no cutting, so edge segments stay complete)."""
    if gdf.empty:
        return gdf
    return gdf[gdf.geometry.intersects(area)].reset_index(drop=True)


def parquet_safe(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Make object columns writable by pyarrow: dict/list -> JSON, mixed types -> str."""
    gdf = gdf.copy()
    for col in gdf.columns:
        if col == "geometry" or gdf[col].dtype != object:
            continue
        values = gdf[col].map(lambda v: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v)
        types = {type(v) for v in values if v is not None and v == v}
        if len(types) > 1:
            values = values.map(lambda v: None if v is None or v != v else str(v))
        gdf[col] = values
    return gdf
