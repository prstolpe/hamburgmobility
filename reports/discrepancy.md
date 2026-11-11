# Diskrepanz und Priorisierung – Stufe 8

Erzeugt: 2026-11-11T21:10:51+00:00 von `pipeline/s08_discrepancy.py`, rules.yaml 0.20.0. Nicht amtlicher Entwurf. Top 30: `reports/priority_top30.md`.

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| Stärken 0–3 | ok | disc_speed/design/use |
| Priorität 0–3 | ok | 32353 Werte |
| Typ genau bei Diskrepanz | ok | disc_type gesetzt ⇔ Ursache vorhanden ⇔ Stärke > 0 |
| Unfälle vollständig zugeordnet | ok | 16961 von 17534 Unfällen (Fuß/Rad) einem Abschnitt zugeordnet |
| keine Einzelunfälle im Ergebnis | ok | nur Summen je Abschnitt |

## Kennzahlen

- Bewertet: 34 702 Abschnitte im Arbeitsgebiet (4387.3 km), davon 33 712 in Hamburg (7 Bezirke) (4240.4 km); Grundlage cat_final.
- Mit Diskrepanz (Stärke > 0): 14 690 Abschnitte, 1683.0 km (38.4 % der Länge).
- Nicht prüfbar (keine Dimension entscheidbar): 2 349 Abschnitte.
- Anbaufreie GOW50 (Flag gow50_anbaufrei, S-FEAT-12, F23): 25 Abschnitte (17.9 km), davon 13 mit Hinweis statt Tempo-Stärke (Ist ab 60 km/h, D-SPD-01 anbaufrei_hint).
- „kein baulicher Radweg“ (D-DES-01, Ist-Führung S-FEAT-13): 343 Abschnitte (38.4 km), davon mit Parallelroute im Soll-Radnetz (Gewicht 0,5, S-FEAT-11) 101 Abschnitte (15.7 km); Radweg nur aus dem Straßen-Tag (track_tag_only, Prüfliste reports/ist_facility.md): 107.7 km.

### Stärke je Dimension (Abschnitte im Arbeitsgebiet)

Halbe Stufen nur in der Gestaltung (severity_if, F21).

| Dimension | Regel | 0 | 0,5 | 1 | 1,5 | 2 | 2,5 | 3 | nicht prüfbar |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Tempo | D-SPD-01 | 19242 | 0 | 175 | 0 | 12101 | 0 | 214 | 2970 |
| Gestaltung | D-DES-01 | 16512 | 49 | 5672 | 35 | 295 | 17 | 40 | 12082 |
| Nutzung | D-USE-01 | 3251 | 0 | 225 | 0 | 181 | 0 | 315 | 30730 |

### Gestaltung: Häufigkeit der Verstöße und unbekannte Prüfungen

Fehlende OSM-Tags gelten als unbekannt, nicht als Verstoß (S-FEAT-10).

| Soll | Prüfung | Verstoß | kein Verstoß | unbekannt | Anteil unbekannt |
| --- | --- | ---: | ---: | ---: | ---: |
| GOW50 | cycling: kein baulicher Radweg | 343 | 1537 | 105 | 5.3 % |
| GOW50 | cycle_lanes_allowed: Radfahr- oder Schutzstreifen | 160 | 1697 | 128 | 6.4 % |
| GOW50 | parking_along_carriageway: Parken längs der Fahrbahn | 69 | 862 | 1054 | 53.1 % |
| GOW50 | median_if_lanes_per_dir_gte: mehrere Fahrstreifen je Richtung ohne Mitteltrennung | 792 | 1070 | 123 | 6.2 % |
| GOW30 | cycling: Radverkehr auf der Fahrbahn ohne Radfahrstreifen | 529 | 4383 | 91 | 1.8 % |
| GOW30 | centre_line: Mittelmarkierung | 25 | 141 | 4837 | 96.7 % |
| ETW30 | cycling: baulicher Radweg statt Mischverkehr | 3749 | 11800 | 9920 | 38.9 % |
| ETW30 | cycle_lanes_allowed: Radfahr- oder Schutzstreifen | 874 | 14218 | 10377 | 40.7 % |
| ETW_ERF | cycling: baulicher Radweg statt Mischverkehr | 11 | 160 | 1604 | 90.4 % |

Nutzung (D-USE-01): DTV bekannt für 5 829 von 34 702 Abschnitten (nur Hauptverkehrsstraßen, Stand 2019); geprüft nur für Kategorien mit max_dtv (GOW30).

### Verteilung der Diskrepanztypen je Kategorie (Arbeitsgebiet)

| Soll | D1 | D2 | D3 | keine | nicht prüfbar | Summe |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SW | 0 (0.0 km) | 0 (0.0 km) | 0 (0.0 km) | 0 (0.0 km) | 470 (189.2 km) | 470 (189.2 km) |
| GOW50 | 105 (14.6 km) | 997 (118.9 km) | 88 (14.1 km) | 794 (94.7 km) | 1 (0.1 km) | 1985 (242.4 km) |
| GOW30 | 4374 (441.5 km) | 40 (4.4 km) | 489 (55.5 km) | 96 (12.0 km) | 4 (0.1 km) | 5003 (513.5 km) |
| ETW30 | 8526 (1029.4 km) | 0 (0.0 km) | 0 (0.0 km) | 15643 (2148.8 km) | 1300 (146.0 km) | 25469 (3324.3 km) |
| ETW_ERF | 71 (4.5 km) | 0 (0.0 km) | 0 (0.0 km) | 1130 (89.1 km) | 574 (24.3 km) | 1775 (118.0 km) |
| **alle** | 13076 (1490.1 km) | 1037 (123.3 km) | 577 (69.6 km) | 17663 (2344.6 km) | 2349 (359.7 km) | 34702 (4387.3 km) |

### Diskrepanztypen je Bezirk (km-Anteile; – = keine Diskrepanz oder nicht prüfbar)

| Bezirk | Abschnitte | km | D1 | D2 | D3 | – |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 4 886 | 620.5 | 28 % | 3 % | 2 % | 66 % |
| Bergedorf | 1 957 | 209.3 | 29 % | 3 % | 2 % | 67 % |
| Eimsbüttel | 4 004 | 470.4 | 34 % | 3 % | 1 % | 62 % |
| Hamburg-Mitte | 6 839 | 881.3 | 43 % | 4 % | 2 % | 51 % |
| Hamburg-Nord | 5 136 | 563.3 | 36 % | 2 % | 1 % | 60 % |
| Harburg | 3 348 | 465.2 | 28 % | 2 % | 3 % | 67 % |
| Wandsbek | 7 542 | 1 030.4 | 33 % | 2 % | 1 % | 64 % |
| **gesamt** | 33 712 | 4 240.4 | 34 % | 3 % | 2 % | 61 % |

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
| `seg_322c9c18d2a9b4a8` | Altona | Brandstücken | ETW30 | D1 | 2/0/– | 0.53 | Soll Quartiersstraße, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 74 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556301,5937305]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.581572/9.850412) · [OSM](https://www.openstreetmap.org/way/1556743411) |
| `seg_6e3ca11f454c74e0` | Altona | Palmaille | GOW50 | D2 | 0/1/– | 0.04 | Soll Stadtmagistrale, kein baulicher Radweg, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561938,5933460]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546381/9.934777) · [OSM](https://www.openstreetmap.org/way/209827367) |
| `seg_7cedee7b13f61148` | Altona | Osdorfer Landstraße | GOW30 | D1 | 2/0/0 | 0.17 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556416,5936277]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572318/9.851967) · [OSM](https://www.openstreetmap.org/way/861135582) |
| `seg_2ad11cad361a65f3` | Bergedorf | Mary-Marcus-Kehre | ETW_ERF | – | 0/–/– | 0.00 | Soll Aufenthaltsstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 147 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578148,5927017]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.486319/10.177777) · [OSM](https://www.openstreetmap.org/way/528172425) |
| `seg_475a677a7cf94c54` | Bergedorf | Am Langberg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577659,5929706]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.510555/10.171068) · [OSM](https://www.openstreetmap.org/way/264095717) |
| `seg_1c1cceed9c732963` | Eimsbüttel | Henriettenstraße | ETW30 | D1 | 0/1/– | 0.72 | Soll Quartiersstraße, baulicher Radweg statt Mischverkehr, 2 Unfälle mit Radbeteiligung 2021–2025, Schule/Kita in 53 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563345,5936547]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.573959/9.956635) · [OSM](https://www.openstreetmap.org/way/143710358) |
| `seg_ba2f4a7ff187c614` | Eimsbüttel | Julius-Vosseler-Straße | ETW30 | D1 | 2/1/– | 0.91 | Soll Quartiersstraße, heute 50 km/h (Soll 30), baulicher Radweg statt Mischverkehr, 1 Unfall mit Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562619,5938610]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.592584/9.946089) · [OSM](https://www.openstreetmap.org/way/30076869) |
| `seg_cb29280c02e901a3` | Eimsbüttel | Halstenbeker Weg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 1 Unfall mit Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558174,5941434]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.618479/9.879469) · [OSM](https://www.openstreetmap.org/way/1306480196) |
| `seg_cbe71ae6abf8f089` | Eimsbüttel | Duvenacker | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560548,5941400]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.617904/9.915347) · [OSM](https://www.openstreetmap.org/way/127871521) |
| `seg_09e3f78d54235afd` | Hamburg-Mitte | Norderkirchenweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557233,5931748]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.531529/9.863471) · [OSM](https://www.openstreetmap.org/way/4265785) |
| `seg_0aae7f75e01d651d` | Hamburg-Mitte | Neßdeich | GOW30 | D1 | 2/0/– | 0.16 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556540,5932205]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.535706/9.853106) · [OSM](https://www.openstreetmap.org/way/834615551) |
| `seg_1bc631cc660cccc0` | Hamburg-Mitte | Großer Grasbrook | ETW30 | D1 | 2/0/– | 0.56 | Soll Quartiersstraße, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 105 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565868,5932803]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.539993/9.993945) · [OSM](https://www.openstreetmap.org/way/1524097911) |
| `seg_8c0f0461c1f4548a` | Hamburg-Mitte | Neuenfelder Straße | GOW30 | D1 | 2/0/0 | 0.88 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), 1 Unfall mit Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567467,5927438]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.491576/10.016916) · [OSM](https://www.openstreetmap.org/way/606833630) |
| `seg_b53736d1d4395bb8` | Hamburg-Mitte | Hopfenstraße | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, 2 Unfälle mit Fuß-/Radbeteiligung (Rad 1, Fuß 2) 2021–2025, Schule/Kita in 93 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564016,5933687]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.548167/9.966184) · [OSM](https://www.openstreetmap.org/way/1328554121) |
| `seg_c4fc0b3320d31b81` | Hamburg-Mitte | – | ETW30 | D1 | 2/–/– | 0.07 | Soll Quartiersstraße, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572918,5932846]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.539452/10.100323) · [OSM](https://www.openstreetmap.org/way/298844288) |
| `seg_27058396905dede6` | Hamburg-Nord | Fiefstücken | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566596,5939658]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.601514/10.006396) · [OSM](https://www.openstreetmap.org/way/8153228) |
| `seg_5d571eb609277d9a` | Hamburg-Nord | Ochsenweberstraße | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566973,5947608]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.672913/10.013802) · [OSM](https://www.openstreetmap.org/way/204052341) |
| `seg_6291b5588c1d614e` | Hamburg-Nord | Wiesendamm | ETW30 | D1 | 2/0/– | 1.26 | Soll Quartiersstraße, heute 50 km/h (Soll 30), 3 Unfälle mit Radbeteiligung 2021–2025, im Radnetz | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569224,5938045]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.586673/10.045739) · [OSM](https://www.openstreetmap.org/way/136788530) |
| `seg_d533d3aa8a0a0ad2` | Hamburg-Nord | Rotbuchenstieg | ETW30 | – | 0/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 110 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567418,5940532]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.609257/10.018998) · [OSM](https://www.openstreetmap.org/way/4770800) |
| `seg_fdd705374056948a` | Hamburg-Nord | Rathenaustraße | ETW30 | – | –/0/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 101 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565945,5940110]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.605656/9.996652) · [OSM](https://www.openstreetmap.org/way/694340074) |
| `seg_0b5f509d2a553560` | Harburg | Beerentalweg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562290,5921939]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.442792/9.937802) · [OSM](https://www.openstreetmap.org/way/152955441) |
| `seg_444c72f5b35574ed` | Harburg | Stader Straße | GOW30 | D1 | 2/0/– | 0.03 | Soll Stadtstraße 30, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562228,5925073]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470966/9.937501) · [OSM](https://www.openstreetmap.org/way/1212378933) |
| `seg_c6840595d32857f7` | Harburg | Baererstraße | ETW_ERF | – | 0/–/– | 0.00 | Soll Aufenthaltsstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 11 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565077,5923151]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.453352/9.980004) · [OSM](https://www.openstreetmap.org/way/697815153) |
| `seg_3fd9e8765631584d` | Wandsbek | Stephanstraße | ETW30 | D1 | 0/1/– | 0.36 | Soll Quartiersstraße, baulicher Radweg statt Mischverkehr, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 106 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571798,5938186]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.587596/10.084650) · [OSM](https://www.openstreetmap.org/way/10067023) |
| `seg_7a6b1f4087aba9d0` | Wandsbek | Schusterkoppel | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571151,5947323]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.669800/10.076963) · [OSM](https://www.openstreetmap.org/way/24242409) |
| `seg_9e7c4d81279c518d` | Wandsbek | Hauke-Haien-Weg | ETW30 | – | 0/–/– | 0.00 | Soll Quartiersstraße, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577776,5938528]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.589819/10.175019) · [OSM](https://www.openstreetmap.org/way/8326590) |
| `seg_bbf4c376ff4931c2` | Wandsbek | Holstenhofweg | GOW50 | D2 | 0/1/– | 0.30 | Soll Stadtmagistrale, mehrere Fahrstreifen je Richtung ohne Mitteltrennung, keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 118 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573033,5937165]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.578251/10.103070) · [OSM](https://www.openstreetmap.org/way/324687481) |
| `seg_cae86131cc988625` | Wandsbek | Lüdmoor | ETW30 | D1 | 2/0/– | 0.23 | Soll Quartiersstraße, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025 | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572352,5942493]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.626230/10.094018) · [OSM](https://www.openstreetmap.org/way/53187961) |
| `seg_cf16e0cfd303f62c` | Wandsbek | Overland | ETW30 | D1 | 2/0/– | 0.58 | Soll Quartiersstraße, heute 50 km/h (Soll 30), keine Unfälle mit Fuß-/Radbeteiligung 2021–2025, Schule/Kita in 112 m | [Orthophoto](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573776,5941462]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.616759/10.115301) · [OSM](https://www.openstreetmap.org/way/151819846) |

## Lizenz

Abschnitte und Gestaltungsmerkmale aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale (Tempo, Verkehrsmengen): Freie und Hansestadt Hamburg, dl-de/by-2.0; Einwohner: Zensus 2022, dl-de/by-2.0; Unfälle: © Statistische Ämter des Bundes und der Länder, Unfallatlas, dl-de/by-2.0 (nur Summen je Abschnitt). Orthophotos: LGV Hamburg, dl-de/by-2.0. Panoramax-Bilder: Lizenz je Bild.

