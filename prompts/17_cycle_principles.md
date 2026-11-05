# 17 – Fünf Prinzipien prüfen

**Ziel:** jede Route und das Gesamtnetz nach Zusammenhang, Direktheit, Sicherheit, Komfort und Attraktivität bewerten – für Ist und Soll.
**Eingaben:** cycle_routes.parquet, cycle_edges.parquet, Ist-Radführung, LSA, Unfälle, Bäume/Grün, Lärm, Beleuchtung (OSM lit), config/cycling_rules.yaml (principles, principle_weights).
**Ergebnis:** pipeline/c04_principles.py, data/interim/cycle_principles.parquet (je route_id und edge_id), reports/cycle_principles.md.
**Prüfschritt:** Kennzahlen plausibel; 20 Routen stichprobenartig mit Ortskundigen besprechen; Sensitivität der Gewichte.

## Auftrag

Implementiere c04_principles.py mit allen Checks P-COH-*, P-DIR-*, P-SAF-*, P-COM-*, P-ATT-*:
- P-DIR-01: Umwegfaktor für eine Stichprobe von OD-Paaren je Kategorie (Netzweg auf Kategorie-
  Ebene inkl. höherer Ebenen vs. kürzester Weg auf allen befahrbaren Kanten). Anzahl OD-Paare und
  Seed dokumentieren.
- P-DIR-02/03: Halte/km aus LSA und Wartepflichten (Knotentyp Ist, später Soll aus Prompt 20).
- P-SAF-01: zunächst Ist-Führung gegen separation_matrix; nach Prompt 18 auch Soll.
- P-COM-01/02: Breite und Belag (OSM width, surface; fehlende Werte als unbekannt, nicht als gut).
- P-ATT-01/02/03: Grünanteil im 20-m-Puffer, Lärm (falls Lärmkarte vorhanden), Parallelität.
Scores je Prinzip 0–1, Gesamtscore mit principle_weights; fehlende Daten senken die confidence.

Gib zwei Sichten aus: score_ist (heutiger Zustand der Soll-Route) und score_soll (nach regelkonformem
Ausbau). Die Differenz zeigt den Handlungsbedarf. Report: Netzkennzahlen, Top-30-Routen mit größtem
Handlungsbedarf, Karte je Prinzip, Gewichts-Sensitivität (±20 %).
