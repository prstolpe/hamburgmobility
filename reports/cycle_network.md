# Soll-Radnetz: Hierarchie und Lückenschluss (Stufe c03)

Erzeugt 2026-11-07T15:12:26+00:00 mit pipeline/c03_cycle_network.py · cycling_rules.yaml 0.7.0 · nicht amtlicher Entwurf. Alle Entwurfsparameter (C-NET-01…13) sind Annahmen (source_type assumption, status draft) und vor fachlicher Nutzung zu prüfen.

## Kurzfassung

- RSV: 66 km (805 Kanten)
- HAUPT: 1 873 km (18 661 Kanten)
- BASIS: 1 021 km (9 784 Kanten)
- ERSCHL: 3 471 km (36 723 Kanten)
- Amtliches Radnetz (Bestand, 371 km): 58% liegt am Soll-Netz RSV/HAUPT, 73% am Soll-Netz bis BASIS (Puffer 20 m).
- Soll RSV/HAUPT außerhalb des amtlichen Bestands: 1 694 km, davon 168 km im geplanten amtlichen Netz.
- Maschen über der Höchstweite nach Verdichtung: HAUPT 34, BASIS 409 (Lückenliste unten; Maschen in ländlichen Stadtteilen nicht geprüft).
- Parallelregel P-ATT-03: 4 von 435 geprüften Läufen an Straßen mit DTV > 15 000 auf eine Parallelroute verlegt.
- Overrides angewendet: 0.

**Grenzen vorab:** Bezirks- und Stadtteilzentren fehlen als Korridorpunkte (kein Endpunkt für das Zentrenkonzept, Entscheidung 2026-11-06). Die Nachfrage aus Prompt 15 ist nur mäßig kalibriert (Spearman 0,53, mittlere relative Abweichung 154 %; Nebenstraßen parallel zu Hauptstraßen ohne erfassten Radweg werden überschätzt). Beides wirkt auf Korridore und RSV-Abschnitte; bitte die RSV-Liste und die Karten mit Ortskenntnis lesen.

## Verfahren

1. **Soll-Widerstand (C-NET-03):** Länge × Faktor der regelkonformen Führung je cat_final (path separated_track_or_cycle_street, SW gow50_separated_track, GOW80 gow50_separated_track, GOW50 gow50_separated_track, GOW30 gow30_cycle_lane, ETW30 etw30_mixed, ETW_ERF etw30_mixed, ETW60 etw30_mixed) plus Wartezeiten des Ist-Zustands; ungerichtet.
2. **Boni:** Nachfrage (C-NET-04) bis −30% ab 2 000 Rad/Werktag; amtliches Radnetz (C-NET-05, alle Status) × 0.8 bei ≥ 50% Überdeckung im Puffer 15 m.
3. **Korridore (C-NET-01/02):** Punkte zusammengefasst ab 500 m; jeder Punkt mit seinen 4 nächsten (bis 15 km) und mit der Innenstadt verbunden, günstigster Weg nach Soll-Widerstand mit Boni.
4. **RSV (C-NET-06):** Korridorläufe mit ≥ 2 000 Rad/Werktag (Lücken bis 500 m überbrückt) und ≥ 5 km Länge; übrige Korridorkanten HAUPT.
5. **HAUPT-Verdichtung (C-NET-07/08):** Maschen des RSV+HAUPT-Netzes mit Barrieren (Bahn, Flüsse/Kanäle) und Landesgrenze; Seite des flächengleichen Quadrats ohne Wasser, Wald, Parks, Friedhöfe, Flughafen (≥ 5 ha); Maschen > 600 m × √(4 400 Einwohner/km² / Einwohnerdichte der Masche), nie darunter; Maschen ohne Einwohner nicht (C-NET-07 density_scaling) werden geteilt, ab der Kante mit der höchsten Nachfrage im Kernbereich (Abstand zum Maschenrand ≥ 0.5 × größter Abstand).
6. **Parallelregel (C-NET-10, P-ATT-03):** Läufe ≥ 300 m an Straßen mit DTV > 15 000; Alternative über Kanten im Puffer 200 m, höchstens 60 m an der Hauptstraße (Anschluss/Querung), Umwegfaktor ≤ P-DIR-01 (RSV 1.1, HAUPT 1.2); die Hauptstraße bleibt BASIS. Danach zweite HAUPT-Verdichtung ohne diese Hauptstraßen.
7. **BASIS (C-NET-09/08):** Schulen und Nahversorgung (supermarket, convenience, bakery, butcher, greengrocer, chemist) weiter als 150 m vom Netz angebunden; dann Maschen > 300 m × √(4 400 Einwohner/km² / Einwohnerdichte der Masche), nie darunter; Maschen ohne Einwohner nicht (C-NET-07 density_scaling) geteilt.
8. **Kontinuität (C-NET-11):** niedrigere Läufe bis 200 m zwischen zwei gleichen höheren Läufen angehoben.
9. **ERSCHL (C-NET-12):** alle übrigen Kanten. **Overrides:** overrides/cycle_network_overrides.csv, nur approved.

## Korridorpunkte (C-NET-01)

| Art | Punkte | nach Zusammenfassung | Quelle |
| --- | ---: | ---: | --- |
| Innenstadt | 1 | 1 | Annahme (Rathausmarkt, 53.5503/9.9925) |
| Schnellbahn-Umsteigeknoten | 127 | 16 | HVV-GTFS, ≥ 2 Verkehrsmittel im Umkreis 250 m |
| Hochschule | 41 | 20 | OSM amenity=university (Fallback) |
| Arbeitsplatzschwerpunkt | 51 | 23 | ALKIS-Geschossfläche Nichtwohnen, Zonen ≥ Quantil 0.98 (224 Tsd. m²) |
| Bezirks-/Stadtteilzentren | – | – | fehlt: sources.yaml `centres` ohne Endpunkt (TODO) |

Korridorpaare: 209, davon mit Weg: 209. Anbindung an den Radgraphen: Median 61 m, Maximum 362 m.

## Kennzahlen je Kategorie

| Kategorie | km | Kanten | davon Bestand amtlich km | Komponenten | größte Komponente (Längenanteil) |
| --- | ---: | ---: | ---: | ---: | ---: |
| RSV | 66.0 | 805 | 29.8 | 6 | 20% |
| HAUPT | 1 872.7 | 18 661 | 189.8 | 1 | 100% |
| BASIS | 1 020.9 | 9 784 | 74.0 | 1 | 100% |
| ERSCHL | 3 470.9 | 36 723 | 251.7 | – | – |

Komponenten (P-COH-02): je Ebene einschließlich der höheren Ebenen.

Anteile je Bezirk (Kantenlänge):

| Bezirk | Abschnitte | km | RSV | HAUPT | BASIS | ERSCHL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 8 424 | 787.5 | 1 % | 37 % | 15 % | 47 % |
| Bergedorf | 5 014 | 631.5 | 0 % | 15 % | 16 % | 69 % |
| Eimsbüttel | 8 086 | 629.2 | 1 % | 37 % | 19 % | 43 % |
| Hamburg-Mitte | 12 403 | 1 102.3 | 3 % | 26 % | 16 % | 56 % |
| Hamburg-Nord | 10 442 | 805.6 | 2 % | 31 % | 19 % | 49 % |
| Harburg | 5 650 | 701.3 | 1 % | 25 % | 12 % | 62 % |
| Wandsbek | 14 241 | 1 476.3 | 0 % | 38 % | 18 % | 44 % |
| ohne Bezirk | 1 713 | 296.7 | 0 % | 0 % | 0 % | 100 % |
| **gesamt** | 65 973 | 6 430.4 | 1 % | 29 % | 16 % | 54 % |

### Maschenweite (P-COH-01)

| Ebene | Höchstweite m | Maschen geprüft | Median Seite m | 90-%-Quantil m | größte m | über Höchstweite | über mesh_m.max | in ländl. Stadtteilen nicht geprüft |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| HAUPT + höher | 600 | 3 594 | 157 | 540 | 4 073 | 34 | 168 | 7 |
| BASIS + höher | 300 | 6 443 | 161 | 331 | 4 064 | 409 | 847 | 13 |

Verdichtungsrunden:

| Ebene | Runde | Maschen zu groß | neue Routen |
| --- | ---: | ---: | ---: |
| HAUPT 1 | 1 | 74 | 71 |
| HAUPT 1 | 2 | 86 | 83 |
| HAUPT 1 | 3 | 82 | 79 |
| HAUPT 1 | 4 | 78 | 75 |
| HAUPT 1 | 5 | 76 | 73 |
| HAUPT 1 | 6 | 70 | 67 |
| HAUPT 1 | 7 | 63 | 60 |
| HAUPT 1 | 8 | 61 | 58 |
| HAUPT 1 | 9 | 56 | 52 |
| HAUPT 1 | 10 | 61 | 57 |
| HAUPT 1 | 11 | 60 | 56 |
| HAUPT 1 | 12 | 59 | 54 |
| HAUPT 1 | 13 | 53 | 48 |
| HAUPT 1 | 14 | 46 | 41 |
| HAUPT 1 | 15 | 49 | 44 |
| HAUPT 1 | 16 | 44 | 39 |
| HAUPT 1 | 17 | 45 | 39 |
| HAUPT 1 | 18 | 40 | 33 |
| HAUPT 1 | 19 | 41 | 33 |
| HAUPT 1 | 20 | 40 | 32 |
| HAUPT 1 | 21 | 40 | 31 |
| HAUPT 1 | 22 | 39 | 30 |
| HAUPT 1 | 23 | 38 | 29 |
| HAUPT 1 | 24 | 35 | 26 |
| HAUPT 1 | 25 | 36 | 27 |
| HAUPT 1 | 26 | 35 | 26 |
| HAUPT 1 | 27 | 36 | 27 |
| HAUPT 1 | 28 | 33 | 23 |
| HAUPT 1 | 29 | 33 | 20 |
| HAUPT 1 | 30 | 34 | 21 |
| HAUPT 1 | 31 | 36 | 23 |
| HAUPT 1 | 32 | 35 | 22 |
| HAUPT 1 | 33 | 33 | 19 |
| HAUPT 1 | 34 | 32 | 18 |
| HAUPT 1 | 35 | 34 | 20 |
| HAUPT 1 | 36 | 34 | 20 |
| HAUPT 1 | 37 | 34 | 19 |
| HAUPT 1 | 38 | 32 | 17 |
| HAUPT 1 | 39 | 32 | 17 |
| HAUPT 1 | 40 | 31 | 15 |
| HAUPT 2 | 1 | 33 | 17 |
| HAUPT 2 | 2 | 33 | 17 |
| HAUPT 2 | 3 | 33 | 16 |
| HAUPT 2 | 4 | 33 | 13 |
| HAUPT 2 | 5 | 33 | 13 |
| HAUPT 2 | 6 | 32 | 12 |
| HAUPT 2 | 7 | 32 | 11 |
| HAUPT 2 | 8 | 32 | 11 |
| HAUPT 2 | 9 | 32 | 11 |
| HAUPT 2 | 10 | 32 | 11 |
| HAUPT 2 | 11 | 32 | 11 |
| HAUPT 2 | 12 | 33 | 11 |
| HAUPT 2 | 13 | 32 | 10 |
| HAUPT 2 | 14 | 32 | 10 |
| HAUPT 2 | 15 | 32 | 10 |
| HAUPT 2 | 16 | 32 | 9 |
| HAUPT 2 | 17 | 33 | 10 |
| HAUPT 2 | 18 | 33 | 10 |
| HAUPT 2 | 19 | 33 | 10 |
| HAUPT 2 | 20 | 34 | 10 |
| HAUPT 2 | 21 | 33 | 9 |
| HAUPT 2 | 22 | 33 | 8 |
| HAUPT 2 | 23 | 33 | 8 |
| HAUPT 2 | 24 | 33 | 8 |
| HAUPT 2 | 25 | 33 | 8 |
| HAUPT 2 | 26 | 33 | 8 |
| HAUPT 2 | 27 | 33 | 8 |
| HAUPT 2 | 28 | 33 | 8 |
| HAUPT 2 | 29 | 33 | 8 |
| HAUPT 2 | 30 | 33 | 8 |
| HAUPT 2 | 31 | 33 | 8 |
| HAUPT 2 | 32 | 33 | 8 |
| HAUPT 2 | 33 | 33 | 6 |
| HAUPT 2 | 34 | 34 | 7 |
| HAUPT 2 | 35 | 34 | 7 |
| HAUPT 2 | 36 | 34 | 7 |
| HAUPT 2 | 37 | 34 | 7 |
| HAUPT 2 | 38 | 34 | 6 |
| HAUPT 2 | 39 | 34 | 6 |
| HAUPT 2 | 40 | 34 | 5 |
| BASIS | 1 | 871 | 794 |
| BASIS | 2 | 772 | 642 |
| BASIS | 3 | 647 | 455 |
| BASIS | 4 | 541 | 275 |
| BASIS | 5 | 484 | 173 |
| BASIS | 6 | 445 | 104 |
| BASIS | 7 | 424 | 62 |
| BASIS | 8 | 413 | 39 |
| BASIS | 9 | 413 | 30 |
| BASIS | 10 | 410 | 21 |
| BASIS | 11 | 410 | 18 |
| BASIS | 12 | 410 | 16 |
| BASIS | 13 | 410 | 12 |
| BASIS | 14 | 410 | 10 |
| BASIS | 15 | 411 | 9 |
| BASIS | 16 | 412 | 9 |
| BASIS | 17 | 410 | 6 |
| BASIS | 18 | 410 | 6 |
| BASIS | 19 | 409 | 3 |
| BASIS | 20 | 409 | 3 |
| BASIS | 21 | 409 | 3 |
| BASIS | 22 | 409 | 3 |
| BASIS | 23 | 409 | 3 |
| BASIS | 24 | 409 | 2 |
| BASIS | 25 | 409 | 2 |
| BASIS | 26 | 409 | 1 |
| BASIS | 27 | 409 | 1 |
| BASIS | 28 | 409 | 1 |
| BASIS | 29 | 409 | 0 |

### Abdeckung wichtiger Ziele (P-COH-03, ≤ 300 m vom RSV/HAUPT-Netz)

| Ziel | Anzahl | abgedeckt |
| --- | ---: | ---: |
| Schulen (OSM) | 557 | 96% |
| Schnellbahnhalte | 375 | 99% |
| Hochschulen (OSM university) | 41 | 100% |
| Zentren | – | nicht prüfbar (Datensatz fehlt) |

## Karten

![RSV und HAUPT](cycle_network_haupt.png)

![BASIS](cycle_network_basis.png)

![Soll vs. amtliches Radnetz](cycle_network_compare.png)

## Vergleich mit dem amtlichen Radnetz

Amtlich = WFS Radnetz Hamburg, Status Bestand; geplant = In Arbeit, Priorisierte Netzergänzungen/Netzverbesserungen, Netzbedeutende Abschnitte mit Verbesserungspotential (Entscheidung 2026-11-06). Überdeckung im Puffer 20 m.

| Kennzahl | km |
| --- | ---: |
| amtlich (Bestand) | 371.4 |
| davon am Soll RSV/HAUPT | 216.5 |
| davon am Soll bis BASIS | 272.8 |
| fehlt im Soll RSV/HAUPT | 154.8 |
| geplant (amtlich) | 292.4 |
| davon am Soll RSV/HAUPT | 158.8 |
| Soll RSV/HAUPT gesamt | 1 938.6 |
| Soll RSV/HAUPT zusätzlich (nicht am amtlichen Bestand) | 1 694.2 |
| davon im geplanten amtlichen Netz | 168.4 |

Längste amtliche Bestandsabschnitte ohne Soll RSV/HAUPT (Top 15):

| Länge m | Soll dort (größte Kategorie) | Prüfen |
| ---: | --- | --- |
| 5 103 | BASIS | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577209,5920892]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.431411/10.162119) · [OSM](https://www.openstreetmap.org/?mlat=53.431411&mlon=10.162119#map=18/53.431411/10.162119) |
| 4 454 | HAUPT | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570437,5929974]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.513978/10.062247) · [OSM](https://www.openstreetmap.org/?mlat=53.513978&mlon=10.062247#map=18/53.513978/10.062247) |
| 4 209 | ERSCHL | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580907,5917845]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.403472/10.216980) · [OSM](https://www.openstreetmap.org/?mlat=53.403472&mlon=10.216980#map=18/53.403472/10.216980) |
| 3 614 | BASIS | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[585025,5921139]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.432426/10.279804) · [OSM](https://www.openstreetmap.org/?mlat=53.432426&mlon=10.279804#map=18/53.432426/10.279804) |
| 3 466 | BASIS | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578652,5918928]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.413549/10.183340) · [OSM](https://www.openstreetmap.org/?mlat=53.413549&mlon=10.183340#map=18/53.413549/10.183340) |
| 3 440 | BASIS | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[581378,5924306]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.461462/10.225732) · [OSM](https://www.openstreetmap.org/?mlat=53.461462&mlon=10.225732#map=18/53.461462/10.225732) |
| 3 192 | HAUPT | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575498,5929969]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.513233/10.138550) · [OSM](https://www.openstreetmap.org/?mlat=53.513233&mlon=10.138550#map=18/53.513233/10.138550) |
| 2 431 | BASIS | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555512,5931491]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.529402/9.837457) · [OSM](https://www.openstreetmap.org/?mlat=53.529402&mlon=9.837457#map=18/53.529402/9.837457) |
| 2 199 | BASIS | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[582589,5919714]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.420006/10.242761) · [OSM](https://www.openstreetmap.org/?mlat=53.420006&mlon=10.242761#map=18/53.420006/10.242761) |
| 2 182 | HAUPT | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566259,5927431]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.491666/9.998716) · [OSM](https://www.openstreetmap.org/?mlat=53.491666&mlon=9.998716#map=18/53.491666/9.998716) |
| 2 132 | BASIS | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580584,5921676]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.437953/10.213108) · [OSM](https://www.openstreetmap.org/?mlat=53.437953&mlon=10.213108#map=18/53.437953/10.213108) |
| 2 080 | BASIS | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573363,5950518]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.698207/10.111192) · [OSM](https://www.openstreetmap.org/?mlat=53.698207&mlon=10.111192#map=18/53.698207/10.111192) |
| 2 034 | RSV | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566013,5930578]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.519984/9.995661) · [OSM](https://www.openstreetmap.org/?mlat=53.519984&mlon=9.995661#map=18/53.519984/9.995661) |
| 2 010 | BASIS | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558879,5931435]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.528535/9.888246) · [OSM](https://www.openstreetmap.org/?mlat=53.528535&mlon=9.888246#map=18/53.528535/9.888246) |
| 1 936 | HAUPT | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566969,5924238]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.462885/10.008733) · [OSM](https://www.openstreetmap.org/?mlat=53.462885&mlon=10.008733#map=18/53.462885/10.008733) |

Zusätzliche Soll-RSV/HAUPT-Straßen ohne amtlichen Bestand (Top 15 nach Länge):

| Straße / Weg | km | Kategorie | im geplanten Netz km | Prüfen |
| --- | ---: | --- | ---: | --- |
| neben Bremer Straße | 5.56 | HAUPT | 4.35 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563326,5922159]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.444645/9.953453) · [OSM](https://www.openstreetmap.org/?mlat=53.444645&mlon=9.953453#map=18/53.444645/9.953453) |
| Billwerder Billdeich | 4.49 | HAUPT | 0.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573850,5930988]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.522622/10.113949) · [OSM](https://www.openstreetmap.org/?mlat=53.522622&mlon=10.113949#map=18/53.522622/10.113949) |
| Alsterwanderweg | 4.20 | HAUPT | 0.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568678,5943090]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.632088/10.038614) · [OSM](https://www.openstreetmap.org/?mlat=53.632088&mlon=10.038614#map=18/53.632088/10.038614) |
| neben Waltershofer Straße | 4.15 | HAUPT | 4.15 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559835,5925130]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.471757/9.901457) · [OSM](https://www.openstreetmap.org/?mlat=53.471757&mlon=9.901457#map=18/53.471757/9.901457) |
| Elbchaussee | 4.08 | HAUPT | 3.34 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555693,5934025]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.552159/9.840641) · [OSM](https://www.openstreetmap.org/?mlat=53.552159&mlon=9.840641#map=18/53.552159/9.840641) |
| Cuxhavener Straße | 3.98 | RSV | 0.08 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556267,5925199]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.472774/9.847726) · [OSM](https://www.openstreetmap.org/?mlat=53.472774&mlon=9.847726#map=18/53.472774/9.847726) |
| neben Alte Landstraße | 3.97 | HAUPT | 0.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569783,5944037]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.640453/10.055533) · [OSM](https://www.openstreetmap.org/?mlat=53.640453&mlon=10.055533#map=18/53.640453/10.055533) |
| neben Cuxhavener Straße | 3.82 | RSV | 0.28 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554297,5924837]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.469722/9.817979) · [OSM](https://www.openstreetmap.org/?mlat=53.469722&mlon=9.817979#map=18/53.469722/9.817979) |
| neben Berner Heerweg | 3.71 | HAUPT | 0.91 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573678,5938954]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594240/10.113226) · [OSM](https://www.openstreetmap.org/?mlat=53.594240&mlon=10.113226#map=18/53.594240/10.113226) |
| neben Meiendorfer Straße | 3.66 | HAUPT | 0.01 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577014,5942017]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.621283/10.164381) · [OSM](https://www.openstreetmap.org/?mlat=53.621283&mlon=10.164381#map=18/53.621283/10.164381) |
| neben Holsteiner Chaussee | 3.64 | HAUPT | 0.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560051,5944379]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.644733/9.908417) · [OSM](https://www.openstreetmap.org/?mlat=53.644733&mlon=9.908417#map=18/53.644733/9.908417) |
| neben Luruper Hauptstraße | 3.58 | HAUPT | 0.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557235,5939064]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.597277/9.864841) · [OSM](https://www.openstreetmap.org/?mlat=53.597277&mlon=9.864841#map=18/53.597277/9.864841) |
| neben Kieler Straße | 3.51 | HAUPT | 0.19 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560204,5939866]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.604153/9.909859) · [OSM](https://www.openstreetmap.org/?mlat=53.604153&mlon=9.909859#map=18/53.604153/9.909859) |
| neben Winsener Straße | 3.49 | HAUPT | 2.79 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565212,5920057]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.425524/9.981396) · [OSM](https://www.openstreetmap.org/?mlat=53.425524&mlon=9.981396#map=18/53.425524/9.981396) |
| neben Schnackenburgallee | 3.48 | HAUPT | 0.37 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559898,5938256]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.589718/9.904915) · [OSM](https://www.openstreetmap.org/?mlat=53.589718&mlon=9.904915#map=18/53.589718/9.904915) |

## RSV-Abschnitte (C-NET-06)

22 Korridore mit RSV-Läufen. Längste Korridore mit RSV-Anteil:

| route_id | Korridor | km | RSV km | Median Rad/Werktag | Prüfen |
| --- | --- | ---: | ---: | ---: | --- |
| `rt_46a9a9c639d7d6c8` | Innenstadt (Rathausmarkt) – Umsteigeknoten Neugraben | 23.2 | 15.3 | 1 935 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566101,5925609]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.475314/9.995944) · [OSM](https://www.openstreetmap.org/?mlat=53.475314&mlon=9.995944#map=18/53.475314/9.995944) |
| `rt_3645a25b810b0a3f` | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) | 19.8 | 13.3 | 1 859 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565693,5927156]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.489264/9.990118) · [OSM](https://www.openstreetmap.org/?mlat=53.489264&mlon=9.990118#map=18/53.489264/9.990118) |
| `rt_e91f74bd5e0fdea8` | Innenstadt (Rathausmarkt) – Umsteigeknoten Bergedorf | 18.8 | 11.5 | 2 677 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573736,5933031]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.541004/10.112699) · [OSM](https://www.openstreetmap.org/?mlat=53.541004&mlon=10.112699#map=18/53.541004/10.112699) |
| `rt_0d622f210ba0d8d0` | Innenstadt (Rathausmarkt) – Hochschule HAW - Life Sciences - Campus Bergedorf | 18.1 | 11.5 | 2 862 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573428,5933191]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.542486/10.108102) · [OSM](https://www.openstreetmap.org/?mlat=53.542486&mlon=10.108102#map=18/53.542486/10.108102) |
| `rt_bc1008c8faddf565` | Innenstadt (Rathausmarkt) – Hochschule HAW Hamburg Energie Campus | 20.9 | 11.5 | 2 335 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573789,5932167]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.533228/10.113295) · [OSM](https://www.openstreetmap.org/?mlat=53.533228&mlon=10.113295#map=18/53.533228/10.113295) |
| `rt_d1185a69cd09cd51` | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Mitte (278 Tsd. m²) | 9.4 | 7.5 | 4 314 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569891,5934617]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.555777/10.055045) · [OSM](https://www.openstreetmap.org/?mlat=53.555777&mlon=10.055045#map=18/53.555777/10.055045) |
| `rt_ab30177e1398e7c5` | Innenstadt (Rathausmarkt) – Hochschule Helmut-Schmidt-Universität – Universität der Bundeswehr Hamburg | 10.1 | 7.1 | 2 340 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570213,5934548]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.555114/10.059896) · [OSM](https://www.openstreetmap.org/?mlat=53.555114&mlon=10.059896#map=18/53.555114/10.059896) |
| `rt_09e1893552ad7372` | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Mitte (263 Tsd. m²) | 9.7 | 6.9 | 2 690 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567796,5931226]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.525578/10.022700) · [OSM](https://www.openstreetmap.org/?mlat=53.525578&mlon=10.022700#map=18/53.525578/10.022700) |
| `rt_1123a8241fbeabaf` | Innenstadt (Rathausmarkt) – Hochschule I. Institut für Theoretische Physik | 9.0 | 6.8 | 3 480 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561918,5934079]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.551944/9.934600) · [OSM](https://www.openstreetmap.org/?mlat=53.551944&mlon=9.934600#map=18/53.551944/9.934600) |
| `rt_9f1b1b0a361099ed` | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Wandsbek (290 Tsd. m²) | 8.5 | 6.1 | 2 949 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568417,5936625]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.574016/10.033242) · [OSM](https://www.openstreetmap.org/?mlat=53.574016&mlon=10.033242#map=18/53.574016/10.033242) |
| `rt_a3f51202ca48fa1c` | Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) – Arbeitsplatzschwerpunkt Harburg (241 Tsd. m²) | 6.8 | 6.0 | 2 813 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562608,5925087]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.471045/9.943226) · [OSM](https://www.openstreetmap.org/?mlat=53.471045&mlon=9.943226#map=18/53.471045/9.943226) |
| `rt_c0ce6a0c99b89187` | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Nord (327 Tsd. m²) | 8.5 | 5.8 | 1 724 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565978,5937485]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.582059/9.996591) · [OSM](https://www.openstreetmap.org/?mlat=53.582059&mlon=9.996591#map=18/53.582059/9.996591) |
| `rt_6d054520df21bbad` | Innenstadt (Rathausmarkt) – Hochschule Helmut-Schmidt-Universität - Campus Nord | 10.0 | 5.5 | 1 136 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569187,5936505]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572841/10.044849) · [OSM](https://www.openstreetmap.org/?mlat=53.572841&mlon=10.044849#map=18/53.572841/10.044849) |
| `rt_463b00cfca1d45be` | Umsteigeknoten Hamburg-Harburg – Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) | 7.4 | 5.4 | 1 505 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562896,5925065]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470813/9.947549) · [OSM](https://www.openstreetmap.org/?mlat=53.470813&mlon=9.947549#map=18/53.470813/9.947549) |
| `rt_01ce314479204899` | Innenstadt (Rathausmarkt) – Umsteigeknoten Hamburg-Harburg | 13.8 | 5.4 | 1 510 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565247,5929856]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.513591/9.983962) · [OSM](https://www.openstreetmap.org/?mlat=53.513591&mlon=9.983962#map=18/53.513591/9.983962) |

## Parallelregel P-ATT-03 (C-NET-10)

328 verschiedene Läufe an Straßen mit DTV > 15 000 (auf 435 Routen geprüft): nur über die Hauptstraße 242, Umweg zu groß 82, verlegt 4.

| Routen | Straße (DTV > Schwelle) | Kategorie | Lauf m | Alternative | Alternative m | davon Hauptstraße m | Umwegfaktor | Schwelle | Ergebnis | Prüfen |
| ---: | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- | --- |
| 1 | Schiffbeker Weg, Schiffbeker Höhe | HAUPT | 712 | Maukestieg, Sandkoppelweg, Gothaer Weg | 724 | 0 | 1.02 | 1.2 | verlegt | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573328,5933701]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.547076/10.106713) · [OSM](https://www.openstreetmap.org/?mlat=53.547076&mlon=10.106713#map=18/53.547076/10.106713) |
| 1 | neben Friedrich-Ebert-Damm | HAUPT | 495 | neben Friedrich-Ebert-Damm, neben Eckerkoppel | 586 | 19 | 1.18 | 1.2 | verlegt | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573563,5939329]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.597623/10.111580) · [OSM](https://www.openstreetmap.org/?mlat=53.597623&mlon=10.111580#map=18/53.597623/10.111580) |
| 1 | neben Dehnhaide, Dehnhaide | HAUPT | 420 | Langenrehm, Dehnhaide | 35 | 19 | 0.08 | 1.2 | verlegt | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569144,5937215]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.579225/10.044351) · [OSM](https://www.openstreetmap.org/?mlat=53.579225&mlon=10.044351#map=18/53.579225/10.044351) |
| 1 | Eiffestraße | HAUPT | 382 | Grevenweg, Eiffestraße | 31 | 17 | 0.08 | 1.2 | verlegt | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568750,5934228]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.552437/10.037737) · [OSM](https://www.openstreetmap.org/?mlat=53.552437&mlon=10.037737#map=18/53.552437/10.037737) |
| 1 | Elbchaussee, Dockenhudener Straße | HAUPT | 3 805 | Elbuferweg, Elbschloßstraße, Elbchaussee | 4 620 | 2 096 | 1.21 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555561,5934186]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.553616/9.838684) · [OSM](https://www.openstreetmap.org/?mlat=53.553616&mlon=9.838684#map=18/53.553616/9.838684) |
| 1 | neben Stader Straße, neben Cuxhavener Straße, Cuxhavener Straße | RSV | 2 169 | neben Stader Straße, neben Cuxhavener Straße, Hausbrucher Bahnhofstraße | 2 871 | 1 912 | 1.32 | 1.1 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560355,5925010]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470616/9.909273) · [OSM](https://www.openstreetmap.org/?mlat=53.470616&mlon=9.909273#map=18/53.470616/9.909273) |
| 1 | neben Wandsbeker Marktstraße, Wandsbeker Allee, Wandsbeker Marktstraße | HAUPT | 1 992 | neben Wandsbeker Marktstraße, neben Robert-Schuman-Brücke, Wandsbeker Marktstraße | 2 945 | 428 | 1.48 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571426,5936891]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.576014/10.078732) · [OSM](https://www.openstreetmap.org/?mlat=53.576014&mlon=10.078732#map=18/53.576014/10.078732) |
| 1 | Saseler Chaussee, neben Rolfinckstraße, neben Saseler Chaussee | HAUPT | 1 774 | Saseler Chaussee, Farmsener Weg, Volksdorfer Weg | 2 486 | 1 153 | 1.40 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572794,5944714]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.646126/10.101214) · [OSM](https://www.openstreetmap.org/?mlat=53.646126&mlon=10.101214#map=18/53.646126/10.101214) |
| 1 | Krohnstieg, neben Krohnstieg | HAUPT | 1 692 | Garstedter Weg, Krohnstieg, Niendorfer Straße | 1 695 | 1 124 | 1.00 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564685,5944647]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.646589/9.978552) · [OSM](https://www.openstreetmap.org/?mlat=53.646589&mlon=9.978552#map=18/53.646589/9.978552) |
| 1 | neben Saseler Chaussee, Farmsener Weg | HAUPT | 1 552 | neben Saseler Chaussee, neben Kunaustraße, Wegzoll | 1 776 | 1 054 | 1.14 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572788,5944639]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.645450/10.101116) · [OSM](https://www.openstreetmap.org/?mlat=53.645450&mlon=10.101116#map=18/53.645450/10.101116) |
| 1 | Saseler Chaussee, Bergstedter Chaussee / Saseler Chaussee, Bergstedter Chaussee | HAUPT | 1 393 | Saseler Chaussee, Bergstedter Chaussee / Saseler Chaussee, Bergstedter Chaussee | 1 593 | 1 223 | 1.14 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573793,5946422]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.661331/10.116732) · [OSM](https://www.openstreetmap.org/?mlat=53.661331&mlon=10.116732#map=18/53.661331/10.116732) |
| 1 | neben Cuxhavener Straße, neben Stader Straße | RSV | 1 315 | neben Cuxhavener Straße, neben Stader Straße | 1 315 | 1 315 | 1.00 | 1.1 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560487,5924992]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470440/9.911258) · [OSM](https://www.openstreetmap.org/?mlat=53.470440&mlon=9.911258#map=18/53.470440/9.911258) |
| 2 | neben Stader Straße, neben Cuxhavener Straße | RSV | 1 315 | neben Stader Straße, neben Cuxhavener Straße | 1 315 | 1 315 | 1.00 | 1.1 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559930,5925026]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470813/9.902868) · [OSM](https://www.openstreetmap.org/?mlat=53.470813&mlon=9.902868#map=18/53.470813/9.902868) |
| 1 | neben Stader Straße, neben Cuxhavener Straße | HAUPT | 1 315 | neben Stader Straße, neben Cuxhavener Straße | 1 315 | 1 315 | 1.00 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559930,5925026]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470813/9.902868) · [OSM](https://www.openstreetmap.org/?mlat=53.470813&mlon=9.902868#map=18/53.470813/9.902868) |
| 1 | neben Sander Damm, neben Curslacker Neuer Deich | HAUPT | 1 306 | neben Sander Damm, neben Vierlandenstraße, neben Curslacker Neuer Deich | 1 430 | 1 254 | 1.10 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580212,5926662]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.482816/10.208771) · [OSM](https://www.openstreetmap.org/?mlat=53.482816&mlon=10.208771#map=18/53.482816/10.208771) |
| 2 | neben Curslacker Neuer Deich, neben Sander Damm | HAUPT | 1 306 | neben Curslacker Neuer Deich, neben Neuer Weg, neben Vierlandenstraße | 1 430 | 1 254 | 1.10 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580214,5926832]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.484341/10.208852) · [OSM](https://www.openstreetmap.org/?mlat=53.484341&mlon=10.208852#map=18/53.484341/10.208852) |
| 3 | neben Buxtehuder Straße, neben Stader Straße | RSV | 1 275 | Grumbrechtstraße, Bissingstraße, Nobléestraße | 1 467 | 0 | 1.15 | 1.1 | Umweg zu groß | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563643,5924987]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470025/9.958790) · [OSM](https://www.openstreetmap.org/?mlat=53.470025&mlon=9.958790#map=18/53.470025/9.958790) |
| 1 | neben Stader Straße, neben Buxtehuder Straße | RSV | 1 275 | neben Milchgrund, Milchgrund, Hermesweg | 1 467 | 0 | 1.15 | 1.1 | Umweg zu groß | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563488,5925014]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470283/9.956465) · [OSM](https://www.openstreetmap.org/?mlat=53.470283&mlon=9.956465#map=18/53.470283/9.956465) |
| 1 | neben Borsteler Chaussee, neben Papenreye, neben Kollaustraße | HAUPT | 1 254 | neben Papenreye, neben Kollaustraße | 1 363 | 1 144 | 1.09 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563848,5940887]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.612901/9.965125) · [OSM](https://www.openstreetmap.org/?mlat=53.612901&mlon=9.965125#map=18/53.612901/9.965125) |
| 1 | neben Cuxhavener Straße, Cuxhavener Straße | HAUPT | 1 207 | An de Geest, Op de Wisch, Sandbek | 1 907 | 377 | 1.58 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554966,5925007]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.471182/9.828094) · [OSM](https://www.openstreetmap.org/?mlat=53.471182&mlon=9.828094#map=18/53.471182/9.828094) |
| 1 | Bergedorfer Straße | HAUPT | 1 173 | Bergedorfer Straße | 1 173 | 1 173 | 1.00 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578717,5928583]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.500300/10.186729) · [OSM](https://www.openstreetmap.org/?mlat=53.500300&mlon=10.186729#map=18/53.500300/10.186729) |
| 1 | neben Bargteheider Straße, Berner Straße, Meiendorfer Straße | HAUPT | 1 172 | Kohövedstraße, Boytinstraße, neben Boytinstraße | 2 040 | 412 | 1.74 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576294,5940914]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.611481/10.153223) · [OSM](https://www.openstreetmap.org/?mlat=53.611481&mlon=10.153223#map=18/53.611481/10.153223) |
| 1 | neben Meiendorfer Straße, Oldenfelder Stieg, Bargteheider Straße | HAUPT | 1 125 | Dassauweg, Saseler Straße, neben Meiendorfer Straße | 1 943 | 664 | 1.73 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576767,5941689]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.618376/10.160571) · [OSM](https://www.openstreetmap.org/?mlat=53.618376&mlon=10.160571#map=18/53.618376/10.160571) |
| 2 | neben Finkenwerder Straße | HAUPT | 1 102 | Dradenaustraße, Finkenwerder Straße, neben Finkenwerder Straße | 1 208 | 263 | 1.10 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559974,5929865]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.514300/9.904451) · [OSM](https://www.openstreetmap.org/?mlat=53.514300&mlon=9.904451#map=18/53.514300/9.904451) |
| 1 | neben Krohnstieg, neben Langenhorner Chaussee | HAUPT | 1 099 | Langenhorner Chaussee, neben Langenhorner Chaussee, Timmstieg | 1 829 | 878 | 1.66 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566959,5944325]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.643411/10.012882) · [OSM](https://www.openstreetmap.org/?mlat=53.643411&mlon=10.012882#map=18/53.643411/10.012882) |
| 1 | neben Rennbahnstraße | HAUPT | 1 096 | neben Rennbahnstraße | 1 096 | 1 096 | 1.00 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571513,5935304]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.561734/10.079693) · [OSM](https://www.openstreetmap.org/?mlat=53.561734&mlon=10.079693#map=18/53.561734/10.079693) |
| 4 | neben Finkenwerder Straße | HAUPT | 1 094 | neben Finkenwerder Straße, Dradenaustraße, Finkenwerder Straße | 1 214 | 268 | 1.11 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559971,5929868]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.514326/9.904407) · [OSM](https://www.openstreetmap.org/?mlat=53.514326&mlon=9.904407#map=18/53.514326/9.904407) |
| 1 | neben Schnackenburgallee | HAUPT | 1 083 | neben Schnackenburgallee, Am Volkspark, Schnackenburgallee | 1 593 | 498 | 1.47 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560071,5937768]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.585318/9.907433) · [OSM](https://www.openstreetmap.org/?mlat=53.585318&mlon=9.907433#map=18/53.585318/9.907433) |
| 1 | neben Bargteheider Straße | HAUPT | 1 083 | neben Oldenfelder Straße, Delingsdorfer Weg, Oldenfelder Straße | 1 992 | 224 | 1.84 | 1.2 | nur über die Hauptstraße | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576222,5940721]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.609752/10.152094) · [OSM](https://www.openstreetmap.org/?mlat=53.609752&mlon=10.152094#map=18/53.609752/10.152094) |
| 1 | Saarlandstraße, neben Saarlandstraße | HAUPT | 1 080 | Hellbrookstraße, Alter Güterbahnhof, Alte Wöhr | 1 837 | 29 | 1.70 | 1.2 | Umweg zu groß | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568287,5939026]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.595617/10.031809) · [OSM](https://www.openstreetmap.org/?mlat=53.595617&mlon=10.031809#map=18/53.595617/10.031809) |

(298 weitere Läufe nicht gelistet; je Route in data/interim/cycle_routes.parquet, Spalte patt_runs.)

## Kontinuität (C-NET-11, P-COH-04)

- 5 Kanten angehoben (kurze Lücken zwischen gleichen höheren Kategorien).
- Routen mit Kategoriewechseln entlang des Wegs: 128 von 5030; mit Bruch durch Override: 0.
- Kategoriewechsel RSV↔HAUPT an Korridoren sind gewollt (RSV nur auf Läufen mit hoher Nachfrage); sie sind in data/interim/cycle_routes.parquet je Route gezählt (n_category_changes).

| Routenart | Routen | km (Summe Routenlängen) |
| --- | ---: | ---: |
| Anbindung Schule/Nahversorgung | 193 | 223 |
| Korridor | 209 | 1 008 |
| Verdichtung BASIS | 2703 | 926 |
| Verdichtung HAUPT | 1925 | 1 621 |

## Lückenliste (Maschen über der Höchstweite)

443 Maschen, nach Größe; vollständig in data/interim/cycle_mesh_gaps.parquet.

| Ebene | Seite m | Höchstweite m | Grund | Bezirk | Prüfen |
| --- | ---: | ---: | --- | --- | --- |
| HAUPT | 4 073 | 1197 | max_rounds erreicht | Wandsbek | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571889,5947892]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.674809/10.088274) · [OSM](https://www.openstreetmap.org/?mlat=53.674809&mlon=10.088274#map=18/53.674809/10.088274) |
| BASIS | 4 064 | 598 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Wandsbek | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571889,5947892]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.674809/10.088274) · [OSM](https://www.openstreetmap.org/?mlat=53.674809&mlon=10.088274#map=18/53.674809/10.088274) |
| BASIS | 3 150 | 643 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Altona | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[551153,5938727]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594878/9.772900) · [OSM](https://www.openstreetmap.org/?mlat=53.594878&mlon=9.772900#map=18/53.594878/9.772900) |
| HAUPT | 3 150 | 1285 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Altona | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[551153,5938727]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594878/9.772900) · [OSM](https://www.openstreetmap.org/?mlat=53.594878&mlon=9.772900#map=18/53.594878/9.772900) |
| BASIS | 2 565 | 2473 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Hamburg-Mitte | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559960,5932074]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.534148/9.904670) · [OSM](https://www.openstreetmap.org/?mlat=53.534148&mlon=9.904670#map=18/53.534148/9.904670) |
| HAUPT | 2 434 | 996 | max_rounds erreicht | Harburg | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556893,5922073]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.444606/9.856586) · [OSM](https://www.openstreetmap.org/?mlat=53.444606&mlon=9.856586#map=18/53.444606/9.856586) |
| BASIS | 2 419 | 509 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Harburg | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556893,5922073]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.444606/9.856586) · [OSM](https://www.openstreetmap.org/?mlat=53.444606&mlon=9.856586#map=18/53.444606/9.856586) |
| BASIS | 2 413 | 2213 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Harburg | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561798,5928570]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.502450/9.931703) · [OSM](https://www.openstreetmap.org/?mlat=53.502450&mlon=9.931703#map=18/53.502450/9.931703) |
| HAUPT | 2 037 | 1437 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Wandsbek | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572367,5947410]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.670417/10.095395) · [OSM](https://www.openstreetmap.org/?mlat=53.670417&mlon=10.095395#map=18/53.670417/10.095395) |
| BASIS | 2 025 | 437 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Hamburg-Mitte | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576327,5935134]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559533/10.152308) · [OSM](https://www.openstreetmap.org/?mlat=53.559533&mlon=10.152308#map=18/53.559533/10.152308) |
| HAUPT | 2 025 | 874 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Hamburg-Mitte | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576327,5935134]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559533/10.152308) · [OSM](https://www.openstreetmap.org/?mlat=53.559533&mlon=10.152308#map=18/53.559533/10.152308) |
| HAUPT | 2 020 | 789 | max_rounds erreicht | Wandsbek | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576973,5941360]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.615382/10.163598) · [OSM](https://www.openstreetmap.org/?mlat=53.615382&mlon=10.163598#map=18/53.615382/10.163598) |
| HAUPT | 1 874 | 881 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Altona | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[549809,5935311]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564309/9.752044) · [OSM](https://www.openstreetmap.org/?mlat=53.564309&mlon=9.752044#map=18/53.564309/9.752044) |
| HAUPT | 1 805 | 879 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Harburg | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567115,5920972]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.433508/10.010232) · [OSM](https://www.openstreetmap.org/?mlat=53.433508&mlon=10.010232#map=18/53.433508/10.010232) |
| BASIS | 1 805 | 440 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Harburg | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567115,5920972]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.433508/10.010232) · [OSM](https://www.openstreetmap.org/?mlat=53.433508&mlon=10.010232#map=18/53.433508/10.010232) |
| BASIS | 1 782 | 456 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Altona | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[549804,5935313]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564327/9.751972) · [OSM](https://www.openstreetmap.org/?mlat=53.564327&mlon=9.751972#map=18/53.564327/9.751972) |
| HAUPT | 1 664 | 981 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Wandsbek | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576575,5940138]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.604466/10.157287) · [OSM](https://www.openstreetmap.org/?mlat=53.604466&mlon=10.157287#map=18/53.604466/10.157287) |
| BASIS | 1 664 | 491 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Wandsbek | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576575,5940138]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.604466/10.157287) · [OSM](https://www.openstreetmap.org/?mlat=53.604466&mlon=10.157287#map=18/53.604466/10.157287) |
| BASIS | 1 614 | 1175 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Hamburg-Mitte | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572097,5931974]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.531728/10.087729) · [OSM](https://www.openstreetmap.org/?mlat=53.531728&mlon=10.087729#map=18/53.531728/10.087729) |
| BASIS | 1 612 | 1443 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Hamburg-Mitte | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568243,5929605]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.510949/10.029082) · [OSM](https://www.openstreetmap.org/?mlat=53.510949&mlon=10.029082#map=18/53.510949/10.029082) |
| BASIS | 1 594 | 489 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Wandsbek | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576973,5941360]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.615382/10.163598) · [OSM](https://www.openstreetmap.org/?mlat=53.615382&mlon=10.163598#map=18/53.615382/10.163598) |
| BASIS | 1 560 | 1410 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Hamburg-Mitte | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568559,5926895]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.486557/10.033256) · [OSM](https://www.openstreetmap.org/?mlat=53.486557&mlon=10.033256#map=18/53.486557/10.033256) |
| BASIS | 1 481 | 1209 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Wandsbek | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576825,5952671]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.717058/10.164154) · [OSM](https://www.openstreetmap.org/?mlat=53.717058&mlon=10.164154#map=18/53.717058/10.164154) |
| HAUPT | 1 478 | 1096 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Eimsbüttel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559938,5943391]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.635862/9.906509) · [OSM](https://www.openstreetmap.org/?mlat=53.635862&mlon=9.906509#map=18/53.635862/9.906509) |
| HAUPT | 1 430 | 626 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Eimsbüttel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559662,5943339]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.635429/9.902324) · [OSM](https://www.openstreetmap.org/?mlat=53.635429&mlon=9.902324#map=18/53.635429/9.902324) |
| BASIS | 1 430 | 313 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Eimsbüttel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559662,5943339]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.635429/9.902324) · [OSM](https://www.openstreetmap.org/?mlat=53.635429&mlon=9.902324#map=18/53.635429/9.902324) |
| BASIS | 1 403 | 627 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Eimsbüttel | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560012,5943974]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.641101/9.907738) · [OSM](https://www.openstreetmap.org/?mlat=53.641101&mlon=9.907738#map=18/53.641101/9.907738) |
| BASIS | 1 365 | 907 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Hamburg-Nord | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565703,5942855]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.630361/9.993581) · [OSM](https://www.openstreetmap.org/?mlat=53.630361&mlon=9.993581#map=18/53.630361/9.993581) |
| HAUPT | 1 342 | 807 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Wandsbek | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576956,5946835]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.664594/10.164689) · [OSM](https://www.openstreetmap.org/?mlat=53.664594&mlon=10.164689#map=18/53.664594/10.164689) |
| BASIS | 1 342 | 403 | keine Teilung möglich (weniger als zwei erreichbare Netzknoten am Außenrand) | Wandsbek | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576956,5946835]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.664594/10.164689) · [OSM](https://www.openstreetmap.org/?mlat=53.664594&mlon=10.164689#map=18/53.664594/10.164689) |

## 30 Zufallsstichproben (Seed 42)

| edge_id | Bezirk | Name | Art | Kategorie | Rad/Werktag | amtlich | Route | Prüfen |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `ce_0e1d83d28915dc9e` | Altona | Bernstorffstraße | road | HAUPT | 3 082 | – | `rt_1b9c1ec15ceedf68` | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563529,5934847]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558658/9.959080) · [OSM](https://www.openstreetmap.org/?mlat=53.558658&mlon=9.959080#map=18/53.558658/9.959080) |
| `ce_39bb6efb31c3109a` | Altona | neben Taşköprüstraße | path | ERSCHL | 0 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561683,5935344]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.563338/9.931312) · [OSM](https://www.openstreetmap.org/?mlat=53.563338&mlon=9.931312#map=18/53.563338/9.931312) |
| `ce_7cf8178f45f27db2` | Altona | – | path | ERSCHL | 0 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[552041,5936299]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572966/9.785906) · [OSM](https://www.openstreetmap.org/?mlat=53.572966&mlon=9.785906#map=18/53.572966/9.785906) |
| `ce_8ab7b65cb27936b9` | Altona | Altonaer Poststraße | road | ERSCHL | 0 | Bestand | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562334,5933885]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.550152/9.940844) · [OSM](https://www.openstreetmap.org/?mlat=53.550152&mlon=9.940844#map=18/53.550152/9.940844) |
| `ce_2bc960a2ce848093` | Bergedorf | Sichter | road | HAUPT | 22 | – | `rt_a30566b7d0f606a7` | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580914,5927340]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.488798/10.219532) · [OSM](https://www.openstreetmap.org/?mlat=53.488798&mlon=10.219532#map=18/53.488798/10.219532) |
| `ce_3b2bb8473d28d4d6` | Bergedorf | Bockhorster Höhe | road | ERSCHL | 0 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577876,5930261]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.515511/10.174475) · [OSM](https://www.openstreetmap.org/?mlat=53.515511&mlon=10.174475#map=18/53.515511/10.174475) |
| `ce_5b12a772e8bb4ac2` | Bergedorf | Wehrdeich | road | HAUPT | 1 981 | geplant | `rt_ffc8cc9c45cd1719` | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578803,5927078]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.486770/10.187651) · [OSM](https://www.openstreetmap.org/?mlat=53.486770&mlon=10.187651#map=18/53.486770/10.187651) |
| `ce_8b678c66ddf3f761` | Eimsbüttel | – | road | ERSCHL | 0 | geplant | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564116,5937889]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.585924/9.968558) · [OSM](https://www.openstreetmap.org/?mlat=53.585924&mlon=9.968558#map=18/53.585924/9.968558) |
| `ce_abc6142660b07fb6` | Eimsbüttel | Volksparkstraße | road | HAUPT | 0 | geplant | `rt_57f41b8dd5ab1b23` | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561050,5938484]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.591636/9.922361) · [OSM](https://www.openstreetmap.org/?mlat=53.591636&mlon=9.922361#map=18/53.591636/9.922361) |
| `ce_bd1adc80048064ef` | Eimsbüttel | Julius-Vosseler-Straße | road | ERSCHL | 1 069 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562651,5938731]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.593667/9.946592) · [OSM](https://www.openstreetmap.org/?mlat=53.593667&mlon=9.946592#map=18/53.593667/9.946592) |
| `ce_e671b4baed8076dd` | Eimsbüttel | – | path | BASIS | 177 | – | `rt_e01fdde6d39d84d3` | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564795,5936453]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572935/9.978509) · [OSM](https://www.openstreetmap.org/?mlat=53.572935&mlon=9.978509#map=18/53.572935/9.978509) |
| `ce_0a22f1fc42a92259` | Hamburg-Mitte | – | path | ERSCHL | 658 | Bestand | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565888,5930486]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.519168/9.993759) · [OSM](https://www.openstreetmap.org/?mlat=53.519168&mlon=9.993759#map=18/53.519168/9.993759) |
| `ce_0aae7f75e01d651d` | Hamburg-Mitte | Neßdeich | road | ERSCHL | 432 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556540,5932205]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.535706/9.853106) · [OSM](https://www.openstreetmap.org/?mlat=53.535706&mlon=9.853106#map=18/53.535706/9.853106) |
| `ce_1c7271fedfadf05d` | Hamburg-Mitte | Horner Rampe | road | ERSCHL | 851 | Bestand | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571781,5933578]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546187/10.083330) · [OSM](https://www.openstreetmap.org/?mlat=53.546187&mlon=10.083330#map=18/53.546187/10.083330) |
| `ce_8ede197ff5496440` | Hamburg-Mitte | Bürgerweide | road | ERSCHL | 1 456 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568803,5935004]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559400/10.038718) · [OSM](https://www.openstreetmap.org/?mlat=53.559400&mlon=10.038718#map=18/53.559400/10.038718) |
| `ce_c6daeec0afd7fa3b` | Hamburg-Mitte | neben Klosterwall | path | ERSCHL | 3 076 | geplant | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566643,5933942]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.550136/10.005889) · [OSM](https://www.openstreetmap.org/?mlat=53.550136&mlon=10.005889#map=18/53.550136/10.005889) |
| `ce_244f9315d1c931d6` | Hamburg-Nord | – | ferry | ERSCHL | 136 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566555,5936542]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.573516/10.005108) · [OSM](https://www.openstreetmap.org/?mlat=53.573516&mlon=10.005108#map=18/53.573516/10.005108) |
| `ce_570528d05d29c065` | Hamburg-Nord | Timmerloh | road | BASIS | 141 | – | `rt_032ed2fe60fbdf6a` | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567487,5945934]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.657802/10.021217) · [OSM](https://www.openstreetmap.org/?mlat=53.657802&mlon=10.021217#map=18/53.657802/10.021217) |
| `ce_5d7e9d35e5ed864c` | Hamburg-Nord | – | road | BASIS | 0 | – | `rt_a47056974ed90874` | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567595,5940285]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607016/10.021616) · [OSM](https://www.openstreetmap.org/?mlat=53.607016&mlon=10.021616#map=18/53.607016/10.021616) |
| `ce_cac951672170e268` | Hamburg-Nord | Bendixensweg | road | BASIS | 25 | – | `rt_5556df93e9eb3c3f` | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569031,5939317]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.598136/10.043116) · [OSM](https://www.openstreetmap.org/?mlat=53.598136&mlon=10.043116#map=18/53.598136/10.043116) |
| `ce_0b5c7abf5fc36f0b` | Harburg | – | path | ERSCHL | 0 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555777,5925142]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.472314/9.840326) · [OSM](https://www.openstreetmap.org/?mlat=53.472314&mlon=9.840326#map=18/53.472314/9.840326) |
| `ce_d35fee753dfd8605` | Harburg | Cuxhavener Straße | road | ERSCHL | 104 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558181,5925138]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.472012/9.876549) · [OSM](https://www.openstreetmap.org/?mlat=53.472012&mlon=9.876549#map=18/53.472012/9.876549) |
| `ce_e236be26b3192f6e` | Harburg | neben Hohe Straße | path | ERSCHL | 1 302 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564811,5922969]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.451747/9.975968) · [OSM](https://www.openstreetmap.org/?mlat=53.451747&mlon=9.975968#map=18/53.451747/9.975968) |
| `ce_3a77b3f377c7fff9` | Wandsbek | Sonnenweg | road | ERSCHL | 35 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574383,5938419]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.589329/10.123753) · [OSM](https://www.openstreetmap.org/?mlat=53.589329&mlon=10.123753#map=18/53.589329/10.123753) |
| `ce_7be121ee4e62a624` | Wandsbek | Baggesenstieg | road | BASIS | 16 | – | `rt_f8d22bba0e5b4a1d` | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572617,5945496]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.653182/10.098731) · [OSM](https://www.openstreetmap.org/?mlat=53.653182&mlon=10.098731#map=18/53.653182/10.098731) |
| `ce_a06e8872ffc89448` | Wandsbek | Baben de Möhl | road | ERSCHL | 0 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573273,5947692]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.672825/10.109172) · [OSM](https://www.openstreetmap.org/?mlat=53.672825&mlon=10.109172#map=18/53.672825/10.109172) |
| `ce_bf7607d1b83eab1b` | Wandsbek | – | path | ERSCHL | 0 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570263,5936563]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.573220/10.061105) · [OSM](https://www.openstreetmap.org/?mlat=53.573220&mlon=10.061105#map=18/53.573220/10.061105) |
| `ce_cda57e4f3b8da40e` | Wandsbek | Tegelweg | road | ERSCHL | 34 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573361,5940049]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.604124/10.108695) · [OSM](https://www.openstreetmap.org/?mlat=53.604124&mlon=10.108695#map=18/53.604124/10.108695) |
| `ce_d21c146febc9478e` | Wandsbek | Kaskadenpark | road | ERSCHL | 85 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575125,5937448]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.580497/10.134718) · [OSM](https://www.openstreetmap.org/?mlat=53.580497&mlon=10.134718#map=18/53.580497/10.134718) |
| `ce_44f558c621a1ef09` | nan | – | road | ERSCHL | 0 | – | – | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[583070,5926378]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.479818/10.251769) · [OSM](https://www.openstreetmap.org/?mlat=53.479818&mlon=10.251769#map=18/53.479818/10.251769) |

## Grenzen

- Ohne Bezirks- und Stadtteilzentren fehlen Korridore zwischen Zentren ohne Schnellbahn-Umsteigeknoten, Hochschule oder großen Arbeitsplatzschwerpunkt. Sobald ein Datensatz zum Zentrenkonzept vorliegt (sources.yaml `centres`), neu rechnen.
- Die Nachfrage ist ein einfaches Modell mit mäßiger Kalibrierung (reports/cycle_demand.md); RSV hängt direkt am Auslöser 2 000 Rad/Werktag. Gebündelte Nebenstraßen können zu RSV werden, wo in Wirklichkeit die Hauptstraße genutzt würde.
- Die Maschenregel erzeugt ein dichtes Netz: Bei 600 m bzw. 300 m Maschenweite entstehen rechnerisch rund 2 bzw. 4 km Netz je km². Die Werte stammen aus der Delfter Netzlogik (DCE) und sind für Hamburg zu prüfen.
- Verdichtung wählt die Kante mit der höchsten Modellnachfrage im Kernbereich der Masche als Start; bei fehlender Nachfrage entscheidet die Lage zur Maschenmitte. Das Ergebnis ist ein Vorschlag, keine Optimierung.
- Barrieren nur Bahn (ohne Tunnel) und Flüsse/Kanäle aus OSM; Autobahnen sind keine Barriere, weil der Radgraph sie nicht enthält und Querungen über die Kanten erfasst sind. Ausschlussflächen aus OSM-Landnutzung.
- Der Netzentwurf ist ungerichtet; Einbahnstraßen ohne Radfreigabe in Gegenrichtung zählen in einer Richtung.
- Fähren können Teil eines Korridors sein (z. B. Elbquerung); sie erhalten die Kategorie der Route.

## Quellen und Lizenzen

- © OpenStreetMap-Beitragende (ODbL): Radgraph, Barrieren, Ausschlussflächen, Hochschulen, Schulen, Geschäfte; abgeleitete Daten unter ODbL.
- Radnetz Hamburg (WFS) © Freie und Hansestadt Hamburg, BVM (dl-de/by-2.0).
- ALKIS © Freie und Hansestadt Hamburg, LGV (dl-de/by-2.0); HVV-GTFS © Hamburger Verkehrsverbund GmbH (dl-de/by-2.0).
