"""Phase 1.3: the GOW30 -> GOW50 switch of rules.yaml 0.14.0 (C-G30-01 cap gow30_max_dtv, C-G50-02).

Compares the saved variant (data/variants/2026-11-07_gow50-kompromiss, rules 0.14.0) with the current export
(data/out, rules 0.16.0). The pure mechanism = segments whose variant rule_path contains C-G50-02.
Other differences between the two states come from batch 5 (rules 0.16.0) and are reported separately.

Usage: python -m analysis.review_2026_11.gow_switch <out_dir>
"""

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
VAR = ROOT / "data/variants/2026-11-07_gow50-kompromiss/site/downloads"
CUR = ROOT / "data/out/downloads"
COLS = ["segment_id", "name", "bezirk", "highway", "length_m", "cat_final", "cat_proposed", "rule_path", "in_hvs",
        "dtv_official", "schools_or_kitas_within_m", "shop_frontage_share", "conn_score", "disc_max", "priority"]


def strkeys(o):
    """JSON needs string keys; tuples from groupby become 'a->b'."""
    if isinstance(o, dict):
        return {("->".join(map(str, k)) if isinstance(k, tuple) else str(k)): strkeys(v) for k, v in o.items()}
    return o


def km(s: pd.Series) -> float:
    return round(float(s.sum()) / 1000, 1)


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    v = pd.read_parquet(VAR / "segments.parquet", columns=COLS)
    c = pd.read_parquet(CUR / "segments.parquet", columns=COLS)
    m = c.merge(v, on="segment_id", suffixes=("", "_var"), how="outer", indicator=True)
    res = {"rows_cur": len(c), "rows_var": len(v), "only_cur": int((m._merge == "left_only").sum()),
           "only_var": int((m._merge == "right_only").sum())}
    m = m[m._merge == "both"].copy()
    m["c_g50_02"] = m.rule_path_var.astype(str).str.contains("C-G50-02")

    # transition matrix (km) variant -> current
    res["transition_km"] = (m.groupby(["cat_final_var", "cat_final"]).length_m.sum() / 1000).round(1) \
        .unstack(fill_value=0).to_dict()
    pure = m[m.c_g50_02]
    res["c_g50_02"] = {"segments": len(pure), "km": km(pure.length_m),
                       "now": (pure.groupby("cat_final").length_m.sum() / 1000).round(1).to_dict()}
    sw = pure[(pure.cat_final_var == "GOW50") & (pure.cat_final == "GOW30")]
    other = m[(m.cat_final_var != m.cat_final) & ~m.c_g50_02]
    res["switched_gow50_to_gow30"] = {"segments": len(sw), "km": km(sw.length_m)}
    res["other_changes_batch5"] = {"segments": len(other), "km": km(other.length_m),
                                   "by_pair_km": (other.groupby(["cat_final_var", "cat_final"]).length_m.sum() / 1000)
                                   .round(1).sort_values(ascending=False).head(10).to_dict()}
    # HVS km per category in both states
    for tag, col in (("var", "cat_final_var"), ("cur", "cat_final")):
        h = m[m.in_hvs.fillna(False).astype(bool)]
        res[f"hvs_km_{tag}"] = (h.groupby(col).length_m.sum() / 1000).round(1).to_dict()

    by_d = sw.groupby("bezirk").agg(segments=("segment_id", "size"), km=("length_m", lambda s: km(s)),
                                    dtv_median=("dtv_official", "median")).sort_values("km", ascending=False)
    by_d.to_csv(out / "gow_switch_by_bezirk.csv")
    streets = sw.groupby(["name", "bezirk"]).agg(km=("length_m", lambda s: km(s)), segments=("segment_id", "size"),
                                                 dtv_max=("dtv_official", "max"),
                                                 example=("segment_id", "first")) \
        .sort_values("km", ascending=False)
    streets.head(40).to_csv(out / "gow_switch_streets.csv")
    # trigger of C-G30-01 on the switched segments (what made them GOW30 in the first place)
    trig = pd.DataFrame({
        "school_kita_le_150m": sw.schools_or_kitas_within_m.fillna(1e9) <= 150,
        "frontage_ge_0_4": sw.shop_frontage_share.fillna(-1) >= 0.4})
    res["triggers_on_switched"] = {k: int(v) for k, v in trig.sum().items()}
    res["dtv_on_switched"] = sw.dtv_official.describe().round(0).to_dict()

    # cycle routes on switched segments (current cycle network)
    cyc = pd.read_parquet(CUR / "cycle_segments.parquet", columns=["segment_id", "cycle_cat_final", "fit_class"])
    sc = sw.merge(cyc, on="segment_id", how="left")
    res["cycle_cat_on_switched_km"] = (sc.groupby(sc.cycle_cat_final.fillna("kein")).length_m.sum() / 1000) \
        .round(1).to_dict()
    res["fit_class_on_switched_km"] = (sc.groupby(sc.fit_class.fillna("null")).length_m.sum() / 1000).round(1).to_dict()

    # junctions touching switched segments (current junction legs)
    j = pd.read_parquet(ROOT / "data/interim/junctions.parquet", columns=["node_id", "legs", "pair",
                                                                           "junction_type_final"])
    ids = set(sw.segment_id)
    touch = j[j.legs.map(lambda s: any(i in ids for leg in json.loads(s) for i in leg["ids"]))]
    res["junctions_touching"] = {"n": len(touch),
                                 "pairs": touch.pair.value_counts().head(8).to_dict(),
                                 "types_now": touch.junction_type_final.value_counts().head(8).to_dict()}
    res = strkeys(res)
    (out / "gow_switch.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    print(by_d)
    print(streets.head(15))


if __name__ == "__main__":
    main(sys.argv[1])
