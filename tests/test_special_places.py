"""Special places (prompts/26): schema of config/special_places.yaml and the comparison sentences."""

import copy

import pandas as pd
import pytest
import yaml
from pydantic import ValidationError

from config.schema.special_places_model import SpecialPlaces
from pipeline.lib.export import load_texts
from pipeline.lib.rules import DEFAULT_SPECIAL_PLACES_PATH, load_special_places
from pipeline.lib.special_places import comparison, comparison_values, segment_blocks

GLOSSARY = {"categories": {"ETW30": {"plain": "Wohnstraße mit Tempo 30"}, "GOW50": {"plain": "Hauptstraße mit Tempo 50"},
                           "ETW_ERF": {"plain": "Fußgängerzone oder Spielstraße"}}}


@pytest.fixture(scope="module")
def raw() -> dict:
    with open(DEFAULT_SPECIAL_PLACES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def texts() -> dict:
    return load_texts()


def test_config_valid():
    sp = load_special_places()
    assert sp.places, "at least one place"
    for p in sp.places:
        assert p.sources and p.status_date
        assert p.segment_ids()


@pytest.mark.parametrize("path, value", [
    (("sources",), []),
    (("status_date",), None),
    (("kind",), "planned"),
    (("segments", 0, "segment_ids"), ["seg_XYZ"]),
    (("segments", 0, "measure"), "car_free"),
    (("theme", "palette", "main"), "pink"),
])
def test_invalid_place_rejected(raw, path, value):
    bad = copy.deepcopy(raw)
    node = bad["places"][0]
    for k in path[:-1]:
        node = node[k]
    node[path[-1]] = value
    with pytest.raises(ValidationError):
        SpecialPlaces.model_validate(bad)


def test_segment_in_two_groups_rejected(raw):
    bad = copy.deepcopy(raw)
    groups = bad["places"][0]["segments"]
    groups[1]["segment_ids"].append(groups[0]["segment_ids"][0])
    with pytest.raises(ValidationError):
        SpecialPlaces.model_validate(bad)


def _values(cat="ETW30", soll="mixed", cycle_cat="HAUPT", bus=0, speed=30):
    seg = pd.Series({"cat_final": cat, "bus_trips_weekday": bus, "speed_ist_kmh": speed})
    fac = pd.Series({"cycle_cat_final": cycle_cat, "cycle_facility_soll": soll})
    return comparison_values(seg, fac, None, GLOSSARY)


@pytest.mark.parametrize("kw, expect", [
    ({"soll": "cycle_street"}, "auch eine Fahrradstraße"),
    ({"cycle_cat": "BASIS"}, "gehört zum Radnetz"),
    ({"cycle_cat": "ERSCHL"}, "nicht zum Radnetz"),
    ({"cat": "GOW50", "cycle_cat": None}, "weicht der Vorschlag vom Regelwerk ab"),
    ({"cat": "ETW_ERF"}, "weniger streng"),
])
def test_cycle_street_compare(texts, kw, expect):
    assert expect in comparison("cycle_street", _values(**kw), texts)["compare"]


def test_cycle_street_notes(texts):
    out = comparison("cycle_street", _values(bus=120, speed=50), texts)
    assert any("Tempo 50" in n for n in out["notes"])
    assert any("Busse" in n for n in out["notes"])
    assert comparison("cycle_street", _values(), texts)["notes"] == []


def test_missing_cycling_data_falls_through(texts):
    seg = pd.Series({"cat_final": "ETW30", "bus_trips_weekday": None, "speed_ist_kmh": None})
    out = comparison("cycle_street", comparison_values(seg, None, None, GLOSSARY), texts)
    assert "nicht zum Radnetz" in out["compare"]  # unknown network level: no claim that it belongs to the network
    assert out["notes"] == []


@pytest.mark.parametrize("cat, expect", [("ETW30", "Neue Fußgängerzonen plant es nicht"),
                                         ("ETW_ERF", "passen zusammen"), ("GOW50", "stark vom Regelwerk ab")])
def test_pedestrian_zone_compare(texts, cat, expect):
    assert expect in comparison("pedestrian_zone_bikes_allowed", _values(cat=cat), texts)["compare"]


def test_segment_blocks(texts):
    sp = load_special_places()
    place = sp.places[0]
    sid = place.segments[0].segment_ids[0]
    seg = pd.DataFrame([{"segment_id": sid, "cat_final": "ETW30", "bus_trips_weekday": 0, "speed_ist_kmh": 30},
                        {"segment_id": "seg_ffff", "cat_final": "ETW30", "bus_trips_weekday": 0, "speed_ist_kmh": 30}])
    blocks = segment_blocks(sp, seg, None, None, texts, GLOSSARY)
    assert set(blocks) == {sid}
    b = blocks[sid]
    assert b["band"].startswith(f"Besonderer Ort: {place.title} – Vorschlag des Bürgerbegehrens: ")
    assert b["status_line"].startswith("Stand 25.09.2026")


# --- cross section of the proposal ---------------------------------------------------------------------------

from pipeline.c06_cross_section_soll import _params  # noqa: E402
from pipeline.lib import profile as pf  # noqa: E402
from pipeline.lib.rules import load_cycling_rules, load_design_rules  # noqa: E402
from pipeline.lib.special_places import proposal_input, proposal_profiles  # noqa: E402


@pytest.fixture(scope="module")
def params():
    return _params(load_design_rules(), load_cycling_rules())


def _seg(params, cat="ETW30", facility="mixed"):
    return pf.SegmentInput(cat=cat, cycle_cat="HAUPT", facility=facility, fallback=None, cycle_width=None, peak_dir=None,
                           peak_both=None, dtv=None, bus_peak_dir=0.0, lanes_ist=1, oneway=False,
                           parking_sides=pf.parking_sides_soll("street_side", cat, params), business=False, tram=False)


def test_proposal_cycle_street_changes_only_the_facility(params):
    change = load_special_places().measures["cycle_street"].profile
    seg = proposal_input(_seg(params), change, "street_side", params)
    assert (seg.cat, seg.facility, seg.cycle_width) == ("ETW30", "cycle_street", None)
    assert seg.parking_sides == _seg(params).parking_sides


def test_proposal_pedestrian_zone_is_shared_surface_without_parking(params):
    change = load_special_places().measures["pedestrian_zone_bikes_allowed"].profile
    seg = proposal_input(_seg(params), change, "street_side", params)
    assert seg.cat == "ETW_ERF" and seg.parking_sides == 0
    elements = {e["element"] for e in pf.evaluate_profile(seg, 15.0, params).elements}
    assert "shared_surface" in elements and "parking_parallel" not in elements and "sidewalk" not in elements


def test_proposal_profiles_per_segment(params, texts):
    sp = load_special_places()
    sid = sp.places[0].segments[1].segment_ids[0]
    out = proposal_profiles(sp, {sid: (_seg(params), "street_side", 15.0)}, params, texts["cycling"]["fit"])
    assert set(out) == {sid}
    assert out[sid]["fit"] in pf.FIT_CLASSES and out[sid]["fit_text"]
