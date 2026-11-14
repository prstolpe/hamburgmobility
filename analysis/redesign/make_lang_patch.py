"""Patch with the proposed plain-language fields (prompt 24, A5) for the dry run in a worktree.

Inserts label_plain / explain_plain (and why, where written) from analysis/redesign/rule_plain.yaml into copies of
config/rules.yaml, cycling_rules.yaml and design_rules.yaml (every rule with id, every category, every threshold
under a `thresholds` key), as text edits that keep the existing formatting. The schema gets the three optional fields
(config/schema/rules_model.py, _Strict base) and provenance treats them as text (META_KEYS).

Before writing the patch it proves that the change is text only: every modified YAML, with the three new keys removed,
loads to exactly the same Python object as the original.

Usage: uv run python -m analysis.redesign.make_lang_patch
Writes data/scenarios/redesign/lang/plain_fields.patch and prints counts.
"""

import json
import re
import subprocess
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/scenarios/redesign/lang"
NEW_KEYS = ("label_plain", "explain_plain", "why")
FILES = ["config/rules.yaml", "config/cycling_rules.yaml", "config/design_rules.yaml"]


def q(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)  # valid YAML double-quoted scalar


def fields(d: dict) -> list[tuple[str, str]]:
    return [(k, d[k]) for k in NEW_KEYS if d.get(k)]


def insert_rule_fields(text: str, plain: dict) -> tuple[str, int]:
    lines = text.split("\n")
    out, n = [], 0
    for line in lines:
        m_flow = re.search(r"\{id: ([A-Za-z0-9-]+),", line)
        m_item = re.match(r"^(\s*)- id: ([A-Za-z0-9-]+)\s*$", line)
        m_plain = re.match(r"^(\s*)id: ([A-Za-z0-9-]+)\s*$", line)
        if m_flow and m_flow.group(1) in plain:
            add = "".join(f" {k}: {q(v)}," for k, v in fields(plain[m_flow.group(1)]))
            line = line.replace(m_flow.group(0), m_flow.group(0) + add, 1)
            out.append(line)
            n += 1
        elif m_item and m_item.group(2) in plain:
            out.append(line)
            ind = " " * (len(m_item.group(1)) + 2)
            out += [f"{ind}{k}: {q(v)}" for k, v in fields(plain[m_item.group(2)])]
            n += 1
        elif m_plain and m_plain.group(2) in plain:
            out.append(line)
            out += [f"{m_plain.group(1)}{k}: {q(v)}" for k, v in fields(plain[m_plain.group(2)])]
            n += 1
        else:
            out.append(line)
    return "\n".join(out), n


def insert_categories(text: str, cats: dict) -> tuple[str, int]:
    n = 0
    for k, v in cats.items():
        pat = re.compile(rf"^(  {re.escape(k)}:\s*\{{)", re.M)
        add = "".join(f"{kk}: {q(vv)}, " for kk, vv in fields(v))
        text, c = pat.subn(lambda m: m.group(1) + add, text, count=1)
        n += c
    return text, n


def insert_thresholds(text: str, labels: dict) -> tuple[str, int]:
    """Threshold entries are flow mappings `name: {value: …` directly below a `thresholds:` line (same block)."""
    lines = text.split("\n")
    names = {p.rsplit(".", 1)[-1] for p in labels}
    by_name = {}
    for p, lab in labels.items():
        by_name.setdefault(p.rsplit(".", 1)[-1], []).append((p, lab))
    out, n, in_thr, thr_ind = [], 0, False, 0
    # walk with a minimal path tracker: we only need to know we are inside a `thresholds:` block
    for line in lines:
        m_thr = re.match(r"^(\s*)thresholds:\s*$", line)
        if m_thr:
            in_thr, thr_ind = True, len(m_thr.group(1))
            out.append(line)
            continue
        if in_thr and line.strip() and (len(line) - len(line.lstrip())) <= thr_ind:
            in_thr = False
        m = re.match(r"^(\s*)([a-z_0-9]+):\s*\{", line)
        if in_thr and m and m.group(2) in names and "value:" in line:
            cands = by_name[m.group(2)]
            lab = cands.pop(0)[1] if len(cands) == 1 or not cands else cands.pop(0)[1]
            line = line.replace("{", f"{{label_plain: {q(lab)}, ", 1)
            n += 1
        out.append(line)
    return "\n".join(out), n


def strip_new(o):
    if isinstance(o, dict):
        return {k: strip_new(v) for k, v in o.items() if k not in NEW_KEYS}
    if isinstance(o, list):
        return [strip_new(v) for v in o]
    return o


def main():
    plain = yaml.safe_load((ROOT / "analysis/redesign/rule_plain.yaml").read_text(encoding="utf-8"))
    cats = plain.pop("_categories")
    thr = plain.pop("_thresholds")
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        a, b = Path(tmp) / "a", Path(tmp) / "b"
        counts = {}
        for f in FILES + ["config/schema/rules_model.py", "config/schema/provenance.py"]:
            for base in (a, b):
                (base / f).parent.mkdir(parents=True, exist_ok=True)
                (base / f).write_text((ROOT / f).read_text(encoding="utf-8"), encoding="utf-8")
        for f in FILES:
            t = (b / f).read_text(encoding="utf-8")
            t, nr = insert_rule_fields(t, plain)
            nc = nt = 0
            if f.endswith("/rules.yaml"):
                t, nc = insert_categories(t, cats)
            key = f.split("/")[-1]
            if key in thr:
                t, nt = insert_thresholds(t, dict(thr[key]))
            (b / f).write_text(t, encoding="utf-8")
            orig = yaml.safe_load((a / f).read_text(encoding="utf-8"))
            new = yaml.safe_load(t)
            assert strip_new(new) == orig, f"{f}: content changed beyond the new text fields"
            counts[f] = {"rules": nr, "categories": nc, "thresholds": nt}
        # schema: three optional text fields on the strict base model
        p = b / "config/schema/rules_model.py"
        s = p.read_text(encoding="utf-8")
        s = s.replace('''class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
''', '''class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    # plain-language texts for the website and the rule reference (redesign 2026-11, A5); text only, no logic
    label_plain: str | None = None
    explain_plain: str | None = None
    why: str | None = None
''', 1)
        assert "label_plain: str | None" in s, "rules_model.py: _Strict not found"
        p.write_text(s, encoding="utf-8")
        p = b / "config/schema/provenance.py"
        s = p.read_text(encoding="utf-8")
        m = re.search(r"META_KEYS\s*=\s*\{", s)
        assert m, "provenance.py: META_KEYS not found"
        s = s[:m.end()] + '"label_plain", "explain_plain", "why", ' + s[m.end():]
        p.write_text(s, encoding="utf-8")
        diff = subprocess.run(["diff", "-ruN", "a", "b"], cwd=tmp, capture_output=True, text=True).stdout
    patch = OUT / "plain_fields.patch"
    patch.write_text(diff, encoding="utf-8")
    print(json.dumps(counts, indent=1))
    print(f"wrote {patch.relative_to(ROOT)} ({diff.count(chr(10))} lines)")


if __name__ == "__main__":
    main()
