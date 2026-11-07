"""Phase 1.2: classify every entry in docs/open_questions.md.

Status per entry:
  eingearbeitet         answered ([x]) and the answer is in the rules/code (or the answer is "belassen")
  beantwortet_offen     answered, but the answer points to later work (Prompt 22/23, "später", "Wert am Original prüfen")
  offen                 [ ] without a decision
  offen_teilantwort     [ ] with a dated note, but no final decision
Rule IDs are taken from the text; for open entries the affected km/nodes are measured from the traces in
data/interim (rows whose trace contains the rule id). Manual corrections: MANUAL below (line number -> status).

Usage: python -m analysis.review_2026_11.open_questions <out_dir>
"""

import re
import sys
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs/open_questions.md"
RULE_RE = re.compile(r"\b(?:[A-Z]{1,4}-[A-Z0-9]{1,5}(?:-[0-9]{2})?|N[1-7]|PRF-0\d|PL-0\d|L-0\d|J-\d\d|JC-0\d|S-0\d)\b")
LATER = re.compile(r"später|Prompt 2[23]|am Original prüfen|Fachplaner-Termin|zurückgestellt", re.I)
DECIDED = re.compile(r"Entscheidung|erledigt|umgestellt|geändert|freigegeben|ergänzt|übernommen|belassen", re.I)
# Manual corrections after reading each entry (line -> status, reason)
MANUAL = {
    70: ("offen_teilantwort", "Obergrenze eingeführt und zurückgenommen; 'Regel später verbessern'"),
    124: ("offen_teilantwort", "Probelauf gerechnet, Entscheidung zurückgestellt"),
    201: ("offen_teilantwort", "wie Zeile 70"),
    202: ("beantwortet_offen", "4,75 m übernommen, Wert am Original prüfen"),
    159: ("eingearbeitet", "Faktor 1,5 übernommen (cycling_rules 0.7.0)"),
    168: ("eingearbeitet", "density_scaling übernommen (cycling_rules 0.6.0)"),
    57: ("offen_teilantwort", "Feed geprüft, Folgefeed fehlt noch"),
}

TRACES = {
    "discrepancy": ("segment_id", "length_m", ["rule_trace", "coherence_trace", "disc_trace", "feature_trace",
                                                "conflation_trace", "crosssection_trace", "rule_path"]),
    "cycle_facility": ("segment_id", "length_m", ["rule_trace_facility"]),
    "cross_section_soll": ("segment_id", "length_m", ["rule_trace_profile"]),
    "junctions": ("node_id", None, ["rule_trace_junction", "decision_rule"]),
}


def parse() -> pd.DataFrame:
    rows, section = [], ""
    lines = SRC.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, start=1):
        if line.startswith("## "):
            section = line[3:].strip()
        m = re.match(r"- \[( |x)\] (.*)", line)
        if not m:
            continue
        # sub-bullets belong to the entry
        text = m.group(2)
        j = i
        while j < len(lines) and lines[j].startswith("  - "):
            text += " | " + lines[j].strip()[2:]
            j += 1
        done = m.group(1) == "x"
        parts = m.group(2).split(" – ")  # head line only; sub-bullets stay in `text`
        who = next((p for p in parts[1:] if re.search(r"Verkehrsplaner|Methodik|GIS|Team|Ortskundige", p)), "")
        answer = " – ".join(parts[parts.index(who) + 1:]) if who in parts else ""
        if done:
            status = "beantwortet_offen" if LATER.search(answer) and not re.search(r"belassen", answer) \
                else "eingearbeitet"
        else:
            status = "offen_teilantwort" if re.search(r"20\d\d-\d\d-\d\d", answer) and DECIDED.search(answer) else "offen"
        reason = ""
        if i in MANUAL:
            status, reason = MANUAL[i]
        rows.append({"line": i, "section": section, "done": done, "status": status, "who": who.strip(),
                     "question": parts[0][:220], "answer": answer[:260], "rules": sorted(set(RULE_RE.findall(text))),
                     "manual_note": reason})
    return pd.DataFrame(rows)


def impact(df: pd.DataFrame) -> pd.DataFrame:
    """km (segments) and nodes whose traces mention a rule of the entry."""
    hits: dict[str, tuple[float, int]] = {}
    want = {r for rs in df.rules for r in rs}
    for name, (key, length, cols) in TRACES.items():
        path = ROOT / "data/interim" / f"{name}.parquet"
        have = [c for c in cols if c in pq.read_schema(path).names]
        t = pq.read_table(path, columns=[key] + ([length] if length else []) + have).to_pandas()
        blob = t[have].astype(object).map(lambda v: "" if v is None or v != v else str(v)).agg(" ".join, axis=1)
        for r in want:
            mask = blob.str.contains(rf"(?<![A-Za-z0-9-]){re.escape(r)}(?![A-Za-z0-9])", regex=True)
            if not mask.any():
                continue
            km, nodes = hits.get(r, (0.0, 0))
            if length:
                km = max(km, float(t.loc[mask, length].sum()) / 1000)
            else:
                nodes = max(nodes, int(mask.sum()))
            hits[r] = (km, nodes)
    df["km_affected"] = df.rules.map(lambda rs: round(max([hits.get(r, (0, 0))[0] for r in rs] or [0]), 1))
    df["nodes_affected"] = df.rules.map(lambda rs: max([hits.get(r, (0, 0))[1] for r in rs] or [0]))
    return df


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    df = impact(parse())
    df.to_csv(out / "open_questions_status.csv", index=False)
    print(df.status.value_counts())
    print(df.groupby(["section", "status"]).size().unstack(fill_value=0))


if __name__ == "__main__":
    main(sys.argv[1])
