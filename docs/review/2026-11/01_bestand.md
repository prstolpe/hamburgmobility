# Review 2026-11 · Phase 1: Bestandsaufnahme

Stand: 2026-11-07, Branch `review/2026-11` (Code = `radnetz-setup` 8443aa7), rules.yaml 0.16.0, cycling_rules.yaml 0.7.0,
design_rules.yaml 0.6.0. Nicht amtlicher Entwurf. Alle Zahlen stammen aus den Skripten unter `analysis/review_2026_11/`
(je Abschnitt genannt) und lassen sich neu erzeugen; Zwischenergebnisse liegen unter `data/scenarios/` (nicht in Git).

## Kurzfassung

1. **Die Pipeline ist deterministisch.** Zwei vollständige Läufe (`make rerun FROM=network`, 8 Kerne, kalter Cache) und der
   Produktivlauf vom selben Tag ergeben byte-gleiche Zwischenergebnisse (23 von 23 Dateien) und gleiche Kacheldaten. Es
   unterscheiden sich nur Zeitstempel, Laufzeitangaben und der Erzeugungspfad in den PMTiles-Metadaten.
2. **Nebenbefund Datenschutz:** Die veröffentlichten PMTiles auf hamburgmobility.de tragen den lokalen Pfad
   `/Users/raphael/Code/web_projects/SFP/...` (Felder name, description, generator_options).
3. **Keine Prüfung gegen die Wirklichkeit:** Alle 176 Regeln haben `status: draft`. Keine der fünf Prüflisten ist
   ausgefüllt (0 von 520 Zeilen), die Transektmessung fehlt, es gibt keine GitHub-Issues. Die einzigen fachlichen
   Korrekturen sind 7 Overrides (Reeperbahn, Sengelmannstraße).
4. **Offene Fragen:** 159 Einträge: 85 offen, 4 mit Teilantwort, 6 beantwortet und noch nicht eingearbeitet (5 davon
   verweisen auf Prompt 22/23), 64 eingearbeitet. 46 der 85 offenen Fragen richten sich an eine Verkehrsplaner*in.
5. **Der Wechsel GOW30 → GOW50** (rules.yaml 0.14.0, zurückgenommen in 0.15.0) betraf 358 km auf 3 204 Abschnitten,
   fast nur Hauptverkehrsstraßen mit 11 000–110 000 Kfz/Tag (Median 25 000). Auf 324 km davon gilt heute GOW30, darunter
   175 km Soll-RSV/HAUPT-Radrouten; 2 265 Knotenpunkte grenzen an.
6. **Wird die Nutzung zur Bestimmung der Funktion verwendet?** In 0.14.0 ja (Ist-DTV entschied zwischen GOW30 und GOW50).
   Im heutigen Stand nur mittelbar. Die HVS-Eigenschaft (`in_hvs`) stammt aus der DTV-Zählkarte 2019 und macht 85 % des
   GOW-Netzes aus. Das Gewicht `dtv_norm` im `conn_score` entscheidet über die GOW-Eigenschaft von nur 11 km.

---

## 1 Code und Reproduzierbarkeit

### 1.1 Determinismus nach der Parallelisierung

Methode: zwei vollständige Läufe in eigenen Git-Worktrees (`analysis/review_2026_11/run_worktree.sh det1|det2 network`)
mit gleichen Rohdaten (`data/raw`, Manifest unverändert), leerem Cache und allen 8 Kernen; Vergleich je Datei und Spalte
über segment_id/edge_id/node_id/route_id (`compare_runs.py`, Gleitkomma mit relativer Toleranz 1e-9; zusätzlich SHA-256
der Dateien). Einen seriellen Vergleichslauf gab es nicht: Die Gleichheit seriell/parallel ist laut Commit ffb75a9 und
8443aa7 bereits geprüft (Entscheidung prstolpe 2026-11-07).

| Vergleich | Zwischenergebnisse (`data/interim`, 23 Dateien) | Export (`data/out`, 50 000 Dateien) |
|---|---|---|
| Lauf 1 ↔ Lauf 2 | alle byte-gleich (gleicher SHA-256) | gleich bis auf `meta.json` und 3 PMTiles |
| Lauf 1 ↔ Produktivlauf (15:03–15:16 UTC) | alle byte-gleich | wie oben (Grundkarte gehört nicht zu `make rerun`) |

Ursachen der verbleibenden Unterschiede (keine fachlichen):

| Datei | Ursache | Beleg |
|---|---|---|
| `meta.json` | Feld `generated` (Zeitstempel) | einzige Zeile im Diff |
| `tiles/*.pmtiles` | tippecanoe schreibt den absoluten Ausgabe- und Eingabepfad in `name`, `description`, `generator_options`; die Worktrees liegen unter einem anderen Pfad | Wurzelverzeichnis, Blattverzeichnisse und Kacheldaten aller drei Dateien SHA-gleich |
| `reports/*.md` | Zeile „Erzeugt: <Zeitstempel>“, Laufzeitspalten (z. B. `reports/cycle_demand.md`, Spalte „Laufzeit s“) | nach Ausblenden dieser Zeilen keine Unterschiede |

Keine Hinweise auf Reihenfolgeabhängigkeit, Zufall ohne Seed, Race Conditions oder Gleitkomma-Streuung. Auch die
Monte-Carlo-Sensitivität (`validation.parquet`, `validation_cycling.parquet`) ist reproduzierbar.

**Nebenbefund:** Die veröffentlichten Kacheln zeigen den lokalen Pfad mit Benutzernamen. Geprüft mit
`pmtiles show https://hamburgmobility.de/tiles/segments.pmtiles` (Feld `name`). → Optionspapier (Export: tippecanoe mit
`--name`/`--description` und relativem Arbeitsverzeichnis).

### 1.2 Laufzeit je Stufe

Lauf 1 (8 Kerne, kalter Cache, ab `network`): 30 min Gesamtzeit, Höchstspeicher 2,8 GB.

| Stufe | Dauer | | Stufe | Dauer |
|---|---:|---|---|---:|
| network | 0:50 | | cycle-graph | 1:08 |
| conflate | 0:57 | | cycle-demand | 1:53 |
| **features** | **7:36** | | cycle-network | 1:24 |
| **crosssection** | **3:46** | | cycle-principles | 1:51 |
| classify + harmonise | 0:06 | | cycle-facility | 0:06 |
| **coherence** | **4:51** | | **cross-section-soll** | **4:02** |
| overrides + discrepancy | 0:12 | | junctions | 0:15 |
| validate (parallel zur Radkette) | – | | validate-cycling + export | 1:33 |

Eine Neurechnung ab `classify` (der häufigste Fall bei Regeländerungen) dauert rund 18 min. Die vier langsamsten Stufen
(features, coherence, Soll-Querschnitt, Querschnitt) machen zusammen zwei Drittel aus.

### 1.3 Tests

`pytest --cov=pipeline` (`data/scenarios/review_static/coverage.json`): **1 280 Tests grün**, Gesamtabdeckung 54 %.

| Teil | Abdeckung | Bemerkung |
|---|---:|---|
| `pipeline/lib/*` (Rechenkerne, 41 Module) | 91–100 % (meist ≥ 95 %) | Ausnahmen: `links.py` 33 %, `boundary.py` 78 %, `http.py` 81 % |
| Stufen-Skripte `s0*`, `c0*`, `validate.py` | 0–36 % | lesen Daten, schreiben Reports; geprüft über die Datentests `tests/test_*_data.py` gegen `data/interim` |
| goldene Fälle | 29 (Straße) + Radnetz-Fälle in `tests/golden/cycling/` | — |

Die Rechenlogik ist gut getestet. Die Stufen-Skripte sind nur über ihre Ausgaben abgedeckt. Fällt ein Report oder eine
Prüfung im Skript weg, merkt das kein Test.

### 1.4 Regelwerk und Code

`rule_inventory.py` (`data/scenarios/review_static/rules.csv`, `literals.csv`):

| | rules.yaml | cycling_rules.yaml | design_rules.yaml |
|---|---:|---:|---:|
| Regeln mit `id` | 54 | 78 | 44 |
| davon `status` draft / reviewed / approved | 54 / 0 / 0 | 78 / 0 / 0 | 44 / 0 / 0 |
| ohne `source_type` (auch geerbt) | 0 | 0 | 0 |
| ID nicht im Code (Volltext) | 0 | 12 | 11 |
| ohne Test oder goldenen Fall | 6 | 24 | 13 |

- **„Nicht im Code“ heißt meist „tabellengesteuert“:** Die Knotentabelle J-01…J-13, die Widerstandsfaktoren C-IMP-02…08
  und die Trennungsmatrix werden aus der YAML gelesen; ihre IDs erscheinen in den `rule_trace`-Spalten (geprüft in
  `rules.csv`, Spalte `rows_with_id_in_trace`). C-PRI-07 und C-PRI-11 sind unter ihren Prüf-IDs P-SAF-04 bzw. P-ATT-03
  umgesetzt.
- **Ohne Umsetzung** (weder im Code noch in einem Trace, nur Prosa):
  - S-03: Zweirichtungsradweg innerorts nur einseitig. Wird nur als Teilerfüllung in C-PRI-03 erwähnt; keine Prüfung, ob die
    Straße einseitige Bebauung hat.
  - PL-06: Radverkehr in Gegenrichtung auf ETW30-Einbahnstraßen. Keine Prüfung, keine Ausgabe.
  - PL-04: der Teil „1,00 m Trennstreifen bei GOW50 mit Bus“. Nur der Mindestwert 0,75 m wirkt (steht als offene Frage
    bereits in open_questions.md, Prompt 19 PRF-06).
- **Schwellen im Code:** keine fachlichen. Von 205 Zahlenliteralen außerhalb trivialer Werte sind alle Darstellung
  (Kartengrößen, Top-N-Listen), Geometrie-Toleranzen (`GAP_TOL_M = 0.05`, `_SNAP_M = 0.01`, `OSM_BBOX_MARGIN_DEG`) oder
  Report-Klassen (`validation.speed_bucket`).
- **Prozessregeln ohne Spur je Zeile:** 53 Regeln (Netzbildung S-NET-*, Merkmale S-FEAT-*, Validierung V-*, Nachfrage
  C-DEM-*, Knotenbildung J-M-*) schreiben keinen `rule_trace` je Abschnitt. Das ist für Prozessschritte richtig; ob sie
  wirken, zeigen nur die Reports.

### 1.5 Doppelte Logik und Inkonsistenzen (Stichprobe)

- **Begleitende Radwege beidseitig:** C-FAC-05 zählt sie als Radweg je Seite, C-PRI-02 als Zweirichtungsradweg (steht in
  open_questions.md, Prompt 18). Gleicher Abschnitt, zwei Ist-Führungen je nach Stufe.
- **Querschnitt-Rückkopplung nur als Flag:** D5 (GOW50 → GOW30 vorschlagen) schreibt `cat_change_proposal` (137
  Abschnitte), D7 (Route verlegen) ein Flag (534 Abschnitte). Keine Stufe liest diese Vorschläge wieder ein → 2b.
- **Gleicher Spitzenstundenanteil an drei Stellen:** C-FAC-03 (0,10), Notiz zu L-02 (0,10 × 0,55 Lastrichtung), J-Regeln
  mit Tageswerten; der Lastrichtungsfaktor 0,55 steht nur im Text.
- **`docs/source_policy.md` fehlt.** Der Prompt verweist darauf; die Quellenregeln stehen in CLAUDE.md und guide.md.
  Dieser Review wendet die CLAUDE.md-Regeln an (source, source_type, status; keine erfundenen Schwellen).

## 2 Offene Fragen

`open_questions.py` (`data/scenarios/review_static/open_questions_status.csv`, eine Zeile je Eintrag mit Zeilennummer,
Status, Regeln und Wirkungsbereich). Einstufung automatisch nach Antworttext, dann von Hand nachgesehen (7 Korrekturen,
im Skript als `MANUAL` vermerkt).

| Status | Anzahl |
|---|---:|
| eingearbeitet (beantwortet; Antwort steht in Regeln/Code oder lautet „belassen“) | 64 |
| beantwortet, nicht eingearbeitet | 6 |
| offen mit Teilantwort | 4 |
| offen | 85 |
| **gesamt** | **159** |

Offene Fragen nach Zuständigkeit: Verkehrsplaner*in 46, GIS 16, Team 15, Methodik 6, sonstige 2. Die
**Methodik-Fragen (6) sind reine Formalia** (Einheiten, `status`-Freitext, Feldnamen in guide.md; Gruppe B der Sortierung).
Sie warten seit dem 2026-11-07 nur auf die Freigabe.

**Wirkungsbereich:** Die Tabelle nennt je Frage die km bzw. Knoten, auf denen eine genannte Regel ausgewertet wird
(Obergrenze der Wirkung, nicht die Änderung bei einer Antwort). Fragen zu Annahmen von Merkmalen und Conflation betreffen
das ganze Netz (4 387 km). Die konkrete Wirkung steht, wo bekannt, im Fragetext selbst. Die wichtigsten:

| Zeile | Frage (kurz) | Regel | bekannte Wirkung |
|---:|---|---|---|
| 70, 201 | HVS als GOW30 trotz hoher Belastung | C-G30-01 | 358 km zwischen GOW30 und GOW50 (Abschnitt 3) |
| 124 | `in_hvs` aus `conn_score` nehmen | C-GOW-01 | +430 km GOW (Probelauf 2026-11-07) |
| 123 | Kalibrierung `conn_gow` 0,6 | C-GOW-01 | −20 % → +39,8 km GOW |
| 184 | DTV fehlt auf 99,9 % der ETW30; Fahrradstraße gilt ohne DTV als erfüllt | C-FAC-02/03 | 3 452 km mit `dtv_unknown` |
| 210 | keine Knotenzeile für Radwege über ETW30 | J-08/J-09 | heute 10 Knoten `no_rule` (Stand Prompt 20: 412) |
| 211 | J-03 Kreisverkehr ohne DTV-Grenze | J-03 | 232 Knoten über `roundabout_max_dtv` |
| 212 | ETW_ERF ohne eigene Knotenzeile | N6, J-* | rund 900 Netzknoten weichen ab |
| 214 | Ist-LSA-Radius 30 m trifft Nebenknoten | N6 | 1 159 Gehwegüberfahrten mit Ist „LSA“ |
| 13 | `crossing_demand` nicht definiert | C-G30-01 | Auslöser fehlt überall (Default `not_assessed`) |
| 51 | keine Ortsgrenze, ländliche Stadtteile unbewertet | C-RUR-01 | 17 Stadtteile ohne Kategorie |

### 2.1 Beantwortet, aber nicht eingearbeitet – nötige Änderung

| Zeile | Antwort | nötige Änderung | wohin |
|---:|---|---|---|
| 43 | Betweenness gerichtet (oneway/access) – später | gerichteter Kfz-Graph in s02/s04, betweenness neu | Prompt 22 Stufe B |
| 80 | N4-Schleichverkehr über Umlegung statt Schwelle – später | N4 aus Umlegung ableiten (Mehrbelastung ETW) | Prompt 22 Stufe B; Prototyp in 2a (Szenario D) |
| 129 | Annahmen früherer Stufen variieren – später | Sensitivität S-CONF-01 buffer_m, S-XS-05 quantile | Prompt 22 |
| 182 | Soll für Halte und Unfallwirkung – später | P-DIR-02/P-SAF-04 Soll ≠ Ist | Prompt 23 |
| 202 | ETW30-Mischfahrbahn 4,75 m übernommen, „Wert am Original prüfen“ | Quelle RASt 06 Bild 17 bestätigen, dann `status: reviewed` | Verkehrsplaner*in |
| 217 | Sensitivität Nachfrage/Netzentwurf – später | Läufe c02/c03 mit variierten Annahmen | Prompt 22 |

Dazu Gruppe B der Sortierung (5 Formalia, Zeilen 16, 18, 19, 21, 74): beantwortet im Sinne „Claude Code erledigt, sobald
freigegeben“, aber nicht freigegeben. Kein Wert ändert sich.

### 2.2 Offen mit Teilantwort

| Zeile | Stand | was fehlt |
|---:|---|---|
| 57 | GTFS-Feed endet 2026-12-13, Nachfolger noch nicht veröffentlicht | Mitte Dezember neu abrufen, `make rerun FROM=features` |
| 70, 201 | Obergrenze eingeführt (0.14.0) und zurückgenommen (0.15.0), „Regel später verbessern“ | Entscheidung über den Umgang mit Verkehrsmengen → 2a |
| 124 | Probelauf ohne `in_hvs` im `conn_score` gerechnet (+430 km GOW) | Entscheidung, zurückgestellt bis zum Fachplaner-Termin |

## 3 Der Wechsel GOW30 → GOW50

`gow_switch.py` (`data/scenarios/review_static/gow_switch*.{json,csv}`). Vergleich der gesicherten Variante
(`data/variants/2026-11-07_gow50-kompromiss`, rules.yaml 0.14.0) mit dem heutigen Export (rules.yaml 0.16.0); beide
33 712 Abschnitte, gleiche segment_id.

**Wann:** Commit 8603877 („Entscheidungen Stapel 3 und 4: Tempo-30-Obergrenze …“, rules.yaml 0.14.0) führte die Obergrenze
ein; Commit 720708c (rules.yaml 0.15.0) nahm sie zurück; gesichert als Tag `variante-gow50-kompromiss` (Commit be9629a).

**Auslösende Regeln:** C-G30-01 erhielt die Zusatzbedingung `(not in_hvs or dtv_official <= gow30_max_dtv)` mit
`gow30_max_dtv = 10 000 Kfz/24h` (CROW-GOW30-Profil „wide“); die neue Regel C-G50-02 setzte dann GOW50 mit Hinweis
„Tempo-30-Abschnitt vor Ort prüfen“. C-G30-02 (kein Platz für baulichen Radweg → GOW30) stand davor und blieb wirksam.

**Umfang** (Abschnitte, deren rule_path in 0.14.0 C-G50-02 enthält):

| | Abschnitte | km |
|---|---:|---:|
| über C-G50-02 GOW50 (0.14.0) | 3 204 | 357,7 |
| davon heute GOW30 | – | 355,0 |
| davon heute ETW30 (Stapel 5: Nebenfahrbahnen nicht mehr `in_hvs`) | – | 2,7 |
| … und in beiden Ständen getrennt einer Kategorie zugeordnet: GOW50 (0.14.0) → GOW30 (heute) | 2 853 | 323,8 |

Hauptverkehrsstraßen (`in_hvs`) je Kategorie:

| | 0.14.0 | heute (0.16.0) |
|---|---:|---:|
| GOW50 | 559 km | 200 km |
| GOW30 | 99 km | 467 km |
| SW | 22 km | 22 km |
| ETW30/ETW_ERF | 9 km | 1 km |

Weitere 53 km unterscheiden sich wegen Stapel 5 (rules.yaml 0.16.0: HVS über gleichen Straßennamen, Breiten vom
Nachbarn), davon 44 km GOW50 → GOW30. Sie gehören nicht zum Wechsel.

**Je Bezirk** (GOW50 in 0.14.0 → GOW30 heute):

| Bezirk | Abschnitte | km | DTV-Median |
|---|---:|---:|---:|
| Wandsbek | 650 | 80,4 | 23 000 |
| Hamburg-Nord | 664 | 68,0 | 30 000 |
| Hamburg-Mitte | 585 | 67,3 | 24 000 |
| Altona | 348 | 42,5 | 24 000 |
| Eimsbüttel | 379 | 38,3 | 28 000 |
| Harburg | 144 | 18,5 | 29 000 |
| Bergedorf | 83 | 8,8 | 19 000 |

**Typische Straßen** (längste Strecken; Link je auf einen Beispielabschnitt):

| Straße | Bezirk | km | DTV max | Beispiel |
|---|---|---:|---:|---|
| Cuxhavener Straße | Harburg | 6,1 | 33 000 | [`seg_00e1a2b845f45d2d`](https://hamburgmobility.de/#karte?seg=seg_00e1a2b845f45d2d) · [OSM](https://www.openstreetmap.org/?mlat=53.471981&mlon=9.875832#map=18/53.471981/9.875832) |
| Poppenbütteler Weg | Wandsbek | 5,7 | 32 000 | [`seg_00e096069010de5c`](https://hamburgmobility.de/#karte?seg=seg_00e096069010de5c) · [OSM](https://www.openstreetmap.org/?mlat=53.657370&mlon=10.085231#map=18/53.657370/10.085231) |
| Friedrich-Ebert-Damm | Wandsbek | 5,7 | 28 000 | [`seg_0cda7fe5a634615f`](https://hamburgmobility.de/#karte?seg=seg_0cda7fe5a634615f) · [OSM](https://www.openstreetmap.org/?mlat=53.589848&mlon=10.102780#map=18/53.589848/10.102780) |
| Kieler Straße | Eimsbüttel | 5,3 | 59 000 | [`seg_029db6bb5148f2fd`](https://hamburgmobility.de/#karte?seg=seg_029db6bb5148f2fd) · [OSM](https://www.openstreetmap.org/?mlat=53.593837&mlon=9.926232#map=18/53.593837/9.926232) |
| Sievekingsallee | Hamburg-Mitte | 5,1 | 51 000 | [`seg_08c1f8cd537f0db5`](https://hamburgmobility.de/#karte?seg=seg_08c1f8cd537f0db5) · [OSM](https://www.openstreetmap.org/?mlat=53.560904&mlon=10.052695#map=18/53.560904/10.052695) |
| Osdorfer Landstraße | Altona | 4,9 | 37 000 | [`seg_002b83c73be9064a`](https://hamburgmobility.de/#karte?seg=seg_002b83c73be9064a) · [OSM](https://www.openstreetmap.org/?mlat=53.572031&mlon=9.854735#map=18/53.572031/9.854735) |
| Steilshooper Allee | Wandsbek | 4,7 | 42 000 | [`seg_0548976ba60f5599`](https://hamburgmobility.de/#karte?seg=seg_0548976ba60f5599) · [OSM](https://www.openstreetmap.org/?mlat=53.608464&mlon=10.055805#map=18/53.608464/10.055805) |
| Eiffestraße | Hamburg-Mitte | 4,0 | 44 000 | [`seg_00afdcce26f4b43d`](https://hamburgmobility.de/#karte?seg=seg_00afdcce26f4b43d) · [OSM](https://www.openstreetmap.org/?mlat=53.550615&mlon=10.062167#map=18/53.550615/10.062167) |

Volle Liste (40 Straßen) in `data/scenarios/review_static/gow_switch_streets.csv`. Luftbild-Links erzeugt
`analysis/review_2026_11/common.seg_links`.

**Auslöser von C-G30-01 auf diesen 2 853 Abschnitten:** Schule/Kita ≤ 150 m bei 2 090, Publikumsnutzung ≥ 0,4 bei 1 766
(Mehrfachnennung). DTV: Minimum 11 000, Median 25 000, 75 %-Quantil 33 000, Maximum 110 000 Kfz/Tag.

**Betroffene Radrouten** (heutiges Soll-Radnetz auf diesen Abschnitten): HAUPT 162,2 km, RSV 12,4 km, BASIS 49,6 km,
ERSCHL 93,2 km, kein Radnetz 6,4 km. Querschnitt heute (als GOW30): passt 211 km, passt nach Abbau 89 km, passt nicht
20 km, ohne Bewertung 4 km.

**Betroffene Knoten:** 2 265 Knotenpunkte haben einen Arm auf einem dieser Abschnitte; Kategoriepaare heute GOW30+ETW30
1 284, GOW30+GOW30 643, GOW50+GOW30 291; Soll-Typ heute Gehwegüberfahrt 1 293, geschützte LSA 451, Plateau eingefärbt 258,
einstreifiger Kreisverkehr 139, Turbokreisverkehr 95.

**Mechanismus.** In 0.14.0 entschied auf Hauptverkehrsstraßen die heutige Verkehrsmenge (Ist-DTV 2019) zwischen GOW30 und
GOW50: Wo das Umfeld für Tempo 30 sprach, aber mehr als 10 000 Kfz/Tag gezählt wurden, wurde die Straße GOW50. Damit
bestimmte die Nutzung die Soll-Funktion. Nach Duurzaam Veilig ist die Reihenfolge umgekehrt (Funktion → Gestaltung →
Nutzung), und die Nutzung ist der Prüfstein der Diskrepanz. Heute (0.15.0 ff.) entscheidet das Umfeld; die hohe Belastung
erscheint nur noch als Flag `gow30_dtv_above_profile` am Soll-Querschnitt (3 404 Abschnitte, 363 km).

**Wo die Nutzung heute noch in die Funktion eingeht** (`analysis/review_2026_11`, Nachrechnung von `conn_score`):

| Kanal | Wirkung |
|---|---|
| `in_hvs` aus der DTV-Zählkarte HVS 2019 (S-CONF-04, weil HH-SIB nicht erreichbar ist) | 691 von 816 km GOW (85 %) sind GOW, weil sie in der Zählkarte stehen. Die Zählkarte bildet das amtliche HVS-Netz ab, also eine Funktionszuweisung, die nur über einen Zähldatensatz kommt. Strecken ohne Zählung fallen heraus (offene Frage Zeile 126). |
| `dtv_norm` im `conn_score` (Gewicht 0,20) | ohne dieses Gewicht verlieren 11,4 km die GOW-Eigenschaft, 0,1 km kommen hinzu; DTV liegt nur auf 763 km vor |
| Netzkohärenz N4, Machbarkeit, Diskrepanz D-USE-01 | Nutzung als Prüfung, nicht als Kategorie (DV-konform) |

## 4 Rückmeldungen

Es gibt keine externen Rückmeldungen, die sich Fehlertypen zuordnen ließen:

| Quelle | Stand 2026-11-07 |
|---|---|
| GitHub-Issues prstolpe/hamburgmobility | 0 (auch geschlossene) |
| GitHub-Pull-Requests | 3, alle Impressum/Ausweitung, keine fachlichen |
| overrides/overrides.csv | 7 Einträge, alle approved, ein Fall: Reeperbahn/Sengelmannstraße (C-ERF-01 vor C-GOW-01) |
| cycle_network-, junction-, lane_overrides.csv | je 0 Einträge |
| reports/classification_sample.csv (150), conflation_sample.csv (50), cycle_principles_review.csv (20), junctions_review.csv (270), validation_cycling_review.csv (30) | Prüfspalten leer: 0 von 520 Zeilen |
| reports/transect_measurements.csv | fehlt |

Die einzigen fachlichen Rückmeldungen sind die Entscheidungen von prstolpe in open_questions.md (Stapel 1–5) und
variants.md. Ordnet man die dort korrigierten Befunde Fehlertypen zu:

| Fehlertyp | Beispiele (Zeile in open_questions.md) |
|---|---|
| Abgleich amtlicher Daten (Conflation) | Nebenfahrbahnen als HVS (113), HVS-Lücken Kieler Straße/Hallerstraße (34, 126), verkehrsberuhigte Bereiche am Puffer (136) |
| fehlende Merkmale → Default | ohne Gebäude kein shop_frontage_share (69), fehlende Breite (61), `crossing_demand` (13) |
| Regel zu grob | DTV-Obergrenze (70), J-03 ohne DTV (211), Maschenweiten (168) |
| Datenlücke | Ortsgrenze (51), DTV Nebenstraßen (184), Ist-Knotentyp (85, 214) |

**Folgerung für Phase 2:** Eine Fehlerrate der Klassifikation lässt sich mit vorhandenen Daten nicht angeben. Phase 2
nutzt deshalb (a) Abgleich mit amtlichen Ebenen (HVS-Netz, Ist-Tempo), (b) Plausibilitätsregeln mit Beispielen und
(c) eine eigene Stichprobe von 50 Knoten (2c), deren Bewertung als „Review, nicht Ortsprüfung“ gekennzeichnet ist.
