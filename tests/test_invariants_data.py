"""Invariants V-INV-01..09 on the real data/interim files (rules.yaml validation.invariants, Review 2026-11).

test_invariant_result_matches_expected runs every check of pipeline/lib/invariants.py and compares it with
`expected` in rules.yaml (holds -> no violation; violated -> known violation, open question). Explicit tests for
V-INV-01 and V-INV-09; the other invariants also have their own tests next to the stage (see tested_in)."""

import pandas as pd
import pytest

from pipeline.lib import invariants as iv
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_rules

FINAL = REPO_ROOT / "data" / "interim" / "final.parquet"
RULES = load_rules()


@pytest.mark.parametrize("inv", RULES.validation.invariants, ids=lambda i: i.id)
def test_invariant_result_matches_expected(inv):
    res = iv.CHECKS[inv.id]()
    if res.status == "not_checked":
        pytest.skip(res.detail)
    if inv.expected == "holds":
        assert res.ok, f"{inv.id}: {res.detail}"
    else:
        assert not res.ok, f"{inv.id} gilt jetzt – expected in rules.yaml auf holds setzen und xfail entfernen"


@pytest.mark.skipif(not FINAL.exists(), reason="run `make coherence` first")
def test_v_inv_01_cat_final_has_matrix_and_profile():
    """V-INV-01 (F28): every cat_final in the data has a matrix row and a profile rule or no profile by design."""
    cats = set(pd.read_parquet(FINAL, columns=["cat_final"])["cat_final"].dropna())
    assert cats
    assert not cats & set(iv.categories_without_matrix_or_profile())


@pytest.mark.skipif(not FINAL.exists(), reason="run `make coherence` first")
@pytest.mark.xfail(reason="V-INV-09 verletzt: 20 HVS-Abschnitte (0,8 km) werden durch H-STR-01 Schritt (2) ETW30; "
                          "docs/open_questions.md, Review 2026-11 P6 V-INV-09", strict=True)
def test_v_inv_09_hvs_never_etw_without_override():
    """V-INV-09 (F29): no HVS segment with cat_final ETW30/ETW_ERF without an approved override."""
    final = pd.read_parquet(FINAL, columns=["segment_id", "in_hvs", "cat_final"])
    bad = iv.v_inv_09_violations(final)
    assert bad.empty, sorted(bad["segment_id"])


@pytest.mark.skipif(not FINAL.exists(), reason="run `make coherence` first")
def test_v_inv_09_cascade_alone_never_makes_hvs_etw():
    """The violations come from harmonisation only: cat_cascade of every violating segment is a GOW category."""
    final = pd.read_parquet(FINAL, columns=["segment_id", "in_hvs", "cat_final", "cat_cascade"])
    bad = iv.v_inv_09_violations(final)
    assert not bad["cat_cascade"].isin(iv.ETW_CATEGORIES).any()
