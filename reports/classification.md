# Klassifikationsbericht – Stufe 5

Erzeugt: 2026-11-04T20:36:46+00:00 von `pipeline/s05_classify.py`, rules.yaml 0.12.0. Nicht amtlicher Entwurf: Die Automatik schlägt vor, Menschen entscheiden (overrides/overrides.csv).

## Kennzahlen

- Klassifiziert: 4 947 Abschnitte im Arbeitsgebiet (573.4 km), davon 4 004 im Bezirk Eimsbüttel (470.4 km). Abschnitte außerhalb des Arbeitsgebiets bleiben leer.
- Defaults aus C-MISS-01 genutzt: crossing_demand 100.0 %, outside_builtup_area 100.0 %, override_school_street 100.0 % der Abschnitte im Arbeitsgebiet.

### km je Kategorie

| Kategorie | Bezeichnung | Eimsbüttel km | Anteil | Arbeitsgebiet km | Anteil | Abschnitte (Arbeitsgebiet) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| SW | Schnellverkehrsstraße | 25.6 | 5.4 % | 28.4 | 5.0 % | 120 |
| GOW50 | Stadtmagistrale | 30.9 | 6.6 % | 38.9 | 6.8 % | 385 |
| GOW30 | Stadtstraße 30 | 50.5 | 10.7 % | 58.4 | 10.2 % | 616 |
| ETW30 | Quartiersstraße | 354.5 | 75.4 % | 437.2 | 76.2 % | 3 663 |
| ETW_ERF | Aufenthaltsstraße | 9.0 | 1.9 % | 10.6 | 1.8 % | 163 |
| GOW80 | Landstraße (Verbindung) | 0.0 | 0.0 % | 0.0 | 0.0 % | 0 |
| ETW60 | Landstraße (Erschließung) | 0.0 | 0.0 % | 0.0 | 0.0 % | 0 |

### confidence (Anteil der Länge im Arbeitsgebiet)

| Kategorie | hoch | mittel | niedrig |
| --- | ---: | ---: | ---: |
| SW | 100.0 % | 0.0 % | 0.0 % |
| GOW50 | 0.0 % | 36.7 % | 63.3 % |
| GOW30 | 0.0 % | 88.5 % | 11.5 % |
| ETW30 | 0.0 % | 94.7 % | 5.3 % |
| ETW_ERF | 0.0 % | 100.0 % | 0.0 % |
| alle | 5.0 % | 85.6 % | 9.5 % |

Häufigste Gründe für eine herabgesetzte confidence (Abschnitte, Mehrfachnennung):

| Grund | Abschnitte |
| --- | ---: |
| `fallback:outside_builtup_area` | 4 827 |
| `fallback:override_school_street` | 4 664 |
| `fallback:in_hvs` | 3 838 |
| `fallback:conn_score` | 3 762 |
| `fallback:schools_or_kitas_within_m` | 598 |
| `fallback:crossing_demand` | 385 |
| `nahe_schwelle:conn_score~thresholds.conn_gow` | 302 |
| `fehlt:shop_frontage_share` | 254 |
| `fehlt:width_p10_m` | 67 |
| `nahe_schwelle:schools_or_kitas_within_m~thresholds.sensitive_radius` | 65 |
| `fehlt:separated_cycle_track_present` | 15 |
| `nahe_schwelle:shop_frontage_share~thresholds.frontage` | 5 |

`fehlt:x` = Eingangswert fehlt und entscheidet; `nahe_schwelle:x~s` = Wert innerhalb ±10 % der Schwelle; `fallback:x` = Fallback-Quelle oder Default (C-CONF-01).

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| Goldene Fälle grün | ok | 27/27 |
| Jeder Abschnitt im Arbeitsgebiet hat eine Kategorie | ok | 4947 klassifiziert, 31579 außerhalb (leer) |
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
| SW | 0.3 | 25.3 | 0.0 | 25.6 | 0.4 % |
| GOW50 | 30.6 | 0.2 | 0.0 | 30.9 | 39.4 % |
| GOW30 | 46.8 | 3.6 | 0.0 | 50.5 | 60.2 % |
| ETW30 | 0.0 | 354.5 | 0.0 | 354.5 | 0.0 % |
| ETW_ERF | 0.0 | 9.0 | 0.0 | 9.0 | 0.0 % |
| **Summe** | 77.8 | 392.6 | 0.0 | 470.4 | |

## Kreuztabelle Soll × HVS – Arbeitsgebiet (km)

| Soll | HVS km | keine HVS km | unbekannt km | Summe km | Anteil HVS-km |
| --- | ---: | ---: | ---: | ---: | ---: |
| SW | 0.4 | 28.0 | 0.0 | 28.4 | 0.4 % |
| GOW50 | 38.2 | 0.6 | 0.0 | 38.9 | 41.4 % |
| GOW30 | 53.7 | 4.7 | 0.0 | 58.4 | 58.2 % |
| ETW30 | 0.0 | 437.2 | 0.0 | 437.2 | 0.0 % |
| ETW_ERF | 0.0 | 10.6 | 0.0 | 10.6 | 0.0 % |
| **Summe** | 92.3 | 481.1 | 0.0 | 573.4 | |

### HVS-km je Bezirk (Arbeitsgebiet, Bezirke nur mit ihrem Anteil im Arbeitsgebiet)

| Bezirk | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | GOW80 | ETW60 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 0.0 | 3.4 | 1.8 | 0.0 | 0.0 | 0.0 | 0.0 |
| Eimsbüttel | 0.3 | 30.6 | 46.8 | 0.0 | 0.0 | 0.0 | 0.0 |
| Hamburg-Mitte | 0.0 | 2.1 | 2.5 | 0.0 | 0.0 | 0.0 | 0.0 |
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
| Eimsbüttel | Kieler Straße | primary | 1 | 0.0 | 0.63–0.63 | 1 | `seg_596c7377b0aff893` |
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
| `seg_0d04aeab169d1db6` | – | motorway_link | 36 | keine HVS | 0.25 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561096,5938963]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.595940/9.923148) | [Way](https://www.openstreetmap.org/way/1145434376) |
| `seg_18898a328316b431` | – | motorway_link | 35 | keine HVS | 0.23 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560012,5941411]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.618067/9.907242) | [Way](https://www.openstreetmap.org/way/526877185) |
| `seg_1dcaac6278efae03` | – | motorway_link | 145 | keine HVS | 0.42 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560193,5941346]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.617456/9.909974) | [Way](https://www.openstreetmap.org/way/37813970) |
| `seg_1dcc1de7b7e38c6f` | – | motorway_link | 54 | keine HVS | 0.16 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561409,5944438]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645107/9.928969) | [Way](https://www.openstreetmap.org/way/10713029) |
| `seg_2e4755bd181b2cb1` | – | motorway_link | 50 | keine HVS | 0.26 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561057,5938950]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.595827/9.922557) | [Way](https://www.openstreetmap.org/way/329485054) |
| `seg_44cb1a0e3ae2aec8` | – | motorway_link | 61 | keine HVS | 0.24 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561570,5944493]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645577/9.931402) | [Way](https://www.openstreetmap.org/way/323606086) |
| `seg_4b05c6d22ed6c74c` | – | motorway_link | 47 | keine HVS | 0.09 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561155,5943156]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633614/9.924870) | [Way](https://www.openstreetmap.org/way/323606076) |
| `seg_4bf2d90852297d5b` | – | motorway | 546 | keine HVS | 0.53 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561080,5943298]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.634901/9.923767) | [Way](https://www.openstreetmap.org/way/323606066) |
| `seg_4e12950aa3e1a431` | – | motorway | 221 | keine HVS | 0.34 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559747,5941740]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.621046/9.903305) | [Way](https://www.openstreetmap.org/way/10621048) |
| `seg_53288ca455b0fa7d` | – | motorway_link | 101 | keine HVS | 0.05 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561399,5944414]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.644888/9.928801) | [Way](https://www.openstreetmap.org/way/1128088138) |
| `seg_6428c75993e67a8f` | – | motorway_link | 278 | keine HVS | 0.09 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561100,5943433]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.636107/9.924094) | [Way](https://www.openstreetmap.org/way/10713261) |
| `seg_ae7935402e3a7ab8` | – | motorway_link | 18 | keine HVS | 0.05 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561148,5943125]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633336/9.924754) | [Way](https://www.openstreetmap.org/way/103948925) |
| `seg_af4b2e547be7d9ca` | – | motorway_link | 369 | keine HVS | 0.28 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560940,5938822]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.594688/9.920777) | [Way](https://www.openstreetmap.org/way/3128030) |
| `seg_b9cd9c6b834f7948` | – | motorway_link | 48 | keine HVS | 0.07 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561143,5943167]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633712/9.924688) | [Way](https://www.openstreetmap.org/way/10713259) |
| `seg_c0bbcc80b6c2e5d9` | – | motorway_link | 59 | keine HVS | 0.32 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560056,5941651]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620211/9.907960) | [Way](https://www.openstreetmap.org/way/127628264) |
| `seg_c9517409770da0de` | – | motorway | 246 | keine HVS | 0.53 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561121,5943390]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.635722/9.924401) | [Way](https://www.openstreetmap.org/way/296326689) |
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
| `seg_fa8172b9922d7535` | – | motorway | 214 | keine HVS | 0.33 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561493,5944662]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.647107/9.930279) | [Way](https://www.openstreetmap.org/way/682144625) |
| `seg_fa95ba685cc08de6` | – | motorway_link | 24 | keine HVS | 0.23 | hoch | C-SW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561055,5943241]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.634386/9.923377) | [Way](https://www.openstreetmap.org/way/760656564) |

### GOW50 (30 von 295)

| segment_id | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_13d3c4d5358ddc41` | Kieler Straße | primary | 11 | HVS | 0.91 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559894,5940289]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.607989/9.905244) | [Way](https://www.openstreetmap.org/way/1429699464) |
| `seg_145ef7ddda9b1c2b` | Grindelallee | primary | 13 | HVS | 0.84 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565200,5935471]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.564063/9.984424) | [Way](https://www.openstreetmap.org/way/391787290) |
| `seg_1e7079b3332dae61` | Hoheluftchaussee | primary | 11 | HVS | 0.88 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564575,5937110]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578866/9.975335) | [Way](https://www.openstreetmap.org/way/391821253) |
| `seg_240edc3089b2fc7c` | Kieler Straße | primary | 101 | HVS | 0.86 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562110,5936796]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576343/9.938046) | [Way](https://www.openstreetmap.org/way/733544407) |
| `seg_28c898a73895f770` | Rothenbaumchaussee | secondary | 8 | HVS | 0.63 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565563,5935187]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.561458/9.989851) | [Way](https://www.openstreetmap.org/way/35170417) |
| `seg_29471d27244f53ca` | Oldesloer Straße | primary | 156 | HVS | 0.33 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561483,5944478]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645456/9.930086) | [Way](https://www.openstreetmap.org/way/46742300) |
| `seg_296482f204d6c471` | Rentzelstraße | secondary | 32 | HVS | 0.64 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564726,5935467]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.564082/9.977274) | [Way](https://www.openstreetmap.org/way/521045491) |
| `seg_29703de6753c43dd` | Holsteiner Chaussee | primary | 23 | HVS | 0.68 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559861,5940507]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.609953/9.904798) | [Way](https://www.openstreetmap.org/way/940084044) |
| `seg_3210bd89f2c3fbbf` | Holsteiner Chaussee | primary | 286 | HVS | 0.66 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560166,5943890]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.640323/9.910051) | [Way](https://www.openstreetmap.org/way/964082694) |
| `seg_40fa35f416c48fad` | Rentzelstraße / Messeplatz | secondary | 37 | HVS | 0.79 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564706,5935440]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.563841/9.976966) | [Way](https://www.openstreetmap.org/way/6376884) |
| `seg_41233d444e4d2134` | Julius-Vosseler-Straße | primary | 7 | HVS | 0.92 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563023,5939306]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598788/9.952334) | [Way](https://www.openstreetmap.org/way/886260308) |
| `seg_4e3d304c5fe73729` | Holsteiner Chaussee | primary | 202 | HVS | 0.65 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560115,5944128]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.642473/9.909333) | [Way](https://www.openstreetmap.org/way/593924192) |
| `seg_596c7377b0aff893` | Kieler Straße | primary | 11 | keine HVS | 0.63 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559867,5940375]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.608769/9.904852) | [Way](https://www.openstreetmap.org/way/1429699436) |
| `seg_5c161233de14bd93` | Garstedter Weg | secondary | 86 | HVS | 0.77 | mittel | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563145,5942015]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.623120/9.954731) | [Way](https://www.openstreetmap.org/way/159656520) |
| `seg_5cf917b1a2247075` | Beim Schlump | secondary | 8 | HVS | 0.71 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564800,5936388]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572349/9.978580) | [Way](https://www.openstreetmap.org/way/238921527) |
| `seg_6c5ff477d098e948` | Rothenbaumchaussee | secondary | 58 | HVS | 0.62 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565565,5935219]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.561752/9.989881) | [Way](https://www.openstreetmap.org/way/24288798) |
| `seg_73a63c917350363c` | Schleswiger Damm | secondary | 156 | HVS | 0.70 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560334,5944425]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645117/9.912695) | [Way](https://www.openstreetmap.org/way/3997436) |
| `seg_7716cfb4e94769f3` | Kollaustraße | primary | 87 | HVS | 0.94 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563191,5940751]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.611755/9.955165) | [Way](https://www.openstreetmap.org/way/220515420) |
| `seg_7f22f400ca1eaa04` | Swebenweg | primary | 33 | HVS | 0.72 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564417,5944516]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645448/9.974472) | [Way](https://www.openstreetmap.org/way/129788406) |
| `seg_986d6815deffbfab` | Fruchtallee | primary | 14 | HVS | 0.83 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563320,5936154]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.570426/9.956178) | [Way](https://www.openstreetmap.org/way/80992108) |
| `seg_99c2d726994899d7` | Binsbarg | primary | 13 | HVS | 0.88 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559844,5938515]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592050/9.904153) | [Way](https://www.openstreetmap.org/way/629594744) |
| `seg_9ad9ae63cc5b516d` | Binsbarg | primary | 31 | HVS | 0.74 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560863,5938399]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.590896/9.919519) | [Way](https://www.openstreetmap.org/way/1377206757) |
| `seg_a0de84542f4d9127` | Lokstedter Steindamm | primary | 99 | HVS | 0.88 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564021,5938503]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591450/9.967251) | [Way](https://www.openstreetmap.org/way/1567673937) |
| `seg_a1c261c3793b1841` | Oldesloer Straße | primary_link | 37 | HVS | 0.45 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562675,5944963]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.649672/9.948212) | [Way](https://www.openstreetmap.org/way/210197353) |
| `seg_a91a98beb1151546` | Garstedter Weg | secondary_link | 34 | HVS | 0.49 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564444,5944534]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645601/9.974884) | [Way](https://www.openstreetmap.org/way/42412602) |
| `seg_a9a1b05b643b50d1` | Kollaustraße | primary | 41 | HVS | 0.94 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563687,5939697]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.602222/9.962448) | [Way](https://www.openstreetmap.org/way/1455895049) |
| `seg_bf4ee71728444fba` | Kollaustraße | primary | 42 | HVS | 0.69 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563660,5939852]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603616/9.962078) | [Way](https://www.openstreetmap.org/way/650779300) |
| `seg_cf04be27d428bebd` | Kieler Straße | primary | 71 | HVS | 0.91 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561189,5938856]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.594965/9.924544) | [Way](https://www.openstreetmap.org/way/47135496) |
| `seg_efea8515f1a1109c` | Schleswiger Damm | secondary | 61 | HVS | 0.61 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561000,5943308]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.634995/9.922550) | [Way](https://www.openstreetmap.org/way/23299829) |
| `seg_f699ff93b089d293` | Holstenkamp | secondary | 726 | HVS | 0.69 | niedrig | C-GOW-01 → C-G50-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561655,5936469]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573459/9.931110) | [Way](https://www.openstreetmap.org/way/205384710) |

### GOW30 (30 von 529)

| segment_id | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_0edb2689fcd37b3c` | Friedrich-Ebert-Straße | primary | 130 | HVS | 0.90 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562658,5941517]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.618709/9.947272) | [Way](https://www.openstreetmap.org/way/153842980) |
| `seg_1bcb6ca2b5edd175` | Gärtnerstraße | primary | 160 | HVS | 0.89 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564103,5937661]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.583880/9.968313) | [Way](https://www.openstreetmap.org/way/1525043459) |
| `seg_2328c48d0a05bd24` | Vogt-Wells-Straße | primary | 42 | HVS | 0.96 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563464,5939361]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599231/9.959008) | [Way](https://www.openstreetmap.org/way/912126014) |
| `seg_257fa0dc952d7744` | Klosterstern | secondary | 13 | HVS | 0.48 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565410,5937469]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.581987/9.988011) | [Way](https://www.openstreetmap.org/way/1370385207) |
| `seg_5222f35a8ee6c6e2` | Beim Schlump | secondary | 51 | HVS | 0.79 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564633,5936160]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.570320/9.976003) | [Way](https://www.openstreetmap.org/way/238747025) |
| `seg_52253ca968642117` | Eppendorfer Baum | secondary | 204 | HVS | 0.73 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565297,5937544]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582676/9.986323) | [Way](https://www.openstreetmap.org/way/1144841161) |
| `seg_54e2f881116fa080` | Kieler Straße | primary | 71 | HVS | 0.86 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560359,5939691]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.602567/9.912159) | [Way](https://www.openstreetmap.org/way/28175272) |
| `seg_65d01c37a01d8baf` | Schröderstiftstraße | primary | 210 | HVS | 0.88 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564486,5935663]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565874/9.973681) | [Way](https://www.openstreetmap.org/way/521056836) |
| `seg_6600444efd3d9aa4` | Swebenweg | primary | 45 | HVS | 0.82 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564435,5944538]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645639/9.974750) | [Way](https://www.openstreetmap.org/way/149852883) |
| `seg_66aa2ae45681d992` | Kieler Straße | primary | 8 | HVS | 0.89 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562404,5936397]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572725/9.942395) | [Way](https://www.openstreetmap.org/way/591410904) |
| `seg_690b9052dc5e4fa4` | Kollaustraße | primary | 58 | HVS | 0.89 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563352,5940623]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.610587/9.957577) | [Way](https://www.openstreetmap.org/way/586235751) |
| `seg_6b990f3206989f17` | Schäferkampsallee | primary | 142 | HVS | 0.81 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563918,5936051]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.569431/9.965195) | [Way](https://www.openstreetmap.org/way/30070899) |
| `seg_723a3367966552d2` | Rothenbaumchaussee | secondary | 80 | HVS | 0.78 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565462,5936212]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.570685/9.988529) | [Way](https://www.openstreetmap.org/way/136712399) |
| `seg_7ba9e343e3126b09` | Gärtnerstraße | primary | 31 | HVS | 0.90 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563841,5937257]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580276/9.964280) | [Way](https://www.openstreetmap.org/way/142762605) |
| `seg_7c2753dde5f70932` | Rentzelstraße | secondary | 28 | HVS | 0.48 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564953,5935784]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.566904/9.980756) | [Way](https://www.openstreetmap.org/way/391801522) |
| `seg_7d1275a8ec00b9a1` | Oldesloer Straße | secondary | 401 | HVS | 0.73 | mittel | C-GOW-01 → C-G30-01 → C-G30-02 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561149,5943879]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.640108/9.924923) | [Way](https://www.openstreetmap.org/way/831737839) |
| `seg_80c55763f2ddca8f` | Rothenbaumchaussee | secondary | 265 | HVS | 0.78 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565459,5936040]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.569136/9.988456) | [Way](https://www.openstreetmap.org/way/1210826072) |
| `seg_923fa143b87755f1` | Eimsbütteler Marktplatz | primary | 240 | HVS | 0.76 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562700,5936464]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573291/9.946884) | [Way](https://www.openstreetmap.org/way/1359178748) |
| `seg_9299750046b2e39a` | Eimsbütteler Marktplatz | primary | 130 | HVS | 0.74 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562473,5936398]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572723/9.943437) | [Way](https://www.openstreetmap.org/way/49637391) |
| `seg_99600d5004ffd886` | Lappenbergsallee | tertiary | 48 | keine HVS | 0.64 | niedrig | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562367,5936924]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.577459/9.941955) | [Way](https://www.openstreetmap.org/way/1011480552) |
| `seg_ac99690dc62716bf` | Schröderstiftstraße | primary | 149 | HVS | 0.88 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564627,5935553]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.564864/9.975795) | [Way](https://www.openstreetmap.org/way/521056834) |
| `seg_b156ac787b079969` | Beim Schlump | secondary | 32 | HVS | 0.74 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564717,5936275]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571346/9.977308) | [Way](https://www.openstreetmap.org/way/391801507) |
| `seg_b6840cf28b42c5fd` | Fruchtallee | primary | 163 | HVS | 0.91 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563694,5936050]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.569444/9.961801) | [Way](https://www.openstreetmap.org/way/664780014) |
| `seg_be03688885b26b0e` | Kieler Straße | primary | 177 | HVS | 0.84 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561914,5937172]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.579746/9.935153) | [Way](https://www.openstreetmap.org/way/733544406) |
| `seg_be08bf5a585a6e49` | Hallerstraße | secondary | 139 | HVS | 0.80 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565229,5936419]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572575/9.985060) | [Way](https://www.openstreetmap.org/way/1188140109) |
| `seg_c341ebfaec60354c` | Lokstedter Steindamm | primary | 35 | HVS | 0.73 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564107,5937938]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.586365/9.968433) | [Way](https://www.openstreetmap.org/way/682409935) |
| `seg_c6fd9fba57de73c7` | Holstenkamp | secondary | 59 | HVS | 0.63 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562305,5936405]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572805/9.940907) | [Way](https://www.openstreetmap.org/way/48936440) |
| `seg_e5c1aa91bda4ef75` | Nedderfeld | secondary | 88 | HVS | 0.70 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564029,5939800]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603109/9.967632) | [Way](https://www.openstreetmap.org/way/143824754) |
| `seg_e883a88bf7d1c4b6` | Kollaustraße | primary | 439 | HVS | 0.96 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562928,5941137]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.615254/9.951276) | [Way](https://www.openstreetmap.org/way/1561698174) |
| `seg_fa902cc611661da4` | Altonaer Straße | secondary | 57 | HVS | 0.65 | mittel | C-GOW-01 → C-G30-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563618,5935432]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.563901/9.960531) | [Way](https://www.openstreetmap.org/way/919746336) |

### ETW30 (30 von 2934)

| segment_id | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_11e4f968d0022afc` | Kollenhof | residential | 171 | keine HVS | 0.15 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561359,5940114]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.606249/9.927360) | [Way](https://www.openstreetmap.org/way/38613168) |
| `seg_16a52f26ffbe1937` | Neuer Jungfernstieg | primary | 76 | keine HVS | 0.27 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565847,5934830]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.558219/9.994060) | [Way](https://www.openstreetmap.org/way/603103444) |
| `seg_2038157dd7e0da6c` | Vogt-Wells-Straße | primary_link | 9 | keine HVS | 0.21 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563785,5939432]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599831/9.963877) | [Way](https://www.openstreetmap.org/way/347903363) |
| `seg_270fcc3b85ca0ef1` | Döringweg | residential | 139 | keine HVS | 0.10 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563076,5940152]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.606385/9.953310) | [Way](https://www.openstreetmap.org/way/23417192) |
| `seg_30cbd68440c9d608` | Hellkamp | residential | 230 | keine HVS | 0.06 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562801,5937046]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578508/9.948520) | [Way](https://www.openstreetmap.org/way/145693819) |
| `seg_30f132e295a05674` | Kulemannstieg | residential | 435 | keine HVS | 0.10 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559777,5943634]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.638065/9.904124) | [Way](https://www.openstreetmap.org/way/8135124) |
| `seg_3274a6c500859758` | Hauptweg | service | 24 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562059,5937817]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.585524/9.937470) | [Way](https://www.openstreetmap.org/way/1036888962) |
| `seg_3658bc2a34a20df5` | Ohmoor / Keltenweg | residential | 872 | keine HVS | 0.04 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563921,5944182]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.642503/9.966904) | [Way](https://www.openstreetmap.org/way/593380094) |
| `seg_3882e28e339b36bf` | Spengelweg / Rellinger Straße | residential | 224 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562449,5936502]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573663/9.943104) | [Way](https://www.openstreetmap.org/way/23100115) |
| `seg_4dc56d0f4f9c2d40` | Alter Weg | residential | 33 | keine HVS | 0.09 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561951,5937144]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.579487/9.935706) | [Way](https://www.openstreetmap.org/way/996116337) |
| `seg_58220dc3e93553f4` | Haldenstieg | residential | 70 | keine HVS | 0.24 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563988,5941074]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.614559/9.967275) | [Way](https://www.openstreetmap.org/way/59920781) |
| `seg_5dc74e1c7a428762` | Bismarckstraße | residential | 154 | keine HVS | 0.10 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564079,5936749]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575678/9.967761) | [Way](https://www.openstreetmap.org/way/922719954) |
| `seg_5e9c7356d3064bf2` | Redingskamp | residential | 123 | keine HVS | 0.31 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559062,5940097]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.606357/9.892646) | [Way](https://www.openstreetmap.org/way/1304763135) |
| `seg_822112322d71569d` | Vielohweg | tertiary | 221 | keine HVS | 0.54 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562113,5943829]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.639545/9.939487) | [Way](https://www.openstreetmap.org/way/1166229950) |
| `seg_8a4e8cc5726c15ae` | Bundesstraße | tertiary | 124 | keine HVS | 0.54 | niedrig | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564549,5935990]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.568800/9.974709) | [Way](https://www.openstreetmap.org/way/1291539901) |
| `seg_8b3aeffffc36d6cf` | Alsterufer | residential | 76 | keine HVS | 0.17 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565930,5934920]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.559015/9.995337) | [Way](https://www.openstreetmap.org/way/790292963) |
| `seg_905476006cbf75ae` | Schwenckestraße | residential | 67 | keine HVS | 0.21 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562993,5937318]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580928/9.951486) | [Way](https://www.openstreetmap.org/way/1186524134) |
| `seg_9821520e4dd5befe` | Eichenstraße / Im Gehölz / Alardusstraße | residential | 448 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563644,5936761]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575845/9.961205) | [Way](https://www.openstreetmap.org/way/26609629) |
| `seg_9afdb438bea183a0` | Schmiedekoppel | unclassified | 343 | keine HVS | 0.27 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562841,5940716]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.611483/9.949873) | [Way](https://www.openstreetmap.org/way/10430462) |
| `seg_a3fcbbf6fe414efd` | Langobardenweg | residential | 214 | keine HVS | 0.21 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563735,5943424]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.635714/9.963943) | [Way](https://www.openstreetmap.org/way/23807792) |
| `seg_b070de284cf80f00` | Lewetzauweg | residential | 225 | keine HVS | 0.17 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562169,5943338]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.635133/9.940232) | [Way](https://www.openstreetmap.org/way/1166234766) |
| `seg_b5af316a5773a879` | Kassubenweg | residential | 91 | keine HVS | 0.22 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563095,5944490]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645373/9.954473) | [Way](https://www.openstreetmap.org/way/23807654) |
| `seg_c114f44771e0e957` | Jaarsmoor | residential | 100 | keine HVS | 0.36 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559081,5940384]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.608935/9.892975) | [Way](https://www.openstreetmap.org/way/5112647) |
| `seg_c8bf58d3bc35b785` | Hainholz | residential | 47 | keine HVS | 0.21 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563574,5941913]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.622152/9.961189) | [Way](https://www.openstreetmap.org/way/24403317) |
| `seg_cf6ba4914334862f` | Emilienstraße | residential | 186 | keine HVS | 0.16 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563133,5936389]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572564/9.953401) | [Way](https://www.openstreetmap.org/way/1565176194) |
| `seg_cfe64a88e05b5219` | Allende-Platz | service | 79 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565069,5935869]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567652/9.982529) | [Way](https://www.openstreetmap.org/way/27487129) |
| `seg_d30d483bf6160344` | Eimsbütteler Marktplatz | primary | 28 | keine HVS | 0.20 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562450,5936356]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572345/9.943090) | [Way](https://www.openstreetmap.org/way/56701994) |
| `seg_de632bc945c8fe10` | Paul-Sorge-Straße | tertiary | 89 | keine HVS | 0.36 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562977,5943116]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633037/9.952412) | [Way](https://www.openstreetmap.org/way/926287337) |
| `seg_e3b8e15a4c5b34a7` | Elbgaustraße | primary | 12 | keine HVS | 0.30 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559964,5940186]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.607057/9.906292) | [Way](https://www.openstreetmap.org/way/1429699451) |
| `seg_f2dfc43510f356b2` | Antonie-Möbis-Weg | residential | 65 | keine HVS | 0.00 | mittel | C-ETW-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559517,5940210]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.607323/9.899533) | [Way](https://www.openstreetmap.org/way/7315237) |

### ETW_ERF (30 von 148)

| segment_id | Name | highway | m | HVS | conn_score | confidence | Regeln | Orthophoto | Panoramax | OSM |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- | --- | --- |
| `seg_0391547b8f09a389` | Eidelstedter Weg | living_street | 84 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563330,5937301]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580739/9.956567) | [Way](https://www.openstreetmap.org/way/144069404) |
| `seg_0b594a49dab7ece1` | Moorflagen | living_street | 49 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562504,5944290]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.643645/9.945496) | [Way](https://www.openstreetmap.org/way/26783778) |
| `seg_2f9e1af1c9742139` | Nyswanderweg | living_street | 56 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559125,5941554]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.619448/9.893871) | [Way](https://www.openstreetmap.org/way/7626606) |
| `seg_2fbde63c63a92b13` | – | pedestrian | 11 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562546,5936756]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575934/9.944619) | [Way](https://www.openstreetmap.org/way/1084007706) |
| `seg_37157d7df687cbb1` | Siloahweg | living_street | 95 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559562,5943295]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.635048/9.900802) | [Way](https://www.openstreetmap.org/way/57841693) |
| `seg_38926833099b9b94` | Schlüterstraße | pedestrian | 77 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565334,5935803]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567025/9.986511) | [Way](https://www.openstreetmap.org/way/738633624) |
| `seg_3a1af222674e6102` | Tibarg | pedestrian | 56 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562932,5941642]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.619793/9.951437) | [Way](https://www.openstreetmap.org/way/1157929376) |
| `seg_3a56764a0a82b909` | Tibarg | pedestrian | 74 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563027,5941735]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620624/9.952890) | [Way](https://www.openstreetmap.org/way/124212740) |
| `seg_4ecc0306b23e1cdb` | Ohmoorring | living_street | 15 | keine HVS | 0.03 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563641,5943640]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.637669/9.962551) | [Way](https://www.openstreetmap.org/way/432988854) |
| `seg_56c79720bcb19053` | Am Ziegelteich | living_street | 260 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561722,5936852]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576891/9.932198) | [Way](https://www.openstreetmap.org/way/15089591) |
| `seg_5f7db3bd903c7eea` | Klabautermannweg | living_street | 113 | keine HVS | 0.03 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561084,5944644]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.646994/9.924083) | [Way](https://www.openstreetmap.org/way/593924194) |
| `seg_7b8842ebe2f9e58d` | An der Mühlenau | living_street | 96 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559903,5939570]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.601529/9.905243) | [Way](https://www.openstreetmap.org/way/7566373) |
| `seg_8086824462c8d60c` | Harvestehuder Stieg | living_street | 110 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566017,5936803]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575928/9.997045) | [Way](https://www.openstreetmap.org/way/119223002) |
| `seg_82cdaef5779ebd8c` | Martin-Luther-King-Platz | pedestrian | 73 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564779,5935834]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567375/9.978145) | [Way](https://www.openstreetmap.org/way/316524933) |
| `seg_92b23473a37a141f` | Tibarg | pedestrian | 16 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562942,5941676]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620104/9.951589) | [Way](https://www.openstreetmap.org/way/1157929376) |
| `seg_93910bac92b79295` | Tibarg | pedestrian | 14 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562947,5941667]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620020/9.951659) | [Way](https://www.openstreetmap.org/way/913610316) |
| `seg_94fce9570efbb3de` | Kurt-Schill-Weg | living_street | 100 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562667,5944154]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.642405/9.947931) | [Way](https://www.openstreetmap.org/way/26783756) |
| `seg_9ba5a064070bb092` | Isern-Hinnerk-Weg | living_street | 148 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561234,5945258]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.652493/9.926477) | [Way](https://www.openstreetmap.org/way/23300052) |
| `seg_a06cc4b0c4a2c082` | Am Ziegelteich | living_street | 16 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561736,5936715]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575653/9.932382) | [Way](https://www.openstreetmap.org/way/1078034982) |
| `seg_ad15c337575ac5e6` | Albertinenstieg | living_street | 37 | keine HVS | 0.22 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559468,5943125]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633527/9.899357) | [Way](https://www.openstreetmap.org/way/57841698) |
| `seg_bbc6664e064bef08` | Ernst-Mittelbach-Stieg | living_street | 90 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562719,5944383]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.644453/9.948769) | [Way](https://www.openstreetmap.org/way/25076009) |
| `seg_c247052cf4a16cdf` | Anne-Barth-Weg | living_street | 65 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562005,5937583]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.583431/9.936612) | [Way](https://www.openstreetmap.org/way/145693785) |
| `seg_cc26a0f235ad72cf` | Kaiser-Friedrich-Ufer | pedestrian | 38 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563987,5936506]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573512/9.966326) | [Way](https://www.openstreetmap.org/way/24846541) |
| `seg_d0cfee373bf383d7` | – | pedestrian | 67 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562684,5943996]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.640977/9.948161) | [Way](https://www.openstreetmap.org/way/1279927824) |
| `seg_dd0dec4dda7685d0` | Moorflagen | pedestrian | 12 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562616,5943915]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.640264/9.947120) | [Way](https://www.openstreetmap.org/way/26783796) |
| `seg_de6e32489eec31b6` | Martin-Luther-King-Platz | pedestrian | 25 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564807,5935862]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567622/9.978570) | [Way](https://www.openstreetmap.org/way/316524933) |
| `seg_e90d0aac3b546d96` | Lindenallee | living_street | 212 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563584,5935770]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.566945/9.960088) | [Way](https://www.openstreetmap.org/way/137037876) |
| `seg_e9ec19be27f8bca8` | – | pedestrian | 4 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563038,5936799]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576257/9.952058) | [Way](https://www.openstreetmap.org/way/1293310387) |
| `seg_efdf395cc6f52c06` | Lohwurt | living_street | 100 | keine HVS | 0.10 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559603,5940312]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.608228/9.900856) | [Way](https://www.openstreetmap.org/way/33065799) |
| `seg_f5f5d563d23de63b` | Tibarg | pedestrian | 6 | keine HVS | 0.00 | mittel | C-ERF-01 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562941,5941685]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620178/9.951580) | [Way](https://www.openstreetmap.org/way/913610320) |

### GOW80

_keine Abschnitte im Bezirk_

### ETW60

_keine Abschnitte im Bezirk_

## Lizenz

Abschnitte und Merkmale aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; amtliche Merkmale (Tempo, Verkehrsmengen, ALKIS): Freie und Hansestadt Hamburg, dl-de/by-2.0; Busfahrten: HVV, dl-de/by-2.0; Einwohner: Zensus 2022, dl-de/by-2.0. Orthophotos: LGV Hamburg, dl-de/by-2.0. Panoramax-Bilder: Lizenz je Bild.
