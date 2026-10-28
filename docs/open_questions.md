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

## Daten
- [ ] Führt HH_WFS_Strategisches_Strassennetz ein Attribut „Hauptverkehrsstraße“ mit Stand 2023? – GIS
- [ ] Welche Jahrgänge enthält api.hamburg.de/datasets/v1/verkehrsmengen (DTV Hauptverkehrsstraßen)? – GIS
- [ ] Gibt es Kfz-Zählungen auf Bezirksstraßen? Transparenzanfrage an Bezirksämter – Team
- [ ] Dienst-URL für „Radnetz Hamburg“ im Geoportal – GIS
- [ ] Endpunkte für Schulen, Kitas, Lärmkarten, Laserscan, Baumkataster, ALKIS-Download – GIS
- [ ] Abdeckung Hamburgs im Unfallatlas je Jahr – GIS
- [ ] Gibt es amtliche Flächen für Fahrbahn/Radweg/Gehweg (LSBG, Bezirke)? Transparenzanfrage – Team
- [ ] Lizenzen der OGC-API-Datensätze (api.hamburg.de) auf den Landing Pages prüfen – GIS

## Rechtlich / Veröffentlichung
- [ ] ODbL-Pflichten bei Kombination OSM + amtliche Daten juristisch prüfen lassen – Team
- [ ] Rückmeldekanal und Datenschutz (GitHub-Issues, Formular) festlegen – Team
