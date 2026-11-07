# Harmonisierung je Straßenzug – Stufe 5b

Erzeugt: 2026-11-07T12:52:39+00:00 von `pipeline/s05b_harmonise.py`, rules.yaml 0.14.0. Nicht amtlicher Entwurf.

Regel H-STR-01: kurze Läufe unter 200 m (N2) auf einem Straßenzug werden angeglichen; bei 50 gegen 30 gewinnt das niedrigere Tempo. Straßenzug wie N2 (Knoten mit Grad 2 laufen weiter, an Kreuzungen der gegenseitig beste Partner mit höchstens 30° Richtungsänderung).

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| gesperrte Kategorien unverändert | ok | ETW60, ETW_ERF, GOW80, SW |
| Kategorien gültig | ok | 34702 Abschnitte im Arbeitsgebiet |

## Kennzahlen

- Straßenzüge: 11 673; geänderte Abschnitte: 855 (48,9 km) im Arbeitsgebiet, davon 855 (48,9 km) in Hamburg (7 Bezirke).

| Wechsel | Abschnitte | km |
| --- | ---: | ---: |
| ETW30 → GOW30 | 75 | 2,6 |
| ETW30 → GOW50 | 277 | 9,0 |
| GOW30 → ETW30 | 13 | 1,0 |
| GOW50 → ETW30 | 30 | 1,3 |
| GOW50 → GOW30 | 460 | 35,1 |

| Bezirk | geänderte Abschnitte | km | Anteil an der Länge im Bezirk |
| --- | ---: | ---: | ---: |
| Altona | 127 | 6,7 | 1,1 % |
| Bergedorf | 13 | 0,6 | 0,3 % |
| Eimsbüttel | 137 | 8,5 | 1,8 % |
| Hamburg-Mitte | 216 | 12,1 | 1,4 % |
| Hamburg-Nord | 165 | 8,7 | 1,5 % |
| Harburg | 56 | 4,0 | 0,9 % |
| Wandsbek | 141 | 8,3 | 0,8 % |

| Schritt | Abschnitte |
| --- | ---: |
| 1: ETW30-Insel in GOW → GOW | 348 |
| 2: GOW-Insel in ETW30 → ETW30 | 43 |
| 3: GOW50-Insel in GOW30 → GOW30 | 237 |
| 4: GOW30 auf Mindestlänge verlängert | 227 |

km je Kategorie im Arbeitsgebiet vorher (Kaskade) und nachher:

| Kategorie | Kaskade km | harmonisiert km |
| --- | ---: | ---: |
| SW | 189,2 | 189,2 |
| GOW50 | 616,1 | 588,6 |
| GOW30 | 119,0 | 155,7 |
| ETW30 | 3344,8 | 3335,5 |
| ETW_ERF | 118,3 | 118,3 |

Straßen mit den meisten geänderten km in Hamburg (7 Bezirke):

| Bezirk | Straße | Abschnitte | km |
| --- | --- | ---: | ---: |
| Eimsbüttel | Holsteiner Chaussee | 10 | 0,9 |
| Eimsbüttel | Doormannsweg | 9 | 0,9 |
| Harburg | Hannoversche Straße | 5 | 0,8 |
| Eimsbüttel | Grindelallee | 10 | 0,8 |
| Hamburg-Mitte | Borgfelder Straße | 8 | 0,7 |
| Harburg | Winsener Straße | 9 | 0,7 |
| Eimsbüttel | Oldesloer Straße | 13 | 0,6 |
| Hamburg-Mitte | Liebigstraße | 1 | 0,6 |
| Wandsbek | Jenfelder Allee | 4 | 0,6 |
| Hamburg-Mitte | Billstraße | 3 | 0,6 |
| Altona | Osdorfer Landstraße | 8 | 0,6 |
| Hamburg-Nord | Überseering | 7 | 0,6 |
| Hamburg-Nord | Fuhlsbüttler Straße | 5 | 0,5 |
| Hamburg-Nord | Nordschleswiger Straße | 10 | 0,5 |
| Wandsbek | Poppenbütteler Weg | 11 | 0,5 |
| Harburg | Ehestorfer Heuweg | 2 | 0,5 |
| Eimsbüttel | Kieler Straße | 7 | 0,5 |
| Hamburg-Mitte | Reeperbahn | 2 | 0,5 |
| Eimsbüttel | Kollaustraße | 6 | 0,5 |
| Hamburg-Nord | Krausestraße | 3 | 0,4 |

## Stichprobe: 30 zufällige geänderte Abschnitte in Hamburg (7 Bezirke), nach Bezirk geschichtet (Seed 42)

| segment_id | Bezirk | Straße | highway | Kaskade | neu | Schritt | Lauf m | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `seg_0a44432b010a0a9f` | Altona | Max-Brauer-Allee | secondary | GOW50 | GOW30 | 3 | 32 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562901,5934855]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.558799/9.949600) | [Way](https://www.openstreetmap.org/way/31767945) |
| `seg_235bfd2912f0c27f` | Altona | Rugenbarg | primary | ETW30 | GOW50 | 1 | 10 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557992,5938087]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.588415/9.876095) | [Way](https://www.openstreetmap.org/way/756339559) |
| `seg_b0b253b73932c7d0` | Altona | Hohenzollernring | secondary | ETW30 | GOW50 | 1 | 12 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560813,5933974]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.551130/9.917904) | [Way](https://www.openstreetmap.org/way/30472558) |
| `seg_c91f9bd1062eb992` | Altona | Osdorfer Weg | primary | GOW50 | GOW30 | 4 | 10 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559366,5935578]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565711/9.896375) | [Way](https://www.openstreetmap.org/way/223336660) |
| `seg_4f0a54145522cc84` | Bergedorf | – | primary_link | GOW50 | ETW30 | 2 | 43 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580690,5927027]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.486027/10.216071) | [Way](https://www.openstreetmap.org/way/587834628) |
| `seg_33cb6ed3e7ffbd56` | Eimsbüttel | Doormannsweg | primary | GOW50 | GOW30 | 3 | 93 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563308,5936150]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.570394/9.955995) | [Way](https://www.openstreetmap.org/way/143710276) |
| `seg_3ac1a8795499671f` | Eimsbüttel | Oldesloer Straße | secondary | GOW50 | GOW30 | 3 | 194 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561038,5943677]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.638312/9.923200) | [Way](https://www.openstreetmap.org/way/1150429542) |
| `seg_4a0a443c84d46d77` | Eimsbüttel | Oldesloer Straße | primary | ETW30 | GOW50 | 1 | 45 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561616,5944551]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.646099/9.932120) | [Way](https://www.openstreetmap.org/way/370452150) |
| `seg_7676faba52fb8710` | Eimsbüttel | Doormannsweg | primary | GOW50 | GOW30 | 4 | 140 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563322,5936145]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.570345/9.956207) | [Way](https://www.openstreetmap.org/way/44365496) |
| `seg_7c5eb304e028c4a4` | Eimsbüttel | Rothenbaumchaussee | secondary | ETW30 | GOW30 | 1 | 6 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565563,5935179]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.561393/9.989851) | [Way](https://www.openstreetmap.org/way/35170185) |
| `seg_0649fc1a88b1bcb3` | Hamburg-Mitte | Wöhlerstraße | primary | ETW30 | GOW50 | 1 | 132 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571771,5932449]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.536040/10.082919) | [Way](https://www.openstreetmap.org/way/677241308) |
| `seg_07b35bc7e0a1a9f6` | Hamburg-Mitte | Grevenweg | primary | ETW30 | GOW50 | 1 | 15 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568940,5934247]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.552583/10.040613) | [Way](https://www.openstreetmap.org/way/733883670) |
| `seg_1adcd4aeca359496` | Hamburg-Mitte | Sievekingsallee | secondary | ETW30 | GOW30 | 1 | 136 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571807,5934527]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.554708/10.083939) | [Way](https://www.openstreetmap.org/way/30153833) |
| `seg_45bfeb0f646bd6a3` | Hamburg-Mitte | Domstraße | secondary | GOW50 | GOW30 | 3 | 49 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566020,5933858]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.549462/9.996465) | [Way](https://www.openstreetmap.org/way/372643598) |
| `seg_48d876a6f6676166` | Hamburg-Mitte | Klosterwall | primary | ETW30 | GOW50 | 1 | 24 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566670,5933745]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.548364/10.006243) | [Way](https://www.openstreetmap.org/way/1420822092) |
| `seg_7fda4452d37b8c74` | Hamburg-Mitte | Neßdeich | tertiary | GOW50 | GOW30 | 3 | 180 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557094,5932061]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.534354/9.861437) | [Way](https://www.openstreetmap.org/way/582276139) |
| `seg_a8034ac38f4b568f` | Hamburg-Mitte | Horner Rampe | primary | ETW30 | GOW50 | 1 | 48 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571771,5933414]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.544715/10.083151) | [Way](https://www.openstreetmap.org/way/886644231) |
| `seg_094cf78ce3b0aecb` | Hamburg-Nord | Krausestraße | secondary | GOW50 | GOW30 | 4 | 199 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570078,5937028]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.577423/10.058413) | [Way](https://www.openstreetmap.org/way/4255855) |
| `seg_57ee56ddefcd62c3` | Hamburg-Nord | Fuhlsbüttler Straße | secondary | GOW50 | GOW30 | 3 | 61 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569121,5938608]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591747/10.044310) | [Way](https://www.openstreetmap.org/way/147233375) |
| `seg_c4744bc5e39e230d` | Hamburg-Nord | Tarpenbekstraße | primary | GOW50 | GOW30 | 4 | 119 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565105,5938544]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591689/9.983634) | [Way](https://www.openstreetmap.org/way/612753194) |
| `seg_d1c9abc0a1d76831` | Hamburg-Nord | Ludolfstraße | primary | GOW50 | GOW30 | 3 | 48 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565667,5938667]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592726/9.992149) | [Way](https://www.openstreetmap.org/way/1131525508) |
| `seg_e51c32ae361357e3` | Hamburg-Nord | Winterhuder Marktplatz | primary | GOW50 | GOW30 | 3 | 38 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566188,5938841]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.594225/10.000050) | [Way](https://www.openstreetmap.org/way/132260177) |
| `seg_c67b7838317aa5c5` | Harburg | Süderelbebogen | secondary | GOW50 | GOW30 | 3 | 69 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556845,5925283]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.473461/9.856448) | [Way](https://www.openstreetmap.org/way/682835817) |
| `seg_c899deec13648885` | Harburg | Winsener Straße | secondary | GOW50 | GOW30 | 4 | 8 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565581,5922842]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.450507/9.987531) | [Way](https://www.openstreetmap.org/way/607692926) |
| `seg_cac6c87a38110da8` | Harburg | Hannoversche Straße | secondary | ETW30 | GOW50 | 1 | 105 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565754,5923755]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.458698/9.990337) | [Way](https://www.openstreetmap.org/way/1205244082) |
| `seg_71cb379b4b6bd385` | Wandsbek | Rahlstedter Straße | secondary | GOW50 | GOW30 | 4 | 9 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576455,5939574]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.599410/10.155324) | [Way](https://www.openstreetmap.org/way/28487979) |
| `seg_96ae5a9f9616ec3c` | Wandsbek | Sonnenweg | secondary | GOW50 | GOW30 | 4 | 156 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574442,5938175]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.587131/10.124581) | [Way](https://www.openstreetmap.org/way/443791881) |
| `seg_c96dad22b10f2603` | Wandsbek | Rahlstedter Weg | secondary | GOW50 | GOW30 | 3 | 168 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574110,5940287]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.606158/10.120068) | [Way](https://www.openstreetmap.org/way/22744329) |
| `seg_d33dd4ec2b19862b` | Wandsbek | Poppenbütteler Weg | primary | ETW30 | GOW50 | 1 | 13 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571201,5945466]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.653100/10.077300) | [Way](https://www.openstreetmap.org/way/27071216) |
| `seg_fe30fdf44c6090c8` | Wandsbek | Schöneberger Straße | tertiary | ETW30 | GOW30 | 1 | 42 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575796,5937855]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.584057/10.144962) | [Way](https://www.openstreetmap.org/way/1358315345) |

## Lizenz

Abschnitte aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0.
