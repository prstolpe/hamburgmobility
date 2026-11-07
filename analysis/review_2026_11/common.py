"""Shared helpers for the review 2026-11: links for examples (site, OSM, orthophoto) and markdown formatting."""

from pathlib import Path

import geopandas as gpd
import pandas as pd

from pipeline.lib.links import load_viewers, orthophoto_link, osm_map_link

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://hamburgmobility.de/"
_VIEWERS = None


def _viewers():
    global _VIEWERS
    if _VIEWERS is None:
        _VIEWERS = load_viewers()
    return _VIEWERS


def seg_links(segment_id: str, geom_work) -> str:
    """Markdown links for one segment: site profile, OSM map, orthophoto (geometry in EPSG:25832)."""
    p = geom_work.interpolate(0.5, normalized=True) if geom_work.geom_type != "Point" else geom_work
    p84 = gpd.GeoSeries([p], crs=25832).to_crs(4326).iloc[0]
    return (f"[`{segment_id}`]({SITE}#karte?seg={segment_id}) · [OSM]({osm_map_link(p84)}) · "
            f"[Luftbild]({orthophoto_link(p, _viewers())})")


def node_links(node_id: str, point_work) -> str:
    p84 = gpd.GeoSeries([point_work], crs=25832).to_crs(4326).iloc[0]
    return (f"[`{node_id}`]({SITE}#karte?layer=jct&jct={node_id}) · [OSM]({osm_map_link(p84)}) · "
            f"[Luftbild]({orthophoto_link(point_work, _viewers())})")


def fmt(x, nd=0) -> str:
    """German number format with thin thousands separator."""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "–"
    s = f"{x:,.{nd}f}".replace(",", " ").replace(".", ",")
    return s


def md_table(df: pd.DataFrame, nd: dict | None = None) -> str:
    nd = nd or {}
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join("---:" if pd.api.types.is_numeric_dtype(df[c])
                                                                     else "---" for c in cols) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(fmt(r[c], nd.get(c, 1)) if isinstance(r[c], (int, float)) and not isinstance(r[c], bool)
                                     else str(r[c]) for c in cols) + " |")
    return "\n".join(out)
