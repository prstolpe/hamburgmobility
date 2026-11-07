"""Side-by-side figures of street scenarios (A = data/interim, others = data/scenarios/<name>/).

Per scenario: km per cat_final (whole work area, per district), km of Soll facility types, fit_class, junction types,
discrepancy (priority > 0) and GOW30 above the CROW wide profile without a separated track.
Usage: python -m analysis.review_2026_11.compare_scenarios <out_json> A=data/interim B=data/scenarios/B_gow30_cap ...
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def figures(d: Path) -> dict:
    f = pd.read_parquet(d / "final.parquet", columns=["segment_id", "bezirk", "length_m", "cat_final", "in_hvs",
                                                     "dtv_official", "separated_cycle_track_present"])
    f = f[f.cat_final.notna()]
    km = lambda s: round(float(s.sum()) / 1000, 1)
    x = pd.read_parquet(d / "cross_section_soll.parquet", columns=["segment_id", "length_m", "fit_class",
                                                                  "cycle_facility_final"])
    j = pd.read_parquet(d / "junctions.parquet", columns=["junction_type_final", "action_needed"])
    disc = pd.read_parquet(d / "discrepancy.parquet", columns=["segment_id", "length_m", "priority", "disc_max"])
    hvs = f.in_hvs.fillna(False).astype(bool)
    over = (f.cat_final == "GOW30") & (f.dtv_official > 10000) & ~f.separated_cycle_track_present.fillna(False).astype(bool)
    return {
        "cat_km": (f.groupby("cat_final").length_m.sum() / 1000).round(1).to_dict(),
        "hvs_cat_km": (f[hvs].groupby("cat_final").length_m.sum() / 1000).round(1).to_dict(),
        "cat_km_by_bezirk": (f.groupby([f.bezirk.fillna("Randbereich"), "cat_final"]).length_m.sum() / 1000).round(1)
        .unstack(fill_value=0).to_dict(orient="index"),
        "gow30_over_wide_no_track_km": km(f.length_m[over]),
        "facility_km": (x.groupby("cycle_facility_final").length_m.sum() / 1000).round(1).to_dict(),
        "fit_km": (x.groupby(x.fit_class.fillna("null")).length_m.sum() / 1000).round(1).to_dict(),
        "junction_types": j.junction_type_final.value_counts().to_dict(),
        "junction_action_needed": int(j.action_needed.fillna(False).astype(bool).sum()),
        "disc_km_by_max": {str(int(k)): v for k, v in (disc.groupby(disc.disc_max.fillna(-1)).length_m.sum() / 1000).round(1).items()},
    }


def main(out_json: str, *pairs: str) -> None:
    res = {}
    for p in pairs:
        name, path = p.split("=", 1)
        res[name] = figures(ROOT / path)
    Path(out_json).write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    for k in ("cat_km", "hvs_cat_km", "gow30_over_wide_no_track_km", "facility_km", "fit_km", "junction_types",
              "junction_action_needed", "disc_km_by_max"):
        print(k, {n: r[k] for n, r in res.items()})


if __name__ == "__main__":
    main(sys.argv[1], *sys.argv[2:])
