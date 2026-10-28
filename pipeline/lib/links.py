"""Links for manual checks in the sample reports."""

OSM_BASE = "https://www.openstreetmap.org"


def osm_map_link(point_wgs84) -> str:
    """Map link with marker; point_wgs84 is a shapely Point in EPSG:4326 (x = lon, y = lat)."""
    lat, lon = point_wgs84.y, point_wgs84.x
    return f"{OSM_BASE}/?mlat={lat:.6f}&mlon={lon:.6f}#map=18/{lat:.6f}/{lon:.6f}"


def osm_way_link(way_id: int) -> str:
    return f"{OSM_BASE}/way/{int(way_id)}"


def load_viewers() -> dict:
    import yaml

    from pipeline.lib.manifest import REPO_ROOT

    with open(REPO_ROOT / "config" / "sources.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)["viewers"]


def orthophoto_link(point_work, viewers: dict | None = None) -> str:
    """Geoportal Hamburg with the orthophoto layer; point_work is a shapely Point in EPSG:25832."""
    v = (viewers or load_viewers())["orthophoto"]
    p = v["params"]
    return (f"{v['url']}?MAP/PROJECTION={p['projection']}&MAP/CENTER=[{point_work.x:.0f},{point_work.y:.0f}]"
            f"&MAP/ZOOMLEVEL={p['zoom_level']}&MAP/LAYERIDS={p['layer_id']}")


def panoramax_link(point_wgs84, viewers: dict | None = None) -> str:
    """Panoramax map view; point_wgs84 is a shapely Point in EPSG:4326 (x = lon, y = lat)."""
    v = (viewers or load_viewers())["panoramax"]
    return f"{v['url']}#focus=map&map={v['params']['zoom']}/{point_wgs84.y:.6f}/{point_wgs84.x:.6f}"
