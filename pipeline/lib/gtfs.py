"""Minimal GTFS reader for bus trips per weekday (rule S-FEAT-08).

Uses only columns from the GTFS reference (calendar, calendar_dates, routes, trips, shapes).
"""

import datetime as dt
import io
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely

from pipeline.lib.crs import to_work_crs

TABLES = ("routes", "trips", "calendar", "calendar_dates", "shapes", "frequencies")
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
REPRESENTATIVE_WEEKDAYS = (1, 2, 3)  # Tuesday-Thursday (S-FEAT-08)


def load_feed(path: str | Path) -> dict[str, pd.DataFrame]:
    """Read the needed tables from a GTFS zip or folder; missing optional tables become empty frames."""
    path = Path(path)
    feed: dict[str, pd.DataFrame] = {}

    def read(name: str, data) -> pd.DataFrame:
        return pd.read_csv(data, dtype=str, keep_default_na=False, na_values=[""])

    if path.is_dir():
        for name in TABLES:
            f = path / f"{name}.txt"
            feed[name] = read(name, f) if f.exists() else pd.DataFrame()
    else:
        with zipfile.ZipFile(path) as z:
            names = {Path(n).name: n for n in z.namelist()}
            for name in TABLES:
                n = names.get(f"{name}.txt")
                feed[name] = read(name, io.BytesIO(z.read(n))) if n else pd.DataFrame()
    for name in ("routes", "trips"):
        if feed[name].empty:
            raise ValueError(f"GTFS {path}: {name}.txt missing")
    if not feed["frequencies"].empty:
        # Trips in frequencies.txt stand for many runs; counting rows would be wrong.
        raise ValueError(f"GTFS {path}: frequencies.txt is not empty; frequency-based trips are not supported")
    return feed


def _date(s: str) -> dt.date:
    return dt.datetime.strptime(s, "%Y%m%d").date()


def _validity(feed: dict) -> tuple[dt.date, dt.date]:
    dates = []
    if not feed["calendar"].empty:
        dates += [_date(s) for s in feed["calendar"]["start_date"]] + [_date(s) for s in feed["calendar"]["end_date"]]
    if not feed["calendar_dates"].empty:
        dates += [_date(s) for s in feed["calendar_dates"]["date"]]
    if not dates:
        raise ValueError("GTFS has neither calendar nor calendar_dates")
    return min(dates), max(dates)


def active_services(feed: dict, day: dt.date) -> set[str]:
    """service_ids running on day (calendar plus calendar_dates exceptions: 1 = added, 2 = removed)."""
    active: set[str] = set()
    cal = feed["calendar"]
    if not cal.empty:
        key = day.strftime("%Y%m%d")
        mask = (cal[WEEKDAYS[day.weekday()]] == "1") & (cal["start_date"] <= key) & (cal["end_date"] >= key)
        active = set(cal.loc[mask, "service_id"])
    cd = feed["calendar_dates"]
    if not cd.empty:
        today = cd[cd["date"] == day.strftime("%Y%m%d")]
        active |= set(today.loc[today["exception_type"] == "1", "service_id"])
        active -= set(today.loc[today["exception_type"] == "2", "service_id"])
    return active


def representative_weekday(feed: dict) -> dt.date:
    """Tuesday-Thursday in the feed validity with the most active services; earliest on ties."""
    start, end = _validity(feed)
    best, best_n = None, -1
    day = start
    while day <= end:
        if day.weekday() in REPRESENTATIVE_WEEKDAYS:
            n = len(active_services(feed, day))
            if n > best_n:
                best, best_n = day, n
        day += dt.timedelta(days=1)
    if best is None:
        raise ValueError("GTFS validity contains no Tuesday-Thursday")
    return best


def trips_per_shape(feed: dict, day: dt.date, route_types: tuple[int, ...]) -> tuple[pd.Series, int]:
    """Number of bus trips on day per shape_id, and the number of bus trips without shape_id."""
    routes = feed["routes"]
    bus = set(routes.loc[routes["route_type"].astype(int).isin(route_types), "route_id"])
    trips = feed["trips"]
    trips = trips[trips["route_id"].isin(bus) & trips["service_id"].isin(active_services(feed, day))]
    has_shape = trips["shape_id"].notna() if "shape_id" in trips else pd.Series(False, index=trips.index)
    counts = trips.loc[has_shape, "shape_id"].value_counts()
    counts.index.name = "shape_id"
    return counts.rename("trips"), int((~has_shape).sum())


def shapes_gdf(feed: dict, shape_ids=None) -> gpd.GeoDataFrame:
    """One LineString per shape_id in EPSG:25832, points ordered by shape_pt_sequence (optionally only shape_ids)."""
    s = feed["shapes"]
    s = (s[s["shape_id"].isin(set(shape_ids))] if shape_ids is not None and not s.empty else s).copy()
    if s.empty:
        return gpd.GeoDataFrame({"shape_id": []}, geometry=[], crs="EPSG:25832").set_index("shape_id")
    s["seq"] = s["shape_pt_sequence"].astype(int)
    s = s.sort_values(["shape_id", "seq"])
    lines = s.groupby("shape_id").apply(
        lambda g: shapely.LineString(list(zip(g["shape_pt_lon"].astype(float), g["shape_pt_lat"].astype(float)))),
        include_groups=False)
    gdf = gpd.GeoDataFrame(geometry=lines.to_list(), index=lines.index, crs="EPSG:4326")
    return to_work_crs(gdf)
