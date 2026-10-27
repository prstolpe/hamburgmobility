# 02 – Regelwerk, Schema, goldene Fälle

**Ziel:** config/rules.yaml wird zu einer geprüften, testbaren Datenquelle.
**Eingaben:** config/rules.yaml (v0.1.0), docs/guide.md Teil 1 und Anhang A.
**Ergebnis:** pydantic-Schema, Loader pipeline/lib/rules.py, tests/test_rules_schema.py, tests/golden/*.geojson.
**Prüfschritt:** Tests grün. Danach prüft eine Verkehrsplaner*in jede Regel gegen ihre Quelle und setzt geprüfte Regeln auf `status: reviewed`.

## Auftrag

config/rules.yaml liegt bereit. Ändere keine Werte darin.
Schreibe in config/schema/ ein pydantic-Modell, das rules.yaml vollständig validiert:
Pflichtfelder source und source_type (swov_crow|de_regelwerk|hamburg|assumption) je Regel,
Einheit bei Zahlen mit Maßangabe, gültige Kategorien, eindeutige IDs.
Schreibe pipeline/lib/rules.py (Laden + Validieren) und tests/test_rules_schema.py.

Lege in tests/golden/ mindestens 12 synthetische Abschnitte (GeoJSON, EPSG:25832) mit allen
Merkmalen an, die die Kaskade braucht, plus erwarteter Kategorie – je Regelpfad mindestens ein Fall:
- Autobahn -> SW
- verkehrsberuhigter Bereich -> ETW_ERF
- HVS mit getrenntem Radweg, width_p10 20 m, keine Schule -> GOW50
- HVS ohne Radweg, width_p10 13 m -> GOW30 (C-G30-02)
- HVS mit Radweg, Schule in 100 m -> GOW30 (C-G30-01)
- Wohnstraße, niedriger conn_score -> ETW30
- außerorts, hoher conn_score -> GOW80
sowie Grenzfälle knapp ober- und unterhalb jeder Schwelle.
Die Tests für die Klassifikation selbst werden in Prompt 08 grün; markiere sie bis dahin als xfail.

Erfinde keine neuen Schwellen. Fehlt etwas, trage es in docs/open_questions.md ein.
