"""Links for manual checks in the sample reports."""

OSM_BASE = "https://www.openstreetmap.org"


def osm_map_link(point_wgs84) -> str:
    """Map link with marker; point_wgs84 is a shapely Point in EPSG:4326 (x = lon, y = lat)."""
    lat, lon = point_wgs84.y, point_wgs84.x
    return f"{OSM_BASE}/?mlat={lat:.6f}&mlon={lon:.6f}#map=18/{lat:.6f}/{lon:.6f}"


def osm_way_link(way_id: int) -> str:
    return f"{OSM_BASE}/way/{int(way_id)}"
