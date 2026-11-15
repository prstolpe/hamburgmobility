# Ist-Führung und Parallelroute je Abschnitt (Stufe c03b)

Erzeugt 2026-11-15T01:54:19+00:00 mit pipeline/c03b_ist_facility.py · rules.yaml 0.22.0 · cycling_rules.yaml 0.12.0 · nicht amtlicher Entwurf. Regeln S-FEAT-13 und S-FEAT-11 (Review 2026-11 F26/E9, F21), source_type assumption, status draft.

Eine Ist-Führung je Abschnitt nach den Regeln von C-FAC-05 (Fahrradstraße, Radweg mit begleitenden Radwegen je Seite, Streifen, Sharrow/Busspur, keine). Die Prinzipienbewertung (c04, C-PRI-02), die Führungsform (c05, C-FAC-05) und die Diskrepanz (s08, D-DES-01/D-USE-01) lesen sie; bis rules.yaml 0.19.0 gab es drei Definitionen. `separated_cycle_track_present` = Ist-Führung Radweg je Seite oder Zweirichtungsradweg; unbekannt, wenn die Ist-Klasse „keine“ nur aus fehlenden OSM-Angaben folgt (S-FEAT-10).

## Kurzfassung

- 34 702 klassifizierte Abschnitte, 4 387 km. Baulicher Radweg: ja 1 054 km, nein 1 670 km, unbekannt 1 664 km.
- Radweg-Tag an der Straße (S-FEAT-10 `cycle_track_tag`), aber weder begleitender Radweg noch Radweg in der Straßenlinie im Radgraphen (Flag `track_tag_only`): 1 592 Abschnitte, 107.7 km. Sie zählen nach C-FAC-05 überall als Radweg; bis cycling_rules 0.10.0 zählte c04 sie als Fahrbahnführung. Prüfliste unten.
- Abweichung von der früheren Radgraph-Definition (C-PRI-02 bis cycling_rules 0.10.0): 220.7 km; davon Radweg-Tag ohne Radgraph 104.6 km, begleitende Zweirichtungsradwege auf beiden Seiten (E9: jetzt Radweg je Seite) 73.6 km.
- Abweichung vom Radweg-Tag allein (S-FEAT-10 bis rules.yaml 0.19.0): Tag nein/unbekannt, Ist Radweg 163.8 km (begleitender Radweg im Radgraphen); Tag ja, Ist kein Radweg 0.9 km (Fahrradstraße geht vor).
- Parallelroute (S-FEAT-11, nur Soll-Radnetz RSV/HAUPT/BASIS mit Umweg ≤ P-DIR-01; geprüft für GOW50): 87.4 von 242.4 km; ohne baulichen Radweg 28.1 von 55.5 km.
- Laufzeit: Eingänge 0 s, Ist-Führung 1 s, Parallelroute 4 s.

## km je Ist-Führung und Straßenkategorie

| Ist-Führung | SW | GOW50 | GOW30 | ETW30 | ETW_ERF | gesamt |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Radweg je Seite | 0.3 | 128.0 | 301.6 | 289.4 | 0.3 | 719.6 |
| Zweirichtungsradweg | 10.0 | 58.9 | 93.9 | 170.9 | 0.5 | 334.2 |
| Radfahrstreifen | 0.0 | 9.8 | 51.2 | 63.5 | 0.0 | 124.5 |
| Fahrradstraße | 0.0 | 0.0 | 0.6 | 26.0 | 0.0 | 26.6 |
| Mischverkehr | 178.9 | 45.7 | 66.2 | 2 774.5 | 117.2 | 3 182.4 |
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

km je Straßenkategorie: SW 0.3, GOW50 27.2, GOW30 37.4, ETW30 42.7, ETW_ERF 0.0

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
| Bremer Straße | Harburg | GOW30 | 5 | 0.64 |
| Georg-Wilhelm-Straße | Hamburg-Mitte | GOW30 | 3 | 0.64 |
| Zeppelinstraße | Hamburg-Nord | ETW30 | 12 | 0.63 |
| Barmbeker Straße | Hamburg-Nord | GOW30 | 9 | 0.62 |
| Curslacker Neuer Deich | Bergedorf | GOW50 | 11 | 0.62 |
| Stader Straße | Harburg | GOW30 | 4 | 0.61 |
| Kieler Straße | Eimsbüttel | GOW30 | 12 | 0.60 |
| Bremer Straße | Harburg | GOW50 | 4 | 0.57 |
| Sengelmannstraße | Hamburg-Nord | ETW30 | 11 | 0.57 |
| Glinder Weg | Bergedorf | ETW30 | 1 | 0.56 |
| Stapelfelder Straße | Wandsbek | ETW30 | 2 | 0.55 |

Vollständige Liste: `data/interim/ist_facility.parquet`, Spalte `track_tag_only`.

### Stichproben (30, über Bezirke verteilt, Seed 42)

| segment_id | Straße | Bezirk | Kategorie | C-PRI-02 alt | Prüfen |
| --- | --- | --- | --- | --- | --- |
| `seg_10b9a464ef2097b9` | Bahrenfelder Chaussee | Altona | GOW30 | Radfahrstreifen | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559531,5936152]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.570852/9.898970) · [OSM](https://www.openstreetmap.org/?mlat=53.570852&mlon=9.898970#map=18/53.570852/9.898970) |
| `seg_2e08b757a509b726` | Behringstraße / Walderseestraße | Altona | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559427,5934650]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.557366/9.897114) · [OSM](https://www.openstreetmap.org/?mlat=53.557366&mlon=9.897114#map=18/53.557366/9.897114) |
| `seg_79d67627fca6303f` | Max-Brauer-Allee | Altona | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562830,5934807]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558378/9.948519) · [OSM](https://www.openstreetmap.org/?mlat=53.558378&mlon=9.948519#map=18/53.558378/9.948519) |
| `seg_590116c18c90e3b8` | Sander Damm | Bergedorf | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579760,5927540]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.490777/10.202190) · [OSM](https://www.openstreetmap.org/?mlat=53.490777&mlon=10.202190#map=18/53.490777/10.202190) |
| `seg_62ea090c4e38f954` | Bergedorfer Straße | Bergedorf | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579788,5927576]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.491094/10.202616) · [OSM](https://www.openstreetmap.org/?mlat=53.491094&mlon=10.202616#map=18/53.491094/10.202616) |
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
| `seg_501ee8d176053060` | Deelböge | Hamburg-Nord | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565335,5939865]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.603532/9.987383) · [OSM](https://www.openstreetmap.org/?mlat=53.603532&mlon=9.987383#map=18/53.603532/9.987383) |
| `seg_5268d2671e5a349a` | Barmbeker Straße | Hamburg-Nord | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566901,5938447]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.590587/10.010746) · [OSM](https://www.openstreetmap.org/?mlat=53.590587&mlon=10.010746#map=18/53.590587/10.010746) |
| `seg_b672bcd7b40bc618` | Rümkerstraße | Hamburg-Nord | ETW30 | Radfahrstreifen | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569492,5939792]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.602338/10.050182) · [OSM](https://www.openstreetmap.org/?mlat=53.602338&mlon=10.050182#map=18/53.602338/10.050182) |
| `seg_de19570f67b78a7f` | Winterhuder Marktplatz | Hamburg-Nord | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566157,5938880]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594571/9.999601) · [OSM](https://www.openstreetmap.org/?mlat=53.594571&mlon=9.999601#map=18/53.594571/9.999601) |
| `seg_0c15919c4aeab19b` | Maldfeldstraße | Harburg | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562190,5920603]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.430798/9.936042) · [OSM](https://www.openstreetmap.org/?mlat=53.430798&mlon=9.936042#map=18/53.430798/9.936042) |
| `seg_388993c8ca017a0b` | Vollhöfner Weiden | Harburg | GOW50 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559564,5929264]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.508947/9.898160) · [OSM](https://www.openstreetmap.org/?mlat=53.508947&mlon=9.898160#map=18/53.508947/9.898160) |
| `seg_95163000739aef4a` | Aluminiumstraße | Harburg | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558757,5929762]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.513509/9.886092) · [OSM](https://www.openstreetmap.org/?mlat=53.513509&mlon=9.886092#map=18/53.513509/9.886092) |
| `seg_b0ccb7fd45c6e9ce` | Am Pulverhof | Wandsbek | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575138,5939004]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594482/10.135289) · [OSM](https://www.openstreetmap.org/?mlat=53.594482&mlon=10.135289#map=18/53.594482/10.135289) |
| `seg_d88ae5a141d9317d` | (ohne Namen) | Wandsbek | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572648,5938861]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.593547/10.097646) · [OSM](https://www.openstreetmap.org/?mlat=53.593547&mlon=10.097646#map=18/53.593547/10.097646) |
| `seg_ead96a353f63eef6` | August-Krogmann-Straße | Wandsbek | GOW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573890,5940416]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607351/10.116770) · [OSM](https://www.openstreetmap.org/?mlat=53.607351&mlon=10.116770#map=18/53.607351/10.116770) |
| `seg_f2ee076a38868863` | (ohne Namen) | Wandsbek | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573894,5940421]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607391/10.116840) · [OSM](https://www.openstreetmap.org/?mlat=53.607391&mlon=10.116840#map=18/53.607391/10.116840) |
| `seg_44b6a7d755189654` | Hauptstraße | nan | ETW30 | Mischverkehr | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553296,5924320]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.465182/9.802816) · [OSM](https://www.openstreetmap.org/?mlat=53.465182&mlon=9.802816#map=18/53.465182/9.802816) |

## Parallelroute an Abschnitten ohne baulichen Radweg (S-FEAT-11)

D-DES-01 zählt „kein baulicher Radweg“ dort nur mit dem Gewicht 0,5 (severity_if); die Soll-Führung (C-FAC-01) bleibt Radweg, Flag `parallel_cycle_route` in c05.

km je Ebene: bis RSV (P-DIR-01 ≤ 1.1) 4.2, bis HAUPT (P-DIR-01 ≤ 1.2) 20.8, bis BASIS (P-DIR-01 ≤ 1.3) 3.0

### Stichproben (30, über Bezirke verteilt, Seed 42)

| segment_id | Straße | Bezirk | Ebene | Umweg | Anteil im Puffer | Prüfen |
| --- | --- | --- | --- | ---: | ---: | --- |
| `seg_06e88d159e9da665` | Elbchaussee | Altona | BASIS | 0.64 | 0.65 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559284,5933429]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546412/9.894729) · [OSM](https://www.openstreetmap.org/?mlat=53.546412&mlon=9.894729#map=18/53.546412/9.894729) |
| `seg_1e9767c6996b0139` | Ebertallee | Altona | BASIS | 0.23 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559007,5936362]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572801/9.891106) · [OSM](https://www.openstreetmap.org/?mlat=53.572801&mlon=9.891106#map=18/53.572801/9.891106) |
| `seg_777ab7e6564ee62a` | Barnerstraße | Altona | HAUPT | 1.04 | 0.97 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561634,5934609]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.556741/9.930419) · [OSM](https://www.openstreetmap.org/?mlat=53.556741&mlon=9.930419#map=18/53.556741/9.930419) |
| `seg_e6b3d2a344280e51` | Holstenstraße | Altona | HAUPT | 1.01 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562722,5935151]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.561483/9.946957) · [OSM](https://www.openstreetmap.org/?mlat=53.561483&mlon=9.946957#map=18/53.561483/9.946957) |
| `seg_2823724f8c66aa4a` | Lohbrügger Landstraße | Bergedorf | HAUPT | 1.00 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578876,5929057]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.504539/10.189257) · [OSM](https://www.openstreetmap.org/?mlat=53.504539&mlon=10.189257#map=18/53.504539/10.189257) |
| `seg_2ecda096c1a969aa` | Bergedorfer Straße | Bergedorf | HAUPT | 1.02 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578266,5929389]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.507615/10.180138) · [OSM](https://www.openstreetmap.org/?mlat=53.507615&mlon=10.180138#map=18/53.507615/10.180138) |
| `seg_443d16c9cdcf28e6` | Bergedorfer Straße | Bergedorf | HAUPT | 0.72 | 0.72 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577718,5929856]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.511893/10.171988) · [OSM](https://www.openstreetmap.org/?mlat=53.511893&mlon=10.171988#map=18/53.511893/10.171988) |
| `seg_f1ec7b159afdf47b` | Bergedorfer Straße | Bergedorf | RSV | 0.80 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575314,5931430]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.526386/10.136129) · [OSM](https://www.openstreetmap.org/?mlat=53.526386&mlon=10.136129#map=18/53.526386/10.136129) |
| `seg_175d0a5ec4e33d9f` | Schleswiger Damm | Eimsbüttel | HAUPT | 0.81 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561185,5943080]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.632923/9.925300) · [OSM](https://www.openstreetmap.org/?mlat=53.632923&mlon=9.925300#map=18/53.632923/9.925300) |
| `seg_c715b7abcecb27a3` | Schleswiger Damm | Eimsbüttel | BASIS | 0.73 | 0.73 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561028,5943283]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.634768/9.922975) · [OSM](https://www.openstreetmap.org/?mlat=53.634768&mlon=9.922975#map=18/53.634768/9.922975) |
| `seg_efea8515f1a1109c` | Schleswiger Damm | Eimsbüttel | BASIS | 1.28 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561000,5943308]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.634995/9.922550) · [OSM](https://www.openstreetmap.org/?mlat=53.634995&mlon=9.922550#map=18/53.634995/9.922550) |
| `seg_168a6785705cc66d` | Brooktorkai | Hamburg-Mitte | HAUPT | 1.08 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566424,5933448]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.545721/10.002467) · [OSM](https://www.openstreetmap.org/?mlat=53.545721&mlon=10.002467#map=18/53.545721/10.002467) |
| `seg_1cf536f45e4682d6` | Köhlbrandbrücke | Hamburg-Mitte | HAUPT | 1.05 | 0.77 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562368,5930709]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.521608/9.940722) · [OSM](https://www.openstreetmap.org/?mlat=53.521608&mlon=9.940722#map=18/53.521608/9.940722) |
| `seg_2372da720d69487d` | – | Hamburg-Mitte | RSV | 0.94 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568009,5932165]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.533990/10.026116) · [OSM](https://www.openstreetmap.org/?mlat=53.533990&mlon=10.026116#map=18/53.533990/10.026116) |
| `seg_50069583a787b87d` | Bergedorfer Straße | Hamburg-Mitte | RSV | 0.91 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575007,5931612]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.528066/10.131540) · [OSM](https://www.openstreetmap.org/?mlat=53.528066&mlon=10.131540#map=18/53.528066/10.131540) |
| `seg_51622f2841c3ee61` | Bergedorfer Straße | Hamburg-Mitte | RSV | 0.98 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575130,5931546]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.527454/10.133385) · [OSM](https://www.openstreetmap.org/?mlat=53.527454&mlon=10.133385#map=18/53.527454/10.133385) |
| `seg_80864fa15075c308` | Finkenwerder Straße | Hamburg-Mitte | HAUPT | 0.96 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560581,5929903]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.514572/9.913621) · [OSM](https://www.openstreetmap.org/?mlat=53.514572&mlon=9.913621#map=18/53.514572/9.913621) |
| `seg_967805f375c1aa66` | Barcastraße | Hamburg-Mitte | RSV | 0.77 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567220,5935102]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560489/10.014847) · [OSM](https://www.openstreetmap.org/?mlat=53.560489&mlon=10.014847#map=18/53.560489/10.014847) |
| `seg_a15941839deafe7a` | Rennbahnstraße | Hamburg-Mitte | BASIS | 0.09 | 0.72 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571843,5934471]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.554207/10.084484) · [OSM](https://www.openstreetmap.org/?mlat=53.554207&mlon=10.084484#map=18/53.554207/10.084484) |
| `seg_a4b4f2ff7b7f96ac` | – | Hamburg-Mitte | HAUPT | 0.66 | 0.88 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571875,5933462]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.545133/10.084731) · [OSM](https://www.openstreetmap.org/?mlat=53.545133&mlon=10.084731#map=18/53.545133/10.084731) |
| `seg_0a0ad19b257180cb` | Hebebrandstraße | Hamburg-Nord | HAUPT | 1.00 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568409,5940379]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607756/10.033940) · [OSM](https://www.openstreetmap.org/?mlat=53.607756&mlon=10.033940#map=18/53.607756/10.033940) |
| `seg_7a44c575a4d82113` | Zeppelinstraße | Hamburg-Nord | RSV | 0.46 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566690,5942504]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.627080/10.008418) · [OSM](https://www.openstreetmap.org/?mlat=53.627080&mlon=10.008418#map=18/53.627080/10.008418) |
| `seg_b7efe5fa97c56cfd` | Tangstedter Landstraße | Hamburg-Nord | HAUPT | 0.93 | 0.93 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567374,5945633]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.655111/10.019442) · [OSM](https://www.openstreetmap.org/?mlat=53.655111&mlon=10.019442#map=18/53.655111/10.019442) |
| `seg_fcfec9781d955dd0` | Zeppelinstraße | Hamburg-Nord | RSV | 0.97 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566716,5942679]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.628646/10.008854) · [OSM](https://www.openstreetmap.org/?mlat=53.628646&mlon=10.008854#map=18/53.628646/10.008854) |
| `seg_36963b9a44130647` | Vollhöfner Weiden | Harburg | HAUPT | 0.67 | 0.75 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559833,5929787]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.513611/9.902315) · [OSM](https://www.openstreetmap.org/?mlat=53.513611&mlon=9.902315#map=18/53.513611/9.902315) |
| `seg_c27ae69f0fb44227` | Brücke des 17. Juni | Harburg | RSV | 1.00 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566076,5925403]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.473468/9.995526) · [OSM](https://www.openstreetmap.org/?mlat=53.473468&mlon=9.995526#map=18/53.473468/9.995526) |
| `seg_10f50665dbf00346` | Höltigbaum | Wandsbek | HAUPT | 0.92 | 0.92 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577721,5941272]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.614488/10.174882) · [OSM](https://www.openstreetmap.org/?mlat=53.614488&mlon=10.174882#map=18/53.614488/10.174882) |
| `seg_4223a93c98726256` | Wagnerstraße | Wandsbek | HAUPT | 0.87 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569122,5935991]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.568229/10.043749) · [OSM](https://www.openstreetmap.org/?mlat=53.568229&mlon=10.043749#map=18/53.568229/10.043749) |
| `seg_748caa36806b869f` | Hammer Straße | Wandsbek | HAUPT | 0.48 | 0.97 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570839,5935081]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.559824/10.069460) · [OSM](https://www.openstreetmap.org/?mlat=53.559824&mlon=10.069460#map=18/53.559824/10.069460) |
| `seg_fadbfc5eea28067e` | August-Krogmann-Straße | Wandsbek | BASIS | 0.98 | 1.00 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573569,5941919]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.620897/10.112286) · [OSM](https://www.openstreetmap.org/?mlat=53.620897&mlon=10.112286#map=18/53.620897/10.112286) |

## Grenzen

- Begleitende Radwege und ihre Seite kommen aus dem Radgraphen (C-GRAPH-06); fehlt die Zuordnung, entscheidet der Tag an der Straße.
- Parallelroute: Netzweg zwischen den Lotfußpunkten der Abschnittsenden auf den Soll-Kanten der Ebene, ohne Zu- und Abfahrt; sehr kurze Abschnitte werden damit eher großzügig bewertet.
- Ohne jede OSM-Angabe bleibt `separated_cycle_track_present` unbekannt (S-FEAT-10), die Ist-Führung ist Mischverkehr (C-FAC-05).

Quellen: OpenStreetMap-Mitwirkende (ODbL); Freie und Hansestadt Hamburg, Fahrradstraßen (dl-de/by-2.0).
