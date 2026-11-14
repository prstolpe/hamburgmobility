# Redesign 2026-11 · A5 Regeldateien in verständlicher Sprache (ohne Bedeutungsänderung)

Vorschlag. Nichts davon ist in `config/` übernommen. Entscheidung: `decisions.md`, Zeile E5. Umsetzung: Teil B,
Paket 4 (neue Patch-Version, CHANGELOG, Hash-Vergleich).

## Befund (aus A1.4)

- Nur 23 von 196 Regeln sind für Laien verständlich beschrieben. 104 sind es teilweise, 69 nicht. 14 Regeln haben gar
  keinen Text.
- In 124 Regeltexten steht Code: Variablennamen wie `conn_score` und `width_p10_m`, Operatoren wie `>=`, Formeln.
- 68 von 196 Regeln mischen in `description`/`note` drei Dinge: die Regel selbst, die Begründung und die Geschichte der
  Regel („seit 0.18.0 (F07, Entscheidung Q2 b 2026-11-08) …“).
- Die Bezeichnung einer Regel ist nur ihre ID. Schwellen haben englische Schlüssel (`conn_gow`, `access_radius`).
- Kategorien sind doppelt benannt: `label_de` in `rules.yaml` und Klartext in `plain_language.yaml`. Die Methodenseite
  erklärt die Kaskade ein drittes Mal, von Hand in `web/src/pages.js`.

## Vorschlag: drei neue Felder, sonst nichts ändern

| Feld | Inhalt | Länge | Wo es erscheint |
|---|---|---|---|
| `label_plain` | Name der Regel, Kategorie oder Schwelle in Einfacher Sprache | 2–8 Wörter | Ebene 2/3 der Seite, Regelreferenz (Überschrift), Steckbrief Ebene 3 neben der ID |
| `explain_plain` | was die Regel tut | 1 Satz, unter 25 Wörter | Regelreferenz, Tooltip der ID, „Zweck“ im Regelinventar |
| `why` | warum es die Regel gibt | 1–2 Sätze | Regelreferenz (Ebene 2 des Kapitels) |

Regeln dafür:

- Bestehende Schlüssel, IDs, Werte, Bedingungen und Quellen bleiben unverändert.
- Die Felder sind reiner Text. Kein Code liest sie für eine Entscheidung.
- Sprache nach `04_language.md`, Begriffe aus `glossary.yaml`.
- Die Felder gelten für jede Regel mit `id`, für jede Kategorie (`categories.*`) und für jede Schwelle (Eintrag mit
  `value` unter `thresholds`).
- `source`/`source_type` bleiben bei den Zahlen. Die neuen Felder brauchen keine Quelle, weil sie nichts festlegen.

Für alle 196 Regeln, 7 Kategorien und 58 Schwellen liegen `label_plain` und `explain_plain` als Entwurf vor:
[`analysis/redesign/rule_plain.yaml`](../../analysis/redesign/rule_plain.yaml). Sie füllen auch die Spalte „Zweck“
im Regelinventar (`01_rules_inventory.csv`). `why` ist für die 10 Beispielregeln unten geschrieben, für die übrigen in
Teil B.

**Schema:**

- `config/schema/rules_model.py`: Alle Modelle in `rules.yaml` verbieten unbekannte Felder (`extra="forbid"` in
  `_Strict`). Die drei Felder müssen dort als optionale Texte eingetragen werden. Für den Probelauf sind sie in `_Strict`
  eingetragen. Für die Umsetzung ist ein eigener Baustein `PlainText` sauberer, den nur Regel-, Kategorie- und
  Schwellenmodelle erben.
- `cycling_model.py` und `design_model.py` lassen Zusatzfelder in den Regeln schon zu.
- `config/schema/provenance.py` und `analysis/review_2026_11/rules_register.py`: Die neuen Schlüssel kommen in
  `META_KEYS` (Text, keine Zahl).

## Diff-Skizze für 10 Beispielregeln

Ausgewählt sind je zwei Kaskadenregeln, eine Harmonisierungsregel, eine Netzprüfung, eine Diskrepanzregel, eine
Radwegregel, eine Führungsform, eine Fahrstreifenregel und eine Knotenregel. Im Patch stehen die Felder direkt nach der
`id`. Hier sind sie zur besseren Lesbarkeit unten angefügt.

<!-- table:rule_diff_sketch -->
**C-GOW-01** (`config/rules.yaml`)

```diff
    - id: C-GOW-01
      description: "Verbindungsfunktion hoch → Gebiedsontsluitingsweg"
      if: "conn_score >= thresholds.conn_gow or in_hvs"
      then: "GOW (weiter mit C-G30-*)"
+ label_plain: "Verbindet die Straße Stadtteile?"
+ explain_plain: "Eine Straße wird Hauptstraße, wenn sie auf der Liste der Hauptverkehrsstraßen steht oder ihr Verbindungswert hoch ist."
+ why: "Nach Duurzaam Veilig hat jede Straße genau eine Aufgabe. Straßen, die Stadtteile verbinden, brauchen eine andere Gestaltung als Straßen im Wohngebiet."
```

**C-G30-01** (`config/rules.yaml`)

```diff
    - id: C-G30-01
      description: "GOW30-Auslöser a: Umfeld spricht für 30 (Schule/Kita am Abschnitt, Leben, Querbarkeit)"
      applies_to: GOW
      if: "school_or_kita_access_m <= thresholds.access_radius or shop_frontage_share >= thresholds.frontage or crossing_demand == high"
      then: GOW30
+ label_plain: "Tempo 30 wegen Schule oder Läden"
+ explain_plain: "Eine Hauptstraße bekommt Tempo 30, wenn eine Schule oder Kita direkt an ihr liegt oder viele Läden an ihr sind."
+ why: "Wo viele Menschen zu Fuß queren, verhindert Tempo 30 schwere Unfälle. Das niederländische Regelwerk nennt das Umfeld als ersten Grund für Tempo 30 auf Hauptstraßen."
```

**C-G30-02** (`config/rules.yaml`)

```diff
    - id: C-G30-02
      description: "GOW30-Auslöser b: 50 nicht sicher gestaltbar (kein ausreichender getrennter Radweg möglich)"
      applies_to: GOW
      if: "(not bus_route and width_p10_m < required_width.GOW50) or (bus_route and width_p10_m < required_width.GOW50_bus)"
      then: GOW30
      note: >-
  …
+ label_plain: "Tempo 30, wenn Platz für den Radweg fehlt"
+ explain_plain: "Eine Hauptstraße bekommt Tempo 30, wenn kein Platz für einen eigenen Radweg ist."
+ why: "Bei Tempo 50 braucht das Rad einen getrennten Radweg. Passt er nicht in die Straße, ist Tempo 50 nicht sicher zu gestalten."
```

**H-STR-01** (`config/rules.yaml`)

```diff
      - id: H-STR-01
        description: >-
          Kurze Läufe (unter min_run_m aus N2) auf einem Straßenzug angleichen, wiederholt bis nichts mehr wechselt:
          (1) ETW30 zwischen zwei GOW-Läufen -> GOW (niedrigeres Soll-Tempo der Nachbarn); (2) GOW zwischen zwei
          ETW30-Läufen -> ETW30; (3) GOW50 zwischen zwei GOW30-Läufen oder am Zugende neben GOW30 -> GOW30;
          (4) GOW30 zwischen GOW50 (oder am Zugende neben GOW50) bleibt und wird in die angrenzenden GOW50-Abschnitte
  …
+ label_plain: "Kurze Stücke angleichen"
+ explain_plain: "Kurze Stücke bekommen die Aufgabe der Straße davor und dahinter; trifft 50 auf 30, gewinnt 30."
+ why: "Eine Straße soll auf langer Strecke gleich aussehen und gleich schnell sein. Ständige Wechsel verwirren und machen die Regel unglaubwürdig."
```

**N4** (`config/rules.yaml`)

```diff
    - id: N4
      rule: "Kürzester Weg zwischen GOW-Knoten nutzt > max_etw_m ETW -> Schleichverkehrsflag"
      max_etw_m: 300
      source: SWOV_FS_2023
      source_type: assumption
      status: draft
  …
+ label_plain: "Schleichverkehr möglich"
+ explain_plain: "Hinweis, wenn der kürzeste Weg zwischen Hauptstraßen lange durch Wohnstraßen führt."
+ why: "Ein Wohngebiet ist nur ruhig, wenn Abkürzen sich nicht lohnt. Der Hinweis zeigt, wo ein Filter oder eine andere Aufgabe nötig sein könnte."
```

**D-SPD-01** (`config/rules.yaml`)

```diff
      id: D-SPD-01
      rule: "excess_kmh = speed_ist_kmh - categories[cat_final].speed_kmh; Stärke = höchste Stufe mit excess_kmh >= min_excess_kmh"
+ label_plain: "Tempo zu hoch?"
+ explain_plain: "Abweichung, wenn heute schneller gefahren werden darf als im Ziel."
+ why: "Das Tempo ist der wichtigste Hebel für die Sicherheit. Eine Straße, die schneller erlaubt als ihre Aufgabe, ist ein Hinweis auf Handlungsbedarf."
```

**S-01** (`config/cycling_rules.yaml`)

```diff
      - {id: S-01, rule: 'Kein Radfahr- oder Schutzstreifen an GOW50', source: CROW_GOW30_2023, source_type: swov_crow, status: draft}
+ label_plain: 'Kein Radstreifen bei Tempo 50'
+ explain_plain: 'An Hauptstraßen mit Tempo 50 braucht das Rad einen eigenen Radweg, keinen Streifen.'
+ why: 'Bei Tempo 50 und vielen Lastwagen ist ein Streifen auf der Fahrbahn nicht sicher genug. Das niederländische Regelwerk trennt hier immer baulich.'
```

**C-FAC-02** (`config/cycling_rules.yaml`)

```diff
      - id: C-FAC-02
        description: 'Fahrradstraße nur, wenn Kfz/Tag <= cycle_street.max_motor_vehicles_day und Radverkehr in der Spitzenstunde (cyc_peak_h, beide Richtungen)…
        dtv_missing_counts_as_met: true
+ label_plain: "Wann Fahrradstraße?"
+ explain_plain: "Fahrradstraße nur, wenn wenige Autos fahren und mehr Räder als Autos."
+ why: "Eine Fahrradstraße funktioniert nur, wenn das Rad dort wirklich die Mehrheit ist. Sonst bleibt es eine Wohnstraße mit Schild."
```

**L-06** (`config/design_rules.yaml`)

```diff
      - id: L-06
        status: draft
        rule: 'Kein Fahrstreifenzuwachs gegenüber Ist ohne fachliche Freigabe (overrides/lane_overrides.csv seit 0.6.0; ein freigegebener Eintrag ersetzt L-02 …
        source_type: assumption
+ label_plain: "Nicht mehr Fahrstreifen als heute"
+ explain_plain: "Der Entwurf plant nie mehr Fahrstreifen als heute, außer nach fachlicher Freigabe."
+ why: "Mehr Fahrstreifen ziehen mehr Autoverkehr an. Ein Zuwachs ist eine politische Entscheidung, keine Folge einer Rechenregel."
```

**J-05** (`config/design_rules.yaml`)

```diff
        - {id: J-05, legs: 'GOW30+ETW30', then: continuous_footway_exit, fallback: priority_raised, source: CROW_GOW30_2023, status: draft}
+ label_plain: 'Hauptstraße 30 trifft Wohnstraße'
+ explain_plain: 'Durchgehender Gehweg über die Einmündung.'
+ why: 'Wer aus der Wohnstraße kommt, fährt langsam über den Gehweg. So sieht jeder: Hier beginnt ein ruhiges Gebiet, Fußgänger haben Vorrang.'
```
<!-- /table:rule_diff_sketch -->

## Klarere Wörter für bestehende Felder

Die technischen Felder bleiben für Fachleute. Sie können aber lesbarer werden, ohne ihre Bedeutung zu ändern:

1. **Geschichte heraus aus der Beschreibung.** „Seit 0.18.0 (F07, Entscheidung Q2 b …)“ gehört in `CHANGELOG.md` oder
   ein Feld `history:`. Betroffen sind 68 Regeln.
2. **Ein Satz Regel, dann Einzelheiten.** `description` beginnt mit dem, was die Regel tut. Ausnahmen und Datenhinweise
   kommen in `note`.
3. **Variablennamen in Klammern hinter ein Wort**, nicht als Satzteil: „Breite an der engsten Stelle (`width_p10_m`)“.

Beispiele, sinngleich umformuliert:

| Regel | heute | Vorschlag |
|---|---|---|
| C-MISS-01 `description` | „Fehlende Werte: dreiwertige Logik (Kleene). Ein Vergleich mit einem fehlenden Wert ist unbekannt; „oder“ ist wahr, sobald ein Teil wahr ist, „und“ ist falsch, sobald ein Teil falsch ist. Eine Regel greift nur, wenn ihre Bedingung sicher wahr ist. Hängt das Ergebnis an einem unbekannten Wert, ist confidence niedrig (C-CONF-01).“ | „Eine Regel greift nur, wenn ihre Bedingung sicher wahr ist. Fehlt ein Wert, ist jeder Vergleich mit ihm unbekannt (dreiwertige Logik nach Kleene): „oder“ ist wahr, sobald ein Teil wahr ist; „und“ ist falsch, sobald ein Teil falsch ist. Hängt das Ergebnis an einem unbekannten Wert, ist die Datenlage niedrig (C-CONF-01).“ |
| C-G30-02 `note` | „Seit 0.18.0 (F06): nur über den Raum. Ein vorhandener Radweg zählt nicht (CROW-Auslöser b fragt, ob ein ausreichender Radweg realisierbar ist). bus_route = Busse je Spitzenstunde … Flag existing_track_below_floor (c05), …“ | „Es zählt nur der Platz, nicht ein vorhandener Radweg: Der CROW-Auslöser b fragt, ob ein ausreichender Radweg *möglich* ist. Busstrecke (`bus_route`) heißt: mindestens S-FEAT-08 `bus_route_min_peak_h_dir` Busse je Spitzenstunde und Richtung (PRF-02). Ist ein heutiger Radweg schmaler als die Untergrenze C-FAC-04, setzt c05 das Flag `existing_track_below_floor`.“ *(Geschichte „seit 0.18.0 (F06)“ → `history`)* |
| S-NET-04 `description` | „Benannte Zufahrten zusätzlich ins Netz: highway=service ohne service-Untertyp oder mit service=alley und highway=track mit Kfz-Zugang (erster bekannter Wert aus motor_access_keys in motor_access_values oder ohne Angabe); jeweils nur mit name. …“ | „Benannte Zufahrten kommen zusätzlich ins Netz. Das sind `highway=service` ohne Untertyp oder mit `service=alley` und `highway=track` mit Kfz-Zugang, jeweils nur mit Namen. Kfz-Zugang heißt: Der erste bekannte Wert aus `motor_access_keys` steht in `motor_access_values`, oder es gibt keinen Wert. Fußwege, `path`, Parkplatzgassen und Grundstückszufahrten bleiben draußen.“ |
| C-FAC-01 `description` | „Soll-Führung = separation_matrix[cat_final][cycle_cat_final] (außerorts separation_matrix.rural); vorher die Zelle high_volume der Zeile, wenn dtv_official > deren dtv_above (S-05, GOW30). Zelle mit preferred/fallback: preferred; …“ | „Die Soll-Führung steht in der Trennungsmatrix: Zeile = Kategorie der Straße, Spalte = Radnetzstufe (außerorts die Matrix `rural`). Liegt der DTV über `dtv_above` der Zeile, gilt vorher die Zelle `high_volume` (S-05, nur GOW30). Hat die Zelle `preferred` und `fallback`, gilt `preferred`. `fallback` gilt nur, wenn der Platz nicht reicht (`space_fits_preferred = false`, Prompt 19). Ist der Platz noch nicht geprüft, bleibt `preferred` mit Flag `fallback_check_p19`.“ |
| J-M-04 `rule` | „Kategoriepaar wie N6 (rules.yaml): höchste Straßenkategorie (bis zu zwei ihrer Arme = durchgehender Zug) und höchste der übrigen Arme; Rang nach N6.category_rank. …“ | „Das Paar besteht aus der höchsten Straßenkategorie am Knoten und der höchsten Kategorie der übrigen Arme. Bis zu zwei Arme der höchsten Kategorie zählen als ein durchgehender Zug. Rang nach `category_rank`. Bleibt neben dem Zug nur ein eigenständiger Radweg, ist das Paar (Zug, `cycle_path`).“ |

## Texte nur an einer Stelle

Damit Webseite, Steckbrief und Regelreferenz dieselben Wörter benutzen:

1. **Export:** `pipeline/s09_export.py` schreibt die Regelreferenz nach `meta.json` (oder als eigene Datei
   `rules.json`). Je Regel stehen dort:
   - `id`, `label_plain`, `explain_plain`, `why`
   - `file`, `status`, `source_type`, `source`
   - die Schwellen mit `label_plain`, Wert, Einheit und Quelle
   - aus dem Lauf: wie oft die Regel greift und entscheidet (wie in `01_rules_inventory.csv`)
2. **Methode, Kapitel und Regelreferenz:** Die Seite erzeugt die Referenz aus diesen Daten. Den Kaskadentext liest sie
   aus `label_plain`/`explain_plain` der C-Regeln, statt ihn in `pages.js` nachzuschreiben.
3. **Kategorien:** `label_plain`/`explain_plain` in `rules.yaml` ersetzen `categories` in `plain_language.yaml`.
   `label_de` bleibt als Fachname auf Ebene 3. Damit fällt eine der zwei Quellen weg.
4. **Begründungsbausteine im Steckbrief** (`plain_language.yaml`, `rules.<ID>.passed/failed`) bleiben, wo sie sind: Es
   sind Satzbausteine mit Werten aus `rule_trace`, kein Regeltext. Sie folgen aber dem Glossar. Die Trennung „trifft zu /
   trifft nicht zu“ kommt aus `passed`.
5. **Prüfung:** Ein Test vergleicht, dass jede Regel mit `id` `label_plain` und `explain_plain` hat und dass diese ohne
   Kürzel aus der Kürzelliste auskommen (wie `language_scores.py`).

## Nachweis: keine Änderung der Bedeutung

**Vorgehen** (`analysis/redesign/make_lang_patch.py`, `analysis/redesign/run_worktree.sh`):

1. Die drei Felder werden in Kopien der Regeldateien eingefügt, als Textänderung bei unveränderter Formatierung.
   - `rules.yaml`: 65 Regeln, 7 Kategorien, 52 Schwellen
   - `cycling_rules.yaml`: 79 Regeln
   - `design_rules.yaml`: 52 Regeln, 6 Schwellen
   - Schema und `META_KEYS` wie oben
2. **Prüfung vor dem Lauf:** Jede geänderte YAML-Datei lädt ohne die drei neuen Schlüssel zu genau demselben
   Python-Objekt wie das Original (`assert`). Bestanden.
3. **Tests:** `pytest` im Worktree mit Patch: 1 543 bestanden, 2 xfailed. Das ist dasselbe Ergebnis wie ohne Patch.
4. **Volle Neurechnung im Worktree ab der ersten Stufe** (`make rerun FROM=network`). Dann Vergleich aller Dateien in
   `data/interim` mit dem Stand ohne Patch (`analysis/review_2026_11/compare_runs.py`: Datei-Hash, Schlüssel,
   Reihenfolge, jede Spalte). Verglichen wird mit dem Basislauf ohne Patch (`data/scenarios/redesign/base`), der
   `data/interim` hashgleich wiedergibt (A1).

<!-- table:lang_proof -->
| Datei (data/interim) | Zeilen | Datei-Hash gleich | Spalten mit Unterschied (Zeilen) |
|---|---|---|---|
| classified.parquet | 36526 | ja | – |
| coherence.parquet | 36526 | ja | – |
| coherence_areas.parquet | 3195 | ja | – |
| coherence_nodes.parquet | 5061 | ja | – |
| cross_section_soll.parquet | 36526 | ja | – |
| crosssection.parquet | 36526 | ja | – |
| cycle_edges.parquet | 65973 | ja | – |
| cycle_facility.parquet | 36526 | ja | – |
| cycle_graph.parquet | 65973 | ja | – |
| cycle_mesh_gaps.parquet | 441 | ja | – |
| cycle_network.parquet | 65973 | ja | – |
| cycle_principles.parquet | 33913 | ja | – |
| cycle_routes.parquet | 4936 | ja | – |
| discrepancy.parquet | 36526 | ja | – |
| features.parquet | 36526 | ja | – |
| final.parquet | 36526 | ja | – |
| harmonised.parquet | 36526 | ja | – |
| ist_facility.parquet | 36526 | ja | – |
| junctions.parquet | 16244 | ja | – |
| segments.parquet | 36526 | ja | – |
| segments_conflated.parquet | 36526 | ja | – |
| transects.parquet | 219291 | ja | – |
| validation.parquet | 34702 | ja | – |
| validation_cycling.parquet | 52770 | ja | – |
<!-- /table:lang_proof -->

**Ergebnis:** Alle 24 Dateien in `data/interim` sind hashgleich mit dem Lauf ohne Patch. Es gibt keine einzige
abweichende Spalte, auch keine Rundungsabweichung. In `data/out` unterscheiden sich nur diese Dateien:

- die kopierten Regeldateien `downloads/rules.yaml`, `cycling_rules.yaml` und `design_rules.yaml`, wie gewollt, weil sie
  die neuen Felder enthalten
- `meta.json`, das den Zeitpunkt des Exports (`generated`) trägt und deshalb in jedem Lauf anders ist

Alle übrigen Dateien des Exports (Steckbriefe, Tabellen, Downloads außer den Regeldateien) sind hashgleich. Die Felder
ändern also keine Klassifikation, keine Radanlage, keinen Querschnitt und keinen Knotentyp.

Laufzeit: 25 Minuten (`data/scenarios/redesign/lang/run.log`).
