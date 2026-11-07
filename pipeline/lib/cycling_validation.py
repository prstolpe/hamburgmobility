"""Helpers of the cycling validation (pipeline/c08_validate_cycling.py, prompts/21_web_validation_cycling.md).

Sensitivity: every numeric value with source_type assumption in cycling_rules.yaml and design_rules.yaml (an entry
inherits source_type from the entry above it, CLAUDE.md) is varied by -delta and +delta, one at a time. Only the
stages facility (c05), Soll cross section (c06) and junction type (c07) are rerun on their stored inputs; values that
feed the demand model, the network design, the principles or the junction geometry (routing, clustering) are listed
but not rerun. Counts and identifiers (seeds, number of sides, route types, lane defaults) are no thresholds and are
not varied.
"""

import copy
from collections.abc import Mapping
from dataclasses import dataclass

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from pipeline.lib.cycle_network import overlap_share

# Keys whose numbers are counts, identifiers or category codes, not thresholds.
STRUCTURAL_KEYS = {"seed", "sides", "sidewalk_sides", "tree_sides", "loading_sides", "max_lanes_per_direction",
                   "default_per_direction", "iterations", "top_n", "review_n", "od_pairs_per_category", "k_nearest",
                   "max_rounds", "hub_min_modes", "mixed_use_storeys", "lat", "lon"}
STRUCTURAL_SUFFIXES = ("route_types",)

# Sections whose assumptions the rerun chain reads (file, key prefix) -> first stage that reads them. Everything
# downstream of that stage is rerun as well (c05 -> c06 -> c07).
RECOMPUTED = {
    ("cycling", "separation_matrix"): "c05",
    ("cycling", "cycle_street"): "c05",
    ("cycling", "facility_assignment"): "c05",
    ("cycling", "widths_m"): "c05",
    ("design", "lanes"): "c06",
    ("design", "cross_section_allocation"): "c06",
    ("design", "profile_assignment"): "c06",
    ("design", "junctions.thresholds"): "c07",
    ("design", "junctions.method.[J-M-02].dtv_share_entering"): "c07",
}
# Why the other sections are not rerun (report text).
NOT_RECOMPUTED_REASON = {
    "cycle_categories": "Kategoriebeschreibung, Prinzipien (Prompt 17)",
    "principles": "Prinzipienprüfung (Prompt 17), keine Wirkung auf Führung, Fahrstreifen, Knoten",
    "principle_weights": "Prinzipienprüfung (Prompt 17); Gewichts-Sensitivität in reports/cycle_principles.md",
    "principle_scoring": "Prinzipienprüfung (Prompt 17)",
    "routing_impedance": "Routenwahl und Netzentwurf (Prompts 15–16) – je Lauf eine neue Umlegung",
    "cycle_graph": "Radgraph (Prompt 15)",
    "demand_model": "Nachfragemodell (Prompt 15) – je Lauf eine neue Umlegung",
    "network_design": "Netzentwurf (Prompt 16) – je Lauf eine neue Umlegung",
    "junctions.method": "Knotenbildung und Platz (J-M-01, J-M-03) – Geometrie, nicht neu gebildet",
}


@dataclass(frozen=True)
class Param:
    file: str              # cycling | design
    path: tuple            # keys and list indices into the raw YAML
    key: str               # dotted label, list items by id: lanes.rules.[L-02].target_vc.value
    value: float
    stage: str | None      # first rerun stage, None = not rerun
    skip: str | None       # structural | zero | None (varied)


def _stage(file: str, key: str) -> str | None:
    for (f, prefix), stage in RECOMPUTED.items():
        if f == file and (key == prefix or key.startswith(prefix + ".")):
            return stage
    return None


def _skip(parts: list[str], value: float) -> str | None:
    if any(p in STRUCTURAL_KEYS or p.endswith(STRUCTURAL_SUFFIXES) for p in parts):
        return "structural"
    if value == 0:
        return "zero"
    return None


def assumption_params(raw: dict, file: str) -> list[Param]:
    """All numeric values with (inherited) source_type assumption, in file order."""
    out: list[Param] = []

    def walk(node, path: tuple, parts: list[str], st):
        if isinstance(node, dict):
            st = node.get("source_type", st)
            for k, v in node.items():
                walk(v, (*path, k), [*parts, str(k)], st)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                label = f"[{v['id']}]" if isinstance(v, dict) and "id" in v else f"[{i}]"
                walk(v, (*path, i), [*parts, label], st)
        elif isinstance(node, (int, float)) and not isinstance(node, bool) and st == "assumption":
            key = ".".join(parts)
            out.append(Param(file, path, key, float(node), _stage(file, key), _skip(parts, float(node))))

    walk(raw, (), [], None)
    return out


def section(p: Param) -> str:
    """Report section of a parameter (first key, or junctions.method)."""
    return "junctions.method" if p.key.startswith("junctions.method") else p.key.split(".")[0]


def with_value(raw: dict, path: tuple, value: float) -> dict:
    out = copy.deepcopy(raw)
    node = out
    for k in path[:-1]:
        node = node[k]
    node[path[-1]] = value
    return out


def change_share(base: pd.Series, run: pd.Series, length: pd.Series) -> tuple[float, float]:
    """Share of rows (and of length) whose value differs from the base; missing on both sides is no change."""
    b, r = base.astype(object), run.astype(object)
    both_missing = b.isna().to_numpy() & r.isna().to_numpy()
    changed = (b.fillna("\0").to_numpy() != r.fillna("\0").to_numpy()) & ~both_missing
    w = length.to_numpy(dtype="float64")
    return float(changed.mean()) if len(changed) else 0.0, float(w[changed].sum() / w.sum()) if w.sum() else 0.0


def arm_rep_ids(legs: list[dict], base_facility: Mapping) -> list[str | None]:
    """Per junction arm the segment whose base facility the arm carries (merged dual carriageways keep the facility
    of one member); None for arms without a street segment (standalone cycle paths)."""
    out = []
    for leg in legs:
        ids = [i for i in leg["ids"] if i in base_facility]
        hit = next((i for i in ids if base_facility[i] == leg.get("facility")), ids[0] if ids else None)
        out.append(hit)
    return out


def official_by_district(soll: gpd.GeoDataFrame, official: gpd.GeoDataFrame, districts: gpd.GeoDataFrame,
                         buffer_m: float, official_status: tuple, planned_status: tuple) -> pd.DataFrame:
    """Soll network against the official Radnetz per Bezirk and for Hamburg (km).

    official_* = official lines (status in official_status) cut at the Bezirk boundaries; on_soll_hr / on_soll_any =
    their length within buffer_m of the Soll network RSV/HAUPT resp. RSV/HAUPT/BASIS (anywhere, so lines at a Bezirk
    boundary find their partner); soll_hr_* = Soll RSV/HAUPT edges of the Bezirk and their length near official lines.
    """
    cats = soll["cycle_cat_final"]
    hr = soll[cats.isin(("RSV", "HAUPT"))]
    any_ = soll[cats.isin(("RSV", "HAUPT", "BASIS"))]
    hr_buf = shapely.buffer(hr.geometry.values, buffer_m)
    any_buf = shapely.buffer(any_.geometry.values, buffer_m)
    off = official[official["status"].isin(official_status)]
    plan = official[official["status"].isin(planned_status)]
    off_buf = shapely.buffer(off.geometry.values, buffer_m)
    rows = []
    for name, poly in zip(districts["name"], districts.geometry):
        off_d = shapely.intersection(off.geometry.values, poly)
        off_d = off_d[~shapely.is_empty(off_d)]
        plan_d = shapely.intersection(plan.geometry.values, poly)
        plan_d = plan_d[~shapely.is_empty(plan_d)]
        hr_d = hr[hr["bezirk"] == name].geometry.values
        off_len, plan_len, hr_len = shapely.length(off_d), shapely.length(plan_d), shapely.length(hr_d)
        rows.append({
            "bezirk": name, "official_km": off_len.sum() / 1000,
            "official_on_soll_hr_km": (off_len * overlap_share(off_d, hr_buf)).sum() / 1000,
            "official_on_soll_any_km": (off_len * overlap_share(off_d, any_buf)).sum() / 1000,
            "planned_km": plan_len.sum() / 1000,
            "planned_on_soll_hr_km": (plan_len * overlap_share(plan_d, hr_buf)).sum() / 1000,
            "soll_hr_km": hr_len.sum() / 1000,
            "soll_hr_on_official_km": (hr_len * overlap_share(hr_d, off_buf)).sum() / 1000})
    t = pd.DataFrame(rows)
    t["soll_hr_additional_km"] = t["soll_hr_km"] - t["soll_hr_on_official_km"]
    total = t.drop(columns="bezirk").sum().to_dict()
    t = pd.concat([t, pd.DataFrame([{"bezirk": "Hamburg", **total}])], ignore_index=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        t["official_on_soll_hr_share"] = t["official_on_soll_hr_km"] / t["official_km"]
        t["official_on_soll_any_share"] = t["official_on_soll_any_km"] / t["official_km"]
        t["soll_hr_on_official_share"] = t["soll_hr_on_official_km"] / t["soll_hr_km"]
    return t
