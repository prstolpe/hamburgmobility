"""Checks on the real interim data for the cycling validation (skipped until `make junctions` has run)."""

import geopandas as gpd
import pandas as pd
import pytest

from pipeline import c08_validate_cycling as c08
from pipeline.lib.rules import load_cycling_rules, load_design_rules, load_rules

NEEDED = (c08.FINAL_PATH, c08.FACILITY_PATH, c08.XS_PATH, c08.JUNCTIONS_PATH)
pytestmark = pytest.mark.skipif(not all(p.exists() for p in NEEDED), reason="run the cycling stages first")


@pytest.fixture(scope="module")
def chain_and_stored():
    fac = gpd.read_parquet(c08.FACILITY_PATH, columns=c08.FAC_COLS).set_index("segment_id")
    xs = pd.read_parquet(c08.XS_PATH).set_index("segment_id")
    final = pd.read_parquet(c08.FINAL_PATH, columns=c08.FINAL_COLS).set_index("segment_id")
    j = gpd.read_parquet(c08.JUNCTIONS_PATH)
    chain = c08.Chain(fac[["cat_final", "dtv_official", "cycle_cat_final", "cyc_peak_h_dir", "cyc_peak_h"]], final, xs, j,
                      load_rules())
    return chain, fac, xs, j


def test_rerun_reproduces_stored_stages(chain_and_stored):
    chain, fac, xs, j = chain_and_stored
    res = chain.run(load_cycling_rules(), load_design_rules())
    xs = xs.reindex(chain.fac.index)
    assert (res["fac"]["cycle_facility_soll"].fillna("-") == fac["cycle_facility_soll"].fillna("-")).all()
    assert (res["profile"]["facility"].fillna("-") == xs["cycle_facility_final"].fillna("-")).all()
    assert (res["profile"]["lanes"].fillna("-") == xs["lanes_per_dir_soll"].fillna("-")).all()
    assert (res["profile"]["fit"].fillna("-") == xs["fit_class"].fillna("-")).all()
    assert (res["junction"].fillna("-").to_numpy() == j["junction_type_soll"].fillna("-").to_numpy()).all()


@pytest.mark.skipif(not c08.OUT_PATH.exists(), reason="run `make export-cycling` first")
def test_validation_output_covers_every_segment_and_junction(chain_and_stored):
    chain, _, _, j = chain_and_stored
    out = pd.read_parquet(c08.OUT_PATH)
    seg = out[out["kind"] == "segment"]
    jct = out[out["kind"] == "junction"]
    assert set(seg["id"]) == set(chain.fac.index)
    assert set(jct["id"]) == set(j["node_id"].astype(str))
    assert (seg["facility_changes"] <= seg["n_runs"]).all() and (jct["type_changes"] <= jct["n_runs"]).all()
