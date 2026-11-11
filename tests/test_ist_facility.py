"""Ist cycle facility once per segment (rules.yaml S-FEAT-13, F26/E9) and parallel route of the Soll cycle network
(S-FEAT-11, F21) in pipeline/lib/ist_facility.py."""

import json

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import LineString

from pipeline.lib import facility as fa
from pipeline.lib import ist_facility as ist
from pipeline.lib.rules import load_cycling_rules, load_rules

RULES, CYC = load_rules(), load_cycling_rules()
P = fa.FacilityParams.from_rules(CYC, RULES)
TRACKS = frozenset(RULES.features.rule("S-FEAT-13").track_facilities)
PP = ist.ParallelParams.from_rules(RULES, CYC)
CRS = "EPSG:25832"


def s13(**kw):
    return ist.ist_for_segment(P, TRACKS, **kw)


# --- S-FEAT-13 ----------------------------------------------------------------------------------------------


def test_rule_values_from_rules_yaml():
    assert TRACKS == {"separated_oneway_both", "separated_twoway"}
    assert PP.categories == {"GOW50"}  # requirements.GOW50.cycling = separated_track_or_parallel_route
    assert [lv[2] for lv in PP.levels] == ["RSV", "HAUPT", "BASIS"]
    detour = {c["id"]: c for p in CYC.principles.values() for c in p["checks"]}["P-DIR-01"]["thresholds"]
    assert [lv[1] for lv in PP.levels] == [detour["RSV"], detour["HAUPT"], detour["BASIS"]]


def test_tag_only_track_counts_as_track_and_is_listed():
    # the "83 km": street tag says track, cycle graph has neither sidepath nor carriageway track
    r = s13(cycle_track_tag=True, cycleway_values={"separate"}, graph_track=False)
    assert r["cycle_osm_ist"] == "track" and r["cycle_facility_ist"] == "separated_oneway_both"
    assert r["separated_cycle_track_present"] is True and r[ist.TRACK_TAG_ONLY_FLAG] is True
    assert r["trace"]["id"] == "S-FEAT-13"


def test_sidepath_track_is_not_tag_only():
    r = s13(has_sidepath=True, graph_track=True, cycle_track_tag=None)
    assert r["separated_cycle_track_present"] is True and r[ist.TRACK_TAG_ONLY_FLAG] is False


def test_twoway_sidepaths_on_both_sides_are_oneway_both_e9():
    # E9 / C-FAC-05: sidepaths per side; C-PRI-02 counted these as two-way track until cycling_rules 0.10.0
    both = s13(has_sidepath=True, sidepath_twoway=True, sidepath_both_sides=True, graph_track=True)
    one = s13(has_sidepath=True, sidepath_twoway=True, sidepath_both_sides=False, graph_track=True)
    assert both["cycle_facility_ist"] == "separated_oneway_both"
    assert one["cycle_facility_ist"] == "separated_twoway"
    assert one["separated_cycle_track_present"] is True


def test_missing_tags_stay_unknown():
    r = s13()
    assert r["cycle_osm_ist"] == "no" and r["cycle_facility_ist"] == "mixed"
    assert r["separated_cycle_track_present"] is None  # S-FEAT-10: no data is unknown, not "no"


@pytest.mark.parametrize("kw", [{"cycle_track_tag": False}, {"cycleway_values": {"no"}}, {"cycle_lane_present": True},
                                {"cycleway_values": {"lane"}}])
def test_known_no_track(kw):
    assert s13(**kw)["separated_cycle_track_present"] is False


def test_cycle_street_before_track_tag():
    r = s13(fahrradstrasse=True, cycle_track_tag=True)
    assert r["cycle_facility_ist"] == "cycle_street" and r["separated_cycle_track_present"] is False


def _gs(*lines):
    return gpd.GeoSeries(list(lines), crs=CRS)


def test_segment_graph_inputs():
    seg = gpd.GeoSeries([LineString([(0, 0), (100, 0)]), LineString([(0, 500), (100, 500)])], index=["a", "b"], crs=CRS)
    net = gpd.GeoDataFrame({
        "kind": ["road", "path", "path", "road"],
        "segment_id": ["a", None, None, "b"],
        "sidepath_of": [None, "a", "a", None],
        "impedance_trace": [json.dumps({"inputs": {"cycleway": ["separate"]}}), None, None,
                            json.dumps({"inputs": {"cycleway": ["track"], "bicycle_road": "no"}})],
        "cost_fwd": [1.0, 1.0, 1.0, 1.0], "cost_bwd": [1.0, np.nan, 1.0, 1.0],
    }, geometry=[LineString([(0, 0), (100, 0)]), LineString([(0, 5), (100, 5)]), LineString([(0, -5), (100, -5)]),
                 LineString([(0, 500), (100, 500)])], crs=CRS)
    g = ist.segment_graph_inputs(seg, net)
    assert g.loc["a", "has_sidepath"] and g.loc["a", "sidepath_both_sides"] and g.loc["a", "sidepath_twoway"]
    assert g.loc["a", "cycleway_values"] == {"separate"} and g.loc["a", "graph_track"]
    assert not g.loc["b", "has_sidepath"] and g.loc["b", "graph_track"]  # carriageway track (C-IMP-03 condition)


# --- S-FEAT-11 ----------------------------------------------------------------------------------------------


def _net(rows):
    """rows: (geometry, node_u, node_v, cycle_cat_final, kind, segment_id, sidepath_of)."""
    geoms, u, v, cat, kind, seg, side = zip(*rows)
    return gpd.GeoDataFrame({"node_u": u, "node_v": v, "cycle_cat_final": cat, "kind": kind, "segment_id": seg,
                             "sidepath_of": side, "length_m": [g.length for g in geoms]}, geometry=list(geoms), crs=CRS)


SEG = gpd.GeoDataFrame(geometry=[LineString([(0, 0), (300, 0)])], index=["main"], crs=CRS)
NAMES = pd.Series({"main": "Hauptstraße", "other": "Nebenstraße", "main2": "Hauptstraße"})


def test_parallel_route_on_soll_network_counts():
    net = _net([(LineString([(-50, 150), (350, 150)]), 1, 2, "HAUPT", "road", "other", None)])
    r = ist.parallel_routes(SEG, net, NAMES, PP).loc["main"]
    assert r["parallel_cycle_route_present"] and r["parallel_level"] == "HAUPT"
    assert r["parallel_detour"] == pytest.approx(1.0)


def test_parallel_route_needs_qualifying_category():
    # F21: ERSCHL (e.g. a park path) is no substitute; S-FEAT-11 qualifying_cycle_categories = RSV, HAUPT, BASIS
    net = _net([(LineString([(-50, 150), (350, 150)]), 1, 2, "ERSCHL", "path", None, None)])
    assert not ist.parallel_routes(SEG, net, NAMES, PP).loc["main", "parallel_cycle_route_present"]


def test_same_street_never_counts():
    # the street's own Soll edge (or a sidepath / service carriageway of the same name) is no parallel route
    net = _net([(LineString([(-50, 150), (350, 150)]), 1, 2, "HAUPT", "road", "main2", None),
                (LineString([(-50, 20), (350, 20)]), 3, 4, "RSV", "path", None, "main")])
    assert not ist.parallel_routes(SEG, net, NAMES, PP).loc["main", "parallel_cycle_route_present"]


def test_parallel_route_with_detour_over_p_dir_01_fails():
    pieces = [(LineString([(-50, 150), (150, 150)]), 1, 2, "HAUPT", "path", None, None),
              (LineString([(150, 180), (350, 180)]), 3, 4, "HAUPT", "path", None, None)]
    loop = [(LineString([(150, 150), (150, 500)]), 2, 5, "HAUPT", "path", None, None),
            (LineString([(150, 500), (150, 180)]), 5, 3, "HAUPT", "path", None, None)]
    r = ist.parallel_routes(SEG, _net(pieces + loop), NAMES, PP).loc["main"]
    assert r["parallel_share"] == pytest.approx(1.0) and not r["parallel_cycle_route_present"]  # ~970 m / 300 m
    direct = [(LineString([(150, 150), (150, 180)]), 2, 3, "HAUPT", "path", None, None)]
    r = ist.parallel_routes(SEG, _net(pieces + direct), NAMES, PP).loc["main"]
    assert r["parallel_cycle_route_present"] and r["parallel_detour"] == pytest.approx(330 / 300)
    # 1.1 is within HAUPT (1.2) but the network has no RSV level
    assert r["parallel_level"] == "HAUPT"


def test_disconnected_parallel_pieces_fail():
    pieces = [(LineString([(-50, 150), (150, 150)]), 1, 2, "BASIS", "path", None, None),
              (LineString([(150, 180), (350, 180)]), 3, 4, "BASIS", "path", None, None)]
    assert not ist.parallel_routes(SEG, _net(pieces), NAMES, PP).loc["main", "parallel_cycle_route_present"]


def test_crossing_route_is_not_parallel():
    net = _net([(LineString([(150, -300), (150, 300)]), 1, 2, "RSV", "path", None, None)])
    r = ist.parallel_routes(SEG, net, NAMES, PP).loc["main"]
    assert not r["parallel_cycle_route_present"] and r["parallel_share"] == 0.0
