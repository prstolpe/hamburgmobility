# 13 – Ausweitung auf ganz Hamburg

**Ziel:** die Pipeline aus Prompt 01–12 für alle Bezirke Hamburgs statt nur für den Pilotbezirk laufen lassen.
**Eingaben:** config/project.yaml (Abschnitt `area`), alle Stufen, Ergebnisse des Pilotlaufs als Vergleich.
**Ergebnis:** pipeline/lib/area.py, Berichte je Bezirk, Webseite mit allen Bezirken, rules.yaml 0.13.0.
**Prüfschritt:** Vergleich Eimsbüttel vorher/nachher (reports/validation.md) und Liste der ländlichen Stadtteile
(docs/open_questions.md) fachlich prüfen.

## Auftrag

1. Arbeitsgebiet aus config/project.yaml: Bezirke (OSM admin_level 9 innerhalb der Stadt, admin_level 4), Ausschlüsse
   (Neuwerk mit dem abgetrennten Polygonteil), Puffer. Alle Stufen lesen es über pipeline/lib/area.py.
2. Abruf in Kacheln (area.fetch_tile_m), doppelte Objekte an Kachelgrenzen entfernen; Zählung je Kachel prüfen.
3. Ländliche Stadtteile (area.rural_exclude) nicht klassifizieren, solange `outside_builtup_area` keine Datenquelle hat;
   auf der Karte grau zeigen.
4. Normierung (S-FEAT-01) stadtweit.
5. Berichte: je Bezirk und gesamt; Stichproben nach Bezirk geschichtet; Prioritätenliste Top 30 Hamburg und Top 10
   je Bezirk.
6. Webseite: Bezirksfilter, Tabelle je Bezirk, Bezirksgrenzen, Größe gegen die Grenze von GitHub Pages prüfen.

## Grenzen

- Keine neuen Schwellen. Fehlt für einen Teil der Stadt eine Datengrundlage, wird der Teil ausgeschlossen und in
  docs/open_questions.md eingetragen, nicht geschätzt.
