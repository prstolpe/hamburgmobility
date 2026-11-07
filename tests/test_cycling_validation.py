"""Helpers of the cycling validation (pipeline/lib/cycling_validation.py, prompts/21_web_validation_cycling.md)."""

import copy

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import yaml
from shapely.geometry import LineString, box

from config.schema.cycling_model import CyclingRuleSet
from config.schema.design_model import DesignRuleSet
from pipeline.lib import cycling_validation as cv
from pipeline.lib.rules import DEFAULT_CYCLING_RULES_PATH, DEFAULT_DESIGN_RULES_PATH

RAW = {
    "meta": {"version": "1.0"},
    "widths_m": {
        "project_target": {"source_type": "assumption", "separated_oneway": {"HAUPT": 2.5, "BASIS": 2.0}},
        "de": {"source_type": "de_regelwerk", "separated_oneway": 2.0},
    },
    "lanes": {
        "default_per_direction": {"GOW50": 1, "source_type": "assumption"},
        "rules": [{"id": "L-02", "source_type": "assumption", "lane_capacity_veh_h": {"value": 900, "source_type": "assumption"},
                   "target_vc": {"value": 0.85}},
                  {"id": "L-03", "source_type": "swov_crow", "median": {"value": 2.0}}],
    },
    "profile_assignment": {"source_type": "assumption", "rules": [{"id": "PRF-03", "tree_sides": 2, "seed": 42,
                                                                    "tram_route_types": [0, 900], "flag": True}]},
    "cross_section_allocation": {"source_type": "assumption", "elements_min_m": {"building_buffer": 0.0, "tree_strip": 2.0}},
    "demand_model": {"rules": [{"id": "C-DEM-04", "source_type": "assumption", "beta_per_km": 0.25}]},
}


def _by_key(params):
    return {p.key: p for p in params}


def test_assumption_params_inherit_source_type_and_skip_other_types():
    ps = _by_key(cv.assumption_params(RAW, "design"))
    assert ps["widths_m.project_target.separated_oneway.HAUPT"].value == 2.5
    assert ps["lanes.rules.[L-02].target_vc.value"].value == 0.85  # inherits from the rule
    assert "widths_m.de.separated_oneway" not in ps
    assert "lanes.rules.[L-03].median.value" not in ps
    assert "meta.version" not in ps


def test_structural_and_zero_values_are_listed_but_not_varied():
    ps = _by_key(cv.assumption_params(RAW, "design"))
    for key in ("lanes.default_per_direction.GOW50", "profile_assignment.rules.[PRF-03].tree_sides",
                "profile_assignment.rules.[PRF-03].seed", "profile_assignment.rules.[PRF-03].tram_route_types.[1]"):
        assert ps[key].skip == "structural", key
    assert ps["cross_section_allocation.elements_min_m.building_buffer"].skip == "zero"
    assert ps["cross_section_allocation.elements_min_m.tree_strip"].skip is None
    assert "profile_assignment.rules.[PRF-03].flag" not in ps  # booleans are not numbers here


def test_stage_by_section():
    ps = _by_key(cv.assumption_params(RAW, "cycling"))
    assert ps["widths_m.project_target.separated_oneway.HAUPT"].stage == "c05"
    assert ps["demand_model.rules.[C-DEM-04].beta_per_km"].stage is None
    pd_ = _by_key(cv.assumption_params(RAW, "design"))
    assert pd_["lanes.rules.[L-02].lane_capacity_veh_h.value"].stage == "c06"


def test_with_value_copies():
    ps = _by_key(cv.assumption_params(RAW, "design"))
    p = ps["lanes.rules.[L-02].lane_capacity_veh_h.value"]
    before = copy.deepcopy(RAW)
    out = cv.with_value(RAW, p.path, 720.0)
    assert out["lanes"]["rules"][0]["lane_capacity_veh_h"]["value"] == 720.0
    assert RAW == before


@pytest.mark.parametrize("path, model, file", [(DEFAULT_CYCLING_RULES_PATH, CyclingRuleSet, "cycling"),
                                                 (DEFAULT_DESIGN_RULES_PATH, DesignRuleSet, "design")])
def test_real_rules_vary_and_validate(path, model, file):
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    params = [p for p in cv.assumption_params(raw, file) if p.skip is None and p.stage]
    assert params, "recomputed assumptions expected"
    for p in params:
        for f in (0.8, 1.2):
            model.model_validate(cv.with_value(raw, p.path, p.value * f))  # still a valid rule set


def test_real_rules_cover_the_recomputed_sections():
    raw_c = yaml.safe_load(DEFAULT_CYCLING_RULES_PATH.read_text(encoding="utf-8"))
    raw_d = yaml.safe_load(DEFAULT_DESIGN_RULES_PATH.read_text(encoding="utf-8"))
    keys = {p.key for p in cv.assumption_params(raw_c, "cycling") + cv.assumption_params(raw_d, "design")
            if p.skip is None and p.stage}
    assert "cycle_street.max_motor_vehicles_day.value" in keys
    assert "lanes.rules.[L-02].lane_capacity_veh_h.value" in keys
    assert "junctions.thresholds.roundabout_max_dtv.value" in keys
    assert "junctions.method.[J-M-02].dtv_share_entering.value" in keys
    assert "junctions.method.[J-M-01].cluster_radius_m.value" not in keys  # node building is not rerun


def test_change_share_by_count_and_length():
    base = pd.Series(["a", "b", None, "c"])
    run = pd.Series(["a", "x", None, "y"])
    length = pd.Series([100.0, 300.0, 50.0, 50.0])
    n, km = cv.change_share(base, run, length)
    assert n == pytest.approx(0.5)
    assert km == pytest.approx(350 / 500)


def test_change_share_treats_none_to_value_as_change():
    n, _ = cv.change_share(pd.Series([None, "a"]), pd.Series(["a", "a"]), pd.Series([1.0, 1.0]))
    assert n == pytest.approx(0.5)


def test_arm_rep_ids_pick_the_segment_whose_facility_the_arm_carries():
    base = {"seg_a": "mixed", "seg_b": "cycle_street", "seg_c": "mixed"}
    legs = [{"ids": ["seg_a", "seg_b"], "facility": "cycle_street"},
            {"ids": ["seg_c"], "facility": "mixed"},
            {"ids": ["path_1"], "facility": None}]
    assert cv.arm_rep_ids(legs, base) == ["seg_b", "seg_c", None]


def test_official_by_district():
    districts = gpd.GeoDataFrame({"name": ["West", "Ost"]}, geometry=[box(0, 0, 100, 100), box(100, 0, 200, 100)],
                                 crs="EPSG:25832")
    official = gpd.GeoDataFrame({"status": ["Bestand", "In Arbeit"]},
                                geometry=[LineString([(10, 50), (190, 50)]), LineString([(10, 10), (90, 10)])], crs="EPSG:25832")
    soll = gpd.GeoDataFrame({"cycle_cat_final": ["HAUPT", "BASIS", "HAUPT"], "bezirk": ["West", "Ost", "Ost"]},
                            geometry=[LineString([(10, 52), (90, 52)]), LineString([(110, 52), (190, 52)]),
                                      LineString([(110, 90), (190, 90)])], crs="EPSG:25832")
    t = cv.official_by_district(soll, official, districts, buffer_m=5, official_status=("Bestand",),
                                planned_status=("In Arbeit",)).set_index("bezirk")
    assert t.loc["West", "official_km"] == pytest.approx(0.09)
    assert t.loc["West", "official_on_soll_hr_km"] == pytest.approx(0.0846, abs=1e-3)  # round buffer caps
    assert t.loc["Ost", "official_km"] == pytest.approx(0.09)
    assert t.loc["Ost", "official_on_soll_hr_km"] == pytest.approx(0.0)
    assert t.loc["Ost", "official_on_soll_any_km"] == pytest.approx(0.0846, abs=1e-3)
    assert t.loc["Ost", "soll_hr_km"] == pytest.approx(0.08)
    assert t.loc["Ost", "soll_hr_additional_km"] == pytest.approx(0.08)
    assert t.loc["West", "planned_km"] == pytest.approx(0.08)
    assert t.loc["Hamburg", "official_km"] == pytest.approx(0.18)
    assert np.isclose(t.loc["Hamburg", "soll_hr_km"], 0.16)
