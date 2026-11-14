"""District overview, junction search and network gaps for the website (redesign 2026-11, package 2;
pipeline/lib/export_overview.py)."""

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point, Polygon

from pipeline.lib import export_overview as ov

CRS = 25832
P = {"need_min_disc": 2, "top_n": 2}


def seg_frame():
    rows = [  # segment_id, name, bezirk, length_m, disc_max, disc_speed, priority, crashes, cat, speed
        ("s1", "A-Straße", "Nord", 1000, 3, 2, 2.5, 4, "GOW30", 50),
        ("s2", "A-Straße", "Nord", 500, 2, 1, 1.0, 1, "GOW30", 50),
        ("s3", "B-Weg", "Nord", 200, 1, 0, 0.2, 0, "ETW30", 30),
        ("s4", "C-Allee", "Süd", 800, 0, 0, 0.0, 0, "GOW50", 50),
        ("s5", None, "Nord", 100, 3, 3, 2.9, 0, "ETW30", 50),
    ]
    df = pd.DataFrame(rows, columns=["segment_id", "name", "bezirk", "length_m", "disc_max", "disc_speed", "priority",
                                     "crashes_ped_cyc", "cat_final", "speed_ist_kmh"])
    geom = [LineString([(500000 + i * 100, 5900000), (500050 + i * 100, 5900000)]) for i in range(len(df))]
    return gpd.GeoDataFrame(df, geometry=geom, crs=CRS)


def fac_frame():
    df = pd.DataFrame([("s1", "A-Straße", "Nord", 1000, "HAUPT", "missing", "does_not_fit"),
                       ("s2", "A-Straße", "Nord", 500, "BASIS", "none", "fits"),
                       ("s3", "B-Weg", "Nord", 200, "ERSCHL", "missing", "fits"),
                       ("s4", "C-Allee", "Süd", 800, "HAUPT", "missing", "fits")],
                      columns=["segment_id", "name", "bezirk", "length_m", "cycle_cat_final", "facility_gap", "fit_class"])
    geom = [LineString([(500000 + i * 100, 5900000), (500050 + i * 100, 5900000)]) for i in range(len(df))]
    return gpd.GeoDataFrame(df, geometry=geom, crs=CRS)


def jct_frame():
    df = pd.DataFrame([("1", "A / B", "Nord", True, 2, "signal", "continuous_footway_exit", 7),
                       ("2", "A / C", "Nord", True, 1, "roundabout", "priority_raised", 9),
                       ("3", "C / D", "Süd", False, None, "none_mapped", "equal_right_before_left", 0)],
                      columns=["node_id", "names", "bezirk", "action_needed", "priority_rank", "junction_type_ist",
                               "junction_type_final", "crashes_cyc"])
    return gpd.GeoDataFrame(df, geometry=[Point(500000, 5900000 + i) for i in range(3)], crs=CRS)


def test_district_figures_per_bezirk():
    f = ov.district_figures(seg_frame(), fac_frame(), jct_frame(), P)
    assert set(f) == {"Nord", "Süd"}
    n = f["Nord"]
    assert n["km_total"] == 1.8
    assert n["km_need"] == 1.6           # disc_max >= 2: s1, s2, s5
    assert n["km_speed_down"] == 1.6     # disc_speed >= 1: s1, s2, s5
    assert n["km_cycle_main"] == 1.5     # RSV/HAUPT/BASIS only
    assert n["km_cycle_missing"] == 1.0  # main network with facility_gap missing (s3 is ERSCHL)
    assert n["km_profile_no_fit"] == 1.0
    assert (n["junctions"], n["junctions_rebuild"]) == (2, 2)
    assert f["Süd"]["junctions_rebuild"] == 0


def test_top_streets_grouped_by_name_and_ranked_by_priority():
    top = ov.top_streets(seg_frame(), "Nord", P)
    assert [t["name"] for t in top] == ["A-Straße", "B-Weg"]  # unnamed s5 is not listed, one entry per street
    t = top[0]
    assert t["id"] == "s1" and t["priority"] == 2.5 and t["crashes"] == 5 and t["km_need"] == 1.5
    assert t["speed_ist"] == 50 and t["cat"] == "GOW30"
    assert len(t["at"]) == 2 and 0 < t["at"][0] < 20 and 40 < t["at"][1] < 60  # lon/lat in EPSG:4326


def test_top_junctions_only_rebuild_in_rank_order():
    top = ov.top_junctions(jct_frame(), "Nord", P)
    assert [t["id"] for t in top] == ["2", "1"]
    assert top[0]["ist"] == "roundabout" and top[0]["soll"] == "priority_raised" and top[0]["crashes"] == 9
    assert ov.top_junctions(jct_frame(), "Süd", P) == []


def test_top_gaps_weighted_by_demand():
    demand = pd.Series({"s1": 100.0, "s4": 5000.0})
    top = ov.top_gaps(fac_frame(), demand, "Nord", P)
    assert [t["name"] for t in top] == ["A-Straße"]   # ERSCHL gaps are not part of the main network
    assert top[0]["km"] == 1.0 and top[0]["cycle_cat"] == "HAUPT" and top[0]["demand"] == 100


def test_junction_search_index():
    idx = ov.junction_search(jct_frame())
    assert idx[0] == {"name": "A / B", "bezirk": "Nord", "id": "1", "lon": idx[0]["lon"], "lat": idx[0]["lat"]}
    assert len(idx) == 3


def test_mesh_gaps_for_display():
    g = gpd.GeoDataFrame({"side_m": [1200.0], "max_m": [800.0], "level": ["HAUPT"], "bezirk": ["Nord"]},
                         geometry=[Polygon([(500000, 5900000), (501200, 5900000), (501200, 5901200), (500000, 5901200)])],
                         crs=CRS)
    out = ov.mesh_gaps_frame(g)
    assert out.crs.to_epsg() == 4326
    assert list(out.columns) == ["side_m", "max_m", "level", "bezirk", "geometry"]
