# Harmonisierung je Straßenzug – Stufe 5b

Erzeugt: 2026-11-08T14:07:03+00:00 von `pipeline/s05b_harmonise.py`, rules.yaml 0.18.0. Nicht amtlicher Entwurf.

Regel H-STR-01: kurze Läufe unter 200 m (N2) auf einem Straßenzug werden angeglichen; bei 50 gegen 30 gewinnt das niedrigere Tempo. Lückenschluss: ein GOW50-Lauf zwischen zwei GOW30-Läufen wird GOW30, wenn er kürzer als gap_close_m = 500 m ist (F07, StVO-Novelle 2024, Fassung prüfen). Straßenzug wie N2 (Knoten mit Grad 2 laufen weiter, an Kreuzungen der gegenseitig beste Partner mit höchstens 30° Richtungsänderung).

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert | ok | 36526 Abschnitte |
| gesperrte Kategorien unverändert | ok | ETW60, ETW_ERF, GOW80, SW |
| Kategorien gültig | ok | 34702 Abschnitte im Arbeitsgebiet |

## Kennzahlen

- Straßenzüge: 11 673; geänderte Abschnitte: 1 630 (109,2 km) im Arbeitsgebiet, davon 1 629 (109,0 km) in Hamburg (7 Bezirke).

| Wechsel | Abschnitte | km |
| --- | ---: | ---: |
| ETW30 → GOW30 | 189 | 4,8 |
| ETW30 → GOW50 | 63 | 1,5 |
| GOW30 → ETW30 | 22 | 1,2 |
| GOW50 → ETW30 | 17 | 0,5 |
| GOW50 → GOW30 | 1 339 | 101,2 |

| Bezirk | geänderte Abschnitte | km | Anteil an der Länge im Bezirk |
| --- | ---: | ---: | ---: |
| Altona | 215 | 13,8 | 2,2 % |
| Bergedorf | 45 | 3,3 | 1,6 % |
| Eimsbüttel | 228 | 13,7 | 2,9 % |
| Hamburg-Mitte | 407 | 24,2 | 2,7 % |
| Hamburg-Nord | 316 | 19,3 | 3,4 % |
| Harburg | 88 | 8,6 | 1,8 % |
| Wandsbek | 330 | 26,2 | 2,5 % |

| Schritt | Abschnitte |
| --- | ---: |
| 1: ETW30-Insel in GOW → GOW | 230 |
| 2: GOW-Insel in ETW30 → ETW30 | 39 |
| 3: GOW50-Insel in GOW30 → GOW30 | 1 243 |
| 4: GOW30 auf Mindestlänge verlängert | 118 |

km je Kategorie im Arbeitsgebiet vorher (Kaskade) und nachher:

| Kategorie | Kaskade km | harmonisiert km |
| --- | ---: | ---: |
| SW | 189,2 | 189,2 |
| GOW50 | 342,5 | 242,4 |
| GOW30 | 408,5 | 513,2 |
| ETW30 | 3328,8 | 3324,3 |
| ETW_ERF | 118,3 | 118,3 |

Straßen mit den meisten geänderten km in Hamburg (7 Bezirke):

| Bezirk | Straße | Abschnitte | km |
| --- | --- | ---: | ---: |
| Hamburg-Mitte | Sievekingsallee | 21 | 2,1 |
| Eimsbüttel | Kieler Straße | 22 | 1,9 |
| Wandsbek | Bramfelder Chaussee | 15 | 1,7 |
| Wandsbek | Friedrich-Ebert-Damm | 13 | 1,6 |
| Eimsbüttel | Holsteiner Chaussee | 19 | 1,5 |
| Harburg | Stader Straße | 7 | 1,5 |
| Wandsbek | Poppenbütteler Weg | 18 | 1,4 |
| Hamburg-Nord | Langenhorner Chaussee | 15 | 1,3 |
| Hamburg-Mitte | Schiffbeker Weg | 18 | 1,2 |
| Hamburg-Nord | Krohnstieg | 6 | 1,2 |
| Altona | Holstenstraße | 19 | 1,2 |
| Altona | Osdorfer Landstraße | 15 | 1,1 |
| Altona | Max-Brauer-Allee | 20 | 1,0 |
| Eimsbüttel | Kollaustraße | 9 | 1,0 |
| Wandsbek | Jenfelder Allee | 11 | 1,0 |
| Wandsbek | Bargteheider Straße | 11 | 0,9 |
| Wandsbek | Volksdorfer Damm | 8 | 0,9 |
| Altona | Osdorfer Weg | 11 | 0,9 |
| Wandsbek | Steilshooper Allee | 9 | 0,9 |
| Wandsbek | Ahrensburger Straße | 9 | 0,9 |

## Stichprobe: 30 zufällige geänderte Abschnitte in Hamburg (7 Bezirke), nach Bezirk geschichtet (Seed 42)

| segment_id | Bezirk | Straße | highway | Kaskade | neu | Schritt | Lauf m | Orthophoto | Panoramax | OSM |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `seg_09ac747c6326f99e` | Altona | Max-Brauer-Allee | secondary | GOW50 | GOW30 | 3 | 135 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562578,5934611]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556648/9.944676) | [Way](https://www.openstreetmap.org/way/113941240) |
| `seg_2b9e72180b1c44e9` | Altona | Elbchaussee | secondary | GOW50 | GOW30 | 3 | 47 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555762,5933941]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.551396/9.841669) | [Way](https://www.openstreetmap.org/way/1280365462) |
| `seg_c8c5ddbbb884ec0f` | Altona | Bahrenfelder Marktplatz | primary | GOW50 | GOW30 | 3 | 150 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559645,5935502]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.564999/9.900571) | [Way](https://www.openstreetmap.org/way/926301896) |
| `seg_eb09a0580163093c` | Altona | Alsenstraße | primary | ETW30 | GOW30 | 1 | 15 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562989,5935636]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.565809/9.951084) | [Way](https://www.openstreetmap.org/way/916910910) |
| `seg_6129b8a5662bc315` | Bergedorf | Sander Damm | secondary | GOW50 | GOW30 | 3 | 51 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579772,5927546]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.490825/10.202379) | [Way](https://www.openstreetmap.org/way/252700799) |
| `seg_6924f62d2e1943f7` | Bergedorf | Reinbeker Redder | secondary | ETW30 | GOW30 | 1 | 10 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580208,5930012]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.512924/10.209568) | [Way](https://www.openstreetmap.org/way/686950652) |
| `seg_1e7079b3332dae61` | Eimsbüttel | Hoheluftchaussee | primary | GOW50 | GOW30 | 3 | 11 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564575,5937110]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.578866/9.975335) | [Way](https://www.openstreetmap.org/way/391821253) |
| `seg_25d1ac9c3e551005` | Eimsbüttel | Volksparkstraße | primary | GOW50 | GOW30 | 3 | 123 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561437,5938559]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592261/9.928222) | [Way](https://www.openstreetmap.org/way/791191448) |
| `seg_347fddc1941984b2` | Eimsbüttel | Volksparkstraße | primary | GOW50 | GOW30 | 3 | 123 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561405,5938553]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.592213/9.927743) | [Way](https://www.openstreetmap.org/way/83804868) |
| `seg_d5b7721136ea860e` | Eimsbüttel | Oldesloer Straße | primary | ETW30 | GOW50 | 1 | 28 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561558,5944531]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.645921/9.931235) | [Way](https://www.openstreetmap.org/way/120922695) |
| `seg_058412a914c37812` | Hamburg-Mitte | Altmannbrücke | secondary | GOW50 | GOW30 | 3 | 41 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566692,5933958]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.550277/10.006624) | [Way](https://www.openstreetmap.org/way/142944218) |
| `seg_160daf939ec4900a` | Hamburg-Mitte | Sievekingplatz | secondary | GOW50 | GOW30 | 3 | 60 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564850,5934519]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.555546/9.978941) | [Way](https://www.openstreetmap.org/way/1369396243) |
| `seg_88c2fbd18d106639` | Hamburg-Mitte | Stephansplatz / Dammtordamm | tertiary | GOW50 | GOW30 | 3 | 127 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565534,5934886]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.558757/9.989350) | [Way](https://www.openstreetmap.org/way/1330228067) |
| `seg_aa6ac067ba9a20d4` | Hamburg-Mitte | Bürgerweide | primary | GOW50 | GOW30 | 3 | 92 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568036,5934624]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.556083/10.027048) | [Way](https://www.openstreetmap.org/way/59411415) |
| `seg_b6ae7c20bcc74d1a` | Hamburg-Mitte | Kornweide | secondary | GOW50 | GOW30 | 3 | 50 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565885,5926287]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.481431/9.992834) | [Way](https://www.openstreetmap.org/way/610010471) |
| `seg_d51840c3677c6e82` | Hamburg-Mitte | Georg-Wilhelm-Straße | tertiary | GOW50 | GOW30 | 3 | 314 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565771,5928535]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.501649/9.991594) | [Way](https://www.openstreetmap.org/way/934938833) |
| `seg_ee7cbc82eab6acad` | Hamburg-Mitte | Otto-Brenner-Straße | secondary | GOW50 | GOW30 | 3 | 182 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567644,5926992]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.487544/10.019492) | [Way](https://www.openstreetmap.org/way/31027413) |
| `seg_0c3028de9006fbc4` | Hamburg-Nord | Brombeerweg | secondary | GOW50 | GOW30 | 3 | 326 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567901,5942596]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.627747/10.026756) | [Way](https://www.openstreetmap.org/way/39999834) |
| `seg_2a7afc0ac0b8097b` | Hamburg-Nord | Barmbeker Straße | primary | GOW50 | GOW30 | 3 | 11 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567470,5937685]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.583667/10.019166) | [Way](https://www.openstreetmap.org/way/1420839503) |
| `seg_5e7d0de9b770ab18` | Hamburg-Nord | Wagnerstraße | secondary | GOW50 | GOW30 | 3 | 8 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568552,5936738]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.575018/10.035303) | [Way](https://www.openstreetmap.org/way/23391196) |
| `seg_6208d7ad522dcb93` | Hamburg-Nord | Barmbeker Straße | primary | GOW50 | GOW30 | 3 | 8 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566820,5938477]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.590869/10.009525) | [Way](https://www.openstreetmap.org/way/972223517) |
| `seg_ccd4bb5b6cce88aa` | Hamburg-Nord | Schottmüllerstraße | primary | GOW50 | GOW30 | 3 | 158 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565090,5938362]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.590053/9.983362) | [Way](https://www.openstreetmap.org/way/44918964) |
| `seg_114b2538cea6eba2` | Harburg | Cuxhavener Straße | primary | GOW50 | GOW30 | 3 | 80 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555221,5925045]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.471496/9.831936) | [Way](https://www.openstreetmap.org/way/534871344) |
| `seg_dcdcf0d3c15619ba` | Harburg | Hannoversche Straße | secondary | GOW50 | GOW30 | 4 | 66 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565916,5924218]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.462832/9.992870) | [Way](https://www.openstreetmap.org/way/598514733) |
| `seg_5331a3f0109b594b` | Wandsbek | Harksheider Straße | secondary | GOW50 | GOW30 | 3 | 290 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571361,5946551]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.662828/10.079966) | [Way](https://www.openstreetmap.org/way/932565350) |
| `seg_58b2c8bd4f68a010` | Wandsbek | Schiffbeker Weg | secondary | GOW50 | GOW30 | 3 | 28 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574338,5935971]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.567336/10.122492) | [Way](https://www.openstreetmap.org/way/204393316) |
| `seg_a4c7307f9796c5e0` | Wandsbek | Wandsbeker Allee | primary | GOW50 | GOW30 | 3 | 248 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570854,5937020]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.577242/10.070133) | [Way](https://www.openstreetmap.org/way/1201599764) |
| `seg_af3ad69fb197f8f8` | Wandsbek | Halenreie | secondary | GOW50 | GOW30 | 3 | 443 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576742,5945452]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.652197/10.161112) | [Way](https://www.openstreetmap.org/way/906888189) |
| `seg_d8db56244faf982c` | Wandsbek | Bramfelder Chaussee | primary | GOW50 | GOW30 | 3 | 102 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570971,5940526]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.608735/10.072696) | [Way](https://www.openstreetmap.org/way/608361271) |
| `seg_e245082c04c120f6` | Wandsbek | – | secondary | ETW30 | GOW30 | 1 | 12 | [DOP](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572971,5937360]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Bilder](https://api.panoramax.xyz/#focus=map&map=18/53.580007/10.102181) | [Way](https://www.openstreetmap.org/way/685851500) |

## Lizenz

Abschnitte aus OpenStreetMap © OpenStreetMap-Beitragende, ODbL 1.0.
