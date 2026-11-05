"""OGC SensorThings API (iot.hamburg.de): paging, counter stations and daily counts.

Filter values (serviceName, layerName) come from config/sources.yaml; they are documented in the
Transparenzportal entry of the data set.
"""

import datetime as dt
from zoneinfo import ZoneInfo

import geopandas as gpd
import pandas as pd

from pipeline.lib.geo import features_to_gdf
from pipeline.lib.http import FetchError, get_json

LOCAL_TZ = ZoneInfo("Europe/Berlin")
PAGE_SIZE = 1000


def paged(session, url: str, params: dict) -> list[dict]:
    """All entities of a query, following @iot.nextLink; checks @iot.count when the server sends it."""
    page = get_json(session, url, params=params)
    expected = page.get("@iot.count")
    items = list(page.get("value", []))
    while next_link := page.get("@iot.nextLink"):
        page = get_json(session, next_link)
        items.extend(page.get("value", []))
    if expected is not None and len(items) != expected:
        raise FetchError(f"{url}: @iot.count {expected}, got {len(items)}")
    return items


def counter_stations(session, base: str, service_name: str, layer_name: str) -> gpd.GeoDataFrame:
    """Things of one service that have a datastream of the given layer, with location and datastream id."""
    ds_filter = f"properties/serviceName eq '{service_name}' and properties/layerName eq '{layer_name}'"
    params = {"$filter": " and ".join(f"Datastreams/{c}" for c in ds_filter.split(" and ")),
              "$expand": f"Locations($select=location),Datastreams($filter={ds_filter};$select=@iot.id,name,properties)",
              "$count": "true", "$top": PAGE_SIZE}
    things = paged(session, f"{base}/Things", params)
    features = []
    for thing in things:
        streams = [d for d in thing.get("Datastreams", []) if (d.get("properties") or {}).get("layerName") == layer_name]
        if len(streams) != 1:
            raise FetchError(f"Thing {thing.get('@iot.id')}: expected 1 datastream with layerName {layer_name}, "
                             f"got {len(streams)}")
        locations = thing.get("Locations") or [{}]
        geom = locations[0].get("location") or {}
        geom = geom.get("geometry", geom) if geom.get("type") == "Feature" else geom
        props = thing.get("properties") or {}
        features.append({"type": "Feature", "geometry": geom, "properties": {
            "thing_id": thing["@iot.id"], "name": thing.get("name"), "asset_id": props.get("assetID"),
            "art": props.get("art"), "richtung": props.get("richtung"),
            "datastream_id": streams[0]["@iot.id"], "datastream_name": streams[0].get("name"),
            "direction": (streams[0].get("properties") or {}).get("direction")}})
    return features_to_gdf(features, crs="EPSG:4326")


def year_window(year: int) -> tuple[str, str]:
    """UTC query window that contains every local day of the year (plus one day before)."""
    return f"{year - 1}-12-31T00:00:00Z", f"{year + 1}-01-01T00:00:00Z"


def _local_date(phenomenon_time: str) -> dt.date:
    start = phenomenon_time.split("/")[0].replace("Z", "+00:00")
    return dt.datetime.fromisoformat(start).astimezone(LOCAL_TZ).date()


def daily_counts(session, base: str, datastream_id: int, year: int) -> pd.DataFrame:
    """Daily counts of one datastream for the local days of one year: columns date, count."""
    start, end = year_window(year)
    params = {"$filter": f"phenomenonTime ge {start} and phenomenonTime lt {end}",
              "$select": "phenomenonTime,result", "$orderby": "phenomenonTime asc",
              "$top": PAGE_SIZE, "$count": "true"}
    obs = paged(session, f"{base}/Datastreams({datastream_id})/Observations", params)
    rows = [{"date": _local_date(o["phenomenonTime"]), "count": o["result"]} for o in obs]
    df = pd.DataFrame(rows, columns=["date", "count"])
    return df[[d.year == year for d in df["date"]]].reset_index(drop=True)
