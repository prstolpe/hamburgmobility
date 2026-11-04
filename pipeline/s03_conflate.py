"""Stage 3: conflation of official data with the OSM segments (guide 3.2 Stufe 3, prompts/05).

Usage: uv run python -m pipeline.s03_conflate

Reads data/interim/segments.parquet and the official layers in data/raw (via data/manifest.json),
writes data/interim/segments_conflated.parquet, reports/conflation.md and
reports/conflation_sample.csv. Rules and thresholds: config/rules.yaml, section conflation
(S-CONF-01..04). Official data exists only for the work area (pilot district + buffer); segments
outside it keep match_quality = null. The run stops with exit code 1 if a check fails.
"""

import datetime as dt
import json
import math
import random
import sys

import geopandas as gpd
import pandas as pd
import yaml

from pipeline.lib.conflate import QUALITIES, MatchParams, match_lines, parse_speed_kmh, resolve_speed, zone_share
from pipeline.lib.crs import WORK_CRS, to_work_crs
from pipeline.lib.links import osm_map_link, osm_way_link
from pipeline.lib.manifest import REPO_ROOT, load_manifest, sha256_file
from pipeline.lib.rules import load_rules, network_highways

PROJECT_PATH = REPO_ROOT / "config" / "project.yaml"
SEGMENTS_PATH = REPO_ROOT / "data" / "interim" / "segments.parquet"
OUT_PATH = REPO_ROOT / "data" / "interim" / "segments_conflated.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "conflation.md"
SAMPLE_PATH = REPO_ROOT / "reports" / "conflation_sample.csv"
SAMPLE_SIZE = 50  # prompts/05_conflation.md (Prüfschritt)
SAMPLE_SEED = 42

# (manifest source, layer) of every official input.
LAYERS = {
    "speed": ("speed_limits", "zulaessige_hoechstgeschwindigkeiten"),
    "speed_conditional": ("speed_limits", "zulaessige_hoechstgeschwindigkeiten_sonderregelung"),
    "zone_t30": ("speed_limits", "tempo30zonen"),
    "zone_t20": ("speed_limits", "tempo20zonen"),
    "zone_vb": ("speed_limits", "verkehrsberuhigte_bereiche"),
    "hvs": ("traffic_volumes", "verkehrsmengen_dtv_hvs_2019"),
    "bab": ("traffic_volumes", "verkehrsmengen_dtv_bab_2019"),
    "dedication": ("dedications", "de.hh.up:widmung_linie"),
}
LINE_SOURCES = ["speed", "dedication", "hvs", "bab"]
ZONES = {"zone_t30": ("share_t30", "in_zone_t30"), "zone_t20": ("share_t20", "in_zone_t20"),
         "zone_vb": ("share_verkehrsberuhigt", "ist_verkehrsberuhigt")}
DIRECTIONS = ("in", "gegen")


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _none(v):
    return None if v is None or (isinstance(v, float) and math.isnan(v)) or v is pd.NA else v


def _round(v, digits: int = 2):
    v = _none(v)
    return None if v is None else round(float(v), digits)


def _int(v) -> int | None:
    v = _none(v)
    if v is None or str(v).strip() == "":
        return None
    try:
        return int(float(v))
    except ValueError:
        return None


# --- input -----------------------------------------------------------------------------------


def load_layers(manifest: dict) -> tuple[dict[str, gpd.GeoDataFrame], dict[str, dict]]:
    """Official layers by key plus their manifest records; raises if a file is missing or changed."""
    layers, records = {}, {}
    for key, (source, layer) in LAYERS.items():
        entry = manifest["sources"].get(source) or {}
        rec = next((f for f in entry.get("files", []) if f.get("layer") == layer), None)
        if rec is None or not (REPO_ROOT / rec["path"]).exists():
            raise FileNotFoundError(f"{source}/{layer} missing in data/manifest.json or on disk; run `make fetch`")
        path = REPO_ROOT / rec["path"]
        if rec.get("sha256") and sha256_file(path) != rec["sha256"]:
            raise ValueError(f"{rec['path']}: SHA-256 does not match data/manifest.json")
        gdf = to_work_crs(gpd.read_parquet(path))
        layers[key] = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].reset_index(drop=True)
        records[key] = {**rec, "source": source, "layer": layer, "retrieved_at": entry.get("retrieved_at"),
                        "license": entry.get("license"), "attribution": entry.get("attribution"),
                        "url": entry.get("url")}
    return layers, records


# --- attributes per source -------------------------------------------------------------------


def _speed_readings(row) -> dict:
    out = {}
    for d in DIRECTIONS:
        out[d] = resolve_speed(_none(row.get(f"geschwindigkeit_{d}")), _none(row.get(f"sonderregelung_{d}")))
    return out


def _regular_speed(readings: dict) -> int | None:
    values = [r.regular_kmh for r in readings.values() if r.regular_kmh is not None]
    return max(values) if values else None


def speed_attributes(match: pd.Series, off: gpd.GeoDataFrame) -> dict:
    if match["quality"] == "none":
        return {}
    row = off.loc[int(match["best_off_idx"])]
    readings = _speed_readings(row)
    texts = [_none(row.get(f"geschwindigkeit_{d}")) for d in DIRECTIONS]
    conditional = [{"direction": d, "speed_kmh": r.conditional_kmh, "rule": r.rule_text}
                   for d, r in readings.items() if r.rule_text]
    regular_all = {_regular_speed(_speed_readings(off.loc[i])) for i in match["passed_off_idx"]} - {None}
    return {
        "speed_official_kmh": _regular_speed(readings),
        "speed_official_in_kmh": readings["in"].regular_kmh,
        "speed_official_gegen_kmh": readings["gegen"].regular_kmh,
        "speed_official_text": " / ".join(dict.fromkeys(t for t in texts if t)) or None,
        "speed_official_ambiguous": any(r.ambiguous for r in readings.values()),
        "speed_official_conflict": len(regular_all) > 1,
        "speed_conditional": json.dumps(conditional, ensure_ascii=False) if conditional else None,
        "zone_bereich_official": _none(row.get("zone_bereich")) or None,
        "fahrradstrasse_official": _none(row.get("fahrradstrasse")) == "ja",
        "lanes_official_in": _int(row.get("fahrstreifenanzahl_in_stationierungsrichtung")),
        "lanes_official_gegen": _int(row.get("fahrstreifenanzahl_gegen_stationierungsrichtung")),
        "lanes_official_both": _int(row.get("fahrstreifenanzahl_in_beide_richtungen")),
        "bahnigkeit_official": _int(row.get("bahnigkeit")),
        "wegeart_official": _none(row.get("wegeart")),
        "strassenname_official": _none(row.get("strassenname")),
        "strassenschluessel_official": _none(row.get("strassenschluessel")),
    }


def dedication_attributes(match: pd.Series, off: gpd.GeoDataFrame) -> dict:
    if match["quality"] == "none":
        return {}
    row = off.loc[int(match["best_off_idx"])]
    return {"road_class_official": _none(row.get("klasse")), "widmung_official": _none(row.get("widmung")),
            "widmungsfall_official": _none(row.get("widmungsfall"))}


def volume_attributes(match: pd.Series, off: gpd.GeoDataFrame, source: str) -> dict:
    if match["quality"] != "exact":
        return {}
    row = off.loc[int(match["best_off_idx"])]
    return {"dtv_official": _int(row.get("dtv")), "sv_share_pct_official": _int(row.get("sv")),
            "dtv_source": LAYERS[source][1]}


def _trace_line(source: str, match: pd.Series) -> dict:
    return {"rule": "S-CONF-01", "source": LAYERS[source][1], "quality": match["quality"],
            "n_candidates": int(match["n_candidates"]), "n_passed": int(match["n_passed"]),
            "coverage": _round(match["coverage"], 3),
            "best": None if match["quality"] == "none" else {
                "official_idx": int(match["best_off_idx"]), "overlap_seg": _round(match["overlap_seg"], 3),
                "overlap_off": _round(match["overlap_off"], 3), "angle_deg": _round(match["angle_deg"], 1),
                "hausdorff_m": _round(match["hausdorff_m"], 1)}}


def conflate(seg: gpd.GeoDataFrame, in_area: pd.Series, layers: dict, rules) -> gpd.GeoDataFrame:
    params = MatchParams.from_rules(rules)
    min_zone = rules.conflation.rule("S-CONF-02").thresholds["min_length_share"].value
    work = seg.loc[in_area]
    geoms = work.geometry
    matches = {src: match_lines(geoms, layers[src].geometry, params) for src in LINE_SOURCES}
    shares = {z: zone_share(geoms, layers[z].geometry, params) for z in ZONES}

    records = []
    for idx in work.index:
        m = {src: matches[src].loc[idx] for src in LINE_SOURCES}
        rec = {"match_quality": m["speed"]["quality"],
               "match_quality_by_source": json.dumps({LAYERS[s][1]: m[s]["quality"] for s in LINE_SOURCES},
                                                     sort_keys=True)}
        rec |= speed_attributes(m["speed"], layers["speed"])
        rec |= dedication_attributes(m["dedication"], layers["dedication"])
        rec["hvs_match_quality"] = m["hvs"]["quality"]
        rec["in_hvs"] = m["hvs"]["quality"] == "exact"  # S-CONF-04
        rec |= volume_attributes(m["bab"], layers["bab"], "bab") or volume_attributes(m["hvs"], layers["hvs"], "hvs")
        trace = [_trace_line(s, m[s]) for s in LINE_SOURCES]
        for zone, (share_col, flag_col) in ZONES.items():
            share = float(shares[zone].loc[idx])
            rec[share_col] = round(share, 3)
            rec[flag_col] = share >= min_zone
            trace.append({"rule": "S-CONF-02", "source": LAYERS[zone][1], "share": round(share, 3),
                          "applies": rec[flag_col]})
        if rec.get("speed_conditional"):
            trace.append({"rule": "S-CONF-03", "conditional": json.loads(rec["speed_conditional"]),
                          "regular_kmh": rec.get("speed_official_kmh")})
        trace.append({"rule": "S-CONF-04", "in_hvs": rec["in_hvs"], "hvs_match_quality": rec["hvs_match_quality"]})
        rec["conflation_trace"] = json.dumps(trace, ensure_ascii=False)
        records.append(rec)

    attrs = pd.DataFrame(records, index=work.index)
    out = seg.copy()
    out["conflated"] = in_area.values
    for col in attrs.columns:
        out[col] = attrs[col].reindex(seg.index)
    # Nullable dtypes so that "outside the work area" stays null instead of False/NaN.
    for col in ("in_hvs", "in_zone_t30", "in_zone_t20", "ist_verkehrsberuhigt", "speed_official_ambiguous",
                "speed_official_conflict", "fahrradstrasse_official"):
        if col in out:
            out[col] = out[col].astype("boolean")
    for col in ("speed_official_kmh", "speed_official_in_kmh", "speed_official_gegen_kmh", "lanes_official_in",
                "lanes_official_gegen", "lanes_official_both", "bahnigkeit_official", "dtv_official",
                "sv_share_pct_official"):
        if col in out:
            out[col] = out[col].astype("Int64")
    return out


# --- checks ----------------------------------------------------------------------------------


def run_checks(seg_in: gpd.GeoDataFrame, out: gpd.GeoDataFrame, layers: dict) -> list[dict]:
    checks = []
    same_ids = list(out["segment_id"]) == list(seg_in["segment_id"]) and out["segment_id"].is_unique
    checks.append({"name": "segment_id unverändert und eindeutig", "ok": same_ids,
                   "detail": f"{len(out)} Abschnitte"})
    inside = out["conflated"]
    quality_ok = out.loc[inside, "match_quality"].isin(QUALITIES).all() and out.loc[~inside, "match_quality"].isna().all()
    checks.append({"name": "match_quality im Arbeitsgebiet gesetzt, außerhalb leer", "ok": bool(quality_ok),
                   "detail": f"{int(inside.sum())} im Arbeitsgebiet, {int((~inside).sum())} außerhalb"})
    known = {parse_speed_kmh(v) for d in DIRECTIONS for v in layers["speed"][f"geschwindigkeit_{d}"]}
    known |= {resolve_speed(None, v).regular_kmh for d in DIRECTIONS for v in layers["speed"][f"sonderregelung_{d}"]}
    known -= {None}
    values = set(out["speed_official_kmh"].dropna().astype(int))
    checks.append({"name": "Ist-Tempo nur aus Werten der Quelle", "ok": values <= known,
                   "detail": f"Werte {sorted(values)}"})
    bad = 0
    for _, row in out.loc[out["speed_conditional"].notna()].iterrows():
        for c in json.loads(row["speed_conditional"]):
            regular = row[f"speed_official_{c['direction']}_kmh"]
            if c["speed_kmh"] is not None and not pd.isna(regular) and int(regular) == c["speed_kmh"]:
                bad += 1
    checks.append({"name": "Zeitlich begrenztes Tempo nie als Regeltempo (S-CONF-03)", "ok": bad == 0,
                   "detail": f"{bad} Verstöße"})
    return checks


# --- report ----------------------------------------------------------------------------------


def _fmt(x: float, digits: int = 0) -> str:
    return f"{x:,.{digits}f}".replace(",", " ")


def _pct(n: float, d: float) -> str:
    return "–" if not d else f"{100 * n / d:.1f} %"


def _name_key(v) -> str:
    return "" if v is None or pd.isna(v) else str(v).strip().lower()


def _maxspeed_num(v) -> int | None:
    v = _none(v)
    return int(v) if isinstance(v, str) and v.strip().isdigit() else None


def pick_sample(pilot: pd.DataFrame) -> pd.DataFrame:
    """SAMPLE_SIZE random segments, roughly equal per match_quality; missing slots filled from the rest."""
    rng = random.Random(SAMPLE_SEED)
    per_quality = math.ceil(SAMPLE_SIZE / len(QUALITIES))
    picked: list[str] = []
    for q in QUALITIES:
        ids = sorted(pilot.loc[pilot["match_quality"] == q, "segment_id"])
        picked += rng.sample(ids, min(per_quality, len(ids)))
    rest = sorted(set(pilot["segment_id"]) - set(picked))
    picked = picked[:SAMPLE_SIZE] + rng.sample(rest, max(0, min(SAMPLE_SIZE - len(picked), len(rest))))
    return pilot.set_index("segment_id").loc[sorted(picked)].reset_index()


def write_sample(sample: pd.DataFrame) -> None:
    points = gpd.GeoSeries(sample.geometry.interpolate(0.5, normalized=True).values, crs=WORK_CRS).to_crs("EPSG:4326")
    rows = []
    for i, row in sample.iterrows():
        ways = list(row["osm_way_ids"])
        rows.append({
            "segment_id": row["segment_id"], "name_osm": row["name"], "strassenname_official": row.get("strassenname_official"),
            "highway": row["highway"], "length_m": round(float(row["length_m"]), 1),
            "match_quality": row["match_quality"], "hvs_match_quality": row.get("hvs_match_quality"),
            "in_hvs": row.get("in_hvs"), "dtv_official": row.get("dtv_official"),
            "speed_official_kmh": row.get("speed_official_kmh"), "speed_official_text": row.get("speed_official_text"),
            "maxspeed_osm": row["maxspeed_osm"], "speed_conditional": row.get("speed_conditional"),
            "in_zone_t30": row.get("in_zone_t30"), "ist_verkehrsberuhigt": row.get("ist_verkehrsberuhigt"),
            "road_class_official": row.get("road_class_official"),
            "osm_map": osm_map_link(points.iloc[i]), "osm_way": osm_way_link(ways[0]) if ways else None,
            "geoportal": "",  # TODO: link format open (docs/open_questions.md)
            "check_ok": "", "comment": "",
        })
    SAMPLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(SAMPLE_PATH, index=False)


def write_report(out: gpd.GeoDataFrame, ctx: dict, checks: list[dict]) -> None:
    rules, pilot = ctx["rules"], ctx["pilot"]
    work = out[out["conflated"]]
    in_pilot = out[(out["bezirk"] == pilot) & out["conflated"]]
    status = {True: "ok", False: "**FEHLER**"}
    lines = [
        "# Conflation amtlich ↔ OSM (Stufe 3)", "",
        f"Erzeugt: {_now()} von `pipeline/s03_conflate.py`. Nicht amtlicher Entwurf.", "",
        "## Datengrundlage", "",
        f"- Abschnitte: `data/interim/segments.parquet` ({_fmt(len(out))} Abschnitte Hamburg)",
        f"- Arbeitsgebiet: {pilot} + {ctx['buffer_m']} m; abgeglichen werden Abschnitte, die ganz darin liegen "
        f"({_fmt(len(work))}). Außerhalb bleibt `match_quality` leer (keine amtlichen Daten abgerufen).",
        f"- Regelwerk: config/rules.yaml {rules.meta.version}", "",
        "| Schlüssel | Quelle / Ebene | Objekte | Abruf | Lizenz |", "| --- | --- | ---: | --- | --- |",
    ]
    for key, rec in ctx["records"].items():
        lines.append(f"| {key} | {rec['source']} / {rec['layer']} | {_fmt(ctx['n_objects'][key])} | "
                     f"{(rec.get('retrieved_at') or '–')[:10]} | {rec.get('license') or '–'} |")
    lines += [
        "", "**Lücken:**", "",
        "- Der WFS „Strategisches Straßennetz“ (HH-SIB) liefert HTTP 404. Darum stammt `in_hvs` aus den "
        "DTV-Linien der Hauptverkehrsstraßen **2019** (S-CONF-04), nicht aus der HVS-Karte 2023 (nur PDF). "
        "Straßen, die seit 2019 zum HVS-Netz gekommen oder herausgefallen sind, sind falsch zugeordnet.",
        "- Die Zonenebenen (Tempo 30, Tempo 20, verkehrsberuhigt) sind Linien des amtlichen Netzes, keine "
        "Flächen; der Längenanteil wird über den Puffer der richtungsgleichen Linien bestimmt (S-CONF-02).",
        "- Die Ebene `…_sonderregelung` ist eine Teilmenge der Hauptebene (gleiche Geometrien und Felder); "
        "die zeitlich begrenzten Regelungen werden aus der Hauptebene gelesen.", "",
        "## Regeln und Schwellen", "",
    ]
    for r in rules.conflation.rules:
        extra = "".join(f"; {k} = {t.value:g} {t.unit} ({t.source_type})" for k, t in r.thresholds.items())
        lines.append(f"- **{r.id}** ({r.source_type}, {r.status}): {r.description}{extra}")

    lines += ["", f"## Trefferquote (Arbeitsgebiet, {_fmt(len(work))} Abschnitte)", "",
              "| Quelle | exact | partial | none | exact km-Anteil |", "| --- | ---: | ---: | ---: | ---: |"]
    by_source = work["match_quality_by_source"].map(json.loads)
    for src in LINE_SOURCES:
        q = by_source.map(lambda d: d[LAYERS[src][1]])
        km = work.loc[q == "exact", "length_m"].sum()
        lines.append(f"| {LAYERS[src][1]} | {_fmt((q == 'exact').sum())} | {_fmt((q == 'partial').sum())} | "
                     f"{_fmt((q == 'none').sum())} | {_pct(km, work['length_m'].sum())} |")

    lines += ["", f"## match_quality (Tempo-Ebene) je highway-Klasse – {pilot}", "",
              "| highway | Anzahl | exact | partial | none | Name gleich¹ |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for hw in network_highways(rules):
        g = in_pilot[in_pilot["highway"] == hw]
        if g.empty:
            continue
        matched = g[g["match_quality"] != "none"]
        same = (matched["name"].map(_name_key) == matched["strassenname_official"].map(_name_key)).sum()
        lines.append(f"| {hw} | {_fmt(len(g))} | {_pct((g['match_quality'] == 'exact').sum(), len(g))} | "
                     f"{_pct((g['match_quality'] == 'partial').sum(), len(g))} | "
                     f"{_pct((g['match_quality'] == 'none').sum(), len(g))} | {_pct(same, len(matched))} |")
    matched = in_pilot[in_pilot["match_quality"] != "none"]
    same = (matched["name"].map(_name_key) == matched["strassenname_official"].map(_name_key)).sum()
    lines += [f"| **gesamt** | {_fmt(len(in_pilot))} | {_pct((in_pilot['match_quality'] == 'exact').sum(), len(in_pilot))} | "
              f"{_pct((in_pilot['match_quality'] == 'partial').sum(), len(in_pilot))} | "
              f"{_pct((in_pilot['match_quality'] == 'none').sum(), len(in_pilot))} | {_pct(same, len(matched))} |",
              "", "¹ Anteil der zugeordneten Abschnitte, deren OSM-Name gleich dem amtlichen Straßennamen ist "
              "(automatische Plausibilitätsprüfung, ersetzt nicht die manuelle Stichprobe)."]

    sp = in_pilot.dropna(subset=["speed_official_kmh"])
    osm = sp["maxspeed_osm"].map(_maxspeed_num)
    both = sp[osm.notna()]
    agree = (both["speed_official_kmh"].astype(int) == osm[osm.notna()].astype(int)).sum()
    lines += ["", f"## Ist-Tempo – {pilot}", "",
              f"- Abschnitte mit amtlichem Regeltempo: {_fmt(len(sp))} von {_fmt(len(in_pilot))}",
              f"- Übereinstimmung mit OSM-maxspeed (wo beide eine Zahl haben): {_pct(agree, len(both))} "
              f"({_fmt(agree)} von {_fmt(len(both))})",
              f"- Abschnitte mit zeitlich begrenzter Regelung (S-CONF-03, getrennt in `speed_conditional`): "
              f"{_fmt(in_pilot['speed_conditional'].notna().sum())}",
              f"- Regeltempo mehrdeutig (`speed_official_ambiguous`): {_fmt(int(in_pilot['speed_official_ambiguous'].fillna(False).sum()))}",
              f"- Mehrere amtliche Tempi auf einem Abschnitt (`speed_official_conflict`): "
              f"{_fmt(int(in_pilot['speed_official_conflict'].fillna(False).sum()))}", "",
              "| Regeltempo amtlich | Abschnitte | km |", "| --- | ---: | ---: |"]
    for v, g in sp.groupby("speed_official_kmh"):
        lines.append(f"| {v} km/h | {_fmt(len(g))} | {_fmt(g['length_m'].sum() / 1000, 1)} |")
    lines.append(f"| ohne Zahl (z. B. 5-7 km/h, variabel) / keine Zuordnung | "
                 f"{_fmt(len(in_pilot) - len(sp))} | {_fmt((in_pilot['length_m'].sum() - sp['length_m'].sum()) / 1000, 1)} |")

    lines += ["", f"## HVS (S-CONF-04) und Zonen (S-CONF-02) – {pilot}", "",
              "| highway | Anzahl | in_hvs | Tempo-30-Zone | Tempo-20-Zone | verkehrsberuhigt |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for hw in network_highways(rules):
        g = in_pilot[in_pilot["highway"] == hw]
        if g.empty:
            continue
        lines.append(f"| {hw} | {_fmt(len(g))} | {_fmt(int(g['in_hvs'].sum()))} | {_fmt(int(g['in_zone_t30'].sum()))} | "
                     f"{_fmt(int(g['in_zone_t20'].sum()))} | {_fmt(int(g['ist_verkehrsberuhigt'].sum()))} |")
    lines += ["", f"- in_hvs gesamt: {_fmt(int(in_pilot['in_hvs'].sum()))} Abschnitte, "
              f"{_fmt(in_pilot.loc[in_pilot['in_hvs'].astype(bool), 'length_m'].sum() / 1000, 1)} km",
              f"- in_hvs, aber OSM-highway residential/living_street/unclassified (prüfen): "
              f"{_fmt(int(in_pilot.loc[in_pilot['highway'].isin(['residential', 'living_street', 'unclassified']), 'in_hvs'].sum()))}",
              "", "## Prüfungen", "", "| Prüfung | Ergebnis | Detail |", "| --- | --- | --- |"]
    lines += [f"| {c['name']} | {status[bool(c['ok'])]} | {c['detail']} |" for c in checks]
    lines += ["", "## Manuelle Stichprobe", "",
              f"`reports/conflation_sample.csv`: {ctx['n_sample']} Zufallsabschnitte in {pilot} (Seed {SAMPLE_SEED}, "
              "etwa gleich viele je match_quality), mit Links auf OSM-Karte und OSM-Way. Spalte `geoportal` ist leer, "
              "bis das Linkformat geklärt ist (docs/open_questions.md). Prüfende tragen `check_ok` (ja/nein) und "
              "`comment` ein.", "",
              "| Ergebnis | Anzahl |", "| --- | ---: |",
              "| Zuordnung richtig | _offen_ |", "| Zuordnung falsch | _offen_ |",
              "| **Trefferquote** | _offen – nach manueller Prüfung eintragen_ |",
              "", "## Lizenz", "",
              "Abschnitte aus OpenStreetMap-Daten © OpenStreetMap-Beitragende, ODbL 1.0. Amtliche Attribute: "
              "Freie und Hansestadt Hamburg (Widmungen: BVM, dl-de/by-2.0; Höchstgeschwindigkeiten und "
              "Verkehrsmengen: Lizenz in der API nicht angegeben, siehe docs/open_questions.md).", ""]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# --- main ------------------------------------------------------------------------------------


def main() -> int:
    rules = load_rules()
    with open(PROJECT_PATH, encoding="utf-8") as f:
        project = yaml.safe_load(f)["pilot_district"]
    if not SEGMENTS_PATH.exists():
        print("conflate: data/interim/segments.parquet missing; run `make network` first", file=sys.stderr)
        return 1
    try:
        layers, records = load_layers(load_manifest())
    except (FileNotFoundError, ValueError) as e:
        print(f"conflate: {e}", file=sys.stderr)
        return 1

    seg = gpd.read_parquet(SEGMENTS_PATH)
    district = gpd.read_parquet(REPO_ROOT / "data" / "raw" / "district_boundary.parquet")
    work_area = to_work_crs(district).geometry.union_all().buffer(project["buffer_m"])
    in_area = seg.geometry.within(work_area)
    print(f"conflate: {int(in_area.sum())} of {len(seg)} segments in the work area")

    out = conflate(seg, in_area, layers, rules)
    checks = run_checks(seg, out, layers)
    pilot = out[(out["bezirk"] == project["name"]) & out["conflated"]]
    sample = pick_sample(pilot)
    ctx = {"rules": rules, "pilot": project["name"], "buffer_m": project["buffer_m"], "records": records,
           "n_objects": {k: len(v) for k, v in layers.items()}, "n_sample": len(sample)}
    write_report(out, ctx, checks)
    for c in checks:
        print(f"conflate: {c['name']}: {c['ok']} ({c['detail']})")
    if not all(c["ok"] for c in checks):
        print(f"conflate: check(s) failed, {OUT_PATH.name} not written; see {REPORT_PATH}", file=sys.stderr)
        return 1
    write_sample(sample)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_PATH, index=False)
    q = out.loc[out["conflated"], "match_quality"].value_counts().to_dict()
    print(f"conflate: match_quality {q}; in_hvs {int(out['in_hvs'].sum())} -> {OUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
