# Review 2026-11 · Reststand nach der Umsetzung (Pakete P0–P6)

Stand 11.11.2026, rules.yaml 0.21.0, cycling_rules.yaml 0.11.1, design_rules.yaml 0.9.0, plain_language.yaml 0.9.1.
Bezug: `04_review_regelwerk.md` (Befunde F01–F38, Strukturempfehlungen 1–10, Annahmen A1–A11, Entscheidungen Q1–Q4
vom 08.11.2026) und `entscheidungen.md` (E1–E15). Die Pakete P0–P6 dieses Dokuments sind die Umsetzungspakete des
Reviews; sie sind **nicht** dieselben wie die Pakete P0–P6 der Entscheidungsvorlage (Abschnitt 5).

| Paket | Commit | Inhalt |
| --- | --- | --- |
| P0 Grundlagen | `ce13ce4` | Status inactive, halboffene Klassen, Herkunft, Verweise (rules 0.17.0, cycling 0.8.0, design 0.7.0) |
| P1 Klassifikation | `2ad3534` | F05, F06, F07, F13, F14, F22, F23, F25 (rules 0.18.0) |
| P2 Knotenpunkte | `51706c4` | F02, F03, F08, F09, F10, F24 (design 0.8.0, rules 0.19.0) |
| P3 Querschnitt und Radanlage | `860944a`, `44cab73` | F01, F04, F11, F17, F18, F20, G10, V-INV-05 (cycling 0.9.0, design 0.9.0) |
| P4 Radnetz | `ec906cc` | F12, F15, F16, F19 (cycling 0.10.0) |
| P5 Ist-Führung und Diskrepanz | `158967b` | F21, F26, Stufenfolge (rules 0.20.0, cycling 0.11.0) |
| P6 Invarianten, Export, Reststand | dieser Commit | Strukturempfehlung 6, V-INV-01/09, Texte, Export/Website (rules 0.21.0) |

## 1. Umsetzungsstand der Befunde F01–F38

Legende: **umgesetzt** = wie vorgeschlagen oder mit dokumentierter Abweichung (Abschnitt 3); **teilweise** = ein Teil
fehlt oder eine Invariante ist noch verletzt; **offen** = nicht angefasst.

| Nr. | Schweregrad | Stand | Paket / Commit | Anmerkung |
| --- | --- | --- | --- | --- |
| F01 | kritisch | umgesetzt | P3 `860944a` | Zelle GOW30.high_volume (S-05), Flags `gow30_high_volume`, `capacity_reduction_needed` (L-07); V-INV-04 erfüllt |
| F02 | kritisch | umgesetzt | P2 `51706c4` | JC-01 nur einstreifig, JC-06 Turbokreisel; V-INV-07 erfüllt |
| F03 | kritisch | umgesetzt | P2 `51706c4` | J-14 mit `crossing_signal_min_dtv` 12 000 (A8) |
| F04 | hoch | umgesetzt | P3 `860944a` | GOW30-Fahrbahn inkl. Radfahrstreifen (A2 am Original prüfen) |
| F05 | hoch | teilweise | P1 `2ad3534` | GOW50/GOW50_bus/ETW30 mit formula (V-INV-06 erfüllt); GOW30_* und ETW30 mit Bus ohne formula, V-INV-05 verletzt |
| F06 | hoch | umgesetzt | P1 `2ad3534` | C-G30-02 nur über Raum; Flag `existing_track_below_floor` in c05 |
| F07 | hoch | umgesetzt | P1 `2ad3534` | `access_radius` 50 m, `gap_close_m` 500 m (Q2 b) |
| F08 | hoch | umgesetzt | P2 `51706c4` | J-10/J-10b/c/d, Typ `not_applicable` (157 Knoten) |
| F09 | hoch | umgesetzt | P2 `51706c4` | N6 liest c07; Bericht in reports/junctions.md |
| F10 | hoch | umgesetzt | P2 `51706c4` | J-15, J-16; V-INV-02 erfüllt; `cycle_crossing_refuge` wird derzeit an keinem Knoten vergeben |
| F11 | hoch | umgesetzt | P3 `860944a` | PRF-03 `parking_by_category`; V-INV-03 erfüllt |
| F12 | hoch | umgesetzt | P4 `ec906cc` | Umbenennung **und** FGSV-Kennzeichnung mit Unsicherheitsband (beide Optionen) |
| F13 | mittel | umgesetzt | P1 `2ad3534` | in_hvs aus conn_score, conn_gow 0,87 (Q3 b) |
| F14 | mittel | umgesetzt | P1 `2ad3534` | `global_caveats`; noch 73 % „mittel“ wegen `fallback:conn_score` (offene Frage) |
| F15 | mittel | umgesetzt | P4 `ec906cc` | HAUPT auf ETW_ERF: own_path, Faktor 2,1 |
| F16 | mittel | umgesetzt | P4 `ec906cc` | Soll-Faktor aus bevorzugter Führung je Ebene |
| F17 | mittel | teilweise | P3 `860944a` | Reihenfolge D3 vor D2 (Q1 b); Flag `existing_trees_conflict` fehlt (keine Baumdaten) |
| F18 | mittel | umgesetzt | P3 `860944a` | `with_motor_traffic` 4,75 m per ref |
| F19 | mittel | umgesetzt | P4 `ec906cc` | `dtv_proxy` → Flag `filter_needed` |
| F20 | mittel | umgesetzt | P3 `860944a` | `oneside_min` 2,50 m (A6 am Original prüfen) |
| F21 | mittel | umgesetzt | P5 `158967b` | S-FEAT-11 nur Soll-Radnetz mit Umwegprüfung; Parallelroute mildert (0,5) |
| F22 | mittel | umgesetzt | P1 `2ad3534` | `separated_track_or_parallel_route` |
| F23 | mittel | umgesetzt | P1 `2ad3534` | S-FEAT-12, Flag `gow50_anbaufrei` (Q4 a) |
| F24 | mittel | umgesetzt | P2 `51706c4` | Mittelinsel RSV 4,00 m, `turbo_min_radius` 30 m |
| F25 | mittel | umgesetzt | P1 `2ad3534` | `crossing_demand` inactive; `place_score` als Auslöser zurückgestellt (Q2 b) |
| F26 | mittel | umgesetzt | P5 `158967b` | S-FEAT-13, Stufe c03b; V-INV-08 erfüllt |
| F27 | gering | umgesetzt | P0 `ce13ce4` | halboffene Intervalle, Schema-Prüfung |
| F28 | gering | umgesetzt | P0 `ce13ce4` | C-RUR-01 und Außerorts-Matrix inactive; V-INV-01 erfüllt |
| F29 | gering | teilweise | P6 | als Invariante V-INV-09 geführt (statt V-CONS-01); auf cat_final verletzt (20 Abschnitte, H-STR-01) |
| F30 | gering | offen | – | N7 schlägt weiter auch Glättungen vor, die H-STR-01 schon anwendet |
| F31 | gering | umgesetzt | P0 `ce13ce4` | Notizen S-FEAT-04/08 |
| F32 | gering | umgesetzt | P0 `ce13ce4` | `ref:` auf widths_m mit Gleichheitstest |
| F33 | gering | umgesetzt | P0 `ce13ce4` | PL-02 inactive, S-03 `scope: rural` |
| F34 | gering | offen | – | C-IMP-06 weiter ohne eigenen Faktor (1,35 vorgeschlagen) |
| F35 | Hinweis | umgesetzt | – | keine Änderung vorgeschlagen |
| F36 | Hinweis | offen | – | Notiz zu J-07 (Beschilderung der Vorfahrt, VwV-StVO) fehlt |
| F37 | Hinweis | offen | – | Abschlag `roundabout_max_dtv` bei hohem Radverkehr nicht geprüft |
| F38 | Hinweis | offen | – | N4 weiter über Soll-Tempo; Widerstandsfaktor mit Prompt 22 |

Summe: 30 umgesetzt (davon F35 ohne Änderung), 3 teilweise (F05, F17, F29), 5 offen (F30, F34, F36–F38). Alle drei
kritischen und alle neun hohen Befunde sind umgesetzt, F05 teilweise.

## 2. Strukturelle Empfehlungen 1–10

| Nr. | Empfehlung | Stand | Paket / Commit | Anmerkung |
| --- | --- | --- | --- | --- |
| 1 | Eine Quelle für Maße | teilweise | P0 `ce13ce4`, P1 `2ad3534`, P3 `860944a` | `ref:` (F32, F18) und `formula` für required_width GOW50/GOW50_bus/ETW30; GOW30_* sind Bereiche ohne formula |
| 2 | Klassifikation und Querschnitt koppeln | teilweise | P1, P3 | Klassifikation prüft mit dem Mindestprofil; Implikation V-INV-05 ist verletzt (Ladezone, Busfahrbahn ETW30, GOW30-Profil) |
| 3 | Begriffsverzeichnis (`glossary`, Pflichtfeld `unit`) | offen | – | auch die offene Frage „max_dtv ohne Einheit“ gehört dazu |
| 4 | Intervallkonvention `[min, max)` | umgesetzt | P0 `ce13ce4` | config/schema/intervals.py |
| 5 | Status `inactive` | umgesetzt | P0 `ce13ce4`, P1 `2ad3534` | C-RUR-01, Außerorts-Matrix, PL-02, `crossing_demand` |
| 6 | Ausführbare Invarianten | umgesetzt | P0–P6 | Block `validation.invariants`; 7 erfüllt, 2 verletzt (V-INV-05, V-INV-09), beide als strict xfail mit offener Frage |
| 7 | Goldene Fälle G01–G12 | umgesetzt | P0–P4 | G11 (P0), G02–G04 (P1), G05–G08 (P2), G01/G10/G12 (P3), G09 (P4) |
| 8 | Stufenfolge | umgesetzt | P2 `51706c4`, P5 `158967b` | N6 nach c07; c03b vor s08 und c04 |
| 9 | Prüfreihenfolge im Regelregister | offen | – | regelregister.xlsx nicht neu sortiert; Reihenfolge in Abschnitt 5 übernommen |
| 10 | Varianten als Schalter | offen | – | entspricht E15 und der offenen Frage „Varianten umschaltbar machen“ |

### Invarianten nach dem Lauf vom 11.11.2026 (reports/validation.md)

| ID | Ergebnis | Detail |
| --- | --- | --- |
| V-INV-01 | erfüllt | 5 Kategorien in cat_final, alle mit Matrixzeile und Profilregel bzw. in `no_profile_categories` (SW) |
| V-INV-02 | erfüllt | 16 244 Knoten, alle mit Soll-Typ |
| V-INV-03 | erfüllt | kein Parken/Radfahrstreifen an GOW50, kein 2. Fahrstreifen/Mittelstreifen an GOW30 |
| V-INV-04 | erfüllt | kein Radfahrstreifen an GOW30 über 10 000 Kfz/24 h (c05, c06) |
| V-INV-05 | **verletzt** (erwartet) | 1 075 Abschnitte, 135,1 km (ETW30 768, GOW30 291, GOW50 16) |
| V-INV-06 | erfüllt | required_width value = formula |
| V-INV-07 | erfüllt | JC-01 an 283 einstreifigen Kreiseln, 59 Turbokreisel mit JC-06 |
| V-INV-08 | erfüllt | Ist-Führung gleich in c05, s08 und c04 |
| V-INV-09 | **verletzt** (erwartet) | 20 HVS-Abschnitte (0,8 km) als ETW30, alle aus H-STR-01 Schritt (2); Kaskade allein erfüllt |

## 3. Abweichungen von den Vorschlägen

Gesammelt aus CHANGELOG.md und den Commit-Nachrichten P0–P6. Alle sind in den Regeldateien (note) begründet.

- **F01**: Die Grenze gilt einschließlich (10 000 Kfz/24 h → Radfahrstreifen, 10 001 → Radweg); `max_dtv` wird als
  Obergrenze gelesen, nicht als Klassentabelle. Zusätzlich L-07 mit `capacity_reduction_dtv` (DTV − 13 909) und
  S-05 auch für P-SAF-01 (c04). Das ältere Flag `gow30_dtv_above_profile` besteht parallel (offene Frage).
- **F05**: Nur GOW50, GOW50_bus und ETW30 erhalten eine formula; GOW30_narrow/wide bleiben Bereiche ohne formula. Folge:
  V-INV-05 verletzt.
- **F06**: Das Flag `existing_track_below_floor` steht in c05 (`facility_flags`), weil die Ist-Breite erst in der
  Radnetzkette vorliegt. `bus_route` = mindestens ein Bus je Spitzenstunde und Richtung (PRF-02).
- **F07**: Der Lückenschluss `gap_close_m` wirkt in H-STR-01 Schritt (3) (GOW50 zwischen zwei GOW30), nicht in Regel (4)
  wie im Review; Regel (4) verlängert nur und behält `min_run_m`. Der Abstand zur Schule/Kita ist eine OSM-Näherung.
- **F08**: J-10 erfasst nur noch eigenständige RSV/HAUPT-Radwege an SW; der goldene Fall j13 wurde deshalb umgedeutet.
- **F09**: Der frühere Abgleich N6 ↔ c07 entfällt; N6-Flags erscheinen nicht mehr auf Abschnitten und der Website.
- **F10**: J-15 vergibt bei Bedingung wie J-14 LSA, sonst `cycle_crossing_refuge`; dieser Typ kommt in den Daten
  derzeit nicht vor.
- **F12**: Beide Optionen kombiniert (Umbenennung „Radvorrangroute / Radroute+“ und FGSV-Kandidat mit
  `demand_band_factor`); keine Kategorie ändert sich.
- **F13**: conn_gow 0,87 trifft die Bezugsgröße nur ungefähr (82,6 statt 78,0 km Nicht-HVS-GOW).
- **F14**: Wirkung kleiner als erwartet (hoch 7,0 → 19,7 % der Länge); „mittel“ kommt jetzt fast nur aus
  `fallback:conn_score`.
- **F15/F16**: ETW_ERF rechnet auf allen Ebenen mit Schrittgeschwindigkeit (`soll_factor_by_category` geht vor), obwohl
  die Matrix dort für RSV/HAUPT eine eigene Trasse bevorzugt (sonst lägen Hauptrouten bevorzugt in Fußgängerzonen).
- **F17**: `existing_trees_conflict` nur als TODO; D2 betrifft nur neue Baumstreifen.
- **F18**: Annahme „Kfz frei“ für alle Soll-Fahrradstraßen (`cycle_street_motor_traffic: true`), kein Attribut.
- **F19**: Mit Proxy wird die Bedingung „unbekannt“ (nicht „nicht erfüllt“); `filter_needed` senkt die confidence nicht.
- **F21**: Parallelroute nur im Soll-Radnetz RSV/HAUPT/BASIS (Review: HAUPT/BASIS) und als Milderung mit Gewicht 0,5
  statt Ersatz (neue Setzung `severity_if`, halbe Gestaltungsstärken auf der Website).
- **F24**: `turbo_min_radius` gilt auch im Fallback (`condition_by_type`), nicht nur in J-01.
- **F26**: Neue Stufe c03b zwischen cycle-network und s08; Radweg-Tag ohne Radgraph zählt als Radweg (Prüfliste
  `track_tag_only`, 107,7 km).
- **F27**: `intensity_upgrade` jetzt `>=` statt `>` (keine Datenänderung).
- **F29**: Statt einer Regel V-CONS-01 die Invariante V-INV-09; sie bezieht sich auf cat_final und ist dort verletzt.
  Die Review-Angabe „Test besteht“ galt nur für die Kaskade vor der Harmonisierung.
- **Strukturempfehlung 6**: `no_profile_categories` steht nur in design_rules PRF-04 (keine zweite Liste in rules.yaml);
  „Profilregel“ = Eintrag in PRF-03 `parking_by_category`.

## 4. Offene Fragen, gruppiert und priorisiert

docs/open_questions.md enthält nach P6 **107 offene** und 78 erledigte Punkte (P6: 2 erledigte Punkte abgehakt, eine
neue Frage V-INV-09). Priorität: **A** = blockiert eine Invariante, einen kritischen Befund oder die Veröffentlichung;
**B** = ändert Ergebnisse spürbar; **C** = Feinschliff oder später (Prompt 22, außerorts).

| Gruppe | Anzahl | davon A |
| --- | ---: | ---: |
| 4.1 Entscheidung durch prstolpe / Projektteam | 40 | 6 |
| 4.2 Prüfung am Original (A2–A7 u. a.) | 18 | 6 |
| 4.3 Daten beschaffen oder prüfen | 22 | 4 |
| 4.4 Stichproben und Durchsicht (E1) | 17 | 5 |
| 4.5 Technisch | 10 | 1 |
| **Summe** | **107** | **22** |

### 4.1 Entscheidung durch prstolpe / Projektteam (40)

| Prio | Frage (Kurzform) | Abschnitt in open_questions.md |
| --- | --- | --- |
| A | V-INV-09: H-STR-01 Schritt (2) für HVS sperren, Override je Abschnitt oder Invariante nur auf die Kaskade? | Review P6 |
| A | V-INV-05: Ladezone als Abbaustufe, required_width GOW30_*/ETW30_bus per formula oder Invariante enger fassen? | Review P3 |
| A | HVS als GOW30 (64,6 % der HVS-km) und GOW30 über dem CROW-Profil: E2 entscheiden (Arbeitsbasis C) | Klassifikation; Querschnitt Prompt 19 |
| A | F14: `fallback:conn_score` als globaler Vorbehalt oder je Abschnitt? | Review P1 |
| A | Schwellen `assumption` freigeben (conn_gow, access_radius, frontage, N2–N4, Machbarkeitsklassen) | Fachlich |
| A | F01: S-05-Grenze einschließlich so gemeint? | Review P3 |
| B | Gewichte conn_score, place_score, Priorisierung | Fachlich |
| B | C-MISS-01/C-CONF-01 freigeben | Klassifikation |
| B | F03 Umsetzung „Radroute quert den Zug“ bestätigen | Review P2 |
| B | F08 `not_applicable`-Ist-Prüfung; F10 Mittelinselbreite ERSCHL | Review P2 |
| B | F15/F16 Schrittgeschwindigkeit in ETW_ERF bestätigen; F15 auch für freigegebene Gehwege | Review P4 |
| B | F18 „Kfz frei“ auch für die Ist-Prüfung P-COM-01 | Review P3 |
| B | F21 Umwegmessung S-FEAT-11; F26 unbekannte Radanlage an Hauptstraßen als „nein“ | Review P5 |
| B | Projekt-Sollbreiten zwischen ERA und NL-Hauptnetz | Radnetz |
| B | Nutzung: max_dtv für ETW30/GOW50 | Diskrepanz |
| B | GOW30_narrow mit Untergrenze; H-STR-01 Inseln und 200-m-Mindestlänge; Tracks mit maxspeed=walk | Querschnitt; Harmonisierung |
| B | ETW_ERF eigene Knotenzeilen | Radnetz Prompt 20 |
| C | Annahmenpakete der Prompts 15–20 und Metadaten 0.1.1 freigeben (7 Punkte) | Radnetz |
| C | S-NET-03 400 m, Standardtempo, Puffer, ALKIS-Listen, N1/N2/N6, N3-Kompaktheit freigeben | Netz; Merkmale; Kohärenz |
| C | Außerorts: ETW60 mixed, roundabout_single_lane_cycle_yield; Neuwerk/Scharhörn | Radnetz; Ganz Hamburg |

### 4.2 Prüfung am Original (18)

| Prio | Quelle und Wert | Betrifft |
| --- | --- | --- |
| A | CROW-Handreiking GOW30 2023: Spannen 5,80–8,40 / 8,40–10,70 m enthalten die Fietsstroken (A2) | F01, F04 |
| A | StVO § 45 (9) S. 4 Nr. 6, Fassung 2024: „unmittelbarer Bereich“ und Lückenschluss 500 m (A4) | F07 |
| A | RASt 06: Gehweg 2,50 m, Fahrbahn 6,50 m, Bild 17 Mischfahrbahn 4,75 m | F05, F18 |
| A | ERA 2010: einseitiger Zweirichtungsradweg 2,50 m (A6); Bild 7 Belastungsbereiche (S-04) | F20, C-FAC-03 |
| A | FGSV-Hinweise Radschnellverbindungen: 10 km, 2 000 Rad/24 h (A5) | F12 |
| A | CROW/Fietsberaad: Rad wartepflichtig am Turbokreisel (A3); `turbo_min_radius` 30 m | F02, F24 |
| B | HBS 2015: L-02 (900 Kfz/h, v/c 0,85), Kreisverkehrsgrenzen 25 000/35 000 | F35, F37 |
| B | Vorrang am Kreisverkehr (CROW/SWOV/StVO) – Rechtsprüfung | F02 |
| B | ReStra/RASt: Gehwegbreiten (Sensitivität „Querschnitt passt?“) | c06 |
| B | CROW-Ontwerpwijzer 2016: Umwegfaktor, Breiten, Fahrradstraße | Radnetz |
| C | RIN-Kategoriengruppen; FGSV-Neufassungen; Seitenangaben; Hamburger Standards (ReStra, PLAST); Delft-Referenzdichte (CBS) | Fachlich; Radnetz |

VwV-StVO zu Z. 244.1 (A7, F19/F36) steht in keiner offenen Frage; bei der Prüfung von F36 mit erledigen.

### 4.3 Daten beschaffen oder prüfen (22)

| Prio | Frage (Kurzform) | Wer |
| --- | --- | --- |
| A | Amtliche Ortsgrenze/Ortsdurchfahrten (C-RUR-01, F28) | GIS |
| A | Schulen/Kitas amtlich statt OSM (F07, `school_or_kita_access_m`) | GIS |
| A | HVS 2019 gegen HVS-Karte 2023; Hauptstraßen mit Soll ETW30 (Lücken im HVS-Abgleich) | GIS |
| A | Straßenbaumkataster (F17 `existing_trees_conflict`) | GIS |
| B | 292 Soll-ETW30 mit Ist-Tempo > 30; Ist-Tempo fehlt auf 7,4 % | GIS |
| B | `bahnigkeit_official`; Mittelmarkierung; Radwegbreiten (11 %); Radweg-Tag ohne Radgraph (107,7 km) | GIS |
| B | Ist-Knotentyp: Ampelradius 30 m, Gehwegüberfahrten, N5-Torsituation | GIS |
| C | Fußgängerzonen amtlich, zeitlich begrenzte Tempi, GTFS-Periode ab 12/2026, DB Rad+, Hochschulen, Lärm/Steigung, Stadtbahn/U5, Rettungsdienstdaten | GIS, Team |

### 4.4 Stichproben und Durchsicht (E1) (17)

| Prio | Frage (Kurzform) | Datei |
| --- | --- | --- |
| A | Manuelle Stichproben Conflation, Klassifikation, Transekte (Voraussetzung Veröffentlichung) | reports/*_sample.* |
| A | conn_gow kalibrieren; F13-Stichprobe neue/entfallene Nicht-HVS-GOW | reports/classification.md |
| A | `place_score`/`crossing_demand` an E1 kalibrieren (F25) | – |
| A | Top 30 gegenlesen | reports/priority_top30.md |
| A | Externe Fachprüfung (Straßen und Radnetz) | reports/validation*.md |
| B | Knotenpunkte je Soll-Typ, 20 Routen, 30 Radnetz-Stichproben, Zählstellen außerhalb RSV/HAUPT | reports/junctions_review.csv u. a. |
| B | F23 anbaufrei; Flag-Liste Kohärenz; flow/sparse D1–D3; S-CONF-Schwellen | – |
| C | Texte Methodenseite/Steckbriefe auf einfache Sprache | config/plain_language.yaml |

### 4.5 Technisch (10)

| Prio | Frage (Kurzform) |
| --- | --- |
| A | Veröffentlichung: site-data an Release data-latest, `check-range.sh` nach Deployment |
| B | F01: `gow30_dtv_above_profile` oder `gow30_high_volume` streichen |
| B | Varianten als Schalter (Strukturempfehlung 10) |
| B | F19 `proxy_betweenness` und F21 Gewicht 0,5 in V-SENS-01 aufnehmen |
| C | `max_dtv` ohne Einheit; guide.md: Merkmalsnamen, `cat_confidence`; F06-Hinweis zum Flag in c05; Test auf Smartphone/Bildschirmleser |

## 5. Kandidaten für V-SENS-01

V-SENS-01 variiert heute nur Schwellen der Kaskade (darunter `conn_gow` und `access_radius`); c08 variiert 45 Werte der
Radnetzkette (darunter `proxy_betweenness`, `turbo_min_radius`, `crossing_signal_min_dtv`,
`cycle_street_carriageway.with_motor_traffic`). Neue Setzungen aus P0–P5, die in keiner Variation stehen:

| Wert | Datei / Regel | Herkunft | Wirkung |
| --- | --- | --- | --- |
| `gap_close_m` 500 m | rules H-STR-01 | StVO 2024 (Fassung prüfen) | cat_final (Harmonisierung) |
| `min_run_m` 200 m (N2) | rules N2/H-STR-01 | assumption | cat_final; auch Ursache von V-INV-09 |
| `severity_if` 0,5 (Parallelroute) | rules D-DES-01 | assumption | Diskrepanz, Priorität |
| S-FEAT-11 Puffer 200 m, Umweg P-DIR-01 | rules S-FEAT-11 | assumption | Parallelroute |
| `anbaufrei` `min_share` 0,8, `buffer_m` 30 m | rules S-FEAT-12 | assumption | Hinweis, D-SPD-01 |
| `demand_band_factor` 2,0; `fgsv_rsv_candidate` 10 km / 0,5 | cycling C-NET-06 | assumption (A5) | rsv_confidence, FGSV-Kandidat |
| `walking_pace_area` 2,1 | cycling routing_impedance | assumption (A8) | Netzentwurf (braucht neuen Lauf c03) |
| `median_width_m.RSV` 4,00 m | design JC-04 | assumption (A8) | Platzbedarf, kein Typwechsel |
| `de.separated_twoway.oneside_min` 2,50 m | cycling widths_m | A6 | floor c05 |
| S-05 `dtv_above` 10 000 | rules requirements.GOW30 | swov_crow | 378 km `gow30_high_volume`; Grenzlage zeigen, nicht kalibrieren |

Reihenfolge der Prüfung nach Strukturempfehlung 9: `conn_gow`, `access_radius`, `frontage`, `required_width.GOW50`,
`elements_min_m.sidewalk.standard`, `cycle_street_carriageway`, `roundabout_max_dtv`, RSV-Auslöser, Maschenweiten.

## 6. Entscheidungsvorlage E1–E15: was der Review nicht abdeckt

`entscheidungen.md` hat kein Statusfeld; die Spalte „gewählte Option“ ist leer. Entschieden sind nur Q1–Q4 im Review.

| ID | Thema | Bezug zum Review | Stand |
| --- | --- | --- | --- |
| E1 | Prüfung gegen die Wirklichkeit | Grundlage für F07, F13, F23, F25 | offen (Gruppe 4.4) |
| E2 | Umgang mit Verkehrsmengen | A1: Arbeitsbasis C; F01 setzt die Kennzeichnung `capacity_reduction_needed` um | teilweise, Entscheidung offen |
| E3 | Sammelstraßen mit Linienbus | F06 nutzt `bus_route` nur für die Breite | offen |
| E4 | Rückkopplung Querschnitt → Kategorie | Strukturempfehlung 2, V-INV-05 | offen |
| E5 | Knotenzeile „Radroute quert GOW50“ | F03 (J-14) | umgesetzt (P2) |
| E6 | Ist-Knotentyp | – | offen |
| E7 | Richtungsfahrbahnen, kurze Inseln | – | offen |
| E8 | Randbereich außerhalb Hamburgs | – (F28 betrifft nur außerorts) | offen |
| E9 | Zweirichtungsradwege, Lage | F26 (eine Ist-Führung je Seite) | teilweise (P5) |
| E10 | Amtliches Radnetz | – | offen |
| E11 | Haltestellen, Einbahnstraßen | – | offen |
| E12 | Umwegprüfung Maschenrouten | F21 nutzt eine Umwegprüfung nur für Parallelrouten | offen |
| E13 | Oberflächenkonzept | – (P6 hat nur neue Felder geprüft) | offen |
| E14 | Export, Formalia, Bedienfehler | – | offen |
| E15 | Varianten auf der Seite | Strukturempfehlung 10 | offen |

Von den Paketen der Entscheidungsvorlage ist damit keines vollständig erledigt; P3 (E5) und P5 (E9) sind teilweise
abgedeckt. Folgeaufträge laut CLAUDE.md, beide noch offen: **prompts/22_target_scenario.md** (Zielszenario statt heutiger
Mengen; löst auch F38/N4 und die Szenario-Sensitivität) und **prompts/23_junction_performance.md** (Wartezeiten an
Knotenpunkten Ist/Soll; nutzt HBS-Verfahren, siehe 4.2).

## 7. Export und Website

Nach P6 erstmals seit vor P0 neu erzeugt: `make validate`, `make export-cycling` (c08 und Export), `make export`,
`make web`, `make test` (1 543 bestanden, 2 xfail: V-INV-05, V-INV-09), `make a11y` (40 Prüfungen, keine kritischen oder
ernsten Befunde). data/out 516 MB. Alle neuen Felder aus P1–P5 kommen im Steckbrief an: `gow50_anbaufrei` (hints),
`global_caveats` (Methodenseite), `gow30_high_volume`, `capacity_reduction_needed`, `filter_needed`,
`haupt_through_pedestrian_area`, `parallel_cycle_route` (Hinweise Radnetz), `rsv_fgsv_candidate`/`rsv_confidence`
(RSV-Block), Knotentypen `not_applicable` und JC-06 (Knoten-Steckbrief), halbe Gestaltungsstärken. Keine Lücken in web/
gefunden; geändert wurde nur die Kategoriebeschreibung GOW30 (plain_language.yaml 0.9.1).

## 8. Nächste Schritte

1. **E1 b ausführen:** Stichproben und Prüflisten ausfüllen (Klassifikation, Transekte, Knoten, Radnetz, Top 30); sie
   tragen die Kalibrierung von `conn_gow`, `access_radius`, `place_score` und die Prüfung von `anbaufrei`.
2. **Zwei Invarianten entscheiden:** V-INV-09 (HVS in H-STR-01 Schritt 2 sperren?) und V-INV-05 (Ladezone als
   Abbaustufe, required_width GOW30/ETW30_bus per formula) – danach `expected: holds` und xfail entfernen.
3. **Originalprüfung in einem Termin:** CROW GOW30 (A2), StVO § 45 (9) (A4), RASt 06 Bild 17, ERA 2010 (A6), FGSV
   RSV-Hinweise (A5), CROW/Fietsberaad Turbokreisel (A3), VwV-StVO Z. 244.1 (A7).
4. **Entscheidungsvorlage ausfüllen:** E2 (Arbeitsbasis C bestätigen), E3, E4, E6; die übrigen E-Punkte priorisieren.
5. **V-SENS-01 erweitern** um Harmonisierung (`gap_close_m`, `min_run_m`) und die Setzungen aus Abschnitt 5; danach
   Strukturempfehlung 10 (Varianten als Schalter, E15).
6. **Restbefunde schließen:** F30 (N7), F34 (C-IMP-06), F36 (J-07-Notiz), F37 (Kreisel-Abschlag); Strukturempfehlung 3
   (Begriffsverzeichnis mit `unit`).
7. **Prompt 22 und 23** angehen (Zielszenario; Wartezeiten an Knoten), F38 dort lösen.
8. **Veröffentlichung vorbereiten:** site-data an Release, Range-Prüfung, Test mit Smartphone und Bildschirmleser,
   externe Fachprüfung mit reports/validation.md und reports/validation_cycling.md.
