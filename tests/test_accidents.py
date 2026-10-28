"""Unfallatlas reader and aggregation per segment (pipeline/lib/accidents.py, rule P-RISK-01)."""

import io
import zipfile

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import LineString

from pipeline.lib import accidents as acc

SPEC = {"member_suffixes": [".csv", ".txt"], "separator": ";", "decimal": ",", "encoding": "utf-8-sig",
        "x": "LINREFX", "y": "LINREFY", "crs": "EPSG:25832", "land_column": "ULAND", "land": "02",
        "year": "UJAHR", "category": "UKATEGORIE", "severe_or_fatal": ["1", "2"], "pedestrian": "IstFuss",
        "cyclist": "IstRad", "flag_true": "1"}

HEADER = "OID_;ULAND;UJAHR;UKATEGORIE;IstRad;IstFuss;IstPKW;LINREFX;LINREFY"
ROWS = [
    "1;02;2024;3;1;0;1;565005,0;5935001,0",    # cyclist, slight, 1 m from segment a
    "2;02;2024;2;0;1;1;565050,5;5934998,0",    # pedestrian, severe, 2 m from segment a
    "3;02;2024;3;0;0;1;565020,0;5935000,0",    # car only: not counted
    "4;02;2024;1;1;1;0;565100,0;5935110,0",    # both, fatal, near segment b
    "5;02;2024;3;1;0;0;565500,0;5935500,0",    # cyclist, far from all segments (> snap)
    "6;01;2024;3;1;0;0;565010,0;5935000,0",    # Schleswig-Holstein: dropped
]


def _zip(member="csv/Unfallorte2024_LinRef.csv", rows=ROWS, header=HEADER) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("csv/schema.ini", "[x]\n")
        z.writestr(member, "﻿" + "\n".join([header, *rows]) + "\n")
    return buf.getvalue()


@pytest.fixture
def zpath(tmp_path):
    p = tmp_path / "Unfallorte2024_EPSG25832_CSV.zip"
    p.write_bytes(_zip())
    return p


def _segments():
    return gpd.GeoSeries([LineString([(565000, 5935000), (565100, 5935000)]),       # a, 100 m
                          LineString([(565100, 5935000), (565100, 5935200)])],      # b, 200 m
                         crs="EPSG:25832", index=[10, 11])


def test_read_keeps_hamburg_only_and_parses_decimal_comma(zpath):
    crashes = acc.read_accidents_zip(zpath, SPEC)
    assert len(crashes) == 5
    assert crashes.crs == "EPSG:25832"
    assert crashes.geometry.iloc[0].x == pytest.approx(565005.0)
    assert set(crashes.columns) == {"year", "severe_or_fatal", "pedestrian", "cyclist", "geometry"}
    assert list(crashes["year"].unique()) == [2024]


def test_read_finds_txt_member(tmp_path):
    p = tmp_path / "Unfallorte2021_EPSG25832_CSV.zip"
    p.write_bytes(_zip(member="Unfallorte2021_EPSG25832_CSV/Unfallorte_2021_LinRef.txt"))
    assert len(acc.read_accidents_zip(p, SPEC)) == 5


def test_read_fails_on_missing_column(tmp_path):
    p = tmp_path / "x.zip"
    p.write_bytes(_zip(header=HEADER.replace("IstFuss", "IstFussg")))
    with pytest.raises(ValueError, match="IstFuss"):
        acc.read_accidents_zip(p, SPEC)


def test_read_fails_without_single_member(tmp_path):
    p = tmp_path / "x.zip"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("a.csv", HEADER)
        z.writestr("b.csv", HEADER)
    p.write_bytes(buf.getvalue())
    with pytest.raises(ValueError, match="member"):
        acc.read_accidents_zip(p, SPEC)


def test_aggregate_per_segment(zpath):
    crashes = acc.read_accidents_zip(zpath, SPEC)
    agg = acc.aggregate_crashes(_segments(), crashes, snap_m=15, severe_weight=3)
    assert list(agg.index) == [10, 11]
    a, b = agg.loc[10], agg.loc[11]
    assert (a["crashes_ped_cyc"], a["crashes_cyc"], a["crashes_ped"], a["crashes_severe_fatal"]) == (2, 1, 1, 1)
    assert a["crash_weighted"] == 1 + 3
    assert (b["crashes_ped_cyc"], b["crashes_cyc"], b["crashes_ped"], b["crashes_severe_fatal"]) == (1, 1, 1, 1)
    assert b["crash_weighted"] == 3


def test_aggregate_output_has_no_single_crash_data(zpath):
    crashes = acc.read_accidents_zip(zpath, SPEC)
    agg = acc.aggregate_crashes(_segments(), crashes, snap_m=15, severe_weight=3)
    assert not isinstance(agg, gpd.GeoDataFrame)
    assert set(agg.columns) == set(acc.AGG_COLUMNS)
    assert all(pd.api.types.is_integer_dtype(agg[c]) or pd.api.types.is_float_dtype(agg[c]) for c in agg.columns)


def test_unassigned_crashes_are_counted(zpath):
    crashes = acc.read_accidents_zip(zpath, SPEC)
    stats = acc.assignment_stats(_segments(), crashes, snap_m=15)
    assert stats == {"ped_cyc": 4, "assigned": 3, "unassigned": 1}


def test_empty_crashes():
    empty = gpd.GeoDataFrame({"year": [], "severe_or_fatal": [], "pedestrian": [], "cyclist": []},
                             geometry=[], crs="EPSG:25832")
    agg = acc.aggregate_crashes(_segments(), empty, snap_m=15, severe_weight=3)
    assert (agg == 0).all().all()


def test_coverage_by_year():
    crashes = gpd.GeoDataFrame({"year": [2021, 2021, 2023], "severe_or_fatal": [False] * 3,
                                "pedestrian": [True] * 3, "cyclist": [False] * 3},
                               geometry=gpd.points_from_xy([0, 1, 2], [0, 1, 2]), crs="EPSG:25832")
    cov = acc.coverage(crashes, [2021, 2022, 2023])
    assert cov == {2021: 2, 2022: 0, 2023: 1}
