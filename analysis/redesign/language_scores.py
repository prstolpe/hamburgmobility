"""Readability before/after for the plain-language samples (prompt 24, A4).

Reads analysis/redesign/language_samples.yaml, takes "before" from the content capture
(data/scenarios/redesign/ui/content.json) and scores before and after with the same measures as
analysis/redesign/readability.py. Also checks the "after" texts against the A4 rules (sentences under 15 words,
no technical term outside the glossary's level-1/2 names, no rule IDs or category codes).

Usage: uv run --with textstat --with pyphen python -m analysis.redesign.language_scores
Writes data/scenarios/redesign/language_scores.json (also used by fill_tables: table language_scores).
"""

import json
import re
from pathlib import Path

import yaml

from analysis.redesign.readability import WORDS, measure, sentences, term_hits

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "data/scenarios/redesign/ui"
CODES = re.compile(r"\b(SW|GOW\d*|ETW\w*|D[1-3]|[A-Z]{1,5}-[A-Z0-9-]{2,})\b")


def before_text(ref: str, c: dict) -> str:
    kind, *rest = ref.split(":")
    if kind == "page":
        page, heads = rest[0], rest[1].split("|")
        return "\n".join(s["text"] for s in c["pages"][page]["sections"] if s["heading"] in heads)
    if kind == "layer":
        v = c["layers"][rest[0]]
        return "\n".join([v["text"], *v["legend"], *v["notes"]])
    if kind == "profile":
        cat, heads = rest[0], rest[1].split("|")
        p = c["profiles"][cat]
        return "\n".join(f"{s['heading']}\n{s['text']}" for s in p["sections"] if s["heading"] in heads)
    if kind == "junction":
        heads = rest[0].split("|")
        return "\n".join(f"{s['heading']}\n{s['text']}" for s in c["junction"]["sections"] if s["heading"] in heads)
    raise ValueError(ref)


def main():
    c = json.loads((UI / "content.json").read_text(encoding="utf-8"))
    samples = yaml.safe_load((ROOT / "analysis/redesign/language_samples.yaml").read_text(encoding="utf-8"))["samples"]
    out = []
    for s in samples:
        b = before_text(s["ref"], c)
        a = s["after"].strip()
        mb, ma = measure(b), measure(a)
        long_after = [x for x in sentences(a) if len(WORDS.findall(x)) > 15]
        codes_after = sorted(set(CODES.findall(a)))
        out.append({"id": s["id"], "title": s["title"], "before": b, "after": a, "m_before": mb, "m_after": ma,
                    "terms_before": term_hits(b), "terms_after": term_hits(a),
                    "after_long_sentences": long_after, "after_codes": codes_after})
    tot_b = measure("\n".join(x["before"] for x in out))
    tot_a = measure("\n".join(x["after"] for x in out))
    res = {"samples": out, "total_before": tot_b, "total_after": tot_a}
    (ROOT / "data/scenarios/redesign/language_scores.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    for x in out:
        print(f"{x['id']:16s} WSTF {x['m_before'].get('wstf')} -> {x['m_after'].get('wstf')}  FRE {x['m_before'].get('fre_amstad')} -> "
              f"{x['m_after'].get('fre_amstad')}  words {x['m_before']['words']} -> {x['m_after']['words']}  long {len(x['after_long_sentences'])} codes {x['after_codes']}")
    print("total", tot_b, "->", tot_a)


if __name__ == "__main__":
    main()
