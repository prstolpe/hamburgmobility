"""Cycle stage 3: target cycle network – hierarchy and gap closing (prompts/16_cycle_network.md).

Usage: uv run python -m pipeline.c03_cycle_network

Corridors between the Innenstadt, rapid-transit interchanges, universities and job clusters on the Soll
resistance with bonuses for demand and the official cycle network (C-NET-01..05); RSV on corridor runs with
high demand (C-NET-06); HAUPT and BASIS by splitting meshes that are too large (C-NET-07/08); binding of
schools and local shops (C-NET-09); parallel rule P-ATT-03 (C-NET-10); continuity (C-NET-11); ERSCHL for the
rest (C-NET-12); overrides/cycle_network_overrides.csv. Writes data/interim/cycle_network.parquet,
data/interim/cycle_routes.parquet, data/interim/cycle_mesh_gaps.parquet and reports/cycle_network.md.
"""

import datetime as dt
import json
import sys
import time
import warnings
from dataclasses import dataclass

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from scipy.sparse.csgraph import connected_components

from pipeline.lib import cycle_demand as cd
from pipeline.lib import cycle_network as cn
from pipeline.lib import gtfs
from pipeline.lib import overrides as ov
from pipeline.lib.area import NO_DISTRICT, read_districts, read_rural, sample_by_district
from pipeline.lib.crs import WORK_CRS, to_work_crs
from pipeline.lib.links import load_viewers, orthophoto_link, osm_map_link, panoramax_link
from pipeline.lib.manifest import REPO_ROOT, load_manifest
from pipeline.lib.report import district_breakdown
from pipeline.lib.rules import load_cycling_rules
from pipeline.s02_network import _pbf_from_manifest

RAW = REPO_ROOT / "data" / "raw"
INTERIM = REPO_ROOT / "data" / "interim"
EDGES_PATH = INTERIM / "cycle_edges.parquet"
FINAL_PATH = INTERIM / "final.parquet"
OFFICIAL_PATH = RAW / "cycle_network_official__radnetz.parquet"
OUT_PATH = INTERIM / "cycle_network.parquet"
ROUTES_PATH = INTERIM / "cycle_routes.parquet"
GAPS_PATH = INTERIM / "cycle_mesh_gaps.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "cycle_network.md"
MAP_HAUPT = REPO_ROOT / "reports" / "cycle_network_haupt.png"
MAP_BASIS = REPO_ROOT / "reports" / "cycle_network_basis.png"
MAP_COMPARE = REPO_ROOT / "reports" / "cycle_network_compare.png"
GRID_CRS = "EPSG:3035"  # Zensus grid of the demand zones (C-DEM-01)
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
TOP_N = 15
TRACE_ROUTES = 3  # route ids listed per edge in rule_trace_cycle (all ids are in route_ids)
H, B, R, E = cn.RANK["HAUPT"], cn.RANK["BASIS"], cn.RANK["RSV"], cn.RANK["ERSCHL"]
KIND_RULE = {"corridor": "C-NET-02", "mesh_haupt": "C-NET-08", "mesh_basis": "C-NET-08", "attach": "C-NET-09"}
KIND_DE = {"corridor": "Korridor", "mesh_haupt": "Verdichtung HAUPT", "mesh_basis": "Verdichtung BASIS",
           "attach": "Anbindung Schule/Nahversorgung"}


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _fmt(v: float, digits: int = 0) -> str:
    return f"{v:,.{digits}f}".replace(",", " ")


@dataclass
class Route:
    kind: str
    edges: list
    ranks: np.ndarray       # own category rank per edge along the route
    label: str = ""
    route_id: str = ""


# --- inputs -------------------------------------------------------------------------------------------


def _gtfs_path(manifest: dict):
    files = (manifest["sources"].get("gtfs_hvv") or {}).get("files") or []
    paths = [REPO_ROOT / f["path"] for f in files if (REPO_ROOT / f["path"]).exists()]
    if not paths:
        raise FileNotFoundError("GTFS feed missing; run `make fetch`")
    return paths[0]


def _tags(row) -> dict:
    t = row.get("tags")
    if isinstance(t, str):
        try:
            return json.loads(t)
        except ValueError:
            return {}
    return t if isinstance(t, dict) else {}


def read_barriers(pbf, p: cn.NetworkParams, area) -> np.ndarray:
    """C-NET-07 barrier lines (railway, waterway) from OSM, without tunnels, simplified, inside the area."""
    from pyrosm import OSM

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        g = OSM(str(pbf)).get_data_by_custom_criteria(
            custom_filter={k: list(v) for k, v in p.barrier_lines.items()}, osm_keys_to_keep=list(p.barrier_lines),
            filter_type="keep", keep_nodes=False, keep_ways=True, keep_relations=False)
    g = to_work_crs(g)
    if p.barrier_exclude_tunnel:
        tunnel = g.apply(lambda r: str(r.get("tunnel") or _tags(r).get("tunnel") or "no") not in ("no", "None", "nan"), axis=1)
        g = g[~tunnel]
    lines = shapely.get_parts(shapely.boundary(g.geometry.values[g.geom_type.isin(["Polygon", "MultiPolygon"])]))
    lines = np.concatenate([g.geometry.values[g.geom_type.isin(["LineString", "MultiLineString"])], lines])
    lines = shapely.simplify(shapely.get_parts(lines), p.simplify_m)
    return lines[shapely.intersects(lines, area)]


def read_exclude_areas(pbf, p: cn.NetworkParams, area) -> np.ndarray:
    """C-NET-07 areas without cycle demand (water, forest, parks, airport) of at least exclude_area_min_m2."""
    from pyrosm import OSM

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        g = OSM(str(pbf)).get_data_by_custom_criteria(
            custom_filter={k: list(v) for k, v in p.exclude_areas.items()}, osm_keys_to_keep=list(p.exclude_areas),
            filter_type="keep", keep_nodes=False, keep_ways=True, keep_relations=True)
    g = to_work_crs(g)
    g = g[g.geom_type.isin(["Polygon", "MultiPolygon"])]
    polys = shapely.make_valid(shapely.simplify(g.geometry.values, p.simplify_m))
    polys = polys[shapely.area(polys) >= p.exclude_area_min_m2]
    return polys[shapely.intersects(polys, area)]


def read_shops(pbf, kinds: tuple) -> gpd.GeoDataFrame:
    from pyrosm import OSM

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pois = OSM(str(pbf)).get_pois(custom_filter={"shop": list(kinds)})
    pois = to_work_crs(pois[pois["shop"].isin(kinds)].reset_index(drop=True))
    return gpd.GeoDataFrame({"shop": pois["shop"].to_numpy()}, geometry=pois.geometry.representative_point().to_numpy(), crs=WORK_CRS)


def corridor_points(p: cn.NetworkParams, dp: cd.DemandParams, manifest: dict, hamburg, districts) -> gpd.GeoDataFrame:
    """C-NET-01: Innenstadt, interchanges, universities and job clusters in priority order, merged within merge_m."""
    rows = []
    centre = gpd.GeoSeries(gpd.points_from_xy([p.innenstadt_lonlat[0]], [p.innenstadt_lonlat[1]]), crs="EPSG:4326").to_crs(WORK_CRS)
    rows.append({"kind": "innenstadt", "label": f"Innenstadt ({p.innenstadt_label})", "weight": np.inf, "geometry": centre.iloc[0]})

    st = gtfs.rapid_transit_stations(_gtfs_path(manifest), dp.rapid_transit_route_types)
    st = st[st.within(hamburg)].reset_index(drop=True)
    hub = cn.hubs(np.c_[st.geometry.x, st.geometry.y], [set(t) for t in st["route_types"]], p.hub_radius_m, p.hub_min_modes)
    for _, r in st[hub].sort_values(["n_route_types", "name"], ascending=[False, True]).iterrows():
        rows.append({"kind": "hub", "label": f"Umsteigeknoten {r['name']}", "weight": float(r["n_route_types"]), "geometry": r.geometry})

    uni = gpd.read_parquet(RAW / "universities__osm.parquet")
    uni = uni[uni["amenity"].isin(p.university_amenity)]
    uni = uni.assign(geometry=uni.geometry.representative_point())
    uni = uni[uni.within(hamburg)].sort_values("name", na_position="last")
    for _, r in uni.iterrows():
        rows.append({"kind": "university", "label": f"Hochschule {r['name'] or 'ohne Namen'}", "weight": 1.0, "geometry": r.geometry})

    b = gpd.read_parquet(RAW / "alkis__GebaeudeBauwerk.parquet", columns=["gebnutzbez", "funktion", "anzahlgs", "rellage", "geometry"])
    area = cd.jobs_floor_area(b, dp).to_numpy()
    pts = gpd.GeoSeries(b.geometry.representative_point().to_numpy(), crs=WORK_CRS)
    ok = (area > 0) & pts.within(hamburg).to_numpy()
    g3035 = pts[ok].to_crs(GRID_CRS)
    ix, iy = cd.zone_index(g3035.x.to_numpy(), g3035.y.to_numpy(), dp.zone_m)
    z = pd.DataFrame({"zone": [f"{a}_{c}" for a, c in zip(ix, iy)], "a": area[ok],
                      "x": pts[ok].x.to_numpy(), "y": pts[ok].y.to_numpy()})
    z["ax"], z["ay"] = z["a"] * z["x"], z["a"] * z["y"]
    zs = z.groupby("zone")[["a", "ax", "ay"]].sum()
    thr = zs["a"].quantile(p.job_cluster_quantile)
    jobs = zs[zs["a"] >= thr].sort_values("a", ascending=False)
    jp = gpd.GeoDataFrame(jobs, geometry=gpd.points_from_xy(jobs["ax"] / jobs["a"], jobs["ay"] / jobs["a"]), crs=WORK_CRS)
    j = gpd.sjoin(jp, districts[["name", "geometry"]], how="left", predicate="within")
    jp["bezirk"] = j[~j.index.duplicated()]["name"].reindex(jp.index)
    for _, r in jp.iterrows():
        rows.append({"kind": "jobs", "label": f"Arbeitsplatzschwerpunkt {r['bezirk'] or ''} ({_fmt(r['a'] / 1000)} Tsd. m²)".replace("  ", " "),
                     "weight": float(r["a"]), "geometry": r.geometry})
    pts = gpd.GeoDataFrame(rows, geometry="geometry", crs=WORK_CRS)
    keep = cn.merge_points(np.c_[pts.geometry.x, pts.geometry.y], p.merge_m)
    pts["kept"] = keep
    pts.attrs["job_threshold_m2"] = float(thr)
    return pts


# --- design steps -------------------------------------------------------------------------------------


def edge_ranks(routes: list[Route], n: int) -> np.ndarray:
    r = np.full(n, E)
    for rt in routes:
        np.maximum.at(r, np.asarray(rt.edges, dtype="int64"), rt.ranks)
    return r


def parallel_rule(routes: list[Route], inp: cn.DesignInputs, high: np.ndarray, p: cn.NetworkParams,
                  names: pd.Series) -> tuple[np.ndarray, list[dict]]:
    """C-NET-10 on every route with HAUPT/RSV edges; changes the routes in place. Returns the mask of main-street
    edges taken out of a route and one record per examined run."""
    main = np.zeros(len(high), dtype=bool)
    records = []
    cache: dict[tuple, cn.Alternative] = {}
    for rt in routes:
        e = np.asarray(rt.edges, dtype="int64")
        if rt.ranks.max() < H:
            continue
        nodes = cn.route_nodes(rt.edges, inp.node_u, inp.node_v)
        ok = cn.chain_ok(rt.edges, inp.node_u, inp.node_v, nodes)
        runs = cn.high_volume_runs(high[e] & ok, inp.length[e], p.patt_min_run_m)
        if not runs:
            continue
        new_e, new_r, last = [], [], 0
        for s, t in runs:
            cat = int(rt.ranks[s:t].max())
            thr = p.detour_max["RSV" if cat == R else "HAUPT"]
            key = (tuple(e[s:t].tolist()), nodes[s], nodes[t], thr)
            if key not in cache:
                cache[key] = cn.parallel_alternative(inp, e[s:t].tolist(), nodes[s], nodes[t], high, p.patt_parallel_max_m,
                                                     thr, p.patt_max_on_main_m)
            alt = cache[key]
            run_names = [n for n in dict.fromkeys(names.iloc[e[s:t]]) if n and n != "–"]
            alt_names = [n for n in dict.fromkeys(names.iloc[alt.edges]) if n and n != "–"] if alt.edges else []
            records.append({"route": rt, "edges": e[s:t].tolist(), "alt_edges": alt.edges, "accepted": alt.accepted,
                            "detour": alt.detour, "run_m": alt.run_m, "alt_m": alt.alt_m, "on_main_m": alt.on_main_m,
                            "category": cn.CATEGORY_ORDER[cat],
                            "threshold": thr, "street": ", ".join(run_names[:3]) or "–", "alt_street": ", ".join(alt_names[:3]) or "–"})
            if alt.accepted:
                new_e += e[last:s].tolist() + alt.edges
                new_r += rt.ranks[last:s].tolist() + [cat] * len(alt.edges)
                main[e[s:t]] = True
                last = t
        if last:
            new_e += e[last:].tolist()
            new_r += rt.ranks[last:].tolist()
            rt.edges, rt.ranks = new_e, np.asarray(new_r)
    return main, records


def components(inp: cn.DesignInputs, mask: np.ndarray) -> tuple[int, float]:
    """Number of connected components of the edges in mask and the length share of the largest one."""
    pos = np.flatnonzero(mask)
    if len(pos) == 0:
        return 0, float("nan")
    g = cn.Graph(inp.node_u[pos], inp.node_v[pos], np.ones(len(pos)), pos)
    n, lab = connected_components(g.matrix, directed=False)
    node_lab = lab[g.index(inp.node_u[pos])]
    km = pd.Series(inp.length[pos]).groupby(node_lab).sum()
    return int(n), float(km.max() / km.sum())


# --- figures -------------------------------------------------------------------------------------------


def _segs(geoms) -> list:
    return [np.asarray(c)[:, :2] for g in geoms for c in ([g.coords] if g.geom_type == "LineString" else [x.coords for x in g.geoms])]


def _map(path, layers: list[tuple], districts, title: str, points: gpd.GeoDataFrame | None = None) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection

    fig, ax = plt.subplots(figsize=(12, 10), dpi=100)
    districts.boundary.plot(ax=ax, color="#bbb", lw=0.6)
    for geoms, color, lw, label, ls in layers:
        if len(geoms):
            ax.add_collection(LineCollection(_segs(geoms), colors=color, linewidths=lw, label=label, linestyles=ls))
    if points is not None and len(points):
        ax.scatter(points.geometry.x, points.geometry.y, s=14, color="#222", zorder=5, label="Korridorpunkt")
    ax.set_aspect("equal")
    ax.autoscale()
    ax.set_axis_off()
    ax.legend(loc="lower left")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


# --- report ----------------------------------------------------------------------------------------------


def _links(geom, viewers) -> str:
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        p = geom.representative_point()
    else:
        p = geom.interpolate(0.5, normalized=True) if geom.geom_type != "Point" else geom
    pw = gpd.GeoSeries([p], crs=WORK_CRS).to_crs("EPSG:4326").iloc[0]
    return f"[Luftbild]({orthophoto_link(p, viewers)}) · [Panoramax]({panoramax_link(pw, viewers)}) · [OSM]({osm_map_link(pw)})"


def _labels(out: gpd.GeoDataFrame, final_names: pd.Series) -> pd.Series:
    side = out["sidepath_of"].map(final_names)
    label = out["name"].where(out["name"].notna() & (out["name"] != ""), None)
    label = label.where(label.notna(), ("neben " + side).where(side.notna(), None))
    return label.fillna("–")


def write_report(ctx: dict) -> None:
    out, p, viewers = ctx["out"], ctx["p"], load_viewers()
    km = out["length_m"] / 1000
    cat = out["cycle_cat_final"]
    lines = [
        "# Soll-Radnetz: Hierarchie und Lückenschluss (Stufe c03)",
        "",
        f"Erzeugt {_now()} mit pipeline/c03_cycle_network.py · cycling_rules.yaml {ctx['version']} · nicht amtlicher Entwurf. "
        "Alle Entwurfsparameter (C-NET-01…13) sind Annahmen (source_type assumption, status draft) und vor fachlicher Nutzung zu prüfen.",
        "",
        "## Kurzfassung",
        "",
    ]
    for c in reversed(cn.CATEGORY_ORDER):
        lines.append(f"- {c}: {_fmt(km[cat == c].sum(), 0)} km ({_fmt((cat == c).sum())} Kanten)")
    cmp_ = ctx["compare"]
    lines += [
        f"- Amtliches Radnetz (Bestand, {_fmt(cmp_['official_km'], 0)} km): {cmp_['official_covered_share']:.0%} liegt am Soll-Netz "
        f"RSV/HAUPT, {cmp_['official_covered_any_share']:.0%} am Soll-Netz bis BASIS (Puffer {p.compare_buffer_m:.0f} m).",
        f"- Soll RSV/HAUPT außerhalb des amtlichen Bestands: {_fmt(cmp_['additional_km'], 0)} km, davon "
        f"{_fmt(cmp_['additional_in_planned_km'], 0)} km im geplanten amtlichen Netz.",
        f"- Maschen über der Höchstweite nach Verdichtung: HAUPT {len(ctx['gaps_haupt'])}, BASIS {len(ctx['gaps_basis'])} "
        "(Lückenliste unten; Maschen in ländlichen Stadtteilen nicht geprüft).",
        f"- Parallelregel P-ATT-03: {sum(r['accepted'] for r in ctx['patt'])} von {len(ctx['patt'])} geprüften Läufen an Straßen "
        f"mit DTV > {_fmt(p.patt_dtv)} auf eine Parallelroute verlegt.",
        f"- Overrides angewendet: {int((out['cycle_cat_source'] == 'override').sum())}.",
        "",
        "**Grenzen vorab:** Bezirks- und Stadtteilzentren fehlen als Korridorpunkte (kein Endpunkt für das Zentrenkonzept, "
        "Entscheidung 2026-11-06). Die Nachfrage aus Prompt 15 ist nur mäßig kalibriert (Spearman 0,53, mittlere relative "
        "Abweichung 154 %; Nebenstraßen parallel zu Hauptstraßen ohne erfassten Radweg werden überschätzt). Beides wirkt auf "
        "Korridore und RSV-Abschnitte; bitte die RSV-Liste und die Karten mit Ortskenntnis lesen.",
        "",
        "## Verfahren",
        "",
        "1. **Soll-Widerstand (C-NET-03):** Länge × Faktor der regelkonformen Führung je cat_final "
        f"({', '.join(f'{k} {v}' for k, v in p.soll_factor_keys.items())}) plus Wartezeiten des Ist-Zustands; ungerichtet.",
        f"2. **Boni:** Nachfrage (C-NET-04) bis −{p.max_reduction:.0%} ab {_fmt(p.rsv_trigger)} Rad/Werktag; amtliches Radnetz "
        f"(C-NET-05, alle Status) × {p.official_multiplier} bei ≥ {p.min_overlap:.0%} Überdeckung im Puffer {p.match_buffer_m:.0f} m.",
        f"3. **Korridore (C-NET-01/02):** Punkte zusammengefasst ab {p.merge_m:.0f} m; jeder Punkt mit seinen {p.k_nearest} nächsten "
        f"(bis {p.max_pair_m / 1000:.0f} km) und mit der Innenstadt verbunden, günstigster Weg nach Soll-Widerstand mit Boni.",
        f"4. **RSV (C-NET-06):** Korridorläufe mit ≥ {_fmt(p.rsv_trigger)} Rad/Werktag (Lücken bis {p.rsv_gap_max_m:.0f} m überbrückt) "
        f"und ≥ {p.rsv_min_length_m / 1000:.0f} km Länge; übrige Korridorkanten HAUPT.",
        f"5. **HAUPT-Verdichtung (C-NET-07/08):** Maschen des RSV+HAUPT-Netzes mit Barrieren (Bahn, Flüsse/Kanäle) und Landesgrenze; "
        f"Seite des flächengleichen Quadrats ohne Wasser, Wald, Parks, Friedhöfe, Flughafen (≥ {_fmt(p.exclude_area_min_m2 / 1e4)} ha); "
        f"Maschen > {p.mesh_max_m['HAUPT']:.0f} m werden geteilt, ab der Kante mit der höchsten Nachfrage im Kernbereich "
        f"(Abstand zum Maschenrand ≥ {p.seed_core_share} × größter Abstand).",
        f"6. **Parallelregel (C-NET-10, P-ATT-03):** Läufe ≥ {p.patt_min_run_m:.0f} m an Straßen mit DTV > {_fmt(p.patt_dtv)}; "
        f"Alternative über Kanten im Puffer {p.patt_parallel_max_m:.0f} m, höchstens {p.patt_max_on_main_m:.0f} m an der Hauptstraße "
        f"(Anschluss/Querung), Umwegfaktor ≤ P-DIR-01 (RSV {p.detour_max['RSV']}, HAUPT {p.detour_max['HAUPT']}); "
        "die Hauptstraße bleibt BASIS. Danach zweite HAUPT-Verdichtung ohne diese Hauptstraßen.",
        f"7. **BASIS (C-NET-09/08):** Schulen und Nahversorgung ({', '.join(p.nahversorgung_shops)}) weiter als "
        f"{p.binding_radius_m:.0f} m vom Netz angebunden; dann Maschen > {p.mesh_max_m['BASIS']:.0f} m geteilt.",
        f"8. **Kontinuität (C-NET-11):** niedrigere Läufe bis {p.continuity_max_gap_m:.0f} m zwischen zwei gleichen höheren Läufen angehoben.",
        "9. **ERSCHL (C-NET-12):** alle übrigen Kanten. **Overrides:** overrides/cycle_network_overrides.csv, nur approved.",
        "",
        "## Korridorpunkte (C-NET-01)",
        "",
        "| Art | Punkte | nach Zusammenfassung | Quelle |",
        "| --- | ---: | ---: | --- |",
    ]
    pts = ctx["points"]
    src = {"innenstadt": f"Annahme ({p.innenstadt_label}, {p.innenstadt_lonlat[1]}/{p.innenstadt_lonlat[0]})",
           "hub": f"HVV-GTFS, ≥ {p.hub_min_modes} Verkehrsmittel im Umkreis {p.hub_radius_m:.0f} m",
           "university": f"OSM amenity={'|'.join(p.university_amenity)} (Fallback)",
           "jobs": f"ALKIS-Geschossfläche Nichtwohnen, Zonen ≥ Quantil {p.job_cluster_quantile} ({_fmt(pts.attrs['job_threshold_m2'] / 1000)} Tsd. m²)"}
    de = {"innenstadt": "Innenstadt", "hub": "Schnellbahn-Umsteigeknoten", "university": "Hochschule", "jobs": "Arbeitsplatzschwerpunkt"}
    for k in ("innenstadt", "hub", "university", "jobs"):
        g = pts[pts["kind"] == k]
        lines.append(f"| {de[k]} | {len(g)} | {int(g['kept'].sum())} | {src[k]} |")
    lines += ["| Bezirks-/Stadtteilzentren | – | – | fehlt: sources.yaml `centres` ohne Endpunkt (TODO) |", "",
              f"Korridorpaare: {ctx['n_pairs']}, davon mit Weg: {ctx['n_corridors']}. Anbindung an den Radgraphen: Median "
              f"{ctx['snap'].median():.0f} m, Maximum {ctx['snap'].max():.0f} m.", "",
              "## Kennzahlen je Kategorie", "",
              "| Kategorie | km | Kanten | davon Bestand amtlich km | Komponenten | größte Komponente (Längenanteil) |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for c in reversed(cn.CATEGORY_ORDER):
        m = cat == c
        comp = ctx["components"].get(c, (None, None))
        comp_txt = f"{comp[0]} | {comp[1]:.0%}" if comp[0] is not None else "– | –"
        lines.append(f"| {c} | {_fmt(km[m].sum(), 1)} | {_fmt(m.sum())} | {_fmt(km[m & (out['official_network'] == 'official')].sum(), 1)} | {comp_txt} |")
    lines += ["", "Komponenten (P-COH-02): je Ebene einschließlich der höheren Ebenen.", "",
              "Anteile je Bezirk (Kantenlänge):", ""]
    lines += district_breakdown(out, "cycle_cat_final", list(reversed(cn.CATEGORY_ORDER)))
    lines += ["", "### Maschenweite (P-COH-01)", "",
              "| Ebene | Höchstweite m | Maschen geprüft | Median Seite m | 90-%-Quantil m | größte m | über Höchstweite | in ländl. Stadtteilen nicht geprüft |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for lvl in ("HAUPT", "BASIS"):
        s = ctx["mesh_stats"][lvl]
        lines.append(f"| {lvl} + höher | {p.mesh_max_m[lvl]:.0f} | {_fmt(s['n'])} | {_fmt(s['median'])} | {_fmt(s['p90'])} | {_fmt(s['max'])} | "
                     f"{s['over']} | {s['skipped']} |")
    lines += ["", "Verdichtungsrunden:", "", "| Ebene | Runde | Maschen zu groß | neue Routen |", "| --- | ---: | ---: | ---: |"]
    for lvl, rounds in ctx["rounds"].items():
        for r in rounds:
            lines.append(f"| {lvl} | {r['round']} | {r['faces_over']} | {r['routes_added']} |")
    cov = ctx["coverage"]
    lines += ["", f"### Abdeckung wichtiger Ziele (P-COH-03, ≤ {p.coverage_m:.0f} m vom RSV/HAUPT-Netz)", "",
              "| Ziel | Anzahl | abgedeckt |", "| --- | ---: | ---: |"]
    for k, (n, share) in cov.items():
        lines.append(f"| {k} | {_fmt(n)} | {share:.0%} |")
    lines += ["| Zentren | – | nicht prüfbar (Datensatz fehlt) |", "",
              "## Karten", "",
              f"![RSV und HAUPT]({MAP_HAUPT.name})", "", f"![BASIS]({MAP_BASIS.name})", "",
              f"![Soll vs. amtliches Radnetz]({MAP_COMPARE.name})", "",
              "## Vergleich mit dem amtlichen Radnetz", "",
              f"Amtlich = WFS Radnetz Hamburg, Status {', '.join(p.official_status)}; geplant = {', '.join(p.planned_status)} "
              f"(Entscheidung 2026-11-06). Überdeckung im Puffer {p.compare_buffer_m:.0f} m.", "",
              "| Kennzahl | km |", "| --- | ---: |",
              f"| amtlich (Bestand) | {_fmt(cmp_['official_km'], 1)} |",
              f"| davon am Soll RSV/HAUPT | {_fmt(cmp_['official_covered_km'], 1)} |",
              f"| davon am Soll bis BASIS | {_fmt(cmp_['official_covered_any_km'], 1)} |",
              f"| fehlt im Soll RSV/HAUPT | {_fmt(cmp_['official_km'] - cmp_['official_covered_km'], 1)} |",
              f"| geplant (amtlich) | {_fmt(cmp_['planned_km'], 1)} |",
              f"| davon am Soll RSV/HAUPT | {_fmt(cmp_['planned_covered_km'], 1)} |",
              f"| Soll RSV/HAUPT gesamt | {_fmt(cmp_['soll_km'], 1)} |",
              f"| Soll RSV/HAUPT zusätzlich (nicht am amtlichen Bestand) | {_fmt(cmp_['additional_km'], 1)} |",
              f"| davon im geplanten amtlichen Netz | {_fmt(cmp_['additional_in_planned_km'], 1)} |",
              "", f"Längste amtliche Bestandsabschnitte ohne Soll RSV/HAUPT (Top {TOP_N}):", "",
              "| Länge m | Soll dort (größte Kategorie) | Prüfen |", "| ---: | --- | --- |"]
    for _, r in cmp_["missing"].iterrows():
        lines.append(f"| {_fmt(r['missing_m'])} | {r['soll_here']} | {_links(r.geometry, viewers)} |")
    lines += ["", f"Zusätzliche Soll-RSV/HAUPT-Straßen ohne amtlichen Bestand (Top {TOP_N} nach Länge):", "",
              "| Straße / Weg | km | Kategorie | im geplanten Netz km | Prüfen |", "| --- | ---: | --- | ---: | --- |"]
    for _, r in cmp_["additional"].iterrows():
        lines.append(f"| {r['label']} | {r['km']:.2f} | {r['cat']} | {r['planned_km']:.2f} | {_links(r.geometry, viewers)} |")

    rsv = ctx["routes"][ctx["routes"]["n_rsv_edges"] > 0]
    lines += ["", "## RSV-Abschnitte (C-NET-06)", "",
              f"{len(rsv)} Korridore mit RSV-Läufen. Längste Korridore mit RSV-Anteil:", "",
              "| route_id | Korridor | km | RSV km | Median Rad/Werktag | Prüfen |", "| --- | --- | ---: | ---: | ---: | --- |"]
    for _, r in rsv.sort_values("rsv_km", ascending=False).head(TOP_N).iterrows():
        lines.append(f"| `{r['route_id']}` | {r['label']} | {r['length_m'] / 1000:.1f} | {r['rsv_km']:.1f} | {_fmt(r['cyc_median'])} | {_links(r.geometry, viewers)} |")

    runs = {}
    for r in ctx["patt"]:
        k = (tuple(r["edges"]), r["threshold"])
        runs.setdefault(k, {**r, "routes": []})["routes"].append(r["route"].route_id)
    runs = list(runs.values())

    def result(r) -> str:
        if r["accepted"]:
            return "verlegt"
        if not r["alt_edges"]:
            return "keine Alternative im Puffer"
        if r["on_main_m"] > p.patt_max_on_main_m:
            return "nur über die Hauptstraße"
        return "Umweg zu groß"

    counts = pd.Series([result(r) for r in runs]).value_counts()
    lines += ["", "## Parallelregel P-ATT-03 (C-NET-10)", "",
              f"{len(runs)} verschiedene Läufe an Straßen mit DTV > {_fmt(p.patt_dtv)} (auf {len(ctx['patt'])} Routen geprüft): "
              + ", ".join(f"{k} {v}" for k, v in counts.items()) + ".", "",
              "| Routen | Straße (DTV > Schwelle) | Kategorie | Lauf m | Alternative | Alternative m | davon Hauptstraße m | Umwegfaktor | Schwelle | Ergebnis | Prüfen |",
              "| ---: | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- | --- |"]
    ordered = sorted(runs, key=lambda x: (not x["accepted"], -x["run_m"]))
    for r in ordered[:2 * TOP_N]:
        geom = shapely.union_all(out.geometry.values[r["edges"]])
        det = f"{r['detour']:.2f}" if np.isfinite(r["detour"]) else "–"
        alt_m = _fmt(r["alt_m"]) if np.isfinite(r["alt_m"]) else "–"
        on_main = _fmt(r["on_main_m"]) if np.isfinite(r["on_main_m"]) else "–"
        lines.append(f"| {len(r['routes'])} | {r['street']} | {r['category']} | {_fmt(r['run_m'])} | {r['alt_street']} | {alt_m} | {on_main} | "
                     f"{det} | {r['threshold']} | {result(r)} | {_links(geom, viewers)} |")
    if len(runs) > 2 * TOP_N:
        lines.append(f"\n({len(runs) - 2 * TOP_N} weitere Läufe nicht gelistet; je Route in data/interim/cycle_routes.parquet, Spalte patt_runs.)")

    lines += ["", "## Kontinuität (C-NET-11, P-COH-04)", "",
              f"- {ctx['n_smoothed']} Kanten angehoben (kurze Lücken zwischen gleichen höheren Kategorien).",
              f"- Routen mit Kategoriewechseln entlang des Wegs: {int((ctx['routes']['n_category_changes'] > 0).sum())} von {len(ctx['routes'])}; "
              f"mit Bruch durch Override: {int(ctx['routes']['override_break'].sum())}.",
              "- Kategoriewechsel RSV↔HAUPT an Korridoren sind gewollt (RSV nur auf Läufen mit hoher Nachfrage); sie sind in "
              "data/interim/cycle_routes.parquet je Route gezählt (n_category_changes).", "",
              "| Routenart | Routen | km (Summe Routenlängen) |", "| --- | ---: | ---: |"]
    for k, g in ctx["routes"].groupby("kind"):
        lines.append(f"| {KIND_DE.get(k, k)} | {len(g)} | {_fmt(g['length_m'].sum() / 1000, 0)} |")

    gaps = ctx["gaps"]
    lines += ["", "## Lückenliste (Maschen über der Höchstweite)", "",
              f"{len(gaps)} Maschen, nach Größe; vollständig in data/interim/cycle_mesh_gaps.parquet.", "",
              "| Ebene | Seite m | Höchstweite m | Grund | Bezirk | Prüfen |", "| --- | ---: | ---: | --- | --- | --- |"]
    for _, r in gaps.sort_values("side_m", ascending=False).head(2 * TOP_N).iterrows():
        lines.append(f"| {r['level']} | {_fmt(r['side_m'])} | {r['max_m']:.0f} | {r['reason']} | {r['bezirk'] or '–'} | {_links(r.geometry, viewers)} |")

    sample = sample_by_district(out, SAMPLE_SIZE, SAMPLE_SEED, id_col="edge_id")
    lines += ["", f"## {len(sample)} Zufallsstichproben (Seed {SAMPLE_SEED})", "",
              "| edge_id | Bezirk | Name | Art | Kategorie | Rad/Werktag | amtlich | Route | Prüfen |",
              "| --- | --- | --- | --- | --- | ---: | --- | --- | --- |"]
    off_de = {"official": "Bestand", "planned": "geplant"}
    for _, r in sample.iterrows():
        cyc = _fmt(r["cyc_calibrated"]) if pd.notna(r["cyc_calibrated"]) else "–"
        lines.append(f"| `{r['edge_id']}` | {r['bezirk'] or '–'} | {r['label']} | {r['kind']} | {r['cycle_cat_final']} | {cyc} | "
                     f"{off_de.get(r['official_network'], '–')} | {('`' + r['route_id'] + '`') if isinstance(r['route_id'], str) else '–'} | {_links(r.geometry, viewers)} |")
    lines += [
        "", "## Grenzen", "",
        "- Ohne Bezirks- und Stadtteilzentren fehlen Korridore zwischen Zentren ohne Schnellbahn-Umsteigeknoten, Hochschule oder "
        "großen Arbeitsplatzschwerpunkt. Sobald ein Datensatz zum Zentrenkonzept vorliegt (sources.yaml `centres`), neu rechnen.",
        "- Die Nachfrage ist ein einfaches Modell mit mäßiger Kalibrierung (reports/cycle_demand.md); RSV hängt direkt am Auslöser "
        f"{_fmt(p.rsv_trigger)} Rad/Werktag. Gebündelte Nebenstraßen können zu RSV werden, wo in Wirklichkeit die Hauptstraße genutzt würde.",
        "- Die Maschenregel erzeugt ein dichtes Netz: Bei 600 m bzw. 300 m Maschenweite entstehen rechnerisch rund 2 bzw. 4 km Netz "
        "je km². Die Werte stammen aus der Delfter Netzlogik (DCE) und sind für Hamburg zu prüfen.",
        "- Verdichtung wählt die Kante mit der höchsten Modellnachfrage im Kernbereich der Masche als Start; bei fehlender Nachfrage "
        "entscheidet die Lage zur Maschenmitte. Das Ergebnis ist ein Vorschlag, keine Optimierung.",
        "- Barrieren nur Bahn (ohne Tunnel) und Flüsse/Kanäle aus OSM; Autobahnen sind keine Barriere, weil der Radgraph sie nicht "
        "enthält und Querungen über die Kanten erfasst sind. Ausschlussflächen aus OSM-Landnutzung.",
        "- Der Netzentwurf ist ungerichtet; Einbahnstraßen ohne Radfreigabe in Gegenrichtung zählen in einer Richtung.",
        "- Fähren können Teil eines Korridors sein (z. B. Elbquerung); sie erhalten die Kategorie der Route.",
        "", "## Quellen und Lizenzen", "",
        "- © OpenStreetMap-Beitragende (ODbL): Radgraph, Barrieren, Ausschlussflächen, Hochschulen, Schulen, Geschäfte; abgeleitete Daten unter ODbL.",
        "- Radnetz Hamburg (WFS) © Freie und Hansestadt Hamburg, BVM (dl-de/by-2.0).",
        "- ALKIS © Freie und Hansestadt Hamburg, LGV (dl-de/by-2.0); HVV-GTFS © Hamburger Verkehrsverbund GmbH (dl-de/by-2.0).",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# --- main --------------------------------------------------------------------------------------------------


def main() -> int:
    cyc_rules = load_cycling_rules()
    p = cn.NetworkParams.from_rules(cyc_rules)
    dp = cd.DemandParams.from_rules(cyc_rules)
    for path, step in ((EDGES_PATH, "make cycle-demand"), (FINAL_PATH, "make coherence"), (OFFICIAL_PATH, "make fetch")):
        if not path.exists():
            print(f"cycle-network: {path.relative_to(REPO_ROOT)} missing; run `{step}` first", file=sys.stderr)
            return 1
    t_start = time.perf_counter()
    manifest = load_manifest()
    pbf = REPO_ROOT / _pbf_from_manifest(manifest)["path"]
    edges = gpd.read_parquet(EDGES_PATH)
    final = pd.read_parquet(FINAL_PATH, columns=["segment_id", "cat_final", "dtv_official", "name"]).set_index("segment_id")
    districts = read_districts()
    hamburg = districts.union_all()
    rural = read_rural().union_all()
    official = gpd.read_parquet(OFFICIAL_PATH).to_crs(WORK_CRS)
    n = len(edges)
    geoms = edges.geometry.values
    length = edges["length_m"].to_numpy(dtype="float64")
    kind = edges["kind"].to_numpy()

    # C-NET-03 Soll resistance
    cat_final = edges["segment_id"].map(final["cat_final"])
    soll = [cn.soll_factor_for(k, c, f, p) for k, c, f in zip(kind, cat_final, edges["factor"])]
    edges["cat_final"] = cat_final
    edges["soll_factor"] = [s[0] for s in soll]
    edges["soll_factor_key"] = [s[1] for s in soll]
    sf, sb = cn.soll_costs(length, edges["factor"], edges["cost_fwd"], edges["cost_bwd"], edges["soll_factor"])
    edges["soll_cost_fwd"], edges["soll_cost_bwd"] = sf, sb

    # C-NET-04/05 bonuses
    is_off = official["status"].isin(p.official_status).to_numpy()
    is_plan = official["status"].isin(p.planned_status).to_numpy()
    buf = official.geometry.buffer(p.match_buffer_m).values
    share_all = cn.overlap_share(geoms, buf)
    share_off = cn.overlap_share(geoms, buf[is_off])
    share_plan = cn.overlap_share(geoms, buf[is_plan])
    edges["official_share"] = share_all
    edges["official_network"] = np.where(share_off >= p.min_overlap, "official", np.where(share_plan >= p.min_overlap, "planned", None))
    dem_mult = cn.demand_multiplier(edges["cyc_calibrated"], p)
    off_mult = np.where(share_all >= p.min_overlap, p.official_multiplier, 1.0)
    design = cn.undirected_cost(sf, sb) * dem_mult * off_mult
    edges["design_cost"] = design
    main_comp = edges["in_main_component"].to_numpy(dtype=bool)
    ferry = kind == "ferry"
    inp = cn.DesignInputs.build(geoms, edges["node_u"], edges["node_v"], design, length, edges["cyc_calibrated"], main_comp & ~ferry)
    pos_all = np.flatnonzero(main_comp & np.isfinite(design))
    g_all = cn.Graph(inp.node_u[pos_all], inp.node_v[pos_all], design[pos_all], pos_all)
    g_new = inp.graph(np.ones(n, dtype=bool))
    print(f"cycle-network: Soll resistance and bonuses ({time.perf_counter() - t_start:.0f} s)")

    # C-NET-01/02 corridors
    pts_all = corridor_points(p, dp, manifest, hamburg, districts)
    pts = pts_all[pts_all["kept"]].reset_index(drop=True)
    xy = np.c_[pts.geometry.x, pts.geometry.y]
    pts["node"] = cn.nearest_nodes(inp, g_new, xy)
    node_xy = pd.DataFrame(inp.node_xy, index=inp.node_ids).loc[pts["node"]].to_numpy()
    snap = pd.Series(np.hypot(*(node_xy - xy).T))
    pairs = cn.corridor_pairs(xy, centre=0, k=p.k_nearest, max_m=p.max_pair_m)
    paths = cn.route_pairs(g_all, pts["node"].to_numpy(), pairs)
    routes: list[Route] = []
    cyc = inp.demand
    for (a, b_), path in paths.items():
        rsv = cn.rsv_mask(length[path], cyc[path], p)
        routes.append(Route("corridor", list(path), np.where(rsv, R, H), f"{pts['label'][a]} – {pts['label'][b_]}"))
    print(f"cycle-network: {len(pts)} corridor points, {len(pairs)} pairs, {len(routes)} corridors ({time.perf_counter() - t_start:.0f} s)")

    # C-NET-07/08 HAUPT
    barriers = read_barriers(pbf, p, hamburg)
    exclude = read_exclude_areas(pbf, p, hamburg)
    ranks = edge_ranks(routes, n)
    res_h1 = cn.densify(inp, ranks >= H, p.mesh_max_m["HAUPT"], barriers, hamburg, exclude, rural, p)
    routes += [Route("mesh_haupt", r, np.full(len(r), H)) for r in res_h1.routes]
    print(f"cycle-network: HAUPT densify {len(res_h1.routes)} routes, {len(res_h1.gaps)} gaps ({time.perf_counter() - t_start:.0f} s)")

    # C-NET-10 parallel rule
    final_names = final["name"]
    labels = _labels(edges, final_names)
    seg_dtv = edges["segment_id"].map(final["dtv_official"])
    side_dtv = edges["sidepath_of"].map(final["dtv_official"])
    dtv = seg_dtv.fillna(side_dtv).to_numpy(dtype="float64")
    high = np.nan_to_num(dtv, nan=0.0) > p.patt_dtv
    patt_main, patt = parallel_rule(routes, inp, high, p, labels)
    ranks = edge_ranks(routes, n)
    patt_basis = patt_main & (ranks < H)
    res_h2 = cn.densify(inp, ranks >= H, p.mesh_max_m["HAUPT"], barriers, hamburg, exclude, rural, p, blocked=patt_basis)
    routes += [Route("mesh_haupt", r, np.full(len(r), H)) for r in res_h2.routes]
    ranks = edge_ranks(routes, n)
    ranks[patt_basis & (ranks < B)] = B
    print(f"cycle-network: P-ATT-03 {sum(r['accepted'] for r in patt)}/{len(patt)} runs moved; HAUPT densify 2: "
          f"{len(res_h2.routes)} routes ({time.perf_counter() - t_start:.0f} s)")

    # C-NET-09 binding, C-NET-08 BASIS
    schools = gpd.read_parquet(RAW / "schools__osm.parquet")
    school_pts = schools.geometry.representative_point()
    shops = read_shops(pbf, p.nahversorgung_shops)
    targets = pd.concat([gpd.GeoSeries(school_pts.to_numpy(), crs=WORK_CRS), shops.geometry], ignore_index=True)
    targets = targets[targets.within(hamburg)]
    attach = cn.attach_points(g_new, inp, ranks >= B, np.c_[targets.x, targets.y], p.binding_radius_m)
    routes += [Route("attach", r, np.full(len(r), B)) for r in attach]
    ranks = edge_ranks(routes, n)
    ranks[patt_basis & (ranks < B)] = B
    res_b = cn.densify(inp, ranks >= B, p.mesh_max_m["BASIS"], barriers, hamburg, exclude, rural, p)
    routes += [Route("mesh_basis", r, np.full(len(r), B)) for r in res_b.routes]
    ranks = edge_ranks(routes, n)
    ranks[patt_basis & (ranks < B)] = B
    print(f"cycle-network: {len(attach)} attachments, BASIS densify {len(res_b.routes)} routes, {len(res_b.gaps)} gaps "
          f"({time.perf_counter() - t_start:.0f} s)")

    # C-NET-11 continuity (before overrides)
    smoothed = np.zeros(n, dtype=bool)
    for rt in routes:
        e = np.asarray(rt.edges, dtype="int64")
        if len(e) < 3:
            continue
        new, _ = cn.smooth_sequence(ranks[e], length[e], patt_basis[e], p.continuity_max_gap_m)
        up = new > ranks[e]
        if up.any():
            smoothed[e[up]] = True
            ranks[e[up]] = new[up]

    for i, rt in enumerate(routes):
        rt.route_id = cn.route_id(rt.kind, edges["edge_id"].iloc[rt.edges]) if rt.edges else f"rt_empty_{i}"
    out = edges.copy()
    out["cycle_cat_proposed"] = np.array(cn.CATEGORY_ORDER, dtype=object)[ranks]
    ovr = ov.read_overrides(ov.CYCLE_NETWORK_OVERRIDES_PATH)
    ov.validate_cycle_network(ovr, out["edge_id"])
    out = ov.apply_cycle_network(out, ovr)
    final_rank = out["cycle_cat_final"].map(cn.RANK).to_numpy()
    locked_override = (out["cycle_cat_source"] == "override").to_numpy()

    # routes table, primary route per edge
    best_rank = np.full(n, -1)
    primary = np.array([None] * n, dtype=object)
    members: list[list[str]] = [[] for _ in range(n)]
    trace_routes: list[list[dict]] = [[] for _ in range(n)]
    route_rows = []
    seen = {}
    for rt in routes:
        if not rt.edges:
            continue
        e = np.asarray(rt.edges, dtype="int64")
        if rt.route_id in seen:
            continue
        seen[rt.route_id] = True
        for pos, rk in zip(e, rt.ranks):
            members[pos].append(rt.route_id)
            if rk > best_rank[pos]:
                best_rank[pos], primary[pos] = rk, rt.route_id
            if len(trace_routes[pos]) < TRACE_ROUTES:
                trace_routes[pos].append({"rule": KIND_RULE[rt.kind] if not (rt.kind == "corridor" and rk == R) else "C-NET-06",
                                          "result": cn.CATEGORY_ORDER[rk], "route_id": rt.route_id})
        fr = final_rank[e]
        geom = shapely.line_merge(shapely.union_all(geoms[e]))
        rsv_m = float(length[e][rt.ranks == R].sum())
        route_rows.append({
            "route_id": rt.route_id, "kind": rt.kind, "label": rt.label or KIND_DE[rt.kind],
            "category": cn.CATEGORY_ORDER[int(rt.ranks.max())], "length_m": float(length[e].sum()), "n_edges": len(e),
            "n_rsv_edges": int((rt.ranks == R).sum()), "rsv_km": rsv_m / 1000,
            "cyc_median": float(np.median(cyc[e])), "edge_ids": edges["edge_id"].iloc[e].tolist(),
            "n_category_changes": len(cn._runs(fr.tolist())) - 1,
            "override_break": bool((locked_override[e] & (fr < rt.ranks)).any()),
            "patt_runs": json.dumps([{"edges": edges["edge_id"].iloc[r["edges"]].tolist(), "accepted": r["accepted"],
                                      "detour": None if not np.isfinite(r["detour"]) else round(r["detour"], 3)}
                                     for r in patt if r["route"] is rt]),
            "geometry": geom})
    routes_gdf = gpd.GeoDataFrame(route_rows, geometry="geometry", crs=WORK_CRS)

    # rule_trace_cycle
    patt_alt = np.zeros(n, dtype=bool)
    for r in patt:
        if r["accepted"]:
            patt_alt[r["alt_edges"]] = True
    traces = []
    sk, sfac = out["soll_factor_key"].to_numpy(), out["soll_factor"].to_numpy()
    for i in range(n):
        steps = [{"rule": "C-NET-03", "result": round(float(sfac[i]), 3),
                  "values": {"factor": sk[i], "cat_final": cat_final.iat[i] if isinstance(cat_final.iat[i], str) else None}},
                 {"rule": "C-NET-04", "result": round(float(dem_mult[i]), 3), "values": {"cyc": None if not np.isfinite(cyc[i]) else round(float(cyc[i]))}},
                 {"rule": "C-NET-05", "result": float(off_mult[i]), "values": {"official_share": round(float(share_all[i]), 2)}}]
        steps += trace_routes[i]
        if len(members[i]) > TRACE_ROUTES:
            steps.append({"rule": "routes", "result": len(members[i])})
        if patt_alt[i]:
            steps.append({"rule": "C-NET-10", "result": "Parallelroute"})
        if patt_basis[i]:
            steps.append({"rule": "C-NET-10", "result": "BASIS", "values": {"dtv": round(float(dtv[i]))}})
        if smoothed[i]:
            steps.append({"rule": "C-NET-11", "result": out["cycle_cat_proposed"].iat[i]})
        if not members[i] and not patt_basis[i]:
            steps.append({"rule": "C-NET-12", "result": "ERSCHL", "values": {"in_main_component": bool(main_comp[i])}})
        if locked_override[i]:
            steps.append({"rule": "override", "result": out["cycle_cat_final"].iat[i], "values": {"reason": out["cycle_override_reason"].iat[i]}})
        traces.append(cn.trace_json(steps))
    out["route_id"] = primary
    out["route_ids"] = [m or None for m in members]
    out["patt_main_street"] = patt_basis
    out["patt_alternative"] = patt_alt
    out["continuity_smoothed"] = smoothed
    out["rule_trace_cycle"] = traces
    out["label"] = labels

    # gaps
    gap_rows = [{**g, "level": "HAUPT", "max_m": p.mesh_max_m["HAUPT"]} for g in res_h2.gaps] + \
               [{**g, "level": "BASIS", "max_m": p.mesh_max_m["BASIS"]} for g in res_b.gaps]
    gaps = gpd.GeoDataFrame(gap_rows, geometry="geometry", crs=WORK_CRS) if gap_rows else \
        gpd.GeoDataFrame({"side_m": [], "reason": [], "level": [], "max_m": []}, geometry=[], crs=WORK_CRS)
    if len(gaps):
        j = gpd.sjoin(gpd.GeoDataFrame(geometry=gaps.geometry.representative_point(), crs=WORK_CRS),
                      districts[["name", "geometry"]], how="left", predicate="within")
        gaps["bezirk"] = j[~j.index.duplicated()]["name"].reindex(gaps.index)
    else:
        gaps["bezirk"] = []

    # metrics for the report
    mesh_stats = {}
    for lvl in ("HAUPT", "BASIS"):
        net = final_rank >= cn.RANK[lvl]
        faces = cn.mesh_faces(geoms[net], barriers, hamburg)
        rural_f = shapely.within(shapely.point_on_surface(faces), rural)
        raw = np.sqrt(shapely.area(faces))
        side = cn.mesh_side(faces, exclude, only=raw > p.mesh_max_m[lvl])
        chk = side[~rural_f] if len(faces) else np.array([np.nan])
        mesh_stats[lvl] = {"n": int((~rural_f).sum()), "median": float(np.nanmedian(chk)), "p90": float(np.nanquantile(chk, 0.9)),
                           "max": float(np.nanmax(chk)), "over": int((chk > p.mesh_max_m[lvl]).sum()),
                           "skipped": int(((side > p.mesh_max_m[lvl]) & rural_f).sum())}
    comps = {c: components(inp, final_rank >= cn.RANK[c]) for c in ("RSV", "HAUPT", "BASIS")}
    hr_geoms = geoms[final_rank >= H]
    hr_zone = shapely.buffer(hr_geoms, p.coverage_m)
    st = gtfs.rapid_transit_stations(_gtfs_path(manifest), dp.rapid_transit_route_types)
    st = st[st.within(hamburg)]
    uni = gpd.read_parquet(RAW / "universities__osm.parquet")
    uni = uni[uni["amenity"].isin(p.university_amenity)].geometry.representative_point()
    zone_tree = shapely.STRtree(hr_zone)
    coverage = {}
    for name, g in (("Schulen (OSM)", school_pts[school_pts.within(hamburg)]), ("Schnellbahnhalte", st.geometry),
                    ("Hochschulen (OSM university)", uni[uni.within(hamburg)])):
        hit = zone_tree.query(g.values, predicate="within")[0]
        coverage[name] = (len(g), len(np.unique(hit)) / len(g) if len(g) else float("nan"))

    off_lines = official.geometry.values[is_off]
    plan_lines = official.geometry.values[is_plan]
    soll_any = geoms[final_rank >= B]
    hr_buf = shapely.buffer(hr_geoms, p.compare_buffer_m)
    any_buf = shapely.buffer(soll_any, p.compare_buffer_m)
    off_len, plan_len = shapely.length(off_lines), shapely.length(plan_lines)
    cov_off = cn.overlap_share(off_lines, hr_buf)
    cov_off_any = cn.overlap_share(off_lines, any_buf)
    cov_plan = cn.overlap_share(plan_lines, hr_buf)
    hr_len = length[final_rank >= H]
    in_off = cn.overlap_share(hr_geoms, shapely.buffer(off_lines, p.compare_buffer_m))
    in_plan = cn.overlap_share(hr_geoms, shapely.buffer(plan_lines, p.compare_buffer_m))
    add_m = hr_len * (1 - in_off)
    add_plan_m = hr_len * np.minimum(in_plan, 1 - in_off)
    miss = gpd.GeoDataFrame({"missing_m": off_len * (1 - cov_off)}, geometry=off_lines, crs=WORK_CRS)
    miss = miss.sort_values("missing_m", ascending=False).head(TOP_N)
    rank_tree = shapely.STRtree(geoms)
    soll_here = []
    for g in miss.geometry:
        idx = rank_tree.query(g.buffer(p.compare_buffer_m), predicate="intersects")
        soll_here.append(cn.CATEGORY_ORDER[int(final_rank[idx].max())] if len(idx) else "–")
    miss["soll_here"] = soll_here
    hr = out[final_rank >= H].assign(add_m=add_m, add_plan_m=add_plan_m)
    add = hr[hr["add_m"] > 0].groupby("label").agg(km=("add_m", lambda s: s.sum() / 1000), planned_km=("add_plan_m", lambda s: s.sum() / 1000),
                                                     cat=("cycle_cat_final", "max"), geometry=("geometry", lambda s: shapely.union_all(s.values)))
    add = add[add.index != "–"].sort_values("km", ascending=False).head(TOP_N).reset_index()
    compare = {"official_km": off_len.sum() / 1000, "official_covered_km": (off_len * cov_off).sum() / 1000,
               "official_covered_any_km": (off_len * cov_off_any).sum() / 1000,
               "planned_km": plan_len.sum() / 1000, "planned_covered_km": (plan_len * cov_plan).sum() / 1000,
               "soll_km": hr_len.sum() / 1000, "additional_km": add_m.sum() / 1000, "additional_in_planned_km": add_plan_m.sum() / 1000,
               "missing": miss, "additional": add}
    compare["official_covered_share"] = compare["official_covered_km"] / compare["official_km"]
    compare["official_covered_any_share"] = compare["official_covered_any_km"] / compare["official_km"]

    # outputs
    keep_cols = [c for c in out.columns if c not in ("label",)]
    out_w = out[keep_cols].copy()
    out_w["route_ids"] = out_w["route_ids"].map(lambda m: json.dumps(m) if m else None)
    out_w.to_parquet(OUT_PATH, index=False)
    routes_gdf.assign(edge_ids=routes_gdf["edge_ids"].map(json.dumps)).to_parquet(ROUTES_PATH, index=False)
    gaps.to_parquet(GAPS_PATH, index=False)

    _map(MAP_HAUPT, [(geoms[final_rank == H], "#2b6cb0", 1.0, "HAUPT", "solid"), (geoms[final_rank == R], "#c53030", 2.2, "RSV", "solid")],
         districts, "Soll-Radnetz: RSV und HAUPT (Entwurf, nicht amtlich)", pts)
    _map(MAP_BASIS, [(geoms[final_rank == B], "#38a169", 0.5, "BASIS", "solid"), (geoms[final_rank >= H], "#999", 0.9, "RSV/HAUPT", "solid")],
         districts, "Soll-Radnetz: BASIS über RSV/HAUPT (Entwurf, nicht amtlich)")
    _map(MAP_COMPARE, [(plan_lines, "#ed8936", 1.2, "amtlich geplant", "dashed"), (off_lines, "#dd6b20", 2.4, "amtlich Bestand", "solid"),
                       (hr_geoms, "#2b6cb0", 0.8, "Soll RSV/HAUPT", "solid")],
         districts, "Soll RSV/HAUPT vs. amtliches Radnetz Hamburg")
    ctx = {"out": out, "p": p, "version": cyc_rules.meta.version, "compare": compare, "gaps_haupt": res_h2.gaps,
           "gaps_basis": res_b.gaps, "patt": patt, "points": pts_all, "n_pairs": len(pairs), "n_corridors": len(paths),
           "snap": snap, "components": comps, "mesh_stats": mesh_stats,
           "rounds": {"HAUPT 1": res_h1.rounds, "HAUPT 2": res_h2.rounds, "BASIS": res_b.rounds},
           "coverage": coverage, "routes": routes_gdf, "n_smoothed": int(smoothed.sum()), "gaps": gaps}
    write_report(ctx)
    print(f"cycle-network: {n} edges -> {OUT_PATH.relative_to(REPO_ROOT)}, {len(routes_gdf)} routes, report "
          f"{REPORT_PATH.relative_to(REPO_ROOT)} ({time.perf_counter() - t_start:.0f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
