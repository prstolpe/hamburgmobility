# 14 – Radnetz-Erweiterung einrichten

**Ziel:** neue Regelwerke, Schemas, Korrekturdateien und Daten für das Radnetz in das bestehende Repository einbinden.
**Eingaben:** config/cycling_rules.yaml, config/design_rules.yaml, docs/guide_radnetz.md, CLAUDE.md, config/sources.yaml.
**Ergebnis:** pydantic-Schemas, Loader, CLAUDE.md-Abschnitt „Radnetz“, Makefile-Ziele, overrides/cycle_network_overrides.csv, overrides/junction_overrides.csv, neue Quellen in sources.yaml, goldene Fälle in tests/golden/cycling/.
**Prüfschritt:** `make test` grün; Verkehrsplaner*in prüft beide YAML-Dateien gegen ihre Quellen; neue Quellen im Datenbericht.

## Auftrag

Lies docs/guide_radnetz.md, config/cycling_rules.yaml und config/design_rules.yaml.
Ändere keine Werte in den YAML-Dateien.

1. Schemas: Erweitere config/schema/ um pydantic-Modelle für beide Dateien (Pflichtfelder
   source/source_type bei jeder Regel und jedem Zahlenwert mit Maßangabe; gültige Kategorien;
   eindeutige IDs). Loader in pipeline/lib/rules.py ergänzen.
2. CLAUDE.md: Füge einen Abschnitt „Radnetz und Soll-Querschnitt“ hinzu: Verweis auf die beiden
   YAML-Dateien und docs/guide_radnetz.md, Grundsatz „keine Schwellen im Code“, Korrekturebenen,
   neue Make-Ziele. Bestehende Abschnitte nicht verändern.
3. Makefile: Ziele cycle-demand, cycle-network, cycle-principles, cycle-facility, cross-section-soll,
   junctions, export-cycling (vorerst Platzhalter).
4. Korrekturdateien anlegen:
   - overrides/cycle_network_overrides.csv: edge_id, cycle_cat_final, reason, author, date, source, review_status
   - overrides/junction_overrides.csv: node_id, junction_type_final, reason, author, date, source, review_status
5. sources.yaml ergänzen (nur mit belegten URLs, sonst url: null + TODO): Radnetz Hamburg (Geoportal-Dienst
   ermitteln; Fallback OSM-Relationen cycle_network=DE:HH:Radnetz_Hamburg), Rad-Zählstellen
   (SensorThings https://iot.hamburg.de/v1.1 prüfen), DB Rad+ (bereits vorhanden), OSM-Radinfrastruktur
   (highway=cycleway, cycleway:*, bicycle=*, bicycle_road=yes), LSA-Standorte (OSM highway=traffic_signals;
   amtliche Quelle suchen), Straßenbahn/Bus aus GTFS, Ziele (Schulen, Hochschulen, Schnellbahnhalte, Zentren).
   Erweitere s01_fetch.py entsprechend und lade die Daten für ganz Hamburg.
6. Goldene Fälle in tests/golden/cycling/: mindestens 10 Abschnitte und 6 Knoten mit erwarteter
   Führungsform, Breite, Fahrstreifen bzw. Knotentyp (je Zeile der separation_matrix und der
   junctions.decision_table mindestens ein Fall). Tests bis Prompt 18/20 als xfail markieren.

Erfinde keine Endpunkte oder Schwellen. Offene Punkte in docs/open_questions.md unter „Radnetz“.
Zeige zuerst den Plan.
