"""Phase 2b: conflict typology cycle network <-> street network, counted on one state (data/interim of a run).

K1 RSV/HAUPT on GOW50 without space for separated tracks (fit_class does_not_fit)
K2 Soll cycle street on ETW30 with too much motor traffic: DTV > cycle_street.max_motor_vehicles_day, or bus service
   (no DTV on ETW30: bus_trips_weekday > 0 as a known indicator), or flag mixed_over_s04
K3 RSV/HAUPT crossing GOW50 at a junction without a suitable type (not signal/grade separated/roundabout/
   cycle crossing with priority)
K4 Category change GOW30 <-> GOW50 along RSV/HAUPT routes (number of changes per route)
K5 Detour above the P-DIR-01 threshold on RSV/HAUPT/BASIS routes (P-ATT-03 alternatives counted separately)
K6 Degrade cascade D5/D7 on the cycle network (route should move / category should change, but stays)
K7 Existing separated track on an ETW30 main route (flag track_on_access_road: street category vs. route type)
Usage: python -m analysis.review_2026_11.conflicts_2b <interim_dir> <out_json>
"""

import json
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
SUITABLE_GOW50_CROSSING = {"signal_protected", "grade_separated_cycle", "roundabout_single_lane_cycle_priority",
                           "turbo_roundabout", "cycle_crossing_priority"}
TOP = {"RSV", "HAUPT"}


def km(s: pd.Series) -> float:
    return round(float(s.sum()) / 1000, 1)


def has(series: pd.Series, token: str) -> pd.Series:
    return series.fillna("").astype(str).str.split("|").map(lambda x: token in x)


def count(interim: Path) -> dict:
    cyc = yaml.safe_load((ROOT / "config/cycling_rules.yaml").read_text(encoding="utf-8"))
    det_thr = next(x for x in cyc["principles"]["directness"]["checks"] if x["id"] == "P-DIR-01")["thresholds"] \
        if "principles" in cyc and isinstance(cyc["principles"], dict) and "directness" in cyc["principles"] else \
        {"RSV": 1.1, "HAUPT": 1.2, "BASIS": 1.3}
    street_max = float(cyc["cycle_street"]["max_motor_vehicles_day"]["value"])
    x = pd.read_parquet(interim / "cross_section_soll.parquet",
                        columns=["segment_id", "length_m", "cat_final", "cycle_cat_final", "fit_class",
                                 "degrade_steps_applied", "cat_change_proposal", "bezirk"])
    f = pd.read_parquet(interim / "cycle_facility.parquet",
                        columns=["segment_id", "cycle_facility_soll", "facility_flags", "dtv_official"])
    seg = pd.read_parquet(interim / "final.parquet", columns=["segment_id", "bus_trips_weekday", "name"])
    s = x.merge(f, on="segment_id", how="left").merge(seg, on="segment_id", how="left")
    top = s.cycle_cat_final.isin(TOP)
    res = {}

    k1 = top & (s.cat_final == "GOW50") & (s.fit_class == "does_not_fit")
    res["K1"] = {"km": km(s.length_m[k1]), "segments": int(k1.sum()),
                 "km_top_on_gow50": km(s.length_m[top & (s.cat_final == "GOW50")])}

    cs = (s.cycle_facility_soll == "cycle_street") & (s.cat_final == "ETW30")
    over = cs & (s.dtv_official > street_max)
    bus = cs & (s.bus_trips_weekday.fillna(0) > 0)
    mix = cs & has(s.facility_flags, "mixed_over_s04")
    res["K2"] = {"km_cycle_street_soll": km(s.length_m[cs]), "km_dtv_over": km(s.length_m[over]),
                 "km_with_bus": km(s.length_m[bus]), "km_with_bus_ge_100": km(s.length_m[bus & (s.bus_trips_weekday >= 100)]),
                 "km_mixed_over_s04": km(s.length_m[mix]), "km_dtv_unknown": km(s.length_m[cs & has(s.facility_flags, "dtv_unknown")]),
                 "km_any": km(s.length_m[over | bus | mix])}

    j = pd.read_parquet(interim / "junctions.parquet", columns=["node_id", "pair", "legs", "junction_type_final",
                                                                "top_cycle_cat", "conflict_flags"])
    legs = j.legs.map(json.loads)
    # the route crosses the GOW50: at least two non-GOW50 arms carry RSV/HAUPT (otherwise it only joins it)
    crosses = legs.map(lambda ls: any(l["cat"] == "GOW50" for l in ls) and
                       sum(1 for l in ls if l.get("cycle_cat") in TOP and l["cat"] != "GOW50") >= 2)
    k3 = crosses & ~j.junction_type_final.isin(SUITABLE_GOW50_CROSSING)
    res["K3"] = {"junctions_top_route_crossing_gow50": int(crosses.sum()), "unsuitable_type": int(k3.sum()),
                 "types": j.junction_type_final[k3].value_counts().to_dict()}

    r = pd.read_parquet(interim / "cycle_routes.parquet", columns=["route_id", "category", "length_m", "edge_ids"])
    e = pd.read_parquet(interim / "cycle_network.parquet", columns=["edge_id", "segment_id", "cat_final", "length_m"])
    cat = e.set_index("edge_id").cat_final
    changes = []
    for _, rt in r[r.category.isin(TOP)].iterrows():
        ids = json.loads(rt.edge_ids) if isinstance(rt.edge_ids, str) else list(rt.edge_ids)
        seq = [c for c in cat.reindex(ids).tolist() if c in ("GOW30", "GOW50")]
        changes.append(sum(1 for a, b in zip(seq, seq[1:]) if a != b))
    ch = pd.Series(changes)
    res["K4"] = {"routes": len(ch), "routes_with_change": int((ch > 0).sum()), "changes_total": int(ch.sum()),
                 "routes_ge_3_changes": int((ch >= 3).sum())}

    p = pd.read_parquet(interim / "cycle_principles.parquet", columns=["level", "route_id", "category", "detour",
                                                                       "length_m"])
    p = p[(p.level == "route") & p.detour.notna()]
    thr = p.category.map(det_thr)
    k5 = p.detour > thr
    res["K5"] = {"routes_with_detour_value": len(p), "over_threshold": int(k5.sum()),
                 "by_cat": p[k5].category.value_counts().to_dict(), "km": km(p.length_m[k5])}
    cn = pd.read_parquet(interim / "cycle_network.parquet", columns=["patt_alternative"])
    res["K5"]["patt_alternative_edges"] = int(cn.patt_alternative.fillna(False).sum())

    d5 = has(s.degrade_steps_applied, "D5")
    d7 = has(s.degrade_steps_applied, "D7")
    res["K6"] = {"d7_km": km(s.length_m[d7]), "d7_on_top_km": km(s.length_m[d7 & top]),
                 "d5_proposals_km": km(s.length_m[d5]), "d5_on_top_km": km(s.length_m[d5 & top])}

    k7 = has(s.facility_flags, "track_on_access_road")
    res["K7"] = {"km": km(s.length_m[k7]), "segments": int(k7.sum())}
    return res


def main(interim: str, out_json: str) -> None:
    res = count(Path(interim))
    Path(out_json).write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:3])
