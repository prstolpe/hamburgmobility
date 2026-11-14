"""Rule reference for the method page (redesign 2026-11, package 3, decisions E2/E5).

Generated from the three rule files, so the website explains every rule with the text of the rule file itself
(label_plain, explain_plain, why) and shows the technical fields, thresholds and sources on demand. Each rule is put
into one chapter of the method page by the section it stands in (plain_language.yaml method.chapters[].sections).
`decides` counts how often a rule made the decision in the current run (same reading of the traces as
analysis/redesign/rule_inventory.py, limited to the decisions shown on the website).
"""

import json
from pathlib import Path

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RULE_FILES = ["rules.yaml", "cycling_rules.yaml", "design_rules.yaml"]
META_KEYS = {"id", "label_plain", "explain_plain", "why", "history", "source", "source_type", "status", "thresholds",
             "description", "note"}
VAR_NAMES = ["area_label", "n_rules", "n_rules_assumption", "n_thresholds", "n_thresholds_assumption", "mc_runs",
             "mc_delta_pct", "mc_min_change_pct", "n_junctions", "n_junctions_action", "cyc_sens_runs",
             "cyc_sens_delta_pct"]


def load_rule_docs(config_dir: Path = REPO_ROOT / "config") -> dict:
    return {f: yaml.safe_load((config_dir / f).read_text(encoding="utf-8")) for f in RULE_FILES}


def find_entry(node, rid: str):
    if isinstance(node, dict):
        if node.get("id") == rid:
            return node
        node = list(node.values())
    if isinstance(node, list):
        for v in node:
            if (hit := find_entry(v, rid)) is not None:
                return hit
    return None


def _has_id(v) -> bool:
    if isinstance(v, dict):
        return "id" in v or any(_has_id(x) for x in v.values())
    if isinstance(v, list):
        return any(_has_id(x) for x in v)
    return False


def _text(v) -> str:
    if isinstance(v, str):
        return " ".join(v.split())
    if isinstance(v, list) and all(not isinstance(x, (dict, list)) for x in v):
        return ", ".join(str(x) for x in v)
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, default=str)
    return str(v)


def _plain(v):
    return " ".join(v.split()) if isinstance(v, str) else v


def _sources(keys, catalogue: dict) -> list[dict]:
    keys = [keys] if isinstance(keys, str) else list(keys or [])
    return [{"key": k, **{f: _plain(str(x)) if f != "url" and x is not None else x
                          for f, x in (catalogue.get(k) or {}).items()}} for k in keys]


def _thresholds(entry: dict, source_type, key_labels: dict) -> list[dict]:
    out = []
    for key, t in (entry.get("thresholds") or {}).items():
        t = t if isinstance(t, dict) else {"value": t}
        out.append({"key": key, "label_plain": t.get("label_plain") or key_labels.get(key), "value": t.get("value"), "unit": t.get("unit"),
                    "source_type": t.get("source_type", source_type), "check": _plain(t.get("check")),
                    **({"values": _text({k: v for k, v in t.items() if k not in
                                         {"label_plain", "value", "unit", "source_type", "check", "source"}})}
                       if "value" not in t else {})})
    return out


def collect_rules(file: str, doc: dict, section_chapter: dict, key_labels: dict | None = None) -> list[dict]:
    """Every mapping with an `id` in file order; source/source_type are inherited from parents (as the schema does).

    key_labels: plain names for threshold keys without their own label_plain (per category, e.g. RSV -> Radvorrangroute).
    """
    catalogue = doc.get("sources") or {}
    out = []

    def walk(node, section, inherited):
        if isinstance(node, dict):
            inh = {**inherited, **{k: node[k] for k in ("source", "source_type") if k in node}}
            if isinstance(node.get("id"), str):
                sec = f"{file}:{section}"
                if sec not in section_chapter:
                    raise ValueError(f"{node['id']}: section {sec} has no chapter (plain_language.yaml method.chapters)")
                out.append({
                    "id": node["id"], "file": file, "section": section, "chapter": section_chapter[sec],
                    "label_plain": _plain(node.get("label_plain")), "explain_plain": _plain(node.get("explain_plain")),
                    "why": _plain(node.get("why")), "description": _plain(node.get("description")),
                    "note": _plain(node.get("note")), "history": node.get("history"),
                    "technical": [[k, _text(v)] for k, v in node.items() if k not in META_KEYS and not _has_id(v)],
                    "thresholds": _thresholds(node, inh.get("source_type"), key_labels or {}),
                    "source": _sources(inh.get("source"), catalogue), "source_type": inh.get("source_type"),
                    "status": node.get("status")})
            for k, v in node.items():
                walk(v, section or k, inh)
        elif isinstance(node, list):
            for v in node:
                walk(v, section, inherited)

    for k, v in doc.items():
        if k not in ("meta", "sources"):
            walk(v, k, {})
    return out


def rule_reference(docs: dict, chapters: list[dict], decides: dict, key_labels: dict | None = None) -> dict:
    section_chapter = {s: c["key"] for c in chapters for s in c["sections"]}
    rules = [r for f in RULE_FILES for r in collect_rules(f, docs[f], section_chapter, key_labels)]
    for r in rules:
        r["decides"] = decides.get(r["id"])
    return {"versions": {f: str(docs[f]["meta"]["version"]) for f in RULE_FILES}, "rules": rules}


def key_labels(glossary: dict) -> dict:
    """Plain names of road categories and cycle network levels (config/glossary.yaml) for threshold keys."""
    return {k: v["plain"] for sec in ("categories", "cycling") for k, v in (glossary.get(sec) or {}).items()
            if isinstance(v, dict) and v.get("plain")}


def counts(ref: dict) -> dict:
    rules = ref["rules"]
    th = [t for r in rules for t in r["thresholds"]]
    return {"n_rules": len(rules), "n_rules_assumption": sum(r["source_type"] == "assumption" for r in rules),
            "n_thresholds": len(th), "n_thresholds_assumption": sum(t["source_type"] == "assumption" for t in th)}


def method_vars(ref: dict, meta: dict) -> dict:
    """Values for the placeholders in plain_language.yaml method (numbers; the website formats them)."""
    sens = meta.get("sensitivity") or {}
    cyc = meta.get("cycling") or {}
    stats, csens = cyc.get("stats") or {}, cyc.get("sensitivity") or {}
    pct = lambda x: None if x is None else round(x * 100)  # noqa: E731
    return {"area_label": meta.get("area_label"), **counts(ref),
            "mc_runs": sens.get("runs"), "mc_delta_pct": pct(sens.get("delta")),
            "mc_min_change_pct": pct(sens.get("min_change_rate")),
            "n_junctions": stats.get("n_junctions"), "n_junctions_action": stats.get("n_junctions_action"),
            "cyc_sens_runs": csens.get("runs"), "cyc_sens_delta_pct": pct(csens.get("delta"))}


def _trace(x) -> list:
    if isinstance(x, str):
        return json.loads(x)
    return list(x) if x is not None and not (isinstance(x, float) and pd.isna(x)) else []


def decides(final: pd.DataFrame | None = None, junctions: pd.DataFrame | None = None,
            facility: pd.DataFrame | None = None, network: pd.DataFrame | None = None) -> dict:
    """rule id -> {n, km, unit}: how often the rule made the decision in this run.

    Category: last C-* step of rule_path, H-STR-01 when it is in rule_path. Junction type: decision_rule; cyclist
    treatment: each JC-* of cyclist_treatment. Cycle facility and cycle network category: last trace step whose result
    equals the final value.
    """
    acc: dict[str, dict] = {}

    def add(rid, km, unit):
        a = acc.setdefault(rid, {"n": 0, "km": None if km is None else 0.0, "unit": unit})
        a["n"] += 1
        if km is not None:
            a["km"] += km

    if final is not None:
        for path, m in zip(final["rule_path"], final["length_m"]):
            if not isinstance(path, str):
                continue
            steps = [s.strip() for s in path.split("→")]
            cascade = [s for s in steps if s.startswith("C-")]
            if cascade:
                add(cascade[-1], m / 1000, "Abschnitte")
            if "H-STR-01" in steps:
                add("H-STR-01", m / 1000, "Abschnitte")
    if junctions is not None:
        for rule, treat in zip(junctions["decision_rule"], junctions["cyclist_treatment"]):
            if isinstance(rule, str):
                add(rule, None, "Kreuzungen")
            if isinstance(treat, str):
                for t in treat.split("|"):
                    add(t, None, "Kreuzungen")
    for df, res_col, tr_col, key in ((facility, "cycle_facility_soll", "rule_trace_facility", "id"),
                                     (network, "cycle_cat_proposed", "rule_trace_cycle", "rule")):
        if df is None:
            continue
        for m, res, tr in zip(df["length_m"], df[res_col], df[tr_col]):
            last = None
            for e in _trace(tr):
                if e.get("result") is not None and e["result"] == res:
                    last = e.get(key)
            if last:
                add(last, m / 1000, "Abschnitte")
    for a in acc.values():
        if a["km"] is not None:
            a["km"] = round(a["km"], 3)
    return acc
