"""Stage 2: OSM road network and segments with stable IDs (guide 3.2 Stufe 2).

Usage: uv run python -m pipeline.s02_network

Builds the network for all of Hamburg (so IDs at the edge of the pilot district do not depend on
a clip) and writes data/interim/segments.parquet plus reports/network.md. Rules and thresholds
come from config/rules.yaml (section network). The run stops with exit code 1 if a check fails;
segments.parquet is then not written.
"""

import datetime as dt
import random
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely
import yaml

from pipeline.lib.boundary import boundaries_from_pbf
from pipeline.lib.crs import WORK_CRS, to_work_crs
from pipeline.lib.links import osm_map_link, osm_way_link
from pipeline.lib.manifest import REPO_ROOT, load_manifest, sha256_file
from pipeline.lib.network import segments_from_edges, select_ways
from pipeline.lib.rules import load_rules, network_highways

PROJECT_PATH = REPO_ROOT / "config" / "project.yaml"
OUT_PATH = REPO_ROOT / "data" / "interim" / "segments.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "network.md"
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
# Acceptance criterion from prompts/04_network.md (Prüfschritt), not a classification threshold.
MAX_LENGTH_DEVIATION = 0.01
BEZIRK_ADMIN_LEVEL = "9"  # config/project.yaml: admin_level 9 = Bezirk in Hamburg


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _pbf_from_manifest(manifest: dict) -> dict:
    osm = manifest["sources"].get("osm") or {}
    pbf = next((f for f in osm.get("files", []) if f.get("layer") == "pbf"), None)
    if pbf is None or not (REPO_ROOT / pbf["path"]).exists():
        raise FileNotFoundError("OSM extract missing in data/manifest.json or on disk; run `make fetch` first")
    return {**pbf, "retrieved_at": osm.get("retrieved_at"), "url": osm.get("url")}


def _with_tag_columns(df: pd.DataFrame) -> pd.DataFrame:
    for c in ("service", "access", "motor_vehicle", "motorcar", "tags", "name"):
        if c not in df.columns:
            df[c] = None
    return df


def read_edges(pbf: Path, rules) -> gpd.GeoDataFrame:
    """Node-to-node edges of all ways in the network (highway_classes and S-NET-04), EPSG:25832."""
    from pyrosm import OSM

    _, edges = OSM(str(pbf)).get_network(network_type="all", nodes=True)
    edges = _with_tag_columns(edges)
    edges = edges[select_ways(edges, rules)]
    edges = edges.rename(columns={"id": "way_id"})[["u", "v", "way_id", "highway", "name", "maxspeed", "geometry"]]
    return to_work_crs(edges.reset_index(drop=True))


def reference_length_m(pbf: Path, rules) -> float:
    """Length of the OSM source network read independently as whole ways (Prüfschritt)."""
    from pyrosm import OSM

    ways = OSM(str(pbf)).get_data_by_custom_criteria(
        custom_filter={"highway": network_highways(rules)}, filter_type="keep", osm_keys_to_keep="highway",
        keep_nodes=False, keep_relations=False)
    ways = _with_tag_columns(ways)
    ways = ways[select_ways(ways, rules)]
    ways = to_work_crs(ways[ways.geometry.geom_type.isin(["LineString", "MultiLineString"])])
    return float(ways.geometry.length.sum())


def assign_bezirk(seg: gpd.GeoDataFrame, bezirke: gpd.GeoDataFrame) -> pd.Series:
    """Name of the Bezirk with the largest share of each segment's length (None outside)."""
    pairs = gpd.sjoin(seg[["geometry"]], bezirke[["name", "geometry"]], predicate="intersects", how="inner")
    shares = shapely.length(shapely.intersection(
        seg.geometry.loc[pairs.index].values, bezirke.geometry.loc[pairs["index_right"]].values))
    pairs = pairs.assign(share=shares).reset_index(names="seg_idx")
    best = pairs.sort_values(["share", "name"], ascending=[False, True]).drop_duplicates("seg_idx")
    return best.set_index("seg_idx")["name"].reindex(seg.index)


def run_checks(seg: gpd.GeoDataFrame, reference_m: float, previous_ids: set[str] | None) -> list[dict]:
    total = float(seg["length_m"].sum())
    deviation = abs(total - reference_m) / reference_m if reference_m else float("inf")
    checks = [
        {"name": "Längensumme vs. OSM-Ausgangsnetz", "ok": deviation < MAX_LENGTH_DEVIATION,
         "detail": f"{total / 1000:.1f} km vs. {reference_m / 1000:.1f} km, Abweichung {deviation:.4%} "
                   f"(Grenze {MAX_LENGTH_DEVIATION:.0%})"},
        {"name": "Keine doppelten segment_id", "ok": bool(seg["segment_id"].is_unique),
         "detail": f"{int(seg['segment_id'].duplicated().sum())} doppelt"},
        {"name": "Geometrien gültig", "ok": bool(seg.geometry.is_valid.all()),
         "detail": f"{int((~seg.geometry.is_valid).sum())} ungültig"},
        {"name": "Länge > 0", "ok": bool((seg["length_m"] > 0).all()),
         "detail": f"{int((seg['length_m'] <= 0).sum())} mit Länge 0"},
        {"name": "CRS EPSG:25832", "ok": seg.crs == WORK_CRS, "detail": str(seg.crs)},
    ]
    if previous_ids is None:
        checks.append({"name": "IDs identisch mit Vorlauf", "ok": None, "detail": "kein Vorlauf vorhanden"})
    else:
        ids = set(seg["segment_id"])
        checks.append({"name": "IDs identisch mit Vorlauf", "ok": ids == previous_ids,
                       "detail": f"{len(ids & previous_ids)} gleich, {len(ids - previous_ids)} neu, "
                                 f"{len(previous_ids - ids)} entfallen"})
    return checks


# --- report ----------------------------------------------------------------------------------


def _txt(value) -> str:
    return "" if value is None or pd.isna(value) else str(value)


def _fmt(x: float, digits: int = 0) -> str:
    return f"{x:,.{digits}f}".replace(",", " ")


def _length_table(seg: pd.DataFrame, order: list[str]) -> list[str]:
    lines = ["| highway | Anzahl | Summe km | P10 m | Median m | P90 m | Max m |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for hw in order:
        s = seg.loc[seg["highway"] == hw, "length_m"]
        if s.empty:
            continue
        lines.append(f"| {hw} | {_fmt(len(s))} | {_fmt(s.sum() / 1000, 1)} | {_fmt(s.quantile(0.1))} | "
                     f"{_fmt(s.median())} | {_fmt(s.quantile(0.9))} | {_fmt(s.max())} |")
    s = seg["length_m"]
    lines.append(f"| **gesamt** | {_fmt(len(s))} | {_fmt(s.sum() / 1000, 1)} | {_fmt(s.quantile(0.1))} | "
                 f"{_fmt(s.median())} | {_fmt(s.quantile(0.9))} | {_fmt(s.max())} |")
    return lines


def write_report(seg: gpd.GeoDataFrame, ctx: dict, checks: list[dict]) -> None:
    rules, pilot = ctx["rules"], ctx["pilot"]
    order = network_highways(rules)
    in_pilot = seg[seg["bezirk"] == pilot]
    status = {True: "ok", False: "**FEHLER**", None: "–"}
    lines = [
        "# Netzbericht – Abschnitte (Stufe 2)", "",
        f"Erzeugt: {_now()} von `pipeline/s02_network.py`. Nicht amtlicher Entwurf.", "",
        "## Eingabe", "",
        f"- OSM-Auszug: `{ctx['pbf']['path']}` (Abruf {(ctx['pbf'].get('retrieved_at') or '–')[:10]}, "
        f"SHA-256 `{ctx['pbf_sha'][:16]}…`)",
        f"- Regelwerk: config/rules.yaml {rules.meta.version}",
        f"- highway-Klassen: {', '.join(order)}",
        "- Netz für ganz Hamburg berechnet, damit IDs am Rand des Pilotbezirks nicht vom Zuschnitt abhängen.",
        "", "## Segmentierungsregeln", "",
    ]
    for r in rules.network.rules:
        extra = "".join(f"; {k} = {_fmt(t.value)} {t.unit} ({t.source_type})" for k, t in r.thresholds.items())
        lines.append(f"- **{r.id}** ({r.source_type}, {r.status}): {r.description}{extra}")
    lines += [
        "", "segment_id = Hash aus sortierten OSM-Way-IDs und den auf 1 m gerundeten Koordinaten der beiden "
        "Endknoten (EPSG:25832). Haben zwei Abschnitte dieselben Ways und Endknoten (z. B. die Bögen eines "
        "Kreisverkehrs aus einem geschlossenen Way), gehen zusätzlich alle Knotenkoordinaten in den Hash ein.",
        "", "## Kennzahlen", "",
        f"- Kanten (Knoten zu Knoten) im Ausgangsnetz: {_fmt(ctx['n_edges'])} aus {_fmt(ctx['n_ways'])} Ways",
        f"- Abschnitte Hamburg: {_fmt(len(seg))} ({_fmt(seg['length_m'].sum() / 1000, 1)} km)",
        f"- Abschnitte {pilot}: {_fmt(len(in_pilot))} ({_fmt(in_pilot['length_m'].sum() / 1000, 1)} km)",
        f"- Abschnitte im Arbeitsgebiet ({pilot} + {ctx['buffer_m']} m): {_fmt(ctx['n_work_area'])}",
        f"- Abschnitte aus Teilung nach S-NET-03: {_fmt(int(seg['split_rule'].notna().sum()))} "
        f"(davon {pilot}: {_fmt(int(in_pilot['split_rule'].notna().sum()))})",
        f"- Abschnitte ohne Bezirk (außerhalb Hamburgs, Randstreifen des OSM-Auszugs; nur für den Netzzusammenhang): {_fmt(int(seg['bezirk'].isna().sum()))}",
        f"- Abschnitte ohne OSM-maxspeed: {_fmt(int(seg['maxspeed_osm'].isna().sum()))}; mit mehreren "
        f"maxspeed-Werten: {_fmt(int(seg['maxspeed_osm'].fillna('').str.contains(' / ').sum()))}",
        "", "## Prüfungen", "", "| Prüfung | Ergebnis | Detail |", "| --- | --- | --- |",
    ]
    lines += [f"| {c['name']} | {status[c['ok']]} | {c['detail']} |" for c in checks]
    lines += ["", f"## Längenverteilung je highway-Klasse – {pilot}", ""]
    lines += _length_table(in_pilot, order)
    lines += ["", "## Längenverteilung je highway-Klasse – Hamburg", ""]
    lines += _length_table(seg, order)
    lines += ["", "## Abschnitte je Bezirk", "", "| Bezirk | Anzahl | km |", "| --- | ---: | ---: |"]
    for name, grp in seg.groupby(seg["bezirk"].fillna("(außerhalb Hamburgs)")):
        lines.append(f"| {name} | {_fmt(len(grp))} | {_fmt(grp['length_m'].sum() / 1000, 1)} |")

    rng = random.Random(SAMPLE_SEED)
    picked = sorted(rng.sample(sorted(in_pilot["segment_id"]), min(SAMPLE_SIZE, len(in_pilot))))
    sample = in_pilot.set_index("segment_id").loc[picked]
    points = gpd.GeoSeries(sample.geometry.interpolate(0.5, normalized=True), crs=WORK_CRS).to_crs("EPSG:4326")
    lines += ["", f"## Stichprobe ({len(sample)} zufällige Abschnitte in {pilot}, Seed {SAMPLE_SEED})", "",
              "Links auf openstreetmap.org (Way und Kartenausschnitt am Abschnittsmittelpunkt). Orthophoto- und "
              "Panoramax-Links folgen, sobald das Linkformat geklärt ist (docs/open_questions.md).", "",
              "| segment_id | highway | Name | Länge m | maxspeed (OSM) | Ways | Karte |",
              "| --- | --- | --- | ---: | --- | --- | --- |"]
    for sid, row in sample.iterrows():
        ways = ", ".join(f"[{w}]({osm_way_link(w)})" for w in row["osm_way_ids"][:3])
        if len(row["osm_way_ids"]) > 3:
            ways += f" (+{len(row['osm_way_ids']) - 3})"
        lines.append(f"| `{sid}` | {row['highway']} | {_txt(row['name'])} | {_fmt(row['length_m'])} | "
                     f"{_txt(row['maxspeed_osm']) or '–'} | {ways} | [OSM]({osm_map_link(points.loc[sid])}) |")
    lines += ["", "## Lizenz", "",
              "Abgeleitet aus OpenStreetMap-Daten © OpenStreetMap-Beitragende, ODbL 1.0 (docs/licenses.md).", ""]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# --- main ------------------------------------------------------------------------------------


def main() -> int:
    rules = load_rules()
    network = rules.network
    differ_rule, split_rule = network.rule("S-NET-02"), network.rule("S-NET-03")
    with open(PROJECT_PATH, encoding="utf-8") as f:
        project = yaml.safe_load(f)["pilot_district"]
    manifest = load_manifest()
    pbf = _pbf_from_manifest(manifest)
    pbf_path = REPO_ROOT / pbf["path"]
    pbf_sha = sha256_file(pbf_path)
    if pbf.get("sha256") and pbf_sha != pbf["sha256"]:
        print(f"network: SHA-256 of {pbf['path']} does not match data/manifest.json", file=sys.stderr)
        return 1

    print(f"network: reading {pbf['path']}")
    edges = read_edges(pbf_path, rules)
    seg = segments_from_edges(edges, differ=[differ_rule.attribute], split_attribute=split_rule.attribute,
                              min_length_m=split_rule.thresholds["min_length_m"].value,
                              split_rule_id=split_rule.id)
    bezirke = to_work_crs(boundaries_from_pbf(pbf_path))
    bezirke = bezirke[bezirke["admin_level"].astype(str) == BEZIRK_ADMIN_LEVEL].reset_index(drop=True)
    seg["bezirk"] = assign_bezirk(seg, bezirke)

    district = gpd.read_parquet(REPO_ROOT / "data" / "raw" / "district_boundary.parquet")
    work_area = to_work_crs(district).geometry.union_all().buffer(project["buffer_m"])
    previous_ids = set(pd.read_parquet(OUT_PATH, columns=["segment_id"])["segment_id"]) if OUT_PATH.exists() else None
    checks = run_checks(seg, reference_length_m(pbf_path, rules), previous_ids)

    ctx = {"rules": rules, "pilot": project["name"], "buffer_m": project["buffer_m"], "pbf": pbf,
           "pbf_sha": pbf_sha, "n_edges": len(edges), "n_ways": int(edges["way_id"].nunique()),
           "n_work_area": int(seg.geometry.intersects(work_area).sum())}
    write_report(seg, ctx, checks)
    failed = [c for c in checks if c["ok"] is False and c["name"] != "IDs identisch mit Vorlauf"]
    for c in checks:
        print(f"network: {c['name']}: {c['ok']} ({c['detail']})")
    if failed:
        print(f"network: {len(failed)} check(s) failed, {OUT_PATH.name} not written; see {REPORT_PATH}",
              file=sys.stderr)
        return 1
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    seg.to_parquet(OUT_PATH, index=False)
    print(f"network: {len(seg)} segments -> {OUT_PATH.relative_to(REPO_ROOT)}, report {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
