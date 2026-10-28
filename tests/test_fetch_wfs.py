import pytest
import requests

from pipeline.lib.http import FetchError
from pipeline.lib.wfs import capabilities, get_features, hits
from tests.fakes import FakeResponse, FakeSession, point_feature

URL = "https://example.test/wfs"
BBOX = (560000.0, 5935000.0, 562000.0, 5937000.0)

CAPS = """<?xml version="1.0"?>
<wfs:WFS_Capabilities xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:ows="http://www.opengis.net/ows/1.1" version="2.0.0">
  <ows:ServiceIdentification><ows:Fees>Datenlizenz Deutschland Namensnennung 2.0</ows:Fees></ows:ServiceIdentification>
  <ows:OperationsMetadata>
    <ows:Operation name="GetFeature">
      <ows:Parameter name="outputFormat"><ows:AllowedValues><ows:Value>application/geo+json</ows:Value></ows:AllowedValues></ows:Parameter>
    </ows:Operation>
    <ows:Constraint name="ImplementsResultPaging"><ows:NoValues/><ows:DefaultValue>{paging}</ows:DefaultValue></ows:Constraint>
    <ows:Constraint name="CountDefault"><ows:NoValues/><ows:DefaultValue>{count_default}</ows:DefaultValue></ows:Constraint>
  </ows:OperationsMetadata>
  <wfs:FeatureTypeList>
    <wfs:FeatureType><wfs:Name>de.hh.up:layer_a</wfs:Name><wfs:Title>Layer A</wfs:Title></wfs:FeatureType>
    <wfs:FeatureType><wfs:Name>de.hh.up:layer_b</wfs:Name><wfs:Title>Layer B</wfs:Title></wfs:FeatureType>
  </wfs:FeatureTypeList>
</wfs:WFS_Capabilities>"""

HITS = '<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" numberMatched="{n}" numberReturned="0"/>'

INSIDE = [point_feature(560100.0 + i, 5935100.0, id=i) for i in range(5)]


def _wfs_server(features, total=None):
    """Fake WFS: answers hits and GetFeature with optional STARTINDEX/COUNT paging."""
    total = len(features) if total is None else total

    def handler(url, params):
        if params.get("RESULTTYPE") == "hits":
            return FakeResponse(text=HITS.format(n=total))
        start = int(params.get("STARTINDEX", 0))
        count = int(params.get("COUNT", len(features)))
        return FakeResponse(payload={"type": "FeatureCollection", "features": features[start:start + count]})

    return handler


def test_capabilities_parsed():
    session = FakeSession(lambda u, p: FakeResponse(text=CAPS.format(paging="FALSE", count_default=1000000)))
    caps = capabilities(session, URL)
    assert caps.typenames == ["de.hh.up:layer_a", "de.hh.up:layer_b"]
    assert caps.titles["de.hh.up:layer_a"] == "Layer A"
    assert caps.paging is False
    assert caps.count_default == 1000000
    assert "application/geo+json" in caps.output_formats
    assert "Namensnennung" in caps.fees


def test_hits():
    session = FakeSession(_wfs_server(INSIDE))
    assert hits(session, URL, "de.hh.up:layer_a", BBOX) == 5
    assert session.calls[0][1]["RESULTTYPE"] == "hits"


def test_paging_uses_startindex():
    session = FakeSession(_wfs_server(INSIDE))
    gdf = get_features(session, URL, "de.hh.up:layer_a", BBOX, expected=5, paging=True, page_size=2)
    assert len(gdf) == 5
    starts = [int(p["STARTINDEX"]) for _, p in session.calls]
    assert starts == [0, 2, 4]
    assert gdf.crs.to_epsg() == 25832


def test_without_paging_single_request():
    session = FakeSession(_wfs_server(INSIDE))
    gdf = get_features(session, URL, "de.hh.up:layer_a", BBOX, expected=5, paging=False)
    assert len(gdf) == 5
    assert len(session.calls) == 1
    assert "STARTINDEX" not in session.calls[0][1]


def test_without_paging_too_many_features():
    session = FakeSession(_wfs_server(INSIDE))
    with pytest.raises(FetchError, match="CountDefault"):
        get_features(session, URL, "de.hh.up:layer_a", BBOX, expected=5, paging=False, count_default=3)


def test_count_mismatch_raises():
    session = FakeSession(_wfs_server(INSIDE[:4]))
    with pytest.raises(FetchError, match="expected 5"):
        get_features(session, URL, "de.hh.up:layer_a", BBOX, expected=5, paging=False)


def test_features_outside_bbox_raise():
    # Swapped axes put the features far away from the requested bbox.
    swapped = [point_feature(5935100.0, 560100.0 + i) for i in range(2)]
    session = FakeSession(_wfs_server(swapped))
    with pytest.raises(FetchError, match="outside"):
        get_features(session, URL, "de.hh.up:layer_a", BBOX, expected=2, paging=False)


@pytest.mark.parametrize(
    "result",
    [FakeResponse(status_code=404, text="not found"), requests.ConnectionError("no route")],
)
def test_unreachable_endpoint_raises(result):
    session = FakeSession(lambda u, p: result)
    with pytest.raises(FetchError):
        capabilities(session, URL)
    assert len(session.calls) == 1  # no other URL tried


def test_hits_without_bbox_counts_whole_service():
    session = FakeSession(_wfs_server(INSIDE, total=15))
    assert hits(session, URL, "de.hh.up:layer_a", None) == 15
    assert "BBOX" not in session.calls[0][1]
