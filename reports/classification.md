# Klassifikationsbericht – Stufe 5

Erzeugt: 2026-11-15T21:35:17+00:00 von `pipeline/s05_classify.py`, rules.yaml 0.24.0. Nicht amtlicher Entwurf: Die Automatik schlägt vor, Menschen entscheiden (overrides/overrides.csv).

## Kennzahlen

- Klassifiziert: 34 702 Abschnitte im Arbeitsgebiet (4387.3 km), davon 33 712 in Hamburg (7 Bezirke) (4240.4 km). Abschnitte außerhalb des Arbeitsgebiets bleiben leer.
- Defaults aus C-MISS-01 genutzt: outside_builtup_area 100.0 %, override_school_street 100.0 % der Abschnitte im Arbeitsgebiet.
- Stillgelegt (C-MISS-01 status inactive, zählt nicht als abgedeckt): crossing_demand. Der zugehörige Teil der Bedingung greift nie.
- Globale Vorbehalte (C-CONF-01 global_caveats, gelten für alle Abschnitte gleich und senken confidence nicht): outside_builtup_area, override_school_street, crossing_demand, in_hvs, school_or_kita_access_m.

### km je Kategorie

| Kategorie | Bezeichnung | Hamburg (7 Bezirke) km | Anteil | Arbeitsgebiet km | Anteil | Abschnitte (Arbeitsgebiet) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| SW | Schnellverkehrsstraße | 185.7 | 4.4 % | 189.2 | 4.3 % | 470 |
| GOW50 | Stadtmagistrale | 618.0 | 14.6 % | 619.0 | 14.1 % | 5 757 |
| GOW30 | Stadtstraße 30 | 132.0 | 3.1 % | 132.0 | 3.0 % | 1 016 |
| ETW30 | Quartiersstraße | 3186.7 | 75.2 % | 3328.8 | 75.9 % | 25 682 |
| ETW_ERF | Aufenthaltsstraße | 118.0 | 2.8 % | 118.3 | 2.7 % | 1 777 |
| GOW80 | Landstraße (Verbindung) | 0.0 | 0.0 % | 0.0 | 0.0 % | 0 |
| ETW60 | Landstraße (Erschließung) | 0.0 | 0.0 % | 0.0 | 0.0 % | 0 |

### km-Anteile je Kategorie und Bezirk

| Bezirk | Abschnitte | km | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | GOW80 | ETW60 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 4 886 | 620.5 | 5 % | 12 % | 3 % | 79 % | 2 % | 0 % | 0 % |
| Bergedorf | 1 957 | 209.3 | 2 % | 12 % | 1 % | 75 % | 10 % | 0 % | 0 % |
| Eimsbüttel | 4 004 | 470.4 | 5 % | 16 % | 2 % | 74 % | 2 % | 0 % | 0 % |
| Hamburg-Mitte | 6 839 | 881.3 | 9 % | 18 % | 4 % | 67 % | 3 % | 0 % | 0 % |
| Hamburg-Nord | 5 136 | 563.3 | 2 % | 19 % | 2 % | 75 % | 2 % | 0 % | 0 % |
| Harburg | 3 348 | 465.2 | 8 % | 12 % | 5 % | 71 % | 4 % | 0 % | 0 % |
| Wandsbek | 7 542 | 1 030.4 | 0 % | 12 % | 3 % | 82 % | 2 % | 0 % | 0 % |
| **gesamt** | 33 712 | 4 240.4 | 4 % | 15 % | 3 % | 75 % | 3 % | 0 % | 0 % |

### confidence (Anteil der Länge im Arbeitsgebiet)

| Kategorie | hoch | mittel | niedrig |
| --- | ---: | ---: | ---: |
| SW | 100.0 % | 0.0 % | 0.0 % |
| GOW50 | 70.0 % | 12.6 % | 17.4 % |
| GOW30 | 43.7 % | 3.6 % | 52.7 % |
| ETW30 | 0.0 % | 95.1 % | 4.9 % |
| ETW_ERF | 100.0 % | 0.0 % | 0.0 % |
| alle | 18.2 % | 74.0 % | 7.8 % |

Häufigste Gründe für eine herabgesetzte confidence (Abschnitte, Mehrfachnennung):

| Grund | Abschnitte |
| --- | ---: |
| `fallback:conn_score` | 26 546 |
| `fallback:width_p10_m` | 2 544 |
| `nahe_schwelle:conn_score~thresholds.conn_gow` | 2 367 |
| `nahe_schwelle:width_p10_m~required_width.GOW50_bus_min` | 353 |
| `fehlt:width_p10_m` | 265 |
| `nahe_schwelle:dtv_official~thresholds.gow30_max_dtv` | 138 |
| `fehlt:dtv_official` | 112 |
| `nahe_schwelle:shop_frontage_share~thresholds.frontage` | 93 |
| `nahe_schwelle:school_or_kita_access_m~thresholds.access_radius` | 78 |
| `nahe_schwelle:width_p10_m~required_width.GOW50_min` | 74 |

`fehlt:x` = Eingangswert fehlt und entscheidet; `nahe_schwelle:x~s` = Wert innerhalb ±10 % der Schwelle; `fallback:x` = Fallback-Quelle oder Default (C-CONF-01).

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| Goldene Fälle grün | ok | 34/34 |
| Jeder Abschnitt im Arbeitsgebiet hat eine Kategorie | ok | 34702 klassifiziert, 1824 außerhalb (leer) |
| rule_trace gefüllt | ok | JSON-Liste mit mindestens einer Regel |
| confidence gültig | ok | hoch, mittel, niedrig |

## Methode

- Kaskade `classification` aus rules.yaml, Reihenfolge = Priorität: C-SW-01 → C-RUR-01 → C-ERF-01 → C-GOW-01 (dann C-G30-01, C-G30-02, C-G50-02, sonst C-G50-01) → C-ETW-01. Die Bedingungen werden von `pipeline/lib/expr.py` gelesen; Schwellen nur aus rules.yaml. Inaktive Regeln (status inactive: C-RUR-01) werden nicht geprüft, senken confidence nicht und stehen in `rule_trace` nur mit status inactive.
- **Fehlende Werte (C-MISS-01):** dreiwertige Logik; eine Regel greift nur bei sicher wahrer Bedingung. Defaults für Merkmale ohne Datenquelle: outside_builtup_area = False, override_school_street = False, crossing_demand = not_assessed.
- **confidence (C-CONF-01):** niedrig, wenn ein entscheidender Wert fehlt oder innerhalb ±10 % einer Schwelle liegt; mittel bei Fallback-Quellen (conn_score, width_p10_m) und Defaults; sonst hoch. Es zählen nur Werte, die das Ergebnis bestimmt haben. Defaults und Fallbacks, die für alle Abschnitte gleich gelten (global_caveats, F14), senken confidence nicht; sie stehen einmal oben unter Kennzahlen.
- `rule_trace` (JSON) enthält je geprüfter Regel id, passed, result (true/false/null), inputs, confidence und Gründe; `rule_path` die gegriffenen Regeln.
- HVS = `in_hvs` (DTV-Linien 2019, S-CONF-04). Bezirksstraße = keine HVS und keine Autobahn (motorway, motorway_link); Annahme für diesen Bericht.

## Kreuztabelle Soll × HVS – Hamburg (7 Bezirke) (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 21.8 | 163.9 | 0.0 | 185.7 | 3.2 % |
| GOW50 | 583.6 | 34.4 | 0.0 | 618.0 | 84.6 % |
| GOW30 | 84.0 | 48.0 | 0.0 | 132.0 | 12.2 % |
| ETW30 | 0.0 | 3186.7 | 0.0 | 3186.7 | 0.0 % |
| ETW_ERF | 0.6 | 117.4 | 0.0 | 118.0 | 0.1 % |
| **Summe** | 690.0 | 3550.4 | 0.0 | 4240.4 | |

## Kreuztabelle Soll × HVS – Arbeitsgebiet (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 21.8 | 167.4 | 0.0 | 189.2 | 3.2 % |
| GOW50 | 584.4 | 34.6 | 0.0 | 619.0 | 84.6 % |
| GOW30 | 84.0 | 48.0 | 0.0 | 132.0 | 12.2 % |
| ETW30 | 0.0 | 3328.8 | 0.0 | 3328.8 | 0.0 % |
| ETW_ERF | 0.6 | 117.6 | 0.0 | 118.3 | 0.1 % |
| **Summe** | 690.8 | 3696.5 | 0.0 | 4387.3 | |

### HVS-km je Bezirk (Arbeitsgebiet)

| Bezirk | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | GOW80 | ETW60 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 3.0 | 69.9 | 11.8 | 0.0 | 0.0 | 0.0 | 0.0 |
| Bergedorf | 0.0 | 22.8 | 2.1 | 0.0 | 0.0 | 0.0 | 0.0 |
| Eimsbüttel | 0.3 | 72.7 | 5.6 | 0.0 | 0.0 | 0.0 | 0.0 |
| Hamburg-Mitte | 9.8 | 149.2 | 21.5 | 0.0 | 0.2 | 0.0 | 0.0 |
| Hamburg-Nord | 8.6 | 101.0 | 3.6 | 0.0 | 0.4 | 0.0 | 0.0 |
| Harburg | 0.0 | 50.7 | 21.3 | 0.0 | 0.0 | 0.0 | 0.0 |
| Wandsbek | 0.0 | 117.3 | 18.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| – | 0.0 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## HVS-Abschnitte, die ETW30 werden (0 Abschnitte, 0.0 km)

Einzeln begründen (guide.md Teil 7). Ursache ist in der Kaskade nur möglich, wenn `in_hvs` wahr ist und C-GOW-01 trotzdem nicht greift – das kommt nicht vor, solange in_hvs bekannt ist.

_keine_

Weitere HVS-Abschnitte außerhalb GOW50/GOW30: ETW_ERF 7 (0.6 km), SW 39 (21.8 km).

## Bezirksstraßen, die GOW50 werden (398 Abschnitte, 34.6 km)

Zusammengefasst nach Bezirk und Straßenname. Grund ist immer C-GOW-01 über conn_score ≥ 0.87 ohne GOW30-Auslöser; einzeln begründen (guide.md Teil 7). Einzelne Abschnitte stehen in `data/interim/classified.parquet`.

Befund: tertiary 253, primary 57, secondary 51, residential 13, service 7, trunk 6, trunk_link 3, secondary_link 3, tertiary_link 3, primary_link 2; Median-Länge 62 m. Kurze Stücke von Hauptstraßen deuten eher auf Lücken im HVS-Abgleich (S-CONF-04, nur match exact) als auf Bezirksstraßen hin – bei der Durchsicht prüfen.

Gezeigt: die 50 längsten von 153 Straßen (Bezirk + Name).

| Bezirk | Name | highway | Abschnitte | km | conn_score min–max | confidence niedrig | Beispiel |
| --- | --- | --- | ---: | ---: | --- | ---: | --- |
| Harburg | Neuwiedenthaler Straße | tertiary | 19 | 2.0 | 0.90–0.95 | 19 | `seg_0760947bbe8fbb2c` |
| Hamburg-Mitte | Ausschläger Allee | tertiary | 8 | 1.7 | 0.91–0.92 | 8 | `seg_1f7981beee3fc490` |
| Hamburg-Nord | Tangstedter Landstraße | tertiary | 13 | 1.5 | 0.87–0.91 | 13 | `seg_02e7aa1a7d28177b` |
| Harburg | Marmstorfer Weg | tertiary | 12 | 1.5 | 0.88–0.89 | 12 | `seg_0514d706e3e5f47b` |
| Wandsbek | Schöneberger Straße | tertiary | 9 | 1.2 | 0.92–0.96 | 5 | `seg_226113150b698c28` |
| Bergedorf | Lohbrügger Landstraße | tertiary | 14 | 1.2 | 0.88–0.93 | 14 | `seg_0a85476ea769f8e5` |
| Hamburg-Nord | Maienweg | secondary, tertiary | 14 | 1.1 | 0.91–0.94 | 14 | `seg_067ed6ea6bbb90c0` |
| Wandsbek | Berner Heerweg | tertiary | 8 | 0.9 | 0.88–0.91 | 8 | `seg_185fdb580b6dcd09` |
| Altona | Kalckreuthweg | tertiary | 14 | 0.9 | 0.88–0.89 | 14 | `seg_3e7885199a36fff8` |
| Hamburg-Mitte | Billhorner Brückenstraße | primary, trunk | 14 | 0.9 | 0.87–0.93 | 14 | `seg_2ec04644e430a922` |
| Wandsbek | Pezolddamm | tertiary | 8 | 0.9 | 0.91–0.93 | 8 | `seg_30a3c24d7c5d96a8` |
| Wandsbek | Charlottenburger Straße | tertiary | 8 | 0.8 | 0.95–0.95 | 8 | `seg_3534a0281c4818f0` |
| Wandsbek | Steilshooper Straße | tertiary | 8 | 0.8 | 0.89–0.90 | 8 | `seg_0c7f02931d88c899` |
| Hamburg-Nord | Steilshooper Straße | tertiary | 8 | 0.7 | 0.88–0.88 | 8 | `seg_08ece6937e6d7ad7` |
| Wandsbek | Berner Allee | tertiary | 6 | 0.7 | 0.88–0.89 | 6 | `seg_09e17e6170276c08` |
| Hamburg-Nord | Weg beim Jäger | tertiary | 1 | 0.7 | 0.89–0.89 | 1 | `seg_6f7aae04e2c2a022` |
| Wandsbek | Berner Chaussee | tertiary | 3 | 0.6 | 0.91–0.91 | 3 | `seg_6de586cbaf6d264e` |
| Hamburg-Nord | Alsterdorfer Straße | tertiary | 3 | 0.6 | 0.89–0.89 | 3 | `seg_2a21e7aeee41bdaf` |
| Wandsbek | Kielkoppelstraße | tertiary | 4 | 0.5 | 0.87–0.90 | 4 | `seg_49a3dea7f129878d` |
| Eimsbüttel | Edmund-Siemers-Allee | service | 3 | 0.5 | 0.98–0.98 | 0 | `seg_99c694e110e792d8` |
| Hamburg-Mitte | – | secondary_link, trunk_link | 3 | 0.5 | 0.87–0.89 | 3 | `seg_2372da720d69487d` |
| Wandsbek | Eilbeker Weg | tertiary | 3 | 0.5 | 0.91–0.91 | 3 | `seg_a78ed16ed0928032` |
| Wandsbek | Ruscheweyhstraße | tertiary | 5 | 0.4 | 0.90–0.91 | 5 | `seg_0cb09ad647eafa58` |
| Eimsbüttel | Quickbornstraße | tertiary | 2 | 0.4 | 0.88–0.88 | 2 | `seg_61f70b135937ae03` |
| Wandsbek | Alter Zollweg | tertiary | 5 | 0.4 | 0.94–0.94 | 5 | `seg_531c97b51f58e4ae` |
| Eimsbüttel | Lohkampstraße | tertiary | 3 | 0.4 | 0.87–0.88 | 3 | `seg_2762e609df8d952c` |
| Wandsbek | Hummelsbütteler Weg | tertiary | 2 | 0.4 | 0.88–0.88 | 2 | `seg_3f3139d0fae15f82` |
| Bergedorf | Nettelnburger Landweg | secondary | 3 | 0.4 | 0.87–0.92 | 3 | `seg_46e7e42775169c44` |
| Hamburg-Mitte | Hermannstal | tertiary | 1 | 0.4 | 0.87–0.87 | 1 | `seg_dc42fad1b365750d` |
| Hamburg-Nord | Bebelallee | secondary, tertiary | 5 | 0.4 | 0.88–0.92 | 5 | `seg_06c7890a327eb8d1` |
| Bergedorf | Oberer Landweg | secondary | 4 | 0.4 | 0.90–0.92 | 4 | `seg_000299ecaf105205` |
| Hamburg-Mitte | Adenauerallee | secondary | 5 | 0.4 | 0.92–0.93 | 5 | `seg_2429620f019bcb2a` |
| Hamburg-Mitte | Möllner Landstraße | tertiary | 3 | 0.3 | 0.88–0.88 | 3 | `seg_9f1d40ee552964ef` |
| Wandsbek | Kupferdamm | tertiary | 2 | 0.3 | 0.90–0.90 | 2 | `seg_055f5e48ff2f5ce6` |
| Wandsbek | Meiendorfer Mühlenweg | tertiary | 1 | 0.3 | 0.89–0.89 | 1 | `seg_9ab5e01a03cc7f47` |
| Hamburg-Nord | Meenkwiese | tertiary | 1 | 0.3 | 0.90–0.90 | 1 | `seg_4debe96f25eb0357` |
| Wandsbek | Pezolddamm / Berner Allee | tertiary | 1 | 0.3 | 0.89–0.89 | 1 | `seg_f98cc9459a231ea9` |
| Eimsbüttel | Mittelweg | tertiary | 4 | 0.3 | 0.87–0.87 | 4 | `seg_256d65caf205cfe3` |
| Hamburg-Mitte | Sievekingdamm | tertiary | 3 | 0.3 | 0.94–0.94 | 3 | `seg_29e91aea8d61d6a9` |
| Hamburg-Nord | Ohlsdorfer Straße | tertiary | 7 | 0.3 | 0.89–0.94 | 7 | `seg_00534af899d9745f` |
| Hamburg-Mitte | Veddeler Brückenstraße / Hovestieg | tertiary | 1 | 0.3 | 0.90–0.90 | 1 | `seg_2024efa5cd8010a0` |
| Hamburg-Nord | Weidestraße | tertiary | 5 | 0.3 | 0.88–0.88 | 5 | `seg_568fb824d852e8f4` |
| Harburg | Karnapp | residential | 2 | 0.3 | 0.92–0.92 | 2 | `seg_235b1e7d23ea74ec` |
| Hamburg-Mitte | Kandinskyallee | tertiary | 1 | 0.2 | 0.93–0.93 | 1 | `seg_62651b34e7cf00a0` |
| Harburg | Am Schwarzenberg-Campus | tertiary | 1 | 0.2 | 0.93–0.93 | 1 | `seg_bd1647670cc9bf7a` |
| Altona | Bernadottestraße | residential | 2 | 0.2 | 0.92–0.92 | 2 | `seg_3277f740cddf88ca` |
| – | Krohnstieg | trunk | 1 | 0.2 | 0.97–0.97 | 0 | `seg_e3a576cd7361f4e4` |
| Altona | Augustenburger Straße | tertiary | 1 | 0.2 | 0.93–0.93 | 1 | `seg_dec429e444c35324` |
| Hamburg-Mitte | Neßdeich | tertiary | 2 | 0.2 | 0.92–0.93 | 2 | `seg_7fda4452d37b8c74` |
| Hamburg-Mitte | Neßdeich / Finkenwerder Norderdeich | tertiary | 1 | 0.2 | 0.94–0.94 | 1 | `seg_cc01ce0bc74bcaf1` |

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

### GOW50 (30 von 5750)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_0a44432b010a0a9f` | Altona | Max-Brauer-Allee | secondary | 32 | HVS | 0.55 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562901,5934855]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.558799/9.949600) | [Way](https://www.openstreetmap.org/way/31767945) |
| `seg_298880218eff6f57` | Altona | Lessingtunnel | secondary | 125 | HVS | 0.62 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561949,5934504]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.555765/9.935154) | [Way](https://www.openstreetmap.org/way/23103060) |
| `seg_6d0ec501552822d8` | Altona | Schnackenburgallee | secondary | 175 | HVS | 0.71 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560059,5937771]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.585346/9.907260) | [Way](https://www.openstreetmap.org/way/536693447) |
| `seg_f5710e5d56272427` | Altona | Bahrenfelder Chaussee | secondary | 5 | HVS | 0.80 | mittel | C-GOW-01 → C-G50-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560078,5935749]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567165/9.907160) | [Way](https://www.openstreetmap.org/way/1021656074) |
| `seg_47734e8faecd21eb` | Bergedorf | Bergedorfer Straße | primary | 51 | HVS | 0.93 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577917,5929637]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.509899/10.174937) | [Way](https://www.openstreetmap.org/way/818455481) |
| `seg_4cac78e561d81e0b` | Bergedorf | Bergedorfer Straße | primary | 36 | HVS | 0.56 | mittel | C-GOW-01 → C-G50-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579762,5927584]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.491169/10.202231) | [Way](https://www.openstreetmap.org/way/230396454) |
| `seg_248877d15484bb21` | Eimsbüttel | Grindelallee | primary | 453 | HVS | 0.76 | hoch | C-GOW-01 → C-G50-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565100,5935626]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565463/9.982949) | [Way](https://www.openstreetmap.org/way/24335863) |
| `seg_2df3de6b4d35f22e` | Eimsbüttel | Mittelweg | tertiary | 32 | keine HVS | 0.87 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565792,5937014]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.577855/9.993688) | [Way](https://www.openstreetmap.org/way/206426305) |
| `seg_e883a88bf7d1c4b6` | Eimsbüttel | Kollaustraße | primary | 439 | HVS | 0.96 | hoch | C-GOW-01 → C-G50-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562928,5941137]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.615254/9.951276) | [Way](https://www.openstreetmap.org/way/1561698174) |
| `seg_fb14f3574ca83a99` | Eimsbüttel | Pinneberger Chaussee | secondary | 59 | HVS | 0.74 | mittel | C-GOW-01 → C-G50-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559812,5940372]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.608749/9.904030) | [Way](https://www.openstreetmap.org/way/1364895242) |
| `seg_0bcdd90353a9524e` | Hamburg-Mitte | Kreuzweg | secondary | 173 | HVS | 0.69 | hoch | C-GOW-01 → C-G50-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567119,5934301]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.553299/10.013149) | [Way](https://www.openstreetmap.org/way/147936465) |
| `seg_0c513236546fd7f8` | Hamburg-Mitte | Bei der Wollkämmerei | secondary | 107 | HVS | 0.40 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565422,5928502]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.501401/9.986315) | [Way](https://www.openstreetmap.org/way/692333174) |
| `seg_2024efa5cd8010a0` | Hamburg-Mitte | Veddeler Brückenstraße / Hovestieg | tertiary | 267 | keine HVS | 0.90 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567805,5931230]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.525615/10.022826) | [Way](https://www.openstreetmap.org/way/5009103) |
| `seg_2290cbc2b2c83b70` | Hamburg-Mitte | Oberbaumbrücke | secondary | 167 | HVS | 0.72 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566518,5933538]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.546518/10.003909) | [Way](https://www.openstreetmap.org/way/152176404) |
| `seg_9d3197899d407123` | Hamburg-Mitte | Dovenfleet | secondary | 53 | HVS | 0.41 | hoch | C-GOW-01 → C-G50-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566275,5933613]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.547227/10.000261) | [Way](https://www.openstreetmap.org/way/23165589) |
| `seg_cc434e015ce2fdb8` | Hamburg-Mitte | Recha-Lübke-Damm | secondary | 105 | HVS | 0.74 | hoch | C-GOW-01 → C-G50-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567155,5933517]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.546252/10.013512) | [Way](https://www.openstreetmap.org/way/637815817) |
| `seg_dccdd10d1bf70729` | Hamburg-Mitte | Hammer Landstraße | secondary | 10 | HVS | 0.86 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568927,5934579]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.555564/10.040486) | [Way](https://www.openstreetmap.org/way/239778161) |
| `seg_0b3ab3b16f37a467` | Hamburg-Nord | Barmbeker Straße | primary | 168 | HVS | 0.92 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567287,5938173]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.588078/10.016514) | [Way](https://www.openstreetmap.org/way/145893937) |
| `seg_59a740cb2c32a341` | Hamburg-Nord | Sengelmannstraße | primary | 130 | HVS | 0.61 | hoch | C-GOW-01 → C-G50-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567522,5941002]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.613472/10.020674) | [Way](https://www.openstreetmap.org/way/608715857) |
| `seg_6208d7ad522dcb93` | Hamburg-Nord | Barmbeker Straße | primary | 8 | HVS | 0.81 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566820,5938477]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.590869/10.009525) | [Way](https://www.openstreetmap.org/way/972223517) |
| `seg_6954142febe167e0` | Hamburg-Nord | Lauensteinstraße | primary | 110 | HVS | 0.89 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568701,5939534]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600128/10.038166) | [Way](https://www.openstreetmap.org/way/186106626) |
| `seg_e8ac168c7e906fc1` | Hamburg-Nord | Lenhartzstraße | secondary | 40 | HVS | 0.74 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565054,5938275]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.589277/9.982810) | [Way](https://www.openstreetmap.org/way/40425005) |
| `seg_c114a4a2dd978588` | Harburg | Seehafenstraße | secondary | 306 | HVS | 0.43 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564902,5924552]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.465965/9.977669) | [Way](https://www.openstreetmap.org/way/27084154) |
| `seg_d01979d08051be4c` | Harburg | Cuxhavener Straße | primary | 84 | HVS | 0.74 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553588,5924490]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.466678/9.807238) | [Way](https://www.openstreetmap.org/way/534871383) |
| `seg_d4bdd58e1565bbce` | Harburg | Ehestorfer Heuweg | secondary | 100 | HVS | 0.62 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559014,5924640]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.467447/9.888993) | [Way](https://www.openstreetmap.org/way/1410340883) |
| `seg_02b86c408375803d` | Wandsbek | Harksheider Straße | secondary | 304 | HVS | 0.67 | hoch | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570232,5947362]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.670276/10.063072) | [Way](https://www.openstreetmap.org/way/150491921) |
| `seg_66403ed26e875ff9` | Wandsbek | Volksdorfer Damm | secondary | 13 | HVS | 0.63 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574972,5947427]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.670196/10.134816) | [Way](https://www.openstreetmap.org/way/549438039) |
| `seg_81f1fe058459b33e` | Wandsbek | Mühlenstraße | secondary | 5 | HVS | 0.81 | mittel | C-GOW-01 → C-G50-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570082,5936832]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575661/10.058427) | [Way](https://www.openstreetmap.org/way/1570353902) |
| `seg_c31bb5f16c40366e` | Wandsbek | Rahlstedter Straße | secondary | 25 | HVS | 0.76 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577170,5940293]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.605769/10.166314) | [Way](https://www.openstreetmap.org/way/35917423) |
| `seg_d3095872fd3c2b38` | Wandsbek | Bramfelder Chaussee | primary | 43 | HVS | 0.77 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571782,5942584]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.627123/10.085425) | [Way](https://www.openstreetmap.org/way/1099838116) |

### GOW30 (30 von 1016)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_09e9dafaf5f6c59e` | Altona | Walderseestraße | secondary | 179 | HVS | 0.67 | hoch | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559061,5934631]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.557237/9.891591) | [Way](https://www.openstreetmap.org/way/30647242) |
| `seg_2ae64f223e5920e0` | Altona | – | secondary | 18 | HVS | 0.63 | hoch | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559018,5936437]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573469/9.891288) | [Way](https://www.openstreetmap.org/way/692404087) |
| `seg_6afaf944098ed2e0` | Altona | – | secondary_link | 42 | keine HVS | 0.90 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554545,5934966]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.560731/9.823488) | [Way](https://www.openstreetmap.org/way/571458737) |
| `seg_78f10dcab01bde3f` | Altona | Kalckreuthweg | tertiary | 44 | keine HVS | 0.89 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559293,5935578]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565721/9.895264) | [Way](https://www.openstreetmap.org/way/885603172) |
| `seg_45f16bed592b0d36` | Bergedorf | Korachstraße | residential | 18 | keine HVS | 0.89 | niedrig | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579325,5929888]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.511937/10.196231) | [Way](https://www.openstreetmap.org/way/18255066) |
| `seg_2397041f834dc48d` | Eimsbüttel | Märkerweg | tertiary | 95 | keine HVS | 0.87 | niedrig | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563299,5944499]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645427/9.957554) | [Way](https://www.openstreetmap.org/way/359743701) |
| `seg_2c7b526267eb8794` | Eimsbüttel | Frohmestraße | secondary_link | 71 | keine HVS | 0.90 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561561,5942652]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.629037/9.930915) | [Way](https://www.openstreetmap.org/way/30436527) |
| `seg_e79feb96eb7427cc` | Eimsbüttel | Garstedter Weg | secondary | 43 | HVS | 0.67 | mittel | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564154,5943884]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.639796/9.970360) | [Way](https://www.openstreetmap.org/way/911734456) |
| `seg_14f6d853cfe10653` | Hamburg-Mitte | Grandeswerder Straße | residential | 32 | keine HVS | 0.88 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566742,5932863]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.540426/10.007140) | [Way](https://www.openstreetmap.org/way/307541272) |
| `seg_5f19c2463174f45d` | Hamburg-Mitte | Georg-Wilhelm-Straße | secondary | 231 | HVS | 0.34 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565739,5928044]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.497241/9.991005) | [Way](https://www.openstreetmap.org/way/934924994) |
| `seg_805bc33b9d074353` | Hamburg-Mitte | Steintorwall | secondary | 16 | keine HVS | 0.99 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566657,5933959]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.550290/10.006094) | [Way](https://www.openstreetmap.org/way/188376942) |
| `seg_8eb19ba709f07b73` | Hamburg-Mitte | Zweibrückenstraße | secondary_link | 97 | HVS | 0.59 | mittel | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568076,5932147]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.533820/10.027111) | [Way](https://www.openstreetmap.org/way/829829779) |
| `seg_a4e1097c48b32af8` | Hamburg-Mitte | Sievekingdamm | tertiary | 27 | keine HVS | 0.95 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569337,5934892]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.558327/10.046748) | [Way](https://www.openstreetmap.org/way/940921900) |
| `seg_b1303be8355a0682` | Hamburg-Mitte | Hohe-Schaar-Straße | secondary | 34 | HVS | 0.63 | mittel | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565049,5926206]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.480810/9.980215) | [Way](https://www.openstreetmap.org/way/408046758) |
| `seg_dfe8b90d6e42340f` | Hamburg-Mitte | Davidstraße | residential | 38 | keine HVS | 0.88 | niedrig | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563991,5933495]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.546449/9.965770) | [Way](https://www.openstreetmap.org/way/299265209) |
| `seg_0a7951836e56e5f0` | Hamburg-Nord | Tangstedter Landstraße | tertiary | 231 | keine HVS | 0.90 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567330,5945284]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.651977/10.018707) | [Way](https://www.openstreetmap.org/way/195227475) |
| `seg_0bfe1b093584e4c7` | Hamburg-Nord | Weidestraße | tertiary | 101 | keine HVS | 0.88 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567765,5937390]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580983/10.023570) | [Way](https://www.openstreetmap.org/way/101507724) |
| `seg_286d325c6eb453b4` | Hamburg-Nord | Fuhlsbüttler Straße | secondary | 64 | HVS | 0.67 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569284,5937997]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.586233/10.046633) | [Way](https://www.openstreetmap.org/way/90060916) |
| `seg_47b5000b2b845e95` | Hamburg-Nord | Steilshooper Straße | tertiary | 230 | keine HVS | 0.88 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569534,5939571]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600347/10.050757) | [Way](https://www.openstreetmap.org/way/1567790348) |
| `seg_0a4cc67aaf856ce9` | Harburg | Schloßmühlendamm | secondary | 48 | HVS | 0.53 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565170,5924180]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.462590/9.981618) | [Way](https://www.openstreetmap.org/way/580230397) |
| `seg_5ce21acd3fd8c1da` | Harburg | Hannoversche Straße | secondary | 266 | HVS | 0.51 | niedrig | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565986,5924850]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.468505/9.994059) | [Way](https://www.openstreetmap.org/way/385295529) |
| `seg_cb012a70e37ebc62` | Harburg | Neuwiedenthaler Straße | tertiary | 223 | keine HVS | 0.90 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557399,5925664]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.476824/9.864859) | [Way](https://www.openstreetmap.org/way/549753043) |
| `seg_e0ed0d30b5a7c51c` | Harburg | Ehestorfer Heuweg | secondary | 48 | HVS | 0.02 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558983,5925120]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.471760/9.888618) | [Way](https://www.openstreetmap.org/way/2567790) |
| `seg_f835afa6e1e7b19d` | Harburg | Friedhofstraße | tertiary | 79 | HVS | 0.31 | hoch | C-GOW-01 → C-G30-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563548,5922366]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.446483/9.956828) | [Way](https://www.openstreetmap.org/way/783336839) |
| `seg_350b0aae19d935a1` | Wandsbek | Beim Farenland | tertiary | 109 | keine HVS | 0.90 | niedrig | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575204,5943269]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632797/10.137318) | [Way](https://www.openstreetmap.org/way/7918418) |
| `seg_771680f35f4b96ae` | Wandsbek | Hummelsbütteler Weg | tertiary | 95 | keine HVS | 0.88 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569521,5944505]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.644691/10.051674) | [Way](https://www.openstreetmap.org/way/27220694) |
| `seg_9924e406ab794ee1` | Wandsbek | Karlshöher Weg | tertiary | 107 | keine HVS | 0.90 | niedrig | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575387,5942955]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.629952/10.140018) | [Way](https://www.openstreetmap.org/way/32921081) |
| `seg_b1793c5a2d0e88f4` | Wandsbek | Waldweg | secondary | 253 | HVS | 0.68 | hoch | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574878,5945825]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.655818/10.133007) | [Way](https://www.openstreetmap.org/way/1543096176) |
| `seg_c0edcb2934525ef0` | Wandsbek | Bergstedter Chaussee | primary | 204 | HVS | 0.68 | niedrig | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574719,5947741]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.673057/10.131063) | [Way](https://www.openstreetmap.org/way/42365349) |
| `seg_c3792228268f03e1` | Wandsbek | Segeberger Chaussee | primary | 226 | HVS | 0.52 | niedrig | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571155,5952309]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.714609/10.078167) | [Way](https://www.openstreetmap.org/way/526161039) |

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
