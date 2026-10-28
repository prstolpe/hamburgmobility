# Conflation amtlich ↔ OSM (Stufe 3)

Erzeugt: 2026-10-28T10:15:33+00:00 von `pipeline/s03_conflate.py`. Nicht amtlicher Entwurf.

## Datengrundlage

- Abschnitte: `data/interim/segments.parquet` (34 502 Abschnitte Hamburg)
- Arbeitsgebiet: Eimsbüttel + 500 m; abgeglichen werden Abschnitte, die ganz darin liegen (4 787). Außerhalb bleibt `match_quality` leer (keine amtlichen Daten abgerufen).
- Regelwerk: config/rules.yaml 0.3.0

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

## Trefferquote (Arbeitsgebiet, 4 787 Abschnitte)

| Quelle | exact | partial | none | exact km-Anteil |
| --- | ---: | ---: | ---: | ---: |
| zulaessige_hoechstgeschwindigkeiten | 3 958 | 83 | 746 | 90.3 % |
| de.hh.up:widmung_linie | 4 013 | 89 | 685 | 91.0 % |
| verkehrsmengen_dtv_hvs_2019 | 888 | 64 | 3 835 | 16.1 % |
| verkehrsmengen_dtv_bab_2019 | 30 | 2 | 4 755 | 3.2 % |

## match_quality (Tempo-Ebene) je highway-Klasse – Eimsbüttel

| highway | Anzahl | exact | partial | none | Name gleich¹ |
| --- | ---: | ---: | ---: | ---: | ---: |
| motorway | 26 | 88.5 % | 11.5 % | 0.0 % | 0.0 % |
| motorway_link | 72 | 72.2 % | 4.2 % | 23.6 % | 0.0 % |
| trunk | 1 | 100.0 % | 0.0 % | 0.0 % | 100.0 % |
| primary | 561 | 90.2 % | 2.1 % | 7.7 % | 93.1 % |
| primary_link | 28 | 64.3 % | 3.6 % | 32.1 % | 26.3 % |
| secondary | 328 | 87.2 % | 2.1 % | 10.7 % | 92.2 % |
| secondary_link | 21 | 57.1 % | 14.3 % | 28.6 % | 46.7 % |
| tertiary | 525 | 87.6 % | 1.1 % | 11.2 % | 95.9 % |
| tertiary_link | 9 | 33.3 % | 22.2 % | 44.4 % | 60.0 % |
| unclassified | 89 | 68.5 % | 2.2 % | 29.2 % | 92.1 % |
| residential | 2 013 | 89.4 % | 1.2 % | 9.4 % | 95.5 % |
| living_street | 117 | 75.2 % | 1.7 % | 23.1 % | 98.9 % |
| pedestrian | 86 | 12.8 % | 1.2 % | 86.0 % | 25.0 % |
| **gesamt** | 3 876 | 85.7 % | 1.7 % | 12.6 % | 91.7 % |

¹ Anteil der zugeordneten Abschnitte, deren OSM-Name gleich dem amtlichen Straßennamen ist (automatische Plausibilitätsprüfung, ersetzt nicht die manuelle Stichprobe).

## Ist-Tempo – Eimsbüttel

- Abschnitte mit amtlichem Regeltempo: 3 261 von 3 876
- Übereinstimmung mit OSM-maxspeed (wo beide eine Zahl haben): 96.3 % (2 897 von 3 009)
- Abschnitte mit zeitlich begrenzter Regelung (S-CONF-03, getrennt in `speed_conditional`): 150
- Regeltempo mehrdeutig (`speed_official_ambiguous`): 21
- Mehrere amtliche Tempi auf einem Abschnitt (`speed_official_conflict`): 42

| Regeltempo amtlich | Abschnitte | km |
| --- | ---: | ---: |
| 20 km/h | 11 | 0.9 |
| 30 km/h | 1 712 | 250.2 |
| 50 km/h | 1 500 | 155.9 |
| 60 km/h | 12 | 2.0 |
| 70 km/h | 14 | 5.3 |
| 100 km/h | 12 | 2.9 |
| ohne Zahl (z. B. 5-7 km/h, variabel) / keine Zuordnung | 615 | 44.4 |

## HVS (S-CONF-04) und Zonen (S-CONF-02) – Eimsbüttel

| highway | Anzahl | in_hvs | Tempo-30-Zone | Tempo-20-Zone | verkehrsberuhigt |
| --- | ---: | ---: | ---: | ---: | ---: |
| motorway | 26 | 0 | 0 | 0 | 0 |
| motorway_link | 72 | 2 | 0 | 0 | 0 |
| trunk | 1 | 1 | 0 | 0 | 0 |
| primary | 561 | 479 | 1 | 0 | 0 |
| primary_link | 28 | 5 | 0 | 0 | 0 |
| secondary | 328 | 235 | 0 | 0 | 0 |
| secondary_link | 21 | 4 | 0 | 0 | 0 |
| tertiary | 525 | 4 | 15 | 0 | 0 |
| tertiary_link | 9 | 0 | 0 | 0 | 0 |
| unclassified | 89 | 0 | 15 | 0 | 0 |
| residential | 2 013 | 1 | 1 566 | 11 | 3 |
| living_street | 117 | 0 | 22 | 0 | 59 |
| pedestrian | 86 | 0 | 8 | 0 | 0 |

- in_hvs gesamt: 731 Abschnitte, 75.9 km
- in_hvs, aber OSM-highway residential/living_street/unclassified (prüfen): 1

## Prüfungen

| Prüfung | Ergebnis | Detail |
| --- | --- | --- |
| segment_id unverändert und eindeutig | ok | 34502 Abschnitte |
| match_quality im Arbeitsgebiet gesetzt, außerhalb leer | ok | 4787 im Arbeitsgebiet, 29715 außerhalb |
| Ist-Tempo nur aus Werten der Quelle | ok | Werte [20, 30, 50, 60, 70, 80, 100] |
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
