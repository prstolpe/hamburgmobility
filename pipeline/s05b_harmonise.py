"""Stage 5b: harmonise categories along streets (H-STR-01) and across carriageways (H-PAIR-01), after the cascade and
before network coherence.

Usage: uv run python -m pipeline.s05b_harmonise   (part of make classify)

Reads data/interim/classified.parquet and writes data/interim/harmonised.parquet with
  cat_cascade   result of the cascade (stage 5)
  cat_proposed  harmonised category (input of coherence, overrides, discrepancy)
and a rule_trace step H-STR-01 or H-PAIR-01 for every changed segment, plus reports/harmonisation.md with 30 random
changed segments in the work area, the carriageway pairs and the GOW50 islands of at least gap_close_m between GOW30
(review list, reports/harmonisation_gow50_islands.geojson). Segments with an approved override are not changed.
"""

import json
import sys

import geopandas as gpd
import pandas as pd
import shapely

from pipeline.lib import coherence as coh
from pipeline.lib.area import area_label, district_names, sample_by_district
from pipeline.lib.crs import WORK_CRS
from pipeline.lib.harmonise import GOW, PAIR_RULE_ID, RULE_ID, _runs, carriageway_pairs, harmonise_all
from pipeline.lib.links import load_viewers, orthophoto_link, osm_way_link, panoramax_link
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.overrides import read_overrides
from pipeline.lib.rules import load_rules
from pipeline.s04_features import _fmt, _now

IN_PATH = REPO_ROOT / "data" / "interim" / "classified.parquet"
OUT_PATH = REPO_ROOT / "data" / "interim" / "harmonised.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "harmonisation.md"
ISLANDS_PATH = REPO_ROOT / "reports" / "harmonisation_gow50_islands.geojson"
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
STEP_TEXT = {1: "ETW30-Insel in GOW → GOW", 2: "GOW-Insel in ETW30 → ETW30", 3: "GOW50-Insel in GOW30 → GOW30",
             4: "GOW30 auf Mindestlänge verlängert", "P": "Richtungsfahrbahn neben GOW30 → GOW30 (H-PAIR-01)"}


def approved_override_ids() -> set[str]:
    ov = read_overrides()
    return set(ov.loc[ov["review_status"] == "approved", "segment_id"])


def street_strokes(area: gpd.GeoDataFrame, rules, cat_col: str = "cat_proposed") -> list[list[str]]:
    """Strokes (as N2) over the classified segments of the work area."""
    seg = area[["segment_id", "node_u", "node_v", cat_col, "length_m", "highway", "travel_speed_kmh",
                "geometry"]].rename(columns={cat_col: "cat"})
    return coh.strokes(coh.build_graph(seg, rules), rules)


def street_pairs(area: gpd.GeoDataFrame, rules) -> list[dict]:
    """H-PAIR-01 carriageway pairs in the work area, independent of the category (the rule only acts on GOW)."""
    if "oneway" not in area.columns:
        raise ValueError("column oneway missing (S-FEAT-10 since rules.yaml 0.23.0); run `make features` first")
    return carriageway_pairs(area[["segment_id", "name", "oneway", "node_u", "node_v", "geometry"]], rules)


def _trace_step(rid: str, steps: list[dict], conf, names: dict) -> dict:
    """One rule_trace entry per harmonisation rule: first 'from', last 'to' and the inputs of the last step."""
    last = steps[-1]
    inputs = {"from_cat": steps[0]["from"], "to_cat": last["to"], "pass": last["pass"]}
    if rid == RULE_ID:
        inputs |= {"run_m": last["run_m"], "neighbours": " und ".join(n for n in last["neighbours"] if n) or "–",
                   "step": last["step"]}
    else:
        inputs |= {"partner": last["partner"], "partner_name": names.get(last["partner"]) or "–",
                   "dist_m": last["dist_m"], "overlap_share": last["overlap_share"]}
    return {"id": rid, "passed": True, "result": True, "confidence": conf, "inputs": inputs}


def apply(inp: gpd.GeoDataFrame, rules, locked: set[str]) -> tuple[gpd.GeoDataFrame, dict]:
    out = inp.copy()
    out["cat_cascade"] = out["cat_proposed"]
    area = out[out["conflated"].astype(bool) & out["cat_proposed"].notna()]
    strokes = street_strokes(area, rules)
    pairs = street_pairs(area, rules)
    new, trace = harmonise_all(strokes, pairs, dict(zip(area["segment_id"], area["cat_proposed"])),
                               dict(zip(area["segment_id"], area["length_m"])), rules, locked=locked)
    idx = area.index
    out.loc[idx, "cat_proposed"] = area["segment_id"].map(new).to_numpy()
    names = dict(zip(area["segment_id"], area["name"]))
    traces, paths = [], []
    for sid, t, p, conf in zip(out["segment_id"], out["rule_trace"], out["rule_path"], out["confidence"]):
        steps = trace.get(sid)
        if not steps:
            traces.append(t)
            paths.append(p)
            continue
        rids = list(dict.fromkeys(s["id"] for s in steps))
        added = [_trace_step(r, [s for s in steps if s["id"] == r], conf, names) for r in rids]
        traces.append(json.dumps([*json.loads(t), *added], ensure_ascii=False))
        paths.append(" → ".join([p, *rids]))
    out["rule_trace"], out["rule_path"] = traces, paths
    return out, {"strokes": strokes, "pairs": pairs, "trace": trace}


def mixed_pairs(out: gpd.GeoDataFrame, pairs: list[dict], locked: set[str]) -> list[dict]:
    """Pairs that still have GOW30 on one side and GOW50 on the other, without an approved override."""
    cat = dict(zip(out["segment_id"], out["cat_proposed"]))
    return [p for p in pairs if {cat.get(p["a"]), cat.get(p["b"])} == {"GOW30", "GOW50"}
            and not {p["a"], p["b"]} & locked]


def gow50_islands(out: gpd.GeoDataFrame, strokes: list[list[str]], min_m: float) -> list[list[str]]:
    """GOW50 runs of at least min_m between two GOW30 runs on one street (what H-STR-01 leaves for the review)."""
    cat = dict(zip(out["segment_id"], out["cat_proposed"]))
    length = dict(zip(out["segment_id"], out["length_m"]))
    found = []
    for stroke in strokes:
        runs = _runs([s for s in stroke if s in cat], lambda s: cat[s])
        for i in range(1, len(runs) - 1):
            k, sids = runs[i]
            if (k == "GOW50" and runs[i - 1][0] == runs[i + 1][0] == "GOW30"
                    and sum(length[s] for s in sids) >= min_m):
                found.append(sids)
    return found


def island_table(out: gpd.GeoDataFrame, islands: list[list[str]]) -> gpd.GeoDataFrame:
    """One row per island: street, length, and the inputs of C-G30-01/02 that kept it at 50."""
    by_id = out.set_index("segment_id")
    rows, geoms = [], []
    for sids in islands:
        g = by_id.loc[sids]
        bus = g["bus_route"].astype("boolean")
        rows.append({"name": g["name"].dropna().iloc[0] if g["name"].notna().any() else "–",
                     "bezirk": g["bezirk"].mode().iloc[0] if g["bezirk"].notna().any() else "–",
                     "length_m": round(float(g["length_m"].sum())), "segments": len(sids),
                     "bus_route_share": round(float(g.loc[bus.fillna(False).astype(bool), "length_m"].sum() / g["length_m"].sum()), 2),
                     "school_or_kita_access_m_min": None if g["school_or_kita_access_m"].isna().all() else round(float(g["school_or_kita_access_m"].min())),
                     "shop_frontage_share_max": None if g["shop_frontage_share"].isna().all() else round(float(g["shop_frontage_share"].max()), 2),
                     "width_p10_m_min": None if g["width_p10_m"].isna().all() else round(float(g["width_p10_m"].min()), 1),
                     "confidence_low": int((g["confidence"] == "low").sum()),
                     "segment_ids": ",".join(sids)})
        geoms.append(shapely.line_merge(shapely.union_all(g.geometry.to_numpy())))
    return gpd.GeoDataFrame(rows, geometry=geoms, crs=WORK_CRS).sort_values("length_m", ascending=False, ignore_index=True)


def run_checks(inp, out, rules, pairs: list[dict] | None = None, locked: set[str] = frozenset()) -> list[dict]:
    area = out["conflated"].astype(bool)
    locked_cats = set(rules.harmonisation.rule(RULE_ID).locked_categories)
    touched_locked = out.loc[area & out["cat_cascade"].isin(locked_cats)]
    return [
        {"name": "segment_id unverändert", "ok": list(out["segment_id"]) == list(inp["segment_id"]),
         "detail": f"{len(out)} Abschnitte"},
        {"name": "gesperrte Kategorien unverändert", "ok": bool((touched_locked["cat_proposed"] == touched_locked["cat_cascade"]).all()),
         "detail": ", ".join(sorted(locked_cats))},
        {"name": "Kategorien gültig", "ok": bool(out.loc[area, "cat_proposed"].isin(set(rules.categories)).all()),
         "detail": f"{int(area.sum())} Abschnitte im Arbeitsgebiet"},
        {"name": "Richtungsfahrbahnen gleich (H-PAIR-01)", "ok": not mixed_pairs(out, pairs or [], locked),
         "detail": f"{len(pairs or [])} Paare, {len(mixed_pairs(out, pairs or [], locked))} mit GOW30 und GOW50"},
    ]


def _km(m: float) -> str:
    return f"{m / 1000:.1f}".replace(".", ",")


def write_report(out: gpd.GeoDataFrame, res: dict, rules, districts: list[str], checks: list[dict],
                 islands: gpd.GeoDataFrame) -> None:
    pilot = area_label(districts)
    area = out[out["conflated"].astype(bool) & out["cat_proposed"].notna()]
    ch = area[area["cat_proposed"] != area["cat_cascade"]]
    pch = ch[ch["bezirk"].isin(districts)]
    min_run = rules.coherence_rule("N2").param("min_run_m")
    lines = ["# Harmonisierung je Straßenzug – Stufe 5b", "",
             f"Erzeugt: {_now()} von `pipeline/s05b_harmonise.py`, rules.yaml {rules.meta.version}. Nicht amtlicher Entwurf.", "",
             f"Regel H-STR-01: kurze Läufe unter {min_run:g} m (N2) auf einem Straßenzug werden angeglichen; bei 50 gegen 30 "
             "gewinnt das niedrigere Tempo. Lückenschluss: ein GOW50-Lauf zwischen zwei GOW30-Läufen wird GOW30, wenn er "
             f"kürzer als gap_close_m = {rules.harmonisation.rule('H-STR-01').thresholds['gap_close_m'].value:g} m ist "
             "(F07, StVO-Novelle 2024, Fassung prüfen). Straßenzug wie N2 (Knoten mit Grad 2 laufen weiter, an Kreuzungen der "
             "gegenseitig beste Partner mit höchstens 30° Richtungsänderung).", "",
             "Regel H-PAIR-01 (seit 0.23.0): getrennt gezeichnete Richtungsfahrbahnen derselben Straße bekommen dasselbe "
             "Tempo; ist eine Seite GOW30, wird die GOW50-Seite GOW30. Danach gleicht H-STR-01 erneut an.", "",
             "## Prüfungen", "", "| Prüfung | Ergebnis | Detail |", "| --- | --- | --- |",
             *[f"| {c['name']} | {'ok' if c['ok'] else 'FEHLER'} | {c['detail']} |" for c in checks], "",
             "## Kennzahlen", "",
             f"- Straßenzüge: {_fmt(len(res['strokes']))}; geänderte Abschnitte: {_fmt(len(ch))} ({_km(ch['length_m'].sum())} km) "
             f"im Arbeitsgebiet, davon {_fmt(len(pch))} ({_km(pch['length_m'].sum())} km) in {pilot}.", "",
             "| Wechsel | Abschnitte | km |", "| --- | ---: | ---: |"]
    for (f, t), g in ch.groupby(["cat_cascade", "cat_proposed"]):
        lines.append(f"| {f} → {t} | {_fmt(len(g))} | {_km(g['length_m'].sum())} |")
    lines += ["", "| Bezirk | geänderte Abschnitte | km | Anteil an der Länge im Bezirk |", "| --- | ---: | ---: | ---: |"]
    for bz, g in pch.groupby("bezirk"):
        share = g["length_m"].sum() / area.loc[area["bezirk"] == bz, "length_m"].sum()
        lines.append(f"| {bz} | {_fmt(len(g))} | {_km(g['length_m'].sum())} | {f'{100 * share:.1f}'.replace('.', ',')} % |")
    step_of = {sid: steps[-1].get("step", "P") for sid, steps in res["trace"].items()}
    lines += ["", "Letzter Schritt je geändertem Abschnitt:", "", "| Schritt | Abschnitte |", "| --- | ---: |"]
    counts = pd.Series([step_of[s] for s in ch["segment_id"]]).value_counts()
    for k, v in sorted(counts.items(), key=lambda kv: str(kv[0])):
        lines.append(f"| {k}: {STEP_TEXT[k]} | {_fmt(v)} |")
    lines += ["", "km je Kategorie im Arbeitsgebiet vorher (Kaskade) und nachher:", "",
              "| Kategorie | Kaskade km | harmonisiert km |", "| --- | ---: | ---: |"]
    for c in rules.categories:
        a, b = area.loc[area["cat_cascade"] == c, "length_m"].sum(), area.loc[area["cat_proposed"] == c, "length_m"].sum()
        if a or b:
            lines.append(f"| {c} | {_km(a)} | {_km(b)} |")
    lines += pair_section(out, res, ch)
    names = (pch.assign(name=pch["name"].fillna("–")).groupby(["bezirk", "name"])["length_m"].agg(["count", "sum"])
             .sort_values("sum", ascending=False))
    lines += ["", f"Straßen mit den meisten geänderten km in {pilot}:", "", "| Bezirk | Straße | Abschnitte | km |",
              "| --- | --- | ---: | ---: |",
              *[f"| {b} | {n} | {int(r['count'])} | {_km(r['sum'])} |" for (b, n), r in names.head(20).iterrows()]]
    viewers = load_viewers()
    pick = list(sample_by_district(pch, SAMPLE_SIZE, SAMPLE_SEED).index)
    lines += ["", f"## Stichprobe: {len(pick)} zufällige geänderte Abschnitte in {pilot}, nach Bezirk geschichtet (Seed {SAMPLE_SEED})", "",
              "| segment_id | Bezirk | Straße | highway | Kaskade | neu | Schritt | Lauf m | Orthophoto | Panoramax | OSM |",
              "| --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |"]
    for i in pick:
        r = out.loc[i]
        mid = r.geometry.interpolate(0.5, normalized=True)
        wgs = gpd.GeoSeries([mid], crs=WORK_CRS).to_crs(4326).iloc[0]
        last = res["trace"][r["segment_id"]][-1]
        run_m = f"{last['run_m']:.0f}" if "run_m" in last else "–"
        lines.append(f"| `{r['segment_id']}` | {r['bezirk']} | {r['name'] if isinstance(r['name'], str) else '–'} | {r['highway']} | "
                     f"{r['cat_cascade']} | {r['cat_proposed']} | {last.get('step', 'P')} | {run_m} | "
                     f"[DOP]({orthophoto_link(mid, viewers)}) | [Bilder]({panoramax_link(wgs, viewers)}) | "
                     f"[Way]({osm_way_link(r['osm_way_ids'][0])}) |")
    lines += island_section(islands, rules, viewers)
    lines += ["", "## Lizenz", "", "Abschnitte aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0.", ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def pair_section(out: gpd.GeoDataFrame, res: dict, ch: gpd.GeoDataFrame) -> list[str]:
    cat = dict(zip(out["segment_id"], out["cat_proposed"]))
    pairs = [p for p in res["pairs"] if cat.get(p["a"]) in GOW and cat.get(p["b"]) in GOW]
    in_pairs = {s for p in pairs for s in (p["a"], p["b"])}
    length = dict(zip(out["segment_id"], out["length_m"]))
    paired = [s for s, steps in res["trace"].items() if any(t["id"] == PAIR_RULE_ID for t in steps)]
    paired_km = sum(length[s] for s in paired) / 1000
    lines = ["", "### Richtungsfahrbahnen (H-PAIR-01)", "",
             f"- Paare getrennter Richtungsfahrbahnen (GOW, beide oneway, gleicher Name): {_fmt(len(pairs))} mit "
             f"{_fmt(len(in_pairs))} Abschnitten ({_km(sum(length[s] for s in in_pairs))} km).",
             f"- durch H-PAIR-01 GOW50 → GOW30: {_fmt(len(paired))} Abschnitte ({f'{paired_km:.1f}'.replace('.', ',')} km); "
             "weitere Abschnitte kann H-STR-01 danach angleichen.",
             f"- Abstand der Paare (Median): {f'{pd.Series([p['dist_m'] for p in pairs]).median():.1f}'.replace('.', ',') if pairs else '–'} m.", ""]
    if paired:
        sub = out[out["segment_id"].isin(paired)]
        top = sub.assign(name=sub["name"].fillna("–")).groupby("name")["length_m"].agg(["count", "sum"]).sort_values("sum", ascending=False)
        lines += ["| Straße | Abschnitte | km |", "| --- | ---: | ---: |",
                  *[f"| {n} | {int(r['count'])} | {_km(r['sum'])} |" for n, r in top.head(20).iterrows()]]
    return lines


def island_section(islands: gpd.GeoDataFrame, rules, viewers) -> list[str]:
    gap = rules.harmonisation.rule(RULE_ID).thresholds["gap_close_m"].value
    lines = ["", f"## Prüfliste: GOW50-Inseln ab {gap:g} m zwischen GOW30", "",
             f"{_fmt(len(islands))} Läufe mit {_fmt(int(islands['segments'].sum()) if len(islands) else 0)} Abschnitten "
             f"({_km(islands['length_m'].sum() if len(islands) else 0)} km). H-STR-01 schließt nur Lücken unter "
             f"gap_close_m = {gap:g} m (StVO § 45 Abs. 9, Fassung prüfen); längere Läufe bleiben GOW50, weil kein Auslöser "
             "von C-G30-01/02 greift (Schule/Kita, Publikumsnutzung, Breite). Fachliche Entscheidung je Lauf über "
             "`overrides/overrides.csv` (review_status = approved). Karte: `reports/harmonisation_gow50_islands.geojson` "
             "(EPSG:4326).", "",
             "| Straße | Bezirk | Länge m | Abschnitte | Anteil Buslinie | Schule/Kita min. m | Publikumsnutzung max. | "
             "Breite p10 min. m | low | Orthophoto | Panoramax |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |"]
    mids = islands.geometry.interpolate(0.5, normalized=True)

    def f(v, d=0):
        return "–" if v is None or pd.isna(v) else f"{v:.{d}f}".replace(".", ",")
    for (_, r), mid, mid_wgs in zip(islands.iterrows(), mids, mids.to_crs(4326)):
        lines.append(f"| {r['name']} | {r['bezirk']} | {_fmt(r['length_m'])} | {r['segments']} | {f(100 * r['bus_route_share'])} % | "
                     f"{f(r['school_or_kita_access_m_min'])} | {f(r['shop_frontage_share_max'], 2)} | "
                     f"{f(r['width_p10_m_min'], 1)} | {r['confidence_low']} | [DOP]({orthophoto_link(mid, viewers)}) | "
                     f"[Bilder]({panoramax_link(mid_wgs, viewers)}) |")
    return lines


def write_islands(islands: gpd.GeoDataFrame) -> None:
    ISLANDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    islands.to_crs(4326).to_file(ISLANDS_PATH, driver="GeoJSON", COORDINATE_PRECISION=6)


def main() -> int:
    rules = load_rules()
    districts = district_names()
    if not IN_PATH.exists():
        print("harmonise: data/interim/classified.parquet missing; run `make classify` first", file=sys.stderr)
        return 1
    inp = gpd.read_parquet(IN_PATH)
    locked = approved_override_ids()
    out, res = apply(inp, rules, locked)
    checks = run_checks(inp, out, rules, res["pairs"], locked)
    area = out[out["conflated"].astype(bool) & out["cat_proposed"].notna()]
    islands = island_table(area, gow50_islands(area, res["strokes"],
                                               rules.harmonisation.rule(RULE_ID).thresholds["gap_close_m"].value))
    write_report(out, res, rules, districts, checks, islands)
    write_islands(islands)
    for c in checks:
        print(f"harmonise: {c['name']}: {c['ok']} ({c['detail']})")
    if not all(c["ok"] for c in checks):
        print(f"harmonise: check(s) failed, outputs not written; see {REPORT_PATH}", file=sys.stderr)
        return 1
    out.to_parquet(OUT_PATH, index=False)
    n = int((out["cat_cascade"].notna() & (out["cat_proposed"] != out["cat_cascade"])).sum())
    print(f"harmonise: {n} segments changed -> {OUT_PATH.relative_to(REPO_ROOT)}, {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
