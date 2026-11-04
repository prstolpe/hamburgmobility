"""Stage 5b: harmonise categories along streets (H-STR-01), after the cascade and before network coherence.

Usage: uv run python -m pipeline.s05b_harmonise   (part of make classify)

Reads data/interim/classified.parquet and writes data/interim/harmonised.parquet with
  cat_cascade   result of the cascade (stage 5)
  cat_proposed  harmonised category (input of coherence, overrides, discrepancy)
and a rule_trace step H-STR-01 for every changed segment, plus reports/harmonisation.md with 30 random
changed segments in the pilot district. Segments with an approved override are not changed.
"""

import json
import random
import sys

import geopandas as gpd
import pandas as pd
import yaml

from pipeline.lib import coherence as coh
from pipeline.lib.crs import WORK_CRS
from pipeline.lib.harmonise import RULE_ID, harmonise
from pipeline.lib.links import load_viewers, orthophoto_link, osm_way_link, panoramax_link
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.overrides import read_overrides
from pipeline.lib.rules import load_rules
from pipeline.s04_features import _fmt, _now

PROJECT_PATH = REPO_ROOT / "config" / "project.yaml"
IN_PATH = REPO_ROOT / "data" / "interim" / "classified.parquet"
OUT_PATH = REPO_ROOT / "data" / "interim" / "harmonised.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "harmonisation.md"
SAMPLE_SIZE = 30
SAMPLE_SEED = 42
STEP_TEXT = {1: "ETW30-Insel in GOW → GOW", 2: "GOW-Insel in ETW30 → ETW30", 3: "GOW50-Insel in GOW30 → GOW30",
             4: "GOW30 auf Mindestlänge verlängert"}


def approved_override_ids() -> set[str]:
    ov = read_overrides()
    return set(ov.loc[ov["review_status"] == "approved", "segment_id"])


def street_strokes(area: gpd.GeoDataFrame, rules, cat_col: str = "cat_proposed") -> list[list[str]]:
    """Strokes (as N2) over the classified segments of the work area."""
    seg = area[["segment_id", "node_u", "node_v", cat_col, "length_m", "highway", "travel_speed_kmh",
                "geometry"]].rename(columns={cat_col: "cat"})
    return coh.strokes(coh.build_graph(seg, rules), rules)


def apply(inp: gpd.GeoDataFrame, rules, locked: set[str]) -> tuple[gpd.GeoDataFrame, dict]:
    out = inp.copy()
    out["cat_cascade"] = out["cat_proposed"]
    area = out[out["conflated"].astype(bool) & out["cat_proposed"].notna()]
    strokes = street_strokes(area, rules)
    new, trace = harmonise(strokes, dict(zip(area["segment_id"], area["cat_proposed"])),
                           dict(zip(area["segment_id"], area["length_m"])), rules, locked=locked)
    idx = area.index
    out.loc[idx, "cat_proposed"] = area["segment_id"].map(new).to_numpy()
    traces, paths = [], []
    for sid, t, p, conf in zip(out["segment_id"], out["rule_trace"], out["rule_path"], out["confidence"]):
        steps = trace.get(sid)
        if not steps:
            traces.append(t)
            paths.append(p)
            continue
        last = steps[-1]
        step = {"id": RULE_ID, "passed": True, "result": True, "confidence": conf,
                "inputs": {"from_cat": steps[0]["from"], "to_cat": last["to"], "run_m": last["run_m"],
                           "neighbours": " und ".join(n for n in last["neighbours"] if n) or "–",
                           "step": last["step"], "pass": last["pass"]}}
        traces.append(json.dumps([*json.loads(t), step], ensure_ascii=False))
        paths.append(f"{p} → {RULE_ID}")
    out["rule_trace"], out["rule_path"] = traces, paths
    return out, {"strokes": strokes, "trace": trace}


def run_checks(inp, out, rules) -> list[dict]:
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
    ]


def _km(m: float) -> str:
    return f"{m / 1000:.1f}".replace(".", ",")


def write_report(out: gpd.GeoDataFrame, res: dict, rules, pilot: str, checks: list[dict]) -> None:
    area = out[out["conflated"].astype(bool) & out["cat_proposed"].notna()]
    ch = area[area["cat_proposed"] != area["cat_cascade"]]
    pch = ch[ch["bezirk"] == pilot]
    min_run = rules.coherence_rule("N2").param("min_run_m")
    lines = ["# Harmonisierung je Straßenzug – Stufe 5b", "",
             f"Erzeugt: {_now()} von `pipeline/s05b_harmonise.py`, rules.yaml {rules.meta.version}. Nicht amtlicher Entwurf.", "",
             f"Regel H-STR-01: kurze Läufe unter {min_run:g} m (N2) auf einem Straßenzug werden angeglichen; bei 50 gegen 30 "
             "gewinnt das niedrigere Tempo. Straßenzug wie N2 (Knoten mit Grad 2 laufen weiter, an Kreuzungen der "
             "gegenseitig beste Partner mit höchstens 30° Richtungsänderung).", "",
             "## Prüfungen", "", "| Prüfung | Ergebnis | Detail |", "| --- | --- | --- |",
             *[f"| {c['name']} | {'ok' if c['ok'] else 'FEHLER'} | {c['detail']} |" for c in checks], "",
             "## Kennzahlen", "",
             f"- Straßenzüge: {_fmt(len(res['strokes']))}; geänderte Abschnitte: {_fmt(len(ch))} ({_km(ch['length_m'].sum())} km) "
             f"im Arbeitsgebiet, davon {_fmt(len(pch))} ({_km(pch['length_m'].sum())} km) im Bezirk {pilot}.", "",
             "| Wechsel | Abschnitte | km |", "| --- | ---: | ---: |"]
    for (f, t), g in ch.groupby(["cat_cascade", "cat_proposed"]):
        lines.append(f"| {f} → {t} | {_fmt(len(g))} | {_km(g['length_m'].sum())} |")
    step_of = {sid: steps[-1]["step"] for sid, steps in res["trace"].items()}
    lines += ["", "| Schritt | Abschnitte |", "| --- | ---: |"]
    for k, v in pd.Series([step_of[s] for s in ch["segment_id"]]).value_counts().sort_index().items():
        lines.append(f"| {k}: {STEP_TEXT[k]} | {_fmt(v)} |")
    lines += ["", "km je Kategorie im Arbeitsgebiet vorher (Kaskade) und nachher:", "",
              "| Kategorie | Kaskade km | harmonisiert km |", "| --- | ---: | ---: |"]
    for c in rules.categories:
        a, b = area.loc[area["cat_cascade"] == c, "length_m"].sum(), area.loc[area["cat_proposed"] == c, "length_m"].sum()
        if a or b:
            lines.append(f"| {c} | {_km(a)} | {_km(b)} |")
    names = pch.assign(name=pch["name"].fillna("–")).groupby("name")["length_m"].agg(["count", "sum"]).sort_values("sum", ascending=False)
    lines += ["", f"Straßen mit den meisten geänderten km im Bezirk {pilot}:", "", "| Straße | Abschnitte | km |", "| --- | ---: | ---: |",
              *[f"| {n} | {int(r['count'])} | {_km(r['sum'])} |" for n, r in names.head(20).iterrows()]]
    viewers = load_viewers()
    rnd = random.Random(SAMPLE_SEED)
    pick = sorted(rnd.sample(list(pch.index), min(SAMPLE_SIZE, len(pch))))
    lines += ["", f"## Stichprobe: {len(pick)} zufällige geänderte Abschnitte im Bezirk {pilot} (Seed {SAMPLE_SEED})", "",
              "| segment_id | Straße | highway | Kaskade | neu | Schritt | Lauf m | Orthophoto | Panoramax | OSM |",
              "| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |"]
    for i in pick:
        r = out.loc[i]
        mid = r.geometry.interpolate(0.5, normalized=True)
        wgs = gpd.GeoSeries([mid], crs=WORK_CRS).to_crs(4326).iloc[0]
        last = res["trace"][r["segment_id"]][-1]
        lines.append(f"| `{r['segment_id']}` | {r['name'] if isinstance(r['name'], str) else '–'} | {r['highway']} | "
                     f"{r['cat_cascade']} | {r['cat_proposed']} | {last['step']} | {last['run_m']:.0f} | "
                     f"[DOP]({orthophoto_link(mid, viewers)}) | [Bilder]({panoramax_link(wgs, viewers)}) | "
                     f"[Way]({osm_way_link(r['osm_way_ids'][0])}) |")
    lines += ["", "## Lizenz", "", "Abschnitte aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0.", ""]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rules = load_rules()
    with open(PROJECT_PATH, encoding="utf-8") as f:
        pilot = yaml.safe_load(f)["pilot_district"]["name"]
    if not IN_PATH.exists():
        print("harmonise: data/interim/classified.parquet missing; run `make classify` first", file=sys.stderr)
        return 1
    inp = gpd.read_parquet(IN_PATH)
    out, res = apply(inp, rules, approved_override_ids())
    checks = run_checks(inp, out, rules)
    write_report(out, res, rules, pilot, checks)
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
