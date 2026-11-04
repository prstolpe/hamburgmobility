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
- [x] Fehlende Werte in der Kaskade: Was gilt, wenn z. B. keine Schule/Kita im Umkreis liegt (`schools_or_kitas_within_m` leer) oder `width_p10_m` fehlt? Goldene Fälle nutzen vorerst explizite Werte (600 m) – Verkehrsplaner*in (Klärung vor Prompt 08) – 2026-10-28: C-MISS-01 (dreiwertige Logik, Defaults für Merkmale ohne Quelle), rules.yaml 0.8.0
- [ ] C-G30-02 vergleicht immer mit `required_width.GOW50` (16,50 m). Soll auf Busrouten `GOW50_bus` (17,00 m) gelten? – Verkehrsplaner*in
- [ ] `required_width.sidewalk_m` und `carriageway_2lane_m` führen in `status` Freitext („am Original prüfen“) statt draft/reviewed/approved. Vorschlag: status: draft + Text in `note` (neue Version nötig) – Methodik
- [x] Netzregeln N1–N6 haben kein Feld `status` (CLAUDE.md verlangt status je Regel). Ergänzen? – Methodik – 2026-10-28: status draft ergänzt (rules.yaml 0.9.0)
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

## Merkmale (Prompt 06, rules.yaml 0.4.0)
- [ ] Standardtempo je highway-Klasse für die Reisezeit (S-FEAT-02: motorway 100, trunk 70, residential 30, living_street 7, übrige 50 km/h) freigeben. Betrifft 5,5 % der Abschnitte im Arbeitsgebiet – Verkehrsplaner*in
- [ ] Puffer freigeben: Gebäudedichte 50 m, Einwohner 100 m, Publikumsnutzung 20 m, Knoten-Fangradius 1 m (S-FEAT-03/04/05/10) – Verkehrsplaner*in
- [ ] Betweenness ungerichtet, weil die Abschnitte keine Einbahn-Information tragen; Zufahrtsbeschränkungen (access, motor_vehicle) werden nicht berücksichtigt. Reicht das, oder oneway/access in s02 mitführen? – Methodik
- [ ] Autobahnen fahren keine Busse; seit rules.yaml 0.5.0 zählt das als 0 und senkt ihren conn_score (Median 0,60 → 0,52). Für C-SW-01 ohne Wirkung; soll bus_trips_weekday auf Autobahnen nicht gewertet werden (Gewicht umlegen)? – Methodik
- [ ] Normierung über das Arbeitsgebiet (Eimsbüttel + 500 m): Werte ändern sich, wenn das Gebiet wächst. Bei Ausweitung auf ganz Hamburg über die ganze Stadt normieren? – Methodik
- [ ] DTV liegt nur für Hauptverkehrsstraßen vor (19 % der Abschnitte); `dtv_norm` rangiert nur innerhalb der HVS, alle übrigen Abschnitte bekommen das Gewicht umgelegt. Fehlendes DTV auf Nebenstraßen als „niedrig“ werten? – Verkehrsplaner*in
- [x] ALKIS liegt seit sources.yaml 0.1.4 vor: Gebäudedichte und Publikumsnutzung auf ALKIS umstellen? – 2026-10-28: umgestellt (rules.yaml 0.6.0)
- [ ] Listen alkis_public_functions / alkis_ancillary_functions (S-FEAT-05) fachlich prüfen, v. a. „Gemischt genutztes Gebäude mit Wohnen“ (707 Gebäude) und „Bürogebäude“ (nicht gezählt). Mit ALKIS steigt der Anteil der Abschnitte mit shop_frontage_share ≥ 0,4 (C-G30-01) von 17 % auf 27 % – Verkehrsplaner*in
- [ ] shop_frontage_share bei wenigen Gebäuden instabil (1 von 1 = 1,0, z. B. Deckel Schnelsen). Mindestzahl Gebäude im Puffer, sonst null? – Methodik
- [ ] Publikumsnutzung: Definition (Anteil Gebäude statt Fassadenlänge, Geschoss der POIs nicht geprüft) und Liste `amenity_excluded` prüfen; ALKIS-Gebäudefunktion ergänzen, sobald ALKIS vorliegt – Methodik
- [ ] `outside_builtup_area` (C-RUR-01) hat keine Datenquelle (Ortsgrenze/Ortstafeln). Quelle festlegen; in Eimsbüttel vermutlich überall innerorts – GIS
- [ ] OSM-Gestaltungsmerkmale ohne Tag bleiben null (z. B. centre_line 84 %, parking 57 %, lanes 53 % null). Für die Diskrepanz (Prompt 10) fehlende Tags als „nein“ werten oder als unbekannt? – Methodik
- [ ] `access_motor_only` = motorway/motorway_link oder motorroad=yes, sonst nein (nicht null, weil motorroad nur positiv erfasst wird). Passt das? – Methodik
- [x] Zensus-Gitter: direkte Download-URL und Spaltennamen prüfen – 2026-10-28: Zensus2022_Bevoelkerungszahl.zip (destatis.de), Spalten laut Datensatzbeschreibung im ZIP, sources.yaml 0.1.3
- [x] GTFS HVV: Download-URL in sources.yaml eintragen – 2026-10-28: Transparenzportal, Fahrplan 2026-04-08 bis 2026-12-12, sources.yaml 0.1.3
- [x] Gleiche Werte im Perzentilrang (S-FEAT-01) bekommen den mittleren Rang. – 2026-10-28: geändert auf kleinsten Rang (rules.yaml 0.5.0). Ursprünglich: Folge: Abschnitte ohne Bus (70 %) erhalten bus_trips_weekday_norm 0,35 statt 0; ähnlich Sackgassen bei der Betweenness. Vorschlag: Bindungen mit dem kleinsten Rang (Wert 0 → Norm 0); ändert conn_score und braucht rules.yaml 0.5.0 – Methodik
- [ ] GTFS-Fahrplanperiode endet 2026-12-12; danach neuen Datensatz wählen. Repräsentativer Werktag des aktuellen Feeds: 2026-04-29 (Mi). Getrennte Richtungsfahrbahnen erhalten nur die Fahrten ihrer Richtung – Team

## Querschnitt (Prompt 07, rules.yaml 0.7.0)
- [ ] 50 Transekte im DOP20 messen (reports/transect_sample.geojson) und in reports/transect_measurements.csv eintragen; Ziel mittlere absolute Abweichung < 1 m (Annahme) – GIS
- [ ] 39 % der Abschnitte (14 % der Länge) haben keine Breite: v. a. kurze Abschnitte, deren Transekte alle innerhalb 20 m eines Knotens liegen (30,8 % der Transekte verworfen). Was gilt in C-G30-02 ohne width_p10_m? Breite vom Nachbarabschnitt gleichen Namens übernehmen? – Methodik
- [ ] GOW30_narrow ist ein Bereich (10,80–13,40 m); die Machbarkeit nutzt die Untergrenze (range_reference: min). Passt das? – Verkehrsplaner*in
- [ ] Variante Verkehrsfläche: ALKIS „Weg“ umfasst auch Parkwege; „Strassenverkehr“-Flurstücke enthalten Böschungen und Grün. Fassade ist offen bei 40,6 % der Transekte (kein Gebäude in 40 m auf einer Seite). Breite für Straßen am Park/Bahndamm nur einseitig begrenzt – Methodik
- [ ] Getrennte Richtungsfahrbahnen: beide OSM-Abschnitte messen dieselbe Straßenraumbreite (ganzes Flurstück). Für die Klassifikation gewollt? – Methodik
- [ ] reports/transect_sample.geojson ist in EPSG:4326 (GeoJSON-Standard), obwohl laut CLAUDE.md nur die Exportstufe nach 4326 transformiert. Für Prüf-Dateien in reports/ zulassen? – Team

## Klassifikation (Prompt 08, rules.yaml 0.8.0)
- [ ] C-MISS-01 und C-CONF-01 fachlich freigeben (Defaults outside_builtup_area = false, override_school_street = false, crossing_demand = not_assessed; Liste der Fallback-Quellen). Folge: Nur SW erreicht „hoch“ (5 % der Länge), 85 % sind „mittel“, solange Ortsgrenze, Schulstraßen-Overrides, HVS-Karte 2023 und amtliche Schulen/Kitas fehlen – Verkehrsplaner*in
- [ ] `shop_frontage_share` ist leer, wenn kein Gebäude im 20-m-Puffer liegt (236 von 367 GOW50-Abschnitten, meist kurze Knotenstücke). C-G30-01 ist dort unbekannt → GOW50 mit confidence niedrig. Ohne Gebäude als 0 werten (S-FEAT-05 ändern) oder Wert vom Nachbarabschnitt übernehmen? – Methodik
- [ ] HVS in Eimsbüttel: 45,6 km GOW30 gegenüber 29,9 km GOW50 (60 % der HVS-km werden GOW30), fast immer über C-G30-01 (Schule/Kita ≤ 150 m bei 443, Publikumsnutzung ≥ 0,4 bei 386 von 600 GOW30-Abschnitten, Mehrfachnennung). Plausibel, oder sind sensitive_radius/frontage zu weit? (Schwellen nicht geändert) – Verkehrsplaner*in
- [ ] „Bezirksstraßen, die GOW50 werden“ (17 Abschnitte, 0,6 km) sind kurze primary/tertiary-Stücke, vermutlich Lücken im HVS-Abgleich (in_hvs nur bei match exact). Definition im Report: Bezirksstraße = in_hvs false und keine Autobahn. Passt das? – Methodik
- [ ] Durchsicht der Stichprobe (reports/classification_sample.csv, bis zu 30 Abschnitte je Kategorie in Eimsbüttel) im Orthophoto und in Panoramax; Fehlerrate je Kategorie in den Report – Verkehrsplaner*in
- [ ] guide.md 3.4 nennt die Spalte `cat_confidence`, prompts/08 und die Pipeline `confidence`. guide.md angleichen? – Methodik

## Netzkohärenz und Korrekturebene (Prompt 09, rules.yaml 0.9.0)
- [ ] Neue Annahmen freigeben: N1 Stadtgrenze ≤ 50 m, N2 Straßenzug ≤ 30° Richtungsänderung (Richtung über 15 m), N6 Ampel/Plateau im Umkreis 30 m – Verkehrsplaner*in
- [ ] N3: Schwelle für „sehr lange Grenze im Verhältnis zur Fläche“ fehlt (guide.md 1.5). Kompaktheit 4π·A/U² wird berichtet; ab welchem Wert markieren? – Verkehrsplaner*in
- [ ] N3: Flächen ohne ETW-Abschnitt (Verkehrsinseln, Grünflächen) gelten nicht als Aufenthaltsbereich. Bahn, Gewässer und Parks als Grenzen ergänzen? – Methodik
- [ ] N4: 29 % der OD-Paare im GOW/SW-Netz haben einen kürzesten Weg mit > 300 m ETW (1 082 ETW-Abschnitte, 112 km), weil GOW30 und ETW30 dasselbe Soll-Tempo haben. Soll N4 nur bei Zeitvorteil über einer Schwelle oder ab einer Mindestzahl OD-Paare markieren? Einbahnstraßen/Abbiegeverbote fehlen – Verkehrsplaner*in
- [ ] N4: 73 000 OD-Paare sind nur über ETW verbunden (Lücken im GOW/SW-Netz). Als eigenes Flag ausweisen? – Methodik
- [ ] N5: Ob an einem Übergang GOW→ETW oder GOW50→GOW30 eine Torsituation vorhanden ist, steht in keiner Quelle. Merkmal festlegen (z. B. Gehwegüberfahrt, Plateau, Einengung) und Datenquelle – Verkehrsplaner*in, GIS
- [ ] N6: Tabelle 1.4 deckt SW–GOW50 (50 Knoten), SW–SW (49), ETW_ERF–ETW_ERF (40) und SW–ETW30 nicht ab (not_defined). Soll-Knotentyp festlegen? – Verkehrsplaner*in
- [ ] N6: GOW50–GOW30 gilt als „Kreisverkehr, sonst Signal mit Plateau“ (Zeile GOW50), GOW30–GOW30 als Kreisverkehr. So gemeint? Kreisverkehr an ETW–ETW-Knoten (64) gilt als Abweichung von „gleichrangig“ – Verkehrsplaner*in
- [ ] N6: Gehwegüberfahrten und Vorfahrtregelung (give_way/stop) sind in OSM kaum erfasst; die meisten Knoten sind not_checkable. Quelle für Ist-Knotentypen? – GIS
- [ ] Flag-Liste fachlich durchsehen (reports/coherence.md, Stichprobe, reports/coherence_flags.geojson) – Verkehrsplaner*in
- [ ] reports/coherence_flags.geojson ist 1,5 MB (alle markierten Abschnitte, Knoten, Flächen). In Git lassen oder nur erzeugen? – Team

## Diskrepanz und Priorisierung (Prompt 10, rules.yaml 0.10.0)
- [ ] **Top 30 gegenlesen** (reports/priority_top30.md, Spalte „Prüfung“) – Ortskundige
- [x] Stärke 1 bei 1–19 km/h über Soll (D-SPD-01), DTV-Faktoren 1,5/2,0 (D-USE-01, Arbeitswert), Unfallzuordnung ≤ 15 m und Mindestlänge 100 m (P-RISK-01) – 2026-10-28: freigegeben (Entscheidung Projektteam 2026-10-28, rules.yaml 0.10.1)
- [ ] Zuordnung flow/sparse je Verstoß und damit D1–D3 (D-DES-01, D-TYPE-01) an Beispielen der Sichtprüfung beurteilen (reports/discrepancy.md, Stichprobe) – Verkehrsplaner*in
- [ ] Die Top 30 werden von HVS-Abschnitten mit Soll GOW30 bestimmt: 14 von 30 sind HVS mit Soll GOW30 und DTV 2019 von 21 000–39 000 Kfz/Tag (Nutzung Stärke 3), 6 weitere GOW30, 10 ETW30. Das hängt an der offenen Frage aus Prompt 08 (60 % der HVS-km werden GOW30). Erst klären, dann Liste neu erzeugen – Verkehrsplaner*in
- [ ] Top 30 enthält mehrere Abschnitte derselben Straße (z. B. Hallerstraße 8×: 6 GOW30, 2 ETW30). – 2026-10-28: Straßenliste (Top 30 Straßen nach Name) vor der Abschnittsliste ergänzt (Entscheidung Projektteam 2026-10-28). Offen: Hallerstraße-Abschnitte mit Soll ETW30 und Ist 50 sind vermutlich Lücken im HVS-Abgleich (in_hvs false) – Methodik
- [ ] `bahnigkeit_official` als Mitteltrennung: Bedeutung des Attributs (1/2) in der Quelle nicht bestätigt. 173 von 367 GOW50-Abschnitten haben ≥ 2 Fahrstreifen je Richtung bei bahnigkeit 1 (z. B. Kieler Straße) – GIS
- [ ] D-DES-01 GOW50 „Radweg oder Parallelroute“: Parallelroute ist nicht prüfbar, jeder GOW50 ohne baulichen Radweg zählt als Verstoß (74 Abschnitte) – Methodik
- [ ] Nutzung nur für GOW30 prüfbar (nur dort max_dtv) und DTV nur auf Hauptverkehrsstraßen 2019 (918 von 4 787 Abschnitten). max_dtv für ETW30 (Erschließung) und GOW50 festlegen? – Verkehrsplaner*in
- [ ] Mittelmarkierung (GOW30) ist bei 98,7 % unbekannt (OSM lane_markings kaum erfasst); Gestaltungs-Diskrepanz auf GOW30 daher fast nur über die Radführung – GIS
- [ ] Unfälle an Knoten gehen an genau einen anliegenden Abschnitt (den nächsten). Vorerst so belassen (Entscheidung Projektteam 2026-10-28); mit der Webkarte (Prompt 11) erneut prüfen: auf alle Arme verteilen oder Knoten gesondert ausweisen? 666 von 17 534 Unfällen mit Fuß-/Radbeteiligung liegen > 15 m von jedem Abschnitt – Methodik
- [ ] Risiko berücksichtigt nur Unfälle mit Fuß-/Radbeteiligung (polizeilich erfasst). Rettungsdienstdaten wie in Amsterdam (guide.md) verfügbar? – Team

## Export und Webseite (Prompt 11)
- [ ] GitHub-Repository anlegen und `web.github_repo` sowie `web.feedback_email` in config/project.yaml eintragen (ohne Werte kein Rückmeldeknopf) – Team
- [ ] Impressum: Verantwortliche Person/Organisation eintragen (web/src/pages.js, derzeit Platzhalter) – Team
- [ ] Nach dem ersten Deployment HTTP-Range auf GitHub Pages prüfen (`web/scripts/check-range.sh <URL>`); lokal mit vite preview: 206 für beide PMTiles – GIS
- [ ] Test auf einem echten Smartphone und mit Bildschirmleser (VoiceOver/NVDA); automatisch geprüft sind nur axe-core und emuliertes Pixel 7 (reports/web_accessibility.md) – Team
- [ ] Lizenz der amtlichen Tempo- und Verkehrsmengendaten fehlt in der API („Lizenz in der Quelle nicht angegeben“ im Steckbrief). Vor der Veröffentlichung klären, ob die abgeleiteten Werte gezeigt werden dürfen – GIS, Team
- [ ] Texte der Methodenseite und der Steckbriefe (config/plain_language.yaml) fachlich und auf einfache Sprache prüfen; Fotos aus Panoramax je Kategorie fehlen noch (guide.md 5.5) – Verkehrsplaner*in
- [ ] Cloudflare R2 für die PMTiles erst nötig, wenn mehrere Bezirke dazukommen (jetzt 1,6 MB + 13 MB Hintergrundkarte, Seite gesamt ca. 66 MB). Entscheidung später – Team
- [ ] Querschnittsskizze im Steckbrief zeigt nur „vorhanden vs. nötig“; Soll-Aufteilung (Gehweg/Radweg/Fahrbahn) als Skizze fehlt noch (guide.md 5.3) – Methodik

## Validierung und Sensitivität (Prompt 12, rules.yaml 0.11.0)
- [ ] Monte-Carlo variiert Gewichte **und** Annahme-Schwellen gemeinsam (guide.md 7.1 „über alle Annahmen“); prompts/12 nennt nur Gewichte. So belassen? Nur Gewichte ergäben deutlich weniger „unsichere“ Abschnitte – Methodik
- [ ] „unsicher“ ab Wechselquote 0,3 (prompts/12) oder erst über 0,3 (guide.md P11)? Umgesetzt: ab 0,3 (V-UNC-01) – Methodik
- [ ] conn_gow ist die mit Abstand einflussreichste Annahme: −20 % (0,48) macht 39,8 km zu GOW, vor allem ETW30 → GOW30 (z. B. Mittelweg, Lohkampstraße, Wördemanns Weg). Schwelle am HVS-Netz und an Stichproben kalibrieren – Verkehrsplaner*in
- [ ] Das Gewicht von in_hvs in conn_score wirkt auf Nicht-HVS-Straßen wie ein Abzug (ihr Wert 0 zählt mit, HVS greift ohnehin über C-GOW-01). −20 % auf dieses Gewicht macht 15,2 km zu GOW. in_hvs aus conn_score herausnehmen? – Methodik
- [ ] 292 Soll-ETW30-Abschnitte mit Ist-Tempo > 30 sind mögliche Datenfehler (Zone 30 laut Zonenebene, Quellen widersprechen sich, nur OSM-Tempo, HVS-Abgleich teilweise). Liste in reports/validation.md Abschnitt 2 durchsehen; z. B. Osterstraße (nur OSM-Tempo 50) – GIS
- [ ] Hauptstraßen mit Soll ETW30 (Kieler Straße, Vogt-Wells-Straße, primary) deuten auf Lücken im HVS-Abgleich (S-CONF-04, nur match exact) – GIS
- [ ] Abschnitte ohne Ist-Tempo 7,3 % (Ziel unter 5 %, V-DQ-01); im Randbereich „ohne Bezirk“ 24 % – GIS
- [ ] Abbruchgrenze für einen Rückgang der Kennzahl „HVS-km als GOW50/GOW30“ zwischen zwei Läufen (guide.md 3.4) ist nicht festgelegt; reports/validation_metrics.json speichert die Kennzahlen je Lauf – Methodik
- [ ] Annahmen früherer Stufen (Conflation-Puffer, Transekte, Puffer der Merkmale) sind nicht variiert, weil jede Variante einen neuen Lauf ab der jeweiligen Stufe braucht. Für die wichtigsten (S-CONF-01 buffer_m, S-XS-05 quantile) einmalig nachholen? – Methodik
- [ ] Manuelle Stichproben (reports/conflation_sample.csv, classification_sample.csv, transect_sample.geojson) sind nicht ausgefüllt; ohne sie ist der Entwurf nach guide.md Teil 7 nicht veröffentlichungsreif – Team
- [ ] Externe Fachprüfung: reports/validation.md an Hochschule oder Planungsbüro geben – Team

## Daten
- [ ] Führt HH_WFS_Strategisches_Strassennetz ein Attribut „Hauptverkehrsstraße“ mit Stand 2023? – GIS
- [x] Welche Jahrgänge enthält api.hamburg.de/datasets/v1/verkehrsmengen (DTV Hauptverkehrsstraßen)? – GIS – 2026-10-28: dtv_hvs_2019, dtvw_hvs_2014, dtv_bab_2019, dtvw_bab_2013 (siehe reports/data_report.md)
- [ ] Gibt es Kfz-Zählungen auf Bezirksstraßen? Transparenzanfrage an Bezirksämter – Team
- [ ] Dienst-URL für „Radnetz Hamburg“ im Geoportal – GIS
- [ ] Endpunkte für Schulen, Kitas, Lärmkarten, Laserscan, Baumkataster, ALKIS-Download – GIS (GTFS, Zensus und ALKIS 2026-10-28 erledigt: WFS_HH_ALKIS_vereinfacht)
- [x] Abdeckung Hamburgs im Unfallatlas je Jahr – GIS – 2026-10-28: laut Datensatzbeschreibung ab 2016; 2021–2025 je 6 397–7 332 Unfälle (sources.yaml 0.1.6)
- [ ] Gibt es amtliche Flächen für Fahrbahn/Radweg/Gehweg (LSBG, Bezirke)? Transparenzanfrage – Team
- [ ] Lizenzen der OGC-API-Datensätze (api.hamburg.de) auf den Landing Pages prüfen – GIS
- [ ] HH_WFS_Strategisches_Strassennetz liefert seit 2026-10-28 HTTP 404 (Dataport-Fehlerseite). Neue Dienst-URL ermitteln (Geoportal/Transparenzportal); wird für die Conflation (Prompt 05) gebraucht – GIS
- [ ] DB Rad+ (api.hamburg.de/datasets/v1/dbradplus, jahr2025): Abfrage mit bbox bricht reproduzierbar ab (HTTP 200, abgeschnittenes JSON bei offset 10000/11000). Fehler an die Urban Data Platform melden; danach erneut `make fetch` – Team
- [ ] Lizenz fehlt in der API für „Zulässige Höchstgeschwindigkeiten“ und „Verkehrsmengen“ sowie in GetCapabilities von „Ruhige Gebiete“ – GIS
- [ ] Verkehrsmengen auf Hauptverkehrsstraßen liegen in der API nur bis 2019 (DTV) vor. Gibt es neuere Zählungen? – GIS
- [x] Direkter Download-Link für das Zensus-2022-Gitter (100 m, Bevölkerung) in sources.yaml eintragen – 2026-10-28 erledigt (sources.yaml 0.1.3)
- [x] Linkformat für Orthophoto (Geoportal Hamburg) und Panoramax in den Stichproben-Reports festlegen; bisher nur OSM-Links – Team – 2026-10-28: sources.yaml 0.1.5 `viewers` (Geoportal Layer 19968, Panoramax-Hash), genutzt ab reports/classification.md
- [ ] SensorThings (iot.hamburg.de): 3.137 Locations im Arbeitsgebiet, gemischte IoT-Daten. Welche Things sind Kfz-/Rad-Zählstellen (Filterkriterium)? – GIS

## Rechtlich / Veröffentlichung
- [ ] ODbL-Pflichten bei Kombination OSM + amtliche Daten juristisch prüfen lassen – Team
- [ ] Rückmeldekanal und Datenschutz (GitHub-Issues, Formular) festlegen – Team
