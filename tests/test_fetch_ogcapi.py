import pytest

from pipeline.lib.http import FetchError
from pipeline.lib.ogcapi import collections, get_items
from tests.fakes import FakeResponse, FakeSession, point_feature

URL = "https://example.test/datasets/v1/demo"
BBOX = (560000.0, 5935000.0, 562000.0, 5937000.0)
FEATURES = [point_feature(560100.0 + i, 5935100.0, id=i) for i in range(5)]


def _api(features, page_size=2, matched=None):
    """Fake OGC API Features: pages via next links like api.hamburg.de."""
    matched = len(features) if matched is None else matched
    items_url = f"{URL}/collections/c1/items"

    def handler(url, params):
        if url == f"{URL}/collections":
            return FakeResponse(payload={"collections": [{"id": "c1", "title": "Collection 1"}]})
        offset = int(url.split("offset=")[1]) if "offset=" in url else 0
        page = features[offset:offset + page_size]
        links = [{"rel": "self", "href": url}]
        if offset + page_size < len(features):
            links.append({"rel": "next", "href": f"{items_url}?f=json&offset={offset + page_size}"})
        return FakeResponse(payload={
            "type": "FeatureCollection", "features": page, "links": links,
            "numberMatched": matched, "numberReturned": len(page),
        })

    return handler


def test_collections():
    session = FakeSession(_api(FEATURES))
    assert collections(session, URL) == [{"id": "c1", "title": "Collection 1"}]


def test_follows_next_links_until_last_page():
    session = FakeSession(_api(FEATURES, page_size=2))
    gdf = get_items(session, URL, "c1", BBOX)
    assert len(gdf) == 5
    assert len(session.calls) == 3
    first_params = session.calls[0][1]
    assert first_params["bbox"] == "560000.0,5935000.0,562000.0,5937000.0"
    assert first_params["crs"].endswith("/25832")
    assert gdf.crs.to_epsg() == 25832


def test_number_matched_mismatch_raises():
    session = FakeSession(_api(FEATURES, matched=7))
    with pytest.raises(FetchError, match="numberMatched"):
        get_items(session, URL, "c1", BBOX)


def test_http_error_raises():
    session = FakeSession(lambda u, p: FakeResponse(status_code=500, text="boom"))
    with pytest.raises(FetchError):
        get_items(session, URL, "c1", BBOX)


def test_truncated_page_raises():
    # api.hamburg.de sometimes sends HTTP 200 with a body cut off mid-feature.
    good = _api(FEATURES, page_size=2)

    def handler(url, params):
        if "offset=2" in url:
            return FakeResponse(text='{"type": "FeatureCollection", "features": [{"type": "Feat')
        return good(url, params)

    with pytest.raises(FetchError, match="invalid JSON"):
        get_items(FakeSession(handler), URL, "c1", BBOX)


def test_without_bbox_requests_whole_collection():
    from tests.fakes import FakeResponse, FakeSession, point_feature
    from pipeline.lib import ogcapi
    session = FakeSession(lambda url, params: FakeResponse(payload={
        "numberMatched": 1, "features": [point_feature(560500, 5935500)], "links": []}))
    gdf = ogcapi.get_items(session, "https://example.org/api", "jahr2025", None)
    assert len(gdf) == 1
    assert "bbox" not in session.calls[0][1] and "bbox-crs" not in session.calls[0][1]


# --- skip_broken: single records the server cannot serialise (api.hamburg.de dbradplus) ---------

MANY = [point_feature(560100.0 + i, 5935100.0, id=i) for i in range(23)]


def _broken_api(features, broken: set[int]):
    """Offset paging; a page that contains a broken record is cut off, the record alone gives HTTP 500."""
    items_url = f"{URL}/collections/c1/items"

    def handler(url, params):
        query = dict(p.split("=", 1) for p in url.split("?", 1)[1].split("&")) if "?" in url else {}
        query.update({k: str(v) for k, v in params.items()})
        offset, limit = int(query.get("offset", 0)), int(query.get("limit", 10))
        hit = [o for o in range(offset, min(offset + limit, len(features))) if o in broken]
        if hit and limit == 1:
            return FakeResponse(status_code=500, text="<html>HTTP Error 500</html>")
        if hit:
            return FakeResponse(text='{"type": "FeatureCollection", "features": [{"type": "Feat')
        page = features[offset:offset + limit]
        links = []
        if offset + limit < len(features):
            links.append({"rel": "next", "href": f"{items_url}?f=json&limit={limit}&offset={offset + limit}"})
        return FakeResponse(payload={"type": "FeatureCollection", "features": page, "links": links,
                                     "numberMatched": len(features), "numberReturned": len(page)})

    return handler


def test_skip_broken_skips_and_reports_single_records():
    from pipeline.lib.ogcapi import get_items_skipping_broken
    gdf, skipped = get_items_skipping_broken(FakeSession(_broken_api(MANY, {7, 15})), URL, "c1", limit=10)
    assert skipped == [7, 15]
    assert sorted(gdf["id"]) == [i for i in range(23) if i not in (7, 15)]


def test_skip_broken_without_broken_records_matches_get_items():
    from pipeline.lib.ogcapi import get_items_skipping_broken
    gdf, skipped = get_items_skipping_broken(FakeSession(_broken_api(MANY, set())), URL, "c1", limit=10)
    assert skipped == []
    assert sorted(gdf["id"]) == list(range(23))


def test_skip_broken_first_page_broken_still_reads_number_matched():
    from pipeline.lib.ogcapi import get_items_skipping_broken
    gdf, skipped = get_items_skipping_broken(FakeSession(_broken_api(MANY, {0})), URL, "c1", limit=10)
    assert skipped == [0] and len(gdf) == 22


def test_skip_broken_does_not_hide_a_dead_endpoint():
    from pipeline.lib.ogcapi import get_items_skipping_broken
    session = FakeSession(lambda u, p: FakeResponse(status_code=500, text="boom"))
    with pytest.raises(FetchError):
        get_items_skipping_broken(session, URL, "c1", limit=10)


def test_skip_broken_too_many_skipped_raises():
    from pipeline.lib.ogcapi import get_items_skipping_broken
    with pytest.raises(FetchError, match="broken records"):
        get_items_skipping_broken(FakeSession(_broken_api(MANY, set(range(0, 23, 2)))), URL, "c1",
                                  limit=10, max_skipped=3)


def test_plain_get_items_still_fails_on_broken_record():
    with pytest.raises(FetchError):
        get_items(FakeSession(_broken_api(MANY, {7})), URL, "c1", None, limit=10)
