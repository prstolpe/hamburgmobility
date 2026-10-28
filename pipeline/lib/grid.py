"""Statistical grid cells (Zensus 2022) from centre coordinates."""

import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely


def cells_from_centres(df: pd.DataFrame, x: str, y: str, value: str, cell_m: float, crs: str) -> gpd.GeoDataFrame:
    """Square cells of side cell_m around the centre coordinates; value goes to column 'population'."""
    h = cell_m / 2
    xs, ys = df[x].to_numpy(dtype="float64"), df[y].to_numpy(dtype="float64")
    geoms = shapely.box(xs - h, ys - h, xs + h, ys + h)
    return gpd.GeoDataFrame({"population": df[value].to_numpy()}, geometry=geoms, crs=crs)


def read_grid_zip(path: str | Path, spec: dict, area) -> gpd.GeoDataFrame:
    """Cells of the CSV spec['member'] in the zip that intersect area (geometry in spec['crs']).

    Raises ValueError if a value in the area is not an integer (special characters are never guessed).
    """
    with zipfile.ZipFile(path) as z, z.open(spec["member"]) as f:
        df = pd.read_csv(f, sep=spec["separator"], usecols=[spec["x"], spec["y"], spec["value"]], dtype=str)
    h = spec["cell_m"] / 2
    minx, miny, maxx, maxy = area.bounds
    xs, ys = df[spec["x"]].astype(float), df[spec["y"]].astype(float)
    df = df[(xs + h >= minx) & (xs - h <= maxx) & (ys + h >= miny) & (ys - h <= maxy)]
    bad = df[~df[spec["value"]].str.fullmatch(r"\d+")]
    if len(bad):
        raise ValueError(f"{spec['member']}: {len(bad)} non-numeric values in column {spec['value']}, "
                         f"e.g. {bad[spec['value']].iloc[0]!r}")
    df = df.assign(**{spec["value"]: df[spec["value"]].astype(int)})
    cells = cells_from_centres(df, spec["x"], spec["y"], spec["value"], spec["cell_m"], spec["crs"])
    return cells[cells.intersects(area)].reset_index(drop=True)
