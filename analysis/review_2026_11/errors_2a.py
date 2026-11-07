"""Phase 2a: systematic error patterns of the street classification (current state, data/interim).

Checks (each with km, segments, district split and linked examples):
  E1 Bus collector roads as ETW30: tertiary/secondary/primary ETW30 with bus service
  E2 Ist speed above Soll: ETW30 with Ist 40-50/ > 50
  E3 Dual carriageways: parallel segments with the same name, different cat_final
  E4 Short category runs: a run along a street name shorter than N2 min_run_m between two equal neighbours
  E5 Edge effect: conn_score of the same highway class by distance to the Hamburg boundary
  E6 Bridges: segments whose name contains "brücke" or OSM bridge (if tagged), category and width
  E7 Commercial/port areas: GOW30 via frontage in port/industry Stadtteile
  E8 Missing Ist speed / DTV
Usage: python -m analysis.review_2026_11.errors_2a <out_dir>
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml

from analysis.review_2026_11.common import ROOT, seg_links

PORT = ["Waltershof", "Altenwerder", "Steinwerder", "Kleiner Grasbrook", "Billbrook", "Wilhelmsburg", "Moorburg",
        "Hammerbrook", "Rothenburgsort"]


def _walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def km(df, m=None) -> float:
    s = df.length_m if m is None else df.length_m[m]
    return round(float(s.sum()) / 1000, 1)


def examples(df, n=6, sort="length_m") -> list[str]:
    out = []
    for _, r in df.sort_values(sort, ascending=False).drop_duplicates("name").head(n).iterrows():
        out.append(f"{r['name'] or '(ohne Name)'} ({r.bezirk or 'Randbereich'}): {seg_links(r.segment_id, r.geometry)}")
    return out


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rules = yaml.safe_load((ROOT / "config/rules.yaml").read_text(encoding="utf-8"))
    min_run = float(next(x for x in _walk(rules) if x.get("id") == "N2")["min_run_m"])
    d = gpd.read_parquet(ROOT / "data/interim/discrepancy.parquet",
                         columns=["segment_id", "highway", "name", "length_m", "bezirk", "cat_final", "in_hvs",
                                  "speed_ist_kmh", "dtv_official", "conn_score", "bus_trips_weekday", "node_u",
                                  "node_v", "geometry", "width_p10_m", "shop_frontage_share",
                                  "schools_or_kitas_within_m", "rule_path", "osm_way_ids"])
    d = d[d.cat_final.notna()].reset_index(drop=True)
    res, ex = {}, {}
    hvs = d.in_hvs.fillna(False).astype(bool)

    # E1 bus collector roads as ETW30
    main_cls = d.highway.isin(["primary", "secondary", "tertiary"])
    e1 = d[main_cls & (d.cat_final == "ETW30")]
    bus = e1.bus_trips_weekday.fillna(0) > 0
    res["E1"] = {"km_etw30_main_classes": km(e1), "km_with_bus": km(e1, bus),
                 "by_highway_km": (e1.groupby("highway").length_m.sum() / 1000).round(1).to_dict(),
                 "bus_trips_quartiles": e1.bus_trips_weekday[bus].quantile([.25, .5, .75]).round(0).tolist(),
                 "conn_ge_0_5_km": km(e1, e1.conn_score >= 0.5),
                 "ist_ge_50_km": km(e1, e1.speed_ist_kmh >= 50),
                 "by_bezirk_km": (e1[bus].groupby(e1.bezirk.fillna("Randbereich")).length_m.sum() / 1000).round(1).to_dict(),
                 "streets": (e1[bus].groupby("name").length_m.sum() / 1000).sort_values(ascending=False).head(15).round(2).to_dict()}
    ex["E1"] = examples(e1[bus], sort="bus_trips_weekday")
    # all ETW30 with buses (any class)
    etw_bus = d[(d.cat_final == "ETW30") & (d.bus_trips_weekday.fillna(0) > 0)]
    res["E1"]["all_etw30_with_bus_km"] = km(etw_bus)
    res["E1"]["all_etw30_with_bus_ge_100_trips_km"] = km(etw_bus, etw_bus.bus_trips_weekday >= 100)

    # E2 Ist speed above Soll
    etw = d[d.cat_final == "ETW30"]
    res["E2"] = {"etw30_ist_40_50_km": km(etw, etw.speed_ist_kmh.between(31, 50)),
                 "etw30_ist_gt_50_km": km(etw, etw.speed_ist_kmh > 50),
                 "etw30_ist_40_50_by_highway": (etw[etw.speed_ist_kmh.between(31, 50)].groupby("highway").length_m.sum()
                                                / 1000).round(1).to_dict(),
                 "gow50_ist_30_km": km(d, (d.cat_final == "GOW50") & (d.speed_ist_kmh <= 30))}
    ex["E2"] = examples(etw[etw.speed_ist_kmh > 50])

    # E3 dual carriageways: same name, both ends within 40 m of each other's line, different category
    named = d[d.name.notna() & d.highway.isin(["primary", "secondary", "tertiary", "trunk"])].copy()
    sidx = named.sindex
    pairs = []
    for i, r in named.iterrows():
        if r.length_m < 50:
            continue
        cand = named.iloc[sidx.query(r.geometry.buffer(40), predicate="intersects")]
        cand = cand[(cand.name == r["name"]) & (cand.segment_id != r.segment_id) &
                    (cand.cat_final != r.cat_final) & (cand.node_u != r.node_u) & (cand.node_v != r.node_v) &
                    (cand.node_u != r.node_v) & (cand.node_v != r.node_u)]
        for _, c in cand.iterrows():
            # parallel: the other line lies within 40 m along most of its length
            if c.geometry.hausdorff_distance(r.geometry) < 60:
                pairs.append((r.segment_id, c.segment_id, r.cat_final, c.cat_final, r["name"], r.bezirk,
                              min(r.length_m, c.length_m)))
    p = pd.DataFrame(pairs, columns=["a", "b", "cat_a", "cat_b", "name", "bezirk", "len"])
    p["key"] = p.apply(lambda x: tuple(sorted([x.a, x.b])), axis=1)
    p = p.drop_duplicates("key")
    res["E3"] = {"pairs": len(p), "km_min_side": round(p.len.sum() / 1000, 1),
                 "cat_pairs": p.apply(lambda x: "/".join(sorted([x.cat_a, x.cat_b])), axis=1).value_counts().to_dict(),
                 "streets": p.groupby("name").len.sum().sort_values(ascending=False).head(12).round(0).to_dict()}
    g = d.set_index("segment_id").geometry
    ex["E3"] = [f"{r['name']} ({r.bezirk}): {r.cat_a} {seg_links(r.a, g[r.a])} gegenüber {r.cat_b} "
                f"{seg_links(r.b, g[r.b])}" for _, r in p.sort_values("len", ascending=False).head(6).iterrows()]

    # E4 short runs along a street name (graph walk over shared nodes, same name)
    nm = d[d.name.notna()]
    short = []
    by_node = {}
    for i, r in nm.iterrows():
        for n in (r.node_u, r.node_v):
            by_node.setdefault((r["name"], n), []).append(i)
    for i, r in nm.iterrows():
        neigh = set()
        for n in (r.node_u, r.node_v):
            neigh.update(j for j in by_node[(r["name"], n)] if j != i)
        cats = [nm.at[j, "cat_final"] for j in neigh]
        if len(neigh) == 2 and cats[0] == cats[1] and cats[0] != r.cat_final and r.length_m < min_run:
            short.append(i)
    s = nm.loc[short]
    res["E4"] = {"min_run_m": min_run, "segments": len(s), "km": km(s),
                 "by_cat": (s.groupby("cat_final").length_m.sum() / 1000).round(1).to_dict()}
    ex["E4"] = examples(s)

    # E5 edge effect: conn_score by distance to the Hamburg boundary for the same class
    area = gpd.read_parquet(ROOT / "data/raw/work_area.parquet")
    ham = area  # the seven districts (admin_level 9)
    boundary = ham.union_all().boundary
    mid = d.geometry.interpolate(0.5, normalized=True)
    dist = mid.distance(boundary)
    inside = mid.within(ham.union_all())
    dist = np.where(inside, dist, -dist)
    d["dist_boundary_m"] = dist
    bands = pd.cut(d.dist_boundary_m, [-1e9, 0, 1000, 3000, 1e9], labels=["außerhalb", "0–1 km", "1–3 km", "> 3 km"])
    e5 = d[d.highway.isin(["secondary", "tertiary", "residential"])].groupby(["highway", bands], observed=False) \
        .conn_score.median().round(3).unstack()
    res["E5"] = {"median_conn_by_band": e5.to_dict(orient="index"),
                 "km_outside_hamburg_classified": km(d, d.dist_boundary_m < 0),
                 "outside_by_cat": (d[d.dist_boundary_m < 0].groupby("cat_final").length_m.sum() / 1000).round(1).to_dict()}

    # E6 bridges (by name; OSM bridge tag is not carried in the segments)
    br = d[d.name.fillna("").str.contains("brücke", case=False)]
    res["E6"] = {"segments": len(br), "km": km(br), "by_cat": (br.groupby("cat_final").length_m.sum() / 1000).round(1).to_dict(),
                 "width_unknown_km": km(br, br.width_p10_m.isna()),
                 "gow30_by_c_g30_02_km": km(br, (br.cat_final == "GOW30") & br.rule_path.astype(str).str.contains("C-G30-02"))}
    ex["E6"] = examples(br[(br.cat_final == "GOW30") & br.rule_path.astype(str).str.contains("C-G30-02")])

    # E7 port/industry: GOW30 via frontage or school in port Stadtteile (by name of Stadtteil not available ->
    # use rule path and low population as proxy)
    feats = pd.read_parquet(ROOT / "data/interim/features.parquet", columns=["segment_id", "population_100m"])
    d = d.merge(feats, on="segment_id", how="left")
    g30_front = (d.cat_final == "GOW30") & d.rule_path.astype(str).str.contains("C-G30-01") & \
        (d.population_100m.fillna(0) < 50)
    res["E7"] = {"gow30_c_g30_01_with_lt_50_residents_km": km(d, g30_front),
                 "by_bezirk": (d[g30_front].groupby(d.bezirk.fillna("Randbereich")).length_m.sum() / 1000).round(1).to_dict()}
    ex["E7"] = examples(d[g30_front])

    # E8 missing data
    res["E8"] = {"ist_speed_unknown_km": km(d, d.speed_ist_kmh.isna()),
                 "ist_speed_unknown_share_len": round(float(d.length_m[d.speed_ist_kmh.isna()].sum() / d.length_m.sum()), 3),
                 "dtv_known_km": km(d, d.dtv_official.notna()), "total_km": km(d)}

    (out / "errors_2a.json").write_text(json.dumps({"results": res, "examples": ex}, ensure_ascii=False, indent=1,
                                                   default=str))
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1])
