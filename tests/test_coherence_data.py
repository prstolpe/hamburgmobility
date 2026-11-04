"""Checks on the real data/interim/coherence.parquet and final.parquet (skipped until `make coherence` has run).

Includes the test for orphaned overrides (guide 3.2 Stufe 7): every segment_id in overrides/overrides.csv must
still exist in the current network.
"""

import json

import pandas as pd
import pytest

from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.overrides import OVERRIDES_PATH, read_overrides, validate
from pipeline.lib.rules import load_rules

IN = REPO_ROOT / "data" / "interim" / "harmonised.parquet"
COH = REPO_ROOT / "data" / "interim" / "coherence.parquet"
FINAL = REPO_ROOT / "data" / "interim" / "final.parquet"

pytestmark = pytest.mark.skipif(not (COH.exists() and FINAL.exists()), reason="run `make coherence` first")


@pytest.fixture(scope="module")
def final() -> pd.DataFrame:
    return pd.read_parquet(FINAL, columns=["segment_id", "conflated", "cat_proposed", "cat_final", "cat_final_source",
                                           "flags", "coherence_trace", "override_reason"])


def test_segment_ids_and_cat_proposed_unchanged(final):
    inp = pd.read_parquet(IN, columns=["segment_id", "cat_proposed"])
    assert list(final["segment_id"]) == list(inp["segment_id"])
    assert final["cat_proposed"].fillna("–").equals(inp["cat_proposed"].fillna("–"))


def test_flags_are_json_with_known_rule_ids(final):
    known = {r.id for r in load_rules().coherence}
    area = final[final["conflated"].astype(bool)]
    for flags, trace in zip(area["flags"], area["coherence_trace"]):
        codes, entries = json.loads(flags), json.loads(trace)
        assert codes == list(dict.fromkeys(e["flag"] for e in entries))
        assert all(e["id"] in known for e in entries)
    assert final.loc[~final["conflated"].astype(bool), "flags"].isna().all()


def test_no_orphaned_overrides(final):
    rules = load_rules()
    df = read_overrides(OVERRIDES_PATH)
    validate(df, final.loc[final["cat_proposed"].notna(), "segment_id"], final["segment_id"], rules.categories)


def test_cat_final_only_differs_by_approved_override(final):
    approved = set(read_overrides(OVERRIDES_PATH).query("review_status == 'approved'")["segment_id"])
    diff = final[final["cat_final"].fillna("–") != final["cat_proposed"].fillna("–")]
    assert set(diff["segment_id"]) <= approved
    assert (final.loc[final["cat_final_source"] == "override", "override_reason"].str.strip() != "").all()
