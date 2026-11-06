"""Cycle stage 5: target cycle facility and width per street segment (prompts/18_cycle_facility.md).

Usage: uv run python -m pipeline.c05_facility

Rules C-FAC-01..07 (config/cycling_rules.yaml `facility_assignment`) on top of separation_matrix, cycle_street,
S-04 and widths_m. The fallback of a matrix cell is decided in prompt 19 (space); until then the preferred
facility stays and the flag fallback_check_p19 is set. Writes data/interim/cycle_facility.parquet (one row per
segment_id of final.parquet) and reports/cycle_facility.md.
"""

import datetime as dt
import json
import sys
import time

import geopandas as gpd
import numpy as np
import pandas as pd

from config.schema.cycling_model import FACILITIES, NO_CYCLE_CATEGORY, CyclingRuleSet
from pipeline.c04_principles import _links, edge_width, read_way_tags
from pipeline.lib import facility as fa
from pipeline.lib.area import sample_by_district
from pipeline.lib.links import load_viewers
from pipeline.lib.manifest import REPO_ROOT, load_manifest
from pipeline.lib.report import district_breakdown
from pipeline.lib.rules import load_cycling_rules
from pipeline.s02_network import _pbf_from_manifest

INTERIM = REPO_ROOT / "data" / "interim"
FINAL_PATH = INTERIM / "final.parquet"
NETWORK_PATH = INTERIM / "cycle_network.parquet"
OUT_PATH = INTERIM / "cycle_facility.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "cycle_facility.md"
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
GAP_LIST_N = 40
FACILITY_ORDER = ["separated_oneway_both", "separated_twoway", "cycle_lane", "cycle_street", "mixed", "own_path"]
FACILITY_DE = {"separated_oneway_both": "Radweg je Seite", "separated_twoway": "Zweirichtungsradweg",
               "cycle_lane": "Radfahrstreifen", "cycle_street": "Fahrradstraße", "mixed": "Mischverkehr",
               "own_path": "eigene Trasse", None: "ohne Soll"}
IST_DE = {"cycle_street": "Fahrradstraße", "track": "Radweg", "lane": "Rad-/Schutzstreifen",
          "shared_lane": "Sharrow/Busspur", "no": "keine Radanlage"}
GAP_ORDER = ["missing", "wrong_type", "too_narrow", "none", "not_assessed"]
GAP_DE = {"missing": "fehlt", "wrong_type": "falscher Typ", "too_narrow": "zu schmal", "none": "keine Lücke",
          "not_assessed": "nicht bewertet"}
FLAG_DE = {"dtv_unknown": "Kfz-Menge unbekannt – Bedingung vorläufig erfüllt (C-FAC-02/03)",
           "fallback_check_p19": "Fallback der Matrixzelle möglich – Raumprüfung in Prompt 19",
           "cycle_street_blocked": "Kfz-Menge reduzieren (Filter) oder Route verlegen (C-FAC-02)",
           "mixed_over_s04": "Mischverkehr über S-04 (Kfz/h zu hoch)",
           "no_target_width": "keine Sollbreite für Führung × Radkategorie",
           "ist_width_unknown": "Ist-Breite unbekannt (OSM)"}
CAT_ORDER = ["SW", "GOW80", "GOW50", "GOW30", "ETW60", "ETW30", "ETW_ERF"]
CYC_ORDER = ["RSV", "HAUPT", "BASIS", "ERSCHL", NO_CYCLE_CATEGORY]
# OSM width keys (as C-PRI-08)
PATH_WIDTH_KEYS = ("width", "est_width")
CYCLEWAY_WIDTH_KEYS = ("cycleway:width", "cycleway:both:width", "cycleway:right:width", "cycleway:left:width")
ROAD_WIDTH_KEYS = ("width",)


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _fmt(v, digits: int = 0) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "–"
    return f"{v:,.{digits}f}".replace(",", " ")


_PARAMS: dict[int, tuple[CyclingRuleSet, fa.FacilityParams]] = {}


def _params(cycling: CyclingRuleSet) -> fa.FacilityParams:
    hit = _PARAMS.get(id(cycling))
    if hit is None or hit[0] is not cycling:
        hit = _PARAMS[id(cycling)] = (cycling, fa.FacilityParams.from_rules(cycling))
    return hit[1]


def evaluate(cat_final, cycle_cat, dtv, peak_dir, peak_both, space_fits_preferred, p: fa.FacilityParams) -> dict:
    """Soll facility and width of one segment (C-FAC-01..04)."""
    soll = fa.soll_facility(cat_final, cycle_cat, dtv, peak_both, space_fits_preferred, p)
    width = fa.target_width(soll.facility, cycle_cat, peak_dir, peak_both, p)
    flags = list(soll.flags)
    if width.width is None and soll.facility in p.required_by_facility:
        flags.append("no_target_width")
    return {"cycle_facility": soll.facility, "cycle_facility_fallback": soll.fallback, "cycle_width_m": width.width,
            "cycle_width_de_m": width.de, "cycle_width_nl_m": width.nl, "flags": flags,
            "rule_trace": [*soll.trace, width.trace]}


def facility_for_segment(props: dict, cycling: CyclingRuleSet) -> dict:
    """Golden-case API (tests/golden/cycling/s*.geojson): facility and width from the case properties."""
    peak_dir = props.get("cyc_peak_h_oneway")
    peak_both = props.get("cyc_peak_h", peak_dir)
    return evaluate(props["cat_final"], props["cycle_cat"], props.get("dtv"), peak_dir, peak_both,
                    props.get("space_fits_preferred"), _params(cycling))


# --- inputs per segment -------------------------------------------------------------------------------------


def _trace_inputs(trace: str) -> dict:
    try:
        return json.loads(trace)["inputs"]
    except (TypeError, ValueError, KeyError):
        return {}


def segment_inputs(final: pd.DataFrame, net: gpd.GeoDataFrame, tags: dict, p: fa.FacilityParams) -> pd.DataFrame:
    """Cycle category, peak hour, OSM cycleway values, sidepaths and Ist width per segment_id."""
    road = net[(net["kind"] == "road") & net["segment_id"].notna()].copy()
    side = net[(net["kind"] == "path") & net["sidepath_of"].notna()].copy()
    road["seg"], side["seg"] = road["segment_id"], side["sidepath_of"]
    road_in = [_trace_inputs(t) for t in road["impedance_trace"]]
    road["cw"] = [set(i.get("cycleway") or []) for i in road_in]
    road["bicycle_road"] = [i.get("bicycle_road") == "yes" for i in road_in]
    road["w_cw"] = edge_width(road["osm_way_ids"].tolist(), tags, CYCLEWAY_WIDTH_KEYS)
    road["w_road"] = edge_width(road["osm_way_ids"].tolist(), tags, ROAD_WIDTH_KEYS)
    side["w_path"] = edge_width(side["osm_way_ids"].tolist(), tags, PATH_WIDTH_KEYS)
    side["twoway"] = side["cost_fwd"].notna() & side["cost_bwd"].notna()
    side["side"] = fa.sidepath_side(final.geometry.reindex(side["seg"]).values, side.geometry.values)

    both = pd.concat([road[["seg", "cycle_cat_final", "cyc_peak_h", "cyc_peak_h_fwd", "cyc_peak_h_bwd"]],
                      side[["seg", "cycle_cat_final", "cyc_peak_h", "cyc_peak_h_fwd", "cyc_peak_h_bwd"]]])
    both["peak_dir"] = np.fmax(both["cyc_peak_h_fwd"].to_numpy(dtype="float64"), both["cyc_peak_h_bwd"].to_numpy(dtype="float64"))
    g = both.groupby("seg")
    out = pd.DataFrame(index=final.index)
    out["cycle_cat_final"] = g["cycle_cat_final"].agg(lambda s: fa.highest_category(s, p)).reindex(out.index).fillna(NO_CYCLE_CATEGORY)
    out["cyc_peak_h_dir"] = g["peak_dir"].max().reindex(out.index)
    out["cyc_peak_h"] = g["cyc_peak_h"].max().reindex(out.index)
    rg = road.groupby("seg")
    out["cycleway_values"] = rg["cw"].agg(lambda s: set().union(*s)).reindex(out.index)
    out["bicycle_road"] = rg["bicycle_road"].any().reindex(out.index).fillna(False).astype(bool)
    out["w_cw"] = rg["w_cw"].min().reindex(out.index)
    out["w_road"] = rg["w_road"].min().reindex(out.index)
    sg = side.groupby("seg")
    out["has_sidepath"] = out.index.isin(side["seg"])
    out["sidepath_twoway"] = sg["twoway"].any().reindex(out.index).fillna(False).astype(bool)
    out["sidepath_both_sides"] = sg["side"].agg(lambda x: {-1, 1} <= set(x)).reindex(out.index).fillna(False).astype(bool)
    out["w_path"] = sg["w_path"].min().reindex(out.index)
    return out


def _bool(v) -> bool:
    return bool(v) if v is not None and v is not pd.NA and not (isinstance(v, float) and np.isnan(v)) else False


def classify(final: pd.DataFrame, inp: pd.DataFrame, p: fa.FacilityParams) -> pd.DataFrame:
    rows = []
    for seg, f in final.iterrows():
        i = inp.loc[seg]
        cw = set(i["cycleway_values"]) if isinstance(i["cycleway_values"], set) else set()
        res = evaluate(f["cat_final"], i["cycle_cat_final"], f["dtv_official"], i["cyc_peak_h_dir"], i["cyc_peak_h"], None, p)
        cls = fa.ist_class(p, fahrradstrasse=_bool(f["fahrradstrasse_official"]), bicycle_road=bool(i["bicycle_road"]),
                           cycleway_values=cw, has_sidepath=bool(i["has_sidepath"]),
                           # s04 features also cover segments without a road edge (no impedance_trace)
                           track_present=_bool(f["separated_cycle_track_present"]), lane_present=_bool(f["cycle_lane_present"]))
        ist = fa.ist_facility(cls, bool(i["sidepath_twoway"]), p, bool(i["sidepath_both_sides"]))
        if i["has_sidepath"] and cls == "track":
            w_ist = i["w_path"]
        elif cls in ("track", "lane"):
            w_ist = i["w_cw"]
        elif cls == "cycle_street":
            w_ist = i["w_road"]
        else:
            w_ist = np.nan
        flags = res["flags"]
        if res["cycle_width_m"] is not None and not np.isfinite(w_ist) and ist in p.satisfies.get(res["cycle_facility"], ()):
            flags.append("ist_width_unknown")
        gap, partial = fa.facility_gap(res["cycle_facility"], res["cycle_facility_fallback"], cls, ist, w_ist,
                                       res["cycle_width_m"], p)
        conf = fa.confidence(f["cat_final"], flags, p)
        trace = [*res["rule_trace"],
                 {"id": "C-FAC-05", "result": cls, "values": {"fahrradstrasse_official": _bool(f["fahrradstrasse_official"]),
                                                               "track_present": _bool(f["separated_cycle_track_present"]),
                                                               "lane_present": _bool(f["cycle_lane_present"]),
                                                               "bicycle_road": bool(i["bicycle_road"]), "cycleway": sorted(cw),
                                                               "sidepath": bool(i["has_sidepath"]),
                                                               "sidepath_both_sides": bool(i["sidepath_both_sides"]), "facility_ist": ist,
                                                               "width_ist_m": None if not np.isfinite(w_ist) else float(w_ist)}},
                 {"id": "C-FAC-06", "result": gap, "values": {"partial": partial}},
                 {"id": "C-FAC-07", "result": conf, "values": {"flags": flags}}]
        rows.append({"segment_id": seg, "cycle_cat_final": i["cycle_cat_final"], "cyc_peak_h": i["cyc_peak_h"],
                     "cyc_peak_h_dir": i["cyc_peak_h_dir"], "cycle_facility_soll": res["cycle_facility"],
                     "cycle_facility_fallback": res["cycle_facility_fallback"], "cycle_width_soll_m": res["cycle_width_m"],
                     "cycle_width_de_m": res["cycle_width_de_m"], "cycle_width_nl_m": res["cycle_width_nl_m"],
                     "cycle_osm_ist": cls, "cycle_facility_ist": ist, "cycle_width_ist_m": w_ist, "facility_gap": gap,
                     "gap_partial": partial, "facility_flags": "|".join(flags) or None, "facility_confidence": conf,
                     "rule_trace_facility": json.dumps(trace, ensure_ascii=False, default=float)})
    return pd.DataFrame(rows).set_index("segment_id")


# --- report -------------------------------------------------------------------------------------------------


def _km_table(df: pd.DataFrame, rows: str, cols: str, row_order: list, col_order: list, row_de=None, col_de=None) -> list[str]:
    km = df.groupby([rows, cols], dropna=False)["length_m"].sum().unstack(fill_value=0) / 1000
    row_keys = [r for r in row_order if r in km.index] + [r for r in km.index if r not in row_order]
    col_keys = [c for c in col_order if c in km.columns] + [c for c in km.columns if c not in col_order]
    name = lambda d, k: (d or {}).get(k, "–" if k is None or (isinstance(k, float) and np.isnan(k)) else str(k))
    lines = ["| | " + " | ".join(name(col_de, c) for c in col_keys) + " | gesamt |",
             "| --- | " + " | ".join("---:" for _ in col_keys) + " | ---: |"]
    for r in row_keys:
        vals = [km.loc[r, c] for c in col_keys]
        lines.append(f"| {name(row_de, r)} | " + " | ".join(_fmt(v, 1) for v in vals) + f" | {_fmt(sum(vals), 1)} |")
    tot = [km[c].sum() for c in col_keys]
    lines.append("| **gesamt** | " + " | ".join(_fmt(v, 1) for v in tot) + f" | **{_fmt(sum(tot), 1)}** |")
    return lines


def write_report(out: gpd.GeoDataFrame, version: str, p: fa.FacilityParams) -> None:
    viewers = load_viewers()
    km = lambda m: out.loc[m, "length_m"].sum() / 1000
    has = out["cycle_facility_soll"].notna()
    net = out["cycle_cat_final"] != NO_CYCLE_CATEGORY
    flags = out["facility_flags"].fillna("")
    main = out["cycle_cat_final"].isin(["RSV", "HAUPT", "BASIS"])
    gap = out["facility_gap"].isin(["missing", "wrong_type", "too_narrow"])
    lines = [
        "# Führungsform und Breite der Radanlagen (Stufe c05)",
        "",
        f"Erzeugt {_now()} mit pipeline/c05_facility.py · cycling_rules.yaml {version} · nicht amtlicher Entwurf. "
        "Regeln C-FAC-01…07 sind Annahmen (source_type assumption, status draft); Trennungsmatrix und Breiten nach "
        "config/cycling_rules.yaml.",
        "",
        "Soll-Führung = Trennungsmatrix (cat_final × cycle_cat_final). Bei Zellen mit Fallback bleibt bis Prompt 19 die "
        "bevorzugte Führung (Flag fallback_check_p19). Fehlt die Kfz-Menge, gelten Fahrradstraßen- und S-04-Bedingung "
        "vorläufig als erfüllt (Entscheidung 2026-11-06, Flag dtv_unknown).",
        "",
        "## Kurzfassung",
        "",
        f"- {_fmt(len(out))} Abschnitte, {_fmt(km(slice(None)), 0)} km; Soll-Führung für {_fmt(km(has), 0)} km "
        f"(ohne Soll: {_fmt(km(~has), 0)} km ohne cat_final, v. a. nicht klassifizierte ländliche Stadtteile).",
        f"- Soll-Radnetz RSV/HAUPT/BASIS: {_fmt(km(main), 0)} km; davon mit Lücke (fehlt/falscher Typ/zu schmal): "
        f"{_fmt(km(main & gap), 0)} km ({_fmt(100 * km(main & gap) / km(main), 0)} %). Erschließungsnetz ERSCHL: "
        f"{_fmt(km(out['cycle_cat_final'] == 'ERSCHL'), 0)} km, davon mit Lücke {_fmt(km((out['cycle_cat_final'] == 'ERSCHL') & gap), 0)} km.",
        f"- Fahrradstraße nicht möglich (Kfz zu hoch oder Rad nicht dominant): {_fmt((flags.str.contains('cycle_street_blocked')).sum())} "
        f"Abschnitte, {_fmt(km(flags.str.contains('cycle_street_blocked')), 1)} km.",
        f"- Kfz-Menge unbekannt (vorläufig erfüllt): {_fmt(km(flags.str.contains('dtv_unknown')), 0)} km; "
        f"Fallback in Prompt 19 zu prüfen: {_fmt(km(flags.str.contains('fallback_check_p19')), 0)} km.",
        "",
        "## km je Führungsform: Soll und Ist",
        "",
        "Ist auf die Soll-Vokabel abgebildet (C-FAC-05: Radweg → Radweg je Seite bzw. Zweirichtungsradweg, Streifen → "
        "Radfahrstreifen, Sharrow/keine Anlage → Mischverkehr).",
        "",
        "| Führungsform | Soll km | Ist km | Soll km im Radnetz | Ist km im Radnetz |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for f in FACILITY_ORDER:
        lines.append(f"| {FACILITY_DE[f]} | {_fmt(km(out['cycle_facility_soll'] == f), 1)} | {_fmt(km(out['cycle_facility_ist'] == f), 1)} | "
                     f"{_fmt(km(net & (out['cycle_facility_soll'] == f)), 1)} | {_fmt(km(net & (out['cycle_facility_ist'] == f)), 1)} |")
    lines += ["", "Ist-Klassen aus OSM (C-FAC-05):", "", "| Ist-Klasse | km | km im Radnetz |", "| --- | ---: | ---: |"]
    for c in p.ist_classes:
        lines.append(f"| {IST_DE[c]} (`{c}`) | {_fmt(km(out['cycle_osm_ist'] == c), 1)} | {_fmt(km(net & (out['cycle_osm_ist'] == c)), 1)} |")

    lines += ["", "## Matrix Straßenkategorie × Radkategorie (km)", ""]
    lines += _km_table(out, "cat_final", "cycle_cat_final", CAT_ORDER, CYC_ORDER)
    lines += ["", "Soll-Führung je Straßenkategorie (km):", ""]
    lines += _km_table(out[has], "cat_final", "cycle_facility_soll", CAT_ORDER, FACILITY_ORDER, col_de=FACILITY_DE)

    lines += ["", "## Lücken (facility_gap)", "", "km je Lückentyp und Radkategorie:", ""]
    lines += _km_table(out, "facility_gap", "cycle_cat_final", GAP_ORDER, CYC_ORDER, row_de=GAP_DE)
    lines += ["", f"Teilerfüllung (gap_partial: Ist = Teilerfüllung nach C-PRI-03 oder Fallback der Zelle): "
              f"{_fmt(km(out['gap_partial']), 1)} km.", ""]

    gaps = out[out["facility_gap"].isin(["missing", "wrong_type", "too_narrow"]) & out["cycle_cat_final"].isin(["RSV", "HAUPT"])].copy()
    gaps["name"] = gaps["name"].fillna("(ohne Namen)")
    agg = (gaps.groupby(["name", "bezirk", "cycle_cat_final", "cat_final", "cycle_facility_soll", "cycle_facility_ist", "facility_gap"],
                        dropna=False)["length_m"].sum().sort_values(ascending=False).head(GAP_LIST_N))
    lines += [f"### Lückenliste RSV/HAUPT (längste {GAP_LIST_N}, je Straße und Bezirk zusammengefasst)", "",
              "| Straße | Bezirk | Rad | Kfz | Soll | Ist | Lücke | km |", "| --- | --- | --- | --- | --- | --- | --- | ---: |"]
    for (name, bez, cc, cat, soll, ist, gap), length in agg.items():
        lines.append(f"| {name} | {bez} | {cc} | {cat} | {FACILITY_DE.get(soll, soll)} | {FACILITY_DE.get(ist, ist)} | {GAP_DE[gap]} | {_fmt(length / 1000, 2)} |")

    lines += ["", "## Hinweise (Flags)", "", "| Flag | Bedeutung | Abschnitte | km |", "| --- | --- | ---: | ---: |"]
    for flag, text in FLAG_DE.items():
        m = flags.str.split("|").apply(lambda xs, f=flag: f in xs)
        lines.append(f"| `{flag}` | {text} | {_fmt(m.sum())} | {_fmt(km(m), 1)} |")
    lines += ["", f"confidence: " + ", ".join(f"{k} {_fmt(km(out['facility_confidence'] == k), 0)} km" for k in ("high", "medium", "low")), ""]

    lines += ["## Breiten: Projekt-Soll, DE-Regelmaß, NL-Hauptnetz", "",
              "Längengewichtetes Mittel der Soll-Breite je Führung (Projekt-Soll inkl. intensity_upgrade, nie unter der Untergrenze); "
              "DE und NL als Vergleichswerte für den Steckbrief.", "",
              "| Führungsform | km | Projekt-Soll m | DE-Regelmaß m | NL-Hauptnetz m | Ist-Breite bekannt km |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for f in FACILITY_ORDER:
        g = out[(out["cycle_facility_soll"] == f) & out["cycle_width_soll_m"].notna()]
        if g.empty:
            continue
        w = g["length_m"]
        lines.append(f"| {FACILITY_DE[f]} | {_fmt(w.sum() / 1000, 1)} | {_fmt(np.average(g['cycle_width_soll_m'], weights=w), 2)} | "
                     f"{_fmt(p.de_ref.get(f), 2)} | {_fmt(p.nl_ref.get(f), 2)} | "
                     f"{_fmt(g.loc[g['cycle_width_ist_m'].notna(), 'length_m'].sum() / 1000, 1)} |")

    lines += ["", "## Soll-Führung je Bezirk (Anteil km)", ""]
    bz = out.copy()
    bz["soll_de"] = bz["cycle_facility_soll"].map(FACILITY_DE)
    lines += district_breakdown(bz, "soll_de", [FACILITY_DE[f] for f in FACILITY_ORDER])

    lines += ["", f"## Stichproben ({SAMPLE_SIZE} je Soll-Führung, über Bezirke verteilt, Seed {SAMPLE_SEED})", ""]
    for f in FACILITY_ORDER:
        g = out[out["cycle_facility_soll"] == f]
        if g.empty:
            continue
        s = sample_by_district(g.reset_index(), SAMPLE_SIZE, SAMPLE_SEED)
        lines += [f"### {FACILITY_DE[f]} (`{f}`, {_fmt(len(g))} Abschnitte)", "",
                  "| segment_id | Straße | Bezirk | Kfz | Rad | Soll-Breite m | Ist | Lücke | Flags | Prüfen |",
                  "| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |"]
        for r in s.itertuples():
            lines.append(f"| `{r.segment_id}` | {r.name if isinstance(r.name, str) else '–'} | {r.bezirk} | {r.cat_final} | "
                         f"{r.cycle_cat_final} | {_fmt(r.cycle_width_soll_m, 2)} | {IST_DE[r.cycle_osm_ist]} | {GAP_DE[r.facility_gap]} | "
                         f"{r.facility_flags or '–'} | {_links(r.geometry, viewers)} |")
        lines.append("")
    lines += ["## Grenzen", "",
              "- Kfz-DTV nur für Hauptverkehrsstraßen (Zählung 2019); auf Erschließungsstraßen gelten C-FAC-02/03 vorläufig als erfüllt.",
              "- Kfz-Spitzenstundenanteil 0,10 aus der Notiz zu L-02 (Annahme, HBS prüfen).",
              "- Radverkehr je Abschnitt = Maximum über Straßenkante und begleitende Radwege (Näherung).",
              "- Ist-Breite nur, wo OSM width/cycleway:width erfasst ist; ohne Breite keine Lücke „zu schmal“.",
              "- Eigene Trassen (own_path) ohne Sollbreite und ohne Lückenbewertung (docs/open_questions.md).",
              "",
              "Quellen: OpenStreetMap-Mitwirkende (ODbL); Freie und Hansestadt Hamburg, Verkehrsmengen und Fahrradstraßen "
              "(dl-de/by-2.0).", ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    cyc = load_cycling_rules()
    p = fa.FacilityParams.from_rules(cyc)
    for path, step in ((NETWORK_PATH, "make cycle-network"), (FINAL_PATH, "make coherence")):
        if not path.exists():
            print(f"cycle-facility: {path.relative_to(REPO_ROOT)} missing; run `{step}` first", file=sys.stderr)
            return 1
    t0 = time.perf_counter()

    def tick(msg: str) -> None:
        print(f"cycle-facility: {msg} ({time.perf_counter() - t0:.0f} s)")

    final = gpd.read_parquet(FINAL_PATH, columns=["segment_id", "name", "bezirk", "length_m", "cat_final", "dtv_official",
                                                  "fahrradstrasse_official", "separated_cycle_track_present",
                                                  "cycle_lane_present", "width_median_m", "geometry"]).set_index("segment_id")
    net = gpd.read_parquet(NETWORK_PATH)
    pbf = REPO_ROOT / _pbf_from_manifest(load_manifest())["path"]
    way_ids = {int(w) for ws in net["osm_way_ids"] for w in ws}
    tags = read_way_tags(pbf, way_ids)
    tick(f"OSM tags of {len(tags)} ways")
    inp = segment_inputs(final, net, tags, p)
    res = classify(final, inp, p)
    tick(f"{len(res)} segments classified")
    out = final[["name", "bezirk", "length_m", "cat_final", "dtv_official", "width_median_m", "geometry"]].join(res)
    out = gpd.GeoDataFrame(out, geometry="geometry", crs=final.crs).reset_index()
    assert set(out["cycle_facility_soll"].dropna()) <= FACILITIES
    out.to_parquet(OUT_PATH)
    write_report(out, cyc.meta.version, p)
    tick(f"wrote {OUT_PATH.relative_to(REPO_ROOT)} and {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
