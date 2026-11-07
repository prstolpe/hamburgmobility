# Barrierefreiheit der Webseite (axe-core)

Erzeugt: 2026-11-07T12:46:50Z mit `npm --prefix web run a11y` (Playwright, axe-core 4.13.0, Regeln WCAG 2.0/2.1/2.2 A und AA) gegen `vite preview` mit den Daten aus data/out. Geräte: Desktop Chrome und Pixel 7 (emuliert).

Ergebnis: **0 kritisch, 0 schwerwiegend, 0 mittel, 0 gering.**

| Gerät | Seite | Verstöße | bestanden | manuell prüfen |
| --- | --- | --- | ---: | ---: |
| desktop | Karte | keine | 29 | 2 |
| desktop | Karte mit Steckbrief | keine | 34 | 2 |
| desktop | Tabelle (Bezirk wählen) | keine | 25 | 0 |
| desktop | Tabelle | keine | 25 | 0 |
| desktop | Methode | keine | 26 | 0 |
| desktop | Radnetz | keine | 26 | 0 |
| desktop | Karte Radanlagen Soll/Ist | keine | 29 | 2 |
| desktop | Karte Knotenpunkte mit Steckbrief | keine | 31 | 2 |
| desktop | Downloads | keine | 24 | 0 |
| desktop | Quellen und Lizenzen | keine | 25 | 0 |
| desktop | Impressum | keine | 23 | 0 |
| mobile | Karte | keine | 29 | 2 |
| mobile | Karte mit Steckbrief | keine | 34 | 2 |
| mobile | Tabelle (Bezirk wählen) | keine | 25 | 0 |
| mobile | Tabelle | keine | 26 | 1 |
| mobile | Methode | keine | 26 | 0 |
| mobile | Radnetz | keine | 27 | 1 |
| mobile | Karte Radanlagen Soll/Ist | keine | 29 | 2 |
| mobile | Karte Knotenpunkte mit Steckbrief | keine | 31 | 2 |
| mobile | Downloads | keine | 24 | 0 |
| mobile | Quellen und Lizenzen | keine | 26 | 1 |
| mobile | Impressum | keine | 23 | 0 |

## Nicht automatisch prüfbar (offen)

- Bedienung mit Bildschirmleser (VoiceOver, NVDA) und Test auf einem echten Smartphone.
- Karteninhalte sind für Bildschirmleser über die Tabellenansicht und die Suche zugänglich; die Karte selbst ist per Tastatur verschieb- und zoombar.
- Farbkontrast der Kartenlinien: im Unit-Test geprüft (jede Farbe ≥ 3:1 gegen die weiße Kontur, web/test/unit.test.js); Kategorien unterscheiden sich zusätzlich in Breite und Strichmuster.
- HTTP-Range-Anfragen: lokal mit `vite preview` geprüft (206 für beide PMTiles-Dateien); beim Hosting nach dem ersten Deployment mit `web/scripts/check-range.sh <URL>` prüfen.
