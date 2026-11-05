"""Report helpers of the validation (pipeline/lib/validation.py, guide Teil 7, prompts/12_validation.md)."""

import pandas as pd
import pytest

from pipeline.lib import validation as v
from pipeline.lib.rules import load_rules

RULES = load_rules()


def seg(**kw) -> dict:
    base = {"segment_id": "s", "name": "A-Straße", "bezirk": "Eimsbüttel", "highway": "residential", "length_m": 100.0,
            "cat_final": "ETW30", "in_hvs": False, "speed_ist_kmh": 30, "speed_ist_source": "official",
            "speed_sources_conflict": False, "in_zone_t30": True, "hvs_match_quality": "none", "match_quality": "exact",
            "rule_path": "C-ETW-01", "dtv_official": None}
    return {**base, **kw}


# --- HVS -------------------------------------------------------------------------------------


def test_crosstab_km():
    df = pd.DataFrame([seg(cat_final="GOW50", in_hvs=True, length_m=1500), seg(cat_final="GOW30", in_hvs=True),
                       seg(length_m=2000), seg(in_hvs=None, length_m=500)])
    t = v.crosstab_km(df, ["GOW50", "GOW30", "ETW30"])
    assert t.loc["GOW50", "HVS"] == pytest.approx(1.5)
    assert t.loc["GOW30", "HVS"] == pytest.approx(0.1)
    assert t.loc["ETW30", "keine HVS"] == pytest.approx(2.0)
    assert t.loc["ETW30", "unbekannt"] == pytest.approx(0.5)
    assert list(t.columns) == ["HVS", "keine HVS", "unbekannt"]


def test_hvs_deviations():
    df = pd.DataFrame([
        seg(segment_id="a", cat_final="GOW50", in_hvs=True),
        seg(segment_id="b", cat_final="ETW30", in_hvs=True, name="Hallerstraße"),
        seg(segment_id="c", cat_final="ETW30", in_hvs=True, name="Hallerstraße", length_m=50),
        seg(segment_id="d", cat_final="GOW50", in_hvs=False, highway="secondary", name="Weg"),
        seg(segment_id="e", cat_final="GOW50", in_hvs=False, highway="motorway", name=None),
    ])
    hvs_other, district_gow50 = v.hvs_deviations(df)
    assert hvs_other["segment_id"].tolist() == ["b", "c"]
    assert district_gow50["segment_id"].tolist() == ["d"]
    groups = v.street_groups(hvs_other)
    assert len(groups) == 1
    g = groups.iloc[0]
    assert (g["name"], g["n"], g["km"], g["cats"]) == ("Hallerstraße", 2, pytest.approx(0.15), "ETW30")


# --- Ist-Tempo -------------------------------------------------------------------------------


def test_speed_bucket():
    assert [v.speed_bucket(x) for x in (7, 20, 30, 40, 50, 60, None)] == [
        "≤ 20", "≤ 20", "30", "40–50", "40–50", "> 50", "unbekannt"]


def test_etw30_tempo_and_outlier_hints():
    df = pd.DataFrame([
        seg(segment_id="ok", speed_ist_kmh=30),
        seg(segment_id="z", speed_ist_kmh=50, in_zone_t30=True),
        seg(segment_id="c", speed_ist_kmh=50, in_zone_t30=False, speed_sources_conflict=True, length_m=300),
        seg(segment_id="o", speed_ist_kmh=50, in_zone_t30=False, speed_ist_source="osm"),
        seg(segment_id="h", speed_ist_kmh=50, in_zone_t30=False, hvs_match_quality="partial"),
        seg(segment_id="n", speed_ist_kmh=50, in_zone_t30=False),
        seg(segment_id="u", speed_ist_kmh=None),
        seg(segment_id="g", cat_final="GOW30", speed_ist_kmh=50),
    ])
    res = v.etw30_tempo(df, RULES)
    assert res["soll_kmh"] == 30
    assert res["km_total"] == pytest.approx(0.9)
    assert res["km_at_or_below"] == pytest.approx(0.1)
    assert res["km_unknown"] == pytest.approx(0.1)
    out = res["outliers"].set_index("segment_id")
    assert list(out.index) == ["c", "h", "n", "o", "z"]  # longest first, then id
    assert "Tempo-30-Zone laut Zonenebene" in out.loc["z", "hints"]
    assert "amtlich und OSM verschieden" in out.loc["c", "hints"]
    assert "nur OSM-Tempo" in out.loc["o", "hints"]
    assert "HVS-Abgleich nur teilweise" in out.loc["h", "hints"]
    assert out.loc["n", "data_error_candidate"] == False  # noqa: E712 – residential with 50, nothing contradicts it
    assert out.loc["z", "data_error_candidate"] == True  # noqa: E712


# --- data quality ----------------------------------------------------------------------------


def test_data_quality_per_district():
    df = pd.DataFrame([
        seg(bezirk="A", match_quality="exact", separated_cycle_track_present=True, cycle_lane_present=None,
            centre_line=None, parking_along_carriageway=False, lanes=2, surface="asphalt", maxspeed_osm="50",
            in_hvs=True, dtv_official=12000),
        seg(bezirk="A", match_quality="none", separated_cycle_track_present=None, cycle_lane_present=None,
            centre_line=None, parking_along_carriageway=None, lanes=None, surface=None, maxspeed_osm=None,
            in_hvs=True, dtv_official=None, speed_ist_kmh=None, length_m=300),
        seg(bezirk=None, match_quality="partial", separated_cycle_track_present=False, cycle_lane_present=False,
            centre_line=False, parking_along_carriageway=True, lanes=1, surface="asphalt", maxspeed_osm="30"),
    ])
    q = v.data_quality(df).set_index("bezirk")
    assert list(q.index) == ["A", "ohne Bezirk", "gesamt"]
    a = q.loc["A"]
    assert a["n"] == 2 and a["km"] == pytest.approx(0.4)
    assert a["conflation_hit_km"] == pytest.approx(0.25)  # 100 of 400 m matched
    assert a["tag_separated_cycle_track_present"] == pytest.approx(0.5)
    assert a["tag_centre_line"] == 0.0
    assert a["osm_tags_mean"] == pytest.approx((0.5 + 0 + 0 + 0.5 + 0.5 + 0.5 + 0.5) / 7)
    assert a["missing_speed"] == pytest.approx(0.5)
    assert a["hvs_n"] == 2 and a["hvs_missing_dtv"] == pytest.approx(0.5)
    assert a["missing_dtv"] == pytest.approx(0.5)
    assert a["main_n"] == 0 and pd.isna(a["main_missing_dtv"])  # residential only
    assert q.loc["gesamt", "n"] == 3
    assert q.loc["ohne Bezirk", "hvs_n"] == 0 and pd.isna(q.loc["ohne Bezirk", "hvs_missing_dtv"])


# --- manual samples --------------------------------------------------------------------------


@pytest.mark.parametrize("raw, expected", [
    ("ja", True), ("Nein", False), ("1", True), (0, False), (True, True), ("x", True), (None, None), ("", None),
    (float("nan"), None), ("vielleicht", None),
])
def test_parse_ok(raw, expected):
    assert v.parse_ok(raw) is expected


def test_sample_summary():
    df = pd.DataFrame({"cat_proposed": ["GOW30", "GOW30", "GOW30", "ETW30", "ETW30"],
                       "check_ok": ["ja", "nein", None, None, None],
                       "cat_expected_manual": [None, None, None, "GOW30", None]})
    s = v.sample_summary(df, "cat_proposed", expected_col="cat_expected_manual").set_index("group")
    assert (s.loc["GOW30", "n"], s.loc["GOW30", "reviewed"], s.loc["GOW30", "disputed"]) == (3, 2, 1)
    assert s.loc["GOW30", "disputed_share"] == pytest.approx(0.5)
    assert (s.loc["ETW30", "reviewed"], s.loc["ETW30", "disputed"]) == (1, 1)  # expected category differs
    assert s.loc["alle", "n"] == 5 and s.loc["alle", "reviewed"] == 3


def test_sample_summary_nothing_reviewed():
    df = pd.DataFrame({"match_quality": ["exact", "none"], "check_ok": [None, None]})
    s = v.sample_summary(df, "match_quality").set_index("group")
    assert s.loc["alle", "reviewed"] == 0 and pd.isna(s.loc["alle", "disputed_share"])


def test_transect_summary():
    df = pd.DataFrame({"width_traffic_m": [20.0, 15.0, 12.0], "measured_m": [21.0, None, 10.0]})
    t = v.transect_summary(df)
    assert t["n"] == 3 and t["measured"] == 2
    assert t["mean_abs_diff_m"] == pytest.approx(1.5)
    assert v.transect_summary(df.assign(measured_m=None))["mean_abs_diff_m"] is None


# --- open questions --------------------------------------------------------------------------


def test_open_questions():
    text = "# Offene Fragen\n\n## Fachlich\n- [ ] Frage 1 – Team\n- [x] erledigt\n\n## Daten\n- [ ] Frage 2\n  weiter\n## Leer\n- [x] alt\n"
    assert v.open_questions(text) == [("Fachlich", ["Frage 1 – Team"]), ("Daten", ["Frage 2 weiter"])]


def test_data_quality_main_roads_without_dtv():
    df = pd.DataFrame([seg(highway="primary", dtv_official=20000), seg(highway="secondary_link", dtv_official=None),
                       seg(highway="tertiary", dtv_official=None)])
    q = v.data_quality(df).set_index("bezirk")
    assert q.loc["gesamt", "main_n"] == 2
    assert q.loc["gesamt", "main_missing_dtv"] == pytest.approx(0.5)


def test_compare_baseline_counts_changes_on_common_ids():
    import pandas as pd
    from pipeline.lib.validation import compare_baseline
    base = pd.DataFrame({"segment_id": ["a", "b", "c", "x"], "cat_final": ["GOW50", "ETW30", "GOW30", "ETW30"],
                         "priority": [2.0, 0.5, 1.0, 0.1], "length_m": [100.0, 200.0, 300.0, 50.0]})
    cur = pd.DataFrame({"segment_id": ["a", "b", "c", "y"], "cat_final": ["GOW30", "ETW30", "GOW30", "ETW30"],
                        "priority": [1.0, 0.5, 2.0, 0.2], "length_m": [100.0, 200.0, 300.0, 70.0]})
    r = compare_baseline(base, cur, top_n=2)
    assert (r["n_common"], r["n_only_base"], r["n_only_new"]) == (3, 1, 1)
    assert r["n_changed"] == 1 and r["km_changed"] == 0.1
    assert r["changes"].to_dict("records") == [{"from": "GOW50", "to": "GOW30", "n": 1, "km": 0.1}]
    assert r["top_overlap"] == 1.0  # top 2 before {a, c}, after {c, a}
