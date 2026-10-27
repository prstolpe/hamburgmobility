# 08 – Klassifikation

**Ziel:** Soll-Kategorie mit nachvollziehbarer Begründung.
**Eingaben:** features.parquet inkl. Querschnitt, config/rules.yaml, tests/golden/.
**Ergebnis:** pipeline/s05_classify.py, Spalten cat_proposed, confidence, rule_trace (JSON), reports/classification.md.
**Prüfschritt:** alle goldenen Fälle grün; Kreuztabelle Soll × HVS plausibel; 30 Zufallsabschnitte je Kategorie gesichtet.

## Auftrag

Implementiere pipeline/s05_classify.py als Interpreter der Kaskade `classification` in
config/rules.yaml. Die Bedingungen in rules.yaml sind lesbare Pseudo-Ausdrücke: übersetze sie in
einen kleinen, getesteten Ausdrucks-Evaluator oder in Python-Funktionen je Regel-ID – aber halte
die Schwellen ausschließlich in rules.yaml.

- Jede geprüfte Regel liefert (rule_id, passed, inputs); speichere rule_trace als JSON.
- confidence = niedrig, wenn Eingangswerte fehlen oder ein Wert innerhalb ±10 % einer Schwelle
  liegt; mittel bei Fallback-Quellen; sonst hoch (diese Logik als assumption in rules.yaml).
- Entferne die xfail-Markierung der goldenen Fälle; alle müssen grün sein.

Report reports/classification.md: km je Kategorie, Kreuztabelle Soll × HVS in km, Liste der
HVS-Abschnitte, die ETW30 werden, und der Bezirksstraßen, die GOW50 werden, sowie 30
Zufallsabschnitte je Kategorie mit Orthophoto- und Panoramax-Links.

Ändere keine Schwellen, um Tests oder Erwartungen zu erfüllen – frage stattdessen und trage die
Frage in docs/open_questions.md ein.
