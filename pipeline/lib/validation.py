"""Report helpers for the validation (guide Teil 7, prompts/12_validation.md).

HVS cross table and deviations, Soll-ETW30 vs. Ist-Tempo, data quality per district, manual samples and the
open questions. Thresholds come from config/rules.yaml; the speed buckets are display classes only.
"""

import math
import re
from typing import Any

import pandas as pd

from config.schema.rules_model import RuleSet

HVS_COLUMNS = ["HVS", "keine HVS", "unbekannt"]
GOW_URBAN = {"GOW50", "GOW30"}
# Autobahnen are federal roads, not Bezirksstraßen (as in reports/classification.md).
FEDERAL_HIGHWAY = {"motorway", "motorway_link"}
NO_DISTRICT = "ohne Bezirk"
TOTAL = "gesamt"
# Columns derived from OSM tags (S-FEAT-10, maxspeed) whose completeness is reported, with labels.
OSM_TAG_COLUMNS = {
    "separated_cycle_track_present": "baulicher Radweg",
    "cycle_lane_present": "Radfahrstreifen",
    "centre_line": "Mittelmarkierung",
    "parking_along_carriageway": "Parken",
    "lanes": "Fahrstreifen",
    "surface": "Belag",
    "maxspeed_osm": "maxspeed",
}
# OSM main road classes for the DTV gap (in_hvs itself comes from the DTV lines, S-CONF-04).
MAIN_ROADS = {"primary", "primary_link", "secondary", "secondary_link"}
SPEED_BUCKETS = ["≤ 20", "30", "40–50", "> 50", "unbekannt"]


def _missing(x: Any) -> bool:
    if x is None or x is pd.NA:
        return True
    try:
        return bool(pd.isna(x))
    except (TypeError, ValueError):
        return False


def hvs_label(x: Any) -> str:
    return "unbekannt" if _missing(x) else ("HVS" if bool(x) else "keine HVS")


def _is_true(s: pd.Series) -> pd.Series:
    return s.map(lambda x: not _missing(x) and bool(x))


def _is_false(s: pd.Series) -> pd.Series:
    return s.map(lambda x: not _missing(x) and not bool(x))


# --- HVS -------------------------------------------------------------------------------------


def crosstab_km(df: pd.DataFrame, cats: list[str], cat_col: str = "cat_final") -> pd.DataFrame:
    """km per Soll category (rows, in the order of cats) and HVS yes/no/unknown (columns)."""
    hvs = df["in_hvs"].map(hvs_label)
    t = df.groupby([df[cat_col], hvs])["length_m"].sum().unstack(fill_value=0.0)
    return (t.reindex(index=cats, columns=HVS_COLUMNS, fill_value=0.0).fillna(0.0) / 1000.0)


def hvs_deviations(df: pd.DataFrame, cat_col: str = "cat_final") -> tuple[pd.DataFrame, pd.DataFrame]:
    """(HVS segments outside GOW50/GOW30, Bezirksstraßen with GOW50) – to be justified one by one (guide 7.1)."""
    hvs_other = df[_is_true(df["in_hvs"]) & ~df[cat_col].isin(GOW_URBAN)]
    district = df[_is_false(df["in_hvs"]) & ~df["highway"].isin(FEDERAL_HIGHWAY) & (df[cat_col] == "GOW50")]
    return hvs_other, district


def _name(x: Any) -> str:
    return x if isinstance(x, str) and x else "–"


def street_groups(df: pd.DataFrame, cat_col: str = "cat_final") -> pd.DataFrame:
    """Segments grouped by district and street name, longest first."""
    cols = ["bezirk", "name", "n", "km", "cats", "highways", "example"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    d = df.assign(name=df["name"].map(_name), bezirk=df["bezirk"].map(lambda b: b if isinstance(b, str) else NO_DISTRICT))
    rows = []
    for (b, n), g in d.groupby(["bezirk", "name"]):
        rows.append({"bezirk": b, "name": n, "n": len(g), "km": g["length_m"].sum() / 1000.0,
                     "cats": ", ".join(sorted(set(g[cat_col]))), "highways": ", ".join(sorted(set(g["highway"]))),
                     "example": g.sort_values("length_m", ascending=False)["segment_id"].iloc[0]})
    return pd.DataFrame(rows, columns=cols).sort_values(["km", "name"], ascending=[False, True]).reset_index(drop=True)


# --- Ist-Tempo -------------------------------------------------------------------------------


def speed_bucket(x: Any) -> str:
    if _missing(x):
        return "unbekannt"
    x = float(x)
    if x <= 20:
        return "≤ 20"
    if x <= 30:
        return "30"
    if x <= 50:
        return "40–50"
    return "> 50"


def speed_table_km(df: pd.DataFrame, cats: list[str], cat_col: str = "cat_final") -> pd.DataFrame:
    """km per Soll category and Ist-Tempo bucket."""
    b = df["speed_ist_kmh"].map(speed_bucket)
    t = df.groupby([df[cat_col], b])["length_m"].sum().unstack(fill_value=0.0)
    return t.reindex(index=cats, columns=SPEED_BUCKETS, fill_value=0.0).fillna(0.0) / 1000.0


# Hints that point to a data error; the last one only describes the street.
_HINTS = [
    ("speed_sources_conflict", lambda r: r.get("speed_sources_conflict") is True or r.get("speed_sources_conflict") == 1,
     "amtlich und OSM verschieden", True),
    ("in_zone_t30", lambda r: not _missing(r.get("in_zone_t30")) and bool(r.get("in_zone_t30")),
     "Tempo-30-Zone laut Zonenebene", True),
    ("speed_ist_source", lambda r: r.get("speed_ist_source") == "osm", "nur OSM-Tempo", True),
    ("hvs_match_quality", lambda r: r.get("hvs_match_quality") == "partial", "HVS-Abgleich nur teilweise", True),
    ("match_quality", lambda r: r.get("match_quality") == "none", "kein amtlicher Abgleich", True),
    ("highway", lambda r: r.get("highway") in ("residential", "living_street"), "Wohnstraße (OSM)", False),
]


def outlier_hints(r: dict) -> tuple[list[str], bool]:
    hits = [(text, err) for _, test, text, err in _HINTS if test(r)]
    return [t for t, _ in hits], any(err for _, err in hits)


def etw30_tempo(df: pd.DataFrame, rules: RuleSet, cat: str = "ETW30", cat_col: str = "cat_final") -> dict:
    """Share of Soll-ETW30 km whose Ist-Tempo is at most the Soll speed; outliers with hints (guide 7.1)."""
    soll = rules.categories[cat].speed_kmh
    d = df[df[cat_col] == cat]
    speed = pd.to_numeric(d["speed_ist_kmh"], errors="coerce")
    at_or_below = d[speed <= soll]
    unknown = d[speed.isna()]
    out = d[speed > soll].copy()
    hints = [outlier_hints(r) for r in out.to_dict("records")]
    out["hints"] = [h for h, _ in hints]
    out["data_error_candidate"] = [e for _, e in hints]
    out = out.sort_values(["length_m", "segment_id"], ascending=[False, True]).reset_index(drop=True)
    return {"soll_kmh": soll, "km_total": d["length_m"].sum() / 1000.0,
            "km_at_or_below": at_or_below["length_m"].sum() / 1000.0,
            "km_unknown": unknown["length_m"].sum() / 1000.0, "outliers": out}


# --- data quality ----------------------------------------------------------------------------


def _known_share(s: pd.Series) -> float:
    return float((~s.map(_missing)).mean()) if len(s) else math.nan


def _quality_row(name: str, g: pd.DataFrame) -> dict:
    km = g["length_m"].sum()
    matched = g["match_quality"].isin(["exact", "partial"])
    row = {"bezirk": name, "n": len(g), "km": km / 1000.0,
           "conflation_hit_km": g.loc[matched, "length_m"].sum() / km if km else math.nan,
           "conflation_exact_km": g.loc[g["match_quality"] == "exact", "length_m"].sum() / km if km else math.nan}
    tags = {f"tag_{c}": _known_share(g[c]) if c in g.columns else math.nan for c in OSM_TAG_COLUMNS}
    row.update(tags)
    row["osm_tags_mean"] = float(pd.Series(tags).mean())
    row["missing_speed"] = float(g["speed_ist_kmh"].map(_missing).mean())
    hvs = g[_is_true(g["in_hvs"])]
    row["hvs_n"] = len(hvs)
    row["hvs_missing_dtv"] = float(hvs["dtv_official"].map(_missing).mean()) if len(hvs) else math.nan
    main = g[g["highway"].isin(MAIN_ROADS)]
    row["main_n"] = len(main)
    row["main_missing_dtv"] = float(main["dtv_official"].map(_missing).mean()) if len(main) else math.nan
    row["missing_dtv"] = float(g["dtv_official"].map(_missing).mean())
    return row


def data_quality(df: pd.DataFrame) -> pd.DataFrame:
    """Per district (largest first), then segments without district, then the total."""
    bez = df["bezirk"].map(lambda b: b if isinstance(b, str) and b else NO_DISTRICT)
    named = sorted((b for b in bez.unique() if b != NO_DISTRICT),
                   key=lambda b: (-df.loc[bez == b, "length_m"].sum(), b))
    rows = [_quality_row(b, df[bez == b]) for b in named]
    if (bez == NO_DISTRICT).any():
        rows.append(_quality_row(NO_DISTRICT, df[bez == NO_DISTRICT]))
    rows.append(_quality_row(TOTAL, df))
    return pd.DataFrame(rows)


# --- manual samples --------------------------------------------------------------------------

_TRUE = {"true", "ja", "j", "1", "yes", "y", "ok", "x"}
_FALSE = {"false", "nein", "n", "0", "no"}


def parse_ok(x: Any) -> bool | None:
    """check_ok cell -> True/False, None if empty or unreadable."""
    if _missing(x):
        return None
    if isinstance(x, bool):
        return x
    s = str(x).strip().lower()
    if s.endswith(".0"):
        s = s[:-2]
    if s in _TRUE:
        return True
    if s in _FALSE:
        return False
    return None


def sample_summary(df: pd.DataFrame, group_col: str, ok_col: str = "check_ok",
                   expected_col: str | None = None) -> pd.DataFrame:
    """Reviewed and disputed rows per group and in total.

    A row is reviewed if check_ok is filled, or (classification sample) if an expected category is entered;
    disputed if check_ok is no, or the expected category differs from group_col.
    """
    ok = df[ok_col].map(parse_ok) if ok_col in df.columns else pd.Series(None, index=df.index, dtype="object")
    if expected_col and expected_col in df.columns:
        exp = df[expected_col]
        from_expected = exp.map(lambda x: not _missing(x) and str(x).strip() != "")
        fill = ok.isna() & from_expected
        ok = ok.astype("object")
        ok[fill] = (exp[fill].astype(str).str.strip() == df.loc[fill, group_col].astype(str))
    reviewed = ok.notna()
    disputed = ok.map(lambda x: x is False)

    def row(name, mask):
        n_rev = int((reviewed & mask).sum())
        n_dis = int((disputed & mask).sum())
        return {"group": name, "n": int(mask.sum()), "reviewed": n_rev, "disputed": n_dis,
                "disputed_share": n_dis / n_rev if n_rev else math.nan}

    groups = list(dict.fromkeys(df[group_col].astype(str)))
    rows = [row(g, df[group_col].astype(str) == g) for g in groups]
    rows.append(row("alle", pd.Series(True, index=df.index)))
    return pd.DataFrame(rows)


def transect_summary(df: pd.DataFrame) -> dict:
    """Manually measured widths vs. the traffic-area width (S-XS-02)."""
    measured = pd.to_numeric(df.get("measured_m"), errors="coerce") if "measured_m" in df.columns else pd.Series(dtype=float)
    width = pd.to_numeric(df["width_traffic_m"], errors="coerce")
    both = measured.notna() & width.notna()
    diff = (measured[both] - width[both]).abs()
    return {"n": len(df), "measured": int(measured.notna().sum()),
            "mean_abs_diff_m": float(diff.mean()) if both.any() else None}


# --- open questions --------------------------------------------------------------------------

_ITEM = re.compile(r"^- \[( |x)\] (.*)$")


def open_questions(text: str) -> list[tuple[str, list[str]]]:
    """Unchecked items '- [ ] …' per '## ' section (continuation lines joined); sections without open items dropped."""
    out: list[tuple[str, list[str]]] = []
    section, items, current = None, [], None
    for line in text.splitlines():
        if line.startswith("## "):
            if section and items:
                out.append((section, items))
            section, items, current = line[3:].strip(), [], None
            continue
        m = _ITEM.match(line)
        if m:
            current = None
            if m.group(1) == " ":
                items.append(m.group(2).strip())
                current = len(items) - 1
        elif current is not None and line.startswith("  ") and line.strip():
            items[current] += " " + line.strip()
        else:
            current = None if not line.strip() or not line.startswith("  ") else current
    if section and items:
        out.append((section, items))
    return out
