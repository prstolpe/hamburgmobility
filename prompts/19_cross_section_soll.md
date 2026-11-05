# 19 – Soll-Querschnitt: Fahrstreifen, Lage der Radwege, Raumaufteilung

**Ziel:** je Straßenabschnitt ein Soll-Profil mit Kfz-Fahrstreifen je Richtung, Lage und Breite der Radanlagen, Gehwegen, ÖPNV, Grün, Laden und Parken – passend in den verfügbaren Straßenraum.
**Eingaben:** Ergebnis Prompt 18, width_p10/width_median aus dem Querschnitt (Prompt 07), DTV, Busfahrten aus GTFS, Straßenbahn, Ist-Fahrstreifen (OSM lanes), config/design_rules.yaml (lanes, placement, cross_section_allocation).
**Ergebnis:** pipeline/c06_cross_section_soll.py, Spalten lanes_per_dir_soll, lanes_per_dir_ist, bus_lane_soll, median_soll, cycle_side, profile_elements (JSON: Reihenfolge, Element, Breite), total_required_m, available_m, fit_class, degrade_steps_applied, rule_trace_profile; reports/cross_section_soll.md; reports/profiles_sample/*.svg.
**Prüfschritt:** goldene Fälle grün; 30 Profile gegen Orthophoto und Straßenbilder geprüft; Verteilung der Abbaustufen D1–D7 plausibel.

## Auftrag

Implementiere c06_cross_section_soll.py:
1. Fahrstreifen nach lanes.rules L-01 bis L-06. Spitzenstunde je Richtung aus DTV mit
   peak_h_dir_from_dtv; fehlt DTV, nimm den Ist-Wert aus OSM lanes und setze confidence niedrig.
   Nie mehr Fahrstreifen als im Ist ohne Override (L-06).
2. Busfahrstreifen nach L-04 aus GTFS (Busse je Spitzenstunde und Richtung, repräsentativer Werktag).
3. Lage nach placement PL-01 bis PL-06; Zweirichtungsradweg nur bei PL-02.
4. Raumaufteilung nach cross_section_allocation.fill_order mit Elementbreiten aus elements_min_m,
   Radbreite aus Prompt 18, Fahrbahnbreiten aus lanes.lane_width_m.
   Verfügbare Breite = width_p10 (Variante „Fassade“ und „Verkehrsfläche“ beide rechnen; Verkehrsfläche
   ist maßgeblich, Fassade zeigt Potenzial inkl. Vorgärten).
5. Passt es nicht: degrade_cascade_if_not_fit Schritt für Schritt anwenden, nach jedem Schritt neu
   prüfen; D5 erzeugt einen Vorschlag zur Kategorieänderung (nicht automatisch übernehmen), D6/D7
   nur als Flag. Jede Stufe im rule_trace_profile.
6. fit_class: fits | fits_after_degrade | does_not_fit.
7. Zeichne für 30 Zufallsabschnitte und die 20 breitesten/engsten ein einfaches Querschnitts-SVG
   (Elemente maßstäblich, beschriftet), das später im Steckbrief der Webseite angezeigt wird.

Entferne xfail für Fahrstreifen-/Profil-Tests. Keine Werte im Code. Report: km je fit_class,
Häufigkeit der Abbaustufen, Fahrstreifenänderungen Ist → Soll in km, Liste der D5/D6/D7-Fälle.
