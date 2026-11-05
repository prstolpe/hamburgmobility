"""Stage 6: network coherence N1–N7 on the graph of proposed categories (guide 1.5, 3.2 Stufe 6, prompts/09).

Usage: uv run python -m pipeline.s06_coherence

Reads data/interim/harmonised.parquet, config/rules.yaml (coherence) and the OSM extract (city boundary,
traffic signals, traffic_calming=table, roundabouts). Writes data/interim/coherence.parquet (input columns plus
flags and coherence_trace as JSON), data/interim/coherence_nodes.parquet (N5/N6 per node),
data/interim/coherence_areas.parquet (N3), reports/coherence.md, reports/coherence_flags.geojson.
Nothing is reclassified: cat_proposed is unchanged, smoothing proposals are N7 flags.
The run stops with exit code 1 if a check fails; outputs are then not written.
"""

import json
import sys
import warnings
from collections import Counter

import geopandas as gpd
import pandas as pd

from pipeline.lib import coherence as coh
from pipeline.lib.area import NO_DISTRICT, area_label, district_names, load_area_config, read_work_area, sample_by_district
from pipeline.lib.crs import WORK_CRS, to_work_crs
from pipeline.lib.links import load_viewers, orthophoto_link, osm_way_link, panoramax_link
from pipeline.lib.manifest import REPO_ROOT, load_manifest
from pipeline.lib.rules import load_rules
from pipeline.s02_network import _pbf_from_manifest
from pipeline.s04_features import OSM_BBOX_MARGIN_DEG, _fmt, _now, _pct

IN_PATH = REPO_ROOT / "data" / "interim" / "harmonised.parquet"
OUT_PATH = REPO_ROOT / "data" / "interim" / "coherence.parquet"
NODES_PATH = REPO_ROOT / "data" / "interim" / "coherence_nodes.parquet"
AREAS_PATH = REPO_ROOT / "data" / "interim" / "coherence_areas.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "coherence.md"
GEOJSON_PATH = REPO_ROOT / "reports" / "coherence_flags.geojson"
CITY_NAME = "Hamburg"
CITY_ADMIN_LEVEL = "4"
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
RULE_LABELS = {
    "N1": "Durchgängigkeit (GOW-Zug endet ohne Anschluss)",
    "N2": "Kurze Kategorie-Insel",
    "N3": "Kleiner Aufenthaltsbereich",
    "N4": "Schleichverkehr über ETW",
    "N5": "Direkter Übergang ≥ 70 → 30",
    "N6": "Knotentyp Soll ≠ Ist",
    "N7": "Glättungsvorschlag",
}


# --- inputs ----------------------------------------------------------------------------------


def read_osm_inputs(pbf, work_area) -> dict:
    """City boundary (admin_level 4), traffic signals, plateaus and roundabout way ids."""
    from pyrosm import OSM

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        b = OSM(str(pbf)).get_boundaries(boundary_type="administrative")
        city = b[(b["name"] == CITY_NAME) & (b["admin_level"].astype(str) == CITY_ADMIN_LEVEL)]
        if len(city) != 1:
            raise RuntimeError(f"{len(city)} OSM boundaries {CITY_NAME} admin_level {CITY_ADMIN_LEVEL}; expected 1")
        wgs = gpd.GeoSeries([work_area], crs=WORK_CRS).to_crs(4326).iloc[0]
        osm = OSM(str(pbf), bounding_box=wgs.buffer(OSM_BBOX_MARGIN_DEG))
        kw = dict(filter_type="keep", keep_nodes=True, keep_ways=False, keep_relations=False)
        signals = osm.get_data_by_custom_criteria(custom_filter={"highway": ["traffic_signals"]}, **kw)
        tables = osm.get_data_by_custom_criteria(custom_filter={"traffic_calming": ["table"]}, **kw)
        rb = osm.get_data_by_custom_criteria(custom_filter={"junction": ["roundabout", "circular"]},
                                             filter_type="keep", keep_nodes=False, keep_ways=True, keep_relations=False)
    return {"city": to_work_crs(city).geometry.iloc[0],
            "signals": to_work_crs(signals).geometry.reset_index(drop=True),
            "tables": to_work_crs(tables).geometry.reset_index(drop=True),
            "roundabout_ways": set() if rb is None else {int(i) for i in rb["id"]}}


def area_edge_nodes(seg_all: pd.DataFrame) -> set:
    """Nodes where a classified segment meets a segment outside the work area."""
    inside = seg_all["conflated"].astype(bool)
    n_in = set(seg_all.loc[inside, "node_u"]) | set(seg_all.loc[inside, "node_v"])
    n_out = set(seg_all.loc[~inside, "node_u"]) | set(seg_all.loc[~inside, "node_v"])
    return n_in & n_out


def roundabout_nodes(seg: pd.DataFrame, way_ids: set) -> set:
    hit = seg["osm_way_ids"].map(lambda ws: any(int(w) in way_ids for w in ws))
    return set(seg.loc[hit, "node_u"]) | set(seg.loc[hit, "node_v"])


# --- computation -----------------------------------------------------------------------------


def compute(inp: gpd.GeoDataFrame, rules, osm: dict, work_area) -> dict:
    in_area = inp["conflated"].astype(bool)
    seg = inp.loc[in_area, ["segment_id", "node_u", "node_v", "cat_proposed", "length_m", "highway",
                            "travel_speed_kmh", "osm_way_ids", "geometry"]].rename(columns={"cat_proposed": "cat"})
    g = coh.build_graph(seg, rules)
    n1, ends = coh.n1_dead_ends(g, rules, area_edge_nodes(inp), osm["city"].boundary)
    n2 = coh.n2_islands(g, rules)
    areas, n3 = coh.n3_areas(seg, rules, work_area=work_area, city_area=osm["city"])
    n4, n4_stats = coh.n4_shortcuts(g, rules)
    n5, n5_nodes = coh.n5_transitions(g, rules)
    points = gpd.GeoSeries({n: d["point"] for n, d in g.nodes(data=True)}, crs=WORK_CRS)
    ist = coh.ist_node_types(points, osm["signals"], osm["tables"], roundabout_nodes(seg, osm["roundabout_ways"]),
                             rules.coherence_rule("N6").param("signal_radius_m"))
    n6, n6_nodes = coh.n6_node_types(g, rules, ist)
    flags = coh.merge_flags(n1, n2, n3, n4, n5, n6)

    out = inp.copy()
    out["flags"] = None
    out["coherence_trace"] = None
    out.loc[in_area, "flags"] = out.loc[in_area, "segment_id"].map(
        lambda s: json.dumps(list(dict.fromkeys(f["flag"] for f in flags.get(s, [])))))
    out.loc[in_area, "coherence_trace"] = out.loc[in_area, "segment_id"].map(
        lambda s: json.dumps(flags.get(s, []), ensure_ascii=False))

    nodes = pd.DataFrame(n6_nodes, columns=["node", "pair", "soll_type", "ist_type", "result"]).merge(
        pd.DataFrame(n5_nodes, columns=["node", "gates", "direct_to_30"]), on="node", how="outer")
    nodes["pair"] = nodes["pair"].map(lambda v: json.dumps(v) if isinstance(v, list) else None)
    nodes["gates"] = nodes["gates"].map(lambda v: json.dumps(v) if isinstance(v, list) else "[]")
    nodes["direct_to_30"] = nodes["direct_to_30"].fillna(False).astype(bool)
    nodes = gpd.GeoDataFrame(nodes, geometry=nodes["node"].map(points.to_dict()), crs=WORK_CRS)
    return {"out": out, "flags": flags, "ends": pd.DataFrame(ends), "areas": areas, "nodes": nodes,
            "n4": n4_stats, "graph": g}


# --- checks ----------------------------------------------------------------------------------


def run_checks(inp: pd.DataFrame, out: pd.DataFrame, rules) -> list[dict]:
    area = out["conflated"].astype(bool)
    known = {r.id for r in rules.coherence}
    traces = out.loc[area, "coherence_trace"].map(json.loads)
    ids_ok = all(isinstance(t, list) and all(f["id"] in known for f in t) for t in traces)
    same_cat = out["cat_proposed"].fillna("–").equals(inp["cat_proposed"].fillna("–"))
    return [
        {"name": "segment_id unverändert", "ok": list(out["segment_id"]) == list(inp["segment_id"]),
         "detail": f"{len(out)} Abschnitte"},
        {"name": "cat_proposed unverändert (keine Umklassifizierung)", "ok": same_cat, "detail": "Vergleich mit Eingabe"},
        {"name": "flags nur im Arbeitsgebiet, gültiges JSON mit bekannten Regel-IDs", "ok":
         ids_ok and out.loc[~area, "flags"].isna().all(), "detail": ", ".join(sorted(known))},
    ]


# --- report ----------------------------------------------------------------------------------


def _km(x: float) -> str:
    return f"{x / 1000:.1f}"


def _name(v) -> str:
    return v if isinstance(v, str) and v else "–"


def flag_table(out: pd.DataFrame, districts: list[str]) -> pd.DataFrame:
    """One row per (segment, rule) with length and Bezirk."""
    area = out[out["conflated"].astype(bool)]
    rows = []
    for r in area.itertuples(index=False):
        for rid in dict.fromkeys(f["id"] for f in json.loads(r.coherence_trace)):
            rows.append({"segment_id": r.segment_id, "rule": rid, "length_m": r.length_m,
                         "bezirk": r.bezirk if isinstance(r.bezirk, str) else NO_DISTRICT,
                         "pilot": r.bezirk in districts})
    return pd.DataFrame(rows, columns=["segment_id", "rule", "length_m", "bezirk", "pilot"])


def pick_sample(out: gpd.GeoDataFrame, districts: list[str]) -> gpd.GeoDataFrame:
    pilot = out[out["conflated"].astype(bool) & out["bezirk"].isin(districts)]
    flagged = pilot[pilot["flags"].map(lambda f: f not in (None, "[]"))]
    return sample_by_district(flagged, SAMPLE_SIZE, SAMPLE_SEED)


def _points(geom):
    mid = geom.interpolate(0.5, normalized=True)
    return mid, gpd.GeoSeries([mid], crs=WORK_CRS).to_crs(4326).iloc[0]


def write_geojson(res: dict) -> None:
    out = res["out"]
    seg = out[out["flags"].map(lambda f: f not in (None, "[]"))]
    parts = [gpd.GeoDataFrame({"layer": "segment", "segment_id": seg["segment_id"], "cat": seg["cat_proposed"],
                               "name": seg["name"], "rule": seg["coherence_trace"].map(
                                   lambda t: ",".join(dict.fromkeys(f["id"] for f in json.loads(t)))),
                               "flags": seg["flags"]}, geometry=seg.geometry, crs=WORK_CRS)]
    nodes = res["nodes"]
    bad = nodes[(nodes["result"] == "mismatch") | nodes["direct_to_30"]]
    parts.append(gpd.GeoDataFrame({"layer": "node", "node": bad["node"], "rule": bad.apply(
        lambda r: ",".join([x for x, on in (("N5", r["direct_to_30"]), ("N6", r["result"] == "mismatch")) if on]), axis=1),
        "soll_type": bad["soll_type"], "ist_type": bad["ist_type"]}, geometry=bad.geometry, crs=WORK_CRS))
    areas = res["areas"]
    small = areas[areas["small"] & areas["complete"]]
    parts.append(gpd.GeoDataFrame({"layer": "area", "rule": "N3", "area_id": small["area_id"],
                                   "area_ha": small["area_ha"].round(2)}, geometry=small.geometry, crs=WORK_CRS))
    gj = pd.concat(parts, ignore_index=True).to_crs(4326)
    GEOJSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    gj.to_file(GEOJSON_PATH, driver="GeoJSON", COORDINATE_PRECISION=6)


def write_report(res: dict, ctx: dict, checks: list[dict]) -> None:
    rules, pilot_name, out = ctx["rules"], ctx["pilot"], res["out"]
    area = out[out["conflated"].astype(bool)]
    ft = flag_table(out, ctx["districts"])
    cats = list(rules.categories)
    p = {r.id: r for r in rules.coherence}
    lines = [
        "# Kohärenzbericht – Stufe 6", "",
        f"Erzeugt: {_now()} von `pipeline/s06_coherence.py`, rules.yaml {rules.meta.version}. Nicht amtlicher Entwurf: "
        "Die Regeln markieren nur; nichts wird umklassifiziert. Entscheidungen über overrides/overrides.csv.", "",
        "## Kennzahlen", "",
        f"- Geprüft: {_fmt(len(area))} Abschnitte im Arbeitsgebiet ({_km(area['length_m'].sum())} km), "
        f"{_fmt(res['graph'].number_of_nodes())} Knoten. Knoten = OSM-Knoten; getrennte Richtungsfahrbahnen sind nicht "
        "zusammengefasst (mehrere Knoten je Kreuzung).",
        f"- Abschnitte mit mindestens einem Flag: {_fmt(area['flags'].map(lambda f: f != '[]').sum())}.", "",
        f"| Regel | Bedeutung | Abschnitte (Arbeitsgebiet) | km | Abschnitte {pilot_name} | km {pilot_name} |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for rid, label in RULE_LABELS.items():
        f = ft[ft["rule"] == rid]
        fp = f[f["pilot"]]
        lines.append(f"| {rid} | {label} | {_fmt(len(f))} | {_km(f['length_m'].sum())} | {_fmt(len(fp))} | "
                     f"{_km(fp['length_m'].sum())} |")
    rule_ids = list(RULE_LABELS)
    lines += ["", "km mit Flag je Bezirk und Regel:", "", "| Bezirk | km geprüft | " + " | ".join(rule_ids) + " |",
              "| --- | ---: |" + " ---: |" * len(rule_ids)]
    bez_all = area["bezirk"].fillna(NO_DISTRICT)
    for bz in sorted(bez_all.unique(), key=lambda b: (b == NO_DISTRICT, b)):
        f = ft[ft["bezirk"] == bz]
        km = f.groupby("rule")["length_m"].sum()
        lines.append(f"| {bz} | {_km(area.loc[bez_all == bz, 'length_m'].sum())} | "
                     + " | ".join(_km(km.get(r, 0.0)) for r in rule_ids) + " |")
    lines += ["", "Karte: `reports/coherence_flags.geojson` (EPSG:4326; Ebenen segment, node, area; Eigenschaft `rule`), "
              "z. B. in QGIS oder geojson.io öffnen.", "",
              "## Prüfungen", "", "| Prüfung | Ergebnis | Detail |", "| --- | --- | --- |",
              *[f"| {c['name']} | {'ok' if c['ok'] else 'FEHLER'} | {c['detail']} |" for c in checks]]

    ends = res["ends"]
    st = ends["status"].value_counts() if not ends.empty else pd.Series(dtype=int)
    lines += ["", "## N1 Durchgängigkeit", "",
              f"Enden von GOW-Zügen ({', '.join(p['N1'].gow_categories)}): Knoten mit genau einem GOW-Abschnitt. "
              f"In Ordnung, wenn dort {', '.join(p['N1'].end_ok_categories)} anschließt oder die Stadtgrenze höchstens "
              f"{p['N1'].param('boundary_tolerance_m'):g} m entfernt ist; am Rand des Arbeitsgebiets nicht prüfbar.", "",
              "| Status | Enden |", "| --- | ---: |",
              *[f"| {k} | {_fmt(st.get(k, 0))} |" for k in ("ok_sw", "ok_city_boundary", "unknown_area_edge", "dead_end")]]
    dead = ends[ends["status"] == "dead_end"] if not ends.empty else ends
    if not dead.empty:
        d = area.set_index("segment_id").loc[dead["segment_id"]]
        by = d.assign(name=d["name"].map(_name)).groupby(["name", "cat_proposed"]).size().sort_values(ascending=False)
        lines += ["", "Häufigste Straßen mit offenem GOW-Ende:", "", "| Name | Kategorie | Enden |", "| --- | --- | ---: |",
                  *[f"| {n} | {c} | {v} |" for (n, c), v in by.head(15).items()]]

    n2 = ft[ft["rule"] == "N2"]
    smooth = Counter(f["flag"].split(":")[1] + " ← " + f["inputs"]["current"]
                     for t in area["coherence_trace"] for f in json.loads(t) if f["id"] == "N7")
    lines += ["", "## N2 Kategorie-Inseln und N7 Glättungsvorschläge", "",
              f"Straßenzug: an Knoten mit Grad 2 immer weiter, an Kreuzungen zum gegenseitig besten Abschnitt mit höchstens "
              f"{p['N2'].param('max_deflection_deg'):g}° Richtungsänderung. Insel = Lauf einer Kategorie unter "
              f"{p['N2'].param('min_run_m'):g} m zwischen zwei Läufen gleicher anderer Kategorie. "
              f"{_fmt(len(n2))} Abschnitte ({_km(n2['length_m'].sum())} km).", "",
              "| Vorschlag (N7) neu ← bisher | Abschnitte |", "| --- | ---: |",
              *[f"| {k} | {v} |" for k, v in smooth.most_common()]]

    areas = res["areas"]
    resid = areas[areas["has_etw"]]
    comp = resid[resid["complete"]]
    small = comp[comp["small"]]
    lines += ["", "## N3 Aufenthaltsbereiche", "",
              f"Flächen aus GOW/SW-Linien und Stadtgrenze innerhalb des Arbeitsgebiets: {len(areas)}. Davon enthalten "
              f"{len(resid)} mindestens einen ETW-Abschnitt (Aufenthaltsbereiche); die übrigen {len(areas) - len(resid)} "
              f"sind Verkehrsinseln zwischen Richtungsfahrbahnen oder Grünflächen ohne Erschließung und werden nicht "
              f"bewertet. Vollständig (berühren den Rand des Arbeitsgebiets nicht): {len(comp)}; davon unter "
              f"{p['N3'].param('min_area_ha'):g} ha: {len(small)} mit {_fmt((ft['rule'] == 'N3').sum())} ETW-Abschnitten. "
              "Kompaktheit = 4π·Fläche/Umfang² (1 = Kreis); dafür gibt es noch keine Schwelle (docs/open_questions.md).", "",
              "| Fläche | ha | Umfang m | Kompaktheit | ETW-Abschnitte | vollständig | unter Schwelle |",
              "| ---: | ---: | ---: | ---: | ---: | --- | --- |",
              *[f"| {int(r.area_id)} | {r.area_ha:.1f} | {r.perimeter_m:.0f} | {r.compactness:.2f} | {r.n_etw_segments} | "
                f"{'ja' if r.complete else 'nein'} | {'ja' if r.small and r.complete else 'nein'} |"
                for r in resid.sort_values("area_ha").itertuples()]]

    s = res["n4"]
    n4 = ft[ft["rule"] == "N4"]
    n4_counts = [f["inputs"]["n_od_pairs"] for fl in res["flags"].values() for f in fl if f["id"] == "N4"]
    top = sorted(((f["inputs"]["n_od_pairs"], sid) for sid, fl in res["flags"].items() for f in fl if f["id"] == "N4"),
                 reverse=True)[:15]
    seg_by_id = area.set_index("segment_id")
    md = s["median_detour_factor"]
    lines += ["", "## N4 Schleichverkehr", "",
              f"OD-Knoten: alle {_fmt(s['od_nodes'])} Knoten des GOW/SW-Netzes ({', '.join(p['N4'].restricted_categories)}) "
              f"im Arbeitsgebiet; OD-Paare (ungerichtet, verbunden): {_fmt(s['od_pairs'])}. Reisezeit mit Soll-Tempo je "
              f"Kategorie, SW mit travel_speed_kmh; {', '.join(p['N4'].exclude_highway)} gesperrt; ohne Einbahnstraßen "
              "(Abschnitte tragen keine Richtung). Wege nur innerhalb des Arbeitsgebiets.", "",
              f"- OD-Paare, deren kürzester Weg mehr als {p['N4'].param('max_etw_m'):g} m ETW nutzt: {_fmt(s['flagged_pairs'])} "
              f"({_pct(s['flagged_pairs'] / s['od_pairs']) if s['od_pairs'] else '–'}), obwohl ein Weg nur auf GOW/SW "
              "besteht.",
              f"- Weitere {_fmt(s['etw_only_pairs'])} OD-Paare sind nur über ETW verbunden (Lücke im GOW/SW-Netz, siehe N1); "
              "sie werden gezählt, aber nicht als Schleichverkehr markiert.",
              f"- Median Umwegfaktor (Zeit GOW/SW-Weg ÷ kürzester Weg) dieser Paare: {md:.2f}." if md else "- Umwegfaktor: –",
              f"- Markierte ETW-Abschnitte: {_fmt(len(n4))} ({_km(n4['length_m'].sum())} km). Verteilung der OD-Paare je "
              "Abschnitt: " + ", ".join(f"{label}: {_fmt(sum(1 for n in n4_counts if lo <= n <= hi))}" for label, lo, hi in
                                       (("1–99", 1, 99), ("100–999", 100, 999), ("1 000–9 999", 1000, 9999),
                                        ("≥ 10 000", 10000, float("inf")))) + ".",
              "- GOW30 und ETW30 haben dasselbe Soll-Tempo; jeder kürzere Weg durch ETW gewinnt dann. Die Zahl ist "
              "deshalb ein Maß für die Durchlässigkeit der Quartiere, kein Verkehrsmodell.", "",
              "Meistgenutzte ETW-Abschnitte:", "", "| segment_id | Name | Kategorie | OD-Paare |", "| --- | --- | --- | ---: |",
              *[f"| `{sid}` | {_name(seg_by_id.loc[sid, 'name'])} | {seg_by_id.loc[sid, 'cat_proposed']} | {_fmt(n)} |"
                for n, sid in top]]

    nodes = res["nodes"]
    gates = Counter(tuple(x) for gs in nodes["gates"] for x in json.loads(gs))
    lines += ["", "## N5 Übergänge", "",
              "Übergänge, die eine Torsituation brauchen, je Kategoriepaar (Knoten). Ob eine Torsituation vorhanden ist, "
              "lässt sich aus den Daten nicht ablesen; die Liste dient der Durchsicht.", "",
              "| von → nach | Knoten |", "| --- | ---: |", *[f"| {a} → {b} | {_fmt(v)} |" for (a, b), v in gates.most_common()],
              "", f"Direkter Übergang ≥ {p['N5'].param('min_speed_kmh'):g} km/h → {p['N5'].param('target_speed_kmh'):g}-km/h-Kategorie "
              f"(Flag auf der 30-Seite): {_fmt(int(nodes['direct_to_30'].sum()))} Knoten, "
              f"{_fmt((ft['rule'] == 'N5').sum())} Abschnitte."]

    n6 = nodes[nodes["soll_type"].notna()]
    xt = pd.crosstab(n6["soll_type"], n6["ist_type"])
    res_ct = n6["result"].value_counts()
    lines += ["", "## N6 Knotentypen", "",
              f"Knoten mit Grad ≥ 3: {_fmt(len(n6))}. Ergebnis: " + ", ".join(f"{k} {_fmt(v)}" for k, v in res_ct.items()) + ". "
              f"Ist aus OSM ({_fmt(ctx['n_signals'])} Ampelknoten, {_fmt(ctx['n_tables'])} Plateaus, "
              f"{_fmt(ctx['n_roundabouts'])} Kreisverkehrs-Ways im Umkreis {p['N6'].param('signal_radius_m'):g} m); "
              "none_mapped = nichts davon erfasst. Gehwegüberfahrten sind in OSM nicht erfasst → not_checkable. "
              "Eine Ampel im Umkreis kann zur Nachbarkreuzung gehören (v. a. bei ETW-Knoten nahe einer Hauptstraße); "
              "Kreisverkehre haben mehrere Knoten.", "",
              "| Soll \\ Ist | " + " | ".join(xt.columns) + " |", "| --- |" + " ---: |" * len(xt.columns),
              *[f"| {i} | " + " | ".join(_fmt(v) for v in row) + " |" for i, row in xt.iterrows()]]
    mm = n6[n6["result"] == "mismatch"].groupby(["soll_type", "ist_type"]).size().sort_values(ascending=False)
    lines += ["", "Abweichungen Soll ≠ Ist:", "", "| Soll | Ist | Knoten |", "| --- | --- | ---: |",
              *[f"| {a} | {b} | {_fmt(v)} |" for (a, b), v in mm.items()]]
    nd = n6[n6["soll_type"] == "not_defined"]["pair"].value_counts()
    lines += ["", "Kategoriepaare ohne Soll-Knotentyp (Tabelle 1.4 deckt sie nicht ab): " +
              (", ".join(f"{', '.join(json.loads(k))} ({v})" for k, v in nd.items()) or "keine") + "."]

    sample, viewers = ctx["sample"], ctx["viewers"]
    lines += ["", f"## Stichprobe: {len(sample)} zufällige markierte Abschnitte in {pilot_name}, nach Bezirk geschichtet (Seed {SAMPLE_SEED})", "",
              "Fachlich durchsehen: Ist das Flag berechtigt? **Durchsicht: offen.**", "",
              "| segment_id | Bezirk | Name | Kategorie | m | Flags | Orthophoto | Panoramax | OSM |",
              "| --- | --- | --- | --- | ---: | --- | --- | --- | --- |"]
    for _, r in sample.iterrows():
        work, wgs = _points(r.geometry)
        lines.append(f"| `{r['segment_id']}` | {r['bezirk']} | {_name(r['name'])} | {r['cat_proposed']} | {r['length_m']:.0f} | "
                     f"{', '.join(json.loads(r['flags']))} | [DOP]({orthophoto_link(work, viewers)}) | "
                     f"[Bilder]({panoramax_link(wgs, viewers)}) | [Way]({osm_way_link(r['osm_way_ids'][0])}) |")
    lines += ["", "## Grenzen", "",
              "- Alle Parameter mit source_type assumption (rules.yaml coherence, thresholds) sind fachlich freizugeben.",
              f"- Wege, Flächen und Knoten nur im Arbeitsgebiet ({pilot_name} + Puffer, ohne Neuwerk); Randeffekte sind ausgewiesen.",
              "- Ungerichteter Graph; Abbiegeverbote, Einbahnstraßen und Zufahrtsbeschränkungen fehlen (N4).",
              "- N3 berücksichtigt keine Barrieren wie Bahn, Gewässer oder Parks.", "",
              "## Lizenz", "",
              "Netz, Ampeln, Plateaus, Kreisverkehre, Stadtgrenze: © OpenStreetMap-Beitragende, ODbL 1.0; "
              "Kategorien beruhen auf amtlichen Daten der Freien und Hansestadt Hamburg, dl-de/by-2.0 (siehe "
              "reports/classification.md). Orthophotos: LGV Hamburg, dl-de/by-2.0.", ""]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# --- main ------------------------------------------------------------------------------------


def main() -> int:
    rules = load_rules()
    cfg = load_area_config()
    names = district_names()
    if not IN_PATH.exists():
        print("coherence: data/interim/harmonised.parquet missing; run `make classify` first", file=sys.stderr)
        return 1
    try:
        pbf = _pbf_from_manifest(load_manifest())
    except FileNotFoundError as e:
        print(f"coherence: {e}", file=sys.stderr)
        return 1
    inp = gpd.read_parquet(IN_PATH)
    work_area = read_work_area(cfg)
    print("coherence: reading OSM extract")
    osm = read_osm_inputs(REPO_ROOT / pbf["path"], work_area)
    print(f"coherence: {len(osm['signals'])} signals, {len(osm['tables'])} tables, "
          f"{len(osm['roundabout_ways'])} roundabout ways")
    res = compute(inp, rules, osm, work_area)
    checks = run_checks(inp, res["out"], rules)
    ctx = {"rules": rules, "pilot": area_label(names), "districts": names, "viewers": load_viewers(),
           "sample": pick_sample(res["out"], names), "n_signals": len(osm["signals"]),
           "n_tables": len(osm["tables"]), "n_roundabouts": len(osm["roundabout_ways"])}
    write_report(res, ctx, checks)
    for c in checks:
        print(f"coherence: {c['name']}: {c['ok']} ({c['detail']})")
    if not all(c["ok"] for c in checks):
        print(f"coherence: check(s) failed, outputs not written; see {REPORT_PATH}", file=sys.stderr)
        return 1
    write_geojson(res)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    res["out"].to_parquet(OUT_PATH, index=False)
    res["nodes"].to_parquet(NODES_PATH, index=False)
    res["areas"].to_parquet(AREAS_PATH, index=False)
    counts = Counter(f["id"] for fl in res["flags"].values() for f in fl)
    print("coherence: flags per rule: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print(f"coherence: -> {OUT_PATH.relative_to(REPO_ROOT)}, {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
