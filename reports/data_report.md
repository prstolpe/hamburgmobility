# Datenbericht – Abruf Pilotbezirk

Erzeugt: 2026-10-28T09:45:02+00:00 von `pipeline/s01_fetch.py`. Nicht amtlicher Entwurf.

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
| traffic_counters | ok | 3137 | unknown | 2026-10-28 | nur Bestand (Locations + Things), keine Messwerte |
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
| population_grid | manuell | – | unknown | – | kein maschinenlesbarer Direktzugriff in sources.yaml (Webseite/PDF) |
| gtfs_hvv | fehlt | – | dl-de/by-2.0 | – | TODO: aktuellen Datensatz im Transparenzportal wählen ("hvv Fahrplandaten GTFS") |
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
| traffic_counters | locations_things | 3137 | EPSG:25832 | [557869.1, 5933864.0, 566909.7, 5945067.0] | `data/raw/traffic_counters__locations_things.parquet` |
| cycle_network | osm | 11 | EPSG:25832 | [559477.1, 5934127.3, 567331.8, 5943928.0] | `data/raw/cycle_network__osm.parquet` |
| road_condition_zeb | de.hh.up:zeb2025_geb | 18529 | EPSG:25832 | [557375.7, 5934189.9, 567196.9, 5945503.7] | `data/raw/road_condition_zeb__zeb2025_geb.parquet` |
| road_condition_zeb | de.hh.up:zeb2025_gw | 55587 | EPSG:25832 | [557375.7, 5934189.9, 567196.9, 5945503.7] | `data/raw/road_condition_zeb__zeb2025_gw.parquet` |
| road_condition_zeb | de.hh.up:zeb2025_sub | 37058 | EPSG:25832 | [557375.7, 5934189.9, 567196.9, 5945503.7] | `data/raw/road_condition_zeb__zeb2025_sub.parquet` |
| road_surface | de.hh.up:strassendeckschicht | 5096 | EPSG:25832 | [557363.9, 5934161.6, 567231.7, 5945503.8] | `data/raw/road_surface__strassendeckschicht.parquet` |
| quiet_areas | de.hh.up:ruhige_gebiete_hamburg | 0 | EPSG:25832 | None | `data/raw/quiet_areas__ruhige_gebiete_hamburg.parquet` |
| schools | osm | 93 | EPSG:25832 | [557647.5, 5934652.4, 566606.5, 5944650.8] | `data/raw/schools__osm.parquet` |
| kitas | osm | 220 | EPSG:25832 | [558525.5, 5935025.8, 566075.0, 5944951.6] | `data/raw/kitas__osm.parquet` |
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
- osm: © OpenStreetMap-Beitragende (ODbL-1.0)

## Stichprobe (30 zufällige Objekte, Seed 42)

Links auf OpenStreetMap. Orthophoto- und Panoramax-Links folgen, sobald das Linkformat geklärt ist (docs/open_questions.md).

| Quelle | Ebene | Bezeichnung | Karte |
| --- | --- | --- | --- |
| dedications | widmung_linie | Gazellenkamp | [OSM](https://www.openstreetmap.org/?mlat=53.599347&mlon=9.944359#map=18/53.599347/9.944359) |
| road_condition_zeb | zeb2025_geb | Försterweg | [OSM](https://www.openstreetmap.org/?mlat=53.579679&mlon=9.927565#map=18/53.579679/9.927565) |
| road_condition_zeb | zeb2025_geb | Hagenbeckallee | [OSM](https://www.openstreetmap.org/?mlat=53.595323&mlon=9.938769#map=18/53.595323/9.938769) |
| road_condition_zeb | zeb2025_geb | Julius-Vosseler-Straße | [OSM](https://www.openstreetmap.org/?mlat=53.584340&mlon=9.950270#map=18/53.584340/9.950270) |
| road_condition_zeb | zeb2025_geb | Jungfrauenthal | [OSM](https://www.openstreetmap.org/?mlat=53.581229&mlon=9.982964#map=18/53.581229/9.982964) |
| road_condition_zeb | zeb2025_geb | Milchstraße | [OSM](https://www.openstreetmap.org/?mlat=53.570696&mlon=9.997618#map=18/53.570696/9.997618) |
| road_condition_zeb | zeb2025_geb | Zum Niendorfer Grenzhaus | [OSM](https://www.openstreetmap.org/?mlat=53.648958&mlon=9.947508#map=18/53.648958/9.947508) |
| road_condition_zeb | zeb2025_gw | Ernst-Horn-Straße | [OSM](https://www.openstreetmap.org/?mlat=53.584095&mlon=9.925511#map=18/53.584095/9.925511) |
| road_condition_zeb | zeb2025_gw | Gaedechensweg | [OSM](https://www.openstreetmap.org/?mlat=53.588120&mlon=9.993855#map=18/53.588120/9.993855) |
| road_condition_zeb | zeb2025_gw | Susannenstraße | [OSM](https://www.openstreetmap.org/?mlat=53.562408&mlon=9.963691#map=18/53.562408/9.963691) |
| road_condition_zeb | zeb2025_gw | Baumacker | [OSM](https://www.openstreetmap.org/?mlat=53.621322&mlon=9.895255#map=18/53.621322/9.895255) |
| road_condition_zeb | zeb2025_gw | Borsteler Chaussee | [OSM](https://www.openstreetmap.org/?mlat=53.611002&mlon=9.974597#map=18/53.611002/9.974597) |
| road_condition_zeb | zeb2025_gw | Burgunderweg | [OSM](https://www.openstreetmap.org/?mlat=53.631589&mlon=9.975962#map=18/53.631589/9.975962) |
| road_condition_zeb | zeb2025_gw | Dorpsfelde | [OSM](https://www.openstreetmap.org/?mlat=53.609955&mlon=9.914971#map=18/53.609955/9.914971) |
| road_condition_zeb | zeb2025_gw | Grandweg | [OSM](https://www.openstreetmap.org/?mlat=53.589434&mlon=9.964373#map=18/53.589434/9.964373) |
| road_condition_zeb | zeb2025_gw | Keltenweg | [OSM](https://www.openstreetmap.org/?mlat=53.645741&mlon=9.954785#map=18/53.645741/9.954785) |
| road_condition_zeb | zeb2025_gw | Waterloostraße | [OSM](https://www.openstreetmap.org/?mlat=53.566988&mlon=9.955933#map=18/53.566988/9.955933) |
| road_condition_zeb | zeb2025_gw | Wunderbrunnen | [OSM](https://www.openstreetmap.org/?mlat=53.645833&mlon=9.926063#map=18/53.645833/9.926063) |
| road_condition_zeb | zeb2025_gw | Winsbergring | [OSM](https://www.openstreetmap.org/?mlat=53.576692&mlon=9.918472#map=18/53.576692/9.918472) |
| road_condition_zeb | zeb2025_gw | Seerosenweg | [OSM](https://www.openstreetmap.org/?mlat=53.614163&mlon=9.875769#map=18/53.614163/9.875769) |
| road_condition_zeb | zeb2025_gw | Syringenweg | [OSM](https://www.openstreetmap.org/?mlat=53.615646&mlon=9.881108#map=18/53.615646/9.881108) |
| road_condition_zeb | zeb2025_sub | Winsbergring | [OSM](https://www.openstreetmap.org/?mlat=53.576667&mlon=9.918173#map=18/53.576667/9.918173) |
| road_condition_zeb | zeb2025_sub | Nyswanderweg | [OSM](https://www.openstreetmap.org/?mlat=53.619648&mlon=9.894300#map=18/53.619648/9.894300) |
| road_condition_zeb | zeb2025_sub | Abendrothsweg | [OSM](https://www.openstreetmap.org/?mlat=53.585434&mlon=9.978398#map=18/53.585434/9.978398) |
| road_condition_zeb | zeb2025_sub | Hegestieg | [OSM](https://www.openstreetmap.org/?mlat=53.585113&mlon=9.983577#map=18/53.585113/9.983577) |
| road_surface | strassendeckschicht | Döhrnstraße | [OSM](https://www.openstreetmap.org/?mlat=53.598463&mlon=9.953053#map=18/53.598463/9.953053) |
| speed_limits | tempo30zonen | Geschwister-Witonski-Straße | [OSM](https://www.openstreetmap.org/?mlat=53.648291&mlon=9.911816#map=18/53.648291/9.911816) |
| speed_limits | tempo30zonen | Puckholm | [OSM](https://www.openstreetmap.org/?mlat=53.624451&mlon=9.892527#map=18/53.624451/9.892527) |
| speed_limits | tempo30zonen | Eduardstraße | [OSM](https://www.openstreetmap.org/?mlat=53.572723&mlon=9.945544#map=18/53.572723/9.945544) |
| speed_limits | tempo30zonen | Mölenwisch | [OSM](https://www.openstreetmap.org/?mlat=53.608315&mlon=9.964006#map=18/53.608315/9.964006) |
