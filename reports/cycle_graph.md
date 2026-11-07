# Radgraph (Stufe c01)

Erzeugt 2026-11-07T13:06:24+00:00 mit pipeline/c01_cycle_graph.py · cycling_rules.yaml 0.7.0 · OSM-Auszug `data/raw/osm/hamburg_2026-10-28.osm.pbf` (SHA-256 700d2e2603a7…) · nicht amtlicher Entwurf

## Kennzahlen

- Kanten: 65 973 (6 430.4 km), Knoten: 46 682
- OSM-Knotenkanten gelesen: 848 309; Straßenkanten ohne Abschnitt verworfen: 0
- Fähren: 64 OSM-Linien, davon 50 als Kante (bicycle-Werte: customers 11, no 1, private 1, yes 47, – 4); Wartezeit 450 s, Anbindung ≤ 400 m (C-GRAPH-03)
- Größte stark zusammenhängende Komponente: 6 217.7 km (96.7% der Länge)
- Nur in einer Richtung befahrbar: 17 934 Kanten; in keiner Richtung (widersprüchliche oneway-Angaben der OSM-Wege einer Kante): 16 Kanten, 1 237 m
- Eigenständige Wege mit Bezug zu einem Straßenabschnitt (sidepath_of, C-GRAPH-06): 8 096 von 21 638
- Laufzeit: Lesen und Widerstand 22 s, Zusammenfassen 7 s

## Länge nach Kantenart und Widerstandsregel

| Art | Regel | Faktor (Mittel) | km | Anteil |
| --- | --- | ---: | ---: | ---: |
| ferry | C-GRAPH-03 | 1.00 | 47.0 | 0.7% |
| path | C-IMP-01 | 1.00 | 0.6 | 0.0% |
| path | C-IMP-02 | 1.10 | 1 756.6 | 27.3% |
| road | C-IMP-01 | 1.01 | 25.4 | 0.4% |
| road | C-IMP-03 | 1.11 | 403.7 | 6.3% |
| road | C-IMP-04 | 1.07 | 2 483.6 | 38.6% |
| road | C-IMP-05 | 1.25 | 3.6 | 0.1% |
| road | C-IMP-06 | 1.25 | 46.3 | 0.7% |
| road | C-IMP-07 | 1.54 | 1 663.7 | 25.9% |

Regeln: config/cycling_rules.yaml (`routing_impedance.ist_mapping`, `cycle_graph`). Alle Werte sind Annahmen (status draft).

## Länge je Bezirk

| Bezirk | km | davon eigenständige Wege |
| --- | ---: | ---: |
| Altona | 787.5 | 186.6 |
| Bergedorf | 631.5 | 149.0 |
| Eimsbüttel | 629.2 | 188.2 |
| Hamburg-Mitte | 1 102.3 | 305.9 |
| Hamburg-Nord | 805.6 | 246.7 |
| Harburg | 701.3 | 178.0 |
| Wandsbek | 1 476.3 | 444.5 |
| ohne Bezirk | 296.7 | 58.3 |

## 30 Zufallsstichproben (Seed 42)

| edge_id | Bezirk | Name | Art | Regel | Faktor | Richtungen | Prüfen |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `ce_0e1d83d28915dc9e` | Altona | Bernstorffstraße | road | C-IMP-04 | 1.05 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563529,5934847]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558658/9.959080) · [OSM](https://www.openstreetmap.org/?mlat=53.558658&mlon=9.959080#map=18/53.558658/9.959080) · [Way](https://www.openstreetmap.org/way/143018789) |
| `ce_39ca73731ebf95ee` | Altona | Hasenhöhe | road | C-IMP-04 | 1.05 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554289,5935954]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.569638/9.819784) · [OSM](https://www.openstreetmap.org/?mlat=53.569638&mlon=9.819784#map=18/53.569638/9.819784) · [Way](https://www.openstreetmap.org/way/131627197) |
| `ce_7d278eefb73f963b` | Altona | Max-Brauer-Allee | road | C-IMP-07 | 1.50 | eine | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562307,5934366]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.554483/9.940531) · [OSM](https://www.openstreetmap.org/?mlat=53.554483&mlon=9.940531#map=18/53.554483/9.940531) · [Way](https://www.openstreetmap.org/way/1378728926) |
| `ce_8ac9fedb1ac33744` | Altona | – | path | C-IMP-02 | 1.00 | eine | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559221,5935553]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.565500/9.894174) · [OSM](https://www.openstreetmap.org/?mlat=53.565500&mlon=9.894174#map=18/53.565500/9.894174) · [Way](https://www.openstreetmap.org/way/727131084) |
| `ce_2bc960a2ce848093` | Bergedorf | Sichter | road | C-IMP-04 | 1.37 | eine | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580914,5927340]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.488798/10.219532) · [OSM](https://www.openstreetmap.org/?mlat=53.488798&mlon=10.219532#map=18/53.488798/10.219532) · [Way](https://www.openstreetmap.org/way/152222483) |
| `ce_3b2bb8473d28d4d6` | Bergedorf | Bockhorster Höhe | road | C-IMP-04 | 1.05 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577876,5930261]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.515511/10.174475) · [OSM](https://www.openstreetmap.org/?mlat=53.515511&mlon=10.174475#map=18/53.515511/10.174475) · [Way](https://www.openstreetmap.org/way/25753629) |
| `ce_5b12a772e8bb4ac2` | Bergedorf | Wehrdeich | road | C-IMP-04 | 1.05 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578803,5927078]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.486770/10.187651) · [OSM](https://www.openstreetmap.org/?mlat=53.486770&mlon=10.187651#map=18/53.486770/10.187651) · [Way](https://www.openstreetmap.org/way/153805769) |
| `ce_8b6e96eb4c52fa7a` | Eimsbüttel | Kollaustraße | road | C-IMP-07 | 1.50 | eine | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563641,5939867]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.603761/9.961784) · [OSM](https://www.openstreetmap.org/?mlat=53.603761&mlon=9.961784#map=18/53.603761/9.961784) · [Way](https://www.openstreetmap.org/way/650779284) |
| `ce_abc63b4339ab0cf1` | Eimsbüttel | Vizelinstraße | road | C-IMP-04 | 1.05 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563311,5938066]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.587613/9.956437) · [OSM](https://www.openstreetmap.org/?mlat=53.587613&mlon=9.956437#map=18/53.587613/9.956437) · [Way](https://www.openstreetmap.org/way/1072289747) |
| `ce_bd28f32e94221ee7` | Eimsbüttel | – | path | C-IMP-02 | 1.00 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563192,5936274]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.571521/9.954272) · [OSM](https://www.openstreetmap.org/?mlat=53.571521&mlon=9.954272#map=18/53.571521/9.954272) · [Way](https://www.openstreetmap.org/way/22562958) |
| `ce_e679de9bc1929faf` | Eimsbüttel | Krähenweg | road | C-IMP-07 | 1.50 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563175,5943093]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.632808/9.955400) · [OSM](https://www.openstreetmap.org/?mlat=53.632808&mlon=9.955400#map=18/53.632808/9.955400) · [Way](https://www.openstreetmap.org/way/47371972) |
| `ce_0a352bd6a099c14e` | Hamburg-Mitte | Brackhövel | road | C-IMP-04 | 1.05 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567439,5929639]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.511363/10.016975) · [OSM](https://www.openstreetmap.org/?mlat=53.511363&mlon=10.016975#map=18/53.511363/10.016975) · [Way](https://www.openstreetmap.org/way/674042166) |
| `ce_0ab61ce081cef0a2` | Hamburg-Mitte | Industriestraße | road | C-IMP-07 | 1.50 | eine | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565164,5928982]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.505745/9.982524) · [OSM](https://www.openstreetmap.org/?mlat=53.505745&mlon=9.982524#map=18/53.505745/9.982524) · [Way](https://www.openstreetmap.org/way/692333158) |
| `ce_1c8f8bea44e2319b` | Hamburg-Mitte | Reinskamp | road | C-IMP-04 | 1.05 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575143,5933949]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.549053/10.134149) · [OSM](https://www.openstreetmap.org/?mlat=53.549053&mlon=10.134149#map=18/53.549053/10.134149) · [Way](https://www.openstreetmap.org/way/697764149) |
| `ce_8f301622eace1ec0` | Hamburg-Mitte | Havighorster Redder | road | C-IMP-07 | 1.50 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576023,5931558]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.527433/10.146854) · [OSM](https://www.openstreetmap.org/?mlat=53.527433&mlon=10.146854#map=18/53.527433/10.146854) · [Way](https://www.openstreetmap.org/way/3075474) |
| `ce_c736f2f5628149a0` | Hamburg-Mitte | Billwerder Neuer Deich | road | C-IMP-04 | 1.05 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568321,5932466]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.536659/10.030876) · [OSM](https://www.openstreetmap.org/?mlat=53.536659&mlon=10.030876#map=18/53.536659/10.030876) · [Way](https://www.openstreetmap.org/way/139785377) |
| `ce_2451736874fe34f0` | Hamburg-Nord | – | path | C-IMP-02 | 1.30 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567384,5938262]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.588866/10.017998) · [OSM](https://www.openstreetmap.org/?mlat=53.588866&mlon=10.017998#map=18/53.588866/10.017998) · [Way](https://www.openstreetmap.org/way/144956167) |
| `ce_571787c7fb7dac1b` | Hamburg-Nord | Suhrenkamp | road | C-IMP-04 | 1.05 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566950,5941559]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.618549/10.012154) · [OSM](https://www.openstreetmap.org/?mlat=53.618549&mlon=10.012154#map=18/53.618549/10.012154) · [Way](https://www.openstreetmap.org/way/146632932) |
| `ce_5d82bea214ccc77e` | Hamburg-Nord | – | path | C-IMP-02 | 1.00 | eine | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570240,5938307]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.588895/10.061141) · [OSM](https://www.openstreetmap.org/?mlat=53.588895&mlon=10.061141#map=18/53.588895/10.061141) · [Way](https://www.openstreetmap.org/way/1570893327) |
| `ce_cad60c6595213f95` | Hamburg-Nord | – | path | C-IMP-02 | 1.30 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565849,5947116]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.668633/9.996687) · [OSM](https://www.openstreetmap.org/?mlat=53.668633&mlon=9.996687#map=18/53.668633/9.996687) · [Way](https://www.openstreetmap.org/way/34690554) |
| `ce_0b5c7abf5fc36f0b` | Harburg | – | path | C-IMP-02 | 1.00 | eine | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555777,5925142]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.472314/9.840326) · [OSM](https://www.openstreetmap.org/?mlat=53.472314&mlon=9.840326#map=18/53.472314/9.840326) · [Way](https://www.openstreetmap.org/way/1332159167) |
| `ce_d35fee753dfd8605` | Harburg | Cuxhavener Straße | road | C-IMP-07 | 1.50 | eine | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558181,5925138]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.472012/9.876549) · [OSM](https://www.openstreetmap.org/?mlat=53.472012&mlon=9.876549#map=18/53.472012/9.876549) · [Way](https://www.openstreetmap.org/way/232588397) |
| `ce_e236be26b3192f6e` | Harburg | – | path | C-IMP-02 | 1.00 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564811,5922969]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.451747/9.975968) · [OSM](https://www.openstreetmap.org/?mlat=53.451747&mlon=9.975968#map=18/53.451747/9.975968) · [Way](https://www.openstreetmap.org/way/27860942) |
| `ce_3a77b3f377c7fff9` | Wandsbek | Sonnenweg | road | C-IMP-07 | 1.50 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574383,5938419]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.589329/10.123753) · [OSM](https://www.openstreetmap.org/?mlat=53.589329&mlon=10.123753#map=18/53.589329/10.123753) · [Way](https://www.openstreetmap.org/way/1302526811) |
| `ce_7be121ee4e62a624` | Wandsbek | Baggesenstieg | road | C-IMP-04 | 1.05 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572617,5945496]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.653182/10.098731) · [OSM](https://www.openstreetmap.org/?mlat=53.653182&mlon=10.098731#map=18/53.653182/10.098731) · [Way](https://www.openstreetmap.org/way/22793448) |
| `ce_a06e8872ffc89448` | Wandsbek | Baben de Möhl | road | C-IMP-04 | 1.05 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573273,5947692]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.672825/10.109172) · [OSM](https://www.openstreetmap.org/?mlat=53.672825&mlon=10.109172#map=18/53.672825/10.109172) · [Way](https://www.openstreetmap.org/way/26198206) |
| `ce_bf7607d1b83eab1b` | Wandsbek | – | path | C-IMP-02 | 1.00 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570263,5936563]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.573220/10.061105) · [OSM](https://www.openstreetmap.org/?mlat=53.573220&mlon=10.061105#map=18/53.573220/10.061105) · [Way](https://www.openstreetmap.org/way/759555864) |
| `ce_cda57e4f3b8da40e` | Wandsbek | Tegelweg | road | C-IMP-07 | 1.50 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573361,5940049]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.604124/10.108695) · [OSM](https://www.openstreetmap.org/?mlat=53.604124&mlon=10.108695#map=18/53.604124/10.108695) · [Way](https://www.openstreetmap.org/way/650129016) |
| `ce_d21c146febc9478e` | Wandsbek | Kaskadenpark | road | C-IMP-04 | 1.05 | eine | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575125,5937448]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.580497/10.134718) · [OSM](https://www.openstreetmap.org/?mlat=53.580497&mlon=10.134718#map=18/53.580497/10.134718) · [Way](https://www.openstreetmap.org/way/294968710) |
| `ce_44f558c621a1ef09` | nan | – | road | C-IMP-04 | 1.05 | beide | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[583070,5926378]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.479818/10.251769) · [OSM](https://www.openstreetmap.org/?mlat=53.479818&mlon=10.251769#map=18/53.479818/10.251769) · [Way](https://www.openstreetmap.org/way/388557308) |

Quellen: © OpenStreetMap-Beitragende (ODbL); abgeleitete Daten unter ODbL (docs/licenses.md). Straßenkategorien und Tempo aus data/interim/final.parquet.
