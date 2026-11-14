# Redesign 2026-11 · Vorschläge (Teil A)

## Auf einer Seite

**Ausgangslage** (`01_inventory.md`):

- **Steckbriefe:** Ein Straßen-Steckbrief hat 13–15 gleichrangige Abschnitte mit 380–560 Wörtern. Er ist 4–5
  Bildschirmhöhen lang, der längste Abschnitt sind die Datenquellen.
- **Karte:** 13 Kartenebenen als Radioknöpfe. Am Smartphone ist bei keiner die Legende ohne Scrollen sichtbar.
- **Farben:** Rot hat 10 Bedeutungen, Grün auch, darunter „passt“ und „Spielstraße“.
- **Kürzel:** Kategorie-Kürzel und Regel-IDs stehen überall. Die Antwort auf „Wo ist der Handlungsbedarf?“ ist eine
  Kürzeltabelle ohne Radverkehr und Kreuzungen.
- **Lesbarkeit:** Die Steckbriefe liegen bei Wiener Sachtextformel 11–14, also schwer.
- **Regeldateien:** Nur 23 von 196 Regeln sind für Laien verständlich beschrieben.

**Vorschlag in fünf Sätzen:**

1. Jede Seite und jeder Steckbrief bekommt drei Ebenen: auf einen Blick, Erklärung, Details und Quellen.
2. Aus 13 Ebenen werden 5 Themen mit „Ziel / heute“. Die Legende steht in Worten neben der Karte.
3. Ein strenges Schweizer Design-System: Inter, 12/8/4-Spalten-Raster, eine Bedeutung je Farbe, keine Ornamente.
4. Alle Texte in Einfacher Sprache mit einem verbindlichen Glossar. In den Beispielen fällt die Wiener Sachtextformel
   von 9,2 auf 3,7.
5. Die Regeldateien bekommen Klartext-Felder (nachweislich ohne Wirkung auf die Ergebnisse). 17 Regeln können
   zusammengelegt, vereinfacht oder gestrichen werden, fast alle ohne Wirkung auf Ergebnisse.

**Was du ansehen solltest:**

1. Die zwei Prototypen (`prototypes/redesign/`, Start siehe `03_design_system.md`)
2. `decisions.md`
3. Den Nebenbefund X1 zu Kreuzungen

## Entscheidungen nach Priorität

### E1 · Startseite und Variante (`03_design_system.md`)

| Option | Wirkung | Aufwand Teil B |
|---|---|---|
| a so lassen | Karte unter Bedienfeld als Start; am Smartphone beginnt die Karte bei rund 1 050 px | 0 |
| b Variante A „Karte zuerst“ | Karte mit Themen, Legende links, Steckbrief rechts; t3 (Bezirk) einen Klick entfernt | Paket 1 + 2: 7–9 Tage |
| c Variante B „Überblick zuerst“ | Bezirk mit drei Kennzahlen und Top-5-Listen als Start; Karte auf Klick | 8–10 Tage |
| **d B als Startseite, A als Karte** (Empfehlung) | beantwortet t3 ohne Klick und lädt am Smartphone schneller; die Karte bleibt einen Klick oder eine Suche entfernt | 8–10 Tage (kaum mehr als c, die Bezirksseite braucht E2 ohnehin) |

### E2 · Informationsarchitektur (`02_information_architecture.md`)

| Option | Wirkung | Aufwand |
|---|---|---|
| a so lassen | 7 gleichrangige Seiten, ein Steckbrief auf einer Ebene | 0 |
| **b drei Ebenen überall, 5 Menüpunkte** (Empfehlung) | Ebene 1 höchstens 25 Wörter, Ebene 1+2 höchstens 120 (Prototyp Hallerstraße: 16 + 108 statt 558); Bezirksseite ersetzt „Tabelle“; Methode als Zusammenfassung plus Kapitel plus Regelreferenz; alte Links werden umgeschrieben | in Paket 2/3 |
| c wie b ohne Startseite | spart rund 1 Tag; die Frage „Was ist das?“ beantwortet dann die Methode | 1 Tag weniger |

### E3 · Kartenebenen, E3b Machbarkeit, E3c Unsicherheit

| Zeile | Option | Wirkung |
|---|---|---|
| E3 | a 13 Ebenen · **b 5 Themen mit 2–3 Ansichten** · c b plus „alle Ebenen“ für Fachleute | b: 5 statt 13 Entscheidungen beim Einstieg; kein Inhalt fällt weg; Netzlücken werden erstmals sichtbar (neuer Export der Maschen) |
| E3b | a beide Machbarkeitsaussagen · **b nur „Passt das Ziel?“** | eine Aussage statt zwei sich teils widersprechender (Beispiel Schippelsweg: „passt“ und „passt nach Abstrichen“) |
| E3c | a Ampel + zwei Robustheitsabschnitte · **b ein Merkmal „Wie sicher ist das?“** | heute ist 73 % der Länge gelb, weil ein Ersatzwert stadtweit gilt; künftig fällt nur „unsicher“ auf (7,3 % der Länge); die Rechnung ändert sich nicht |

### E4 · Einfache Sprache und Glossar (`04_language.md`, `glossary.yaml`)

| Option | Wirkung | Aufwand |
|---|---|---|
| a so lassen | WSTF der Steckbriefe 11–14 | 0 |
| **b Regeln und Glossar überall** (Empfehlung) | 15 Beispieltexte: WSTF 9,2 → 3,7, FRE 54 → 78, 30 % kürzer, keine Kürzel auf Ebene 1/2; neue Kategorienamen („Hauptstraße mit Tempo 30“ statt „Stadtstraße 30“) | in Paket 2 (Texte), 3 (Methode) |
| c wie b, alte Kategorienamen | Fachnamen bleiben auf Ebene 1; „Magistrale“ und „Quartier“ bleiben Planungssprache | gleich |

### E5 · Sprache der Regeldateien (`05_rule_language.md`)

| Option | Wirkung | Aufwand |
|---|---|---|
| a so lassen | Seite und Regelwerk erklären dieselbe Regel verschieden; Methodentext von Hand | 0 |
| b Felder `label_plain`, `explain_plain`, `why` | Entwurf für alle 196 Regeln, 7 Kategorien, 58 Schwellen liegt vor; Regelreferenz und Methodentext aus einer Quelle; **Nachweis:** volle Neurechnung ab der ersten Stufe gibt alle Dateien in `data/interim` unverändert wieder (24 von 24 Dateien hashgleich) | Paket 4: 1–2 Tage |
| **c wie b und Feld `history`** (Empfehlung) | zusätzlich 68 Beschreibungen ohne Versionsgeschichte, kürzer und lesbarer | + ½ Tag |

### E6 · Farbkonzept, E7 · Schrift (`03_design_system.md`, `tokens.json`)

| Zeile | Option | Wirkung |
|---|---|---|
| E6 | a Palette wie heute · **b eine Bedeutung je Farbe** | Tempo heute und Ziel mit gleichen Farben; Orange = Handlungsbedarf überall; alle Kontraste ≥ 3:1 (Daten) bzw. ≥ 4,5:1 (Text); jedes bei Farbsehschwäche enge Paar hat Breite oder Strich als zweites Merkmal |
| E7 | a Systemschrift · **b Inter selbst gehostet** · c b plus Kartenbeschriftung in Inter | b: eine Grotesk mit Tabellenziffern, keine externen Dienste; c: + 1 Tag für PBF-Glyphen |

### K1–K11 · Regeln zusammenlegen, vereinfachen, streichen (`06_rule_consolidation.md`)

Je Regel eine eigene Zeile in `decisions.md`. Zusammengefasst:

| ID | Vorschlag | Wirkung (Probelauf oder Beleg) | Empfehlung |
|---|---|---|---|
| K1 | N7 in N2 | keine; gleiche 74 Abschnitte | freigeben |
| K2 | JC-05 in JC-02 | keine Kreuzungsart; nur Kennung an 840 Knoten | freigeben |
| K3 | J-02 in J-01 | keine Kreuzungsart; nur die Zeilen-ID wechselt an 522 Knoten (J-02 → J-01) | freigeben |
| K4 | C-IMP-06 in C-IMP-05 | keine; gleicher Faktor 1,25 | freigeben |
| K5 | C-FAC-03 in S-04 | keine; gleicher Wert | freigeben |
| K6 | N6 streichen | keine | freigeben |
| K7 | PRF-07 streichen | keine; Flag kommt 0-mal vor | freigeben |
| K8 | J-11 streichen | keine (Probelauf: 0 Änderungen) | freigeben |
| K9 | P-COM-03, P-ATT-02 inaktiv | keine | freigeben |
| K10 | C-NET-11 streichen | 5 Kanten, 0,07 km Radnetz: RSV → HAUPT in Hamburg-Mitte (kurze Lücke in einem Radschnellweg) | ablehnen |
| K11 | C-NET-10 nur als Hinweis | 22 Kanten, 2,27 km Radnetzstufe (HAUPT ↔ BASIS), 5 Abschnitte (0,36 km) Fahrradstraße → Rad auf der Fahrbahn, 2 Kreuzungen „Vorfahrt erhöht“ → „rechts vor links“ (Hamburg-Nord) | ablehnen |
| alle | zusammen (Probelauf ALL) | 0 km Kategorie, 0 km Fahrstreifen und Querschnitt; 2,34 km Radnetzstufe, 0,36 km Radweg, 2 Kreuzungen (Summe aus K10 und K11) | – |

### Nebenbefunde X1–X4

- **X1 Kreuzungen:** An 743 Knoten mit heutiger Ampel schlägt J-05 einen durchgehenden Gehweg vor. 589 davon haben
  ≥ 10 000 Kfz/Tag Zufluss, zusammen gibt es dort 1 306 Radunfälle. Beispiele sind Altonaer Straße / Max-Brauer-Allee /
  Schulterblatt und Grindelberg / Hoheluftchaussee. Für GOW30 fehlt eine Zeile wie J-14 (Radroute quert). Das ist keine
  Frage des Designs, aber die neue Bezirksseite stellt genau diese Knoten nach vorn.
- **X2:** Gründe dafür und dagegen sehen gleich aus (92 % der Steckbriefe).
- **X3:** Zwei Ist-Angaben zum Radverkehr widersprechen sich (93 Abschnitte).
- **X4:** `docs/source_policy.md` fehlt.

Empfehlung: X1 als offene Frage in `docs/open_questions.md` und in die nächste Regelrunde; X2 und X3 in Paket 2
beheben.

## Aufwand Teil B im Überblick

| Paket | grob |
|---|---|
| 1 Design-System und Layout | 2–3 Tage |
| 2 Inhalte und Texte | 5–7 Tage |
| 3 Methode | 2–3 Tage |
| 4 Sprache der Regeldateien | 1–2 Tage |
| 5 Regeln zusammenlegen (nur freigegebene) | 1–2 Tage |
| **gesamt bei allen Empfehlungen** | **11–17 Tage** |

## Belege und Nachrechnen

Alle Zahlen stammen aus Skripten in `analysis/redesign/`. Die Ausgaben liegen in `data/scenarios/redesign/`, nicht in
Git. Neu erzeugen:

```sh
uv run python -m analysis.redesign.rule_inventory
uv run --with textstat --with pyphen python -m analysis.redesign.readability
uv run --with textstat --with pyphen python -m analysis.redesign.rule_language
uv run --with textstat --with pyphen python -m analysis.redesign.language_scores
uv run python -m analysis.redesign.district_data
node analysis/redesign/ui/capture.mjs && node analysis/redesign/ui/tasks.mjs          # vite preview auf :4173
node analysis/redesign/ui/prototypes.mjs && node analysis/redesign/ui/cvd.mjs         # Prototyp-Server auf :5180
uv run python -m analysis.redesign.make_lang_patch && analysis/redesign/run_worktree.sh lang network data/scenarios/redesign/lang/plain_fields.patch
uv run python -m analysis.redesign.make_consolidation_patches                          # dann run_worktree.sh je K
uv run python -m analysis.redesign.consolidation_effects K3 K8 K10 K11 ALL
uv run --with textstat --with pyphen python -m analysis.redesign.fill_tables docs/redesign/*.md
```
