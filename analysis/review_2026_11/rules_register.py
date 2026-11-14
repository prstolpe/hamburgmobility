"""Regelregister als Excel-Datei zur fachlichen Prüfung der Regelwerke.

Liest config/rules.yaml, cycling_rules.yaml und design_rules.yaml und schreibt
docs/review/2026-11/regelregister.xlsx mit:
  - Regeln: jeder Eintrag mit id
  - Werte: jede Zahl (Schwelle, Breite, Gewicht ...) mit wirksamer Herkunft
  - Quellen, Übersicht (Formeln), Legende
source/source_type werden wie in config/schema/provenance.py vererbt.

Aufruf: uv run --with openpyxl python analysis/review_2026_11/rules_register.py
"""

import re
import subprocess
from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[2]
FILES = ["config/rules.yaml", "config/cycling_rules.yaml", "config/design_rules.yaml"]
OUT = ROOT / "docs/review/2026-11/regelregister.xlsx"

META_KEYS = {"label_plain", "explain_plain", "why", "history", "source", "source_type", "status", "note", "unit", "description", "label_de", "nl", "url", "title"}
SKIP_TOP = {"meta", "sources"}
TEXT_KEYS = ["description", "rule", "metric", "check"]
REVIEW_OPTIONS = ["offen", "ok", "ändern", "Frage", "streichen"]
SOURCE_TYPE_ORDER = {"(fehlt)": 0, "assumption (nur Kommentar)": 1, "assumption": 2, "hamburg": 3, "de_regelwerk": 4, "swov_crow": 5}

FONT = "Arial"


def scalar(node):
    """Python value of a scalar YAML node (uses the safe resolver tags)."""
    return yaml.safe_load(yaml.serialize(node)) if node is not None else None


def to_py(node):
    return scalar(node)


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def fmt(x):
    if isinstance(x, list):
        if len(x) == 2 and all(is_number(v) for v in x):
            return f"{fmt(x[0])}–{fmt(x[1])}"
        return ", ".join(fmt(v) for v in x)
    if isinstance(x, float):
        return f"{x:g}".replace(".", ",")
    return str(x)


def as_list(src):
    if src is None:
        return []
    return [src] if isinstance(src, str) else list(src)


def holds_number(x):
    return is_number(x) or (isinstance(x, list) and any(holds_number(v) for v in x))


def code_refs(ids):
    """Rule id -> pipeline files that mention it."""
    refs = {}
    for rid in ids:
        out = subprocess.run(["grep", "-rlw", "--include=*.py", rid, "pipeline"], cwd=ROOT,
                             capture_output=True, text=True).stdout.split()
        refs[rid] = ", ".join(sorted(p.removeprefix("pipeline/") for p in out))
    return refs


COMMENT_ST = re.compile(r"#\s*source_type:\s*(\w+)")
LINES: dict[str, list[str]] = {}


def walk(node, path, file, section, st, st_from, src, rule_id, rules, values):
    """Collect rules (mappings with id) and numeric values with effective provenance."""
    if isinstance(node, yaml.SequenceNode):
        for i, item in enumerate(node.value):
            walk(item, f"{path}[{i}]", file, section, st, st_from, src, rule_id, rules, values)
        return
    if not isinstance(node, yaml.MappingNode):
        return

    d = {k.value: v for k, v in node.value}
    py = {k: to_py(v) for k, v in d.items()}
    own_st = py.get("source_type")
    if own_st:
        st, st_from = own_st, path
    if py.get("source"):
        src = as_list(py["source"])
    line = node.start_mark.line + 1

    if "id" in py:
        rule_id = py["id"]
        params = []
        for k, v in py.items():
            if k in META_KEYS or k in {"id", "if", "then", *TEXT_KEYS}:
                continue
            if holds_number(v) or (isinstance(v, dict) and any(holds_number(x) for x in v.values())):
                if isinstance(v, dict):
                    if "value" in v:
                        params.append(f"{k} = {fmt(v['value'])}{' ' + v['unit'] if v.get('unit') else ''}")
                    else:
                        inner = "; ".join(f"{kk} {fmt(vv)}" for kk, vv in v.items()
                                          if kk not in META_KEYS and holds_number(vv))
                        params.append(f"{k}: {inner}")
                else:
                    params.append(f"{k} = {fmt(v)}")
        rules.append({
            "file": file, "section": section, "path": path, "line": line, "id": rule_id,
            "text": next((str(py[k]) for k in TEXT_KEYS if k in py), ""),
            "if": str(py.get("if", "")), "then": str(py.get("then", "")),
            "params": "\n".join(params), "source": ", ".join(src), "source_type": st or "(fehlt)",
            "inherited": "" if own_st else (st_from or ""), "status": py.get("status", ""),
            "note": str(py.get("note", "")).strip(),
        })

    for k, v in py.items():
        if k in META_KEYS or k == "id":
            continue
        if holds_number(v):
            label = path if k == "value" else f"{path}.{k}"
            vst = st or "(fehlt)"
            vsrc = ", ".join(src)
            if vsrc and vst.startswith("assumption") and not py.get("source"):
                vsrc = f"(nur übergeordnet: {vsrc})"
            values.append({
                "file": file, "section": section, "path": label, "line": d[k].start_mark.line + 1,
                "rule_id": rule_id or "", "value": v if is_number(v) else fmt(v), "unit": py.get("unit", "") if k in {"value", "range"} else "",
                "source": vsrc, "source_type": vst, "inherited": "" if own_st else (st_from or ""),
                "note": str(py.get("note", "")).strip() if k in {"value", "range", "factor"} or len(py) <= 4 else "",
            })
    for kn, child in node.value:
        k = kn.value
        if k in META_KEYS:
            continue
        cst, cfrom = st, st_from
        m = COMMENT_ST.search(LINES[file][kn.start_mark.line])
        if m and isinstance(child, yaml.MappingNode) and "source_type" not in {x.value for x, _ in child.value}:
            cst, cfrom = f"{m.group(1)} (nur Kommentar)", f"YAML-Kommentar Zeile {kn.start_mark.line + 1}"
        walk(child, f"{path}.{k}", file, section, cst, cfrom, src, rule_id, rules, values)


def load():
    rules, values, sources, versions = [], [], [], {}
    for f in FILES:
        text = (ROOT / f).read_text(encoding="utf-8")
        root = yaml.compose(text)
        name = Path(f).name
        LINES[name] = text.splitlines()
        for k, v in root.value:
            if k.value == "meta":
                versions[name] = to_py(v).get("version")
            elif k.value == "sources":
                for sk, sv in to_py(v).items():
                    sources.append({"file": name, "id": sk, "title": sv.get("title", ""), "date": str(sv.get("date", "") or ""),
                                    "url": sv.get("url") or "", "note": sv.get("note", "")})
            else:
                walk(v, k.value, name, k.value, None, None, [], None, rules, values)
    return rules, values, sources, versions


# ---------------------------------------------------------------- Excel
HEAD_FILL = PatternFill("solid", start_color="1F3864")
HEAD_FONT = Font(name=FONT, bold=True, color="FFFFFF")
INPUT_FILL = PatternFill("solid", start_color="FFF2CC")
ASSUMPTION_FILL = PatternFill("solid", start_color="FCE4D6")
BODY = Font(name=FONT, size=10)
WRAP = Alignment(wrap_text=True, vertical="top")


def table(ws, headers, rows, widths, review_from):
    ws.append([h for h, _ in headers])
    for c in ws[1]:
        c.fill, c.font = HEAD_FILL, HEAD_FONT
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for r in rows:
        ws.append([r.get(key, "") if key else "" for _, key in headers])
    n = ws.max_row
    for row in ws.iter_rows(min_row=2, max_row=n):
        for c in row:
            c.font, c.alignment = BODY, WRAP
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=2, column=6)
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{n}"

    # Review columns: yellow input cells, Prüfstatus as dropdown, default "offen"
    first = get_column_letter(review_from)
    last = get_column_letter(len(headers))
    for row in ws.iter_rows(min_row=2, max_row=n, min_col=review_from, max_col=len(headers)):
        for c in row:
            c.fill = INPUT_FILL
    for r in range(2, n + 1):
        ws.cell(row=r, column=review_from, value="offen")
    dv = DataValidation(type="list", formula1='"' + ",".join(REVIEW_OPTIONS) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{first}2:{first}{n}")

    # Highlight unsourced assumptions
    st_col = get_column_letter([k for _, k in headers].index("source_type") + 1)
    ws.conditional_formatting.add(
        f"A2:{get_column_letter(review_from - 1)}{n}",
        FormulaRule(formula=[f'LEFT(${st_col}2,10)="assumption"'], fill=ASSUMPTION_FILL))
    ws.conditional_formatting.add(
        f"A2:{get_column_letter(review_from - 1)}{n}",
        FormulaRule(formula=[f'${st_col}2="(fehlt)"'], fill=PatternFill("solid", start_color="F4B6B6")))
    return n, first, last


def main():
    rules, values, sources, versions = load()
    refs = code_refs([r["id"] for r in rules])
    for r in rules:
        r["code"] = refs[r["id"]]
    key = lambda r: (SOURCE_TYPE_ORDER.get(r["source_type"], 6), FILES.index("config/" + r["file"]), r["line"])
    rules.sort(key=key)
    values.sort(key=key)

    wb = Workbook()
    ov = wb.active
    ov.title = "Übersicht"

    ws_r = wb.create_sheet("Regeln")
    hr = [("Datei", "file"), ("Abschnitt", "section"), ("Zeile", "line"), ("ID", "id"), ("source_type", "source_type"),
          ("Beschreibung / Regel", "text"), ("Bedingung (if)", "if"), ("Ergebnis (then)", "then"),
          ("Parameter", "params"), ("Quelle", "source"), ("source_type geerbt von", "inherited"),
          ("Status", "status"), ("Hinweis", "note"), ("YAML-Pfad", "path"), ("Verwendet in pipeline/", "code"),
          ("Prüfstatus", None), ("Kommentar", None), ("Vorschlag (neuer Wert / Text)", None)]
    nr, _, _ = table(ws_r, hr, rules, [16, 16, 7, 12, 13, 45, 35, 22, 32, 22, 18, 9, 45, 30, 26, 12, 40, 30], 16)

    ws_v = wb.create_sheet("Werte")
    hv = [("Datei", "file"), ("Abschnitt", "section"), ("Zeile", "line"), ("Regel-ID", "rule_id"), ("source_type", "source_type"),
          ("YAML-Pfad", "path"), ("Wert", "value"), ("Einheit", "unit"), ("Quelle", "source"),
          ("source_type geerbt von", "inherited"), ("Hinweis", "note"),
          ("Prüfstatus", None), ("Kommentar", None), ("Vorschlag (neuer Wert)", None)]
    nv, _, _ = table(ws_v, hv, values, [16, 16, 7, 11, 13, 48, 14, 16, 22, 22, 45, 12, 40, 18], 12)

    ws_s = wb.create_sheet("Quellen")
    ws_s.append(["Datei", "ID", "Titel", "Datum", "URL", "Hinweis"])
    for c in ws_s[1]:
        c.fill, c.font = HEAD_FILL, HEAD_FONT
    for s in sources:
        ws_s.append([s["file"], s["id"], s["title"], s["date"], s["url"], s["note"]])
        if s["url"]:
            ws_s.cell(row=ws_s.max_row, column=5).hyperlink = s["url"]
    for row in ws_s.iter_rows(min_row=2):
        for c in row:
            c.font, c.alignment = BODY, WRAP
    for i, w in enumerate([16, 24, 60, 10, 50, 35], 1):
        ws_s.column_dimensions[get_column_letter(i)].width = w
    ws_s.freeze_panes = "C2"
    ws_s.auto_filter.ref = f"A1:F{ws_s.max_row}"

    # ---- Übersicht with live formulas
    bold = Font(name=FONT, bold=True)
    ov["A1"] = "Regelregister – Prüfung der Regelwerke (Entwurf, nicht amtlich)"
    ov["A1"].font = Font(name=FONT, bold=True, size=14)
    ov["A2"] = "Stand: " + ", ".join(f"{k} {v}" for k, v in versions.items()) + \
               " · erzeugt mit analysis/review_2026_11/rules_register.py"
    ov["A2"].font = Font(name=FONT, italic=True, size=9)

    types = ["(fehlt)", "assumption (nur Kommentar)", "assumption", "hamburg", "de_regelwerk", "swov_crow"]
    names = [Path(f).name for f in FILES]

    def block(top, title, sheet, nrows, st_col, review_col):
        ov.cell(row=top, column=1, value=title).font = bold
        hdr = ["source_type"] + names + ["Summe", "geprüft (≠ offen)", "Anteil geprüft"]
        for j, h in enumerate(hdr, 1):
            c = ov.cell(row=top + 1, column=j, value=h)
            c.fill, c.font = HEAD_FILL, HEAD_FONT
        rng = lambda col: f"{sheet}!${col}$2:${col}${nrows}"
        for i, t in enumerate(types + ["Summe"]):
            r = top + 2 + i
            ov.cell(row=r, column=1, value=t).font = bold if t == "Summe" else BODY
            for j, n in enumerate(names, 2):
                if t == "Summe":
                    f = f"=SUM({get_column_letter(j)}{top + 2}:{get_column_letter(j)}{r - 1})"
                else:
                    f = f'=COUNTIFS({rng("A")},"{n}",{rng(st_col)},"{t}")'
                ov.cell(row=r, column=j, value=f)
            sc = len(names) + 2
            ov.cell(row=r, column=sc, value=f"=SUM(B{r}:{get_column_letter(sc - 1)}{r})")
            if t == "Summe":
                done = f'=COUNTA({rng(review_col)})-COUNTIF({rng(review_col)},"offen")'
            else:
                done = f'=COUNTIFS({rng(st_col)},"{t}",{rng(review_col)},"<>offen",{rng(review_col)},"<>")'
            ov.cell(row=r, column=sc + 1, value=done)
            pc = ov.cell(row=r, column=sc + 2, value=f"=IF({get_column_letter(sc)}{r}=0,0,"
                                                     f"{get_column_letter(sc + 1)}{r}/{get_column_letter(sc)}{r})")
            pc.number_format = "0%"
            for c in ov[r]:
                c.font = Font(name=FONT, bold=(t == "Summe"))
        return top + 2 + len(types) + 2

    nxt = block(4, "Regeln (Einträge mit id)", "Regeln", nr, "E", "P")
    nxt = block(nxt, "Werte (Zahlen: Schwellen, Breiten, Gewichte …)", "Werte", nv, "E", "L")

    ov.cell(row=nxt, column=1, value="Prüfstatus Regeln").font = bold
    for i, o in enumerate(REVIEW_OPTIONS):
        ov.cell(row=nxt + 1 + i, column=1, value=o).font = BODY
        ov.cell(row=nxt + 1 + i, column=2, value=f'=COUNTIF(Regeln!$P$2:$P${nr},"{o}")').font = BODY
        ov.cell(row=nxt + 1 + i, column=3, value=f'=COUNTIF(Werte!$L$2:$L${nv},"{o}")').font = BODY
    ov.cell(row=nxt, column=2, value="Regeln").font = bold
    ov.cell(row=nxt, column=3, value="Werte").font = bold

    lg = nxt + len(REVIEW_OPTIONS) + 3
    legend = [
        ("Legende", True),
        ("Gelbe Spalten (Prüfstatus, Kommentar, Vorschlag) sind zum Ausfüllen; alles andere ist aus den YAML-Dateien erzeugt.", False),
        ("Prüfstatus: offen · ok · ändern · Frage · streichen (Auswahlliste). Die Übersicht zählt automatisch mit.", False),
        ("Lachsfarbene Zeilen: source_type = assumption, also Setzungen ohne Fachquelle – zuerst prüfen. Sortierung: assumption, hamburg, de_regelwerk, swov_crow.", False),
        ("„source_type geerbt von“: Wert steht nicht am Eintrag selbst, sondern an einem übergeordneten Eintrag (Vererbung wie config/schema/provenance.py).", False),
        ("Rote Zeilen: source_type fehlt ganz. „assumption (nur Kommentar)“: steht nur als YAML-Kommentar, wird von der Herkunftsprüfung nicht gesehen.", False),
        ("Zeile = Zeilennummer in der YAML-Datei (in VS Code: Strg/Cmd+G).", False),
        ("Beispiel: Werte, conn_gow = 0,6 → Prüfstatus „ändern“, Kommentar „HVS-Abgleich zeigt zu viele GOW“, Vorschlag „0,65“.", False),
        ("Änderungen wirken erst nach Übernahme in die YAML mit neuer meta.version und CHANGELOG-Eintrag. Neu erzeugen überschreibt Eingaben – Datei vorher umbenennen.", False),
    ]
    for i, (t, b) in enumerate(legend):
        ov.cell(row=lg + i, column=1, value=t).font = Font(name=FONT, bold=b, size=11 if b else 10)
    ov.column_dimensions["A"].width = 30
    for col in "BCDEFG":
        ov.column_dimensions[col].width = 20

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.calculation.fullCalcOnLoad = True
    wb.save(OUT)
    print(f"{OUT.relative_to(ROOT)}: {len(rules)} Regeln, {len(values)} Werte, {len(sources)} Quellen")


if __name__ == "__main__":
    main()
