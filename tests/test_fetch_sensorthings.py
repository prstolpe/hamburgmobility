"""SensorThings counters (prompts/14): stations with their daily datastream and daily counts of one year."""

import pytest

from pipeline.lib.http import FetchError
from pipeline.lib.sensorthings import counter_stations, daily_counts, paged, year_window
from tests.fakes import FakeResponse, FakeSession

BASE = "https://example.test/v1.1"
SERVICE = "HH_STA_Demo"
LAYER = "Anzahl_Fahrraeder_Zaehlstelle_1-Tag"


def _thing(i: int, layer: str = LAYER) -> dict:
    return {"@iot.id": i, "name": f"Verkehrszählstelle {i}",
            "properties": {"art": "Zählstelle", "assetID": str(i), "richtung": "Keine Richtung"},
            "Locations": [{"location": {"type": "Point", "coordinates": [10.0 + i / 100, 53.55]}}],
            "Datastreams": [{"@iot.id": 1000 + i, "name": f"Fahrrad-Aufkommen {i}",
                             "properties": {"layerName": layer, "direction": "0"}}]}


def _paging_handler(items: list, page_size: int = 2, count: int | None = None):
    count = len(items) if count is None else count

    def handler(url, params):
        skip = int(url.split("$skip=")[1]) if "$skip=" in url else 0
        page = {"@iot.count": count, "value": items[skip:skip + page_size]}
        if skip + page_size < len(items):
            page["@iot.nextLink"] = f"{BASE}/Things?$skip={skip + page_size}"
        return FakeResponse(payload=page)

    return handler


def test_paged_follows_next_links():
    session = FakeSession(_paging_handler(list(range(5))))
    assert paged(session, f"{BASE}/Things", {"$count": "true"}) == [0, 1, 2, 3, 4]
    assert len(session.calls) == 3


def test_paged_count_mismatch_raises():
    session = FakeSession(_paging_handler(list(range(3)), count=4))
    with pytest.raises(FetchError, match="@iot.count"):
        paged(session, f"{BASE}/Things", {"$count": "true"})


def test_counter_stations_filter_and_fields():
    session = FakeSession(_paging_handler([_thing(1), _thing(2)]))
    gdf = counter_stations(session, BASE, SERVICE, LAYER)
    url, params = session.calls[0]
    assert url == f"{BASE}/Things"
    assert f"properties/serviceName eq '{SERVICE}'" in params["$filter"]
    assert f"properties/layerName eq '{LAYER}'" in params["$filter"]
    assert list(gdf["datastream_id"]) == [1001, 1002]
    assert list(gdf["asset_id"]) == ["1", "2"]
    assert gdf.crs.to_epsg() == 4326


def test_counter_stations_without_matching_datastream_raises():
    session = FakeSession(_paging_handler([_thing(1, layer="other")]))
    with pytest.raises(FetchError, match="layerName"):
        counter_stations(session, BASE, SERVICE, LAYER)


def test_year_window_covers_local_days():
    start, end = year_window(2025)
    # Daily intervals start at local midnight (23:00Z in winter), so the first day starts on 31 Dec UTC.
    assert start == "2024-12-31T00:00:00Z"
    assert end == "2026-01-01T00:00:00Z"


def test_daily_counts_keep_local_dates_of_the_year():
    obs = [{"phenomenonTime": "2024-12-30T23:00:00Z/2024-12-31T22:59:59Z", "result": 1},
           {"phenomenonTime": "2024-12-31T23:00:00Z/2025-01-01T22:59:59Z", "result": 635},
           {"phenomenonTime": "2025-06-30T22:00:00Z/2025-07-01T21:59:59Z", "result": 900},
           {"phenomenonTime": "2025-12-31T23:00:00Z/2026-01-01T22:59:59Z", "result": 2}]
    session = FakeSession(_paging_handler(obs, page_size=10))
    df = daily_counts(session, BASE, 1001, 2025)
    assert [str(d) for d in df["date"]] == ["2025-01-01", "2025-07-01"]
    assert list(df["count"]) == [635, 900]
    params = session.calls[0][1]
    assert "phenomenonTime ge 2024-12-31T00:00:00Z" in params["$filter"]
