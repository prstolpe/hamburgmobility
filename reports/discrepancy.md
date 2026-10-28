# Diskrepanz und Priorisierung – Stufe 8

Erzeugt: 2026-10-28T14:26:31+00:00 von `pipeline/s08_discrepancy.py`, rules.yaml 0.10.1. Nicht amtlicher Entwurf. Top 30: `reports/priority_top30.md`.

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 34502 Abschnitte |
| Stärken 0–3 | ok | disc_speed/design/use |
| Priorität 0–3 | ok | 4466 Werte |
| Typ genau bei Diskrepanz | ok | disc_type gesetzt ⇔ Ursache vorhanden ⇔ Stärke > 0 |
| Unfälle vollständig zugeordnet | ok | 16868 von 17534 Unfällen (Fuß/Rad) einem Abschnitt zugeordnet |
| keine Einzelunfälle im Ergebnis | ok | nur Summen je Abschnitt |

## Kennzahlen

- Bewertet: 4 787 Abschnitte im Arbeitsgebiet (562.0 km), davon 3 876 im Bezirk Eimsbüttel (461.5 km); Grundlage cat_final.
- Mit Diskrepanz (Stärke > 0): 2 102 Abschnitte, 201.7 km (35.9 % der Länge).
- Nicht prüfbar (keine Dimension entscheidbar): 321 Abschnitte.

### Stärke je Dimension (Abschnitte im Arbeitsgebiet)

| Dimension | Regel | 0 | 1 | 2 | 3 | nicht prüfbar |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Tempo | D-SPD-01 | 2584 | 33 | 1713 | 9 | 448 |
| Gestaltung | D-DES-01 | 3032 | 873 | 50 | 15 | 817 |
| Nutzung | D-USE-01 | 398 | 34 | 34 | 60 | 4261 |

### Gestaltung: Häufigkeit der Verstöße und unbekannte Prüfungen

Fehlende OSM-Tags gelten als unbekannt, nicht als Verstoß (S-FEAT-10).

| Soll | Prüfung | Verstoß | kein Verstoß | unbekannt | Anteil unbekannt |
| --- | --- | ---: | ---: | ---: | ---: |
| GOW50 | cycling: kein baulicher Radweg | 74 | 284 | 9 | 2.5 % |
| GOW50 | cycle_lanes_allowed: Radfahr- oder Schutzstreifen | 37 | 321 | 9 | 2.5 % |
| GOW50 | parking_along_carriageway: Parken längs der Fahrbahn | 15 | 214 | 138 | 37.6 % |
| GOW50 | median_if_lanes_per_dir_gte: mehrere Fahrstreifen je Richtung ohne Mitteltrennung | 173 | 172 | 22 | 6.0 % |
| GOW30 | cycling: Radverkehr auf der Fahrbahn ohne Radfahrstreifen | 49 | 542 | 9 | 1.5 % |
| GOW30 | centre_line: Mittelmarkierung | 0 | 8 | 592 | 98.7 % |
| ETW30 | cycling: baulicher Radweg statt Mischverkehr | 459 | 2510 | 568 | 16.1 % |
| ETW30 | cycle_lanes_allowed: Radfahr- oder Schutzstreifen | 211 | 2758 | 568 | 16.1 % |
| ETW_ERF | cycling: baulicher Radweg statt Mischverkehr | 0 | 43 | 120 | 73.6 % |

Nutzung (D-USE-01): DTV bekannt für 918 von 4 787 Abschnitten (nur Hauptverkehrsstraßen, Stand 2019); geprüft nur für Kategorien mit max_dtv (GOW30).

### Verteilung der Diskrepanztypen je Kategorie (Arbeitsgebiet)

| Soll | D1 | D2 | D3 | keine | nicht prüfbar | Summe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SW | 0 (0.0 km) | 0 (0.0 km) | 0 (0.0 km) | 0 (0.0 km) | 120 (28.4 km) | 120 (28.4 km) |
| GOW50 | 28 (4.7 km) | 212 (16.1 km) | 17 (5.1 km) | 110 (12.1 km) | 0 (0.0 km) | 367 (38.1 km) |
| GOW30 | 530 (50.7 km) | 0 (0.0 km) | 49 (4.7 km) | 21 (2.1 km) | 0 (0.0 km) | 600 (57.5 km) |
| ETW30 | 1252 (119.3 km) | 0 (0.0 km) | 0 (0.0 km) | 2193 (302.2 km) | 92 (6.0 km) | 3537 (427.4 km) |
| ETW_ERF | 14 (1.0 km) | 0 (0.0 km) | 0 (0.0 km) | 40 (2.4 km) | 109 (7.1 km) | 163 (10.6 km) |
| **alle** | 1824 (175.7 km) | 212 (16.1 km) | 66 (9.8 km) | 2364 (318.8 km) | 321 (41.5 km) | 4787 (562.0 km) |

## Unfälle (Unfallatlas)

| Jahr | Unfälle mit Personenschaden in Hamburg |
| --- | ---: |
| 2021 | 6 397 |
| 2022 | 7 174 |
| 2023 | 7 332 |
| 2024 | 7 031 |
| 2025 | 7 057 |

- Unfälle mit Fuß- oder Radbeteiligung in Hamburg: 17 534; davon 16 868 einem Abschnitt zugeordnet (höchstens 15 m entfernt), 666 nicht (kein Abschnitt im Umkreis, z. B. Unfälle auf Wegen, Plätzen oder Parkplätzen außerhalb des Kfz-Netzes).
- Im Arbeitsgebiet: 3 613 Unfälle auf 1 608 Abschnitten; davon 296 mit Getöteten oder Schwerverletzten.
- Gespeichert werden nur Summen je Abschnitt (crashes_ped_cyc, crashes_ped, crashes_cyc, crashes_severe_fatal, crash_weighted). Unfälle an Knoten zählen bei genau einem anliegenden Abschnitt.
- Unfallatlas enthält nur polizeilich erfasste Unfälle mit Personenschaden; Alleinunfälle von Radfahrenden sind untererfasst.

## Stichprobe (30 zufällige Abschnitte mit Bewertung in Eimsbüttel, Seed 42)

| segment_id | Name | Soll | Typ | Stärke T/G/N | Priorität | Begründung | Links |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `seg_08286f57dfffd7bc` | Sandkrugweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559023,5942279]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.625977/9.892470) · [OSM](https://www.openstreetmap.org/way/23711864) |
| `seg_084b77659b8b9fdb` | Halstenbeker Weg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 1 Unfall mit Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558297,5941362]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.617818/9.881309) · [OSM](https://www.openstreetmap.org/way/1306480196) |
| `seg_094a4278a1b7df0b` | Redingskamp | ETW30 | D1 | 2/1/– | 0.50 | Soll Quartiersstraße, heute 50 km/h (Soll 30), baulicher Radweg statt Mischverkehr, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 67 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558928,5940780]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.612511/9.890739) · [OSM](https://www.openstreetmap.org/way/42413679) |
| `seg_098790fe850d2584` | Sandweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 46 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562891,5936322]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.571990/9.949740) · [OSM](https://www.openstreetmap.org/way/32200318) |
| `seg_18d3ccf1ce303ad8` | Hallerplatz | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 4 Unfälle mit Radbeteiligung 2021–2025, im Radnetz, Schule/Kita in 82 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565274,5936355]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.571989/9.985730) · [OSM](https://www.openstreetmap.org/way/1473489729) |
| `seg_1abf10d7274d8422` | Rahweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564622,5944053]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.641256/9.977482) · [OSM](https://www.openstreetmap.org/way/148170157) |
| `seg_1d6fbefedef6a0c5` | Alsterglacis | ETW30 | D1 | 2/1/– | 0.43 | Soll Quartiersstraße, heute 50 km/h (Soll 30), baulicher Radweg statt Mischverkehr, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, im Radnetz | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565833,5934897]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558821/9.993866) · [OSM](https://www.openstreetmap.org/way/1108564798) |
| `seg_2046c69968499c60` | Paul-Sorge-Straße | ETW30 | D1 | 2/1/– | 0.55 | Soll Quartiersstraße, heute 50 km/h (Soll 30), Radfahr- oder Schutzstreifen, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, im Radnetz | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562861,5942532]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.627805/9.950539) · [OSM](https://www.openstreetmap.org/way/1165978443) |
| `seg_2895dfd8975cbca8` | Heckenrosenweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 1 Unfall mit Radbeteiligung 2021–2025, Schule/Kita in 12 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563309,5940095]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.605846/9.956816) · [OSM](https://www.openstreetmap.org/way/139267077) |
| `seg_3872c0416154780d` | – | ETW30 | D1 | 2/0/– | 0.51 | Soll Quartiersstraße, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 85 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565797,5937623]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.583323/9.993898) · [OSM](https://www.openstreetmap.org/way/1300900338) |
| `seg_3d962dec972e1262` | Koppelstraße | GOW50 | – | 0/0/– | 0.00 | Soll Stadtmagistrale, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562427,5938684]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.593268/9.943199) · [OSM](https://www.openstreetmap.org/way/692687387) |
| `seg_3efdab96049371c7` | Holsteiner Chaussee | GOW50 | – | 0/0/– | 0.00 | Soll Stadtmagistrale, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560026,5941397]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.617932/9.907453) · [OSM](https://www.openstreetmap.org/way/38664956) |
| `seg_418a436681581d2f` | Beckstedtweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564620,5942632]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.628486/9.977156) · [OSM](https://www.openstreetmap.org/way/147144663) |
| `seg_4575f2dd9c2a2b4b` | Rungwisch | ETW30 | D1 | 2/1/– | 0.49 | Soll Quartiersstraße, heute 50 km/h (Soll 30), baulicher Radweg statt Mischverkehr, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 7 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560336,5940656]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.611241/9.911997) · [OSM](https://www.openstreetmap.org/way/51167181) |
| `seg_4d73d89d0b764cc6` | Hagendeel | ETW30 | D1 | 0/1/– | 0.11 | Soll Quartiersstraße, baulicher Radweg statt Mischverkehr, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562940,5939731]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.602616/9.951161) · [OSM](https://www.openstreetmap.org/way/139267069) |
| `seg_769780fab587f15d` | Ellerbeker Weg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559983,5944219]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.643301/9.907358) · [OSM](https://www.openstreetmap.org/way/964082439) |
| `seg_91537ed7fb26718d` | Oddernskamp | ETW30 | D1 | 2/1/– | 0.22 | Soll Quartiersstraße, heute 50 km/h (Soll 30), baulicher Radweg statt Mischverkehr, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562987,5939529]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.600797/9.951836) · [OSM](https://www.openstreetmap.org/way/1081798492) |
| `seg_9e049b271856659d` | Försterweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 42 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561793,5937144]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.579508/9.933326) · [OSM](https://www.openstreetmap.org/way/145693815) |
| `seg_9e0db8b89e223eea` | Frohmestraße | GOW30 | D1 | 2/0/3 | 0.13 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), 35 000 Kfz/Tag (DTV 2019) über 10 000, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561581,5942654]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.629053/9.931210) · [OSM](https://www.openstreetmap.org/way/149136683) |
| `seg_a20f166249e66a0b` | Salierweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 149 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562639,5943734]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.638630/9.947431) · [OSM](https://www.openstreetmap.org/way/1166228138) |
| `seg_aa27b0be1b33c3cb` | Niendorfer Gehege | ETW30 | D1 | 2/0/– | 0.57 | Soll Quartiersstraße, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 23 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560490,5940634]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.611020/9.914320) · [OSM](https://www.openstreetmap.org/way/30333050) |
| `seg_ad9741851cf7c4c8` | Niendorfer Gehege | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562284,5941305]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.616844/9.941571) · [OSM](https://www.openstreetmap.org/way/127717730) |
| `seg_b901c17049e36b66` | Quedlinburger Weg | ETW30 | D1 | 2/0/– | 0.24 | Soll Quartiersstraße, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562119,5942897]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.631173/9.939390) · [OSM](https://www.openstreetmap.org/way/4335095) |
| `seg_bc2c8bdfba099b09` | Klosterstern | ETW30 | D1 | 2/1/– | 0.91 | Soll Quartiersstraße, heute 50 km/h (Soll 30), Radfahr- oder Schutzstreifen, 4 Unfälle mit Radbeteiligung 2021–2025, davon 1 mit Getöteten/Schwerverletzten | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565485,5937408]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.581429/9.989136) · [OSM](https://www.openstreetmap.org/way/1370385199) |
| `seg_c455ff9d651c7ff1` | Kranichhorst | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563384,5942854]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.630631/9.958512) · [OSM](https://www.openstreetmap.org/way/26781741) |
| `seg_cb3513dab9af667f` | Rahweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564572,5943818]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.639154/9.976671) · [OSM](https://www.openstreetmap.org/way/1167748514) |
| `seg_ced2d92803cf16fa` | Zum Markt | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563049,5941847]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.621628/9.953239) · [OSM](https://www.openstreetmap.org/way/24402806) |
| `seg_d3c29f370ca3d5d5` | Osterfeldstraße | GOW30 | D1 | 2/0/0 | 0.62 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 79 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563824,5939428]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.599791/9.964467) · [OSM](https://www.openstreetmap.org/way/144246660) |
| `seg_d4e3c2baa189dc4e` | Hermann-Behn-Weg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 142 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565372,5936309]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.571572/9.987197) · [OSM](https://www.openstreetmap.org/way/136712396) |
| `seg_d556155f455062cc` | Erlenstraße | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 1 Unfall mit Radbeteiligung 2021–2025, Schule/Kita in 86 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563277,5939216]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.597954/9.956154) · [OSM](https://www.openstreetmap.org/way/22757927) |

## Lizenz

Abschnitte und Gestaltungsmerkmale aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale (Tempo, Verkehrsmengen): Freie und Hansestadt Hamburg, dl-de/by-2.0; Einwohner: Zensus 2022, dl-de/by-2.0; Unfälle: © Statistische Ämter des Bundes und der Länder, Unfallatlas, dl-de/by-2.0 (nur Summen je Abschnitt). Orthophotos: LGV Hamburg, dl-de/by-2.0. Panoramax-Bilder: Lizenz je Bild.

