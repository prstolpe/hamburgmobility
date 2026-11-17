"""Trees and parking per target cross section (prompts/26 Teil 2): synthetic cases for pipeline/lib/trees_parking.py."""

import pytest
from shapely.geometry import LineString, Point, box

from pipeline.lib import trees_parking as tp
from pipeline.lib.features import parking_by_side
from pipeline.lib.rules import load_design_rules


@pytest.fixture(scope="module")
def p() -> tp.Params:
    return tp.Params.from_rules(load_design_rules())


def test_params_from_rules(p):
    assert p.kerb_m["parallel"] == 5.2 and p.setback_m == 5 and p.setback_cycle_track_m == 8
    assert "carriageway" in p.affected and "tree_strip" in p.keep and "sidewalk" in p.keep  # 2026-11-17
    assert not p.extrapolate  # TP-P-04 inactive


def test_parking_by_side_new_and_old_scheme():
    assert parking_by_side({"parking:both": "lane", "parking:both:orientation": "parallel"}) == \
        {"left": ("lane", "parallel"), "right": ("lane", "parallel")}
    assert parking_by_side({"parking:right": "no", "parking:left": "street_side"}) == \
        {"left": ("street_side", None), "right": ("no", None)}
    assert parking_by_side({"parking:lane:right": "diagonal", "parking:lane:right:diagonal": "on_kerb"}) == \
        {"right": ("on_kerb", "diagonal")}
    assert parking_by_side({"highway": "residential"}) == {}  # untagged = unknown, not "no"


def test_signed_offset_left_positive():
    line = LineString([(0, 0), (100, 0)])
    assert tp.signed_offset(line, Point(50, 4)) == pytest.approx((50, 4))
    assert tp.signed_offset(line, Point(50, -3))[1] == pytest.approx(-3)


def test_usable_kerb_setbacks(p):
    # both ends at junctions: 5 + 5; with a cycle track the end before the junction (right side: end) is 8
    assert tp.usable_kerb_m(100, True, True, False, "right", p) == 90
    assert tp.usable_kerb_m(100, True, True, True, "right", p) == 87
    assert tp.usable_kerb_m(100, True, False, True, "left", p) == 92   # left side drives end -> start
    assert tp.usable_kerb_m(100, False, False, True, "left", p) == 100
    assert tp.usable_kerb_m(6, True, True, False, "right", p) == 0


def test_osm_spaces_missing_is_not_zero(p):
    assert tp.osm_spaces(None, None, 52, 1.0, p) is None
    assert tp.osm_spaces("separate", None, 52, 1.0, p) is None
    assert tp.osm_spaces("no", None, 52, 1.0, p) == 0
    assert tp.osm_spaces("lane", None, 52, 1.0, p) == pytest.approx(10)
    assert tp.osm_spaces("lane", "perpendicular", 50, 0.8, p) == pytest.approx(16)


def test_official_space_count(p):
    assert tp.official_space_count(box(0, 0, 5.2, 2.1), "längs", p) == 1
    assert tp.official_space_count(box(0, 0, 2.5, 5.1), "quer", p) == 1
    assert tp.official_space_count(box(0, 0, 52, 2.1), "längs", p) == pytest.approx(52 * 2.1 / 10.9)
    assert tp.official_space_count(box(0, 0, 25.5, 5.0), "quer", p) == pytest.approx(10)
    # a single diagonal space drawn as a long thin parallelogram-like box must not count twice (QA 2026-11-16)
    assert tp.official_space_count(box(0, 0, 8.4, 2.0), "schräg", p) == pytest.approx(1, abs=0.15)


ELEMENTS = [  # left outer -> inner, centre, right inner -> outer (as in profile_elements)
    {"element": "sidewalk", "width_m": 3.0, "side": "left"},
    {"element": "parking_parallel", "width_m": 2.0, "side": "left"},
    {"element": "carriageway", "width_m": 5.0, "side": "centre"},
    {"element": "cycle_track", "width_m": 2.0, "side": "right"},
    {"element": "sidewalk", "width_m": 3.0, "side": "right"},
]


def test_bands_layout():
    bs = tp.bands(ELEMENTS, available=19.0)
    assert tp.element_at(0, bs) == "carriageway"
    assert tp.element_at(3.5, bs) == "parking_parallel"
    assert tp.element_at(6.0, bs) == "sidewalk"
    assert tp.element_at(-3.5, bs) == "cycle_track"
    assert tp.element_at(-6.0, bs) == "sidewalk"
    assert tp.element_at(9.3, bs) == "rest"        # 4 m unused width, 2 m per side
    mirrored = tp.bands(ELEMENTS, available=19.0, mirrored=True)
    assert tp.element_at(3.5, mirrored) == "cycle_track"


def test_classify_tree(p):
    # in the middle of the carriageway: affected in every variant
    assert tp.classify_tree(0.0, ELEMENTS, 19.0, p)[:3] == (True, True, 1.0)
    # far outside: kept in every variant
    assert tp.classify_tree(11.0, ELEMENTS, 19.0, p)[:2] == (False, False)
    # parking row on one side, cycle track on the other: mirroring makes it possibly affected, not surely
    assert tp.classify_tree(3.5, ELEMENTS, 19.0, p)[:3] == (False, True, 0.5)


def test_target_parking_as_ist(p):
    usable = {"left": 52.0, "right": 52.0}
    # ETW30 (as_ist): today's spaces stay, capped by what fits parallel (52 / 5.2 = 10)
    assert tp.target_parking({"left": 6.0, "right": 14.0}, usable, ELEMENTS, 1.0, p, "ETW30") == (16.0, 16.0)
    lo, hi = tp.target_parking({"left": None, "right": 4.0}, usable, ELEMENTS, 1.0, p, "ETW30")
    assert lo is None and hi == pytest.approx(14.0)
    # degrade step D1 removes parking
    assert tp.target_parking({"left": 6.0, "right": 4.0}, usable, ELEMENTS, 1.0, p, "ETW30", parking_removed=True) == (0.0, 0.0)


def test_target_parking_none_and_list(p):
    usable = {"left": 52.0, "right": 52.0}
    assert tp.target_parking({"left": 6.0, "right": 4.0}, usable, ELEMENTS, 1.0, p, "GOW50") == (0.0, 0.0)
    # GOW30 (list of positions): only sides with a parking row; one row -> both assignments 4..6
    assert tp.target_parking({"left": 6.0, "right": 4.0}, usable, ELEMENTS, 1.0, p, "GOW30") == (4.0, 6.0)
    no_row = [e for e in ELEMENTS if e["element"] != "parking_parallel"]
    assert tp.target_parking({"left": 6.0, "right": 4.0}, usable, no_row, 1.0, p, "GOW30") == (0.0, 0.0)
    # position unknown today (official spaces, no OSM tag): 0 up to today's spaces
    assert tp.target_parking({"left": 6.0, "right": 4.0}, usable, no_row, 1.0, p, "GOW30",
                             position_known={"left": False, "right": False}) == (0.0, 10.0)


def test_new_trees(p):
    strip = ELEMENTS + [{"element": "tree_strip", "width_m": 2.0, "side": "right"}]
    assert tp.new_trees({"left": 60.0, "right": 60.0}, strip, 2, p) == pytest.approx(3.0)
    assert tp.new_trees({"left": 60.0, "right": 60.0}, ELEMENTS, 0, p) == 0
