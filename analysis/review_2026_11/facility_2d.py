"""Phase 2d: cycle facility type, width and placement (data/interim, cycling_rules 0.7.0, design_rules 0.6.0).

F1 Soll/final/Ist facility on the cycle network (RSV/HAUPT/BASIS), gaps
F2 continuity along routes: facility changes per km (Soll) above C-PRI-12 max_changes_per_km
F3 two-way paths: Ist separated_twoway vs. Soll (S-03 not implemented)
F4 bus stops along Soll separated tracks (PL-05 not checkable in the profile): GTFS stops within STOP_M
F5 one-way streets on the cycle network (PL-06 contraflow not checked)
F6 bridges on the cycle network
F7 official cycle network (Bestand/Planung) vs. Soll RSV/HAUPT
F8 width data: Ist width known
Usage: python -m analysis.review_2026_11.facility_2d <out_dir>
"""

import json
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import yaml

from analysis.review_2026_11.common import ROOT, seg_links

NET = ["RSV", "HAUPT", "BASIS"]
STOP_M = 25  # assumption: a stop "lies on" a segment within this distance (review only, no rule)


def km(df, m=None):
    s = df.length_m if m is None else df.length_m[m]
    return round(float(s.sum()) / 1000, 1)


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cyc = yaml.safe_load((ROOT / "config/cycling_rules.yaml").read_text(encoding="utf-8"))
    max_changes = next(x for x in cyc["principles"]["cohesion"]["checks"] if x["id"] == "P-COH-04") \
        if False else 1.0
    for x in _walk(cyc):
        if x.get("id") == "C-PRI-12":
            max_changes = float(x["max_changes_per_km"])
    f = gpd.read_parquet(ROOT / "data/interim/cycle_facility.parquet")
    x = pd.read_parquet(ROOT / "data/interim/cross_section_soll.parquet",
                        columns=["segment_id", "cycle_side", "oneway", "cycle_facility_final", "fit_class",
                                 "bus_peak_h_dir"])
    s = f.merge(x, on="segment_id")
    net = s.cycle_cat_final.isin(NET)
    res = {}
    res["F1"] = {k: (s[net].groupby(c).length_m.sum() / 1000).round(1).to_dict() for k, c in
                 (("soll", "cycle_facility_soll"), ("final", "cycle_facility_final"), ("ist", "cycle_facility_ist"))}
    res["F1"]["gap"] = (s[net].groupby(s.facility_gap.fillna("null")).length_m.sum() / 1000).round(1).to_dict()
    res["F1"]["net_km"] = km(s, net)
    downgraded = net & (s.cycle_facility_soll != s.cycle_facility_final)
    res["F1"]["soll_to_final_changed_km"] = (s[downgraded].groupby(["cycle_facility_soll", "cycle_facility_final"])
                                             .length_m.sum() / 1000).round(1).rename(lambda k: k).to_dict()
    res["F1"]["soll_to_final_changed_km"] = {f"{a}->{b}": v for (a, b), v in res["F1"]["soll_to_final_changed_km"].items()}

    p = pd.read_parquet(ROOT / "data/interim/cycle_principles.parquet",
                        columns=["level", "route_id", "category", "length_m", "changes_soll_per_km",
                                 "changes_ist_per_km"])
    p = p[(p.level == "route") & p.category.isin(NET)]
    res["F2"] = {"max_changes_per_km": max_changes, "routes": len(p),
                 "soll_over": int((p.changes_soll_per_km > max_changes).sum()),
                 "ist_over": int((p.changes_ist_per_km > max_changes).sum()),
                 "soll_over_km": km(p, p.changes_soll_per_km > max_changes),
                 "soll_over_by_cat": p[p.changes_soll_per_km > max_changes].category.value_counts().to_dict()}

    twoway_ist = net & (s.cycle_facility_ist == "separated_twoway")
    res["F3"] = {"ist_twoway_km": km(s, twoway_ist),
                 "soll_twoway_km": km(s, net & (s.cycle_facility_soll == "separated_twoway")),
                 "ist_twoway_gap": (s[twoway_ist].groupby(s.facility_gap.fillna("null")).length_m.sum() / 1000).round(1).to_dict(),
                 "cycle_side_values": s.cycle_side.value_counts(dropna=False).to_dict()}

    feed = next((ROOT / "data/raw/gtfs_hvv").glob("*.ZIP"))
    with zipfile.ZipFile(feed) as z, z.open("stops.txt") as fh:
        stops = pd.read_csv(fh, usecols=["stop_id", "stop_lat", "stop_lon"])
    st = gpd.GeoDataFrame(stops, geometry=gpd.points_from_xy(stops.stop_lon, stops.stop_lat), crs=4326).to_crs(25832)
    sep = s[net & s.cycle_facility_final.astype(str).str.startswith("separated") &
            (s.bus_peak_h_dir.fillna(0) > 0)].copy()
    hits = gpd.sjoin(st, gpd.GeoDataFrame(sep[["segment_id", "geometry"]], crs=25832).assign(
        geometry=lambda g: g.buffer(STOP_M)), predicate="within")
    res["F4"] = {"separated_on_bus_routes_km": km(sep), "stop_points_on_them": int(hits.stop_id.nunique()),
                 "segments_with_stop": int(hits.segment_id.nunique()), "stop_m": STOP_M,
                 "note": "PL-05 (Haltestelleninsel) ist im Profil nicht prüfbar (Flag pl02_unchecked)"}

    ow = net & s.oneway.fillna(False).astype(bool)
    res["F5"] = {"oneway_on_net_km": km(s, ow), "oneway_etw30_km": km(s, ow & (s.cat_final == "ETW30")),
                 "oneway_etw30_by_facility": (s[ow & (s.cat_final == "ETW30")].groupby("cycle_facility_final")
                                              .length_m.sum() / 1000).round(1).to_dict()}

    br = net & s.name.fillna("").str.contains("brücke", case=False)
    res["F6"] = {"km": km(s, br), "fit": (s[br].groupby(s.fit_class.fillna("null")).length_m.sum() / 1000).round(1).to_dict(),
                 "width_unknown_km": km(s, br & s.width_median_m.isna())}

    cn = pd.read_parquet(ROOT / "data/interim/cycle_network.parquet",
                         columns=["edge_id", "length_m", "official_share", "official_network", "cycle_cat_final"])
    off = cn.official_share.fillna(0) >= 0.5
    top = cn.cycle_cat_final.isin(["RSV", "HAUPT"])
    res["F7"] = {"official_km_in_graph": km(cn, off), "official_and_soll_top_km": km(cn, off & top),
                 "official_not_in_soll_network_km": km(cn, off & ~cn.cycle_cat_final.isin(NET)),
                 "soll_top_km": km(cn, top), "soll_top_not_official_km": km(cn, top & ~off),
                 "official_by_soll_cat": (cn[off].groupby(cn.cycle_cat_final.fillna("none")).length_m.sum() / 1000).round(1).to_dict()}

    res["F8"] = {"ist_width_known_km": km(s, net & s.cycle_width_ist_m.notna()), "net_km": km(s, net)}
    ex = s[twoway_ist].sort_values("length_m", ascending=False).drop_duplicates("name").head(5)
    res["examples_twoway"] = [f"{r['name']} ({r.bezirk}): {seg_links(r.segment_id, r.geometry)}" for _, r in ex.iterrows()]
    ex = s[ow & (s.cat_final == "ETW30")].sort_values("length_m", ascending=False).drop_duplicates("name").head(5)
    res["examples_oneway"] = [f"{r['name']} ({r.bezirk}): {seg_links(r.segment_id, r.geometry)}" for _, r in ex.iterrows()]
    (out / "facility_2d.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("examples")}, ensure_ascii=False, indent=1, default=str))


def _walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


if __name__ == "__main__":
    main(sys.argv[1])
