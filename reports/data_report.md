# Datenbericht – Abruf Pilotbezirk

Erzeugt: 2026-10-28T14:14:26+00:00 von `pipeline/s01_fetch.py`. Nicht amtlicher Entwurf.

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
| traffic_counters | ok | 3139 | unknown | 2026-10-28 | nur Bestand (Locations + Things), keine Messwerte |
| bike_volumes_dbradplus | fehler | – | ODbL-1.0 | – | https://api.hamburg.de/datasets/v1/dbradplus/collections/jahr2025/items?f=json&bbox=557002.1468911578%2C5934196.7297488125%2C567274.8341519193%2C5946089.7089329&bbox-crs=http%3A%2F%2Fwww.opengis.net%2Fdef%2Fcrs%2FEPSG%2F0%2F25832&crs=http%3A%2F%2Fwww.opengis.net%2Fdef%2Fcrs%2FEPSG%2F0%2F25832&limit=1000&offset=10000: invalid JSON after 63156 bytes (Expecting ',' delimiter: line 1 column 63157 (char 63156)) |
| cycle_network | fallback | 11 | ODbL-1.0 | 2026-10-28 | Fallback OSM: {"relations": {"cycle_network": ["DE:HH:Radnetz_Hamburg"]}} |
| alkis | ok | 72433 | dl-de/by-2.0 | 2026-10-28 |  |
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
| population_grid | ok | 4274 | dl-de/by-2.0 | 2026-10-28 | lokale Datei wiederverwendet |
| gtfs_hvv | ok | 0 | dl-de/by-2.0 | 2026-10-28 | lokale Datei wiederverwendet |
| accidents | ok | 0 | dl-de/by-2.0 | 2026-10-28 |  |
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
| traffic_counters | locations_things | 3139 | EPSG:25832 | [557869.1, 5933864.0, 566909.7, 5945067.0] | `data/raw/traffic_counters__locations_things.parquet` |
| cycle_network | osm | 11 | EPSG:25832 | [559477.1, 5934127.3, 567331.8, 5943928.0] | `data/raw/cycle_network__osm.parquet` |
| alkis | ave:Nutzung | 12381 | EPSG:25832 | [556939.5, 5934001.7, 567665.8, 5945590.9] | `data/raw/alkis__Nutzung.parquet` |
| alkis | ave:GebaeudeBauwerk | 60052 | EPSG:25832 | [557310.5, 5934160.9, 567192.1, 5945353.4] | `data/raw/alkis__GebaeudeBauwerk.parquet` |
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
| accidents | zip_2021 | – | – | – | `data/raw/accidents/Unfallorte2021_EPSG25832_CSV.zip` |
| accidents | zip_2022 | – | – | – | `data/raw/accidents/Unfallorte2022_EPSG25832_CSV.zip` |
| accidents | zip_2023 | – | – | – | `data/raw/accidents/Unfallorte2023_EPSG25832_CSV.zip` |
| accidents | zip_2024 | – | – | – | `data/raw/accidents/Unfallorte2024_EPSG25832_CSV.zip` |
| accidents | zip_2025 | – | – | – | `data/raw/accidents/Unfallorte2025_EPSG25832_CSV.zip` |
| osm | pbf | – | – | – | `data/raw/osm/hamburg_2026-10-28.osm.pbf` |
| osm | district_boundary | 1 | EPSG:25832 | [557501.6, 5934696.6, 566774.9, 5945590.0] | `data/raw/district_boundary.parquet` |

## Angebotene Feature-Typen und Collections

- **dedications**: de.hh.up:widmung_flaeche ✔, de.hh.up:widmung_linie ✔
- **speed_limits**: tempo20zonen ✔, tempo30zonen ✔, verkehrsberuhigte_bereiche ✔, zulaessige_hoechstgeschwindigkeiten ✔, zulaessige_hoechstgeschwindigkeiten_sonderregelung ✔
- **traffic_volumes**: verkehrsmengen_dtv_bab_2019 ✔, verkehrsmengen_dtv_hvs_2019 ✔, verkehrsmengen_dtvw_bab_2013, verkehrsmengen_dtvw_hvs_2014
- **alkis**: ave:KatasterBezirk, ave:Flurstueck, ave:GebaeudeBauwerk ✔, ave:Nutzung ✔, ave:NutzungFlurstueck, ave:VerwaltungsEinheit
- **road_condition_zeb**: de.hh.up:zeb2014_geb, de.hh.up:zeb2014_gw, de.hh.up:zeb2014_sub, de.hh.up:zeb2016_geb, de.hh.up:zeb2016_gw, de.hh.up:zeb2016_sub, de.hh.up:zeb2018_geb, de.hh.up:zeb2018_gw, de.hh.up:zeb2018_sub, de.hh.up:zeb2020_geb, de.hh.up:zeb2020_gw, de.hh.up:zeb2020_sub, de.hh.up:zeb2021_geb, de.hh.up:zeb2021_gw, de.hh.up:zeb2021_sub, de.hh.up:zeb2024_geb, de.hh.up:zeb2024_gw, de.hh.up:zeb2024_sub, de.hh.up:zeb2025_geb ✔, de.hh.up:zeb2025_gw ✔, de.hh.up:zeb2025_sub ✔
- **road_surface**: de.hh.up:strassendeckschicht ✔
- **quiet_areas**: de.hh.up:ruhige_gebiete_hamburg ✔
- **accidents**: 2021, 2022, 2023, 2024, 2025

Neuester Jahrgang Verkehrsmengen Hauptverkehrsstraßen: **2019**.

## Quellenvermerke

- dedications: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (BVM) (dl-de/by-2.0)
- speed_limits: Quellenvermerk unbekannt – klären (unknown)
- traffic_volumes: Quellenvermerk unbekannt – klären (unknown)
- traffic_counters: Quellenvermerk unbekannt – klären (unknown)
- cycle_network: © OpenStreetMap-Beitragende (ODbL-1.0)
- alkis: Freie und Hansestadt Hamburg, Landesbetrieb Geoinformation und Vermessung (LGV) (dl-de/by-2.0)
- road_condition_zeb: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende, (BVM) (dl-de/by-2.0)
- road_surface: Freie und Hansestadt Hamburg, Behörde für Verkehr und Mobilitätswende (dl-de/by-2.0)
- quiet_areas: Quellenvermerk unbekannt – klären (unknown)
- schools: © OpenStreetMap-Beitragende (ODbL-1.0)
- kitas: © OpenStreetMap-Beitragende (ODbL-1.0)
- population_grid: © Statistische Ämter des Bundes und der Länder, Zensus 2022 (dl-de/by-2.0)
- gtfs_hvv: Hamburger Verkehrsverbund GmbH (dl-de/by-2.0)
- accidents: © Statistische Ämter des Bundes und der Länder, Unfallatlas (dl-de/by-2.0)
- osm: © OpenStreetMap-Beitragende (ODbL-1.0)

## Stichprobe (30 zufällige Objekte, Seed 42)

Links auf OpenStreetMap. Orthophoto- und Panoramax-Links folgen, sobald das Linkformat geklärt ist (docs/open_questions.md).

| Quelle | Ebene | Bezeichnung | Karte |
| --- | --- | --- | --- |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.601088&mlon=9.973745#map=18/53.601088/9.973745) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.634533&mlon=9.940800#map=18/53.634533/9.940800) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.570511&mlon=9.986601#map=18/53.570511/9.986601) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.605160&mlon=9.896512#map=18/53.605160/9.896512) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.632304&mlon=9.942138#map=18/53.632304/9.942138) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.585456&mlon=9.928895#map=18/53.585456/9.928895) |
| alkis | GebaeudeBauwerk | nan | [OSM](https://www.openstreetmap.org/?mlat=53.615638&mlon=9.882284#map=18/53.615638/9.882284) |
| alkis | Nutzung | nan | [OSM](https://www.openstreetmap.org/?mlat=53.632891&mlon=9.911688#map=18/53.632891/9.911688) |
| alkis | Nutzung | nan | [OSM](https://www.openstreetmap.org/?mlat=53.573033&mlon=9.945775#map=18/53.573033/9.945775) |
| alkis | Nutzung | nan | [OSM](https://www.openstreetmap.org/?mlat=53.584974&mlon=9.969315#map=18/53.584974/9.969315) |
| alkis | Nutzung | nan | [OSM](https://www.openstreetmap.org/?mlat=53.635527&mlon=9.970052#map=18/53.635527/9.970052) |
| road_condition_zeb | zeb2025_gw | Bekstück | [OSM](https://www.openstreetmap.org/?mlat=53.610750&mlon=9.964687#map=18/53.610750/9.964687) |
| road_condition_zeb | zeb2025_gw | Friedrich-Ebert-Straße | [OSM](https://www.openstreetmap.org/?mlat=53.626159&mlon=9.936836#map=18/53.626159/9.936836) |
| road_condition_zeb | zeb2025_gw | Stellinger Steindamm | [OSM](https://www.openstreetmap.org/?mlat=53.594170&mlon=9.928102#map=18/53.594170/9.928102) |
| road_condition_zeb | zeb2025_gw | Stresemannstraße | [OSM](https://www.openstreetmap.org/?mlat=53.559445&mlon=9.960944#map=18/53.559445/9.960944) |
| road_condition_zeb | zeb2025_gw | Alte Volksparkstraße | [OSM](https://www.openstreetmap.org/?mlat=53.592373&mlon=9.925526#map=18/53.592373/9.925526) |
| road_condition_zeb | zeb2025_gw | Jugendstraße | [OSM](https://www.openstreetmap.org/?mlat=53.591567&mlon=9.930715#map=18/53.591567/9.930715) |
| road_condition_zeb | zeb2025_gw | Nienkamp | [OSM](https://www.openstreetmap.org/?mlat=53.624912&mlon=9.964192#map=18/53.624912/9.964192) |
| road_condition_zeb | zeb2025_sub | Dachsberg | [OSM](https://www.openstreetmap.org/?mlat=53.626260&mlon=9.926675#map=18/53.626260/9.926675) |
| road_condition_zeb | zeb2025_sub | Gottschalkweg | [OSM](https://www.openstreetmap.org/?mlat=53.634757&mlon=9.948519#map=18/53.634757/9.948519) |
| road_condition_zeb | zeb2025_sub | Pöseldorfer Weg | [OSM](https://www.openstreetmap.org/?mlat=53.571744&mlon=9.998214#map=18/53.571744/9.998214) |
| road_condition_zeb | zeb2025_sub | Ameisenkamp | [OSM](https://www.openstreetmap.org/?mlat=53.618391&mlon=9.884243#map=18/53.618391/9.884243) |
| road_condition_zeb | zeb2025_sub | Fettstraße | [OSM](https://www.openstreetmap.org/?mlat=53.567065&mlon=9.963021#map=18/53.567065/9.963021) |
| road_condition_zeb | zeb2025_sub | Langenfelder Straße | [OSM](https://www.openstreetmap.org/?mlat=53.568570&mlon=9.946080#map=18/53.568570/9.946080) |
| road_condition_zeb | zeb2025_sub | Mergenthalerweg | [OSM](https://www.openstreetmap.org/?mlat=53.611146&mlon=9.896288#map=18/53.611146/9.896288) |
| road_condition_zeb | zeb2025_sub | Moltkestraße | [OSM](https://www.openstreetmap.org/?mlat=53.579355&mlon=9.973068#map=18/53.579355/9.973068) |
| speed_limits | tempo30zonen | Geschwister-Witonski-Straße | [OSM](https://www.openstreetmap.org/?mlat=53.648291&mlon=9.911816#map=18/53.648291/9.911816) |
| speed_limits | tempo30zonen | Puckholm | [OSM](https://www.openstreetmap.org/?mlat=53.624451&mlon=9.892527#map=18/53.624451/9.892527) |
| speed_limits | tempo30zonen | Eduardstraße | [OSM](https://www.openstreetmap.org/?mlat=53.572723&mlon=9.945544#map=18/53.572723/9.945544) |
| speed_limits | tempo30zonen | Mölenwisch | [OSM](https://www.openstreetmap.org/?mlat=53.608315&mlon=9.964006#map=18/53.608315/9.964006) |
