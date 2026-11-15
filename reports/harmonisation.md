# Harmonisierung je Straßenzug – Stufe 5b

Erzeugt: 2026-11-15T21:35:21+00:00 von `pipeline/s05b_harmonise.py`, rules.yaml 0.24.0. Nicht amtlicher Entwurf.

Regel H-STR-01: kurze Läufe unter 200 m (N2) auf einem Straßenzug werden angeglichen; kurze GOW30-Stücke zwischen GOW50 werden GOW50 (seit 0.24.0). Abschnitte aus C-G50-02 (DTV-Obergrenze) und mit approved override bleiben unverändert. Lückenschluss: ein GOW50-Lauf zwischen zwei GOW30-Läufen wird GOW30, wenn er kürzer als gap_close_m = 500 m ist (F07, StVO-Novelle 2024, Fassung prüfen). Straßenzug wie N2 (Knoten mit Grad 2 laufen weiter, an Kreuzungen der gegenseitig beste Partner mit höchstens 30° Richtungsänderung).

Regel H-PAIR-01 (seit 0.23.0): getrennt gezeichnete Richtungsfahrbahnen derselben Straße bekommen dasselbe Tempo; ist eine Seite GOW30, wird die GOW50-Seite GOW30, außer sie ist gesperrt (C-G50-02, override): dann wird die GOW30-Seite GOW50. Danach gleicht H-STR-01 erneut an.

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| gesperrte Kategorien unverändert | ok | ETW60, ETW_ERF, GOW80, SW |
| Kategorien gültig | ok | 34702 Abschnitte im Arbeitsgebiet |
| Richtungsfahrbahnen gleich (H-PAIR-01) | ok | 2183 Paare, 0 mit GOW30 und GOW50 |

## Kennzahlen

- Straßenzüge: 11 673; geänderte Abschnitte: 585 (31,1 km) im Arbeitsgebiet, davon 585 (31,1 km) in Hamburg (7 Bezirke).

| Wechsel | Abschnitte | km |
| --- | ---: | ---: |
| ETW30 → GOW30 | 50 | 1,8 |
| ETW30 → GOW50 | 202 | 4,5 |
| GOW30 → ETW30 | 10 | 0,6 |
| GOW30 → GOW50 | 77 | 4,1 |
| GOW50 → ETW30 | 23 | 0,8 |
| GOW50 → GOW30 | 223 | 19,4 |

| Bezirk | geänderte Abschnitte | km | Anteil an der Länge im Bezirk |
| --- | ---: | ---: | ---: |
| Altona | 80 | 4,6 | 0,7 % |
| Bergedorf | 17 | 0,9 | 0,4 % |
| Eimsbüttel | 61 | 2,2 | 0,5 % |
| Hamburg-Mitte | 159 | 8,0 | 0,9 % |
| Hamburg-Nord | 102 | 5,2 | 0,9 % |
| Harburg | 57 | 3,6 | 0,8 % |
| Wandsbek | 109 | 6,6 | 0,6 % |

Letzter Schritt je geändertem Abschnitt:

| Schritt | Abschnitte |
| --- | ---: |
| 1: ETW30-Insel in GOW → GOW | 239 |
| 2: GOW-Insel in ETW30 → ETW30 | 33 |
| 3: GOW50-Insel in GOW30 → GOW30 | 192 |
| 4: GOW30-Insel in GOW50 → GOW50 | 81 |
| P: Richtungsfahrbahn angeglichen (H-PAIR-01) | 40 |

km je Kategorie im Arbeitsgebiet vorher (Kaskade) und nachher:

| Kategorie | Kaskade km | harmonisiert km |
| --- | ---: | ---: |
| SW | 189,2 | 189,2 |
| GOW50 | 619,0 | 607,3 |
| GOW30 | 132,0 | 148,6 |
| ETW30 | 3328,8 | 3323,9 |
| ETW_ERF | 118,3 | 118,3 |

### Richtungsfahrbahnen (H-PAIR-01)

- Paare getrennter Richtungsfahrbahnen (GOW, beide oneway, gleicher Name): 1 448 mit 2 335 Abschnitten (234,4 km).
- durch H-PAIR-01 GOW50 → GOW30: 35 Abschnitte (3,1 km)
- durch H-PAIR-01 GOW30 → GOW50: 10 Abschnitte (0,8 km) (Gegenfahrbahn gesperrt, C-G50-02 oder override)
- weitere Abschnitte kann H-STR-01 danach angleichen.
- Abstand der Paare (Median): 12,5 m.

| Straße | Abschnitte | km |
| --- | ---: | ---: |
| Luruper Chaussee | 3 | 0,8 |
| Ebertallee | 3 | 0,5 |
| Überseeallee | 2 | 0,3 |
| Otto-Brenner-Straße | 1 | 0,2 |
| Esplanade | 1 | 0,2 |
| Maldfeldstraße | 5 | 0,2 |
| Willy-Brandt-Straße | 1 | 0,2 |
| Shanghaiallee | 1 | 0,2 |
| Ratsmühlendamm | 4 | 0,2 |
| Schwanenwik | 2 | 0,1 |
| Traute-Lafrenz-Straße | 1 | 0,1 |
| Walderseestraße | 1 | 0,1 |
| Bargteheider Straße | 2 | 0,1 |
| Reiherstieg-Hauptdeich | 2 | 0,1 |
| Reeperbahn | 1 | 0,1 |
| Erdkampsweg | 1 | 0,1 |
| Binnenfeldredder | 1 | 0,1 |
| Millerntorplatz | 1 | 0,1 |
| Harburger Ring | 1 | 0,1 |
| Isfeldstraße | 1 | 0,1 |

Straßen mit den meisten geänderten km in Hamburg (7 Bezirke):

| Bezirk | Straße | Abschnitte | km |
| --- | --- | ---: | ---: |
| Altona | Luruper Chaussee | 6 | 1,0 |
| Altona | Ebertallee | 7 | 0,9 |
| Hamburg-Nord | Schwanenwik | 10 | 0,8 |
| Hamburg-Mitte | Hermannstal | 4 | 0,7 |
| Wandsbek | Berner Chaussee | 3 | 0,6 |
| Wandsbek | Hummelsbütteler Weg | 5 | 0,6 |
| Hamburg-Nord | Steilshooper Straße | 5 | 0,6 |
| Harburg | Maldfeldstraße | 8 | 0,6 |
| Eimsbüttel | Holsteiner Chaussee | 5 | 0,5 |
| Wandsbek | Charlottenburger Straße | 5 | 0,5 |
| Hamburg-Mitte | Reiherstieg-Hauptdeich | 8 | 0,5 |
| Hamburg-Mitte | Otto-Brenner-Straße | 4 | 0,5 |
| Harburg | Milchgrund | 5 | 0,5 |
| Hamburg-Nord | Maienweg | 6 | 0,4 |
| Hamburg-Mitte | Neuenfelder Straße | 4 | 0,4 |
| Bergedorf | Holtenklinker Straße | 3 | 0,4 |
| Wandsbek | Alter Zollweg | 5 | 0,4 |
| Hamburg-Nord | Tangstedter Landstraße | 3 | 0,4 |
| Altona | Rissener Landstraße | 5 | 0,4 |
| Hamburg-Mitte | Hohe-Schaar-Straße | 4 | 0,3 |

## Stichprobe: 30 zufällige geänderte Abschnitte in Hamburg (7 Bezirke), nach Bezirk geschichtet (Seed 42)

| segment_id | Bezirk | Straße | highway | Kaskade | neu | Schritt | Lauf m | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `seg_12e7dd2a953a4851` | Altona | Ebertallee | secondary | GOW50 | GOW30 | 3 | 370 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558990,5936246]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.571763/9.890824) | [Way](https://www.openstreetmap.org/way/317564015) |
| `seg_2fc5da57fe1a3522` | Altona | – | secondary | ETW30 | GOW30 | 1 | 56 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559022,5936447]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573558/9.891346) | [Way](https://www.openstreetmap.org/way/817894931) |
| `seg_6328b049b523d2ee` | Altona | Behringstraße | secondary | ETW30 | GOW50 | 1 | 30 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559718,5934596]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556848/9.901494) | [Way](https://www.openstreetmap.org/way/571803831) |
| `seg_6d37989a404e3931` | Altona | – | secondary | ETW30 | GOW30 | 1 | 56 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559042,5936450]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.573585/9.891646) | [Way](https://www.openstreetmap.org/way/692404088) |
| `seg_4b7a2c044d0fa7b9` | Bergedorf | Kurt-A.-Körber-Chaussee | secondary | GOW30 | ETW30 | 2 | 60 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578798,5927498]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.490542/10.187680) | [Way](https://www.openstreetmap.org/way/153758866) |
| `seg_6924f62d2e1943f7` | Bergedorf | Reinbeker Redder | secondary | ETW30 | GOW50 | 1 | 10 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580208,5930012]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.512924/10.209568) | [Way](https://www.openstreetmap.org/way/686950652) |
| `seg_2b98581e20649c08` | Eimsbüttel | Holsteiner Chaussee | primary | GOW50 | GOW30 | 3 | 450 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560219,5943637]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.638047/9.910810) | [Way](https://www.openstreetmap.org/way/30338973) |
| `seg_ceb0498de58be0bd` | Eimsbüttel | Swebenweg | primary | ETW30 | GOW50 | 1 | 33 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562677,5944940]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.649470/9.948246) | [Way](https://www.openstreetmap.org/way/23300343) |
| `seg_d5ee0785eeceec97` | Eimsbüttel | Kollaustraße | primary | ETW30 | GOW50 | 1 | 43 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563407,5940579]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.610187/9.958392) | [Way](https://www.openstreetmap.org/way/1338619582) |
| `seg_f7f1e277c887bd9e` | Eimsbüttel | Theodor-Heuss-Platz | primary | ETW30 | GOW50 | 1 | 17 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565630,5935094]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.560616/9.990836) | [Way](https://www.openstreetmap.org/way/139084186) |
| `seg_0b404a0a9589a7e3` | Hamburg-Mitte | Ludwig-Erhard-Straße | primary | GOW30 | GOW50 | 4 | 10 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564789,5933836]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.549417/9.977887) | [Way](https://www.openstreetmap.org/way/596230216) |
| `seg_0b43b70d8ad796f7` | Hamburg-Mitte | Hammer Landstraße | secondary | ETW30 | GOW50 | 1 | 10 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570055,5934518]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.554869/10.057501) | [Way](https://www.openstreetmap.org/way/989704750) |
| `seg_29e91aea8d61d6a9` | Hamburg-Mitte | Sievekingdamm | tertiary | GOW50 | GOW30 | 3 | 237 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569213,5934796]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.557481/10.044861) | [Way](https://www.openstreetmap.org/way/74412385) |
| `seg_2b263cc8f1c198d5` | Hamburg-Mitte | Ostfrieslandstraße | tertiary | GOW50 | GOW30 | 3 | 149 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558262,5931424]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.528503/9.878926) | [Way](https://www.openstreetmap.org/way/506273604) |
| `seg_a15941839deafe7a` | Hamburg-Mitte | Rennbahnstraße | primary | ETW30 | GOW50 | 1 | 123 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571843,5934471]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.554207/10.084484) | [Way](https://www.openstreetmap.org/way/609039976) |
| `seg_d464f4935e4ed85a` | Hamburg-Mitte | Otto-Sill-Brücke | secondary | GOW50 | GOW30 | 3 | 68 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565223,5933353]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.545021/9.984325) | [Way](https://www.openstreetmap.org/way/158822885) |
| `seg_f0e43e657f1ad476` | Hamburg-Mitte | Shanghaiallee | secondary | GOW50 | GOW30 | P | – | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566365,5933291]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.544317/10.001546) | [Way](https://www.openstreetmap.org/way/654708419) |
| `seg_1272aad94df7c9a2` | Hamburg-Nord | Schwanenwik | secondary | GOW50 | GOW30 | 3 | 192 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567357,5935550]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.564499/10.017010) | [Way](https://www.openstreetmap.org/way/1427756850) |
| `seg_416a760df825f628` | Hamburg-Nord | Kellinghusenstraße | tertiary | ETW30 | GOW50 | 1 | 94 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565707,5938658]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592642/9.992751) | [Way](https://www.openstreetmap.org/way/82540957) |
| `seg_4854ffdd2acd6081` | Hamburg-Nord | Wellingsbütteler Landstraße | secondary | ETW30 | GOW50 | 1 | 13 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568203,5942408]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.626021/10.031283) | [Way](https://www.openstreetmap.org/way/22817410) |
| `seg_9473ec33c65d3661` | Hamburg-Nord | Jahnbrücke | primary | ETW30 | GOW50 | 1 | 6 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568132,5939534]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.600200/10.029576) | [Way](https://www.openstreetmap.org/way/140430403) |
| `seg_b2e8619696ed22d1` | Hamburg-Nord | Schwanenwik | secondary | GOW50 | GOW30 | 3 | 100 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567305,5935944]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.568043/10.016302) | [Way](https://www.openstreetmap.org/way/40016484) |
| `seg_32b4307dbb64f910` | Harburg | Hannoversche Straße | secondary | GOW30 | GOW50 | 4 | 178 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565760,5923367]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.455209/9.990337) | [Way](https://www.openstreetmap.org/way/485704360) |
| `seg_72ae1a04c5089cd1` | Harburg | Vollhöfner Weiden | secondary | ETW30 | GOW50 | 1 | 11 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559760,5929576]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.511721/9.901177) | [Way](https://www.openstreetmap.org/way/4930326) |
| `seg_aefb1bb8e2a9f08f` | Harburg | Cuxhavener Straße | primary | ETW30 | GOW50 | 1 | 13 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556745,5925154]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.472312/9.854916) | [Way](https://www.openstreetmap.org/way/535203422) |
| `seg_580035287bda8139` | Wandsbek | – | secondary | GOW50 | ETW30 | 2 | 12 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576787,5945229]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.650184/10.161743) | [Way](https://www.openstreetmap.org/way/7996278) |
| `seg_989d06ff33b8cf4c` | Wandsbek | Poppenbütteler Weg | primary | ETW30 | GOW50 | 1 | 9 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570130,5945007]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.649125/10.060994) | [Way](https://www.openstreetmap.org/way/39999259) |
| `seg_b4fb974e33043fd2` | Wandsbek | Alter Zollweg | tertiary | GOW50 | GOW30 | 3 | 265 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574803,5940001]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603488/10.130471) | [Way](https://www.openstreetmap.org/way/379762772) |
| `seg_d286d15e327b9ab9` | Wandsbek | Saseler Chaussee | primary | ETW30 | GOW50 | 1 | 10 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572382,5943940]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.639226/10.094814) | [Way](https://www.openstreetmap.org/way/777580969) |
| `seg_d87998d8fc5153ac` | Wandsbek | Charlottenburger Straße | tertiary | GOW50 | GOW30 | 3 | 484 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575296,5937333]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.579444/10.137277) | [Way](https://www.openstreetmap.org/way/85942768) |

## Prüfliste: GOW50-Inseln ab 500 m zwischen GOW30

15 Läufe mit 115 Abschnitten (16,8 km). H-STR-01 schließt nur Lücken unter gap_close_m = 500 m (StVO § 45 Abs. 9, Fassung prüfen); längere Läufe bleiben GOW50, weil kein Auslöser von C-G30-01/02 greift (Schule/Kita, Publikumsnutzung, Breite). Fachliche Entscheidung je Lauf über `overrides/overrides.csv` (review_status = approved). Karte: `reports/harmonisation_gow50_islands.geojson` (EPSG:4326).

| Straße | Bezirk | Länge m | Abschnitte | Anteil Buslinie | Schule/Kita min. m | Publikumsnutzung max. | Breite p10 min. m | low | Orthophoto | Panoramax |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Lemsahler Landstraße | Wandsbek | 1 934 | 8 | 100 % | 12 | 1,00 | 18,3 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572331,5948735]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.682325/10.095151) |
| Ulzburger Straße | Wandsbek | 1 701 | 5 | 100 % | 10 | 0,06 | 18,2 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571373,5947077]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.667561/10.080271) |
| Volksdorfer Damm | Wandsbek | 1 674 | 8 | 100 % | 9 | 1,00 | 16,7 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575913,5946707]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.663592/10.148888) |
| Sierichstraße | Hamburg-Nord | 1 672 | 12 | 0 % | 116 | 0,69 | 16,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566731,5937298]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580284/10.007932) |
| Schöneberger Straße | Wandsbek | 1 654 | 12 | 100 % | 57 | 0,00 | 19,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576588,5938326]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.588180/10.157036) |
| Bergstedter Chaussee / Saseler Chaussee | Wandsbek | 1 371 | 6 | 100 % | 235 | 1,00 | 17,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573955,5946704]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.663849/10.119256) |
| Ehestorfer Weg | Harburg | 1 279 | 12 | 100 % | 68 | 0,33 | 20,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562357,5923327]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.455262/9.939087) |
| Weusthoffstraße | Harburg | 937 | 8 | 100 % | 50 | 0,44 | 12,3 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563377,5923361]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.455445/9.954462) |
| Traute-Lafrenz-Straße | Hamburg-Nord | 855 | 9 | 36 % | 25 | 1,00 | 25,1 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567028,5939922]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.603828/10.012980) |
| Kalckreuthweg | Altona | 797 | 13 | 100 % | 89 | 0,27 | 19,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558878,5935516]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565209/9.888988) |
| Lohbrügger Landstraße | Bergedorf | 645 | 5 | 100 % | 261 | 0,38 | 17,4 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579433,5928696]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.501212/10.197561) |
| Tangstedter Landstraße | Hamburg-Nord | 631 | 3 | 100 % | 130 | 0,38 | 24,9 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567501,5946244]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.660582/10.021489) |
| Pezolddamm | Wandsbek | 557 | 5 | 100 % | 193 | 0,25 | 17,0 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572834,5941892]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.620761/10.101161) |
| Berner Allee | Wandsbek | 545 | 4 | 100 % | 173 | 0,17 | 17,4 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573997,5942465]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.625744/10.118878) |
| Georg-Wilhelm-Straße | Hamburg-Mitte | 525 | 5 | 98 % | 11 | 0,00 | 23,5 | 0 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565777,5928680]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.502953/9.991713) |

## Lizenz

Abschnitte aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0.
