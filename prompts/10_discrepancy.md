# 10 – Diskrepanz („grijze wegen“) und Priorisierung

**Ziel:** graue Straßen erkennen und nach Risiko ordnen.
**Eingaben:** cat_final, Ist-Merkmale, Unfallatlas, config/rules.yaml (discrepancy, priority).
**Ergebnis:** pipeline/s08_discrepancy.py, Spalten disc_type, disc_speed, disc_design, disc_use, priority, reports/priority_top30.md.
**Prüfschritt:** Top-30-Liste von Ortskundigen gegenlesen lassen.

## Auftrag

Implementiere pipeline/s08_discrepancy.py nach rules.yaml:
- Tempo-, Gestaltungs- und Nutzungsdiskrepanz je Abschnitt mit Stärke 0–3 und den
  verursachenden Merkmalen; Typ D1–D3.
- Risiko aus Unfallatlas (Beteiligung Fuß/Rad, Schwere gewichtet, 5 Jahre; Jahre ohne
  Hamburg-Abdeckung ausweisen), Radnetz, Bevölkerung, Schulen/Kitas.
- Unfälle nur aggregiert je Abschnitt speichern; keine Einzelunfälle im Export.
- Priorität nach priority.formula.

Report: Top 30 mit Begründung in Klartext (z. B. „Soll Stadtstraße 30, heute 50, Radverkehr
auf Fahrbahn, 7 Unfälle mit Radbeteiligung in 5 Jahren, Grundschule in 120 m“) und Verteilung
der Diskrepanztypen je Kategorie.
