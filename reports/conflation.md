# Conflation amtlich ↔ OSM (Stufe 3)

Erzeugt: 2026-11-04T20:33:26+00:00 von `pipeline/s03_conflate.py`. Nicht amtlicher Entwurf.

## Datengrundlage

- Abschnitte: `data/interim/segments.parquet` (36 526 Abschnitte Hamburg)
- Arbeitsgebiet: Eimsbüttel + 500 m; abgeglichen werden Abschnitte, die ganz darin liegen (4 947). Außerhalb bleibt `match_quality` leer (keine amtlichen Daten abgerufen).
- Regelwerk: config/rules.yaml 0.11.0

| Schlüssel | Quelle / Ebene | Objekte | Abruf | Lizenz |
| --- | --- | ---: | --- | --- |
| speed | speed_limits / zulaessige_hoechstgeschwindigkeiten | 4 916 | 2026-10-28 | unknown |
| speed_conditional | speed_limits / zulaessige_hoechstgeschwindigkeiten_sonderregelung | 162 | 2026-10-28 | unknown |
| zone_t30 | speed_limits / tempo30zonen | 2 810 | 2026-10-28 | unknown |
| zone_t20 | speed_limits / tempo20zonen | 22 | 2026-10-28 | unknown |
| zone_vb | speed_limits / verkehrsberuhigte_bereiche | 100 | 2026-10-28 | unknown |
| hvs | traffic_volumes / verkehrsmengen_dtv_hvs_2019 | 598 | 2026-10-28 | unknown |
| bab | traffic_volumes / verkehrsmengen_dtv_bab_2019 | 92 | 2026-10-28 | unknown |
| dedication | dedications / de.hh.up:widmung_linie | 5 804 | 2026-10-28 | dl-de/by-2.0 |

**Lücken:**

- Der WFS „Strategisches Straßennetz“ (HH-SIB) liefert HTTP 404. Darum stammt `in_hvs` aus den DTV-Linien der Hauptverkehrsstraßen **2019** (S-CONF-04), nicht aus der HVS-Karte 2023 (nur PDF). Straßen, die seit 2019 zum HVS-Netz gekommen oder herausgefallen sind, sind falsch zugeordnet.
- Die Zonenebenen (Tempo 30, Tempo 20, verkehrsberuhigt) sind Linien des amtlichen Netzes, keine Flächen; der Längenanteil wird über den Puffer der richtungsgleichen Linien bestimmt (S-CONF-02).
- Die Ebene `…_sonderregelung` ist eine Teilmenge der Hauptebene (gleiche Geometrien und Felder); die zeitlich begrenzten Regelungen werden aus der Hauptebene gelesen.

## Regeln und Schwellen

- **S-CONF-01** (assumption, draft): Linienabgleich amtlich -> Abschnitt: Kandidaten im Puffer, Filter nach Richtungswinkel und Überdeckungsanteil, Zuordnung nach Hausdorff-Abstand; buffer_m = 15 m (assumption); max_angle_deg = 20 Grad (ungerichtet, 0-90) (assumption); min_overlap_share = 0.6 Anteil 0-1 (assumption)
- **S-CONF-02** (assumption, draft): Zonen (Tempo 30, Tempo 20, verkehrsberuhigte Bereiche) über Längenanteil zuordnen; min_length_share = 0.5 Anteil 0-1 der Abschnittslänge (assumption)
- **S-CONF-03** (hamburg, draft): Zeitlich begrenzte Regelungen (sonderregelung) getrennt speichern, nie als Regeltempo
- **S-CONF-04** (hamburg, draft): in_hvs aus den DTV-Linien der Hauptverkehrsstraßen 2019 (match_quality exact), weil HH-SIB nicht erreichbar ist

## Trefferquote (Arbeitsgebiet, 4 947 Abschnitte)

| Quelle | exact | partial | none | exact km-Anteil |
| --- | ---: | ---: | ---: | ---: |
| zulaessige_hoechstgeschwindigkeiten | 4 075 | 82 | 790 | 90.0 % |
| de.hh.up:widmung_linie | 4 136 | 89 | 722 | 90.7 % |
| verkehrsmengen_dtv_hvs_2019 | 924 | 63 | 3 960 | 16.1 % |
| verkehrsmengen_dtv_bab_2019 | 30 | 2 | 4 915 | 3.1 % |

## match_quality (Tempo-Ebene) je highway-Klasse – Eimsbüttel

| highway | Anzahl | exact | partial | none | Name gleich¹ |
| --- | ---: | ---: | ---: | ---: | ---: |
| motorway | 26 | 88.5 % | 11.5 % | 0.0 % | 0.0 % |
| motorway_link | 72 | 72.2 % | 4.2 % | 23.6 % | 0.0 % |
| trunk | 1 | 100.0 % | 0.0 % | 0.0 % | 100.0 % |
| primary | 566 | 90.6 % | 1.9 % | 7.4 % | 92.9 % |
| primary_link | 29 | 62.1 % | 3.4 % | 34.5 % | 26.3 % |
| secondary | 337 | 86.1 % | 2.1 % | 11.9 % | 91.9 % |
| secondary_link | 21 | 57.1 % | 14.3 % | 28.6 % | 46.7 % |
| tertiary | 537 | 87.7 % | 0.9 % | 11.4 % | 96.0 % |
| tertiary_link | 9 | 33.3 % | 22.2 % | 44.4 % | 60.0 % |
| unclassified | 94 | 69.1 % | 2.1 % | 28.7 % | 92.5 % |
| residential | 2 039 | 89.7 % | 1.2 % | 9.1 % | 95.6 % |
| living_street | 117 | 75.2 % | 1.7 % | 23.1 % | 98.9 % |
| pedestrian | 86 | 12.8 % | 1.2 % | 86.0 % | 25.0 % |
| service | 56 | 62.5 % | 0.0 % | 37.5 % | 91.4 % |
| track | 14 | 71.4 % | 0.0 % | 28.6 % | 100.0 % |
| **gesamt** | 4 004 | 85.4 % | 1.6 % | 13.0 % | 91.8 % |

¹ Anteil der zugeordneten Abschnitte, deren OSM-Name gleich dem amtlichen Straßennamen ist (automatische Plausibilitätsprüfung, ersetzt nicht die manuelle Stichprobe).

## Ist-Tempo – Eimsbüttel

- Abschnitte mit amtlichem Regeltempo: 3 357 von 4 004
- Übereinstimmung mit OSM-maxspeed (wo beide eine Zahl haben): 96.4 % (2 958 von 3 070)
- Abschnitte mit zeitlich begrenzter Regelung (S-CONF-03, getrennt in `speed_conditional`): 151
- Regeltempo mehrdeutig (`speed_official_ambiguous`): 21
- Mehrere amtliche Tempi auf einem Abschnitt (`speed_official_conflict`): 43

| Regeltempo amtlich | Abschnitte | km |
| --- | ---: | ---: |
| 10 km/h | 1 | 0.1 |
| 20 km/h | 11 | 0.9 |
| 30 km/h | 1 761 | 253.7 |
| 50 km/h | 1 546 | 159.3 |
| 60 km/h | 12 | 2.0 |
| 70 km/h | 14 | 5.3 |
| 100 km/h | 12 | 2.9 |
| ohne Zahl (z. B. 5-7 km/h, variabel) / keine Zuordnung | 647 | 46.3 |

## HVS (S-CONF-04) und Zonen (S-CONF-02) – Eimsbüttel

| highway | Anzahl | in_hvs | Tempo-30-Zone | Tempo-20-Zone | verkehrsberuhigt |
| --- | ---: | ---: | ---: | ---: | ---: |
| motorway | 26 | 0 | 0 | 0 | 0 |
| motorway_link | 72 | 2 | 0 | 0 | 0 |
| trunk | 1 | 1 | 0 | 0 | 0 |
| primary | 566 | 484 | 1 | 0 | 0 |
| primary_link | 29 | 5 | 0 | 0 | 0 |
| secondary | 337 | 242 | 0 | 0 | 0 |
| secondary_link | 21 | 4 | 0 | 0 | 0 |
| tertiary | 537 | 6 | 15 | 0 | 0 |
| tertiary_link | 9 | 0 | 0 | 0 | 0 |
| unclassified | 94 | 0 | 18 | 0 | 0 |
| residential | 2 039 | 1 | 1 590 | 11 | 3 |
| living_street | 117 | 0 | 22 | 0 | 59 |
| pedestrian | 86 | 0 | 8 | 0 | 0 |
| service | 56 | 17 | 12 | 0 | 0 |
| track | 14 | 0 | 7 | 0 | 0 |

- in_hvs gesamt: 762 Abschnitte, 77.8 km
- in_hvs, aber OSM-highway residential/living_street/unclassified (prüfen): 1

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert und eindeutig | ok | 36526 Abschnitte |
| match_quality im Arbeitsgebiet gesetzt, außerhalb leer | ok | 4947 im Arbeitsgebiet, 31579 außerhalb |
| Ist-Tempo nur aus Werten der Quelle | ok | Werte [10, 20, 30, 50, 60, 70, 80, 100] |
| Zeitlich begrenztes Tempo nie als Regeltempo (S-CONF-03) | ok | 0 Verstöße |

## Manuelle Stichprobe

`reports/conflation_sample.csv`: 50 Zufallsabschnitte in Eimsbüttel (Seed 42, etwa gleich viele je match_quality), mit Links auf OSM-Karte und OSM-Way. Spalte `geoportal` ist leer, bis das Linkformat geklärt ist (docs/open_questions.md). Prüfende tragen `check_ok` (ja/nein) und `comment` ein.

| Ergebnis | Anzahl |
| --- | ---: |
| Zuordnung richtig | _offen_ |
| Zuordnung falsch | _offen_ |
| **Trefferquote** | _offen – nach manueller Prüfung eintragen_ |

## Lizenz

Abschnitte aus OpenStreetMap-Daten © OpenStreetMap-Beitragende, ODbL 1.0. Amtliche Attribute: Freie und Hansestadt Hamburg (Widmungen: BVM, dl-de/by-2.0; Höchstgeschwindigkeiten und Verkehrsmengen: Lizenz in der API nicht angegeben, siehe docs/open_questions.md).
