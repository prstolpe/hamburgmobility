# Validierung und Sensitivität

Erzeugt: 2026-11-04T19:57:01+00:00 von `pipeline/validate.py`, rules.yaml 0.11.0. Nicht amtlicher Diskussionsentwurf: Die Automatik schlägt vor, Menschen entscheiden. Grundlage für die externe Fachprüfung (guide.md Teil 7).

## Kurzfassung

- HVS-Abgleich: 99,6 % der HVS-km sind GOW50 oder GOW30; 0,4 km HVS außerhalb, 0,6 km Bezirksstraßen mit GOW50.
- Ist-Tempo: 74,5 % der Soll-ETW30-km (mit bekanntem Tempo) haben heute höchstens 30 km/h; 292 Ausreißer sind mögliche Datenfehler.
- Sensitivität: 293 Abschnitte (28,7 km, 5,1 % der Länge) sind „unsicher“; die Top 30 der Priorität bleiben im Mittel zu 91,8 % gleich.
- Datenqualität: Conflation-Treffer 92,8 % der km, OSM-Gestaltungsmerkmale im Mittel 65,5 % bekannt, ohne Ist-Tempo 7,3 %.
- Manuelle Stichproben, Rückmelderunde und externe Prüfung sind offen.

Vergleich mit dem vorigen Lauf (2026-11-04T19:53:56+00:00, rules.yaml 0.11.0): HVS-km als GOW50/GOW30 99,6 % → 99,6 %; unsicher 293 → 293 Abschnitte. Eine Abbruchgrenze für einen Rückgang (guide.md 3.4) ist nicht festgelegt (docs/open_questions.md).

## Prüfungen dieses Laufs

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| Basislauf reproduziert cat_proposed | ok | 0 Abweichungen bei 4787 Abschnitten |
| Basislauf reproduziert die Priorität | ok | 0 Abweichungen |
| segment_id eindeutig | ok | 4787 Abschnitte |
| Monte-Carlo-Läufe vollständig | ok | 500 Läufe, Seed 20261104 |

## Stand der Prüfungen nach guide.md 7.1

Veröffentlichungsreif erst, wenn Abgleich HVS-Netz, Stichproben vor Ort, Sensitivitätsanalyse und eine Rückmelderunde mit Ortskundigen dokumentiert sind. Auch dann bleibt der Plan ein Diskussionsentwurf.

| Prüfung | Stand | Abschnitt |
| --- | --- | --- |
| Abgleich HVS-Netz | erledigt (automatisch); Abweichungen einzeln begründen: **offen** | 1 |
| Abgleich mit Ist-Tempo | erledigt (automatisch); Datenfehler-Kandidaten prüfen: **offen** | 2 |
| Stichproben vor Ort | **offen** | 5 |
| Sensitivitätsanalyse | erledigt | 3 |
| Datenqualität | erledigt | 4 |
| Ortskundige (Bezirksgruppen, Feuerwehr, Busbetrieb) | **offen** | 5 |
| Externe Fachprüfung (Hochschule oder Planungsbüro) | **offen** – dieser Bericht ist die Grundlage | – |

## 1. Abgleich mit dem HVS-Netz

Kreuztabelle Soll-Kategorie (`cat_final`) × Hauptverkehrsstraße (`in_hvs`, DTV-Linien 2019, S-CONF-04). Erwartung (guide.md 7.1): fast alle HVS-km sind GOW50 oder GOW30; HVS als ETW30 und Bezirksstraßen als GOW50 einzeln begründen.

**Kennzahl: 99,6 % der HVS-km im Arbeitsgebiet sind GOW50 oder GOW30.**

### Arbeitsgebiet gesamt (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil an HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0,4 | 28,0 | 0,0 | 28,4 | 0,4 % |
| GOW50 | 37,5 | 0,6 | 0,0 | 38,1 | 41,5 % |
| GOW30 | 52,4 | 5,0 | 0,0 | 57,5 | 58,1 % |
| ETW30 | 0,0 | 427,4 | 0,0 | 427,4 | 0,0 % |
| ETW_ERF | 0,0 | 10,6 | 0,0 | 10,6 | 0,0 % |
| **Summe** | 90,3 | 471,7 | 0,0 | 562,0 | |

### Bezirk Eimsbüttel (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil an HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0,3 | 25,3 | 0,0 | 25,6 | 0,5 % |
| GOW50 | 29,9 | 0,2 | 0,0 | 30,2 | 39,4 % |
| GOW30 | 45,6 | 3,9 | 0,0 | 49,6 | 60,1 % |
| ETW30 | 0,0 | 347,1 | 0,0 | 347,1 | 0,0 % |
| ETW_ERF | 0,0 | 9,0 | 0,0 | 9,0 | 0,0 % |
| **Summe** | 75,9 | 385,6 | 0,0 | 461,5 | |

### Je Bezirk (Nachbarbezirke nur mit ihrem Anteil am Arbeitsgebiet)

| Bezirk | km | HVS km | davon GOW50/GOW30 | HVS außerhalb GOW50/GOW30 km | Bezirksstraßen mit GOW50 km |
| --- | ---: | ---: | ---: | ---: | ---: |
| Eimsbüttel | 461,5 | 75,9 | 99,5 % | 0,3 | 0,2 |
| Altona | 36,6 | 5,2 | 99,4 % | 0,0 | 0,2 |
| Hamburg-Mitte | 13,4 | 4,4 | 100,0 % | 0,0 | 0,1 |
| Hamburg-Nord | 33,0 | 3,9 | 100,0 % | 0,0 | 0,1 |
| ohne Bezirk | 17,4 | 0,8 | 100,0 % | 0,0 | 0,0 |

### Abweichung A: HVS-Abschnitte außerhalb GOW50/GOW30 (3 Abschnitte, 0,4 km)

Nach Kategorie: SW 3 (0,4 km). SW auf HVS (Autobahnzubringer) ist fachlich folgerichtig; ETW30 und ETW_ERF auf HVS einzeln begründen.

| Bezirk | Straße | Soll | highway | Abschnitte | km | Beispiel |
| --- | --- | --- | --- | ---: | ---: | --- |
| Eimsbüttel | – | SW | motorway_link | 2 | 0,3 | `seg_1c29f75d06449ca9` |
| Altona | – | SW | motorway_link | 1 | 0,0 | `seg_05a7bf220b7ad3fa` |

### Abweichung B: Bezirksstraßen mit GOW50 (17 Abschnitte, 0,6 km)

Bezirksstraße = keine HVS und keine Autobahn. Grund ist immer C-GOW-01 über conn_score ohne GOW30-Auslöser. Kurze Stücke von Hauptstraßen deuten auf Lücken im HVS-Abgleich (nur match exact) hin.

| Bezirk | Straße | Soll | highway | Abschnitte | km | Beispiel |
| --- | --- | --- | --- | ---: | ---: | --- |
| Altona | Spreestraße | GOW50 | tertiary | 3 | 0,2 | `seg_cdc3caa130436e96` |
| Hamburg-Mitte | Lombardsbrücke | GOW50 | primary | 2 | 0,1 | `seg_52c6fa7754021065` |
| Eimsbüttel | Koppelstraße | GOW50 | primary | 1 | 0,1 | `seg_89490ce5545cfa9f` |
| Hamburg-Nord | Martinistraße | GOW50 | tertiary | 1 | 0,1 | `seg_7aad6709464c0bda` |
| Eimsbüttel | Holsteiner Chaussee | GOW50 | primary | 1 | 0,1 | `seg_9af41066e9ac8903` |
| Eimsbüttel | Doormannsweg | GOW50 | primary | 2 | 0,0 | `seg_4d01f5e0c6202387` |
| Eimsbüttel | Grindelallee | GOW50 | primary | 1 | 0,0 | `seg_316bf3ec250dbe56` |
| Hamburg-Mitte | Stephansplatz | GOW50 | tertiary | 1 | 0,0 | `seg_5306dc4ae89a583a` |
| Eimsbüttel | Bundesstraße | GOW50 | primary | 1 | 0,0 | `seg_f12e48a0b33fb951` |
| Hamburg-Mitte | Glockengießerwall | GOW50 | primary | 1 | 0,0 | `seg_fb2a06f6597892fb` |
| Eimsbüttel | – | GOW50 | primary | 1 | 0,0 | `seg_5a3a77f617521da4` |
| Eimsbüttel | Lokstedter Steindamm | GOW50 | primary | 1 | 0,0 | `seg_35d7d10ef10e9c01` |
| Eimsbüttel | Kieler Straße | GOW50 | primary | 1 | 0,0 | `seg_596c7377b0aff893` |

## 2. Soll-ETW30 und Ist-Tempo

Ist-Tempo = amtliches Regeltempo vor OSM maxspeed (S-FEAT-09). Soll-Tempo ETW30 = 30 km/h (categories.ETW30). Erwartung: hoher Anteil; Ausreißer sind Kandidaten für Datenfehler.

**Kennzahl: 74,5 % der Soll-ETW30-km mit bekanntem Ist-Tempo haben heute höchstens 30 km/h** (310,4 von 416,6 km; Ist-Tempo unbekannt: 10,8 km).

### Soll × Ist-Tempo (km, Arbeitsgebiet)

| Soll | ≤ 20 | 30 | 40–50 | > 50 | unbekannt |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0,0 | 0,0 | 5,6 | 20,0 | 2,8 |
| GOW50 | 0,0 | 0,1 | 27,8 | 9,8 | 0,4 |
| GOW30 | 0,0 | 2,7 | 54,7 | 0,0 | 0,0 |
| ETW30 | 3,0 | 307,4 | 105,8 | 0,4 | 10,8 |
| ETW_ERF | 0,1 | 0,8 | 0,1 | 0,0 | 9,5 |

### Ausreißer: Soll-ETW30 mit Ist-Tempo über 30 km/h (1126 Abschnitte, 106,3 km)

Davon **292 Abschnitte (16,0 km) mögliche Datenfehler**: mindestens ein Hinweis widerspricht dem Ist-Tempo oder der Kategorie (Zone 30 laut Zonenebene, Quellen widersprechen sich, nur OSM-Tempo, HVS-Abgleich nur teilweise, kein amtlicher Abgleich). Die übrigen sind Wohn- oder Sammelstraßen mit Tempo 50 ohne Widerspruch in den Daten – dort ist die Diskrepanz fachlich gemeint (D-SPD-01).

| Hinweis | Abschnitte |
| --- | ---: |
| Wohnstraße (OSM) | 286 |
| nur OSM-Tempo | 189 |
| kein amtlicher Abgleich | 183 |
| amtlich und OSM verschieden | 63 |
| HVS-Abgleich nur teilweise | 38 |
| Tempo-30-Zone laut Zonenebene | 6 |

Mögliche Datenfehler nach Straße (längste zuerst, höchstens 30):

| Bezirk | Straße | Abschnitte | km | Ist km/h | Hinweise | Beispiel |
| --- | --- | --- | ---: | ---: | --- | --- |
| Eimsbüttel | Zum Golfplatz / Wendloher Weg | 1 | 1,0 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_eefb9b6756b4777a` |
| Eimsbüttel | Königsberger Straße / Ellerbeker Moordamm | 1 | 0,6 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_f541871e807c340e` |
| Eimsbüttel | Osterstraße | 7 | 0,6 | 50 | nur OSM-Tempo (7), kein amtlicher Abgleich (2) | `seg_f58a4a80942b8a53` |
| Eimsbüttel | Wunderbrunnen | 4 | 0,5 | 50 | amtlich und OSM verschieden (3), Tempo-30-Zone laut Zonenebene (1) | `seg_6e923cc9e7654ca8` |
| Hamburg-Mitte | Tiergartenstraße | 1 | 0,5 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_648de4f55cfd2110` |
| Eimsbüttel | Wählingsallee | 5 | 0,5 | 50 | amtlich und OSM verschieden (5), Wohnstraße (OSM) (5) | `seg_666bddd75dbff752` |
| Hamburg-Mitte | Esplanade | 2 | 0,5 | 50 | HVS-Abgleich nur teilweise (2) | `seg_3a0b8810b048b6d4` |
| Eimsbüttel | Wählingsweg | 3 | 0,4 | 50 | amtlich und OSM verschieden (3), Wohnstraße (OSM) (3) | `seg_15737e57190e37a7` |
| ohne Bezirk | Süntelstraße | 4 | 0,4 | 50 | nur OSM-Tempo (4), kein amtlicher Abgleich (4) | `seg_b7503a0a23a84838` |
| Altona | Diebsteichweg | 1 | 0,4 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_e40db0821a83017f` |
| Eimsbüttel | Harvestehuder Weg | 5 | 0,4 | 50 | amtlich und OSM verschieden (4), nur OSM-Tempo (1), kein amtlicher Abgleich (1) | `seg_a26690e12f1ddd17` |
| Eimsbüttel | – | 20 | 0,3 | 50 | nur OSM-Tempo (20), kein amtlicher Abgleich (20), Wohnstraße (OSM) (3) | `seg_9741f01e4f551455` |
| ohne Bezirk | Kieler Straße | 1 | 0,3 | 50 | nur OSM-Tempo (1), kein amtlicher Abgleich (1) | `seg_56fa9c45de91b617` |
| Eimsbüttel | Oldesloer Straße | 10 | 0,3 | 50 | nur OSM-Tempo (7), kein amtlicher Abgleich (7), HVS-Abgleich nur teilweise (3) | `seg_2e6adb21f74d688b` |
| ohne Bezirk | Schnelsener Weg | 2 | 0,3 | 50 | nur OSM-Tempo (2), kein amtlicher Abgleich (2) | `seg_2ecf85469ecedb69` |
| Eimsbüttel | Frohbösestraße | 1 | 0,2 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_3be5306ed98e0a7f` |
| Eimsbüttel | Deepenstöcken | 4 | 0,2 | 50 | amtlich und OSM verschieden (4), Wohnstraße (OSM) (4) | `seg_6ba46fb9f4bfaf05` |
| Eimsbüttel | Groß Borsteler Straße | 4 | 0,2 | 50 | Wohnstraße (OSM) (4), nur OSM-Tempo (3), kein amtlicher Abgleich (3), amtlich und OSM verschieden (1) | `seg_c3cfbc9c2f29ec81` |
| Eimsbüttel | Sportplatzring | 2 | 0,2 | 50 | HVS-Abgleich nur teilweise (2) | `seg_a2dd83e6c7222900` |
| Altona | Schnackenburgallee | 3 | 0,2 | 60 | HVS-Abgleich nur teilweise (3) | `seg_a095d3aa3c1d1b87` |
| Eimsbüttel | Schäferstraße | 1 | 0,2 | 50 | Tempo-30-Zone laut Zonenebene (1), Wohnstraße (OSM) (1) | `seg_7708456cb9469b05` |
| Eimsbüttel | Methfesselstraße | 5 | 0,2 | 50 | amtlich und OSM verschieden (5), Wohnstraße (OSM) (1) | `seg_a7d0de43ee72d3f1` |
| Eimsbüttel | Garstedter Weg | 6 | 0,2 | 50 | HVS-Abgleich nur teilweise (3), nur OSM-Tempo (2), kein amtlicher Abgleich (2), amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_f899105e58342e19` |
| Eimsbüttel | Hochallee | 1 | 0,2 | 50 | amtlich und OSM verschieden (1) | `seg_86f68500f5b2695d` |
| Hamburg-Nord | Sierichstraße / Herbert-Weichmann-Straße | 1 | 0,2 | 50 | HVS-Abgleich nur teilweise (1) | `seg_57fb054f5cb343db` |
| Eimsbüttel | Sootbörn | 1 | 0,2 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_b799c47f0630b725` |
| Eimsbüttel | Bogenallee | 1 | 0,2 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_3dfc9b132f75159e` |
| Eimsbüttel | Schleswiger Damm | 2 | 0,2 | 50 | HVS-Abgleich nur teilweise (2), nur OSM-Tempo (1), kein amtlicher Abgleich (1) | `seg_ace66a958ae70fa8` |
| ohne Bezirk | Pinneberger Straße | 1 | 0,2 | 50 | nur OSM-Tempo (1), kein amtlicher Abgleich (1) | `seg_e1fa75f846a97ae9` |
| Eimsbüttel | Paul-Sorge-Straße | 2 | 0,2 | 50 | amtlich und OSM verschieden (2), Wohnstraße (OSM) (2) | `seg_638850061180af26` |
| … | 121 weitere Straßen | | | | | |

## 3. Sensitivitätsanalyse

Geprüft wird die Automatik (`cat_proposed`); fachliche Korrekturen bleiben außen vor. Basis: rules.yaml 0.11.0, 4 787 Abschnitte, 562,0 km.

### 3.1 Einzelvariation (V-SENS-01): jede Annahme ±20 %

km mit anderer Kategorie als im Basislauf. Varianten: Annahme-Schwellen der Kaskade und `required_width` in ihren Bedingungen; zusätzlich die Gewichte von conn_score.

| Annahme | Regel | Basis | −20 %: km | Abschnitte | häufigste Wechsel | +20 %: km | Abschnitte | häufigste Wechsel |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| `thresholds.conn_gow` | C-GOW-01 | 0,6 | 39,8 | 386 | ETW30→GOW30 29,4, ETW30→GOW50 10,5 | 5,7 | 82 | GOW30→ETW30 5,0, GOW50→ETW30 0,6 |
| `thresholds.sensitive_radius` | C-G30-01 | 150 | 4,4 | 47 | GOW30→GOW50 4,4 | 5,2 | 65 | GOW50→GOW30 5,2 |
| `thresholds.frontage` | C-G30-01 | 0,4 | 2,4 | 11 | GOW50→GOW30 2,4 | 0,7 | 5 | GOW30→GOW50 0,7 |
| `required_width.GOW50` | C-G30-02 | 16,5 | 0,2 | 2 | GOW30→GOW50 0,2 | 0,6 | 2 | GOW50→GOW30 0,6 |
| `conn_score.betweenness_norm` | scores.conn_score | 0,35 | 2,9 | 31 | GOW30→ETW30 2,5, GOW50→ETW30 0,4 | 6,0 | 60 | ETW30→GOW30 4,6, ETW30→GOW50 1,4 |
| `conn_score.in_hvs` | scores.conn_score | 0,25 | 15,2 | 137 | ETW30→GOW30 11,8, ETW30→GOW50 3,4 | 3,6 | 46 | GOW30→ETW30 3,1, GOW50→ETW30 0,5 |
| `conn_score.bus_trips_weekday_norm` | scores.conn_score | 0,2 | 1,3 | 16 | GOW30→ETW30 1,1, GOW50→ETW30 0,2 | 3,6 | 31 | ETW30→GOW30 2,7, ETW30→GOW50 0,8 |
| `conn_score.dtv_norm` | scores.conn_score | 0,2 | 0,0 | 0 | – | 0,0 | 0 | – |

Nur auf die confidence wirken: `thresholds.near_threshold` (0,1, C-CONF-01). Sie ändern die Kategorie nicht und werden nicht variiert.

Nicht variiert (Annahmen früherer Stufen oder ohne Wirkung auf die Kategorie):

| Annahme | Wert | Einheit | Grund |
| --- | ---: | --- | --- |
| `network.S-NET-03.min_length_m` | 400 | m | Netz (Stufe 2): wirkt nur über einen neuen Lauf ab make network |
| `conflation.S-CONF-01.buffer_m` | 15 | m | Conflation (Stufe 3): wirkt nur über einen neuen Lauf ab make conflate |
| `conflation.S-CONF-01.max_angle_deg` | 20 | Grad (ungerichtet, 0-90) | Conflation (Stufe 3): wirkt nur über einen neuen Lauf ab make conflate |
| `conflation.S-CONF-01.min_overlap_share` | 0,6 | Anteil 0-1 | Conflation (Stufe 3): wirkt nur über einen neuen Lauf ab make conflate |
| `conflation.S-CONF-02.min_length_share` | 0,5 | Anteil 0-1 der Abschnittslänge | Conflation (Stufe 3): wirkt nur über einen neuen Lauf ab make conflate |
| `features.S-FEAT-02.default_speed_motorway` | 100 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-02.default_speed_motorway_link` | 60 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-02.default_speed_trunk` | 70 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-02.default_speed_trunk_link` | 50 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-02.default_speed_primary` | 50 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-02.default_speed_primary_link` | 50 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-02.default_speed_secondary` | 50 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-02.default_speed_secondary_link` | 50 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-02.default_speed_tertiary` | 50 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-02.default_speed_tertiary_link` | 50 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-02.default_speed_unclassified` | 50 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-02.default_speed_residential` | 30 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-02.default_speed_living_street` | 7 | km/h | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-03.buffer_m` | 50 | m | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-04.buffer_m` | 100 | m | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-05.buffer_m` | 20 | m | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `features.S-FEAT-10.node_snap_m` | 1 | m | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
| `crosssection.S-XS-01.simplify_m` | 2 | m | Querschnitt (Stufe 7): wirkt über width_p10_m nur nach neuem Lauf ab make crosssection |
| `crosssection.S-XS-01.spacing_m` | 20 | m | Querschnitt (Stufe 7): wirkt über width_p10_m nur nach neuem Lauf ab make crosssection |
| `crosssection.S-XS-01.half_length_m` | 40 | m | Querschnitt (Stufe 7): wirkt über width_p10_m nur nach neuem Lauf ab make crosssection |
| `crosssection.S-XS-01.tangent_half_m` | 10 | m | Querschnitt (Stufe 7): wirkt über width_p10_m nur nach neuem Lauf ab make crosssection |
| `crosssection.S-XS-04.node_exclusion_m` | 20 | m | Querschnitt (Stufe 7): wirkt über width_p10_m nur nach neuem Lauf ab make crosssection |
| `crosssection.S-XS-05.quantile` | 0,1 | Anteil 0-1 | Querschnitt (Stufe 7): wirkt über width_p10_m nur nach neuem Lauf ab make crosssection |
| `crosssection.S-XS-05.min_run` | 3 | Transekte (Anzahl) | Querschnitt (Stufe 7): wirkt über width_p10_m nur nach neuem Lauf ab make crosssection |
| `coherence.N1.boundary_tolerance_m` | 50 | m | Netzkohärenz: schreibt nur Hinweise, ändert die Kategorie nicht |
| `coherence.N2.max_deflection_deg` | 30 | ° | Netzkohärenz: schreibt nur Hinweise, ändert die Kategorie nicht |
| `coherence.N2.bearing_sample_m` | 15 | m | Netzkohärenz: schreibt nur Hinweise, ändert die Kategorie nicht |
| `coherence.N2.min_run_m` | 200 | m | Netzkohärenz: schreibt nur Hinweise, ändert die Kategorie nicht |
| `coherence.N3.min_area_ha` | 25 | ha | Netzkohärenz: schreibt nur Hinweise, ändert die Kategorie nicht |
| `coherence.N4.max_etw_m` | 300 | m | Netzkohärenz: schreibt nur Hinweise, ändert die Kategorie nicht |
| `coherence.N6.signal_radius_m` | 30 | m | Netzkohärenz: schreibt nur Hinweise, ändert die Kategorie nicht |
| `discrepancy.D-SPD-01.severity_1` | 1 | km/h | Diskrepanz: ändert die Kategorie nicht |
| `discrepancy.D-USE-01.severity_2` | 1,5 | Faktor | Diskrepanz: ändert die Kategorie nicht |
| `discrepancy.D-USE-01.severity_3` | 2 | Faktor | Diskrepanz: ändert die Kategorie nicht |
| `priority.P-RISK-01.snap_m` | 15 | m | Priorität: Zuordnung der Unfälle und Radien je Abschnitt bleiben fest; nur Gewichte variiert |
| `priority.P-RISK-01.min_length_m` | 100 | m | Priorität: Zuordnung der Unfälle und Radien je Abschnitt bleiben fest; nur Gewichte variiert |
| `priority.P-RISK-01.school_kita_radius_m` | 150 | m | Priorität: Zuordnung der Unfälle und Radien je Abschnitt bleiben fest; nur Gewichte variiert |
| `priority.P-RISK-01.period_years` | 5 | Jahre | Priorität: Zuordnung der Unfälle und Radien je Abschnitt bleiben fest; nur Gewichte variiert |
| `feasibility_classes.fits` | 1 | width_ratio | Machbarkeit: ändert die Kategorie nicht |
| `feasibility_classes.tight` | 0,85 | width_ratio | Machbarkeit: ändert die Kategorie nicht |
| `feasibility_classes.does_not_fit` | 0,85 | width_ratio | Machbarkeit: ändert die Kategorie nicht |
| `required_width.carriageway_2lane_m` | 6,5 | m | Machbarkeit (Stufe 7): nicht in einer Bedingung der Kaskade |
| `required_width.GOW50_bus` | 17 | m | Machbarkeit (Stufe 7): nicht in einer Bedingung der Kaskade |
| `required_width.GOW30_narrow` | 10,8 | m | Machbarkeit (Stufe 7): nicht in einer Bedingung der Kaskade |
| `required_width.GOW30_wide` | 13,4 | m | Machbarkeit (Stufe 7): nicht in einer Bedingung der Kaskade |
| `required_width.ETW30` | 10,8 | m | Machbarkeit (Stufe 7): nicht in einer Bedingung der Kaskade |

### 3.2 Monte-Carlo (V-SENS-02): 500 Läufe, Seed 20261104

Je Lauf wird jede der 13 Annahmen (conn_weight, risk_weight, threshold) unabhängig mit einem Faktor gleichverteilt in [0,8; 1,2] multipliziert. Wechselquote je Abschnitt = Anteil der Läufe mit anderer Kategorie. **„unsicher“ ab Wechselquote 0,3 (V-UNC-01).**

**Kennzahl: 293 Abschnitte (28,7 km, 5,1 % der Länge) sind unsicher.** Mindestens einmal gewechselt: 674 Abschnitte (66,3 km).

| Wechselquote | Abschnitte | km |
| --- | ---: | ---: |
| 0 (stabil) | 4 113 | 495,7 |
| über 0 bis 0,1 | 147 | 14,7 |
| über 0,1 bis unter 0,3 | 234 | 22,9 |
| ab 0,3 (unsicher) | 293 | 28,7 |

Unsichere Abschnitte je Soll-Kategorie (Basis) und häufigste andere Kategorie:

| Kategorie | km gesamt | unsicher km | Anteil | häufigste andere Kategorie (km) |
| --- | ---: | ---: | ---: | --- |
| SW | 28,4 | 0,0 | 0,0 % | – |
| GOW50 | 38,1 | 4,9 | 12,9 % | GOW30 (4,4), ETW30 (0,6) |
| GOW30 | 57,5 | 6,2 | 10,8 % | ETW30 (4,5), GOW50 (1,7) |
| ETW30 | 427,4 | 17,6 | 4,1 % | GOW30 (13,8), GOW50 (3,8) |
| ETW_ERF | 10,6 | 0,0 | 0,0 % | – |

Je Bezirk:

| Bezirk | km | unsicher km | Anteil |
| --- | ---: | ---: | ---: |
| Eimsbüttel | 461,5 | 24,1 | 5,2 % |
| Altona | 36,6 | 3,6 | 9,8 % |
| Hamburg-Mitte | 13,4 | 0,5 | 4,1 % |
| Hamburg-Nord | 33,0 | 0,5 | 1,5 % |
| ohne Bezirk | 17,4 | 0,0 | 0,0 % |

Einfluss je Annahme im Monte-Carlo (Korrelation des Faktors mit dem Anteil gewechselter km je Lauf; nur zur Orientierung, nicht kausal):

| Annahme | Korrelation |
| --- | ---: |
| `thresholds.conn_gow` | -0,79 |
| `conn_score.in_hvs` | -0,24 |
| `conn_score.betweenness_norm` | +0,13 |
| `thresholds.frontage` | -0,08 |
| `required_width.GOW50` | +0,05 |
| `conn_score.bus_trips_weekday_norm` | +0,04 |
| `conn_score.dtv_norm` | +0,03 |
| `thresholds.sensitive_radius` | +0,02 |

### 3.3 Priorität: Top 30 im Bezirk Eimsbüttel bei variierten Gewichten

Gleiche Läufe; risk mit variierten `priority.risk_weights`, Diskrepanzen aus dem Basislauf (eine geänderte Kategorie ändert auch die Diskrepanz – das ist hier nicht abgebildet). Im Mittel bleiben **91,8 % der Top 30** in der Top 30. 24 Abschnitte bleiben in mindestens 90 % der Läufe, 2 in weniger als der Hälfte.


### 3.4 Stichprobe: 30 zufällige unsichere Abschnitte im Bezirk Eimsbüttel (Seed 42)

Zur Durchsicht: Welche Kategorie ist fachlich richtig? Befund als Korrektur in overrides/overrides.csv.

| segment_id | Straße | highway | Soll | andere Kategorie | Wechselquote | Wechsel bei ±20 % | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| `seg_0da4a9ea092c0362` | Troplowitzstraße | tertiary | ETW30 | GOW30 (36,8 %) | 0,368 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564040,5937871]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.585767/9.967412) | [Way](https://www.openstreetmap.org/way/682409953) |
| `seg_0e982aa8dcbfae03` | Lohkampstraße | tertiary | ETW30 | GOW50 (41,4 %) | 0,414 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559183,5940660]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.611411/9.894574) | [Way](https://www.openstreetmap.org/way/42413677) |
| `seg_0e98ddd8104fa9bc` | Märkerweg | tertiary | ETW30 | GOW50 (37,6 %) | 0,376 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563212,5944065]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.641538/9.956158) | [Way](https://www.openstreetmap.org/way/4335099) |
| `seg_1e7079b3332dae61` | Hoheluftchaussee | primary | GOW50 | GOW30 (39,4 %) | 0,394 | `thresholds.sensitive_radius:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564575,5937110]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578866/9.975335) | [Way](https://www.openstreetmap.org/way/391821253) |
| `seg_1e8ba8f726ae7270` | Frohmestraße | tertiary | ETW30 | GOW30 (38,2 %) | 0,408 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561285,5942793]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.630334/9.926760) | [Way](https://www.openstreetmap.org/way/149136687) |
| `seg_2397041f834dc48d` | Märkerweg | tertiary | ETW30 | GOW50 (43,8 %) | 0,438 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563299,5944499]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645427/9.957554) | [Way](https://www.openstreetmap.org/way/359743701) |
| `seg_2467dfafc2f66ace` | Troplowitzstraße | tertiary | ETW30 | GOW30 (38,2 %) | 0,382 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563927,5937805]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.585195/9.965684) | [Way](https://www.openstreetmap.org/way/719283014) |
| `seg_2970d2567777fb79` | Langenfelder Damm | tertiary | GOW30 | ETW30 (36,6 %) | 0,366 | `thresholds.conn_gow:+`, `conn_score.in_hvs:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561888,5937524]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582913/9.934838) | [Way](https://www.openstreetmap.org/way/1289430171) |
| `seg_38a2a82cf51b36a2` | Schnackenburgallee | tertiary | ETW30 | GOW50 (37,4 %) | 0,374 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559864,5938751]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.594175/9.904502) | [Way](https://www.openstreetmap.org/way/27564587) |
| `seg_3babf4754de00a23` | Langenfelder Damm | tertiary | GOW30 | ETW30 (31,2 %) | 0,312 | `thresholds.conn_gow:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561988,5937452]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582254/9.936336) | [Way](https://www.openstreetmap.org/way/362847066) |
| `seg_3d9bd48bf4b570e3` | Heußweg | tertiary | ETW30 | GOW30 (38,8 %) | 0,388 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563340,5937217]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.579976/9.956698) | [Way](https://www.openstreetmap.org/way/923507556) |
| `seg_3f91506d8d854af2` | Schleswiger Damm | primary | GOW30 | GOW50 (30,8 %) | 0,308 | `thresholds.sensitive_radius:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561204,5943069]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632824/9.925596) | [Way](https://www.openstreetmap.org/way/23299739) |
| `seg_446300c7b4014877` | Langenfelder Damm | tertiary | GOW30 | ETW30 (33,2 %) | 0,332 | `thresholds.conn_gow:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562174,5937256]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580466/9.939102) | [Way](https://www.openstreetmap.org/way/757098525) |
| `seg_49696ca06ed4ad48` | Wördemanns Weg | tertiary | ETW30 | GOW30 (44,0 %) | 0,486 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560750,5939421]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600092/9.918009) | [Way](https://www.openstreetmap.org/way/5014761) |
| `seg_6ff9c65ff8a5fd08` | Mittelweg | tertiary | ETW30 | GOW30 (47,4 %) | 0,474 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565800,5937098]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578606/9.993832) | [Way](https://www.openstreetmap.org/way/206426305) |
| `seg_889c8d2b0829d7eb` | Nordalbingerweg | tertiary | ETW30 | GOW30 (41,6 %) | 0,416 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562788,5943913]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.640223/9.949710) | [Way](https://www.openstreetmap.org/way/130423837) |
| `seg_903371f668d431a5` | Lohkampstraße | tertiary | ETW30 | GOW30 (47,4 %) | 0,474 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559331,5940579]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.610664/9.896790) | [Way](https://www.openstreetmap.org/way/5010035) |
| `seg_91c302df4485ff7f` | Rothenbaumchaussee | secondary | GOW30 | ETW30 (41,8 %) | 0,418 | `thresholds.conn_gow:+`, `conn_score.betweenness_norm:-`, `conn_score.in_hvs:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565564,5935174]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.561347/9.989851) | [Way](https://www.openstreetmap.org/way/35170417) |
| `seg_9b3d4a2c736a7b29` | Schleswiger Damm | secondary | GOW50 | GOW30 (45,0 %) | 0,45 | `thresholds.sensitive_radius:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560544,5944159]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.642700/9.915829) | [Way](https://www.openstreetmap.org/way/763381504) |
| `seg_9b9e04c1c04e89a6` | Gazellenkamp | tertiary | ETW30 | GOW50 (43,4 %) | 0,434 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562320,5939340]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599182/9.941718) | [Way](https://www.openstreetmap.org/way/54681028) |
| `seg_a1d1c14791e38f9a` | Lohkampstraße | tertiary | ETW30 | GOW30 (40,6 %) | 0,406 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559042,5940736]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.612109/9.892466) | [Way](https://www.openstreetmap.org/way/42413677) |
| `seg_a2851811bdb6fef7` | Emmy-Beckmann-Weg | tertiary | ETW30 | GOW50 (36,6 %) | 0,366 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563133,5943996]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.640926/9.954950) | [Way](https://www.openstreetmap.org/way/601252770) |
| `seg_acc4c75b899f1133` | Langenfelder Damm | tertiary | GOW30 | ETW30 (31,2 %) | 0,312 | `thresholds.conn_gow:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561952,5937482]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582523/9.935797) | [Way](https://www.openstreetmap.org/way/861181506) |
| `seg_b0dfa3b249bfa9ed` | Niendorfer Straße | secondary | ETW30 | GOW30 (38,6 %) | 0,386 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563195,5940055]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.605503/9.955083) | [Way](https://www.openstreetmap.org/way/1382663972) |
| `seg_b7e8abf865d9264d` | Koppelstraße | primary | GOW50 | GOW30 (45,0 %) | 0,45 | `thresholds.sensitive_radius:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562312,5938676]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.593214/9.941466) | [Way](https://www.openstreetmap.org/way/500693425) |
| `seg_be75fbd1afbd292d` | Niendorfer Straße | secondary | ETW30 | GOW30 (28,4 %) | 0,394 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563057,5939658]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.601953/9.952916) | [Way](https://www.openstreetmap.org/way/792463429) |
| `seg_bfb9697b7b847eb5` | Langenfelder Damm | tertiary | GOW30 | ETW30 (32,2 %) | 0,322 | `thresholds.conn_gow:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562267,5937083]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578898/9.940470) | [Way](https://www.openstreetmap.org/way/27308882) |
| `seg_e766d2d34801d061` | Doormannsweg | primary | GOW30 | GOW50 (40,0 %) | 0,4 | `thresholds.sensitive_radius:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563327,5936173]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.570600/9.956293) | [Way](https://www.openstreetmap.org/way/44365495) |
| `seg_fbc58a7a2bd5e67f` | Mittelweg | tertiary | ETW30 | GOW30 (47,4 %) | 0,474 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565751,5936742]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575408/9.993012) | [Way](https://www.openstreetmap.org/way/206426305) |
| `seg_fd317d3d54e16c2d` | Mittelweg | tertiary | ETW30 | GOW30 (47,4 %) | 0,474 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565787,5936541]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573606/9.993511) | [Way](https://www.openstreetmap.org/way/206426305) |

## 4. Datenqualität je Bezirk

Conflation-Trefferquote = Anteil der km mit amtlichem Gegenstück (match_quality exact oder partial, S-CONF-01). OSM-Tag-Vollständigkeit = Anteil der Abschnitte mit bekanntem Wert (S-FEAT-10; fehlende Tags heißen unbekannt). DTV gibt es nur auf Hauptverkehrsstraßen (2019); weil `in_hvs` selbst aus den DTV-Linien stammt (S-CONF-04), fehlt DTV auf HVS nie. Aussagekräftiger ist der Anteil der OSM-Hauptstraßen (primary, secondary) ohne DTV: Kandidaten für Lücken im HVS-Abgleich.

| Bezirk | Abschnitte | km | Conflation-Treffer (km) | davon exact | OSM-Tags Mittel | ohne Ist-Tempo | Hauptstraßen (OSM) | davon ohne DTV | alle ohne DTV |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Eimsbüttel | 3 876 | 461,5 | 96,1 % | 93,6 % | 65,9 % | 6,5 % | 938 | 22,9 % | 80,4 % |
| Altona | 295 | 36,6 | 94,8 % | 89,6 % | 63,6 % | 9,2 % | 57 | 10,5 % | 81,4 % |
| Hamburg-Nord | 287 | 33,0 | 96,1 % | 95,3 % | 66,7 % | 4,9 % | 36 | 8,3 % | 88,2 % |
| Hamburg-Mitte | 179 | 13,4 | 86,1 % | 82,8 % | 76,1 % | 10,6 % | 80 | 43,8 % | 63,7 % |
| ohne Bezirk | 150 | 17,4 | 0,0 % | 0,0 % | 43,3 % | 24,0 % | 8 | 25,0 % | 96,0 % |
| gesamt | 4 787 | 562,0 | 92,8 % | 90,3 % | 65,5 % | 7,3 % | 1 119 | 23,3 % | 80,8 % |

OSM-Tag-Vollständigkeit je Merkmal (Anteil der Abschnitte mit bekanntem Wert):

| Bezirk | baulicher Radweg | Radfahrstreifen | Mittelmarkierung | Parken | Fahrstreifen | Belag | maxspeed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Eimsbüttel | 83,3 % | 83,3 % | 17,1 % | 42,6 % | 46,9 % | 99,9 % | 88,2 % |
| Altona | 79,3 % | 79,3 % | 14,2 % | 45,1 % | 48,8 % | 100,0 % | 78,6 % |
| Hamburg-Nord | 93,0 % | 93,0 % | 10,8 % | 47,4 % | 42,9 % | 99,0 % | 80,8 % |
| Hamburg-Mitte | 90,5 % | 90,5 % | 13,4 % | 73,2 % | 78,2 % | 100,0 % | 87,2 % |
| ohne Bezirk | 50,0 % | 50,0 % | 12,0 % | 0,7 % | 22,0 % | 90,0 % | 78,7 % |
| gesamt | 82,9 % | 82,9 % | 16,3 % | 42,9 % | 47,1 % | 99,5 % | 86,8 % |

Abschnitte ohne Ist-Tempo: 7,3 % (Ziel unter 5,0 %, V-DQ-01, guide.md 3.4): **nicht erfüllt**.

Auf der Webseite zeigt die Ampel „Datenunsicherheit“ je Abschnitt fehlende und unsichere Eingangswerte (C-CONF-01); neu ist der Hinweis „unsicher“ aus der Sensitivitätsanalyse.

## 5. Manuelle Stichproben

Ziel (V-SAMP-01, guide.md 7.1): unter 15,0 % fachlich strittig je Kategorie. Stand der Dateien in reports/:

**Conflation (reports/conflation_sample.csv, Spalte check_ok):** 0 von 50 Zeilen geprüft – **Durchsicht offen**.

**Klassifikation (reports/classification_sample.csv, Spalten check_ok, cat_expected_manual):** 0 von 150 Zeilen geprüft – **Durchsicht offen**.

**Transekte (reports/transect_sample.geojson, Spalte measured_m):** 0 von 50 nachgemessen – **Durchsicht offen**.

**Korrekturen (overrides/overrides.csv):** 0 Einträge, davon 0 approved. **Rückmeldungen von Ortskundigen:** noch keine (Rückmeldekanal nicht eingerichtet, docs/open_questions.md).

## 6. Grenzen

### Fachlich (guide.md 7.2)

- Die niederländischen Kategorien passen nicht eins zu eins auf RIN/RASt; die Zuordnung ist eine Näherung.
- Die GOW30-Merkmale der CROW (2023) sind ausdrücklich vorläufig; ihre Wirkung wird erst evaluiert.
- Ein Soll-Plan sagt wenig über die Umsetzung: Richtlinien werden oft nicht eingehalten (SWOV 2023).
- Multifunktionale Hauptstraßen landen konsequent in GOW30: 58,3 % der HVS-km in GOW50/GOW30 sind GOW30 – fachlich folgerichtig, politisch der härteste Punkt.
- Busbetrieb, Rettungswege und Wirtschaftsverkehr sind nur Overlays; Fahrzeitwirkungen sind nicht modelliert.

### Rechtlich (guide.md 7.3)

- Der Plan ist kein Verwaltungsakt und keine Anordnung; Tempo auf Hauptverkehrsstraßen setzt weiter die Voraussetzungen der StVO voraus.
- GOW30 begründet in Deutschland derzeit kein flächiges Tempo 30 auf Hauptverkehrsstraßen; es kann Einzelfälle und ein Gesamtkonzept begründen.
- Lizenzen: dl-de/by-2.0- und ODbL-Pflichten; für die amtlichen Tempo- und Verkehrsmengendaten fehlt die Lizenzangabe in der API (offen). Unfälle nur als Summen je Abschnitt.

### Methodisch (guide.md 7.4 und dieser Lauf)

- Kfz-Verkehrsstärken fehlen auf 80,8 % der Abschnitte (DTV nur auf HVS, Stand 2019); Betweenness bildet Verkehr nicht ab.
- HVS aus den DTV-Linien 2019 statt der HVS-Karte 2023 (S-CONF-04); Lücken im Abgleich erzeugen Abweichungen in Abschnitt 1.
- OSM-Attribute sind ungleich vollständig (im Mittel 65,5 % der Gestaltungsmerkmale bekannt); die Ist-Gestaltung und damit die Diskrepanz ist dort unsicher.
- Unfallatlas: nur polizeilich erfasste Unfälle mit Personenschaden; Alleinunfälle mit dem Rad sind untererfasst.
- Annahme-Schwellen sind Setzungen. Die Sensitivitätsanalyse zeigt ihren Einfluss, ersetzt aber keine fachliche Abstimmung. Annahmen früherer Stufen (Conflation, Merkmale, Querschnitt) sind nicht variiert (Abschnitt 3.1).
- Die Monte-Carlo-Faktoren sind unabhängig und gleichverteilt; Abhängigkeiten zwischen Annahmen sind nicht abgebildet.

## Offene Fragen (docs/open_questions.md)

Alle noch offenen Punkte, nach Abschnitt:

**Fachlich (Regelwerk)** (5)

- Gehwegbreite 2,50 m und Fahrbahnbreite 6,50 m (zwei Fahrstreifen, Begegnung Lkw/Bus) am Original der RASt 06 prüfen – Verkehrsplaner*in
- RIN-Kategoriengruppen und RASt-Entwurfssituationen je Kategorie am Original prüfen (Teil 1.3) – Verkehrsplaner*in
- Schwellen mit `source_type: assumption` freigeben: conn_gow 0,6; sensitive_radius 150 m; frontage 0,4; N2 200 m; N3 25 ha; N4 300 m; Machbarkeitsklassen 0,85/1,0 – Verkehrsplaner*in
- Gewichte conn_score, place_score und Priorisierung festlegen – Verkehrsplaner*in
- Stand der FGSV-Neufassungen (RASt, ERA, EFA) vor jedem Release prüfen – Team

**Regelwerk-Datei (Befunde aus Prompt 02, Schema-Prüfung von rules.yaml 0.1.0)** (7)

- `crossing_demand == high` (C-G30-01) ist nicht definiert: Woraus wird der Querungsbedarf abgeleitet, welche Stufen gibt es, ab wann „high“? Goldene Fälle nutzen vorerst „high“/„low“ als Eingabe – Verkehrsplaner*in
- C-G30-02 vergleicht immer mit `required_width.GOW50` (16,50 m). Soll auf Busrouten `GOW50_bus` (17,00 m) gelten? – Verkehrsplaner*in
- `required_width.sidewalk_m` und `carriageway_2lane_m` führen in `status` Freitext („am Original prüfen“) statt draft/reviewed/approved. Vorschlag: status: draft + Text in `note` (neue Version nötig) – Methodik
- `requirements.GOW30.profiles.*.max_dtv` ohne Einheit; das Schema nimmt Kfz/24h an. Einheit in rules.yaml ergänzen? – Methodik
- Gewichte in `scores` und `priority.risk_weights` tragen `source_type: assumption` nur als Kommentar. Als Feld ergänzen? – Methodik
- Teil 1.7 verlangt Quellen mit Seitenangabe; rules.yaml hat keine Seitenangaben – Verkehrsplaner*in
- Merkmalsnamen in guide.md 3.3 (`width_median_m`, `separated_cycle_track_feasible`) weichen von rules.yaml ab (`width_p10_m`, `separated_cycle_track_present`). Pipeline folgt rules.yaml; guide.md angleichen? – Methodik

**Netz und Segmentierung (Prompt 04, rules.yaml 0.2.0)** (5)

- Schwelle S-NET-03 freigeben: Abschnitte erst ab 400 m bei maxspeed-Wechsel teilen (Annahme aus guide.md 3.2) – Verkehrsplaner*in
- guide.md 3.2 nennt auch Querschnittswechsel als Teilungsgrund. Querschnittsdaten gibt es erst nach Prompt 07; soll danach neu segmentiert werden (ändert segment_id)? – Methodik
- Fehlendes maxspeed gilt bei S-NET-03 nicht als Wechsel (50 → unbekannt → 50 wird nicht geteilt, 50 → unbekannt → 30 schon). Passt das? – Methodik
- highway-Klassen: *_link mitführen (derzeit ja)? highway=road, busway nicht enthalten – richtig? – Methodik
- Viele sehr kurze Abschnitte an Knoten mit getrennten Richtungsfahrbahnen (P10 ca. 10–17 m bei primary/secondary/tertiary). Getrennte Fahrbahnen bleiben getrennte Abschnitte; für Klassifikation und Kohärenz zusammenfassen? – Methodik

**Conflation (Prompt 05, rules.yaml 0.3.0)** (8)

- Schwellen S-CONF-01/02 freigeben: Puffer 15 m, Winkel 20°, Überdeckung 60 %, Zonen-Längenanteil 50 % (Startwerte, per Stichprobe reports/conflation_sample.csv kalibrieren) – Verkehrsplaner*in
- Definition match_quality: exact = Abschnitt zu ≥ 60 % von gültigen amtlichen Linien überdeckt, partial = weniger, none = keine. Passt das? – Methodik
- `in_hvs` stammt aus den DTV-Linien HVS 2019 statt aus der HVS-Karte 2023. Bis HH-SIB wieder erreichbar ist oder die Karte digitalisiert ist: Abweichungen 2019 → 2023 bekannt? – GIS
- `in_hvs` nur bei match_quality exact. Sollen auch partial-Treffer zählen? – Methodik
- Mehrdeutige zeitlich begrenzte Regelungen: „30 km/h 22 - 6 h Lärmschutz“ mit Feld geschwindigkeit = 30 (Regeltempo unbekannt) und „… sonst 50km/h“ mit geschwindigkeit = 50 (begrenztes Tempo unbekannt). Was ist das Regeltempo? – GIS
- „5-7 km/h“ (verkehrsberuhigt), „Verkehrsbeeinflussungsanlage“ und „Autobahn-Auffahrt ohne explizite Geschwindigkeitsbegrenzung“ ergeben kein Zahl-Tempo (`speed_official_kmh` leer, Text in `speed_official_text`). Für Prompt 10 einen Rechenwert festlegen? – Methodik
- Abschnitte über einen Namenswechsel hinweg (z. B. „Sperlingsweg / Bayernweg“, bis ca. 1 km): S-NET-02 teilt nur bei highway-Wechsel. Auch bei Namenswechsel teilen (ändert segment_id)? – Methodik
- Fußgängerzonen (highway=pedestrian) sind in den Tempo-/Widmungsebenen meist nicht enthalten (86 % none) – amtliche Quelle für Fußgängerzonen? widmung_flaeche („für den Fußgängerverkehr“) nutzen? – GIS

**Merkmale (Prompt 06, rules.yaml 0.4.0)** (13)

- Standardtempo je highway-Klasse für die Reisezeit (S-FEAT-02: motorway 100, trunk 70, residential 30, living_street 7, übrige 50 km/h) freigeben. Betrifft 5,5 % der Abschnitte im Arbeitsgebiet – Verkehrsplaner*in
- Puffer freigeben: Gebäudedichte 50 m, Einwohner 100 m, Publikumsnutzung 20 m, Knoten-Fangradius 1 m (S-FEAT-03/04/05/10) – Verkehrsplaner*in
- Betweenness ungerichtet, weil die Abschnitte keine Einbahn-Information tragen; Zufahrtsbeschränkungen (access, motor_vehicle) werden nicht berücksichtigt. Reicht das, oder oneway/access in s02 mitführen? – Methodik
- Autobahnen fahren keine Busse; seit rules.yaml 0.5.0 zählt das als 0 und senkt ihren conn_score (Median 0,60 → 0,52). Für C-SW-01 ohne Wirkung; soll bus_trips_weekday auf Autobahnen nicht gewertet werden (Gewicht umlegen)? – Methodik
- Normierung über das Arbeitsgebiet (Eimsbüttel + 500 m): Werte ändern sich, wenn das Gebiet wächst. Bei Ausweitung auf ganz Hamburg über die ganze Stadt normieren? – Methodik
- DTV liegt nur für Hauptverkehrsstraßen vor (19 % der Abschnitte); `dtv_norm` rangiert nur innerhalb der HVS, alle übrigen Abschnitte bekommen das Gewicht umgelegt. Fehlendes DTV auf Nebenstraßen als „niedrig“ werten? – Verkehrsplaner*in
- Listen alkis_public_functions / alkis_ancillary_functions (S-FEAT-05) fachlich prüfen, v. a. „Gemischt genutztes Gebäude mit Wohnen“ (707 Gebäude) und „Bürogebäude“ (nicht gezählt). Mit ALKIS steigt der Anteil der Abschnitte mit shop_frontage_share ≥ 0,4 (C-G30-01) von 17 % auf 27 % – Verkehrsplaner*in
- shop_frontage_share bei wenigen Gebäuden instabil (1 von 1 = 1,0, z. B. Deckel Schnelsen). Mindestzahl Gebäude im Puffer, sonst null? – Methodik
- Publikumsnutzung: Definition (Anteil Gebäude statt Fassadenlänge, Geschoss der POIs nicht geprüft) und Liste `amenity_excluded` prüfen; ALKIS-Gebäudefunktion ergänzen, sobald ALKIS vorliegt – Methodik
- `outside_builtup_area` (C-RUR-01) hat keine Datenquelle (Ortsgrenze/Ortstafeln). Quelle festlegen; in Eimsbüttel vermutlich überall innerorts – GIS
- OSM-Gestaltungsmerkmale ohne Tag bleiben null (z. B. centre_line 84 %, parking 57 %, lanes 53 % null). Für die Diskrepanz (Prompt 10) fehlende Tags als „nein“ werten oder als unbekannt? – Methodik
- `access_motor_only` = motorway/motorway_link oder motorroad=yes, sonst nein (nicht null, weil motorroad nur positiv erfasst wird). Passt das? – Methodik
- GTFS-Fahrplanperiode endet 2026-12-12; danach neuen Datensatz wählen. Repräsentativer Werktag des aktuellen Feeds: 2026-04-29 (Mi). Getrennte Richtungsfahrbahnen erhalten nur die Fahrten ihrer Richtung – Team

**Querschnitt (Prompt 07, rules.yaml 0.7.0)** (6)

- 50 Transekte im DOP20 messen (reports/transect_sample.geojson) und in reports/transect_measurements.csv eintragen; Ziel mittlere absolute Abweichung < 1 m (Annahme) – GIS
- 39 % der Abschnitte (14 % der Länge) haben keine Breite: v. a. kurze Abschnitte, deren Transekte alle innerhalb 20 m eines Knotens liegen (30,8 % der Transekte verworfen). Was gilt in C-G30-02 ohne width_p10_m? Breite vom Nachbarabschnitt gleichen Namens übernehmen? – Methodik
- GOW30_narrow ist ein Bereich (10,80–13,40 m); die Machbarkeit nutzt die Untergrenze (range_reference: min). Passt das? – Verkehrsplaner*in
- Variante Verkehrsfläche: ALKIS „Weg“ umfasst auch Parkwege; „Strassenverkehr“-Flurstücke enthalten Böschungen und Grün. Fassade ist offen bei 40,6 % der Transekte (kein Gebäude in 40 m auf einer Seite). Breite für Straßen am Park/Bahndamm nur einseitig begrenzt – Methodik
- Getrennte Richtungsfahrbahnen: beide OSM-Abschnitte messen dieselbe Straßenraumbreite (ganzes Flurstück). Für die Klassifikation gewollt? – Methodik
- reports/transect_sample.geojson ist in EPSG:4326 (GeoJSON-Standard), obwohl laut CLAUDE.md nur die Exportstufe nach 4326 transformiert. Für Prüf-Dateien in reports/ zulassen? – Team

**Klassifikation (Prompt 08, rules.yaml 0.8.0)** (6)

- C-MISS-01 und C-CONF-01 fachlich freigeben (Defaults outside_builtup_area = false, override_school_street = false, crossing_demand = not_assessed; Liste der Fallback-Quellen). Folge: Nur SW erreicht „hoch“ (5 % der Länge), 85 % sind „mittel“, solange Ortsgrenze, Schulstraßen-Overrides, HVS-Karte 2023 und amtliche Schulen/Kitas fehlen – Verkehrsplaner*in
- `shop_frontage_share` ist leer, wenn kein Gebäude im 20-m-Puffer liegt (236 von 367 GOW50-Abschnitten, meist kurze Knotenstücke). C-G30-01 ist dort unbekannt → GOW50 mit confidence niedrig. Ohne Gebäude als 0 werten (S-FEAT-05 ändern) oder Wert vom Nachbarabschnitt übernehmen? – Methodik
- HVS in Eimsbüttel: 45,6 km GOW30 gegenüber 29,9 km GOW50 (60 % der HVS-km werden GOW30), fast immer über C-G30-01 (Schule/Kita ≤ 150 m bei 443, Publikumsnutzung ≥ 0,4 bei 386 von 600 GOW30-Abschnitten, Mehrfachnennung). Plausibel, oder sind sensitive_radius/frontage zu weit? (Schwellen nicht geändert) – Verkehrsplaner*in
- „Bezirksstraßen, die GOW50 werden“ (17 Abschnitte, 0,6 km) sind kurze primary/tertiary-Stücke, vermutlich Lücken im HVS-Abgleich (in_hvs nur bei match exact). Definition im Report: Bezirksstraße = in_hvs false und keine Autobahn. Passt das? – Methodik
- Durchsicht der Stichprobe (reports/classification_sample.csv, bis zu 30 Abschnitte je Kategorie in Eimsbüttel) im Orthophoto und in Panoramax; Fehlerrate je Kategorie in den Report – Verkehrsplaner*in
- guide.md 3.4 nennt die Spalte `cat_confidence`, prompts/08 und die Pipeline `confidence`. guide.md angleichen? – Methodik

**Netzkohärenz und Korrekturebene (Prompt 09, rules.yaml 0.9.0)** (11)

- Neue Annahmen freigeben: N1 Stadtgrenze ≤ 50 m, N2 Straßenzug ≤ 30° Richtungsänderung (Richtung über 15 m), N6 Ampel/Plateau im Umkreis 30 m – Verkehrsplaner*in
- N3: Schwelle für „sehr lange Grenze im Verhältnis zur Fläche“ fehlt (guide.md 1.5). Kompaktheit 4π·A/U² wird berichtet; ab welchem Wert markieren? – Verkehrsplaner*in
- N3: Flächen ohne ETW-Abschnitt (Verkehrsinseln, Grünflächen) gelten nicht als Aufenthaltsbereich. Bahn, Gewässer und Parks als Grenzen ergänzen? – Methodik
- N4: 29 % der OD-Paare im GOW/SW-Netz haben einen kürzesten Weg mit > 300 m ETW (1 082 ETW-Abschnitte, 112 km), weil GOW30 und ETW30 dasselbe Soll-Tempo haben. Soll N4 nur bei Zeitvorteil über einer Schwelle oder ab einer Mindestzahl OD-Paare markieren? Einbahnstraßen/Abbiegeverbote fehlen – Verkehrsplaner*in
- N4: 73 000 OD-Paare sind nur über ETW verbunden (Lücken im GOW/SW-Netz). Als eigenes Flag ausweisen? – Methodik
- N5: Ob an einem Übergang GOW→ETW oder GOW50→GOW30 eine Torsituation vorhanden ist, steht in keiner Quelle. Merkmal festlegen (z. B. Gehwegüberfahrt, Plateau, Einengung) und Datenquelle – Verkehrsplaner*in, GIS
- N6: Tabelle 1.4 deckt SW–GOW50 (50 Knoten), SW–SW (49), ETW_ERF–ETW_ERF (40) und SW–ETW30 nicht ab (not_defined). Soll-Knotentyp festlegen? – Verkehrsplaner*in
- N6: GOW50–GOW30 gilt als „Kreisverkehr, sonst Signal mit Plateau“ (Zeile GOW50), GOW30–GOW30 als Kreisverkehr. So gemeint? Kreisverkehr an ETW–ETW-Knoten (64) gilt als Abweichung von „gleichrangig“ – Verkehrsplaner*in
- N6: Gehwegüberfahrten und Vorfahrtregelung (give_way/stop) sind in OSM kaum erfasst; die meisten Knoten sind not_checkable. Quelle für Ist-Knotentypen? – GIS
- Flag-Liste fachlich durchsehen (reports/coherence.md, Stichprobe, reports/coherence_flags.geojson) – Verkehrsplaner*in
- reports/coherence_flags.geojson ist 1,5 MB (alle markierten Abschnitte, Knoten, Flächen). In Git lassen oder nur erzeugen? – Team

**Diskrepanz und Priorisierung (Prompt 10, rules.yaml 0.10.0)** (10)

- **Top 30 gegenlesen** (reports/priority_top30.md, Spalte „Prüfung“) – Ortskundige
- Zuordnung flow/sparse je Verstoß und damit D1–D3 (D-DES-01, D-TYPE-01) an Beispielen der Sichtprüfung beurteilen (reports/discrepancy.md, Stichprobe) – Verkehrsplaner*in
- Die Top 30 werden von HVS-Abschnitten mit Soll GOW30 bestimmt: 14 von 30 sind HVS mit Soll GOW30 und DTV 2019 von 21 000–39 000 Kfz/Tag (Nutzung Stärke 3), 6 weitere GOW30, 10 ETW30. Das hängt an der offenen Frage aus Prompt 08 (60 % der HVS-km werden GOW30). Erst klären, dann Liste neu erzeugen – Verkehrsplaner*in
- Top 30 enthält mehrere Abschnitte derselben Straße (z. B. Hallerstraße 8×: 6 GOW30, 2 ETW30). – 2026-10-28: Straßenliste (Top 30 Straßen nach Name) vor der Abschnittsliste ergänzt (Entscheidung Projektteam 2026-10-28). Offen: Hallerstraße-Abschnitte mit Soll ETW30 und Ist 50 sind vermutlich Lücken im HVS-Abgleich (in_hvs false) – Methodik
- `bahnigkeit_official` als Mitteltrennung: Bedeutung des Attributs (1/2) in der Quelle nicht bestätigt. 173 von 367 GOW50-Abschnitten haben ≥ 2 Fahrstreifen je Richtung bei bahnigkeit 1 (z. B. Kieler Straße) – GIS
- D-DES-01 GOW50 „Radweg oder Parallelroute“: Parallelroute ist nicht prüfbar, jeder GOW50 ohne baulichen Radweg zählt als Verstoß (74 Abschnitte) – Methodik
- Nutzung nur für GOW30 prüfbar (nur dort max_dtv) und DTV nur auf Hauptverkehrsstraßen 2019 (918 von 4 787 Abschnitten). max_dtv für ETW30 (Erschließung) und GOW50 festlegen? – Verkehrsplaner*in
- Mittelmarkierung (GOW30) ist bei 98,7 % unbekannt (OSM lane_markings kaum erfasst); Gestaltungs-Diskrepanz auf GOW30 daher fast nur über die Radführung – GIS
- Unfälle an Knoten gehen an genau einen anliegenden Abschnitt (den nächsten). Vorerst so belassen (Entscheidung Projektteam 2026-10-28); mit der Webkarte (Prompt 11) erneut prüfen: auf alle Arme verteilen oder Knoten gesondert ausweisen? 666 von 17 534 Unfällen mit Fuß-/Radbeteiligung liegen > 15 m von jedem Abschnitt – Methodik
- Risiko berücksichtigt nur Unfälle mit Fuß-/Radbeteiligung (polizeilich erfasst). Rettungsdienstdaten wie in Amsterdam (guide.md) verfügbar? – Team

**Export und Webseite (Prompt 11)** (8)

- GitHub-Repository anlegen und `web.github_repo` sowie `web.feedback_email` in config/project.yaml eintragen (ohne Werte kein Rückmeldeknopf) – Team
- Impressum: Verantwortliche Person/Organisation eintragen (web/src/pages.js, derzeit Platzhalter) – Team
- Nach dem ersten Deployment HTTP-Range auf GitHub Pages prüfen (`web/scripts/check-range.sh <URL>`); lokal mit vite preview: 206 für beide PMTiles – GIS
- Test auf einem echten Smartphone und mit Bildschirmleser (VoiceOver/NVDA); automatisch geprüft sind nur axe-core und emuliertes Pixel 7 (reports/web_accessibility.md) – Team
- Lizenz der amtlichen Tempo- und Verkehrsmengendaten fehlt in der API („Lizenz in der Quelle nicht angegeben“ im Steckbrief). Vor der Veröffentlichung klären, ob die abgeleiteten Werte gezeigt werden dürfen – GIS, Team
- Texte der Methodenseite und der Steckbriefe (config/plain_language.yaml) fachlich und auf einfache Sprache prüfen; Fotos aus Panoramax je Kategorie fehlen noch (guide.md 5.5) – Verkehrsplaner*in
- Cloudflare R2 für die PMTiles erst nötig, wenn mehrere Bezirke dazukommen (jetzt 1,6 MB + 13 MB Hintergrundkarte, Seite gesamt ca. 66 MB). Entscheidung später – Team
- Querschnittsskizze im Steckbrief zeigt nur „vorhanden vs. nötig“; Soll-Aufteilung (Gehweg/Radweg/Fahrbahn) als Skizze fehlt noch (guide.md 5.3) – Methodik

**Validierung und Sensitivität (Prompt 12, rules.yaml 0.11.0)** (11)

- Monte-Carlo variiert Gewichte **und** Annahme-Schwellen gemeinsam (guide.md 7.1 „über alle Annahmen“); prompts/12 nennt nur Gewichte. So belassen? Nur Gewichte ergäben deutlich weniger „unsichere“ Abschnitte – Methodik
- „unsicher“ ab Wechselquote 0,3 (prompts/12) oder erst über 0,3 (guide.md P11)? Umgesetzt: ab 0,3 (V-UNC-01) – Methodik
- conn_gow ist die mit Abstand einflussreichste Annahme: −20 % (0,48) macht 39,8 km zu GOW, vor allem ETW30 → GOW30 (z. B. Mittelweg, Lohkampstraße, Wördemanns Weg). Schwelle am HVS-Netz und an Stichproben kalibrieren – Verkehrsplaner*in
- Das Gewicht von in_hvs in conn_score wirkt auf Nicht-HVS-Straßen wie ein Abzug (ihr Wert 0 zählt mit, HVS greift ohnehin über C-GOW-01). −20 % auf dieses Gewicht macht 15,2 km zu GOW. in_hvs aus conn_score herausnehmen? – Methodik
- 292 Soll-ETW30-Abschnitte mit Ist-Tempo > 30 sind mögliche Datenfehler (Zone 30 laut Zonenebene, Quellen widersprechen sich, nur OSM-Tempo, HVS-Abgleich teilweise). Liste in reports/validation.md Abschnitt 2 durchsehen; z. B. Osterstraße (nur OSM-Tempo 50) – GIS
- Hauptstraßen mit Soll ETW30 (Kieler Straße, Vogt-Wells-Straße, primary) deuten auf Lücken im HVS-Abgleich (S-CONF-04, nur match exact) – GIS
- Abschnitte ohne Ist-Tempo 7,3 % (Ziel unter 5 %, V-DQ-01); im Randbereich „ohne Bezirk“ 24 % – GIS
- Abbruchgrenze für einen Rückgang der Kennzahl „HVS-km als GOW50/GOW30“ zwischen zwei Läufen (guide.md 3.4) ist nicht festgelegt; reports/validation_metrics.json speichert die Kennzahlen je Lauf – Methodik
- Annahmen früherer Stufen (Conflation-Puffer, Transekte, Puffer der Merkmale) sind nicht variiert, weil jede Variante einen neuen Lauf ab der jeweiligen Stufe braucht. Für die wichtigsten (S-CONF-01 buffer_m, S-XS-05 quantile) einmalig nachholen? – Methodik
- Manuelle Stichproben (reports/conflation_sample.csv, classification_sample.csv, transect_sample.geojson) sind nicht ausgefüllt; ohne sie ist der Entwurf nach guide.md Teil 7 nicht veröffentlichungsreif – Team
- Externe Fachprüfung: reports/validation.md an Hochschule oder Planungsbüro geben – Team

**Daten** (11)

- Führt HH_WFS_Strategisches_Strassennetz ein Attribut „Hauptverkehrsstraße“ mit Stand 2023? – GIS
- Gibt es Kfz-Zählungen auf Bezirksstraßen? Transparenzanfrage an Bezirksämter – Team
- Dienst-URL für „Radnetz Hamburg“ im Geoportal – GIS
- Endpunkte für Schulen, Kitas, Lärmkarten, Laserscan, Baumkataster, ALKIS-Download – GIS (GTFS, Zensus und ALKIS 2026-10-28 erledigt: WFS_HH_ALKIS_vereinfacht)
- Gibt es amtliche Flächen für Fahrbahn/Radweg/Gehweg (LSBG, Bezirke)? Transparenzanfrage – Team
- Lizenzen der OGC-API-Datensätze (api.hamburg.de) auf den Landing Pages prüfen – GIS
- HH_WFS_Strategisches_Strassennetz liefert seit 2026-10-28 HTTP 404 (Dataport-Fehlerseite). Neue Dienst-URL ermitteln (Geoportal/Transparenzportal); wird für die Conflation (Prompt 05) gebraucht – GIS
- DB Rad+ (api.hamburg.de/datasets/v1/dbradplus, jahr2025): Abfrage mit bbox bricht reproduzierbar ab (HTTP 200, abgeschnittenes JSON bei offset 10000/11000). Fehler an die Urban Data Platform melden; danach erneut `make fetch` – Team
- Lizenz fehlt in der API für „Zulässige Höchstgeschwindigkeiten“ und „Verkehrsmengen“ sowie in GetCapabilities von „Ruhige Gebiete“ – GIS
- Verkehrsmengen auf Hauptverkehrsstraßen liegen in der API nur bis 2019 (DTV) vor. Gibt es neuere Zählungen? – GIS
- SensorThings (iot.hamburg.de): 3.137 Locations im Arbeitsgebiet, gemischte IoT-Daten. Welche Things sind Kfz-/Rad-Zählstellen (Filterkriterium)? – GIS

**Rechtlich / Veröffentlichung** (2)

- ODbL-Pflichten bei Kombination OSM + amtliche Daten juristisch prüfen lassen – Team
- Rückmeldekanal und Datenschutz (GitHub-Issues, Formular) festlegen – Team

## Lizenz

Abschnitte aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale (Tempo, Verkehrsmengen, ALKIS): Freie und Hansestadt Hamburg, dl-de/by-2.0 bzw. laut Quelle; Unfälle: © Statistische Ämter des Bundes und der Länder, Unfallatlas (nur Summen je Abschnitt). Orthophotos: LGV Hamburg, dl-de/by-2.0.
