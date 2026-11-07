# Lizenzen und Quellenvermerke (Entwurf, vor Veröffentlichung juristisch prüfen)

## Eigene Inhalte
- Abschnittsdatensatz (abgeleitet u. a. aus OSM): ODbL 1.0 (Vorschlag, wegen Share-Alike der OSM-Ableitung)
- Radnetz-Entwurf, Radanlagen, Soll-Querschnitte und Knotenpunkte (cycle_segments.*, junctions.*, cycle_network.parquet,
  tiles/cycling.pmtiles, tiles/junctions.pmtiles): ODbL 1.0 (Vorschlag, OSM-Ableitung)
- Code: MIT oder EUPL (vom Team festzulegen)
- Texte und Methodenseite: CC BY 4.0 (Vorschlag)

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
| Weitere (api.hamburg.de u. a.) | je Landing Page prüfen | siehe config/sources.yaml |

Unfalldaten werden nur aggregiert je Abschnitt bzw. je Knotenpunkt veröffentlicht.

Das amtliche Radnetz Hamburg erscheint auf der Webseite unverändert als Vergleichsebene (tiles/cycling.pmtiles, Ebene
cycle_official) mit dem Quellenvermerk „© Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende
(dl-de/by-2.0)“ in Legende, Kartenattribution und Downloads-Seite.
