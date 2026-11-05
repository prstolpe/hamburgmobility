"""Validation and sensitivity (guide Teil 7, prompts/12_validation.md).

Usage: uv run python -m pipeline.validate   (make validate; runs after make discrepancy, before make export)

Reads data/interim/discrepancy.parquet, config/rules.yaml (section validation), the manual sample files in
reports/ and docs/open_questions.md. Writes
  data/interim/validation.parquet   per segment: sens_change_rate, sens_uncertain, sens_alt_category,
                                    sens_alt_share, sens_oat_changes (JSON); read by pipeline/s09_export.py
  reports/validation.md             report for review and publication
  reports/validation_metrics.json   key figures (compared with the previous run)
The Monte-Carlo runs take a few minutes. The run stops with exit code 1 if a check fails; outputs are then
not written (the report is).
"""

import json
import sys
import time

import geopandas as gpd
import numpy as np
import pandas as pd

from pipeline.lib.area import area_label, district_names, sample_by_district
from pipeline.lib import sensitivity as sens
from pipeline.lib import validation as val
from pipeline.lib.crs import WORK_CRS
from pipeline.lib.harmonise import harmonise
from pipeline.lib.links import load_viewers, orthophoto_link, osm_way_link, panoramax_link
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_rules
from pipeline.s04_features import _fmt, _now, _pct
from pipeline.s05b_harmonise import approved_override_ids, street_strokes

IN_PATH = REPO_ROOT / "data" / "interim" / "discrepancy.parquet"
OUT_PATH = REPO_ROOT / "data" / "interim" / "validation.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "validation.md"
METRICS_PATH = REPO_ROOT / "reports" / "validation_metrics.json"
# Pilot run (Eimsbüttel, rules.yaml 0.12.0), saved before the first city-wide run; not in git.
BASELINE_PATH = REPO_ROOT / "data" / "baseline" / "eimsbuettel_discrepancy.parquet"
BASELINE_DISTRICT = "Eimsbüttel"
OPEN_QUESTIONS = REPO_ROOT / "docs" / "open_questions.md"
OVERRIDES = REPO_ROOT / "overrides" / "overrides.csv"
SAMPLES = {"conflation": REPO_ROOT / "reports" / "conflation_sample.csv",
           "classification": REPO_ROOT / "reports" / "classification_sample.csv",
           "transects": REPO_ROOT / "reports" / "transect_sample.geojson"}
OUT_COLUMNS = ["segment_id", "sens_change_rate", "sens_uncertain", "sens_alt_category", "sens_alt_share",
               "sens_oat_changes", "sens_rules_version"]
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
TOP_N = 30  # Top 30 of reports/priority_top30.md
URBAN_CATS = ["SW", "GOW50", "GOW30", "ETW30", "ETW_ERF"]


def _km(x: float) -> str:
    return f"{x:.1f}".replace(".", ",")


def _p(x: float) -> str:
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else _pct(x).replace(".", ",")


def _g(x: float) -> str:
    """Number in German notation, e.g. 0,6."""
    return f"{x:g}".replace(".", ",")


def _name(v) -> str:
    return v if isinstance(v, str) and v else "–"


# --- sensitivity -----------------------------------------------------------------------------


def harmonise_step(area_g: gpd.GeoDataFrame, rules):
    """Post step for the sensitivity runs: H-STR-01 on the strokes of the work area (computed once)."""
    strokes = street_strokes(area_g, rules, cat_col="cat_cascade")
    ids, lengths = area_g["segment_id"].tolist(), dict(zip(area_g["segment_id"], area_g["length_m"]))
    locked = approved_override_ids()

    def post(cats: pd.Series, r) -> pd.Series:
        new, _ = harmonise(strokes, dict(zip(ids, cats)), lengths, r, locked=locked)
        return pd.Series([new[i] for i in ids], index=cats.index, dtype="object")
    return post


def run_sensitivity(area: pd.DataFrame, rules, post=None) -> dict:
    v = rules.validation
    delta1 = v.rule("V-SENS-01").thresholds["delta"].value
    mc = v.rule("V-SENS-02")
    delta2 = mc.thresholds["delta"].value
    min_rate = v.rule("V-UNC-01").thresholds["min_change_rate"].value
    params = sens.varied_parameters(rules)
    base = area["cat_proposed"]

    t0 = time.time()
    oat_params = [p for p in params if p.effect == "category"]
    oat = sens.one_at_a_time(area, rules, oat_params, delta1, post)
    print(f"validate: one-at-a-time {len(oat.columns)} runs in {time.time() - t0:.0f} s")

    groups = set()
    if "thresholds" in mc.vary:
        groups.add("threshold")
    if "weights" in mc.vary:
        groups |= {"conn_weight", "risk_weight"}
    mc_params = [p for p in params if p.group in groups and p.effect != "confidence"]
    factors = sens.sample_factors(mc.runs, len(mc_params), delta2, mc.seed)
    t0 = time.time()

    def progress(i):
        if (i + 1) % 50 == 0:
            print(f"validate: Monte Carlo {i + 1}/{mc.runs} ({time.time() - t0:.0f} s)")

    runs = sens.monte_carlo(area, rules, mc_params, factors, progress, post)
    summary = sens.change_summary(base, runs, min_rate)
    prio = sens.priority_runs(area, rules, mc_params, factors)
    return {"params": params, "oat_params": oat_params, "oat": oat, "mc_params": mc_params, "factors": factors,
            "runs": runs, "summary": summary, "priority_runs": prio, "delta1": delta1, "delta2": delta2,
            "min_rate": min_rate, "n_runs": mc.runs, "seed": mc.seed}


def _transitions(base: pd.Series, other: pd.Series, length: pd.Series) -> str:
    changed = other.ne(base)
    if not changed.any():
        return "–"
    t = pd.DataFrame({"f": base[changed], "t": other[changed], "m": length[changed]}).groupby(["f", "t"])["m"].sum()
    t = t.sort_values(ascending=False)
    return ", ".join(f"{f}→{to} {_km(m / 1000)}" for (f, to), m in t.head(3).items())


# --- checks ----------------------------------------------------------------------------------


def run_checks(area: pd.DataFrame, rules, res: dict, base_cats: pd.Series, base_prio: pd.Series) -> list[dict]:
    checks = []

    def add(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    diff = int(base_cats.ne(area["cat_proposed"]).sum())
    add("Basislauf reproduziert cat_proposed", diff == 0, f"{diff} Abweichungen bei {len(area)} Abschnitten")
    stored = pd.to_numeric(area["priority"], errors="coerce")
    close = np.isclose(base_prio.to_numpy(dtype=float), stored.to_numpy(dtype=float), atol=1e-9, equal_nan=True)
    add("Basislauf reproduziert die Priorität", close.all(), f"{int((~close).sum())} Abweichungen")
    add("segment_id eindeutig", area["segment_id"].is_unique, f"{len(area)} Abschnitte")
    add("Monte-Carlo-Läufe vollständig", res["runs"].shape == (len(area), res["n_runs"]) and not res["runs"].isna().any().any(),
        f"{res['runs'].shape[1]} Läufe, Seed {res['seed']}")
    return checks


# --- report ----------------------------------------------------------------------------------


def _crosstab_lines(t: pd.DataFrame) -> list[str]:
    lines = ["| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil an HVS-km |",
             "| --- | ---: | ---: | ---: | ---: | ---: |"]
    hvs_total = t["HVS"].sum()
    for cat, row in t.iterrows():
        if row.sum() == 0:
            continue
        lines.append(f"| {cat} | {_km(row['HVS'])} | {_km(row['keine HVS'])} | {_km(row['unbekannt'])} | "
                     f"{_km(row.sum())} | {_p(row['HVS'] / hvs_total) if hvs_total else '–'} |")
    lines.append(f"| **Summe** | {_km(t['HVS'].sum())} | {_km(t['keine HVS'].sum())} | {_km(t['unbekannt'].sum())} | "
                 f"{_km(t.values.sum())} | |")
    return lines


def _street_lines(groups: pd.DataFrame, limit: int | None = None) -> list[str]:
    if groups.empty:
        return ["_keine_"]
    lines = ["| Bezirk | Straße | Soll | highway | Abschnitte | km | Beispiel |", "| --- | --- | --- | --- | ---: | ---: | --- |"]
    shown = groups if limit is None else groups.head(limit)
    for _, g in shown.iterrows():
        lines.append(f"| {g['bezirk']} | {g['name']} | {g['cats']} | {g['highways']} | {g['n']} | {_km(g['km'])} | `{g['example']}` |")
    if limit is not None and len(groups) > limit:
        lines.append(f"| … | {len(groups) - limit} weitere Straßen | | | {int(groups['n'].iloc[limit:].sum())} | "
                     f"{_km(groups['km'].iloc[limit:].sum())} | |")
    return lines


def section_hvs(area: pd.DataFrame, districts: list[str]) -> tuple[list[str], dict]:
    pilot_name = area_label(districts)
    t_all = val.crosstab_km(area, URBAN_CATS)
    t_pilot = val.crosstab_km(area[area["bezirk"].isin(districts)], URBAN_CATS)
    hvs_other, district_gow50 = val.hvs_deviations(area)
    hvs_km = t_all["HVS"].sum()
    gow_share = (t_all.loc["GOW50", "HVS"] + t_all.loc["GOW30", "HVS"]) / hvs_km if hvs_km else float("nan")
    lines = ["## 1. Abgleich mit dem HVS-Netz", "",
             "Kreuztabelle Soll-Kategorie (`cat_final`) × Hauptverkehrsstraße (`in_hvs`, DTV-Linien 2019, S-CONF-04). "
             "Erwartung (guide.md 7.1): fast alle HVS-km sind GOW50 oder GOW30; HVS als ETW30 und Bezirksstraßen als "
             "GOW50 einzeln begründen.", "",
             f"**Kennzahl: {_p(gow_share)} der HVS-km im Arbeitsgebiet sind GOW50 oder GOW30.**", "",
             "### Arbeitsgebiet gesamt (km)", "", *_crosstab_lines(t_all), "",
             f"### {pilot_name} (km)", "", *_crosstab_lines(t_pilot), "",
             "### Je Bezirk", "",
             "| Bezirk | km | HVS km | davon GOW50/GOW30 | HVS außerhalb GOW50/GOW30 km | Bezirksstraßen mit GOW50 km |",
             "| --- | ---: | ---: | ---: | ---: | ---: |"]
    bez = area["bezirk"].map(lambda b: b if isinstance(b, str) else val.NO_DISTRICT)
    for b in [*sorted(set(bez) - {val.NO_DISTRICT}), val.NO_DISTRICT]:
        g = area[bez == b]
        if g.empty:
            continue
        t = val.crosstab_km(g, URBAN_CATS)
        h = t["HVS"].sum()
        gs = (t.loc["GOW50", "HVS"] + t.loc["GOW30", "HVS"]) / h if h else float("nan")
        ho, dg = val.hvs_deviations(g)
        lines.append(f"| {b} | {_km(g['length_m'].sum() / 1000)} | {_km(h)} | {_p(gs)} | {_km(ho['length_m'].sum() / 1000)} | "
                     f"{_km(dg['length_m'].sum() / 1000)} |")
    lines += ["", f"### Abweichung A: HVS-Abschnitte außerhalb GOW50/GOW30 ({len(hvs_other)} Abschnitte, "
              f"{_km(hvs_other['length_m'].sum() / 1000)} km)", "",
              "Nach Kategorie: " + (", ".join(f"{c} {len(g)} ({_km(g['length_m'].sum() / 1000)} km)"
                                              for c, g in hvs_other.groupby("cat_final")) or "keine") + ". "
              "SW auf HVS (Autobahnzubringer) ist fachlich folgerichtig; ETW30 und ETW_ERF auf HVS einzeln begründen.", "",
              *_street_lines(val.street_groups(hvs_other)), "",
              f"### Abweichung B: Bezirksstraßen mit GOW50 ({len(district_gow50)} Abschnitte, "
              f"{_km(district_gow50['length_m'].sum() / 1000)} km)", "",
              "Bezirksstraße = keine HVS und keine Autobahn. Grund ist immer C-GOW-01 über conn_score ohne GOW30-Auslöser. "
              "Kurze Stücke von Hauptstraßen deuten auf Lücken im HVS-Abgleich (nur match exact) hin.", "",
              *_street_lines(val.street_groups(district_gow50), limit=40), ""]
    return lines, {"hvs_km": hvs_km, "hvs_gow_share": gow_share, "hvs_other_km": hvs_other["length_m"].sum() / 1000,
                   "district_gow50_km": district_gow50["length_m"].sum() / 1000}


def section_tempo(area: pd.DataFrame, rules) -> tuple[list[str], dict]:
    t = val.speed_table_km(area, URBAN_CATS)
    res = val.etw30_tempo(area, rules)
    out = res["outliers"]
    known = res["km_total"] - res["km_unknown"]
    share = res["km_at_or_below"] / known if known else float("nan")
    cand = out[out["data_error_candidate"]]
    lines = ["## 2. Soll-ETW30 und Ist-Tempo", "",
             f"Ist-Tempo = amtliches Regeltempo vor OSM maxspeed (S-FEAT-09). Soll-Tempo ETW30 = "
             f"{res['soll_kmh']} km/h (categories.ETW30). Erwartung: hoher Anteil; Ausreißer sind Kandidaten für Datenfehler.", "",
             f"**Kennzahl: {_p(share)} der Soll-ETW30-km mit bekanntem Ist-Tempo haben heute höchstens {res['soll_kmh']} km/h** "
             f"({_km(res['km_at_or_below'])} von {_km(known)} km; Ist-Tempo unbekannt: {_km(res['km_unknown'])} km).", "",
             "### Soll × Ist-Tempo (km, Arbeitsgebiet)", "",
             "| Soll | " + " | ".join(val.SPEED_BUCKETS) + " |", "| --- |" + " ---: |" * len(val.SPEED_BUCKETS)]
    for cat, row in t.iterrows():
        if row.sum():
            lines.append(f"| {cat} | " + " | ".join(_km(row[b]) for b in val.SPEED_BUCKETS) + " |")
    hint_counts = out["hints"].explode().dropna().value_counts()
    lines += ["", f"### Ausreißer: Soll-ETW30 mit Ist-Tempo über {res['soll_kmh']} km/h ({len(out)} Abschnitte, "
              f"{_km(out['length_m'].sum() / 1000)} km)", "",
              f"Davon **{len(cand)} Abschnitte ({_km(cand['length_m'].sum() / 1000)} km) mögliche Datenfehler**: mindestens ein "
              "Hinweis widerspricht dem Ist-Tempo oder der Kategorie (Zone 30 laut Zonenebene, Quellen widersprechen sich, nur "
              "OSM-Tempo, HVS-Abgleich nur teilweise, kein amtlicher Abgleich). Die übrigen sind Wohn- oder Sammelstraßen mit "
              "Tempo 50 ohne Widerspruch in den Daten – dort ist die Diskrepanz fachlich gemeint (D-SPD-01).", "",
              "| Hinweis | Abschnitte |", "| --- | ---: |", *[f"| {k} | {_fmt(n)} |" for k, n in hint_counts.items()], "",
              "Mögliche Datenfehler nach Straße (längste zuerst, höchstens 30):", ""]
    if cand.empty:
        lines += ["_keine_"]
    else:
        lines += ["| Bezirk | Straße | Abschnitte | km | Ist km/h | Hinweise | Beispiel |", "| --- | --- | --- | ---: | ---: | --- | --- |"]
        c = cand.assign(name=cand["name"].map(_name), bezirk=cand["bezirk"].map(lambda b: b if isinstance(b, str) else val.NO_DISTRICT))
        grp = sorted(c.groupby(["bezirk", "name"]), key=lambda kv: (-kv[1]["length_m"].sum(), kv[0]))
        for (b, n), g in grp[:30]:
            hints = pd.Series([h for hs in g["hints"] for h in hs]).value_counts()
            lines.append(f"| {b} | {n} | {len(g)} | {_km(g['length_m'].sum() / 1000)} | "
                         f"{', '.join(str(int(x)) for x in sorted(set(g['speed_ist_kmh'].dropna())))} | "
                         f"{', '.join(f'{k} ({v})' for k, v in hints.items())} | `{g['segment_id'].iloc[0]}` |")
        if len(grp) > 30:
            lines.append(f"| … | {len(grp) - 30} weitere Straßen | | | | | |")
    lines.append("")
    return lines, {"etw30_t30_share": share, "etw30_outlier_km": out["length_m"].sum() / 1000,
                   "etw30_data_error_candidates": len(cand)}


def section_sensitivity(area: pd.DataFrame, rules, res: dict, districts: list[str], viewers: dict, geoms) -> tuple[list[str], dict]:
    pilot_name = area_label(districts)
    base, length = area["cat_proposed"], area["length_m"]
    summ = res["summary"]
    total_km = length.sum() / 1000
    unc = summ["uncertain"]
    lines = ["## 3. Sensitivitätsanalyse", "",
             f"Geprüft wird die Automatik (`cat_proposed`: Kaskade und Harmonisierung H-STR-01 je Lauf); fachliche "
             f"Korrekturen bleiben außen vor. "
             f"Basis: rules.yaml {rules.meta.version}, {_fmt(len(area))} Abschnitte, {_km(total_km)} km.", "",
             f"### 3.1 Einzelvariation (V-SENS-01): jede Annahme ±{res['delta1'] * 100:.0f} %", "",
             "km mit anderer Kategorie als im Basislauf. Varianten: Annahme-Schwellen der Kaskade und `required_width` in "
             "ihren Bedingungen; zusätzlich die Gewichte von conn_score.", "",
             "| Annahme | Regel | Basis | −20 %: km | Abschnitte | häufigste Wechsel | +20 %: km | Abschnitte | häufigste Wechsel |",
             "| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- |"]
    oat_km = {}
    for p in res["oat_params"]:
        cells = []
        for s in ("-", "+"):
            col = res["oat"][f"{p.key}:{s}"]
            ch = col.ne(base)
            km = length[ch].sum() / 1000
            oat_km[f"{p.key}:{s}"] = km
            cells += [_km(km), _fmt(int(ch.sum())), _transitions(base, col, length)]
        lines.append(f"| `{p.key}` | {p.source} | {_g(p.base)} | " + " | ".join(cells) + " |")
    conf = [p for p in res["params"] if p.effect == "confidence"]
    lines += ["", "Nur auf die confidence wirken: " + ", ".join(f"`{p.key}` ({_g(p.base)}, {p.source})" for p in conf)
              + ". Sie ändern die Kategorie nicht und werden nicht variiert.", "",
              "Nicht variiert (Annahmen früherer Stufen oder ohne Wirkung auf die Kategorie):", "",
              "| Annahme | Wert | Einheit | Grund |", "| --- | ---: | --- | --- |"]
    for f in sens.fixed_assumptions(rules):
        lines.append(f"| `{f['path']}` | {_g(f['value'])} | {f['unit']} | {f['reason']} |")

    mc_groups = sorted({p.group for p in res["mc_params"]})
    rate = summ["change_rate"]
    lines += ["", f"### 3.2 Monte-Carlo (V-SENS-02): {res['n_runs']} Läufe, Seed {res['seed']}", "",
              f"Je Lauf wird jede der {len(res['mc_params'])} Annahmen ({', '.join(mc_groups)}) unabhängig mit einem Faktor "
              f"gleichverteilt in [{_g(1 - res['delta2'])}; {_g(1 + res['delta2'])}] multipliziert. Wechselquote je Abschnitt = Anteil der Läufe "
              f"mit anderer Kategorie. **„unsicher“ ab Wechselquote {_g(res['min_rate'])} (V-UNC-01).**", "",
              f"**Kennzahl: {_fmt(int(unc.sum()))} Abschnitte ({_km(length[unc].sum() / 1000)} km, "
              f"{_p(length[unc].sum() / length.sum())} der Länge) sind unsicher.** "
              f"Mindestens einmal gewechselt: {_fmt(int((rate > 0).sum()))} Abschnitte ({_km(length[rate > 0].sum() / 1000)} km).", "",
              "| Wechselquote | Abschnitte | km |", "| --- | ---: | ---: |"]
    bins = [("0 (stabil)", rate == 0), ("über 0 bis 0,1", (rate > 0) & (rate <= 0.1)),
            (f"über 0,1 bis unter {_g(res['min_rate'])}", (rate > 0.1) & ~unc), (f"ab {_g(res['min_rate'])} (unsicher)", unc)]
    for label, m in bins:
        lines.append(f"| {label} | {_fmt(int(m.sum()))} | {_km(length[m].sum() / 1000)} |")
    lines += ["", "Unsichere Abschnitte je Soll-Kategorie (Basis) und häufigste andere Kategorie:", "",
              "| Kategorie | km gesamt | unsicher km | Anteil | häufigste andere Kategorie (km) |", "| --- | ---: | ---: | ---: | --- |"]
    for cat in URBAN_CATS:
        m = base == cat
        if not m.any():
            continue
        u = m & unc
        alt = summ.loc[u, "alt_category"].value_counts()
        alt_txt = ", ".join(f"{a} ({_km(length[u & (summ['alt_category'] == a)].sum() / 1000)})" for a in alt.index) or "–"
        lines.append(f"| {cat} | {_km(length[m].sum() / 1000)} | {_km(length[u].sum() / 1000)} | "
                     f"{_p(length[u].sum() / length[m].sum())} | {alt_txt} |")
    bez = area["bezirk"].map(lambda b: b if isinstance(b, str) else val.NO_DISTRICT)
    lines += ["", "Je Bezirk:", "", "| Bezirk | km | unsicher km | Anteil |", "| --- | ---: | ---: | ---: |"]
    for b in [*sorted(set(bez) - {val.NO_DISTRICT}), val.NO_DISTRICT]:
        m = bez == b
        if m.any():
            lines.append(f"| {b} | {_km(length[m].sum() / 1000)} | {_km(length[m & unc].sum() / 1000)} | "
                         f"{_p(length[m & unc].sum() / length[m].sum())} |")

    # which parameters drive the changes: correlation of factor with "category changed" per run share
    changed_share = res["runs"].ne(base, axis=0).mul(length, axis=0).sum(axis=0) / length.sum()
    lines += ["", "Einfluss je Annahme im Monte-Carlo (Korrelation des Faktors mit dem Anteil gewechselter km je Lauf; "
              "nur zur Orientierung, nicht kausal):", "", "| Annahme | Korrelation |", "| --- | ---: |"]
    infl = []
    for j, p in enumerate(res["mc_params"]):
        if p.effect != "category":
            continue
        f = res["factors"][:, j]
        c = float(np.corrcoef(f, changed_share.to_numpy())[0, 1]) if changed_share.std() > 0 else float("nan")
        infl.append((p.key, c))
    for k, c in sorted(infl, key=lambda kv: -abs(kv[1]) if not np.isnan(kv[1]) else 0):
        lines.append(f"| `{k}` | {c:+.2f} |".replace(f"{c:+.2f}", f"{c:+.2f}".replace(".", ",")))

    # priority
    pilot_mask = area["bezirk"].isin(districts).to_numpy()
    base_prio = pd.to_numeric(area["priority"], errors="coerce")
    stab = sens.top_stability(base_prio[pilot_mask], res["priority_runs"][pilot_mask], area["segment_id"][pilot_mask], TOP_N)
    stays = pd.Series(stab["stay_share"])
    lines += ["", f"### 3.3 Priorität: Top {TOP_N} in {pilot_name} bei variierten Gewichten", "",
              f"Gleiche Läufe; risk mit variierten `priority.risk_weights`, Diskrepanzen aus dem Basislauf (eine geänderte "
              f"Kategorie ändert auch die Diskrepanz – das ist hier nicht abgebildet). Im Mittel bleiben "
              f"**{_p(stab['mean_overlap'])} der Top {TOP_N}** in der Top {TOP_N}. "
              f"{int((stays >= 0.9).sum())} Abschnitte bleiben in mindestens 90 % der Läufe, {int((stays < 0.5).sum())} in weniger "
              f"als der Hälfte.", ""]

    sample_lines = ["", f"### 3.4 Stichprobe: {SAMPLE_SIZE} zufällige unsichere Abschnitte in {pilot_name}, nach Bezirk geschichtet (Seed {SAMPLE_SEED})", "",
                    "Zur Durchsicht: Welche Kategorie ist fachlich richtig? Befund als Korrektur in overrides/overrides.csv.", ""]
    pick = list(sample_by_district(area[pilot_mask & unc.to_numpy()], SAMPLE_SIZE, SAMPLE_SEED).index)
    if not pick:
        sample_lines += ["_keine_"]
    else:
        sample_lines += ["| segment_id | Bezirk | Straße | highway | Soll | andere Kategorie | Wechselquote | Wechsel bei ±20 % | Orthophoto | Panoramax | OSM |",
                         "| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |"]
        for i in pick:
            r = area.loc[i]
            mid = geoms.loc[i].interpolate(0.5, normalized=True)
            wgs = gpd.GeoSeries([mid], crs=WORK_CRS).to_crs(4326).iloc[0]
            oat = r["_oat"]
            sample_lines.append(f"| `{r['segment_id']}` | {r['bezirk']} | {_name(r['name'])} | {r['highway']} | {r['cat_proposed']} | "
                                f"{summ.loc[i, 'alt_category']} ({_p(summ.loc[i, 'alt_share'])}) | {_g(round(summ.loc[i, 'change_rate'], 3))} | "
                                f"{', '.join(f'`{x}`' for x in oat) or '–'} | [DOP]({orthophoto_link(mid, viewers)}) | "
                                f"[Bilder]({panoramax_link(wgs, viewers)}) | [Way]({osm_way_link(r['osm_way_ids'][0])}) |")
    lines += sample_lines + [""]
    return lines, {"uncertain_n": int(unc.sum()), "uncertain_km": length[unc].sum() / 1000,
                   "uncertain_share_km": length[unc].sum() / length.sum(),
                   "changed_any_n": int((rate > 0).sum()), "top30_mean_overlap": stab["mean_overlap"],
                   "oat_km": oat_km}


def section_quality(area: pd.DataFrame, rules) -> tuple[list[str], dict]:
    q = val.data_quality(area)
    max_missing = rules.validation.rule("V-DQ-01").thresholds["max_missing_speed_share"].value
    total = q[q["bezirk"] == val.TOTAL].iloc[0]
    lines = ["## 4. Datenqualität je Bezirk", "",
             "Conflation-Trefferquote = Anteil der km mit amtlichem Gegenstück (match_quality exact oder partial, S-CONF-01). "
             "OSM-Tag-Vollständigkeit = Anteil der Abschnitte mit bekanntem Wert (S-FEAT-10; fehlende Tags heißen unbekannt). "
             "DTV gibt es nur auf Hauptverkehrsstraßen (2019); weil `in_hvs` selbst aus den DTV-Linien stammt (S-CONF-04), "
             "fehlt DTV auf HVS nie. Aussagekräftiger ist der Anteil der OSM-Hauptstraßen (primary, secondary) ohne DTV: "
             "Kandidaten für Lücken im HVS-Abgleich.", "",
             "| Bezirk | Abschnitte | km | Conflation-Treffer (km) | davon exact | OSM-Tags Mittel | ohne Ist-Tempo | Hauptstraßen (OSM) | davon ohne DTV | alle ohne DTV |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for _, r in q.iterrows():
        lines.append(f"| {r['bezirk']} | {_fmt(r['n'])} | {_km(r['km'])} | {_p(r['conflation_hit_km'])} | {_p(r['conflation_exact_km'])} | "
                     f"{_p(r['osm_tags_mean'])} | {_p(r['missing_speed'])} | {_fmt(r['main_n'])} | {_p(r['main_missing_dtv'])} | "
                     f"{_p(r['missing_dtv'])} |")
    lines += ["", "OSM-Tag-Vollständigkeit je Merkmal (Anteil der Abschnitte mit bekanntem Wert):", "",
              "| Bezirk | " + " | ".join(val.OSM_TAG_COLUMNS.values()) + " |", "| --- |" + " ---: |" * len(val.OSM_TAG_COLUMNS)]
    for _, r in q.iterrows():
        lines.append(f"| {r['bezirk']} | " + " | ".join(_p(r[f'tag_{c}']) for c in val.OSM_TAG_COLUMNS) + " |")
    ok = total["missing_speed"] < max_missing
    lines += ["", f"Abschnitte ohne Ist-Tempo: {_p(total['missing_speed'])} (Ziel unter {_p(max_missing)}, V-DQ-01, guide.md 3.4): "
              f"**{'erfüllt' if ok else 'nicht erfüllt'}**.", "",
              "Auf der Webseite zeigt die Ampel „Datenunsicherheit“ je Abschnitt fehlende und unsichere Eingangswerte (C-CONF-01); "
              "neu ist der Hinweis „unsicher“ aus der Sensitivitätsanalyse.", ""]
    return lines, {"conflation_hit_km": float(total["conflation_hit_km"]), "osm_tags_mean": float(total["osm_tags_mean"]),
                   "missing_speed": float(total["missing_speed"]), "missing_speed_ok": bool(ok),
                   "main_missing_dtv": float(total["main_missing_dtv"])}


def _sample_lines(title: str, s: pd.DataFrame, max_share: float, group_label: str) -> list[str]:
    alle = s[s["group"] == "alle"].iloc[0]
    lines = [f"**{title}:** {int(alle['reviewed'])} von {int(alle['n'])} Zeilen geprüft"
             + (f", {int(alle['disputed'])} strittig ({_p(alle['disputed_share'])})." if alle["reviewed"] else " – **Durchsicht offen**.")]
    if alle["reviewed"]:
        lines += ["", f"| {group_label} | Zeilen | geprüft | strittig | Anteil | unter {_p(max_share)}? |", "| --- | ---: | ---: | ---: | ---: | --- |"]
        for _, r in s.iterrows():
            verdict = "–" if not r["reviewed"] else ("ja" if r["disputed_share"] < max_share else "**nein**")
            lines.append(f"| {r['group']} | {r['n']} | {r['reviewed']} | {r['disputed']} | {_p(r['disputed_share'])} | {verdict} |")
    return lines + [""]


def section_samples(rules) -> tuple[list[str], dict]:
    max_share = rules.validation.rule("V-SAMP-01").thresholds["max_disputed_share"].value
    lines = ["## 5. Manuelle Stichproben", "",
             f"Ziel (V-SAMP-01, guide.md 7.1): unter {_p(max_share)} fachlich strittig je Kategorie. Stand der Dateien in reports/:", ""]
    stats = {}
    if SAMPLES["conflation"].exists():
        s = val.sample_summary(pd.read_csv(SAMPLES["conflation"]), "match_quality")
        lines += _sample_lines("Conflation (reports/conflation_sample.csv, Spalte check_ok)", s, max_share, "match_quality")
        stats["conflation_reviewed"] = int(s.iloc[-1]["reviewed"])
    if SAMPLES["classification"].exists():
        s = val.sample_summary(pd.read_csv(SAMPLES["classification"]), "cat_proposed", expected_col="cat_expected_manual")
        lines += _sample_lines("Klassifikation (reports/classification_sample.csv, Spalten check_ok, cat_expected_manual)",
                               s, max_share, "Kategorie")
        stats["classification_reviewed"] = int(s.iloc[-1]["reviewed"])
    if SAMPLES["transects"].exists():
        t = val.transect_summary(gpd.read_file(SAMPLES["transects"]))
        diff = f", mittlere Abweichung {t['mean_abs_diff_m']:.1f} m".replace(".", ",") if t["mean_abs_diff_m"] is not None else ""
        lines += [f"**Transekte (reports/transect_sample.geojson, Spalte measured_m):** {t['measured']} von {t['n']} nachgemessen"
                  + (diff + "." if t["measured"] else " – **Durchsicht offen**."), ""]
        stats["transects_measured"] = t["measured"]
    ov = pd.read_csv(OVERRIDES) if OVERRIDES.exists() else pd.DataFrame(columns=["review_status"])
    approved = int((ov["review_status"] == "approved").sum())
    lines += [f"**Korrekturen (overrides/overrides.csv):** {len(ov)} Einträge, davon {approved} approved. "
              "**Rückmeldungen von Ortskundigen:** noch keine (Rückmeldekanal nicht eingerichtet, docs/open_questions.md).", ""]
    stats["overrides"] = len(ov)
    return lines, stats


def section_status(stats: dict) -> list[str]:
    done = lambda ok: "erledigt" if ok else "**offen**"  # noqa: E731
    samples_done = stats.get("classification_reviewed", 0) > 0
    return ["## Stand der Prüfungen nach guide.md 7.1", "",
            "Veröffentlichungsreif erst, wenn Abgleich HVS-Netz, Stichproben vor Ort, Sensitivitätsanalyse und eine "
            "Rückmelderunde mit Ortskundigen dokumentiert sind. Auch dann bleibt der Plan ein Diskussionsentwurf.", "",
            "| Prüfung | Stand | Abschnitt |", "| --- | --- | --- |",
            "| Abgleich HVS-Netz | erledigt (automatisch); Abweichungen einzeln begründen: **offen** | 1 |",
            "| Abgleich mit Ist-Tempo | erledigt (automatisch); Datenfehler-Kandidaten prüfen: **offen** | 2 |",
            f"| Stichproben vor Ort | {done(samples_done)} | 5 |",
            "| Sensitivitätsanalyse | erledigt | 3 |",
            "| Datenqualität | erledigt | 4 |",
            "| Ortskundige (Bezirksgruppen, Feuerwehr, Busbetrieb) | **offen** | 5 |",
            "| Externe Fachprüfung (Hochschule oder Planungsbüro) | **offen** – dieser Bericht ist die Grundlage | – |", ""]


def section_baseline(area: pd.DataFrame) -> list[str]:
    """Eimsbüttel: pilot run (normalised over Eimsbüttel + 500 m) vs. this run (normalised over Hamburg)."""
    head = ["## Vergleich mit dem Pilotlauf Eimsbüttel", ""]
    if not BASELINE_PATH.exists():
        return head + [f"_Kein Pilotlauf unter `{BASELINE_PATH.relative_to(REPO_ROOT)}`._", ""]
    base = pd.read_parquet(BASELINE_PATH, columns=["segment_id", "bezirk", "cat_final", "priority", "length_m"])
    base = base[(base["bezirk"] == BASELINE_DISTRICT) & base["cat_final"].notna()]
    cur = area[area["bezirk"] == BASELINE_DISTRICT]
    r = val.compare_baseline(base, cur, TOP_N)
    lines = head + [
        "Pilotlauf: rules.yaml 0.12.0, Normierung über Eimsbüttel + 500 m. Jetzt: Normierung über ganz Hamburg "
        "(S-FEAT-01), Schwellen unverändert. Verglichen werden Abschnitte mit gleicher segment_id.", "",
        f"- Abschnitte in beiden Läufen: {r['n_common']}; nur im Pilotlauf: {r['n_only_base']}; nur jetzt: {r['n_only_new']}",
        f"- Kategorie (cat_final) geändert: {r['n_changed']} Abschnitte, {_km(r['km_changed'])} km "
        f"({_p(r['km_changed'] / r['km_common']) if r['km_common'] else '–'} der Länge)",
        f"- Top {TOP_N} der Priorität: {_p(r['top_overlap'])} sind in beiden Läufen in der Top {TOP_N}", ""]
    if r["changes"].empty:
        return lines + ["_keine Kategoriewechsel_", ""]
    lines += ["| vorher | jetzt | Abschnitte | km |", "| --- | --- | ---: | ---: |"]
    lines += [f"| {x['from']} | {x['to']} | {x['n']} | {_km(x['km'])} |" for x in r["changes"].to_dict("records")]
    return lines + [""]


def section_limits(area: pd.DataFrame, metrics: dict) -> list[str]:
    no_dtv = float(area["dtv_official"].isna().mean())
    return ["## 6. Grenzen", "",
            "### Fachlich (guide.md 7.2)", "",
            "- Die niederländischen Kategorien passen nicht eins zu eins auf RIN/RASt; die Zuordnung ist eine Näherung.",
            "- Die GOW30-Merkmale der CROW (2023) sind ausdrücklich vorläufig; ihre Wirkung wird erst evaluiert.",
            "- Ein Soll-Plan sagt wenig über die Umsetzung: Richtlinien werden oft nicht eingehalten (SWOV 2023).",
            f"- Multifunktionale Hauptstraßen landen konsequent in GOW30: {_p(1 - metrics['hvs_gow50_share'])} der HVS-km in "
            "GOW50/GOW30 sind GOW30 – fachlich folgerichtig, politisch der härteste Punkt.",
            "- Busbetrieb, Rettungswege und Wirtschaftsverkehr sind nur Overlays; Fahrzeitwirkungen sind nicht modelliert.", "",
            "### Rechtlich (guide.md 7.3)", "",
            "- Der Plan ist kein Verwaltungsakt und keine Anordnung; Tempo auf Hauptverkehrsstraßen setzt weiter die "
            "Voraussetzungen der StVO voraus.",
            "- GOW30 begründet in Deutschland derzeit kein flächiges Tempo 30 auf Hauptverkehrsstraßen; es kann Einzelfälle "
            "und ein Gesamtkonzept begründen.",
            "- Lizenzen: dl-de/by-2.0- und ODbL-Pflichten; für die amtlichen Tempo- und Verkehrsmengendaten fehlt die Lizenzangabe "
            "in der API (offen). Unfälle nur als Summen je Abschnitt.", "",
            "### Methodisch (guide.md 7.4 und dieser Lauf)", "",
            f"- Kfz-Verkehrsstärken fehlen auf {_p(no_dtv)} der Abschnitte (DTV nur auf HVS, Stand 2019); Betweenness bildet "
            "Verkehr nicht ab.",
            f"- HVS aus den DTV-Linien 2019 statt der HVS-Karte 2023 (S-CONF-04); Lücken im Abgleich erzeugen Abweichungen in Abschnitt 1.",
            f"- OSM-Attribute sind ungleich vollständig (im Mittel {_p(metrics['osm_tags_mean'])} der Gestaltungsmerkmale bekannt); "
            "die Ist-Gestaltung und damit die Diskrepanz ist dort unsicher.",
            "- Unfallatlas: nur polizeilich erfasste Unfälle mit Personenschaden; Alleinunfälle mit dem Rad sind untererfasst.",
            "- Annahme-Schwellen sind Setzungen. Die Sensitivitätsanalyse zeigt ihren Einfluss, ersetzt aber keine fachliche "
            "Abstimmung. Annahmen früherer Stufen (Conflation, Merkmale, Querschnitt) sind nicht variiert (Abschnitt 3.1).",
            "- Die Monte-Carlo-Faktoren sind unabhängig und gleichverteilt; Abhängigkeiten zwischen Annahmen sind nicht abgebildet.", ""]


def section_open_questions() -> list[str]:
    lines = ["## Offene Fragen (docs/open_questions.md)", "", "Alle noch offenen Punkte, nach Abschnitt:", ""]
    if not OPEN_QUESTIONS.exists():
        return lines + ["_Datei fehlt_", ""]
    for section, items in val.open_questions(OPEN_QUESTIONS.read_text(encoding="utf-8")):
        lines += [f"**{section}** ({len(items)})", "", *[f"- {i}" for i in items], ""]
    return lines


def write_report(parts: list[list[str]], checks: list[dict], rules, metrics: dict, previous: dict | None) -> None:
    head = ["# Validierung und Sensitivität", "",
            f"Erzeugt: {_now()} von `pipeline/validate.py`, rules.yaml {rules.meta.version}. Nicht amtlicher Diskussionsentwurf: "
            "Die Automatik schlägt vor, Menschen entscheiden. Grundlage für die externe Fachprüfung (guide.md Teil 7).", "",
            "## Kurzfassung", "",
            f"- HVS-Abgleich: {_p(metrics['hvs_gow_share'])} der HVS-km sind GOW50 oder GOW30; "
            f"{_km(metrics['hvs_other_km'])} km HVS außerhalb, {_km(metrics['district_gow50_km'])} km Bezirksstraßen mit GOW50.",
            f"- Ist-Tempo: {_p(metrics['etw30_t30_share'])} der Soll-ETW30-km (mit bekanntem Tempo) haben heute höchstens 30 km/h; "
            f"{metrics['etw30_data_error_candidates']} Ausreißer sind mögliche Datenfehler.",
            f"- Sensitivität: {_fmt(metrics['uncertain_n'])} Abschnitte ({_km(metrics['uncertain_km'])} km, "
            f"{_p(metrics['uncertain_share_km'])} der Länge) sind „unsicher“; die Top {TOP_N} der Priorität bleiben im Mittel zu "
            f"{_p(metrics['top30_mean_overlap'])} gleich.",
            f"- Datenqualität: Conflation-Treffer {_p(metrics['conflation_hit_km'])} der km, OSM-Gestaltungsmerkmale im Mittel "
            f"{_p(metrics['osm_tags_mean'])} bekannt, ohne Ist-Tempo {_p(metrics['missing_speed'])}.",
            "- Manuelle Stichproben, Rückmelderunde und externe Prüfung sind offen.", ""]
    if previous:
        prev = previous.get("hvs_gow_share")
        if prev is not None:
            head += [f"Vergleich mit dem vorigen Lauf ({previous.get('generated', '?')}, rules.yaml {previous.get('rules_version', '?')}): "
                     f"HVS-km als GOW50/GOW30 {_p(prev)} → {_p(metrics['hvs_gow_share'])}; unsicher "
                     f"{_fmt(previous.get('uncertain_n', 0))} → {_fmt(metrics['uncertain_n'])} Abschnitte. Eine Abbruchgrenze für "
                     "einen Rückgang (guide.md 3.4) ist nicht festgelegt (docs/open_questions.md).", ""]
    head += ["## Prüfungen dieses Laufs", "", "| Prüfung | Ergebnis | Detail |", "| --- | --- | --- |",
             *[f"| {c['name']} | {'ok' if c['ok'] else 'FEHLER'} | {c['detail']} |" for c in checks], ""]
    tail = ["## Lizenz", "",
            "Abschnitte aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale (Tempo, Verkehrsmengen, "
            "ALKIS): Freie und Hansestadt Hamburg, dl-de/by-2.0 bzw. laut Quelle; Unfälle: © Statistische Ämter des Bundes und "
            "der Länder, Unfallatlas (nur Summen je Abschnitt). Orthophotos: LGV Hamburg, dl-de/by-2.0.", ""]
    body = [line for part in parts for line in part]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(head + body + tail), encoding="utf-8")


# --- main ------------------------------------------------------------------------------------


def main() -> int:
    rules = load_rules()
    districts = district_names()
    if not IN_PATH.exists():
        print("validate: data/interim/discrepancy.parquet missing; run `make discrepancy` first", file=sys.stderr)
        return 1
    seg = gpd.read_parquet(IN_PATH)
    area_g = seg[seg["conflated"].astype(bool) & seg["cat_final"].notna()]
    geoms = area_g.geometry
    area = pd.DataFrame(area_g.drop(columns="geometry"))
    print(f"validate: {len(area)} segments in the work area")

    post = harmonise_step(area_g, rules)
    base_cats = sens.categories(area, rules, post)
    base_prio = sens.priorities(area, rules)
    res = run_sensitivity(area, rules, post)
    checks = run_checks(area, rules, res, base_cats, base_prio)
    area["_oat"] = sens.oat_changes(area["cat_proposed"], res["oat"])

    viewers = load_viewers()
    hvs_lines, m1 = section_hvs(area, districts)
    t = val.crosstab_km(area, URBAN_CATS)
    gow_hvs = t.loc["GOW50", "HVS"] + t.loc["GOW30", "HVS"]
    m1["hvs_gow50_share"] = t.loc["GOW50", "HVS"] / gow_hvs if gow_hvs else float("nan")
    tempo_lines, m2 = section_tempo(area, rules)
    sens_lines, m3 = section_sensitivity(area, rules, res, districts, viewers, geoms)
    dq_lines, m4 = section_quality(area, rules)
    sample_lines, m5 = section_samples(rules)
    metrics = {**m1, **m2, **m3, **m4, **m5}
    parts = [section_status(m5), hvs_lines, tempo_lines, sens_lines, dq_lines, sample_lines, section_baseline(area),
             section_limits(area, metrics), section_open_questions()]
    previous = json.loads(METRICS_PATH.read_text(encoding="utf-8")) if METRICS_PATH.exists() else None
    write_report(parts, checks, rules, metrics, previous)

    for c in checks:
        print(f"validate: {c['name']}: {c['ok']} ({c['detail']})")
    if not all(c["ok"] for c in checks):
        print(f"validate: check(s) failed, outputs not written; see {REPORT_PATH}", file=sys.stderr)
        return 1

    summ = res["summary"]
    out = pd.DataFrame({
        "segment_id": area["segment_id"], "sens_change_rate": summ["change_rate"].astype("float64"),
        "sens_uncertain": summ["uncertain"].astype(bool), "sens_alt_category": summ["alt_category"],
        "sens_alt_share": summ["alt_share"].astype("float64"),
        "sens_oat_changes": area["_oat"].map(lambda x: json.dumps(x)), "sens_rules_version": rules.meta.version,
    })[OUT_COLUMNS]
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_PATH, index=False)
    metrics_out = {"generated": _now(), "rules_version": rules.meta.version, "runs": res["n_runs"], "seed": res["seed"],
                   **{k: (round(v, 6) if isinstance(v, float) else v) for k, v in metrics.items() if k != "oat_km"},
                   "oat_km": {k: round(v, 3) for k, v in metrics["oat_km"].items()}}
    METRICS_PATH.write_text(json.dumps(metrics_out, ensure_ascii=False, indent=2, default=float) + "\n", encoding="utf-8")
    print(f"validate: {metrics['uncertain_n']} uncertain segments ({metrics['uncertain_km']:.1f} km)")
    print(f"validate: -> {OUT_PATH.relative_to(REPO_ROOT)}, {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
