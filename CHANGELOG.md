# Changelog Regelwerk und Daten

## rules.yaml 0.1.0 – 2026-10-27
- Erster Entwurf aus docs/guide.md, Anhang A. Alle Regeln status: draft.

## sources.yaml 0.1.1 – 2026-10-28
- osm: URL des Geofabrik-Auszugs Hamburg eingetragen (geprüft: HTTP 200, ca. 54 MB), check_status verified.

## sources.yaml 0.1.2 – 2026-10-28
- Neu: `fetch:` je Quelle (welche Feature-Typen/Collections geladen werden) und `fallback_osm:` für Schulen, Kitas, Radnetz.
- strategic_road_network: check_status open (HTTP 404).
- dedications, road_condition_zeb, road_surface, quiet_areas: GetCapabilities gelesen, check_status verified; Lizenz dl-de/by-2.0 laut ows:Fees (außer Ruhige Gebiete: keine Angabe).
- speed_limits, traffic_volumes, bike_volumes_dbradplus: collections_seen aktualisiert; DB Rad+ Lizenz ODbL laut API, Abruf jahr2025 (Abrufproblem in fetch_issue dokumentiert).
- traffic_counters: nur Bestandsabruf (Locations + Things).

## rules.yaml 0.2.0 – 2026-10-28
- Neu: Abschnitt `network` für die Segmentierung (pipeline/s02_network.py, prompts/04_network.md).
  - `highway_classes`: motorway bis living_street inkl. *_link, ohne service; pedestrian als eigene Abschnitte (ETW_ERF möglich).
  - S-NET-01: Abschnittsende an Knoten mit Grad ≠ 2 (guide.md 3.2 Stufe 2).
  - S-NET-02: Abschnittsende bei Wechsel der highway-Klasse (Entscheidung Projektteam 2026-10-28), damit jeder Abschnitt genau eine Klasse hat.
  - S-NET-03: Abschnitte > 400 m bei maxspeed-Wechsel teilen. 400 m ist eine Annahme (guide.md 3.2) und muss fachlich freigegeben werden.
- Schema (config/schema/rules_model.py) um `network` erweitert; Regel-IDs `S-…-NN` gehen in die Prüfung auf doppelte IDs ein.

## rules.yaml 0.3.0 – 2026-10-28
- Neu: Abschnitt `conflation` für den Abgleich amtlich ↔ OSM (pipeline/s03_conflate.py, prompts/05_conflation.md).
  - S-CONF-01: Linienabgleich mit Puffer 15 m, Richtungswinkel ≤ 20°, Überdeckung ≥ 60 % (Startwerte aus guide.md 3.2, assumption).
    match_quality exact/partial/none über die Überdeckung des Abschnitts (Vorschlag, fachlich zu prüfen).
  - S-CONF-02: Zonen über Längenanteil ≥ 50 % (assumption). Die Zonenebenen der API sind Linien, keine Flächen.
  - S-CONF-03: zeitlich begrenzte Regelungen getrennt speichern, nie als Regeltempo.
  - S-CONF-04: `in_hvs` aus den DTV-Linien der Hauptverkehrsstraßen 2019, weil HH-SIB (HTTP 404) nicht erreichbar
    ist und die HVS-Karte 2023 nur als PDF vorliegt (Entscheidung Projektteam 2026-10-28).
- Neue Quellen: HH_DTV_HVS_2019, HH_TEMPO.
- Schema um `conflation` erweitert (IDs in der Dublettenprüfung, Herkunft je Regel und Schwelle).
