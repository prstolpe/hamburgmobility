# Netzbericht – Abschnitte (Stufe 2)

Erzeugt: 2026-10-28T10:02:04+00:00 von `pipeline/s02_network.py`. Nicht amtlicher Entwurf.

## Eingabe

- OSM-Auszug: `data/raw/osm/hamburg_2026-10-28.osm.pbf` (Abruf 2026-10-28, SHA-256 `700d2e2603a7ffb5…`)
- Regelwerk: config/rules.yaml 0.2.0
- highway-Klassen: motorway, motorway_link, trunk, trunk_link, primary, primary_link, secondary, secondary_link, tertiary, tertiary_link, unclassified, residential, living_street, pedestrian
- Netz für ganz Hamburg berechnet, damit IDs am Rand des Pilotbezirks nicht vom Zuschnitt abhängen.

## Segmentierungsregeln

- **S-NET-01** (assumption, draft): Abschnittsende an jedem Knoten mit Grad != 2 (Kreuzung, Einmündung, Sackgassenende)
- **S-NET-02** (assumption, draft): Abschnittsende an Knoten mit Grad 2, an denen sich die highway-Klasse ändert
- **S-NET-03** (assumption, draft): Abschnitte länger als min_length_m an Knoten teilen, an denen sich maxspeed ändert (nur Wechsel zwischen zwei bekannten Werten); min_length_m = 400 m (assumption)

segment_id = Hash aus sortierten OSM-Way-IDs und den auf 1 m gerundeten Koordinaten der beiden Endknoten (EPSG:25832). Haben zwei Abschnitte dieselben Ways und Endknoten (z. B. die Bögen eines Kreisverkehrs aus einem geschlossenen Way), gehen zusätzlich alle Knotenkoordinaten in den Hash ein.

## Kennzahlen

- Kanten (Knoten zu Knoten) im Ausgangsnetz: 218 356 aus 40 421 Ways
- Abschnitte Hamburg: 34 502 (4 706.8 km)
- Abschnitte Eimsbüttel: 3 882 (471.3 km)
- Abschnitte im Arbeitsgebiet (Eimsbüttel + 500 m): 4 964
- Abschnitte aus Teilung nach S-NET-03: 478 (davon Eimsbüttel: 32)
- Abschnitte ohne Bezirk (außerhalb Hamburgs, Randstreifen des OSM-Auszugs; nur für den Netzzusammenhang): 1 118
- Abschnitte ohne OSM-maxspeed: 5 710; mit mehreren maxspeed-Werten: 419

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| Längensumme vs. OSM-Ausgangsnetz | ok | 4706.8 km vs. 4706.2 km, Abweichung 0.0135% (Grenze 1%) |
| Keine doppelten segment_id | ok | 0 doppelt |
| Geometrien gültig | ok | 0 ungültig |
| Länge > 0 | ok | 0 mit Länge 0 |
| CRS EPSG:25832 | ok | EPSG:25832 |
| IDs identisch mit Vorlauf | ok | 34502 gleich, 0 neu, 0 entfallen |

## Längenverteilung je highway-Klasse – Eimsbüttel

| highway | Anzahl | Summe km | P10 m | Median m | P90 m | Max m |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| motorway | 30 | 23.4 | 211 | 618 | 1 722 | 2 179 |
| motorway_link | 72 | 8.8 | 17 | 51 | 301 | 601 |
| trunk | 1 | 0.0 | 33 | 33 | 33 | 33 |
| primary | 562 | 58.3 | 13 | 59 | 240 | 1 730 |
| primary_link | 28 | 0.9 | 10 | 28 | 47 | 119 |
| secondary | 328 | 26.2 | 10 | 42 | 183 | 726 |
| secondary_link | 21 | 1.0 | 22 | 45 | 71 | 86 |
| tertiary | 525 | 51.7 | 11 | 75 | 217 | 1 384 |
| tertiary_link | 9 | 0.4 | 12 | 38 | 67 | 77 |
| unclassified | 90 | 12.5 | 12 | 70 | 344 | 1 345 |
| residential | 2 013 | 274.4 | 30 | 111 | 280 | 993 |
| living_street | 117 | 10.6 | 23 | 65 | 188 | 265 |
| pedestrian | 86 | 3.1 | 7 | 25 | 77 | 169 |
| **gesamt** | 3 882 | 471.3 | 16 | 86 | 264 | 2 179 |

## Längenverteilung je highway-Klasse – Hamburg

| highway | Anzahl | Summe km | P10 m | Median m | P90 m | Max m |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| motorway | 183 | 180.7 | 182 | 634 | 2 085 | 4 780 |
| motorway_link | 372 | 59.6 | 16 | 77 | 348 | 1 347 |
| trunk | 83 | 45.2 | 54 | 396 | 1 419 | 2 638 |
| trunk_link | 131 | 16.8 | 14 | 51 | 314 | 519 |
| primary | 2 780 | 296.1 | 13 | 64 | 244 | 3 488 |
| primary_link | 107 | 5.6 | 10 | 33 | 99 | 530 |
| secondary | 4 014 | 466.4 | 12 | 64 | 266 | 2 278 |
| secondary_link | 206 | 8.2 | 11 | 34 | 80 | 216 |
| tertiary | 4 590 | 613.8 | 13 | 77 | 274 | 3 073 |
| tertiary_link | 122 | 4.7 | 13 | 34 | 67 | 128 |
| unclassified | 1 672 | 334.1 | 16 | 90 | 529 | 3 301 |
| residential | 17 814 | 2 502.2 | 28 | 104 | 290 | 2 500 |
| living_street | 1 724 | 142.2 | 17 | 61 | 179 | 1 155 |
| pedestrian | 704 | 31.3 | 7 | 30 | 99 | 330 |
| **gesamt** | 34 502 | 4 706.8 | 17 | 87 | 286 | 4 780 |

## Abschnitte je Bezirk

| Bezirk | Anzahl | km |
| --- | ---: | ---: |
| (außerhalb Hamburgs) | 1 118 | 212.4 |
| Altona | 4 606 | 578.0 |
| Bergedorf | 2 817 | 506.0 |
| Eimsbüttel | 3 882 | 471.3 |
| Hamburg-Mitte | 6 481 | 855.6 |
| Hamburg-Nord | 4 854 | 541.1 |
| Harburg | 3 485 | 550.7 |
| Wandsbek | 7 259 | 991.7 |

## Stichprobe (30 zufällige Abschnitte in Eimsbüttel, Seed 42)

Links auf openstreetmap.org (Way und Kartenausschnitt am Abschnittsmittelpunkt). Orthophoto- und Panoramax-Links folgen, sobald das Linkformat geklärt ist (docs/open_questions.md).

| segment_id | highway | Name | Länge m | maxspeed (OSM) | Ways | Karte |
| --- | --- | --- | ---: | --- | --- | --- |
| `seg_074cd95a035a05c4` | residential | Papendamm | 111 | 30 | [4004664](https://www.openstreetmap.org/way/4004664) | [OSM](https://www.openstreetmap.org/?mlat=53.566680&mlon=9.976908#map=18/53.566680/9.976908) |
| `seg_0817c77e740f6f6c` | motorway_link |  | 255 | 50 / 80 / 60 | [1276595268](https://www.openstreetmap.org/way/1276595268), [1232032188](https://www.openstreetmap.org/way/1232032188), [3128005](https://www.openstreetmap.org/way/3128005) | [OSM](https://www.openstreetmap.org/?mlat=53.593640&mlon=9.922273#map=18/53.593640/9.922273) |
| `seg_08c8ff2f0960effa` | primary | Holsteiner Chaussee | 10 | 50 | [408642295](https://www.openstreetmap.org/way/408642295) | [OSM](https://www.openstreetmap.org/?mlat=53.620392&mlon=9.908264#map=18/53.620392/9.908264) |
| `seg_094a4278a1b7df0b` | residential | Redingskamp | 33 | 30 | [42413679](https://www.openstreetmap.org/way/42413679) | [OSM](https://www.openstreetmap.org/?mlat=53.612511&mlon=9.890739#map=18/53.612511/9.890739) |
| `seg_1795d520ce96094f` | tertiary | Hallerstraße | 355 | 50 | [39095469](https://www.openstreetmap.org/way/39095469), [625164523](https://www.openstreetmap.org/way/625164523), [40154297](https://www.openstreetmap.org/way/40154297) (+2) | [OSM](https://www.openstreetmap.org/?mlat=53.572680&mlon=9.991315#map=18/53.572680/9.991315) |
| `seg_191011c181a9eccc` | residential | Nordalbingerweg | 161 | 30 | [1168136673](https://www.openstreetmap.org/way/1168136673), [1168136883](https://www.openstreetmap.org/way/1168136883) | [OSM](https://www.openstreetmap.org/?mlat=53.647269&mlon=9.953846#map=18/53.647269/9.953846) |
| `seg_1b9a3cddb28e88fc` | residential | Baarkamp | 121 | 30 | [496601616](https://www.openstreetmap.org/way/496601616) | [OSM](https://www.openstreetmap.org/?mlat=53.606061&mlon=9.940001#map=18/53.606061/9.940001) |
| `seg_1e458da33ee07a13` | primary | Holsteiner Chaussee | 105 | 50 | [1237810184](https://www.openstreetmap.org/way/1237810184) | [OSM](https://www.openstreetmap.org/?mlat=53.613632&mlon=9.906137#map=18/53.613632/9.906137) |
| `seg_25d1ac9c3e551005` | primary | Volksparkstraße | 29 | 50 | [791191448](https://www.openstreetmap.org/way/791191448) | [OSM](https://www.openstreetmap.org/?mlat=53.592261&mlon=9.928222#map=18/53.592261/9.928222) |
| `seg_358951a082994ddb` | tertiary_link | Randstraße | 52 | 50 | [294341136](https://www.openstreetmap.org/way/294341136) | [OSM](https://www.openstreetmap.org/?mlat=53.590672&mlon=9.919112#map=18/53.590672/9.919112) |
| `seg_3aa36b39784dd8ef` | tertiary | Bundesstraße | 159 | 50 | [34910042](https://www.openstreetmap.org/way/34910042), [1564787505](https://www.openstreetmap.org/way/1564787505), [1564787506](https://www.openstreetmap.org/way/1564787506) (+2) | [OSM](https://www.openstreetmap.org/?mlat=53.566505&mlon=9.978338#map=18/53.566505/9.978338) |
| `seg_3babf4754de00a23` | tertiary | Langenfelder Damm | 27 | 50 | [362847066](https://www.openstreetmap.org/way/362847066) | [OSM](https://www.openstreetmap.org/?mlat=53.582254&mlon=9.936336#map=18/53.582254/9.936336) |
| `seg_3e223c69dbb2f955` | residential | Sillemstraße | 57 | 30 | [33174204](https://www.openstreetmap.org/way/33174204), [1071074633](https://www.openstreetmap.org/way/1071074633) | [OSM](https://www.openstreetmap.org/?mlat=53.575755&mlon=9.947214#map=18/53.575755/9.947214) |
| `seg_4148700f372a9ce0` | unclassified | Niewisch | 543 | – | [23789665](https://www.openstreetmap.org/way/23789665), [27005658](https://www.openstreetmap.org/way/27005658), [61389797](https://www.openstreetmap.org/way/61389797) | [OSM](https://www.openstreetmap.org/?mlat=53.603593&mlon=9.933482#map=18/53.603593/9.933482) |
| `seg_49b79f06f43ff531` | secondary | Beim Schlump | 29 | 50 | [885624896](https://www.openstreetmap.org/way/885624896), [391821196](https://www.openstreetmap.org/way/391821196), [391821195](https://www.openstreetmap.org/way/391821195) | [OSM](https://www.openstreetmap.org/?mlat=53.572154&mlon=9.978520#map=18/53.572154/9.978520) |
| `seg_6fea3421a8e61461` | residential | König-Heinrich-Weg | 16 | 30 | [148170151](https://www.openstreetmap.org/way/148170151) | [OSM](https://www.openstreetmap.org/?mlat=53.629453&mlon=9.958140#map=18/53.629453/9.958140) |
| `seg_889c8d2b0829d7eb` | tertiary | Nordalbingerweg | 88 | 50 | [130423837](https://www.openstreetmap.org/way/130423837), [655188659](https://www.openstreetmap.org/way/655188659), [1018242773](https://www.openstreetmap.org/way/1018242773) (+1) | [OSM](https://www.openstreetmap.org/?mlat=53.640223&mlon=9.949710#map=18/53.640223/9.949710) |
| `seg_941f9f9872f60c5b` | residential | Albertine-Assor-Straße | 102 | 30 | [57841666](https://www.openstreetmap.org/way/57841666) | [OSM](https://www.openstreetmap.org/?mlat=53.631831&mlon=9.899701#map=18/53.631831/9.899701) |
| `seg_991b1ad0c5162d48` | residential | Jägerdamm | 242 | 30 | [8139313](https://www.openstreetmap.org/way/8139313), [1166226259](https://www.openstreetmap.org/way/1166226259), [1166226256](https://www.openstreetmap.org/way/1166226256) (+1) | [OSM](https://www.openstreetmap.org/?mlat=53.631254&mlon=9.936048#map=18/53.631254/9.936048) |
| `seg_a0d1d176f25580c5` | residential | Am Ziegelteich | 66 | 30 | [871610817](https://www.openstreetmap.org/way/871610817) | [OSM](https://www.openstreetmap.org/?mlat=53.575285&mlon=9.932449#map=18/53.575285/9.932449) |
| `seg_a37288f67fbcc839` | residential | Wischhofsweg | 45 | 30 | [7399630](https://www.openstreetmap.org/way/7399630) | [OSM](https://www.openstreetmap.org/?mlat=53.605459&mlon=9.903236#map=18/53.605459/9.903236) |
| `seg_adb79e6d36616843` | residential | Lohbekstieg | 122 | 30 | [16322441](https://www.openstreetmap.org/way/16322441) | [OSM](https://www.openstreetmap.org/?mlat=53.594663&mlon=9.955353#map=18/53.594663/9.955353) |
| `seg_b089ef4f24741d02` | primary | Kieler Straße | 41 | 50 | [692691299](https://www.openstreetmap.org/way/692691299) | [OSM](https://www.openstreetmap.org/?mlat=53.592685&mlon=9.927902#map=18/53.592685/9.927902) |
| `seg_b848f5e7a207d8a3` | residential | Jungfrauenthal | 48 | 30 | [48766126](https://www.openstreetmap.org/way/48766126) | [OSM](https://www.openstreetmap.org/?mlat=53.581339&mlon=9.982308#map=18/53.581339/9.982308) |
| `seg_bf4ee71728444fba` | primary | Kollaustraße | 42 | 50 | [650779300](https://www.openstreetmap.org/way/650779300) | [OSM](https://www.openstreetmap.org/?mlat=53.603616&mlon=9.962078#map=18/53.603616/9.962078) |
| `seg_c2ceda44fea05517` | living_street | Albertinenstieg | 20 | – | [57841698](https://www.openstreetmap.org/way/57841698) | [OSM](https://www.openstreetmap.org/?mlat=53.633720&mlon=9.899070#map=18/53.633720/9.899070) |
| `seg_c872845679239d81` | motorway | Deckel Stellingen | 2 086 | 80 | [1547022452](https://www.openstreetmap.org/way/1547022452), [683647786](https://www.openstreetmap.org/way/683647786), [544411422](https://www.openstreetmap.org/way/544411422) (+4) | [OSM](https://www.openstreetmap.org/?mlat=53.603810&mlon=9.920568#map=18/53.603810/9.920568) |
| `seg_c9517409770da0de` | motorway |  | 246 | 80 | [296326689](https://www.openstreetmap.org/way/296326689) | [OSM](https://www.openstreetmap.org/?mlat=53.635722&mlon=9.924401#map=18/53.635722/9.924401) |
| `seg_c99f612476e4c588` | tertiary | Harvestehuder Weg | 9 | 50 | [1493614351](https://www.openstreetmap.org/way/1493614351) | [OSM](https://www.openstreetmap.org/?mlat=53.578535&mlon=9.997219#map=18/53.578535/9.997219) |
| `seg_f1069d5b1080e6b7` | motorway_link |  | 364 | 80 | [1080326852](https://www.openstreetmap.org/way/1080326852), [144146627](https://www.openstreetmap.org/way/144146627) | [OSM](https://www.openstreetmap.org/?mlat=53.613403&mlon=9.915521#map=18/53.613403/9.915521) |

## Lizenz

Abgeleitet aus OpenStreetMap-Daten © OpenStreetMap-Beitragende, ODbL 1.0 (docs/licenses.md).
