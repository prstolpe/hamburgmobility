"""Scenario C (review 2026-11): GOW30 stays, with the label "Verkehrsreduktion nötig" and the required reduction.

Post-processing of the current state (= scenario A); no rule change, no pipeline run. Limits from rules.yaml
requirements.GOW30.profiles (CROW_GOW30_2023, swov_crow): wide 10 000, narrow 6 000 Kfz/24h. Profile choice as in
D-USE-01: separated_cycle_track_present -> profile track (no limit), otherwise wide (narrow reported).
Measures per segment are candidates only (no rule): modal filter / through-traffic cut where an ETW-free alternative
exists in scenario D, otherwise network change on the corridor.

Usage: python -m analysis.review_2026_11.scenario_c <out_dir> [scenario_d_segments.parquet]
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import yaml

from analysis.review_2026_11.common import ROOT, seg_links


def main(out_dir: str, d_path: str | None = None) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    r = yaml.safe_load((ROOT / "config/rules.yaml").read_text(encoding="utf-8"))
    wide = float(r["requirements"]["GOW30"]["profiles"]["wide"]["max_dtv"])
    narrow = float(r["requirements"]["GOW30"]["profiles"]["narrow"]["max_dtv"])
    d = gpd.read_parquet(ROOT / "data/interim/discrepancy.parquet",
                         columns=["segment_id", "name", "bezirk", "length_m", "cat_final", "dtv_official",
                                  "separated_cycle_track_present", "geometry"])
    g = d[(d.cat_final == "GOW30") & d.dtv_official.notna()].copy()
    track = g.separated_cycle_track_present.fillna(False).astype(bool)
    g["limit"] = wide
    g.loc[track, "limit"] = float("nan")  # profile track: no CROW limit
    g["reduction_wide"] = (g.dtv_official - wide).clip(lower=0)
    g["reduction_narrow"] = (g.dtv_official - narrow).clip(lower=0)
    g["reduction_share_wide"] = g.reduction_wide / g.dtv_official
    over = g[g.reduction_wide > 0]
    need = over[~track[over.index]]  # profile wide applies (no separated track); track profile has no CROW limit
    bins = pd.cut(need.reduction_share_wide, [0, .25, .5, .75, 1], labels=["bis 25 %", "25–50 %", "50–75 %", "über 75 %"])
    res = {
        "gow30_with_dtv_km": round(g.length_m.sum() / 1000, 1),
        "over_wide_limit_km": round(over.length_m.sum() / 1000, 1),
        "over_wide_but_track_profile_km": round(over.length_m[track[over.index]].sum() / 1000, 1),
        "needs_reduction_wide_km": round(need.length_m.sum() / 1000, 1),
        "needs_reduction_wide_segments": len(need),
        "if_track_counted_like_wide_km": round(over.length_m.sum() / 1000, 1),
        "needs_reduction_narrow_km": round(g.length_m[g.reduction_narrow > 0].sum() / 1000, 1),
        "reduction_share_bins_km": (need.groupby(bins, observed=False).length_m.sum() / 1000).round(1).to_dict(),
        "reduction_kfz_day_quartiles": need.reduction_wide.quantile([.25, .5, .75]).round(-2).tolist(),
        "by_bezirk_km": (need.groupby(need.bezirk.fillna("Randbereich")).length_m.sum() / 1000).round(1).to_dict(),
    }
    if d_path:
        sd = pd.read_parquet(d_path)
        dtv_cols = [c for c in sd.columns if c.startswith("dtv_etw")]
        m = need[["segment_id", "length_m", "dtv_official"]].merge(sd[["segment_id", *dtv_cols]], on="segment_id")
        res["viable_after_D_km"] = {c.removeprefix("dtv_"): round(m.length_m[m[c] <= wide].sum() / 1000, 1)
                                    for c in dtv_cols}
    streets = need.groupby(["name", "bezirk"]).agg(km=("length_m", lambda s: round(s.sum() / 1000, 2)),
                                                   dtv_max=("dtv_official", "max"),
                                                   reduction_max=("reduction_wide", "max"),
                                                   example=("segment_id", "first")).sort_values("km", ascending=False)
    streets.head(40).to_csv(out / "scenario_c_streets.csv")
    geo = need.set_index("segment_id").geometry
    res["examples"] = [f"{n} ({b}): {int(row.dtv_max):d} Kfz/Tag, Reduktion {int(row.reduction_max):d} → "
                       f"{seg_links(row.example, geo[row.example])}" for (n, b), row in streets.head(8).iterrows()]
    need.drop(columns="geometry").to_parquet(out / "scenario_c_segments.parquet")
    (out / "scenario_c.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    print(json.dumps({k: v for k, v in res.items() if k != "examples"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:3])
