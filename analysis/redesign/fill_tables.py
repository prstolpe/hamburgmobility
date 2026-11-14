"""Fill generated tables into the redesign documents (prompt 24). A document contains markers
    <!-- table:NAME -->
    ...generated content...
    <!-- /table:NAME -->
and this script replaces the content between them, so prose is written once by hand and every number comes from the
analysis outputs in data/scenarios/redesign/.

Usage: uv run --with textstat --with pyphen python -m analysis.redesign.fill_tables docs/redesign/01_inventory.md [...]
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd

from analysis.review_2026_11.common import fmt

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/scenarios/redesign"
UI = DATA / "ui"

PAGE_INFO = {  # what it shows / explains / for whom (hand-written from the screenshots and the source in web/src)
    "karte": ("Karte mit Bedienfeld (Ebenen, Legende, Zusatzebenen, Filter)", "Ein Satz je Ebene, Legende",
              "alle; Einstieg"),
    "tabelle": ("Bezirksauswahl, dann alle Abschnitte des Bezirks nach Priorität", "ein Satz", "Fachleute, Politik"),
    "methode": ("Kategorien, Kaskade, Unsicherheit, Diskrepanz, Grenzen, Änderungen", "Methode der Straßenfunktion",
                "Interessierte, Fachleute"),
    "radnetz": ("Prinzipien, Ebenen, Radanlage, Querschnitt, Knoten, Grenzen", "Methode Radnetz",
                "Interessierte, Fachleute"),
    "downloads": ("Tabelle der Dateien mit Format, Größe, Lizenz", "kurz je Datei", "Fachleute, Datennutzer"),
    "quellen": ("Datenquellen, Hintergrundkarte, Lizenzen, Quellenvermerke", "Lizenzen", "Datennutzer, rechtlich"),
    "impressum": ("Verantwortlich, Datenschutz", "rechtlich", "rechtlich"),
}


def cell(x):
    return "–" if x is None or (isinstance(x, float) and pd.isna(x)) else (fmt(x, 1) if isinstance(x, float) else str(x))


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(cell(v) for v in r) + " |" for r in rows]
    return "\n".join(out)


def top_terms(texts, n=6):
    from analysis.redesign.readability import term_hits
    agg = {}
    for t in texts:
        for k, v in term_hits(t).items():
            if k not in ("Soll", "Ist", "Abschnitt"):
                agg[k] = agg.get(k, 0) + v
    return ", ".join(k.replace("Regel-ID ", "") for k, _ in sorted(agg.items(), key=lambda x: -x[1])[:n]) or "–"


def t_pages():
    from analysis.redesign.readability import measure
    c = json.loads((UI / "content.json").read_text(encoding="utf-8"))
    rows = []
    for p, v in c["pages"].items():
        text = "\n".join(s["text"] for s in v["sections"])
        m = measure(text)
        shows, explains, who = PAGE_INFO[p]
        rows.append([f"[{p}]({v['image']})", shows, explains, who, v["words"], m.get("wstf"), m.get("fre_amstad"),
                     fmt(v.get("page_height_mobile"), 0) + " px", top_terms([text])])
    return table(["Seite", "zeigt", "erklärt", "für wen", "Wörter", "WSTF", "FRE", "Höhe mobil", "häufigste Fachbegriffe"], rows)


def t_layers():
    c = json.loads((UI / "content.json").read_text(encoding="utf-8"))
    rows = []
    for l, v in c["layers"].items():
        rows.append([f"[{v['title']}]({v['image']})", l, v["text"], len(v["legend"]), v["words"],
                     "ja" if v["legend_top_px"] < 900 else "nein", "ja" if v["legend_visible_mobile"] else "nein",
                     top_terms([v["text"], *v["legend"], *v["notes"]], 4)])
    return table(["Ebene", "Schlüssel", "Erklärsatz", "Legendeneinträge", "Wörter", "Legende sichtbar (Desktop)",
                  "Legende sichtbar (mobil, ohne Scrollen)", "Fachbegriffe"], rows)


def t_profiles():
    c = json.loads((UI / "content.json").read_text(encoding="utf-8"))
    from analysis.redesign.readability import measure
    rows = []
    for cat, v in c["profiles"].items():
        text = "\n".join(s["text"] for s in v["sections"])
        m = measure(text)
        rows.append([f"[{cat}]({v['image']})", v["name"], len(v["sections"]), v["words"],
                     fmt(v["panel_height_px"], 0) + " px", fmt(v["panel_height_mobile"], 0) + " px", m.get("wstf"),
                     m.get("fre_amstad"), top_terms([text])])
    j = c["junction"]
    text = "\n".join(s["text"] for s in j["sections"])
    m = measure(text)
    rows.append([f"[Knoten]({j['image']})", j["title"], len(j["sections"]), j["words"], "–", "–", m.get("wstf"),
                 m.get("fre_amstad"), top_terms([text])])
    return table(["Steckbrief", "Beispiel", "Abschnitte", "Wörter", "Länge Desktop", "Länge mobil", "WSTF", "FRE",
                  "Fachbegriffe"], rows)


def t_profile_sections():
    c = json.loads((UI / "content.json").read_text(encoding="utf-8"))
    heads = {}
    for cat, v in c["profiles"].items():
        for s in v["sections"]:
            heads.setdefault(s["heading"] if not s["heading"].startswith(v["name"]) else "(Titel)", {})[cat] = s["words"]
    cats = list(c["profiles"])
    return table(["Abschnitt im Steckbrief", *cats], [[h, *[d.get(k, "–") for k in cats]] for h, d in heads.items()])


def t_tasks():
    t = json.loads((UI / "tasks.json").read_text(encoding="utf-8"))
    names = {"t1": "Was ist für meine Straße geplant, und warum?", "t2": "Passt der geplante Querschnitt in die Straße?",
             "t3": "Wo hat mein Bezirk den größten Handlungsbedarf?", "t4": "Wie sieht das Radnetz aus, wo sind Lücken?",
             "t5": "Was ändert sich an diesem Knotenpunkt?"}
    rows = []
    for r in t["results"]:
        rows.append([r["task"], names[r["task"]], r["device"], r["steps"], r["clicks"], r["keystrokes"], r["scrolls"],
                     r["words_read"], r["seconds"], len(r["errors"])])
    return table(["Aufgabe", "Frage", "Gerät", "Schritte", "Klicks", "Tasten", "Scrollen", "Wörter gelesen",
                  "Zeit (KLM, s)", "JS-Fehler"], rows)


def t_task_paths():
    from analysis.redesign.readability import term_hits
    t = json.loads((UI / "tasks.json").read_text(encoding="utf-8"))
    out = []
    for r in t["results"]:
        if r["device"] != "desktop":
            continue
        mob = next(x for x in t["results"] if x["task"] == r["task"] and x["device"] == "mobile")
        out.append(f"**{r['task']}** – Klickpfad (Desktop):")
        for s in r["path"]:
            ms = next((x for x in mob["path"] if x["n"] == s["n"]), None)
            img = f" ([Desktop]({s['image']})" + (f", [mobil]({ms['image']})" if ms and ms.get("image") else "") + ")" if s.get("image") else ""
            out.append(f"{s['n']}. {s['desc']}{img}")
        terms = {}
        for s in r["path"]:
            for k, v in term_hits(s.get("text") or "").items():
                if k not in ("Abschnitt",):
                    terms[k.replace("Regel-ID ", "")] = terms.get(k.replace("Regel-ID ", ""), 0) + v
        if terms:
            out.append("")
            out.append("Wörter, die das Verständnis blockieren (im gelesenen Text, Anzahl): "
                       + ", ".join(f"{k} ({v})" for k, v in sorted(terms.items(), key=lambda x: -x[1])))
        notes = list(dict.fromkeys(r["notes"] + mob["notes"]))
        if notes:
            out.append("")
            out.append("Hänger:")
            out += [f"- {n}" for n in notes]
        out.append("")
    return "\n".join(out).rstrip()


def t_readability():
    s = json.loads((DATA / "readability_summary.json").read_text(encoding="utf-8"))
    rows = []
    for k, v in s["by_group"].items():
        pct = lambda x: "–" if x is None else f"{round(x * 100)} %"
        rows.append([k.replace(" | ", ": "), v["units"], v.get("words"), pct(v.get("label_share")), v.get("sentences"),
                     v.get("wstf"), v.get("fre_amstad"), v.get("mean_sentence_words"),
                     pct(v.get("share_sentences_over_15")), pct(v.get("passive_share")), pct(v.get("long_noun_share"))])
    return table(["Quelle: Gruppe", "Einheiten", "Wörter", "Anteil Stichwörter", "Sätze", "WSTF", "FRE (Amstad)",
                  "Ø Satzlänge", "Anteil Sätze > 15 W.", "Anteil Passiv", "Anteil lange Subst."], rows)


def t_terms():
    d = pd.read_csv(DATA / "readability_terms.csv")
    d = d[~d.term.str.startswith("Regel-ID")].head(60)
    return table(["Begriff", "Vorkommen", "Orte", "wo"], d[["term", "count", "n_places", "where"]].values.tolist())


def t_rule_ids_on_site():
    d = pd.read_csv(DATA / "readability_terms.csv")
    d = d[d.term.str.startswith("Regel-ID") & d["where"].str.contains("Webseite")]
    return f"{len(d)} verschiedene Regel-IDs (ohne die Diskrepanztypen D1–D3) erscheinen in den erfassten Webseitentexten: " + \
        ", ".join(f"{t.removeprefix('Regel-ID ')} ({c})" for t, c in zip(d.term, d["count"])) + "."


def t_rule_language():
    d = pd.read_csv(DATA / "rule_language.csv")
    piv = d.groupby(["kind", "verdict"]).size().unstack(fill_value=0)
    rows = [[k, *[int(piv.loc[k].get(v, 0)) for v in ("ja", "teilweise", "nein")], int(piv.loc[k].sum())] for k in piv.index]
    by_file = d[d.kind == "Regel"].groupby(["file", "verdict"]).size().unstack(fill_value=0)
    rows += [[f"Regel – {f}", *[int(by_file.loc[f].get(v, 0)) for v in ("ja", "teilweise", "nein")],
              int(by_file.loc[f].sum())] for f in by_file.index]
    return table(["Art", "verständlich: ja", "teilweise", "nein", "gesamt"], rows)


def t_rule_language_examples():
    d = pd.read_csv(DATA / "rule_language.csv")
    d = d[d.kind == "Regel"]
    rows = []
    for v in ("ja", "teilweise", "nein"):
        for _, r in d[d.verdict == v].head(4).iterrows():
            rows.append([r["item"], v, (r["text"] if isinstance(r["text"], str) else "")[:140], r["fails"]])
    return table(["Regel", "Urteil", "Text (Anfang)", "Gründe"], rows)


def t_rules_summary():
    d = pd.read_csv(DATA / "rule_usage.csv")
    rows = []
    for f, g in d.groupby("file"):
        rows.append([f, len(g), int((g.status == "inactive").sum()), int((g.fired_n == 0).sum()),
                     int((g.decides_n > 0).sum()), int(((g.golden_cases == 0) & g.test_files.isna()).sum()),
                     int((g.source_type == "assumption").sum()),
                     ", ".join(f"{a} {n}" for a, n in g.action.value_counts().items())])
    return table(["Datei", "Regeln", "inaktiv", "greift im Lauf nie", "entscheidet etwas", "ohne Test", "assumption",
                  "Vorschlag"], rows)


def t_rules_candidates():
    d = pd.read_csv(DATA / "rule_usage.csv")
    d = d[d.action != "keep"]
    rows = [[r.id, r.action, r.unit if isinstance(r.unit, str) else "–", r.fired_n, r.decides_n, r.decides_km,
             r.golden_cases, r.source_type, r.reason] for r in d.itertuples()]
    return table(["Regel", "Vorschlag", "Einheit", "greift", "entscheidet", "km entschieden", "goldene Fälle",
                  "source_type", "Begründung"], rows)


def t_rules_never():
    d = pd.read_csv(DATA / "rule_usage.csv")
    d = d[d.fired_n == 0]
    groups = d.groupby(d.id.str.extract(r"^([A-Z]+(?:-[A-Z]+)?)")[0]).id.apply(lambda s: ", ".join(s))
    return "\n".join(f"- **{k}**: {v}" for k, v in groups.items())


TABLES = {n.removeprefix("t_"): f for n, f in globals().items() if n.startswith("t_") and callable(f)}


def fill(path: Path):
    text = path.read_text(encoding="utf-8")

    def rep(m):
        name = m.group(1)
        return f"<!-- table:{name} -->\n{TABLES[name]()}\n<!-- /table:{name} -->"
    new = re.sub(r"<!-- table:(\w+) -->.*?<!-- /table:\1 -->", rep, text, flags=re.S)
    path.write_text(new, encoding="utf-8")
    print(f"{path}: {len(re.findall(r'<!-- table:', new))} tables")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        fill(Path(p))
