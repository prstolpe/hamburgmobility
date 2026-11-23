# Bericht Prompt 28 – Karteninteraktion und Legenden

Stand: 22.11.2026 · Branch `feature/map-interaction` (von main) · Haltepunkt 2 · noch nicht gemergt, nicht ausgeliefert.
Nur Darstellung: Regelwerk, `segment_id`/`node_id`, Overrides und Datenexporte sind unverändert (keine Änderung unter
`pipeline/`, `config/`, `overrides/`).

## Auf einen Blick

- **Legende aus einem Register** (`web/src/legend_registry.js`): zeigt nur, was eingeschaltet ist; Einträge ohne
  Linie im Ausschnitt grau; Eintrag antippen hebt nur diese Linien hervor; „?“ erklärt den Eintrag; jede Ansicht
  verlinkt ihr Methodenkapitel. Bus, Unfälle und Schulen/Kitas haben jetzt Legendeneinträge (vorher keine).
- **Panel links, Variante C** („Ebenen = Legende“): Thema und Ansicht mit ihrer Legende oben, darunter jede Ebene
  als Schalter – eingeschaltet klappt ihre Legende darunter auf. Chips auf der Karte entfernen eine Ebene mit einem
  Tipp. Höchstens 3 Ebenen gleichzeitig.
- **Mobil**: Karte füllt den Bildschirm, das Panel ist ein Bottom Sheet **unter** der Karte (drei Höhen,
  „Einklappen“), ein Tipp auf eine Linie zeigt erst eine Vorschau; der Steckbrief ersetzt das Sheet. Kompakter Kopf
  (Logo, Suche, Menü) – spart rund 130 px.
- **Farben**: Buslinien Ocker `#997700`, Unfälle Weinrot `#882255`, Schulen/Kitas als Ring.
- **URL-Schema v2** (`docs/url_scheme.md`) mit 33 Tests, darunter 25 alte Linkmuster und 300 zufällige Round-Trips.
- **Bild-Renderer** `tools/render_card`: drei Formate, deterministisch (byte-gleich geprüft), Alternativtext.
- Tests: 206 Unit-Tests, 80 E2E-/axe-Tests grün; axe 0 Verstöße auf 34 Seitenprüfungen.

## Vorher / nachher

| Ansicht | vorher | nachher |
| --- | --- | --- |
| Desktop, Aufgabe | `img/before/before-desktop-aufgabe-z13.jpg` | `img/after/after-desktop-aufgabe-z13.jpg` |
| Desktop, Buslinien an | `img/before/before-desktop-bus-z13.jpg` (keine Legende zum Bus) | `img/after/after-desktop-bus-z13.jpg` (Legende + Chip, Ocker) |
| Desktop, drei Ebenen | – | `img/after/after-desktop-layers.jpg` |
| Desktop, Hervorhebung + „?“ | – | `img/after/after-desktop-highlight.jpg` |
| Desktop, Vorschau beim Überfahren | – | `img/after/after-desktop-hover.jpg` |
| Desktop, Ort Schanze | `img/before/before-desktop-place-schanze.jpg` | `img/after/after-desktop-place-schanze.jpg` |
| Mobil, Start | `img/before/before-mobile-aufgabe-z13.jpg` (Karte ≈ 55 % der Höhe, Legende unter der Karte) | `img/after/after-mobile-aufgabe-z13.jpg` (Karte ≈ 87 %) |
| Mobil, Bedienung offen | `img/before/before-mobile-panel-open.jpg` (≈ 57 px Karte) | `img/after/after-mobile-sheet-half.jpg` (Karte ≈ 42 %, nichts verdeckt) |
| Mobil, Steckbrief | `img/before/before-mobile-seg-selected.jpg` | `img/after/after-mobile-seg-selected.jpg` |
| Mobil, Menü | – | `img/after/after-mobile-menu.jpg` |

Varianten-Vorschau aus Haltepunkt 1: `img/options/`.

## Walkthrough: Schritte vorher → nachher

Agent `usability-walkthrough` (sonnet), gleiche Aufgaben und Zählregeln wie in `02_walkthrough.md`.

| Aufgabe | Desktop | Tastatur | Mobil |
| --- | --- | --- | --- |
| T1 Steckbrief Osterstraße | 3 → 3 | 10 → 10 | 3 → 3 |
| T2 Bedeutung einer Linienfarbe | Legende 0 → 0; eine Straße prüfen 5 → **1** (Überfahren) | auf der Karte nicht möglich → Hervorhebung über Legende; Straße über Liste | 5 → 3 (Sheet öffnen bzw. Linie antippen) |
| T3 Bus an und aus | 3 → 3 | 27, danach Fokus verloren → 26, **Fokus bleibt** | 5, Karte unsichtbar → 5, **Karte sichtbar** |
| T4 Ort Schanze | 1 → 1 (+ Scrollen) | 20 → 28 (über „Orte“: 8) | 2, Karte unsichtbar → 5 bzw. 3 über Menü → Orte, **Karte sichtbar** |
| T5 Kreuzung heute/Ziel | 3 → 3; neu auch über die Karte (2) | 11 → 11 | 3 → 3 |
| T6 Link teilen | 3 + Adresszeile → **4, mit „Link kopieren“** | 10 + Strg+L/C → 12 | 3 + Teilen des Browsers → 4, oder 1 aus der Vorschau |

Nach dem Walkthrough behoben: Kamera blieb mobil nach Suche stehen (Polsterung brach die Kamerafahrt ab);
besondere Orte stehen jetzt als erste Ebene (T4 mobil: ein Wischen weniger); „Einklappen“-Knopf im Sheet;
Sprunglinks „Zu den Ebenen“ / „Zur Liste“ am Panelanfang (T4 Tastatur ≈ 20 Tabs kürzer, nicht nachgezählt);
doppeltes „Vorschlag. Vorschlag …“; kurzer Platzhalter in der mobilen Suche; Fokus nach „Auf der Karte zeigen“.

Mehr Schritte als vorher: T4 Tastatur ohne Sprunglink (jeder Legendeneintrag hat zwei Stopps: Eintrag und „?“) und
T4 mobil (das Sheet muss erst geöffnet werden) – dafür bleibt die Karte sichtbar.

## Leistung

Gemessen mit demselben Skript wie vorher (`03_baseline.md`), ruhige Maschine, 5 Läufe; Bildrate auf dem
gedrosselten Mobilprofil (CPU ×4, Software-WebGL im Headless-Chromium).

| Kennzahl | vorher | nachher | Budget | erfüllt |
| --- | ---: | ---: | --- | --- |
| JS auf `#karte` (gzip) | 347,5 KB | 356,2 KB (+8,7 KB) | ≤ +15 KB | ja |
| CSS auf `#karte` (gzip) | 14,4 KB | 15,4 KB | – | – |
| Renderer-Seite `card.html` (nur dort geladen) | – | 7,6 KB | – | – |
| Zeit bis bedienbar, Desktop (Median) | 1578 ms | 1680 ms (+6,5 %) | ≤ +5 % | **knapp nein** |
| Zeit bis bedienbar, Mobil (Median) | 2691 ms | 2770 ms (+2,9 %) | ≤ +5 % | ja |
| Bildrate Mobil, Median | 9,8 fps | 7,9 fps | nicht schlechter | **nein** |
| Bildrate Mobil, gleiche Kartengröße wie vorher | 9,8 fps | 10,5 fps | nicht schlechter | ja |
| axe-Verstöße | 0 | 0 | 0 | ja |

Einordnung:
- **Bildrate:** Die Karte ist mobil jetzt ≈ 58 % größer (390 × 733 statt 390 × 464 px) – das war das Ziel. Bei
  gleicher Kartengröße ist die neue Seite nicht langsamer (10,5 statt 9,8 fps). Der Rückgang kommt allein von der
  Fläche; im Headless-Chromium rechnet die CPU jedes Pixel (SwiftShader), auf echten Telefonen die GPU. Auf einem
  echten Mittelklasse-Telefon nicht gemessen.
- **Desktop-Ladezeit:** +6,5 % im Median liegt knapp über dem Budget und innerhalb der Streuung der Läufe
  (vorher 1547–1727 ms, nachher 1564–1783 ms); die Karte ist auch auf dem Desktop etwas größer (volle Höhe unter
  dem Kopf). Eine erste Messung (+42 %) war durch parallel laufende Agenten verfälscht und zeigte zusätzlich, dass
  das Panel bei jedem Neuzeichnen alle Kartenebenen neu einfärbte – behoben (Farbänderung nur noch bei geänderter
  Hervorhebung).
- Lange Aufgaben (> 50 ms) beim Verschieben: max. 75 ms, in der Trägheit der Kartenbewegung; 0 in Ruhe.

Vorschlag: Budget für die Bildrate künftig **je Kartenfläche** festlegen; Desktop-Ladezeit bei der Live-Prüfung
erneut messen.

## Barrierefreiheit

- axe-core 4.13: 0 Verstöße (34 Seitenprüfungen, Desktop und Mobil), `reports/web_accessibility.md` neu erzeugt.
- Tastatur: sichtbarer Fokus an allen 34 Stopps; Thema und Ansicht als Radiogruppen mit Pfeiltasten; Fokus bleibt
  beim Umschalten erhalten; Esc schließt nacheinander Steckbrief, Vorschau, Hervorhebung.
- Namen: Legendeneinträge, „?“ („Was heißt „…“?“), Chips („Buslinien ausblenden“), Zoomknöpfe deutsch,
  Kartenbeschreibung je Thema. Behoben nach der Prüfung: Chips-Gruppe mit `role="group"`, „Steckbrief schließen“
  ohne doppelten Namen, unterstrichene Links in der mobilen Quellenzeile (WCAG 1.4.1).
- Bewegung: Kamerafahrten unter `prefers-reduced-motion` ohne Animation; das Sheet springt ohne Übergang.

## URL-Schema

`docs/url_scheme.md`. Neu: `v=2`, `layers`, `node`, `z`/`lat`/`lon`/`pitch`/`bearing`. Alte Parameter (`ov`, `jct`,
`map`, `layer`, `place`, Seitenaliasse) werden beim Laden umgeschrieben und öffnen dieselbe Ansicht; unbekannte
Parameter werden ignoriert. Tests: `web/test/url_scheme.test.js`.
Bewusste Änderung: Ein Link **ohne** Kartenausschnitt, aber mit Auswahl (`seg=` oder `node=`, wie ihn „Link
kopieren“ erzeugt) zoomt jetzt auf die Auswahl statt ganz Hamburg zu zeigen. Alte geteilte Links enthalten fast
immer `map=` und öffnen unverändert.

## Bild-Renderer

`tools/render_card` (Doku: `05_renderer.md`). Muster für 5 Abschnitte, 3 Kreuzungen und den Ort Schanze
(`cards_samples.txt`) in drei Formaten, als JPEG unter `img/cards/` mit Alternativtexten (`*.alt.txt`):

| Element | Linkvorschau 1200 × 630 | hochkant 1080 × 1350 | A4 140 × 100 mm, 300 dpi |
| --- | --- | --- | --- |
| Hoheluftchaussee (Hauptstraße 50) | `seg_fa69d3625e877ae8_og.jpg` | `…_portrait.jpg` | `…_a4.jpg` |
| Eißendorfer Waldweg (Hauptstraße 30) | `seg_896df8d623e86dbd_og.jpg` | … | … |
| Ahlfeld (Wohnstraße 30) | `seg_2918b094e23dd272_og.jpg` | … | … |
| Max-Herz-Ring (Fußgängerzone/Spielstraße) | `seg_bb2a610284237a82_og.jpg` | … | … |
| Juliusstraße (im Ort Schanze) | `seg_6ce9aef17032f285_og.jpg` | … | … |
| Kreuzung Curschmannstraße / Eppendorfer Weg / Lenhartzstraße (Umbau) | `node_250834498_og.jpg` | … | … |
| Kreuzung Heußweg / Lutterothstraße (Umbau) | `node_243077324_og.jpg` | … | … |
| Kreuzung Söderblomstraße / Wichelwisch (kein Umbau) | `node_225473807_og.jpg` | … | … |
| Verkehrsberuhigte Schanze | `place_schanze_verkehrsberuhigt_og.jpg` | … | … |

27 Karten in 47 s (≈ 1,7 s je Karte), 7,9 MB PNG. Determinismus: dieselbe Karte zweimal gerendert → gleicher
SHA-256 (`web/e2e/card.spec.js`). Heute wird als Text gezeigt (Tempo, Radführung, Breite), weil der Export keinen
Ist-Querschnitt nach Elementen hat.

## Wer hat was gemacht

| Agent | Modell | Aufgabe |
| --- | --- | --- |
| `ui-inventory` (neu angelegt) | haiku | Inventur Ebenen, Legende, Bedienelemente, URL-Parameter, Farben → `01_inventory.md` |
| `screenshot-runner` | haiku | Screenshots vorher und nachher, Desktop 1440 / Mobil 390 → `img/before/`, `img/after/` |
| `usability-walkthrough` (neu angelegt) | sonnet | Aufgaben T1–T6 in drei Modi, alte und neue Oberfläche → `02_walkthrough.md`, Tabelle oben |
| `a11y-perf-check` | haiku | Bundle, Ladezeit, Bildrate, axe, Tastaturgang, Namen (vorher/nachher) |
| `review` | sonnet | unabhängige Prüfung des Diffs gegen den Auftrag (13 Punkte; 9 behoben, Rest unten) |
| Hauptsitzung | Opus | Konzept, Varianten-Vorschau, Register, Panel, URL-Schema, Renderer, Texte, Nachmessung, Korrekturen |

## Offene Punkte

1. **Leeres Kartenband in Headless-Screenshots**: Wenn das mobile Menü über der Karte aufklappt, zeigt
   Headless-Chromium unter dem Menü teils eine weiße Fläche (`img/after/after-mobile-menu.jpg`). Vermutlich ein
   Darstellungsfehler von Software-WebGL beim Überlagern; auf einem echten Telefon nicht geprüft. Bitte in der
   Vorschau auf dem eigenen Telefon ansehen.
2. **Bildrate** auf dem Telefon mit großer Karte: auf echtem Gerät messen (siehe Leistung).
3. **Liste „Straßen im Ausschnitt“** ist bei kleinem Zoom leer (die Kacheln tragen dort keine Namen); der Hinweis
   sagt „Hineinzoomen“. Für Tastaturnutzer ist der Weg zu einer Kreuzung über die Karte damit lang; die Suche
   bleibt der kurze Weg.
4. **Suche**: Enter wählt den ersten Treffer (oft die Straße statt der Kreuzung), ein Straßentreffer öffnet das
   erste Stück. Nicht geändert (außerhalb dieses Auftrags); Kandidat für den Such-Auftrag mit Adresssuche.
5. **Vorschau einer Kreuzung** nennt nur das Ziel, „heute“ steht erst im Steckbrief.
6. **`card.html`** wird mit der Seite ausgeliefert (nicht verlinkt, `noindex`, lädt nur ohnehin öffentliche Daten).
   Wenn unerwünscht: nur für lokale Builds erzeugen.
7. **Zurück-Taste** setzt die Auswahl zurück, nicht den Kartenausschnitt (der Ausschnitt wird ohne
   Verlaufseintrag mitgeschrieben). So beabsichtigt.
8. Außerhalb des Auftrags notiert (`docs/open_questions.md`): „Warum?“-Text kann der Überschrift widersprechen;
   „Parkplätze: keine Daten. (keine Daten)“.
9. Nach dem Mergen: Live-Prüfung mit `screenshot-runner` inklusive 10 alter geteilter Links.
