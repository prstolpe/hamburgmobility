"""Stage 1: fetch all sources from config/sources.yaml for the work area (config/project.yaml, area).

Usage: uv run python -m pipeline.s01_fetch [--only id,id] [--refresh]

Only URLs from sources.yaml are used. A failing source is recorded and reported, never
replaced by another source; the run then exits with code 1. WFS and OGC API sources are requested in square tiles
(area.fetch_tile_m) and merged; features returned by two tiles are identical and dropped by clean().
"""

import argparse
import datetime as dt
import json
import random
import re
import sys
import zipfile
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime
from pathlib import Path

import geopandas as gpd
import pandas as pd
import yaml

from pipeline.lib import ogcapi, sensorthings, wfs
from pipeline.lib.area import RURAL_PATH, WORK_AREA_PATH, build_work_area, load_area_config, select_districts, select_rural
from pipeline.lib.boundary import BoundaryError, boundaries_from_pbf
from pipeline.lib.crs import WORK_CRS
from pipeline.lib.geo import clean, features_to_gdf, keep_intersecting, parquet_safe, tile_bboxes
from pipeline.lib.grid import read_grid_zip
from pipeline.lib.http import FetchError, get, get_json, make_session
from pipeline.lib.links import osm_map_link
from pipeline.lib.manifest import REPO_ROOT, file_record, load_manifest, save_manifest, sha256_file

SOURCES_PATH = REPO_ROOT / "config" / "sources.yaml"
RAW_DIR = REPO_ROOT / "data" / "raw"
REPORT_PATH = REPO_ROOT / "reports" / "data_report.md"
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
# OSM tags kept for fallback sources unless sources.yaml lists `fallback_osm.columns`.
OSM_FALLBACK_COLUMNS = ["amenity", "cycle_network", "network", "ref", "route"]


@dataclass
class Result:
    source_id: str
    title: str
    status: str  # ok | fehler | fehlt | manuell | fallback | fallback_fehlt
    url: str | None = None
    license: str | None = None
    retrieved_at: str | None = None
    files: list[dict] = field(default_factory=list)
    listing: dict[str, str] = field(default_factory=dict)  # feature types / collections seen
    attribution: str | None = None
    error: str | None = None
    note: str | None = None
    skipped_records: dict[str, list[int]] = field(default_factory=dict)  # collection -> offsets (skip_broken_records)


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _url_comments(path: Path) -> dict[str, str]:
    """TODO comments on `url:` lines per source (YAML loaders drop comments)."""
    comments, current = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if m := re.match(r"^  ([a-z0-9_]+):\s*$", line):
            current = m.group(1)
        elif current and (m := re.match(r"^    url:.*?#\s*(.+)$", line)):
            comments[current] = m.group(1).strip()
    return comments


def _write_layer(gdf: gpd.GeoDataFrame, source_id: str, layer: str) -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    short = layer.split(":")[-1]
    path = RAW_DIR / f"{source_id}__{short}.parquet"
    parquet_safe(gdf).to_parquet(path)
    return {"layer": layer, **file_record(path, gdf)}


# --- OSM -------------------------------------------------------------------------------------


def fetch_osm(session, source_id: str, src: dict, manifest: dict, refresh: bool) -> tuple[Result, Path | None]:
    result = Result(source_id, src["title"], "ok", url=src["url"], license=src.get("license"))
    previous = manifest["sources"].get(source_id, {})
    old_files = previous.get("files", [])
    if not refresh and old_files:
        path = REPO_ROOT / old_files[0]["path"]
        if path.exists() and sha256_file(path) == old_files[0]["sha256"]:
            result.files, result.retrieved_at = old_files, previous.get("retrieved_at")
            result.note = f"lokale Datei wiederverwendet (Stand {previous.get('last_modified')})"
            return result, path
    try:
        response = get(session, src["url"], stream=True)
        last_modified = response.headers.get("Last-Modified")
        stamp = parsedate_to_datetime(last_modified).date().isoformat() if last_modified else _now()[:10]
        path = RAW_DIR / "osm" / f"hamburg_{stamp}.osm.pbf"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    except (FetchError, OSError) as exc:
        result.status, result.error = "fehler", str(exc)
        return result, None
    result.retrieved_at = _now()
    result.files = [{"layer": "pbf", **file_record(path)}]
    result.note = f"Last-Modified: {last_modified}"
    manifest["sources"].setdefault(source_id, {})["last_modified"] = last_modified
    return result, path


def fetch_osm_fallback(pbf: Path, source_id: str, src: dict, area_wgs84) -> Result:
    """OSM fallback for a source without URL (marked as fallback, never silent)."""
    from pyrosm import OSM

    spec = src["fallback_osm"]
    result = Result(source_id, src["title"], "fallback", url=None, license="ODbL-1.0",
                    retrieved_at=_now(), note=f"Fallback OSM: {json.dumps(spec, ensure_ascii=False)}")
    osm = OSM(str(pbf), bounding_box=area_wgs84)
    try:
        if "tags" in spec:
            gdf = osm.get_pois(custom_filter=spec["tags"])
        else:
            gdf = osm.get_data_by_custom_criteria(custom_filter=spec["relations"], filter_type="keep",
                                                  keep_nodes=False, keep_ways=False, keep_relations=True)
    except Exception as exc:  # pyrosm raises various errors for unsupported relation types
        result.status, result.error = "fallback_fehlt", f"pyrosm: {exc}"
        return result
    if gdf is None or gdf.empty:
        result.status, result.error = "fallback_fehlt", "keine passenden OSM-Objekte gelesen"
        return result
    wanted = ["id", "osm_type", "name", *spec.get("columns", OSM_FALLBACK_COLUMNS), "geometry"]
    keep = [c for c in dict.fromkeys(wanted) if c in gdf.columns]
    result.files = [_write_layer(clean(gdf[keep]), source_id, "osm")]
    return result


# --- file downloads (GTFS, Zensus grid, Unfallatlas) ----------------------------------------------------


def _download(session, url: str, path: Path) -> None:
    response = get(session, url, stream=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    with open(tmp, "wb") as f:
        for chunk in response.iter_content(chunk_size=1 << 20):
            f.write(chunk)
    tmp.replace(path)


def _reusable(previous: dict, layer: str, path: Path, refresh: bool) -> bool:
    old = next((f for f in previous.get("files", []) if f.get("layer") == layer), None)
    return (not refresh and old is not None and old["path"] == str(path.relative_to(REPO_ROOT))
            and path.exists() and sha256_file(path) == old["sha256"])


def fetch_download_files(session, source_id: str, src: dict, manifest: dict, refresh: bool) -> Result:
    """Several files below one base URL (fetch.files: key -> file name), e.g. one Unfallatlas ZIP per year.

    With fetch.points the records of the state are counted per file (coverage); no point layer is written,
    because single crashes are only kept in the original ZIPs (CLAUDE.md: Unfalldaten nur aggregiert).
    """
    from pipeline.lib.accidents import read_accidents_zip

    result = Result(source_id, src["title"], "ok", url=src["url"], license=src.get("license"),
                    attribution=src.get("attribution"))
    previous = manifest["sources"].get(source_id, {})
    spec = src["fetch"].get("points")
    reused, empty = 0, []
    for key, name in src["fetch"]["files"].items():
        layer, path = f"zip_{key}", RAW_DIR / source_id / name
        if _reusable(previous, layer, path, refresh):
            reused += 1
        else:
            try:
                _download(session, src["url"] + name, path)
            except (FetchError, OSError) as exc:
                result.status, result.error = "fehler", f"{name}: {exc}"
                return result
        result.files.append({"layer": layer, **file_record(path)})
        if spec:
            try:
                n = len(read_accidents_zip(path, spec))
            except (KeyError, ValueError, zipfile.BadZipFile) as exc:
                result.status, result.error = "fehler", f"{name}: {exc}"
                return result
            result.listing[str(key)] = f"{n} Unfälle Hamburg" if n else "keine Unfälle Hamburg"
            if n == 0:
                empty.append(str(key))
    result.retrieved_at = previous.get("retrieved_at") if reused == len(result.files) else _now()
    notes = []
    if reused:
        notes.append(f"{reused} lokale Datei(en) wiederverwendet")
    if empty:
        notes.append(f"ohne Daten für Hamburg: {', '.join(empty)}")
    result.note = "; ".join(notes) or None
    return result


def fetch_download(session, source_id: str, src: dict, area, manifest: dict, refresh: bool) -> Result:
    """Download a file once (reused while its hash matches the manifest); optionally extract a grid layer."""
    if "files" in src["fetch"]:
        return fetch_download_files(session, source_id, src, manifest, refresh)
    result = Result(source_id, src["title"], "ok", url=src["url"], license=src.get("license"),
                    attribution=src.get("attribution"))
    previous = manifest["sources"].get(source_id, {})
    old = next((f for f in previous.get("files", []) if f.get("layer") == "zip"), None)
    path = RAW_DIR / source_id / Path(src["url"].split("?")[0]).name
    reuse = (not refresh and old is not None and old["path"] == str(path.relative_to(REPO_ROOT))
             and path.exists() and sha256_file(path) == old["sha256"])
    if reuse:
        result.retrieved_at = previous.get("retrieved_at")
        result.note = "lokale Datei wiederverwendet"
    else:
        try:
            _download(session, src["url"], path)
        except (FetchError, OSError) as exc:
            result.status, result.error = "fehler", str(exc)
            return result
        result.retrieved_at = _now()
    result.files = [{"layer": "zip", **file_record(path)}]
    grid = src["fetch"].get("grid")
    if grid:
        area_grid = gpd.GeoSeries([area], crs=WORK_CRS).to_crs(grid["crs"]).iloc[0]
        try:
            cells = read_grid_zip(path, grid, area_grid).to_crs(WORK_CRS)
        except (KeyError, ValueError) as exc:
            result.status, result.error = "fehler", f"{grid['member']}: {exc}"
            return result
        result.files.append(_write_layer(cells, source_id, f"{int(grid['cell_m'])}m"))
    return result


# --- WFS / OGC API / SensorThings ------------------------------------------------------------


def _concat(parts: list[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    parts = [p for p in parts if not p.empty]
    if not parts:
        return gpd.GeoDataFrame(geometry=[], crs=WORK_CRS)
    return gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=parts[0].crs)


def fetch_wfs(session, source_id: str, src: dict, area, tiles) -> Result:
    result = Result(source_id, src["title"], "ok", url=src["url"], license=src.get("license"))
    caps = wfs.capabilities(session, src["url"])
    result.listing = caps.titles
    result.attribution = src.get("attribution")
    if caps.fees and "Quellenvermerk:" in caps.fees and not result.attribution:
        result.attribution = caps.fees.split("Quellenvermerk:", 1)[1].strip(' "')
    wanted = src["fetch"]["typenames"]
    typenames = caps.typenames if wanted == "all" else wanted
    missing = sorted(set(typenames) - set(caps.typenames))
    if missing:
        raise FetchError(f"feature types not offered by the service: {missing}")
    if wfs.GEOJSON not in caps.output_formats:
        raise FetchError(f"service does not offer {wfs.GEOJSON}")
    for typename in typenames:
        parts = []
        for bbox in tiles:
            expected = wfs.hits(session, src["url"], typename, bbox)
            if expected:
                parts.append(wfs.get_features(session, src["url"], typename, bbox, expected=expected,
                                              paging=caps.paging, count_default=caps.count_default))
        gdf = keep_intersecting(clean(_concat(parts)), area)
        result.files.append(_write_layer(gdf, source_id, typename))
        if gdf.empty:  # make an empty layer checkable: how many exist city-wide?
            total = wfs.hits(session, src["url"], typename, None)
            result.note = f"{typename}: 0 Objekte im Arbeitsgebiet, {total} im gesamten Dienst"
    result.retrieved_at = _now()
    return result


def fetch_ogcapi(session, source_id: str, src: dict, area, tiles) -> Result:
    """Per collection in tiles; with fetch.bbox: false the whole collection in one request series."""
    result = Result(source_id, src["title"], "ok", url=src["url"], license=src.get("license"))
    available = ogcapi.collections(session, src["url"])
    result.listing = {c["id"]: c["title"] or "" for c in available}
    wanted = src["fetch"]["collections"]
    missing = sorted(set(wanted) - set(result.listing))
    if missing:
        raise FetchError(f"collections not offered by the API: {missing}")
    use_bbox = src["fetch"].get("bbox", True)
    skip_broken = bool(src["fetch"].get("skip_broken_records", False))
    if skip_broken and use_bbox:
        raise FetchError("fetch.skip_broken_records needs fetch.bbox: false (offset paging over the whole collection)")
    for collection in wanted:
        if skip_broken:
            gdf, skipped = ogcapi.get_items_skipping_broken(session, src["url"], collection)
            result.skipped_records[collection] = skipped
        elif use_bbox:
            gdf = _concat([ogcapi.get_items(session, src["url"], collection, bbox) for bbox in tiles])
        else:
            gdf = ogcapi.get_items(session, src["url"], collection, None)
        result.files.append(_write_layer(keep_intersecting(clean(gdf), area), source_id, collection))
    if any(result.skipped_records.values()):
        result.note = "; ".join(f"{c}: {len(o)} Datensatz/Datensätze vom Server nicht lieferbar (HTTP 500), "
                                f"übersprungen bei offset {', '.join(map(str, o))}"
                                for c, o in result.skipped_records.items() if o)
    result.retrieved_at = _now()
    return result


def fetch_sensorthings(session, source_id: str, src: dict, area, area_wgs84) -> Result:
    """Inventory only: Locations in the work area with their Things, no observations."""
    result = Result(source_id, src["title"], "ok", url=src["url"], license=src.get("license"),
                    note="nur Bestand (Locations + Things), keine Messwerte")
    params = {"$filter": f"st_intersects(location, geography'{area_wgs84.envelope.wkt}')",
              "$expand": "Things($select=name,description,properties)", "$top": 1000, "$count": "true"}
    page = get_json(session, f"{src['url']}/Locations", params=params)
    expected = page.get("@iot.count")
    locations = list(page.get("value", []))
    while next_link := page.get("@iot.nextLink"):
        page = get_json(session, next_link)
        locations.extend(page.get("value", []))
    if expected is not None and len(locations) != expected:
        raise FetchError(f"@iot.count {expected}, got {len(locations)}")
    features = []
    for loc in locations:
        geom = loc.get("location") or {}
        geom = geom.get("geometry", geom) if geom.get("type") == "Feature" else geom
        things = loc.get("Things", [])
        features.append({"type": "Feature", "geometry": geom, "properties": {
            "location_id": loc.get("@iot.id"), "location_name": loc.get("name"), "n_things": len(things),
            "things": json.dumps(things, ensure_ascii=False)}})
    gdf = keep_intersecting(clean(features_to_gdf(features, crs="EPSG:4326")), area)
    result.files.append(_write_layer(gdf, source_id, "locations_things"))
    result.retrieved_at = _now()
    return result


def fetch_sensorthings_counters(session, source_id: str, src: dict, area) -> Result:
    """Counter stations of one SensorThings service with their daily counts of one year (fetch.year)."""
    spec = src["fetch"]
    year = int(spec["year"])
    result = Result(source_id, src["title"], "ok", url=src["url"], license=src.get("license"),
                    note=f"Zählstellen mit Tageswerten {year} (layerName {spec['layer_name']})")
    stations = sensorthings.counter_stations(session, src["url"], spec["service_name"], spec["layer_name"])
    stations = keep_intersecting(clean(stations), area)
    parts = []
    for row in stations.itertuples():
        df = sensorthings.daily_counts(session, src["url"], int(row.datastream_id), year)
        df.insert(0, "datastream_id", int(row.datastream_id))
        df.insert(0, "thing_id", int(row.thing_id))
        parts.append(df)
    daily = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(
        columns=["thing_id", "datastream_id", "date", "count"])
    stations["n_days"] = stations["datastream_id"].map(daily.groupby("datastream_id").size()).fillna(0).astype(int)
    result.files.append(_write_layer(stations, source_id, "stations"))
    path = RAW_DIR / f"{source_id}__daily_{year}.parquet"
    daily.to_parquet(path)
    result.files.append({"layer": f"daily_{year}", "n_rows": len(daily), **file_record(path)})
    result.retrieved_at = _now()
    return result


# --- report ----------------------------------------------------------------------------------


def _samples(results: list[Result]) -> list[dict]:
    rows = []
    for r in results:
        for f in r.files:
            if f["path"].endswith(".parquet") and f.get("n_features"):
                gdf = gpd.read_parquet(REPO_ROOT / f["path"])
                for idx in range(len(gdf)):
                    rows.append((r.source_id, f["layer"], f["path"], idx))
    rng = random.Random(SAMPLE_SEED)
    picked = rng.sample(rows, min(SAMPLE_SIZE, len(rows)))
    out, cache = [], {}
    for source_id, layer, path, idx in sorted(picked):
        gdf = cache.setdefault(path, gpd.read_parquet(REPO_ROOT / path))
        row = gdf.iloc[idx]
        point = gpd.GeoSeries([row.geometry.representative_point()], crs=WORK_CRS).to_crs("EPSG:4326").iloc[0]
        label = next((str(row[c]) for c in ("strassenname", "name", "location_name", "bezeichnung")
                      if c in gdf.columns and row[c] not in (None, "")), "")
        out.append({"source": source_id, "layer": layer.split(":")[-1], "label": label, "link": osm_map_link(point)})
    return out


def write_report(results: list[Result], work_area: dict, url_comments: dict, sources: dict) -> None:
    lines = [
        "# Datenbericht – Abruf Arbeitsgebiet",
        "",
        f"Erzeugt: {_now()} von `pipeline/s01_fetch.py`. Nicht amtlicher Entwurf.",
        "",
        "## Arbeitsgebiet",
        "",
    ]
    if work_area.get("error"):
        lines += [f"**Fehler:** {work_area['error']}", ""]
    else:
        excluded = ", ".join(f"{e['name']} (admin_level {e['admin_level']})" for e in work_area["exclude"]) or "–"
        lines += [f"Bezirke von {work_area['city']} (admin_level {work_area['district_admin_level']}, Grenzen aus OSM, "
                  "weil die ALKIS-URL in config/sources.yaml fehlt):", "",
                  "| Bezirk | OSM-Relation | Fläche km² |", "| --- | ---: | ---: |"]
        lines += [f"| {d['name']} | {d['osm_id']} | {d['area_km2']:.1f} |" for d in work_area["districts"]]
        lines += [
            f"| **gesamt** | | **{work_area['area_km2']:.1f}** |",
            "",
            f"- Ausgeschlossen: {excluded} samt dem abgetrennten Polygonteil, in dem es liegt (Neuwerk: Insel, "
            "Scharhörn, Wattenmeer; Entscheidung 2026-11-04)",
            f"- Puffer: {work_area['buffer_m']:.0f} m, Arbeitsgebiet {work_area['area_buffered_km2']:.1f} km²",
            f"- Abgerufen wird das ganze Arbeitsgebiet. Nicht klassifiziert werden {len(work_area.get('rural', []))} ländliche "
            f"Stadtteile ({sum(r['area_km2'] for r in work_area.get('rural', [])):.1f} km²; config/project.yaml, "
            f"rural_exclude): {', '.join(r['name'] for r in work_area.get('rural', [])) or '–'}",
            f"- Bounding Box (EPSG:25832): {work_area['bbox']}",
            f"- Abruf von WFS und OGC API in {work_area['n_tiles']} Kacheln zu {work_area['tile_m'] / 1000:.0f} km; "
            "doppelt gelieferte Objekte an Kachelgrenzen werden entfernt.",
            "- Objekte, die das Arbeitsgebiet schneiden, werden vollständig übernommen (kein Zuschnitt).",
            "",
        ]
    lines += ["## Übersicht je Quelle", "",
              "| Quelle | Status | Objekte | Lizenz | Abruf | Hinweis |", "| --- | --- | --- | --- | --- | --- |"]
    for r in results:
        n = sum(f.get("n_features", 0) for f in r.files if "n_features" in f)
        hint = r.error or r.note or ""
        if r.status == "fehlt":
            hint = url_comments.get(r.source_id, "URL in config/sources.yaml ergänzen")
        lines.append(f"| {r.source_id} | {r.status} | {n if r.files else '–'} | {r.license or 'unbekannt'} | "
                     f"{(r.retrieved_at or '–')[:10]} | {hint.replace('|', '/')} |")
    lines += ["", "## Ebenen", "", "| Quelle | Ebene | Objekte | CRS | Bounding Box | Datei |",
              "| --- | --- | --- | --- | --- | --- |"]
    for r in results:
        for f in r.files:
            lines.append(f"| {r.source_id} | {f['layer']} | {f.get('n_features', '–')} | {f.get('crs', '–')} | "
                         f"{f.get('bbox', '–')} | `{f['path']}` |")
    lines += ["", "## Angebotene Feature-Typen und Collections", ""]
    for r in results:
        if r.listing:
            fetched = {f["layer"] for f in r.files}
            items = ", ".join(f"{k}{' ✔' if k in fetched else ''}" for k in r.listing)
            lines.append(f"- **{r.source_id}**: {items}")
    volumes = next((r for r in results if r.source_id == "traffic_volumes"), None)
    if volumes and volumes.listing:
        years = sorted(int(m.group(1)) for k in volumes.listing if (m := re.search(r"_hvs_(\d{4})$", k)))
        if years:
            lines += ["", f"Neuester Jahrgang Verkehrsmengen Hauptverkehrsstraßen: **{years[-1]}**."]
    lines += ["", "## Quellenvermerke", ""]
    for r in results:
        if not r.files:
            continue
        attribution = r.attribution or sources[r.source_id].get("attribution")
        if r.status.startswith("fallback"):
            attribution = "© OpenStreetMap-Beitragende"
        lines.append(f"- {r.source_id}: {attribution or 'Quellenvermerk unbekannt – klären'} "
                     f"({r.license or 'Lizenz unbekannt'})")
    lines += ["", f"## Stichprobe ({SAMPLE_SIZE} zufällige Objekte, Seed {SAMPLE_SEED})", "",
              "Links auf OpenStreetMap. Orthophoto- und Panoramax-Links folgen, sobald das Linkformat "
              "geklärt ist (docs/open_questions.md).", "", "| Quelle | Ebene | Bezeichnung | Karte |",
              "| --- | --- | --- | --- |"]
    for s in _samples(results):
        lines.append(f"| {s['source']} | {s['layer']} | {s['label']} | [OSM]({s['link']}) |")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --- main ------------------------------------------------------------------------------------


def _from_manifest(source_id: str, src: dict, entry: dict) -> Result:
    """Result of an earlier run (source skipped with --only), so the report stays complete."""
    return Result(source_id, entry.get("title") or src["title"], entry.get("status") or "fehlt", url=entry.get("url"),
                  license=entry.get("license"), retrieved_at=entry.get("retrieved_at"), files=entry.get("files") or [],
                  attribution=entry.get("attribution"), error=entry.get("error"),
                  note="aus früherem Abruf (nicht neu geladen)")


def _manifest_entry(r: Result, src: dict, previous: dict) -> dict:
    entry = {k: v for k, v in previous.items() if k == "last_modified"}
    entry.update({"title": r.title, "url": r.url, "access": src.get("access"), "status": r.status,
                  "license": r.license, "attribution": src.get("attribution"), "retrieved_at": r.retrieved_at,
                  "fallback": r.status.startswith("fallback"), "files": r.files, "error": r.error})
    if r.skipped_records:
        entry["skipped_records"] = r.skipped_records
    elif "skipped_records" in previous and r.note == "aus früherem Abruf (nicht neu geladen)":
        entry["skipped_records"] = previous["skipped_records"]
    return entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", help="comma-separated source ids (OSM and boundary always run)")
    parser.add_argument("--refresh", action="store_true", help="download the OSM extract and other files again")
    args = parser.parse_args(argv)

    sources = _load_yaml(SOURCES_PATH)["sources"]
    cfg = load_area_config()
    tile_m = float(_load_yaml(REPO_ROOT / "config" / "project.yaml")["area"]["fetch_tile_m"])
    only = set(args.only.split(",")) if args.only else None
    manifest = load_manifest()
    session = make_session()
    results: list[Result] = []

    osm_result, pbf = fetch_osm(session, "osm", sources["osm"], manifest, args.refresh)
    osm_result.attribution = sources["osm"].get("attribution")
    print(f"osm: {osm_result.status} {osm_result.error or osm_result.note or ''}")

    work_area: dict = {}
    area = area_wgs84 = None
    tiles: list = []
    if pbf is None:
        work_area["error"] = "OSM-Auszug fehlt, daher keine Bezirksgrenzen"
    else:
        try:
            boundaries = boundaries_from_pbf(pbf)
            districts = select_districts(boundaries, cfg)
            rural = select_rural(boundaries, cfg)
            rural.to_parquet(RURAL_PATH)
            area = build_work_area(districts, cfg.buffer_m)
            area_wgs84 = gpd.GeoSeries([area], crs=WORK_CRS).to_crs("EPSG:4326").iloc[0]
            tiles = tile_bboxes(area, tile_m)
            districts.to_parquet(WORK_AREA_PATH)
            old_boundary = RAW_DIR / "district_boundary.parquet"  # pilot era (until 2026-11-04)
            old_boundary.unlink(missing_ok=True)
            osm_result.files = [f for f in osm_result.files
                                if f["layer"] not in ("district_boundary", "work_area", "rural_excluded")]
            osm_result.files.append({"layer": "work_area", **file_record(WORK_AREA_PATH, districts)})
            osm_result.files.append({"layer": "rural_excluded", **file_record(RURAL_PATH, rural)})
            work_area = {"districts": [{"name": r["name"], "osm_id": int(r["id"]), "area_km2": r.geometry.area / 1e6}
                                       for _, r in districts.iterrows()],
                         "city": cfg.city_name, "district_admin_level": cfg.district_admin_level,
                         "exclude": cfg.exclude, "buffer_m": cfg.buffer_m,
                         "area_km2": float(districts.area.sum() / 1e6), "area_buffered_km2": area.area / 1e6,
                         "bbox": [round(v, 1) for v in area.bounds], "tile_m": tile_m, "n_tiles": len(tiles),
                         "rural": [{"name": r["name"], "area_km2": r.geometry.area / 1e6} for _, r in rural.iterrows()],
                         "boundary_source": "osm"}
        except BoundaryError as exc:
            work_area["error"] = str(exc)
    if work_area.get("error"):
        print(f"Arbeitsgebiet: FEHLER {work_area['error']}")

    url_comments = _url_comments(SOURCES_PATH)
    for source_id, src in sources.items():
        if source_id == "osm":
            results.append(osm_result)
            continue
        if only and source_id not in only:
            previous = manifest["sources"].get(source_id)
            if previous:  # keep the last result in manifest and report
                results.append(_from_manifest(source_id, src, previous))
            continue
        fetch, url = src.get("fetch"), src.get("url")
        if url is None and "fallback_osm" not in src:
            result = Result(source_id, src["title"], "fehlt", license=src.get("license"))
        elif url is None:
            result = (fetch_osm_fallback(pbf, source_id, src, area_wgs84) if area is not None else
                      Result(source_id, src["title"], "fallback_fehlt", error="kein Arbeitsgebiet"))
        elif fetch is None:
            result = Result(source_id, src["title"], "manuell", url=url, license=src.get("license"),
                            note="kein maschinenlesbarer Direktzugriff in sources.yaml (Webseite/PDF)")
        elif area is None:
            result = Result(source_id, src["title"], "fehler", url=url, license=src.get("license"),
                            error="kein Arbeitsgebiet (Bezirksgrenzen fehlen)")
        else:
            handlers = {"download": lambda: fetch_download(session, source_id, src, area, manifest, args.refresh),
                        "wfs": lambda: fetch_wfs(session, source_id, src, area, tiles),
                        "ogc_api_features": lambda: fetch_ogcapi(session, source_id, src, area, tiles),
                        "sensorthings": lambda: fetch_sensorthings(session, source_id, src, area, area_wgs84),
                        "sensorthings_counters": lambda: fetch_sensorthings_counters(session, source_id, src, area)}
            try:
                result = handlers[src["access"]]()
            except FetchError as exc:
                result = Result(source_id, src["title"], "fehler", url=url, license=src.get("license"),
                                error=str(exc))
        print(f"{source_id}: {result.status} {result.error or ''}")
        results.append(result)

    for r in results:
        manifest["sources"][r.source_id] = _manifest_entry(r, sources[r.source_id],
                                                          manifest["sources"].get(r.source_id, {}))
    manifest["work_area"] = work_area
    manifest["updated_at"] = _now()
    save_manifest(manifest)
    write_report(results, work_area, url_comments, sources)
    print(f"Bericht: {REPORT_PATH.relative_to(REPO_ROOT)}")

    failed = [r.source_id for r in results if r.status == "fehler" and r.note != "aus früherem Abruf (nicht neu geladen)"] + (["work_area"] if work_area.get("error") else [])
    if failed:
        print(f"FEHLER bei: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
