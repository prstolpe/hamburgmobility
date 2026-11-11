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

## cycling_rules.yaml 0.3.0 – 2026-11-06: Netzentwurf (Prompt 16)
- Neuer Abschnitt `network_design` (C-NET-01…13), alle Werte Vorschläge (source_type assumption, status draft) und
  fachlich freizugeben (docs/open_questions.md). Bestehende Werte unverändert; Schwellen der Hierarchie kommen weiter aus
  `cycle_categories` (RSV-Auslöser 2.000 Rad/Werktag, 5 km, Maschenweiten) und `principles` (P-ATT-03, P-DIR-01, P-COH-03).
  - C-NET-01/02 Korridorpunkte und -paare: Innenstadt (Rathausmarkt), Umsteigeknoten (≥ 2 Verkehrsmittel im Umkreis 250 m;
    im HVV-GTFS sind U- und S-Bahn getrennte Stationen), OSM amenity=university, Arbeitsplatzschwerpunkte (98-%-Quantil),
    Zusammenfassen ab 500 m, 4 nächste Punkte bis 15 km plus Innenstadt. Ohne Zentren (Entscheidung 2026-11-06).
  - C-NET-03 Soll-Widerstand je cat_final aus `routing_impedance.factors`; C-NET-04 Nachfragebonus bis −30 %;
    C-NET-05 Bonus amtliches Radnetz × 0,8, Bestand = amtlich, übrige Status = geplant (Entscheidung 2026-11-06).
  - C-NET-06 RSV-Läufe (Lücken bis 500 m); C-NET-07 Maschen mit Barrieren und Ausschlussflächen; C-NET-08 Verdichtung
    (Kernbereich 0,5, 40 Runden, Teilungsroute ≥ 50 m); C-NET-09 Anbindung Schulen/Nahversorgung ab 150 m;
    C-NET-10 P-ATT-03 (Läufe ab 300 m, ≤ 60 m an der Hauptstraße); C-NET-11 Kontinuität (200 m); C-NET-12 ERSCHL;
    C-NET-13 Vergleichspuffer 20 m.
- Schema config/schema/cycling_model.py: `network_design` mit Prüfung der Regel-IDs, Faktorschlüssel, Bonusbereiche und
  Statuslisten.
- pipeline/lib/gtfs.py: `rapid_transit_stations` liefert zusätzlich `route_types`/`n_route_types` je Station.
- pipeline/lib/overrides.py: Prüfung und Anwendung von overrides/cycle_network_overrides.csv.
- Neu: pipeline/c03_cycle_network.py, pipeline/lib/cycle_network.py; Ausgaben data/interim/cycle_network.parquet,
  cycle_routes.parquet, cycle_mesh_gaps.parquet, reports/cycle_network.md (+ drei Karten).


## cycling_rules.yaml 0.4.0 / sources.yaml 0.1.11 – 2026-11-06: Fünf Prinzipien prüfen (Prompt 17)
- Neuer Abschnitt `principle_scoring` (C-PRI-01…16), alle Werte Vorschläge (source_type assumption, status draft) und
  fachlich freizugeben (docs/open_questions.md). Schwellen der Prüfungen (`principles`), Gewichte (`principle_weights`),
  Breiten, Trennungsmatrix und Widerstandsfaktoren bleiben unverändert; C-PRI regelt nur, wie aus Prüfwerten Scores werden.
  - C-PRI-01 Score-Formen je Prüfung (share, ratio, inverse_ratio, excess, percentile_inverse), unbekannt ≠ gut,
    nicht anwendbar zählt nicht; C-PRI-02 Ist-Führung aus der Ist-Widerstandsregel, begleitende Radwege;
    C-PRI-03 Erfüllung der Trennungsmatrix (voll/teilweise 0,5).
  - C-PRI-04 Umwegfaktor je Route und Netzstichprobe (200 OD-Paare je Kategorie, Seed 42, Band trip_length_km);
    C-PRI-05 Halte (LSA, Wartepflicht nach C-GRAPH-05) und Zeitverlust; Soll = Ist bis Prompt 20.
  - C-PRI-06 Beleuchtung (OSM lit); C-PRI-07 Unfälle mit Radbeteiligung je km (snap_m/min_length_m aus P-RISK-01);
    C-PRI-08 Breite gegen widths_m.project_target (eigene Wege vorläufig wie Zweirichtungsradweg);
    C-PRI-09 Belag; C-PRI-10 Grünanteil 20-m-Puffer aus ALKIS-Nutzung und OSM-Bäumen (Ziel 30 %, Kronenradius 4 m);
    C-PRI-11 P-ATT-03 Anteil an Straßen mit DTV > 15 000; C-PRI-12 Maschenrand, Komponenten, Wechsel je km (Schwelle 1);
    C-PRI-13 confidence (high ab 0,8, medium ab 0,6); C-PRI-14 Gewichts-Sensitivität ±20 %, Top 30;
    C-PRI-15 Stichprobe 20 Routen; C-PRI-16 nicht bewertbar: P-SAF-02 (Prompt 20), P-COM-03 (kein Höhenmodell),
    P-ATT-02 (keine Lärmkarte, Entscheidung 2026-11-06).
- sources.yaml: purpose von alkis (green_share) und osm (lit, surface, trees) ergänzt; keine neuen Endpunkte.
  Straßenbaumkataster und Lärmkarten bleiben ohne Endpunkt (Entscheidung 2026-11-06: ALKIS + OSM-Bäume, Lärm unbewertet).
- Schema config/schema/cycling_model.py: `principle_scoring` mit Prüfung der Regel-IDs, Score-Formen je Prüfung,
  Führungsnamen, Breitenverweise, confidence-Klassen und unavailable-Prüfungen.
- Neu: pipeline/c04_principles.py, pipeline/lib/principles.py; Ausgaben data/interim/cycle_principles.parquet
  (Zeilen je edge_id und route_id), reports/cycle_principles.md (+ sechs Karten), reports/cycle_principles_review.csv.

## cycling_rules.yaml 0.5.0 – 2026-11-06: Führungsform und Breite (Prompt 18)
- Neuer Abschnitt `facility_assignment` (C-FAC-01…07), alle Werte Vorschläge (source_type assumption, status draft) und
  fachlich freizugeben (docs/open_questions.md). Trennungsmatrix, cycle_street, S-04 und widths_m bleiben unverändert.
  - C-FAC-01 Soll-Führung aus der Matrix; Fallback nur bei space_fits_preferred = false (Prompt 19), sonst Flag
    fallback_check_p19; ETW60-Fallback mixed nur bei DTV ≤ mixed_rural_max_dtv; Radkategorie je Abschnitt = höchste der Kanten.
  - C-FAC-02 Fahrradstraße nur bei Kfz/Tag ≤ max_motor_vehicles_day und Rad ≥ Kfz in der Spitzenstunde, sonst mixed und
    Flag cycle_street_blocked. Ohne DTV vorläufig erfüllt (Entscheidung Projektteam 2026-11-06, Flag dtv_unknown).
  - C-FAC-03 S-04 bei mixed: Kfz/h = DTV × motor_peak_hour_share 0,10 (aus der Notiz zu L-02, Annahme); Flag mixed_over_s04.
  - C-FAC-04 Sollbreite = project_target + intensity_upgrade, Untergrenze de.*.min (Radfahrstreifen: CROW gow30_cycle_lane.min,
    weil ERA dort keinen Mindestwert nennt); Vergleichswerte DE-Regelmaß und NL-Hauptnetz.
  - C-FAC-05 Ist-Klasse aus OSM (cycle_street/track/lane/shared_lane/no) und Abbildung auf die Führungsnamen; begleitende
    Radwege auf beiden Seiten → Radweg je Seite.
  - C-FAC-06 facility_gap (missing/wrong_type/too_narrow/none/not_assessed) mit C-PRI-03 satisfies/partial;
    C-FAC-07 facility_confidence.
- Schema config/schema/cycling_model.py: `facility_assignment` mit Prüfung der Regel-IDs, Breitenpfade, Ist-Klassen und Flags.
- Neu: pipeline/c05_facility.py, pipeline/lib/facility.py; Ausgaben data/interim/cycle_facility.parquet (je segment_id),
  reports/cycle_facility.md. Goldene Fälle Führung/Breite (tests/golden/cycling/s*) ohne xfail.

## design_rules.yaml 0.3.0 – 2026-11-06: Knotenpunkte (Prompt 20)
- J-01 `else_if`: informelles „space ok“ ersetzt durch `space_radius_m >= roundabout_min_radius` (gleiche Platzschwelle
  wie der einstreifige Kreisverkehr; eigener Platzbedarf für Turbokreisverkehre fehlt, offene Frage). Schwellen unverändert.
- Neuer Abschnitt `junctions.method` (J-M-01…07), alle Setzungen Annahmen (source_type assumption, status draft):
  - J-M-01 Knoten: Grad ≥ 3 und Anschluss eigenständiger Radwege (cycleway oder RSV/HAUPT/BASIS, kein begleitender
    Radweg); Zusammenfassung über Abschnitte ≤ cluster_radius_m 25 m (Startwert aus Prompt 20) und ganze Kreisverkehre.
  - J-M-02 Arme und Zufluss: ½ DTV je Arm; ETW-Arme ohne DTV zählen 0; Richtungsfahrbahnen (gleicher Name, gleicher DTV,
    Richtung ≤ 30°) bilden einen Arm, weil der amtliche DTV auf beiden Fahrbahnen als Querschnittswert steht.
  - J-M-03 Platz: größter einbeschriebener Kreis in der ALKIS-Verkehrsfläche (S-XS-02) im Umkreis 40 m; umschlossene
    Inseln zählen als Fläche (sonst hätten bestehende Kreisverkehre wegen der Mittelinsel zu wenig Platz).
  - J-M-04 Kategoriepaar wie N6 (durchgehender Zug zählt einmal) statt wörtlich „die beiden ranghöchsten Arme“;
    category_alias ETW_ERF → ETW30.
  - J-M-05 Reihenfolge J-10, J-11, J-09, J-08, J-07, J-01…J-06; unbekannte Bedingung → `then` der Zeile; `fallback`
    gilt, wenn `then` ein Kreisverkehr ist und der Platz nicht reicht.
  - J-M-06 Ist-Typ aus OSM und ist_check je Soll-Typ (Handlungsbedarf); J-M-07 Prioritätsreihenfolge.
- JC-01…JC-05: `applies_to`-Klauseln (Soll-Typ, Radkategorie, gequerte Straßenkategorie) als Annahme der Zuordnung.
- Schema (config/schema/design_model.py): `junctions.method`, Prüfung von evaluation_order, ist_check, category_alias und
  applies_to.

## design_rules.yaml 0.2.0 – 2026-11-06: Soll-Querschnitt (Prompt 19)
- Neuer Abschnitt `profile_assignment` (PRF-01…07), alle Setzungen Annahmen (source_type assumption, status draft),
  fachlich freizugeben (docs/open_questions.md). lanes, placement und cross_section_allocation bleiben unverändert;
  Werte werden über Pfade auf bestehende Einträge verwiesen (lane_width_m, elements_min_m, widths_m, C-G30-01 frontage).
  - PRF-01 Ist-Fahrstreifen (amtlich vor OSM), Einrichtungsverkehr, ohne DTV Soll = Ist (höchstens 2 je Richtung).
  - PRF-02 Busse und Straßenbahnen je Spitzenstunde und Richtung aus GTFS (Abfahrtsstunde der ersten Haltestelle,
    stärkste Stunde der stärkeren Richtung; Entscheidung Projektteam 2026-11-06).
  - PRF-03 Bausteine je Kategorie: Gehwege beidseitig (nicht ETW_ERF), Radanlage je Führungsform, Baumstreifen an GOW,
    Ladezone bei Geschäftsnutzung, Parken nur wo OSM heute Parken zeigt (Entscheidung 2026-11-06).
  - PRF-04 Fahrbahnbreiten je Kategorie und Fahrstreifenzahl; SW/GOW80/ETW60 ohne Profilregeln.
  - PRF-05 Passung gegen width_p10_m (Verkehrsfläche, maßgeblich) und facade_width_p10_m (Potenzial).
  - PRF-06 Kaskade D1, D2, Fallback der Matrixzelle (Entscheidung 2026-11-06), D3, D4, D5, D6/D7 nur als Flag.
  - PRF-07 PL-02/PL-05 nicht prüfbar (Flag pl02_unchecked).
- Schema config/schema/design_model.py: `profile_assignment` mit Prüfung der Regel-IDs, Kaskadenstufen, Bausteine,
  Führungsformen und Kategorien.
- Neu: pipeline/c06_cross_section_soll.py, pipeline/lib/profile.py, GTFS-Hilfen in pipeline/lib/gtfs.py
  (trip_start_hours, hourly_trips_per_shape, shape_direction); Ausgaben data/interim/cross_section_soll.parquet,
  reports/cross_section_soll.md, reports/profiles_sample/*.svg. Goldene Fälle Fahrstreifen/Busfahrstreifen ohne xfail.

## config/plain_language.yaml 0.4.0 – 2026-11-07: Webseite und Validierung Radnetz (Prompt 21)
- Keine Regeländerung (rules.yaml, cycling_rules.yaml, design_rules.yaml unverändert).
- Neuer Abschnitt `cycling`: Klartexte für Radnetz-Ebenen, Steckbriefe (Abschnitt und Knoten), Legenden und die
  Datenbeschreibung der neuen Downloads (`cycling.columns`).
- Export (pipeline/s09_export.py, pipeline/lib/export_cycling.py): tiles/cycling.pmtiles (cycle_network,
  cycle_segments, cycle_official) und tiles/junctions.pmtiles getrennt von segments.pmtiles, damit die Seite erst bei
  Bedarf lädt; Radnetz-Block in jedem Abschnitts-Steckbrief (Kategorie, Führung, Breite mit DE- und NL-Wert, Lage,
  Fahrstreifen, Soll-Profil, Abbaustufen, Prinzipien Ist/Soll, Robustheit); junctions/{node_id}.json; Downloads
  cycle_segments.*, junctions.*, cycle_network.parquet, cycling_rules.yaml, design_rules.yaml.
- Webseite: Ebenen „Radnetz (Soll)“, „Radanlagen (Soll)“, „Radanlagen Soll/Ist“, „Fahrstreifen Soll/Ist“,
  „Querschnitt passt?“, „Knotenpunkte“, „Radnetz Hamburg (amtlich)“; Legenden mit Linienstil bzw. Symbolform;
  Querschnitts-Skizze im Steckbrief; Knoten-Steckbrief; Methodenseite „Radnetz“; Hinweis „nicht amtlicher Entwurf“
  auf allen neuen Ebenen. Die Radanlagen sind in zwei Ebenen geteilt (Soll; Soll/Ist), damit jede Legende lesbar bleibt.
- Validierung pipeline/c08_validate_cycling.py → reports/validation_cycling.md, reports/validation_cycling_review.csv,
  data/interim/validation_cycling.parquet: Vergleich mit dem amtlichen Radnetz je Bezirk, Modell vs. Zählstellen,
  Sensitivität aller assumption-Werte ±delta (V-SENS-01) mit Neuberechnung der Stufen c05–c07 auf gespeicherten
  Eingängen, Stand der Stichproben, offene Fragen und Grenzen. `make export-cycling` = c08 + Export.
- pipeline/lib/profile.py: öffentlicher Name ELEMENT_COLOURS für die Legendenfarben (Werte unverändert).

## cycling_rules.yaml 0.6.0, plain_language.yaml 0.4.1 – 2026-11-07: dichteabhängige Maschenweite; Radweg statt Fahrradstraße als Teilerfüllung
- Entscheidung prstolpe 2026-11-07 (docs/open_questions.md, Prompt 16, Delfter Maschenweiten): C-NET-07 `density_scaling`.
  Höchstweite je Masche = mesh_m.max × √(Referenzdichte / Einwohnerdichte der Masche), nie unter mesh_m.max; Maschen
  ohne Einwohner werden nicht geteilt. Neue Annahme `reference_density_per_km2` 4 400 (Delft, am Original prüfen),
  gilt für HAUPT und BASIS. Einwohner aus dem Zensus-2022-Gitter (bereits in sources.yaml). Probelauf: HAUPT 2 027 → 1 862 km,
  RSV/HAUPT auf ETW30 1 250 → 1 148 km, zu große Maschen nach Verdichtung 836 → 444 (Wald, Hafen, Wasser fallen weg).
  mesh_m-Werte unverändert. reports/cycle_network.md: Spalte „über mesh_m.max“ zusätzlich zur Höchstweite je Masche.
- Entscheidung prstolpe 2026-11-07 (docs/open_questions.md, Prompt 18, „Soll Fahrradstraße, Ist baulicher Radweg auf
  248 km“): Ein baulicher Radweg (beidseitig oder Zweirichtung) an einer ETW30-Hauptroute erfüllt die Soll-Fahrradstraße
  teilweise. C-PRI-03 `partial.cycle_street` um separated_oneway_both und separated_twoway ergänzt (P-SAF-01 dort
  partial_score statt 0).
- C-FAC-06: neue Stufe `partial` zwischen missing und wrong_type: Ist erfüllt das Soll nicht, ist aber Teilerfüllung
  (C-PRI-03 partial oder Fallback der Zelle). Betrifft auch Zweirichtungs- statt beidseitiger Radwege und Ist = Fallback;
  beide waren bisher wrong_type mit gap_partial = true. Keine Schwelle geändert.
- C-FAC-06 `category_check`: Flag `track_on_access_road` („Straßenkategorie prüfen“) bei Radweg an ETW30 mit
  Soll-Fahrradstraße, weil ein Radweg auf eine verbindende Funktion der Straße hindeutet.
- Webseite: Legende „Radanlagen Soll/Ist“ mit eigener Linie für „teilweise“; Klartexte in plain_language.yaml.

## design_rules.yaml 0.4.0 – 2026-11-07: Knotenpunkte (Entscheidungen prstolpe, offene Fragen Prompt 20)
- J-12 neu: eigenständiger Radweg des Radnetzes (RSV/HAUPT/BASIS) quert ETW30 → Radwegfurt mit Vorrang (wie J-08).
  Vorher 412 Knotenpunkte ohne Zeile (`no_rule`); Radwege des Quartiersnetzes bleiben ohne Soll-Typ. Rechtslage prüfen.
- J-03 (GOW30+GOW30) mit den DTV-Grenzen von J-01: einstreifiger Kreisverkehr bis roundabout_max_dtv, Turbokreisverkehr
  bis turbo_max_dtv, darüber LSA (geschützte Kreuzung); ohne Platz weiter eingefärbte Vorfahrt (fallback). Keine neuen Werte.
- J-13 neu: ETW30+ETW_ERF → Gehwegüberfahrt wie N6. J-M-04: Zeilen mit ETW_ERF prüfen das Paar vor category_alias.
- J-M-06 `signal_assignment: nearest_junction`: jede Ampel zählt im Ist nur für den nächstgelegenen Knotenpunkt im Umkreis
  N6.signal_radius_m (vorher jeder Knotenpunkt im Umkreis; 1 169 Gehwegüberfahrten hatten Ist „LSA“).
- Goldene Fälle j15 (J-12) und j16 (J-13).

## rules.yaml 0.14.0, design_rules.yaml 0.5.0, cycling_rules.yaml 0.7.0, plain_language.yaml 0.4.2 – 2026-11-07: Stapel 3
Entscheidungen prstolpe 2026-11-07 (docs/open_questions.md, Prompts 08, 14, 19).
- rules.yaml C-G30-01: Auslöser Schule/Kita/Publikumsnutzung auf Hauptverkehrsstraßen nur bis `gow30_max_dtv`
  10 000 Kfz/24h (CROW_GOW30_2023, gleich requirements.GOW30.profiles.wide.max_dtv; das Schema prüft die Gleichheit).
  Neu C-G50-02 (nach C-G30-02): Umfeld spräche für 30, DTV darüber → GOW50 mit Hinweis „Tempo-30-Abschnitt vor Ort
  prüfen“. Fehlt der Platz für einen baulichen Radweg, bleibt GOW30 über C-G30-02. Neues Eingangsmerkmal `dtv_official`
  (auf Hauptverkehrsstraßen immer vorhanden); goldene Fälle um dtv_official ergänzt (HVS 8 000, sonst 2 000, beides unter
  der Grenze), neue Fälle 28–30.
- design_rules.yaml lane_width_m.ETW30_mixed 5,80 → 4,75 m (RASt 06 Bild 17, Begegnung Lkw/Pkw bei verminderter
  Geschwindigkeit; aus Erinnerung, am Original prüfen). 5,80 m war die Untergrenze des CROW-GOW30-Profils. Bus 6,50 m bleibt.
- cycling_rules.yaml C-FAC-04: eigene Trasse (own_path) erhält Sollbreite, Untergrenze und Vergleichswerte des
  Zweirichtungsradwegs. Die Lücke bleibt für own_path „nicht bewertet“ (C-FAC-06 not_assessed_soll).
- plain_language.yaml: Texte für C-G50-02 und den Grund „zu viel Verkehr für eine Stadtstraße 30“.
- cycling_rules.yaml routing_impedance.factors.gow50_cycle_lane_or_mixed 2,0 → 1,5 (C-IMP-07, Hauptstraße ohne erfasste
  Radanlage), an den Zählstellen kalibriert: Probelauf Spearman 0,53 → 0,56, mittlere Abweichung 154 % → 113 %. OSM-Prüfung:
  83 km Straßen mit Radweg-Tag ohne nutzbare Kante im Radgraphen, davon 3 km im Umkreis 100 m der Zählstellen.

## sources.yaml 0.1.12 – 2026-11-07: Lizenzen Tempo und Verkehrsmengen
- speed_limits und traffic_volumes: Lizenz dl-de/by-2.0 laut Transparenzportal (die OGC API api.hamburg.de nennt keine),
  Namensnennung „Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (BVM)“, Link license_info.
  Die Steckbriefe zeigten bisher „Lizenz in der Quelle nicht angegeben (wird geklärt)“; dtv_official und das Ist-Tempo
  stehen in Downloads und Steckbriefen, die Namensnennung ist daher nötig.
- gtfs_hvv: Prüfung 2026-11-07, noch kein Feed für die Fahrplanperiode ab Dezember 2026.

## rules.yaml 0.15.0, plain_language.yaml 0.4.3 – 2026-11-07: Tempo-30-Obergrenze zurückgenommen
- Entscheidung prstolpe 2026-11-07: Das Umfeld (Schule/Kita, Publikumsnutzung, Querungsbedarf) hat Vorrang vor der
  heutigen Verkehrsmenge. C-G30-01 wieder ohne DTV-Obergrenze, C-G50-02 und Schwelle gow30_max_dtv entfernt (wie 0.13.0).
  GOW30 über dem CROW-Profil bleibt sichtbar über das Flag gow30_dtv_above_profile im Soll-Querschnitt (setzt weniger
  Kfz-Verkehr voraus). Die Regel soll später verbessert werden.
- Goldene Fälle: 28 erwartet jetzt GOW30 auch bei hohem DTV, Grenzfall 30 entfällt; dtv_official bleibt in den Fällen
  (wird nicht mehr gelesen).

## rules.yaml 0.16.0, design_rules.yaml 0.6.0 – 2026-11-07: Stapel 5 (Sammelfreigabe prstolpe, docs/open_questions_batch5.md)
- S-CONF-04: in_hvs auch bei match partial, wenn der Abschnitt über Abschnitte gleichen Namens mit einem exact-Treffer
  verbunden ist (in_hvs_source = neighbour); Wege aus S-NET-04 (service, track) nie HVS (parallele Nebenfahrbahnen).
- S-CONF-03 text_values: „5-7 km/h“ (verkehrsberuhigt) = 7 km/h, der Rechenwert von ETW_ERF.
- S-FEAT-05: ohne Gebäude im Puffer shop_frontage_share = 0 (vorher leer).
- Neu S-FEAT-11 parallel_cycle_route_present (OSM-Radwege mit Radfreigabe und amtliches Radnetz Bestand, gleich gerichtet
  im Puffer 200 m wie P-ATT-03); D-DES-01 GOW50 „Radweg oder Parallelroute“ damit prüfbar.
- Neu S-XS-07: fehlende Breite vom angrenzenden Abschnitt gleichen Namens (Flag width_from_neighbour, in C-CONF-01 Fallback).
- N3: Bahn und Flüsse/Kanäle (ohne Tunnel) begrenzen Aufenthaltsbereiche (Werte wie C-NET-07). N4: neues Flag
  N4_gow_gap für ETW-Abschnitte auf Verbindungen ohne GOW/SW-Weg (Lücke im GOW-Netz).
- design_rules.yaml L-06: Korrekturebene overrides/lane_overrides.csv (Fahrstreifen je Richtung, Busfahrstreifen; nur
  approved), ersetzt L-02 bis L-06 für den Abschnitt (rule_trace L-OVR, Spalte lanes_source).
- CLAUDE.md: Prüfdateien in reports/ dürfen EPSG:4326 sein.
- Nicht umgesetzt (Probelauf, Entscheidung offen): in_hvs aus conn_score nehmen (+430 km GOW).

## rules.yaml 0.17.0, cycling_rules.yaml 0.8.0, design_rules.yaml 0.7.0 – 2026-11-08: Review 2026-11, Paket P0 (Grundlagen)
- Neuer Regelstatus `inactive` (Strukturempfehlung 5) in allen drei Schemas: Regel bzw. Block ohne Datengrundlage,
  greift nie, senkt confidence nicht und zählt nicht als abgedeckt (`active_rule_ids`, `collect_ids(active_only=True)`).
  Die Kaskade prüft inaktive Regeln nicht; rule_trace führt sie als `{id, passed: false, result: null, status: inactive}`.
  Ein `status` an Blöcken ohne id wird in cycling/design_rules jetzt ebenfalls geprüft; die Default-Regel darf nicht
  inaktiv sein.
- F28: C-RUR-01 und cycling_rules `separation_matrix.rural` auf `inactive` (keine Datenquelle für die Ortsgrenze),
  Notiz „bei Aktivierung `or in_hvs` ergänzen“; N5: Notiz, dass die GOW80/ETW60-Teile ohne Wirkung sind. c04/c05
  vergeben für GOW80/ETW60 keine Soll-Führung, solange die Zeile inaktiv ist. Ergebnis: keine Kategorie ändert sich;
  `fallback:outside_builtup_area` senkt confidence nicht mehr (1 777 Abschnitte mittel → hoch, Längenanteil hoch
  4,3 % → 7,0 %). Goldene Fälle 03–06 und cycling s13/s14 prüfen die Regeln mit `activate` (eingeschaltet); neuer Fall
  30_rural_inactive zeigt, dass C-RUR-01 nicht greift.
- F33: design_rules PL-02 `inactive` und `scope: rural` (separated_twoway vergibt nur die inaktive Außerorts-Matrix);
  cycling_rules S-03 `scope: rural` mit Notiz (bleibt draft, C-PRI-03 begründet damit die Teilerfüllung);
  PRF-07 Notiz (Teil PL-02 nur außerorts, Teil PL-05 gilt innerorts, bleibt draft). Neues Feld `scope` (Kennzeichnung).
- F27 / Strukturempfehlung 4: Klassentabellen sind halboffen `[min, max)`, dokumentiert in den Dateiköpfen; Schema prüft
  Lückenlosigkeit und Überlappungsfreiheit (feasibility_classes, demand.intensity_classes_peak_h,
  config/schema/intervals.py). `feasibility_class` liest die Intervalle aus der Tabelle (Ergebnis wie bisher:
  1,00 → fits, 0,85 → tight; goldener Fall G11). intensity_upgrade jetzt `peak_h >= 750` bzw. `>= 350` (bisher `>`),
  muss an einer Klassengrenze beginnen; in den Daten liegt kein Wert genau auf der Grenze, keine Ergebnisänderung.
- F31: Notizen S-FEAT-04 (Zensus-Gitter) und S-FEAT-08 (GTFS) aktualisiert – beide liegen in data/raw und werden genutzt.
- F32: `requirements`-Breiten, die auch in cycling_rules `widths_m` stehen, tragen `ref:` mit dem Pfad dorthin
  (GOW50 cycle_track_width_m, buffer_to_parking_m; GOW30 cycle_lane_width_m, cycle_lane_width_de_m); ein Test prüft die
  Gleichheit (`requirement_ref_mismatches`). Werte unverändert.
- Herkunft ergänzt: `categories.*` mit source/source_type (speed_kmh; ETW_ERF 7 km/h als assumption),
  `scores.conn_score`, `scores.place_score` und `priority` (formula, risk_weights) mit `source_type: assumption` als
  Schlüssel statt YAML-Kommentar. Gewichte unverändert.

## rules.yaml 0.18.0, plain_language.yaml 0.5.0 – 2026-11-08: Review 2026-11, Paket P1 (Klassifikation)
- F05: Eine Machbarkeitsrechnung. `required_width.GOW50` 17,00 m, `GOW50_bus` 17,50 m, `ETW30` 9,75 m (vorher 16,50 /
  17,00 / 10,80) als Mindestprofil aus design_rules (Gehweg min 2,50, Trennstreifen 0,75, Fahrbahn 6,50 / 7,00 / 4,75)
  plus ERA-Radweg 2,00 aus cycling_rules; `formula` nennt die Pfade (D./C.) und ergibt genau diese Werte. Neuer Test
  „value = formula“ (Invariante V-INV-06, `required_width_formula_mismatches`). Einzelmaße `sidewalk_m` und
  `carriageway_2lane_m` entfallen (doppelt zu design_rules). Goldene Fälle 26/27 = G02 (16,99 → GOW30, 17,00 → GOW50).
- F06: C-G30-02 nur über den Raum: `(not bus_route and width_p10_m < GOW50) or (bus_route and width_p10_m < GOW50_bus)`;
  ein vorhandener Radweg zählt nicht mehr. `bus_route` = Busse je Spitzenstunde und Richtung (PRF-02, gleiche Rechnung
  wie c06, Funktion `transit_peak` nach pipeline/lib/transit.py verschoben) ≥ S-FEAT-08 `bus_route_min_peak_h_dir` 1;
  neue Merkmale `bus_peak_h_dir`, `bus_route` in s04. Flag `existing_track_below_floor` in c05 (`facility_flags`), wenn
  die Ist-Breite des Radwegs bekannt ist und unter C-FAC-04 floor liegt. Goldener Fall 18 = G03 (Bestandsradweg 1,20 m,
  15,0 m → GOW30), neue Fälle 31/32 (Busroute an der Grenze 17,50 m).
- F07 (Q2 b): C-G30-01 liest `school_or_kita_access_m <= access_radius` (50 m, assumption) statt
  `schools_or_kitas_within_m <= sensitive_radius` (150 m). Näherung: Abstand zur OSM-Fläche bzw. zum OSM-Punkt
  (S-FEAT-06, docs/open_questions.md); `schools_or_kitas_within_m` bleibt für place_score und P-RISK-01
  (school_kita_radius_m 150 m). H-STR-01: `gap_close_m` 500 m (de_regelwerk, Quelle STVO_2024, Fassung prüfen):
  GOW50-Lauf zwischen zwei GOW30-Läufen unter 500 m wird GOW30 (umgesetzt in Schritt 3, siehe Notiz H-STR-01).
  Goldene Fälle 13, 22/23 (= G04: 50 m → GOW30, 51 m → weiter mit C-G30-02), 28 angepasst.
- F13 (Q3 b): `in_hvs` aus `conn_score` (Gewichte 0,45/0,30/0,25 statt 0,35/0,25/0,20/0,20). conn_gow neu kalibriert
  von 0,6 auf 0,87. Methode: Bezugsgröße = km der Abschnitte im Arbeitsgebiet mit `in_hvs = false`, die die Kaskade zu
  GOW50/GOW30 macht (`cat_proposed` in classified.parquet, vor H-STR-01); Stand 0.17.0: 78,0 km (= 0.16.0). Mit den
  neuen Gewichten aus den Normwerten in features.parquet nachgerechnet (bei 0,6: 507,9 km, die +430 km des Probelaufs);
  gewählt ist der zweistellige Wert mit der kleinsten Abweichung: 0,87 → 82,6 km (0,88 → 67,8 km). Kontrolllauf der
  Kaskade: 82,6 km, davon 76,9 km auch vorher GOW (5,7 km neu, 1,2 km entfallen). GOW gesamt (Kaskade) 746,5 → 751,0 km.
  Goldene Fälle 05/06 und 20/21 auf 0,87/0,86, 03 und 17 auf conn_score 0,95.
- F14: C-CONF-01 `global_caveats` [outside_builtup_area, override_school_street, crossing_demand, in_hvs,
  school_or_kita_access_m]: senken confidence nicht mehr, stehen einmal im Klassifikationsbericht und auf der
  Methodenseite (meta.json `global_caveats`). confidence (Längenanteil) hoch/mittel/niedrig 7,0/86,7/6,3 % →
  19,7/73,3/6,9 %; „mittel“ kommt jetzt fast nur aus `fallback:conn_score` (DTV fehlt außerhalb der HVS, Gewicht umgelegt).
- F22: `requirements.GOW50.cycling` = `separated_track_or_parallel_route` (Benutzungspflicht ist eine Anordnung, nicht
  Gegenstand des Plans); D-DES-01 `requirement` gleich umbenannt, Logik unverändert.
- F23 (Q4 a): neues Merkmal S-FEAT-12 `anbaufrei` (Längenanteil ohne ALKIS-Gebäude und Einmündung im Puffer 30 m
  ≥ 0,8; Spalten `anbaufrei_share`, `anbaufrei`). Flag `gow50_anbaufrei` (s08) im Steckbrief (`hints`) und in D-SPD-01
  (`anbaufrei_hint`: Ist ≥ 60 km/h → Stärke 0 und Hinweis statt Tempo-Stärke). Keine neue Kategorie.
- F25 (Q2 b): C-MISS-01 `crossing_demand` mit `status: inactive` (Schema `MissingDefault.status`): Wert immer
  not_assessed, senkt confidence nicht, zählt im Bericht als stillgelegt. `place_score` Notiz „derzeit von keiner Regel
  gelesen“. Goldener Fall 15 heißt jetzt 15_crossing_demand_high_inactive und erwartet GOW50 (Eingabe high greift nicht).
- Ergebnis (Lauf features → discrepancy): Kaskade GOW50 272,3 → 342,5 km, GOW30 474,1 → 408,5 km, ETW30 3 333,4 →
  3 328,8 km; HVS-km als GOW30 61,0 % → 51,2 %. Nach Harmonisierung und Korrekturen (cat_final) GOW50 223,2 → 242,4 km,
  GOW30 527,6 → 513,5 km, ETW30 3 329,4 → 3 324,3 km, HVS-km als GOW30 67,6 % → 64,6 % (Lückenschluss 500 m).
  1 346 Abschnitte (150,7 km) ändern die Kaskaden-Kategorie, 1 075 (133,5 km) cat_final. 25 anbaufreie GOW50
  (17,9 km), davon 13 mit Hinweis statt Tempo-Stärke.

## design_rules.yaml 0.8.0, rules.yaml 0.19.0, plain_language.yaml 0.6.0 – 2026-11-08: Review 2026-11, Paket P2 (Knotenpunkte)
- F02: JC-01 (Rad-Vorrang) nur noch am einstreifigen Kreisverkehr. Neu JC-06 (assumption, A3): Turbokreisverkehr mit
  abgesetztem Radweg, Radverkehr wartepflichtig; Flag `turbo_grade_sep_check` (Schlüssel `flag`/`flag_cycle_cats`),
  wenn ein Arm RSV/HAUPT trägt. Datentest V-INV-07. Goldener Fall j18 (G06), j02 erwartet JC-06 statt JC-01.
- F03: J-14 `GOW50+ETW30` mit `cycle_crossing: [RSV, HAUPT, BASIS]`: quert eine Radroute den Zug (mindestens zwei Arme
  außerhalb des Zugs in der Radkategorie, nach Armrichtung auf beiden Seiten), dann `cycle_crossing_signal`, wenn
  `lanes_per_direction_max >= 2 or entering_dtv_sum > crossing_signal_min_dtv`, sonst `continuous_footway_exit`; sonst
  J-04. Neue Schwelle `crossing_signal_min_dtv` 12 000 Kfz/24h (assumption, A8). Neuer Eingang
  `lanes_per_direction_max` = höchste Soll-Fahrstreifenzahl je Richtung der Straßenarme aus c06 (`lanes_per_dir_soll`,
  `shared` = 1); c07 las cross_section_soll schon, die Stufenfolge c06 → c07 bleibt. Goldener Fall j17 (G05).
- F08: J-10 nur noch `cycle_path(RSV|HAUPT)+SW` → planfrei; neu J-10b `SW+GOW50|GOW30` (same_as J-01), J-10c
  `SW+ETW30|ETW_ERF` → LSA, J-10d `SW+SW|cycle_path(BASIS|ERSCHL)` → neuer Typ `not_applicable` (der Review schreibt
  `SW+SW|cycle_path(BASIS|ERSCHL)+SW`, gleichbedeutend). `legs` erlaubt dafür Alternativen je Seite. evaluation_order
  beginnt mit J-10, J-10d, J-10c, J-10b. Goldene Fälle j19/j20 (G07), j22, j23; j13 (vorher GOW50-Hauptroute × SW)
  ist jetzt ein eigenständiger HAUPT-Radweg × SW, weil J-10 nur noch eigenständige Radwege erfasst.
- F09: N6 ohne `node_types`, `ist_check`, `thresholds.signal_radius_m`; neu `source_of_truth:
  design_rules.junctions.decision_table`, `category_rank` bleibt. `signal_radius_m` (30 m) jetzt in J-M-06. s06 rechnet
  N6 nicht mehr (keine Flags `N6_node_mismatch` auf Abschnitten, damit auch nicht mehr auf der Webseite); der N6-Teil
  (Knotenpunkte ohne Soll-Typ, N5-Übergänge je Knotenpunkt) steht nach c07 in reports/junctions.md (strukturelle
  Empfehlung 8). Der frühere Abgleich N6 ↔ c07 im Knotenbericht entfällt.
- F10: J-15 `cycle_path(BASIS|ERSCHL)+GOW50` → LSA bzw. neuer Typ `cycle_crossing_refuge` (Rad wartepflichtig,
  Mittelinsel nach JC-04); J-16 `cycle_path(ERSCHL)+ETW30` → rechts vor links. ist_check für beide neuen Typen.
  Datentest V-INV-02 (kein `no_rule`). Goldene Fälle j21 (G08), j24.
- F24: JC-04 `median_width_m.RSV` 4,00 m (assumption); `turbo_min_radius` 30 m (assumption, am Original prüfen) in
  J-01 else_if und als `fallback_if.condition_by_type` (Turbokreisel aus J-03 erhalten unter 30 m den Fallback).
- Webseite: Typtexte für `cycle_crossing_refuge` und `not_applicable` (Kartensymbol „kein Soll-Typ“), Flag-Text
  `turbo_grade_sep_check`, Methodenseite Knotenpunkte angepasst.
- Ergebnis (Lauf coherence, discrepancy, validate, junctions, c08): Knotenpunkte 16 259; `no_rule` 11 → 0; planfrei
  277 → 1; LSA (signal_protected + cycle_crossing_signal) 708 → 892 (840 + 52); Turbokreisel 136 → 59; einstreifige
  Kreisverkehre 258 → 283; `not_applicable` 157; Gehwegüberfahrt 3 039 → 2 987; eingefärbte Vorfahrt 300 → 339;
  Handlungsbedarf 2 605 → 2 358; JC-01 394 → 283, JC-06 59 (davon 35 mit `turbo_grade_sep_check`).

## cycling_rules.yaml 0.9.0, design_rules.yaml 0.9.0, plain_language.yaml 0.7.0 – 2026-11-08: Review 2026-11, Paket P3 (Soll-Querschnitt und Radanlage)
- F01: Neue Zelle `separation_matrix.GOW30.high_volume` mit Regel S-05 (CROW_GOW30_2023, swov_crow): bei
  `dtv_official > rules.yaml requirements.GOW30.profiles.wide.max_dtv` (10 000 Kfz/Tag, Grenze einschließlich) vor der
  Radkategorie `separated_oneway_both`, kein Fallback auf Radfahrstreifen, Flag `gow30_high_volume`. Gilt in c05 und
  für die Soll-Führung von P-SAF-01 (c04, DTV der Straße bzw. der Straße des begleitenden Radwegs). Schema prüft die
  Zelle (`all`, `fallback: null`, `flag`, `dtv_above` als Pfad in rules.yaml). design_rules: neue Regel L-07 (GOW30,
  Flag `capacity_reduction_needed`, Spalte `capacity_reduction_dtv` = DTV − L-02-Grenze 13 909 Kfz/Tag); PRF-04: GOW30
  mit Radweg (auch S-05) Fahrbahn `requirements.GOW30.profiles.track.carriageway_min_m`, Radwege nach PL-01.
  Datentests V-INV-04 (c05 und c06). Goldene Fälle s15/s16 (G01: 10 000 → cycle_lane, 10 001 → separated_oneway_both
  + Flag).
- F04: PRF-04 GOW30 mit Radfahrstreifen = max(untere Profilgrenze, Kernfahrbahn + 2 × Radfahrstreifen); Kernfahrbahn
  schmal `centre_runner_max_m` (3,80 m), breit obere Grenze von `avoid_runner_m` (4,80 m), beide aus rules.yaml;
  `lane_width_m.GOW30_*_profile.includes_cycle_lanes: true` (A2). Beispiele BASIS 8,30 m, HAUPT-Fallback 9,80 m.
- F11: PRF-03 `parking_by_category` (GOW50 none, GOW30 [street_side], ETW30 as_ist, ETW_ERF none); c06 schreibt
  `parking_sides_ist` (wie bisher) und neu `parking_sides_soll`. Datentest V-INV-03 (kein Parken/Radfahrstreifen an
  GOW50, keine Mittellinie an GOW30; maßgeblich die D5-Kategorie, wo vorhanden). Goldener Fall s19 (G12) mit neuer
  Golden-API `c06.profile_for_segment` und Prüfung `forbidden_elements`.
- F17 (Q1 b): Abbaureihenfolge `cascade_order: [D1, D3, D2, fallback, D4, D5, D6, D7]`, Liste
  `degrade_cascade_if_not_fit` entsprechend umsortiert. D2 = neuer Baumstreifen auf Baumscheiben im Trenn- oder
  Seitenraum; Flag `trees_in_parking_row` heißt jetzt `trees_as_pits`. `existing_trees_conflict` nur als TODO (keine
  Baumdaten, offene Frage). Unit-Test D3 vor D2 ersetzt den alten Test „D2 vor D3“.
- F18: `widths_m.project_target.cycle_street_carriageway.with_motor_traffic` 4,75 m mit `ref` auf design_rules
  `lane_width_m.ETW30_mixed.value` (Test `cycling_design_ref_mismatches`). C-FAC-04 `cycle_street_motor_traffic: true`
  (assumption, Hamburger Regelfall „Kfz frei“, kein Attribut vorhanden); C-FAC-04 und C-PRI-08 lesen dann
  `with_motor_traffic`. Goldener Fall s08 erwartet `with_motor_traffic` statt `value` (gewollte Änderung).
- F20: `widths_m.de.separated_twoway.oneside_min` 2,50 m (A6, am Original prüfen); C-FAC-04 floor für
  separated_twoway und own_path = `de.separated_twoway.oneside_min`.
- G10: Goldene Fälle s17/s18 (GOW50, Ist 2: DTV 13 900 → 1, 14 000 → 2 je Richtung); L-02 ergibt 13 909 Kfz/Tag.
- V-INV-05 als Datentest, auf realen Daten verletzt (1 069 Abschnitte, 134 km), xfail mit offener Frage.
- Ergebnis (Lauf c04, c05, c06): `gow30_high_volume` 378,0 km von 513,5 km GOW30; Soll-Führung Radfahrstreifen
  249,4 → 71,5 km, Radweg je Seite 506,5 → 684,4 km; fits 2 095,1 → 2 072,6 km, fits_after_degrade 788,1 → 779,7 km,
  does_not_fit 978,0 → 1 008,9 km (GOW30 88,0 → 60,0 km, ETW30 884,7 → 943,6 km wegen Fahrradstraße 4,75 m); D6
  6 191 → 6 328 Abschnitte, D7 549 → 339; D3 218 → 411, D2 2 550 → 1 878, fallback 639 → 244;
  `capacity_reduction_needed` 3 272 Abschnitte (342,9 km), Reduktion im Median 12 091 Kfz/Tag. c07/c08 nicht neu
  gerechnet (Datenträger voll, pyrosm konnte keine Zwischendateien schreiben).
