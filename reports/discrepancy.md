# Diskrepanz und Priorisierung – Stufe 8

Erzeugt: 2026-11-04T20:38:08+00:00 von `pipeline/s08_discrepancy.py`, rules.yaml 0.12.0. Nicht amtlicher Entwurf. Top 30: `reports/priority_top30.md`.

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| Stärken 0–3 | ok | disc_speed/design/use |
| Priorität 0–3 | ok | 4597 Werte |
| Typ genau bei Diskrepanz | ok | disc_type gesetzt ⇔ Ursache vorhanden ⇔ Stärke > 0 |
| Unfälle vollständig zugeordnet | ok | 16961 von 17534 Unfällen (Fuß/Rad) einem Abschnitt zugeordnet |
| keine Einzelunfälle im Ergebnis | ok | nur Summen je Abschnitt |

## Kennzahlen

- Bewertet: 4 947 Abschnitte im Arbeitsgebiet (573.4 km), davon 4 004 im Bezirk Eimsbüttel (470.4 km); Grundlage cat_final.
- Mit Diskrepanz (Stärke > 0): 2 192 Abschnitte, 208.1 km (36.3 % der Länge).
- Nicht prüfbar (keine Dimension entscheidbar): 350 Abschnitte.

### Stärke je Dimension (Abschnitte im Arbeitsgebiet)

| Dimension | Regel | 0 | 1 | 2 | 3 | nicht prüfbar |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Tempo | D-SPD-01 | 2521 | 34 | 1897 | 9 | 486 |
| Gestaltung | D-DES-01 | 3236 | 784 | 32 | 11 | 884 |
| Nutzung | D-USE-01 | 507 | 43 | 45 | 75 | 4277 |

### Gestaltung: Häufigkeit der Verstöße und unbekannte Prüfungen

Fehlende OSM-Tags gelten als unbekannt, nicht als Verstoß (S-FEAT-10).

| Soll | Prüfung | Verstoß | kein Verstoß | unbekannt | Anteil unbekannt |
| --- | --- | ---: | ---: | ---: | ---: |
| GOW50 | cycling: kein baulicher Radweg | 48 | 179 | 13 | 5.4 % |
| GOW50 | cycle_lanes_allowed: Radfahr- oder Schutzstreifen | 22 | 205 | 13 | 5.4 % |
| GOW50 | parking_along_carriageway: Parken längs der Fahrbahn | 12 | 139 | 89 | 37.1 % |
| GOW50 | median_if_lanes_per_dir_gte: mehrere Fahrstreifen je Richtung ohne Mitteltrennung | 95 | 127 | 18 | 7.5 % |
| GOW30 | cycling: Radverkehr auf der Fahrbahn ohne Radfahrstreifen | 71 | 725 | 24 | 2.9 % |
| GOW30 | centre_line: Mittelmarkierung | 0 | 16 | 804 | 98.0 % |
| ETW30 | cycling: baulicher Radweg statt Mischverkehr | 423 | 2561 | 620 | 17.2 % |
| ETW30 | cycle_lanes_allowed: Radfahr- oder Schutzstreifen | 210 | 2774 | 620 | 17.2 % |
| ETW_ERF | cycling: baulicher Radweg statt Mischverkehr | 0 | 43 | 120 | 73.6 % |

Nutzung (D-USE-01): DTV bekannt für 954 von 4 947 Abschnitten (nur Hauptverkehrsstraßen, Stand 2019); geprüft nur für Kategorien mit max_dtv (GOW30).

### Verteilung der Diskrepanztypen je Kategorie (Arbeitsgebiet)

| Soll | D1 | D2 | D3 | keine | nicht prüfbar | Summe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SW | 0 (0.0 km) | 0 (0.0 km) | 0 (0.0 km) | 0 (0.0 km) | 120 (28.4 km) | 120 (28.4 km) |
| GOW50 | 28 (4.7 km) | 117 (11.1 km) | 17 (5.1 km) | 78 (9.3 km) | 0 (0.0 km) | 240 (30.2 km) |
| GOW30 | 723 (60.1 km) | 1 (0.0 km) | 70 (6.6 km) | 24 (2.1 km) | 2 (0.0 km) | 820 (68.8 km) |
| ETW30 | 1222 (119.4 km) | 0 (0.0 km) | 0 (0.0 km) | 2263 (308.2 km) | 119 (7.8 km) | 3604 (435.4 km) |
| ETW_ERF | 14 (1.0 km) | 0 (0.0 km) | 0 (0.0 km) | 40 (2.4 km) | 109 (7.1 km) | 163 (10.6 km) |
| **alle** | 1987 (185.3 km) | 118 (11.1 km) | 87 (11.7 km) | 2405 (322.0 km) | 350 (43.3 km) | 4947 (573.4 km) |

## Unfälle (Unfallatlas)

| Jahr | Unfälle mit Personenschaden in Hamburg |
| --- | ---: |
| 2021 | 6 397 |
| 2022 | 7 174 |
| 2023 | 7 332 |
| 2024 | 7 031 |
| 2025 | 7 057 |

- Unfälle mit Fuß- oder Radbeteiligung in Hamburg: 17 534; davon 16 961 einem Abschnitt zugeordnet (höchstens 15 m entfernt), 573 nicht (kein Abschnitt im Umkreis, z. B. Unfälle auf Wegen, Plätzen oder Parkplätzen außerhalb des Kfz-Netzes).
- Im Arbeitsgebiet: 3 624 Unfälle auf 1 618 Abschnitten; davon 296 mit Getöteten oder Schwerverletzten.
- Gespeichert werden nur Summen je Abschnitt (crashes_ped_cyc, crashes_ped, crashes_cyc, crashes_severe_fatal, crash_weighted). Unfälle an Knoten zählen bei genau einem anliegenden Abschnitt.
- Unfallatlas enthält nur polizeilich erfasste Unfälle mit Personenschaden; Alleinunfälle von Radfahrenden sind untererfasst.

## Stichprobe (30 zufällige Abschnitte mit Bewertung in Eimsbüttel, Seed 42)

| segment_id | Name | Soll | Typ | Stärke T/G/N | Priorität | Begründung | Links |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `seg_07a76dc665cc0939` | Röthmoorweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 115 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561069,5942260]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.625570/9.923399) · [OSM](https://www.openstreetmap.org/way/1567327921) |
| `seg_0830e79c06f98c1a` | Schleswiger Damm | GOW30 | D1 | 2/0/0 | 0.71 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 85 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560264,5944517]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.645952/9.911654) · [OSM](https://www.openstreetmap.org/way/936656313) |
| `seg_090957ada8b66b71` | Wagrierweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 65 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562287,5944066]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.641658/9.942168) · [OSM](https://www.openstreetmap.org/way/1166233444) |
| `seg_0966ad36312a606a` | Uhuweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561245,5940427]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.609074/9.925697) · [OSM](https://www.openstreetmap.org/way/5015300) |
| `seg_18248e31f5ea9e52` | Dornröschenweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560961,5944835]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.648722/9.922270) · [OSM](https://www.openstreetmap.org/way/20929255) |
| `seg_1a0896cff5d03f64` | Garstedter Weg | GOW30 | D1 | 2/0/0 | 0.47 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 112 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562938,5941475]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.618298/9.951490) · [OSM](https://www.openstreetmap.org/way/30339456) |
| `seg_1cc6f3ba9463d373` | Osterfeldstraße | GOW30 | D1 | 2/0/0 | 0.57 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 68 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563870,5939389]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.599438/9.965145) · [OSM](https://www.openstreetmap.org/way/308317373) |
| `seg_1f86d2d452104ac5` | Am Dorfteich | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 89 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560828,5943460]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.636380/9.919979) · [OSM](https://www.openstreetmap.org/way/149136682) |
| `seg_2719ffe412b0dfb5` | Schleswiger Damm | GOW30 | D1 | 2/0/0 | 0.54 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 130 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560814,5943576]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.637431/9.919794) · [OSM](https://www.openstreetmap.org/way/958704058) |
| `seg_36815085f75780c4` | Kieler Straße | GOW30 | D1 | 2/0/0 | 0.72 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 22 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561899,5937222]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.580199/9.934940) · [OSM](https://www.openstreetmap.org/way/145693839) |
| `seg_3bb18ca10dc1f60c` | Warnstedtstraße | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 3 Unfälle mit Radbeteiligung 2021–2025, Schule/Kita in 111 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561666,5937619]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.583793/9.931496) · [OSM](https://www.openstreetmap.org/way/996085254) |
| `seg_3d209916eaf576f1` | Emil-Andresen-Straße | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 1 Unfall mit Radbeteiligung 2021–2025, Schule/Kita in 93 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563411,5939054]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.596475/9.958153) · [OSM](https://www.openstreetmap.org/way/139611673) |
| `seg_3fc5e20bbf0f3110` | Ekenknick | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559699,5940268]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607828/9.902295) · [OSM](https://www.openstreetmap.org/way/122003241) |
| `seg_43917a2052c78965` | Fohrwisch | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561517,5940199]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.606999/9.929763) · [OSM](https://www.openstreetmap.org/way/27005518) |
| `seg_4b9558c7812548e6` | Vietinghoffweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 87 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562122,5943236]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.634218/9.939503) · [OSM](https://www.openstreetmap.org/way/26784001) |
| `seg_73a63c917350363c` | Schleswiger Damm | GOW50 | – | 0/0/– | 0.00 | Soll Stadtmagistrale, 1 Unfall mit Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560334,5944425]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.645117/9.912695) · [OSM](https://www.openstreetmap.org/way/3997436) |
| `seg_8ce2a8460ead4daf` | Alte Elbgaustraße | ETW_ERF | – | –/0/– | 0.00 | Soll Aufenthaltsstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 147 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559738,5940159]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.606845/9.902865) · [OSM](https://www.openstreetmap.org/way/7400680) |
| `seg_988ddc6206499464` | Hildburgweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562317,5940196]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.606875/9.941848) · [OSM](https://www.openstreetmap.org/way/411157232) |
| `seg_9d64a4ac91c54d17` | Mittelweg | ETW30 | D1 | 2/1/– | 1.42 | Soll Quartiersstraße, heute 50 km/h (Soll 30), Radfahr- oder Schutzstreifen, 2 Unfälle mit Fuß-/Radbeteiligung (Rad 1, Fuß 1) 2021–2025, davon 1 mit Getöteten/Schwerverletzten, Schule/Kita in 29 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565893,5936242]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.570899/9.995042) · [OSM](https://www.openstreetmap.org/way/653534687) |
| `seg_a4b1721da090bdcf` | Kieler Straße | GOW30 | D1 | 2/0/0 | 1.09 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), 1 Unfall mit Radbeteiligung 2021–2025, Schule/Kita in 77 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562395,5936326]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572080/9.942254) · [OSM](https://www.openstreetmap.org/way/1359178744) |
| `seg_a869cf09b6234160` | Vogt-Wells-Straße | GOW30 | D1 | 2/0/3 | 0.90 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), 43 000 Kfz/Tag (DTV 2019) über 10 000, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 84 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563779,5939424]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.599762/9.963777) · [OSM](https://www.openstreetmap.org/way/230609914) |
| `seg_b2b45cf9505ddc9c` | Wehmerstieg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562718,5940062]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.605619/9.947881) · [OSM](https://www.openstreetmap.org/way/23417362) |
| `seg_b5ab35a7fb18c3bb` | – | ETW30 | D1 | 2/0/– | 1.26 | Soll Quartiersstraße, heute 50 km/h (Soll 30), 3 Unfälle mit Radbeteiligung 2021–2025, Schule/Kita in 87 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565793,5937600]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.583120/9.993827) · [OSM](https://www.openstreetmap.org/way/1300900342) |
| `seg_be03688885b26b0e` | Kieler Straße | GOW30 | D1 | 2/0/0 | 1.52 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), 4 Unfälle mit Fuß-/Radbeteiligung (Rad 3, Fuß 2) 2021–2025, davon 1 mit Getöteten/Schwerverletzten, Schule/Kita in 22 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561914,5937172]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.579746/9.935153) · [OSM](https://www.openstreetmap.org/way/733544406) |
| `seg_c5326e98c137974e` | Sachsenweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, 1 Unfall mit Radbeteiligung 2021–2025, Schule/Kita in 11 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563450,5944122]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.642026/9.959764) · [OSM](https://www.openstreetmap.org/way/24586472) |
| `seg_c8fd37a4058d26dc` | Holstenkamp | GOW30 | D1 | 2/0/0 | 0.46 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 37 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562313,5936396]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572719/9.941028) · [OSM](https://www.openstreetmap.org/way/791199499) |
| `seg_ce1e4a5cafa62db3` | Oldesloer Straße | GOW50 | D2 | 0/1/– | 0.01 | Soll Stadtmagistrale, kein baulicher Radweg, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562769,5945060]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.650531/9.949655) · [OSM](https://www.openstreetmap.org/way/749892946) |
| `seg_cf0e0ce11178d1f3` | Wilzenweg | ETW30 | – | –/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563349,5944747]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.647649/9.958375) · [OSM](https://www.openstreetmap.org/way/1211705525) |
| `seg_cf3b3058902f3ab7` | Vielohweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 1 Unfall mit Radbeteiligung 2021–2025, Schule/Kita in 18 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562532,5943662]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.638001/9.945799) · [OSM](https://www.openstreetmap.org/way/1166229249) |
| `seg_fa9a41fff47f2219` | Kieler Straße | GOW30 | D1 | 2/0/0 | 0.74 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 63 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562189,5936651]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.575030/9.939205) · [OSM](https://www.openstreetmap.org/way/1352769094) |

## Lizenz

Abschnitte und Gestaltungsmerkmale aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale (Tempo, Verkehrsmengen): Freie und Hansestadt Hamburg, dl-de/by-2.0; Einwohner: Zensus 2022, dl-de/by-2.0; Unfälle: © Statistische Ämter des Bundes und der Länder, Unfallatlas, dl-de/by-2.0 (nur Summen je Abschnitt). Orthophotos: LGV Hamburg, dl-de/by-2.0. Panoramax-Bilder: Lizenz je Bild.

