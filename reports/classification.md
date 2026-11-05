# Klassifikationsbericht – Stufe 5

Erzeugt: 2026-11-04T21:50:09+00:00 von `pipeline/s05_classify.py`, rules.yaml 0.13.0. Nicht amtlicher Entwurf: Die Automatik schlägt vor, Menschen entscheiden (overrides/overrides.csv).

## Kennzahlen

- Klassifiziert: 34 702 Abschnitte im Arbeitsgebiet (4387.3 km), davon 33 712 in Hamburg (7 Bezirke) (4240.4 km). Abschnitte außerhalb des Arbeitsgebiets bleiben leer.
- Defaults aus C-MISS-01 genutzt: crossing_demand 100.0 %, outside_builtup_area 100.0 %, override_school_street 100.0 % der Abschnitte im Arbeitsgebiet.

### km je Kategorie

| Kategorie | Bezeichnung | Hamburg (7 Bezirke) km | Anteil | Arbeitsgebiet km | Anteil | Abschnitte (Arbeitsgebiet) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| SW | Schnellverkehrsstraße | 185.7 | 4.4 % | 189.2 | 4.3 % | 470 |
| GOW50 | Stadtmagistrale | 265.6 | 6.3 % | 266.7 | 6.1 % | 2 422 |
| GOW30 | Stadtstraße 30 | 468.4 | 11.0 % | 468.4 | 10.7 % | 4 133 |
| ETW30 | Quartiersstraße | 3202.7 | 75.5 % | 3344.8 | 76.2 % | 25 900 |
| ETW_ERF | Aufenthaltsstraße | 118.0 | 2.8 % | 118.3 | 2.7 % | 1 777 |
| GOW80 | Landstraße (Verbindung) | 0.0 | 0.0 % | 0.0 | 0.0 % | 0 |
| ETW60 | Landstraße (Erschließung) | 0.0 | 0.0 % | 0.0 | 0.0 % | 0 |

### km-Anteile je Kategorie und Bezirk

| Bezirk | Abschnitte | km | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | GOW80 | ETW60 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 4 886 | 620.5 | 5 % | 4 % | 10 % | 80 % | 2 % | 0 % | 0 % |
| Bergedorf | 1 957 | 209.3 | 2 % | 7 % | 6 % | 75 % | 10 % | 0 % | 0 % |
| Eimsbüttel | 4 004 | 470.4 | 5 % | 7 % | 11 % | 75 % | 2 % | 0 % | 0 % |
| Hamburg-Mitte | 6 839 | 881.3 | 9 % | 10 % | 11 % | 67 % | 3 % | 0 % | 0 % |
| Hamburg-Nord | 5 136 | 563.3 | 2 % | 5 % | 16 % | 76 % | 2 % | 0 % | 0 % |
| Harburg | 3 348 | 465.2 | 8 % | 7 % | 9 % | 72 % | 4 % | 0 % | 0 % |
| Wandsbek | 7 542 | 1 030.4 | 0 % | 5 % | 11 % | 82 % | 2 % | 0 % | 0 % |
| **gesamt** | 33 712 | 4 240.4 | 4 % | 6 % | 11 % | 76 % | 3 % | 0 % | 0 % |

### confidence (Anteil der Länge im Arbeitsgebiet)

| Kategorie | hoch | mittel | niedrig |
| --- | ---: | ---: | ---: |
| SW | 100.0 % | 0.0 % | 0.0 % |
| GOW50 | 0.0 % | 43.3 % | 56.7 % |
| GOW30 | 0.0 % | 83.7 % | 16.3 % |
| ETW30 | 0.0 % | 95.2 % | 4.8 % |
| ETW_ERF | 0.0 % | 100.0 % | 0.0 % |
| alle | 4.3 % | 86.8 % | 8.8 % |

Häufigste Gründe für eine herabgesetzte confidence (Abschnitte, Mehrfachnennung):

| Grund | Abschnitte |
| --- | ---: |
| `fallback:outside_builtup_area` | 34 232 |
| `fallback:override_school_street` | 32 455 |
| `fallback:in_hvs` | 27 144 |
| `fallback:conn_score` | 26 817 |
| `fallback:schools_or_kitas_within_m` | 4 054 |
| `fallback:crossing_demand` | 2 422 |
| `nahe_schwelle:conn_score~thresholds.conn_gow` | 2 409 |
| `fehlt:shop_frontage_share` | 1 363 |
| `fehlt:width_p10_m` | 379 |
| `nahe_schwelle:schools_or_kitas_within_m~thresholds.sensitive_radius` | 356 |
| `fehlt:separated_cycle_track_present` | 92 |
| `nahe_schwelle:shop_frontage_share~thresholds.frontage` | 49 |

`fehlt:x` = Eingangswert fehlt und entscheidet; `nahe_schwelle:x~s` = Wert innerhalb ±10 % der Schwelle; `fallback:x` = Fallback-Quelle oder Default (C-CONF-01).

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| Goldene Fälle grün | ok | 27/27 |
| Jeder Abschnitt im Arbeitsgebiet hat eine Kategorie | ok | 34702 klassifiziert, 1824 außerhalb (leer) |
| rule_trace gefüllt | ok | JSON-Liste mit mindestens einer Regel |
| confidence gültig | ok | hoch, mittel, niedrig |

## Methode

- Kaskade `classification` aus rules.yaml, Reihenfolge = Priorität: C-SW-01 → C-RUR-01 → C-ERF-01 → C-GOW-01 (dann C-G30-01, C-G30-02, sonst C-G50-01) → C-ETW-01. Die Bedingungen werden von `pipeline/lib/expr.py` gelesen; Schwellen nur aus rules.yaml.
- **Fehlende Werte (C-MISS-01):** dreiwertige Logik; eine Regel greift nur bei sicher wahrer Bedingung. Defaults für Merkmale ohne Datenquelle: outside_builtup_area = False, override_school_street = False, crossing_demand = not_assessed.
- **confidence (C-CONF-01):** niedrig, wenn ein entscheidender Wert fehlt oder innerhalb ±10 % einer Schwelle liegt; mittel bei Fallback-Quellen (schools_or_kitas_within_m, in_hvs, conn_score) und Defaults; sonst hoch. Es zählen nur Werte, die das Ergebnis bestimmt haben.
- `rule_trace` (JSON) enthält je geprüfter Regel id, passed, result (true/false/null), inputs, confidence und Gründe; `rule_path` die gegriffenen Regeln.
- HVS = `in_hvs` (DTV-Linien 2019, S-CONF-04). Bezirksstraße = keine HVS und keine Autobahn (motorway, motorway_link); Annahme für diesen Bericht.

## Kreuztabelle Soll × HVS – Hamburg (7 Bezirke) (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 20.7 | 165.0 | 0.0 | 185.7 | 3.1 % |
| GOW50 | 237.6 | 28.0 | 0.0 | 265.6 | 35.5 % |
| GOW30 | 410.0 | 58.4 | 0.0 | 468.4 | 61.3 % |
| ETW30 | 0.0 | 3202.7 | 0.0 | 3202.7 | 0.0 % |
| ETW_ERF | 0.6 | 117.4 | 0.0 | 118.0 | 0.1 % |
| **Summe** | 668.9 | 3571.5 | 0.0 | 4240.4 | |

## Kreuztabelle Soll × HVS – Arbeitsgebiet (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 20.7 | 168.6 | 0.0 | 189.2 | 3.1 % |
| GOW50 | 238.4 | 28.2 | 0.0 | 266.7 | 35.6 % |
| GOW30 | 410.0 | 58.4 | 0.0 | 468.4 | 61.2 % |
| ETW30 | 0.0 | 3344.8 | 0.0 | 3344.8 | 0.0 % |
| ETW_ERF | 0.6 | 117.6 | 0.0 | 118.3 | 0.1 % |
| **Summe** | 669.8 | 3717.6 | 0.0 | 4387.3 | |

### HVS-km je Bezirk (Arbeitsgebiet)

| Bezirk | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | GOW80 | ETW60 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 3.0 | 23.1 | 56.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| Bergedorf | 0.0 | 13.0 | 11.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| Eimsbüttel | 0.3 | 30.6 | 46.8 | 0.0 | 0.0 | 0.0 | 0.0 |
| Hamburg-Mitte | 9.8 | 76.5 | 87.4 | 0.0 | 0.2 | 0.0 | 0.0 |
| Hamburg-Nord | 7.6 | 23.3 | 77.0 | 0.0 | 0.4 | 0.0 | 0.0 |
| Harburg | 0.0 | 30.8 | 38.5 | 0.0 | 0.0 | 0.0 | 0.0 |
| Wandsbek | 0.0 | 40.3 | 92.9 | 0.0 | 0.0 | 0.0 | 0.0 |
| – | 0.0 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## HVS-Abschnitte, die ETW30 werden (0 Abschnitte, 0.0 km)

Einzeln begründen (guide.md Teil 7). Ursache ist in der Kaskade nur möglich, wenn `in_hvs` wahr ist und C-GOW-01 trotzdem nicht greift – das kommt nicht vor, solange in_hvs bekannt ist.

_keine_

Weitere HVS-Abschnitte außerhalb GOW50/GOW30: ETW_ERF 7 (0.6 km), SW 33 (20.7 km).

## Bezirksstraßen, die GOW50 werden (319 Abschnitte, 28.2 km)

Zusammengefasst nach Bezirk und Straßenname. Grund ist immer C-GOW-01 über conn_score ≥ 0.6 ohne GOW30-Auslöser; einzeln begründen (guide.md Teil 7). Einzelne Abschnitte stehen in `data/interim/classified.parquet`.

Befund: tertiary 183, primary 58, secondary 50, residential 12, trunk 6, secondary_link 4, trunk_link 2, tertiary_link 2, unclassified 1, primary_link 1; Median-Länge 62 m. Kurze Stücke von Hauptstraßen deuten eher auf Lücken im HVS-Abgleich (S-CONF-04, nur match exact) als auf Bezirksstraßen hin – bei der Durchsicht prüfen.

Gezeigt: die 50 längsten von 145 Straßen (Bezirk + Name).

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
| Hamburg-Mitte | Harburger Chaussee | secondary | 1 | 0.5 | 0.65–0.65 | 1 | `seg_a2eef54e6ee34ec2` |
| Hamburg-Nord | Alsterdorfer Straße | tertiary | 2 | 0.5 | 0.62–0.62 | 2 | `seg_58c8665a50ce8fcb` |
| Altona | Kalckreuthweg | tertiary | 9 | 0.5 | 0.60–0.61 | 9 | `seg_3e7885199a36fff8` |
| Wandsbek | An der Alsterschleife | tertiary | 1 | 0.5 | 0.62–0.62 | 1 | `seg_c5db1848591c3a8f` |
| Wandsbek | Berner Heerweg | tertiary | 4 | 0.5 | 0.61–0.62 | 4 | `seg_4e1a0a9712fd3d21` |
| Wandsbek | Ruscheweyhstraße | tertiary | 5 | 0.4 | 0.62–0.62 | 5 | `seg_0cb09ad647eafa58` |
| Wandsbek | Berner Allee | tertiary | 3 | 0.4 | 0.61–0.61 | 3 | `seg_2dfbd52511ff83f5` |
| Hamburg-Mitte | Neuhöfer Straße | secondary | 1 | 0.4 | 0.61–0.61 | 1 | `seg_6af3149ffb1f92b1` |
| Bergedorf | Nettelnburger Landweg | secondary | 3 | 0.4 | 0.60–0.63 | 3 | `seg_46e7e42775169c44` |
| Hamburg-Mitte | Hermannstal | tertiary | 1 | 0.4 | 0.60–0.60 | 1 | `seg_dc42fad1b365750d` |
| Bergedorf | Oberer Landweg | secondary | 4 | 0.4 | 0.61–0.63 | 4 | `seg_000299ecaf105205` |
| Wandsbek | Sonnenweg | tertiary | 3 | 0.3 | 0.62–0.62 | 3 | `seg_018e6051ca6f7e91` |
| Wandsbek | Pezolddamm / Berner Allee | tertiary | 1 | 0.3 | 0.61–0.61 | 1 | `seg_f98cc9459a231ea9` |
| Harburg | Karnapp | residential | 2 | 0.3 | 0.63–0.63 | 2 | `seg_235b1e7d23ea74ec` |
| Hamburg-Mitte | Schiffbeker Weg | secondary | 1 | 0.2 | 0.62–0.62 | 1 | `seg_abf7659fac6ea5a3` |
| Hamburg-Mitte | Kandinskyallee | tertiary | 1 | 0.2 | 0.63–0.63 | 1 | `seg_62651b34e7cf00a0` |
| Hamburg-Mitte | Ostfrieslandstraße | tertiary | 2 | 0.2 | 0.65–0.65 | 2 | `seg_2b263cc8f1c198d5` |
| Hamburg-Mitte | Aue-Hauptdeich / Finkenwerder Straße | tertiary | 1 | 0.2 | 0.65–0.65 | 1 | `seg_92b3de74023ddec5` |
| Hamburg-Mitte | Bergedorfer Straße | primary | 1 | 0.2 | 0.65–0.65 | 1 | `seg_51622f2841c3ee61` |
| Bergedorf | Bergedorfer Straße | primary | 4 | 0.2 | 0.62–0.68 | 4 | `seg_2ecda096c1a969aa` |
| – | Krohnstieg | trunk | 1 | 0.2 | 0.67–0.67 | 1 | `seg_e3a576cd7361f4e4` |
| Wandsbek | Jenfelder Allee | secondary | 2 | 0.2 | 0.64–0.65 | 2 | `seg_1ce1057fbf472666` |
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
| Altona | Osdorfer Landstraße | primary | 2 | 0.1 | 0.64–0.66 | 2 | `seg_94150d16a4a1459d` |
| Hamburg-Nord | Weidestraße | tertiary | 1 | 0.1 | 0.61–0.61 | 1 | `seg_568fb824d852e8f4` |
| Harburg | Stader Straße | primary | 1 | 0.1 | 0.60–0.60 | 1 | `seg_e7876de107a2b7ff` |

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

### GOW50 (30 von 2415)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_0abf070f423578e0` | Altona | Osdorfer Landstraße | primary | 160 | HVS | 0.87 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555905,5936327]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572825/9.844261) | [Way](https://www.openstreetmap.org/way/232714406) |
| `seg_31837e4164d831d2` | Altona | St. Pauli Fischmarkt | secondary | 30 | HVS | 0.55 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563159,5933470]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.546322/9.953213) | [Way](https://www.openstreetmap.org/way/609095341) |
| `seg_71eb8671ec6d1923` | Altona | Bornkampsweg | secondary | 25 | HVS | 0.65 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560778,5936090]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.570154/9.917793) | [Way](https://www.openstreetmap.org/way/296990992) |
| `seg_7dfe6b1bed83bf05` | Altona | Osdorfer Weg | primary | 48 | keine HVS | 0.63 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559584,5935521]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565177/9.899655) | [Way](https://www.openstreetmap.org/way/926301895) |
| `seg_2363f3418e2ba2e3` | Bergedorf | Holtenklinker Straße | secondary | 177 | HVS | 0.74 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[581724,5926330]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.479603/10.231469) | [Way](https://www.openstreetmap.org/way/173990377) |
| `seg_37acd7514e10cd8e` | Bergedorf | Bergedorfer Straße | primary | 321 | HVS | 0.96 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575518,5931300]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.525191/10.139172) | [Way](https://www.openstreetmap.org/way/700678219) |
| `seg_2699219a31c71094` | Eimsbüttel | Beim Schlump | secondary | 91 | HVS | 0.80 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564760,5936319]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571730/9.977962) | [Way](https://www.openstreetmap.org/way/391801504) |
| `seg_29703de6753c43dd` | Eimsbüttel | Holsteiner Chaussee | primary | 23 | HVS | 0.71 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559861,5940507]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.609953/9.904798) | [Way](https://www.openstreetmap.org/way/940084044) |
| `seg_ba96cdfff8639515` | Eimsbüttel | Friedrich-Ebert-Straße / Frohmestraße | primary | 350 | HVS | 0.92 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561764,5942486]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.627524/9.933940) | [Way](https://www.openstreetmap.org/way/674053446) |
| `seg_f17d5f52cc79b795` | Eimsbüttel | Volksparkstraße | primary | 73 | HVS | 0.73 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561202,5938509]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591847/9.924660) | [Way](https://www.openstreetmap.org/way/1173689311) |
| `seg_080976fbfb400735` | Hamburg-Mitte | Amsinckstraße | primary | 433 | HVS | 0.78 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567229,5933630]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.547254/10.014653) | [Way](https://www.openstreetmap.org/way/190538908) |
| `seg_097a4533f3598a68` | Hamburg-Mitte | Kattwykdamm | secondary | 86 | HVS | 0.26 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563343,5927774]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.495107/9.954828) | [Way](https://www.openstreetmap.org/way/1207844761) |
| `seg_0b1ee812de80225c` | Hamburg-Mitte | Zweibrückenstraße | trunk_link | 55 | keine HVS | 0.61 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568125,5932101]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.533403/10.027850) | [Way](https://www.openstreetmap.org/way/151157099) |
| `seg_221d36c0183e2a55` | Hamburg-Mitte | Veddeler Straße | secondary | 269 | HVS | 0.81 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567321,5930575]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.519787/10.015388) | [Way](https://www.openstreetmap.org/way/516892188) |
| `seg_51b01f48c5373950` | Hamburg-Mitte | Großmannstraße | secondary | 217 | HVS | 0.54 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570789,5932330]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.535110/10.068084) | [Way](https://www.openstreetmap.org/way/1015338001) |
| `seg_56e6f80cbf7e70c2` | Hamburg-Mitte | Neuhöfer Straße | secondary | 17 | HVS | 0.72 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564787,5929615]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.511480/9.976973) | [Way](https://www.openstreetmap.org/way/692335717) |
| `seg_b9ddf9d4241cd59d` | Hamburg-Mitte | Karolinenstraße / Messeplatz | secondary | 23 | HVS | 0.81 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564654,5935285]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.562452/9.976140) | [Way](https://www.openstreetmap.org/way/252843140) |
| `seg_e1e21c2c081964ed` | Hamburg-Mitte | Lombardsbrücke | primary | 295 | HVS | 0.96 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566040,5934696]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556993/9.996943) | [Way](https://www.openstreetmap.org/way/186713427) |
| `seg_4b5fca6f41b56517` | Hamburg-Nord | Braamkamp | primary | 16 | HVS | 0.69 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565919,5939703]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.601998/9.996167) | [Way](https://www.openstreetmap.org/way/178146706) |
| `seg_abd1c7797dded80f` | Hamburg-Nord | Krohnstieg | trunk | 818 | HVS | 0.66 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564808,5944754]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.647531/9.980434) | [Way](https://www.openstreetmap.org/way/220656000) |
| `seg_e391632b1868185c` | Hamburg-Nord | Herbert-Weichmann-Straße | secondary | 122 | HVS | 0.62 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567043,5936589]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573873/10.012485) | [Way](https://www.openstreetmap.org/way/22468208) |
| `seg_e64db4accca52e32` | Hamburg-Nord | Bramfelder Straße | primary | 14 | HVS | 0.73 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569598,5938053]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.586696/10.051389) | [Way](https://www.openstreetmap.org/way/31640693) |
| `seg_33323428ce02a477` | Harburg | Moorburger Bogen | secondary | 49 | HVS | 0.47 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562214,5925713]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.476719/9.937412) | [Way](https://www.openstreetmap.org/way/274759845) |
| `seg_6a036e250f4d9f2e` | Harburg | Bremer Straße | secondary | 38 | HVS | 0.58 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561904,5920388]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.428902/9.931694) | [Way](https://www.openstreetmap.org/way/4801288) |
| `seg_906aa1c54932fe25` | Harburg | Neuländer Straße | secondary | 141 | HVS | 0.79 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566064,5924458]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.464974/9.995143) | [Way](https://www.openstreetmap.org/way/598514755) |
| `seg_01689beed31241e6` | Wandsbek | Scharbeutzer Straße | secondary | 70 | HVS | 0.83 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576139,5939705]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600639/10.150581) | [Way](https://www.openstreetmap.org/way/18164415) |
| `seg_53202303db842abd` | Wandsbek | Am Luisenhof | secondary | 16 | HVS | 0.83 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573899,5940411]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.607302/10.116905) | [Way](https://www.openstreetmap.org/way/608158356) |
| `seg_e2446ff751139d13` | Wandsbek | Farmsener Landstraße | secondary | 13 | HVS | 0.64 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576601,5944774]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.646121/10.158817) | [Way](https://www.openstreetmap.org/way/971933056) |
| `seg_f531834395a3c19c` | Wandsbek | Poppenbütteler Weg | primary | 158 | HVS | 0.93 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571347,5945548]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.653816/10.079520) | [Way](https://www.openstreetmap.org/way/89250284) |
| `seg_f5a1e1d118c7c4a2` | Wandsbek | Am Stadtrand | secondary | 38 | HVS | 0.62 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572846,5937889]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.584785/10.100412) | [Way](https://www.openstreetmap.org/way/1487754199) |

### GOW30 (30 von 4133)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_0552b19135b13d9e` | Altona | Wedeler Landstraße | primary | 241 | HVS | 0.76 | mittel | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[549204,5937593]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.584873/9.743271) | [Way](https://www.openstreetmap.org/way/1171268124) |
| `seg_1b4ca2ba3d687aa8` | Altona | Stresemannstraße | primary | 188 | HVS | 0.97 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561462,5935364]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.563546/9.927975) | [Way](https://www.openstreetmap.org/way/149776905) |
| `seg_a88da8ea882f9ee5` | Altona | Ebertallee | secondary | 234 | HVS | 0.72 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558954,5936187]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571233/9.890265) | [Way](https://www.openstreetmap.org/way/88820384) |
| `seg_c2d60f287f45ea0a` | Altona | Rissener Landstraße | secondary | 113 | HVS | 0.68 | mittel | C-GOW-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[552264,5936027]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.570499/9.789234) | [Way](https://www.openstreetmap.org/way/132426250) |
| `seg_6b036b84c9e2a962` | Bergedorf | Curslacker Neuer Deich | secondary | 47 | HVS | 0.63 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580130,5926296]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.479537/10.207454) | [Way](https://www.openstreetmap.org/way/1418989261) |
| `seg_328fed2de7f0332f` | Eimsbüttel | Alsterglacis | primary | 8 | HVS | 0.79 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565619,5935078]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.560473/9.990663) | [Way](https://www.openstreetmap.org/way/521045513) |
| `seg_44d5f05fd367885d` | Eimsbüttel | Schleswiger Damm | secondary | 9 | HVS | 0.73 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560594,5944088]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.642058/9.916560) | [Way](https://www.openstreetmap.org/way/973179017) |
| `seg_67fe48eecf60a9ff` | Eimsbüttel | Hoheluftchaussee | primary | 125 | HVS | 0.83 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564232,5937628]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.583563/9.970262) | [Way](https://www.openstreetmap.org/way/50390277) |
| `seg_6f9c99c800beb8d8` | Eimsbüttel | Grindelallee | primary | 333 | HVS | 0.85 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564903,5935964]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.568522/9.980043) | [Way](https://www.openstreetmap.org/way/391801517) |
| `seg_1986e6768e4a6516` | Hamburg-Mitte | Heidenkampsweg | primary | 169 | HVS | 0.93 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568006,5934019]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.550649/10.026471) | [Way](https://www.openstreetmap.org/way/763469904) |
| `seg_7d893767ffe3928b` | Hamburg-Mitte | Eiffestraße | primary | 103 | HVS | 0.74 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568690,5934226]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.552420/10.036839) | [Way](https://www.openstreetmap.org/way/129654581) |
| `seg_a0fd1e4055ba6f79` | Hamburg-Mitte | Kurt-Schumacher-Allee | secondary | 165 | HVS | 0.42 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567222,5934130]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.551754/10.014659) | [Way](https://www.openstreetmap.org/way/429244717) |
| `seg_ad2476f3119e960a` | Hamburg-Mitte | Horner Landstraße | secondary | 258 | HVS | 0.78 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571246,5934130]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.551218/10.075386) | [Way](https://www.openstreetmap.org/way/228238169) |
| `seg_c739640b7f3af5e5` | Hamburg-Mitte | Überseeallee | secondary | 141 | HVS | 0.58 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566323,5932924]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.541028/10.000845) | [Way](https://www.openstreetmap.org/way/1146544574) |
| `seg_db0fccdc5b32f79b` | Hamburg-Mitte | Nordkanalbrücke / Nordkanalstraße | primary | 408 | HVS | 0.92 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567115,5933699]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.547889/10.012950) | [Way](https://www.openstreetmap.org/way/118756784) |
| `seg_08d292714ba78144` | Hamburg-Nord | Kellinghusenstraße | tertiary | 22 | keine HVS | 0.61 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565678,5938484]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591079/9.992272) | [Way](https://www.openstreetmap.org/way/584698808) |
| `seg_08ece6937e6d7ad7` | Hamburg-Nord | Steilshooper Straße | tertiary | 6 | keine HVS | 0.60 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569491,5938872]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.594074/10.049964) | [Way](https://www.openstreetmap.org/way/1119913469) |
| `seg_19daa0f36ece29a1` | Hamburg-Nord | Alsterkrugchaussee | secondary | 159 | HVS | 0.83 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567122,5943083]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632226/10.015083) | [Way](https://www.openstreetmap.org/way/951670845) |
| `seg_3ab3482da24298cb` | Hamburg-Nord | Barmbeker Straße | primary | 21 | HVS | 0.87 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566402,5938634]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592339/10.003237) | [Way](https://www.openstreetmap.org/way/1297690804) |
| `seg_3f576898794f7737` | Hamburg-Nord | Erdkampsweg | secondary | 75 | HVS | 0.58 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567839,5942465]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.626578/10.025786) | [Way](https://www.openstreetmap.org/way/22817705) |
| `seg_92475fc4b68961e4` | Hamburg-Nord | Barmbeker Straße | primary | 73 | HVS | 0.94 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567334,5938062]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.587072/10.017200) | [Way](https://www.openstreetmap.org/way/55301793) |
| `seg_0b583aef30cef6cb` | Harburg | Hohe Straße | primary | 206 | HVS | 0.68 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564791,5922959]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.451655/9.975658) | [Way](https://www.openstreetmap.org/way/152741721) |
| `seg_e3ef1bf1917da630` | Harburg | Neuwiedenthaler Straße | tertiary | 81 | keine HVS | 0.65 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558993,5925817]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.478028/9.888901) | [Way](https://www.openstreetmap.org/way/549792188) |
| `seg_f835afa6e1e7b19d` | Harburg | Friedhofstraße | tertiary | 79 | HVS | 0.49 | mittel | C-GOW-01 → C-G30-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563548,5922366]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.446483/9.956828) | [Way](https://www.openstreetmap.org/way/783336839) |
| `seg_392c4f29b4fef7f6` | Wandsbek | Schiffbeker Weg | secondary | 60 | HVS | 0.91 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574456,5936343]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.570662/10.124362) | [Way](https://www.openstreetmap.org/way/253918283) |
| `seg_798cd4377996f0de` | Wandsbek | Bramfelder Chaussee | primary | 96 | HVS | 0.95 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570980,5940573]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.609156/10.072837) | [Way](https://www.openstreetmap.org/way/990146037) |
| `seg_a06c136394551aa7` | Wandsbek | Hummelsbüttler Hauptstraße | secondary | 444 | HVS | 0.61 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568856,5944388]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.643730/10.041583) | [Way](https://www.openstreetmap.org/way/27218691) |
| `seg_bfe70a8f4b68c556` | Wandsbek | Rahlstedter Weg | secondary | 37 | HVS | 0.85 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574115,5940298]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.606255/10.120146) | [Way](https://www.openstreetmap.org/way/22744195) |
| `seg_ceff3ff5ae54ed4d` | Wandsbek | Hummelsbütteler Weg | tertiary | 48 | keine HVS | 0.61 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569273,5944256]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.642487/10.047857) | [Way](https://www.openstreetmap.org/way/181369514) |
| `seg_d420278acca3b969` | Wandsbek | Saseler Damm | primary | 22 | HVS | 0.66 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572811,5945603]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.654108/10.101691) | [Way](https://www.openstreetmap.org/way/549602108) |

### ETW30 (30 von 24929)

| segment_id | Bezirk | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_076219059b33c596` | Altona | Haubachstraße | residential | 123 | keine HVS | 0.21 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562084,5934560]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556248/9.937205) | [Way](https://www.openstreetmap.org/way/720558991) |
| `seg_1fd8f2ecbd8c4628` | Altona | Lüttkamp | residential | 148 | keine HVS | 0.55 | niedrig | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558079,5938488]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592010/9.877484) | [Way](https://www.openstreetmap.org/way/130661482) |
| `seg_4a08be8ae4598797` | Altona | Thunstraße | residential | 197 | keine HVS | 0.06 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556183,5934387]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.555359/9.848103) | [Way](https://www.openstreetmap.org/way/13448784) |
| `seg_aacb5f243901bdb7` | Altona | Düpenautal | residential | 27 | keine HVS | 0.23 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555339,5935911]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.569145/9.835636) | [Way](https://www.openstreetmap.org/way/23046224) |
| `seg_c5d7c215d4aec750` | Altona | Heerhof | residential | 74 | keine HVS | 0.11 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[552654,5937407]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582869/9.795349) | [Way](https://www.openstreetmap.org/way/24241601) |
| `seg_59ee903f389357df` | Bergedorf | Max-Eichholz-Ring | residential | 99 | keine HVS | 0.20 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580710,5929194]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.505492/10.216934) | [Way](https://www.openstreetmap.org/way/26305892) |
| `seg_6022526f5e6f287e` | Bergedorf | Albert-Gebel-Straße | residential | 306 | keine HVS | 0.20 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579458,5926970]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.485699/10.197502) | [Way](https://www.openstreetmap.org/way/45108687) |
| `seg_2467dfafc2f66ace` | Eimsbüttel | Troplowitzstraße | tertiary | 214 | keine HVS | 0.58 | niedrig | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563927,5937805]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.585195/9.965684) | [Way](https://www.openstreetmap.org/way/719283014) |
| `seg_311f8d09a50bcf8c` | Eimsbüttel | Im Holderstrauch | residential | 402 | keine HVS | 0.11 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560653,5944789]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.648349/9.917604) | [Way](https://www.openstreetmap.org/way/23300037) |
| `seg_c489f68538aafe52` | Eimsbüttel | Niendorfer Straße | secondary | 26 | keine HVS | 0.57 | niedrig | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563239,5940110]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.605988/9.955760) | [Way](https://www.openstreetmap.org/way/1308433391) |
| `seg_f32a379f01a4456f` | Eimsbüttel | Kalvslohtwiete | residential | 243 | keine HVS | 0.27 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559135,5942601]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.628856/9.894216) | [Way](https://www.openstreetmap.org/way/23711872) |
| `seg_0d3da40f53552143` | Hamburg-Mitte | Breslauer Straße | unclassified | 19 | keine HVS | 0.28 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564012,5930157]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.516446/9.965408) | [Way](https://www.openstreetmap.org/way/795925236) |
| `seg_0deb7636122db276` | Hamburg-Mitte | Strandweg-Ost | service | 353 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570009,5933095]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.542089/10.056484) | [Way](https://www.openstreetmap.org/way/24757488) |
| `seg_24a19537f4d3890b` | Hamburg-Mitte | Horner-Marsch-Straße | track | 98 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570876,5934119]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.551168/10.069802) | [Way](https://www.openstreetmap.org/way/822262243) |
| `seg_27df5bed33af1c56` | Hamburg-Mitte | Adenauerallee | residential | 106 | keine HVS | 0.29 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567248,5934242]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.552751/10.015077) | [Way](https://www.openstreetmap.org/way/147936476) |
| `seg_bc28eac2deb98d00` | Hamburg-Mitte | Horner Landstraße | secondary | 309 | keine HVS | 0.52 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571867,5933725]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.547499/10.084666) | [Way](https://www.openstreetmap.org/way/886646665) |
| `seg_075119564fdce97c` | Hamburg-Nord | Alter Güterbahnhof | residential | 24 | keine HVS | 0.30 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568532,5938602]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591771/10.035410) | [Way](https://www.openstreetmap.org/way/397150026) |
| `seg_3d2d81d4c9c9ec19` | Hamburg-Nord | Südring | residential | 116 | keine HVS | 0.40 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567277,5938589]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591821/10.016458) | [Way](https://www.openstreetmap.org/way/1568921144) |
| `seg_41c6d60713cc547f` | Hamburg-Nord | Geffckenstraße | tertiary | 143 | keine HVS | 0.33 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565739,5937948]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.586255/9.993088) | [Way](https://www.openstreetmap.org/way/20901082) |
| `seg_8b5940e442daab00` | Hamburg-Nord | Justus-Strandes-Weg | residential | 344 | keine HVS | 0.03 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568100,5942198]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.624142/10.029680) | [Way](https://www.openstreetmap.org/way/4825187) |
| `seg_a56007ffbfdc4322` | Hamburg-Nord | Alsterdorfer Straße | tertiary_link | 13 | keine HVS | 0.27 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566902,5940593]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.609878/10.011215) | [Way](https://www.openstreetmap.org/way/1340650970) |
| `seg_568f0dfcf92ccd8c` | Harburg | Neumoorland | residential | 78 | keine HVS | 0.25 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557912,5925731]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.477370/9.872598) | [Way](https://www.openstreetmap.org/way/3678063) |
| `seg_ec99303ad029d94f` | Harburg | Hohe Straße | tertiary | 14 | keine HVS | 0.29 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565118,5922975]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.451761/9.980595) | [Way](https://www.openstreetmap.org/way/601093065) |
| `seg_f38eb23c8ace9bc7` | Harburg | Treidelweg | residential | 200 | keine HVS | 0.11 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565767,5924648]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.466715/9.990720) | [Way](https://www.openstreetmap.org/way/5808394) |
| `seg_02ef983d258313de` | Wandsbek | Schmalenremen | residential | 28 | keine HVS | 0.24 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576750,5946620]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.662690/10.161530) | [Way](https://www.openstreetmap.org/way/44018493) |
| `seg_4eec952b6c79a761` | Wandsbek | Stadtbahnstraße | tertiary | 22 | keine HVS | 0.22 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572918,5945506]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.653228/10.103275) | [Way](https://www.openstreetmap.org/way/549602127) |
| `seg_64d505be46592ca6` | Wandsbek | Hochestieg / Kelterstraße | residential | 581 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571198,5943156]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632346/10.076729) | [Way](https://www.openstreetmap.org/way/71422764) |
| `seg_9785221dc06e60d5` | Wandsbek | Nydamer Weg | residential | 96 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576570,5941791]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.619315/10.157607) | [Way](https://www.openstreetmap.org/way/23067918) |
| `seg_a1267a40d7925afc` | Wandsbek | Zur Küperkoppel | residential | 104 | keine HVS | 0.23 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574971,5938551]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.590436/10.132670) | [Way](https://www.openstreetmap.org/way/24625411) |
| `seg_d1ad8a33142be586` | Wandsbek | Ellerneck | residential | 120 | keine HVS | 0.26 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575795,5938681]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591483/10.145149) | [Way](https://www.openstreetmap.org/way/4361364) |

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
