# Klassifikationsbericht – Stufe 5

Erzeugt: 2026-11-07T15:03:15+00:00 von `pipeline/s05_classify.py`, rules.yaml 0.16.0. Nicht amtlicher Entwurf: Die Automatik schlägt vor, Menschen entscheiden (overrides/overrides.csv).

## Kennzahlen

- Klassifiziert: 34 702 Abschnitte im Arbeitsgebiet (4387.3 km), davon 33 712 in Hamburg (7 Bezirke) (4240.4 km). Abschnitte außerhalb des Arbeitsgebiets bleiben leer.
- Defaults aus C-MISS-01 genutzt: crossing_demand 100.0 %, outside_builtup_area 100.0 %, override_school_street 100.0 % der Abschnitte im Arbeitsgebiet.

### km je Kategorie

| Kategorie | Bezeichnung | Hamburg (7 Bezirke) km | Anteil | Arbeitsgebiet km | Anteil | Abschnitte (Arbeitsgebiet) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| SW | Schnellverkehrsstraße | 185.7 | 4.4 % | 189.2 | 4.3 % | 470 |
| GOW50 | Stadtmagistrale | 271.3 | 6.4 % | 272.3 | 6.2 % | 2 474 |
| GOW30 | Stadtstraße 30 | 474.1 | 11.2 % | 474.1 | 10.8 % | 4 237 |
| ETW30 | Quartiersstraße | 3191.3 | 75.3 % | 3333.4 | 76.0 % | 25 744 |
| ETW_ERF | Aufenthaltsstraße | 118.0 | 2.8 % | 118.3 | 2.7 % | 1 777 |
| GOW80 | Landstraße (Verbindung) | 0.0 | 0.0 % | 0.0 | 0.0 % | 0 |
| ETW60 | Landstraße (Erschließung) | 0.0 | 0.0 % | 0.0 | 0.0 % | 0 |

### km-Anteile je Kategorie und Bezirk

| Bezirk | Abschnitte | km | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | GOW80 | ETW60 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 4 886 | 620.5 | 5 % | 4 % | 10 % | 79 % | 2 % | 0 % | 0 % |
| Bergedorf | 1 957 | 209.3 | 2 % | 7 % | 6 % | 75 % | 10 % | 0 % | 0 % |
| Eimsbüttel | 4 004 | 470.4 | 5 % | 7 % | 11 % | 75 % | 2 % | 0 % | 0 % |
| Hamburg-Mitte | 6 839 | 881.3 | 9 % | 10 % | 12 % | 67 % | 3 % | 0 % | 0 % |
| Hamburg-Nord | 5 136 | 563.3 | 2 % | 5 % | 16 % | 75 % | 2 % | 0 % | 0 % |
| Harburg | 3 348 | 465.2 | 8 % | 7 % | 9 % | 71 % | 4 % | 0 % | 0 % |
| Wandsbek | 7 542 | 1 030.4 | 0 % | 5 % | 11 % | 82 % | 2 % | 0 % | 0 % |
| **gesamt** | 33 712 | 4 240.4 | 4 % | 6 % | 11 % | 75 % | 3 % | 0 % | 0 % |

### confidence (Anteil der Länge im Arbeitsgebiet)

| Kategorie | hoch | mittel | niedrig |
| --- | ---: | ---: | ---: |
| SW | 100.0 % | 0.0 % | 0.0 % |
| GOW50 | 0.0 % | 82.2 % | 17.8 % |
| GOW30 | 0.0 % | 84.9 % | 15.1 % |
| ETW30 | 0.0 % | 95.3 % | 4.7 % |
| ETW_ERF | 0.0 % | 100.0 % | 0.0 % |
| alle | 4.3 % | 89.3 % | 6.3 % |

Häufigste Gründe für eine herabgesetzte confidence (Abschnitte, Mehrfachnennung):

| Grund | Abschnitte |
| --- | ---: |
| `fallback:outside_builtup_area` | 34 232 |
| `fallback:override_school_street` | 32 455 |
| `fallback:in_hvs` | 27 032 |
| `fallback:conn_score` | 26 773 |
| `fallback:schools_or_kitas_within_m` | 4 143 |
| `fallback:crossing_demand` | 2 474 |
| `nahe_schwelle:conn_score~thresholds.conn_gow` | 2 288 |
| `nahe_schwelle:schools_or_kitas_within_m~thresholds.sensitive_radius` | 364 |
| `fallback:width_p10_m` | 332 |
| `nahe_schwelle:width_p10_m~required_width.GOW50` | 69 |
| `fehlt:width_p10_m` | 56 |
| `nahe_schwelle:shop_frontage_share~thresholds.frontage` | 49 |

`fehlt:x` = Eingangswert fehlt und entscheidet; `nahe_schwelle:x~s` = Wert innerhalb ±10 % der Schwelle; `fallback:x` = Fallback-Quelle oder Default (C-CONF-01).

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| Goldene Fälle grün | ok | 29/29 |
| Jeder Abschnitt im Arbeitsgebiet hat eine Kategorie | ok | 34702 klassifiziert, 1824 außerhalb (leer) |
| rule_trace gefüllt | ok | JSON-Liste mit mindestens einer Regel |
| confidence gültig | ok | hoch, mittel, niedrig |

## Methode

- Kaskade `classification` aus rules.yaml, Reihenfolge = Priorität: C-SW-01 → C-RUR-01 → C-ERF-01 → C-GOW-01 (dann C-G30-01, C-G30-02, sonst C-G50-01) → C-ETW-01. Die Bedingungen werden von `pipeline/lib/expr.py` gelesen; Schwellen nur aus rules.yaml.
- **Fehlende Werte (C-MISS-01):** dreiwertige Logik; eine Regel greift nur bei sicher wahrer Bedingung. Defaults für Merkmale ohne Datenquelle: outside_builtup_area = False, override_school_street = False, crossing_demand = not_assessed.
- **confidence (C-CONF-01):** niedrig, wenn ein entscheidender Wert fehlt oder innerhalb ±10 % einer Schwelle liegt; mittel bei Fallback-Quellen (schools_or_kitas_within_m, in_hvs, conn_score, width_p10_m) und Defaults; sonst hoch. Es zählen nur Werte, die das Ergebnis bestimmt haben.
- `rule_trace` (JSON) enthält je geprüfter Regel id, passed, result (true/false/null), inputs, confidence und Gründe; `rule_path` die gegriffenen Regeln.
- HVS = `in_hvs` (DTV-Linien 2019, S-CONF-04). Bezirksstraße = keine HVS und keine Autobahn (motorway, motorway_link); Annahme für diesen Bericht.

## Kreuztabelle Soll × HVS – Hamburg (7 Bezirke) (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 21.8 | 163.9 | 0.0 | 185.7 | 3.2 % |
| GOW50 | 245.9 | 25.3 | 0.0 | 271.3 | 35.6 % |
| GOW30 | 421.6 | 52.5 | 0.0 | 474.1 | 61.1 % |
| ETW30 | 0.0 | 3191.3 | 0.0 | 3191.3 | 0.0 % |
| ETW_ERF | 0.6 | 117.4 | 0.0 | 118.0 | 0.1 % |
| **Summe** | 690.0 | 3550.4 | 0.0 | 4240.4 | |

## Kreuztabelle Soll × HVS – Arbeitsgebiet (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 21.8 | 167.4 | 0.0 | 189.2 | 3.2 % |
| GOW50 | 246.8 | 25.5 | 0.0 | 272.3 | 35.7 % |
| GOW30 | 421.6 | 52.5 | 0.0 | 474.1 | 61.0 % |
| ETW30 | 0.0 | 3333.4 | 0.0 | 3333.4 | 0.0 % |
| ETW_ERF | 0.6 | 117.6 | 0.0 | 118.3 | 0.1 % |
| **Summe** | 690.8 | 3696.5 | 0.0 | 4387.3 | |

### HVS-km je Bezirk (Arbeitsgebiet)

| Bezirk | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | GOW80 | ETW60 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 3.0 | 23.8 | 57.9 | 0.0 | 0.0 | 0.0 | 0.0 |
| Bergedorf | 0.0 | 13.2 | 11.7 | 0.0 | 0.0 | 0.0 | 0.0 |
| Eimsbüttel | 0.3 | 30.8 | 47.5 | 0.0 | 0.0 | 0.0 | 0.0 |
| Hamburg-Mitte | 9.8 | 80.1 | 90.6 | 0.0 | 0.2 | 0.0 | 0.0 |
| Hamburg-Nord | 8.6 | 25.2 | 79.4 | 0.0 | 0.4 | 0.0 | 0.0 |
| Harburg | 0.0 | 32.0 | 40.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Wandsbek | 0.0 | 40.8 | 94.5 | 0.0 | 0.0 | 0.0 | 0.0 |
| – | 0.0 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## HVS-Abschnitte, die ETW30 werden (0 Abschnitte, 0.0 km)

Einzeln begründen (guide.md Teil 7). Ursache ist in der Kaskade nur möglich, wenn `in_hvs` wahr ist und C-GOW-01 trotzdem nicht greift – das kommt nicht vor, solange in_hvs bekannt ist.

_keine_

Weitere HVS-Abschnitte außerhalb GOW50/GOW30: ETW_ERF 7 (0.6 km), SW 39 (21.8 km).

## Bezirksstraßen, die GOW50 werden (287 Abschnitte, 25.5 km)

Zusammengefasst nach Bezirk und Straßenname. Grund ist immer C-GOW-01 über conn_score ≥ 0.6 ohne GOW30-Auslöser; einzeln begründen (guide.md Teil 7). Einzelne Abschnitte stehen in `data/interim/classified.parquet`.

Befund: tertiary 180, primary 40, secondary 36, residential 11, trunk 6, secondary_link 4, service 4, trunk_link 2, tertiary_link 2, unclassified 1, primary_link 1; Median-Länge 62 m. Kurze Stücke von Hauptstraßen deuten eher auf Lücken im HVS-Abgleich (S-CONF-04, nur match exact) als auf Bezirksstraßen hin – bei der Durchsicht prüfen.

Gezeigt: die 50 längsten von 123 Straßen (Bezirk + Name).

| Bezirk | Name | highway | Abschnitte | km | conn_score min–max | confidence niedrig | Beispiel |
| --- | --- | --- | ---: | ---: | --- | ---: | --- |
| Hamburg-Mitte | Ausschläger Allee | tertiary | 6 | 1.5 | 0.63–0.63 | 6 | `seg_1f7981beee3fc490` |
| Harburg | Neuwiedenthaler Straße | tertiary | 13 | 1.4 | 0.62–0.65 | 13 | `seg_0760947bbe8fbb2c` |
| Bergedorf | Lohbrügger Landstraße | tertiary | 14 | 1.2 | 0.61–0.64 | 14 | `seg_0a85476ea769f8e5` |
| Wandsbek | Pezolddamm | tertiary | 9 | 1.2 | 0.63–0.64 | 9 | `seg_0b3867bdbe79e3c8` |
| Wandsbek | Meiendorfer Mühlenweg | tertiary | 3 | 1.0 | 0.61–0.62 | 3 | `seg_30bb3774a6771bf5` |
| Hamburg-Mitte | Neßdeich | tertiary | 11 | 1.0 | 0.63–0.64 | 11 | `seg_0aae7f75e01d651d` |
| Wandsbek | Berner Chaussee | tertiary | 6 | 1.0 | 0.63–0.63 | 6 | `seg_019c93438edaebfe` |
| Hamburg-Mitte | Billhorner Brückenstraße | primary, trunk | 14 | 0.9 | 0.61–0.64 | 14 | `seg_2ec04644e430a922` |
| Wandsbek | Alter Zollweg | tertiary | 8 | 0.7 | 0.61–0.65 | 8 | `seg_531c97b51f58e4ae` |
| Harburg | Marmstorfer Weg | tertiary | 7 | 0.7 | 0.60–0.61 | 7 | `seg_0514d706e3e5f47b` |
| Hamburg-Nord | Tangstedter Landstraße | tertiary | 7 | 0.7 | 0.60–0.61 | 7 | `seg_35a5b2a465ea40fc` |
| Hamburg-Nord | Weg beim Jäger | tertiary | 1 | 0.7 | 0.61–0.61 | 1 | `seg_6f7aae04e2c2a022` |
| Hamburg-Nord | Maienweg | secondary, tertiary | 8 | 0.7 | 0.63–0.63 | 8 | `seg_0a91c4695fe747e2` |
| Wandsbek | Schöneberger Straße | tertiary | 4 | 0.6 | 0.63–0.66 | 4 | `seg_226113150b698c28` |
| Wandsbek | Charlottenburger Straße | tertiary | 6 | 0.6 | 0.65–0.65 | 6 | `seg_60bd10132b62c45d` |
| Eimsbüttel | Edmund-Siemers-Allee | service | 3 | 0.5 | 0.60–0.60 | 3 | `seg_99c694e110e792d8` |
| Hamburg-Nord | Alsterdorfer Straße | tertiary | 2 | 0.5 | 0.62–0.62 | 2 | `seg_58c8665a50ce8fcb` |
| Altona | Kalckreuthweg | tertiary | 9 | 0.5 | 0.60–0.61 | 9 | `seg_3e7885199a36fff8` |
| Wandsbek | An der Alsterschleife | tertiary | 1 | 0.5 | 0.62–0.62 | 1 | `seg_c5db1848591c3a8f` |
| Wandsbek | Berner Heerweg | tertiary | 4 | 0.5 | 0.61–0.62 | 4 | `seg_4e1a0a9712fd3d21` |
| Wandsbek | Ruscheweyhstraße | tertiary | 5 | 0.4 | 0.62–0.62 | 5 | `seg_0cb09ad647eafa58` |
| Wandsbek | Berner Allee | tertiary | 3 | 0.4 | 0.61–0.61 | 3 | `seg_2dfbd52511ff83f5` |
| Bergedorf | Nettelnburger Landweg | secondary | 3 | 0.4 | 0.60–0.63 | 3 | `seg_46e7e42775169c44` |
| Hamburg-Mitte | Hermannstal | tertiary | 1 | 0.4 | 0.60–0.60 | 1 | `seg_dc42fad1b365750d` |
| Bergedorf | Oberer Landweg | secondary | 4 | 0.4 | 0.61–0.63 | 4 | `seg_000299ecaf105205` |
| Wandsbek | Sonnenweg | tertiary | 3 | 0.3 | 0.62–0.62 | 3 | `seg_018e6051ca6f7e91` |
| Wandsbek | Pezolddamm / Berner Allee | tertiary | 1 | 0.3 | 0.61–0.61 | 1 | `seg_f98cc9459a231ea9` |
| Harburg | Karnapp | residential | 2 | 0.3 | 0.63–0.63 | 2 | `seg_235b1e7d23ea74ec` |
| Hamburg-Mitte | Kandinskyallee | tertiary | 1 | 0.2 | 0.63–0.63 | 1 | `seg_62651b34e7cf00a0` |
| Hamburg-Mitte | Ostfrieslandstraße | tertiary | 2 | 0.2 | 0.65–0.65 | 2 | `seg_2b263cc8f1c198d5` |
| Hamburg-Mitte | Aue-Hauptdeich / Finkenwerder Straße | tertiary | 1 | 0.2 | 0.65–0.65 | 1 | `seg_92b3de74023ddec5` |
| – | Krohnstieg | trunk | 1 | 0.2 | 0.67–0.67 | 0 | `seg_e3a576cd7361f4e4` |
| Altona | Spreestraße | tertiary | 3 | 0.2 | 0.63–0.63 | 3 | `seg_a7cc126b6015b2e7` |
| Eimsbüttel | Märkerweg | tertiary | 2 | 0.2 | 0.60–0.60 | 2 | `seg_77b72da9323f149e` |
| Altona | Baron-Voght-Straße | tertiary | 3 | 0.2 | 0.60–0.60 | 3 | `seg_25c14603dc04c0ac` |
| Hamburg-Mitte | – | secondary_link, trunk_link | 2 | 0.2 | 0.61–0.61 | 2 | `seg_2372da720d69487d` |
| Hamburg-Mitte | Adenauerallee | secondary | 3 | 0.2 | 0.63–0.64 | 3 | `seg_2429620f019bcb2a` |
| Wandsbek | Poppenbüttler Hauptstraße | tertiary | 2 | 0.2 | 0.62–0.62 | 2 | `seg_859335b1c862adf0` |
| Altona | Kaltenkirchener Straße | tertiary | 2 | 0.2 | 0.64–0.65 | 2 | `seg_6ae63ab99dc4e38d` |
| Altona | Franzosenkoppel | tertiary | 1 | 0.2 | 0.60–0.60 | 1 | `seg_b4c6d3bf46bec651` |
| Wandsbek | Saseler Damm | residential | 1 | 0.2 | 0.66–0.66 | 0 | `seg_dca9ee4f71ebce4a` |
| Eimsbüttel | Quickbornstraße | tertiary | 1 | 0.2 | 0.60–0.60 | 1 | `seg_d2909ef54dd5521f` |
| Hamburg-Nord | Weidestraße | tertiary | 1 | 0.1 | 0.61–0.61 | 1 | `seg_568fb824d852e8f4` |
| Hamburg-Mitte | Veddeler Brückenstraße | tertiary | 1 | 0.1 | 0.62–0.62 | 1 | `seg_c2da4f80c0b760fa` |
| Hamburg-Nord | Barcastraße | residential, tertiary | 3 | 0.1 | 0.63–0.64 | 3 | `seg_825bb84f32539221` |
| Wandsbek | August-Krogmann-Straße | secondary | 2 | 0.1 | 0.63–0.64 | 2 | `seg_95d3d1e97133e96c` |
| Hamburg-Mitte | Wilhelmsburger Brücke / Veddeler Straße | tertiary | 1 | 0.1 | 0.62–0.62 | 1 | `seg_2e4d6adb4c35233e` |
| Wandsbek | Pulverhofsweg | tertiary | 1 | 0.1 | 0.63–0.63 | 1 | `seg_f1483665c3670ee3` |
| Hamburg-Mitte | Billhorner Röhrendamm | tertiary | 3 | 0.1 | 0.62–0.62 | 3 | `seg_04ca7d40bfa6a9fa` |
| Hamburg-Nord | Buchtstraße | residential | 2 | 0.1 | 0.63–0.63 | 2 | `seg_bc4663404f91cebe` |

## Stichprobe: bis zu 30 zufällige Abschnitte je Kategorie in Hamburg (7 Bezirke), nach Bezirk geschichtet (Seed 42)

Zur manuellen Durchsicht im Orthophoto (Geoportal Hamburg, DOP belaubt) und in Panoramax. Befund in `reports/classification_sample.csv` eintragen (Spalten cat_expected_manual, check_ok, comment).

**Durchsicht: offen.**

### SW (30 von 461)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_05a7bf220b7ad3fa` | Altona | – | motorway_link | 34 | HVS | 0.69 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560518,5937501]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582861/9.914132) | [Way](https://www.openstreetmap.org/way/7728240) |
| `seg_325e440917f1278c` | Altona | – | motorway | 1907 | keine HVS | 0.43 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560039,5936613]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.574939/9.906739) | [Way](https://www.openstreetmap.org/way/544370554) |
| `seg_7cc5b04626f82d44` | Altona | Sülldorfer Landstraße | trunk | 67 | HVS | 0.65 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[551436,5937115]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580366/9.776909) | [Way](https://www.openstreetmap.org/way/87332490) |
| `seg_85c73edbca417d8b` | Altona | – | motorway_link | 208 | keine HVS | 0.14 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559369,5934537]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556352/9.896224) | [Way](https://www.openstreetmap.org/way/10702956) |
| `seg_69014dc36e618efa` | Bergedorf | – | motorway_link | 209 | keine HVS | 0.37 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580198,5925909]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.476047/10.208379) | [Way](https://www.openstreetmap.org/way/154660626) |
| `seg_69d0025726b99d8a` | Bergedorf | – | motorway_link | 70 | keine HVS | 0.10 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580060,5925886]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.475867/10.206298) | [Way](https://www.openstreetmap.org/way/549828895) |
| `seg_18898a328316b431` | Eimsbüttel | – | motorway_link | 35 | keine HVS | 0.24 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560012,5941411]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.618067/9.907242) | [Way](https://www.openstreetmap.org/way/526877185) |
| `seg_1dcaac6278efae03` | Eimsbüttel | – | motorway_link | 145 | keine HVS | 0.42 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560193,5941346]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.617456/9.909974) | [Way](https://www.openstreetmap.org/way/37813970) |
| `seg_c9517409770da0de` | Eimsbüttel | – | motorway | 246 | keine HVS | 0.52 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561121,5943390]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.635722/9.924401) | [Way](https://www.openstreetmap.org/way/296326689) |
| `seg_dc0c91a089a9e1d1` | Eimsbüttel | – | motorway_link | 207 | keine HVS | 0.10 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559881,5941656]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620280/9.905321) | [Way](https://www.openstreetmap.org/way/10621047) |
| `seg_eb8ba2578753f64e` | Eimsbüttel | – | motorway | 653 | keine HVS | 0.52 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561276,5943811]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.639489/9.926834) | [Way](https://www.openstreetmap.org/way/850384023) |
| `seg_fa8172b9922d7535` | Eimsbüttel | – | motorway | 214 | keine HVS | 0.34 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561493,5944662]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.647107/9.930279) | [Way](https://www.openstreetmap.org/way/682144625) |
| `seg_07cb43beddcf7600` | Hamburg-Mitte | – | trunk | 570 | keine HVS | 0.61 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566743,5929014]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.505835/10.006336) | [Way](https://www.openstreetmap.org/way/733716414) |
| `seg_08cfbba6b302b4d7` | Hamburg-Mitte | – | motorway_link | 487 | keine HVS | 0.40 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568058,5926657]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.484482/10.025656) | [Way](https://www.openstreetmap.org/way/93762326) |
| `seg_0abd6821a7c3f28c` | Hamburg-Mitte | – | motorway_link | 11 | keine HVS | 0.54 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575842,5933532]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.545204/10.144603) | [Way](https://www.openstreetmap.org/way/316060718) |
| `seg_2245a9ca41da71ee` | Hamburg-Mitte | – | motorway | 824 | keine HVS | 0.52 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568536,5929746]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.512184/10.033532) | [Way](https://www.openstreetmap.org/way/45069890) |
| `seg_4f05da745142390c` | Hamburg-Mitte | – | motorway | 190 | keine HVS | 0.55 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561046,5930228]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.517438/9.920689) | [Way](https://www.openstreetmap.org/way/1567691200) |
| `seg_52e216c99dd55193` | Hamburg-Mitte | – | motorway_link | 65 | keine HVS | 0.35 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575001,5931577]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.527751/10.131449) | [Way](https://www.openstreetmap.org/way/10625741) |
| `seg_9e2e39ca5b19a8a1` | Hamburg-Mitte | – | motorway | 1463 | keine HVS | 0.67 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575315,5935905]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.566608/10.137214) | [Way](https://www.openstreetmap.org/way/316907870) |
| `seg_c04a7f4cc75ce047` | Hamburg-Mitte | – | motorway_link | 135 | keine HVS | 0.42 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560992,5930222]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.517390/9.919878) | [Way](https://www.openstreetmap.org/way/10594246) |
| `seg_cd6fc0c6adf7bcc2` | Hamburg-Mitte | – | motorway_link | 381 | keine HVS | 0.22 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568077,5926586]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.483842/10.025925) | [Way](https://www.openstreetmap.org/way/486882724) |
| `seg_dd263af2d32758b0` | Hamburg-Mitte | – | motorway | 634 | keine HVS | 0.52 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568910,5928843]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.504017/10.038967) | [Way](https://www.openstreetmap.org/way/4068560) |
| `seg_2aae0ac4ea792b30` | Hamburg-Nord | Zeppelinstraße | trunk | 470 | HVS | 0.67 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566760,5943283]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.634066/10.009651) | [Way](https://www.openstreetmap.org/way/659872942) |
| `seg_b40e03ccc0cd495e` | Hamburg-Nord | Zeppelinstraße | trunk | 127 | HVS | 0.90 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567005,5941837]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.621047/10.013043) | [Way](https://www.openstreetmap.org/way/463120830) |
| `seg_7bdd3af3e5469024` | Harburg | – | trunk | 390 | keine HVS | 0.29 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565329,5922898]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.451045/9.983746) | [Way](https://www.openstreetmap.org/way/25822442) |
| `seg_948857f2a6011244` | Harburg | – | motorway_link | 294 | keine HVS | 0.19 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560580,5926152]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.480857/9.912873) | [Way](https://www.openstreetmap.org/way/219200781) |
| `seg_d14a31b5d7a7321d` | Harburg | – | motorway_link | 20 | keine HVS | 0.29 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562120,5920626]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.431009/9.934986) | [Way](https://www.openstreetmap.org/way/206331860) |
| `seg_dc681d6fcc16da43` | Harburg | – | trunk | 396 | keine HVS | 0.29 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565688,5923035]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.452228/9.989189) | [Way](https://www.openstreetmap.org/way/26960825) |
| `seg_fc23ca32faaee987` | Harburg | – | motorway | 1133 | keine HVS | 0.47 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561550,5921169]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.435962/9.926513) | [Way](https://www.openstreetmap.org/way/25784075) |
| `seg_feea10141c96d56a` | Wandsbek | – | motorway_link | 68 | keine HVS | 0.42 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574313,5935968]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567315/10.122105) | [Way](https://www.openstreetmap.org/way/204393313) |

### GOW50 (30 von 2467)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_0abf070f423578e0` | Altona | Osdorfer Landstraße | primary | 160 | HVS | 0.87 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555905,5936327]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572825/9.844261) | [Way](https://www.openstreetmap.org/way/232714406) |
| `seg_316ac1577affe50a` | Altona | Rugenbarg | primary | 7 | HVS | 0.93 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557986,5938100]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.588530/9.876008) | [Way](https://www.openstreetmap.org/way/756339556) |
| `seg_7289f4a0809d7ab8` | Altona | Rugenfeld | primary | 56 | HVS | 0.39 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556119,5936884]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.577807/9.847584) | [Way](https://www.openstreetmap.org/way/746558961) |
| `seg_7f7fd8cb1d324885` | Altona | Rugenbarg | primary | 72 | HVS | 0.85 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556213,5936915]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578080/9.849007) | [Way](https://www.openstreetmap.org/way/1271824772) |
| `seg_2363f3418e2ba2e3` | Bergedorf | Holtenklinker Straße | secondary | 177 | HVS | 0.74 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[581724,5926330]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.479603/10.231469) | [Way](https://www.openstreetmap.org/way/173990377) |
| `seg_37acd7514e10cd8e` | Bergedorf | Bergedorfer Straße | primary | 321 | HVS | 0.96 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575518,5931300]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.525191/10.139172) | [Way](https://www.openstreetmap.org/way/700678219) |
| `seg_2699219a31c71094` | Eimsbüttel | Beim Schlump | secondary | 91 | HVS | 0.80 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564760,5936319]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571730/9.977962) | [Way](https://www.openstreetmap.org/way/391801504) |
| `seg_29703de6753c43dd` | Eimsbüttel | Holsteiner Chaussee | primary | 23 | HVS | 0.71 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559861,5940507]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.609953/9.904798) | [Way](https://www.openstreetmap.org/way/940084044) |
| `seg_e79feb96eb7427cc` | Eimsbüttel | Garstedter Weg | secondary | 43 | HVS | 0.74 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564154,5943884]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.639796/9.970360) | [Way](https://www.openstreetmap.org/way/911734456) |
| `seg_f9bd7a659bac1c8a` | Eimsbüttel | Kieler Straße | primary | 84 | HVS | 0.78 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561084,5938986]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.596144/9.922980) | [Way](https://www.openstreetmap.org/way/519098916) |
| `seg_0826aabb1bc35b8e` | Hamburg-Mitte | Sievekingsallee | primary | 8 | HVS | 0.58 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568832,5934994]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.559307/10.039141) | [Way](https://www.openstreetmap.org/way/1116978227) |
| `seg_0aae7f75e01d651d` | Hamburg-Mitte | Neßdeich | tertiary | 45 | keine HVS | 0.64 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556540,5932205]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.535706/9.853106) | [Way](https://www.openstreetmap.org/way/834615551) |
| `seg_206fefd38b4811c1` | Hamburg-Mitte | Am Saalehafen | primary | 99 | HVS | 0.70 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567085,5930940]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.523100/10.011908) | [Way](https://www.openstreetmap.org/way/516884653) |
| `seg_50069583a787b87d` | Hamburg-Mitte | Bergedorfer Straße | primary | 80 | HVS | 0.97 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575007,5931612]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.528066/10.131540) | [Way](https://www.openstreetmap.org/way/152773681) |
| `seg_54784c94a64026a2` | Hamburg-Mitte | Neuenfelder Straße | secondary | 130 | HVS | 0.76 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566925,5927959]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.496331/10.008860) | [Way](https://www.openstreetmap.org/way/252573183) |
| `seg_97fdd8c164c3e060` | Hamburg-Mitte | Horner Landstraße | secondary | 292 | HVS | 0.72 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572327,5933342]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.543993/10.091515) | [Way](https://www.openstreetmap.org/way/886646663) |
| `seg_b474f18c003bfe90` | Hamburg-Mitte | Bei der Wollkämmerei | secondary | 82 | HVS | 0.45 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565186,5928950]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.505456/9.982855) | [Way](https://www.openstreetmap.org/way/692333162) |
| `seg_d992b63dc0b626d9` | Hamburg-Mitte | Neuhöfer Damm | secondary | 171 | HVS | 0.67 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564310,5930110]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.515984/9.969885) | [Way](https://www.openstreetmap.org/way/536703971) |
| `seg_084256663f50f536` | Hamburg-Nord | Krohnstieg / Gehlengraben | primary | 241 | HVS | 0.83 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567379,5944983]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.649267/10.019370) | [Way](https://www.openstreetmap.org/way/38685166) |
| `seg_4ae87725e8103716` | Hamburg-Nord | Braamkamp | primary | 65 | HVS | 0.88 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565854,5939719]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.602153/9.995191) | [Way](https://www.openstreetmap.org/way/599771431) |
| `seg_df4d7ae5be674b8a` | Hamburg-Nord | Lauensteinstraße | primary | 11 | HVS | 0.75 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568541,5939618]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600898/10.035765) | [Way](https://www.openstreetmap.org/way/965329901) |
| `seg_e3a5909cdcf3ec1b` | Hamburg-Nord | Osterfeldstraße | primary | 55 | HVS | 0.60 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564720,5939217]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.597780/9.977957) | [Way](https://www.openstreetmap.org/way/1558898334) |
| `seg_3680b4329d73a846` | Harburg | Ehestorfer Weg | secondary | 128 | HVS | 0.64 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561883,5923203]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.454199/9.931928) | [Way](https://www.openstreetmap.org/way/39538472) |
| `seg_6477147aae7de420` | Harburg | Maldfeldstraße | secondary | 128 | HVS | 0.32 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562175,5920597]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.430747/9.935810) | [Way](https://www.openstreetmap.org/way/208933145) |
| `seg_6a036e250f4d9f2e` | Harburg | Bremer Straße | secondary | 38 | HVS | 0.58 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561904,5920388]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.428902/9.931694) | [Way](https://www.openstreetmap.org/way/4801288) |
| `seg_01689beed31241e6` | Wandsbek | Scharbeutzer Straße | secondary | 70 | HVS | 0.83 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576139,5939705]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600639/10.150581) | [Way](https://www.openstreetmap.org/way/18164415) |
| `seg_53f7659d7ad49f4e` | Wandsbek | Segeberger Chaussee | primary | 11 | HVS | 0.47 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571074,5952223]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.713843/10.076921) | [Way](https://www.openstreetmap.org/way/850928478) |
| `seg_afa3d38846933bb9` | Wandsbek | Oldenfelder Stieg | secondary | 109 | HVS | 0.63 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576538,5941232]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.614301/10.156995) | [Way](https://www.openstreetmap.org/way/222320593) |
| `seg_e5cd93f3634d1e90` | Wandsbek | Berner Straße | secondary | 12 | HVS | 0.62 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576480,5941250]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.614468/10.156125) | [Way](https://www.openstreetmap.org/way/222320583) |
| `seg_f7a46fcdf3371d89` | Wandsbek | Bramfelder Chaussee | primary | 43 | HVS | 0.91 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571835,5942740]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.628520/10.086257) | [Way](https://www.openstreetmap.org/way/1099840784) |

### GOW30 (30 von 4237)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_0b50233486bb86c5` | Altona | Luruper Hauptstraße | primary | 73 | HVS | 0.91 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556564,5939164]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598248/9.854724) | [Way](https://www.openstreetmap.org/way/759539872) |
| `seg_35d684d7fa615823` | Altona | Reventlowstraße | tertiary | 93 | keine HVS | 0.61 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559000,5934459]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.555696/9.890635) | [Way](https://www.openstreetmap.org/way/360038188) |
| `seg_7caf5b35e3b9e7cd` | Altona | Behringstraße | secondary | 69 | HVS | 0.89 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560238,5934338]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.554468/9.909303) | [Way](https://www.openstreetmap.org/way/885611490) |
| `seg_8d02b44285202a1b` | Altona | Max-Brauer-Allee | secondary | 129 | HVS | 0.56 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563384,5935245]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.562248/9.956958) | [Way](https://www.openstreetmap.org/way/919746337) |
| `seg_47cf3d0cfde97767` | Bergedorf | Holtenklinker Straße | secondary | 408 | HVS | 0.74 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[581468,5926471]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.480907/10.227659) | [Way](https://www.openstreetmap.org/way/455780731) |
| `seg_2a4334484d6efad9` | Eimsbüttel | Koppelstraße | primary | 79 | HVS | 0.92 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561836,5938612]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592697/9.934269) | [Way](https://www.openstreetmap.org/way/1504405792) |
| `seg_3059f2624fc34795` | Eimsbüttel | Vogt-Wells-Straße | primary | 11 | HVS | 0.78 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563782,5939437]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599873/9.963833) | [Way](https://www.openstreetmap.org/way/347903360) |
| `seg_446300c7b4014877` | Eimsbüttel | Langenfelder Damm | tertiary | 12 | keine HVS | 0.65 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562174,5937256]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580466/9.939102) | [Way](https://www.openstreetmap.org/way/757098525) |
| `seg_cad6571749a7fa7d` | Eimsbüttel | Pinneberger Chaussee | secondary | 46 | HVS | 0.79 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559770,5940403]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.609027/9.903398) | [Way](https://www.openstreetmap.org/way/585251802) |
| `seg_08e2ef58517bf643` | Hamburg-Mitte | Bürgerweide | primary | 14 | HVS | 0.45 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568815,5935021]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.559557/10.038893) | [Way](https://www.openstreetmap.org/way/1116978247) |
| `seg_099ca33334dc8281` | Hamburg-Mitte | Dammtorstraße | tertiary | 22 | HVS | 0.78 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565460,5934662]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556751/9.988186) | [Way](https://www.openstreetmap.org/way/551319332) |
| `seg_1b7d18c90b532e9b` | Hamburg-Mitte | Steinstraße | secondary | 113 | HVS | 0.75 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566532,5933935]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.550088/10.004213) | [Way](https://www.openstreetmap.org/way/1270952931) |
| `seg_3e8f4e37c5f6e4ca` | Hamburg-Mitte | An der Alster | residential | 81 | HVS | 0.51 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566987,5935050]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.560046/10.011305) | [Way](https://www.openstreetmap.org/way/671042146) |
| `seg_42608e7435983212` | Hamburg-Mitte | Willy-Brandt-Straße / Deichtortunnel / Amsinckstraße | primary | 346 | HVS | 0.94 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566687,5933685]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.547819/10.006497) | [Way](https://www.openstreetmap.org/way/233756781) |
| `seg_90c7139ee49a14e7` | Hamburg-Mitte | Schiffbeker Weg | secondary | 58 | HVS | 0.81 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573337,5933731]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.547343/10.106853) | [Way](https://www.openstreetmap.org/way/906652558) |
| `seg_07a821be04b03138` | Hamburg-Nord | Dennerstraße | primary | 171 | HVS | 0.92 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569200,5939142]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.596540/10.045626) | [Way](https://www.openstreetmap.org/way/55055517) |
| `seg_3460d8fded082035` | Hamburg-Nord | Barmbeker Straße | primary | 103 | HVS | 0.84 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567094,5938356]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.589749/10.013637) | [Way](https://www.openstreetmap.org/way/951434437) |
| `seg_9d918dca98c70fc3` | Hamburg-Nord | Fuhlsbüttler Straße | secondary | 24 | HVS | 0.88 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568938,5939382]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598733/10.041725) | [Way](https://www.openstreetmap.org/way/42988656) |
| `seg_a8c1d156e3f64e76` | Hamburg-Nord | Sengelmannstraße | primary | 121 | HVS | 0.70 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567508,5940996]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.613418/10.020469) | [Way](https://www.openstreetmap.org/way/608715899) |
| `seg_b7542aca43a05281` | Hamburg-Nord | Nordschleswiger Straße | primary | 34 | HVS | 0.96 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570670,5937608]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582557/10.067485) | [Way](https://www.openstreetmap.org/way/917996487) |
| `seg_cac687164acb0f7b` | Hamburg-Nord | Tarpenbekstraße | primary | 41 | HVS | 0.88 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565112,5938963]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.595456/9.983823) | [Way](https://www.openstreetmap.org/way/135652411) |
| `seg_50971d149311d938` | Harburg | Meckelfelder Weg | secondary | 144 | HVS | 0.71 | mittel | C-GOW-01 → C-G30-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565254,5919941]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.424481/9.982011) | [Way](https://www.openstreetmap.org/way/347277932) |
| `seg_a63c28394b92cec4` | Harburg | Harburger Ring | secondary | 110 | HVS | 0.76 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565375,5923645]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.457753/9.984596) | [Way](https://www.openstreetmap.org/way/672837206) |
| `seg_cf72384d8cd26522` | Harburg | Cuxhavener Straße | primary | 69 | HVS | 0.57 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554354,5924854]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.469872/9.818837) | [Way](https://www.openstreetmap.org/way/534871370) |
| `seg_02b86c408375803d` | Wandsbek | Harksheider Straße | secondary | 304 | HVS | 0.74 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570232,5947362]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.670276/10.063072) | [Way](https://www.openstreetmap.org/way/150491921) |
| `seg_4fbaa540e880c5fb` | Wandsbek | Bramfelder Chaussee | primary | 91 | HVS | 0.95 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570850,5940147]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.605352/10.070783) | [Way](https://www.openstreetmap.org/way/46042155) |
| `seg_8076e983c462fae5` | Wandsbek | Wandsbeker Marktstraße | primary | 235 | HVS | 0.88 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570676,5936451]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572157/10.067314) | [Way](https://www.openstreetmap.org/way/36971813) |
| `seg_aa23d8adb0c2b353` | Wandsbek | August-Krogmann-Straße | secondary | 13 | HVS | 0.79 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573877,5940536]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.608431/10.116615) | [Way](https://www.openstreetmap.org/way/40152296) |
| `seg_e949c809e168b5f6` | Wandsbek | Saseler Damm | primary | 39 | HVS | 0.94 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572912,5945534]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.653480/10.103190) | [Way](https://www.openstreetmap.org/way/252376138) |
| `seg_fd95150c93f6d451` | Wandsbek | Bramfelder Chaussee | primary | 90 | HVS | 0.96 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571239,5941370]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.616284/10.076931) | [Way](https://www.openstreetmap.org/way/46042157) |

### ETW30 (30 von 24773)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_076219059b33c596` | Altona | Haubachstraße | residential | 123 | keine HVS | 0.21 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562084,5934560]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556248/9.937205) | [Way](https://www.openstreetmap.org/way/720558991) |
| `seg_200b4ba6e76d3153` | Altona | Goetheallee | residential | 99 | keine HVS | 0.07 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562140,5934559]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556233/9.938050) | [Way](https://www.openstreetmap.org/way/720558996) |
| `seg_4a578fa646015979` | Altona | Baron-Voght-Straße | tertiary | 425 | keine HVS | 0.42 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557246,5933784]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.549822/9.864033) | [Way](https://www.openstreetmap.org/way/1151636261) |
| `seg_abe686d56a3cbdf2` | Altona | Vereinsweg | residential | 87 | keine HVS | 0.07 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562310,5934887]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.559160/9.940683) | [Way](https://www.openstreetmap.org/way/136726868) |
| `seg_c6d1452e2518f0d7` | Altona | Theodorstraße | service | 22 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559326,5936044]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.569909/9.895856) | [Way](https://www.openstreetmap.org/way/1073279836) |
| `seg_5a4d452691e012a7` | Bergedorf | Mary-Marcus-Kehre | living_street | 4 | keine HVS | 0.11 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578133,5927022]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.486362/10.177539) | [Way](https://www.openstreetmap.org/way/520832416) |
| `seg_60ec678848c62d9c` | Bergedorf | Richard-Linde-Weg | service | 236 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579081,5928541]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.499869/10.192208) | [Way](https://www.openstreetmap.org/way/987466410) |
| `seg_247a82a292488ced` | Eimsbüttel | Oldenburger Straße | residential | 119 | keine HVS | 0.16 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561440,5939960]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.604855/9.928542) | [Way](https://www.openstreetmap.org/way/144964690) |
| `seg_31a3882e92c3ad71` | Eimsbüttel | Haldenstieg | residential | 75 | keine HVS | 0.11 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563763,5941162]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.615383/9.963898) | [Way](https://www.openstreetmap.org/way/25550732) |
| `seg_c603392e923176d6` | Eimsbüttel | Isestraße | residential | 93 | keine HVS | 0.29 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564803,5937154]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.579232/9.978777) | [Way](https://www.openstreetmap.org/way/963174500) |
| `seg_f49389e2cb219198` | Eimsbüttel | Rebhuhnweg | residential | 135 | keine HVS | 0.25 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563127,5942759]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.629808/9.954613) | [Way](https://www.openstreetmap.org/way/4879781) |
| `seg_0d784cb73374d1d9` | Hamburg-Mitte | Bei der Stadtwassermühle | service | 144 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565692,5934217]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.552729/9.991594) | [Way](https://www.openstreetmap.org/way/1410384120) |
| `seg_0e0ff880d4c95595` | Hamburg-Mitte | Schlenzigstraße | tertiary | 15 | keine HVS | 0.02 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566280,5930585]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.520007/9.999696) | [Way](https://www.openstreetmap.org/way/1023910537) |
| `seg_256a83c2a1d64c1a` | Hamburg-Mitte | Sorbenstraße | unclassified | 298 | keine HVS | 0.03 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569220,5933957]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.549937/10.044781) | [Way](https://www.openstreetmap.org/way/1184522519) |
| `seg_2860e3ab83198a29` | Hamburg-Mitte | Altstädter Straße | residential | 9 | keine HVS | 0.20 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566480,5933847]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.549302/10.003398) | [Way](https://www.openstreetmap.org/way/1499593033) |
| `seg_beaadabd4b007200` | Hamburg-Mitte | Danziger Straße | residential | 10 | keine HVS | 0.28 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567301,5934511]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.555163/10.015929) | [Way](https://www.openstreetmap.org/way/1207286639) |
| `seg_3dc49f894797248a` | Hamburg-Nord | Ratsmühlendamm | residential | 100 | keine HVS | 0.26 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567038,5942520]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.627180/10.013689) | [Way](https://www.openstreetmap.org/way/147419145) |
| `seg_4232fc77115ceda5` | Hamburg-Nord | Brödermannsweg | residential | 91 | keine HVS | 0.17 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564291,5940100]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.605771/9.971659) | [Way](https://www.openstreetmap.org/way/264373205) |
| `seg_8c3138110e665f1e` | Hamburg-Nord | Güntherstraße | residential | 102 | keine HVS | 0.49 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568416,5935469]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.563635/10.032967) | [Way](https://www.openstreetmap.org/way/4200938) |
| `seg_a5faed2216278e77` | Hamburg-Nord | Diekwisch | residential | 218 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567070,5946039]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.658797/10.014932) | [Way](https://www.openstreetmap.org/way/150294459) |
| `seg_0e70c4adb0041402` | Harburg | Westufer-Strasse | service | 106 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563603,5925813]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.477454/9.958349) | [Way](https://www.openstreetmap.org/way/123870504) |
| `seg_57450b972d2238a2` | Harburg | An der Horeburg | residential | 56 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565415,5925021]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.470116/9.985483) | [Way](https://www.openstreetmap.org/way/5834481) |
| `seg_f58096e24a31a813` | Harburg | Strucksbarg | tertiary | 153 | keine HVS | 0.55 | niedrig | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562360,5922686]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.449495/9.939010) | [Way](https://www.openstreetmap.org/way/733216350) |
| `seg_4efd73b5b1cd53e8` | Wandsbek | Timmermoor | track | 219 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575836,5946586]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.662520/10.147690) | [Way](https://www.openstreetmap.org/way/142613440) |
| `seg_98112c15b714b00c` | Wandsbek | Fichtestraße | residential | 139 | keine HVS | 0.11 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569570,5936115]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.569281/10.050535) | [Way](https://www.openstreetmap.org/way/11924693) |
| `seg_a166852504b78b38` | Wandsbek | Öjendorfer Damm | tertiary | 66 | keine HVS | 0.59 | niedrig | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575250,5936522]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572157/10.136390) | [Way](https://www.openstreetmap.org/way/627538251) |
| `seg_c2cfb8f2769b62de` | Wandsbek | Alsterfurt / Haberkamp | residential | 397 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572061,5946539]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.662628/10.090563) | [Way](https://www.openstreetmap.org/way/24242572) |
| `seg_e68057cdb805ab73` | Wandsbek | Meiendorfer Weg | tertiary | 65 | keine HVS | 0.21 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576982,5943416]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633863/10.164234) | [Way](https://www.openstreetmap.org/way/865779428) |
| `seg_f8aa68b17acfd60e` | Wandsbek | Machandelstieg | residential | 164 | keine HVS | 0.17 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572424,5942721]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.628269/10.095166) | [Way](https://www.openstreetmap.org/way/22875998) |
| `seg_fe727299ef7ac6fe` | Wandsbek | Grönkamp | residential | 105 | keine HVS | 0.30 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570190,5945204]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.650881/10.061946) | [Way](https://www.openstreetmap.org/way/23517280) |

### ETW_ERF (30 von 1774)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_0a90dbbf0e28d531` | Altona | Zassenhausweg | living_street | 19 | keine HVS | 0.20 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554782,5936859]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.577720/9.827390) | [Way](https://www.openstreetmap.org/way/345751347) |
| `seg_32e52607b7a315a5` | Altona | Schmarjestraße | living_street | 9 | keine HVS | 0.18 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562146,5933755]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.549004/9.937986) | [Way](https://www.openstreetmap.org/way/33891763) |
| `seg_71606ad890d6bf5e` | Altona | Mariannenruh-Platz | pedestrian | 50 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562229,5935161]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.561637/9.939518) | [Way](https://www.openstreetmap.org/way/294929070) |
| `seg_20e26eafb62f9ecd` | Bergedorf | Sachsentor | pedestrian | 11 | keine HVS | 0.33 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580371,5927311]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.488619/10.211341) | [Way](https://www.openstreetmap.org/way/154189006) |
| `seg_2b47743e3b530940` | Bergedorf | Felix-Jud-Ring | living_street | 41 | keine HVS | 0.11 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576260,5926573]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.482607/10.149222) | [Way](https://www.openstreetmap.org/way/26130977) |
| `seg_4e1eb7115a28fc87` | Bergedorf | Fanny-Elßler-Bogen | living_street | 30 | keine HVS | 0.04 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578058,5925991]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.477109/10.176162) | [Way](https://www.openstreetmap.org/way/153805609) |
| `seg_545e5e6d34c1e562` | Bergedorf | Marta-Damkowski-Kehre | living_street | 86 | keine HVS | 0.11 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578106,5926594]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.482525/10.177026) | [Way](https://www.openstreetmap.org/way/153775299) |
| `seg_eec2df47d9c128f3` | Bergedorf | Elly-Heuss-Knapp-Ring | living_street | 64 | keine HVS | 0.11 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577423,5926276]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.479768/10.166668) | [Way](https://www.openstreetmap.org/way/25098094) |
| `seg_fde2817e5eeb82cf` | Bergedorf | – | pedestrian | 52 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576869,5927184]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.488007/10.158534) | [Way](https://www.openstreetmap.org/way/281414343) |
| `seg_31c797157a516623` | Eimsbüttel | Margaretha-Rothe-Weg | living_street | 94 | keine HVS | 0.11 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562654,5944351]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.644179/9.947779) | [Way](https://www.openstreetmap.org/way/8433886) |
| `seg_bc4d97869eb925d5` | Eimsbüttel | Tibarg | pedestrian | 20 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562944,5941731]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620593/9.951626) | [Way](https://www.openstreetmap.org/way/124212740) |
| `seg_ecec638b22bb3c55` | Eimsbüttel | Roman-Zeller-Platz | pedestrian | 13 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560083,5944664]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.647292/9.908953) | [Way](https://www.openstreetmap.org/way/650674161) |
| `seg_0a352bd6a099c14e` | Hamburg-Mitte | Brackhövel | residential | 27 | keine HVS | 0.11 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567439,5929639]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.511363/10.016975) | [Way](https://www.openstreetmap.org/way/674042166) |
| `seg_0a8e2e2fec8fac0a` | Hamburg-Mitte | Marseiller Promenade | pedestrian | 330 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565240,5935059]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.560351/9.984941) | [Way](https://www.openstreetmap.org/way/1212698253) |
| `seg_18d4299db55d76a3` | Hamburg-Mitte | Barkhof | pedestrian | 16 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566335,5934090]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.551507/10.001260) | [Way](https://www.openstreetmap.org/way/24408625) |
| `seg_40924f0e13f2163c` | Hamburg-Mitte | Bleicherstraße | living_street | 116 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563652,5934414]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.554753/9.960844) | [Way](https://www.openstreetmap.org/way/26609383) |
| `seg_445246126f1d2f56` | Hamburg-Mitte | Haferblöcken | residential | 536 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574817,5935235]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.560652/10.129535) | [Way](https://www.openstreetmap.org/way/24534015) |
| `seg_a5b538141740d972` | Hamburg-Mitte | Masurenweg | living_street | 129 | keine HVS | 0.03 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573509,5933469]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.544969/10.109386) | [Way](https://www.openstreetmap.org/way/25203583) |
| `seg_08c668c263ad1f49` | Hamburg-Nord | Götkensweg | residential | 72 | keine HVS | 0.11 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567958,5947508]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.671886/10.028688) | [Way](https://www.openstreetmap.org/way/86902037) |
| `seg_8b0ea278c64eebc8` | Hamburg-Nord | Erna-Stahl-Ring | living_street | 70 | keine HVS | 0.11 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569165,5942835]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.629731/10.045911) | [Way](https://www.openstreetmap.org/way/15693759) |
| `seg_5690c37f1120397d` | Harburg | Wieselstraße | living_street | 20 | keine HVS | 0.20 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558383,5926308]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.482510/9.879806) | [Way](https://www.openstreetmap.org/way/2975544) |
| `seg_64922b8ab04e1b56` | Harburg | Wilhelm-Busch-Weg | living_street | 229 | keine HVS | 0.24 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563894,5923705]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.458476/9.962317) | [Way](https://www.openstreetmap.org/way/628394521) |
| `seg_c5d4b7e8bb61f420` | Harburg | Groot Enn | pedestrian | 8 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556601,5925090]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.471754/9.852728) | [Way](https://www.openstreetmap.org/way/183797569) |
| `seg_f38743971805df5e` | Harburg | Baererstraße | living_street | 13 | keine HVS | 0.20 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565098,5923155]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.453384/9.980332) | [Way](https://www.openstreetmap.org/way/697815155) |
| `seg_fccdc9e87258e8d0` | Harburg | Distelfalterweg | living_street | 26 | keine HVS | 0.20 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553914,5924456]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.466338/9.812152) | [Way](https://www.openstreetmap.org/way/931567043) |
| `seg_025e6bcf85c67528` | Wandsbek | Roggengabel | living_street | 51 | keine HVS | 0.11 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573271,5950652]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.699424/10.109832) | [Way](https://www.openstreetmap.org/way/45275436) |
| `seg_428089fe0c2f1497` | Wandsbek | Grootmoorweg | living_street | 45 | keine HVS | 0.11 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572878,5943125]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.631838/10.102116) | [Way](https://www.openstreetmap.org/way/22822905) |
| `seg_749835014a743fe9` | Wandsbek | Herthastraße | pedestrian | 60 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571433,5940868]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.611752/10.079745) | [Way](https://www.openstreetmap.org/way/135453092) |
| `seg_b59587ff394a4e1b` | Wandsbek | Sedenkamp | living_street | 28 | keine HVS | 0.11 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572965,5952193]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.713315/10.105563) | [Way](https://www.openstreetmap.org/way/24370038) |
| `seg_c2b86be4ca53f373` | Wandsbek | Grootmoorgraben | living_street | 44 | keine HVS | 0.11 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572259,5943175]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632372/10.092764) | [Way](https://www.openstreetmap.org/way/22822825) |

### GOW80

_keine Abschnitte_

### ETW60

_keine Abschnitte_

## Lizenz

Abschnitte und Merkmale aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale (Tempo, Verkehrsmengen, ALKIS): Freie und Hansestadt Hamburg, dl-de/by-2.0; Busfahrten: HVV, dl-de/by-2.0; Einwohner: Zensus 2022, dl-de/by-2.0. Orthophotos: LGV Hamburg, dl-de/by-2.0. Panoramax-Bilder: Lizenz je Bild.
