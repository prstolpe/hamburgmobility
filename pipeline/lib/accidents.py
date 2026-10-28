"""Unfallatlas: read the yearly CSV ZIPs and aggregate crashes per segment (rule P-RISK-01).

Column names and codes come from the `points` spec in config/sources.yaml (dataset description
DSB_Unfallatlas.pdf). Single crashes are only held in memory; callers store the aggregates only.
"""

import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from pipeline.lib.crs import WORK_CRS

AGG_COLUMNS = ["crashes_ped_cyc", "crashes_ped", "crashes_cyc", "crashes_severe_fatal", "crash_weighted"]


def _member(z: zipfile.ZipFile, suffixes: list[str]) -> str:
    names = [n for n in z.namelist() if n.lower().endswith(tuple(s.lower() for s in suffixes))]
    if len(names) != 1:
        raise ValueError(f"expected exactly one data member with suffix {suffixes}, found {names}")
    return names[0]


def read_accidents_zip(path: str | Path, spec: dict) -> gpd.GeoDataFrame:
    """Crashes of the state spec['land'] as points in the working CRS.

    Columns: year (int), severe_or_fatal, pedestrian, cyclist (bool). Raises ValueError if a column is missing.
    """
    cols = [spec["land_column"], spec["year"], spec["category"], spec["pedestrian"], spec["cyclist"],
            spec["x"], spec["y"]]
    with zipfile.ZipFile(path) as z:
        member = _member(z, spec["member_suffixes"])
        with z.open(member) as f:
            df = pd.read_csv(f, sep=spec["separator"], dtype=str, encoding=spec["encoding"])
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{Path(path).name}/{member}: columns missing {missing}")
    df = df.loc[df[spec["land_column"]].str.strip() == spec["land"], cols]

    def number(s: pd.Series) -> np.ndarray:
        return s.str.replace(spec["decimal"], ".", regex=False).astype("float64").to_numpy()

    flag = spec["flag_true"]
    out = gpd.GeoDataFrame(
        {"year": df[spec["year"]].astype(int).to_numpy(),
         "severe_or_fatal": df[spec["category"]].str.strip().isin(spec["severe_or_fatal"]).to_numpy(),
         "pedestrian": (df[spec["pedestrian"]].str.strip() == flag).to_numpy(),
         "cyclist": (df[spec["cyclist"]].str.strip() == flag).to_numpy()},
        geometry=gpd.points_from_xy(number(df[spec["x"]]), number(df[spec["y"]])), crs=spec["crs"])
    return out.to_crs(WORK_CRS)


def coverage(crashes: pd.DataFrame, years: list[int]) -> dict[int, int]:
    """Number of crash records per expected year (0 = the year has no coverage)."""
    counts = crashes["year"].value_counts()
    return {int(y): int(counts.get(y, 0)) for y in years}


def _ped_cyc(crashes: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    return crashes[crashes["pedestrian"].astype(bool) | crashes["cyclist"].astype(bool)]


def _nearest(seg: gpd.GeoSeries, points: gpd.GeoSeries, snap_m: float) -> tuple[np.ndarray, np.ndarray]:
    """(point positions, segment positions) of each point's nearest segment within snap_m."""
    if points.empty or seg.empty:
        return np.array([], dtype=int), np.array([], dtype=int)
    tree = shapely.STRtree(seg.to_numpy())
    i_pt, i_seg = tree.query_nearest(points.to_numpy(), max_distance=snap_m, all_matches=False)
    return i_pt, i_seg


def aggregate_crashes(seg: gpd.GeoSeries, crashes: gpd.GeoDataFrame, snap_m: float,
                      severe_weight: float) -> pd.DataFrame:
    """Counts per segment (index of seg) of crashes with pedestrian or cyclist involvement.

    Each crash goes to its nearest segment at most snap_m away; severe or fatal crashes count
    severe_weight times in crash_weighted. Returns plain numbers only (no crash ids, no geometries).
    """
    pc = _ped_cyc(crashes)
    i_pt, i_seg = _nearest(seg, pc.geometry, snap_m)
    n = len(seg)
    sub = pc.iloc[i_pt]

    def count(mask) -> np.ndarray:
        return np.bincount(i_seg, weights=np.asarray(mask, dtype="float64"), minlength=n)

    severe = sub["severe_or_fatal"].to_numpy(dtype=bool)
    out = pd.DataFrame({
        "crashes_ped_cyc": np.bincount(i_seg, minlength=n),
        "crashes_ped": count(sub["pedestrian"].to_numpy(dtype=bool)),
        "crashes_cyc": count(sub["cyclist"].to_numpy(dtype=bool)),
        "crashes_severe_fatal": count(severe),
        "crash_weighted": count(np.where(severe, severe_weight, 1.0)),
    }, index=seg.index)
    for c in ("crashes_ped_cyc", "crashes_ped", "crashes_cyc", "crashes_severe_fatal"):
        out[c] = out[c].astype("int64")
    return out[AGG_COLUMNS]


def assignment_stats(seg: gpd.GeoSeries, crashes: gpd.GeoDataFrame, snap_m: float) -> dict[str, int]:
    """How many pedestrian/cyclist crashes were assigned to a segment and how many were not."""
    pc = _ped_cyc(crashes)
    i_pt, _ = _nearest(seg, pc.geometry, snap_m)
    return {"ped_cyc": len(pc), "assigned": len(i_pt), "unassigned": len(pc) - len(i_pt)}
