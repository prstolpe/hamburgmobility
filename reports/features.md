# Merkmalsbericht – Stufe 4

Erzeugt: 2026-11-04T20:36:03+00:00 von `pipeline/s04_features.py`, rules.yaml 0.11.0. Nicht amtlicher Entwurf.

## Kennzahlen

- Abschnitte gesamt (Hamburg): 36 526; im Arbeitsgebiet (Eimsbüttel + 500 m): 4 947; davon im Bezirk Eimsbüttel: 4 004
- Betweenness: exakt (keine Stichprobe), ungerichtet, 34 375 Kfz-Abschnitte ganz Hamburgs, Laufzeit 57 s
- Reisezeit-Tempo im Arbeitsgebiet: official 81.1 %, osm 11.1 %, default 5.3 %, keins 2.5 %
- Ist-Tempo: amtlich 81.1 %, OSM 11.1 %, unbekannt 7.8 %; Konflikt amtlich ≠ OSM: 131 Abschnitte
- GTFS: repräsentativer Werktag 2026-04-29, 265 shapes, 0 Fahrten ohne shape
- Zensus-Gitter 100 m: 4274 Zellen im Arbeitsgebiet, Einwohner im 100-m-Puffer flächenanteilig; Zellen ohne Einwohner fehlen in der Datei und zählen 0; Werte durch Geheimhaltung leicht verändert
- ALKIS-Gebäude: 52 528 oberirdische Gebäude im Arbeitsgebiet (WFS_HH_ALKIS_vereinfacht, seit rules.yaml 0.6.0 statt OSM)

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

| Merkmal | Quelle | Regel | benötigt von | null Arbeitsgebiet | null Bezirk |
| --- | --- | --- | --- | ---: | ---: |
| `betweenness` | OSM-Netz + Tempo | S-FEAT-02 | Rohwert für betweenness_norm | 3.7 % | 3.9 % |
| `betweenness_norm` | OSM-Netz + Tempo | S-FEAT-01/02 | scores.conn_score | 3.7 % | 3.9 % |
| `in_hvs` | DTV-Linien HVS 2019 | S-CONF-04 | C-GOW-01, scores.conn_score | 0.0 % | 0.0 % |
| `bus_trips_weekday` | GTFS HVV | S-FEAT-08 | Rohwert für bus_trips_weekday_norm | 0.0 % | 0.0 % |
| `bus_trips_weekday_norm` | GTFS HVV | S-FEAT-01/08 | scores.conn_score | 0.0 % | 0.0 % |
| `dtv_official` | DTV-Linien HVS 2019 | S-CONF-01 | discrepancy.use, Rohwert für dtv_norm | 80.7 % | 80.3 % |
| `dtv_norm` | DTV-Linien HVS 2019 | S-FEAT-01 | scores.conn_score | 80.7 % | 80.3 % |
| `conn_score` | abgeleitet | scores.conn_score | C-RUR-01, C-GOW-01 | 0.0 % | 0.0 % |
| `conn_weight_available` | abgeleitet | scores.conn_score | missing_value_policy (confidence, Prompt 08) | 0.0 % | 0.0 % |
| `building_density` | ALKIS-Gebäude | S-FEAT-03 | Rohwert für building_density_norm | 0.0 % | 0.0 % |
| `building_density_norm` | ALKIS-Gebäude | S-FEAT-01/03 | scores.place_score | 0.0 % | 0.0 % |
| `population_100m` | Zensus 2022 Gitter | S-FEAT-04 | priority.risk_weights, Rohwert | 0.0 % | 0.0 % |
| `population_100m_norm` | Zensus 2022 Gitter | S-FEAT-01/04 | scores.place_score | 0.0 % | 0.0 % |
| `shop_frontage_share` | ALKIS-Gebäudefunktion + OSM shop/amenity | S-FEAT-05 | C-G30-01, scores.place_score (frontage_share) | 19.7 % | 16.3 % |
| `frontage_buildings` | ALKIS-Gebäude | S-FEAT-05 | Nenner von shop_frontage_share (Nachvollziehbarkeit) | 0.0 % | 0.0 % |
| `schools_or_kitas_within_m` | OSM Schulen/Kitas | S-FEAT-06 | C-G30-01, priority.school_kita_within_150m | 0.0 % | 0.0 % |
| `sensitive_facilities_norm` | OSM Schulen/Kitas | S-FEAT-01/06 | scores.place_score | 0.0 % | 0.0 % |
| `place_score` | abgeleitet | scores.place_score | Prompt 08/10 (Funktionskonflikt, Diskrepanz) | 0.0 % | 0.0 % |
| `place_weight_available` | abgeleitet | scores.place_score | missing_value_policy | 0.0 % | 0.0 % |
| `in_cycle_network` | OSM Radnetz Hamburg | S-FEAT-07 | priority.risk_weights.cycle_network, ETW30-Ausnahme | 0.0 % | 0.0 % |
| `speed_ist_kmh` | Tempo amtlich/OSM | S-FEAT-09 | discrepancy.speed | 7.8 % | 6.9 % |
| `speed_ist_source` | Tempo amtlich/OSM | S-FEAT-09 | Herkunft von speed_ist_kmh | 7.8 % | 6.9 % |
| `speed_sources_conflict` | Tempo amtlich/OSM | S-FEAT-09 | Unsicherheit (confidence) | 0.0 % | 0.0 % |
| `travel_speed_kmh` | Tempo amtlich/OSM/Standard | S-FEAT-02 | Gewicht der Betweenness | 2.5 % | 2.5 % |
| `travel_speed_source` | Tempo amtlich/OSM/Standard | S-FEAT-02 | Herkunft von travel_speed_kmh | 2.5 % | 2.5 % |
| `separated_cycle_track_present` | OSM-Tags | S-FEAT-10 | C-G30-02, requirements.*.cycling | 18.0 % | 17.7 % |
| `cycle_lane_present` | OSM-Tags | S-FEAT-10 | requirements.*.cycle_lanes_allowed | 18.0 % | 17.7 % |
| `lanes` | OSM-Tags | S-FEAT-10 | requirements.GOW50.median_if_lanes_per_dir_gte | 53.3 % | 53.5 % |
| `centre_line` | OSM-Tags | S-FEAT-10 | requirements.GOW30.centre_line | 83.9 % | 83.1 % |
| `parking` | OSM-Tags | S-FEAT-10 | Rohwert der Parkmerkmale | 56.9 % | 57.4 % |
| `parking_on_carriageway` | OSM-Tags | S-FEAT-10 | requirements.GOW30.parking_on_carriageway | 57.9 % | 58.1 % |
| `parking_along_carriageway` | OSM-Tags | S-FEAT-10 | requirements.GOW50.parking_along_carriageway | 57.9 % | 58.1 % |
| `angle_parking` | OSM-Tags | S-FEAT-10 | requirements.GOW50.angle_parking | 57.9 % | 58.1 % |
| `crossings_count` | OSM-Knoten | S-FEAT-10 | requirements.GOW50.crossings | 0.0 % | 0.0 % |
| `traffic_calming_count` | OSM-Knoten | S-FEAT-10 | requirements.ETW30.speed_reducer_spacing_m | 0.0 % | 0.0 % |
| `surface` | OSM-Tags | S-FEAT-10 | Erkennbarkeit (guide.md 1.2) | 0.5 % | 0.2 % |
| `access_motor_only` | OSM-Tags | S-FEAT-10 | C-SW-01 | 0.0 % | 0.0 % |
| `pedestrian_zone` | OSM-Tags | S-FEAT-10 | C-ERF-01 | 0.0 % | 0.0 % |
| `outside_builtup_area` | keine Quelle | – | C-RUR-01 (keine Datenquelle für die Ortsgrenze (docs/open_questions.md)) | 100.0 % | 100.0 % |
| `crossing_demand` | nicht definiert | – | C-G30-01 (in rules.yaml nicht definiert (docs/open_questions.md)) | 100.0 % | 100.0 % |
| `override_school_street` | overrides.csv (Prompt 09) | – | C-ERF-01 (kommt aus overrides/overrides.csv (Prompt 09)) | 100.0 % | 100.0 % |
| `width_p10_m` | Querschnitt (Prompt 07) | – | C-G30-02 (kommt aus dem Querschnitt (Prompt 07)) | 100.0 % | 100.0 % |

## Nullwertanteil je Datenquelle

| Quelle | Status (manifest) | Merkmale | mittlerer Nullanteil |
| --- | --- | --- | ---: |
| OSM-Netz + Tempo | – | `betweenness`, `betweenness_norm` | 3.7 % |
| DTV-Linien HVS 2019 | ok | `in_hvs`, `dtv_official`, `dtv_norm` | 53.8 % |
| GTFS HVV | ok | `bus_trips_weekday`, `bus_trips_weekday_norm` | 0.0 % |
| abgeleitet | – | `conn_score`, `conn_weight_available`, `place_score`, `place_weight_available` | 0.0 % |
| ALKIS-Gebäude | ok | `building_density`, `building_density_norm`, `frontage_buildings` | 0.0 % |
| Zensus 2022 Gitter | ok | `population_100m`, `population_100m_norm` | 0.0 % |
| ALKIS-Gebäudefunktion + OSM shop/amenity | – | `shop_frontage_share` | 19.7 % |
| OSM Schulen/Kitas | fallback | `schools_or_kitas_within_m`, `sensitive_facilities_norm` | 0.0 % |
| OSM Radnetz Hamburg | fallback | `in_cycle_network` | 0.0 % |
| Tempo amtlich/OSM | ok | `speed_ist_kmh`, `speed_ist_source`, `speed_sources_conflict` | 5.2 % |
| Tempo amtlich/OSM/Standard | – | `travel_speed_kmh`, `travel_speed_source` | 2.5 % |
| OSM-Tags | – | `separated_cycle_track_present`, `cycle_lane_present`, `lanes`, `centre_line`, `parking`, `parking_on_carriageway`, `parking_along_carriageway`, `angle_parking`, `surface`, `access_motor_only`, `pedestrian_zone` | 36.7 % |
| OSM-Knoten | – | `crossings_count`, `traffic_calming_count` | 0.0 % |
| keine Quelle | – | `outside_builtup_area` | 100.0 % |
| nicht definiert | – | `crossing_demand` | 100.0 % |
| overrides.csv (Prompt 09) | – | `override_school_street` | 100.0 % |
| Querschnitt (Prompt 07) | – | `width_p10_m` | 100.0 % |

## Verteilungen (Arbeitsgebiet)

### `betweenness`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 2.07e+06 | 4177 | ██████████████████████████████ |
| 2.07e+06 | 4.13e+06 | 276 | ██ |
| 4.13e+06 | 6.2e+06 | 107 | █ |
| 6.2e+06 | 8.27e+06 | 84 | █ |
| 8.27e+06 | 1.03e+07 | 27 |  |
| 1.03e+07 | 1.24e+07 | 18 |  |
| 1.24e+07 | 1.45e+07 | 37 |  |
| 1.45e+07 | 1.65e+07 | 10 |  |
| 1.65e+07 | 1.86e+07 | 19 |  |
| 1.86e+07 | 2.07e+07 | 8 |  |

### `betweenness_norm`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.1 | 477 | ██████████████████████ |
| 0.1 | 0.2 | 476 | ██████████████████████ |
| 0.2 | 0.3 | 659 | ██████████████████████████████ |
| 0.3 | 0.4 | 293 | █████████████ |
| 0.4 | 0.5 | 476 | ██████████████████████ |
| 0.5 | 0.6 | 477 | ██████████████████████ |
| 0.6 | 0.7 | 476 | ██████████████████████ |
| 0.7 | 0.8 | 476 | ██████████████████████ |
| 0.8 | 0.9 | 476 | ██████████████████████ |
| 0.9 | 1 | 477 | ██████████████████████ |

### `dtv_official`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 8e+03 | 2.03e+04 | 319 | ██████████████████████████████ |
| 2.03e+04 | 3.26e+04 | 323 | ██████████████████████████████ |
| 3.26e+04 | 4.49e+04 | 174 | ████████████████ |
| 4.49e+04 | 5.72e+04 | 81 | ████████ |
| 5.72e+04 | 6.95e+04 | 24 | ██ |
| 6.95e+04 | 8.18e+04 | 15 | █ |
| 8.18e+04 | 9.41e+04 | 8 | █ |
| 9.41e+04 | 1.06e+05 | 0 |  |
| 1.06e+05 | 1.19e+05 | 8 | █ |
| 1.19e+05 | 1.31e+05 | 2 |  |

### `building_density`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.0764 | 780 | █████████████ |
| 0.0764 | 0.153 | 1154 | ████████████████████ |
| 0.153 | 0.229 | 1739 | ██████████████████████████████ |
| 0.229 | 0.306 | 703 | ████████████ |
| 0.306 | 0.382 | 400 | ███████ |
| 0.382 | 0.458 | 125 | ██ |
| 0.458 | 0.535 | 26 |  |
| 0.535 | 0.611 | 11 |  |
| 0.611 | 0.688 | 6 |  |
| 0.688 | 0.764 | 3 |  |

### `shop_frontage_share`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.1 | 1688 | ██████████████████████████████ |
| 0.1 | 0.2 | 381 | ███████ |
| 0.2 | 0.3 | 343 | ██████ |
| 0.3 | 0.4 | 223 | ████ |
| 0.4 | 0.5 | 109 | ██ |
| 0.5 | 0.6 | 300 | █████ |
| 0.6 | 0.7 | 99 | ██ |
| 0.7 | 0.8 | 72 | █ |
| 0.8 | 0.9 | 72 | █ |
| 0.9 | 1 | 687 | ████████████ |

### `schools_or_kitas_within_m`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 169 | 2672 | ██████████████████████████████ |
| 169 | 338 | 1166 | █████████████ |
| 338 | 507 | 595 | ███████ |
| 507 | 675 | 273 | ███ |
| 675 | 844 | 161 | ██ |
| 844 | 1.01e+03 | 63 | █ |
| 1.01e+03 | 1.18e+03 | 16 |  |
| 1.18e+03 | 1.35e+03 | 0 |  |
| 1.35e+03 | 1.52e+03 | 0 |  |
| 1.52e+03 | 1.69e+03 | 1 |  |

### `speed_ist_kmh`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 10 | 19 | 19 |  |
| 19 | 28 | 25 |  |
| 28 | 37 | 2297 | ██████████████████████████████ |
| 37 | 46 | 2 |  |
| 46 | 55 | 2118 | ████████████████████████████ |
| 55 | 64 | 48 | █ |
| 64 | 73 | 15 |  |
| 73 | 82 | 19 |  |
| 82 | 91 | 0 |  |
| 91 | 100 | 18 |  |

### `lanes`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 1 | 1.6 | 444 | ██████████ |
| 1.6 | 2.2 | 1286 | ██████████████████████████████ |
| 2.2 | 2.8 | 0 |  |
| 2.8 | 3.4 | 336 | ████████ |
| 3.4 | 4 | 0 |  |
| 4 | 4.6 | 181 | ████ |
| 4.6 | 5.2 | 35 | █ |
| 5.2 | 5.8 | 0 |  |
| 5.8 | 6.4 | 22 | █ |
| 6.4 | 7 | 7 |  |

### `crossings_count`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.5 | 2997 | ██████████████████████████████ |
| 0.5 | 1 | 0 |  |
| 1 | 1.5 | 1513 | ███████████████ |
| 1.5 | 2 | 0 |  |
| 2 | 2.5 | 375 | ████ |
| 2.5 | 3 | 0 |  |
| 3 | 3.5 | 52 | █ |
| 3.5 | 4 | 0 |  |
| 4 | 4.5 | 9 |  |
| 4.5 | 5 | 1 |  |

### `conn_score`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.099 | 1632 | ██████████████████████████████ |
| 0.099 | 0.198 | 472 | █████████ |
| 0.198 | 0.297 | 886 | ████████████████ |
| 0.297 | 0.396 | 384 | ███████ |
| 0.396 | 0.495 | 221 | ████ |
| 0.495 | 0.594 | 438 | ████████ |
| 0.594 | 0.693 | 227 | ████ |
| 0.693 | 0.792 | 296 | █████ |
| 0.792 | 0.891 | 233 | ████ |
| 0.891 | 0.99 | 158 | ███ |

### `place_score`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.0958 | 270 | ██████████ |
| 0.0958 | 0.192 | 441 | ████████████████ |
| 0.192 | 0.287 | 451 | ████████████████ |
| 0.287 | 0.383 | 660 | ████████████████████████ |
| 0.383 | 0.479 | 820 | ██████████████████████████████ |
| 0.479 | 0.575 | 733 | ███████████████████████████ |
| 0.575 | 0.671 | 582 | █████████████████████ |
| 0.671 | 0.766 | 457 | █████████████████ |
| 0.766 | 0.862 | 407 | ███████████████ |
| 0.862 | 0.958 | 126 | █████ |

### `conn_weight_available`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0.45 | 0.505 | 164 | █ |
| 0.505 | 0.56 | 0 |  |
| 0.56 | 0.615 | 0 |  |
| 0.615 | 0.67 | 20 |  |
| 0.67 | 0.725 | 0 |  |
| 0.725 | 0.78 | 0 |  |
| 0.78 | 0.835 | 3829 | ██████████████████████████████ |
| 0.835 | 0.89 | 0 |  |
| 0.89 | 0.945 | 0 |  |
| 0.945 | 1 | 934 | ███████ |

### Kategoriale Merkmale

| Merkmal | Werte (Anteil der Abschnitte) |
| --- | --- |
| `in_hvs` | False: 81.3 %, True: 18.7 % |
| `in_cycle_network` | False: 91.6 %, True: 8.4 % |
| `separated_cycle_track_present` | False: 58.0 %, True: 24.0 %, null: 18.0 % |
| `cycle_lane_present` | False: 74.3 %, null: 18.0 %, True: 7.7 % |
| `centre_line` | null: 83.9 %, False: 16.0 %, True: 0.1 % |
| `parking_on_carriageway` | null: 57.9 %, False: 31.2 %, True: 11.0 % |
| `parking_along_carriageway` | null: 57.9 %, False: 25.7 %, True: 16.5 % |
| `angle_parking` | null: 57.9 %, False: 39.4 %, True: 2.7 % |
| `surface` | asphalt: 88.1 %, paving_stones: 5.8 %, sett: 4.9 %, null: 0.5 %, unhewn_cobblestone: 0.3 %, compacted: 0.3 %, unpaved: 0.0 %, dirt: 0.0 % |
| `access_motor_only` | False: 97.6 %, True: 2.4 % |
| `pedestrian_zone` | False: 98.0 %, True: 2.0 % |
| `speed_sources_conflict` | False: 97.4 %, True: 2.6 % |

### conn_score nach highway-Klasse (Median)

| highway | Abschnitte | conn_score | place_score |
| --- | ---: | ---: | ---: |
| living_street | 159 | 0.10 | 0.39 |
| motorway | 29 | 0.53 | 0.19 |
| motorway_link | 90 | 0.25 | 0.12 |
| pedestrian | 97 | 0.00 | 0.65 |
| primary | 646 | 0.82 | 0.46 |
| primary_link | 31 | 0.24 | 0.53 |
| residential | 2524 | 0.15 | 0.47 |
| secondary | 434 | 0.66 | 0.42 |
| secondary_link | 24 | 0.40 | 0.20 |
| service | 66 | 0.00 | 0.39 |
| tertiary | 685 | 0.44 | 0.51 |
| tertiary_link | 17 | 0.36 | 0.42 |
| track | 21 | 0.00 | 0.09 |
| trunk | 3 | 0.96 | 0.06 |
| unclassified | 121 | 0.10 | 0.28 |

## Stichprobe (30 zufällige Abschnitte im Bezirk Eimsbüttel, Seed 42)

Links auf OSM-Karte und OSM-Way. Orthophoto- und Panoramax-Links folgen, sobald das Linkformat geklärt ist (docs/open_questions.md).

| segment_id | Name | highway | conn | place | betw. | HVS | Tempo | Radweg | Front. | Schule/Kita m | Karte | Way |
| --- | --- | --- | ---: | ---: | ---: | --- | ---: | --- | ---: | ---: | --- | --- |
| `seg_06c51c323ecec35f` | Sachsenweg | residential | 0.19 | 0.40 | 0.44 | nein | 30 | – | 0.50 | 32 | [Karte](https://www.openstreetmap.org/?mlat=53.643495&mlon=9.960601#map=18/53.643495/9.960601) | [Way](https://www.openstreetmap.org/way/1018232732) |
| `seg_0796a6ac6a25cf94` | Bogenstraße | tertiary | 0.27 | 0.63 | 0.63 | nein | 50 | ja | – | 221 | [Karte](https://www.openstreetmap.org/?mlat=53.571076&mlon=9.978445#map=18/53.571076/9.978445) | [Way](https://www.openstreetmap.org/way/238921530) |
| `seg_085fcf760eb5e9c1` | Lohkampstraße | tertiary | 0.55 | 0.22 | 0.80 | nein | 50 | ja | 0.07 | 535 | [Karte](https://www.openstreetmap.org/?mlat=53.615241&mlon=9.877703#map=18/53.615241/9.877703) | [Way](https://www.openstreetmap.org/way/4919897) |
| `seg_0906305a37756fb1` | Krähenweg | tertiary | 0.31 | 0.62 | 0.71 | nein | 50 | nein | 1.00 | 128 | [Karte](https://www.openstreetmap.org/?mlat=53.633004&mlon=9.954534#map=18/53.633004/9.954534) | [Way](https://www.openstreetmap.org/way/1165983748) |
| `seg_16df18fb7177523d` | Alte Rabenstraße | residential | 0.09 | 0.59 | 0.21 | nein | 30 | nein | 1.00 | 157 | [Karte](https://www.openstreetmap.org/?mlat=53.567259&mlon=10.000605#map=18/53.567259/10.000605) | [Way](https://www.openstreetmap.org/way/16232763) |
| `seg_1885bcb6c1f638e2` | Heketweg | service | 0.00 | 0.40 | – | nein | 30 | – | 0.00 | 48 | [Karte](https://www.openstreetmap.org/?mlat=53.650543&mlon=9.908991#map=18/53.650543/9.908991) | [Way](https://www.openstreetmap.org/way/186967128) |
| `seg_1abf10d7274d8422` | Rahweg | residential | 0.19 | 0.25 | 0.43 | nein | 30 | nein | 0.05 | 887 | [Karte](https://www.openstreetmap.org/?mlat=53.641256&mlon=9.977482#map=18/53.641256/9.977482) | [Way](https://www.openstreetmap.org/way/148170157) |
| `seg_1d42b16a862590fe` | Bei der Lutherbuche | residential | 0.10 | 0.41 | 0.22 | nein | 30 | nein | 0.00 | 103 | [Karte](https://www.openstreetmap.org/?mlat=53.597870&mlon=9.962414#map=18/53.597870/9.962414) | [Way](https://www.openstreetmap.org/way/465938393) |
| `seg_25316f77fd2a2a9c` | Heußweg | tertiary | 0.58 | 0.86 | 0.85 | nein | 50 | nein | 1.00 | 61 | [Karte](https://www.openstreetmap.org/?mlat=53.577094&mlon=9.951971#map=18/53.577094/9.951971) | [Way](https://www.openstreetmap.org/way/367080898) |
| `seg_33cb6ed3e7ffbd56` | Doormannsweg | primary | 0.64 | 0.41 | 0.93 | nein | 50 | ja | – | 166 | [Karte](https://www.openstreetmap.org/?mlat=53.570394&mlon=9.955995#map=18/53.570394/9.955995) | [Way](https://www.openstreetmap.org/way/143710276) |
| `seg_38926833099b9b94` | Schlüterstraße | pedestrian | 0.00 | 0.58 | – | nein | 30 | – | 0.33 | 133 | [Karte](https://www.openstreetmap.org/?mlat=53.567025&mlon=9.986511#map=18/53.567025/9.986511) | [Way](https://www.openstreetmap.org/way/738633624) |
| `seg_3a464de2b19a6893` | Vielohweg | tertiary | 0.38 | 0.55 | 0.35 | nein | 50 | ja | – | 74 | [Karte](https://www.openstreetmap.org/?mlat=53.638404&mlon=9.923778#map=18/53.638404/9.923778) | [Way](https://www.openstreetmap.org/way/1018245714) |
| `seg_3c7f89d9293122a6` | Gandersheimer Weg | residential | 0.07 | 0.62 | 0.17 | nein | 30 | nein | 0.03 | 9 | [Karte](https://www.openstreetmap.org/?mlat=53.630804&mlon=9.942861#map=18/53.630804/9.942861) | [Way](https://www.openstreetmap.org/way/1182341953) |
| `seg_3fadede7b82f43f3` | Lauterberger Weg | residential | 0.04 | 0.48 | 0.09 | nein | 30 | nein | 0.04 | 114 | [Karte](https://www.openstreetmap.org/?mlat=53.625898&mlon=9.942608#map=18/53.625898/9.942608) | [Way](https://www.openstreetmap.org/way/4302356) |
| `seg_4837b087ed325fa2` | Vogt-Kölln-Straße | tertiary | 0.52 | 0.23 | 0.74 | nein | 50 | nein | 0.06 | 223 | [Karte](https://www.openstreetmap.org/?mlat=53.607743&mlon=9.927913#map=18/53.607743/9.927913) | [Way](https://www.openstreetmap.org/way/167262195) |
| `seg_6d5977fd43d3ba6c` | Burgwedeltwiete | residential | 0.10 | 0.34 | 0.22 | nein | 30 | – | 0.05 | 345 | [Karte](https://www.openstreetmap.org/?mlat=53.642727&mlon=9.911655#map=18/53.642727/9.911655) | [Way](https://www.openstreetmap.org/way/23780951) |
| `seg_84ea9801ae9fdb64` | Kollaustraße | primary | 0.90 | 0.34 | 0.95 | ja | 50 | ja | 0.50 | 150 | [Karte](https://www.openstreetmap.org/?mlat=53.604111&mlon=9.961662#map=18/53.604111/9.961662) | [Way](https://www.openstreetmap.org/way/650779284) |
| `seg_8f5c71cc17760317` | Levkojenweg | service | 0.00 | 0.23 | – | nein | – | – | 0.00 | 535 | [Karte](https://www.openstreetmap.org/?mlat=53.614969&mlon=9.878638#map=18/53.614969/9.878638) | [Way](https://www.openstreetmap.org/way/1346846914) |
| `seg_9393b66447f464b6` | Bei der Apostelkirche | residential | 0.00 | 0.68 | 0.00 | nein | 30 | nein | 0.17 | 115 | [Karte](https://www.openstreetmap.org/?mlat=53.575495&mlon=9.943669#map=18/53.575495/9.943669) | [Way](https://www.openstreetmap.org/way/1071074636) |
| `seg_9bd1744203202163` | Wunderbrunnen | unclassified | 0.45 | 0.14 | 0.61 | nein | 50 | nein | 0.00 | 329 | [Karte](https://www.openstreetmap.org/?mlat=53.643433&mlon=9.927441#map=18/53.643433/9.927441) | [Way](https://www.openstreetmap.org/way/22651253) |
| `seg_9eb122117042b96b` | Garstedter Weg | secondary | 0.58 | 0.18 | 0.83 | nein | 50 | ja | – | 400 | [Karte](https://www.openstreetmap.org/?mlat=53.622682&mlon=9.954858#map=18/53.622682/9.954858) | [Way](https://www.openstreetmap.org/way/159656516) |
| `seg_a869cf09b6234160` | Vogt-Wells-Straße | primary | 0.96 | 0.63 | 1.00 | ja | 50 | nein | 1.00 | 84 | [Karte](https://www.openstreetmap.org/?mlat=53.599762&mlon=9.963777#map=18/53.599762/9.963777) | [Way](https://www.openstreetmap.org/way/230609914) |
| `seg_aac2b2469aadbb68` | Harvestehuder Weg | residential | 0.09 | 0.21 | 0.21 | nein | 30 | nein | – | 359 | [Karte](https://www.openstreetmap.org/?mlat=53.578321&mlon=9.997483#map=18/53.578321/9.997483) | [Way](https://www.openstreetmap.org/way/710544692) |
| `seg_b14dd9d1cd005339` | Herulerweg | unclassified | 0.03 | 0.05 | 0.07 | nein | 50 | ja | 0.00 | 806 | [Karte](https://www.openstreetmap.org/?mlat=53.650258&mlon=9.949240#map=18/53.650258/9.949240) | [Way](https://www.openstreetmap.org/way/25739516) |
| `seg_b88b298d46679b5e` | Vereinsstraße | residential | 0.16 | 0.77 | 0.37 | nein | 30 | nein | 0.20 | 60 | [Karte](https://www.openstreetmap.org/?mlat=53.565824&mlon=9.962228#map=18/53.565824/9.962228) | [Way](https://www.openstreetmap.org/way/736612811) |
| `seg_bc75c394f223eb26` | Vielohwisch | unclassified | 0.10 | 0.06 | 0.22 | nein | 50 | – | 0.00 | 562 | [Karte](https://www.openstreetmap.org/?mlat=53.638235&mlon=9.933887#map=18/53.638235/9.933887) | [Way](https://www.openstreetmap.org/way/8379199) |
| `seg_c232d0e509b97fa5` | Burgwedelkamp | residential | 0.49 | 0.19 | 0.67 | nein | 50 | – | 0.00 | 402 | [Karte](https://www.openstreetmap.org/?mlat=53.641930&mlon=9.911588#map=18/53.641930/9.911588) | [Way](https://www.openstreetmap.org/way/4089419) |
| `seg_c330d48355534e10` | Hohe Weide | residential | 0.16 | 0.68 | 0.37 | nein | 30 | nein | 0.07 | 18 | [Karte](https://www.openstreetmap.org/?mlat=53.576150&mlon=9.973005#map=18/53.576150/9.973005) | [Way](https://www.openstreetmap.org/way/137037866) |
| `seg_c36cd78befbd0aa8` | Lüttenredder | residential | 0.24 | 0.53 | 0.54 | nein | 30 | – | 0.00 | 50 | [Karte](https://www.openstreetmap.org/?mlat=53.645107&mlon=9.914883#map=18/53.645107/9.914883) | [Way](https://www.openstreetmap.org/way/23780954) |
| `seg_e9677794317ea023` | Niendorfer Straße | secondary | 0.06 | 0.40 | 0.13 | nein | – | ja | 1.00 | 520 | [Karte](https://www.openstreetmap.org/?mlat=53.610757&mlon=9.957467#map=18/53.610757/9.957467) | [Way](https://www.openstreetmap.org/way/586238234) |

## Lizenz

Abschnitte, POIs, Schulen, Kitas und Radnetz aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; abgeleitete Merkmale stehen ebenfalls unter ODbL. Gebäude: Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV), dl-de/by-2.0. Busfahrten: Hamburger Verkehrsverbund GmbH, dl-de/by-2.0. Einwohner: © Statistische Ämter des Bundes und der Länder, Zensus 2022, dl-de/by-2.0. Amtliche Attribute: Freie und Hansestadt Hamburg (Höchstgeschwindigkeiten und Verkehrsmengen: Lizenz in der API nicht angegeben, siehe docs/open_questions.md).
