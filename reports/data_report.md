# Datenbericht – Abruf Arbeitsgebiet

Erzeugt: 2026-11-05T18:18:20+00:00 von `pipeline/s01_fetch.py`. Nicht amtlicher Entwurf.

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
| bike_volumes_dbradplus | ok | 150778 | ODbL-1.0 | 2026-11-05 | jahr2025: 3 Datensatz/Datensätze vom Server nicht lieferbar (HTTP 500), übersprungen bei offset 1581, 36024, 40622 |
| cycle_network | fallback | 24 | ODbL-1.0 | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| cycle_network_official | ok | 1116 | dl-de/by-2.0 | 2026-11-05 | aus früherem Abruf (nicht neu geladen) |
| bike_counters | ok | 312 | dl-de/by-2.0 | 2026-11-05 | aus früherem Abruf (nicht neu geladen) |
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
| traffic_signals | fallback | 5558 | ODbL-1.0 | 2026-11-05 | aus früherem Abruf (nicht neu geladen) |
| universities | fallback | 111 | ODbL-1.0 | 2026-11-05 | aus früherem Abruf (nicht neu geladen) |
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
| bike_volumes_dbradplus | jahr2025 | 150778 | EPSG:25832 | [548508.0, 5917198.4, 587557.4, 5955179.3] | `data/raw/bike_volumes_dbradplus__jahr2025.parquet` |
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

- **bike_volumes_dbradplus**: aktuelles_jahr, jahr2022, jahr2023, jahr2024, jahr2025 ✔, letzte_woche

## Quellenvermerke

- dedications: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (BVM) (dl-de/by-2.0)
- speed_limits: Quellenvermerk unbekannt – klären (unknown)
- traffic_volumes: Quellenvermerk unbekannt – klären (unknown)
- traffic_counters: Quellenvermerk unbekannt – klären (unknown)
- bike_volumes_dbradplus: Quellenvermerk unbekannt – klären (ODbL-1.0)
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
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.567454&mlon=9.895407#map=18/53.567454/9.895407) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.472933&mlon=9.961027#map=18/53.472933/9.961027) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.442045&mlon=9.939391#map=18/53.442045/9.939391) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.442130&mlon=9.970969#map=18/53.442130/9.970969) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.521031&mlon=10.031010#map=18/53.521031/10.031010) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.678397&mlon=10.039135#map=18/53.678397/10.039135) |
| alkis | Nutzung | nan | [OSM](https://www.openstreetmap.org/?mlat=53.481029&mlon=10.052757#map=18/53.481029/10.052757) |
| bike_volumes_dbradplus | jahr2025 |  | [OSM](https://www.openstreetmap.org/?mlat=53.584433&mlon=9.878983#map=18/53.584433/9.878983) |
| bike_volumes_dbradplus | jahr2025 |  | [OSM](https://www.openstreetmap.org/?mlat=53.639898&mlon=10.214724#map=18/53.639898/10.214724) |
| bike_volumes_dbradplus | jahr2025 |  | [OSM](https://www.openstreetmap.org/?mlat=53.586654&mlon=10.088586#map=18/53.586654/10.088586) |
| bike_volumes_dbradplus | jahr2025 |  | [OSM](https://www.openstreetmap.org/?mlat=53.647419&mlon=10.136551#map=18/53.647419/10.136551) |
| road_condition_zeb | zeb2025_geb | Reinbeker Redder | [OSM](https://www.openstreetmap.org/?mlat=53.511836&mlon=10.195055#map=18/53.511836/10.195055) |
| road_condition_zeb | zeb2025_gw | Gurlittstraße | [OSM](https://www.openstreetmap.org/?mlat=53.557954&mlon=10.009939#map=18/53.557954/10.009939) |
| road_condition_zeb | zeb2025_gw | Fritz-Solmitz-Weg | [OSM](https://www.openstreetmap.org/?mlat=53.664816&mlon=10.029816#map=18/53.664816/10.029816) |
| road_condition_zeb | zeb2025_gw | Alsterweg | [OSM](https://www.openstreetmap.org/?mlat=53.640832&mlon=10.053772#map=18/53.640832/10.053772) |
| road_condition_zeb | zeb2025_gw | Kirchwerder Elbdeich | [OSM](https://www.openstreetmap.org/?mlat=53.400144&mlon=10.175199#map=18/53.400144/10.175199) |
| road_condition_zeb | zeb2025_gw | Eckenerstraße | [OSM](https://www.openstreetmap.org/?mlat=53.587207&mlon=10.119707#map=18/53.587207/10.119707) |
| road_condition_zeb | zeb2025_gw | Klosterwisch | [OSM](https://www.openstreetmap.org/?mlat=53.646247&mlon=10.151893#map=18/53.646247/10.151893) |
| road_condition_zeb | zeb2025_sub | Sandmoorweg | [OSM](https://www.openstreetmap.org/?mlat=53.592561&mlon=9.746520#map=18/53.592561/9.746520) |
| road_condition_zeb | zeb2025_sub | Pletschgang | [OSM](https://www.openstreetmap.org/?mlat=53.582528&mlon=9.819898#map=18/53.582528/9.819898) |
| road_condition_zeb | zeb2025_sub | Bei der Lutherbuche | [OSM](https://www.openstreetmap.org/?mlat=53.597512&mlon=9.962920#map=18/53.597512/9.962920) |
| road_condition_zeb | zeb2025_sub | Eekboomkoppel | [OSM](https://www.openstreetmap.org/?mlat=53.651256&mlon=10.000025#map=18/53.651256/10.000025) |
| road_condition_zeb | zeb2025_sub | Billwiese | [OSM](https://www.openstreetmap.org/?mlat=53.491614&mlon=10.188829#map=18/53.491614/10.188829) |
| road_condition_zeb | zeb2025_sub | Prinzenweg | [OSM](https://www.openstreetmap.org/?mlat=53.555281&mlon=10.113448#map=18/53.555281/10.113448) |
| road_condition_zeb | zeb2025_sub | Blakshörn | [OSM](https://www.openstreetmap.org/?mlat=53.628968&mlon=10.122806#map=18/53.628968/10.122806) |
| road_condition_zeb | zeb2025_sub | Eckloßberg | [OSM](https://www.openstreetmap.org/?mlat=53.637882&mlon=10.096247#map=18/53.637882/10.096247) |
| speed_limits | tempo30zonen | Am Großen Dahlen | [OSM](https://www.openstreetmap.org/?mlat=53.445547&mlon=9.960285#map=18/53.445547/9.960285) |
| speed_limits | tempo30zonen | Innocentiastraße | [OSM](https://www.openstreetmap.org/?mlat=53.579121&mlon=9.981825#map=18/53.579121/9.981825) |
| speed_limits | tempo30zonen | Meriandamm | [OSM](https://www.openstreetmap.org/?mlat=53.549722&mlon=10.115492#map=18/53.549722/10.115492) |
| speed_limits | tempo30zonen | Chrysanderstraße | [OSM](https://www.openstreetmap.org/?mlat=53.496070&mlon=10.214557#map=18/53.496070/10.214557) |
