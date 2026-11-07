"""Phase 2c: quality check of the junctions (data/interim/junctions.parquet, design_rules.yaml 0.6.0).

Q1 clustering: too large (extent > 2 x cluster_radius_m), too many members; too small: separate junction points
   closer than cluster_radius_m to each other (candidates for one junction)
Q2 arms: legs_count < 3 at a junction of the street graph (degree >= 3 expected), legs vs. carriageway legs
Q3 implausible types: roundabout with space_unknown or space below roundabout_min_radius, roundabout with entering DTV
   above roundabout_max_dtv, signal at ETW30+ETW30, Soll roundabout where OSM shows a signal (and vice versa)
Q4 Ist type from OSM: share none_mapped, OSM roundabouts found
Q5 sample of 50 junction points (stratified by Soll type, seed 42) with a data-based plausibility rating:
   falsch = a Q1/Q3 rule fires (incl. Ist signal at ETW30+ETW30 = signal of a neighbour); richtig = confidence high, no flag, Ist known and consistent; else unsicher.
   This is a desk review on data, not a visual check (orthophoto links for the manual check are included).
Usage: python -m analysis.review_2026_11.junctions_2c <out_dir>
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml
from scipy.spatial import cKDTree

from analysis.review_2026_11.common import ROOT, node_links

ROUNDABOUTS = {"roundabout_single_lane_cycle_priority", "roundabout_single_lane_cycle_yield", "turbo_roundabout"}


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def param(d, key):
    for x in walk(d):
        if key in x:
            v = x[key]
            return float(v["value"] if isinstance(v, dict) else v)
    raise KeyError(key)


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    dr = yaml.safe_load((ROOT / "config/design_rules.yaml").read_text(encoding="utf-8"))
    cluster_r, rmin, rmax = param(dr, "cluster_radius_m"), param(dr, "roundabout_min_radius"), param(dr, "roundabout_max_dtv")
    j = gpd.read_parquet(ROOT / "data/interim/junctions.parquet")
    flags = j.conflict_flags.fillna("").str.split("|")
    res = {"n": len(j), "params": {"cluster_radius_m": cluster_r, "roundabout_min_radius": rmin,
                                   "roundabout_max_dtv": rmax}}

    # Q1
    big = j.extent_m > 2 * cluster_r
    pts = np.column_stack([j.geometry.centroid.x, j.geometry.centroid.y])
    pairs = cKDTree(pts).query_pairs(cluster_r, output_type="ndarray")
    close_ids = set(pairs.ravel().tolist()) if len(pairs) else set()
    res["Q1"] = {"extent_gt_2r": int(big.sum()), "extent_max_m": round(float(j.extent_m.max()), 1),
                 "members_gt_5": int((j.n_members > 5).sum()),
                 "separate_points_closer_than_r_pairs": int(len(pairs)),
                 "pairs_both_carriageway_ge3": int(sum(1 for a, b in pairs if j.legs_count.iat[a] >= 3 and j.legs_count.iat[b] >= 3))}
    # Q2
    res["Q2"] = {"legs_lt_3": int((j.legs_count < 3).sum()),
                 "legs_lt_3_pairs": j.pair[j.legs_count < 3].value_counts().head(6).to_dict(),
                 "legs_ge_6": int((j.legs_count >= 6).sum())}
    # Q3
    rb = j.junction_type_final.isin(ROUNDABOUTS)
    q3 = {
        "roundabout_space_unknown": rb & flags.map(lambda f: "space_unknown" in f),
        "roundabout_space_below_min": rb & (j.space_radius_m < rmin),
        "single_lane_roundabout_dtv_above_max": (j.junction_type_final == "roundabout_single_lane_cycle_priority") &
                                                (j.entering_dtv_sum > rmax),
        "signal_soll_at_etw_etw": (j.junction_type_final == "signal_protected") & (j.pair == "ETW30+ETW30"),
        "soll_roundabout_ist_signal": rb & (j.junction_type_ist == "signal"),
        "soll_equal_ist_signal": (j.junction_type_final == "equal_right_before_left") & (j.junction_type_ist == "signal"),
        "ist_signal_at_etw_etw": (j.junction_type_ist == "signal") & (j.pair == "ETW30+ETW30"),
    }
    res["Q3"] = {k: int(v.sum()) for k, v in q3.items()}
    # Q4
    res["Q4"] = {"ist_types": j.junction_type_ist.value_counts().to_dict(),
                 "ist_result": j.ist_result.value_counts().to_dict(),
                 "share_none_mapped": round(float((j.junction_type_ist == "none_mapped").mean()), 3)}

    # Q5 sample
    implausible = big | q3["roundabout_space_unknown"] | q3["roundabout_space_below_min"] | \
        q3["single_lane_roundabout_dtv_above_max"] | q3["signal_soll_at_etw_etw"] | q3["ist_signal_at_etw_etw"]
    j["implausible"] = implausible
    j["close_to_other"] = [i in close_ids for i in range(len(j))]
    clean = (j.confidence == "high") & (j.conflict_flags.fillna("") == "") & (j.junction_type_ist != "none_mapped") & \
        (j.ist_result != "mismatch") & ~j.close_to_other
    j["rating"] = np.where(implausible, "falsch", np.where(clean, "richtig", "unsicher"))
    types = j.junction_type_final.value_counts().index.tolist()
    per = max(1, 50 // len(types))
    sample = pd.concat([j[j.junction_type_final == t].sample(min(per, (j.junction_type_final == t).sum()), random_state=42)
                        for t in types])
    rest = j.drop(sample.index)
    if len(sample) < 50:
        sample = pd.concat([sample, rest.sample(50 - len(sample), random_state=42)])
    sample = sample.head(50)

    def reason(r):
        why = []
        if r.extent_m > 2 * cluster_r:
            why.append(f"Ausdehnung {r.extent_m:.0f} m")
        if r.junction_type_final in ROUNDABOUTS and (pd.isna(r.space_radius_m) or r.space_radius_m < rmin):
            why.append(f"Kreisverkehr ohne Platz (Radius {r.space_radius_m if pd.notna(r.space_radius_m) else 'unbekannt'})")
        if r.junction_type_final == "roundabout_single_lane_cycle_priority" and r.entering_dtv_sum > rmax:
            why.append(f"Zufluss {r.entering_dtv_sum:.0f} > {rmax:.0f}")
        if r.junction_type_final == "signal_protected" and r.pair == "ETW30+ETW30":
            why.append("Ampel an ETW×ETW")
        if r.junction_type_ist == "signal" and r.pair == "ETW30+ETW30":
            why.append("Ist-Ampel an ETW×ETW (vermutlich Ampel des Nachbarknotens, N6 signal_radius_m)")
        if r.junction_type_ist == "none_mapped":
            why.append("Ist-Typ in OSM nicht erfasst")
        if r.ist_result == "mismatch":
            why.append(f"Ist {r.junction_type_ist} ≠ Soll")
        if r.close_to_other:
            why.append("weiterer Knotenpunkt < 25 m")
        if r.conflict_flags:
            why.append(f"Flags {r.conflict_flags}")
        if r.confidence != "high":
            why.append(f"confidence {r.confidence}")
        return "; ".join(why) or "keine Auffälligkeit"

    sample["begruendung"] = sample.apply(reason, axis=1)
    sample["links"] = [node_links(r.node_id, r.geometry.centroid) for _, r in sample.iterrows()]
    cols = ["node_id", "names", "bezirk", "pair", "legs_count", "junction_type_final", "junction_type_ist",
            "confidence", "rating", "begruendung", "links"]
    sample[cols].to_csv(out / "junctions_sample50.csv", index=False)
    res["Q5"] = {"sample_ratings": sample.rating.value_counts().to_dict(),
                 "all_ratings": j.rating.value_counts().to_dict(),
                 "sample_by_type": sample.groupby(["junction_type_final", "rating"]).size().unstack(fill_value=0)
                 .to_dict(orient="index")}
    (out / "junctions_2c.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1])
