"""Cycle stage 1: directed cycle graph for all of Hamburg (prompts/15_cycle_demand.md, step 1).

Usage: uv run python -m pipeline.c01_cycle_graph

Edges: road segments (data/interim/final.parquet) usable by bike, own cycle and shared paths and
ferries with bicycle transport from the OSM extract (C-GRAPH-01..03). Ist resistance per direction =
length x factor (C-IMP-01..08) + node delays (C-GRAPH-04/05). Writes data/interim/cycle_graph.parquet
and reports/cycle_graph.md. Parameters: config/cycling_rules.yaml.
"""

import datetime as dt
import json
import sys
import time
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from pipeline.lib import cycle_graph as cg
from pipeline.lib.area import NO_DISTRICT, read_districts, sample_by_district
from pipeline.lib.conflate import MatchParams, match_lines
from pipeline.lib.crs import WORK_CRS, to_work_crs
from pipeline.lib.links import load_viewers, orthophoto_link, osm_map_link, osm_way_link, panoramax_link
from pipeline.lib.manifest import REPO_ROOT, load_manifest, sha256_file
from pipeline.lib.rules import load_cycling_rules
from pipeline.s02_network import _pbf_from_manifest, assign_bezirk

FINAL_PATH = REPO_ROOT / "data" / "interim" / "final.parquet"
SIGNALS_PATH = REPO_ROOT / "data" / "raw" / "traffic_signals__osm.parquet"
OUT_PATH = REPO_ROOT / "data" / "interim" / "cycle_graph.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "cycle_graph.md"
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
# Columns pyrosm returns as own columns; everything else is in the JSON column `tags`.
TAG_COLUMNS = ("bicycle", "oneway", "junction", "surface", "cycleway", "cycleway:left", "cycleway:right",
               "cycleway:both", "oneway:bicycle", "bicycle_road", "cyclestreet", "motorroad", "name")
SEGMENT_COLUMNS = ["segment_id", "osm_way_ids", "cat_final", "speed_ist_kmh", "travel_speed_kmh",
                   "fahrradstrasse_official", "bezirk", "geometry"]


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def way_tags(row: dict) -> dict:
    tags = json.loads(row["tags"]) if isinstance(row.get("tags"), str) else {}
    for col in TAG_COLUMNS:
        val = row.get(col)
        if isinstance(val, str):
            tags.setdefault(col, val)
    return tags


def read_osm(pbf) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Node-to-node edges of all highway ways, and ferry ways (EPSG:25832)."""
    from pyrosm import OSM

    osm = OSM(str(pbf))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        _, edges = osm.get_network(network_type="all", nodes=True)
        ferries = osm.get_data_by_custom_criteria(custom_filter={"route": ["ferry"]}, filter_type="keep",
                                                  keep_nodes=False, keep_relations=False)
    edges = edges.rename(columns={"id": "way_id"})
    for c in TAG_COLUMNS:
        if c not in edges.columns:
            edges[c] = None
    ferries = ferries[ferries.geometry.geom_type == "LineString"].rename(columns={"id": "way_id"})
    if "bicycle" not in ferries.columns:
        ferries["bicycle"] = None
    return to_work_crs(edges.reset_index(drop=True)), to_work_crs(ferries.reset_index(drop=True))


def edge_segments(edges: gpd.GeoDataFrame, seg: gpd.GeoDataFrame) -> pd.Series:
    """segment_id per node-to-node edge of a road way: the segment of the same way closest to the edge midpoint."""
    pairs = seg[["segment_id", "osm_way_ids", "geometry"]].explode("osm_way_ids").rename(columns={"osm_way_ids": "way_id"})
    pairs["way_id"] = pairs["way_id"].astype("int64")
    e = pd.DataFrame({"row": np.arange(len(edges)), "way_id": edges["way_id"].astype("int64").to_numpy(),
                      "mid": shapely.line_interpolate_point(edges.geometry.values, 0.5, normalized=True)})
    m = e.merge(pairs, on="way_id", how="inner")
    m["dist"] = shapely.distance(m["mid"].values, gpd.GeoSeries(m["geometry"].values).values)
    best = m.sort_values(["row", "dist", "segment_id"]).drop_duplicates("row").set_index("row")
    return best["segment_id"].reindex(np.arange(len(edges)))


def build(params: cg.GraphParams, pbf, seg: gpd.GeoDataFrame, signal_nodes: set, bezirke: gpd.GeoDataFrame):
    stats: dict = {}
    t0 = time.perf_counter()
    edges, ferries = read_osm(pbf)
    stats["n_osm_edges"] = len(edges)
    seg_ways = set(int(w) for ws in seg["osm_way_ids"] for w in ws)

    # per way: tags, kind, directions (pyrosm repeats the way attributes on every node-to-node edge)
    first = edges.drop_duplicates("way_id").set_index("way_id")
    info = {}
    for wid, row in first.drop(columns="geometry").iterrows():
        tags = way_tags(row.to_dict())
        kind = cg.way_kind(row["highway"], tags, int(wid) in seg_ways, params)
        if kind is not None:
            info[int(wid)] = (tags, kind, *cg.allowed_directions(tags))
    edges = edges[edges["way_id"].astype("int64").isin(info)].reset_index(drop=True)
    edges["kind"] = [info[int(w)][1] for w in edges["way_id"]]
    edges["fwd_ok"] = [info[int(w)][2] for w in edges["way_id"]]
    edges["bwd_ok"] = [info[int(w)][3] for w in edges["way_id"]]

    road = edges["kind"] == "road"
    edges["segment_id"] = None
    edges.loc[road, "segment_id"] = edge_segments(edges[road].reset_index(drop=True), seg).to_numpy()
    lost = road & edges["segment_id"].isna()
    stats["road_edges_without_segment"] = int(lost.sum())
    edges = edges[~lost].reset_index(drop=True)

    s = seg.set_index("segment_id")
    speed = s["speed_ist_kmh"].astype("Float64").fillna(s["travel_speed_kmh"].astype("Float64"))
    imp_cache: dict = {}
    factors, rules_, traces, prio = [], [], [], []
    for wid, sid, hw in zip(edges["way_id"].astype("int64"), edges["segment_id"], edges["highway"]):
        key = (wid, sid)
        if key not in imp_cache:
            tags, kind = info[wid][0], info[wid][1]
            cat = s.at[sid, "cat_final"] if sid is not None else None
            sp = speed.get(sid) if sid is not None else None
            fstr = bool(s.at[sid, "fahrradstrasse_official"]) if sid is not None and pd.notna(s.at[sid, "fahrradstrasse_official"]) else False
            f, rule, trace = cg.impedance(kind, hw, tags, cat, sp, fstr, params)
            imp_cache[key] = (f, rule, json.dumps(trace, ensure_ascii=False), kind == "road" and cg.is_priority(cat, hw, params))
        f, rule, trace, p = imp_cache[key]
        factors.append(f)
        rules_.append(rule)
        traces.append(trace)
        prio.append(p)
    edges["factor"], edges["imp_rule"], edges["impedance_trace"], edges["priority"] = factors, rules_, traces, prio
    edges["delay_v"], edges["delay_u"] = cg.node_delays(edges["u"].to_numpy(), edges["v"].to_numpy(),
                                                        edges["priority"].to_numpy(), signal_nodes, params)
    edges["name"] = edges["name"].where(edges["name"].notna(), None)
    stats["t_read_s"] = time.perf_counter() - t0

    t1 = time.perf_counter()
    cyc = cg.merge_edges(edges[["u", "v", "way_id", "name", "highway", "kind", "imp_rule", "factor", "fwd_ok", "bwd_ok",
                                "segment_id", "delay_v", "delay_u", "impedance_trace", "priority", "geometry"]],
                         carry=("impedance_trace", "priority"))
    cyc["n_signals"] = _signals_on(cyc, edges, signal_nodes)
    stats["t_merge_s"] = time.perf_counter() - t1

    # ferries: snap to the end nodes of the cycle edges
    ends = pd.concat([pd.DataFrame({"node": cyc["node_u"], "geometry": shapely.get_point(cyc.geometry.values, 0)}),
                      pd.DataFrame({"node": cyc["node_v"], "geometry": shapely.get_point(cyc.geometry.values, -1)})])
    nodes = gpd.GeoDataFrame(ends.drop_duplicates("node"), geometry="geometry", crs=WORK_CRS)
    stats["n_ferry_ways"] = len(ferries)
    stats["ferry_bicycle_values"] = ferries["bicycle"].fillna("–").value_counts().to_dict()
    fer = cg.ferry_edges(ferries, nodes, params)
    fer["impedance_trace"] = cg.ferry_trace(params)
    fer["priority"] = False
    fer["segment_id"] = None
    fer["name"] = None
    fer["n_signals"] = 0
    stats["n_ferry_edges"] = len(fer)
    cyc = pd.concat([cyc, fer], ignore_index=True)
    cyc = gpd.GeoDataFrame(cyc, geometry="geometry", crs=WORK_CRS)
    if not cyc["edge_id"].is_unique:
        raise RuntimeError(f"duplicate edge_id: {cyc.loc[cyc['edge_id'].duplicated(), 'edge_id'].head().tolist()}")

    # C-GRAPH-06: own paths along a road segment
    paths = cyc.index[cyc["kind"] == "path"]
    mp = MatchParams(params.sidepath_buffer_m, params.sidepath_max_angle_deg, params.sidepath_min_overlap)
    m = match_lines(cyc.geometry.loc[paths].reset_index(drop=True), seg.geometry.reset_index(drop=True), mp)
    best = m["best_off_idx"].where(m["quality"] == "exact")
    cyc["sidepath_of"] = None
    cyc.loc[paths, "sidepath_of"] = [seg["segment_id"].iloc[int(i)] if pd.notna(i) else None for i in best]

    # Bezirk: from the segment, otherwise by length share
    cyc["bezirk"] = cyc["segment_id"].map(s["bezirk"])
    missing = cyc["bezirk"].isna()
    cyc.loc[missing, "bezirk"] = assign_bezirk(cyc.loc[missing], bezirke).to_numpy()

    # largest strongly connected component of the directed graph
    a = cg.arcs(cyc)
    node_ids, inv = np.unique(np.concatenate([a["tail"].to_numpy(), a["head"].to_numpy()]), return_inverse=True)
    n = len(node_ids)
    mat = coo_matrix((np.ones(len(a)), (inv[: len(a)], inv[len(a):])), shape=(n, n)).tocsr()
    _, labels = connected_components(mat, directed=True, connection="strong")
    main = np.bincount(labels).argmax()
    in_main = set(node_ids[labels == main].tolist())
    cyc["in_main_component"] = cyc["node_u"].isin(in_main) & cyc["node_v"].isin(in_main)
    stats["n_nodes"] = n
    cyc["length_m"] = cyc.geometry.length
    return cyc, stats


def _signals_on(cyc: gpd.GeoDataFrame, edges: gpd.GeoDataFrame, signal_nodes: set) -> list[int]:
    """Number of signal nodes on each cycle edge (ends and interior), for the report and later prompts."""
    nodes_per_way: dict[int, set] = {}
    for w, u, v in zip(edges["way_id"].astype("int64"), edges["u"], edges["v"]):
        if u in signal_nodes or v in signal_nodes:
            nodes_per_way.setdefault(int(w), set()).update(x for x in (u, v) if x in signal_nodes)
    out = []
    for ways, geom in zip(cyc["osm_way_ids"], cyc.geometry):
        cand = set().union(*(nodes_per_way.get(int(w), set()) for w in ways)) if len(ways) else set()
        out.append(len(cand))
    return out


def _fmt(v: float, digits: int = 0) -> str:
    return f"{v:,.{digits}f}".replace(",", " ")


def write_report(cyc: gpd.GeoDataFrame, stats: dict, params: cg.GraphParams, meta: dict) -> None:
    km = cyc["length_m"].sum() / 1000
    lines = [
        "# Radgraph (Stufe c01)",
        "",
        f"Erzeugt {_now()} mit pipeline/c01_cycle_graph.py · cycling_rules.yaml {meta['version']} · "
        f"OSM-Auszug `{meta['pbf']}` (SHA-256 {meta['pbf_sha'][:12]}…) · nicht amtlicher Entwurf",
        "",
        "## Kennzahlen",
        "",
        f"- Kanten: {_fmt(len(cyc))} ({_fmt(km, 1)} km), Knoten: {_fmt(stats['n_nodes'])}",
        f"- OSM-Knotenkanten gelesen: {_fmt(stats['n_osm_edges'])}; Straßenkanten ohne Abschnitt verworfen: "
        f"{stats['road_edges_without_segment']}",
        f"- Fähren: {stats['n_ferry_ways']} OSM-Linien, davon {stats['n_ferry_edges']} als Kante "
        f"(bicycle-Werte: {', '.join(f'{k} {v}' for k, v in sorted(stats['ferry_bicycle_values'].items()))}); "
        f"Wartezeit {params.ferry_wait_s:.0f} s, Anbindung ≤ {params.ferry_snap_m:.0f} m (C-GRAPH-03)",
        f"- Größte stark zusammenhängende Komponente: {_fmt(cyc.loc[cyc['in_main_component'], 'length_m'].sum() / 1000, 1)} km "
        f"({cyc.loc[cyc['in_main_component'], 'length_m'].sum() / cyc['length_m'].sum():.1%} der Länge)",
        f"- Nur in einer Richtung befahrbar: {_fmt((cyc['cost_fwd'].isna() ^ cyc['cost_bwd'].isna()).sum())} Kanten; "
        f"in keiner Richtung (widersprüchliche oneway-Angaben der OSM-Wege einer Kante): "
        f"{_fmt((cyc['cost_fwd'].isna() & cyc['cost_bwd'].isna()).sum())} Kanten, "
        f"{_fmt(cyc.loc[cyc['cost_fwd'].isna() & cyc['cost_bwd'].isna(), 'length_m'].sum())} m",
        f"- Eigenständige Wege mit Bezug zu einem Straßenabschnitt (sidepath_of, C-GRAPH-06): "
        f"{_fmt(cyc['sidepath_of'].notna().sum())} von {_fmt((cyc['kind'] == 'path').sum())}",
        f"- Laufzeit: Lesen und Widerstand {stats['t_read_s']:.0f} s, Zusammenfassen {stats['t_merge_s']:.0f} s",
        "",
        "## Länge nach Kantenart und Widerstandsregel",
        "",
        "| Art | Regel | Faktor (Mittel) | km | Anteil |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    g = cyc.groupby(["kind", "imp_rule"], dropna=False)
    for (kind, rule), grp in g:
        k = grp["length_m"].sum() / 1000
        f = (grp["factor"] * grp["length_m"]).sum() / grp["length_m"].sum()
        lines.append(f"| {kind} | {rule} | {f:.2f} | {_fmt(k, 1)} | {k / km:.1%} |")
    lines += ["", "Regeln: config/cycling_rules.yaml (`routing_impedance.ist_mapping`, `cycle_graph`). "
              "Alle Werte sind Annahmen (status draft).", "",
              "## Länge je Bezirk", "", "| Bezirk | km | davon eigenständige Wege |", "| --- | ---: | ---: |"]
    for bez, grp in cyc.groupby(cyc["bezirk"].fillna(NO_DISTRICT)):
        lines.append(f"| {bez} | {_fmt(grp['length_m'].sum() / 1000, 1)} | "
                     f"{_fmt(grp.loc[grp['kind'] == 'path', 'length_m'].sum() / 1000, 1)} |")
    viewers = load_viewers()
    sample = sample_by_district(cyc[cyc["kind"] != "ferry"], SAMPLE_SIZE, SAMPLE_SEED, id_col="edge_id")
    lines += ["", f"## {len(sample)} Zufallsstichproben (Seed {SAMPLE_SEED})", "",
              "| edge_id | Bezirk | Name | Art | Regel | Faktor | Richtungen | Prüfen |", "| --- | --- | --- | --- | --- | ---: | --- | --- |"]
    mids = gpd.GeoSeries(sample.geometry.interpolate(0.5, normalized=True), crs=WORK_CRS)
    mids_wgs = mids.to_crs("EPSG:4326")
    for (_, r), p, pw in zip(sample.iterrows(), mids, mids_wgs):
        dirs = "beide" if pd.notna(r["cost_fwd"]) and pd.notna(r["cost_bwd"]) else "eine"
        way = osm_way_link(r["osm_way_ids"][0])
        lines.append(f"| `{r['edge_id']}` | {r['bezirk'] or '–'} | {r['name'] if isinstance(r['name'], str) and r['name'] else '–'} | {r['kind']} | {r['imp_rule']} | "
                     f"{r['factor']:.2f} | {dirs} | [Luftbild]({orthophoto_link(p, viewers)}) · "
                     f"[Panoramax]({panoramax_link(pw, viewers)}) · [OSM]({osm_map_link(pw)}) · [Way]({way}) |")
    lines += ["", "Quellen: © OpenStreetMap-Beitragende (ODbL); abgeleitete Daten unter ODbL (docs/licenses.md). "
              "Straßenkategorien und Tempo aus data/interim/final.parquet.", ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    cyc_rules = load_cycling_rules()
    params = cg.GraphParams.from_rules(cyc_rules)
    manifest = load_manifest()
    pbf = _pbf_from_manifest(manifest)
    pbf_path = REPO_ROOT / pbf["path"]
    pbf_sha = sha256_file(pbf_path)
    if pbf.get("sha256") and pbf_sha != pbf["sha256"]:
        print(f"cycle-graph: SHA-256 of {pbf['path']} does not match data/manifest.json", file=sys.stderr)
        return 1
    if not FINAL_PATH.exists():
        print("cycle-graph: data/interim/final.parquet missing; run the road pipeline first", file=sys.stderr)
        return 1
    seg = gpd.read_parquet(FINAL_PATH, columns=SEGMENT_COLUMNS)
    signals = gpd.read_parquet(SIGNALS_PATH)
    signal_nodes = set(signals.loc[signals["osm_type"] == "node", "id"].astype("int64").tolist())
    bezirke = read_districts()
    print(f"cycle-graph: reading {pbf['path']}")
    cyc, stats = build(params, pbf_path, seg, signal_nodes, bezirke)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out = cyc.copy()
    out["osm_way_ids"] = out["osm_way_ids"].map(lambda ws: [int(w) for w in ws])
    out.to_parquet(OUT_PATH, index=False)
    write_report(cyc, stats, params, {"version": cyc_rules.meta.version, "pbf": pbf["path"], "pbf_sha": pbf_sha})
    print(f"cycle-graph: {len(cyc)} edges, {cyc['length_m'].sum() / 1000:.0f} km -> {OUT_PATH.relative_to(REPO_ROOT)}, "
          f"report {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
