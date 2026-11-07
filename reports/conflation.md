# Conflation amtlich ↔ OSM (Stufe 3)

Erzeugt: 2026-11-07T14:42:56+00:00 von `pipeline/s03_conflate.py`. Nicht amtlicher Entwurf.

## Datengrundlage

- Abschnitte: `data/interim/segments.parquet` (36 526 Abschnitte Hamburg)
- Arbeitsgebiet: Hamburg (7 Bezirke) + 500 m; abgeglichen werden Abschnitte, die ganz darin liegen (34 702). Außerhalb bleibt `match_quality` leer.
- Nicht bewertet (ländliche Stadtteile, config/project.yaml rural_exclude): 1 478 Abschnitte, 436.0 km – Bergedorf 317.1 km, Harburg 118.9 km
- Regelwerk: config/rules.yaml 0.16.0

| Schlüssel | Quelle / Ebene | Objekte | Abruf | Lizenz |
| --- | --- | ---: | --- | --- |
| speed | speed_limits / zulaessige_hoechstgeschwindigkeiten | 35 538 | 2026-11-04 | unknown |
| speed_conditional | speed_limits / zulaessige_hoechstgeschwindigkeiten_sonderregelung | 832 | 2026-11-04 | unknown |
| zone_t30 | speed_limits / tempo30zonen | 19 472 | 2026-11-04 | unknown |
| zone_t20 | speed_limits / tempo20zonen | 192 | 2026-11-04 | unknown |
| zone_vb | speed_limits / verkehrsberuhigte_bereiche | 1 477 | 2026-11-04 | unknown |
| hvs | traffic_volumes / verkehrsmengen_dtv_hvs_2019 | 3 728 | 2026-11-04 | unknown |
| bab | traffic_volumes / verkehrsmengen_dtv_bab_2019 | 575 | 2026-11-04 | unknown |
| dedication | dedications / de.hh.up:widmung_linie | 43 547 | 2026-11-04 | dl-de/by-2.0 |

**Lücken:**

- Der WFS „Strategisches Straßennetz“ (HH-SIB) liefert HTTP 404. Darum stammt `in_hvs` aus den DTV-Linien der Hauptverkehrsstraßen **2019** (S-CONF-04), nicht aus der HVS-Karte 2023 (nur PDF). Straßen, die seit 2019 zum HVS-Netz gekommen oder herausgefallen sind, sind falsch zugeordnet.
- Die Zonenebenen (Tempo 30, Tempo 20, verkehrsberuhigt) sind Linien des amtlichen Netzes, keine Flächen; der Längenanteil wird über den Puffer der richtungsgleichen Linien bestimmt (S-CONF-02).
- Die Ebene `…_sonderregelung` ist eine Teilmenge der Hauptebene (gleiche Geometrien und Felder); die zeitlich begrenzten Regelungen werden aus der Hauptebene gelesen.

## Regeln und Schwellen

- **S-CONF-01** (assumption, draft): Linienabgleich amtlich -> Abschnitt: Kandidaten im Puffer, Filter nach Richtungswinkel und Überdeckungsanteil, Zuordnung nach Hausdorff-Abstand; buffer_m = 15 m (assumption); max_angle_deg = 20 Grad (ungerichtet, 0-90) (assumption); min_overlap_share = 0.6 Anteil 0-1 (assumption)
- **S-CONF-02** (assumption, draft): Zonen (Tempo 30, Tempo 20, verkehrsberuhigte Bereiche) über Längenanteil zuordnen; min_length_share = 0.5 Anteil 0-1 der Abschnittslänge (assumption)
- **S-CONF-03** (hamburg, draft): Zeitlich begrenzte Regelungen (sonderregelung) getrennt speichern, nie als Regeltempo
- **S-CONF-04** (hamburg, draft): in_hvs aus den DTV-Linien der Hauptverkehrsstraßen 2019 (match_quality exact), weil HH-SIB nicht erreichbar ist. Seit 0.16.0: partial zählt, wenn der Abschnitt über Abschnitte gleichen Namens mit einem exact-Treffer verbunden ist (in_hvs_source neighbour); Wege aus S-NET-04 (service, track) nie

## Trefferquote (Arbeitsgebiet, 34 702 Abschnitte)

| Quelle | exact | partial | none | exact km-Anteil |
| --- | ---: | ---: | ---: | ---: |
| zulaessige_hoechstgeschwindigkeiten | 28 248 | 578 | 5 876 | 86.4 % |
| de.hh.up:widmung_linie | 28 873 | 589 | 5 240 | 88.1 % |
| verkehrsmengen_dtv_hvs_2019 | 5 698 | 338 | 28 666 | 15.3 % |
| verkehrsmengen_dtv_bab_2019 | 138 | 35 | 34 529 | 2.1 % |

## match_quality (Tempo-Ebene) je Bezirk (km-Anteile)

| Bezirk | Abschnitte | km | exact | partial | none |
| --- | ---: | ---: | ---: | ---: | ---: |
| Altona | 4 886 | 620.5 | 89 % | 2 % | 8 % |
| Bergedorf | 1 957 | 209.3 | 87 % | 3 % | 10 % |
| Eimsbüttel | 4 004 | 470.4 | 93 % | 2 % | 4 % |
| Hamburg-Mitte | 6 839 | 881.3 | 86 % | 4 % | 11 % |
| Hamburg-Nord | 5 136 | 563.3 | 92 % | 2 % | 6 % |
| Harburg | 3 348 | 465.2 | 83 % | 5 % | 11 % |
| Wandsbek | 7 542 | 1 030.4 | 92 % | 2 % | 6 % |
| **gesamt** | 33 712 | 4 240.4 | 89 % | 3 % | 8 % |

## match_quality (Tempo-Ebene) je highway-Klasse – Hamburg (7 Bezirke)

| highway | Anzahl | exact | partial | none | Name gleich¹ |
| --- | ---: | ---: | ---: | ---: | ---: |
| motorway | 125 | 80.0 % | 15.2 % | 4.8 % | 0.0 % |
| motorway_link | 282 | 68.8 % | 8.2 % | 23.0 % | 0.0 % |
| trunk | 74 | 81.1 % | 9.5 % | 9.5 % | 56.7 % |
| trunk_link | 109 | 76.1 % | 7.3 % | 16.5 % | 15.4 % |
| primary | 2 750 | 89.5 % | 3.1 % | 7.3 % | 91.7 % |
| primary_link | 105 | 52.4 % | 5.7 % | 41.9 % | 26.2 % |
| secondary | 3 806 | 87.8 % | 2.4 % | 9.9 % | 91.7 % |
| secondary_link | 193 | 49.7 % | 5.2 % | 45.1 % | 46.2 % |
| tertiary | 4 133 | 88.0 % | 1.3 % | 10.8 % | 93.2 % |
| tertiary_link | 114 | 36.0 % | 7.9 % | 56.1 % | 54.0 % |
| unclassified | 1 509 | 71.9 % | 1.8 % | 26.3 % | 81.0 % |
| residential | 17 045 | 90.5 % | 1.0 % | 8.6 % | 95.1 % |
| living_street | 1 576 | 76.6 % | 1.9 % | 21.5 % | 96.4 % |
| pedestrian | 702 | 8.7 % | 1.4 % | 89.9 % | 46.5 % |
| service | 850 | 35.3 % | 3.1 % | 61.6 % | 93.3 % |
| track | 339 | 31.9 % | 3.2 % | 64.9 % | 85.7 % |
| **gesamt** | 33 712 | 83.8 % | 1.7 % | 14.5 % | 91.6 % |

¹ Anteil der zugeordneten Abschnitte, deren OSM-Name gleich dem amtlichen Straßennamen ist (automatische Plausibilitätsprüfung, ersetzt nicht die manuelle Stichprobe).

## Ist-Tempo – Hamburg (7 Bezirke)

- Abschnitte mit amtlichem Regeltempo: 28 376 von 33 712
- Übereinstimmung mit OSM-maxspeed (wo beide eine Zahl haben): 95.3 % (23 133 von 24 279)
- Abschnitte mit zeitlich begrenzter Regelung (S-CONF-03, getrennt in `speed_conditional`): 1 035
- Regeltempo mehrdeutig (`speed_official_ambiguous`): 103
- Mehrere amtliche Tempi auf einem Abschnitt (`speed_official_conflict`): 470

| Regeltempo amtlich | Abschnitte | km |
| --- | ---: | ---: |
| 7 km/h | 1 250 | 103.2 |
| 10 km/h | 31 | 4.0 |
| 15 km/h | 2 | 1.6 |
| 20 km/h | 196 | 17.4 |
| 25 km/h | 27 | 2.2 |
| 30 km/h | 14 303 | 2 058.3 |
| 40 km/h | 8 | 1.4 |
| 50 km/h | 12 099 | 1 442.5 |
| 60 km/h | 303 | 66.9 |
| 70 km/h | 42 | 12.4 |
| 80 km/h | 69 | 39.7 |
| 100 km/h | 37 | 14.0 |
| 120 km/h | 9 | 10.4 |
| ohne Zahl (z. B. 5-7 km/h, variabel) / keine Zuordnung | 5 336 | 466.3 |

## HVS (S-CONF-04) und Zonen (S-CONF-02) – Hamburg (7 Bezirke)

| highway | Anzahl | in_hvs | Tempo-30-Zone | Tempo-20-Zone | verkehrsberuhigt |
| --- | ---: | ---: | ---: | ---: | ---: |
| motorway | 125 | 0 | 0 | 0 | 0 |
| motorway_link | 282 | 5 | 0 | 0 | 0 |
| trunk | 74 | 48 | 0 | 0 | 0 |
| trunk_link | 109 | 10 | 1 | 0 | 0 |
| primary | 2 750 | 2 435 | 11 | 3 | 1 |
| primary_link | 105 | 11 | 0 | 0 | 0 |
| secondary | 3 806 | 3 143 | 25 | 0 | 1 |
| secondary_link | 193 | 44 | 0 | 0 | 0 |
| tertiary | 4 133 | 137 | 165 | 3 | 0 |
| tertiary_link | 114 | 6 | 0 | 0 | 0 |
| unclassified | 1 509 | 24 | 247 | 17 | 0 |
| residential | 17 045 | 78 | 12 798 | 149 | 109 |
| living_street | 1 576 | 1 | 193 | 0 | 944 |
| pedestrian | 702 | 4 | 32 | 4 | 0 |
| service | 850 | 0 | 126 | 1 | 16 |
| track | 339 | 0 | 27 | 1 | 1 |

- in_hvs gesamt: 5 946 Abschnitte, 690.0 km
- in_hvs, aber OSM-highway residential/living_street/unclassified (prüfen): 103

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert und eindeutig | ok | 36526 Abschnitte |
| match_quality im Arbeitsgebiet gesetzt, außerhalb leer | ok | 34702 im Arbeitsgebiet, 1824 außerhalb |
| Ist-Tempo nur aus Werten der Quelle | ok | Werte [7, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 100, 120] |
| Zeitlich begrenztes Tempo nie als Regeltempo (S-CONF-03) | ok | 0 Verstöße |

## Manuelle Stichprobe

`reports/conflation_sample.csv`: 50 Zufallsabschnitte in Hamburg (7 Bezirke) (Seed 42, Spalte `bezirk`, etwa gleich viele je match_quality), mit Links auf OSM-Karte und OSM-Way. Spalte `geoportal` ist leer, bis das Linkformat geklärt ist (docs/open_questions.md). Prüfende tragen `check_ok` (ja/nein) und `comment` ein.

| Ergebnis | Anzahl |
| --- | ---: |
| Zuordnung richtig | _offen_ |
| Zuordnung falsch | _offen_ |
| **Trefferquote** | _offen – nach manueller Prüfung eintragen_ |

## Lizenz

Abschnitte aus OpenStreetMap-Daten © OpenStreetMap-Beitragende, ODbL 1.0. Amtliche Attribute: Freie und Hansestadt Hamburg (Widmungen: BVM, dl-de/by-2.0; Höchstgeschwindigkeiten und Verkehrsmengen: Lizenz in der API nicht angegeben, siehe docs/open_questions.md).
