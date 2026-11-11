"""Schema and config checks for rules.yaml validation.invariants (Review 2026-11, structural recommendation 6)."""

import ast
import re

import pytest

from pipeline.lib import invariants as iv
from pipeline.lib.manifest import REPO_ROOT
from pipeline.lib.rules import load_cycling_rules, load_design_rules, load_rules

RULES = load_rules()
INVARIANTS = RULES.validation.invariants


def test_invariant_block_lists_v_inv_01_to_09():
    assert [i.id for i in INVARIANTS] == [f"V-INV-{n:02d}" for n in range(1, 10)]
    assert set(iv.CHECKS) == {i.id for i in INVARIANTS}
    for inv in INVARIANTS:
        assert all(re.fullmatch(r"F\d{2}", f) for f in inv.finding), inv.id
        assert inv.status != "inactive", inv.id


@pytest.mark.parametrize("inv", INVARIANTS, ids=lambda i: i.id)
def test_every_invariant_has_a_test_referencing_it(inv):
    """Every V-INV id in the block names at least one test; the test exists and its file mentions the id."""
    for ref in inv.tested_in:
        path, name = ref.split("::")
        file = REPO_ROOT / path
        assert file.exists(), ref
        text = file.read_text(encoding="utf-8")
        assert inv.id in text, f"{path} erwähnt {inv.id} nicht"
        funcs = {n.name for n in ast.walk(ast.parse(text)) if isinstance(n, ast.FunctionDef)}
        assert name in funcs, ref


def test_every_v_inv_mentioned_in_tests_is_in_the_block():
    known = {i.id for i in INVARIANTS}
    used = {m for f in (REPO_ROOT / "tests").glob("test_*.py")
            for m in re.findall(r"V-INV-\d{2}", f.read_text(encoding="utf-8"))}
    assert used <= known, sorted(used - known)


def test_v_inv_01_every_category_has_matrix_and_profile():
    """V-INV-01 (F28), config part: every category of rules.yaml has an active separation_matrix row and a profile
    rule (PRF-03 parking_by_category) or is in design_rules PRF-04 no_profile_categories."""
    assert iv.categories_without_matrix_or_profile(RULES, load_cycling_rules(), load_design_rules()) == {}


def test_v_inv_01_detects_a_missing_profile_rule():
    design = load_design_rules()
    rules = [dict(r) for r in design.profile_assignment["rules"]]
    prf03 = next(r for r in rules if r["id"] == "PRF-03")
    prf03["parking_by_category"] = {k: v for k, v in prf03["parking_by_category"].items() if k != "ETW_ERF"}
    bad = design.model_copy(update={"profile_assignment": {**design.profile_assignment, "rules": rules}})
    assert iv.categories_without_matrix_or_profile(RULES, load_cycling_rules(), bad) == {"ETW_ERF": "Profilregel fehlt"}


def test_v_inv_01_rural_categories_need_no_profile_entry_while_matrix_inactive():
    """Outside built-up areas the matrix is inactive (F28); GOW80/ETW60 are covered only via no_profile_categories."""
    design = load_design_rules()
    prf04 = next(r for r in design.profile_assignment["rules"] if r["id"] == "PRF-04")
    assert {"SW", "GOW80", "ETW60"} <= set(prf04["no_profile_categories"])
    rules = [dict(r) for r in design.profile_assignment["rules"]]
    next(r for r in rules if r["id"] == "PRF-04")["no_profile_categories"] = ["SW", "ETW60"]
    bad = design.model_copy(update={"profile_assignment": {**design.profile_assignment, "rules": rules}})
    assert "GOW80" in iv.categories_without_matrix_or_profile(RULES, load_cycling_rules(), bad)
