# 18 – Führungsform und Breite der Radanlagen

**Ziel:** je Straßenabschnitt Soll-Führungsform und Soll-Breite der Radanlage.
**Eingaben:** cat_final, cycle_cat_final, cyc_peak_h, Ist-Radführung, config/cycling_rules.yaml (separation_matrix, cycle_street, widths_m).
**Ergebnis:** pipeline/c05_facility.py, Spalten cycle_facility_soll, cycle_width_soll_m, cycle_facility_ist, facility_gap, rule_trace_facility; reports/cycle_facility.md.
**Prüfschritt:** goldene Fälle aus tests/golden/cycling grün; km je Führungsform Soll vs. Ist; 30 Stichproben je Führungsform.

## Auftrag

Implementiere c05_facility.py:
1. Führungsform aus separation_matrix[cat_final][cycle_cat_final]; bei preferred/fallback zunächst
   preferred, fallback erst in Prompt 19, wenn der Raum nicht reicht (Flag setzen).
2. Fahrradstraße nur, wenn cycle_street-Bedingungen erfüllt sind (Kfz/Tag, Radverkehr dominant);
   sonst Flag „Kfz-Menge reduzieren (Filter) oder Route verlegen“ und vorläufig mixed.
3. Mischverkehr-Regel S-04 prüfen (Kfz/h aus DTV × Spitzenstundenanteil; Annahme dokumentieren).
4. Breite: project_target je Führungsform und Radkategorie, plus intensity_upgrade nach cyc_peak_h;
   nie unter widths_m.de.*.min. Zusätzlich die Vergleichswerte DE-Regelmaß und NL-Hauptnetz mit
   ausgeben (für den Steckbrief).
5. Ist-Führung aus OSM normalisieren (track/lane/shared_lane/no/cycle_street) und facility_gap
   bestimmen (fehlt, zu schmal, falscher Typ).
6. Außerorts (GOW80/ETW60) nach separation_matrix.rural.

Entferne xfail für die Führungsform-Tests. Keine Werte im Code. Report mit Matrix
Straßenkategorie × Radkategorie (km), Lückenliste und Beispielen.
