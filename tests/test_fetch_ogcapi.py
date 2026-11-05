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
