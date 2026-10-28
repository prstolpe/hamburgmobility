"""Stage 8: discrepancy ('grijze wegen') and priority (guide 1.6, 3.2 Stufe 8, prompts/10_discrepancy.md).

Usage: uv run python -m pipeline.s08_discrepancy

Reads data/interim/final.parquet (cat_final and Ist features), the Unfallatlas ZIPs listed in data/manifest.json
and config/rules.yaml (discrepancy, priority). Writes data/interim/discrepancy.parquet with disc_speed,
disc_design, disc_use (0-3), disc_type (D1-D3), disc_causes, crash counts per segment, risk, priority and
disc_trace (JSON), plus reports/priority_top30.md and reports/discrepancy.md.
Crashes are stored and shown only as counts per segment, never as single records.
The run stops with exit code 1 if a check fails; outputs are then not written.
"""

import json
import random
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml

from pipeline.lib import accidents as acc
from pipeline.lib import discrepancy as disc
from pipeline.lib import expr
from pipeline.lib.crs import WORK_CRS
from pipeline.lib.links import load_viewers, orthophoto_link, osm_way_link, panoramax_link
from pipeline.lib.manifest import REPO_ROOT, load_manifest
from pipeline.lib.rules import load_rules
from pipeline.s04_features import _fmt, _now, _pct

PROJECT_PATH = REPO_ROOT / "config" / "project.yaml"
SOURCES_PATH = REPO_ROOT / "config" / "sources.yaml"
IN_PATH = REPO_ROOT / "data" / "interim" / "final.parquet"
OUT_PATH = REPO_ROOT / "data" / "interim" / "discrepancy.parquet"
TOP_PATH = REPO_ROOT / "reports" / "priority_top30.md"
REPORT_PATH = REPO_ROOT / "reports" / "discrepancy.md"
ACCIDENT_SOURCE = "accidents"
TOP_N = 30
TOP_STREETS = 30
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
FIXED_INPUTS = ["speed_ist_kmh", "dtv_official", "separated_cycle_track_present", "lanes_official_in",
                "lanes_official_gegen"]
DIMENSIONS = {"disc_speed": "Tempo", "disc_design": "Gestaltung", "disc_use": "Nutzung"}
RESULT_COLUMNS = ["disc_speed", "disc_design", "disc_use", "disc_max", "disc_type", "disc_causes",
                  "disc_design_unknown", *acc.AGG_COLUMNS, "crash_weighted_per_km", "crash_years", "crash_norm",
                  "school_kita_near", "risk", "risk_weight_available", "priority", "disc_trace"]


# --- inputs ----------------------------------------------------------------------------------


def discrepancy_inputs(rules) -> list[str]:
    cols = set(FIXED_INPUTS)
    for v in rules.discrepancy.design.violations:
        cols |= expr.features_in(expr.parse(v.violated_if))
    return sorted(cols - {"requirement", "lanes_per_dir_max"})


def load_crashes(manifest: dict, src: dict) -> tuple[gpd.GeoDataFrame, dict[int, int]]:
    """All Hamburg crashes of the configured years (in memory only) and the records per year."""
    entry = manifest["sources"].get(ACCIDENT_SOURCE)
    if not entry or entry.get("status") != "ok":
        raise FileNotFoundError("Unfallatlas fehlt im Manifest; zuerst `make fetch`")
    years = [int(y) for y in src["fetch"]["files"]]
    by_layer = {f["layer"]: f for f in entry["files"]}
    parts = []
    for y in years:
        f = by_layer.get(f"zip_{y}")
        if f is None or not (REPO_ROOT / f["path"]).exists():
            raise FileNotFoundError(f"Unfallatlas {y} fehlt in data/raw; zuerst `make fetch`")
        parts.append(acc.read_accidents_zip(REPO_ROOT / f["path"], src["fetch"]["points"]))
    crashes = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=WORK_CRS)
    return crashes, acc.coverage(crashes, years)


def _year_span(cov: dict[int, int]) -> str:
    years = [y for y, n in cov.items() if n > 0]
    return f"{min(years)}–{max(years)}" if years else "–"


# --- computation -----------------------------------------------------------------------------


def assess_frame(df: pd.DataFrame, rules) -> pd.DataFrame:
    """Discrepancy columns for each row (cat_final must be set)."""
    cols = discrepancy_inputs(rules)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"input columns missing: {missing}")
    rows = []
    for values, cat in zip(df[cols].to_dict("records"), df["cat_final"]):
        rows.append(disc.assess_segment(values, cat, rules))
    return pd.DataFrame(rows, index=df.index)


def compute(seg: gpd.GeoDataFrame, crashes: gpd.GeoDataFrame, cov: dict[int, int], rules) -> tuple[pd.DataFrame, dict]:
    """Result columns for the classified segments in the work area; returns (result, crash statistics)."""
    risk_rule = rules.priority.risk
    snap = risk_rule.thresholds["snap_m"].value
    severe = rules.priority.risk_weights[risk_rule.severe_weight_key]
    area = seg[seg["conflated"].astype(bool) & seg["cat_final"].notna()]

    # all segments are candidates, so that crashes at the edge of the work area go to the right segment
    agg_all = acc.aggregate_crashes(seg.geometry, crashes, snap, severe)
    stats = acc.assignment_stats(seg.geometry, crashes, snap)
    stats["in_area"] = int(agg_all.loc[area.index, "crashes_ped_cyc"].sum())
    stats["coverage"] = cov

    res = assess_frame(area, rules)
    agg = agg_all.loc[area.index]
    res = res.join(agg)
    res["crash_weighted_per_km"] = disc.crashes_per_km(agg["crash_weighted"], area["length_m"], rules)
    res["crash_years"] = _year_span(cov)
    risk_in = area[["in_cycle_network", "population_100m_norm", "schools_or_kitas_within_m"]].join(
        res[["crash_weighted_per_km"]])
    res = res.join(disc.risk_frame(risk_in, rules))
    res["priority"] = [disc.priority(m, r) for m, r in zip(res["disc_max"], res["risk"])]

    traces = []
    for i, r in res.iterrows():
        risk_step = {"rule": risk_rule.id, "result": expr.clean_value(r["risk"]), "inputs": {
            "crashes_ped_cyc": int(r["crashes_ped_cyc"]), "crashes_severe_fatal": int(r["crashes_severe_fatal"]),
            "crash_weighted_per_km": expr.clean_value(r["crash_weighted_per_km"]),
            "crash_norm": expr.clean_value(r["crash_norm"]),
            "in_cycle_network": expr.clean_value(area.at[i, "in_cycle_network"]),
            "population_100m_norm": expr.clean_value(area.at[i, "population_100m_norm"]),
            "school_kita_near": expr.clean_value(r["school_kita_near"]),
            "risk_weight_available": expr.clean_value(r["risk_weight_available"])}}
        prio_step = {"rule": "priority", "formula": rules.priority.formula, "result": expr.clean_value(r["priority"]),
                     "inputs": {"disc_max": expr.clean_value(r["disc_max"]), "risk": expr.clean_value(r["risk"])}}
        traces.append(json.dumps([*r["disc_trace"], risk_step, prio_step], ensure_ascii=False, default=_json))
    res["disc_trace"] = traces
    res["disc_causes"] = [json.dumps(c, ensure_ascii=False, default=_json) for c in res["disc_causes"]]
    res["disc_design_unknown"] = [json.dumps(u) for u in res["disc_design_unknown"]]
    for c in ("disc_speed", "disc_design", "disc_use", "disc_max"):
        res[c] = pd.array(res[c].tolist(), dtype="Int64")
    res["priority"] = pd.to_numeric(res["priority"], errors="coerce").astype("float64")
    return res[RESULT_COLUMNS], stats


def _json(v):
    return expr.clean_value(v)


def run_checks(seg: gpd.GeoDataFrame, out: gpd.GeoDataFrame, res: pd.DataFrame, stats: dict) -> list[dict]:
    checks = []

    def add(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    add("segment_id unverändert", list(out["segment_id"]) == list(seg["segment_id"]) and out["segment_id"].is_unique,
        f"{len(out)} Abschnitte")
    sev = res[["disc_speed", "disc_design", "disc_use"]]
    add("Stärken 0–3", ((sev.isna()) | ((sev >= 0) & (sev <= 3))).all().all(), "disc_speed/design/use")
    p = res["priority"].dropna()
    add("Priorität 0–3", ((p >= 0) & (p <= 3)).all(), f"{len(p)} Werte")
    has_cause = res["disc_causes"].map(lambda s: len(json.loads(s)) > 0)
    add("Typ genau bei Diskrepanz", (has_cause == res["disc_type"].notna()).all()
        and ((res["disc_max"].fillna(0) > 0) == has_cause).all(), "disc_type gesetzt ⇔ Ursache vorhanden ⇔ Stärke > 0")
    add("Unfälle vollständig zugeordnet", int(res["crashes_ped_cyc"].sum()) == stats["in_area"]
        and stats["assigned"] + stats["unassigned"] == stats["ped_cyc"],
        f"{stats['assigned']} von {stats['ped_cyc']} Unfällen (Fuß/Rad) einem Abschnitt zugeordnet")
    forbidden = {"UIDENTSTLAE", "LINREFX", "LINREFY", "XGCSWGS84", "YGCSWGS84", "UMONAT", "USTUNDE"}
    add("keine Einzelunfälle im Ergebnis", not (forbidden & set(out.columns))
        and isinstance(out.geometry.iloc[0], type(seg.geometry.iloc[0])), "nur Summen je Abschnitt")
    return checks


# --- plain-text reasons ----------------------------------------------------------------------


def _int(v) -> int | None:
    return None if expr.is_missing(v) else int(v)


def reason_text(r: pd.Series, rules) -> str:
    """Plain German explanation of one segment's priority, e.g. for the Top 30 list."""
    cat = rules.categories[r["cat_final"]]
    soll = "Schrittgeschwindigkeit" if r["cat_final"] == "ETW_ERF" else f"{cat.speed_kmh}" if cat.speed_kmh else None
    parts = [f"Soll {cat.label_de}"]
    for c in json.loads(r["disc_causes"]):
        if c["dimension"] == "speed":
            parts.append(f"heute {c['inputs']['speed_ist_kmh']:.0f} km/h (Soll {soll})")
        elif c["dimension"] == "use":
            parts.append(f"{_fmt(c['inputs']['dtv'])} Kfz/Tag (DTV 2019) über {_fmt(c['inputs'].get('max_dtv_wide', 0))}")
        else:
            parts.append(c["label"])
    cyc, ped, severe = _int(r["crashes_cyc"]), _int(r["crashes_ped"]), _int(r["crashes_severe_fatal"])
    years = r["crash_years"]
    n = _int(r["crashes_ped_cyc"])
    if n:
        word = "Unfall" if n == 1 else "Unfälle"
        crash = (f"{n} {word} mit Radbeteiligung" if not ped else f"{n} {word} mit Fußbeteiligung" if not cyc
                 else f"{n} {word} mit Fuß-/Radbeteiligung (Rad {cyc}, Fuß {ped})")  # one crash may involve both
        parts.append(f"{crash} {years}" + (f", davon {severe} mit Getöteten/Schwerverletzten" if severe else ""))
    else:
        parts.append(f"keine Unfälle mit Fuß-/Radbeteiligung {years}")
    if not expr.is_missing(r.get("in_cycle_network")) and bool(r["in_cycle_network"]):
        parts.append("im Radnetz")
    d = r.get("schools_or_kitas_within_m")
    if not expr.is_missing(d) and r["school_kita_near"] == 1:
        parts.append(f"Schule/Kita in {d:.0f} m")
    return ", ".join(parts)


# --- reports ---------------------------------------------------------------------------------


def _km(x: float) -> str:
    return f"{x / 1000:.1f}"


def _name(v) -> str:
    return v if isinstance(v, str) and v else "–"


def _points(geom):
    mid = geom.interpolate(0.5, normalized=True)
    return mid, gpd.GeoSeries([mid], crs=WORK_CRS).to_crs(4326).iloc[0]


def _links(r, viewers) -> str:
    work, wgs = _points(r.geometry)
    return (f"[Orthophoto]({orthophoto_link(work, viewers)}) · [Panoramax]({panoramax_link(wgs, viewers)}) · "
            f"[OSM]({osm_way_link(r['osm_way_ids'][0])})")


def _licence() -> list[str]:
    return ["## Lizenz", "",
            "Abschnitte und Gestaltungsmerkmale aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale "
            "(Tempo, Verkehrsmengen): Freie und Hansestadt Hamburg, dl-de/by-2.0; Einwohner: Zensus 2022, dl-de/by-2.0; "
            "Unfälle: © Statistische Ämter des Bundes und der Länder, Unfallatlas, dl-de/by-2.0 (nur Summen je Abschnitt). "
            "Orthophotos: LGV Hamburg, dl-de/by-2.0. Panoramax-Bilder: Lizenz je Bild.", ""]


def _type_table(df: pd.DataFrame, cats: list[str]) -> list[str]:
    state = df["disc_type"].fillna(df["disc_max"].map(lambda m: "nicht prüfbar" if pd.isna(m) else "keine"))
    cols = ["D1", "D2", "D3", "keine", "nicht prüfbar"]
    n = pd.crosstab(df["cat_final"], state).reindex(index=cats, columns=cols, fill_value=0)
    km = df.groupby([df["cat_final"], state])["length_m"].sum().unstack(fill_value=0.0).reindex(
        index=cats, columns=cols, fill_value=0.0)
    lines = ["| Soll | " + " | ".join(cols) + " | Summe |", "| --- |" + " ---: |" * (len(cols) + 1)]
    for cat in cats:
        if n.loc[cat].sum() == 0:
            continue
        cells = [f"{n.at[cat, c]} ({_km(km.at[cat, c])} km)" for c in cols]
        lines.append(f"| {cat} | " + " | ".join(cells) + f" | {n.loc[cat].sum()} ({_km(km.loc[cat].sum())} km) |")
    tot = [f"{n[c].sum()} ({_km(km[c].sum())} km)" for c in cols]
    lines.append("| **alle** | " + " | ".join(tot) + f" | {n.values.sum()} ({_km(km.values.sum())} km) |")
    return lines


def street_summary(df: pd.DataFrame, top_ids: set[str]) -> pd.DataFrame:
    """Named streets with priority > 0, grouped by street name and sorted by their highest priority.

    Groups by name only (pieces of one name need not be connected). best_segment_id = segment with the highest priority.
    """
    d = df[(df["priority"] > 0) & df["name"].map(lambda v: isinstance(v, str) and v != "")]
    d = d.sort_values(["priority", "segment_id"], ascending=[False, True])
    rows = []
    for name, g in d.groupby("name", sort=False):
        rows.append({"name": name, "cats": ", ".join(dict.fromkeys(g["cat_final"])), "n_segments": len(g),
                     "length_m": float(g["length_m"].sum()), "max_priority": float(g["priority"].iloc[0]),
                     "crashes_ped_cyc": int(g["crashes_ped_cyc"].sum()),
                     "crashes_severe_fatal": int(g["crashes_severe_fatal"].sum()),
                     "n_in_top": int(g["segment_id"].isin(top_ids).sum()), "best_segment_id": g["segment_id"].iloc[0]})
    return pd.DataFrame(rows, columns=["name", "cats", "n_segments", "length_m", "max_priority", "crashes_ped_cyc",
                                       "crashes_severe_fatal", "n_in_top", "best_segment_id"])


def write_top30(pilot: gpd.GeoDataFrame, ctx: dict) -> None:
    rules, viewers, stats = ctx["rules"], ctx["viewers"], ctx["stats"]
    cats = [c for c in rules.categories if c in set(pilot["cat_final"])]
    top = pilot[pilot["priority"] > 0].sort_values(["priority", "segment_id"], ascending=[False, True]).head(TOP_N)
    cov = stats["coverage"]
    lines = [
        f"# Prioritätenliste – Top {TOP_N} im Bezirk {ctx['pilot']}", "",
        f"Erzeugt: {_now()} von `pipeline/s08_discrepancy.py`, rules.yaml {rules.meta.version}. Nicht amtlicher Entwurf: "
        "Diskrepanz und Priorität sind Vorschläge zur Diskussion, keine Bewertung einzelner Straßen. "
        "**Prüfschritt:** Listen von Ortskundigen gegenlesen (Spalte „Prüfung“), zuerst die Straßenliste.", "",
        f"Priorität = {rules.priority.formula} (0–3). risk = gewichtete Summe aus Unfällen mit Fuß-/Radbeteiligung je km "
        f"(Perzentilrang, Schwere gewichtet), Radnetz, Einwohner und Schule/Kita im Umkreis "
        f"{rules.priority.risk.thresholds['school_kita_radius_m'].value:.0f} m (P-RISK-01). Alle Gewichte sind Annahmen.",
        "", f"Unfalljahre: {', '.join(f'{y} ({_fmt(n)} Unfälle in Hamburg)' for y, n in cov.items())}. "
        + ("Alle Jahre mit Daten für Hamburg." if all(cov.values()) else
           f"**Ohne Hamburg-Daten:** {', '.join(str(y) for y, n in cov.items() if not n)}."), "",
        f"## Top {TOP_STREETS} Straßen", "",
        "Abschnitte mit Priorität > 0, zusammengefasst nach Straßenname (Teile mit gleichem Namen müssen nicht "
        "zusammenhängen; Abschnitte ohne Namen nur in der Abschnittsliste). Links auf den Abschnitt mit der höchsten "
        "Priorität. Prüfung je Straße.", "",
        "| # | Straße | Soll | Abschnitte (km) | davon in Top 30 | Unfälle Fuß/Rad (schwer) | höchste Priorität | "
        "Links | Prüfung |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    streets = street_summary(pilot, set(top["segment_id"])).head(TOP_STREETS)
    by_id = pilot.set_index("segment_id")
    for i, s in enumerate(streets.itertuples(index=False), start=1):
        best = by_id.loc[s.best_segment_id]
        lines.append(f"| {i} | {s.name} | {s.cats} | {s.n_segments} ({_km(s.length_m)}) | {s.n_in_top} | "
                     f"{s.crashes_ped_cyc} ({s.crashes_severe_fatal}) | {s.max_priority:.2f} | {_links(best, viewers)} | ☐ |")
    lines += [
        "", f"## Top {TOP_N} Abschnitte", "",
        "| # | Name | Soll | Typ | Stärke T/G/N | Unfälle Fuß/Rad | Risiko | Priorität | Begründung | Links | Prüfung |",
        "| ---: | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for i, (_, r) in enumerate(top.iterrows(), start=1):
        sev = "/".join("–" if pd.isna(r[c]) else str(int(r[c])) for c in DIMENSIONS)
        lines.append(f"| {i} | {_name(r['name'])} | {r['cat_final']} | {r['disc_type']} | {sev} | "
                     f"{int(r['crashes_ped_cyc'])} | {r['risk']:.2f} | {r['priority']:.2f} | {reason_text(r, rules)} | "
                     f"{_links(r, viewers)} | ☐ |")
    lines += ["", f"Abschnitt-IDs der Liste (für overrides/overrides.csv): "
              + ", ".join(f"`{s}`" for s in top["segment_id"]), "",
              f"## Verteilung der Diskrepanztypen je Kategorie ({ctx['pilot']})", "",
              "Anzahl Abschnitte (km). D1 Erschließungsfunktion mit Durchfluss-Gestaltung, D2 Verbindungsfunktion mit "
              "sparsamer Gestaltung, D3 Mischform (D-TYPE-01). „nicht prüfbar“: keine Dimension entscheidbar.", "",
              *_type_table(pilot, cats), "", *_licence()]
    TOP_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(area: gpd.GeoDataFrame, pilot: gpd.GeoDataFrame, checks: list[dict], ctx: dict) -> None:
    rules, viewers, stats = ctx["rules"], ctx["viewers"], ctx["stats"]
    cats = [c for c in rules.categories if c in set(area["cat_final"])]
    d = rules.discrepancy
    lines = [
        "# Diskrepanz und Priorisierung – Stufe 8", "",
        f"Erzeugt: {_now()} von `pipeline/s08_discrepancy.py`, rules.yaml {rules.meta.version}. Nicht amtlicher Entwurf. "
        f"Top {TOP_N}: `reports/priority_top30.md`.", "",
        "## Prüfungen", "", "| Prüfung | Ergebnis | Detail |", "| --- | --- | --- |",
        *[f"| {c['name']} | {'ok' if c['ok'] else 'FEHLER'} | {c['detail']} |" for c in checks], "",
        "## Kennzahlen", "",
        f"- Bewertet: {_fmt(len(area))} Abschnitte im Arbeitsgebiet ({_km(area['length_m'].sum())} km), davon "
        f"{_fmt(len(pilot))} im Bezirk {ctx['pilot']} ({_km(pilot['length_m'].sum())} km); Grundlage cat_final.",
        f"- Mit Diskrepanz (Stärke > 0): {_fmt((area['disc_max'] > 0).sum())} Abschnitte, "
        f"{_km(area.loc[area['disc_max'] > 0, 'length_m'].sum())} km "
        f"({_pct(area.loc[area['disc_max'] > 0, 'length_m'].sum() / area['length_m'].sum())} der Länge).",
        f"- Nicht prüfbar (keine Dimension entscheidbar): {_fmt(area['disc_max'].isna().sum())} Abschnitte.", "",
        "### Stärke je Dimension (Abschnitte im Arbeitsgebiet)", "",
        "| Dimension | Regel | 0 | 1 | 2 | 3 | nicht prüfbar |", "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for col, label in DIMENSIONS.items():
        vc = area[col].value_counts(dropna=False)
        rule_id = {"disc_speed": d.speed.id, "disc_design": d.design.id, "disc_use": d.use.id}[col]
        lines.append(f"| {label} | {rule_id} | " + " | ".join(str(int(vc.get(k, 0))) for k in (0, 1, 2, 3))
                     + f" | {int(area[col].isna().sum())} |")
    lines += ["", "### Gestaltung: Häufigkeit der Verstöße und unbekannte Prüfungen", "",
              "Fehlende OSM-Tags gelten als unbekannt, nicht als Verstoß (S-FEAT-10).", "",
              "| Soll | Prüfung | Verstoß | kein Verstoß | unbekannt | Anteil unbekannt |",
              "| --- | --- | ---: | ---: | ---: | ---: |"]
    for cat in cats:
        sub = area[area["cat_final"] == cat]
        causes = sub["disc_causes"].map(json.loads)
        unknown = sub["disc_design_unknown"].map(json.loads)
        for v in disc.applicable_violations(cat, rules):
            n_v = int(causes.map(lambda cs: any(c["check"] == v.check for c in cs)).sum())
            n_u = int(unknown.map(lambda u: v.check in u).sum())
            lines.append(f"| {cat} | {v.check}: {v.label_de} | {n_v} | {len(sub) - n_v - n_u} | {n_u} | "
                         f"{_pct(n_u / len(sub)) if len(sub) else '–'} |")
    dtv_known = area["dtv_official"].notna()
    lines += ["", f"Nutzung (D-USE-01): DTV bekannt für {_fmt(dtv_known.sum())} von {_fmt(len(area))} Abschnitten "
              f"(nur Hauptverkehrsstraßen, Stand 2019); geprüft nur für Kategorien mit max_dtv (GOW30).", "",
              "### Verteilung der Diskrepanztypen je Kategorie (Arbeitsgebiet)", "", *_type_table(area, cats), "",
              "## Unfälle (Unfallatlas)", "",
              "| Jahr | Unfälle mit Personenschaden in Hamburg |", "| --- | ---: |",
              *[f"| {y} | {_fmt(n) if n else 'keine Daten'} |" for y, n in stats["coverage"].items()], "",
              f"- Unfälle mit Fuß- oder Radbeteiligung in Hamburg: {_fmt(stats['ped_cyc'])}; davon "
              f"{_fmt(stats['assigned'])} einem Abschnitt zugeordnet (höchstens "
              f"{rules.priority.risk.thresholds['snap_m'].value:.0f} m entfernt), {_fmt(stats['unassigned'])} nicht "
              "(kein Abschnitt im Umkreis, z. B. Unfälle auf Wegen, Plätzen oder Parkplätzen außerhalb des Kfz-Netzes).",
              f"- Im Arbeitsgebiet: {_fmt(stats['in_area'])} Unfälle auf {_fmt((area['crashes_ped_cyc'] > 0).sum())} "
              f"Abschnitten; davon {_fmt(int(area['crashes_severe_fatal'].sum()))} mit Getöteten oder Schwerverletzten.",
              "- Gespeichert werden nur Summen je Abschnitt (crashes_ped_cyc, crashes_ped, crashes_cyc, "
              "crashes_severe_fatal, crash_weighted). Unfälle an Knoten zählen bei genau einem anliegenden Abschnitt.",
              "- Unfallatlas enthält nur polizeilich erfasste Unfälle mit Personenschaden; Alleinunfälle von "
              "Radfahrenden sind untererfasst.", "",
              f"## Stichprobe ({SAMPLE_SIZE} zufällige Abschnitte mit Bewertung in {ctx['pilot']}, Seed {SAMPLE_SEED})", "",
              "| segment_id | Name | Soll | Typ | Stärke T/G/N | Priorität | Begründung | Links |",
              "| --- | --- | --- | --- | --- | ---: | --- | --- |"]
    checked = pilot[pilot["disc_max"].notna()]
    rnd = random.Random(SAMPLE_SEED)
    idx = sorted(rnd.sample(list(checked.index), min(SAMPLE_SIZE, len(checked))))
    for _, r in checked.loc[idx].iterrows():
        sev = "/".join("–" if pd.isna(r[c]) else str(int(r[c])) for c in DIMENSIONS)
        prio = "–" if pd.isna(r["priority"]) else f"{r['priority']:.2f}"
        lines.append(f"| `{r['segment_id']}` | {_name(r['name'])} | {r['cat_final']} | {r['disc_type'] if isinstance(r['disc_type'], str) else '–'} | {sev} | "
                     f"{prio} | {reason_text(r, rules)} | {_links(r, viewers)} |")
    lines += ["", *_licence()]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --- main ------------------------------------------------------------------------------------


def main() -> int:
    rules = load_rules()
    with open(PROJECT_PATH, encoding="utf-8") as f:
        pilot_name = yaml.safe_load(f)["pilot_district"]["name"]
    with open(SOURCES_PATH, encoding="utf-8") as f:
        src = yaml.safe_load(f)["sources"][ACCIDENT_SOURCE]
    if not IN_PATH.exists():
        print("discrepancy: data/interim/final.parquet missing; run `make coherence` first", file=sys.stderr)
        return 1
    seg = gpd.read_parquet(IN_PATH)
    try:
        crashes, cov = load_crashes(load_manifest(), src)
    except (FileNotFoundError, ValueError) as exc:
        print(f"discrepancy: {exc}", file=sys.stderr)
        return 1
    print(f"discrepancy: {len(crashes)} crashes in Hamburg, per year {cov}")

    res, stats = compute(seg, crashes, cov, rules)
    del crashes  # single crashes are not kept beyond this point
    out = seg.join(res)
    checks = run_checks(seg, out, res, stats)
    area = out.loc[res.index]
    pilot = area[area["bezirk"] == pilot_name]
    ctx = {"rules": rules, "pilot": pilot_name, "viewers": load_viewers(), "stats": stats}
    write_report(area, pilot, checks, ctx)
    for c in checks:
        print(f"discrepancy: {c['name']}: {c['ok']} ({c['detail']})")
    if not all(c["ok"] for c in checks):
        print(f"discrepancy: check(s) failed, outputs not written; see {REPORT_PATH}", file=sys.stderr)
        return 1
    write_top30(pilot, ctx)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_PATH, index=False)
    types = area["disc_type"].value_counts().to_dict()
    print(f"discrepancy: types {types}; -> {OUT_PATH.relative_to(REPO_ROOT)}, {TOP_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
