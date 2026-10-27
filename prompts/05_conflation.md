# 05 – Conflation amtlich ↔ OSM

**Ziel:** amtliche Attribute (HVS, Netzklassifizierung, Ist-Tempo) je Abschnitt.
**Eingaben:** data/interim/segments.parquet, data/raw (HH-SIB, Tempo, HVS), docs/guide.md Teil 3.2 Stufe 3.
**Ergebnis:** pipeline/s03_conflate.py, Spalten match_quality, in_hvs, speed_official_kmh, reports/conflation_sample.csv.
**Prüfschritt:** 50 Zufallsfälle manuell prüfen; Trefferquote im Report.

## Auftrag

Implementiere pipeline/s03_conflate.py:
- Linienabgleich HH-SIB/HVS -> Abschnitte: Kandidaten im Puffer, Filter nach Richtungswinkel
  und Überdeckungsanteil, Zuordnung nach Hausdorff-Abstand. Startwerte 15 m, 20°, 60 % als
  source_type: assumption in rules.yaml (Abschnitt conflation) anlegen, falls nicht vorhanden.
- Flächenquellen (Tempo-30-Zonen, verkehrsberuhigte Bereiche) über Längenanteil zuordnen
  (Anteil >= 50 % = gilt für den Abschnitt; ebenfalls als assumption).
- Zeitlich begrenzte Regelungen (z. B. Tempo 30 nachts) getrennt speichern, nicht als Regeltempo.
- Schreibe match_quality (exact | partial | none) und alle zugeordneten Attribute.

Keine Schwellen im Code. Erzeuge reports/conflation_sample.csv mit 50 Zufallsfällen und
Links (OSM, Geoportal) für die manuelle Prüfung sowie reports/conflation.md mit Kennzahlen.
