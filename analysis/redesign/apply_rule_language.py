"""Apply the plain-language fields and the history field to the rule files (redesign 2026-11, package 4, decision E5 c).

Inputs: analysis/redesign/rule_plain.yaml (label_plain, explain_plain, why per rule; categories; thresholds) and
analysis/redesign/rule_history.yaml (per rule: new description and/or note without version history, history list).
Edits are text edits that keep the formatting of everything else (a YAML round trip would rewrite hundreds of lines).

Proof before writing (assert): every file, with the keys label_plain/explain_plain/why/history removed and the
description/note of the history rules taken from the original, loads to exactly the same object as before; and the
new description/note/history read back exactly as given. Writes the config files in place (or --dry-run).

Usage: uv run python -m analysis.redesign.apply_rule_language [--dry-run]
"""

import copy
import json
import re
import sys
import textwrap
from pathlib import Path

import yaml

from analysis.redesign.make_lang_patch import insert_categories, insert_rule_fields, insert_thresholds

ROOT = Path(__file__).resolve().parents[2]
FILES = ["config/rules.yaml", "config/cycling_rules.yaml", "config/design_rules.yaml"]
NEW_KEYS = ("label_plain", "explain_plain", "why", "history")
WIDTH = 118


def q(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def norm(s) -> str | None:
    return None if s is None else " ".join(str(s).split())


def entry_span(lines: list[str], rid: str) -> tuple[int, int, str]:
    """Line range [start, end) of the entry with this id and its style ('flow' or 'block')."""
    pat_flow = re.compile(rf"\{{id: {re.escape(rid)},")
    pat_block = re.compile(rf"^(\s*)(- )?id: {re.escape(rid)}\s*$")
    for i, line in enumerate(lines):
        if pat_flow.search(line):
            depth, j = 0, i
            while True:
                depth += lines[j].count("{") - lines[j].count("}")
                if depth <= 0:
                    return i, j + 1, "flow"
                j += 1
        m = pat_block.match(line)
        if m:
            ind = len(m.group(1)) + (2 if m.group(2) else 0)
            j = i + 1
            while j < len(lines) and (not lines[j].strip() or len(lines[j]) - len(lines[j].lstrip()) >= ind) \
                    and not (lines[j].strip().startswith("- ") and len(lines[j]) - len(lines[j].lstrip()) < ind + 1 and m.group(2)
                             and len(lines[j]) - len(lines[j].lstrip()) == len(m.group(1))):
                j += 1
            while j > i + 1 and not lines[j - 1].strip():
                j -= 1
            return i, j, "block"
    raise KeyError(rid)


def block_key_range(lines, start, end, key, key_ind) -> tuple[int, int, int] | None:
    """Lines [a, b) of `key:` of the entry itself (indentation key_ind, not keys of nested mappings)."""
    for i in range(start, end):
        m = re.match(rf"^(\s*)(- )?{key}:(.*)$", lines[i])
        if not m:
            continue
        ind = len(m.group(1)) + (2 if m.group(2) else 0)
        if ind != key_ind:
            continue
        rest = m.group(3).strip()
        j = i + 1
        if rest in (">-", ">", "|", "|-", ">+", "") or (rest and rest[0] in "'\"" and not re.match(r"^(['\"]).*\1\s*$", rest)):
            while j < end and lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) > ind:
                j += 1
        return i, j, ind
    return None


def block_value(key: str, text: str, ind: int) -> list[str]:
    body = textwrap.wrap(text, WIDTH - ind - 2, break_long_words=False, break_on_hyphens=False)
    return [f"{' ' * ind}{key}: >-", *[f"{' ' * (ind + 2)}{b}" for b in body]]


def apply_history(text: str, hist: dict) -> str:
    lines = text.split("\n")
    for rid, h in hist.items():
        start, end, style = entry_span(lines, rid)
        if style == "flow":
            seg = "\n".join(lines[start:end])
            for key in ("description", "note"):
                if key not in h:
                    continue
                m = re.search(rf"\b{key}: ('(?:[^']|'')*'|\"(?:[^\"\\]|\\.)*\")", seg)
                if h[key] is None:
                    seg = re.sub(rf",?\s*\b{key}: ('(?:[^']|'')*'|\"(?:[^\"\\]|\\.)*\")", "", seg, count=1) if m else seg
                elif m:
                    seg = seg[:m.start(1)] + q(h[key]) + seg[m.end(1):]
                else:
                    seg = seg.replace(f"{{id: {rid},", f"{{id: {rid}, {key}: {q(h[key])},", 1)
            if h.get("history"):
                seg = seg.replace(f"{{id: {rid},", f"{{id: {rid}, history: [{', '.join(q(x) for x in h['history'])}],", 1)
            lines[start:end] = seg.split("\n")
        else:
            id_ind = len(lines[start]) - len(lines[start].lstrip()) + (2 if lines[start].lstrip().startswith("- ") else 0)
            insert_at = None
            for key in ("description", "note"):
                if key not in h:
                    continue
                start, end, _ = entry_span(lines, rid)
                r = block_key_range(lines, start, end, key, id_ind)
                if h[key] is None:
                    if r:
                        del lines[r[0]:r[1]]
                    continue
                new = block_value(key, h[key], r[2] if r else id_ind)
                if r:
                    lines[r[0]:r[1]] = new
                    insert_at = r[0] + len(new)
                else:
                    lines[start + 1:start + 1] = new
                    insert_at = start + 1 + len(new)
            if h.get("history"):
                start, end, _ = entry_span(lines, rid)
                at = insert_at if insert_at is not None else end
                lines[at:at] = [f"{' ' * id_ind}history:", *[f"{' ' * (id_ind + 2)}- {q(x)}" for x in h["history"]]]
    return "\n".join(lines)


def strip(o, hist_ids, orig_index):
    """Remove the new keys; take description/note of history rules from the original (they are allowed to change)."""
    if isinstance(o, dict):
        d = {k: strip(v, hist_ids, orig_index) for k, v in o.items() if k not in NEW_KEYS}
        if d.get("id") in hist_ids:
            for k in ("description", "note"):
                d.pop(k, None)
                if k in orig_index[d["id"]]:
                    d[k] = orig_index[d["id"]][k]
        return d
    if isinstance(o, list):
        return [strip(v, hist_ids, orig_index) for v in o]
    return o


def index(o, out=None):
    out = {} if out is None else out
    if isinstance(o, dict):
        if isinstance(o.get("id"), str):
            out[o["id"]] = o
        for v in o.values():
            index(v, out)
    elif isinstance(o, list):
        for v in o:
            index(v, out)
    return out


def main(dry: bool) -> None:
    plain = yaml.safe_load((ROOT / "analysis/redesign/rule_plain.yaml").read_text(encoding="utf-8"))
    cats, thr = plain.pop("_categories"), plain.pop("_thresholds")
    hist = yaml.safe_load((ROOT / "analysis/redesign/rule_history.yaml").read_text(encoding="utf-8")) or {}
    counts = {}
    for f in FILES:
        src = (ROOT / f).read_text(encoding="utf-8")
        orig = yaml.safe_load(src)
        h = {k: v for k, v in hist.items() if v.get("file") == f}
        t = apply_history(src, h)
        t, nr = insert_rule_fields(t, plain)
        nc = nt = 0
        if f.endswith("/rules.yaml"):
            t, nc = insert_categories(t, cats)
        if f.split("/")[-1] in thr:
            t, nt = insert_thresholds(t, dict(thr[f.split("/")[-1]]))
        new = yaml.safe_load(t)
        oi, ni = index(orig), index(new)
        assert strip(copy.deepcopy(new), set(h), oi) == strip(copy.deepcopy(orig), set(h), oi), f"{f}: unexpected change"
        for rid, v in h.items():
            for k in ("description", "note"):
                if k in v:
                    assert norm(ni[rid].get(k)) == norm(v[k]), f"{rid}.{k} not written as given"
            assert ni[rid].get("history") == v.get("history"), f"{rid}.history not written as given"
        counts[f] = {"rules": nr, "categories": nc, "thresholds": nt, "history": len(h)}
        if not dry:
            (ROOT / f).write_text(t, encoding="utf-8")
    print(json.dumps(counts, indent=1), "(dry run)" if dry else "written")


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
