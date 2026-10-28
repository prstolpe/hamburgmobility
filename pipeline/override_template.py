"""Template rows for new overrides (prompts/09).

Usage:
  uv run python -m pipeline.override_template seg_… seg_… [--author "Name"] [--out datei.csv]
  uv run python -m pipeline.override_template --file ids.txt
  make override-template IDS="seg_… seg_…"

Writes CSV with the columns of overrides/overrides.csv: cat_final = cat_proposed, review_status = draft,
date = today, reason empty. Fill in cat_final, reason and source, then add the rows to overrides/overrides.csv
via pull request. The pipeline refuses rows without a reason.
"""

import argparse
import datetime as dt
import sys
from pathlib import Path

import pandas as pd

from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.overrides import OverrideError, template_csv

SEGMENTS_PATHS = [REPO_ROOT / "data" / "interim" / name for name in ("final.parquet", "coherence.parquet",
                                                                       "classified.parquet")]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Vorlage für neue Overrides aus segment_ids")
    ap.add_argument("ids", nargs="*", help="segment_ids")
    ap.add_argument("--file", type=Path, help="Datei mit einer segment_id je Zeile")
    ap.add_argument("--author", default="", help="Autor*in (sonst leer)")
    ap.add_argument("--out", type=Path, help="Zieldatei (sonst Ausgabe auf stdout)")
    args = ap.parse_args(argv)
    ids = list(args.ids)
    if args.file:
        ids += [ln.strip() for ln in args.file.read_text(encoding="utf-8").splitlines() if ln.strip()]
    ids = list(dict.fromkeys(ids))
    if not ids:
        ap.error("keine segment_id angegeben")
    src = next((p for p in SEGMENTS_PATHS if p.exists()), None)
    if src is None:
        print("override_template: no classified segments; run `make classify` first", file=sys.stderr)
        return 1
    seg = pd.read_parquet(src, columns=["segment_id", "cat_proposed"])
    try:
        text = template_csv(ids, seg, author=args.author, today=dt.date.today().isoformat())
    except OverrideError as e:
        print(f"override_template: {e}", file=sys.stderr)
        return 1
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"override_template: {len(ids)} rows -> {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
