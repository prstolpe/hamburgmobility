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

## rules.yaml 0.7.0 – 2026-10-28
- Neu: Abschnitt `crosssection` für Straßenraumbreite und Machbarkeit (pipeline/s07_crosssection.py, prompts/07_crosssection.md).
  - S-XS-01 Transekte (vereinfachen 2 m, alle 20 m, ± 40 m, Tangente ± 10 m; Werte aus guide.md 4.3 a).
  - S-XS-02 Variante Verkehrsfläche: ALKIS nutzart Strassenverkehr, Weg, Platz (Werte aus den Daten); liefert width_p10_m
    für C-G30-02, weil required_width Grenze zu Grenze gilt. Mittelpunkt außerhalb → Transekt verworfen.
  - S-XS-03 Variante Fassade: erste oberirdische ALKIS-Gebäude links/rechts.
  - S-XS-04 Knoten (Grad ≠ 2) 20 m, Brücken/Tunnel aus OSM, open_space.
  - S-XS-05 Median, p10, Minimum, Engstellen (≥ 3 Transekte unter p10).
  - S-XS-06 Machbarkeit für GOW50, GOW30_narrow (Untergrenze 10,80 m), ETW30 mit feasibility_classes.
  Alle Werte assumption/draft.
- Schema: Modell `Crosssection`; Ziele müssen in required_width stehen.

## rules.yaml 0.8.0, sources.yaml 0.1.5 – 2026-10-28
- Neu: Abschnitt `classification_policy` für die Auswertung der Kaskade (pipeline/s05_classify.py, prompts/08_classify.md).
  - C-MISS-01: fehlende Werte mit dreiwertiger Logik (Kleene); eine Regel greift nur bei sicher wahrer Bedingung.
    Defaults für Merkmale ohne Datenquelle: outside_builtup_area = false, override_school_street = false,
    crossing_demand = not_assessed (zählt als nicht high). Entscheidung Projektteam 2026-10-28 (offene Frage aus Prompt 02).
  - C-CONF-01: confidence niedrig bei fehlendem entscheidendem Wert oder Wert innerhalb ±10 % einer Schwelle
    (near_threshold 0,10, Vorgabe aus prompts/08); mittel bei Fallback-Quellen (Schulen/Kitas aus OSM, in_hvs aus
    DTV-Linien 2019, conn_score mit umgelegtem Gewicht) und bei Defaults aus C-MISS-01; sonst hoch. Es zählen nur Werte,
    die das Ergebnis bestimmt haben. Entscheidung Projektteam 2026-10-28.
  - Schwellen der Kaskade unverändert.
- Schema: Modell `PolicyRule` (defaults, fallback_inputs, thresholds); IDs gehen in die Dublettenprüfung ein.
- sources.yaml: neuer Abschnitt `viewers` (keine Datenquellen) mit Linkformat für die Stichproben: Geoportal Hamburg
  (Masterportal, Layer 19968 „Digitale Orthophotos (belaubt) Hamburg mit Umland“, laut config.json) und Panoramax
  (Hash `#focus=map&map=zoom/lat/lon`, laut @panoramax/web-viewer 5.3.1).
- Wirkung (Arbeitsgebiet, 562 km): SW 28,4 km, GOW50 38,1, GOW30 57,5, ETW30 427,4, ETW_ERF 10,6; confidence nach
  Länge hoch 5,1 %, mittel 85,4 %, niedrig 9,6 %.


## rules.yaml 0.9.0 – 2026-10-28
- Abschnitt `coherence` für die Netzkohärenz (pipeline/s06_coherence.py, prompts/09_coherence_overrides.md) ausgebaut.
  Bestehende Schwellen (N2 200 m, N3 25 ha, N4 300 m) unverändert.
  - Alle Netzregeln haben jetzt `status: draft` (offene Frage aus Prompt 02).
  - N1: `boundary_tolerance_m` 50 m (assumption) für „endet an der Stadtgrenze“ (OSM admin_level 4);
    `gow_categories`, `end_ok_categories`.
  - N2: Straßenzug über `max_deflection_deg` 30° und `bearing_sample_m` 15 m (assumption).
  - N3: Kompaktheit wird nur berichtet; Flächen ohne ETW-Abschnitt (Verkehrsinseln, Grün) zählen nicht als
    Aufenthaltsbereich.
  - N4: Reisezeit mit Soll-Tempo, SW mit travel_speed_kmh (`speed_fallback`); highway=pedestrian gesperrt;
    OD-Paare ohne GOW/SW-Weg werden gezählt, nicht markiert.
  - N5: `gate_transitions` (GOW50→GOW30, GOW→ETW) und `min_speed_kmh` 70 / `target_speed_kmh` 30 (aus CROW-Tabelle 4).
  - N6: `node_types` nach guide.md Tabelle 1.4, `category_rank`, `ist_check` (Ist-Typ aus OSM: Kreisverkehr, Ampel,
    Plateau) und `signal_radius_m` 30 m (assumption). Knoten = OSM-Knoten (Entscheidung Projektteam 2026-10-28).
  - Neu N7: Glättungsvorschlag für N2-Inseln, nur als Flag.
- Schema: `CoherenceRule` mit status (Pflicht), thresholds und Prüfung der Kategorien, Rangfolge und ist_check.
- Korrekturebene: overrides/overrides.csv mit review_status draft | approved | rejected (Entscheidung Projektteam
  2026-10-28); nur approved wird übernommen (pipeline/s06b_overrides.py).
- Wirkung (Arbeitsgebiet): Flags N1 91 GOW-Enden, N2/N7 132 Abschnitte, N3 106, N4 1 082, N5 0, N6 758 Knoten mit
  Abweichung (siehe reports/coherence.md).


## sources.yaml 0.1.6 – 2026-10-28
- accidents (Unfallatlas): Basis-URL https://www.opengeodata.nrw.de/produkte/transport_verkehr/unfallatlas/ (OpenData-Seite
  laut unfallatlas.statistikportal.de), Unfalljahre 2021–2025 als `fetch.files`, Spalten und Codes laut
  Datensatzbeschreibung DSB_Unfallatlas.pdf (Stand 10.06.2025) in `fetch.points`; check_status verified.
- Hamburg (ULAND 02) ist in allen fünf Jahren enthalten: 6 397 / 7 174 / 7 332 / 7 031 / 7 057 Unfälle mit Personenschaden.
- s01_fetch lädt mehrere Dateien je Quelle (`fetch_download_files`) und zählt die Unfälle je Jahr; Einzelunfälle bleiben
  nur in den ZIPs in data/raw, es wird keine Punktebene geschrieben.

## rules.yaml 0.10.0 – 2026-10-28
- Abschnitte `discrepancy` und `priority` für pipeline/s08_discrepancy.py (prompts/10_discrepancy.md) ausgebaut.
  Bestehende Werte (+20 → 2, +30 → 3, max_dtv, risk_weights) unverändert. Lücken als Annahmen gefüllt (Entscheidung
  Projektteam 2026-10-28), alle `status: draft`:
  - D-SPD-01: Stufen als `levels`; neu Stärke 1 bei 1–19 km/h Überschreitung (assumption).
  - D-DES-01: `violations` übersetzen die Anforderungen in dreiwertige Bedingungen auf Ist-Merkmale; fehlende OSM-Tags
    sind unbekannt, kein Verstoß. Je Verstoß `direction` flow/sparse (assumption). Mitteltrennung über
    bahnigkeit_official; Abschnitte ohne Gegenrichtung zählen nicht.
  - D-USE-01: Profil track bei baulichem Radweg (ohne max_dtv), sonst wide; Stärke 2 ab 1,5-fach, 3 ab 2-fach (assumption).
  - D-TYPE-01: nur flow → D1, nur sparse → D2, beides → D3.
  - P-RISK-01: Komponenten-Zuordnung, Zuordnung der Unfälle zum nächsten Abschnitt ≤ 15 m, Mindestlänge 100 m für
    „je km“, Schule/Kita ≤ 150 m (wie C-G30-01), 5 Jahre; Normierung über den Perzentilrang (S-FEAT-01).
- Schema: Modelle für levels, violations, type_rule und risk; IDs D-*/P-* in der Prüfung auf doppelte IDs.
- Wirkung (Arbeitsgebiet, 4 787 Abschnitte): Diskrepanz bei 2 102 Abschnitten (201,7 km, 35,9 % der Länge),
  D1 1 824, D2 212, D3 66; Tempo-Diskrepanz Stärke 2 bei 1 713 Abschnitten (meist Ist 50 auf Soll 30).

## rules.yaml 0.10.1 – 2026-10-28
- Keine Werte geändert. Entscheidung Projektteam 2026-10-28 in `check`/`note` vermerkt: D-SPD-01 Stärke 1 bei
  1–19 km/h und P-RISK-01 snap_m 15 m / min_length_m 100 m freigegeben; D-USE-01 Faktoren 1,5/2,0 als Arbeitswert;
  Unfälle an Knoten vorerst beim nächsten Abschnitt, mit der Webkarte erneut prüfen.
- reports/priority_top30.md: neue Straßenliste (Top 30 Straßen, zusammengefasst nach Name) vor der Abschnittsliste.

## sources.yaml 0.1.7 – 2026-10-28
- Neu: Abschnitt `web_assets` (keine Pipeline-Quelle): Protomaps-Tagesbuild 20261028 (ODbL, Ausschnitt mit
  `make basemap`), basemaps-assets (Noto Sans, SIL OFL 1.1; Sprites MIT), Kartenstil @protomaps/basemaps (BSD-3-Clause).

## config/plain_language.yaml 0.1.0 – 2026-10-28
- Neu: Klartexte für Steckbriefe (je Regel der Kaskade mit Platzhaltern für Eingangswerte und Schwellen aus
  rules.yaml), Kategorien, Datenunsicherheit, Machbarkeit und die Datenbeschreibung der Downloads. Keine Schwellenwerte.
- Export (pipeline/s09_export.py) und Webseite (web/) für den Bezirk Eimsbüttel; Version der Seite = Regelversion +
  Datenstand (0.10.1+2026-10-28).

## rules.yaml 0.11.0 – 2026-11-04
- Neu: Abschnitt `validation` (pipeline/validate.py, guide.md Teil 7, prompts/12_validation.md). Alle Werte assumption.
  - V-SENS-01: Einzelvariation ±20 % jeder Annahme-Schwelle, die die Kaskade liest (conn_gow, sensitive_radius,
    frontage, required_width.GOW50); near_threshold wirkt nur auf die confidence.
  - V-SENS-02: 500 Monte-Carlo-Läufe, Seed 20261104; Gewichte (conn_score, risk_weights) und die Schwellen aus
    V-SENS-01 gemeinsam, je Faktor gleichverteilt in [0,8; 1,2].
  - V-UNC-01: „unsicher“ ab Wechselquote 0,3 (prompts/12: „ab 0,3“; guide.md P11 nennt „> 0,3“).
  - V-SAMP-01 (unter 15 % strittig je Kategorie) und V-DQ-01 (unter 5 % ohne Ist-Tempo) aus guide.md 7.1 bzw. 3.4 übernommen.
- Keine bestehenden Werte geändert; Kategorien unverändert.
- Schema: Modelle `Validation`/`ValidationRule` (runs, seed, vary), IDs V-* in der Prüfung auf doppelte IDs.
- Ergebnis (Arbeitsgebiet, 4 787 Abschnitte, 562,0 km): 293 Abschnitte (28,7 km, 5,1 % der Länge) unsicher;
  größte Einzelwirkung conn_gow −20 % (39,8 km wechseln, meist ETW30 → GOW30); Top 30 der Priorität im Mittel zu
  91,8 % stabil. 99,6 % der HVS-km sind GOW50/GOW30; 74,5 % der Soll-ETW30-km haben heute höchstens 30 km/h.
- Export: Spalten `sens_change_rate` und `sens_uncertain` in den Downloads, Robustheit im Steckbrief, Spalte
  „Robustheit“ in der Tabelle, Attribut `un` in den Kacheln; `make validate` läuft vor `make export`.

## config/plain_language.yaml 0.2.0 – 2026-11-04
- Neu: Abschnitt `sensitivity` (Texte zur Robustheit im Steckbrief, Namen der variierten Annahmen) und
  Spaltenbeschreibungen `sens_change_rate`, `sens_uncertain`.

## rules.yaml 0.12.0 – 2026-11-04
- Neu: S-NET-04 (assumption): benannte Zufahrten ins Netz – highway=service ohne Untertyp oder alley, highway=track
  mit Kfz-Zugang (motor_vehicle/motorcar/vehicle/access ∈ yes, destination, designated oder ohne Angabe). Fußwege,
  path, Parkplatzgassen und Grundstückszufahrten bleiben draußen. Hamburg: 930 service- und 515 track-Abschnitte
  (290,8 km); Eimsbüttel: 70 Abschnitte (9,0 km). segment_id: 2 526 neu, 502 entfallen (Eimsbüttel: 45 von 3 882),
  weil neue Einmündungen Abschnitte teilen; overrides.csv war leer.
- S-FEAT-02: exclude_highway um service und track ergänzt (kein Standardtempo für diese Klassen).
- Neu: Abschnitt `harmonisation`, Regel H-STR-01 (assumption, SWOV_FS_2023): kurze Läufe unter min_run_m (N2, 200 m)
  je Straßenzug angleichen – ETW30-Insel in GOW → GOW, GOW-Insel in ETW30 → ETW30, GOW50-Insel in GOW30 → GOW30,
  kurzes GOW30 in GOW50 bleibt und wird auf 200 m verlängert. Neue Stufe pipeline/s05b_harmonise.py (make classify);
  das Ergebnis der Kaskade bleibt als `cat_cascade`. Entscheidung Projektteam 2026-11-04.
- Wirkung (Arbeitsgebiet, 4 947 Abschnitte): 223 Abschnitte (11,5 km) angeglichen, davon GOW50 → GOW30 152 (9,0 km),
  ETW30 → GOW 65 (2,2 km); N2-Inseln 132 → 5 (nur ETW_ERF/ETW30); unsicher 258 Abschnitte (26,6 km).
- Schema: Felder für S-NET-04, Modelle `Harmonisation`/`HarmonisationRule`; validate wendet H-STR-01 in jedem
  Sensitivitätslauf an.

## config/plain_language.yaml 0.3.0 – 2026-11-04
- Text für H-STR-01 im Steckbrief, Spaltenbeschreibung `cat_cascade`.

## rules.yaml 0.13.0, sources.yaml 0.1.8 – 2026-11-04: ganz Hamburg
- Arbeitsgebiet ist ganz Hamburg statt des Pilotbezirks Eimsbüttel: alle sieben Bezirke (OSM admin_level 9 innerhalb
  der Stadtgrenze), Puffer 500 m. config/project.yaml: Abschnitt `area` ersetzt `pilot_district`; für Testläufe kann
  `districts` eine Liste sein. Gemeinsame Funktionen in pipeline/lib/area.py.
- Ausgeschlossen (Entscheidung Projektteam 2026-11-04):
  - Neuwerk samt Scharhörn und Wattenmeer (abgetrennter Teil von Hamburg-Mitte). In OSM umfasst der Stadtteil Neuwerk
    nur die Insel (7,6 km²); entfernt wird darum der ganze abgetrennte Polygonteil (226 km²).
  - 17 ländliche Stadtteile (Vier- und Marschlande, Süderelbe; 172,8 km²) werden nicht klassifiziert und auf der
    Karte grau gezeigt. Grund: Für `outside_builtup_area` (C-RUR-01) gibt es keine Datenquelle. Geprüft wurde, das
    Netz an den 145 Ortstafeln aus OSM (traffic_sign=city_limit) zu schneiden: Es bleibt ein zusammenhängendes Netz
    von 4 472 km über fast ganz Hamburg, weil in den Dörfern Ortstafeln fehlen; nur 26 Ways tragen DE:rural.
    Liste status: proposed (docs/open_questions.md).
- S-FEAT-01: Normierung über ganz Hamburg (note ergänzt). Schwellen unverändert; die Ergebnisse in Eimsbüttel ändern
  sich durch die neue Bezugsverteilung (reports/validation.md, Vergleich mit dem Pilotlauf).
- C-MISS-01: note zu `outside_builtup_area` aktualisiert.
- Abruf (s01): WFS und OGC API in Kacheln zu 10 km, doppelte Objekte an Kachelgrenzen entfernt.
- sources.yaml 0.1.8: DB Rad+ ohne bbox (ganz Hamburg); der Abruf scheitert seit 2026-11-04 aber auch ohne bbox
  (abgebrochenes JSON bei offset 1000) – Quelle bleibt „fehler“, keine Umgehung. Basemap-Ausschnitt: Arbeitsgebiet.
- Berichte: Tabellen je Bezirk, Stichproben nach Bezirk geschichtet, Prioritätenliste Top 30 Hamburg plus Top 10 je
  Bezirk. Webseite: Bezirksfilter mit allen Bezirken, Tabelle je Bezirk (data/out/table/), Bezirksgrenzen,
  Stil für GOW80/ETW60.

## overrides.csv – 2026-11-04
- 7 Korrekturen (approved, prstolpe) für HVS-Abschnitte, die C-ERF-01 zu ETW_ERF machte: Reeperbahn
  (`seg_3129d58aeb9c8e41`) und Sengelmannstraße Hauptfahrbahn (`seg_3b1d68013e44c2c9`) → GOW30; Sengelmannstraße
  Nebenfahrbahn und 4 Fußwege in Hamburg-Mitte → ETW_ERF bestätigt (in_hvs ist dort ein Abgleichfehler). Befund aus
  Datenanalyse, Ortsprüfung offen.
- tests/test_classification_data.py::test_hvs_is_never_etw: HVS als ETW ist nur mit approved Override erlaubt
  (guide.md 7.1, „einzeln begründen“).

## cycling_rules.yaml 0.1.0, design_rules.yaml 0.1.0 – 2026-11-05
- Neu: Regelwerke der Radnetz-Erweiterung (docs/guide_radnetz.md, prompts/14–21). Alle Regeln Entwurf.

## cycling_rules.yaml 0.1.1, design_rules.yaml 0.1.1 – 2026-11-05
- Nur Metadaten, keine Werte geändert (geprüft durch Vergleich aller Werte mit 0.1.0). Anlass: Schema-Prüfung
  (config/schema/cycling_model.py, design_model.py) verlangt für jede Regel und jeden Zahlenwert source_type
  und für jede Regel mit id einen status.
- `status: draft` an allen 49 Regeln mit id.
- cycling_rules: `trip_length_km` je Radkategorie als Eintrag mit `range` und Quelle (HAUPT/BASIS/ERSCHL:
  DCE_INFRA laut docs/guide_radnetz.md, Delft-Beispiel; RSV: assumption); `principle_weights`: assumption.
- design_rules: `lanes.default_per_direction`, L-02 und L-04 (Regelebene): assumption; PL-01 von swov_crow ohne
  Quelle auf assumption (Quelle fehlt); PL-03 Quelle ERA_2010 ergänzt (neu in `sources`).
- Vererbung: source/source_type gelten für alle Einträge darunter (Kommentar im Dateikopf).

## sources.yaml 0.1.9 – 2026-11-05
- Neu: `cycle_network_official` – WFS Radnetz Hamburg (https://geodienste.hamburg.de/wfs_radnetz, dl-de/by-2.0),
  Feature-Typen radnetz und radrouten. `cycle_network` bleibt OSM-Fallback für S-FEAT-07 (Umstellung offen).
- Neu: `bike_counters` – Rad-Dauerzählstellen (SensorThings, Datensatz „Verkehrsdaten Rad (Infrarotdetektoren)
  Hamburg“), 312 Zählstellen mit Tageswerten 2025; neuer Zugriffstyp `sensorthings_counters` in s01_fetch.py.
- Neu: `traffic_signals` (OSM-Fallback highway=traffic_signals; amtliches Verzeichnis offen), `universities`
  (OSM-Fallback amenity=university|college), `centres` (url null, Zentrenkonzept offen).
- `fallback_osm.columns`: gewünschte OSM-Spalten je Fallback-Quelle.
- purpose ergänzt bei bike_volumes_dbradplus (nur Plausibilität), schools, gtfs_hvv, osm (Radinfrastruktur aus dem PBF).

## sources.yaml 0.1.10 – 2026-11-05: DB Rad+ abrufbar
- Ursache des abgebrochenen DB-Rad+-Abrufs gefunden: einzelne Datensätze liefert der Server mit HTTP 500
  (z. B. `jahr2025?limit=1&offset=1581`, Error ID 8c3d758741fc1e75); Seiten mit einem solchen Datensatz brechen mit
  HTTP 200 mitten im JSON ab.
- Neu: `fetch.skip_broken_records: true` (nur bike_volumes_dbradplus, Entscheidung 2026-11-05). Der Abruf halbiert eine
  fehlerhafte Seite bis zum einzelnen Datensatz, überspringt ihn und protokolliert den offset in data/manifest.json
  (`skipped_records`) und reports/data_report.md (pipeline/lib/ogcapi.py `get_items_skipping_broken`). Prüfung
  numberMatched = geladen + übersprungen; mehr als 100 defekte Datensätze oder gar keine lesbare Seite bricht ab.
- Ergebnis 2026-11-05: 150 778 Linien im Arbeitsgebiet, übersprungen offset 1581, 36024, 40622.

## cycling_rules.yaml 0.2.0 – 2026-11-05: Radgraph und Nachfragemodell (Prompt 15)
- Alle neuen Werte sind Vorschläge (source_type assumption, status draft) und fachlich freizugeben
  (docs/open_questions.md). Bestehende Werte unverändert.
- `routing_impedance.ist_mapping` (C-IMP-01…08): Ist-Widerstandsfaktor je Kante, erste zutreffende Regel; Tempo-Grenze
  30 km/h, Erschließungskategorien, unbefestigte Beläge. C-IMP-06 (Hauptstraße Tempo 30 ohne Radstreifen) nutzt
  vorläufig `gow30_cycle_lane`, weil `factors` dafür keinen Wert hat.
- `cycle_graph` (C-GRAPH-01…06): Kantenauswahl, Einbahnstraßen (Gegenrichtung nur mit oneway:bicycle=no), Fähren
  (Wartezeit 450 s, Anbindung ≤ 400 m mit Anbindungsstrecke im Widerstand), LSA- und Wartepflicht-Verzögerung,
  Bezug eigenständiger Wege zum Straßenabschnitt (Werte wie S-CONF-01), Radgeschwindigkeit 15 km/h für die
  Umrechnung von Wartezeiten.
- `demand_model` (C-DEM-01…07): Zonen 500 m, Zielgewichte, Arbeitsplatz-Proxy aus ALKIS, Gravitationsmodell
  exp(−0,25·d) im Band 0,5–15 km, stochastische Umlegung (3 Läufe, σ 0,1, Seed 42), Kalibrierung mit einem Faktor
  an den Zählstellen ohne Richtung (Mo–Fr 2025), demand_confidence.
- Schema config/schema/cycling_model.py: neue Abschnitte, Prüfung der Bedingungsnamen und Faktorschlüssel,
  Zielgewichte summieren zu 1, Distanzband und Umlegungsverfahren.
- pipeline/lib/network.py: `segment_id`/`segments_from_edges` mit optionalem Präfix und Mitgliedskanten
  (Standard unverändert, segment_id bleibt gleich).
- Neue Abhängigkeiten: scipy (kürzeste Wege), matplotlib (Abbildungen im Report).
