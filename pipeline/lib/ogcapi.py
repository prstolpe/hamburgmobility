"""OGC API Features access: collections and items with next-link paging (EPSG:25832)."""

import geopandas as gpd

from pipeline.lib.geo import Bbox, check_in_bbox, features_to_gdf
from pipeline.lib.http import FetchError, get_json

CRS_URI = "http://www.opengis.net/def/crs/EPSG/0/25832"
MAX_PAGES = 10_000


def collections(session, url: str) -> list[dict]:
    data = get_json(session, f"{url}/collections", params={"f": "json"})
    return [{"id": c["id"], "title": c.get("title")} for c in data.get("collections", [])]


def get_items(session, url: str, collection: str, bbox: Bbox | None, limit: int = 1000) -> gpd.GeoDataFrame:
    """All items in bbox (bbox=None: the whole collection)."""
    label = f"{url} {collection}"
    params = {"f": "json", "limit": limit, "crs": CRS_URI}
    if bbox is not None:
        params.update({"bbox": ",".join(str(v) for v in bbox), "bbox-crs": CRS_URI})
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
    if bbox is not None:
        check_in_bbox(gdf, bbox, label)
    return gdf


def get_items_skipping_broken(session, url: str, collection: str, limit: int = 200,
                              max_skipped: int = 100) -> tuple[gpd.GeoDataFrame, list[int]]:
    """Whole collection with explicit offset paging; records the server cannot deliver are skipped.

    api.hamburg.de answers single broken records with HTTP 500 and cuts off any page that contains
    them (HTTP 200, truncated JSON). A failing page is halved until the failing record stands alone;
    that record's offset is skipped and returned. Only for sources with fetch.skip_broken_records in
    config/sources.yaml. Raises FetchError if no page can be read at all, if more than max_skipped
    records fail, or if numberMatched != fetched + skipped.
    """
    label = f"{url} {collection}"
    items_url = f"{url}/collections/{collection}/items"
    features: list[dict] = []
    skipped: list[int] = []
    state: dict = {"matched": None, "last_error": None}

    def read(offset: int, size: int) -> None:
        try:
            page = get_json(session, items_url, params={"f": "json", "limit": size, "offset": offset, "crs": CRS_URI})
        except FetchError as exc:
            state["last_error"] = exc
            if size == 1:
                skipped.append(offset)
                if len(skipped) > max_skipped:
                    raise FetchError(f"{label}: more than {max_skipped} broken records ({exc})") from exc
                return
            half = size // 2
            read(offset, half)
            if state["matched"] is None or offset + half < state["matched"]:
                read(offset + half, size - half)
            return
        if state["matched"] is None and page.get("numberMatched") is not None:
            state["matched"] = int(page["numberMatched"])
        features.extend(page.get("features", []))

    offset = 0
    for _ in range(MAX_PAGES):
        read(offset, limit)
        offset += limit
        if state["matched"] is None:
            raise FetchError(f"{label}: no page could be read ({state['last_error']})")
        if offset >= state["matched"]:
            break
    else:
        raise FetchError(f"{label}: more than {MAX_PAGES} pages")
    if len(features) + len(skipped) != state["matched"]:
        raise FetchError(f"{label}: numberMatched {state['matched']}, got {len(features)} + {len(skipped)} skipped")
    return features_to_gdf(features), sorted(skipped)
