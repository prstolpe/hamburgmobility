# Datenbericht – Abruf Arbeitsgebiet

Erzeugt: 2026-11-16T22:24:58+00:00 von `pipeline/s01_fetch.py`. Nicht amtlicher Entwurf.

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
| bike_volumes_dbradplus | ok | 150778 | ODbL-1.0 | 2026-11-05 | aus früherem Abruf (nicht neu geladen) |
| cycle_network | fallback | 24 | ODbL-1.0 | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| cycle_network_official | ok | 1116 | dl-de/by-2.0 | 2026-11-05 | aus früherem Abruf (nicht neu geladen) |
| bike_counters | ok | 312 | dl-de/by-2.0 | 2026-11-05 | aus früherem Abruf (nicht neu geladen) |
| alkis | ok | 527311 | dl-de/by-2.0 | 2026-11-04 | aus früherem Abruf (nicht neu geladen) |
| buildings_3d | fehlt | – | dl-de/by-2.0 | – | TODO: Transparenzportal |
| orthophotos | fehlt | – | dl-de/by-2.0 | – | TODO: Transparenzportal / WMS |
| laserscan | fehlt | – | unknown | – | TODO |
| street_trees | ok | 229876 | dl-de/by-2.0 | 2026-11-16 |  |
| parking_spaces | ok | 203029 | dl-de/by-2.0 | 2026-11-16 |  |
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
| street_trees | de.hh.up:strassenbaumkataster | 229876 | EPSG:25832 | [548628.9, 5917302.3, 587559.0, 5953531.7] | `data/raw/street_trees__strassenbaumkataster.parquet` |
| parking_spaces | de.hh.up:parkraum | 203029 | EPSG:25832 | [553431.1, 5921467.9, 581123.1, 5948633.6] | `data/raw/parking_spaces__parkraum.parquet` |
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

- **street_trees**: de.hh.up:strassenbaumkataster ✔
- **parking_spaces**: de.hh.up:parkraum ✔

## Quellenvermerke

- dedications: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (BVM) (dl-de/by-2.0)
- speed_limits: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (BVM) (unknown)
- traffic_volumes: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (BVM) (unknown)
- traffic_counters: Quellenvermerk unbekannt – klären (unknown)
- bike_volumes_dbradplus: Quellenvermerk unbekannt – klären (ODbL-1.0)
- cycle_network: © OpenStreetMap-Beitragende (ODbL-1.0)
- cycle_network_official: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (dl-de/by-2.0)
- bike_counters: Freie und Hansestadt Hamburg (dl-de/by-2.0)
- alkis: Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV) (dl-de/by-2.0)
- street_trees: Freie und Hansestadt Hamburg, Behörde für Umwelt, Klima, Energie und Agrarwirtschaft (dl-de/by-2.0)
- parking_spaces: Freie und Hansestadt Hamburg, Landesbetrieb Verkehr (dl-de/by-2.0)
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
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.476377&mlon=9.890229#map=18/53.476377/9.890229) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.470856&mlon=9.841663#map=18/53.470856/9.841663) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.570677&mlon=9.812616#map=18/53.570677/9.812616) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.555955&mlon=9.857206#map=18/53.555955/9.857206) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.508216&mlon=10.013636#map=18/53.508216/10.013636) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.620854&mlon=9.912266#map=18/53.620854/9.912266) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.589089&mlon=10.096389#map=18/53.589089/10.096389) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.548488&mlon=10.062386#map=18/53.548488/10.062386) |
| alkis | Nutzung | nan | [OSM](https://www.openstreetmap.org/?mlat=53.660385&mlon=10.087041#map=18/53.660385/10.087041) |
| bike_volumes_dbradplus | jahr2025 |  | [OSM](https://www.openstreetmap.org/?mlat=53.565548&mlon=9.830908#map=18/53.565548/9.830908) |
| bike_volumes_dbradplus | jahr2025 |  | [OSM](https://www.openstreetmap.org/?mlat=53.612719&mlon=9.973556#map=18/53.612719/9.973556) |
| dedications | widmung_linie | Teutonenweg | [OSM](https://www.openstreetmap.org/?mlat=53.635264&mlon=9.971432#map=18/53.635264/9.971432) |
| parking_spaces | parkraum | Eilbeker Weg | [OSM](https://www.openstreetmap.org/?mlat=53.570654&mlon=10.047942#map=18/53.570654/10.047942) |
| parking_spaces | parkraum | Sierichstraße | [OSM](https://www.openstreetmap.org/?mlat=53.585854&mlon=10.003843#map=18/53.585854/10.003843) |
| parking_spaces | parkraum | Birkenau | [OSM](https://www.openstreetmap.org/?mlat=53.568344&mlon=10.028773#map=18/53.568344/10.028773) |
| road_condition_zeb | zeb2025_gw | Liebermannstraße | [OSM](https://www.openstreetmap.org/?mlat=53.547596&mlon=9.899352#map=18/53.547596/9.899352) |
| road_condition_zeb | zeb2025_gw | Im Keil | [OSM](https://www.openstreetmap.org/?mlat=53.602511&mlon=9.896887#map=18/53.602511/9.896887) |
| road_condition_zeb | zeb2025_gw | Kakenhaner Weg | [OSM](https://www.openstreetmap.org/?mlat=53.704860&mlon=10.099697#map=18/53.704860/10.099697) |
| road_condition_zeb | zeb2025_gw | Brookdeich | [OSM](https://www.openstreetmap.org/?mlat=53.477375&mlon=10.240171#map=18/53.477375/10.240171) |
| road_condition_zeb | zeb2025_gw | Ahrensfelder Weg | [OSM](https://www.openstreetmap.org/?mlat=53.634913&mlon=10.211433#map=18/53.634913/10.211433) |
| road_condition_zeb | zeb2025_sub | Grünebergstraße | [OSM](https://www.openstreetmap.org/?mlat=53.557021&mlon=9.914288#map=18/53.557021/9.914288) |
| street_trees | strassenbaumkataster |  | [OSM](https://www.openstreetmap.org/?mlat=53.488316&mlon=9.905703#map=18/53.488316/9.905703) |
| street_trees | strassenbaumkataster |  | [OSM](https://www.openstreetmap.org/?mlat=53.585016&mlon=9.988075#map=18/53.585016/9.988075) |
| street_trees | strassenbaumkataster |  | [OSM](https://www.openstreetmap.org/?mlat=53.636889&mlon=9.920115#map=18/53.636889/9.920115) |
| street_trees | strassenbaumkataster |  | [OSM](https://www.openstreetmap.org/?mlat=53.629494&mlon=10.055444#map=18/53.629494/10.055444) |
| street_trees | strassenbaumkataster |  | [OSM](https://www.openstreetmap.org/?mlat=53.457703&mlon=10.075808#map=18/53.457703/10.075808) |
| street_trees | strassenbaumkataster |  | [OSM](https://www.openstreetmap.org/?mlat=53.576201&mlon=10.137084#map=18/53.576201/10.137084) |
| street_trees | strassenbaumkataster |  | [OSM](https://www.openstreetmap.org/?mlat=53.486396&mlon=10.223566#map=18/53.486396/10.223566) |
| traffic_counters | locations_things | StadtRad-Station Fähranleger Finkenwerder/ Butendeichsweg | [OSM](https://www.openstreetmap.org/?mlat=53.536200&mlon=9.877750#map=18/53.536200/9.877750) |
| traffic_volumes | verkehrsmengen_dtv_hvs_2019 |  | [OSM](https://www.openstreetmap.org/?mlat=53.585042&mlon=9.739364#map=18/53.585042/9.739364) |
