"""Grid cells from centre coordinates (pipeline/lib/grid.py, Zensus 2022 100-m grid)."""

import io
import zipfile

import pandas as pd
import pytest
from shapely.geometry import box

from pipeline.lib.grid import cells_from_centres, read_grid_zip

SPEC = {"member": "grid.csv", "separator": ";", "x": "x_mp_100m", "y": "y_mp_100m", "value": "Einwohner",
        "crs": "EPSG:3035", "cell_m": 100}
CSV = "GITTER_ID_100m;x_mp_100m;y_mp_100m;Einwohner\na;4321050;3381050;12\nb;4321150;3381050;3\nc;4500050;3500050;7\n"


def test_cells_from_centres_are_squares():
    df = pd.DataFrame({"x": [50.0], "y": [150.0], "v": [4]})
    cells = cells_from_centres(df, "x", "y", "v", cell_m=100, crs="EPSG:3035")
    assert cells.geometry.iloc[0].equals(box(0, 100, 100, 200))
    assert cells["population"].iloc[0] == 4


def test_read_grid_zip_clips_to_area(tmp_path):
    path = tmp_path / "g.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("grid.csv", CSV)
    area_3035 = box(4321000, 3381000, 4321100, 3381100)  # contains cell a, touches b
    cells = read_grid_zip(path, SPEC, area_3035)
    assert sorted(cells["population"]) == [3, 12]
    assert cells.crs == "EPSG:3035"


def test_read_grid_zip_rejects_non_numeric(tmp_path):
    path = tmp_path / "g.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("grid.csv", CSV.replace(";12\n", ";–\n"))
    with pytest.raises(ValueError, match="Einwohner"):
        read_grid_zip(path, SPEC, box(4321000, 3381000, 4321100, 3381100))
