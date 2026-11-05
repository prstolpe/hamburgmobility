"""Cycle stage 2: cycle demand per edge (prompts/15_cycle_demand.md, steps 2–3).

Usage: uv run python -m pipeline.c02_cycle_demand

Gravity model from 500 m zones (Zensus population) to destinations (non-residential floor area,
shops, schools, universities, rapid-transit stations), assigned to shortest paths on the Ist
resistance of data/interim/cycle_graph.parquet, calibrated with one factor on the bike counters
without direction (C-DEM-01..07). DB Rad+ only as a plausibility check. Writes
data/interim/cycle_edges.parquet and reports/cycle_demand.md (+ two PNG figures).
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

from pipeline.lib import cycle_demand as cd
from pipeline.lib import cycle_graph as cg
from pipeline.lib import gtfs
from pipeline.lib.area import NO_DISTRICT, RURAL_PATH, read_districts, sample_by_district
from pipeline.lib.crs import WORK_CRS, to_work_crs
from pipeline.lib.links import load_viewers, orthophoto_link, osm_map_link, panoramax_link
from pipeline.lib.manifest import REPO_ROOT, load_manifest
from pipeline.lib.rules import load_cycling_rules
from pipeline.s02_network import _pbf_from_manifest

RAW = REPO_ROOT / "data" / "raw"
GRAPH_PATH = REPO_ROOT / "data" / "interim" / "cycle_graph.parquet"
OUT_PATH = REPO_ROOT / "data" / "interim" / "cycle_edges.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "cycle_demand.md"
SCATTER_PATH = REPO_ROOT / "reports" / "cycle_demand_scatter.png"
MAP_PATH = REPO_ROOT / "reports" / "cycle_demand_map.png"
GRID_CRS = "EPSG:3035"  # Zensus grid; zones are aligned to it (C-DEM-01)
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
TOP_N = 30


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _fmt(v: float, digits: int = 0) -> str:
    return f"{v:,.{digits}f}".replace(",", " ")


# --- inputs ------------------------------------------------------------------------------------


def _gtfs_path(manifest: dict):
    files = (manifest["sources"].get("gtfs_hvv") or {}).get("files") or []
    paths = [REPO_ROOT / f["path"] for f in files if (REPO_ROOT / f["path"]).exists()]
    if not paths:
        raise FileNotFoundError("GTFS feed missing; run `make fetch`")
    return paths[0]


def read_shops(pbf) -> gpd.GeoDataFrame:
    from pyrosm import OSM

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pois = OSM(str(pbf)).get_pois(custom_filter={"shop": True})
    pois = to_work_crs(pois[pois["shop"].notna()].reset_index(drop=True))
    return gpd.GeoDataFrame(geometry=pois.geometry.representative_point(), crs=WORK_CRS)


def destination_points(params: cd.DemandParams, manifest: dict, pbf, hamburg) -> dict[str, gpd.GeoDataFrame]:
    """Point layers with a `value` column per destination type (C-DEM-02/03), inside Hamburg."""
    b = gpd.read_parquet(RAW / "alkis__GebaeudeBauwerk.parquet", columns=["gebnutzbez", "funktion", "anzahlgs", "rellage", "geometry"])
    jobs = gpd.GeoDataFrame({"value": cd.jobs_floor_area(b, params).to_numpy()},
                            geometry=b.geometry.representative_point().to_numpy(), crs=WORK_CRS)
    jobs = jobs[jobs["value"] > 0]
    layers = {"jobs_floor_area": jobs}
    shops = read_shops(pbf)
    layers["shops"] = shops.assign(value=1.0)
    for t, f in (("schools", "schools__osm.parquet"), ("universities", "universities__osm.parquet")):
        g = gpd.read_parquet(RAW / f)
        layers[t] = gpd.GeoDataFrame({"value": np.ones(len(g))}, geometry=g.geometry.representative_point().to_numpy(), crs=g.crs)
    st = gtfs.rapid_transit_stations(_gtfs_path(manifest), params.rapid_transit_route_types)
    layers["rapid_transit_stops"] = st.assign(value=1.0)[["value", "geometry"]]
    return {t: g[g.within(hamburg)].reset_index(drop=True) for t, g in layers.items()}


def zone_points(params: cd.DemandParams, hamburg, layers: dict) -> pd.DataFrame:
    """One row per input point: zone key, x/y (EPSG:25832), population and one column per destination type."""
    pop = gpd.read_parquet(RAW / "population_grid__100m.parquet")
    pop = gpd.GeoDataFrame({"population": pop["population"].to_numpy()}, geometry=pop.geometry.centroid.to_numpy(), crs=pop.crs)
    pop = pop[pop.within(hamburg)]
    frames = [pop.assign(kind="population")]
    for t, g in layers.items():
        frames.append(gpd.GeoDataFrame({t: g["value"].to_numpy(), "kind": t}, geometry=g.geometry.to_numpy(), crs=WORK_CRS))
    pts = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry="geometry", crs=WORK_CRS)
    cols = ["population", *params.weights]
    pts[cols] = pts[cols].fillna(0.0)
    g = pts.geometry.to_crs(GRID_CRS)
    ix, iy = cd.zone_index(g.x.to_numpy(), g.y.to_numpy(), params.zone_m)
    pts["zone"] = [f"{a}_{b}" for a, b in zip(ix, iy)]
    pts["x"], pts["y"] = pts.geometry.x, pts.geometry.y
    return pd.DataFrame(pts.drop(columns="geometry"))


def build_zones(params: cd.DemandParams, pts: pd.DataFrame) -> pd.DataFrame:
    cols = ["population", *params.weights]
    z = cd.aggregate(pts, cols)
    z["attraction"] = cd.attraction(z, params.weights)
    # zone point: weighted by the point's share of population plus its weighted share of attraction
    w = pts["population"] / pts["population"].sum()
    for t, wt in params.weights.items():
        total = pts[t].sum()
        if total > 0:
            w = w + wt * pts[t] / total
    pts = pts.assign(_w=w, _wx=w * pts["x"], _wy=w * pts["y"])
    s = pts.groupby("zone")[["_w", "_wx", "_wy"]].sum()
    z["x"], z["y"] = s["_wx"] / s["_w"], s["_wy"] / s["_w"]
    return z[(z["population"] > 0) | (z["attraction"] > 0)]


# --- model ---------------------------------------------------------------------------------------


def snap_zones(z: pd.DataFrame, edges: gpd.GeoDataFrame) -> pd.Series:
    """Nearest end node of a routable (main component, not ferry) edge for each zone point."""
    e = edges[edges["in_main_component"] & (edges["kind"] != "ferry")]
    nodes = pd.concat([pd.DataFrame({"node": e["node_u"].to_numpy(), "geometry": shapely.get_point(e.geometry.values, 0)}),
                       pd.DataFrame({"node": e["node_v"].to_numpy(), "geometry": shapely.get_point(e.geometry.values, -1)})])
    nodes = gpd.GeoDataFrame(nodes.drop_duplicates("node"), geometry="geometry", crs=WORK_CRS)
    zp = gpd.GeoDataFrame(index=z.index, geometry=gpd.points_from_xy(z["x"], z["y"]), crs=WORK_CRS)
    j = gpd.sjoin_nearest(zp, nodes, distance_col="snap_m")
    j = j[~j.index.duplicated()]
    return j["node"], j["snap_m"]


def run_model(params: cd.DemandParams, edges: gpd.GeoDataFrame, z: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, dict]:
    """Model trips per edge and direction (mean over the runs of C-DEM-05) and run statistics."""
    main = edges["in_main_component"].to_numpy()
    sub = edges[main]
    a = cg.arcs(sub)
    node_ids = np.unique(np.concatenate([a["tail"].to_numpy(), a["head"].to_numpy()]))
    idx = {n: i for i, n in enumerate(node_ids.tolist())}
    tail = np.array([idx[n] for n in a["tail"].tolist()])
    head = np.array([idx[n] for n in a["head"].tolist()])
    origins_z = z[z["population"] > 0]
    dests_z = z[z["attraction"] > 0]
    origin_nodes = [idx[n] for n in origins_z["node"]]
    dest_nodes = np.array([idx[n] for n in dests_z["node"]])
    prod = origins_z["population"].to_numpy(dtype="float64")
    attr = dests_z["attraction"].to_numpy(dtype="float64")
    fwd = np.zeros(len(sub))
    bwd = np.zeros(len(sub))
    runs = []
    ids = params.iteration_ids()
    for it in ids:
        t0 = time.perf_counter()
        acc = {"trips": 0.0, "trip_km": 0.0, "no_dest": 0}

        def od(i, d_m):
            t = cd.gravity_row(prod[i], attr, d_m / 1000.0, params.beta_per_km, params.distance_band_km)
            s = t.sum()
            if s == 0:
                acc["no_dest"] += 1
            else:
                acc["trips"] += s
                acc["trip_km"] += float((t * np.where(np.isfinite(d_m), d_m, 0)).sum()) / 1000.0
            return t

        cost = a["cost"].to_numpy() * cd.noise_factors(len(a), params.noise_sigma, params.seed, it)
        flows = cd.assign_od(len(node_ids), tail, head, cost, origin_nodes, dest_nodes, od)
        f = np.zeros(len(sub))
        b = np.zeros(len(sub))
        fw = a["forward"].to_numpy()
        np.add.at(f, a["edge"].to_numpy()[fw], flows[fw])
        np.add.at(b, a["edge"].to_numpy()[~fw], flows[~fw])
        fwd += f / len(ids)
        bwd += b / len(ids)
        runs.append({"iteration": it, "seconds": time.perf_counter() - t0, "trips": acc["trips"],
                     "mean_km": acc["trip_km"] / acc["trips"] if acc["trips"] else float("nan"),
                     "origins_without_destination": acc["no_dest"]})
        print(f"cycle-demand: run {it}: {runs[-1]['seconds']:.0f} s, {acc['trips']:.0f} trips, "
              f"mean {runs[-1]['mean_km']:.2f} km")
    out_f = np.full(len(edges), np.nan)
    out_b = np.full(len(edges), np.nan)
    out_f[main], out_b[main] = fwd, bwd
    stats = {"runs": runs, "n_nodes": len(node_ids), "n_arcs": len(a), "n_origins": len(origin_nodes),
             "n_destinations": len(dest_nodes), "population": float(prod.sum())}
    return out_f, out_b, stats


# --- calibration and checks ----------------------------------------------------------------------


def cross_sections(params: cd.DemandParams, edges: gpd.GeoDataFrame, model_day: np.ndarray,
                   districts: gpd.GeoDataFrame) -> pd.DataFrame:
    stations = gpd.read_parquet(RAW / "bike_counters__stations.parquet").to_crs(WORK_CRS)
    daily = pd.read_parquet(RAW / "bike_counters__daily_2025.parquet")
    values = cd.counter_values(stations, daily, params.min_valid_weekdays)
    routable = (edges["in_main_component"] & (edges["kind"] != "ferry")).to_numpy()
    pos = np.flatnonzero(routable)
    geoms = gpd.GeoSeries(edges.geometry.values[pos], crs=WORK_CRS)
    st = stations.set_index("thing_id")
    rows = []
    for tid, v in values.iterrows():
        p = st.at[tid, "geometry"]
        hit = cd.cross_section_rows(geoms, p, params.transect_half_m, params.counter_snap_m, params.transect_min_angle_deg)
        e = pos[hit]
        rows.append({"thing_id": tid, "name": st.at[tid, "name"], "count_weekday": v["count_weekday"],
                     "n_weekdays": int(v["n_weekdays"]), "n_edges": len(e),
                     "edge_ids": [edges["edge_id"].iat[i] for i in e],
                     "model": float(np.nansum(model_day[e])) if len(e) else np.nan, "geometry": p})
    cs = gpd.GeoDataFrame(rows, geometry="geometry", crs=WORK_CRS)
    j = gpd.sjoin(cs, districts[["name", "geometry"]].rename(columns={"name": "bezirk"}), how="left", predicate="within")
    cs["bezirk"] = j[~j.index.duplicated()]["bezirk"].reindex(cs.index)
    cs.attrs["n_stations"] = len(stations)
    cs.attrs["n_undirected"] = int((stations["richtung"] == cd.UNDIRECTED).sum())
    return cs


def dbradplus_compare(params: cd.DemandParams, edges: gpd.GeoDataFrame, cal: np.ndarray) -> dict | None:
    path = RAW / "bike_volumes_dbradplus__jahr2025.parquet"
    if not path.exists():
        return None
    db = gpd.read_parquet(path, columns=["anzahl", "geometry"])
    mid = gpd.GeoDataFrame({"anzahl": db["anzahl"].to_numpy()},
                           geometry=db.geometry.interpolate(0.5, normalized=True).to_numpy(), crs=db.crs)
    ok = np.isfinite(cal) & (cal > 0) & (edges["kind"] != "ferry").to_numpy()
    e = gpd.GeoDataFrame({"pos": np.flatnonzero(ok)}, geometry=edges.geometry.values[ok], crs=WORK_CRS)
    j = gpd.sjoin_nearest(mid, e, max_distance=params.dbradplus_snap_m, how="inner")
    per_edge = j.groupby("pos")["anzahl"].max()
    from scipy import stats as sstats
    x = cal[per_edge.index.to_numpy()]
    y = per_edge.to_numpy(dtype="float64")
    return {"n_lines": len(db), "n_matched_lines": len(j), "n_edges": len(per_edge),
            "spearman": float(sstats.spearmanr(x, y).statistic),
            "pearson_log": float(np.corrcoef(np.log(x), np.log(y))[0, 1]), "per_edge": per_edge}


# --- figures ------------------------------------------------------------------------------------


def scatter_png(cs: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    c = cs[cs["cyc_calibrated"] > 0]
    fig, ax = plt.subplots(figsize=(6.5, 6), dpi=130)
    ax.scatter(c["count_weekday"], c["cyc_calibrated"], s=18, color="#2b6cb0", alpha=0.8)
    lim = [min(c["count_weekday"].min(), c["cyc_calibrated"].min()) * 0.8,
           max(c["count_weekday"].max(), c["cyc_calibrated"].max()) * 1.25]
    ax.plot(lim, lim, color="#444", lw=1)
    ax.plot(lim, [v * 2 for v in lim], color="#999", lw=0.8, ls="--")
    ax.plot(lim, [v / 2 for v in lim], color="#999", lw=0.8, ls="--")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("Zählwert Rad/Werktag (Mo–Fr 2025)")
    ax.set_ylabel("Modell kalibriert Rad/Werktag")
    ax.set_title("Modell vs. Zählstellen (Linie 1:1, gestrichelt Faktor 2)")
    fig.tight_layout()
    fig.savefig(SCATTER_PATH)
    plt.close(fig)


def map_png(edges: gpd.GeoDataFrame, cal: np.ndarray, cs: pd.DataFrame, districts: gpd.GeoDataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.colors import LogNorm

    ok = np.isfinite(cal) & (cal > 0)
    order = np.argsort(cal[ok])
    geoms = edges.geometry.values[ok][order]
    vals = cal[ok][order]
    segs = [np.asarray(g.coords)[:, :2] for g in geoms]
    fig, ax = plt.subplots(figsize=(12, 10), dpi=100)
    districts.boundary.plot(ax=ax, color="#bbb", lw=0.6)
    norm = LogNorm(vmin=max(np.percentile(vals, 5), 1), vmax=np.percentile(vals, 99.5))
    lc = LineCollection(segs, array=vals, cmap="viridis", norm=norm,
                        linewidths=0.2 + 2.0 * np.clip(np.log10(np.maximum(vals, 1)) / 4, 0, 1))
    ax.add_collection(lc)
    ax.scatter(cs.geometry.x, cs.geometry.y, s=10, facecolor="none", edgecolor="#d53f3f", lw=0.8, label="Zählquerschnitt")
    fig.colorbar(lc, ax=ax, shrink=0.6, label="Rad/Werktag (Modell, kalibriert)")
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.legend(loc="lower left")
    ax.set_title("Radverkehrsstärke je Kante (Modell, nicht amtlich)")
    fig.tight_layout()
    fig.savefig(MAP_PATH)
    plt.close(fig)


# --- report ---------------------------------------------------------------------------------------


def _links(geom, viewers) -> str:
    p = geom.interpolate(0.5, normalized=True) if geom.geom_type != "Point" else geom
    pw = gpd.GeoSeries([p], crs=WORK_CRS).to_crs("EPSG:4326").iloc[0]
    return (f"[Luftbild]({orthophoto_link(p, viewers)}) · [Panoramax]({panoramax_link(pw, viewers)}) · "
            f"[OSM]({osm_map_link(pw)})")


def _labels(out: gpd.GeoDataFrame) -> pd.Series:
    """Display name: OSM name, for unnamed own paths along a street "neben <street>" (sidepath_of)."""
    names = pd.read_parquet(REPO_ROOT / "data" / "interim" / "final.parquet", columns=["segment_id", "name"]).set_index("segment_id")["name"]
    side = out["sidepath_of"].map(names)
    label = out["name"].where(out["name"].notna() & (out["name"] != ""), None)
    label = label.where(label.notna(), ("neben " + side).where(side.notna(), None))
    return label.fillna("–")


def write_report(out: gpd.GeoDataFrame, cs: gpd.GeoDataFrame, z: pd.DataFrame, layers: dict, stats: dict, fit: dict,
                 k: float, db: dict | None, params: cd.DemandParams, meta: dict) -> None:
    viewers = load_viewers()
    out = out.assign(label=_labels(out))
    km = out["length_m"] / 1000
    runs = stats["runs"]
    used = cs[cs["model"] > 0]
    lines = [
        "# Radverkehrsnachfrage (Stufe c02)",
        "",
        f"Erzeugt {_now()} mit pipeline/c02_cycle_demand.py · cycling_rules.yaml {meta['version']} · nicht amtlicher Entwurf. "
        "Alle Modellparameter sind Annahmen (source_type assumption, status draft) und vor fachlicher Nutzung zu prüfen.",
        "",
        "## Kurzfassung",
        "",
        f"- Kalibrierfaktor k = {k:.3f} (ein Faktor für Hamburg, C-DEM-06) aus {fit['n']} Zählquerschnitten.",
        f"- Güte: Spearman {fit['spearman']:.2f}, Pearson (log) {fit['pearson_log']:.2f}, Pearson {fit['pearson']:.2f}, "
        f"mittlere relative Abweichung {fit['mrd']:.0%}, {fit['share_within_factor_2']:.0%} der Querschnitte innerhalb Faktor 2.",
        f"- {_fmt(km[out['demand_confidence'] == 'hoch'].sum(), 0)} km mit Konfidenz hoch, "
        f"{_fmt(km[out['demand_confidence'] == 'mittel'].sum(), 0)} km mittel, "
        f"{_fmt(km[out['demand_confidence'] == 'niedrig'].sum(), 0)} km niedrig.",
        "- Werte sind modelliert, nicht gezählt. Sie dienen als Grundlage für Hierarchie (Prompt 16) und Breiten (Prompt 18).",
        "",
        "## Modell",
        "",
        f"- Zonen: {_fmt(len(z))} Quadrate zu {params.zone_m:.0f} m im Zensus-Gitter (EPSG:3035), davon "
        f"{_fmt(stats['n_origins'])} mit Einwohnern ({_fmt(stats['population'])} Einwohner in Hamburg) und "
        f"{_fmt(stats['n_destinations'])} mit Zielen (C-DEM-01). Zonenpunkt an den nächsten Graphknoten angebunden "
        f"(Median {z['snap_m'].median():.0f} m, Maximum {z['snap_m'].max():.0f} m).",
        "- Ziele (C-DEM-02/03), Gewicht × Anteil der Zone an der Hamburger Summe:",
        "",
        "| Zieltyp | Gewicht | Objekte | Summe | Quelle |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    src = {"jobs_floor_area": "ALKIS Gebäude (Geschossfläche Nichtwohnen, m²)", "shops": "OSM shop=*",
           "schools": "OSM amenity=school (Fallback)", "universities": "OSM amenity=university|college (Fallback)",
           "rapid_transit_stops": f"HVV-GTFS, route_type {list(params.rapid_transit_route_types)}"}
    for t, w in params.weights.items():
        lines.append(f"| {t} | {w:.2f} | {_fmt(len(layers[t]))} | {_fmt(layers[t]['value'].sum())} | {src[t]} |")
    lines += [
        "",
        f"- Verteilung (C-DEM-04): produktionsgebundenes Gravitationsmodell, f(d) = exp(−{params.beta_per_km} · d), "
        f"d = wahrgenommener Widerstand in km, nur Relationen {params.distance_band_km[0]}–{params.distance_band_km[1]} km.",
        f"- Umlegung (C-DEM-05): {params.method}, {len(runs)} Lauf/Läufe, Störung σ = {params.noise_sigma}, Seed {params.seed}; "
        f"Graph {_fmt(stats['n_nodes'])} Knoten, {_fmt(stats['n_arcs'])} gerichtete Bögen (größte stark zusammenhängende Komponente).",
        "",
        "| Lauf | Laufzeit s | Fahrten (Modell) | mittlere Weglänge km (Widerstand) | Quellzonen ohne Ziel im Band |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in runs:
        lines.append(f"| {r['iteration']} | {r['seconds']:.0f} | {_fmt(r['trips'])} | {r['mean_km']:.2f} | {r['origins_without_destination']} |")
    lines += [
        "",
        "Modellfahrten haben keine absolute Einheit (1 Fahrt je Einwohner); erst der Kalibrierfaktor macht daraus Rad/Werktag.",
        "",
        "## Kalibrierung an Zählstellen",
        "",
        f"- Zählstellen: {cs.attrs['n_stations']}, davon {cs.attrs['n_undirected']} ohne Richtung. Nur diese gehen ein; sie sind "
        "die Summe der zwei richtungsbezogenen Zählstellen am selben Querschnitt (Median-Verhältnis 1,00; geprüft 2026-11-05), "
        "so wird nichts doppelt gezählt.",
        f"- Zählwert: Mittel Mo–Fr 2025 über Tage mit count > 0, mindestens {params.min_valid_weekdays} gültige Werktage: "
        f"{len(cs)} Querschnitte. Modellwert: Summe beider Richtungen aller Kanten, die ein Querschnitt von "
        f"±{params.transect_half_m:.0f} m schneidet (≥ {params.transect_min_angle_deg:.0f}°).",
        f"- Mit Modellwert > 0: {len(used)}; ohne Kante im Umkreis von {params.counter_snap_m:.0f} m oder ohne Modellfluss: {len(cs) - len(used)}.",
        f"- k = geometrisches Mittel von Zählwert/Modellwert = **{k:.3f}**.",
        "",
        "| Kennzahl | Wert |",
        "| --- | ---: |",
        f"| Querschnitte | {fit['n']} |",
        f"| Pearson r (linear) | {fit['pearson']:.2f} |",
        f"| Pearson r (log) | {fit['pearson_log']:.2f} |",
        f"| Spearman ρ | {fit['spearman']:.2f} |",
        f"| mittlere relative Abweichung | {fit['mrd']:.0%} |",
        f"| Median Zählwert/Modell | {fit['median_ratio']:.2f} |",
        f"| Anteil innerhalb Faktor 2 | {fit['share_within_factor_2']:.0%} |",
        "",
        f"![Modell vs. Zählstellen]({SCATTER_PATH.name})",
        "",
        "Verhältnis Zählwert/Modell je Bezirk (nur Diagnose; kalibriert wird mit einem Faktor für Hamburg):",
        "",
        "| Bezirk | Querschnitte | geom. Mittel Zählwert/Modell |",
        "| --- | ---: | ---: |",
    ]
    for bez, g in used.groupby(used["bezirk"].fillna(NO_DISTRICT)):
        lines.append(f"| {bez} | {len(g)} | {np.exp(np.mean(np.log(g['count_weekday'] / g['cyc_calibrated']))):.2f} |")
    used = used.assign(ratio=used["count_weekday"] / used["cyc_calibrated"])
    lines += ["", "Größte Abweichungen (je 5 über- und unterschätzt):", "",
              "| Zählstelle | Bezirk | Zählwert | Modell | Zählwert/Modell | Kanten | Prüfen |", "| --- | --- | ---: | ---: | ---: | ---: | --- |"]
    for _, r in pd.concat([used.nsmallest(5, "ratio"), used.nlargest(5, "ratio")]).iterrows():
        lines.append(f"| {r['name']} | {r['bezirk'] or '–'} | {_fmt(r['count_weekday'])} | {_fmt(r['cyc_calibrated'])} | "
                     f"{r['ratio']:.2f} | {r['n_edges']} | {_links(r.geometry, viewers)} |")
    lines += ["", "## Vergleich mit DB Rad+ (nur Plausibilität)", ""]
    if db is None:
        lines.append("- DB Rad+ liegt nicht vor (data/raw/bike_volumes_dbradplus__jahr2025.parquet fehlt).")
    else:
        lines += [f"- {_fmt(db['n_lines'])} Linien 2025 (App-Stichprobe, nicht repräsentativ; drei Datensätze vom Server nicht lieferbar, "
                  "siehe data/manifest.json skipped_records). Linienmitte an die nächste Kante ≤ "
                  f"{params.dbradplus_snap_m:.0f} m: {_fmt(db['n_matched_lines'])} Linien auf {_fmt(db['n_edges'])} Kanten (Maximum je Kante).",
                  f"- Spearman ρ (Modell kalibriert vs. DB-Rad+-Fahrten): {db['spearman']:.2f}; Pearson (log): {db['pearson_log']:.2f}.",
                  "- DB Rad+ geht nicht in die Kalibrierung ein."]
    lines += ["", "## Karte", "", f"![Radverkehrsstärke je Kante]({MAP_PATH.name})", "",
              "## demand_confidence (C-DEM-07)", "",
              f"- hoch: ≤ {params.high_radius_m:.0f} m von einem Querschnitt mit Zählwert/Modell in "
              f"[{params.high_ratio_band[0]}, {params.high_ratio_band[1]}]",
              f"- niedrig: ≤ {params.border_m / 1000:.0f} km von der Landesgrenze (Wege über die Grenze fehlen), in ländlichen "
              f"Stadtteilen, unter {params.low_flow_day:.0f} Rad/Tag oder ohne Modellwert (außerhalb der Hauptkomponente)",
              "- sonst mittel", "", "| Konfidenz | Kanten | km |", "| --- | ---: | ---: |"]
    for c in ("hoch", "mittel", "niedrig"):
        m = out["demand_confidence"] == c
        lines.append(f"| {c} | {_fmt(m.sum())} | {_fmt(km[m].sum(), 1)} |")
    top = out[out["kind"] != "ferry"].nlargest(TOP_N, "cyc_calibrated")
    lines += ["", f"## Die {TOP_N} stärksten Kanten (Prüfung durch Ortskundige)", "",
              "| # | edge_id | Bezirk | Name | Art | Rad/Werktag | Spitzenstunde | Konfidenz | Prüfen |",
              "| ---: | --- | --- | --- | --- | ---: | ---: | --- | --- |"]
    for i, (_, r) in enumerate(top.iterrows(), 1):
        lines.append(f"| {i} | `{r['edge_id']}` | {r['bezirk'] or '–'} | {r['label']} | {r['kind']} | {_fmt(r['cyc_calibrated'])} | "
                     f"{_fmt(r['cyc_peak_h'])} | {r['demand_confidence']} | {_links(r.geometry, viewers)} |")
    sample = sample_by_district(out[out["cyc_calibrated"].notna()], SAMPLE_SIZE, SAMPLE_SEED, id_col="edge_id")
    lines += ["", f"## {len(sample)} Zufallsstichproben (Seed {SAMPLE_SEED})", "",
              "| edge_id | Bezirk | Name | Art | Rad/Werktag | hin/zurück | Konfidenz | Prüfen |",
              "| --- | --- | --- | --- | ---: | --- | --- | --- |"]
    for _, r in sample.iterrows():
        lines.append(f"| `{r['edge_id']}` | {r['bezirk'] or '–'} | {r['label']} | {r['kind']} | {_fmt(r['cyc_calibrated'])} | "
                     f"{_fmt(r['cyc_day_fwd'])}/{_fmt(r['cyc_day_bwd'])} | {r['demand_confidence']} | {_links(r.geometry, viewers)} |")
    lines += [
        "", "## Grenzen", "",
        "- Einfaches Modell: ein Zweck, keine Tageszeiten, keine Verkehrsmittelwahl; Quellen nur Einwohner, Ziele über Proxys. "
        "Parameter (β, Gewichte, Widerstandsfaktoren) sind Setzungen und nicht geschätzt.",
        "- Wege über die Landesgrenze und Freizeitverkehr fehlen; deshalb Konfidenz niedrig am Rand.",
        "- Routenwahl nur über den wahrgenommenen Widerstand im Ist-Zustand; Abbiegewiderstände fehlen, Wartezeiten sind pauschal.",
        "- Getrennt erfasste Radwege tragen den Fluss neben der Fahrbahnkante; je Straßenabschnitt sind Fahrbahn und Seitenwege "
        "(sidepath_of) zusammen zu lesen.",
        "- Zählstellen messen nur an 100 Querschnitten, vor allem an Hauptstraßen; Werte in Nebenstraßen sind kaum geprüft.",
        "- DB Rad+ ist eine App-Stichprobe und nicht repräsentativ.",
        "", "## Quellen und Lizenzen", "",
        "- © OpenStreetMap-Beitragende (ODbL): Radgraph, Geschäfte, Schulen, Hochschulen; abgeleitete Daten unter ODbL.",
        "- Zensus 2022 Gitter 100 m © Statistische Ämter des Bundes und der Länder (dl-de/by-2.0).",
        "- ALKIS © Freie und Hansestadt Hamburg, LGV (dl-de/by-2.0); HVV-GTFS © Hamburger Verkehrsverbund GmbH (dl-de/by-2.0).",
        "- Rad-Zählstellen © Freie und Hansestadt Hamburg (dl-de/by-2.0); DB Rad+ (ODbL).",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# --- main -------------------------------------------------------------------------------------------


def main() -> int:
    cyc_rules = load_cycling_rules()
    params = cd.DemandParams.from_rules(cyc_rules)
    if not GRAPH_PATH.exists():
        print("cycle-demand: data/interim/cycle_graph.parquet missing; run c01_cycle_graph first", file=sys.stderr)
        return 1
    for f in ("bike_counters__stations.parquet", "bike_counters__daily_2025.parquet"):
        if not (RAW / f).exists():
            print(f"cycle-demand: counter data {f} missing; stopping (prompts/15: abbrechen und berichten)", file=sys.stderr)
            return 1
    manifest = load_manifest()
    pbf = REPO_ROOT / _pbf_from_manifest(manifest)["path"]
    edges = gpd.read_parquet(GRAPH_PATH)
    districts = read_districts()
    hamburg = districts.union_all()

    t0 = time.perf_counter()
    layers = destination_points(params, manifest, pbf, hamburg)
    pts = zone_points(params, hamburg, layers)
    z = build_zones(params, pts)
    z["node"], z["snap_m"] = snap_zones(z, edges)
    t_inputs = time.perf_counter() - t0
    print(f"cycle-demand: {len(z)} zones ({t_inputs:.0f} s for inputs)")

    fwd, bwd, stats = run_model(params, edges, z)
    model_day = fwd + bwd
    cs = cross_sections(params, edges, model_day, districts)
    k = cd.calibration_factor(cs["count_weekday"].to_numpy(), cs["model"].fillna(0).to_numpy())
    cs["cyc_calibrated"] = cs["model"] * k
    fit = cd.fit_stats(cs["count_weekday"].to_numpy(), cs["cyc_calibrated"].fillna(0).to_numpy())
    print(f"cycle-demand: k = {k:.3f}, Spearman {fit['spearman']:.2f}, MRD {fit['mrd']:.0%} at {fit['n']} cross-sections")

    out = edges.copy()
    out["cyc_day_model"] = model_day
    out["cyc_calibrated"] = model_day * k
    out["cyc_day_fwd"], out["cyc_day_bwd"] = fwd * k, bwd * k
    out["cyc_peak_h"] = cd.peak_hour(out["cyc_calibrated"].to_numpy(), params.peak_hour_share)
    out["cyc_peak_h_fwd"] = cd.peak_hour(out["cyc_day_fwd"].to_numpy(), params.peak_hour_share)
    out["cyc_peak_h_bwd"] = cd.peak_hour(out["cyc_day_bwd"].to_numpy(), params.peak_hour_share)

    lo, hi = params.high_ratio_band
    ratio = cs["count_weekday"] / cs["cyc_calibrated"]
    good = cs[(cs["cyc_calibrated"] > 0) & (ratio >= lo) & (ratio <= hi)]
    near_good = np.zeros(len(out), dtype=bool)
    if len(good):
        hit = out.sindex.query(good.geometry.buffer(params.high_radius_m).union_all(), predicate="intersects")
        near_good[hit] = True
    near_border = shapely.dwithin(out.geometry.values, hamburg.boundary, params.border_m)
    rural_poly = gpd.read_parquet(RURAL_PATH).union_all()
    rural = shapely.within(shapely.line_interpolate_point(out.geometry.values, 0.5, normalized=True), rural_poly)
    out["demand_confidence"] = cd.confidence(near_good, near_border, rural, out["cyc_calibrated"].to_numpy(), params.low_flow_day)
    reasons = [
        json.dumps({"rules": ["C-DEM-04", "C-DEM-05", "C-DEM-06", "C-DEM-07"], "k": round(k, 4), "method": params.method,
                    "runs": len(stats["runs"]), "near_good_counter": bool(g), "near_border": bool(b), "rural": bool(r)})
        for g, b, r in zip(near_good, near_border, rural)]
    out["demand_trace"] = reasons

    db = dbradplus_compare(params, out, out["cyc_calibrated"].to_numpy())
    out["dbradplus_anzahl"] = np.nan
    if db is not None:
        out.loc[out.index[db["per_edge"].index.to_numpy()], "dbradplus_anzahl"] = db["per_edge"].to_numpy()

    out.to_parquet(OUT_PATH, index=False)
    scatter_png(cs)
    map_png(out, out["cyc_calibrated"].to_numpy(), cs, districts)
    write_report(out, cs, z, layers, stats, fit, k, db, params, {"version": cyc_rules.meta.version})
    print(f"cycle-demand: {len(out)} edges -> {OUT_PATH.relative_to(REPO_ROOT)}, report {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
