# Diskrepanz und Priorisierung – Stufe 8

Erzeugt: 2026-11-07T15:08:10+00:00 von `pipeline/s08_discrepancy.py`, rules.yaml 0.16.0. Nicht amtlicher Entwurf. Top 30: `reports/priority_top30.md`.

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| Stärken 0–3 | ok | disc_speed/design/use |
| Priorität 0–3 | ok | 32322 Werte |
| Typ genau bei Diskrepanz | ok | disc_type gesetzt ⇔ Ursache vorhanden ⇔ Stärke > 0 |
| Unfälle vollständig zugeordnet | ok | 16961 von 17534 Unfällen (Fuß/Rad) einem Abschnitt zugeordnet |
| keine Einzelunfälle im Ergebnis | ok | nur Summen je Abschnitt |

## Kennzahlen

- Bewertet: 34 702 Abschnitte im Arbeitsgebiet (4387.3 km), davon 33 712 in Hamburg (7 Bezirke) (4240.4 km); Grundlage cat_final.
- Mit Diskrepanz (Stärke > 0): 14 207 Abschnitte, 1587.4 km (36.2 % der Länge).
- Nicht prüfbar (keine Dimension entscheidbar): 2 380 Abschnitte.

### Stärke je Dimension (Abschnitte im Arbeitsgebiet)

| Dimension | Regel | 0 | 1 | 2 | 3 | nicht prüfbar |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Tempo | D-SPD-01 | 18952 | 208 | 12386 | 186 | 2970 |
| Gestaltung | D-DES-01 | 17107 | 4835 | 170 | 10 | 12580 |
| Nutzung | D-USE-01 | 3190 | 288 | 235 | 423 | 30566 |

### Gestaltung: Häufigkeit der Verstöße und unbekannte Prüfungen

Fehlende OSM-Tags gelten als unbekannt, nicht als Verstoß (S-FEAT-10).

| Soll | Prüfung | Verstoß | kein Verstoß | unbekannt | Anteil unbekannt |
| --- | --- | ---: | ---: | ---: | ---: |
| GOW50 | cycling: kein baulicher Radweg | 124 | 1576 | 44 | 2.5 % |
| GOW50 | cycle_lanes_allowed: Radfahr- oder Schutzstreifen | 120 | 1496 | 128 | 7.3 % |
| GOW50 | parking_along_carriageway: Parken längs der Fahrbahn | 57 | 713 | 974 | 55.8 % |
| GOW50 | median_if_lanes_per_dir_gte: mehrere Fahrstreifen je Richtung ohne Mitteltrennung | 657 | 980 | 107 | 6.1 % |
| GOW30 | cycling: Radverkehr auf der Fahrbahn ohne Radfahrstreifen | 647 | 4429 | 111 | 2.1 % |
| GOW30 | centre_line: Mittelmarkierung | 19 | 132 | 5036 | 97.1 % |
| ETW30 | cycling: baulicher Radweg statt Mischverkehr | 2696 | 12439 | 10391 | 40.7 % |
| ETW30 | cycle_lanes_allowed: Radfahr- oder Schutzstreifen | 885 | 14250 | 10391 | 40.7 % |
| ETW_ERF | cycling: baulicher Radweg statt Mischverkehr | 0 | 161 | 1614 | 90.9 % |

Nutzung (D-USE-01): DTV bekannt für 5 829 von 34 702 Abschnitten (nur Hauptverkehrsstraßen, Stand 2019); geprüft nur für Kategorien mit max_dtv (GOW30).

### Verteilung der Diskrepanztypen je Kategorie (Arbeitsgebiet)

| Soll | D1 | D2 | D3 | keine | nicht prüfbar | Summe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SW | 0 (0.0 km) | 0 (0.0 km) | 0 (0.0 km) | 0 (0.0 km) | 470 (189.2 km) | 470 (189.2 km) |
| GOW50 | 142 (25.5 km) | 737 (78.4 km) | 92 (21.8 km) | 772 (97.3 km) | 1 (0.1 km) | 1744 (223.2 km) |
| GOW30 | 4464 (438.9 km) | 37 (3.8 km) | 610 (75.3 km) | 76 (9.6 km) | 0 (0.0 km) | 5187 (527.6 km) |
| ETW30 | 8065 (939.9 km) | 0 (0.0 km) | 0 (0.0 km) | 16135 (2228.9 km) | 1326 (160.7 km) | 25526 (3329.4 km) |
| ETW_ERF | 60 (3.7 km) | 0 (0.0 km) | 0 (0.0 km) | 1132 (89.3 km) | 583 (25.0 km) | 1775 (118.0 km) |
| **alle** | 12731 (1407.9 km) | 774 (82.3 km) | 702 (97.2 km) | 18115 (2425.0 km) | 2380 (375.0 km) | 34702 (4387.3 km) |

### Diskrepanztypen je Bezirk (km-Anteile; – = keine Diskrepanz oder nicht prüfbar)

| Bezirk | Abschnitte | km | D1 | D2 | D3 | – |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 4 886 | 620.5 | 25 % | 2 % | 3 % | 70 % |
| Bergedorf | 1 957 | 209.3 | 25 % | 2 % | 2 % | 71 % |
| Eimsbüttel | 4 004 | 470.4 | 33 % | 2 % | 1 % | 64 % |
| Hamburg-Mitte | 6 839 | 881.3 | 41 % | 3 % | 4 % | 53 % |
| Hamburg-Nord | 5 136 | 563.3 | 36 % | 2 % | 2 % | 61 % |
| Harburg | 3 348 | 465.2 | 27 % | 2 % | 3 % | 68 % |
| Wandsbek | 7 542 | 1 030.4 | 31 % | 2 % | 1 % | 66 % |
| **gesamt** | 33 712 | 4 240.4 | 32 % | 2 % | 2 % | 64 % |

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
| `seg_0bc86b9702b3e9a8` | Altona | Rispenweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 9 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559003,5939229]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.598564/9.891589) · [OSM](https://www.openstreetmap.org/way/246363341) |
| `seg_324ad127426c35fb` | Altona | Scheplerstraße | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 22 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563236,5934547]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.555995/9.954591) · [OSM](https://www.openstreetmap.org/way/903042368) |
| `seg_6e4d886eeee94c38` | Altona | Hemmingstedter Weg | ETW30 | D1 | 2/1/– | 0.49 | Soll Quartiersstraße, heute 50 km/h (Soll 30), baulicher Radweg statt Mischverkehr, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 145 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557405,5935568]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.565841/9.866771) · [OSM](https://www.openstreetmap.org/way/692572020) |
| `seg_7d29c4b119f4ec91` | Altona | Rugenbarg | GOW30 | D1 | 2/0/3 | 1.33 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), 38 000 Kfz/Tag (DTV 2019) über 10 000, 2 Unfälle mit Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557923,5938032]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.587932/9.875041) · [OSM](https://www.openstreetmap.org/way/908569136) |
| `seg_2b069579f0b2abbe` | Bergedorf | Gersonweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578414,5925691]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.474362/10.181441) · [OSM](https://www.openstreetmap.org/way/153758857) |
| `seg_476166976a695c69` | Bergedorf | Auf der Bojewiese | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577827,5928889]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.503187/10.173396) · [OSM](https://www.openstreetmap.org/way/25010517) |
| `seg_1c1cceed9c732963` | Eimsbüttel | Henriettenstraße | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 2 Unfälle mit Radbeteiligung 2021–2025, Schule/Kita in 53 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563345,5936547]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.573959/9.956635) · [OSM](https://www.openstreetmap.org/way/143710358) |
| `seg_ba96cdfff8639515` | Eimsbüttel | Friedrich-Ebert-Straße / Frohmestraße | GOW50 | D2 | 0/2/– | 0.90 | Soll Stadtmagistrale, Parken längs der Fahrbahn, mehrere Fahrstreifen je Richtung ohne Mitteltrennung, 1 Unfall mit Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561764,5942486]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.627524/9.933940) · [OSM](https://www.openstreetmap.org/way/674053446) |
| `seg_cb51be3f5bfa9f8c` | Eimsbüttel | Wietersheim / Hörgensweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 2 Unfälle mit Radbeteiligung 2021–2025, Schule/Kita in 45 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559477,5941868]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.622227/9.899255) · [OSM](https://www.openstreetmap.org/way/970384364) |
| `seg_cc2dd24560798679` | Eimsbüttel | Bayernweg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564864,5943825]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.639179/9.981087) · [OSM](https://www.openstreetmap.org/way/1459903218) |
| `seg_09e3f78d54235afd` | Hamburg-Mitte | Norderkirchenweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557233,5931748]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.531529/9.863471) · [OSM](https://www.openstreetmap.org/way/4265785) |
| `seg_0aae7f75e01d651d` | Hamburg-Mitte | Neßdeich | GOW50 | – | 0/0/– | 0.00 | Soll Stadtmagistrale, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556540,5932205]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.535706/9.853106) · [OSM](https://www.openstreetmap.org/way/834615551) |
| `seg_1bc631cc660cccc0` | Hamburg-Mitte | Großer Grasbrook | ETW30 | D1 | 2/0/– | 0.56 | Soll Quartiersstraße, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 105 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565868,5932803]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.539993/9.993945) · [OSM](https://www.openstreetmap.org/way/1524097911) |
| `seg_8c2239d3c701fabd` | Hamburg-Mitte | Kreetslag | ETW30 | D1 | 2/1/– | 0.08 | Soll Quartiersstraße, heute 50 km/h (Soll 30), baulicher Radweg statt Mischverkehr, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556144,5932334]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.536910/9.847149) · [OSM](https://www.openstreetmap.org/way/261158800) |
| `seg_b5729186206591a9` | Hamburg-Mitte | Blostwiete | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 8 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572253,5933689]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.547118/10.090479) · [OSM](https://www.openstreetmap.org/way/151772500) |
| `seg_c52e38deccf8f4cf` | Hamburg-Mitte | Schiffbeker Weg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 134 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574093,5935268]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.561055/10.118621) · [OSM](https://www.openstreetmap.org/way/88803505) |
| `seg_27058396905dede6` | Hamburg-Nord | Fiefstücken | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566596,5939658]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.601514/10.006396) · [OSM](https://www.openstreetmap.org/way/8153228) |
| `seg_5d571eb609277d9a` | Hamburg-Nord | Ochsenweberstraße | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566973,5947608]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.672913/10.013802) · [OSM](https://www.openstreetmap.org/way/204052341) |
| `seg_6291b5588c1d614e` | Hamburg-Nord | Wiesendamm | ETW30 | D1 | 2/0/– | 1.26 | Soll Quartiersstraße, heute 50 km/h (Soll 30), 3 Unfälle mit Radbeteiligung 2021–2025, im Radnetz | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569224,5938045]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.586673/10.045739) · [OSM](https://www.openstreetmap.org/way/136788530) |
| `seg_d533d3aa8a0a0ad2` | Hamburg-Nord | Rotbuchenstieg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 110 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567418,5940532]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.609257/10.018998) · [OSM](https://www.openstreetmap.org/way/4770800) |
| `seg_fdd7bf103ee69f48` | Hamburg-Nord | Schwanenwik | GOW50 | – | 0/0/– | 0.00 | Soll Stadtmagistrale, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, im Radnetz | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567247,5935359]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.562790/10.015301) · [OSM](https://www.openstreetmap.org/way/363104439) |
| `seg_0b5f509d2a553560` | Harburg | Beerentalweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562290,5921939]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.442792/9.937802) · [OSM](https://www.openstreetmap.org/way/152955441) |
| `seg_444f7cf9d87f93fa` | Harburg | Milchgrund | GOW30 | D1 | 2/0/0 | 0.26 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563319,5924484]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.465541/9.953810) · [OSM](https://www.openstreetmap.org/way/711062784) |
| `seg_c6852bb5a97b2e04` | Harburg | Scheideholzweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, 1 Unfall mit Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556359,5924856]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.469678/9.849047) · [OSM](https://www.openstreetmap.org/way/183797575) |
| `seg_3fd9e8765631584d` | Wandsbek | Stephanstraße | ETW30 | D1 | 0/1/– | 0.36 | Soll Quartiersstraße, baulicher Radweg statt Mischverkehr, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 106 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571798,5938186]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.587596/10.084650) · [OSM](https://www.openstreetmap.org/way/10067023) |
| `seg_7a769a8a6fa0ad03` | Wandsbek | Berner Heerweg | GOW30 | D3 | 2/1/1 | 1.25 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), Radverkehr auf der Fahrbahn ohne Radfahrstreifen, 14 000 Kfz/Tag (DTV 2019) über 10 000, 1 Unfall mit Fußbeteiligung 2021–2025, davon 1 mit Getöteten/Schwerverletzten, Schule/Kita in 38 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575551,5943090]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.631138/10.142528) · [OSM](https://www.openstreetmap.org/way/233486003) |
| `seg_9e8b8460bc4d7110` | Wandsbek | Bültenkoppel | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570802,5946598]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.663330/10.071516) · [OSM](https://www.openstreetmap.org/way/23523354) |
| `seg_bc1a817a4a40b14a` | Wandsbek | Sandkule | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575957,5940468]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607515/10.148022) · [OSM](https://www.openstreetmap.org/way/15730909) |
| `seg_cb38187e5b71a7c8` | Wandsbek | Am Knill | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 116 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574682,5940039]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.603850/10.128649) · [OSM](https://www.openstreetmap.org/way/109508115) |
| `seg_cf209571cfecc6ce` | Wandsbek | Waldweg | GOW30 | D3 | 2/1/1 | 1.22 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), Radverkehr auf der Fahrbahn ohne Radfahrstreifen, 12 000 Kfz/Tag (DTV 2019) über 10 000, 1 Unfall mit Radbeteiligung 2021–2025, Schule/Kita in 9 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574592,5945723]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.654943/10.128663) · [OSM](https://www.openstreetmap.org/way/1543096179) |

## Lizenz

Abschnitte und Gestaltungsmerkmale aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale (Tempo, Verkehrsmengen): Freie und Hansestadt Hamburg, dl-de/by-2.0; Einwohner: Zensus 2022, dl-de/by-2.0; Unfälle: © Statistische Ämter des Bundes und der Länder, Unfallatlas, dl-de/by-2.0 (nur Summen je Abschnitt). Orthophotos: LGV Hamburg, dl-de/by-2.0. Panoramax-Bilder: Lizenz je Bild.

