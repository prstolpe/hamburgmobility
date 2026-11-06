# Radnetz und Soll-Querschnitt – Methodik (Erweiterung des Straßenfunktionsplans)

Stand 05.11.2026 · nicht amtlicher Entwurf · [F] = Fakt mit Quelle, [B] = Bewertung/Annahme

## Kurzfassung

Die Erweiterung legt ein zweites Netz über den Straßenfunktionsplan: ein hierarchisches Radnetz,
das nach den fünf Prinzipien der niederländischen Radverkehrsplanung entworfen und geprüft wird.
Aus Straßenkategorie (`cat_final`), Radnetzkategorie, Radverkehrsstärke und verfügbarem
Straßenraum bestimmt ein Regelwerk dann je Abschnitt Führungsform, Breite und Lage der
Radanlage sowie die Zahl der Kfz-Fahrstreifen und je Knoten den Knotentyp [B].
Wie bisher gilt: Automatik schlägt vor, Menschen entscheiden; jede Entscheidung hat einen
`rule_trace`.

Neue Konfiguration:
- `config/cycling_rules.yaml` – Radnetzkategorien, fünf Prinzipien als Prüfregeln, Trennungsmatrix, Breiten
- `config/design_rules.yaml` – Fahrstreifen, Lage, Raumaufteilung, Knotenpunkte
- `overrides/cycle_network_overrides.csv`, `overrides/junction_overrides.csv` – Korrekturebenen

## 1. Die fünf Prinzipien und ihre Übersetzung

Die fünf Hauptanforderungen der CROW-Ontwerpwijzer sind Zusammenhang (cohesion),
Direktheit, Sicherheit, Komfort und Attraktivität ([Dutch Cycling Embassy](https://dutchcycling.nl/expertises/cycling-infrastructure/)) [F].

| Prinzip | Kern [F] | Messgröße im Projekt [B] |
| --- | --- | --- |
| Zusammenhang | einheitliches Netz, das Quellen und Ziele verbindet | Maschenweite je Ebene, zusammenhängende Komponenten, Abdeckung wichtiger Ziele, Kontinuität der Führung |
| Direktheit | wenige Umwege und Halte, Bevorrechtigung | Umwegfaktor, Halte/km, Zeitverlust s/km |
| Sicherheit | Verkehrs- und soziale Sicherheit, Trennung von schnellem Kfz-Verkehr; Radrouten möglichst nicht parallel zu belasteten Hauptstraßen | Führungsform nach Trennungsmatrix, Knotentyp, Beleuchtung, Unfälle |
| Komfort | wenig Halte, glatte Beläge, klare Wegweisung | Breite ≥ Soll, geschlossene Decke, Steigungen |
| Attraktivität | Grün, Ruhe, gepflegte Straßen | Grünanteil, Lärm, Parallelität zu DTV-starken Straßen |

Netzebenen nach dem Delft-Beispiel ([DCE](https://dutchcycling.nl/expertises/cycling-infrastructure/)) [F]:
Stadtnetz 400–600 m Maschenweite (Wege 2–3 km), Bezirksnetz 200–300 m (1–2 km),
Quartiersnetz 100–150 m (0,5–1 km). Darüber liegen Radschnellverbindungen; Hessen setzt dafür
≥ 2.000 Radfahrende/Werktag, Zielgeschwindigkeit 20 km/h, Entwurfsgeschwindigkeit 30 km/h und
≤ 30 s/km Zeitverlust innerorts an ([Hessen 2019](https://mobil.hessen.de/sites/mobil.hessen.de/files/2022-01/handbuch_qualitaetsstandards_und_musterloesungen_150dpi_maerz_2019.pdf)) [F].

Hamburgs „Radnetz Hamburg“ umfasst 23 übergeordnete Radrouten mit 369 km; der Anteil
geschützter Radinfrastruktur und Fahrradstraßen liegt bei 66 %
([Jahresbericht 2025, März 2026](https://www.hamburg.de/resource/blob/1152164/b439698b0306d2e755aeccfc216dd29e/jahresbericht-2025-rad-und-fussverkehr-data.pdf)) [F].
Das amtliche Radnetz ist Startpunkt und Vergleichsebene, nicht Ergebnis [B].

## 2. Kategorien

| Code | Hamburg-Begriff | NL-Vorbild | Maschenweite | Auslöser |
| --- | --- | --- | --- | --- |
| RSV | Radschnellverbindung / Radroute+ | snelfietsroute | Korridore | ≥ 2.000 Rad/Werktag (Hessen) [F], ≥ 5 km [F] |
| HAUPT | Radroute | hoofdfietsroute | 400–600 m [F] | Stadtnetz, Bezirkszentren, Schnellbahn |
| BASIS | Bezirksroute | wijkontsluitend | 200–300 m [F] | Schulen, Nahversorgung |
| ERSCHL | Quartiersnetz | buurtnetwerk | 100–150 m [F] | alle übrigen befahrbaren Straßen/Wege |

## 3. Netzentwurf in fünf Schritten

1. **Kandidatennetz:** alle für Rad befahrbaren Kanten (OSM, Straßenabschnitte, eigenständige Wege) mit Ist- und Soll-Widerstand (`routing_impedance`).
2. **Nachfrage:** Radverkehrsstärke je Kante aus einem einfachen Nachfragemodell (Bevölkerungsgitter → Ziele, Gravitationsansatz, Routenwahl auf wahrgenommenem Widerstand), kalibriert an Zählstellen und DB Rad+ [B].
3. **Hierarchie:** Kanten mit hoher Modellbelastung und Lage auf Korridoren zwischen Zentren werden RSV/HAUPT; amtliche Radrouten erhalten einen Startbonus; Maschenregeln erzwingen Lückenschlüsse [B].
4. **Prinzipienprüfung:** Kriterien P-COH bis P-ATT je Route und Netz; Flags statt automatischer Reparatur.
5. **Korrektur:** `overrides/cycle_network_overrides.csv` mit Begründung; nur `approved` wird übernommen.

### 3.1 Radgraph und Nachfragemodell (Prompt 15, umgesetzt)

- **Radgraph** (pipeline/c01_cycle_graph.py, Regeln C-GRAPH-01…06): Straßenabschnitte mit Radverkehr, eigenständige Rad-
  und freigegebene Fußwege sowie Fähren mit Radmitnahme aus OSM, gerichtet (Gegenrichtung in Einbahnstraßen nur mit
  `oneway:bicycle=no`). Kanten-ID `ce_…` stabil wie `segment_id`; Bezug zum Abschnitt über `segment_id` bzw. `sidepath_of`.
- **Widerstand Ist** (C-IMP-01…08): Länge × Faktor aus `routing_impedance` je Führung und Tempo, plus Wartezeit an LSA und
  bei Wartepflicht, umgerechnet mit 15 km/h [B].
- **Nachfrage** (pipeline/c02_cycle_demand.py, C-DEM-01…07): Einwohner aus dem Zensus-Gitter in 500-m-Zonen; Ziele aus
  ALKIS-Geschossfläche (Nichtwohnen), Geschäften, Schulen, Hochschulen und Schnellbahnstationen; Gravitationsmodell mit
  exponentiellem Distanzverfall im Band 0,5–15 km; Umlegung auf kürzeste Wege nach wahrgenommenem Widerstand, gemittelt
  über drei Läufe mit leicht gestörten Widerständen [B].
- **Kalibrierung:** ein Faktor für Hamburg an den 104 Rad-Zählquerschnitten (Werktagsmittel 2025). DB Rad+ dient nur dem
  Plausibilitätsvergleich [B]. Ergebnis und Güte: reports/cycle_demand.md. Alle Parameter sind Annahmen und offen zur
  Freigabe (docs/open_questions.md).

### 3.2 Netzentwurf (Prompt 16, umgesetzt)

pipeline/c03_cycle_network.py, Regeln C-NET-01…13 in `network_design` (alle Annahmen, status draft):

- **Soll-Widerstand:** Länge × Faktor der regelkonformen Führung je cat_final plus Wartezeiten des Ist-Zustands; Boni für
  hohe Nachfrage und für Kanten des amtlichen Radnetzes [B].
- **Korridore:** Innenstadt, Schnellbahn-Umsteigeknoten, Hochschulen und Arbeitsplatzschwerpunkte, je mit den nächsten
  Punkten und der Innenstadt verbunden. Bezirks- und Stadtteilzentren fehlen noch (kein Datensatz) [B].
- **Hierarchie:** RSV auf Korridorläufen ab 2.000 Rad/Werktag und 5 km [F]; HAUPT und BASIS durch Teilen zu großer Maschen
  (Seite des flächengleichen Quadrats, Barrieren Bahn und Gewässer, ohne Wald-, Wasser- und Parkflächen) [B];
  Schulen und Nahversorgung an das BASIS-Netz angebunden; ERSCHL für alle übrigen Kanten.
- **P-ATT-03 und Kontinuität:** Parallelroute statt Hauptstraße, wenn sie im 200-m-Puffer den Umwegfaktor einhält;
  kurze Kategorielücken entlang einer Route werden geschlossen [B].
- Ergebnis, Vergleich mit dem amtlichen Radnetz (Status Bestand) und Lückenliste: reports/cycle_network.md.

Zielkonflikt Direktheit vs. Sicherheit/Attraktivität: Die DCE empfiehlt Routen, die nicht parallel
zu belasteten Hauptstraßen verlaufen [F]. Regel P-ATT-03 schlägt eine Parallelroute vor, wenn sie
innerhalb von 200 m liegt und den Umwegfaktor einhält; die Hauptstraße erhält trotzdem getrennte
Radwege (GOW50), weil dort Ziele liegen [B].

### 3.3 Prinzipienprüfung (Prompt 17, umgesetzt)

pipeline/c04_principles.py, Prüfungen P-COH/P-DIR/P-SAF/P-COM/P-ATT aus `principles`, Bewertung nach C-PRI-01…16 in
`principle_scoring` (alle Annahmen, status draft):

- **Zwei Sichten:** score_ist bewertet den heutigen Zustand der Soll-Route, score_soll den Zustand nach regelkonformem
  Ausbau (Führung nach Trennungsmatrix, Sollbreite, geschlossene Decke, Beleuchtung). Die Differenz ist der
  Handlungsbedarf [B].
- **Scores:** je Prüfung 0–1, je Prinzip das Mittel der bewerteten Prüfungen, gesamt mit `principle_weights`.
  Fehlende Daten (z. B. OSM width) zählen nicht als gut, sondern senken die confidence [B].
- **Ist-Führung** aus der Ist-Widerstandsregel (C-IMP) und OSM cycleway; begleitende Radwege gelten als baulich getrennt
  und ersetzen die Führung der Straße daneben [B].
- **Direktheit:** Umwegfaktor je Route und als Netzstichprobe (OD-Paare je Kategorie, Seed dokumentiert); Halte an LSA
  und bei Wartepflicht, Zeitverlust mit den Wartezeiten aus `routing_impedance` [B].
- **Nicht bewertet (Daten fehlen):** Knotentyp P-SAF-02 (Prompt 20), Steigung P-COM-03 (kein Höhenmodell), Lärm P-ATT-02
  (keine Lärmkarte). Grünanteil ohne Straßenbaumkataster, aus ALKIS-Nutzung und OSM-Bäumen [B].
- Ergebnis, Top-30-Routen, Karten je Prinzip und Gewichts-Sensitivität (±20 %): reports/cycle_principles.md;
  20 Routen zur Durchsicht mit Ortskundigen: reports/cycle_principles_review.csv.

### 3.4 Führungsform und Breite (Prompt 18, umgesetzt)

pipeline/c05_facility.py je Straßenabschnitt, Regeln C-FAC-01…07 in `facility_assignment` (alle Annahmen, status draft):

- **Soll-Führung** aus der Trennungsmatrix (cat_final × cycle_cat_final, höchste Radkategorie der Kanten des Abschnitts).
  Bei Zellen mit Fallback bleibt bis Prompt 19 die bevorzugte Führung; der Fallback folgt erst, wenn der Raum nicht reicht [B].
- **Fahrradstraße** nur bei höchstens 2 500 Kfz/Tag und Radverkehr ≥ Kfz in der Spitzenstunde, sonst Mischverkehr mit dem
  Hinweis „Kfz-Menge reduzieren (Filter) oder Route verlegen“. **S-04:** Mischverkehr bis 700 Kfz/h (DTV × 0,10) [B].
  Kfz-Mengen gibt es nur für Hauptverkehrsstraßen; ohne Zählung gelten beide Bedingungen vorläufig als erfüllt
  (Entscheidung 2026-11-06, Flag dtv_unknown) [B].
- **Sollbreite** = Projekt-Soll plus Verbreiterung nach Spitzenstunde, nie unter dem deutschen Mindestmaß; DE-Regelmaß und
  NL-Hauptnetz werden als Vergleich mitgeführt. Mischverkehr und eigene Trasse ohne Sollbreite [B].
- **Ist-Führung** aus OSM (Fahrradstraße, Radweg, Streifen, Sharrow/Busspur, keine) und **Lücke**: fehlt, falscher Typ,
  zu schmal (nur wo OSM eine Breite hat) [B].
- Ergebnis, Matrix Straßen- × Radkategorie, Lückenliste und 30 Stichproben je Führungsform: reports/cycle_facility.md.

## 4. Führungsform, Breite, Lage

Die Trennungsmatrix (`separation_matrix`) kombiniert Straßenkategorie und Radnetzkategorie:
- GOW50: immer baulich getrennte Einrichtungsradwege beidseitig; keine Radstreifen an GOW50 ([CROW 2023](https://www.amersfoort.nl/sites/default/files/2025-09/2023-crow-handreiking-voorlopige-inrichtingskenmerken-gow30.pdf)) [F].
- GOW30: Radfahrstreifen (CROW min. 1,70 m, ideal 2,20 m) [F]; Hauptroute bevorzugt getrennt [B].
- ETW30: Mischverkehr; Hauptroute als Fahrradstraße; keine Radstreifen auf ETW [F CROW].

Breiten: deutsche Regelwerte (Radweg 2,00 m, Zweirichtung 2,50 m, Radfahrstreifen 1,85 m,
Schutzstreifen 1,50 m, Trennstreifen 0,75 m) ([ERA 2010 via FGSV-Kolloquium](https://www.fgsv-verlag.de/pub/media/pdf/284_Gwiasda_P_Radverkehr_an_inneroertlichen_Hauptverkehrsstrassen.pdf)) [F],
E Klima 2,25 m für Radfahrstreifen [F] und niederländische Werte für Hauptnetze (Einrichtung 3,00 m,
Zweirichtung 4,00 m in einer kommunalen CROW-Umsetzung, [Castricum 2020](https://www.castricum.nl/fileadmin/Castricum/documenten-per-onderwerp/raadsdocumenten/Fietsbeleidsplan-eisen-fietsnetwerk-Castricum-april-2020.pdf)) [F].
Das Projekt-Soll in `widths_m.project_target` ist eine Setzung zwischen beiden und wird mit der
Spitzenstunde (15 % der Tagesmenge, [RWS 2021](https://www.ndw.nu/binaries/ndw/documenten/publicaties/2021/7/23/operationalisatie-definitie-van-voldoende-veilige-wegen-en-fietsinfrastructuur/Operationalisatie+Definitie+KN+SPV+30-50-70-60-80-fietspaden+definitief+def.pdf)) verbreitert [B].

## 5. Fahrstreifen und Raumaufteilung

- Grundsatz: so wenige Kfz-Fahrstreifen wie möglich; GOW30/ETW höchstens einer je Richtung [F CROW].
- GOW50: zweiter Fahrstreifen nur bei rechnerischer Kapazitätsnot (Regel L-02, Werte = Annahme, am HBS prüfen); dann Mittelstreifen [F CROW]; Busfahrstreifen hat Vorrang vor zweitem Kfz-Streifen (L-04) [B].
- Raumaufteilung: Bausteine in fester Reihenfolge (Gehwege → Radverkehr → ÖPNV → Kfz-Minimum → Puffer → Regelbreiten → Grün → Laden → Parken). Reicht der Raum nicht, greift die Abbaukaskade D1–D7, protokolliert im `rule_trace` [B].
- Ergebnis je Abschnitt: Soll-Profil mit Elementen und Breiten, Fahrstreifen je Richtung, Führungsform, Radwegbreite und -seite, Passung (passt/eng/passt nicht).

### 5.1 Soll-Querschnitt (Prompt 19, umgesetzt)

pipeline/c06_cross_section_soll.py je Straßenabschnitt, Regeln L-01…06, PL-01…06 und `profile_assignment` PRF-01…07
in design_rules.yaml 0.2.0 (Setzungen sind Annahmen, status draft):

- **Fahrstreifen:** Ist aus den amtlichen Fahrstreifen je Richtung (sonst OSM lanes); Soll nach L-01/L-02, ohne DTV
  = Ist mit niedriger confidence; nie mehr als im Ist (L-06) [B].
- **Busfahrstreifen** statt zweitem Kfz-Streifen ab 20 Bussen je Spitzenstunde und Richtung; die Spitzenstunde kommt aus
  dem HVV-GTFS (stärkste Abfahrtsstunde der stärkeren Richtung, Entscheidung 2026-11-06) [B].
- **Profil:** Gehwege, Radanlage (Lage nach PL-01…03), ÖPNV, Fahrbahn, Trennstreifen, Bäume an GOW, Ladezone bei
  Geschäftsnutzung und Parken nur, wo es heute Parken gibt. Verfügbar = width_p10_m (Verkehrsfläche); die Fassadenbreite
  zeigt das Potenzial [B].
- **Abbau:** D1 Parken, D2 Bäume, dann Fallback der Matrixzelle aus Prompt 18, D3 zweiter Fahrstreifen, D4 Mindestbreiten,
  D5 Vorschlag GOW50 → GOW30 (nicht übernommen), D6/D7 nur als Hinweis (D7 nur, wo die Radanlage eigene Breite belegt) [B].
- Ergebnis, Abbaustufen, Fahrstreifen Ist → Soll und Querschnitts-Skizzen: reports/cross_section_soll.md,
  reports/profiles_sample/*.svg.

## 6. Knotenpunkte

- Kreisverkehre sind der sicherste Knotentyp; ein vierarmiger einstreifiger Kreisverkehr hat 4 statt 24 Konfliktpunkte; Kreisverkehre mit getrennten Radwegen sind für Radfahrende am sichersten ([SWOV 2022](https://swov.nl/sites/default/files/bestanden/downloads/FS%20Rotondes%20en%20andere%20kruispunten_1.pdf)) [F].
- CROW empfiehlt innerorts Vorrang für Radfahrende auf umlaufenden Radwegen; SWOV-Analysen sehen Wartepflicht als sicherer [F] – im Regelwerk als dokumentierter Zielkonflikt (JC-01). In Deutschland hängt die Vorfahrt am Kreisverkehr von der fahrbahnnahen Führung ab; vor Gebrauch rechtlich prüfen [B].
- LSA-Knoten sind nach Volumenkorrektur die unsichersten [F]; sie kommen nur bei hoher Belastung oder Straßenbahn zum Einsatz und werden dann als geschützte Kreuzung gestaltet [B].
- Sehr belastete oder schnelle Kreuzungen von Hauptrouten: Tunnel oder Brücke ([DCE](https://dutchcycling.nl/expertises/cycling-infrastructure/)) [F].
- Entscheidungstabelle J-01 bis J-11 in `design_rules.yaml`; Schwellen für Kreisverkehrskapazität sind Annahmen.

## 7. Grenzen

- Radverkehrsstärken sind modelliert, nicht gezählt; DB Rad+ ist eine nicht repräsentative Stichprobe [B].
- CROW-Ontwerpwijzer und ERA wurden nicht im Original geprüft; viele Werte stammen aus Sekundärquellen [B].
- Die FGSV-Neufassung der ERA ist angekündigt; Breiten können sich ändern [B].
- Knotentypen setzen Platz und Leistungsfähigkeit voraus, die das Projekt nur grob schätzt [B].
- Der Entwurf ersetzt keine Planung; er macht Netzlogik und Raumansprüche sichtbar [B].
