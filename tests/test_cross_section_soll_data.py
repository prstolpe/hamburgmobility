"""Checks on the real data/interim/cross_section_soll.parquet (skipped until `make cross-section-soll` has run)."""

import json

import geopandas as gpd
import pandas as pd
import pytest

from config.schema.cycling_model import FACILITIES
from pipeline.lib import profile as pf
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_cycling_rules, load_design_rules, load_rules

OUT = REPO_ROOT / "data" / "interim" / "cross_section_soll.parquet"
FINAL = REPO_ROOT / "data" / "interim" / "final.parquet"

pytestmark = pytest.mark.skipif(not OUT.exists(), reason="run `make cross-section-soll` first")
P = pf.ProfileParams.from_rules(load_design_rules(), load_cycling_rules(), load_rules())


@pytest.fixture(scope="module")
def out() -> gpd.GeoDataFrame:
    return gpd.read_parquet(OUT)


def test_one_row_per_segment(out):
    final = pd.read_parquet(FINAL, columns=["segment_id"])
    assert out["segment_id"].is_unique
    assert set(out["segment_id"]) == set(final["segment_id"])
    assert out.crs == "EPSG:25832"


def test_value_domains(out):
    assert set(out["fit_class"].dropna()) <= set(pf.FIT_CLASSES)
    assert set(out["fit_class_facade"].dropna()) <= set(pf.FIT_CLASSES)
    assert set(out["cycle_side"].dropna()) <= set(pf.CYCLE_SIDES)
    assert set(out["cycle_facility_final"].dropna()) <= FACILITIES
    assert set(out["lanes_per_dir_soll"].dropna()) <= {"1", "2", "shared"}
    steps = {s for v in out["degrade_steps_applied"].dropna() for s in v.split("|")}
    assert steps <= set(P.cascade_order)
    assert set(out["cat_change_proposal"].dropna()) <= {"GOW30"}


def test_total_matches_elements(out):
    rated = out[out["total_required_m"].notna()]
    totals = rated["profile_elements"].map(lambda s: sum(e["width_m"] for e in json.loads(s)))
    assert (abs(totals - rated["total_required_m"]) < 0.05).all()


def test_fit_class_consistent_with_widths(out):
    r = out[out["fit_class"].notna()]
    fits = r["fit_class"].isin(["fits", "fits_after_degrade"])
    assert (r.loc[fits, "total_required_m"] <= r.loc[fits, "available_m"] + 1e-6).all()
    assert (r.loc[~fits, "total_required_m"] > r.loc[~fits, "available_m"]).all()
    assert r.loc[r["fit_class"] == "fits", "degrade_steps_applied"].isna().all()


def test_never_more_lanes_than_ist(out):
    num = pd.to_numeric(out["lanes_per_dir_soll"], errors="coerce")
    ist = out["lanes_per_dir_ist"]
    known = num.notna() & ist.notna()
    assert (num[known] <= ist[known]).all()


def test_gow30_and_etw_at_most_one_lane(out):
    m = out["cat_final"].isin(["GOW30"])
    assert (out.loc[m, "lanes_per_dir_soll"] == "1").all()
    e = out["cat_final"].isin(["ETW30", "ETW_ERF"])
    assert (out.loc[e, "lanes_per_dir_soll"] == "shared").all()


def test_d5_only_on_gow50(out):
    assert (out.loc[out["cat_change_proposal"].notna(), "cat_final"] == "GOW50").all()


def test_every_profile_has_trace(out):
    rated = out[out["fit_class"].notna()]
    for t in rated["rule_trace_profile"].sample(min(200, len(rated)), random_state=1):
        ids = {s["id"] for s in json.loads(t)}
        assert {"PRF-05", "PRF-06"} <= ids


def _effective_cat(out):
    """Category the profile was built for: the D5 proposal (GOW30) where present, else cat_final."""
    return out["cat_change_proposal"].fillna(out["cat_final"])


def test_v_inv_03_no_element_the_category_forbids(out):
    """V-INV-03 (Review 2026-11 F11): no parking and no cycle lane in GOW50 profiles, no centre line (second lane or
    median) on GOW30 (rules.yaml requirements: parking_along_carriageway, cycle_lanes_allowed, centre_line)."""
    cat = _effective_cat(out)
    elements = out["profile_elements"].map(lambda s: {e["element"] for e in json.loads(s)} if isinstance(s, str) else set())
    gow50 = cat == "GOW50"
    assert not elements[gow50].map(lambda e: "parking_parallel" in e or "cycle_lane" in e).any()
    gow30 = cat == "GOW30"
    assert (out.loc[gow30, "lanes_per_dir_soll"] == "1").all()
    assert not out.loc[gow30, "median_soll"].astype(bool).any()
    assert not elements[gow30].map(lambda e: "median" in e).any()


def test_v_inv_04_no_cycle_lane_on_high_volume_gow30(out):
    """V-INV-04 (F01): the final facility after the cascade is never a cycle lane on GOW30 above wide.max_dtv."""
    final = pd.read_parquet(FINAL, columns=["segment_id", "dtv_official"]).set_index("segment_id")
    dtv = out["segment_id"].map(final["dtv_official"])
    high = (_effective_cat(out) == "GOW30") & (dtv > P.fp.high_volume["GOW30"].dtv_above)
    assert not (high & (out["cycle_facility_final"] == "cycle_lane")).any()


def test_l07_reduction_only_on_gow30(out):
    flagged = out["profile_flags"].fillna("").str.split("|").apply(lambda xs: pf.CAPACITY_FLAG in xs)
    assert (out.loc[flagged, "cat_final"] == "GOW30").all()
    assert (out.loc[flagged, "capacity_reduction_dtv"] > 0).all()
    assert out.loc[~flagged, "capacity_reduction_dtv"].isna().all()


V_INV_05_STEPS = {"D1", "D2", "D3", "fallback", "D4"}


def v_inv_05_violations(out) -> pd.DataFrame:
    """Segments that fit in S-XS-06 (feasibility of their category) but not in c06 after at most D4."""
    target = {"GOW50": "feasibility_GOW50", "GOW30": "feasibility_GOW30_narrow", "ETW30": "feasibility_ETW30"}
    final = pd.read_parquet(FINAL, columns=["segment_id", *target.values()]).set_index("segment_id")
    feas = pd.Series(None, index=out.index, dtype=object)
    for cat, col in target.items():
        m = out["cat_final"] == cat
        feas[m] = out.loc[m, "segment_id"].map(final[col]).to_numpy()
    rated = out["fit_class"].notna() & (feas == "fits")
    steps = out["degrade_steps_applied"].fillna("").str.split("|").map(lambda xs: {x for x in xs if x} - {"D6", "D7"})
    ok = out["fit_class"].isin(["fits", "fits_after_degrade"]) & steps.map(lambda s: s <= V_INV_05_STEPS)
    return out[rated & ~ok]


@pytest.mark.xfail(reason="V-INV-05 auf realen Daten verletzt (1 069 Abschnitte, 134 km): Ladezone baut keine Stufe ab, "
                          "Busfahrbahn ETW30 6,50 m und GOW30-Profil mit Radweg/Radfahrstreifen sind breiter als required_width; "
                          "docs/open_questions.md, Review 2026-11 P3 V-INV-05", strict=True)
def test_v_inv_05_fits_in_s_xs_06_fits_after_d4(out):
    """V-INV-05 (Review 2026-11 F05): fits in S-XS-06 => c06 fits or fits_after_degrade with steps up to D4."""
    assert v_inv_05_violations(out).empty
