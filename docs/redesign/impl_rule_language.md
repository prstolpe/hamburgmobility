# Redesign 2026-11 · Teil B, Paket 4: Sprache der Regeldateien

Branch `redesign/2026-11-p4-rule-language` (von `redesign/2026-11`). Umgesetzt ist **E5 c**: Klartext-Felder und ein
Feld `history`, **ohne Änderung der Bedeutung**. Neue Patch-Versionen: rules.yaml 0.21.1, cycling_rules.yaml 0.11.2,
design_rules.yaml 0.9.1 (CHANGELOG). Nicht live.

## Was sich ändert

| | Umfang | Quelle |
|---|---|---|
| `label_plain`, `explain_plain`, `why` | alle 196 Regeln | `analysis/redesign/rule_plain.yaml` |
| `label_plain`, `explain_plain` | 7 Kategorien (gleich dem Glossar, Test) | ebenda, `config/glossary.yaml` |
| `label_plain` | 58 Schwellen unter `thresholds` | ebenda |
| `history` (Liste) | 60 Regeln: Versionsgeschichte aus `description`/`note` verschoben | `analysis/redesign/rule_history.yaml` |
| Schema | die vier Felder sind optionaler Text (`config/schema/rules_model.py`), `provenance.py` behandelt sie als Text | – |
| Export | Hinweis für Radfahrende im Kreuzungs-Steckbrief aus `explain_plain` von JC-01…JC-06; damit keine Kürzel mehr auf Ebene 2 (Rest aus Paket 2) | `pipeline/lib/export_cycling.py` |
| Glossar | oberste Radnetzstufe „Radvorrangroute“ statt „Radschnellweg“ (keine Radschnellverbindung nach FGSV) | `config/glossary.yaml` |

**Wie die Texte entstanden sind:**

- `label_plain` und `explain_plain` habe ich in A5 geschrieben.
- `why` hat für 10 Regeln in A5 ich geschrieben. Für die übrigen 186 hat ein Agent einen Entwurf geschrieben, den ein
  zweiter Agent Regel für Regel gegen den Eintrag in der Regeldatei geprüft hat.
  - Geändert wurden 145 Texte in 128 Regeln. Das Protokoll mit alt, neu und Grund liegt in
    `data/scenarios/redesign/why_review.md`.
  - Die häufigsten Gründe: nicht belegte Sicherheits- oder Komfortbehauptungen; Annahmen, die wie belegte Tatsachen
    klangen (jetzt: „Das Projekt hat diesen Wert gesetzt; er wird noch geprüft.“); falsche oder unvollständige
    Bedingungen (z. B. C-FAC-02 „mindestens so viele Räder wie Autos“, S-CONF-02 Zonen sind Linien).
- Die Geschichtsfelder hat ein Agent vorgeschlagen. Ich habe sie mit einem Skript übernommen, das beweist, dass sich
  außer diesen Texten nichts ändert (unten). 6 Regeln mit bloßen Verweisen auf offene Fragen bleiben unverändert.

**Lesbarkeit der neuen Felder:**

| Feld | Wiener Sachtextformel | Flesch-Amstad | Ø Satzlänge |
|---|---:|---:|---:|
| `explain_plain` | 7,1 | 62,7 | 10,7 |
| `why` | 6,0 | 69,6 | 8,0 |
| zum Vergleich: technische `description` | 11,7 | 34,7 | – |

**Beispiel (C-G30-02):**

```diff
   - id: C-G30-02
+    label_plain: "Tempo 30, wenn Platz für den Radweg fehlt"
+    explain_plain: "Ist die Straße zu schmal für Tempo 50 mit Radweg, wird es Tempo 30."
+    why: "Bei Tempo 50 braucht das Rad einen getrennten Radweg. Passt er nicht in die Straße, ist Tempo 50 nicht sicher zu gestalten."
     description: "GOW30-Auslöser b: 50 nicht sicher gestaltbar (kein ausreichender getrennter Radweg möglich)"
     …
     note: >-
-      Seit 0.18.0 (F06): nur über den Raum. Ein vorhandener Radweg zählt nicht (CROW-Auslöser b fragt, ob ein …
+      Nur über den Raum. Ein vorhandener Radweg zählt nicht (CROW-Auslöser b fragt, ob ein ausreichender Radweg …
+    history:
+      - "seit 0.18.0 (F06): nur über den Raum"
```

## Nachweis: keine Änderung der Bedeutung

1. **Vor dem Schreiben** (`analysis/redesign/apply_rule_language.py`, `assert`): Jede Regeldatei lädt ohne die neuen
   Schlüssel und mit den alten `description`/`note` der 60 Geschichtsregeln zu genau demselben Objekt wie vorher. Die
   neuen Texte stehen genau wie vorgegeben in der Datei.
2. **Tests:** `tests/test_rule_language.py` (Tests zuerst) prüft, dass jede Regel die drei Felder hat, ohne Kürzel,
   Regel-IDs und Variablennamen, mit Längengrenzen. Außerdem: Kategorien gleich dem Glossar, alle 58 Schwellen mit
   `label_plain`, Regeldateien gültig. `make test`: grün (1750 Python-Tests bestanden, 2 erwartet fehlschlagend; 102 Web-Tests bestanden).
3. **Volle Neurechnung** im Worktree ab der ersten Stufe (`make rerun FROM=network`) mit den geänderten Regeldateien
   (vor dem Erhöhen der Versionsnummern, die in Spalten der Validierung stehen). Verglichen werden alle Dateien in
   `data/interim` mit dem Basislauf:

<!-- table:p4_proof -->
| Datei (data/interim) | Zeilen | Datei-Hash gleich | Spalten mit Unterschied (Zeilen) |
|---|---|---|---|
| classified.parquet | 36526 | ja | – |
| coherence.parquet | 36526 | ja | – |
| coherence_areas.parquet | 3195 | ja | – |
| coherence_nodes.parquet | 5061 | ja | – |
| cross_section_soll.parquet | 36526 | ja | – |
| crosssection.parquet | 36526 | ja | – |
| cycle_edges.parquet | 65973 | ja | – |
| cycle_facility.parquet | 36526 | ja | – |
| cycle_graph.parquet | 65973 | ja | – |
| cycle_mesh_gaps.parquet | 441 | ja | – |
| cycle_network.parquet | 65973 | ja | – |
| cycle_principles.parquet | 33913 | ja | – |
| cycle_routes.parquet | 4936 | ja | – |
| discrepancy.parquet | 36526 | ja | – |
| features.parquet | 36526 | ja | – |
| final.parquet | 36526 | ja | – |
| harmonised.parquet | 36526 | ja | – |
| ist_facility.parquet | 36526 | ja | – |
| junctions.parquet | 16244 | ja | – |
| segments.parquet | 36526 | ja | – |
| segments_conflated.parquet | 36526 | ja | – |
| transects.parquet | 219291 | ja | – |
| validation.parquet | 34702 | ja | – |
| validation_cycling.parquet | 52770 | ja | – |
<!-- /table:p4_proof -->

**Ergebnis:** Alle 24 Dateien sind Byte für Byte gleich (Datei-Hash gleich, 0 Spalten mit Unterschied). Die neuen Felder ändern nur Texte, kein Ergebnis. Danach `make validate` und `make export-cycling` mit den neuen Versionsnummern: Der Basislauf reproduziert Kategorie, Priorität, Führungsform, Fahrstreifen und Knotentyp zu 100 %.

## Offen

- **Klarere Formulierungen** der technischen Felder (5 Beispiele in `05_rule_language.md`) sind nicht umgesetzt: Sie
  waren Vorschlag, aber nicht Teil der gewählten Option c. Bei Bedarf als eigener Schritt.
- **Regelreferenz auf der Webseite:** Sie folgt in Paket 3 (Methode) und liest diese Felder.
- Die `why`-Texte sind geprüft, aber nicht fachlich freigegeben. Sie stehen mit den Regeln weiter auf `status: draft`.
