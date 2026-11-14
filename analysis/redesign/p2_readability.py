"""Readability of the texts changed in Part B, package 2 (prompt 24): config/plain_language.yaml (without the technical
download description `columns`) and the view descriptions in web/src/layers.js (LAYER_INFO), before (branch
redesign/2026-11, before package 2) and after (working tree). Same measures as analysis/redesign/readability.py.

Usage: uv run --with textstat --with pyphen python -m analysis.redesign.p2_readability
Writes data/scenarios/redesign/p2_readability.json and prints a table.
"""

import json
import re
import subprocess
from pathlib import Path

import yaml

from analysis.redesign.readability import measure, term_hits

ROOT = Path(__file__).resolve().parents[2]
BEFORE_REF = "redesign/2026-11"


def git_show(path: str) -> str:
    return subprocess.run(["git", "show", f"{BEFORE_REF}:{path}"], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def yaml_texts(text: str) -> list[str]:
    doc = yaml.safe_load(text)
    doc.pop("columns", None)
    doc.get("cycling", {}).pop("columns", None)
    out = []

    def walk(n, key=""):
        if isinstance(n, str) and key not in ("when",):
            out.append(re.sub(r"\{[^}]+\}", "x", n))  # placeholders count as one word
        elif isinstance(n, dict):
            for k, v in n.items():
                if k != "meta":
                    walk(v, k)
        elif isinstance(n, list):
            for v in n:
                walk(v, key)
    walk(doc)
    return out


def layer_texts(js: str) -> list[str]:
    block = js[js.index("export const LAYER_INFO"):js.index("export const OVERLAY_INFO")]
    return re.findall(r'text: "([^"]+)"', block)


def main():
    groups = {
        "plain_language.yaml (ohne Datenbeschreibung)": (yaml_texts(git_show("config/plain_language.yaml")),
                                                       yaml_texts((ROOT / "config/plain_language.yaml").read_text(encoding="utf-8"))),
        "Erklärsätze der Kartenansichten (layers.js)": (layer_texts(git_show("web/src/layers.js")),
                                                       layer_texts((ROOT / "web/src/layers.js").read_text(encoding="utf-8"))),
    }
    res = {}
    for name, (before, after) in groups.items():
        b, a = "\n".join(before), "\n".join(after)
        res[name] = {"before": measure(b), "after": measure(a),
                     "terms_before": sum(term_hits(b).values()), "terms_after": sum(term_hits(a).values())}
    (ROOT / "data/scenarios/redesign/p2_readability.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    for name, r in res.items():
        print(f"{name}: WSTF {r['before'].get('wstf')} -> {r['after'].get('wstf')}, FRE {r['before'].get('fre_amstad')} -> "
              f"{r['after'].get('fre_amstad')}, Ø Satz {r['before'].get('mean_sentence_words')} -> {r['after'].get('mean_sentence_words')}, "
              f"Fachbegriffe/Kürzel {r['terms_before']} -> {r['terms_after']}")


if __name__ == "__main__":
    main()
