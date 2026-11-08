"""Matching GTFS shapes to street segments, on all cores and with a cache (used by s04 and c06).

The cache in data/interim/cache is only a shortcut: its key covers the feed file, route types, the S-CONF matching
parameters and the segment geometry, so a hit gives the same result as a new computation.
"""

import hashlib
import json

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from pipeline.lib import gtfs, parallel
from pipeline.lib.conflate import MatchParams, zone_share
from pipeline.lib.manifest import REPO_ROOT

CACHE_DIR = REPO_ROOT / "data" / "interim" / "cache"


def match_shapes(seg_geoms: gpd.GeoSeries, shapes: list, mp: MatchParams, min_share: float) -> list[tuple]:
    """Per GTFS shape: (indices of the segments it runs on, direction +1/-1 per segment); shapes in parallel."""
    geoms = seg_geoms.reset_index(drop=True)
    tree = shapely.STRtree(geoms.values)
    empty = (np.array([], dtype=int), np.array([], dtype=int))

    def one(k: int) -> tuple:
        shape = shapes[k]
        idx = tree.query(shape.buffer(mp.buffer_m))
        if len(idx) == 0:
            return empty
        share = zone_share(geoms.iloc[idx], gpd.GeoSeries([shape], crs=seg_geoms.crs), mp).to_numpy()
        hit = idx[share >= min_share]
        if len(hit) == 0:
            return empty
        return hit, np.asarray(gtfs.shape_direction(geoms.iloc[hit], shape))

    return parallel.pmap(one, len(shapes), chunksize=64)


def transit_cache_key(feed_name: str, feed_size: int, route_types: tuple, mp: MatchParams, min_share: float,
                      seg_geoms: gpd.GeoSeries) -> str:
    """Fingerprint of everything the bus matching depends on (feed file, route types, S-CONF parameters, geometry)."""
    h = hashlib.sha256()
    h.update(json.dumps([feed_name, int(feed_size), sorted(route_types), mp.buffer_m, mp.max_angle_deg,
                         mp.min_overlap_share, min_share]).encode())
    for wkb in shapely.to_wkb(shapely.set_precision(seg_geoms.values, 0.001)):
        h.update(wkb)
    return h.hexdigest()[:20]


def transit_peak(seg: gpd.GeoDataFrame, feed_path, route_types: tuple, start_hours: pd.Series, feed: dict,
                 day, mp: MatchParams, min_share: float) -> np.ndarray:
    """PRF-02 (design_rules) / S-FEAT-08 bus_peak_h_dir: trips in the busiest hour of the busier direction per segment
    (0 without a matching shape); used by s04 (bus_route, C-G30-02) and c06.
    Cached in data/interim/cache by transit_cache_key; the cache is only a shortcut, the result is the same."""
    key = transit_cache_key(feed_path.name, feed_path.stat().st_size, route_types, mp, min_share, seg.geometry)
    cache = CACHE_DIR / f"transit_peak_{key}.npy"
    if cache.exists():
        return np.load(cache)
    hist = gtfs.hourly_trips_per_shape(feed, start_hours, day, route_types)
    n = len(seg)
    if hist.empty:
        return np.zeros(n)
    hours = sorted(hist.columns)
    fwd, bwd = np.zeros((n, len(hours))), np.zeros((n, len(hours)))
    shapes = gtfs.shapes_gdf(feed, hist.index)
    matched = match_shapes(seg.geometry, list(shapes.geometry.values), mp, min_share)
    for shape_id, (hit, d) in zip(shapes.index, matched):
        if len(hit) == 0:
            continue
        counts = hist.loc[shape_id, hours].to_numpy(dtype=float)
        fwd[hit[d > 0]] += counts
        bwd[hit[d < 0]] += counts
    out = np.maximum(fwd.max(axis=1), bwd.max(axis=1))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.save(cache, out)
    return out
