# Harmonisierung je Straßenzug – Stufe 5b

Erzeugt: 2026-11-07T13:43:19+00:00 von `pipeline/s05b_harmonise.py`, rules.yaml 0.15.0. Nicht amtlicher Entwurf.

Regel H-STR-01: kurze Läufe unter 200 m (N2) auf einem Straßenzug werden angeglichen; bei 50 gegen 30 gewinnt das niedrigere Tempo. Straßenzug wie N2 (Knoten mit Grad 2 laufen weiter, an Kreuzungen der gegenseitig beste Partner mit höchstens 30° Richtungsänderung).

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| gesperrte Kategorien unverändert | ok | ETW60, ETW_ERF, GOW80, SW |
| Kategorien gültig | ok | 34702 Abschnitte im Arbeitsgebiet |

## Kennzahlen

- Straßenzüge: 11 673; geänderte Abschnitte: 1 132 (61,4 km) im Arbeitsgebiet, davon 1 132 (61,4 km) in Hamburg (7 Bezirke).

| Wechsel | Abschnitte | km |
| --- | ---: | ---: |
| ETW30 → GOW30 | 272 | 8,5 |
| ETW30 → GOW50 | 80 | 3,0 |
| GOW30 → ETW30 | 21 | 1,4 |
| GOW50 → ETW30 | 22 | 0,8 |
| GOW50 → GOW30 | 737 | 47,6 |

| Bezirk | geänderte Abschnitte | km | Anteil an der Länge im Bezirk |
| --- | ---: | ---: | ---: |
| Altona | 148 | 7,0 | 1,1 % |
| Bergedorf | 22 | 1,1 | 0,5 % |
| Eimsbüttel | 187 | 9,9 | 2,1 % |
| Hamburg-Mitte | 296 | 14,1 | 1,6 % |
| Hamburg-Nord | 197 | 9,9 | 1,8 % |
| Harburg | 68 | 5,9 | 1,3 % |
| Wandsbek | 214 | 13,5 | 1,3 % |

| Schritt | Abschnitte |
| --- | ---: |
| 1: ETW30-Insel in GOW → GOW | 336 |
| 2: GOW-Insel in ETW30 → ETW30 | 43 |
| 3: GOW50-Insel in GOW30 → GOW30 | 611 |
| 4: GOW30 auf Mindestlänge verlängert | 142 |

km je Kategorie im Arbeitsgebiet vorher (Kaskade) und nachher:

| Kategorie | Kaskade km | harmonisiert km |
| --- | ---: | ---: |
| SW | 189,2 | 189,2 |
| GOW50 | 266,7 | 221,3 |
| GOW30 | 468,4 | 523,1 |
| ETW30 | 3344,8 | 3335,5 |
| ETW_ERF | 118,3 | 118,3 |

Straßen mit den meisten geänderten km in Hamburg (7 Bezirke):

| Bezirk | Straße | Abschnitte | km |
| --- | --- | ---: | ---: |
| Eimsbüttel | Holsteiner Chaussee | 19 | 1,4 |
| Eimsbüttel | Kieler Straße | 13 | 1,1 |
| Wandsbek | Bramfelder Chaussee | 11 | 1,0 |
| Harburg | Stader Straße | 4 | 1,0 |
| Harburg | Bremer Straße | 11 | 1,0 |
| Harburg | Hannoversche Straße | 5 | 0,8 |
| Hamburg-Nord | Krohnstieg | 2 | 0,8 |
| Harburg | Cuxhavener Straße | 12 | 0,8 |
| Wandsbek | Poppenbütteler Weg | 17 | 0,8 |
| Hamburg-Mitte | Schiffbeker Weg | 12 | 0,7 |
| Eimsbüttel | Schleswiger Damm | 12 | 0,7 |
| Hamburg-Nord | Schwanenwik | 7 | 0,6 |
| Hamburg-Mitte | Liebigstraße | 1 | 0,6 |
| Hamburg-Nord | Bramfelder Straße | 10 | 0,6 |
| Eimsbüttel | Julius-Vosseler-Straße | 5 | 0,6 |
| Wandsbek | Ölmühlenweg | 6 | 0,6 |
| Hamburg-Mitte | Billstraße | 3 | 0,6 |
| Altona | Bahrenfelder Chaussee | 11 | 0,6 |
| Eimsbüttel | Garstedter Weg | 8 | 0,5 |
| Wandsbek | Meiendorfer Straße | 8 | 0,5 |

## Stichprobe: 30 zufällige geänderte Abschnitte in Hamburg (7 Bezirke), nach Bezirk geschichtet (Seed 42)

| segment_id | Bezirk | Straße | highway | Kaskade | neu | Schritt | Lauf m | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `seg_132b76c55e4344c9` | Altona | Rugenbarg | primary | ETW30 | GOW30 | 1 | 13 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556790,5937383]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.582222/9.857813) | [Way](https://www.openstreetmap.org/way/603677509) |
| `seg_2f9e3fde2fa34c98` | Altona | Reventlowstraße | tertiary | ETW30 | GOW30 | 1 | 57 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558980,5934512]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556178/9.890346) | [Way](https://www.openstreetmap.org/way/1385167644) |
| `seg_6c33ed0d601ce557` | Altona | Max-Brauer-Allee | secondary | ETW30 | GOW30 | 1 | 13 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562886,5934831]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.558585/9.949361) | [Way](https://www.openstreetmap.org/way/703016288) |
| `seg_7dfe6b1bed83bf05` | Altona | Osdorfer Weg | primary | GOW50 | GOW30 | 3 | 150 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559584,5935521]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565177/9.899655) | [Way](https://www.openstreetmap.org/way/926301895) |
| `seg_33a942ed5864c7f3` | Bergedorf | Bergedorfer Straße | primary | GOW50 | GOW30 | 3 | 117 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579936,5927270]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.488322/10.204771) | [Way](https://www.openstreetmap.org/way/927212619) |
| `seg_4f0a54145522cc84` | Bergedorf | – | primary_link | GOW30 | ETW30 | 2 | 43 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580690,5927027]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.486027/10.216071) | [Way](https://www.openstreetmap.org/way/587834628) |
| `seg_1e7079b3332dae61` | Eimsbüttel | Hoheluftchaussee | primary | GOW50 | GOW30 | 3 | 11 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564575,5937110]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578866/9.975335) | [Way](https://www.openstreetmap.org/way/391821253) |
| `seg_240edc3089b2fc7c` | Eimsbüttel | Kieler Straße | primary | GOW50 | GOW30 | 3 | 113 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562110,5936796]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576343/9.938046) | [Way](https://www.openstreetmap.org/way/733544407) |
| `seg_bc004103ea04f345` | Eimsbüttel | Sportplatzring | primary | ETW30 | GOW30 | 1 | 104 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561534,5938565]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592305/9.929687) | [Way](https://www.openstreetmap.org/way/40163449) |
| `seg_cc528c365f7c8717` | Eimsbüttel | Pinneberger Straße | secondary | ETW30 | GOW30 | 1 | 12 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560018,5943027]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632589/9.907654) | [Way](https://www.openstreetmap.org/way/936667680) |
| `seg_ebc5861505e0a97d` | Eimsbüttel | Fruchtallee | primary | GOW50 | GOW30 | 3 | 38 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563771,5936072]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.569637/9.962971) | [Way](https://www.openstreetmap.org/way/664780006) |
| `seg_07b35bc7e0a1a9f6` | Hamburg-Mitte | Grevenweg | primary | ETW30 | GOW30 | 1 | 15 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568940,5934247]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.552583/10.040613) | [Way](https://www.openstreetmap.org/way/733883670) |
| `seg_0826aabb1bc35b8e` | Hamburg-Mitte | Sievekingsallee | primary | GOW50 | GOW30 | 3 | 34 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568832,5934994]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.559307/10.039141) | [Way](https://www.openstreetmap.org/way/1116978227) |
| `seg_232a4a5752ca14fb` | Hamburg-Mitte | Ludwig-Erhard-Straße | primary | GOW50 | GOW30 | 3 | 36 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565137,5933739]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.548504/9.983110) | [Way](https://www.openstreetmap.org/way/172289065) |
| `seg_5f7fe55d5d5158d1` | Hamburg-Mitte | Kornweide | secondary | ETW30 | GOW30 | 1 | 9 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565858,5926271]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.481293/9.992429) | [Way](https://www.openstreetmap.org/way/606686934) |
| `seg_653246e01e6a00ae` | Hamburg-Mitte | Schiffbeker Weg | secondary | GOW50 | GOW30 | 3 | 56 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573635,5934305]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.552462/10.111476) | [Way](https://www.openstreetmap.org/way/200185710) |
| `seg_acc10aca54daa273` | Hamburg-Mitte | Steintorplatz | tertiary | GOW50 | GOW30 | 3 | 72 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566874,5934182]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.552262/10.009417) | [Way](https://www.openstreetmap.org/way/27805057) |
| `seg_dc64196cb78ab837` | Hamburg-Mitte | Rödingsmarkt | secondary | ETW30 | GOW30 | 1 | 40 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565392,5933766]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.548710/9.986973) | [Way](https://www.openstreetmap.org/way/37071273) |
| `seg_092b53ecb1724b17` | Hamburg-Nord | Sengelmannstraße | service | GOW50 | ETW30 | 2 | 70 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566889,5942078]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.623224/10.011346) | [Way](https://www.openstreetmap.org/way/89126780) |
| `seg_423f00d1121d0573` | Hamburg-Nord | Otto-Wels-Straße | secondary | GOW50 | GOW30 | 3 | 95 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567023,5939967]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.604234/10.012904) | [Way](https://www.openstreetmap.org/way/675487130) |
| `seg_b22cbb15f523ae9c` | Hamburg-Nord | Traute-Lafrenz-Straße | secondary | ETW30 | GOW30 | 1 | 39 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566908,5940568]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.609654/10.011308) | [Way](https://www.openstreetmap.org/way/30652647) |
| `seg_bcad4f91e58feeea` | Hamburg-Nord | Deelböge | primary | GOW50 | GOW30 | 3 | 86 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565364,5939831]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603221/9.987818) | [Way](https://www.openstreetmap.org/way/30385974) |
| `seg_e515c577d2d26581` | Hamburg-Nord | Lokstedter Weg | primary | GOW50 | GOW30 | 3 | 87 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565175,5938958]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.595397/9.984783) | [Way](https://www.openstreetmap.org/way/584708067) |
| `seg_5885615fbe00a272` | Harburg | Bremer Straße | primary | ETW30 | GOW50 | 1 | 11 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561934,5920629]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.431062/9.932184) | [Way](https://www.openstreetmap.org/way/206331867) |
| `seg_c36c3fd7f82340dd` | Harburg | Großmoordamm | primary | GOW50 | GOW30 | 3 | 13 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565931,5923638]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.457619/9.992978) | [Way](https://www.openstreetmap.org/way/598514688) |
| `seg_013bef3e1d4dc26b` | Wandsbek | Berner Straße | secondary | GOW50 | GOW30 | 3 | 137 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576380,5941259]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.614566/10.154617) | [Way](https://www.openstreetmap.org/way/222320587) |
| `seg_53202303db842abd` | Wandsbek | Am Luisenhof | secondary | GOW50 | GOW30 | 3 | 16 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573899,5940411]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.607302/10.116905) | [Way](https://www.openstreetmap.org/way/608158356) |
| `seg_859335b1c862adf0` | Wandsbek | Poppenbüttler Hauptstraße | tertiary | GOW50 | GOW30 | 3 | 162 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571939,5946641]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.663564/10.088733) | [Way](https://www.openstreetmap.org/way/150741163) |
| `seg_afd1b19976ec4b54` | Wandsbek | Holzmühlenstraße | secondary | ETW30 | GOW30 | 1 | 14 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571398,5937869]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.584807/10.078543) | [Way](https://www.openstreetmap.org/way/1295821606) |
| `seg_f5a1e1d118c7c4a2` | Wandsbek | Am Stadtrand | secondary | GOW50 | GOW30 | 3 | 38 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572846,5937889]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.584785/10.100412) | [Way](https://www.openstreetmap.org/way/1487754199) |

## Lizenz

Abschnitte aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0.
