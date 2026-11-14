"""Effect of the rule-consolidation dry runs (prompt 24, A6): compares data/scenarios/redesign/<K>/interim with the
current run in data/interim and reports, by Bezirk, the km and nodes whose
- street category (final.cat_final),
- cycle network category (cycle_network.cycle_cat_final, km of edges),
- cycle facility (cycle_facility.cycle_facility_soll), lane count (cross_section_soll.lanes_per_dir_soll),
  cross-section fit (cross_section_soll.fit_class),
- junction type (junctions.junction_type_final) or deciding row (junctions.decision_rule)
change; with up to five examples (links to site, OSM, orthophoto) and a map (PNG; changed objects as GeoJSON in
EPSG:4326 for visual checks, like the review files in reports/).

Usage: uv run python -m analysis.redesign.consolidation_effects K3 K8 K10 K11 ALL
Writes data/scenarios/redesign/<K>/effect.json, changes.geojson and docs/redesign/img/k-<K>.png.
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from analysis.review_2026_11.common import node_links, seg_links  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "data/interim"
SCEN = ROOT / "data/scenarios/redesign"
IMG = ROOT / "docs/redesign/img"

CHECKS = [  # (file, key, column, unit, label)
    ("final", "segment_id", "cat_final", "km", "Kategorie der Straße"),
    ("cycle_network", "edge_id", "cycle_cat_final", "km", "Radnetzstufe"),
    ("cycle_facility", "segment_id", "cycle_facility_soll", "km", "Art des Radwegs (Ziel)"),
    ("cross_section_soll", "segment_id", "lanes_per_dir_soll", "km", "Fahrstreifen je Richtung (Ziel)"),
    ("cross_section_soll", "segment_id", "fit_class", "km", "Passt der Querschnitt"),
    ("junctions", "node_id", "junction_type_final", "Knoten", "Art der Kreuzung (Ziel)"),
    ("junctions", "node_id", "decision_rule", "Knoten", "entscheidende Zeile der Kreuzungstabelle"),
]


def norm(s: pd.Series) -> pd.Series:
    return s.astype(object).where(s.notna(), "∅").astype(str)  # None/NaN compare equal to each other


def effect(name: str) -> dict:
    sdir = SCEN / name / "interim"
    for stale in (SCEN / name / "changes.geojson", IMG / f"k-{name}.png"):
        stale.unlink(missing_ok=True)
    out = {"scenario": name, "checks": []}
    changed_geo = []
    for f, key, col, unit, label in CHECKS:
        cols = [key, col, "bezirk", "geometry"] + (["length_m"] if unit == "km" else [])
        a = gpd.read_parquet(BASE / f"{f}.parquet", columns=cols)
        b = pd.read_parquet(sdir / f"{f}.parquet", columns=[key, col])
        m = a.merge(b, on=key, how="outer", suffixes=("_a", "_b"), indicator=True)
        diff = m[(norm(m[f"{col}_a"]) != norm(m[f"{col}_b"])) | (m["_merge"] != "both")]
        rec = {"file": f, "column": col, "label": label, "unit": unit, "n": int(len(diff))}
        if unit == "km":
            rec["km"] = round(float(diff.length_m.fillna(0).sum()) / 1000, 2)
            rec["by_bezirk"] = (diff.groupby("bezirk").length_m.sum() / 1000).round(2).to_dict()
        else:
            rec["by_bezirk"] = diff.groupby("bezirk").size().to_dict()
        pairs = (diff[f"{col}_a"].astype(str) + " → " + diff[f"{col}_b"].astype(str)).value_counts().head(6)
        rec["transitions"] = pairs.to_dict()
        ex = []
        for r in diff.head(5).itertuples():
            g = r.geometry
            if g is None:
                continue
            if key == "node_id":
                link = node_links(getattr(r, key), g)
            elif key == "segment_id":
                link = seg_links(getattr(r, key), g)
            else:  # cycle network edge: the site has no page per edge, keep OSM and orthophoto
                link = f"`{getattr(r, key)}` · " + " · ".join(seg_links(str(getattr(r, key)), g).split(" · ")[1:])
            ex.append({"id": getattr(r, key), "from": getattr(r, f"{col}_a"), "to": getattr(r, f"{col}_b"), "links": link})
        rec["examples"] = ex
        out["checks"].append(rec)
        if len(diff) and not col == "decision_rule":
            g = gpd.GeoDataFrame(diff[[key, f"{col}_a", f"{col}_b", "bezirk", "geometry"]].rename(columns={key: "id"}),
                                 geometry="geometry", crs=a.crs)
            g["what"] = label
            changed_geo.append(g)
    d = SCEN / name
    if changed_geo:
        allg = pd.concat(changed_geo, ignore_index=True)
        allg = gpd.GeoDataFrame(allg, geometry="geometry", crs=changed_geo[0].crs)
        allg.astype({c: str for c in allg.columns if c not in ("geometry",)}).to_crs(4326).to_file(d / "changes.geojson", driver="GeoJSON")
        fig, ax = plt.subplots(figsize=(7, 6), dpi=110)
        bz = gpd.read_file(ROOT / "data/out/districts.geojson").to_crs(25832)
        bz.boundary.plot(ax=ax, color="#999999", linewidth=0.6)
        for what, gg in allg.groupby("what"):
            gg.to_crs(25832).plot(ax=ax, linewidth=2.5, markersize=12, label=what)
        ax.set_axis_off()
        ax.legend(loc="lower left", fontsize=8, frameon=False)
        ax.set_title(f"{name}: geänderte Objekte", fontsize=10, loc="left")
        fig.tight_layout()
        fig.savefig(IMG / f"k-{name}.png")
        plt.close(fig)
        out["map"] = f"img/k-{name}.png"
    (d / "effect.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out


def main():
    for name in sys.argv[1:]:
        e = effect(name)
        print(name, [(c["label"], c["n"], c.get("km")) for c in e["checks"]])


if __name__ == "__main__":
    main()
