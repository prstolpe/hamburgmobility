# Offene Fragen

Format: `- [ ] Frage – Wer klärt – Status/Antwort`. Claude Code trägt hier ein, statt zu raten.

## Fachlich (Regelwerk)
- [ ] Gehwegbreite 2,50 m und Fahrbahnbreite 6,50 m (zwei Fahrstreifen, Begegnung Lkw/Bus) am Original der RASt 06 prüfen – Verkehrsplaner*in
- [ ] RIN-Kategoriengruppen und RASt-Entwurfssituationen je Kategorie am Original prüfen (Teil 1.3) – Verkehrsplaner*in
- [ ] Schwellen mit `source_type: assumption` freigeben: conn_gow 0,6; sensitive_radius 150 m; frontage 0,4; N2 200 m; N3 25 ha; N4 300 m; Machbarkeitsklassen 0,85/1,0 – Verkehrsplaner*in
- [ ] Gewichte conn_score, place_score und Priorisierung festlegen – Verkehrsplaner*in
- [ ] Stand der FGSV-Neufassungen (RASt, ERA, EFA) vor jedem Release prüfen – Team

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
