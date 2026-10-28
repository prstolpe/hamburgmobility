# Kohärenzbericht – Stufe 6

Erzeugt: 2026-10-28T13:48:35+00:00 von `pipeline/s06_coherence.py`, rules.yaml 0.9.0. Nicht amtlicher Entwurf: Die Regeln markieren nur; nichts wird umklassifiziert. Entscheidungen über overrides/overrides.csv.

## Kennzahlen

- Geprüft: 4 787 Abschnitte im Arbeitsgebiet (562.0 km), 3 372 Knoten. Knoten = OSM-Knoten; getrennte Richtungsfahrbahnen sind nicht zusammengefasst (mehrere Knoten je Kreuzung).
- Abschnitte mit mindestens einem Flag: 2 394.

| Regel | Bedeutung | Abschnitte (Arbeitsgebiet) | km | Abschnitte Eimsbüttel | km Eimsbüttel |
| --- | --- | ---: | ---: | ---: | ---: |
| N1 | Durchgängigkeit (GOW-Zug endet ohne Anschluss) | 88 | 8.2 | 59 | 5.5 |
| N2 | Kurze Kategorie-Insel | 132 | 6.5 | 106 | 5.2 |
| N3 | Kleiner Aufenthaltsbereich | 106 | 4.2 | 88 | 3.5 |
| N4 | Schleichverkehr über ETW | 1 082 | 112.2 | 967 | 100.5 |
| N5 | Direkter Übergang ≥ 70 → 30 | 0 | 0.0 | 0 | 0.0 |
| N6 | Knotentyp Soll ≠ Ist | 1 774 | 171.4 | 1 441 | 141.4 |
| N7 | Glättungsvorschlag | 132 | 6.5 | 106 | 5.2 |

Karte: `reports/coherence_flags.geojson` (EPSG:4326; Ebenen segment, node, area; Eigenschaft `rule`), z. B. in QGIS oder geojson.io öffnen.

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 34502 Abschnitte |
| cat_proposed unverändert (keine Umklassifizierung) | ok | Vergleich mit Eingabe |
| flags nur im Arbeitsgebiet, gültiges JSON mit bekannten Regel-IDs | ok | N1, N2, N3, N4, N5, N6, N7 |

## N1 Durchgängigkeit

Enden von GOW-Zügen (GOW80, GOW50, GOW30): Knoten mit genau einem GOW-Abschnitt. In Ordnung, wenn dort SW anschließt oder die Stadtgrenze höchstens 50 m entfernt ist; am Rand des Arbeitsgebiets nicht prüfbar.

| Status | Enden |
| --- | ---: |
| ok_sw | 13 |
| ok_city_boundary | 4 |
| unknown_area_edge | 27 |
| dead_end | 91 |

Häufigste Straßen mit offenem GOW-Ende:

| Name | Kategorie | Enden |
| --- | --- | ---: |
| Garstedter Weg | GOW50 | 5 |
| Stresemannstraße | GOW30 | 4 |
| St. Benedictstraße | GOW30 | 4 |
| Langenfelder Damm | GOW30 | 4 |
| Wördemanns Weg | GOW30 | 3 |
| Kennedybrücke | GOW50 | 3 |
| Max-Brauer-Allee | GOW30 | 3 |
| Lokstedter Steindamm | GOW30 | 3 |
| Kieler Straße | GOW30 | 3 |
| Pinneberger Straße | GOW50 | 2 |
| Oldesloer Straße | GOW50 | 2 |
| Oldesloer Straße | GOW30 | 2 |
| Neuer Jungfernstieg | GOW50 | 2 |
| Kollaustraße | GOW50 | 2 |
| Klosterstern | GOW50 | 2 |

## N2 Kategorie-Inseln und N7 Glättungsvorschläge

Straßenzug: an Knoten mit Grad 2 immer weiter, an Kreuzungen zum gegenseitig besten Abschnitt mit höchstens 30° Richtungsänderung. Insel = Lauf einer Kategorie unter 200 m zwischen zwei Läufen gleicher anderer Kategorie. 132 Abschnitte (6.5 km).

| Vorschlag (N7) neu ← bisher | Abschnitte |
| --- | ---: |
| GOW30 ← GOW50 | 41 |
| GOW30 ← ETW30 | 34 |
| GOW50 ← ETW30 | 16 |
| GOW50 ← GOW30 | 15 |
| ETW30 ← GOW50 | 13 |
| ETW30 ← GOW30 | 8 |
| ETW30 ← ETW_ERF | 4 |
| ETW_ERF ← ETW30 | 1 |

## N3 Aufenthaltsbereiche

Flächen aus GOW/SW-Linien und Stadtgrenze innerhalb des Arbeitsgebiets: 159. Davon enthalten 46 mindestens einen ETW-Abschnitt (Aufenthaltsbereiche); die übrigen 113 sind Verkehrsinseln zwischen Richtungsfahrbahnen oder Grünflächen ohne Erschließung und werden nicht bewertet. Vollständig (berühren den Rand des Arbeitsgebiets nicht): 45; davon unter 25 ha: 37 mit 106 ETW-Abschnitten. Kompaktheit = 4π·Fläche/Umfang² (1 = Kreis); dafür gibt es noch keine Schwelle (docs/open_questions.md).

| Fläche | ha | Umfang m | Kompaktheit | ETW-Abschnitte | vollständig | unter Schwelle |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 101 | 0.0 | 69 | 0.58 | 1 | ja | ja |
| 46 | 0.0 | 99 | 0.52 | 1 | ja | ja |
| 93 | 0.1 | 133 | 0.40 | 2 | ja | ja |
| 119 | 0.1 | 217 | 0.15 | 1 | ja | ja |
| 57 | 0.1 | 200 | 0.21 | 1 | ja | ja |
| 28 | 0.1 | 219 | 0.21 | 2 | ja | ja |
| 108 | 0.1 | 275 | 0.14 | 2 | ja | ja |
| 40 | 0.1 | 172 | 0.39 | 2 | ja | ja |
| 73 | 0.1 | 468 | 0.06 | 1 | ja | ja |
| 36 | 0.1 | 252 | 0.20 | 2 | ja | ja |
| 75 | 0.1 | 250 | 0.22 | 1 | ja | ja |
| 38 | 0.1 | 241 | 0.24 | 1 | ja | ja |
| 34 | 0.1 | 281 | 0.19 | 1 | ja | ja |
| 104 | 0.1 | 260 | 0.24 | 1 | ja | ja |
| 85 | 0.2 | 306 | 0.21 | 1 | ja | ja |
| 87 | 0.2 | 278 | 0.27 | 1 | ja | ja |
| 42 | 0.2 | 324 | 0.20 | 1 | ja | ja |
| 8 | 0.2 | 356 | 0.17 | 1 | ja | ja |
| 96 | 0.2 | 341 | 0.19 | 1 | ja | ja |
| 45 | 0.2 | 325 | 0.23 | 3 | ja | ja |
| 123 | 0.3 | 459 | 0.15 | 2 | ja | ja |
| 70 | 0.3 | 742 | 0.07 | 2 | ja | ja |
| 110 | 0.3 | 448 | 0.20 | 2 | ja | ja |
| 18 | 0.3 | 706 | 0.09 | 4 | ja | ja |
| 77 | 0.4 | 694 | 0.10 | 1 | ja | ja |
| 9 | 0.6 | 902 | 0.09 | 1 | ja | ja |
| 43 | 1.1 | 2005 | 0.03 | 4 | ja | ja |
| 30 | 1.4 | 2616 | 0.03 | 9 | ja | ja |
| 39 | 1.6 | 2341 | 0.04 | 6 | ja | ja |
| 25 | 1.7 | 2762 | 0.03 | 6 | ja | ja |
| 121 | 3.8 | 4189 | 0.03 | 2 | ja | ja |
| 97 | 3.9 | 3061 | 0.05 | 1 | ja | ja |
| 54 | 5.1 | 1162 | 0.48 | 11 | ja | ja |
| 13 | 5.2 | 4641 | 0.03 | 1 | ja | ja |
| 56 | 7.9 | 1241 | 0.65 | 9 | ja | ja |
| 10 | 12.8 | 1729 | 0.54 | 12 | ja | ja |
| 37 | 15.4 | 2827 | 0.24 | 6 | ja | ja |
| 32 | 27.2 | 2291 | 0.65 | 28 | ja | nein |
| 29 | 54.4 | 3380 | 0.60 | 41 | ja | nein |
| 64 | 55.8 | 3152 | 0.71 | 7 | ja | nein |
| 17 | 126.9 | 5629 | 0.50 | 65 | ja | nein |
| 51 | 155.9 | 5089 | 0.76 | 174 | ja | nein |
| 6 | 179.5 | 7164 | 0.44 | 98 | ja | nein |
| 5 | 540.8 | 10376 | 0.63 | 461 | ja | nein |
| 7 | 866.4 | 12654 | 0.68 | 361 | ja | nein |
| 159 | 4262.4 | 77481 | 0.09 | 2208 | nein | nein |

## N4 Schleichverkehr

OD-Knoten: alle 984 Knoten des GOW/SW-Netzes (SW, GOW80, GOW50, GOW30) im Arbeitsgebiet; OD-Paare (ungerichtet, verbunden): 481 672. Reisezeit mit Soll-Tempo je Kategorie, SW mit travel_speed_kmh; pedestrian gesperrt; ohne Einbahnstraßen (Abschnitte tragen keine Richtung). Wege nur innerhalb des Arbeitsgebiets.

- OD-Paare, deren kürzester Weg mehr als 300 m ETW nutzt: 141 275 (29.3 %), obwohl ein Weg nur auf GOW/SW besteht.
- Weitere 72 996 OD-Paare sind nur über ETW verbunden (Lücke im GOW/SW-Netz, siehe N1); sie werden gezählt, aber nicht als Schleichverkehr markiert.
- Median Umwegfaktor (Zeit GOW/SW-Weg ÷ kürzester Weg) dieser Paare: 1.18.
- Markierte ETW-Abschnitte: 1 082 (112.2 km). Verteilung der OD-Paare je Abschnitt: 1–99: 224, 100–999: 366, 1 000–9 999: 404, ≥ 10 000: 88.
- GOW30 und ETW30 haben dasselbe Soll-Tempo; jeder kürzere Weg durch ETW gewinnt dann. Die Zahl ist deshalb ein Maß für die Durchlässigkeit der Quartiere, kein Verkehrsmodell.

Meistgenutzte ETW-Abschnitte:

| segment_id | Name | Kategorie | OD-Paare |
| --- | --- | --- | ---: |
| `seg_1606c90ff4547561` | – | ETW30 | 24 007 |
| `seg_61f70b135937ae03` | Quickbornstraße | ETW30 | 22 878 |
| `seg_d2273291da58242a` | Eidelstedter Weg | ETW30 | 22 327 |
| `seg_1d3b3fe24c77d387` | Lappenbergsallee | ETW30 | 21 735 |
| `seg_fe3f68204c6167a5` | Eidelstedter Weg | ETW30 | 20 770 |
| `seg_2d543ae331a97ff8` | Steenwisch | ETW30 | 20 757 |
| `seg_c75da928ca3da5c9` | Eidelstedter Weg | ETW30 | 20 719 |
| `seg_d2909ef54dd5521f` | Quickbornstraße | ETW30 | 20 464 |
| `seg_ccfe03a785277910` | Mansteinstraße | ETW30 | 19 836 |
| `seg_95c6864081297434` | Eidelstedter Weg | ETW30 | 19 753 |
| `seg_3f83e48c8f2ecc41` | Eidelstedter Weg | ETW30 | 19 424 |
| `seg_adcc7eaf45ce240c` | – | ETW30 | 18 757 |
| `seg_a4ae8748a2b153be` | Eidelstedter Weg | ETW30 | 18 757 |
| `seg_86c1ae410c6822d8` | – | ETW30 | 18 722 |
| `seg_090ec8e9150f0ae2` | Weidenallee | ETW30 | 18 456 |

## N5 Übergänge

Übergänge, die eine Torsituation brauchen, je Kategoriepaar (Knoten). Ob eine Torsituation vorhanden ist, lässt sich aus den Daten nicht ablesen; die Liste dient der Durchsicht.

| von → nach | Knoten |
| --- | ---: |
| GOW30 → ETW30 | 512 |
| GOW50 → ETW30 | 321 |
| GOW50 → GOW30 | 162 |
| GOW50 → ETW_ERF | 4 |
| GOW30 → ETW_ERF | 4 |

Direkter Übergang ≥ 70 km/h → 30-km/h-Kategorie (Flag auf der 30-Seite): 0 Knoten, 0 Abschnitte.

## N6 Knotentypen

Knoten mit Grad ≥ 3: 2 742. Ergebnis: not_checkable 1 814, mismatch 758, not_defined 140, match 30. Ist aus OSM (1 425 Ampelknoten, 43 Plateaus, 76 Kreisverkehrs-Ways im Umkreis 30 m); none_mapped = nichts davon erfasst. Gehwegüberfahrten sind in OSM nicht erfasst → not_checkable. Eine Ampel im Umkreis kann zur Nachbarkreuzung gehören (v. a. bei ETW-Knoten nahe einer Hauptstraße); Kreisverkehre haben mehrere Knoten.

| Soll \ Ist | none_mapped | plateau | roundabout | signal | signal_plateau |
| --- | ---: | ---: | ---: | ---: | ---: |
| equal_right_before_left | 1 449 | 20 | 64 | 160 | 0 |
| not_defined | 78 | 3 | 0 | 59 | 0 |
| priority_gow_sidewalk_crossover | 48 | 0 | 3 | 122 | 0 |
| roundabout | 36 | 0 | 2 | 69 | 0 |
| roundabout_or_signal_plateau | 77 | 0 | 4 | 114 | 0 |
| sidewalk_crossover | 70 | 4 | 1 | 1 | 0 |
| sidewalk_crossover_or_priority_plateau | 129 | 4 | 10 | 214 | 1 |

Abweichungen Soll ≠ Ist:

| Soll | Ist | Knoten |
| --- | --- | ---: |
| sidewalk_crossover_or_priority_plateau | signal | 214 |
| equal_right_before_left | signal | 160 |
| priority_gow_sidewalk_crossover | signal | 122 |
| roundabout_or_signal_plateau | none_mapped | 77 |
| roundabout | signal | 69 |
| equal_right_before_left | roundabout | 64 |
| roundabout | none_mapped | 36 |
| sidewalk_crossover_or_priority_plateau | roundabout | 10 |
| priority_gow_sidewalk_crossover | roundabout | 3 |
| sidewalk_crossover | roundabout | 1 |
| sidewalk_crossover | signal | 1 |
| sidewalk_crossover_or_priority_plateau | signal_plateau | 1 |

Kategoriepaare ohne Soll-Knotentyp (Tabelle 1.4 deckt sie nicht ab): SW, GOW50 (50), SW, SW (49), ETW_ERF, ETW_ERF (40), SW, ETW30 (1).

## Stichprobe: 30 zufällige markierte Abschnitte im Bezirk Eimsbüttel (Seed 42)

Fachlich durchsehen: Ist das Flag berechtigt? **Durchsicht: offen.**

| segment_id | Name | Kategorie | m | Flags | Orthophoto | Panoramax | OSM |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| `seg_066ca5ae57e63d8e` | Schröderstiftstraße | GOW50 | 46 | N2_island, N7_smooth:GOW30, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564282,5935829]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567391/9.970636) | [Way](https://www.openstreetmap.org/way/521056825) |
| `seg_07e455276155aef6` | An der Verbindungsbahn | GOW30 | 48 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564756,5935480]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.564194/9.977726) | [Way](https://www.openstreetmap.org/way/521045479) |
| `seg_08b35bcbc85ff8a0` | Grindelallee | GOW50 | 107 | N2_island, N7_smooth:GOW30 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564788,5936302]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571579/9.978375) | [Way](https://www.openstreetmap.org/way/391801520) |
| `seg_094a4278a1b7df0b` | Redingskamp | ETW30 | 33 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558928,5940780]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.612511/9.890739) | [Way](https://www.openstreetmap.org/way/42413679) |
| `seg_17dbbbb23baf1331` | Klosterallee | ETW30 | 9 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564869,5937299]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580524/9.979801) | [Way](https://www.openstreetmap.org/way/963174501) |
| `seg_19a68824da60d5c7` | Edmund-Siemers-Allee | GOW30 | 455 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565397,5935312]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.562609/9.987367) | [Way](https://www.openstreetmap.org/way/1373419495) |
| `seg_1c08f680501af279` | Wendlohstraße | ETW30 | 303 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562712,5942177]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.624632/9.948219) | [Way](https://www.openstreetmap.org/way/1415502489) |
| `seg_1eecc3971dd25d6c` | Oldesloer Straße | ETW30 | 12 | N2_island, N7_smooth:GOW30, N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560233,5943063]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632880/9.910904) | [Way](https://www.openstreetmap.org/way/945786829) |
| `seg_2665db9aff3caf38` | Alte Volksparkstraße | ETW30 | 181 | N3_small_area | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561241,5938561]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592310/9.925264) | [Way](https://www.openstreetmap.org/way/904851773) |
| `seg_352e1a7eb20c61ac` | Siemersplatz | GOW30 | 56 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563800,5939401]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599551/9.964095) | [Way](https://www.openstreetmap.org/way/128280053) |
| `seg_3a4adc68e516ae25` | Jütländer Allee | ETW30 | 143 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561465,5939443]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600203/9.928818) | [Way](https://www.openstreetmap.org/way/144964687) |
| `seg_3aecaf2567797fde` | Höxterstraße | ETW30 | 327 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564025,5939192]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.597645/9.967458) | [Way](https://www.openstreetmap.org/way/143961980) |
| `seg_3cf7358b56f26acd` | Vogt-Kölln-Straße | ETW30 | 398 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561561,5939787]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603288/9.930342) | [Way](https://www.openstreetmap.org/way/1417924345) |
| `seg_40b3b1a8df5a4df7` | Fruchtallee | ETW30 | 18 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563811,5936060]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.569525/9.963577) | [Way](https://www.openstreetmap.org/way/427238245) |
| `seg_491c6b925034f47e` | Klosterallee | ETW30 | 106 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564866,5937356]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.581038/9.979775) | [Way](https://www.openstreetmap.org/way/3986682) |
| `seg_6c8517f1d3ca26a5` | An der Lohe | ETW30 | 11 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563124,5942077]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.623683/9.954426) | [Way](https://www.openstreetmap.org/way/1160842651) |
| `seg_84ea9801ae9fdb64` | Kollaustraße | GOW30 | 152 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563632,5939906]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.604111/9.961662) | [Way](https://www.openstreetmap.org/way/650779284) |
| `seg_8e8347988f3e7564` | Warburgstraße | ETW30 | 15 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565844,5934901]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.558851/9.994032) | [Way](https://www.openstreetmap.org/way/27064186) |
| `seg_932e987a5540d234` | Högenstraße | ETW30 | 6 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562125,5937310]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580956/9.938368) | [Way](https://www.openstreetmap.org/way/806872057) |
| `seg_9c00922c31525307` | Arminiusstraße | ETW30 | 107 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562025,5937342]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.581257/9.936869) | [Way](https://www.openstreetmap.org/way/763480040) |
| `seg_9f9f90637978a3ca` | Swebenweg | GOW50 | 969 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563811,5944599]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.646267/9.965329) | [Way](https://www.openstreetmap.org/way/220656006) |
| `seg_a8fedde93dfec4fa` | Hainholz | ETW30 | 77 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563192,5941957]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.622597/9.955430) | [Way](https://www.openstreetmap.org/way/159656524) |
| `seg_aae50bec21e57d5c` | Gärtnerstraße | GOW30 | 41 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564019,5937539]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582794/9.967015) | [Way](https://www.openstreetmap.org/way/142762606) |
| `seg_b12d4c35b6d029e7` | Rentzelstraße | GOW30 | 68 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564824,5935658]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565781/9.978793) | [Way](https://www.openstreetmap.org/way/914335526) |
| `seg_b9003657d305da30` | Bismarckstraße | ETW30 | 79 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564169,5936821]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576322/9.969141) | [Way](https://www.openstreetmap.org/way/605881859) |
| `seg_be638afe94e5d439` | Wischhofsweg | ETW30 | 79 | N4_shortcut | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559785,5939947]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.604931/9.903533) | [Way](https://www.openstreetmap.org/way/7399630) |
| `seg_c330d48355534e10` | Hohe Weide | ETW30 | 266 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564425,5936806]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576150/9.973005) | [Way](https://www.openstreetmap.org/way/137037866) |
| `seg_c428210ed9ace2bc` | – | ETW30 | 55 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562301,5936413]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572874/9.940844) | [Way](https://www.openstreetmap.org/way/996116296) |
| `seg_c44ee5bd4f23a4b4` | Baumacker | ETW30 | 31 | N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559459,5940739]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.612082/9.898759) | [Way](https://www.openstreetmap.org/way/1344848985) |
| `seg_ec154048f73c1c11` | Sandweg | ETW30 | 25 | N4_shortcut, N6_node_mismatch | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562905,5936397]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572659/9.949973) | [Way](https://www.openstreetmap.org/way/22757942) |

## Grenzen

- Alle Parameter mit source_type assumption (rules.yaml coherence, thresholds) sind fachlich freizugeben.
- Wege, Flächen und Knoten nur im Arbeitsgebiet (Eimsbüttel + Puffer); Randeffekte sind ausgewiesen.
- Ungerichteter Graph; Abbiegeverbote, Einbahnstraßen und Zufahrtsbeschränkungen fehlen (N4).
- N3 berücksichtigt keine Barrieren wie Bahn, Gewässer oder Parks.

## Korrekturebene (Stufe 6b)

Erzeugt: 2026-10-28T13:48:36+00:00 von `pipeline/s06b_overrides.py`, rules.yaml 0.9.0. Quelle: `overrides/overrides.csv`; übernommen wird nur review_status = approved. cat_proposed bleibt unverändert, cat_final steht daneben.

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
