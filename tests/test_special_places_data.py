"""Special places against the real segment table (skipped until `make classify`/`make coherence` has run)."""

import pandas as pd
import pytest

from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_special_places

FINAL = REPO_ROOT / "data" / "interim" / "final.parquet"
pytestmark = pytest.mark.skipif(not FINAL.exists(), reason="run the pipeline up to data/interim/final.parquet first")


def test_segment_ids_exist():
    ids = set(pd.read_parquet(FINAL, columns=["segment_id"])["segment_id"])
    for p in load_special_places().places:
        missing = sorted(set(p.segment_ids()) - ids)
        assert not missing, f"{p.id}: unknown segment ids {missing}"
