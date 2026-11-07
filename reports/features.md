# Merkmalsbericht – Stufe 4

Erzeugt: 2026-11-07T14:59:45+00:00 von `pipeline/s04_features.py`, rules.yaml 0.16.0. Nicht amtlicher Entwurf.

## Kennzahlen

- Abschnitte gesamt (OSM-Auszug): 36 526; im Arbeitsgebiet (Hamburg (7 Bezirke) + 500 m): 34 702; davon mit Bezirk: 33 712
- Normierung (S-FEAT-01): Perzentilrang über das ganze Arbeitsgebiet, also über ganz Hamburg (Entscheidung 2026-11-04), damit derselbe Abschnitt in jedem Bezirk gleich bewertet wird.
- Betweenness: exakt (keine Stichprobe), ungerichtet, 34 375 Kfz-Abschnitte ganz Hamburgs, Laufzeit 55 s
- Reisezeit-Tempo im Arbeitsgebiet: official 81.8 %, osm 10.8 %, default 4.0 %, keins 3.4 %
- Ist-Tempo: amtlich 81.8 %, OSM 10.8 %, unbekannt 7.4 %; Konflikt amtlich ≠ OSM: 1146 Abschnitte
- GTFS: repräsentativer Werktag 2026-04-29, 1662 shapes, 0 Fahrten ohne shape
- Zensus-Gitter 100 m: 31152 Zellen im Arbeitsgebiet, Einwohner im 100-m-Puffer flächenanteilig; Zellen ohne Einwohner fehlen in der Datei und zählen 0; Werte durch Geheimhaltung leicht verändert
- ALKIS-Gebäude: 377 027 oberirdische Gebäude im Arbeitsgebiet (WFS_HH_ALKIS_vereinfacht, seit rules.yaml 0.6.0 statt OSM)

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| Normwerte und Scores in [0, 1] | ok | alle |
| conn_score im Arbeitsgebiet vollständig | ok | 0 ohne conn_score |
| Betweenness für alle Kfz-Abschnitte | ok | 0 ohne Wert |
| Gebäudefunktionen aus rules.yaml kommen in ALKIS vor | ok | alle |

## Methode

- **Normierung (S-FEAT-01):** Perzentilrang über alle Abschnitte im Arbeitsgebiet mit bekanntem Wert, (Rang − 1) / (n − 1); gleiche Werte erhalten den kleinsten Rang ihrer Gruppe (rules.yaml 0.5.0), damit der kleinste Wert – z. B. 0 Busfahrten – auf 0 fällt. 1 = größter Wert. `in_hvs` geht als 0/1 ein, `shop_frontage_share` unverändert. `sensitive_facilities_norm` ist der Perzentilrang der negativen Entfernung (nah = hoch). Die Normierung hängt vom Arbeitsgebiet ab; bei Ausweitung auf ganz Hamburg ändern sich die Werte.
- **Fehlende Werte:** bleiben null. conn_score und place_score legen das Gewicht fehlender Merkmale anteilig auf die übrigen um (missing_value_policy); `conn_weight_available`/`place_weight_available` zeigen, welcher Gewichtsanteil Werte hatte. Die Herabstufung der confidence folgt in Prompt 08.
- **Betweenness (S-FEAT-02):** Reisezeit = Länge / Tempo (amtlich → OSM maxspeed → Standardwert je Klasse). Ohne pedestrian, service, track. Mehrere OSM-Werte je Abschnitt (z. B. „50 / 30“) gelten als unbekannt.
- **Gebäudedichte (S-FEAT-03):** Grundfläche der oberirdischen ALKIS-Gebäude (gebnutzbez Gebaeude) im 50-m-Puffer / Pufferfläche.
- **Publikumsnutzung (S-FEAT-05):** Anteil der ALKIS-Gebäude im 20-m-Puffer mit Publikumsnutzung: Gebäudefunktion aus der Liste in rules.yaml (36 Werte) oder OSM-shop/amenity-Punkt im Gebäude (ohne Stadtmöblierung). Nebengebäude (17 Funktionen, z. B. Garage, Gartenhaus) zählen nicht. Schulen und Kitas gehen über S-FEAT-06 ein, nicht hier. Das Geschoss wird nicht geprüft.
- **Radnetz, Busfahrten (S-FEAT-07/08):** Längenanteil wie S-CONF-02 (Puffer, Winkel, Mindestanteil).
- **Ist-Gestaltung (S-FEAT-10):** Mehrheitswert über die Ways des Abschnitts (Gewicht: Länge im 1-m-Puffer). Kein Tag = unbekannt (null), nicht „nein“. Querungen und Verkehrsberuhigung: OSM-Knoten höchstens 1 m vom Abschnitt. `access_motor_only`: motorway/motorway_link oder motorroad=yes (sonst nein, weil motorroad nur positiv erfasst wird).

## Nullwertanteil je Merkmal (Arbeitsgebiet)

| Merkmal | Quelle | Regel | benötigt von | null Arbeitsgebiet | null mit Bezirk |
| --- | --- | --- | --- | ---: | ---: |
| `betweenness` | OSM-Netz + Tempo | S-FEAT-02 | Rohwert für betweenness_norm | 5.6 % | 5.6 % |
| `betweenness_norm` | OSM-Netz + Tempo | S-FEAT-01/02 | scores.conn_score | 5.6 % | 5.6 % |
| `in_hvs` | DTV-Linien HVS 2019 | S-CONF-04 | C-GOW-01, scores.conn_score | 0.0 % | 0.0 % |
| `bus_trips_weekday` | GTFS HVV | S-FEAT-08 | Rohwert für bus_trips_weekday_norm | 0.0 % | 0.0 % |
| `bus_trips_weekday_norm` | GTFS HVV | S-FEAT-01/08 | scores.conn_score | 0.0 % | 0.0 % |
| `dtv_official` | DTV-Linien HVS 2019 | S-CONF-01 | discrepancy.use, Rohwert für dtv_norm | 83.2 % | 82.7 % |
| `dtv_norm` | DTV-Linien HVS 2019 | S-FEAT-01 | scores.conn_score | 83.2 % | 82.7 % |
| `conn_score` | abgeleitet | scores.conn_score | C-RUR-01, C-GOW-01 | 0.0 % | 0.0 % |
| `conn_weight_available` | abgeleitet | scores.conn_score | missing_value_policy (confidence, Prompt 08) | 0.0 % | 0.0 % |
| `building_density` | ALKIS-Gebäude | S-FEAT-03 | Rohwert für building_density_norm | 0.0 % | 0.0 % |
| `building_density_norm` | ALKIS-Gebäude | S-FEAT-01/03 | scores.place_score | 0.0 % | 0.0 % |
| `population_100m` | Zensus 2022 Gitter | S-FEAT-04 | priority.risk_weights, Rohwert | 0.0 % | 0.0 % |
| `population_100m_norm` | Zensus 2022 Gitter | S-FEAT-01/04 | scores.place_score | 0.0 % | 0.0 % |
| `shop_frontage_share` | ALKIS-Gebäudefunktion + OSM shop/amenity | S-FEAT-05 | C-G30-01, scores.place_score (frontage_share) | 0.0 % | 0.0 % |
| `frontage_buildings` | ALKIS-Gebäude | S-FEAT-05 | Nenner von shop_frontage_share (Nachvollziehbarkeit) | 0.0 % | 0.0 % |
| `schools_or_kitas_within_m` | OSM Schulen/Kitas | S-FEAT-06 | C-G30-01, priority.school_kita_within_150m | 0.0 % | 0.0 % |
| `sensitive_facilities_norm` | OSM Schulen/Kitas | S-FEAT-01/06 | scores.place_score | 0.0 % | 0.0 % |
| `place_score` | abgeleitet | scores.place_score | Prompt 08/10 (Funktionskonflikt, Diskrepanz) | 0.0 % | 0.0 % |
| `place_weight_available` | abgeleitet | scores.place_score | missing_value_policy | 0.0 % | 0.0 % |
| `in_cycle_network` | OSM Radnetz Hamburg | S-FEAT-07 | priority.risk_weights.cycle_network, ETW30-Ausnahme | 0.0 % | 0.0 % |
| `speed_ist_kmh` | Tempo amtlich/OSM | S-FEAT-09 | discrepancy.speed | 7.4 % | 6.7 % |
| `speed_ist_source` | Tempo amtlich/OSM | S-FEAT-09 | Herkunft von speed_ist_kmh | 7.4 % | 6.7 % |
| `speed_sources_conflict` | Tempo amtlich/OSM | S-FEAT-09 | Unsicherheit (confidence) | 0.0 % | 0.0 % |
| `travel_speed_kmh` | Tempo amtlich/OSM/Standard | S-FEAT-02 | Gewicht der Betweenness | 3.4 % | 3.4 % |
| `travel_speed_source` | Tempo amtlich/OSM/Standard | S-FEAT-02 | Herkunft von travel_speed_kmh | 3.4 % | 3.4 % |
| `separated_cycle_track_present` | OSM-Tags | S-FEAT-10 | C-G30-02, requirements.*.cycling | 36.5 % | 35.8 % |
| `parallel_cycle_route_present` | OSM-Radwege + amtliches Radnetz (Bestand) | S-FEAT-11 | D-DES-01 (GOW50: Radweg oder Parallelroute) | 0.0 % | 0.0 % |
| `cycle_lane_present` | OSM-Tags | S-FEAT-10 | requirements.*.cycle_lanes_allowed | 36.5 % | 35.8 % |
| `lanes` | OSM-Tags | S-FEAT-10 | requirements.GOW50.median_if_lanes_per_dir_gte | 57.3 % | 57.0 % |
| `centre_line` | OSM-Tags | S-FEAT-10 | requirements.GOW30.centre_line | 83.3 % | 83.1 % |
| `parking` | OSM-Tags | S-FEAT-10 | Rohwert der Parkmerkmale | 70.1 % | 69.3 % |
| `parking_on_carriageway` | OSM-Tags | S-FEAT-10 | requirements.GOW30.parking_on_carriageway | 70.7 % | 69.9 % |
| `parking_along_carriageway` | OSM-Tags | S-FEAT-10 | requirements.GOW50.parking_along_carriageway | 70.7 % | 69.9 % |
| `angle_parking` | OSM-Tags | S-FEAT-10 | requirements.GOW50.angle_parking | 70.7 % | 69.9 % |
| `crossings_count` | OSM-Knoten | S-FEAT-10 | requirements.GOW50.crossings | 0.0 % | 0.0 % |
| `traffic_calming_count` | OSM-Knoten | S-FEAT-10 | requirements.ETW30.speed_reducer_spacing_m | 0.0 % | 0.0 % |
| `surface` | OSM-Tags | S-FEAT-10 | Erkennbarkeit (guide.md 1.2) | 4.0 % | 3.5 % |
| `access_motor_only` | OSM-Tags | S-FEAT-10 | C-SW-01 | 0.0 % | 0.0 % |
| `pedestrian_zone` | OSM-Tags | S-FEAT-10 | C-ERF-01 | 0.0 % | 0.0 % |
| `outside_builtup_area` | keine Quelle | – | C-RUR-01 (keine Datenquelle für die Ortsgrenze (docs/open_questions.md)) | 100.0 % | 100.0 % |
| `crossing_demand` | nicht definiert | – | C-G30-01 (in rules.yaml nicht definiert (docs/open_questions.md)) | 100.0 % | 100.0 % |
| `override_school_street` | overrides.csv (Prompt 09) | – | C-ERF-01 (kommt aus overrides/overrides.csv (Prompt 09)) | 100.0 % | 100.0 % |
| `width_p10_m` | Querschnitt (Prompt 07) | – | C-G30-02 (kommt aus dem Querschnitt (Prompt 07)) | 100.0 % | 100.0 % |

## Kennzahlen je Bezirk

| Bezirk | Abschnitte | km | conn_score (Median) | place_score (Median) | Ist-Tempo null | Gebäudedichte null | lanes (OSM) null |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 4 886 | 620.5 | 0.23 | 0.46 | 5.4 % | 0.0 % | 61.5 % |
| Bergedorf | 1 957 | 209.3 | 0.23 | 0.47 | 13.3 % | 0.0 % | 70.0 % |
| Eimsbüttel | 4 004 | 470.4 | 0.25 | 0.51 | 5.2 % | 0.0 % | 53.5 % |
| Hamburg-Mitte | 6 839 | 881.3 | 0.27 | 0.43 | 8.5 % | 0.0 % | 47.6 % |
| Hamburg-Nord | 5 136 | 563.3 | 0.26 | 0.53 | 4.5 % | 0.0 % | 52.5 % |
| Harburg | 3 348 | 465.2 | 0.21 | 0.40 | 10.4 % | 0.0 % | 59.5 % |
| Wandsbek | 7 542 | 1 030.4 | 0.23 | 0.41 | 5.0 % | 0.0 % | 62.9 % |
| **gesamt** | 33 712 | 4 240.4 | 0.24 | 0.45 | 6.7 % | 0.0 % | 57.0 % |

## Nullwertanteil je Datenquelle

| Quelle | Status (manifest) | Merkmale | mittlerer Nullanteil |
| --- | --- | --- | ---: |
| OSM-Netz + Tempo | – | `betweenness`, `betweenness_norm` | 5.6 % |
| DTV-Linien HVS 2019 | ok | `in_hvs`, `dtv_official`, `dtv_norm` | 55.5 % |
| GTFS HVV | ok | `bus_trips_weekday`, `bus_trips_weekday_norm` | 0.0 % |
| abgeleitet | – | `conn_score`, `conn_weight_available`, `place_score`, `place_weight_available` | 0.0 % |
| ALKIS-Gebäude | ok | `building_density`, `building_density_norm`, `frontage_buildings` | 0.0 % |
| Zensus 2022 Gitter | ok | `population_100m`, `population_100m_norm` | 0.0 % |
| ALKIS-Gebäudefunktion + OSM shop/amenity | – | `shop_frontage_share` | 0.0 % |
| OSM Schulen/Kitas | fallback | `schools_or_kitas_within_m`, `sensitive_facilities_norm` | 0.0 % |
| OSM Radnetz Hamburg | fallback | `in_cycle_network` | 0.0 % |
| Tempo amtlich/OSM | ok | `speed_ist_kmh`, `speed_ist_source`, `speed_sources_conflict` | 4.9 % |
| Tempo amtlich/OSM/Standard | – | `travel_speed_kmh`, `travel_speed_source` | 3.4 % |
| OSM-Tags | – | `separated_cycle_track_present`, `cycle_lane_present`, `lanes`, `centre_line`, `parking`, `parking_on_carriageway`, `parking_along_carriageway`, `angle_parking`, `surface`, `access_motor_only`, `pedestrian_zone` | 45.4 % |
| OSM-Radwege + amtliches Radnetz (Bestand) | – | `parallel_cycle_route_present` | 0.0 % |
| OSM-Knoten | – | `crossings_count`, `traffic_calming_count` | 0.0 % |
| keine Quelle | – | `outside_builtup_area` | 100.0 % |
| nicht definiert | – | `crossing_demand` | 100.0 % |
| overrides.csv (Prompt 09) | – | `override_school_street` | 100.0 % |
| Querschnitt (Prompt 07) | – | `width_p10_m` | 100.0 % |

## Verteilungen (Arbeitsgebiet)

### `betweenness`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 3.65e+06 | 30298 | ██████████████████████████████ |
| 3.65e+06 | 7.29e+06 | 1281 | █ |
| 7.29e+06 | 1.09e+07 | 674 | █ |
| 1.09e+07 | 1.46e+07 | 308 |  |
| 1.46e+07 | 1.82e+07 | 109 |  |
| 1.82e+07 | 2.19e+07 | 62 |  |
| 2.19e+07 | 2.55e+07 | 11 |  |
| 2.55e+07 | 2.92e+07 | 8 |  |
| 2.92e+07 | 3.28e+07 | 3 |  |
| 3.28e+07 | 3.65e+07 | 1 |  |

### `betweenness_norm`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.1 | 3278 | ███████████████████ |
| 0.1 | 0.2 | 3273 | ███████████████████ |
| 0.2 | 0.3 | 5274 | ██████████████████████████████ |
| 0.3 | 0.4 | 1277 | ███████ |
| 0.4 | 0.5 | 3275 | ███████████████████ |
| 0.5 | 0.6 | 3276 | ███████████████████ |
| 0.6 | 0.7 | 3275 | ███████████████████ |
| 0.7 | 0.8 | 3276 | ███████████████████ |
| 0.8 | 0.9 | 3275 | ███████████████████ |
| 0.9 | 1 | 3276 | ███████████████████ |

### `dtv_official`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 1e+03 | 1.4e+04 | 1052 | █████████████ |
| 1.4e+04 | 2.7e+04 | 2497 | ██████████████████████████████ |
| 2.7e+04 | 4e+04 | 1523 | ██████████████████ |
| 4e+04 | 5.3e+04 | 487 | ██████ |
| 5.3e+04 | 6.6e+04 | 167 | ██ |
| 6.6e+04 | 7.9e+04 | 25 |  |
| 7.9e+04 | 9.2e+04 | 12 |  |
| 9.2e+04 | 1.05e+05 | 26 |  |
| 1.05e+05 | 1.18e+05 | 26 |  |
| 1.18e+05 | 1.31e+05 | 14 |  |

### `building_density`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.0848 | 7411 | ██████████████████ |
| 0.0848 | 0.17 | 12097 | ██████████████████████████████ |
| 0.17 | 0.254 | 9710 | ████████████████████████ |
| 0.254 | 0.339 | 3435 | █████████ |
| 0.339 | 0.424 | 1313 | ███ |
| 0.424 | 0.509 | 492 | █ |
| 0.509 | 0.594 | 172 |  |
| 0.594 | 0.679 | 51 |  |
| 0.679 | 0.763 | 17 |  |
| 0.763 | 0.848 | 4 |  |

### `shop_frontage_share`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.1 | 21392 | ██████████████████████████████ |
| 0.1 | 0.2 | 2126 | ███ |
| 0.2 | 0.3 | 2017 | ███ |
| 0.3 | 0.4 | 1226 | ██ |
| 0.4 | 0.5 | 637 | █ |
| 0.5 | 0.6 | 1830 | ███ |
| 0.6 | 0.7 | 688 | █ |
| 0.7 | 0.8 | 460 | █ |
| 0.8 | 0.9 | 449 | █ |
| 0.9 | 1 | 3877 | █████ |

### `schools_or_kitas_within_m`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 483 | 29827 | ██████████████████████████████ |
| 483 | 967 | 3367 | ███ |
| 967 | 1.45e+03 | 840 | █ |
| 1.45e+03 | 1.93e+03 | 309 |  |
| 1.93e+03 | 2.42e+03 | 174 |  |
| 2.42e+03 | 2.9e+03 | 146 |  |
| 2.9e+03 | 3.38e+03 | 17 |  |
| 3.38e+03 | 3.87e+03 | 8 |  |
| 3.87e+03 | 4.35e+03 | 11 |  |
| 4.35e+03 | 4.83e+03 | 3 |  |

### `speed_ist_kmh`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 5 | 16.5 | 1365 | ███ |
| 16.5 | 28 | 367 | █ |
| 28 | 39.5 | 15802 | ██████████████████████████████ |
| 39.5 | 51 | 13947 | ██████████████████████████ |
| 51 | 62.5 | 387 | █ |
| 62.5 | 74 | 67 |  |
| 74 | 85.5 | 111 |  |
| 85.5 | 97 | 0 |  |
| 97 | 108 | 62 |  |
| 108 | 120 | 32 |  |

### `lanes`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 1 | 1.6 | 3145 | ███████████ |
| 1.6 | 2.2 | 8402 | ██████████████████████████████ |
| 2.2 | 2.8 | 0 |  |
| 2.8 | 3.4 | 1939 | ███████ |
| 3.4 | 4 | 0 |  |
| 4 | 4.6 | 1101 | ████ |
| 4.6 | 5.2 | 170 | █ |
| 5.2 | 5.8 | 0 |  |
| 5.8 | 6.4 | 58 |  |
| 6.4 | 7 | 7 |  |

### `crossings_count`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.9 | 24563 | ██████████████████████████████ |
| 0.9 | 1.8 | 8574 | ██████████ |
| 1.8 | 2.7 | 1348 | ██ |
| 2.7 | 3.6 | 173 |  |
| 3.6 | 4.5 | 30 |  |
| 4.5 | 5.4 | 7 |  |
| 5.4 | 6.3 | 2 |  |
| 6.3 | 7.2 | 3 |  |
| 7.2 | 8.1 | 1 |  |
| 8.1 | 9 | 1 |  |

### `conn_score`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.0995 | 8062 | ██████████████████████████████ |
| 0.0995 | 0.199 | 6708 | █████████████████████████ |
| 0.199 | 0.299 | 6158 | ███████████████████████ |
| 0.299 | 0.398 | 2800 | ██████████ |
| 0.398 | 0.498 | 1824 | ███████ |
| 0.498 | 0.597 | 3031 | ███████████ |
| 0.597 | 0.697 | 1853 | ███████ |
| 0.697 | 0.796 | 1671 | ██████ |
| 0.796 | 0.896 | 1527 | ██████ |
| 0.896 | 0.995 | 1068 | ████ |

### `place_score`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 7.49e-05 | 0.0977 | 2576 | ██████████████ |
| 0.0977 | 0.195 | 2878 | ████████████████ |
| 0.195 | 0.293 | 3986 | ██████████████████████ |
| 0.293 | 0.391 | 5032 | ███████████████████████████ |
| 0.391 | 0.488 | 5516 | ██████████████████████████████ |
| 0.488 | 0.586 | 4953 | ███████████████████████████ |
| 0.586 | 0.684 | 4004 | ██████████████████████ |
| 0.684 | 0.781 | 3256 | ██████████████████ |
| 0.781 | 0.879 | 2008 | ███████████ |
| 0.879 | 0.977 | 493 | ███ |

### `conn_weight_available`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0.45 | 0.505 | 1916 | ██ |
| 0.505 | 0.56 | 0 |  |
| 0.56 | 0.615 | 0 |  |
| 0.615 | 0.67 | 31 |  |
| 0.67 | 0.725 | 0 |  |
| 0.725 | 0.78 | 0 |  |
| 0.78 | 0.835 | 26957 | ██████████████████████████████ |
| 0.835 | 0.89 | 0 |  |
| 0.89 | 0.945 | 0 |  |
| 0.945 | 1 | 5798 | ██████ |

### Kategoriale Merkmale

| Merkmal | Werte (Anteil der Abschnitte) |
| --- | --- |
| `in_hvs` | False: 82.8 %, True: 17.2 % |
| `in_cycle_network` | False: 96.9 %, True: 3.1 % |
| `separated_cycle_track_present` | False: 41.8 %, null: 36.5 %, True: 21.7 % |
| `cycle_lane_present` | False: 57.9 %, null: 36.5 %, True: 5.5 % |
| `centre_line` | null: 83.3 %, False: 16.4 %, True: 0.3 % |
| `parking_on_carriageway` | null: 70.7 %, False: 22.1 %, True: 7.2 % |
| `parking_along_carriageway` | null: 70.7 %, False: 17.5 %, True: 11.9 % |
| `angle_parking` | null: 70.7 %, False: 27.5 %, True: 1.8 % |
| `surface` | asphalt: 82.8 %, paving_stones: 6.7 %, sett: 4.8 %, null: 4.0 %, compacted: 0.6 %, unhewn_cobblestone: 0.3 %, paved: 0.2 %, concrete: 0.2 % |
| `access_motor_only` | False: 98.5 %, True: 1.5 % |
| `pedestrian_zone` | False: 98.0 %, True: 2.0 % |
| `speed_sources_conflict` | False: 96.7 %, True: 3.3 % |

### conn_score nach highway-Klasse (Median)

| highway | Abschnitte | conn_score | place_score |
| --- | ---: | ---: | ---: |
| living_street | 1633 | 0.11 | 0.43 |
| motorway | 130 | 0.53 | 0.12 |
| motorway_link | 285 | 0.31 | 0.09 |
| pedestrian | 705 | 0.00 | 0.69 |
| primary | 2777 | 0.83 | 0.43 |
| primary_link | 106 | 0.28 | 0.38 |
| residential | 17571 | 0.17 | 0.47 |
| secondary | 3878 | 0.71 | 0.41 |
| secondary_link | 198 | 0.36 | 0.29 |
| service | 890 | 0.00 | 0.31 |
| tertiary | 4303 | 0.51 | 0.46 |
| tertiary_link | 115 | 0.32 | 0.32 |
| track | 352 | 0.00 | 0.10 |
| trunk | 76 | 0.70 | 0.16 |
| trunk_link | 113 | 0.34 | 0.14 |
| unclassified | 1570 | 0.21 | 0.21 |

## Stichprobe (30 zufällige Abschnitte in Hamburg (7 Bezirke), nach Bezirk geschichtet, Seed 42)

Links auf OSM-Karte und OSM-Way. Orthophoto- und Panoramax-Links folgen, sobald das Linkformat geklärt ist (docs/open_questions.md).

| segment_id | Bezirk | Name | highway | conn | place | betw. | HVS | Tempo | Radweg | Front. | Schule/Kita m | Karte | Way |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | ---: | --- | ---: | ---: | --- | --- |
| `seg_0b429570fa26ebba` | Altona | Blankeneser Landstraße | secondary | 0.77 | 0.56 | 0.85 | ja | 50 | nein | 0.50 | 90 | [Karte](https://www.openstreetmap.org/?mlat=53.565854&mlon=9.799288#map=18/53.565854/9.799288) | [Way](https://www.openstreetmap.org/way/4347380) |
| `seg_30696dcbf7bc7a04` | Altona | Stresemannstraße | primary | 0.72 | 0.55 | 0.39 | ja | 50 | ja | 0.25 | 250 | [Karte](https://www.openstreetmap.org/?mlat=53.563539&mlon=9.941936#map=18/53.563539/9.941936) | [Way](https://www.openstreetmap.org/way/936598996) |
| `seg_69ef3a0b69aab218` | Altona | Augustenpassage | residential | 0.07 | 0.91 | 0.16 | nein | 30 | nein | 0.64 | 3 | [Karte](https://www.openstreetmap.org/?mlat=53.559088&mlon=9.965603#map=18/53.559088/9.965603) | [Way](https://www.openstreetmap.org/way/618750343) |
| `seg_76cb381fe708c1fa` | Altona | Babenwischenweg | unclassified | 0.20 | 0.03 | 0.46 | nein | 30 | nein | 0.00 | 1962 | [Karte](https://www.openstreetmap.org/?mlat=53.609687&mlon=9.763284#map=18/53.609687/9.763284) | [Way](https://www.openstreetmap.org/way/139864005) |
| `seg_264144b18b9fcea1` | Bergedorf | Agnes-Wolffson-Straße | living_street | 0.20 | 0.50 | 0.46 | nein | 7 | – | 0.00 | 132 | [Karte](https://www.openstreetmap.org/?mlat=53.485344&mlon=10.179786#map=18/53.485344/10.179786) | [Way](https://www.openstreetmap.org/way/547484929) |
| `seg_3da7e9d4c44d23c5` | Bergedorf | Bergedorfer Straße | primary | 0.96 | 0.17 | 1.00 | ja | 70 | nein | 0.00 | 378 | [Karte](https://www.openstreetmap.org/?mlat=53.521662&mlon=10.148217#map=18/53.521662/10.148217) | [Way](https://www.openstreetmap.org/way/229835361) |
| `seg_1abf10d7274d8422` | Eimsbüttel | Rahweg | residential | 0.20 | 0.30 | 0.45 | nein | 30 | nein | 0.05 | 887 | [Karte](https://www.openstreetmap.org/?mlat=53.641256&mlon=9.977482#map=18/53.641256/9.977482) | [Way](https://www.openstreetmap.org/way/148170157) |
| `seg_b14dd9d1cd005339` | Eimsbüttel | Herulerweg | unclassified | 0.03 | 0.07 | 0.07 | nein | 50 | ja | 0.00 | 806 | [Karte](https://www.openstreetmap.org/?mlat=53.650258&mlon=9.949240#map=18/53.650258/9.949240) | [Way](https://www.openstreetmap.org/way/25739516) |
| `seg_c232d0e509b97fa5` | Eimsbüttel | Burgwedelkamp | residential | 0.51 | 0.24 | 0.70 | nein | 50 | – | 0.00 | 402 | [Karte](https://www.openstreetmap.org/?mlat=53.641930&mlon=9.911588#map=18/53.641930/9.911588) | [Way](https://www.openstreetmap.org/way/4089419) |
| `seg_c330d48355534e10` | Eimsbüttel | Hohe Weide | residential | 0.17 | 0.71 | 0.39 | nein | 30 | nein | 0.07 | 18 | [Karte](https://www.openstreetmap.org/?mlat=53.576150&mlon=9.973005#map=18/53.576150/9.973005) | [Way](https://www.openstreetmap.org/way/137037866) |
| `seg_08e2ef58517bf643` | Hamburg-Mitte | Bürgerweide | primary | 0.45 | 0.42 | 0.21 | ja | 50 | ja | 0.00 | 114 | [Karte](https://www.openstreetmap.org/?mlat=53.559557&mlon=10.038893#map=18/53.559557/10.038893) | [Way](https://www.openstreetmap.org/way/1116978247) |
| `seg_09aed50abf56bb66` | Hamburg-Mitte | Billstieg | living_street | 0.11 | 0.50 | 0.24 | nein | 50 | – | 0.00 | 86 | [Karte](https://www.openstreetmap.org/?mlat=53.534394&mlon=10.110004#map=18/53.534394/10.110004) | [Way](https://www.openstreetmap.org/way/25581052) |
| `seg_196a8094aa248d80` | Hamburg-Mitte | Lietbargredder | residential | 0.04 | 0.72 | 0.08 | nein | 30 | – | 0.17 | 38 | [Karte](https://www.openstreetmap.org/?mlat=53.527304&mlon=10.152096#map=18/53.527304/10.152096) | [Way](https://www.openstreetmap.org/way/23044175) |
| `seg_7fda4452d37b8c74` | Hamburg-Mitte | Neßdeich | tertiary | 0.64 | 0.37 | 0.94 | nein | 50 | ja | 0.00 | 248 | [Karte](https://www.openstreetmap.org/?mlat=53.534354&mlon=9.861437#map=18/53.534354/9.861437) | [Way](https://www.openstreetmap.org/way/582276139) |
| `seg_a63abe1685a892ba` | Hamburg-Mitte | Riedweg | residential | 0.11 | 0.58 | 0.24 | nein | 30 | – | 0.10 | 76 | [Karte](https://www.openstreetmap.org/?mlat=53.547382&mlon=10.096196#map=18/53.547382/10.096196) | [Way](https://www.openstreetmap.org/way/22604799) |
| `seg_b3afd578702025a0` | Hamburg-Mitte | Dratelnstraße | secondary | 0.57 | 0.61 | 0.88 | nein | 50 | nein | 0.67 | 28 | [Karte](https://www.openstreetmap.org/?mlat=53.500583&mlon=10.001670#map=18/53.500583/10.001670) | [Way](https://www.openstreetmap.org/way/1321676828) |
| `seg_25faecf475c757b5` | Hamburg-Nord | Wakendorfer Weg | residential | 0.34 | 0.42 | 0.78 | nein | 30 | nein | 0.00 | 531 | [Karte](https://www.openstreetmap.org/?mlat=53.677874&mlon=10.035990#map=18/53.677874/10.035990) | [Way](https://www.openstreetmap.org/way/4339201) |
| `seg_5a4f9205e401376b` | Hamburg-Nord | Am Schulwald | tertiary | 0.05 | 0.10 | 0.12 | nein | 50 | ja | 0.00 | 445 | [Karte](https://www.openstreetmap.org/?mlat=53.649806&mlon=10.025809#map=18/53.649806/10.025809) | [Way](https://www.openstreetmap.org/way/27217205) |
| `seg_6037ec807e38fc1e` | Hamburg-Nord | Husumer Straße | residential | 0.07 | 0.75 | 0.17 | nein | 30 | nein | 0.20 | 43 | [Karte](https://www.openstreetmap.org/?mlat=53.586805&mlon=9.978740#map=18/53.586805/9.978740) | [Way](https://www.openstreetmap.org/way/5229056) |
| `seg_ce1e34eab5f15ff9` | Hamburg-Nord | Biedermannplatz | secondary | 0.86 | 0.47 | 0.86 | ja | 50 | ja | 0.00 | 110 | [Karte](https://www.openstreetmap.org/?mlat=53.581917&mlon=10.032758#map=18/53.581917/10.032758) | [Way](https://www.openstreetmap.org/way/53207254) |
| `seg_f684a9657aacf796` | Hamburg-Nord | Sperlingweg | track | 0.00 | 0.13 | – | nein | – | nein | 0.00 | 312 | [Karte](https://www.openstreetmap.org/?mlat=53.613888&mlon=9.967951#map=18/53.613888/9.967951) | [Way](https://www.openstreetmap.org/way/1283331826) |
| `seg_0a1aee1745190a87` | Harburg | Marmstorfer Schützenweg | living_street | 0.03 | 0.29 | 0.06 | nein | 7 | – | 0.00 | 300 | [Karte](https://www.openstreetmap.org/?mlat=53.434846&mlon=9.970139#map=18/53.434846/9.970139) | [Way](https://www.openstreetmap.org/way/893156160) |
| `seg_3e6907faa3bbdc4b` | Harburg | Lorenz-von-Ehren-Weg | track | 0.00 | 0.04 | – | nein | – | – | 0.00 | 1941 | [Karte](https://www.openstreetmap.org/?mlat=53.432430&mlon=9.917560#map=18/53.432430/9.917560) | [Way](https://www.openstreetmap.org/way/900889335) |
| `seg_b2737ecffbf1238b` | Harburg | Dradenauer Deichweg | secondary | 0.45 | 0.00 | 0.11 | ja | 50 | nein | 0.00 | 1446 | [Karte](https://www.openstreetmap.org/?mlat=53.515172&mlon=9.896514#map=18/53.515172/9.896514) | [Way](https://www.openstreetmap.org/way/340295899) |
| `seg_3cd4166bef71ff70` | Wandsbek | Helmut-Steidl-Platz | pedestrian | 0.00 | 0.68 | – | nein | – | – | 1.00 | 224 | [Karte](https://www.openstreetmap.org/?mlat=53.604519&mlon=10.154917#map=18/53.604519/10.154917) | [Way](https://www.openstreetmap.org/way/10630855) |
| `seg_75f47c8b84607bca` | Wandsbek | Farmsener Landstraße | secondary | 0.64 | 0.49 | 0.57 | ja | 30 | nein | 0.50 | 60 | [Karte](https://www.openstreetmap.org/?mlat=53.650162&mlon=10.161503#map=18/53.650162/10.161503) | [Way](https://www.openstreetmap.org/way/550871424) |
| `seg_99601bd306a75add` | Wandsbek | Nordlandweg | tertiary | 0.56 | 0.51 | 0.80 | nein | 50 | nein | 0.00 | 20 | [Karte](https://www.openstreetmap.org/?mlat=53.627439&mlon=10.163299#map=18/53.627439/10.163299) | [Way](https://www.openstreetmap.org/way/4265354) |
| `seg_b4dd5703096504be` | Wandsbek | Falkenhorst | residential | 0.03 | 0.30 | 0.07 | nein | 30 | nein | 0.00 | 233 | [Karte](https://www.openstreetmap.org/?mlat=53.625645&mlon=10.128023#map=18/53.625645/10.128023) | [Way](https://www.openstreetmap.org/way/18490229) |
| `seg_c342eec71151ce48` | Wandsbek | August-Krogmann-Straße | secondary | 0.80 | 0.40 | 0.97 | ja | 50 | – | 0.14 | 142 | [Karte](https://www.openstreetmap.org/?mlat=53.617401&mlon=10.113166#map=18/53.617401/10.113166) | [Way](https://www.openstreetmap.org/way/816627212) |
| `seg_c76090a05eee85f2` | Wandsbek | Stadtbahnstraße | primary | 0.96 | 0.65 | 0.97 | ja | 50 | nein | 1.00 | 55 | [Karte](https://www.openstreetmap.org/?mlat=53.653563&mlon=10.106468#map=18/53.653563/10.106468) | [Way](https://www.openstreetmap.org/way/464187409) |

## Lizenz

Abschnitte, POIs, Schulen, Kitas und Radnetz aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; abgeleitete Merkmale stehen ebenfalls unter ODbL. Gebäude: Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV), dl-de/by-2.0. Busfahrten: Hamburger Verkehrsverbund GmbH, dl-de/by-2.0. Einwohner: © Statistische Ämter des Bundes und der Länder, Zensus 2022, dl-de/by-2.0. Amtliche Attribute: Freie und Hansestadt Hamburg (Höchstgeschwindigkeiten und Verkehrsmengen: Lizenz in der API nicht angegeben, siehe docs/open_questions.md).
