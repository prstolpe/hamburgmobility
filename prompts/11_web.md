# 11 – Export und Webseite

**Ziel:** statische, barrierearme Karte nach docs/guide.md Teil 5.
**Eingaben:** alle Ergebnisse, docs/guide.md Teil 5, docs/licenses.md.
**Ergebnis:** pipeline/s09_export.py, web/ (Vite), Deployment-Workflow, data/out/ mit Downloads.
**Prüfschritt:** axe-core ohne kritische Fehler, Test auf Smartphone, HTTP-Range-Anfragen beim gewählten Hosting mit der PMTiles-Datei geprüft.

## Auftrag

1. pipeline/s09_export.py: GeoParquet, GeoJSON und CSV für den Download; segments/{id}.json für
   Steckbriefe (Kategorie, Begründung in Klartext aus rule_trace, Ist, Querschnitt, Diskrepanz,
   Unsicherheit, Quellen mit Stand und Lizenz); search.json (Straßenname, Bezirk, Bounding Box);
   PMTiles via tippecanoe (Zoom 10–16). Transformation nach EPSG:4326 nur hier.
2. web/: Vite + Vanilla JS (oder Svelte), MapLibre GL JS mit pmtiles-Protokoll.
   - Ebenen: Soll-Kategorie, Ist-Tempo, Diskrepanz, Straßenraumbreite, Machbarkeit, HVS-Vergleich,
     Overlays Bus, Radnetz, Schulen/Kitas, Unfälle aggregiert.
   - Steckbrief als Seitenpanel (mobil Bottom Sheet), Filter Bezirk/Kategorie/Diskrepanz,
     Suche mit Autovervollständigung, Filter und Ausschnitt in der URL.
   - Methodenseite in einfacher Sprache, Download-Seite, Lizenz- und Quellenseite aus docs/licenses.md.
   - Rückmeldung: vorausgefüllter GitHub-Issue-Link mit segment_id; mailto als Alternative.
   - Dauerhaftes Band: „Nicht amtlicher Diskussionsentwurf – keine Planung oder Anordnung der
     Freien und Hansestadt Hamburg“ plus Datenstand. Keine Behördenlogos.
   - WCAG 2.2 AA: Kontraste, Tastaturbedienung, Fokus, farbsehschwächen-taugliche Palette mit
     zusätzlichem Linienstil, Tabellenansicht je Bezirk als Alternative zur Karte.
   - Kein Tracking, keine externen Schriften, keine Laufzeitabhängigkeit von Drittservern außer
     dem Hintergrundkartendienst (offen lizenziert, im Impressum genannt).
3. Workflow (z. B. GitHub Actions): Tests -> Export -> Kacheln -> Build -> Deployment.

Führe axe-core aus und berichte die Ergebnisse in reports/web_accessibility.md.
