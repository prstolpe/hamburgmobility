# Barrierefreiheit der Webseite (axe-core)

Erzeugt: 2026-11-16T22:10:38Z mit `npm --prefix web run a11y` (Playwright, axe-core 4.13.0, Regeln WCAG 2.0/2.1/2.2 A und AA) gegen `vite preview` mit den Daten aus data/out. Geräte: Desktop Chrome und Pixel 7 (emuliert).

Ergebnis: **0 kritisch, 0 schwerwiegend, 0 mittel, 0 gering.**

| Gerät | Seite | Verstöße | bestanden | manuell prüfen |
| --- | --- | --- | ---: | ---: |
| desktop | Karte | keine | 31 | 2 |
| desktop | Karte mit Steckbrief | keine | 32 | 2 |
| desktop | Bezirke | keine | 27 | 0 |
| desktop | Bezirk Eimsbüttel | keine | 30 | 0 |
| desktop | Bezirk mit Tabelle | keine | 32 | 0 |
| desktop | Methode | keine | 26 | 0 |
| desktop | Methode Kapitel Radnetz | keine | 29 | 0 |
| desktop | Methode Regeln | keine | 27 | 0 |
| desktop | Karte Radnetz | keine | 31 | 2 |
| desktop | Karte Fahrstreifen | keine | 31 | 2 |
| desktop | Karte Abweichung | keine | 31 | 2 |
| desktop | Karte Kreuzungen mit Steckbrief | keine | 31 | 2 |
| desktop | Besondere Orte | keine | 27 | 0 |
| desktop | Karte besonderer Ort mit Steckbrief | keine | 33 | 2 |
| desktop | Daten | keine | 29 | 0 |
| desktop | Impressum | keine | 26 | 0 |
| mobile | Karte | keine | 31 | 2 |
| mobile | Karte mit Steckbrief | keine | 31 | 2 |
| mobile | Bezirke | keine | 27 | 0 |
| mobile | Bezirk Eimsbüttel | keine | 30 | 0 |
| mobile | Bezirk mit Tabelle | keine | 33 | 1 |
| mobile | Methode | keine | 26 | 0 |
| mobile | Methode Kapitel Radnetz | keine | 29 | 0 |
| mobile | Methode Regeln | keine | 27 | 0 |
| mobile | Karte Radnetz | keine | 31 | 2 |
| mobile | Karte Fahrstreifen | keine | 31 | 2 |
| mobile | Karte Abweichung | keine | 31 | 2 |
| mobile | Karte Kreuzungen mit Steckbrief | keine | 31 | 2 |
| mobile | Besondere Orte | keine | 27 | 0 |
| mobile | Karte besonderer Ort mit Steckbrief | keine | 32 | 2 |
| mobile | Daten | keine | 30 | 1 |
| mobile | Impressum | keine | 26 | 0 |

## Nicht automatisch prüfbar (offen)

- Bedienung mit Bildschirmleser (VoiceOver, NVDA) und Test auf einem echten Smartphone.
- Karteninhalte sind für Bildschirmleser über die Tabellenansicht und die Suche zugänglich; die Karte selbst ist per Tastatur verschieb- und zoombar.
- Farbkontrast der Kartenlinien: im Unit-Test geprüft (jede Farbe ≥ 3:1 gegen die weiße Kontur, web/test/unit.test.js); Kategorien unterscheiden sich zusätzlich in Breite und Strichmuster.
- HTTP-Range-Anfragen: lokal mit `vite preview` geprüft (206 für beide PMTiles-Dateien); beim Hosting nach dem ersten Deployment mit `web/scripts/check-range.sh <URL>` prüfen.
