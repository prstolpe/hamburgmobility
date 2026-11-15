"""Rule inventory for the redesign (prompt 24, A1.5): one row per rule id in the three rule files with
purpose, inputs, how often the rule fires and decides the outcome in the current run, overlaps, tests and
a candidate action.

Measures come from the traces in data/interim (current run). "Decides" is defined per domain:
- classification cascade: last C-* step of final.rule_path; H-STR-01 when it is in rule_path
- coherence: N1–N5 only set flags or proposals (the N2 smoothing proposal, formerly N7, is applied only via overrides)
- junctions: junctions.decision_rule; JC-* from junctions.cyclist_treatment
- cycle facility: last step in rule_trace_facility whose result equals cycle_facility_soll
- cycle network: last C-NET step whose result equals cycle_cat_proposed
- soll cross-section: lane rules = last L-* step with a result; degrade steps D1–D7 = applied
- discrepancy: rule whose result equals disc_max (> 0)
Everything else (features, conflation, graph, demand, impedance, principles, validation) is a preprocessing
or check step: it fires but does not decide a category, facility or junction type on its own.

Candidate actions are curated by hand in analysis/redesign/rule_candidates.yaml; rules without an entry are "keep".

Usage: uv run python -m analysis.redesign.rule_inventory
Writes data/scenarios/redesign/rule_usage.csv and docs/redesign/01_rules_inventory.csv.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd
import yaml

from analysis.review_2026_11.rule_inventory import RULE_FILES, texts, walk_ids

ROOT = Path(__file__).resolve().parents[2]
INTERIM = ROOT / "data/interim"
OUT_DATA = ROOT / "data/scenarios/redesign"
OUT_DOC = ROOT / "docs/redesign"
TEXT_KEYS = ["description", "rule", "check", "metric", "principle", "note", "label_de"]
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")
EXPR_WORDS = {"and", "or", "not", "in", "true", "false", "null", "is", "none", "True", "False", "None"}


def load(name, cols):
    return pd.read_parquet(INTERIM / f"{name}.parquet", columns=cols)


def parse(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return []
    v = json.loads(x) if isinstance(x, str) else x
    return v if isinstance(v, list) else [v]


class Usage:
    """fired/decided counts and km per rule id, plus the set of object keys it fired on (for overlaps)."""

    def __init__(self):
        self.fired_n = defaultdict(int)
        self.fired_km = defaultdict(float)
        self.dec_n = defaultdict(int)
        self.dec_km = defaultdict(float)
        self.unit = {}
        self.measure = {}
        self.keys = defaultdict(set)
        self.inputs = defaultdict(set)
        self.domain = {}
        self.current = None

    def fire(self, rid, key, km, unit, inputs=None):
        self.fired_n[rid] += 1
        self.fired_km[rid] += km or 0.0
        self.unit.setdefault(rid, unit)
        self.domain.setdefault(rid, self.current)
        self.keys[rid].add(key)
        if isinstance(inputs, dict):
            self.inputs[rid].update(inputs.keys())

    def decide(self, rid, km, measure):
        self.dec_n[rid] += 1
        self.dec_km[rid] += km or 0.0
        self.measure.setdefault(rid, measure)


def collect() -> Usage:
    u = Usage()

    u.current = "final"
    f = load("final", ["segment_id", "length_m", "rule_path", "rule_trace", "coherence_trace", "feature_trace",
                       "crosssection_trace", "conflation_trace", "split_rule", "confidence_reasons"])
    for sid, km, path, tr, coh, feat, xs, conf, split, reasons in zip(
            f.segment_id, f.length_m / 1000, f.rule_path, f.rule_trace, f.coherence_trace, f.feature_trace,
            f.crosssection_trace, f.conflation_trace, f.split_rule, f.confidence_reasons):
        for e in parse(tr):
            if e.get("passed"):
                u.fire(e["id"], sid, km, "Abschnitte", e.get("inputs"))
            elif e.get("inputs"):
                u.inputs[e["id"]].update(e["inputs"].keys())
        if isinstance(path, str):
            steps = [s.strip() for s in path.split("→")]
            cascade = [s for s in steps if s.startswith("C-")]
            if cascade:
                u.decide(cascade[-1], km, "letzte Kaskadenstufe in rule_path")
            if "H-STR-01" in steps:
                u.decide("H-STR-01", km, "Angleichung im rule_path")
        for e in parse(coh):
            u.fire(e["id"], sid, km, "Abschnitte", e.get("inputs"))
        for col in (feat, xs):
            for e in parse(col):
                u.fire(e["id"], sid, km, "Abschnitte", e.get("inputs"))
        for e in parse(conf):
            if e.get("n_passed"):
                u.fire(e["rule"], sid, km, "Abschnitte")
        if isinstance(split, str):
            u.fire(split, sid, km, "Abschnitte")
        rs = parse(reasons)
        if any(r.startswith(("fallback:", "fehlt:")) for r in rs):
            u.fire("C-MISS-01", sid, km, "Abschnitte")
        if rs:
            u.fire("C-CONF-01", sid, km, "Abschnitte")

    u.current = "discrepancy"
    d = load("discrepancy", ["segment_id", "length_m", "disc_max", "disc_trace"])
    for sid, km, dmax, tr in zip(d.segment_id, d.length_m / 1000, d.disc_max, d.disc_trace):
        for e in parse(tr):
            r = e.get("result")
            if r not in (None, 0, False):
                u.fire(e["rule"], sid, km, "Abschnitte", e.get("inputs"))
                if e["rule"].startswith("D-") and e["rule"] != "D-TYPE-01" and dmax and r == dmax:
                    u.decide(e["rule"], km, "Ergebnis = disc_max")

    u.current = "junctions"
    j = load("junctions", ["node_id", "decision_rule", "cyclist_treatment", "rule_trace_junction"])
    for nid, rule, treat, tr in zip(j.node_id, j.decision_rule, j.cyclist_treatment, j.rule_trace_junction):
        for e in parse(tr):
            if e.get("passed"):
                u.fire(e["id"], nid, 0, "Knoten", e.get("values"))
        if isinstance(rule, str):
            u.decide(rule, 0, "decision_rule")
        if isinstance(treat, str):
            for t in treat.split("|"):
                u.fire(t, nid, 0, "Knoten")
                u.decide(t, 0, "cyclist_treatment")

    u.current = "cycle_facility"
    fac = load("cycle_facility", ["segment_id", "length_m", "cycle_facility_soll", "rule_trace_facility"])
    for sid, km, sol, tr in zip(fac.segment_id, fac.length_m / 1000, fac.cycle_facility_soll, fac.rule_trace_facility):
        last = None
        for e in parse(tr):
            if e.get("result") is not None:
                u.fire(e["id"], sid, km, "Abschnitte", e.get("values"))
                if e["result"] == sol:
                    last = e["id"]
        if last:
            u.decide(last, km, "letzte Stufe mit Ergebnis = Soll-Führungsform")

    u.current = "cross_section_soll"
    xs = load("cross_section_soll", ["segment_id", "length_m", "rule_trace_profile"])
    for sid, km, tr in zip(xs.segment_id, xs.length_m / 1000, xs.rule_trace_profile):
        last_lane = None
        for e in parse(tr):
            rid = e["id"]
            on = e.get("applied") if "applied" in e else e.get("result") not in (None, False)
            if on:
                u.fire(rid, sid, km, "Abschnitte", e.get("values"))
                if re.fullmatch(r"D\d", rid):
                    u.decide(rid, km, "Rückbauschritt angewendet")
                if rid.startswith("L-") and e.get("result") is not None:
                    last_lane = rid
        if last_lane:
            u.decide(last_lane, km, "letzte Fahrstreifenregel mit Ergebnis")

    u.current = "cycle_facility"
    ist = load("ist_facility", ["segment_id", "rule_trace_ist"])
    km_of = dict(zip(fac.segment_id, fac.length_m / 1000))
    for sid, tr in zip(ist.segment_id, ist.rule_trace_ist):
        for e in parse(tr):
            if e.get("result") is not None:
                u.fire(e["id"], sid, km_of.get(sid, 0.0), "Abschnitte", e.get("values"))

    u.current = "cycle_network"
    cn = load("cycle_network", ["edge_id", "length_m", "cycle_cat_proposed", "rule_trace_cycle", "impedance_trace",
                                "demand_trace"])
    for eid, km, cat, tr, imp, dem in zip(cn.edge_id, cn.length_m / 1000, cn.cycle_cat_proposed, cn.rule_trace_cycle,
                                          cn.impedance_trace, cn.demand_trace):
        last = None
        for e in parse(tr):
            if e.get("result") is not None:
                u.fire(e["rule"], eid, km, "Kanten", e.get("values"))
                if e["result"] == cat:
                    last = e["rule"]
        if last:
            u.decide(last, km, "letzte Stufe mit Ergebnis = Radnetzkategorie")
        for col in (imp, dem):
            for e in parse(col):
                for rid in e.get("rules", []):
                    u.fire(rid, eid, km, "Kanten", e.get("inputs"))

    u.current = "cycle_principles"
    pr = load("cycle_principles", ["id", "length_m", "rule_trace_principles"])
    for pid, km, tr in zip(pr["id"], pr.length_m / 1000, pr.rule_trace_principles):
        for e in parse(tr):
            if e.get("result") is not None:
                u.fire(e["rule"], pid, km, "Routen/Abschnitte", e.get("values") if isinstance(e.get("values"), dict) else None)
    return u


def rule_meta():
    """id -> file, path, status, source_type, text, if-expression inputs, raw entry."""
    rows, raw = [], {}

    def grab(node):
        if isinstance(node, dict):
            if isinstance(node.get("id"), str):
                raw[node["id"]] = node
            for v in node.values():
                grab(v)
        elif isinstance(node, list):
            for v in node:
                grab(v)

    for f in RULE_FILES:
        doc = yaml.safe_load((ROOT / f).read_text(encoding="utf-8"))
        found = []
        walk_ids(doc, "", found, {})
        for r in found:
            r["file"] = f.removeprefix("config/")
        rows += found
        grab(doc)
    for r in rows:
        node = raw[r["id"]]
        text = next((str(node[k]) for k in TEXT_KEYS if isinstance(node.get(k), str)), "")
        r["text"] = " ".join(text.split())
        expr = " ".join(str(node.get(k, "")) for k in ("if", "when", "condition"))
        r["expr_inputs"] = sorted({w for w in WORD.findall(expr) if w not in EXPR_WORDS
                                   and not w.startswith(("thresholds.", "required_width."))})
    return pd.DataFrame(rows), raw


def first_sentence(t: str) -> str:
    m = re.match(r"(.+?[.!?])(\s|$)", t)
    s = m.group(1) if m else t
    return s[:220]


def golden_counts():
    """rule id -> number of golden cases listing it in expected_rules."""
    cnt = defaultdict(int)
    for p in ROOT.glob("tests/golden/**/*.geojson"):
        gj = json.loads(p.read_text(encoding="utf-8"))
        for feat in gj.get("features", [gj]):
            for rid in (feat.get("properties") or {}).get("expected_rules", []) or []:
                cnt[rid] += 1
    return cnt


def overlaps(u: Usage, ids):
    """Pairs of deciding rules of the same unit whose fired sets overlap strongly (Jaccard ≥ 0.8 or containment
    ≥ 0.95). Steps that run on every object (preprocessing) are left out: they overlap with everything."""
    out = defaultdict(list)
    size = defaultdict(int)
    for i in ids:
        size[u.domain.get(i)] = max(size[u.domain.get(i)], len(u.keys.get(i, ())))
    ids = [i for i in ids if 20 <= len(u.keys.get(i, ())) < 0.9 * size[u.domain.get(i)] and u.dec_n.get(i)]
    for a_i, a in enumerate(ids):
        for b in ids[a_i + 1:]:
            if u.domain.get(a) != u.domain.get(b):
                continue
            ka, kb = u.keys[a], u.keys[b]
            inter = len(ka & kb)
            if not inter:
                continue
            jac = inter / len(ka | kb)
            cont = inter / min(len(ka), len(kb))
            if jac >= 0.8 or cont >= 0.95:
                out[a].append(f"{b} (J {jac:.2f}, ⊂ {cont:.2f})")
                out[b].append(f"{a} (J {jac:.2f}, ⊂ {cont:.2f})")
    return out


def main():
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_DOC.mkdir(parents=True, exist_ok=True)
    meta, raw = rule_meta()
    u = collect()
    gold = golden_counts()
    tests = texts(["tests/*.py"])
    cands = yaml.safe_load((ROOT / "analysis/redesign/rule_candidates.yaml").read_text(encoding="utf-8")) or {}
    plain = {}
    plain_path = ROOT / "analysis/redesign/rule_plain.yaml"
    if plain_path.exists():
        plain = yaml.safe_load(plain_path.read_text(encoding="utf-8")) or {}
    ov = overlaps(u, list(meta.id))

    rows = []
    for _, r in meta.iterrows():
        rid = r.id
        pat = re.compile(rf"(?<![A-Za-z0-9-]){re.escape(rid)}(?![A-Za-z0-9])")
        tfiles = sorted(p.name for p, t in tests.items() if pat.search(t))
        inputs = sorted(set(r.expr_inputs) | u.inputs.get(rid, set()))
        c = cands.get(rid, {})
        p = plain.get(rid, {})
        rows.append({
            "id": rid, "file": r.file, "path": r.path, "status": r.status, "source_type": r.source_type,
            "purpose": p.get("explain_plain") or first_sentence(r.text),
            "purpose_source": "rule_plain.yaml" if p.get("explain_plain") else "Regeldatei (erster Satz)",
            "inputs": ", ".join(inputs[:12]) + (" …" if len(inputs) > 12 else ""),
            "unit": u.unit.get(rid, ""),
            "fired_n": u.fired_n.get(rid, 0), "fired_km": round(u.fired_km.get(rid, 0.0), 1),
            "decides_n": u.dec_n.get(rid, 0), "decides_km": round(u.dec_km.get(rid, 0.0), 1),
            "decides_measure": u.measure.get(rid, ""),
            "overlaps": "; ".join(ov.get(rid, [])),
            "golden_cases": gold.get(rid, 0), "test_files": ", ".join(tfiles),
            "action": c.get("action", "keep"), "reason": c.get("reason", ""),
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DATA / "rule_usage.csv", index=False)
    df.to_csv(OUT_DOC / "01_rules_inventory.csv", index=False)
    print(df.groupby(["file", "action"]).size().unstack(fill_value=0))
    print(f"{len(df)} rules; never fired: {(df.fired_n == 0).sum()}; decides something: {(df.decides_n > 0).sum()}")


if __name__ == "__main__":
    main()
