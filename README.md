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
