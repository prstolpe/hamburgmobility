# Datenbericht – Abruf Arbeitsgebiet

Erzeugt: 2026-11-05T17:54:53+00:00 von `pipeline/s01_fetch.py`. Nicht amtlicher Entwurf.

## Arbeitsgebiet

Bezirke von Hamburg (admin_level 9, Grenzen aus OSM, weil die ALKIS-URL in config/sources.yaml fehlt):

| Bezirk | OSM-Relation | Fläche km² |
| --- | ---: | ---: |
| Altona | 30223 | 77.8 |
| Bergedorf | 28936 | 154.6 |
| Eimsbüttel | 30243 | 49.8 |
| Hamburg-Mitte | 28971 | 134.6 |
| Hamburg-Nord | 30352 | 57.7 |
| Harburg | 28964 | 125.0 |
| Wandsbek | 30353 | 147.4 |
| **gesamt** | | **746.9** |

- Ausgeschlossen: Neuwerk (admin_level 10) samt dem abgetrennten Polygonteil, in dem es liegt (Neuwerk: Insel, Scharhörn, Wattenmeer; Entscheidung 2026-11-04)
- Puffer: 500 m, Arbeitsgebiet 842.6 km²
- Abgerufen wird das ganze Arbeitsgebiet. Nicht klassifiziert werden 17 ländliche Stadtteile (172.8 km²; config/project.yaml, rural_exclude): Allermöhe, Altengamme, Billwerder, Cranz, Curslack, Francop, Gut Moor, Kirchwerder, Moorburg, Moorfleet, Neuenfelde, Neuengamme, Neuland, Ochsenwerder, Reitbrook, Spadenland, Tatenberg
- Bounding Box (EPSG:25832): [547864.4, 5916431.7, 588510.4, 5955661.7]
- Abruf von WFS und OGC API in 20 Kacheln zu 10 km; doppelt gelieferte Objekte an Kachelgrenzen werden entfernt.
- Objekte, die das Arbeitsgebiet schneiden, werden vollständig übernommen (kein Zuschnitt).

## Übersicht je Quelle

| Quelle | Status | Objekte | Lizenz | Abruf | Hinweis |
| --- | --- | --- | --- | --- | --- |
| hvs_network_map | manuell | – | unknown | – | aus früherem Abruf (nicht neu geladen) |
| strategic_road_network | fehler | – | dl-de/by-2.0 | – | https://geodienste.hamburg.de/HH_WFS_Strategisches_Strassennetz: HTTP 404 |
| dedications | ok | 47391 | dl-de/by-2.0 | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| speed_limits | ok | 57511 | unknown | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| traffic_volumes | ok | 4303 | unknown | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| traffic_counters | ok | 11673 | unknown | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| bike_volumes_dbradplus | fehler | – | ODbL-1.0 | – | https://api.hamburg.de/datasets/v1/dbradplus/collections/jahr2025/items?f=json&crs=http%3A%2F%2Fwww.opengis.net%2Fdef%2Fcrs%2FEPSG%2F0%2F25832&limit=1000&offset=1000: invalid JSON after 150646 bytes (Expecting ',' delimiter: line 1 column 150647 (char 150646)) |
| cycle_network | fallback | 24 | ODbL-1.0 | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| cycle_network_official | ok | 1116 | dl-de/by-2.0 | 2026-11-05 |  |
| bike_counters | ok | 312 | dl-de/by-2.0 | 2026-11-05 | Zählstellen mit Tageswerten 2025 (layerName Anzahl_Fahrraeder_Zaehlstelle_1-Tag) |
| alkis | ok | 527311 | dl-de/by-2.0 | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| buildings_3d | fehlt | – | dl-de/by-2.0 | – | TODO: Transparenzportal |
| orthophotos | fehlt | – | dl-de/by-2.0 | – | TODO: Transparenzportal / WMS |
| laserscan | fehlt | – | unknown | – | TODO |
| street_trees | fehlt | – | unknown | – | TODO: Transparenzportal |
| road_condition_zeb | ok | 808932 | dl-de/by-2.0 | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| road_surface | ok | 37835 | dl-de/by-2.0 | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| quiet_areas | ok | 15 | unknown | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| noise_maps | fehlt | – | unbekannt | – | TODO |
| schools | fallback | 558 | ODbL-1.0 | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| kitas | fallback | 987 | ODbL-1.0 | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| traffic_signals | fallback | 5558 | ODbL-1.0 | 2026-11-05 | Fallback OSM: {"tags": {"highway": ["traffic_signals"]}, "columns": ["highway", "crossing", "traffic_signals"]} |
| universities | fallback | 111 | ODbL-1.0 | 2026-11-05 | Fallback OSM: {"tags": {"amenity": ["university", "college"]}, "columns": ["amenity"]} |
| centres | fehlt | – | unbekannt | – | TODO: Hamburger Zentrenkonzept – Datensatz/Dienst ermitteln; nicht durch eine Ersatzquelle ersetzen |
| population_grid | ok | 31152 | dl-de/by-2.0 | 2026-10-28 | aus früherem Abruf (nicht neu geladen) |
| gtfs_hvv | ok | 0 | dl-de/by-2.0 | 2026-10-28 | aus früherem Abruf (nicht neu geladen) |
| accidents | ok | 0 | dl-de/by-2.0 | 2026-10-28 | aus früherem Abruf (nicht neu geladen) |
| osm | ok | 24 | ODbL-1.0 | 2026-10-28 | lokale Datei wiederverwendet (Stand Wed, 28 Oct 2026 03:56:24 GMT) |

## Ebenen

| Quelle | Ebene | Objekte | CRS | Bounding Box | Datei |
| --- | --- | --- | --- | --- | --- |
| dedications | de.hh.up:widmung_flaeche | 3844 | EPSG:25832 | [548818.0, 5917261.3, 585676.8, 5953530.7] | `data/raw/dedications__widmung_flaeche.parquet` |
| dedications | de.hh.up:widmung_linie | 43547 | EPSG:25832 | [548676.3, 5917191.3, 588004.0, 5953544.0] | `data/raw/dedications__widmung_linie.parquet` |
| speed_limits | tempo20zonen | 192 | EPSG:25832 | [549993.5, 5923858.3, 580666.5, 5945532.0] | `data/raw/speed_limits__tempo20zonen.parquet` |
| speed_limits | tempo30zonen | 19472 | EPSG:25832 | [548986.1, 5917239.8, 585760.5, 5952432.3] | `data/raw/speed_limits__tempo30zonen.parquet` |
| speed_limits | verkehrsberuhigte_bereiche | 1477 | EPSG:25832 | [549289.7, 5919032.8, 586448.3, 5952406.4] | `data/raw/speed_limits__verkehrsberuhigte_bereiche.parquet` |
| speed_limits | zulaessige_hoechstgeschwindigkeiten | 35538 | EPSG:25832 | [548683.1, 5917191.3, 588004.0, 5953544.0] | `data/raw/speed_limits__zulaessige_hoechstgeschwindigkeiten.parquet` |
| speed_limits | zulaessige_hoechstgeschwindigkeiten_sonderregelung | 832 | EPSG:25832 | [550159.7, 5917459.7, 581284.7, 5951293.6] | `data/raw/speed_limits__zulaessige_hoechstgeschwindigkeiten_sonderregelung.parquet` |
| traffic_volumes | verkehrsmengen_dtv_hvs_2019 | 3728 | EPSG:25832 | [548832.4, 5918844.7, 584029.9, 5952916.3] | `data/raw/traffic_volumes__verkehrsmengen_dtv_hvs_2019.parquet` |
| traffic_volumes | verkehrsmengen_dtv_bab_2019 | 575 | EPSG:25832 | [557583.4, 5918776.3, 584409.3, 5945291.2] | `data/raw/traffic_volumes__verkehrsmengen_dtv_bab_2019.parquet` |
| traffic_counters | locations_things | 11673 | EPSG:25832 | [548710.0, 5917280.5, 584015.0, 5952303.0] | `data/raw/traffic_counters__locations_things.parquet` |
| cycle_network | osm | 24 | EPSG:25832 | [557955.9, 5923659.4, 580081.2, 5943928.0] | `data/raw/cycle_network__osm.parquet` |
| cycle_network_official | de.hh.up:radnetz | 1026 | EPSG:25832 | [548952.1, 5917330.8, 586460.4, 5951545.8] | `data/raw/cycle_network_official__radnetz.parquet` |
| cycle_network_official | de.hh.up:radrouten | 90 | EPSG:25832 | [548952.1, 5917267.2, 584414.8, 5951545.8] | `data/raw/cycle_network_official__radrouten.parquet` |
| bike_counters | stations | 312 | EPSG:25832 | [553766.0, 5923498.8, 580122.5, 5945884.4] | `data/raw/bike_counters__stations.parquet` |
| bike_counters | daily_2025 | – | – | – | `data/raw/bike_counters__daily_2025.parquet` |
| alkis | ave:Nutzung | 102339 | EPSG:25832 | [548365.3, 5916918.1, 588010.4, 5955161.7] | `data/raw/alkis__Nutzung.parquet` |
| alkis | ave:GebaeudeBauwerk | 424972 | EPSG:25832 | [548681.9, 5917227.9, 587611.8, 5953580.7] | `data/raw/alkis__GebaeudeBauwerk.parquet` |
| road_condition_zeb | de.hh.up:zeb2025_geb | 134822 | EPSG:25832 | [548946.7, 5917198.8, 587470.7, 5952682.1] | `data/raw/road_condition_zeb__zeb2025_geb.parquet` |
| road_condition_zeb | de.hh.up:zeb2025_gw | 404466 | EPSG:25832 | [548946.7, 5917198.8, 587470.7, 5952682.1] | `data/raw/road_condition_zeb__zeb2025_gw.parquet` |
| road_condition_zeb | de.hh.up:zeb2025_sub | 269644 | EPSG:25832 | [548946.7, 5917198.8, 587470.7, 5952682.1] | `data/raw/road_condition_zeb__zeb2025_sub.parquet` |
| road_surface | de.hh.up:strassendeckschicht | 37835 | EPSG:25832 | [548683.1, 5917191.3, 587561.5, 5953544.0] | `data/raw/road_surface__strassendeckschicht.parquet` |
| quiet_areas | de.hh.up:ruhige_gebiete_hamburg | 15 | EPSG:25832 | [550110.0, 5918718.2, 580556.3, 5955120.2] | `data/raw/quiet_areas__ruhige_gebiete_hamburg.parquet` |
| schools | osm | 558 | EPSG:25832 | [549701.6, 5917466.0, 584459.3, 5951180.9] | `data/raw/schools__osm.parquet` |
| kitas | osm | 987 | EPSG:25832 | [548705.5, 5917380.7, 584544.2, 5951373.9] | `data/raw/kitas__osm.parquet` |
| traffic_signals | osm | 5558 | EPSG:25832 | [548339.0, 5918549.3, 582373.0, 5952236.2] | `data/raw/traffic_signals__osm.parquet` |
| universities | osm | 111 | EPSG:25832 | [555223.2, 5923512.6, 582488.5, 5942531.8] | `data/raw/universities__osm.parquet` |
| population_grid | zip | – | – | – | `data/raw/population_grid/Zensus2022_Bevoelkerungszahl.zip` |
| population_grid | 100m | 31152 | EPSG:25832 | [548111.8, 5916358.5, 587228.7, 5955482.0] | `data/raw/population_grid__100m.parquet` |
| gtfs_hvv | zip | – | – | – | `data/raw/gtfs_hvv/Upload__hvv_Rohdaten_GTFS_Fpl_20260408.ZIP` |
| accidents | zip_2021 | – | – | – | `data/raw/accidents/Unfallorte2021_EPSG25832_CSV.zip` |
| accidents | zip_2022 | – | – | – | `data/raw/accidents/Unfallorte2022_EPSG25832_CSV.zip` |
| accidents | zip_2023 | – | – | – | `data/raw/accidents/Unfallorte2023_EPSG25832_CSV.zip` |
| accidents | zip_2024 | – | – | – | `data/raw/accidents/Unfallorte2024_EPSG25832_CSV.zip` |
| accidents | zip_2025 | – | – | – | `data/raw/accidents/Unfallorte2025_EPSG25832_CSV.zip` |
| osm | pbf | – | – | – | `data/raw/osm/hamburg_2026-10-28.osm.pbf` |
| osm | work_area | 7 | EPSG:25832 | [548364.3, 5916931.6, 588010.6, 5955161.7] | `data/raw/work_area.parquet` |
| osm | rural_excluded | 17 | EPSG:25832 | [550639.8, 5916931.6, 588010.6, 5933013.2] | `data/raw/rural_excluded.parquet` |

## Angebotene Feature-Typen und Collections

- **cycle_network_official**: de.hh.up:radnetz ✔, de.hh.up:radrouten ✔

## Quellenvermerke

- dedications: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (BVM) (dl-de/by-2.0)
- speed_limits: Quellenvermerk unbekannt – klären (unknown)
- traffic_volumes: Quellenvermerk unbekannt – klären (unknown)
- traffic_counters: Quellenvermerk unbekannt – klären (unknown)
- cycle_network: © OpenStreetMap-Beitragende (ODbL-1.0)
- cycle_network_official: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (dl-de/by-2.0)
- bike_counters: Freie und Hansestadt Hamburg (dl-de/by-2.0)
- alkis: Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV) (dl-de/by-2.0)
- road_condition_zeb: Quellenvermerk unbekannt – klären (dl-de/by-2.0)
- road_surface: Quellenvermerk unbekannt – klären (dl-de/by-2.0)
- quiet_areas: Quellenvermerk unbekannt – klären (unknown)
- schools: © OpenStreetMap-Beitragende (ODbL-1.0)
- kitas: © OpenStreetMap-Beitragende (ODbL-1.0)
- traffic_signals: © OpenStreetMap-Beitragende (ODbL-1.0)
- universities: © OpenStreetMap-Beitragende (ODbL-1.0)
- population_grid: © Statistische Ämter des Bundes und der Länder, Zensus 2022 (dl-de/by-2.0)
- gtfs_hvv: Hamburger Verkehrsverbund GmbH (dl-de/by-2.0)
- accidents: © Statistische Ämter des Bundes und der Länder, Unfallatlas (dl-de/by-2.0)
- osm: © OpenStreetMap-Beitragende (ODbL-1.0)

## Stichprobe (30 zufällige Objekte, Seed 42)

Links auf OpenStreetMap. Orthophoto- und Panoramax-Links folgen, sobald das Linkformat geklärt ist (docs/open_questions.md).

| Quelle | Ebene | Bezeichnung | Karte |
| --- | --- | --- | --- |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.514068&mlon=9.814090#map=18/53.514068/9.814090) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.575376&mlon=9.859155#map=18/53.575376/9.859155) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.612878&mlon=10.050351#map=18/53.612878/10.050351) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.656580&mlon=9.993360#map=18/53.656580/9.993360) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.654539&mlon=10.007488#map=18/53.654539/10.007488) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.627539&mlon=9.932478#map=18/53.627539/9.932478) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.487585&mlon=10.189048#map=18/53.487585/10.189048) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.581951&mlon=10.124967#map=18/53.581951/10.124967) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.637270&mlon=10.169937#map=18/53.637270/10.169937) |
| alkis | Nutzung | nan | [OSM](https://www.openstreetmap.org/?mlat=53.671482&mlon=10.051878#map=18/53.671482/10.051878) |
| alkis | Nutzung | nan | [OSM](https://www.openstreetmap.org/?mlat=53.599075&mlon=10.179530#map=18/53.599075/10.179530) |
| alkis | Nutzung | nan | [OSM](https://www.openstreetmap.org/?mlat=53.609838&mlon=10.124197#map=18/53.609838/10.124197) |
| road_condition_zeb | zeb2025_gw | Homannstraße | [OSM](https://www.openstreetmap.org/?mlat=53.464373&mlon=9.958233#map=18/53.464373/9.958233) |
| road_condition_zeb | zeb2025_gw | Talwinkel | [OSM](https://www.openstreetmap.org/?mlat=53.451730&mlon=9.933773#map=18/53.451730/9.933773) |
| road_condition_zeb | zeb2025_gw | Norburger Straße | [OSM](https://www.openstreetmap.org/?mlat=53.567350&mlon=9.910632#map=18/53.567350/9.910632) |
| road_condition_zeb | zeb2025_gw | Rungholt | [OSM](https://www.openstreetmap.org/?mlat=53.598659&mlon=10.159133#map=18/53.598659/10.159133) |
| road_condition_zeb | zeb2025_gw | Schloßkoppel | [OSM](https://www.openstreetmap.org/?mlat=53.626864&mlon=10.126644#map=18/53.626864/10.126644) |
| road_condition_zeb | zeb2025_gw | Steinwegel | [OSM](https://www.openstreetmap.org/?mlat=53.654230&mlon=10.124955#map=18/53.654230/10.124955) |
| road_condition_zeb | zeb2025_gw | Specksaalredder | [OSM](https://www.openstreetmap.org/?mlat=53.706027&mlon=10.116181#map=18/53.706027/10.116181) |
| road_condition_zeb | zeb2025_sub | Grillenweg | [OSM](https://www.openstreetmap.org/?mlat=53.619776&mlon=9.886195#map=18/53.619776/9.886195) |
| road_condition_zeb | zeb2025_sub | Sand | [OSM](https://www.openstreetmap.org/?mlat=53.461196&mlon=9.981021#map=18/53.461196/9.981021) |
| road_condition_zeb | zeb2025_sub | Kriegerdankweg | [OSM](https://www.openstreetmap.org/?mlat=53.631490&mlon=9.916140#map=18/53.631490/9.916140) |
| road_condition_zeb | zeb2025_sub | Elly-Heuss-Knapp-Ring | [OSM](https://www.openstreetmap.org/?mlat=53.479056&mlon=10.167414#map=18/53.479056/10.167414) |
| road_condition_zeb | zeb2025_sub | Sthamerstraße | [OSM](https://www.openstreetmap.org/?mlat=53.692256&mlon=10.141567#map=18/53.692256/10.141567) |
| road_surface | strassendeckschicht | Alsterdorfer Straße | [OSM](https://www.openstreetmap.org/?mlat=53.597810&mlon=9.996944#map=18/53.597810/9.996944) |
| speed_limits | tempo30zonen | Am Großen Dahlen | [OSM](https://www.openstreetmap.org/?mlat=53.445547&mlon=9.960285#map=18/53.445547/9.960285) |
| speed_limits | tempo30zonen | Innocentiastraße | [OSM](https://www.openstreetmap.org/?mlat=53.579121&mlon=9.981825#map=18/53.579121/9.981825) |
| speed_limits | tempo30zonen | Meriandamm | [OSM](https://www.openstreetmap.org/?mlat=53.549722&mlon=10.115492#map=18/53.549722/10.115492) |
| speed_limits | tempo30zonen | Chrysanderstraße | [OSM](https://www.openstreetmap.org/?mlat=53.496070&mlon=10.214557#map=18/53.496070/10.214557) |
| traffic_signals | osm | nan | [OSM](https://www.openstreetmap.org/?mlat=53.553480&mlon=9.938896#map=18/53.553480/9.938896) |
