"""data/manifest.json: source, retrieval date and hash of every raw file."""

import hashlib
import json
from pathlib import Path

import geopandas as gpd

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.json"


def sha256_file(path: str | Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: str | Path = MANIFEST_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        manifest = json.load(f)
    manifest.setdefault("sources", {})
    return manifest


def save_manifest(manifest: dict, path: str | Path = MANIFEST_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def file_record(path: Path, gdf: gpd.GeoDataFrame | None = None) -> dict:
    """Manifest entry for one written file (path relative to the repository)."""
    record = {
        "path": str(Path(path).resolve().relative_to(REPO_ROOT)),
        "sha256": sha256_file(path),
        "bytes": Path(path).stat().st_size,
    }
    if gdf is not None:
        record["n_features"] = len(gdf)
        record["crs"] = gdf.crs.to_string() if gdf.crs else None
        record["bbox"] = [round(float(v), 1) for v in gdf.total_bounds] if len(gdf) else None
    return record
