# Harmonisierung je Straßenzug – Stufe 5b

Erzeugt: 2026-11-07T15:03:18+00:00 von `pipeline/s05b_harmonise.py`, rules.yaml 0.16.0. Nicht amtlicher Entwurf.

Regel H-STR-01: kurze Läufe unter 200 m (N2) auf einem Straßenzug werden angeglichen; bei 50 gegen 30 gewinnt das niedrigere Tempo. Straßenzug wie N2 (Knoten mit Grad 2 laufen weiter, an Kreuzungen der gegenseitig beste Partner mit höchstens 30° Richtungsänderung).

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| gesperrte Kategorien unverändert | ok | ETW60, ETW_ERF, GOW80, SW |
| Kategorien gültig | ok | 34702 Abschnitte im Arbeitsgebiet |

## Kennzahlen

- Straßenzüge: 11 673; geänderte Abschnitte: 1 064 (58,1 km) im Arbeitsgebiet, davon 1 064 (58,1 km) in Hamburg (7 Bezirke).

| Wechsel | Abschnitte | km |
| --- | ---: | ---: |
| ETW30 → GOW30 | 208 | 5,0 |
| ETW30 → GOW50 | 51 | 1,2 |
| GOW30 → ETW30 | 24 | 1,5 |
| GOW50 → ETW30 | 17 | 0,7 |
| GOW50 → GOW30 | 764 | 49,7 |

| Bezirk | geänderte Abschnitte | km | Anteil an der Länge im Bezirk |
| --- | ---: | ---: | ---: |
| Altona | 136 | 6,5 | 1,0 % |
| Bergedorf | 26 | 1,4 | 0,7 % |
| Eimsbüttel | 171 | 9,0 | 1,9 % |
| Hamburg-Mitte | 283 | 13,8 | 1,6 % |
| Hamburg-Nord | 178 | 9,0 | 1,6 % |
| Harburg | 62 | 5,4 | 1,2 % |
| Wandsbek | 208 | 13,2 | 1,3 % |

| Schritt | Abschnitte |
| --- | ---: |
| 1: ETW30-Insel in GOW → GOW | 247 |
| 2: GOW-Insel in ETW30 → ETW30 | 41 |
| 3: GOW50-Insel in GOW30 → GOW30 | 627 |
| 4: GOW30 auf Mindestlänge verlängert | 149 |

km je Kategorie im Arbeitsgebiet vorher (Kaskade) und nachher:

| Kategorie | Kaskade km | harmonisiert km |
| --- | ---: | ---: |
| SW | 189,2 | 189,2 |
| GOW50 | 272,3 | 223,2 |
| GOW30 | 474,1 | 527,3 |
| ETW30 | 3333,4 | 3329,4 |
| ETW_ERF | 118,3 | 118,3 |

Straßen mit den meisten geänderten km in Hamburg (7 Bezirke):

| Bezirk | Straße | Abschnitte | km |
| --- | --- | ---: | ---: |
| Eimsbüttel | Holsteiner Chaussee | 18 | 1,3 |
| Eimsbüttel | Kieler Straße | 11 | 1,0 |
| Wandsbek | Bramfelder Chaussee | 10 | 1,0 |
| Harburg | Bremer Straße | 10 | 0,9 |
| Harburg | Stader Straße | 3 | 0,9 |
| Hamburg-Nord | Krohnstieg | 2 | 0,8 |
| Wandsbek | Poppenbütteler Weg | 17 | 0,8 |
| Hamburg-Mitte | Schmidts Breite | 1 | 0,8 |
| Harburg | Hannoversche Straße | 4 | 0,7 |
| Harburg | Cuxhavener Straße | 11 | 0,7 |
| Hamburg-Mitte | Schiffbeker Weg | 12 | 0,7 |
| Bergedorf | Bergedorfer Straße | 11 | 0,7 |
| Hamburg-Mitte | Billstraße | 4 | 0,6 |
| Hamburg-Nord | Schwanenwik | 7 | 0,6 |
| Hamburg-Mitte | Liebigstraße | 1 | 0,6 |
| Hamburg-Nord | Bramfelder Straße | 10 | 0,6 |
| Eimsbüttel | Julius-Vosseler-Straße | 5 | 0,6 |
| Wandsbek | Ölmühlenweg | 6 | 0,6 |
| Altona | Bahrenfelder Chaussee | 11 | 0,6 |
| Eimsbüttel | Schleswiger Damm | 11 | 0,5 |

## Stichprobe: 30 zufällige geänderte Abschnitte in Hamburg (7 Bezirke), nach Bezirk geschichtet (Seed 42)

| segment_id | Bezirk | Straße | highway | Kaskade | neu | Schritt | Lauf m | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `seg_1745be9fb83e2321` | Altona | Isfeldstraße | primary | GOW50 | GOW30 | 3 | 97 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555441,5936430]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573798/9.837265) | [Way](https://www.openstreetmap.org/way/463135740) |
| `seg_31837e4164d831d2` | Altona | St. Pauli Fischmarkt | secondary | GOW50 | GOW30 | 3 | 94 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563159,5933470]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.546322/9.953213) | [Way](https://www.openstreetmap.org/way/609095341) |
| `seg_7cedee7b13f61148` | Altona | Osdorfer Landstraße | primary | GOW50 | GOW30 | 3 | 58 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556416,5936277]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572318/9.851967) | [Way](https://www.openstreetmap.org/way/861135582) |
| `seg_94150d16a4a1459d` | Altona | Osdorfer Landstraße | primary | GOW50 | GOW30 | 3 | 117 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556130,5936327]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572802/9.847651) | [Way](https://www.openstreetmap.org/way/332808667) |
| `seg_33a942ed5864c7f3` | Bergedorf | Bergedorfer Straße | primary | GOW50 | GOW30 | 3 | 117 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579936,5927270]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.488322/10.204771) | [Way](https://www.openstreetmap.org/way/927212619) |
| `seg_4f0a54145522cc84` | Bergedorf | – | primary_link | GOW30 | ETW30 | 2 | 43 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580690,5927027]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.486027/10.216071) | [Way](https://www.openstreetmap.org/way/587834628) |
| `seg_1fa4249a0a4df88a` | Eimsbüttel | Holsteiner Chaussee | primary | ETW30 | GOW30 | 1 | 9 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560036,5944499]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645811/9.908201) | [Way](https://www.openstreetmap.org/way/1010345437) |
| `seg_2699219a31c71094` | Eimsbüttel | Beim Schlump | secondary | GOW50 | GOW30 | 3 | 109 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564760,5936319]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571730/9.977962) | [Way](https://www.openstreetmap.org/way/391801504) |
| `seg_9af41066e9ac8903` | Eimsbüttel | Holsteiner Chaussee | primary | GOW50 | GOW30 | 3 | 125 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560071,5941704]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620688/9.908200) | [Way](https://www.openstreetmap.org/way/408642296) |
| `seg_ceb0498de58be0bd` | Eimsbüttel | Swebenweg | primary | ETW30 | GOW50 | 1 | 33 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562677,5944940]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.649470/9.948246) | [Way](https://www.openstreetmap.org/way/23300343) |
| `seg_ddcb25c524d538d6` | Eimsbüttel | Pinneberger Chaussee | secondary | GOW50 | GOW30 | 4 | 105 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559520,5940614]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.610953/9.899652) | [Way](https://www.openstreetmap.org/way/1345163973) |
| `seg_07563a38926e397e` | Hamburg-Mitte | Süderstraße | secondary | GOW50 | GOW30 | 3 | 51 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568314,5933450]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.545496/10.030996) | [Way](https://www.openstreetmap.org/way/1006424083) |
| `seg_0826aabb1bc35b8e` | Hamburg-Mitte | Sievekingsallee | primary | GOW50 | GOW30 | 3 | 34 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568832,5934994]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.559307/10.039141) | [Way](https://www.openstreetmap.org/way/1116978227) |
| `seg_099ca33334dc8281` | Hamburg-Mitte | Dammtorstraße | tertiary | GOW30 | ETW30 | 2 | 164 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565460,5934662]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556751/9.988186) | [Way](https://www.openstreetmap.org/way/551319332) |
| `seg_282e497f21deb835` | Hamburg-Mitte | Süderstraße | secondary | GOW50 | GOW30 | 4 | 128 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567933,5933196]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.543265/10.025194) | [Way](https://www.openstreetmap.org/way/333891065) |
| `seg_6425b33bac6c49b5` | Hamburg-Mitte | Deichtorplatz | primary | GOW50 | GOW30 | 3 | 64 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566644,5933704]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.547992/10.005848) | [Way](https://www.openstreetmap.org/way/776747678) |
| `seg_6ba7d4d5a5341da5` | Hamburg-Mitte | Adenauerallee | secondary | GOW50 | GOW30 | 3 | 165 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567164,5934218]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.552553/10.013806) | [Way](https://www.openstreetmap.org/way/528961137) |
| `seg_eb2cf3e49356839e` | Hamburg-Mitte | Willy-Brandt-Straße | primary | GOW50 | GOW30 | 3 | 7 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565519,5933619]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.547378/9.988848) | [Way](https://www.openstreetmap.org/way/24438746) |
| `seg_47375d0e43dfd000` | Hamburg-Nord | Im Grünen Grunde | residential | GOW30 | ETW30 | 2 | 113 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568222,5942070]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.622976/10.031485) | [Way](https://www.openstreetmap.org/way/4773045) |
| `seg_98b65280fba76bd9` | Hamburg-Nord | Weidestraße | tertiary | GOW30 | ETW30 | 2 | 40 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568887,5937314]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580153/10.040487) | [Way](https://www.openstreetmap.org/way/68287359) |
| `seg_c0a7cef2ca12b7c0` | Hamburg-Nord | Otto-Wels-Straße | secondary | GOW50 | GOW30 | 3 | 95 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567013,5940049]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.604971/10.012776) | [Way](https://www.openstreetmap.org/way/1181469194) |
| `seg_cb6f27ab7729f111` | Hamburg-Nord | Deelböge | primary | GOW50 | GOW30 | 3 | 86 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565329,5939842]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603324/9.987292) | [Way](https://www.openstreetmap.org/way/136125022) |
| `seg_e515c577d2d26581` | Hamburg-Nord | Lokstedter Weg | primary | GOW50 | GOW30 | 3 | 87 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565175,5938958]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.595397/9.984783) | [Way](https://www.openstreetmap.org/way/584708067) |
| `seg_321dca5b2fd545a3` | Harburg | Bremer Straße | secondary | GOW50 | GOW30 | 3 | 42 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564376,5922861]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.450828/9.969389) | [Way](https://www.openstreetmap.org/way/485653723) |
| `seg_60ada578d5113391` | Harburg | Stader Straße | primary | GOW50 | GOW30 | 4 | 194 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563427,5925030]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.470438/9.955550) | [Way](https://www.openstreetmap.org/way/631243141) |
| `seg_013bef3e1d4dc26b` | Wandsbek | Berner Straße | secondary | GOW50 | GOW30 | 3 | 137 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576380,5941259]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.614566/10.154617) | [Way](https://www.openstreetmap.org/way/222320587) |
| `seg_53202303db842abd` | Wandsbek | Am Luisenhof | secondary | GOW50 | GOW30 | 3 | 16 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573899,5940411]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.607302/10.116905) | [Way](https://www.openstreetmap.org/way/608158356) |
| `seg_b0926a9e38a6197a` | Wandsbek | Bramfelder Chaussee | primary | GOW50 | GOW30 | 4 | 151 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570743,5939724]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.601559/10.069065) | [Way](https://www.openstreetmap.org/way/1109686129) |
| `seg_ef614f1211619eed` | Wandsbek | Ölmühlenweg | secondary | GOW50 | GOW30 | 4 | 81 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572915,5937782]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.583810/10.101433) | [Way](https://www.openstreetmap.org/way/328868492) |
| `seg_ffeee194f0dac2de` | Wandsbek | Steilshooper Allee | secondary | GOW50 | GOW30 | 3 | 112 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570847,5940510]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.608616/10.070813) | [Way](https://www.openstreetmap.org/way/608361259) |

## Lizenz

Abschnitte aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0.
