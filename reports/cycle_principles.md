# Fünf Prinzipien: Bewertung des Soll-Radnetzes (Stufe c04)

Erzeugt 2026-11-07T15:14:14+00:00 mit pipeline/c04_principles.py · cycling_rules.yaml 0.7.0 · nicht amtlicher Entwurf. Alle Bewertungsregeln (C-PRI-01…16) und die Gewichte sind Annahmen (source_type assumption, status draft) und vor fachlicher Nutzung zu prüfen.

**score_ist** bewertet den heutigen Zustand der Soll-Route, **score_soll** den Zustand nach regelkonformem Ausbau (Führung nach Trennungsmatrix, Sollbreite, geschlossene Decke, Beleuchtung). Die Differenz ist der Handlungsbedarf. Fehlende Daten senken die confidence, nicht den Score.

## Kurzfassung

- RSV: 66 km, Score Ist 0.57 → Soll 0.69
- HAUPT: 1 873 km, Score Ist 0.67 → Soll 0.77
- BASIS: 1 021 km, Score Ist 0.79 → Soll 0.83
- Führung entspricht heute der Trennungsmatrix auf 49 % der Netzlänge mit bekannter Führung (RSV/HAUPT: 27 %).
- 5030 Routen bewertet; mittlerer Handlungsbedarf (score_soll − score_ist) 0.06, confidence: high 1877, medium 3153, low 0.
- Nicht bewertbar mangels Daten: P-SAF-02 (Knotentypen erst mit Prompt 20 (pipeline/c07_junctions.py)), P-COM-03 (kein Höhenmodell geladen (sources.yaml laserscan ohne Abruf)), P-ATT-02 (keine Lärmkarte (sources.yaml noise_maps ohne Endpunkt, Entscheidung 2026-11-06)).

## Datenlage je Prüfung

Anteil der Länge des Soll-Netzes (RSV, HAUPT, BASIS) mit Wert, unter den Kanten, für die die Prüfung anwendbar ist.

| Prüfung | Prinzip | Datengrundlage | anwendbar (km) | mit Wert |
| --- | --- | --- | ---: | ---: |
| P-COH-01 | Zusammenhang | c03 Maschen | 2 960 | 100 % |
| P-COH-02 | Zusammenhang | Soll-Netz | 2 958 | 100 % |
| P-COH-04 | Zusammenhang | Ist-Führung entlang der Route | 2 958 | 100 % |
| P-DIR-01 | Direktheit | Radgraph (Länge) | 2 958 | 99 % |
| P-DIR-02 | Direktheit | OSM-LSA, Vorfahrt C-GRAPH-05 | 2 958 | 100 % |
| P-DIR-03 | Direktheit | wie P-DIR-02 | 1 939 | 100 % |
| P-SAF-01 | Sicherheit | Ist-Führung (C-PRI-02), Trennungsmatrix | 2 902 | 100 % |
| P-SAF-02 | Sicherheit | – | 2 960 | 0 % |
| P-SAF-03 | Sicherheit | OSM lit | 2 960 | 85 % |
| P-SAF-04 | Sicherheit | Unfallatlas | 2 960 | 100 % |
| P-COM-01 | Komfort | OSM width/cycleway:width | 1 278 | 11 % |
| P-COM-02 | Komfort | OSM surface | 2 960 | 96 % |
| P-COM-03 | Komfort | – | 2 960 | 0 % |
| P-ATT-01 | Attraktivität | ALKIS, OSM-Bäume | 2 960 | 100 % |
| P-ATT-02 | Attraktivität | – | 2 960 | 0 % |
| P-ATT-03 | Attraktivität | DTV 2019 (HVS) | 2 960 | 100 % |

## Netzkennzahlen je Kategorie

Längengewichtete Mittel über die Kanten der Kategorie (Kantenwerte für Direktheit und Zusammenhang aus der Hauptroute der Kante).

| Kategorie | km | Zusammenhang Ist / Soll | Direktheit Ist / Soll | Sicherheit Ist / Soll | Komfort Ist / Soll | Attraktivität Ist / Soll | Gesamt Ist / Soll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| RSV | 66 | 0.33 / 0.34 | 0.66 / 0.66 | 0.66 / 0.79 | 0.51 / 1.00 | 0.65 / 0.65 | 0.57 / 0.69 |
| HAUPT | 1 873 | 0.68 / 0.71 | 0.66 / 0.66 | 0.64 / 0.82 | 0.69 / 1.00 | 0.70 / 0.70 | 0.67 / 0.77 |
| BASIS | 1 021 | 0.79 / 0.80 | 0.81 / 0.81 | 0.75 / 0.82 | 0.86 / 1.00 | 0.71 / 0.71 | 0.79 / 0.83 |

## Zusammenhang (P-COH)

**P-COH-01 Maschenweite** (aus c03, cycle_mesh_gaps.parquet):

| Ebene | Höchstweite | zu große Maschen | Seite Median | Seite max |
| --- | ---: | ---: | ---: | ---: |
| HAUPT | 600 m | 34 | 1 050 m | 4 073 m |
| BASIS | 300 m | 409 | 413 m | 4 064 m |

**P-COH-02 Komponenten** (je Ebene mit höheren Ebenen):

| Ebene | Komponenten | Anteil größte Komponente (Länge) |
| --- | ---: | ---: |
| RSV | 6 | 20 % |
| HAUPT | 1 | 100 % |
| BASIS | 1 | 100 % |

**P-COH-03 Abdeckung** (Ziele höchstens 300 m vom RSV/HAUPT-Netz; Zentren fehlen, kein Datensatz):

| Ziele | Anzahl | abgedeckt |
| --- | ---: | ---: |
| Schulen (OSM) | 557 | 96 % |
| Schnellbahnhalte | 375 | 99 % |
| Hochschulen (OSM university) | 41 | 100 % |

**P-COH-04 Kontinuität:** Wechsel der Ist-Führung je km (Median über Routen) 1.09, Soll (Führung und Kategorie) 0.00; Schwelle 1.0 je km (C-PRI-12).

## Direktheit (P-DIR)

**P-DIR-01 Umwegfaktor, Netzstichprobe** (C-PRI-04): je Kategorie 200 OD-Paare, Seed 42, Knoten der größten Komponente der Ebene (mit höheren Ebenen), Luftlinie im Band trip_length_km. Netzweg auf der Ebene gegen kürzesten Weg auf allen befahrbaren Kanten (Länge).

| Kategorie | Band (km) | Paare | ohne Weg | Median | 90-%-Wert | Schwelle | Anteil ≤ Schwelle |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RSV | 5–15 | 200 | 0 | 1.11 | 1.17 | 1.1 | 39 % |
| HAUPT | 2–3 | 200 | 0 | 1.18 | 3.58 | 1.2 | 55 % |
| BASIS | 1–2 | 200 | 0 | 1.07 | 3.20 | 1.3 | 78 % |

**Je Route** (Median über Routen der Kategorie; Halte nach C-PRI-05, Soll = Ist bis Prompt 20):

| Kategorie | Routen | Umwegfaktor | Halte/km | Schwelle Halte | Zeitverlust s/km | Schwelle s/km |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RSV | 22 | 1.08 | 1.6 | 0.5 | 23 | 30 |
| HAUPT | 2112 | 1.11 | 1.1 | 1.0 | 11 | 30 |
| BASIS | 2896 | 1.00 | 0.0 | 2.0 | 0 | – |

## Sicherheit (P-SAF)

**P-SAF-01 Ist-Führung gegen Soll-Führung** (km, Kanten RSV/HAUPT/BASIS):

| Ist \ Soll | Radfahrstreifen | Fahrradstraße | Mischverkehr | eigener Weg | Radweg je Seite | unbekannt |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Radfahrstreifen | 16 | 30 | 15 | 0 | 24 | 0 |
| Fahrradstraße | 0 | 18 | 2 | 0 | 0 | 0 |
| Mischverkehr | 14 | 975 | 595 | 0 | 49 | 41 |
| eigener Weg | 0 | 0 | 0 | 418 | 0 | 0 |
| Radweg je Seite | 55 | 98 | 45 | 0 | 220 | 7 |
| Zweirichtungsradweg | 22 | 109 | 48 | 11 | 138 | 4 |
| unbekannt | 0 | 0 | 0 | 0 | 0 | 5 |

P-SAF-03 Beleuchtung: OSM lit auf 85 % der Netzlänge bekannt; davon beleuchtet 90 %. P-SAF-04 Unfälle mit Radbeteiligung 2021–2025: 7 605 Unfälle an Kanten des Soll-Netzes (je Kante höchstens 15 m entfernt; nur Summen gespeichert).

## Komfort und Attraktivität (P-COM, P-ATT)

- P-COM-01 Breite: anwendbar auf 1 278 km (ohne Mischverkehr), Breite in OSM auf 11 % davon; von diesen erreichen 20 % die Sollbreite.
- P-COM-02 Belag: bekannt auf 96 %; RSV/HAUPT mit geschlossener Decke 67 %.
- P-ATT-01 Grünanteil im 20-m-Puffer: Median 13 % (Ziel 30 %, ALKIS-Grünflächen und OSM-Bäume).
- P-ATT-03: 329 km des Soll-Netzes liegen an Straßen mit DTV > 15 000.

## Top 30 Routen mit dem größten Handlungsbedarf

Rangfolge nach Handlungsbedarf-km = (score_soll − score_ist) × Länge in km (C-PRI-14), damit lange Routen mit mittlerem Defizit vor sehr kurzen Verdichtungsstücken stehen. S/K: Sicherheit und Komfort Ist → Soll.

| # | Route | Kategorie | km | Ist | Soll | Δ | Δ × km | S | K | confidence | Prüfen |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 1 | Innenstadt (Rathausmarkt) – Umsteigeknoten Neugraben (`rt_46a9a9c639d7d6c8`) | RSV | 23.2 | 0.57 | 0.71 | 0.14 | 3.30 | 0.59 → 0.76 | 0.44 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566101,5925609]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.475314/9.995944) · [OSM](https://www.openstreetmap.org/?mlat=53.475314&mlon=9.995944#map=18/53.475314/9.995944) |
| 2 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) (`rt_3645a25b810b0a3f`) | RSV | 19.8 | 0.56 | 0.71 | 0.14 | 2.86 | 0.57 → 0.75 | 0.44 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565693,5927156]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.489264/9.990118) · [OSM](https://www.openstreetmap.org/?mlat=53.489264&mlon=9.990118#map=18/53.489264/9.990118) |
| 3 | Umsteigeknoten Neugraben – Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) (`rt_a1437067c8713aec`) | HAUPT | 16.2 | 0.73 | 0.87 | 0.14 | 2.33 | 0.59 → 0.83 | 0.60 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560451,5929359]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.509694/9.911549) · [OSM](https://www.openstreetmap.org/?mlat=53.509694&mlon=9.911549#map=18/53.509694/9.911549) |
| 4 | Umsteigeknoten Neugraben – Hochschule Technologiezentrum Hamburg-Finkenwerder (`rt_fa57d47917cbb47c`) | HAUPT | 15.3 | 0.73 | 0.87 | 0.14 | 2.16 | 0.59 → 0.83 | 0.61 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560443,5928887]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.505453/9.911335) · [OSM](https://www.openstreetmap.org/?mlat=53.505453&mlon=9.911335#map=18/53.505453/9.911335) |
| 5 | Innenstadt (Rathausmarkt) – Hochschule Gebäude D (`rt_8eabe7a2f46ef973`) | RSV | 14.8 | 0.59 | 0.72 | 0.12 | 1.80 | 0.58 → 0.74 | 0.55 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565276,5929388]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.509382/9.984308) · [OSM](https://www.openstreetmap.org/?mlat=53.509382&mlon=9.984308#map=18/53.509382/9.984308) |
| 6 | Arbeitsplatzschwerpunkt Hamburg-Mitte (263 Tsd. m²) – Arbeitsplatzschwerpunkt Bergedorf (224 Tsd. m²) (`rt_a0ba9480bcf0aba0`) | HAUPT | 14.9 | 0.74 | 0.86 | 0.12 | 1.75 | 0.57 → 0.78 | 0.67 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569146,5931763]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.530230/10.043167) · [OSM](https://www.openstreetmap.org/?mlat=53.530230&mlon=10.043167#map=18/53.530230/10.043167) |
| 7 | Innenstadt (Rathausmarkt) – Hochschule HAW Hamburg Energie Campus (`rt_bc1008c8faddf565`) | RSV | 20.9 | 0.63 | 0.71 | 0.08 | 1.74 | 0.62 → 0.73 | 0.69 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573789,5932167]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.533228/10.113295) · [OSM](https://www.openstreetmap.org/?mlat=53.533228&mlon=10.113295#map=18/53.533228/10.113295) |
| 8 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_3a0535e6b916dd87`) | HAUPT | 12.9 | 0.70 | 0.83 | 0.13 | 1.72 | 0.56 → 0.76 | 0.57 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564309,5933531]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546728/9.970578) · [OSM](https://www.openstreetmap.org/?mlat=53.546728&mlon=9.970578#map=18/53.546728/9.970578) |
| 9 | Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) – Arbeitsplatzschwerpunkt Hamburg-Mitte (263 Tsd. m²) (`rt_d0346677dc8f077d`) | HAUPT | 14.3 | 0.74 | 0.85 | 0.12 | 1.68 | 0.57 → 0.78 | 0.68 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569013,5931962]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.532036/10.041212) · [OSM](https://www.openstreetmap.org/?mlat=53.532036&mlon=10.041212#map=18/53.532036/10.041212) |
| 10 | Innenstadt (Rathausmarkt) – Umsteigeknoten Hamburg-Harburg (`rt_01ce314479204899`) | RSV | 13.8 | 0.61 | 0.72 | 0.11 | 1.56 | 0.57 → 0.73 | 0.61 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565247,5929856]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.513591/9.983962) · [OSM](https://www.openstreetmap.org/?mlat=53.513591&mlon=9.983962#map=18/53.513591/9.983962) |
| 11 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Harburg (241 Tsd. m²) (`rt_f16d9e5fc98b74d3`) | RSV | 13.4 | 0.61 | 0.72 | 0.11 | 1.51 | 0.58 → 0.74 | 0.62 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565220,5930046]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.515299/9.983596) · [OSM](https://www.openstreetmap.org/?mlat=53.515299&mlon=9.983596#map=18/53.515299/9.983596) |
| 12 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Bergedorf (224 Tsd. m²) (`rt_f148bb5f25fd2127`) | HAUPT | 12.5 | 0.70 | 0.81 | 0.11 | 1.42 | 0.55 → 0.76 | 0.65 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570219,5931700]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.529524/10.059349) · [OSM](https://www.openstreetmap.org/?mlat=53.529524&mlon=10.059349#map=18/53.529524/10.059349) |
| 13 | Innenstadt (Rathausmarkt) – Umsteigeknoten Bergedorf (`rt_e91f74bd5e0fdea8`) | RSV | 18.8 | 0.64 | 0.72 | 0.07 | 1.39 | 0.63 → 0.73 | 0.75 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573736,5933031]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.541004/10.112699) · [OSM](https://www.openstreetmap.org/?mlat=53.541004&mlon=10.112699#map=18/53.541004/10.112699) |
| 14 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Nord (307 Tsd. m²) (`rt_dfa72f03b92f11e4`) | RSV | 12.9 | 0.57 | 0.68 | 0.11 | 1.38 | 0.62 → 0.72 | 0.53 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568341,5938662]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.592332/10.032533) · [OSM](https://www.openstreetmap.org/?mlat=53.592332&mlon=10.032533#map=18/53.592332/10.032533) |
| 15 | Umsteigeknoten Neugraben – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_1f65359785a52cea`) | HAUPT | 10.2 | 0.73 | 0.86 | 0.13 | 1.36 | 0.62 → 0.82 | 0.58 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559820,5926567]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.484673/9.901500) · [OSM](https://www.openstreetmap.org/?mlat=53.484673&mlon=9.901500#map=18/53.484673/9.901500) |
| 16 | Arbeitsplatzschwerpunkt Hamburg-Mitte (278 Tsd. m²) – Arbeitsplatzschwerpunkt Bergedorf (224 Tsd. m²) (`rt_5be88c5238ed113e`) | HAUPT | 7.1 | 0.66 | 0.84 | 0.19 | 1.34 | 0.45 → 0.81 | 0.50 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572709,5930397]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.517468/10.096597) · [OSM](https://www.openstreetmap.org/?mlat=53.517468&mlon=10.096597#map=18/53.517468/10.096597) |
| 17 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) (`rt_312c55eaf10e71ed`) | HAUPT | 12.0 | 0.70 | 0.81 | 0.11 | 1.34 | 0.55 → 0.75 | 0.66 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569982,5931778]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.530255/10.055787) · [OSM](https://www.openstreetmap.org/?mlat=53.530255&mlon=10.055787#map=18/53.530255/10.055787) |
| 18 | Umsteigeknoten Altona – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_3b5657ead1bad7ac`) | HAUPT | 10.9 | 0.67 | 0.80 | 0.12 | 1.33 | 0.55 → 0.77 | 0.70 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557645,5933527]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.547474/9.870014) · [OSM](https://www.openstreetmap.org/?mlat=53.547474&mlon=9.870014#map=18/53.547474/9.870014) |
| 19 | Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) – Arbeitsplatzschwerpunkt Altona (226 Tsd. m²) (`rt_9fe1aad7bdd69990`) | HAUPT | 9.8 | 0.75 | 0.88 | 0.13 | 1.26 | 0.64 → 0.81 | 0.64 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560124,5935043]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560821/9.907711) · [OSM](https://www.openstreetmap.org/?mlat=53.560821&mlon=9.907711#map=18/53.560821/9.907711) |
| 20 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) (`rt_49c8cf1fbb966392`) | HAUPT | 13.2 | 0.61 | 0.71 | 0.09 | 1.24 | 0.57 → 0.72 | 0.73 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562986,5933966]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.550802/9.950704) · [OSM](https://www.openstreetmap.org/?mlat=53.550802&mlon=9.950704#map=18/53.550802/9.950704) |
| 21 | Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) – Arbeitsplatzschwerpunkt Hamburg-Mitte (278 Tsd. m²) (`rt_e3d331b9b5cc9556`) | HAUPT | 6.6 | 0.65 | 0.84 | 0.19 | 1.23 | 0.45 → 0.81 | 0.52 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572886,5930550]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.518820/10.099305) · [OSM](https://www.openstreetmap.org/?mlat=53.518820&mlon=10.099305#map=18/53.518820/10.099305) |
| 22 | Verdichtung HAUPT: Niendorfer Gehege (`rt_c0464578be8fb33b`) | HAUPT | 7.2 | 0.62 | 0.79 | 0.17 | 1.21 | 0.57 → 0.81 | 0.52 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560322,5940791]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.612452/9.911817) · [OSM](https://www.openstreetmap.org/?mlat=53.612452&mlon=9.911817#map=18/53.612452/9.911817) |
| 23 | Hochschule HAW Hamburg Energie Campus – Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) (`rt_ffc8cc9c45cd1719`) | HAUPT | 9.6 | 0.76 | 0.88 | 0.12 | 1.18 | 0.60 → 0.81 | 0.61 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577281,5927329]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.489250/10.164780) · [OSM](https://www.openstreetmap.org/?mlat=53.489250&mlon=10.164780#map=18/53.489250/10.164780) |
| 24 | Umsteigeknoten Hamburg-Harburg – Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) (`rt_463b00cfca1d45be`) | RSV | 7.4 | 0.52 | 0.68 | 0.15 | 1.14 | 0.60 → 0.80 | 0.33 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562896,5925065]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470813/9.947549) · [OSM](https://www.openstreetmap.org/?mlat=53.470813&mlon=9.947549#map=18/53.470813/9.947549) |
| 25 | Verdichtung HAUPT: neben Osdorfer Landstraße (`rt_72d1850ab8acbd17`) | HAUPT | 9.2 | 0.57 | 0.70 | 0.12 | 1.14 | 0.60 → 0.76 | 0.51 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554538,5936526]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.574756/9.823643) · [OSM](https://www.openstreetmap.org/?mlat=53.574756&mlon=9.823643#map=18/53.574756/9.823643) |
| 26 | Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) – Arbeitsplatzschwerpunkt Harburg (241 Tsd. m²) (`rt_a3f51202ca48fa1c`) | RSV | 6.8 | 0.51 | 0.68 | 0.17 | 1.14 | 0.56 → 0.78 | 0.34 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562608,5925087]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.471045/9.943226) · [OSM](https://www.openstreetmap.org/?mlat=53.471045&mlon=9.943226#map=18/53.471045/9.943226) |
| 27 | Innenstadt (Rathausmarkt) – Hochschule HAW - Life Sciences - Campus Bergedorf (`rt_0d622f210ba0d8d0`) | RSV | 18.1 | 0.65 | 0.71 | 0.06 | 1.13 | 0.64 → 0.73 | 0.81 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573428,5933191]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.542486/10.108102) · [OSM](https://www.openstreetmap.org/?mlat=53.542486&mlon=10.108102#map=18/53.542486/10.108102) |
| 28 | Verdichtung HAUPT: Little Whistler (`rt_08c9b542408be57e`) | HAUPT | 4.3 | 0.53 | 0.80 | 0.26 | 1.12 | 0.42 → 0.83 | 0.07 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560773,5923351]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.455657/9.915248) · [OSM](https://www.openstreetmap.org/?mlat=53.455657&mlon=9.915248#map=18/53.455657/9.915248) |
| 29 | Innenstadt (Rathausmarkt) – Hochschule Technologiezentrum Hamburg-Finkenwerder (`rt_76e351b7ff2f7d14`) | HAUPT | 12.3 | 0.61 | 0.70 | 0.09 | 1.12 | 0.56 → 0.71 | 0.73 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562544,5934070]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.551790/9.944056) · [OSM](https://www.openstreetmap.org/?mlat=53.551790&mlon=9.944056#map=18/53.551790/9.944056) |
| 30 | Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_9978d70cbf7eefbe`) | HAUPT | 6.9 | 0.73 | 0.89 | 0.16 | 1.11 | 0.55 → 0.83 | 0.67 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558090,5932012]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.533804/9.876452) · [OSM](https://www.openstreetmap.org/?mlat=53.533804&mlon=9.876452#map=18/53.533804/9.876452) |

Höchster Δ einer Route (ohne Längengewicht): 0.30; Routen mit Δ ≥ 0,2: 192.

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
| Zusammenhang | 0.200 | 0.240 | 30/30 | 0.998 |
| Direktheit | 0.250 | 0.200 | 30/30 | 1.000 |
| Direktheit | 0.250 | 0.300 | 30/30 | 1.000 |
| Sicherheit | 0.300 | 0.240 | 29/30 | 0.996 |
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
| Bergedorf | 194 | 0.73 | 0.82 | 0.09 |
| Eimsbüttel | 362 | 0.70 | 0.78 | 0.08 |
| Hamburg-Mitte | 481 | 0.71 | 0.80 | 0.09 |
| Hamburg-Nord | 415 | 0.70 | 0.78 | 0.08 |
| Harburg | 266 | 0.69 | 0.79 | 0.10 |
| Wandsbek | 823 | 0.71 | 0.80 | 0.08 |

## Stichprobe: 30 zufällige Kanten (Seed 42, nach Bezirk verteilt)

| Kante | Name | Kategorie | Führung Ist → Soll | Breite / Soll | Belag | lit | Score Ist / Soll | Prüfen |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| `ce_0e844a824c1521f6` | Walderseestraße / Bosselkamp / Gottorpstraße | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.70 / 0.75 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559425,5934781]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.558544/9.897105) · [OSM](https://www.openstreetmap.org/?mlat=53.558544&mlon=9.897105#map=18/53.558544/9.897105) |
| `ce_3abe80566402e079` | Seestraße | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.66 / 0.71 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557941,5936027]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.569907/9.874942) · [OSM](https://www.openstreetmap.org/?mlat=53.569907&mlon=9.874942#map=18/53.569907/9.874942) |
| `ce_7eefe0d97e280200` | Langenfelder Straße | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.66 / 0.70 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563024,5935657]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.565992/9.951607) · [OSM](https://www.openstreetmap.org/?mlat=53.565992&mlon=9.951607#map=18/53.565992/9.951607) |
| `ce_8e0d5f866cb7b1c4` | Achtern Born | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.75 / 0.83 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556376,5937915]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.587047/9.851652) · [OSM](https://www.openstreetmap.org/?mlat=53.587047&mlon=9.851652#map=18/53.587047/9.851652) |
| `ce_28e49f052a0c6b34` | Riehlstraße | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | – | 0.77 / 0.86 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579456,5928352]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.498120/10.197821) · [OSM](https://www.openstreetmap.org/?mlat=53.498120&mlon=10.197821#map=18/53.498120/10.197821) |
| `ce_40fff4aa5ba545a9` | – | BASIS | eigener Weg → eigener Weg | – / 3.00 | asphalt | ja | 0.89 / 0.90 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578586,5927375]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.489471/10.184463) · [OSM](https://www.openstreetmap.org/?mlat=53.489471&mlon=10.184463#map=18/53.489471/10.184463) |
| `ce_1a37334ae737e10d` | Haseldorfer Weg | HAUPT | Zweirichtungsradweg → Fahrradstraße | – / 3.50 | asphalt | ja | 0.66 / 0.71 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559198,5940258]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607790/9.894721) · [OSM](https://www.openstreetmap.org/?mlat=53.607790&mlon=9.894721#map=18/53.607790/9.894721) |
| `ce_b096d3a4467d9652` | Bundesstraße | BASIS | Zweirichtungsradweg → Mischverkehr | – / 3.00 | paving_stones | ja | 0.74 / 0.79 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564150,5936350]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.572090/9.968761) · [OSM](https://www.openstreetmap.org/?mlat=53.572090&mlon=9.968761#map=18/53.572090/9.968761) |
| `ce_c2390b9ee654503e` | – | HAUPT | eigener Weg → eigener Weg | 2.50 / 3.50 | asphalt | ja | 0.82 / 0.84 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563748,5936094]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.569835/9.962626) · [OSM](https://www.openstreetmap.org/?mlat=53.569835&mlon=9.962626#map=18/53.569835/9.962626) |
| `ce_c31ac66f7681d93b` | – | HAUPT | eigener Weg → eigener Weg | – / 3.50 | asphalt | ja | 0.74 / 0.74 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565869,5935543]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564620/9.994545) · [OSM](https://www.openstreetmap.org/?mlat=53.564620&mlon=9.994545#map=18/53.564620/9.994545) |
| `ce_0ccf652dc17f847e` | Vogelhüttendeich | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.73 / 0.78 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565418,5930310]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.517647/9.986630) · [OSM](https://www.openstreetmap.org/?mlat=53.517647&mlon=9.986630#map=18/53.517647/9.986630) |
| `ce_22a3dfc8100c4201` | Hauptweg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | – | 0.78 / 0.87 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571210,5933226]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.543099/10.074638) · [OSM](https://www.openstreetmap.org/?mlat=53.543099&mlon=10.074638#map=18/53.543099/10.074638) |
| `ce_b12977390f142d35` | neben Ballindamm | HAUPT | Radweg je Seite → Fahrradstraße | 3.00 / 2.50 | asphalt | ja | 0.69 / 0.74 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565885,5934143]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.552040/9.994485) · [OSM](https://www.openstreetmap.org/?mlat=53.552040&mlon=9.994485#map=18/53.552040/9.994485) |
| `ce_e643a0fa8bfd4dc0` | Vogelhüttendeich | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.77 / 0.82 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565672,5930209]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.516708/9.990452) · [OSM](https://www.openstreetmap.org/?mlat=53.516708&mlon=9.990452#map=18/53.516708/9.990452) |
| `ce_f8380738ba233ae6` | neben Amsinckstraße | HAUPT | Radweg je Seite → Radweg je Seite | 1.80 / 2.50 | paving_stones | ja | 0.64 / 0.73 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567430,5933402]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.545181/10.017636) · [OSM](https://www.openstreetmap.org/?mlat=53.545181&mlon=10.017636#map=18/53.545181/10.017636) |
| `ce_0b2bd77f586d4e37` | Lokstedter Weg | BASIS | Mischverkehr → Radfahrstreifen | – / – | asphalt | ja | 0.70 / 0.81 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565119,5938994]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.595731/9.983944) · [OSM](https://www.openstreetmap.org/?mlat=53.595731&mlon=9.983944#map=18/53.595731/9.983944) |
| `ce_26ca28b01b057873` | Lengerckestraße | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.86 / 0.91 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570619,5937335]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.580110/10.066657) · [OSM](https://www.openstreetmap.org/?mlat=53.580110&mlon=10.066657#map=18/53.580110/10.066657) |
| `ce_5f136c39f26218f3` | Sengelmannstraße | BASIS | Mischverkehr → Mischverkehr | – / – | asphalt | ja | 0.70 / 0.70 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566908,5942048]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.622952/10.011617) · [OSM](https://www.openstreetmap.org/?mlat=53.622952&mlon=10.011617#map=18/53.622952/10.011617) |
| `ce_6596be3e394a38bd` | Bramfelder Straße | HAUPT | Radweg je Seite → Radweg je Seite | – / 2.50 | asphalt | ja | 0.61 / 0.61 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569256,5937603]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.582701/10.046127) · [OSM](https://www.openstreetmap.org/?mlat=53.582701&mlon=10.046127#map=18/53.582701/10.046127) |
| `ce_d78c701f0c180531` | Dorotheenstraße | RSV | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.66 / 0.71 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566320,5938536]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.591467/10.001980) · [OSM](https://www.openstreetmap.org/?mlat=53.591467&mlon=10.001980#map=18/53.591467/10.001980) |
| `ce_0ea8f04d1f51c171` | Goeschenstraße | BASIS | Mischverkehr → Mischverkehr | – / – | sett | ja | 0.67 / 0.82 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564679,5923625]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.457663/9.974119) · [OSM](https://www.openstreetmap.org/?mlat=53.457663&mlon=9.974119#map=18/53.457663/9.974119) |
| `ce_5e1d7512b6844ad4` | Reeseberg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.69 / 0.75 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[566161,5922251]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.445124/9.996141) · [OSM](https://www.openstreetmap.org/?mlat=53.445124&mlon=9.996141#map=18/53.445124/9.996141) |
| `ce_c6c1a7612f4fde57` | Wilstorfer Straße | HAUPT | Mischverkehr → Radweg je Seite | – / – | asphalt | ja | 0.59 / 0.70 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565583,5923003]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.451954/9.987605) · [OSM](https://www.openstreetmap.org/?mlat=53.451954&mlon=9.987605#map=18/53.451954/9.987605) |
| `ce_01fe1d06d08fb2a4` | Müssenredder | HAUPT | Mischverkehr → Fahrradstraße | – / – | nan | ja | 0.61 / 0.73 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571422,5945713]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.655292/10.080706) · [OSM](https://www.openstreetmap.org/?mlat=53.655292&mlon=10.080706#map=18/53.655292/10.080706) |
| `ce_402923a88dd05f66` | – | HAUPT | eigener Weg → eigener Weg | – / 3.50 | unpaved | nein | 0.56 / 0.81 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574776,5951170]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.703860/10.132760) · [OSM](https://www.openstreetmap.org/?mlat=53.703860&mlon=10.132760#map=18/53.703860/10.132760) |
| `ce_50b9011ec40a1298` | Moorbekring | BASIS | Mischverkehr → Mischverkehr | – / – | asphalt | ja | 0.74 / 0.74 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[578695,5945493]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.652271/10.190670) · [OSM](https://www.openstreetmap.org/?mlat=53.652271&mlon=10.190670#map=18/53.652271/10.190670) |
| `ce_7fc87a2b6a50ad2e` | – | BASIS | eigener Weg → eigener Weg | – / 3.00 | fine_gravel | nein | 0.52 / 0.77 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[571895,5941134]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.614074/10.086798) · [OSM](https://www.openstreetmap.org/?mlat=53.614074&mlon=10.086798#map=18/53.614074/10.086798) |
| `ce_a7f22b862d0928dd` | Wartenburger Weg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.77 / 0.82 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570799,5938495]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.590511/10.069631) · [OSM](https://www.openstreetmap.org/?mlat=53.590511&mlon=10.069631#map=18/53.590511/10.069631) |
| `ce_e742e95398b80988` | Kroonstücken | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.69 / 0.79 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573747,5937108]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.577636/10.113827) · [OSM](https://www.openstreetmap.org/?mlat=53.577636&mlon=10.113827#map=18/53.577636/10.113827) |
| `ce_f8aa68b17acfd60e` | Machandelstieg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.81 / 0.86 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572424,5942721]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.628269/10.095166) · [OSM](https://www.openstreetmap.org/?mlat=53.628269&mlon=10.095166#map=18/53.628269/10.095166) |

## Durchsicht mit Ortskundigen

20 Routen (nach Kategorie geschichtet, Seed 42, C-PRI-15) in `reports/cycle_principles_review.csv` mit Links und leeren Spalten für Einschätzung und Kommentar.

## Hinweise

- Soll-Führung je Kante vorläufig direkt aus der Trennungsmatrix (bevorzugte Führung); Prompt 18 legt Führung und Breite je Abschnitt fest, danach P-SAF-01/P-COM-01 (Soll) mit dessen Ergebnis rechnen.
- Halte und Zeitverlust (P-DIR-02/03) im Soll wie im Ist, bis Prompt 20 Soll-Knotentypen liefert; P-SAF-02 bis dahin unbekannt.
- Unfälle (P-SAF-04) bleiben im Soll unverändert (keine Wirkungsprognose).
- Nachfrage und Netz beruhen auf dem mäßig kalibrierten Modell aus Prompt 15 (reports/cycle_demand.md).

Quellen: OpenStreetMap-Beitragende (ODbL); ALKIS © Freie und Hansestadt Hamburg, LGV (dl-de/by-2.0); Unfallatlas © Statistische Ämter des Bundes und der Länder (dl-de/by-2.0); HVV-GTFS © Hamburger Verkehrsverbund GmbH (dl-de/by-2.0).
