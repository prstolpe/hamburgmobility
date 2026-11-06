"""Checks on the real data/interim/cycle_principles.parquet (skipped until `make cycle-principles` has run)."""

import json

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest

from pipeline.lib import principles as pr
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_cycling_rules, load_rules

OUT = REPO_ROOT / "data" / "interim" / "cycle_principles.parquet"
ROUTES = REPO_ROOT / "data" / "interim" / "cycle_routes.parquet"
NETWORK = REPO_ROOT / "data" / "interim" / "cycle_network.parquet"

pytestmark = pytest.mark.skipif(not OUT.exists(), reason="run `make cycle-principles` first")
P = pr.PrincipleParams.from_rules(load_cycling_rules(), load_rules())
SCORE_COLS = [f"{k}_{v}" for k in P.weights for v in ("ist", "soll")] + ["score_ist", "score_soll"]


@pytest.fixture(scope="module")
def out() -> gpd.GeoDataFrame:
    return gpd.read_parquet(OUT)


def test_crs_and_levels(out):
    assert out.crs == "EPSG:25832"
    assert set(out["level"]) == {"edge", "route"}


def test_one_row_per_route(out):
    routes = pd.read_parquet(ROUTES, columns=["route_id"])
    r = out[out["level"] == "route"]
    assert r["id"].is_unique
    assert set(r["id"]) == set(routes["route_id"])


def test_edges_are_soll_network_edges(out):
    net = pd.read_parquet(NETWORK, columns=["edge_id", "cycle_cat_final", "route_id"])
    e = out[out["level"] == "edge"]
    assert e["id"].is_unique
    in_net = net[(net["cycle_cat_final"] != "ERSCHL") | net["route_id"].notna()]
    assert set(e["id"]) == set(in_net["edge_id"])


def test_scores_in_unit_interval(out):
    for c in SCORE_COLS + ["confidence_ist", "confidence_soll"]:
        v = out[c].dropna()
        assert ((v >= -1e-9) & (v <= 1 + 1e-9)).all(), c


def test_every_route_has_a_total_score_and_confidence(out):
    r = out[out["level"] == "route"]
    assert r["score_ist"].notna().all()
    assert r["score_soll"].notna().all()
    assert r["confidence"].isin(["high", "medium", "low"]).all()


def test_soll_not_below_ist_for_build_out_checks(out):
    for c in ("p_saf_01", "p_saf_03", "p_com_01", "p_com_02"):
        both = out[[f"{c}_ist", f"{c}_soll"]].dropna()
        assert (both[f"{c}_soll"] >= both[f"{c}_ist"] - 1e-9).all(), c


def test_unavailable_checks_are_unknown(out):
    for c in P.unavailable:
        col = c.lower().replace("-", "_")
        assert out[f"{col}_ist"].isna().all() and out[f"{col}_soll"].isna().all(), c


def test_confidence_capped_by_unavailable_checks(out):
    assert out["confidence_ist"].max() < 1.0


def test_detour_at_least_one(out):
    d = out.loc[out["level"] == "route", "detour"].dropna()
    assert (d >= 1 - 1e-6).all()


def test_rule_trace_parses_and_names_checks(out):
    sample = out.sample(200, random_state=1)
    for t in sample["rule_trace_principles"]:
        steps = json.loads(t)
        assert {s["rule"] for s in steps} <= set(P.check_principle)


def test_only_aggregated_crash_values(out):
    crash_cols = [c for c in out.columns if "crash" in c]
    assert set(crash_cols) <= {"crashes_cyc_5y", "crashes_cyc_per_km_5y"}
    assert not any(c in out.columns for c in ("unfall_id", "OID_", "UJAHR", "LINREFX"))
    assert np.issubdtype(out["crashes_cyc_per_km_5y"].dtype, np.floating)
