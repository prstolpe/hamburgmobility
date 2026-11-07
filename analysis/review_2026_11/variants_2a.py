"""Phase 2a: dry runs of rule proposals for the street classification (cascade only, see dryrun.py).

V-BUS-100 / V-BUS-200  C-GOW-01 also true for bus_trips_weekday >= 100 / 200 (new threshold, assumption)
V-CONN-050            conn_gow 0.6 -> 0.5 (calibration question, open_questions line 123)
V-NOHVS               in_hvs out of conn_score (open_questions line 124; weights renormalised over the rest)
V-NODTV               dtv_norm out of conn_score (usage out of function)
Usage: python -m analysis.review_2026_11.variants_2a <out_dir>
"""

import json
import sys
from pathlib import Path

import pandas as pd

from analysis.review_2026_11 import dryrun
from analysis.review_2026_11.common import seg_links

OLD_IF = 'if: "conn_score >= thresholds.conn_gow or in_hvs"'
OLD_THR = 'conn_gow: {value: 0.6, unit: "score 0-1", source_type: assumption, check: "Sensitivität ±20 %, Abgleich HVS"}'
WEIGHTS = {"betweenness_norm": 0.35, "in_hvs": 0.25, "bus_trips_weekday_norm": 0.20, "dtv_norm": 0.20}


def bus_rule(n: int):
    def edit(t: str) -> str:
        t = t.replace(OLD_IF, 'if: "conn_score >= thresholds.conn_gow or in_hvs or bus_trips_weekday >= thresholds.bus_gow"')
        return t.replace(OLD_THR, OLD_THR + f'\n      bus_gow: {{value: {n}, unit: "Busfahrten je Werktag", source_type: assumption}}')
    return edit


def conn_score_without(drop: str, df: pd.DataFrame) -> pd.Series:
    feats = pd.read_parquet(dryrun.ROOT / "data/interim/features.parquet", columns=["segment_id", *WEIGHTS])
    f = df[["segment_id"]].merge(feats, on="segment_id", how="left")
    w = {k: v for k, v in WEIGHTS.items() if k != drop}
    x = f[list(w)].astype(float)
    num = sum(x[k].fillna(0) * v for k, v in w.items())
    den = sum(x[k].notna() * v for k, v in w.items())
    return (num / den).to_numpy()


def summary(name: str, cmp: dict, out: Path) -> dict:
    rows = cmp.pop("rows")
    rows.drop(columns="geometry").to_csv(out / f"dry_{name}.csv", index=False)
    ex = [f"{r['name'] or '(ohne Name)'} ({r.bezirk or 'Randbereich'}, {r.cat_proposed} → {r.cat_new}): "
          f"{seg_links(r.segment_id, r.geometry)}"
          for _, r in rows.sort_values("length_m", ascending=False).drop_duplicates("name").head(6).iterrows()]
    cmp["examples"] = ex
    print(name, {k: v for k, v in cmp.items() if k != "examples"})
    return cmp


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    base = dryrun.baseline()
    res = {"baseline_km": (base.groupby("cat_proposed").length_m.sum() / 1000).round(1).to_dict()}
    for n in (100, 200):
        res[f"V-BUS-{n}"] = summary(f"V-BUS-{n}", dryrun.compare(base, dryrun.run_variant(bus_rule(n), f"bus{n}")), out)
    res["V-CONN-050"] = summary("V-CONN-050", dryrun.compare(base, dryrun.run_variant(
        lambda t: t.replace(OLD_THR, OLD_THR.replace("value: 0.6", "value: 0.5")), "conn050")), out)
    orig = dryrun.inputs().conn_score.copy()
    for drop, name in (("in_hvs", "V-NOHVS"), ("dtv_norm", "V-NODTV")):
        dryrun._INPUT["conn_score"] = conn_score_without(drop, dryrun._INPUT)
        var = dryrun.classify_with(dryrun.RULES.read_text(encoding="utf-8"))
        res[name] = summary(name, dryrun.compare(base, var), out)
        dryrun._INPUT["conn_score"] = orig
    (out / "variants_2a.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1])
