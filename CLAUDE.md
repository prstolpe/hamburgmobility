# Hamburger Straßenfunktionsplan – Entwurf (nicht amtlich)

## Ziel
Jedem Straßenabschnitt in Hamburg eine Soll-Kategorie (SW, GOW50, GOW30, ETW30, ETW_ERF;
außerorts GOW80, ETW60) nach Duurzaam Veilig zuordnen, Diskrepanzen zum Ist zeigen und alles
erklärbar, reproduzierbar und fortschreibbar machen.
Automatik schlägt vor, Menschen entscheiden (overrides/overrides.csv).

## Pilotbezirk
Eimsbüttel

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
- Rechnen immer in EPSG:25832; nur die Exportstufe transformiert nach EPSG:4326.
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

## Befehle
make fetch | make network | make conflate | make features | make crosssection | make classify |
make coherence | make discrepancy | make export | make web | make validate | make test
