"""Cycle stage 4: five principles per route, edge and network, Ist and Soll (prompts/17_cycle_principles.md).

Usage: uv run python -m pipeline.c04_principles

Checks P-COH-*, P-DIR-*, P-SAF-*, P-COM-*, P-ATT-* (config/cycling_rules.yaml `principles`) scored after
C-PRI-01..16 (`principle_scoring`). score_ist = today's state of the Soll route, score_soll = after rule-conform
build-out (facility after separation_matrix, target width, closed surface, lit); delta = need for action.
Writes data/interim/cycle_principles.parquet (rows per edge_id of the Soll network and per route_id),
reports/cycle_principles.md with one map per principle and reports/cycle_principles_review.csv.
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
import yaml
from scipy.sparse.csgraph import connected_components

from pipeline.lib import cycle_network as cn
from pipeline.lib import principles as pr
from pipeline.lib.accidents import aggregate_crashes
from pipeline.lib.area import NO_DISTRICT, read_districts, sample_by_district
from pipeline.lib.crs import WORK_CRS, to_work_crs
from pipeline.lib.cycle_demand import DemandParams
from pipeline.lib import gtfs
from pipeline.lib.links import load_viewers, orthophoto_link, osm_map_link, panoramax_link
from pipeline.lib.manifest import REPO_ROOT, load_manifest
from pipeline.lib.rules import load_cycling_rules, load_rules
from pipeline.s02_network import _pbf_from_manifest

RAW = REPO_ROOT / "data" / "raw"
INTERIM = REPO_ROOT / "data" / "interim"
NETWORK_PATH = INTERIM / "cycle_network.parquet"
ROUTES_PATH = INTERIM / "cycle_routes.parquet"
GAPS_PATH = INTERIM / "cycle_mesh_gaps.parquet"
FINAL_PATH = INTERIM / "final.parquet"
ALKIS_PATH = RAW / "alkis__Nutzung.parquet"
SIGNALS_PATH = RAW / "traffic_signals__osm.parquet"
SCHOOLS_PATH = RAW / "schools__osm.parquet"
UNIVERSITIES_PATH = RAW / "universities__osm.parquet"
SOURCES_PATH = REPO_ROOT / "config" / "sources.yaml"
OUT_PATH = INTERIM / "cycle_principles.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "cycle_principles.md"
REVIEW_PATH = REPO_ROOT / "reports" / "cycle_principles_review.csv"
MAP_DIR = REPO_ROOT / "reports"
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
NETWORK_LEVELS = ("RSV", "HAUPT", "BASIS")
PRINCIPLE_DE = {"cohesion": "Zusammenhang", "directness": "Direktheit", "safety": "Sicherheit", "comfort": "Komfort",
                "attractiveness": "Attraktivität"}
FACILITY_DE = {"separated_oneway_both": "Radweg je Seite", "separated_twoway": "Zweirichtungsradweg", "cycle_lane": "Radfahrstreifen",
               "cycle_street": "Fahrradstraße", "mixed": "Mischverkehr", "own_path": "eigener Weg", None: "unbekannt", "unknown": "unbekannt"}
# OSM keys read per way (C-PRI-06/08/09)
WAY_KEYS = ("lit", "width", "est_width", "surface", "cycleway:width", "cycleway:both:width", "cycleway:right:width",
            "cycleway:left:width", "cycleway:surface", "cycleway:both:surface", "cycleway:right:surface", "cycleway:left:surface")
EDGE_CHECKS = ("P-SAF-01", "P-SAF-03", "P-SAF-04", "P-COM-01", "P-COM-02", "P-ATT-01", "P-ATT-03", "P-COH-01")
ROUTE_ONLY_CHECKS = ("P-COH-02", "P-COH-04", "P-DIR-01", "P-DIR-02", "P-DIR-03")


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _fmt(v: float, digits: int = 0) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "–"
    return f"{v:,.{digits}f}".replace(",", " ")


def _pct(v: float) -> str:
    return "–" if v is None or not np.isfinite(v) else f"{100 * v:.0f} %"


def _col(check: str, view: str) -> str:
    return check.lower().replace("-", "_") + "_" + view


# --- inputs -----------------------------------------------------------------------------------------------


def _gtfs_path(manifest: dict):
    files = (manifest["sources"].get("gtfs_hvv") or {}).get("files") or []
    paths = [REPO_ROOT / f["path"] for f in files if (REPO_ROOT / f["path"]).exists()]
    if not paths:
        raise FileNotFoundError("GTFS feed missing; run `make fetch`")
    return paths[0]


def read_way_tags(pbf, way_ids: set) -> dict[int, dict]:
    """The WAY_KEYS of every needed OSM way (own columns of pyrosm or the JSON column tags)."""
    from pyrosm import OSM

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        edges = OSM(str(pbf)).get_network(network_type="all", nodes=False)
    edges = edges.drop_duplicates("id")
    edges = edges[edges["id"].astype("int64").isin(way_ids)]
    out = {}
    cols = [k for k in WAY_KEYS if k in edges.columns]
    for row in edges[["id", "tags", *cols]].to_dict("records"):
        tags = json.loads(row["tags"]) if isinstance(row.get("tags"), str) else {}
        out[int(row["id"])] = {k: (row[k] if isinstance(row.get(k), str) else tags.get(k)) for k in WAY_KEYS}
    return out


def read_trees(pbf) -> np.ndarray:
    """OSM natural=tree (points) and natural=tree_row (lines), EPSG:25832 (C-PRI-10)."""
    from pyrosm import OSM

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        g = OSM(str(pbf)).get_data_by_custom_criteria(custom_filter={"natural": ["tree", "tree_row"]}, osm_keys_to_keep=["natural"],
                                                       filter_type="keep", keep_nodes=True, keep_ways=True, keep_relations=False)
    if g is None or g.empty:
        return np.array([], dtype=object)
    g = to_work_crs(g)
    g = g[g["natural"].isin(["tree", "tree_row"]) & g.geom_type.isin(["Point", "LineString", "MultiLineString"])]
    return g.geometry.values


def read_green(p: pr.PrincipleParams, area) -> np.ndarray:
    alk = to_work_crs(gpd.read_parquet(ALKIS_PATH, columns=["nutzart", "geometry"]))
    alk = alk[alk["nutzart"].isin(p.green_nutzart)]
    polys = alk.geometry.values
    return polys[shapely.intersects(polys, area)]


def load_crashes(manifest: dict) -> tuple[gpd.GeoDataFrame, list[int]]:
    from pipeline.s08_discrepancy import ACCIDENT_SOURCE
    from pipeline.s08_discrepancy import load_crashes as _load

    with open(SOURCES_PATH, encoding="utf-8") as f:
        src = yaml.safe_load(f)["sources"][ACCIDENT_SOURCE]
    crashes, cov = _load(manifest, src)
    return crashes, [y for y, n in cov.items() if n > 0]


# --- per edge -----------------------------------------------------------------------------------------------


def _first(values: list):
    return next((v for v in values if isinstance(v, str) and v), None)


def edge_osm_values(way_lists, tags: dict, keys: tuple) -> list:
    """First known value of the keys (in order) over the ways of each edge."""
    out = []
    for ways in way_lists:
        tv = [tags.get(int(w), {}) for w in (ways if ways is not None else [])]
        out.append(_first([t.get(k) for k in keys for t in tv]))
    return out


def edge_lit(way_lists, tags: dict, p: pr.PrincipleParams) -> list:
    """Lit state per edge: False if a way is unlit, True if a way is lit, else None."""
    out = []
    for ways in way_lists:
        states = [pr.lit_state(tags.get(int(w), {}).get("lit"), p) for w in (ways if ways is not None else [])]
        out.append(False if False in states else (True if True in states else None))
    return out


def edge_width(way_lists, tags: dict, keys: tuple) -> np.ndarray:
    """Smallest known width over the ways of an edge, from the first key that has a value."""
    out = np.full(len(way_lists), np.nan)
    for i, ways in enumerate(way_lists):
        vals = []
        for w in (ways if ways is not None else []):
            t = tags.get(int(w), {})
            for k in keys:
                v = pr.parse_width(t.get(k))
                if np.isfinite(v):
                    vals.append(v)
                    break
        if vals:
            out[i] = min(vals)
    return out


def _trace_cycleway(trace: str):
    try:
        return json.loads(trace)["inputs"].get("cycleway")
    except (TypeError, ValueError, KeyError):
        return None


def edge_frame(net: gpd.GeoDataFrame, final: pd.DataFrame, tags: dict, p: pr.PrincipleParams) -> pd.DataFrame:
    """Facility, width, surface, lit, DTV per edge (Ist and Soll inputs), sidepaths folded into their road."""
    n = len(net)
    kind = net["kind"].to_numpy()
    ways = net["osm_way_ids"].tolist()
    side = net["sidepath_of"]
    is_side = side.notna().to_numpy() & (kind == "path")
    oneway = (net["cost_fwd"].isna() | net["cost_bwd"].isna()).to_numpy()
    cyc_cat = net["cycle_cat_final"].to_numpy()
    cat_final = net["segment_id"].map(final["cat_final"]).to_numpy(dtype=object)
    parent_cat = side.map(final["cat_final"]).to_numpy(dtype=object)
    cycleway = [_trace_cycleway(t) for t in net["impedance_trace"]]
    fac = [pr.ist_facility(k, r, c, bool(o) if s else None, p)
           for k, r, c, o, s in zip(kind, net["imp_rule"], cycleway, oneway, is_side)]

    lit = edge_lit(ways, tags, p)
    surf_own = edge_osm_values(ways, tags, ("surface",))
    surf_cw = edge_osm_values(ways, tags, ("cycleway:surface", "cycleway:both:surface", "cycleway:right:surface", "cycleway:left:surface"))
    w_path = edge_width(ways, tags, ("width", "est_width"))
    w_cw = edge_width(ways, tags, ("cycleway:width", "cycleway:both:width", "cycleway:right:width", "cycleway:left:width"))
    w_road = edge_width(ways, tags, ("width",))
    width = np.full(n, np.nan)
    surface = list(surf_own)
    for i in range(n):
        f = fac[i]
        if kind[i] == "path":
            width[i] = w_path[i]
        elif f in ("cycle_lane", "separated_oneway_both"):
            width[i] = w_cw[i]
            surface[i] = surf_cw[i] or surf_own[i]
        elif f == "cycle_street":
            width[i] = w_road[i]

    # C-PRI-02: a road edge with a sidepath takes the sidepath's facility, width, surface and lit
    sp = pd.DataFrame({"seg": side.to_numpy(), "fac": fac, "oneway": oneway, "width": width, "surface": surface,
                       "lit": lit, "on": is_side})
    sp = sp[sp["on"]]
    by_seg = {}
    for seg, g in sp.groupby("seg"):
        twoway = (~g["oneway"]).any()
        lits = [x for x in g["lit"] if x is not None]
        by_seg[seg] = {"fac": p.sidepath_twoway if twoway else p.sidepath_oneway, "width": np.nanmin(g["width"]) if g["width"].notna().any() else np.nan,
                       "surface": _first(g["surface"].tolist()), "lit": (False if False in lits else (True if lits else None))}
    from_side = np.zeros(n, dtype=bool)
    segs = net["segment_id"].to_numpy(dtype=object)
    for i in range(n):
        if kind[i] == "road" and segs[i] in by_seg:
            b = by_seg[segs[i]]
            fac[i], width[i], surface[i] = b["fac"], b["width"], b["surface"] or surface[i]
            lit[i] = b["lit"] if b["lit"] is not None else lit[i]
            from_side[i] = True

    soll = [pr.edge_soll_facility(k, c, pc if s else None, cc, p)
            for k, c, pc, s, cc in zip(kind, cat_final, parent_cat, is_side, cyc_cat)]
    seg_dtv = net["segment_id"].map(final["dtv_official"])
    side_dtv = side.map(final["dtv_official"])
    dtv = seg_dtv.fillna(side_dtv).to_numpy(dtype="float64")
    peak_dir = np.fmax(net["cyc_peak_h_fwd"].to_numpy(dtype="float64"), net["cyc_peak_h_bwd"].to_numpy(dtype="float64"))
    return pd.DataFrame({
        "kind": kind, "is_sidepath": is_side, "from_sidepath": from_side, "cat_final": cat_final, "parent_cat": parent_cat,
        "cycle_cat": cyc_cat, "facility_ist": fac, "facility_soll": [s[0] for s in soll], "facility_fallback": [s[1] for s in soll],
        "width_m": width, "surface": surface, "lit": lit, "dtv": dtv, "peak_dir": peak_dir,
        "peak_both": net["cyc_peak_h"].to_numpy(dtype="float64")}, index=net.index)


def edge_checks(ef: pd.DataFrame, length: np.ndarray, crashes_cyc: np.ndarray, green: np.ndarray, gap_share: np.ndarray,
                net_mask: np.ndarray, p: pr.PrincipleParams) -> tuple[dict, dict, dict, pd.DataFrame]:
    """Per edge and view: check scores, data availability (0/1) and applicability for the edge checks.
    Crash percentiles (P-SAF-04) are ranked among the edges in net_mask only."""
    n = len(ef)
    sc = {"ist": {}, "soll": {}}
    known, appl = {}, {}
    fi, fs, ff, cc = ef["facility_ist"].tolist(), ef["facility_soll"].tolist(), ef["facility_fallback"].tolist(), ef["cycle_cat"].tolist()

    s01 = np.array([pr.facility_score(a, b, c, p) for a, b, c in zip(fi, fs, ff)])
    sc["ist"]["P-SAF-01"] = s01
    sc["soll"]["P-SAF-01"] = np.where(pd.notna(pd.Series(fs)).to_numpy(), 1.0, np.nan)
    appl["P-SAF-01"] = pd.notna(pd.Series(fs)).to_numpy()
    known["P-SAF-01"] = ~np.isnan(s01)

    lit = ef["lit"].tolist()
    s03 = np.array([np.nan if x is None else float(x) for x in lit])
    sc["ist"]["P-SAF-03"] = s03
    sc["soll"]["P-SAF-03"] = np.ones(n) if p.soll_lit else s03
    appl["P-SAF-03"] = np.ones(n, dtype=bool)
    known["P-SAF-03"] = ~np.isnan(s03)

    rate = crashes_cyc / np.maximum(length, p.crash_min_length_m) * 1000
    s04 = np.full(n, np.nan)
    s04[net_mask] = pr.percentile_inverse(rate[net_mask])
    sc["ist"]["P-SAF-04"] = s04
    sc["soll"]["P-SAF-04"] = s04
    appl["P-SAF-04"] = np.ones(n, dtype=bool)
    known["P-SAF-04"] = np.ones(n, dtype=bool)

    req_ist = np.array([pr.required_width(f, c, a, b, p) for f, c, a, b in zip(fi, cc, ef["peak_dir"], ef["peak_both"])])
    req_soll = np.array([pr.required_width(f, c, a, b, p) for f, c, a, b in zip(fs, cc, ef["peak_dir"], ef["peak_both"])])
    width = ef["width_m"].to_numpy(dtype="float64")
    s_w = pr.score_array("ratio", width, req_ist)
    sc["ist"]["P-COM-01"] = np.where(np.isfinite(req_ist), s_w, np.nan)
    sc["soll"]["P-COM-01"] = np.where(np.isfinite(req_soll), 1.0, np.nan)
    appl["P-COM-01"] = np.isfinite(req_ist)
    known["P-COM-01"] = np.isfinite(req_ist) & np.isfinite(width)

    s_s = np.array([pr.surface_score(s, c, p) for s, c in zip(ef["surface"], cc)])
    sc["ist"]["P-COM-02"] = s_s
    sc["soll"]["P-COM-02"] = np.ones(n)
    appl["P-COM-02"] = np.ones(n, dtype=bool)
    known["P-COM-02"] = ~np.isnan(s_s)

    s_g = pr.score_array("ratio", green, p.green_target)
    sc["ist"]["P-ATT-01"] = s_g
    sc["soll"]["P-ATT-01"] = s_g
    appl["P-ATT-01"] = np.ones(n, dtype=bool)
    known["P-ATT-01"] = np.ones(n, dtype=bool)

    high = np.nan_to_num(ef["dtv"].to_numpy(dtype="float64"), nan=0.0) > p.patt_dtv
    s_a = np.where(high, 0.0, 1.0)
    sc["ist"]["P-ATT-03"] = s_a
    sc["soll"]["P-ATT-03"] = s_a
    appl["P-ATT-03"] = np.ones(n, dtype=bool)
    known["P-ATT-03"] = np.ones(n, dtype=bool)

    s_c = 1.0 - gap_share
    sc["ist"]["P-COH-01"] = s_c
    sc["soll"]["P-COH-01"] = s_c
    appl["P-COH-01"] = np.ones(n, dtype=bool)
    known["P-COH-01"] = np.ones(n, dtype=bool)
    vals = pd.DataFrame({"width_required_m": req_ist, "width_required_soll_m": req_soll, "crashes_cyc_5y": crashes_cyc,
                         "crashes_cyc_per_km_5y": rate, "green_share": green, "high_dtv": high, "mesh_gap_share": gap_share},
                        index=ef.index)
    return sc, known, appl, vals


def gap_edge_share(geoms: np.ndarray, rank: np.ndarray, gaps: gpd.GeoDataFrame, p: pr.PrincipleParams) -> np.ndarray:
    """P-COH-01 per edge: length share on the rim of an oversized mesh of the edge's level or a lower level."""
    share = np.zeros(len(geoms))
    for lvl in ("HAUPT", "BASIS"):
        g = gaps[gaps["level"] == lvl]
        if g.empty:
            continue
        rims = shapely.buffer(shapely.boundary(g.geometry.values), p.gap_edge_buffer_m)
        sel = rank >= cn.RANK[lvl]
        share[sel] = np.maximum(share[sel], cn.overlap_share(geoms[sel], rims))
    return share


# --- per route ------------------------------------------------------------------------------------------------


def route_values(routes: gpd.GeoDataFrame, net: gpd.GeoDataFrame, ef: pd.DataFrame, pos_of: dict, signal_nodes: set,
                 edge_prio: np.ndarray, prio_nodes: set, interior: np.ndarray, g_len: pr.Graph, comp_ok: dict,
                 p: pr.PrincipleParams) -> pd.DataFrame:
    """Route-only check values: detour, stops, time loss, components, changes (C-PRI-04/05/12)."""
    node_u = net["node_u"].to_numpy(dtype="int64")
    node_v = net["node_v"].to_numpy(dtype="int64")
    length = net["length_m"].to_numpy(dtype="float64")
    fac_ist = ef["facility_ist"].to_numpy(dtype=object)
    fac_soll = ef["facility_soll"].to_numpy(dtype=object)
    rows = []
    starts, ends, lims, idx = [], [], [], []
    for i, r in enumerate(routes.itertuples(index=False)):
        e = [pos_of[x] for x in json.loads(r.edge_ids)]
        nodes = cn.route_nodes(e, node_u, node_v)
        chain = bool(cn.chain_ok(e, node_u, node_v, nodes).all())
        km = length[e].sum() / 1000
        sig, gw = pr.route_stops(nodes, edge_prio[e].tolist(), interior[e].tolist(), signal_nodes, prio_nodes) if chain else (np.nan, np.nan)
        comp = comp_ok[r.category]
        rows.append({
            "chain": chain, "km": km, "signals": sig, "give_way": gw,
            "stops_per_km": (sig + gw) / km if chain and km > 0 else np.nan,
            "time_loss_s_per_km": float(pr.time_loss_s(sig, gw, p)) / km if chain and km > 0 else np.nan,
            "in_main_component": bool(np.isin(node_u[e], comp).all()),
            "changes_ist_per_km": pr.facility_changes(list(fac_ist[e])) / km if km > 0 else np.nan,
            "changes_soll_per_km": (pr.facility_changes(list(fac_soll[e])) + int(r.n_category_changes)) / km if km > 0 else np.nan,
            "edges": e})
        if chain:
            starts.append(nodes[0])
            ends.append(nodes[-1])
            lims.append(length[e].sum())
            idx.append(i)
    detour = np.full(len(routes), np.nan)
    order = np.argsort(starts, kind="stable")
    starts, ends, lims, idx = (np.asarray(x)[order] for x in (starts, ends, lims, idx))
    for s in np.unique(starts):
        m = starts == s
        d = pr.shortest_lengths(g_len, [s], ends[m], limit=float(lims[m].max()) * 1.0001)[0]
        detour[idx[m]] = np.where(np.isfinite(d) & (d > 0), lims[m] / d, np.nan)
    out = pd.DataFrame(rows)
    out["detour"] = detour
    return out


def aggregate_routes(routes: gpd.GeoDataFrame, rv: pd.DataFrame, length: np.ndarray, sc: dict, known: dict, appl: dict,
                     crashes_cyc: np.ndarray, p: pr.PrincipleParams) -> tuple[dict, dict, dict]:
    """Route check scores per view, data shares and applicability (edge checks length-weighted)."""
    nr = len(routes)
    rsc = {"ist": {c: np.full(nr, np.nan) for c in p.check_principle}, "soll": {c: np.full(nr, np.nan) for c in p.check_principle}}
    rknown = {c: np.zeros(nr) for c in p.check_principle}
    rappl = {c: np.zeros(nr, dtype=bool) for c in p.check_principle}
    cats = routes["category"].to_numpy()
    rate = np.zeros(nr)
    for i, e in enumerate(rv["edges"]):
        e = np.asarray(e, dtype="int64")
        w = length[e]
        for c in EDGE_CHECKS:
            if c == "P-SAF-04":
                continue
            a = appl[c][e]
            if not a.any():
                continue
            rappl[c][i] = True
            for view in ("ist", "soll"):
                rsc[view][c][i], kn = pr.weighted_mean(np.where(a, sc[view][c][e], np.nan), np.where(a, w, 0.0))
                if view == "ist":
                    rknown[c][i] = kn if np.isfinite(rsc[view][c][i]) else 0.0
        rate[i] = crashes_cyc[e].sum() / max(w.sum(), p.crash_min_length_m) * 1000
    s04 = pr.percentile_inverse(rate)
    for view in ("ist", "soll"):
        rsc[view]["P-SAF-04"] = s04
    rappl["P-SAF-04"][:] = True
    rknown["P-SAF-04"][:] = 1.0

    # route-only checks
    det_thr = np.array([p.detour_max.get(c, np.nan) for c in cats])
    stop_thr = np.array([p.stops_max.get(c, np.nan) for c in cats])
    loss_thr = np.array([p.time_loss_max.get(c, np.nan) for c in cats])
    for c, vals, thr in (("P-DIR-01", rv["detour"], det_thr), ("P-DIR-02", rv["stops_per_km"], stop_thr),
                         ("P-DIR-03", rv["time_loss_s_per_km"], loss_thr)):
        s = pr.score_array(p.forms[c], vals, thr)
        rappl[c] = np.isfinite(thr)
        for view in ("ist", "soll"):
            rsc[view][c] = np.where(rappl[c], s, np.nan)
        rknown[c] = (rappl[c] & np.isfinite(vals.to_numpy(dtype="float64"))).astype(float)
    comp = rv["in_main_component"].to_numpy(dtype=float)
    for view in ("ist", "soll"):
        rsc[view]["P-COH-02"] = comp
    rappl["P-COH-02"][:] = True
    rknown["P-COH-02"][:] = 1.0
    rsc["ist"]["P-COH-04"] = pr.score_array(p.forms["P-COH-04"], rv["changes_ist_per_km"], p.max_changes_per_km)
    rsc["soll"]["P-COH-04"] = pr.score_array(p.forms["P-COH-04"], rv["changes_soll_per_km"], p.max_changes_per_km)
    rappl["P-COH-04"][:] = True
    rknown["P-COH-04"] = np.isfinite(rsc["ist"]["P-COH-04"]).astype(float)
    for c in p.unavailable:
        rappl[c][:] = True
        rknown[c][:] = 0.0
    rsc["rate"] = rate
    return rsc, rknown, rappl


def scores_and_confidence(sc_view: dict, known: dict, appl: dict, p: pr.PrincipleParams) -> tuple[dict, np.ndarray, np.ndarray]:
    ps = pr.principle_scores(sc_view, p)
    total = pr.total_score(ps, p.weights)
    conf = pr.confidence(known, appl, p)
    return ps, total, conf


def trace_rows(sc: dict, known: dict, extra: list[dict], checks: list[str]) -> list[str]:
    """rule_trace_principles per row: check id, Ist/Soll score, data share and input values."""
    out = []
    for i, ex in enumerate(extra):
        steps = []
        for c in checks:
            a, b = sc["ist"][c][i], sc["soll"][c][i]
            if not (np.isfinite(a) or np.isfinite(b)) and known[c][i] == 0:
                steps.append({"rule": c, "result": None})
                continue
            steps.append({"rule": c, "result": {"ist": None if not np.isfinite(a) else round(float(a), 3),
                                                "soll": None if not np.isfinite(b) else round(float(b), 3)},
                          "values": ex.get(c)})
        out.append(json.dumps(steps, ensure_ascii=False, default=lambda x: None if x is None else (float(x) if np.isscalar(x) else str(x))))
    return out


# --- network -------------------------------------------------------------------------------------------------


def components(node_u, node_v, length, mask) -> tuple[int, float, np.ndarray]:
    """Number of components of the masked edges, length share of the largest one and its node ids."""
    pos = np.flatnonzero(mask)
    if len(pos) == 0:
        return 0, float("nan"), np.array([], dtype="int64")
    g = cn.Graph(node_u[pos], node_v[pos], np.ones(len(pos)), pos)
    n, lab = connected_components(g.matrix, directed=False)
    node_lab = lab[g.index(node_u[pos])]
    km = pd.Series(length[pos]).groupby(node_lab).sum()
    big = int(km.idxmax())
    return int(n), float(km.max() / km.sum()), g.nodes[lab == big]


def od_detours(net, rank, main, p: pr.PrincipleParams, g_all) -> dict:
    """P-DIR-01 network sample per category (C-PRI-04)."""
    node_u = net["node_u"].to_numpy(dtype="int64")
    node_v = net["node_v"].to_numpy(dtype="int64")
    length = net["length_m"].to_numpy(dtype="float64")
    geoms = net.geometry.values
    ids = np.concatenate([node_u, node_v])
    pts = np.concatenate([shapely.get_coordinates(shapely.get_point(geoms, 0)), shapely.get_coordinates(shapely.get_point(geoms, -1))])
    node_ids, first = np.unique(ids, return_index=True)
    xy_all = pd.DataFrame(pts[first], index=node_ids)
    out = {}
    for lvl in NETWORK_LEVELS:
        if lvl not in p.detour_max:
            continue
        sel = main & (rank >= cn.RANK[lvl])
        g_lvl = pr.length_graph(node_u[sel], node_v[sel], length[sel])
        n_c, _, big = components(node_u, node_v, length, sel)
        xy = xy_all.loc[big].to_numpy()
        pairs = pr.od_sample(xy, big, p.trip_band_m[lvl], p.od_pairs, p.od_seed)
        det, unreach = [], 0
        for a, b in pairs:
            d_net = pr.shortest_lengths(g_lvl, [a], [b])[0, 0]
            d_all = pr.shortest_lengths(g_all, [a], [b])[0, 0]
            if not (np.isfinite(d_net) and np.isfinite(d_all)) or d_all <= 0:
                unreach += 1
                continue
            det.append(d_net / d_all)
        det = np.array(det)
        out[lvl] = {"n": len(pairs), "unreachable": unreach, "median": float(np.median(det)) if len(det) else np.nan,
                    "p90": float(np.quantile(det, 0.9)) if len(det) else np.nan,
                    "share_ok": float((det <= p.detour_max[lvl]).mean()) if len(det) else np.nan,
                    "threshold": p.detour_max[lvl], "band_km": tuple(x / 1000 for x in p.trip_band_m[lvl]),
                    "score": float(np.mean(pr.score_array("excess", det, p.detour_max[lvl]))) if len(det) else np.nan}
    return out


# --- figures ---------------------------------------------------------------------------------------------------


def _segs(geoms) -> list:
    return [np.asarray(c)[:, :2] for g in geoms for c in ([g.coords] if g.geom_type == "LineString" else [x.coords for x in g.geoms])]


def _seg_values(geoms, values) -> np.ndarray:
    return np.concatenate([np.full(1 if g.geom_type == "LineString" else len(g.geoms), v) for g, v in zip(geoms, values)]) if len(geoms) else np.array([])


def map_principle(path, geoms, ist, soll, districts, title: str, cmap="RdYlGn", vmin=0.0, vmax=1.0, labels=("Ist", "Soll")) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection

    panels = [(labels[0], ist)] + ([(labels[1], soll)] if soll is not None else [])
    fig, axes = plt.subplots(1, len(panels), figsize=(9 * len(panels), 8.5), dpi=100, squeeze=False)
    for ax, (lab, vals) in zip(axes[0], panels):
        districts.boundary.plot(ax=ax, color="#bbb", lw=0.6)
        known = np.isfinite(vals)
        if (~known).any():
            ax.add_collection(LineCollection(_segs(geoms[~known]), colors="#cccccc", linewidths=0.5))
        lc = LineCollection(_segs(geoms[known]), array=_seg_values(geoms[known], vals[known]), cmap=cmap, linewidths=0.9)
        lc.set_clim(vmin, vmax)
        ax.add_collection(lc)
        ax.set_aspect("equal")
        ax.autoscale()
        ax.set_axis_off()
        ax.set_title(lab)
    fig.colorbar(lc, ax=axes[0].tolist(), shrink=0.6, label="Score (grau = unbekannt)")
    fig.suptitle(title)
    fig.savefig(path)
    plt.close(fig)


# --- report ------------------------------------------------------------------------------------------------------


def _links(geom, viewers) -> str:
    p_ = geom.interpolate(0.5, normalized=True) if geom.geom_type != "Point" else geom
    pw = gpd.GeoSeries([p_], crs=WORK_CRS).to_crs("EPSG:4326").iloc[0]
    return f"[Luftbild]({orthophoto_link(p_, viewers)}) · [Panoramax]({panoramax_link(pw, viewers)}) · [OSM]({osm_map_link(pw)})"


def _wmean(v, w) -> float:
    return pr.weighted_mean(v, w)[0]


def write_report(ctx: dict) -> None:
    p, viewers = ctx["p"], load_viewers()
    E, R = ctx["edges"], ctx["routes"]
    w = E["length_m"].to_numpy()
    lines = [
        "# Fünf Prinzipien: Bewertung des Soll-Radnetzes (Stufe c04)",
        "",
        f"Erzeugt {_now()} mit pipeline/c04_principles.py · cycling_rules.yaml {ctx['version']} · nicht amtlicher Entwurf. "
        "Alle Bewertungsregeln (C-PRI-01…16) und die Gewichte sind Annahmen (source_type assumption, status draft) und vor "
        "fachlicher Nutzung zu prüfen.",
        "",
        "**score_ist** bewertet den heutigen Zustand der Soll-Route, **score_soll** den Zustand nach regelkonformem Ausbau "
        "(Führung nach Trennungsmatrix, Sollbreite, geschlossene Decke, Beleuchtung). Die Differenz ist der Handlungsbedarf. "
        "Fehlende Daten senken die confidence, nicht den Score.",
        "",
        "## Kurzfassung",
        "",
    ]
    for lvl in NETWORK_LEVELS:
        m = (E["category"] == lvl).to_numpy()
        lines.append(f"- {lvl}: {_fmt(w[m].sum() / 1000)} km, Score Ist {_fmt(_wmean(E['score_ist'][m], w[m]), 2)} → "
                     f"Soll {_fmt(_wmean(E['score_soll'][m], w[m]), 2)}")
    ok = (E["p_saf_01_ist"] == 1).to_numpy()
    known_fac = E["p_saf_01_ist"].notna().to_numpy()
    lines += [
        f"- Führung entspricht heute der Trennungsmatrix auf {_pct(w[ok].sum() / w[known_fac].sum())} der Netzlänge mit bekannter "
        f"Führung (RSV/HAUPT: {_pct(w[ok & (E['category'].isin(['RSV', 'HAUPT'])).to_numpy()].sum() / w[known_fac & (E['category'].isin(['RSV', 'HAUPT'])).to_numpy()].sum())}).",
        f"- {len(R)} Routen bewertet; mittlerer Handlungsbedarf (score_soll − score_ist) {_fmt(R['delta'].mean(), 2)}, "
        f"confidence: {', '.join(f'{k} {v}' for k, v in R['confidence'].value_counts().reindex(['high', 'medium', 'low']).fillna(0).astype(int).items())}.",
        f"- Nicht bewertbar mangels Daten: {', '.join(f'{c} ({t})' for c, t in p.unavailable.items())}.",
        "",
        "## Datenlage je Prüfung",
        "",
        "Anteil der Länge des Soll-Netzes (RSV, HAUPT, BASIS) mit Wert, unter den Kanten, für die die Prüfung anwendbar ist.",
        "",
        "| Prüfung | Prinzip | Datengrundlage | anwendbar (km) | mit Wert |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for c, (src, km, share) in ctx["availability"].items():
        lines.append(f"| {c} | {PRINCIPLE_DE[p.check_principle[c]]} | {src} | {_fmt(km)} | {_pct(share)} |")
    lines += ["", "## Netzkennzahlen je Kategorie", "",
              "Längengewichtete Mittel über die Kanten der Kategorie (Kantenwerte für Direktheit und Zusammenhang aus der Hauptroute der Kante).", "",
              "| Kategorie | km | " + " | ".join(f"{PRINCIPLE_DE[k]} Ist / Soll" for k in p.weights) + " | Gesamt Ist / Soll |",
              "| --- | ---: | " + " | ".join("---:" for _ in p.weights) + " | ---: |"]
    for lvl in NETWORK_LEVELS:
        m = (E["category"] == lvl).to_numpy()
        cells = [f"{_fmt(_wmean(E[k + '_ist'][m], w[m]), 2)} / {_fmt(_wmean(E[k + '_soll'][m], w[m]), 2)}" for k in p.weights]
        lines.append(f"| {lvl} | {_fmt(w[m].sum() / 1000)} | " + " | ".join(cells) +
                     f" | {_fmt(_wmean(E['score_ist'][m], w[m]), 2)} / {_fmt(_wmean(E['score_soll'][m], w[m]), 2)} |")

    # cohesion
    lines += ["", "## Zusammenhang (P-COH)", "", "**P-COH-01 Maschenweite** (aus c03, cycle_mesh_gaps.parquet):", "",
              "| Ebene | Höchstweite | zu große Maschen | Seite Median | Seite max |", "| --- | ---: | ---: | ---: | ---: |"]
    for lvl, s in ctx["gaps"].items():
        lines.append(f"| {lvl} | {_fmt(s['max_m'])} m | {s['n']} | {_fmt(s['median'])} m | {_fmt(s['max'])} m |")
    lines += ["", "**P-COH-02 Komponenten** (je Ebene mit höheren Ebenen):", "", "| Ebene | Komponenten | Anteil größte Komponente (Länge) |",
              "| --- | ---: | ---: |"]
    for lvl, (nc, share) in ctx["components"].items():
        lines.append(f"| {lvl} | {nc} | {_pct(share)} |")
    lines += ["", f"**P-COH-03 Abdeckung** (Ziele höchstens {_fmt(ctx['coverage_m'])} m vom RSV/HAUPT-Netz; Zentren fehlen, kein Datensatz):", "",
              "| Ziele | Anzahl | abgedeckt |", "| --- | ---: | ---: |"]
    for name, (n_, share) in ctx["coverage"].items():
        lines.append(f"| {name} | {_fmt(n_)} | {_pct(share)} |")
    lines += ["", f"**P-COH-04 Kontinuität:** Wechsel der Ist-Führung je km (Median über Routen) {_fmt(R['changes_ist_per_km'].median(), 2)}, "
              f"Soll (Führung und Kategorie) {_fmt(R['changes_soll_per_km'].median(), 2)}; Schwelle {_fmt(p.max_changes_per_km, 1)} je km (C-PRI-12)."]

    # directness
    lines += ["", "## Direktheit (P-DIR)", "",
              f"**P-DIR-01 Umwegfaktor, Netzstichprobe** (C-PRI-04): je Kategorie {p.od_pairs} OD-Paare, Seed {p.od_seed}, "
              "Knoten der größten Komponente der Ebene (mit höheren Ebenen), Luftlinie im Band trip_length_km. "
              "Netzweg auf der Ebene gegen kürzesten Weg auf allen befahrbaren Kanten (Länge).", "",
              "| Kategorie | Band (km) | Paare | ohne Weg | Median | 90-%-Wert | Schwelle | Anteil ≤ Schwelle |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for lvl, s in ctx["od"].items():
        lines.append(f"| {lvl} | {s['band_km'][0]:g}–{s['band_km'][1]:g} | {s['n']} | {s['unreachable']} | {_fmt(s['median'], 2)} | "
                     f"{_fmt(s['p90'], 2)} | {s['threshold']:g} | {_pct(s['share_ok'])} |")
    lines += ["", "**Je Route** (Median über Routen der Kategorie; Halte nach C-PRI-05, Soll = Ist bis Prompt 20):", "",
              "| Kategorie | Routen | Umwegfaktor | Halte/km | Schwelle Halte | Zeitverlust s/km | Schwelle s/km |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for lvl in NETWORK_LEVELS:
        m = R["category"] == lvl
        lines.append(f"| {lvl} | {int(m.sum())} | {_fmt(R.loc[m, 'detour'].median(), 2)} | {_fmt(R.loc[m, 'stops_per_km'].median(), 1)} | "
                     f"{_fmt(p.stops_max.get(lvl, np.nan), 1)} | {_fmt(R.loc[m, 'time_loss_s_per_km'].median(), 0)} | {_fmt(p.time_loss_max.get(lvl, np.nan), 0)} |")

    # safety
    lines += ["", "## Sicherheit (P-SAF)", "", "**P-SAF-01 Ist-Führung gegen Soll-Führung** (km, Kanten RSV/HAUPT/BASIS):", ""]
    ct = ctx["facility_table"]
    lines += ["| Ist \\ Soll | " + " | ".join(FACILITY_DE.get(c, str(c)) for c in ct.columns) + " |",
              "| --- | " + " | ".join("---:" for _ in ct.columns) + " |"]
    for idx, row in ct.iterrows():
        lines.append(f"| {FACILITY_DE.get(idx, str(idx))} | " + " | ".join(_fmt(v) for v in row) + " |")
    lines += ["", f"P-SAF-03 Beleuchtung: OSM lit auf {_pct(ctx['availability']['P-SAF-03'][2])} der Netzlänge bekannt; davon beleuchtet "
              f"{_pct(ctx['lit_share'])}. P-SAF-04 Unfälle mit Radbeteiligung {ctx['crash_years']}: {_fmt(ctx['crashes_total'])} Unfälle "
              f"an Kanten des Soll-Netzes (je Kante höchstens {p.crash_snap_m:g} m entfernt; nur Summen gespeichert)."]

    # comfort, attractiveness
    lines += ["", "## Komfort und Attraktivität (P-COM, P-ATT)", "",
              f"- P-COM-01 Breite: anwendbar auf {_fmt(ctx['availability']['P-COM-01'][1])} km (ohne Mischverkehr), Breite in OSM auf "
              f"{_pct(ctx['availability']['P-COM-01'][2])} davon; von diesen erreichen {_pct(ctx['width_ok'])} die Sollbreite.",
              f"- P-COM-02 Belag: bekannt auf {_pct(ctx['availability']['P-COM-02'][2])}; RSV/HAUPT mit geschlossener Decke {_pct(ctx['smooth_share'])}.",
              f"- P-ATT-01 Grünanteil im {p.green_buffer_m:g}-m-Puffer: Median {_pct(np.nanmedian(E['green_share']))} (Ziel {_pct(p.green_target)}, ALKIS-Grünflächen und OSM-Bäume).",
              f"- P-ATT-03: {_fmt(ctx['high_dtv_km'])} km des Soll-Netzes liegen an Straßen mit DTV > {_fmt(p.patt_dtv)}.",
              ""]

    # top 30
    lines += [f"## Top {p.top_n} Routen mit dem größten Handlungsbedarf", "",
              "Rangfolge nach Handlungsbedarf-km = (score_soll − score_ist) × Länge in km (C-PRI-14), damit lange Routen mit mittlerem Defizit vor "
              "sehr kurzen Verdichtungsstücken stehen. S/K: Sicherheit und Komfort Ist → Soll.", "",
              "| # | Route | Kategorie | km | Ist | Soll | Δ | Δ × km | S | K | confidence | Prüfen |",
              "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |"]
    top = R.sort_values("need_km", ascending=False).head(p.top_n)
    for k, r in enumerate(top.itertuples(index=False), 1):
        lines.append(f"| {k} | {r.label} (`{r.id}`) | {r.category} | {_fmt(r.length_m / 1000, 1)} | {_fmt(r.score_ist, 2)} | {_fmt(r.score_soll, 2)} | "
                     f"{_fmt(r.delta, 2)} | {_fmt(r.need_km, 2)} | {_fmt(r.safety_ist, 2)} → {_fmt(r.safety_soll, 2)} | "
                     f"{_fmt(r.comfort_ist, 2)} → {_fmt(r.comfort_soll, 2)} | {r.confidence} | {_links(r.geometry, viewers)} |")
    lines += ["", f"Höchster Δ einer Route (ohne Längengewicht): {_fmt(R['delta'].max(), 2)}; Routen mit Δ ≥ 0,2: {int((R['delta'] >= 0.2).sum())}."]

    # maps
    lines += ["", "## Karten je Prinzip", ""]
    for name, path in ctx["maps"].items():
        lines += [f"![{name}]({path.name})", ""]

    # sensitivity
    sens = ctx["sensitivity"]
    lines += ["## Gewichts-Sensitivität (±20 %)", "",
              f"Jedes Gewicht einzeln um ±{p.sens_delta:.0%} verändert, die übrigen anteilig umgelegt (C-PRI-14). Verglichen mit den Basisgewichten: "
              f"Überschneidung der Top {p.top_n} nach Handlungsbedarf-km, Rangkorrelation (Spearman) aller Routen.", "",
              "| Gewicht | Basis | Variante | Top-Überschneidung | Spearman |", "| --- | ---: | ---: | ---: | ---: |"]
    for row in sens:
        lines.append(f"| {PRINCIPLE_DE[row['principle']]} | {row['base']:.3f} | {row['value']:.3f} | {row['overlap']}/{p.top_n} | {row['spearman']:.3f} |")
    lines += ["", f"Kleinste Überschneidung: {min(r['overlap'] for r in sens)}/{p.top_n}.", ""]

    # districts
    lines += ["## Handlungsbedarf je Bezirk", "", "| Bezirk | Netz-km | Score Ist | Score Soll | Δ |", "| --- | ---: | ---: | ---: | ---: |"]
    bez = E["bezirk"].fillna(NO_DISTRICT)
    for b in sorted(bez.unique(), key=lambda x: (x == NO_DISTRICT, x)):
        m = (bez == b).to_numpy()
        si, ss = _wmean(E["score_ist"][m], w[m]), _wmean(E["score_soll"][m], w[m])
        lines.append(f"| {b} | {_fmt(w[m].sum() / 1000)} | {_fmt(si, 2)} | {_fmt(ss, 2)} | {_fmt(ss - si, 2)} |")

    # samples
    lines += ["", f"## Stichprobe: {SAMPLE_SIZE} zufällige Kanten (Seed {SAMPLE_SEED}, nach Bezirk verteilt)", "",
              "| Kante | Name | Kategorie | Führung Ist → Soll | Breite / Soll | Belag | lit | Score Ist / Soll | Prüfen |",
              "| --- | --- | --- | --- | ---: | --- | --- | --- | --- |"]
    for r in ctx["sample"].itertuples(index=False):
        lit = {True: "ja", False: "nein"}.get(r.lit, "–")
        lines.append(f"| `{r.id}` | {r.label} | {r.category} | {FACILITY_DE.get(r.facility_ist, r.facility_ist)} → {FACILITY_DE.get(r.facility_soll, r.facility_soll)} | "
                     f"{_fmt(r.width_m, 2)} / {_fmt(r.width_required_m, 2)} | {r.surface or '–'} | {lit} | {_fmt(r.score_ist, 2)} / {_fmt(r.score_soll, 2)} | "
                     f"{_links(r.geometry, viewers)} |")
    lines += ["", "## Durchsicht mit Ortskundigen", "",
              f"{len(ctx['review'])} Routen (nach Kategorie geschichtet, Seed {p.review_seed}, C-PRI-15) in "
              f"`{REVIEW_PATH.relative_to(REPO_ROOT)}` mit Links und leeren Spalten für Einschätzung und Kommentar.", "",
              "## Hinweise", "",
              "- Soll-Führung je Kante vorläufig direkt aus der Trennungsmatrix (bevorzugte Führung); Prompt 18 legt Führung und Breite je Abschnitt fest, "
              "danach P-SAF-01/P-COM-01 (Soll) mit dessen Ergebnis rechnen.",
              "- Halte und Zeitverlust (P-DIR-02/03) im Soll wie im Ist, bis Prompt 20 Soll-Knotentypen liefert; P-SAF-02 bis dahin unbekannt.",
              "- Unfälle (P-SAF-04) bleiben im Soll unverändert (keine Wirkungsprognose).",
              "- Nachfrage und Netz beruhen auf dem mäßig kalibrierten Modell aus Prompt 15 (reports/cycle_demand.md).",
              "",
              "Quellen: OpenStreetMap-Beitragende (ODbL); ALKIS © Freie und Hansestadt Hamburg, LGV (dl-de/by-2.0); "
              "Unfallatlas © Statistische Ämter des Bundes und der Länder (dl-de/by-2.0); HVV-GTFS © Hamburger Verkehrsverbund GmbH (dl-de/by-2.0).",
              ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# --- main ---------------------------------------------------------------------------------------------------------


def main() -> int:
    cyc_rules = load_cycling_rules()
    p = pr.PrincipleParams.from_rules(cyc_rules, load_rules())
    for path, step in ((NETWORK_PATH, "make cycle-network"), (ROUTES_PATH, "make cycle-network"), (GAPS_PATH, "make cycle-network"),
                       (FINAL_PATH, "make coherence"), (ALKIS_PATH, "make fetch"), (SIGNALS_PATH, "make fetch")):
        if not path.exists():
            print(f"cycle-principles: {path.relative_to(REPO_ROOT)} missing; run `{step}` first", file=sys.stderr)
            return 1
    t0 = time.perf_counter()

    def tick(msg: str) -> None:
        print(f"cycle-principles: {msg} ({time.perf_counter() - t0:.0f} s)")

    manifest = load_manifest()
    pbf = REPO_ROOT / _pbf_from_manifest(manifest)["path"]
    net = gpd.read_parquet(NETWORK_PATH)
    routes = gpd.read_parquet(ROUTES_PATH)
    gaps = gpd.read_parquet(GAPS_PATH)
    final = pd.read_parquet(FINAL_PATH, columns=["segment_id", "cat_final", "dtv_official", "name"]).set_index("segment_id")
    districts = read_districts()
    hamburg = districts.union_all()
    n = len(net)
    rank = net["cycle_cat_final"].map(cn.RANK).to_numpy()
    length = net["length_m"].to_numpy(dtype="float64")
    geoms = net.geometry.values
    node_u = net["node_u"].to_numpy(dtype="int64")
    node_v = net["node_v"].to_numpy(dtype="int64")
    main_comp = net["in_main_component"].to_numpy(dtype=bool) & (net["kind"] != "ferry").to_numpy()
    in_net = (rank >= cn.RANK["BASIS"]) | net["route_id"].notna().to_numpy()

    # OSM values
    way_ids = {int(w) for ws in net["osm_way_ids"] for w in ws}
    tags = read_way_tags(pbf, way_ids)
    tick(f"OSM tags of {len(tags)} ways")
    ef = edge_frame(net, final, tags, p)

    # stops per edge (C-PRI-05)
    signals = gpd.read_parquet(SIGNALS_PATH)
    signal_nodes = set(signals.loc[signals["osm_type"] == "node", "id"].astype("int64").tolist())
    prio = net["priority"].fillna(False).to_numpy(dtype=bool)
    seg_prio = pd.Series(prio[(net["kind"] == "road").to_numpy()], index=net.loc[net["kind"] == "road", "segment_id"]).groupby(level=0).any()
    edge_prio = np.where(ef["is_sidepath"].to_numpy(), net["sidepath_of"].map(seg_prio).fillna(False).to_numpy(dtype=bool), prio)
    prio_nodes = set(node_u[prio].tolist()) | set(node_v[prio].tolist())
    end_sig = np.isin(node_u, list(signal_nodes)).astype(int) + np.isin(node_v, list(signal_nodes)).astype(int)
    interior = np.maximum(net["n_signals"].fillna(0).to_numpy(dtype=int) - end_sig, 0)

    # crashes (aggregated per edge only)
    crashes, years = load_crashes(manifest)
    agg = aggregate_crashes(net.geometry, crashes, p.crash_snap_m, 1.0)
    crashes_cyc = agg["crashes_cyc"].to_numpy(dtype="float64")
    del crashes
    tick(f"crashes {min(years)}–{max(years)} aggregated")

    # green share (network edges only)
    green_polys = read_green(p, hamburg)
    trees = read_trees(pbf)
    tree_pts = np.array([g for g in trees if g.geom_type == "Point"], dtype=object)
    tree_rows = np.array([g for g in trees if g.geom_type != "Point"], dtype=object)
    crowns = np.concatenate([tree_pts, tree_rows]) if len(tree_rows) else tree_pts
    green = pr.prepare_green(green_polys, crowns, p.tree_radius_m)
    green_share = np.full(n, np.nan)
    green_share[in_net] = pr.green_share(geoms[in_net], green, p.green_buffer_m)
    tick(f"green share ({len(green_polys)} ALKIS areas, {len(tree_pts)} trees, {len(tree_rows)} tree rows)")

    gap_share = gap_edge_share(geoms, rank, gaps, p)
    sc, known, appl, vals = edge_checks(ef, length, crashes_cyc, np.nan_to_num(green_share, nan=0.0), gap_share, in_net, p)

    # routes
    g_len = pr.length_graph(node_u[main_comp], node_v[main_comp], length[main_comp])
    comp_stats, comp_nodes = {}, {}
    for lvl in NETWORK_LEVELS:
        nc, share, big = components(node_u, node_v, length, rank >= cn.RANK[lvl])
        comp_stats[lvl], comp_nodes[lvl] = (nc, share), big
    pos_of = {e: i for i, e in enumerate(net["edge_id"])}
    rv = route_values(routes, net, ef, pos_of, signal_nodes, edge_prio, prio_nodes, interior, g_len, comp_nodes, p)
    tick(f"{len(routes)} routes: detour, stops, continuity")
    rsc, rknown, rappl = aggregate_routes(routes, rv, length, sc, known, appl, crashes_cyc, p)
    r_ps, r_tot, r_conf = {}, {}, {}
    for view in ("ist", "soll"):
        kn = rknown if view == "ist" else {c: np.where(rappl[c], np.isfinite(rsc["soll"][c]).astype(float), 0.0) for c in p.check_principle}
        for c in p.unavailable:
            kn[c] = np.zeros(len(routes))
        r_ps[view], r_tot[view], r_conf[view] = scores_and_confidence(
            {c: rsc[view][c] for c in p.check_principle if c not in p.network_only}, kn, rappl, p)

    # edges of the Soll network: own checks plus route checks of the primary route
    route_pos = {rid: i for i, rid in enumerate(routes["route_id"])}
    prim = net["route_id"].map(route_pos)
    has_route = prim.notna().to_numpy()
    prim_i = prim.fillna(-1).to_numpy(dtype=int)
    esc = {"ist": {}, "soll": {}}
    eknown, eappl = {}, {}
    for c in p.check_principle:
        if c in p.network_only:
            continue
        if c in ROUTE_ONLY_CHECKS:
            for view in ("ist", "soll"):
                esc[view][c] = np.where(has_route, rsc[view][c][prim_i], np.nan)
            eknown[c] = np.where(has_route, rknown[c][prim_i], 0.0)
            eappl[c] = np.where(has_route, rappl[c][prim_i], False)
        elif c in p.unavailable:
            for view in ("ist", "soll"):
                esc[view][c] = np.full(n, np.nan)
            eknown[c], eappl[c] = np.zeros(n), np.ones(n, dtype=bool)
        else:
            for view in ("ist", "soll"):
                esc[view][c] = sc[view][c]
            eknown[c], eappl[c] = known[c].astype(float), appl[c]
    e_ps, e_tot, e_conf = {}, {}, {}
    for view in ("ist", "soll"):
        kn = eknown if view == "ist" else {c: np.where(eappl[c], np.isfinite(esc["soll"][c]).astype(float), 0.0) for c in eknown}
        for c in p.unavailable:
            kn[c] = np.zeros(n)
        e_ps[view], e_tot[view], e_conf[view] = scores_and_confidence(esc[view], kn, eappl, p)
    tick("scores and confidence")

    # network KPIs
    g_all = g_len
    od = od_detours(net, rank, main_comp, p, g_all)
    tick("OD detour sample")
    st = gtfs.rapid_transit_stations(_gtfs_path(manifest), DemandParams.from_rules(cyc_rules).rapid_transit_route_types)
    st = st[st.within(hamburg)]
    schools = gpd.read_parquet(SCHOOLS_PATH).geometry.representative_point()
    uni_raw = gpd.read_parquet(UNIVERSITIES_PATH)
    net_params = cn.NetworkParams.from_rules(cyc_rules)
    uni = uni_raw[uni_raw["amenity"].isin(net_params.university_amenity)].geometry.representative_point()
    zone_tree = shapely.STRtree(shapely.buffer(geoms[rank >= cn.RANK["HAUPT"]], net_params.coverage_m))
    coverage = {}
    for name, g in (("Schulen (OSM)", schools[schools.within(hamburg)]), ("Schnellbahnhalte", st.geometry),
                    ("Hochschulen (OSM university)", uni[uni.within(hamburg)])):
        hit = zone_tree.query(g.values, predicate="within")[0]
        coverage[name] = (len(g), len(np.unique(hit)) / len(g) if len(g) else float("nan"))
    gap_stats = {lvl: {"n": int((gaps["level"] == lvl).sum()), "max_m": net_params.mesh_max_m[lvl],
                       "median": float(gaps.loc[gaps["level"] == lvl, "side_m"].median()) if (gaps["level"] == lvl).any() else np.nan,
                       "max": float(gaps.loc[gaps["level"] == lvl, "side_m"].max()) if (gaps["level"] == lvl).any() else np.nan}
                 for lvl in ("HAUPT", "BASIS")}

    # sensitivity (C-PRI-14): ranking by need = (score_soll - score_ist) x km
    route_km = routes["length_m"].to_numpy(dtype="float64") / 1000
    base_delta = (r_tot["soll"] - r_tot["ist"]) * route_km
    sens = []
    for name in p.weights:
        for f in (1 - p.sens_delta, 1 + p.sens_delta):
            wv = pr.vary_weights(p.weights, name, f)
            d = (pr.total_score(r_ps["soll"], wv) - pr.total_score(r_ps["ist"], wv)) * route_km
            sens.append({"principle": name, "base": p.weights[name], "value": wv[name],
                         "overlap": pr.top_overlap(base_delta, d, routes["route_id"].to_numpy(), p.top_n),
                         "spearman": float(pd.Series(base_delta).corr(pd.Series(d), method="spearman"))})

    # output tables
    check_cols = [c for c in p.check_principle if c not in p.network_only]
    labels = net["name"].where(net["name"].notna() & (net["name"] != ""), None)
    labels = labels.fillna(("neben " + net["sidepath_of"].map(final["name"])).where(net["sidepath_of"].map(final["name"]).notna(), None)).fillna("–")
    edge_extra = []
    for i in range(n):
        edge_extra.append({
            "P-SAF-01": {"ist": ef["facility_ist"].iat[i], "soll": ef["facility_soll"].iat[i], "fallback": ef["facility_fallback"].iat[i],
                         "from_sidepath": bool(ef["from_sidepath"].iat[i])},
            "P-SAF-03": {"lit": ef["lit"].iat[i]},
            "P-SAF-04": {"crashes_cyc_5y": int(crashes_cyc[i])},
            "P-COM-01": {"width_m": None if not np.isfinite(ef["width_m"].iat[i]) else round(float(ef["width_m"].iat[i]), 2),
                         "required_m": None if not np.isfinite(vals["width_required_m"].iat[i]) else round(float(vals["width_required_m"].iat[i]), 2)},
            "P-COM-02": {"surface": ef["surface"].iat[i]},
            "P-ATT-01": {"green_share": None if not np.isfinite(green_share[i]) else round(float(green_share[i]), 3)},
            "P-ATT-03": {"dtv": None if not np.isfinite(ef["dtv"].iat[i]) else round(float(ef["dtv"].iat[i]))},
            "P-COH-01": {"mesh_gap_share": round(float(gap_share[i]), 3)},
            "P-DIR-01": {"from_route": net["route_id"].iat[i]},
        })
    sel = np.flatnonzero(in_net)
    sub = lambda d: {c: np.asarray(v)[sel] for c, v in d.items()}  # noqa: E731
    e_trace = trace_rows({"ist": sub(esc["ist"]), "soll": sub(esc["soll"])}, sub(eknown), [edge_extra[i] for i in sel], check_cols)
    E = pd.DataFrame({
        "level": "edge", "id": net["edge_id"].to_numpy()[sel], "route_id": net["route_id"].to_numpy()[sel],
        "category": net["cycle_cat_final"].to_numpy()[sel], "label": labels.to_numpy()[sel], "length_m": length[sel],
        "bezirk": net["bezirk"].to_numpy()[sel], "cat_final": ef["cat_final"].to_numpy()[sel],
        "facility_ist": ef["facility_ist"].to_numpy()[sel], "facility_soll": ef["facility_soll"].to_numpy()[sel],
        "width_m": ef["width_m"].to_numpy()[sel], "width_required_m": vals["width_required_m"].to_numpy()[sel],
        "surface": ef["surface"].to_numpy()[sel], "lit": ef["lit"].to_numpy()[sel],
        "crashes_cyc_5y": crashes_cyc[sel].astype(int), "crashes_cyc_per_km_5y": vals["crashes_cyc_per_km_5y"].to_numpy()[sel],
        "green_share": green_share[sel], "dtv": ef["dtv"].to_numpy()[sel], "mesh_gap_share": gap_share[sel],
    })
    for c in check_cols:
        for view in ("ist", "soll"):
            E[_col(c, view)] = esc[view][c][sel]
    for view in ("ist", "soll"):
        for k in p.weights:
            E[f"{k}_{view}"] = e_ps[view][k][sel]
        E[f"score_{view}"] = e_tot[view][sel]
        E[f"confidence_{view}"] = e_conf[view][sel]
    E["delta"] = E["score_soll"] - E["score_ist"]
    E["confidence"] = pr.confidence_class(E["confidence_ist"], p)
    E["rule_trace_principles"] = e_trace
    E = gpd.GeoDataFrame(E, geometry=geoms[sel], crs=WORK_CRS)

    bez_of_route, street_of_route = [], []
    bez_arr = net["bezirk"].fillna(NO_DISTRICT).to_numpy()
    lab_arr = labels.to_numpy()
    for e in rv["edges"]:
        s = pd.Series(length[e]).groupby(bez_arr[e]).sum()
        bez_of_route.append(s.idxmax() if len(s) else None)
        st_ = pd.Series(length[e]).groupby(lab_arr[e]).sum().drop("–", errors="ignore")
        street_of_route.append(st_.idxmax() if len(st_) else None)
    route_label = [f"{lab}: {st_}" if kind != "corridor" and st_ else lab
                   for lab, kind, st_ in zip(routes["label"], routes["kind"], street_of_route)]
    r_extra = [{"P-DIR-01": {"detour": None if not np.isfinite(a) else round(float(a), 3)},
                "P-DIR-02": {"signals": None if not np.isfinite(sg) else int(sg), "give_way": None if not np.isfinite(gw) else int(gw),
                             "stops_per_km": None if not np.isfinite(spk) else round(float(spk), 2)},
                "P-DIR-03": {"time_loss_s_per_km": None if not np.isfinite(tl) else round(float(tl), 1)},
                "P-SAF-04": {"crashes_cyc_per_km_5y": round(float(rt), 2)},
                "P-COH-02": {"in_main_component": bool(mc)},
                "P-COH-04": {"changes_ist_per_km": None if not np.isfinite(ci) else round(float(ci), 2),
                             "changes_soll_per_km": None if not np.isfinite(cs) else round(float(cs), 2)}}
               for a, sg, gw, spk, tl, rt, mc, ci, cs in zip(rv["detour"], rv["signals"].astype(float), rv["give_way"].astype(float),
                                                             rv["stops_per_km"], rv["time_loss_s_per_km"], rsc["rate"], rv["in_main_component"],
                                                             rv["changes_ist_per_km"], rv["changes_soll_per_km"])]
    r_trace = trace_rows({"ist": rsc["ist"], "soll": rsc["soll"]}, rknown, r_extra, check_cols)
    Rt = pd.DataFrame({
        "level": "route", "id": routes["route_id"].to_numpy(), "route_id": routes["route_id"].to_numpy(),
        "category": routes["category"].to_numpy(), "label": route_label, "length_m": routes["length_m"].to_numpy(),
        "main_street": street_of_route, "bezirk": bez_of_route, "route_kind": routes["kind"].to_numpy(), "detour": rv["detour"].to_numpy(),
        "stops_per_km": rv["stops_per_km"].to_numpy(dtype="float64"), "time_loss_s_per_km": rv["time_loss_s_per_km"].to_numpy(dtype="float64"),
        "crashes_cyc_per_km_5y": rsc["rate"], "changes_ist_per_km": rv["changes_ist_per_km"].to_numpy(),
        "changes_soll_per_km": rv["changes_soll_per_km"].to_numpy(),
    })
    for c in check_cols:
        for view in ("ist", "soll"):
            Rt[_col(c, view)] = rsc[view][c]
    for view in ("ist", "soll"):
        for k in p.weights:
            Rt[f"{k}_{view}"] = r_ps[view][k]
        Rt[f"score_{view}"] = r_tot[view]
        Rt[f"confidence_{view}"] = r_conf[view]
    Rt["delta"] = Rt["score_soll"] - Rt["score_ist"]
    Rt["need_km"] = Rt["delta"] * Rt["length_m"] / 1000
    Rt["confidence"] = pr.confidence_class(Rt["confidence_ist"], p)
    Rt["rule_trace_principles"] = r_trace
    Rt = gpd.GeoDataFrame(Rt, geometry=routes.geometry.values, crs=WORK_CRS)
    out = pd.concat([E, Rt], ignore_index=True)
    out = gpd.GeoDataFrame(out, geometry="geometry", crs=WORK_CRS)
    out["lit"] = out["lit"].map(lambda x: None if x is None or (isinstance(x, float) and np.isnan(x)) else bool(x)).astype("boolean")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_PATH, index=False)
    tick(f"{len(E)} edges and {len(Rt)} routes -> {OUT_PATH.relative_to(REPO_ROOT)}")

    # report inputs
    w_net = length[sel]
    avail_src = {"P-COH-01": "c03 Maschen", "P-COH-02": "Soll-Netz", "P-COH-04": "Ist-Führung entlang der Route", "P-DIR-01": "Radgraph (Länge)",
                 "P-DIR-02": "OSM-LSA, Vorfahrt C-GRAPH-05", "P-DIR-03": "wie P-DIR-02", "P-SAF-01": "Ist-Führung (C-PRI-02), Trennungsmatrix",
                 "P-SAF-02": "–", "P-SAF-03": "OSM lit", "P-SAF-04": "Unfallatlas", "P-COM-01": "OSM width/cycleway:width",
                 "P-COM-02": "OSM surface", "P-COM-03": "–", "P-ATT-01": "ALKIS, OSM-Bäume", "P-ATT-02": "–", "P-ATT-03": "DTV 2019 (HVS)"}
    availability = {}
    for c in check_cols:
        a = np.asarray(eappl[c], dtype=bool)[sel]
        k = np.asarray(eknown[c], dtype="float64")[sel]
        km = w_net[a].sum() / 1000
        availability[c] = (avail_src.get(c, ""), km, (w_net[a] * k[a]).sum() / w_net[a].sum() if a.any() else np.nan)
    lit_known = E["lit"].notna().to_numpy()
    lit_share = w_net[lit_known & (E["lit"] == True).to_numpy()].sum() / w_net[lit_known].sum() if lit_known.any() else np.nan  # noqa: E712
    wk = np.isfinite(E["width_m"]) & np.isfinite(E["width_required_m"])
    width_ok = w_net[wk & (E["width_m"] >= E["width_required_m"] - 1e-9)].sum() / w_net[wk].sum() if wk.any() else np.nan
    hr = E["category"].isin(["RSV", "HAUPT"]).to_numpy()
    sk = hr & E["surface"].notna().to_numpy()
    smooth_share = w_net[sk & E["surface"].isin(list(p.smooth_surfaces)).to_numpy()].sum() / w_net[sk].sum() if sk.any() else np.nan
    ft = pd.DataFrame({"ist": E["facility_ist"].fillna("unknown"), "soll": E["facility_soll"].fillna("unknown"), "km": w_net / 1000})
    facility_table = ft.pivot_table(index="ist", columns="soll", values="km", aggfunc="sum", fill_value=0.0)

    maps = {}
    for k in p.weights:
        path = MAP_DIR / f"cycle_principles_{k}.png"
        map_principle(path, geoms[sel], E[f"{k}_ist"].to_numpy(), E[f"{k}_soll"].to_numpy(), districts,
                      f"{PRINCIPLE_DE[k]}: Score je Kante des Soll-Netzes (Entwurf, nicht amtlich)")
        maps[PRINCIPLE_DE[k]] = path
    path = MAP_DIR / "cycle_principles_delta.png"
    map_principle(path, geoms[sel], E["delta"].to_numpy(), None, districts, "Handlungsbedarf: score_soll − score_ist je Kante",
                  cmap="Reds", vmin=0.0, vmax=float(np.nanquantile(E["delta"], 0.98)) or 1.0, labels=("Handlungsbedarf", ""))
    maps["Handlungsbedarf"] = path
    tick("maps")

    sample = sample_by_district(E.drop(columns="geometry").assign(geometry=E.geometry.values), SAMPLE_SIZE, SAMPLE_SEED, id_col="id")
    review = pr.stratified_sample(Rt.drop(columns="geometry").assign(geometry=Rt.geometry.values), "category", "id", p.review_n, p.review_seed)
    viewers = load_viewers()
    rev = review[["id", "label", "category", "length_m", "score_ist", "score_soll", "delta", "need_km", "confidence"] + [f"{k}_ist" for k in p.weights]].copy()
    rev.insert(0, "route_id", rev.pop("id"))
    rev["length_m"] = rev["length_m"].round(0)
    for c in rev.select_dtypes("float").columns:
        rev[c] = rev[c].round(3)
    mids = [g.interpolate(0.5, normalized=True) for g in review["geometry"]]
    mids_w = gpd.GeoSeries(mids, crs=WORK_CRS).to_crs("EPSG:4326")
    rev["orthophoto"] = [orthophoto_link(m, viewers) for m in mids]
    rev["panoramax"] = [panoramax_link(m, viewers) for m in mids_w]
    rev["osm"] = [osm_map_link(m) for m in mids_w]
    rev["reviewer"] = ""
    rev["assessment"] = ""
    rev["comment"] = ""
    rev.to_csv(REVIEW_PATH, index=False)

    ctx = {"p": p, "version": cyc_rules.meta.version, "edges": E, "routes": Rt, "availability": availability, "od": od,
           "components": comp_stats, "coverage": coverage, "coverage_m": net_params.coverage_m, "gaps": gap_stats,
           "facility_table": facility_table, "lit_share": lit_share, "width_ok": width_ok, "smooth_share": smooth_share,
           "high_dtv_km": w_net[E["dtv"].fillna(0).to_numpy() > p.patt_dtv].sum() / 1000,
           "crash_years": f"{min(years)}–{max(years)}", "crashes_total": float(E["crashes_cyc_5y"].sum()),
           "sensitivity": sens, "maps": maps, "sample": sample, "review": review}
    write_report(ctx)
    tick(f"report {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
