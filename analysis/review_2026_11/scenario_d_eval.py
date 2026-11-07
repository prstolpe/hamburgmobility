"""Evaluate scenario D: which GOW30 candidates become viable, where the traffic goes (incl. rat-running on ETW30).

Inputs: data/scenarios/D_assignment/scenario_d_segments.parquet (model and pivot DTV per variant),
data/interim/cycle_facility.parquet (Soll cycle street), rules for the limits.
Usage: python -m analysis.review_2026_11.scenario_d_eval <out_dir>
"""

import json
import sys
from pathlib import Path

import pandas as pd
import yaml

from analysis.review_2026_11.common import ROOT

D = ROOT / "data/scenarios/D_assignment"


def main(out_dir: str) -> None:
    out = Path(out_dir)
    r = yaml.safe_load((ROOT / "config/rules.yaml").read_text(encoding="utf-8"))
    c = yaml.safe_load((ROOT / "config/cycling_rules.yaml").read_text(encoding="utf-8"))
    wide = float(r["requirements"]["GOW30"]["profiles"]["wide"]["max_dtv"])
    street_max = float(c["cycle_street"]["max_motor_vehicles_day"]["value"])
    s = pd.read_parquet(D / "scenario_d_segments.parquet")
    meta = json.loads((D / "scenario_d_meta.json").read_text(encoding="utf-8"))
    fac = pd.read_parquet(ROOT / "data/interim/cycle_facility.parquet", columns=["segment_id", "cycle_facility_soll",
                                                                                 "cycle_cat_final"])
    s = s.merge(fac, on="segment_id", how="left")
    runs = meta["runs"]
    km = lambda m: round(float(s.length_m[m].sum()) / 1000, 1)
    res = {"calibration": meta["chosen"], "n_zones": [meta["n_zones_internal"], meta["n_zones_external"]], "runs": {}}
    need = pd.read_parquet(ROOT / "data/scenarios/C_gow30_reduction/scenario_c_segments.parquet", columns=["segment_id"])
    cand = s.segment_id.isin(need.segment_id)  # GOW30 > 10 000 without separated track (scenario C)
    over_all = (s.cat_final == "GOW30") & (s.dtv_official > wide)  # incl. track profile
    etw = s.cat_final.isin(["ETW30", "ETW_ERF"])
    cs = s.cycle_facility_soll == "cycle_street"
    vkm = lambda col: (s[col] * s.length_m / 1000).groupby(s.cat_final.fillna("ohne")).sum()
    base_vkm = vkm("model_ist")
    for k in runs:
        mcol, dcol = f"model_{k}", f"dtv_{k}"
        delta = s[mcol] - s.model_ist
        res["runs"][k] = {
            "gow30_candidates_viable_km": km(cand & (s[dcol] <= wide)), "gow30_candidates_km": km(cand),
            "gow30_over_wide_all_viable_km": km(over_all & (s[dcol] <= wide)), "gow30_over_wide_all_km": km(over_all),
            "vkm_change_pct_by_cat": ((vkm(mcol) / base_vkm - 1) * 100).round(1).to_dict(),
            "etw_increase_gt_1000_km": km(etw & (delta > 1000)),
            "etw_increase_gt_2500_km": km(etw & (delta > street_max)),
            "cycle_street_soll_model_gt_2500_km": km(cs & (s[mcol] > street_max)),
            "cycle_street_soll_model_gt_2500_ist_km": km(cs & (s.model_ist > street_max)),
            "gow50_increase_gt_5000_km": km((s.cat_final == "GOW50") & (delta > 5000)),
        }
    # top rat-running streets in the reference variant (etw 1.0, no evaporation)
    k = runs[0]
    s["delta_ref"] = s[f"model_{k}"] - s.model_ist
    rr = s[etw & (s.delta_ref > 1000)].groupby(["name", "bezirk"]).agg(km=("length_m", lambda x: round(x.sum() / 1000, 2)),
                                                                        delta_max=("delta_ref", "max")) \
        .sort_values("km", ascending=False).head(15)
    rr.to_csv(out / "scenario_d_ratrun_streets.csv")
    res["ratrun_streets_ref"] = rr.reset_index().to_dict(orient="records")
    (out / "scenario_d_eval.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1])
