"""Export of the cycling layers and profiles (pipeline/lib/export_cycling.py, prompts/21_web_validation_cycling.md)."""

import json
import math

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import LineString, Point

from pipeline.lib import export as ex
from pipeline.lib import export_cycling as xc
from pipeline.lib import profile as pf
from pipeline.lib.rules import load_cycling_rules, load_design_rules

CYC = load_cycling_rules()
DES = load_design_rules()
TEXTS = ex.load_texts()
LABELS = xc.Labels.from_rules(TEXTS, CYC, DES)
CRS = "EPSG:25832"
LINE = LineString([(565000, 5935000), (565100, 5935000)])


def _gdf(rows: list[dict], geom=LINE) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(rows, geometry=[geom] * len(rows), crs=CRS)


# --- tiles ---------------------------------------------------------------------------------------


def test_network_tile_frame_keeps_network_edges_and_links_segments():
    net = _gdf([
        {"edge_id": "ce_1", "segment_id": "seg_a", "sidepath_of": None, "cycle_cat_final": "HAUPT", "official_network": "official", "bezirk": "Altona", "rule_trace_cycle": "[]"},
        {"edge_id": "ce_2", "segment_id": None, "sidepath_of": "seg_b", "cycle_cat_final": "BASIS", "official_network": None, "bezirk": "Altona", "rule_trace_cycle": "[]"},
        {"edge_id": "ce_3", "segment_id": None, "sidepath_of": None, "cycle_cat_final": "none", "official_network": None, "bezirk": "Altona", "rule_trace_cycle": "[]"},
        {"edge_id": "ce_4", "segment_id": None, "sidepath_of": None, "cycle_cat_final": None, "official_network": None, "bezirk": None, "rule_trace_cycle": "[]"},
    ])
    out = xc.network_tile_frame(net)
    assert list(out["id"]) == ["ce_1", "ce_2"]
    assert list(out["seg"]) == ["seg_a", "seg_b"]
    assert list(out["cc"]) == ["HAUPT", "BASIS"]
    assert out["off"].tolist()[0] == "official" and out["off"].isna().tolist()[1]
    assert out.crs.to_epsg() == 4326
    assert set(out.columns) == {"id", "seg", "cc", "off", "bz", "geometry"}


@pytest.mark.parametrize("soll, ist, expected", [
    ("shared", 2.0, "shared"),
    ("1", 2.0, "fewer"),
    ("1", 1.0, "same"),
    ("2", 1.0, "more"),
    ("1", None, "ist_unknown"),
    ("1", float("nan"), "ist_unknown"),
    (None, 2.0, None),
])
def test_lanes_change(soll, ist, expected):
    assert xc.lanes_change(soll, ist) == expected


def _fac_row(**kw) -> dict:
    row = {"segment_id": "seg_a", "name": "Teststraße", "bezirk": "Altona", "length_m": 100.0, "cat_final": "GOW50",
           "cycle_cat_final": "HAUPT", "cycle_facility_soll": "separated_oneway_both", "cycle_facility_fallback": None,
           "cycle_width_soll_m": 2.5, "cycle_width_de_m": 2.0, "cycle_width_nl_m": 3.0, "cycle_osm_ist": "lane",
           "cycle_facility_ist": "cycle_lane", "cycle_width_ist_m": float("nan"), "facility_gap": "wrong_type",
           "facility_flags": "ist_width_unknown", "facility_confidence": "medium", "rule_trace_facility": "[]"}
    row.update(kw)
    return row


def _xs_row(**kw) -> dict:
    elements = [{"order": 1, "element": "sidewalk", "width_m": 3.0, "side": "left"},
                {"order": 2, "element": "cycle_track", "width_m": 2.5, "side": "left"},
                {"order": 3, "element": "carriageway", "width_m": 6.5, "side": "centre"},
                {"order": 4, "element": "cycle_track", "width_m": 2.5, "side": "right"},
                {"order": 5, "element": "sidewalk", "width_m": 3.0, "side": "right"}]
    row = {"segment_id": "seg_a", "lanes_per_dir_soll": "1", "lanes_per_dir_ist": 2.0, "bus_lane_soll": False,
           "median_soll": False, "cycle_facility_final": "separated_oneway_both", "cycle_width_final_m": 2.5,
           "cycle_side": "both", "profile_elements": json.dumps(elements), "total_required_m": 17.5, "available_m": 16.0,
           "fit_class": "fits_after_degrade", "degrade_steps_applied": "D1|D4", "cat_change_proposal": None,
           "profile_flags": "D6", "profile_confidence": "medium", "rule_trace_profile": "[]"}
    row.update(kw)
    return row


def test_segment_tile_frame_short_attributes():
    fac = _gdf([_fac_row()])
    xs = pd.DataFrame([_xs_row()])
    out = xc.segment_tile_frame(fac, xs)
    r = out.iloc[0]
    assert r["id"] == "seg_a" and r["cc"] == "HAUPT"
    assert r["fs"] == "separated_oneway_both"  # Soll after prompt 19 (final)
    assert r["fi"] == "cycle_lane" and r["gap"] == "wrong_type"
    assert r["ws"] == 2.5 and (r["wi"] is None or math.isnan(r["wi"]))
    assert r["ls"] == "1" and r["li"] == 2 and r["ld"] == "fewer"
    assert r["fit"] == "fits_after_degrade"
    assert out.crs.to_epsg() == 4326
    assert not {c for c in out.columns if "trace" in c}


def test_segment_tile_frame_without_network_category():
    fac = _gdf([_fac_row(cycle_cat_final="none", cycle_facility_soll=None, facility_gap="not_assessed")])
    xs = pd.DataFrame([_xs_row(cycle_facility_final=None, lanes_per_dir_soll=None, fit_class=None)])
    r = xc.segment_tile_frame(fac, xs).iloc[0]
    assert r["cc"] == "none" and r["fs"] is None and r["ld"] is None and r["fit"] is None


@pytest.mark.parametrize("jtype, group", [
    ("roundabout_single_lane_cycle_priority", "roundabout"), ("turbo_roundabout", "roundabout"),
    ("signal_protected", "signal"), ("cycle_crossing_signal", "signal"),
    ("priority_raised", "priority"), ("priority_flat_coloured", "priority"), ("cycle_crossing_priority", "priority"),
    ("continuous_footway_exit", "continuous"), ("equal_right_before_left", "equal"),
    ("grade_separated_cycle", "grade_separated"), (None, "none"),
])
def test_junction_group(jtype, group):
    assert xc.junction_group(jtype) == group


def test_every_junction_type_has_a_group_and_text():
    for t in DES.junctions.types:
        assert xc.junction_group(t) != "none"
        assert t in TEXTS["cycling"]["junction_type"]
    assert set(xc.JUNCTION_GROUPS) <= set(TEXTS["cycling"]["junction_group"])


def _junction(**kw) -> dict:
    legs = [{"ids": ["seg_a"], "cat": "GOW50", "cycle_cat": "HAUPT", "facility": "separated_oneway_both", "dtv": 30000.0, "name": "Hauptstraße", "bearing": 90},
            {"ids": ["seg_b"], "cat": "GOW50", "cycle_cat": "HAUPT", "facility": "separated_oneway_both", "dtv": 30000.0, "name": "Hauptstraße", "bearing": 270},
            {"ids": ["seg_c"], "cat": "ETW30", "cycle_cat": "ERSCHL", "facility": "mixed", "dtv": None, "name": "Nebenweg", "bearing": 0}]
    row = {"node_id": "123", "names": "Hauptstraße / Nebenweg", "bezirk": "Altona", "pair": "GOW50+ETW30", "legs": json.dumps(legs),
           "legs_count": 3, "entering_dtv_sum": 30000.0, "space_radius_m": 12.0, "tram_present": False, "signal_present_ist": False,
           "decision_rule": "J-04", "junction_type_soll": "continuous_footway_exit", "junction_type_final": "continuous_footway_exit",
           "junction_type_source": "proposed", "junction_type_ist": "none_mapped", "ist_result": "not_checkable",
           "action_needed": False, "cyclist_treatment": "JC-04", "treatment_text": "Mittelinsel für die Querung.",
           "conflict_flags": "dtv_partial", "confidence": "medium", "top_cycle_cat": "HAUPT", "crashes_cyc": 2,
           "crashes_cyc_severe": 1, "rule_trace_junction": "[]", "junction_override_reason": None,
           "junction_override_author": None, "junction_override_date": None, "junction_override_source": None,
           "priority_rank": np.nan}
    row.update(kw)
    return row


def test_junction_tile_frame_points():
    j = gpd.GeoDataFrame([_junction(), _junction(node_id="124", junction_type_final=None, junction_type_soll=None,
                                                 ist_result=None, action_needed=False, decision_rule=None)],
                         geometry=[Point(565000, 5935000)] * 2, crs=CRS)
    out = xc.junction_tile_frame(j)
    assert list(out["id"]) == ["123", "124"]
    assert list(out["grp"]) == ["continuous", "none"]
    assert out["act"].tolist() == [0, 0]
    assert out.iloc[0]["js"] == "continuous_footway_exit" and out.iloc[0]["ji"] == "none_mapped"
    assert out.crs.to_epsg() == 4326 and (out.geom_type == "Point").all()
    assert not {c for c in out.columns if "trace" in c or "crash" in c}


def test_official_tile_frame_groups_status():
    off = _gdf([{"status": "Bestand", "laenge": 1}, {"status": "In Arbeit", "laenge": 1},
                {"status": "Priorisierte Netzergänzungen/Netzverbesserungen", "laenge": 1}])
    out = xc.official_tile_frame(off)
    assert list(out["grp"]) == ["Bestand", "In Arbeit", "planned"]
    assert out.crs.to_epsg() == 4326


# --- profiles ------------------------------------------------------------------------------------


def test_segment_cycling_block():
    b = xc.segment_cycling_block(pd.Series(_fac_row()), pd.Series(_xs_row()), None, LABELS)
    assert b["cycle_cat"] == {"code": "HAUPT", "label": CYC.cycle_categories["HAUPT"]["label_de"]}
    assert b["facility"]["soll"] == "separated_oneway_both"
    assert b["facility"]["soll_text"] == TEXTS["cycling"]["facility"]["separated_oneway_both"]
    assert b["facility"]["ist_text"] == TEXTS["cycling"]["facility"]["cycle_lane"]
    assert b["facility"]["gap_text"] == TEXTS["cycling"]["gap"]["wrong_type"]
    assert b["facility"]["fallback_used"] is False
    assert b["width"] == {"soll_m": 2.5, "ist_m": None, "de_m": 2.0, "nl_m": 3.0}
    assert b["lanes"]["soll"] == "1" and b["lanes"]["ist"] == 2 and b["lanes"]["change"] == "fewer"
    assert b["side_text"] == TEXTS["cycling"]["side"]["both"]
    assert [s["step"] for s in b["profile"]["steps"]] == ["D1", "D4"]
    assert b["profile"]["steps"][0]["text"].startswith("Parken entfernen")
    assert b["profile"]["fit_text"] == TEXTS["cycling"]["fit"]["fits_after_degrade"]
    assert [e["element"] for e in b["profile"]["elements"]][:2] == ["sidewalk", "cycle_track"]
    assert TEXTS["cycling"]["profile_flags"]["D6"] in b["flags"]
    assert TEXTS["cycling"]["facility_flags"]["ist_width_unknown"] in b["flags"]
    assert b["principles"] is None
    json.dumps(b)  # JSON-serialisable (no NaN objects)


def test_segment_block_hides_de_nl_width_after_fallback():
    fac = pd.Series(_fac_row(cycle_facility_soll="separated_oneway_both", cycle_facility_fallback="cycle_lane"))
    xs = pd.Series(_xs_row(cycle_facility_final="cycle_lane", cycle_width_final_m=2.25, degrade_steps_applied="fallback"))
    b = xc.segment_cycling_block(fac, xs, None, LABELS)
    assert b["facility"]["soll"] == "cycle_lane" and b["facility"]["fallback_used"] is True
    assert b["width"]["soll_m"] == 2.25 and b["width"]["de_m"] is None and b["width"]["nl_m"] is None
    assert b["profile"]["steps"][0]["text"] == TEXTS["cycling"]["degrade_fallback"]


def test_principle_scores_pick_highest_category_edge():
    net = pd.DataFrame({"edge_id": ["ce_1", "ce_2", "ce_3"], "segment_id": ["seg_a", None, "seg_b"],
                        "sidepath_of": [None, "seg_a", None]})
    cols = {f"{p}_{v}": 0.5 for p in xc.PRINCIPLES for v in ("ist", "soll")}
    pr = pd.DataFrame([
        {"level": "edge", "id": "ce_1", "category": "BASIS", "length_m": 50, **cols, "score_ist": 0.4, "score_soll": 0.6},
        {"level": "edge", "id": "ce_2", "category": "HAUPT", "length_m": 40, **cols, "score_ist": 0.3, "score_soll": 0.9},
        {"level": "edge", "id": "ce_3", "category": "ERSCHL", "length_m": 40, **cols, "score_ist": 0.7, "score_soll": 0.8},
        {"level": "route", "id": "rt_1", "category": "HAUPT", "length_m": 900, **cols, "score_ist": 0.1, "score_soll": 0.2},
    ])
    s = xc.principle_scores(pr, net)
    assert s["seg_a"]["category"] == "HAUPT" and s["seg_a"]["ist"]["score"] == 0.3 and s["seg_a"]["soll"]["score"] == 0.9
    assert s["seg_b"]["ist"]["score"] == 0.7
    assert set(s["seg_a"]["ist"]) == {*xc.PRINCIPLES, "score"}


def test_junction_profile():
    p = xc.junction_profile(pd.Series(_junction()), LABELS, "1.0+2026-11-01")
    assert p["id"] == "123" and p["names"] == "Hauptstraße / Nebenweg"
    assert p["soll"]["code"] == "continuous_footway_exit"
    assert p["soll"]["text"] == TEXTS["cycling"]["junction_type"]["continuous_footway_exit"]
    assert p["ist"]["text"] == TEXTS["cycling"]["junction_ist"]["none_mapped"]
    assert p["result"]["text"] == TEXTS["cycling"]["junction_result"]["not_checkable"]
    assert p["rule"]["id"] == "J-04" and "GOW50+ETW30" in p["rule"]["text"]
    assert p["treatment"] == "Mittelinsel für die Querung."
    assert p["conflicts"] == [TEXTS["cycling"]["junction_flags"]["dtv_partial"]]
    assert [leg["name"] for leg in p["legs"]] == ["Hauptstraße", "Hauptstraße", "Nebenweg"]
    assert p["legs"][0]["facility_text"] == TEXTS["cycling"]["facility"]["separated_oneway_both"]
    assert p["crashes"] == {"cyc": 2, "cyc_severe": 1}
    assert p["override"] is None
    assert "rule_trace_junction" not in json.dumps(p)
    json.dumps(p)


def test_junction_profile_with_override():
    p = xc.junction_profile(pd.Series(_junction(junction_type_source="override", junction_type_final="signal_protected",
                                                junction_override_reason="Straßenbahn geplant", junction_override_author="Team",
                                                junction_override_date="2026-11-07")), LABELS, "v")
    assert p["soll"]["code"] == "signal_protected" and p["proposed"]["code"] == "continuous_footway_exit"
    assert p["override"]["reason"] == "Straßenbahn geplant"


def test_cycling_meta_has_labels_for_every_element_and_category():
    m = xc.cycling_meta(LABELS)
    assert set(pf.LABEL_DE) <= set(m["elements"])
    assert all(set(v) == {"label", "color"} for v in m["elements"].values())
    assert set(m["cycle_categories"]) == {"RSV", "HAUPT", "BASIS", "ERSCHL"}
    assert m["disclaimer"] == TEXTS["cycling"]["disclaimer"]
    for key in ("facility", "gap", "fit", "lanes", "junction_type", "junction_group", "official_status"):
        assert m[key] == TEXTS["cycling"][key]
