"""Readability of the method page, Part B package 3 (prompt 24): before = the hand-written pages "Methode" and "Radnetz"
in web/src/pages.js on branch redesign/2026-11 before package 3 (HTML stripped); after = config/plain_language.yaml
section `method` (working tree), per part and in total. Same measures as analysis/redesign/readability.py.

Usage: uv run --with textstat --with pyphen python -m analysis.redesign.p3_readability
Writes data/scenarios/redesign/p3_readability.json and prints a Markdown table.
"""

import html
import json
import re
import subprocess
from pathlib import Path

import yaml

from analysis.redesign.readability import measure, term_hits

ROOT = Path(__file__).resolve().parents[2]
BEFORE_REF = "redesign/2026-11"
OUT = ROOT / "data" / "scenarios" / "redesign" / "p3_readability.json"


def strip_html(s: str) -> str:
    s = re.sub(r"\$\{[^{}]*(\{[^{}]*\}[^{}]*)*\}", "x", s)  # template expressions count as one word
    s = re.sub(r"</(p|li|h\d|tr|ul|ol|div)>", ".\n", s)
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


def before_texts() -> dict:
    js = subprocess.run(["git", "show", f"{BEFORE_REF}:web/src/pages.js"], cwd=ROOT, capture_output=True, text=True,
                        check=True).stdout
    out = {}
    for name, fn, end in (("Seite Methode (alt)", "export function methodHtml", "export function radnetzHtml"),
                          ("Seite Radnetz (alt)", "export function radnetzHtml", "export function downloadsHtml")):
        out[name] = strip_html(js[js.index(fn):js.index(end)])
    return out


def md_plain(s: str) -> str:
    s = re.sub(r"\{[^}]+\}", "x", s)
    s = re.sub(r"^\s*\|?-+\|.*$", "", s, flags=re.M)
    s = re.sub(r"[*_#|]", " ", s)
    return re.sub(r"^\s*(\d+\.|-)\s+", "", s, flags=re.M)


def after_texts() -> dict:
    m = yaml.safe_load((ROOT / "config/plain_language.yaml").read_text(encoding="utf-8"))["method"]
    s = m["summary"]
    out = {"Zusammenfassung": md_plain("\n".join([s["what"], *[f"{x['title']}. {x['text']}" for x in s["shows"] + s["not"]],
                                                  s["assumptions"]]))}
    for c in m["chapters"]:
        out[f"Kapitel {c['title']}"] = md_plain(f"{c['l1']}\n{c['l2']}")
    out["Regelreferenz (Einleitung)"] = md_plain(m["reference"]["intro"])
    out["Was ist neu"] = md_plain("\n".join(f"{n['title']}. {n['text']}\n" + "\n".join(n["items"]) for n in m["news"]))
    return out


def main():
    b, a = before_texts(), after_texts()
    rows = {**{k: {"stand": "vorher", **measure(v), "terms": sorted(term_hits(v))} for k, v in b.items()},
            **{k: {"stand": "nachher", **measure(v), "terms": sorted(term_hits(v))} for k, v in a.items()}}
    rows["gesamt vorher"] = {"stand": "vorher", **measure("\n".join(b.values())), "terms": sorted(term_hits("\n".join(b.values())))}
    rows["gesamt nachher"] = {"stand": "nachher", **measure("\n".join(a.values())), "terms": sorted(term_hits("\n".join(a.values())))}
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("| Teil | Stand | Wörter | WSTF | Flesch-Amstad | Wörter je Satz | Sätze > 15 Wörter | Fachbegriffe |")
    print("|---|---|---:|---:|---:|---:|---:|---|")
    for k, r in rows.items():
        f = lambda x: "–" if x is None else str(x).replace(".", ",")  # noqa: E731
        print(f"| {k} | {r['stand']} | {r['words']} | {f(r.get('wstf'))} | {f(r.get('fre_amstad'))} | "
              f"{f(r.get('mean_sentence_words'))} | {f(round(100 * r['share_sentences_over_15']) if 'share_sentences_over_15' in r else None)} % | "
              f"{', '.join(r['terms']) or '–'} |")


if __name__ == "__main__":
    main()
