"""District boundaries from OSM (selection of several Bezirke: pipeline/lib/area.py)."""

from pathlib import Path

import geopandas as gpd

from pipeline.lib.crs import to_work_crs


class BoundaryError(RuntimeError):
    """District boundary missing or ambiguous."""


def _describe(candidates: gpd.GeoDataFrame) -> str:
    rows = [f"{r['name']} (admin_level {r['admin_level']}, {r.geometry.area / 1e6:.1f} km²)"
            for _, r in to_work_crs(candidates).iterrows()]
    return "; ".join(rows) or "none"


def select_district(boundaries: gpd.GeoDataFrame, name: str, admin_level: int | None) -> gpd.GeoDataFrame:
    """Exactly one boundary with this name and admin_level; never guesses the level."""
    candidates = boundaries[boundaries["name"] == name]
    if admin_level is None:
        raise BoundaryError(f"admin_level for {name!r} not set in config/project.yaml. "
                            f"Candidates: {_describe(candidates)}")
    match = candidates[candidates["admin_level"].astype(str) == str(admin_level)]
    if len(match) != 1:
        raise BoundaryError(f"{len(match)} boundaries named {name!r} with admin_level {admin_level}. "
                            f"Candidates: {_describe(candidates)}")
    return to_work_crs(match.reset_index(drop=True))


def buffered_area(district: gpd.GeoDataFrame, buffer_m: float):
    """Union of the district geometry buffered by buffer_m (EPSG:25832)."""
    return to_work_crs(district).geometry.union_all().buffer(buffer_m)


def boundaries_from_pbf(pbf_path: str | Path) -> gpd.GeoDataFrame:
    """All administrative boundaries in the PBF (name, admin_level, geometry)."""
    from pyrosm import OSM

    gdf = OSM(str(pbf_path)).get_boundaries(boundary_type="administrative")
    if gdf is None or gdf.empty:
        raise BoundaryError(f"no administrative boundaries in {pbf_path}")
    return gdf[["name", "admin_level", "id", "geometry"]]
