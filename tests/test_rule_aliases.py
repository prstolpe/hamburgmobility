"""Former rule ids (redesign 2026-11, package 5): a merged or removed rule keeps its old id as an alias of the rule
that took it over, so old links, traces and overrides stay readable. Ids and aliases are unique across all three rule
files, and no override names a retired id.
"""

import csv
from pathlib import Path

from pipeline.lib import export_rules as er

REPO = Path(__file__).resolve().parents[1]


def _all():
    docs = er.load_rule_docs()
    chapters = [{"key": "x", "sections": [f"{f}:{k}" for f, d in docs.items() for k in d if k not in ("meta", "sources")]}]
    return er.rule_reference(docs, chapters, decides={})["rules"]


def test_ids_and_aliases_unique_across_files():
    rules = _all()
    names = [r["id"] for r in rules] + [a for r in rules for a in (r["aliases"] or [])]
    assert len(names) == len(set(names)), sorted({n for n in names if names.count(n) > 1})


def test_aliases_are_lists_of_rule_id_strings():
    for r in _all():
        assert r["aliases"] is None or (r["aliases"] and all(isinstance(a, str) and a.strip() == a for a in r["aliases"]))


def test_no_override_names_a_retired_id():
    retired = {a for r in _all() for a in (r["aliases"] or [])}
    hits = []
    for f in (REPO / "overrides").glob("*.csv"):
        with f.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                hits += [(f.name, v) for v in row.values() if isinstance(v, str) and v in retired]
    assert not hits
