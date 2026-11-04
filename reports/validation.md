# Validierung und Sensitivität

Erzeugt: 2026-11-04T20:41:20+00:00 von `pipeline/validate.py`, rules.yaml 0.12.0. Nicht amtlicher Diskussionsentwurf: Die Automatik schlägt vor, Menschen entscheiden. Grundlage für die externe Fachprüfung (guide.md Teil 7).

## Kurzfassung

- HVS-Abgleich: 99,2 % der HVS-km sind GOW50 oder GOW30; 0,7 km HVS außerhalb, 0,8 km Bezirksstraßen mit GOW50.
- Ist-Tempo: 74,8 % der Soll-ETW30-km (mit bekanntem Tempo) haben heute höchstens 30 km/h; 250 Ausreißer sind mögliche Datenfehler.
- Sensitivität: 258 Abschnitte (26,6 km, 4,6 % der Länge) sind „unsicher“; die Top 30 der Priorität bleiben im Mittel zu 92,9 % gleich.
- Datenqualität: Conflation-Treffer 92,4 % der km, OSM-Gestaltungsmerkmale im Mittel 64,9 % bekannt, ohne Ist-Tempo 7,8 %.
- Manuelle Stichproben, Rückmelderunde und externe Prüfung sind offen.

Vergleich mit dem vorigen Lauf (2026-11-04T20:39:25+00:00, rules.yaml 0.12.0): HVS-km als GOW50/GOW30 99,2 % → 99,2 %; unsicher 258 → 258 Abschnitte. Eine Abbruchgrenze für einen Rückgang (guide.md 3.4) ist nicht festgelegt (docs/open_questions.md).

## Prüfungen dieses Laufs

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| Basislauf reproduziert cat_proposed | ok | 0 Abweichungen bei 4947 Abschnitten |
| Basislauf reproduziert die Priorität | ok | 0 Abweichungen |
| segment_id eindeutig | ok | 4947 Abschnitte |
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

**Kennzahl: 99,2 % der HVS-km im Arbeitsgebiet sind GOW50 oder GOW30.**

### Arbeitsgebiet gesamt (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil an HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0,4 | 28,0 | 0,0 | 28,4 | 0,4 % |
| GOW50 | 29,5 | 0,8 | 0,0 | 30,2 | 31,9 % |
| GOW30 | 62,1 | 6,7 | 0,0 | 68,8 | 67,3 % |
| ETW30 | 0,3 | 435,1 | 0,0 | 435,4 | 0,3 % |
| ETW_ERF | 0,0 | 10,6 | 0,0 | 10,6 | 0,0 % |
| **Summe** | 92,3 | 481,1 | 0,0 | 573,4 | |

### Bezirk Eimsbüttel (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil an HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0,3 | 25,3 | 0,0 | 25,6 | 0,4 % |
| GOW50 | 22,9 | 0,5 | 0,0 | 23,4 | 29,5 % |
| GOW30 | 54,5 | 5,1 | 0,0 | 59,5 | 70,0 % |
| ETW30 | 0,1 | 352,8 | 0,0 | 352,9 | 0,1 % |
| ETW_ERF | 0,0 | 9,0 | 0,0 | 9,0 | 0,0 % |
| **Summe** | 77,8 | 392,6 | 0,0 | 470,4 | |

### Je Bezirk (Nachbarbezirke nur mit ihrem Anteil am Arbeitsgebiet)

| Bezirk | km | HVS km | davon GOW50/GOW30 | HVS außerhalb GOW50/GOW30 km | Bezirksstraßen mit GOW50 km |
| --- | ---: | ---: | ---: | ---: | ---: |
| Eimsbüttel | 470,4 | 77,8 | 99,5 % | 0,4 | 0,5 |
| Altona | 37,1 | 5,2 | 97,9 % | 0,1 | 0,2 |
| Hamburg-Mitte | 13,8 | 4,5 | 99,1 % | 0,0 | 0,0 |
| Hamburg-Nord | 34,3 | 3,9 | 96,5 % | 0,1 | 0,1 |
| ohne Bezirk | 17,9 | 0,8 | 100,0 % | 0,0 | 0,0 |

### Abweichung A: HVS-Abschnitte außerhalb GOW50/GOW30 (8 Abschnitte, 0,7 km)

Nach Kategorie: ETW30 5 (0,3 km), SW 3 (0,4 km). SW auf HVS (Autobahnzubringer) ist fachlich folgerichtig; ETW30 und ETW_ERF auf HVS einzeln begründen.

| Bezirk | Straße | Soll | highway | Abschnitte | km | Beispiel |
| --- | --- | --- | --- | ---: | ---: | --- |
| Eimsbüttel | – | SW | motorway_link | 2 | 0,3 | `seg_1c29f75d06449ca9` |
| Hamburg-Nord | Herbert-Weichmann-Straße | ETW30 | secondary | 1 | 0,1 | `seg_a04af7ba72ceb9c8` |
| Altona | Stresemannstraße | ETW30 | primary | 1 | 0,1 | `seg_b2518f25302cba54` |
| Hamburg-Mitte | Neuer Jungfernstieg | ETW30 | secondary | 1 | 0,0 | `seg_550709d20236307d` |
| Eimsbüttel | Neuer Jungfernstieg | ETW30 | primary | 1 | 0,0 | `seg_e08001af1dc9d2aa` |
| Altona | – | SW | motorway_link | 1 | 0,0 | `seg_05a7bf220b7ad3fa` |
| Eimsbüttel | Alsterufer | ETW30 | residential | 1 | 0,0 | `seg_9d3ad8f1fea2fa54` |

### Abweichung B: Bezirksstraßen mit GOW50 (14 Abschnitte, 0,8 km)

Bezirksstraße = keine HVS und keine Autobahn. Grund ist immer C-GOW-01 über conn_score ohne GOW30-Auslöser. Kurze Stücke von Hauptstraßen deuten auf Lücken im HVS-Abgleich (nur match exact) hin.

| Bezirk | Straße | Soll | highway | Abschnitte | km | Beispiel |
| --- | --- | --- | --- | ---: | ---: | --- |
| Eimsbüttel | Oldesloer Straße | GOW50 | primary | 4 | 0,2 | `seg_2e6adb21f74d688b` |
| Eimsbüttel | Schleswiger Damm | GOW50 | primary | 1 | 0,1 | `seg_ace66a958ae70fa8` |
| Altona | Schnackenburgallee | GOW50 | secondary | 2 | 0,1 | `seg_adbd21cdecd38c7a` |
| Hamburg-Nord | Martinistraße | GOW50 | tertiary | 1 | 0,1 | `seg_7aad6709464c0bda` |
| Altona | Spreestraße | GOW50 | tertiary | 1 | 0,1 | `seg_a7cc126b6015b2e7` |
| Eimsbüttel | Kollaustraße | GOW50 | primary | 1 | 0,0 | `seg_3be25c3254402884` |
| Hamburg-Mitte | Lombardsbrücke | GOW50 | primary | 1 | 0,0 | `seg_72035f8f6b0bb062` |
| Eimsbüttel | Holsteiner Chaussee | GOW50 | primary | 1 | 0,0 | `seg_9103d3849a6b7f6e` |
| Eimsbüttel | Swebenweg | GOW50 | primary | 1 | 0,0 | `seg_ceb0498de58be0bd` |
| Eimsbüttel | Garstedter Weg | GOW50 | secondary | 1 | 0,0 | `seg_9eb122117042b96b` |

## 2. Soll-ETW30 und Ist-Tempo

Ist-Tempo = amtliches Regeltempo vor OSM maxspeed (S-FEAT-09). Soll-Tempo ETW30 = 30 km/h (categories.ETW30). Erwartung: hoher Anteil; Ausreißer sind Kandidaten für Datenfehler.

**Kennzahl: 74,8 % der Soll-ETW30-km mit bekanntem Ist-Tempo haben heute höchstens 30 km/h** (315,1 von 421,4 km; Ist-Tempo unbekannt: 13,9 km).

### Soll × Ist-Tempo (km, Arbeitsgebiet)

| Soll | ≤ 20 | 30 | 40–50 | > 50 | unbekannt |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0,0 | 0,0 | 5,6 | 20,0 | 2,8 |
| GOW50 | 0,0 | 0,1 | 20,0 | 9,8 | 0,4 |
| GOW30 | 0,0 | 2,7 | 65,8 | 0,2 | 0,1 |
| ETW30 | 3,2 | 311,9 | 106,0 | 0,3 | 13,9 |
| ETW_ERF | 0,1 | 0,8 | 0,1 | 0,0 | 9,5 |

### Ausreißer: Soll-ETW30 mit Ist-Tempo über 30 km/h (1097 Abschnitte, 106,3 km)

Davon **250 Abschnitte (14,2 km) mögliche Datenfehler**: mindestens ein Hinweis widerspricht dem Ist-Tempo oder der Kategorie (Zone 30 laut Zonenebene, Quellen widersprechen sich, nur OSM-Tempo, HVS-Abgleich nur teilweise, kein amtlicher Abgleich). Die übrigen sind Wohn- oder Sammelstraßen mit Tempo 50 ohne Widerspruch in den Daten – dort ist die Diskrepanz fachlich gemeint (D-SPD-01).

| Hinweis | Abschnitte |
| --- | ---: |
| Wohnstraße (OSM) | 287 |
| nur OSM-Tempo | 174 |
| kein amtlicher Abgleich | 168 |
| amtlich und OSM verschieden | 63 |
| HVS-Abgleich nur teilweise | 9 |
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
| ohne Bezirk | Schnelsener Weg | 2 | 0,3 | 50 | nur OSM-Tempo (2), kein amtlicher Abgleich (2) | `seg_2ecf85469ecedb69` |
| Eimsbüttel | Frohbösestraße | 1 | 0,2 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_3be5306ed98e0a7f` |
| Eimsbüttel | Deepenstöcken | 4 | 0,2 | 50 | amtlich und OSM verschieden (4), Wohnstraße (OSM) (4) | `seg_6ba46fb9f4bfaf05` |
| Eimsbüttel | Groß Borsteler Straße | 4 | 0,2 | 50 | Wohnstraße (OSM) (4), nur OSM-Tempo (3), kein amtlicher Abgleich (3), amtlich und OSM verschieden (1) | `seg_c3cfbc9c2f29ec81` |
| Eimsbüttel | Schäferstraße | 1 | 0,2 | 50 | Tempo-30-Zone laut Zonenebene (1), Wohnstraße (OSM) (1) | `seg_7708456cb9469b05` |
| Eimsbüttel | Methfesselstraße | 5 | 0,2 | 50 | amtlich und OSM verschieden (5), Wohnstraße (OSM) (1) | `seg_a7d0de43ee72d3f1` |
| Eimsbüttel | Hochallee | 1 | 0,2 | 50 | amtlich und OSM verschieden (1) | `seg_86f68500f5b2695d` |
| Hamburg-Nord | Sierichstraße / Herbert-Weichmann-Straße | 1 | 0,2 | 50 | HVS-Abgleich nur teilweise (1) | `seg_57fb054f5cb343db` |
| Eimsbüttel | Sootbörn | 1 | 0,2 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_b799c47f0630b725` |
| Eimsbüttel | Bogenallee | 1 | 0,2 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_3dfc9b132f75159e` |
| Eimsbüttel | Garstedter Weg | 4 | 0,2 | 50 | nur OSM-Tempo (2), kein amtlicher Abgleich (2), HVS-Abgleich nur teilweise (1), amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_f899105e58342e19` |
| ohne Bezirk | Pinneberger Straße | 1 | 0,2 | 50 | nur OSM-Tempo (1), kein amtlicher Abgleich (1) | `seg_e1fa75f846a97ae9` |
| Eimsbüttel | Paul-Sorge-Straße | 2 | 0,2 | 50 | amtlich und OSM verschieden (2), Wohnstraße (OSM) (2) | `seg_638850061180af26` |
| Eimsbüttel | Holsteiner Chaussee / Kieler Straße | 1 | 0,2 | 100 | nur OSM-Tempo (1), kein amtlicher Abgleich (1) | `seg_96fad374c81385de` |
| Hamburg-Nord | Borsteler Chaussee | 1 | 0,2 | 50 | amtlich und OSM verschieden (1), Tempo-30-Zone laut Zonenebene (1), Wohnstraße (OSM) (1) | `seg_61d64d6ca2cb1e1e` |
| Eimsbüttel | Egenbüttler Weg | 1 | 0,2 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_2c1b6433c85b14e7` |
| Eimsbüttel | Heilwigstraße | 1 | 0,1 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_598838be369c4209` |
| … | 101 weitere Straßen | | | | | |

## 3. Sensitivitätsanalyse

Geprüft wird die Automatik (`cat_proposed`: Kaskade und Harmonisierung H-STR-01 je Lauf); fachliche Korrekturen bleiben außen vor. Basis: rules.yaml 0.12.0, 4 947 Abschnitte, 573,4 km.

### 3.1 Einzelvariation (V-SENS-01): jede Annahme ±20 %

km mit anderer Kategorie als im Basislauf. Varianten: Annahme-Schwellen der Kaskade und `required_width` in ihren Bedingungen; zusätzlich die Gewichte von conn_score.

| Annahme | Regel | Basis | −20 %: km | Abschnitte | häufigste Wechsel | +20 %: km | Abschnitte | häufigste Wechsel |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| `thresholds.conn_gow` | C-GOW-01 | 0,6 | 39,5 | 368 | ETW30→GOW30 31,0, ETW30→GOW50 8,3, GOW50→GOW30 0,1 | 4,6 | 61 | GOW30→ETW30 4,2, GOW30→GOW50 0,3, GOW50→ETW30 0,1 |
| `thresholds.sensitive_radius` | C-G30-01 | 150 | 4,2 | 42 | GOW30→GOW50 4,2, GOW50→GOW30 0,0 | 4,2 | 37 | GOW50→GOW30 3,9, GOW30→GOW50 0,3 |
| `thresholds.frontage` | C-G30-01 | 0,4 | 1,7 | 7 | GOW50→GOW30 1,7 | 0,6 | 7 | GOW30→GOW50 0,6 |
| `required_width.GOW50` | C-G30-02 | 16,5 | 0,3 | 3 | GOW30→GOW50 0,3 | 0,7 | 4 | GOW50→GOW30 0,7 |
| `conn_score.betweenness_norm` | scores.conn_score | 0,35 | 2,5 | 28 | GOW30→ETW30 2,3, GOW50→ETW30 0,1, GOW30→GOW50 0,1 | 6,2 | 65 | ETW30→GOW30 5,3, ETW30→GOW50 0,8, GOW50→GOW30 0,1 |
| `conn_score.in_hvs` | scores.conn_score | 0,25 | 15,4 | 132 | ETW30→GOW30 12,8, ETW30→GOW50 2,5, GOW50→GOW30 0,1 | 3,1 | 37 | GOW30→ETW30 2,9, GOW50→ETW30 0,1, GOW30→GOW50 0,1 |
| `conn_score.bus_trips_weekday_norm` | scores.conn_score | 0,2 | 1,1 | 11 | GOW30→ETW30 1,0, GOW50→ETW30 0,1 | 3,8 | 31 | ETW30→GOW30 3,2, ETW30→GOW50 0,6 |
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

**Kennzahl: 258 Abschnitte (26,6 km, 4,6 % der Länge) sind unsicher.** Mindestens einmal gewechselt: 606 Abschnitte (63,1 km).

| Wechselquote | Abschnitte | km |
| --- | ---: | ---: |
| 0 (stabil) | 4 341 | 510,3 |
| über 0 bis 0,1 | 138 | 14,2 |
| über 0,1 bis unter 0,3 | 210 | 22,3 |
| ab 0,3 (unsicher) | 258 | 26,6 |

Unsichere Abschnitte je Soll-Kategorie (Basis) und häufigste andere Kategorie:

| Kategorie | km gesamt | unsicher km | Anteil | häufigste andere Kategorie (km) |
| --- | ---: | ---: | ---: | --- |
| SW | 28,4 | 0,0 | 0,0 % | – |
| GOW50 | 30,2 | 3,1 | 10,2 % | GOW30 (2,9), ETW30 (0,1) |
| GOW30 | 68,8 | 6,1 | 8,8 % | ETW30 (3,9), GOW50 (2,1) |
| ETW30 | 435,4 | 17,5 | 4,0 % | GOW30 (14,8), GOW50 (2,8) |
| ETW_ERF | 10,6 | 0,0 | 0,0 % | – |

Je Bezirk:

| Bezirk | km | unsicher km | Anteil |
| --- | ---: | ---: | ---: |
| Eimsbüttel | 470,4 | 22,4 | 4,8 % |
| Altona | 37,1 | 3,3 | 9,0 % |
| Hamburg-Mitte | 13,8 | 0,4 | 3,0 % |
| Hamburg-Nord | 34,3 | 0,5 | 1,5 % |
| ohne Bezirk | 17,9 | 0,0 | 0,0 % |

Einfluss je Annahme im Monte-Carlo (Korrelation des Faktors mit dem Anteil gewechselter km je Lauf; nur zur Orientierung, nicht kausal):

| Annahme | Korrelation |
| --- | ---: |
| `thresholds.conn_gow` | -0,80 |
| `conn_score.in_hvs` | -0,24 |
| `conn_score.betweenness_norm` | +0,13 |
| `thresholds.frontage` | -0,07 |
| `required_width.GOW50` | +0,05 |
| `conn_score.bus_trips_weekday_norm` | +0,04 |
| `conn_score.dtv_norm` | +0,03 |
| `thresholds.sensitive_radius` | +0,00 |

### 3.3 Priorität: Top 30 im Bezirk Eimsbüttel bei variierten Gewichten

Gleiche Läufe; risk mit variierten `priority.risk_weights`, Diskrepanzen aus dem Basislauf (eine geänderte Kategorie ändert auch die Diskrepanz – das ist hier nicht abgebildet). Im Mittel bleiben **92,9 % der Top 30** in der Top 30. 24 Abschnitte bleiben in mindestens 90 % der Läufe, 1 in weniger als der Hälfte.


### 3.4 Stichprobe: 30 zufällige unsichere Abschnitte im Bezirk Eimsbüttel (Seed 42)

Zur Durchsicht: Welche Kategorie ist fachlich richtig? Befund als Korrektur in overrides/overrides.csv.

| segment_id | Straße | highway | Soll | andere Kategorie | Wechselquote | Wechsel bei ±20 % | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| `seg_0a792eba3800c1d5` | Kollaustraße | primary | GOW30 | GOW50 (34,0 %) | 0,34 | `thresholds.conn_gow:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563279,5940685]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.611150/9.956486) | [Way](https://www.openstreetmap.org/way/220515421) |
| `seg_0b318799c39cffac` | Mittelweg | tertiary | ETW30 | GOW30 (34,6 %) | 0,346 | `thresholds.conn_gow:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565655,5935116]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.560807/9.991214) | [Way](https://www.openstreetmap.org/way/51981485) |
| `seg_0d450d708920b749` | Wendlohstraße | tertiary | ETW30 | GOW30 (19,8 %) | 0,342 | `thresholds.conn_gow:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562283,5942716]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.629526/9.941839) | [Way](https://www.openstreetmap.org/way/1166241920) |
| `seg_1e8ba8f726ae7270` | Frohmestraße | tertiary | ETW30 | GOW30 (39,6 %) | 0,396 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561285,5942793]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.630334/9.926760) | [Way](https://www.openstreetmap.org/way/149136687) |
| `seg_1fa175ddedea3ddf` | Mittelweg | tertiary | ETW30 | GOW30 (47,2 %) | 0,472 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565796,5936517]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573382/9.993645) | [Way](https://www.openstreetmap.org/way/206426305) |
| `seg_240edc3089b2fc7c` | Kieler Straße | primary | GOW30 | GOW50 (51,2 %) | 0,512 | `thresholds.frontage:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562110,5936796]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576343/9.938046) | [Way](https://www.openstreetmap.org/way/733544407) |
| `seg_2467dfafc2f66ace` | Troplowitzstraße | tertiary | ETW30 | GOW30 (38,2 %) | 0,382 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563927,5937805]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.585195/9.965684) | [Way](https://www.openstreetmap.org/way/719283014) |
| `seg_2970d2567777fb79` | Langenfelder Damm | tertiary | GOW30 | ETW30 (36,8 %) | 0,368 | `thresholds.conn_gow:+`, `conn_score.in_hvs:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561888,5937524]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582913/9.934838) | [Way](https://www.openstreetmap.org/way/1289430171) |
| `seg_3b7cf20ededaf18f` | Heidlohstraße | secondary | ETW30 | GOW30 (41,8 %) | 0,418 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560899,5942537]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.628076/9.920876) | [Way](https://www.openstreetmap.org/way/30334147) |
| `seg_3f83e48c8f2ecc41` | Eidelstedter Weg | tertiary | ETW30 | GOW30 (37,4 %) | 0,374 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562924,5937485]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582440/9.950478) | [Way](https://www.openstreetmap.org/way/1185539897) |
| `seg_43544c78e0c1afd6` | Oddernskamp | secondary | ETW30 | GOW30 (39,8 %) | 0,398 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563040,5939625]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.601652/9.952662) | [Way](https://www.openstreetmap.org/way/1081798526) |
| `seg_460069d522b52ba9` | Heußweg | tertiary | ETW30 | GOW30 (37,0 %) | 0,37 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563193,5937071]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578679/9.954445) | [Way](https://www.openstreetmap.org/way/23105093) |
| `seg_49560bb1289b25cb` | Niendorfer Straße | secondary | ETW30 | GOW30 (39,4 %) | 0,394 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563135,5939813]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603335/9.954136) | [Way](https://www.openstreetmap.org/way/47985735) |
| `seg_5190df2af336f5fa` | – | tertiary_link | ETW30 | GOW50 (24,4 %) | 0,382 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562625,5938713]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.593506/9.946203) | [Way](https://www.openstreetmap.org/way/309066612) |
| `seg_7ce6e28c008c4ab7` | Heußweg | tertiary | ETW30 | GOW30 (37,6 %) | 0,376 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563069,5936948]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.577594/9.952547) | [Way](https://www.openstreetmap.org/way/367080896) |
| `seg_959abe7498269a4e` | Heußweg | tertiary | ETW30 | GOW30 (36,8 %) | 0,368 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562963,5936640]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.574840/9.950890) | [Way](https://www.openstreetmap.org/way/362847837) |
| `seg_9fb73b297a07377a` | Lappenbergsallee | tertiary | GOW30 | ETW30 (31,6 %) | 0,316 | `thresholds.conn_gow:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562404,5936875]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.577017/9.942496) | [Way](https://www.openstreetmap.org/way/1071071540) |
| `seg_a1d1c14791e38f9a` | Lohkampstraße | tertiary | ETW30 | GOW30 (40,4 %) | 0,404 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559042,5940736]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.612109/9.892466) | [Way](https://www.openstreetmap.org/way/42413677) |
| `seg_b096d3a4467d9652` | Bundesstraße | tertiary | ETW30 | GOW30 (38,2 %) | 0,382 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564150,5936350]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572090/9.968761) | [Way](https://www.openstreetmap.org/way/236098418) |
| `seg_b588b5e4d32753c3` | Wördemanns Weg | tertiary | GOW30 | ETW30 (50,8 %) | 0,508 | `thresholds.conn_gow:+`, `conn_score.betweenness_norm:-`, `conn_score.in_hvs:+`, `conn_score.bus_trips_weekday_norm:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561527,5939212]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598125/9.929715) | [Way](https://www.openstreetmap.org/way/34342302) |
| `seg_c10809f2b0514956` | Lappenbergsallee | tertiary | GOW30 | ETW30 (31,6 %) | 0,316 | `thresholds.conn_gow:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562346,5936956]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.577753/9.941638) | [Way](https://www.openstreetmap.org/way/32199151) |
| `seg_c715b7abcecb27a3` | Schleswiger Damm | secondary | GOW30 | GOW50 (30,8 %) | 0,308 | `thresholds.sensitive_radius:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561028,5943283]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.634768/9.922975) | [Way](https://www.openstreetmap.org/way/136485974) |
| `seg_caadfc974482539b` | Heußweg | tertiary | ETW30 | GOW30 (36,8 %) | 0,368 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563004,5936739]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575718/9.951524) | [Way](https://www.openstreetmap.org/way/362847835) |
| `seg_cd5d82b10e4a8558` | Pinneberger Chaussee | secondary | GOW30 | GOW50 (44,2 %) | 0,442 | `thresholds.sensitive_radius:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559582,5940563]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.610492/9.900589) | [Way](https://www.openstreetmap.org/way/1486691847) |
| `seg_d062ff49340be67e` | Mittelweg | tertiary | ETW30 | GOW30 (34,6 %) | 0,346 | `thresholds.conn_gow:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565638,5935094]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.560612/9.990966) | [Way](https://www.openstreetmap.org/way/34424807) |
| `seg_d1e7c9190a8a42c3` | Nordalbingerweg | tertiary | ETW30 | GOW30 (39,0 %) | 0,39 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562884,5943953]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.640570/9.951170) | [Way](https://www.openstreetmap.org/way/1166222452) |
| `seg_d2273291da58242a` | Eidelstedter Weg | tertiary | ETW30 | GOW30 (37,8 %) | 0,378 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563296,5937367]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.581328/9.956066) | [Way](https://www.openstreetmap.org/way/367149771) |
| `seg_ecf7b02d88b8dc7d` | Niendorfer Straße | secondary | ETW30 | GOW30 (39,8 %) | 0,398 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563113,5939734]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.602629/9.953784) | [Way](https://www.openstreetmap.org/way/47985735) |
| `seg_fa5c4a68f755d0d3` | Oddernskamp | secondary | ETW30 | GOW50 (41,0 %) | 0,41 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562985,5939378]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599438/9.951776) | [Way](https://www.openstreetmap.org/way/886260316) |
| `seg_fbc58a7a2bd5e67f` | Mittelweg | tertiary | ETW30 | GOW30 (47,2 %) | 0,472 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565751,5936742]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575408/9.993012) | [Way](https://www.openstreetmap.org/way/206426305) |

## 4. Datenqualität je Bezirk

Conflation-Trefferquote = Anteil der km mit amtlichem Gegenstück (match_quality exact oder partial, S-CONF-01). OSM-Tag-Vollständigkeit = Anteil der Abschnitte mit bekanntem Wert (S-FEAT-10; fehlende Tags heißen unbekannt). DTV gibt es nur auf Hauptverkehrsstraßen (2019); weil `in_hvs` selbst aus den DTV-Linien stammt (S-CONF-04), fehlt DTV auf HVS nie. Aussagekräftiger ist der Anteil der OSM-Hauptstraßen (primary, secondary) ohne DTV: Kandidaten für Lücken im HVS-Abgleich.

| Bezirk | Abschnitte | km | Conflation-Treffer (km) | davon exact | OSM-Tags Mittel | ohne Ist-Tempo | Hauptstraßen (OSM) | davon ohne DTV | alle ohne DTV |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Eimsbüttel | 4 004 | 470,4 | 95,8 % | 93,5 % | 65,3 % | 6,9 % | 953 | 22,9 % | 80,3 % |
| Altona | 298 | 37,1 | 94,6 % | 89,6 % | 63,5 % | 9,1 % | 57 | 10,5 % | 81,5 % |
| Hamburg-Nord | 303 | 34,3 | 93,0 % | 92,2 % | 65,9 % | 6,9 % | 36 | 8,3 % | 88,8 % |
| Hamburg-Mitte | 187 | 13,8 | 85,4 % | 82,1 % | 75,0 % | 11,2 % | 81 | 43,2 % | 62,6 % |
| ohne Bezirk | 155 | 17,9 | 0,0 % | 0,0 % | 43,2 % | 25,2 % | 8 | 25,0 % | 96,1 % |
| gesamt | 4 947 | 573,4 | 92,4 % | 90,0 % | 64,9 % | 7,8 % | 1 135 | 23,3 % | 80,7 % |

OSM-Tag-Vollständigkeit je Merkmal (Anteil der Abschnitte mit bekanntem Wert):

| Bezirk | baulicher Radweg | Radfahrstreifen | Mittelmarkierung | Parken | Fahrstreifen | Belag | maxspeed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Eimsbüttel | 82,3 % | 82,3 % | 16,9 % | 41,9 % | 46,5 % | 99,8 % | 87,0 % |
| Altona | 79,2 % | 79,2 % | 14,1 % | 44,6 % | 48,3 % | 100,0 % | 78,9 % |
| Hamburg-Nord | 92,7 % | 92,7 % | 10,9 % | 46,2 % | 40,6 % | 99,0 % | 79,2 % |
| Hamburg-Mitte | 88,8 % | 88,8 % | 12,8 % | 71,7 % | 78,1 % | 100,0 % | 85,0 % |
| ohne Bezirk | 49,7 % | 49,7 % | 12,3 % | 0,6 % | 22,6 % | 90,3 % | 77,4 % |
| gesamt | 82,0 % | 82,0 % | 16,1 % | 42,1 % | 46,7 % | 99,5 % | 85,7 % |

Abschnitte ohne Ist-Tempo: 7,8 % (Ziel unter 5,0 %, V-DQ-01, guide.md 3.4): **nicht erfüllt**.

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
- Multifunktionale Hauptstraßen landen konsequent in GOW30: 67,8 % der HVS-km in GOW50/GOW30 sind GOW30 – fachlich folgerichtig, politisch der härteste Punkt.
- Busbetrieb, Rettungswege und Wirtschaftsverkehr sind nur Overlays; Fahrzeitwirkungen sind nicht modelliert.

### Rechtlich (guide.md 7.3)

- Der Plan ist kein Verwaltungsakt und keine Anordnung; Tempo auf Hauptverkehrsstraßen setzt weiter die Voraussetzungen der StVO voraus.
- GOW30 begründet in Deutschland derzeit kein flächiges Tempo 30 auf Hauptverkehrsstraßen; es kann Einzelfälle und ein Gesamtkonzept begründen.
- Lizenzen: dl-de/by-2.0- und ODbL-Pflichten; für die amtlichen Tempo- und Verkehrsmengendaten fehlt die Lizenzangabe in der API (offen). Unfälle nur als Summen je Abschnitt.

### Methodisch (guide.md 7.4 und dieser Lauf)

- Kfz-Verkehrsstärken fehlen auf 80,7 % der Abschnitte (DTV nur auf HVS, Stand 2019); Betweenness bildet Verkehr nicht ab.
- HVS aus den DTV-Linien 2019 statt der HVS-Karte 2023 (S-CONF-04); Lücken im Abgleich erzeugen Abweichungen in Abschnitt 1.
- OSM-Attribute sind ungleich vollständig (im Mittel 64,9 % der Gestaltungsmerkmale bekannt); die Ist-Gestaltung und damit die Diskrepanz ist dort unsicher.
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

**Netz und Harmonisierung (rules.yaml 0.12.0, 2026-11-04)** (6)

- Parallele Nebenfahrbahnen (highway=service, z. B. Grindelallee) werden über den Puffer der HVS-Linien als in_hvs zugeordnet und dadurch GOW30/GOW50 (22 Abschnitte, 2,0 km). Nach Duurzaam Veilig ist ein „ventweg“ Erschließung (ETW). in_hvs für S-NET-04-Wege nicht zuordnen? – Methodik
- Tracks mit maxspeed=walk (z. B. Amselweg, Hamburg-Nord) werden ETW30; eigene Regel für ETW_ERF? – Verkehrsplaner*in
- service/track sind nicht in der Betweenness (kein Standardtempo); ihr conn_score stützt sich nur auf die übrigen Merkmale (confidence mittel) – Methodik
- Amselweg/Meisenweg in Eimsbüttel sind Wege und Parkplatzgassen in Kleingartenvereinen (Klgv. 329, 331) und bleiben bewusst ohne Kategorie – erledigt, nur zur Info
- H-STR-01 lässt ETW_ERF/ETW30-Inseln stehen (5 Abschnitte, N2) – bei Bedarf ergänzen – Verkehrsplaner*in
- H-STR-01 verlängert kurze GOW30-Stücke (z. B. vor Schulen) auf 200 m; ob 200 m (N2 min_run_m) als Mindestlänge für Tempo-30-Abschnitte passt, fachlich prüfen – Verkehrsplaner*in

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
