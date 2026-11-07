"""Dry run of rule proposals: classification cascade only (s05), in-process, with a modified copy of rules.yaml.

Harmonisation (s05b), coherence (s06), overrides (s06b) and the cycling chain are NOT rerun; results therefore
show the direct effect of a rule change on cat_proposed. Baseline = the same function with the unchanged rules,
checked against data/interim/classified.parquet (must be identical).

Usage in code:
    from analysis.review_2026_11.dryrun import baseline, run_variant
    base = baseline()
    var = run_variant(lambda text: text.replace(...), name="X")
"""

import tempfile
from pathlib import Path

import geopandas as gpd
import pandas as pd

from pipeline.lib.classify import clear_cache
from pipeline.lib.rules import load_rules
from pipeline.s05_classify import classify_frame

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "config/rules.yaml"
_INPUT = None


def inputs() -> gpd.GeoDataFrame:
    global _INPUT
    if _INPUT is None:
        x = gpd.read_parquet(ROOT / "data/interim/crosssection.parquet")
        area = pd.read_parquet(ROOT / "data/interim/classified.parquet", columns=["segment_id", "cat_proposed"])
        x = x.merge(area.rename(columns={"cat_proposed": "cat_proposed_stored"}), on="segment_id", how="left")
        _INPUT = x[x.cat_proposed_stored.notna()].reset_index(drop=True)  # work area only
    return _INPUT


def classify_with(rules_text: str) -> pd.DataFrame:
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write(rules_text)
        path = f.name
    clear_cache()
    rules = load_rules(path)
    df = inputs()
    out = classify_frame(df, rules)
    Path(path).unlink()
    clear_cache()
    return pd.concat([df[["segment_id", "name", "bezirk", "highway", "length_m", "geometry", "in_hvs", "dtv_official",
                          "bus_trips_weekday", "speed_ist_kmh"]], out[["cat_proposed", "rule_path", "confidence"]]], axis=1)


def baseline() -> pd.DataFrame:
    b = classify_with(RULES.read_text(encoding="utf-8"))
    stored = inputs().cat_proposed_stored
    n_diff = int((b.cat_proposed != stored).sum())
    assert n_diff == 0, f"baseline differs from classified.parquet on {n_diff} segments"
    return b


def run_variant(edit, name: str) -> pd.DataFrame:
    text = RULES.read_text(encoding="utf-8")
    new = edit(text)
    assert new != text, f"variant {name}: edit changed nothing"
    return classify_with(new)


def compare(base: pd.DataFrame, var: pd.DataFrame) -> dict:
    """km per category change, per district, and the changed rows."""
    ch = base.cat_proposed != var.cat_proposed
    d = base[ch].assign(cat_new=var.cat_proposed[ch])
    pair = (d.groupby([d.cat_proposed, d.cat_new]).length_m.sum() / 1000).round(1)
    return {"segments": int(ch.sum()), "km": round(float(d.length_m.sum()) / 1000, 1),
            "pairs_km": {f"{a}->{b}": v for (a, b), v in pair.items()},
            "by_bezirk_km": (d.groupby(d.bezirk.fillna("Randbereich")).length_m.sum() / 1000).round(1).to_dict(),
            "rows": d}
