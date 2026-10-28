import geopandas as gpd
import pytest
from shapely.geometry import Point, box

from pipeline.lib.boundary import BoundaryError, buffered_area, select_district

# Bezirk (large) and Stadtteil (small) with the same name, as in Hamburg.
CANDIDATES = gpd.GeoDataFrame(
    {"name": ["Eimsbüttel", "Eimsbüttel", "Altona"], "admin_level": ["9", "10", "9"]},
    geometry=[box(0, 0, 4000, 4000), box(1000, 1000, 2000, 2000), box(5000, 0, 9000, 4000)],
    crs="EPSG:25832",
)


def test_ambiguous_name_without_admin_level_raises():
    with pytest.raises(BoundaryError, match="admin_level"):
        select_district(CANDIDATES, "Eimsbüttel", None)


def test_select_by_admin_level():
    district = select_district(CANDIDATES, "Eimsbüttel", 9)
    assert len(district) == 1
    assert district.area.iloc[0] == pytest.approx(16_000_000)


def test_no_match_raises():
    with pytest.raises(BoundaryError):
        select_district(CANDIDATES, "Eimsbüttel", 8)


def test_buffer_is_500_m():
    district = select_district(CANDIDATES, "Eimsbüttel", 9)
    area = buffered_area(district, 500)
    assert area.contains(Point(4499, 2000))
    assert not area.contains(Point(4501, 2000))
