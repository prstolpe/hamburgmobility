"""Plain-language fields of the rule files (redesign 2026-11, package 4, decision E5 c; docs/redesign/05_rule_language.md).

Every rule with an id has label_plain, explain_plain and why; every category and every threshold under `thresholds`
has label_plain; the plain texts use no codes, rule IDs or variable names; history is a list of strings. The fields are
text only: the classification does not read them (proved by a full rerun, docs/redesign/impl_rule_language.md).
"""

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
FILES = ["config/rules.yaml", "config/cycling_rules.yaml", "config/design_rules.yaml"]
CODES = re.compile(r"\b(SW|GOW\d*|ETW\w*|RSV|HAUPT|BASIS|ERSCHL|DTV|Kfz|LSA|[A-Z]{1,5}-[A-Z0-9]{1,4}[a-z]?)\b")
SNAKE = re.compile(r"\b[a-z]+_[a-z0-9_]+\b")


def entries():
    out = []

    def walk(n, file):
        if isinstance(n, dict):
            if isinstance(n.get("id"), str):
                out.append((file, n))
            for v in n.values():
                walk(v, file)
        elif isinstance(n, list):
            for v in n:
                walk(v, file)
    for f in FILES:
        walk(yaml.safe_load((ROOT / f).read_text(encoding="utf-8")), f)
    return out


def thresholds():
    out = []

    def walk(n, path, under):
        if isinstance(n, dict):
            if "value" in n and under:
                out.append((path, n))
                return
            for k, v in n.items():
                walk(v, f"{path}.{k}", under or k == "thresholds")
        elif isinstance(n, list):
            for i, v in enumerate(n):
                walk(v, f"{path}[{i}]", under)
    for f in FILES:
        walk(yaml.safe_load((ROOT / f).read_text(encoding="utf-8")), f, False)
    return out


RULES = entries()


def plain_ok(text: str) -> list[str]:
    problems = []
    if CODES.search(text):
        problems.append(f"code {CODES.search(text).group(0)!r}")
    if SNAKE.search(text):
        problems.append(f"variable {SNAKE.search(text).group(0)!r}")
    return problems


def test_rule_count():
    assert len(RULES) == 190  # 0.23.0: H-PAIR-01; 0.24.0: C-G50-02


@pytest.mark.parametrize("file,rule", RULES, ids=[r["id"] for _, r in RULES])
def test_every_rule_has_plain_fields(file, rule):
    for key in ("label_plain", "explain_plain", "why"):
        assert isinstance(rule.get(key), str) and rule[key].strip(), f"{rule['id']}: {key} missing"
        assert not plain_ok(rule[key]), f"{rule['id']}.{key}: {plain_ok(rule[key])}"
    assert len(rule["label_plain"].split()) <= 8
    assert len(rule["explain_plain"].split()) <= 25
    if "history" in rule:
        assert isinstance(rule["history"], list) and all(isinstance(h, str) and h for h in rule["history"])


def test_categories_have_plain_fields_matching_the_glossary():
    rules = yaml.safe_load((ROOT / "config/rules.yaml").read_text(encoding="utf-8"))
    glossary = yaml.safe_load((ROOT / "config/glossary.yaml").read_text(encoding="utf-8"))
    for code, c in rules["categories"].items():
        assert c.get("label_plain") == glossary["categories"][code]["plain"], code
        assert c.get("explain_plain") and not plain_ok(c["explain_plain"]), code


def test_every_threshold_has_a_plain_label():
    th = thresholds()
    assert len(th) == 62  # 0.23.0: three H-PAIR-01 thresholds; 0.24.0: gow30_max_dtv
    for path, t in th:
        assert t.get("label_plain") and not plain_ok(t["label_plain"]), path


def test_rule_files_still_validate():
    from pipeline.lib.rules import load_cycling_rules, load_design_rules, load_rules
    load_rules(), load_cycling_rules(), load_design_rules()
