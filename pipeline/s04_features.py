"""Stage 4: features per segment (guide 3.2 Stufe 4, prompts/06_features.md).

Usage: uv run python -m pipeline.s04_features

Reads data/interim/segments_conflated.parquet and the raw layers listed in data/manifest.json and
writes data/interim/features.parquet plus reports/features.md. Rules and parameters come from
config/rules.yaml (sections features and scores). Features are computed for segments in the work
area (conflated = true); betweenness uses the whole Hamburg network. Missing values stay null and
scores follow scores.*.missing_value_policy. The run stops with exit code 1 if a check fails;
features.parquet is then not written.
"""

import datetime as dt
import json
import sys
import time
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd

from pipeline.lib import gtfs
from pipeline.lib.area import area_label, district_names, load_area_config, read_work_area, sample_by_district
from pipeline.lib.betweenness import edge_betweenness
from pipeline.lib.conflate import MatchParams, zone_share
from pipeline.lib.crs import WORK_CRS, to_work_crs
from pipeline.lib.features import (
    FeatureParams,
    alkis_buildings,
    area_weighted_sum,
    building_density,
    count_near,
    frontage_share,
    ist_speed,
    majority,
    nearest_distance,
    parallel_route_present,
    percentile_rank,
    travel_speed_kmh,
    way_design,
    weighted_score,
)
from pipeline.lib.links import osm_map_link, osm_way_link
from pipeline.lib.manifest import REPO_ROOT, load_manifest
from pipeline.lib.rules import load_rules
from pipeline.s02_network import _pbf_from_manifest

SEGMENTS_PATH = REPO_ROOT / "data" / "interim" / "segments_conflated.parquet"
OUT_PATH = REPO_ROOT / "data" / "interim" / "features.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "features.md"
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
HIST_BINS = 10
BAR_WIDTH = 30
OSM_BBOX_MARGIN_DEG = 0.005  # read a little more OSM than the work area so edge ways are complete
WAY_WEIGHT_BUFFER_M = 1.0  # length of a way inside this buffer of the segment = its weight (S-FEAT-10)
MOTORWAY_CLASSES = {"motorway", "motorway_link"}

DESIGN_COLUMNS = ["separated_cycle_track_present", "cycle_lane_present", "lanes", "centre_line", "surface",
                  "parking", "parking_on_carriageway", "parking_along_carriageway", "angle_parking"]

# Feature -> (data source, rule, where rules.yaml uses it). Every output column is listed here.
FEATURE_DOC = {
    "betweenness": ("OSM-Netz + Tempo", "S-FEAT-02", "Rohwert für betweenness_norm"),
    "betweenness_norm": ("OSM-Netz + Tempo", "S-FEAT-01/02", "scores.conn_score"),
    "in_hvs": ("DTV-Linien HVS 2019", "S-CONF-04", "C-GOW-01, scores.conn_score"),
    "bus_trips_weekday": ("GTFS HVV", "S-FEAT-08", "Rohwert für bus_trips_weekday_norm"),
    "bus_trips_weekday_norm": ("GTFS HVV", "S-FEAT-01/08", "scores.conn_score"),
    "dtv_official": ("DTV-Linien HVS 2019", "S-CONF-01", "discrepancy.use, Rohwert für dtv_norm"),
    "dtv_norm": ("DTV-Linien HVS 2019", "S-FEAT-01", "scores.conn_score"),
    "conn_score": ("abgeleitet", "scores.conn_score", "C-RUR-01, C-GOW-01"),
    "conn_weight_available": ("abgeleitet", "scores.conn_score", "missing_value_policy (confidence, Prompt 08)"),
    "building_density": ("ALKIS-Gebäude", "S-FEAT-03", "Rohwert für building_density_norm"),
    "building_density_norm": ("ALKIS-Gebäude", "S-FEAT-01/03", "scores.place_score"),
    "population_100m": ("Zensus 2022 Gitter", "S-FEAT-04", "priority.risk_weights, Rohwert"),
    "population_100m_norm": ("Zensus 2022 Gitter", "S-FEAT-01/04", "scores.place_score"),
    "shop_frontage_share": ("ALKIS-Gebäudefunktion + OSM shop/amenity", "S-FEAT-05", "C-G30-01, scores.place_score (frontage_share)"),
    "frontage_buildings": ("ALKIS-Gebäude", "S-FEAT-05", "Nenner von shop_frontage_share (Nachvollziehbarkeit)"),
    "schools_or_kitas_within_m": ("OSM Schulen/Kitas", "S-FEAT-06", "C-G30-01, priority.school_kita_within_150m"),
    "sensitive_facilities_norm": ("OSM Schulen/Kitas", "S-FEAT-01/06", "scores.place_score"),
    "place_score": ("abgeleitet", "scores.place_score", "Prompt 08/10 (Funktionskonflikt, Diskrepanz)"),
    "place_weight_available": ("abgeleitet", "scores.place_score", "missing_value_policy"),
    "in_cycle_network": ("OSM Radnetz Hamburg", "S-FEAT-07", "priority.risk_weights.cycle_network, ETW30-Ausnahme"),
    "speed_ist_kmh": ("Tempo amtlich/OSM", "S-FEAT-09", "discrepancy.speed"),
    "speed_ist_source": ("Tempo amtlich/OSM", "S-FEAT-09", "Herkunft von speed_ist_kmh"),
    "speed_sources_conflict": ("Tempo amtlich/OSM", "S-FEAT-09", "Unsicherheit (confidence)"),
    "travel_speed_kmh": ("Tempo amtlich/OSM/Standard", "S-FEAT-02", "Gewicht der Betweenness"),
    "travel_speed_source": ("Tempo amtlich/OSM/Standard", "S-FEAT-02", "Herkunft von travel_speed_kmh"),
    "separated_cycle_track_present": ("OSM-Tags", "S-FEAT-10", "C-G30-02, requirements.*.cycling"),
    "parallel_cycle_route_present": ("OSM-Radwege + amtliches Radnetz (Bestand)", "S-FEAT-11", "D-DES-01 (GOW50: Radweg oder Parallelroute)"),
    "cycle_lane_present": ("OSM-Tags", "S-FEAT-10", "requirements.*.cycle_lanes_allowed"),
    "lanes": ("OSM-Tags", "S-FEAT-10", "requirements.GOW50.median_if_lanes_per_dir_gte"),
    "centre_line": ("OSM-Tags", "S-FEAT-10", "requirements.GOW30.centre_line"),
    "parking": ("OSM-Tags", "S-FEAT-10", "Rohwert der Parkmerkmale"),
    "parking_on_carriageway": ("OSM-Tags", "S-FEAT-10", "requirements.GOW30.parking_on_carriageway"),
    "parking_along_carriageway": ("OSM-Tags", "S-FEAT-10", "requirements.GOW50.parking_along_carriageway"),
    "angle_parking": ("OSM-Tags", "S-FEAT-10", "requirements.GOW50.angle_parking"),
    "crossings_count": ("OSM-Knoten", "S-FEAT-10", "requirements.GOW50.crossings"),
    "traffic_calming_count": ("OSM-Knoten", "S-FEAT-10", "requirements.ETW30.speed_reducer_spacing_m"),
    "surface": ("OSM-Tags", "S-FEAT-10", "Erkennbarkeit (guide.md 1.2)"),
    "access_motor_only": ("OSM-Tags", "S-FEAT-10", "C-SW-01"),
    "pedestrian_zone": ("OSM-Tags", "S-FEAT-10", "C-ERF-01"),
    "outside_builtup_area": ("keine Quelle", "–", "C-RUR-01"),
    "crossing_demand": ("nicht definiert", "–", "C-G30-01"),
    "override_school_street": ("overrides.csv (Prompt 09)", "–", "C-ERF-01"),
    "width_p10_m": ("Querschnitt (Prompt 07)", "–", "C-G30-02"),
}
# Raw inputs per data source for the null table; status comes from the manifest.
SOURCE_OF = {"Zensus 2022 Gitter": "population_grid", "ALKIS-Gebäude": "alkis", "GTFS HVV": "gtfs_hvv", "OSM Schulen/Kitas": "schools",
             "OSM Radnetz Hamburg": "cycle_network", "DTV-Linien HVS 2019": "traffic_volumes",
             "Tempo amtlich/OSM": "speed_limits"}
NULL_REASON = {
    "outside_builtup_area": "keine Datenquelle für die Ortsgrenze (docs/open_questions.md)",
    "crossing_demand": "in rules.yaml nicht definiert (docs/open_questions.md)",
    "override_school_street": "kommt aus overrides/overrides.csv (Prompt 09)",
    "width_p10_m": "kommt aus dem Querschnitt (Prompt 07)",
}


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def _none(v):
    if v is None:
        return None
    try:
        return None if pd.isna(v) else v
    except (TypeError, ValueError):
        return v


def _round(v, digits: int = 3):
    v = _none(v)
    return None if v is None else round(float(v), digits)


# --- inputs ----------------------------------------------------------------------------------


def _layer(manifest: dict, source: str, layer: str | None = None) -> gpd.GeoDataFrame | None:
    files = (manifest["sources"].get(source) or {}).get("files") or []
    paths = [REPO_ROOT / f["path"] for f in files if str(f.get("path", "")).endswith(".parquet")
             and (layer is None or f.get("layer") == layer)]
    if not paths or not all(p.exists() for p in paths):
        return None
    return to_work_crs(pd.concat([gpd.read_parquet(p) for p in paths], ignore_index=True))


def _gtfs_path(manifest: dict):
    files = (manifest["sources"].get("gtfs_hvv") or {}).get("files") or []
    paths = [REPO_ROOT / f["path"] for f in files if (REPO_ROOT / f["path"]).exists()]
    return paths[0] if paths else None


def read_osm(pbf, work_area_wgs84) -> dict[str, gpd.GeoDataFrame]:
    """Ways with tags, shop/amenity POIs, crossing and traffic_calming nodes in the work area."""
    from pyrosm import OSM

    osm = OSM(str(pbf), bounding_box=work_area_wgs84.buffer(OSM_BBOX_MARGIN_DEG))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ways = osm.get_network(network_type="all")
        pois = osm.get_pois(custom_filter={"shop": True, "amenity": True})
        node_kw = dict(filter_type="keep", keep_nodes=True, keep_ways=False, keep_relations=False)
        crossings = osm.get_data_by_custom_criteria(custom_filter={"highway": ["crossing"]}, **node_kw)
        calming = osm.get_data_by_custom_criteria(custom_filter={"traffic_calming": True}, **node_kw)
    out = {"ways": ways, "pois": pois, "crossings": crossings, "calming": calming}
    return {k: to_work_crs(v.reset_index(drop=True)) for k, v in out.items()}


OFFICIAL_CYCLE_NETWORK_PATH = REPO_ROOT / "data" / "raw" / "cycle_network_official__radnetz.parquet"


def cycle_route_lines(ways: gpd.GeoDataFrame, rule) -> gpd.GeoSeries:
    """S-FEAT-11: OSM cycleways and paths with bicycle access, plus the official cycle network with official_status."""
    hw = ways["highway"].astype(str)
    bicycle = ways["bicycle"].astype(str) if "bicycle" in ways else pd.Series("", index=ways.index)
    keep = (hw == "cycleway") | (hw.isin(rule.path_highways) & bicycle.isin(rule.bicycle_allowed))
    parts = [ways.geometry[keep]]
    if OFFICIAL_CYCLE_NETWORK_PATH.exists():
        off = to_work_crs(gpd.read_parquet(OFFICIAL_CYCLE_NETWORK_PATH))
        parts.append(off.geometry[off["status"].isin(rule.official_status)])
    lines = pd.concat(parts, ignore_index=True)
    return gpd.GeoSeries(lines, crs=ways.crs).explode(index_parts=False).reset_index(drop=True)


def _way_tags(row) -> dict:
    tags = json.loads(row["tags"]) if isinstance(row.get("tags"), str) else {}
    for col, val in row.items():
        if col not in ("tags", "geometry") and isinstance(val, str):
            tags.setdefault(col, val)
    return tags


# --- features --------------------------------------------------------------------------------


def betweenness_features(seg: gpd.GeoDataFrame, params: FeatureParams) -> tuple[pd.DataFrame, float]:
    """S-FEAT-02 on all segments; returns columns and the runtime in seconds."""
    speeds = [travel_speed_kmh(o, m, h, params.default_speed_kmh)
              for o, m, h in zip(seg["speed_official_kmh"], seg["maxspeed_osm"], seg["highway"])]
    speed = pd.Series([s for s, _ in speeds], index=seg.index, dtype="float64")
    source = pd.Series([src for _, src in speeds], index=seg.index, dtype="object")
    routed = ~seg["highway"].isin(params.exclude_highway) & speed.notna()
    seconds = (seg["length_m"] / (speed / 3.6)).where(routed)
    t0 = time.perf_counter()
    b = edge_betweenness(seg["node_u"].to_numpy(), seg["node_v"].to_numpy(), seconds.to_numpy())
    runtime = time.perf_counter() - t0
    return pd.DataFrame({"travel_speed_kmh": speed, "travel_speed_source": source, "betweenness": b},
                        index=seg.index), runtime


def design_features(area: gpd.GeoDataFrame, ways: gpd.GeoDataFrame) -> pd.DataFrame:
    """S-FEAT-10: majority of each design attribute over the segment's ways, weighted by length inside."""
    ways = ways.drop_duplicates("id").set_index("id")
    pairs = area[["segment_id", "osm_way_ids", "geometry"]].explode("osm_way_ids").rename(columns={"osm_way_ids": "way_id"})
    pairs = pairs[pairs["way_id"].isin(ways.index)]
    way_geom = gpd.GeoSeries(ways.loc[pairs["way_id"], "geometry"].to_numpy(), crs=WORK_CRS)
    seg_buf = gpd.GeoSeries(pairs.geometry.to_numpy(), crs=WORK_CRS).buffer(WAY_WEIGHT_BUFFER_M)
    pairs["weight"] = way_geom.intersection(seg_buf).length.to_numpy()
    design = {wid: way_design(_way_tags(row)) for wid, row in ways.loc[pairs["way_id"].unique()].iterrows()}
    rows = {}
    for sid, grp in pairs.groupby("segment_id", sort=False):
        values = [design[w] for w in grp["way_id"]]
        weights = grp["weight"].tolist()
        rows[sid] = {c: majority([v[c] for v in values], weights) for c in DESIGN_COLUMNS}
        rows[sid]["motorroad"] = any(v["motorroad"] for v in values)
    out = pd.DataFrame.from_dict(rows, orient="index").reindex(area["segment_id"])
    out.index = area.index
    return out


def bus_features(area: gpd.GeoDataFrame, feed_path, params: FeatureParams, mp: MatchParams,
                 min_share: float) -> tuple[pd.Series, dict]:
    """S-FEAT-08; all null while no GTFS feed is in data/raw."""
    if feed_path is None:
        return pd.Series(np.nan, index=area.index), {"status": "fehlt"}
    feed = gtfs.load_feed(feed_path)
    day = gtfs.representative_weekday(feed)
    trips, without_shape = gtfs.trips_per_shape(feed, day, params.bus_route_types)
    shapes = gtfs.shapes_gdf(feed, trips.index)
    shapes = shapes[shapes.intersects(area.geometry.union_all().buffer(mp.buffer_m))]
    total = pd.Series(0.0, index=area.index)
    for shape_id, geom in shapes.geometry.items():
        share = zone_share(area.geometry, gpd.GeoSeries([geom], crs=WORK_CRS), mp)
        total[share >= min_share] += trips[shape_id]
    return total, {"status": "ok", "day": day.isoformat(), "trips_without_shape": without_shape,
                   "shapes": len(shapes)}


def compute(seg: gpd.GeoDataFrame, layers: dict, osm: dict, feed_path, rules) -> tuple[gpd.GeoDataFrame, dict]:
    params = FeatureParams.from_rules(rules)
    mp = MatchParams.from_rules(rules)
    min_share = rules.conflation.rule("S-CONF-02").thresholds["min_length_share"].value
    info: dict = {}
    out = seg.copy()

    bt, info["betweenness_runtime_s"] = betweenness_features(seg, params)
    out = out.join(bt)

    in_area = out["conflated"].astype(bool)
    area = out[in_area]
    g = area.geometry

    speeds = [ist_speed(o, m) for o, m in zip(area["speed_official_kmh"], area["maxspeed_osm"])]
    out.loc[in_area, "speed_ist_kmh"] = [s for s, _, _ in speeds]
    out.loc[in_area, "speed_ist_source"] = [s for _, s, _ in speeds]
    out.loc[in_area, "speed_sources_conflict"] = [c for _, _, c in speeds]

    buildings = alkis_buildings(layers["alkis_buildings"], params)
    info["alkis_buildings"] = len(buildings)
    out.loc[in_area, "building_density"] = building_density(g, buildings.geometry, params.building_buffer_m)
    share, n_total, n_public = frontage_share(g, buildings, osm["pois"], params.frontage_buffer_m,
                                              params.amenity_excluded)
    out.loc[in_area, "shop_frontage_share"] = share
    out.loc[in_area, "frontage_buildings"] = n_total
    out.loc[in_area, "frontage_public"] = n_public
    grid = layers.get("population_grid")
    if grid is not None:
        out.loc[in_area, "population_100m"] = area_weighted_sum(g, grid, "population", params.population_buffer_m)
    else:
        out["population_100m"] = np.nan

    facilities = pd.concat([layers[k] for k in ("schools", "kitas") if layers.get(k) is not None], ignore_index=True)
    out.loc[in_area, "schools_or_kitas_within_m"] = nearest_distance(g, facilities.geometry) if len(facilities) \
        else np.nan

    cyc = layers.get("cycle_network")
    if cyc is not None and len(cyc):
        out.loc[in_area, "in_cycle_network"] = zone_share(g, cyc.geometry.explode(index_parts=False)
                                                          .reset_index(drop=True), mp) >= min_share
    out.loc[in_area, "bus_trips_weekday"], info["gtfs"] = bus_features(area, feed_path, params, mp, min_share)

    out.loc[in_area, "crossings_count"] = count_near(g, osm["crossings"].geometry, params.node_snap_m)
    out.loc[in_area, "traffic_calming_count"] = count_near(g, osm["calming"].geometry, params.node_snap_m)
    design = design_features(area, osm["ways"])
    for c in DESIGN_COLUMNS:
        out.loc[in_area, c] = design[c]
    out.loc[in_area, "access_motor_only"] = area["highway"].isin(MOTORWAY_CLASSES) | design["motorroad"].fillna(False)
    f11 = rules.features.rule("S-FEAT-11")
    mp11 = MatchParams(buffer_m=f11.thresholds["buffer_m"].value, max_angle_deg=mp.max_angle_deg,
                       min_overlap_share=mp.min_overlap_share)
    routes = cycle_route_lines(osm["ways"], f11)
    out.loc[in_area, "parallel_cycle_route_present"] = parallel_route_present(g, routes, mp11, min_share).to_numpy()
    info["parallel_route_lines"] = len(routes)
    out.loc[in_area, "pedestrian_zone"] = area["highway"] == "pedestrian"
    for c in NULL_REASON:
        out[c] = None

    # S-FEAT-01 normalisation over the work area
    out["betweenness_norm"] = percentile_rank(out["betweenness"], in_area, ties=params.ties)
    out["bus_trips_weekday_norm"] = percentile_rank(out["bus_trips_weekday"], in_area, ties=params.ties)
    out["dtv_norm"] = percentile_rank(out["dtv_official"], in_area, ties=params.ties)
    out["building_density_norm"] = percentile_rank(out["building_density"], in_area, ties=params.ties)
    out["population_100m_norm"] = percentile_rank(out["population_100m"], in_area, ties=params.ties)
    out["sensitive_facilities_norm"] = percentile_rank(-out["schools_or_kitas_within_m"], in_area, ties=params.ties)
    norms = pd.DataFrame({
        "betweenness_norm": out["betweenness_norm"],
        "in_hvs": out["in_hvs"].astype("float64").where(in_area),
        "bus_trips_weekday_norm": out["bus_trips_weekday_norm"],
        "dtv_norm": out["dtv_norm"],
        "building_density_norm": out["building_density_norm"],
        "population_100m_norm": out["population_100m_norm"],
        "frontage_share": out["shop_frontage_share"].where(in_area),
        "sensitive_facilities_norm": out["sensitive_facilities_norm"],
    })
    for score, prefix in (("conn_score", "conn"), ("place_score", "place")):
        s, avail = weighted_score(norms, rules.scores[score].weights)
        out[score] = s.where(in_area)
        out[f"{prefix}_weight_available"] = avail.where(in_area)

    out = _typed(out)
    out["feature_trace"] = [_trace(r, rules) if r["conflated"] else None for _, r in out.iterrows()]
    return out, info


def _typed(out: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    for c in ("speed_ist_kmh", "lanes", "crossings_count", "traffic_calming_count", "frontage_buildings",
              "frontage_public"):
        out[c] = pd.array([None if _none(v) is None else int(v) for v in out[c]], dtype="Int64")
    for c in ("speed_sources_conflict", "in_cycle_network", "separated_cycle_track_present", "parallel_cycle_route_present", "cycle_lane_present",
              "centre_line", "parking_on_carriageway", "parking_along_carriageway", "angle_parking",
              "access_motor_only", "pedestrian_zone"):
        if c not in out:
            out[c] = None
        out[c] = pd.array([None if _none(v) is None else bool(v) for v in out[c]], dtype="boolean")
    for c in ("speed_ist_source", "surface", "parking", "travel_speed_source", *NULL_REASON):
        out[c] = out[c].astype("object").where(out[c].notna(), None)
    for c in ("building_density", "shop_frontage_share", "schools_or_kitas_within_m", "bus_trips_weekday",
              "population_100m"):
        out[c] = pd.to_numeric(out[c], errors="coerce").astype("float64")
    return out


def _trace(r, rules) -> str:
    trace = [
        {"id": "S-FEAT-02", "inputs": {"travel_speed_kmh": _round(r["travel_speed_kmh"], 0),
                                        "speed_source": _none(r["travel_speed_source"]),
                                        "betweenness": _round(r["betweenness"], 1)}},
        {"id": "S-FEAT-03", "inputs": {"building_density": _round(r["building_density"])}},
        {"id": "S-FEAT-05", "inputs": {"buildings": _none(r["frontage_buildings"]),
                                        "public": _none(r["frontage_public"])}},
        {"id": "S-FEAT-06", "inputs": {"distance_m": _round(r["schools_or_kitas_within_m"], 1)}},
        {"id": "S-FEAT-09", "inputs": {"official_kmh": _none(r["speed_official_kmh"]),
                                        "osm": _none(r["maxspeed_osm"]), "result": _none(r["speed_ist_kmh"])}},
    ]
    for score in ("conn_score", "place_score"):
        used = {k: w for k, w in rules.scores[score].weights.items()}
        trace.append({"id": f"scores.{score}", "inputs": {"weights": used,
                                                          "weight_available": _round(r[f"{score[:-6]}_weight_available"]),
                                                          "result": _round(r[score])}})
    return json.dumps(trace, ensure_ascii=False, default=lambda v: v.item() if hasattr(v, "item") else str(v))


# --- checks and report -----------------------------------------------------------------------


def run_checks(seg: gpd.GeoDataFrame, out: gpd.GeoDataFrame, params: FeatureParams) -> list[dict]:
    in_area = out["conflated"].astype(bool)
    checks = [{"name": "segment_id unverändert", "ok": list(out["segment_id"]) == list(seg["segment_id"]),
               "detail": f"{len(out)} Abschnitte"}]
    bad = []
    for c in ["betweenness_norm", "bus_trips_weekday_norm", "dtv_norm", "building_density_norm",
              "population_100m_norm", "sensitive_facilities_norm", "shop_frontage_share", "conn_score", "place_score"]:
        v = out[c].dropna()
        if not ((v >= 0) & (v <= 1)).all():
            bad.append(c)
    checks.append({"name": "Normwerte und Scores in [0, 1]", "ok": not bad, "detail": ", ".join(bad) or "alle"})
    missing = int(out.loc[in_area, "conn_score"].isna().sum())
    checks.append({"name": "conn_score im Arbeitsgebiet vollständig", "ok": missing == 0,
                   "detail": f"{missing} ohne conn_score"})
    routed = ~out["highway"].isin(params.exclude_highway)
    nb = int(out.loc[routed, "betweenness"].isna().sum())
    checks.append({"name": "Betweenness für alle Kfz-Abschnitte", "ok": nb == 0, "detail": f"{nb} ohne Wert"})
    return checks


def _fmt(x: float, digits: int = 0) -> str:
    return f"{x:,.{digits}f}".replace(",", " ")


def _pct(x: float) -> str:
    return f"{100 * x:.1f} %"


def text_histogram(values: pd.Series, bins: int = HIST_BINS) -> list[str]:
    v = pd.to_numeric(values, errors="coerce").dropna().astype("float64")
    if v.empty:
        return ["_keine Werte_"]
    if v.nunique() == 1:
        return [f"alle {len(v)} Werte = {v.iloc[0]:.3g}"]
    counts, edges = np.histogram(v, bins=bins)
    peak = counts.max()
    lines = ["| von | bis | Anzahl | |", "| ---: | ---: | ---: | --- |"]
    for c, a, b in zip(counts, edges[:-1], edges[1:]):
        lines.append(f"| {a:.3g} | {b:.3g} | {c} | {'█' * int(round(BAR_WIDTH * c / peak))} |")
    return lines


def _source_status(manifest: dict, source: str) -> str:
    return (manifest["sources"].get(source) or {}).get("status", "–")


def write_report(out: gpd.GeoDataFrame, ctx: dict, checks: list[dict]) -> None:
    rules, params = ctx["rules"], ctx["params"]
    area = out[out["conflated"].astype(bool)]
    pilot = area[area["bezirk"].isin(ctx["districts"])]
    gt = ctx["info"]["gtfs"]
    lines = [
        "# Merkmalsbericht – Stufe 4", "",
        f"Erzeugt: {_now()} von `pipeline/s04_features.py`, rules.yaml {rules.meta.version}. Nicht amtlicher Entwurf.", "",
        "## Kennzahlen", "",
        f"- Abschnitte gesamt (OSM-Auszug): {_fmt(len(out))}; im Arbeitsgebiet ({ctx['pilot']} + {ctx['buffer_m']:.0f} m): "
        f"{_fmt(len(area))}; davon mit Bezirk: {_fmt(len(pilot))}",
        "- Normierung (S-FEAT-01): Perzentilrang über das ganze Arbeitsgebiet, also über ganz Hamburg "
        "(Entscheidung 2026-11-04), damit derselbe Abschnitt in jedem Bezirk gleich bewertet wird.",
        f"- Betweenness: exakt (keine Stichprobe), ungerichtet, {_fmt(int(out['betweenness'].notna().sum()))} "
        f"Kfz-Abschnitte ganz Hamburgs, Laufzeit {ctx['info']['betweenness_runtime_s']:.0f} s",
        f"- Reisezeit-Tempo im Arbeitsgebiet: " + ", ".join(
            f"{k} {_pct(v)}" for k, v in area["travel_speed_source"].fillna("keins").value_counts(normalize=True).items()),
        f"- Ist-Tempo: amtlich {_pct((area['speed_ist_source'] == 'official').mean())}, "
        f"OSM {_pct((area['speed_ist_source'] == 'osm').mean())}, unbekannt {_pct(area['speed_ist_kmh'].isna().mean())}; "
        f"Konflikt amtlich ≠ OSM: {int(area['speed_sources_conflict'].fillna(False).sum())} Abschnitte",
        f"- GTFS: {'repräsentativer Werktag ' + gt['day'] + ', ' + str(gt['shapes']) + ' shapes, ' + str(gt['trips_without_shape']) + ' Fahrten ohne shape' if gt['status'] == 'ok' else 'Datensatz fehlt in data/raw – bus_trips_weekday ist null'}",
        ("- Zensus-Gitter 100 m: " + (f"{ctx['n_grid_cells']} Zellen im Arbeitsgebiet, Einwohner im "
                                      f"{params.population_buffer_m:.0f}-m-Puffer flächenanteilig; Zellen ohne Einwohner "
                                      "fehlen in der Datei und zählen 0; Werte durch Geheimhaltung leicht verändert"
                                      if ctx["n_grid_cells"] else "fehlt in data/raw – population_100m ist null")),
        f"- ALKIS-Gebäude: {_fmt(ctx['info']['alkis_buildings'])} oberirdische Gebäude im Arbeitsgebiet "
        "(WFS_HH_ALKIS_vereinfacht, seit rules.yaml 0.6.0 statt OSM)",
        "",
        "## Prüfungen", "", "| Prüfung | Ergebnis | Detail |", "| --- | --- | --- |",
        *[f"| {c['name']} | {'ok' if c['ok'] else 'FEHLER'} | {c['detail']} |" for c in checks],
        "",
        "## Methode", "",
        "- **Normierung (S-FEAT-01):** Perzentilrang über alle Abschnitte im Arbeitsgebiet mit bekanntem Wert, "
        "(Rang − 1) / (n − 1); gleiche Werte erhalten den kleinsten Rang ihrer Gruppe (rules.yaml 0.5.0), damit der "
        "kleinste Wert – z. B. 0 Busfahrten – auf 0 fällt. 1 = größter Wert. `in_hvs` geht als 0/1 "
        "ein, `shop_frontage_share` unverändert. `sensitive_facilities_norm` ist der Perzentilrang der negativen "
        "Entfernung (nah = hoch). Die Normierung hängt vom Arbeitsgebiet ab; bei Ausweitung auf ganz Hamburg ändern "
        "sich die Werte.",
        "- **Fehlende Werte:** bleiben null. conn_score und place_score legen das Gewicht fehlender Merkmale "
        "anteilig auf die übrigen um (missing_value_policy); `conn_weight_available`/`place_weight_available` "
        "zeigen, welcher Gewichtsanteil Werte hatte. Die Herabstufung der confidence folgt in Prompt 08.",
        f"- **Betweenness (S-FEAT-02):** Reisezeit = Länge / Tempo (amtlich → OSM maxspeed → Standardwert je Klasse). "
        f"Ohne {', '.join(params.exclude_highway)}. Mehrere OSM-Werte je Abschnitt (z. B. „50 / 30“) gelten als unbekannt.",
        f"- **Gebäudedichte (S-FEAT-03):** Grundfläche der oberirdischen ALKIS-Gebäude (gebnutzbez Gebaeude) im "
        f"{params.building_buffer_m:.0f}-m-Puffer / Pufferfläche.",
        f"- **Publikumsnutzung (S-FEAT-05):** Anteil der ALKIS-Gebäude im {params.frontage_buffer_m:.0f}-m-Puffer mit "
        f"Publikumsnutzung: Gebäudefunktion aus der Liste in rules.yaml ({len(params.alkis_public_functions)} Werte) "
        "oder OSM-shop/amenity-Punkt im Gebäude (ohne Stadtmöblierung). Nebengebäude "
        f"({len(params.alkis_ancillary_functions)} Funktionen, z. B. Garage, Gartenhaus) zählen nicht. Schulen und Kitas "
        "gehen über S-FEAT-06 ein, nicht hier. Das Geschoss wird nicht geprüft.",
        "- **Radnetz, Busfahrten (S-FEAT-07/08):** Längenanteil wie S-CONF-02 (Puffer, Winkel, Mindestanteil).",
        f"- **Ist-Gestaltung (S-FEAT-10):** Mehrheitswert über die Ways des Abschnitts (Gewicht: Länge im "
        f"{WAY_WEIGHT_BUFFER_M:.0f}-m-Puffer). Kein Tag = unbekannt (null), nicht „nein“. Querungen und "
        f"Verkehrsberuhigung: OSM-Knoten höchstens {params.node_snap_m:.0f} m vom Abschnitt. `access_motor_only`: "
        "motorway/motorway_link oder motorroad=yes (sonst nein, weil motorroad nur positiv erfasst wird).",
        "",
        "## Nullwertanteil je Merkmal (Arbeitsgebiet)", "",
        "| Merkmal | Quelle | Regel | benötigt von | null Arbeitsgebiet | null mit Bezirk |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for col, (src, rule, used) in FEATURE_DOC.items():
        reason = f" ({NULL_REASON[col]})" if col in NULL_REASON else ""
        lines.append(f"| `{col}` | {src} | {rule} | {used}{reason} | {_pct(area[col].isna().mean())} | "
                     f"{_pct(pilot[col].isna().mean())} |")
    lines += ["", "## Kennzahlen je Bezirk", "",
              "| Bezirk | Abschnitte | km | conn_score (Median) | place_score (Median) | Ist-Tempo null | "
              "Gebäudedichte null | lanes (OSM) null |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for bz, grp in sorted(pilot.groupby("bezirk")) + [("**gesamt**", pilot)]:
        lines.append(f"| {bz} | {_fmt(len(grp))} | {_fmt(grp['length_m'].sum() / 1000, 1)} | "
                     f"{grp['conn_score'].median():.2f} | {grp['place_score'].median():.2f} | "
                     f"{_pct(grp['speed_ist_kmh'].isna().mean())} | {_pct(grp['building_density'].isna().mean())} | "
                     f"{_pct(grp['lanes'].isna().mean())} |")
    lines += ["", "## Nullwertanteil je Datenquelle", "",
              "| Quelle | Status (manifest) | Merkmale | mittlerer Nullanteil |", "| --- | --- | --- | ---: |"]
    by_src: dict[str, list[str]] = {}
    for col, (src, _, _) in FEATURE_DOC.items():
        by_src.setdefault(src, []).append(col)
    for src, cols in by_src.items():
        status = _source_status(ctx["manifest"], SOURCE_OF[src]) if src in SOURCE_OF else "–"
        lines.append(f"| {src} | {status} | {', '.join(f'`{c}`' for c in cols)} | "
                     f"{_pct(float(np.mean([area[c].isna().mean() for c in cols])))} |")

    lines += ["", "## Verteilungen (Arbeitsgebiet)", ""]
    for col in ["betweenness", "betweenness_norm", "dtv_official", "building_density", "shop_frontage_share",
                "schools_or_kitas_within_m", "speed_ist_kmh", "lanes", "crossings_count", "conn_score", "place_score",
                "conn_weight_available"]:
        lines += [f"### `{col}`", "", *text_histogram(area[col]), ""]
    lines += ["### Kategoriale Merkmale", "", "| Merkmal | Werte (Anteil der Abschnitte) |", "| --- | --- |"]
    for col in ["in_hvs", "in_cycle_network", "separated_cycle_track_present", "cycle_lane_present", "centre_line",
                "parking_on_carriageway", "parking_along_carriageway", "angle_parking", "surface",
                "access_motor_only", "pedestrian_zone", "speed_sources_conflict"]:
        vc = area[col].astype("object").where(area[col].notna(), "null").value_counts(normalize=True).head(8)
        lines.append(f"| `{col}` | {', '.join(f'{k}: {_pct(v)}' for k, v in vc.items())} |")
    lines += ["", "### conn_score nach highway-Klasse (Median)", "", "| highway | Abschnitte | conn_score | place_score |",
              "| --- | ---: | ---: | ---: |"]
    for hw, grp in area.groupby("highway"):
        lines.append(f"| {hw} | {len(grp)} | {grp['conn_score'].median():.2f} | {grp['place_score'].median():.2f} |")

    lines += ["", f"## Stichprobe ({len(ctx['sample'])} zufällige Abschnitte in {ctx['pilot']}, nach Bezirk geschichtet, Seed {SAMPLE_SEED})", "",
              "Links auf OSM-Karte und OSM-Way. Orthophoto- und Panoramax-Links folgen, sobald das Linkformat geklärt ist "
              "(docs/open_questions.md).", "",
              "| segment_id | Bezirk | Name | highway | conn | place | betw. | HVS | Tempo | Radweg | Front. | Schule/Kita m | Karte | Way |",
              "| --- | --- | --- | --- | ---: | ---: | ---: | --- | ---: | --- | ---: | ---: | --- | --- |"]
    for _, r in ctx["sample"].iterrows():
        pt = gpd.GeoSeries([r.geometry.interpolate(0.5, normalized=True)], crs=WORK_CRS).to_crs(4326).iloc[0]

        def f(v, d=2):
            return "–" if _none(v) is None else f"{float(v):.{d}f}"

        def b(v):
            return "–" if _none(v) is None else ("ja" if v else "nein")

        lines.append(f"| `{r['segment_id']}` | {r['bezirk']} | {_none(r['name']) or '–'} | {r['highway']} | {f(r['conn_score'])} | "
                     f"{f(r['place_score'])} | {f(r['betweenness_norm'])} | {b(r['in_hvs'])} | "
                     f"{f(r['speed_ist_kmh'], 0)} | {b(r['separated_cycle_track_present'])} | "
                     f"{f(r['shop_frontage_share'])} | {f(r['schools_or_kitas_within_m'], 0)} | "
                     f"[Karte]({osm_map_link(pt)}) | [Way]({osm_way_link(r['osm_way_ids'][0])}) |")
    lines += ["", "## Lizenz", "",
              "Abschnitte, POIs, Schulen, Kitas und Radnetz aus OpenStreetMap © OpenStreetMap-Beitragende, "
              "ODbL 1.0; abgeleitete Merkmale stehen ebenfalls unter ODbL. Gebäude: Freie und Hansestadt Hamburg, "
              "Landesbetrieb Geoinformation und Vermessung (LGV), dl-de/by-2.0. Busfahrten: Hamburger Verkehrsverbund GmbH, "
              "dl-de/by-2.0. Einwohner: © Statistische Ämter des Bundes und der Länder, Zensus 2022, dl-de/by-2.0. "
              "Amtliche Attribute: Freie und Hansestadt Hamburg (Höchstgeschwindigkeiten und Verkehrsmengen: Lizenz in "
              "der API nicht angegeben, siehe docs/open_questions.md).", ""]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# --- main ------------------------------------------------------------------------------------


def main() -> int:
    rules = load_rules()
    params = FeatureParams.from_rules(rules)
    cfg = load_area_config()
    if not SEGMENTS_PATH.exists():
        print("features: data/interim/segments_conflated.parquet missing; run `make conflate` first", file=sys.stderr)
        return 1
    manifest = load_manifest()
    try:
        pbf = _pbf_from_manifest(manifest)
    except FileNotFoundError as e:
        print(f"features: {e}", file=sys.stderr)
        return 1

    seg = gpd.read_parquet(SEGMENTS_PATH)
    work_area = read_work_area(cfg)
    names = district_names()
    work_area_wgs84 = gpd.GeoSeries([work_area], crs=WORK_CRS).to_crs(4326).iloc[0]
    layers = {k: _layer(manifest, k) for k in ("schools", "kitas", "cycle_network", "population_grid")}
    layers["alkis_buildings"] = _layer(manifest, "alkis", "ave:GebaeudeBauwerk")
    if layers["alkis_buildings"] is None:
        print("features: ALKIS buildings (ave:GebaeudeBauwerk) missing in data/raw; run `make fetch` first",
              file=sys.stderr)
        return 1
    print("features: reading OSM extract")
    osm = read_osm(REPO_ROOT / pbf["path"], work_area_wgs84)
    print(f"features: {len(osm['ways'])} ways, {len(layers['alkis_buildings'])} ALKIS objects, {len(osm['pois'])} POIs")

    out, info = compute(seg, layers, osm, _gtfs_path(manifest), rules)
    checks = run_checks(seg, out, params)
    present = set(layers["alkis_buildings"]["funktion"].dropna())
    unknown = sorted((params.alkis_public_functions | params.alkis_ancillary_functions) - present)
    checks.append({"name": "Gebäudefunktionen aus rules.yaml kommen in ALKIS vor", "ok": not unknown,
                   "detail": ", ".join(unknown) or "alle"})
    pilot = out[out["bezirk"].isin(names) & out["conflated"].astype(bool)]
    sample = sample_by_district(pilot, SAMPLE_SIZE, SAMPLE_SEED)
    ctx = {"rules": rules, "params": params, "pilot": area_label(names), "districts": names, "buffer_m": cfg.buffer_m,
           "info": info, "manifest": manifest, "sample": sample,
           "n_grid_cells": 0 if layers["population_grid"] is None else len(layers["population_grid"])}
    write_report(out, ctx, checks)
    for c in checks:
        print(f"features: {c['name']}: {c['ok']} ({c['detail']})")
    if not all(c["ok"] for c in checks):
        print(f"features: check(s) failed, {OUT_PATH.name} not written; see {REPORT_PATH}", file=sys.stderr)
        return 1
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_PATH, index=False)
    print(f"features: {int(out['conflated'].sum())} segments with features -> {OUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
