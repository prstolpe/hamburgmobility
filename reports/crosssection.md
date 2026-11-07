# Querschnittsbericht – Stufe 7

Erzeugt: 2026-11-07T15:03:11+00:00 von `pipeline/s07_crosssection.py`, rules.yaml 0.16.0. Nicht amtlicher Entwurf.

## Kennzahlen

- Abschnitte im Arbeitsgebiet: 34 702 (4 387.3 km); davon mit Bezirk (Hamburg (7 Bezirke)): 33 712
- Transekte: 219 291 (alle 20 m, ± 40 m, Tangente ± 10 m, Mittellinie vereinfacht 2 m)
- Verworfen: nahe Knoten (≤ 20 m) 28.6 %, Brücke/Tunnel 1.8 %
- Verkehrsfläche: gültig 59.2 %; Mittelpunkt außerhalb der ALKIS-Verkehrsfläche 6.2 %; offen/Platz (keine Grenze in 40 m) 4.4 %
- Fassade: gültig 22.1 %; offen 47.7 %; Mittelpunkt in Gebäude 0.0 %
- Abschnitte mit width_p10_m: 89.3 % (Länge: 91.1 %); mit Fassadenbreite 81.3 %
- Engstellen (≥ 3 Transekte unter p10): 339 in 332 Abschnitten
- ALKIS: 41 558 Verkehrsflächen (Platz, Strassenverkehr, Weg), 377 027 oberirdische Gebäude

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| Breiten positiv | ok | 129923 gültige Transekte Verkehrsfläche |
| min ≤ p10 ≤ Median | ok | 30981 Abschnitte mit Breite |
| transect_id eindeutig | ok | 219291 Transekte |

## Validierung im Orthophoto (Prüfschritt)

50 zufällige gültige Transekte in Hamburg (7 Bezirke) (Seed 42) stehen in `reports/transect_sample.geojson` (EPSG:4326, Breite Verkehrsfläche Grenze zu Grenze). Messung im DOP20 eintragen in `reports/transect_measurements.csv` (Spalten `transect_id`, `measured_m`) und Stufe neu laufen lassen.

| Kennzahl | Wert |
| --- | --- |
| gemessene Transekte | _offen_ |
| mittlere absolute Abweichung (Ziel < 1 m, Annahme) | _offen – nach manueller Messung_ |

## Methode

- **Transekte (S-XS-01):** Mittellinie vereinfacht, Transekt alle spacing_m ab spacing_m/2, Richtung senkrecht zur Sehne über ± tangent_half_m.
- **Verkehrsfläche (S-XS-02):** zusammenhängende Strecke des Transekts in ALKIS-Flächen Platz, Strassenverkehr, Weg um den Mittelpunkt; aneinandergrenzende Flächen zählen als eine. `width_p10_m` (für C-G30-02) kommt aus dieser Variante.
- **Fassade (S-XS-03):** Abstand der ersten oberirdischen ALKIS-Gebäude (wie S-FEAT-03) links und rechts.
- **Sonderfälle (S-XS-04):** Knoten = Abschnittsenden mit Grad ≠ 2; Brücken/Tunnel: Mittelpunkt auf einem OSM-Way des Abschnitts mit bridge/tunnel. Offene Transekte gehen nicht in die Statistik ein.
- **Aggregation (S-XS-05):** Median, Quantil 0.1, Minimum; Engstelle = mindestens 3 aufeinanderfolgende gültige Transekte unter dem p10 des Abschnitts.
- **Machbarkeit (S-XS-06):** width_ratio = width_p10_m / erforderliche Breite; GOW50 16.50 m, GOW30_narrow 10.80 m, ETW30 10.80 m (bei Bereichen die Untergrenze). Klassen: fits ≥ 1.00, tight ≥ 0.85, sonst does_not_fit.
- **Fehlerquellen (guide.md 4.3 a):** Straßenflurstücke enthalten Böschungen und Grün; Vorgärten fehlen in der Variante Verkehrsfläche; Versatz der OSM-Mittellinie (→ centre_outside); Arkaden und Durchfahrten.

## Machbarkeit je Soll-Kategorie (Arbeitsgebiet, Anteil der Länge)

| Ziel | erforderlich | fits | tight | does_not_fit | ohne Breite |
| --- | ---: | ---: | ---: | ---: | ---: |
| GOW50 | 16.50 m | 35.6 % | 8.1 % | 47.5 % | 8.9 % |
| GOW30_narrow | 10.80 m | 60.8 % | 11.0 % | 19.4 % | 8.9 % |
| ETW30 | 10.80 m | 60.8 % | 11.0 % | 19.4 % | 8.9 % |

## Machbarkeit GOW50 und Breitenabdeckung je Bezirk (Anteil der Länge)

| Bezirk | km | mit width_p10_m | GOW50 fits | tight | does_not_fit |
| --- | ---: | ---: | ---: | ---: | ---: |
| Altona | 620.5 | 93.9 % | 26.7 % | 8.1 % | 59.2 % |
| Bergedorf | 209.3 | 96.5 % | 35.3 % | 4.9 % | 56.4 % |
| Eimsbüttel | 470.4 | 96.9 % | 39.0 % | 11.0 % | 46.9 % |
| Hamburg-Mitte | 881.3 | 89.0 % | 46.8 % | 7.7 % | 34.4 % |
| Hamburg-Nord | 563.3 | 93.3 % | 52.9 % | 7.6 % | 32.8 % |
| Harburg | 465.2 | 91.2 % | 29.2 % | 8.3 % | 53.6 % |
| Wandsbek | 1 030.4 | 98.4 % | 28.0 % | 8.9 % | 61.6 % |
| **gesamt** | 4 240.4 | 94.0 % | 36.7 % | 8.3 % | 49.0 % |

## width_p10_m nach highway-Klasse (Median über Abschnitte)

| highway | Abschnitte | mit Breite | p10 Verkehrsfläche | p10 Fassade | GOW50 fits |
| --- | ---: | ---: | ---: | ---: | ---: |
| living_street | 1633 | 89.0 % | 7.3 | 24.4 | 9.4 % |
| motorway | 130 | 56.2 % | 42.4 | 50.0 | 55.4 % |
| motorway_link | 285 | 21.1 % | 35.3 | 44.2 | 18.6 % |
| pedestrian | 705 | 47.2 % | 14.9 | 17.8 | 21.1 % |
| primary | 2777 | 94.5 % | 31.4 | 41.2 | 92.5 % |
| primary_link | 106 | 45.3 % | 32.4 | 38.6 | 42.5 % |
| residential | 17571 | 94.9 % | 12.0 | 28.0 | 22.3 % |
| secondary | 3878 | 93.3 % | 27.0 | 40.6 | 84.9 % |
| secondary_link | 198 | 53.0 % | 29.1 | 43.3 | 48.5 % |
| service | 890 | 56.4 % | 10.1 | 28.0 | 16.4 % |
| tertiary | 4303 | 92.3 % | 20.0 | 36.1 | 70.4 % |
| tertiary_link | 115 | 60.9 % | 25.7 | 35.4 | 51.3 % |
| track | 352 | 43.5 % | 7.4 | 40.4 | 1.7 % |
| trunk | 76 | 84.2 % | 50.0 | 56.8 | 84.2 % |
| trunk_link | 113 | 31.0 % | 35.0 | 42.4 | 30.1 % |
| unclassified | 1570 | 76.1 % | 15.4 | 31.6 | 35.0 % |

## Verteilungen

### Breite Verkehrsfläche je Transekt (m)

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0.14 | 8.05 | 15393 | ███████ |
| 8.05 | 16 | 61628 | ██████████████████████████████ |
| 16 | 23.9 | 28687 | ██████████████ |
| 23.9 | 31.8 | 11833 | ██████ |
| 31.8 | 39.7 | 7178 | ███ |
| 39.7 | 47.6 | 2961 | █ |
| 47.6 | 55.5 | 1347 | █ |
| 55.5 | 63.4 | 546 |  |
| 63.4 | 71.4 | 279 |  |
| 71.4 | 79.3 | 71 |  |

### Breite Fassade je Transekt (m)

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 4.1 | 11.6 | 583 | ██ |
| 11.6 | 19.1 | 5113 | ██████████████ |
| 19.1 | 26.6 | 10084 | ███████████████████████████ |
| 26.6 | 34.1 | 11198 | ██████████████████████████████ |
| 34.1 | 41.6 | 8962 | ████████████████████████ |
| 41.6 | 49.2 | 6353 | █████████████████ |
| 49.2 | 56.7 | 3804 | ██████████ |
| 56.7 | 64.2 | 1540 | ████ |
| 64.2 | 71.7 | 599 | ██ |
| 71.7 | 79.2 | 187 | █ |

### width_p10_m je Abschnitt (m)

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 2.4 | 9.91 | 6242 | ███████████████ |
| 9.91 | 17.4 | 12414 | ██████████████████████████████ |
| 17.4 | 24.9 | 5133 | ████████████ |
| 24.9 | 32.4 | 3683 | █████████ |
| 32.4 | 40 | 2054 | █████ |
| 40 | 47.5 | 749 | ██ |
| 47.5 | 55 | 376 | █ |
| 55 | 62.5 | 200 |  |
| 62.5 | 70 | 106 |  |
| 70 | 77.5 | 24 |  |

Fassade schmaler als Verkehrsfläche bei 0.6 % der Transekte mit beiden Werten (Hinweis auf Gebäude im Straßenflurstück, Arkaden oder Versatz).

## Stichprobe (30 zufällige Abschnitte in Hamburg (7 Bezirke), nach Bezirk geschichtet, Seed 42)

Links auf OSM-Karte und OSM-Way; Orthophoto-/Panoramax-Links folgen, sobald das Linkformat geklärt ist.

| segment_id | Bezirk | Name | highway | Länge m | Transekte | gültig | p10 Verkehrsfl. | Median | p10 Fassade | GOW50 | GOW30 | Karte | Way |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `seg_0b429570fa26ebba` | Altona | Blankeneser Landstraße | secondary | 171 | 9.0 | 6.0 | 21.5 | 21.6 | 30.1 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.565854&mlon=9.799288#map=18/53.565854/9.799288) | [Way](https://www.openstreetmap.org/way/4347380) |
| `seg_30696dcbf7bc7a04` | Altona | Stresemannstraße | primary | 55 | 3.0 | 0.0 | 21.8 | 21.9 | 21.8 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.563539&mlon=9.941936#map=18/53.563539/9.941936) | [Way](https://www.openstreetmap.org/way/936598996) |
| `seg_69ef3a0b69aab218` | Altona | Augustenpassage | residential | 187 | 9.0 | 7.0 | 4.4 | 5.9 | 13.6 | does_not_fit | does_not_fit | [Karte](https://www.openstreetmap.org/?mlat=53.559088&mlon=9.965603#map=18/53.559088/9.965603) | [Way](https://www.openstreetmap.org/way/618750343) |
| `seg_76cb381fe708c1fa` | Altona | Babenwischenweg | unclassified | 215 | 11.0 | 9.0 | 7.0 | 7.0 | – | does_not_fit | does_not_fit | [Karte](https://www.openstreetmap.org/?mlat=53.609687&mlon=9.763284#map=18/53.609687/9.763284) | [Way](https://www.openstreetmap.org/way/139864005) |
| `seg_264144b18b9fcea1` | Bergedorf | Agnes-Wolffson-Straße | living_street | 7 | 0.0 | 0.0 | 18.4 | 19.0 | 29.8 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.485344&mlon=10.179786#map=18/53.485344/10.179786) | [Way](https://www.openstreetmap.org/way/547484929) |
| `seg_3da7e9d4c44d23c5` | Bergedorf | Bergedorfer Straße | primary | 537 | 27.0 | 7.0 | 50.4 | 60.4 | 56.8 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.521662&mlon=10.148217#map=18/53.521662/10.148217) | [Way](https://www.openstreetmap.org/way/229835361) |
| `seg_1abf10d7274d8422` | Eimsbüttel | Rahweg | residential | 324 | 16.0 | 14.0 | 12.0 | 12.0 | 32.7 | does_not_fit | fits | [Karte](https://www.openstreetmap.org/?mlat=53.641256&mlon=9.977482#map=18/53.641256/9.977482) | [Way](https://www.openstreetmap.org/way/148170157) |
| `seg_b14dd9d1cd005339` | Eimsbüttel | Herulerweg | unclassified | 19 | 1.0 | 0.0 | 7.2 | 9.7 | – | does_not_fit | does_not_fit | [Karte](https://www.openstreetmap.org/?mlat=53.650258&mlon=9.949240#map=18/53.650258/9.949240) | [Way](https://www.openstreetmap.org/way/25739516) |
| `seg_c232d0e509b97fa5` | Eimsbüttel | Burgwedelkamp | residential | 62 | 3.0 | 0.0 | 15.0 | 15.0 | 25.3 | tight | fits | [Karte](https://www.openstreetmap.org/?mlat=53.641930&mlon=9.911588#map=18/53.641930/9.911588) | [Way](https://www.openstreetmap.org/way/4089419) |
| `seg_c330d48355534e10` | Eimsbüttel | Hohe Weide | residential | 266 | 13.0 | 11.0 | 23.0 | 23.0 | 23.3 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.576150&mlon=9.973005#map=18/53.576150/9.973005) | [Way](https://www.openstreetmap.org/way/137037866) |
| `seg_08e2ef58517bf643` | Hamburg-Mitte | Bürgerweide | primary | 14 | 1.0 | 0.0 | 51.0 | 51.0 | 39.7 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.559557&mlon=10.038893#map=18/53.559557/10.038893) | [Way](https://www.openstreetmap.org/way/1116978247) |
| `seg_09aed50abf56bb66` | Hamburg-Mitte | Billstieg | living_street | 157 | 8.0 | 0.0 | 5.6 | 5.6 | – | does_not_fit | does_not_fit | [Karte](https://www.openstreetmap.org/?mlat=53.534394&mlon=10.110004#map=18/53.534394/10.110004) | [Way](https://www.openstreetmap.org/way/25581052) |
| `seg_196a8094aa248d80` | Hamburg-Mitte | Lietbargredder | residential | 283 | 14.0 | 11.0 | 15.0 | 15.0 | 44.8 | tight | fits | [Karte](https://www.openstreetmap.org/?mlat=53.527304&mlon=10.152096#map=18/53.527304/10.152096) | [Way](https://www.openstreetmap.org/way/23044175) |
| `seg_7fda4452d37b8c74` | Hamburg-Mitte | Neßdeich | tertiary | 93 | 5.0 | 3.0 | 18.8 | 19.8 | 31.1 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.534354&mlon=9.861437#map=18/53.534354/9.861437) | [Way](https://www.openstreetmap.org/way/582276139) |
| `seg_a63abe1685a892ba` | Hamburg-Mitte | Riedweg | residential | 152 | 8.0 | 6.0 | 13.5 | 14.0 | 38.1 | does_not_fit | fits | [Karte](https://www.openstreetmap.org/?mlat=53.547382&mlon=10.096196#map=18/53.547382/10.096196) | [Way](https://www.openstreetmap.org/way/22604799) |
| `seg_b3afd578702025a0` | Hamburg-Mitte | Dratelnstraße | secondary | 202 | 10.0 | 8.0 | 22.5 | 23.1 | 31.7 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.500583&mlon=10.001670#map=18/53.500583/10.001670) | [Way](https://www.openstreetmap.org/way/1321676828) |
| `seg_25faecf475c757b5` | Hamburg-Nord | Wakendorfer Weg | residential | 66 | 3.0 | 1.0 | 16.5 | 16.5 | 23.7 | tight | fits | [Karte](https://www.openstreetmap.org/?mlat=53.677874&mlon=10.035990#map=18/53.677874/10.035990) | [Way](https://www.openstreetmap.org/way/4339201) |
| `seg_5a4f9205e401376b` | Hamburg-Nord | Am Schulwald | tertiary | 16 | 1.0 | 0.0 | 20.8 | 20.8 | 48.1 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.649806&mlon=10.025809#map=18/53.649806/10.025809) | [Way](https://www.openstreetmap.org/way/27217205) |
| `seg_6037ec807e38fc1e` | Hamburg-Nord | Husumer Straße | residential | 86 | 4.0 | 2.0 | 17.0 | 17.0 | 25.6 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.586805&mlon=9.978740#map=18/53.586805/9.978740) | [Way](https://www.openstreetmap.org/way/5229056) |
| `seg_ce1e34eab5f15ff9` | Hamburg-Nord | Biedermannplatz | secondary | 49 | 2.0 | 0.0 | 22.8 | 22.8 | 33.7 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.581917&mlon=10.032758#map=18/53.581917/10.032758) | [Way](https://www.openstreetmap.org/way/53207254) |
| `seg_f684a9657aacf796` | Hamburg-Nord | Sperlingweg | track | 133 | 7.0 | 0.0 | – | – | 34.9 | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.613888&mlon=9.967951#map=18/53.613888/9.967951) | [Way](https://www.openstreetmap.org/way/1283331826) |
| `seg_0a1aee1745190a87` | Harburg | Marmstorfer Schützenweg | living_street | 15 | 1.0 | 0.0 | 8.2 | 9.1 | 18.8 | does_not_fit | does_not_fit | [Karte](https://www.openstreetmap.org/?mlat=53.434846&mlon=9.970139#map=18/53.434846/9.970139) | [Way](https://www.openstreetmap.org/way/893156160) |
| `seg_3e6907faa3bbdc4b` | Harburg | Lorenz-von-Ehren-Weg | track | 395 | 20.0 | 0.0 | – | – | – | nan | nan | [Karte](https://www.openstreetmap.org/?mlat=53.432430&mlon=9.917560#map=18/53.432430/9.917560) | [Way](https://www.openstreetmap.org/way/900889335) |
| `seg_b2737ecffbf1238b` | Harburg | Dradenauer Deichweg | secondary | 35 | 2.0 | 0.0 | 13.3 | 13.3 | – | does_not_fit | fits | [Karte](https://www.openstreetmap.org/?mlat=53.515172&mlon=9.896514#map=18/53.515172/9.896514) | [Way](https://www.openstreetmap.org/way/340295899) |
| `seg_3cd4166bef71ff70` | Wandsbek | Helmut-Steidl-Platz | pedestrian | 32 | 2.0 | 0.0 | 34.4 | 34.4 | 34.3 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.604519&mlon=10.154917#map=18/53.604519/10.154917) | [Way](https://www.openstreetmap.org/way/10630855) |
| `seg_75f47c8b84607bca` | Wandsbek | Farmsener Landstraße | secondary | 22 | 1.0 | 0.0 | 17.0 | 17.0 | 40.6 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.650162&mlon=10.161503#map=18/53.650162/10.161503) | [Way](https://www.openstreetmap.org/way/550871424) |
| `seg_99601bd306a75add` | Wandsbek | Nordlandweg | tertiary | 157 | 8.0 | 6.0 | 17.0 | 17.0 | 29.8 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.627439&mlon=10.163299#map=18/53.627439/10.163299) | [Way](https://www.openstreetmap.org/way/4265354) |
| `seg_b4dd5703096504be` | Wandsbek | Falkenhorst | residential | 72 | 4.0 | 2.0 | 7.9 | 7.9 | 21.9 | does_not_fit | does_not_fit | [Karte](https://www.openstreetmap.org/?mlat=53.625645&mlon=10.128023#map=18/53.625645/10.128023) | [Way](https://www.openstreetmap.org/way/18490229) |
| `seg_c342eec71151ce48` | Wandsbek | August-Krogmann-Straße | secondary | 77 | 4.0 | 2.0 | 24.6 | 24.6 | 35.7 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.617401&mlon=10.113166#map=18/53.617401/10.113166) | [Way](https://www.openstreetmap.org/way/816627212) |
| `seg_c76090a05eee85f2` | Wandsbek | Stadtbahnstraße | primary | 58 | 3.0 | 0.0 | 24.4 | 24.5 | 26.9 | fits | fits | [Karte](https://www.openstreetmap.org/?mlat=53.653563&mlon=10.106468#map=18/53.653563/10.106468) | [Way](https://www.openstreetmap.org/way/464187409) |

## Lizenz

ALKIS (tatsächliche Nutzung, Gebäude): Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV), dl-de/by-2.0. Abschnitte und Brücken/Tunnel aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0.
