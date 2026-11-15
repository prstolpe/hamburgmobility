"""Rule reference for the method page (redesign 2026-11, package 3; pipeline/lib/export_rules.py).

The reference is generated from the three rule files, so the website explains each rule with the same text as the rule
file (decision E5 c). Every rule belongs to exactly one chapter of the method page (plain_language.yaml method.chapters).
"""

import json
import re

import pandas as pd
import pytest
import yaml

from pipeline.lib import export_rules as er
from pipeline.lib.export import load_texts

DOCS = er.load_rule_docs()
TEXTS = load_texts()
CHAPTERS = TEXTS["method"]["chapters"]


@pytest.fixture(scope="module")
def ref():
    return er.rule_reference(DOCS, CHAPTERS, decides={})


def test_every_rule_once_in_order(ref):
    ids = [r["id"] for r in ref["rules"]]
    assert len(ids) == len(set(ids)) == 190
    assert ids[:3] == ["C-SW-01", "C-RUR-01", "C-ERF-01"]


def test_every_rule_has_exactly_one_chapter(ref):
    keys = {c["key"] for c in CHAPTERS}
    assert all(r["chapter"] in keys for r in ref["rules"])
    # sections may not overlap and each listed section must exist
    secs = [s for c in CHAPTERS for s in c["sections"]]
    assert len(secs) == len(set(secs))
    present = {f"{r['file']}:{r['section']}" for r in ref["rules"]}
    assert set(secs) == present


def test_unmapped_section_raises():
    with pytest.raises(ValueError, match="no chapter"):
        er.rule_reference(DOCS, [{"key": "x", "sections": ["rules.yaml:classification"]}], decides={})


def test_plain_fields_come_from_the_rule_file(ref):
    r = next(r for r in ref["rules"] if r["id"] == "C-G30-02")
    raw = er.find_entry(DOCS["rules.yaml"], "C-G30-02")
    for k in ("label_plain", "explain_plain", "why", "description", "note", "history"):
        assert r[k] == (" ".join(raw[k].split()) if isinstance(raw[k], str) else raw[k])
    assert r["chapter"] == "aufgabe" and r["file"] == "rules.yaml" and r["section"] == "classification"
    assert r["status"] == "draft" and r["source_type"] == "swov_crow"
    assert ["if", raw["if"]] in r["technical"] and ["then", "GOW30"] in r["technical"]


def test_sources_resolve_in_their_own_file(ref):
    r = next(r for r in ref["rules"] if r["id"] == "C-G30-02")
    assert [s["key"] for s in r["source"]] == ["SWOV_FS_2023", "CROW_GOW30_2023"]
    assert r["source"][0]["title"] == DOCS["rules.yaml"]["sources"]["SWOV_FS_2023"]["title"]
    # SWOV_FS_2023 is defined differently in design_rules.yaml: a design rule must get that file's entry
    d = next(r for r in ref["rules"] if r["file"] == "design_rules.yaml"
             and any(s["key"] == "SWOV_FS_2023" for s in r["source"]))
    s = next(s for s in d["source"] if s["key"] == "SWOV_FS_2023")
    assert s["title"] == DOCS["design_rules.yaml"]["sources"]["SWOV_FS_2023"]["title"]


def test_source_and_source_type_are_inherited():
    doc = {"sources": {"A": {"title": "a"}}, "sec": {"source": "A", "source_type": "hamburg",
                                                      "items": [{"id": "X-1", "status": "draft"}]}}
    rules = er.collect_rules("f.yaml", doc, {"f.yaml:sec": "k"})
    assert rules[0]["source_type"] == "hamburg" and rules[0]["source"] == [{"key": "A", "title": "a"}]


def test_thresholds_with_plain_label(ref):
    r = next(r for r in ref["rules"] if r["id"] == "N1")
    t = next(t for t in r["thresholds"] if t["key"] == "boundary_tolerance_m")
    raw = er.find_entry(DOCS["rules.yaml"], "N1")["thresholds"]["boundary_tolerance_m"]
    assert t["value"] == raw["value"] and t["unit"] == raw["unit"] and t["label_plain"] == raw["label_plain"]
    assert t["source_type"]  # own or inherited from the rule


def test_threshold_keys_per_category_get_the_glossary_name():
    glossary = yaml.safe_load((er.REPO_ROOT / "config" / "glossary.yaml").read_text(encoding="utf-8"))
    ref = er.rule_reference(DOCS, CHAPTERS, decides={}, key_labels=er.key_labels(glossary))
    t = {x["key"]: x for r in ref["rules"] if r["id"] == "P-DIR-01" for x in r["thresholds"]}
    assert t["RSV"]["label_plain"] == glossary["cycling"]["RSV"]["plain"] and t["RSV"]["value"] == 1.1
    assert all(x["label_plain"] for r in ref["rules"] for x in r["thresholds"])


def test_technical_fields_leave_out_meta_and_nested_rules(ref):
    for r in ref["rules"]:
        keys = {k for k, _ in r["technical"]}
        assert not keys & {"id", "label_plain", "explain_plain", "why", "history", "source", "source_type", "status",
                           "thresholds", "description", "note"}, r["id"]
        assert all(isinstance(v, str) for _, v in r["technical"]), r["id"]
        assert not any(re.search(r"'id': ", v) for _, v in r["technical"]), r["id"]


def test_versions_and_counts(ref):
    assert ref["versions"]["rules.yaml"] == str(DOCS["rules.yaml"]["meta"]["version"])
    c = er.counts(ref)
    assert c["n_rules"] == 190
    assert c["n_rules_assumption"] == sum(r["source_type"] == "assumption" for r in ref["rules"])
    assert c["n_thresholds"] == sum(len(r["thresholds"]) for r in ref["rules"])
    assert 0 < c["n_thresholds_assumption"] <= c["n_thresholds"]


def test_json_serialisable(ref):
    json.dumps(ref, ensure_ascii=False)


# --- how often a rule decided in the current run ---------------------------------------------------------------------

def test_decides_classification_and_harmonisation():
    final = pd.DataFrame({"rule_path": ["C-SW-01", "C-GOW-01 → C-G30-02 → H-STR-01", "C-GOW-01 → C-G50-01", None],
                          "length_m": [1000.0, 500.0, 250.0, 100.0]})
    d = er.decides(final=final)
    assert d["C-SW-01"] == {"n": 1, "km": 1.0, "unit": "Abschnitte"}
    assert d["C-G30-02"]["km"] == 0.5 and d["H-STR-01"]["n"] == 1 and d["C-G50-01"]["km"] == 0.25
    assert "C-GOW-01" not in d  # only the last cascade step decides


def test_decides_junctions_and_cycling():
    j = pd.DataFrame({"decision_rule": ["J-01", "J-01", None], "cyclist_treatment": ["JC-01|JC-04", None, "JC-04"]})
    fac = pd.DataFrame({"length_m": [1000.0], "cycle_facility_soll": ["track"],
                        "rule_trace_facility": [json.dumps([{"id": "C-FAC-01", "result": "lane"},
                                                            {"id": "C-FAC-02", "result": "track"}])]})
    net = pd.DataFrame({"length_m": [2000.0], "cycle_cat_proposed": ["HAUPT"],
                        "rule_trace_cycle": [json.dumps([{"rule": "C-NET-03", "result": "HAUPT"},
                                                         {"rule": "C-NET-09", "result": None}])]})
    d = er.decides(junctions=j, facility=fac, network=net)
    assert d["J-01"] == {"n": 2, "km": None, "unit": "Kreuzungen"}
    assert d["JC-04"]["n"] == 2 and d["JC-01"]["n"] == 1
    assert d["C-FAC-02"] == {"n": 1, "km": 1.0, "unit": "Abschnitte"} and "C-FAC-01" not in d
    assert d["C-NET-03"]["km"] == 2.0 and "C-NET-09" not in d


def test_decides_attached_to_rules():
    ref = er.rule_reference(DOCS, CHAPTERS, decides={"C-SW-01": {"n": 3, "km": 1.5, "unit": "Abschnitte"}})
    by = {r["id"]: r for r in ref["rules"]}
    assert by["C-SW-01"]["decides"]["n"] == 3 and by["C-RUR-01"]["decides"] is None


# --- texts of the method page ----------------------------------------------------------------------------------------

def test_method_texts_use_only_known_placeholders():
    used = set(re.findall(r"\{(\w+)\}", yaml.safe_dump(TEXTS["method"], allow_unicode=True)))
    assert used <= set(er.VAR_NAMES)


def test_method_vars():
    ref = er.rule_reference(DOCS, CHAPTERS, decides={})
    meta = {"area_label": "Hamburg", "sensitivity": {"runs": 500, "delta": 0.2, "min_change_rate": 0.3},
            "cycling": {"stats": {"n_junctions": 10, "n_junctions_action": 4}, "sensitivity": {"runs": 30, "delta": 0.2}}}
    v = er.method_vars(ref, meta)
    assert set(v) == set(er.VAR_NAMES)
    assert v["mc_runs"] == 500 and v["mc_delta_pct"] == 20 and v["mc_min_change_pct"] == 30
    assert v["n_junctions_action"] == 4 and v["cyc_sens_delta_pct"] == 20 and v["n_rules"] == 190
    assert er.method_vars(ref, {"area_label": "Hamburg", "sensitivity": None, "cycling": None})["mc_runs"] is None
