# Ist-Führung und Parallelroute je Abschnitt (Stufe c03b)

Erzeugt 2026-11-15T21:43:37+00:00 mit pipeline/c03b_ist_facility.py · rules.yaml 0.24.0 · cycling_rules.yaml 0.12.0 · nicht amtlicher Entwurf. Regeln S-FEAT-13 und S-FEAT-11 (Review 2026-11 F26/E9, F21), source_type assumption, status draft.

Eine Ist-Führung je Abschnitt nach den Regeln von C-FAC-05 (Fahrradstraße, Radweg mit begleitenden Radwegen je Seite, Streifen, Sharrow/Busspur, keine). Die Prinzipienbewertung (c04, C-PRI-02), die Führungsform (c05, C-FAC-05) und die Diskrepanz (s08, D-DES-01/D-USE-01) lesen sie; bis rules.yaml 0.19.0 gab es drei Definitionen. `separated_cycle_track_present` = Ist-Führung Radweg je Seite oder Zweirichtungsradweg; unbekannt, wenn die Ist-Klasse „keine“ nur aus fehlenden OSM-Angaben folgt (S-FEAT-10).

## Kurzfassung

- 34 702 klassifizierte Abschnitte, 4 387 km. Baulicher Radweg: ja 1 054 km, nein 1 670 km, unbekannt 1 664 km.
- Radweg-Tag an der Straße (S-FEAT-10 `cycle_track_tag`), aber weder begleitender Radweg noch Radweg in der Straßenlinie im Radgraphen (Flag `track_tag_only`): 1 592 Abschnitte, 107.7 km. Sie zählen nach C-FAC-05 überall als Radweg; bis cycling_rules 0.10.0 zählte c04 sie als Fahrbahnführung. Prüfliste unten.
- Abweichung von der früheren Radgraph-Definition (C-PRI-02 bis cycling_rules 0.10.0): 220.7 km; davon Radweg-Tag ohne Radgraph 104.6 km, begleitende Zweirichtungsradwege auf beiden Seiten (E9: jetzt Radweg je Seite) 73.6 km.
- Abweichung vom Radweg-Tag allein (S-FEAT-10 bis rules.yaml 0.19.0): Tag nein/unbekannt, Ist Radweg 163.8 km (begleitender Radweg im Radgraphen); Tag ja, Ist kein Radweg 0.9 km (Fahrradstraße geht vor).
- Parallelroute (S-FEAT-11, nur Soll-Radnetz RSV/HAUPT/BASIS mit Umweg ≤ P-DIR-01; geprüft für GOW50): 245.4 von 607.3 km; ohne baulichen Radweg 58.3 von 118.5 km.
- Laufzeit: Eingänge 0 s, Ist-Führung 1 s, Parallelroute 12 s.

## km je Ist-Führung und Straßenkategorie

| Ist-Führung | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | gesamt |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Radweg je Seite | 0.3 | 359.5 | 70.1 | 289.4 | 0.3 | 719.6 |
| Zweirichtungsradweg | 10.0 | 129.4 | 23.6 | 170.7 | 0.5 | 334.2 |
| Radfahrstreifen | 0.0 | 46.8 | 14.4 | 63.3 | 0.0 | 124.5 |
| Fahrradstraße | 0.0 | 0.5 | 0.0 | 26.0 | 0.0 | 26.6 |
| Mischverkehr | 178.9 | 71.1 | 40.7 | 2 774.5 | 117.2 | 3 182.4 |
| eigene Trasse | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## Frühere Radgraph-Definition (C-PRI-02) gegen S-FEAT-13 (km)

Zeilen: Ist-Führung nach C-PRI-02 bis cycling_rules 0.10.0 (begleitende Radwege, sonst längste Straßenkante); Spalten: S-FEAT-13.

| C-PRI-02 alt | Radweg je Seite | Zweirichtungsradweg | Radfahrstreifen | Fahrradstraße | Mischverkehr |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fahrradstraße | 0.0 | 0.0 | 0.0 | 24.3 | 0.0 |
| Mischverkehr | 119.8 | 0.0 | 6.6 | 0.9 | 2 948.2 |
| Radfahrstreifen | 18.3 | 0.0 | 117.9 | 0.0 | 0.0 |
| Radweg je Seite | 504.8 | 0.0 | 0.0 | 0.3 | 0.0 |
| Zweirichtungsradweg | 73.6 | 334.2 | 0.0 | 1.1 | 0.0 |
| ohne Kante | 3.1 | 0.0 | 0.0 | 0.0 | 234.2 |

## Prüfliste: Radweg-Tag ohne Radweg im Radgraphen (`track_tag_only`)

OSM trägt an der Straße einen Radweg (cycleway*=track|separate oder bicycle=use_sidepath), der Radgraph hat aber keinen begleitenden Radweg (sidepath_of) und keinen Radweg in der Straßenlinie; die Straßenkante hat einen Widerstand für Fahrbahnführung (C-IMP-04…07). Für Diskrepanz, Prinzipien und Führungsform gilt der Radweg (C-FAC-05); der Widerstand im Radgraphen (c01) bleibt unverändert. Tags prüfen oder den begleitenden Radweg in OSM ergänzen (docs/open_questions.md).

km je Straßenkategorie: SW 0.3, GOW50 55.4, GOW30 9.2, ETW30 42.7, ETW_ERF 0.0

### Längste 40 Straßen (je Straße und Bezirk zusammengefasst)

| Straße | Bezirk | Kategorie | Abschnitte | km |
| --- | --- | --- | ---: | ---: |
| Vollhöfner Weiden | Harburg | GOW50 | 6 | 1.83 |
| Glashütter Landstraße | Wandsbek | ETW30 | 3 | 1.82 |
| Glinder Straße | Hamburg-Mitte | GOW50 | 19 | 1.80 |
| (ohne Namen) | Hamburg-Mitte | ETW30 | 21 | 1.78 |
| Cuxhavener Straße | Harburg | GOW50 | 7 | 1.47 |
| Osdorfer Landstraße | Altona | GOW50 | 14 | 1.40 |
| Oldesloer Straße | Eimsbüttel | GOW50 | 9 | 1.31 |
| Osterfelddeich / Kirchenaußendeichsweg | Hamburg-Mitte | ETW30 | 1 | 1.28 |
| Finkenwerder Straße | Hamburg-Mitte | GOW50 | 9 | 1.18 |
| Bremer Straße | Harburg | GOW50 | 8 | 1.17 |
| Wohldorfer Damm | Wandsbek | ETW30 | 3 | 1.07 |
| Roßweg | Hamburg-Mitte | ETW30 | 9 | 1.04 |
| Zum Golfplatz / Wendloher Weg | Eimsbüttel | ETW30 | 1 | 0.99 |
| Rugenberger Damm | Hamburg-Mitte | ETW30 | 1 | 0.96 |
| Alsterkrugchaussee | Hamburg-Nord | GOW50 | 12 | 0.90 |
| Liebigstraße | Hamburg-Mitte | GOW50 | 3 | 0.83 |
| Maldfeldstraße | Harburg | ETW30 | 1 | 0.81 |
| Hainholzweg | Harburg | ETW30 | 4 | 0.81 |
| Stader Straße | Harburg | GOW50 | 6 | 0.81 |
| Kornweide | Hamburg-Mitte | GOW50 | 5 | 0.79 |
| Holsteiner Chaussee | Eimsbüttel | GOW50 | 12 | 0.79 |
| Ehestorfer Weg | Harburg | GOW30 | 2 | 0.78 |
| Roßdamm | Hamburg-Mitte | GOW50 | 1 | 0.77 |
| Nettelnburger Landweg | Bergedorf | ETW30 | 9 | 0.76 |
| Kieler Straße | Eimsbüttel | GOW50 | 14 | 0.76 |
| Fürstenmoordamm | Harburg | GOW30 | 2 | 0.74 |
| Reiherstieg-Hauptdeich | Hamburg-Mitte | GOW30 | 2 | 0.73 |
| Sieker Landstraße | Wandsbek | GOW50 | 8 | 0.72 |
| Lemsahler Landstraße | Wandsbek | GOW30 | 1 | 0.70 |
| Hamburger Straße | nan | ETW30 | 3 | 0.70 |
| Bargteheider Straße | Wandsbek | GOW50 | 4 | 0.69 |
| Hohe-Schaar-Straße | Hamburg-Mitte | GOW30 | 6 | 0.68 |
| Unterer Landweg | Hamburg-Mitte | GOW50 | 5 | 0.68 |
| Zeppelinstraße | Hamburg-Nord | ETW30 | 12 | 0.63 |
| Barmbeker Straße | Hamburg-Nord | GOW50 | 9 | 0.62 |
| Curslacker Neuer Deich | Bergedorf | GOW50 | 11 | 0.62 |
| Harburger Chaussee | Hamburg-Mitte | GOW50 | 6 | 0.59 |
| Jahnring | Hamburg-Nord | GOW50 | 6 | 0.57 |
| Sengelmannstraße | Hamburg-Nord | ETW30 | 11 | 0.57 |
| Glinder Weg | Bergedorf | ETW30 | 1 | 0.56 |

Vollständige Liste: `data/interim/ist_facility.parquet`, Spalte `track_tag_only`.

### Stichproben (30, über Bezirke verteilt, Seed 42)

| segment_id | Straße | Bezirk | Kategorie | C-PRI-02 alt | Prüfen |
| --- | --- | --- | --- | --- | --- |
| `seg_10b9a464ef2097b9` | Bahrenfelder Chaussee | Altona | GOW50 | Radfahrstreifen | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559531,5936152]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.570852/9.898970) · [OSM](https://www.openstreetmap.org/?mlat=53.570852&mlon=9.898970#map=18/53.570852/9.898970) |
| `seg_2e08b757a509b726` | Behringstraße / Walderseestraße | Altona | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559427,5934650]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.557366/9.897114) · [OSM](https://www.openstreetmap.org/?mlat=53.557366&mlon=9.897114#map=18/53.557366/9.897114) |
| `seg_79d67627fca6303f` | Max-Brauer-Allee | Altona | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562830,5934807]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558378/9.948519) · [OSM](https://www.openstreetmap.org/?mlat=53.558378&mlon=9.948519#map=18/53.558378/9.948519) |
| `seg_590116c18c90e3b8` | Sander Damm | Bergedorf | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579760,5927540]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.490777/10.202190) · [OSM](https://www.openstreetmap.org/?mlat=53.490777&mlon=10.202190#map=18/53.490777/10.202190) |
| `seg_62ea090c4e38f954` | Bergedorfer Straße | Bergedorf | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579788,5927576]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.491094/10.202616) · [OSM](https://www.openstreetmap.org/?mlat=53.491094&mlon=10.202616#map=18/53.491094/10.202616) |
| `seg_17c5dc360d218640` | Schulweg | Eimsbüttel | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563517,5936579]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.574222/9.959250) · [OSM](https://www.openstreetmap.org/?mlat=53.574222&mlon=9.959250#map=18/53.574222/9.959250) |
| `seg_255d5954765b3021` | Kieler Straße | Eimsbüttel | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559935,5940233]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607480/9.905865) · [OSM](https://www.openstreetmap.org/?mlat=53.607480&mlon=9.905865#map=18/53.607480/9.905865) |
| `seg_cecd4b8ffd0ae5fe` | Bundesstraße | Eimsbüttel | ETW30 | Radfahrstreifen | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564852,5935678]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.565961/9.979218) · [OSM](https://www.openstreetmap.org/?mlat=53.565961&mlon=9.979218#map=18/53.565961/9.979218) |
| `seg_e766d2d34801d061` | Doormannsweg | Eimsbüttel | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563327,5936173]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.570600/9.956293) · [OSM](https://www.openstreetmap.org/?mlat=53.570600&mlon=9.956293#map=18/53.570600/9.956293) |
| `seg_0b1b420d90635705` | (ohne Namen) | Hamburg-Mitte | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565084,5930547]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.519816/9.981652) · [OSM](https://www.openstreetmap.org/?mlat=53.519816&mlon=9.981652#map=18/53.519816/9.981652) |
| `seg_184ece9c37f1008f` | Helgoländer Allee | Hamburg-Mitte | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564230,5933449]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546006/9.969371) · [OSM](https://www.openstreetmap.org/?mlat=53.546006&mlon=9.969371#map=18/53.546006/9.969371) |
| `seg_7b402e0aedbe7979` | (ohne Namen) | Hamburg-Mitte | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571741,5934597]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.555349/10.082967) · [OSM](https://www.openstreetmap.org/?mlat=53.555349&mlon=10.082967#map=18/53.555349/10.082967) |
| `seg_9e7ac42b80e8d8ff` | Burgstraße | Hamburg-Mitte | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568807,5934995]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559324/10.038769) · [OSM](https://www.openstreetmap.org/?mlat=53.559324&mlon=10.038769#map=18/53.559324/10.038769) |
| `seg_ac2801227d618d47` | Sievekingplatz | Hamburg-Mitte | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564880,5934565]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.555954/9.979406) · [OSM](https://www.openstreetmap.org/?mlat=53.555954&mlon=9.979406#map=18/53.555954/9.979406) |
| `seg_d45315218cc8e7e2` | Millerntordamm | Hamburg-Mitte | ETW30 | ohne Kante | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564484,5933860]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.549666/9.973278) · [OSM](https://www.openstreetmap.org/?mlat=53.549666&mlon=9.973278#map=18/53.549666/9.973278) |
| `seg_f74172463e10dc23` | Glinder Straße | Hamburg-Mitte | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575746,5933629]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546092/10.143181) · [OSM](https://www.openstreetmap.org/?mlat=53.546092&mlon=10.143181#map=18/53.546092/10.143181) |
| `seg_0be0b44008702754` | Sechslingspforte | Hamburg-Nord | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567256,5935361]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.562812/10.015436) · [OSM](https://www.openstreetmap.org/?mlat=53.562812&mlon=10.015436#map=18/53.562812/10.015436) |
| `seg_22f565f609c5c4b3` | Kellinghusenstraße | Hamburg-Nord | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565702,5938657]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.592625/9.992670) · [OSM](https://www.openstreetmap.org/?mlat=53.592625&mlon=9.992670#map=18/53.592625/9.992670) |
| `seg_501ee8d176053060` | Deelböge | Hamburg-Nord | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565335,5939865]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.603532/9.987383) · [OSM](https://www.openstreetmap.org/?mlat=53.603532&mlon=9.987383#map=18/53.603532/9.987383) |
| `seg_5268d2671e5a349a` | Barmbeker Straße | Hamburg-Nord | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566901,5938447]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.590587/10.010746) · [OSM](https://www.openstreetmap.org/?mlat=53.590587&mlon=10.010746#map=18/53.590587/10.010746) |
| `seg_b672bcd7b40bc618` | Rümkerstraße | Hamburg-Nord | ETW30 | Radfahrstreifen | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569492,5939792]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.602338/10.050182) · [OSM](https://www.openstreetmap.org/?mlat=53.602338&mlon=10.050182#map=18/53.602338/10.050182) |
| `seg_de19570f67b78a7f` | Winterhuder Marktplatz | Hamburg-Nord | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566157,5938880]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594571/9.999601) · [OSM](https://www.openstreetmap.org/?mlat=53.594571&mlon=9.999601#map=18/53.594571/9.999601) |
| `seg_0c15919c4aeab19b` | Maldfeldstraße | Harburg | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562190,5920603]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.430798/9.936042) · [OSM](https://www.openstreetmap.org/?mlat=53.430798&mlon=9.936042#map=18/53.430798/9.936042) |
| `seg_388993c8ca017a0b` | Vollhöfner Weiden | Harburg | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559564,5929264]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.508947/9.898160) · [OSM](https://www.openstreetmap.org/?mlat=53.508947&mlon=9.898160#map=18/53.508947/9.898160) |
| `seg_95163000739aef4a` | Aluminiumstraße | Harburg | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558757,5929762]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.513509/9.886092) · [OSM](https://www.openstreetmap.org/?mlat=53.513509&mlon=9.886092#map=18/53.513509/9.886092) |
| `seg_b0ccb7fd45c6e9ce` | Am Pulverhof | Wandsbek | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575138,5939004]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594482/10.135289) · [OSM](https://www.openstreetmap.org/?mlat=53.594482&mlon=10.135289#map=18/53.594482/10.135289) |
| `seg_d88ae5a141d9317d` | (ohne Namen) | Wandsbek | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572648,5938861]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.593547/10.097646) · [OSM](https://www.openstreetmap.org/?mlat=53.593547&mlon=10.097646#map=18/53.593547/10.097646) |
| `seg_ead96a353f63eef6` | August-Krogmann-Straße | Wandsbek | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573890,5940416]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607351/10.116770) · [OSM](https://www.openstreetmap.org/?mlat=53.607351&mlon=10.116770#map=18/53.607351/10.116770) |
| `seg_f2ee076a38868863` | (ohne Namen) | Wandsbek | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573894,5940421]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607391/10.116840) · [OSM](https://www.openstreetmap.org/?mlat=53.607391&mlon=10.116840#map=18/53.607391/10.116840) |
| `seg_44b6a7d755189654` | Hauptstraße | nan | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553296,5924320]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.465182/9.802816) · [OSM](https://www.openstreetmap.org/?mlat=53.465182&mlon=9.802816#map=18/53.465182/9.802816) |

## Parallelroute an Abschnitten ohne baulichen Radweg (S-FEAT-11)

D-DES-01 zählt „kein baulicher Radweg“ dort nur mit dem Gewicht 0,5 (severity_if); die Soll-Führung (C-FAC-01) bleibt Radweg, Flag `parallel_cycle_route` in c05.

km je Ebene: bis RSV (P-DIR-01 ≤ 1.1) 8.1, bis HAUPT (P-DIR-01 ≤ 1.2) 40.3, bis BASIS (P-DIR-01 ≤ 1.3) 9.9

### Stichproben (30, über Bezirke verteilt, Seed 42)

| segment_id | Straße | Bezirk | Ebene | Umweg | Anteil im Puffer | Prüfen |
| --- | --- | --- | --- | ---: | ---: | --- |
| `seg_083401f41080c06d` | Holstenstraße | Altona | HAUPT | 0.96 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562881,5934864]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558889/9.949290) · [OSM](https://www.openstreetmap.org/?mlat=53.558889&mlon=9.949290#map=18/53.558889/9.949290) |
| `seg_23cdcc60ecc10b5a` | Bahrenfelder Marktplatz | Altona | RSV | 0.13 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559651,5935491]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564897/9.900655) · [OSM](https://www.openstreetmap.org/?mlat=53.564897&mlon=9.900655#map=18/53.564897/9.900655) |
| `seg_bb73f010c0dae3c2` | Palmaille | Altona | HAUPT | 0.35 | 0.96 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562530,5933462]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546328/9.943723) · [OSM](https://www.openstreetmap.org/?mlat=53.546328&mlon=9.943723#map=18/53.546328/9.943723) |
| `seg_d63276ed7c4d2e01` | Holstenstraße | Altona | BASIS | 0.15 | 0.95 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563303,5933880]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.549992/9.955464) · [OSM](https://www.openstreetmap.org/?mlat=53.549992&mlon=9.955464#map=18/53.549992/9.955464) |
| `seg_48c65fb5a3f283a0` | Bergedorfer Straße | Bergedorf | HAUPT | 0.94 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577418,5930103]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.514157/10.167531) · [OSM](https://www.openstreetmap.org/?mlat=53.514157&mlon=10.167531#map=18/53.514157/10.167531) |
| `seg_4b548c3d7e1cb258` | Bergedorfer Straße | Bergedorf | HAUPT | 0.97 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576345,5930754]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.520161/10.151516) · [OSM](https://www.openstreetmap.org/?mlat=53.520161&mlon=10.151516#map=18/53.520161/10.151516) |
| `seg_62dd8977c5c32951` | Bergedorfer Straße | Bergedorf | RSV | 0.86 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575329,5931404]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.526150/10.136349) · [OSM](https://www.openstreetmap.org/?mlat=53.526150&mlon=10.136349#map=18/53.526150/10.136349) |
| `seg_35dfc1fe7842007e` | Kleiner Schäferkamp | Eimsbüttel | HAUPT | 0.99 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563962,5935605]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.565419/9.965758) · [OSM](https://www.openstreetmap.org/?mlat=53.565419&mlon=9.965758#map=18/53.565419/9.965758) |
| `seg_5705f349e1e92b96` | Sportplatzring | Eimsbüttel | BASIS | 0.60 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561458,5938560]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.592272/9.928548) · [OSM](https://www.openstreetmap.org/?mlat=53.592272&mlon=9.928548#map=18/53.592272/9.928548) |
| `seg_e8c51f39beb4ada7` | Theodor-Heuss-Platz | Eimsbüttel | RSV | 0.88 | 0.90 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565568,5935172]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.561328/9.989921) · [OSM](https://www.openstreetmap.org/?mlat=53.561328&mlon=9.989921#map=18/53.561328/9.989921) |
| `seg_106b019829cd8a7c` | Hammer Landstraße | Hamburg-Mitte | RSV | 0.97 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570018,5934532]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.555001/10.056946) · [OSM](https://www.openstreetmap.org/?mlat=53.555001&mlon=10.056946#map=18/53.555001/10.056946) |
| `seg_11de1b1fa27fb4b0` | Graskeller | Hamburg-Mitte | HAUPT | 0.72 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565352,5933854]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.549504/9.986388) · [OSM](https://www.openstreetmap.org/?mlat=53.549504&mlon=9.986388#map=18/53.549504/9.986388) |
| `seg_125519c694e37135` | Stephansplatz | Hamburg-Mitte | HAUPT | 0.97 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565534,5934843]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558371/9.989335) · [OSM](https://www.openstreetmap.org/?mlat=53.558371&mlon=9.989335#map=18/53.558371/9.989335) |
| `seg_2719a38bc226c176` | Ausschläger Allee | Hamburg-Mitte | HAUPT | 0.99 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570054,5931910]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.531427/10.056910) · [OSM](https://www.openstreetmap.org/?mlat=53.531427&mlon=10.056910#map=18/53.531427/10.056910) |
| `seg_278a95feba356106` | Simon-von-Utrecht-Straße | Hamburg-Mitte | RSV | 0.10 | 0.83 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563394,5934071]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.551697/9.956877) · [OSM](https://www.openstreetmap.org/?mlat=53.551697&mlon=9.956877#map=18/53.551697/9.956877) |
| `seg_61b03d956bd293af` | – | Hamburg-Mitte | RSV | 0.66 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567811,5931556]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.528545/10.022994) · [OSM](https://www.openstreetmap.org/?mlat=53.528545&mlon=10.022994#map=18/53.528545/10.022994) |
| `seg_64be1593d6109878` | Simon-von-Utrecht-Straße | Hamburg-Mitte | RSV | 0.95 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563850,5934012]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.551111/9.963751) · [OSM](https://www.openstreetmap.org/?mlat=53.551111&mlon=9.963751#map=18/53.551111/9.963751) |
| `seg_b5272d1a7dea072b` | Neuenfelder Straße | Hamburg-Mitte | HAUPT | 0.31 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566502,5928099]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.497640/10.002516) · [OSM](https://www.openstreetmap.org/?mlat=53.497640&mlon=10.002516#map=18/53.497640/10.002516) |
| `seg_e3e6f658ee1b0664` | Baumwall | Hamburg-Mitte | HAUPT | 0.20 | 0.97 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565043,5933245]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.544074/9.981590) · [OSM](https://www.openstreetmap.org/?mlat=53.544074&mlon=9.981590#map=18/53.544074/9.981590) |
| `seg_4f9feb3bfd4ddb25` | Barmbeker Markt | Hamburg-Nord | RSV | 1.00 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569282,5937637]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.583004/10.046528) · [OSM](https://www.openstreetmap.org/?mlat=53.583004&mlon=10.046528#map=18/53.583004/10.046528) |
| `seg_a9d88be72deb9bd4` | Lenhartzstraße | Hamburg-Nord | HAUPT | 0.88 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565086,5938367]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.590102/9.983313) · [OSM](https://www.openstreetmap.org/?mlat=53.590102&mlon=9.983313#map=18/53.590102/9.983313) |
| `seg_ce6ffc8237c2ff48` | Bramfelder Straße | Hamburg-Nord | RSV | 0.94 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569253,5937609]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.582751/10.046080) · [OSM](https://www.openstreetmap.org/?mlat=53.582751&mlon=10.046080#map=18/53.582751/10.046080) |
| `seg_e2d44dcc389cf6b2` | Erdkampsweg | Hamburg-Nord | HAUPT | 0.06 | 0.99 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567814,5942469]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.626619/10.025406) · [OSM](https://www.openstreetmap.org/?mlat=53.626619&mlon=10.025406#map=18/53.626619/10.025406) |
| `seg_ffa305f5666cd417` | Barmbeker Straße | Hamburg-Nord | HAUPT | 0.59 | 0.99 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567372,5937990]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.586424/10.017757) · [OSM](https://www.openstreetmap.org/?mlat=53.586424&mlon=10.017757#map=18/53.586424/10.017757) |
| `seg_287f995c38753798` | Hohe Straße | Harburg | HAUPT | 0.03 | 0.56 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564999,5922953]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.451581/9.978800) · [OSM](https://www.openstreetmap.org/?mlat=53.451581&mlon=9.978800#map=18/53.451581/9.978800) |
| `seg_931c3760babc64dd` | Hohe Straße | Harburg | HAUPT | 0.03 | 0.82 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564998,5922965]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.451688/9.978788) · [OSM](https://www.openstreetmap.org/?mlat=53.451688&mlon=9.978788#map=18/53.451688/9.978788) |
| `seg_10f50665dbf00346` | Höltigbaum | Wandsbek | HAUPT | 0.92 | 0.92 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577721,5941272]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.614488/10.174882) · [OSM](https://www.openstreetmap.org/?mlat=53.614488&mlon=10.174882#map=18/53.614488/10.174882) |
| `seg_69da7db0b471d4c8` | Halenreie | Wandsbek | HAUPT | 0.85 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576786,5945265]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.650503/10.161727) · [OSM](https://www.openstreetmap.org/?mlat=53.650503&mlon=10.161727#map=18/53.650503/10.161727) |
| `seg_b794288837f97d32` | Sieker Landstraße | Wandsbek | BASIS | 0.97 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577907,5940427]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.606860/10.177486) · [OSM](https://www.openstreetmap.org/?mlat=53.606860&mlon=10.177486#map=18/53.606860/10.177486) |
| `seg_fadbfc5eea28067e` | August-Krogmann-Straße | Wandsbek | BASIS | 0.98 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573569,5941919]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.620897/10.112286) · [OSM](https://www.openstreetmap.org/?mlat=53.620897&mlon=10.112286#map=18/53.620897/10.112286) |

## Grenzen

- Begleitende Radwege und ihre Seite kommen aus dem Radgraphen (C-GRAPH-06); fehlt die Zuordnung, entscheidet der Tag an der Straße.
- Parallelroute: Netzweg zwischen den Lotfußpunkten der Abschnittsenden auf den Soll-Kanten der Ebene, ohne Zu- und Abfahrt; sehr kurze Abschnitte werden damit eher großzügig bewertet.
- Ohne jede OSM-Angabe bleibt `separated_cycle_track_present` unbekannt (S-FEAT-10), die Ist-Führung ist Mischverkehr (C-FAC-05).

Quellen: OpenStreetMap-Mitwirkende (ODbL); Freie und Hansestadt Hamburg, Fahrradstraßen (dl-de/by-2.0).
