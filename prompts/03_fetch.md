# 03 – Datenbeschaffung

**Ziel:** reproduzierbarer Download aller Quellen aus config/sources.yaml für den Pilotbezirk.
**Eingaben:** config/sources.yaml, CLAUDE.md (Pilotbezirk), docs/guide.md Teil 2 und Anhang B.
**Ergebnis:** pipeline/s01_fetch.py, data/raw/*.parquet, data/manifest.json, reports/data_report.md.
**Prüfschritt:** Report zeigt je Quelle Objektanzahl, CRS, Bounding Box, Lizenz, Abrufdatum; Zuschnitt auf den Bezirk stimmt.

## Auftrag

Implementiere pipeline/s01_fetch.py. Nutze ausschließlich URLs aus config/sources.yaml.
Für Einträge mit `url: null` versuche nicht, Endpunkte zu erraten: liste sie im Report als
„fehlt“, schlage vor, wie die URL zu finden ist, und ergänze docs/open_questions.md.
Bei Quellen mit Fallback (z. B. OSM für Schulen/Kitas) nutze den Fallback und kennzeichne das.

Technik:
- WFS: GetCapabilities lesen, Feature-Typen auflisten, Paging mit count/startIndex,
  Gesamtanzahl mit resultType=hits prüfen.
- OGC API Features: /collections abfragen, alle Collections auflisten, Paging über next-Links;
  für verkehrsmengen den aktuellsten Jahrgang Hauptverkehrsstraßen ermitteln und berichten.
- Downloads: SHA-256-Hash und Abrufdatum in data/manifest.json.
- Bezirksgrenze aus ALKIS-Verwaltungseinheiten oder OSM (admin_level prüfen) und Zuschnitt
  mit 500 m Puffer, damit Randabschnitte vollständig sind.
- Alles nach EPSG:25832, Speicherung als GeoParquet in data/raw/.

Teste das Paging mit einem gemockten WFS und einer gemockten OGC API.
Wenn ein Endpunkt nicht antwortet: abbrechen, Fehler berichten, keine Ersatzquelle erfinden.
Schreibe reports/data_report.md und aktualisiere check_status in sources.yaml nur mit Begründung.
