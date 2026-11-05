"""Work area: the selected Hamburg Bezirke (config/project.yaml, section area) minus excluded Stadtteile.

s01_fetch selects the Bezirke from the OSM boundaries and writes them to data/raw/work_area.parquet; all later
stages read that file. The work area is the union of the Bezirke buffered by buffer_m (EPSG:25832).
"""

from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import shapely
import yaml

from pipeline.lib.boundary import BoundaryError, _describe
from pipeline.lib.crs import to_work_crs
from pipeline.lib.manifest import REPO_ROOT

PROJECT_PATH = REPO_ROOT / "config" / "project.yaml"
WORK_AREA_PATH = REPO_ROOT / "data" / "raw" / "work_area.parquet"
RURAL_PATH = REPO_ROOT / "data" / "raw" / "rural_excluded.parquet"
NO_DISTRICT = "ohne Bezirk"


@dataclass(frozen=True)
class AreaConfig:
    districts: str | list[str]  # "all" or a list of Bezirk names
    city_name: str
    city_admin_level: int
    district_admin_level: int
    exclude: list[dict]
    buffer_m: float
    rural_admin_level: int = 10
    rural_stadtteile: tuple[str, ...] | list[str] = ()

    @property
    def all_districts(self) -> bool:
        return self.districts == "all"


def load_area_config(path: Path = PROJECT_PATH) -> AreaConfig:
    with open(path, encoding="utf-8") as f:
        a = yaml.safe_load(f)["area"]
    rural = a.get("rural_exclude") or {}
    return AreaConfig(districts=a["districts"], city_name=a["city_name"], city_admin_level=a["city_admin_level"],
                      district_admin_level=a["district_admin_level"], exclude=list(a.get("exclude") or []),
                      buffer_m=float(a["buffer_m"]), rural_admin_level=int(rural.get("admin_level", 10)),
                      rural_stadtteile=list(rural.get("stadtteile") or []))


def _level(gdf: gpd.GeoDataFrame, level: int) -> gpd.GeoDataFrame:
    return gdf[gdf["admin_level"].astype(str) == str(level)]


def _one(boundaries: gpd.GeoDataFrame, name: str, level: int, what: str) -> gpd.GeoDataFrame:
    match = _level(boundaries[boundaries["name"] == name], level)
    if len(match) != 1:
        raise BoundaryError(f"{what}: {len(match)} boundaries named {name!r} with admin_level {level}. "
                            f"Candidates: {_describe(boundaries[boundaries['name'] == name])}")
    return match


def select_districts(boundaries: gpd.GeoDataFrame, cfg: AreaConfig) -> gpd.GeoDataFrame:
    """Bezirke in scope (name, admin_level, id, geometry in EPSG:25832) with excluded Stadtteile cut out.

    Separate polygon parts that contain an excluded Stadtteil are dropped as a whole.
    "all" means every boundary at district_admin_level whose interior point lies in the city boundary; level-9
    areas outside Hamburg in the OSM extract are skipped. Named Bezirke must exist exactly once inside the city.
    """
    b = to_work_crs(boundaries)
    city = _one(b, cfg.city_name, cfg.city_admin_level, "city").geometry.iloc[0]
    level = _level(b, cfg.district_admin_level)
    inside = level[level.geometry.representative_point().within(city)]
    if cfg.all_districts:
        picked = inside
        if picked.empty:
            raise BoundaryError(f"no boundaries with admin_level {cfg.district_admin_level} inside {cfg.city_name}")
    else:
        for name in cfg.districts:
            if (inside["name"] == name).sum() != 1:
                raise BoundaryError(f"Bezirk {name!r}: {(inside['name'] == name).sum()} boundaries with admin_level "
                                    f"{cfg.district_admin_level} inside {cfg.city_name}. "
                                    f"Candidates: {_describe(b[b['name'] == name])}")
        picked = inside[inside["name"].isin(cfg.districts)]
    picked = picked[["name", "admin_level", "id", "geometry"]].copy()
    for ex in cfg.exclude:
        cut = _one(b, ex["name"], ex["admin_level"], "exclude").geometry.iloc[0]
        picked["geometry"] = [_drop_parts(g, cut) for g in picked.geometry]
    picked = picked[~picked.geometry.is_empty]
    return picked.sort_values("name").reset_index(drop=True)


def _drop_parts(geom, cut):
    """Remove `cut` and every separate polygon part touching it (Neuwerk: island plus the Wattenmeer around it)."""
    parts = list(getattr(geom, "geoms", [geom]))
    kept = [p for p in parts if not p.intersects(cut)]
    if len(parts) == 1 or len(kept) == len(parts):  # contiguous Bezirk: cut out only the Stadtteil
        return geom.difference(cut)
    return shapely.union_all(kept) if kept else shapely.Polygon()


def select_rural(boundaries: gpd.GeoDataFrame, cfg: AreaConfig) -> gpd.GeoDataFrame:
    """Rural Stadtteile that are not classified (area.rural_exclude); each must exist once inside the city."""
    b = to_work_crs(boundaries)
    city = _one(b, cfg.city_name, cfg.city_admin_level, "city").geometry.iloc[0]
    level = _level(b, cfg.rural_admin_level)
    inside = level[level.geometry.representative_point().within(city)]
    for name in cfg.rural_stadtteile:
        if (inside["name"] == name).sum() != 1:
            raise BoundaryError(f"rural Stadtteil {name!r}: {(inside['name'] == name).sum()} boundaries with "
                                f"admin_level {cfg.rural_admin_level} inside {cfg.city_name}")
    picked = inside[inside["name"].isin(cfg.rural_stadtteile)][["name", "admin_level", "id", "geometry"]]
    return picked.sort_values("name").reset_index(drop=True)


def classification_area(districts: gpd.GeoDataFrame, rural: gpd.GeoDataFrame, buffer_m: float):
    """Work area for features and classification: Bezirke + buffer minus the rural Stadtteile (unbuffered)."""
    area = build_work_area(districts, buffer_m)
    if rural is None or rural.empty:
        return area
    return area.difference(to_work_crs(rural).geometry.union_all())


def build_work_area(districts: gpd.GeoDataFrame, buffer_m: float):
    """Union of the Bezirke buffered by buffer_m (EPSG:25832)."""
    return to_work_crs(districts).geometry.union_all().buffer(buffer_m)


def read_districts(path: Path = WORK_AREA_PATH) -> gpd.GeoDataFrame:
    """Bezirke in scope as written by s01_fetch."""
    if not path.exists():
        raise BoundaryError(f"{path.relative_to(REPO_ROOT)} missing: run make fetch first")
    return to_work_crs(gpd.read_parquet(path))


def read_rural(path: Path = RURAL_PATH) -> gpd.GeoDataFrame:
    """Rural Stadtteile as written by s01_fetch (empty if none are configured)."""
    if not path.exists():
        raise BoundaryError(f"{path.relative_to(REPO_ROOT)} missing: run make fetch first")
    return to_work_crs(gpd.read_parquet(path))


def read_work_area(cfg: AreaConfig | None = None, path: Path = WORK_AREA_PATH, exclude_rural: bool = True):
    """Classification area (default) or, with exclude_rural=False, the whole area incl. rural Stadtteile."""
    cfg = cfg or load_area_config()
    districts = read_districts(path)
    if not exclude_rural:
        return build_work_area(districts, cfg.buffer_m)
    return classification_area(districts, read_rural(), cfg.buffer_m)


def district_names(path: Path = WORK_AREA_PATH) -> list[str]:
    return sorted(read_districts(path)["name"])


def area_label(names: list[str]) -> str:
    """'Hamburg' for the whole city, otherwise the Bezirk names (for report headings)."""
    return ", ".join(names) if len(names) <= 2 else f"Hamburg ({len(names)} Bezirke)"


def sample_by_district(df, n: int, seed: int, id_col: str = "segment_id", key: str = "bezirk"):
    """n random rows spread over the Bezirke in proportion to their row count, at least one per Bezirk.

    Reproducible: rows are sorted by id_col before sampling with random.Random(seed). Returns rows sorted by
    Bezirk and id.
    """
    import random

    if len(df) <= n:
        return df.sort_values([key, id_col])
    counts = df[key].fillna(NO_DISTRICT).value_counts().sort_index()
    quota = {k: 1 for k in counts.index}
    rest = n - len(quota)
    if rest > 0:
        share = (counts - 1) / (counts - 1).sum() * rest
        base = share.astype(int)
        order = (share - base).sort_values(ascending=False, kind="stable").index
        for k in counts.index:
            quota[k] += int(base[k])
        for k in order[: rest - int(base.sum())]:
            quota[k] += 1
    rng = random.Random(seed)
    picked = []
    for k in counts.index:
        ids = sorted(df.loc[df[key].fillna(NO_DISTRICT) == k, id_col])
        picked += rng.sample(ids, min(quota[k], len(ids)))
    return df[df[id_col].isin(picked)].sort_values([key, id_col])


def in_scope(df, names: list[str], key: str = "bezirk"):
    """Mask: rows in one of the Bezirke in scope."""
    return df[key].isin(names)
