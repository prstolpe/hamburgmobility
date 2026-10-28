import hashlib

from pipeline.lib.manifest import load_manifest, save_manifest, sha256_file


def test_sha256_file(tmp_path):
    path = tmp_path / "x.bin"
    path.write_bytes(b"hamburg" * 1000)
    assert sha256_file(path) == hashlib.sha256(b"hamburg" * 1000).hexdigest()


def test_empty_manifest_has_sources(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text("{}\n")
    assert load_manifest(path) == {"sources": {}}


def test_round_trip(tmp_path):
    path = tmp_path / "manifest.json"
    manifest = {"sources": {"osm": {"status": "ok", "files": [{"path": "data/raw/a.pbf", "sha256": "abc"}]}}}
    save_manifest(manifest, path)
    assert load_manifest(path) == manifest
