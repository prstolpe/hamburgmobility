# Bäume und Parkplätze je Soll-Querschnitt (Stufe c09)

Stand 2026-11-17 · design_rules.yaml 0.12.0 · Regeln TP-P-01 bis TP-T-03 · Methode: docs/trees_parking/methode_vorschlag.md

Schätzung, keine Planung. Bäume: „möglicherweise betroffen“, nie „wird gefällt“. Fehlende Daten zählen nie als 0.

## Daten

- Öffentlicher Parkraum (LBV): 203 029 Flächen, davon 5 841 ohne Parkrecht (eingeschränktes Haltverbot), 192 579 einem Abschnitt zugeordnet, 4 609 ohne Abschnitt im Straßenraum.
- Straßenbaumkataster: 229 876 Bäume, 190 567 einem Abschnitt zugeordnet, 39 309 außerhalb des Straßenraums (Parks, Gärten, außerhalb des Arbeitsgebiets).
- OSM-Parkangaben je Seite: 10 343 Abschnitte mit mindestens einer Seite.
- Eichung OSM (TP-P-01 osm_factor): gezählt ÷ rechnerisch auf 4 077 Seiten mit beiden Angaben: Median 0.74 (25.–75. Perzentil 0.56–0.89).

## Abdeckung Parken (Länge der Abschnitte)

| Bezirk | km | amtlich | nur OSM | keine Daten |
| --- | ---: | ---: | ---: | ---: |
| Altona | 620 | 25.2 % | 22.1 % | 52.7 % |
| Bergedorf | 209 | 4.4 % | 10.7 % | 84.9 % |
| Eimsbüttel | 470 | 23.8 % | 28.0 % | 48.2 % |
| Hamburg-Mitte | 881 | 26.7 % | 24.5 % | 48.8 % |
| Hamburg-Nord | 563 | 68.1 % | 11.0 % | 20.9 % |
| Harburg | 465 | 6.1 % | 7.3 % | 86.5 % |
| Wandsbek | 1 030 | 10.5 % | 2.7 % | 86.8 % |
| Hamburg | 4 240 | 24.4 % | 14.9 % | 60.7 % |

## Kennzahlen

| Bezirk | Parkplätze gezählt | davon Straßen vollständig | Ziel (vollständige Straßen) | Bäume | möglicherweise betroffen: Mitte (Spanne) | neu möglich |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Altona | 43 330 | 39 729 | 17 824–18 529 | 20 761 | 2 408 (341–7 305) | 7 422 |
| Bergedorf | 5 208 | 4 647 | 2 948–2 964 | 11 406 | 1 117 (150–4 104) | 2 014 |
| Eimsbüttel | 40 697 | 40 289 | 19 346–19 580 | 22 775 | 2 213 (497–6 185) | 8 422 |
| Hamburg-Mitte | 50 728 | 50 424 | 27 111–28 236 | 35 412 | 4 328 (834–10 982) | 20 982 |
| Hamburg-Nord | 83 358 | 82 990 | 49 566–50 793 | 30 527 | 3 480 (575–9 032) | 12 028 |
| Harburg | 8 344 | 8 213 | 3 385–3 519 | 16 166 | 1 740 (215–5 401) | 5 407 |
| Wandsbek | 23 114 | 22 098 | 13 977–14 382 | 53 520 | 6 620 (1 288–18 172) | 10 673 |
| Hamburg | 254 779 | 248 390 | 134 157–138 004 | 190 567 | 21 904 (3 900–61 181) | 66 947 |

## 30 Zufallsstichproben (Abschnitte mit Parkdaten oder Bäumen)

| Abschnitt | Straße | Bezirk | Parken heute (Quelle) | Ziel | Bäume | betroffen | neu | Orthophoto | Panoramax |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `seg_3a2a90c2dfef7fbb` | Große Bergstraße | Altona | 0 (osm) | 0–0 | 2 | 0–1 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562539,5934071]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.551797/9.943977) |
| `seg_3b54be069f7c9827` | Regerstraße | Altona | 17 (official/official_zero) | 16–16 | 5 | 0–2 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560048,5935696]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.566695/9.906692) |
| `seg_bc157f5060d690bd` | Rissener Busch | Altona | 16 (none/osm) | 0–0 | 0 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[550788,5937094]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.580239/9.767121) |
| `seg_d4c92882e695e988` | Beselerstraße | Altona | 5 (official/official_zero) | 5–5 | 2 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558308,5935485]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.564997/9.880379) |
| `seg_b663bf61bdb68991` | Max-Eichholz-Ring | Bergedorf | – (none) | ––20 | 2 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580711,5929105]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.504692/10.216928) |
| `seg_e986731500b5c763` | Lohbrügger Landstraße | Bergedorf | – (none) | ––9 | 4 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578525,5929258]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.506404/10.184015) |
| `seg_1323ee752475d314` | Eppendorfer Weg | Eimsbüttel | 0 (osm) | 0–0 | 0 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563784,5936942]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.577452/9.963347) |
| `seg_29ef5030242edc51` | Lokstedter Holt | Eimsbüttel | – (none) | ––35 | 1 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562835,5940862]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.612798/9.949812) |
| `seg_9e69be34b496ce38` | Osterstraße | Eimsbüttel | 25 (official) | 25–25 | 21 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563335,5936676]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.575119/9.956514) |
| `seg_fd6f64645f36aeae` | Grindelhof | Eimsbüttel | 1 (official/official_zero) | 1–1 | 10 | 0–5 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564997,5935853]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.567518/9.981442) |
| `seg_111c9a51eded89d4` | Grevenweg | Hamburg-Mitte | 14 (official/official_zero) | 0–0 | 7 | 0–7 | 13 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568949,5934306]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.553111/10.040769) |
| `seg_449d66a3cbfc58fe` | Alter Wall | Hamburg-Mitte | 4 (none/official) | ––6 | 1 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565471,5933830]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.549273/9.988170) |
| `seg_64113d7d5fe8e957` | Raboisen | Hamburg-Mitte | 22 (official) | 22–22 | 0 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566382,5934401]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.554293/10.002045) |
| `seg_ab4dacc5482f35d0` | Otto-Brenner-Straße | Hamburg-Mitte | 0 (osm) | 0–0 | 1 | 0–1 | 1 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566961,5926222]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.480715/10.009037) |
| `seg_b33190a6f8afa16a` | Pagenfelder Straße | Hamburg-Mitte | 43 (official) | 41–41 | 15 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571723,5933941]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.549456/10.082547) |
| `seg_d3a578f069e51a40` | Rantumer Weg | Hamburg-Mitte | – (none) | ––33 | 9 | 0–1 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575472,5933001]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.540482/10.138895) |
| `seg_0e7e77bf6afb3dcd` | Barmbeker Markt | Hamburg-Nord | 0 (osm) | 0–0 | 0 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568902,5937292]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.579949/10.040707) |
| `seg_3f581d8aede78575` | Nirrnheimweg / Dannmeyerstraße | Hamburg-Nord | – (none) | ––119 | 15 | 0–15 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564610,5941019]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.613988/9.976662) |
| `seg_45e969425b9b8a73` | Braamkamp | Hamburg-Nord | 0 (osm) | 0–0 | 0 | 0–0 | 1 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565808,5939703]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.602016/9.994499) |
| `seg_62c2e343beea8a1a` | Anita-Sellenschloh-Ring | Hamburg-Nord | 42 (official) | 42–42 | 2 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568196,5948040]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.676637/10.032407) |
| `seg_6bdccafb8ec72bca` | Kellinghusenstraße | Hamburg-Nord | 0 (osm) | 0–0 | 0 | 0–0 | 1 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565702,5938592]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.592049/9.992666) |
| `seg_6eba4e8b6fdd4b01` | Beim Bergwerk | Harburg | – (none) | ––4 | 5 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559118,5923269]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.455110/9.890306) |
| `seg_c4d44c0af772088b` | Hohe Straße | Harburg | 0 (osm) | 0–0 | 12 | 2–10 | 9 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564418,5922844]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.450670/9.970025) |
| `seg_f5cd4013b56425c0` | Heimfelder Straße | Harburg | 63 (osm) | 63–63 | 36 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562415,5923960]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.460944/9.940084) |
| `seg_0d2cb17653aaca7e` | Kupferdamm | Wandsbek | – (none) | 0–0 | 5 | 0–3 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574250,5939132]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.595760/10.121918) |
| `seg_0d82d97d854c078d` | Kielbarg | Wandsbek | – (none) | ––69 | 10 | 0–4 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573212,5948514]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.680215/10.108434) |
| `seg_67b181bdcb7a8c92` | Hochstraße | Wandsbek | 24 (official) | 20–20 | 3 | 0–2 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571495,5937722]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.583469/10.079970) |
| `seg_7dea188af515cc5e` | Walddörferstraße | Wandsbek | – (none) | ––34 | 14 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573026,5938066]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.586350/10.103172) |
| `seg_9c677f366dd8cd27` | Sedenkamp | Wandsbek | – (none) | 0–0 | 9 | 0–5 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572955,5952116]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.712618/10.105397) |
| `seg_f6848df187676f51` | Brauhausstieg | Wandsbek | 6 (official/official_zero) | 6–6 | 2 | 0–0 | 0 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570248,5936410]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) | [Straße](https://api.panoramax.xyz/#focus=map&map=18/53.571843/10.060842) |

Quellenvermerke: Straßenbaumkataster © FHH, BUKEA; Öffentlicher Parkraum © FHH, Landesbetrieb Verkehr (beide dl-de/by-2.0); © OpenStreetMap-Beitragende (ODbL).
