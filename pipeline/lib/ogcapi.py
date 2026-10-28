"""OGC API Features access: collections and items with next-link paging (EPSG:25832)."""

import geopandas as gpd

from pipeline.lib.geo import Bbox, check_in_bbox, features_to_gdf
from pipeline.lib.http import FetchError, get_json

CRS_URI = "http://www.opengis.net/def/crs/EPSG/0/25832"
MAX_PAGES = 10_000


def collections(session, url: str) -> list[dict]:
    data = get_json(session, f"{url}/collections", params={"f": "json"})
    return [{"id": c["id"], "title": c.get("title")} for c in data.get("collections", [])]


def get_items(session, url: str, collection: str, bbox: Bbox, limit: int = 1000) -> gpd.GeoDataFrame:
    label = f"{url} {collection}"
    params = {"f": "json", "limit": limit, "bbox": ",".join(str(v) for v in bbox),
              "bbox-crs": CRS_URI, "crs": CRS_URI}
    page = get_json(session, f"{url}/collections/{collection}/items", params=params)
    matched = page.get("numberMatched")
    features = list(page.get("features", []))
    for _ in range(MAX_PAGES):
        next_link = next((link["href"] for link in page.get("links", []) if link.get("rel") == "next"), None)
        if not next_link or not page.get("features"):
            break
        page = get_json(session, next_link)  # next links carry all parameters
        features.extend(page.get("features", []))
    else:
        raise FetchError(f"{label}: more than {MAX_PAGES} pages")
    if matched is not None and len(features) != matched:
        raise FetchError(f"{label}: numberMatched {matched}, got {len(features)}")
    gdf = features_to_gdf(features)
    check_in_bbox(gdf, bbox, label)
    return gdf
