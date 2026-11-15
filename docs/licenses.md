# Lizenzen und Quellenvermerke

## Eigene Inhalte
Rechteinhaber: Raphael Stolpe (hamburgmobility.de). Festgelegt am 2026-11-15.

| Was | Lizenz | Warum |
| --- | --- | --- |
| Code und Regelwerke: `pipeline/`, `web/` (ohne Schriften), `analysis/`, `prototypes/`, `tests/`, `config/` (ohne `plain_language.yaml`), `Makefile` | EUPL-1.2 (Datei `LICENSE`) | Freie Lizenz der EU mit amtlicher deutscher Fassung. Änderungen müssen offen bleiben, auch wenn jemand den Code nur als Webdienst betreibt. Verträglich mit GPL, LGPL, MPL und anderen. |
| Datensätze: Abschnitte, Radnetz-Entwurf, Radanlagen, Soll-Querschnitte, Knotenpunkte (Downloads, `tiles/*.pmtiles`, Steckbriefe) und `overrides/` | ODbL 1.0 | Abgeleitet aus OpenStreetMap; die ODbL verlangt für Ableitungen dieselbe Lizenz. |
| Texte: Webseite (`config/plain_language.yaml`), Methodenseite, `docs/`, `reports/`, `prompts/` | CC BY 4.0 | Freie Nutzung mit Namensnennung. |

Namensnennung für Texte und Daten: „Hamburger Straßenfunktionsplan – nicht amtlicher Entwurf, Raphael Stolpe,
hamburgmobility.de“. Bei den Daten zusätzlich „© OpenStreetMap-Beitragende“ und die Vermerke der Fremddaten unten.

Lizenztexte: EUPL-1.2 in `LICENSE` (alle Sprachfassungen: https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12),
ODbL 1.0: https://opendatacommons.org/licenses/odbl/1-0/, CC BY 4.0: https://creativecommons.org/licenses/by/4.0/deed.de.

## Fremddaten
| Quelle | Lizenz | Quellenvermerk |
| --- | --- | --- |
| OpenStreetMap | ODbL 1.0 | © OpenStreetMap-Beitragende |
| HH-SIB / Strategisches Straßennetz | dl-de/by-2.0 | Freie und Hansestadt Hamburg, Behörde für Wirtschaft, Verkehr und Innovation |
| ALKIS, LoD2, DOP | dl-de/by-2.0 | Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV) |
| HVV-GTFS | dl-de/by-2.0 | Hamburger Verkehrsverbund GmbH |
| Unfallatlas | dl-de/by-2.0 | Statistische Ämter des Bundes und der Länder |
| Zensus 2022, 100-m-Gitter | dl-de/by-2.0 | © Statistische Ämter des Bundes und der Länder, Zensus 2022 |
| Radnetz Hamburg (WFS) | dl-de/by-2.0 | Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende |
| Rad-Zählstellen (Infrarotdetektoren, SensorThings) | dl-de/by-2.0 | Freie und Hansestadt Hamburg |
| Zulässige Höchstgeschwindigkeiten, Verkehrsmengen HVS 2019 (api.hamburg.de) | dl-de/by-2.0 (laut Transparenzportal; die API nennt keine Lizenz) | Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (BVM) |
| Weitere (api.hamburg.de u. a.) | je Landing Page prüfen | siehe config/sources.yaml |

## Schrift der Webseite
Inter 4.1 (variabel, auf lateinische Zeichen reduziert), © 2016 The Inter Project Authors, SIL Open Font License 1.1.
Selbst gehostet mit der Lizenzdatei (`web/src/fonts/OFL-Inter.txt`), keine Anfrage an einen Schriftdienst. Quelle:
https://github.com/rsms/inter/releases/tag/v4.1. Die Kartenbeschriftung nutzt weiter Noto Sans (SIL OFL 1.1, siehe
Hintergrundkarte).

Unfalldaten werden nur aggregiert je Abschnitt bzw. je Knotenpunkt veröffentlicht.

Das amtliche Radnetz Hamburg erscheint auf der Webseite unverändert als Vergleichsebene (tiles/cycling.pmtiles, Ebene
cycle_official) mit dem Quellenvermerk „© Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende
(dl-de/by-2.0)“ in Legende, Kartenattribution und Downloads-Seite.
