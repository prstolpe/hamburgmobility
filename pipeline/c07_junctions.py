"""Cycle stage 7: Soll junction type and cyclist treatment per junction (prompts/20_junctions.md).

Usage: uv run python -m pipeline.c07_junctions

Junctions (J-M-01): nodes of the street graph (segments with cat_final) with degree >= 3 and nodes where a standalone
cycle path meets a street; nodes joined by a short street segment or on the same roundabout form one junction.
Legs with category, cycle category, Soll facility and DTV (J-M-02), space from the ALKIS traffic area (J-M-03),
decision table J-01..J-11 (J-M-04, J-M-05), cyclist treatment JC-01..JC-05, Ist type from OSM (J-M-06), priority
(J-M-07) and overrides/junction_overrides.csv (approved only). Writes data/interim/junctions.parquet (points),
reports/junctions.md and reports/junctions_review.csv.
"""

import datetime as dt
import json
import sys
import time
import warnings
from collections import Counter, defaultdict

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import MultiPoint, Point

from config.schema.cycling_model import NO_CYCLE_CATEGORY
from config.schema.design_model import IST_JUNCTION_TYPES
from pipeline.c04_principles import ALKIS_PATH, SIGNALS_PATH, _links, load_crashes
from pipeline.lib import junctions as jn
from pipeline.lib import overrides as ov
from pipeline.lib.area import read_work_area, sample_by_district
from pipeline.lib.crs import WORK_CRS, to_work_crs
from pipeline.lib.links import load_viewers
from pipeline.lib.manifest import REPO_ROOT, load_manifest
from pipeline.lib.rules import load_design_rules, load_rules
from pipeline.s02_network import _pbf_from_manifest
from pipeline.s04_features import OSM_BBOX_MARGIN_DEG

INTERIM = REPO_ROOT / "data" / "interim"
FINAL_PATH = INTERIM / "final.parquet"
FACILITY_PATH = INTERIM / "cycle_facility.parquet"
XS_PATH = INTERIM / "cross_section_soll.parquet"
NETWORK_PATH = INTERIM / "cycle_network.parquet"
N6_PATH = INTERIM / "coherence_nodes.parquet"
OUT_PATH = INTERIM / "junctions.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "junctions.md"
REVIEW_PATH = REPO_ROOT / "reports" / "junctions_review.csv"
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
TOP_N = 30
NETWORK_CATS = ("RSV", "HAUPT", "BASIS")

TYPE_DE = {
    "roundabout_single_lane_cycle_priority": "Kreisverkehr einstreifig, Rad bevorrechtigt",
    "roundabout_single_lane_cycle_yield": "Kreisverkehr einstreifig, Rad wartepflichtig",
    "turbo_roundabout": "Turbokreisverkehr",
    "signal_protected": "LSA, geschützte Kreuzung",
    "priority_raised": "Vorfahrt mit Plateau",
    "priority_flat_coloured": "Vorfahrt, eingefärbte Fläche",
    "continuous_footway_exit": "Gehwegüberfahrt",
    "equal_right_before_left": "gleichrangig, rechts vor links",
    "cycle_crossing_priority": "Radwegfurt mit Vorrang",
    "cycle_crossing_signal": "Radwegfurt mit LSA",
    "grade_separated_cycle": "planfrei (Brücke/Tunnel)",
    None: "kein Soll-Typ",
}
IST_DE = {"roundabout": "Kreisverkehr", "signal_plateau": "LSA mit Plateau", "signal": "LSA", "plateau": "Plateau",
          "none_mapped": "nichts erfasst"}
RESULT_DE = {"match": "passt", "not_checkable": "nicht prüfbar", "mismatch": "Handlungsbedarf", None: "–"}
FLAG_DE = {
    "dtv_partial": "DTV fehlt an einem GOW/SW-Arm; Zufluss ist eine Untergrenze",
    "dtv_unknown": "DTV fehlt an allen GOW/SW-Armen",
    "space_unknown": "keine ALKIS-Verkehrsfläche am Knoten; Platz unbekannt",
    "condition_unknown": "Bedingung wegen fehlender Werte unbekannt; Typ nach J-M-05.on_unknown",
    "category_alias": "Kategorie über category_alias abgebildet (ETW_ERF → ETW30)",
    "cycle_path_ignored": "eigenständiger Radweg an einem Straßenknoten; Paar aus Straßen gebildet",
    "no_rule": "keine Zeile der Entscheidungstabelle passt",
    "no_cycle_crossing": "planfrei vorgeschlagen, aber keine Radroute quert den Stroomweg (Autobahnanschluss oder Route nur längs)",
    "dtv_above_roundabout_max": "einstreifiger Kreisverkehr vorgeschlagen (J-03 ohne DTV-Bedingung), Zufluss über roundabout_max_dtv",
}
# N6 (rules.yaml) Soll types and the c07 types that fulfil them; only for the comparison in the report.
N6_COMPATIBLE = {
    "roundabout_or_signal_plateau": {"roundabout_single_lane_cycle_priority", "roundabout_single_lane_cycle_yield",
                                     "turbo_roundabout", "signal_protected"},
    "roundabout": {"roundabout_single_lane_cycle_priority", "roundabout_single_lane_cycle_yield", "turbo_roundabout"},
    "priority_gow_sidewalk_crossover": {"continuous_footway_exit", "priority_raised"},
    "sidewalk_crossover_or_priority_plateau": {"continuous_footway_exit", "priority_raised"},
    "equal_right_before_left": {"equal_right_before_left"},
    "sidewalk_crossover": {"continuous_footway_exit"},
}


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _fmt(v, digits: int = 0) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "–"
    return f"{v:,.{digits}f}".replace(",", " ")


_PARAMS: dict = {}


def junction_type(props: dict, design) -> dict:
    """Golden-case API (tests/golden/cycling/j*.geojson): Soll type, trace and cyclist treatment from case properties."""
    hit = _PARAMS.get(id(design))
    if hit is None or hit[0] is not design:
        hit = _PARAMS[id(design)] = (design, jn.JunctionParams.from_rules(design, load_rules()))
    p = hit[1]
    res = jn.decide(props, p)
    return {**res, "cyclist_treatment": jn.treatments(res["junction_type_soll"], res["pair"], props["legs"], p)}


# --- inputs ------------------------------------------------------------------------------------------------------


def read_osm(pbf, work_area) -> dict:
    """Roundabout way ids and traffic_calming=table nodes (as in s06_coherence)."""
    from pyrosm import OSM

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wgs = gpd.GeoSeries([work_area], crs=WORK_CRS).to_crs(4326).iloc[0]
        osm = OSM(str(pbf), bounding_box=wgs.buffer(OSM_BBOX_MARGIN_DEG))
        tables = osm.get_data_by_custom_criteria(custom_filter={"traffic_calming": ["table"]}, filter_type="keep",
                                                 keep_nodes=True, keep_ways=False, keep_relations=False)
        rb = osm.get_data_by_custom_criteria(custom_filter={"junction": ["roundabout", "circular"]},
                                             filter_type="keep", keep_nodes=False, keep_ways=True, keep_relations=False)
    return {"tables": gpd.GeoSeries([], crs=WORK_CRS) if tables is None else to_work_crs(tables).geometry.reset_index(drop=True),
            "roundabout_ways": set() if rb is None else {int(i) for i in rb["id"]}}


def node_points(seg: gpd.GeoDataFrame) -> dict[int, Point]:
    pts = {}
    for u, v, g in zip(seg["node_u"], seg["node_v"], seg.geometry):
        pts.setdefault(int(u), Point(g.coords[0]))
        pts.setdefault(int(v), Point(g.coords[-1]))
    return pts


def standalone_paths(net: gpd.GeoDataFrame, m01: dict) -> gpd.GeoDataFrame:
    """J-M-01: path edges that are no sidepath and are a cycleway or part of the cycle network."""
    path = net[(net["kind"] == "path") & net["sidepath_of"].isna()]
    keep = path["highway"].isin(m01["cycle_path_highways"]) | path["cycle_cat_final"].isin(m01["cycle_path_network_cats"])
    return path[keep]


# --- junctions ---------------------------------------------------------------------------------------------------


class _UF:
    def __init__(self, items):
        self.p = {i: i for i in items}

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def build_clusters(seg: pd.DataFrame, paths: pd.DataFrame, rb_segments: set, radius: float) -> dict[int, list[int]]:
    """{root node: member nodes}. Candidates: degree >= 3 or touched by a standalone cycle path (J-M-01)."""
    deg = Counter()
    for u, v in zip(seg["node_u"], seg["node_v"]):
        deg[int(u)] += 1
        deg[int(v)] += 1
    street_nodes = set(deg)
    path_nodes = (set(paths["node_u"].astype(int)) | set(paths["node_v"].astype(int))) & street_nodes
    cand = {n for n, d in deg.items() if d >= 3} | path_nodes
    uf = _UF(cand)
    for sid, u, v, length in zip(seg["segment_id"], seg["node_u"], seg["node_v"], seg["length_m"]):
        u, v = int(u), int(v)
        if u in cand and v in cand and (length <= radius or sid in rb_segments):
            uf.union(u, v)
    # nodes on the same roundabout: components of the roundabout segments
    rb = seg[seg["segment_id"].isin(rb_segments)]
    rb_uf = _UF(set(rb["node_u"].astype(int)) | set(rb["node_v"].astype(int)))
    for u, v in zip(rb["node_u"], rb["node_v"]):
        rb_uf.union(int(u), int(v))
    groups = defaultdict(list)
    for n in rb_uf.p:
        groups[rb_uf.find(n)].append(n)
    for members in groups.values():
        inside = [n for n in members if n in cand]
        for a, b in zip(inside, inside[1:]):
            uf.union(a, b)
    clusters = defaultdict(list)
    for n in cand:
        clusters[uf.find(n)].append(n)
    return {min(m): sorted(m) for m in clusters.values()}


def _bearing(origin: tuple[float, float], geom, from_start: bool, dist: float) -> float:
    length = geom.length
    d = min(dist, length)
    q = geom.interpolate(d if from_start else length - d)
    return float(np.degrees(np.arctan2(q.x - origin[0], q.y - origin[1])) % 360.0)


def describe_legs(clusters: dict, seg: pd.DataFrame, paths: pd.DataFrame, pts: dict, m02: dict, search_m: float) -> dict:
    """Per junction: legs, arms (J-M-02 arm_merge), internal segments, entering_dtv_sum and flags."""
    node_to = {n: root for root, members in clusters.items() for n in members}
    centre = {root: (float(np.mean([pts[n].x for n in m])), float(np.mean([pts[n].y for n in m])))
              for root, m in clusters.items()}
    out = {root: {"legs": [], "internal": [], "flags": []} for root in clusters}

    def add(c, base: dict, geom, at_start: bool) -> None:
        out[c]["legs"].append({**base, "bearing": _bearing(centre[c], geom, at_start, search_m)})

    for r in seg.itertuples(index=False):
        cu, cv = node_to.get(int(r.node_u)), node_to.get(int(r.node_v))
        if cu is not None and cu == cv:
            out[cu]["internal"].append(r.segment_id)
            continue
        base = {"id": r.segment_id, "cat": r.cat_final, "cycle_cat": r.cycle_cat, "facility": r.facility,
                "dtv": None if pd.isna(r.dtv_official) else float(r.dtv_official), "tram": bool(r.tram),
                "bezirk": r.bezirk, "name": r.name if isinstance(r.name, str) else None}
        if cu is not None:
            add(cu, base, r.geometry, True)
        if cv is not None:
            add(cv, base, r.geometry, False)
    for r in paths.itertuples(index=False):
        cu, cv = node_to.get(int(r.node_u)), node_to.get(int(r.node_v))
        if cu is not None and cu == cv:
            continue
        base = {"id": r.edge_id, "cat": jn.CYCLE_PATH, "cycle_cat": r.cycle_cat_final, "facility": "own_path",
                "dtv": None, "tram": False, "bezirk": r.bezirk, "name": r.name if isinstance(r.name, str) else None}
        if cu is not None:
            add(cu, base, r.geometry, True)
        if cv is not None:
            add(cv, base, r.geometry, False)
    share, zero = float(m02["dtv_share_entering"]["value"]), set(m02["zero_dtv_categories"])
    angle = float(m02["arm_merge_angle_deg"]["value"])
    for d in out.values():
        d["legs"].sort(key=lambda leg: (leg["cat"] == jn.CYCLE_PATH, leg["id"]))
        d["arms"] = jn.merge_arms(d["legs"], angle)
        d["entering_dtv_sum"], f = jn.entering_dtv(d["arms"], share, zero)
        d["flags"] += f
    return out


def space_radius(geoms: gpd.GeoSeries, traffic: np.ndarray, search_m: float, tol: float) -> np.ndarray:
    """J-M-03: radius of the largest inscribed circle of the ALKIS traffic area within search_m of the junction."""
    tree = shapely.STRtree(traffic)
    out = np.full(len(geoms), np.nan)
    for i, g in enumerate(geoms):
        buf = g.buffer(search_m)
        idx = tree.query(buf, predicate="intersects")
        if len(idx) == 0:
            continue
        area = shapely.union_all(shapely.intersection(traffic[idx], buf))
        if area.is_empty:
            continue
        parts = list(getattr(area, "geoms", [area]))
        parts = [shapely.Polygon(p.exterior) for p in parts if p.geom_type == "Polygon" and p.area > 0]
        if not parts:
            continue
        hit = [p for p in parts if p.intersects(g)]
        part = max(hit or parts, key=lambda p: (p.area if hit else -p.distance(g)))
        out[i] = shapely.maximum_inscribed_circle(part, tol).length
    return out


def near_any(points: gpd.GeoSeries, features: gpd.GeoSeries, radius: float) -> np.ndarray:
    """Per junction geometry: is a feature within radius of any member node?"""
    if features is None or len(features) == 0:
        return np.zeros(len(points), dtype=bool)
    tree = shapely.STRtree(features.to_numpy())
    idx = tree.query(points.to_numpy(), predicate="dwithin", distance=radius)
    hit = np.zeros(len(points), dtype=bool)
    hit[np.unique(idx[0])] = True
    return hit


def crash_counts(geoms: gpd.GeoSeries, crashes: gpd.GeoDataFrame, radius: float) -> pd.DataFrame:
    """Cyclist crashes per junction (nearest junction within radius); counts only (J-M-07)."""
    cyc = crashes[crashes["cyclist"].astype(bool)]
    n = len(geoms)
    tree = shapely.STRtree(geoms.to_numpy())
    i_pt, i_j = tree.query_nearest(cyc.geometry.to_numpy(), max_distance=radius, all_matches=False)
    severe = cyc["severe_or_fatal"].to_numpy(dtype=bool)[i_pt]
    return pd.DataFrame({"crashes_cyc": np.bincount(i_j, minlength=n).astype("int64"),
                         "crashes_cyc_severe": np.bincount(i_j, weights=severe.astype(float), minlength=n).astype("int64")})


# --- classification ------------------------------------------------------------------------------------------------


def _leg_json(legs: list[dict]) -> str:
    return json.dumps([{"ids": leg["ids"], **{k: leg[k] for k in ("cat", "cycle_cat", "facility", "dtv", "name")},
                        "bearing": round(leg["bearing"])} for leg in legs],
                      ensure_ascii=False, default=float)


def classify(j: pd.DataFrame, p: jn.JunctionParams) -> pd.DataFrame:
    rows = []
    for r in j.itertuples(index=False):
        legs = r.legs_list
        flags = list(r.build_flags)
        if np.isnan(r.space_radius_m):
            flags.append("space_unknown")
        props = {"legs": legs, "entering_dtv_sum": r.entering_dtv_sum, "tram_present": r.tram_present,
                 "space_radius_m": None if np.isnan(r.space_radius_m) else float(r.space_radius_m),
                 "signal_present_ist": r.signal_present_ist, "flags": flags}
        res = jn.decide(props, p)
        soll = res["junction_type_soll"]
        if soll == "grade_separated_cycle" and not any(
                leg.get("cycle_cat") in NETWORK_CATS for leg in jn.crossing_legs(legs, res["pair"], p)):
            res["conflict_flags"].append("no_cycle_crossing")
        jc = jn.treatments(soll, res["pair"], legs, p)
        ist = jn.ist_type(r.roundabout_ist, r.signal_present_ist, r.plateau_ist)
        result = jn.ist_result(soll, ist, p)
        trace = res["rule_trace_junction"] + [
            {"id": "J-M-06", "passed": result is not None, "result": result, "values": {"ist": ist, "soll": soll}}]
        rows.append({
            "pair": "+".join(res["pair"]) if res["pair"] else None, "decision_rule": res["rule_id"],
            "junction_type_soll": soll, "junction_type_ist": ist, "ist_result": result,
            "action_needed": result == "mismatch", "cyclist_treatment": "|".join(jc) or None,
            "treatment_text": jn.treatment_text(jc),
            "conflict_flags": "|".join(dict.fromkeys(res["conflict_flags"])) or None,
            "confidence": res["confidence"],
            "rule_trace_junction": json.dumps(trace, ensure_ascii=False, default=float)})
    return pd.DataFrame(rows, index=j.index)


# --- report ------------------------------------------------------------------------------------------------------


def _type_de(t) -> str:
    return TYPE_DE.get(t if isinstance(t, str) else None, str(t))


def _s(v) -> str:
    return v if isinstance(v, str) and v else "–"


def _junction_row(r, viewers) -> str:
    return (f"| `{r.node_id}` | {_s(r.names)} | {_s(r.bezirk)} | {_s(r.pair)} | {r.top_cycle_cat} | "
            f"{_fmt(r.entering_dtv_sum)} | {_fmt(r.space_radius_m, 0)} | {IST_DE[r.junction_type_ist]} | "
            f"{_type_de(r.junction_type_final)} | {_s(r.cyclist_treatment)} | {r.crashes_cyc} | {_links(r.geometry, viewers)} |")


ROW_HEAD = ["| node_id | Straßen | Bezirk | Paar | Rad | Zufluss Kfz/24h | Platz r m | Ist | Soll | Führung | Radunfälle | Prüfen |",
            "| --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | ---: | --- |"]


def write_report(out: gpd.GeoDataFrame, n6: pd.DataFrame, ctx: dict) -> None:
    viewers = load_viewers()
    n = len(out)
    lines = [
        "# Knotenpunkte: Soll-Knotentyp und Radverkehrsführung (Stufe c07)", "",
        f"Erzeugt {_now()} mit pipeline/c07_junctions.py · design_rules.yaml {ctx['design_version']} · nicht amtlicher "
        "Entwurf. Entscheidungstabelle J-01…J-11, Führungen JC-01…JC-05 und Verfahren J-M-01…J-M-07 sind Entwürfe bzw. "
        "Annahmen (status draft) und vor Gebrauch fachlich zu prüfen.", "",
        "## Kurzfassung", "",
        f"- {_fmt(n)} Knotenpunkte aus {_fmt(ctx['n_nodes'])} Netzknoten (Grad ≥ 3: {_fmt(ctx['n_deg3'])}, Kreuzungen "
        f"eigenständiger Radwege: {_fmt(ctx['n_path_nodes'])}); {_fmt((out['n_members'] > 1).sum())} Knotenpunkte fassen "
        f"mehrere Netzknoten zusammen (Radius {ctx['cluster_radius']:g} m, Kreisverkehre ganz). Größter Knotenpunkt: "
        f"{out['n_members'].max()} Netzknoten, Ausdehnung bis {_fmt(out['extent_m'].max(), 0)} m.",
        f"- Soll-Typ vergeben: {_fmt(out['junction_type_soll'].notna().sum())}; ohne passende Zeile (`no_rule`): "
        f"{_fmt(out['junction_type_soll'].isna().sum())}.",
        f"- Handlungsbedarf (Ist passt nicht zum Soll): {_fmt(out['action_needed'].sum())} Knotenpunkte; nicht prüfbar: "
        f"{_fmt((out['ist_result'] == 'not_checkable').sum())}; passt: {_fmt((out['ist_result'] == 'match').sum())}.",
        f"- Overrides angewendet: {_fmt((out['junction_type_source'] == 'override').sum())} (overrides/junction_overrides.csv, nur approved).",
        f"- Straßenbahn an keinem Arm: der GTFS-Feed enthält {ctx['tram_routes']} Straßenbahnrouten; J-11 greift daher nicht."
        if ctx["tram_routes"] == 0 else f"- Straßenbahn an {_fmt(out['tram_present'].sum())} Knotenpunkten.",
        "- confidence: " + ", ".join(f"{k} {_fmt((out['confidence'] == k).sum())}" for k in jn.CONFIDENCE) + ".",
        "",
        "## Vorgehen", "",
        "1. **Knoten (J-M-01):** Knoten des Straßengraphen (Abschnitte mit cat_final) mit Grad ≥ 3 und Knoten, an denen "
        "ein eigenständiger Radweg (kein begleitender Radweg; highway=cycleway oder RSV/HAUPT/BASIS) auf eine Straße trifft. "
        "Knoten, die über einen Straßenabschnitt ≤ Clusterradius verbunden sind, und alle Knoten eines Kreisverkehrs bilden einen Knotenpunkt. "
        "node_id = kleinste OSM-Knoten-ID des Knotenpunkts.",
        "2. **Arme (J-M-02):** Abschnitte und eigenständige Radwege, die den Knotenpunkt verlassen. Zufluss = ½ × DTV je "
        "Kfz-Arm; ETW-Arme ohne DTV zählen 0, fehlt DTV an einem GOW/SW-Arm, ist die Summe eine Untergrenze.",
        "3. **Platz (J-M-03):** Radius des größten einbeschriebenen Kreises in der ALKIS-Verkehrsfläche im Umkreis "
        f"{ctx['search_radius']:g} m.",
        "4. **Kategoriepaar (J-M-04):** wie N6 – durchgehender Zug (höchste Kategorie, bis zu zwei Arme) und höchste übrige "
        "Straße; bleibt keine, aber ein eigenständiger Radweg, ist das Paar (Zug, cycle_path). Der Prompt nennt „die beiden "
        "ranghöchsten Arme“; wörtlich wäre jede Einmündung an einer GOW50 ein Paar GOW50+GOW50 (offene Frage).",
        "5. **Entscheidung (J-M-05):** Zeilen in der Reihenfolge " + ", ".join(ctx["order"]) + "; erste passende gilt. "
        "Unbekannte Bedingung → Typ der Zeile (Kreisverkehr bzw. erste Wahl), Flag condition_unknown.",
        "6. **Ist (J-M-06):** OSM junction=roundabout an einem Arm oder inneren Abschnitt, highway=traffic_signals und "
        f"traffic_calming=table im Umkreis {ctx['signal_radius']:g} m eines Netzknotens.",
        "", "## Anzahl je Soll-Typ", "",
        "| Soll-Typ | Knotenpunkte | davon Handlungsbedarf | davon Radnetz (RSV/HAUPT/BASIS) | Regeln |",
        "| --- | ---: | ---: | ---: | --- |"]
    in_net = out["top_cycle_cat"].isin(["RSV", "HAUPT", "BASIS"])
    for t in [*ctx["types"], None]:
        m = out["junction_type_final"].isna() if t is None else out["junction_type_final"] == t
        if not m.any():
            continue
        rules = ", ".join(f"{k} {v}" for k, v in out.loc[m, "decision_rule"].fillna("–").value_counts().sort_index().items())
        lines.append(f"| {_type_de(t)} | {_fmt(m.sum())} | {_fmt((m & out['action_needed']).sum())} | "
                     f"{_fmt((m & in_net).sum())} | {rules} |")

    lines += ["", "## Ist → Soll (Anzahl Knotenpunkte)", "",
              "Zeilen Ist aus OSM, Spalten Soll. Geschützte Kreuzung, eingefärbte Fläche, Gehwegüberfahrt und Furtgestaltung "
              "sind in OSM kaum erfasst; dort gilt „nicht prüfbar“ (J-M-06.ist_check).", ""]
    soll_cols = [t for t in ctx["types"] if (out["junction_type_final"] == t).any()]
    lines += ["| Ist \\ Soll | " + " | ".join(_type_de(t) for t in soll_cols) + " | gesamt |",
              "| --- | " + " | ".join("---:" for _ in soll_cols) + " | ---: |"]
    for ist in IST_JUNCTION_TYPES:
        mi = out["junction_type_ist"] == ist
        if not mi.any():
            continue
        lines.append(f"| {IST_DE[ist]} | " + " | ".join(_fmt((mi & (out['junction_type_final'] == t)).sum()) for t in soll_cols)
                     + f" | {_fmt(mi.sum())} |")

    lines += ["", "## Radverkehrsführung", "", "| Führung | Knotenpunkte | Beschreibung |", "| --- | ---: | --- |"]
    jc = out["cyclist_treatment"].fillna("").str.split("|")
    for k, text in jn.TREATMENT_DE.items():
        lines.append(f"| {k} | {_fmt(jc.apply(lambda xs, k=k: k in xs).sum())} | {text} |")
    lines += ["", "**Zielkonflikt JC-01 (Vorrang am Kreisverkehr):** CROW empfiehlt innerorts den Vorrang für Radfahrende "
              "auf dem umlaufenden Radweg; SWOV-Auswertungen sehen die Wartepflicht als sicherer. Nach deutschem Recht hat der "
              "Radverkehr am Kreisverkehr nur bei fahrbahnnaher Führung Vorrang (StVO/VwV prüfen). Die Steckbrieftexte der "
              f"{_fmt(jc.apply(lambda xs: 'JC-01' in xs).sum())} Kreisverkehre nennen diesen Konflikt (Spalte treatment_text); "
              "entschieden ist er nicht.", ""]

    lines += ["## Hinweise (conflict_flags)", "", "| Flag | Bedeutung | Knotenpunkte |", "| --- | --- | ---: |"]
    flags = out["conflict_flags"].fillna("").str.split("|")
    for f, text in FLAG_DE.items():
        lines.append(f"| `{f}` | {text} | {_fmt(flags.apply(lambda xs, f=f: f in xs).sum())} |")
    nr = out[out["junction_type_final"].isna()]
    if len(nr):
        lines += ["", "Paare ohne Zeile (Anzahl): " + ", ".join(f"{k} {v}" for k, v in nr["pair"].fillna("–").value_counts().head(12).items()) + "."]

    lines += ["", f"## Top {TOP_N} Knotenpunkte nach Priorität", "",
              "Nur Knotenpunkte mit Handlungsbedarf; sortiert nach Radunfällen (Unfallatlas "
              f"{ctx['crash_years']}, Radbeteiligung, nächster Knotenpunkt im Umkreis {ctx['cluster_radius']:g} m), dann "
              "Radkategorie des ranghöchsten Arms, dann Kfz-Zufluss (J-M-07).", "", *ROW_HEAD]
    for r in ctx["top"].itertuples():
        lines.append(_junction_row(r, viewers))

    gs = out[out["junction_type_final"] == "grade_separated_cycle"]
    gs_net = gs[~gs["conflict_flags"].fillna("").str.contains("no_cycle_crossing")]
    lines += ["", "## Vorschläge planfreie Querung (grade_separated_cycle)", "",
              f"{_fmt(len(gs))} Knotenpunkte; davon {_fmt(len(gs_net))} mit querender Radroute RSV/HAUPT/BASIS (unten). Die übrigen "
              f"{_fmt(len(gs) - len(gs_net))} sind Knoten an Stroomwegen, die keine Radroute quert (Autobahnanschlüsse oder "
              "Route nur längs des Stroomwegs, Flag no_cycle_crossing); dort ist keine planfreie Radquerung nötig.", "", *ROW_HEAD]
    for r in gs_net.sort_values(["crashes_cyc", "cycle_rank", "node_id"], ascending=[False, False, True]).itertuples():
        lines.append(_junction_row(r, viewers))

    lines += ["", "## Abgleich mit N6 (Straßenfunktionsplan, reports/coherence.md)", "",
              "Je Netzknoten mit N6-Eintrag: N6-Soll-Typ gegen den Soll-Typ des Knotenpunkts, zu dem er gehört. "
              "„vereinbar“ = der c07-Typ erfüllt den N6-Typ.", ""]
    if len(n6):
        n6 = n6.copy()
        n6["ok"] = [t in N6_COMPATIBLE.get(s, set()) for s, t in zip(n6["soll_type"], n6["junction_type_final"])]
        cols = [t for t in ctx["types"] if (n6["junction_type_final"] == t).any()]
        lines += ["| N6 \\ c07 | " + " | ".join(_type_de(t) for t in cols) + " | vereinbar |",
                  "| --- | " + " | ".join("---:" for _ in cols) + " | ---: |"]
        for s, g in n6.groupby("soll_type"):
            share = f"{100 * g['ok'].mean():.0f} %" if s in N6_COMPATIBLE else "–"
            lines.append(f"| {s} | " + " | ".join(_fmt((g['junction_type_final'] == t).sum()) for t in cols) + f" | {share} |")
        d = n6[n6["soll_type"].isin(N6_COMPATIBLE)]
        def cnt(s, c):
            return _fmt(((n6["soll_type"] == s) & (n6["junction_type_final"].isin(c))).sum())

        lines += ["", f"Vereinbar insgesamt: {100 * d['ok'].mean():.0f} % von {_fmt(len(d))} Netzknoten mit definiertem N6-Typ. "
                  "Hauptursachen der Unterschiede:", "",
                  f"- N6 kennt keine Fahrradstraßen: {cnt('equal_right_before_left', {'priority_raised'})} ETW–ETW-Knoten "
                  "werden in c07 „Vorfahrt mit Plateau“ für die Fahrradstraße (J-07).",
                  f"- ETW_ERF: N6 sieht Gehwegüberfahrt vor, c07 bildet ETW_ERF über category_alias auf ETW30 ab "
                  f"({cnt('sidewalk_crossover', {'equal_right_before_left', 'priority_raised'})} Netzknoten gleichrangig "
                  "bzw. Vorfahrt mit Plateau; offene Frage).",
                  f"- Kreisverkehr ohne Platz: {cnt('roundabout', {'priority_flat_coloured'})} GOW30–GOW30-Knoten erhalten "
                  "den J-03-Fallback „Vorfahrt, eingefärbte Fläche“; N6 prüft keinen Platz.",
                  "- Zusammenfassung naher Knoten und Richtungsfahrbahnen: das Kategoriepaar gilt für den ganzen Knotenpunkt; "
                  "c07 nutzt cat_final (nach Overrides), N6 cat_proposed."]

    lines += ["", f"## {SAMPLE_SIZE} Zufallsstichproben", "",
              f"Über Bezirke verteilt, Seed {SAMPLE_SEED}. Zusätzlich reports/junctions_review.csv mit bis zu {SAMPLE_SIZE} "
              "Knotenpunkten je Soll-Typ für die Prüfung im Orthophoto (Spalten reviewer, assessment, comment von Hand füllen).",
              "", *ROW_HEAD]
    for r in ctx["sample"].itertuples():
        lines.append(_junction_row(r, viewers))
    lines += ["", "## Grenzen", "",
              "- Knoten nur, wo OSM einen gemeinsamen Knoten hat; Brücken und Tunnel ohne Knoten fehlen, daher ist jeder "
              "Knotenpunkt im Ist plangleich.",
              "- Zusammenfassung naher Knoten über Abschnitte ≤ Clusterradius; in dichten Altbauquartieren können Ketten "
              "entstehen (Spalte extent_m).",
              "- DTV nur aus der HVS-Zählung 2019; an ETW-Armen fast nie vorhanden (zählt 0).",
              "- Platz aus der ALKIS-Verkehrsfläche ohne Gebäude, Bäume oder Leitungen; Kreisverkehr-Platzbedarf "
              "(roundabout_min_radius) ist eine Annahme.",
              "- Ist-Typ: Gehwegüberfahrten, Vorfahrtregelung und Furtgestaltung sind in OSM kaum erfasst (N6, offene Frage).",
              "- Radunfälle werden dem nächsten Knotenpunkt im Clusterradius zugeordnet und nur als Anzahl gespeichert.",
              "",
              "Quellen: OpenStreetMap-Mitwirkende (ODbL); Freie und Hansestadt Hamburg, ALKIS und Verkehrsmengen "
              "(dl-de/by-2.0); Unfallatlas der Statistischen Ämter des Bundes und der Länder (dl-de/by-2.0); HVV-GTFS "
              "(dl-de/by-2.0).", ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def review_sample(out: gpd.GeoDataFrame, viewers) -> pd.DataFrame:
    parts = []
    for t, g in out[out["junction_type_final"].notna()].groupby("junction_type_final"):
        parts.append(g.sample(n=min(SAMPLE_SIZE, len(g)), random_state=SAMPLE_SEED))
    s = pd.concat(parts).sort_values(["junction_type_final", "node_id"])
    wgs = s.to_crs(4326)
    return pd.DataFrame({
        "node_id": s["node_id"], "junction_type_soll": s["junction_type_final"], "junction_type_ist": s["junction_type_ist"],
        "pair": s["pair"], "names": s["names"], "bezirk": s["bezirk"], "lat": wgs.geometry.y.round(6), "lon": wgs.geometry.x.round(6),
        "links": [_links(g, viewers) for g in s.geometry], "reviewer": "", "assessment": "", "comment": ""})


# --- main --------------------------------------------------------------------------------------------------------


def main() -> int:
    design, rules = load_design_rules(), load_rules()
    p = jn.JunctionParams.from_rules(design, rules)
    for path, step in ((FINAL_PATH, "make coherence"), (FACILITY_PATH, "make cycle-facility"),
                       (XS_PATH, "make cross-section-soll"), (NETWORK_PATH, "make cycle-network"),
                       (N6_PATH, "make coherence"), (ALKIS_PATH, "make fetch"), (SIGNALS_PATH, "make fetch")):
        if not path.exists():
            print(f"junctions: {path.relative_to(REPO_ROOT)} missing; run `{step}` first", file=sys.stderr)
            return 1
    t0 = time.perf_counter()

    def tick(msg: str) -> None:
        print(f"junctions: {msg} ({time.perf_counter() - t0:.0f} s)")

    m = p.method
    radius = float(m["J-M-01"]["cluster_radius_m"]["value"])
    search = float(m["J-M-03"]["search_radius_m"]["value"])
    tol = float(m["J-M-03"]["tolerance_m"]["value"])
    signal_radius = float(rules.coherence_rule("N6").param("signal_radius_m"))
    manifest = load_manifest()

    final = gpd.read_parquet(FINAL_PATH, columns=["segment_id", "osm_way_ids", "name", "bezirk", "length_m", "node_u",
                                                  "node_v", "cat_final", "dtv_official", "geometry"])
    seg = final[final["cat_final"].notna()].copy()
    fac = pd.read_parquet(FACILITY_PATH, columns=["segment_id", "cycle_cat_final"]).set_index("segment_id")
    xs = pd.read_parquet(XS_PATH, columns=["segment_id", "cycle_facility_final", "tram_present"]).set_index("segment_id")
    seg["cycle_cat"] = seg["segment_id"].map(fac["cycle_cat_final"]).fillna(NO_CYCLE_CATEGORY)
    seg["facility"] = seg["segment_id"].map(xs["cycle_facility_final"])
    seg["facility"] = seg["facility"].where(seg["facility"].notna(), None)
    seg["tram"] = seg["segment_id"].map(xs["tram_present"]).fillna(False).astype(bool)
    net = gpd.read_parquet(NETWORK_PATH, columns=["edge_id", "kind", "highway", "name", "sidepath_of", "node_u", "node_v",
                                                  "cycle_cat_final", "bezirk", "geometry"])
    paths = standalone_paths(net, m["J-M-01"])
    osm = read_osm(REPO_ROOT / _pbf_from_manifest(manifest)["path"], read_work_area())
    rb_segments = set(seg.loc[seg["osm_way_ids"].map(lambda ws: any(int(w) in osm["roundabout_ways"] for w in ws)), "segment_id"])
    tick(f"{len(seg)} street segments, {len(paths)} standalone cycle path edges, {len(rb_segments)} roundabout segments")

    pts = node_points(seg)
    clusters = build_clusters(seg, paths, rb_segments, radius)
    deg = Counter(list(seg["node_u"].astype(int)) + list(seg["node_v"].astype(int)))
    path_nodes = (set(paths["node_u"].astype(int)) | set(paths["node_v"].astype(int))) & set(deg)
    legs = describe_legs(clusters, seg, paths, pts, m["J-M-02"], search)
    tick(f"{sum(len(v) for v in clusters.values())} nodes -> {len(clusters)} junctions")

    roots = sorted(clusters)
    member_geoms = gpd.GeoSeries([MultiPoint([pts[n] for n in clusters[r]]) for r in roots], crs=WORK_CRS)
    j = pd.DataFrame({"node_id": [str(r) for r in roots], "members": [clusters[r] for r in roots]})
    j["n_members"] = j["members"].map(len)
    j["extent_m"] = [shapely.minimum_bounding_radius(g) * 2 for g in member_geoms]
    j["legs_list"] = [legs[r]["arms"] for r in roots]
    j["legs_count"] = j["legs_list"].map(len)
    j["n_carriageway_legs"] = [len(legs[r]["legs"]) for r in roots]
    j["build_flags"] = [legs[r]["flags"] for r in roots]
    j["entering_dtv_sum"] = [legs[r]["entering_dtv_sum"] for r in roots]
    j["tram_present"] = [any(leg["tram"] for leg in legs[r]["legs"]) for r in roots]
    j["roundabout_ist"] = [bool(set(legs[r]["internal"]) & rb_segments or {leg["id"] for leg in legs[r]["legs"]} & rb_segments)
                           for r in roots]
    signals = to_work_crs(gpd.read_parquet(SIGNALS_PATH)).geometry
    j["signal_present_ist"] = near_any(member_geoms, signals, signal_radius)
    j["plateau_ist"] = near_any(member_geoms, osm["tables"], signal_radius)
    alk = gpd.read_parquet(ALKIS_PATH, columns=["nutzart", "geometry"])
    alk = to_work_crs(alk[alk["nutzart"].isin(rules.crosssection.rule("S-XS-02").alkis_nutzart)])
    j["space_radius_m"] = space_radius(member_geoms, alk.geometry.to_numpy(), search, tol)
    tick("space, signals, roundabouts")

    res = classify(j, p)
    j = j.join(res)
    crashes, years = load_crashes(manifest)
    cc = crash_counts(member_geoms, crashes, radius)
    del crashes
    j["crashes_cyc"], j["crashes_cyc_severe"] = cc["crashes_cyc"].to_numpy(), cc["crashes_cyc_severe"].to_numpy()
    tick(f"classified; crashes {min(years)}–{max(years)}")

    def top_cycle(ls):
        return max((leg["cycle_cat"] if leg["cycle_cat"] in jn.CYCLE_RANK else NO_CYCLE_CATEGORY for leg in ls),
                   key=jn.CYCLE_RANK.__getitem__, default=NO_CYCLE_CATEGORY)

    j["top_cycle_cat"] = j["legs_list"].map(top_cycle)
    j["cycle_rank"] = j["top_cycle_cat"].map(jn.CYCLE_RANK)
    j["bezirk"] = j["legs_list"].map(lambda ls: Counter(leg["bezirk"] for leg in ls if leg["bezirk"]).most_common(1)[0][0]
                                     if any(leg["bezirk"] for leg in ls) else None)
    j["names"] = j["legs_list"].map(lambda ls: " / ".join(sorted({leg["name"] for leg in ls if leg["name"]})) or None)
    j["legs"] = j["legs_list"].map(_leg_json)
    j["member_nodes"] = j["members"].map(json.dumps)
    j["n_internal"] = [len(legs[r]["internal"]) for r in roots]

    df = ov.read_overrides(ov.JUNCTION_OVERRIDES_PATH)
    ov.validate_junctions(df, j["node_id"], p.types)
    j = ov.apply_junctions(j, df)

    keep = ["node_id", "member_nodes", "n_members", "extent_m", "n_internal", "legs", "legs_count", "n_carriageway_legs", "pair",
            "entering_dtv_sum", "space_radius_m", "tram_present", "signal_present_ist", "decision_rule",
            "junction_type_soll", "junction_type_final", "junction_type_source", "junction_type_ist", "ist_result",
            "action_needed", "cyclist_treatment", "treatment_text", "conflict_flags", "confidence", "top_cycle_cat",
            "cycle_rank", "crashes_cyc", "crashes_cyc_severe", "bezirk", "names", "rule_trace_junction",
            "junction_override_reason", "junction_override_author", "junction_override_date", "junction_override_source"]
    out = gpd.GeoDataFrame(j[keep], geometry=member_geoms.centroid.to_numpy(), crs=WORK_CRS)
    out["priority_rank"] = np.nan
    act = out[out["action_needed"]].sort_values([*m["J-M-07"]["sort_keys"], "node_id"],
                                                ascending=[False] * len(m["J-M-07"]["sort_keys"]) + [True],
                                                na_position="last")
    out.loc[act.index, "priority_rank"] = np.arange(1, len(act) + 1)
    out.to_parquet(OUT_PATH)

    n6 = pd.read_parquet(N6_PATH, columns=["node", "soll_type"]).dropna(subset=["soll_type"])
    node_to = {n: str(r) for r in roots for n in clusters[r]}
    n6["node_id"] = n6["node"].map(node_to)
    n6 = n6.dropna(subset=["node_id"]).merge(out[["node_id", "junction_type_final"]], on="node_id")
    viewers = load_viewers()
    sample = sample_by_district(out, SAMPLE_SIZE, SAMPLE_SEED, id_col="node_id")
    review_sample(out, viewers).to_csv(REVIEW_PATH, index=False)
    ctx = {"design_version": design.meta.version, "n_nodes": len(pts), "n_deg3": sum(1 for d in deg.values() if d >= 3),
           "n_path_nodes": len(path_nodes), "cluster_radius": radius, "search_radius": search,
           "signal_radius": signal_radius, "order": p.order, "types": p.types, "tram_routes": _tram_routes(design),
           "crash_years": f"{min(years)}–{max(years)}", "top": out.loc[act.index[:TOP_N]], "sample": sample}
    write_report(out, n6, ctx)
    tick(f"wrote {OUT_PATH.relative_to(REPO_ROOT)}, {REPORT_PATH.relative_to(REPO_ROOT)}, {REVIEW_PATH.relative_to(REPO_ROOT)}")
    return 0


def _tram_routes(design) -> int:
    from pipeline.c04_principles import _gtfs_path
    from pipeline.lib import gtfs

    prf02 = next(r for r in design.profile_assignment["rules"] if r["id"] == "PRF-02")
    routes = gtfs.load_feed(_gtfs_path(load_manifest()))["routes"]
    return int(routes["route_type"].astype(int).isin(tuple(prf02["tram_route_types"])).sum())


if __name__ == "__main__":
    sys.exit(main())
