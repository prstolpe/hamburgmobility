# 12 – Validierung und Sensitivität

**Ziel:** Bericht nach docs/guide.md Teil 7 als Grundlage für Review und Veröffentlichung.
**Eingaben:** alle Ergebnisse, config/rules.yaml, Rückmeldungen.
**Ergebnis:** pipeline/validate.py, reports/validation.md.
**Prüfschritt:** externe Fachperson liest den Bericht; offene Punkte in docs/open_questions.md.

## Auftrag

Schreibe pipeline/validate.py und erzeuge reports/validation.md mit:
1. Kreuztabelle Soll × HVS in km, gesamt und je Bezirk, mit Liste der Abweichungen.
2. Abgleich Soll-ETW30 mit Ist-Tempo 30; Ausreißer als mögliche Datenfehler.
3. Sensitivitätsanalyse: jede Schwelle mit source_type assumption einzeln ±20 %;
   zusätzlich 500 Läufe mit zufällig variierten Gewichten (±20 %, Seed festhalten).
   Je Abschnitt Anteil Kategoriewechsel; Markierung „unsicher“ ab Wechselquote 0,3
   (als assumption in rules.yaml ergänzen). Wirkung je Schwelle in km.
4. Datenqualität je Bezirk: Conflation-Trefferquote, OSM-Tag-Vollständigkeit, fehlende DTV.
5. Ergebnisse der manuellen Stichproben (Conflation, Transekte, Klassifikation) zusammengefasst.
6. Grenzen (fachlich, rechtlich, methodisch) nach Teil 7 und Liste offener Fragen.

Speichere die Unsicherheitsmarkierung zurück in den Export, damit die Webseite sie zeigt.
