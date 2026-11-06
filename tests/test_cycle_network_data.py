"""Checks on the real data/interim/cycle_network.parquet and cycle_routes.parquet (skipped until
`make cycle-network` has run)."""

import json

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest

from pipeline.lib import cycle_network as cn
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_cycling_rules

NETWORK = REPO_ROOT / "data" / "interim" / "cycle_network.parquet"
ROUTES = REPO_ROOT / "data" / "interim" / "cycle_routes.parquet"
EDGES = REPO_ROOT / "data" / "interim" / "cycle_edges.parquet"

pytestmark = pytest.mark.skipif(not NETWORK.exists() or not ROUTES.exists(), reason="run `make cycle-network` first")
P = cn.NetworkParams.from_rules(load_cycling_rules())


@pytest.fixture(scope="module")
def net() -> gpd.GeoDataFrame:
    return gpd.read_parquet(NETWORK)


@pytest.fixture(scope="module")
def routes() -> gpd.GeoDataFrame:
    return gpd.read_parquet(ROUTES)


def test_crs_and_columns(net):
    assert net.crs == "EPSG:25832"
    assert {"edge_id", "cycle_cat_proposed", "cycle_cat_final", "cycle_cat_source", "route_id", "route_ids",
            "rule_trace_cycle", "official_network", "soll_factor", "design_cost"} <= set(net.columns)


def test_same_edges_as_cycle_graph(net):
    edges = pd.read_parquet(EDGES, columns=["edge_id"])
    assert net["edge_id"].is_unique
    assert set(net["edge_id"]) == set(edges["edge_id"])


def test_every_edge_has_a_category(net):
    assert net["cycle_cat_proposed"].isin(cn.CATEGORY_ORDER).all()
    assert net["cycle_cat_final"].isin(cn.CATEGORY_ORDER).all()


def test_final_equals_proposed_without_override(net):
    plain = net["cycle_cat_source"] == "proposed"
    assert (net.loc[plain, "cycle_cat_final"] == net.loc[plain, "cycle_cat_proposed"]).all()


def test_trace_is_json_with_rule_ids(net):
    for t in net["rule_trace_cycle"].sample(500, random_state=1):
        steps = json.loads(t)
        assert steps[0]["rule"] == "C-NET-03"
        assert all("rule" in s and "result" in s for s in steps)


def test_network_edges_belong_to_a_route(net):
    in_net = net["cycle_cat_proposed"] != "ERSCHL"
    on_route = net["route_id"].notna() | net["patt_main_street"]
    assert (on_route[in_net]).all()


def test_rsv_runs_long_enough(routes):
    """Each RSV run along a corridor is at least min_route_length_km long (C-NET-06)."""
    net = pd.read_parquet(NETWORK, columns=["edge_id", "length_m", "cyc_calibrated"]).set_index("edge_id")
    for _, r in routes[routes["n_rsv_edges"] > 0].iterrows():
        ids = json.loads(r["edge_ids"])
        mask = cn.rsv_mask(net.loc[ids, "length_m"].to_numpy(), net.loc[ids, "cyc_calibrated"].to_numpy(), P)
        assert mask.sum() == r["n_rsv_edges"]


def test_route_ids_unique_and_prefixed(routes):
    assert routes["route_id"].is_unique
    assert routes["route_id"].str.startswith("rt_").all()


def test_haupt_and_basis_connected(net):
    """P-COH-02: HAUPT+RSV and BASIS+higher are one connected network each."""
    from scipy.sparse.csgraph import connected_components

    rank = net["cycle_cat_final"].map(cn.RANK).to_numpy()
    for level in ("HAUPT", "BASIS"):
        pos = np.flatnonzero(rank >= cn.RANK[level])
        g = cn.Graph(net["node_u"].to_numpy()[pos], net["node_v"].to_numpy()[pos], np.ones(len(pos)), pos)
        n, _ = connected_components(g.matrix, directed=False)
        assert n == 1, level
