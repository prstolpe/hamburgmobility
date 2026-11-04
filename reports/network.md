# Netzbericht – Abschnitte (Stufe 2)

Erzeugt: 2026-11-04T20:32:13+00:00 von `pipeline/s02_network.py`. Nicht amtlicher Entwurf.

## Eingabe

- OSM-Auszug: `data/raw/osm/hamburg_2026-10-28.osm.pbf` (Abruf 2026-10-28, SHA-256 `700d2e2603a7ffb5…`)
- Regelwerk: config/rules.yaml 0.11.0
- highway-Klassen: motorway, motorway_link, trunk, trunk_link, primary, primary_link, secondary, secondary_link, tertiary, tertiary_link, unclassified, residential, living_street, pedestrian, service, track
- Netz für ganz Hamburg berechnet, damit IDs am Rand des Pilotbezirks nicht vom Zuschnitt abhängen.

## Segmentierungsregeln

- **S-NET-01** (assumption, draft): Abschnittsende an jedem Knoten mit Grad != 2 (Kreuzung, Einmündung, Sackgassenende)
- **S-NET-02** (assumption, draft): Abschnittsende an Knoten mit Grad 2, an denen sich die highway-Klasse ändert
- **S-NET-03** (assumption, draft): Abschnitte länger als min_length_m an Knoten teilen, an denen sich maxspeed ändert (nur Wechsel zwischen zwei bekannten Werten); min_length_m = 400 m (assumption)
- **S-NET-04** (assumption, draft): Benannte Zufahrten zusätzlich ins Netz: highway=service ohne service-Untertyp oder mit service=alley und highway=track mit Kfz-Zugang (erster bekannter Wert aus motor_access_keys in motor_access_values oder ohne Angabe); jeweils nur mit name. Fußwege, path, Parkplatzgassen und Grundstückszufahrten bleiben draußen.

segment_id = Hash aus sortierten OSM-Way-IDs und den auf 1 m gerundeten Koordinaten der beiden Endknoten (EPSG:25832). Haben zwei Abschnitte dieselben Ways und Endknoten (z. B. die Bögen eines Kreisverkehrs aus einem geschlossenen Way), gehen zusätzlich alle Knotenkoordinaten in den Hash ein.

## Kennzahlen

- Kanten (Knoten zu Knoten) im Ausgangsnetz: 228 005 aus 42 001 Ways
- Abschnitte Hamburg: 36 526 (4 997.7 km)
- Abschnitte Eimsbüttel: 4 010 (480.1 km)
- Abschnitte im Arbeitsgebiet (Eimsbüttel + 500 m): 5 127
- Abschnitte aus Teilung nach S-NET-03: 461 (davon Eimsbüttel: 32)
- Abschnitte ohne Bezirk (außerhalb Hamburgs, Randstreifen des OSM-Auszugs; nur für den Netzzusammenhang): 1 240
- Abschnitte ohne OSM-maxspeed: 6 843; mit mehreren maxspeed-Werten: 426

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| Längensumme vs. OSM-Ausgangsnetz | ok | 4997.7 km vs. 4997.0 km, Abweichung 0.0127% (Grenze 1%) |
| Keine doppelten segment_id | ok | 0 doppelt |
| Geometrien gültig | ok | 0 ungültig |
| Länge > 0 | ok | 0 mit Länge 0 |
| CRS EPSG:25832 | ok | EPSG:25832 |
| IDs identisch mit Vorlauf | **FEHLER** | 34000 gleich, 2526 neu, 502 entfallen |

## Längenverteilung je highway-Klasse – Eimsbüttel

| highway | Anzahl | Summe km | P10 m | Median m | P90 m | Max m |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| motorway | 30 | 23.4 | 211 | 618 | 1 722 | 2 179 |
| motorway_link | 72 | 8.8 | 17 | 51 | 301 | 601 |
| trunk | 1 | 0.0 | 33 | 33 | 33 | 33 |
| primary | 567 | 58.3 | 13 | 59 | 238 | 1 730 |
| primary_link | 29 | 0.9 | 9 | 27 | 47 | 119 |
| secondary | 337 | 26.2 | 10 | 41 | 180 | 726 |
| secondary_link | 21 | 1.0 | 22 | 45 | 71 | 86 |
| tertiary | 537 | 51.7 | 11 | 71 | 217 | 1 384 |
| tertiary_link | 9 | 0.4 | 12 | 38 | 67 | 77 |
| unclassified | 95 | 12.5 | 12 | 71 | 332 | 1 345 |
| residential | 2 039 | 274.3 | 30 | 110 | 275 | 993 |
| living_street | 117 | 10.6 | 23 | 65 | 188 | 265 |
| pedestrian | 86 | 3.1 | 7 | 25 | 77 | 169 |
| service | 56 | 5.5 | 12 | 75 | 222 | 474 |
| track | 14 | 3.5 | 76 | 198 | 464 | 619 |
| **gesamt** | 4 010 | 480.1 | 16 | 85 | 259 | 2 179 |

## Längenverteilung je highway-Klasse – Hamburg

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
| (außerhalb Hamburgs) | 1 240 | 241.8 |
| Altona | 4 887 | 621.1 |
| Bergedorf | 3 063 | 544.0 |
| Eimsbüttel | 4 010 | 480.1 |
| Hamburg-Mitte | 6 854 | 898.2 |
| Hamburg-Nord | 5 136 | 563.3 |
| Harburg | 3 790 | 611.2 |
| Wandsbek | 7 546 | 1 037.9 |

## Stichprobe (30 zufällige Abschnitte in Eimsbüttel, Seed 42)

Links auf openstreetmap.org (Way und Kartenausschnitt am Abschnittsmittelpunkt). Orthophoto- und Panoramax-Links folgen, sobald das Linkformat geklärt ist (docs/open_questions.md).

| segment_id | highway | Name | Länge m | maxspeed (OSM) | Ways | Karte |
| --- | --- | --- | ---: | --- | --- | --- |
| `seg_06c51c323ecec35f` | residential | Sachsenweg | 136 | 30 | [1018232732](https://www.openstreetmap.org/way/1018232732) | [OSM](https://www.openstreetmap.org/?mlat=53.643495&mlon=9.960601#map=18/53.643495/9.960601) |
| `seg_0796a6ac6a25cf94` | tertiary | Bogenstraße | 10 | 50 | [238921530](https://www.openstreetmap.org/way/238921530) | [OSM](https://www.openstreetmap.org/?mlat=53.571076&mlon=9.978445#map=18/53.571076/9.978445) |
| `seg_085fcf760eb5e9c1` | tertiary | Lohkampstraße | 137 | 50 | [4919897](https://www.openstreetmap.org/way/4919897) | [OSM](https://www.openstreetmap.org/?mlat=53.615241&mlon=9.877703#map=18/53.615241/9.877703) |
| `seg_0906305a37756fb1` | tertiary | Krähenweg | 36 | 50 | [1165983748](https://www.openstreetmap.org/way/1165983748) | [OSM](https://www.openstreetmap.org/?mlat=53.633004&mlon=9.954534#map=18/53.633004/9.954534) |
| `seg_16df18fb7177523d` | residential | Alte Rabenstraße | 82 | 30 | [16232763](https://www.openstreetmap.org/way/16232763), [984956917](https://www.openstreetmap.org/way/984956917) | [OSM](https://www.openstreetmap.org/?mlat=53.567259&mlon=10.000605#map=18/53.567259/10.000605) |
| `seg_1885bcb6c1f638e2` | service | Heketweg | 212 | – | [186967128](https://www.openstreetmap.org/way/186967128), [23840069](https://www.openstreetmap.org/way/23840069) | [OSM](https://www.openstreetmap.org/?mlat=53.650543&mlon=9.908991#map=18/53.650543/9.908991) |
| `seg_1abf10d7274d8422` | residential | Rahweg | 324 | 30 | [148170157](https://www.openstreetmap.org/way/148170157), [1459903219](https://www.openstreetmap.org/way/1459903219) | [OSM](https://www.openstreetmap.org/?mlat=53.641256&mlon=9.977482#map=18/53.641256/9.977482) |
| `seg_1d3b3fe24c77d387` | tertiary | Lappenbergsallee | 14 | 50 | [695925121](https://www.openstreetmap.org/way/695925121) | [OSM](https://www.openstreetmap.org/?mlat=53.573393&mlon=9.948760#map=18/53.573393/9.948760) |
| `seg_2520202b82b96419` | residential | Alsterufer | 22 | 50 | [1345098540](https://www.openstreetmap.org/way/1345098540), [1073054122](https://www.openstreetmap.org/way/1073054122) | [OSM](https://www.openstreetmap.org/?mlat=53.558896&mlon=9.993841#map=18/53.558896/9.993841) |
| `seg_33c01a47652cf1df` | tertiary | Bogenstraße | 14 | 50 | [136712391](https://www.openstreetmap.org/way/136712391) | [OSM](https://www.openstreetmap.org/?mlat=53.571012&mlon=9.978584#map=18/53.571012/9.978584) |
| `seg_3882e28e339b36bf` | residential | Spengelweg / Rellinger Straße | 224 | 30 | [23100115](https://www.openstreetmap.org/way/23100115), [239962438](https://www.openstreetmap.org/way/239962438), [28313036](https://www.openstreetmap.org/way/28313036) (+1) | [OSM](https://www.openstreetmap.org/?mlat=53.573663&mlon=9.943104#map=18/53.573663/9.943104) |
| `seg_3a33dc270eaaf8ed` | residential | Jungfrauenthal | 32 | – | [136965459](https://www.openstreetmap.org/way/136965459) | [OSM](https://www.openstreetmap.org/?mlat=53.581471&mlon=9.987730#map=18/53.581471/9.987730) |
| `seg_3be5306ed98e0a7f` | residential | Frohbösestraße | 240 | 30 | [368064190](https://www.openstreetmap.org/way/368064190), [145693805](https://www.openstreetmap.org/way/145693805) | [OSM](https://www.openstreetmap.org/?mlat=53.573857&mlon=9.938727#map=18/53.573857/9.938727) |
| `seg_3f91506d8d854af2` | primary | Schleswiger Damm | 60 | 50 | [23299739](https://www.openstreetmap.org/way/23299739) | [OSM](https://www.openstreetmap.org/?mlat=53.632824&mlon=9.925596#map=18/53.632824/9.925596) |
| `seg_47cd5b763bcfa29e` | tertiary | Hagenbeckstraße | 22 | 50 | [1561196248](https://www.openstreetmap.org/way/1561196248) | [OSM](https://www.openstreetmap.org/?mlat=53.583284&mlon=9.947488#map=18/53.583284/9.947488) |
| `seg_6d0e0b2329b1d570` | residential | Bismarckstraße | 79 | 30 | [137247324](https://www.openstreetmap.org/way/137247324) | [OSM](https://www.openstreetmap.org/?mlat=53.578374&mlon=9.973497#map=18/53.578374/9.973497) |
| `seg_84b63f5668d782a0` | residential | Hollwören | 9 | 30 | [8385642](https://www.openstreetmap.org/way/8385642) | [OSM](https://www.openstreetmap.org/?mlat=53.619192&mlon=9.942506#map=18/53.619192/9.942506) |
| `seg_8f3580d1090efd3c` | residential | Bruktererweg | 64 | 30 | [25076220](https://www.openstreetmap.org/way/25076220) | [OSM](https://www.openstreetmap.org/?mlat=53.647150&mlon=9.955036#map=18/53.647150/9.955036) |
| `seg_9360c0070d5d8fc8` | tertiary | Grindelhof | 16 | 30 | [136915268](https://www.openstreetmap.org/way/136915268) | [OSM](https://www.openstreetmap.org/?mlat=53.567884&mlon=9.982048#map=18/53.567884/9.982048) |
| `seg_9bb1cf3412c19733` | unclassified | Modering | 259 | 50 | [10223274](https://www.openstreetmap.org/way/10223274) | [OSM](https://www.openstreetmap.org/?mlat=53.637367&mlon=9.922109#map=18/53.637367/9.922109) |
| `seg_9e5767e0c7ad02d8` | primary | Kieler Straße | 215 | 50 | [1352770748](https://www.openstreetmap.org/way/1352770748), [1352769095](https://www.openstreetmap.org/way/1352769095), [145693831](https://www.openstreetmap.org/way/145693831) (+1) | [OSM](https://www.openstreetmap.org/?mlat=53.575102&mlon=9.939301#map=18/53.575102/9.939301) |
| `seg_a830200978b8de3c` | living_street | Assorweg | 17 | – | [57841656](https://www.openstreetmap.org/way/57841656) | [OSM](https://www.openstreetmap.org/?mlat=53.632276&mlon=9.898395#map=18/53.632276/9.898395) |
| `seg_aa9749a5add7c059` | primary | Niendorfer Marktplatz | 65 | 50 | [30339585](https://www.openstreetmap.org/way/30339585), [1561698175](https://www.openstreetmap.org/way/1561698175) | [OSM](https://www.openstreetmap.org/?mlat=53.618125&mlon=9.949407#map=18/53.618125/9.949407) |
| `seg_b112936ec884f5d8` | tertiary |  | 11 | 50 | [59557227](https://www.openstreetmap.org/way/59557227), [1511356916](https://www.openstreetmap.org/way/1511356916) | [OSM](https://www.openstreetmap.org/?mlat=53.582256&mlon=9.947678#map=18/53.582256/9.947678) |
| `seg_b84ce5c2151c69de` | secondary | Beim Schlump | 28 | 50 | [52092679](https://www.openstreetmap.org/way/52092679), [220112336](https://www.openstreetmap.org/way/220112336) | [OSM](https://www.openstreetmap.org/?mlat=53.567576&mlon=9.970552#map=18/53.567576/9.970552) |
| `seg_bc13ad58ca792ef8` | residential | Feldrosenweg | 211 | 30 | [4920036](https://www.openstreetmap.org/way/4920036) | [OSM](https://www.openstreetmap.org/?mlat=53.612080&mlon=9.885824#map=18/53.612080/9.885824) |
| `seg_c1c808ce9df1c275` | residential | Böttgerstraße | 172 | 30 | [4048171](https://www.openstreetmap.org/way/4048171) | [OSM](https://www.openstreetmap.org/?mlat=53.568747&mlon=9.996735#map=18/53.568747/9.996735) |
| `seg_c28aa1753bd31112` | primary_link |  | 88 | 50 | [692691300](https://www.openstreetmap.org/way/692691300) | [OSM](https://www.openstreetmap.org/?mlat=53.592565&mlon=9.928214#map=18/53.592565/9.928214) |
| `seg_c2fb646f49fcf631` | residential | Teutonenweg | 301 | 30 | [329802783](https://www.openstreetmap.org/way/329802783), [4860840](https://www.openstreetmap.org/way/4860840) | [OSM](https://www.openstreetmap.org/?mlat=53.634120&mlon=9.970232#map=18/53.634120/9.970232) |
| `seg_e932efaa0fc40339` | residential | Fuhlsbütteler Weg | 254 | 30 | [8470233](https://www.openstreetmap.org/way/8470233), [125603392](https://www.openstreetmap.org/way/125603392) | [OSM](https://www.openstreetmap.org/?mlat=53.623607&mlon=9.956940#map=18/53.623607/9.956940) |

## Lizenz

Abgeleitet aus OpenStreetMap-Daten © OpenStreetMap-Beitragende, ODbL 1.0 (docs/licenses.md).
