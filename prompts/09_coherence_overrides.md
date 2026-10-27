# 09 – Netzkohärenz und Korrekturebene

**Ziel:** Widersprüche im Netz markieren; fachliche Korrekturen versioniert übernehmen.
**Eingaben:** Klassifikation, config/rules.yaml (coherence), overrides/overrides.csv.
**Ergebnis:** pipeline/s06_coherence.py, pipeline/s06b_overrides.py, Spalten flags, cat_final, override_reason, reports/coherence.md.
**Prüfschritt:** Flag-Liste fachlich durchgesehen; Test auf verwaiste Overrides grün.

## Auftrag

Implementiere pipeline/s06_coherence.py mit den Regeln N1–N6 aus rules.yaml auf dem Graphen der
vorgeschlagenen Kategorien:
- N1 Durchgängigkeit, N2 kurze Kategorie-Inseln, N3 Aufenthaltsbereiche als Flächen bilden,
  N4 Schleichverkehr (kürzester Weg bei Soll-Tempo vs. Weg auf GOW/SW; OD-Paare und Anzahl
  dokumentieren), N5 Übergänge mit Torsituation, N6 Soll-Knotentyp je Kategoriepaar.
- Nichts automatisch umklassifizieren. Glättungsvorschläge als eigene flags mit Regel-ID.

Implementiere die Korrekturebene:
- overrides/overrides.csv: segment_id, cat_final, reason, author, date, source, review_status.
- Nur review_status = approved wird übernommen; cat_proposed und cat_final bleiben nebeneinander.
- Tests: verwaiste segment_ids, ungültige Kategorie, fehlende Begründung -> Fehler mit klarer Meldung.
- Hilfsskript, das aus einer Liste von segment_ids eine Vorlage für neue Overrides erzeugt.

Report: alle Flags je Regel mit Karte (statisches PNG oder GeoJSON) und Kennzahlen.
