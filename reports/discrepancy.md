# Diskrepanz und Priorisierung – Stufe 8

Erzeugt: 2026-11-04T22:30:21+00:00 von `pipeline/s08_discrepancy.py`, rules.yaml 0.13.0. Nicht amtlicher Entwurf. Top 30: `reports/priority_top30.md`.

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| Stärken 0–3 | ok | disc_speed/design/use |
| Priorität 0–3 | ok | 31271 Werte |
| Typ genau bei Diskrepanz | ok | disc_type gesetzt ⇔ Ursache vorhanden ⇔ Stärke > 0 |
| Unfälle vollständig zugeordnet | ok | 16961 von 17534 Unfällen (Fuß/Rad) einem Abschnitt zugeordnet |
| keine Einzelunfälle im Ergebnis | ok | nur Summen je Abschnitt |

## Kennzahlen

- Bewertet: 34 702 Abschnitte im Arbeitsgebiet (4387.3 km), davon 33 712 in Hamburg (7 Bezirke) (4240.4 km); Grundlage cat_final.
- Mit Diskrepanz (Stärke > 0): 14 371 Abschnitte, 1605.4 km (36.6 % der Länge).
- Nicht prüfbar (keine Dimension entscheidbar): 3 431 Abschnitte.

### Stärke je Dimension (Abschnitte im Arbeitsgebiet)

| Dimension | Regel | 0 | 1 | 2 | 3 | nicht prüfbar |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Tempo | D-SPD-01 | 17765 | 209 | 12426 | 193 | 4109 |
| Gestaltung | D-DES-01 | 16937 | 4933 | 200 | 51 | 12581 |
| Nutzung | D-USE-01 | 3172 | 291 | 236 | 425 | 30578 |

### Gestaltung: Häufigkeit der Verstöße und unbekannte Prüfungen

Fehlende OSM-Tags gelten als unbekannt, nicht als Verstoß (S-FEAT-10).

| Soll | Prüfung | Verstoß | kein Verstoß | unbekannt | Anteil unbekannt |
| --- | --- | ---: | ---: | ---: | ---: |
| GOW50 | cycling: kein baulicher Radweg | 370 | 1244 | 129 | 7.4 % |
| GOW50 | cycle_lanes_allowed: Radfahr- oder Schutzstreifen | 118 | 1496 | 129 | 7.4 % |
| GOW50 | parking_along_carriageway: Parken längs der Fahrbahn | 56 | 707 | 980 | 56.2 % |
| GOW50 | median_if_lanes_per_dir_gte: mehrere Fahrstreifen je Richtung ohne Mitteltrennung | 657 | 980 | 106 | 6.1 % |
| GOW30 | cycling: Radverkehr auf der Fahrbahn ohne Radfahrstreifen | 630 | 4379 | 114 | 2.2 % |
| GOW30 | centre_line: Mittelmarkierung | 19 | 131 | 4973 | 97.1 % |
| ETW30 | cycling: baulicher Radweg statt Mischverkehr | 2748 | 12456 | 10387 | 40.6 % |
| ETW30 | cycle_lanes_allowed: Radfahr- oder Schutzstreifen | 888 | 14316 | 10387 | 40.6 % |
| ETW_ERF | cycling: baulicher Radweg statt Mischverkehr | 0 | 161 | 1614 | 90.9 % |

Nutzung (D-USE-01): DTV bekannt für 5 829 von 34 702 Abschnitten (nur Hauptverkehrsstraßen, Stand 2019); geprüft nur für Kategorien mit max_dtv (GOW30).

### Verteilung der Diskrepanztypen je Kategorie (Arbeitsgebiet)

| Soll | D1 | D2 | D3 | keine | nicht prüfbar | Summe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SW | 0 (0.0 km) | 0 (0.0 km) | 0 (0.0 km) | 0 (0.0 km) | 470 (189.2 km) | 470 (189.2 km) |
| GOW50 | 121 (19.2 km) | 850 (89.7 km) | 110 (27.8 km) | 661 (84.5 km) | 1 (0.1 km) | 1743 (221.3 km) |
| GOW30 | 4419 (435.6 km) | 35 (3.4 km) | 595 (75.4 km) | 72 (9.0 km) | 2 (0.0 km) | 5123 (523.4 km) |
| ETW30 | 8129 (945.4 km) | 0 (0.0 km) | 0 (0.0 km) | 16021 (2218.8 km) | 1441 (171.3 km) | 25591 (3335.5 km) |
| ETW_ERF | 112 (8.9 km) | 0 (0.0 km) | 0 (0.0 km) | 146 (9.6 km) | 1517 (99.4 km) | 1775 (118.0 km) |
| **alle** | 12781 (1409.1 km) | 885 (93.1 km) | 705 (103.2 km) | 16900 (2321.8 km) | 3431 (460.1 km) | 34702 (4387.3 km) |

### Diskrepanztypen je Bezirk (km-Anteile; – = keine Diskrepanz oder nicht prüfbar)

| Bezirk | Abschnitte | km | D1 | D2 | D3 | – |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 4 886 | 620.5 | 25 % | 2 % | 3 % | 70 % |
| Bergedorf | 1 957 | 209.3 | 25 % | 2 % | 2 % | 71 % |
| Eimsbüttel | 4 004 | 470.4 | 32 % | 2 % | 2 % | 64 % |
| Hamburg-Mitte | 6 839 | 881.3 | 41 % | 3 % | 4 % | 52 % |
| Hamburg-Nord | 5 136 | 563.3 | 36 % | 2 % | 2 % | 61 % |
| Harburg | 3 348 | 465.2 | 27 % | 2 % | 3 % | 68 % |
| Wandsbek | 7 542 | 1 030.4 | 31 % | 2 % | 1 % | 66 % |
| **gesamt** | 33 712 | 4 240.4 | 32 % | 2 % | 2 % | 63 % |

## Unfälle (Unfallatlas)

| Jahr | Unfälle mit Personenschaden in Hamburg |
| --- | ---: |
| 2021 | 6 397 |
| 2022 | 7 174 |
| 2023 | 7 332 |
| 2024 | 7 031 |
| 2025 | 7 057 |

- Unfälle mit Fuß- oder Radbeteiligung in Hamburg: 17 534; davon 16 961 einem Abschnitt zugeordnet (höchstens 15 m entfernt), 573 nicht (kein Abschnitt im Umkreis, z. B. Unfälle auf Wegen, Plätzen oder Parkplätzen außerhalb des Kfz-Netzes).
- Im Arbeitsgebiet: 16 543 Unfälle auf 8 413 Abschnitten; davon 1 700 mit Getöteten oder Schwerverletzten.
- Gespeichert werden nur Summen je Abschnitt (crashes_ped_cyc, crashes_ped, crashes_cyc, crashes_severe_fatal, crash_weighted). Unfälle an Knoten zählen bei genau einem anliegenden Abschnitt.
- Unfallatlas enthält nur polizeilich erfasste Unfälle mit Personenschaden; Alleinunfälle von Radfahrenden sind untererfasst.

## Stichprobe (30 zufällige Abschnitte mit Bewertung in Hamburg (7 Bezirke), nach Bezirk geschichtet, Seed 42)

| segment_id | Bezirk | Name | Soll | Typ | Stärke T/G/N | Priorität | Begründung | Links |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- |
| `seg_0c4098037ee6dd9f` | Altona | Baurs Park | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553797,5934595]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.557479/9.812132) · [OSM](https://www.openstreetmap.org/way/636632439) |
| `seg_337e0bab04a62db1` | Altona | Klövensteenweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, 1 Unfall mit Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[550564,5937886]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.587374/9.763852) · [OSM](https://www.openstreetmap.org/way/132414980) |
| `seg_710b7ef2e0b432af` | Altona | Bahrenfelder Chaussee | GOW30 | D1 | 2/0/0 | 1.10 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), 3 Unfälle mit Fuß-/Radbeteiligung (Rad 2, Fuß 1) 2021–2025, davon 1 mit Getöteten/Schwerverletzten | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560843,5935418]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564101/9.918636) · [OSM](https://www.openstreetmap.org/way/687462783) |
| `seg_7f6ce35f9e41e379` | Altona | Holstenstraße | GOW30 | D1 | 2/0/3 | 0.49 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), 31 000 Kfz/Tag (DTV 2019) über 10 000, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562751,5935107]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.561089/9.947375) · [OSM](https://www.openstreetmap.org/way/1370704080) |
| `seg_34a178c7e5ca0cb9` | Bergedorf | Holtenklinker Straße / Rothenhauschaussee | GOW50 | – | 0/0/– | 0.00 | Soll Stadtmagistrale, 1 Unfall mit Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[582078,5926200]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.478374/10.236767) · [OSM](https://www.openstreetmap.org/way/212269619) |
| `seg_56b1e67657df37eb` | Bergedorf | Richard-Linde-Weg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 56 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579081,5928689]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.501201/10.192253) · [OSM](https://www.openstreetmap.org/way/158098464) |
| `seg_1cc6f3ba9463d373` | Eimsbüttel | Osterfeldstraße | GOW30 | D1 | 2/0/0 | 0.61 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 68 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563870,5939389]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.599438/9.965145) · [OSM](https://www.openstreetmap.org/way/308317373) |
| `seg_be03688885b26b0e` | Eimsbüttel | Kieler Straße | GOW30 | D1 | 2/0/0 | 1.55 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), 4 Unfälle mit Fuß-/Radbeteiligung (Rad 3, Fuß 2) 2021–2025, davon 1 mit Getöteten/Schwerverletzten, Schule/Kita in 22 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561914,5937172]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.579746/9.935153) · [OSM](https://www.openstreetmap.org/way/733544406) |
| `seg_ce1e4a5cafa62db3` | Eimsbüttel | Oldesloer Straße | GOW50 | D2 | 0/1/– | 0.02 | Soll Stadtmagistrale, kein baulicher Radweg, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562769,5945060]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.650531/9.949655) · [OSM](https://www.openstreetmap.org/way/749892946) |
| `seg_cf0e0ce11178d1f3` | Eimsbüttel | Wilzenweg | ETW30 | – | –/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563349,5944747]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.647649/9.958375) · [OSM](https://www.openstreetmap.org/way/1211705525) |
| `seg_0a1de293e9047cb0` | Hamburg-Mitte | Willy-Brandt-Straße | GOW30 | D1 | 2/0/0 | 0.10 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565822,5933613]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.547280/9.993419) · [OSM](https://www.openstreetmap.org/way/1012865752) |
| `seg_0af7274411d3047f` | Hamburg-Mitte | Mannesallee | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 13 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565572,5929933]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.514242/9.988875) · [OSM](https://www.openstreetmap.org/way/32983726) |
| `seg_1c57093578f2e955` | Hamburg-Mitte | Neuer Korbmachersand | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556293,5931656]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.530806/9.849267) · [OSM](https://www.openstreetmap.org/way/4887136) |
| `seg_8eb3c8ae5ea35fbc` | Hamburg-Mitte | Reeperbahn | GOW30 | D3 | 2/1/3 | 2.14 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), Radverkehr auf der Fahrbahn ohne Radfahrstreifen, 32 000 Kfz/Tag (DTV 2019) über 10 000, 1 Unfall mit Radbeteiligung 2021–2025, davon 1 mit Getöteten/Schwerverletzten, im Radnetz | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563376,5933858]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.549786/9.956566) · [OSM](https://www.openstreetmap.org/way/1045534398) |
| `seg_b8c3c2b87580ae68` | Hamburg-Mitte | Roßweg | ETW30 | D1 | 2/0/– | 0.00 | Soll Quartiersstraße, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562481,5931073]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.524859/9.942495) · [OSM](https://www.openstreetmap.org/way/23573960) |
| `seg_c84d83048e482a5d` | Hamburg-Mitte | Veddeler Damm | GOW50 | D2 | 0/1/– | 0.00 | Soll Stadtmagistrale, kein baulicher Radweg, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564940,5931428]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.527755/9.979666) · [OSM](https://www.openstreetmap.org/way/378233719) |
| `seg_0b0b47063899b7fe` | Hamburg-Nord | Rübenkamp | ETW30 | D1 | 2/1/– | 0.17 | Soll Quartiersstraße, heute 50 km/h (Soll 30), baulicher Radweg statt Mischverkehr, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568476,5939993]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.604284/10.034875) · [OSM](https://www.openstreetmap.org/way/983618750) |
| `seg_2746706c6a515287` | Hamburg-Nord | Erlenkamp | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 1 Unfall mit Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567589,5935911]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.567715/10.020582) · [OSM](https://www.openstreetmap.org/way/4018069) |
| `seg_5e8cb35997194751` | Hamburg-Nord | Brödermannsweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 5 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564678,5940111]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.605820/9.977509) · [OSM](https://www.openstreetmap.org/way/23414143) |
| `seg_649d3b34c18ac7ce` | Hamburg-Nord | Wittekopsweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566746,5944318]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.643375/10.009664) · [OSM](https://www.openstreetmap.org/way/26471537) |
| `seg_d811981e9cc6ebf7` | Hamburg-Nord | Breitenfelder Straße | GOW30 | D1 | 2/0/0 | 1.45 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), 2 Unfälle mit Radbeteiligung 2021–2025, Schule/Kita in 27 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564578,5938013]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.586976/9.975562) · [OSM](https://www.openstreetmap.org/way/885624894) |
| `seg_47dc403c2c2b11ad` | Harburg | Rönneburger Straße | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 90 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566090,5921669]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.439905/9.994952) · [OSM](https://www.openstreetmap.org/way/153142456) |
| `seg_d119d20f28523d79` | Harburg | Neugrabener Bahnhofstraße | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556572,5923756]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.459768/9.852060) · [OSM](https://www.openstreetmap.org/way/46721345) |
| `seg_f20753a3df6f4e86` | Harburg | Waldschlucht | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556968,5923046]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.453347/9.857897) · [OSM](https://www.openstreetmap.org/way/6228564) |
| `seg_42b69e81c84b3026` | Wandsbek | Trakehner Kehre | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 77 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572461,5942412]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.625487/10.095646) · [OSM](https://www.openstreetmap.org/way/225674434) |
| `seg_801f5d28919c115c` | Wandsbek | Wandsbeker Chaussee | GOW30 | D1 | 2/0/0 | 0.73 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 70 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568854,5935784]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.566407/10.039651) · [OSM](https://www.openstreetmap.org/way/777458783) |
| `seg_88faf105cbf4fff4` | Wandsbek | Eichberg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577500,5941296]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.614734/10.171546) · [OSM](https://www.openstreetmap.org/way/734268258) |
| `seg_a4b708fdf5bc9582` | Wandsbek | Karlshöher Weg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575207,5943076]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.631067/10.137313) · [OSM](https://www.openstreetmap.org/way/4386548) |
| `seg_b16f6cd9105180a5` | Wandsbek | Saseler Mühlenweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573140,5946526]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.662361/10.106883) · [OSM](https://www.openstreetmap.org/way/41879445) |
| `seg_d309b99ff4a096b6` | Wandsbek | Altmühlweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 1 Unfall mit Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573462,5944137]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.640842/10.111190) · [OSM](https://www.openstreetmap.org/way/493495726) |

## Lizenz

Abschnitte und Gestaltungsmerkmale aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale (Tempo, Verkehrsmengen): Freie und Hansestadt Hamburg, dl-de/by-2.0; Einwohner: Zensus 2022, dl-de/by-2.0; Unfälle: © Statistische Ämter des Bundes und der Länder, Unfallatlas, dl-de/by-2.0 (nur Summen je Abschnitt). Orthophotos: LGV Hamburg, dl-de/by-2.0. Panoramax-Bilder: Lizenz je Bild.

