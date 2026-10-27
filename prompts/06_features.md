# 06 – Merkmale je Abschnitt

**Ziel:** alle Eingangswerte, die rules.yaml verlangt.
**Eingaben:** segments nach Conflation, data/raw (GTFS, ALKIS, Zensus, OSM, Bäume, Schulen, Kitas), docs/guide.md Teil 3.2 Stufe 4.
**Ergebnis:** pipeline/s04_features.py, data/interim/features.parquet, reports/features.md.
**Prüfschritt:** Verteilungen plausibel; Anteil fehlender Werte je Merkmal im Report; keine Merkmale, die rules.yaml nicht braucht, ohne Begründung.

## Auftrag

Implementiere pipeline/s04_features.py. Leite die Liste der benötigten Merkmale aus
config/rules.yaml ab (classification, scores, requirements, discrepancy) und berechne:
- Verbindung: edge betweenness zeitgewichtet (igraph; bei Laufzeitproblemen Stichprobe von
  Quellknoten, dokumentieren), in_hvs, Busfahrten pro Werktag aus GTFS (shapes auf Abschnitte
  matchen; repräsentativen Werktag wählen und nennen), DTV wo vorhanden.
- Aufenthalt/Erschließung: Gebäudedichte, Einwohner aus dem Zensus-Gitter (flächenanteilig im
  Puffer), Anteil Erdgeschoss mit Publikumsnutzung (OSM shop/amenity, ALKIS-Gebäudefunktion),
  Entfernung zu Schulen/Kitas, Zugehörigkeit zum Radnetz.
- Ist-Tempo: amtlich vor OSM maxspeed; Konflikt beider Quellen als Unsicherheit speichern.
- Ist-Gestaltung aus OSM: separated_cycle_track_present, cycle_lane_present, lanes,
  centre_line (lane_markings), parking, crossings, traffic_calming, surface.
- Normierung auf 0–1 (Methode im Report dokumentieren) und conn_score/place_score nach rules.yaml.

Fehlende Werte nicht auffüllen, sondern als null führen und missing_value_policy aus
rules.yaml anwenden. Report mit Histogrammen, Nullwertanteilen je Merkmal und je Datenquelle.
