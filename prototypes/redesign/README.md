# Prototypen Redesign 2026-11 (Prompt 24, Teil A)

Klickbare Entwürfe, **nur lokal**, nicht veröffentlicht und nicht Teil der Webseite. Bewertung: `docs/redesign/03_design_system.md`.

| Ordner | Inhalt |
|---|---|
| `karte-zuerst/` | Variante A: Karte als Startseite, 5 Themen, Legende in Worten, Steckbrief in drei Ebenen |
| `ueberblick-zuerst/` | Variante B: Bezirk als Startseite (Kennzahlen, Top-5-Listen, Vergleich), Karte auf Klick |
| `shared/` | Tokens als CSS (`tokens.css`), Karte (`map.js`), Kartenansicht (`mapview.js`), Steckbrief (`profile.js`) |
| `data/` | Bezirkskennzahlen und Netzlücken Eimsbüttel, erzeugt von `analysis/redesign/district_data.py` |
| `fonts/` | Inter 4.1 (variabel) mit Lizenz `OFL-Inter.txt` (SIL OFL 1.1) |

## Starten

Voraussetzung: `make export` (Daten in `data/out`) und `npm --prefix web install`.

```sh
uv run python -m analysis.redesign.district_data         # data/districts.json, data/mesh_gaps.geojson
cd web && npx vite --config ../prototypes/vite.config.mjs  # http://localhost:5180/redesign/
node analysis/redesign/ui/prototypes.mjs                    # Bildschirmfotos, axe, Wortzahlen
```

## Hinweise

- `data/out` dient als öffentliches Verzeichnis; Daten werden nicht kopiert (außer den kleinen Dateien in `data/`).
- Aus `web/src` werden `palette.js` (nur `SHAPES`), `panel.js` (`crossSectionSvg`) und `util.js` importiert, nicht geändert;
  aus dem Review-Prototyp `shared/steckbrief.js` die Hilfen `changes` und `fitAnswer`.
- `mesh_gaps.geojson` liegt nur zur Anzeige in EPSG:4326 vor, wie die Prüfdateien in `reports/`.
- `window.proto` ist ein Testzugang für `analysis/redesign/ui/prototypes.mjs`.
