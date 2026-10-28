# Datenbericht – Abruf Pilotbezirk

Erzeugt: 2026-10-28T10:45:37+00:00 von `pipeline/s01_fetch.py`. Nicht amtlicher Entwurf.

## Arbeitsgebiet

- Bezirk: Eimsbüttel (OSM-Relation 30243, admin_level 9), Fläche 49.8 km²
- Puffer: 500 m, Arbeitsgebiet 69.7 km²
- Bounding Box (EPSG:25832): [557002.1, 5934196.7, 567274.8, 5946089.7]
- Grenze aus OSM, weil die ALKIS-URL in config/sources.yaml fehlt.
- Objekte, die das Arbeitsgebiet schneiden, werden vollständig übernommen (kein Zuschnitt).

## Übersicht je Quelle

| Quelle | Status | Objekte | Lizenz | Abruf | Hinweis |
| --- | --- | --- | --- | --- | --- |
| hvs_network_map | manuell | – | unknown | – | kein maschinenlesbarer Direktzugriff in sources.yaml (Webseite/PDF) |
| strategic_road_network | fehler | – | dl-de/by-2.0 | – | https://geodienste.hamburg.de/HH_WFS_Strategisches_Strassennetz: HTTP 404 |
| dedications | ok | 6259 | dl-de/by-2.0 | 2026-10-28 |  |
| speed_limits | ok | 8010 | unknown | 2026-10-28 |  |
| traffic_volumes | ok | 690 | unknown | 2026-10-28 |  |
| traffic_counters | ok | 3138 | unknown | 2026-10-28 | nur Bestand (Locations + Things), keine Messwerte |
| bike_volumes_dbradplus | fehler | – | ODbL-1.0 | – | https://api.hamburg.de/datasets/v1/dbradplus/collections/jahr2025/items?f=json&bbox=557002.1468911578%2C5934196.7297488125%2C567274.8341519193%2C5946089.7089329&bbox-crs=http%3A%2F%2Fwww.opengis.net%2Fdef%2Fcrs%2FEPSG%2F0%2F25832&crs=http%3A%2F%2Fwww.opengis.net%2Fdef%2Fcrs%2FEPSG%2F0%2F25832&limit=1000&offset=10000: invalid JSON after 63156 bytes (Expecting ',' delimiter: line 1 column 63157 (char 63156)) |
| cycle_network | fallback | 11 | ODbL-1.0 | 2026-10-28 | Fallback OSM: {"relations": {"cycle_network": ["DE:HH:Radnetz_Hamburg"]}} |
| alkis | fehlt | – | dl-de/by-2.0 | – | TODO: WFS 'ALKIS – Liegenschaften und Verwaltungseinheiten' bzw. NAS-Download im Transparenzportal |
| buildings_3d | fehlt | – | dl-de/by-2.0 | – | TODO: Transparenzportal |
| orthophotos | fehlt | – | dl-de/by-2.0 | – | TODO: Transparenzportal / WMS |
| laserscan | fehlt | – | unknown | – | TODO |
| street_trees | fehlt | – | unknown | – | TODO: Transparenzportal |
| road_condition_zeb | ok | 111174 | dl-de/by-2.0 | 2026-10-28 |  |
| road_surface | ok | 5096 | dl-de/by-2.0 | 2026-10-28 |  |
| quiet_areas | ok | 0 | unknown | 2026-10-28 | de.hh.up:ruhige_gebiete_hamburg: 0 Objekte im Arbeitsgebiet, 15 im gesamten Dienst |
| noise_maps | fehlt | – | unbekannt | – | TODO |
| schools | fallback | 93 | ODbL-1.0 | 2026-10-28 | Fallback OSM: {"tags": {"amenity": ["school"]}} |
| kitas | fallback | 220 | ODbL-1.0 | 2026-10-28 | Fallback OSM: {"tags": {"amenity": ["kindergarten"]}} |
| population_grid | ok | 4274 | dl-de/by-2.0 | 2026-10-28 |  |
| gtfs_hvv | ok | 0 | dl-de/by-2.0 | 2026-10-28 |  |
| accidents | fehlt | – | dl-de/by-2.0 | – | TODO: Opendata-Seite auf unfallatlas.statistikportal.de, Jahre einzeln |
| osm | ok | 1 | ODbL-1.0 | 2026-10-28 | lokale Datei wiederverwendet (Stand Wed, 28 Oct 2026 03:56:24 GMT) |

## Ebenen

| Quelle | Ebene | Objekte | CRS | Bounding Box | Datei |
| --- | --- | --- | --- | --- | --- |
| dedications | de.hh.up:widmung_flaeche | 455 | EPSG:25832 | [557593.7, 5934101.2, 566761.0, 5945009.9] | `data/raw/dedications__widmung_flaeche.parquet` |
| dedications | de.hh.up:widmung_linie | 5804 | EPSG:25832 | [557358.8, 5933728.4, 567231.7, 5946516.1] | `data/raw/dedications__widmung_linie.parquet` |
| speed_limits | tempo20zonen | 22 | EPSG:25832 | [559611.5, 5934263.5, 565782.0, 5940417.7] | `data/raw/speed_limits__tempo20zonen.parquet` |
| speed_limits | tempo30zonen | 2810 | EPSG:25832 | [557363.9, 5934611.5, 567151.6, 5945503.8] | `data/raw/speed_limits__tempo30zonen.parquet` |
| speed_limits | verkehrsberuhigte_bereiche | 100 | EPSG:25832 | [557471.0, 5935031.0, 566018.2, 5945272.7] | `data/raw/speed_limits__verkehrsberuhigte_bereiche.parquet` |
| speed_limits | zulaessige_hoechstgeschwindigkeiten | 4916 | EPSG:25832 | [557363.9, 5933728.4, 567231.7, 5945503.8] | `data/raw/speed_limits__zulaessige_hoechstgeschwindigkeiten.parquet` |
| speed_limits | zulaessige_hoechstgeschwindigkeiten_sonderregelung | 162 | EPSG:25832 | [558472.0, 5934911.0, 565856.8, 5944500.3] | `data/raw/speed_limits__zulaessige_hoechstgeschwindigkeiten_sonderregelung.parquet` |
| traffic_volumes | verkehrsmengen_dtv_hvs_2019 | 598 | EPSG:25832 | [557979.4, 5934259.0, 567018.7, 5945253.2] | `data/raw/traffic_volumes__verkehrsmengen_dtv_hvs_2019.parquet` |
| traffic_volumes | verkehrsmengen_dtv_bab_2019 | 92 | EPSG:25832 | [557583.4, 5936922.6, 561516.1, 5945291.2] | `data/raw/traffic_volumes__verkehrsmengen_dtv_bab_2019.parquet` |
| traffic_counters | locations_things | 3138 | EPSG:25832 | [557869.1, 5933864.0, 566909.7, 5945067.0] | `data/raw/traffic_counters__locations_things.parquet` |
| cycle_network | osm | 11 | EPSG:25832 | [559477.1, 5934127.3, 567331.8, 5943928.0] | `data/raw/cycle_network__osm.parquet` |
| road_condition_zeb | de.hh.up:zeb2025_geb | 18529 | EPSG:25832 | [557375.7, 5934189.9, 567196.9, 5945503.7] | `data/raw/road_condition_zeb__zeb2025_geb.parquet` |
| road_condition_zeb | de.hh.up:zeb2025_gw | 55587 | EPSG:25832 | [557375.7, 5934189.9, 567196.9, 5945503.7] | `data/raw/road_condition_zeb__zeb2025_gw.parquet` |
| road_condition_zeb | de.hh.up:zeb2025_sub | 37058 | EPSG:25832 | [557375.7, 5934189.9, 567196.9, 5945503.7] | `data/raw/road_condition_zeb__zeb2025_sub.parquet` |
| road_surface | de.hh.up:strassendeckschicht | 5096 | EPSG:25832 | [557363.9, 5934161.6, 567231.7, 5945503.8] | `data/raw/road_surface__strassendeckschicht.parquet` |
| quiet_areas | de.hh.up:ruhige_gebiete_hamburg | 0 | EPSG:25832 | None | `data/raw/quiet_areas__ruhige_gebiete_hamburg.parquet` |
| schools | osm | 93 | EPSG:25832 | [557647.5, 5934652.4, 566606.5, 5944650.8] | `data/raw/schools__osm.parquet` |
| kitas | osm | 220 | EPSG:25832 | [558525.5, 5935025.8, 566075.0, 5944951.6] | `data/raw/kitas__osm.parquet` |
| population_grid | zip | – | – | – | `data/raw/population_grid/Zensus2022_Bevoelkerungszahl.zip` |
| population_grid | 100m | 4274 | EPSG:25832 | [556956.0, 5934137.8, 567325.9, 5946066.6] | `data/raw/population_grid__100m.parquet` |
| gtfs_hvv | zip | – | – | – | `data/raw/gtfs_hvv/Upload__hvv_Rohdaten_GTFS_Fpl_20260408.ZIP` |
| osm | pbf | – | – | – | `data/raw/osm/hamburg_2026-10-28.osm.pbf` |
| osm | district_boundary | 1 | EPSG:25832 | [557501.6, 5934696.6, 566774.9, 5945590.0] | `data/raw/district_boundary.parquet` |

## Angebotene Feature-Typen und Collections

- **dedications**: de.hh.up:widmung_flaeche ✔, de.hh.up:widmung_linie ✔
- **speed_limits**: tempo20zonen ✔, tempo30zonen ✔, verkehrsberuhigte_bereiche ✔, zulaessige_hoechstgeschwindigkeiten ✔, zulaessige_hoechstgeschwindigkeiten_sonderregelung ✔
- **traffic_volumes**: verkehrsmengen_dtv_bab_2019 ✔, verkehrsmengen_dtv_hvs_2019 ✔, verkehrsmengen_dtvw_bab_2013, verkehrsmengen_dtvw_hvs_2014
- **road_condition_zeb**: de.hh.up:zeb2014_geb, de.hh.up:zeb2014_gw, de.hh.up:zeb2014_sub, de.hh.up:zeb2016_geb, de.hh.up:zeb2016_gw, de.hh.up:zeb2016_sub, de.hh.up:zeb2018_geb, de.hh.up:zeb2018_gw, de.hh.up:zeb2018_sub, de.hh.up:zeb2020_geb, de.hh.up:zeb2020_gw, de.hh.up:zeb2020_sub, de.hh.up:zeb2021_geb, de.hh.up:zeb2021_gw, de.hh.up:zeb2021_sub, de.hh.up:zeb2024_geb, de.hh.up:zeb2024_gw, de.hh.up:zeb2024_sub, de.hh.up:zeb2025_geb ✔, de.hh.up:zeb2025_gw ✔, de.hh.up:zeb2025_sub ✔
- **road_surface**: de.hh.up:strassendeckschicht ✔
- **quiet_areas**: de.hh.up:ruhige_gebiete_hamburg ✔

Neuester Jahrgang Verkehrsmengen Hauptverkehrsstraßen: **2019**.

## Quellenvermerke

- dedications: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (BVM) (dl-de/by-2.0)
- speed_limits: Quellenvermerk unbekannt – klären (unknown)
- traffic_volumes: Quellenvermerk unbekannt – klären (unknown)
- traffic_counters: Quellenvermerk unbekannt – klären (unknown)
- cycle_network: © OpenStreetMap-Beitragende (ODbL-1.0)
- road_condition_zeb: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende, (BVM) (dl-de/by-2.0)
- road_surface: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (dl-de/by-2.0)
- quiet_areas: Quellenvermerk unbekannt – klären (unknown)
- schools: © OpenStreetMap-Beitragende (ODbL-1.0)
- kitas: © OpenStreetMap-Beitragende (ODbL-1.0)
- population_grid: © Statistische Ämter des Bundes und der Länder, Zensus 2022 (dl-de/by-2.0)
- gtfs_hvv: Hamburger Verkehrsverbund GmbH (dl-de/by-2.0)
- osm: © OpenStreetMap-Beitragende (ODbL-1.0)

## Stichprobe (30 zufällige Objekte, Seed 42)

Links auf OpenStreetMap. Orthophoto- und Panoramax-Links folgen, sobald das Linkformat geklärt ist (docs/open_questions.md).

| Quelle | Ebene | Bezeichnung | Karte |
| --- | --- | --- | --- |
| dedications | widmung_linie | Gazellenkamp | [OSM](https://www.openstreetmap.org/?mlat=53.599347&mlon=9.944359#map=18/53.599347/9.944359) |
| road_condition_zeb | zeb2025_geb | Försterweg | [OSM](https://www.openstreetmap.org/?mlat=53.579772&mlon=9.927407#map=18/53.579772/9.927407) |
| road_condition_zeb | zeb2025_geb | Hagenbeckallee | [OSM](https://www.openstreetmap.org/?mlat=53.595280&mlon=9.938553#map=18/53.595280/9.938553) |
| road_condition_zeb | zeb2025_geb | Julius-Vosseler-Straße | [OSM](https://www.openstreetmap.org/?mlat=53.584178&mlon=9.950277#map=18/53.584178/9.950277) |
| road_condition_zeb | zeb2025_geb | Jungfrauenthal | [OSM](https://www.openstreetmap.org/?mlat=53.581228&mlon=9.982664#map=18/53.581228/9.982664) |
| road_condition_zeb | zeb2025_geb | Milchstraße | [OSM](https://www.openstreetmap.org/?mlat=53.570672&mlon=9.997352#map=18/53.570672/9.997352) |
| road_condition_zeb | zeb2025_geb | Zum Niendorfer Grenzhaus | [OSM](https://www.openstreetmap.org/?mlat=53.648878&mlon=9.947318#map=18/53.648878/9.947318) |
| road_condition_zeb | zeb2025_gw | Ernst-Horn-Straße | [OSM](https://www.openstreetmap.org/?mlat=53.584038&mlon=9.925755#map=18/53.584038/9.925755) |
| road_condition_zeb | zeb2025_gw | Gaedechensweg | [OSM](https://www.openstreetmap.org/?mlat=53.587869&mlon=9.993470#map=18/53.587869/9.993470) |
| road_condition_zeb | zeb2025_gw | Susannenstraße | [OSM](https://www.openstreetmap.org/?mlat=53.562295&mlon=9.963403#map=18/53.562295/9.963403) |
| road_condition_zeb | zeb2025_gw | Baumacker | [OSM](https://www.openstreetmap.org/?mlat=53.621137&mlon=9.895311#map=18/53.621137/9.895311) |
| road_condition_zeb | zeb2025_gw | Borsteler Chaussee | [OSM](https://www.openstreetmap.org/?mlat=53.618636&mlon=9.974605#map=18/53.618636/9.974605) |
| road_condition_zeb | zeb2025_gw | Burgunderweg | [OSM](https://www.openstreetmap.org/?mlat=53.631449&mlon=9.975773#map=18/53.631449/9.975773) |
| road_condition_zeb | zeb2025_gw | Dorpsfelde | [OSM](https://www.openstreetmap.org/?mlat=53.609884&mlon=9.915311#map=18/53.609884/9.915311) |
| road_condition_zeb | zeb2025_gw | Grandweg | [OSM](https://www.openstreetmap.org/?mlat=53.589291&mlon=9.964558#map=18/53.589291/9.964558) |
| road_condition_zeb | zeb2025_gw | Keltenweg | [OSM](https://www.openstreetmap.org/?mlat=53.645783&mlon=9.954634#map=18/53.645783/9.954634) |
| road_condition_zeb | zeb2025_gw | Waterloostraße | [OSM](https://www.openstreetmap.org/?mlat=53.566939&mlon=9.955602#map=18/53.566939/9.955602) |
| road_condition_zeb | zeb2025_gw | Wunderbrunnen | [OSM](https://www.openstreetmap.org/?mlat=53.645646&mlon=9.926104#map=18/53.645646/9.926104) |
| road_condition_zeb | zeb2025_gw | Winsbergring | [OSM](https://www.openstreetmap.org/?mlat=53.576667&mlon=9.918173#map=18/53.576667/9.918173) |
| road_condition_zeb | zeb2025_gw | Sedanstraße | [OSM](https://www.openstreetmap.org/?mlat=53.569866&mlon=9.978941#map=18/53.569866/9.978941) |
| road_condition_zeb | zeb2025_gw | Syringenweg | [OSM](https://www.openstreetmap.org/?mlat=53.615695&mlon=9.880902#map=18/53.615695/9.880902) |
| road_condition_zeb | zeb2025_sub | Winsbergring | [OSM](https://www.openstreetmap.org/?mlat=53.576642&mlon=9.917875#map=18/53.576642/9.917875) |
| road_condition_zeb | zeb2025_sub | Nyswanderweg | [OSM](https://www.openstreetmap.org/?mlat=53.619667&mlon=9.894572#map=18/53.619667/9.894572) |
| road_condition_zeb | zeb2025_sub | Abendrothsweg | [OSM](https://www.openstreetmap.org/?mlat=53.585513&mlon=9.978669#map=18/53.585513/9.978669) |
| road_condition_zeb | zeb2025_sub | Hegestieg | [OSM](https://www.openstreetmap.org/?mlat=53.584997&mlon=9.983803#map=18/53.584997/9.983803) |
| road_surface | strassendeckschicht | Schwalbenweg | [OSM](https://www.openstreetmap.org/?mlat=53.620757&mlon=9.963045#map=18/53.620757/9.963045) |
| speed_limits | tempo30zonen | Geschwister-Witonski-Straße | [OSM](https://www.openstreetmap.org/?mlat=53.648291&mlon=9.911816#map=18/53.648291/9.911816) |
| speed_limits | tempo30zonen | Puckholm | [OSM](https://www.openstreetmap.org/?mlat=53.624451&mlon=9.892527#map=18/53.624451/9.892527) |
| speed_limits | tempo30zonen | Eduardstraße | [OSM](https://www.openstreetmap.org/?mlat=53.572723&mlon=9.945544#map=18/53.572723/9.945544) |
| speed_limits | tempo30zonen | Mölenwisch | [OSM](https://www.openstreetmap.org/?mlat=53.608315&mlon=9.964006#map=18/53.608315/9.964006) |
