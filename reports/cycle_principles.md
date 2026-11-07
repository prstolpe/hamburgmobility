# Fünf Prinzipien: Bewertung des Soll-Radnetzes (Stufe c04)

Erzeugt 2026-11-07T13:11:07+00:00 mit pipeline/c04_principles.py · cycling_rules.yaml 0.7.0 · nicht amtlicher Entwurf. Alle Bewertungsregeln (C-PRI-01…16) und die Gewichte sind Annahmen (source_type assumption, status draft) und vor fachlicher Nutzung zu prüfen.

**score_ist** bewertet den heutigen Zustand der Soll-Route, **score_soll** den Zustand nach regelkonformem Ausbau (Führung nach Trennungsmatrix, Sollbreite, geschlossene Decke, Beleuchtung). Die Differenz ist der Handlungsbedarf. Fehlende Daten senken die confidence, nicht den Score.

## Kurzfassung

- RSV: 51 km, Score Ist 0.57 → Soll 0.69
- HAUPT: 1 841 km, Score Ist 0.67 → Soll 0.77
- BASIS: 1 061 km, Score Ist 0.78 → Soll 0.83
- Führung entspricht heute der Trennungsmatrix auf 49 % der Netzlänge mit bekannter Führung (RSV/HAUPT: 27 %).
- 5008 Routen bewertet; mittlerer Handlungsbedarf (score_soll − score_ist) 0.06, confidence: high 1898, medium 3110, low 0.
- Nicht bewertbar mangels Daten: P-SAF-02 (Knotentypen erst mit Prompt 20 (pipeline/c07_junctions.py)), P-COM-03 (kein Höhenmodell geladen (sources.yaml laserscan ohne Abruf)), P-ATT-02 (keine Lärmkarte (sources.yaml noise_maps ohne Endpunkt, Entscheidung 2026-11-06)).

## Datenlage je Prüfung

Anteil der Länge des Soll-Netzes (RSV, HAUPT, BASIS) mit Wert, unter den Kanten, für die die Prüfung anwendbar ist.

| Prüfung | Prinzip | Datengrundlage | anwendbar (km) | mit Wert |
| --- | --- | --- | ---: | ---: |
| P-COH-01 | Zusammenhang | c03 Maschen | 2 954 | 100 % |
| P-COH-02 | Zusammenhang | Soll-Netz | 2 953 | 100 % |
| P-COH-04 | Zusammenhang | Ist-Führung entlang der Route | 2 953 | 100 % |
| P-DIR-01 | Direktheit | Radgraph (Länge) | 2 953 | 99 % |
| P-DIR-02 | Direktheit | OSM-LSA, Vorfahrt C-GRAPH-05 | 2 953 | 100 % |
| P-DIR-03 | Direktheit | wie P-DIR-02 | 1 893 | 100 % |
| P-SAF-01 | Sicherheit | Ist-Führung (C-PRI-02), Trennungsmatrix | 2 897 | 100 % |
| P-SAF-02 | Sicherheit | – | 2 954 | 0 % |
| P-SAF-03 | Sicherheit | OSM lit | 2 954 | 85 % |
| P-SAF-04 | Sicherheit | Unfallatlas | 2 954 | 100 % |
| P-COM-01 | Komfort | OSM width/cycleway:width | 1 275 | 11 % |
| P-COM-02 | Komfort | OSM surface | 2 954 | 96 % |
| P-COM-03 | Komfort | – | 2 954 | 0 % |
| P-ATT-01 | Attraktivität | ALKIS, OSM-Bäume | 2 954 | 100 % |
| P-ATT-02 | Attraktivität | – | 2 954 | 0 % |
| P-ATT-03 | Attraktivität | DTV 2019 (HVS) | 2 954 | 100 % |

## Netzkennzahlen je Kategorie

Längengewichtete Mittel über die Kanten der Kategorie (Kantenwerte für Direktheit und Zusammenhang aus der Hauptroute der Kante).

| Kategorie | km | Zusammenhang Ist / Soll | Direktheit Ist / Soll | Sicherheit Ist / Soll | Komfort Ist / Soll | Attraktivität Ist / Soll | Gesamt Ist / Soll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| RSV | 51 | 0.33 / 0.35 | 0.67 / 0.67 | 0.68 / 0.79 | 0.46 / 1.00 | 0.65 / 0.65 | 0.57 / 0.69 |
| HAUPT | 1 841 | 0.68 / 0.71 | 0.66 / 0.66 | 0.64 / 0.82 | 0.69 / 1.00 | 0.70 / 0.70 | 0.67 / 0.77 |
| BASIS | 1 061 | 0.78 / 0.79 | 0.80 / 0.80 | 0.75 / 0.82 | 0.87 / 1.00 | 0.71 / 0.71 | 0.78 / 0.83 |

## Zusammenhang (P-COH)

**P-COH-01 Maschenweite** (aus c03, cycle_mesh_gaps.parquet):

| Ebene | Höchstweite | zu große Maschen | Seite Median | Seite max |
| --- | ---: | ---: | ---: | ---: |
| HAUPT | 600 m | 33 | 899 m | 4 956 m |
| BASIS | 300 m | 410 | 411 m | 4 071 m |

**P-COH-02 Komponenten** (je Ebene mit höheren Ebenen):

| Ebene | Komponenten | Anteil größte Komponente (Länge) |
| --- | ---: | ---: |
| RSV | 5 | 25 % |
| HAUPT | 1 | 100 % |
| BASIS | 1 | 100 % |

**P-COH-03 Abdeckung** (Ziele höchstens 300 m vom RSV/HAUPT-Netz; Zentren fehlen, kein Datensatz):

| Ziele | Anzahl | abgedeckt |
| --- | ---: | ---: |
| Schulen (OSM) | 557 | 95 % |
| Schnellbahnhalte | 375 | 99 % |
| Hochschulen (OSM university) | 41 | 100 % |

**P-COH-04 Kontinuität:** Wechsel der Ist-Führung je km (Median über Routen) 1.08, Soll (Führung und Kategorie) 0.00; Schwelle 1.0 je km (C-PRI-12).

## Direktheit (P-DIR)

**P-DIR-01 Umwegfaktor, Netzstichprobe** (C-PRI-04): je Kategorie 200 OD-Paare, Seed 42, Knoten der größten Komponente der Ebene (mit höheren Ebenen), Luftlinie im Band trip_length_km. Netzweg auf der Ebene gegen kürzesten Weg auf allen befahrbaren Kanten (Länge).

| Kategorie | Band (km) | Paare | ohne Weg | Median | 90-%-Wert | Schwelle | Anteil ≤ Schwelle |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RSV | 5–15 | 200 | 0 | 1.05 | 1.05 | 1.1 | 100 % |
| HAUPT | 2–3 | 200 | 0 | 1.17 | 2.91 | 1.2 | 52 % |
| BASIS | 1–2 | 200 | 0 | 1.06 | 2.63 | 1.3 | 76 % |

**Je Route** (Median über Routen der Kategorie; Halte nach C-PRI-05, Soll = Ist bis Prompt 20):

| Kategorie | Routen | Umwegfaktor | Halte/km | Schwelle Halte | Zeitverlust s/km | Schwelle s/km |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RSV | 20 | 1.08 | 1.7 | 0.5 | 21 | 30 |
| HAUPT | 1999 | 1.10 | 1.1 | 1.0 | 11 | 30 |
| BASIS | 2989 | 1.00 | 0.0 | 2.0 | 0 | – |

## Sicherheit (P-SAF)

**P-SAF-01 Ist-Führung gegen Soll-Führung** (km, Kanten RSV/HAUPT/BASIS):

| Ist \ Soll | Radfahrstreifen | Fahrradstraße | Mischverkehr | eigener Weg | Radweg je Seite | unbekannt |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Radfahrstreifen | 7 | 29 | 16 | 0 | 34 | 0 |
| Fahrradstraße | 0 | 18 | 2 | 0 | 0 | 0 |
| Mischverkehr | 10 | 950 | 619 | 0 | 53 | 41 |
| eigener Weg | 0 | 0 | 0 | 411 | 0 | 0 |
| Radweg je Seite | 16 | 99 | 46 | 0 | 260 | 7 |
| Zweirichtungsradweg | 9 | 105 | 51 | 11 | 149 | 4 |
| unbekannt | 0 | 0 | 0 | 0 | 0 | 5 |

P-SAF-03 Beleuchtung: OSM lit auf 85 % der Netzlänge bekannt; davon beleuchtet 90 %. P-SAF-04 Unfälle mit Radbeteiligung 2021–2025: 7 656 Unfälle an Kanten des Soll-Netzes (je Kante höchstens 15 m entfernt; nur Summen gespeichert).

## Komfort und Attraktivität (P-COM, P-ATT)

- P-COM-01 Breite: anwendbar auf 1 275 km (ohne Mischverkehr), Breite in OSM auf 11 % davon; von diesen erreichen 20 % die Sollbreite.
- P-COM-02 Belag: bekannt auf 96 %; RSV/HAUPT mit geschlossener Decke 68 %.
- P-ATT-01 Grünanteil im 20-m-Puffer: Median 13 % (Ziel 30 %, ALKIS-Grünflächen und OSM-Bäume).
- P-ATT-03: 329 km des Soll-Netzes liegen an Straßen mit DTV > 15 000.

## Top 30 Routen mit dem größten Handlungsbedarf

Rangfolge nach Handlungsbedarf-km = (score_soll − score_ist) × Länge in km (C-PRI-14), damit lange Routen mit mittlerem Defizit vor sehr kurzen Verdichtungsstücken stehen. S/K: Sicherheit und Komfort Ist → Soll.

| # | Route | Kategorie | km | Ist | Soll | Δ | Δ × km | S | K | confidence | Prüfen |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 1 | Innenstadt (Rathausmarkt) – Umsteigeknoten Neugraben (`rt_ef74f810d825e8b0`) | RSV | 23.8 | 0.58 | 0.71 | 0.13 | 3.16 | 0.66 → 0.78 | 0.37 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563960,5924903]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.469229/9.963550) · [OSM](https://www.openstreetmap.org/?mlat=53.469229&mlon=9.963550#map=18/53.469229/9.963550) |
| 2 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) (`rt_ad15aafddcc3fd36`) | RSV | 20.3 | 0.57 | 0.71 | 0.13 | 2.74 | 0.65 → 0.77 | 0.36 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565304,5924573]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.466099/9.983721) · [OSM](https://www.openstreetmap.org/?mlat=53.466099&mlon=9.983721#map=18/53.466099/9.983721) |
| 3 | Umsteigeknoten Neugraben – Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) (`rt_a1437067c8713aec`) | HAUPT | 16.2 | 0.73 | 0.87 | 0.14 | 2.33 | 0.59 → 0.83 | 0.60 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560451,5929359]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.509694/9.911549) · [OSM](https://www.openstreetmap.org/?mlat=53.509694&mlon=9.911549#map=18/53.509694/9.911549) |
| 4 | Umsteigeknoten Neugraben – Hochschule Technologiezentrum Hamburg-Finkenwerder (`rt_fa57d47917cbb47c`) | HAUPT | 15.3 | 0.73 | 0.87 | 0.14 | 2.16 | 0.59 → 0.83 | 0.61 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560443,5928887]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.505453/9.911335) · [OSM](https://www.openstreetmap.org/?mlat=53.505453&mlon=9.911335#map=18/53.505453/9.911335) |
| 5 | Arbeitsplatzschwerpunkt Hamburg-Mitte (263 Tsd. m²) – Arbeitsplatzschwerpunkt Bergedorf (224 Tsd. m²) (`rt_89d0e0b926b16b75`) | HAUPT | 14.9 | 0.74 | 0.86 | 0.12 | 1.78 | 0.57 → 0.78 | 0.67 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569145,5931763]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.530232/10.043163) · [OSM](https://www.openstreetmap.org/?mlat=53.530232&mlon=10.043163#map=18/53.530232/10.043163) |
| 6 | Innenstadt (Rathausmarkt) – Hochschule Gebäude D (`rt_b3e5311382ffdee5`) | RSV | 15.3 | 0.61 | 0.72 | 0.11 | 1.74 | 0.68 → 0.77 | 0.42 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565862,5926294]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.481498/9.992496) · [OSM](https://www.openstreetmap.org/?mlat=53.481498&mlon=9.992496#map=18/53.481498/9.992496) |
| 7 | Innenstadt (Rathausmarkt) – Hochschule HAW Hamburg Energie Campus (`rt_3f2cb5eac8db9800`) | RSV | 20.6 | 0.64 | 0.72 | 0.08 | 1.73 | 0.64 → 0.73 | 0.66 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573859,5932112]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.532725/10.114342) · [OSM](https://www.openstreetmap.org/?mlat=53.532725&mlon=10.114342#map=18/53.532725/10.114342) |
| 8 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_3a0535e6b916dd87`) | HAUPT | 12.9 | 0.70 | 0.84 | 0.13 | 1.71 | 0.56 → 0.76 | 0.58 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564309,5933531]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.546728/9.970578) · [OSM](https://www.openstreetmap.org/?mlat=53.546728&mlon=9.970578#map=18/53.546728/9.970578) |
| 9 | Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) – Arbeitsplatzschwerpunkt Hamburg-Mitte (263 Tsd. m²) (`rt_581c9b764c31051f`) | HAUPT | 14.3 | 0.74 | 0.85 | 0.12 | 1.70 | 0.57 → 0.78 | 0.67 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569013,5931962]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.532038/10.041212) · [OSM](https://www.openstreetmap.org/?mlat=53.532038&mlon=10.041212#map=18/53.532038/10.041212) |
| 10 | Innenstadt (Rathausmarkt) – Umsteigeknoten Hamburg-Harburg (`rt_82768bcf84d75ee6`) | RSV | 14.4 | 0.62 | 0.72 | 0.10 | 1.50 | 0.68 → 0.75 | 0.46 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565881,5930202]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.516617/9.993598) · [OSM](https://www.openstreetmap.org/?mlat=53.516617&mlon=9.993598#map=18/53.516617/9.993598) |
| 11 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Bergedorf (224 Tsd. m²) (`rt_691eee243ae51138`) | HAUPT | 12.4 | 0.70 | 0.81 | 0.12 | 1.43 | 0.55 → 0.76 | 0.64 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570251,5931674]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.529279/10.059822) · [OSM](https://www.openstreetmap.org/?mlat=53.529279&mlon=10.059822#map=18/53.529279/10.059822) |
| 12 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Harburg (241 Tsd. m²) (`rt_2a3981f4e8e27282`) | RSV | 13.9 | 0.62 | 0.73 | 0.10 | 1.43 | 0.69 → 0.77 | 0.47 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565713,5926950]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.487410/9.990387) · [OSM](https://www.openstreetmap.org/?mlat=53.487410&mlon=9.990387#map=18/53.487410/9.990387) |
| 13 | Innenstadt (Rathausmarkt) – Umsteigeknoten Bergedorf (`rt_04983fdf6c08b203`) | RSV | 18.6 | 0.64 | 0.72 | 0.08 | 1.41 | 0.63 → 0.73 | 0.73 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573807,5932951]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.540271/10.113752) · [OSM](https://www.openstreetmap.org/?mlat=53.540271&mlon=10.113752#map=18/53.540271/10.113752) |
| 14 | Umsteigeknoten Altona – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_3b5657ead1bad7ac`) | HAUPT | 10.9 | 0.68 | 0.80 | 0.12 | 1.36 | 0.55 → 0.77 | 0.70 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[557645,5933527]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.547474/9.870014) · [OSM](https://www.openstreetmap.org/?mlat=53.547474&mlon=9.870014#map=18/53.547474/9.870014) |
| 15 | Umsteigeknoten Neugraben – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_1f65359785a52cea`) | HAUPT | 10.2 | 0.73 | 0.86 | 0.13 | 1.36 | 0.62 → 0.82 | 0.58 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559820,5926567]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.484673/9.901500) · [OSM](https://www.openstreetmap.org/?mlat=53.484673&mlon=9.901500#map=18/53.484673/9.901500) |
| 16 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) (`rt_4c7fbf3a9175713b`) | HAUPT | 11.9 | 0.70 | 0.81 | 0.11 | 1.36 | 0.55 → 0.75 | 0.65 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[570023,5931770]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.530175/10.056400) · [OSM](https://www.openstreetmap.org/?mlat=53.530175&mlon=10.056400#map=18/53.530175/10.056400) |
| 17 | Arbeitsplatzschwerpunkt Hamburg-Mitte (278 Tsd. m²) – Arbeitsplatzschwerpunkt Bergedorf (224 Tsd. m²) (`rt_5be88c5238ed113e`) | HAUPT | 7.1 | 0.66 | 0.84 | 0.19 | 1.34 | 0.45 → 0.81 | 0.50 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572709,5930397]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.517468/10.096597) · [OSM](https://www.openstreetmap.org/?mlat=53.517468&mlon=10.096597#map=18/53.517468/10.096597) |
| 18 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Nord (307 Tsd. m²) (`rt_9495f3dbb07d7452`) | RSV | 12.9 | 0.58 | 0.68 | 0.10 | 1.33 | 0.62 → 0.72 | 0.55 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568340,5938666]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.592369/10.032524) · [OSM](https://www.openstreetmap.org/?mlat=53.592369&mlon=10.032524#map=18/53.592369/10.032524) |
| 19 | Innenstadt (Rathausmarkt) – Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) (`rt_6cc83bd6e2bc969d`) | HAUPT | 13.1 | 0.59 | 0.68 | 0.10 | 1.26 | 0.58 → 0.72 | 0.69 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563004,5934485]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.555468/9.951076) · [OSM](https://www.openstreetmap.org/?mlat=53.555468&mlon=9.951076#map=18/53.555468/9.951076) |
| 20 | Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) – Arbeitsplatzschwerpunkt Altona (226 Tsd. m²) (`rt_9fe1aad7bdd69990`) | HAUPT | 9.8 | 0.75 | 0.88 | 0.13 | 1.26 | 0.64 → 0.82 | 0.64 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560124,5935043]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560821/9.907711) · [OSM](https://www.openstreetmap.org/?mlat=53.560821&mlon=9.907711#map=18/53.560821/9.907711) |
| 21 | Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) – Arbeitsplatzschwerpunkt Hamburg-Mitte (278 Tsd. m²) (`rt_e3d331b9b5cc9556`) | HAUPT | 6.6 | 0.65 | 0.84 | 0.19 | 1.23 | 0.45 → 0.81 | 0.52 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572886,5930550]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.518820/10.099305) · [OSM](https://www.openstreetmap.org/?mlat=53.518820&mlon=10.099305#map=18/53.518820/10.099305) |
| 22 | Verdichtung HAUPT: Niendorfer Gehege (`rt_c0464578be8fb33b`) | HAUPT | 7.2 | 0.63 | 0.79 | 0.17 | 1.21 | 0.57 → 0.81 | 0.52 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560322,5940791]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.612452/9.911817) · [OSM](https://www.openstreetmap.org/?mlat=53.612452&mlon=9.911817#map=18/53.612452/9.911817) |
| 23 | Hochschule HAW Hamburg Energie Campus – Arbeitsplatzschwerpunkt Bergedorf (549 Tsd. m²) (`rt_aec7fc2a531ca29a`) | HAUPT | 9.6 | 0.76 | 0.88 | 0.12 | 1.18 | 0.60 → 0.81 | 0.61 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[577280,5927329]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.489251/10.164766) · [OSM](https://www.openstreetmap.org/?mlat=53.489251&mlon=10.164766#map=18/53.489251/10.164766) |
| 24 | Innenstadt (Rathausmarkt) – Hochschule HAW - Life Sciences - Campus Bergedorf (`rt_b93eca52aba3874d`) | RSV | 17.8 | 0.65 | 0.72 | 0.06 | 1.15 | 0.64 → 0.73 | 0.79 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573537,5933144]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.542046/10.109728) · [OSM](https://www.openstreetmap.org/?mlat=53.542046&mlon=10.109728#map=18/53.542046/10.109728) |
| 25 | Umsteigeknoten Hamburg-Harburg – Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) (`rt_463b00cfca1d45be`) | RSV | 7.4 | 0.52 | 0.68 | 0.15 | 1.14 | 0.60 → 0.81 | 0.33 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562896,5925065]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.470813/9.947549) · [OSM](https://www.openstreetmap.org/?mlat=53.470813&mlon=9.947549#map=18/53.470813/9.947549) |
| 26 | Verdichtung HAUPT: neben Osdorfer Landstraße (`rt_72d1850ab8acbd17`) | HAUPT | 9.2 | 0.57 | 0.70 | 0.12 | 1.14 | 0.60 → 0.76 | 0.51 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554538,5936526]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.574756/9.823643) · [OSM](https://www.openstreetmap.org/?mlat=53.574756&mlon=9.823643#map=18/53.574756/9.823643) |
| 27 | Arbeitsplatzschwerpunkt Harburg (300 Tsd. m²) – Arbeitsplatzschwerpunkt Harburg (241 Tsd. m²) (`rt_a3f51202ca48fa1c`) | RSV | 6.8 | 0.51 | 0.68 | 0.17 | 1.14 | 0.56 → 0.78 | 0.34 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562608,5925087]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.471045/9.943226) · [OSM](https://www.openstreetmap.org/?mlat=53.471045&mlon=9.943226#map=18/53.471045/9.943226) |
| 28 | Innenstadt (Rathausmarkt) – Hochschule Technologiezentrum Hamburg-Finkenwerder (`rt_4d89627cef3a3329`) | HAUPT | 12.2 | 0.58 | 0.67 | 0.09 | 1.13 | 0.58 → 0.71 | 0.69 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562565,5934469]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.555374/9.944449) · [OSM](https://www.openstreetmap.org/?mlat=53.555374&mlon=9.944449#map=18/53.555374/9.944449) |
| 29 | Verdichtung HAUPT: Little Whistler (`rt_08c9b542408be57e`) | HAUPT | 4.3 | 0.53 | 0.79 | 0.26 | 1.12 | 0.42 → 0.83 | 0.07 → 1.00 | high | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[560773,5923351]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.455657/9.915248) · [OSM](https://www.openstreetmap.org/?mlat=53.455657&mlon=9.915248#map=18/53.455657/9.915248) |
| 30 | Arbeitsplatzschwerpunkt Hamburg-Mitte (379 Tsd. m²) – Arbeitsplatzschwerpunkt Hamburg-Mitte (231 Tsd. m²) (`rt_9978d70cbf7eefbe`) | HAUPT | 6.9 | 0.73 | 0.89 | 0.16 | 1.11 | 0.55 → 0.83 | 0.67 → 1.00 | medium | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558090,5932012]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.533804/9.876452) · [OSM](https://www.openstreetmap.org/?mlat=53.533804&mlon=9.876452#map=18/53.533804/9.876452) |

Höchster Δ einer Route (ohne Längengewicht): 0.30; Routen mit Δ ≥ 0,2: 175.

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
| Zusammenhang | 0.200 | 0.240 | 29/30 | 0.998 |
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
| Altona | 421 | 0.70 | 0.78 | 0.08 |
| Bergedorf | 196 | 0.73 | 0.82 | 0.09 |
| Eimsbüttel | 353 | 0.70 | 0.78 | 0.08 |
| Hamburg-Mitte | 488 | 0.72 | 0.80 | 0.08 |
| Hamburg-Nord | 411 | 0.70 | 0.78 | 0.08 |
| Harburg | 268 | 0.69 | 0.79 | 0.10 |
| Wandsbek | 818 | 0.71 | 0.80 | 0.08 |

## Stichprobe: 30 zufällige Kanten (Seed 42, nach Bezirk verteilt)

| Kante | Name | Kategorie | Führung Ist → Soll | Breite / Soll | Belag | lit | Score Ist / Soll | Prüfen |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| `ce_0e7da0c5a0df07cd` | Knospenweg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.78 / 0.83 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553463,5936487]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.574521/9.807408) · [OSM](https://www.openstreetmap.org/?mlat=53.574521&mlon=9.807408#map=18/53.574521/9.807408) |
| `ce_3a77d5a0636fa9cb` | neben Blomkamp | HAUPT | Zweirichtungsradweg → Fahrradstraße | – / 3.50 | asphalt | ja | 0.71 / 0.76 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[556875,5936799]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.576960/9.858989) · [OSM](https://www.openstreetmap.org/?mlat=53.576960&mlon=9.858989#map=18/53.576960/9.858989) |
| `ce_7e2aaac1a5ae2e5c` | Gätgensstraße | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.64 / 0.69 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[554292,5934939]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.560523/9.819665) · [OSM](https://www.openstreetmap.org/?mlat=53.560523&mlon=9.819665#map=18/53.560523/9.819665) |
| `ce_8c9bb9df8f8cebca` | Eimsbütteler Straße | BASIS | Mischverkehr → Mischverkehr | – / – | asphalt | ja | 0.88 / 0.88 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563113,5935692]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.566299/9.952970) · [OSM](https://www.openstreetmap.org/?mlat=53.566299&mlon=9.952970#map=18/53.566299/9.952970) |
| `ce_28e49f052a0c6b34` | Riehlstraße | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | – | 0.77 / 0.86 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[579456,5928352]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.498120/10.197821) · [OSM](https://www.openstreetmap.org/?mlat=53.498120&mlon=10.197821#map=18/53.498120/10.197821) |
| `ce_417a3364826a402b` | Reinbeker Weg | HAUPT | Mischverkehr → Fahrradstraße | – / – | unhewn_cobblestone | ja | 0.63 / 0.83 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[580865,5927510]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.490340/10.218832) · [OSM](https://www.openstreetmap.org/?mlat=53.490340&mlon=10.218832#map=18/53.490340/10.218832) |
| `ce_1aafa48c130f1b5b` | Oliver-Lißy-Straße | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.73 / 0.78 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[559683,5941629]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.620059/9.902316) · [OSM](https://www.openstreetmap.org/?mlat=53.620059&mlon=9.902316#map=18/53.620059/9.902316) |
| `ce_b45d071fbf384c53` | Lohbekstieg | BASIS | Mischverkehr → Mischverkehr | – / – | asphalt | ja | 0.91 / 0.91 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563242,5938810]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.594305/9.955540) · [OSM](https://www.openstreetmap.org/?mlat=53.594305&mlon=9.955540#map=18/53.594305/9.955540) |
| `ce_c6585e766469725c` | Ohmoor | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.78 / 0.83 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563725,5943561]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.636950/9.963819) · [OSM](https://www.openstreetmap.org/?mlat=53.636950&mlon=9.963819#map=18/53.636950/9.963819) |
| `ce_c7dfee1525635f8d` | Oberstraße | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.82 / 0.87 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565143,5936940]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.577266/9.983873) · [OSM](https://www.openstreetmap.org/?mlat=53.577266&mlon=9.983873#map=18/53.577266/9.983873) |
| `ce_0c9cd7f18ecc8454` | Karl-Arnold-Ring | BASIS | Mischverkehr → Mischverkehr | – / – | asphalt | ja | 0.85 / 0.85 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567821,5926895]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.486651/10.022141) · [OSM](https://www.openstreetmap.org/?mlat=53.486651&mlon=10.022141#map=18/53.486651/10.022141) |
| `ce_2291d2ac1d6234df` | – | HAUPT | eigener Weg → eigener Weg | – / 3.50 | paving_stones | ja | 0.71 / 0.87 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564517,5931462]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.528116/9.973289) · [OSM](https://www.openstreetmap.org/?mlat=53.528116&mlon=9.973289#map=18/53.528116/9.973289) |
| `ce_b00de690474e07b2` | Dahlgrünring | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.84 / 0.89 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567608,5926417]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.482380/10.018816) · [OSM](https://www.openstreetmap.org/?mlat=53.482380&mlon=10.018816#map=18/53.482380/10.018816) |
| `ce_e32a34507f0a5276` | Gothaer Weg | BASIS | Mischverkehr → Mischverkehr | – / – | asphalt | ja | 0.91 / 0.91 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[573519,5933270]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.543178/10.109484) · [OSM](https://www.openstreetmap.org/?mlat=53.543178&mlon=10.109484#map=18/53.543178/10.109484) |
| `ce_f68b9a0c465f6add` | – | HAUPT | eigener Weg → eigener Weg | – / 3.50 | nan | – | 0.85 / 0.89 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575445,5932218]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.533447/10.138296) · [OSM](https://www.openstreetmap.org/?mlat=53.533447&mlon=10.138296#map=18/53.533447/10.138296) |
| `ce_0b1b6958b74fb758` | Moorreye | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.75 / 0.83 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567442,5944029]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.640691/10.020123) · [OSM](https://www.openstreetmap.org/?mlat=53.640691&mlon=10.020123#map=18/53.640691/10.020123) |
| `ce_26baa727b8d8249c` | neben Alsterdorfer Straße | HAUPT | Zweirichtungsradweg → Radweg je Seite | – / 3.50 | nan | ja | 0.63 / 0.74 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567455,5941044]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.613859/10.019668) · [OSM](https://www.openstreetmap.org/?mlat=53.613859&mlon=10.019668#map=18/53.613859/10.019668) |
| `ce_5f53b97cd869fe12` | Friedrichsberger Straße | BASIS | Radweg je Seite → Mischverkehr | – / 2.00 | asphalt | ja | 0.80 / 0.86 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569531,5936560]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.573290/10.050044) · [OSM](https://www.openstreetmap.org/?mlat=53.573290&mlon=10.050044#map=18/53.573290/10.050044) |
| `ce_65b6e8d319cf8f4f` | Tangstedter Landstraße | BASIS | Radweg je Seite → Radweg je Seite | – / 2.00 | asphalt | ja | 0.81 / 0.81 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[567676,5946824]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.665778/10.024265) · [OSM](https://www.openstreetmap.org/?mlat=53.665778&mlon=10.024265#map=18/53.665778/10.024265) |
| `ce_d91af74f29189446` | Dehnhaide | BASIS | Mischverkehr → Radweg je Seite | – / – | asphalt | ja | 0.46 / 0.57 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[568896,5937294]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.579967/10.040625) · [OSM](https://www.openstreetmap.org/?mlat=53.579967&mlon=10.040625#map=18/53.579967/10.040625) |
| `ce_0e9d0c21509796cb` | Triftstraße | HAUPT | Zweirichtungsradweg → Fahrradstraße | – / 3.50 | asphalt | ja | 0.62 / 0.68 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[563182,5923006]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.452274/9.951447) · [OSM](https://www.openstreetmap.org/?mlat=53.452274&mlon=9.951447#map=18/53.452274/9.951447) |
| `ce_5d7a66e6d8eb1a82` | Winsener Straße | HAUPT | Radweg je Seite → Radweg je Seite | – / 2.50 | asphalt | ja | 0.62 / 0.62 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565770,5922113]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.443934/9.990228) · [OSM](https://www.openstreetmap.org/?mlat=53.443934&mlon=9.990228#map=18/53.443934/9.990228) |
| `ce_fe316f198c34efab` | Cuxhavener Straße | BASIS | Mischverkehr → Radweg je Seite | – / – | asphalt | ja | 0.58 / 0.68 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[553830,5924632]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.467929/9.810913) · [OSM](https://www.openstreetmap.org/?mlat=53.467929&mlon=9.810913#map=18/53.467929/9.810913) |
| `ce_4071cf1ae76017b4` | Treptower Straße | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | – | 0.76 / 0.86 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575460,5941163]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.613834/10.140684) · [OSM](https://www.openstreetmap.org/?mlat=53.613834&mlon=10.140684#map=18/53.613834/10.140684) |
| `ce_5163e8d727b7e941` | Saseler Weg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.71 / 0.80 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[575688,5945034]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.648590/10.145067) · [OSM](https://www.openstreetmap.org/?mlat=53.648590&mlon=10.145067#map=18/53.648590/10.145067) |
| `ce_7941b01b8f3f2d1c` | Volksdorfer Damm | HAUPT | Radweg je Seite → Fahrradstraße | – / 2.50 | sett | ja | 0.59 / 0.80 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[574449,5947523]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.671134/10.126925) · [OSM](https://www.openstreetmap.org/?mlat=53.671134&mlon=10.126925#map=18/53.671134/10.126925) |
| `ce_81343ae9c5d3d90e` | Poppenbüttler Stieg | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.82 / 0.87 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[569420,5944552]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.645126/10.050145) · [OSM](https://www.openstreetmap.org/?mlat=53.645126&mlon=10.050145#map=18/53.645126/10.050145) |
| `ce_a8f3a4863d304eb6` | Kätnermoor | HAUPT | Mischverkehr → Fahrradstraße | – / – | asphalt | ja | 0.73 / 0.78 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[572550,5942602]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.627181/10.097044) · [OSM](https://www.openstreetmap.org/?mlat=53.627181&mlon=10.097044#map=18/53.627181/10.097044) |
| `ce_e89a5224e634dd4a` | Oldenfelder Straße | HAUPT | Radweg je Seite → Fahrradstraße | – / 2.50 | asphalt | ja | 0.75 / 0.84 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576510,5940524]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.607940/10.156393) · [OSM](https://www.openstreetmap.org/?mlat=53.607940&mlon=10.156393#map=18/53.607940/10.156393) |
| `ce_fa2ddca389f11da1` | neben Farmsener Landstraße | HAUPT | Radweg je Seite → Radweg je Seite | – / 2.50 | paving_stones | ja | 0.42 / 0.57 | [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[576619,5944753]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968) · [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.645930/10.159081) · [OSM](https://www.openstreetmap.org/?mlat=53.645930&mlon=10.159081#map=18/53.645930/10.159081) |

## Durchsicht mit Ortskundigen

20 Routen (nach Kategorie geschichtet, Seed 42, C-PRI-15) in `reports/cycle_principles_review.csv` mit Links und leeren Spalten für Einschätzung und Kommentar.

## Hinweise

- Soll-Führung je Kante vorläufig direkt aus der Trennungsmatrix (bevorzugte Führung); Prompt 18 legt Führung und Breite je Abschnitt fest, danach P-SAF-01/P-COM-01 (Soll) mit dessen Ergebnis rechnen.
- Halte und Zeitverlust (P-DIR-02/03) im Soll wie im Ist, bis Prompt 20 Soll-Knotentypen liefert; P-SAF-02 bis dahin unbekannt.
- Unfälle (P-SAF-04) bleiben im Soll unverändert (keine Wirkungsprognose).
- Nachfrage und Netz beruhen auf dem mäßig kalibrierten Modell aus Prompt 15 (reports/cycle_demand.md).

Quellen: OpenStreetMap-Beitragende (ODbL); ALKIS © Freie und Hansestadt Hamburg, LGV (dl-de/by-2.0); Unfallatlas © Statistische Ämter des Bundes und der Länder (dl-de/by-2.0); HVV-GTFS © Hamburger Verkehrsverbund GmbH (dl-de/by-2.0).
