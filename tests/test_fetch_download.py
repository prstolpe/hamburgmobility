"""File downloads in the fetch stage (GTFS zip, Zensus grid zip), no network."""

import io
import zipfile

import geopandas as gpd
import pytest
from shapely.geometry import box

import pipeline.lib.manifest as manifest_mod
import pipeline.s01_fetch as s01
from pipeline.lib.http import FetchError
from tests.fakes import FakeResponse, FakeSession

URL = "https://example.test/files/Grid.zip"
CSV = "GITTER_ID_100m;x_mp_100m;y_mp_100m;Einwohner\na;4321050;3381050;12\n"
GRID = {"member": "grid.csv", "separator": ";", "x": "x_mp_100m", "y": "y_mp_100m", "value": "Einwohner",
        "crs": "EPSG:3035", "cell_m": 100}


class ZipResponse(FakeResponse):
    def __init__(self, data: bytes):
        super().__init__()
        self.content = data

    def iter_content(self, chunk_size=1):
        yield self.content


def _zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("grid.csv", CSV)
    return buf.getvalue()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(s01, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(s01, "RAW_DIR", tmp_path / "data" / "raw")
    monkeypatch.setattr(manifest_mod, "REPO_ROOT", tmp_path)
    return tmp_path


def _area():
    cell = gpd.GeoSeries([box(4321000, 3381000, 4321100, 3381100)], crs="EPSG:3035").to_crs("EPSG:25832")
    return cell.iloc[0].buffer(10)


def _src(grid=None):
    fetch = {"download": "zip", **({"grid": grid} if grid else {})}
    return {"title": "Grid", "url": URL, "license": "dl-de/by-2.0", "fetch": fetch}


def test_download_zip_and_grid_layer(repo):
    session = FakeSession(lambda url, params: ZipResponse(_zip()))
    result = s01.fetch_download(session, "population_grid", _src(GRID), _area(), {"sources": {}}, refresh=False)
    assert result.status == "ok"
    assert [f["layer"] for f in result.files] == ["zip", "100m"]
    assert (repo / "data" / "raw" / "population_grid" / "Grid.zip").exists()
    cells = gpd.read_parquet(repo / result.files[1]["path"])
    assert cells.crs == "EPSG:25832" and list(cells["population"]) == [12]


def test_download_reused_when_hash_matches(repo):
    session = FakeSession(lambda url, params: ZipResponse(_zip()))
    first = s01.fetch_download(session, "gtfs", _src(), _area(), {"sources": {}}, refresh=False)
    manifest = {"sources": {"gtfs": {"files": first.files, "retrieved_at": "2026-10-28T00:00:00+00:00"}}}
    second = s01.fetch_download(session, "gtfs", _src(), _area(), manifest, refresh=False)
    assert len(session.calls) == 1
    assert second.note == "lokale Datei wiederverwendet"


def test_download_error_is_reported(repo):
    session = FakeSession(lambda url, params: FetchError(f"{url}: HTTP 404"))
    result = s01.fetch_download(session, "gtfs", _src(), _area(), {"sources": {}}, refresh=False)
    assert result.status == "fehler" and "404" in result.error
