"""Rule-file language check (prompt 24, A1.4): for every rule, category and threshold, would a non-expert understand
the label and the explanation?

Verdict per item (documented criteria, applied mechanically; examples checked by hand in 01_inventory.md):
- rules: main text = first of description/rule/check/metric/principle/note.
  Failures counted: (a) no text at all, (b) code in the text (snake_case names, dotted keys, comparison operators,
  formula letters such as T_ij), (c) more than one technical term or abbreviation from readability.TERMS/rule IDs,
  (d) mean sentence length over 15 words, (e) long-noun share over 10 %.
  ja = no failure; teilweise = 1–2 failures; nein = no text, or 3 and more failures.
  The label of a rule is its ID (e.g. C-G30-02): never understandable without explanation, so label_ok is always false.
- categories (rules.yaml categories.*): label_de and the text in plain_language.yaml categories.
- thresholds (every mapping with `value` below a key named thresholds or an *_m/_kmh/_dtv/_share style key):
  name is an English key (never understandable); verdict ja if a German note/unit explains it, else nein.

Usage: uv run --with textstat --with pyphen python -m analysis.redesign.rule_language
Writes data/scenarios/redesign/rule_language.csv and prints counts.
"""

import json
import re
from pathlib import Path

import pandas as pd
import yaml

from analysis.redesign.readability import measure, term_hits
from analysis.redesign.rule_inventory import rule_meta

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/scenarios/redesign"
CODE = re.compile(r"\b[a-z]+_[a-z0-9_]+\b|\b[a-z_]+\.[a-z_]+\b|<=|>=|==|!=|\b[A-Z]_[a-z]{1,3}\b")
MAIN_KEYS = ["description", "rule", "check", "metric", "principle", "note"]
COMMON_TERMS = {"Soll", "Ist", "Abschnitt", "Kfz", "Schwelle", "Annahme", "Ebene", "Priorität"}


def verdict_text(text: str) -> tuple[str, list[str], dict]:
    if not text:
        return "nein", ["kein Text"], {}
    m = measure(text)
    fails = []
    code = CODE.findall(text)
    if code:
        fails.append(f"Code im Text ({', '.join(sorted(set(code))[:4])})")
    terms = {t: n for t, n in term_hits(text).items() if t not in COMMON_TERMS}
    if len(terms) > 1:
        fails.append(f"{len(terms)} Fachbegriffe/Kürzel ({', '.join(list(terms)[:4])})")
    if (m.get("mean_sentence_words") or 0) > 15:
        fails.append(f"Sätze im Mittel {m['mean_sentence_words']} Wörter")
    if (m.get("long_noun_share") or 0) > 0.10:
        fails.append(f"{round(m['long_noun_share'] * 100)} % lange Substantive")
    v = "ja" if not fails else ("teilweise" if len(fails) <= 2 else "nein")
    return v, fails, m


def thresholds(doc, file):
    out = []

    def walk(n, path, under_thr):
        if isinstance(n, dict):
            if "value" in n and under_thr:
                note = " ".join(str(n.get(k, "")) for k in ("note", "unit")).strip()
                out.append({"kind": "Schwelle", "file": file, "item": path, "label": path.rsplit(".", 1)[-1],
                            "text": note, "verdict": "teilweise" if note else "nein",
                            "fails": "englischer Schlüssel" + ("" if note else "; keine Erklärung")})
                return
            for k, v in n.items():
                walk(v, f"{path}.{k}" if path else k, under_thr or k == "thresholds")
        elif isinstance(n, list):
            for i, v in enumerate(n):
                walk(v, f"{path}[{i}]", under_thr)
    walk(doc, "", False)
    return out


def main():
    rows = []
    meta, raw = rule_meta()
    for _, r in meta.iterrows():
        node = raw[r.id]
        text = next((" ".join(str(node[k]).split()) for k in MAIN_KEYS if isinstance(node.get(k), str)), "")
        v, fails, m = verdict_text(text)
        rows.append({"kind": "Regel", "file": r.file, "item": r.id, "label": r.id, "text": text, "verdict": v,
                     "fails": "; ".join(["Bezeichnung ist nur die ID"] + fails), "wstf": m.get("wstf"),
                     "mean_sentence_words": m.get("mean_sentence_words")})
    rules = yaml.safe_load((ROOT / "config/rules.yaml").read_text(encoding="utf-8"))
    pl = yaml.safe_load((ROOT / "config/plain_language.yaml").read_text(encoding="utf-8"))
    for cat, c in (rules.get("categories") or {}).items():
        label = c.get("label_de", "")
        text = pl.get("categories", {}).get(cat, "")
        v, fails, m = verdict_text(text)
        if not label:
            fails = ["kein label_de"] + fails
        rows.append({"kind": "Kategorie", "file": "rules.yaml", "item": cat, "label": label, "text": text, "verdict": v,
                     "fails": "; ".join(fails), "wstf": m.get("wstf"), "mean_sentence_words": m.get("mean_sentence_words")})
    for f in ["rules.yaml", "cycling_rules.yaml", "design_rules.yaml"]:
        rows += thresholds(yaml.safe_load((ROOT / "config" / f).read_text(encoding="utf-8")), f)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "rule_language.csv", index=False)
    print(df.groupby(["kind", "verdict"]).size().unstack(fill_value=0))
    print(df[df.kind == "Regel"].groupby(["file", "verdict"]).size().unstack(fill_value=0))
    fails = df[df.kind == "Regel"].fails.str.split("; ").explode().str.replace(r" \(.*", "", regex=True)
    print(fails.str.replace(r"^\d+ % ", "", regex=True).str.replace(r"\d+(\.\d)? Wörter", "> 15 Wörter", regex=True)
          .str.replace(r"^\d+ Fach", "n Fach", regex=True).value_counts())
    (OUT / "rule_language_summary.json").write_text(json.dumps(
        df.groupby(["kind", "verdict"]).size().unstack(fill_value=0).to_dict(orient="index"), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
