"""Effect of the junction arm filter (design_rules J-M-01, redesign 2026-11 package 5): current run (data/interim) vs.
dry run (data/scenarios/redesign/<name>/interim). Junctions per Bezirk, dropped and joined pseudo-junctions, changes at
the junctions that stay (type, decision row, space, crashes), orphaned junction overrides, examples with links.

Usage: uv run python -m analysis.redesign.armfilter_effects [name] [after-interim-dir]
  default name armfilter; "before" is data/scenarios/redesign/base/interim, "after" defaults to
  data/scenarios/redesign/<name>/interim (package 5 final: `p5 data/interim`).
Writes data/scenarios/redesign/<name>/effect.json and prints Markdown.
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

from analysis.review_2026_11.common import fmt

ROOT = Path(__file__).resolve().parents[2]
COLS = ["node_id", "member_nodes", "n_members", "legs_count", "junction_type_final", "decision_rule", "space_radius_m",
        "action_needed", "crashes_cyc", "bezirk", "names", "geometry"]


def load(path: Path) -> gpd.GeoDataFrame:
    return gpd.read_parquet(path, columns=COLS).set_index("node_id")


def site_link(nid: str) -> str:
    return f"https://hamburgmobility.de/#karte?theme=knoten&jct={nid}"


def main(name: str = "armfilter", after: str | None = None) -> None:
    d = ROOT / "data" / "scenarios" / "redesign" / name
    d.mkdir(parents=True, exist_ok=True)
    a = load(ROOT / "data/scenarios/redesign/base/interim/junctions.parquet")
    b = load((ROOT / after if after else d / "interim") / "junctions.parquet")
    gone = a.index.difference(b.index)
    new = b.index.difference(a.index)
    stay = a.index.intersection(b.index)
    members_b = {int(n): nid for nid, ms in b["member_nodes"].items() for n in json.loads(ms)}
    joined = [nid for nid in gone if int(nid) in members_b]
    dropped = [nid for nid in gone if int(nid) not in members_b]

    by_bz = pd.DataFrame({"vorher": a.groupby("bezirk").size(), "nachher": b.groupby("bezirk").size(),
                          "angeschlossen": a.loc[joined].groupby("bezirk").size(),
                          "entfallen": a.loc[dropped].groupby("bezirk").size()}).fillna(0).astype(int)
    by_bz.loc["Hamburg"] = by_bz.sum()

    def changed(col):
        x, y = a.loc[stay, col], b.loc[stay, col]
        eq = (x == y) | (x.isna() & y.isna())
        return list(stay[~eq.to_numpy()])

    ch = {c: changed(c) for c in ("junction_type_final", "decision_rule", "space_radius_m", "crashes_cyc", "legs_count",
                                  "action_needed")}
    ov = pd.read_csv(ROOT / "overrides/junction_overrides.csv", dtype=str)
    orphans = sorted(set(ov["node_id"]) - set(b.index)) if len(ov) else []
    lost = a.loc[dropped]
    res = {
        "junctions_before": len(a), "junctions_after": len(b), "joined": len(joined), "dropped": len(dropped),
        "new_ids": len(new), "dropped_action_needed": int(lost["action_needed"].sum()),
        "dropped_crashes_cyc": int(lost["crashes_cyc"].sum()),
        "dropped_by_type": lost["junction_type_final"].value_counts().to_dict(),
        "dropped_legs_count": lost["legs_count"].value_counts().sort_index().to_dict(),
        "changed_at_staying": {k: len(v) for k, v in ch.items()},
        "type_changes": (a.loc[ch["junction_type_final"], "junction_type_final"] + " → "
                         + b.loc[ch["junction_type_final"], "junction_type_final"]).value_counts().to_dict(),
        "orphan_overrides": orphans, "by_bezirk": by_bz.to_dict(orient="index"),
        "examples_type_change": ch["junction_type_final"][:10], "examples_dropped": dropped[:10],
        "examples_joined": joined[:10],
    }
    (d / "effect.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=int), encoding="utf-8")

    print(f"Kreuzungen: {fmt(len(a))} → {fmt(len(b))}; angeschlossen {fmt(len(joined))}, entfallen {fmt(len(dropped))}, "
          f"neue IDs {len(new)}; verwaiste Overrides: {orphans or 'keine'}")
    print("\n| Bezirk | vorher | nachher | angeschlossen | entfallen |\n|---|---:|---:|---:|---:|")
    for bz, r in by_bz.iterrows():
        print(f"| {bz} | {fmt(r.vorher)} | {fmt(r.nachher)} | {fmt(r.angeschlossen)} | {fmt(r.entfallen)} |")
    print("\nEntfallene nach Art (Ziel):", res["dropped_by_type"])
    print("Entfallene mit Umbaubedarf:", res["dropped_action_needed"], "· Radunfälle dort:", res["dropped_crashes_cyc"])
    print("Bleibende Kreuzungen mit Änderung:", res["changed_at_staying"])
    print("Typwechsel:", res["type_changes"])
    for nid in ch["junction_type_final"][:8]:
        print(f"- [{nid}]({site_link(nid)}) {a.at[nid, 'names']}: {a.at[nid, 'junction_type_final']} → "
              f"{b.at[nid, 'junction_type_final']} (Arme {a.at[nid, 'legs_count']} → {b.at[nid, 'legs_count']}, "
              f"Platz {a.at[nid, 'space_radius_m']} → {b.at[nid, 'space_radius_m']})")


if __name__ == "__main__":
    main(*sys.argv[1:3])
