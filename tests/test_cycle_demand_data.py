"""Checks on the real data/interim/cycle_edges.parquet (skipped until `make cycle-demand` has run)."""

import json

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest

from pipeline.lib.cycle_demand import DemandParams
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_cycling_rules

EDGES = REPO_ROOT / "data" / "interim" / "cycle_edges.parquet"
FINAL = REPO_ROOT / "data" / "interim" / "final.parquet"
ALKIS = REPO_ROOT / "data" / "raw" / "alkis__GebaeudeBauwerk.parquet"

pytestmark = pytest.mark.skipif(not EDGES.exists(), reason="run `make cycle-demand` first")
PARAMS = DemandParams.from_rules(load_cycling_rules())


@pytest.fixture(scope="module")
def edges() -> gpd.GeoDataFrame:
    return gpd.read_parquet(EDGES)


def test_crs_and_geometry(edges):
    assert edges.crs == "EPSG:25832"
    assert edges.geometry.is_valid.all()
    assert (edges["length_m"] > 0).all()


def test_columns(edges):
    assert {"edge_id", "segment_id", "sidepath_of", "kind", "cost_fwd", "cost_bwd", "impedance_trace",
            "cyc_day_model", "cyc_calibrated", "cyc_day_fwd", "cyc_day_bwd", "cyc_peak_h", "demand_confidence",
            "demand_trace", "bezirk"} <= set(edges.columns)


def test_edge_ids_unique_and_prefixed(edges):
    assert edges["edge_id"].is_unique
    assert edges["edge_id"].str.fullmatch(r"ce_[0-9a-f]{16}").all()


def test_segment_references_exist():
    e = pd.read_parquet(EDGES, columns=["segment_id", "sidepath_of"])
    ids = set(pd.read_parquet(FINAL, columns=["segment_id"])["segment_id"])
    for col in ("segment_id", "sidepath_of"):
        assert set(e[col].dropna()) <= ids, col


def test_edges_blocked_both_ways_are_rare_and_carry_no_flow(edges):
    # chains of OSM ways with contradicting oneway tags; listed in reports/cycle_graph.md
    blocked = edges["cost_fwd"].isna() & edges["cost_bwd"].isna()
    assert edges.loc[blocked, "length_m"].sum() < 0.001 * edges["length_m"].sum()
    assert (edges.loc[blocked, "cyc_calibrated"].fillna(0) == 0).all()


def test_main_component_has_flows(edges):
    main = edges["in_main_component"]
    assert edges.loc[main, "cyc_calibrated"].notna().all()
    assert edges.loc[~main, "cyc_calibrated"].isna().all()


def test_calibrated_is_model_times_one_factor(edges):
    m = edges["cyc_day_model"] > 0
    k = (edges.loc[m, "cyc_calibrated"] / edges.loc[m, "cyc_day_model"]).unique()
    assert np.allclose(k, k[0])
    assert json.loads(edges["demand_trace"].iloc[0])["k"] == pytest.approx(k[0], rel=1e-3)


def test_directions_sum_to_total(edges):
    m = edges["cyc_calibrated"].notna()
    assert np.allclose(edges.loc[m, "cyc_day_fwd"] + edges.loc[m, "cyc_day_bwd"], edges.loc[m, "cyc_calibrated"])


def test_no_flow_against_a_blocked_direction(edges):
    assert (edges.loc[edges["cost_fwd"].isna(), "cyc_day_fwd"].fillna(0) == 0).all()
    assert (edges.loc[edges["cost_bwd"].isna(), "cyc_day_bwd"].fillna(0) == 0).all()


def test_peak_hour_share_from_yaml(edges):
    m = edges["cyc_calibrated"].notna()
    assert np.allclose(edges.loc[m, "cyc_peak_h"], edges.loc[m, "cyc_calibrated"] * PARAMS.peak_hour_share)


def test_confidence_values(edges):
    assert set(edges["demand_confidence"]) <= {"hoch", "mittel", "niedrig"}
    assert (edges.loc[edges["cyc_calibrated"].isna(), "demand_confidence"] == "niedrig").all()


@pytest.mark.skipif(not ALKIS.exists(), reason="ALKIS buildings missing")
def test_alkis_function_lists_occur_in_data():
    f = set(pd.read_parquet(ALKIS, columns=["funktion"])["funktion"].dropna())
    assert PARAMS.excluded_functions <= f, sorted(PARAMS.excluded_functions - f)
    assert PARAMS.mixed_use_functions <= f, sorted(PARAMS.mixed_use_functions - f)
