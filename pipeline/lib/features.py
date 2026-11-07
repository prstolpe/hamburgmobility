"""Feature helpers for stage 4 (rules S-FEAT-01..10 in config/rules.yaml).

All parameters come in through FeatureParams (from rules.yaml); there are no thresholds here.
Geometries must be in the working CRS (metres). Missing values stay None/NaN, never filled.
"""

import re
from dataclasses import dataclass

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from config.schema.rules_model import RuleSet

DEFAULT_SPEED_PREFIX = "default_speed_"


@dataclass(frozen=True)
class FeatureParams:
    ties: str
    default_speed_kmh: dict[str, float]
    exclude_highway: tuple[str, ...]
    building_buffer_m: float
    population_buffer_m: float
    frontage_buffer_m: float
    amenity_excluded: frozenset[str]
    alkis_gebnutzbez: frozenset[str]
    alkis_rellage_excluded: frozenset[str]
    alkis_public_functions: frozenset[str]
    alkis_ancillary_functions: frozenset[str]
    bus_route_types: tuple[int, ...]
    node_snap_m: float

    @classmethod
    def from_rules(cls, rules: RuleSet) -> "FeatureParams":
        f = rules.features
        b = f.rule("S-FEAT-02")
        speeds = {k.removeprefix(DEFAULT_SPEED_PREFIX): t.value
                  for k, t in b.thresholds.items() if k.startswith(DEFAULT_SPEED_PREFIX)}
        return cls(
            ties=f.rule("S-FEAT-01").ties,
            default_speed_kmh=speeds,
            exclude_highway=tuple(b.exclude_highway),
            building_buffer_m=f.rule("S-FEAT-03").thresholds["buffer_m"].value,
            population_buffer_m=f.rule("S-FEAT-04").thresholds["buffer_m"].value,
            frontage_buffer_m=f.rule("S-FEAT-05").thresholds["buffer_m"].value,
            amenity_excluded=frozenset(f.rule("S-FEAT-05").amenity_excluded),
            alkis_gebnutzbez=frozenset(f.rule("S-FEAT-03").alkis_gebnutzbez),
            alkis_rellage_excluded=frozenset(f.rule("S-FEAT-03").alkis_rellage_excluded),
            alkis_public_functions=frozenset(f.rule("S-FEAT-05").alkis_public_functions),
            alkis_ancillary_functions=frozenset(f.rule("S-FEAT-05").alkis_ancillary_functions),
            bus_route_types=tuple(f.rule("S-FEAT-08").route_types),
            node_snap_m=f.rule("S-FEAT-10").thresholds["node_snap_m"].value,
        )


# --- S-FEAT-01 normalisation and scores ------------------------------------------------------


TIES = ("min", "average")


def percentile_rank(values: pd.Series, mask: pd.Series | None = None, *, ties: str) -> pd.Series:
    """Percentile rank 0-1 over the known values (where mask is True): (rank - 1) / (n - 1).

    ties='min': equal values get the lowest rank of their group (smallest value -> 0; no spread -> 0).
    ties='average': equal values get the mean rank (no spread -> 0.5). Unknown -> NaN.
    """
    if ties not in TIES:
        raise ValueError(f"ties must be one of {TIES}, got {ties!r}")
    v = pd.to_numeric(values, errors="coerce").astype("float64")
    if mask is not None:
        v = v.where(mask.astype(bool).to_numpy())
    known = v.notna()
    out = pd.Series(np.nan, index=values.index, dtype="float64")
    n = int(known.sum())
    if n == 0:
        return out
    if n == 1:
        out[known] = 0.0 if ties == "min" else 0.5
        return out
    ranks = v[known].rank(method=ties)
    out[known] = (ranks - 1) / (n - 1)
    return out


def weighted_score(norms: pd.DataFrame, weights: dict[str, float]) -> tuple[pd.Series, pd.Series]:
    """Weighted sum of normalised features; missing features' weights move to the available ones.

    Returns (score, weight_available): weight_available is the sum of the weights that had a value.
    """
    cols = list(weights)
    data = norms[cols].apply(pd.to_numeric, errors="coerce").astype("float64")
    w = pd.Series(weights, dtype="float64")
    present = data.notna()
    available = present.mul(w, axis=1).sum(axis=1)
    weighted = data.fillna(0.0).mul(w, axis=1).sum(axis=1)
    score = (weighted / available).where(available > 0)
    return score, available


# --- S-FEAT-02 / S-FEAT-09 speeds ------------------------------------------------------------

_NUMBER = re.compile(r"^\s*(\d+)\s*$")


def parse_osm_speed(text) -> int | None:
    """Numeric OSM maxspeed ('30') -> 30. Several values ('50 / 30'), 'walk', 'none', 'DE:urban' -> None."""
    if not isinstance(text, str):
        return None
    m = _NUMBER.match(text)
    return int(m.group(1)) if m else None


def _known(v) -> bool:
    return v is not None and not pd.isna(v)


def travel_speed_kmh(official, osm_text, highway: str, defaults: dict[str, float]):
    """Speed for travel times: official before numeric OSM maxspeed before the default of the class."""
    if _known(official):
        return int(official), "official"
    osm = parse_osm_speed(osm_text)
    if osm is not None:
        return osm, "osm"
    if highway in defaults:
        return defaults[highway], "default"
    return None, None


def ist_speed(official, osm_text):
    """Actual speed limit: official before OSM. Returns (speed, source, conflict)."""
    osm = parse_osm_speed(osm_text)
    if _known(official):
        return int(official), "official", osm is not None and osm != int(official)
    if osm is not None:
        return osm, "osm", False
    return None, None, False


# --- S-FEAT-03..06 surroundings --------------------------------------------------------------


def _pairs(seg_buffers: gpd.GeoSeries, other: gpd.GeoSeries) -> tuple[np.ndarray, np.ndarray]:
    """Index pairs (segment position, other position) whose geometries intersect."""
    if other.empty or seg_buffers.empty:
        return np.array([], dtype=int), np.array([], dtype=int)
    tree = shapely.STRtree(other.to_numpy())
    i_seg, i_other = tree.query(seg_buffers.to_numpy(), predicate="intersects")
    return i_seg, i_other


def building_density(seg: gpd.GeoSeries, buildings: gpd.GeoSeries, buffer_m: float) -> pd.Series:
    """S-FEAT-03: building footprint area inside the buffer / buffer area (0-1)."""
    buf = seg.buffer(buffer_m)
    i_seg, i_b = _pairs(buf, buildings)
    area = np.zeros(len(seg))
    if len(i_seg):
        inter = shapely.area(shapely.intersection(buf.to_numpy()[i_seg], buildings.to_numpy()[i_b]))
        np.add.at(area, i_seg, inter)
    return pd.Series(area / buf.area.to_numpy(), index=seg.index)


def area_weighted_sum(seg: gpd.GeoSeries, cells: gpd.GeoDataFrame, column: str, buffer_m: float) -> pd.Series:
    """S-FEAT-04: sum of cells[column] weighted by the share of each cell's area inside the buffer."""
    buf = seg.buffer(buffer_m)
    i_seg, i_c = _pairs(buf, cells.geometry)
    total = np.zeros(len(seg))
    if len(i_seg):
        geoms = cells.geometry.to_numpy()
        share = shapely.area(shapely.intersection(buf.to_numpy()[i_seg], geoms[i_c])) / shapely.area(geoms[i_c])
        np.add.at(total, i_seg, share * cells[column].to_numpy(dtype="float64")[i_c])
    return pd.Series(total, index=seg.index)


def alkis_buildings(buildings: gpd.GeoDataFrame, params: "FeatureParams") -> gpd.GeoDataFrame:
    """S-FEAT-03/05: above-ground ALKIS buildings with flags 'public' (building function) and 'ancillary'."""
    keep = buildings["gebnutzbez"].isin(params.alkis_gebnutzbez) & ~buildings["rellage"].isin(params.alkis_rellage_excluded)
    out = buildings[keep].reset_index(drop=True)
    out["public"] = out["funktion"].isin(params.alkis_public_functions)
    out["ancillary"] = out["funktion"].isin(params.alkis_ancillary_functions)
    return out


def _public(df: pd.DataFrame, amenity_excluded: frozenset[str]) -> np.ndarray:
    """Column 'public' if present, or shop=* / amenity=* not in the excluded list."""
    base = df["public"].fillna(False).to_numpy(dtype=bool) if "public" in df else np.zeros(len(df), bool)
    shop = df["shop"].notna().to_numpy() if "shop" in df else np.zeros(len(df), bool)
    amenity = df["amenity"] if "amenity" in df else pd.Series([None] * len(df), index=df.index)
    am = (amenity.notna() & ~amenity.isin(amenity_excluded)).to_numpy()
    return base | shop | am


def frontage_share(seg: gpd.GeoSeries, buildings: gpd.GeoDataFrame, pois: gpd.GeoDataFrame, buffer_m: float,
                   amenity_excluded: frozenset[str]) -> tuple[pd.Series, pd.Series, pd.Series]:
    """S-FEAT-05: share of buildings in the buffer with public use (tag on the building or POI inside).

    Buildings flagged 'ancillary' (garages, sheds, ...) are left out. Returns (share, n_buildings, n_public);
    share is 0 where no building is in the buffer (no public use; rules.yaml 0.16.0).
    """
    if "ancillary" in buildings:
        buildings = buildings[~buildings["ancillary"].fillna(False).to_numpy(dtype=bool)].reset_index(drop=True)
    public = _public(buildings, amenity_excluded)
    if len(pois) and len(buildings):
        poi_pub = pois[_public(pois, amenity_excluded)]
        if len(poi_pub):
            pts = shapely.point_on_surface(poi_pub.geometry.to_numpy())
            i_b, _ = shapely.STRtree(pts).query(buildings.geometry.to_numpy(), predicate="contains")
            public[np.unique(i_b)] = True
    i_seg, i_b = _pairs(seg.buffer(buffer_m), buildings.geometry)
    n_total = np.bincount(i_seg, minlength=len(seg))
    n_public = np.bincount(i_seg, weights=public[i_b].astype(float), minlength=len(seg)).astype(int)
    share = np.where(n_total > 0, n_public / np.maximum(n_total, 1), 0.0)
    return (pd.Series(share, index=seg.index), pd.Series(n_total, index=seg.index),
            pd.Series(n_public, index=seg.index))


def nearest_distance(seg: gpd.GeoSeries, targets: gpd.GeoSeries) -> pd.Series:
    """S-FEAT-06: distance from each segment to the nearest target geometry (NaN if there is none)."""
    if targets.empty:
        return pd.Series(np.nan, index=seg.index)
    tree = shapely.STRtree(targets.to_numpy())
    (i_seg, _), dist = tree.query_nearest(seg.to_numpy(), return_distance=True, all_matches=False)
    out = np.full(len(seg), np.nan)
    out[i_seg] = dist
    return pd.Series(out, index=seg.index)


def count_near(seg: gpd.GeoSeries, points: gpd.GeoSeries, snap_m: float) -> pd.Series:
    """S-FEAT-10: number of points at most snap_m from each segment."""
    i_seg, _ = _pairs(seg.buffer(snap_m), points)
    return pd.Series(np.bincount(i_seg, minlength=len(seg)), index=seg.index)


# --- S-FEAT-10 OSM design tags ---------------------------------------------------------------

_SIDES = ("both", "left", "right")
_TRACK = {"track", "opposite_track", "separate"}
_LANE = {"lane", "opposite_lane"}
_PARK_NO = {"no", "no_parking", "no_stopping", "fire_lane"}
_PARK_ON_CARRIAGEWAY = {"lane", "half_on_kerb", "shoulder"}
_PARK_ALONG = {"lane", "half_on_kerb", "on_kerb", "street_side", "shoulder"}
_ORIENTATIONS = {"parallel", "diagonal", "perpendicular"}
# Old scheme parking:lane:<side>:<orientation>=<position>; on_street means on the carriageway.
_OLD_POSITION = {"on_street": "lane", "painted_area_only": "lane", "half_on_kerb": "half_on_kerb",
                 "on_kerb": "on_kerb", "street_side": "street_side", "shoulder": "shoulder", "lay_by": "street_side"}


def _side_values(tags: dict, prefix: str) -> dict[str, str]:
    """Values of <prefix>, <prefix>:both|left|right per side ('left'/'right')."""
    out: dict[str, str] = {}
    for key in (prefix, f"{prefix}:both"):
        if isinstance(tags.get(key), str):
            out["left"] = out["right"] = tags[key]
    for side in ("left", "right"):
        if isinstance(tags.get(f"{prefix}:{side}"), str):
            out[side] = tags[f"{prefix}:{side}"]
    return out


def _parking(tags: dict) -> tuple[set[str], set[str]]:
    """Parking positions and orientations from the new (parking:*) and old (parking:lane:*) scheme."""
    positions: set[str] = set()
    orientations: set[str] = set()
    for side in ("left", "right"):
        new = next((tags[k] for k in (f"parking:{side}", "parking:both") if isinstance(tags.get(k), str)), None)
        if new is not None and new not in ("yes",):
            positions.add("no" if new in _PARK_NO else new)
            o = next((tags[k] for k in (f"parking:{side}:orientation", "parking:both:orientation")
                      if isinstance(tags.get(k), str)), None)
            if o in _ORIENTATIONS:
                orientations.add(o)
            continue
        old_key = next((k for k in (f"parking:lane:{side}", "parking:lane:both") if isinstance(tags.get(k), str)), None)
        if old_key is None:
            continue
        old = tags[old_key]
        if old in _PARK_NO:
            positions.add("no")
        elif old == "separate":
            positions.add("separate")
        else:
            if old in _ORIENTATIONS:
                orientations.add(old)
            pos = next((tags[f"{k}:{old}"] for k in (f"parking:lane:{side}", "parking:lane:both")
                        if isinstance(tags.get(f"{k}:{old}"), str)), "on_street")
            positions.add(_OLD_POSITION.get(pos, "lane"))
    return positions, orientations


def _int_or_none(v) -> int | None:
    return int(v) if isinstance(v, str) and v.strip().isdigit() else None


def way_design(tags: dict) -> dict:
    """Design attributes of one OSM way. Untagged attributes are None ('unknown'), never False."""
    cyc = set(_side_values(tags, "cycleway").values())
    sidepath = tags.get("bicycle") == "use_sidepath"
    if cyc or sidepath:
        track = bool(cyc & _TRACK) or sidepath
        lane = bool(cyc & _LANE)
    else:
        track = lane = None
    markings = tags.get("lane_markings")
    positions, orientations = _parking(tags)
    known = positions - {"separate"}
    return {
        "separated_cycle_track_present": track,
        "cycle_lane_present": lane,
        "lanes": _int_or_none(tags.get("lanes")),
        "centre_line": {"yes": True, "no": False}.get(markings),
        "surface": tags.get("surface") if isinstance(tags.get("surface"), str) else None,
        "parking": "|".join(sorted(positions)) if positions else None,
        "parking_on_carriageway": bool(known & _PARK_ON_CARRIAGEWAY) if known else None,
        "parking_along_carriageway": bool(known & _PARK_ALONG) if known else None,
        "angle_parking": bool(orientations - {"parallel"}) if known - {"no"} else (False if known else None),
        "motorroad": True if tags.get("motorroad") == "yes" else None,
    }


def majority(values: list, weights: list[float]):
    """Value with the largest total weight among known values; None if no value is known."""
    totals: dict = {}
    for v, w in zip(values, weights):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            continue
        totals[v] = totals.get(v, 0.0) + float(w)
    if not totals:
        return None
    return max(totals.items(), key=lambda kv: kv[1])[0]


def parallel_route_present(seg: gpd.GeoSeries, lines: gpd.GeoSeries, params, min_share: float) -> pd.Series:
    """S-FEAT-11: True where at least min_share of the segment lies within params.buffer_m of a cycle route line
    running in the same direction (zone_share of S-CONF-02 with the parallel buffer)."""
    from pipeline.lib.conflate import zone_share

    if lines is None or len(lines) == 0:
        return pd.Series(False, index=seg.index)
    return zone_share(seg, lines, params) >= min_share
