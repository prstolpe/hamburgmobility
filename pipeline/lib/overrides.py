"""Override layer: expert corrections in overrides/overrides.csv (guide 3.2 Stufe 7, prompts/09).

Only rows with review_status = approved are applied. cat_proposed is never changed; cat_final holds the
result next to it. Every row is validated (also drafts), so a broken file stops the pipeline.
"""

import csv
import datetime as dt
import io
from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from pipeline.lib.manifest import REPO_ROOT

OVERRIDES_PATH = REPO_ROOT / "overrides" / "overrides.csv"
COLUMNS = ["segment_id", "cat_final", "reason", "author", "date", "source", "review_status"]
REVIEW_STATUS = ("draft", "approved", "rejected")  # Entscheidung Projektteam 2026-10-28
APPLIED_STATUS = "approved"
OVERRIDE_COLUMNS = ["cat_final", "cat_final_source", "override_reason", "override_author", "override_date",
                    "override_source"]


class OverrideError(ValueError):
    """overrides.csv is invalid; the message lists every problem with its CSV line."""


def read_overrides(path: str | Path = OVERRIDES_PATH) -> pd.DataFrame:
    """All fields as text; empty cells as empty strings."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def _blank(value) -> bool:
    return value is None or (isinstance(value, float) and value != value) or not str(value).strip()


def _is_iso_date(value) -> bool:
    try:
        return dt.date.fromisoformat(str(value)).isoformat() == str(value)
    except ValueError:
        return False


def validate(df: pd.DataFrame, classified_ids: Iterable[str], all_ids: Iterable[str], categories: Iterable[str]) -> None:
    """Raise OverrideError listing all problems. classified_ids = segments with cat_proposed (work area),
    all_ids = every segment of the current network (an ID missing there is an orphan)."""
    if list(df.columns) != COLUMNS:
        raise OverrideError(f"overrides.csv: Spalten müssen genau {', '.join(COLUMNS)} sein (gefunden: "
                            f"{', '.join(map(str, df.columns))})")
    classified, known, cats = set(classified_ids), set(all_ids), set(categories)
    errors = []
    counts = df["segment_id"].value_counts()
    for i, r in enumerate(df.itertuples(index=False), start=2):  # line 1 = header
        where = f"Zeile {i} ({r.segment_id or 'ohne segment_id'})"
        if _blank(r.segment_id):
            errors.append(f"{where}: segment_id fehlt")
        elif r.segment_id not in known:
            errors.append(f"{where}: segment_id verwaist – im aktuellen Netz nicht vorhanden "
                          "(nach Datenupdate weggefallen?); Korrektur prüfen und neu zuordnen")
        elif r.segment_id not in classified:
            errors.append(f"{where}: Abschnitt liegt außerhalb des Arbeitsgebiets (keine cat_proposed)")
        if not _blank(r.segment_id) and counts.get(r.segment_id, 0) > 1:
            errors.append(f"{where}: segment_id doppelt in overrides.csv")
        if r.cat_final not in cats:
            errors.append(f"{where}: ungültige Kategorie {r.cat_final!r} (erlaubt: {', '.join(sorted(cats))})")
        if _blank(r.reason):
            errors.append(f"{where}: Begründung fehlt (Spalte reason)")
        if _blank(r.author):
            errors.append(f"{where}: author fehlt")
        if not _is_iso_date(r.date):
            errors.append(f"{where}: Datum {r.date!r} nicht im Format JJJJ-MM-TT")
        if r.review_status not in REVIEW_STATUS:
            errors.append(f"{where}: review_status {r.review_status!r} ungültig (erlaubt: {', '.join(REVIEW_STATUS)})")
    if errors:
        raise OverrideError("overrides.csv ungültig:\n  " + "\n  ".join(errors))


def apply(segments: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """Copy of segments with cat_final and override_* columns; cat_proposed stays as it is."""
    out = segments.copy()
    approved = df[df["review_status"] == APPLIED_STATUS].set_index("segment_id")
    hit = out["segment_id"].map(lambda s: s in approved.index)
    out["cat_final"] = out["cat_proposed"]
    out["cat_final_source"] = out["cat_proposed"].map(lambda c: None if _blank(c) else "proposed")
    for col in ("reason", "author", "date", "source"):
        out[f"override_{col}"] = None
    if hit.any():
        ids = out.loc[hit, "segment_id"]
        out.loc[hit, "cat_final"] = ids.map(approved["cat_final"]).to_numpy()
        out.loc[hit, "cat_final_source"] = "override"
        for col in ("reason", "author", "date", "source"):
            out.loc[hit, f"override_{col}"] = ids.map(approved[col]).to_numpy()
    return out


def template_csv(segment_ids: list[str], segments: pd.DataFrame, author: str, today: str) -> str:
    """CSV rows for new overrides: cat_final = cat_proposed, review_status = draft, reason empty
    (a person has to fill it in; validate() rejects empty reasons)."""
    cat = segments.set_index("segment_id")["cat_proposed"]
    unknown = [s for s in segment_ids if s not in cat.index or _blank(cat.get(s))]
    if unknown:
        raise OverrideError("Unbekannte oder nicht klassifizierte segment_id: " + ", ".join(unknown))
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COLUMNS)
    for sid in segment_ids:
        w.writerow([sid, cat[sid], "", author, today, "", "draft"])
    return buf.getvalue()
