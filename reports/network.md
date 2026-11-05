# Netzbericht – Abschnitte (Stufe 2)

Erzeugt: 2026-11-04T21:29:22+00:00 von `pipeline/s02_network.py`. Nicht amtlicher Entwurf.

## Eingabe

- OSM-Auszug: `data/raw/osm/hamburg_2026-10-28.osm.pbf` (Abruf 2026-10-28, SHA-256 `700d2e2603a7ffb5…`)
- Regelwerk: config/rules.yaml 0.13.0
- highway-Klassen: motorway, motorway_link, trunk, trunk_link, primary, primary_link, secondary, secondary_link, tertiary, tertiary_link, unclassified, residential, living_street, pedestrian, service, track
- Netz für ganz Hamburg berechnet, damit IDs nicht vom Zuschnitt des Arbeitsgebiets abhängen.
- Bezirk je Abschnitt: Bezirk mit dem größten Längenanteil; Neuwerk/Scharhörn und Flächen außerhalb Hamburgs bleiben ohne Bezirk (config/project.yaml, area).

## Segmentierungsregeln

- **S-NET-01** (assumption, draft): Abschnittsende an jedem Knoten mit Grad != 2 (Kreuzung, Einmündung, Sackgassenende)
- **S-NET-02** (assumption, draft): Abschnittsende an Knoten mit Grad 2, an denen sich die highway-Klasse ändert
- **S-NET-03** (assumption, draft): Abschnitte länger als min_length_m an Knoten teilen, an denen sich maxspeed ändert (nur Wechsel zwischen zwei bekannten Werten); min_length_m = 400 m (assumption)
- **S-NET-04** (assumption, draft): Benannte Zufahrten zusätzlich ins Netz: highway=service ohne service-Untertyp oder mit service=alley und highway=track mit Kfz-Zugang (erster bekannter Wert aus motor_access_keys in motor_access_values oder ohne Angabe); jeweils nur mit name. Fußwege, path, Parkplatzgassen und Grundstückszufahrten bleiben draußen.

segment_id = Hash aus sortierten OSM-Way-IDs und den auf 1 m gerundeten Koordinaten der beiden Endknoten (EPSG:25832). Haben zwei Abschnitte dieselben Ways und Endknoten (z. B. die Bögen eines Kreisverkehrs aus einem geschlossenen Way), gehen zusätzlich alle Knotenkoordinaten in den Hash ein.

## Kennzahlen

- Kanten (Knoten zu Knoten) im Ausgangsnetz: 228 005 aus 42 001 Ways
- Abschnitte Hamburg: 36 526 (4 997.7 km)
- Abschnitte in Hamburg (7 Bezirke): 35 280 (4 750.7 km)
- Abschnitte im Arbeitsgebiet (Hamburg (7 Bezirke) + 500 m): 34 999
- Abschnitte aus Teilung nach S-NET-03: 461 (davon Hamburg (7 Bezirke): 420)
- Abschnitte ohne Bezirk (außerhalb Hamburgs, Randstreifen des OSM-Auszugs, Neuwerk; nur für den Netzzusammenhang): 1 246
- Abschnitte ohne OSM-maxspeed: 6 843; mit mehreren maxspeed-Werten: 426

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| Längensumme vs. OSM-Ausgangsnetz | ok | 4997.7 km vs. 4997.0 km, Abweichung 0.0127% (Grenze 1%) |
| Keine doppelten segment_id | ok | 0 doppelt |
| Geometrien gültig | ok | 0 ungültig |
| Länge > 0 | ok | 0 mit Länge 0 |
| CRS EPSG:25832 | ok | EPSG:25832 |
| IDs identisch mit Vorlauf | ok | 36526 gleich, 0 neu, 0 entfallen |

## Längenverteilung je highway-Klasse – Hamburg (7 Bezirke)

| highway | Anzahl | Summe km | P10 m | Median m | P90 m | Max m |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| motorway | 177 | 177.1 | 184 | 618 | 2 093 | 4 780 |
| motorway_link | 368 | 58.0 | 16 | 74 | 347 | 1 347 |
| trunk | 81 | 44.7 | 54 | 433 | 1 421 | 2 638 |
| trunk_link | 128 | 16.3 | 16 | 51 | 306 | 519 |
| primary | 2 767 | 291.7 | 12 | 64 | 241 | 3 488 |
| primary_link | 105 | 5.5 | 10 | 33 | 99 | 530 |
| secondary | 3 985 | 452.2 | 12 | 64 | 260 | 2 054 |
| secondary_link | 201 | 8.0 | 11 | 34 | 81 | 216 |
| tertiary | 4 491 | 574.4 | 13 | 75 | 261 | 3 073 |
| tertiary_link | 121 | 4.6 | 13 | 34 | 67 | 128 |
| unclassified | 1 638 | 295.1 | 15 | 83 | 462 | 2 855 |
| residential | 17 493 | 2 394.5 | 27 | 102 | 280 | 2 500 |
| living_street | 1 658 | 134.6 | 16 | 60 | 175 | 1 155 |
| pedestrian | 703 | 31.1 | 7 | 30 | 98 | 330 |
| service | 886 | 131.1 | 20 | 80 | 283 | 6 328 |
| track | 478 | 131.7 | 33 | 168 | 631 | 2 954 |
| **gesamt** | 35 280 | 4 750.7 | 17 | 86 | 281 | 6 328 |

## Längenverteilung je highway-Klasse – gesamter OSM-Auszug

| highway | Anzahl | Summe km | P10 m | Median m | P90 m | Max m |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| motorway | 183 | 180.7 | 182 | 634 | 2 085 | 4 780 |
| motorway_link | 372 | 59.6 | 16 | 77 | 348 | 1 347 |
| trunk | 83 | 45.2 | 54 | 396 | 1 419 | 2 638 |
| trunk_link | 132 | 16.8 | 14 | 51 | 313 | 519 |
| primary | 2 804 | 296.1 | 12 | 64 | 241 | 3 488 |
| primary_link | 108 | 5.6 | 10 | 33 | 98 | 530 |
| secondary | 4 072 | 466.4 | 12 | 64 | 263 | 2 054 |
| secondary_link | 206 | 8.2 | 11 | 34 | 80 | 216 |
| tertiary | 4 683 | 613.8 | 13 | 76 | 269 | 3 073 |
| tertiary_link | 122 | 4.7 | 13 | 34 | 67 | 128 |
| unclassified | 1 733 | 334.1 | 16 | 89 | 511 | 2 855 |
| residential | 18 141 | 2 502.2 | 28 | 103 | 284 | 2 500 |
| living_street | 1 736 | 142.2 | 16 | 60 | 178 | 1 155 |
| pedestrian | 706 | 31.3 | 7 | 30 | 98 | 330 |
| service | 930 | 136.6 | 20 | 80 | 284 | 6 328 |
| track | 515 | 154.2 | 34 | 172 | 733 | 3 635 |
| **gesamt** | 36 526 | 4 997.7 | 17 | 87 | 286 | 6 328 |

## Abschnitte je Bezirk

| Bezirk | Anzahl | km |
| --- | ---: | ---: |
| Altona | 4 887 | 621.1 |
| Bergedorf | 3 063 | 544.0 |
| Eimsbüttel | 4 010 | 480.1 |
| Hamburg-Mitte | 6 848 | 893.0 |
| Hamburg-Nord | 5 136 | 563.3 |
| Harburg | 3 790 | 611.2 |
| Wandsbek | 7 546 | 1 037.9 |
| ohne Bezirk (außerhalb Hamburgs, Neuwerk) | 1 246 | 247.0 |

## Stichprobe (30 zufällige Abschnitte in Hamburg (7 Bezirke), nach Bezirk geschichtet, Seed 42)

Links auf openstreetmap.org (Way und Kartenausschnitt am Abschnittsmittelpunkt). Orthophoto- und Panoramax-Links folgen, sobald das Linkformat geklärt ist (docs/open_questions.md).

| segment_id | Bezirk | highway | Name | Länge m | maxspeed (OSM) | Ways | Karte |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| `seg_0b429570fa26ebba` | Altona | secondary | Blankeneser Landstraße | 171 | 50 | [4347380](https://www.openstreetmap.org/way/4347380), [1085324056](https://www.openstreetmap.org/way/1085324056) | [OSM](https://www.openstreetmap.org/?mlat=53.565854&mlon=9.799288#map=18/53.565854/9.799288) |
| `seg_30696dcbf7bc7a04` | Altona | primary | Stresemannstraße | 55 | 50 | [936598996](https://www.openstreetmap.org/way/936598996), [936599010](https://www.openstreetmap.org/way/936599010), [1071071905](https://www.openstreetmap.org/way/1071071905) | [OSM](https://www.openstreetmap.org/?mlat=53.563539&mlon=9.941936#map=18/53.563539/9.941936) |
| `seg_69ef3a0b69aab218` | Altona | residential | Augustenpassage | 187 | 30 | [618750343](https://www.openstreetmap.org/way/618750343), [139172720](https://www.openstreetmap.org/way/139172720), [618750342](https://www.openstreetmap.org/way/618750342) (+2) | [OSM](https://www.openstreetmap.org/?mlat=53.559088&mlon=9.965603#map=18/53.559088/9.965603) |
| `seg_76cb381fe708c1fa` | Altona | unclassified | Babenwischenweg | 215 | – | [139864005](https://www.openstreetmap.org/way/139864005) | [OSM](https://www.openstreetmap.org/?mlat=53.609687&mlon=9.763284#map=18/53.609687/9.763284) |
| `seg_3055a1151f286ebc` | Bergedorf | service | Marie-Henning-Weg | 38 | – | [374350909](https://www.openstreetmap.org/way/374350909) | [OSM](https://www.openstreetmap.org/?mlat=53.482009&mlon=10.155254#map=18/53.482009/10.155254) |
| `seg_4b548c3d7e1cb258` | Bergedorf | primary | Bergedorfer Straße | 14 | 70 | [40158675](https://www.openstreetmap.org/way/40158675) | [OSM](https://www.openstreetmap.org/?mlat=53.520161&mlon=10.151516#map=18/53.520161/10.151516) |
| `seg_fad06e039233b2f9` | Bergedorf | living_street | Bockhorster Höhe | 59 | – | [25753638](https://www.openstreetmap.org/way/25753638) | [OSM](https://www.openstreetmap.org/?mlat=53.515690&mlon=10.172691#map=18/53.515690/10.172691) |
| `seg_1abf10d7274d8422` | Eimsbüttel | residential | Rahweg | 324 | 30 | [148170157](https://www.openstreetmap.org/way/148170157), [1459903219](https://www.openstreetmap.org/way/1459903219) | [OSM](https://www.openstreetmap.org/?mlat=53.641256&mlon=9.977482#map=18/53.641256/9.977482) |
| `seg_b112936ec884f5d8` | Eimsbüttel | tertiary |  | 11 | 50 | [59557227](https://www.openstreetmap.org/way/59557227), [1511356916](https://www.openstreetmap.org/way/1511356916) | [OSM](https://www.openstreetmap.org/?mlat=53.582256&mlon=9.947678#map=18/53.582256/9.947678) |
| `seg_c28aa1753bd31112` | Eimsbüttel | primary_link |  | 88 | 50 | [692691300](https://www.openstreetmap.org/way/692691300) | [OSM](https://www.openstreetmap.org/?mlat=53.592565&mlon=9.928214#map=18/53.592565/9.928214) |
| `seg_e932efaa0fc40339` | Eimsbüttel | residential | Fuhlsbütteler Weg | 254 | 30 | [8470233](https://www.openstreetmap.org/way/8470233), [125603392](https://www.openstreetmap.org/way/125603392) | [OSM](https://www.openstreetmap.org/?mlat=53.623607&mlon=9.956940#map=18/53.623607/9.956940) |
| `seg_09aed50abf56bb66` | Hamburg-Mitte | living_street | Billstieg | 157 | – | [25581052](https://www.openstreetmap.org/way/25581052) | [OSM](https://www.openstreetmap.org/?mlat=53.534394&mlon=10.110004#map=18/53.534394/10.110004) |
| `seg_196a081a2cbb22e9` | Hamburg-Mitte | unclassified | Eversween | 12 | 50 | [408046751](https://www.openstreetmap.org/way/408046751) | [OSM](https://www.openstreetmap.org/?mlat=53.480681&mlon=9.980563#map=18/53.480681/9.980563) |
| `seg_7fc697e24a3a259c` | Hamburg-Mitte | residential | Schiffbeker Weg | 15 | 30 | [151362244](https://www.openstreetmap.org/way/151362244) | [OSM](https://www.openstreetmap.org/?mlat=53.555131&mlon=10.113725#map=18/53.555131/10.113725) |
| `seg_a606d8a75b4ad901` | Hamburg-Mitte | living_street |  | 78 | walk | [965138690](https://www.openstreetmap.org/way/965138690) | [OSM](https://www.openstreetmap.org/?mlat=53.542381&mlon=9.844991#map=18/53.542381/9.844991) |
| `seg_b3783719c59d5712` | Hamburg-Mitte | residential | Kentzlerdamm / Rumpffsweg | 307 | 30 | [25592021](https://www.openstreetmap.org/way/25592021), [40246686](https://www.openstreetmap.org/way/40246686), [25592019](https://www.openstreetmap.org/way/25592019) (+1) | [OSM](https://www.openstreetmap.org/?mlat=53.554402&mlon=10.054247#map=18/53.554402/10.054247) |
| `seg_0be0b44008702754` | Hamburg-Nord | primary | Sechslingspforte | 31 | 50 | [1266104813](https://www.openstreetmap.org/way/1266104813) | [OSM](https://www.openstreetmap.org/?mlat=53.562812&mlon=10.015436#map=18/53.562812/10.015436) |
| `seg_25faecf475c757b5` | Hamburg-Nord | residential | Wakendorfer Weg | 66 | 30 | [4339201](https://www.openstreetmap.org/way/4339201) | [OSM](https://www.openstreetmap.org/?mlat=53.677874&mlon=10.035990#map=18/53.677874/10.035990) |
| `seg_5a4f9205e401376b` | Hamburg-Nord | tertiary | Am Schulwald | 16 | 50 | [27217205](https://www.openstreetmap.org/way/27217205) | [OSM](https://www.openstreetmap.org/?mlat=53.649806&mlon=10.025809#map=18/53.649806/10.025809) |
| `seg_6037ec807e38fc1e` | Hamburg-Nord | residential | Husumer Straße | 86 | 30 | [5229056](https://www.openstreetmap.org/way/5229056) | [OSM](https://www.openstreetmap.org/?mlat=53.586805&mlon=9.978740#map=18/53.586805/9.978740) |
| `seg_09a6be0f29a3e434` | Harburg | track | Hellkuhle | 660 | – | [4231690](https://www.openstreetmap.org/way/4231690) | [OSM](https://www.openstreetmap.org/?mlat=53.457406&mlon=9.925473#map=18/53.457406/9.925473) |
| `seg_8ddf141592f67370` | Harburg | tertiary_link | Finkenwerder Straße | 36 | 50 | [210978344](https://www.openstreetmap.org/way/210978344) | [OSM](https://www.openstreetmap.org/?mlat=53.517972&mlon=9.885548#map=18/53.517972/9.885548) |
| `seg_9da4d1abecc497a1` | Harburg | residential | Baererstraße | 7 | 30 | [1276575946](https://www.openstreetmap.org/way/1276575946) | [OSM](https://www.openstreetmap.org/?mlat=53.453609&mlon=9.986445#map=18/53.453609/9.986445) |
| `seg_a9654d6711ba142e` | Harburg | residential | Neuländer Kamp | 94 | 50 | [1319225471](https://www.openstreetmap.org/way/1319225471) | [OSM](https://www.openstreetmap.org/?mlat=53.460083&mlon=10.001861#map=18/53.460083/10.001861) |
| `seg_36c54a4a192e62a2` | Wandsbek | residential | Raamfeld | 77 | 30 | [1416043367](https://www.openstreetmap.org/way/1416043367) | [OSM](https://www.openstreetmap.org/?mlat=53.690418&mlon=10.090378#map=18/53.690418/10.090378) |
| `seg_75edd7ff12990b89` | Wandsbek | residential | Hinsbleek | 284 | 30 | [536409894](https://www.openstreetmap.org/way/536409894), [536409888](https://www.openstreetmap.org/way/536409888), [150741147](https://www.openstreetmap.org/way/150741147) | [OSM](https://www.openstreetmap.org/?mlat=53.652279&mlon=10.079342#map=18/53.652279/10.079342) |
| `seg_995f22efab2f65a7` | Wandsbek | residential | Otto-Burrmeister-Ring | 12 | 30 | [3374402](https://www.openstreetmap.org/way/3374402) | [OSM](https://www.openstreetmap.org/?mlat=53.617542&mlon=10.069078#map=18/53.617542/10.069078) |
| `seg_b4d2497aceaa106e` | Wandsbek | residential | Zuschlagkoppel | 262 | 30 | [7996499](https://www.openstreetmap.org/way/7996499) | [OSM](https://www.openstreetmap.org/?mlat=53.640807&mlon=10.177401#map=18/53.640807/10.177401) |
| `seg_c330e5f079de24f9` | Wandsbek | secondary | Halenreie | 176 | 50 | [31061305](https://www.openstreetmap.org/way/31061305), [550871427](https://www.openstreetmap.org/way/550871427) | [OSM](https://www.openstreetmap.org/?mlat=53.651382&mlon=10.161517#map=18/53.651382/10.161517) |
| `seg_c742220b5e1602bd` | Wandsbek | residential | Gropiusring | 493 | 30 | [817199725](https://www.openstreetmap.org/way/817199725), [539241969](https://www.openstreetmap.org/way/539241969), [1162634972](https://www.openstreetmap.org/way/1162634972) | [OSM](https://www.openstreetmap.org/?mlat=53.611934&mlon=10.055166#map=18/53.611934/10.055166) |

## Lizenz

Abgeleitet aus OpenStreetMap-Daten © OpenStreetMap-Beitragende, ODbL 1.0 (docs/licenses.md).
