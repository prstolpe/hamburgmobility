# Harmonisierung je Straßenzug – Stufe 5b

Erzeugt: 2026-11-04T20:36:47+00:00 von `pipeline/s05b_harmonise.py`, rules.yaml 0.12.0. Nicht amtlicher Entwurf.

Regel H-STR-01: kurze Läufe unter 200 m (N2) auf einem Straßenzug werden angeglichen; bei 50 gegen 30 gewinnt das niedrigere Tempo. Straßenzug wie N2 (Knoten mit Grad 2 laufen weiter, an Kreuzungen der gegenseitig beste Partner mit höchstens 30° Richtungsänderung).

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| gesperrte Kategorien unverändert | ok | ETW60, ETW_ERF, GOW80, SW |
| Kategorien gültig | ok | 4947 Abschnitte im Arbeitsgebiet |

## Kennzahlen

- Straßenzüge: 1 582; geänderte Abschnitte: 223 (11,5 km) im Arbeitsgebiet, davon 188 (9,7 km) im Bezirk Eimsbüttel.

| Wechsel | Abschnitte | km |
| --- | ---: | ---: |
| ETW30 → GOW30 | 54 | 1,6 |
| ETW30 → GOW50 | 11 | 0,6 |
| GOW30 → ETW30 | 2 | 0,1 |
| GOW50 → ETW30 | 4 | 0,2 |
| GOW50 → GOW30 | 152 | 9,0 |

| Schritt | Abschnitte |
| --- | ---: |
| 1: ETW30-Insel in GOW → GOW | 60 |
| 2: GOW-Insel in ETW30 → ETW30 | 6 |
| 3: GOW50-Insel in GOW30 → GOW30 | 116 |
| 4: GOW30 auf Mindestlänge verlängert | 41 |

km je Kategorie im Arbeitsgebiet vorher (Kaskade) und nachher:

| Kategorie | Kaskade km | harmonisiert km |
| --- | ---: | ---: |
| SW | 28,4 | 28,4 |
| GOW50 | 38,9 | 30,2 |
| GOW30 | 58,4 | 68,8 |
| ETW30 | 437,2 | 435,4 |
| ETW_ERF | 10,6 | 10,6 |

Straßen mit den meisten geänderten km im Bezirk Eimsbüttel:

| Straße | Abschnitte | km |
| --- | ---: | ---: |
| Holsteiner Chaussee | 19 | 1,4 |
| Kieler Straße | 13 | 1,1 |
| Schleswiger Damm | 12 | 0,7 |
| Garstedter Weg | 11 | 0,6 |
| Julius-Vosseler-Straße | 5 | 0,6 |
| Kollaustraße | 8 | 0,5 |
| Lokstedter Steindamm | 9 | 0,5 |
| Pinneberger Chaussee | 6 | 0,5 |
| Oldesloer Straße | 9 | 0,4 |
| Schröderstiftstraße | 4 | 0,3 |
| Volksparkstraße | 3 | 0,2 |
| Binsbarg | 4 | 0,2 |
| Beim Schlump | 9 | 0,2 |
| Nedderfeld | 5 | 0,2 |
| Klosterstern | 7 | 0,2 |
| Elbgaustraße | 2 | 0,2 |
| Grindelallee | 6 | 0,2 |
| Kennedybrücke | 4 | 0,2 |
| Fruchtallee | 6 | 0,2 |
| Swebenweg | 2 | 0,2 |

## Stichprobe: 30 zufällige geänderte Abschnitte im Bezirk Eimsbüttel (Seed 42)

| segment_id | Straße | highway | Kaskade | neu | Schritt | Lauf m | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `seg_03097a65ca0b389f` | Kieler Straße | primary | ETW30 | GOW30 | 1 | 78 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561509,5938524]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591946/9.929311) | [Way](https://www.openstreetmap.org/way/395002917) |
| `seg_088f224d8cae79e6` | Schleswiger Damm | secondary | GOW50 | GOW30 | 3 | 128 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561002,5943317]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.635080/9.922590) | [Way](https://www.openstreetmap.org/way/136485974) |
| `seg_08b35bcbc85ff8a0` | Grindelallee | primary | GOW50 | GOW30 | 3 | 107 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564788,5936302]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571579/9.978375) | [Way](https://www.openstreetmap.org/way/391801520) |
| `seg_08bbdbe2ab4dc4e8` | Rentzelstraße | secondary | GOW50 | GOW30 | 3 | 30 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564713,5935472]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.564124/9.977077) | [Way](https://www.openstreetmap.org/way/51764174) |
| `seg_1e7079b3332dae61` | Hoheluftchaussee | primary | GOW50 | GOW30 | 3 | 11 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564575,5937110]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578866/9.975335) | [Way](https://www.openstreetmap.org/way/391821253) |
| `seg_1eecc3971dd25d6c` | Oldesloer Straße | secondary | ETW30 | GOW30 | 1 | 51 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560233,5943063]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632880/9.910904) | [Way](https://www.openstreetmap.org/way/945786829) |
| `seg_240edc3089b2fc7c` | Kieler Straße | primary | GOW50 | GOW30 | 3 | 113 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562110,5936796]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576343/9.938046) | [Way](https://www.openstreetmap.org/way/733544407) |
| `seg_2699219a31c71094` | Beim Schlump | secondary | GOW50 | GOW30 | 3 | 109 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564760,5936319]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571730/9.977962) | [Way](https://www.openstreetmap.org/way/391801504) |
| `seg_2c005710075de192` | Holsteiner Chaussee | primary | GOW50 | GOW30 | 3 | 73 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560241,5943121]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633406/9.911033) | [Way](https://www.openstreetmap.org/way/945786824) |
| `seg_3d962dec972e1262` | Koppelstraße | primary | GOW50 | GOW30 | 4 | 158 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562427,5938684]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.593268/9.943199) | [Way](https://www.openstreetmap.org/way/692687387) |
| `seg_41c593aab47c4936` | Schleswiger Damm | secondary | GOW50 | GOW30 | 3 | 47 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560529,5944177]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.642861/9.915606) | [Way](https://www.openstreetmap.org/way/763381509) |
| `seg_44b43700761498cc` | Julius-Vosseler-Straße | primary | GOW50 | GOW30 | 3 | 72 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562779,5938918]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.595337/9.948575) | [Way](https://www.openstreetmap.org/way/634124991) |
| `seg_48c9df3c26c2028f` | Lokstedter Steindamm | primary | GOW50 | GOW30 | 3 | 192 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563913,5939153]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.597306/9.965747) | [Way](https://www.openstreetmap.org/way/234008021) |
| `seg_4a0a443c84d46d77` | Oldesloer Straße | primary | ETW30 | GOW50 | 1 | 45 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561616,5944551]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.646099/9.932120) | [Way](https://www.openstreetmap.org/way/370452150) |
| `seg_4d01f5e0c6202387` | Doormannsweg | primary | GOW50 | GOW30 | 3 | 117 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563049,5935781]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567111/9.952010) | [Way](https://www.openstreetmap.org/way/949764833) |
| `seg_5a3a77f617521da4` | – | primary | GOW50 | GOW30 | 3 | 77 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564120,5937919]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.586194/9.968630) | [Way](https://www.openstreetmap.org/way/682409936) |
| `seg_5c161233de14bd93` | Garstedter Weg | secondary | GOW50 | GOW30 | 4 | 105 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563145,5942015]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.623120/9.954731) | [Way](https://www.openstreetmap.org/way/159656520) |
| `seg_911ac8da3f792b4a` | Garstedter Weg | secondary | GOW50 | GOW30 | 3 | 106 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564408,5944476]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645087/9.974327) | [Way](https://www.openstreetmap.org/way/593387516) |
| `seg_91f070700cdeac73` | Schröderstiftstraße | primary | GOW50 | GOW30 | 3 | 123 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564292,5935804]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567160/9.970785) | [Way](https://www.openstreetmap.org/way/3390890) |
| `seg_9af41066e9ac8903` | Holsteiner Chaussee | primary | GOW50 | GOW30 | 3 | 125 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560071,5941704]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620688/9.908200) | [Way](https://www.openstreetmap.org/way/408642296) |
| `seg_ace66a958ae70fa8` | Schleswiger Damm | primary | ETW30 | GOW50 | 1 | 136 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561084,5943189]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.633917/9.923799) | [Way](https://www.openstreetmap.org/way/103948929) |
| `seg_bc2c8bdfba099b09` | Klosterstern | secondary | ETW30 | GOW30 | 3 | 95 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565485,5937408]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.581429/9.989136) | [Way](https://www.openstreetmap.org/way/1370385199) |
| `seg_c761fc50839560f9` | Klosterstern | secondary | GOW50 | GOW30 | 3 | 95 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565497,5937434]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.581665/9.989318) | [Way](https://www.openstreetmap.org/way/1370385200) |
| `seg_cc528c365f7c8717` | Pinneberger Straße | secondary | ETW30 | GOW30 | 1 | 12 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560018,5943027]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632589/9.907654) | [Way](https://www.openstreetmap.org/way/936667680) |
| `seg_cd5d82b10e4a8558` | Pinneberger Chaussee | secondary | GOW50 | GOW30 | 4 | 177 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559582,5940563]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.610492/9.900589) | [Way](https://www.openstreetmap.org/way/1486691847) |
| `seg_d0a300e05e2177ca` | Julius-Vosseler-Straße | primary | GOW50 | GOW30 | 4 | 116 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562999,5939298]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.598721/9.951968) | [Way](https://www.openstreetmap.org/way/105267430) |
| `seg_dd6650a707cf7760` | Nedderfeld | secondary | GOW50 | GOW30 | 3 | 65 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563832,5939849]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603569/9.964668) | [Way](https://www.openstreetmap.org/way/991211002) |
| `seg_ebc5861505e0a97d` | Fruchtallee | primary | GOW50 | GOW30 | 3 | 38 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563771,5936072]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.569637/9.962971) | [Way](https://www.openstreetmap.org/way/664780006) |
| `seg_f3bcf72f9c949ce9` | Kollaustraße | primary | ETW30 | GOW30 | 3 | 94 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563237,5940737]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.611623/9.955857) | [Way](https://www.openstreetmap.org/way/1113387691) |
| `seg_faddc467213f0678` | Binsbarg | primary | GOW50 | GOW30 | 3 | 141 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560832,5938394]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.590855/9.919062) | [Way](https://www.openstreetmap.org/way/1377206755) |

## Lizenz

Abschnitte aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0.
