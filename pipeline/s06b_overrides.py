"""Stage 6b: apply expert corrections from overrides/overrides.csv (guide 3.2 Stufe 7, prompts/09).

Usage: uv run python -m pipeline.s06b_overrides

Reads data/interim/coherence.parquet and overrides/overrides.csv, validates every row (orphan segment_id,
invalid category, missing reason, ...) and applies rows with review_status = approved. Writes
data/interim/final.parquet with cat_proposed and cat_final side by side (plus cat_final_source and override_*),
and the section "Korrekturebene" in reports/coherence.md. Stops with exit code 1 on any invalid row.
"""

import sys

import geopandas as gpd
import pandas as pd

from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.overrides import OVERRIDES_PATH, REVIEW_STATUS, OverrideError, apply, read_overrides, validate
from pipeline.lib.rules import load_rules
from pipeline.s04_features import _fmt, _now

IN_PATH = REPO_ROOT / "data" / "interim" / "coherence.parquet"
OUT_PATH = REPO_ROOT / "data" / "interim" / "final.parquet"
REPORT_PATH = REPO_ROOT / "reports" / "coherence.md"
SECTION = "## Korrekturebene (Stufe 6b)"


def report_section(df: pd.DataFrame, out: pd.DataFrame, rules) -> list[str]:
    status = df["review_status"].value_counts()
    applied = out[out["cat_final_source"] == "override"]
    lines = [SECTION, "",
             f"Erzeugt: {_now()} von `pipeline/s06b_overrides.py`, rules.yaml {rules.meta.version}. "
             "Quelle: `overrides/overrides.csv`; übernommen wird nur review_status = approved. cat_proposed bleibt "
             "unverändert, cat_final steht daneben.", "",
             "| review_status | Einträge |", "| --- | ---: |",
             *[f"| {s} | {_fmt(status.get(s, 0))} |" for s in REVIEW_STATUS], "",
             f"Alle {len(df)} Einträge geprüft: keine verwaisten segment_id, gültige Kategorien, Begründung, Autor*in und "
             "Datum vorhanden.", "",
             f"Übernommene Korrekturen: {len(applied)}."]
    if not applied.empty:
        lines += ["", "| segment_id | Name | cat_proposed | cat_final | Begründung | Autor*in | Datum | Quelle |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for _, r in applied.sort_values("segment_id").iterrows():
            name = r["name"] if isinstance(r["name"], str) and r["name"] else "–"
            lines.append(f"| `{r['segment_id']}` | {name} | {r['cat_proposed']} | {r['cat_final']} | {r['override_reason']} | "
                         f"{r['override_author']} | {r['override_date']} | {r['override_source'] or '–'} |")
    lines += ["", "Neue Korrekturen: `make override-template IDS=\"seg_… seg_…\"` erzeugt Zeilen mit review_status draft; "
              "Begründung eintragen und per Pull Request (Vier-Augen-Prinzip) auf approved setzen.", ""]
    return lines


def write_section(lines: list[str]) -> None:
    text = REPORT_PATH.read_text(encoding="utf-8") if REPORT_PATH.exists() else "# Kohärenzbericht – Stufe 6\n"
    if SECTION in text:  # replace the section of an earlier run; the stage-6 part stays as it is
        head, _, rest = text.partition(SECTION)
        nxt = rest.find("\n## ")
        text = head + (rest[nxt + 1:] if nxt >= 0 else "")
    # keep the section before the licence note at the end
    marker = "## Lizenz"
    body = "\n".join(lines)
    text = text.replace(marker, body + "\n" + marker, 1) if marker in text else text.rstrip("\n") + "\n\n" + body
    REPORT_PATH.write_text(text, encoding="utf-8")


def main() -> int:
    rules = load_rules()
    if not IN_PATH.exists():
        print("overrides: data/interim/coherence.parquet missing; run `make coherence` first", file=sys.stderr)
        return 1
    seg = gpd.read_parquet(IN_PATH)
    df = read_overrides(OVERRIDES_PATH)
    classified = seg.loc[seg["cat_proposed"].notna(), "segment_id"]
    try:
        validate(df, classified, seg["segment_id"], rules.categories)
    except OverrideError as e:
        print(f"overrides: {e}", file=sys.stderr)
        return 1
    out = apply(seg, df)
    if not out["cat_proposed"].fillna("–").equals(seg["cat_proposed"].fillna("–")):
        print("overrides: cat_proposed changed – this must not happen", file=sys.stderr)
        return 1
    write_section(report_section(df, out, rules))
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_PATH, index=False)
    n = int((out["cat_final_source"] == "override").sum())
    print(f"overrides: {len(df)} rows valid, {n} approved applied -> {OUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
