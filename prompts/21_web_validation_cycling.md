# 21 – Webseite erweitern und validieren

**Ziel:** neue Ebenen und Steckbriefe auf hamburgmobility.de; Validierungsbericht für das Radnetz.
**Eingaben:** Ergebnisse der Prompts 15–20, bestehendes web/ und pipeline/s09_export.py, docs/guide_radnetz.md.
**Ergebnis:** erweiterter Export (PMTiles-Layer cycle_network, cycle_facility, cross_section_soll, junctions), Steckbrief-Erweiterung, Methodenseite „Radnetz“, Downloads; pipeline/c08_validate_cycling.py; reports/validation_cycling.md.
**Prüfschritt:** axe-core ohne kritische Fehler; Mobiltest; Dateigrößen der PMTiles vertretbar (Lazy Loading je Ebene); externer Fachreview des Validierungsberichts.

## Auftrag

1. Export: Erweitere s09_export.py um die neuen Layer (Linien: Radnetz-Kategorie, Führungsform
   Soll/Ist, Breite, fit_class, Fahrstreifen Soll/Ist; Punkte: Knotentyp Soll/Ist). Bei großer
   Datenmenge eigene PMTiles-Datei je Themengruppe, damit die Seite schnell bleibt.
2. Web: neue umschaltbare Ebenen „Radnetz (Soll)“, „Radanlagen Soll/Ist“, „Fahrstreifen Soll/Ist“,
   „Querschnitt passt?“, „Knotenpunkte“, „Radnetz Hamburg (amtlich)“ als Vergleich.
   Steckbrief Abschnitt: Radkategorie, Führungsform und Breite (mit DE- und NL-Vergleichswert),
   Lage, Fahrstreifen, Querschnitts-SVG, Abbaustufen in Klartext, Prinzipien-Scores Ist/Soll.
   Steckbrief Knoten: Soll- und Ist-Typ, Radverkehrsführung, Begründung, Zielkonflikte.
   Legenden farbsehschwächen-tauglich mit zusätzlichem Linienstil bzw. Symbolform.
3. Methodenseite „Radnetz“ in einfacher Sprache aus docs/guide_radnetz.md, inklusive der fünf
   Prinzipien und der Grenzen. Hinweis „nicht amtlicher Entwurf“ auch auf den neuen Ebenen.
4. Validierung c08_validate_cycling.py → reports/validation_cycling.md:
   - Vergleich Soll-Radnetz vs. amtliches Radnetz Hamburg (km, Überdeckung, Abweichungen je Bezirk);
   - Modell vs. Zählstellen;
   - Sensitivität: alle assumption-Werte in cycling_rules.yaml und design_rules.yaml ±20 %, Anteil
     Abschnitte mit geänderter Führungsform/Fahrstreifenzahl und Knoten mit geändertem Typ;
   - Stichprobenergebnisse aus Prompts 18–20;
   - offene Fragen und Grenzen.
5. GitHub-Pages-Deployment wie bisher; prüfe, dass die neuen PMTiles per HTTP-Range ausgeliefert werden.
