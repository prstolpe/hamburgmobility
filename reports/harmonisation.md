# Harmonisierung je Straßenzug – Stufe 5b

Erzeugt: 2026-11-15T20:08:23+00:00 von `pipeline/s05b_harmonise.py`, rules.yaml 0.23.0. Nicht amtlicher Entwurf.

Regel H-STR-01: kurze Läufe unter 200 m (N2) auf einem Straßenzug werden angeglichen; bei 50 gegen 30 gewinnt das niedrigere Tempo. Lückenschluss: ein GOW50-Lauf zwischen zwei GOW30-Läufen wird GOW30, wenn er kürzer als gap_close_m = 500 m ist (F07, StVO-Novelle 2024, Fassung prüfen). Straßenzug wie N2 (Knoten mit Grad 2 laufen weiter, an Kreuzungen der gegenseitig beste Partner mit höchstens 30° Richtungsänderung).

Regel H-PAIR-01 (seit 0.23.0): getrennt gezeichnete Richtungsfahrbahnen derselben Straße bekommen dasselbe Tempo; ist eine Seite GOW30, wird die GOW50-Seite GOW30. Danach gleicht H-STR-01 erneut an.

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| gesperrte Kategorien unverändert | ok | ETW60, ETW_ERF, GOW80, SW |
| Kategorien gültig | ok | 34702 Abschnitte im Arbeitsgebiet |
| Richtungsfahrbahnen gleich (H-PAIR-01) | ok | 2183 Paare, 0 mit GOW30 und GOW50 |

## Kennzahlen

- Straßenzüge: 11 673; geänderte Abschnitte: 2 067 (151,0 km) im Arbeitsgebiet, davon 2 066 (150,8 km) in Hamburg (7 Bezirke).

| Wechsel | Abschnitte | km |
| --- | ---: | ---: |
| ETW30 → GOW30 | 204 | 5,1 |
| ETW30 → GOW50 | 48 | 1,2 |
| GOW30 → ETW30 | 22 | 1,2 |
| GOW50 → ETW30 | 17 | 0,5 |
| GOW50 → GOW30 | 1 776 | 143,0 |

| Bezirk | geänderte Abschnitte | km | Anteil an der Länge im Bezirk |
| --- | ---: | ---: | ---: |
| Altona | 282 | 21,0 | 3,4 % |
| Bergedorf | 62 | 4,6 | 2,2 % |
| Eimsbüttel | 295 | 18,6 | 4,0 % |
| Hamburg-Mitte | 512 | 34,8 | 4,0 % |
| Hamburg-Nord | 387 | 26,1 | 4,6 % |
| Harburg | 108 | 9,9 | 2,1 % |
| Wandsbek | 420 | 35,7 | 3,5 % |

Letzter Schritt je geändertem Abschnitt:

| Schritt | Abschnitte |
| --- | ---: |
| 1: ETW30-Insel in GOW → GOW | 215 |
| 2: GOW-Insel in ETW30 → ETW30 | 39 |
| 3: GOW50-Insel in GOW30 → GOW30 | 1 369 |
| 4: GOW30 auf Mindestlänge verlängert | 141 |
| P: Richtungsfahrbahn neben GOW30 → GOW30 (H-PAIR-01) | 303 |

km je Kategorie im Arbeitsgebiet vorher (Kaskade) und nachher:

| Kategorie | Kaskade km | harmonisiert km |
| --- | ---: | ---: |
| SW | 189,2 | 189,2 |
| GOW50 | 342,5 | 200,3 |
| GOW30 | 408,5 | 555,3 |
| ETW30 | 3328,8 | 3324,3 |
| ETW_ERF | 118,3 | 118,3 |

### Richtungsfahrbahnen (H-PAIR-01)

- Paare getrennter Richtungsfahrbahnen (GOW, beide oneway, gleicher Name): 1 445 mit 2 331 Abschnitten (234,0 km).
- durch H-PAIR-01 GOW50 → GOW30: 303 Abschnitte (31,2 km); weitere Abschnitte kann H-STR-01 danach angleichen.
- Abstand der Paare (Median): 12,5 m.

| Straße | Abschnitte | km |
| --- | ---: | ---: |
| Poppenbütteler Weg | 14 | 1,8 |
| Friedrich-Ebert-Damm | 6 | 1,4 |
| Luruper Chaussee | 6 | 1,2 |
| Steilshooper Allee | 8 | 1,1 |
| Alsterkrugchaussee | 6 | 1,1 |
| Rugenbarg | 7 | 1,0 |
| Krohnstieg | 4 | 0,8 |
| Sievekingsallee | 3 | 0,7 |
| Eiffestraße | 3 | 0,7 |
| Kurt-Schumacher-Allee | 5 | 0,6 |
| Moorfleeter Straße | 5 | 0,6 |
| Palmaille | 2 | 0,6 |
| Überseering | 6 | 0,5 |
| Deelböge | 5 | 0,5 |
| Stein-Hardenberg-Straße | 2 | 0,5 |
| Amsinckstraße | 2 | 0,5 |
| Bürgerweide | 2 | 0,5 |
| Saarlandstraße | 2 | 0,5 |
| Ebertallee | 3 | 0,5 |
| Reeperbahn | 4 | 0,5 |

Straßen mit den meisten geänderten km in Hamburg (7 Bezirke):

| Bezirk | Straße | Abschnitte | km |
| --- | --- | ---: | ---: |
| Wandsbek | Poppenbütteler Weg | 37 | 3,7 |
| Wandsbek | Friedrich-Ebert-Damm | 21 | 3,2 |
| Hamburg-Mitte | Sievekingsallee | 26 | 2,9 |
| Wandsbek | Bramfelder Chaussee | 24 | 2,2 |
| Wandsbek | Steilshooper Allee | 20 | 2,2 |
| Hamburg-Nord | Krohnstieg | 11 | 2,1 |
| Eimsbüttel | Holsteiner Chaussee | 26 | 2,0 |
| Altona | Rugenbarg | 22 | 1,9 |
| Eimsbüttel | Kieler Straße | 23 | 1,9 |
| Hamburg-Mitte | Schiffbeker Weg | 24 | 1,7 |
| Altona | Osdorfer Landstraße | 17 | 1,5 |
| Altona | Luruper Chaussee | 12 | 1,5 |
| Eimsbüttel | Kollaustraße | 17 | 1,5 |
| Hamburg-Nord | Alsterkrugchaussee | 13 | 1,5 |
| Harburg | Stader Straße | 7 | 1,5 |
| Hamburg-Nord | Langenhorner Chaussee | 17 | 1,5 |
| Hamburg-Mitte | Eiffestraße | 14 | 1,4 |
| Altona | Behringstraße | 20 | 1,4 |
| Altona | Bahrenfelder Chaussee | 14 | 1,3 |
| Eimsbüttel | Binsbarg | 11 | 1,2 |

## Stichprobe: 30 zufällige geänderte Abschnitte in Hamburg (7 Bezirke), nach Bezirk geschichtet (Seed 42)

| segment_id | Bezirk | Straße | highway | Kaskade | neu | Schritt | Lauf m | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `seg_0f9221c7d42eb15b` | Altona | Behringstraße | secondary | GOW50 | GOW30 | P | – | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559709,5934582]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556724/9.901360) | [Way](https://www.openstreetmap.org/way/571803882) |
| `seg_31c07bc7f5252ac1` | Altona | Max-Brauer-Allee | secondary | GOW50 | GOW30 | 3 | 85 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562190,5934260]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.553543/9.938752) | [Way](https://www.openstreetmap.org/way/1380338775) |
| `seg_7bc2c1fdc54e8c2b` | Altona | Osdorfer Landstraße | primary | GOW50 | GOW30 | 3 | 167 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555378,5936458]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.574054/9.836320) | [Way](https://www.openstreetmap.org/way/562055464) |
| `seg_8c6b45d773084b69` | Altona | Alsenplatz | primary | GOW50 | GOW30 | 3 | 164 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563025,5935728]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.566635/9.951640) | [Way](https://www.openstreetmap.org/way/44846266) |
| `seg_2efeb25caa3dc07a` | Bergedorf | Lohbrügger Markt | secondary | GOW50 | GOW30 | 3 | 190 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580082,5928018]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.495025/10.207163) | [Way](https://www.openstreetmap.org/way/836315429) |
| `seg_4b7a2c044d0fa7b9` | Bergedorf | Kurt-A.-Körber-Chaussee | secondary | GOW30 | ETW30 | 2 | 60 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578798,5927498]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.490542/10.187680) | [Way](https://www.openstreetmap.org/way/153758866) |
| `seg_240edc3089b2fc7c` | Eimsbüttel | Kieler Straße | primary | GOW50 | GOW30 | 3 | 113 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562110,5936796]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576343/9.938046) | [Way](https://www.openstreetmap.org/way/733544407) |
| `seg_28c898a73895f770` | Eimsbüttel | Rothenbaumchaussee | secondary | GOW50 | GOW30 | 3 | 66 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565563,5935187]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.561458/9.989851) | [Way](https://www.openstreetmap.org/way/35170417) |
| `seg_b7e8abf865d9264d` | Eimsbüttel | Koppelstraße | primary | GOW50 | GOW30 | 3 | 227 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562312,5938676]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.593214/9.941466) | [Way](https://www.openstreetmap.org/way/500693425) |
| `seg_f540c9143ccf3fb3` | Eimsbüttel | Eimsbütteler Marktplatz | primary | GOW50 | GOW30 | P | – | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562493,5936377]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572528/9.943739) | [Way](https://www.openstreetmap.org/way/143710284) |
| `seg_08e2ef58517bf643` | Hamburg-Mitte | Bürgerweide | primary | GOW50 | GOW30 | 3 | 28 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568815,5935021]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.559557/10.038893) | [Way](https://www.openstreetmap.org/way/1116978247) |
| `seg_09b1a22a9b477859` | Hamburg-Mitte | Holstenglacis | secondary | GOW30 | ETW30 | 2 | 159 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564654,5934677]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556989/9.976012) | [Way](https://www.openstreetmap.org/way/252843129) |
| `seg_0b43b70d8ad796f7` | Hamburg-Mitte | Hammer Landstraße | secondary | ETW30 | GOW30 | 1 | 10 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570055,5934518]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.554869/10.057501) | [Way](https://www.openstreetmap.org/way/989704750) |
| `seg_2b9d8d2ff03cdfa5` | Hamburg-Mitte | Süderstraße | secondary | GOW50 | GOW30 | P | – | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567955,5933188]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.543187/10.025524) | [Way](https://www.openstreetmap.org/way/179060068) |
| `seg_6aac98b65dc12020` | Hamburg-Mitte | Billhorner Röhrendamm | tertiary | GOW50 | ETW30 | 2 | 18 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568549,5932481]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.536758/10.034330) | [Way](https://www.openstreetmap.org/way/53436020) |
| `seg_72035f8f6b0bb062` | Hamburg-Mitte | Lombardsbrücke | primary | GOW50 | GOW30 | 3 | 422 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565883,5934752]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.557512/9.994581) | [Way](https://www.openstreetmap.org/way/186713426) |
| `seg_7ae1c3d519be73f0` | Hamburg-Mitte | Moorfleeter Straße | secondary | GOW50 | GOW30 | 3 | 161 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572908,5932852]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.539511/10.100179) | [Way](https://www.openstreetmap.org/way/61650709) |
| `seg_8db0342ff219cd56` | Hamburg-Nord | Nordschleswiger Straße | primary | GOW50 | GOW30 | 3 | 46 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570739,5937442]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.581052/10.068485) | [Way](https://www.openstreetmap.org/way/917996504) |
| `seg_b54bb4274c240282` | Hamburg-Nord | Barcastraße | residential | GOW50 | GOW30 | 3 | 125 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567357,5935298]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.562227/10.016948) | [Way](https://www.openstreetmap.org/way/189764300) |
| `seg_d687bf7d5e8986d6` | Hamburg-Nord | Borsteler Chaussee | secondary | GOW50 | GOW30 | 3 | 347 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565108,5940005]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.604815/9.983977) | [Way](https://www.openstreetmap.org/way/545868502) |
| `seg_ec04385e4b31874e` | Hamburg-Nord | Nordschleswiger Straße | primary | GOW50 | GOW30 | 3 | 102 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570741,5937418]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580836/10.068506) | [Way](https://www.openstreetmap.org/way/917996497) |
| `seg_f2ad483b78036eae` | Hamburg-Nord | Deelböge | primary | GOW50 | GOW30 | P | – | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565724,5939715]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.602133/9.993235) | [Way](https://www.openstreetmap.org/way/1119352315) |
| `seg_3a34d8bf8961f3b7` | Harburg | Stader Straße | primary | GOW50 | GOW30 | 3 | 59 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562304,5925087]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.471084/9.938635) | [Way](https://www.openstreetmap.org/way/1212378916) |
| `seg_72ae1a04c5089cd1` | Harburg | Vollhöfner Weiden | secondary | ETW30 | GOW50 | 1 | 11 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559760,5929576]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.511721/9.901177) | [Way](https://www.openstreetmap.org/way/4930326) |
| `seg_01689beed31241e6` | Wandsbek | Scharbeutzer Straße | secondary | GOW50 | GOW30 | 3 | 70 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576139,5939705]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600639/10.150581) | [Way](https://www.openstreetmap.org/way/18164415) |
| `seg_549a8c14f24ee29c` | Wandsbek | Robert-Schuman-Brücke | primary | GOW50 | GOW30 | 3 | 32 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570889,5936544]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572961/10.070551) | [Way](https://www.openstreetmap.org/way/42988655) |
| `seg_b34ce9f1410b7699` | Wandsbek | Bramfelder Chaussee | primary | GOW50 | GOW30 | 3 | 44 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571794,5942582]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.627108/10.085610) | [Way](https://www.openstreetmap.org/way/1099838115) |
| `seg_ee7beba81e37e807` | Wandsbek | Harksheider Straße | secondary | GOW50 | GOW30 | 3 | 290 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571426,5946501]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.662373/10.080935) | [Way](https://www.openstreetmap.org/way/932565350) |
| `seg_fab5929161c1ead3` | Wandsbek | Jüthornstraße | secondary | GOW50 | GOW30 | 3 | 478 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572104,5936100]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.568810/10.088786) | [Way](https://www.openstreetmap.org/way/159003499) |
| `seg_fce407e550813b18` | Wandsbek | Ahrensburger Straße | primary | GOW50 | GOW30 | 3 | 71 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573221,5937455]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580832/10.105971) | [Way](https://www.openstreetmap.org/way/685851515) |

## Prüfliste: GOW50-Inseln ab 500 m zwischen GOW30

63 Läufe mit 351 Abschnitten (59,1 km). H-STR-01 schließt nur Lücken unter gap_close_m = 500 m (StVO § 45 Abs. 9, Fassung prüfen); längere Läufe bleiben GOW50, weil kein Auslöser von C-G30-01/02 greift (Schule/Kita, Publikumsnutzung, Breite). Fachliche Entscheidung je Lauf über `overrides/overrides.csv` (review_status = approved). Karte: `reports/harmonisation_gow50_islands.geojson` (EPSG:4326).

| Straße | Bezirk | Länge m | Abschnitte | Anteil Buslinie | Schule/Kita min. m | Publikumsnutzung max. | Breite p10 min. m | low | Orthophoto | Panoramax |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Swebenweg | Eimsbüttel | 3 450 | 14 | 34 % | 383 | 0,00 | 20,1 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562625,5944932]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.649397/9.947457) |
| Alte Landstraße | Wandsbek | 3 445 | 17 | 100 % | 135 | 0,09 | 23,8 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570477,5944394]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.643563/10.066100) |
| Ohlsdorfer Straße | Hamburg-Nord | 2 400 | 21 | 95 % | 72 | 0,25 | 20,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567605,5939564]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600543/10.021621) |
| Andreas-Meyer-Straße | Hamburg-Mitte | 1 928 | 2 | 100 % | 1568 | 0,25 | 26,1 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571402,5930539]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.518925/10.076916) |
| Schöneberger Straße | Wandsbek | 1 654 | 12 | 100 % | 57 | 0,00 | 19,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576588,5938326]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.588180/10.157036) |
| Kornweide | Hamburg-Mitte | 1 596 | 11 | 100 % | 307 | 0,00 | 20,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566803,5926225]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.480764/10.006650) |
| Bergedorfer Straße | Bergedorf | 1 455 | 10 | 100 % | 170 | 0,33 | 25,1 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577987,5929565]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.509242/10.175973) |
| Holstenkamp | Altona | 1 409 | 7 | 35 % | 152 | 0,00 | 20,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561523,5936391]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.572774/9.929096) |
| Ehestorfer Weg | Harburg | 1 279 | 12 | 100 % | 68 | 0,33 | 20,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562357,5923327]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.455262/9.939087) |
| Farnhornweg | Altona | 1 248 | 5 | 100 % | 227 | 0,04 | 21,5 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559236,5938613]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.593006/9.894990) |
| Höltigbaum | Wandsbek | 1 228 | 5 | 0 % | 108 | 0,00 | 23,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577178,5941293]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.614755/10.166678) |
| Steilshooper Allee / Am Luisenhof | Wandsbek | 1 181 | 1 | 100 % | 69 | 0,00 | 18,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572646,5940228]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.605833/10.097931) |
| Farmsener Weg | Wandsbek | 1 176 | 9 | 100 % | 75 | 0,00 | 20,4 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573055,5943234]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.632792/10.104825) |
| Stein-Hardenberg-Straße | Wandsbek | 1 059 | 6 | 100 % | 123 | 0,00 | 23,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574803,5938655]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.591395/10.130146) |
| Hohenzollernring / Elbchaussee | Altona | 1 057 | 2 | 0 % | 70 | 0,20 | 17,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560542,5933413]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.546117/9.913704) |
| Poppenbütteler Berg | Wandsbek | 1 053 | 3 | 100 % | 61 | 0,00 | 18,2 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571618,5947290]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.669437/10.084025) |
| Gehlengraben | Hamburg-Nord | 1 048 | 5 | 100 % | 145 | 0,20 | 28,3 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567855,5945077]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.650051/10.026601) |
| Reinbeker Redder | Bergedorf | 1 027 | 4 | 100 % | 225 | 0,00 | 20,1 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579134,5929870]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.511812/10.193353) |
| Mengestraße | Hamburg-Mitte | 993 | 10 | 59 % | 238 | 0,00 | 17,6 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565559,5928429]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.500727/9.988364) |
| Bergedorfer Straße | Bergedorf | 983 | 6 | 100 % | 205 | 0,14 | 23,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579328,5927895]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.494026/10.195770) |
| Holsteiner Chaussee | Eimsbüttel | 922 | 6 | 77 % | 91 | 0,33 | 19,2 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560138,5942201]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.625151/9.909313) |
| Winsener Straße | Harburg | 912 | 7 | 100 % | 305 | 0,25 | 24,7 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565369,5920824]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.432396/9.983930) |
| Gehlengraben | Hamburg-Nord | 902 | 2 | 100 % | 155 | 0,00 | 28,3 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567923,5945090]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.650156/10.027624) |
| Harksheider Straße | Wandsbek | 881 | 7 | 100 % | 61 | 0,33 | 19,2 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570438,5947160]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.668428/10.066137) |
| Bremer Straße | Harburg | 827 | 5 | 100 % | 92 | 0,00 | 21,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563146,5921986]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.443112/9.950701) |
| Kalckreuthweg | Altona | 797 | 13 | 100 % | 89 | 0,27 | 19,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558878,5935516]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565209/9.888988) |
| Sierichstraße | Hamburg-Nord | 768 | 5 | 0 % | 316 | 0,25 | 17,2 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566917,5936886]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.576559/10.010645) |
| Holsteiner Chaussee | Eimsbüttel | 761 | 4 | 100 % | 120 | 0,20 | 18,4 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560116,5944122]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.642420/9.909350) |
| Holtenklinker Straße / Rothenhauschaussee | Bergedorf | 755 | 2 | 100 % | 280 | 0,10 | 19,2 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[581994,5926229]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.478649/10.235516) |
| Marmstorfer Weg | Harburg | 747 | 7 | 100 % | 57 | 0,11 | 18,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564288,5921714]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.440532/9.967838) |
| August-Krogmann-Straße | Wandsbek | 742 | 9 | 100 % | 142 | 0,29 | 20,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573577,5941858]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620352/10.112388) |
| Kieler Straße | Eimsbüttel | 737 | 9 | 100 % | 68 | 0,00 | 24,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560960,5939119]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.597350/9.921134) |
| Veddeler Damm | Hamburg-Mitte | 730 | 2 | 0 % | 1108 | 0,00 | 21,8 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565809,5931218]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.525757/9.992724) |
| Pinneberger Chaussee | Eimsbüttel | 724 | 3 | 100 % | 78 | 0,20 | 19,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559165,5940962]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.614119/9.894356) |
| Bergstedter Chaussee / Saseler Chaussee | Wandsbek | 715 | 1 | 100 % | 448 | 0,05 | 18,7 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573792,5946420]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.661314/10.116714) |
| Lemsahler Landstraße | Wandsbek | 699 | 3 | 100 % | 152 | 0,00 | 22,1 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572331,5948799]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.682897/10.095173) |
| Berner Heerweg | Wandsbek | 695 | 3 | 100 % | 88 | 0,00 | 23,3 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574361,5941056]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.613027/10.124042) |
| Schiffbeker Weg | Hamburg-Mitte | 695 | 7 | 100 % | 100 | 0,08 | 24,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574013,5935055]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.559155/10.117359) |
| Cuxhavener Straße | Harburg | 665 | 2 | 100 % | 88 | 0,09 | 21,2 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557844,5925106]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.471762/9.871462) |
| Osdorfer Landstraße | Altona | 652 | 5 | 100 % | 73 | 0,20 | 23,8 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557607,5936162]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571158/9.869928) |
| Bremer Straße | Harburg | 643 | 4 | 100 % | 223 | 0,33 | 23,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563928,5922593]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.448476/9.962595) |
| Tangstedter Landstraße | Hamburg-Nord | 631 | 3 | 100 % | 130 | 0,38 | 24,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567501,5946244]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.660582/10.021489) |
| Luruper Hauptstraße | Altona | 617 | 4 | 100 % | 154 | 0,33 | 21,5 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557464,5938844]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.595274/9.868260) |
| Friedrich-Ebert-Straße / Frohmestraße | Eimsbüttel | 614 | 4 | 100 % | 157 | 0,17 | 30,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561879,5942422]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.626936/9.935675) |
| Julius-Vosseler-Straße | Eimsbüttel | 611 | 3 | 100 % | 126 | 0,00 | 27,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562902,5939156]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.597461/9.950478) |
| Saarlandstraße | Hamburg-Nord | 606 | 5 | 0 % | 87 | 0,00 | 32,7 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568307,5938793]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.593516/10.032056) |
| Saarlandstraße | Hamburg-Nord | 605 | 3 | 0 % | 75 | 0,00 | 31,2 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568319,5938794]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.593527/10.032235) |
| Ehestorfer Heuweg | Harburg | 594 | 6 | 100 % | 117 | 0,00 | 18,7 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559124,5924420]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.465457/9.890622) |
| Weusthoffstraße | Harburg | 586 | 4 | 100 % | 61 | 0,25 | 20,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563439,5923522]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.456886/9.955429) |
| Alsterkrugchaussee | Hamburg-Nord | 579 | 2 | 100 % | 458 | 0,00 | 36,5 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565793,5940534]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.609486/9.994439) |
| Osdorfer Landstraße | Altona | 569 | 4 | 0 % | 53 | 0,17 | 25,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554851,5936616]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575531/9.828395) |
| Tonndorfer Hauptstraße | Wandsbek | 559 | 4 | 100 % | 70 | 0,21 | 19,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574874,5938366]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.588783/10.131151) |
| Lesserstraße | Wandsbek | 556 | 5 | 100 % | 224 | 0,20 | 18,8 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571352,5938424]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.589797/10.077963) |
| Bei der Wollkämmerei | Hamburg-Mitte | 546 | 4 | 0 % | 248 | 0,00 | 18,4 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564922,5929082]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.506675/9.978906) |
| Poppenbütteler Weg | Wandsbek | 546 | 3 | 0 % | 81 | 0,00 | 24,5 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570380,5945126]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.650162/10.064799) |
| Berner Brücke | Wandsbek | 542 | 6 | 100 % | 50 | 0,11 | 24,3 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575672,5942615]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.626851/10.144232) |
| Osdorfer Landstraße | Altona | 540 | 3 | 100 % | 92 | 0,38 | 23,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557661,5936165]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571182/9.870737) |
| Barnerstraße | Altona | 534 | 2 | 100 % | 127 | 0,29 | 19,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561736,5934657]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.557160/9.931972) |
| Garstedter Weg | Eimsbüttel | 532 | 3 | 100 % | 154 | 0,00 | 30,8 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563101,5941691]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620215/9.953991) |
| Langenhorner Chaussee | Hamburg-Nord | 525 | 3 | 100 % | 182 | 0,38 | 21,2 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567107,5943620]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.637055/10.014972) |
| Steilshooper Allee | Wandsbek | 522 | 4 | 100 % | 73 | 0,00 | 27,1 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571297,5940514]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.608588/10.077623) |
| Krohnstieg | Hamburg-Nord | 515 | 7 | 100 % | 166 | 0,15 | 18,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566550,5944872]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.648374/10.006817) |
| Alsterkrugchaussee | Hamburg-Nord | 509 | 1 | 100 % | 471 | 0,00 | 36,4 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565762,5940514]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.609309/9.993975) |

## Lizenz

Abschnitte aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0.
