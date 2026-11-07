# Prototypen Oberfläche (Review 2026-11, Phase 3)

Klickbare Entwürfe, **nur lokal**, nicht veröffentlicht und nicht Teil der Webseite. Bewertung: `docs/review/2026-11/03_oberflaeche.md`.

| Ordner | Konzept |
|---|---|
| `themen/` | A – Themen statt Ebenen |
| `vergleich/` | B – Ist/Soll-Vergleich mit Schieberegler, Szenario „GOW50-Kompromiss“ |
| `gefuehrt/` | C – Geführter Einstieg mit Bezirksübersicht |
| `shared/` | Karte, neuer Steckbrief, Kennzahlen und Szenariodaten für Eimsbüttel |

## Starten

Voraussetzung: `make export` (Daten in `data/out`) und `npm --prefix web install`.

```sh
uv run python analysis/review_2026_11/ui/district_kpi.py   # shared/kpi.json, scenario_eimsbuettel.json, mesh_gaps_eimsbuettel.geojson
cd web && npx vite --config ../prototypes/vite.config.mjs  # http://localhost:5180/
```

## Hinweise

- `data/out` dient als öffentliches Verzeichnis; es werden keine Daten kopiert.
- Aus `web/src` werden `palette.js`, `layers.js`, `panel.js` und `util.js` nur importiert, nicht geändert.
- Das Szenario stammt aus `data/variants/2026-11-07_gow50-kompromiss` (Regelwerk 0.14.0).
- Die Netzlücken stammen aus `data/interim/cycle_mesh_gaps.parquet`. Sie liegen nur zur Anzeige in EPSG:4326 vor, wie die Prüfdateien in `reports/`.
- Der Ist-Querschnitt im Vergleich ist schematisch, mit angenommenen Breiten (`source_type: assumption`, siehe `shared/steckbrief.js`).
- `window.proto` ist ein Testzugang für `analysis/review_2026_11/ui/prototypes.mjs`.
