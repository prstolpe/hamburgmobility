"""Checks on the real data/interim/ist_facility.parquet (stage c03b, rules.yaml S-FEAT-13 / S-FEAT-11) and the
invariant V-INV-08 (Review 2026-11 F26): the Ist facility is identical in s08, c04 and c05."""

import geopandas as gpd
import pandas as pd
import pytest

from config.schema.cycling_model import FACILITIES, IST_CLASSES
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_rules

INTERIM = REPO_ROOT / "data" / "interim"
IST = INTERIM / "ist_facility.parquet"
FINAL = INTERIM / "final.parquet"
FACILITY = INTERIM / "cycle_facility.parquet"
DISCREPANCY = INTERIM / "discrepancy.parquet"
PRINCIPLES = INTERIM / "cycle_principles.parquet"
NETWORK = INTERIM / "cycle_network.parquet"

pytestmark = pytest.mark.skipif(not IST.exists(), reason="run `make ist-facility` first")
RULES = load_rules()
TRACKS = set(RULES.features.rule("S-FEAT-13").track_facilities)


@pytest.fixture(scope="module")
def ist() -> pd.DataFrame:
    return pd.read_parquet(IST).set_index("segment_id")


def test_one_row_per_segment(ist):
    final = pd.read_parquet(FINAL, columns=["segment_id"])
    assert ist.index.is_unique and set(ist.index) == set(final["segment_id"])


def test_value_domains(ist):
    assert set(ist["cycle_facility_ist"]) <= FACILITIES
    assert set(ist["cycle_osm_ist"]) <= IST_CLASSES
    assert ist["rule_trace_ist"].notna().all()


def test_track_flag_follows_ist_facility(ist):
    """S-FEAT-13: separated_cycle_track_present = ist_facility in track_facilities (unknown only for class 'no')."""
    t = ist["separated_cycle_track_present"]
    in_tracks = ist["cycle_facility_ist"].isin(TRACKS)
    assert (t[in_tracks] == True).all()  # noqa: E712
    assert (t[~in_tracks].isna() | (t[~in_tracks] == False)).all()  # noqa: E712
    assert (ist.loc[t.isna(), "cycle_osm_ist"] == "no").all()


def test_tag_only_list(ist):
    tag_only = ist["track_tag_only"].astype(bool)
    assert (ist.loc[tag_only, "cycle_osm_ist"] == "track").all()
    assert not ist.loc[tag_only, "has_sidepath"].astype(bool).any()


def test_parallel_route_only_where_assessed(ist):
    final = pd.read_parquet(FINAL, columns=["segment_id", "cat_final"]).set_index("segment_id")
    assessed = ist["parallel_cycle_route_present"].notna()
    assert set(final.loc[assessed[assessed].index, "cat_final"]) <= {"GOW50"}
    yes = ist["parallel_cycle_route_present"] == True  # noqa: E712
    assert set(ist.loc[yes, "parallel_level"]) <= set(RULES.features.rule("S-FEAT-11").qualifying_cycle_categories)
    assert (ist.loc[yes, "parallel_share"] >= RULES.conflation.rule("S-CONF-02").thresholds["min_length_share"].value).all()


# --- V-INV-08 -----------------------------------------------------------------------------------------------


@pytest.mark.skipif(not FACILITY.exists(), reason="run `make cycle-facility` first")
def test_v_inv_08_c05(ist):
    fac = pd.read_parquet(FACILITY, columns=["segment_id", "cycle_facility_ist", "cycle_osm_ist"]).set_index("segment_id")
    j = fac.join(ist, rsuffix="_s13")
    assert (j["cycle_facility_ist"] == j["cycle_facility_ist_s13"]).all()
    assert (j["cycle_osm_ist"] == j["cycle_osm_ist_s13"]).all()


@pytest.mark.skipif(not DISCREPANCY.exists(), reason="run `make discrepancy` first")
def test_v_inv_08_s08(ist):
    d = pd.read_parquet(DISCREPANCY, columns=["segment_id", "cycle_facility_ist", "separated_cycle_track_present",
                                              "parallel_cycle_route_present"]).set_index("segment_id")
    j = d.join(ist, rsuffix="_s13")
    assert (j["cycle_facility_ist"] == j["cycle_facility_ist_s13"]).all()
    for c in ("separated_cycle_track_present", "parallel_cycle_route_present"):
        a, b = j[c].astype("boolean"), j[f"{c}_s13"].astype("boolean")
        assert ((a == b).fillna(False) | (a.isna() & b.isna())).all(), c


@pytest.mark.skipif(not (PRINCIPLES.exists() and NETWORK.exists()), reason="run `make cycle-principles` first")
def test_v_inv_08_c04(ist):
    """C-PRI-02: street edges and their sidepaths carry the Ist facility of their segment."""
    pri = pd.read_parquet(PRINCIPLES, columns=["level", "id", "facility_ist"])
    pri = pri[pri["level"] == "edge"].set_index("id")
    net = gpd.read_parquet(NETWORK, columns=["edge_id", "kind", "segment_id", "sidepath_of", "geometry"]).set_index("edge_id")
    owner = net["segment_id"].where(net["kind"] == "road").fillna(net["sidepath_of"].where(net["kind"] == "path"))
    owner = owner.reindex(pri.index).dropna()
    owner = owner[owner.isin(ist.index)]
    assert len(owner) > 0
    assert (pri.loc[owner.index, "facility_ist"].to_numpy() == ist.loc[owner.to_numpy(), "cycle_facility_ist"].to_numpy()).all()
