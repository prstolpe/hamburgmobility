"""Cycle stage 3b: Ist cycle facility per segment (rules.yaml S-FEAT-13) and parallel route of the Soll cycle network
(S-FEAT-11). Review 2026-11 F21, F26 (E9).

Usage: uv run python -m pipeline.c03b_ist_facility

Runs after the Soll cycle network (c03) and before c04 (C-PRI-02), c05 (C-FAC-05) and s08 (D-DES-01, D-USE-01), which
all read the result: one Ist facility per segment instead of three definitions. Reads data/interim/final.parquet
(S-FEAT-10 tags, official cycle streets, cat_final) and data/interim/cycle_network.parquet (street edges,
sidepaths, Soll cycle categories). Writes data/interim/ist_facility.parquet (one row per segment_id of final.parquet)
and reports/ist_facility.md with the list of segments whose track rests on the street tag only (track_tag_only).
"""

import datetime as dt
import json
import sys
import time

import geopandas as gpd
import numpy as np
import pandas as pd

from pipeline.c04_principles import _links
from pipeline.lib import facility as fa
from pipeline.lib import ist_facility as ist
from pipeline.lib import principles as pr
from pipeline.lib.area import sample_by_district
from pipeline.lib.links import load_viewers
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_cycling_rules, load_rules

INTERIM = REPO_ROOT / "data" / "interim"
FINAL_PATH = INTERIM / "final.parquet"
NETWORK_PATH = INTERIM / "cycle_network.parquet"
OUT_PATH = INTERIM / "ist_facility.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "ist_facility.md"
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
STREET_LIST_N = 40
FINAL_COLUMNS = ["segment_id", "name", "bezirk", "length_m", "cat_final", "conflated", "fahrradstrasse_official",
                 "cycle_track_tag", "cycle_lane_present", "geometry"]
OUT_COLUMNS = ["cycle_osm_ist", "cycle_facility_ist", "separated_cycle_track_present", ist.TRACK_TAG_ONLY_FLAG,
               "has_sidepath", "parallel_cycle_route_present", "parallel_share", "parallel_level", "parallel_detour",
               "cycle_facility_ist_c_pri_02_old", "rule_trace_ist"]
FACILITY_DE = {"separated_oneway_both": "Radweg je Seite", "separated_twoway": "Zweirichtungsradweg",
               "cycle_lane": "Radfahrstreifen", "cycle_street": "Fahrradstraße", "mixed": "Mischverkehr",
               "own_path": "eigene Trasse", None: "unbekannt"}
CAT_ORDER = ["SW", "GOW80", "GOW50", "GOW30", "ETW60", "ETW30", "ETW_ERF"]


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _fmt(v, digits: int = 0) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "–"
    return f"{v:,.{digits}f}".replace(",", " ")


def old_c_pri_02(net: gpd.GeoDataFrame, segs: pd.Index, pp: pr.PrincipleParams) -> pd.Series:
    """Ist facility per segment as C-PRI-02 computed it until cycling_rules 0.10.0 (for the report only): sidepaths
    -> one-way / two-way track (any two-way sidepath), else the facility of the longest street edge."""
    road = net[(net["kind"] == "road") & net["segment_id"].notna()]
    side = net[(net["kind"] == "path") & net["sidepath_of"].notna()]
    twoway = (side["cost_fwd"].notna() & side["cost_bwd"].notna()).groupby(side["sidepath_of"]).any()
    by_side = twoway.map(lambda t: pp.sidepath_twoway if t else pp.sidepath_oneway)
    longest = road.sort_values("length_m", ascending=False).drop_duplicates("segment_id")
    fac = [pr.ist_facility("road", r, ist._trace_inputs(t).get("cycleway"), None, pp)
           for r, t in zip(longest["imp_rule"], longest["impedance_trace"])]
    by_road = pd.Series(fac, index=longest["segment_id"].to_numpy())
    return by_side.reindex(segs).fillna(by_road.reindex(segs))


def write_report(out: gpd.GeoDataFrame, versions: tuple[str, str], pp: ist.ParallelParams, runtime: dict) -> None:
    viewers = load_viewers()
    area = out[out["cat_final"].notna() & out["conflated"].fillna(False).astype(bool)]
    km = lambda m: area.loc[m, "length_m"].sum() / 1000
    track = area["separated_cycle_track_present"]
    tag = area["cycle_track_tag"]
    tag_only = area[ist.TRACK_TAG_ONLY_FLAG].astype(bool)
    old = area["cycle_facility_ist_c_pri_02_old"]
    differs_old = old.notna() & (old != area["cycle_facility_ist"])
    req = area["cat_final"].isin(pp.categories)
    par = area["parallel_cycle_route_present"].astype(bool)
    lines = [
        "# Ist-Führung und Parallelroute je Abschnitt (Stufe c03b)",
        "",
        f"Erzeugt {_now()} mit pipeline/c03b_ist_facility.py · rules.yaml {versions[0]} · cycling_rules.yaml {versions[1]} · "
        "nicht amtlicher Entwurf. Regeln S-FEAT-13 und S-FEAT-11 (Review 2026-11 F26/E9, F21), source_type assumption, "
        "status draft.",
        "",
        "Eine Ist-Führung je Abschnitt nach den Regeln von C-FAC-05 (Fahrradstraße, Radweg mit begleitenden Radwegen je "
        "Seite, Streifen, Sharrow/Busspur, keine). Die Prinzipienbewertung (c04, C-PRI-02), die Führungsform (c05, "
        "C-FAC-05) und die Diskrepanz (s08, D-DES-01/D-USE-01) lesen sie; bis rules.yaml 0.19.0 gab es drei Definitionen. "
        "`separated_cycle_track_present` = Ist-Führung Radweg je Seite oder Zweirichtungsradweg; unbekannt, wenn die "
        "Ist-Klasse „keine“ nur aus fehlenden OSM-Angaben folgt (S-FEAT-10).",
        "",
        "## Kurzfassung",
        "",
        f"- {_fmt(len(area))} klassifizierte Abschnitte, {_fmt(km(slice(None)), 0)} km. Baulicher Radweg: ja "
        f"{_fmt(km(track == True), 0)} km, nein {_fmt(km(track == False), 0)} km, unbekannt {_fmt(km(track.isna()), 0)} km.",
        f"- Radweg-Tag an der Straße (S-FEAT-10 `cycle_track_tag`), aber weder begleitender Radweg noch Radweg in der "
        f"Straßenlinie im Radgraphen (Flag `{ist.TRACK_TAG_ONLY_FLAG}`): {_fmt(tag_only.sum())} Abschnitte, "
        f"{_fmt(km(tag_only), 1)} km. Sie zählen nach C-FAC-05 überall als Radweg; bis cycling_rules 0.10.0 zählte c04 "
        "sie als Fahrbahnführung. Prüfliste unten.",
        f"- Abweichung von der früheren Radgraph-Definition (C-PRI-02 bis cycling_rules 0.10.0): {_fmt(km(differs_old), 1)} km; "
        f"davon Radweg-Tag ohne Radgraph {_fmt(km(differs_old & tag_only), 1)} km, begleitende Zweirichtungsradwege auf beiden "
        f"Seiten (E9: jetzt Radweg je Seite) {_fmt(km(differs_old & (old == 'separated_twoway') & (area['cycle_facility_ist'] == 'separated_oneway_both')), 1)} km.",
        f"- Abweichung vom Radweg-Tag allein (S-FEAT-10 bis rules.yaml 0.19.0): Tag nein/unbekannt, Ist Radweg "
        f"{_fmt(km((tag != True) & (track == True)), 1)} km (begleitender Radweg im Radgraphen); Tag ja, Ist kein Radweg "
        f"{_fmt(km((tag == True) & (track != True)), 1)} km (Fahrradstraße geht vor).",
        f"- Parallelroute (S-FEAT-11, nur Soll-Radnetz {'/'.join(lv[2] for lv in pp.levels)} mit Umweg ≤ P-DIR-01; geprüft für "
        f"{', '.join(sorted(pp.categories))}): {_fmt(km(req & par), 1)} von {_fmt(km(req), 1)} km; ohne baulichen Radweg "
        f"{_fmt(km(req & par & (track != True)), 1)} von {_fmt(km(req & (track != True)), 1)} km.",
        f"- Laufzeit: Eingänge {runtime['read']:.0f} s, Ist-Führung {runtime['ist']:.0f} s, Parallelroute {runtime['parallel']:.0f} s.",
        "",
        "## km je Ist-Führung und Straßenkategorie",
        "",
    ]
    cats = [c for c in CAT_ORDER if (area["cat_final"] == c).any()]
    facs = list(FACILITY_DE)[:-1]
    lines += ["| Ist-Führung | " + " | ".join(cats) + " | gesamt |", "| --- |" + " ---: |" * (len(cats) + 1)]
    for f in facs:
        vals = [km((area["cycle_facility_ist"] == f) & (area["cat_final"] == c)) for c in cats]
        lines.append(f"| {FACILITY_DE[f]} | " + " | ".join(_fmt(v, 1) for v in vals) + f" | {_fmt(sum(vals), 1)} |")

    lines += ["", "## Frühere Radgraph-Definition (C-PRI-02) gegen S-FEAT-13 (km)", "",
              "Zeilen: Ist-Führung nach C-PRI-02 bis cycling_rules 0.10.0 (begleitende Radwege, sonst längste Straßenkante); "
              "Spalten: S-FEAT-13.", ""]
    ct = area.assign(old_de=old.map(lambda v: FACILITY_DE.get(v, "ohne Kante")),
                     new_de=area["cycle_facility_ist"].map(FACILITY_DE))
    tab = ct.groupby(["old_de", "new_de"])["length_m"].sum().unstack(fill_value=0) / 1000
    cols = [FACILITY_DE[f] for f in facs if FACILITY_DE[f] in tab.columns]
    lines += ["| C-PRI-02 alt | " + " | ".join(cols) + " |", "| --- |" + " ---: |" * len(cols)]
    for r in tab.index:
        lines.append(f"| {r} | " + " | ".join(_fmt(tab.at[r, c], 1) for c in cols) + " |")

    lst = area[tag_only].copy()
    lst["name"] = lst["name"].fillna("(ohne Namen)")
    lines += ["", f"## Prüfliste: Radweg-Tag ohne Radweg im Radgraphen (`{ist.TRACK_TAG_ONLY_FLAG}`)", "",
              "OSM trägt an der Straße einen Radweg (cycleway*=track|separate oder bicycle=use_sidepath), der Radgraph hat "
              "aber keinen begleitenden Radweg (sidepath_of) und keinen Radweg in der Straßenlinie; die Straßenkante "
              "hat einen Widerstand für Fahrbahnführung (C-IMP-04…07). Für Diskrepanz, Prinzipien und Führungsform gilt "
              "der Radweg (C-FAC-05); der Widerstand im Radgraphen (c01) bleibt unverändert. Tags prüfen oder den "
              "begleitenden Radweg in OSM ergänzen (docs/open_questions.md).", "",
              "km je Straßenkategorie: " + ", ".join(f"{c} {_fmt(km(tag_only & (area['cat_final'] == c)), 1)}" for c in cats), "",
              f"### Längste {STREET_LIST_N} Straßen (je Straße und Bezirk zusammengefasst)", "",
              "| Straße | Bezirk | Kategorie | Abschnitte | km |", "| --- | --- | --- | ---: | ---: |"]
    agg = (lst.groupby(["name", "bezirk", "cat_final"], dropna=False)["length_m"].agg(["count", "sum"])
           .sort_values("sum", ascending=False).head(STREET_LIST_N))
    for (name, bez, cat), r in agg.iterrows():
        lines.append(f"| {name} | {bez} | {cat} | {int(r['count'])} | {_fmt(r['sum'] / 1000, 2)} |")
    lines += ["", "Vollständige Liste: `data/interim/ist_facility.parquet`, Spalte `track_tag_only`.", ""]

    lines += [f"### Stichproben ({SAMPLE_SIZE}, über Bezirke verteilt, Seed {SAMPLE_SEED})", "",
              "| segment_id | Straße | Bezirk | Kategorie | C-PRI-02 alt | Prüfen |", "| --- | --- | --- | --- | --- | --- |"]
    if not lst.empty:
        for r in sample_by_district(lst.reset_index(), SAMPLE_SIZE, SAMPLE_SEED).itertuples():
            lines.append(f"| `{r.segment_id}` | {r.name} | {r.bezirk} | {r.cat_final} | "
                         f"{FACILITY_DE.get(r.cycle_facility_ist_c_pri_02_old, 'ohne Kante')} | {_links(r.geometry, viewers)} |")

    pl = area[req & par & (track != True)]
    lines += ["", "## Parallelroute an Abschnitten ohne baulichen Radweg (S-FEAT-11)", "",
              "D-DES-01 zählt „kein baulicher Radweg“ dort nur mit dem Gewicht 0,5 (severity_if); die Soll-Führung (C-FAC-01) "
              "bleibt Radweg, Flag `parallel_cycle_route` in c05.", "",
              "km je Ebene: " + ", ".join(f"bis {lv[2]} (P-DIR-01 ≤ {lv[1]:g}) {_fmt(km(req & par & (track != True) & (area['parallel_level'] == lv[2])), 1)}"
                                          for lv in pp.levels), "",
              f"### Stichproben ({SAMPLE_SIZE}, über Bezirke verteilt, Seed {SAMPLE_SEED})", "",
              "| segment_id | Straße | Bezirk | Ebene | Umweg | Anteil im Puffer | Prüfen |",
              "| --- | --- | --- | --- | ---: | ---: | --- |"]
    if not pl.empty:
        for r in sample_by_district(pl.reset_index(), SAMPLE_SIZE, SAMPLE_SEED).itertuples():
            lines.append(f"| `{r.segment_id}` | {r.name if isinstance(r.name, str) else '–'} | {r.bezirk} | {r.parallel_level} | "
                         f"{_fmt(r.parallel_detour, 2)} | {_fmt(r.parallel_share, 2)} | {_links(r.geometry, viewers)} |")
    lines += ["", "## Grenzen", "",
              "- Begleitende Radwege und ihre Seite kommen aus dem Radgraphen (C-GRAPH-06); fehlt die Zuordnung, entscheidet "
              "der Tag an der Straße.",
              "- Parallelroute: Netzweg zwischen den Lotfußpunkten der Abschnittsenden auf den Soll-Kanten der Ebene, ohne "
              "Zu- und Abfahrt; sehr kurze Abschnitte werden damit eher großzügig bewertet.",
              "- Ohne jede OSM-Angabe bleibt `separated_cycle_track_present` unbekannt (S-FEAT-10), die Ist-Führung ist "
              "Mischverkehr (C-FAC-05).",
              "",
              "Quellen: OpenStreetMap-Mitwirkende (ODbL); Freie und Hansestadt Hamburg, Fahrradstraßen (dl-de/by-2.0).", ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rules, cyc = load_rules(), load_cycling_rules()
    for path, step in ((NETWORK_PATH, "make cycle-network"), (FINAL_PATH, "make coherence")):
        if not path.exists():
            print(f"ist-facility: {path.relative_to(REPO_ROOT)} missing; run `{step}` first", file=sys.stderr)
            return 1
    t0 = time.perf_counter()
    runtime = {}
    final = gpd.read_parquet(FINAL_PATH, columns=FINAL_COLUMNS).set_index("segment_id")
    net = gpd.read_parquet(NETWORK_PATH)
    runtime["read"] = time.perf_counter() - t0

    p = fa.FacilityParams.from_rules(cyc, rules)
    track_facilities = frozenset(rules.features.rule("S-FEAT-13").track_facilities)
    graph = ist.segment_graph_inputs(final.geometry, net)
    res = ist.ist_frame(final, graph, p, track_facilities)
    res["has_sidepath"] = graph["has_sidepath"].reindex(res.index).fillna(False).astype(bool)
    res["cycle_facility_ist_c_pri_02_old"] = old_c_pri_02(net, res.index, pr.PrincipleParams.from_rules(cyc, rules))
    t1 = time.perf_counter()
    runtime["ist"] = t1 - t0 - runtime["read"]
    print(f"ist-facility: S-FEAT-13 for {len(res)} segments ({runtime['ist']:.0f} s)")

    pp = ist.ParallelParams.from_rules(rules, cyc)
    cand = final[final["cat_final"].isin(pp.categories) & final["conflated"].fillna(False).astype(bool)]
    par = ist.parallel_routes(cand[["geometry"]], net, final["name"], pp)
    res = res.join(par)
    res["parallel_cycle_route_present"] = res["parallel_cycle_route_present"].astype(object).where(
        res.index.isin(cand.index), None)
    runtime["parallel"] = time.perf_counter() - t1
    print(f"ist-facility: S-FEAT-11 for {len(cand)} segments ({runtime['parallel']:.0f} s)")

    traces = []
    for seg, r in res.iterrows():
        par_step = {"id": "S-FEAT-11", "result": r["parallel_cycle_route_present"], "values": {
            "share": None if pd.isna(r["parallel_share"]) else round(float(r["parallel_share"]), 3),
            "level": r["parallel_level"] if isinstance(r["parallel_level"], str) else None,
            "detour": None if pd.isna(r["parallel_detour"]) else round(float(r["parallel_detour"]), 3)}}
        traces.append(json.dumps([r["trace"], par_step], ensure_ascii=False, default=str))
    res["rule_trace_ist"] = traces
    res = res[OUT_COLUMNS]
    res.reset_index().to_parquet(OUT_PATH, index=False)
    rep = final.join(res)
    write_report(gpd.GeoDataFrame(rep, geometry="geometry", crs=final.crs), (rules.meta.version, cyc.meta.version), pp, runtime)
    print(f"ist-facility: -> {OUT_PATH.relative_to(REPO_ROOT)}, {REPORT_PATH.relative_to(REPO_ROOT)} "
          f"({time.perf_counter() - t0:.0f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
