# Redesign 2026-11 · Teil B, Paket 2: Inhalte und Texte

Branch `redesign/2026-11-p2-content` (von `redesign/2026-11` nach Paket 1). Umgesetzt sind **E1 b**, **E2 b** (mit der
Klärung zur Navigation), **E3 b**, **E3b b**, **E3c b**, **E4 b**, **X2 b** und **X3 b** aus `decisions.md`. **Nicht
live:** nur lokale Vorschau. Die Daten in `data/out` sind neu exportiert, aber nur lokal.

## Was sich ändert

### Webseite (`web/`)

| Bereich | vorher | nachher |
|---|---|---|
| Navigation | 7 Punkte (Karte, Tabelle, Methode, Radnetz, Downloads, Quellen & Lizenzen, Impressum) | 4 Punkte: **Karte · Bezirke · Methode · Daten**; Impressum, Quellen und Methode auch im Fuß; der Titel führt zur Karte |
| Start | Karte unter dem Bedienfeld | Karte mit dem Kasten **„Was ist das?“** beim ersten Besuch (2 Sätze, Suchhinweis, Link zur Methode; „Verstanden“ merkt sich das im Browser) |
| Kartenebenen | 13 Radioknöpfe | **5 Themen** über der Karte (Aufgabe und Tempo, Heute und Ziel, Platz in der Straße, Radnetz, Kreuzungen) mit je 1–3 Ansichten; seltene Ansichten (Hauptverkehrsstraßen, Breite, Regelprofil, amtliches Netz) unter „Mehr Ansichten und Filter“ |
| Neue Ansichten | – | „Dringlichkeit“ (Priorität in drei Stufen); „Lücken“ zeigt auch zu weitmaschige Netzteile als Fläche |
| Kreuzungen | nur in der Ebene „Knotenpunkte“ anklickbar | in jedem Thema ab Zoom 14 als Punkte antippbar |
| Legende | Kürzel („GOW30 – Stadtstraße 30“, „D1 – …“) | nur Klarnamen („Hauptstraße mit Tempo 30“, „gebaut wie eine Hauptstraße“), Überschrift „Was die Farben bedeuten“, ein Satz je Ansicht in Einfacher Sprache |
| Suche | nur Straßen, öffnet keinen Steckbrief | Straßen **und Kreuzungen**; öffnet den Steckbrief |
| Steckbrief | 13–15 gleichrangige Abschnitte | **drei Ebenen**: Name, Aufgabe, eine Kennzahl; „Mehr erfahren“ (Warum? Was ändert sich? Passt das Ziel?); „Details und Quellen“ (Regeln, Wie sicher ist das?, Abweichung, Radverkehr, Daten, ID) |
| E3b | zwei Machbarkeitsaussagen | eine: „Passt das Ziel?“ (Querschnitt mit Radweg); das Regelprofil nur auf Ebene 3 und als seltene Ansicht |
| E3c | Ampel und zwei Robustheitsabschnitte | ein Merkmal „Wie sicher ist das?“; nur „unsicher“ erscheint auf Ebene 2, als ruhiger Satz; Tabelle mit einer Spalte „Wie sicher?“ |
| X2 | Gründe dafür und dagegen gemischt | „Warum?“ nennt nur zutreffende Gründe; „trifft zu / trifft nicht zu“ auf Ebene 3 |
| X3 | zwei Ist-Angaben zum Radverkehr | nur die Ist-Führung (S-FEAT-13, `cycling.facility.ist_text`) |
| Bezirke | Seite „Tabelle“ mit Kürzeln | **Bezirksseite**: Übersicht der 7 Bezirke; je Bezirk ein Satz, drei Kennzahlen, drei Top-5-Listen (Straßen, Kreuzungen, Radnetz-Lücken), Vergleich aller Bezirke und die Tabelle auf Ebene 3 (Spalten in Klartext) |
| Daten | Downloads und Quellen getrennt | eine Seite „Daten“ (Herunterladen, Quellen und Lizenzen) |
| Alte Links | – | werden beim Laden umgeschrieben (`?layer=…`, `#tabelle`, `#downloads`, `#quellen`, `ov=cyc`), je Zeile der Tabelle in `02_information_architecture.md` ein Test |

### Export und Texte (`pipeline/`, `config/`)

- **Neu im Export** (`pipeline/lib/export_overview.py`, Tests in `tests/test_export_overview.py`):
  - `districts/<bezirk>.json`: Kennzahlen und Top-5-Listen
  - `search_junctions.json`
  - `cycle_mesh_gaps.geojson`
  - in `meta.json`: `overview`, `glossary`, `site_texts`, `categories[*].speed_kmh`
  Anzeigeparameter stehen in `config/project.yaml` `web.overview`, ohne Schwellen im Code.
- **`config/glossary.yaml`** (vorher `docs/redesign/`) ist die einzige Quelle für Klarnamen. Die Kategorienamen der Seite
  kommen von dort, der Fachname bleibt als `label_de`.
- **`config/plain_language.yaml` 0.10.0** (CHANGELOG):
  - Begründungen, Hinweise, Radweg- und Kreuzungsnamen in Einfacher Sprache
  - neue Abschnitte `overview` und `site`
  - keine Bedingung und keine Schwelle geändert
  - Die Datenbeschreibung der Downloads bleibt fachlich.
- **Download-Beschreibungen** in Einfacher Sprache.

### Arbeitsteilung

Die Module `web/src/profile.js`, `districts.js` und `datapage.js` mit ihren Tests sowie die Anpassung der Browser-Tests
und des Bildschirmfoto-Skripts haben Agenten mit kleineren Modellen geschrieben (Sonnet, Haiku). Den Test für das
Sortieren der Tabelle habe ich ergänzt, weil er bei der Anpassung weggefallen war. Ich habe sie danach geprüft, eingebunden
und an drei Stellen korrigiert:

- Klein-/Großschreibung im Steckbrief
- Ziel-Tempo der Fußgängerzone aus den Daten statt fest im Code
- Beschriftungen der Bezirkskarten aus den Texten statt fest im Code

## Prüfungen

| Prüfung | Ergebnis |
|---|---|
| Tests zuerst | `tests/test_export_overview.py` (6), `web/test/state.test.js` (Weiterleitungstabelle), Modultests für Steckbrief, Bezirksseite, Datenseite |
| `make test` | Python 1 549 bestanden (6 neue), 2 xfailed; Web 100 bestanden |
| Determinismus Export | zwei `make export` hintereinander: 49 994 Dateien in `data/out` gleich, nur `meta.json` anders (Feld `generated`) |
| Determinismus Build | zwei Builds: alle 7 Code-Dateien byte-gleich |
| e2e und axe | `npx playwright test` gegen die Vorschau: 42 bestanden (Desktop und Pixel 7), darunter Themen/Ansichten in der URL, Umschreiben alter Links, Bezirksseite, Tabelle sortieren, Suche mit Kreuzungen. axe-core (WCAG 2.2 AA): 11 Seiten × 2 Geräte, **0 Verstöße**. Bildschirmfotos ohne JavaScript-Fehler (`IMG_PREFIX=p2- node analysis/redesign/ui/capture.mjs`) |
| Lesbarkeit geänderter Texte | `plain_language.yaml` (ohne Datenbeschreibung): WSTF 10,0 → **7,6**, FRE 49,3 → **60,6**, Fachbegriffe/Kürzel 86 → 33. Erklärsätze der Kartenansichten: WSTF 10,7 → **4,7**, FRE 43,9 → **72,3**, Fachbegriffe/Kürzel 22 → 1 (`analysis/redesign/p2_readability.py`). Zielwerte aus A4 (WSTF ≤ 8, FRE ≥ 60) erreicht |

## Bilder

| | vorher | nachher |
|---|---|---|
| Karte (Start, erster Besuch) | ![](img/c-karte-desktop.jpg) | ![](img/p2-intro-desktop.jpg) |
| Karte, Thema Aufgabe und Tempo | ![](img/p1-layer-cat-desktop.jpg) | ![](img/p2-layer-aufgabe-ziel-desktop.jpg) |
| Radnetz: Lücken | ![](img/p1-layer-cgap-desktop.jpg) | ![](img/p2-layer-rad-luecken-desktop.jpg) |
| Dringlichkeit (neu) | – | ![](img/p2-layer-abweichung-prio-desktop.jpg) |
| Steckbrief Kieler Straße | ![](img/p1-profile-GOW30-desktop.jpg) | ![](img/p2-profile-GOW30-desktop.jpg) |
| Steckbrief Kreuzung | ![](img/c-junction-desktop.jpg) | ![](img/p2-junction-desktop.jpg) |
| Bezirke (vorher: Tabelle) | ![](img/c-tabelle-desktop.jpg) | ![](img/p2-bezirke-desktop.jpg) |
| Daten | ![](img/c-downloads-desktop.jpg) | ![](img/p2-daten-desktop.jpg) |
| Smartphone: Start | ![](img/c-layer-cat-mobile.jpg) | ![](img/p2-intro-mobile.jpg) |
| Smartphone: Karte | ![](img/p1-layer-cat-mobile.jpg) | ![](img/p2-karte-mobile.jpg) |
| Smartphone: Steckbrief | ![](img/p1-profile-GOW30-mobile.jpg) | ![](img/p2-profile-GOW30-mobile.jpg) |
| Smartphone: Bezirk | – | ![](img/p2-bezirke-mobile.jpg) |

Alle Themen und Ansichten, Steckbriefe und Seiten: `docs/redesign/img/p2-*.jpg` (vollständige Liste in
`data/scenarios/redesign/ui/content-p2.json`). Im Steckbrief-Bild sind für die Texterfassung alle Ebenen geöffnet;
im Normalfall ist Ebene 3 zu und am Smartphone auch Ebene 2.

## Offen und Hinweise

- **Methode** ist inhaltlich noch die alte Seite (mit Kürzeln in der Kategorienliste). Sie wird in Paket 3 neu gebaut,
  mit Kapiteln in drei Ebenen und der Regelreferenz. Die Seite „Radnetz“ ist von der Methode aus verlinkt.
- **Radverkehrsführung an Kreuzungen:** Der Satz für Radfahrende im Kreuzungs-Steckbrief (Ebene 2) kommt wörtlich aus
  den Regeltexten JC-01…JC-06 in `design_rules.yaml`. Er enthält noch Kürzel, zum Beispiel „≥ 4,00 m RSV, ≥ 3,00 m
  HAUPT“. Er wird durch die Klartext-Felder aus Paket 4 (E5) ersetzt.
- **Ebene im Link:** Ob Ebene 2 oder 3 offen ist, steht nicht in der URL. Das wäre eine kleine Ergänzung.
- **Nebenbefunde:** X1 (Kreuzungsregel) und X4 (`docs/source_policy.md`) sind keine Inhalte der Webseite. Sie folgen
  mit Paket 3 bzw. 4.
- Nach deinem OK: Merge nach `redesign/2026-11`. Deployment nur mit deinem ausdrücklichen OK.
