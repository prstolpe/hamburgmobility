# Hamburger Straßenfunktionsplan – Starter-Paket (nicht amtlicher Entwurf)

Dieses Paket enthält alles, was Claude Code braucht, um die Pipeline aus `docs/guide.md`
Schritt für Schritt zu bauen. Code wird erst durch die Prompts erzeugt.

## Inhalt

| Datei | Zweck |
| --- | --- |
| `CLAUDE.md` | Projektgedächtnis: Ziel, Konventionen, Qualitätsregeln. Claude Code liest es bei jedem Start. |
| `docs/guide.md` | Vollständige Anleitung (Teile 1–7, Anhänge A–C, Quellen). Fachliche Referenz. |
| `config/rules.yaml` | Regelwerk v0.1.0 (Anhang A). Einzige Quelle für Schwellenwerte. |
| `config/sources.yaml` | Datenquellen (Anhang B). Nur geprüfte Endpunkte, Rest `url: null` + TODO. |
| `overrides/overrides.csv` | Fachliche Korrekturen. Startet leer. |
| `docs/open_questions.md` | Offene fachliche Fragen. Claude trägt hier ein, statt zu raten. |
| `docs/licenses.md` | Lizenz- und Quellenvermerke. |
| `prompts/01_…md` bis `prompts/12_…md` | Die zwölf Prompts in empfohlener Reihenfolge. |

## Kurzanleitung

1. **Voraussetzungen:** Git, Python 3.12, [uv](https://docs.astral.sh/uv/), Claude Code, ca. 10 GB freier Platz.
   Für Prompt 11 (Webseite) zusätzlich Node.js und `tippecanoe`.
2. **Repository anlegen:** Ordner entpacken, `git init`, erster Commit mit genau diesen Dateien.
3. **Pilotbezirk festlegen** (Vorschlag: Altona oder Eimsbüttel) und in `CLAUDE.md` unter „Pilotbezirk“ eintragen.
4. **Vor Prompt 03:** Verkehrsplaner*in prüft `config/rules.yaml` – jede Regel gegen ihre Quelle.
   Werte mit `source_type: assumption` bewusst freigeben oder ändern.
5. **Claude Code im Repository starten** und die Prompts der Reihe nach ausführen (siehe unten).

## Reihenfolge der Prompts

Ja, nacheinander – aber nicht alle in einer Sitzung und nie ohne Prüfschritt.

| Nr. | Datei | Hängt ab von | Prüfung vor dem nächsten Schritt |
| --- | --- | --- | --- |
| 01 | `01_setup.md` | – | `make test` grün |
| 02 | `02_rules.md` | 01 | Fachliche Freigabe des Regelwerks |
| 03 | `03_fetch.md` | 02 | Datenbericht: Anzahl, CRS, Lizenz je Quelle |
| 04 | `04_network.md` | 03 | Längensumme, keine doppelten IDs |
| 05 | `05_conflation.md` | 04 | 50 Stichproben, Trefferquote |
| 06 | `06_features.md` | 05 | Verteilungen, Nullwerte |
| 07 | `07_crosssection.md` | 06 | 50 Transekte im Orthophoto gemessen |
| 08 | `08_classify.md` | 07 | Goldene Fälle grün, Abgleich mit HVS |
| 09 | `09_coherence_overrides.md` | 08 | Flag-Liste fachlich durchgesehen |
| 10 | `10_discrepancy.md` | 09 | Top-30-Liste plausibel |
| 11 | `11_web.md` | 10 | Barrierefreiheit, Mobiltest |
| 12 | `12_validation.md` | 11 | Externe Fachprüfung |

Hinweis: In `docs/guide.md` heißen die Prompts P0–P11. Der Querschnitt (dort P9) läuft hier
**vor** der Klassifikation, weil die GOW30-Regel `C-G30-02` die Straßenraumbreite braucht.
Die Skriptnamen (`s05_classify.py`, `s07_crosssection.py` …) folgen der Nummerierung der
Anleitung; die Ausführungsreihenfolge regelt das `Makefile` über Abhängigkeiten.

## So läuft jeder Schritt

1. Neue Claude-Code-Sitzung starten (frischer Kontext).
2. Planungsmodus einschalten und schreiben: `Führe prompts/03_fetch.md aus.`
3. Plan lesen, mit `docs/guide.md` abgleichen, erst dann freigeben.
4. Nach der Umsetzung: `make test`, Report in `reports/` lesen, Stichproben ansehen.
5. Commit (bei größeren Schritten Pull Request mit fachlichem Review).
6. Fragen, die Claude in `docs/open_questions.md` einträgt, klären, bevor es weitergeht.

Wenn etwas nicht stimmt: nicht still nachjustieren lassen. Regel in `config/rules.yaml` mit
Begründung und neuer Version ändern oder eine Korrektur in `overrides/overrides.csv` eintragen.

## Status

Diskussionsentwurf zivilgesellschaftlicher Akteure. Keine Planung und keine Anordnung der
Freien und Hansestadt Hamburg.

## Webseite (Prompt 11)

Statische Karte mit MapLibre GL JS und PMTiles in `web/` (Vite, Vanilla JS). Daten aus `data/out/` (nicht in Git).

```bash
make validate    # Validierung und Sensitivität (Prompt 12) -> reports/validation.md; vor make export, ca. 1–2 min
make export      # Downloads, Steckbriefe, search.json, table.json, tiles/segments.pmtiles (tippecanoe)
make basemap     # Hintergrundkarte: Protomaps-Ausschnitt, Schriften, Sprites (pmtiles CLI)
make web         # npm ci + vite build -> web/dist
npm --prefix web run preview   # lokal ansehen: http://localhost:4173/
make a11y        # Smoke-Tests und axe-core -> reports/web_accessibility.md (vorher: npx --prefix web playwright install chromium)
```

Einstellungen in `config/project.yaml` unter `web:` (Repository für Rückmeldungen, E-Mail, Kachel-URL). Ohne
`github_repo` und `feedback_email` blendet die Seite den Rückmeldeknopf aus.

### Veröffentlichen (GitHub Pages)

1. Repository auf GitHub anlegen, `web.github_repo` in `config/project.yaml` eintragen, unter Settings → Pages als
   Quelle „GitHub Actions“ wählen.
2. Lokal `make validate export basemap site-data` und `data/site-data.tar.gz` als Asset an das Release `data-latest` hängen
   (Web-Oberfläche oder `gh release upload data-latest data/site-data.tar.gz --clobber`).
3. Push auf `main` startet `.github/workflows/pages.yml`: Tests → Daten aus dem Release → Build → Deployment.
4. Danach `web/scripts/check-range.sh https://<owner>.github.io/<repo>/` (PMTiles brauchen HTTP-Range, Antwort 206).

Später Kacheln auf Cloudflare R2: `web.tiles_base_url` setzen (R2 mit Range und CORS für die Pages-Domain).

## Validierung (Prompt 12)

`make validate` (pipeline/validate.py) schreibt `reports/validation.md` nach guide.md Teil 7: HVS-Abgleich,
Soll-ETW30 gegen Ist-Tempo, Sensitivitätsanalyse (Einzelvariation ±20 % und 500 Monte-Carlo-Läufe mit festem Seed,
Abschnitt `validation` in rules.yaml), Datenqualität je Bezirk, Stand der Stichproben, Grenzen und offene Fragen.
Die Markierung „unsicher“ landet in `data/interim/validation.parquet` und von dort über `make export` auf der Webseite.
