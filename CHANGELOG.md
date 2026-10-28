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

## rules.yaml 0.4.0 – 2026-10-28
- Neu: Abschnitt `features` für die Merkmale je Abschnitt (pipeline/s04_features.py, prompts/06_features.md).
  - S-FEAT-01: Normierung als Perzentilrang über das Arbeitsgebiet (Entscheidung Projektteam 2026-10-28).
  - S-FEAT-02: zeitgewichtete Edge Betweenness (igraph, ungerichtet, exakt, ganz Hamburg, ohne Fußgängerzonen);
    Standardtempo je highway-Klasse, wenn weder amtliches noch OSM-Tempo bekannt ist (Annahmen, Entscheidung 2026-10-28).
  - S-FEAT-03 Gebäudedichte (Puffer 50 m), S-FEAT-04 Einwohner (Puffer 100 m), S-FEAT-05 Publikumsnutzung (Puffer 20 m,
    Liste amenity_excluded), S-FEAT-06 Schulen/Kitas, S-FEAT-07 Radnetz, S-FEAT-08 Busfahrten (GTFS, Werktag Di–Do mit den
    meisten Diensten), S-FEAT-09 Ist-Tempo, S-FEAT-10 Ist-Gestaltung aus OSM-Tags (node_snap_m 1 m). Alle Puffer und
    Listen sind Annahmen (status draft) und fachlich freizugeben.
  - Gebäude und Publikumsnutzung vorläufig aus OSM, weil ALKIS fehlt; Busfahrten und Einwohner bleiben null, bis GTFS
    und Zensus-Gitter in data/raw liegen.
- Schema (config/schema/rules_model.py) um `features` erweitert; S-FEAT-IDs gehen in die Prüfung auf doppelte IDs ein.

## sources.yaml 0.1.3 – 2026-10-28
- gtfs_hvv: URL des HVV-GTFS im Transparenzportal (Fahrplan 2026-04-08 bis 2026-12-12, 40,4 MB, dl-de/by-2.0), `fetch: {download: zip}`.
- population_grid: direkte URL Zensus2022_Bevoelkerungszahl.zip (destatis.de) statt Übersichtsseite; Lizenz dl-de/by-2.0
  laut Downloadseite; `fetch.grid` mit den Spalten aus der Datensatzbeschreibung im ZIP (100-m-Zellen, EPSG:3035).
- pipeline/s01_fetch.py: neuer Zugriff `download` (Datei einmal laden, bei gleichem Hash wiederverwenden; Gitter wird auf
  das Arbeitsgebiet zugeschnitten und als GeoParquet in EPSG:25832 gespeichert).
- Merkmale: bus_trips_weekday und population_100m jetzt gefüllt (vorher null).

## rules.yaml 0.5.0 – 2026-10-28
- S-FEAT-01: Gleiche Werte im Perzentilrang erhalten den kleinsten Rang ihrer Gruppe (`ties: min`, vorher mittlerer
  Rang). Begründung: Mit dem mittleren Rang bekamen Abschnitte ohne Bus (rund 70 %) bus_trips_weekday_norm 0,35 und
  Sackgassen eine Betweenness-Norm über 0; ein fehlender Beitrag wirkte damit wie ein mittlerer. Jetzt gilt: kleinster
  Wert → 0. Ohne Streuung ist der Normwert 0. Entscheidung Projektteam 2026-10-28.
- Wirkung (Arbeitsgebiet, Median conn_score): residential 0,24 → 0,15, unclassified 0,21 → 0,10, living_street
  0,21 → 0,10, motorway 0,60 → 0,52, primary 0,83 → 0,82; Anteil conn_score ≥ 0,6: 18,8 % → 18,1 %. place_score
  unverändert (keine Bindungen).
- Schema: Feld `ties` (min | average) für Merkmalsregeln.

## sources.yaml 0.1.4 – 2026-10-28
- alkis: WFS „ALKIS – Liegenschaften und Verwaltungseinheiten“ (https://geodienste.hamburg.de/WFS_HH_ALKIS_vereinfacht),
  URL aus dem GDI-DE-Metadatensatz 00F5606E-…; dl-de/by-2.0; Abruf von `ave:Nutzung` (tatsächliche Nutzung, Feld
  `nutzart`) und `ave:GebaeudeBauwerk` (Feld `funktion` = Gebäudefunktion, `gebnutzbez`, `rellage`). Im Arbeitsgebiet
  12 381 Nutzungsflächen (u. a. Strassenverkehr 4 125, Weg 979, Platz 89) und 60 052 Gebäude/Bauwerke.
- Die INSPIRE-Dienste HH_WFS_INSPIRE_Gebaeude_2D_ALKIS und HH_WFS_INSPIRE_Bodenbedeckungsvektor_ALKIS wurden geprüft, aber
  nicht übernommen: Die Bodenbedeckung unterscheidet Straßenverkehr/Weg/Platz nicht, das vereinfachte ALKIS-Schema
  enthält Gebäude mit Gebäudefunktion.

## rules.yaml 0.6.0 – 2026-10-28
- S-FEAT-03 Gebäudedichte: ALKIS-Gebäude (ave:GebaeudeBauwerk, gebnutzbez Gebaeude, ohne „Unter der Erdoberfläche“)
  statt OSM-Gebäude (Entscheidung Projektteam 2026-10-28, nachdem ALKIS mit sources.yaml 0.1.4 verfügbar ist).
- S-FEAT-05 Publikumsnutzung: ALKIS-Gebäudefunktion (Liste alkis_public_functions, 36 Werte aus den Daten) oder
  OSM-shop/amenity-Punkt im Gebäude; Nebengebäude (alkis_ancillary_functions, 17 Werte, z. B. Garage, Gartenhaus) zählen
  nicht. Schulen/Kitas nicht als Publikumsnutzung, weil sie über S-FEAT-06 eingehen. Listen sind Annahmen (status draft).
- Wirkung (Arbeitsgebiet): Gebäudedichte Median 0,179 → 0,173; shop_frontage_share Mittel 0,19 → 0,33, Anteil ≥ 0,4
  (C-G30-01) 17 % → 27 %, null 14,5 % → 19,2 %; place_score Mittel 0,44 → 0,46 (Korrelation 0,97).
- Schema: Felder alkis_gebnutzbez, alkis_rellage_excluded, alkis_public_functions, alkis_ancillary_functions.
- s04_features prüft, dass alle Gebäudefunktionen aus rules.yaml in den ALKIS-Daten vorkommen.
