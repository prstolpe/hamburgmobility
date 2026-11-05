"""Export helpers (stage 9): plain text from rule_trace, public columns, search index, tile attributes.

Texts come from config/plain_language.yaml, thresholds from config/rules.yaml. This is the only place where
geometries are transformed to EPSG:4326 (CLAUDE.md).
"""

import json
import re
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml

from config.schema.rules_model import RuleSet
from pipeline.lib import expr
from pipeline.lib.classify import _ref_resolver
from pipeline.lib.manifest import REPO_ROOT

TEXTS_PATH = REPO_ROOT / "config" / "plain_language.yaml"
EXPORT_CRS = "EPSG:4326"

# Columns of the download files (GeoParquet, GeoJSON, CSV), in this order. Crashes only as counts per segment.
PUBLIC_COLUMNS = [
    "segment_id", "name", "bezirk", "highway", "length_m", "osm_way_ids",
    "cat_final", "cat_proposed", "cat_cascade", "cat_final_source", "override_reason", "confidence",
    "sens_change_rate", "sens_uncertain", "rule_path",
    "speed_ist_kmh", "speed_ist_source", "in_hvs", "dtv_official", "bus_trips_weekday", "in_cycle_network",
    "separated_cycle_track_present", "cycle_lane_present", "centre_line", "parking_along_carriageway",
    "conn_score", "place_score", "schools_or_kitas_within_m", "population_100m", "shop_frontage_share",
    "width_median_m", "width_p10_m", "feasibility_GOW50", "feasibility_GOW30_narrow", "feasibility_ETW30",
    "flags",
    "disc_speed", "disc_design", "disc_use", "disc_max", "disc_type",
    "crashes_ped_cyc", "crashes_ped", "crashes_cyc", "crashes_severe_fatal", "crash_years",
    "risk", "priority",
]

# Short attribute names in the vector tiles (layer `segments`) -> source column.
TILE_COLUMNS = {
    "id": "segment_id", "name": "name", "bz": "bezirk", "cat": "cat_final", "spd": "speed_ist_kmh", "hvs": "in_hvs",
    "dt": "disc_type", "dm": "disc_max", "pr": "priority", "w": "width_p10_m", "fe": "feasibility",
    "bus": "bus_trips_weekday", "cyc": "in_cycle_network", "acc": "crashes_ped_cyc", "conf": "confidence",
    "un": "sens_uncertain",
}

# Feasibility column that belongs to each Soll category (crosssection targets).
FEASIBILITY_BY_CATEGORY = {"GOW50": "feasibility_GOW50", "GOW30": "feasibility_GOW30_narrow",
                           "ETW30": "feasibility_ETW30"}

_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_.]*)(?:\|([^}]*))?\}")


def load_texts(path: str | Path = TEXTS_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def ref_resolver(rules: RuleSet):
    """thresholds.<name> / required_width.<name> -> number (same as the cascade)."""
    return _ref_resolver(rules)


def fmt_number(x: float, digits: int) -> str:
    return f"{x:,.{digits}f}".replace(",", " ").replace(".", ",")


def _format(v: Any, spec: str | None) -> str:
    if expr.is_missing(v):
        return "unbekannt"
    if spec == "yesno":
        return "ja" if bool(v) else "nein"
    if spec == "%":
        return f"{fmt_number(float(v) * 100, 0)} %"
    if spec and spec.startswith(".") and spec.endswith("f"):
        return fmt_number(float(v), int(spec[1:-1]))
    if hasattr(v, "item"):
        v = v.item()
    return str(v)


def render(template: str, values: dict, resolve) -> str:
    """Fill {name|format}; dotted names are references into rules.yaml (KeyError if unknown)."""
    def sub(m: re.Match) -> str:
        name, spec = m.group(1), m.group(2)
        v = resolve(name) if "." in name else values.get(name)
        return _format(v, spec)
    return _PLACEHOLDER.sub(sub, template)


def _fragments(entries: list[dict], values: dict, resolve) -> list[str]:
    out = []
    for e in entries:
        if "when" in e:
            ctx = expr.Context(values, resolve, near_threshold=0.0)
            if expr.evaluate(expr.parse(e["when"]), ctx).value is not True:
                continue
        out.append(render(e["text"], values, resolve))
    return out


def rule_reasons(trace: list[dict], rules: RuleSet, texts: dict) -> list[dict]:
    """Plain-text reasons for the steps of a rule_trace that have a text (passed, or failed where helpful)."""
    resolve = ref_resolver(rules)
    out = []
    for step in trace:
        if "part" in step:
            continue
        entry = texts["rules"].get(step["id"], {})
        passed = bool(step.get("passed"))
        frags = _fragments(entry.get("passed" if passed else "failed", []), step.get("inputs", {}), resolve)
        if frags:
            out.append({"rule": step["id"], "passed": passed, "text": "; ".join(frags)})
    return out


def confidence_info(level: str, reasons: list[str], texts: dict) -> dict:
    """Traffic light: level, summary and the reasons in plain text."""
    c = texts["confidence"]
    lines = []
    for r in reasons:
        kind, _, rest = r.partition(":")
        feature = rest.split("~")[0]
        label = texts["features"].get(feature, feature)
        template = c["reasons"].get(kind)
        lines.append(template.format(feature=label) if template else r)
    return {"level": level, "summary": c.get(level, ""), "reasons": lines}


def sensitivity_info(values: dict, rules: RuleSet, texts: dict, runs: int, delta: float) -> dict:
    """Robustness of the category from pipeline/validate.py (V-SENS-01/02, V-UNC-01) in plain text."""
    t = texts["sensitivity"]
    rate = values.get("sens_change_rate")
    if expr.is_missing(rate):
        return {"change_rate": None, "uncertain": None, "alternative": None, "text": t["not_assessed"],
                "uncertain_text": None, "oat_intro": None, "triggers": []}
    rate = float(rate)
    uncertain = bool(values.get("sens_uncertain"))
    alt = values.get("sens_alt_category")
    alt = None if expr.is_missing(alt) else str(alt)
    if rate == 0 or alt is None:
        text = t["stable"].format(runs=runs)
    else:
        text = t["changes"].format(rate=f"{fmt_number(rate * 100, 0)} %", runs=runs,
                                   alt=f"{rules.categories[alt].label_de} ({alt})")
    raw = values.get("sens_oat_changes")
    keys = json.loads(raw) if isinstance(raw, str) and raw else []
    triggers = []
    for k in keys:
        key, _, sign = k.rpartition(":")
        triggers.append(f"{t['params'].get(key, key)} {t['direction'][sign]}")
    return {"change_rate": round(rate, 3), "uncertain": uncertain, "alternative": alt, "text": text,
            "uncertain_text": t["uncertain"] if uncertain else None,
            "oat_intro": t["oat_intro"].format(delta=f"{fmt_number(delta * 100, 0)} %") if triggers else None,
            "triggers": triggers}


# --- frames ----------------------------------------------------------------------------------


def _join_list(v) -> str | None:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return ";".join(str(int(x)) for x in v)


def public_frame(seg: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Public columns (those present), osm_way_ids as 'id;id', in EPSG:4326."""
    cols = [c for c in PUBLIC_COLUMNS if c in seg.columns]
    out = seg[cols + ["geometry"]].copy()
    if "osm_way_ids" in out.columns:
        out["osm_way_ids"] = out["osm_way_ids"].map(_join_list)
    return gpd.GeoDataFrame(out, geometry="geometry", crs=seg.crs).to_crs(EXPORT_CRS).reset_index(drop=True)


def search_index(seg_wgs84: gpd.GeoDataFrame) -> list[dict]:
    """One entry per street name and district: bbox (west, south, east, north), number of segments, ids."""
    named = seg_wgs84[seg_wgs84["name"].map(lambda v: isinstance(v, str) and v != "")]
    out = []
    for (name, bezirk), g in named.groupby(["name", "bezirk"], sort=True):
        w, s, e, n = g.total_bounds
        out.append({"name": name, "bezirk": bezirk, "n": len(g),
                    "bbox": [round(float(w), 6), round(float(s), 6), round(float(e), 6), round(float(n), 6)],
                    "ids": sorted(g["segment_id"])})
    return out


def tile_frame(seg_wgs84: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Slim attributes for the vector tiles (TILE_COLUMNS), feasibility of the own Soll category."""
    df = seg_wgs84.copy()
    df["feasibility"] = [r.get(FEASIBILITY_BY_CATEGORY.get(r["cat_final"], ""), None) for _, r in df.iterrows()]
    out = pd.DataFrame({short: df[col] if col in df.columns else None for short, col in TILE_COLUMNS.items()})
    for c in ("hvs", "cyc", "un"):
        out[c] = out[c].map(lambda v: None if expr.is_missing(v) else int(bool(v)))
    for c in ("w", "pr", "bus"):
        out[c] = pd.to_numeric(out[c], errors="coerce").round(2)
    return gpd.GeoDataFrame(out, geometry=df.geometry.to_numpy(), crs=seg_wgs84.crs)


def district_slug(name: str) -> str:
    """ASCII file name part for a Bezirk (table/<slug>.json): umlauts spelled out, spaces to hyphens."""
    import re

    s = name.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")
