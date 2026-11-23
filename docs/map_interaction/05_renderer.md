# Bild-Renderer `tools/render_card`

Stand: 22.11.2026, Prompt 28 – Konzept aus Phase 1.5, in Phase 2 umgesetzt (Abweichungen vom Konzept unter
„Umsetzung“ am Ende). Entscheidung (Frage 4): **nur auf Abruf** per Kommandozeile für ausgewählte
Elemente. Keine Vorschaubilder je Link (Open Graph), weil die Seite mit Hash-Links arbeitet und dafür je Element
eine statische Seite nötig wäre (≈ 33 700 Abschnitte + 14 300 Kreuzungen, geschätzt 3–8 GB PNG). Das
seitenweite `og-image.png` bleibt.

## Aufruf

```
npm --prefix web run build                                    # einmal: gebaute Seite mit data/out
tools/render_card seg seg_fa69d3625e877ae8                    # alle drei Formate nach data/cards/
tools/render_card node 250834498 --format og
tools/render_card place schanze_verkehrsberuhigt --format og,portrait,a4 --out data/cards
tools/render_card --list docs/map_interaction/cards_samples.txt   # eine Zeile je Element: "<seg|node|place> <id>"
tools/render_card … --base http://localhost:4173/             # gegen einen laufenden vite preview
```

`tools/render_card` ist ein kleines Shell-Skript, das `web/tools/render_card.mjs` startet (Node + Playwright aus
`web/node_modules`, keine neue Abhängigkeit).

## Ablauf

1. Startet einen lokalen statischen Server auf `web/dist` (gebaute Seite mit `data/out`), oder nutzt `--base` für
   einen laufenden `vite preview`. Kein externer Kachel- oder Renderdienst; Grundkarte, Schriften und Sprites
   kommen aus `data/out/basemap`.
2. Öffnet eine eigene Seite `card.html` (zweiter Vite-Einstieg, nicht in der Navigation) mit Hash im
   URL-Schema v2, z. B. `card.html#karte?v=2&seg=seg_…`. Die Seite
   - lädt den Steckbrief (`segments/<id>.json`, `junctions/<id>.json` bzw. den Ort aus `meta.special_places`),
   - zeichnet die Karte mit **denselben Ebenen und Farben wie die Webseite** (`sfpLayers` aus `layers.js`,
     Palette aus `palette.js`), Ausschnitt per `fitBounds` auf das Element, Auswahl hervorgehoben,
   - setzt Querschnitt bzw. Kreuzungsskizze aus denselben Funktionen wie der Steckbrief ein
     (`crossSectionSvg` in `panel.js`, `junctionSvg` in `junction_sketch.js`),
   - meldet `window.cardReady = { alt }`, sobald die Karte `idle` ist und die Schriften geladen sind.
3. Playwright macht den Screenshot in der Zielgröße und schreibt `<art>_<id>_<format>.png` und
   `<art>_<id>.alt.txt` (Alternativtext) sowie `<art>_<id>.json` (Eingangswerte, Datenstand, Versionen).

## Formate

| Format | Größe | Zweck | Aufbau |
| --- | --- | --- | --- |
| `og` | 1200 × 630 px | Linkvorschau | Karte links (7 von 12 Spalten), rechts Titel, Satz, Querschnitt klein, Fuß mit Quelle und Link |
| `portrait` | 1080 × 1350 px | Social Media hochkant | Titel oben, Karte (4:3), Querschnitt groß, Satz, Fuß |
| `a4` | 1654 × 1181 px (140 × 100 mm bei 300 dpi) | Einklinker für Briefe | Karte und Querschnitt nebeneinander, Titel, Quelle; ohne Projekt-URL-Werbung, nur Deep Link klein |

Die A4-Variante wird mit `deviceScaleFactor` 300/96 gerendert, damit Linien und Schrift scharf sind; die
Pixelmaße oben sind das Ergebnis.

## Inhalt jeder Karte

- **Kartenausschnitt** mit dem Element hervorgehoben, Maßstab, OSM-/Protomaps-Vermerk im Bild.
- **Querschnitt heute und Ziel, wo vorhanden:** Das Ziel als gezeichneter Soll-Querschnitt (`crossSectionSvg`).
  Für heute gibt es im Export keine Aufteilung nach Elementen, nur Kennwerte (Breite, Tempo, Fahrstreifen).
  Heute wird deshalb als kurze Zeile mit Kennwerten gezeigt, nicht als erfundene Zeichnung.
  Kreuzungen: Skizze Ist und Soll aus `junctionSvg`. Orte: Querschnitt im Vorschlag (wie im Steckbrief).
- **Titel** (Straßenname mit Bezirk, Kreuzungsname bzw. Ortsname) und **ein Satz in einfacher Sprache** (Ebene 1
  des Steckbriefs, derselbe Text wie auf der Webseite).
- **Quelle und Stand:** „Straßenfunktionsplan Hamburg – Entwurf, nicht amtlich · Datenstand TT.MM.JJJJ ·
  Kartendaten © OpenStreetMap-Beitragende (ODbL)“ plus die dl-de/by-2.0-Vermerke der verwendeten Quellen (aus
  `meta.json`/`docs/licenses.md`). Bei Orten zusätzlich Initiative und Stand aus `special_places.yaml`.
- **Projekt-URL mit Deep Link**, lesbar gekürzt: `hamburgmobility.de/#karte?v=2&seg=seg_…`.

## Regeln

- **Design-Tokens:** Schrift Inter (selbst gehostet), Größen und Abstände aus `docs/redesign/tokens.json`, keine
  Schatten, keine Rundungen, Farbe nur für Daten. Kein neues Logo-Layout: das HMR-Rasterlogo klein im Fuß.
- **Deterministisch:** gleiche Eingabe → gleiches Bild (byte-gleiche PNG). Dafür:
  - feste Viewport-Größe und `deviceScaleFactor`, Chromium aus `web/node_modules` (Version fest in `package-lock.json`),
  - keine Animation (`fitBounds` mit `duration: 0`), `preserveDrawingBuffer: true`, warten auf `idle` und
    `document.fonts.ready`,
  - kein Datum „heute“ im Bild, nur der Datenstand aus `meta.json`,
  - Hintergrund weiß, keine zufälligen Platzierungen (Beschriftungs-Kollision ist in MapLibre deterministisch bei
    gleichem Ausschnitt),
  - Software-Rendering (`--use-gl=swiftshader`), damit die GPU keine Rolle spielt.
  - Test: dasselbe Element zweimal rendern → gleicher SHA-256. Falls swiftshader minimal abweicht, wird das
    gemessen und als Toleranz (Pixel-Differenz 0) im Bericht genannt, nicht verschwiegen.
- **Alternativtext** je Bild, aus den Daten erzeugt, z. B.: „Karte: Osterstraße in Eimsbüttel, hervorgehoben.
  Ziel: Geschäftsstraße mit Tempo 30. Heute: Tempo 50, zwei Fahrstreifen. Querschnitt im Ziel: Gehweg 3,5 m,
  Radweg 2,3 m, Fahrbahn 6,5 m, Radweg 2,3 m, Gehweg 3,5 m.“
- **Lizenzen:** Bilder sind OSM-Ableitungen (ODbL) und tragen den Vermerk im Bild.
- **Unfalldaten** erscheinen höchstens aggregiert je Abschnitt (wie auf der Webseite).

## Tests (Phase 2)

- Maße je Format, Alt-Text vorhanden und ohne `undefined`, Determinismus (zweimal rendern, gleicher Hash).
- Muster: 5 Abschnitte (verschiedene Kategorien, einer mit Ort), 3 Kreuzungen (mit und ohne Umbau), der Ort
  Schanze → `docs/map_interaction/img/cards/`.

## Umsetzung (Phase 2)

- Dateien: `tools/render_card` (Shell), `web/tools/render_card.mjs` (CLI, Playwright), `web/card.html` +
  `web/src/card.js` (Seite), `web/src/card_content.js` (Inhalt, getestet in `web/test/card.test.js`),
  `web/src/card.css` (Layout). Die Karte kommt aus `createMap(…, { static: true })` in `web/src/map.js`: dieselben
  Ebenen wie die Website, ohne Bedienung, ohne Einblenden, Zeichenpuffer bleibt erhalten.
- Ausgabe standardmäßig nach `data/cards/` (nicht in Git, wie alle Daten); je Element `<id>_<format>.png`,
  `<id>.alt.txt`, `<id>.json` (Dateien, SHA-256, Titel, Alternativtext). Für den Bericht als JPEG unter `img/cards/`.
- Abschnitte: Die Karte wird auf das Stück selbst eingepasst (mindestens ≈ 350 m Ausschnitt), damit die
  Hervorhebung sichtbar ist; Geometrie aus den Vektorkacheln.
- Kreuzungen: In der Linkvorschau (1200 × 630) entfällt die Skizze, sie wäre zu klein zum Lesen; hochkant und A4
  zeigen sie.
- Heute: Für Abschnitte gibt es im Export keinen Ist-Querschnitt nach Elementen; die Karte nennt Tempo, Radführung
  und Breite heute als Text und zeichnet nur das Ziel.
- A4: 827 × 591 CSS-Pixel bei Faktor 2 = 1654 × 1182 px = 140 × 100 mm bei 300 dpi.
- Determinismus geprüft: `web/e2e/card.spec.js` rendert dieselbe Karte zweimal – byte-gleiche PNG (SHA-256 gleich),
  mit SwiftShader und fester Chromium-Version aus `package-lock.json`. Auf einem anderen Rechner oder mit einer
  anderen Chromium-Version können Pixel abweichen; Vergleiche daher immer mit demselben Stand.
- Laufzeit: 27 Karten (9 Elemente × 3 Formate) in 47 s, ≈ 1,7 s je Karte, zusammen 7,9 MB PNG.
- `card.html` wird mit der Website ausgeliefert (nicht verlinkt, `noindex`); sie lädt nur Daten, die die Seite
  ohnehin ausliefert.
