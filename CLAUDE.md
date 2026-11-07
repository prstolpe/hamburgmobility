# Hamburger Straßenfunktionsplan – Entwurf (nicht amtlich)

## Ziel
Jedem Straßenabschnitt in Hamburg eine Soll-Kategorie (SW, GOW50, GOW30, ETW30, ETW_ERF;
außerorts GOW80, ETW60) nach Duurzaam Veilig zuordnen, Diskrepanzen zum Ist zeigen und alles
erklärbar, reproduzierbar und fortschreibbar machen.
Automatik schlägt vor, Menschen entscheiden (overrides/overrides.csv).

## Gebiet
Ganz Hamburg: alle sieben Bezirke ohne Neuwerk/Scharhörn; 17 ländliche Stadtteile werden nicht klassifiziert
(config/project.yaml, Abschnitt `area`). Pilotbezirk war Eimsbüttel (bis rules.yaml 0.12.0).

## Wo was steht
- docs/guide.md – vollständige fachliche Anleitung. Bei Fachfragen zuerst hier nachsehen.
- config/rules.yaml – das einzige Regelwerk. Keine Schwellenwerte im Code.
- config/sources.yaml – Datenquellen. Nur Endpunkte verwenden, die dort stehen.
- overrides/overrides.csv – fachliche Korrekturen; nur review_status = approved wird übernommen.
- prompts/ – Arbeitsaufträge je Phase, in nummerierter Reihenfolge.
- docs/open_questions.md – offene Fragen; hier eintragen statt zu raten.

## Fachliche Regeln
- Jede neue Regel braucht: id, source, source_type (swov_crow|de_regelwerk|hamburg|assumption), status.
- Erfinde keine Schwellenwerte, Endpunkte, Datensätze oder Attributnamen. Unbekanntes als TODO
  markieren, in docs/open_questions.md eintragen und nachfragen.
- Ändere nie Schwellen, um Tests grün zu bekommen. Regeländerungen nur mit Begründung und neuer
  Version in rules.yaml (meta.version) und Eintrag in CHANGELOG.md.

## Konventionen
- Python 3.12, uv, geopandas/shapely 2, pyogrio, DuckDB Spatial; Code, Namen und Konfiguration auf
  Englisch, Dokumentation und Reports auf Deutsch.
- Rechnen immer in EPSG:25832; nur die Exportstufe transformiert nach EPSG:4326. Ausnahme: Prüfdateien in reports/
  (GeoJSON zur Sichtprüfung) dürfen nach GeoJSON-Standard in EPSG:4326 vorliegen.
- Zwischenergebnisse als GeoParquet in data/interim, Rohdaten in data/raw mit Quelle, Abrufdatum
  und Hash in data/manifest.json.
- segment_id ist stabil (Hash aus sortierten OSM-Way-IDs und gerundeten Knotenkoordinaten).
  Nie neu nummerieren.
- Jede Klassifikation schreibt rule_trace (Regel-ID, Ergebnis, Eingangswerte).
- Pipeline-Skripte: pipeline/sNN_name.py; gemeinsame Funktionen in pipeline/lib/.

## Qualitätsregeln
- Erst Tests (tests/, tests/golden/), dann Code. `make test` muss vor jedem Commit grün sein.
- Keine Daten in Git außer kleinen Testfixtures und data/manifest.json.
- Nach jeder Stufe ein kurzer Report in reports/ mit Kennzahlen und 30 Zufallsstichproben
  (mit Links auf Orthophoto bzw. Panoramax/OSM zur manuellen Prüfung).
- Lizenzen beachten: dl-de/by-2.0-Quellenvermerke, ODbL für OSM-Ableitungen (docs/licenses.md).
- Unfalldaten nur aggregiert je Abschnitt speichern und darstellen.
- Bei Netzwerkfehlern oder nicht erreichbaren Endpunkten: abbrechen und berichten, keine
  Ersatzquellen erfinden.

## Radnetz und Soll-Querschnitt
- Erweiterung ab Prompt 14 (prompts/14_cycling_setup.md bis 21_web_validation_cycling.md):
  hierarchisches Radnetz nach den fünf Prinzipien, Führungsform/Breite, Soll-Querschnitt, Knotenpunkte.
- Folgeaufträge (noch offen): prompts/22_target_scenario.md (Zielszenario statt heutiger Mengen),
  prompts/23_junction_performance.md (Wartezeiten an Knotenpunkten Ist/Soll).
- docs/guide_radnetz.md – Methodik mit Quellen. Bei Fachfragen zum Radnetz zuerst hier nachsehen.
- config/cycling_rules.yaml – Radnetzkategorien, Prinzipien, Trennungsmatrix, Breiten.
- config/design_rules.yaml – Fahrstreifen, Lage der Radanlagen, Raumaufteilung, Knotenpunkte.
- Schemas: config/schema/cycling_model.py, design_model.py; Loader in pipeline/lib/rules.py.
  source/source_type gelten auch für Einträge darunter; jede Regel mit id braucht status.
- Auch hier gilt: keine Schwellen im Code; Regeländerungen mit neuer meta.version und CHANGELOG-Eintrag.
- Korrekturebenen (nur review_status = approved wird übernommen):
  overrides/cycle_network_overrides.csv (edge_id), overrides/junction_overrides.csv (node_id),
  overrides/lane_overrides.csv (segment_id, Fahrstreifen und Busfahrstreifen).
- Pipeline-Skripte: pipeline/cNN_name.py; goldene Fälle in tests/golden/cycling/.
- Make-Ziele: make cycle-demand | make cycle-network | make cycle-principles | make cycle-facility |
  make cross-section-soll | make junctions | make export-cycling

## Befehle
make fetch | make network | make conflate | make features | make crosssection | make classify |
make coherence | make discrepancy | make export | make web | make validate | make test
make rerun FROM=<Stufe> – Neurechnung ab einer Straßenstufe bis zum Export (validate parallel zur Radnetzkette).
Rechenkerne: SFP_WORKERS (Standard alle, 1 = seriell); Cache für den Bus-Abgleich in data/interim/cache.
