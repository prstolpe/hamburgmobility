# Teil B, Paket 2 (Inhalte und Texte) – Arbeitsplan zum Weitermachen

Stand 14.11.2026, Branch `redesign/2026-11-p2-content` (von `redesign/2026-11` nach Merge von Paket 1). Noch kein Code.
Grundlage: `decisions.md` (E1 b, E2 b mit Navigation-Klärung, E3 b, E3b b, E3c b, E4 b, X2 b, X3 b).

## A Export (pipeline, Tests zuerst, dann `make export` zweimal: Determinismus)
1. `pipeline/lib/export_districts.py` → `data/out/districts/<slug>.json`: Kennzahlen je Bezirk und Top-5 (Straßen nach
   Priorität, Knoten nach `priority_rank`, Radnetzlücken nach Länge × Nachfrage). Logik aus `analysis/redesign/district_data.py`.
2. `data/out/cycle_mesh_gaps.geojson` (vereinfacht, EPSG:4326) für die Ansicht „Lücken“.
3. Knoten in die Suche (eigene Datei `search_junctions.json`, `search.json` bleibt unverändert).
4. `docs/redesign/glossary.yaml` → `config/glossary.yaml` (eine Quelle), Export nach `meta.json` (`glossary`).
5. `config/plain_language.yaml`: Kategorienamen und Begründungsbausteine nach Glossar (Texte aus `04_language.md`),
   neue meta.version, CHANGELOG. Download-Texte (`DOWNLOAD_TEXTS` in `s09_export.py`) ebenso.

## B Webseite (vitest zuerst)
1. `state.js`: Seiten karte, bezirke, methode, daten, impressum; `theme`/`view` statt `layer`; alte Parameter und Seiten
   nach Tabelle in `02_information_architecture.md` umschreiben (Test je Zeile).
2. Kopf: 4 Menüpunkte, Impressum/Datenschutz/Lizenzen im Fuß; Kasten „Was ist das?“ beim ersten Besuch (localStorage mit try/catch).
3. Karte: Themen-Umschalter und Ansicht über der Karte (Themen → bestehende Ebenen in `layers.js`, neue Ansicht
   „Dringlichkeit“), Legende links/mobil unter der Karte, Mehr Ebenen und Filter auf Ebene 3, Kreuzungspunkte ab Zoom 14.
4. Steckbrief Straße und Kreuzung in drei Ebenen (Vorlage `prototypes/redesign/shared/profile.js`); E3c ein Merkmal
   „Wie sicher ist das?“; E3b nur „Passt das Ziel?“; X2 „Warum?“ nur zutreffende Gründe; X3 Ist-Radverkehr nur aus
   `cycling.facility.ist_text`.
5. Bezirksseite (Karten, Top-Listen, Tabelle auf Ebene 3), Seite „Daten“ (Downloads + Quellen und Lizenzen).

## C Prüfen und berichten
Builds zweimal, e2e anpassen, axe, Bilder `IMG_PREFIX=p2-`, Lesbarkeit der geänderten Texte, Bericht
`docs/redesign/impl_content.md`, dann Halt für OK.
