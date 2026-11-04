"""Stage 9: export for downloads and the website (guide 3.2 Stufe 9, Teil 5, prompts/11_web.md).

Usage: uv run python -m pipeline.s09_export

Reads data/interim/discrepancy.parquet (pilot district only) and data/interim/validation.parquet (robustness
from make validate) and writes data/out/:
  downloads/  segments.parquet (GeoParquet), segments.geojson, segments.csv, rules.yaml, overrides.csv,
              datenbeschreibung.md
  segments/{segment_id}.json  profile per segment (plain-text reasons from rule_trace)
  search.json, table.json, meta.json, district.geojson, licenses.md, changelog.md
  tiles/segments.pmtiles      tippecanoe, layers segments and facilities, zoom 10-16
plus reports/export.md. This is the only stage that transforms to EPSG:4326. Crashes only as counts.
The run stops with exit code 1 if a check fails.
"""

import datetime as dt
import json
import random
import shutil
import subprocess
import sys
from email.utils import parsedate_to_datetime

import geopandas as gpd
import pandas as pd
import yaml

from pipeline.lib import export as ex
from pipeline.lib.crs import WORK_CRS
from pipeline.lib.links import load_viewers, orthophoto_link, osm_way_link, panoramax_link
from pipeline.lib.manifest import REPO_ROOT, load_manifest
from pipeline.lib.rules import load_rules
from pipeline.s04_features import _fmt, _now
from pipeline.s06_coherence import RULE_LABELS
from pipeline.s08_discrepancy import reason_text

PROJECT_PATH = REPO_ROOT / "config" / "project.yaml"
SOURCES_PATH = REPO_ROOT / "config" / "sources.yaml"
IN_PATH = REPO_ROOT / "data" / "interim" / "discrepancy.parquet"
VALIDATION_PATH = REPO_ROOT / "data" / "interim" / "validation.parquet"
OUT_DIR = REPO_ROOT / "data" / "out"
TILES_TMP = REPO_ROOT / "data" / "interim" / "tiles"
REPORT_PATH = REPO_ROOT / "reports" / "export.md"
MIN_ZOOM, MAX_ZOOM = 10, 16
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
# Sources named in every profile (sources.yaml ids), with what they contribute.
PROFILE_SOURCES = {
    "osm": "Netz, Gestaltung (Radführung, Parken), Ist-Tempo ohne amtlichen Wert",
    "speed_limits": "Ist-Tempo, Tempo-30-Zonen",
    "traffic_volumes": "Hauptverkehrsstraßen, Verkehrsmengen 2019",
    "alkis": "Gebäude, Flurstücke (Straßenraumbreite)",
    "population_grid": "Einwohner",
    "gtfs_hvv": "Busfahrten",
    "accidents": "Unfälle (nur Summen je Abschnitt)",
    "schools": "Schulen (OpenStreetMap)",
    "kitas": "Kitas (OpenStreetMap)",
    "cycle_network": "Radnetz (OpenStreetMap)",
}
DOWNLOAD_TEXTS = {
    "segments.parquet": "Abschnitte mit allen Merkmalen (GeoParquet)",
    "segments.geojson": "Abschnitte mit allen Merkmalen (GeoJSON)",
    "segments.csv": "Abschnitte als Tabelle mit Mittelpunkt (CSV)",
    "datenbeschreibung.md": "Datenbeschreibung: Bedeutung aller Spalten",
    "rules.yaml": "Regelwerk mit allen Schwellenwerten und Quellen",
    "overrides.csv": "Fachliche Korrekturen (Korrekturdatei)",
}
FACILITY_LAYERS = {"schools": "data/raw/schools__osm.parquet", "kitas": "data/raw/kitas__osm.parquet"}


def _load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _val(v):
    from pipeline.lib import expr
    return expr.clean_value(v)


# --- context ---------------------------------------------------------------------------------


def data_date(manifest: dict) -> str:
    """As-of date of the OSM extract (Last-Modified), else its retrieval date."""
    osm = manifest["sources"]["osm"]
    if osm.get("last_modified"):
        return parsedate_to_datetime(osm["last_modified"]).date().isoformat()
    return osm["retrieved_at"][:10]


def source_list(manifest: dict, sources: dict) -> list[dict]:
    out = []
    for sid, purpose in PROFILE_SOURCES.items():
        src, man = sources[sid], manifest["sources"].get(sid, {})
        licence = man.get("license") or src.get("license")
        if not licence or licence == "unknown":
            licence = "Lizenz in der Quelle nicht angegeben (wird geklärt)"
        attribution = src.get("attribution") or ("© OpenStreetMap-Beitragende" if man.get("fallback") else None)
        out.append({"id": sid, "title": src["title"], "purpose": purpose,
                    "as_of": str(src.get("as_of") or (man.get("retrieved_at") or "")[:10]),
                    "license": licence, "attribution": attribution})
    return out


def required_width_for(cat: str, rules) -> float | None:
    w = {"GOW50": "GOW50", "GOW30": "GOW30_narrow", "ETW30": "ETW30"}.get(cat)
    if w is None:
        return None
    entry = rules.required_width[w]
    return entry.value if entry.value is not None else entry.range[0]


def join_validation(seg: gpd.GeoDataFrame, rules) -> tuple[gpd.GeoDataFrame, dict]:
    """Add the robustness columns from make validate (left join on segment_id); missing file -> empty columns."""
    v = rules.validation
    ctx = {"runs": v.rule("V-SENS-02").runs, "seed": v.rule("V-SENS-02").seed,
           "delta": v.rule("V-SENS-02").thresholds["delta"].value,
           "min_change_rate": v.rule("V-UNC-01").thresholds["min_change_rate"].value, "rules_version": None}
    cols = ["sens_change_rate", "sens_uncertain", "sens_alt_category", "sens_alt_share", "sens_oat_changes"]
    if VALIDATION_PATH.exists():
        val = pd.read_parquet(VALIDATION_PATH)
        versions = set(val["sens_rules_version"].dropna())
        ctx["rules_version"] = ", ".join(sorted(versions)) or None
        out = seg.merge(val[["segment_id", *cols]], on="segment_id", how="left", validate="one_to_one")
    else:
        print("export: data/interim/validation.parquet missing; run `make validate` first", file=sys.stderr)
        out = seg.assign(**{c: None for c in cols})
    ctx["version_ok"] = ctx["rules_version"] == rules.meta.version
    ctx["n_missing"] = int(out["sens_change_rate"].isna().sum())
    out["sens_uncertain"] = out["sens_uncertain"].astype("boolean")
    return gpd.GeoDataFrame(out, geometry="geometry", crs=seg.crs), ctx


# --- profile ---------------------------------------------------------------------------------


def _cycling(r) -> str:
    track, lane = r.get("separated_cycle_track_present"), r.get("cycle_lane_present")
    if _val(track):
        return "baulicher Radweg"
    if _val(lane):
        return "Radfahr- oder Schutzstreifen"
    if _val(track) is False and _val(lane) is False:
        return "keine Radverkehrsanlage (Radverkehr auf der Fahrbahn)"
    return "unbekannt (in OpenStreetMap nicht erfasst)"


def profile(r: pd.Series, ctx: dict) -> dict:
    rules, texts = ctx["rules"], ctx["texts"]
    cat = r["cat_final"]
    trace = json.loads(r["rule_trace"]) if isinstance(r["rule_trace"], str) else []
    fe_col = ex.FEASIBILITY_BY_CATEGORY.get(cat)
    fe = r.get(fe_col) if fe_col else None
    causes = json.loads(r["disc_causes"]) if isinstance(r["disc_causes"], str) else []
    flags = []
    for e in json.loads(r["coherence_trace"]) if isinstance(r["coherence_trace"], str) else []:
        label = RULE_LABELS.get(e["id"], e["id"])
        if (e["id"], label) not in [(f["rule"], f["text"]) for f in flags]:
            flags.append({"rule": e["id"], "text": label})
    override = r.get("cat_final_source") == "override"
    return {
        "id": r["segment_id"], "name": r["name"] if isinstance(r["name"], str) else None, "bezirk": r["bezirk"],
        "length_m": round(float(r["length_m"]), 1), "highway": r["highway"],
        "osm_way_ids": [int(x) for x in r["osm_way_ids"]],
        "category": {"code": cat, "label": rules.categories[cat].label_de, "text": texts["categories"][cat],
                     "proposed": r["cat_proposed"], "corrected": override,
                     "cascade": r["cat_cascade"] if r["cat_cascade"] != r["cat_proposed"] else None,
                     "override": {"reason": r.get("override_reason"), "author": r.get("override_author"),
                                  "date": _val(r.get("override_date"))} if override else None},
        "reasons": ex.rule_reasons(trace, rules, texts), "rule_path": r["rule_path"],
        "confidence": ex.confidence_info(r["confidence"], json.loads(r["confidence_reasons"]), texts),
        "sensitivity": ex.sensitivity_info(r.to_dict(), rules, texts, ctx["sens"]["runs"], ctx["sens"]["delta"]),
        "ist": {"speed_kmh": _val(r["speed_ist_kmh"]),
                "speed_source": texts["speed_source"].get(r["speed_ist_source"]) if isinstance(r["speed_ist_source"], str) else None,
                "speed_sources_conflict": _val(r.get("speed_sources_conflict")), "cycling": _cycling(r),
                "bus_trips_weekday": _val(r["bus_trips_weekday"]), "dtv": _val(r["dtv_official"]), "dtv_year": 2019,
                "in_hvs": _val(r["in_hvs"]), "in_cycle_network": _val(r["in_cycle_network"])},
        "crosssection": {"width_median_m": _val(r["width_median_m"]), "width_p10_m": _val(r["width_p10_m"]),
                         "required_m": required_width_for(cat, rules), "feasibility": _val(fe),
                         "feasibility_text": texts["feasibility"].get(fe) if isinstance(fe, str) else None,
                         "narrow_points": _val(r.get("narrow_points_count"))},
        "discrepancy": {"speed": _val(r["disc_speed"]), "design": _val(r["disc_design"]), "use": _val(r["disc_use"]),
                        "max": _val(r["disc_max"]), "type": _val(r["disc_type"]),
                        "type_text": rules.discrepancy.types.get(r["disc_type"]) if isinstance(r["disc_type"], str) else None,
                        "causes": [c["label"] for c in causes],
                        "unknown_checks": json.loads(r["disc_design_unknown"]) if isinstance(r["disc_design_unknown"], str) else [],
                        "text": reason_text(r, rules),
                        "crashes": {"ped_cyc": int(r["crashes_ped_cyc"]), "ped": int(r["crashes_ped"]),
                                    "cyc": int(r["crashes_cyc"]), "severe_fatal": int(r["crashes_severe_fatal"]),
                                    "years": r["crash_years"]},
                        "risk": _val(r["risk"]), "priority": _val(r["priority"])},
        "coherence": flags,
        "sources": ctx["sources"],
        "version": ctx["version"],
    }


# --- writers ---------------------------------------------------------------------------------


def write_json(path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def data_description(texts: dict, ctx: dict) -> str:
    lines = ["# Datenbeschreibung – Straßenfunktionsplan Hamburg (Entwurf, nicht amtlich)", "",
             f"Version {ctx['version']}, Bezirk {ctx['pilot']}, {ctx['n']} Abschnitte. Dateien: segments.parquet "
             "(GeoParquet), segments.geojson, segments.csv (mit Mittelpunkt lon/lat), rules.yaml (Regelwerk), "
             "overrides.csv (fachliche Korrekturen). Koordinaten in WGS 84 (EPSG:4326).", "",
             "Lizenz des Abschnittsdatensatzes: ODbL 1.0 (abgeleitet aus OpenStreetMap). Quellenvermerke siehe "
             "Quellen- und Lizenzseite. Unfälle nur als Summen je Abschnitt.", "",
             "| Spalte | Bedeutung |", "| --- | --- |"]
    lines += [f"| {c} | {texts['columns'][c]} |" for c in [*ex.PUBLIC_COLUMNS, "geometry"]]
    return "\n".join(lines) + "\n"


def facilities_frame() -> gpd.GeoDataFrame:
    parts = []
    for kind, path in FACILITY_LAYERS.items():
        g = gpd.read_parquet(REPO_ROOT / path).to_crs(WORK_CRS)
        parts.append(gpd.GeoDataFrame({"kind": "Schule" if kind == "schools" else "Kita", "name": g["name"]},
                                      geometry=g.geometry.representative_point(), crs=WORK_CRS))
    return gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=WORK_CRS).to_crs(ex.EXPORT_CRS)


def build_tiles(tiles: gpd.GeoDataFrame, facilities: gpd.GeoDataFrame, attribution: str) -> None:
    if shutil.which("tippecanoe") is None:
        raise RuntimeError("tippecanoe fehlt (brew install tippecanoe)")
    TILES_TMP.mkdir(parents=True, exist_ok=True)
    seg_path, fac_path = TILES_TMP / "segments.geojson", TILES_TMP / "facilities.geojson"
    tiles.to_file(seg_path, driver="GeoJSON")
    facilities.to_file(fac_path, driver="GeoJSON")
    out = OUT_DIR / "tiles" / "segments.pmtiles"
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["tippecanoe", "-o", str(out), "--force", f"-Z{MIN_ZOOM}", f"-z{MAX_ZOOM}", "-r1",
           "--no-feature-limit", "--no-tile-size-limit", "--no-simplification-of-shared-nodes",
           "--attribution", attribution, "-L", f"segments:{seg_path}", "-L", f"facilities:{fac_path}", "--quiet"]
    subprocess.run(cmd, check=True)


def run_checks(seg: gpd.GeoDataFrame, pub: gpd.GeoDataFrame, ctx: dict) -> list[dict]:
    checks = []

    def add(name, ok, detail):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    add("nur Pilotbezirk", (pub["bezirk"] == ctx["pilot"]).all(), f"{len(pub)} Abschnitte")
    add("segment_id eindeutig und unverändert", pub["segment_id"].is_unique
        and list(pub["segment_id"]) == list(seg["segment_id"]), "Reihenfolge wie discrepancy.parquet")
    add("Export in EPSG:4326", pub.crs.to_epsg() == 4326, str(pub.crs))
    forbidden = {"UIDENTSTLAE", "LINREFX", "LINREFY", "XGCSWGS84", "YGCSWGS84", "rule_trace", "disc_trace"}
    add("keine Einzelunfälle oder Rohspuren", not forbidden & set(pub.columns), "Spalten aus PUBLIC_COLUMNS")
    n_profiles = len(list((OUT_DIR / "segments").glob("*.json")))
    add("Steckbrief je Abschnitt", n_profiles == len(pub), f"{n_profiles} Dateien")
    add("Begründung je Abschnitt", ctx["n_without_reason"] == 0, f"{ctx['n_without_reason']} ohne Klartext")
    sv = ctx["sens"]
    add("Robustheit aus make validate übernommen", sv["n_missing"] == 0 and sv["version_ok"],
        f"{len(pub) - sv['n_missing']}/{len(pub)} Abschnitte, rules.yaml {sv['rules_version'] or '–'}"
        + ("" if sv["version_ok"] else " (veraltet: make validate ausführen)"))
    return checks


def write_report(pub, profiles_sample, checks, ctx) -> None:
    sizes = []
    for p in sorted(OUT_DIR.rglob("*")):
        rel = p.relative_to(OUT_DIR)
        if p.is_file() and p.parent.name != "segments" and rel.parts[:2] != ("basemap", "fonts"):
            sizes.append((str(rel), p.stat().st_size))
    fonts = list((OUT_DIR / "basemap" / "fonts").rglob("*.pbf"))
    if fonts:
        sizes.append((f"basemap/fonts/ ({len(fonts)} Glyphen-Dateien)", sum(f.stat().st_size for f in fonts)))
    profile_bytes = sum(p.stat().st_size for p in (OUT_DIR / "segments").glob("*.json"))
    viewers = ctx["viewers"]
    lines = ["# Export – Stufe 9", "",
             f"Erzeugt: {_now()} von `pipeline/s09_export.py`, Version {ctx['version']}. Nicht amtlicher Entwurf.", "",
             "## Prüfungen", "", "| Prüfung | Ergebnis | Detail |", "| --- | --- | --- |",
             *[f"| {c['name']} | {'ok' if c['ok'] else 'FEHLER'} | {c['detail']} |" for c in checks], "",
             "## Kennzahlen", "",
             f"- Abschnitte: {_fmt(len(pub))} im Bezirk {ctx['pilot']} ({pub['length_m'].sum() / 1000:.1f} km)",
             f"- Suchindex: {_fmt(ctx['n_search'])} Straßennamen; Schulen/Kitas in den Kacheln: {_fmt(ctx['n_facilities'])}",
             f"- Steckbriefe: {_fmt(len(pub))} Dateien, zusammen {profile_bytes / 1e6:.1f} MB",
             f"- Robustheit (make validate, {ctx['sens']['runs']} Läufe): {_fmt(int(pub['sens_uncertain'].fillna(False).sum()))} "
             f"Abschnitte „unsicher“ ({pub.loc[pub['sens_uncertain'].fillna(False).astype(bool), 'length_m'].sum() / 1000:.1f} km)", "",
             "| Datei | Größe |", "| --- | ---: |",
             *[f"| `data/out/{n}` | {s / 1e6:.2f} MB |" for n, s in sizes], "",
             f"## Stichprobe ({SAMPLE_SIZE} zufällige Steckbriefe, Seed {SAMPLE_SEED})", "",
             "Klartext-Begründung wie im Steckbrief. Bitte gegen Orthophoto/Panoramax prüfen.", "",
             "| segment_id | Name | Soll | Begründung | Datenunsicherheit | Links |", "| --- | --- | --- | --- | --- | --- |"]
    for p, geom in profiles_sample:
        mid = geom.interpolate(0.5, normalized=True)
        wgs = gpd.GeoSeries([mid], crs=WORK_CRS).to_crs(4326).iloc[0]
        reasons = "; ".join(x["text"] for x in p["reasons"]) or "–"
        conf = p["confidence"]["level"] + (": " + ", ".join(p["confidence"]["reasons"]) if p["confidence"]["reasons"] else "")
        if p["sensitivity"]["uncertain"]:
            conf += "; unsicher (Sensitivität)"
        lines.append(f"| `{p['id']}` | {p['name'] or '–'} | {p['category']['code']} | {reasons} | {conf} | "
                     f"[Orthophoto]({orthophoto_link(mid, viewers)}) · [Panoramax]({panoramax_link(wgs, viewers)}) · "
                     f"[OSM]({osm_way_link(p['osm_way_ids'][0])}) |")
    lines += ["", "## Lizenz", "", "Abschnittsdatensatz: ODbL 1.0 (© OpenStreetMap-Beitragende); amtliche Quellen "
              "dl-de/by-2.0 bzw. laut Quelle; Unfälle: © Statistische Ämter des Bundes und der Länder, Unfallatlas "
              "(nur Summen). Siehe docs/licenses.md.", ""]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --- main ------------------------------------------------------------------------------------


def main() -> int:
    rules, texts = load_rules(), ex.load_texts()
    project = _load_yaml(PROJECT_PATH)
    sources_yaml = _load_yaml(SOURCES_PATH)
    pilot = project["pilot_district"]["name"]
    if not IN_PATH.exists():
        print("export: data/interim/discrepancy.parquet missing; run `make discrepancy` first", file=sys.stderr)
        return 1
    manifest = load_manifest()
    seg = gpd.read_parquet(IN_PATH)
    seg = seg[seg["conflated"].astype(bool) & seg["cat_final"].notna() & (seg["bezirk"] == pilot)].reset_index(drop=True)
    seg, sens_ctx = join_validation(seg, rules)
    date = data_date(manifest)
    version = f"{rules.meta.version}+{date}"
    ctx = {"rules": rules, "texts": texts, "pilot": pilot, "version": version, "n": len(seg),
           "sources": source_list(manifest, sources_yaml["sources"]), "viewers": load_viewers(), "sens": sens_ctx}

    if OUT_DIR.exists():
        for sub in ("segments", "downloads", "tiles"):
            shutil.rmtree(OUT_DIR / sub, ignore_errors=True)
    dl = OUT_DIR / "downloads"
    dl.mkdir(parents=True, exist_ok=True)

    pub = ex.public_frame(seg)
    pub.to_parquet(dl / "segments.parquet", index=False)
    pub.to_file(dl / "segments.geojson", driver="GeoJSON")
    mid = seg.geometry.interpolate(0.5, normalized=True).to_crs(ex.EXPORT_CRS)  # computed in EPSG:25832
    pub.drop(columns="geometry").assign(lon=mid.x.round(6), lat=mid.y.round(6)).to_csv(dl / "segments.csv", index=False)
    shutil.copy(REPO_ROOT / "config" / "rules.yaml", dl / "rules.yaml")
    shutil.copy(REPO_ROOT / "overrides" / "overrides.csv", dl / "overrides.csv")
    (dl / "datenbeschreibung.md").write_text(data_description(texts, ctx), encoding="utf-8")

    n_without_reason, sample_profiles = 0, []
    rnd = random.Random(SAMPLE_SEED)
    sample_idx = set(rnd.sample(range(len(seg)), min(SAMPLE_SIZE, len(seg))))
    for i, r in seg.iterrows():
        p = profile(r, ctx)
        n_without_reason += not p["reasons"]
        write_json(OUT_DIR / "segments" / f"{p['id']}.json", p)
        if i in sample_idx:
            sample_profiles.append((p, r.geometry))

    search = ex.search_index(pub)
    write_json(OUT_DIR / "search.json", search)
    table = [{"id": r.segment_id, "name": r.name if isinstance(r.name, str) else None, "bz": r.bezirk, "cat": r.cat_final,
              "spd": _val(r.speed_ist_kmh), "dt": _val(r.disc_type), "dm": _val(r.disc_max), "pr": _val(r.priority),
              "conf": r.confidence, "un": None if pd.isna(r.sens_uncertain) else bool(r.sens_uncertain),
              "len": round(float(r.length_m)), "acc": int(r.crashes_ped_cyc)}
             for r in seg.itertuples()]
    write_json(OUT_DIR / "table.json", table)

    district = gpd.read_parquet(REPO_ROOT / "data" / "raw" / "district_boundary.parquet").to_crs(ex.EXPORT_CRS)
    district[["geometry"]].to_file(OUT_DIR / "district.geojson", driver="GeoJSON")
    web = project["web"]
    assets = sources_yaml["web_assets"]
    attribution = ["© OpenStreetMap-Beitragende (ODbL)"] + sorted({s["attribution"] for s in ctx["sources"]
                                                                    if s["attribution"] and "OpenStreetMap" not in s["attribution"]})
    meta = {"version": version, "rules_version": rules.meta.version, "data_date": date,
            "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "pilot": pilot,
            "n_segments": len(pub), "bbox": [round(float(v), 6) for v in district.total_bounds],
            "categories": {c: {"label": rules.categories[c].label_de, "text": texts["categories"][c]}
                           for c in rules.categories if not rules.categories[c].rural},
            "discrepancy_types": dict(rules.discrepancy.types),
            "feasibility": texts["feasibility"],
            "sensitivity": {k: sens_ctx[k] for k in ("runs", "seed", "delta", "min_change_rate", "rules_version")},
            "width_classes_m": {"ETW30": required_width_for("ETW30", rules), "GOW50": required_width_for("GOW50", rules)},
            "disclaimer": texts["disclaimer"], "site_title": web["site_title"],
            "github_repo": web.get("github_repo"), "feedback_email": web.get("feedback_email"),
            "tiles_base_url": web.get("tiles_base_url"),
            "sources": ctx["sources"], "attribution": attribution,
            "downloads": [{"file": f.name, "bytes": f.stat().st_size, "text": DOWNLOAD_TEXTS[f.name]}
                          for f in sorted(dl.iterdir()) if f.name in DOWNLOAD_TEXTS],
            "basemap": {k: {"title": v["title"], "license": v["license"], "attribution": v.get("attribution")}
                        for k, v in assets.items()}}
    write_json(OUT_DIR / "meta.json", meta)
    shutil.copy(REPO_ROOT / "docs" / "licenses.md", OUT_DIR / "licenses.md")
    shutil.copy(REPO_ROOT / "CHANGELOG.md", OUT_DIR / "changelog.md")

    facilities = facilities_frame()
    try:
        build_tiles(ex.tile_frame(pub), facilities, "© OpenStreetMap-Beitragende; Straßenfunktionsplan (Entwurf)")
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"export: tiles failed: {exc}", file=sys.stderr)
        return 1

    ctx.update(n_without_reason=n_without_reason, n_search=len(search), n_facilities=len(facilities))
    checks = run_checks(seg, pub, ctx)
    write_report(pub, sample_profiles, checks, ctx)
    for c in checks:
        print(f"export: {c['name']}: {c['ok']} ({c['detail']})")
    if not all(c["ok"] for c in checks):
        print(f"export: check(s) failed; see {REPORT_PATH}", file=sys.stderr)
        return 1
    print(f"export: {len(pub)} segments, version {version} -> {OUT_DIR.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
