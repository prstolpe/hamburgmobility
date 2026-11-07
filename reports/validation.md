# Validierung und Sensitivität

Erzeugt: 2026-11-07T15:10:34+00:00 von `pipeline/validate.py`, rules.yaml 0.16.0. Nicht amtlicher Diskussionsentwurf: Die Automatik schlägt vor, Menschen entscheiden. Grundlage für die externe Fachprüfung (guide.md Teil 7).

## Kurzfassung

- HVS-Abgleich: 96,7 % der HVS-km sind GOW50 oder GOW30; 23,0 km HVS außerhalb, 22,5 km Bezirksstraßen mit GOW50.
- Ist-Tempo: 72,0 % der Soll-ETW30-km (mit bekanntem Tempo) haben heute höchstens 30 km/h; 1936 Ausreißer sind mögliche Datenfehler.
- Sensitivität: 2 071 Abschnitte (218,4 km, 5,0 % der Länge) sind „unsicher“; die Top 30 der Priorität bleiben im Mittel zu 92,3 % gleich.
- Datenqualität: Conflation-Treffer 89,1 % der km, OSM-Gestaltungsmerkmale im Mittel 56,2 % bekannt, ohne Ist-Tempo 7,4 %.
- Manuelle Stichproben, Rückmelderunde und externe Prüfung sind offen.

Vergleich mit dem vorigen Lauf (2026-11-07T14:28:44+00:00, rules.yaml 0.15.0): HVS-km als GOW50/GOW30 96,7 % → 96,7 %; unsicher 2 133 → 2 071 Abschnitte. Eine Abbruchgrenze für einen Rückgang (guide.md 3.4) ist nicht festgelegt (docs/open_questions.md).

## Prüfungen dieses Laufs

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| Basislauf reproduziert cat_proposed | ok | 0 Abweichungen bei 34702 Abschnitten |
| Basislauf reproduziert die Priorität | ok | 0 Abweichungen |
| segment_id eindeutig | ok | 34702 Abschnitte |
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

**Kennzahl: 96,7 % der HVS-km im Arbeitsgebiet sind GOW50 oder GOW30.**

### Arbeitsgebiet gesamt (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil an HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 21,8 | 167,4 | 0,0 | 189,2 | 3,2 % |
| GOW50 | 200,6 | 22,5 | 0,0 | 223,2 | 29,0 % |
| GOW30 | 467,2 | 60,3 | 0,0 | 527,6 | 67,6 % |
| ETW30 | 0,9 | 3328,6 | 0,0 | 3329,4 | 0,1 % |
| ETW_ERF | 0,3 | 117,6 | 0,0 | 118,0 | 0,0 % |
| **Summe** | 690,8 | 3696,5 | 0,0 | 4387,3 | |

### Hamburg (7 Bezirke) (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil an HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 21,8 | 163,9 | 0,0 | 185,7 | 3,2 % |
| GOW50 | 199,8 | 22,3 | 0,0 | 222,1 | 29,0 % |
| GOW30 | 467,2 | 60,3 | 0,0 | 527,6 | 67,7 % |
| ETW30 | 0,9 | 3186,4 | 0,0 | 3187,3 | 0,1 % |
| ETW_ERF | 0,3 | 117,4 | 0,0 | 117,7 | 0,0 % |
| **Summe** | 690,0 | 3550,4 | 0,0 | 4240,4 | |

### Je Bezirk

| Bezirk | km | HVS km | davon GOW50/GOW30 | HVS außerhalb GOW50/GOW30 km | Bezirksstraßen mit GOW50 km |
| --- | ---: | ---: | ---: | ---: | ---: |
| Altona | 620,5 | 84,8 | 96,4 % | 3,0 | 1,0 |
| Bergedorf | 209,3 | 24,9 | 99,8 % | 0,0 | 1,8 |
| Eimsbüttel | 470,4 | 78,6 | 99,5 % | 0,4 | 0,7 |
| Hamburg-Mitte | 881,3 | 180,8 | 94,2 % | 10,6 | 5,6 |
| Hamburg-Nord | 563,3 | 113,6 | 92,2 % | 8,9 | 3,3 |
| Harburg | 465,2 | 72,0 | 100,0 % | 0,0 | 2,4 |
| Wandsbek | 1030,4 | 135,3 | 100,0 % | 0,0 | 7,5 |
| ohne Bezirk | 146,9 | 0,8 | 100,0 % | 0,0 | 0,2 |

### Abweichung A: HVS-Abschnitte außerhalb GOW50/GOW30 (65 Abschnitte, 23,0 km)

Nach Kategorie: ETW30 21 (0,9 km), ETW_ERF 5 (0,3 km), SW 39 (21,8 km). SW auf HVS (Autobahnzubringer) ist fachlich folgerichtig; ETW30 und ETW_ERF auf HVS einzeln begründen.

| Bezirk | Straße | Soll | highway | Abschnitte | km | Beispiel |
| --- | --- | --- | --- | ---: | ---: | --- |
| Hamburg-Mitte | Bergedorfer Straße | SW | trunk | 16 | 9,8 | `seg_c10ebfd805660a00` |
| Hamburg-Nord | Zeppelinstraße | SW | trunk | 15 | 8,6 | `seg_a3556cbeba8f55db` |
| Altona | Sülldorfer Landstraße | SW | trunk | 3 | 3,0 | `seg_e3e025e0d1630ebd` |
| Eimsbüttel | – | SW | motorway_link | 2 | 0,3 | `seg_1c29f75d06449ca9` |
| Hamburg-Nord | Sengelmannstraße | ETW30, ETW_ERF | living_street, trunk_link | 2 | 0,3 | `seg_59a776f5fc709026` |
| Hamburg-Mitte | Dammtorstraße | ETW30 | tertiary | 4 | 0,2 | `seg_fcdd43dd34c6081d` |
| Hamburg-Mitte | Holstenglacis | ETW30 | secondary | 3 | 0,2 | `seg_09b1a22a9b477859` |
| Hamburg-Mitte | Kajen | ETW30 | secondary | 1 | 0,2 | `seg_1b9d4b4a0d248f2e` |
| Hamburg-Mitte | – | ETW_ERF | pedestrian | 4 | 0,1 | `seg_d3f1c9d7bc9154ef` |
| Hamburg-Mitte | Ellerholzbrücke | ETW30 | primary | 1 | 0,1 | `seg_6b81b7e2c4e1ff78` |
| Altona | – | SW | motorway_link | 2 | 0,1 | `seg_05a7bf220b7ad3fa` |
| Bergedorf | – | ETW30 | primary_link | 1 | 0,0 | `seg_4f0a54145522cc84` |
| Hamburg-Mitte | Neuer Jungfernstieg | ETW30 | secondary | 1 | 0,0 | `seg_550709d20236307d` |
| Hamburg-Mitte | Finkenwerder Straße | SW | motorway_link | 1 | 0,0 | `seg_617f00ba8958e0a8` |
| Hamburg-Nord | Weidestraße | ETW30 | tertiary | 1 | 0,0 | `seg_98b65280fba76bd9` |
| Eimsbüttel | Neuer Jungfernstieg | ETW30 | primary | 1 | 0,0 | `seg_e08001af1dc9d2aa` |
| Hamburg-Mitte | Helgoländer Allee | ETW30 | tertiary | 1 | 0,0 | `seg_f74640427f0cf489` |
| Eimsbüttel | Alsterufer | ETW30 | residential | 1 | 0,0 | `seg_9d3ad8f1fea2fa54` |
| Hamburg-Nord | Barmbeker Markt | ETW30 | tertiary | 1 | 0,0 | `seg_e3b7dd13cf9b48d9` |
| Harburg | Süderelbebogen | ETW30 | secondary | 1 | 0,0 | `seg_43f14dfd66601823` |
| Harburg | – | ETW30 | secondary | 1 | 0,0 | `seg_4a95ef4aaef04298` |
| Wandsbek | – | ETW30 | secondary | 1 | 0,0 | `seg_580035287bda8139` |
| Hamburg-Nord | Erdkampsweg | ETW30 | secondary | 1 | 0,0 | `seg_1f401d9c265869b4` |

### Abweichung B: Bezirksstraßen mit GOW50 (256 Abschnitte, 22,5 km)

Bezirksstraße = keine HVS und keine Autobahn. Grund ist immer C-GOW-01 über conn_score ohne GOW30-Auslöser. Kurze Stücke von Hauptstraßen deuten auf Lücken im HVS-Abgleich (nur match exact) hin.

| Bezirk | Straße | Soll | highway | Abschnitte | km | Beispiel |
| --- | --- | --- | --- | ---: | ---: | --- |
| Hamburg-Mitte | Ausschläger Allee | GOW50 | tertiary | 6 | 1,5 | `seg_506addaae3afa613` |
| Harburg | Neuwiedenthaler Straße | GOW50 | tertiary | 11 | 1,3 | `seg_f9872823b050f4d2` |
| Bergedorf | Lohbrügger Landstraße | GOW50 | tertiary | 14 | 1,2 | `seg_20a6aa6901fd5731` |
| Wandsbek | Pezolddamm | GOW50 | tertiary | 9 | 1,2 | `seg_0b3867bdbe79e3c8` |
| Wandsbek | Meiendorfer Mühlenweg | GOW50 | tertiary | 3 | 1,0 | `seg_30bb3774a6771bf5` |
| Hamburg-Mitte | Billhorner Brückenstraße | GOW50 | primary, trunk | 14 | 0,9 | `seg_2ec04644e430a922` |
| Hamburg-Mitte | Neßdeich | GOW50 | tertiary | 9 | 0,8 | `seg_b3ac4d3a18f6caa9` |
| Harburg | Marmstorfer Weg | GOW50 | tertiary | 7 | 0,7 | `seg_7738adb6a8f73d76` |
| Hamburg-Nord | Tangstedter Landstraße | GOW50 | tertiary | 7 | 0,7 | `seg_d4a8d9012e74e98b` |
| Hamburg-Nord | Weg beim Jäger | GOW50 | tertiary | 1 | 0,7 | `seg_6f7aae04e2c2a022` |
| Wandsbek | Berner Chaussee | GOW50 | tertiary | 3 | 0,7 | `seg_c0f0578287ed0827` |
| Wandsbek | Schöneberger Straße | GOW50 | tertiary | 4 | 0,6 | `seg_7611e5760a13894e` |
| Eimsbüttel | Edmund-Siemers-Allee | GOW50 | service | 3 | 0,5 | `seg_f49ea34515d25699` |
| Hamburg-Nord | Alsterdorfer Straße | GOW50 | tertiary | 2 | 0,5 | `seg_ce38c05e3f7cbf15` |
| Wandsbek | Charlottenburger Straße | GOW50 | tertiary | 5 | 0,5 | `seg_d87998d8fc5153ac` |
| Wandsbek | An der Alsterschleife | GOW50 | tertiary | 1 | 0,5 | `seg_c5db1848591c3a8f` |
| Wandsbek | Berner Heerweg | GOW50 | tertiary | 4 | 0,5 | `seg_4e1a0a9712fd3d21` |
| Wandsbek | Ruscheweyhstraße | GOW50 | tertiary | 5 | 0,4 | `seg_e81dcbeb290831e2` |
| Wandsbek | Alter Zollweg | GOW50 | tertiary | 5 | 0,4 | `seg_9de9c96fcbb6c09e` |
| Hamburg-Nord | Maienweg | GOW50 | tertiary | 5 | 0,4 | `seg_26347d3198391e2e` |
| Bergedorf | Nettelnburger Landweg | GOW50 | secondary | 3 | 0,4 | `seg_d8f79ba8e4ed243b` |
| Hamburg-Mitte | Hermannstal | GOW50 | tertiary | 1 | 0,4 | `seg_dc42fad1b365750d` |
| Wandsbek | Sonnenweg | GOW50 | tertiary | 3 | 0,3 | `seg_3eb7d56e2a5fa23c` |
| Altona | Kalckreuthweg | GOW50 | tertiary | 8 | 0,3 | `seg_866125f213453360` |
| Wandsbek | Pezolddamm / Berner Allee | GOW50 | tertiary | 1 | 0,3 | `seg_f98cc9459a231ea9` |
| Bergedorf | Oberer Landweg | GOW50 | secondary | 2 | 0,3 | `seg_1ac1379276edce2a` |
| Harburg | Karnapp | GOW50 | residential | 2 | 0,3 | `seg_235b1e7d23ea74ec` |
| Hamburg-Mitte | Kandinskyallee | GOW50 | tertiary | 1 | 0,2 | `seg_62651b34e7cf00a0` |
| Hamburg-Mitte | Ostfrieslandstraße | GOW50 | tertiary | 2 | 0,2 | `seg_2b263cc8f1c198d5` |
| Hamburg-Mitte | Aue-Hauptdeich / Finkenwerder Straße | GOW50 | tertiary | 1 | 0,2 | `seg_92b3de74023ddec5` |
| ohne Bezirk | Krohnstieg | GOW50 | trunk | 1 | 0,2 | `seg_e3a576cd7361f4e4` |
| Hamburg-Mitte | – | GOW50 | secondary_link, trunk_link | 3 | 0,2 | `seg_95e20ef5e1af0dd2` |
| Hamburg-Nord | Sierichstraße / Herbert-Weichmann-Straße | GOW50 | secondary | 1 | 0,2 | `seg_57fb054f5cb343db` |
| Altona | Baron-Voght-Straße | GOW50 | tertiary | 2 | 0,2 | `seg_a01ba0fa71b1194e` |
| Wandsbek | Saseler Damm | GOW50 | residential | 1 | 0,2 | `seg_dca9ee4f71ebce4a` |
| Hamburg-Nord | Rosenbrook | GOW50 | primary, secondary_link | 3 | 0,2 | `seg_ae1c3da2b18e9f18` |
| Eimsbüttel | Quickbornstraße | GOW50 | tertiary | 1 | 0,2 | `seg_d2909ef54dd5521f` |
| Hamburg-Mitte | Veddeler Brückenstraße | GOW50 | tertiary | 1 | 0,1 | `seg_c2da4f80c0b760fa` |
| Hamburg-Mitte | Wilhelmsburger Brücke / Veddeler Straße | GOW50 | tertiary | 1 | 0,1 | `seg_2e4d6adb4c35233e` |
| Wandsbek | Pulverhofsweg | GOW50 | tertiary | 1 | 0,1 | `seg_f1483665c3670ee3` |
| … | 71 weitere Straßen | | | 99 | 3,3 | |

## 2. Soll-ETW30 und Ist-Tempo

Ist-Tempo = amtliches Regeltempo vor OSM maxspeed (S-FEAT-09). Soll-Tempo ETW30 = 30 km/h (categories.ETW30). Erwartung: hoher Anteil; Ausreißer sind Kandidaten für Datenfehler.

**Kennzahl: 72,0 % der Soll-ETW30-km mit bekanntem Ist-Tempo haben heute höchstens 30 km/h** (2253,5 von 3131,0 km; Ist-Tempo unbekannt: 198,4 km).

### Soll × Ist-Tempo (km, Arbeitsgebiet)

| Soll | ≤ 20 | 30 | 40–50 | > 50 | unbekannt |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0,0 | 0,0 | 13,3 | 151,7 | 24,3 |
| GOW50 | 0,0 | 5,1 | 169,7 | 47,3 | 1,1 |
| GOW30 | 0,4 | 17,4 | 500,6 | 8,7 | 0,4 |
| ETW30 | 67,0 | 2186,5 | 845,7 | 31,8 | 198,4 |
| ETW_ERF | 86,2 | 2,5 | 1,2 | 0,0 | 28,1 |

### Ausreißer: Soll-ETW30 mit Ist-Tempo über 30 km/h (7459 Abschnitte, 877,5 km)

Davon **1936 Abschnitte (158,7 km) mögliche Datenfehler**: mindestens ein Hinweis widerspricht dem Ist-Tempo oder der Kategorie (Zone 30 laut Zonenebene, Quellen widersprechen sich, nur OSM-Tempo, HVS-Abgleich nur teilweise, kein amtlicher Abgleich). Die übrigen sind Wohn- oder Sammelstraßen mit Tempo 50 ohne Widerspruch in den Daten – dort ist die Diskrepanz fachlich gemeint (D-SPD-01).

| Hinweis | Abschnitte |
| --- | ---: |
| Wohnstraße (OSM) | 2 238 |
| nur OSM-Tempo | 1 432 |
| kein amtlicher Abgleich | 1 399 |
| amtlich und OSM verschieden | 465 |
| Tempo-30-Zone laut Zonenebene | 36 |
| HVS-Abgleich nur teilweise | 32 |

Mögliche Datenfehler nach Straße (längste zuerst, höchstens 30):

| Bezirk | Straße | Abschnitte | km | Ist km/h | Hinweise | Beispiel |
| --- | --- | --- | ---: | ---: | --- | --- |
| Hamburg-Mitte | – | 81 | 6,7 | 50, 60, 80, 100 | nur OSM-Tempo (70), kein amtlicher Abgleich (70), amtlich und OSM verschieden (7), HVS-Abgleich nur teilweise (5), Wohnstraße (OSM) (3), Tempo-30-Zone laut Zonenebene (1) | `seg_ef6b32c32f80c6bd` |
| ohne Bezirk | Elbuferstraße | 11 | 3,7 | 50, 70, 100 | nur OSM-Tempo (11), kein amtlicher Abgleich (11) | `seg_d363d6790d3a9efd` |
| ohne Bezirk | – | 20 | 3,4 | 50, 70 | nur OSM-Tempo (20), kein amtlicher Abgleich (20) | `seg_f9f3f4f1299f01ee` |
| ohne Bezirk | Hoopter Elbdeich | 12 | 2,4 | 50 | nur OSM-Tempo (12), kein amtlicher Abgleich (12) | `seg_56821ee1c7b2183a` |
| ohne Bezirk | Neue Deichstraße | 6 | 2,0 | 50, 70 | nur OSM-Tempo (6), kein amtlicher Abgleich (6) | `seg_b1e63fe63de9458e` |
| Hamburg-Mitte | Washingtonallee | 13 | 2,0 | 50 | nur OSM-Tempo (13), kein amtlicher Abgleich (3) | `seg_496811e031e4246d` |
| ohne Bezirk | Elbdeich | 11 | 2,0 | 50 | nur OSM-Tempo (11), kein amtlicher Abgleich (11) | `seg_246149468768371b` |
| ohne Bezirk | Langereihe | 1 | 1,7 | 50 | nur OSM-Tempo (1), kein amtlicher Abgleich (1) | `seg_c7e464438fe78e81` |
| Hamburg-Nord | Raakmoorgrund / Weg Nr. 651 | 1 | 1,6 | 50 | Tempo-30-Zone laut Zonenebene (1) | `seg_ecf40172d73d6546` |
| ohne Bezirk | Industriestraße | 8 | 1,6 | 50 | nur OSM-Tempo (8), kein amtlicher Abgleich (8) | `seg_a24efa2aff606e3a` |
| Harburg | – | 19 | 1,4 | 50, 60, 80 | nur OSM-Tempo (17), kein amtlicher Abgleich (16), amtlich und OSM verschieden (2) | `seg_af1c4fa8ee8e5f64` |
| Wandsbek | Merkurring | 3 | 1,3 | 50 | nur OSM-Tempo (3), kein amtlicher Abgleich (3) | `seg_b385fc2de0979c43` |
| Hamburg-Nord | Rathenaustraße | 4 | 1,3 | 50 | amtlich und OSM verschieden (3), Wohnstraße (OSM) (3), nur OSM-Tempo (1), kein amtlicher Abgleich (1) | `seg_2206ab88bf5d8b62` |
| Wandsbek | Schleusenredder / Mühlenredder | 1 | 1,2 | 50 | amtlich und OSM verschieden (1), Tempo-30-Zone laut Zonenebene (1) | `seg_02c4ab91dfa1367a` |
| Hamburg-Mitte | Zellmannstraße | 1 | 1,2 | 50 | nur OSM-Tempo (1) | `seg_0b9af34dae4c519b` |
| Wandsbek | Müssenredder | 6 | 1,1 | 50 | amtlich und OSM verschieden (6), Wohnstraße (OSM) (6) | `seg_aa2c399f78fb2850` |
| ohne Bezirk | Hamburger Straße | 11 | 1,1 | 50 | nur OSM-Tempo (11), kein amtlicher Abgleich (11) | `seg_206faa2de61e890c` |
| Altona | Baurstraße | 3 | 1,1 | 50 | amtlich und OSM verschieden (3), Wohnstraße (OSM) (1) | `seg_88c94443792c761a` |
| Hamburg-Mitte | Versmannstraße | 3 | 1,1 | 50 | amtlich und OSM verschieden (2), HVS-Abgleich nur teilweise (1) | `seg_c4a0b9aa4944269d` |
| ohne Bezirk | Wiemerskamper Weg | 4 | 1,0 | 50, 60 | nur OSM-Tempo (4), kein amtlicher Abgleich (4) | `seg_d0ca3eeb441a779d` |
| ohne Bezirk | Niendorfer Straße | 9 | 1,0 | 50, 60 | nur OSM-Tempo (9), kein amtlicher Abgleich (9) | `seg_02aa7e94996856c5` |
| Eimsbüttel | Zum Golfplatz / Wendloher Weg | 1 | 1,0 | 50 | amtlich und OSM verschieden (1), Wohnstraße (OSM) (1) | `seg_eefb9b6756b4777a` |
| Wandsbek | Poppenbütteler Straße / Harksheider Straße | 1 | 1,0 | 50 | HVS-Abgleich nur teilweise (1) | `seg_7eba63965a884180` |
| Altona | Falkenstein | 4 | 1,0 | 50 | amtlich und OSM verschieden (4), Wohnstraße (OSM) (4) | `seg_9ef4d52591b4b4fb` |
| Hamburg-Mitte | Stormarnstraße | 1 | 1,0 | 70 | nur OSM-Tempo (1), kein amtlicher Abgleich (1) | `seg_5778160f96215b63` |
| ohne Bezirk | Alter Elbdeich | 4 | 0,9 | 50 | nur OSM-Tempo (4), kein amtlicher Abgleich (4) | `seg_ab9465b582ed6a26` |
| Altona | Am Osdorfer Born | 2 | 0,9 | 50 | amtlich und OSM verschieden (2), Wohnstraße (OSM) (2) | `seg_a1ea102a61bc6eb1` |
| Harburg | Dritte Meile | 2 | 0,9 | 50 | amtlich und OSM verschieden (2), Wohnstraße (OSM) (2) | `seg_01e9d5296b23b9c2` |
| Bergedorf | – | 20 | 0,8 | 50 | nur OSM-Tempo (19), kein amtlicher Abgleich (19), HVS-Abgleich nur teilweise (2), Wohnstraße (OSM) (2) | `seg_e814df55a00cd4b5` |
| ohne Bezirk | Altonaer Chaussee | 10 | 0,8 | 50 | nur OSM-Tempo (10), kein amtlicher Abgleich (10) | `seg_62e4c2eacef7345a` |
| … | 858 weitere Straßen | | | | | |

## 3. Sensitivitätsanalyse

Geprüft wird die Automatik (`cat_proposed`: Kaskade und Harmonisierung H-STR-01 je Lauf); fachliche Korrekturen bleiben außen vor. Basis: rules.yaml 0.16.0, 34 702 Abschnitte, 4387,3 km.

### 3.1 Einzelvariation (V-SENS-01): jede Annahme ±20 %

km mit anderer Kategorie als im Basislauf. Varianten: Annahme-Schwellen der Kaskade und `required_width` in ihren Bedingungen; zusätzlich die Gewichte von conn_score.

| Annahme | Regel | Basis | −20 %: km | Abschnitte | häufigste Wechsel | +20 %: km | Abschnitte | häufigste Wechsel |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| `thresholds.conn_gow` | C-GOW-01 | 0,6 | 313,1 | 2 831 | ETW30→GOW30 219,4, ETW30→GOW50 91,4, GOW50→GOW30 2,0 | 76,7 | 749 | GOW30→ETW30 55,2, GOW50→ETW30 20,9, GOW30→GOW50 0,5 |
| `thresholds.sensitive_radius` | C-G30-01 | 150 | 26,0 | 246 | GOW30→GOW50 25,8, GOW50→GOW30 0,2 | 21,9 | 221 | GOW50→GOW30 21,3, GOW30→GOW50 0,6 |
| `thresholds.frontage` | C-G30-01 | 0,4 | 12,5 | 102 | GOW50→GOW30 12,5, GOW30→GOW50 0,0 | 6,5 | 46 | GOW30→GOW50 6,0, GOW50→GOW30 0,5 |
| `required_width.GOW50` | C-G30-02 | 16,5 | 8,0 | 51 | GOW30→GOW50 8,0 | 8,1 | 76 | GOW50→GOW30 8,1 |
| `conn_score.betweenness_norm` | scores.conn_score | 0,35 | 47,3 | 440 | GOW30→ETW30 34,2, GOW50→ETW30 12,7, GOW30→GOW50 0,3 | 51,6 | 469 | ETW30→GOW30 37,7, ETW30→GOW50 13,1, GOW50→GOW30 0,9 |
| `conn_score.in_hvs` | scores.conn_score | 0,25 | 96,2 | 916 | ETW30→GOW30 71,8, ETW30→GOW50 23,3, GOW50→GOW30 0,9 | 58,9 | 558 | GOW30→ETW30 42,1, GOW50→ETW30 16,2, GOW30→GOW50 0,4 |
| `conn_score.bus_trips_weekday_norm` | scores.conn_score | 0,2 | 24,8 | 252 | GOW30→ETW30 19,2, GOW50→ETW30 5,3, GOW30→GOW50 0,3 | 31,9 | 304 | ETW30→GOW30 24,6, ETW30→GOW50 6,7, GOW50→GOW30 0,4 |
| `conn_score.dtv_norm` | scores.conn_score | 0,2 | 0,6 | 7 | GOW50→ETW30 0,5, GOW30→ETW30 0,1 | 0,1 | 2 | GOW30→GOW50 0,1, ETW30→GOW50 0,0 |

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
| `features.S-FEAT-11.buffer_m` | 200 | m | Merkmale (Stufe 4): wirkt nur über einen neuen Lauf ab make features |
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
| `coherence.N3.barrier_simplify_m` | 5 | m | Netzkohärenz: schreibt nur Hinweise, ändert die Kategorie nicht |
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

**Kennzahl: 2 071 Abschnitte (218,4 km, 5,0 % der Länge) sind unsicher.** Mindestens einmal gewechselt: 4 821 Abschnitte (531,7 km).

| Wechselquote | Abschnitte | km |
| --- | ---: | ---: |
| 0 (stabil) | 29 881 | 3855,6 |
| über 0 bis 0,1 | 1 186 | 137,9 |
| über 0,1 bis unter 0,3 | 1 564 | 175,5 |
| ab 0,3 (unsicher) | 2 071 | 218,4 |

Unsichere Abschnitte je Soll-Kategorie (Basis) und häufigste andere Kategorie:

| Kategorie | km gesamt | unsicher km | Anteil | häufigste andere Kategorie (km) |
| --- | ---: | ---: | ---: | --- |
| SW | 189,2 | 0,0 | 0,0 % | – |
| GOW50 | 223,2 | 32,0 | 14,4 % | ETW30 (18,9), GOW30 (13,2) |
| GOW30 | 527,3 | 64,3 | 12,2 % | ETW30 (51,1), GOW50 (13,2) |
| ETW30 | 3329,4 | 122,0 | 3,7 % | GOW30 (88,2), GOW50 (33,8) |
| ETW_ERF | 118,3 | 0,0 | 0,0 % | – |

Je Bezirk:

| Bezirk | km | unsicher km | Anteil |
| --- | ---: | ---: | ---: |
| Altona | 620,5 | 27,9 | 4,5 % |
| Bergedorf | 209,3 | 12,2 | 5,8 % |
| Eimsbüttel | 470,4 | 29,0 | 6,2 % |
| Hamburg-Mitte | 881,3 | 40,5 | 4,6 % |
| Hamburg-Nord | 563,3 | 33,3 | 5,9 % |
| Harburg | 465,2 | 13,5 | 2,9 % |
| Wandsbek | 1030,4 | 61,2 | 5,9 % |
| ohne Bezirk | 146,9 | 0,8 | 0,5 % |

Einfluss je Annahme im Monte-Carlo (Korrelation des Faktors mit dem Anteil gewechselter km je Lauf; nur zur Orientierung, nicht kausal):

| Annahme | Korrelation |
| --- | ---: |
| `thresholds.conn_gow` | -0,71 |
| `conn_score.in_hvs` | -0,24 |
| `conn_score.betweenness_norm` | +0,11 |
| `thresholds.frontage` | -0,07 |
| `thresholds.sensitive_radius` | -0,05 |
| `required_width.GOW50` | +0,04 |
| `conn_score.dtv_norm` | +0,03 |
| `conn_score.bus_trips_weekday_norm` | +0,02 |

### 3.3 Priorität: Top 30 in Hamburg (7 Bezirke) bei variierten Gewichten

Gleiche Läufe; risk mit variierten `priority.risk_weights`, Diskrepanzen aus dem Basislauf (eine geänderte Kategorie ändert auch die Diskrepanz – das ist hier nicht abgebildet). Im Mittel bleiben **92,3 % der Top 30** in der Top 30. 24 Abschnitte bleiben in mindestens 90 % der Läufe, 0 in weniger als der Hälfte.


### 3.4 Stichprobe: 30 zufällige unsichere Abschnitte in Hamburg (7 Bezirke), nach Bezirk geschichtet (Seed 42)

Zur Durchsicht: Welche Kategorie ist fachlich richtig? Befund als Korrektur in overrides/overrides.csv.

| segment_id | Bezirk | Straße | highway | Soll | andere Kategorie | Wechselquote | Wechsel bei ±20 % | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| `seg_0b225681433b7e34` | Altona | Bernadottestraße | residential | GOW30 | ETW30 (36,0 %) | 0,36 | `thresholds.conn_gow:+`, `conn_score.in_hvs:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561121,5933646]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.548148/9.922498) | [Way](https://www.openstreetmap.org/way/1178419065) |
| `seg_32b485a26dd9b143` | Altona | Fahrenort | tertiary | ETW30 | GOW30 (33,2 %) | 0,346 | `thresholds.conn_gow:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557792,5939412]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600344/9.873325) | [Way](https://www.openstreetmap.org/way/23410943) |
| `seg_65865a9f0b189fdb` | Altona | Rondenbarg | tertiary | ETW30 | GOW30 (23,0 %) | 0,38 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561083,5936813]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576616/9.922533) | [Way](https://www.openstreetmap.org/way/1167427199) |
| `seg_6c8a575d6dd3cca7` | Altona | Kalckreuthweg | tertiary | GOW50 | ETW30 (47,0 %) | 0,59 | `thresholds.conn_gow:+`, `thresholds.sensitive_radius:+`, `conn_score.betweenness_norm:-`, `conn_score.in_hvs:+`, `conn_score.bus_trips_weekday_norm:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558998,5935530]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565322/9.890803) | [Way](https://www.openstreetmap.org/way/494247496) |
| `seg_7c015096acf29b16` | Altona | Ehrenbergstraße | tertiary | ETW30 | GOW30 (48,0 %) | 0,48 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562094,5933894]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.550265/9.937217) | [Way](https://www.openstreetmap.org/way/1380076205) |
| `seg_217f310fab04b9f6` | Bergedorf | Oberer Landweg | secondary | GOW50 | ETW30 (45,0 %) | 0,662 | `thresholds.conn_gow:+`, `thresholds.sensitive_radius:+`, `conn_score.betweenness_norm:-`, `conn_score.in_hvs:+`, `conn_score.bus_trips_weekday_norm:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578761,5927510]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.490654/10.187125) | [Way](https://www.openstreetmap.org/way/516875062) |
| `seg_e027b808ae2ede7f` | Bergedorf | Rahel-Varnhagen-Weg | tertiary | ETW30 | GOW30 (45,0 %) | 0,45 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578444,5926997]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.486096/10.182221) | [Way](https://www.openstreetmap.org/way/312920345) |
| `seg_11d39bf32e7724bf` | Eimsbüttel | Frohmestraße | tertiary | ETW30 | GOW30 (46,0 %) | 0,46 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561110,5942905]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.631364/9.924137) | [Way](https://www.openstreetmap.org/way/1131066865) |
| `seg_28c898a73895f770` | Eimsbüttel | Rothenbaumchaussee | secondary | GOW30 | GOW50 (39,4 %) | 0,394 | `thresholds.conn_gow:+`, `conn_score.in_hvs:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565563,5935187]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.561458/9.989851) | [Way](https://www.openstreetmap.org/way/35170417) |
| `seg_34cb8dc4a7b0d83d` | Eimsbüttel | Kollaustraße | primary | GOW50 | GOW30 (35,6 %) | 0,356 | `thresholds.sensitive_radius:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563667,5939826]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603383/9.962177) | [Way](https://www.openstreetmap.org/way/650779301) |
| `seg_caadfc974482539b` | Eimsbüttel | Heußweg | tertiary | ETW30 | GOW30 (42,8 %) | 0,428 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563004,5936739]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575718/9.951524) | [Way](https://www.openstreetmap.org/way/362847835) |
| `seg_09e4fe23d671e1e0` | Hamburg-Mitte | Reclamstraße | tertiary | ETW30 | GOW30 (39,0 %) | 0,39 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573294,5933175]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.542352/10.106078) | [Way](https://www.openstreetmap.org/way/567809436) |
| `seg_228ec040e19525ed` | Hamburg-Mitte | Ausschläger Allee | tertiary | GOW50 | ETW30 (40,0 %) | 0,654 | `thresholds.conn_gow:+`, `required_width.GOW50:+`, `conn_score.in_hvs:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569964,5931933]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.531644/10.055554) | [Way](https://www.openstreetmap.org/way/193563495) |
| `seg_4a659a7f8e927094` | Hamburg-Mitte | Hovestieg | tertiary | GOW30 | ETW30 (42,2 %) | 0,422 | `thresholds.conn_gow:+`, `conn_score.betweenness_norm:-`, `conn_score.in_hvs:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567742,5931085]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.524319/10.021853) | [Way](https://www.openstreetmap.org/way/4374952) |
| `seg_4e594d85e08006e4` | Hamburg-Mitte | Billstedter Hauptstraße | tertiary | ETW30 | GOW30 (33,0 %) | 0,33 | `thresholds.conn_gow:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573466,5932587]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.537050/10.108522) | [Way](https://www.openstreetmap.org/way/298844200) |
| `seg_ad4e27fdaa8c372d` | Hamburg-Mitte | Ausschläger Weg | tertiary | GOW30 | ETW30 (41,8 %) | 0,418 | `thresholds.conn_gow:+`, `conn_score.betweenness_norm:-`, `conn_score.in_hvs:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568495,5934325]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.553340/10.033916) | [Way](https://www.openstreetmap.org/way/177037597) |
| `seg_092b53ecb1724b17` | Hamburg-Nord | Sengelmannstraße | service | ETW30 | GOW30 (33,8 %) | 0,422 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566889,5942078]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.623224/10.011346) | [Way](https://www.openstreetmap.org/way/89126780) |
| `seg_4467322f6006927a` | Hamburg-Nord | Hellbrookstraße | tertiary | ETW30 | GOW30 (37,6 %) | 0,376 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569020,5938570]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591424/10.042776) | [Way](https://www.openstreetmap.org/way/188565075) |
| `seg_c368125199a7aa04` | Hamburg-Nord | Alsterdorfer Straße | tertiary | ETW30 | GOW30 (34,0 %) | 0,34 | `thresholds.conn_gow:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565980,5939183]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.597321/9.996983) | [Way](https://www.openstreetmap.org/way/40989370) |
| `seg_d31527413df372a0` | Hamburg-Nord | Tangstedter Landstraße | tertiary | GOW30 | ETW30 (50,4 %) | 0,504 | `thresholds.conn_gow:+`, `conn_score.betweenness_norm:-`, `conn_score.in_hvs:+`, `conn_score.bus_trips_weekday_norm:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567761,5947212]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.669250/10.025646) | [Way](https://www.openstreetmap.org/way/957978454) |
| `seg_fd41b409622147d9` | Hamburg-Nord | Alter Teichweg | tertiary | ETW30 | GOW30 (38,0 %) | 0,38 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570242,5937898]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.585217/10.061081) | [Way](https://www.openstreetmap.org/way/147278950) |
| `seg_b7cd7c816b35352b` | Harburg | Marmstorfer Weg | tertiary | GOW50 | ETW30 (49,4 %) | 0,71 | `thresholds.conn_gow:+`, `thresholds.sensitive_radius:+`, `conn_score.betweenness_norm:-`, `conn_score.in_hvs:+`, `conn_score.bus_trips_weekday_norm:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564341,5921900]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.442196/9.968673) | [Way](https://www.openstreetmap.org/way/578238938) |
| `seg_bf6e370e7ea18ec0` | Harburg | Wilstorfer Straße | tertiary | GOW30 | ETW30 (36,4 %) | 0,364 | `thresholds.conn_gow:+`, `conn_score.in_hvs:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565588,5923055]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.452424/9.987690) | [Way](https://www.openstreetmap.org/way/485697041) |
| `seg_021f50d63136cb18` | Wandsbek | Bargteheider Straße | primary | GOW30 | GOW50 (51,2 %) | 0,512 | `thresholds.frontage:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576024,5940354]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.606485/10.149004) | [Way](https://www.openstreetmap.org/way/222135546) |
| `seg_523089be27066ee5` | Wandsbek | Allensteiner Straße | tertiary | ETW30 | GOW30 (44,0 %) | 0,44 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571170,5938623]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591607/10.075273) | [Way](https://www.openstreetmap.org/way/1221989841) |
| `seg_6e23a575ecd054c8` | Wandsbek | Stapelfelder Straße | tertiary | ETW30 | GOW30 (35,8 %) | 0,358 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578171,5939993]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.602923/10.181365) | [Way](https://www.openstreetmap.org/way/43159245) |
| `seg_8c8023d66bf68ac6` | Wandsbek | Bargteheider Straße | primary | GOW30 | GOW50 (51,2 %) | 0,512 | `thresholds.frontage:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575988,5940284]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.605861/10.148440) | [Way](https://www.openstreetmap.org/way/222135546) |
| `seg_d67c075285903eaa` | Wandsbek | Schöneberger Straße | tertiary | ETW30 | GOW30 (42,8 %) | 0,428 | `thresholds.conn_gow:-`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575439,5937847]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.584035/10.139569) | [Way](https://www.openstreetmap.org/way/24526487) |
| `seg_d990b4c9ac624962` | Wandsbek | Meiendorfer Mühlenweg | tertiary | ETW30 | GOW50 (45,8 %) | 0,458 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574141,5944618]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645076/10.121566) | [Way](https://www.openstreetmap.org/way/46695448) |
| `seg_ea0e3c6b9fe13a1c` | Wandsbek | Neumann-Reichardt-Straße | tertiary | ETW30 | GOW30 (49,0 %) | 0,49 | `thresholds.conn_gow:-`, `conn_score.betweenness_norm:+`, `conn_score.in_hvs:-`, `conn_score.bus_trips_weekday_norm:+` | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571463,5936531]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572770/10.079214) | [Way](https://www.openstreetmap.org/way/36971826) |

## 4. Datenqualität je Bezirk

Conflation-Trefferquote = Anteil der km mit amtlichem Gegenstück (match_quality exact oder partial, S-CONF-01). OSM-Tag-Vollständigkeit = Anteil der Abschnitte mit bekanntem Wert (S-FEAT-10; fehlende Tags heißen unbekannt). DTV gibt es nur auf Hauptverkehrsstraßen (2019); weil `in_hvs` selbst aus den DTV-Linien stammt (S-CONF-04), fehlt DTV auf HVS nie. Aussagekräftiger ist der Anteil der OSM-Hauptstraßen (primary, secondary) ohne DTV: Kandidaten für Lücken im HVS-Abgleich.

| Bezirk | Abschnitte | km | Conflation-Treffer (km) | davon exact | OSM-Tags Mittel | ohne Ist-Tempo | Hauptstraßen (OSM) | davon ohne DTV | alle ohne DTV |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Wandsbek | 7 542 | 1030,4 | 94,4 % | 92,3 % | 49,2 % | 5,0 % | 1 271 | 14,7 % | 85,5 % |
| Hamburg-Mitte | 6 839 | 881,3 | 89,4 % | 85,9 % | 61,4 % | 8,5 % | 1 726 | 26,2 % | 78,5 % |
| Altona | 4 886 | 620,5 | 91,5 % | 89,5 % | 58,6 % | 5,4 % | 822 | 18,6 % | 85,4 % |
| Hamburg-Nord | 5 136 | 563,3 | 93,7 % | 91,6 % | 65,0 % | 4,5 % | 1 238 | 20,2 % | 79,7 % |
| Eimsbüttel | 4 004 | 470,4 | 95,8 % | 93,5 % | 65,3 % | 5,2 % | 953 | 22,9 % | 80,3 % |
| Harburg | 3 348 | 465,2 | 88,7 % | 83,5 % | 49,8 % | 10,4 % | 564 | 19,3 % | 84,1 % |
| Bergedorf | 1 957 | 209,3 | 90,0 % | 86,5 % | 38,1 % | 13,3 % | 280 | 37,5 % | 90,6 % |
| ohne Bezirk | 990 | 146,9 | 0,6 % | 0,0 % | 38,5 % | 29,6 % | 105 | 94,3 % | 99,4 % |
| gesamt | 34 702 | 4387,3 | 89,1 % | 86,4 % | 56,2 % | 7,4 % | 6 959 | 22,6 % | 83,2 % |

OSM-Tag-Vollständigkeit je Merkmal (Anteil der Abschnitte mit bekanntem Wert):

| Bezirk | baulicher Radweg | Radfahrstreifen | Mittelmarkierung | Parken | Fahrstreifen | Belag | maxspeed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Wandsbek | 54,1 % | 54,1 % | 16,3 % | 5,0 % | 37,1 % | 94,2 % | 83,5 % |
| Hamburg-Mitte | 68,2 % | 68,2 % | 18,1 % | 43,8 % | 52,4 % | 98,0 % | 81,0 % |
| Altona | 64,2 % | 64,2 % | 18,1 % | 43,0 % | 38,5 % | 97,5 % | 85,1 % |
| Hamburg-Nord | 80,9 % | 80,9 % | 15,3 % | 44,0 % | 47,5 % | 99,3 % | 87,4 % |
| Eimsbüttel | 82,3 % | 82,3 % | 16,9 % | 41,9 % | 46,5 % | 99,8 % | 87,0 % |
| Harburg | 52,2 % | 52,2 % | 19,0 % | 16,1 % | 40,5 % | 90,6 % | 77,7 % |
| Bergedorf | 29,2 % | 29,2 % | 12,7 % | 10,1 % | 30,0 % | 93,8 % | 61,4 % |
| ohne Bezirk | 37,8 % | 37,8 % | 9,2 % | 3,3 % | 32,2 % | 77,9 % | 71,4 % |
| gesamt | 63,5 % | 63,5 % | 16,7 % | 29,3 % | 42,7 % | 96,0 % | 82,1 % |

Abschnitte ohne Ist-Tempo: 7,4 % (Ziel unter 5,0 %, V-DQ-01, guide.md 3.4): **nicht erfüllt**.

Auf der Webseite zeigt die Ampel „Datenunsicherheit“ je Abschnitt fehlende und unsichere Eingangswerte (C-CONF-01); neu ist der Hinweis „unsicher“ aus der Sensitivitätsanalyse.

## 5. Manuelle Stichproben

Ziel (V-SAMP-01, guide.md 7.1): unter 15,0 % fachlich strittig je Kategorie. Stand der Dateien in reports/:

**Conflation (reports/conflation_sample.csv, Spalte check_ok):** 0 von 50 Zeilen geprüft – **Durchsicht offen**.

**Klassifikation (reports/classification_sample.csv, Spalten check_ok, cat_expected_manual):** 0 von 150 Zeilen geprüft – **Durchsicht offen**.

**Transekte (reports/transect_sample.geojson, Spalte measured_m):** 0 von 50 nachgemessen – **Durchsicht offen**.

**Korrekturen (overrides/overrides.csv):** 7 Einträge, davon 7 approved. **Rückmeldungen von Ortskundigen:** noch keine (Rückmeldekanal nicht eingerichtet, docs/open_questions.md).

## Vergleich mit dem Pilotlauf Eimsbüttel

Pilotlauf: rules.yaml 0.12.0, Normierung über Eimsbüttel + 500 m. Jetzt: Normierung über ganz Hamburg (S-FEAT-01), Schwellen unverändert. Verglichen werden Abschnitte mit gleicher segment_id.

- Abschnitte in beiden Läufen: 4004; nur im Pilotlauf: 0; nur jetzt: 0
- Kategorie (cat_final) geändert: 49 Abschnitte, 5,3 km (1,1 % der Länge)
- Top 30 der Priorität: 86,7 % sind in beiden Läufen in der Top 30

| vorher | jetzt | Abschnitte | km |
| --- | --- | ---: | ---: |
| ETW30 | GOW30 | 31 | 3,7 |
| GOW30 | ETW30 | 11 | 1,2 |
| ETW30 | GOW50 | 2 | 0,2 |
| GOW30 | GOW50 | 3 | 0,1 |
| GOW50 | GOW30 | 1 | 0,1 |
| GOW50 | ETW30 | 1 | 0,0 |

## 6. Grenzen

### Fachlich (guide.md 7.2)

- Die niederländischen Kategorien passen nicht eins zu eins auf RIN/RASt; die Zuordnung ist eine Näherung.
- Die GOW30-Merkmale der CROW (2023) sind ausdrücklich vorläufig; ihre Wirkung wird erst evaluiert.
- Ein Soll-Plan sagt wenig über die Umsetzung: Richtlinien werden oft nicht eingehalten (SWOV 2023).
- Multifunktionale Hauptstraßen landen konsequent in GOW30: 70,0 % der HVS-km in GOW50/GOW30 sind GOW30 – fachlich folgerichtig, politisch der härteste Punkt.
- Busbetrieb, Rettungswege und Wirtschaftsverkehr sind nur Overlays; Fahrzeitwirkungen sind nicht modelliert.

### Rechtlich (guide.md 7.3)

- Der Plan ist kein Verwaltungsakt und keine Anordnung; Tempo auf Hauptverkehrsstraßen setzt weiter die Voraussetzungen der StVO voraus.
- GOW30 begründet in Deutschland derzeit kein flächiges Tempo 30 auf Hauptverkehrsstraßen; es kann Einzelfälle und ein Gesamtkonzept begründen.
- Lizenzen: dl-de/by-2.0- und ODbL-Pflichten; für die amtlichen Tempo- und Verkehrsmengendaten fehlt die Lizenzangabe in der API (offen). Unfälle nur als Summen je Abschnitt.

### Methodisch (guide.md 7.4 und dieser Lauf)

- Kfz-Verkehrsstärken fehlen auf 83,2 % der Abschnitte (DTV nur auf HVS, Stand 2019); Betweenness bildet Verkehr nicht ab.
- HVS aus den DTV-Linien 2019 statt der HVS-Karte 2023 (S-CONF-04); Lücken im Abgleich erzeugen Abweichungen in Abschnitt 1.
- OSM-Attribute sind ungleich vollständig (im Mittel 56,2 % der Gestaltungsmerkmale bekannt); die Ist-Gestaltung und damit die Diskrepanz ist dort unsicher.
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

**Netz und Segmentierung (Prompt 04, rules.yaml 0.2.0)** (1)

- Schwelle S-NET-03 freigeben: Abschnitte erst ab 400 m bei maxspeed-Wechsel teilen (Annahme aus guide.md 3.2) – Verkehrsplaner*in

**Conflation (Prompt 05, rules.yaml 0.3.0)** (4)

- Schwellen S-CONF-01/02 freigeben: Puffer 15 m, Winkel 20°, Überdeckung 60 %, Zonen-Längenanteil 50 % (Startwerte, per Stichprobe reports/conflation_sample.csv kalibrieren) – Verkehrsplaner*in
- `in_hvs` stammt aus den DTV-Linien HVS 2019 statt aus der HVS-Karte 2023. Bis HH-SIB wieder erreichbar ist oder die Karte digitalisiert ist: Abweichungen 2019 → 2023 bekannt? – GIS
- Mehrdeutige zeitlich begrenzte Regelungen: „30 km/h 22 - 6 h Lärmschutz“ mit Feld geschwindigkeit = 30 (Regeltempo unbekannt) und „… sonst 50km/h“ mit geschwindigkeit = 50 (begrenztes Tempo unbekannt). Was ist das Regeltempo? – GIS
- Fußgängerzonen (highway=pedestrian) sind in den Tempo-/Widmungsebenen meist nicht enthalten (86 % none) – amtliche Quelle für Fußgängerzonen? widmung_flaeche („für den Fußgängerverkehr“) nutzen? – GIS

**Merkmale (Prompt 06, rules.yaml 0.4.0)** (5)

- Standardtempo je highway-Klasse für die Reisezeit (S-FEAT-02: motorway 100, trunk 70, residential 30, living_street 7, übrige 50 km/h) freigeben. Betrifft 5,5 % der Abschnitte im Arbeitsgebiet – Verkehrsplaner*in
- Puffer freigeben: Gebäudedichte 50 m, Einwohner 100 m, Publikumsnutzung 20 m, Knoten-Fangradius 1 m (S-FEAT-03/04/05/10) – Verkehrsplaner*in
- Listen alkis_public_functions / alkis_ancillary_functions (S-FEAT-05) fachlich prüfen, v. a. „Gemischt genutztes Gebäude mit Wohnen“ (707 Gebäude) und „Bürogebäude“ (nicht gezählt). Mit ALKIS steigt der Anteil der Abschnitte mit shop_frontage_share ≥ 0,4 (C-G30-01) von 17 % auf 27 % – Verkehrsplaner*in
- `outside_builtup_area` (C-RUR-01) hat keine Datenquelle (Ortsgrenze/Ortstafeln). 2026-11-04 geprüft: OSM-Ortstafeln schließen kein ländliches Gebiet ab (ein zusammenhängendes Netz von 4 472 km); darum werden ländliche Stadtteile vorerst nicht klassifiziert. Amtliche Quelle für Ortsdurchfahrten/Ortstafeln (Straßenverkehrsbehörde, HH-SIB) ermitteln – GIS
- GTFS-Fahrplanperiode endet 2026-12-12; danach neuen Datensatz wählen. Repräsentativer Werktag des aktuellen Feeds: 2026-04-29 (Mi). Getrennte Richtungsfahrbahnen erhalten nur die Fahrten ihrer Richtung – Team – 2026-11-07 geprüft: neuester Feed Oktober–Dezember 2026 (bis 2026-12-13), noch keiner für die Periode ab Dezember; Mitte Dezember erneut prüfen

**Querschnitt (Prompt 07, rules.yaml 0.7.0)** (2)

- 50 Transekte im DOP20 messen (reports/transect_sample.geojson) und in reports/transect_measurements.csv eintragen; Ziel mittlere absolute Abweichung < 1 m (Annahme) – GIS
- GOW30_narrow ist ein Bereich (10,80–13,40 m); die Machbarkeit nutzt die Untergrenze (range_reference: min). Passt das? – Verkehrsplaner*in

**Klassifikation (Prompt 08, rules.yaml 0.8.0)** (4)

- C-MISS-01 und C-CONF-01 fachlich freigeben (Defaults outside_builtup_area = false, override_school_street = false, crossing_demand = not_assessed; Liste der Fallback-Quellen). Folge: Nur SW erreicht „hoch“ (5 % der Länge), 85 % sind „mittel“, solange Ortsgrenze, Schulstraßen-Overrides, HVS-Karte 2023 und amtliche Schulen/Kitas fehlen – Verkehrsplaner*in
- HVS in Eimsbüttel: 45,6 km GOW30 gegenüber 29,9 km GOW50 (60 % der HVS-km werden GOW30), fast immer über C-G30-01 (Schule/Kita ≤ 150 m bei 443, Publikumsnutzung ≥ 0,4 bei 386 von 600 GOW30-Abschnitten, Mehrfachnennung). Plausibel, oder sind sensitive_radius/frontage zu weit? (Schwellen nicht geändert) – Verkehrsplaner*in – 2026-11-07: Obergrenze gow30_max_dtv (CROW-Profil 10 000 Kfz/24h) für den Auslöser auf Hauptverkehrsstraßen, darüber C-G50-02 mit Hinweis Tempo-30-Abschnitt (Entscheidung prstolpe, rules.yaml 0.14.0); Schwellen sensitive_radius/frontage unverändert – 2026-11-07: Obergrenze wieder zurückgenommen (rules.yaml 0.15.0): Umfeld vor heutiger Verkehrsmenge; Regel später verbessern (prstolpe) – Variante mit Obergrenze als Kompromiss gesichert: docs/variants.md (Tag variante-gow50-kompromiss)
- Varianten umschaltbar machen: Regelwerk-Varianten (z. B. „Kompromiss Hamburg“ mit GOW30-Obergrenze, docs/variants.md) als benannte Schalter in rules.yaml führen und beide Ergebnisse auf der Webseite vergleichbar machen? – Methodik
- guide.md 3.4 nennt die Spalte `cat_confidence`, prompts/08 und die Pipeline `confidence`. guide.md angleichen? – Methodik

**Netzkohärenz und Korrekturebene (Prompt 09, rules.yaml 0.9.0)** (7)

- Neue Annahmen freigeben: N1 Stadtgrenze ≤ 50 m, N2 Straßenzug ≤ 30° Richtungsänderung (Richtung über 15 m), N6 Ampel/Plateau im Umkreis 30 m – Verkehrsplaner*in
- N3: Schwelle für „sehr lange Grenze im Verhältnis zur Fläche“ fehlt (guide.md 1.5). Kompaktheit 4π·A/U² wird berichtet; ab welchem Wert markieren? – Verkehrsplaner*in
- N5: Ob an einem Übergang GOW→ETW oder GOW50→GOW30 eine Torsituation vorhanden ist, steht in keiner Quelle. Merkmal festlegen (z. B. Gehwegüberfahrt, Plateau, Einengung) und Datenquelle – Verkehrsplaner*in, GIS
- N6: Tabelle 1.4 deckt SW–GOW50 (50 Knoten), SW–SW (49), ETW_ERF–ETW_ERF (40) und SW–ETW30 nicht ab (not_defined). Soll-Knotentyp festlegen? – Verkehrsplaner*in
- N6: GOW50–GOW30 gilt als „Kreisverkehr, sonst Signal mit Plateau“ (Zeile GOW50), GOW30–GOW30 als Kreisverkehr. So gemeint? Kreisverkehr an ETW–ETW-Knoten (64) gilt als Abweichung von „gleichrangig“ – Verkehrsplaner*in
- N6: Gehwegüberfahrten und Vorfahrtregelung (give_way/stop) sind in OSM kaum erfasst; die meisten Knoten sind not_checkable. Quelle für Ist-Knotentypen? – GIS
- Flag-Liste fachlich durchsehen (reports/coherence.md, Stichprobe, reports/coherence_flags.geojson) – Verkehrsplaner*in

**Diskrepanz und Priorisierung (Prompt 10, rules.yaml 0.10.0)** (6)

- **Top 30 gegenlesen** (reports/priority_top30.md, Spalte „Prüfung“) – Ortskundige
- Zuordnung flow/sparse je Verstoß und damit D1–D3 (D-DES-01, D-TYPE-01) an Beispielen der Sichtprüfung beurteilen (reports/discrepancy.md, Stichprobe) – Verkehrsplaner*in
- `bahnigkeit_official` als Mitteltrennung: Bedeutung des Attributs (1/2) in der Quelle nicht bestätigt. 173 von 367 GOW50-Abschnitten haben ≥ 2 Fahrstreifen je Richtung bei bahnigkeit 1 (z. B. Kieler Straße) – GIS
- Nutzung nur für GOW30 prüfbar (nur dort max_dtv) und DTV nur auf Hauptverkehrsstraßen 2019 (918 von 4 787 Abschnitten). max_dtv für ETW30 (Erschließung) und GOW50 festlegen? – Verkehrsplaner*in
- Mittelmarkierung (GOW30) ist bei 98,7 % unbekannt (OSM lane_markings kaum erfasst); Gestaltungs-Diskrepanz auf GOW30 daher fast nur über die Radführung – GIS
- Risiko berücksichtigt nur Unfälle mit Fuß-/Radbeteiligung (polizeilich erfasst). Rettungsdienstdaten wie in Amsterdam (guide.md) verfügbar? – Team

**Export und Webseite (Prompt 11)** (2)

- Test auf einem echten Smartphone und mit Bildschirmleser (VoiceOver/NVDA); automatisch geprüft sind nur axe-core und emuliertes Pixel 7 (reports/web_accessibility.md) – Team
- Texte der Methodenseite und der Steckbriefe (config/plain_language.yaml) fachlich und auf einfache Sprache prüfen; Fotos aus Panoramax je Kategorie fehlen noch (guide.md 5.5) – Verkehrsplaner*in

**Netz und Harmonisierung (rules.yaml 0.12.0, 2026-11-04)** (3)

- Tracks mit maxspeed=walk (z. B. Amselweg, Hamburg-Nord) werden ETW30; eigene Regel für ETW_ERF? – Verkehrsplaner*in
- H-STR-01 lässt ETW_ERF/ETW30-Inseln stehen (5 Abschnitte, N2) – bei Bedarf ergänzen – Verkehrsplaner*in
- H-STR-01 verlängert kurze GOW30-Stücke (z. B. vor Schulen) auf 200 m; ob 200 m (N2 min_run_m) als Mindestlänge für Tempo-30-Abschnitte passt, fachlich prüfen – Verkehrsplaner*in

**Validierung und Sensitivität (Prompt 12, rules.yaml 0.11.0)** (7)

- conn_gow ist die mit Abstand einflussreichste Annahme: −20 % (0,48) macht 39,8 km zu GOW, vor allem ETW30 → GOW30 (z. B. Mittelweg, Lohkampstraße, Wördemanns Weg). Schwelle am HVS-Netz und an Stichproben kalibrieren – Verkehrsplaner*in
- Das Gewicht von in_hvs in conn_score wirkt auf Nicht-HVS-Straßen wie ein Abzug (ihr Wert 0 zählt mit, HVS greift ohnehin über C-GOW-01). −20 % auf dieses Gewicht macht 15,2 km zu GOW. in_hvs aus conn_score herausnehmen? – Verkehrsplaner*in – 2026-11-07 Probelauf: ohne in_hvs im conn_score werden 430 km ETW30 zu GOW (289 km GOW30, 141 km GOW50), z. B. Flughafenstraße, Alsterdorfer Straße, Walddörferstraße; Entscheidung offen – zurückgestellt für den Fachplaner-Termin (prstolpe 2026-11-07)
- 292 Soll-ETW30-Abschnitte mit Ist-Tempo > 30 sind mögliche Datenfehler (Zone 30 laut Zonenebene, Quellen widersprechen sich, nur OSM-Tempo, HVS-Abgleich teilweise). Liste in reports/validation.md Abschnitt 2 durchsehen; z. B. Osterstraße (nur OSM-Tempo 50) – GIS
- Hauptstraßen mit Soll ETW30 (Kieler Straße, Vogt-Wells-Straße, primary) deuten auf Lücken im HVS-Abgleich (S-CONF-04, nur match exact) – GIS
- Abschnitte ohne Ist-Tempo 7,3 % (Ziel unter 5 %, V-DQ-01); im Randbereich „ohne Bezirk“ 24 % – GIS
- Manuelle Stichproben (reports/conflation_sample.csv, classification_sample.csv, transect_sample.geojson) sind nicht ausgefüllt; ohne sie ist der Entwurf nach guide.md Teil 7 nicht veröffentlichungsreif – Team
- Externe Fachprüfung: reports/validation.md an Hochschule oder Planungsbüro geben – Team

**Ganz Hamburg (rules.yaml 0.13.0, 2026-11-04)** (2)

- Neuwerk/Scharhörn ausgeschlossen (Entscheidung 2026-11-04); später als eigenes kleines Gebiet aufnehmen? – Team
- DB Rad+ jahr2025: Abruf scheitert seit 2026-11-04 auch ohne bbox (abgebrochenes JSON ab offset 1000). Bei der Datenstelle melden – Team

**Radnetz (Prompt 14, cycling_rules.yaml/design_rules.yaml 0.1.1, sources.yaml 0.1.9, 2026-11-05)** (34)

- Projekt-Sollbreiten (`widths_m.project_target`) zwischen ERA-Regelmaß und NL-Hauptnetz festlegen – Verkehrsplaner*in
- CROW-Ontwerpwijzer 2016 im Original: Umwegfaktor, Breiten nach Intensität, Fahrradstraßen-Kriterien prüfen – Verkehrsplaner*in
- ERA 2010 Bild 7 (Belastungsbereiche) und Neufassung ERA prüfen; S-04 anpassen – Verkehrsplaner*in
- Kapazitätsschwellen L-02 (900 Kfz/h je Fahrstreifen, v/c 0,85) und Kreisverkehrsgrenzen (25.000/35.000 Kfz/24h) mit HBS abgleichen – Verkehrsplaner*in
- Vorrang Radverkehr am Kreisverkehr (CROW vs. SWOV vs. StVO/VwV) – Entscheidung und Rechtsprüfung – Team
- Hamburger Standards (ReStra, PLAST Radverkehr) als zusätzliche Quelle `hamburg` einpflegen – GIS/Verkehrsplanung
- Metadaten-Ergänzungen in 0.1.1 freigeben (Werte unverändert): als `assumption` markiert wurden RSV `trip_length_km` [5, 15], `principle_weights`, `lanes.default_per_direction`, L-02, L-04; PL-01 war `swov_crow` ohne Quelle und ist jetzt `assumption` (CROW-Quelle ergänzen?); PL-03 hat die Quelle ERA_2010 erhalten (Trennstreifen buffer_to_parking) – Verkehrsplaner*in
- ETW60 außerorts: Ist `mixed` bei DTV ≤ `mixed_rural_max_dtv` nur erlaubt oder die Soll-Führung? Goldener Fall s14 deckt nur DTV > 2 500 ab – Verkehrsplaner*in
- Prompt 15 (cycling_rules.yaml 0.2.0): neue Annahmen freigeben – Verkehrsplaner*in - Widerstand Ist (C-IMP-01…08): Zuordnung der Kanten zu den bestehenden Faktoren; Tempo-Grenze 30 km/h; C-IMP-06 Hauptstraße Tempo 30 ohne Radstreifen hat keinen eigenen Faktor (vorläufig 1,25 wie mit Radstreifen) - Radgraph (C-GRAPH-01…06): nur cycleway sowie path/footway/pedestrian/bridleway mit bicycle=yes|designated|permissive; highway=track/service außerhalb der Straßenabschnitte bleiben draußen, auch mit Radfreigabe. Aufnehmen? Fähren: Wartezeit 450 s pauschal (aus GTFS-Takt ableiten?), Anbindung ≤ 400 m; Radgeschwindigkeit 15 km/h - Nachfrage (C-DEM-01…07): Zonen 500 m; Zielgewichte Geschossfläche 0,40 / Geschäfte 0,20 / Schulen 0,15 / Hochschulen 0,10 / Schnellbahn 0,15; β = 0,25/km im Band 0,5–15 km; 3 Läufe mit σ = 0,1; mindestens 150 Werktage je Zählstelle; Querschnitt ±25 m, Winkel ≥ 45°; Konfidenz: 500 m, Faktor 2, 2 km Grenzabstand, 50 Rad/Tag
- Prompt 16 (cycling_rules.yaml 0.3.0): neue Annahmen C-NET-01…13 freigeben – Verkehrsplaner*in - Korridorpunkte: Innenstadt = Rathausmarkt (Koordinate gesetzt); Umsteigeknoten = ≥ 2 Verkehrsmittel im Umkreis 250 m; nur OSM amenity=university; Arbeitsplatzschwerpunkte = Zonen ab 98-%-Quantil der Geschossfläche; Zusammenfassen ab 500 m; Paare = 4 nächste bis 15 km plus Innenstadt - Soll-Widerstand je cat_final (Faktoren aus routing_impedance), Bonus Nachfrage bis −30 % ab 2.000 Rad/Werktag, Bonus amtliches Radnetz × 0,8 (alle Status) - RSV: Lücken bis 500 m überbrückt; Barrieren Bahn/Flüsse/Kanäle; Ausschlussflächen ≥ 5 ha (Wasser, Wald, Parks, Friedhöfe, Flughafen); Kernbereich der Verdichtung 0,5; 40 Runden; Mindestlänge Teilungsroute 50 m - BASIS-Anbindung von Schulen und Nahversorgung (supermarket, convenience, bakery, butcher, greengrocer, chemist) ab 150 m - P-ATT-03: Läufe ab 300 m, höchstens 60 m an der Hauptstraße zum Anschließen/Queren; Kontinuität: Lücken bis 200 m angehoben
- Prompt 16: Hochschulen aus OSM enthalten Einzelgebäude und Institute („Gebäude D“, „Institut für Theoretische Physik“); amtliche Hochschulstandorte würden Korridorpunkte bereinigen (siehe Daten: Hochschulen) – GIS
- 83 km Straßen tragen in OSM einen Radweg (separated_cycle_track_present), der Radgraph hat aber weder begleitenden noch parallelen Weg (Kante mit Faktor C-IMP-07). Tags prüfen oder Radweg in c01 aus dem Straßen-Tag ableiten – GIS
- Prompt 17 (cycling_rules.yaml 0.4.0): neue Annahmen C-PRI-01…16 freigeben – Verkehrsplaner*in - Score-Formen je Prüfung (C-PRI-01), Prinzip-Score = Mittel der Prüfungen mit gleichem Gewicht; Teilerfüllung der Trennungsmatrix 0,5 (C-PRI-03: Zweirichtungs- statt Einrichtungsradweg, Mischverkehr statt Fahrradstraße, Radweg statt eigener Trasse) - Begleitende Radwege ersetzen die Führung der Straße daneben (C-PRI-02); eigene Wege ohne Sollbreite vorläufig wie Zweirichtungsradweg (C-PRI-08) - Umweg-Stichprobe 200 OD-Paare je Kategorie, Seed 42, Band trip_length_km (C-PRI-04); Halte an LSA und bei Wartepflicht wie im Radgraphen, auch an Routenenden (C-PRI-05) - Grünanteil: ALKIS-Nutzungen (Wald, Gehölz, Sport/Freizeit/Erholung, Friedhof, Landwirtschaft, Heide, Moor, Sumpf) und OSM-Bäume mit 4 m Kronenradius, Ziel 30 % im 20-m-Puffer (C-PRI-10); Wechsel der Führung höchstens 1 je km (C-PRI-12); confidence high ab 0,8, medium ab 0,6 (C-PRI-13) - Rangfolge des Handlungsbedarfs nach Δ × km statt Δ allein (C-PRI-14), sonst stehen 100–500 m lange Verdichtungsstücke vorn
- Prompt 17: Lärm (P-ATT-02), Steigung (P-COM-03) und Knotentyp (P-SAF-02) sind nicht bewertet; confidence liegt daher höchstens bei 0,84. Lärmkarte (sources.yaml noise_maps) und Straßenbaumkataster (street_trees) als Endpunkte ermitteln? – GIS
- Prompt 17: Breite ist nur auf 11 % der Netzlänge mit Radanlage in OSM erfasst (width, cycleway:width); P-COM-01 stützt sich fast nur auf den Belag. Breiten aus Querschnitten (Prompt 19) oder Ortsbegehung? – GIS
- Prompt 17: 20 Routen zur Durchsicht mit Ortskundigen in reports/cycle_principles_review.csv eintragen (Spalten reviewer, assessment, comment) – Team
- Prompt 18 (cycling_rules.yaml 0.5.0): neue Annahmen C-FAC-01…07 freigeben – Verkehrsplaner*in - Kfz-DTV fehlt auf 99,9 % der ETW30-Abschnitte (nur HVS-Zählung 2019). Fahrradstraßen-Bedingung (C-FAC-02) und S-04 (C-FAC-03) gelten ohne DTV vorläufig als erfüllt (Entscheidung Projektteam 2026-11-06, Flag `dtv_unknown`, confidence medium; 3 452 km). Kfz-Mengen für Erschließungsstraßen beschaffen oder schätzen? - Kfz-Spitzenstundenanteil 0,10 (C-FAC-03) aus der Notiz zu L-02 übernommen; mit HBS abgleichen. „Radverkehr dominant“ = Rad/h (beide Richtungen) ≥ Kfz/h - cycle_cat_final je Abschnitt = höchste Kategorie seiner Kanten und begleitenden Radwege; Radverkehr = Maximum über die Kanten (Näherung) - Lücke „zu schmal“ gegen die Projekt-Sollbreite (nicht gegen das DE-Minimum); Ist-Breite ist nur auf 119 km bekannt - Begleitende Radwege auf beiden Straßenseiten zählen als Radweg je Seite, auch wenn sie in beiden Richtungen befahrbar sind (C-FAC-05; weicht von C-PRI-02 ab, c04 zählt sie als Zweirichtungsradweg). C-PRI-02 angleichen?
- Prompt 19 (design_rules.yaml 0.2.0): neue Annahmen PRF-01…07 freigeben (Entscheidungen prstolpe 2026-11-06: Busse aus GTFS-Stundenmaximum, Zusatzbausteine nach Ist, Fallback nach D1/D2) – Verkehrsplaner*in - PRF-01: Ist-Fahrstreifen = max(amtlich in/gegen), sonst OSM lanes/2; Einrichtungsverkehr = eine amtliche Richtung 0 und bahnigkeit ≠ 2; bei bahnigkeit 2 ganzes Profil mit beiden Richtungen (Bedeutung von bahnigkeit unbestätigt, siehe oben); ohne DTV an GOW50 Soll = Ist (höchstens 2) - PRF-02: Spitzenstunde der Busse aus der Abfahrtsstunde an der ersten Haltestelle; auf langen Linien liegt der Abschnitt bis zu einer Stunde später. Genauer: Zeit an der nächstgelegenen Haltestelle (stop_times je Haltestelle) – lohnt der Aufwand? - PRF-03: Gehwege beidseitig; Baumstreifen beidseitig an GOW50/GOW30; Ladezone einseitig bei shop_frontage_share ≥ 0,4 (Schwelle aus C-G30-01); Parken nur, wo OSM parking erfasst ist; Zweirichtungsradweg links - PRF-04: GOW30-Fahrbahn = untere Grenze der CROW-Profile (5,80 m bis DTV 6 000, sonst 8,40 m), Radfahrstreifen zusätzlich – oder liegen sie innerhalb der CROW-Spanne? Einrichtungsstraßen: GOW 3,25 m je Fahrstreifen, ETW 4,00 m (Fahrradstraßen-Fahrbahn, Rad in Gegenrichtung) – beides ohne Quelle - PRF-04: Für SW, GOW80 und ETW60 fehlen Profilregeln (Fahrstreifenbreiten außerorts, Gehwege außerorts); derzeit kommen GOW80/ETW60 in cat_final nicht vor - PRF-06: Trennstreifen PL-04 nur 0,75 m (elements_min_m); die Annahme 1,00 m bei GOW50 mit Bus steht nur im Text von PL-04 – als Wert aufnehmen?
- Prompt 19: 362 von 523 km GOW30 haben ein DTV über dem breiten CROW-GOW30-Profil (> 10 000 Kfz/Tag; Flag gow30_dtv_above_profile in reports/cross_section_soll.md). Passt die Einstufung dieser Hauptverkehrsstraßen als GOW30, oder braucht GOW30 mit hoher Belastung eigene Fahrbahnbreiten? – Verkehrsplaner*in – 2026-11-07: siehe rules.yaml 0.14.0 (C-G30-01 Obergrenze, C-G50-02) – 2026-11-07: Obergrenze wieder zurückgenommen (rules.yaml 0.15.0): Umfeld vor heutiger Verkehrsmenge; Regel später verbessern (prstolpe) – Variante mit Obergrenze als Kompromiss gesichert: docs/variants.md (Tag variante-gow50-kompromiss)
- Prompt 20 (design_rules.yaml 0.3.0): neue Annahmen J-M-01…07 und die Zuordnung JC-01…05 (applies_to) freigeben – Verkehrsplaner*in - Kategoriepaar: Prompt 20 nennt „die beiden ranghöchsten Arme“; wörtlich wäre jede Einmündung an einer GOW50 ein Paar GOW50+GOW50 (Kreisverkehr/LSA). Gewählt ist die N6-Lesart (durchgehender Zug zählt einmal). So gemeint? - Clusterradius 25 m über verbindende Abschnitte; 63 Knotenpunkte sind größer als 50 m (bis 187 m, Ketten in dichten Netzen). Zusätzlich eine Obergrenze der Ausdehnung? - Richtungsfahrbahnen: gleicher Name, gleicher DTV, Richtung ≤ 30° = ein Arm. Bestätigen, dass der amtliche DTV auf beiden Richtungsfahrbahnen der Querschnittswert ist - Platz: Suchradius 40 m, umschlossene Inseln zählen als Fläche; Turbokreisverkehr nutzt dieselbe Platzschwelle wie der einstreifige (roundabout_min_radius). Eigener Wert für Turbokreisverkehre? - Unbekannte Bedingung (DTV oder Platz fehlt) → Kreisverkehr bzw. erste Wahl der Zeile mit confidence low; Alternative wäre „kein Soll-Typ“ - JC-03 auch an LSA-, Plateau- und eingefärbten Knoten im RSV/HAUPT-Netz und an jeder Radwegfurt mit Vorrang; JC-04 nur, wenn die Radroute die GOW quert (nicht längs); JC-05 an jeder geschützten LSA-Kreuzung
- Prompt 20: Die Entscheidungstabelle hat keine Zeile für eigenständige Radwege, die ETW30 queren (412 Knotenpunkte, `no_rule`), und keine für cycle_path(BASIS/ERSCHL)+GOW50 (J-09 nur RSV|HAUPT). Zeilen ergänzen (z. B. Radwegfurt mit Vorrang wie J-08)? – Verkehrsplaner*in
- Prompt 20: J-03 (GOW30+GOW30 → Kreisverkehr) hat keine DTV-Bedingung; 232 Knotenpunkte erhalten einen einstreifigen Kreisverkehr mit Zufluss über roundabout_max_dtv (Flag dtv_above_roundabout_max, z. B. Ludwig-Erhard-Straße/Rödingsmarkt 61 000 Kfz/24h). J-03 um die Bedingungen von J-01 ergänzen? Hängt mit der Frage zu GOW30 mit hoher Belastung zusammen (Prompt 19) – Verkehrsplaner*in
- Prompt 20: ETW_ERF hat keine eigene Zeile; über category_alias wie ETW30 behandelt. N6 sieht an ETW–ETW_ERF-Knoten Gehwegüberfahrten vor (rund 900 Netzknoten weichen ab). Eigene Zeilen J-xx für ETW_ERF (z. B. continuous_footway_exit)? – Verkehrsplaner*in
- Prompt 20: roundabout_single_lane_cycle_yield (Rad wartepflichtig) wird von keiner Zeile vergeben; laut JC-01 gilt der Vorrang innerorts. Für GOW80/ETW60 (außerorts, derzeit nicht in cat_final) vorsehen? – Verkehrsplaner*in
- Prompt 20: Ist-Typ: Ampeln im Umkreis 30 m (N6) treffen auch Nebenknoten neben einer LSA-Kreuzung (z. B. 1 159 Gehwegüberfahrten mit Ist „LSA“). Kleinerer Radius für Knotenpunkte ohne eigene Ampel? – GIS
- Prompt 20: Hamburg hat keine Straßenbahn; J-11 greift nicht. Stadtbahn-/U5-Planungen später als tram_present einspielen? – Team
- Prompt 20: 30 Knotenpunkte je Soll-Typ im Orthophoto prüfen (reports/junctions_review.csv, Spalten reviewer, assessment, comment) – Team
- Prompt 21: „Querschnitt passt?“ hängt vor allem an den Gehwegbreiten (`elements_min_m.sidewalk.standard` 3,00 m und `min` 2,50 m; ±20 % ändern die Passung auf bis zu 7,7 % der Länge) und an der Fahrbahn der Fahrradstraße (`cycle_street_carriageway` 4,00 m). Werte mit ReStra/RASt bestätigen – Verkehrsplaner*in
- Prompt 21: Zwei der 15 stärksten Zählstellen liegen nicht im Soll RSV/HAUPT (7297940 Altona: BASIS, 4 016 Rad/Werktag gezählt, 61 modelliert; 6283960 Eimsbüttel: ERSCHL, 3 763 gezählt, 326 modelliert). Lage der Zählstellen und Netz an diesen Stellen prüfen – Team
- Prompt 21: 30 Zufallsstichproben in reports/validation_cycling_review.csv (Spalten reviewer, assessment, comment) und die Prüflisten der Prompts 17 und 20 ausfüllen; erst dann gibt es eine Trefferquote der Regeln – Team
- Prompt 21: Externer Fachreview des Validierungsberichts (reports/validation_cycling.md, Abschnitt „Hinweise für den externen Fachreview“) organisieren – Team
- cycling_rules.yaml 0.6.0: Referenzdichte 4 400 Einwohner/km² (C-NET-07 density_scaling) an CBS-Zahlen für Delft prüfen; Brutto- (Delft) gegen Nettodichte (Masche ohne Ausschlussflächen) – Verkehrsplaner*in
- design_rules.yaml 0.5.0: ETW30-Mischfahrbahn 4,75 m (Begegnung Lkw/Pkw bei verminderter Geschwindigkeit) am Original RASt 06 Bild 17 prüfen – Verkehrsplaner*in
- Prompt 21: Veröffentlichung: site-data.tar.gz (jetzt rund 510 MB data/out, davon tiles/cycling.pmtiles 27 MB, tiles/junctions.pmtiles 3 MB, 16 285 Knoten-Steckbriefe) an das Release data-latest hängen und nach dem Deployment `web/scripts/check-range.sh` gegen die Seite laufen lassen – Team

## Lizenz

Abschnitte aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale (Tempo, Verkehrsmengen, ALKIS): Freie und Hansestadt Hamburg, dl-de/by-2.0 bzw. laut Quelle; Unfälle: © Statistische Ämter des Bundes und der Länder, Unfallatlas (nur Summen je Abschnitt). Orthophotos: LGV Hamburg, dl-de/by-2.0.
