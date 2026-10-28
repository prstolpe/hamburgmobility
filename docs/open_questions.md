# Offene Fragen

Format: `- [ ] Frage – Wer klärt – Status/Antwort`. Claude Code trägt hier ein, statt zu raten.

## Fachlich (Regelwerk)
- [ ] Gehwegbreite 2,50 m und Fahrbahnbreite 6,50 m (zwei Fahrstreifen, Begegnung Lkw/Bus) am Original der RASt 06 prüfen – Verkehrsplaner*in
- [ ] RIN-Kategoriengruppen und RASt-Entwurfssituationen je Kategorie am Original prüfen (Teil 1.3) – Verkehrsplaner*in
- [ ] Schwellen mit `source_type: assumption` freigeben: conn_gow 0,6; sensitive_radius 150 m; frontage 0,4; N2 200 m; N3 25 ha; N4 300 m; Machbarkeitsklassen 0,85/1,0 – Verkehrsplaner*in
- [ ] Gewichte conn_score, place_score und Priorisierung festlegen – Verkehrsplaner*in
- [ ] Stand der FGSV-Neufassungen (RASt, ERA, EFA) vor jedem Release prüfen – Team

## Regelwerk-Datei (Befunde aus Prompt 02, Schema-Prüfung von rules.yaml 0.1.0)
- [ ] `crossing_demand == high` (C-G30-01) ist nicht definiert: Woraus wird der Querungsbedarf abgeleitet, welche Stufen gibt es, ab wann „high“? Goldene Fälle nutzen vorerst „high“/„low“ als Eingabe – Verkehrsplaner*in
- [ ] Fehlende Werte in der Kaskade: Was gilt, wenn z. B. keine Schule/Kita im Umkreis liegt (`schools_or_kitas_within_m` leer) oder `width_p10_m` fehlt? Goldene Fälle nutzen vorerst explizite Werte (600 m) – Verkehrsplaner*in (Klärung vor Prompt 08)
- [ ] C-G30-02 vergleicht immer mit `required_width.GOW50` (16,50 m). Soll auf Busrouten `GOW50_bus` (17,00 m) gelten? – Verkehrsplaner*in
- [ ] `required_width.sidewalk_m` und `carriageway_2lane_m` führen in `status` Freitext („am Original prüfen“) statt draft/reviewed/approved. Vorschlag: status: draft + Text in `note` (neue Version nötig) – Methodik
- [ ] Netzregeln N1–N6 haben kein Feld `status` (CLAUDE.md verlangt status je Regel). Ergänzen? – Methodik
- [ ] `requirements.GOW30.profiles.*.max_dtv` ohne Einheit; das Schema nimmt Kfz/24h an. Einheit in rules.yaml ergänzen? – Methodik
- [ ] Gewichte in `scores` und `priority.risk_weights` tragen `source_type: assumption` nur als Kommentar. Als Feld ergänzen? – Methodik
- [ ] Teil 1.7 verlangt Quellen mit Seitenangabe; rules.yaml hat keine Seitenangaben – Verkehrsplaner*in
- [ ] Merkmalsnamen in guide.md 3.3 (`width_median_m`, `separated_cycle_track_feasible`) weichen von rules.yaml ab (`width_p10_m`, `separated_cycle_track_present`). Pipeline folgt rules.yaml; guide.md angleichen? – Methodik

## Netz und Segmentierung (Prompt 04, rules.yaml 0.2.0)
- [ ] Schwelle S-NET-03 freigeben: Abschnitte erst ab 400 m bei maxspeed-Wechsel teilen (Annahme aus guide.md 3.2) – Verkehrsplaner*in
- [ ] guide.md 3.2 nennt auch Querschnittswechsel als Teilungsgrund. Querschnittsdaten gibt es erst nach Prompt 07; soll danach neu segmentiert werden (ändert segment_id)? – Methodik
- [ ] Fehlendes maxspeed gilt bei S-NET-03 nicht als Wechsel (50 → unbekannt → 50 wird nicht geteilt, 50 → unbekannt → 30 schon). Passt das? – Methodik
- [ ] highway-Klassen: *_link mitführen (derzeit ja)? highway=road, busway nicht enthalten – richtig? – Methodik
- [ ] Viele sehr kurze Abschnitte an Knoten mit getrennten Richtungsfahrbahnen (P10 ca. 10–17 m bei primary/secondary/tertiary). Getrennte Fahrbahnen bleiben getrennte Abschnitte; für Klassifikation und Kohärenz zusammenfassen? – Methodik

## Conflation (Prompt 05, rules.yaml 0.3.0)
- [ ] Schwellen S-CONF-01/02 freigeben: Puffer 15 m, Winkel 20°, Überdeckung 60 %, Zonen-Längenanteil 50 % (Startwerte, per Stichprobe reports/conflation_sample.csv kalibrieren) – Verkehrsplaner*in
- [ ] Definition match_quality: exact = Abschnitt zu ≥ 60 % von gültigen amtlichen Linien überdeckt, partial = weniger, none = keine. Passt das? – Methodik
- [ ] `in_hvs` stammt aus den DTV-Linien HVS 2019 statt aus der HVS-Karte 2023. Bis HH-SIB wieder erreichbar ist oder die Karte digitalisiert ist: Abweichungen 2019 → 2023 bekannt? – GIS
- [ ] `in_hvs` nur bei match_quality exact. Sollen auch partial-Treffer zählen? – Methodik
- [ ] Mehrdeutige zeitlich begrenzte Regelungen: „30 km/h 22 - 6 h Lärmschutz“ mit Feld geschwindigkeit = 30 (Regeltempo unbekannt) und „… sonst 50km/h“ mit geschwindigkeit = 50 (begrenztes Tempo unbekannt). Was ist das Regeltempo? – GIS
- [ ] „5-7 km/h“ (verkehrsberuhigt), „Verkehrsbeeinflussungsanlage“ und „Autobahn-Auffahrt ohne explizite Geschwindigkeitsbegrenzung“ ergeben kein Zahl-Tempo (`speed_official_kmh` leer, Text in `speed_official_text`). Für Prompt 10 einen Rechenwert festlegen? – Methodik
- [ ] Abschnitte über einen Namenswechsel hinweg (z. B. „Sperlingsweg / Bayernweg“, bis ca. 1 km): S-NET-02 teilt nur bei highway-Wechsel. Auch bei Namenswechsel teilen (ändert segment_id)? – Methodik
- [ ] Fußgängerzonen (highway=pedestrian) sind in den Tempo-/Widmungsebenen meist nicht enthalten (86 % none) – amtliche Quelle für Fußgängerzonen? widmung_flaeche („für den Fußgängerverkehr“) nutzen? – GIS

## Daten
- [ ] Führt HH_WFS_Strategisches_Strassennetz ein Attribut „Hauptverkehrsstraße“ mit Stand 2023? – GIS
- [x] Welche Jahrgänge enthält api.hamburg.de/datasets/v1/verkehrsmengen (DTV Hauptverkehrsstraßen)? – GIS – 2026-10-28: dtv_hvs_2019, dtvw_hvs_2014, dtv_bab_2019, dtvw_bab_2013 (siehe reports/data_report.md)
- [ ] Gibt es Kfz-Zählungen auf Bezirksstraßen? Transparenzanfrage an Bezirksämter – Team
- [ ] Dienst-URL für „Radnetz Hamburg“ im Geoportal – GIS
- [ ] Endpunkte für Schulen, Kitas, Lärmkarten, Laserscan, Baumkataster, ALKIS-Download – GIS
- [ ] Abdeckung Hamburgs im Unfallatlas je Jahr – GIS
- [ ] Gibt es amtliche Flächen für Fahrbahn/Radweg/Gehweg (LSBG, Bezirke)? Transparenzanfrage – Team
- [ ] Lizenzen der OGC-API-Datensätze (api.hamburg.de) auf den Landing Pages prüfen – GIS
- [ ] HH_WFS_Strategisches_Strassennetz liefert seit 2026-10-28 HTTP 404 (Dataport-Fehlerseite). Neue Dienst-URL ermitteln (Geoportal/Transparenzportal); wird für die Conflation (Prompt 05) gebraucht – GIS
- [ ] DB Rad+ (api.hamburg.de/datasets/v1/dbradplus, jahr2025): Abfrage mit bbox bricht reproduzierbar ab (HTTP 200, abgeschnittenes JSON bei offset 10000/11000). Fehler an die Urban Data Platform melden; danach erneut `make fetch` – Team
- [ ] Lizenz fehlt in der API für „Zulässige Höchstgeschwindigkeiten“ und „Verkehrsmengen“ sowie in GetCapabilities von „Ruhige Gebiete“ – GIS
- [ ] Verkehrsmengen auf Hauptverkehrsstraßen liegen in der API nur bis 2019 (DTV) vor. Gibt es neuere Zählungen? – GIS
- [ ] Direkter Download-Link für das Zensus-2022-Gitter (100 m, Bevölkerung) in sources.yaml eintragen; bisher nur die Übersichtsseite – GIS
- [ ] Linkformat für Orthophoto (Geoportal Hamburg) und Panoramax in den Stichproben-Reports festlegen; bisher nur OSM-Links – Team
- [ ] SensorThings (iot.hamburg.de): 3.137 Locations im Arbeitsgebiet, gemischte IoT-Daten. Welche Things sind Kfz-/Rad-Zählstellen (Filterkriterium)? – GIS

## Rechtlich / Veröffentlichung
- [ ] ODbL-Pflichten bei Kombination OSM + amtliche Daten juristisch prüfen lassen – Team
- [ ] Rückmeldekanal und Datenschutz (GitHub-Issues, Formular) festlegen – Team
