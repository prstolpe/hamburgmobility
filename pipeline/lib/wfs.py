"""WFS 2.0 access: capabilities, hit count, GetFeature (GeoJSON, EPSG:25832)."""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

import geopandas as gpd

from pipeline.lib.geo import Bbox, check_in_bbox, features_to_gdf
from pipeline.lib.http import FetchError, get, get_json

SRS = "urn:ogc:def:crs:EPSG::25832"  # axis order easting, northing
GEOJSON = "application/geo+json"


@dataclass
class Capabilities:
    typenames: list[str] = field(default_factory=list)
    titles: dict[str, str] = field(default_factory=dict)
    paging: bool = False
    count_default: int | None = None
    output_formats: list[str] = field(default_factory=list)
    fees: str | None = None


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child(el: ET.Element, name: str) -> ET.Element | None:
    return next((c for c in el if _local(c.tag) == name), None)


def capabilities(session, url: str) -> Capabilities:
    response = get(session, url, params={"SERVICE": "WFS", "REQUEST": "GetCapabilities"})
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as exc:
        raise FetchError(f"{url}: capabilities are not XML ({exc})") from exc
    caps = Capabilities()
    for el in root.iter():
        name = _local(el.tag)
        if name == "FeatureType":
            type_name = _child(el, "Name")
            title = _child(el, "Title")
            if type_name is not None and type_name.text:
                caps.typenames.append(type_name.text.strip())
                caps.titles[type_name.text.strip()] = (title.text or "").strip() if title is not None else ""
        elif name == "Constraint":
            default = next((c for c in el.iter() if _local(c.tag) == "DefaultValue"), None)
            value = (default.text or "").strip() if default is not None else ""
            if el.get("name") == "ImplementsResultPaging":
                caps.paging = value.upper() == "TRUE"
            elif el.get("name") == "CountDefault" and value.isdigit():
                caps.count_default = int(value)
        elif name == "Parameter" and el.get("name") == "outputFormat":
            caps.output_formats = [v.text.strip() for v in el.iter() if _local(v.tag) == "Value" and v.text]
        elif name == "Fees" and el.text:
            caps.fees = el.text.strip()
    return caps


def _bbox_param(bbox: Bbox) -> str:
    return ",".join(str(v) for v in bbox) + f",{SRS}"


def hits(session, url: str, typename: str, bbox: Bbox | None) -> int:
    """Number of features in bbox (bbox=None: whole service)."""
    params = {"SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature", "TYPENAMES": typename,
              "RESULTTYPE": "hits"}
    if bbox is not None:
        params["BBOX"] = _bbox_param(bbox)
    root = ET.fromstring(get(session, url, params=params).content)
    matched = root.get("numberMatched")
    if matched is None or not matched.isdigit():
        raise FetchError(f"{url} {typename}: no numeric numberMatched in hits response ({matched!r})")
    return int(matched)


def get_features(session, url: str, typename: str, bbox: Bbox, expected: int, paging: bool,
                 page_size: int = 5000, count_default: int | None = None) -> gpd.GeoDataFrame:
    """All features of typename in bbox; the count must equal `expected` (from hits)."""
    label = f"{url} {typename}"
    base = {"SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature", "TYPENAMES": typename,
            "OUTPUTFORMAT": GEOJSON, "SRSNAME": SRS, "BBOX": _bbox_param(bbox)}
    features: list[dict] = []
    if paging:
        start = 0
        while start < expected:
            page = get_json(session, url, params={**base, "STARTINDEX": start, "COUNT": page_size})
            batch = page.get("features", [])
            if not batch:
                break
            features.extend(batch)
            start += len(batch)
    else:
        if count_default is not None and expected > count_default:
            raise FetchError(f"{label}: {expected} features exceed CountDefault {count_default} and the "
                             f"server does not support paging")
        features = get_json(session, url, params=base).get("features", [])
    if len(features) != expected:
        raise FetchError(f"{label}: expected {expected} features (resultType=hits), got {len(features)}")
    gdf = features_to_gdf(features)
    check_in_bbox(gdf, bbox, label)
    return gdf
