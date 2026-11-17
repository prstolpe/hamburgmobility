"""Special places (prompts/26, config/special_places.yaml): profile block per segment, map layer and meta entry.

The comparison sentences are filled from config/plain_language.yaml (section special_places) with the segment's
rule result; nothing here changes the classification. Geometries are computed in EPSG:25832 and transformed to
EPSG:4326 only for the output file (CLAUDE.md).
"""

import dataclasses
import datetime as dt
import json

import geopandas as gpd
import pandas as pd

from config.schema.special_places_model import Place, SpecialPlaces
from pipeline.lib import expr
from pipeline.lib import profile as pf
from pipeline.lib.export import EXPORT_CRS, _fragments

GEOJSON_NAME = "special_places.geojson"


def _no_ref(name: str):
    raise KeyError(f"special_places texts use no rule references: {name}")


def _date_de(d: dt.date) -> str:
    return d.strftime("%d.%m.%Y")


def _clean(v):
    return None if expr.is_missing(v) else expr.clean_value(v)


def comparison_values(seg: pd.Series, fac: pd.Series | None, xs: pd.Series | None, glossary: dict) -> dict:
    """Inputs of the comparison sentences for one segment (missing cycling data stays missing)."""
    cat = seg["cat_final"]
    soll = None
    if xs is not None:
        soll = _clean(xs.get("cycle_facility_final"))
    if soll is None and fac is not None:
        soll = _clean(fac.get("cycle_facility_soll"))
    return {"cat": cat, "cat_plain": glossary["categories"].get(cat, {}).get("plain", cat),
            "cycle_facility_soll": soll, "cycle_cat": _clean(fac.get("cycle_cat_final")) if fac is not None else None,
            "bus_trips_weekday": _clean(seg.get("bus_trips_weekday")), "speed_ist_kmh": _clean(seg.get("speed_ist_kmh"))}


def comparison(measure: str, values: dict, texts: dict) -> dict:
    """First matching `compare` sentence and all matching `notes` of the measure."""
    t = texts["special_places"]["measures"][measure]
    compare = next(iter(_fragments(_first_match(t["compare"], values), values, _no_ref)), "")
    return {"compare": compare, "notes": _fragments(t.get("notes", []), values, _no_ref)}


def _first_match(entries: list[dict], values: dict) -> list[dict]:
    for e in entries:
        if "when" not in e:
            return [e]
        ctx = expr.Context(values, _no_ref, near_threshold=0.0)
        if expr.evaluate(expr.parse(e["when"]), ctx).value is True:
            return [e]
    return []


def _band(place: Place, measure_plain: str, texts: dict) -> str:
    t = texts["special_places"]
    return t["band"].format(title=place.title, kind_plain=t["kind"][place.kind], by=t["by"].get(place.kind, "").strip(),
                            measure_plain=measure_plain).replace("  ", " ").replace(" :", ":")


def _status_line(place: Place, texts: dict) -> str:
    return texts["special_places"]["status_line"].format(status_date=_date_de(place.status_date), status=place.status)


def proposal_input(base: pf.SegmentInput, change, parking, p: pf.ProfileParams) -> pf.SegmentInput:
    """Inputs of our cross-section logic with the measure applied: category and/or cycle facility replaced, the
    cycle width then follows the new facility, parking sides follow the category (PRF-03)."""
    if change is None:
        return base
    cat = change.cat or base.cat
    upd = {"cat": cat, "parking_sides": pf.parking_sides_soll(parking, cat, p)}
    if change.facility:
        upd.update(facility=change.facility, fallback=None, cycle_width=None)
    return dataclasses.replace(base, **upd)


def proposal_profiles(sp: SpecialPlaces, inputs: dict[str, tuple[pf.SegmentInput, object, object]],
                      p: pf.ProfileParams, fit_texts: dict) -> dict[str, dict]:
    """segment_id -> cross section of the proposal ("Querschnitt im Vorschlag"), computed with the same logic and
    parameters as the Soll cross section (pipeline/lib/profile.py, config/design_rules.yaml).
    inputs: segment_id -> (SegmentInput of the rule result, parking tags, available width)."""
    out = {}
    for place in sp.places:
        for g in place.segments:
            change = sp.measures[g.measure].profile
            for sid in g.segment_ids:
                if sid not in inputs or change is None:
                    continue
                base, parking, available = inputs[sid]
                res = pf.evaluate_profile(proposal_input(base, change, parking, p), available, p)
                out[sid] = {"elements": [{"element": e["element"], "width_m": e["width_m"], "side": e["side"]} for e in res.elements],
                            "required_m": res.total_required_m,
                            "available_m": None if res.available_m is None else round(res.available_m, 2), "fit": res.fit_class,
                            "fit_text": fit_texts.get(res.fit_class), "steps": res.degrade_steps_applied}
    return out


def _with_same(profiles: dict | None, sid: str, xs: pd.DataFrame | None) -> dict | None:
    """The proposal's cross section, marked `same_as_soll` when it equals our Soll cross section (then the website
    shows no second sketch)."""
    prof = (profiles or {}).get(sid)
    if prof is None or xs is None or sid not in xs.index or not isinstance(xs.at[sid, "profile_elements"], str):
        return prof
    soll = [{"element": e["element"], "width_m": e["width_m"], "side": e["side"]} for e in json.loads(xs.at[sid, "profile_elements"])]
    return {**prof, "same_as_soll": soll == prof["elements"]}


def segment_blocks(sp: SpecialPlaces, seg: pd.DataFrame, fac: pd.DataFrame | None, xs: pd.DataFrame | None,
                   texts: dict, glossary: dict, profiles: dict[str, dict] | None = None) -> dict[str, dict]:
    """segment_id -> profile block `special_place` (only for segments of a place)."""
    s = seg.set_index("segment_id")
    f = fac.set_index("segment_id") if fac is not None else None
    x = xs.set_index("segment_id") if xs is not None else None
    out = {}
    for place in sp.places:
        for g in place.segments:
            measure_plain = sp.measures[g.measure].label_plain
            for sid in g.segment_ids:
                if sid not in s.index:
                    continue
                row = s.loc[sid]
                values = comparison_values(row, f.loc[sid] if f is not None and sid in f.index else None,
                                           x.loc[sid] if x is not None and sid in x.index else None, glossary)
                out[sid] = {"place": place.id, "title": place.title, "kind": place.kind, "measure": g.measure,
                            "measure_plain": measure_plain, "band": _band(place, measure_plain, texts),
                            "status_line": _status_line(place, texts), "colour": place.theme.palette["main"],
                            **comparison(g.measure, values, texts), "profile": _with_same(profiles, sid, x),
                            "profile_note": texts["special_places"]["measures"][g.measure].get("profile_note")}
    return out


def place_frame(sp: SpecialPlaces, seg: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """One line per segment of a place (EPSG:25832) with its measure."""
    rows = []
    s = seg.set_index("segment_id")
    for place in sp.places:
        for g in place.segments:
            for sid in g.segment_ids:
                if sid in s.index:
                    r = s.loc[sid]
                    rows.append({"place": place.id, "measure": g.measure, "id": sid, "name": r["name"], "geometry": r.geometry})
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=seg.crs)


def geojson_frame(lines: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """The lines of all places in EPSG:4326 (data/out/special_places.geojson)."""
    return lines.to_crs(EXPORT_CRS)[["place", "measure", "id", "name", "geometry"]]


def meta_entry(sp: SpecialPlaces, lines: gpd.GeoDataFrame, blocks: dict[str, dict], texts: dict) -> dict:
    """meta.special_places: texts of the website, one entry per place with bbox, counts per measure and the
    comparison sentences of its segments (for the place card, level 3)."""
    t = texts["special_places"]
    places = []
    for p in sp.places:
        mine = lines[lines["place"] == p.id]
        bbox = [round(float(v), 6) for v in mine.to_crs(EXPORT_CRS).total_bounds] if len(mine) else None
        measures = []
        for g in p.segments:
            m = mine[mine["measure"] == g.measure]
            compares = {}
            for sid in g.segment_ids:
                b = blocks.get(sid)
                if b:
                    compares[b["compare"]] = compares.get(b["compare"], 0) + 1
            measures.append({"measure": g.measure, "label": sp.measures[g.measure].label_plain, "streets": g.streets,
                             "n_segments": int(len(m)), "km": round(float(m.length.sum()) / 1000, 2),
                             "compare": [{"text": k, "n": v} for k, v in compares.items()]})
        places.append({"id": p.id, "title": p.title, "kind": p.kind, "kind_plain": t["kind"][p.kind],
                       "initiator": p.initiator, "status": p.status, "status_date": p.status_date.isoformat(),
                       "status_line": _status_line(p, texts), "status_note": p.status_note,
                       "sources": [{"title": s.title, "url": s.url} for s in p.sources], "exceptions": p.exceptions,
                       "theme": p.theme.model_dump(), "texts": p.texts.model_dump(), "measures": measures, "bbox": bbox})
    return {"file": GEOJSON_NAME, "version": sp.meta.version,
            "texts": {k: t[k] for k in ("legend", "overlay", "page_title", "page_intro", "profile_title", "profile_same")},
            "places": places}


def place_parking(sp: SpecialPlaces, tpdf: pd.DataFrame, profiles: dict[str, dict], categories: dict[str, str],
                  p) -> dict[str, dict]:
    """Parking under each place's proposal (prompts/26 Teil 2): place id -> today and target range on the place's
    streets with data on both sides. Target with the proposal's cross section (pipeline/lib/trees_parking.py
    target_parking): the category of the measure (or the segment's), D1 if the proposal's profile drops parking."""
    from pipeline.lib import trees_parking as tp

    t = tpdf.set_index("segment_id")
    out = {}
    for place in sp.places:
        today = lo = hi = 0.0
        n = n_complete = 0
        for g in place.segments:
            change = sp.measures[g.measure].profile
            for sid in g.segment_ids:
                if sid not in t.index or sid not in profiles:
                    continue
                n += 1
                r = t.loc[sid]
                if not bool(r["park_today_complete"]):
                    continue
                n_complete += 1
                prof = profiles[sid]
                cat = (change.cat if change and change.cat else None) or categories.get(sid)
                sides = {"left": float(r["park_today_left"]), "right": float(r["park_today_right"])}
                usable = {"left": float(r["usable_left_m"]), "right": float(r["usable_right_m"])}
                known = {"left": r["park_src_left"] == "osm", "right": r["park_src_right"] == "osm"}
                t_lo, t_hi = tp.target_parking(sides, usable, prof["elements"], float(r["osm_factor"]), p, cat,
                                               "D1" in (prof.get("steps") or []), known)
                today += sides["left"] + sides["right"]
                lo += t_lo if t_lo is not None else 0.0
                hi += t_hi
        out[place.id] = {"segments": n, "segments_complete": n_complete, "today": round(today),
                         "target_min": round(lo), "target_max": round(hi), "lost": round(today - (lo + hi) / 2)}
    return out

