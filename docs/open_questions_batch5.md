# Offene Fragen – Stapel 5: Sammelfreigabe (Stand 2026-11-07)

42 kleinere Entscheidungen aus Gruppe C (docs/open_questions_triage.md). Nummern wie dort. Je Punkt eine Empfehlung von
Claude Code: **belassen** (Umsetzung bleibt, Frage wird mit Begründung geschlossen), **ändern** (Regel/Code anpassen,
neue Version, Neurechnung), **später** (geht in Prompt 22 oder 23 auf), **erledigt** (durch spätere Prompts beantwortet).

## Ändern (11; davon 10 umgesetzt, 87 zurückgestellt)

| Nr | Frage (kurz) | Empfehlung |
|---|---|---|
| 21 | in_hvs nur bei match exact | auch partial zählen, wenn der Straßenname gleich ist; behebt Lücken wie Kieler Straße, Hallerstraße (Abgleich S-CONF-04). Neurechnung ab Conflation |
| 23 | Tempo-Texte ohne Zahl | „5-7 km/h“ (verkehrsberuhigt) = 7 km/h wie der Rechenwert von ETW_ERF; Verkehrsbeeinflussungsanlage und Auffahrt bleiben unbekannt |
| 39 | 14 % der Länge ohne Breite | width_p10_m vom angrenzenden Abschnitt gleichen Namens übernehmen (Flag width_from_neighbour, confidence mittel); kein neuer Wert |
| 43 | Prüfdateien in reports/ in EPSG:4326 | für Prüfdateien (GeoJSON-Standard) zulassen; Satz in CLAUDE.md, Rechnen bleibt EPSG:25832 |
| 45 | shop_frontage_share leer ohne Gebäude im Puffer | ohne Gebäude = 0 (keine Publikumsnutzung); 236 GOW-Knotenstücke erhalten eine sichere Einstufung |
| 52 | N3: Flächen ohne Barrieren | Bahn, Flüsse/Kanäle als Grenzen wie C-NET-07 barrier_lines; nur Flags, keine Umklassifizierung |
| 54 | N4: 73 000 OD-Paare nur über ETW | eigenes Flag gow_network_gap (Lücke im GOW-Netz); keine Schwelle |
| 65 | D-DES-01 „Parallelroute“ nicht prüfbar | Parallelroute = eigenständiger Radweg oder amtliches Radnetz (Bestand) im Abstand P-ATT-03 parallel_max_m (200 m); vorhandener Wert |
| 78 | parallele Nebenfahrbahnen als in_hvs | S-NET-04-Wege (service) nicht dem HVS zuordnen → Erschließung (DV: ventweg); 22 Abschnitte |
| 87 | in_hvs im conn_score wirkt als Abzug | **zurückgestellt (Fachplaner*in):** Probelauf ergibt +430 km GOW (289 km GOW30, 141 km GOW50); Entscheidung mit den Fachplaner-Fragen |
| 129 | keine Override-Ebene für Fahrstreifen | overrides/lane_overrides.csv wie die übrigen Korrekturebenen (nur approved) |

## Später (5)

| Nr | Frage (kurz) | Empfehlung |
|---|---|---|
| 28 | Betweenness ungerichtet, ohne oneway/access | Prompt 22 Stufe B baut einen gerichteten Kfz-Graphen; dann übernehmen |
| 53 | N4-Schleichverkehr: Schwelle Zeitvorteil | Prompt 22 Stufe B (Umlegung mit Filtern) zeigt echten Schleichverkehr; keine Schwelle erfinden |
| 92 | Annahmen früherer Stufen einmalig variieren | zusammen mit der Szenario-Sensitivität in Prompt 22 |
| 122 | Soll für Halte, Wirkung auf Unfälle | Prompt 23 (Wartezeiten je Knotentyp) |
| 140 | Sensitivität Nachfrage/Netzentwurf über Nacht | zusammen mit Prompt 22 (Faktor C-IMP-07, Referenzdichte) |

## Erledigt (1)

| Nr | Frage (kurz) | Begründung |
|---|---|---|
| 68 | Unfälle an Knoten nur einem Abschnitt zugeordnet | Knotenpunkte zählen Radunfälle seit Prompt 20 selbst (J-M-07, Knoten-Steckbrief); Abschnitte bleiben wie entschieden |

## Belassen (25)

| Nr | Frage (kurz) | Begründung |
|---|---|---|
| 14 | Neu segmentieren nach Querschnitt | nein: segment_id muss stabil bleiben (CLAUDE.md) |
| 15 | fehlendes maxspeed kein Wechsel | passt: unbekannt ist kein Teilungsgrund |
| 16 | *_link ja, road/busway nein | passt: busway ohne allgemeinen Verkehr, road kaum vorhanden |
| 17 | kurze Stücke an Richtungsfahrbahnen | bleiben getrennt; Harmonisierung (H-STR-01) und Knotenbildung (J-M-02) fassen zusammen |
| 24 | Teilen bei Namenswechsel | nein: ändert segment_id; Harmonisierung arbeitet über den Namen |
| 19 | Definition match_quality | passt |
| 29 | Autobahnen ohne Busse senken conn_score | ohne Wirkung auf C-SW-01 |
| 30 | fehlendes DTV auf Nebenstraßen | Gewicht weiter umlegen; „niedrig“ würde Nebenstraßen pauschal abwerten |
| 32 | shop_frontage_share bei wenigen Gebäuden | Mindestzahl wäre eine neue Schwelle; zur Fachplaner-Liste |
| 33 | Definition Publikumsnutzung, amenity_excluded | Listenprüfung durch Fachplaner*in (Gruppe D) |
| 35 | fehlende OSM-Gestaltungstags | bleiben unbekannt statt „nein“ (ehrlicher) |
| 36 | access_motor_only | passt |
| 41 | Verkehrsfläche umfasst Parkwege, Böschungen | bekannte Grenze, im Report dokumentiert |
| 42 | Richtungsfahrbahnen messen dieselbe Breite | gewollt: der ganze Straßenraum zählt |
| 47 | Definition Bezirksstraße im Report | passt |
| 80 | service/track ohne Betweenness | passt (confidence mittel) |
| 84 | Monte-Carlo über Gewichte und Schwellen | so belassen (guide.md 7.1) |
| 85 | „unsicher“ ab 0,3 | so belassen (V-UNC-01) |
| 91 | Abbruchgrenze Kennzahl HVS-km | nur berichten, keine Grenze erfinden |
| 95 | Liste ländlicher Stadtteile | Liste freigeben (status approved) |
| 96 | Hafen- und Gewerbestraßen | wie Stadtstraßen; HPA-Straßen später gesondert |
| 105 | Gewichte der fünf Prinzipien | gleiche Gewichte; Top 30 bleibt bei Variation zu ≥ 28/30 gleich |
| 116 | große Maschen ohne querendes Wegenetz | mit density_scaling meist erledigt; Rest als Lücke melden, Wirtschaftswege nicht aufnehmen |
| 121 | P-COH-02 für RSV allein | belassen, bis RSV in Prompt 22 neu bewertet werden (Zielnachfrage) |
| 128 | PL-02/PL-05 nicht prüfbar | Flag bleibt |
