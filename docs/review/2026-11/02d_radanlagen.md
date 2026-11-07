# Review 2026-11 · Phase 2d: Radanlagen (Führungsform, Breite, Lage)

Stand: cycling_rules.yaml 0.7.0, design_rules.yaml 0.6.0; `data/interim/cycle_facility.parquet`,
`cross_section_soll.parquet`, `cycle_network.parquet`, `cycle_principles.parquet`. Skript:
`analysis/review_2026_11/facility_2d.py`, Ergebnisse `data/scenarios/review_static/facility_2d.json`.
Radnetz = Soll-Kategorien RSV, HAUPT, BASIS (2 565 km Straßenabschnitte).

## Kurzfassung

- **Zweirichtungsradwege kommen im Soll nicht vor.** 242 km Ist-Zweirichtungsradweg auf dem Radnetz werden zu 188 km
  „Teilerfüllung“. Regel S-03 (Zweirichtungsradweg einseitig, wo nur eine Seite Ziele hat) ist nicht umgesetzt.
- **Die Lage wird nicht modelliert.** `cycle_side` kennt nur „beidseitig“, „Fahrbahn“ und „eigener Weg“; Seitenwechsel
  und Linksführung lassen sich daher nicht prüfen.
- **Einbahnstraßen:** 204 km ETW30-Einbahnstraßen liegen im Radnetz (120 km davon Soll-Fahrradstraße). Ob Radverkehr in
  Gegenrichtung zugelassen ist (PL-06), wird nicht geprüft.
- **Bushaltestellen:** An 257 km Soll-Radweg auf Buslinien liegen 1 028 Haltestellenpunkte. Ob eine Haltestelleninsel
  Platz hat (PL-05), ist im Profil nicht prüfbar.
- **Amtliches Radnetz:** 956 km amtliches Netz (Bestand und Planung) liegen im Radgraphen; 374 km davon sind Soll-RSV/
  HAUPT, **454 km sind im Soll nur Erschließung**. Umgekehrt liegen 1 564 km Soll-RSV/HAUPT außerhalb des amtlichen Netzes.
- **Breiten:** Ist-Breite bekannt auf 114 von 2 565 km (4 %). „Zu schmal“ (41,5 km) ist deshalb eine Untergrenze.
- **Kontinuität:** 2 157 von 5 030 Routen haben im Soll mehr als 1 Führungswechsel je km (C-PRI-12). Viele davon sind
  kurze Verdichtungsrouten, bei denen ein Wechsel schon über der Grenze liegt.

## 1 Führungsform Soll, nach Querschnitt, Ist

| Führungsform | Soll (Matrix) | final (nach Querschnitt) | Ist (OSM) |
|---|---:|---:|---:|
| beidseitiger Einrichtungsradweg | 402,4 km | 315,3 km | 500,1 km |
| Zweirichtungsradweg | 0 | 0 | 241,9 km |
| Radfahrstreifen | 86,2 km | 173,3 km | 84,9 km |
| Fahrradstraße | 1 324,8 km | 1 324,8 km | 21,7 km |
| Mischverkehr | 684,1 km | 684,1 km | 1 716,2 km |
| eigene Trasse | 1,9 km | 1,9 km | – |

Der Querschnitt stuft 87,1 km Einrichtungsradweg auf Radfahrstreifen ab (Rückfall der Matrixzelle, GOW30-Hauptroute).
Lücken auf dem Radnetz: fehlt 1 091 km, keine 957 km, teilweise 358 km, falscher Typ 50 km, zu schmal 42 km, nicht
bewertet 67 km.

## 2 Befunde je Thema

| Thema | Befund | Beleg |
|---|---|---|
| Kontinuität | Soll: 2 157 Routen > 1 Wechsel/km (HAUPT 1 188, BASIS 947, RSV 22); Ist: 2 542 | `cycle_principles.parquet`, Spalten changes_soll_per_km/changes_ist_per_km |
| Seitenwechsel | nicht modelliert (`cycle_side` ∈ both, carriageway, own_path) | 6 931 Abschnitte „both“ |
| Zweirichtungsradweg | Ist 242 km, Soll 0; Lücke „teilweise“ auf 188 km | S-03 ohne Umsetzung (01_bestand.md, 1.4) |
| Bushaltestellen | 1 028 Haltestellenpunkte an 974 Abschnitten mit Soll-Radweg und Bus | GTFS stops.txt, Abstand ≤ 25 m (nur für diese Auswertung) |
| Einbahnstraßen | 204 km ETW30-Einbahn im Netz (Fahrradstraße 120 km, Mischverkehr 84 km) | PL-06 ohne Umsetzung |
| Brücken | 16,6 km im Netz (Name „…brücke“); passt 9,7, passt nach Abbau 1,4, passt nicht 1,5, ohne Breite 4,0 km | Breite über ALKIS-Verkehrsfläche (Wasserflächen begrenzen nicht) |
| Abgleich amtliches Netz | 454 km amtlich → Soll ERSCHL; 1 564 km Soll-RSV/HAUPT nicht amtlich | official_share ≥ 0,5 je Kante |
| Breiten | Ist-Breite auf 114 km bekannt | OSM width/cycleway:width |

Beispiele (Zweirichtungsradweg Ist, Einbahnstraße ETW30 im Netz) mit Links: `facility_2d.json`, Felder
`examples_twoway`, `examples_oneway`.

## 3 Vorschläge

Struktur je Vorschlag: Problem · Beleg · Vorschlag · erwartete Wirkung · Risiken · Aufwand · source_type. „Wirkung“ ist
hier eine Obergrenze aus den vorhandenen Daten; die Stufen c05/c06 wurden nicht neu gerechnet (Neurechnung ab
`cycle-facility` rund 6 min, sobald eine Entscheidung fällt).

### R-1 Zweirichtungsradweg als Soll zulassen (S-03 umsetzen)

- **Problem:** Die Matrix kennt für GOW nur beidseitige Einrichtungsradwege; bestehende Zweirichtungsradwege gelten immer
  als Teilerfüllung.
- **Beleg:** 242 km Ist, 188 km davon „teilweise“.
- **Vorschlag:**
  ```yaml
  # cycling_rules.yaml separation_matrix, neue Bedingung je GOW-Zelle
  + twoway_if: 'one_sided_destinations or crossings_per_km <= twoway_max_crossings_per_km'
  + twoway_max_crossings_per_km: {value: TODO, source_type: assumption}   # Wert offen, nicht erfinden
  ```
  Merkmal `one_sided_destinations` = eine Straßenseite ohne Gebäude im Puffer (aus `share_facade_open` der Transekte,
  S-XS-*).
- **Wirkung:** bis zu 242 km „teilweise“ → „passt“; zusätzlich weniger Platzbedarf im Querschnitt (ein statt zwei
  Radwege).
- **Risiken:** Zweirichtungsradwege sind an Knoten unfallträchtig (Geisterradler-Konflikt); CROW empfiehlt sie innerorts nur
  eingeschränkt. Schwelle für Knotendichte fehlt (TODO, offene Frage).
- **Aufwand:** mittel (Merkmal, Matrix, Querschnitt PRF-03 Seite links).
- **source_type:** swov_crow für die Regel (CROW_OW_2016), assumption für die Schwelle.

### R-2 Lage je Seite führen

- **Problem:** Ohne Seite kein Seitenwechsel, keine Prüfung von Linksführung oder Haltestelleninsel.
- **Vorschlag:** `cycle_side` ∈ left, right, both, carriageway, own_path; bei Zweirichtungsradweg die Seite mit mehr Zielen;
  Wechselzahl je Route als Teil von P-COH-04.
- **Wirkung:** Grundlage für R-1, R-3 und die Kontinuitätsprüfung.
- **Risiken:** braucht die Fahrtrichtung der Abschnitte (Geometrierichtung reicht).
- **Aufwand:** mittel.
- **source_type:** keine neue Schwelle.

### R-3 Bushaltestellen im Profil

- **Problem:** PL-05 ist nicht prüfbar.
- **Beleg:** 1 028 Haltestellenpunkte an Soll-Radwegen.
- **Vorschlag:** Haltestellen aus GTFS den Abschnitten zuordnen (Abstand aus PRF-02 bzw. 25 m als Annahme); an diesen
  Abschnitten Profil mit Haltestelleninsel (Breite Wartefläche aus ERA/EAÖ, TODO) prüfen, sonst Flag.
- **Wirkung:** 974 Abschnitte erhalten eine Haltestellenprüfung; ein Teil wechselt zu „passt nicht“ oder „passt nach
  Abbau“.
- **Risiken:** GTFS-Haltestellenpunkte liegen teils mittig; Zuordnung zur Seite unsicher.
- **Aufwand:** mittel.
- **source_type:** de_regelwerk für die Breite (nach Prüfung), assumption für den Abstand.

### R-4 Gegenrichtung in Einbahnstraßen (PL-06 umsetzen)

- **Problem:** 204 km ETW30-Einbahn im Netz ohne Aussage zum Radverkehr in Gegenrichtung.
- **Vorschlag:** Flag `contraflow_needed`, wenn Einbahn und Radnetz; Ist aus OSM `oneway:bicycle=no`/`cycleway=opposite*`.
  Breitenprüfung gegen die vorhandene Einbahnfahrbahn (PRF-04 ETW 4,00 m).
- **Wirkung:** 204 km mit Aussage „Gegenrichtung frei / fehlt“.
- **Aufwand:** klein.
- **source_type:** de_regelwerk (StVO/VwV, nach Prüfung), keine neue Schwelle.

### R-5 Amtliches Radnetz als Mindestnetz

- **Problem:** 454 km amtliches Netz sind im Soll nur Erschließung.
- **Vorschlag (Option):** amtliches Radnetz (Bestand und Planung) mindestens als BASIS führen (C-NET-12 vor ERSCHL). Die
  bestehende Regel gibt nur einen Bonus × 0,8 im Widerstand.
- **Wirkung:** bis zu 454 km zusätzlich BASIS; BASIS wächst von rund 1 000 km entsprechend.
- **Risiken:** übernimmt auch amtliche Routen, die das Modell für unattraktiv hält; Netzumfang steigt weiter.
- **Aufwand:** klein.
- **source_type:** hamburg.

### R-6 Breiten beschaffen statt schätzen

- **Problem:** Ist-Breite auf 4 % der Netzlänge.
- **Vorschlag:** Breiten aus ALKIS-Flächen „Radweg“ (falls in nutzart vorhanden) oder Ortsbegehung in einem Bezirk; bis
  dahin „zu schmal“ als Untergrenze kennzeichnen (Webseite).
- **Aufwand:** groß (Daten).
- **source_type:** —.

## 4 Bezug zu anderen Teilen

- 2b K2: 304 km Soll-Fahrradstraße auf ETW30 mit Bus. Fahrradstraßen mit Linienbus sind ein Zielkonflikt; Auflösung
  über Straßenkategorie (2a, Busregel) oder Führungsform (Radweg statt Fahrradstraße).
- Offene Fragen Zeilen 184 (Annahmen C-FAC), 189 (C-FAC-05 gegen C-PRI-02), 199 (PL-02/PL-05).
