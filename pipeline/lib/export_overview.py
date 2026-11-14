"""District overview, junction search and network gaps for the website (redesign 2026-11, package 2).

Pure functions on the frames of the export (EPSG:25832); coordinates for the website are transformed to EPSG:4326
only here. Display parameters (from which discrepancy level a street counts as "large deviation", list length) come
from config/project.yaml web.overview; no rule thresholds are set here.
"""

import geopandas as gpd
import pandas as pd

EXPORT_CRS = 4326
MAIN_NETWORK = ("RSV", "HAUPT", "BASIS")


def _km(s: pd.Series) -> float:
    return round(float(s.fillna(0).sum()) / 1000, 1)


def _at(geom) -> list[float]:
    p = geom.interpolate(0.5, normalized=True) if geom.geom_type != "Point" else geom
    q = gpd.GeoSeries([p], crs=25832).to_crs(EXPORT_CRS).iloc[0]
    return [round(q.x, 6), round(q.y, 6)]


def district_figures(seg: gpd.GeoDataFrame, fac: pd.DataFrame, jct: pd.DataFrame, params: dict) -> dict:
    """Key figures per Bezirk: km of streets, of large deviation, of too high speed, of main cycle network, of main
    network without a fitting cycle facility, of target cross-section that does not fit; junctions and rebuilds."""
    need = params["need_min_disc"]
    out = {}
    for bz, s in seg.groupby("bezirk"):
        f = fac[fac.bezirk == bz]
        main = f[f.cycle_cat_final.isin(MAIN_NETWORK)]
        j = jct[jct.bezirk == bz]
        out[bz] = {
            "km_total": _km(s.length_m),
            "km_need": _km(s.loc[s.disc_max.fillna(0) >= need, "length_m"]),
            "km_speed_down": _km(s.loc[s.disc_speed.fillna(0) >= 1, "length_m"]),
            "km_cycle_main": _km(main.length_m),
            "km_cycle_missing": _km(main.loc[main.facility_gap == "missing", "length_m"]),
            "km_profile_no_fit": _km(f.loc[f.fit_class == "does_not_fit", "length_m"]),
            "junctions": int(len(j)),
            "junctions_rebuild": int(j.action_needed.fillna(False).astype(bool).sum()),
        }
    return out


def top_streets(seg: gpd.GeoDataFrame, bz: str, params: dict) -> list[dict]:
    """Streets (by name) with the highest priority in the Bezirk; the segment with the highest priority stands for it."""
    s = seg[(seg.bezirk == bz) & seg.name.notna() & (seg.priority.fillna(0) > 0)]
    out = []
    for name, g in s.sort_values("priority", ascending=False, kind="stable").groupby("name", sort=False):
        top = g.iloc[0]
        out.append({"name": name, "id": top.segment_id, "priority": round(float(top.priority), 2),
                    "cat": top.cat_final, "speed_ist": None if pd.isna(top.speed_ist_kmh) else int(top.speed_ist_kmh),
                    "crashes": int(g.crashes_ped_cyc.fillna(0).sum()),
                    "km_need": _km(g.loc[g.disc_max.fillna(0) >= params["need_min_disc"], "length_m"]),
                    "at": _at(top.geometry)})
        if len(out) == params["top_n"]:
            break
    return out


def top_junctions(jct: gpd.GeoDataFrame, bz: str, params: dict) -> list[dict]:
    """Junctions that need a rebuild, in the order of priority_rank (design_rules J-M-07)."""
    j = jct[(jct.bezirk == bz) & jct.action_needed.fillna(False).astype(bool)].sort_values("priority_rank", kind="stable")
    return [{"name": r.names, "id": str(r.node_id), "rank": int(r.priority_rank), "ist": r.junction_type_ist,
             "soll": r.junction_type_final, "crashes": int(r.crashes_cyc or 0), "at": _at(r.geometry)}
            for r in j.head(params["top_n"]).itertuples()]


def top_gaps(fac: gpd.GeoDataFrame, demand: pd.Series, bz: str, params: dict) -> list[dict]:
    """Streets of the main cycle network without a cycle facility, ranked by length x modelled cycle trips."""
    f = fac[(fac.bezirk == bz) & fac.cycle_cat_final.isin(MAIN_NETWORK) & (fac.facility_gap == "missing") & fac.name.notna()].copy()
    if f.empty:
        return []
    f["demand"] = f.segment_id.map(demand).fillna(0.0)
    out = []
    for name, g in f.groupby("name", sort=True):
        top = g.sort_values("demand", ascending=False, kind="stable").iloc[0]
        out.append({"name": name, "id": top.segment_id, "km": _km(g.length_m), "cycle_cat": top.cycle_cat_final,
                    "demand": int(round(float(top.demand))), "score": float((g.length_m * g.demand).sum()),
                    "at": _at(top.geometry)})
    out.sort(key=lambda x: (-x["score"], x["name"]))
    for x in out:
        del x["score"]
    return out[: params["top_n"]]


def junction_search(jct: gpd.GeoDataFrame) -> list[dict]:
    """Search entries for junctions (name, Bezirk, id, point in EPSG:4326)."""
    p = jct.geometry.to_crs(EXPORT_CRS)
    return [{"name": n, "bezirk": b, "id": str(i), "lon": round(g.x, 6), "lat": round(g.y, 6)}
            for n, b, i, g in zip(jct.names, jct.bezirk, jct.node_id, p) if isinstance(n, str) and n]


def mesh_gaps_frame(gaps: gpd.GeoDataFrame, simplify_m: float = 5.0) -> gpd.GeoDataFrame:
    """Meshes of the target cycle network wider than planned, simplified for display (5 m is below a pixel at
    zoom 14), in EPSG:4326."""
    g = gaps[["side_m", "max_m", "level", "bezirk", "geometry"]].copy()
    g["geometry"] = g.geometry.simplify(simplify_m)
    return g.to_crs(EXPORT_CRS)
