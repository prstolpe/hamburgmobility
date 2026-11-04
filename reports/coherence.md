# Kohärenzbericht – Stufe 6

Erzeugt: 2026-11-04T20:38:02+00:00 von `pipeline/s06_coherence.py`, rules.yaml 0.12.0. Nicht amtlicher Entwurf: Die Regeln markieren nur; nichts wird umklassifiziert. Entscheidungen über overrides/overrides.csv.

## Kennzahlen

- Geprüft: 4 947 Abschnitte im Arbeitsgebiet (573.4 km), 3 503 Knoten. Knoten = OSM-Knoten; getrennte Richtungsfahrbahnen sind nicht zusammengefasst (mehrere Knoten je Kreuzung).
- Abschnitte mit mindestens einem Flag: 2 577.

| Regel | Bedeutung | Abschnitte (Arbeitsgebiet) | km | Abschnitte Eimsbüttel | km Eimsbüttel |
| --- | --- | ---: | ---: | ---: | ---: |
| N1 | Durchgängigkeit (GOW-Zug endet ohne Anschluss) | 31 | 2.4 | 20 | 1.2 |
| N2 | Kurze Kategorie-Insel | 5 | 0.4 | 4 | 0.3 |
| N3 | Kleiner Aufenthaltsbereich | 185 | 6.0 | 145 | 4.5 |
| N4 | Schleichverkehr über ETW | 1 280 | 135.6 | 1 117 | 119.0 |
| N5 | Direkter Übergang ≥ 70 → 30 | 0 | 0.0 | 0 | 0.0 |
| N6 | Knotentyp Soll ≠ Ist | 1 870 | 172.3 | 1 524 | 142.2 |
| N7 | Glättungsvorschlag | 5 | 0.4 | 4 | 0.3 |

Karte: `reports/coherence_flags.geojson` (EPSG:4326; Ebenen segment, node, area; Eigenschaft `rule`), z. B. in QGIS oder geojson.io öffnen.

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| cat_proposed unverändert (keine Umklassifizierung) | ok | Vergleich mit Eingabe |
| flags nur im Arbeitsgebiet, gültiges JSON mit bekannten Regel-IDs | ok | N1, N2, N3, N4, N5, N6, N7 |

## N1 Durchgängigkeit

Enden von GOW-Zügen (GOW80, GOW50, GOW30): Knoten mit genau einem GOW-Abschnitt. In Ordnung, wenn dort SW anschließt oder die Stadtgrenze höchstens 50 m entfernt ist; am Rand des Arbeitsgebiets nicht prüfbar.

| Status | Enden |
| --- | ---: |
| ok_sw | 1 |
| ok_city_boundary | 2 |
| unknown_area_edge | 19 |
| dead_end | 32 |

Häufigste Straßen mit offenem GOW-Ende:

| Name | Kategorie | Enden |
| --- | --- | ---: |
| St. Benedictstraße | GOW30 | 4 |
| Langenfelder Damm | GOW30 | 4 |
| Wördemanns Weg | GOW30 | 2 |
| Neuer Jungfernstieg | GOW50 | 2 |
| Martinistraße | GOW30 | 1 |
| Stresemannstraße | GOW30 | 1 |
| Stresemannallee | GOW30 | 1 |
| Pinneberger Straße | GOW50 | 1 |
| Oldesloer Straße | GOW30 | 1 |
| Nedderfeld | GOW50 | 1 |
| Max-Brauer-Allee | GOW30 | 1 |
| Martinistraße | GOW50 | 1 |
| Eidelstedter Weg | GOW30 | 1 |
| Friedrich-Ebert-Straße | GOW30 | 1 |
| Lokstedter Steindamm | GOW30 | 1 |

## N2 Kategorie-Inseln und N7 Glättungsvorschläge

Straßenzug: an Knoten mit Grad 2 immer weiter, an Kreuzungen zum gegenseitig besten Abschnitt mit höchstens 30° Richtungsänderung. Insel = Lauf einer Kategorie unter 200 m zwischen zwei Läufen gleicher anderer Kategorie. 5 Abschnitte (0.4 km).

| Vorschlag (N7) neu ← bisher | Abschnitte |
| --- | ---: |
| ETW30 ← ETW_ERF | 4 |
| ETW_ERF ← ETW30 | 1 |

## N3 Aufenthaltsbereiche

Flächen aus GOW/SW-Linien und Stadtgrenze innerhalb des Arbeitsgebiets: 223. Davon enthalten 66 mindestens einen ETW-Abschnitt (Aufenthaltsbereiche); die übrigen 157 sind Verkehrsinseln zwischen Richtungsfahrbahnen oder Grünflächen ohne Erschließung und werden nicht bewertet. Vollständig (berühren den Rand des Arbeitsgebiets nicht): 65; davon unter 25 ha: 54 mit 185 ETW-Abschnitten. Kompaktheit = 4π·Fläche/Umfang² (1 = Kreis); dafür gibt es noch keine Schwelle (docs/open_questions.md).

| Fläche | ha | Umfang m | Kompaktheit | ETW-Abschnitte | vollständig | unter Schwelle |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 188 | 0.0 | 51 | 0.64 | 1 | ja | ja |
| 40 | 0.0 | 67 | 0.47 | 1 | ja | ja |
| 43 | 0.0 | 62 | 0.63 | 1 | ja | ja |
| 147 | 0.0 | 69 | 0.58 | 1 | ja | ja |
| 70 | 0.0 | 62 | 0.72 | 1 | ja | ja |
| 63 | 0.0 | 99 | 0.52 | 1 | ja | ja |
| 170 | 0.1 | 217 | 0.15 | 1 | ja | ja |
| 87 | 0.1 | 200 | 0.21 | 1 | ja | ja |
| 100 | 0.1 | 224 | 0.21 | 2 | ja | ja |
| 157 | 0.1 | 275 | 0.14 | 2 | ja | ja |
| 50 | 0.1 | 252 | 0.20 | 2 | ja | ja |
| 130 | 0.1 | 280 | 0.17 | 1 | ja | ja |
| 165 | 0.1 | 250 | 0.22 | 2 | ja | ja |
| 110 | 0.1 | 250 | 0.22 | 1 | ja | ja |
| 48 | 0.1 | 281 | 0.19 | 1 | ja | ja |
| 111 | 0.1 | 297 | 0.18 | 2 | ja | ja |
| 153 | 0.1 | 260 | 0.24 | 1 | ja | ja |
| 128 | 0.1 | 234 | 0.33 | 1 | ja | ja |
| 136 | 0.2 | 279 | 0.25 | 1 | ja | ja |
| 124 | 0.2 | 306 | 0.21 | 1 | ja | ja |
| 137 | 0.2 | 284 | 0.27 | 1 | ja | ja |
| 14 | 0.2 | 356 | 0.17 | 1 | ja | ja |
| 72 | 0.2 | 359 | 0.17 | 3 | ja | ja |
| 62 | 0.2 | 325 | 0.23 | 3 | ja | ja |
| 176 | 0.3 | 459 | 0.15 | 2 | ja | ja |
| 146 | 0.3 | 603 | 0.09 | 2 | ja | ja |
| 103 | 0.3 | 742 | 0.07 | 2 | ja | ja |
| 159 | 0.3 | 448 | 0.20 | 2 | ja | ja |
| 29 | 0.3 | 706 | 0.09 | 4 | ja | ja |
| 113 | 0.4 | 694 | 0.10 | 1 | ja | ja |
| 15 | 0.4 | 686 | 0.10 | 7 | ja | ja |
| 77 | 0.4 | 723 | 0.10 | 2 | ja | ja |
| 61 | 0.4 | 961 | 0.06 | 1 | ja | ja |
| 53 | 0.4 | 1204 | 0.04 | 1 | ja | ja |
| 57 | 0.5 | 679 | 0.13 | 5 | ja | ja |
| 86 | 0.5 | 807 | 0.10 | 2 | ja | ja |
| 16 | 0.6 | 902 | 0.09 | 1 | ja | ja |
| 10 | 0.7 | 1209 | 0.06 | 2 | ja | ja |
| 8 | 0.7 | 2112 | 0.02 | 2 | ja | ja |
| 95 | 0.9 | 1366 | 0.06 | 6 | ja | ja |
| 151 | 1.0 | 834 | 0.18 | 1 | ja | ja |
| 58 | 1.1 | 2005 | 0.03 | 4 | ja | ja |
| 69 | 1.3 | 2034 | 0.04 | 7 | ja | ja |
| 44 | 1.4 | 2616 | 0.03 | 9 | ja | ja |
| 37 | 1.7 | 2762 | 0.03 | 6 | ja | ja |
| 27 | 2.1 | 3020 | 0.03 | 5 | ja | ja |
| 59 | 2.6 | 1652 | 0.12 | 12 | ja | ja |
| 148 | 3.4 | 6112 | 0.01 | 7 | ja | ja |
| 174 | 3.8 | 4152 | 0.03 | 2 | ja | ja |
| 20 | 5.2 | 4641 | 0.03 | 1 | ja | ja |
| 85 | 7.9 | 1241 | 0.65 | 9 | ja | ja |
| 26 | 12.6 | 2498 | 0.25 | 29 | ja | ja |
| 17 | 12.8 | 1729 | 0.54 | 12 | ja | ja |
| 51 | 15.3 | 2769 | 0.25 | 6 | ja | ja |
| 46 | 27.2 | 2291 | 0.65 | 28 | ja | nein |
| 41 | 54.4 | 3380 | 0.60 | 43 | ja | nein |
| 96 | 55.8 | 3152 | 0.71 | 7 | ja | nein |
| 7 | 56.8 | 3553 | 0.56 | 44 | ja | nein |
| 11 | 122.8 | 5076 | 0.60 | 56 | ja | nein |
| 28 | 126.9 | 5629 | 0.50 | 67 | ja | nein |
| 98 | 154.2 | 5070 | 0.75 | 164 | ja | nein |
| 31 | 294.8 | 9094 | 0.45 | 182 | ja | nein |
| 6 | 537.4 | 9671 | 0.72 | 461 | ja | nein |
| 13 | 679.8 | 10603 | 0.76 | 418 | ja | nein |
| 12 | 865.9 | 12586 | 0.69 | 377 | ja | nein |
| 5 | 3270.1 | 79976 | 0.06 | 1579 | nein | nein |

## N4 Schleichverkehr

OD-Knoten: alle 998 Knoten des GOW/SW-Netzes (SW, GOW80, GOW50, GOW30) im Arbeitsgebiet; OD-Paare (ungerichtet, verbunden): 495 511. Reisezeit mit Soll-Tempo je Kategorie, SW mit travel_speed_kmh; pedestrian gesperrt; ohne Einbahnstraßen (Abschnitte tragen keine Richtung). Wege nur innerhalb des Arbeitsgebiets.

- OD-Paare, deren kürzester Weg mehr als 300 m ETW nutzt: 200 593 (40.5 %), obwohl ein Weg nur auf GOW/SW besteht.
- Weitere 26 538 OD-Paare sind nur über ETW verbunden (Lücke im GOW/SW-Netz, siehe N1); sie werden gezählt, aber nicht als Schleichverkehr markiert.
- Median Umwegfaktor (Zeit GOW/SW-Weg ÷ kürzester Weg) dieser Paare: 1.13.
- Markierte ETW-Abschnitte: 1 280 (135.6 km). Verteilung der OD-Paare je Abschnitt: 1–99: 243, 100–999: 439, 1 000–9 999: 501, ≥ 10 000: 97.
- GOW30 und ETW30 haben dasselbe Soll-Tempo; jeder kürzere Weg durch ETW gewinnt dann. Die Zahl ist deshalb ein Maß für die Durchlässigkeit der Quartiere, kein Verkehrsmodell.

Meistgenutzte ETW-Abschnitte:

| segment_id | Name | Kategorie | OD-Paare |
| --- | --- | --- | ---: |
| `seg_ea815fcfa6e7037e` | Rondenbarg | ETW30 | 33 569 |
| `seg_e6f1f82c33617125` | Rondenbarg | ETW30 | 33 569 |
| `seg_65865a9f0b189fdb` | Rondenbarg | ETW30 | 33 569 |
| `seg_61f70b135937ae03` | Quickbornstraße | ETW30 | 30 679 |
| `seg_a2dd83e6c7222900` | Sportplatzring | ETW30 | 29 585 |
| `seg_d2273291da58242a` | Eidelstedter Weg | ETW30 | 28 982 |
| `seg_d2909ef54dd5521f` | Quickbornstraße | ETW30 | 27 506 |
| `seg_ccfe03a785277910` | Mansteinstraße | ETW30 | 27 368 |
| `seg_fe3f68204c6167a5` | Eidelstedter Weg | ETW30 | 27 290 |
| `seg_c75da928ca3da5c9` | Eidelstedter Weg | ETW30 | 27 238 |
| `seg_ba2f4a7ff187c614` | Julius-Vosseler-Straße | ETW30 | 26 707 |
| `seg_5a20e531cbd69184` | Julius-Vosseler-Straße | ETW30 | 26 707 |
| `seg_52078bb4cc4688f7` | Julius-Vosseler-Straße | ETW30 | 26 707 |
| `seg_984bbd7d72cabcb1` | Julius-Vosseler-Straße | ETW30 | 26 456 |
| `seg_86c1ae410c6822d8` | – | ETW30 | 25 763 |

## N5 Übergänge

Übergänge, die eine Torsituation brauchen, je Kategoriepaar (Knoten). Ob eine Torsituation vorhanden ist, lässt sich aus den Daten nicht ablesen; die Liste dient der Durchsicht.

| von → nach | Knoten |
| --- | ---: |
| GOW30 → ETW30 | 542 |
| GOW50 → ETW30 | 180 |
| GOW50 → GOW30 | 92 |
| GOW30 → ETW_ERF | 4 |
| GOW50 → ETW_ERF | 2 |

Direkter Übergang ≥ 70 km/h → 30-km/h-Kategorie (Flag auf der 30-Seite): 0 Knoten, 0 Abschnitte.

## N6 Knotentypen

Knoten mit Grad ≥ 3: 2 819. Ergebnis: not_checkable 1 821, mismatch 828, not_defined 140, match 30. Ist aus OSM (1 425 Ampelknoten, 43 Plateaus, 76 Kreisverkehrs-Ways im Umkreis 30 m); none_mapped = nichts davon erfasst. Gehwegüberfahrten sind in OSM nicht erfasst → not_checkable. Eine Ampel im Umkreis kann zur Nachbarkreuzung gehören (v. a. bei ETW-Knoten nahe einer Hauptstraße); Kreisverkehre haben mehrere Knoten.

| Soll \ Ist | none_mapped | plateau | roundabout | signal | signal_plateau |
| --- | ---: | ---: | ---: | ---: | ---: |
| equal_right_before_left | 1 504 | 21 | 64 | 164 | 0 |
| not_defined | 78 | 3 | 0 | 59 | 0 |
| priority_gow_sidewalk_crossover | 37 | 0 | 0 | 81 | 0 |
| roundabout | 53 | 1 | 4 | 111 | 0 |
| roundabout_or_signal_plateau | 48 | 0 | 2 | 53 | 0 |
| sidewalk_crossover | 71 | 4 | 1 | 1 | 0 |
| sidewalk_crossover_or_priority_plateau | 152 | 3 | 13 | 290 | 1 |

Abweichungen Soll ≠ Ist:

| Soll | Ist | Knoten |
| --- | --- | ---: |
| sidewalk_crossover_or_priority_plateau | signal | 290 |
| equal_right_before_left | signal | 164 |
| roundabout | signal | 111 |
| priority_gow_sidewalk_crossover | signal | 81 |
| equal_right_before_left | roundabout | 64 |
| roundabout | none_mapped | 53 |
| roundabout_or_signal_plateau | none_mapped | 48 |
| sidewalk_crossover_or_priority_plateau | roundabout | 13 |
| roundabout | plateau | 1 |
| sidewalk_crossover | roundabout | 1 |
| sidewalk_crossover | signal | 1 |
| sidewalk_crossover_or_priority_plateau | signal_plateau | 1 |

Kategoriepaare ohne Soll-Knotentyp (Tabelle 1.4 deckt sie nicht ab): SW, SW (49), ETW_ERF, ETW_ERF (40), SW, GOW50 (38), SW, GOW30 (13).

## Stichprobe: 30 zufällige markierte Abschnitte im Bezirk Eimsbüttel (Seed 42)

Fachlich durchsehen: Ist das Flag berechtigt? **Durchsicht: offen.**

| segment_id | Name | Kategorie | m | Flags | Orthophoto | Panoramax | OSM |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| `seg_03041f6cf99b8e0a` | Emilienstraße | ETW30 | 39 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563102,5936282]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571602/9.952924) | [Way](https://www.openstreetmap.org/way/1114937846) |
| `seg_0da4a9ea092c0362` | Troplowitzstraße | ETW30 | 49 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564040,5937871]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.585767/9.967412) | [Way](https://www.openstreetmap.org/way/682409953) |
| `seg_0e4cbf86fab8a5f1` | Altonaer Straße | GOW30 | 93 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563687,5935460]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.564145/9.961583) | [Way](https://www.openstreetmap.org/way/702923200) |
| `seg_1043561df8d1bb0c` | Kieler Straße | GOW30 | 284 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561331,5938724]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.593763/9.926664) | [Way](https://www.openstreetmap.org/way/395002918) |
| `seg_1149ace6a8d325d7` | – | ETW30 | 43 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563758,5939455]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600044/9.963466) | [Way](https://www.openstreetmap.org/way/144246657) |
| `seg_2ac0e22cb6848f18` | Halstenbeker Straße / Schnelsener Weg | ETW30 | 290 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558906,5942035]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.623795/9.890644) | [Way](https://www.openstreetmap.org/way/10714530) |
| `seg_2d79472d6e07d869` | Wendlohstraße | ETW30 | 103 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562061,5942760]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.629944/9.938485) | [Way](https://www.openstreetmap.org/way/28176321) |
| `seg_31586e0ccf94c0cc` | Garstedter Weg | GOW30 | 168 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563622,5942713]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.629339/9.962079) | [Way](https://www.openstreetmap.org/way/148170148) |
| `seg_316bf3ec250dbe56` | Grindelallee | GOW30 | 20 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565211,5935459]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.563948/9.984586) | [Way](https://www.openstreetmap.org/way/391787287) |
| `seg_361476383b25ee7e` | Stellinger Weg | ETW30 | 11 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562824,5937163]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.579550/9.948900) | [Way](https://www.openstreetmap.org/way/1186526052) |
| `seg_444b2ba59aef7437` | Langenfelder Damm | ETW30 | 13 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562155,5937251]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580424/9.938806) | [Way](https://www.openstreetmap.org/way/745522722) |
| `seg_4a7fb4bca7199827` | Reichsbahnstraße | ETW30 | 106 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559978,5939259]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598725/9.906316) | [Way](https://www.openstreetmap.org/way/28175306) |
| `seg_4c5be0d5bbe9c00d` | Osterfeldstraße | GOW30 | 41 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564258,5939311]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598687/9.970990) | [Way](https://www.openstreetmap.org/way/975434251) |
| `seg_5efa89ba554e8c48` | Osterfeldstraße | GOW30 | 121 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564360,5939290]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598487/9.972529) | [Way](https://www.openstreetmap.org/way/39965326) |
| `seg_6600444efd3d9aa4` | Swebenweg | GOW30 | 45 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564435,5944538]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645639/9.974750) | [Way](https://www.openstreetmap.org/way/149852883) |
| `seg_67a4a8afe4cc2fc6` | Oberstraße | ETW30 | 185 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565385,5936985]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.577640/9.987529) | [Way](https://www.openstreetmap.org/way/69421321) |
| `seg_68a9851f7fc8ff88` | St. Benedictstraße | GOW30 | 26 | N1_dead_end, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565815,5937621]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.583306/9.994158) | [Way](https://www.openstreetmap.org/way/30412060) |
| `seg_69d0075bb2b3f754` | Grandweg | ETW30 | 11 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563443,5939354]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599170/9.958692) | [Way](https://www.openstreetmap.org/way/912126033) |
| `seg_6e6e66151260eedf` | Osterfeldstraße | GOW30 | 66 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563877,5939396]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599498/9.965255) | [Way](https://www.openstreetmap.org/way/490926532) |
| `seg_7530d0d752b242fc` | Kieler Straße | GOW30 | 30 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561530,5938511]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591823/9.929627) | [Way](https://www.openstreetmap.org/way/395002920) |
| `seg_85271f68c2aae9f8` | Anna-Susanna-Stieg | ETW30 | 46 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560568,5944164]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.642745/9.916185) | [Way](https://www.openstreetmap.org/way/763381505) |
| `seg_86c1ae410c6822d8` | – | ETW30 | 13 | N3_small_area, N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563793,5937144]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.579267/9.963523) | [Way](https://www.openstreetmap.org/way/952072729) |
| `seg_86d228ee644d0a7f` | Osterfeldstraße | ETW30 | 94 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564266,5939261]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598239/9.971113) | [Way](https://www.openstreetmap.org/way/48538356) |
| `seg_a35d62b337055cb0` | Peter-Timm-Straße | ETW30 | 179 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560471,5943834]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.639785/9.914653) | [Way](https://www.openstreetmap.org/way/4974352) |
| `seg_a52d0e033bd95814` | Harvestehuder Weg | ETW30 | 12 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566027,5937084]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578448/9.997254) | [Way](https://www.openstreetmap.org/way/1493614351) |
| `seg_ce1587b332b13e84` | Nedderfeld | GOW30 | 22 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563742,5939851]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603598/9.963303) | [Way](https://www.openstreetmap.org/way/650779328) |
| `seg_cf0e0ce11178d1f3` | Wilzenweg | ETW30 | 17 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563349,5944747]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.647649/9.958375) | [Way](https://www.openstreetmap.org/way/1211705525) |
| `seg_cf3992f4bf1f96ba` | Furtweg | ETW30 | 117 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559859,5939714]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.602828/9.904605) | [Way](https://www.openstreetmap.org/way/28175311) |
| `seg_dba8f1535513a4ff` | Müggenkampstraße | ETW30 | 224 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562510,5937179]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.579738/9.944159) | [Way](https://www.openstreetmap.org/way/28174447) |
| `seg_f854da0277bcb65c` | Lappenbergsallee | GOW30 | 138 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562605,5936677]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575212/9.945485) | [Way](https://www.openstreetmap.org/way/145693853) |

## Grenzen

- Alle Parameter mit source_type assumption (rules.yaml coherence, thresholds) sind fachlich freizugeben.
- Wege, Flächen und Knoten nur im Arbeitsgebiet (Eimsbüttel + Puffer); Randeffekte sind ausgewiesen.
- Ungerichteter Graph; Abbiegeverbote, Einbahnstraßen und Zufahrtsbeschränkungen fehlen (N4).
- N3 berücksichtigt keine Barrieren wie Bahn, Gewässer oder Parks.

## Korrekturebene (Stufe 6b)

Erzeugt: 2026-11-04T20:38:04+00:00 von `pipeline/s06b_overrides.py`, rules.yaml 0.12.0. Quelle: `overrides/overrides.csv`; übernommen wird nur review_status = approved. cat_proposed bleibt unverändert, cat_final steht daneben.

| review_status | Einträge |
| --- | ---: |
| draft | 0 |
| approved | 0 |
| rejected | 0 |

Alle 0 Einträge geprüft: keine verwaisten segment_id, gültige Kategorien, Begründung, Autor*in und Datum vorhanden.

Übernommene Korrekturen: 0.

Neue Korrekturen: `make override-template IDS="seg_… seg_…"` erzeugt Zeilen mit review_status draft; Begründung eintragen und per Pull Request (Vier-Augen-Prinzip) auf approved setzen.

## Lizenz

Netz, Ampeln, Plateaus, Kreisverkehre, Stadtgrenze: © OpenStreetMap-Beitragende, ODbL 1.0; Kategorien beruhen auf amtlichen Daten der Freien und Hansestadt Hamburg, dl-de/by-2.0 (siehe reports/classification.md). Orthophotos: LGV Hamburg, dl-de/by-2.0.
