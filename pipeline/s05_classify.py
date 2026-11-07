"""Stage 5: rule-based target category per segment (guide 3.4 step 5, prompts/08_classify.md).

Usage: uv run python -m pipeline.s05_classify

Reads data/interim/crosssection.parquet (features incl. cross section) and config/rules.yaml (sections
classification, classification_policy) and writes data/interim/classified.parquet with the columns
cat_proposed, confidence, confidence_reasons (JSON), rule_path and rule_trace (JSON), plus
reports/classification.md and reports/classification_sample.csv (30 random segments per category in the
pilot district for the manual check). Only segments in the work area (conflated) are classified.
The run stops with exit code 1 if a check fails; outputs are then not written.
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

from pipeline.lib.area import area_label, district_names, sample_by_district
from pipeline.lib.classify import classification_inputs, classify_segment
from pipeline.lib.crs import WORK_CRS
from pipeline.lib.links import load_viewers, orthophoto_link, osm_map_link, osm_way_link, panoramax_link
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.report import district_breakdown
from pipeline.lib.rules import all_thresholds, load_rules, referenced_features
from pipeline.s04_features import _fmt, _now, _pct

__all__ = ["classification_inputs", "classify_segment", "classify_frame", "main"]

IN_PATH = REPO_ROOT / "data" / "interim" / "crosssection.parquet"
OUT_PATH = REPO_ROOT / "data" / "interim" / "classified.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "classification.md"
MAX_STREET_ROWS = 50  # report readability only
SAMPLE_CSV = REPO_ROOT / "reports" / "classification_sample.csv"
GOLDEN_DIR = REPO_ROOT / "tests" / "golden"
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
CONF_ORDER = ["hoch", "mittel", "niedrig"]
# Autobahnen are federal roads, not Bezirksstraßen (report list "Bezirksstraßen, die GOW50 werden").
FEDERAL_HIGHWAY = {"motorway", "motorway_link"}


def classify_frame(df: pd.DataFrame, rules) -> pd.DataFrame:
    """Classify each row; returns the result columns with the index of df."""
    cols = classification_inputs(rules)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"input columns missing: {missing}")
    rows = []
    for rec in df[cols].to_dict("records"):
        r = classify_segment(rec, rules)
        rows.append({
            "cat_proposed": r["cat_proposed"],
            "confidence": r["confidence"],
            "confidence_reasons": json.dumps(r["confidence_reasons"], ensure_ascii=False),
            "rule_path": " → ".join(dict.fromkeys(s["id"] for s in r["rule_trace"] if s["passed"])),
            "rule_trace": json.dumps(r["rule_trace"], ensure_ascii=False),
        })
    return pd.DataFrame(rows, index=df.index)


# --- checks ----------------------------------------------------------------------------------


def golden_results(rules) -> list[dict]:
    out = []
    for path in sorted(GOLDEN_DIR.glob("*.geojson")):
        props = json.loads(path.read_text(encoding="utf-8"))["features"][0]["properties"]
        r = classify_segment({k: props.get(k) for k in referenced_features(rules)}, rules)
        passed = {s["id"] for s in r["rule_trace"] if s["passed"]}
        out.append({"case": props["case_id"], "expected": props["expected_category"], "got": r["cat_proposed"],
                    "ok": r["cat_proposed"] == props["expected_category"] and set(props["expected_rules"]) <= passed})
    return out


def run_checks(inp: pd.DataFrame, out: pd.DataFrame, golden: list[dict], rules) -> list[dict]:
    area = out["conflated"].astype(bool)
    failed = [g["case"] for g in golden if not g["ok"]]
    traces_ok = all(isinstance(json.loads(t), list) and json.loads(t) for t in out.loc[area, "rule_trace"])
    return [
        {"name": "segment_id unverändert", "ok": list(out["segment_id"]) == list(inp["segment_id"]),
         "detail": f"{len(out)} Abschnitte"},
        {"name": "Goldene Fälle grün", "ok": not failed,
         "detail": f"{len(golden) - len(failed)}/{len(golden)}" + (f"; falsch: {', '.join(failed)}" if failed else "")},
        {"name": "Jeder Abschnitt im Arbeitsgebiet hat eine Kategorie", "ok":
         bool(out.loc[area, "cat_proposed"].isin(set(rules.categories)).all()) and out.loc[~area, "cat_proposed"].isna().all(),
         "detail": f"{int(area.sum())} klassifiziert, {int((~area).sum())} außerhalb (leer)"},
        {"name": "rule_trace gefüllt", "ok": traces_ok, "detail": "JSON-Liste mit mindestens einer Regel"},
        {"name": "confidence gültig", "ok": bool(out.loc[area, "confidence"].isin(CONF_ORDER).all()), "detail": ", ".join(CONF_ORDER)},
    ]


# --- report ----------------------------------------------------------------------------------


def _km(x: float) -> str:
    return f"{x / 1000:.1f}"


def _hvs_label(v) -> str:
    return "unbekannt" if pd.isna(v) else ("HVS" if bool(v) else "keine HVS")


def _name(v) -> str:
    return v if isinstance(v, str) and v else "–"


def _points(geom):
    mid = geom.interpolate(0.5, normalized=True)
    return mid, gpd.GeoSeries([mid], crs=WORK_CRS).to_crs(4326).iloc[0]


def pick_sample(pilot: gpd.GeoDataFrame, categories: list[str]) -> gpd.GeoDataFrame:
    """Up to SAMPLE_SIZE segments per category, spread over the Bezirke (sample_by_district)."""
    parts = [sample_by_district(pilot[pilot["cat_proposed"] == cat], SAMPLE_SIZE, SAMPLE_SEED)
             for cat in categories if (pilot["cat_proposed"] == cat).any()]
    return pd.concat(parts) if parts else pilot.iloc[0:0]


def write_sample_csv(sample: gpd.GeoDataFrame, viewers: dict) -> None:
    rows = []
    for _, r in sample.iterrows():
        work, wgs = _points(r.geometry)
        rows.append({"segment_id": r["segment_id"], "bezirk": r["bezirk"], "cat_proposed": r["cat_proposed"], "confidence": r["confidence"],
                     "rule_path": r["rule_path"], "name": r["name"], "highway": r["highway"],
                     "in_hvs": r["in_hvs"], "conn_score": round(r["conn_score"], 3) if pd.notna(r["conn_score"]) else None,
                     "length_m": round(r["length_m"], 1),
                     "orthophoto": orthophoto_link(work, viewers), "panoramax": panoramax_link(wgs, viewers),
                     "osm_map": osm_map_link(wgs), "osm_way": osm_way_link(r["osm_way_ids"][0]),
                     "cat_expected_manual": None, "check_ok": None, "comment": None})
    SAMPLE_CSV.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(SAMPLE_CSV, index=False)


def _crosstab(df: pd.DataFrame, cats: list[str]) -> list[str]:
    hvs = df["in_hvs"].map(_hvs_label)
    cols = ["HVS", "keine HVS", "unbekannt"]
    t = df.groupby([df["cat_proposed"], hvs])["length_m"].sum().unstack(fill_value=0.0).reindex(index=cats, columns=cols, fill_value=0.0)
    lines = ["| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil HVS-km |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    hvs_total = t["HVS"].sum()
    for cat, row in t.iterrows():
        if row.sum() == 0:
            continue
        lines.append(f"| {cat} | {_km(row['HVS'])} | {_km(row['keine HVS'])} | {_km(row['unbekannt'])} | {_km(row.sum())} | "
                     f"{_pct(row['HVS'] / hvs_total) if hvs_total else '–'} |")
    lines.append(f"| **Summe** | {_km(t['HVS'].sum())} | {_km(t['keine HVS'].sum())} | {_km(t['unbekannt'].sum())} | "
                 f"{_km(t.values.sum())} | |")
    return lines


def _reason_counts(df: pd.DataFrame) -> pd.Series:
    reasons = df["confidence_reasons"].map(json.loads).explode().dropna()
    return reasons.value_counts()


def write_report(out: gpd.GeoDataFrame, ctx: dict, checks: list[dict]) -> None:
    rules, pilot_name = ctx["rules"], ctx["pilot"]
    cats = list(rules.categories)
    area = out[out["conflated"].astype(bool)]
    pilot = area[area["bezirk"].isin(ctx["districts"])]
    total_km = area["length_m"].sum()
    lines = [
        "# Klassifikationsbericht – Stufe 5", "",
        f"Erzeugt: {_now()} von `pipeline/s05_classify.py`, rules.yaml {rules.meta.version}. Nicht amtlicher Entwurf: "
        "Die Automatik schlägt vor, Menschen entscheiden (overrides/overrides.csv).", "",
        "## Kennzahlen", "",
        f"- Klassifiziert: {_fmt(len(area))} Abschnitte im Arbeitsgebiet ({_km(total_km)} km), davon {_fmt(len(pilot))} in "
        f"{pilot_name} ({_km(pilot['length_m'].sum())} km). Abschnitte außerhalb des Arbeitsgebiets bleiben leer.",
        f"- Defaults aus C-MISS-01 genutzt: " + ", ".join(
            f"{k} {_pct(v)}" for k, v in ctx["defaults_share"].items()) + " der Abschnitte im Arbeitsgebiet.", "",
        "### km je Kategorie", "",
        f"| Kategorie | Bezeichnung | {pilot_name} km | Anteil | Arbeitsgebiet km | Anteil | Abschnitte (Arbeitsgebiet) |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cat in cats:
        a, p = area[area["cat_proposed"] == cat], pilot[pilot["cat_proposed"] == cat]
        lines.append(f"| {cat} | {rules.categories[cat].label_de} | {_km(p['length_m'].sum())} | "
                     f"{_pct(p['length_m'].sum() / pilot['length_m'].sum())} | {_km(a['length_m'].sum())} | "
                     f"{_pct(a['length_m'].sum() / total_km)} | {_fmt(len(a))} |")
    lines += ["", "### km-Anteile je Kategorie und Bezirk", "", *district_breakdown(pilot, "cat_proposed", cats)]
    lines += ["", "### confidence (Anteil der Länge im Arbeitsgebiet)", "",
              "| Kategorie | hoch | mittel | niedrig |", "| --- | ---: | ---: | ---: |"]
    for cat in cats + ["alle"]:
        a = area if cat == "alle" else area[area["cat_proposed"] == cat]
        if a.empty:
            continue
        share = a.groupby("confidence")["length_m"].sum() / a["length_m"].sum()
        lines.append(f"| {cat} | " + " | ".join(_pct(share.get(c, 0.0)) for c in CONF_ORDER) + " |")
    rc = _reason_counts(area)
    lines += ["", "Häufigste Gründe für eine herabgesetzte confidence (Abschnitte, Mehrfachnennung):", "",
              "| Grund | Abschnitte |", "| --- | ---: |", *[f"| `{k}` | {_fmt(v)} |" for k, v in rc.head(12).items()],
              "", "`fehlt:x` = Eingangswert fehlt und entscheidet; `nahe_schwelle:x~s` = Wert innerhalb ±10 % der Schwelle; "
              "`fallback:x` = Fallback-Quelle oder Default (C-CONF-01).",
              "", "## Prüfungen", "", "| Prüfung | Ergebnis | Detail |", "| --- | --- | --- |",
              *[f"| {c['name']} | {'ok' if c['ok'] else 'FEHLER'} | {c['detail']} |" for c in checks]]

    lines += ["", "## Methode", "",
              "- Kaskade `classification` aus rules.yaml, Reihenfolge = Priorität: C-SW-01 → C-RUR-01 → C-ERF-01 → C-GOW-01 "
              "(dann C-G30-01, C-G30-02, C-G50-02, sonst C-G50-01) → C-ETW-01. Die Bedingungen werden von `pipeline/lib/expr.py` gelesen; "
              "Schwellen nur aus rules.yaml.",
              "- **Fehlende Werte (C-MISS-01):** dreiwertige Logik; eine Regel greift nur bei sicher wahrer Bedingung. "
              "Defaults für Merkmale ohne Datenquelle: " + ", ".join(
                  f"{k} = {d.value}" for p in rules.classification_policy for k, d in p.defaults.items()) + ".",
              "- **confidence (C-CONF-01):** niedrig, wenn ein entscheidender Wert fehlt oder innerhalb ±10 % einer Schwelle liegt; "
              "mittel bei Fallback-Quellen (" + ", ".join(
                  p_name for p in rules.classification_policy for p_name in p.fallback_inputs) + ") und Defaults; sonst hoch. "
              "Es zählen nur Werte, die das Ergebnis bestimmt haben.",
              "- `rule_trace` (JSON) enthält je geprüfter Regel id, passed, result (true/false/null), inputs, confidence und Gründe; "
              "`rule_path` die gegriffenen Regeln.",
              f"- HVS = `in_hvs` (DTV-Linien 2019, S-CONF-04). Bezirksstraße = keine HVS und keine Autobahn "
              f"({', '.join(sorted(FEDERAL_HIGHWAY))}); Annahme für diesen Bericht.", ""]

    lines += [f"## Kreuztabelle Soll × HVS – {pilot_name} (km)", "", *_crosstab(pilot, cats), "",
              "## Kreuztabelle Soll × HVS – Arbeitsgebiet (km)", "", *_crosstab(area, cats), "",
              "### HVS-km je Bezirk (Arbeitsgebiet)", "",
              "| Bezirk | " + " | ".join(cats) + " |", "| --- |" + " ---: |" * len(cats)]
    hv = area[area["in_hvs"].fillna(False).astype(bool)]
    for bez, g in hv.groupby(hv["bezirk"].fillna("–")):
        km = g.groupby("cat_proposed")["length_m"].sum()
        lines.append(f"| {bez} | " + " | ".join(_km(km.get(c, 0.0)) for c in cats) + " |")

    etw = area[area["in_hvs"].fillna(False).astype(bool) & (area["cat_proposed"] == "ETW30")]
    lines += ["", f"## HVS-Abschnitte, die ETW30 werden ({len(etw)} Abschnitte, {_km(etw['length_m'].sum())} km)", "",
              "Einzeln begründen (guide.md Teil 7). Ursache ist in der Kaskade nur möglich, wenn `in_hvs` wahr ist und "
              "C-GOW-01 trotzdem nicht greift – das kommt nicht vor, solange in_hvs bekannt ist."]
    if etw.empty:
        lines += ["", "_keine_"]
    else:
        lines += ["", "| segment_id | Bezirk | Name | highway | m | conn_score | confidence | Regeln |", "| --- | --- | --- | --- | ---: | ---: | --- | --- |"]
        for _, r in etw.sort_values(["bezirk", "name"]).iterrows():
            lines.append(f"| `{r['segment_id']}` | {r['bezirk']} | {_name(r['name'])} | {r['highway']} | {r['length_m']:.0f} | "
                         f"{r['conn_score']:.2f} | {r['confidence']} | {r['rule_path']} |")

    hvs_other = area[area["in_hvs"].fillna(False).astype(bool) & ~area["cat_proposed"].isin(["GOW50", "GOW30"])]
    lines += ["", f"Weitere HVS-Abschnitte außerhalb GOW50/GOW30: " + (", ".join(
        f"{c} {len(g)} ({_km(g['length_m'].sum())} km)" for c, g in hvs_other.groupby("cat_proposed")) or "keine") + "."]

    bez = area[(area["in_hvs"] == False) & ~area["highway"].isin(FEDERAL_HIGHWAY) & (area["cat_proposed"] == "GOW50")]  # noqa: E712
    lines += ["", f"## Bezirksstraßen, die GOW50 werden ({len(bez)} Abschnitte, {_km(bez['length_m'].sum())} km)", "",
              "Zusammengefasst nach Bezirk und Straßenname. Grund ist immer C-GOW-01 über conn_score ≥ "
              f"{all_thresholds(rules)["conn_gow"].value:g} ohne GOW30-Auslöser; einzeln begründen "
              "(guide.md Teil 7). Einzelne Abschnitte stehen in `data/interim/classified.parquet`."]
    if bez.empty:
        lines += ["", "_keine_"]
    else:
        hw = bez["highway"].value_counts()
        lines += ["", "Befund: " + ", ".join(f"{k} {v}" for k, v in hw.items()) + f"; Median-Länge {bez['length_m'].median():.0f} m. "
                  "Kurze Stücke von Hauptstraßen deuten eher auf Lücken im HVS-Abgleich (S-CONF-04, nur match exact) als "
                  "auf Bezirksstraßen hin – bei der Durchsicht prüfen."]
        lines += ["", "| Bezirk | Name | highway | Abschnitte | km | conn_score min–max | confidence niedrig | Beispiel |",
                  "| --- | --- | --- | ---: | ---: | --- | ---: | --- |"]
        grp = sorted(bez.assign(name=bez["name"].map(_name)).groupby([bez["bezirk"].fillna("–"), "name"]),
                     key=lambda kv: (-kv[1]["length_m"].sum(), kv[0]))
        if len(grp) > MAX_STREET_ROWS:
            lines[-2:-2] = [f"Gezeigt: die {MAX_STREET_ROWS} längsten von {len(grp)} Straßen (Bezirk + Name).", ""]
        for (b, n), g in grp[:MAX_STREET_ROWS]:
            lines.append(f"| {b} | {n} | {', '.join(sorted(set(g['highway'])))} | {len(g)} | {_km(g['length_m'].sum())} | "
                         f"{g['conn_score'].min():.2f}–{g['conn_score'].max():.2f} | {int((g['confidence'] == 'niedrig').sum())} | "
                         f"`{g['segment_id'].iloc[0]}` |")

    sample, viewers = ctx["sample"], ctx["viewers"]
    lines += ["", f"## Stichprobe: bis zu {SAMPLE_SIZE} zufällige Abschnitte je Kategorie in {pilot_name}, nach Bezirk geschichtet (Seed {SAMPLE_SEED})", "",
              "Zur manuellen Durchsicht im Orthophoto (Geoportal Hamburg, DOP belaubt) und in Panoramax. Befund in "
              "`reports/classification_sample.csv` eintragen (Spalten cat_expected_manual, check_ok, comment).", "",
              "**Durchsicht: offen.**", ""]
    for cat in cats:
        s = sample[sample["cat_proposed"] == cat]
        if s.empty:
            lines += [f"### {cat}", "", "_keine Abschnitte_", ""]
            continue
        lines += [f"### {cat} ({len(s)} von {int((pilot['cat_proposed'] == cat).sum())})", "",
                  "| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |",
                  "| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |"]
        for _, r in s.iterrows():
            work, wgs = _points(r.geometry)
            cs = "–" if pd.isna(r["conn_score"]) else f"{r['conn_score']:.2f}"
            lines.append(f"| `{r['segment_id']}` | {r['bezirk']} | {_name(r['name'])} | {r['highway']} | {r['length_m']:.0f} | "
                         f"{_hvs_label(r['in_hvs'])} | {cs} | {r['confidence']} | {r['rule_path']} | "
                         f"[DOP]({orthophoto_link(work, viewers)}) | [Bilder]({panoramax_link(wgs, viewers)}) | "
                         f"[Way]({osm_way_link(r['osm_way_ids'][0])}) |")
        lines.append("")
    lines += ["## Lizenz", "",
              "Abschnitte und Merkmale aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale "
              "(Tempo, Verkehrsmengen, ALKIS): Freie und Hansestadt Hamburg, dl-de/by-2.0; Busfahrten: HVV, dl-de/by-2.0; "
              "Einwohner: Zensus 2022, dl-de/by-2.0. Orthophotos: LGV Hamburg, dl-de/by-2.0. Panoramax-Bilder: Lizenz je Bild.", ""]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# --- main ------------------------------------------------------------------------------------


def main() -> int:
    rules = load_rules()
    names = district_names()
    if not IN_PATH.exists():
        print("classify: data/interim/crosssection.parquet missing; run `make crosssection` first", file=sys.stderr)
        return 1
    inp = gpd.read_parquet(IN_PATH)
    in_area = inp["conflated"].astype(bool)
    print(f"classify: {int(in_area.sum())} segments in the work area")

    result = classify_frame(inp[in_area], rules)
    out = inp.join(result)
    defaults = {k for p in rules.classification_policy for k in p.defaults}
    defaults_share = {k: float(inp.loc[in_area, k].isna().mean()) for k in sorted(defaults)}

    golden = golden_results(rules)
    checks = run_checks(inp, out, golden, rules)
    pilot = out[in_area & out["bezirk"].isin(names)]
    sample = pick_sample(pilot, list(rules.categories))
    viewers = load_viewers()
    ctx = {"rules": rules, "pilot": area_label(names), "districts": names, "sample": sample, "viewers": viewers, "defaults_share": defaults_share}
    write_report(out, ctx, checks)
    for c in checks:
        print(f"classify: {c['name']}: {c['ok']} ({c['detail']})")
    if not all(c["ok"] for c in checks):
        print(f"classify: check(s) failed, outputs not written; see {REPORT_PATH}", file=sys.stderr)
        return 1
    write_sample_csv(sample, viewers)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_PATH, index=False)
    km = out[in_area].groupby("cat_proposed")["length_m"].sum() / 1000
    print("classify: km per category: " + ", ".join(f"{k} {v:.1f}" for k, v in km.items()))
    print(f"classify: -> {Path(OUT_PATH).relative_to(REPO_ROOT)}, {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
