# 04 – Netz und Segmentierung

**Ziel:** Straßenabschnitte zwischen Knoten mit stabilen IDs.
**Eingaben:** OSM-Auszug in data/raw, docs/guide.md Teil 3.2 Stufe 2.
**Ergebnis:** pipeline/s02_network.py, data/interim/segments.parquet, reports/network.md.
**Prüfschritt:** Längensumme gegenüber OSM-Ausgangsnetz (Abweichung < 1 %), keine doppelten IDs, IDs bei zweitem Lauf identisch.

## Auftrag

Implementiere pipeline/s02_network.py nach docs/guide.md Teil 3.2 Stufe 2:
- OSM-Fahrzeuggraph: highway-Klassen motorway bis living_street, ohne service; Fußgängerzonen
  (highway=pedestrian) als eigene Abschnitte mitführen, weil sie ETW_ERF werden können.
- Vereinfachung auf Kanten zwischen Knoten mit Grad != 2.
- Kanten > 400 m teilen, wenn sich maxspeed ändert (Schwelle als assumption in rules.yaml
  ergänzen und in CHANGELOG.md vermerken).
- segment_id = stabiler Hash aus sortierten OSM-Way-IDs und auf 1 m gerundeten Knotenkoordinaten.
- Attribute: osm_way_ids, highway, name, length_m, bezirk.

Tests: Gültigkeit, CRS, Eindeutigkeit, Stabilität der IDs bei zweimaligem Lauf, Längensumme.
Report: Anzahl, Längenverteilung je highway-Klasse, 30 Zufallsabschnitte mit Link auf
openstreetmap.org.
