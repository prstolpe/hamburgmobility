# 22 – Zielszenario: Netz für die Verkehrsverteilung von morgen

**Ziel:** den Soll-Entwurf nicht nur auf die heutigen Verkehrsmengen auslegen, sondern auf ein Zieljahr, in dem Kfz-Verkehr
abnimmt und Radverkehr zunimmt. Regeln mit Mengenbezug lesen wahlweise Ist oder Zieljahr; wo der Entwurf nur mit weniger
Kfz-Verkehr funktioniert, wird das sichtbar („setzt Verkehrsreduktion voraus“), statt es stillschweigend anzunehmen.
**Eingaben:** DTV 2019 (traffic_volumes), Radnachfrage und Radgraph (c01/c02), Soll-Radnetz mit Soll-Widerstand (c03),
cat_final, Soll-Knotentypen (c07); Hamburger Ziele zum Modal Split und Radverkehrsanteil (Quelle ermitteln, source_type
hamburg); Literatur zur Verkehrsverdunstung bei Kapazitätsabbau (Quelle prüfen); optional Prognose-Planfall des
Verkehrsmodells der BVM (Anfrage).
**Ergebnis:** config/scenario.yaml (meta.version, Schema config/schema/scenario_model.py, Loader in pipeline/lib/rules.py),
pipeline/c09_scenario.py, data/interim/scenario.parquet (segment_id bzw. edge_id, dtv_scenario, cyc_day_scenario,
cyc_peak_h_scenario, scenario_trace), reports/scenario.md, docs/data_requests.md (Anfrage an die BVM).
**Prüfschritt:** design_basis = ist reproduziert die heutigen Ergebnisse zu 100 %; goldene Fälle für beide Basen;
jede Szenariogröße hat eine Quelle oder steht als offene Frage in docs/open_questions.md; Sensitivität ±20 % (V-SENS-01).

## Auftrag

1. **Szenario-Regelwerk** config/scenario.yaml: Zieljahr, Modal Split Ist und Ziel (Hamburger Erhebung und Zielbeschluss –
   Werte und Fundstellen ermitteln, nichts erfinden; unbekannt = TODO), Verdunstungsfaktoren je Maßnahme (modaler Filter,
   GOW50 → GOW30, Fahrstreifenabbau) als assumption mit Literaturquelle, `design_basis` je Regel mit Mengenbezug (ist | scenario).
2. **Rad:** Nachfrage aus c02 auf dem Soll-Netz mit Soll-Widerstand umlegen (gleiche Umlegung wie c02, Kosten aus c03) und
   die Erzeugung auf den Zielanteil skalieren. Ergebnis cyc_day_scenario und cyc_peak_h_scenario je Kante.
3. **Kfz, Stufe A:** pauschale Faktoren je Kategorie aus dem Modal-Split-Ziel. **Stufe B (optional, eigener Schritt):**
   Umlegung auf dem Soll-Straßennetz (Soll-Tempo, Durchfahrtssperre auf Fahrradstraßen mit Filter, Fahrstreifen Soll);
   Quelle-Ziel-Matrix aus einem am DTV kalibrierten Schwerkraftmodell wie c02. Ergebnis dtv_scenario je Abschnitt.
   Liegt ein Prognose-Planfall der BVM vor, ersetzt er Stufe A/B.
4. **Regeln mit Mengenbezug** lesen `design_basis`: Fahrradstraße (C-FAC-02), Mischverkehr (S-04), Fahrstreifen (L-02),
   Kreisverkehrsgrenzen (J-01, J-03), Breitenzuschlag (intensity_upgrade), RSV-Auslöser, Flag gow30_dtv_above_profile.
   Erfüllt der Abschnitt bzw. Knoten die Bedingung nur im Zieljahr: Flag `requires_traffic_reduction` mit der Maßnahme,
   die die Reduktion bewirken soll.
5. **Datenanfrage** docs/data_requests.md: Entwurf einer Anfrage an die BVM nach Prognose-Planfällen des Verkehrsmodells
   (DTV je Abschnitt) und nach Signalprogrammen der LSA (für Prompt 23).
6. **Validierung:** c08 um die Szenariofaktoren erweitern (±20 %); Report: km je Kategorie, Fahrradstraßen, Fahrstreifen und
   Knotentypen für Ist und Zieljahr, Liste der Abschnitte mit requires_traffic_reduction, 30 Zufallsstichproben.
7. **Web:** Umschalter „heute | Zieljahr“ für die Radnetz- und Querschnittsebenen; Steckbriefe zeigen beide Werte und das
   Flag; Methodenseite erklärt das Szenario und seine Grenzen in einfacher Sprache.

Keine Schwellen im Code. Szenariowerte sind Setzungen und so zu kennzeichnen; CHANGELOG und meta.version wie bei den
übrigen Regelwerken. CLAUDE.md um config/scenario.yaml und `make scenario` ergänzen.
