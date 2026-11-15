# Klassifikationsbericht – Stufe 5

Erzeugt: 2026-11-15T20:07:56+00:00 von `pipeline/s05_classify.py`, rules.yaml 0.23.0. Nicht amtlicher Entwurf: Die Automatik schlägt vor, Menschen entscheiden (overrides/overrides.csv).

## Kennzahlen

- Klassifiziert: 34 702 Abschnitte im Arbeitsgebiet (4387.3 km), davon 33 712 in Hamburg (7 Bezirke) (4240.4 km). Abschnitte außerhalb des Arbeitsgebiets bleiben leer.
- Defaults aus C-MISS-01 genutzt: outside_builtup_area 100.0 %, override_school_street 100.0 % der Abschnitte im Arbeitsgebiet.
- Stillgelegt (C-MISS-01 status inactive, zählt nicht als abgedeckt): crossing_demand. Der zugehörige Teil der Bedingung greift nie.
- Globale Vorbehalte (C-CONF-01 global_caveats, gelten für alle Abschnitte gleich und senken confidence nicht): outside_builtup_area, override_school_street, crossing_demand, in_hvs, school_or_kita_access_m.

### km je Kategorie

| Kategorie | Bezeichnung | Hamburg (7 Bezirke) km | Anteil | Arbeitsgebiet km | Anteil | Abschnitte (Arbeitsgebiet) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| SW | Schnellverkehrsstraße | 185.7 | 4.4 % | 189.2 | 4.3 % | 470 |
| GOW50 | Stadtmagistrale | 341.5 | 8.1 % | 342.5 | 7.8 % | 3 278 |
| GOW30 | Stadtstraße 30 | 408.5 | 9.6 % | 408.5 | 9.3 % | 3 495 |
| ETW30 | Quartiersstraße | 3186.7 | 75.2 % | 3328.8 | 75.9 % | 25 682 |
| ETW_ERF | Aufenthaltsstraße | 118.0 | 2.8 % | 118.3 | 2.7 % | 1 777 |
| GOW80 | Landstraße (Verbindung) | 0.0 | 0.0 % | 0.0 | 0.0 % | 0 |
| ETW60 | Landstraße (Erschließung) | 0.0 | 0.0 % | 0.0 | 0.0 % | 0 |

### km-Anteile je Kategorie und Bezirk

| Bezirk | Abschnitte | km | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | GOW80 | ETW60 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 4 886 | 620.5 | 5 % | 6 % | 8 % | 79 % | 2 % | 0 % | 0 % |
| Bergedorf | 1 957 | 209.3 | 2 % | 8 % | 5 % | 75 % | 10 % | 0 % | 0 % |
| Eimsbüttel | 4 004 | 470.4 | 5 % | 9 % | 10 % | 74 % | 2 % | 0 % | 0 % |
| Hamburg-Mitte | 6 839 | 881.3 | 9 % | 10 % | 11 % | 67 % | 3 % | 0 % | 0 % |
| Hamburg-Nord | 5 136 | 563.3 | 2 % | 9 % | 12 % | 75 % | 2 % | 0 % | 0 % |
| Harburg | 3 348 | 465.2 | 8 % | 8 % | 8 % | 71 % | 4 % | 0 % | 0 % |
| Wandsbek | 7 542 | 1 030.4 | 0 % | 6 % | 9 % | 82 % | 2 % | 0 % | 0 % |
| **gesamt** | 33 712 | 4 240.4 | 4 % | 8 % | 10 % | 75 % | 3 % | 0 % | 0 % |

### confidence (Anteil der Länge im Arbeitsgebiet)

| Kategorie | hoch | mittel | niedrig |
| --- | ---: | ---: | ---: |
| SW | 100.0 % | 0.0 % | 0.0 % |
| GOW50 | 69.1 % | 14.2 % | 16.7 % |
| GOW30 | 78.5 % | 1.0 % | 20.5 % |
| ETW30 | 0.0 % | 95.1 % | 4.9 % |
| ETW_ERF | 100.0 % | 0.0 % | 0.0 % |
| alle | 19.7 % | 73.3 % | 6.9 % |

Häufigste Gründe für eine herabgesetzte confidence (Abschnitte, Mehrfachnennung):

| Grund | Abschnitte |
| --- | ---: |
| `fallback:conn_score` | 26 546 |
| `nahe_schwelle:conn_score~thresholds.conn_gow` | 2 367 |
| `fallback:width_p10_m` | 1 638 |
| `nahe_schwelle:width_p10_m~required_width.GOW50_bus` | 286 |
| `fehlt:width_p10_m` | 185 |
| `nahe_schwelle:shop_frontage_share~thresholds.frontage` | 91 |
| `nahe_schwelle:school_or_kita_access_m~thresholds.access_radius` | 77 |
| `nahe_schwelle:width_p10_m~required_width.GOW50` | 52 |

`fehlt:x` = Eingangswert fehlt und entscheidet; `nahe_schwelle:x~s` = Wert innerhalb ±10 % der Schwelle; `fallback:x` = Fallback-Quelle oder Default (C-CONF-01).

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| Goldene Fälle grün | ok | 32/32 |
| Jeder Abschnitt im Arbeitsgebiet hat eine Kategorie | ok | 34702 klassifiziert, 1824 außerhalb (leer) |
| rule_trace gefüllt | ok | JSON-Liste mit mindestens einer Regel |
| confidence gültig | ok | hoch, mittel, niedrig |

## Methode

- Kaskade `classification` aus rules.yaml, Reihenfolge = Priorität: C-SW-01 → C-RUR-01 → C-ERF-01 → C-GOW-01 (dann C-G30-01, C-G30-02, sonst C-G50-01) → C-ETW-01. Die Bedingungen werden von `pipeline/lib/expr.py` gelesen; Schwellen nur aus rules.yaml. Inaktive Regeln (status inactive: C-RUR-01) werden nicht geprüft, senken confidence nicht und stehen in `rule_trace` nur mit status inactive.
- **Fehlende Werte (C-MISS-01):** dreiwertige Logik; eine Regel greift nur bei sicher wahrer Bedingung. Defaults für Merkmale ohne Datenquelle: outside_builtup_area = False, override_school_street = False, crossing_demand = not_assessed.
- **confidence (C-CONF-01):** niedrig, wenn ein entscheidender Wert fehlt oder innerhalb ±10 % einer Schwelle liegt; mittel bei Fallback-Quellen (conn_score, width_p10_m) und Defaults; sonst hoch. Es zählen nur Werte, die das Ergebnis bestimmt haben. Defaults und Fallbacks, die für alle Abschnitte gleich gelten (global_caveats, F14), senken confidence nicht; sie stehen einmal oben unter Kennzahlen.
- `rule_trace` (JSON) enthält je geprüfter Regel id, passed, result (true/false/null), inputs, confidence und Gründe; `rule_path` die gegriffenen Regeln.
- HVS = `in_hvs` (DTV-Linien 2019, S-CONF-04). Bezirksstraße = keine HVS und keine Autobahn (motorway, motorway_link); Annahme für diesen Bericht.

## Kreuztabelle Soll × HVS – Hamburg (7 Bezirke) (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 21.8 | 163.9 | 0.0 | 185.7 | 3.2 % |
| GOW50 | 313.8 | 27.7 | 0.0 | 341.5 | 45.5 % |
| GOW30 | 353.8 | 54.7 | 0.0 | 408.5 | 51.3 % |
| ETW30 | 0.0 | 3186.7 | 0.0 | 3186.7 | 0.0 % |
| ETW_ERF | 0.6 | 117.4 | 0.0 | 118.0 | 0.1 % |
| **Summe** | 690.0 | 3550.4 | 0.0 | 4240.4 | |

## Kreuztabelle Soll × HVS – Arbeitsgebiet (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 21.8 | 167.4 | 0.0 | 189.2 | 3.2 % |
| GOW50 | 314.6 | 27.9 | 0.0 | 342.5 | 45.5 % |
| GOW30 | 353.8 | 54.7 | 0.0 | 408.5 | 51.2 % |
| ETW30 | 0.0 | 3328.8 | 0.0 | 3328.8 | 0.0 % |
| ETW_ERF | 0.6 | 117.6 | 0.0 | 118.3 | 0.1 % |
| **Summe** | 690.8 | 3696.5 | 0.0 | 4387.3 | |

### HVS-km je Bezirk (Arbeitsgebiet)

| Bezirk | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | GOW80 | ETW60 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 3.0 | 37.8 | 43.9 | 0.0 | 0.0 | 0.0 | 0.0 |
| Bergedorf | 0.0 | 15.0 | 9.9 | 0.0 | 0.0 | 0.0 | 0.0 |
| Eimsbüttel | 0.3 | 38.9 | 39.3 | 0.0 | 0.0 | 0.0 | 0.0 |
| Hamburg-Mitte | 9.8 | 86.3 | 84.5 | 0.0 | 0.2 | 0.0 | 0.0 |
| Hamburg-Nord | 8.6 | 43.9 | 60.7 | 0.0 | 0.4 | 0.0 | 0.0 |
| Harburg | 0.0 | 35.3 | 36.7 | 0.0 | 0.0 | 0.0 | 0.0 |
| Wandsbek | 0.0 | 56.5 | 78.8 | 0.0 | 0.0 | 0.0 | 0.0 |
| – | 0.0 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## HVS-Abschnitte, die ETW30 werden (0 Abschnitte, 0.0 km)

Einzeln begründen (guide.md Teil 7). Ursache ist in der Kaskade nur möglich, wenn `in_hvs` wahr ist und C-GOW-01 trotzdem nicht greift – das kommt nicht vor, solange in_hvs bekannt ist.

_keine_

Weitere HVS-Abschnitte außerhalb GOW50/GOW30: ETW_ERF 7 (0.6 km), SW 39 (21.8 km).

## Bezirksstraßen, die GOW50 werden (346 Abschnitte, 27.9 km)

Zusammengefasst nach Bezirk und Straßenname. Grund ist immer C-GOW-01 über conn_score ≥ 0.87 ohne GOW30-Auslöser; einzeln begründen (guide.md Teil 7). Einzelne Abschnitte stehen in `data/interim/classified.parquet`.

Befund: tertiary 205, primary 57, secondary 49, residential 11, service 7, trunk 6, trunk_link 3, secondary_link 3, tertiary_link 3, primary_link 2; Median-Länge 58 m. Kurze Stücke von Hauptstraßen deuten eher auf Lücken im HVS-Abgleich (S-CONF-04, nur match exact) als auf Bezirksstraßen hin – bei der Durchsicht prüfen.

Gezeigt: die 50 längsten von 142 Straßen (Bezirk + Name).

| Bezirk | Name | highway | Abschnitte | km | conn_score min–max | confidence niedrig | Beispiel |
| --- | --- | --- | ---: | ---: | --- | ---: | --- |
| Harburg | Neuwiedenthaler Straße | tertiary | 15 | 1.6 | 0.90–0.95 | 15 | `seg_1ab82a0ffe8b4393` |
| Hamburg-Nord | Tangstedter Landstraße | tertiary | 13 | 1.5 | 0.87–0.91 | 13 | `seg_02e7aa1a7d28177b` |
| Harburg | Marmstorfer Weg | tertiary | 11 | 1.3 | 0.88–0.89 | 11 | `seg_0514d706e3e5f47b` |
| Wandsbek | Schöneberger Straße | tertiary | 9 | 1.2 | 0.92–0.96 | 8 | `seg_226113150b698c28` |
| Hamburg-Nord | Maienweg | secondary, tertiary | 14 | 1.1 | 0.91–0.94 | 14 | `seg_067ed6ea6bbb90c0` |
| Bergedorf | Lohbrügger Landstraße | tertiary | 12 | 1.0 | 0.88–0.93 | 12 | `seg_0a85476ea769f8e5` |
| Altona | Kalckreuthweg | tertiary | 14 | 0.9 | 0.88–0.89 | 14 | `seg_3e7885199a36fff8` |
| Hamburg-Mitte | Billhorner Brückenstraße | primary, trunk | 14 | 0.9 | 0.87–0.93 | 14 | `seg_2ec04644e430a922` |
| Wandsbek | Berner Heerweg | tertiary | 7 | 0.9 | 0.90–0.91 | 7 | `seg_185fdb580b6dcd09` |
| Wandsbek | Charlottenburger Straße | tertiary | 8 | 0.8 | 0.95–0.95 | 8 | `seg_3534a0281c4818f0` |
| Wandsbek | Steilshooper Straße | tertiary | 8 | 0.8 | 0.89–0.90 | 8 | `seg_0c7f02931d88c899` |
| Hamburg-Nord | Weg beim Jäger | tertiary | 1 | 0.7 | 0.89–0.89 | 1 | `seg_6f7aae04e2c2a022` |
| Wandsbek | Pezolddamm | tertiary | 5 | 0.6 | 0.91–0.93 | 5 | `seg_30a3c24d7c5d96a8` |
| Hamburg-Mitte | Ausschläger Allee | tertiary | 3 | 0.5 | 0.91–0.92 | 3 | `seg_1f7981beee3fc490` |
| Wandsbek | Kielkoppelstraße | tertiary | 4 | 0.5 | 0.87–0.90 | 4 | `seg_49a3dea7f129878d` |
| Eimsbüttel | Edmund-Siemers-Allee | service | 3 | 0.5 | 0.98–0.98 | 0 | `seg_99c694e110e792d8` |
| Wandsbek | Berner Allee | tertiary | 4 | 0.5 | 0.88–0.89 | 4 | `seg_74b76fcc62362bbd` |
| Hamburg-Mitte | – | secondary_link, trunk_link | 3 | 0.5 | 0.87–0.89 | 3 | `seg_2372da720d69487d` |
| Hamburg-Nord | Steilshooper Straße | tertiary | 4 | 0.5 | 0.88–0.88 | 4 | `seg_2acf8a43762d198f` |
| Wandsbek | Ruscheweyhstraße | tertiary | 5 | 0.4 | 0.90–0.91 | 5 | `seg_0cb09ad647eafa58` |
| Eimsbüttel | Lohkampstraße | tertiary | 3 | 0.4 | 0.87–0.88 | 3 | `seg_2762e609df8d952c` |
| Wandsbek | Hummelsbütteler Weg | tertiary | 2 | 0.4 | 0.88–0.88 | 2 | `seg_3f3139d0fae15f82` |
| Bergedorf | Nettelnburger Landweg | secondary | 3 | 0.4 | 0.87–0.92 | 3 | `seg_46e7e42775169c44` |
| Hamburg-Mitte | Hermannstal | tertiary | 1 | 0.4 | 0.87–0.87 | 1 | `seg_dc42fad1b365750d` |
| Hamburg-Nord | Bebelallee | secondary, tertiary | 5 | 0.4 | 0.88–0.92 | 5 | `seg_06c7890a327eb8d1` |
| Hamburg-Mitte | Adenauerallee | secondary | 5 | 0.4 | 0.92–0.93 | 5 | `seg_2429620f019bcb2a` |
| Hamburg-Nord | Alsterdorfer Straße | tertiary | 2 | 0.3 | 0.89–0.89 | 2 | `seg_2a21e7aeee41bdaf` |
| Hamburg-Mitte | Möllner Landstraße | tertiary | 3 | 0.3 | 0.88–0.88 | 3 | `seg_9f1d40ee552964ef` |
| Wandsbek | Meiendorfer Mühlenweg | tertiary | 1 | 0.3 | 0.89–0.89 | 1 | `seg_9ab5e01a03cc7f47` |
| Hamburg-Nord | Meenkwiese | tertiary | 1 | 0.3 | 0.90–0.90 | 1 | `seg_4debe96f25eb0357` |
| Eimsbüttel | Mittelweg | tertiary | 4 | 0.3 | 0.87–0.87 | 4 | `seg_256d65caf205cfe3` |
| Hamburg-Mitte | Sievekingdamm | tertiary | 3 | 0.3 | 0.94–0.94 | 3 | `seg_29e91aea8d61d6a9` |
| Hamburg-Nord | Ohlsdorfer Straße | tertiary | 7 | 0.3 | 0.89–0.94 | 7 | `seg_00534af899d9745f` |
| Hamburg-Mitte | Veddeler Brückenstraße / Hovestieg | tertiary | 1 | 0.3 | 0.90–0.90 | 1 | `seg_2024efa5cd8010a0` |
| Harburg | Karnapp | residential | 2 | 0.3 | 0.92–0.92 | 2 | `seg_235b1e7d23ea74ec` |
| Hamburg-Mitte | Kandinskyallee | tertiary | 1 | 0.2 | 0.93–0.93 | 1 | `seg_62651b34e7cf00a0` |
| Harburg | Am Schwarzenberg-Campus | tertiary | 1 | 0.2 | 0.93–0.93 | 1 | `seg_bd1647670cc9bf7a` |
| – | Krohnstieg | trunk | 1 | 0.2 | 0.97–0.97 | 0 | `seg_e3a576cd7361f4e4` |
| Altona | Augustenburger Straße | tertiary | 1 | 0.2 | 0.93–0.93 | 1 | `seg_dec429e444c35324` |
| Hamburg-Mitte | Neßdeich | tertiary | 2 | 0.2 | 0.92–0.93 | 2 | `seg_7fda4452d37b8c74` |
| Hamburg-Mitte | Neßdeich / Finkenwerder Norderdeich | tertiary | 1 | 0.2 | 0.94–0.94 | 1 | `seg_cc01ce0bc74bcaf1` |
| Altona | Kaltenkirchener Straße | tertiary | 2 | 0.2 | 0.93–0.93 | 2 | `seg_6ae63ab99dc4e38d` |
| Altona | Franzosenkoppel | tertiary | 1 | 0.2 | 0.88–0.88 | 1 | `seg_b4c6d3bf46bec651` |
| Wandsbek | Saseler Damm | residential | 1 | 0.2 | 0.97–0.97 | 0 | `seg_dca9ee4f71ebce4a` |
| Wandsbek | August-Krogmann-Straße | secondary | 3 | 0.2 | 0.88–0.93 | 3 | `seg_040145ac3054ff0c` |
| Hamburg-Mitte | Ostfrieslandstraße | tertiary | 1 | 0.1 | 0.94–0.94 | 1 | `seg_2b263cc8f1c198d5` |
| Altona | Luruper Chaussee | secondary | 1 | 0.1 | 0.93–0.93 | 1 | `seg_8dcb6e7fd3863acf` |
| Hamburg-Mitte | Veddeler Brückenstraße | tertiary | 1 | 0.1 | 0.90–0.90 | 1 | `seg_c2da4f80c0b760fa` |
| Hamburg-Nord | Barcastraße | residential, tertiary | 3 | 0.1 | 0.92–0.93 | 3 | `seg_825bb84f32539221` |
| Wandsbek | Berner Chaussee | tertiary | 1 | 0.1 | 0.91–0.91 | 1 | `seg_ced052589340541b` |

## Stichprobe: bis zu 30 zufällige Abschnitte je Kategorie in Hamburg (7 Bezirke), nach Bezirk geschichtet (Seed 42)

Zur manuellen Durchsicht im Orthophoto (Geoportal Hamburg, DOP belaubt) und in Panoramax. Befund in `reports/classification_sample.csv` eintragen (Spalten cat_expected_manual, check_ok, comment).

**Durchsicht: offen.**

### SW (30 von 461)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_05a7bf220b7ad3fa` | Altona | – | motorway_link | 34 | HVS | 0.59 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560518,5937501]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582861/9.914132) | [Way](https://www.openstreetmap.org/way/7728240) |
| `seg_325e440917f1278c` | Altona | – | motorway | 1907 | keine HVS | 0.60 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560039,5936613]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.574939/9.906739) | [Way](https://www.openstreetmap.org/way/544370554) |
| `seg_7cc5b04626f82d44` | Altona | Sülldorfer Landstraße | trunk | 67 | HVS | 0.51 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[551436,5937115]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580366/9.776909) | [Way](https://www.openstreetmap.org/way/87332490) |
| `seg_85c73edbca417d8b` | Altona | – | motorway_link | 208 | keine HVS | 0.19 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559369,5934537]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556352/9.896224) | [Way](https://www.openstreetmap.org/way/10702956) |
| `seg_69014dc36e618efa` | Bergedorf | – | motorway_link | 209 | keine HVS | 0.56 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580198,5925909]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.476047/10.208379) | [Way](https://www.openstreetmap.org/way/154660626) |
| `seg_69d0025726b99d8a` | Bergedorf | – | motorway_link | 70 | keine HVS | 0.14 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580060,5925886]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.475867/10.206298) | [Way](https://www.openstreetmap.org/way/549828895) |
| `seg_18898a328316b431` | Eimsbüttel | – | motorway_link | 35 | keine HVS | 0.33 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560012,5941411]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.618067/9.907242) | [Way](https://www.openstreetmap.org/way/526877185) |
| `seg_1dcaac6278efae03` | Eimsbüttel | – | motorway_link | 145 | keine HVS | 0.58 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560193,5941346]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.617456/9.909974) | [Way](https://www.openstreetmap.org/way/37813970) |
| `seg_c9517409770da0de` | Eimsbüttel | – | motorway | 246 | keine HVS | 0.66 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561121,5943390]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.635722/9.924401) | [Way](https://www.openstreetmap.org/way/296326689) |
| `seg_dc0c91a089a9e1d1` | Eimsbüttel | – | motorway_link | 207 | keine HVS | 0.13 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559881,5941656]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620280/9.905321) | [Way](https://www.openstreetmap.org/way/10621047) |
| `seg_eb8ba2578753f64e` | Eimsbüttel | – | motorway | 653 | keine HVS | 0.66 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561276,5943811]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.639489/9.926834) | [Way](https://www.openstreetmap.org/way/850384023) |
| `seg_fa8172b9922d7535` | Eimsbüttel | – | motorway | 214 | keine HVS | 0.44 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561493,5944662]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.647107/9.930279) | [Way](https://www.openstreetmap.org/way/682144625) |
| `seg_07cb43beddcf7600` | Hamburg-Mitte | – | trunk | 570 | keine HVS | 0.87 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566743,5929014]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.505835/10.006336) | [Way](https://www.openstreetmap.org/way/733716414) |
| `seg_08cfbba6b302b4d7` | Hamburg-Mitte | – | motorway_link | 487 | keine HVS | 0.59 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568058,5926657]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.484482/10.025656) | [Way](https://www.openstreetmap.org/way/93762326) |
| `seg_0abd6821a7c3f28c` | Hamburg-Mitte | – | motorway_link | 11 | keine HVS | 0.77 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575842,5933532]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.545204/10.144603) | [Way](https://www.openstreetmap.org/way/316060718) |
| `seg_2245a9ca41da71ee` | Hamburg-Mitte | – | motorway | 824 | keine HVS | 0.66 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568536,5929746]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.512184/10.033532) | [Way](https://www.openstreetmap.org/way/45069890) |
| `seg_4f05da745142390c` | Hamburg-Mitte | – | motorway | 190 | keine HVS | 0.70 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561046,5930228]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.517438/9.920689) | [Way](https://www.openstreetmap.org/way/1567691200) |
| `seg_52e216c99dd55193` | Hamburg-Mitte | – | motorway_link | 65 | keine HVS | 0.48 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575001,5931577]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.527751/10.131449) | [Way](https://www.openstreetmap.org/way/10625741) |
| `seg_9e2e39ca5b19a8a1` | Hamburg-Mitte | – | motorway | 1463 | keine HVS | 0.88 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575315,5935905]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.566608/10.137214) | [Way](https://www.openstreetmap.org/way/316907870) |
| `seg_c04a7f4cc75ce047` | Hamburg-Mitte | – | motorway_link | 135 | keine HVS | 0.58 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560992,5930222]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.517390/9.919878) | [Way](https://www.openstreetmap.org/way/10594246) |
| `seg_cd6fc0c6adf7bcc2` | Hamburg-Mitte | – | motorway_link | 381 | keine HVS | 0.30 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568077,5926586]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.483842/10.025925) | [Way](https://www.openstreetmap.org/way/486882724) |
| `seg_dd263af2d32758b0` | Hamburg-Mitte | – | motorway | 634 | keine HVS | 0.66 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568910,5928843]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.504017/10.038967) | [Way](https://www.openstreetmap.org/way/4068560) |
| `seg_2aae0ac4ea792b30` | Hamburg-Nord | Zeppelinstraße | trunk | 470 | HVS | 0.54 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566760,5943283]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.634066/10.009651) | [Way](https://www.openstreetmap.org/way/659872942) |
| `seg_b40e03ccc0cd495e` | Hamburg-Nord | Zeppelinstraße | trunk | 127 | HVS | 0.87 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567005,5941837]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.621047/10.013043) | [Way](https://www.openstreetmap.org/way/463120830) |
| `seg_7bdd3af3e5469024` | Harburg | – | trunk | 390 | keine HVS | 0.37 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565329,5922898]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.451045/9.983746) | [Way](https://www.openstreetmap.org/way/25822442) |
| `seg_948857f2a6011244` | Harburg | – | motorway_link | 294 | keine HVS | 0.26 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560580,5926152]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.480857/9.912873) | [Way](https://www.openstreetmap.org/way/219200781) |
| `seg_d14a31b5d7a7321d` | Harburg | – | motorway_link | 20 | keine HVS | 0.40 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562120,5920626]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.431009/9.934986) | [Way](https://www.openstreetmap.org/way/206331860) |
| `seg_dc681d6fcc16da43` | Harburg | – | trunk | 396 | keine HVS | 0.38 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565688,5923035]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.452228/9.989189) | [Way](https://www.openstreetmap.org/way/26960825) |
| `seg_fc23ca32faaee987` | Harburg | – | motorway | 1133 | keine HVS | 0.60 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561550,5921169]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.435962/9.926513) | [Way](https://www.openstreetmap.org/way/25784075) |
| `seg_feea10141c96d56a` | Wandsbek | – | motorway_link | 68 | keine HVS | 0.58 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574313,5935968]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567315/10.122105) | [Way](https://www.openstreetmap.org/way/204393313) |

### GOW50 (30 von 3271)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_09ac747c6326f99e` | Altona | Max-Brauer-Allee | secondary | 135 | HVS | 0.79 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562578,5934611]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556648/9.944676) | [Way](https://www.openstreetmap.org/way/113941240) |
| `seg_286b7016ad302682` | Altona | Rugenbarg | primary | 26 | HVS | 0.95 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557905,5938016]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.587786/9.874775) | [Way](https://www.openstreetmap.org/way/1347144291) |
| `seg_d0e8fdea3694678e` | Altona | Rugenbarg | primary | 107 | HVS | 0.87 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557577,5937823]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.586090/9.869774) | [Way](https://www.openstreetmap.org/way/591215452) |
| `seg_fa78768193e60679` | Altona | Palmaille | secondary | 65 | HVS | 0.17 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561904,5933462]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.546400/9.934270) | [Way](https://www.openstreetmap.org/way/256266873) |
| `seg_6ad6d99de4c03402` | Bergedorf | Sander Damm | secondary | 115 | HVS | 0.78 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579753,5927451]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.489975/10.202064) | [Way](https://www.openstreetmap.org/way/40158185) |
| `seg_7710b58fb823c38a` | Bergedorf | Mohnhof | primary | 4 | HVS | 0.40 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580677,5927043]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.486172/10.215876) | [Way](https://www.openstreetmap.org/way/314123060) |
| `seg_20a614fcf9b07620` | Eimsbüttel | Klosterstern | secondary | 41 | HVS | 0.65 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565426,5937397]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.581338/9.988243) | [Way](https://www.openstreetmap.org/way/1370385196) |
| `seg_284913c9c5aee2b6` | Eimsbüttel | Beim Schlump | secondary | 17 | HVS | 0.69 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564256,5935839]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567481/9.970249) | [Way](https://www.openstreetmap.org/way/136784578) |
| `seg_3df2c22745a64ac1` | Eimsbüttel | Hallerstraße | secondary | 61 | HVS | 0.76 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564892,5936399]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572434/9.979964) | [Way](https://www.openstreetmap.org/way/1188140110) |
| `seg_eb7c910d595c5621` | Eimsbüttel | Garstedter Weg | secondary | 31 | HVS | 0.45 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564424,5944508]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645373/9.974582) | [Way](https://www.openstreetmap.org/way/136090927) |
| `seg_07eaeda58cab5a97` | Hamburg-Mitte | Veddeler Damm | primary | 38 | HVS | 0.28 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564916,5931429]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.527767/9.979304) | [Way](https://www.openstreetmap.org/way/378233717) |
| `seg_1b0379802420b5a4` | Hamburg-Mitte | Amsinckstraße | primary | 25 | HVS | 0.78 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567925,5933142]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.542786/10.025059) | [Way](https://www.openstreetmap.org/way/333890919) |
| `seg_82686f4c3c79a4be` | Hamburg-Mitte | Horner Rampe | primary | 51 | HVS | 0.73 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571882,5934045]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.550370/10.084974) | [Way](https://www.openstreetmap.org/way/22605323) |
| `seg_a5ea7d42d1edeb7a` | Hamburg-Mitte | Burgstraße | primary | 43 | HVS | 0.30 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568834,5934970]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.559092/10.039179) | [Way](https://www.openstreetmap.org/way/59410535) |
| `seg_b31753c0684c45b8` | Hamburg-Mitte | Köhlbrandbrücke | primary | 282 | HVS | 0.48 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564166,5930128]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.516162/9.967714) | [Way](https://www.openstreetmap.org/way/795923142) |
| `seg_ce1485c590635fd5` | Hamburg-Mitte | Stresemannstraße | primary | 20 | HVS | 0.78 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563836,5934797]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.558165/9.963704) | [Way](https://www.openstreetmap.org/way/1562914102) |
| `seg_e3aa4dc02f8ec1e3` | Hamburg-Mitte | Finkenwerder Straße | secondary | 67 | HVS | 0.74 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559004,5930237]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.517755/9.889903) | [Way](https://www.openstreetmap.org/way/407689645) |
| `seg_0d4bf7c042db2eec` | Hamburg-Nord | Brombeerweg | secondary | 113 | HVS | 0.69 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568464,5943294]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633946/10.035416) | [Way](https://www.openstreetmap.org/way/97080014) |
| `seg_29e4198521672911` | Hamburg-Nord | Krohnstieg | primary | 27 | HVS | 0.71 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566804,5944912]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.648702/10.010656) | [Way](https://www.openstreetmap.org/way/30651333) |
| `seg_62536f2f253fd8ee` | Hamburg-Nord | Tarpenbekstraße | primary | 80 | HVS | 0.91 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565116,5939149]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.597124/9.983926) | [Way](https://www.openstreetmap.org/way/44867404) |
| `seg_67eaa3ae8686f025` | Hamburg-Nord | Gehlengraben | primary | 147 | HVS | 0.88 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567426,5944985]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.649277/10.020083) | [Way](https://www.openstreetmap.org/way/250569943) |
| `seg_e6959c3169c30118` | Hamburg-Nord | Maria-Louisen-Straße | secondary | 155 | HVS | 0.67 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566252,5937919]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.585927/10.000822) | [Way](https://www.openstreetmap.org/way/52718467) |
| `seg_0d1c1ddfb7a62e32` | Harburg | Süderelbebogen | secondary | 236 | HVS | 0.37 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556940,5925513]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.475523/9.857923) | [Way](https://www.openstreetmap.org/way/547729017) |
| `seg_4e1b85158081c0ec` | Harburg | Seehafenbrücke | secondary | 17 | HVS | 0.66 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564896,5924313]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.463814/9.977521) | [Way](https://www.openstreetmap.org/way/597208328) |
| `seg_fd70e9fc640bb0dc` | Harburg | Bremer Straße | primary | 108 | HVS | 0.74 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562086,5921186]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.436052/9.934592) | [Way](https://www.openstreetmap.org/way/206331861) |
| `seg_5d63d6bb11036678` | Wandsbek | Kielkoppelstraße | tertiary | 65 | keine HVS | 0.90 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576999,5938508]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.589752/10.163291) | [Way](https://www.openstreetmap.org/way/641894386) |
| `seg_7492d65ee75e5a2e` | Wandsbek | Rahlstedter Bahnhofstraße | secondary | 192 | HVS | 0.45 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576294,5939582]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599506/10.152895) | [Way](https://www.openstreetmap.org/way/23750837) |
| `seg_b3e62fdd13a35842` | Wandsbek | Charlottenburger Straße | tertiary | 58 | keine HVS | 0.95 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575553,5937783]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.583450/10.141265) | [Way](https://www.openstreetmap.org/way/23241073) |
| `seg_bd15ea438802bf62` | Wandsbek | Poppenbütteler Weg | primary | 247 | HVS | 0.87 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571320,5945517]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.653544/10.079111) | [Way](https://www.openstreetmap.org/way/136218510) |
| `seg_f25856b9389cf14c` | Wandsbek | Rodigallee | secondary | 172 | HVS | 0.75 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572711,5936161]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.569272/10.097974) | [Way](https://www.openstreetmap.org/way/204178205) |

### GOW30 (30 von 3495)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_087480f5bf6b10a6` | Altona | Barnerstraße | secondary | 20 | HVS | 0.73 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561878,5934491]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.555651/9.934088) | [Way](https://www.openstreetmap.org/way/1321427973) |
| `seg_1bbf68e62eb1b746` | Altona | Holstenstraße | secondary | 65 | HVS | 0.81 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562982,5934501]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.555615/9.950751) | [Way](https://www.openstreetmap.org/way/782361019) |
| `seg_c62a1186a0181269` | Altona | Holstenplatz | secondary | 112 | HVS | 0.63 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562808,5935189]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.561814/9.948255) | [Way](https://www.openstreetmap.org/way/1071074525) |
| `seg_e22eb1fe413dcff1` | Altona | Holstenstraße | secondary | 163 | HVS | 0.68 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563312,5933985]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.550931/9.955621) | [Way](https://www.openstreetmap.org/way/609084547) |
| `seg_4b7a2c044d0fa7b9` | Bergedorf | Kurt-A.-Körber-Chaussee | secondary | 60 | keine HVS | 0.90 | niedrig | C-GOW-01 → C-G30-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578798,5927498]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.490542/10.187680) | [Way](https://www.openstreetmap.org/way/153758866) |
| `seg_54a388fb00ccf99e` | Bergedorf | Bergedorfer Straße | primary | 78 | HVS | 0.53 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579982,5927256]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.488187/10.205461) | [Way](https://www.openstreetmap.org/way/519988299) |
| `seg_214c08c080c0b67c` | Eimsbüttel | Kieler Straße | primary | 53 | HVS | 0.84 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561828,5937487]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582583/9.933923) | [Way](https://www.openstreetmap.org/way/145693836) |
| `seg_2c77cc12fc382716` | Eimsbüttel | An der Verbindungsbahn | primary | 191 | HVS | 0.85 | niedrig | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564944,5935478]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.564153/9.980560) | [Way](https://www.openstreetmap.org/way/1473481864) |
| `seg_44fea621a1234984` | Eimsbüttel | Hoheluftchaussee | primary | 12 | HVS | 0.80 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564594,5937117]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578929/9.975619) | [Way](https://www.openstreetmap.org/way/391821249) |
| `seg_d4f140d54c7dc177` | Eimsbüttel | Groß Borsteler Straße | residential | 86 | keine HVS | 0.87 | niedrig | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563633,5940564]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.610018/9.961815) | [Way](https://www.openstreetmap.org/way/146321662) |
| `seg_1bfcf1febbff82c3` | Hamburg-Mitte | Vorsetzen | secondary | 135 | HVS | 0.70 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564756,5933260]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.544247/9.977258) | [Way](https://www.openstreetmap.org/way/824230968) |
| `seg_8401dfaf56bc76b8` | Hamburg-Mitte | Willy-Brandt-Straße | primary | 85 | HVS | 0.93 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566094,5933653]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.547604/9.997531) | [Way](https://www.openstreetmap.org/way/458320761) |
| `seg_b0a0b92cd5b4e1d8` | Hamburg-Mitte | Reiherstieg-Hauptdeich | secondary | 70 | HVS | 0.08 | niedrig | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564785,5929566]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.511040/9.976934) | [Way](https://www.openstreetmap.org/way/5229525) |
| `seg_bbb8483a31e1e3da` | Hamburg-Mitte | Moorfleeter Straße | secondary | 200 | HVS | 0.62 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572696,5932157]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.533286/10.096811) | [Way](https://www.openstreetmap.org/way/670443231) |
| `seg_db10c387d6c647c6` | Hamburg-Mitte | Großmannstraße | secondary | 34 | HVS | 0.20 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569363,5932989]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.541215/10.046720) | [Way](https://www.openstreetmap.org/way/246042910) |
| `seg_f6fe3c5acbc591b9` | Hamburg-Mitte | Amsinckstraße | primary | 55 | HVS | 0.84 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566965,5933710]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.548010/10.010686) | [Way](https://www.openstreetmap.org/way/1114923262) |
| `seg_0a7951836e56e5f0` | Hamburg-Nord | Tangstedter Landstraße | tertiary | 231 | keine HVS | 0.90 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567330,5945284]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.651977/10.018707) | [Way](https://www.openstreetmap.org/way/195227475) |
| `seg_0bfe1b093584e4c7` | Hamburg-Nord | Weidestraße | tertiary | 101 | keine HVS | 0.88 | niedrig | C-GOW-01 → C-G30-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567765,5937390]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580983/10.023570) | [Way](https://www.openstreetmap.org/way/101507724) |
| `seg_20478bb242bcdc04` | Hamburg-Nord | Barmbeker Straße | primary | 89 | HVS | 0.79 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567175,5938306]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.589284/10.014850) | [Way](https://www.openstreetmap.org/way/176276490) |
| `seg_5268d2671e5a349a` | Hamburg-Nord | Barmbeker Straße | primary | 165 | HVS | 0.81 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566901,5938447]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.590587/10.010746) | [Way](https://www.openstreetmap.org/way/55693551) |
| `seg_5a0f3b71a8908d4f` | Hamburg-Nord | Eppendorfer Landstraße | tertiary | 15 | HVS | 0.66 | hoch | C-GOW-01 → C-G30-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565406,5938852]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.594420/9.988236) | [Way](https://www.openstreetmap.org/way/5210294) |
| `seg_0b583aef30cef6cb` | Harburg | Hohe Straße | primary | 206 | HVS | 0.55 | niedrig | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564791,5922959]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.451655/9.975658) | [Way](https://www.openstreetmap.org/way/152741721) |
| `seg_dc8e4ad9fd18daff` | Harburg | Eißendorfer Straße | secondary | 56 | HVS | 0.53 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564827,5923935]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.460424/9.976408) | [Way](https://www.openstreetmap.org/way/580124811) |
| `seg_f64e656a0ce74a9d` | Harburg | Hannoversche Straße | secondary | 54 | HVS | 0.52 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565993,5924520]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.465543/9.994086) | [Way](https://www.openstreetmap.org/way/601038982) |
| `seg_42eb68a6a6eca248` | Wandsbek | Harksheider Straße | secondary | 116 | HVS | 0.75 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571473,5946378]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.661263/10.081621) | [Way](https://www.openstreetmap.org/way/1426432260) |
| `seg_96b499db5c0b5979` | Wandsbek | Scharbeutzer Straße | secondary | 33 | HVS | 0.72 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574963,5939604]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599895/10.132791) | [Way](https://www.openstreetmap.org/way/296666825) |
| `seg_bdbf8870120a2851` | Wandsbek | Schloßstraße | secondary | 34 | HVS | 0.76 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570990,5936449]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572096/10.072045) | [Way](https://www.openstreetmap.org/way/1457576336) |
| `seg_e0966c26834b72b4` | Wandsbek | Rahlstedter Straße | secondary | 47 | HVS | 0.77 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576265,5939232]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.596363/10.152383) | [Way](https://www.openstreetmap.org/way/921823695) |
| `seg_f4ab5f437f7edd15` | Wandsbek | Rahlstedter Straße | secondary | 178 | HVS | 0.73 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576522,5939756]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.601040/10.156393) | [Way](https://www.openstreetmap.org/way/28759518) |
| `seg_fa4ba6bb99435180` | Wandsbek | Kielkoppelstraße | tertiary | 279 | keine HVS | 0.88 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577458,5938390]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.588627/10.170184) | [Way](https://www.openstreetmap.org/way/42411275) |

### ETW30 (30 von 24711)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_076219059b33c596` | Altona | Haubachstraße | residential | 123 | keine HVS | 0.29 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562084,5934560]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556248/9.937205) | [Way](https://www.openstreetmap.org/way/720558991) |
| `seg_203d795c2ee7f6f3` | Altona | Luckmoor | residential | 251 | keine HVS | 0.31 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557419,5938492]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592121/9.867510) | [Way](https://www.openstreetmap.org/way/128036470) |
| `seg_4a824683b1d7091e` | Altona | Kaistraße | tertiary | 137 | keine HVS | 0.74 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561807,5933364]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.545536/9.932787) | [Way](https://www.openstreetmap.org/way/143878207) |
| `seg_ac54c74d02f31c53` | Altona | Missundestraße | residential | 12 | keine HVS | 0.25 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563054,5935423]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.563890/9.952025) | [Way](https://www.openstreetmap.org/way/8295827) |
| `seg_c764379aedd18189` | Altona | Bugdahnstraße | residential | 182 | keine HVS | 0.15 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562221,5933971]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.550940/9.939158) | [Way](https://www.openstreetmap.org/way/143263690) |
| `seg_5ad66fd973b8d36d` | Bergedorf | Gojenbergsweg | residential | 92 | keine HVS | 0.65 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[582007,5926428]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.480439/10.235761) | [Way](https://www.openstreetmap.org/way/152467088) |
| `seg_612af155424c4005` | Bergedorf | Boberger Höhe | residential | 37 | keine HVS | 0.44 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577403,5930450]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.517282/10.167397) | [Way](https://www.openstreetmap.org/way/755430006) |
| `seg_24c89eeeeb5796be` | Eimsbüttel | Quadenstieg | residential | 104 | keine HVS | 0.15 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563917,5943150]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633226/9.966624) | [Way](https://www.openstreetmap.org/way/148170155) |
| `seg_31dbf0ca2744e59b` | Eimsbüttel | Harvestehuder Weg | tertiary | 12 | keine HVS | 0.23 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565767,5937240]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.579886/9.993351) | [Way](https://www.openstreetmap.org/way/802415578) |
| `seg_c6a029a3cb2ddeba` | Eimsbüttel | Willhoop | residential | 161 | keine HVS | 0.15 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563888,5940834]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.612420/9.965724) | [Way](https://www.openstreetmap.org/way/1212879657) |
| `seg_f570ecc55d89c2e9` | Eimsbüttel | Weidenallee | tertiary | 10 | keine HVS | 0.29 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563961,5935624]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565586/9.965758) | [Way](https://www.openstreetmap.org/way/919823381) |
| `seg_0d784cb73374d1d9` | Hamburg-Mitte | Bei der Stadtwassermühle | service | 144 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565692,5934217]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.552729/9.991594) | [Way](https://www.openstreetmap.org/way/1410384120) |
| `seg_0e0ff880d4c95595` | Hamburg-Mitte | Schlenzigstraße | tertiary | 15 | keine HVS | 0.03 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566280,5930585]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.520007/9.999696) | [Way](https://www.openstreetmap.org/way/1023910537) |
| `seg_256a83c2a1d64c1a` | Hamburg-Mitte | Sorbenstraße | unclassified | 298 | keine HVS | 0.04 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569220,5933957]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.549937/10.044781) | [Way](https://www.openstreetmap.org/way/1184522519) |
| `seg_2860e3ab83198a29` | Hamburg-Mitte | Altstädter Straße | residential | 9 | keine HVS | 0.27 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566480,5933847]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.549302/10.003398) | [Way](https://www.openstreetmap.org/way/1499593033) |
| `seg_bf50f94aeb0d3701` | Hamburg-Mitte | Glashüttenstraße | residential | 73 | keine HVS | 0.36 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564419,5934715]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.557363/9.972477) | [Way](https://www.openstreetmap.org/way/25554897) |
| `seg_3dca12b049950a6f` | Hamburg-Nord | Timmerloh | residential | 160 | keine HVS | 0.15 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567627,5946045]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.658778/10.023353) | [Way](https://www.openstreetmap.org/way/24301568) |
| `seg_424124cd737ebed2` | Hamburg-Nord | Flughafenstraße | unclassified | 66 | keine HVS | 0.33 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566576,5942872]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.630402/10.006778) | [Way](https://www.openstreetmap.org/way/320874036) |
| `seg_8c6c3d2a676e9f53` | Hamburg-Nord | Fuhlsbüttler Straße | secondary | 26 | keine HVS | 0.65 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569265,5938146]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.587578/10.046383) | [Way](https://www.openstreetmap.org/way/340061032) |
| `seg_a635170f886b475f` | Hamburg-Nord | Saarlandstraße | secondary | 8 | keine HVS | 0.54 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568132,5939537]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600228/10.029569) | [Way](https://www.openstreetmap.org/way/140430411) |
| `seg_0e70c4adb0041402` | Harburg | Westufer-Strasse | service | 106 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563603,5925813]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.477454/9.958349) | [Way](https://www.openstreetmap.org/way/123870504) |
| `seg_5737927e8ae06145` | Harburg | Kirchenhang | residential | 95 | keine HVS | 0.34 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563763,5923471]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.456386/9.960286) | [Way](https://www.openstreetmap.org/way/42942851) |
| `seg_f5829ccc175c3c0b` | Harburg | Heimfelder Straße | tertiary | 30 | keine HVS | 0.71 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563709,5924388]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.464634/9.959670) | [Way](https://www.openstreetmap.org/way/3235903) |
| `seg_4f2030cf7d7d990b` | Wandsbek | Berner Allee | tertiary | 32 | keine HVS | 0.07 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575424,5942873]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.629205/10.140551) | [Way](https://www.openstreetmap.org/way/543206907) |
| `seg_9833558e5b883e89` | Wandsbek | Seebekring | residential | 362 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570107,5939785]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.602198/10.059467) | [Way](https://www.openstreetmap.org/way/3449721) |
| `seg_a1be2de29d93c4cc` | Wandsbek | Höfenkamp | residential | 189 | keine HVS | 0.08 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573670,5944796]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.646736/10.114482) | [Way](https://www.openstreetmap.org/way/23345484) |
| `seg_c30f3abf7abd1f02` | Wandsbek | Kelterstraße | residential | 29 | keine HVS | 0.30 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571196,5943850]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.638585/10.076859) | [Way](https://www.openstreetmap.org/way/5155253) |
| `seg_e6b45ba5ccc2f47a` | Wandsbek | Distelkoppel | residential | 167 | keine HVS | 0.39 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568931,5943663]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.637201/10.042560) | [Way](https://www.openstreetmap.org/way/33104674) |
| `seg_f8fcdc7abcab6abe` | Wandsbek | Victoriaallee | tertiary | 11 | keine HVS | 0.06 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578955,5940760]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.609696/10.193397) | [Way](https://www.openstreetmap.org/way/1026843182) |
| `seg_fedf9b94cd188b4e` | Wandsbek | Hagenweg | unclassified | 1053 | keine HVS | 0.15 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578629,5942686]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.627054/10.188961) | [Way](https://www.openstreetmap.org/way/23011908) |

### ETW_ERF (30 von 1774)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_0a90dbbf0e28d531` | Altona | Zassenhausweg | living_street | 19 | keine HVS | 0.27 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554782,5936859]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.577720/9.827390) | [Way](https://www.openstreetmap.org/way/345751347) |
| `seg_32e52607b7a315a5` | Altona | Schmarjestraße | living_street | 9 | keine HVS | 0.24 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562146,5933755]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.549004/9.937986) | [Way](https://www.openstreetmap.org/way/33891763) |
| `seg_71606ad890d6bf5e` | Altona | Mariannenruh-Platz | pedestrian | 50 | keine HVS | 0.00 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562229,5935161]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.561637/9.939518) | [Way](https://www.openstreetmap.org/way/294929070) |
| `seg_20e26eafb62f9ecd` | Bergedorf | Sachsentor | pedestrian | 11 | keine HVS | 0.74 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580371,5927311]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.488619/10.211341) | [Way](https://www.openstreetmap.org/way/154189006) |
| `seg_2b47743e3b530940` | Bergedorf | Felix-Jud-Ring | living_street | 41 | keine HVS | 0.15 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576260,5926573]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.482607/10.149222) | [Way](https://www.openstreetmap.org/way/26130977) |
| `seg_4e1eb7115a28fc87` | Bergedorf | Fanny-Elßler-Bogen | living_street | 30 | keine HVS | 0.06 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578058,5925991]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.477109/10.176162) | [Way](https://www.openstreetmap.org/way/153805609) |
| `seg_545e5e6d34c1e562` | Bergedorf | Marta-Damkowski-Kehre | living_street | 86 | keine HVS | 0.15 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578106,5926594]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.482525/10.177026) | [Way](https://www.openstreetmap.org/way/153775299) |
| `seg_eec2df47d9c128f3` | Bergedorf | Elly-Heuss-Knapp-Ring | living_street | 64 | keine HVS | 0.15 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577423,5926276]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.479768/10.166668) | [Way](https://www.openstreetmap.org/way/25098094) |
| `seg_fde2817e5eeb82cf` | Bergedorf | – | pedestrian | 52 | keine HVS | 0.00 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576869,5927184]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.488007/10.158534) | [Way](https://www.openstreetmap.org/way/281414343) |
| `seg_31c797157a516623` | Eimsbüttel | Margaretha-Rothe-Weg | living_street | 94 | keine HVS | 0.15 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562654,5944351]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.644179/9.947779) | [Way](https://www.openstreetmap.org/way/8433886) |
| `seg_bc4d97869eb925d5` | Eimsbüttel | Tibarg | pedestrian | 20 | keine HVS | 0.00 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562944,5941731]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620593/9.951626) | [Way](https://www.openstreetmap.org/way/124212740) |
| `seg_ecec638b22bb3c55` | Eimsbüttel | Roman-Zeller-Platz | pedestrian | 13 | keine HVS | 0.00 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560083,5944664]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.647292/9.908953) | [Way](https://www.openstreetmap.org/way/650674161) |
| `seg_0a352bd6a099c14e` | Hamburg-Mitte | Brackhövel | residential | 27 | keine HVS | 0.15 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567439,5929639]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.511363/10.016975) | [Way](https://www.openstreetmap.org/way/674042166) |
| `seg_0a8e2e2fec8fac0a` | Hamburg-Mitte | Marseiller Promenade | pedestrian | 330 | keine HVS | 0.00 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565240,5935059]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.560351/9.984941) | [Way](https://www.openstreetmap.org/way/1212698253) |
| `seg_18d4299db55d76a3` | Hamburg-Mitte | Barkhof | pedestrian | 16 | keine HVS | 0.00 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566335,5934090]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.551507/10.001260) | [Way](https://www.openstreetmap.org/way/24408625) |
| `seg_40924f0e13f2163c` | Hamburg-Mitte | Bleicherstraße | living_street | 116 | keine HVS | 0.00 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563652,5934414]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.554753/9.960844) | [Way](https://www.openstreetmap.org/way/26609383) |
| `seg_445246126f1d2f56` | Hamburg-Mitte | Haferblöcken | residential | 536 | keine HVS | 0.00 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574817,5935235]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.560652/10.129535) | [Way](https://www.openstreetmap.org/way/24534015) |
| `seg_a5b538141740d972` | Hamburg-Mitte | Masurenweg | living_street | 129 | keine HVS | 0.04 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573509,5933469]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.544969/10.109386) | [Way](https://www.openstreetmap.org/way/25203583) |
| `seg_08c668c263ad1f49` | Hamburg-Nord | Götkensweg | residential | 72 | keine HVS | 0.15 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567958,5947508]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.671886/10.028688) | [Way](https://www.openstreetmap.org/way/86902037) |
| `seg_8b0ea278c64eebc8` | Hamburg-Nord | Erna-Stahl-Ring | living_street | 70 | keine HVS | 0.15 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569165,5942835]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.629731/10.045911) | [Way](https://www.openstreetmap.org/way/15693759) |
| `seg_5690c37f1120397d` | Harburg | Wieselstraße | living_street | 20 | keine HVS | 0.27 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558383,5926308]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.482510/9.879806) | [Way](https://www.openstreetmap.org/way/2975544) |
| `seg_64922b8ab04e1b56` | Harburg | Wilhelm-Busch-Weg | living_street | 229 | keine HVS | 0.33 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563894,5923705]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.458476/9.962317) | [Way](https://www.openstreetmap.org/way/628394521) |
| `seg_c5d4b7e8bb61f420` | Harburg | Groot Enn | pedestrian | 8 | keine HVS | 0.00 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556601,5925090]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.471754/9.852728) | [Way](https://www.openstreetmap.org/way/183797569) |
| `seg_f38743971805df5e` | Harburg | Baererstraße | living_street | 13 | keine HVS | 0.27 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565098,5923155]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.453384/9.980332) | [Way](https://www.openstreetmap.org/way/697815155) |
| `seg_fccdc9e87258e8d0` | Harburg | Distelfalterweg | living_street | 26 | keine HVS | 0.27 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553914,5924456]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.466338/9.812152) | [Way](https://www.openstreetmap.org/way/931567043) |
| `seg_025e6bcf85c67528` | Wandsbek | Roggengabel | living_street | 51 | keine HVS | 0.15 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573271,5950652]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.699424/10.109832) | [Way](https://www.openstreetmap.org/way/45275436) |
| `seg_428089fe0c2f1497` | Wandsbek | Grootmoorweg | living_street | 45 | keine HVS | 0.15 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572878,5943125]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.631838/10.102116) | [Way](https://www.openstreetmap.org/way/22822905) |
| `seg_749835014a743fe9` | Wandsbek | Herthastraße | pedestrian | 60 | keine HVS | 0.00 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571433,5940868]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.611752/10.079745) | [Way](https://www.openstreetmap.org/way/135453092) |
| `seg_b59587ff394a4e1b` | Wandsbek | Sedenkamp | living_street | 28 | keine HVS | 0.15 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572965,5952193]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.713315/10.105563) | [Way](https://www.openstreetmap.org/way/24370038) |
| `seg_c2b86be4ca53f373` | Wandsbek | Grootmoorgraben | living_street | 44 | keine HVS | 0.15 | hoch | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572259,5943175]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632372/10.092764) | [Way](https://www.openstreetmap.org/way/22822825) |

### GOW80

_keine Abschnitte_

### ETW60

_keine Abschnitte_

## Lizenz

Abschnitte und Merkmale aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale (Tempo, Verkehrsmengen, ALKIS): Freie und Hansestadt Hamburg, dl-de/by-2.0; Busfahrten: HVV, dl-de/by-2.0; Einwohner: Zensus 2022, dl-de/by-2.0. Orthophotos: LGV Hamburg, dl-de/by-2.0. Panoramax-Bilder: Lizenz je Bild.
