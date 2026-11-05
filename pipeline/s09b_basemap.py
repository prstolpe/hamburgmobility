"""Stage 9b: background map for the website (prompts/11_web.md, config/sources.yaml web_assets).

Usage: uv run python -m pipeline.s09b_basemap [--refresh]

Cuts the work area (config/project.yaml, area: Bezirke plus buffer) out of the Protomaps daily build with `pmtiles extract` and takes
fonts (glyph PBFs) and sprites from protomaps/basemaps-assets. Output in data/out/basemap/ (not in git);
files and hashes go to data/manifest.json under web_assets. Only URLs from sources.yaml are used; a network
error stops the run (no substitute sources).
"""

import argparse
import io
import json
import shutil
import subprocess
import sys
import zipfile

import geopandas as gpd
import yaml

from pipeline.lib.area import read_work_area
from pipeline.lib.crs import WORK_CRS
from pipeline.lib.http import FetchError, get, make_session
from pipeline.lib.manifest import REPO_ROOT, file_record, load_manifest, save_manifest
from pipeline.s04_features import _now

OUT = REPO_ROOT / "data" / "out" / "basemap"
FONTS = ["Noto Sans Regular", "Noto Sans Medium", "Noto Sans Italic"]
SPRITE_VERSION = "v4"  # sprites/v4 belongs to @protomaps/basemaps 4.x/5.x
SPRITE_FLAVOR = "light"


def _load_yaml(name: str) -> dict:
    with open(REPO_ROOT / "config" / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def bbox_wgs84() -> list[float]:
    """Bounding box of the work area (Bezirke + buffer, without Neuwerk); EPSG:25832 -> 4326 only here."""
    area = read_work_area(exclude_rural=False)  # the map also shows the rural Stadtteile (grey)
    return [round(float(v), 5) for v in gpd.GeoSeries([area], crs=WORK_CRS).to_crs(4326).total_bounds]


def extract(url: str, bbox: list[float], maxzoom: int, out) -> None:
    if shutil.which("pmtiles") is None:
        raise RuntimeError("pmtiles CLI fehlt (brew install pmtiles)")
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pmtiles", "extract", url, str(out), f"--bbox={','.join(map(str, bbox))}",
                    f"--maxzoom={maxzoom}"], check=True)


def assets(session, url: str) -> None:
    data = get(session, url).content
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        root = z.namelist()[0].split("/")[0]
        wanted = [f"{root}/fonts/{f}/" for f in FONTS] + [f"{root}/sprites/{SPRITE_VERSION}/{SPRITE_FLAVOR}",
                                                          f"{root}/fonts/OFL.txt"]
        for name in z.namelist():
            if name.endswith("/") or not any(name.startswith(w) for w in wanted):
                continue
            target = OUT / name.removeprefix(f"{root}/").replace(f"sprites/{SPRITE_VERSION}/", "sprites/")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(name))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true", help="extract and download again")
    args = parser.parse_args(argv)
    project, sources = _load_yaml("project.yaml"), _load_yaml("sources.yaml")["web_assets"]
    web = project["web"]["basemap"]
    url = sources["basemap"]["url"].replace("{build}", str(web["build"]))
    tiles = OUT / "basemap.pmtiles"
    stamp = OUT / "extract.json"  # bbox and build of the current extract; a new work area means a new extract
    bbox = bbox_wgs84()
    wanted = {"bbox": bbox, "build": str(web["build"]), "maxzoom": int(web["maxzoom"])}
    current = json.loads(stamp.read_text()) if stamp.exists() else None
    try:
        if args.refresh or not tiles.exists() or current != wanted:
            extract(url, bbox, int(web["maxzoom"]), tiles)
            stamp.write_text(json.dumps(wanted))
        if args.refresh or not (OUT / "fonts").exists():
            assets(make_session(), sources["basemap_assets"]["url"])
    except (RuntimeError, subprocess.CalledProcessError, FetchError, OSError, zipfile.BadZipFile) as exc:
        print(f"basemap: FEHLER {exc}", file=sys.stderr)
        return 1
    n_fonts = len(list((OUT / "fonts").rglob("*.pbf")))
    if n_fonts == 0 or not (OUT / "sprites" / f"{SPRITE_FLAVOR}.json").exists():
        print("basemap: FEHLER Schriften oder Sprites fehlen im Archiv", file=sys.stderr)
        return 1
    manifest = load_manifest()
    manifest.setdefault("web_assets", {})["basemap"] = {
        "url": url, "bbox_wgs84": bbox, "maxzoom": web["maxzoom"], "license": sources["basemap"]["license"],
        "retrieved_at": _now(), "files": [{"layer": "basemap", **file_record(tiles)}],
        "assets": {"url": sources["basemap_assets"]["url"], "fonts": FONTS, "glyph_files": n_fonts,
                   "sprites": f"{SPRITE_VERSION}/{SPRITE_FLAVOR}"}}
    save_manifest(manifest)
    print(f"basemap: {tiles.stat().st_size / 1e6:.1f} MB, {n_fonts} glyph files, bbox {bbox}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
