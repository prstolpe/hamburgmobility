"""Stage 7: street-space width from transects and feasibility (guide 4.3 a and c, prompts/07_crosssection.md).

Usage: uv run python -m pipeline.s07_crosssection

Reads data/interim/features.parquet, ALKIS land use and buildings and the OSM extract (bridges/tunnels) and
writes data/interim/crosssection.parquet (features + width and feasibility columns), data/interim/transects.parquet,
reports/crosssection.md and reports/transect_sample.geojson (50 transects for manual measurement in the DOP20).
Parameters come from config/rules.yaml (sections crosssection, required_width, feasibility_classes).
If reports/transect_measurements.csv (transect_id, measured_m) exists, the report compares it with the
computed widths. The run stops with exit code 1 if a check fails; outputs are then not written.
"""

import json
import random
import sys
import warnings

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from pipeline.lib.area import area_label, district_names, load_area_config, read_work_area, sample_by_district
from pipeline.lib.crosssection import (
    XsParams,
    aggregate_widths,
    covered_extent,
    feasibility_class,
    fill_from_neighbours,
    first_hit,
    make_transects,
    near_points,
    required_widths,
)
from pipeline.lib.crs import WORK_CRS, to_work_crs
from pipeline.lib.features import FeatureParams, alkis_buildings
from pipeline.lib.links import osm_map_link, osm_way_link
from pipeline.lib.manifest import REPO_ROOT, load_manifest
from pipeline.lib.rules import load_rules
from pipeline.s02_network import _pbf_from_manifest
from pipeline.s04_features import _layer, _now, _fmt, _pct, text_histogram

FEATURES_PATH = REPO_ROOT / "data" / "interim" / "features.parquet"
OUT_PATH = REPO_ROOT / "data" / "interim" / "crosssection.parquet"
TRANSECTS_PATH = REPO_ROOT / "data" / "interim" / "transects.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "crosssection.md"
SAMPLE_GEOJSON = REPO_ROOT / "reports" / "transect_sample.geojson"
MEASUREMENTS_PATH = REPO_ROOT / "reports" / "transect_measurements.csv"
N_TRANSECT_SAMPLE = 50  # prompts/07 Prüfschritt
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
BRIDGE_SNAP_M = 1.0  # transect centre on a bridge/tunnel way of its own segment (geometric tolerance)
MAE_TARGET_M = 1.0  # prompts/07 Prüfschritt: target mean absolute error (assumption)
OSM_BBOX_MARGIN_DEG = 0.005


# --- inputs ----------------------------------------------------------------------------------


def bridge_tunnel_ways(pbf, work_area_wgs84) -> gpd.GeoDataFrame:
    """OSM ways tagged bridge or tunnel (value other than 'no') in the work area."""
    from pyrosm import OSM

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ways = OSM(str(pbf), bounding_box=work_area_wgs84.buffer(OSM_BBOX_MARGIN_DEG)).get_network(network_type="all")
    flag = pd.Series(False, index=ways.index)
    for col in ("bridge", "tunnel"):
        if col in ways:
            flag |= ways[col].notna() & (ways[col] != "no")
    return to_work_crs(ways.loc[flag, ["id", "geometry"]].reset_index(drop=True))


def junction_points(seg: gpd.GeoDataFrame) -> gpd.GeoSeries:
    """S-XS-04: end points of segments at nodes with degree != 2 (as S-NET-01)."""
    ends = pd.concat([
        pd.DataFrame({"node": seg["node_u"], "geometry": shapely.get_point(seg.geometry.to_numpy(), 0)}),
        pd.DataFrame({"node": seg["node_v"], "geometry": shapely.get_point(seg.geometry.to_numpy(), -1)})])
    degree = ends["node"].value_counts()
    keep = ends["node"].map(degree) != 2
    pts = ends[keep].drop_duplicates("node")
    return gpd.GeoSeries(pts["geometry"].to_numpy(), crs=seg.crs)


# --- computation -----------------------------------------------------------------------------


def on_bridge_or_tunnel(transects: gpd.GeoDataFrame, area: gpd.GeoDataFrame, bt: gpd.GeoDataFrame) -> np.ndarray:
    out = np.zeros(len(transects), dtype=bool)
    if bt.empty or transects.empty:
        return out
    i_t, i_w = shapely.STRtree(bt.geometry.to_numpy()).query(
        transects["centre"].to_numpy(), predicate="dwithin", distance=BRIDGE_SNAP_M)
    way_sets = [set(map(int, w)) for w in area["osm_way_ids"]]
    seg_pos = transects["seg_pos"].to_numpy()
    bt_ids = bt["id"].to_numpy()
    for t, w in zip(i_t, i_w):
        if int(bt_ids[w]) in way_sets[seg_pos[t]]:
            out[t] = True
    return out


def compute_transects(area: gpd.GeoDataFrame, seg_all: gpd.GeoDataFrame, traffic: gpd.GeoSeries,
                      buildings: gpd.GeoSeries, bt: gpd.GeoDataFrame, xs: XsParams) -> gpd.GeoDataFrame:
    t = make_transects(area.geometry, xs)
    t["segment_id"] = area["segment_id"].to_numpy()[t["seg_pos"].to_numpy()]
    t["near_node"] = near_points(t["centre"], junction_points(seg_all), xs.node_exclusion_m)
    t["bridge_tunnel"] = on_bridge_or_tunnel(t, area, bt)
    t["excluded"] = t["near_node"] | t["bridge_tunnel"]

    dl, end_l, cov_l = covered_extent(t["left"], traffic)
    dr, end_r, cov_r = covered_extent(t["right"], traffic)
    t["traffic_left_m"], t["traffic_right_m"] = dl, dr
    t["centre_outside"] = ~(cov_l & cov_r)
    t["traffic_open"] = end_l | end_r
    t["width_traffic_m"] = np.where(~t["excluded"] & ~t["centre_outside"] & ~t["traffic_open"], dl + dr, np.nan)

    fl, in_l = first_hit(t["left"], buildings)
    fr, in_r = first_hit(t["right"], buildings)
    t["facade_left_m"], t["facade_right_m"] = fl, fr
    t["centre_in_building"] = in_l | in_r
    t["facade_open"] = np.isnan(fl) | np.isnan(fr)
    t["width_facade_m"] = np.where(~t["excluded"] & ~t["centre_in_building"] & ~t["facade_open"], fl + fr, np.nan)
    t["open_space"] = t["traffic_open"] | t["facade_open"]
    t["transect_id"] = [f"{s}@{p:.0f}" for s, p in zip(t["segment_id"], t["position_m"])]
    return t


def segment_widths(area: gpd.GeoDataFrame, t: gpd.GeoDataFrame, xs: XsParams, rules) -> pd.DataFrame:
    n = len(area)
    traffic = aggregate_widths(t.rename(columns={"width_traffic_m": "width"})[["seg_pos", "position_m", "width"]], xs)
    facade = aggregate_widths(t.rename(columns={"width_facade_m": "width"})[["seg_pos", "position_m", "width"]], xs)
    out = pd.DataFrame(index=range(n))
    out = out.join(traffic.rename(columns={"n_valid": "width_n_valid"}))
    out = out.join(facade.rename(columns={"width_median_m": "facade_width_median_m", "width_p10_m": "facade_width_p10_m",
                                          "width_min_m": "facade_width_min_m", "n_valid": "facade_n_valid",
                                          "narrow_points": "facade_narrow_points"}))
    g = t.groupby("seg_pos")
    out["n_transects"] = g.size().reindex(out.index).fillna(0).astype(int)
    for col in ("excluded", "centre_outside", "traffic_open", "facade_open", "centre_in_building"):
        out[f"share_{col}"] = g[col].mean().reindex(out.index)
    out["width_n_valid"] = out["width_n_valid"].fillna(0).astype(int)
    out["facade_n_valid"] = out["facade_n_valid"].fillna(0).astype(int)
    out["narrow_points_count"] = out["narrow_points"].map(lambda v: len(v) if isinstance(v, list) else 0)
    out["narrow_points"] = out["narrow_points"].map(lambda v: json.dumps(v if isinstance(v, list) else []))
    out["facade_narrow_points"] = out["facade_narrow_points"].map(lambda v: json.dumps(v if isinstance(v, list) else []))
    keys = area[["name", "node_u", "node_v", "length_m"]].reset_index(drop=True)
    for col in ("width_p10_m", "width_median_m", "width_min_m", "facade_width_p10_m", "facade_width_median_m"):
        out[col], from_nb = fill_from_neighbours(keys.assign(**{col: out[col]}), col)  # S-XS-07
        if col == "width_p10_m":
            out["width_from_neighbour"] = from_nb
    for target, req in required_widths(rules).items():
        ratio = out["width_p10_m"] / req
        out[f"width_ratio_{target}"] = ratio
        out[f"feasibility_{target}"] = [feasibility_class(r, rules.feasibility_classes) for r in ratio]
    out.index = area.index
    return out


def _trace(r) -> str:
    def v(x):
        return None if pd.isna(x) else (round(float(x), 2) if isinstance(x, float) else x)
    return json.dumps([
        {"id": "S-XS-04", "inputs": {"n_transects": v(r["n_transects"]), "share_excluded": v(r["share_excluded"])}},
        {"id": "S-XS-02", "inputs": {"n_valid": v(r["width_n_valid"]), "share_centre_outside": v(r["share_centre_outside"]),
                                      "share_open": v(r["share_traffic_open"]), "p10_m": v(r["width_p10_m"])}},
        {"id": "S-XS-03", "inputs": {"n_valid": v(r["facade_n_valid"]), "p10_m": v(r["facade_width_p10_m"])}},
        {"id": "S-XS-07", "inputs": {"width_from_neighbour": bool(r["width_from_neighbour"])}},
    ], ensure_ascii=False)


# --- checks, samples, report -----------------------------------------------------------------


def run_checks(feat: gpd.GeoDataFrame, out: gpd.GeoDataFrame, t: gpd.GeoDataFrame) -> list[dict]:
    checks = [{"name": "segment_id unverändert", "ok": list(out["segment_id"]) == list(feat["segment_id"]),
               "detail": f"{len(out)} Abschnitte"}]
    w = t["width_traffic_m"].dropna()
    checks.append({"name": "Breiten positiv", "ok": bool((w > 0).all()) and bool((t["width_facade_m"].dropna() > 0).all()),
                   "detail": f"{len(w)} gültige Transekte Verkehrsfläche"})
    a = out.dropna(subset=["width_p10_m"])
    ok = bool((a["width_min_m"] <= a["width_p10_m"] + 1e-9).all() and (a["width_p10_m"] <= a["width_median_m"] + 1e-9).all())
    checks.append({"name": "min ≤ p10 ≤ Median", "ok": ok, "detail": f"{len(a)} Abschnitte mit Breite"})
    checks.append({"name": "transect_id eindeutig", "ok": t["transect_id"].is_unique, "detail": f"{len(t)} Transekte"})
    return checks


def pick_transect_sample(t: gpd.GeoDataFrame, pilot_ids: set[str]) -> gpd.GeoDataFrame:
    valid = t[t["segment_id"].isin(pilot_ids) & t["width_traffic_m"].notna()]
    rnd = random.Random(SAMPLE_SEED)
    idx = sorted(rnd.sample(list(valid.index), min(N_TRANSECT_SAMPLE, len(valid))))
    return valid.loc[idx]


def write_transect_sample(sample: gpd.GeoDataFrame) -> None:
    """GeoJSON in EPSG:4326 (RFC 7946) for the manual DOP20 measurement; measured_m stays empty."""
    cols = ["transect_id", "segment_id", "position_m", "width_traffic_m", "width_facade_m",
            "traffic_left_m", "traffic_right_m", "facade_left_m", "facade_right_m"]
    g = gpd.GeoDataFrame(sample[cols].round(2), geometry=sample.geometry, crs=WORK_CRS).to_crs("EPSG:4326")
    g["osm"] = [osm_map_link(p) for p in gpd.GeoSeries(sample["centre"].to_numpy(), crs=WORK_CRS).to_crs(4326)]
    g["measured_m"] = None
    g["comment"] = None
    SAMPLE_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    g.to_file(SAMPLE_GEOJSON, driver="GeoJSON")


def validation(t: gpd.GeoDataFrame) -> dict | None:
    if not MEASUREMENTS_PATH.exists():
        return None
    m = pd.read_csv(MEASUREMENTS_PATH).dropna(subset=["measured_m"])
    j = m.merge(t[["transect_id", "width_traffic_m"]], on="transect_id", how="inner").dropna()
    if j.empty:
        return {"n": 0}
    err = (j["width_traffic_m"] - j["measured_m"]).abs()
    return {"n": len(j), "mae": float(err.mean()), "max": float(err.max()), "bias": float((j["width_traffic_m"] - j["measured_m"]).mean())}


def write_report(out: gpd.GeoDataFrame, t: gpd.GeoDataFrame, ctx: dict, checks: list[dict]) -> None:
    rules, xs = ctx["rules"], ctx["xs"]
    area = out[out["conflated"].astype(bool)]
    pilot = area[area["bezirk"].isin(ctx["districts"])]
    req = required_widths(rules)
    n = len(t)
    km = area["length_m"].sum() / 1000
    val = ctx["validation"]
    lines = [
        "# Querschnittsbericht – Stufe 7", "",
        f"Erzeugt: {_now()} von `pipeline/s07_crosssection.py`, rules.yaml {rules.meta.version}. Nicht amtlicher Entwurf.", "",
        "## Kennzahlen", "",
        f"- Abschnitte im Arbeitsgebiet: {_fmt(len(area))} ({_fmt(km, 1)} km); davon mit Bezirk ({ctx['pilot']}): {_fmt(len(pilot))}",
        f"- Transekte: {_fmt(n)} (alle {xs.spacing_m:.0f} m, ± {xs.half_length_m:.0f} m, Tangente ± {xs.tangent_half_m:.0f} m, "
        f"Mittellinie vereinfacht {xs.simplify_m:.0f} m)",
        f"- Verworfen: nahe Knoten (≤ {xs.node_exclusion_m:.0f} m) {_pct(t['near_node'].mean())}, Brücke/Tunnel "
        f"{_pct(t['bridge_tunnel'].mean())}",
        f"- Verkehrsfläche: gültig {_pct(t['width_traffic_m'].notna().mean())}; Mittelpunkt außerhalb der ALKIS-Verkehrsfläche "
        f"{_pct((t['centre_outside'] & ~t['excluded']).mean())}; offen/Platz (keine Grenze in {xs.half_length_m:.0f} m) "
        f"{_pct((t['traffic_open'] & ~t['excluded']).mean())}",
        f"- Fassade: gültig {_pct(t['width_facade_m'].notna().mean())}; offen {_pct((t['facade_open'] & ~t['excluded']).mean())}; "
        f"Mittelpunkt in Gebäude {_pct((t['centre_in_building'] & ~t['excluded']).mean())}",
        f"- Abschnitte mit width_p10_m: {_pct(area['width_p10_m'].notna().mean())} (Länge: "
        f"{_pct(area.loc[area['width_p10_m'].notna(), 'length_m'].sum() / area['length_m'].sum())}); mit Fassadenbreite "
        f"{_pct(area['facade_width_p10_m'].notna().mean())}",
        f"- Engstellen (≥ {xs.min_run} Transekte unter p10): {int(area['narrow_points_count'].sum())} in "
        f"{int((area['narrow_points_count'] > 0).sum())} Abschnitten",
        f"- ALKIS: {_fmt(ctx['n_traffic'])} Verkehrsflächen ({', '.join(sorted(xs.nutzart))}), {_fmt(ctx['n_buildings'])} oberirdische Gebäude",
        "", "## Prüfungen", "", "| Prüfung | Ergebnis | Detail |", "| --- | --- | --- |",
        *[f"| {c['name']} | {'ok' if c['ok'] else 'FEHLER'} | {c['detail']} |" for c in checks],
        "", "## Validierung im Orthophoto (Prüfschritt)", "",
        f"{N_TRANSECT_SAMPLE} zufällige gültige Transekte in {ctx['pilot']} (Seed {SAMPLE_SEED}) stehen in "
        "`reports/transect_sample.geojson` (EPSG:4326, Breite Verkehrsfläche Grenze zu Grenze). Messung im DOP20 "
        "eintragen in `reports/transect_measurements.csv` (Spalten `transect_id`, `measured_m`) und Stufe neu laufen lassen.", "",
    ]
    if val is None or val.get("n", 0) == 0:
        lines += [f"| Kennzahl | Wert |", "| --- | --- |", "| gemessene Transekte | _offen_ |",
                  f"| mittlere absolute Abweichung (Ziel < {MAE_TARGET_M:.0f} m, Annahme) | _offen – nach manueller Messung_ |"]
    else:
        lines += ["| Kennzahl | Wert |", "| --- | --- |", f"| gemessene Transekte | {val['n']} |",
                  f"| mittlere absolute Abweichung | {val['mae']:.2f} m ({'Ziel erreicht' if val['mae'] < MAE_TARGET_M else 'Ziel verfehlt'}) |",
                  f"| größte Abweichung | {val['max']:.2f} m |", f"| mittlere Abweichung (berechnet − gemessen) | {val['bias']:+.2f} m |"]
    lines += ["", "## Methode", "",
              "- **Transekte (S-XS-01):** Mittellinie vereinfacht, Transekt alle spacing_m ab spacing_m/2, Richtung senkrecht "
              "zur Sehne über ± tangent_half_m.",
              "- **Verkehrsfläche (S-XS-02):** zusammenhängende Strecke des Transekts in ALKIS-Flächen "
              f"{', '.join(sorted(xs.nutzart))} um den Mittelpunkt; aneinandergrenzende Flächen zählen als eine. "
              "`width_p10_m` (für C-G30-02) kommt aus dieser Variante.",
              "- **Fassade (S-XS-03):** Abstand der ersten oberirdischen ALKIS-Gebäude (wie S-FEAT-03) links und rechts.",
              "- **Sonderfälle (S-XS-04):** Knoten = Abschnittsenden mit Grad ≠ 2; Brücken/Tunnel: Mittelpunkt auf einem OSM-Way "
              "des Abschnitts mit bridge/tunnel. Offene Transekte gehen nicht in die Statistik ein.",
              f"- **Aggregation (S-XS-05):** Median, Quantil {xs.quantile:g}, Minimum; Engstelle = mindestens {xs.min_run} "
              "aufeinanderfolgende gültige Transekte unter dem p10 des Abschnitts.",
              "- **Machbarkeit (S-XS-06):** width_ratio = width_p10_m / erforderliche Breite; " +
              ", ".join(f"{k} {v:.2f} m" for k, v in req.items()) + " (bei Bereichen die Untergrenze). Klassen: fits ≥ "
              f"{rules.feasibility_classes['fits'].min:.2f}, tight ≥ {rules.feasibility_classes['tight'].min:.2f}, sonst does_not_fit.",
              "- **Fehlerquellen (guide.md 4.3 a):** Straßenflurstücke enthalten Böschungen und Grün; Vorgärten fehlen in der "
              "Variante Verkehrsfläche; Versatz der OSM-Mittellinie (→ centre_outside); Arkaden und Durchfahrten.",
              "", "## Machbarkeit je Soll-Kategorie (Arbeitsgebiet, Anteil der Länge)", "",
              "| Ziel | erforderlich | fits | tight | does_not_fit | ohne Breite |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for target, r in req.items():
        col = area[f"feasibility_{target}"].fillna("none")
        share = area.groupby(col)["length_m"].sum() / area["length_m"].sum()
        lines.append(f"| {target} | {r:.2f} m | " + " | ".join(_pct(share.get(k, 0.0)) for k in
                                                                 ("fits", "tight", "does_not_fit", "none")) + " |")
    lines += ["", "## Machbarkeit GOW50 und Breitenabdeckung je Bezirk (Anteil der Länge)", "",
              "| Bezirk | km | mit width_p10_m | GOW50 fits | tight | does_not_fit |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for bz, g in sorted(pilot.groupby("bezirk")) + [("**gesamt**", pilot)]:
        L = g["length_m"].sum()
        sh = g.groupby(g["feasibility_GOW50"].fillna("none"))["length_m"].sum() / L
        lines.append(f"| {bz} | {_fmt(L / 1000, 1)} | {_pct(g.loc[g['width_p10_m'].notna(), 'length_m'].sum() / L)} | "
                     + " | ".join(_pct(sh.get(k, 0.0)) for k in ("fits", "tight", "does_not_fit")) + " |")
    lines += ["", "## width_p10_m nach highway-Klasse (Median über Abschnitte)", "",
              "| highway | Abschnitte | mit Breite | p10 Verkehrsfläche | p10 Fassade | GOW50 fits |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for hw, g in area.groupby("highway"):
        lines.append(f"| {hw} | {len(g)} | {_pct(g['width_p10_m'].notna().mean())} | {g['width_p10_m'].median():.1f} | "
                     f"{g['facade_width_p10_m'].median():.1f} | {_pct((g['feasibility_GOW50'] == 'fits').mean())} |")
    both = t.dropna(subset=["width_traffic_m", "width_facade_m"])
    lines += ["", "## Verteilungen", "", "### Breite Verkehrsfläche je Transekt (m)", "", *text_histogram(t["width_traffic_m"]),
              "", "### Breite Fassade je Transekt (m)", "", *text_histogram(t["width_facade_m"]),
              "", "### width_p10_m je Abschnitt (m)", "", *text_histogram(area["width_p10_m"]),
              "", f"Fassade schmaler als Verkehrsfläche bei {_pct((both['width_facade_m'] < both['width_traffic_m'] - 0.5).mean())} "
              "der Transekte mit beiden Werten (Hinweis auf Gebäude im Straßenflurstück, Arkaden oder Versatz).", ""]
    lines += [f"## Stichprobe ({len(ctx['sample'])} zufällige Abschnitte in {ctx['pilot']}, nach Bezirk geschichtet, Seed {SAMPLE_SEED})", "",
              "Links auf OSM-Karte und OSM-Way; Orthophoto-/Panoramax-Links folgen, sobald das Linkformat geklärt ist.", "",
              "| segment_id | Bezirk | Name | highway | Länge m | Transekte | gültig | p10 Verkehrsfl. | Median | p10 Fassade | GOW50 | GOW30 | Karte | Way |",
              "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |"]
    for _, r in ctx["sample"].iterrows():
        pt = gpd.GeoSeries([r.geometry.interpolate(0.5, normalized=True)], crs=WORK_CRS).to_crs(4326).iloc[0]

        def f(v, d=1):
            return "–" if pd.isna(v) else f"{float(v):.{d}f}"
        lines.append(f"| `{r['segment_id']}` | {r['bezirk']} | {r['name'] if isinstance(r['name'], str) else '–'} | {r['highway']} | "
                     f"{r['length_m']:.0f} | {r['n_transects']} | {r['width_n_valid']} | {f(r['width_p10_m'])} | "
                     f"{f(r['width_median_m'])} | {f(r['facade_width_p10_m'])} | {r['feasibility_GOW50'] or '–'} | "
                     f"{r['feasibility_GOW30_narrow'] or '–'} | [Karte]({osm_map_link(pt)}) | [Way]({osm_way_link(r['osm_way_ids'][0])}) |")
    lines += ["", "## Lizenz", "",
              "ALKIS (tatsächliche Nutzung, Gebäude): Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und "
              "Vermessung (LGV), dl-de/by-2.0. Abschnitte und Brücken/Tunnel aus OpenStreetMap © OpenStreetMap-Beitragende, "
              "ODbL 1.0.", ""]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# --- main ------------------------------------------------------------------------------------


def main() -> int:
    rules = load_rules()
    xs = XsParams.from_rules(rules)
    cfg = load_area_config()
    names = district_names()
    if not FEATURES_PATH.exists():
        print("crosssection: data/interim/features.parquet missing; run `make features` first", file=sys.stderr)
        return 1
    manifest = load_manifest()
    nutzung = _layer(manifest, "alkis", "ave:Nutzung")
    raw_buildings = _layer(manifest, "alkis", "ave:GebaeudeBauwerk")
    if nutzung is None or raw_buildings is None:
        print("crosssection: ALKIS layers missing in data/raw; run `make fetch` first", file=sys.stderr)
        return 1
    unknown = sorted(xs.nutzart - set(nutzung["nutzart"].dropna()))
    if unknown:
        print(f"crosssection: nutzart values from rules.yaml not in ALKIS data: {unknown}", file=sys.stderr)
        return 1
    try:
        pbf = _pbf_from_manifest(manifest)
    except FileNotFoundError as e:
        print(f"crosssection: {e}", file=sys.stderr)
        return 1

    feat = gpd.read_parquet(FEATURES_PATH)
    work_area = read_work_area(cfg)
    work_area_wgs84 = gpd.GeoSeries([work_area], crs=WORK_CRS).to_crs(4326).iloc[0]
    traffic = nutzung.loc[nutzung["nutzart"].isin(xs.nutzart)].geometry.reset_index(drop=True)
    buildings = alkis_buildings(raw_buildings, FeatureParams.from_rules(rules)).geometry
    bt = bridge_tunnel_ways(REPO_ROOT / pbf["path"], work_area_wgs84)

    in_area = feat["conflated"].astype(bool)
    area = feat[in_area]
    print(f"crosssection: {len(area)} segments, {len(traffic)} traffic areas, {len(buildings)} buildings, "
          f"{len(bt)} bridge/tunnel ways")
    t = compute_transects(area, feat, traffic, buildings, bt, xs)
    print(f"crosssection: {len(t)} transects")
    widths = segment_widths(area, t, xs, rules)
    # features.parquet carries width_p10_m as a null placeholder (stage 4); this stage fills it.
    out = feat.drop(columns=[c for c in widths.columns if c in feat.columns]).join(widths)
    out["crosssection_trace"] = [_trace(r) if c else None for c, (_, r) in zip(in_area, out.iterrows())]

    checks = run_checks(feat, out, t)
    pilot = out[out["bezirk"].isin(names) & in_area]
    sample = sample_by_district(pilot, SAMPLE_SIZE, SAMPLE_SEED)
    transect_sample = pick_transect_sample(t, set(pilot["segment_id"]))
    ctx = {"rules": rules, "xs": xs, "pilot": area_label(names), "districts": names, "sample": sample, "validation": validation(t),
           "n_traffic": len(traffic), "n_buildings": len(buildings)}
    write_report(out, t, ctx, checks)
    for c in checks:
        print(f"crosssection: {c['name']}: {c['ok']} ({c['detail']})")
    if not all(c["ok"] for c in checks):
        print(f"crosssection: check(s) failed, outputs not written; see {REPORT_PATH}", file=sys.stderr)
        return 1
    write_transect_sample(transect_sample)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_PATH, index=False)
    t_out = t.drop(columns=["centre", "left", "right"])
    t_out.to_parquet(TRANSECTS_PATH, index=False)
    print(f"crosssection: width_p10_m for {int(out['width_p10_m'].notna().sum())} segments -> "
          f"{OUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
