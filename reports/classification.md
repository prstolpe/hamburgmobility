# Klassifikationsbericht – Stufe 5

Erzeugt: 2026-10-28T13:28:54+00:00 von `pipeline/s05_classify.py`, rules.yaml 0.8.0. Nicht amtlicher Entwurf: Die Automatik schlägt vor, Menschen entscheiden (overrides/overrides.csv).

## Kennzahlen

- Klassifiziert: 4 787 Abschnitte im Arbeitsgebiet (562.0 km), davon 3 876 im Bezirk Eimsbüttel (461.5 km). Abschnitte außerhalb des Arbeitsgebiets bleiben leer.
- Defaults aus C-MISS-01 genutzt: crossing_demand 100.0 %, outside_builtup_area 100.0 %, override_school_street 100.0 % der Abschnitte im Arbeitsgebiet.

### km je Kategorie

| Kategorie | Bezeichnung | Eimsbüttel km | Anteil | Arbeitsgebiet km | Anteil | Abschnitte (Arbeitsgebiet) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| SW | Schnellverkehrsstraße | 25.6 | 5.5 % | 28.4 | 5.1 % | 120 |
| GOW50 | Stadtmagistrale | 30.2 | 6.5 % | 38.1 | 6.8 % | 367 |
| GOW30 | Stadtstraße 30 | 49.6 | 10.7 % | 57.5 | 10.2 % | 600 |
| ETW30 | Quartiersstraße | 347.1 | 75.2 % | 427.4 | 76.1 % | 3 537 |
| ETW_ERF | Aufenthaltsstraße | 9.0 | 2.0 % | 10.6 | 1.9 % | 163 |
| GOW80 | Landstraße (Verbindung) | 0.0 | 0.0 % | 0.0 | 0.0 % | 0 |
| ETW60 | Landstraße (Erschließung) | 0.0 | 0.0 % | 0.0 | 0.0 % | 0 |

### confidence (Anteil der Länge im Arbeitsgebiet)

| Kategorie | hoch | mittel | niedrig |
| --- | ---: | ---: | ---: |
| SW | 100.0 % | 0.0 % | 0.0 % |
| GOW50 | 0.0 % | 37.4 % | 62.6 % |
| GOW30 | 0.0 % | 87.8 % | 12.2 % |
| ETW30 | 0.0 % | 94.7 % | 5.3 % |
| ETW_ERF | 0.0 % | 100.0 % | 0.0 % |
| alle | 5.1 % | 85.4 % | 9.6 % |

Häufigste Gründe für eine herabgesetzte confidence (Abschnitte, Mehrfachnennung):

| Grund | Abschnitte |
| --- | ---: |
| `fallback:outside_builtup_area` | 4 667 |
| `fallback:override_school_street` | 4 504 |
| `fallback:in_hvs` | 3 709 |
| `fallback:conn_score` | 3 619 |
| `fallback:schools_or_kitas_within_m` | 582 |
| `fallback:crossing_demand` | 367 |
| `nahe_schwelle:conn_score~thresholds.conn_gow` | 297 |
| `fehlt:shop_frontage_share` | 236 |
| `nahe_schwelle:schools_or_kitas_within_m~thresholds.sensitive_radius` | 65 |
| `fehlt:width_p10_m` | 55 |
| `fehlt:separated_cycle_track_present` | 8 |
| `nahe_schwelle:shop_frontage_share~thresholds.frontage` | 5 |

`fehlt:x` = Eingangswert fehlt und entscheidet; `nahe_schwelle:x~s` = Wert innerhalb ±10 % der Schwelle; `fallback:x` = Fallback-Quelle oder Default (C-CONF-01).

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 34502 Abschnitte |
| Goldene Fälle grün | ok | 27/27 |
| Jeder Abschnitt im Arbeitsgebiet hat eine Kategorie | ok | 4787 klassifiziert, 29715 außerhalb (leer) |
| rule_trace gefüllt | ok | JSON-Liste mit mindestens einer Regel |
| confidence gültig | ok | hoch, mittel, niedrig |

## Methode

- Kaskade `classification` aus rules.yaml, Reihenfolge = Priorität: C-SW-01 → C-RUR-01 → C-ERF-01 → C-GOW-01 (dann C-G30-01, C-G30-02, sonst C-G50-01) → C-ETW-01. Die Bedingungen werden von `pipeline/lib/expr.py` gelesen; Schwellen nur aus rules.yaml.
- **Fehlende Werte (C-MISS-01):** dreiwertige Logik; eine Regel greift nur bei sicher wahrer Bedingung. Defaults für Merkmale ohne Datenquelle: outside_builtup_area = False, override_school_street = False, crossing_demand = not_assessed.
- **confidence (C-CONF-01):** niedrig, wenn ein entscheidender Wert fehlt oder innerhalb ±10 % einer Schwelle liegt; mittel bei Fallback-Quellen (schools_or_kitas_within_m, in_hvs, conn_score) und Defaults; sonst hoch. Es zählen nur Werte, die das Ergebnis bestimmt haben.
- `rule_trace` (JSON) enthält je geprüfter Regel id, passed, result (true/false/null), inputs, confidence und Gründe; `rule_path` die gegriffenen Regeln.
- HVS = `in_hvs` (DTV-Linien 2019, S-CONF-04). Bezirksstraße = keine HVS und keine Autobahn (motorway, motorway_link); Annahme für diesen Bericht.

## Kreuztabelle Soll × HVS – Bezirk Eimsbüttel (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0.3 | 25.3 | 0.0 | 25.6 | 0.5 % |
| GOW50 | 29.9 | 0.2 | 0.0 | 30.2 | 39.4 % |
| GOW30 | 45.6 | 3.9 | 0.0 | 49.6 | 60.1 % |
| ETW30 | 0.0 | 347.1 | 0.0 | 347.1 | 0.0 % |
| ETW_ERF | 0.0 | 9.0 | 0.0 | 9.0 | 0.0 % |
| **Summe** | 75.9 | 385.6 | 0.0 | 461.5 | |

## Kreuztabelle Soll × HVS – Arbeitsgebiet (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0.4 | 28.0 | 0.0 | 28.4 | 0.4 % |
| GOW50 | 37.5 | 0.6 | 0.0 | 38.1 | 41.5 % |
| GOW30 | 52.4 | 5.0 | 0.0 | 57.5 | 58.1 % |
| ETW30 | 0.0 | 427.4 | 0.0 | 427.4 | 0.0 % |
| ETW_ERF | 0.0 | 10.6 | 0.0 | 10.6 | 0.0 % |
| **Summe** | 90.3 | 471.7 | 0.0 | 562.0 | |

### HVS-km je Bezirk (Arbeitsgebiet, Bezirke nur mit ihrem Anteil im Arbeitsgebiet)

| Bezirk | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | GOW80 | ETW60 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 0.0 | 3.4 | 1.8 | 0.0 | 0.0 | 0.0 | 0.0 |
| Eimsbüttel | 0.3 | 29.9 | 45.6 | 0.0 | 0.0 | 0.0 | 0.0 |
| Hamburg-Mitte | 0.0 | 2.0 | 2.4 | 0.0 | 0.0 | 0.0 | 0.0 |
| Hamburg-Nord | 0.0 | 1.3 | 2.6 | 0.0 | 0.0 | 0.0 | 0.0 |
| – | 0.0 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## HVS-Abschnitte, die ETW30 werden (0 Abschnitte, 0.0 km)

Einzeln begründen (guide.md Teil 7). Ursache ist in der Kaskade nur möglich, wenn `in_hvs` wahr ist und C-GOW-01 trotzdem nicht greift – das kommt nicht vor, solange in_hvs bekannt ist.

_keine_

Weitere HVS-Abschnitte außerhalb GOW50/GOW30: SW 3 (0.4 km).

## Bezirksstraßen, die GOW50 werden (17 Abschnitte, 0.6 km)

Zusammengefasst nach Bezirk und Straßenname. Grund ist immer C-GOW-01 über conn_score ≥ 0.6 ohne GOW30-Auslöser; einzeln begründen (guide.md Teil 7). Einzelne Abschnitte stehen in `data/interim/classified.parquet`.

Befund: primary 12, tertiary 5; Median-Länge 28 m. Kurze Stücke von Hauptstraßen deuten eher auf Lücken im HVS-Abgleich (S-CONF-04, nur match exact) als auf Bezirksstraßen hin – bei der Durchsicht prüfen.

| Bezirk | Name | highway | Abschnitte | km | conn_score min–max | confidence niedrig | Beispiel |
| --- | --- | --- | ---: | ---: | --- | ---: | --- |
| Eimsbüttel | Koppelstraße | primary | 1 | 0.1 | 0.68–0.68 | 1 | `seg_89490ce5545cfa9f` |
| Eimsbüttel | Holsteiner Chaussee | primary | 1 | 0.1 | 0.61–0.61 | 1 | `seg_9af41066e9ac8903` |
| Eimsbüttel | Doormannsweg | primary | 2 | 0.0 | 0.64–0.64 | 2 | `seg_33cb6ed3e7ffbd56` |
| Eimsbüttel | Grindelallee | primary | 1 | 0.0 | 0.66–0.66 | 1 | `seg_316bf3ec250dbe56` |
| Eimsbüttel | Bundesstraße | primary | 1 | 0.0 | 0.61–0.61 | 1 | `seg_f12e48a0b33fb951` |
| Eimsbüttel | – | primary | 1 | 0.0 | 0.65–0.65 | 1 | `seg_5a3a77f617521da4` |
| Eimsbüttel | Lokstedter Steindamm | primary | 1 | 0.0 | 0.64–0.64 | 1 | `seg_35d7d10ef10e9c01` |
| Eimsbüttel | Kieler Straße | primary | 1 | 0.0 | 0.64–0.64 | 1 | `seg_596c7377b0aff893` |
| Altona | Spreestraße | tertiary | 3 | 0.2 | 0.62–0.62 | 3 | `seg_a7cc126b6015b2e7` |
| Hamburg-Mitte | Lombardsbrücke | primary | 2 | 0.1 | 0.61–0.64 | 2 | `seg_52c6fa7754021065` |
| Hamburg-Nord | Martinistraße | tertiary | 1 | 0.1 | 0.61–0.61 | 1 | `seg_7aad6709464c0bda` |
| Hamburg-Mitte | Stephansplatz | tertiary | 1 | 0.0 | 0.60–0.60 | 1 | `seg_5306dc4ae89a583a` |
| Hamburg-Mitte | Glockengießerwall | primary | 1 | 0.0 | 0.64–0.64 | 1 | `seg_fb2a06f6597892fb` |

## Stichprobe: bis zu 30 zufällige Abschnitte je Kategorie im Bezirk Eimsbüttel (Seed 42)

Zur manuellen Durchsicht im Orthophoto (Geoportal Hamburg, DOP belaubt) und in Panoramax. Befund in `reports/classification_sample.csv` eintragen (Spalten cat_expected_manual, check_ok, comment).

**Durchsicht: offen.**

### SW (30 von 98)

| segment_id | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_04c4a38ca03eda33` | – | motorway_link | 292 | keine HVS | 0.16 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559912,5941527]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.619117/9.905766) | [Way](https://www.openstreetmap.org/way/660144694) |
| `seg_0817c77e740f6f6c` | – | motorway_link | 255 | keine HVS | 0.43 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561041,5938707]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.593640/9.922273) | [Way](https://www.openstreetmap.org/way/1276595268) |
| `seg_0d04aeab169d1db6` | – | motorway_link | 36 | keine HVS | 0.26 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561096,5938963]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.595940/9.923148) | [Way](https://www.openstreetmap.org/way/1145434376) |
| `seg_18898a328316b431` | – | motorway_link | 35 | keine HVS | 0.23 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560012,5941411]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.618067/9.907242) | [Way](https://www.openstreetmap.org/way/526877185) |
| `seg_1dcaac6278efae03` | – | motorway_link | 145 | keine HVS | 0.42 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560193,5941346]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.617456/9.909974) | [Way](https://www.openstreetmap.org/way/37813970) |
| `seg_1dcc1de7b7e38c6f` | – | motorway_link | 54 | keine HVS | 0.16 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561409,5944438]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645107/9.928969) | [Way](https://www.openstreetmap.org/way/10713029) |
| `seg_2e4755bd181b2cb1` | – | motorway_link | 50 | keine HVS | 0.26 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561057,5938950]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.595827/9.922557) | [Way](https://www.openstreetmap.org/way/329485054) |
| `seg_44cb1a0e3ae2aec8` | – | motorway_link | 61 | keine HVS | 0.25 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561570,5944493]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645577/9.931402) | [Way](https://www.openstreetmap.org/way/323606086) |
| `seg_4b05c6d22ed6c74c` | – | motorway_link | 47 | keine HVS | 0.09 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561155,5943156]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633614/9.924870) | [Way](https://www.openstreetmap.org/way/323606076) |
| `seg_4bf2d90852297d5b` | – | motorway | 546 | keine HVS | 0.53 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561080,5943298]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.634901/9.923767) | [Way](https://www.openstreetmap.org/way/323606066) |
| `seg_4e12950aa3e1a431` | – | motorway | 221 | keine HVS | 0.35 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559747,5941740]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.621046/9.903305) | [Way](https://www.openstreetmap.org/way/10621048) |
| `seg_53288ca455b0fa7d` | – | motorway_link | 101 | keine HVS | 0.05 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561399,5944414]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.644888/9.928801) | [Way](https://www.openstreetmap.org/way/1128088138) |
| `seg_6428c75993e67a8f` | – | motorway_link | 278 | keine HVS | 0.09 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561100,5943433]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.636107/9.924094) | [Way](https://www.openstreetmap.org/way/10713261) |
| `seg_ae7935402e3a7ab8` | – | motorway_link | 18 | keine HVS | 0.06 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561148,5943125]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633336/9.924754) | [Way](https://www.openstreetmap.org/way/103948925) |
| `seg_af4b2e547be7d9ca` | – | motorway_link | 369 | keine HVS | 0.28 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560940,5938822]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.594688/9.920777) | [Way](https://www.openstreetmap.org/way/3128030) |
| `seg_b9cd9c6b834f7948` | – | motorway_link | 48 | keine HVS | 0.07 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561143,5943167]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633712/9.924688) | [Way](https://www.openstreetmap.org/way/10713259) |
| `seg_c0bbcc80b6c2e5d9` | – | motorway_link | 59 | keine HVS | 0.32 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560056,5941651]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620211/9.907960) | [Way](https://www.openstreetmap.org/way/127628264) |
| `seg_c9517409770da0de` | – | motorway | 246 | keine HVS | 0.52 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561121,5943390]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.635722/9.924401) | [Way](https://www.openstreetmap.org/way/296326689) |
| `seg_d5d4dc3ea94d970f` | – | motorway | 926 | keine HVS | 0.55 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560663,5938259]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.589661/9.916478) | [Way](https://www.openstreetmap.org/way/640564561) |
| `seg_dc0c91a089a9e1d1` | – | motorway_link | 207 | keine HVS | 0.09 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559881,5941656]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620280/9.905321) | [Way](https://www.openstreetmap.org/way/10621047) |
| `seg_de371e874a6cc7b3` | – | motorway_link | 375 | keine HVS | 0.32 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561202,5943335]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.635219/9.925610) | [Way](https://www.openstreetmap.org/way/757714790) |
| `seg_e0b838e13c55cef1` | – | motorway_link | 74 | keine HVS | 0.38 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561139,5938839]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.594812/9.923780) | [Way](https://www.openstreetmap.org/way/10706759) |
| `seg_e13d6b530ed40d42` | – | motorway_link | 82 | keine HVS | 0.43 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561152,5938831]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.594746/9.923973) | [Way](https://www.openstreetmap.org/way/323606084) |
| `seg_eb8ba2578753f64e` | – | motorway | 653 | keine HVS | 0.53 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561276,5943811]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.639489/9.926834) | [Way](https://www.openstreetmap.org/way/850384023) |
| `seg_effc86f78823c91e` | – | motorway_link | 62 | keine HVS | 0.30 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561065,5938949]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.595815/9.922688) | [Way](https://www.openstreetmap.org/way/28319635) |
| `seg_f050f8204fbed9a3` | – | motorway_link | 262 | keine HVS | 0.42 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561409,5944601]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.646566/9.928998) | [Way](https://www.openstreetmap.org/way/276183952) |
| `seg_f3e461dd69e75e50` | – | motorway_link | 342 | keine HVS | 0.39 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561147,5938984]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.596121/9.923926) | [Way](https://www.openstreetmap.org/way/654215500) |
| `seg_fa4a0341a23f1f28` | – | motorway | 15 | keine HVS | 0.35 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559840,5941660]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620323/9.904702) | [Way](https://www.openstreetmap.org/way/10621045) |
| `seg_fa8172b9922d7535` | – | motorway | 214 | keine HVS | 0.34 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561493,5944662]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.647107/9.930279) | [Way](https://www.openstreetmap.org/way/682144625) |
| `seg_fa95ba685cc08de6` | – | motorway_link | 24 | keine HVS | 0.24 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561055,5943241]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.634386/9.923377) | [Way](https://www.openstreetmap.org/way/760656564) |

### GOW50 (30 von 281)

| segment_id | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_15f35a37699009b9` | Garstedter Weg | secondary | 35 | HVS | 0.67 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563172,5942142]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.624262/9.955160) | [Way](https://www.openstreetmap.org/way/159656519) |
| `seg_1659af0d3641ed9b` | Hoheluftchaussee | primary | 31 | HVS | 0.89 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564122,5937897]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.585996/9.968655) | [Way](https://www.openstreetmap.org/way/239293568) |
| `seg_22810a73805eeed3` | Garstedter Weg | secondary | 147 | HVS | 0.73 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564345,5944351]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.643973/9.973344) | [Way](https://www.openstreetmap.org/way/1302476474) |
| `seg_248286f0d1db813a` | Friedrich-Ebert-Straße | primary | 36 | HVS | 0.89 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561929,5942387]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.626611/9.936413) | [Way](https://www.openstreetmap.org/way/674053445) |
| `seg_295e7394e2c330ae` | Osterfeldstraße | primary | 18 | HVS | 0.92 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564043,5939353]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599091/9.967751) | [Way](https://www.openstreetmap.org/way/143962001) |
| `seg_29703de6753c43dd` | Holsteiner Chaussee | primary | 23 | HVS | 0.69 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559861,5940507]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.609953/9.904798) | [Way](https://www.openstreetmap.org/way/940084044) |
| `seg_2b98581e20649c08` | Holsteiner Chaussee | primary | 180 | HVS | 0.67 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560219,5943637]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.638047/9.910810) | [Way](https://www.openstreetmap.org/way/30338973) |
| `seg_2c005710075de192` | Holsteiner Chaussee | primary | 37 | HVS | 0.46 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560241,5943121]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633406/9.911033) | [Way](https://www.openstreetmap.org/way/945786824) |
| `seg_34cb8dc4a7b0d83d` | Kollaustraße | primary | 11 | HVS | 0.76 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563667,5939826]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603383/9.962177) | [Way](https://www.openstreetmap.org/way/650779301) |
| `seg_41b6123e83bbf1e6` | Kieler Straße | primary | 266 | HVS | 0.76 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560972,5939120]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.597363/9.921309) | [Way](https://www.openstreetmap.org/way/239301560) |
| `seg_41e4edeb0964942f` | Holsteiner Chaussee | primary | 39 | HVS | 0.76 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559855,5940463]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.609559/9.904696) | [Way](https://www.openstreetmap.org/way/940084044) |
| `seg_50a0dd7c3e25a0bf` | Elbgaustraße | primary | 71 | HVS | 0.78 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559219,5939839]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.604021/9.894970) | [Way](https://www.openstreetmap.org/way/1497087240) |
| `seg_5ad31111ea13876d` | Rothenbaumchaussee | secondary | 78 | HVS | 0.55 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565573,5935210]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.561667/9.990000) | [Way](https://www.openstreetmap.org/way/156559302) |
| `seg_5ecf65f266026be9` | Garstedter Weg | secondary | 6 | HVS | 0.72 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564082,5943717]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.638301/9.969240) | [Way](https://www.openstreetmap.org/way/1302476475) |
| `seg_5efa89ba554e8c48` | Osterfeldstraße | primary | 121 | HVS | 0.91 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564360,5939290]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598487/9.972529) | [Way](https://www.openstreetmap.org/way/39965326) |
| `seg_723827f8bd512c15` | Kieler Straße | primary | 382 | HVS | 0.79 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562057,5936924]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.577495/9.937263) | [Way](https://www.openstreetmap.org/way/1167433312) |
| `seg_7699420b5ae1b114` | Kollaustraße | primary | 106 | HVS | 0.64 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563642,5939923]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.604261/9.961811) | [Way](https://www.openstreetmap.org/way/650779308) |
| `seg_81b5bf7664aabfe7` | Garstedter Weg | secondary | 46 | HVS | 0.73 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564391,5944436]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.644732/9.974061) | [Way](https://www.openstreetmap.org/way/601252767) |
| `seg_8416b30305e42774` | Kollaustraße | primary | 221 | HVS | 0.96 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563082,5940858]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.612728/9.953536) | [Way](https://www.openstreetmap.org/way/1561698173) |
| `seg_9be79d5e9ac076f4` | Oldesloer Straße | secondary | 207 | HVS | 0.74 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561311,5944136]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.642402/9.927425) | [Way](https://www.openstreetmap.org/way/831737839) |
| `seg_9f9f90637978a3ca` | Swebenweg | primary | 969 | HVS | 0.93 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563811,5944599]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.646267/9.965329) | [Way](https://www.openstreetmap.org/way/220656006) |
| `seg_a104f2f196416623` | Holsteiner Chaussee | primary | 14 | HVS | 0.64 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560079,5941737]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620986/9.908331) | [Way](https://www.openstreetmap.org/way/532673285) |
| `seg_a7ff7844fd03defb` | Garstedter Weg | secondary | 58 | HVS | 0.72 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564420,5944479]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645114/9.974513) | [Way](https://www.openstreetmap.org/way/411929772) |
| `seg_a91a98beb1151546` | Garstedter Weg | secondary_link | 34 | HVS | 0.50 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564444,5944534]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645601/9.974884) | [Way](https://www.openstreetmap.org/way/42412602) |
| `seg_b07e654a80e1fd9b` | Klosterstern | secondary | 15 | HVS | 0.53 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565454,5937392]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.581289/9.988656) | [Way](https://www.openstreetmap.org/way/249820594) |
| `seg_b431be3dae18e6ed` | Julius-Vosseler-Straße | primary | 13 | HVS | 0.94 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563028,5939294]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598686/9.952408) | [Way](https://www.openstreetmap.org/way/886260309) |
| `seg_c7f4629a10ff4c78` | Julius-Vosseler-Straße | primary | 80 | HVS | 0.92 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563066,5939314]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598859/9.952982) | [Way](https://www.openstreetmap.org/way/912126028) |
| `seg_d4c1d055caa52398` | Holsteiner Chaussee | primary | 180 | HVS | 0.68 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560260,5943372]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.635660/9.911382) | [Way](https://www.openstreetmap.org/way/30338973) |
| `seg_d6b8ba8c88576562` | Kieler Straße | primary | 6 | HVS | 0.86 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560207,5939887]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.604339/9.909903) | [Way](https://www.openstreetmap.org/way/239301547) |
| `seg_faddc467213f0678` | Binsbarg | primary | 31 | HVS | 0.59 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560832,5938394]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.590855/9.919062) | [Way](https://www.openstreetmap.org/way/1377206755) |

### GOW30 (30 von 514)

| segment_id | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_1043561df8d1bb0c` | Kieler Straße | primary | 284 | HVS | 0.95 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561331,5938724]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.593763/9.926664) | [Way](https://www.openstreetmap.org/way/395002918) |
| `seg_1c7a855263671925` | Rentzelstraße | secondary | 42 | HVS | 0.74 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564790,5935615]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565399/9.978266) | [Way](https://www.openstreetmap.org/way/54231215) |
| `seg_24698eade3b4929f` | Papenreye | secondary | 36 | HVS | 0.65 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563255,5940745]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.611691/9.956138) | [Way](https://www.openstreetmap.org/way/1113387692) |
| `seg_25d1ac9c3e551005` | Volksparkstraße | primary | 29 | HVS | 0.74 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561437,5938559]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592261/9.928222) | [Way](https://www.openstreetmap.org/way/791191448) |
| `seg_4ac3dcd2f68d61fb` | Grindelberg / Hoheluftchaussee | primary | 212 | HVS | 0.88 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564647,5937025]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578096/9.976403) | [Way](https://www.openstreetmap.org/way/82312392) |
| `seg_541910afbd7378c3` | Siemersplatz | primary | 10 | HVS | 0.91 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563779,5939433]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599842/9.963786) | [Way](https://www.openstreetmap.org/way/27432671) |
| `seg_54d63491ca456e28` | Kollaustraße | primary | 44 | HVS | 0.94 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563749,5939497]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600416/9.963349) | [Way](https://www.openstreetmap.org/way/144246643) |
| `seg_578139368c8c0aa9` | Alsterglacis | primary | 14 | HVS | 0.98 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565617,5935080]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.560494/9.990643) | [Way](https://www.openstreetmap.org/way/24483185) |
| `seg_67455920d2b92298` | Niendorfer Marktplatz | primary | 20 | HVS | 0.94 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562879,5941360]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.617271/9.950580) | [Way](https://www.openstreetmap.org/way/30339611) |
| `seg_68a9851f7fc8ff88` | St. Benedictstraße | secondary | 26 | HVS | 0.64 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565815,5937621]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.583306/9.994158) | [Way](https://www.openstreetmap.org/way/30412060) |
| `seg_690b9052dc5e4fa4` | Kollaustraße | primary | 58 | HVS | 0.89 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563352,5940623]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.610587/9.957577) | [Way](https://www.openstreetmap.org/way/586235751) |
| `seg_6b09ff03f5982bd0` | Rentzelstraße | secondary | 71 | HVS | 0.74 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564740,5935531]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.564654/9.977497) | [Way](https://www.openstreetmap.org/way/673236747) |
| `seg_6e307a31eec2ef04` | Eimsbütteler Marktplatz | primary | 238 | HVS | 0.93 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562703,5936474]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573380/9.946930) | [Way](https://www.openstreetmap.org/way/143710291) |
| `seg_75c93e2d943dc0fc` | Friedrich-Ebert-Straße | primary | 298 | HVS | 0.89 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562182,5942085]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.623864/9.940186) | [Way](https://www.openstreetmap.org/way/1119366814) |
| `seg_7dd6653617143e92` | Altonaer Straße | secondary | 63 | HVS | 0.52 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563934,5935592]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565302/9.965345) | [Way](https://www.openstreetmap.org/way/919823391) |
| `seg_7edb4e1317354fe9` | Marek-James-Straße | secondary | 41 | HVS | 0.61 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560055,5944508]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645888/9.908491) | [Way](https://www.openstreetmap.org/way/958530189) |
| `seg_7ff1a23fcfbbc3f1` | Lokstedter Steindamm | primary | 151 | HVS | 0.56 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564080,5938194]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.588668/9.968080) | [Way](https://www.openstreetmap.org/way/51255675) |
| `seg_80c55763f2ddca8f` | Rothenbaumchaussee | secondary | 265 | HVS | 0.78 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565459,5936040]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.569136/9.988456) | [Way](https://www.openstreetmap.org/way/1210826072) |
| `seg_99cfb30d958c8bb5` | Niendorfer Marktplatz | primary | 40 | HVS | 0.86 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562872,5941389]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.617531/9.950477) | [Way](https://www.openstreetmap.org/way/30505764) |
| `seg_9a55ef119436ad6e` | Grindelberg | primary | 233 | HVS | 0.82 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564763,5936852]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576522/9.978111) | [Way](https://www.openstreetmap.org/way/391821221) |
| `seg_a032dc90cb0e15fe` | Grindelallee | primary | 50 | HVS | 0.84 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565051,5935673]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565893/9.982217) | [Way](https://www.openstreetmap.org/way/49056723) |
| `seg_b4adf4a889ba92e4` | Beim Schlump | secondary | 90 | HVS | 0.79 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564472,5936006]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.568958/9.973547) | [Way](https://www.openstreetmap.org/way/216631360) |
| `seg_bd6eec1ce3ea44ae` | Kollaustraße | primary | 34 | HVS | 0.94 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563731,5939531]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600726/9.963085) | [Way](https://www.openstreetmap.org/way/650779279) |
| `seg_bfb9697b7b847eb5` | Langenfelder Damm | tertiary | 154 | keine HVS | 0.64 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562267,5937083]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578898/9.940470) | [Way](https://www.openstreetmap.org/way/27308882) |
| `seg_c28aa1753bd31112` | – | primary_link | 88 | HVS | 0.97 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561436,5938592]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592565/9.928214) | [Way](https://www.openstreetmap.org/way/692691300) |
| `seg_cdea3a610059d1c7` | Hoheluftchaussee | primary | 202 | HVS | 0.89 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564137,5937783]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.584971/9.968859) | [Way](https://www.openstreetmap.org/way/218907472) |
| `seg_cf12420582b72eaf` | Fruchtallee | primary | 34 | HVS | 0.95 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562905,5936409]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572771/9.949974) | [Way](https://www.openstreetmap.org/way/362847063) |
| `seg_ef7e15e1eac9ad21` | Elbgaustraße | primary | 50 | HVS | 0.78 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559455,5940014]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.605568/9.898559) | [Way](https://www.openstreetmap.org/way/1571069722) |
| `seg_f00db1ded79fd6db` | Hallerstraße | secondary | 52 | HVS | 0.70 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564828,5936399]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572444/9.979005) | [Way](https://www.openstreetmap.org/way/114928659) |
| `seg_ffaa1413c5de3352` | Marek-James-Straße | secondary | 36 | HVS | 0.63 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560093,5944512]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645926/9.909075) | [Way](https://www.openstreetmap.org/way/1082687253) |

### ETW30 (30 von 2835)

| segment_id | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_123ea820645b953e` | Halstenbeker Straße | tertiary | 123 | keine HVS | 0.57 | niedrig | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560076,5942407]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.627002/9.908415) | [Way](https://www.openstreetmap.org/way/42734216) |
| `seg_1701d528e894441b` | Sethweg | residential | 147 | keine HVS | 0.21 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562198,5943000]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632092/9.940615) | [Way](https://www.openstreetmap.org/way/1450394478) |
| `seg_20f02b4121e8bcf3` | Deepenstöcken | residential | 20 | keine HVS | 0.19 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563080,5937735]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.584663/9.952875) | [Way](https://www.openstreetmap.org/way/23064159) |
| `seg_28abaec6bf420cf9` | Ottensener Straße | residential | 12 | keine HVS | 0.08 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560121,5938467]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591587/9.908334) | [Way](https://www.openstreetmap.org/way/629594753) |
| `seg_325fa9662ba22bbb` | Teinstücken | residential | 267 | keine HVS | 0.09 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560325,5939440]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600309/9.911602) | [Way](https://www.openstreetmap.org/way/1094423060) |
| `seg_32cefe02fce0219d` | Immenweide / Krupunder Weg | residential | 401 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558655,5941316]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.617360/9.886721) | [Way](https://www.openstreetmap.org/way/986306845) |
| `seg_3820f0ed15e9065f` | Riekbornweg | residential | 413 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560553,5943148]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633615/9.915770) | [Way](https://www.openstreetmap.org/way/149136697) |
| `seg_3acaec28c563607d` | Bei der Pulvermühle | unclassified | 107 | keine HVS | 0.26 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563898,5940033]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.605218/9.965706) | [Way](https://www.openstreetmap.org/way/146342884) |
| `seg_507493056c8510c0` | Süntelstraße | tertiary | 31 | keine HVS | 0.53 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560014,5943015]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632474/9.907585) | [Way](https://www.openstreetmap.org/way/936662870) |
| `seg_5a61d79d7aa3d25f` | Volksparkstraße | residential | 83 | keine HVS | 0.10 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560910,5938460]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591439/9.920239) | [Way](https://www.openstreetmap.org/way/5015684) |
| `seg_5c33c97ed770ee7a` | Gneisenaustraße | residential | 386 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564122,5937038]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578275/9.968474) | [Way](https://www.openstreetmap.org/way/137159045) |
| `seg_60963b253003b120` | Rellinger Straße | residential | 69 | keine HVS | 0.16 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562309,5936734]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575764/9.941037) | [Way](https://www.openstreetmap.org/way/23099392) |
| `seg_86f68500f5b2695d` | Hochallee | tertiary | 183 | keine HVS | 0.29 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565299,5936515]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573427/9.986143) | [Way](https://www.openstreetmap.org/way/137154558) |
| `seg_8e5051aaffa25eb6` | Niendorfer Straße | secondary | 177 | keine HVS | 0.57 | niedrig | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563285,5940194]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.606743/9.956475) | [Way](https://www.openstreetmap.org/way/23118430) |
| `seg_8f5feb8e7a02565a` | Julius-Vosseler-Straße | residential | 219 | keine HVS | 0.07 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562845,5937980]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.586895/9.949384) | [Way](https://www.openstreetmap.org/way/23064063) |
| `seg_961dd07097701e95` | Quedlinburger Weg | tertiary | 54 | keine HVS | 0.52 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562434,5943540]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.636915/9.944292) | [Way](https://www.openstreetmap.org/way/1166223807) |
| `seg_9e049b271856659d` | Försterweg | residential | 79 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561793,5937144]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.579508/9.933326) | [Way](https://www.openstreetmap.org/way/145693815) |
| `seg_a0111f695ea685b3` | Heidlohstraße | secondary | 273 | keine HVS | 0.57 | niedrig | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560497,5942487]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.627680/9.914793) | [Way](https://www.openstreetmap.org/way/4228152) |
| `seg_ad9741851cf7c4c8` | Niendorfer Gehege | tertiary | 26 | keine HVS | 0.26 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562284,5941305]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.616844/9.941571) | [Way](https://www.openstreetmap.org/way/127717730) |
| `seg_b74752d6cc20fe72` | Wullenweberstieg | residential | 133 | keine HVS | 0.10 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559794,5940791]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.612511/9.903840) | [Way](https://www.openstreetmap.org/way/7396354) |
| `seg_bcfdbddb8ed23419` | Lohkoppelweg | residential | 137 | keine HVS | 0.10 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563399,5938515]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591636/9.957858) | [Way](https://www.openstreetmap.org/way/683687173) |
| `seg_c498c64311e941d2` | Wrangelstraße | residential | 53 | keine HVS | 0.08 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563992,5937539]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582797/9.966610) | [Way](https://www.openstreetmap.org/way/54461833) |
| `seg_c8294c7fc1117801` | Bellealliancestraße | residential | 68 | keine HVS | 0.20 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563509,5935852]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567692/9.958970) | [Way](https://www.openstreetmap.org/way/137473731) |
| `seg_cf3992f4bf1f96ba` | Furtweg | residential | 117 | keine HVS | 0.23 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559859,5939714]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.602828/9.904605) | [Way](https://www.openstreetmap.org/way/28175311) |
| `seg_d60dc732c55af189` | Klosterallee | residential | 25 | keine HVS | 0.17 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564878,5937286]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580407/9.979949) | [Way](https://www.openstreetmap.org/way/48759572) |
| `seg_d65ec152dacebb8b` | Gutenbergstraße | tertiary | 170 | keine HVS | 0.26 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561298,5938043]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.587643/9.926031) | [Way](https://www.openstreetmap.org/way/1546589779) |
| `seg_da60f1b79d3e3c53` | Zweigweg | residential | 115 | keine HVS | 0.21 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558901,5940874]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.613360/9.890353) | [Way](https://www.openstreetmap.org/way/4974271) |
| `seg_da958c8d43813b29` | Auf dem Kollauer Hof | residential | 84 | keine HVS | 0.23 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563640,5940171]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.606489/9.961837) | [Way](https://www.openstreetmap.org/way/321428137) |
| `seg_e68233bbf574820b` | Nonnenstieg | residential | 192 | keine HVS | 0.06 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565580,5937613]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.583263/9.990609) | [Way](https://www.openstreetmap.org/way/136965464) |
| `seg_fc1fd071e2dd14f8` | Behrmannplatz | residential | 42 | keine HVS | 0.29 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563438,5939380]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599406/9.958619) | [Way](https://www.openstreetmap.org/way/912126015) |

### ETW_ERF (30 von 148)

| segment_id | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_0391547b8f09a389` | Eidelstedter Weg | living_street | 84 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563330,5937301]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580739/9.956567) | [Way](https://www.openstreetmap.org/way/144069404) |
| `seg_0b594a49dab7ece1` | Moorflagen | living_street | 49 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562504,5944290]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.643645/9.945496) | [Way](https://www.openstreetmap.org/way/26783778) |
| `seg_2fbde63c63a92b13` | – | pedestrian | 11 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562546,5936756]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575934/9.944619) | [Way](https://www.openstreetmap.org/way/1084007706) |
| `seg_38926833099b9b94` | Schlüterstraße | pedestrian | 77 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565334,5935803]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567025/9.986511) | [Way](https://www.openstreetmap.org/way/738633624) |
| `seg_3a1af222674e6102` | Tibarg | pedestrian | 56 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562932,5941642]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.619793/9.951437) | [Way](https://www.openstreetmap.org/way/1157929376) |
| `seg_3a56764a0a82b909` | Tibarg | pedestrian | 74 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563027,5941735]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620624/9.952890) | [Way](https://www.openstreetmap.org/way/124212740) |
| `seg_4e321157df03efec` | Assorweg | living_street | 57 | keine HVS | 0.22 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559467,5942988]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632298/9.899312) | [Way](https://www.openstreetmap.org/way/57841711) |
| `seg_4ecc0306b23e1cdb` | Ohmoorring | living_street | 15 | keine HVS | 0.03 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563641,5943640]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.637669/9.962551) | [Way](https://www.openstreetmap.org/way/432988854) |
| `seg_56c79720bcb19053` | Am Ziegelteich | living_street | 260 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561722,5936852]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576891/9.932198) | [Way](https://www.openstreetmap.org/way/15089591) |
| `seg_5f7db3bd903c7eea` | Klabautermannweg | living_street | 113 | keine HVS | 0.04 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561084,5944644]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.646994/9.924083) | [Way](https://www.openstreetmap.org/way/593924194) |
| `seg_68001cd5805129fc` | Martin-Luther-King-Platz | pedestrian | 7 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564815,5935852]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567531/9.978692) | [Way](https://www.openstreetmap.org/way/309124580) |
| `seg_8086824462c8d60c` | Harvestehuder Stieg | living_street | 110 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566017,5936803]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575928/9.997045) | [Way](https://www.openstreetmap.org/way/119223002) |
| `seg_82cdaef5779ebd8c` | Martin-Luther-King-Platz | pedestrian | 73 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564779,5935834]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567375/9.978145) | [Way](https://www.openstreetmap.org/way/316524933) |
| `seg_846af48be7c90be4` | Tibarg | pedestrian | 5 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562933,5941616]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.619558/9.951447) | [Way](https://www.openstreetmap.org/way/410582641) |
| `seg_92b23473a37a141f` | Tibarg | pedestrian | 16 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562942,5941676]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620104/9.951589) | [Way](https://www.openstreetmap.org/way/1157929376) |
| `seg_93910bac92b79295` | Tibarg | pedestrian | 14 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562947,5941667]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620020/9.951659) | [Way](https://www.openstreetmap.org/way/913610316) |
| `seg_a06cc4b0c4a2c082` | Am Ziegelteich | living_street | 16 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561736,5936715]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575653/9.932382) | [Way](https://www.openstreetmap.org/way/1078034982) |
| `seg_ad15c337575ac5e6` | Albertinenstieg | living_street | 37 | keine HVS | 0.22 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559468,5943125]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633527/9.899357) | [Way](https://www.openstreetmap.org/way/57841698) |
| `seg_af9be1d9af7e7658` | Tibarg | pedestrian | 9 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562992,5941882]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.621944/9.952380) | [Way](https://www.openstreetmap.org/way/48055635) |
| `seg_c247052cf4a16cdf` | Anne-Barth-Weg | living_street | 65 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562005,5937583]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.583431/9.936612) | [Way](https://www.openstreetmap.org/way/145693785) |
| `seg_cc26a0f235ad72cf` | Kaiser-Friedrich-Ufer | pedestrian | 38 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563987,5936506]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573512/9.966326) | [Way](https://www.openstreetmap.org/way/24846541) |
| `seg_ceaa68b44f1147ce` | Kielortallee | living_street | 52 | keine HVS | 0.05 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564541,5936281]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571419/9.974644) | [Way](https://www.openstreetmap.org/way/8298715) |
| `seg_cfaff741421598ca` | Klabautermannweg | living_street | 121 | keine HVS | 0.20 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561021,5944701]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.647510/9.923139) | [Way](https://www.openstreetmap.org/way/593924194) |
| `seg_d45acd6f91b57115` | – | pedestrian | 97 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562662,5943933]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.640416/9.947816) | [Way](https://www.openstreetmap.org/way/1134804549) |
| `seg_dd0dec4dda7685d0` | Moorflagen | pedestrian | 12 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562616,5943915]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.640264/9.947120) | [Way](https://www.openstreetmap.org/way/26783796) |
| `seg_de6e32489eec31b6` | Martin-Luther-King-Platz | pedestrian | 25 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564807,5935862]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567622/9.978570) | [Way](https://www.openstreetmap.org/way/316524933) |
| `seg_e71eb4435aed754a` | Albertinenstieg | living_street | 36 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559426,5943160]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633845/9.898731) | [Way](https://www.openstreetmap.org/way/57841698) |
| `seg_e90d0aac3b546d96` | Lindenallee | living_street | 212 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563584,5935770]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.566945/9.960088) | [Way](https://www.openstreetmap.org/way/137037876) |
| `seg_e9ec19be27f8bca8` | – | pedestrian | 4 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563038,5936799]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576257/9.952058) | [Way](https://www.openstreetmap.org/way/1293310387) |
| `seg_efdf395cc6f52c06` | Lohwurt | living_street | 100 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559603,5940312]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.608228/9.900856) | [Way](https://www.openstreetmap.org/way/33065799) |

### GOW80

_keine Abschnitte im Bezirk_

### ETW60

_keine Abschnitte im Bezirk_

## Lizenz

Abschnitte und Merkmale aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale (Tempo, Verkehrsmengen, ALKIS): Freie und Hansestadt Hamburg, dl-de/by-2.0; Busfahrten: HVV, dl-de/by-2.0; Einwohner: Zensus 2022, dl-de/by-2.0. Orthophotos: LGV Hamburg, dl-de/by-2.0. Panoramax-Bilder: Lizenz je Bild.
