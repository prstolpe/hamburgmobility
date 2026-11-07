"""Line matching, zone shares and speed parsing (pipeline/lib/conflate.py, rules S-CONF-01..03).

Boundary values come from config/rules.yaml, so the tests follow a recalibrated rule file.
"""

import geopandas as gpd
import pytest
from shapely.geometry import LineString

from pipeline.lib.conflate import MatchParams, match_lines, parse_speed_kmh, resolve_speed, zone_share
from pipeline.lib.rules import load_rules

CRS = "EPSG:25832"


@pytest.fixture(scope="module")
def params() -> MatchParams:
    return MatchParams.from_rules(load_rules())


@pytest.fixture(scope="module")
def min_zone_share() -> float:
    return load_rules().conflation.rule("S-CONF-02").thresholds["min_length_share"].value


def _gs(*lines) -> gpd.GeoSeries:
    return gpd.GeoSeries(list(lines), crs=CRS)


SEG = LineString([(0, 0), (100, 0)])


def _quality(seg, off, params) -> str:
    return match_lines(_gs(seg), _gs(*off), params).loc[0, "quality"]


# --- S-CONF-01 line matching -----------------------------------------------------------------


def test_parallel_line_close_is_exact(params):
    assert _quality(SEG, [LineString([(0, 5), (100, 5)])], params) == "exact"


def test_reversed_direction_counts_as_parallel(params):
    assert _quality(SEG, [LineString([(100, 5), (0, 5)])], params) == "exact"


def test_long_official_line_covering_short_segment_is_exact(params):
    # Official sections often span several OSM segments.
    assert _quality(SEG, [LineString([(-500, 3), (600, 3)])], params) == "exact"


def test_perpendicular_line_is_rejected_by_angle(params):
    assert _quality(SEG, [LineString([(50, -50), (50, 50)])], params) == "none"


def test_angle_at_threshold_passes_and_above_fails(params):
    import math

    def rotated(deg: float) -> LineString:
        r = math.radians(deg)
        return LineString([(50 - 50 * math.cos(r), -50 * math.sin(r)), (50 + 50 * math.cos(r), 50 * math.sin(r))])

    ok = match_lines(_gs(SEG), _gs(rotated(params.max_angle_deg - 0.01)), params).loc[0]
    bad = match_lines(_gs(SEG), _gs(rotated(params.max_angle_deg + 1)), params).loc[0]
    assert ok["n_passed"] == 1
    assert bad["n_passed"] == 0


def test_bent_segment_matches_official_line_along_one_leg(params):
    # A segment spanning two streets (L shape) still matches the official line of each leg.
    bent = LineString([(0, 0), (100, 0), (100, 100)])
    off = _gs(LineString([(0, 2), (100, 2)]), LineString([(102, 0), (102, 100)]))
    row = match_lines(_gs(bent), off, params).loc[0]
    assert row["n_passed"] == 2
    assert row["quality"] == "exact"


def test_short_official_piece_on_long_segment_is_partial(params):
    assert _quality(SEG, [LineString([(10, 2), (30, 2)])], params) == "partial"


def test_line_outside_buffer_is_none(params):
    far = params.buffer_m + 5
    assert _quality(SEG, [LineString([(0, far), (100, far)])], params) == "none"


def test_hausdorff_picks_closer_of_two_parallel_candidates(params):
    off = _gs(LineString([(0, 10), (100, 10)]), LineString([(0, 2), (100, 2)]))
    row = match_lines(_gs(SEG), off, params).loc[0]
    assert row["best_off_idx"] == 1
    assert row["n_passed"] == 2
    assert row["hausdorff_m"] == pytest.approx(2.0)


def test_coverage_combines_several_official_pieces(params):
    # Two halves with different attributes (e.g. speed change in the middle) cover the segment together.
    off = _gs(LineString([(0, 1), (50, 1)]), LineString([(50, 1), (100, 1)]))
    row = match_lines(_gs(SEG), off, params).loc[0]
    assert row["quality"] == "exact"
    assert row["coverage"] == pytest.approx(1.0)


def test_no_official_lines_gives_none(params):
    row = match_lines(_gs(SEG), gpd.GeoSeries([], crs=CRS), params).loc[0]
    assert row["quality"] == "none"
    assert row["n_candidates"] == 0


def test_result_keeps_segment_index(params):
    seg = gpd.GeoSeries([SEG, LineString([(0, 500), (100, 500)])], index=[7, 9], crs=CRS)
    out = match_lines(seg, _gs(LineString([(0, 1), (100, 1)])), params)
    assert list(out.index) == [7, 9]
    assert list(out["quality"]) == ["exact", "none"]


# --- S-CONF-02 zone shares -------------------------------------------------------------------


def test_zone_share_at_threshold_applies(params, min_zone_share):
    end = 100 * min_zone_share
    share = zone_share(_gs(SEG), _gs(LineString([(0, 3), (end, 3)])), params).loc[0]
    assert share == pytest.approx(min_zone_share)
    assert share >= min_zone_share


def test_zone_share_below_threshold(params, min_zone_share):
    end = 100 * min_zone_share - 1
    assert zone_share(_gs(SEG), _gs(LineString([(0, 3), (end, 3)])), params).loc[0] < min_zone_share


def test_zone_share_ignores_cross_streets(params):
    cross = _gs(LineString([(0, 0), (0, 80)]), LineString([(100, 0), (100, -80)]))
    assert zone_share(_gs(LineString([(0, 0), (20, 0)])), cross, params).loc[0] == 0.0


def test_zone_share_overlapping_lines_not_double_counted(params):
    lines = _gs(LineString([(0, 2), (100, 2)]), LineString([(0, -2), (100, -2)]))
    assert zone_share(_gs(SEG), lines, params).loc[0] == pytest.approx(1.0)


# --- speeds and time-limited rules (S-CONF-03) -----------------------------------------------


@pytest.mark.parametrize("text, expected", [
    ("10 km/h", 10), ("20 km/h", 20), ("30 km/h", 30), ("40 km/h", 40), ("50 km/h", 50),
    ("60 km/h", 60), ("70 km/h", 70), ("80 km/h", 80), ("100 km/h", 100),
    ("5-7 km/h", None),
    ("Verkehrsbeeinflussungsanlage (variable Geschwindigkeitsbeg.)", None),
    ("Autobahn-Auffahrt ohne explizite Geschwindigkeitsbegrenzung", None),
    ("Nicht mit KFZ befahrbar", None), (None, None), ("", None),
])
def test_parse_speed(text, expected):
    assert parse_speed_kmh(text) == expected


def test_parse_speed_text_values_from_rules():
    # rules.yaml 0.16.0 (open question 23): '5-7 km/h' (verkehrsberuhigt) = calculation value of ETW_ERF
    from pipeline.lib.rules import load_rules
    rules = load_rules()
    tv = rules.conflation.rule("S-CONF-03").text_values
    assert tv["5-7 km/h"] == rules.categories["ETW_ERF"].speed_kmh
    assert parse_speed_kmh("5-7 km/h", tv) == rules.categories["ETW_ERF"].speed_kmh
    assert parse_speed_kmh("Verkehrsbeeinflussungsanlage (variable Geschwindigkeitsbeg.)", tv) is None
    assert resolve_speed("5-7 km/h", "keine Sonderregelung", tv).regular_kmh == rules.categories["ETW_ERF"].speed_kmh


def test_no_rule_keeps_signed_speed():
    r = resolve_speed("50 km/h", "keine Sonderregelung")
    assert (r.regular_kmh, r.conditional_kmh, r.rule_text, r.ambiguous) == (50, None, None, False)


@pytest.mark.parametrize("rule", ["Mo-Fr 6-19 h, sonst 50km/h", "Werktags 6-22 h, sonst 50km/h",
                                  "Werktags 6-19 h, sonst 50km/h", "6 - 19 h, sonst 50km/h"])
def test_daytime_30_is_conditional_not_regular(rule):
    r = resolve_speed("30 km/h", rule)
    assert r.regular_kmh == 50
    assert r.conditional_kmh == 30
    assert r.rule_text == rule
    assert not r.ambiguous


def test_sonst_rule_with_same_signed_speed_has_unknown_conditional_speed():
    r = resolve_speed("50 km/h", "Werktags 6-19 h, sonst 50km/h")
    assert r.regular_kmh == 50
    assert r.conditional_kmh is None
    assert r.ambiguous


def test_night_30_with_signed_50_keeps_regular_50():
    r = resolve_speed("50 km/h", "30 km/h 22 - 6 h Lärmschutz")
    assert (r.regular_kmh, r.conditional_kmh, r.ambiguous) == (50, 30, False)


def test_night_30_with_signed_30_has_unknown_regular_speed():
    # The time-limited 30 must never become the regular speed.
    r = resolve_speed("30 km/h", "30 km/h 22 - 6 h Lärmschutz")
    assert r.regular_kmh is None
    assert r.conditional_kmh == 30
    assert r.ambiguous


def test_unknown_rule_text_gives_unknown_regular_speed():
    r = resolve_speed("30 km/h", "Schulzeit irgendwas")
    assert r.regular_kmh is None
    assert r.ambiguous


# --- in_hvs along the street name (S-CONF-04, rules.yaml 0.16.0, open questions 21 and 78) ----------------


def test_hvs_from_neighbours_fills_partial_gaps_with_same_name():
    import pandas as pd
    from pipeline.lib.conflate import hvs_from_neighbours
    df = pd.DataFrame([
        # Kieler Straße: exact - partial - partial - exact; Nebenstraße partial with another name
        {"name": "Kieler Straße", "node_u": 1, "node_v": 2, "highway": "primary", "hvs_match_quality": "exact", "in_hvs": True},
        {"name": "Kieler Straße", "node_u": 2, "node_v": 3, "highway": "primary", "hvs_match_quality": "partial", "in_hvs": False},
        {"name": "Kieler Straße", "node_u": 3, "node_v": 4, "highway": "primary", "hvs_match_quality": "partial", "in_hvs": False},
        {"name": "Nebenweg", "node_u": 3, "node_v": 9, "highway": "residential", "hvs_match_quality": "partial", "in_hvs": False},
        # partial without an exact neighbour of the same name stays out
        {"name": "Insel", "node_u": 20, "node_v": 21, "highway": "secondary", "hvs_match_quality": "partial", "in_hvs": False},
        # parallel service road with the main road's name never joins the HVS (S-NET-04 highways)
        {"name": "Kieler Straße", "node_u": 4, "node_v": 5, "highway": "service", "hvs_match_quality": "partial", "in_hvs": False},
    ])
    in_hvs, source = hvs_from_neighbours(df, exclude_highways={"service", "track"})
    assert list(in_hvs) == [True, True, True, False, False, False]
    assert list(source) == ["exact", "neighbour", "neighbour", None, None, None]


def test_hvs_exact_match_on_service_road_is_dropped():
    import pandas as pd
    from pipeline.lib.conflate import hvs_from_neighbours
    df = pd.DataFrame([{"name": "Grindelallee", "node_u": 1, "node_v": 2, "highway": "service",
                        "hvs_match_quality": "exact", "in_hvs": True}])
    in_hvs, source = hvs_from_neighbours(df, exclude_highways={"service", "track"})
    assert list(in_hvs) == [False] and list(source) == [None]
