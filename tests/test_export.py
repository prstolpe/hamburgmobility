"""Export helpers (pipeline/lib/export.py): plain text from rule_trace, public columns, search index, tiles."""

import json

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import LineString

from pipeline.lib import export as ex
from pipeline.lib.rules import load_rules

RULES = load_rules()
TEXTS = ex.load_texts()


def resolve(ref):
    return ex.ref_resolver(RULES)(ref)


# --- render ----------------------------------------------------------------------------------


@pytest.mark.parametrize("template, values, expected", [
    ("{w|.1f} m", {"w": 14.234}, "14,2 m"),
    ("{w|.0f} m", {"w": 99.6}, "100 m"),
    ("{s|%}", {"s": 0.5}, "50 %"),
    ("{h}", {"h": "primary"}, "primary"),
    ("{b|yesno}", {"b": True}, "ja"),
    ("nötig {required_width.GOW50|.1f} m", {}, "nötig 16,5 m"),
    ("ab {thresholds.conn_gow|.2f}", {}, "ab 0,60"),
    ("{w|.1f}", {"w": None}, "unbekannt"),
])
def test_render(template, values, expected):
    assert ex.render(template, values, resolve) == expected


def test_render_unknown_placeholder_fails():
    with pytest.raises(KeyError):
        ex.render("{thresholds.nope}", {}, resolve)


# --- reasons from rule_trace -----------------------------------------------------------------


def _step(rule_id, passed, **inputs):
    return {"id": rule_id, "passed": passed, "result": passed, "inputs": inputs, "confidence": "hoch"}


def test_reason_c_g30_02_names_widths():
    trace = [_step("C-SW-01", False, highway="primary", access_motor_only=False),
             _step("C-GOW-01", True, conn_score=0.88, in_hvs=True),
             _step("C-G30-01", False, schools_or_kitas_within_m=400.0, shop_frontage_share=0.1,
                   crossing_demand="not_assessed"),
             _step("C-G30-02", True, separated_cycle_track_present=False, width_p10_m=14.2)]
    reasons = ex.rule_reasons(trace, RULES, TEXTS)
    assert [r["rule"] for r in reasons] == ["C-GOW-01", "C-G30-01", "C-G30-02"]  # failed C-SW-01 has no text
    assert reasons[0]["text"] == ("Hauptverkehrsstraße der BVM; hohe Verbindungsfunktion: Verbindungswert 0,88 "
                                  "(ab 0,60)")
    assert reasons[2]["text"] == ("kein baulicher Radweg, und für einen fehlt der Platz: Straßenraum 14,2 m, "
                                  "nötig 16,5 m")
    assert reasons[2]["passed"] is True and reasons[1]["passed"] is False


def test_reason_only_true_fragments():
    trace = [_step("C-G30-01", True, schools_or_kitas_within_m=43.6, shop_frontage_share=0.5,
                   crossing_demand="not_assessed")]
    text = ex.rule_reasons(trace, RULES, TEXTS)[0]["text"]
    assert text.startswith("Schule oder Kita in 44 m (bis 150 m); viele Gebäude mit Läden oder Publikumsverkehr: 50 %")
    assert "Querungsbedarf" not in text


def test_reason_unknown_fragment_left_out():
    trace = [_step("C-G30-02", False, separated_cycle_track_present=True, width_p10_m=None)]
    assert ex.rule_reasons(trace, RULES, TEXTS)[0]["text"] == "baulicher Radweg vorhanden"


def test_every_cascade_rule_has_a_text():
    ids = {r.id for r in RULES.classification}
    assert ids <= set(TEXTS["rules"])
    assert set(RULES.categories) <= set(TEXTS["categories"])


def test_confidence_info():
    info = ex.confidence_info("mittel", ["fallback:in_hvs", "nahe_schwelle:conn_score~thresholds.conn_gow",
                                         "fehlt:width_p10_m"], TEXTS)
    assert info["level"] == "mittel"
    assert info["reasons"] == ["Hauptverkehrsstraße (Verkehrsmengenkarte 2019 statt HVS-Karte 2023): Ersatzquelle oder "
                               "Standardwert", "Verbindungswert (nicht alle Merkmale bekannt): nahe an der Schwelle",
                               "Straßenraumbreite: fehlt"]


# --- frames ----------------------------------------------------------------------------------


def _segments():
    geom = [LineString([(565000, 5935000), (565100, 5935000)]), LineString([(565100, 5935000), (565100, 5935200)]),
            LineString([(566000, 5936000), (566050, 5936000)])]
    return gpd.GeoDataFrame({
        "segment_id": ["seg_a", "seg_b", "seg_c"], "name": ["Hallerstraße", "Hallerstraße", None],
        "bezirk": ["Eimsbüttel"] * 3, "osm_way_ids": [[1, 2], [3], [4]], "cat_final": ["GOW30", "GOW30", "ETW30"],
        "crashes_ped_cyc": [2, 0, 1], "width_p10_m": [14.2, None, 9.0], "priority": [1.5, 0.0, None],
    }, geometry=geom, crs="EPSG:25832")


def test_public_frame_is_wgs84_and_whitelisted():
    seg = _segments().assign(LINREFX=1.0, rule_trace="[]")
    out = ex.public_frame(seg)
    assert out.crs.to_epsg() == 4326
    assert "LINREFX" not in out.columns and "rule_trace" not in out.columns
    assert list(out["segment_id"]) == ["seg_a", "seg_b", "seg_c"]
    assert out["osm_way_ids"].iloc[0] == "1;2"


def test_public_columns_have_no_single_crash_fields():
    assert not {c for c in ex.PUBLIC_COLUMNS if c.startswith(("U", "LINREF", "XGCS", "YGCS"))}


def test_search_index_groups_named_streets():
    idx = ex.search_index(_segments().to_crs(4326))
    assert len(idx) == 1
    s = idx[0]
    assert (s["name"], s["bezirk"], s["n"]) == ("Hallerstraße", "Eimsbüttel", 2)
    west, south, east, north = s["bbox"]
    assert west < east and south < north
    assert s["ids"] == ["seg_a", "seg_b"]
    json.dumps(idx)


# --- sensitivity (prompts/12_validation.md) --------------------------------------------------


def test_sensitivity_info_uncertain():
    info = ex.sensitivity_info({"sens_change_rate": 0.42, "sens_uncertain": True, "sens_alt_category": "GOW30",
                                "sens_oat_changes": '["thresholds.conn_gow:-", "conn_score.in_hvs:-"]'},
                               RULES, TEXTS, runs=500, delta=0.2)
    assert info["uncertain"] is True and info["change_rate"] == pytest.approx(0.42)
    assert info["alternative"] == "GOW30"
    assert "42 %" in info["text"] and "500" in info["text"] and RULES.categories["GOW30"].label_de in info["text"]
    assert info["uncertain_text"]
    assert info["oat_intro"].endswith(":") and "20 %" in info["oat_intro"]
    assert info["triggers"] == ["Schwelle für den Verbindungswert niedriger", "Gewicht Hauptverkehrsstraße niedriger"]


def test_sensitivity_info_stable_and_missing():
    stable = ex.sensitivity_info({"sens_change_rate": 0.0, "sens_uncertain": False, "sens_alt_category": None,
                                  "sens_oat_changes": "[]"}, RULES, TEXTS, runs=500, delta=0.2)
    assert stable["uncertain"] is False and "allen 500" in stable["text"] and stable["triggers"] == []
    assert stable["uncertain_text"] is None
    missing = ex.sensitivity_info({}, RULES, TEXTS, runs=500, delta=0.2)
    assert missing["change_rate"] is None and missing["uncertain"] is None
    assert missing["text"] == TEXTS["sensitivity"]["not_assessed"]


def test_every_varied_category_parameter_has_a_label():
    from pipeline.lib import sensitivity as sens
    keys = {p.key for p in sens.varied_parameters(RULES) if p.effect == "category"}
    assert keys <= set(TEXTS["sensitivity"]["params"])


def test_public_and_tile_columns_include_sensitivity():
    assert {"sens_change_rate", "sens_uncertain"} <= set(ex.PUBLIC_COLUMNS)
    assert ex.TILE_COLUMNS["un"] == "sens_uncertain"
    assert all(c in TEXTS["columns"] for c in ex.PUBLIC_COLUMNS)


# --- harmonisation (H-STR-01) ----------------------------------------------------------------


def test_harmonisation_reason_text():
    trace = [{"id": "H-STR-01", "passed": True, "inputs": {"from_cat": "GOW50", "to_cat": "GOW30", "run_m": 86.4,
                                                           "neighbours": "GOW30 und GOW30", "step": 3, "pass": 1}}]
    reasons = ex.rule_reasons(trace, RULES, TEXTS)
    assert len(reasons) == 1 and reasons[0]["rule"] == "H-STR-01"
    assert "86 m" in reasons[0]["text"] and "GOW30 und GOW30" in reasons[0]["text"]


def test_cat_cascade_is_public():
    assert "cat_cascade" in ex.PUBLIC_COLUMNS and "cat_cascade" in TEXTS["columns"]


def test_district_slug_is_ascii_and_stable():
    from pipeline.lib.export import district_slug
    assert district_slug("Eimsbüttel") == "eimsbuettel"
    assert district_slug("Hamburg-Mitte") == "hamburg-mitte"
    assert district_slug("Wandsbek") == "wandsbek"
    assert district_slug("Groß Flottbek") == "gross-flottbek"
