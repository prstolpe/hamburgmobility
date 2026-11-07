# Soll-Querschnitt: Fahrstreifen, Lage der Radanlagen, Raumaufteilung (Stufe c06)

Erzeugt 2026-11-07T15:14:28+00:00 mit pipeline/c06_cross_section_soll.py · design_rules.yaml 0.6.0 · cycling_rules.yaml 0.7.0 · nicht amtlicher Entwurf. Regeln L-01…06, PL-01…06 und PRF-01…07 sind Annahmen bzw. Entwürfe (status draft) und vor Gebrauch fachlich zu prüfen.

Verfügbare Breite = width_p10_m der Variante Verkehrsfläche (maßgeblich); die Variante Fassade zeigt das Potenzial inklusive Vorgärten. Das gewünschte Profil enthält Gehwege (Regelmaß), die Radanlage mit Sollbreite aus Prompt 18, ÖPNV, Fahrbahn, Trennstreifen, Bäume (GOW), Ladezone bei Geschäftsnutzung und Parken nur dort, wo OSM heute Parken zeigt (Entscheidung 2026-11-06). Passt es nicht, gilt die Kaskade D1, D2, Fallback, D3, D4, D5, D6, D7 (PRF-06).

## Kurzfassung

- 36 526 Abschnitte, 4 998 km; bewertet (Profilregeln und Breite vorhanden): 3 861 km. Ohne Breite: 337 km; ohne Profilregeln: 800 km.
- passt: 2 107 km (55 % der bewerteten Länge).
- passt nach Abbau: 777 km (20 % der bewerteten Länge).
- passt nicht: 978 km (25 % der bewerteten Länge).
- Vorschlag GOW50 → GOW30 (D5): 137 Abschnitte, 26.2 km – nicht übernommen, Entscheidung über overrides/overrides.csv.
- GTFS: repräsentativer Werktag 2026-04-29 (Upload__hvv_Rohdaten_GTFS_Fpl_20260408.ZIP); Straßenbahnrouten im Feed: 0. Busfahrstreifen Soll: 13.1 km.

## km je fit_class und Straßenkategorie

| Kategorie | passt | passt nach Abbau | passt nicht | nicht bewertet | gesamt |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0.0 | 0.0 | 0.0 | 189.2 | 189.2 |
| GOW50 | 95.2 | 99.2 | 21.8 | 7.0 | 223.2 |
| GOW30 | 303.9 | 150.2 | 64.5 | 9.0 | 527.6 |
| ETW30 | 1 610.7 | 525.3 | 886.0 | 307.5 | 3 329.4 |
| ETW_ERF | 97.1 | 2.0 | 5.3 | 13.5 | 118.0 |

### Verkehrsfläche gegen Fassade (km, nur mit beiden Breiten)

| Verkehrsfläche \ Fassade | passt | passt nach Abbau | passt nicht |
| --- | ---: | ---: | ---: |
| passt | 1 886.5 | 5.7 | 2.8 |
| passt nach Abbau | 672.0 | 43.2 | 1.4 |
| passt nicht | 762.9 | 17.2 | 20.4 |

## Abbaustufen

Häufigkeit je Stufe (ein Abschnitt kann mehrere Stufen haben). Eine Stufe zählt nur, wenn sie das Profil verändert.

| Stufe | Maßnahme | Abschnitte | km | Anteil an bewerteter Länge |
| --- | --- | ---: | ---: | ---: |
| D1 | Parken entfernen | 2 162 | 320.0 | 8.3 % |
| D2 | Baumstreifen → Baumscheiben | 2 441 | 322.4 | 8.4 % |
| fallback | Fallback der Matrixzelle (Prompt 18) | 549 | 73.6 | 1.9 % |
| D3 | zweiten Kfz-Fahrstreifen streichen | 200 | 29.8 | 0.8 % |
| D4 | Rad- und Gehweg auf Mindestbreite | 8 877 | 1 420.1 | 36.8 % |
| D5 | Vorschlag GOW50 → GOW30 (C-G30-02) | 137 | 26.2 | 0.7 % |
| D6 | Flag: Einrichtungsverkehr / Durchfahrtsunterbrechung prüfen | 6 182 | 977.6 | 25.3 % |
| D7 | Flag: Radroute auf Parallelstraße verlegen | 534 | 83.8 | 2.2 % |

Letzte wirksame Stufe bei „passt nach Abbau“ (km):

D1 159.1 · D2 125.5 · fallback 16.2 · D3 28.0 · D4 443.5 · D5 4.4

## Fahrstreifen Ist → Soll (km)

Ist je Richtung aus amtlichen Fahrstreifen (sonst OSM lanes, PRF-01). Soll nach L-01…L-06; L-06 verhindert jeden Zuwachs ohne Override (eine Override-Ebene für Fahrstreifen gibt es noch nicht).

| Ist \ Soll | 1 | 1 + Bus | 2 | shared | – |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 283.8 | 0.0 | 0.0 | 2 935.3 | 84.7 |
| 2 | 266.3 | 9.4 | 49.3 | 86.1 | 83.8 |
| 3 | 88.3 | 2.1 | 17.2 | 15.4 | 14.1 |
| 4 | 20.7 | 1.1 | 7.4 | 1.7 | 6.2 |
| 5 | 2.5 | 0.0 | 0.3 | 0.5 | 0.4 |
| 6 | 0.2 | 0.0 | 0.6 | 0.1 | 0.0 |
| unbekannt | 0.7 | 0.5 | 0.0 | 408.2 | 0.0 |

Weniger Kfz-Fahrstreifen je Richtung im Soll: 416.4 km (davon an GOW50 79.4 km). Zusätzlich D3 im Profil: 29.8 km.

## Fälle D5: Vorschlag GOW50 → GOW30 (C-G30-02)

137 Abschnitte, 26.2 km. Längste 40, je Straße und Bezirk zusammengefasst:

| Straße | Bezirk | Kfz | Rad | Abschnitte | km | verfügbar m (Median) | Bedarf m (Median) | Beispiel |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Hohe-Schaar-Straße | Hamburg-Mitte | GOW50 | ERSCHL | 15 | 2.58 | 13.6 | 16.8 | `seg_041bf1bffc8768d7` |
| Elbchaussee | Altona | GOW50 | HAUPT | 4 | 1.82 | 12.1 | 16.8 | `seg_095ae2689e067006` |
| Kattwykdamm | Hamburg-Mitte | GOW50 | ERSCHL | 8 | 1.47 | 13.0 | 16.8 | `seg_1b8e45ab81ba0191` |
| Maldfeldstraße | Harburg | GOW50 | ERSCHL | 2 | 1.26 | 5.2 | 15.5 | `seg_62e6f106c665fcdc` |
| Wellingsbüttler Weg | Wandsbek | GOW50 | HAUPT | 3 | 0.95 | 14.2 | 16.8 | `seg_8232dbac21641f26` |
| Unterer Landweg | Hamburg-Mitte | GOW50 | HAUPT | 3 | 0.82 | 13.7 | 16.8 | `seg_41145b28109c17fc` |
| Hafenrandstraße | Hamburg-Mitte | GOW50 | ERSCHL | 1 | 0.77 | 14.0 | 16.8 | `seg_ce0603f23047a60c` |
| Fürstenmoordamm | Harburg | GOW50 | none | 2 | 0.74 | 12.9 | 16.8 | `seg_02452cc02f4b00d2` |
| Meiendorfer Mühlenweg | Wandsbek | GOW50 | HAUPT | 2 | 0.74 | 11.0 | 14.2 | `seg_30bb3774a6771bf5` |
| Neßdeich | Hamburg-Mitte | GOW50 | ERSCHL | 8 | 0.72 | 14.9 | 14.2 | `seg_0aae7f75e01d651d` |
| Ehestorfer Weg | Harburg | GOW50 | ERSCHL | 1 | 0.67 | 7.8 | 14.2 | `seg_aaf7eec60da1d6d1` |
| Segeberger Chaussee | Wandsbek | GOW50 | ERSCHL | 3 | 0.65 | 16.4 | 16.8 | `seg_1265f8ab675eb0e7` |
| Poppenbütteler Chaussee | Wandsbek | GOW50 | ERSCHL | 1 | 0.63 | 11.9 | 16.8 | `seg_91501613d1b165c2` |
| Farnhornweg | Altona | GOW50 | HAUPT | 4 | 0.60 | 17.0 | 16.8 | `seg_19c6219f387e811c` |
| Garstedter Weg | Eimsbüttel | GOW50 | BASIS | 5 | 0.60 | 13.9 | 16.8 | `seg_2928b89d6277a8e4` |
| Eißendorfer Waldweg | Harburg | GOW50 | HAUPT | 1 | 0.52 | 9.3 | 14.2 | `seg_896df8d623e86dbd` |
| Reinbeker Redder | Bergedorf | GOW50 | HAUPT | 1 | 0.49 | 16.2 | 16.8 | `seg_2818b7cebb47b115` |
| An der Alsterschleife | Wandsbek | GOW50 | HAUPT | 1 | 0.47 | 10.7 | 14.2 | `seg_c5db1848591c3a8f` |
| Meiendorfer Straße | Wandsbek | GOW50 | HAUPT | 5 | 0.45 | 15.9 | 16.8 | `seg_372377a05d48046f` |
| Waldweg | Wandsbek | GOW50 | HAUPT | 2 | 0.44 | 13.9 | 16.8 | `seg_33cee3733f4f13e1` |
| Garstedter Weg | Eimsbüttel | GOW50 | HAUPT | 3 | 0.39 | 13.9 | 16.8 | `seg_5318793c486e4563` |
| Saseler Chaussee | Wandsbek | GOW50 | HAUPT | 2 | 0.37 | 15.6 | 16.8 | `seg_631a440381c8a262` |
| Pinneberger Straße | Eimsbüttel | GOW50 | ERSCHL | 1 | 0.37 | 16.4 | 16.8 | `seg_5fe94056e73a9e8c` |
| Lohe | Wandsbek | GOW50 | ERSCHL | 2 | 0.36 | 13.8 | 16.8 | `seg_77776eb8d7a91a60` |
| Liebigstraße / Unterer Landweg | Hamburg-Mitte | GOW50 | HAUPT | 1 | 0.36 | 13.3 | 16.8 | `seg_2ee8229c6c588661` |
| Jüthornstraße | Wandsbek | GOW50 | HAUPT | 1 | 0.34 | 21.3 | 16.8 | `seg_fab5929161c1ead3` |
| Reiherstieg-Hauptdeich | Hamburg-Mitte | GOW50 | ERSCHL | 1 | 0.32 | 9.5 | 16.8 | `seg_698b1f7244691ed8` |
| Krohnstieg | Hamburg-Nord | GOW50 | ERSCHL | 2 | 0.31 | 16.3 | 16.8 | `seg_3d0aaec34de39593` |
| Liebigstraße | Hamburg-Mitte | GOW50 | BASIS | 1 | 0.29 | 15.2 | 16.8 | `seg_0c0b612632fa40c2` |
| Pezolddamm | Wandsbek | GOW50 | HAUPT | 1 | 0.28 | 15.3 | 14.2 | `seg_0b3867bdbe79e3c8` |
| Volksdorfer Damm | Wandsbek | GOW50 | HAUPT | 2 | 0.27 | 14.4 | 16.8 | `seg_028ae77ce0dc6098` |
| Rodigallee | Wandsbek | GOW50 | HAUPT | 2 | 0.27 | 23.0 | 16.8 | `seg_5f44df6ede1cc9ce` |
| Hannoversche Straße | Harburg | GOW50 | HAUPT | 1 | 0.27 | 16.6 | 14.2 | `seg_5ce21acd3fd8c1da` |
| Eißendorfer Waldweg | Harburg | GOW50 | ERSCHL | 1 | 0.26 | 11.7 | 14.2 | `seg_b5c783553fd19e66` |
| Altmannbrücke / Kurt-Schumacher-Allee | Hamburg-Mitte | GOW50 | ERSCHL | 1 | 0.25 | 15.3 | 16.8 | `seg_b7b3dba2f3c09dbd` |
| Reinbeker Redder | Bergedorf | GOW50 | ERSCHL | 1 | 0.24 | 21.1 | 16.8 | `seg_26c82b76b61029ab` |
| Maldfeldstraße | Harburg | GOW50 | HAUPT | 1 | 0.23 | 12.4 | 16.8 | `seg_3d552fad6c87a274` |
| Lemsahler Landstraße | Wandsbek | GOW50 | HAUPT | 1 | 0.22 | 14.4 | 16.8 | `seg_40f4235f6c8c2d16` |
| Aue-Hauptdeich / Finkenwerder Straße | Hamburg-Mitte | GOW50 | BASIS | 1 | 0.20 | 11.5 | 14.2 | `seg_92b3de74023ddec5` |
| Curslacker Neuer Deich | Bergedorf | GOW50 | HAUPT | 1 | 0.20 | 22.8 | 16.8 | `seg_b5b9db937f5fb2db` |

## Fälle D6: Flag: Einrichtungsverkehr / Durchfahrtsunterbrechung prüfen

6 182 Abschnitte, 977.6 km. Längste 40, je Straße und Bezirk zusammengefasst:

| Straße | Bezirk | Kfz | Rad | Abschnitte | km | verfügbar m (Median) | Bedarf m (Median) | Beispiel |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| (ohne Namen) | Hamburg-Mitte | ETW30 | BASIS | 8 | 4.75 | 8.4 | 9.8 | `seg_0ba8afeeda9be278` |
| Moorwerder Hauptdeich | Hamburg-Mitte | ETW30 | HAUPT | 6 | 3.42 | 8.3 | 9.0 | `seg_471bc3129ecccfdf` |
| Duvenstedter Triftweg / Langenreiher Weg | Wandsbek | ETW30 | HAUPT | 1 | 2.95 | 3.0 | 11.5 | `seg_be1fbefc540be72f` |
| Elbchaussee | Altona | GOW30 | HAUPT | 10 | 2.76 | 11.1 | 16.8 | `seg_0fb495600eaa26e8` |
| Eversween | Hamburg-Mitte | ETW30 | ERSCHL | 3 | 2.60 | 11.5 | 11.5 | `seg_1418f89bb01333ff` |
| Hohe-Schaar-Straße | Hamburg-Mitte | GOW50 | ERSCHL | 15 | 2.58 | 13.6 | 16.8 | `seg_041bf1bffc8768d7` |
| Falkensteiner Ufer | Altona | ETW30 | HAUPT | 8 | 2.29 | 6.4 | 9.0 | `seg_1b0f130473ae92f5` |
| Moorwerder Hauptdeich | Hamburg-Mitte | ETW30 | ERSCHL | 4 | 2.14 | 8.1 | 11.5 | `seg_012525751224d503` |
| Finkenwerder Süderdeich / Süderkirchenweg | Hamburg-Mitte | ETW30 | ERSCHL | 1 | 2.07 | 7.9 | 9.8 | `seg_aa01d1f1f774f9e3` |
| Wiet | Hamburg-Mitte | ETW30 | ERSCHL | 1 | 1.88 | 7.3 | 9.8 | `seg_2f0b1863a6eaabb2` |
| Elbchaussee | Altona | GOW50 | HAUPT | 4 | 1.82 | 12.1 | 16.8 | `seg_095ae2689e067006` |
| Puckaffer Weg | Wandsbek | ETW30 | ERSCHL | 8 | 1.80 | 9.1 | 10.6 | `seg_659f97f5ab7790ed` |
| Finkenrieker Hauptdeich | Hamburg-Mitte | ETW30 | ERSCHL | 5 | 1.77 | 5.5 | 9.8 | `seg_09c5ef0ea218b4ab` |
| Walter-Hammer-Weg | Bergedorf | ETW30 | HAUPT | 1 | 1.73 | 5.0 | 9.0 | `seg_791d0d6faad5e65e` |
| Niendorfer Gehege | Eimsbüttel | ETW30 | HAUPT | 2 | 1.67 | 8.8 | 10.2 | `seg_95a931e2a8b279ea` |
| Siedenfelder Weg | Hamburg-Mitte | ETW30 | HAUPT | 2 | 1.66 | 7.8 | 9.0 | `seg_7fd526806f07de8c` |
| Raakmoorgrund / Weg Nr. 651 | Hamburg-Nord | ETW30 | HAUPT | 1 | 1.65 | 6.0 | 9.0 | `seg_ecf40172d73d6546` |
| Waldweg | Wandsbek | GOW30 | BASIS | 5 | 1.57 | 13.9 | 16.8 | `seg_074d9f02a98f9463` |
| Berliner Ufer | Hamburg-Mitte | ETW30 | ERSCHL | 1 | 1.54 | 4.8 | 9.8 | `seg_b65f34b9ef2b1049` |
| Meiendorfer Straße | Wandsbek | GOW30 | HAUPT | 9 | 1.51 | 16.2 | 16.8 | `seg_107b5a7d8c2f22df` |
| Kattwykdamm | Hamburg-Mitte | GOW50 | ERSCHL | 8 | 1.47 | 13.0 | 16.8 | `seg_1b8e45ab81ba0191` |
| Am Ochsenzoll | Hamburg-Nord | ETW30 | HAUPT | 3 | 1.46 | 5.1 | 9.0 | `seg_aa8b6df36b4c4943` |
| Mesterbrooksweg | Wandsbek | ETW30 | ERSCHL | 3 | 1.46 | 8.2 | 9.8 | `seg_0f7b44ffb9b6294a` |
| Rissener Landstraße | Altona | GOW30 | HAUPT | 4 | 1.45 | 13.2 | 16.8 | `seg_01442ed9c9d6fc5f` |
| Hans-Ulrich-Höller-Weg | Bergedorf | ETW30 | BASIS | 1 | 1.41 | 5.0 | 9.8 | `seg_9c01c86026c409b4` |
| Kobberdiekskoppel / Ödenweg | Wandsbek | ETW30 | ERSCHL | 1 | 1.39 | 8.2 | 9.8 | `seg_83c6f1d534de6622` |
| Kuhtrift | Harburg | ETW30 | ERSCHL | 7 | 1.38 | 5.3 | 9.8 | `seg_200e180f02fde42e` |
| Francoper Straße | Harburg | GOW30 | ERSCHL | 3 | 1.36 | 8.4 | 14.2 | `seg_2cd77ed942e139d9` |
| Wulmsberggrund | Harburg | ETW30 | HAUPT | 3 | 1.35 | 4.4 | 9.0 | `seg_12b7e9bc1394309e` |
| Köterdamm | Hamburg-Mitte | ETW30 | ERSCHL | 2 | 1.34 | 8.0 | 9.8 | `seg_1a176f153e0174eb` |
| Ellerholzweg | Hamburg-Mitte | ETW30 | ERSCHL | 4 | 1.32 | 9.0 | 9.8 | `seg_41858456ea6919d4` |
| Hagenweg | Wandsbek | ETW30 | ERSCHL | 2 | 1.31 | 8.8 | 9.8 | `seg_b59fc543632c9b89` |
| Friedrichshulder Weg | Altona | ETW30 | HAUPT | 1 | 1.31 | 7.4 | 9.0 | `seg_e9ede1815b056b10` |
| Moorwerder Norderdeich | Hamburg-Mitte | ETW30 | HAUPT | 2 | 1.29 | 5.1 | 9.0 | `seg_1da1e89613f6cde1` |
| Finkenwerder Landscheideweg | Hamburg-Mitte | ETW30 | BASIS | 3 | 1.28 | 8.2 | 9.8 | `seg_11205afd99725fda` |
| Osterfelddeich / Kirchenaußendeichsweg | Hamburg-Mitte | ETW30 | HAUPT | 1 | 1.28 | 8.5 | 9.0 | `seg_f107760b70327da7` |
| Rahlstedter Straße | Wandsbek | GOW30 | HAUPT | 10 | 1.28 | 18.0 | 19.3 | `seg_249dcaa103e67551` |
| Stillhorner Hauptdeich | Hamburg-Mitte | ETW30 | HAUPT | 2 | 1.27 | 6.4 | 9.0 | `seg_6e9d83c097a58e71` |
| Maldfeldstraße | Harburg | GOW50 | ERSCHL | 2 | 1.26 | 5.2 | 15.5 | `seg_62e6f106c665fcdc` |
| Einlagedeich | Hamburg-Mitte | ETW30 | HAUPT | 1 | 1.24 | 7.2 | 9.0 | `seg_64a83dbfbc6d2c96` |

## Fälle D7: Flag: Radroute auf Parallelstraße verlegen

534 Abschnitte, 83.8 km. Längste 40, je Straße und Bezirk zusammengefasst:

| Straße | Bezirk | Kfz | Rad | Abschnitte | km | verfügbar m (Median) | Bedarf m (Median) | Beispiel |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Elbchaussee | Altona | GOW30 | HAUPT | 10 | 2.76 | 11.1 | 16.8 | `seg_0fb495600eaa26e8` |
| Hohe-Schaar-Straße | Hamburg-Mitte | GOW50 | ERSCHL | 15 | 2.58 | 13.6 | 16.8 | `seg_041bf1bffc8768d7` |
| Elbchaussee | Altona | GOW50 | HAUPT | 4 | 1.82 | 12.1 | 16.8 | `seg_095ae2689e067006` |
| Waldweg | Wandsbek | GOW30 | BASIS | 5 | 1.57 | 13.9 | 16.8 | `seg_074d9f02a98f9463` |
| Meiendorfer Straße | Wandsbek | GOW30 | HAUPT | 9 | 1.51 | 16.2 | 16.8 | `seg_107b5a7d8c2f22df` |
| Kattwykdamm | Hamburg-Mitte | GOW50 | ERSCHL | 8 | 1.47 | 13.0 | 16.8 | `seg_1b8e45ab81ba0191` |
| Rissener Landstraße | Altona | GOW30 | HAUPT | 4 | 1.45 | 13.2 | 16.8 | `seg_01442ed9c9d6fc5f` |
| Francoper Straße | Harburg | GOW30 | ERSCHL | 3 | 1.36 | 8.4 | 14.2 | `seg_2cd77ed942e139d9` |
| Rahlstedter Straße | Wandsbek | GOW30 | HAUPT | 10 | 1.28 | 18.0 | 19.3 | `seg_249dcaa103e67551` |
| Maldfeldstraße | Harburg | GOW50 | ERSCHL | 2 | 1.26 | 5.2 | 15.5 | `seg_62e6f106c665fcdc` |
| Pollhorner Hauptdeich | Hamburg-Mitte | GOW30 | ERSCHL | 1 | 1.24 | 8.7 | 14.2 | `seg_429717595f22897b` |
| Seehafenstraße | Harburg | GOW30 | ERSCHL | 3 | 1.20 | 12.0 | 16.8 | `seg_6c5bd4d8e45a5ae3` |
| Kieler Straße | Eimsbüttel | GOW30 | HAUPT | 5 | 1.02 | 17.3 | 19.3 | `seg_54e2f881116fa080` |
| Wellingsbüttler Weg | Wandsbek | GOW50 | HAUPT | 3 | 0.95 | 14.2 | 16.8 | `seg_8232dbac21641f26` |
| Schmidts Breite | Hamburg-Mitte | GOW30 | ERSCHL | 4 | 0.89 | 11.3 | 14.2 | `seg_4ede7ec38f7fb372` |
| Otto-Wels-Straße | Hamburg-Nord | GOW30 | HAUPT | 2 | 0.89 | 12.5 | 14.2 | `seg_8f04976664d41c67` |
| Unterer Landweg | Hamburg-Mitte | GOW50 | HAUPT | 3 | 0.82 | 13.7 | 16.8 | `seg_41145b28109c17fc` |
| Wellingsbüttler Weg | Wandsbek | GOW30 | BASIS | 7 | 0.81 | 13.7 | 19.3 | `seg_0658711bfb38f869` |
| Hafenrandstraße | Hamburg-Mitte | GOW50 | ERSCHL | 1 | 0.77 | 14.0 | 16.8 | `seg_ce0603f23047a60c` |
| Waldweg | Wandsbek | GOW30 | ERSCHL | 4 | 0.77 | 13.3 | 16.8 | `seg_4b56f559d4e0e09f` |
| Oldesloer Straße | Eimsbüttel | GOW30 | BASIS | 5 | 0.76 | 13.7 | 16.8 | `seg_00ee9ea9ee15e9e6` |
| Moorburger Straße | Harburg | GOW30 | ERSCHL | 3 | 0.76 | 14.9 | 16.8 | `seg_3315c26eadc8d159` |
| Garstedter Weg | Eimsbüttel | GOW30 | BASIS | 5 | 0.75 | 13.9 | 16.8 | `seg_31586e0ccf94c0cc` |
| Meiendorfer Mühlenweg | Wandsbek | GOW50 | HAUPT | 2 | 0.74 | 11.0 | 14.2 | `seg_30bb3774a6771bf5` |
| Meckelfelder Weg | Harburg | GOW30 | ERSCHL | 5 | 0.73 | 9.3 | 16.8 | `seg_39ef70c47c8ad7a7` |
| Poppenbütteler Chaussee | Wandsbek | GOW30 | ERSCHL | 6 | 0.73 | 9.7 | 18.1 | `seg_17f60dcf357e2a14` |
| Poppenbüttler Hauptstraße | Wandsbek | GOW30 | HAUPT | 6 | 0.72 | 13.6 | 15.4 | `seg_510dca558bd59282` |
| Aue-Hauptdeich | Hamburg-Mitte | GOW30 | BASIS | 2 | 0.72 | 12.1 | 14.2 | `seg_620f28acdc81233f` |
| Reiherstieg-Hauptdeich | Hamburg-Mitte | GOW30 | ERSCHL | 1 | 0.71 | 11.1 | 16.8 | `seg_4c3ca98a1f2942fa` |
| Volksdorfer Damm | Wandsbek | GOW30 | HAUPT | 3 | 0.71 | 17.0 | 19.3 | `seg_0e2587013a5860c3` |
| Lemsahler Landstraße | Wandsbek | GOW30 | ERSCHL | 1 | 0.70 | 10.8 | 16.8 | `seg_9a1db680f64d374e` |
| Friedhofstraße | Harburg | GOW30 | HAUPT | 5 | 0.70 | 11.6 | 16.8 | `seg_0b972cbad9999e38` |
| Ehestorfer Weg | Harburg | GOW50 | ERSCHL | 1 | 0.67 | 7.8 | 14.2 | `seg_aaf7eec60da1d6d1` |
| Nedderfeld | Hamburg-Nord | GOW30 | HAUPT | 1 | 0.67 | 17.0 | 19.3 | `seg_aa5407704b13547b` |
| Rahlstedter Straße | Wandsbek | GOW30 | BASIS | 6 | 0.66 | 18.0 | 19.3 | `seg_31be3a0f3d9cd46d` |
| Bergstedter Chaussee | Wandsbek | GOW30 | HAUPT | 7 | 0.66 | 15.5 | 16.8 | `seg_21a34d8ca88f0d1a` |
| Gazellenkamp | Eimsbüttel | GOW30 | HAUPT | 2 | 0.66 | 12.0 | 15.4 | `seg_84efc14cffb00c7b` |
| Ehestorfer Weg | Harburg | GOW30 | HAUPT | 1 | 0.65 | 9.9 | 14.2 | `seg_71f041587ef4854d` |
| Segeberger Chaussee | Wandsbek | GOW50 | ERSCHL | 3 | 0.65 | 16.4 | 16.8 | `seg_1265f8ab675eb0e7` |
| Waldweg | Wandsbek | GOW30 | HAUPT | 7 | 0.64 | 13.8 | 16.8 | `seg_3118f842ed1786fa` |

## Hinweise (Flags)

| Flag | Bedeutung | Abschnitte | km |
| --- | --- | ---: | ---: |
| `width_unknown` | keine verfügbare Breite (width_p10_m fehlt) | 3 435 | 336.9 |
| `no_profile_rules` | keine Profilregeln (SW, GOW80, ETW60 oder ohne Kategorie, PRF-04) | 2 294 | 799.6 |
| `dtv_unknown` | DTV fehlt an GOW50 – Fahrstreifen = Ist (PRF-01), confidence low | 330 | 30.3 |
| `lanes_capped_l06` | Soll-Fahrstreifen auf Ist begrenzt (L-06, kein Override) | 248 | 36.8 |
| `pl02_unchecked` | Zweirichtungsradweg: Seitenbedingung PL-02 nicht prüfbar (PRF-07) | 0 | 0.0 |
| `trees_in_parking_row` | Baumstreifen entfällt, Bäume als Baumscheiben (D2) | 2 441 | 322.4 |
| `gow30_dtv_above_profile` | GOW30 mit DTV über dem breiten CROW-Profil | 3 404 | 362.6 |
| `D6` | Flag: Einrichtungsverkehr / Durchfahrtsunterbrechung prüfen | 6 182 | 977.6 |
| `D7` | Flag: Radroute auf Parallelstraße verlegen | 534 | 83.8 |

confidence: high 3 625 km, medium 208 km, low 1 165 km

## fit_class je Bezirk (Anteil km)

| Bezirk | Abschnitte | km | passt | passt nach Abbau | passt nicht | nicht bewertet |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 4 886 | 620.5 | 40 % | 22 % | 29 % | 9 % |
| Bergedorf | 1 957 | 209.3 | 58 % | 16 % | 21 % | 6 % |
| Eimsbüttel | 4 004 | 470.4 | 54 % | 21 % | 18 % | 7 % |
| Hamburg-Mitte | 6 839 | 881.3 | 50 % | 13 % | 19 % | 18 % |
| Hamburg-Nord | 5 136 | 563.3 | 61 % | 15 % | 16 % | 8 % |
| Harburg | 3 348 | 465.2 | 40 % | 18 % | 26 % | 16 % |
| Wandsbek | 7 542 | 1 030.4 | 49 % | 21 % | 28 % | 2 % |
| ohne Bezirk | 990 | 146.9 | 4 % | 1 % | 2 % | 93 % |
| **gesamt** | 34 702 | 4 387.3 | 48 % | 18 % | 22 % | 12 % |

## Querschnitts-Skizzen (70 Profile)

reports/profiles_sample/<segment_id>.svg: 30 Zufallsabschnitte (über Bezirke verteilt, Seed 42), die 20 breitesten und die 20 engsten (verfügbare Breite). Elemente maßstäblich, blau gestrichelt die verfügbare Breite. Prüfung gegen Luftbild und Straßenbilder: Spalte „geprüft“ von Hand ausfüllen.

| Gruppe | segment_id | Straße | Bezirk | Kfz | Rad | Führung | Bedarf m | verfügbar m | Passung | Abbau | Skizze | Prüfen | geprüft |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| Zufall | `seg_0c20c4b7963908f5` | Am Sumpfgraben | Altona | ETW30 | ERSCHL | Mischverkehr | 9.8 | 7.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_0c20c4b7963908f5.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557662,5940361]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.608887/9.871528) · [OSM](https://www.openstreetmap.org/?mlat=53.608887&mlon=9.871528#map=18/53.608887/9.871528) | ☐ |
| Zufall | `seg_337e0bab04a62db1` | Klövensteenweg | Altona | ETW30 | ERSCHL | Mischverkehr | 10.8 | 13.9 | passt nach Abbau | D1 | [SVG](profiles_sample/seg_337e0bab04a62db1.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[550564,5937886]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.587374/9.763852) · [OSM](https://www.openstreetmap.org/?mlat=53.587374&mlon=9.763852#map=18/53.587374/9.763852) | ☐ |
| Zufall | `seg_7057d4d9f0b70bb4` | Manteuffelstraße | Altona | ETW30 | HAUPT | Fahrradstraße | 10.0 | 26.0 | passt | nan | [SVG](profiles_sample/seg_7057d4d9f0b70bb4.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554998,5934979]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560804/9.830326) · [OSM](https://www.openstreetmap.org/?mlat=53.560804&mlon=9.830326#map=18/53.560804/9.830326) | ☐ |
| Zufall | `seg_7ec16be77aa4f1d3` | Behnstraße | Altona | ETW30 | HAUPT | Fahrradstraße | 16.5 | 22.2 | passt | nan | [SVG](profiles_sample/seg_7ec16be77aa4f1d3.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562437,5933493]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546617/9.942317) · [OSM](https://www.openstreetmap.org/?mlat=53.546617&mlon=9.942317#map=18/53.546617/9.942317) | ☐ |
| Zufall | `seg_2ad11cad361a65f3` | Mary-Marcus-Kehre | Bergedorf | ETW_ERF | ERSCHL | Mischverkehr | 4.8 | 19.0 | passt | nan | [SVG](profiles_sample/seg_2ad11cad361a65f3.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578148,5927017]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.486319/10.177777) · [OSM](https://www.openstreetmap.org/?mlat=53.486319&mlon=10.177777#map=18/53.486319/10.177777) | ☐ |
| Zufall | `seg_4540c335d10b5685` | Ulmenhang | Bergedorf | ETW30 | ERSCHL | Mischverkehr | 9.8 | 6.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_4540c335d10b5685.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579706,5927700]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.492218/10.201413) · [OSM](https://www.openstreetmap.org/?mlat=53.492218&mlon=10.201413#map=18/53.492218/10.201413) | ☐ |
| Zufall | `seg_1cc6f3ba9463d373` | Osterfeldstraße | Eimsbüttel | GOW30 | ERSCHL | Radfahrstreifen | 24.9 | 29.1 | passt | nan | [SVG](profiles_sample/seg_1cc6f3ba9463d373.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563870,5939389]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.599438/9.965145) · [OSM](https://www.openstreetmap.org/?mlat=53.599438&mlon=9.965145#map=18/53.599438/9.965145) | ☐ |
| Zufall | `seg_c06ccbe1087fa5e5` | Binsbarg | Eimsbüttel | GOW50 | none | Radweg je Seite | 18.5 | 19.5 | passt nach Abbau | D2|D3 | [SVG](profiles_sample/seg_c06ccbe1087fa5e5.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560760,5938408]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.590985/9.917974) · [OSM](https://www.openstreetmap.org/?mlat=53.590985&mlon=9.917974#map=18/53.590985/9.917974) | ☐ |
| Zufall | `seg_cff436841e62ecf8` | Niendorfer Gehege | Eimsbüttel | ETW30 | HAUPT | Fahrradstraße | 10.0 | 27.4 | passt | nan | [SVG](profiles_sample/seg_cff436841e62ecf8.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562495,5941492]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.618504/9.944799) · [OSM](https://www.openstreetmap.org/?mlat=53.618504&mlon=9.944799#map=18/53.618504/9.944799) | ☐ |
| Zufall | `seg_d0f9eb1279ea00a2` | Niendorfer Straße | Eimsbüttel | ETW30 | ERSCHL | Mischverkehr | 15.0 | 15.9 | passt | nan | [SVG](profiles_sample/seg_d0f9eb1279ea00a2.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563209,5940082]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.605744/9.955307) · [OSM](https://www.openstreetmap.org/?mlat=53.605744&mlon=9.955307#map=18/53.605744/9.955307) | ☐ |
| Zufall | `seg_0c2c0b827e31be64` | Willy-Brandt-Straße | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 13.2 | 41.8 | passt | nan | [SVG](profiles_sample/seg_0c2c0b827e31be64.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565352,5933641]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.547596/9.986331) · [OSM](https://www.openstreetmap.org/?mlat=53.547596&mlon=9.986331#map=18/53.547596/9.986331) | ☐ |
| Zufall | `seg_1e9aaa4df265c8b7` | Hammer Landstraße | Hamburg-Mitte | GOW30 | ERSCHL | Radfahrstreifen | 22.4 | 44.4 | passt | nan | [SVG](profiles_sample/seg_1e9aaa4df265c8b7.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570054,5934531]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.554983/10.057486) · [OSM](https://www.openstreetmap.org/?mlat=53.554983&mlon=10.057486#map=18/53.554983/10.057486) | ☐ |
| Zufall | `seg_991b2777bbc66a56` | Hans-Sander-Straße | Hamburg-Mitte | ETW_ERF | HAUPT | Mischverkehr | 11.2 | 15.0 | passt | nan | [SVG](profiles_sample/seg_991b2777bbc66a56.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565420,5930367]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.518162/9.986676) · [OSM](https://www.openstreetmap.org/?mlat=53.518162&mlon=9.986676#map=18/53.518162/9.986676) | ☐ |
| Zufall | `seg_c65789f9243aaf61` | Detlev-Bremer-Straße | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 12.5 | 15.0 | passt | nan | [SVG](profiles_sample/seg_c65789f9243aaf61.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563944,5934067]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.551597/9.965181) · [OSM](https://www.openstreetmap.org/?mlat=53.551597&mlon=9.965181#map=18/53.551597/9.965181) | ☐ |
| Zufall | `seg_d7778491df2b2aeb` | Caspar-Voght-Straße | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 12.2 | 10.4 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_d7778491df2b2aeb.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570255,5934982]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559009/10.060632) · [OSM](https://www.openstreetmap.org/?mlat=53.559009&mlon=10.060632#map=18/53.559009/10.060632) | ☐ |
| Zufall | `seg_0ce68fe5cf817c19` | Beckermannweg | Hamburg-Nord | ETW30 | ERSCHL | Mischverkehr | 10.8 | 11.2 | passt | nan | [SVG](profiles_sample/seg_0ce68fe5cf817c19.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566608,5946608]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.663971/10.008065) · [OSM](https://www.openstreetmap.org/?mlat=53.663971&mlon=10.008065#map=18/53.663971/10.008065) | ☐ |
| Zufall | `seg_296f650955e81515` | Barmbeker Straße | Hamburg-Nord | GOW30 | ERSCHL | Radfahrstreifen | 27.6 | 32.0 | passt | nan | [SVG](profiles_sample/seg_296f650955e81515.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566361,5938647]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.592457/10.002621) · [OSM](https://www.openstreetmap.org/?mlat=53.592457&mlon=10.002621#map=18/53.592457/10.002621) | ☐ |
| Zufall | `seg_6230eeac8f450ca9` | Weg beim Jäger | Hamburg-Nord | ETW30 | HAUPT | Fahrradstraße | 12.0 | 20.0 | passt | nan | [SVG](profiles_sample/seg_6230eeac8f450ca9.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565164,5941143]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.615034/9.985063) · [OSM](https://www.openstreetmap.org/?mlat=53.615034&mlon=9.985063#map=18/53.615034/9.985063) | ☐ |
| Zufall | `seg_680f15dba73d6dc3` | Alfred-Johann-Levy-Straße | Hamburg-Nord | ETW30 | BASIS | Mischverkehr | 14.8 | 19.0 | passt | nan | [SVG](profiles_sample/seg_680f15dba73d6dc3.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568663,5939856]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.603023/10.037670) · [OSM](https://www.openstreetmap.org/?mlat=53.603023&mlon=10.037670#map=18/53.603023/10.037670) | ☐ |
| Zufall | `seg_e0f61b9f6c093595` | Semperstraße | Hamburg-Nord | ETW30 | ERSCHL | Mischverkehr | 13.2 | 17.0 | passt | nan | [SVG](profiles_sample/seg_e0f61b9f6c093595.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567578,5938181]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.588116/10.020913) · [OSM](https://www.openstreetmap.org/?mlat=53.588116&mlon=10.020913#map=18/53.588116/10.020913) | ☐ |
| Zufall | `seg_0b90647ba524e0a3` | Geutensweg | Harburg | ETW30 | ERSCHL | Mischverkehr | 10.8 | 14.9 | passt | nan | [SVG](profiles_sample/seg_0b90647ba524e0a3.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555698,5925401]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.474649/9.839188) · [OSM](https://www.openstreetmap.org/?mlat=53.474649&mlon=9.839188#map=18/53.474649/9.839188) | ☐ |
| Zufall | `seg_c6d3724c921c0b78` | Wilstorfer Straße | Harburg | GOW30 | HAUPT | Radweg je Seite | 27.4 | 28.3 | passt | nan | [SVG](profiles_sample/seg_c6d3724c921c0b78.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565386,5923563]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.457016/9.984743) · [OSM](https://www.openstreetmap.org/?mlat=53.457016&mlon=9.984743#map=18/53.457016/9.984743) | ☐ |
| Zufall | `seg_d4e2996f3f4ce787` | Ostheide | Harburg | ETW30 | BASIS | Mischverkehr | 9.8 | 9.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_d4e2996f3f4ce787.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557037,5924351]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.465067/9.859171) · [OSM](https://www.openstreetmap.org/?mlat=53.465067&mlon=9.859171#map=18/53.465067/9.859171) | ☐ |
| Zufall | `seg_3847814a8f0f60f5` | Thomas-Mann-Straße | Wandsbek | ETW30 | BASIS | Mischverkehr | 12.5 | 14.0 | passt | nan | [SVG](profiles_sample/seg_3847814a8f0f60f5.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573842,5942666]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.627573/10.116583) · [OSM](https://www.openstreetmap.org/?mlat=53.627573&mlon=10.116583#map=18/53.627573/10.116583) | ☐ |
| Zufall | `seg_79687387a89efb09` | Sthamerstraße | Wandsbek | ETW30 | HAUPT | Fahrradstraße | 9.0 | 6.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_79687387a89efb09.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575301,5949864]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.692049/10.140394) · [OSM](https://www.openstreetmap.org/?mlat=53.692049&mlon=10.140394#map=18/53.692049/10.140394) | ☐ |
| Zufall | `seg_9d2cffde89b12109` | Rabenhorst | Wandsbek | ETW30 | HAUPT | Fahrradstraße | 10.0 | 13.0 | passt | nan | [SVG](profiles_sample/seg_9d2cffde89b12109.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572054,5944113]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.640825/10.089893) · [OSM](https://www.openstreetmap.org/?mlat=53.640825&mlon=10.089893#map=18/53.640825/10.089893) | ☐ |
| Zufall | `seg_ba64bc5985c35e1f` | Tonndorfer Hauptstraße | Wandsbek | GOW30 | HAUPT | Radfahrstreifen | 19.3 | 19.9 | passt nach Abbau | D2|fallback|D4 | [SVG](profiles_sample/seg_ba64bc5985c35e1f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575270,5938810]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.592718/10.137238) · [OSM](https://www.openstreetmap.org/?mlat=53.592718&mlon=10.137238#map=18/53.592718/10.137238) | ☐ |
| Zufall | `seg_c94138c1adf29362` | Kolpingweg | Wandsbek | ETW30 | ERSCHL | Mischverkehr | 14.8 | 16.0 | passt | nan | [SVG](profiles_sample/seg_c94138c1adf29362.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570659,5937329]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.580049/10.067248) · [OSM](https://www.openstreetmap.org/?mlat=53.580049&mlon=10.067248#map=18/53.580049/10.067248) | ☐ |
| Zufall | `seg_cd63534161ff9bda` | Leemrackeln / Beim Ziegelhof | Wandsbek | ETW30 | ERSCHL | Mischverkehr | 9.8 | 9.3 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_cd63534161ff9bda.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573587,5950787]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.700593/10.114652) · [OSM](https://www.openstreetmap.org/?mlat=53.700593&mlon=10.114652#map=18/53.700593/10.114652) | ☐ |
| Zufall | `seg_62aa117eb4cabacb` | Zeppelinstraße | nan | ETW30 | ERSCHL | Mischverkehr | 10.8 | 31.3 | passt | nan | [SVG](profiles_sample/seg_62aa117eb4cabacb.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565228,5945174]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.651261/9.986886) · [OSM](https://www.openstreetmap.org/?mlat=53.651261&mlon=9.986886#map=18/53.651261/9.986886) | ☐ |
| am breitesten | `seg_4dbd2b1c32ab013f` | Foorthkamp | Hamburg-Nord | ETW30 | ERSCHL | Mischverkehr | 13.2 | 77.5 | passt | nan | [SVG](profiles_sample/seg_4dbd2b1c32ab013f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567184,5946303]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.661157/10.016711) · [OSM](https://www.openstreetmap.org/?mlat=53.661157&mlon=10.016711#map=18/53.661157/10.016711) | ☐ |
| am breitesten | `seg_fc49f8757247b9f9` | Wendlohstieg | Eimsbüttel | ETW30 | ERSCHL | Mischverkehr | 10.8 | 77.0 | passt | nan | [SVG](profiles_sample/seg_fc49f8757247b9f9.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561751,5942662]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.629106/9.933786) · [OSM](https://www.openstreetmap.org/?mlat=53.629106&mlon=9.933786#map=18/53.629106/9.933786) | ☐ |
| am breitesten | `seg_c27ae69f0fb44227` | Brücke des 17. Juni | Harburg | GOW50 | ERSCHL | Radweg je Seite | 22.5 | 76.9 | passt | nan | [SVG](profiles_sample/seg_c27ae69f0fb44227.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566076,5925403]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.473468/9.995526) · [OSM](https://www.openstreetmap.org/?mlat=53.473468&mlon=9.995526#map=18/53.473468/9.995526) | ☐ |
| am breitesten | `seg_b3e6636488940420` | Brücke des 17. Juni | Harburg | GOW50 | ERSCHL | Radweg je Seite | 22.0 | 76.9 | passt | nan | [SVG](profiles_sample/seg_b3e6636488940420.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565982,5925064]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470431/9.994034) · [OSM](https://www.openstreetmap.org/?mlat=53.470431&mlon=9.994034#map=18/53.470431/9.994034) | ☐ |
| am breitesten | `seg_acbd875df0e2d263` | Brücke des 17. Juni | Harburg | GOW50 | ERSCHL | Radweg je Seite | 22.5 | 76.9 | passt | nan | [SVG](profiles_sample/seg_acbd875df0e2d263.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565988,5925119]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470919/9.994142) · [OSM](https://www.openstreetmap.org/?mlat=53.470919&mlon=9.994142#map=18/53.470919/9.994142) | ☐ |
| am breitesten | `seg_73f4aff29f56f111` | Brücke des 17. Juni | Harburg | GOW50 | ERSCHL | Radweg je Seite | 22.5 | 76.9 | passt | nan | [SVG](profiles_sample/seg_73f4aff29f56f111.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565975,5925066]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470446/9.993933) · [OSM](https://www.openstreetmap.org/?mlat=53.470446&mlon=9.993933#map=18/53.470446/9.993933) | ☐ |
| am breitesten | `seg_6653e0921378fd9a` | Brücke des 17. Juni | Hamburg-Mitte | GOW50 | HAUPT | Radweg je Seite | 23.5 | 76.9 | passt | nan | [SVG](profiles_sample/seg_6653e0921378fd9a.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566171,5925768]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.476734/9.997030) · [OSM](https://www.openstreetmap.org/?mlat=53.476734&mlon=9.997030#map=18/53.476734/9.997030) | ☐ |
| am breitesten | `seg_275e9dae1753fd32` | Brücke des 17. Juni | Harburg | GOW50 | ERSCHL | Radweg je Seite | 22.5 | 76.9 | passt | nan | [SVG](profiles_sample/seg_275e9dae1753fd32.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566070,5925405]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.473484/9.995436) · [OSM](https://www.openstreetmap.org/?mlat=53.473484&mlon=9.995436#map=18/53.473484/9.995436) | ☐ |
| am breitesten | `seg_a2a3f7396d1f5979` | Löwenzahnweg | Altona | ETW30 | BASIS | Mischverkehr | 14.8 | 76.0 | passt | nan | [SVG](profiles_sample/seg_a2a3f7396d1f5979.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557212,5937627]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.584369/9.864226) · [OSM](https://www.openstreetmap.org/?mlat=53.584369&mlon=9.864226#map=18/53.584369/9.864226) | ☐ |
| am breitesten | `seg_a7a3f9eb51e6058a` | Billhorner Brückenstraße / Billhorner Brücke | Hamburg-Mitte | GOW50 | RSV | Radweg je Seite | 32.5 | 75.7 | passt | nan | [SVG](profiles_sample/seg_a7a3f9eb51e6058a.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568239,5932345]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.535575/10.029617) · [OSM](https://www.openstreetmap.org/?mlat=53.535575&mlon=10.029617#map=18/53.535575/10.029617) | ☐ |
| am breitesten | `seg_fb985afcf9d8c4e6` | Hannoversche Straße | Harburg | ETW30 | ERSCHL | Mischverkehr | 10.8 | 74.0 | passt | nan | [SVG](profiles_sample/seg_fb985afcf9d8c4e6.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565579,5922985]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.451799/9.987529) · [OSM](https://www.openstreetmap.org/?mlat=53.451799&mlon=9.987529#map=18/53.451799/9.987529) | ☐ |
| am breitesten | `seg_81b7a90ad59d7128` | Hannoversche Straße | Harburg | ETW30 | ERSCHL | Mischverkehr | 10.8 | 74.0 | passt | nan | [SVG](profiles_sample/seg_81b7a90ad59d7128.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565579,5922998]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.451910/9.987538) · [OSM](https://www.openstreetmap.org/?mlat=53.451910&mlon=9.987538#map=18/53.451910/9.987538) | ☐ |
| am breitesten | `seg_59f595e5fa9367f0` | Hannoversche Straße | Harburg | GOW50 | ERSCHL | Radweg je Seite | 22.0 | 74.0 | passt | nan | [SVG](profiles_sample/seg_59f595e5fa9367f0.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565641,5923003]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.451947/9.988470) · [OSM](https://www.openstreetmap.org/?mlat=53.451947&mlon=9.988470#map=18/53.451947/9.988470) | ☐ |
| am breitesten | `seg_4bd566ad5a8101e0` | Hannoversche Straße | Harburg | GOW50 | ERSCHL | Radweg je Seite | 22.0 | 74.0 | passt | nan | [SVG](profiles_sample/seg_4bd566ad5a8101e0.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565730,5923052]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.452381/9.989818) · [OSM](https://www.openstreetmap.org/?mlat=53.452381&mlon=9.989818#map=18/53.452381/9.989818) | ☐ |
| am breitesten | `seg_3092d50608aed695` | Hannoversche Straße | Harburg | GOW50 | ERSCHL | Radweg je Seite | 22.0 | 74.0 | passt | nan | [SVG](profiles_sample/seg_3092d50608aed695.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565639,5923014]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.452048/9.988439) · [OSM](https://www.openstreetmap.org/?mlat=53.452048&mlon=9.988439#map=18/53.452048/9.988439) | ☐ |
| am breitesten | `seg_ddd72b0f3d02de20` | Finkenwerder Straße | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 10.0 | 71.2 | passt | nan | [SVG](profiles_sample/seg_ddd72b0f3d02de20.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559461,5929968]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.515280/9.896742) · [OSM](https://www.openstreetmap.org/?mlat=53.515280&mlon=9.896742#map=18/53.515280/9.896742) | ☐ |
| am breitesten | `seg_7cea60c66a63b99a` | Finkenwerder Straße | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 10.0 | 71.2 | passt | nan | [SVG](profiles_sample/seg_7cea60c66a63b99a.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559670,5929878]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.514453/9.899877) · [OSM](https://www.openstreetmap.org/?mlat=53.514453&mlon=9.899877#map=18/53.514453/9.899877) | ☐ |
| am breitesten | `seg_bc98ce13e2cbee57` | Eimsbütteler Marktplatz | Eimsbüttel | GOW30 | HAUPT | Radweg je Seite | 20.0 | 70.1 | passt | nan | [SVG](profiles_sample/seg_bc98ce13e2cbee57.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562562,5936428]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572983/9.944795) · [OSM](https://www.openstreetmap.org/?mlat=53.572983&mlon=9.944795#map=18/53.572983/9.944795) | ☐ |
| am breitesten | `seg_9299750046b2e39a` | Eimsbütteler Marktplatz | Eimsbüttel | GOW30 | HAUPT | Radweg je Seite | 19.8 | 70.1 | passt | nan | [SVG](profiles_sample/seg_9299750046b2e39a.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562473,5936398]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572723/9.943437) · [OSM](https://www.openstreetmap.org/?mlat=53.572723&mlon=9.943437#map=18/53.572723/9.943437) | ☐ |
| am breitesten | `seg_5190df2af336f5fa` | – | Eimsbüttel | ETW30 | HAUPT | Fahrradstraße | 10.0 | 69.1 | passt | nan | [SVG](profiles_sample/seg_5190df2af336f5fa.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562625,5938713]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.593506/9.946203) · [OSM](https://www.openstreetmap.org/?mlat=53.593506&mlon=9.946203#map=18/53.593506/9.946203) | ☐ |
| am engsten | `seg_62fb2a90f492573f` | Bullertweg | Hamburg-Mitte | ETW30 | HAUPT | Fahrradstraße | 9.0 | 2.4 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_62fb2a90f492573f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568455,5928501]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.501000/10.032042) · [OSM](https://www.openstreetmap.org/?mlat=53.501000&mlon=10.032042#map=18/53.501000/10.032042) | ☐ |
| am engsten | `seg_693c64e252eaded2` | Wildgrund | Eimsbüttel | ETW30 | HAUPT | Fahrradstraße | 9.0 | 2.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_693c64e252eaded2.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561581,5941820]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.621556/9.931050) · [OSM](https://www.openstreetmap.org/?mlat=53.621556&mlon=9.931050#map=18/53.621556/9.931050) | ☐ |
| am engsten | `seg_73049fbda31028cb` | Birkenweg | Wandsbek | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_73049fbda31028cb.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574519,5946252]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.659707/10.127681) · [OSM](https://www.openstreetmap.org/?mlat=53.659707&mlon=10.127681#map=18/53.659707/10.127681) | ☐ |
| am engsten | `seg_98cc08aff1b66f2e` | Hügelhain | Harburg | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_98cc08aff1b66f2e.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562518,5922291]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.445926/9.941305) · [OSM](https://www.openstreetmap.org/?mlat=53.445926&mlon=9.941305#map=18/53.445926/9.941305) | ☐ |
| am engsten | `seg_2a212a9eebd3db10` | Kielkamp | Altona | ETW30 | HAUPT | Fahrradstraße | 9.0 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_2a212a9eebd3db10.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559774,5936346]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572572/9.902684) · [OSM](https://www.openstreetmap.org/?mlat=53.572572&mlon=9.902684#map=18/53.572572/9.902684) | ☐ |
| am engsten | `seg_8b5b1cfe85865b04` | Kielkamp | Altona | ETW30 | ERSCHL | Mischverkehr | 9.0 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_8b5b1cfe85865b04.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559795,5936500]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.573948/9.903032) · [OSM](https://www.openstreetmap.org/?mlat=53.573948&mlon=9.903032#map=18/53.573948/9.903032) | ☐ |
| am engsten | `seg_6eb298c350f0d8d0` | Holtkoppel 17a-17f | Hamburg-Nord | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_6eb298c350f0d8d0.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566472,5944079]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.641260/10.005470) · [OSM](https://www.openstreetmap.org/?mlat=53.641260&mlon=10.005470#map=18/53.641260/10.005470) | ☐ |
| am engsten | `seg_946d407d2bda5ac5` | Wulmstal | Harburg | ETW30 | HAUPT | Fahrradstraße | 9.0 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_946d407d2bda5ac5.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559128,5923157]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.454106/9.890435) · [OSM](https://www.openstreetmap.org/?mlat=53.454106&mlon=9.890435#map=18/53.454106/9.890435) | ☐ |
| am engsten | `seg_4297cf5c2c015321` | Hans-Lange-Straße | Altona | ETW_ERF | none | Mischverkehr | 4.8 | 2.6 | passt nicht | D6 | [SVG](profiles_sample/seg_4297cf5c2c015321.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553205,5934743]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558868/9.803217) · [OSM](https://www.openstreetmap.org/?mlat=53.558868&mlon=9.803217#map=18/53.558868/9.803217) | ☐ |
| am engsten | `seg_b91c4915f98dfc0d` | Hans-Lange-Straße | Altona | ETW_ERF | none | Mischverkehr | 4.8 | 2.6 | passt nicht | D6 | [SVG](profiles_sample/seg_b91c4915f98dfc0d.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553235,5934791]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559300/9.803680) · [OSM](https://www.openstreetmap.org/?mlat=53.559300&mlon=9.803680#map=18/53.559300/9.803680) | ☐ |
| am engsten | `seg_fbab51f03791f399` | Zirpenweg | Wandsbek | ETW30 | HAUPT | Fahrradstraße | 9.0 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_fbab51f03791f399.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572819,5935670]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564847/10.099485) · [OSM](https://www.openstreetmap.org/?mlat=53.564847&mlon=10.099485#map=18/53.564847/10.099485) | ☐ |
| am engsten | `seg_f39b5c200a3411b2` | Scharlbargstieg | Harburg | ETW30 | ERSCHL | Mischverkehr | 12.2 | 2.7 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_f39b5c200a3411b2.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554627,5923997]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.462137/9.822813) · [OSM](https://www.openstreetmap.org/?mlat=53.462137&mlon=9.822813#map=18/53.462137/9.822813) | ☐ |
| am engsten | `seg_92a1060f84d6d02f` | Beentkamp | Eimsbüttel | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.7 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_92a1060f84d6d02f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560727,5941613]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.619795/9.918093) · [OSM](https://www.openstreetmap.org/?mlat=53.619795&mlon=9.918093#map=18/53.619795/9.918093) | ☐ |
| am engsten | `seg_22b48d236c70cfc8` | Neuwulmstorfer Schulstraße | Harburg | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.7 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_22b48d236c70cfc8.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553387,5924779]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.469300/9.804270) · [OSM](https://www.openstreetmap.org/?mlat=53.469300&mlon=9.804270#map=18/53.469300/9.804270) | ☐ |
| am engsten | `seg_a153e0eb11822045` | Weg Nr. 12 | Wandsbek | ETW30 | HAUPT | Fahrradstraße | 9.0 | 2.8 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_a153e0eb11822045.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573017,5935743]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.565477/10.102489) · [OSM](https://www.openstreetmap.org/?mlat=53.565477&mlon=10.102489#map=18/53.565477/10.102489) | ☐ |
| am engsten | `seg_4332c4e9c8d1da2c` | Kahlkamp | Altona | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.8 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_4332c4e9c8d1da2c.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553280,5934949]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560714/9.804384) · [OSM](https://www.openstreetmap.org/?mlat=53.560714&mlon=9.804384#map=18/53.560714/9.804384) | ☐ |
| am engsten | `seg_5818aab473f4ba6f` | Baxmannstraße | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.8 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_5818aab473f4ba6f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574839,5933226]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.542600/10.129397) · [OSM](https://www.openstreetmap.org/?mlat=53.542600&mlon=10.129397#map=18/53.542600/10.129397) | ☐ |
| am engsten | `seg_2115922e761159b0` | Garnstück | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.8 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_2115922e761159b0.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558493,5931673]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.530715/9.882466) · [OSM](https://www.openstreetmap.org/?mlat=53.530715&mlon=9.882466#map=18/53.530715/9.882466) | ☐ |
| am engsten | `seg_d5bc14135eaec84f` | Hainholzweg | Harburg | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.8 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_d5bc14135eaec84f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561820,5922709]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.449771/9.930879) · [OSM](https://www.openstreetmap.org/?mlat=53.449771&mlon=9.930879#map=18/53.449771/9.930879) | ☐ |
| am engsten | `seg_72a9ab69b20da1a8` | Up de Worth | Wandsbek | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.8 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_72a9ab69b20da1a8.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571223,5944143]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.641213/10.077328) · [OSM](https://www.openstreetmap.org/?mlat=53.641213&mlon=10.077328#map=18/53.641213/10.077328) | ☐ |

## Grenzen

- Busse je Spitzenstunde aus der Abfahrtsstunde der ersten Haltestelle je Fahrt; auf langen Linien liegt die Stunde am Abschnitt später (PRF-02, docs/open_questions.md).
- Verfügbare Breite nur auf rund 58 % der Abschnitte (ALKIS-Verkehrsfläche); ohne Breite keine Passung.
- Ist-Parken nur, wo OSM parking erfasst ist; ohne Angabe kein Parken im Soll-Profil (PRF-03).
- Bushaltestellen (PL-05), Abbiegestreifen (L-05) und die Seitenbedingung PL-02 sind nicht im Streckenprofil.
- GOW30 mit Radfahrstreifen: Radfahrstreifen kommen zur CROW-Fahrbahnbreite hinzu (Annahme, offen).
- Bei bahnigkeit 2 beschreibt das Profil den ganzen Straßenraum; beide Richtungsfahrbahnen bekommen dasselbe Profil.

Quellen: OpenStreetMap-Mitwirkende (ODbL); Freie und Hansestadt Hamburg, ALKIS, Verkehrsmengen und Fahrstreifen (dl-de/by-2.0); HVV-Fahrplandaten GTFS (Transparenzportal Hamburg, dl-de/by-2.0).
