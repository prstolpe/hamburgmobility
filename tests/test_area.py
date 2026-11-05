import geopandas as gpd
import pytest
from shapely.geometry import Point, box

from pipeline.lib.area import AreaConfig, build_work_area, select_districts
from pipeline.lib.boundary import BoundaryError

# City (level 4) with two Bezirke (level 9), an island Stadtteil inside Mitte (level 10),
# a Stadtteil with a Bezirk name and a level-9 area outside the city (as Sahlenburg in the OSM extract).
BOUNDARIES = gpd.GeoDataFrame(
    {"name": ["Hamburg", "Eimsbüttel", "Hamburg-Mitte", "Neuwerk", "Eimsbüttel", "Sahlenburg"],
     "admin_level": ["4", "9", "9", "10", "10", "9"],
     "id": [1, 2, 3, 4, 5, 6]},
    geometry=[box(0, 0, 20000, 4000), box(0, 0, 4000, 4000),
              box(4000, 0, 20000, 4000), box(18000, 0, 20000, 4000),
              box(1000, 1000, 2000, 2000), box(30000, 0, 34000, 4000)],
    crs="EPSG:25832",
)


def cfg(districts="all", exclude=({"name": "Neuwerk", "admin_level": 10},), buffer_m=500.0):
    return AreaConfig(districts=districts, city_name="Hamburg", city_admin_level=4, district_admin_level=9,
                      exclude=list(exclude), buffer_m=buffer_m)


def test_all_means_level9_inside_the_city():
    d = select_districts(BOUNDARIES, cfg())
    assert sorted(d["name"]) == ["Eimsbüttel", "Hamburg-Mitte"]


def test_excluded_stadtteil_is_cut_out():
    d = select_districts(BOUNDARIES, cfg()).set_index("name")
    assert d.loc["Hamburg-Mitte"].geometry.area == pytest.approx(14000 * 4000)
    assert not d.loc["Hamburg-Mitte"].geometry.contains(Point(19000, 2000))


def test_list_selects_named_districts_only():
    d = select_districts(BOUNDARIES, cfg(districts=["Eimsbüttel"]))
    assert list(d["name"]) == ["Eimsbüttel"]
    assert d.area.iloc[0] == pytest.approx(16_000_000)


def test_eimsbuettel_only_matches_old_work_area():
    """Regression: districts: [Eimsbüttel] gives the pilot work area (district + 500 m)."""
    area = build_work_area(select_districts(BOUNDARIES, cfg(districts=["Eimsbüttel"])), 500)
    assert area.contains(Point(4499, 2000))
    assert not area.contains(Point(4501, 2000))


def test_unknown_district_raises():
    with pytest.raises(BoundaryError, match="Altona"):
        select_districts(BOUNDARIES, cfg(districts=["Altona"]))


def test_district_outside_city_raises():
    with pytest.raises(BoundaryError, match="Sahlenburg"):
        select_districts(BOUNDARIES, cfg(districts=["Sahlenburg"]))


def test_missing_exclusion_raises():
    with pytest.raises(BoundaryError, match="Scharhörn"):
        select_districts(BOUNDARIES, cfg(exclude=[{"name": "Scharhörn", "admin_level": 10}]))


def test_missing_city_raises():
    with pytest.raises(BoundaryError, match="Hamburg"):
        select_districts(BOUNDARIES[BOUNDARIES["admin_level"] != "4"], cfg())


def test_work_area_excludes_island_buffer():
    area = build_work_area(select_districts(BOUNDARIES, cfg()), 500)
    assert area.contains(Point(17499, 2000))
    assert not area.contains(Point(19000, 2000))


def test_detached_part_containing_excluded_stadtteil_is_dropped():
    """As in OSM: the Stadtteil Neuwerk is only the island, the Wattenmeer around it belongs to Mitte directly."""
    from shapely.geometry import MultiPolygon
    mitte = MultiPolygon([box(4000, 0, 20000, 4000), box(50000, 0, 70000, 20000)])
    b = BOUNDARIES.copy()
    b.loc[b["name"] == "Hamburg", "geometry"] = MultiPolygon([box(0, 0, 20000, 4000), box(50000, 0, 70000, 20000)])
    b.loc[b["name"] == "Hamburg-Mitte", "geometry"] = mitte
    b.loc[b["name"] == "Neuwerk", "geometry"] = box(60000, 5000, 62000, 7000)
    d = select_districts(b, cfg()).set_index("name")
    assert d.loc["Hamburg-Mitte"].geometry.area == pytest.approx(16000 * 4000)


def test_sample_by_district_is_proportional_and_reproducible():
    import pandas as pd
    from pipeline.lib.area import sample_by_district
    df = pd.DataFrame({"segment_id": [f"s{i:03d}" for i in range(100)],
                       "bezirk": ["A"] * 70 + ["B"] * 25 + ["C"] * 5})
    s = sample_by_district(df, 10, seed=42)
    assert len(s) == 10
    # one per Bezirk, the other 7 in proportion to the remaining rows (69:24:4)
    assert s["bezirk"].value_counts().to_dict() == {"A": 6, "B": 3, "C": 1}
    assert list(s["segment_id"]) == list(sample_by_district(df, 10, seed=42)["segment_id"])


def test_sample_by_district_small_input():
    import pandas as pd
    from pipeline.lib.area import sample_by_district
    df = pd.DataFrame({"segment_id": ["a", "b"], "bezirk": ["A", "B"]})
    assert sorted(sample_by_district(df, 30, seed=1)["segment_id"]) == ["a", "b"]


def test_rural_stadtteile_are_cut_from_classification_area_but_not_from_fetch_area():
    from pipeline.lib.area import classification_area, select_rural
    b = gpd.pd.concat([BOUNDARIES, gpd.GeoDataFrame(
        {"name": ["Kirchwerder"], "admin_level": ["10"], "id": [7]},
        geometry=[box(8000, 0, 12000, 4000)], crs="EPSG:25832")], ignore_index=True)
    c = AreaConfig(districts="all", city_name="Hamburg", city_admin_level=4, district_admin_level=9,
                   exclude=[{"name": "Neuwerk", "admin_level": 10}], buffer_m=500.0,
                   rural_admin_level=10, rural_stadtteile=["Kirchwerder"])
    districts, rural = select_districts(b, c), select_rural(b, c)
    assert list(rural["name"]) == ["Kirchwerder"]
    area = classification_area(districts, rural, c.buffer_m)
    full = build_work_area(districts, c.buffer_m)
    assert full.contains(Point(10000, 2000)) and not area.contains(Point(10000, 2000))
    assert area.contains(Point(7000, 2000))


def test_unknown_rural_stadtteil_raises():
    from pipeline.lib.area import select_rural
    c = AreaConfig(districts="all", city_name="Hamburg", city_admin_level=4, district_admin_level=9, exclude=[],
                   buffer_m=500.0, rural_admin_level=10, rural_stadtteile=["Kirchwerder"])
    with pytest.raises(BoundaryError, match="Kirchwerder"):
        select_rural(BOUNDARIES, c)
