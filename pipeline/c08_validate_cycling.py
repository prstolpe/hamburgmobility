"""Cycle stage 8: validation of the cycle network, facilities, cross sections and junctions (prompts/21).

Usage: uv run python -m pipeline.c08_validate_cycling

1. Soll network vs. official Radnetz Hamburg (km, overlap, deviations per Bezirk; buffer C-NET-13).
2. Model vs. counters (cross-sections and fit as in prompt 15, plus the Soll category at each counter).
3. Sensitivity: every assumption value in cycling_rules.yaml and design_rules.yaml ±delta (rules.yaml V-SENS-01),
   one at a time; facility (c05), Soll cross section (c06) and junction type (c07) are rerun on their stored inputs.
   Share of segments with another facility or lane count and of junctions with another type.
4. Review samples of prompts 17-20 and 30 new random samples; open questions and limits.
Writes reports/validation_cycling.md, reports/validation_cycling_review.csv and data/interim/validation_cycling.parquet
(per segment and junction: number of runs with a change, for the website profiles). Exit code 1 if a check fails.
"""

import datetime as dt
import json
import sys
import time

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml

from config.schema.cycling_model import NO_CYCLE_CATEGORY, CyclingRuleSet
from config.schema.design_model import DesignRuleSet
from pipeline import c05_facility as c05
from pipeline import c06_cross_section_soll as c06
from pipeline.c02_cycle_demand import cross_sections
from pipeline.c04_principles import _links
from pipeline.lib import cycle_demand as cd
from pipeline.lib import cycling_validation as cv
from pipeline.lib import facility as fa
from pipeline.lib import junctions as jn
from pipeline.lib import parallel
from pipeline.lib import profile as pf
from pipeline.lib import validation as val
from pipeline.lib.area import read_districts, sample_by_district
from pipeline.lib.crs import WORK_CRS
from pipeline.lib.cycle_network import NetworkParams
from pipeline.lib.links import load_viewers
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import DEFAULT_CYCLING_RULES_PATH, DEFAULT_DESIGN_RULES_PATH, load_rules

INTERIM = REPO_ROOT / "data" / "interim"
RAW = REPO_ROOT / "data" / "raw"
FINAL_PATH = INTERIM / "final.parquet"
NETWORK_PATH = INTERIM / "cycle_network.parquet"
FACILITY_PATH = INTERIM / "cycle_facility.parquet"
XS_PATH = INTERIM / "cross_section_soll.parquet"
JUNCTIONS_PATH = INTERIM / "junctions.parquet"
OFFICIAL_PATH = RAW / "cycle_network_official__radnetz.parquet"
OUT_PATH = INTERIM / "validation_cycling.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "validation_cycling.md"
REVIEW_PATH = REPO_ROOT / "reports" / "validation_cycling_review.csv"
OPEN_QUESTIONS = REPO_ROOT / "docs" / "open_questions.md"
REVIEW_CSVS = {"Prompt 17 – Routen (Prinzipien)": REPO_ROOT / "reports" / "cycle_principles_review.csv",
               "Prompt 20 – Knotenpunkte": REPO_ROOT / "reports" / "junctions_review.csv"}
SAMPLE_REPORTS = {"Prompt 18 – Führungsform": ("reports/cycle_facility.md", "30 je Soll-Führung"),
                  "Prompt 19 – Soll-Querschnitt": ("reports/cross_section_soll.md", "70 Skizzen (30 Zufall, 20 breiteste, 20 schmalste)"),
                  "Prompt 20 – Knotenpunkte": ("reports/junctions.md", "30 Zufall, Prüfliste je Soll-Typ")}
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
TOP_PARAMS = 25
TOP_COUNTERS = 15
TRIGGERS_PER_ROW = 3
STAGES = ("c05", "c06", "c07")
FAC_COLS = ["segment_id", "name", "bezirk", "length_m", "cat_final", "dtv_official", "cycle_cat_final", "cyc_peak_h_dir",
            "cyc_peak_h", "cycle_facility_soll", "cycle_facility_ist", "facility_gap", "geometry"]
FINAL_COLS = ["segment_id", "cat_final", "dtv_official", "width_p10_m", "lanes", "lanes_official_in", "lanes_official_gegen",
              "bahnigkeit_official", "parking", "shop_frontage_share"]
BUILD_FLAGS = {"dtv_partial", "dtv_unknown", "cycle_path_ignored"}  # flags c07 sets while building the legs


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _fmt(v, digits: int = 0) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "–"
    return f"{v:,.{digits}f}".replace(",", " ").replace(".", ",")


def _pct(v, digits: int = 1) -> str:
    return "–" if v is None or not np.isfinite(v) else f"{v * 100:.{digits}f} %".replace(".", ",")


# --- rerun chain c05 -> c06 -> c07 on stored inputs ---------------------------------------------------------


class Chain:
    """Stored inputs of the stages c05-c07 and a rerun with other rule sets (no OSM, GTFS or routing)."""

    def __init__(self, fac: pd.DataFrame, final: pd.DataFrame, xs: pd.DataFrame, j: pd.DataFrame, rules):
        self.rules = rules
        self.fac = fac
        self.final = final.loc[fac.index]
        self.bus = xs["bus_peak_h_dir"].reindex(fac.index).to_numpy(dtype="float64")
        self.tram = xs["tram_present"].reindex(fac.index).fillna(False).astype(bool).to_numpy()
        base_fac = xs["cycle_facility_final"].where(xs["cycle_facility_final"].notna(), None).to_dict()
        self.junctions = []
        for r in j.itertuples(index=False):
            legs = json.loads(r.legs)
            reps = cv.arm_rep_ids(legs, base_fac)
            flags = [x for x in (r.conflict_flags.split("|") if isinstance(r.conflict_flags, str) else []) if x in BUILD_FLAGS]
            space = None if np.isnan(r.space_radius_m) else float(r.space_radius_m)
            if space is None:
                flags.append("space_unknown")
            self.junctions.append({"legs": legs, "reps": reps, "entering_dtv_sum": r.entering_dtv_sum,
                                   "tram_present": bool(r.tram_present), "space_radius_m": space,
                                   "signal_present_ist": bool(r.signal_present_ist), "flags": flags})
        self.node_ids = j["node_id"].astype(str).to_numpy()

    def facility(self, cyc: CyclingRuleSet) -> pd.DataFrame:
        p = fa.FacilityParams.from_rules(cyc)
        f = self.fac
        res = [c05.evaluate(a, b, c, d, e, None, p) for a, b, c, d, e in
               zip(f["cat_final"], f["cycle_cat_final"], f["dtv_official"], f["cyc_peak_h_dir"], f["cyc_peak_h"])]
        return pd.DataFrame({"cycle_cat_final": f["cycle_cat_final"], "cycle_facility_soll": [r["cycle_facility"] for r in res],
                             "cycle_facility_fallback": [r["cycle_facility_fallback"] for r in res],
                             "cycle_width_soll_m": [r["cycle_width_m"] for r in res],
                             "cyc_peak_h_dir": f["cyc_peak_h_dir"], "cyc_peak_h": f["cyc_peak_h"]}, index=f.index)

    def profile(self, fac: pd.DataFrame, des: DesignRuleSet, cyc: CyclingRuleSet) -> pd.DataFrame:
        p = pf.ProfileParams.from_rules(des, cyc, self.rules)
        rows = []
        for (sid, f), b, t in zip(self.final.iterrows(), self.bus, self.tram):
            seg = c06.segment_input(f, fac.loc[sid], b, t, p)
            res = pf.evaluate_profile(seg, f["width_p10_m"], p)
            rows.append((res.cycle_facility, c06._lanes_str(res.lanes), res.fit_class))
        return pd.DataFrame(rows, columns=["facility", "lanes", "fit"], index=fac.index)

    def junction_types(self, facility: pd.Series, des: DesignRuleSet, dtv_scale: float = 1.0) -> pd.Series:
        p = jn.JunctionParams.from_rules(des, self.rules)
        fac = facility.where(facility.notna(), None).to_dict()
        out = []
        for jd in self.junctions:
            legs = [{**leg, "facility": fac.get(rep, leg.get("facility")) if rep else leg.get("facility")}
                    for leg, rep in zip(jd["legs"], jd["reps"])]
            dtv = jd["entering_dtv_sum"]
            props = {**jd, "legs": legs, "flags": list(jd["flags"]),
                     "entering_dtv_sum": None if dtv is None or np.isnan(dtv) else float(dtv) * dtv_scale}
            out.append(jn.decide(props, p)["junction_type_soll"])
        return pd.Series(out, index=self.node_ids, dtype=object)

    def run(self, cyc, des, base: dict | None = None, start: str = "c05", dtv_scale: float = 1.0) -> dict:
        """Facility (final, after the cross section), lanes, fit per segment and Soll type per junction; stages before
        `start` are taken from `base`."""
        if start == "c05":
            fac = self.facility(cyc)
        if start in ("c05", "c06"):
            prof = self.profile(fac if start == "c05" else base["fac"], des, cyc)
        else:
            prof = base["profile"]
        return {"fac": fac if start == "c05" else base["fac"], "profile": prof,
                "junction": self.junction_types(prof["facility"], des, dtv_scale)}


# --- 1. official network ---------------------------------------------------------------------------------------


def section_official(net: gpd.GeoDataFrame, districts: gpd.GeoDataFrame, p: NetworkParams) -> tuple[list[str], dict]:
    official = gpd.read_parquet(OFFICIAL_PATH).to_crs(WORK_CRS)
    t = cv.official_by_district(net, official, districts, p.compare_buffer_m, p.official_status, p.planned_status)
    ham = t[t["bezirk"] == "Hamburg"].iloc[0]
    lines = ["## 1. Soll-Radnetz und amtliches Radnetz Hamburg", "",
             f"Amtlich = WFS „Radnetz Hamburg“ (BVM, dl-de/by-2.0), Status {', '.join(p.official_status)}; geplant = "
             f"{', '.join(p.planned_status)}. Überdeckung = Länge im Puffer {_fmt(p.compare_buffer_m)} m (C-NET-13) um das "
             "jeweils andere Netz; amtliche Linien an den Bezirksgrenzen geschnitten. Das amtliche Netz ist Startpunkt und "
             "Vergleichsebene, nicht Ziel (docs/guide_radnetz.md, Abschnitt 1).", "",
             f"- Amtlicher Bestand: {_fmt(ham['official_km'], 1)} km; davon {_pct(ham['official_on_soll_hr_share'])} am Soll-Netz "
             f"RSV/HAUPT und {_pct(ham['official_on_soll_any_share'])} am Soll-Netz bis BASIS.",
             f"- Soll RSV/HAUPT: {_fmt(ham['soll_hr_km'], 1)} km; davon {_pct(ham['soll_hr_on_official_share'])} am amtlichen "
             f"Bestand, {_fmt(ham['soll_hr_additional_km'], 1)} km zusätzlich.",
             f"- Amtlich geplant: {_fmt(ham['planned_km'], 1)} km; davon {_fmt(ham['planned_on_soll_hr_km'], 1)} km am Soll RSV/HAUPT.", "",
             "| Bezirk | amtlich Bestand km | am Soll RSV/HAUPT | am Soll bis BASIS | fehlt im Soll RSV/HAUPT km | Soll RSV/HAUPT km | davon am Bestand | zusätzlich km | geplant km | geplant am Soll RSV/HAUPT km |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in t.itertuples(index=False):
        b = f"**{r.bezirk}**" if r.bezirk == "Hamburg" else r.bezirk
        lines.append(f"| {b} | {_fmt(r.official_km, 1)} | {_pct(r.official_on_soll_hr_share)} | {_pct(r.official_on_soll_any_share)} | "
                     f"{_fmt(r.official_km - r.official_on_soll_hr_km, 1)} | {_fmt(r.soll_hr_km, 1)} | {_pct(r.soll_hr_on_official_share)} | "
                     f"{_fmt(r.soll_hr_additional_km, 1)} | {_fmt(r.planned_km, 1)} | {_fmt(r.planned_on_soll_hr_km, 1)} |")
    lines += ["", "Karte und längste Abweichungen (amtlich ohne Soll RSV/HAUPT, Soll RSV/HAUPT ohne amtlichen Bestand): "
              "reports/cycle_network.md, Abschnitt „Vergleich mit dem amtlichen Radnetz“.", "",
              "![Soll vs. amtliches Radnetz](cycle_network_compare.png)", "",
              "Lesart: Das Soll-Netz ist mit den Delfter Maschenweiten deutlich dichter als das amtliche Netz "
              "(docs/open_questions.md, Prompt 16). Ein hoher Anteil „zusätzlich“ ist deshalb erwartet; wichtig sind die "
              "amtlichen Abschnitte, die im Soll fehlen – sie sind Prüffälle für den Netzentwurf.", ""]
    return lines, {"official_km": float(ham["official_km"]), "official_on_soll_hr_share": float(ham["official_on_soll_hr_share"]),
                   "official_on_soll_any_share": float(ham["official_on_soll_any_share"]), "soll_hr_km": float(ham["soll_hr_km"])}


# --- 2. counters -----------------------------------------------------------------------------------------------


def section_counters(net: gpd.GeoDataFrame, districts: gpd.GeoDataFrame, cyc: CyclingRuleSet, viewers) -> tuple[list[str], dict]:
    params = cd.DemandParams.from_rules(cyc)
    cs = cross_sections(params, net.reset_index(drop=True), net["cyc_calibrated"].to_numpy(dtype="float64"), districts)
    cat_of = net.set_index("edge_id")["cycle_cat_final"]
    rank = {c: i for i, c in enumerate(("RSV", "HAUPT", "BASIS", "ERSCHL"))}
    cs["soll_cat"] = [min((cat_of.get(e) for e in ids if cat_of.get(e) in rank), key=rank.get, default=NO_CYCLE_CATEGORY)
                      for ids in cs["edge_ids"]]
    fit = cd.fit_stats(cs["count_weekday"].to_numpy(), cs["model"].fillna(0).to_numpy())
    lines = ["## 2. Modell und Zählstellen", "",
             f"Wie Prompt 15 (reports/cycle_demand.md): {cs.attrs['n_stations']} Zählstellen, davon {cs.attrs['n_undirected']} "
             f"ohne Richtung; {len(cs)} Querschnitte mit mindestens {params.min_valid_weekdays} gültigen Werktagen 2025. "
             "Modellwert = kalibrierte Radfahrten je Werktag (Summe beider Richtungen) der Kanten, die der Querschnitt schneidet. "
             "Die Kalibrierung nutzt dieselben Zählstellen; die Werte sind deshalb keine unabhängige Prüfung.", "",
             "| Kennzahl | Wert |", "| --- | ---: |",
             f"| Querschnitte mit Zähl- und Modellwert | {fit['n']} |",
             f"| Spearman (Rang) | {_fmt(fit['spearman'], 2)} |",
             f"| Pearson (log) | {_fmt(fit['pearson_log'], 2)} |",
             f"| mittlere relative Abweichung | {_pct(fit['mrd'])} |",
             f"| Median Zählwert/Modell | {_fmt(fit['median_ratio'], 2)} |",
             f"| Anteil innerhalb Faktor 2 | {_pct(fit['share_within_factor_2'])} |", "",
             "Zählwerte nach Soll-Kategorie am Querschnitt (höchste Kategorie der geschnittenen Kanten). Erwartung: höhere "
             "Kategorien liegen an stärker befahrenen Querschnitten.", "",
             "| Soll-Kategorie | Querschnitte | Median Zählwert Rad/Werktag | Median Modell | geom. Mittel Zählwert/Modell |",
             "| --- | ---: | ---: | ---: | ---: |"]
    ok = cs[(cs["count_weekday"] > 0) & (cs["model"] > 0)]
    for c in [*rank, NO_CYCLE_CATEGORY]:
        g = cs[cs["soll_cat"] == c]
        go = ok[ok["soll_cat"] == c]
        gm = float(np.exp(np.mean(np.log(go["count_weekday"] / go["model"])))) if len(go) else float("nan")
        lines.append(f"| {c} | {len(g)} | {_fmt(g['count_weekday'].median())} | {_fmt(g['model'].median())} | {_fmt(gm, 2)} |")
    top = cs.sort_values("count_weekday", ascending=False).head(TOP_COUNTERS)
    lines += ["", f"Die {TOP_COUNTERS} stärksten Zählstellen und ihre Soll-Kategorie:", "",
              "| Zählstelle | Bezirk | Zählwert | Modell | Soll-Kategorie | Prüfen |", "| --- | --- | ---: | ---: | --- | --- |"]
    for r in top.itertuples(index=False):
        lines.append(f"| {r.name} | {r.bezirk if isinstance(r.bezirk, str) else '–'} | {_fmt(r.count_weekday)} | {_fmt(r.model)} | "
                     f"{r.soll_cat} | {_links(r.geometry, viewers)} |")
    by_cat = {c: int((cs["soll_cat"] == c).sum()) for c in [*rank, NO_CYCLE_CATEGORY]}
    top_hr = float(top["soll_cat"].isin(("RSV", "HAUPT")).mean()) if len(top) else float("nan")
    off_hr = top[~top["soll_cat"].isin(("RSV", "HAUPT"))]
    lines += ["", f"Von den {TOP_COUNTERS} stärksten Zählstellen liegen {_pct(top_hr)} am Soll RSV/HAUPT."]
    if len(off_hr):
        lines.append("Prüffälle (stark befahren, aber nicht im Soll RSV/HAUPT; Modellwert meist weit unter dem Zählwert, "
                     "siehe Lesart in Prompt 15): " + "; ".join(f"{r.name} ({r.soll_cat}, {_fmt(r.count_weekday)} gezählt, "
                                                             f"{_fmt(r.model)} modelliert)" for r in off_hr.itertuples(index=False)) + ".")
    lines.append("")
    return lines, {**{f"counter_{k}": v for k, v in fit.items()}, "counters_by_cat": by_cat, "top_counters_on_hr": top_hr}


# --- 3. sensitivity --------------------------------------------------------------------------------------------


def run_sensitivity(chain: Chain, raw_c: dict, raw_d: dict, cyc, des, delta: float, length: pd.Series, tick) -> dict:
    params = cv.assumption_params(raw_c, "cycling") + cv.assumption_params(raw_d, "design")
    varied = [p for p in params if p.skip is None and p.stage]
    base = chain.run(cyc, des)
    seg_ids, node_ids = chain.fac.index, chain.node_ids
    counts = {"fac": np.zeros(len(seg_ids), int), "lanes": np.zeros(len(seg_ids), int), "junction": np.zeros(len(node_ids), int)}
    triggers = {"fac": [[] for _ in seg_ids], "lanes": [[] for _ in seg_ids], "junction": [[] for _ in node_ids]}
    rows, n_runs = [], 0
    share_param = "junctions.method.[J-M-02].dtv_share_entering.value"
    jobs = [(p, factor) for p in varied for factor in (1 - delta, 1 + delta)]

    def run_job(i: int):
        p, factor = jobs[i]
        new = p.value * factor
        try:
            if p.file == "cycling":
                cyc_v, des_v = CyclingRuleSet.model_validate(cv.with_value(raw_c, p.path, new)), des
            else:
                cyc_v, des_v = cyc, DesignRuleSet.model_validate(cv.with_value(raw_d, p.path, new))
        except ValueError as exc:  # pydantic.ValidationError is a ValueError
            return {"invalid": str(exc).splitlines()[0]}
        res = chain.run(cyc_v, des_v, base, p.stage, factor if p.key == share_param else 1.0)
        return {"fac": res["profile"]["facility"], "lanes": res["profile"]["lanes"], "fit": res["profile"]["fit"],
                "junction": res["junction"]}

    def progress(i: int):
        if i % 2 == 1:
            tick(f"sensitivity {i // 2 + 1}/{len(varied)}: {jobs[i][0].key}")

    results = parallel.pmap(run_job, len(jobs), progress=progress)  # in job order: same report as a serial run
    for k, p in enumerate(varied):
        row = {"param": p, "runs": {}}
        for j, factor in enumerate((1 - delta, 1 + delta)):
            res = results[2 * k + j]
            if "invalid" in res:
                row["runs"][factor] = res
                continue
            n_runs += 1
            out = {}
            for kind, b, r, w in (("fac", base["profile"]["facility"], res["fac"], length),
                                  ("lanes", base["profile"]["lanes"], res["lanes"], length),
                                  ("fit", base["profile"]["fit"], res["fit"], length),
                                  ("junction", base["junction"], res["junction"], pd.Series(1.0, index=node_ids))):
                out[kind] = cv.change_share(b, r, w)
                if kind in counts:
                    changed = (b.astype(object).fillna("\0").to_numpy() != r.astype(object).fillna("\0").to_numpy())
                    counts[kind] += changed
                    label = f"{p.key} {'−' if factor < 1 else '+'}{delta:.0%}"
                    for i in np.flatnonzero(changed):
                        if len(triggers[kind][i]) < TRIGGERS_PER_ROW:
                            triggers[kind][i].append(label)
            row["runs"][factor] = out
        rows.append(row)
    return {"params": params, "varied": varied, "rows": rows, "n_runs": n_runs, "base": base, "counts": counts,
            "triggers": triggers}


def section_sensitivity(sens: dict, delta: float) -> tuple[list[str], dict]:
    params, rows = sens["params"], sens["rows"]

    def eff(row, factor, kind):
        r = row["runs"].get(factor, {})
        return r.get(kind, (np.nan, np.nan))

    def max_eff(row):
        return max([eff(row, f, k)[1] for f in (1 - delta, 1 + delta) for k in ("fac", "lanes", "fit")] +
                   [eff(row, f, "junction")[0] for f in (1 - delta, 1 + delta)], default=0)

    ranked = sorted(rows, key=lambda r: -np.nan_to_num(max_eff(r)))
    n_struct = sum(p.skip == "structural" for p in params)
    n_zero = sum(p.skip == "zero" for p in params)
    not_rerun = [p for p in params if p.skip is None and not p.stage]
    by_section: dict[str, int] = {}
    for p in not_rerun:
        by_section[cv.section(p)] = by_section.get(cv.section(p), 0) + 1
    invalid = [(r["param"].key, f, v["invalid"]) for r in rows for f, v in r["runs"].items() if "invalid" in v]
    any_change = sum(1 for r in rows if np.nan_to_num(max_eff(r)) > 0)
    lines = ["## 3. Sensitivität der Annahmen (±{:.0%})".format(delta), "",
             f"Alle Zahlenwerte mit source_type assumption in cycling_rules.yaml und design_rules.yaml ({len(params)} Werte; "
             "source_type gilt auch für Einträge darunter), je einzeln um "
             f"−{delta:.0%} und +{delta:.0%} (delta aus rules.yaml V-SENS-01). Neu gerechnet werden Führungsform (c05), "
             "Soll-Querschnitt (c06) und Knotentyp (c07) auf ihren gespeicherten Eingangswerten; Werte einer späteren Stufe "
             "rechnen nur ab dieser Stufe neu. Führung und Fahrstreifen als Anteil der Länge aller Straßenabschnitte, Knoten als "
             "Anteil der Knotenpunkte. Führung = Führungsform nach Prompt 19 (inklusive Fallback).", "",
             f"- Variiert: {len(sens['varied'])} Werte, {sens['n_runs']} Läufe; davon {any_change} mit einer Änderung.",
             f"- Nicht neu gerechnet (andere Stufen): {len(not_rerun)} Werte – siehe unten.",
             f"- Nicht variiert: {n_struct} Zähl- oder Kennwerte (Seeds, Seitenzahl, Linientypen, Fahrstreifen-Vorgaben), "
             f"{n_zero} Werte gleich 0.",
             f"- Ungültige Regelwerke nach Variation: {len(invalid)}.", "",
             f"### Wirkung je Annahme (alle mit Änderung, höchstens {TOP_PARAMS}; sortiert nach größter Wirkung)", "",
             "Spalten je Richtung: Führung, Fahrstreifen und „Querschnitt passt?“ (fit_class) als Anteil der Länge, Knoten als "
             "Anteil der Knotenpunkte. Sollbreiten wirken vor allem über „Querschnitt passt?“.", "",
             "| Annahme | Wert | ab Stufe | −: Führung | −: Fahrstr. | −: passt? | −: Knoten | +: Führung | +: Fahrstr. | +: passt? | +: Knoten |",
             "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in [r for r in ranked if np.nan_to_num(max_eff(r)) > 0][:TOP_PARAMS]:
        p = r["param"]
        cells = []
        for f in (1 - delta, 1 + delta):
            cells += [_pct(eff(r, f, "fac")[1], 2), _pct(eff(r, f, "lanes")[1], 2), _pct(eff(r, f, "fit")[1], 2),
                      _pct(eff(r, f, "junction")[0], 2)]
        lines.append(f"| `{p.key}` ({p.file}) | {_fmt(p.value, 2)} | {p.stage} | " + " | ".join(cells) + " |")
    unchanged = [r["param"].key for r in ranked if np.nan_to_num(max_eff(r)) == 0]
    lines += ["", f"Ohne Wirkung bei ±{delta:.0%} ({len(unchanged)}): " + (", ".join(f"`{k}`" for k in unchanged) or "–"), ""]
    if invalid:
        lines += ["Ungültig nach Variation:", "", *[f"- `{k}` × {f:.1f}: {msg}" for k, f, msg in invalid], ""]
    c = sens["counts"]
    n = sens["n_runs"]
    lines += ["### Robustheit je Abschnitt und Knoten", "",
              f"- Abschnitte, deren Führungsform sich in mindestens einem der {n} Läufe ändert: {_fmt(int((c['fac'] > 0).sum()))} "
              f"von {_fmt(len(c['fac']))} ({_pct(float((c['fac'] > 0).mean()))}).",
              f"- Abschnitte mit geänderter Fahrstreifenzahl in mindestens einem Lauf: {_fmt(int((c['lanes'] > 0).sum()))} "
              f"({_pct(float((c['lanes'] > 0).mean()))}).",
              f"- Knotenpunkte mit geändertem Soll-Typ in mindestens einem Lauf: {_fmt(int((c['junction'] > 0).sum()))} von "
              f"{_fmt(len(c['junction']))} ({_pct(float((c['junction'] > 0).mean()))}).",
              "- Die Steckbriefe der Webseite nennen je Abschnitt und Knoten die Zahl der Läufe mit Änderung und bis zu "
              f"{TRIGGERS_PER_ROW} auslösende Annahmen.", "",
              "### Nicht neu gerechnet", "",
              "Diese Annahmen wirken über Nachfragemodell, Netzentwurf, Prinzipien oder die Knotenbildung. Ein Lauf bräuchte "
              "eine neue Umlegung bzw. Geometrie (Stunden je Lauf); sie bleiben hier fest. Wirkung der Nachfrage-Annahmen auf "
              "die Kalibrierung: docs/open_questions.md (Prompt 15, Sensitivitätsläufe 2026-11-05); Gewichte der Prinzipien: "
              "reports/cycle_principles.md.", "",
              "| Abschnitt | Annahmen | warum nicht neu gerechnet |", "| --- | ---: | --- |",
              *[f"| `{s}` | {k} | {cv.NOT_RECOMPUTED_REASON.get(s, 'andere Stufe')} |" for s, k in sorted(by_section.items())], ""]
    metrics = {"sens_params_varied": len(sens["varied"]), "sens_runs": n, "sens_invalid": len(invalid),
               "sens_max_facility_km_share": float(np.nanmax([eff(r, f, "fac")[1] for r in rows for f in (1 - delta, 1 + delta)] or [0])),
               "sens_max_lanes_km_share": float(np.nanmax([eff(r, f, "lanes")[1] for r in rows for f in (1 - delta, 1 + delta)] or [0])),
               "sens_top_fit_param": max(rows, key=lambda r: max(np.nan_to_num(eff(r, f, "fit")[1]) for f in (1 - delta, 1 + delta)))["param"].key if rows else "–",
               "sens_max_fit_km_share": float(np.nanmax([eff(r, f, "fit")[1] for r in rows for f in (1 - delta, 1 + delta)] or [0])),
               "sens_max_junction_share": float(np.nanmax([eff(r, f, "junction")[0] for r in rows for f in (1 - delta, 1 + delta)] or [0]))}
    return lines, metrics


# --- 4. samples, open questions, limits ------------------------------------------------------------------------


def section_samples(fac: gpd.GeoDataFrame, xs: pd.DataFrame, viewers, labels_fac: dict, labels_fit: dict) -> list[str]:
    lines = ["## 4. Stichproben aus den Prompts 17–20", "",
             "| Stichprobe | Bericht | Umfang | Stand der Durchsicht |", "| --- | --- | --- | --- |"]
    for name, (report, size) in SAMPLE_REPORTS.items():
        status = "Durchsicht ausstehend (keine Ergebnisspalten)"
        csv = REVIEW_CSVS.get(name)
        if csv is not None and csv.exists():
            d = pd.read_csv(csv)
            done = int(d["assessment"].notna().sum())
            status = f"{done} von {len(d)} bewertet" + ("" if done else " – Durchsicht ausstehend")
        lines.append(f"| {name} | {report} | {size} | {status} |")
    name = "Prompt 17 – Routen (Prinzipien)"
    d = pd.read_csv(REVIEW_CSVS[name]) if REVIEW_CSVS[name].exists() else pd.DataFrame(columns=["assessment"])
    lines.append(f"| {name} | reports/cycle_principles_review.csv | {len(d)} Routen | "
                 f"{int(d['assessment'].notna().sum())} von {len(d)} bewertet |")
    lines += ["", "Ohne ausgefüllte Prüflisten lässt sich die Trefferquote der Regeln nicht angeben. Die Durchsicht durch "
              "Ortskundige ist der wichtigste nächste Schritt (docs/open_questions.md).", "",
              f"### {SAMPLE_SIZE} neue Zufallsstichproben (Abschnitte im Soll-Radnetz, über Bezirke verteilt, Seed {SAMPLE_SEED})", "",
              "Zum Prüfen gegen Luftbild und Panoramax; dieselben Abschnitte mit Spalten für die Bewertung in "
              "reports/validation_cycling_review.csv.", "",
              "| segment_id | Bezirk | Name | Rad | Soll-Führung | Ist-Führung | Fahrstreifen Soll/Ist | Querschnitt | Prüfen |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    pool = fac[fac["cycle_cat_final"].isin(("RSV", "HAUPT", "BASIS", "ERSCHL"))]
    sample = sample_by_district(pool, SAMPLE_SIZE, SAMPLE_SEED)
    x = xs.set_index("segment_id")
    review = []
    for r in sample.itertuples(index=False):
        xr = x.loc[r.segment_id]
        ist_lanes = "–" if pd.isna(xr["lanes_per_dir_ist"]) else str(int(xr["lanes_per_dir_ist"]))
        soll_f = labels_fac.get(xr["cycle_facility_final"], "–") if isinstance(xr["cycle_facility_final"], str) else "–"
        ist_f = labels_fac.get(r.cycle_facility_ist, "–")
        fit = labels_fit.get(xr["fit_class"], "nicht bewertet") if isinstance(xr["fit_class"], str) else "nicht bewertet"
        links = _links(r.geometry, viewers)
        soll_l = xr["lanes_per_dir_soll"] if isinstance(xr["lanes_per_dir_soll"], str) else "–"
        soll_l = "Misch" if soll_l == "shared" else soll_l
        bz = r.bezirk if isinstance(r.bezirk, str) else "–"
        lines.append(f"| `{r.segment_id}` | {bz} | {r.name if isinstance(r.name, str) else '–'} | {r.cycle_cat_final} | "
                     f"{soll_f} | {ist_f} | {soll_l}/{ist_lanes} | {fit} | {links} |")
        review.append({"segment_id": r.segment_id, "bezirk": r.bezirk, "name": r.name, "cycle_cat_final": r.cycle_cat_final,
                       "facility_soll": xr["cycle_facility_final"], "facility_ist": r.cycle_facility_ist,
                       "lanes_soll": xr["lanes_per_dir_soll"], "lanes_ist": xr["lanes_per_dir_ist"], "fit_class": xr["fit_class"],
                       "links": links, "reviewer": None, "assessment": None, "comment": None})
    pd.DataFrame(review).to_csv(REVIEW_PATH, index=False)
    return lines + [""]


def section_open_questions() -> list[str]:
    lines = ["## 5. Offene Fragen und Grenzen", "", "### Offene Fragen zum Radnetz (docs/open_questions.md)", ""]
    if not OPEN_QUESTIONS.exists():
        return lines + ["_Datei fehlt_", ""]
    for section, items in val.open_questions(OPEN_QUESTIONS.read_text(encoding="utf-8")):
        if section.startswith("Radnetz"):
            lines += [f"{len(items)} offene Punkte:", "", *[f"- {i}" for i in items], ""]
    return lines


LIMITS = [
    "Radverkehrsstärken sind modelliert und mit denselben Zählstellen kalibriert, mit denen hier verglichen wird; die "
    "Kalibrierungsgüte ist mäßig (Abschnitt 2). DB Rad+ ist eine nicht repräsentative Stichprobe.",
    "Die Sensitivität rechnet nur die Stufen c05–c07 neu. Annahmen des Nachfragemodells, des Netzentwurfs, der "
    "Prinzipien und der Knotenbildung bleiben fest (Abschnitt 3); ihre Wirkung auf Führung, Fahrstreifen und Knoten ist "
    "damit nicht erfasst. Die Variation ist einzeln (eine Annahme je Lauf), Wechselwirkungen fehlen.",
    "Kfz-Mengen gibt es nur für Hauptverkehrsstraßen (Stand 2019). Ohne Zählung gelten Bedingungen der Fahrradstraße und "
    "von S-04 vorläufig als erfüllt (Flag dtv_unknown); die Sensitivität der Kfz-Schwellen wirkt deshalb nur dort, wo "
    "gezählt wurde.",
    "Ist-Führung, Ist-Breite und Ist-Knotentyp stammen aus OpenStreetMap; Breiten sind dort selten erfasst.",
    "Straßenraumbreite aus Kataster (ALKIS), nicht vor Ort gemessen; Knotentypen setzen Platz und Leistungsfähigkeit "
    "voraus, die nur grob geschätzt sind.",
    "Der Vergleich mit dem amtlichen Radnetz misst Lagegleichheit im Puffer, nicht die Qualität der Führung.",
    "Ohne ausgefüllte Prüflisten gibt es keine Trefferquote der Regeln (Abschnitt 4).",
    "Der Entwurf ersetzt keine Planung; er macht Netzlogik und Raumansprüche sichtbar (docs/guide_radnetz.md, Abschnitt 7).",
]

REVIEW_HINTS = [
    "Passen die Kategorien des Soll-Netzes zu den stärksten Zählstellen und zum amtlichen Radnetz (Abschnitte 1–2)?",
    "Sind die Annahmen mit großer Wirkung (Abschnitt 3) fachlich begründbar, oder brauchen sie eine Quelle?",
    "Stimmen die Zufallsstichproben (Abschnitt 4) mit Luftbild und Ortskenntnis überein?",
    "Fehlen Grenzen oder Prüfungen, die vor einer Veröffentlichung nötig sind?",
]


def write_report(parts: list[list[str]], checks: list[dict], ctx: dict) -> None:
    lines = ["# Validierung Radnetz, Radanlagen, Querschnitte und Knoten (Prompt 21)", "",
             f"Erzeugt {_now()} mit pipeline/c08_validate_cycling.py · cycling_rules.yaml {ctx['cyc_version']} · "
             f"design_rules.yaml {ctx['des_version']} · rules.yaml {ctx['rules_version']} · nicht amtlicher Entwurf.", "",
             "## Kurzfassung", "", *[f"- {s}" for s in ctx["summary"]], "",
             "## Prüfungen", "", "| Prüfung | Ergebnis | Detail |", "| --- | --- | --- |",
             *[f"| {c['name']} | {'ok' if c['ok'] else 'FEHLER'} | {c['detail']} |" for c in checks], ""]
    for p in parts:
        lines += p
    lines += ["### Grenzen", "", *[f"- {s}" for s in LIMITS], "",
              "## Hinweise für den externen Fachreview", "", *[f"- {s}" for s in REVIEW_HINTS], "",
              "Rückmeldungen bitte als Eintrag in docs/open_questions.md oder als GitHub-Issue.", "",
              "## Lizenz", "", "Radnetz Hamburg: © Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende "
              "(dl-de/by-2.0). Zählstellen: laut Quelle (config/sources.yaml). OSM-Ableitungen: ODbL 1.0.", ""]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --- main ------------------------------------------------------------------------------------------------------


def main() -> int:
    need = ((FINAL_PATH, "make coherence"), (NETWORK_PATH, "make cycle-network"), (FACILITY_PATH, "make cycle-facility"),
            (XS_PATH, "make cross-section-soll"), (JUNCTIONS_PATH, "make junctions"), (OFFICIAL_PATH, "make fetch"))
    for path, step in need:
        if not path.exists():
            print(f"validate-cycling: {path.relative_to(REPO_ROOT)} missing; run `{step}` first", file=sys.stderr)
            return 1
    t0 = time.perf_counter()

    def tick(msg: str) -> None:
        print(f"validate-cycling: {msg} ({time.perf_counter() - t0:.0f} s)")

    raw_c = yaml.safe_load(DEFAULT_CYCLING_RULES_PATH.read_text(encoding="utf-8"))
    raw_d = yaml.safe_load(DEFAULT_DESIGN_RULES_PATH.read_text(encoding="utf-8"))
    cyc, des, rules = CyclingRuleSet.model_validate(raw_c), DesignRuleSet.model_validate(raw_d), load_rules()
    delta = float(rules.validation.rule("V-SENS-01").thresholds["delta"].value)
    texts = yaml.safe_load((REPO_ROOT / "config" / "plain_language.yaml").read_text(encoding="utf-8"))["cycling"]
    viewers = load_viewers()
    districts = read_districts()

    fac = gpd.read_parquet(FACILITY_PATH, columns=FAC_COLS)
    xs = pd.read_parquet(XS_PATH)
    final = pd.read_parquet(FINAL_PATH, columns=FINAL_COLS).set_index("segment_id")
    j = gpd.read_parquet(JUNCTIONS_PATH)
    net = gpd.read_parquet(NETWORK_PATH, columns=["edge_id", "kind", "in_main_component", "cycle_cat_final", "cyc_calibrated",
                                                  "bezirk", "geometry"])
    tick("inputs loaded")

    off_lines, off_m = section_official(net, districts, NetworkParams.from_rules(cyc))
    tick("official network compared")
    cnt_lines, cnt_m = section_counters(net, districts, cyc, viewers)
    tick("counters compared")

    chain = Chain(fac.set_index("segment_id")[["cat_final", "dtv_official", "cycle_cat_final", "cyc_peak_h_dir", "cyc_peak_h"]],
                  final, xs.set_index("segment_id"), j, rules)
    length = fac.set_index("segment_id")["length_m"]
    sens = run_sensitivity(chain, raw_c, raw_d, cyc, des, delta, length, tick)
    base = sens["base"]
    xs_i = xs.set_index("segment_id").reindex(chain.fac.index)
    repro = {
        "Führungsform (c05)": float((base["fac"]["cycle_facility_soll"].fillna("-") ==
                                     fac.set_index("segment_id")["cycle_facility_soll"].fillna("-")).mean()),
        "Führungsform nach Querschnitt (c06)": float((base["profile"]["facility"].fillna("-") == xs_i["cycle_facility_final"].fillna("-")).mean()),
        "Fahrstreifen (c06)": float((base["profile"]["lanes"].fillna("-") == xs_i["lanes_per_dir_soll"].fillna("-")).mean()),
        "fit_class (c06)": float((base["profile"]["fit"].fillna("-") == xs_i["fit_class"].fillna("-")).mean()),
        "Knotentyp (c07)": float((base["junction"].fillna("-").to_numpy() == j["junction_type_soll"].fillna("-").to_numpy()).mean()),
    }
    sens_lines, sens_m = section_sensitivity(sens, delta)
    tick("sensitivity written")

    c, tr = sens["counts"], sens["triggers"]
    seg_out = pd.DataFrame({"kind": "segment", "id": chain.fac.index, "n_runs": sens["n_runs"], "facility_changes": c["fac"],
                            "lanes_changes": c["lanes"], "type_changes": 0,
                            "triggers": [json.dumps({"facility": a, "lanes": b}, ensure_ascii=False) for a, b in zip(tr["fac"], tr["lanes"])]})
    jct_out = pd.DataFrame({"kind": "junction", "id": chain.node_ids, "n_runs": sens["n_runs"], "facility_changes": 0,
                            "lanes_changes": 0, "type_changes": c["junction"],
                            "triggers": [json.dumps({"type": a}, ensure_ascii=False) for a in tr["junction"]]})
    out = pd.concat([seg_out, jct_out], ignore_index=True)
    out["cycling_rules_version"], out["design_rules_version"], out["delta"] = cyc.meta.version, des.meta.version, delta
    out.to_parquet(OUT_PATH, index=False)

    smp_lines = section_samples(fac, xs, viewers, texts["facility"], texts["fit"])
    oq_lines = section_open_questions()
    checks = [{"name": f"Basislauf reproduziert {k}", "ok": v == 1.0, "detail": f"{_pct(v)} gleich (sonst Zwischenergebnisse veraltet)"}
              for k, v in repro.items()]
    checks.append({"name": "Regelwerke nach Variation gültig", "ok": sens_m["sens_invalid"] == 0, "detail": f"{sens_m['sens_invalid']} ungültig"})
    checks.append({"name": "Zählstellen-Querschnitte vorhanden", "ok": cnt_m["counter_n"] > 0, "detail": f"{cnt_m['counter_n']} Querschnitte"})
    summary = [
        f"Amtlicher Bestand {_fmt(off_m['official_km'], 0)} km: {_pct(off_m['official_on_soll_hr_share'])} am Soll RSV/HAUPT, "
        f"{_pct(off_m['official_on_soll_any_share'])} bis BASIS; Soll RSV/HAUPT {_fmt(off_m['soll_hr_km'], 0)} km.",
        f"Zählstellen: Spearman {_fmt(cnt_m['counter_spearman'], 2)} an {cnt_m['counter_n']} Querschnitten; "
        f"{_pct(cnt_m['top_counters_on_hr'])} der {TOP_COUNTERS} stärksten liegen am Soll RSV/HAUPT.",
        f"Sensitivität ±{delta:.0%}: {sens_m['sens_params_varied']} Annahmen, {sens_m['sens_runs']} Läufe; größte Wirkung "
        f"{_pct(sens_m['sens_max_facility_km_share'])} der Länge mit anderer Führung, {_pct(sens_m['sens_max_lanes_km_share'])} mit "
        f"anderer Fahrstreifenzahl, {_pct(sens_m['sens_max_junction_share'])} der Knoten mit anderem Typ; „Querschnitt passt?“ "
        f"reagiert stärker (bis {_pct(sens_m['sens_max_fit_km_share'])} der Länge, am stärksten `{sens_m['sens_top_fit_param']}`).",
        "Prüflisten der Prompts 17–20 sind noch nicht ausgefüllt; eine Trefferquote der Regeln fehlt.",
    ]
    write_report([off_lines, cnt_lines, sens_lines, smp_lines, oq_lines], checks,
                 {"cyc_version": cyc.meta.version, "des_version": des.meta.version, "rules_version": rules.meta.version,
                  "summary": summary})
    for ch in checks:
        print(f"validate-cycling: {ch['name']}: {ch['ok']} ({ch['detail']})")
    tick(f"wrote {REPORT_PATH.relative_to(REPO_ROOT)}, {REVIEW_PATH.relative_to(REPO_ROOT)}, {OUT_PATH.relative_to(REPO_ROOT)}")
    if not all(ch["ok"] for ch in checks):
        print(f"validate-cycling: check(s) failed; see {REPORT_PATH}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
