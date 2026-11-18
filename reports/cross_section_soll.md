# Soll-Querschnitt: Fahrstreifen, Lage der Radanlagen, Raumaufteilung (Stufe c06)

Erzeugt 2026-11-17T22:30:26+00:00 mit pipeline/c06_cross_section_soll.py · design_rules.yaml 0.12.0 · cycling_rules.yaml 0.13.0 · nicht amtlicher Entwurf. Regeln L-01…07, PL-01…06 und PRF-01…07 sind Annahmen bzw. Entwürfe (status draft) und vor Gebrauch fachlich zu prüfen.

Verfügbare Breite = width_p10_m der Variante Verkehrsfläche (maßgeblich); die Variante Fassade zeigt das Potenzial inklusive Vorgärten. Das gewünschte Profil enthält Gehwege (Regelmaß), die Radanlage mit Sollbreite aus Prompt 18, ÖPNV, Fahrbahn, Trennstreifen, Bäume (GOW), Ladezone bei Geschäftsnutzung (im Park- oder Baumstreifen, sonst eigener Streifen) und Parken nur dort, wo OSM heute Parken zeigt (Entscheidung 2026-11-06) und die Kategorie es erlaubt (PRF-03 parking_by_category: GOW50 und ETW_ERF keins, GOW30 nur Parkstreifen, ETW30 wie Ist). Passt es nicht, gilt die Kaskade D1, D3, D2, Fallback, D4, D5, D6, D7 (PRF-06).

## Kurzfassung

- 36 526 Abschnitte, 4 998 km; bewertet (Profilregeln und Breite vorhanden): 3 861 km. Ohne Breite: 337 km; ohne Profilregeln: 800 km.
- passt: 2 018 km (52 % der bewerteten Länge).
- passt nach Abbau: 899 km (23 % der bewerteten Länge).
- passt nicht: 944 km (24 % der bewerteten Länge).
- Vorschlag GOW50 → GOW30 (D5): 209 Abschnitte, 22.4 km – nicht übernommen, Entscheidung über overrides/overrides.csv.
- GOW30 mit Kfz-Menge über der Kapazität eines Fahrstreifens je Richtung (L-07, capacity_reduction_needed): 189 Abschnitte, 28.1 km; nötige Reduktion im Median 5 091 Kfz/Tag.
- GTFS: repräsentativer Werktag 2026-04-29 (Upload__hvv_Rohdaten_GTFS_Fpl_20260408.ZIP); Straßenbahnrouten im Feed: 0. Busfahrstreifen Soll: 63.3 km.

## km je fit_class und Straßenkategorie

| Kategorie | passt | passt nach Abbau | passt nicht | nicht bewertet | gesamt |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0.0 | 0.0 | 0.0 | 189.2 | 189.2 |
| GOW50 | 309.1 | 275.8 | 8.3 | 14.0 | 607.3 |
| GOW30 | 40.8 | 54.5 | 51.5 | 2.1 | 148.9 |
| ETW30 | 1 568.6 | 566.4 | 881.6 | 307.3 | 3 323.9 |
| ETW_ERF | 99.1 | 2.7 | 2.6 | 13.5 | 118.0 |

### Verkehrsfläche gegen Fassade (km, nur mit beiden Breiten)

| Verkehrsfläche \ Fassade | passt | passt nach Abbau | passt nicht |
| --- | ---: | ---: | ---: |
| passt | 1 802.4 | 6.1 | 2.2 |
| passt nach Abbau | 771.3 | 60.7 | 1.2 |
| passt nicht | 746.8 | 13.0 | 8.3 |

## Abbaustufen

Häufigkeit je Stufe (ein Abschnitt kann mehrere Stufen haben). Eine Stufe zählt nur, wenn sie das Profil verändert.

| Stufe | Maßnahme | Abschnitte | km | Anteil an bewerteter Länge |
| --- | --- | ---: | ---: | ---: |
| D1 | Parken und Ladezone entfernen | 2 833 | 379.6 | 9.8 % |
| D3 | zweiten Kfz-Fahrstreifen streichen | 1 468 | 157.2 | 4.1 % |
| D2 | neuer Baumstreifen → Baumscheiben im Trenn-/Seitenraum | 2 044 | 262.2 | 6.8 % |
| fallback | Fallback der Matrixzelle (Prompt 18) | 203 | 27.4 | 0.7 % |
| D4 | Rad- und Gehweg auf Mindestbreite | 8 652 | 1 415.5 | 36.7 % |
| D5 | Vorschlag GOW50 → GOW30 (C-G30-02) | 209 | 22.4 | 0.6 % |
| D6 | Flag: Einrichtungsverkehr / Durchfahrtsunterbrechung prüfen | 5 656 | 944.1 | 24.5 % |
| D7 | Flag: Radroute auf Parallelstraße verlegen | 337 | 57.7 | 1.5 % |

Letzte wirksame Stufe bei „passt nach Abbau“ (km):

D1 191.4 · D3 125.5 · D2 98.6 · fallback 9.9 · D4 460.0 · D5 14.1

## Fahrstreifen Ist → Soll (km)

Ist je Richtung aus amtlichen Fahrstreifen (sonst OSM lanes, PRF-01). Soll nach L-01…L-06; L-06 verhindert jeden Zuwachs ohne Override (eine Override-Ebene für Fahrstreifen gibt es noch nicht).

| Ist \ Soll | 1 | 1 + Bus | 2 | shared | – |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 288.5 | 0.0 | 0.0 | 2 930.6 | 84.7 |
| 2 | 173.9 | 39.4 | 112.0 | 85.7 | 83.8 |
| 3 | 35.4 | 16.0 | 56.7 | 15.1 | 14.1 |
| 4 | 5.1 | 6.8 | 17.3 | 1.7 | 6.2 |
| 5 | 0.0 | 0.6 | 2.3 | 0.5 | 0.4 |
| 6 | 0.0 | 0.1 | 0.8 | 0.1 | 0.0 |
| unbekannt | 0.8 | 0.5 | 0.1 | 408.1 | 0.0 |

Weniger Kfz-Fahrstreifen je Richtung im Soll: 354.4 km (davon an GOW50 329.8 km). Zusätzlich D3 im Profil: 157.2 km.

## Fälle D5: Vorschlag GOW50 → GOW30 (C-G30-02)

209 Abschnitte, 22.4 km. Längste 40, je Straße und Bezirk zusammengefasst:

| Straße | Bezirk | Kfz | Rad | Abschnitte | km | verfügbar m (Median) | Bedarf m (Median) | Beispiel |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Luruper Hauptstraße | Altona | GOW50 | HAUPT | 10 | 1.51 | 21.5 | 18.0 | `seg_18c1c8fd83e416ef` |
| Rahlstedter Straße | Wandsbek | GOW50 | HAUPT | 10 | 1.28 | 18.0 | 18.0 | `seg_249dcaa103e67551` |
| Bramfelder Chaussee | Wandsbek | GOW50 | HAUPT | 5 | 0.77 | 23.0 | 18.0 | `seg_0deb113e7b913bf7` |
| Kieler Straße | Eimsbüttel | GOW50 | HAUPT | 4 | 0.75 | 17.8 | 18.0 | `seg_c233062678af90a8` |
| Rodigallee | Wandsbek | GOW50 | HAUPT | 5 | 0.72 | 23.0 | 15.5 | `seg_109e2fbdeaa800bc` |
| Rahlstedter Straße | Wandsbek | GOW50 | BASIS | 7 | 0.67 | 18.0 | 18.0 | `seg_31be3a0f3d9cd46d` |
| Nedderfeld | Hamburg-Nord | GOW50 | HAUPT | 1 | 0.67 | 17.0 | 18.0 | `seg_aa5407704b13547b` |
| Stresemannstraße | Altona | GOW50 | ERSCHL | 4 | 0.64 | 21.8 | 15.5 | `seg_31593b8e022c865f` |
| Farnhornweg | Altona | GOW50 | HAUPT | 4 | 0.60 | 17.0 | 15.5 | `seg_19c6219f387e811c` |
| Curslacker Neuer Deich | Bergedorf | GOW50 | HAUPT | 4 | 0.59 | 20.9 | 15.5 | `seg_24b1b4e09c38573e` |
| Winsener Straße | Harburg | GOW50 | BASIS | 4 | 0.47 | 21.3 | 18.0 | `seg_04a5d1507a4e4758` |
| Lemsahler Landstraße | Wandsbek | GOW50 | BASIS | 1 | 0.40 | 18.6 | 18.0 | `seg_3140e7b6ea5d345f` |
| Jüthornstraße | Wandsbek | GOW50 | HAUPT | 2 | 0.40 | 23.2 | 16.8 | `seg_59214ba3a0168428` |
| Curslacker Neuer Deich | Bergedorf | GOW50 | ERSCHL | 6 | 0.37 | 19.0 | 15.5 | `seg_2bc2e079c0620265` |
| Bremer Straße | Harburg | GOW50 | none | 1 | 0.33 | 18.4 | 18.0 | `seg_a5cfff24d0c26435` |
| Bahrenfelder Chaussee | Altona | GOW50 | BASIS | 2 | 0.33 | 14.2 | 16.7 | `seg_10b9a464ef2097b9` |
| Erdkampsweg | Hamburg-Nord | GOW50 | HAUPT | 2 | 0.33 | 17.0 | 18.0 | `seg_1b137635678df2b1` |
| Elbgaustraße | Eimsbüttel | GOW50 | HAUPT | 2 | 0.32 | 18.0 | 18.0 | `seg_62e2c6585d2121ca` |
| Krausestraße | Hamburg-Nord | GOW50 | HAUPT | 1 | 0.30 | 17.0 | 18.0 | `seg_b68f2f598cf565dd` |
| Bergedorfer Straße | Bergedorf | GOW50 | HAUPT | 1 | 0.29 | 24.4 | 18.0 | `seg_1ce2a6282e5e8b47` |
| Krausestraße | Hamburg-Nord | GOW50 | BASIS | 1 | 0.27 | 17.0 | 18.0 | `seg_067046d5fb26c354` |
| Krausestraße | Hamburg-Nord | GOW50 | ERSCHL | 3 | 0.26 | 16.9 | 18.0 | `seg_2054fe4d1cff862f` |
| Poppenbüttler Landstraße | Wandsbek | GOW50 | HAUPT | 2 | 0.26 | 16.7 | 18.0 | `seg_68b5f66c27607ed9` |
| Schiffbeker Weg | Hamburg-Mitte | GOW50 | HAUPT | 2 | 0.25 | 24.6 | 18.0 | `seg_5d0430fe09de7a35` |
| Krohnstieg | Hamburg-Nord | GOW50 | HAUPT | 1 | 0.24 | 18.6 | 18.0 | `seg_dc2d571360e243af` |
| Reinbeker Redder | Bergedorf | GOW50 | ERSCHL | 1 | 0.24 | 21.1 | 15.5 | `seg_26c82b76b61029ab` |
| Krausestraße | Hamburg-Nord | GOW50 | RSV | 1 | 0.23 | 16.9 | 18.0 | `seg_094cf78ce3b0aecb` |
| Hummelsbüttler Hauptstraße | Wandsbek | GOW50 | HAUPT | 1 | 0.22 | 17.7 | 18.0 | `seg_bd0bbd2862d80627` |
| Reventlowstraße | Altona | GOW50 | HAUPT | 2 | 0.22 | 17.4 | 16.4 | `seg_35d684d7fa615823` |
| Dürerstraße | Altona | GOW50 | HAUPT | 2 | 0.22 | 17.0 | 18.0 | `seg_4f98d0287e474d53` |
| Bramfelder Straße | Hamburg-Nord | GOW50 | RSV | 2 | 0.22 | 24.7 | 18.0 | `seg_1703d8cd28812401` |
| Poppenbütteler Weg | Wandsbek | GOW50 | HAUPT | 1 | 0.21 | 18.6 | 18.0 | `seg_ad50df0b6b1bd76a` |
| Ritterstraße | Wandsbek | GOW50 | BASIS | 1 | 0.21 | 17.2 | 18.0 | `seg_27ed2241db9fc14a` |
| Steintordamm | Hamburg-Mitte | GOW50 | ERSCHL | 2 | 0.20 | 25.1 | 18.0 | `seg_cd6ae319bdc1b352` |
| Berlinertordamm / Borgfelder Straße | Hamburg-Mitte | GOW50 | ERSCHL | 1 | 0.19 | 17.9 | 18.0 | `seg_59db36a26ff4b337` |
| Bremer Straße | Harburg | GOW50 | HAUPT | 1 | 0.19 | 12.9 | 15.5 | `seg_263459ba392e498f` |
| Hummelsbüttler Hauptstraße | Wandsbek | GOW50 | BASIS | 2 | 0.19 | 17.2 | 18.0 | `seg_93b7113650f452a2` |
| Blankeneser Landstraße | Altona | GOW50 | ERSCHL | 2 | 0.19 | 17.1 | 18.0 | `seg_4dab9d7376faba64` |
| Kurt-Schumacher-Allee / Altmannbrücke | Hamburg-Mitte | GOW50 | HAUPT | 1 | 0.18 | 17.4 | 18.0 | `seg_14821c6880357a79` |
| Winsener Straße | Harburg | GOW50 | HAUPT | 3 | 0.17 | 25.1 | 18.0 | `seg_532bfc804c101bbc` |

## Fälle D6: Flag: Einrichtungsverkehr / Durchfahrtsunterbrechung prüfen

5 656 Abschnitte, 944.1 km. Längste 40, je Straße und Bezirk zusammengefasst:

| Straße | Bezirk | Kfz | Rad | Abschnitte | km | verfügbar m (Median) | Bedarf m (Median) | Beispiel |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| (ohne Namen) | Hamburg-Mitte | ETW30 | BASIS | 8 | 4.75 | 8.4 | 9.8 | `seg_0ba8afeeda9be278` |
| Elbchaussee | Altona | GOW30 | HAUPT | 12 | 4.16 | 11.1 | 15.5 | `seg_095ae2689e067006` |
| Moorwerder Hauptdeich | Hamburg-Mitte | ETW30 | HAUPT | 6 | 3.42 | 8.3 | 9.8 | `seg_471bc3129ecccfdf` |
| Duvenstedter Triftweg / Langenreiher Weg | Wandsbek | ETW30 | HAUPT | 1 | 2.95 | 3.0 | 9.8 | `seg_be1fbefc540be72f` |
| Eversween | Hamburg-Mitte | ETW30 | ERSCHL | 3 | 2.60 | 11.5 | 11.5 | `seg_1418f89bb01333ff` |
| Falkensteiner Ufer | Altona | ETW30 | HAUPT | 8 | 2.29 | 6.4 | 9.8 | `seg_1b0f130473ae92f5` |
| Moorwerder Hauptdeich | Hamburg-Mitte | ETW30 | ERSCHL | 4 | 2.14 | 8.1 | 11.5 | `seg_012525751224d503` |
| Finkenwerder Süderdeich / Süderkirchenweg | Hamburg-Mitte | ETW30 | ERSCHL | 1 | 2.07 | 7.9 | 9.8 | `seg_aa01d1f1f774f9e3` |
| Hohe-Schaar-Straße | Hamburg-Mitte | GOW30 | ERSCHL | 9 | 2.04 | 14.7 | 15.5 | `seg_041bf1bffc8768d7` |
| Wiet | Hamburg-Mitte | ETW30 | ERSCHL | 1 | 1.88 | 7.3 | 9.8 | `seg_2f0b1863a6eaabb2` |
| Puckaffer Weg | Wandsbek | ETW30 | ERSCHL | 8 | 1.80 | 9.1 | 9.8 | `seg_659f97f5ab7790ed` |
| Finkenrieker Hauptdeich | Hamburg-Mitte | ETW30 | ERSCHL | 5 | 1.77 | 5.5 | 9.8 | `seg_09c5ef0ea218b4ab` |
| Walter-Hammer-Weg | Bergedorf | ETW30 | HAUPT | 1 | 1.73 | 5.0 | 9.8 | `seg_791d0d6faad5e65e` |
| Niendorfer Gehege | Eimsbüttel | ETW30 | HAUPT | 3 | 1.69 | 9.1 | 9.8 | `seg_95a931e2a8b279ea` |
| Siedenfelder Weg | Hamburg-Mitte | ETW30 | HAUPT | 2 | 1.66 | 7.8 | 9.8 | `seg_7fd526806f07de8c` |
| Raakmoorgrund / Weg Nr. 651 | Hamburg-Nord | ETW30 | HAUPT | 1 | 1.65 | 6.0 | 9.8 | `seg_ecf40172d73d6546` |
| Große Straße | Harburg | ETW30 | HAUPT | 3 | 1.57 | 9.4 | 9.8 | `seg_c7f5fba7773a25e8` |
| Garstedter Weg | Eimsbüttel | GOW30 | HAUPT | 9 | 1.54 | 13.9 | 15.5 | `seg_15f35a37699009b9` |
| Berliner Ufer | Hamburg-Mitte | ETW30 | ERSCHL | 1 | 1.54 | 4.8 | 9.8 | `seg_b65f34b9ef2b1049` |
| Am Ochsenzoll | Hamburg-Nord | ETW30 | BASIS | 3 | 1.46 | 5.1 | 9.8 | `seg_aa8b6df36b4c4943` |
| Mesterbrooksweg | Wandsbek | ETW30 | ERSCHL | 3 | 1.46 | 8.2 | 9.8 | `seg_0f7b44ffb9b6294a` |
| Hans-Ulrich-Höller-Weg | Bergedorf | ETW30 | BASIS | 1 | 1.41 | 5.0 | 9.8 | `seg_9c01c86026c409b4` |
| Kobberdiekskoppel / Ödenweg | Wandsbek | ETW30 | ERSCHL | 1 | 1.39 | 8.2 | 9.8 | `seg_83c6f1d534de6622` |
| Kuhtrift | Harburg | ETW30 | ERSCHL | 7 | 1.38 | 5.3 | 9.8 | `seg_200e180f02fde42e` |
| Poppenbütteler Chaussee | Wandsbek | GOW30 | ERSCHL | 7 | 1.36 | 9.7 | 15.5 | `seg_17f60dcf357e2a14` |
| Wulmsberggrund | Harburg | ETW30 | HAUPT | 3 | 1.35 | 4.4 | 9.8 | `seg_12b7e9bc1394309e` |
| Köterdamm | Hamburg-Mitte | ETW30 | ERSCHL | 2 | 1.34 | 8.0 | 9.8 | `seg_1a176f153e0174eb` |
| Ellerholzweg | Hamburg-Mitte | ETW30 | ERSCHL | 4 | 1.32 | 9.0 | 9.8 | `seg_41858456ea6919d4` |
| Hagenweg | Wandsbek | ETW30 | ERSCHL | 2 | 1.31 | 8.8 | 9.8 | `seg_b59fc543632c9b89` |
| Friedrichshulder Weg | Altona | ETW30 | HAUPT | 1 | 1.31 | 7.4 | 9.8 | `seg_e9ede1815b056b10` |
| Moorwerder Norderdeich | Hamburg-Mitte | ETW30 | HAUPT | 2 | 1.29 | 5.1 | 9.8 | `seg_1da1e89613f6cde1` |
| Brünschentwiete | Altona | ETW30 | HAUPT | 3 | 1.29 | 7.2 | 9.8 | `seg_0b7991f535355d1c` |
| Finkenwerder Landscheideweg | Hamburg-Mitte | ETW30 | BASIS | 3 | 1.28 | 8.2 | 9.8 | `seg_11205afd99725fda` |
| Osterfelddeich / Kirchenaußendeichsweg | Hamburg-Mitte | ETW30 | HAUPT | 1 | 1.28 | 8.5 | 9.8 | `seg_f107760b70327da7` |
| Kattwykdamm | Hamburg-Mitte | GOW30 | ERSCHL | 6 | 1.28 | 13.0 | 13.4 | `seg_1b8e45ab81ba0191` |
| Stillhorner Hauptdeich | Hamburg-Mitte | ETW30 | HAUPT | 2 | 1.27 | 6.4 | 9.8 | `seg_6e9d83c097a58e71` |
| Maldfeldstraße | Harburg | GOW30 | ERSCHL | 2 | 1.26 | 5.2 | 12.8 | `seg_62e6f106c665fcdc` |
| Einlagedeich | Hamburg-Mitte | ETW30 | HAUPT | 1 | 1.24 | 7.2 | 9.8 | `seg_64a83dbfbc6d2c96` |
| Pollhorner Hauptdeich | Hamburg-Mitte | GOW30 | ERSCHL | 1 | 1.24 | 8.7 | 12.2 | `seg_429717595f22897b` |
| (ohne Namen) | Harburg | ETW30 | ERSCHL | 3 | 1.21 | 6.1 | 9.8 | `seg_0784076265a9bda6` |

## Fälle D7: Flag: Radroute auf Parallelstraße verlegen

337 Abschnitte, 57.7 km. Längste 40, je Straße und Bezirk zusammengefasst:

| Straße | Bezirk | Kfz | Rad | Abschnitte | km | verfügbar m (Median) | Bedarf m (Median) | Beispiel |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Elbchaussee | Altona | GOW30 | HAUPT | 12 | 4.16 | 11.1 | 15.5 | `seg_095ae2689e067006` |
| Hohe-Schaar-Straße | Hamburg-Mitte | GOW30 | ERSCHL | 9 | 2.04 | 14.7 | 15.5 | `seg_041bf1bffc8768d7` |
| Garstedter Weg | Eimsbüttel | GOW30 | HAUPT | 9 | 1.54 | 13.9 | 15.5 | `seg_15f35a37699009b9` |
| Poppenbütteler Chaussee | Wandsbek | GOW30 | ERSCHL | 7 | 1.36 | 9.7 | 15.5 | `seg_17f60dcf357e2a14` |
| Kattwykdamm | Hamburg-Mitte | GOW30 | ERSCHL | 6 | 1.28 | 13.0 | 13.4 | `seg_1b8e45ab81ba0191` |
| Maldfeldstraße | Harburg | GOW30 | ERSCHL | 2 | 1.26 | 5.2 | 12.8 | `seg_62e6f106c665fcdc` |
| Pollhorner Hauptdeich | Hamburg-Mitte | GOW30 | ERSCHL | 1 | 1.24 | 8.7 | 12.2 | `seg_429717595f22897b` |
| Reiherstieg-Hauptdeich | Hamburg-Mitte | GOW30 | ERSCHL | 2 | 1.03 | 10.3 | 13.4 | `seg_4c3ca98a1f2942fa` |
| Meiendorfer Straße | Wandsbek | GOW30 | HAUPT | 3 | 1.02 | 15.6 | 18.0 | `seg_15249df5d95a501e` |
| Rahlstedter Straße | Wandsbek | GOW50 | HAUPT | 7 | 1.02 | 17.9 | 18.0 | `seg_249dcaa103e67551` |
| Rissener Landstraße | Altona | GOW30 | HAUPT | 1 | 0.97 | 12.9 | 13.4 | `seg_bbaed5c23367fbdf` |
| Wellingsbüttler Weg | Wandsbek | GOW30 | HAUPT | 4 | 0.97 | 13.9 | 15.5 | `seg_8232dbac21641f26` |
| Schmidts Breite | Hamburg-Mitte | GOW30 | ERSCHL | 4 | 0.89 | 11.3 | 12.2 | `seg_4ede7ec38f7fb372` |
| Francoper Straße | Harburg | GOW30 | ERSCHL | 2 | 0.88 | 8.2 | 12.2 | `seg_2cd77ed942e139d9` |
| Ehestorfer Weg | Harburg | GOW30 | HAUPT | 2 | 0.78 | 9.6 | 12.2 | `seg_71f041587ef4854d` |
| Hafenrandstraße | Hamburg-Mitte | GOW30 | ERSCHL | 1 | 0.77 | 14.0 | 15.5 | `seg_ce0603f23047a60c` |
| Moorburger Straße | Harburg | GOW30 | ERSCHL | 3 | 0.76 | 14.9 | 15.5 | `seg_3315c26eadc8d159` |
| Garstedter Weg | Eimsbüttel | GOW30 | BASIS | 6 | 0.75 | 13.9 | 15.5 | `seg_31586e0ccf94c0cc` |
| Wellingsbüttler Weg | Wandsbek | GOW30 | BASIS | 5 | 0.72 | 13.2 | 18.0 | `seg_0658711bfb38f869` |
| Aue-Hauptdeich | Hamburg-Mitte | GOW30 | BASIS | 2 | 0.72 | 12.1 | 12.2 | `seg_620f28acdc81233f` |
| Lemsahler Landstraße | Wandsbek | GOW30 | ERSCHL | 1 | 0.70 | 10.8 | 15.5 | `seg_9a1db680f64d374e` |
| Seehafenstraße | Harburg | GOW30 | ERSCHL | 2 | 0.69 | 11.9 | 15.5 | `seg_6c5bd4d8e45a5ae3` |
| Meckelfelder Weg | Harburg | GOW30 | ERSCHL | 4 | 0.68 | 9.3 | 13.4 | `seg_39ef70c47c8ad7a7` |
| Friedhofstraße | Harburg | GOW30 | HAUPT | 5 | 0.68 | 9.5 | 15.5 | `seg_0b972cbad9999e38` |
| Ehestorfer Weg | Harburg | GOW30 | ERSCHL | 1 | 0.67 | 7.8 | 12.2 | `seg_aaf7eec60da1d6d1` |
| Nedderfeld | Hamburg-Nord | GOW50 | HAUPT | 1 | 0.67 | 17.0 | 18.0 | `seg_aa5407704b13547b` |
| Gazellenkamp | Eimsbüttel | GOW30 | HAUPT | 2 | 0.66 | 12.0 | 13.4 | `seg_84efc14cffb00c7b` |
| Ulzburger Straße | Wandsbek | GOW30 | HAUPT | 3 | 0.65 | 15.0 | 15.5 | `seg_8f3f9b3c715c31d6` |
| Oldesloer Straße | Eimsbüttel | GOW30 | BASIS | 4 | 0.62 | 13.7 | 15.5 | `seg_2d2a22df6cb0d52a` |
| Am Frankenberg | Harburg | GOW30 | HAUPT | 3 | 0.58 | 10.5 | 12.2 | `seg_27383ed4d77b7e4f` |
| Langenbeker Weg | Harburg | GOW30 | HAUPT | 4 | 0.55 | 9.9 | 12.2 | `seg_21a7de81a0076e20` |
| Waldweg | Wandsbek | GOW30 | BASIS | 4 | 0.54 | 13.3 | 15.5 | `seg_2ff2bc58e900639e` |
| Binnenfeldredder | Bergedorf | GOW30 | HAUPT | 4 | 0.52 | 14.0 | 15.5 | `seg_1743da708bd9bf66` |
| Eißendorfer Waldweg | Harburg | GOW30 | HAUPT | 1 | 0.52 | 9.3 | 12.2 | `seg_896df8d623e86dbd` |
| Beim Farenland | Wandsbek | GOW30 | ERSCHL | 3 | 0.50 | 10.0 | 12.2 | `seg_20071d6c3070d1f0` |
| Wedeler Landstraße | Altona | GOW30 | HAUPT | 2 | 0.50 | 13.2 | 15.5 | `seg_0552b19135b13d9e` |
| Stresemannstraße | Altona | GOW30 | ERSCHL | 1 | 0.48 | 14.8 | 18.0 | `seg_6b87397b2e176f23` |
| An der Alsterschleife | Wandsbek | GOW30 | HAUPT | 1 | 0.47 | 10.7 | 12.2 | `seg_c5db1848591c3a8f` |
| Poppenbüttler Hauptstraße | Wandsbek | GOW30 | BASIS | 4 | 0.46 | 13.1 | 13.4 | `seg_510dca558bd59282` |
| Zweibrückenstraße | Hamburg-Mitte | GOW30 | HAUPT | 4 | 0.45 | 13.8 | 15.5 | `seg_3898002b25e1ce46` |

## Hinweise (Flags)

| Flag | Bedeutung | Abschnitte | km |
| --- | --- | ---: | ---: |
| `width_unknown` | keine verfügbare Breite (width_p10_m fehlt) | 3 435 | 336.9 |
| `no_profile_rules` | keine Profilregeln (SW, GOW80, ETW60 oder ohne Kategorie, PRF-04) | 2 294 | 799.6 |
| `dtv_unknown` | DTV fehlt an GOW50 – Fahrstreifen = Ist (PRF-01), confidence low | 818 | 54.2 |
| `lanes_capped_l06` | Soll-Fahrstreifen auf Ist begrenzt (L-06, kein Override) | 757 | 95.9 |
| `pl02_unchecked` | Zweirichtungsradweg: Seitenbedingung PL-02 nicht prüfbar | 0 | 0.0 |
| `trees_as_pits` | neuer Baumstreifen entfällt, Bäume als Baumscheiben im Trenn- oder Seitenraum (D2) | 2 044 | 262.2 |
| `gow30_dtv_above_profile` | GOW30 mit DTV über dem breiten CROW-Profil (Soll-Führung Radweg, S-05) | 463 | 61.6 |
| `capacity_reduction_needed` | GOW30: Kfz-Menge über der Kapazität eines Fahrstreifens je Richtung – Reduktion nötig (L-07) | 189 | 28.1 |
| `D6` | Flag: Einrichtungsverkehr / Durchfahrtsunterbrechung prüfen | 5 656 | 944.1 |
| `D7` | Flag: Radroute auf Parallelstraße verlegen | 337 | 57.7 |

confidence: high 3 602 km, medium 208 km, low 1 187 km

## fit_class je Bezirk (Anteil km)

| Bezirk | Abschnitte | km | passt | passt nach Abbau | passt nicht | nicht bewertet |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 4 886 | 620.5 | 37 % | 27 % | 28 % | 9 % |
| Bergedorf | 1 957 | 209.3 | 57 % | 18 % | 20 % | 6 % |
| Eimsbüttel | 4 004 | 470.4 | 51 % | 24 % | 18 % | 7 % |
| Hamburg-Mitte | 6 839 | 881.3 | 49 % | 16 % | 18 % | 18 % |
| Hamburg-Nord | 5 136 | 563.3 | 61 % | 17 % | 14 % | 8 % |
| Harburg | 3 348 | 465.2 | 37 % | 20 % | 27 % | 16 % |
| Wandsbek | 7 542 | 1 030.4 | 46 % | 25 % | 28 % | 2 % |
| ohne Bezirk | 990 | 146.9 | 4 % | 1 % | 2 % | 93 % |
| **gesamt** | 34 702 | 4 387.3 | 46 % | 21 % | 22 % | 12 % |

## Querschnitts-Skizzen (70 Profile)

reports/profiles_sample/<segment_id>.svg: 30 Zufallsabschnitte (über Bezirke verteilt, Seed 42), die 20 breitesten und die 20 engsten (verfügbare Breite). Elemente maßstäblich, blau gestrichelt die verfügbare Breite. Prüfung gegen Luftbild und Straßenbilder: Spalte „geprüft“ von Hand ausfüllen.

| Gruppe | segment_id | Straße | Bezirk | Kfz | Rad | Führung | Bedarf m | verfügbar m | Passung | Abbau | Skizze | Prüfen | geprüft |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| Zufall | `seg_0c20c4b7963908f5` | Am Sumpfgraben | Altona | ETW30 | ERSCHL | Mischverkehr | 9.8 | 7.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_0c20c4b7963908f5.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557662,5940361]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.608887/9.871528) · [OSM](https://www.openstreetmap.org/?mlat=53.608887&mlon=9.871528#map=18/53.608887/9.871528) | ☐ |
| Zufall | `seg_337e0bab04a62db1` | Klövensteenweg | Altona | ETW30 | ERSCHL | Mischverkehr | 10.8 | 13.9 | passt nach Abbau | D1 | [SVG](profiles_sample/seg_337e0bab04a62db1.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[550564,5937886]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.587374/9.763852) · [OSM](https://www.openstreetmap.org/?mlat=53.587374&mlon=9.763852#map=18/53.587374/9.763852) | ☐ |
| Zufall | `seg_7057d4d9f0b70bb4` | Manteuffelstraße | Altona | ETW30 | HAUPT | Fahrradstraße | 10.8 | 26.0 | passt | nan | [SVG](profiles_sample/seg_7057d4d9f0b70bb4.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554998,5934979]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560804/9.830326) · [OSM](https://www.openstreetmap.org/?mlat=53.560804&mlon=9.830326#map=18/53.560804/9.830326) | ☐ |
| Zufall | `seg_7ec16be77aa4f1d3` | Behnstraße | Altona | ETW30 | HAUPT | Fahrradstraße | 14.8 | 22.2 | passt | nan | [SVG](profiles_sample/seg_7ec16be77aa4f1d3.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562437,5933493]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546617/9.942317) · [OSM](https://www.openstreetmap.org/?mlat=53.546617&mlon=9.942317#map=18/53.546617/9.942317) | ☐ |
| Zufall | `seg_2ad11cad361a65f3` | Mary-Marcus-Kehre | Bergedorf | ETW_ERF | ERSCHL | Mischverkehr | 4.8 | 19.0 | passt | nan | [SVG](profiles_sample/seg_2ad11cad361a65f3.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578148,5927017]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.486319/10.177777) · [OSM](https://www.openstreetmap.org/?mlat=53.486319&mlon=10.177777#map=18/53.486319/10.177777) | ☐ |
| Zufall | `seg_4540c335d10b5685` | Ulmenhang | Bergedorf | ETW30 | ERSCHL | Mischverkehr | 9.8 | 6.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_4540c335d10b5685.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579706,5927700]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.492218/10.201413) · [OSM](https://www.openstreetmap.org/?mlat=53.492218&mlon=10.201413#map=18/53.492218/10.201413) | ☐ |
| Zufall | `seg_1cc6f3ba9463d373` | Osterfeldstraße | Eimsbüttel | GOW50 | ERSCHL | Radweg je Seite | 22.5 | 29.1 | passt nach Abbau | D3 | [SVG](profiles_sample/seg_1cc6f3ba9463d373.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563870,5939389]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.599438/9.965145) · [OSM](https://www.openstreetmap.org/?mlat=53.599438&mlon=9.965145#map=18/53.599438/9.965145) | ☐ |
| Zufall | `seg_c06ccbe1087fa5e5` | Binsbarg | Eimsbüttel | GOW50 | none | Radweg je Seite | 18.5 | 19.5 | passt nach Abbau | D3|D2 | [SVG](profiles_sample/seg_c06ccbe1087fa5e5.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560760,5938408]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.590985/9.917974) · [OSM](https://www.openstreetmap.org/?mlat=53.590985&mlon=9.917974#map=18/53.590985/9.917974) | ☐ |
| Zufall | `seg_cff436841e62ecf8` | Niendorfer Gehege | Eimsbüttel | ETW30 | HAUPT | Fahrradstraße | 10.8 | 27.4 | passt | nan | [SVG](profiles_sample/seg_cff436841e62ecf8.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562495,5941492]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.618504/9.944799) · [OSM](https://www.openstreetmap.org/?mlat=53.618504&mlon=9.944799#map=18/53.618504/9.944799) | ☐ |
| Zufall | `seg_d0f9eb1279ea00a2` | Niendorfer Straße | Eimsbüttel | ETW30 | ERSCHL | Mischverkehr | 15.0 | 15.9 | passt | nan | [SVG](profiles_sample/seg_d0f9eb1279ea00a2.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563209,5940082]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.605744/9.955307) · [OSM](https://www.openstreetmap.org/?mlat=53.605744&mlon=9.955307#map=18/53.605744/9.955307) | ☐ |
| Zufall | `seg_0c2c0b827e31be64` | Willy-Brandt-Straße | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 13.2 | 41.8 | passt | nan | [SVG](profiles_sample/seg_0c2c0b827e31be64.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565352,5933641]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.547596/9.986331) · [OSM](https://www.openstreetmap.org/?mlat=53.547596&mlon=9.986331#map=18/53.547596/9.986331) | ☐ |
| Zufall | `seg_1e9aaa4df265c8b7` | Hammer Landstraße | Hamburg-Mitte | GOW50 | ERSCHL | Radweg je Seite | 30.5 | 44.4 | passt | nan | [SVG](profiles_sample/seg_1e9aaa4df265c8b7.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570054,5934531]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.554983/10.057486) · [OSM](https://www.openstreetmap.org/?mlat=53.554983&mlon=10.057486#map=18/53.554983/10.057486) | ☐ |
| Zufall | `seg_991b2777bbc66a56` | Hans-Sander-Straße | Hamburg-Mitte | ETW_ERF | HAUPT | eigene Trasse | 7.2 | 15.0 | passt | nan | [SVG](profiles_sample/seg_991b2777bbc66a56.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565420,5930367]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.518162/9.986676) · [OSM](https://www.openstreetmap.org/?mlat=53.518162&mlon=9.986676#map=18/53.518162/9.986676) | ☐ |
| Zufall | `seg_c65789f9243aaf61` | Detlev-Bremer-Straße | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 12.5 | 15.0 | passt | nan | [SVG](profiles_sample/seg_c65789f9243aaf61.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563944,5934067]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.551597/9.965181) · [OSM](https://www.openstreetmap.org/?mlat=53.551597&mlon=9.965181#map=18/53.551597/9.965181) | ☐ |
| Zufall | `seg_d7778491df2b2aeb` | Caspar-Voght-Straße | Hamburg-Mitte | ETW30 | ERSCHL | Mischverkehr | 9.8 | 10.4 | passt nach Abbau | D1|D4 | [SVG](profiles_sample/seg_d7778491df2b2aeb.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570255,5934982]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559009/10.060632) · [OSM](https://www.openstreetmap.org/?mlat=53.559009&mlon=10.060632#map=18/53.559009/10.060632) | ☐ |
| Zufall | `seg_0ce68fe5cf817c19` | Beckermannweg | Hamburg-Nord | ETW30 | ERSCHL | Mischverkehr | 10.8 | 11.2 | passt | nan | [SVG](profiles_sample/seg_0ce68fe5cf817c19.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566608,5946608]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.663971/10.008065) · [OSM](https://www.openstreetmap.org/?mlat=53.663971&mlon=10.008065#map=18/53.663971/10.008065) | ☐ |
| Zufall | `seg_296f650955e81515` | Barmbeker Straße | Hamburg-Nord | GOW50 | ERSCHL | Radweg je Seite | 30.5 | 32.0 | passt | nan | [SVG](profiles_sample/seg_296f650955e81515.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566361,5938647]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.592457/10.002621) · [OSM](https://www.openstreetmap.org/?mlat=53.592457&mlon=10.002621#map=18/53.592457/10.002621) | ☐ |
| Zufall | `seg_6230eeac8f450ca9` | Weg beim Jäger | Hamburg-Nord | ETW30 | HAUPT | Fahrradstraße | 12.8 | 20.0 | passt | nan | [SVG](profiles_sample/seg_6230eeac8f450ca9.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565164,5941143]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.615034/9.985063) · [OSM](https://www.openstreetmap.org/?mlat=53.615034&mlon=9.985063#map=18/53.615034/9.985063) | ☐ |
| Zufall | `seg_680f15dba73d6dc3` | Alfred-Johann-Levy-Straße | Hamburg-Nord | ETW30 | BASIS | Mischverkehr | 14.8 | 19.0 | passt | nan | [SVG](profiles_sample/seg_680f15dba73d6dc3.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568663,5939856]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.603023/10.037670) · [OSM](https://www.openstreetmap.org/?mlat=53.603023&mlon=10.037670#map=18/53.603023/10.037670) | ☐ |
| Zufall | `seg_e0f61b9f6c093595` | Semperstraße | Hamburg-Nord | ETW30 | ERSCHL | Mischverkehr | 13.2 | 17.0 | passt | nan | [SVG](profiles_sample/seg_e0f61b9f6c093595.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567578,5938181]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.588116/10.020913) · [OSM](https://www.openstreetmap.org/?mlat=53.588116&mlon=10.020913#map=18/53.588116/10.020913) | ☐ |
| Zufall | `seg_0b90647ba524e0a3` | Geutensweg | Harburg | ETW30 | ERSCHL | Mischverkehr | 10.8 | 14.9 | passt | nan | [SVG](profiles_sample/seg_0b90647ba524e0a3.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555698,5925401]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.474649/9.839188) · [OSM](https://www.openstreetmap.org/?mlat=53.474649&mlon=9.839188#map=18/53.474649/9.839188) | ☐ |
| Zufall | `seg_c6d3724c921c0b78` | Wilstorfer Straße | Harburg | GOW50 | HAUPT | Radweg je Seite | 25.7 | 28.3 | passt nach Abbau | D2|D4 | [SVG](profiles_sample/seg_c6d3724c921c0b78.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565386,5923563]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.457016/9.984743) · [OSM](https://www.openstreetmap.org/?mlat=53.457016&mlon=9.984743#map=18/53.457016/9.984743) | ☐ |
| Zufall | `seg_d4e2996f3f4ce787` | Ostheide | Harburg | ETW30 | BASIS | Mischverkehr | 9.8 | 9.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_d4e2996f3f4ce787.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557037,5924351]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.465067/9.859171) · [OSM](https://www.openstreetmap.org/?mlat=53.465067&mlon=9.859171#map=18/53.465067/9.859171) | ☐ |
| Zufall | `seg_3847814a8f0f60f5` | Thomas-Mann-Straße | Wandsbek | ETW30 | BASIS | Mischverkehr | 12.5 | 14.0 | passt | nan | [SVG](profiles_sample/seg_3847814a8f0f60f5.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573842,5942666]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.627573/10.116583) · [OSM](https://www.openstreetmap.org/?mlat=53.627573&mlon=10.116583#map=18/53.627573/10.116583) | ☐ |
| Zufall | `seg_79687387a89efb09` | Sthamerstraße | Wandsbek | ETW30 | HAUPT | Fahrradstraße | 9.8 | 6.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_79687387a89efb09.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575301,5949864]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.692049/10.140394) · [OSM](https://www.openstreetmap.org/?mlat=53.692049&mlon=10.140394#map=18/53.692049/10.140394) | ☐ |
| Zufall | `seg_9d2cffde89b12109` | Rabenhorst | Wandsbek | ETW30 | HAUPT | Fahrradstraße | 10.8 | 13.0 | passt | nan | [SVG](profiles_sample/seg_9d2cffde89b12109.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572054,5944113]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.640825/10.089893) · [OSM](https://www.openstreetmap.org/?mlat=53.640825&mlon=10.089893#map=18/53.640825/10.089893) | ☐ |
| Zufall | `seg_ba64bc5985c35e1f` | Tonndorfer Hauptstraße | Wandsbek | GOW50 | HAUPT | Radweg je Seite | 19.2 | 19.9 | passt nach Abbau | D2|D4 | [SVG](profiles_sample/seg_ba64bc5985c35e1f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575270,5938810]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.592718/10.137238) · [OSM](https://www.openstreetmap.org/?mlat=53.592718&mlon=10.137238#map=18/53.592718/10.137238) | ☐ |
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
| am breitesten | `seg_bc98ce13e2cbee57` | Eimsbütteler Marktplatz | Eimsbüttel | GOW50 | HAUPT | Radweg je Seite | 23.5 | 70.1 | passt | nan | [SVG](profiles_sample/seg_bc98ce13e2cbee57.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562562,5936428]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572983/9.944795) · [OSM](https://www.openstreetmap.org/?mlat=53.572983&mlon=9.944795#map=18/53.572983/9.944795) | ☐ |
| am breitesten | `seg_9299750046b2e39a` | Eimsbütteler Marktplatz | Eimsbüttel | GOW50 | HAUPT | Radweg je Seite | 23.0 | 70.1 | passt | nan | [SVG](profiles_sample/seg_9299750046b2e39a.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562473,5936398]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572723/9.943437) · [OSM](https://www.openstreetmap.org/?mlat=53.572723&mlon=9.943437#map=18/53.572723/9.943437) | ☐ |
| am breitesten | `seg_5190df2af336f5fa` | – | Eimsbüttel | ETW30 | HAUPT | Fahrradstraße | 10.8 | 69.1 | passt | nan | [SVG](profiles_sample/seg_5190df2af336f5fa.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562625,5938713]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.593506/9.946203) · [OSM](https://www.openstreetmap.org/?mlat=53.593506&mlon=9.946203#map=18/53.593506/9.946203) | ☐ |
| am engsten | `seg_62fb2a90f492573f` | Bullertweg | Hamburg-Mitte | ETW30 | HAUPT | Fahrradstraße | 9.8 | 2.4 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_62fb2a90f492573f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568455,5928501]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.501000/10.032042) · [OSM](https://www.openstreetmap.org/?mlat=53.501000&mlon=10.032042#map=18/53.501000/10.032042) | ☐ |
| am engsten | `seg_693c64e252eaded2` | Wildgrund | Eimsbüttel | ETW30 | HAUPT | Fahrradstraße | 9.8 | 2.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_693c64e252eaded2.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561581,5941820]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.621556/9.931050) · [OSM](https://www.openstreetmap.org/?mlat=53.621556&mlon=9.931050#map=18/53.621556/9.931050) | ☐ |
| am engsten | `seg_73049fbda31028cb` | Birkenweg | Wandsbek | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_73049fbda31028cb.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574519,5946252]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.659707/10.127681) · [OSM](https://www.openstreetmap.org/?mlat=53.659707&mlon=10.127681#map=18/53.659707/10.127681) | ☐ |
| am engsten | `seg_98cc08aff1b66f2e` | Hügelhain | Harburg | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.5 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_98cc08aff1b66f2e.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562518,5922291]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.445926/9.941305) · [OSM](https://www.openstreetmap.org/?mlat=53.445926&mlon=9.941305#map=18/53.445926/9.941305) | ☐ |
| am engsten | `seg_2a212a9eebd3db10` | Kielkamp | Altona | ETW30 | HAUPT | Fahrradstraße | 9.8 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_2a212a9eebd3db10.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559774,5936346]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572572/9.902684) · [OSM](https://www.openstreetmap.org/?mlat=53.572572&mlon=9.902684#map=18/53.572572/9.902684) | ☐ |
| am engsten | `seg_8b5b1cfe85865b04` | Kielkamp | Altona | ETW30 | ERSCHL | Mischverkehr | 9.0 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_8b5b1cfe85865b04.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559795,5936500]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.573948/9.903032) · [OSM](https://www.openstreetmap.org/?mlat=53.573948&mlon=9.903032#map=18/53.573948/9.903032) | ☐ |
| am engsten | `seg_6eb298c350f0d8d0` | Holtkoppel 17a-17f | Hamburg-Nord | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_6eb298c350f0d8d0.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566472,5944079]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.641260/10.005470) · [OSM](https://www.openstreetmap.org/?mlat=53.641260&mlon=10.005470#map=18/53.641260/10.005470) | ☐ |
| am engsten | `seg_946d407d2bda5ac5` | Wulmstal | Harburg | ETW30 | HAUPT | Fahrradstraße | 9.8 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_946d407d2bda5ac5.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559128,5923157]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.454106/9.890435) · [OSM](https://www.openstreetmap.org/?mlat=53.454106&mlon=9.890435#map=18/53.454106/9.890435) | ☐ |
| am engsten | `seg_4297cf5c2c015321` | Hans-Lange-Straße | Altona | ETW_ERF | none | Mischverkehr | 4.8 | 2.6 | passt nicht | D6 | [SVG](profiles_sample/seg_4297cf5c2c015321.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553205,5934743]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558868/9.803217) · [OSM](https://www.openstreetmap.org/?mlat=53.558868&mlon=9.803217#map=18/53.558868/9.803217) | ☐ |
| am engsten | `seg_b91c4915f98dfc0d` | Hans-Lange-Straße | Altona | ETW_ERF | none | Mischverkehr | 4.8 | 2.6 | passt nicht | D6 | [SVG](profiles_sample/seg_b91c4915f98dfc0d.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553235,5934791]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559300/9.803680) · [OSM](https://www.openstreetmap.org/?mlat=53.559300&mlon=9.803680#map=18/53.559300/9.803680) | ☐ |
| am engsten | `seg_fbab51f03791f399` | Zirpenweg | Wandsbek | ETW30 | HAUPT | Fahrradstraße | 9.8 | 2.6 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_fbab51f03791f399.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572819,5935670]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564847/10.099485) · [OSM](https://www.openstreetmap.org/?mlat=53.564847&mlon=10.099485#map=18/53.564847/10.099485) | ☐ |
| am engsten | `seg_f39b5c200a3411b2` | Scharlbargstieg | Harburg | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.7 | passt nicht | D1|D4|D6 | [SVG](profiles_sample/seg_f39b5c200a3411b2.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554627,5923997]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.462137/9.822813) · [OSM](https://www.openstreetmap.org/?mlat=53.462137&mlon=9.822813#map=18/53.462137/9.822813) | ☐ |
| am engsten | `seg_92a1060f84d6d02f` | Beentkamp | Eimsbüttel | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.7 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_92a1060f84d6d02f.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560727,5941613]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.619795/9.918093) · [OSM](https://www.openstreetmap.org/?mlat=53.619795&mlon=9.918093#map=18/53.619795/9.918093) | ☐ |
| am engsten | `seg_22b48d236c70cfc8` | Neuwulmstorfer Schulstraße | Harburg | ETW30 | ERSCHL | Mischverkehr | 9.8 | 2.7 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_22b48d236c70cfc8.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553387,5924779]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.469300/9.804270) · [OSM](https://www.openstreetmap.org/?mlat=53.469300&mlon=9.804270#map=18/53.469300/9.804270) | ☐ |
| am engsten | `seg_a153e0eb11822045` | Weg Nr. 12 | Wandsbek | ETW30 | HAUPT | Fahrradstraße | 9.8 | 2.8 | passt nicht | D4|D6 | [SVG](profiles_sample/seg_a153e0eb11822045.svg) | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573017,5935743]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.565477/10.102489) · [OSM](https://www.openstreetmap.org/?mlat=53.565477&mlon=10.102489#map=18/53.565477/10.102489) | ☐ |
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
- GOW30 mit Radfahrstreifen: die CROW-Spannen enthalten die Radfahrstreifen (Annahme A2, Original nicht geprüft; PRF-04).
- Bestandsbäume sind nicht erfasst; D2 betrifft nur den neuen Baumstreifen (Flag existing_trees_conflict fehlt, docs/open_questions.md).
- Bei bahnigkeit 2 beschreibt das Profil den ganzen Straßenraum; beide Richtungsfahrbahnen bekommen dasselbe Profil.

Quellen: OpenStreetMap-Mitwirkende (ODbL); Freie und Hansestadt Hamburg, ALKIS, Verkehrsmengen und Fahrstreifen (dl-de/by-2.0); HVV-Fahrplandaten GTFS (Transparenzportal Hamburg, dl-de/by-2.0).
