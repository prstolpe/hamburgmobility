# Soll-Querschnitt: Fahrstreifen, Lage der Radanlagen, Raumaufteilung (Stufe c06)

Erzeugt 2026-11-07T14:25:01+00:00 mit pipeline/c06_cross_section_soll.py · design_rules.yaml 0.5.0 · cycling_rules.yaml 0.7.0 · nicht amtlicher Entwurf. Regeln L-01…06, PL-01…06 und PRF-01…07 sind Annahmen bzw. Entwürfe (status draft) und vor Gebrauch fachlich zu prüfen.

Verfügbare Breite = width_p10_m der Variante Verkehrsfläche (maßgeblich); die Variante Fassade zeigt das Potenzial inklusive Vorgärten. Das gewünschte Profil enthält Gehwege (Regelmaß), die Radanlage mit Sollbreite aus Prompt 18, ÖPNV, Fahrbahn, Trennstreifen, Bäume (GOW), Ladezone bei Geschäftsnutzung und Parken nur dort, wo OSM heute Parken zeigt (Entscheidung 2026-11-06). Passt es nicht, gilt die Kaskade D1, D2, Fallback, D3, D4, D5, D6, D7 (PRF-06).

## Kurzfassung

- 36 526 Abschnitte, 4 998 km; bewertet (Profilregeln und Breite vorhanden): 3 520 km. Ohne Breite: 678 km; ohne Profilregeln: 800 km.
- passt: 1 868 km (53 % der bewerteten Länge).
- passt nach Abbau: 728 km (21 % der bewerteten Länge).
- passt nicht: 924 km (26 % der bewerteten Länge).
- Vorschlag GOW50 → GOW30 (D5): 82 Abschnitte, 24.3 km – nicht übernommen, Entscheidung über overrides/overrides.csv.
- GTFS: repräsentativer Werktag 2026-04-29 (Upload__hvv_Rohdaten_GTFS_Fpl_20260408.ZIP); Straßenbahnrouten im Feed: 0. Busfahrstreifen Soll: 13.8 km.

## km je fit_class und Straßenkategorie

| Kategorie | passt | passt nach Abbau | passt nicht | nicht bewertet | gesamt |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0.0 | 0.0 | 0.0 | 189.2 | 189.2 |
| GOW50 | 76.8 | 87.5 | 20.8 | 36.2 | 221.3 |
| GOW30 | 251.5 | 133.6 | 58.4 | 79.8 | 523.4 |
| ETW30 | 1 455.4 | 505.5 | 840.2 | 534.3 | 3 335.5 |
| ETW_ERF | 83.8 | 1.9 | 4.5 | 27.7 | 118.0 |

### Verkehrsfläche gegen Fassade (km, nur mit beiden Breiten)

| Verkehrsfläche \ Fassade | passt | passt nach Abbau | passt nicht |
| --- | ---: | ---: | ---: |
| passt | 1 358.7 | 0.9 | 0.2 |
| passt nach Abbau | 549.7 | 35.6 | 0.4 |
| passt nicht | 620.8 | 15.2 | 16.7 |

## Abbaustufen

Häufigkeit je Stufe (ein Abschnitt kann mehrere Stufen haben). Eine Stufe zählt nur, wenn sie das Profil verändert.

| Stufe | Maßnahme | Abschnitte | km | Anteil an bewerteter Länge |
| --- | --- | ---: | ---: | ---: |
| D1 | Parken entfernen | 1 912 | 311.6 | 8.9 % |
| D2 | Baumstreifen → Baumscheiben | 1 467 | 287.1 | 8.2 % |
| fallback | Fallback der Matrixzelle (Prompt 18) | 370 | 68.5 | 1.9 % |
| D3 | zweiten Kfz-Fahrstreifen streichen | 104 | 26.4 | 0.7 % |
| D4 | Rad- und Gehweg auf Mindestbreite | 6 906 | 1 345.3 | 38.2 % |
| D5 | Vorschlag GOW50 → GOW30 (C-G30-02) | 82 | 24.3 | 0.7 % |
| D6 | Flag: Einrichtungsverkehr / Durchfahrtsunterbrechung prüfen | 4 777 | 924.0 | 26.2 % |
| D7 | Flag: Radroute auf Parallelstraße verlegen | 335 | 77.0 | 2.2 % |

Letzte wirksame Stufe bei „passt nach Abbau“ (km):

D1 156.0 · D2 107.7 · fallback 14.5 · D3 24.5 · D4 422.3 · D5 3.5

## Fahrstreifen Ist → Soll (km)

Ist je Richtung aus amtlichen Fahrstreifen (sonst OSM lanes, PRF-01). Soll nach L-01…L-06; L-06 verhindert jeden Zuwachs ohne Override (eine Override-Ebene für Fahrstreifen gibt es noch nicht).

| Ist \ Soll | 1 | 1 + Bus | 2 | shared | – |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 282.4 | 0.0 | 0.0 | 2 936.7 | 84.7 |
| 2 | 261.0 | 9.7 | 50.1 | 90.4 | 83.8 |
| 3 | 87.5 | 2.5 | 17.4 | 15.7 | 14.1 |
| 4 | 20.5 | 1.1 | 7.6 | 1.8 | 6.2 |
| 5 | 2.4 | 0.1 | 0.3 | 0.5 | 0.4 |
| 6 | 0.2 | 0.0 | 0.6 | 0.1 | 0.0 |
| unbekannt | 0.7 | 0.5 | 0.0 | 408.2 | 0.0 |

Weniger Kfz-Fahrstreifen je Richtung im Soll: 411.0 km (davon an GOW50 76.4 km). Zusätzlich D3 im Profil: 26.4 km.

## Fälle D5: Vorschlag GOW50 → GOW30 (C-G30-02)

82 Abschnitte, 24.3 km. Längste 40, je Straße und Bezirk zusammengefasst:

| Straße | Bezirk | Kfz | Rad | Abschnitte | km | verfügbar m (Median) | Bedarf m (Median) | Beispiel |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Hohe-Schaar-Straße | Hamburg-Mitte | GOW50 | ERSCHL | 5 | 2.37 | 13.6 | 16.8 | `seg_041bf1bffc8768d7` |
| Elbchaussee | Altona | GOW50 | HAUPT | 4 | 1.82 | 12.1 | 16.8 | `seg_095ae2689e067006` |
| Kattwykdamm | Hamburg-Mitte | GOW50 | ERSCHL | 4 | 1.42 | 14.8 | 16.8 | `seg_46aad5633abbb4c1` |
| Wellingsbüttler Weg | Wandsbek | GOW50 | HAUPT | 3 | 0.95 | 14.2 | 16.8 | `seg_8232dbac21641f26` |
| Unterer Landweg | Hamburg-Mitte | GOW50 | HAUPT | 3 | 0.82 | 13.7 | 16.8 | `seg_41145b28109c17fc` |
| Hafenrandstraße | Hamburg-Mitte | GOW50 | BASIS | 1 | 0.77 | 14.0 | 16.8 | `seg_ce0603f23047a60c` |
| Schmidts Breite | Hamburg-Mitte | GOW50 | ERSCHL | 1 | 0.76 | 11.3 | 14.2 | `seg_78df93b3ecc9671d` |
| Meiendorfer Mühlenweg | Wandsbek | GOW50 | HAUPT | 2 | 0.74 | 11.0 | 14.2 | `seg_30bb3774a6771bf5` |
| Fürstenmoordamm | Harburg | GOW50 | none | 1 | 0.71 | 12.9 | 16.8 | `seg_02452cc02f4b00d2` |
| Ehestorfer Weg | Harburg | GOW50 | ERSCHL | 1 | 0.67 | 7.8 | 14.2 | `seg_aaf7eec60da1d6d1` |
| Segeberger Chaussee | Wandsbek | GOW50 | ERSCHL | 2 | 0.64 | 16.3 | 16.8 | `seg_1265f8ab675eb0e7` |
| Poppenbütteler Chaussee | Wandsbek | GOW50 | ERSCHL | 1 | 0.63 | 11.9 | 16.8 | `seg_91501613d1b165c2` |
| Garstedter Weg | Eimsbüttel | GOW50 | BASIS | 2 | 0.54 | 13.9 | 16.8 | `seg_73bba197a1d9fa7b` |
| Neßdeich | Hamburg-Mitte | GOW50 | ERSCHL | 3 | 0.54 | 14.9 | 14.2 | `seg_2459331cda9a82dd` |
| Maldfeldstraße | Harburg | GOW50 | ERSCHL | 1 | 0.53 | 5.3 | 16.8 | `seg_c4a60d27c5bb5ac4` |
| Eißendorfer Waldweg | Harburg | GOW50 | HAUPT | 1 | 0.52 | 9.3 | 14.2 | `seg_896df8d623e86dbd` |
| Farnhornweg | Altona | GOW50 | HAUPT | 2 | 0.49 | 19.3 | 16.8 | `seg_19c6219f387e811c` |
| Reinbeker Redder | Bergedorf | GOW50 | HAUPT | 1 | 0.49 | 16.2 | 16.8 | `seg_2818b7cebb47b115` |
| An der Alsterschleife | Wandsbek | GOW50 | HAUPT | 1 | 0.47 | 10.7 | 14.2 | `seg_c5db1848591c3a8f` |
| Waldweg | Wandsbek | GOW50 | HAUPT | 2 | 0.44 | 13.9 | 16.8 | `seg_33cee3733f4f13e1` |
| Meiendorfer Straße | Wandsbek | GOW50 | HAUPT | 4 | 0.43 | 15.8 | 16.8 | `seg_372377a05d48046f` |
| Garstedter Weg | Eimsbüttel | GOW50 | HAUPT | 2 | 0.38 | 15.0 | 16.8 | `seg_5318793c486e4563` |
| Pinneberger Straße | Eimsbüttel | GOW50 | ERSCHL | 1 | 0.37 | 16.4 | 16.8 | `seg_5fe94056e73a9e8c` |
| Liebigstraße / Unterer Landweg | Hamburg-Mitte | GOW50 | HAUPT | 1 | 0.36 | 13.3 | 16.8 | `seg_2ee8229c6c588661` |
| Lohe | Wandsbek | GOW50 | ERSCHL | 1 | 0.36 | 13.8 | 16.8 | `seg_ae6f2bc9b7841d26` |
| Saseler Chaussee | Wandsbek | GOW50 | HAUPT | 1 | 0.35 | 15.6 | 16.8 | `seg_631a440381c8a262` |
| Jüthornstraße | Wandsbek | GOW50 | HAUPT | 1 | 0.34 | 21.3 | 16.8 | `seg_fab5929161c1ead3` |
| Reiherstieg-Hauptdeich | Hamburg-Mitte | GOW50 | ERSCHL | 1 | 0.32 | 9.5 | 16.8 | `seg_698b1f7244691ed8` |
| Liebigstraße | Hamburg-Mitte | GOW50 | BASIS | 1 | 0.29 | 15.2 | 16.8 | `seg_0c0b612632fa40c2` |
| Pezolddamm | Wandsbek | GOW50 | HAUPT | 1 | 0.28 | 15.3 | 14.2 | `seg_0b3867bdbe79e3c8` |
| Volksdorfer Damm | Wandsbek | GOW50 | HAUPT | 2 | 0.27 | 14.4 | 16.8 | `seg_028ae77ce0dc6098` |
| Rodigallee | Wandsbek | GOW50 | HAUPT | 2 | 0.27 | 23.0 | 16.8 | `seg_5f44df6ede1cc9ce` |
| Hannoversche Straße | Harburg | GOW50 | HAUPT | 1 | 0.27 | 16.6 | 14.2 | `seg_5ce21acd3fd8c1da` |
| Eißendorfer Waldweg | Harburg | GOW50 | ERSCHL | 1 | 0.26 | 11.7 | 14.2 | `seg_b5c783553fd19e66` |
| Krohnstieg | Hamburg-Nord | GOW50 | ERSCHL | 1 | 0.26 | 16.3 | 16.8 | `seg_ea3f9b8236a966ea` |
| Altmannbrücke / Kurt-Schumacher-Allee | Hamburg-Mitte | GOW50 | ERSCHL | 1 | 0.25 | 15.3 | 16.8 | `seg_b7b3dba2f3c09dbd` |
| Reinbeker Redder | Bergedorf | GOW50 | ERSCHL | 1 | 0.24 | 21.1 | 16.8 | `seg_26c82b76b61029ab` |
| Maldfeldstraße | Harburg | GOW50 | BASIS | 1 | 0.23 | 12.4 | 16.8 | `seg_3d552fad6c87a274` |
| Lemsahler Landstraße | Wandsbek | GOW50 | BASIS | 1 | 0.22 | 14.4 | 16.8 | `seg_40f4235f6c8c2d16` |
| Aue-Hauptdeich / Finkenwerder Straße | Hamburg-Mitte | GOW50 | BASIS | 1 | 0.20 | 11.5 | 14.2 | `seg_92b3de74023ddec5` |

## Fälle D6: Flag: Einrichtungsverkehr / Durchfahrtsunterbrechung prüfen

4 777 Abschnitte, 924.0 km. Längste 40, je Straße und Bezirk zusammengefasst:

| Straße | Bezirk | Kfz | Rad | Abschnitte | km | verfügbar m (Median) | Bedarf m (Median) | Beispiel |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| (ohne Namen) | Hamburg-Mitte | ETW30 | BASIS | 8 | 4.75 | 8.4 | 9.8 | `seg_0ba8afeeda9be278` |
| Moorwerder Hauptdeich | Hamburg-Mitte | ETW30 | HAUPT | 6 | 3.42 | 8.3 | 9.0 | `seg_471bc3129ecccfdf` |
| Duvenstedter Triftweg / Langenreiher Weg | Wandsbek | ETW30 | HAUPT | 1 | 2.95 | 3.0 | 11.5 | `seg_be1fbefc540be72f` |
| Elbchaussee | Altona | GOW30 | HAUPT | 9 | 2.72 | 11.1 | 16.8 | `seg_0fb495600eaa26e8` |
| Eversween | Hamburg-Mitte | ETW30 | ERSCHL | 1 | 2.50 | 11.5 | 11.5 | `seg_f82cb6d74aac2ddb` |
| Hohe-Schaar-Straße | Hamburg-Mitte | GOW50 | ERSCHL | 5 | 2.37 | 13.6 | 16.8 | `seg_041bf1bffc8768d7` |
| Falkensteiner Ufer | Altona | ETW30 | HAUPT | 6 | 2.24 | 6.6 | 9.0 | `seg_1b0f130473ae92f5` |
| Moorwerder Hauptdeich | Hamburg-Mitte | ETW30 | ERSCHL | 4 | 2.14 | 8.1 | 11.5 | `seg_012525751224d503` |
| Finkenwerder Süderdeich / Süderkirchenweg | Hamburg-Mitte | ETW30 | ERSCHL | 1 | 2.07 | 7.9 | 9.8 | `seg_aa01d1f1f774f9e3` |
| Wiet | Hamburg-Mitte | ETW30 | ERSCHL | 1 | 1.88 | 7.3 | 9.8 | `seg_2f0b1863a6eaabb2` |
| Elbchaussee | Altona | GOW50 | HAUPT | 4 | 1.82 | 12.1 | 16.8 | `seg_095ae2689e067006` |
| Finkenrieker Hauptdeich | Hamburg-Mitte | ETW30 | ERSCHL | 4 | 1.76 | 5.4 | 9.8 | `seg_5352c602d7768bbb` |
| Puckaffer Weg | Wandsbek | ETW30 | ERSCHL | 4 | 1.68 | 9.1 | 9.8 | `seg_74c53ae7faf60098` |
| Niendorfer Gehege | Eimsbüttel | ETW30 | HAUPT | 2 | 1.67 | 8.8 | 10.2 | `seg_95a931e2a8b279ea` |
| Raakmoorgrund / Weg Nr. 651 | Hamburg-Nord | ETW30 | HAUPT | 1 | 1.65 | 6.0 | 9.0 | `seg_ecf40172d73d6546` |
| Siedenfelder Weg | Hamburg-Mitte | ETW30 | HAUPT | 1 | 1.61 | 7.8 | 9.0 | `seg_7fd526806f07de8c` |
| Waldweg | Wandsbek | GOW30 | BASIS | 4 | 1.56 | 14.0 | 16.8 | `seg_074d9f02a98f9463` |
| Maldfeldstraße | Harburg | ETW30 | ERSCHL | 2 | 1.54 | 6.8 | 9.8 | `seg_3f69460314cc2cbb` |
| Berliner Ufer | Hamburg-Mitte | ETW30 | ERSCHL | 1 | 1.54 | 4.8 | 9.8 | `seg_b65f34b9ef2b1049` |
| Mesterbrooksweg | Wandsbek | ETW30 | ERSCHL | 3 | 1.46 | 8.2 | 9.8 | `seg_0f7b44ffb9b6294a` |
| Rissener Landstraße | Altona | GOW30 | HAUPT | 3 | 1.44 | 13.5 | 16.8 | `seg_5e2484b7e7a56fbc` |
| Am Ochsenzoll | Hamburg-Nord | ETW30 | BASIS | 2 | 1.42 | 5.7 | 9.8 | `seg_aa8b6df36b4c4943` |
| Kattwykdamm | Hamburg-Mitte | GOW50 | ERSCHL | 4 | 1.42 | 14.8 | 16.8 | `seg_46aad5633abbb4c1` |
| Hans-Ulrich-Höller-Weg | Bergedorf | ETW30 | BASIS | 1 | 1.41 | 5.0 | 9.8 | `seg_9c01c86026c409b4` |
| Kobberdiekskoppel / Ödenweg | Wandsbek | ETW30 | ERSCHL | 1 | 1.39 | 8.2 | 9.8 | `seg_83c6f1d534de6622` |
| Francoper Straße | Harburg | GOW30 | ERSCHL | 3 | 1.36 | 8.4 | 14.2 | `seg_2cd77ed942e139d9` |
| Meiendorfer Straße | Wandsbek | GOW30 | HAUPT | 3 | 1.35 | 16.2 | 19.3 | `seg_35cf645c49234837` |
| Köterdamm | Hamburg-Mitte | ETW30 | ERSCHL | 2 | 1.34 | 8.0 | 9.8 | `seg_1a176f153e0174eb` |
| Hagenweg | Wandsbek | ETW30 | ERSCHL | 2 | 1.31 | 8.8 | 9.8 | `seg_b59fc543632c9b89` |
| Friedrichshulder Weg | Altona | ETW30 | HAUPT | 1 | 1.31 | 7.4 | 9.0 | `seg_e9ede1815b056b10` |
| Moorwerder Norderdeich | Hamburg-Mitte | ETW30 | HAUPT | 2 | 1.29 | 5.1 | 9.0 | `seg_1da1e89613f6cde1` |
| Wulmsberggrund | Harburg | ETW30 | HAUPT | 2 | 1.29 | 4.2 | 9.0 | `seg_12b7e9bc1394309e` |
| Osterfelddeich / Kirchenaußendeichsweg | Hamburg-Mitte | ETW30 | HAUPT | 1 | 1.28 | 8.5 | 9.0 | `seg_f107760b70327da7` |
| Stillhorner Hauptdeich | Hamburg-Mitte | ETW30 | HAUPT | 2 | 1.27 | 6.4 | 9.0 | `seg_6e9d83c097a58e71` |
| Einlagedeich | Hamburg-Mitte | ETW30 | HAUPT | 1 | 1.24 | 7.2 | 9.0 | `seg_64a83dbfbc6d2c96` |
| Pollhorner Hauptdeich | Hamburg-Mitte | GOW30 | ERSCHL | 1 | 1.24 | 8.7 | 14.2 | `seg_429717595f22897b` |
| Finkenwerder Landscheideweg | Hamburg-Mitte | ETW30 | BASIS | 2 | 1.23 | 8.4 | 9.8 | `seg_11205afd99725fda` |
| (ohne Namen) | Harburg | ETW30 | ERSCHL | 3 | 1.21 | 6.1 | 9.8 | `seg_0784076265a9bda6` |
| Kreetsander Hauptdeich | Hamburg-Mitte | ETW30 | HAUPT | 1 | 1.21 | 8.3 | 9.0 | `seg_ca730898b406b2ad` |
| Vogelhüttendeich / Buscher Weg | Hamburg-Mitte | ETW30 | ERSCHL | 1 | 1.21 | 4.8 | 9.8 | `seg_9d8d92481cc4fcd4` |

## Fälle D7: Flag: Radroute auf Parallelstraße verlegen

335 Abschnitte, 77.0 km. Längste 40, je Straße und Bezirk zusammengefasst:

| Straße | Bezirk | Kfz | Rad | Abschnitte | km | verfügbar m (Median) | Bedarf m (Median) | Beispiel |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Elbchaussee | Altona | GOW30 | HAUPT | 9 | 2.72 | 11.1 | 16.8 | `seg_0fb495600eaa26e8` |
| Hohe-Schaar-Straße | Hamburg-Mitte | GOW50 | ERSCHL | 5 | 2.37 | 13.6 | 16.8 | `seg_041bf1bffc8768d7` |
| Elbchaussee | Altona | GOW50 | HAUPT | 4 | 1.82 | 12.1 | 16.8 | `seg_095ae2689e067006` |
| Waldweg | Wandsbek | GOW30 | BASIS | 4 | 1.56 | 14.0 | 16.8 | `seg_074d9f02a98f9463` |
| Rissener Landstraße | Altona | GOW30 | HAUPT | 3 | 1.44 | 13.5 | 16.8 | `seg_5e2484b7e7a56fbc` |
| Kattwykdamm | Hamburg-Mitte | GOW50 | ERSCHL | 4 | 1.42 | 14.8 | 16.8 | `seg_46aad5633abbb4c1` |
| Francoper Straße | Harburg | GOW30 | ERSCHL | 3 | 1.36 | 8.4 | 14.2 | `seg_2cd77ed942e139d9` |
| Meiendorfer Straße | Wandsbek | GOW30 | HAUPT | 3 | 1.35 | 16.2 | 19.3 | `seg_35cf645c49234837` |
| Pollhorner Hauptdeich | Hamburg-Mitte | GOW30 | ERSCHL | 1 | 1.24 | 8.7 | 14.2 | `seg_429717595f22897b` |
| Seehafenstraße | Harburg | GOW30 | ERSCHL | 3 | 1.20 | 12.0 | 16.8 | `seg_6c5bd4d8e45a5ae3` |
| Rahlstedter Straße | Wandsbek | GOW30 | HAUPT | 5 | 1.19 | 18.0 | 19.3 | `seg_38f7a7648152fafc` |
| Kieler Straße | Eimsbüttel | GOW30 | HAUPT | 5 | 1.02 | 17.3 | 19.3 | `seg_54e2f881116fa080` |
| Wellingsbüttler Weg | Wandsbek | GOW50 | HAUPT | 3 | 0.95 | 14.2 | 16.8 | `seg_8232dbac21641f26` |
| Otto-Wels-Straße | Hamburg-Nord | GOW30 | HAUPT | 1 | 0.83 | 12.5 | 14.2 | `seg_b131d045260ba24f` |
| Unterer Landweg | Hamburg-Mitte | GOW50 | HAUPT | 3 | 0.82 | 13.7 | 16.8 | `seg_41145b28109c17fc` |
| Hafenrandstraße | Hamburg-Mitte | GOW50 | BASIS | 1 | 0.77 | 14.0 | 16.8 | `seg_ce0603f23047a60c` |
| Waldweg | Wandsbek | GOW30 | ERSCHL | 4 | 0.77 | 13.3 | 16.8 | `seg_4b56f559d4e0e09f` |
| Schmidts Breite | Hamburg-Mitte | GOW50 | ERSCHL | 1 | 0.76 | 11.3 | 14.2 | `seg_78df93b3ecc9671d` |
| Moorburger Straße | Harburg | GOW30 | ERSCHL | 2 | 0.75 | 13.8 | 16.8 | `seg_3315c26eadc8d159` |
| Meiendorfer Mühlenweg | Wandsbek | GOW50 | HAUPT | 2 | 0.74 | 11.0 | 14.2 | `seg_30bb3774a6771bf5` |
| Wellingsbüttler Weg | Wandsbek | GOW30 | BASIS | 4 | 0.74 | 13.5 | 18.1 | `seg_0658711bfb38f869` |
| Meckelfelder Weg | Harburg | GOW30 | ERSCHL | 5 | 0.73 | 9.3 | 16.8 | `seg_39ef70c47c8ad7a7` |
| Reiherstieg-Hauptdeich | Hamburg-Mitte | GOW30 | ERSCHL | 1 | 0.71 | 11.1 | 16.8 | `seg_4c3ca98a1f2942fa` |
| Volksdorfer Damm | Wandsbek | GOW30 | HAUPT | 3 | 0.71 | 17.0 | 19.3 | `seg_0e2587013a5860c3` |
| Garstedter Weg | Eimsbüttel | GOW30 | BASIS | 4 | 0.70 | 13.9 | 16.8 | `seg_31586e0ccf94c0cc` |
| Lemsahler Landstraße | Wandsbek | GOW30 | ERSCHL | 1 | 0.70 | 10.8 | 16.8 | `seg_9a1db680f64d374e` |
| Poppenbüttler Hauptstraße | Wandsbek | GOW30 | HAUPT | 5 | 0.70 | 13.0 | 14.2 | `seg_510dca558bd59282` |
| Aue-Hauptdeich | Hamburg-Mitte | GOW30 | BASIS | 1 | 0.69 | 12.1 | 14.2 | `seg_f7d11cd0eb080a2f` |
| Friedhofstraße | Harburg | GOW30 | HAUPT | 4 | 0.69 | 10.5 | 18.1 | `seg_3165ee34f155014a` |
| Ehestorfer Weg | Harburg | GOW50 | ERSCHL | 1 | 0.67 | 7.8 | 14.2 | `seg_aaf7eec60da1d6d1` |
| Nedderfeld | Hamburg-Nord | GOW30 | HAUPT | 1 | 0.67 | 17.0 | 19.3 | `seg_aa5407704b13547b` |
| Rahlstedter Straße | Wandsbek | GOW30 | BASIS | 6 | 0.66 | 18.0 | 19.3 | `seg_31be3a0f3d9cd46d` |
| Langenbeker Weg | Harburg | GOW30 | HAUPT | 5 | 0.66 | 10.2 | 14.2 | `seg_21a7de81a0076e20` |
| Poppenbütteler Chaussee | Wandsbek | GOW30 | ERSCHL | 3 | 0.66 | 9.7 | 16.8 | `seg_17f60dcf357e2a14` |
| Ehestorfer Weg | Harburg | GOW30 | HAUPT | 1 | 0.65 | 9.9 | 14.2 | `seg_71f041587ef4854d` |
| Segeberger Chaussee | Wandsbek | GOW50 | ERSCHL | 2 | 0.64 | 16.3 | 16.8 | `seg_1265f8ab675eb0e7` |
| Holtenklinker Straße | Bergedorf | GOW30 | HAUPT | 4 | 0.64 | 17.0 | 19.3 | `seg_139717d7d1061f76` |
| Wedeler Landstraße | Altona | GOW30 | HAUPT | 3 | 0.63 | 13.6 | 16.8 | `seg_0552b19135b13d9e` |
| Poppenbütteler Chaussee | Wandsbek | GOW50 | ERSCHL | 1 | 0.63 | 11.9 | 16.8 | `seg_91501613d1b165c2` |
| Oldesloer Straße | Eimsbüttel | GOW30 | BASIS | 3 | 0.61 | 13.7 | 16.8 | `seg_2d2a22df6cb0d52a` |

## Hinweise (Flags)

| Flag | Bedeutung | Abschnitte | km |
| --- | --- | ---: | ---: |
| `width_unknown` | keine verfügbare Breite (width_p10_m fehlt) | 13 217 | 678.1 |
| `no_profile_rules` | keine Profilregeln (SW, GOW80, ETW60 oder ohne Kategorie, PRF-04) | 2 294 | 799.6 |
| `dtv_unknown` | DTV fehlt an GOW50 – Fahrstreifen = Ist (PRF-01), confidence low | 303 | 26.2 |
| `lanes_capped_l06` | Soll-Fahrstreifen auf Ist begrenzt (L-06, kein Override) | 250 | 37.1 |
| `pl02_unchecked` | Zweirichtungsradweg: Seitenbedingung PL-02 nicht prüfbar (PRF-07) | 0 | 0.0 |
| `trees_in_parking_row` | Baumstreifen entfällt, Bäume als Baumscheiben (D2) | 1 467 | 287.1 |
| `gow30_dtv_above_profile` | GOW30 mit DTV über dem breiten CROW-Profil | 3 380 | 362.1 |
| `D6` | Flag: Einrichtungsverkehr / Durchfahrtsunterbrechung prüfen | 4 777 | 924.0 |
| `D7` | Flag: Radroute auf Parallelstraße verlegen | 335 | 77.0 |

confidence: high 3 350 km, medium 151 km, low 1 497 km

## fit_class je Bezirk (Anteil km)

| Bezirk | Abschnitte | km | passt | passt nach Abbau | passt nicht | nicht bewertet |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 4 886 | 620.5 | 36 % | 21 % | 27 % | 16 % |
| Bergedorf | 1 957 | 209.3 | 52 % | 15 % | 19 % | 15 % |
| Eimsbüttel | 4 004 | 470.4 | 48 % | 20 % | 17 % | 15 % |
| Hamburg-Mitte | 6 839 | 881.3 | 43 % | 13 % | 18 % | 26 % |
| Hamburg-Nord | 5 136 | 563.3 | 52 % | 14 % | 15 % | 19 % |
| Harburg | 3 348 | 465.2 | 36 % | 17 % | 25 % | 22 % |
| Wandsbek | 7 542 | 1 030.4 | 46 % | 20 % | 27 % | 7 % |
| ohne Bezirk | 990 | 146.9 | 0 % | 0 % | 0 % | 100 % |
| **gesamt** | 34 702 | 4 387.3 | 43 % | 17 % | 21 % | 20 % |

## Querschnitts-Skizzen (70 Profile)

reports/profiles_sample/<segment_id>.svg: 30 Zufallsabschnitte (über Bezirke verteilt, Seed 42), die 20 breitesten und die 20 engsten (verfügbare Breite). Elemente maßstäblich, blau gestrichelt die verfügbare Breite. Prüfung gegen Luftbild und Straßenbilder: Spalte „geprüft“ von Hand ausfüllen.

| Gruppe | segment_id | Straße | Bezirk | Kfz | Rad | Führung | Bedarf m | verfügbar m | Passung | Abbau | Skizze | Prüfen | geprüft |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| Zufall | `seg_08ff06fc4e198f0e` | Eichengrund | Altona | ETW30 | BASIS | Mischverkehr | 10.8 | 12.0 | passt | nan | [SVG](profiles_sample/seg_08ff06fc4e198f0e.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553299,5936023]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.570359/9.804847) · [OSM](https://www.openstreetmap.org/?mlat=53.570359&mlon=9.804847#map=18/53.570359/9.804847) | ☐ |
| Zufall | `seg_2625829deddad73b` | Hohenzollernring | Altona | GOW30 | BASIS | Radfahrstreifen | 23.2 | 48.3 | passt | nan | [SVG](profiles_sample/seg_2625829deddad73b.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560796,5934156]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.552764/9.917685) · [OSM](https://www.openstreetmap.org/?mlat=53.552764&mlon=9.917685#map=18/53.552764/9.917685) | ☐ |
| Zufall | `seg_d29fcd6c5f953d12` | Harkortstieg | Altona | ETW30 | HAUPT | Fahrradstraße | 12.0 | 15.0 | passt | nan | [SVG](profiles_sample/seg_d29fcd6c5f953d12.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562229,5934806]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558439/9.939440) · [OSM](https://www.openstreetmap.org/?mlat=53.558439&mlon=9.939440#map=18/53.558439/9.939440) | ☐ |
| Zufall | `seg_f748249a7d829727` | Feldweg 61 | Altona | ETW30 | ERSCHL | Mischverkehr | 9.8 | 4.7 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_f748249a7d829727.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[552095,5937601]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.584669/9.786930) · [OSM](https://www.openstreetmap.org/?mlat=53.584669&mlon=9.786930#map=18/53.584669/9.786930) | ☐ |
| Zufall | `seg_71ab94b63304d70c` | Oberer Landweg | Bergedorf | ETW30 | HAUPT | Fahrradstraße | 10.5 | 30.8 | passt | nan | [SVG](profiles_sample/seg_71ab94b63304d70c.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578733,5927486]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.490444/10.186705) · [OSM](https://www.openstreetmap.org/?mlat=53.490444&mlon=10.186705#map=18/53.490444/10.186705) | ☐ |
| Zufall | `seg_7e6d0cd0f846b072` | Bergedorfer Straße | Bergedorf | GOW50 | none | Radweg je Seite | 30.5 | 36.1 | passt | nan | [SVG](profiles_sample/seg_7e6d0cd0f846b072.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575777,5931140]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.523712/10.143036) · [OSM](https://www.openstreetmap.org/?mlat=53.523712&mlon=10.143036#map=18/53.523712/10.143036) | ☐ |
| Zufall | `seg_2ad00ba4316ccde6` | Radenwisch | Eimsbüttel | ETW30 | HAUPT | Fahrradstraße | 9.0 | 10.0 | passt nach Abbau | D4 | [SVG](profiles_sample/seg_2ad00ba4316ccde6.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561029,5944023]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.641422/9.923132) · [OSM](https://www.openstreetmap.org/?mlat=53.641422&mlon=9.923132#map=18/53.641422/9.923132) | ☐ |
| Zufall | `seg_3a4adc68e516ae25` | Jütländer Allee | Eimsbüttel | ETW30 | BASIS | Mischverkehr | 10.8 | 14.0 | passt | nan | [SVG](profiles_sample/seg_3a4adc68e516ae25.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561465,5939443]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.600203/9.928818) · [OSM](https://www.openstreetmap.org/?mlat=53.600203&mlon=9.928818#map=18/53.600203/9.928818) | ☐ |
| Zufall | `seg_5be2b82046407d07` | Emil-Andresen-Straße | Eimsbüttel | ETW30 | HAUPT | Fahrradstraße | 10.0 | 14.8 | passt | nan | [SVG](profiles_sample/seg_5be2b82046407d07.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563339,5939011]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.596100/9.957056) · [OSM](https://www.openstreetmap.org/?mlat=53.596100&mlon=9.957056#map=18/53.596100/9.957056) | ☐ |
| Zufall | `seg_e58f753dc2c30316` | Thusneldastraße | Eimsbüttel | ETW30 | ERSCHL | Mischverkehr | 9.0 | 9.0 | passt nach Abbau | D1|D4 | [SVG](profiles_sample/seg_e58f753dc2c30316.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561963,5937342]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.581268/9.935937) · [OSM](https://www.openstreetmap.org/?mlat=53.581268&mlon=9.935937#map=18/53.581268/9.935937) | ☐ |
| Zufall | `seg_0953ebe662affe46` | Steinbeker Weg | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 9.8 | 8.3 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_0953ebe662affe46.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574422,5931891]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.530660/10.122782) · [OSM](https://www.openstreetmap.org/?mlat=53.530660&mlon=10.122782#map=18/53.530660/10.122782) | ☐ |
| Zufall | `seg_0a2e095e1a9902bb` | Eiffestraße | Hamburg-Mitte | GOW30 | HAUPT | Radweg je Seite | 24.9 | 27.1 | passt | nan | [SVG](profiles_sample/seg_0a2e095e1a9902bb.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569220,5934247]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.552545/10.044845) · [OSM](https://www.openstreetmap.org/?mlat=53.552545&mlon=10.044845#map=18/53.552545/10.044845) | ☐ |
| Zufall | `seg_1979773f24629248` | Mattkamp | Hamburg-Mitte | ETW30 | BASIS | Mischverkehr | 10.8 | 23.0 | passt | nan | [SVG](profiles_sample/seg_1979773f24629248.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574702,5934228]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.551624/10.127559) · [OSM](https://www.openstreetmap.org/?mlat=53.551624&mlon=10.127559#map=18/53.551624/10.127559) | ☐ |
| Zufall | `seg_78ebc75940535ce1` | Möllner Landstraße | Hamburg-Mitte | ETW30 | HAUPT | Fahrradstraße | 10.0 | 22.9 | passt | nan | [SVG](profiles_sample/seg_78ebc75940535ce1.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575140,5932932]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.539915/10.133870) · [OSM](https://www.openstreetmap.org/?mlat=53.539915&mlon=10.133870#map=18/53.539915/10.133870) | ☐ |
| Zufall | `seg_ac5bef8d0388c524` | Georgswerder Damm | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 12.0 | 19.9 | passt | nan | [SVG](profiles_sample/seg_ac5bef8d0388c524.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568020,5931246]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.525726/10.026079) · [OSM](https://www.openstreetmap.org/?mlat=53.525726&mlon=10.026079#map=18/53.525726/10.026079) | ☐ |
| Zufall | `seg_1ebfe9be416603de` | Suhrenkamp | Hamburg-Nord | ETW30 | HAUPT | Fahrradstraße | 10.0 | 12.9 | passt | nan | [SVG](profiles_sample/seg_1ebfe9be416603de.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567173,5941752]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.620261/10.015566) · [OSM](https://www.openstreetmap.org/?mlat=53.620261&mlon=10.015566#map=18/53.620261/10.015566) | ☐ |
| Zufall | `seg_48a8488f8933c766` | Mundsburger Damm | Hamburg-Nord | GOW30 | HAUPT | Radweg je Seite | 27.4 | 27.6 | passt | nan | [SVG](profiles_sample/seg_48a8488f8933c766.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567507,5935638]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.565269/10.019289) · [OSM](https://www.openstreetmap.org/?mlat=53.565269&mlon=10.019289#map=18/53.565269/10.019289) | ☐ |
| Zufall | `seg_4e16cea18be2d86f` | Moorreye | Hamburg-Nord | ETW30 | ERSCHL | Mischverkehr | 10.8 | 17.0 | passt | nan | [SVG](profiles_sample/seg_4e16cea18be2d86f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567732,5944496]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.644842/10.024604) · [OSM](https://www.openstreetmap.org/?mlat=53.644842&mlon=10.024604#map=18/53.644842/10.024604) | ☐ |
| Zufall | `seg_ab5f4653e380bba9` | Bilser Straße | Hamburg-Nord | ETW30 | HAUPT | Fahrradstraße | 10.0 | 12.9 | passt | nan | [SVG](profiles_sample/seg_ab5f4653e380bba9.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566359,5940101]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.605528/10.002906) · [OSM](https://www.openstreetmap.org/?mlat=53.605528&mlon=10.002906#map=18/53.605528/10.002906) | ☐ |
| Zufall | `seg_0f343a2c4f34e209` | Harburger Rathausstraße | Harburg | ETW30 | BASIS | Mischverkehr | 13.2 | 14.9 | passt | nan | [SVG](profiles_sample/seg_0f343a2c4f34e209.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565176,5923747]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.458696/9.981618) · [OSM](https://www.openstreetmap.org/?mlat=53.458696&mlon=9.981618#map=18/53.458696/9.981618) | ☐ |
| Zufall | `seg_5ed2531b568edd73` | Striepenweg | Harburg | ETW30 | HAUPT | Fahrradstraße | 10.0 | 22.8 | passt | nan | [SVG](profiles_sample/seg_5ed2531b568edd73.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558407,5925325]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.473666/9.879987) · [OSM](https://www.openstreetmap.org/?mlat=53.473666&mlon=9.879987#map=18/53.473666/9.879987) | ☐ |
| Zufall | `seg_c96e80f8e4c595cc` | Binnenfeld | Harburg | ETW30 | HAUPT | Fahrradstraße | 10.0 | 14.7 | passt | nan | [SVG](profiles_sample/seg_c96e80f8e4c595cc.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563849,5921745]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.440860/9.961239) · [OSM](https://www.openstreetmap.org/?mlat=53.440860&mlon=9.961239#map=18/53.440860/9.961239) | ☐ |
| Zufall | `seg_02c4ab91dfa1367a` | Schleusenredder / Mühlenredder | Wandsbek | ETW30 | HAUPT | Fahrradstraße | 10.0 | 12.8 | passt | nan | [SVG](profiles_sample/seg_02c4ab91dfa1367a.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574482,5951424]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.706192/10.128369) · [OSM](https://www.openstreetmap.org/?mlat=53.706192&mlon=10.128369#map=18/53.706192/10.128369) | ☐ |
| Zufall | `seg_3c4db2a61f511755` | Thiedeweg | Wandsbek | ETW30 | HAUPT | Fahrradstraße | 10.0 | 11.2 | passt | nan | [SVG](profiles_sample/seg_3c4db2a61f511755.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571600,5937780]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.583976/10.081569) · [OSM](https://www.openstreetmap.org/?mlat=53.583976&mlon=10.081569#map=18/53.583976/10.081569) | ☐ |
| Zufall | `seg_5538b0d201a328a0` | Sieker Landstraße | Wandsbek | GOW30 | HAUPT | Radfahrstreifen | 16.8 | 18.8 | passt nach Abbau | D2|fallback|D4 | [SVG](profiles_sample/seg_5538b0d201a328a0.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577621,5940435]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.606980/10.173161) · [OSM](https://www.openstreetmap.org/?mlat=53.606980&mlon=10.173161#map=18/53.606980/10.173161) | ☐ |
| Zufall | `seg_6b3744e4c42adbfe` | Oktaviostraße | Wandsbek | ETW30 | HAUPT | Fahrradstraße | 11.5 | 10.9 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_6b3744e4c42adbfe.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572934,5935859]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.566526/10.101264) · [OSM](https://www.openstreetmap.org/?mlat=53.566526&mlon=10.101264#map=18/53.566526/10.101264) | ☐ |
| Zufall | `seg_a2d1818f7d7b03ea` | Grootmoorweg | Wandsbek | ETW_ERF | ERSCHL | Mischverkehr | 4.8 | 7.0 | passt | nan | [SVG](profiles_sample/seg_a2d1818f7d7b03ea.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572827,5943160]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.632156/10.101351) · [OSM](https://www.openstreetmap.org/?mlat=53.632156&mlon=10.101351#map=18/53.632156/10.101351) | ☐ |
| Zufall | `seg_ab31d7f0a902680f` | Rodenbeker Straße | Wandsbek | ETW30 | ERSCHL | Mischverkehr | 10.8 | 27.3 | passt | nan | [SVG](profiles_sample/seg_ab31d7f0a902680f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574149,5947976]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.675248/10.122498) · [OSM](https://www.openstreetmap.org/?mlat=53.675248&mlon=10.122498#map=18/53.675248/10.122498) | ☐ |
| Zufall | `seg_e2905f4c5a09ffc6` | Bramfelder Chaussee | Wandsbek | GOW50 | HAUPT | Radweg je Seite | 19.5 | 26.4 | passt nach Abbau | D2|D3 | [SVG](profiles_sample/seg_e2905f4c5a09ffc6.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571804,5942664]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.627841/10.085779) · [OSM](https://www.openstreetmap.org/?mlat=53.627841&mlon=10.085779#map=18/53.627841/10.085779) | ☐ |
| Zufall | `seg_e1b84e6f0b140bfd` | Emmetal | nan | ETW30 | ERSCHL | Mischverkehr | 11.5 | 9.8 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_e1b84e6f0b140bfd.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559630,5923113]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.453655/9.897992) · [OSM](https://www.openstreetmap.org/?mlat=53.453655&mlon=9.897992#map=18/53.453655/9.897992) | ☐ |
| am breitesten | `seg_4dbd2b1c32ab013f` | Foorthkamp | Hamburg-Nord | ETW30 | ERSCHL | Mischverkehr | 13.2 | 77.5 | passt | nan | [SVG](profiles_sample/seg_4dbd2b1c32ab013f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567184,5946303]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.661157/10.016711) · [OSM](https://www.openstreetmap.org/?mlat=53.661157&mlon=10.016711#map=18/53.661157/10.016711) | ☐ |
| am breitesten | `seg_fc49f8757247b9f9` | Wendlohstieg | Eimsbüttel | ETW30 | ERSCHL | Mischverkehr | 10.8 | 77.0 | passt | nan | [SVG](profiles_sample/seg_fc49f8757247b9f9.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561751,5942662]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.629106/9.933786) · [OSM](https://www.openstreetmap.org/?mlat=53.629106&mlon=9.933786#map=18/53.629106/9.933786) | ☐ |
| am breitesten | `seg_acbd875df0e2d263` | Brücke des 17. Juni | Harburg | GOW50 | ERSCHL | Radweg je Seite | 22.5 | 76.9 | passt | nan | [SVG](profiles_sample/seg_acbd875df0e2d263.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565988,5925119]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470919/9.994142) · [OSM](https://www.openstreetmap.org/?mlat=53.470919&mlon=9.994142#map=18/53.470919/9.994142) | ☐ |
| am breitesten | `seg_a2a3f7396d1f5979` | Löwenzahnweg | Altona | ETW30 | BASIS | Mischverkehr | 14.8 | 76.0 | passt | nan | [SVG](profiles_sample/seg_a2a3f7396d1f5979.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557212,5937627]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.584369/9.864226) · [OSM](https://www.openstreetmap.org/?mlat=53.584369&mlon=9.864226#map=18/53.584369/9.864226) | ☐ |
| am breitesten | `seg_a7a3f9eb51e6058a` | Billhorner Brückenstraße / Billhorner Brücke | Hamburg-Mitte | GOW50 | RSV | Radweg je Seite | 32.5 | 75.7 | passt | nan | [SVG](profiles_sample/seg_a7a3f9eb51e6058a.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568239,5932345]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.535575/10.029617) · [OSM](https://www.openstreetmap.org/?mlat=53.535575&mlon=10.029617#map=18/53.535575/10.029617) | ☐ |
| am breitesten | `seg_3092d50608aed695` | Hannoversche Straße | Harburg | GOW50 | ERSCHL | Radweg je Seite | 22.0 | 74.0 | passt | nan | [SVG](profiles_sample/seg_3092d50608aed695.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565639,5923014]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.452048/9.988439) · [OSM](https://www.openstreetmap.org/?mlat=53.452048&mlon=9.988439#map=18/53.452048/9.988439) | ☐ |
| am breitesten | `seg_7cea60c66a63b99a` | Finkenwerder Straße | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 10.0 | 71.2 | passt | nan | [SVG](profiles_sample/seg_7cea60c66a63b99a.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559670,5929878]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.514453/9.899877) · [OSM](https://www.openstreetmap.org/?mlat=53.514453&mlon=9.899877#map=18/53.514453/9.899877) | ☐ |
| am breitesten | `seg_bc98ce13e2cbee57` | Eimsbütteler Marktplatz | Eimsbüttel | GOW30 | HAUPT | Radweg je Seite | 20.0 | 70.1 | passt | nan | [SVG](profiles_sample/seg_bc98ce13e2cbee57.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562562,5936428]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572983/9.944795) · [OSM](https://www.openstreetmap.org/?mlat=53.572983&mlon=9.944795#map=18/53.572983/9.944795) | ☐ |
| am breitesten | `seg_5190df2af336f5fa` | – | Eimsbüttel | ETW30 | HAUPT | Fahrradstraße | 10.0 | 69.1 | passt | nan | [SVG](profiles_sample/seg_5190df2af336f5fa.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562625,5938713]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.593506/9.946203) · [OSM](https://www.openstreetmap.org/?mlat=53.593506&mlon=9.946203#map=18/53.593506/9.946203) | ☐ |
| am breitesten | `seg_a2762df8a578868f` | Bekstück | Eimsbüttel | ETW30 | ERSCHL | Mischverkehr | 13.2 | 69.0 | passt | nan | [SVG](profiles_sample/seg_a2762df8a578868f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563826,5940870]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.612754/9.964784) · [OSM](https://www.openstreetmap.org/?mlat=53.612754&mlon=9.964784#map=18/53.612754/9.964784) | ☐ |
| am breitesten | `seg_d11b514be57f85e2` | Flughafenstraße | Hamburg-Nord | ETW30 | HAUPT | Fahrradstraße | 12.5 | 68.9 | passt | nan | [SVG](profiles_sample/seg_d11b514be57f85e2.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566653,5942820]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.629920/10.007934) · [OSM](https://www.openstreetmap.org/?mlat=53.629920&mlon=10.007934#map=18/53.629920/10.007934) | ☐ |
| am breitesten | `seg_fcd752a9d1a86a5d` | Am Sandtorkai | Hamburg-Mitte | GOW30 | ERSCHL | Radfahrstreifen | 22.4 | 68.2 | passt | nan | [SVG](profiles_sample/seg_fcd752a9d1a86a5d.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566084,5933257]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.544053/9.997307) · [OSM](https://www.openstreetmap.org/?mlat=53.544053&mlon=9.997307#map=18/53.544053/9.997307) | ☐ |
| am breitesten | `seg_61d788dca9101b87` | Finkenwerder Straße | Hamburg-Mitte | GOW50 | none | Radweg je Seite | 19.0 | 68.0 | passt | nan | [SVG](profiles_sample/seg_61d788dca9101b87.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561276,5930098]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.516241/9.924133) · [OSM](https://www.openstreetmap.org/?mlat=53.516241&mlon=9.924133#map=18/53.516241/9.924133) | ☐ |
| am breitesten | `seg_d387e3b4b45177f7` | Adenauerallee | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 14.5 | 67.7 | passt | nan | [SVG](profiles_sample/seg_d387e3b4b45177f7.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567223,5934208]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.552457/10.014699) · [OSM](https://www.openstreetmap.org/?mlat=53.552457&mlon=10.014699#map=18/53.552457/10.014699) | ☐ |
| am breitesten | `seg_420d5e53b5dd820e` | Vorsetzen / Baumwall | Hamburg-Mitte | GOW30 | ERSCHL | Radfahrstreifen | 20.0 | 67.3 | passt | nan | [SVG](profiles_sample/seg_420d5e53b5dd820e.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564897,5933244]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.544083/9.979396) · [OSM](https://www.openstreetmap.org/?mlat=53.544083&mlon=9.979396#map=18/53.544083/9.979396) | ☐ |
| am breitesten | `seg_d0e8ba17634e49ca` | Überseering | Hamburg-Nord | GOW30 | HAUPT | Radweg je Seite | 20.0 | 67.0 | passt | nan | [SVG](profiles_sample/seg_d0e8ba17634e49ca.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567846,5939635]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.601145/10.025279) · [OSM](https://www.openstreetmap.org/?mlat=53.601145&mlon=10.025279#map=18/53.601145/10.025279) | ☐ |
| am breitesten | `seg_c3e47cd973e9b5d2` | Lohbrügger Markt | Bergedorf | GOW30 | ERSCHL | Radfahrstreifen | 24.9 | 66.9 | passt | nan | [SVG](profiles_sample/seg_c3e47cd973e9b5d2.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580050,5927998]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.494843/10.206673) · [OSM](https://www.openstreetmap.org/?mlat=53.494843&mlon=10.206673#map=18/53.494843/10.206673) | ☐ |
| am breitesten | `seg_3616db96e9486a3d` | Hebebrandstraße | Hamburg-Nord | GOW50 | ERSCHL | Radweg je Seite | 22.5 | 66.6 | passt | nan | [SVG](profiles_sample/seg_3616db96e9486a3d.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568285,5940337]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607394/10.032062) · [OSM](https://www.openstreetmap.org/?mlat=53.607394&mlon=10.032062#map=18/53.607394/10.032062) | ☐ |
| am breitesten | `seg_e56dd3f086922231` | Friedensallee | Altona | ETW30 | RSV | Fahrradstraße | 10.5 | 66.5 | passt | nan | [SVG](profiles_sample/seg_e56dd3f086922231.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559715,5935459]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564604/9.901624) · [OSM](https://www.openstreetmap.org/?mlat=53.564604&mlon=9.901624#map=18/53.564604/9.901624) | ☐ |
| am breitesten | `seg_d8a1a287fca94793` | Ernst-Merck-Straße | Hamburg-Mitte | ETW30 | BASIS | Mischverkehr | 13.2 | 66.4 | passt | nan | [SVG](profiles_sample/seg_d8a1a287fca94793.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566608,5934433]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.554553/10.005458) · [OSM](https://www.openstreetmap.org/?mlat=53.554553&mlon=10.005458#map=18/53.554553/10.005458) | ☐ |
| am engsten | `seg_62fb2a90f492573f` | Bullertweg | Hamburg-Mitte | ETW30 | HAUPT | Fahrradstraße | 9.0 | 2.4 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_62fb2a90f492573f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568455,5928501]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.501000/10.032042) · [OSM](https://www.openstreetmap.org/?mlat=53.501000&mlon=10.032042#map=18/53.501000/10.032042) | ☐ |
| am engsten | `seg_693c64e252eaded2` | Wildgrund | Eimsbüttel | ETW30 | HAUPT | Fahrradstraße | 9.0 | 2.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_693c64e252eaded2.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561581,5941820]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.621556/9.931050) · [OSM](https://www.openstreetmap.org/?mlat=53.621556&mlon=9.931050#map=18/53.621556/9.931050) | ☐ |
| am engsten | `seg_73049fbda31028cb` | Birkenweg | Wandsbek | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_73049fbda31028cb.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574519,5946252]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.659707/10.127681) · [OSM](https://www.openstreetmap.org/?mlat=53.659707&mlon=10.127681#map=18/53.659707/10.127681) | ☐ |
| am engsten | `seg_98cc08aff1b66f2e` | Hügelhain | Harburg | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_98cc08aff1b66f2e.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562518,5922291]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.445926/9.941305) · [OSM](https://www.openstreetmap.org/?mlat=53.445926&mlon=9.941305#map=18/53.445926/9.941305) | ☐ |
| am engsten | `seg_8b5b1cfe85865b04` | Kielkamp | Altona | ETW30 | ERSCHL | Mischverkehr | 9.0 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_8b5b1cfe85865b04.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559795,5936500]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.573948/9.903032) · [OSM](https://www.openstreetmap.org/?mlat=53.573948&mlon=9.903032#map=18/53.573948/9.903032) | ☐ |
| am engsten | `seg_6eb298c350f0d8d0` | Holtkoppel 17a-17f | Hamburg-Nord | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_6eb298c350f0d8d0.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566472,5944079]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.641260/10.005470) · [OSM](https://www.openstreetmap.org/?mlat=53.641260&mlon=10.005470#map=18/53.641260/10.005470) | ☐ |
| am engsten | `seg_946d407d2bda5ac5` | Wulmstal | Harburg | ETW30 | HAUPT | Fahrradstraße | 9.0 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_946d407d2bda5ac5.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559128,5923157]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.454106/9.890435) · [OSM](https://www.openstreetmap.org/?mlat=53.454106&mlon=9.890435#map=18/53.454106/9.890435) | ☐ |
| am engsten | `seg_4297cf5c2c015321` | Hans-Lange-Straße | Altona | ETW_ERF | none | Mischverkehr | 4.8 | 2.6 | passt nicht | D6 | [SVG](profiles_sample/seg_4297cf5c2c015321.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553205,5934743]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558868/9.803217) · [OSM](https://www.openstreetmap.org/?mlat=53.558868&mlon=9.803217#map=18/53.558868/9.803217) | ☐ |
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
| am engsten | `seg_a02e21fff55b5d73` | Fischbeker Heuweg | Harburg | ETW30 | HAUPT | Fahrradstraße | 9.0 | 2.9 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_a02e21fff55b5d73.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554889,5925384]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.474581/9.826998) · [OSM](https://www.openstreetmap.org/?mlat=53.474581&mlon=9.826998#map=18/53.474581/9.826998) | ☐ |
| am engsten | `seg_a8d3c8ef5763338b` | Günselstieg | Wandsbek | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.9 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_a8d3c8ef5763338b.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570840,5941107]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.613980/10.070851) · [OSM](https://www.openstreetmap.org/?mlat=53.613980&mlon=10.070851#map=18/53.613980/10.070851) | ☐ |

## Grenzen

- Busse je Spitzenstunde aus der Abfahrtsstunde der ersten Haltestelle je Fahrt; auf langen Linien liegt die Stunde am Abschnitt später (PRF-02, docs/open_questions.md).
- Verfügbare Breite nur auf rund 58 % der Abschnitte (ALKIS-Verkehrsfläche); ohne Breite keine Passung.
- Ist-Parken nur, wo OSM parking erfasst ist; ohne Angabe kein Parken im Soll-Profil (PRF-03).
- Bushaltestellen (PL-05), Abbiegestreifen (L-05) und die Seitenbedingung PL-02 sind nicht im Streckenprofil.
- GOW30 mit Radfahrstreifen: Radfahrstreifen kommen zur CROW-Fahrbahnbreite hinzu (Annahme, offen).
- Bei bahnigkeit 2 beschreibt das Profil den ganzen Straßenraum; beide Richtungsfahrbahnen bekommen dasselbe Profil.

Quellen: OpenStreetMap-Mitwirkende (ODbL); Freie und Hansestadt Hamburg, ALKIS, Verkehrsmengen und Fahrstreifen (dl-de/by-2.0); HVV-Fahrplandaten GTFS (Transparenzportal Hamburg, dl-de/by-2.0).
