"""Export of the cycling layers (prompts/21_web_validation_cycling.md): tile attributes, profile blocks, labels.

Inputs are the interim results of prompts 16-20 (cycle_network, cycle_facility, cross_section_soll, junctions,
cycle_principles) and the official Radnetz. Texts come from config/plain_language.yaml (section `cycling`), cycle
category names from cycling_rules.yaml, degrade step texts from design_rules.yaml. Like pipeline/lib/export.py this
module transforms to EPSG:4326; nothing here computes a Soll value.
"""

import json
import math
from dataclasses import dataclass

import geopandas as gpd
import pandas as pd

from config.schema.cycling_model import NO_CYCLE_CATEGORY, CyclingRuleSet
from config.schema.design_model import DesignRuleSet
from pipeline.lib import profile as pf
from pipeline.lib.export import EXPORT_CRS

CYCLE_CATS = ("RSV", "HAUPT", "BASIS", "ERSCHL")
CYCLE_RANK = {c: len(CYCLE_CATS) - i for i, c in enumerate(CYCLE_CATS)}
PRINCIPLES = ("cohesion", "directness", "safety", "comfort", "attractiveness")
OFFICIAL_GROUPS = ("Bestand", "In Arbeit")  # every other status of the WFS is a planned addition or improvement

# Display groups of the junction types (map symbols): one shape per group on the website.
JUNCTION_GROUPS = {
    "roundabout": ("roundabout_single_lane_cycle_priority", "roundabout_single_lane_cycle_yield", "turbo_roundabout"),
    "signal": ("signal_protected", "cycle_crossing_signal"),
    "priority": ("priority_raised", "priority_flat_coloured", "cycle_crossing_priority"),
    "continuous": ("continuous_footway_exit",),
    "equal": ("equal_right_before_left",),
    "grade_separated": ("grade_separated_cycle",),
}
_GROUP_OF = {t: g for g, types in JUNCTION_GROUPS.items() for t in types}


# --- small helpers -------------------------------------------------------------------------------


def _missing(v) -> bool:
    if v is None or v is pd.NA:
        return True
    try:
        return isinstance(v, float) and math.isnan(v)
    except TypeError:
        return False


def _str(v) -> str | None:
    return v if isinstance(v, str) and v else None


def _num(v, digits: int = 2) -> float | None:
    if _missing(v):
        return None
    return round(float(v), digits)


def _int(v) -> int | None:
    return None if _missing(v) else int(v)


def _split(v) -> list[str]:
    return [x for x in v.split("|") if x] if isinstance(v, str) else []


def _wgs(df: pd.DataFrame, geometry, crs) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(df.reset_index(drop=True), geometry=list(geometry), crs=crs).to_crs(EXPORT_CRS)


# --- labels --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Labels:
    t: dict                     # plain_language.yaml, section cycling
    cycle_cats: dict            # code -> label_de (cycling_rules.yaml)
    degrade: dict               # D1..D7 -> action (design_rules.yaml)
    rows: dict                  # J-01.. -> decision table row

    @classmethod
    def from_rules(cls, texts: dict, cyc: CyclingRuleSet, des: DesignRuleSet) -> "Labels":
        degrade = {d["step"]: d["action"] for d in des.cross_section_allocation["degrade_cascade_if_not_fit"]}
        rows = {r.id: r.model_dump(by_alias=True) for r in des.junctions.decision_table.rows}
        cats = {c: cyc.cycle_categories[c]["label_de"] for c in CYCLE_CATS}
        return cls(t=texts["cycling"], cycle_cats=cats, degrade=degrade, rows=rows)

    def cat(self, code) -> dict:
        code = code if isinstance(code, str) else NO_CYCLE_CATEGORY
        return {"code": code, "label": self.cycle_cats.get(code, self.t["no_cycle_category"])}

    def text(self, section: str, code) -> str | None:
        return self.t[section].get(code) if isinstance(code, str) else None


def cycling_meta(labels: Labels) -> dict:
    """Labels for meta.json (legends, profiles, method page)."""
    t = labels.t
    return {
        "disclaimer": t["disclaimer"], "cycle_categories": labels.cycle_cats, "no_cycle_category": t["no_cycle_category"],
        "elements": {e: {"label": pf.LABEL_DE[e], "color": pf.ELEMENT_COLOURS.get(e, "#cccccc")} for e in pf.LABEL_DE},
        **{k: t[k] for k in ("facility", "gap", "fit", "lanes", "side", "junction_type", "junction_group",
                             "junction_ist", "junction_result", "official_status", "principles", "confidence")},
    }


# --- tiles ---------------------------------------------------------------------------------------


def network_tile_frame(net: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Edges of the Soll cycle network (RSV..ERSCHL): edge id, linked segment, category, official overlap, Bezirk."""
    sub = net[net["cycle_cat_final"].isin(CYCLE_CATS)]
    seg = sub["segment_id"].where(sub["segment_id"].map(_str).notna(), sub["sidepath_of"])
    df = pd.DataFrame({"id": sub["edge_id"].to_numpy(), "seg": seg.map(_str).to_numpy(),
                       "cc": sub["cycle_cat_final"].to_numpy(), "off": sub["official_network"].map(_str).to_numpy(),
                       "bz": sub["bezirk"].map(_str).to_numpy()})
    return _wgs(df, sub.geometry, net.crs)


def lanes_change(soll, ist) -> str | None:
    """Soll lanes per direction against Ist: shared | fewer | same | more | ist_unknown; None without Soll."""
    if not isinstance(soll, str):
        return None
    if soll == "shared":
        return "shared"
    if _missing(ist):
        return "ist_unknown"
    s, i = int(soll), int(ist)
    return "fewer" if s < i else "same" if s == i else "more"


def segment_tile_frame(fac: gpd.GeoDataFrame, xs: pd.DataFrame) -> gpd.GeoDataFrame:
    """One line per street segment: cycle category, facility Soll (after prompt 19) and Ist, gap, widths, lanes, fit."""
    x = xs.set_index("segment_id").reindex(fac["segment_id"])
    df = pd.DataFrame({
        "id": fac["segment_id"].to_numpy(), "bz": fac["bezirk"].map(_str).to_numpy(),
        "cc": fac["cycle_cat_final"].fillna(NO_CYCLE_CATEGORY).to_numpy(),
        "fs": x["cycle_facility_final"].map(_str).to_numpy(), "fi": fac["cycle_facility_ist"].map(_str).to_numpy(),
        "gap": fac["facility_gap"].map(_str).to_numpy(),
        "ws": [_num(v) for v in x["cycle_width_final_m"]], "wi": [_num(v) for v in fac["cycle_width_ist_m"]],
        "ls": x["lanes_per_dir_soll"].map(_str).to_numpy(), "li": [_int(v) for v in x["lanes_per_dir_ist"]],
        "ld": [lanes_change(s, i) for s, i in zip(x["lanes_per_dir_soll"], x["lanes_per_dir_ist"])],
        "fit": x["fit_class"].map(_str).to_numpy()})
    df["wi"] = df["wi"].astype("float64")
    df["ws"] = df["ws"].astype("float64")
    df["li"] = df["li"].astype("Int64")
    return _wgs(df, fac.geometry, fac.crs)


def junction_group(jtype) -> str:
    return _GROUP_OF.get(jtype, "none") if isinstance(jtype, str) else "none"


def junction_tile_frame(j: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Junction points: Soll type (final) and its symbol group, Ist type, comparison, priority rank, top cycle category."""
    df = pd.DataFrame({
        "id": j["node_id"].astype(str).to_numpy(), "js": j["junction_type_final"].map(_str).to_numpy(),
        "grp": j["junction_type_final"].map(junction_group).to_numpy(), "ji": j["junction_type_ist"].map(_str).to_numpy(),
        "res": j["ist_result"].map(_str).to_numpy(), "act": j["action_needed"].fillna(False).astype(bool).astype(int).to_numpy(),
        "pr": [_int(v) for v in j["priority_rank"]], "cc": j["top_cycle_cat"].map(_str).to_numpy(),
        "bz": j["bezirk"].map(_str).to_numpy()})
    df["pr"] = df["pr"].astype("Int64")
    return _wgs(df, j.geometry, j.crs)


def official_group(status) -> str:
    return status if status in OFFICIAL_GROUPS else "planned"


def official_tile_frame(off: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Official Radnetz Hamburg (WFS, dl-de/by-2.0) for comparison: status and display group."""
    df = pd.DataFrame({"st": off["status"].to_numpy(), "grp": off["status"].map(official_group).to_numpy()})
    return _wgs(df, off.geometry, off.crs)


# --- profiles ------------------------------------------------------------------------------------


def principle_scores(principles: pd.DataFrame, net: pd.DataFrame) -> dict[str, dict]:
    """Principle scores Ist/Soll per segment_id from the edge level of cycle_principles: the edge of the highest
    cycle category (then the longest) among the edges on or beside the segment."""
    edges = principles[principles["level"] == "edge"]
    seg = net.set_index("edge_id")
    link = seg["segment_id"].where(seg["segment_id"].map(_str).notna(), seg["sidepath_of"])
    e = edges.assign(segment_id=edges["id"].map(link), rank=edges["category"].map(CYCLE_RANK).fillna(0))
    e = e[e["segment_id"].map(_str).notna()]
    best = e.sort_values(["segment_id", "rank", "length_m"], ascending=[True, False, False]).drop_duplicates("segment_id")
    out = {}
    for r in best.itertuples(index=False):
        d = r._asdict()
        out[d["segment_id"]] = {
            "category": d["category"],
            **{v: {**{p: _num(d[f"{p}_{v}"]) for p in PRINCIPLES}, "score": _num(d[f"score_{v}"])} for v in ("ist", "soll")}}
    return out


def _steps(value, labels: Labels) -> list[dict]:
    return [{"step": s, "text": labels.t["degrade_fallback"] if s == "fallback" else labels.degrade.get(s, s)}
            for s in _split(value)]


def segment_cycling_block(f: pd.Series, x: pd.Series, scores: dict | None, labels: Labels) -> dict:
    """Cycling part of a segment profile: category, facility and width (with DE and NL values), side, lanes,
    Soll cross section with degrade steps in plain text, flags, principle scores."""
    t = labels.t
    soll_p18 = _str(f["cycle_facility_soll"])
    soll = _str(x["cycle_facility_final"])
    same_facility = soll is not None and soll == soll_p18  # DE/NL values belong to the prompt-18 facility
    flags = [t["facility_flags"][k] for k in _split(f["facility_flags"]) if k in t["facility_flags"]]
    flags += [t["profile_flags"][k] for k in _split(x["profile_flags"]) if k in t["profile_flags"]]
    elements = json.loads(x["profile_elements"]) if isinstance(x["profile_elements"], str) else []
    ist_lanes = _int(x["lanes_per_dir_ist"])
    change = lanes_change(x["lanes_per_dir_soll"], x["lanes_per_dir_ist"])
    return {
        "cycle_cat": labels.cat(f["cycle_cat_final"]),
        "facility": {"soll": soll, "soll_text": labels.text("facility", soll),
                     "ist": _str(f["cycle_facility_ist"]), "ist_text": labels.text("facility", f["cycle_facility_ist"]),
                     "osm_ist_text": labels.text("facility_osm", f["cycle_osm_ist"]),
                     "gap": _str(f["facility_gap"]), "gap_text": labels.text("gap", f["facility_gap"]),
                     "fallback_used": soll is not None and soll_p18 is not None and soll != soll_p18},
        "width": {"soll_m": _num(x["cycle_width_final_m"]), "ist_m": _num(f["cycle_width_ist_m"]),
                  "de_m": _num(f["cycle_width_de_m"]) if same_facility else None,
                  "nl_m": _num(f["cycle_width_nl_m"]) if same_facility else None},
        "side": _str(x["cycle_side"]), "side_text": labels.text("side", x["cycle_side"]),
        "lanes": {"soll": _str(x["lanes_per_dir_soll"]), "ist": ist_lanes, "change": change,
                  "change_text": labels.text("lanes", change), "bus_lane": bool(x["bus_lane_soll"]) if not _missing(x["bus_lane_soll"]) else None,
                  "median": bool(x["median_soll"]) if not _missing(x["median_soll"]) else None},
        "profile": {"elements": [{"element": e["element"], "width_m": _num(e["width_m"]), "side": e.get("side")} for e in elements],
                    "required_m": _num(x["total_required_m"]), "available_m": _num(x["available_m"]),
                    "fit": _str(x["fit_class"]), "fit_text": labels.text("fit", x["fit_class"]),
                    "steps": _steps(x["degrade_steps_applied"], labels), "cat_change_proposal": _str(x["cat_change_proposal"])},
        "flags": list(dict.fromkeys(flags)),
        "confidence": {"facility": labels.text("confidence", f["facility_confidence"]),
                       "profile": labels.text("confidence", x["profile_confidence"])},
        "principles": scores,
    }


def _rule_text(r: pd.Series, labels: Labels) -> dict | None:
    rid = _str(r["decision_rule"])
    if rid is None:
        return None
    row = labels.rows.get(rid, {})
    soll = labels.text("junction_type", r["junction_type_soll"]) or "kein Typ"
    text = f"Regel {rid} (Kategoriepaar {r['pair'] if _str(r['pair']) else row.get('legs', '–')}) ergibt hier: {soll}"
    if row.get("note"):
        text += f". {row['note']}"
    return {"id": rid, "text": text}


def junction_profile(r: pd.Series, labels: Labels, version: str) -> dict:
    """Junction profile ("Steckbrief Knoten"): Soll and Ist type, cyclist treatment, reason, conflicts."""
    t = labels.t
    legs = json.loads(r["legs"]) if isinstance(r["legs"], str) else []
    override = r["junction_type_source"] == "override"
    return {
        "id": str(r["node_id"]), "names": _str(r["names"]), "bezirk": _str(r["bezirk"]), "pair": _str(r["pair"]),
        "legs": [{"name": _str(leg.get("name")), "cat": leg.get("cat"), "cycle_cat": labels.cat(leg.get("cycle_cat")),
                  "facility_text": labels.text("facility", leg.get("facility")), "dtv": _num(leg.get("dtv"), 0)} for leg in legs],
        "entering_dtv": _num(r["entering_dtv_sum"], 0), "space_radius_m": _num(r["space_radius_m"], 1),
        "tram": bool(r["tram_present"]), "signal_ist": bool(r["signal_present_ist"]),
        "soll": {"code": _str(r["junction_type_final"]), "text": labels.text("junction_type", r["junction_type_final"]),
                 "group": junction_group(r["junction_type_final"])},
        "proposed": {"code": _str(r["junction_type_soll"]), "text": labels.text("junction_type", r["junction_type_soll"])},
        "ist": {"code": _str(r["junction_type_ist"]), "text": labels.text("junction_ist", r["junction_type_ist"])},
        "result": {"code": _str(r["ist_result"]), "text": labels.text("junction_result", r["ist_result"])},
        "action_needed": bool(r["action_needed"]) if not _missing(r["action_needed"]) else False,
        "priority_rank": _int(r["priority_rank"]),
        "rule": _rule_text(r, labels),
        "treatment": _str(r["treatment_text"]), "treatment_ids": _split(r["cyclist_treatment"]),
        "conflicts": [t["junction_flags"].get(k, k) for k in _split(r["conflict_flags"])],
        "confidence": {"code": _str(r["confidence"]), "text": labels.text("confidence", r["confidence"])},
        "top_cycle_cat": labels.cat(r["top_cycle_cat"]),
        "crashes": {"cyc": int(r["crashes_cyc"]), "cyc_severe": int(r["crashes_cyc_severe"])},
        "override": {"reason": _str(r["junction_override_reason"]), "author": _str(r["junction_override_author"]),
                     "date": None if _missing(r["junction_override_date"]) else str(r["junction_override_date"])} if override else None,
        "version": version,
    }


# --- downloads -----------------------------------------------------------------------------------


def download_frame(df: gpd.GeoDataFrame, columns: dict) -> gpd.GeoDataFrame:
    """Public columns of a cycling download (keys of plain_language.yaml cycling.columns.<file>), in EPSG:4326.
    Lists and JSON traces are never part of it."""
    cols = [c for c in columns if c != "geometry" and c in df.columns]
    out = df[cols].copy()
    for c in cols:
        if out[c].map(lambda v: isinstance(v, (list, tuple, dict))).any():
            raise ValueError(f"download column {c} holds lists; flatten it first")
    return gpd.GeoDataFrame(out, geometry=df.geometry.to_numpy(), crs=df.crs).to_crs(EXPORT_CRS).reset_index(drop=True)


def robustness(row) -> dict | None:
    """Sensitivity result of one segment or junction (data/interim/validation_cycling.parquet) for the profile."""
    if row is None:
        return None
    trig = json.loads(row["triggers"]) if isinstance(row["triggers"], str) else {}
    return {"n_runs": int(row["n_runs"]), "facility_changes": int(row["facility_changes"]),
            "lanes_changes": int(row["lanes_changes"]), "type_changes": int(row["type_changes"]),
            "delta": float(row["delta"]), "triggers": trig}
