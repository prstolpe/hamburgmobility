"""Example features for the UI review (prompt 21b, phase 3).

Writes data/scenarios/review_ui/fixtures.json: map coordinates of the example street segment and junctions
(the Playwright scripts click them on the map) and a seeded random sample of segment IDs for profile metrics.
Read-only on data/out/downloads.
"""

import json
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[3]
DL = ROOT / "data/out/downloads"
OUT = ROOT / "data/scenarios/review_ui"

# Hallerstraße GOW30 with discrepancy D3 (high priority); Sternschanze junction (signal -> continuous footway)
EXAMPLE_SEGMENT = "seg_5a4361a0331e0791"
EXAMPLE_JUNCTIONS = ["8541215407", "628944060"]
SAMPLE_N = 30
SEED = 21


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    seg = gpd.read_parquet(DL / "segments.parquet")
    jct = gpd.read_parquet(DL / "junctions.parquet")
    s = seg[seg.segment_id == EXAMPLE_SEGMENT].iloc[0]
    mid = s.geometry.interpolate(0.5, normalized=True)
    j = jct[jct.node_id.astype(str).isin(EXAMPLE_JUNCTIONS)]
    sample = seg.sample(n=SAMPLE_N, random_state=SEED)
    out = {
        "segment": {"id": EXAMPLE_SEGMENT, "name": s["name"], "lon": round(mid.x, 6), "lat": round(mid.y, 6)},
        "junctions": [
            {"id": str(r.node_id), "names": r.names, "lon": round(r.geometry.x, 6), "lat": round(r.geometry.y, 6)}
            for r in j.itertuples()
        ],
        "sample_segments": sample.segment_id.tolist(),
    }
    (OUT / "fixtures.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(json.dumps(out, ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()
