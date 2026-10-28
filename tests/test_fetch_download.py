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


# --- several files per source (Unfallatlas, one ZIP per year) ---------------------------------

BASE_URL = "https://example.test/unfallatlas/"
ACC_HEADER = "OID_;ULAND;UJAHR;UKATEGORIE;IstRad;IstFuss;LINREFX;LINREFY"
POINTS = {"member_suffixes": [".csv", ".txt"], "separator": ";", "decimal": ",", "encoding": "utf-8-sig",
          "x": "LINREFX", "y": "LINREFY", "crs": "EPSG:25832", "land_column": "ULAND", "land": "02",
          "year": "UJAHR", "category": "UKATEGORIE", "severe_or_fatal": ["1", "2"], "pedestrian": "IstFuss",
          "cyclist": "IstRad", "flag_true": "1"}


def _acc_zip(year: int, n_hh: int) -> bytes:
    rows = [f"{i};02;{year};3;1;0;565000,0;5935000,0" for i in range(n_hh)] + [f"99;01;{year};3;1;0;1,0;2,0"]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(f"csv/Unfallorte{year}_LinRef.csv", "\n".join([ACC_HEADER, *rows]) + "\n")
    return buf.getvalue()


def _acc_src():
    return {"title": "Unfallatlas", "url": BASE_URL, "license": "dl-de/by-2.0",
            "fetch": {"download": "zip", "files": {2021: "U2021.zip", 2022: "U2022.zip"}, "points": POINTS}}


def _acc_handler(url, params):
    return ZipResponse(_acc_zip(2021, 3) if url.endswith("U2021.zip") else _acc_zip(2022, 0))


def test_download_several_files_with_coverage(repo):
    session = FakeSession(_acc_handler)
    result = s01.fetch_download(session, "accidents", _acc_src(), _area(), {"sources": {}}, refresh=False)
    assert result.status == "ok"
    assert [u for u, _ in session.calls] == [BASE_URL + "U2021.zip", BASE_URL + "U2022.zip"]
    assert [f["layer"] for f in result.files] == ["zip_2021", "zip_2022"]
    assert all(f["path"].startswith("data/raw/accidents/") for f in result.files)
    # Hamburg records per year; a year without records is reported as such, no point layer is written
    assert result.listing == {"2021": "3 Unfälle Hamburg", "2022": "keine Unfälle Hamburg"}
    assert "2022" in result.note
    assert not list((repo / "data" / "raw").glob("accidents__*.parquet"))


def test_download_several_files_reused(repo):
    session = FakeSession(_acc_handler)
    first = s01.fetch_download(session, "accidents", _acc_src(), _area(), {"sources": {}}, refresh=False)
    manifest = {"sources": {"accidents": {"files": first.files, "retrieved_at": "2026-10-28T00:00:00+00:00"}}}
    second = s01.fetch_download(session, "accidents", _acc_src(), _area(), manifest, refresh=False)
    assert len(session.calls) == 2
    assert second.files == first.files


def test_download_several_files_error(repo):
    session = FakeSession(lambda url, params: FetchError(f"{url}: HTTP 404") if "2022" in url
                          else ZipResponse(_acc_zip(2021, 1)))
    result = s01.fetch_download(session, "accidents", _acc_src(), _area(), {"sources": {}}, refresh=False)
    assert result.status == "fehler" and "U2022.zip" in result.error
