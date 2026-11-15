# Ist-Führung und Parallelroute je Abschnitt (Stufe c03b)

Erzeugt 2026-11-15T20:17:11+00:00 mit pipeline/c03b_ist_facility.py · rules.yaml 0.23.0 · cycling_rules.yaml 0.12.0 · nicht amtlicher Entwurf. Regeln S-FEAT-13 und S-FEAT-11 (Review 2026-11 F26/E9, F21), source_type assumption, status draft.

Eine Ist-Führung je Abschnitt nach den Regeln von C-FAC-05 (Fahrradstraße, Radweg mit begleitenden Radwegen je Seite, Streifen, Sharrow/Busspur, keine). Die Prinzipienbewertung (c04, C-PRI-02), die Führungsform (c05, C-FAC-05) und die Diskrepanz (s08, D-DES-01/D-USE-01) lesen sie; bis rules.yaml 0.19.0 gab es drei Definitionen. `separated_cycle_track_present` = Ist-Führung Radweg je Seite oder Zweirichtungsradweg; unbekannt, wenn die Ist-Klasse „keine“ nur aus fehlenden OSM-Angaben folgt (S-FEAT-10).

## Kurzfassung

- 34 702 klassifizierte Abschnitte, 4 387 km. Baulicher Radweg: ja 1 054 km, nein 1 670 km, unbekannt 1 664 km.
- Radweg-Tag an der Straße (S-FEAT-10 `cycle_track_tag`), aber weder begleitender Radweg noch Radweg in der Straßenlinie im Radgraphen (Flag `track_tag_only`): 1 592 Abschnitte, 107.7 km. Sie zählen nach C-FAC-05 überall als Radweg; bis cycling_rules 0.10.0 zählte c04 sie als Fahrbahnführung. Prüfliste unten.
- Abweichung von der früheren Radgraph-Definition (C-PRI-02 bis cycling_rules 0.10.0): 220.7 km; davon Radweg-Tag ohne Radgraph 104.6 km, begleitende Zweirichtungsradwege auf beiden Seiten (E9: jetzt Radweg je Seite) 73.6 km.
- Abweichung vom Radweg-Tag allein (S-FEAT-10 bis rules.yaml 0.19.0): Tag nein/unbekannt, Ist Radweg 163.8 km (begleitender Radweg im Radgraphen); Tag ja, Ist kein Radweg 0.9 km (Fahrradstraße geht vor).
- Parallelroute (S-FEAT-11, nur Soll-Radnetz RSV/HAUPT/BASIS mit Umweg ≤ P-DIR-01; geprüft für GOW50): 72.9 von 200.3 km; ohne baulichen Radweg 25.5 von 48.7 km.
- Laufzeit: Eingänge 0 s, Ist-Führung 1 s, Parallelroute 3 s.

## km je Ist-Führung und Straßenkategorie

| Ist-Führung | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | gesamt |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Radweg je Seite | 0.3 | 104.5 | 325.1 | 289.4 | 0.3 | 719.6 |
| Zweirichtungsradweg | 10.0 | 47.1 | 105.7 | 170.9 | 0.5 | 334.2 |
| Radfahrstreifen | 0.0 | 6.8 | 54.3 | 63.5 | 0.0 | 124.5 |
| Fahrradstraße | 0.0 | 0.0 | 0.6 | 26.0 | 0.0 | 26.6 |
| Mischverkehr | 178.9 | 41.9 | 69.9 | 2 774.5 | 117.2 | 3 182.4 |
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

km je Straßenkategorie: SW 0.3, GOW50 24.2, GOW30 40.4, ETW30 42.7, ETW_ERF 0.0

### Längste 40 Straßen (je Straße und Bezirk zusammengefasst)

| Straße | Bezirk | Kategorie | Abschnitte | km |
| --- | --- | --- | ---: | ---: |
| Vollhöfner Weiden | Harburg | GOW50 | 6 | 1.83 |
| Glashütter Landstraße | Wandsbek | ETW30 | 3 | 1.82 |
| Glinder Straße | Hamburg-Mitte | GOW50 | 19 | 1.80 |
| (ohne Namen) | Hamburg-Mitte | ETW30 | 21 | 1.78 |
| Oldesloer Straße | Eimsbüttel | GOW50 | 8 | 1.30 |
| Osterfelddeich / Kirchenaußendeichsweg | Hamburg-Mitte | ETW30 | 1 | 1.28 |
| Finkenwerder Straße | Hamburg-Mitte | GOW50 | 9 | 1.18 |
| Osdorfer Landstraße | Altona | GOW30 | 12 | 1.10 |
| Cuxhavener Straße | Harburg | GOW50 | 5 | 1.07 |
| Wohldorfer Damm | Wandsbek | ETW30 | 3 | 1.07 |
| Roßweg | Hamburg-Mitte | ETW30 | 9 | 1.04 |
| Zum Golfplatz / Wendloher Weg | Eimsbüttel | ETW30 | 1 | 0.99 |
| Rugenberger Damm | Hamburg-Mitte | ETW30 | 1 | 0.96 |
| Bremer Straße | Harburg | GOW30 | 7 | 0.95 |
| Alsterkrugchaussee | Hamburg-Nord | GOW50 | 12 | 0.90 |
| Liebigstraße | Hamburg-Mitte | GOW50 | 3 | 0.83 |
| Maldfeldstraße | Harburg | ETW30 | 1 | 0.81 |
| Hainholzweg | Harburg | ETW30 | 4 | 0.81 |
| Ehestorfer Weg | Harburg | GOW30 | 2 | 0.78 |
| Roßdamm | Hamburg-Mitte | GOW50 | 1 | 0.77 |
| Nettelnburger Landweg | Bergedorf | ETW30 | 9 | 0.76 |
| Lemsahler Landstraße | Wandsbek | GOW30 | 2 | 0.76 |
| Fürstenmoordamm | Harburg | GOW30 | 2 | 0.74 |
| Reiherstieg-Hauptdeich | Hamburg-Mitte | GOW30 | 2 | 0.73 |
| Sieker Landstraße | Wandsbek | GOW50 | 8 | 0.72 |
| Hamburger Straße | nan | ETW30 | 3 | 0.70 |
| Bargteheider Straße | Wandsbek | GOW30 | 4 | 0.70 |
| Kornweide | Hamburg-Mitte | GOW50 | 4 | 0.68 |
| Hohe-Schaar-Straße | Hamburg-Mitte | GOW30 | 6 | 0.68 |
| Unterer Landweg | Hamburg-Mitte | GOW50 | 5 | 0.68 |
| Georg-Wilhelm-Straße | Hamburg-Mitte | GOW30 | 3 | 0.64 |
| Zeppelinstraße | Hamburg-Nord | ETW30 | 12 | 0.63 |
| Barmbeker Straße | Hamburg-Nord | GOW30 | 9 | 0.62 |
| Curslacker Neuer Deich | Bergedorf | GOW50 | 11 | 0.62 |
| Stader Straße | Harburg | GOW30 | 4 | 0.61 |
| Kieler Straße | Eimsbüttel | GOW30 | 12 | 0.60 |
| Sengelmannstraße | Hamburg-Nord | ETW30 | 11 | 0.57 |
| Glinder Weg | Bergedorf | ETW30 | 1 | 0.56 |
| Stapelfelder Straße | Wandsbek | ETW30 | 2 | 0.55 |
| Überseering | Hamburg-Nord | ETW30 | 15 | 0.55 |

Vollständige Liste: `data/interim/ist_facility.parquet`, Spalte `track_tag_only`.

### Stichproben (30, über Bezirke verteilt, Seed 42)

| segment_id | Straße | Bezirk | Kategorie | C-PRI-02 alt | Prüfen |
| --- | --- | --- | --- | --- | --- |
| `seg_10b9a464ef2097b9` | Bahrenfelder Chaussee | Altona | GOW30 | Radfahrstreifen | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559531,5936152]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.570852/9.898970) · [OSM](https://www.openstreetmap.org/?mlat=53.570852&mlon=9.898970#map=18/53.570852/9.898970) |
| `seg_2e08b757a509b726` | Behringstraße / Walderseestraße | Altona | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559427,5934650]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.557366/9.897114) · [OSM](https://www.openstreetmap.org/?mlat=53.557366&mlon=9.897114#map=18/53.557366/9.897114) |
| `seg_79d67627fca6303f` | Max-Brauer-Allee | Altona | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562830,5934807]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558378/9.948519) · [OSM](https://www.openstreetmap.org/?mlat=53.558378&mlon=9.948519#map=18/53.558378/9.948519) |
| `seg_590116c18c90e3b8` | Sander Damm | Bergedorf | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579760,5927540]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.490777/10.202190) · [OSM](https://www.openstreetmap.org/?mlat=53.490777&mlon=10.202190#map=18/53.490777/10.202190) |
| `seg_62ea090c4e38f954` | Bergedorfer Straße | Bergedorf | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579788,5927576]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.491094/10.202616) · [OSM](https://www.openstreetmap.org/?mlat=53.491094&mlon=10.202616#map=18/53.491094/10.202616) |
| `seg_17c5dc360d218640` | Schulweg | Eimsbüttel | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563517,5936579]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.574222/9.959250) · [OSM](https://www.openstreetmap.org/?mlat=53.574222&mlon=9.959250#map=18/53.574222/9.959250) |
| `seg_255d5954765b3021` | Kieler Straße | Eimsbüttel | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559935,5940233]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607480/9.905865) · [OSM](https://www.openstreetmap.org/?mlat=53.607480&mlon=9.905865#map=18/53.607480/9.905865) |
| `seg_cecd4b8ffd0ae5fe` | Bundesstraße | Eimsbüttel | ETW30 | Radfahrstreifen | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564852,5935678]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.565961/9.979218) · [OSM](https://www.openstreetmap.org/?mlat=53.565961&mlon=9.979218#map=18/53.565961/9.979218) |
| `seg_e766d2d34801d061` | Doormannsweg | Eimsbüttel | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563327,5936173]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.570600/9.956293) · [OSM](https://www.openstreetmap.org/?mlat=53.570600&mlon=9.956293#map=18/53.570600/9.956293) |
| `seg_0b1b420d90635705` | (ohne Namen) | Hamburg-Mitte | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565084,5930547]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.519816/9.981652) · [OSM](https://www.openstreetmap.org/?mlat=53.519816&mlon=9.981652#map=18/53.519816/9.981652) |
| `seg_184ece9c37f1008f` | Helgoländer Allee | Hamburg-Mitte | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564230,5933449]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546006/9.969371) · [OSM](https://www.openstreetmap.org/?mlat=53.546006&mlon=9.969371#map=18/53.546006/9.969371) |
| `seg_7b402e0aedbe7979` | (ohne Namen) | Hamburg-Mitte | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571741,5934597]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.555349/10.082967) · [OSM](https://www.openstreetmap.org/?mlat=53.555349&mlon=10.082967#map=18/53.555349/10.082967) |
| `seg_9e7ac42b80e8d8ff` | Burgstraße | Hamburg-Mitte | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568807,5934995]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559324/10.038769) · [OSM](https://www.openstreetmap.org/?mlat=53.559324&mlon=10.038769#map=18/53.559324/10.038769) |
| `seg_ac2801227d618d47` | Sievekingplatz | Hamburg-Mitte | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564880,5934565]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.555954/9.979406) · [OSM](https://www.openstreetmap.org/?mlat=53.555954&mlon=9.979406#map=18/53.555954/9.979406) |
| `seg_d45315218cc8e7e2` | Millerntordamm | Hamburg-Mitte | ETW30 | ohne Kante | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564484,5933860]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.549666/9.973278) · [OSM](https://www.openstreetmap.org/?mlat=53.549666&mlon=9.973278#map=18/53.549666/9.973278) |
| `seg_f74172463e10dc23` | Glinder Straße | Hamburg-Mitte | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575746,5933629]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546092/10.143181) · [OSM](https://www.openstreetmap.org/?mlat=53.546092&mlon=10.143181#map=18/53.546092/10.143181) |
| `seg_0be0b44008702754` | Sechslingspforte | Hamburg-Nord | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567256,5935361]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.562812/10.015436) · [OSM](https://www.openstreetmap.org/?mlat=53.562812&mlon=10.015436#map=18/53.562812/10.015436) |
| `seg_22f565f609c5c4b3` | Kellinghusenstraße | Hamburg-Nord | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565702,5938657]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.592625/9.992670) · [OSM](https://www.openstreetmap.org/?mlat=53.592625&mlon=9.992670#map=18/53.592625/9.992670) |
| `seg_501ee8d176053060` | Deelböge | Hamburg-Nord | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565335,5939865]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.603532/9.987383) · [OSM](https://www.openstreetmap.org/?mlat=53.603532&mlon=9.987383#map=18/53.603532/9.987383) |
| `seg_5268d2671e5a349a` | Barmbeker Straße | Hamburg-Nord | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566901,5938447]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.590587/10.010746) · [OSM](https://www.openstreetmap.org/?mlat=53.590587&mlon=10.010746#map=18/53.590587/10.010746) |
| `seg_b672bcd7b40bc618` | Rümkerstraße | Hamburg-Nord | ETW30 | Radfahrstreifen | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569492,5939792]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.602338/10.050182) · [OSM](https://www.openstreetmap.org/?mlat=53.602338&mlon=10.050182#map=18/53.602338/10.050182) |
| `seg_de19570f67b78a7f` | Winterhuder Marktplatz | Hamburg-Nord | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566157,5938880]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594571/9.999601) · [OSM](https://www.openstreetmap.org/?mlat=53.594571&mlon=9.999601#map=18/53.594571/9.999601) |
| `seg_0c15919c4aeab19b` | Maldfeldstraße | Harburg | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562190,5920603]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.430798/9.936042) · [OSM](https://www.openstreetmap.org/?mlat=53.430798&mlon=9.936042#map=18/53.430798/9.936042) |
| `seg_388993c8ca017a0b` | Vollhöfner Weiden | Harburg | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559564,5929264]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.508947/9.898160) · [OSM](https://www.openstreetmap.org/?mlat=53.508947&mlon=9.898160#map=18/53.508947/9.898160) |
| `seg_95163000739aef4a` | Aluminiumstraße | Harburg | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558757,5929762]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.513509/9.886092) · [OSM](https://www.openstreetmap.org/?mlat=53.513509&mlon=9.886092#map=18/53.513509/9.886092) |
| `seg_b0ccb7fd45c6e9ce` | Am Pulverhof | Wandsbek | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575138,5939004]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594482/10.135289) · [OSM](https://www.openstreetmap.org/?mlat=53.594482&mlon=10.135289#map=18/53.594482/10.135289) |
| `seg_d88ae5a141d9317d` | (ohne Namen) | Wandsbek | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572648,5938861]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.593547/10.097646) · [OSM](https://www.openstreetmap.org/?mlat=53.593547&mlon=10.097646#map=18/53.593547/10.097646) |
| `seg_ead96a353f63eef6` | August-Krogmann-Straße | Wandsbek | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573890,5940416]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607351/10.116770) · [OSM](https://www.openstreetmap.org/?mlat=53.607351&mlon=10.116770#map=18/53.607351/10.116770) |
| `seg_f2ee076a38868863` | (ohne Namen) | Wandsbek | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573894,5940421]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607391/10.116840) · [OSM](https://www.openstreetmap.org/?mlat=53.607391&mlon=10.116840#map=18/53.607391/10.116840) |
| `seg_44b6a7d755189654` | Hauptstraße | nan | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553296,5924320]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.465182/9.802816) · [OSM](https://www.openstreetmap.org/?mlat=53.465182&mlon=9.802816#map=18/53.465182/9.802816) |

## Parallelroute an Abschnitten ohne baulichen Radweg (S-FEAT-11)

D-DES-01 zählt „kein baulicher Radweg“ dort nur mit dem Gewicht 0,5 (severity_if); die Soll-Führung (C-FAC-01) bleibt Radweg, Flag `parallel_cycle_route` in c05.

km je Ebene: bis RSV (P-DIR-01 ≤ 1.1) 4.0, bis HAUPT (P-DIR-01 ≤ 1.2) 18.7, bis BASIS (P-DIR-01 ≤ 1.3) 2.8

### Stichproben (30, über Bezirke verteilt, Seed 42)

| segment_id | Straße | Bezirk | Ebene | Umweg | Anteil im Puffer | Prüfen |
| --- | --- | --- | --- | ---: | ---: | --- |
| `seg_06e88d159e9da665` | Elbchaussee | Altona | BASIS | 0.64 | 0.65 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559284,5933429]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546412/9.894729) · [OSM](https://www.openstreetmap.org/?mlat=53.546412&mlon=9.894729#map=18/53.546412/9.894729) |
| `seg_a958649272929106` | Palmaille | Altona | BASIS | 0.59 | 0.85 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561950,5933458]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546356/9.934966) · [OSM](https://www.openstreetmap.org/?mlat=53.546356&mlon=9.934966#map=18/53.546356/9.934966) |
| `seg_0ad1bd8b0615e9c0` | Bergedorfer Straße | Bergedorf | HAUPT | 0.29 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578532,5929211]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.505976/10.184100) · [OSM](https://www.openstreetmap.org/?mlat=53.505976&mlon=10.184100#map=18/53.505976/10.184100) |
| `seg_443d16c9cdcf28e6` | Bergedorfer Straße | Bergedorf | HAUPT | 0.72 | 0.72 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577718,5929856]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.511893/10.171988) · [OSM](https://www.openstreetmap.org/?mlat=53.511893&mlon=10.171988#map=18/53.511893/10.171988) |
| `seg_47734e8faecd21eb` | Bergedorfer Straße | Bergedorf | HAUPT | 1.08 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577917,5929637]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.509899/10.174937) · [OSM](https://www.openstreetmap.org/?mlat=53.509899&mlon=10.174937#map=18/53.509899/10.174937) |
| `seg_a583884900cf4b67` | Bergedorfer Straße | Bergedorf | HAUPT | 1.11 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576434,5930686]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.519542/10.152840) · [OSM](https://www.openstreetmap.org/?mlat=53.519542&mlon=10.152840#map=18/53.519542/10.152840) |
| `seg_175d0a5ec4e33d9f` | Schleswiger Damm | Eimsbüttel | HAUPT | 0.81 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561185,5943080]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.632923/9.925300) · [OSM](https://www.openstreetmap.org/?mlat=53.632923&mlon=9.925300#map=18/53.632923/9.925300) |
| `seg_5a902a13afa92e28` | Oldesloer Straße | Eimsbüttel | BASIS | 1.04 | 0.51 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562533,5944914]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.649246/9.946054) · [OSM](https://www.openstreetmap.org/?mlat=53.649246&mlon=9.946054#map=18/53.649246/9.946054) |
| `seg_d6ff58174650493a` | Kieler Straße | Eimsbüttel | BASIS | 0.86 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561176,5938851]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594918/9.924347) · [OSM](https://www.openstreetmap.org/?mlat=53.594918&mlon=9.924347#map=18/53.594918/9.924347) |
| `seg_1cf536f45e4682d6` | Köhlbrandbrücke | Hamburg-Mitte | HAUPT | 1.05 | 0.77 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562368,5930709]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.521608/9.940722) · [OSM](https://www.openstreetmap.org/?mlat=53.521608&mlon=9.940722#map=18/53.521608/9.940722) |
| `seg_202617af3180ff12` | Finkenwerder Straße | Hamburg-Mitte | HAUPT | 1.02 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560852,5929995]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.515367/9.917721) · [OSM](https://www.openstreetmap.org/?mlat=53.515367&mlon=9.917721#map=18/53.515367/9.917721) |
| `seg_2e1ad1ca12a9264a` | Köhlbrandbrücke | Hamburg-Mitte | HAUPT | 1.00 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563989,5930157]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.516445/9.965058) · [OSM](https://www.openstreetmap.org/?mlat=53.516445&mlon=9.965058#map=18/53.516445/9.965058) |
| `seg_51622f2841c3ee61` | Bergedorfer Straße | Hamburg-Mitte | RSV | 0.98 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575130,5931546]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.527454/10.133385) · [OSM](https://www.openstreetmap.org/?mlat=53.527454&mlon=10.133385#map=18/53.527454/10.133385) |
| `seg_55ab00e11d6c0ed2` | Bergedorfer Straße | Hamburg-Mitte | HAUPT | 1.14 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575252,5931450]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.526580/10.135203) · [OSM](https://www.openstreetmap.org/?mlat=53.526580&mlon=10.135203#map=18/53.526580/10.135203) |
| `seg_8a9636415b35c5cd` | Finkenwerder Straße | Hamburg-Mitte | HAUPT | 0.68 | 0.56 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561448,5930218]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.517300/9.926746) · [OSM](https://www.openstreetmap.org/?mlat=53.517300&mlon=9.926746#map=18/53.517300/9.926746) |
| `seg_a10a4b863f3343c4` | Unterer Landweg | Hamburg-Mitte | HAUPT | 1.04 | 0.98 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572752,5930416]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.517637/10.097260) · [OSM](https://www.openstreetmap.org/?mlat=53.517637&mlon=10.097260#map=18/53.517637/10.097260) |
| `seg_b2a715647569db2f` | Mengestraße | Hamburg-Mitte | HAUPT | 0.82 | 0.70 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565836,5928406]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.500488/9.992546) · [OSM](https://www.openstreetmap.org/?mlat=53.500488&mlon=9.992546#map=18/53.500488/9.992546) |
| `seg_b64953bd10ba286d` | Schiffbeker Weg | Hamburg-Mitte | HAUPT | 0.79 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574075,5935187]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560331/10.118338) · [OSM](https://www.openstreetmap.org/?mlat=53.560331&mlon=10.118338#map=18/53.560331/10.118338) |
| `seg_ffbd17389dfa3224` | Finkenwerder Straße | Hamburg-Mitte | HAUPT | 0.78 | 0.52 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561455,5930198]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.517119/9.926861) · [OSM](https://www.openstreetmap.org/?mlat=53.517119&mlon=9.926861#map=18/53.517119/9.926861) |
| `seg_0a0ad19b257180cb` | Hebebrandstraße | Hamburg-Nord | HAUPT | 1.00 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568409,5940379]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607756/10.033940) · [OSM](https://www.openstreetmap.org/?mlat=53.607756&mlon=10.033940#map=18/53.607756/10.033940) |
| `seg_7a44c575a4d82113` | Zeppelinstraße | Hamburg-Nord | RSV | 0.46 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566690,5942504]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.627080/10.008418) · [OSM](https://www.openstreetmap.org/?mlat=53.627080&mlon=10.008418#map=18/53.627080/10.008418) |
| `seg_b7efe5fa97c56cfd` | Tangstedter Landstraße | Hamburg-Nord | HAUPT | 0.93 | 0.93 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567374,5945633]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.655111/10.019442) · [OSM](https://www.openstreetmap.org/?mlat=53.655111&mlon=10.019442#map=18/53.655111/10.019442) |
| `seg_fcfec9781d955dd0` | Zeppelinstraße | Hamburg-Nord | RSV | 0.97 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566716,5942679]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.628646/10.008854) · [OSM](https://www.openstreetmap.org/?mlat=53.628646&mlon=10.008854#map=18/53.628646/10.008854) |
| `seg_36963b9a44130647` | Vollhöfner Weiden | Harburg | HAUPT | 0.67 | 0.75 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559833,5929787]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.513611/9.902315) · [OSM](https://www.openstreetmap.org/?mlat=53.513611&mlon=9.902315#map=18/53.513611/9.902315) |
| `seg_c27ae69f0fb44227` | Brücke des 17. Juni | Harburg | RSV | 1.00 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566076,5925403]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.473468/9.995526) · [OSM](https://www.openstreetmap.org/?mlat=53.473468&mlon=9.995526#map=18/53.473468/9.995526) |
| `seg_10f50665dbf00346` | Höltigbaum | Wandsbek | HAUPT | 0.92 | 0.92 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577721,5941272]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.614488/10.174882) · [OSM](https://www.openstreetmap.org/?mlat=53.614488&mlon=10.174882#map=18/53.614488/10.174882) |
| `seg_4223a93c98726256` | Wagnerstraße | Wandsbek | HAUPT | 0.87 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569122,5935991]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.568229/10.043749) · [OSM](https://www.openstreetmap.org/?mlat=53.568229&mlon=10.043749#map=18/53.568229/10.043749) |
| `seg_7592dcaf36129639` | Lesserstraße | Wandsbek | HAUPT | 0.35 | 0.96 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571334,5937999]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.585981/10.077605) · [OSM](https://www.openstreetmap.org/?mlat=53.585981&mlon=10.077605#map=18/53.585981/10.077605) |
| `seg_a7fde625acc5ed42` | Alte Landstraße | Wandsbek | BASIS | 0.12 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571324,5945179]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.650505/10.079094) · [OSM](https://www.openstreetmap.org/?mlat=53.650505&mlon=10.079094#map=18/53.650505/10.079094) |
| `seg_fb1316612ef23953` | Alte Landstraße | Wandsbek | HAUPT | 0.93 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571355,5945057]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.649409/10.079532) · [OSM](https://www.openstreetmap.org/?mlat=53.649409&mlon=10.079532#map=18/53.649409/10.079532) |

## Grenzen

- Begleitende Radwege und ihre Seite kommen aus dem Radgraphen (C-GRAPH-06); fehlt die Zuordnung, entscheidet der Tag an der Straße.
- Parallelroute: Netzweg zwischen den Lotfußpunkten der Abschnittsenden auf den Soll-Kanten der Ebene, ohne Zu- und Abfahrt; sehr kurze Abschnitte werden damit eher großzügig bewertet.
- Ohne jede OSM-Angabe bleibt `separated_cycle_track_present` unbekannt (S-FEAT-10), die Ist-Führung ist Mischverkehr (C-FAC-05).

Quellen: OpenStreetMap-Mitwirkende (ODbL); Freie und Hansestadt Hamburg, Fahrradstraßen (dl-de/by-2.0).
