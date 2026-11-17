# Bäume und Parkplätze – Methodenvorschlag (Teil 2, vor dem Bau)

Stand: 16.11.2026 · Branch `feature/trees-parking-stats` · Auftrag: `prompts/26_special_places_trees_parking.md`, 2.1

Dieser Vorschlag wartet auf dein OK. Gebaut ist bisher nur der Abruf der Daten. Beide Quellen sind geprüft und in
`config/sources.yaml` 0.1.13 eingetragen.

## Daten

| Quelle | Umfang | Abdeckung im Arbeitsgebiet (4 240 km) |
| --- | --- | --- |
| **Straßenbaumkataster** (BUKEA, WFS, dl-de/by-2.0) | 229 876 Bäume als Punkte, mit Kronendurchmesser und Pflanzjahr | ganz Hamburg; 80 % der Bäume liegen bis 10 m von der Achse entfernt, 94 % bis 20 m |
| **Öffentlicher Parkraum** (LBV, WFS, dl-de/by-2.0) – neu gefunden | 203 029 Flächen, fast alle *ein* Stellplatz (Längsparken: Median 5,2 × 2,1 m), mit Aufstellart und Bewirtschaftung | 28,6 % der Straßenlänge: Hamburg-Nord 77 %, Mitte 33 %, Altona 30 %, Eimsbüttel 27 %, Wandsbek 12 %, Harburg 7 %, Bergedorf 7 % |
| **OSM-Parktags** (`parking:left/right/both`, alt `parking:lane:*`) | Angabe vorhanden auf 26 % der Länge, davon Parken auf 15 % | Altona/Nord 25 %, Eimsbüttel 23 %, Mitte 16 %, Bergedorf 8 %, Harburg 7 %, Wandsbek 3 % |

**Folgerungen:**
- Die amtlichen Daten sind die bessere Quelle für Parkplätze. Auf 824 km gibt es dort Stellplätze, wo OSM nichts oder „kein Parken“ angibt.
- OSM ergänzt 246 km, auf denen es keine amtlichen Flächen gibt.
- Ohne jede Angabe bleiben grob 55–60 % der Straßenlänge, vor allem in Wandsbek, Harburg und Bergedorf.

## Parkplätze

**Heute, je Abschnitt und Seite (links/rechts der Achse):**
1. **Amtliche Flächen** (Quelle `hamburg`):
   - Jede Fläche im Straßenraum des Abschnitts zählt als ein Stellplatz. Zugeordnet wird sie dem nächsten Abschnitt bis zur halben Straßenraumbreite plus Toleranz; die Seite ergibt sich aus der Lage zur Achse.
   - Lange Flächen (Sammelflächen) zählen als Länge ÷ Stellplatzlänge der Aufstellart.
   - Flächen mit „Eingeschränktes Haltverbot“ zählen nicht. Flächen mit „Klärung“ zählen mit, als Spanne.
2. **Sonst OSM** (Quelle OSM; dafür muss `pipeline/lib/features.py` die Seiten getrennt behalten, statt sie wie heute zusammenzulegen):
   - Rechnung: nutzbare Bordlänge ÷ Stellplatzlänge der Aufstellart.
   - Nutzbare Bordlänge = Länge des Abschnitts − Abstand an Kreuzungen − Abzug für Einfahrten und Querungen.
3. **Sonst:** „keine Daten“. Fehlende Angaben zählen nie als 0.

**Im Ziel, je Seite:**
- Aus dem Soll-Querschnitt (`profile_elements`, mit den Abbaustufen D1/D2):
  - **Parkreihe bleibt:** Stellplätze im Ziel = min(heute, nutzbare Bordlänge ÷ 5,2 m). Das Ziel kennt nur Längsparken; Quer- und Schrägparken wird zu Längsparken.
  - **Keine Parkreihe:** 0.
  - **Heute unbekannt, im Ziel eine Reihe:** „keine Daten“ für heute; im Ziel höchstens Bordlänge ÷ 5,2 m.
- Daraus folgen: bleiben, entfallen, neu (neu nur, wo heute nachweislich kein Parken ist).
- **Besonderer Ort Schanze:** dieselbe Rechnung mit dem „Querschnitt im Vorschlag“. Fahrradstraße: Parken wie in unserem Ziel; Fußgängerzone: 0. Daraus der Satz „Im Vorschlag Schanze entfallen ≈ X Parkplätze“, mit dem Hinweis, dass der Vorschlag zum Parken nichts sagt.

**Zahlen für Bezirke und Hamburg:**
- Gezeigt werden „gezählt: X (auf Y % der Straßenlänge mit Daten)“ und eine Hochrechnung als breite Spanne. Für die Hochrechnung nehme ich Stellplätze je km aus den Abschnitten mit Daten, je Kategorie, das 25. bis 75. Perzentil.
- Wichtig: Wo die amtlichen Daten fehlen, heißt das „nicht erfasst“, nicht „kein Parken“. Darum gibt es keine Punktzahl ohne Spanne.

## Straßenbäume

1. **Zuordnung:** Jeder Baum gehört zum nächsten Abschnitt, wenn er höchstens halbe Straßenraumbreite (Haus zu Haus, `width_median_m`) plus 2 m von der Achse entfernt ist. Sonst ist er kein Straßenbaum dieses Netzes, zum Beispiel weil er im Park steht.
2. **Lage:** Seite und Abstand zur Achse (Projektion auf die Linie).
3. **Bänder im Ziel:** Aus `profile_elements` entstehen Bänder quer zur Achse.
   - Die Fahrbahn liegt mittig, die Seitenelemente folgen nach außen in ihrer Reihenfolge. Diese Hilfsfunktion kommt neu dazu, weil das Profil heute keine Abstände kennt.
   - Platz, den das Ziel nicht braucht, liegt als Rest außen an den Häusern.
4. **Einordnung:**
   - **bleibt:** im Baumstreifen, in der Parkreihe, in der Ladezone oder im Rest
   - **möglicherweise betroffen:** in Fahrbahn, Radweg, Radstreifen, Busspur oder Trennstreifen
   - **im Gehweg:** zählt in der unteren Schätzung als „bleibt“ (Baumscheibe im Gehweg), in der oberen als „möglicherweise betroffen“
5. **Spanne:** Die Bandgrenzen werden um die Lageunsicherheit verschoben (± 1,5 m). Daraus ergeben sich die kleinste und die größte Zahl „möglicherweise betroffen“.
6. **neu möglich:** Länge der neuen Baumstreifen im Ziel ÷ Baumabstand, abzüglich der Bäume, die dort schon stehen.
7. **Wortwahl:** immer „möglicherweise betroffen“, nie „wird gefällt“. Alle Werte als Spanne.

## Neue Annahmen (alle mit `source_type`, kommen nach `config/design_rules.yaml`)

| # | Wert | Vorschlag | source_type | Herkunft |
| --- | --- | --- | --- | --- |
| A1 | Stellplatzlänge längs | 5,2 m | hamburg | Median der amtlichen Längsflächen (LBV) |
| A2 | Stellplatzbreite quer (Bordlänge je Platz) | 2,5 m | hamburg | Median der amtlichen Querflächen |
| A3 | Bordlänge je Platz schräg | 3,9 m | assumption | Breite 2,7 m (amtlicher Median) bei 45° |
| A4 | Abstand an Kreuzungen | 5 m, vor Kreuzungen mit baulichem Radweg 8 m | de_regelwerk | StVO § 12 Abs. 3 Nr. 1 (Wortlaut geprüft) |
| A5 | Abzug für Einfahrten und Querungen (nur bei OSM) | aus den Abschnitten mit amtlichen Daten geeicht: Verhältnis gezählt ÷ rechnerisch | hamburg (abgeleitet) | wird beim Bau ermittelt und berichtet |
| A6 | Hochrechnung ohne Daten | Stellplätze je km nach Kategorie, 25.–75. Perzentil | assumption | – |
| A7 | Zuordnung Baum ↔ Abschnitt | halbe Straßenraumbreite + 2 m | assumption | – |
| A8 | Lageunsicherheit Baum und Bänder | ± 1,5 m | assumption | OSM-Achse etwa 1 m, Vereinfachung des Profils |
| A9 | Baumabstand „neu möglich“ | 12 m | assumption | übliche Spanne 8–15 m, am Regelwerk prüfen |

## C-PRI-10 (Grünanteil) auf das Kataster umstellen – deine Entscheidung aus Teil 1

- **Statt OSM-Einzelbäumen** (`natural=tree`) nehme ich die Kataster-Bäume. Der Kronenradius ist der halbe Kronendurchmesser, sofern er zwischen 1 und 30 m liegt; sonst gilt der bisherige `tree_crown_radius_m` (4 m).
- **Baumreihen** (`natural=tree_row`) bleiben aus OSM, weil das Kataster nur Punkte hat.
- **Umfang:** neue Version von `cycling_rules.yaml` mit CHANGELOG-Eintrag; neu gerechnet werden `make cycle-principles` und alles danach. Wie sich die Punkte ändern, steht im Bericht.

## Darstellung (wie besprochen)

- **Bezirke:** zwei Karten je Bezirk und für ganz Hamburg:
  - „Parkplätze: heute ≈ X, im Ziel ≈ Y (−Z)“
  - „Straßenbäume: X bleiben, Y möglicherweise betroffen, Z neu möglich“

  Je mit Stufe 2 (ein, zwei Sätze, was das heißt) und Stufe 3 (Methode, Spannen, Abdeckung).
- **Steckbrief:** dieselben drei Zahlen je Abschnitt auf Stufe 2. Ohne Daten steht dort „keine Daten“.
- **Methode:** neues Kapitel „Bäume und Parkplätze“ in drei Stufen.
- **Download:** neue Spalten je Abschnitt.
- **Ort Schanze:** der Satz zu den entfallenden Parkplätzen.

## Prüfung vor Veröffentlichung

- **`stats-qa`:** 30 Stichproben-Straßen, verteilt über die Bezirke und über die Fälle (amtlich, nur OSM, Bäume betroffen), werden mit Orthophoto- und Panoramax-Links verglichen. Gemessen wird die Fehlerquote; danach passe ich die Methode an.
- **Datentests:** keine fehlenden Werte als 0; Summen je Bezirk = Summe der Abschnitte; kein Baum und keine Fläche doppelt gezählt; Spannen geordnet.
