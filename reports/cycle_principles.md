# Fünf Prinzipien: Bewertung des Soll-Radnetzes (Stufe c04)

Erzeugt 2026-11-06T16:11:01+00:00 mit pipeline/c04_principles.py · cycling_rules.yaml 0.4.0 · nicht amtlicher Entwurf. Alle Bewertungsregeln (C-PRI-01…16) und die Gewichte sind Annahmen (source_type assumption, status draft) und vor fachlicher Nutzung zu prüfen.

**score_ist** bewertet den heutigen Zustand der Soll-Route, **score_soll** den Zustand nach regelkonformem Ausbau (Führung nach Trennungsmatrix, Sollbreite, geschlossene Decke, Beleuchtung). Die Differenz ist der Handlungsbedarf. Fehlende Daten senken die confidence, nicht den Score.

## Kurzfassung

- RSV: 84 km, Score Ist 0.55 → Soll 0.67
- HAUPT: 2 027 km, Score Ist 0.66 → Soll 0.77
- BASIS: 1 052 km, Score Ist 0.78 → Soll 0.83
- Führung entspricht heute der Trennungsmatrix auf 48 % der Netzlänge mit bekannter Führung (RSV/HAUPT: 27 %).
- 5661 Routen bewertet; mittlerer Handlungsbedarf (score_soll − score_ist) 0.07, confidence: high 2117, medium 3543, low 1.
- Nicht bewertbar mangels Daten: P-SAF-02 (Knotentypen erst mit Prompt 20 (pipeline/c07_junctions.py)), P-COM-03 (kein Höhenmodell geladen (sources.yaml laserscan ohne Abruf)), P-ATT-02 (keine Lärmkarte (sources.yaml noise_maps ohne Endpunkt, Entscheidung 2026-11-06)).

## Datenlage je Prüfung

Anteil der Länge des Soll-Netzes (RSV, HAUPT, BASIS) mit Wert, unter den Kanten, für die die Prüfung anwendbar ist.

| Prüfung | Prinzip | Datengrundlage | anwendbar (km) | mit Wert |
| --- | --- | --- | ---: | ---: |
| P-COH-01 | Zusammenhang | c03 Maschen | 3 162 | 100 % |
| P-COH-02 | Zusammenhang | Soll-Netz | 3 159 | 100 % |
| P-COH-04 | Zusammenhang | Ist-Führung entlang der Route | 3 159 | 100 % |
| P-DIR-01 | Direktheit | Radgraph (Länge) | 3 159 | 99 % |
| P-DIR-02 | Direktheit | OSM-LSA, Vorfahrt C-GRAPH-05 | 3 159 | 100 % |
| P-DIR-03 | Direktheit | wie P-DIR-02 | 2 111 | 100 % |
| P-SAF-01 | Sicherheit | Ist-Führung (C-PRI-02), Trennungsmatrix | 3 097 | 100 % |
| P-SAF-02 | Sicherheit | – | 3 162 | 0 % |
| P-SAF-03 | Sicherheit | OSM lit | 3 162 | 85 % |
| P-SAF-04 | Sicherheit | Unfallatlas | 3 162 | 100 % |
| P-COM-01 | Komfort | OSM width/cycleway:width | 1 377 | 11 % |
| P-COM-02 | Komfort | OSM surface | 3 162 | 96 % |
| P-COM-03 | Komfort | – | 3 162 | 0 % |
| P-ATT-01 | Attraktivität | ALKIS, OSM-Bäume | 3 162 | 100 % |
| P-ATT-02 | Attraktivität | – | 3 162 | 0 % |
| P-ATT-03 | Attraktivität | DTV 2019 (HVS) | 3 162 | 100 % |

## Netzkennzahlen je Kategorie

Längengewichtete Mittel über die Kanten der Kategorie (Kantenwerte für Direktheit und Zusammenhang aus der Hauptroute der Kante).

| Kategorie | km | Zusammenhang Ist / Soll | Direktheit Ist / Soll | Sicherheit Ist / Soll | Komfort Ist / Soll | Attraktivität Ist / Soll | Gesamt Ist / Soll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| RSV | 84 | 0.28 / 0.30 | 0.64 / 0.64 | 0.66 / 0.80 | 0.45 / 1.00 | 0.63 / 0.63 | 0.55 / 0.67 |
| HAUPT | 2 027 | 0.65 / 0.67 | 0.67 / 0.67 | 0.62 / 0.82 | 0.69 / 1.00 | 0.71 / 0.71 | 0.66 / 0.77 |
| BASIS | 1 052 | 0.77 / 0.78 | 0.82 / 0.82 | 0.75 / 0.82 | 0.86 / 1.00 | 0.71 / 0.71 | 0.78 / 0.83 |

## Zusammenhang (P-COH)

**P-COH-01 Maschenweite** (aus c03, cycle_mesh_gaps.parquet):

| Ebene | Höchstweite | zu große Maschen | Seite Median | Seite max |
| --- | ---: | ---: | ---: | ---: |
| HAUPT | 600 m | 108 | 819 m | 4 103 m |
| BASIS | 300 m | 728 | 393 m | 4 073 m |

**P-COH-02 Komponenten** (je Ebene mit höheren Ebenen):

| Ebene | Komponenten | Anteil größte Komponente (Länge) |
| --- | ---: | ---: |
| RSV | 6 | 30 % |
| HAUPT | 1 | 100 % |
| BASIS | 1 | 100 % |

**P-COH-03 Abdeckung** (Ziele höchstens 300 m vom RSV/HAUPT-Netz; Zentren fehlen, kein Datensatz):

| Ziele | Anzahl | abgedeckt |
| --- | ---: | ---: |
| Schulen (OSM) | 557 | 96 % |
| Schnellbahnhalte | 375 | 99 % |
| Hochschulen (OSM university) | 41 | 100 % |

**P-COH-04 Kontinuität:** Wechsel der Ist-Führung je km (Median über Routen) 0.69, Soll (Führung und Kategorie) 0.00; Schwelle 1.0 je km (C-PRI-12).

## Direktheit (P-DIR)

**P-DIR-01 Umwegfaktor, Netzstichprobe** (C-PRI-04): je Kategorie 200 OD-Paare, Seed 42, Knoten der größten Komponente der Ebene (mit höheren Ebenen), Luftlinie im Band trip_length_km. Netzweg auf der Ebene gegen kürzesten Weg auf allen befahrbaren Kanten (Länge).

| Kategorie | Band (km) | Paare | ohne Weg | Median | 90-%-Wert | Schwelle | Anteil ≤ Schwelle |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RSV | 5–15 | 200 | 0 | 1.16 | 1.44 | 1.1 | 26 % |
| HAUPT | 2–3 | 200 | 0 | 1.15 | 2.07 | 1.2 | 59 % |
| BASIS | 1–2 | 200 | 0 | 1.07 | 2.25 | 1.3 | 78 % |

**Je Route** (Median über Routen der Kategorie; Halte nach C-PRI-05, Soll = Ist bis Prompt 20):

| Kategorie | Routen | Umwegfaktor | Halte/km | Schwelle Halte | Zeitverlust s/km | Schwelle s/km |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RSV | 23 | 1.11 | 1.6 | 0.5 | 20 | 30 |
| HAUPT | 2459 | 1.09 | 0.6 | 1.0 | 6 | 30 |
| BASIS | 3179 | 1.00 | 0.0 | 2.0 | 0 | – |

## Sicherheit (P-SAF)

**P-SAF-01 Ist-Führung gegen Soll-Führung** (km, Kanten RSV/HAUPT/BASIS):

| Ist \ Soll | Radfahrstreifen | Fahrradstraße | Mischverkehr | eigener Weg | Radweg je Seite | unbekannt |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Radfahrstreifen | 18 | 29 | 16 | 0 | 23 | 0 |
| Fahrradstraße | 0 | 18 | 2 | 0 | 0 | 0 |
| Mischverkehr | 18 | 1 061 | 600 | 0 | 51 | 48 |
| eigener Weg | 0 | 0 | 0 | 459 | 0 | 0 |
| Radweg je Seite | 62 | 110 | 43 | 0 | 236 | 7 |
| Zweirichtungsradweg | 23 | 115 | 51 | 13 | 148 | 4 |
| unbekannt | 0 | 0 | 0 | 0 | 0 | 5 |

P-SAF-03 Beleuchtung: OSM lit auf 85 % der Netzlänge bekannt; davon beleuchtet 90 %. P-SAF-04 Unfälle mit Radbeteiligung 2021–2025: 7 962 Unfälle an Kanten des Soll-Netzes (je Kante höchstens 15 m entfernt; nur Summen gespeichert).

## Komfort und Attraktivität (P-COM, P-ATT)

- P-COM-01 Breite: anwendbar auf 1 377 km (ohne Mischverkehr), Breite in OSM auf 11 % davon; von diesen erreichen 19 % die Sollbreite.
- P-COM-02 Belag: bekannt auf 96 %; RSV/HAUPT mit geschlossener Decke 67 %.
- P-ATT-01 Grünanteil im 20-m-Puffer: Median 13 % (Ziel 30 %, ALKIS-Grünflächen und OSM-Bäume).
- P-ATT-03: 356 km des Soll-Netzes liegen an Straßen mit DTV > 15 000.

## Top 30 Routen mit dem größten Handlungsbedarf

Rangfolge nach Handlungsbedarf-km = (score_soll − score_ist) × Länge in km (C-PRI-14), damit lange Routen mit mittlerem Defizit vor sehr kurzen Verdichtungsstücken stehen. S/K: Sicherheit und Komfort Ist → Soll.

| # | Route | Kategorie | km | Ist | Soll | Δ | Δ × km | S | K | confidence | Prüfen |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 1 | Innenstadt (Rathausmarkt) – Umsteigeknoten Neugraben (`rt_ef74f810d825e8b0`) | RSV | 23.8 | 0.56 | 0.70 | 0.14 | 3.22 | 0.65 → 0.78 | 0.37 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563960,5924903]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.469229/9.963550) · [OSM](https://www.openstreetmap.org/?mlat=53.469229&mlon=9.963550#map=18/53.469229/9.963550) |
| 2 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) (`rt_ad15aafddcc3fd36`) | RSV | 20.3 | 0.55 | 0.69 | 0.14 | 2.77 | 0.64 → 0.77 | 0.35 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565304,5924573]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.466099/9.983721) · [OSM](https://www.openstreetmap.org/?mlat=53.466099&mlon=9.983721#map=18/53.466099/9.983721) |
| 3 | Umsteigeknoten Neugraben – Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) (`rt_1eb91943b8b566de`) | HAUPT | 16.2 | 0.70 | 0.86 | 0.15 | 2.48 | 0.57 → 0.82 | 0.58 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560451,5929363]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.509731/9.911550) · [OSM](https://www.openstreetmap.org/?mlat=53.509731&mlon=9.911550#map=18/53.509731/9.911550) |
| 4 | Umsteigeknoten Neugraben – Hochschule Technologiezentrum Hamburg-Finkenwerder (`rt_f0fa3169346904cf`) | HAUPT | 15.3 | 0.71 | 0.86 | 0.15 | 2.29 | 0.57 → 0.82 | 0.58 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560443,5928891]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.505490/9.911337) · [OSM](https://www.openstreetmap.org/?mlat=53.505490&mlon=9.911337#map=18/53.505490/9.911337) |
| 5 | Arbeitsplatzschwerpunkt Hamburg-Mitte (263 Tsd. m²) – Arbeitsplatzschwerpunkt Bergedorf (224 Tsd. m²) (`rt_0bf6efc364e62515`) | HAUPT | 14.9 | 0.70 | 0.84 | 0.14 | 2.04 | 0.51 → 0.78 | 0.67 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569158,5931755]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.530157/10.043348) · [OSM](https://www.openstreetmap.org/?mlat=53.530157&mlon=10.043348#map=18/53.530157/10.043348) |
| 6 | Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) – Arbeitsplatzschwerpunkt Hamburg-Mitte (263 Tsd. m²) (`rt_c9d2a1f475c68304`) | HAUPT | 14.4 | 0.69 | 0.83 | 0.14 | 1.96 | 0.51 → 0.78 | 0.67 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569012,5931948]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.531906/10.041192) · [OSM](https://www.openstreetmap.org/?mlat=53.531906&mlon=10.041192#map=18/53.531906/10.041192) |
| 7 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_b34e65e7db0ca27f`) | HAUPT | 12.9 | 0.65 | 0.80 | 0.15 | 1.91 | 0.50 → 0.76 | 0.58 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564307,5933529]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546711/9.970552) · [OSM](https://www.openstreetmap.org/?mlat=53.546711&mlon=9.970552#map=18/53.546711/9.970552) |
| 8 | Innenstadt (Rathausmarkt) – Hochschule HAW Hamburg Energie Campus (`rt_9dab92d8a75510aa`) | RSV | 20.9 | 0.62 | 0.71 | 0.09 | 1.86 | 0.62 → 0.74 | 0.66 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573763,5932232]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.533816/10.112927) · [OSM](https://www.openstreetmap.org/?mlat=53.533816&mlon=10.112927#map=18/53.533816/10.112927) |
| 9 | Verdichtung HAUPT: neben Stein-Hardenberg-Straße (`rt_f2a1927097f3667f`) | HAUPT | 13.6 | 0.55 | 0.68 | 0.14 | 1.85 | 0.77 → 0.82 | 0.28 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576935,5942309]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.623921/10.163255) · [OSM](https://www.openstreetmap.org/?mlat=53.623921&mlon=10.163255#map=18/53.623921/10.163255) |
| 10 | Innenstadt (Rathausmarkt) – Hochschule Gebäude D (`rt_b3e5311382ffdee5`) | RSV | 15.3 | 0.58 | 0.70 | 0.12 | 1.78 | 0.67 → 0.76 | 0.42 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565862,5926294]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.481498/9.992496) · [OSM](https://www.openstreetmap.org/?mlat=53.481498&mlon=9.992496#map=18/53.481498/9.992496) |
| 11 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Bergedorf (224 Tsd. m²) (`rt_374f83d55ac09da7`) | HAUPT | 12.5 | 0.66 | 0.79 | 0.13 | 1.56 | 0.52 → 0.75 | 0.64 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570263,5931665]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.529197/10.059998) · [OSM](https://www.openstreetmap.org/?mlat=53.529197&mlon=10.059998#map=18/53.529197/10.059998) |
| 12 | Innenstadt (Rathausmarkt) – Umsteigeknoten Hamburg-Harburg (`rt_c54fa6f4435a9343`) | RSV | 14.6 | 0.59 | 0.70 | 0.11 | 1.54 | 0.68 → 0.76 | 0.47 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565874,5930076]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.515492/9.993469) · [OSM](https://www.openstreetmap.org/?mlat=53.515492&mlon=9.993469#map=18/53.515492/9.993469) |
| 13 | Verdichtung HAUPT: Tarpenbek-Kollau-Wanderweg (`rt_3abb134b0ccd0024`) | HAUPT | 10.0 | 0.58 | 0.73 | 0.15 | 1.50 | 0.67 → 0.80 | 0.37 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561619,5941769]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.621098/9.931609) · [OSM](https://www.openstreetmap.org/?mlat=53.621098&mlon=9.931609#map=18/53.621098/9.931609) |
| 14 | Innenstadt (Rathausmarkt) – Umsteigeknoten Bergedorf (`rt_905b5b331dc096e5`) | RSV | 18.9 | 0.62 | 0.70 | 0.08 | 1.49 | 0.61 → 0.73 | 0.74 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573679,5933060]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.541266/10.111849) · [OSM](https://www.openstreetmap.org/?mlat=53.541266&mlon=10.111849#map=18/53.541266/10.111849) |
| 15 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) (`rt_be5550ff43b6bffd`) | HAUPT | 12.0 | 0.66 | 0.78 | 0.12 | 1.49 | 0.52 → 0.75 | 0.65 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570037,5931767]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.530146/10.056618) · [OSM](https://www.openstreetmap.org/?mlat=53.530146&mlon=10.056618#map=18/53.530146/10.056618) |
| 16 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Harburg (241 Tsd. m²) (`rt_2a3981f4e8e27282`) | RSV | 13.9 | 0.60 | 0.70 | 0.10 | 1.46 | 0.68 → 0.76 | 0.47 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565713,5926950]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.487410/9.990387) · [OSM](https://www.openstreetmap.org/?mlat=53.487410&mlon=9.990387#map=18/53.487410/9.990387) |
| 17 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Nord (307 Tsd. m²) (`rt_d03f7415e12263b1`) | HAUPT | 12.9 | 0.66 | 0.77 | 0.11 | 1.45 | 0.59 → 0.72 | 0.55 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568341,5938658]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.592300/10.032541) · [OSM](https://www.openstreetmap.org/?mlat=53.592300&mlon=10.032541#map=18/53.592300/10.032541) |
| 18 | Umsteigeknoten Neugraben – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_1f65359785a52cea`) | HAUPT | 10.2 | 0.70 | 0.84 | 0.14 | 1.43 | 0.59 → 0.82 | 0.58 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559820,5926567]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.484673/9.901500) · [OSM](https://www.openstreetmap.org/?mlat=53.484673&mlon=9.901500#map=18/53.484673/9.901500) |
| 19 | Umsteigeknoten Altona – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_bd033e96360c6110`) | HAUPT | 11.5 | 0.66 | 0.78 | 0.12 | 1.42 | 0.52 → 0.75 | 0.71 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[561367,5934211]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.553196/9.926314) · [OSM](https://www.openstreetmap.org/?mlat=53.553196&mlon=9.926314#map=18/53.553196/9.926314) |
| 20 | Arbeitsplatzschwerpunkt Hamburg-Mitte (278 Tsd. m²) – Arbeitsplatzschwerpunkt Bergedorf (224 Tsd. m²) (`rt_5be88c5238ed113e`) | HAUPT | 7.1 | 0.63 | 0.83 | 0.19 | 1.37 | 0.43 → 0.81 | 0.50 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572709,5930397]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.517468/10.096597) · [OSM](https://www.openstreetmap.org/?mlat=53.517468&mlon=10.096597#map=18/53.517468/10.096597) |
| 21 | Anbindung Schule/Nahversorgung: Vierländer Eisenbahndamm (`rt_e97c97c7cb138219`) | BASIS | 12.8 | 0.84 | 0.94 | 0.10 | 1.32 | 0.56 → 0.82 | 0.83 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579906,5920392]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.426511/10.202569) · [OSM](https://www.openstreetmap.org/?mlat=53.426511&mlon=10.202569#map=18/53.426511/10.202569) |
| 22 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) (`rt_2017ccd29d0c27dc`) | HAUPT | 13.6 | 0.60 | 0.69 | 0.09 | 1.28 | 0.56 → 0.71 | 0.72 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559900,5934158]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.552888/9.904158) · [OSM](https://www.openstreetmap.org/?mlat=53.552888&mlon=9.904158#map=18/53.552888/9.904158) |
| 23 | Innenstadt (Rathausmarkt) – Umsteigeknoten Ohlsdorf (`rt_afcaa8af59ac04b9`) | HAUPT | 10.4 | 0.65 | 0.78 | 0.12 | 1.28 | 0.55 → 0.71 | 0.56 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568366,5937428]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.581244/10.032648) · [OSM](https://www.openstreetmap.org/?mlat=53.581244&mlon=10.032648#map=18/53.581244/10.032648) |
| 24 | Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) – Arbeitsplatzschwerpunkt Hamburg-Mitte (278 Tsd. m²) (`rt_e3d331b9b5cc9556`) | HAUPT | 6.6 | 0.63 | 0.82 | 0.19 | 1.25 | 0.43 → 0.80 | 0.52 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572886,5930550]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.518820/10.099305) · [OSM](https://www.openstreetmap.org/?mlat=53.518820&mlon=10.099305#map=18/53.518820/10.099305) |
| 25 | Innenstadt (Rathausmarkt) – Hochschule HAW - Life Sciences - Campus Bergedorf (`rt_d98d16d4f6df6b74`) | RSV | 18.2 | 0.62 | 0.69 | 0.07 | 1.21 | 0.62 → 0.73 | 0.79 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573373,5933222]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.542764/10.107268) · [OSM](https://www.openstreetmap.org/?mlat=53.542764&mlon=10.107268#map=18/53.542764/10.107268) |
| 26 | Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_92c799d039928f25`) | HAUPT | 6.9 | 0.71 | 0.88 | 0.17 | 1.18 | 0.53 → 0.82 | 0.63 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558087,5932014]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.533828/9.876405) · [OSM](https://www.openstreetmap.org/?mlat=53.533828&mlon=9.876405#map=18/53.533828/9.876405) |
| 27 | Hochschule HAW Hamburg Energie Campus – Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) (`rt_d21a6b75e7fe151a`) | HAUPT | 9.8 | 0.76 | 0.88 | 0.12 | 1.17 | 0.62 → 0.81 | 0.56 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577180,5927176]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.487890/10.163223) · [OSM](https://www.openstreetmap.org/?mlat=53.487890&mlon=10.163223#map=18/53.487890/10.163223) |
| 28 | Umsteigeknoten Hamburg-Harburg – Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) (`rt_463b00cfca1d45be`) | RSV | 7.4 | 0.52 | 0.68 | 0.16 | 1.16 | 0.59 → 0.80 | 0.33 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562896,5925065]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470813/9.947549) · [OSM](https://www.openstreetmap.org/?mlat=53.470813&mlon=9.947549#map=18/53.470813/9.947549) |
| 29 | Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) – Arbeitsplatzschwerpunkt Harburg (241 Tsd. m²) (`rt_a3f51202ca48fa1c`) | RSV | 6.8 | 0.51 | 0.68 | 0.17 | 1.15 | 0.55 → 0.78 | 0.34 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562608,5925087]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.471045/9.943226) · [OSM](https://www.openstreetmap.org/?mlat=53.471045&mlon=9.943226#map=18/53.471045/9.943226) |
| 30 | Hochschule Gebäude D – Arbeitsplatzschwerpunkt Hamburg-Mitte (263 Tsd. m²) (`rt_b5d72f675be53749`) | HAUPT | 9.5 | 0.67 | 0.80 | 0.12 | 1.15 | 0.62 → 0.80 | 0.58 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566943,5926204]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.480554/10.008763) · [OSM](https://www.openstreetmap.org/?mlat=53.480554&mlon=10.008763#map=18/53.480554/10.008763) |

Höchster Δ einer Route (ohne Längengewicht): 0.35; Routen mit Δ ≥ 0,2: 305.

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
| Zusammenhang | 0.200 | 0.160 | 29/30 | 0.997 |
| Zusammenhang | 0.200 | 0.240 | 29/30 | 0.997 |
| Direktheit | 0.250 | 0.200 | 30/30 | 1.000 |
| Direktheit | 0.250 | 0.300 | 30/30 | 1.000 |
| Sicherheit | 0.300 | 0.240 | 30/30 | 0.995 |
| Sicherheit | 0.300 | 0.360 | 28/30 | 0.997 |
| Komfort | 0.150 | 0.120 | 28/30 | 0.998 |
| Komfort | 0.150 | 0.180 | 29/30 | 0.999 |
| Attraktivität | 0.100 | 0.080 | 30/30 | 1.000 |
| Attraktivität | 0.100 | 0.120 | 30/30 | 1.000 |

Kleinste Überschneidung: 28/30.

## Handlungsbedarf je Bezirk

| Bezirk | Netz-km | Score Ist | Score Soll | Δ |
| --- | ---: | ---: | ---: | ---: |
| Altona | 445 | 0.69 | 0.77 | 0.08 |
| Bergedorf | 210 | 0.72 | 0.81 | 0.09 |
| Eimsbüttel | 371 | 0.69 | 0.78 | 0.09 |
| Hamburg-Mitte | 536 | 0.70 | 0.79 | 0.09 |
| Hamburg-Nord | 442 | 0.69 | 0.78 | 0.09 |
| Harburg | 283 | 0.68 | 0.78 | 0.11 |
| Wandsbek | 875 | 0.70 | 0.79 | 0.09 |

## Stichprobe: 30 zufällige Kanten (Seed 42, nach Bezirk verteilt)

| Kante | Name | Kategorie | Führung Ist → Soll | Breite / Soll | Belag | lit | Score Ist / Soll | Prüfen |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| `ce_0e10c3e49187620a` | neben Max-Brauer-Allee | HAUPT | Zweirichtungsradweg → Radweg je Seite | – / 3.50 | asphalt | ja | 0.62 / 0.67 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562008,5933904]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.550361/9.935920) · [OSM](https://www.openstreetmap.org/?mlat=53.550361&mlon=9.935920#map=18/53.550361/9.935920) |
| `ce_39738c01ec00af94` | Bahrenfelder Steindamm | HAUPT | Radfahrstreifen → Fahrradstraße | – / 2.50 | asphalt | ja | 0.60 / 0.71 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560936,5935319]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.563203/9.920023) · [OSM](https://www.openstreetmap.org/?mlat=53.563203&mlon=9.920023#map=18/53.563203/9.920023) |
| `ce_7a205f345e4231eb` | neben Bahrenfelder Chaussee | HAUPT | Radweg je Seite → Radweg je Seite | 1.80 / 2.50 | paving_stones | ja | 0.71 / 0.81 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560748,5935431]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564235/9.917204) · [OSM](https://www.openstreetmap.org/?mlat=53.564235&mlon=9.917204#map=18/53.564235/9.917204) |
| `ce_87b7453cebcc4d83` | Woyrschweg | HAUPT | Mischverkehr → Fahrradstraße | – / – | sett | ja | 0.60 / 0.81 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560403,5935232]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.562488/9.911965) · [OSM](https://www.openstreetmap.org/?mlat=53.562488&mlon=9.911965#map=18/53.562488/9.911965) |
| `ce_27ad70cff3e7f428` | Weidenbaumsweg | BASIS | Radweg je Seite → Mischverkehr | – / 2.00 | paving_stones | ja | 0.72 / 0.78 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579824,5927175]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.487486/10.203063) · [OSM](https://www.openstreetmap.org/?mlat=53.487486&mlon=10.203063#map=18/53.487486/10.203063) |
| `ce_3ee2f00a7910af5c` | Von-Hacht-Weg | BASIS | eigener Weg → eigener Weg | – / 3.00 | paving_stones | nein | 0.83 / 0.93 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576849,5927090]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.487160/10.158217) · [OSM](https://www.openstreetmap.org/?mlat=53.487160&mlon=10.158217#map=18/53.487160/10.158217) |
| `ce_1957ebd1d94c481d` | Margaretenstraße | BASIS | Mischverkehr → Mischverkehr | – / – | asphalt | ja | 0.93 / 0.93 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563770,5935698]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.566276/9.962877) · [OSM](https://www.openstreetmap.org/?mlat=53.566276&mlon=9.962877#map=18/53.566276/9.962877) |
| `ce_ad49f9331aa1505a` | neben Holsteiner Chaussee | HAUPT | Radweg je Seite → Radweg je Seite | – / 2.50 | paving_stones | ja | 0.49 / 0.67 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560006,5941300]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.617068/9.907135) · [OSM](https://www.openstreetmap.org/?mlat=53.617068&mlon=9.907135#map=18/53.617068/9.907135) |
| `ce_bd7e11b3c4c64fd2` | Wiesingerweg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.79 / 0.84 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563842,5937274]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.580430/9.964290) · [OSM](https://www.openstreetmap.org/?mlat=53.580430&mlon=9.964290#map=18/53.580430/9.964290) |
| `ce_bf5dd137711bbb35` | neben Grindelberg / Hoheluftchaussee | RSV | Zweirichtungsradweg → Radweg je Seite | – / 4.50 | asphalt | ja | 0.52 / 0.57 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564571,5937096]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.578741/9.975263) · [OSM](https://www.openstreetmap.org/?mlat=53.578741&mlon=9.975263#map=18/53.578741/9.975263) |
| `ce_0ba38be1cd922a08` | – | BASIS | eigener Weg → eigener Weg | – / 3.00 | compacted | – | 0.63 / 0.80 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566071,5929410]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.509480/9.996295) · [OSM](https://www.openstreetmap.org/?mlat=53.509480&mlon=9.996295#map=18/53.509480/9.996295) |
| `ce_1f910fac0892584a` | Überseeallee | HAUPT | Zweirichtungsradweg → Radweg je Seite | – / 3.50 | paving_stones | ja | 0.47 / 0.68 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566260,5932936]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.541144/9.999890) · [OSM](https://www.openstreetmap.org/?mlat=53.541144&mlon=9.999890#map=18/53.541144/9.999890) |
| `ce_a01625d0adef524f` | – | RSV | eigener Weg → eigener Weg | – / 4.00 | paving_stones | ja | 0.59 / 0.74 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571776,5934520]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.554649/10.083473) · [OSM](https://www.openstreetmap.org/?mlat=53.554649&mlon=10.083473#map=18/53.554649/10.083473) |
| `ce_cddd79dd5d732571` | Öjendorfer Weg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.80 / 0.86 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573440,5932847]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.539392/10.108200) · [OSM](https://www.openstreetmap.org/?mlat=53.539392&mlon=10.108200#map=18/53.539392/10.108200) |
| `ce_dee047453bce7285` | Gert-Schwämmle-Weg | HAUPT | eigener Weg → eigener Weg | – / 3.50 | paving_stones | nein | 0.53 / 0.80 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565251,5929133]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.507089/9.983878) · [OSM](https://www.openstreetmap.org/?mlat=53.507089&mlon=9.983878#map=18/53.507089/9.983878) |
| `ce_0a74bb61e997f320` | Wandsbeker Stieg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.87 / 0.92 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567977,5935077]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560166/10.026261) · [OSM](https://www.openstreetmap.org/?mlat=53.560166&mlon=10.026261#map=18/53.560166/10.026261) |
| `ce_233901822b9ba5dc` | – | HAUPT | eigener Weg → eigener Weg | – / 3.50 | paving_stones | – | 0.66 / 0.83 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566676,5944867]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.648316/10.008722) · [OSM](https://www.openstreetmap.org/?mlat=53.648316&mlon=10.008722#map=18/53.648316/10.008722) |
| `ce_593c52e5033643e3` | neben Fuhlsbüttler Straße | HAUPT | Radweg je Seite → Radweg je Seite | – / 2.50 | paving_stones | ja | 0.63 / 0.78 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569312,5937904]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.585396/10.047035) · [OSM](https://www.openstreetmap.org/?mlat=53.585396&mlon=10.047035#map=18/53.585396/10.047035) |
| `ce_5e8c506203552425` | – | BASIS | eigener Weg → eigener Weg | – / 3.00 | compacted | ja | 0.81 / 0.96 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567358,5947667]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.673395/10.019643) · [OSM](https://www.openstreetmap.org/?mlat=53.673395&mlon=10.019643#map=18/53.673395/10.019643) |
| `ce_ccba95fa4a7108f8` | Bergmannstraße | BASIS | Mischverkehr → Mischverkehr | – / – | asphalt | – | 0.75 / 0.80 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566130,5947601]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.672954/10.001046) · [OSM](https://www.openstreetmap.org/?mlat=53.672954&mlon=10.001046#map=18/53.672954/10.001046) |
| `ce_0d6077c73e3f546a` | Hainholzweg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.73 / 0.80 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562466,5922787]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.450393/9.940619) · [OSM](https://www.openstreetmap.org/?mlat=53.450393&mlon=9.940619#map=18/53.450393/9.940619) |
| `ce_584975a881fb63f6` | Kleinfeld | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.75 / 0.80 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557462,5925182]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.472488/9.865724) · [OSM](https://www.openstreetmap.org/?mlat=53.472488&mlon=9.865724#map=18/53.472488/9.865724) |
| `ce_f64e656a0ce74a9d` | Hannoversche Straße | HAUPT | Radfahrstreifen → Radweg je Seite | – / 2.50 | paving_stones | ja | 0.54 / 0.74 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565993,5924520]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.465543/9.994086) · [OSM](https://www.openstreetmap.org/?mlat=53.465543&mlon=9.994086#map=18/53.465543/9.994086) |
| `ce_3d05afb298ba8880` | Wilhelm-Bauche-Weg | BASIS | eigener Weg → eigener Weg | 2.00 / 3.00 | paving_stones | ja | 0.83 / 0.86 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572085,5945235]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.650904/10.090611) · [OSM](https://www.openstreetmap.org/?mlat=53.650904&mlon=10.090611#map=18/53.650904/10.090611) |
| `ce_726c85dcd0828f50` | – | HAUPT | eigener Weg → eigener Weg | – / 3.50 | compacted | ja | 0.66 / 0.80 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571782,5936056]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.568453/10.083926) · [OSM](https://www.openstreetmap.org/?mlat=53.568453&mlon=10.083926#map=18/53.568453/10.083926) |
| `ce_7a097e91b55e66aa` | Mühlenredder | HAUPT | Mischverkehr → Fahrradstraße | – / – | cobblestone | – | 0.61 / 0.87 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574403,5950693]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.699633/10.126991) · [OSM](https://www.openstreetmap.org/?mlat=53.699633&mlon=10.126991#map=18/53.699633/10.126991) |
| `ce_933dbb77cd20dd57` | Am Knill | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.61 / 0.66 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574586,5940062]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.604067/10.127215) · [OSM](https://www.openstreetmap.org/?mlat=53.604067&mlon=10.127215#map=18/53.604067/10.127215) |
| `ce_afc705ae85b86b34` | Hoheneichen | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.66 / 0.71 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570605,5943102]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.631940/10.067752) · [OSM](https://www.openstreetmap.org/?mlat=53.631940&mlon=10.067752#map=18/53.631940/10.067752) |
| `ce_bdaf9df7e63e3f2f` | Ellerneck | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | – | 0.46 / 0.58 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575640,5938624]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.590995/10.142791) · [OSM](https://www.openstreetmap.org/?mlat=53.590995&mlon=10.142791#map=18/53.590995/10.142791) |
| `ce_c18e3096f67b49b4` | – | HAUPT | eigener Weg → eigener Weg | – / 3.50 | asphalt | ja | 0.68 / 0.68 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568627,5944160]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.641708/10.038068) · [OSM](https://www.openstreetmap.org/?mlat=53.641708&mlon=10.038068#map=18/53.641708/10.038068) |

## Durchsicht mit Ortskundigen

20 Routen (nach Kategorie geschichtet, Seed 42, C-PRI-15) in `reports/cycle_principles_review.csv` mit Links und leeren Spalten für Einschätzung und Kommentar.

## Hinweise

- Soll-Führung je Kante vorläufig direkt aus der Trennungsmatrix (bevorzugte Führung); Prompt 18 legt Führung und Breite je Abschnitt fest, danach P-SAF-01/P-COM-01 (Soll) mit dessen Ergebnis rechnen.
- Halte und Zeitverlust (P-DIR-02/03) im Soll wie im Ist, bis Prompt 20 Soll-Knotentypen liefert; P-SAF-02 bis dahin unbekannt.
- Unfälle (P-SAF-04) bleiben im Soll unverändert (keine Wirkungsprognose).
- Nachfrage und Netz beruhen auf dem mäßig kalibrierten Modell aus Prompt 15 (reports/cycle_demand.md).

Quellen: OpenStreetMap-Beitragende (ODbL); ALKIS © Freie und Hansestadt Hamburg, LGV (dl-de/by-2.0); Unfallatlas © Statistische Ämter des Bundes und der Länder (dl-de/by-2.0); HVV-GTFS © Hamburger Verkehrsverbund GmbH (dl-de/by-2.0).
