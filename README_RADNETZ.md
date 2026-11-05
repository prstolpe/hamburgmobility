# Radnetz-Erweiterung – Kurzanleitung

Diese Dateien in das bestehende Repository kopieren (gleiche Ordnerstruktur, nichts wird überschrieben):

| Datei | Zweck |
| --- | --- |
| `config/cycling_rules.yaml` | Radnetzkategorien, fünf Prinzipien als Prüfregeln, Trennungsmatrix, Breiten |
| `config/design_rules.yaml` | Fahrstreifen, Lage der Radanlagen, Raumaufteilung, Knotenpunkte |
| `docs/guide_radnetz.md` | Methodik mit Quellen ([F]/[B]) |
| `docs/open_questions.md` | offene Fragen im Abschnitt „Radnetz (Prompt 14)“ |
| `prompts/14_…` bis `prompts/21_…` | acht Claude-Code-Prompts |

## Reihenfolge

| Nr. | Prompt | Prüfung vor dem nächsten Schritt |
| --- | --- | --- |
| 14 | Einrichtung, Schemas, Daten | Fachliche Freigabe beider YAML-Dateien |
| 15 | Radverkehrsnachfrage | Modell vs. Zählstellen plausibel |
| 16 | Radnetz entwerfen | Karte vs. amtliches Radnetz, Ortskundige |
| 17 | Fünf Prinzipien prüfen | Kennzahlen, 20 Routen gesichtet |
| 18 | Führungsform und Breite | goldene Fälle, Stichproben |
| 19 | Soll-Querschnitt und Fahrstreifen | 30 Profile im Orthophoto |
| 20 | Knotenpunkte | 30 Knoten je Typ geprüft |
| 21 | Webseite und Validierung | Barrierefreiheit, Fachreview |

Wie bisher: eine Sitzung je Prompt, Planungsmodus, erst Tests, dann Code, dann Report, dann Commit.
Start in Claude Code: `Führe prompts/14_cycling_setup.md aus.`

Haltepunkte, an denen Menschen entscheiden:
- nach 14: Werte mit `source_type: assumption` freigeben (vor allem Breiten, Kreisverkehrs- und Fahrstreifenschwellen);
- nach 16: Radnetz mit Bezirksgruppen und Ortskundigen durchsehen, Korrekturen in `overrides/cycle_network_overrides.csv`;
- nach 19: D5–D7-Fälle (Kategorieänderung, Kfz-Filter, Routenverlegung) fachlich entscheiden;
- nach 20: Knoten mit Zielkonflikten (Vorrang am Kreisverkehr, Platzbedarf) einzeln prüfen.

Prompt 17 kann nach 20 noch einmal laufen, damit die Soll-Bewertung die Soll-Knoten nutzt.
