"""District figures and top lists for the redesign prototypes (prompt 24, A3), from the current export in
data/out/downloads (read-only). Replaces prototypes/shared/kpi.json of the review (export 0.16.0) for the redesign.

Writes
- prototypes/redesign/data/districts.json: per Bezirk three key figures (one per theme) and for the focus Bezirk the
  top-5 lists (streets by priority, junctions by priority_rank, cycle network gaps by length x demand), each entry
  with a plain sentence, the profile id and a point to fly to
- prototypes/redesign/data/mesh_gaps.geojson: meshes of the target cycle network wider than planned (focus Bezirk;
  display only, EPSG:4326 like the review files in reports/)

Usage: uv run python -m analysis.redesign.district_data
"""

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DL = ROOT / "data/out/downloads"
OUT = ROOT / "prototypes/redesign/data"
FOCUS = "Eimsbüttel"
TARGET_KMH = {"SW": None, "GOW50": 50, "GOW30": 30, "ETW30": 30, "ETW_ERF": 20}
MAIN = ["RSV", "HAUPT", "BASIS"]


def km(s) -> float:
    return round(float(s.sum()) / 1000, 1)


def point(geom) -> list[float]:
    p = gpd.GeoSeries([geom], crs=25832).to_crs(4326).iloc[0]
    p = p.interpolate(0.5, normalized=True) if p.geom_type != "Point" else p
    return [round(p.x, 6), round(p.y, 6)]


def de(x, nd=0):
    return f"{x:,.{nd}f}".replace(",", " ").replace(".", ",")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = json.loads((ROOT / "data/out/meta.json").read_text(encoding="utf-8"))
    seg = gpd.read_parquet(DL / "segments.parquet").to_crs(25832)
    cyc = gpd.read_parquet(DL / "cycle_segments.parquet").to_crs(25832)
    jct = gpd.read_parquet(DL / "junctions.parquet").to_crs(25832)
    net = gpd.read_parquet(DL / "cycle_network.parquet")
    jtext = meta["cycling"]["junction_type"]

    per = {}
    for bz, s in seg.groupby("bezirk"):
        c = cyc[(cyc.bezirk == bz) & cyc.cycle_cat_final.isin(MAIN)]
        j = jct[jct.bezirk == bz]
        per[bz] = {
            "km_total": km(s.length_m),
            "km_need": km(s.loc[s.disc_max >= 2, "length_m"]),
            "km_speed_down": km(s.loc[s.disc_speed >= 1, "length_m"]),
            "km_cycle_main": km(c.length_m),
            "km_cycle_missing": km(c.loc[c.facility_gap == "missing", "length_m"]),
            "km_profile_no_fit": km(cyc.loc[(cyc.bezirk == bz) & (cyc.fit_class == "does_not_fit"), "length_m"]),
            "junctions": int(len(j)),
            "junctions_rebuild": int(j.action_needed.fillna(False).sum()),
        }

    s = seg[(seg.bezirk == FOCUS) & seg.name.notna() & (seg.priority > 0)]
    streets = []
    for name, g in s.sort_values("priority", ascending=False).groupby("name", sort=False):
        top = g.iloc[0]
        tk = TARGET_KMH.get(top.cat_final)
        speed = (f"heute {int(top.speed_ist_kmh)} km/h, Ziel {tk} km/h"
                 if pd.notna(top.speed_ist_kmh) and tk and top.speed_ist_kmh > tk else None)
        crashes = int(g.crashes_ped_cyc.fillna(0).sum())
        sentence = "; ".join(x for x in [speed, f"{crashes} Unfälle mit Fuß- oder Radbeteiligung in 5 Jahren" if crashes else None] if x)
        streets.append({"name": name, "id": top.segment_id, "priority": round(float(top.priority), 2),
                        "km_need": km(g.loc[g.disc_max >= 2, "length_m"]), "label": meta["categories"][top.cat_final]["label"],
                        "sentence": sentence or "Abweichung zwischen heute und Ziel", "at": point(top.geometry)})
        if len(streets) == 5:
            break

    j = jct[(jct.bezirk == FOCUS) & jct.action_needed.fillna(False)].sort_values("priority_rank").head(5)
    junctions = [{"name": r.names, "id": r.node_id, "rank": int(r.priority_rank),
                  "sentence": f"heute {r.junction_type_ist_text}, Ziel {jtext.get(r.junction_type_final, r.junction_type_final)}"
                              + (f"; {int(r.crashes_cyc)} Radunfälle in 5 Jahren" if r.crashes_cyc else ""),
                  "at": point(r.geometry)} for r in j.assign(junction_type_ist_text=j.junction_type_ist.map(
                      lambda x: {"signal": "Ampel", "roundabout": "Kreisverkehr", "plateau": "Aufpflasterung",
                                 "signal_plateau": "Ampel mit Aufpflasterung", "none_mapped": "keine Regelung erfasst"}.get(x, x))).itertuples()]

    demand = net[net.segment_id.notna()].groupby("segment_id").cyc_calibrated.max()
    c = cyc[(cyc.bezirk == FOCUS) & cyc.cycle_cat_final.isin(MAIN) & (cyc.facility_gap == "missing") & cyc.name.notna()].copy()
    c["demand"] = c.segment_id.map(demand).fillna(0)
    c["score"] = c.length_m * c.demand
    gaps = []
    cat_label = meta["cycling"]["cycle_categories"]
    for name, g in c.groupby("name"):
        top = g.sort_values("demand", ascending=False).iloc[0]
        lab = cat_label.get(top.cycle_cat_final, top.cycle_cat_final)
        lab = lab.get("label", top.cycle_cat_final) if isinstance(lab, dict) else lab
        gaps.append({"name": name, "id": top.segment_id, "score": float(g.score.sum()), "km": km(g.length_m),
                     "sentence": f"{de(km(g.length_m), 1)} km {lab} ohne passenden Radweg, bis {de(top.demand)} Radfahrten am Tag (Modell)",
                     "at": point(top.geometry)})
    gaps = sorted(gaps, key=lambda x: -x["score"])[:5]

    bz_geom = gpd.read_file(ROOT / "data/out/districts.geojson")
    bbox = [round(v, 5) for v in bz_geom.loc[bz_geom.name == FOCUS].total_bounds]
    out = {"source": f"data/out/downloads (Version {meta['version']})", "focus": FOCUS, "bbox": bbox,
           "per_bezirk": per, "top": {"streets": streets, "junctions": junctions, "gaps": gaps}}
    (OUT / "districts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    mg = gpd.read_parquet(ROOT / "data/interim/cycle_mesh_gaps.parquet")
    mg = mg[mg.bezirk == FOCUS].copy()
    mg["geometry"] = mg.geometry.simplify(5)  # display only: 5 m is below a pixel at zoom 14
    mg[["side_m", "max_m", "level", "geometry"]].to_crs(4326).to_file(OUT / "mesh_gaps.geojson", driver="GeoJSON",
                                                                     COORDINATE_PRECISION=5)
    print(json.dumps(per[FOCUS], ensure_ascii=False))
    for k, v in out["top"].items():
        print(k, [(x["name"], x["sentence"]) for x in v])
    print(len(mg), "mesh gaps")


if __name__ == "__main__":
    main()
