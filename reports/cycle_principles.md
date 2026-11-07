# Fünf Prinzipien: Bewertung des Soll-Radnetzes (Stufe c04)

Erzeugt 2026-11-07T14:00:52+00:00 mit pipeline/c04_principles.py · cycling_rules.yaml 0.7.0 · nicht amtlicher Entwurf. Alle Bewertungsregeln (C-PRI-01…16) und die Gewichte sind Annahmen (source_type assumption, status draft) und vor fachlicher Nutzung zu prüfen.

**score_ist** bewertet den heutigen Zustand der Soll-Route, **score_soll** den Zustand nach regelkonformem Ausbau (Führung nach Trennungsmatrix, Sollbreite, geschlossene Decke, Beleuchtung). Die Differenz ist der Handlungsbedarf. Fehlende Daten senken die confidence, nicht den Score.

## Kurzfassung

- RSV: 61 km, Score Ist 0.56 → Soll 0.68
- HAUPT: 1 837 km, Score Ist 0.67 → Soll 0.77
- BASIS: 1 055 km, Score Ist 0.78 → Soll 0.83
- Führung entspricht heute der Trennungsmatrix auf 49 % der Netzlänge mit bekannter Führung (RSV/HAUPT: 26 %).
- 5001 Routen bewertet; mittlerer Handlungsbedarf (score_soll − score_ist) 0.06, confidence: high 1871, medium 3130, low 0.
- Nicht bewertbar mangels Daten: P-SAF-02 (Knotentypen erst mit Prompt 20 (pipeline/c07_junctions.py)), P-COM-03 (kein Höhenmodell geladen (sources.yaml laserscan ohne Abruf)), P-ATT-02 (keine Lärmkarte (sources.yaml noise_maps ohne Endpunkt, Entscheidung 2026-11-06)).

## Datenlage je Prüfung

Anteil der Länge des Soll-Netzes (RSV, HAUPT, BASIS) mit Wert, unter den Kanten, für die die Prüfung anwendbar ist.

| Prüfung | Prinzip | Datengrundlage | anwendbar (km) | mit Wert |
| --- | --- | --- | ---: | ---: |
| P-COH-01 | Zusammenhang | c03 Maschen | 2 952 | 100 % |
| P-COH-02 | Zusammenhang | Soll-Netz | 2 950 | 100 % |
| P-COH-04 | Zusammenhang | Ist-Führung entlang der Route | 2 950 | 100 % |
| P-DIR-01 | Direktheit | Radgraph (Länge) | 2 950 | 99 % |
| P-DIR-02 | Direktheit | OSM-LSA, Vorfahrt C-GRAPH-05 | 2 950 | 100 % |
| P-DIR-03 | Direktheit | wie P-DIR-02 | 1 898 | 100 % |
| P-SAF-01 | Sicherheit | Ist-Führung (C-PRI-02), Trennungsmatrix | 2 895 | 100 % |
| P-SAF-02 | Sicherheit | – | 2 952 | 0 % |
| P-SAF-03 | Sicherheit | OSM lit | 2 952 | 85 % |
| P-SAF-04 | Sicherheit | Unfallatlas | 2 952 | 100 % |
| P-COM-01 | Komfort | OSM width/cycleway:width | 1 273 | 11 % |
| P-COM-02 | Komfort | OSM surface | 2 952 | 96 % |
| P-COM-03 | Komfort | – | 2 952 | 0 % |
| P-ATT-01 | Attraktivität | ALKIS, OSM-Bäume | 2 952 | 100 % |
| P-ATT-02 | Attraktivität | – | 2 952 | 0 % |
| P-ATT-03 | Attraktivität | DTV 2019 (HVS) | 2 952 | 100 % |

## Netzkennzahlen je Kategorie

Längengewichtete Mittel über die Kanten der Kategorie (Kantenwerte für Direktheit und Zusammenhang aus der Hauptroute der Kante).

| Kategorie | km | Zusammenhang Ist / Soll | Direktheit Ist / Soll | Sicherheit Ist / Soll | Komfort Ist / Soll | Attraktivität Ist / Soll | Gesamt Ist / Soll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| RSV | 61 | 0.33 / 0.35 | 0.62 / 0.62 | 0.68 / 0.79 | 0.46 / 1.00 | 0.63 / 0.63 | 0.56 / 0.68 |
| HAUPT | 1 837 | 0.68 / 0.71 | 0.66 / 0.66 | 0.64 / 0.82 | 0.69 / 1.00 | 0.70 / 0.70 | 0.67 / 0.77 |
| BASIS | 1 055 | 0.78 / 0.79 | 0.81 / 0.81 | 0.75 / 0.82 | 0.87 / 1.00 | 0.71 / 0.71 | 0.78 / 0.83 |

## Zusammenhang (P-COH)

**P-COH-01 Maschenweite** (aus c03, cycle_mesh_gaps.parquet):

| Ebene | Höchstweite | zu große Maschen | Seite Median | Seite max |
| --- | ---: | ---: | ---: | ---: |
| HAUPT | 600 m | 33 | 1 042 m | 4 966 m |
| BASIS | 300 m | 410 | 410 m | 4 071 m |

**P-COH-02 Komponenten** (je Ebene mit höheren Ebenen):

| Ebene | Komponenten | Anteil größte Komponente (Länge) |
| --- | ---: | ---: |
| RSV | 6 | 25 % |
| HAUPT | 1 | 100 % |
| BASIS | 1 | 100 % |

**P-COH-03 Abdeckung** (Ziele höchstens 300 m vom RSV/HAUPT-Netz; Zentren fehlen, kein Datensatz):

| Ziele | Anzahl | abgedeckt |
| --- | ---: | ---: |
| Schulen (OSM) | 557 | 95 % |
| Schnellbahnhalte | 375 | 99 % |
| Hochschulen (OSM university) | 41 | 100 % |

**P-COH-04 Kontinuität:** Wechsel der Ist-Führung je km (Median über Routen) 1.14, Soll (Führung und Kategorie) 0.00; Schwelle 1.0 je km (C-PRI-12).

## Direktheit (P-DIR)

**P-DIR-01 Umwegfaktor, Netzstichprobe** (C-PRI-04): je Kategorie 200 OD-Paare, Seed 42, Knoten der größten Komponente der Ebene (mit höheren Ebenen), Luftlinie im Band trip_length_km. Netzweg auf der Ebene gegen kürzesten Weg auf allen befahrbaren Kanten (Länge).

| Kategorie | Band (km) | Paare | ohne Weg | Median | 90-%-Wert | Schwelle | Anteil ≤ Schwelle |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RSV | 5–15 | 200 | 0 | 1.13 | 1.16 | 1.1 | 39 % |
| HAUPT | 2–3 | 200 | 0 | 1.14 | 2.12 | 1.2 | 59 % |
| BASIS | 1–2 | 200 | 0 | 1.07 | 2.09 | 1.3 | 79 % |

**Je Route** (Median über Routen der Kategorie; Halte nach C-PRI-05, Soll = Ist bis Prompt 20):

| Kategorie | Routen | Umwegfaktor | Halte/km | Schwelle Halte | Zeitverlust s/km | Schwelle s/km |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RSV | 21 | 1.08 | 1.7 | 0.5 | 22 | 30 |
| HAUPT | 2010 | 1.10 | 1.1 | 1.0 | 11 | 30 |
| BASIS | 2970 | 1.00 | 0.0 | 2.0 | 0 | – |

## Sicherheit (P-SAF)

**P-SAF-01 Ist-Führung gegen Soll-Führung** (km, Kanten RSV/HAUPT/BASIS):

| Ist \ Soll | Radfahrstreifen | Fahrradstraße | Mischverkehr | eigener Weg | Radweg je Seite | unbekannt |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Radfahrstreifen | 17 | 29 | 16 | 0 | 23 | 0 |
| Fahrradstraße | 0 | 18 | 2 | 0 | 0 | 0 |
| Mischverkehr | 15 | 957 | 612 | 0 | 47 | 41 |
| eigener Weg | 0 | 0 | 0 | 414 | 0 | 0 |
| Radweg je Seite | 58 | 100 | 46 | 0 | 216 | 7 |
| Zweirichtungsradweg | 24 | 105 | 51 | 11 | 133 | 4 |
| unbekannt | 0 | 0 | 0 | 0 | 0 | 5 |

P-SAF-03 Beleuchtung: OSM lit auf 85 % der Netzlänge bekannt; davon beleuchtet 90 %. P-SAF-04 Unfälle mit Radbeteiligung 2021–2025: 7 608 Unfälle an Kanten des Soll-Netzes (je Kante höchstens 15 m entfernt; nur Summen gespeichert).

## Komfort und Attraktivität (P-COM, P-ATT)

- P-COM-01 Breite: anwendbar auf 1 273 km (ohne Mischverkehr), Breite in OSM auf 11 % davon; von diesen erreichen 20 % die Sollbreite.
- P-COM-02 Belag: bekannt auf 96 %; RSV/HAUPT mit geschlossener Decke 67 %.
- P-ATT-01 Grünanteil im 20-m-Puffer: Median 13 % (Ziel 30 %, ALKIS-Grünflächen und OSM-Bäume).
- P-ATT-03: 326 km des Soll-Netzes liegen an Straßen mit DTV > 15 000.

## Top 30 Routen mit dem größten Handlungsbedarf

Rangfolge nach Handlungsbedarf-km = (score_soll − score_ist) × Länge in km (C-PRI-14), damit lange Routen mit mittlerem Defizit vor sehr kurzen Verdichtungsstücken stehen. S/K: Sicherheit und Komfort Ist → Soll.

| # | Route | Kategorie | km | Ist | Soll | Δ | Δ × km | S | K | confidence | Prüfen |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 1 | Innenstadt (Rathausmarkt) – Umsteigeknoten Neugraben (`rt_ef74f810d825e8b0`) | RSV | 23.8 | 0.58 | 0.71 | 0.13 | 3.16 | 0.66 → 0.78 | 0.37 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563960,5924903]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.469229/9.963550) · [OSM](https://www.openstreetmap.org/?mlat=53.469229&mlon=9.963550#map=18/53.469229/9.963550) |
| 2 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) (`rt_ad15aafddcc3fd36`) | RSV | 20.3 | 0.57 | 0.71 | 0.13 | 2.74 | 0.65 → 0.77 | 0.36 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565304,5924573]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.466099/9.983721) · [OSM](https://www.openstreetmap.org/?mlat=53.466099&mlon=9.983721#map=18/53.466099/9.983721) |
| 3 | Umsteigeknoten Neugraben – Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) (`rt_a1437067c8713aec`) | HAUPT | 16.2 | 0.73 | 0.87 | 0.14 | 2.33 | 0.59 → 0.83 | 0.60 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560451,5929359]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.509694/9.911549) · [OSM](https://www.openstreetmap.org/?mlat=53.509694&mlon=9.911549#map=18/53.509694/9.911549) |
| 4 | Umsteigeknoten Neugraben – Hochschule Technologiezentrum Hamburg-Finkenwerder (`rt_fa57d47917cbb47c`) | HAUPT | 15.3 | 0.73 | 0.87 | 0.14 | 2.16 | 0.59 → 0.83 | 0.61 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560443,5928887]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.505453/9.911335) · [OSM](https://www.openstreetmap.org/?mlat=53.505453&mlon=9.911335#map=18/53.505453/9.911335) |
| 5 | Arbeitsplatzschwerpunkt Hamburg-Mitte (263 Tsd. m²) – Arbeitsplatzschwerpunkt Bergedorf (224 Tsd. m²) (`rt_0bf6efc364e62515`) | HAUPT | 14.9 | 0.74 | 0.86 | 0.12 | 1.79 | 0.57 → 0.78 | 0.67 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569158,5931755]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.530157/10.043348) · [OSM](https://www.openstreetmap.org/?mlat=53.530157&mlon=10.043348#map=18/53.530157/10.043348) |
| 6 | Innenstadt (Rathausmarkt) – Hochschule HAW Hamburg Energie Campus (`rt_ca7a3c7c5d4e1e7b`) | RSV | 20.6 | 0.63 | 0.71 | 0.08 | 1.75 | 0.63 → 0.72 | 0.67 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573885,5932092]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.532542/10.114736) · [OSM](https://www.openstreetmap.org/?mlat=53.532542&mlon=10.114736#map=18/53.532542/10.114736) |
| 7 | Innenstadt (Rathausmarkt) – Hochschule Gebäude D (`rt_b3e5311382ffdee5`) | RSV | 15.3 | 0.61 | 0.72 | 0.11 | 1.74 | 0.68 → 0.77 | 0.42 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565862,5926294]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.481498/9.992496) · [OSM](https://www.openstreetmap.org/?mlat=53.481498&mlon=9.992496#map=18/53.481498/9.992496) |
| 8 | Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) – Arbeitsplatzschwerpunkt Hamburg-Mitte (263 Tsd. m²) (`rt_c9d2a1f475c68304`) | HAUPT | 14.4 | 0.74 | 0.85 | 0.12 | 1.72 | 0.57 → 0.78 | 0.67 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569012,5931948]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.531906/10.041192) · [OSM](https://www.openstreetmap.org/?mlat=53.531906&mlon=10.041192#map=18/53.531906/10.041192) |
| 9 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_3a0535e6b916dd87`) | HAUPT | 12.9 | 0.70 | 0.83 | 0.13 | 1.70 | 0.56 → 0.76 | 0.58 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564309,5933531]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546728/9.970578) · [OSM](https://www.openstreetmap.org/?mlat=53.546728&mlon=9.970578#map=18/53.546728/9.970578) |
| 10 | Innenstadt (Rathausmarkt) – Umsteigeknoten Hamburg-Harburg (`rt_82768bcf84d75ee6`) | RSV | 14.4 | 0.62 | 0.72 | 0.10 | 1.50 | 0.68 → 0.75 | 0.46 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565881,5930202]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.516617/9.993598) · [OSM](https://www.openstreetmap.org/?mlat=53.516617&mlon=9.993598#map=18/53.516617/9.993598) |
| 11 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Bergedorf (224 Tsd. m²) (`rt_374f83d55ac09da7`) | HAUPT | 12.5 | 0.70 | 0.81 | 0.12 | 1.45 | 0.55 → 0.76 | 0.64 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570263,5931665]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.529197/10.059998) · [OSM](https://www.openstreetmap.org/?mlat=53.529197&mlon=10.059998#map=18/53.529197/10.059998) |
| 12 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Harburg (241 Tsd. m²) (`rt_2a3981f4e8e27282`) | RSV | 13.9 | 0.62 | 0.73 | 0.10 | 1.43 | 0.69 → 0.77 | 0.47 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565713,5926950]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.487410/9.990387) · [OSM](https://www.openstreetmap.org/?mlat=53.487410&mlon=9.990387#map=18/53.487410/9.990387) |
| 13 | Innenstadt (Rathausmarkt) – Umsteigeknoten Bergedorf (`rt_04983fdf6c08b203`) | RSV | 18.6 | 0.64 | 0.72 | 0.08 | 1.40 | 0.63 → 0.72 | 0.73 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573807,5932951]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.540271/10.113752) · [OSM](https://www.openstreetmap.org/?mlat=53.540271&mlon=10.113752#map=18/53.540271/10.113752) |
| 14 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) (`rt_be5550ff43b6bffd`) | HAUPT | 12.0 | 0.69 | 0.81 | 0.11 | 1.37 | 0.55 → 0.75 | 0.65 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570037,5931767]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.530146/10.056618) · [OSM](https://www.openstreetmap.org/?mlat=53.530146&mlon=10.056618#map=18/53.530146/10.056618) |
| 15 | Umsteigeknoten Neugraben – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_1f65359785a52cea`) | HAUPT | 10.2 | 0.73 | 0.86 | 0.13 | 1.36 | 0.62 → 0.82 | 0.58 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559820,5926567]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.484673/9.901500) · [OSM](https://www.openstreetmap.org/?mlat=53.484673&mlon=9.901500#map=18/53.484673/9.901500) |
| 16 | Arbeitsplatzschwerpunkt Hamburg-Mitte (278 Tsd. m²) – Arbeitsplatzschwerpunkt Bergedorf (224 Tsd. m²) (`rt_5be88c5238ed113e`) | HAUPT | 7.1 | 0.66 | 0.84 | 0.19 | 1.34 | 0.45 → 0.81 | 0.50 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572709,5930397]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.517468/10.096597) · [OSM](https://www.openstreetmap.org/?mlat=53.517468&mlon=10.096597#map=18/53.517468/10.096597) |
| 17 | Umsteigeknoten Altona – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_3b5657ead1bad7ac`) | HAUPT | 10.9 | 0.68 | 0.80 | 0.12 | 1.33 | 0.55 → 0.77 | 0.70 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557645,5933527]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.547474/9.870014) · [OSM](https://www.openstreetmap.org/?mlat=53.547474&mlon=9.870014#map=18/53.547474/9.870014) |
| 18 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Nord (307 Tsd. m²) (`rt_e836ce46b7a74785`) | RSV | 12.9 | 0.57 | 0.68 | 0.10 | 1.33 | 0.62 → 0.72 | 0.55 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568340,5938666]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.592369/10.032524) · [OSM](https://www.openstreetmap.org/?mlat=53.592369&mlon=10.032524#map=18/53.592369/10.032524) |
| 19 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) (`rt_ee6414b4e8d872a8`) | HAUPT | 13.3 | 0.59 | 0.69 | 0.10 | 1.27 | 0.56 → 0.72 | 0.70 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563034,5933978]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.550904/9.951430) · [OSM](https://www.openstreetmap.org/?mlat=53.550904&mlon=9.951430#map=18/53.550904/9.951430) |
| 20 | Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) – Arbeitsplatzschwerpunkt Altona (226 Tsd. m²) (`rt_9fe1aad7bdd69990`) | HAUPT | 9.8 | 0.75 | 0.88 | 0.13 | 1.26 | 0.64 → 0.82 | 0.64 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560124,5935043]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560821/9.907711) · [OSM](https://www.openstreetmap.org/?mlat=53.560821&mlon=9.907711#map=18/53.560821/9.907711) |
| 21 | Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) – Arbeitsplatzschwerpunkt Hamburg-Mitte (278 Tsd. m²) (`rt_e3d331b9b5cc9556`) | HAUPT | 6.6 | 0.65 | 0.84 | 0.19 | 1.23 | 0.45 → 0.81 | 0.52 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572886,5930550]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.518820/10.099305) · [OSM](https://www.openstreetmap.org/?mlat=53.518820&mlon=10.099305#map=18/53.518820/10.099305) |
| 22 | Verdichtung HAUPT: Niendorfer Gehege (`rt_c0464578be8fb33b`) | HAUPT | 7.2 | 0.63 | 0.79 | 0.17 | 1.21 | 0.57 → 0.81 | 0.52 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560322,5940791]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.612452/9.911817) · [OSM](https://www.openstreetmap.org/?mlat=53.612452&mlon=9.911817#map=18/53.612452/9.911817) |
| 23 | Hochschule HAW Hamburg Energie Campus – Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) (`rt_aec7fc2a531ca29a`) | HAUPT | 9.6 | 0.76 | 0.88 | 0.12 | 1.18 | 0.60 → 0.81 | 0.61 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577280,5927329]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.489251/10.164766) · [OSM](https://www.openstreetmap.org/?mlat=53.489251&mlon=10.164766#map=18/53.489251/10.164766) |
| 24 | Innenstadt (Rathausmarkt) – Hochschule HAW - Life Sciences - Campus Bergedorf (`rt_b93eca52aba3874d`) | RSV | 17.8 | 0.65 | 0.72 | 0.06 | 1.15 | 0.64 → 0.73 | 0.79 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573537,5933144]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.542046/10.109728) · [OSM](https://www.openstreetmap.org/?mlat=53.542046&mlon=10.109728#map=18/53.542046/10.109728) |
| 25 | Innenstadt (Rathausmarkt) – Hochschule Technologiezentrum Hamburg-Finkenwerder (`rt_9b60c392ebb73835`) | HAUPT | 12.4 | 0.59 | 0.68 | 0.09 | 1.15 | 0.56 → 0.71 | 0.71 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562575,5934064]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.551735/9.944510) · [OSM](https://www.openstreetmap.org/?mlat=53.551735&mlon=9.944510#map=18/53.551735/9.944510) |
| 26 | Umsteigeknoten Hamburg-Harburg – Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) (`rt_463b00cfca1d45be`) | RSV | 7.4 | 0.52 | 0.68 | 0.15 | 1.14 | 0.60 → 0.81 | 0.33 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562896,5925065]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470813/9.947549) · [OSM](https://www.openstreetmap.org/?mlat=53.470813&mlon=9.947549#map=18/53.470813/9.947549) |
| 27 | Verdichtung HAUPT: neben Osdorfer Landstraße (`rt_72d1850ab8acbd17`) | HAUPT | 9.2 | 0.57 | 0.70 | 0.12 | 1.14 | 0.60 → 0.76 | 0.51 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554538,5936526]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.574756/9.823643) · [OSM](https://www.openstreetmap.org/?mlat=53.574756&mlon=9.823643#map=18/53.574756/9.823643) |
| 28 | Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) – Arbeitsplatzschwerpunkt Harburg (241 Tsd. m²) (`rt_a3f51202ca48fa1c`) | RSV | 6.8 | 0.51 | 0.68 | 0.17 | 1.14 | 0.56 → 0.78 | 0.34 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562608,5925087]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.471045/9.943226) · [OSM](https://www.openstreetmap.org/?mlat=53.471045&mlon=9.943226#map=18/53.471045/9.943226) |
| 29 | Verdichtung HAUPT: Little Whistler (`rt_08c9b542408be57e`) | HAUPT | 4.3 | 0.53 | 0.79 | 0.26 | 1.12 | 0.42 → 0.83 | 0.07 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560773,5923351]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.455657/9.915248) · [OSM](https://www.openstreetmap.org/?mlat=53.455657&mlon=9.915248#map=18/53.455657/9.915248) |
| 30 | Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_9978d70cbf7eefbe`) | HAUPT | 6.9 | 0.73 | 0.89 | 0.16 | 1.11 | 0.55 → 0.83 | 0.67 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558090,5932012]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.533804/9.876452) · [OSM](https://www.openstreetmap.org/?mlat=53.533804&mlon=9.876452#map=18/53.533804/9.876452) |

Höchster Δ einer Route (ohne Längengewicht): 0.30; Routen mit Δ ≥ 0,2: 184.

## Karten je Prinzip

![Zusammenhang](cycle_principles_cohesion.png)

![Direktheit](cycle_principles_directness.png)

![Sicherheit](cycle_principles_safety.png)

![Komfort](cycle_principles_comfort.png)

![Attraktivität](cycle_principles_attractiveness.png)

![Handlungsbedarf](cycle_principles_delta.png)

## Gewichts-Sensitivität (±20 %)

Jedes Gewicht einzeln um ±20% verändert, die übrigen anteilig umgelegt (C-PRI-14). Verglichen mit den Basisgewichten: Überschneidung der Top 30 nach Handlungsbedarf-km, Rangkorrelation (Spearman) aller Routen.

| Gewicht | Basis | Variante | Top-Überschneidung | Spearman |
| --- | ---: | ---: | ---: | ---: |
| Zusammenhang | 0.200 | 0.160 | 29/30 | 0.998 |
| Zusammenhang | 0.200 | 0.240 | 30/30 | 0.997 |
| Direktheit | 0.250 | 0.200 | 30/30 | 1.000 |
| Direktheit | 0.250 | 0.300 | 30/30 | 1.000 |
| Sicherheit | 0.300 | 0.240 | 30/30 | 0.996 |
| Sicherheit | 0.300 | 0.360 | 30/30 | 0.997 |
| Komfort | 0.150 | 0.120 | 29/30 | 0.999 |
| Komfort | 0.150 | 0.180 | 29/30 | 0.999 |
| Attraktivität | 0.100 | 0.080 | 30/30 | 1.000 |
| Attraktivität | 0.100 | 0.120 | 30/30 | 1.000 |

Kleinste Überschneidung: 29/30.

## Handlungsbedarf je Bezirk

| Bezirk | Netz-km | Score Ist | Score Soll | Δ |
| --- | ---: | ---: | ---: | ---: |
| Altona | 420 | 0.70 | 0.78 | 0.08 |
| Bergedorf | 193 | 0.73 | 0.82 | 0.09 |
| Eimsbüttel | 354 | 0.70 | 0.78 | 0.08 |
| Hamburg-Mitte | 488 | 0.72 | 0.80 | 0.08 |
| Hamburg-Nord | 410 | 0.70 | 0.78 | 0.08 |
| Harburg | 267 | 0.69 | 0.79 | 0.10 |
| Wandsbek | 820 | 0.71 | 0.80 | 0.08 |

## Stichprobe: 30 zufällige Kanten (Seed 42, nach Bezirk verteilt)

| Kante | Name | Kategorie | Führung Ist → Soll | Breite / Soll | Belag | lit | Score Ist / Soll | Prüfen |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| `ce_0e7da0c5a0df07cd` | Knospenweg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.78 / 0.83 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553463,5936487]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.574521/9.807408) · [OSM](https://www.openstreetmap.org/?mlat=53.574521&mlon=9.807408#map=18/53.574521/9.807408) |
| `ce_3aef5a2940e76ac7` | Pieperweg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.67 / 0.72 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554305,5937212]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.580950/9.820257) · [OSM](https://www.openstreetmap.org/?mlat=53.580950&mlon=9.820257#map=18/53.580950/9.820257) |
| `ce_7ed1488f8e6a3ad0` | Fischers Allee | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.61 / 0.66 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561099,5933658]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.548262/9.922158) · [OSM](https://www.openstreetmap.org/?mlat=53.548262&mlon=9.922158#map=18/53.548262/9.922158) |
| `ce_8da5b1969204a03e` | Bernadottestraße | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.70 / 0.75 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559324,5933741]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.549205/9.895395) · [OSM](https://www.openstreetmap.org/?mlat=53.549205&mlon=9.895395#map=18/53.549205/9.895395) |
| `ce_28e8c38277abe23c` | Ebner-Eschenbach-Weg | BASIS | Mischverkehr → Mischverkehr | – / – | paving_stones | ja | 0.72 / 0.74 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577827,5926541]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.482083/10.172810) · [OSM](https://www.openstreetmap.org/?mlat=53.482083&mlon=10.172810#map=18/53.482083/10.172810) |
| `ce_410783551c7bfd75` | Oberer Landweg | BASIS | Mischverkehr → Mischverkehr | – / – | asphalt | ja | 0.69 / 0.69 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578600,5926851]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.484754/10.184546) · [OSM](https://www.openstreetmap.org/?mlat=53.484754&mlon=10.184546#map=18/53.484754/10.184546) |
| `ce_1aa2495a45888ddb` | Duvenacker | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.72 / 0.80 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560402,5940820]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.612703/9.913036) · [OSM](https://www.openstreetmap.org/?mlat=53.612703&mlon=9.913036#map=18/53.612703/9.913036) |
| `ce_b2ffa67709b37cc8` | Roman-Zeller-Platz | BASIS | Mischverkehr → Mischverkehr | – / – | paving_stones | ja | 0.84 / 0.84 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560129,5944648]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.647140/9.909649) · [OSM](https://www.openstreetmap.org/?mlat=53.647140&mlon=9.909649#map=18/53.647140/9.909649) |
| `ce_c57b913c3deaf7ff` | Hochallee | BASIS | Radfahrstreifen → Mischverkehr | – / 2.25 | asphalt | ja | 0.67 / 0.77 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565250,5937494]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.582237/9.985608) · [OSM](https://www.openstreetmap.org/?mlat=53.582237&mlon=9.985608#map=18/53.582237/9.985608) |
| `ce_c6ac9f215e3f43a7` | Reemstückenkamp | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.71 / 0.76 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560293,5940912]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.613544/9.911392) · [OSM](https://www.openstreetmap.org/?mlat=53.613544&mlon=9.911392#map=18/53.613544/9.911392) |
| `ce_0c77944128eb4d97` | – | HAUPT | eigener Weg → eigener Weg | – / 3.50 | paving_stones | ja | 0.63 / 0.79 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565774,5928717]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.503285/9.991670) · [OSM](https://www.openstreetmap.org/?mlat=53.503285&mlon=9.991670#map=18/53.503285/9.991670) |
| `ce_2291d2ac1d6234df` | – | HAUPT | eigener Weg → eigener Weg | – / 3.50 | paving_stones | ja | 0.71 / 0.87 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564517,5931462]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.528116/9.973289) · [OSM](https://www.openstreetmap.org/?mlat=53.528116&mlon=9.973289#map=18/53.528116/9.973289) |
| `ce_afcd15fc8c3e51b1` | Ludwig Bölkow Straße / Werner-Blohm-Straße | BASIS | Mischverkehr → Mischverkehr | – / – | asphalt | ja | 0.85 / 0.85 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[555504,5933150]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.544309/9.837637) · [OSM](https://www.openstreetmap.org/?mlat=53.544309&mlon=9.837637#map=18/53.544309/9.837637) |
| `ce_e2bc453a2576e4c0` | Sievekingplatz | BASIS | Zweirichtungsradweg → Radfahrstreifen | – / 3.00 | asphalt | ja | 0.62 / 0.62 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564813,5934629]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.556541/9.978410) · [OSM](https://www.openstreetmap.org/?mlat=53.556541&mlon=9.978410#map=18/53.556541/9.978410) |
| `ce_f612caed0fc545fb` | Nordkanalstraße | BASIS | Radweg je Seite → Radfahrstreifen | – / 2.00 | paving_stones | ja | 0.57 / 0.57 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567377,5933809]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.548843/10.016935) · [OSM](https://www.openstreetmap.org/?mlat=53.548843&mlon=10.016935#map=18/53.548843/10.016935) |
| `ce_0b596412fd421cb6` | Weidestraße | HAUPT | Radweg je Seite → Fahrradstraße | – / 2.50 | asphalt | ja | 0.78 / 0.84 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568617,5937322]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.580255/10.036422) · [OSM](https://www.openstreetmap.org/?mlat=53.580255&mlon=10.036422#map=18/53.580255/10.036422) |
| `ce_26ea542cee3718d2` | Fuhlsbüttler Straße | BASIS | Radweg je Seite → Radfahrstreifen | – / 2.00 | paving_stones | ja | 0.72 / 0.78 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568696,5940520]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.608988/10.038310) · [OSM](https://www.openstreetmap.org/?mlat=53.608988&mlon=10.038310#map=18/53.608988/10.038310) |
| `ce_5fd8da24f449a704` | Halbenkamp | HAUPT | Mischverkehr → Fahrradstraße | – / – | sett | ja | 0.66 / 0.87 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569742,5937918]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.585467/10.053530) · [OSM](https://www.openstreetmap.org/?mlat=53.585467&mlon=10.053530#map=18/53.585467/10.053530) |
| `ce_65cd9e5e26c9da83` | Gellertstraße | BASIS | Radfahrstreifen → Mischverkehr | – / 2.25 | asphalt | ja | 0.66 / 0.76 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566483,5937329]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.580595/10.004194) · [OSM](https://www.openstreetmap.org/?mlat=53.580595&mlon=10.004194#map=18/53.580595/10.004194) |
| `ce_da0776e37f17b8a1` | Alsterdorfer Straße | HAUPT | Radweg je Seite → Fahrradstraße | – / 2.50 | asphalt | ja | 0.60 / 0.67 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568277,5941700]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.619649/10.032242) · [OSM](https://www.openstreetmap.org/?mlat=53.619649&mlon=10.032242#map=18/53.619649/10.032242) |
| `ce_0e9d0c21509796cb` | Triftstraße | HAUPT | Zweirichtungsradweg → Fahrradstraße | – / 3.50 | asphalt | ja | 0.62 / 0.68 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563182,5923006]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.452274/9.951447) · [OSM](https://www.openstreetmap.org/?mlat=53.452274&mlon=9.951447#map=18/53.452274/9.951447) |
| `ce_5d9f7429af412d54` | Eigenheimweg | BASIS | Mischverkehr → Mischverkehr | – / – | asphalt | ja | 0.86 / 0.86 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565473,5922545]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.447853/9.985850) · [OSM](https://www.openstreetmap.org/?mlat=53.447853&mlon=9.985850#map=18/53.447853/9.985850) |
| `ce_fe842a7b18f25074` | – | HAUPT | eigener Weg → eigener Weg | – / 3.50 | asphalt | ja | 0.77 / 0.78 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565029,5923608]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.457466/9.979385) · [OSM](https://www.openstreetmap.org/?mlat=53.457466&mlon=9.979385#map=18/53.457466/9.979385) |
| `ce_3fdeae7df94e6da0` | Abrahamstraße | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.78 / 0.83 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576221,5942854]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.628920/10.152602) · [OSM](https://www.openstreetmap.org/?mlat=53.628920&mlon=10.152602#map=18/53.628920/10.152602) |
| `ce_5091c3af01ac6170` | Lottbeker Weg | BASIS | Mischverkehr → Mischverkehr | – / – | asphalt | ja | 0.91 / 0.91 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575423,5949868]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.692074/10.142241) · [OSM](https://www.openstreetmap.org/?mlat=53.692074&mlon=10.142241#map=18/53.692074/10.142241) |
| `ce_7829a19bb453c724` | Hammer Straße | BASIS | eigener Weg → eigener Weg | 1.00 / 3.00 | paving_stones | ja | 0.71 / 0.76 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570687,5935450]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.563159/10.067248) · [OSM](https://www.openstreetmap.org/?mlat=53.563159&mlon=10.067248#map=18/53.563159/10.067248) |
| `ce_7faf61216f219217` | Am Knill | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.80 / 0.85 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574692,5940330]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.606460/10.128882) · [OSM](https://www.openstreetmap.org/?mlat=53.606460&mlon=10.128882#map=18/53.606460/10.128882) |
| `ce_a7ef6b1695a7352b` | Osterkamp | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.78 / 0.83 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572766,5936269]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.570238/10.098821) · [OSM](https://www.openstreetmap.org/?mlat=53.570238&mlon=10.098821#map=18/53.570238/10.098821) |
| `ce_e769ac54cb29f221` | – | BASIS | eigener Weg → eigener Weg | – / 3.00 | paving_stones | ja | 0.79 / 0.79 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570641,5940517]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.608699/10.067697) · [OSM](https://www.openstreetmap.org/?mlat=53.608699&mlon=10.067697#map=18/53.608699/10.067697) |
| `ce_f8fa9634848fd9e3` | Ohlendieksredder | BASIS | Mischverkehr → Mischverkehr | – / – | nan | ja | 0.90 / 0.92 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571167,5947649]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.672726/10.077286) · [OSM](https://www.openstreetmap.org/?mlat=53.672726&mlon=10.077286#map=18/53.672726/10.077286) |

## Durchsicht mit Ortskundigen

20 Routen (nach Kategorie geschichtet, Seed 42, C-PRI-15) in `reports/cycle_principles_review.csv` mit Links und leeren Spalten für Einschätzung und Kommentar.

## Hinweise

- Soll-Führung je Kante vorläufig direkt aus der Trennungsmatrix (bevorzugte Führung); Prompt 18 legt Führung und Breite je Abschnitt fest, danach P-SAF-01/P-COM-01 (Soll) mit dessen Ergebnis rechnen.
- Halte und Zeitverlust (P-DIR-02/03) im Soll wie im Ist, bis Prompt 20 Soll-Knotentypen liefert; P-SAF-02 bis dahin unbekannt.
- Unfälle (P-SAF-04) bleiben im Soll unverändert (keine Wirkungsprognose).
- Nachfrage und Netz beruhen auf dem mäßig kalibrierten Modell aus Prompt 15 (reports/cycle_demand.md).

Quellen: OpenStreetMap-Beitragende (ODbL); ALKIS © Freie und Hansestadt Hamburg, LGV (dl-de/by-2.0); Unfallatlas © Statistische Ämter des Bundes und der Länder (dl-de/by-2.0); HVV-GTFS © Hamburger Verkehrsverbund GmbH (dl-de/by-2.0).
