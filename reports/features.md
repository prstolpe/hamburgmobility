# Merkmalsbericht – Stufe 4

Erzeugt: 2026-10-28T10:53:33+00:00 von `pipeline/s04_features.py`, rules.yaml 0.5.0. Nicht amtlicher Entwurf.

## Kennzahlen

- Abschnitte gesamt (Hamburg): 34 502; im Arbeitsgebiet (Eimsbüttel + 500 m): 4 787; davon im Bezirk Eimsbüttel: 3 876
- Betweenness: exakt (keine Stichprobe), ungerichtet, 33 798 Kfz-Abschnitte ganz Hamburgs, Laufzeit 54 s
- Reisezeit-Tempo im Arbeitsgebiet: official 81.4 %, osm 11.3 %, default 5.5 %, keins 1.8 %
- Ist-Tempo: amtlich 81.4 %, OSM 11.3 %, unbekannt 7.3 %; Konflikt amtlich ≠ OSM: 131 Abschnitte
- GTFS: repräsentativer Werktag 2026-04-29, 265 shapes, 0 Fahrten ohne shape
- Zensus-Gitter 100 m: 4274 Zellen im Arbeitsgebiet, Einwohner im 100-m-Puffer flächenanteilig; Zellen ohne Einwohner fehlen in der Datei und zählen 0; Werte durch Geheimhaltung leicht verändert
- ALKIS: fehlt – Gebäude und Gebäudefunktion vorläufig aus OSM (Entscheidung 2026-10-28)

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 34502 Abschnitte |
| Normwerte und Scores in [0, 1] | ok | alle |
| conn_score im Arbeitsgebiet vollständig | ok | 0 ohne conn_score |
| Betweenness für alle Kfz-Abschnitte | ok | 0 ohne Wert |

## Methode

- **Normierung (S-FEAT-01):** Perzentilrang über alle Abschnitte im Arbeitsgebiet mit bekanntem Wert, (Rang − 1) / (n − 1); gleiche Werte erhalten den kleinsten Rang ihrer Gruppe (rules.yaml 0.5.0), damit der kleinste Wert – z. B. 0 Busfahrten – auf 0 fällt. 1 = größter Wert. `in_hvs` geht als 0/1 ein, `shop_frontage_share` unverändert. `sensitive_facilities_norm` ist der Perzentilrang der negativen Entfernung (nah = hoch). Die Normierung hängt vom Arbeitsgebiet ab; bei Ausweitung auf ganz Hamburg ändern sich die Werte.
- **Fehlende Werte:** bleiben null. conn_score und place_score legen das Gewicht fehlender Merkmale anteilig auf die übrigen um (missing_value_policy); `conn_weight_available`/`place_weight_available` zeigen, welcher Gewichtsanteil Werte hatte. Die Herabstufung der confidence folgt in Prompt 08.
- **Betweenness (S-FEAT-02):** Reisezeit = Länge / Tempo (amtlich → OSM maxspeed → Standardwert je Klasse). Ohne pedestrian. Mehrere OSM-Werte je Abschnitt (z. B. „50 / 30“) gelten als unbekannt.
- **Gebäudedichte (S-FEAT-03):** OSM-Gebäudegrundfläche im 50-m-Puffer / Pufferfläche.
- **Publikumsnutzung (S-FEAT-05):** Anteil der Gebäude im 20-m-Puffer mit shop/amenity (Tag am Gebäude oder POI darin), ohne Stadtmöblierung (amenity_excluded). Das Geschoss wird nicht geprüft.
- **Radnetz, Busfahrten (S-FEAT-07/08):** Längenanteil wie S-CONF-02 (Puffer, Winkel, Mindestanteil).
- **Ist-Gestaltung (S-FEAT-10):** Mehrheitswert über die Ways des Abschnitts (Gewicht: Länge im 1-m-Puffer). Kein Tag = unbekannt (null), nicht „nein“. Querungen und Verkehrsberuhigung: OSM-Knoten höchstens 1 m vom Abschnitt. `access_motor_only`: motorway/motorway_link oder motorroad=yes (sonst nein, weil motorroad nur positiv erfasst wird).

## Nullwertanteil je Merkmal (Arbeitsgebiet)

| Merkmal | Quelle | Regel | benötigt von | null Arbeitsgebiet | null Bezirk |
| --- | --- | --- | --- | ---: | ---: |
| `betweenness` | OSM-Netz + Tempo | S-FEAT-02 | Rohwert für betweenness_norm | 2.0 % | 2.2 % |
| `betweenness_norm` | OSM-Netz + Tempo | S-FEAT-01/02 | scores.conn_score | 2.0 % | 2.2 % |
| `in_hvs` | DTV-Linien HVS 2019 | S-CONF-04 | C-GOW-01, scores.conn_score | 0.0 % | 0.0 % |
| `bus_trips_weekday` | GTFS HVV | S-FEAT-08 | Rohwert für bus_trips_weekday_norm | 0.0 % | 0.0 % |
| `bus_trips_weekday_norm` | GTFS HVV | S-FEAT-01/08 | scores.conn_score | 0.0 % | 0.0 % |
| `dtv_official` | DTV-Linien HVS 2019 | S-CONF-01 | discrepancy.use, Rohwert für dtv_norm | 80.8 % | 80.4 % |
| `dtv_norm` | DTV-Linien HVS 2019 | S-FEAT-01 | scores.conn_score | 80.8 % | 80.4 % |
| `conn_score` | abgeleitet | scores.conn_score | C-RUR-01, C-GOW-01 | 0.0 % | 0.0 % |
| `conn_weight_available` | abgeleitet | scores.conn_score | missing_value_policy (confidence, Prompt 08) | 0.0 % | 0.0 % |
| `building_density` | OSM-Gebäude | S-FEAT-03 | Rohwert für building_density_norm | 0.0 % | 0.0 % |
| `building_density_norm` | OSM-Gebäude | S-FEAT-01/03 | scores.place_score | 0.0 % | 0.0 % |
| `population_100m` | Zensus 2022 Gitter | S-FEAT-04 | priority.risk_weights, Rohwert | 0.0 % | 0.0 % |
| `population_100m_norm` | Zensus 2022 Gitter | S-FEAT-01/04 | scores.place_score | 0.0 % | 0.0 % |
| `shop_frontage_share` | OSM shop/amenity | S-FEAT-05 | C-G30-01, scores.place_score (frontage_share) | 14.5 % | 13.6 % |
| `frontage_buildings` | OSM-Gebäude | S-FEAT-05 | Nenner von shop_frontage_share (Nachvollziehbarkeit) | 0.0 % | 0.0 % |
| `schools_or_kitas_within_m` | OSM Schulen/Kitas | S-FEAT-06 | C-G30-01, priority.school_kita_within_150m | 0.0 % | 0.0 % |
| `sensitive_facilities_norm` | OSM Schulen/Kitas | S-FEAT-01/06 | scores.place_score | 0.0 % | 0.0 % |
| `place_score` | abgeleitet | scores.place_score | Prompt 08/10 (Funktionskonflikt, Diskrepanz) | 0.0 % | 0.0 % |
| `place_weight_available` | abgeleitet | scores.place_score | missing_value_policy | 0.0 % | 0.0 % |
| `in_cycle_network` | OSM Radnetz Hamburg | S-FEAT-07 | priority.risk_weights.cycle_network, ETW30-Ausnahme | 0.0 % | 0.0 % |
| `speed_ist_kmh` | Tempo amtlich/OSM | S-FEAT-09 | discrepancy.speed | 7.3 % | 6.5 % |
| `speed_ist_source` | Tempo amtlich/OSM | S-FEAT-09 | Herkunft von speed_ist_kmh | 7.3 % | 6.5 % |
| `speed_sources_conflict` | Tempo amtlich/OSM | S-FEAT-09 | Unsicherheit (confidence) | 0.0 % | 0.0 % |
| `travel_speed_kmh` | Tempo amtlich/OSM/Standard | S-FEAT-02 | Gewicht der Betweenness | 1.8 % | 2.0 % |
| `travel_speed_source` | Tempo amtlich/OSM/Standard | S-FEAT-02 | Herkunft von travel_speed_kmh | 1.8 % | 2.0 % |
| `separated_cycle_track_present` | OSM-Tags | S-FEAT-10 | C-G30-02, requirements.*.cycling | 17.1 % | 16.7 % |
| `cycle_lane_present` | OSM-Tags | S-FEAT-10 | requirements.*.cycle_lanes_allowed | 17.1 % | 16.7 % |
| `lanes` | OSM-Tags | S-FEAT-10 | requirements.GOW50.median_if_lanes_per_dir_gte | 52.9 % | 53.1 % |
| `centre_line` | OSM-Tags | S-FEAT-10 | requirements.GOW30.centre_line | 83.7 % | 82.9 % |
| `parking` | OSM-Tags | S-FEAT-10 | Rohwert der Parkmerkmale | 56.1 % | 56.6 % |
| `parking_on_carriageway` | OSM-Tags | S-FEAT-10 | requirements.GOW30.parking_on_carriageway | 57.1 % | 57.4 % |
| `parking_along_carriageway` | OSM-Tags | S-FEAT-10 | requirements.GOW50.parking_along_carriageway | 57.1 % | 57.4 % |
| `angle_parking` | OSM-Tags | S-FEAT-10 | requirements.GOW50.angle_parking | 57.1 % | 57.4 % |
| `crossings_count` | OSM-Knoten | S-FEAT-10 | requirements.GOW50.crossings | 0.0 % | 0.0 % |
| `traffic_calming_count` | OSM-Knoten | S-FEAT-10 | requirements.ETW30.speed_reducer_spacing_m | 0.0 % | 0.0 % |
| `surface` | OSM-Tags | S-FEAT-10 | Erkennbarkeit (guide.md 1.2) | 0.5 % | 0.1 % |
| `access_motor_only` | OSM-Tags | S-FEAT-10 | C-SW-01 | 0.0 % | 0.0 % |
| `pedestrian_zone` | OSM-Tags | S-FEAT-10 | C-ERF-01 | 0.0 % | 0.0 % |
| `outside_builtup_area` | keine Quelle | – | C-RUR-01 (keine Datenquelle für die Ortsgrenze (docs/open_questions.md)) | 100.0 % | 100.0 % |
| `crossing_demand` | nicht definiert | – | C-G30-01 (in rules.yaml nicht definiert (docs/open_questions.md)) | 100.0 % | 100.0 % |
| `override_school_street` | overrides.csv (Prompt 09) | – | C-ERF-01 (kommt aus overrides/overrides.csv (Prompt 09)) | 100.0 % | 100.0 % |
| `width_p10_m` | Querschnitt (Prompt 07) | – | C-G30-02 (kommt aus dem Querschnitt (Prompt 07)) | 100.0 % | 100.0 % |

## Nullwertanteil je Datenquelle

| Quelle | Status (manifest) | Merkmale | mittlerer Nullanteil |
| --- | --- | --- | ---: |
| OSM-Netz + Tempo | – | `betweenness`, `betweenness_norm` | 2.0 % |
| DTV-Linien HVS 2019 | ok | `in_hvs`, `dtv_official`, `dtv_norm` | 53.9 % |
| GTFS HVV | ok | `bus_trips_weekday`, `bus_trips_weekday_norm` | 0.0 % |
| abgeleitet | – | `conn_score`, `conn_weight_available`, `place_score`, `place_weight_available` | 0.0 % |
| OSM-Gebäude | – | `building_density`, `building_density_norm`, `frontage_buildings` | 0.0 % |
| Zensus 2022 Gitter | ok | `population_100m`, `population_100m_norm` | 0.0 % |
| OSM shop/amenity | – | `shop_frontage_share` | 14.5 % |
| OSM Schulen/Kitas | fallback | `schools_or_kitas_within_m`, `sensitive_facilities_norm` | 0.0 % |
| OSM Radnetz Hamburg | fallback | `in_cycle_network` | 0.0 % |
| Tempo amtlich/OSM | ok | `speed_ist_kmh`, `speed_ist_source`, `speed_sources_conflict` | 4.8 % |
| Tempo amtlich/OSM/Standard | – | `travel_speed_kmh`, `travel_speed_source` | 1.8 % |
| OSM-Tags | – | `separated_cycle_track_present`, `cycle_lane_present`, `lanes`, `centre_line`, `parking`, `parking_on_carriageway`, `parking_along_carriageway`, `angle_parking`, `surface`, `access_motor_only`, `pedestrian_zone` | 36.2 % |
| OSM-Knoten | – | `crossings_count`, `traffic_calming_count` | 0.0 % |
| keine Quelle | – | `outside_builtup_area` | 100.0 % |
| nicht definiert | – | `crossing_demand` | 100.0 % |
| overrides.csv (Prompt 09) | – | `override_school_street` | 100.0 % |
| Querschnitt (Prompt 07) | – | `width_p10_m` | 100.0 % |

## Verteilungen (Arbeitsgebiet)

### `betweenness`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 1.99e+06 | 4113 | ██████████████████████████████ |
| 1.99e+06 | 3.98e+06 | 274 | ██ |
| 3.98e+06 | 5.97e+06 | 101 | █ |
| 5.97e+06 | 7.96e+06 | 85 | █ |
| 7.96e+06 | 9.94e+06 | 26 |  |
| 9.94e+06 | 1.19e+07 | 19 |  |
| 1.19e+07 | 1.39e+07 | 36 |  |
| 1.39e+07 | 1.59e+07 | 10 |  |
| 1.59e+07 | 1.79e+07 | 18 |  |
| 1.79e+07 | 1.99e+07 | 8 |  |

### `betweenness_norm`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.1 | 469 | █████████████████████ |
| 0.1 | 0.2 | 469 | █████████████████████ |
| 0.2 | 0.3 | 673 | ██████████████████████████████ |
| 0.3 | 0.4 | 265 | ████████████ |
| 0.4 | 0.5 | 469 | █████████████████████ |
| 0.5 | 0.6 | 469 | █████████████████████ |
| 0.6 | 0.7 | 469 | █████████████████████ |
| 0.7 | 0.8 | 469 | █████████████████████ |
| 0.8 | 0.9 | 469 | █████████████████████ |
| 0.9 | 1 | 469 | █████████████████████ |

### `dtv_official`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 8e+03 | 2.03e+04 | 303 | █████████████████████████████ |
| 2.03e+04 | 3.26e+04 | 312 | ██████████████████████████████ |
| 3.26e+04 | 4.49e+04 | 172 | █████████████████ |
| 4.49e+04 | 5.72e+04 | 78 | ████████ |
| 5.72e+04 | 6.95e+04 | 23 | ██ |
| 6.95e+04 | 8.18e+04 | 12 | █ |
| 8.18e+04 | 9.41e+04 | 8 | █ |
| 9.41e+04 | 1.06e+05 | 0 |  |
| 1.06e+05 | 1.19e+05 | 8 | █ |
| 1.19e+05 | 1.31e+05 | 2 |  |

### `building_density`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.0721 | 545 | █████████ |
| 0.0721 | 0.144 | 914 | ███████████████ |
| 0.144 | 0.216 | 1795 | ██████████████████████████████ |
| 0.216 | 0.288 | 816 | ██████████████ |
| 0.288 | 0.361 | 484 | ████████ |
| 0.361 | 0.433 | 174 | ███ |
| 0.433 | 0.505 | 39 | █ |
| 0.505 | 0.577 | 10 |  |
| 0.577 | 0.649 | 8 |  |
| 0.649 | 0.721 | 2 |  |

### `shop_frontage_share`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.1 | 2591 | ██████████████████████████████ |
| 0.1 | 0.2 | 269 | ███ |
| 0.2 | 0.3 | 246 | ███ |
| 0.3 | 0.4 | 173 | ██ |
| 0.4 | 0.5 | 71 | █ |
| 0.5 | 0.6 | 214 | ██ |
| 0.6 | 0.7 | 92 | █ |
| 0.7 | 0.8 | 54 | █ |
| 0.8 | 0.9 | 73 | █ |
| 0.9 | 1 | 310 | ████ |

### `schools_or_kitas_within_m`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 1.52 | 170 | 2624 | ██████████████████████████████ |
| 170 | 339 | 1127 | █████████████ |
| 339 | 508 | 560 | ██████ |
| 508 | 676 | 245 | ███ |
| 676 | 845 | 155 | ██ |
| 845 | 1.01e+03 | 63 | █ |
| 1.01e+03 | 1.18e+03 | 12 |  |
| 1.18e+03 | 1.35e+03 | 0 |  |
| 1.35e+03 | 1.52e+03 | 0 |  |
| 1.52e+03 | 1.69e+03 | 1 |  |

### `speed_ist_kmh`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 10 | 19 | 18 |  |
| 19 | 28 | 24 |  |
| 28 | 37 | 2236 | ██████████████████████████████ |
| 37 | 46 | 2 |  |
| 46 | 55 | 2059 | ████████████████████████████ |
| 55 | 64 | 48 | █ |
| 64 | 73 | 15 |  |
| 73 | 82 | 19 |  |
| 82 | 91 | 0 |  |
| 91 | 100 | 18 |  |

### `lanes`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 1 | 1.6 | 427 | ██████████ |
| 1.6 | 2.2 | 1259 | ██████████████████████████████ |
| 2.2 | 2.8 | 0 |  |
| 2.8 | 3.4 | 330 | ████████ |
| 3.4 | 4 | 0 |  |
| 4 | 4.6 | 176 | ████ |
| 4.6 | 5.2 | 35 | █ |
| 5.2 | 5.8 | 0 |  |
| 5.8 | 6.4 | 22 | █ |
| 6.4 | 7 | 7 |  |

### `crossings_count`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.5 | 2865 | ██████████████████████████████ |
| 0.5 | 1 | 0 |  |
| 1 | 1.5 | 1490 | ████████████████ |
| 1.5 | 2 | 0 |  |
| 2 | 2.5 | 371 | ████ |
| 2.5 | 3 | 0 |  |
| 3 | 3.5 | 50 | █ |
| 3.5 | 4 | 0 |  |
| 4 | 4.5 | 10 |  |
| 4.5 | 5 | 1 |  |

### `conn_score`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0 | 0.0991 | 1033 | ██████████████████████████████ |
| 0.0991 | 0.198 | 976 | ████████████████████████████ |
| 0.198 | 0.297 | 875 | █████████████████████████ |
| 0.297 | 0.396 | 380 | ███████████ |
| 0.396 | 0.496 | 212 | ██████ |
| 0.496 | 0.595 | 431 | █████████████ |
| 0.595 | 0.694 | 220 | ██████ |
| 0.694 | 0.793 | 286 | ████████ |
| 0.793 | 0.892 | 226 | ███████ |
| 0.892 | 0.991 | 148 | ████ |

### `place_score`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0.00219 | 0.0951 | 255 | █████████ |
| 0.0951 | 0.188 | 406 | ███████████████ |
| 0.188 | 0.281 | 485 | █████████████████ |
| 0.281 | 0.374 | 724 | ██████████████████████████ |
| 0.374 | 0.467 | 836 | ██████████████████████████████ |
| 0.467 | 0.56 | 656 | ████████████████████████ |
| 0.56 | 0.653 | 518 | ███████████████████ |
| 0.653 | 0.746 | 490 | ██████████████████ |
| 0.746 | 0.839 | 316 | ███████████ |
| 0.839 | 0.932 | 101 | ████ |

### `conn_weight_available`

| von | bis | Anzahl | |
| ---: | ---: | ---: | --- |
| 0.45 | 0.505 | 97 | █ |
| 0.505 | 0.56 | 0 |  |
| 0.56 | 0.615 | 0 |  |
| 0.615 | 0.67 | 0 |  |
| 0.67 | 0.725 | 0 |  |
| 0.725 | 0.78 | 0 |  |
| 0.78 | 0.835 | 3772 | ██████████████████████████████ |
| 0.835 | 0.89 | 0 |  |
| 0.89 | 0.945 | 0 |  |
| 0.945 | 1 | 918 | ███████ |

### Kategoriale Merkmale

| Merkmal | Werte (Anteil der Abschnitte) |
| --- | --- |
| `in_hvs` | False: 81.4 %, True: 18.6 % |
| `in_cycle_network` | False: 91.7 %, True: 8.3 % |
| `separated_cycle_track_present` | False: 58.4 %, True: 24.5 %, null: 17.1 % |
| `cycle_lane_present` | False: 75.2 %, null: 17.1 %, True: 7.6 % |
| `centre_line` | null: 83.7 %, False: 16.2 %, True: 0.1 % |
| `parking_on_carriageway` | null: 57.1 %, False: 31.7 %, True: 11.2 % |
| `parking_along_carriageway` | null: 57.1 %, False: 26.2 %, True: 16.7 % |
| `angle_parking` | null: 57.1 %, False: 40.1 %, True: 2.8 % |
| `surface` | asphalt: 88.6 %, paving_stones: 5.5 %, sett: 5.0 %, null: 0.5 %, unhewn_cobblestone: 0.3 %, compacted: 0.1 % |
| `access_motor_only` | False: 97.5 %, True: 2.5 % |
| `pedestrian_zone` | False: 98.0 %, True: 2.0 % |
| `speed_sources_conflict` | False: 97.3 %, True: 2.7 % |

### conn_score nach highway-Klasse (Median)

| highway | Abschnitte | conn_score | place_score |
| --- | ---: | ---: | ---: |
| living_street | 159 | 0.10 | 0.38 |
| motorway | 29 | 0.52 | 0.17 |
| motorway_link | 90 | 0.25 | 0.10 |
| pedestrian | 97 | 0.00 | 0.63 |
| primary | 641 | 0.82 | 0.43 |
| primary_link | 30 | 0.24 | 0.47 |
| residential | 2487 | 0.15 | 0.45 |
| secondary | 424 | 0.67 | 0.37 |
| secondary_link | 24 | 0.40 | 0.19 |
| tertiary | 672 | 0.43 | 0.48 |
| tertiary_link | 17 | 0.36 | 0.40 |
| trunk | 3 | 0.97 | 0.05 |
| unclassified | 114 | 0.10 | 0.27 |

## Stichprobe (30 zufällige Abschnitte im Bezirk Eimsbüttel, Seed 42)

Links auf OSM-Karte und OSM-Way. Orthophoto- und Panoramax-Links folgen, sobald das Linkformat geklärt ist (docs/open_questions.md).

| segment_id | Name | highway | conn | place | betw. | HVS | Tempo | Radweg | Front. | Schule/Kita m | Karte | Way |
| --- | --- | --- | ---: | ---: | ---: | --- | ---: | --- | ---: | ---: | --- | --- |
| `seg_074cd95a035a05c4` | Papendamm | residential | 0.16 | 0.65 | 0.37 | nein | 30 | nein | 0.17 | 78 | [Karte](https://www.openstreetmap.org/?mlat=53.566680&mlon=9.976908#map=18/53.566680/9.976908) | [Way](https://www.openstreetmap.org/way/4004664) |
| `seg_0817c77e740f6f6c` | – | motorway_link | 0.43 | 0.10 | 0.98 | nein | 100 | – | 0.00 | 310 | [Karte](https://www.openstreetmap.org/?mlat=53.593640&mlon=9.922273#map=18/53.593640/9.922273) | [Way](https://www.openstreetmap.org/way/1276595268) |
| `seg_08c8ff2f0960effa` | Holsteiner Chaussee | primary | 0.79 | 0.06 | 0.82 | ja | 50 | nein | – | 400 | [Karte](https://www.openstreetmap.org/?mlat=53.620392&mlon=9.908264#map=18/53.620392/9.908264) | [Way](https://www.openstreetmap.org/way/408642295) |
| `seg_094a4278a1b7df0b` | Redingskamp | residential | 0.49 | 0.33 | 0.70 | nein | 50 | ja | 0.00 | 67 | [Karte](https://www.openstreetmap.org/?mlat=53.612511&mlon=9.890739#map=18/53.612511/9.890739) | [Way](https://www.openstreetmap.org/way/42413679) |
| `seg_1795d520ce96094f` | Hallerstraße | tertiary | 0.58 | 0.51 | 0.84 | nein | 50 | nein | 0.25 | 12 | [Karte](https://www.openstreetmap.org/?mlat=53.572680&mlon=9.991315#map=18/53.572680/9.991315) | [Way](https://www.openstreetmap.org/way/39095469) |
| `seg_191011c181a9eccc` | Nordalbingerweg | residential | 0.10 | 0.28 | 0.23 | nein | 30 | ja | 0.00 | 628 | [Karte](https://www.openstreetmap.org/?mlat=53.647269&mlon=9.953846#map=18/53.647269/9.953846) | [Way](https://www.openstreetmap.org/way/1168136673) |
| `seg_1b9a3cddb28e88fc` | Baarkamp | residential | 0.23 | 0.28 | 0.52 | nein | 30 | nein | 0.00 | 225 | [Karte](https://www.openstreetmap.org/?mlat=53.606061&mlon=9.940001#map=18/53.606061/9.940001) | [Way](https://www.openstreetmap.org/way/496601616) |
| `seg_1e51b72f49183c5f` | Rütersbarg | residential | 0.24 | 0.72 | 0.55 | nein | 30 | nein | 0.60 | 11 | [Karte](https://www.openstreetmap.org/?mlat=53.601577&mlon=9.955145#map=18/53.601577/9.955145) | [Way](https://www.openstreetmap.org/way/26628741) |
| `seg_25fff5cebc7b74d3` | – | primary_link | 0.31 | 0.65 | 0.70 | nein | 50 | ja | 1.00 | 45 | [Karte](https://www.openstreetmap.org/?mlat=53.599118&mlon=9.964975#map=18/53.599118/9.964975) | [Way](https://www.openstreetmap.org/way/30091973) |
| `seg_358f1bb94bb81ef1` | Halstenbeker Straße | residential | 0.10 | 0.49 | 0.23 | nein | 30 | – | 0.00 | 14 | [Karte](https://www.openstreetmap.org/?mlat=53.625667&mlon=9.903495#map=18/53.625667/9.903495) | [Way](https://www.openstreetmap.org/way/23711969) |
| `seg_3ac1a8795499671f` | Oldesloer Straße | secondary | 0.77 | 0.49 | 0.89 | ja | 50 | ja | 0.33 | 20 | [Karte](https://www.openstreetmap.org/?mlat=53.638312&mlon=9.923200#map=18/53.638312/9.923200) | [Way](https://www.openstreetmap.org/way/1150429542) |
| `seg_3bb44606e4a813d2` | Siemersplatz | primary | 0.39 | 0.58 | 0.35 | nein | 50 | ja | – | 36 | [Karte](https://www.openstreetmap.org/?mlat=53.599520&mlon=9.964413#map=18/53.599520/9.964413) | [Way](https://www.openstreetmap.org/way/308317374) |
| `seg_3e4ed57d7c923cd1` | Paul-Sorge-Straße | tertiary | 0.32 | 0.44 | 0.73 | nein | 50 | nein | 0.00 | 320 | [Karte](https://www.openstreetmap.org/?mlat=53.638593&mlon=9.951169#map=18/53.638593/9.951169) | [Way](https://www.openstreetmap.org/way/605866503) |
| `seg_414f382c4d6e32b5` | Kleiner Kielort | residential | 0.09 | 0.74 | 0.21 | nein | 30 | nein | 0.00 | 20 | [Karte](https://www.openstreetmap.org/?mlat=53.571620&mlon=9.975728#map=18/53.571620/9.975728) | [Way](https://www.openstreetmap.org/way/3930845) |
| `seg_49ff6b4f33e0a2d0` | Spanische Furt | residential | 0.43 | 0.37 | 0.48 | nein | 30 | nein | 0.00 | 144 | [Karte](https://www.openstreetmap.org/?mlat=53.623372&mlon=9.911985#map=18/53.623372/9.911985) | [Way](https://www.openstreetmap.org/way/1311146889) |
| `seg_703176e854c5b77e` | Randstraße | tertiary | 0.45 | 0.22 | 0.53 | nein | 50 | ja | – | 165 | [Karte](https://www.openstreetmap.org/?mlat=53.590651&mlon=9.919021#map=18/53.590651/9.919021) | [Way](https://www.openstreetmap.org/way/38613476) |
| `seg_88daa65dfa11532b` | Alsterchaussee | residential | 0.19 | 0.49 | 0.43 | nein | 30 | nein | 0.00 | 94 | [Karte](https://www.openstreetmap.org/?mlat=53.573195&mlon=9.998363#map=18/53.573195/9.998363) | [Way](https://www.openstreetmap.org/way/3927749) |
| `seg_9484862e440e4b51` | Doormannsweg | primary | 0.87 | 0.36 | 0.90 | ja | 50 | nein | 0.00 | 146 | [Karte](https://www.openstreetmap.org/?mlat=53.570567&mlon=9.956429#map=18/53.570567/9.956429) | [Way](https://www.openstreetmap.org/way/80992110) |
| `seg_99a68ad44edd39cc` | Goldnesselweg | residential | 0.10 | 0.46 | 0.23 | nein | 30 | nein | 0.00 | 86 | [Karte](https://www.openstreetmap.org/?mlat=53.610652&mlon=9.885212#map=18/53.610652/9.885212) | [Way](https://www.openstreetmap.org/way/7565287) |
| `seg_a0de84542f4d9127` | Lokstedter Steindamm | primary | 0.88 | 0.26 | 0.92 | ja | 50 | ja | 0.00 | 162 | [Karte](https://www.openstreetmap.org/?mlat=53.591450&mlon=9.967251#map=18/53.591450/9.967251) | [Way](https://www.openstreetmap.org/way/1567673937) |
| `seg_a3e092073b821941` | Bei der Lutherbuche | residential | 0.18 | 0.41 | 0.40 | nein | 30 | nein | 0.00 | 66 | [Karte](https://www.openstreetmap.org/?mlat=53.597134&mlon=9.959851#map=18/53.597134/9.959851) | [Way](https://www.openstreetmap.org/way/16322436) |
| `seg_ae2e7d12bd43b1cc` | Eidelstedter Weg | tertiary | 0.55 | 0.70 | 0.85 | nein | 50 | ja | 0.33 | 24 | [Karte](https://www.openstreetmap.org/?mlat=53.582355&mlon=9.948107#map=18/53.582355/9.948107) | [Way](https://www.openstreetmap.org/way/55955783) |
| `seg_b0b2030ddcdc431f` | Hagendeel | residential | 0.10 | 0.15 | 0.23 | nein | 30 | – | 0.00 | 215 | [Karte](https://www.openstreetmap.org/?mlat=53.607190&mlon=9.942861#map=18/53.607190/9.942861) | [Way](https://www.openstreetmap.org/way/411157231) |
| `seg_b88b298d46679b5e` | Vereinsstraße | residential | 0.16 | 0.75 | 0.38 | nein | 30 | nein | 0.07 | 60 | [Karte](https://www.openstreetmap.org/?mlat=53.565824&mlon=9.962228#map=18/53.565824/9.962228) | [Way](https://www.openstreetmap.org/way/736612811) |
| `seg_bfbed037447cf248` | Oldesloer Straße | secondary | 0.76 | 0.63 | 0.85 | ja | 50 | nein | 0.31 | 52 | [Karte](https://www.openstreetmap.org/?mlat=53.635950&mlon=9.917132#map=18/53.635950/9.917132) | [Way](https://www.openstreetmap.org/way/844555843) |
| `seg_c341ebfaec60354c` | Lokstedter Steindamm | primary | 0.73 | 0.37 | 0.49 | ja | 50 | ja | 0.00 | 186 | [Karte](https://www.openstreetmap.org/?mlat=53.586365&mlon=9.968433#map=18/53.586365/9.968433) | [Way](https://www.openstreetmap.org/way/682409935) |
| `seg_c8d453129f45f45c` | Wullwisch | residential | 0.21 | 0.33 | 0.48 | nein | 30 | – | 0.00 | 183 | [Karte](https://www.openstreetmap.org/?mlat=53.606371&mlon=9.950303#map=18/53.606371/9.950303) | [Way](https://www.openstreetmap.org/way/23417329) |
| `seg_c9a61940cb1ab15c` | Stellinger Weg | residential | 0.23 | 0.80 | 0.54 | nein | 30 | nein | 0.50 | 29 | [Karte](https://www.openstreetmap.org/?mlat=53.580453&mlon=9.947393#map=18/53.580453/9.947393) | [Way](https://www.openstreetmap.org/way/1188162855) |
| `seg_c9e7fa8f21ab0779` | Wördemanns Weg | tertiary | 0.62 | 0.61 | 0.91 | nein | 50 | nein | 0.20 | 61 | [Karte](https://www.openstreetmap.org/?mlat=53.597422&mlon=9.932331#map=18/53.597422/9.932331) | [Way](https://www.openstreetmap.org/way/1417927680) |
| `seg_f14ff48e916757c4` | Goslarer Weg | residential | 0.20 | 0.44 | 0.45 | nein | 30 | nein | 0.00 | 146 | [Karte](https://www.openstreetmap.org/?mlat=53.636626&mlon=9.945053#map=18/53.636626/9.945053) | [Way](https://www.openstreetmap.org/way/10060140) |

## Lizenz

Abschnitte, Gebäude, POIs, Schulen, Kitas und Radnetz aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0; abgeleitete Merkmale stehen ebenfalls unter ODbL. Busfahrten: Hamburger Verkehrsverbund GmbH, dl-de/by-2.0. Einwohner: © Statistische Ämter des Bundes und der Länder, Zensus 2022, dl-de/by-2.0. Amtliche Attribute: Freie und Hansestadt Hamburg (Höchstgeschwindigkeiten und Verkehrsmengen: Lizenz in der API nicht angegeben, siehe docs/open_questions.md).
