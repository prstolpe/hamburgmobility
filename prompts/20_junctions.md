# 20 – Knotenpunkte: Soll-Knotentyp für jede Kreuzung

**Ziel:** für jeden Knoten des Straßen- und Radnetzes einen Soll-Knotentyp mit Radverkehrsführung.
**Eingaben:** Knoten aus dem Netzgraphen, Arme mit cat_final, cycle_cat_final, Führungsform; DTV der Arme; LSA-Ist (OSM highway=traffic_signals, junction=roundabout); Straßenbahn; Raum am Knoten; config/design_rules.yaml (junctions).
**Ergebnis:** pipeline/c07_junctions.py, data/interim/junctions.parquet (Punktgeometrie): node_id, legs, junction_type_soll, junction_type_ist, cyclist_treatment, conflict_flags, confidence, rule_trace_junction; reports/junctions.md.
**Prüfschritt:** goldene Knotenfälle grün; 30 Knoten je Soll-Typ im Orthophoto geprüft; Abgleich mit N6 aus dem Straßenfunktionsplan.

## Auftrag

Implementiere c07_junctions.py:
1. Knoten bilden: Netzknoten mit Grad ≥ 3 sowie Kreuzungen eigenständiger Radwege mit Straßen.
   Komplexe Knoten (mehrere nahe Netzknoten, z. B. zweibahnige Straßen, Kreisverkehre) zu einem
   Knoten clustern (Radius als assumption in design_rules.yaml, Start 25 m).
2. Arme beschreiben: Kategorie, Radkategorie, Führungsform, DTV; entering_dtv_sum = Summe der
   zufließenden Tagesmengen (Annahme: Hälfte des Querschnitts-DTV je Arm; dokumentieren).
3. Raum: space_radius_m aus den Straßenraumflächen um den Knoten (größter einbeschriebener Kreis in
   der ALKIS-Verkehrsfläche).
4. Entscheidungstabelle J-01 bis J-11 anwenden; Kategoriepaar = die beiden ranghöchsten Arme.
   Ausnahmen und fehlende Werte als conflict_flags.
5. Radverkehrsführung JC-01 bis JC-05 zuordnen (z. B. umlaufender Radweg mit/ohne Vorrang,
   geschützte Kreuzung, aufgepflasterte rote Furt, Mittelinsel). Den Zielkonflikt JC-01
   (CROW-Vorrang vs. SWOV-Befund, deutsches Recht) im Steckbrieftext offen benennen.
6. junction_type_ist aus OSM ableiten; Abweichung Soll/Ist als Handlungsbedarf.
7. Korrekturebene overrides/junction_overrides.csv anwenden (nur approved).

Entferne xfail für Knotentests. Keine Schwellen im Code. Report: Anzahl je Soll-Typ und Ist→Soll-
Übergangsmatrix, Top-30 Knoten nach Priorität (Radunfälle, Radkategorie, Diskrepanz), Liste der
Grade-Separation-Vorschläge.
