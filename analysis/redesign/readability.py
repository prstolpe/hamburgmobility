"""Readability of all German texts (prompt 24, A1.3/A1.4): website (from the content capture
data/scenarios/redesign/ui/content.json and the task test tasks.json) and the text fields of the rule files.

Measures per text unit (textstat with set_lang("de"), syllables via pyphen):
- Wiener Sachtextformel, variant 1 (WSTF; 4 = very easy … 15 = very hard; school year)
- Flesch reading ease after Amstad (FRE_de = 180 - ASL - 58.5 * ASW; 0 = very hard … 100 = very easy)
- mean sentence length (words), share of sentences over 15 words
- passive share: share of sentences with a form of "werden" plus a participle II (heuristic, precision checked by
  hand on a sample, see check_sample())
- long-noun share: share of words that are capitalised, not sentence-initial, with at least 12 letters and 4 syllables
  (heuristic for compound nouns)
- technical terms and abbreviations: curated list TERMS plus all rule IDs and all-caps tokens

Usage: uv run --with textstat --with pyphen python -m analysis.redesign.readability [--check]
Writes data/scenarios/redesign/readability_units.csv, readability_terms.csv, readability_summary.json.
"""

import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd
import pyphen
import textstat
import yaml

from analysis.redesign.rule_inventory import TEXT_KEYS, rule_meta

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "data/scenarios/redesign/ui"
OUT = ROOT / "data/scenarios/redesign"
textstat.set_lang("de")
DIC = pyphen.Pyphen(lang="de_DE")

# Technical terms checked in every text (case-sensitive where the term is an abbreviation). Plain names: glossary.yaml.
TERMS = [
    "SW", "GOW", "GOW50", "GOW30", "ETW", "ETW30", "ETW_ERF", "GOW80", "ETW60", "Duurzaam Veilig", "SWOV", "CROW",
    "Diskrepanz", "Conflation", "Konflation", "Entwurfssituation", "Kaskade", "Soll", "Ist", "Soll-Kategorie",
    "Querschnitt", "Soll-Querschnitt", "Straßenraumbreite", "Machbarkeit", "DTV", "Kfz", "LSA", "HVS", "BVM",
    "RSV", "HAUPT", "BASIS", "ERSCHL", "Radvorrangroute", "Bezirksroute", "Quartiersnetz", "Führungsform",
    "Trennungsmatrix", "Mischverkehr", "Radfahrstreifen", "Schutzstreifen", "Fahrradstraße", "Gehwegüberfahrt",
    "Turbokreisel", "Turbokreisverkehr", "planfrei", "Furt", "Aufstellfläche", "Knotenpunkt", "Knotentyp", "Arm",
    "Kohärenz", "Harmonisierung", "Robustheit", "Datenunsicherheit", "confidence", "Score", "Perzentil",
    "Perzentilrang", "Betweenness", "Transekt", "Masche", "Torsituation", "Schleichverkehr", "Priorität",
    "Verbindungswert", "Aufenthaltswert", "conn_score", "place_score", "Fallback", "Schwelle", "Schwellenwert",
    "Annahme", "Stadtmagistrale", "Stadtstraße 30", "Quartiersstraße", "Aufenthaltsstraße", "Schnellverkehrsstraße",
    "Steckbrief", "Ebene", "Overlay", "Override", "OSM", "OpenStreetMap", "ALKIS", "GTFS", "WFS", "PMTiles",
    "ODbL", "dl-de", "RASt", "ERA", "HBS", "FGSV", "rule_trace", "segment_id", "Abschnitt", "Straßenzug",
    "Verkehrsfläche", "Fassade", "Engstelle", "Mittelstreifen", "Busfahrstreifen", "Ladezone", "Rückbau",
    "Handlungsbedarf", "Unfallatlas", "Spitzenstunde", "Lastrichtung", "graue Straße", "Erschließung",
    "Verbindungsfunktion", "Aufenthaltsfunktion", "Netzprüfung", "Stroomweg", "Stroomwegen",
    "Gebiedsontsluitingsweg", "Erftoegangsweg", "Auslöser", "anbaufrei", "dreiwertige Logik", "Kleene",
]
# Codes that look like rule IDs but are not (licences, data sets)
NOT_RULE_IDS = {"HH-SIB", "BSD-3", "HVV-GTFS", "CC-BY", "dl-de", "OFL-1"}
RULE_ID = re.compile(r"\b(?:[A-Z][A-Z0-9]{0,4}-){1,2}[A-Z0-9]{1,4}[a-z]?\b|\b[ND]\d\b")
CAPS = re.compile(r"\b[A-ZÄÖÜ]{2,}[A-ZÄÖÜ0-9_]*\b")
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ0-9„\"(])|\n+")
WORDS = re.compile(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß\-]*")
WERDEN = re.compile(r"\b(wird|werden|wurde|wurden|worden|würde|würden)\b", re.I)
PART2 = re.compile(r"\b(ge[a-zäöüß]{2,}(t|en)|[a-zäöüß]{2,}iert|[a-zäöüß]+ge[a-zäöüß]{2,}(t|en))\b")


MIN_SENTENCE_WORDS = 5


def fragments(text: str) -> list[str]:
    return [s.strip() for s in SENT.split(text) if s and s.strip()]


def sentences(text: str) -> list[str]:
    """Sentences for the readability measures. Fragments under MIN_SENTENCE_WORDS words are labels, legend entries
    or table cells, not prose; they count in labels_share and in the term list, not in the sentence measures."""
    return [s for s in fragments(text) if len(WORDS.findall(s)) >= MIN_SENTENCE_WORDS]


def syllables(word: str) -> int:
    return max(1, len(DIC.inserted(word).split("-")))


def is_passive(sent: str) -> bool:
    return bool(WERDEN.search(sent) and PART2.search(sent))


def long_nouns(sent: str) -> tuple[int, int]:
    ws = WORDS.findall(sent)
    hits = sum(1 for i, w in enumerate(ws) if i > 0 and w[0].isupper() and len(w.replace("-", "")) >= 12
               and syllables(w) >= 4)
    return hits, len(ws)


def term_hits(text: str) -> dict[str, int]:
    hits = defaultdict(int)
    for t in TERMS:
        pat = rf"(?<![\w-]){re.escape(t)}(?![\w])" if not t.isupper() else rf"\b{re.escape(t)}\b"
        n = len(re.findall(pat, text))
        if n:
            hits[t] += n
    for m in RULE_ID.findall(text):
        if m not in NOT_RULE_IDS:
            hits[("Kürzel " if re.fullmatch(r"D[1-3]", m) else "Regel-ID ") + m] += 1
    for m in CAPS.findall(RULE_ID.sub(" ", text)):
        if m not in TERMS and not RULE_ID.fullmatch(m):
            hits["Kürzel " + m] += 1
    return dict(hits)


def measure(text: str) -> dict:
    frs = fragments(text)
    ss = sentences(text)
    nw = sum(len(WORDS.findall(s)) for s in ss)
    nw_all = sum(len(WORDS.findall(s)) for s in frs)
    if not ss or nw == 0:
        return {"sentences": 0, "words": nw_all, "label_share": 1.0 if nw_all else None}
    lens = [len(WORDS.findall(s)) for s in ss]
    ln = [long_nouns(s) for s in ss]
    joined = " ".join(s if s.rstrip().endswith((".", "!", "?", ":")) else s + "." for s in ss)
    scorable = nw >= 30 and len(ss) >= 2
    return {
        "sentences": len(ss), "words": nw_all, "label_share": round(1 - nw / nw_all, 2) if nw_all else None,
        "wstf": round(textstat.wiener_sachtextformel(joined, 1), 1) if scorable else None,
        "fre_amstad": round(textstat.flesch_reading_ease(joined), 1) if scorable else None,
        "mean_sentence_words": round(nw / len(ss), 1),
        "share_sentences_over_15": round(sum(1 for x in lens if x > 15) / len(ss), 2),
        "passive_share": round(sum(1 for s in ss if is_passive(s)) / len(ss), 2),
        "long_noun_share": round(sum(h for h, _ in ln) / max(1, sum(n for _, n in ln)), 3),
    }


# --- text units -------------------------------------------------------------------------------------------------


def website_units():
    c = json.loads((UI / "content.json").read_text(encoding="utf-8"))
    units = []
    for p, v in c["pages"].items():
        for s in v["sections"]:
            units.append(("Webseite", f"Seite {p}", s["heading"], s["text"]))
    for l, v in c["layers"].items():
        units.append(("Webseite", "Ebene/Legende", f"{l} – {v['title']}", "\n".join([v["text"], *v["legend"], *v["notes"]])))
    for cat, v in c["profiles"].items():
        for s in v["sections"]:
            units.append(("Webseite", f"Steckbrief {cat}", s["heading"], s["text"]))
    for s in c["junction"]["sections"]:
        units.append(("Webseite", "Steckbrief Knoten", s["heading"], s["text"]))
    if c["chrome"].get("banner"):  # no banner since prompt 25
        units.append(("Webseite", "Rahmen", "Banner", c["chrome"]["banner"]))
    units.append(("Webseite", "Rahmen", "Filter", c["chrome"]["filter_text"]))
    return units


def rule_units():
    meta, raw = rule_meta()
    units = []
    for _, r in meta.iterrows():
        node = raw[r.id]
        for k in TEXT_KEYS:
            if isinstance(node.get(k), str):
                units.append(("Regeldatei", r.file, f"{r.id}.{k}", " ".join(node[k].split())))
    # thresholds and other nested notes
    for f in ["rules.yaml", "cycling_rules.yaml", "design_rules.yaml"]:
        doc = yaml.safe_load((ROOT / "config" / f).read_text(encoding="utf-8"))

        def walk(n, path):
            if isinstance(n, dict):
                for k, v in n.items():
                    if k in ("note", "label_de", "label_note") and isinstance(v, str) and not isinstance(n.get("id"), str):
                        units.append(("Regeldatei", f, f"{path}.{k}", " ".join(v.split())))
                    else:
                        walk(v, f"{path}.{k}" if path else k)
            elif isinstance(n, list):
                for i, v in enumerate(n):
                    walk(v, f"{path}[{i}]")
        walk(doc, "")
    pl = yaml.safe_load((ROOT / "config/plain_language.yaml").read_text(encoding="utf-8"))

    def walk_pl(n, path):
        if isinstance(n, str):
            units.append(("Klartexte", "plain_language.yaml", path, n))
        elif isinstance(n, dict):
            for k, v in n.items():
                if k not in ("when", "meta"):
                    walk_pl(v, f"{path}.{k}" if path else k)
        elif isinstance(n, list):
            for i, v in enumerate(n):
                walk_pl(v, f"{path}[{i}]")
    walk_pl(pl, "")
    return units


def check_sample(rows, n=40, seed=24):
    """Print a random sample of sentences with the passive and long-noun verdicts for a manual precision check."""
    rnd = random.Random(seed)
    sents = [s for r in rows for s in sentences(r["text"])]
    flagged = [s for s in sents if is_passive(s)]
    for s in rnd.sample(flagged, min(n, len(flagged))):
        print("P |", s[:200])
    print("---")
    nouns = [w for s in sents for i, w in enumerate(WORDS.findall(s)) if i > 0 and w[0].isupper()
             and len(w.replace("-", "")) >= 12 and syllables(w) >= 4]
    print("long nouns sample:", rnd.sample(nouns, min(n, len(nouns))))


def main():
    rows = []
    for src, group, item, text in website_units() + rule_units():
        m = measure(text)
        rows.append({"source": src, "group": group, "item": item, "text": text, **m,
                     "terms": json.dumps(term_hits(text), ensure_ascii=False)})
    df = pd.DataFrame(rows)
    if "--check" in sys.argv:
        check_sample(rows)
        return
    df.to_csv(OUT / "readability_units.csv", index=False)

    terms = defaultdict(lambda: {"count": 0, "where": set()})
    for _, r in df.iterrows():
        for t, n in json.loads(r.terms).items():
            terms[t]["count"] += n
            terms[t]["where"].add(f"{r.source}: {r.group}")
    tdf = pd.DataFrame([{"term": t, "count": v["count"], "n_places": len(v["where"]),
                         "where": "; ".join(sorted(v["where"]))} for t, v in terms.items()]).sort_values("count", ascending=False)
    tdf.to_csv(OUT / "readability_terms.csv", index=False)

    def agg(d):
        """Pooled scores over all text of a group (one long text), plus word-weighted shares."""
        text = "\n".join(d.text)
        m = measure(text)
        return {"units": len(d), **m}

    summary = {"by_source": {s: agg(d) for s, d in df.groupby("source")},
               "by_group": {f"{s} | {g}": agg(d) for (s, g), d in df.groupby(["source", "group"])}}
    (OUT / "readability_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in summary["by_source"].items():
        print(k, v)
    print(f"{len(df)} units, {len(tdf)} distinct terms")


if __name__ == "__main__":
    main()
