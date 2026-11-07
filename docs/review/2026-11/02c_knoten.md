# Review 2026-11 · Phase 2c: Kreuzungen (Knotenpunkte)

Stand: design_rules.yaml 0.6.0, `data/interim/junctions.parquet` (16 259 Knotenpunkte). Skript:
`analysis/review_2026_11/junctions_2c.py`, Ergebnisse `data/scenarios/review_static/junctions_2c.json`, Stichprobe
`junctions_sample50.csv` (mit Links auf Seite, OSM und Luftbild).

## Kurzfassung

- **Die Regeln selbst sind in sich stimmig:** kein Kreisverkehr ohne Platz (1 Fall mit unbekanntem Platz), kein
  einstreifiger Kreisverkehr über der Zuflussgrenze, keine Soll-Ampel an ETW×ETW.
- **Die Eingangsdaten sind die Schwachstelle:** Für 86,5 % der Knotenpunkte ist der Ist-Typ in OSM nicht erfasst
  (`none_mapped`). 432 Ist-Ampeln sitzen an Knoten zweier Quartiersstraßen; das sind sehr wahrscheinlich Ampeln des
  Nachbarknotens im 30-m-Radius (offene Frage Zeile 214).
- **Clustering:** 63 Knotenpunkte sind größer als 50 m (bis 187 m); umgekehrt liegen 116 Paare getrennter
  Knotenpunkte mit je ≥ 3 Armen näher als 25 m beieinander (zu wenig zusammengefasst). 2 252 Knotenpunkte haben nach
  der Armzusammenfassung weniger als 3 Arme.
- **Stichprobe (50, geschichtet nach Soll-Typ):** 2 falsch, 48 unsicher, 0 sicher richtig. Bewertet wurde nur auf
  Daten, nicht im Luftbild: Ohne erfassten Ist-Typ lässt sich kein Knoten als „richtig“ bestätigen. Das ist der
  Hauptbefund: Für eine Trefferquote braucht es die Sichtprüfung (30 Knoten je Typ, `reports/junctions_review.csv`,
  bisher leer).

## 1 Qualitätsprüfung

| Prüfung | Anzahl | Bewertung |
|---|---:|---|
| Ausdehnung > 2 × cluster_radius_m (50 m) | 63 | zu viel zusammengefasst: Ketten in dichten Netzen (offene Frage, Prompt 20) |
| mehr als 5 Netzknoten in einem Knotenpunkt | 126 | meist große Kreuzungen mit Richtungsfahrbahnen, teils Ketten |
| getrennte Knotenpunkte < 25 m voneinander, beide ≥ 3 Arme | 116 Paare | zu wenig zusammengefasst: über keinen Straßenabschnitt ≤ 25 m verbunden (z. B. versetzte Einmündungen) |
| weniger als 3 Arme | 2 252 | nach J-M-02 (Arme gleichen Namens, gleichen DTV, ≤ 30°) zusammengefasst; darunter 321 Radweg-Knoten (ETW30+cycle_path); bei Gabelungen und Rampen fasst die Regel zwei echte Arme zusammen (Beispiele: Harburger Chaussee, Neuhöfer Straße) |
| 6 und mehr Arme | 125 | große Plätze; Kategoriepaar aus den zwei ranghöchsten Zügen |
| Soll-Kreisverkehr, Platz unbekannt | 1 | Krohnstieg/Zeppelinstraße (Turbokreisverkehr, confidence low) |
| Soll-Kreisverkehr, Platz < roundabout_min_radius | 0 | Rückfallregel J-M-05 greift |
| einstreifiger Kreisverkehr über roundabout_max_dtv | 0 | seit design_rules 0.4 (J-03 mit DTV-Grenzen) |
| Soll-Ampel an ETW30+ETW30 | 0 | — |
| Soll-Kreisverkehr, heute Ampel | 231 | Umbau großer Knoten; fachlich möglich, aber Platz nur über ALKIS-Verkehrsfläche geschätzt |
| Soll „rechts vor links“, heute Ampel | 169 | Rückbau einer Ampel an ETW×ETW; zum Teil die Fehlzuordnung unten |
| **Ist-Ampel an ETW30+ETW30** | **432** | Ampel des Nachbarknotens (Radius 30 m, N6 signal_radius_m) |

**Kategoriepaare** (Häufigkeit): ETW30+ETW30 11 188, GOW30+ETW30 2 000, GOW30+GOW30 743, GOW50+ETW30 581, GOW50+GOW30
498, ETW30+ETW_ERF 400, ETW30+cycle_path 385, GOW50+GOW50 181, SW+SW 157. Fehlende Tabellenzeilen: heute 10 Knoten
`no_rule` (Stand Prompt 20: 412; 326 Knoten tragen inzwischen das Flag `cycle_path_ignored`: Der eigenständige Radweg
wird übergangen und der Knoten nach den Straßenarmen eingestuft, meist J-07 oder J-05). ETW_ERF wird über `category_alias` wie ETW30 behandelt (727 Knoten mit diesem Flag).

**Ist-Typ aus OSM:** none_mapped 14 071, signal 2 029, roundabout 83, plateau 67, signal_plateau 9. Ergebnis des
Ist/Soll-Vergleichs: nicht prüfbar 8 562, passt 5 068, Handlungsbedarf 2 619. Hamburg hat deutlich mehr als 83
Kreisverkehre; OSM-Tag `junction=roundabout` wird nur an Armen oder inneren Abschnitten gesucht, Minikreisel
(`highway=mini_roundabout`, Knoten-Tag) fehlen.

## 2 Stichprobe 50 Knotenpunkte

Schichtung nach Soll-Typ (je 5–7), Seed 42. Bewertung **auf Daten** (keine Sichtprüfung):
- falsch = eine Regel aus Abschnitt 1 schlägt an (Ausdehnung, Kreisverkehr ohne Platz, Zufluss, Ist-Ampel an ETW×ETW);
- richtig = confidence high, keine Flags, Ist-Typ erfasst und passend, kein Nachbarknoten < 25 m;
- sonst unsicher.

| Soll-Typ | falsch | unsicher | richtig |
|---|---:|---:|---:|
| rechts vor links (equal_right_before_left) | 0 | 7 | 0 |
| Vorfahrt mit Plateau (priority_raised) | 0 | 6 | 0 |
| Gehwegüberfahrt (continuous_footway_exit) | 0 | 6 | 0 |
| Radwegfurt mit Vorrang (cycle_crossing_priority) | 0 | 6 | 0 |
| geschützte LSA (signal_protected) | 1 | 4 | 0 |
| Vorfahrt eingefärbt (priority_flat_coloured) | 0 | 5 | 0 |
| planfrei (grade_separated_cycle) | 0 | 5 | 0 |
| einstreifiger Kreisverkehr | 0 | 5 | 0 |
| Turbokreisverkehr | 1 | 4 | 0 |
| **gesamt** | **2** | **48** | **0** |

Falsch: Gorch-Fock-Wall/Holstenwall/Johannes-Brahms-Platz/Sievekingplatz (84 m Ausdehnung, ein Platz mit mehreren
Knoten als ein Knotenpunkt), Krohnstieg/Zeppelinstraße (Turbokreisverkehr ohne bekannte Fläche, DTV teilweise).
Häufigster Grund für „unsicher“: Ist-Typ nicht erfasst (33 von 48). Über alle Knoten ergibt dieselbe Regel 494 falsch,
176 richtig, 15 589 unsicher. Die vollständige Liste mit Begründung und Luftbild-Link steht in der CSV.

## 3 Vorschläge

Struktur je Vorschlag: Problem · Beleg · Vorschlag · erwartete Wirkung · Risiken · Aufwand · source_type.

### K-1 Ist-Ampel nur dem eigenen Knoten zuordnen

- **Problem:** Eine Ampel im Umkreis 30 m zählt für den nächstgelegenen Knotenpunkt, auch wenn sie an der Kreuzung
  daneben steht.
- **Beleg:** 432 Ist-Ampeln an ETW30+ETW30; davon 169 mit Soll „rechts vor links“ und daher scheinbarem Rückbaubedarf.
- **Vorschlag:** Eine Ampel zählt nur, wenn sie näher als `signal_radius_m` liegt **und** an einem Arm des Knotenpunkts
  (Abstand zur Armlinie ≤ 5 m) und keine GOW/SW-Kreuzung näher liegt.
  ```yaml
  # design_rules.yaml J-M-06
  - signal_assignment: nearest_junction
  + signal_assignment: nearest_junction_on_leg   # Ampel auf einem Arm (≤ leg_snap_m), sonst nicht zugeordnet
  + leg_snap_m: {value: 5, unit: m, source_type: assumption}
  ```
- **Erwartete Wirkung:** bis zu 432 Knoten mit Ist „signal“ → none_mapped; Handlungsbedarf sinkt entsprechend (Ober-
  grenze, ohne Neurechnung geschätzt).
- **Risiken:** Ampeln an Fußgängerüberwegen mitten im Arm werden nicht mehr gezählt (gewollt).
- **Aufwand:** klein (J-M-06, ein Test).
- **source_type:** assumption.

### K-2 Minikreisel und Kreisverkehre aus OSM vollständig lesen

- **Problem:** Nur 83 Ist-Kreisverkehre; Knoten-Tags werden nicht gelesen.
- **Vorschlag:** `highway=mini_roundabout` (Knoten) und `junction=circular` als Ist-Typ ergänzen; zusätzlich eine amtliche
  Quelle für Lichtsignalanlagen prüfen (offene Frage Zeile 85, GIS).
- **Wirkung:** mehr prüfbare Knoten; Zahl erst nach Neurechnung bekannt.
- **Risiken:** keine fachlichen.
- **Aufwand:** klein.
- **source_type:** keine neue Schwelle.

### K-3 Obergrenze der Ausdehnung beim Zusammenfassen

- **Problem:** Ketten bis 187 m.
- **Beleg:** 63 Knotenpunkte > 50 m.
- **Vorschlag:** Zusammenfassen nur, solange die Ausdehnung ≤ `max_extent_m` bleibt; sonst am längsten Verbindungsabschnitt
  teilen.
  ```yaml
  # design_rules.yaml J-M-01
  + max_extent_m: {value: 60, unit: m, source_type: assumption, note: 'größte übliche Kreuzung mit Richtungsfahrbahnen'}
  ```
- **Wirkung:** 63 Knotenpunkte werden geteilt; dazu 116 Paare naher Knotenpunkte prüfen, die über Armlinien statt über
  Abschnitte verbunden sind.
- **Risiken:** node_id ändert sich für diese Knoten (node_id ist ein Hash der Mitglieder). Bestehende Overrides gibt es
  nicht, daher derzeit unkritisch.
- **Aufwand:** mittel.
- **source_type:** assumption.

### K-4 Armzusammenfassung nur bei Richtungsfahrbahnen

- **Problem:** J-M-02 fasst auch Gabelungen und Rampen zusammen (gleicher Name, gleicher DTV, ≤ 30°).
- **Beleg:** 2 252 Knotenpunkte mit < 3 Armen.
- **Vorschlag:** zusätzliche Bedingung „die beiden Abschnitte sind Einrichtungsfahrbahnen (oneway, amtlich eine Richtung 0)“.
- **Wirkung:** bis zu 2 252 Knotenpunkte erhalten wieder 3 Arme; das Kategoriepaar ändert sich nur, wenn die Arme
  verschiedene Kategorien haben.
- **Risiken:** Einbahninformation fehlt teilweise (`oneway` aus PRF-01); dann bleibt es bei der heutigen Regel.
- **Aufwand:** klein.
- **source_type:** keine neue Schwelle.

### K-5 Sichtprüfung statt weiterer Regeln

- **Problem:** Ohne Ist-Typ ist keine Trefferquote möglich.
- **Vorschlag:** die 50 Knoten dieser Stichprobe plus die 270 Zeilen in `reports/junctions_review.csv` im Luftbild prüfen,
  zuerst die 2 619 Knoten mit Handlungsbedarf und hoher Radkategorie (Rang `priority_rank`).
- **Wirkung:** Fehlerquote je Soll-Typ.
- **Aufwand:** etwa 1 Minute je Knoten (Annahme).
- **source_type:** —.

## 4 Bezug zu anderen Teilen

- 2b, K3: An 55 Knoten quert eine RSV/HAUPT-Route eine GOW50 mit Soll „Gehwegüberfahrt“. Dafür fehlt eine
  Tabellenzeile (Querung einer GOW50 durch eine Radroute, die nicht auf der GOW50 liegt); siehe `02b_konflikte.md`.
- Offene Fragen Zeilen 203–216 (Prompt 20) bleiben bestehen; K-1 beantwortet Zeile 214 als Vorschlag, K-3 Zeile 203
  (Clusterradius).
