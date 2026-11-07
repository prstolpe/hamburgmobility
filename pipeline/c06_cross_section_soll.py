"""Cycle stage 6: Soll cross section per street segment (prompts/19_cross_section_soll.md).

Usage: uv run python -m pipeline.c06_cross_section_soll

Car lanes (L-01..L-06), bus lane from GTFS (L-04, PRF-02), cycle facility placement (PL-01..PL-07) and space
allocation with the degrade cascade D1..D7 (cross_section_allocation, PRF-03..PRF-06) in design_rules.yaml.
Facility and cycle width come from prompt 18 (data/interim/cycle_facility.parquet); its pending matrix-cell
fallback is decided here. Writes data/interim/cross_section_soll.parquet (one row per segment_id of final.parquet),
reports/cross_section_soll.md and reports/profiles_sample/*.svg.
"""

import datetime as dt
import hashlib
import json
import sys
import time

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from config.schema.cycling_model import NO_CYCLE_CATEGORY, CyclingRuleSet
from config.schema.design_model import DesignRuleSet
from pipeline.c04_principles import _gtfs_path, _links
from pipeline.lib import gtfs, parallel
from pipeline.lib import profile as pf
from pipeline.lib.area import sample_by_district
from pipeline.lib.conflate import MatchParams, zone_share
from pipeline.lib.links import load_viewers
from pipeline.lib.manifest import REPO_ROOT, load_manifest
from pipeline.lib.report import district_breakdown
from pipeline.lib.rules import load_cycling_rules, load_design_rules, load_rules

INTERIM = REPO_ROOT / "data" / "interim"
FINAL_PATH = INTERIM / "final.parquet"
FACILITY_PATH = INTERIM / "cycle_facility.parquet"
OUT_PATH = INTERIM / "cross_section_soll.parquet"
CACHE_DIR = INTERIM / "cache"
REPORT_PATH = REPO_ROOT / "reports" / "cross_section_soll.md"
SVG_DIR = REPO_ROOT / "reports" / "profiles_sample"
SAMPLE_SIZE = 30
EXTREME_N = 20
SAMPLE_SEED = 42
CASE_LIST_N = 40
CAT_ORDER = ["SW", "GOW80", "GOW50", "GOW30", "ETW60", "ETW30", "ETW_ERF"]
FIT_DE = {"fits": "passt", "fits_after_degrade": "passt nach Abbau", "does_not_fit": "passt nicht", None: "nicht bewertet"}
STEP_DE = {"D1": "Parken entfernen", "D2": "Baumstreifen → Baumscheiben", "fallback": "Fallback der Matrixzelle (Prompt 18)",
           "D3": "zweiten Kfz-Fahrstreifen streichen", "D4": "Rad- und Gehweg auf Mindestbreite",
           "D5": "Vorschlag GOW50 → GOW30 (C-G30-02)", "D6": "Flag: Einrichtungsverkehr / Durchfahrtsunterbrechung prüfen",
           "D7": "Flag: Radroute auf Parallelstraße verlegen"}
FACILITY_DE = {"separated_oneway_both": "Radweg je Seite", "separated_twoway": "Zweirichtungsradweg",
               "cycle_lane": "Radfahrstreifen", "cycle_street": "Fahrradstraße", "mixed": "Mischverkehr",
               "own_path": "eigene Trasse", None: "–"}
FLAG_DE = {"width_unknown": "keine verfügbare Breite (width_p10_m fehlt)",
           "no_profile_rules": "keine Profilregeln (SW, GOW80, ETW60 oder ohne Kategorie, PRF-04)",
           "dtv_unknown": "DTV fehlt an GOW50 – Fahrstreifen = Ist (PRF-01), confidence low",
           "lanes_capped_l06": "Soll-Fahrstreifen auf Ist begrenzt (L-06, kein Override)",
           "pl02_unchecked": "Zweirichtungsradweg: Seitenbedingung PL-02 nicht prüfbar (PRF-07)",
           "trees_in_parking_row": "Baumstreifen entfällt, Bäume als Baumscheiben (D2)",
           "gow30_dtv_above_profile": "GOW30 mit DTV über dem breiten CROW-Profil",
           "D6": STEP_DE["D6"], "D7": STEP_DE["D7"]}


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _fmt(v, digits: int = 0) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "–"
    return f"{v:,.{digits}f}".replace(",", " ")


_PARAMS: dict = {}


def _params(design: DesignRuleSet, cycling: CyclingRuleSet) -> pf.ProfileParams:
    key = (id(design), id(cycling))
    hit = _PARAMS.get(key)
    if hit is None or hit[0] is not design or hit[1] is not cycling:
        hit = _PARAMS[key] = (design, cycling, pf.ProfileParams.from_rules(design, cycling, load_rules()))
    return hit[2]


def lanes_for_segment(props: dict, design: DesignRuleSet, cycling: CyclingRuleSet) -> dict:
    """Golden-case API (tests/golden/cycling/s*.geojson): lanes per direction and bus lane from the case properties."""
    r = pf.lanes_soll(props["cat_final"], props.get("dtv"), props.get("bus_peak_h_dir"), props.get("lanes_ist"),
                      _params(design, cycling))
    return {"lanes_per_direction": r.lanes, "bus_lane": r.bus_lane, "median": r.median, "flags": r.flags,
            "rule_trace": r.trace}


# --- GTFS: buses and trams per peak hour and direction (PRF-02) ------------------------------------------------


def match_shapes(seg_geoms: gpd.GeoSeries, shapes: list, mp: MatchParams, min_share: float) -> list[tuple]:
    """Per GTFS shape: (indices of the segments it runs on, direction +1/-1 per segment); shapes in parallel."""
    geoms = seg_geoms.reset_index(drop=True)
    tree = shapely.STRtree(geoms.values)
    empty = (np.array([], dtype=int), np.array([], dtype=int))

    def one(k: int) -> tuple:
        shape = shapes[k]
        idx = tree.query(shape.buffer(mp.buffer_m))
        if len(idx) == 0:
            return empty
        share = zone_share(geoms.iloc[idx], gpd.GeoSeries([shape], crs=seg_geoms.crs), mp).to_numpy()
        hit = idx[share >= min_share]
        if len(hit) == 0:
            return empty
        return hit, np.asarray(gtfs.shape_direction(geoms.iloc[hit], shape))

    return parallel.pmap(one, len(shapes), chunksize=64)


def transit_cache_key(feed_name: str, feed_size: int, route_types: tuple, mp: MatchParams, min_share: float,
                      seg_geoms: gpd.GeoSeries) -> str:
    """Fingerprint of everything the bus matching depends on (feed file, route types, S-CONF parameters, geometry)."""
    h = hashlib.sha256()
    h.update(json.dumps([feed_name, int(feed_size), sorted(route_types), mp.buffer_m, mp.max_angle_deg,
                         mp.min_overlap_share, min_share]).encode())
    for wkb in shapely.to_wkb(shapely.set_precision(seg_geoms.values, 0.001)):
        h.update(wkb)
    return h.hexdigest()[:20]


def transit_peak(seg: gpd.GeoDataFrame, feed_path, route_types: tuple, start_hours: pd.Series, feed: dict,
                 day, mp: MatchParams, min_share: float) -> np.ndarray:
    """Trips in the busiest hour of the busier direction per segment (0 without a matching shape).
    Cached in data/interim/cache by transit_cache_key; the cache is only a shortcut, the result is the same."""
    key = transit_cache_key(feed_path.name, feed_path.stat().st_size, route_types, mp, min_share, seg.geometry)
    cache = CACHE_DIR / f"transit_peak_{key}.npy"
    if cache.exists():
        return np.load(cache)
    hist = gtfs.hourly_trips_per_shape(feed, start_hours, day, route_types)
    n = len(seg)
    if hist.empty:
        return np.zeros(n)
    hours = sorted(hist.columns)
    fwd, bwd = np.zeros((n, len(hours))), np.zeros((n, len(hours)))
    shapes = gtfs.shapes_gdf(feed, hist.index)
    matched = match_shapes(seg.geometry, list(shapes.geometry.values), mp, min_share)
    for shape_id, (hit, d) in zip(shapes.index, matched):
        if len(hit) == 0:
            continue
        counts = hist.loc[shape_id, hours].to_numpy(dtype=float)
        fwd[hit[d > 0]] += counts
        bwd[hit[d < 0]] += counts
    out = np.maximum(fwd.max(axis=1), bwd.max(axis=1))
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.save(cache, out)
    return out


def bus_and_tram(seg: gpd.GeoDataFrame, p_design: DesignRuleSet, rules) -> tuple[np.ndarray, np.ndarray, dict]:
    feed_path = _gtfs_path(load_manifest())
    feed = gtfs.load_feed(feed_path)
    day = gtfs.representative_weekday(feed)
    hours = gtfs.trip_start_hours(feed_path)
    mp = MatchParams.from_rules(rules)
    min_share = rules.conflation.rule("S-CONF-02").thresholds["min_length_share"].value
    bus_types = tuple(rules.features.rule("S-FEAT-08").route_types)
    prf02 = next(r for r in p_design.profile_assignment["rules"] if r["id"] == "PRF-02")
    tram_types = tuple(prf02["tram_route_types"])
    bus = transit_peak(seg, feed_path, bus_types, hours, feed, day, mp, min_share)
    routes = feed["routes"]
    n_tram_routes = int(routes["route_type"].astype(int).isin(tram_types).sum())
    tram = transit_peak(seg, feed_path, tram_types, hours, feed, day, mp, min_share) if n_tram_routes else np.zeros(len(seg))
    return bus, tram > 0, {"day": day.isoformat(), "file": feed_path.name, "tram_routes": n_tram_routes}


# --- per segment --------------------------------------------------------------------------------------------


def _str_or_none(v):
    return v if isinstance(v, str) else None


def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if np.isnan(f) else f


def segment_input(f, c, bus, tram, p: pf.ProfileParams) -> pf.SegmentInput:
    ist, oneway = pf.lanes_ist(f["lanes_official_in"], f["lanes_official_gegen"], f["bahnigkeit_official"], f["lanes"])
    return pf.SegmentInput(
        cat=_str_or_none(f["cat_final"]), cycle_cat=c["cycle_cat_final"] if isinstance(c["cycle_cat_final"], str) else NO_CYCLE_CATEGORY,
        facility=_str_or_none(c["cycle_facility_soll"]), fallback=_str_or_none(c["cycle_facility_fallback"]),
        cycle_width=_num(c["cycle_width_soll_m"]), peak_dir=_num(c["cyc_peak_h_dir"]), peak_both=_num(c["cyc_peak_h"]),
        dtv=_num(f["dtv_official"]), bus_peak_dir=float(bus), lanes_ist=ist, oneway=oneway,
        parking_sides=pf.parking_sides(f["parking"], p), business=pf.is_business(f["shop_frontage_share"], p),
        tram=bool(tram))


def _lanes_str(v):
    return None if v is None else str(v)


def classify(final: pd.DataFrame, fac: pd.DataFrame, bus: np.ndarray, tram: np.ndarray, p: pf.ProfileParams) -> pd.DataFrame:
    rows = []
    for (seg_id, f), b, t in zip(final.iterrows(), bus, tram):
        c = fac.loc[seg_id]
        seg = segment_input(f, c, b, t, p)
        res = pf.evaluate_profile(seg, f["width_p10_m"], p)
        facade = pf.evaluate_profile(seg, f["facade_width_p10_m"], p)
        trace = [*res.trace, {"id": "PRF-05", "variant": "facade", "result": facade.fit_class,
                              "values": {"available_m": facade.available_m, "steps": facade.degrade_steps_applied}}]
        rows.append({
            "segment_id": seg_id, "lanes_per_dir_soll": _lanes_str(res.lanes), "lanes_per_dir_ist": seg.lanes_ist,
            "oneway": seg.oneway, "bus_peak_h_dir": float(b), "tram_present": bool(t), "bus_lane_soll": res.bus_lane,
            "median_soll": res.median, "cycle_facility_final": res.cycle_facility, "cycle_width_final_m": res.cycle_width_m,
            "cycle_side": res.cycle_side, "parking_sides_ist": seg.parking_sides, "business_use": seg.business,
            "profile_elements": json.dumps(res.elements, ensure_ascii=False), "total_required_m": res.total_required_m,
            "available_m": res.available_m, "available_facade_m": facade.available_m, "fit_class": res.fit_class,
            "fit_class_facade": facade.fit_class, "degrade_steps_applied": "|".join(res.degrade_steps_applied) or None,
            "cat_change_proposal": res.cat_change_proposal, "profile_flags": "|".join(dict.fromkeys(res.flags)) or None,
            "profile_confidence": pf.confidence(res, seg),
            "rule_trace_profile": json.dumps(trace, ensure_ascii=False, default=float)})
    return pd.DataFrame(rows).set_index("segment_id")


# --- SVGs ---------------------------------------------------------------------------------------------------


def svg_selection(out: pd.DataFrame) -> pd.DataFrame:
    """30 random profiles (spread over Bezirke) plus the 20 widest and 20 narrowest available widths."""
    rated = out[out["fit_class"].notna()]
    rnd = sample_by_district(rated.reset_index(drop=True), SAMPLE_SIZE, SAMPLE_SEED).assign(svg_group="Zufall")
    by_w = rated.sort_values(["available_m", "segment_id"])
    narrow = by_w.head(EXTREME_N).assign(svg_group="am engsten")
    wide = by_w.tail(EXTREME_N).iloc[::-1].assign(svg_group="am breitesten")
    sel = pd.concat([rnd, wide, narrow], ignore_index=True)
    return sel.drop_duplicates("segment_id")


def write_svgs(sel: pd.DataFrame) -> None:
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    for old in SVG_DIR.glob("*.svg"):
        old.unlink()
    for r in sel.itertuples():
        title = f"{r.name if isinstance(r.name, str) else '(ohne Namen)'} – {r.bezirk}"
        steps = f" · Abbau {r.degrade_steps_applied}" if isinstance(r.degrade_steps_applied, str) else ""
        sub = (f"{r.segment_id} · {r.cat_final} · Rad {r.cycle_cat_final} · {FACILITY_DE.get(r.cycle_facility_final, '–')} · "
               f"{FIT_DE[r.fit_class]}{steps}")
        svg = pf.profile_svg(json.loads(r.profile_elements), r.available_m, title, sub)
        (SVG_DIR / f"{r.segment_id}.svg").write_text(svg, encoding="utf-8")


# --- report -------------------------------------------------------------------------------------------------


def _km(out, mask) -> float:
    return out.loc[mask, "length_m"].sum() / 1000


def _steps(out: pd.DataFrame) -> pd.Series:
    return out["degrade_steps_applied"].fillna("").str.split("|")


def _case_list(out: pd.DataFrame, step: str) -> list[str]:
    m = _steps(out).apply(lambda xs: step in xs)
    g = out[m].copy()
    g["name"] = g["name"].fillna("(ohne Namen)")
    agg = (g.groupby(["name", "bezirk", "cat_final", "cycle_cat_final"], dropna=False)
           .agg(km=("length_m", lambda s: s.sum() / 1000), n=("length_m", "size"), avail=("available_m", "median"),
                need=("total_required_m", "median"), seg=("segment_id", "first"))
           .sort_values("km", ascending=False).head(CASE_LIST_N))
    lines = [f"{_fmt(m.sum())} Abschnitte, {_fmt(_km(out, m), 1)} km. Längste {CASE_LIST_N}, je Straße und Bezirk zusammengefasst:", "",
             "| Straße | Bezirk | Kfz | Rad | Abschnitte | km | verfügbar m (Median) | Bedarf m (Median) | Beispiel |",
             "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |"]
    for (name, bez, cat, cc), r in agg.iterrows():
        lines.append(f"| {name} | {bez} | {cat} | {cc} | {r.n} | {_fmt(r.km, 2)} | {_fmt(r.avail, 1)} | {_fmt(r.need, 1)} | `{r.seg}` |")
    return lines


def write_report(out: gpd.GeoDataFrame, sel: pd.DataFrame, ctx: dict) -> None:
    viewers = load_viewers()
    rated = out["fit_class"].notna()
    has_cat = out["cat_final"].notna()
    lines = [
        "# Soll-Querschnitt: Fahrstreifen, Lage der Radanlagen, Raumaufteilung (Stufe c06)",
        "",
        f"Erzeugt {_now()} mit pipeline/c06_cross_section_soll.py · design_rules.yaml {ctx['design_version']} · "
        f"cycling_rules.yaml {ctx['cycling_version']} · nicht amtlicher Entwurf. Regeln L-01…06, PL-01…06 und "
        "PRF-01…07 sind Annahmen bzw. Entwürfe (status draft) und vor Gebrauch fachlich zu prüfen.",
        "",
        "Verfügbare Breite = width_p10_m der Variante Verkehrsfläche (maßgeblich); die Variante Fassade zeigt das Potenzial "
        "inklusive Vorgärten. Das gewünschte Profil enthält Gehwege (Regelmaß), die Radanlage mit Sollbreite aus Prompt 18, "
        "ÖPNV, Fahrbahn, Trennstreifen, Bäume (GOW), Ladezone bei Geschäftsnutzung und Parken nur dort, wo OSM heute Parken "
        "zeigt (Entscheidung 2026-11-06). Passt es nicht, gilt die Kaskade D1, D2, Fallback, D3, D4, D5, D6, D7 (PRF-06).",
        "",
        "## Kurzfassung",
        "",
        f"- {_fmt(len(out))} Abschnitte, {_fmt(_km(out, slice(None)), 0)} km; bewertet (Profilregeln und Breite vorhanden): "
        f"{_fmt(_km(out, rated), 0)} km. Ohne Breite: {_fmt(_km(out, out['profile_flags'].fillna('').str.contains('width_unknown')), 0)} km; "
        f"ohne Profilregeln: {_fmt(_km(out, out['profile_flags'].fillna('').str.contains('no_profile_rules')), 0)} km.",
    ]
    for f in ("fits", "fits_after_degrade", "does_not_fit"):
        m = out["fit_class"] == f
        lines.append(f"- {FIT_DE[f]}: {_fmt(_km(out, m), 0)} km ({_fmt(100 * _km(out, m) / max(_km(out, rated), 1e-9), 0)} % der bewerteten Länge).")
    d5 = out["cat_change_proposal"].notna()
    lines += [f"- Vorschlag GOW50 → GOW30 (D5): {_fmt(d5.sum())} Abschnitte, {_fmt(_km(out, d5), 1)} km – nicht übernommen, "
              "Entscheidung über overrides/overrides.csv.",
              f"- GTFS: repräsentativer Werktag {ctx['gtfs']['day']} ({ctx['gtfs']['file']}); Straßenbahnrouten im Feed: "
              f"{ctx['gtfs']['tram_routes']}. Busfahrstreifen Soll: {_fmt(_km(out, out['bus_lane_soll']), 1)} km.",
              "", "## km je fit_class und Straßenkategorie", "",
              "| Kategorie | " + " | ".join(FIT_DE[f] for f in (*pf.FIT_CLASSES, None)) + " | gesamt |",
              "| --- | " + " | ".join("---:" for _ in range(len(pf.FIT_CLASSES) + 1)) + " | ---: |"]
    for cat in CAT_ORDER:
        mc = out["cat_final"] == cat
        if not mc.any():
            continue
        vals = [_km(out, mc & (out["fit_class"] == f)) for f in pf.FIT_CLASSES] + [_km(out, mc & out["fit_class"].isna())]
        lines.append(f"| {cat} | " + " | ".join(_fmt(v, 1) for v in vals) + f" | {_fmt(sum(vals), 1)} |")

    lines += ["", "### Verkehrsfläche gegen Fassade (km, nur mit beiden Breiten)", "",
              "| Verkehrsfläche \\ Fassade | " + " | ".join(FIT_DE[f] for f in pf.FIT_CLASSES) + " |",
              "| --- | " + " | ".join("---:" for _ in pf.FIT_CLASSES) + " |"]
    both = out["fit_class"].notna() & out["fit_class_facade"].notna()
    for a in pf.FIT_CLASSES:
        lines.append(f"| {FIT_DE[a]} | " + " | ".join(
            _fmt(_km(out, both & (out['fit_class'] == a) & (out['fit_class_facade'] == b)), 1) for b in pf.FIT_CLASSES) + " |")

    steps = _steps(out)
    lines += ["", "## Abbaustufen", "",
              "Häufigkeit je Stufe (ein Abschnitt kann mehrere Stufen haben). Eine Stufe zählt nur, wenn sie das Profil verändert.", "",
              "| Stufe | Maßnahme | Abschnitte | km | Anteil an bewerteter Länge |", "| --- | --- | ---: | ---: | ---: |"]
    for s in ctx["cascade_order"]:
        m = steps.apply(lambda xs, s=s: s in xs)
        lines.append(f"| {s} | {STEP_DE[s]} | {_fmt(m.sum())} | {_fmt(_km(out, m), 1)} | {_fmt(100 * _km(out, m) / max(_km(out, rated), 1e-9), 1)} % |")
    last = steps.apply(lambda xs: next((s for s in reversed(xs) if s and s not in ("D6", "D7")), None))
    lines += ["", "Letzte wirksame Stufe bei „passt nach Abbau“ (km):", ""]
    fad = out["fit_class"] == "fits_after_degrade"
    lines.append(" · ".join(f"{s} {_fmt(_km(out, fad & (last == s)), 1)}" for s in ctx["cascade_order"] if s not in ("D6", "D7")))

    lines += ["", "## Fahrstreifen Ist → Soll (km)", "",
              "Ist je Richtung aus amtlichen Fahrstreifen (sonst OSM lanes, PRF-01). Soll nach L-01…L-06; L-06 verhindert "
              "jeden Zuwachs ohne Override (eine Override-Ebene für Fahrstreifen gibt es noch nicht).", ""]
    lanes = out[has_cat].copy()
    lanes["ist"] = lanes["lanes_per_dir_ist"].map(lambda v: "unbekannt" if pd.isna(v) else str(int(v)))
    lanes["soll"] = lanes["lanes_per_dir_soll"].fillna("–") + np.where(lanes["bus_lane_soll"], " + Bus", "")
    tab = lanes.groupby(["ist", "soll"])["length_m"].sum().unstack(fill_value=0) / 1000
    cols = sorted(tab.columns)
    lines += ["| Ist \\ Soll | " + " | ".join(cols) + " |", "| --- | " + " | ".join("---:" for _ in cols) + " |"]
    for i in sorted(tab.index):
        lines.append(f"| {i} | " + " | ".join(_fmt(tab.loc[i, c], 1) for c in cols) + " |")
    num_soll = pd.to_numeric(lanes["lanes_per_dir_soll"], errors="coerce")
    fewer = num_soll < lanes["lanes_per_dir_ist"]
    lines += ["", f"Weniger Kfz-Fahrstreifen je Richtung im Soll: {_fmt(_km(lanes, fewer), 1)} km "
              f"(davon an GOW50 {_fmt(_km(lanes, fewer & (lanes['cat_final'] == 'GOW50')), 1)} km). Zusätzlich D3 im Profil: "
              f"{_fmt(_km(out, steps.apply(lambda xs: 'D3' in xs)), 1)} km.", ""]

    for s in ("D5", "D6", "D7"):
        lines += [f"## Fälle {s}: {STEP_DE[s]}", ""] + _case_list(out, s) + [""]

    lines += ["## Hinweise (Flags)", "", "| Flag | Bedeutung | Abschnitte | km |", "| --- | --- | ---: | ---: |"]
    flags = out["profile_flags"].fillna("").str.split("|")
    for flag, text in FLAG_DE.items():
        m = flags.apply(lambda xs, f=flag: f in xs)
        lines.append(f"| `{flag}` | {text} | {_fmt(m.sum())} | {_fmt(_km(out, m), 1)} |")
    lines += ["", "confidence: " + ", ".join(f"{k} {_fmt(_km(out, out['profile_confidence'] == k), 0)} km" for k in ("high", "medium", "low")), ""]

    lines += ["## fit_class je Bezirk (Anteil km)", ""]
    bz = out.copy()
    bz["fit_de"] = bz["fit_class"].map(lambda v: FIT_DE.get(v if isinstance(v, str) else None))
    lines += district_breakdown(bz[has_cat], "fit_de", [FIT_DE[f] for f in (*pf.FIT_CLASSES, None)])

    lines += ["", f"## Querschnitts-Skizzen ({len(sel)} Profile)", "",
              f"reports/profiles_sample/<segment_id>.svg: {SAMPLE_SIZE} Zufallsabschnitte (über Bezirke verteilt, Seed {SAMPLE_SEED}), "
              f"die {EXTREME_N} breitesten und die {EXTREME_N} engsten (verfügbare Breite). Elemente maßstäblich, "
              "blau gestrichelt die verfügbare Breite. Prüfung gegen Luftbild und Straßenbilder: Spalte „geprüft“ von Hand ausfüllen.", "",
              "| Gruppe | segment_id | Straße | Bezirk | Kfz | Rad | Führung | Bedarf m | verfügbar m | Passung | Abbau | Skizze | Prüfen | geprüft |",
              "| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |"]
    for r in sel.itertuples():
        lines.append(f"| {r.svg_group} | `{r.segment_id}` | {r.name if isinstance(r.name, str) else '–'} | {r.bezirk} | {r.cat_final} | "
                     f"{r.cycle_cat_final} | {FACILITY_DE.get(r.cycle_facility_final, '–')} | {_fmt(r.total_required_m, 1)} | "
                     f"{_fmt(r.available_m, 1)} | {FIT_DE[r.fit_class]} | {r.degrade_steps_applied or '–'} | "
                     f"[SVG](profiles_sample/{r.segment_id}.svg) | {_links(r.geometry, viewers)} | ☐ |")
    lines += ["", "## Grenzen", "",
              "- Busse je Spitzenstunde aus der Abfahrtsstunde der ersten Haltestelle je Fahrt; auf langen Linien liegt die "
              "Stunde am Abschnitt später (PRF-02, docs/open_questions.md).",
              "- Verfügbare Breite nur auf rund 58 % der Abschnitte (ALKIS-Verkehrsfläche); ohne Breite keine Passung.",
              "- Ist-Parken nur, wo OSM parking erfasst ist; ohne Angabe kein Parken im Soll-Profil (PRF-03).",
              "- Bushaltestellen (PL-05), Abbiegestreifen (L-05) und die Seitenbedingung PL-02 sind nicht im Streckenprofil.",
              "- GOW30 mit Radfahrstreifen: Radfahrstreifen kommen zur CROW-Fahrbahnbreite hinzu (Annahme, offen).",
              "- Bei bahnigkeit 2 beschreibt das Profil den ganzen Straßenraum; beide Richtungsfahrbahnen bekommen dasselbe Profil.",
              "",
              "Quellen: OpenStreetMap-Mitwirkende (ODbL); Freie und Hansestadt Hamburg, ALKIS, Verkehrsmengen und Fahrstreifen "
              "(dl-de/by-2.0); HVV-Fahrplandaten GTFS (Transparenzportal Hamburg, dl-de/by-2.0).", ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    design, cyc, rules = load_design_rules(), load_cycling_rules(), load_rules()
    p = _params(design, cyc)
    for path, step in ((FACILITY_PATH, "make cycle-facility"), (FINAL_PATH, "make coherence")):
        if not path.exists():
            print(f"cross-section-soll: {path.relative_to(REPO_ROOT)} missing; run `{step}` first", file=sys.stderr)
            return 1
    t0 = time.perf_counter()

    def tick(msg: str) -> None:
        print(f"cross-section-soll: {msg} ({time.perf_counter() - t0:.0f} s)")

    final = gpd.read_parquet(FINAL_PATH, columns=[
        "segment_id", "name", "bezirk", "length_m", "cat_final", "dtv_official", "width_p10_m", "facade_width_p10_m",
        "lanes", "lanes_official_in", "lanes_official_gegen", "bahnigkeit_official", "parking", "shop_frontage_share",
        "geometry"]).set_index("segment_id")
    fac = pd.read_parquet(FACILITY_PATH, columns=[
        "segment_id", "cycle_cat_final", "cycle_facility_soll", "cycle_facility_fallback", "cycle_width_soll_m",
        "cyc_peak_h_dir", "cyc_peak_h"]).set_index("segment_id")
    bus, tram, gtfs_info = bus_and_tram(final, design, rules)
    tick(f"GTFS peak hour per direction ({int((bus > 0).sum())} segments with buses)")
    res = classify(final, fac, bus, tram, p)
    tick(f"{len(res)} profiles")
    out = final[["name", "bezirk", "length_m", "cat_final", "geometry"]].join(fac[["cycle_cat_final"]]).join(res)
    out = gpd.GeoDataFrame(out, geometry="geometry", crs=final.crs).reset_index()
    assert set(out["fit_class"].dropna()) <= set(pf.FIT_CLASSES)
    out.to_parquet(OUT_PATH)
    sel = svg_selection(out)
    write_svgs(sel)
    write_report(out, sel, {"design_version": design.meta.version, "cycling_version": cyc.meta.version,
                            "gtfs": gtfs_info, "cascade_order": p.cascade_order})
    tick(f"wrote {OUT_PATH.relative_to(REPO_ROOT)}, {len(sel)} SVGs and {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
