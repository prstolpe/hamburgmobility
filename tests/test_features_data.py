"""Checks on the real data/interim/features.parquet (skipped until `make features` has run)."""

import pandas as pd
import pytest

from pipeline.lib.manifest import REPO_ROOT

CONFLATED = REPO_ROOT / "data" / "interim" / "segments_conflated.parquet"
FEATURES = REPO_ROOT / "data" / "interim" / "features.parquet"

pytestmark = pytest.mark.skipif(not FEATURES.exists(), reason="run `make features` first")

NORMS = ["betweenness_norm", "bus_trips_weekday_norm", "dtv_norm", "building_density_norm",
         "population_100m_norm", "sensitive_facilities_norm", "shop_frontage_share"]


@pytest.fixture(scope="module")
def out() -> pd.DataFrame:
    return pd.read_parquet(FEATURES)


def test_segment_ids_unchanged(out):
    ids = pd.read_parquet(CONFLATED, columns=["segment_id"])["segment_id"]
    assert list(out["segment_id"]) == list(ids)


def test_columns(out):
    expected = {"conn_score", "place_score", "conn_weight_available", "place_weight_available", "in_hvs",
                "schools_or_kitas_within_m", "separated_cycle_track_present", "cycle_lane_present", "lanes",
                "centre_line", "parking", "crossings_count", "traffic_calming_count", "surface", "speed_ist_kmh",
                "speed_sources_conflict", "access_motor_only", "pedestrian_zone", "in_cycle_network",
                "feature_trace"} | set(NORMS)
    assert expected <= set(out.columns)


@pytest.mark.parametrize("col", NORMS + ["conn_score", "place_score"])
def test_values_in_unit_interval(out, col):
    v = out[col].dropna()
    assert ((v >= 0) & (v <= 1)).all()


def test_features_only_in_work_area(out):
    assert out.loc[~out["conflated"], "conn_score"].isna().all()
    assert out.loc[out["conflated"], "conn_score"].notna().all()


def test_main_roads_have_higher_betweenness(out):
    area = out[out["conflated"]]
    main = area.loc[area["highway"].isin(["primary", "secondary"]), "betweenness_norm"].median()
    residential = area.loc[area["highway"] == "residential", "betweenness_norm"].median()
    assert main > residential


def test_zero_values_normalise_to_zero(out):
    # S-FEAT-01 ties = min (rules.yaml 0.5.0): no bus -> norm 0.
    area = out[out["conflated"]]
    no_bus = area["bus_trips_weekday"] == 0
    if no_bus.any():
        assert (area.loc[no_bus, "bus_trips_weekday_norm"] == 0).all()
