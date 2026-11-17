"""Stage c09: street trees and parking spaces per target cross section (prompts/26 Teil 2).

Usage: uv run python -m pipeline.c09_trees_parking

Reads data/interim/cross_section_soll.parquet (target profile), data/interim/final.parquet (segments, nodes, ways),
the Öffentlicher Parkraum (LBV) and the Straßenbaumkataster from data/raw and the OSM extract (parking tags per
side). Writes data/interim/trees_parking.parquet and reports/trees_parking.md. Rules: design_rules.yaml
trees_parking (TP-P-01..04, TP-T-01..03). Missing data stays missing; it is never counted as zero.
"""

import json
import sys
import time
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd

from pipeline.lib import trees_parking as tp
from pipeline.lib.area import read_work_area, sample_by_district
from pipeline.lib.crs import WORK_CRS, to_work_crs
from pipeline.lib.features import parking_by_side
from pipeline.lib.links import load_viewers, orthophoto_link, panoramax_link
from pipeline.lib.manifest import REPO_ROOT, load_manifest
from pipeline.lib.rules import load_design_rules
from pipeline.s02_network import _pbf_from_manifest

INTERIM = REPO_ROOT / "data" / "interim"
XS_PATH = INTERIM / "cross_section_soll.parquet"
FINAL_PATH = INTERIM / "final.parquet"
OUT_PATH = INTERIM / "trees_parking.parquet"
CACHE_DIR = INTERIM / "cache"
REPORT_PATH = REPO_ROOT / "reports" / "trees_parking.md"
OSM_BBOX_MARGIN_DEG = 0.005
WAY_WEIGHT_BUFFER_M = 1.0  # as S-FEAT-10: length of a way inside this buffer of the segment = its weight
SAMPLE_SIZE = 30
SAMPLE_SEED = 26


def _raw(manifest: dict, source: str) -> gpd.GeoDataFrame:
    files = (manifest["sources"].get(source) or {}).get("files") or []
    paths = [REPO_ROOT / f["path"] for f in files if str(f.get("path", "")).endswith(".parquet")]
    if not paths or not all(p.exists() for p in paths):
        raise FileNotFoundError(f"{source} missing in data/raw; run `make fetch` first")
    return to_work_crs(pd.concat([gpd.read_parquet(p) for p in paths], ignore_index=True))


# --- OSM parking per side -----------------------------------------------------------------------------------


def read_way_parking(pbf, work_area_wgs84) -> gpd.GeoDataFrame:
    """Ways with parking tags (id, geometry, sides); cached per extract."""
    key = f"{pbf.name}_{pbf.stat().st_size}"
    cache = CACHE_DIR / f"way_parking_{key}.parquet"
    if cache.exists():
        df = gpd.read_parquet(cache)
        df["sides"] = df["sides"].map(json.loads)
        return df
    from pyrosm import OSM

    from pipeline.s04_features import _way_tags

    osm = OSM(str(pbf), bounding_box=work_area_wgs84.buffer(OSM_BBOX_MARGIN_DEG))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ways = to_work_crs(osm.get_network(network_type="all").reset_index(drop=True))
    rows = []
    for _, row in ways.iterrows():
        sides = parking_by_side(_way_tags(row))
        if sides:
            rows.append({"id": int(row["id"]), "sides": sides, "geometry": row.geometry})
    out = gpd.GeoDataFrame(rows, geometry="geometry", crs=WORK_CRS)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out.assign(sides=out["sides"].map(json.dumps)).to_parquet(cache)
    return out


def _same_direction(seg_line, way_line) -> bool:
    """Does the way run in the segment's direction (tangents at the segment midpoint)?"""
    mid = seg_line.interpolate(0.5, normalized=True)
    t_s = seg_line.project(mid)
    a, b = seg_line.interpolate(max(t_s - 1, 0)), seg_line.interpolate(min(t_s + 1, seg_line.length))
    t_w = way_line.project(mid)
    c, d = way_line.interpolate(max(t_w - 1, 0)), way_line.interpolate(min(t_w + 1, way_line.length))
    return (b.x - a.x) * (d.x - c.x) + (b.y - a.y) * (d.y - c.y) >= 0


def segment_osm_sides(seg: gpd.GeoDataFrame, ways: gpd.GeoDataFrame) -> dict[str, dict]:
    """segment_id -> {side: (position, orientation)} in segment direction; per side the value with the largest
    way length inside the segment (S-FEAT-10 majority)."""
    w = ways.drop_duplicates("id").set_index("id")
    out = {}
    for sid, line, way_ids in zip(seg["segment_id"], seg.geometry, seg["osm_way_ids"]):
        votes = {s: {} for s in tp.SIDES}
        buf = None
        for wid in way_ids:
            wid = int(wid)
            if wid not in w.index:
                continue
            way = w.loc[wid]
            buf = buf if buf is not None else line.buffer(WAY_WEIGHT_BUFFER_M)
            weight = way.geometry.intersection(buf).length
            if weight <= 0:
                continue
            flip = not _same_direction(line, way.geometry)
            for side, val in way["sides"].items():
                s = side if not flip else ("left" if side == "right" else "right")
                key = tuple(val)
                votes[s][key] = votes[s].get(key, 0.0) + weight
        sides = {s: max(v, key=v.get) for s, v in votes.items() if v}
        if sides:
            out[sid] = sides
    return out


# --- official spaces and trees ------------------------------------------------------------------------------


def assign_official(spaces: gpd.GeoDataFrame, seg: gpd.GeoDataFrame, p: tp.Params) -> tuple[pd.DataFrame, dict]:
    """Spaces per segment and side (TP-P-01): counted, uncertain (Klärung); excluded management dropped."""
    sp = spaces[~spaces["primaere_bewirtschaftung"].isin(p.exclude_management)].copy()
    sp["n"] = [tp.official_space_count(g, o, p) for g, o in zip(sp.geometry, sp["ausrichtung_zur_strasse"])]
    sp["uncertain"] = sp["primaere_bewirtschaftung"].isin(p.uncertain_management) | \
        (sp["ausrichtung_zur_strasse"] == "Klärung")
    pts = sp.geometry.representative_point()
    max_d = (seg["width_median_m"] / 2 + p.assign_extra_m).fillna(p.tree_no_width_max_m)
    a = tp.nearest_assign(pts, seg, max_d, float(max_d.max()))
    a = a.join(sp[["n", "uncertain"]], on="point")
    a["side"] = np.where(a["offset"] >= 0, "left", "right")
    g = a.groupby(["segment_id", "side"])
    out = pd.DataFrame({"n": g["n"].sum(), "n_uncertain": a[a["uncertain"]].groupby(["segment_id", "side"])["n"].sum()})
    info = {"spaces": len(spaces), "excluded": int(len(spaces) - len(sp)), "assigned": int(len(a)),
            "unassigned": int(len(sp) - len(a))}
    return out.fillna({"n_uncertain": 0.0}), info


def assign_trees(trees: gpd.GeoDataFrame, seg: gpd.GeoDataFrame, p: tp.Params) -> tuple[pd.DataFrame, dict]:
    max_d = (seg["width_median_m"] / 2 + p.tree_extra_m).fillna(p.tree_no_width_max_m)
    pts = trees.geometry.representative_point()  # the cadastre stores single trees as MultiPoint
    a = tp.nearest_assign(pts, seg, max_d, float(max_d.max()))
    return a, {"trees": len(trees), "assigned": int(len(a)), "unassigned": int(len(trees) - len(a))}


# --- per segment --------------------------------------------------------------------------------------------


def node_junctions(final: pd.DataFrame) -> set:
    """Nodes with three or more arms (all segments of the network)."""
    deg = pd.concat([final["node_u"], final["node_v"]]).value_counts()
    return set(deg[deg >= 3].index)


def compute(seg: gpd.GeoDataFrame, official: pd.DataFrame, osm_sides: dict, trees: pd.DataFrame,
            junctions: set, p: tp.Params) -> tuple[pd.DataFrame, float, dict]:
    usable = {}
    for r in seg.itertuples():
        ct = bool(r.cycle_track) if pd.notna(r.cycle_track) else False
        usable[r.segment_id] = {s: tp.usable_kerb_m(r.length_m, r.node_u in junctions, r.node_v in junctions, ct, s, p)
                                for s in tp.SIDES}
    off = official["n"].to_dict() if len(official) else {}
    off_unc = official["n_uncertain"].to_dict() if len(official) else {}
    has_official = {sid for sid, _ in off}

    # TP-P-01 osm_factor: counted (LBV) / computed (OSM) on sides with both
    ratios = []
    for (sid, side), n in off.items():
        val = osm_sides.get(sid, {}).get(side)
        if val and val[0] in p.parking_positions:
            est = tp.osm_spaces(val[0], val[1], usable[sid][side], 1.0, p)
            if est and est > 0:
                ratios.append(n / est)
    factor = float(np.median(ratios)) if ratios else 1.0
    calib = {"sides": len(ratios), "factor": factor,
             "p25": float(np.quantile(ratios, 0.25)) if ratios else None,
             "p75": float(np.quantile(ratios, 0.75)) if ratios else None}

    tree_groups = {sid: g["offset"].to_numpy() for sid, g in trees.groupby("segment_id")} if len(trees) else {}
    rows = []
    for r in seg.itertuples():
        sid = r.segment_id
        today, src = {}, {}
        for s in tp.SIDES:
            if (sid, s) in off:
                today[s], src[s] = float(off[(sid, s)]), "official"
            elif sid in has_official and r.length_m >= p.official_zero_min_length_m:
                today[s], src[s] = 0.0, "official_zero"   # the street was surveyed, this side has no spaces
            else:
                val = osm_sides.get(sid, {}).get(s)
                n = tp.osm_spaces(val[0], val[1], usable[sid][s], factor, p) if val else None
                today[s], src[s] = n, ("osm" if n is not None else "none")
        elements = json.loads(r.profile_elements) if isinstance(r.profile_elements, str) else []
        if elements:
            known_pos = {s: src[s] == "osm" for s in tp.SIDES}
            removed = isinstance(r.degrade_steps_applied, str) and "D1" in r.degrade_steps_applied.split("|")
            t_lo, t_hi = tp.target_parking(today, usable[sid], elements, factor, p, r.cat_final, removed, known_pos)
        else:
            t_lo = t_hi = None
        known = [today[s] for s in tp.SIDES if today[s] is not None]
        complete = len(known) == 2
        offsets = tree_groups.get(sid, np.array([]))
        aff_lo = aff_hi = aff_mid = strip = 0
        if elements:
            for o in offsets:
                surely, possibly, central, in_strip = tp.classify_tree(
                    float(o), elements, r.available_m if pd.notna(r.available_m) else None, p)
                aff_lo += surely
                aff_hi += possibly
                aff_mid += central
                strip += in_strip
        n_trees = len(offsets)
        rows.append({
            "segment_id": sid, "usable_left_m": usable[sid]["left"], "usable_right_m": usable[sid]["right"],
            "park_src_left": src["left"], "park_src_right": src["right"],
            "park_today_left": today["left"], "park_today_right": today["right"],
            "park_today": sum(known) if complete else np.nan, "park_today_known": sum(known) if known else np.nan,
            "park_today_complete": complete, "park_uncertain": off_unc.get((sid, "left"), 0.0) + off_unc.get((sid, "right"), 0.0),
            "park_target_min": np.nan if t_lo is None else t_lo, "park_target_max": np.nan if t_hi is None else t_hi,
            "has_profile": bool(elements),
            "trees_n": n_trees, "trees_affected_min": aff_lo if elements else np.nan,
            "trees_affected_max": aff_hi if elements else np.nan, "trees_affected_mid": aff_mid if elements else np.nan,
            "trees_new": tp.new_trees(usable[sid], elements, strip, p) if elements else np.nan,
        })
    out = pd.DataFrame(rows)
    # change only where today is complete; the target range then gives the change range
    out["park_change_min"] = np.where(out["park_today_complete"], out["park_target_min"] - out["park_today"], np.nan)
    out["park_change_max"] = np.where(out["park_today_complete"], out["park_target_max"] - out["park_today"], np.nan)
    return out, factor, calib


# --- report -------------------------------------------------------------------------------------------------


def _n(x, d=0) -> str:
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:,.{d}f}".replace(",", " ")


def write_report(out: gpd.GeoDataFrame, ctx: dict, summary: dict) -> None:
    viewers = load_viewers()
    lines = ["# Bäume und Parkplätze je Soll-Querschnitt (Stufe c09)", "",
             f"Stand {ctx['date']} · design_rules.yaml {ctx['design_version']} · Regeln TP-P-01 bis TP-T-03 · "
             "Methode: docs/trees_parking/methode_vorschlag.md", "",
             "Schätzung, keine Planung. Bäume: „möglicherweise betroffen“, nie „wird gefällt“. Fehlende Daten zählen nie als 0.", "",
             "## Daten", "",
             f"- Öffentlicher Parkraum (LBV): {_n(ctx['official']['spaces'])} Flächen, davon {_n(ctx['official']['excluded'])} "
             f"ohne Parkrecht (eingeschränktes Haltverbot), {_n(ctx['official']['assigned'])} einem Abschnitt zugeordnet, "
             f"{_n(ctx['official']['unassigned'])} ohne Abschnitt im Straßenraum.",
             f"- Straßenbaumkataster: {_n(ctx['trees']['trees'])} Bäume, {_n(ctx['trees']['assigned'])} einem Abschnitt "
             f"zugeordnet, {_n(ctx['trees']['unassigned'])} außerhalb des Straßenraums (Parks, Gärten, außerhalb des Arbeitsgebiets).",
             f"- OSM-Parkangaben je Seite: {_n(ctx['osm_segments'])} Abschnitte mit mindestens einer Seite.",
             f"- Eichung OSM (TP-P-01 osm_factor): gezählt ÷ rechnerisch auf {_n(ctx['calib']['sides'])} Seiten mit beiden "
             f"Angaben: Median {_n(ctx['calib']['factor'], 2)} (25.–75. Perzentil {_n(ctx['calib']['p25'], 2)}–{_n(ctx['calib']['p75'], 2)}).", "",
             "## Abdeckung Parken (Länge der Abschnitte)", "",
             "| Bezirk | km | amtlich | nur OSM | keine Daten |", "| --- | ---: | ---: | ---: | ---: |"]
    for name, d in summary.items():
        lines.append(f"| {name} | {_n(d['km'])} | {_n(100 * d['share_official'], 1)} % | {_n(100 * d['share_osm'], 1)} % | "
                     f"{_n(100 * d['share_none'], 1)} % |")
    lines += ["", "## Kennzahlen", "",
              "| Bezirk | Parkplätze gezählt | davon Straßen vollständig | Ziel (vollständige Straßen) | "
              "Bäume | möglicherweise betroffen: Mitte (Spanne) | neu möglich |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for name, d in summary.items():
        lines.append(f"| {name} | {_n(d['park_counted'])} | {_n(d['park_today_complete'])} | "
                     f"{_n(d['park_target_lo'])}–{_n(d['park_target_hi'])} | {_n(d['trees_n'])} | "
                     f"{_n(d['trees_affected_mid'])} ({_n(d['trees_affected_lo'])}–{_n(d['trees_affected_hi'])}) | {_n(d['trees_new'])} |")
    lines += ["", f"## {SAMPLE_SIZE} Zufallsstichproben (Abschnitte mit Parkdaten oder Bäumen)", "",
              "| Abschnitt | Straße | Bezirk | Parken heute (Quelle) | Ziel | Bäume | betroffen | neu | Orthophoto | Panoramax |",
              "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |"]
    cand = out[(out["park_today_known"].notna()) | (out["trees_n"] > 0)]
    sample = sample_by_district(cand, SAMPLE_SIZE, SAMPLE_SEED)
    for r in sample.itertuples():
        mid = r.geometry.interpolate(0.5, normalized=True)
        wgs = gpd.GeoSeries([mid], crs=WORK_CRS).to_crs(4326).iloc[0]
        src = "/".join(sorted({r.park_src_left, r.park_src_right}))
        lines.append(f"| `{r.segment_id}` | {r.name if isinstance(r.name, str) else '–'} | {r.bezirk} | {_n(r.park_today_known)} ({src}) | "
                     f"{_n(r.park_target_min)}–{_n(r.park_target_max)} | {r.trees_n} | {_n(r.trees_affected_min)}–{_n(r.trees_affected_max)} | "
                     f"{_n(r.trees_new)} | [Luftbild]({orthophoto_link(mid, viewers)}) | [Straße]({panoramax_link(wgs, viewers)}) |")
    lines += ["", "Quellenvermerke: Straßenbaumkataster © FHH, BUKEA; Öffentlicher Parkraum © FHH, Landesbetrieb Verkehr "
              "(beide dl-de/by-2.0); © OpenStreetMap-Beitragende (ODbL).", ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    for path, step in ((XS_PATH, "make cross-section-soll"), (FINAL_PATH, "make coherence")):
        if not path.exists():
            print(f"trees-parking: {path.relative_to(REPO_ROOT)} missing; run `{step}` first", file=sys.stderr)
            return 1
    t0 = time.perf_counter()

    def tick(msg: str) -> None:
        print(f"trees-parking: {msg} ({time.perf_counter() - t0:.0f} s)")

    design = load_design_rules()
    p = tp.Params.from_rules(design)
    manifest = load_manifest()
    try:
        spaces = _raw(manifest, "parking_spaces")
        trees = _raw(manifest, "street_trees")
        pbf = _pbf_from_manifest(manifest)
    except FileNotFoundError as exc:
        print(f"trees-parking: {exc}", file=sys.stderr)
        return 1
    final = pd.read_parquet(FINAL_PATH, columns=["segment_id", "node_u", "node_v", "osm_way_ids", "width_median_m",
                                                  "cycle_track_tag"])
    xs = gpd.read_parquet(XS_PATH, columns=["segment_id", "name", "bezirk", "length_m", "cat_final", "profile_elements",
                                            "available_m", "degrade_steps_applied", "geometry"])
    seg = xs[xs["cat_final"].notna() & xs["bezirk"].notna()].merge(final, on="segment_id", how="left")
    seg = gpd.GeoDataFrame(seg.rename(columns={"cycle_track_tag": "cycle_track"}), geometry="geometry", crs=WORK_CRS).reset_index(drop=True)
    junctions = node_junctions(final)
    tick(f"{len(seg)} segments, {len(junctions)} junction nodes")

    official, off_info = assign_official(spaces, seg, p)
    tick(f"official spaces assigned: {off_info['assigned']} of {off_info['spaces']}")
    work_area_wgs84 = gpd.GeoSeries([read_work_area()], crs=WORK_CRS).to_crs(4326).iloc[0]
    ways = read_way_parking(REPO_ROOT / pbf["path"], work_area_wgs84)
    osm_sides = segment_osm_sides(seg, ways)
    tick(f"OSM parking per side on {len(osm_sides)} segments")
    tree_a, tree_info = assign_trees(trees, seg, p)
    tick(f"trees assigned: {tree_info['assigned']} of {tree_info['trees']}")

    res, factor, calib = compute(seg, official, osm_sides, tree_a, junctions, p)
    out = seg[["segment_id", "name", "bezirk", "length_m", "cat_final", "geometry"]].merge(res, on="segment_id")
    out = gpd.GeoDataFrame(out, geometry="geometry", crs=WORK_CRS)
    out["osm_factor"] = factor  # TP-P-01, calibrated in this run (also used for the target capacity in the export)
    assert out["segment_id"].is_unique
    out.to_parquet(OUT_PATH)
    summary = tp.district_summary(out, p)
    write_report(out, {"date": pd.Timestamp.now().strftime("%Y-%m-%d"), "design_version": design.meta.version,
                       "official": off_info, "trees": tree_info, "osm_segments": len(osm_sides), "calib": calib}, summary)
    tick(f"wrote {OUT_PATH.relative_to(REPO_ROOT)} and {REPORT_PATH.relative_to(REPO_ROOT)} (osm_factor {factor:.2f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
