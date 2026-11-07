"""District figures and small data files for the UI prototypes (prompt 21b, phase 3.2/3.3).

Reads data/out/downloads (export 0.16.0), the saved variant data/variants/2026-11-07_gow50-kompromiss
(rules 0.14.0, DTV cap C-G50-02) and data/interim/cycle_mesh_gaps.parquet. Writes
- prototypes/shared/kpi.json: figures per Bezirk (all seven, for comparison) and top lists for Eimsbüttel
- prototypes/shared/scenario_eimsbuettel.json: segments of Eimsbüttel whose category differs in the variant
- prototypes/shared/mesh_gaps_eimsbuettel.geojson: cycle network meshes wider than the target (display only,
  EPSG:4326 like the review files in reports/)
- data/scenarios/review_ui/presentation_stats.json: evidence for the report (feasibility statements, confidence)
Read-only on all inputs.
"""

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DL = ROOT / "data/out/downloads"
VAR = ROOT / "data/variants/2026-11-07_gow50-kompromiss/site/downloads"
SHARED = ROOT / "prototypes/shared"
OUT = ROOT / "data/scenarios/review_ui"
BZ = "Eimsbüttel"
CATS = ["SW", "GOW50", "GOW30", "ETW30", "ETW_ERF"]


def km(s: pd.Series) -> float:
    return round(float(s.sum()) / 1000, 1)


def main() -> None:
    SHARED.mkdir(parents=True, exist_ok=True)
    seg = gpd.read_parquet(DL / "segments.parquet")
    cyc = gpd.read_parquet(DL / "cycle_segments.parquet")
    jct = gpd.read_parquet(DL / "junctions.parquet")
    net = gpd.read_parquet(DL / "cycle_network.parquet")
    gaps = gpd.read_parquet(ROOT / "data/interim/cycle_mesh_gaps.parquet")

    per_bz = {}
    for bz, s in seg.groupby("bezirk"):
        c = cyc[cyc.bezirk == bz]
        j = jct[jct.bezirk == bz]
        n = net[net.bezirk == bz]
        main_routes = c[c.cycle_cat_final.isin(["RSV", "HAUPT", "BASIS"])]
        per_bz[bz] = {
            "km_total": km(s.length_m),
            "km_by_cat": {k: km(s.loc[s.cat_final == k, "length_m"]) for k in CATS},
            "km_discrepancy": km(s.loc[s.disc_type.notna(), "length_m"]),
            "km_disc_strong": km(s.loc[s.disc_max >= 2, "length_m"]),
            "km_speed_too_high": km(s.loc[(s.disc_speed >= 1), "length_m"]),
            "km_high_priority": km(s.loc[s.priority >= 2, "length_m"]),
            "km_low_confidence": km(s.loc[s.confidence == "niedrig", "length_m"]),
            "km_uncertain": km(s.loc[s.sens_uncertain == True, "length_m"]),  # noqa: E712
            "km_cycle_network": {k: km(n.loc[n.cycle_cat_final == k, "length_m"]) for k in ["RSV", "HAUPT", "BASIS"]},
            "km_cycle_facility_missing": km(main_routes.loc[main_routes.facility_gap == "missing", "length_m"]),
            "km_cycle_facility_other": km(main_routes.loc[main_routes.facility_gap.isin(["wrong_type", "too_narrow", "partial"]), "length_m"]),
            "km_profile_does_not_fit": km(c.loc[c.fit_class == "does_not_fit", "length_m"]),
            "junctions": int(len(j)),
            "junctions_rebuild": int(j.action_needed.fillna(False).sum()),
            "mesh_gaps": int((gaps.bezirk == bz).sum()),
            "crashes_ped_cyc": int(s.crashes_ped_cyc.fillna(0).sum()),
        }

    s = seg[seg.bezirk == BZ].copy()
    # Top streets by priority: aggregate per street name (a street = several segments)
    top = (s[s.priority > 0].groupby("name", dropna=True)
           .agg(km=("length_m", lambda x: round(x.sum() / 1000, 2)), priority=("priority", "max"),
                crashes=("crashes_ped_cyc", "sum"), cat=("cat_final", lambda x: x.mode().iat[0]),
                speed=("speed_ist_kmh", "max"), seg=("segment_id", "first"), dt=("disc_type", lambda x: x.mode().iat[0] if x.notna().any() else None))
           .sort_values(["priority", "crashes"], ascending=False).head(10).reset_index())
    # a representative segment per street: the one with the highest priority
    best = s.sort_values("priority", ascending=False).drop_duplicates("name").set_index("name")
    top["seg"] = top.name.map(best.segment_id)
    s4326 = s.to_crs(4326)
    top["bbox"] = [s4326[s4326.name == n].total_bounds.round(5).tolist() for n in top.name]
    tj = jct[(jct.bezirk == BZ) & (jct.action_needed == True)].sort_values("priority_rank").head(10)  # noqa: E712
    top_j = [{"id": str(r.node_id), "names": r.names, "soll": r.junction_type_final, "ist": r.junction_type_ist,
              "rank": int(r.priority_rank), "crashes_cyc": int(r.crashes_cyc or 0),
              "lon": round(r.geometry.x, 6), "lat": round(r.geometry.y, 6)} for r in tj.itertuples()]
    c = cyc[(cyc.bezirk == BZ) & cyc.cycle_cat_final.isin(["RSV", "HAUPT"]) & (cyc.facility_gap == "missing")].to_crs(4326)
    top_c = (c.groupby("name").agg(km=("length_m", lambda x: round(x.sum() / 1000, 2)), seg=("segment_id", "first"),
                                   cc=("cycle_cat_final", "first"))
             .sort_values("km", ascending=False).head(10).reset_index())
    top_c["bbox"] = [c[c.name == n].total_bounds.round(5).tolist() for n in top_c.name]
    bounds = seg[seg.bezirk == BZ].total_bounds.round(5).tolist()
    kpi = {"source": "data/out/downloads (Regelwerk 0.16.0, Datenstand 2026-10-28)", "focus": BZ, "bbox": bounds,
           "per_bezirk": per_bz, "top_streets": top.to_dict("records"), "top_junctions": top_j,
           "top_cycle_missing": top_c.to_dict("records")}
    (SHARED / "kpi.json").write_text(json.dumps(kpi, ensure_ascii=False, indent=1, default=str))

    # scenario: variant with DTV cap (rules 0.14.0) vs current export
    v = pd.read_parquet(VAR / "segments.parquet", columns=["segment_id", "cat_final", "rule_path"])
    m = s[["segment_id", "name", "length_m", "cat_final", "dtv_official"]].merge(v, on="segment_id", suffixes=("", "_var"))
    d = m[m.cat_final != m.cat_final_var]
    scen = {"label_current": "Regelwerk 0.16.0 (heute veröffentlicht)",
            "label_variant": "Variante „GOW50-Kompromiss“ (Regelwerk 0.14.0, Verkehrsmenge als Grenze, Regel C-G50-02)",
            "km_changed": km(d.length_m),
            "pairs_km": {f"{a}->{b}": km(g.length_m) for (a, b), g in d.groupby(["cat_final", "cat_final_var"])},
            "segments": {r.segment_id: r.cat_final_var for r in d.itertuples()}}
    (SHARED / "scenario_eimsbuettel.json").write_text(json.dumps(scen, ensure_ascii=False))

    g = gaps[gaps.bezirk == BZ].to_crs(4326)
    g["geometry"] = g.geometry.simplify(0.00005)
    g[["level", "side_m", "max_m", "geometry"]].round({"side_m": 0, "max_m": 0}).to_file(SHARED / "mesh_gaps_eimsbuettel.geojson", driver="GeoJSON")

    # evidence: two feasibility statements per profile (street cross-section vs cycling Soll profile)
    feas_col = {"GOW50": "feasibility_GOW50", "GOW30": "feasibility_GOW30_narrow", "ETW30": "feasibility_ETW30"}
    seg["feas_own"] = [r[feas_col[r.cat_final]] if r.cat_final in feas_col else None for _, r in seg.iterrows()]
    j2 = seg[["segment_id", "length_m", "cat_final", "feas_own"]].merge(cyc[["segment_id", "fit_class"]], on="segment_id")
    both = j2[j2.feas_own.notna() & j2.fit_class.notna()]
    street_ok = both.feas_own.isin(["fits", "tight"])
    contra = both[(street_ok & (both.fit_class == "does_not_fit")) | (~street_ok & (both.fit_class == "fits"))]
    stats = {
        "profiles_with_both_statements": int(len(both)), "km_both": km(both.length_m),
        "km_contradicting": km(contra.length_m), "segments_contradicting": int(len(contra)),
        "contradicting_by_pair_km": {f"{a} / {b}": km(x.length_m) for (a, b), x in contra.groupby(["feas_own", "fit_class"])},
        "examples": contra.sort_values("length_m", ascending=False).head(5)[["segment_id", "cat_final", "feas_own", "fit_class"]].to_dict("records"),
        "confidence_km": {k: km(seg.loc[seg.confidence == k, "length_m"]) for k in ["hoch", "mittel", "niedrig"]},
        "uncertain_km": km(seg.loc[seg.sens_uncertain == True, "length_m"]),  # noqa: E712
        "segment_json_kb": None,
        "mesh_gaps_total": int(len(gaps)), "mesh_gaps_by_level": gaps.level.value_counts().to_dict(),
    }
    # evidence: two statements about today's cycling facility (street discrepancy: OSM tags on the carriageway
    # segment; cycling part: cycle_facility_ist incl. matched side paths)
    ist = seg[["segment_id", "length_m", "separated_cycle_track_present", "cycle_lane_present"]].merge(
        cyc[["segment_id", "cycle_facility_ist"]], on="segment_id")
    none_vs_fac = ist[(ist.cycle_lane_present == False) & (ist.separated_cycle_track_present == False)  # noqa: E712
                      & ist.cycle_facility_ist.isin(["cycle_lane", "separated_oneway_both", "separated_twoway"])]
    stats["ist_cycling_contradicting"] = {"segments": int(len(none_vs_fac)), "km": km(none_vs_fac.length_m),
                                          "examples": none_vs_fac.sort_values("length_m", ascending=False).segment_id.head(5).tolist()}
    sizes = [p.stat().st_size for p in (ROOT / "data/out/segments").glob("*.json")]
    stats["segment_json_kb"] = {"median": round(sorted(sizes)[len(sizes) // 2] / 1024, 1), "max": round(max(sizes) / 1024, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "presentation_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1, default=str))
    print(json.dumps({"eims": per_bz[BZ], "scenario": {k: scen[k] for k in ["km_changed", "pairs_km"]}, "stats": stats}, ensure_ascii=False, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
