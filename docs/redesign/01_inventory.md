# Redesign 2026-11 · A1 Bestandsaufnahme

Stand: 14.11.2026, Branch `redesign/2026-11` (Basis `review/2026-11`, rules.yaml 0.21.0, cycling_rules.yaml 0.11.1,
design_rules.yaml 0.9.0). Geprüft wurde die gebaute Seite aus `web/dist` (Datenstand 28.10.2026, gleiche `meta.json` wie
`data/out`), lokal über `vite preview`. Alle Zahlen kommen aus Skripten in `analysis/redesign/` und lassen sich neu
erzeugen (Abschnitt „Wie gemessen“ am Ende). Die Tabellen zwischen den Markierungen `<!-- table:… -->` schreibt
`analysis/redesign/fill_tables.py`.

## Kurzfassung

1. **Die Seite hat viel Inhalt, aber keine Stufen.** Ein Straßen-Steckbrief hat 13 bis 15 Abschnitte mit 380 bis 560
   Wörtern und ist am Desktop 3 300 bis 4 500 px lang (4 bis 5 Bildschirmhöhen). Der größte Abschnitt sind die
   Datenquellen mit 160 Wörtern. Die Antwort auf „Was ist geplant?“ steht oben, die Begründung danach mit Regel-IDs.
   Alles Weitere steht ungeordnet gleichrangig darunter.
2. **13 Kartenebenen als Radioknöpfe, davon ist immer nur eine sichtbar.** Dazu kommen 4 Zusatzebenen und 4 Filtergruppen.
   Auf dem Smartphone (390 px) liegt das Bedienfeld über der Karte. Die Karte beginnt erst bei rund 1 050 px, und **bei
   keiner der 13 Ebenen ist die Legende ohne Scrollen sichtbar**. Netzlücken im Radnetz zeigt keine Ebene.
3. **Kürzel statt Wörter.** In den erfassten Texten stehen Kategorie-Kürzel (GOW30 89-mal, ETW30 70-mal), die
   Diskrepanztypen D1–D3 (104-mal D1, vor allem in der Tabelle) und 9 Regel-IDs. Die Tabelle, die Antwort auf
   „Wo ist der Handlungsbedarf am größten?“, zeigt nur Kürzel (GOW30, D1, D3).
4. **Lesbarkeit:** Die Seite ist mittelschwer (Wiener Sachtextformel 9,7, also etwa Klasse 10; Flesch-Amstad 51,5).
   Die Steckbriefe sind schwer (WSTF 11,3–14,3). Schwierig sind weniger die Sätze (im Mittel 9 Wörter) als lange
   Wörter und Fachbegriffe. Die Regeldateien sind schwer (WSTF 10,4–11,1, im Mittel 18 Wörter je Satz).
5. **Regeldateien:** Nur 23 von 196 Regeln sind für Laien verständlich beschrieben. 104 sind es teilweise, 69 nicht.
   14 Regeln haben gar keinen Text, darunter drei Stufen der Kategorie-Kaskade (C-ERF-01, C-G50-01, C-ETW-01). In 124
   Regeltexten steht Code (Variablennamen, Operatoren).
6. **Regelinventar:** 196 Regeln. 81 greifen im aktuellen Lauf nie, die meisten davon sind Vorverarbeitung, Prüfung oder
   Validierung. 47 entscheiden ein Ergebnis. 17 Regeln in 11 Gruppen sind Kandidaten zum Zusammenlegen, Vereinfachen oder
   Streichen (A6). Fast alle davon ändern kein Ergebnis.

## A1.1 Inhalte der Webseite

### Seiten

<!-- table:pages -->
| Seite | zeigt | erklärt | für wen | Wörter | WSTF | FRE | Höhe mobil | häufigste Fachbegriffe |
|---|---|---|---|---|---|---|---|---|
| [karte](img/c-karte-desktop.jpg) | Karte mit Bedienfeld (Ebenen, Legende, Zusatzebenen, Filter) | Ein Satz je Ebene, Legende | alle; Einstieg | 79 | – | – | 1 249 px | Ebene, SW, GOW50, GOW30, ETW30, ETW_ERF |
| [tabelle](img/c-tabelle-desktop.jpg) | Bezirksauswahl, dann alle Abschnitte des Bezirks nach Priorität | ein Satz | Fachleute, Politik | 1318 | 2,8 | 75,9 | 5 294 px | Kürzel D1, ETW30, GOW30, Kürzel D3, ETW_ERF, Diskrepanz |
| [methode](img/c-methode-desktop.jpg) | Kategorien, Kaskade, Unsicherheit, Diskrepanz, Grenzen, Änderungen | Methode der Straßenfunktion | Interessierte, Fachleute | 583 | 9,0 | 53,2 | 4 019 px | Kfz, Stadtmagistrale, Stadtstraße 30, Quartiersstraße, Aufenthaltsstraße, Schnellverkehrsstraße |
| [radnetz](img/c-radnetz-desktop.jpg) | Prinzipien, Ebenen, Radanlage, Querschnitt, Knoten, Grenzen | Methode Radnetz | Interessierte, Fachleute | 803 | 9,7 | 52,5 | 5 313 px | Steckbrief, Kfz, Knotentyp, Radvorrangroute, Quartiersnetz, Fahrradstraße |
| [downloads](img/c-downloads-desktop.jpg) | Tabelle der Dateien mit Format, Größe, Lizenz | kurz je Datei | Fachleute, Datennutzer | 162 | 14,4 | 32,6 | 1 995 px | Kürzel MB, Querschnitt, ODbL, Führungsform, Trennungsmatrix, dl-de |
| [quellen](img/c-quellen-desktop.jpg) | Datenquellen, Hintergrundkarte, Lizenzen, Quellenvermerke | Lizenzen | Datennutzer, rechtlich | 460 | 14,1 | 28,8 | 4 542 px | dl-de, OpenStreetMap, ODbL, BVM, OSM, Unfallatlas |
| [impressum](img/c-impressum-desktop.jpg) | Verantwortlich, Datenschutz | rechtlich | rechtlich | 96 | 11,6 | 38,4 | 1 351 px | OpenStreetMap, ODbL, Kürzel IP, Kürzel SIL, Kürzel MIT |
<!-- /table:pages -->

WSTF = Wiener Sachtextformel (Variante 1, ungefähr die Schulstufe, ab etwa 12 schwer). FRE = Flesch-Lesbarkeit nach
Amstad (0 sehr schwer bis 100 sehr leicht, unter 50 schwer). Die Tabelle-Seite hat nur kurze Zellen. Ihre Werte zeigen,
dass dort kaum Prosa steht, und sagen nichts über die Verständlichkeit.

### Bedienelemente und Rahmen

- **Banner** (immer sichtbar): „Entwurf: Nicht amtlicher Diskussionsentwurf – keine Planung oder Anordnung der Freien und
  Hansestadt Hamburg. Datenstand …, Regelwerk …“. Am Smartphone nimmt er drei Zeilen ein
  ([Bild](img/c-layer-cat-mobile.jpg)).
- **Navigation:** 7 gleichrangige Punkte (Karte, Tabelle, Methode, Radnetz, Downloads, Quellen & Lizenzen, Impressum).
  Am Smartphone stehen sie in drei Zeilen.
- **Suche:** findet nur Straßennamen (8 396 Einträge in `search.json`), keine Knotenpunkte. Sie zoomt auf die Straße,
  öffnet aber keinen Steckbrief (Aufgabe t1).
- **Bedienfeld „Ebenen, Legende und Filter“:** zwei Gruppen mit Radioknöpfen (6 Ebenen Straßenfunktion, 7 Ebenen
  Radverkehr). Darunter folgen ein Erklärsatz der Ebene, die Legende, 4 Zusatzebenen als Kästchen (Busverkehr, Radnetz
  Hamburg, Schulen und Kitas, Unfälle) und die aufklappbaren Filter (Bezirk, Soll-Kategorie, Diskrepanztyp, Priorität
  mindestens). Am Desktop ist das Feld 1 180 px hoch, die Legende beginnt unter allen 13 Radioknöpfen.
- **Tooltips und Popups:** keine. Beim Überfahren ändert sich nur der Mauszeiger (`web/src/map.js:111`). Ein Klick öffnet
  den Steckbrief.
- **Steckbrief:** Am Desktop ist er ein Seitenpanel, am Smartphone eine Vollseite über der Karte.
- **Hinweis auf den Entwurfsstatus:** Er steht im Banner, in der Meta-Beschreibung, im Impressum und in der
  Kartenzuschreibung. Ein eigener Hinweis gilt für die Radverkehrsebenen (Legende, Steckbrief, Radnetz-Seite).
- **`docs/source_policy.md`:** Die Datei, auf die der Prompt verweist, gibt es weiterhin nicht (schon im Review 2026-11
  festgestellt). Die Quellenregeln stehen in CLAUDE.md und `docs/guide.md`.

### Kartenebenen und Legenden

<!-- table:layers -->
| Ebene | Schlüssel | Erklärsatz | Legendeneinträge | Wörter | Legende sichtbar (Desktop) | Legende sichtbar (mobil, ohne Scrollen) | Fachbegriffe |
|---|---|---|---|---|---|---|---|
| [Soll-Kategorie](img/c-layer-cat-desktop.jpg) | cat | Welche Funktion die Straße nach Duurzaam Veilig haben soll (Vorschlag). | 6 | 32 | ja | nein | Duurzaam Veilig, SW, Schnellverkehrsstraße, GOW50 |
| [Ist-Tempo](img/c-layer-speed-desktop.jpg) | speed | Heute zulässige Höchstgeschwindigkeit (amtlich, sonst OpenStreetMap). | 7 | 27 | ja | nein | OpenStreetMap |
| [Diskrepanz](img/c-layer-disc-desktop.jpg) | disc | Wo heutiges Tempo, Gestaltung oder Verkehrsmenge nicht zur Soll-Kategorie passen. Breitere Linie = stärkere Diskrepanz. | 6 | 49 | ja | nein | Diskrepanz, Soll-Kategorie, Kürzel D1, Verbindungsfunktion |
| [Straßenraumbreite](img/c-layer-width-desktop.jpg) | width | Breite von Grundstücksgrenze zu Grundstücksgrenze an Engstellen. | 5 | 37 | ja | nein | Quartiersstraße, Stadtmagistrale |
| [Machbarkeit](img/c-layer-feas-desktop.jpg) | feas | Passt der Soll-Querschnitt der eigenen Kategorie in den Straßenraum? | 5 | 24 | ja | nein | Soll-Querschnitt |
| [Hauptverkehrsstraßen (Vergleich)](img/c-layer-hvs-desktop.jpg) | hvs | Hauptverkehrsstraßennetz der BVM zum Vergleich mit der Soll-Kategorie. | 3 | 20 | ja | nein | BVM, Soll-Kategorie |
| [Radnetz (Soll)](img/c-layer-cnet-desktop.jpg) | cnet | Vorgeschlagenes Radnetz in vier Ebenen: Radvorrangroute, Radroute, Bezirksroute und Quartiersnetz. | 5 | 48 | ja | nein | Radvorrangroute, Bezirksroute, Quartiersnetz, RSV |
| [Radanlagen (Soll)](img/c-layer-cfac-desktop.jpg) | cfac | Welche Radverkehrsanlage der Abschnitt nach dem Entwurf haben soll – nach der Prüfung, ob der Platz reicht. | 7 | 58 | ja | nein | Radfahrstreifen, Fahrradstraße, Mischverkehr |
| [Radanlagen Soll/Ist](img/c-layer-cgap-desktop.jpg) | cgap | Wo die heutige Radanlage (aus OpenStreetMap) fehlt, eine andere ist als im Soll oder zu schmal ist. | 7 | 59 | ja | nein | OpenStreetMap |
| [Fahrstreifen Soll/Ist](img/c-layer-lanes-desktop.jpg) | lanes | Kfz-Fahrstreifen je Richtung im Soll-Querschnitt im Vergleich zu heute. | 6 | 50 | ja | nein | Kfz, Soll-Querschnitt, Mischverkehr |
| [Querschnitt passt?](img/c-layer-cfit-desktop.jpg) | cfit | Passen Gehwege, Radanlage, Fahrbahn, Bäume und Parken des Soll-Querschnitts in den Straßenraum? | 5 | 52 | ja | nein | – |
| [Knotenpunkte](img/c-layer-jct-desktop.jpg) | jct | Vorgeschlagener Knotentyp; Form und Farbe zeigen den Typ, größere Zeichen: Umbau nötig. Sichtbar ab Zoomstufe 12. | 8 | 72 | ja | nein | Knotentyp, Furt |
| [Radnetz Hamburg (amtlich)](img/c-layer-coff-desktop.jpg) | coff | Amtliches Radnetz Hamburg zum Vergleich; grau darunter das vorgeschlagene Soll-Radnetz (Radvorrangrouten und Radrouten). | 5 | 63 | ja | nein | RSV, HAUPT, dl-de |
<!-- /table:layers -->

„Legende sichtbar (mobil)“ heißt: Nach dem Laden der Ebene liegt die Legende ganz oder teilweise im ersten Bildschirm
(390 × 844 px). Das ist bei keiner Ebene der Fall, weil Banner, Navigation, Suche und alle 13 Radioknöpfe davor stehen
([Bild](img/c-layer-cat-mobile.jpg)).

### Steckbriefe

<!-- table:profiles -->
| Steckbrief | Beispiel | Abschnitte | Wörter | Länge Desktop | Länge mobil | WSTF | FRE | Fachbegriffe |
|---|---|---|---|---|---|---|---|---|
| [SW](img/c-profile-SW-desktop.jpg) | Deckel Stellingen | 14 | 379 | 3 325 px | 3 661 px | 13,7 | 34,6 | dl-de, OpenStreetMap, ODbL, Schnellverkehrsstraße, SW, Querschnitt |
| [GOW50](img/c-profile-GOW50-desktop.jpg) | Farnhornstieg | 13 | 531 | 4 287 px | 4 625 px | 11,8 | 42,9 | dl-de, OpenStreetMap, ODbL, Kfz, Stadtmagistrale, HAUPT |
| [GOW30](img/c-profile-GOW30-desktop.jpg) | Kieler Straße | 14 | 558 | 4 418 px | 4 900 px | 11,3 | 47,7 | OpenStreetMap, dl-de, Kfz, ODbL, Stadtstraße 30, HAUPT |
| [ETW30](img/c-profile-ETW30-desktop.jpg) | Schippelsweg | 15 | 506 | 4 517 px | 4 908 px | 13,3 | 38,3 | dl-de, OpenStreetMap, Kfz, Quartiersstraße, ODbL, ETW |
| [ETW_ERF](img/c-profile-ETW_ERF-desktop.jpg) | Alte Elbgaustraße | 14 | 390 | 3 540 px | 3 831 px | 14,3 | 34,7 | dl-de, OpenStreetMap, ODbL, Mischverkehr, Aufenthaltsstraße, Kfz |
| [Knoten](img/c-junction-desktop.jpg) | Altonaer Straße / Max-Brauer-Allee / Schulterblatt | 6 | 162 | – | – | 9,0 | 52,8 | Kfz, GOW30, ETW30, Gehwegüberfahrt, RSV, HAUPT |
<!-- /table:profiles -->

Abschnitte je Steckbrief (Wörter):

<!-- table:profile_sections -->
| Abschnitt im Steckbrief | SW | GOW50 | GOW30 | ETW30 | ETW_ERF |
|---|---|---|---|---|---|
| (Titel) | 6 | 6 | 6 | 6 | 6 |
| Soll-Kategorie | 13 | 13 | 19 | 14 | 10 |
| Begründung | 9 | 47 | 31 | 17 | 3 |
| Datenunsicherheit | 16 | 16 | 16 | 23 | 16 |
| Robustheit der Einstufung | 11 | 11 | 11 | 11 | 11 |
| Ist-Zustand | 19 | 21 | 21 | 26 | 22 |
| Querschnitt | 9 | 24 | 24 | 24 | 9 |
| Diskrepanz und Priorität | 31 | 47 | 53 | 35 | 30 |
| Radverkehr und Soll-Querschnitt | 57 | 76 | 75 | 61 | 56 |
| Soll-Querschnitt | 9 | 76 | 40 | 39 | 24 |
| Hinweise | 5 | – | 68 | 52 | 9 |
| Robustheit | 21 | 21 | 21 | 21 | 21 |
| Datenquellen | 160 | 160 | 160 | 160 | 160 |
| Rückmeldung zu diesem Abschnitt | 13 | 13 | 13 | 13 | 13 |
| Hinweise der Netzprüfung | – | – | – | 4 | – |
<!-- /table:profile_sections -->

Befunde aus den Steckbriefen:

- **Drei Abschnitte zum Querschnitt:** „Querschnitt“ (Straßenraum, Machbarkeit der Kategorie), „Radverkehr und
  Soll-Querschnitt“ und darin „Soll-Querschnitt“. Sie enthalten zwei verschiedene Machbarkeitsaussagen. Beispiel
  Hallerstraße: „passt“ (Querschnitt) und „passt in den Straßenraum“ (Soll-Querschnitt Radverkehr), siehe Aufgabe t2.
- **Zwei Abschnitte „Robustheit“** mit verschiedenem Inhalt: Robustheit der Einstufung (Kategorie) und Robustheit
  (Radverkehr).
- **„Datenquellen“ ist der längste Abschnitt** (160 Wörter, 29–42 % des Steckbriefs) und bei allen Abschnitten gleich.
  Er gehört auf Ebene 3 oder auf die Quellenseite.
- **Begründung mit Regel-IDs:** Jede Begründungszeile endet mit einer Regel-ID in Klammern, zum Beispiel
  „(C-G30-01)“. Für Laien ist das Rauschen, für Fachleute die Spur ins Regelwerk.
- **Gründe dafür und dagegen sehen gleich aus:** Die Begründung listet auch Prüfungen, die *nicht* zugetroffen haben
  (`reasons[].passed = false`), mit derselben Formatierung (`web/src/panel.js:185`). Das betrifft 31 115 von 33 712
  Steckbriefen (92 %): C-GOW-01 in 24 711, C-G30-02 in 5 744 und C-G30-01 in 3 751 Steckbriefen. Beispiel
  Hallerstraße: „Platz für einen baulichen Radweg neben der Busfahrbahn: Straßenraum 22,9 m (nötig 17,5 m)“ steht als
  Grund da. Diese Prüfung hat aber nicht gegriffen, sie erklärt nur, warum der Platz *nicht* der Auslöser für Tempo 30
  ist.
- **Zwei verschiedene Ist-Aussagen zum Radverkehr:** „Ist-Zustand → Radverkehr“ kommt aus `s09_export._cycling`
  (OSM-Tags am Abschnitt), „Radanlage heute“ aus der Ist-Führung C-FAC-05/S-FEAT-13. Bei 93 Abschnitten widersprechen sie
  sich. Bei 66 davon ist es eine Fahrradstraße, bei 27 ein Radfahrstreifen, der oben als „keine Radverkehrsanlage“
  erscheint. Beispiel Hallerstraße: oben „keine Radverkehrsanlage (Radverkehr auf der Fahrbahn)“, unten
  „Radfahrstreifen“.

### Methodenteil, Downloads, Lizenzen

- **Methode** (583 Wörter, 7 Abschnitte): gut verständlich (WSTF 9,0). Er ist aber von Hand in `web/src/pages.js`
  geschrieben, und nur Kategorietexte, Versionen und Sensitivitätswerte kommen aus den Daten. Die Kaskade ist dort ein
  zweites Mal beschrieben, unabhängig vom Regelwerk. Eine Regelreferenz fehlt, verwiesen wird nur auf den Download
  `rules.yaml`.
- **Radnetz** (803 Wörter, 8 Abschnitte): ebenfalls von Hand geschrieben, nach `docs/guide_radnetz.md`.
- **Downloads** (162 Wörter): eine Dateitabelle mit Fachwörtern (Führungsform, Trennungsmatrix, ODbL, dl-de). WSTF 14,4
  ist der schwerste Wert der Seite.
- **Quellen & Lizenzen** (460 Wörter): rechtlich nötig, schwer lesbar (WSTF 14,1, 32 % der Sätze über 15 Wörter).

### Woher die Texte kommen

Die Texte stehen an vier Stellen:

- von Hand in `web/src/pages.js`, `layers.js` (`LAYER_INFO`, `OVERLAY_INFO`), `main.js` (Bedienfeld) und `panel.js`
  (Überschriften, Beschriftungen)
- in `config/plain_language.yaml` (Kategorien, Begründungsbausteine je Regel, Hinweise, Spalten, Hinweis auf den
  Entwurfsstatus), über `meta.json` und die Steckbrief-JSON
- in `config/project.yaml` (Titel, Impressum)
- im Python-Code (`pipeline/s09_export.py`: `DOWNLOAD_TEXTS`, Datenbeschreibung)

Ein Begriff kann darum an mehreren Stellen verschieden heißen, zum Beispiel „Soll-Querschnitt“ und „Querschnitt
passt?“.

## A1.2 Aufgabentest

Fünf Aufgaben, jeweils am Desktop (1440 × 900) und am Smartphone (390 × 844), mit Playwright gegen die gebaute Seite
(`analysis/redesign/ui/tasks.mjs`, nach dem Muster aus dem Review 2026-11). Die Zeit ist eine Schätzung nach dem
Keystroke-Level-Modell (Card/Moran/Newell 1983) plus Lesezeit bei 200 Wörtern je Minute. Diese Werte sind Annahmen,
also eine Vergleichsgröße und keine Messung an Menschen.

<!-- table:tasks -->
| Aufgabe | Frage | Gerät | Schritte | Klicks | Tasten | Scrollen | Wörter gelesen | Zeit (KLM, s) | JS-Fehler |
|---|---|---|---|---|---|---|---|---|---|
| t1 | Was ist für meine Straße geplant, und warum? | desktop | 5 | 3 | 9 | 0 | 55 | 30 | 0 |
| t2 | Passt der geplante Querschnitt in die Straße? | desktop | 3 | 0 | 0 | 4 | 304 | 101 | 0 |
| t3 | Wo hat mein Bezirk den größten Handlungsbedarf? | desktop | 5 | 4 | 0 | 0 | 60 | 30 | 0 |
| t4 | Wie sieht das Radnetz aus, wo sind Lücken? | desktop | 4 | 4 | 0 | 0 | 77 | 34 | 0 |
| t5 | Was ändert sich an diesem Knotenpunkt? | desktop | 7 | 6 | 10 | 0 | 74 | 44 | 0 |
| t1 | Was ist für meine Straße geplant, und warum? | mobile | 5 | 3 | 9 | 1 | 55 | 33 | 0 |
| t2 | Passt der geplante Querschnitt in die Straße? | mobile | 3 | 0 | 0 | 6 | 304 | 103 | 0 |
| t3 | Wo hat mein Bezirk den größten Handlungsbedarf? | mobile | 5 | 4 | 0 | 1 | 60 | 31 | 0 |
| t4 | Wie sieht das Radnetz aus, wo sind Lücken? | mobile | 4 | 4 | 0 | 1 | 77 | 35 | 0 |
| t5 | Was ändert sich an diesem Knotenpunkt? | mobile | 7 | 6 | 10 | 1 | 74 | 47 | 0 |
<!-- /table:tasks -->

<!-- table:task_paths -->
**t1** – Klickpfad (Desktop):
1. Startseite: Karte von Hamburg ([Desktop](img/t1-desktop-01.jpg), [mobil](img/t1-mobile-01.jpg))
2. Suchfeld antippen, „Hallerstr" tippen ([Desktop](img/t1-desktop-02.jpg), [mobil](img/t1-mobile-02.jpg))
3. Vorschlag „Hallerstraße" wählen – Karte zoomt auf die Straße ([Desktop](img/t1-desktop-03.jpg), [mobil](img/t1-mobile-03.jpg))
4. Linie der Hallerstraße antippen ([Desktop](img/t1-desktop-04.jpg), [mobil](img/t1-mobile-04.jpg))
5. Steckbrief lesen: Soll-Kategorie und Begründung ([Desktop](img/t1-desktop-05.jpg), [mobil](img/t1-mobile-05.jpg))

Wörter, die das Verständnis blockieren (im gelesenen Text, Anzahl): Stadtstraße 30 (2), GOW (1), GOW30 (1), Soll (1), Soll-Kategorie (1), Kfz (1), BVM (1), Radfahrstreifen (1), C-GOW-01 (1), C-G30-01 (1), C-G30-02 (1)

Hänger:
- Die Suche zoomt nur auf die Straße; der Steckbrief öffnet sich nicht. Man muss die Linie auf der Karte treffen.
- Nach der Suche zeigt der Bildschirm nur 17 % Karte (Kartenoberkante bei 701 px von 844 px); das aufgeklappte Bedienfeld liegt darüber.

**t2** – Klickpfad (Desktop):
1. Zur Diskrepanz scrollen und lesen ([Desktop](img/t2-desktop-01.jpg), [mobil](img/t2-mobile-01.jpg))
2. Querschnitt (Straße) lesen ([Desktop](img/t2-desktop-02.jpg), [mobil](img/t2-mobile-02.jpg))
3. Radverkehr und Soll-Querschnitt lesen (zweite Querschnitts-Angabe) ([Desktop](img/t2-desktop-03.jpg), [mobil](img/t2-mobile-03.jpg))

Wörter, die das Verständnis blockieren (im gelesenen Text, Anzahl): Soll (12), Kfz (6), Radfahrstreifen (3), OpenStreetMap (3), Priorität (2), Querschnitt (2), Soll-Querschnitt (2), BASIS (2), Diskrepanz (1), DTV (1), Stadtstraße 30 (1), Kürzel D3 (1), Soll-Kategorie (1), Machbarkeit (1), Engstelle (1), Ist (1), Bezirksroute (1), Schutzstreifen (1), Robustheit (1), Datenunsicherheit (1), Verkehrsfläche (1), Kürzel DE (1), Kürzel NL (1)

Hänger:
- Zwei Machbarkeitsaussagen im selben Steckbrief: „passt" (Querschnitt) und „passt in den Straßenraum" (Soll-Querschnitt Radverkehr).

**t3** – Klickpfad (Desktop):
1. Startseite ([Desktop](img/t3-desktop-01.jpg), [mobil](img/t3-mobile-01.jpg))
2. „Tabelle" wählen ([Desktop](img/t3-desktop-02.jpg), [mobil](img/t3-mobile-02.jpg))
3. Bezirk „Eimsbüttel" wählen ([Desktop](img/t3-desktop-03.jpg), [mobil](img/t3-mobile-03.jpg))
4. Obersten Eintrag öffnen ([Desktop](img/t3-desktop-04.jpg), [mobil](img/t3-mobile-04.jpg))
5. „Auf der Karte zeigen" ([Desktop](img/t3-desktop-05.jpg), [mobil](img/t3-mobile-05.jpg))

Wörter, die das Verständnis blockieren (im gelesenen Text, Anzahl): GOW30 (5), Kürzel D1 (4), Diskrepanz (1), Soll (1), Ist (1), Robustheit (1), Datenunsicherheit (1), Priorität (1), Steckbrief (1), Kürzel D3 (1)

Hänger:
- Die Tabelle ist nach Priorität sortiert, zeigt aber Kürzel (GOW30, ETW30, D3, D1) und keine Ortsangabe außer dem Straßennamen.
- Handlungsbedarf beim Radverkehr (Radanlagen fehlen, Querschnitt passt nicht) und an Knoten (Rangliste priority_rank) fehlt in der Tabelle; sie enthält nur Straßenabschnitte und ihre Diskrepanz.
- Die Tabelle ist breiter als der Bildschirm (waagerecht scrollen).
- „Auf der Karte zeigen" ist nicht bedienbar: Die Seite ist 1021 px breit bei 390 px sichtbarer Breite (breite Tabelle); der Steckbrief reicht von 0 bis 1021 px, die Schaltfläche liegt bei 700–879 px und damit außerhalb des sichtbaren Bereichs.

**t4** – Klickpfad (Desktop):
1. Startseite ([Desktop](img/t4-desktop-01.jpg), [mobil](img/t4-mobile-01.jpg))
2. Ebene „Radnetz (Soll)" wählen ([Desktop](img/t4-desktop-02.jpg), [mobil](img/t4-mobile-02.jpg))
3. Ebene „Radanlagen Soll/Ist" wählen ([Desktop](img/t4-desktop-03.jpg), [mobil](img/t4-mobile-03.jpg))
4. Kartenausschnitt Eimsbüttel heranzoomen (zweimal +) ([Desktop](img/t4-desktop-04.jpg), [mobil](img/t4-mobile-04.jpg))

Wörter, die das Verständnis blockieren (im gelesenen Text, Anzahl): Soll (4), Radvorrangroute (2), Bezirksroute (2), Quartiersnetz (2), RSV (1), HAUPT (1), BASIS (1), ERSCHL (1), Erschließung (1), Ist (1), OpenStreetMap (1)

Hänger:
- Keine Ebene zeigt Lücken im Netz (fehlende Verbindungen, Maschen); Ebenen: Soll-Kategorie, Ist-Tempo, Diskrepanz, Straßenraumbreite, Machbarkeit, Hauptverkehrsstraßen (Vergleich), Radnetz (Soll), Radanlagen (Soll), Radanlagen Soll/Ist, Fahrstreifen Soll/Ist, Querschnitt passt?, Knotenpunkte, Radnetz Hamburg (amtlich). „Radanlagen Soll/Ist" zeigt nur fehlende oder abweichende Radanlagen auf vorhandenen Abschnitten. Es ist immer nur eine Ebene sichtbar.

**t5** – Klickpfad (Desktop):
1. Startseite ([Desktop](img/t5-desktop-01.jpg), [mobil](img/t5-mobile-01.jpg))
2. Suchfeld antippen, „Schulterbl" tippen ([Desktop](img/t5-desktop-02.jpg), [mobil](img/t5-mobile-02.jpg))
3. Vorschlag „Schulterblatt" wählen – Karte zoomt auf die Straße ([Desktop](img/t5-desktop-03.jpg), [mobil](img/t5-mobile-03.jpg))
4. Kreuzung in der Standard-Ebene antippen (öffnet einen Straßen-Steckbrief, keinen Knoten) ([Desktop](img/t5-desktop-04.jpg), [mobil](img/t5-mobile-04.jpg))
5. Ebene „Knotenpunkte" wählen ([Desktop](img/t5-desktop-05.jpg), [mobil](img/t5-mobile-05.jpg))
6. Knotensymbol Altonaer Straße / Max-Brauer-Allee / Schulterblatt antippen ([Desktop](img/t5-desktop-06.jpg), [mobil](img/t5-mobile-06.jpg))
7. Knoten-Steckbrief lesen: Soll-Knotentyp ([Desktop](img/t5-desktop-07.jpg), [mobil](img/t5-mobile-07.jpg))

Wörter, die das Verständnis blockieren (im gelesenen Text, Anzahl): Soll (2), Kfz (2), Gehwegüberfahrt (2), Furt (1), Knotentyp (1), GOW30 (1), ETW30 (1), Verkehrsfläche (1), J-05 (1)

Hänger:
- In der Standard-Ebene öffnet ein Tipp auf die Kreuzung den Straßen-Steckbrief „Schulterblatt"; Knoten sind nur in der Rad-Ebene „Knotenpunkte" anklickbar, die Suche findet keine Knoten.
<!-- /table:task_paths -->

Zusammengefasst:

- **t1** gelingt in 5 Schritten. Die Suche öffnet aber keinen Steckbrief, man muss die Linie treffen. Am Smartphone
  bleiben nach der Suche 17 % Karte.
- **t2** ist die teuerste Aufgabe: 304 Wörter in drei Abschnitten, mit zwei Machbarkeitsaussagen.
- **t3** endet in einer Kürzeltabelle ohne Radverkehr und Knoten. Am Smartphone ist „Auf der Karte zeigen“ nicht
  erreichbar.
- **t4** zeigt das Netz, aber keine Lücken.
- **t5** braucht das Wissen, dass Knoten nur in der Ebene „Knotenpunkte“ anklickbar sind.

## A1.3 Lesbarkeit

<!-- table:readability -->
| Quelle: Gruppe | Einheiten | Wörter | Anteil Stichwörter | Sätze | WSTF | FRE (Amstad) | Ø Satzlänge | Anteil Sätze > 15 W. | Anteil Passiv | Anteil lange Subst. |
|---|---|---|---|---|---|---|---|---|---|---|
| Klartexte: plain_language.yaml | 291 | 1701 | 21 % | 157 | 11,2 | 43,7 | 8,6 | 5 % | 1 % | 6 % |
| Regeldatei: cycling_rules.yaml | 139 | 3188 | 4 % | 167 | 11,1 | 36,6 | 18,4 | 44 % | 7 % | 4 % |
| Regeldatei: design_rules.yaml | 81 | 1932 | 2 % | 101 | 10,5 | 41,1 | 18,7 | 39 % | 5 % | 4 % |
| Regeldatei: rules.yaml | 132 | 3623 | 2 % | 200 | 10,4 | 47,0 | 17,7 | 45 % | 7 % | 3 % |
| Webseite: Ebene/Legende | 13 | 550 | 24 % | 51 | 12,9 | 47,1 | 8,2 | 4 % | 0 % | 7 % |
| Webseite: Rahmen | 2 | 16 | 19 % | 1 | – | – | 13,0 | 0 % | 0 % | 8 % |
| Webseite: Seite downloads | 1 | 161 | 12 % | 15 | 14,4 | 32,6 | 9,5 | 7 % | 0 % | 7 % |
| Webseite: Seite impressum | 4 | 98 | 16 % | 7 | 11,6 | 38,4 | 11,7 | 14 % | 0 % | 8 % |
| Webseite: Seite karte | 1 | 75 | 63 % | 4 | – | – | 7,0 | 0 % | 0 % | 7 % |
| Webseite: Seite methode | 7 | 562 | 2 % | 52 | 9,0 | 53,2 | 10,5 | 15 % | 10 % | 5 % |
| Webseite: Seite quellen | 4 | 453 | 1 % | 31 | 14,1 | 28,8 | 14,4 | 32 % | 3 % | 11 % |
| Webseite: Seite radnetz | 8 | 788 | 0 % | 69 | 9,7 | 52,5 | 11,4 | 20 % | 4 % | 5 % |
| Webseite: Seite tabelle | 1 | 815 | 17 % | 106 | 2,8 | 75,9 | 6,4 | 1 % | 0 % | 1 % |
| Webseite: Steckbrief ETW30 | 15 | 434 | 33 % | 35 | 13,3 | 38,3 | 8,3 | 3 % | 3 % | 9 % |
| Webseite: Steckbrief ETW_ERF | 14 | 342 | 35 % | 26 | 14,3 | 34,7 | 8,5 | 4 % | 4 % | 9 % |
| Webseite: Steckbrief GOW30 | 14 | 464 | 33 % | 36 | 11,3 | 47,7 | 8,7 | 3 % | 3 % | 7 % |
| Webseite: Steckbrief GOW50 | 13 | 443 | 34 % | 35 | 11,8 | 42,9 | 8,4 | 3 % | 3 % | 9 % |
| Webseite: Steckbrief Knoten | 6 | 139 | 15 % | 12 | 9,0 | 52,8 | 9,8 | 0 % | 0 % | 7 % |
| Webseite: Steckbrief SW | 14 | 340 | 33 % | 26 | 13,7 | 34,6 | 8,7 | 4 % | 4 % | 10 % |
<!-- /table:readability -->

„Anteil Stichwörter“ ist der Anteil der Wörter in Bruchstücken unter 5 Wörtern: Legendeneinträge, Beschriftungen,
Tabellenzellen. Sie gehen nicht in die Satzmaße ein. Lesart: Unter 50 bei FRE und über 12 bei WSTF gilt als schwer.
Zielwerte für Einfache Sprache (B1) legt keine der beiden Formeln fest. Für A4 setzen wir als Annahme WSTF ≤ 8 und
FRE ≥ 60 (siehe `04_language.md`).

**Fachbegriffe und Kürzel** (die 60 häufigsten; vollständig in `data/scenarios/redesign/readability_terms.csv`):

<!-- table:terms -->
| Begriff | Vorkommen | Orte | wo |
|---|---|---|---|
| Soll | 154 | 16 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite downloads; Webseite: Seite karte; Webseite: Seite methode; Webseite: Seite quellen; Webseite: Seite radnetz; Webseite: Seite tabelle; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief SW |
| Kürzel D1 | 104 | 7 | Klartexte: plain_language.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite tabelle; Webseite: Steckbrief ETW30; Webseite: Steckbrief GOW30 |
| GOW30 | 89 | 10 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite karte; Webseite: Seite methode; Webseite: Seite tabelle; Webseite: Steckbrief GOW30; Webseite: Steckbrief Knoten |
| Ist | 87 | 16 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite downloads; Webseite: Seite karte; Webseite: Seite methode; Webseite: Seite quellen; Webseite: Seite tabelle; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief Knoten; Webseite: Steckbrief SW |
| Kfz | 80 | 13 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite methode; Webseite: Seite radnetz; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief Knoten; Webseite: Steckbrief SW |
| ETW30 | 70 | 10 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite karte; Webseite: Seite methode; Webseite: Seite tabelle; Webseite: Steckbrief ETW30; Webseite: Steckbrief Knoten |
| dl-de | 59 | 8 | Webseite: Ebene/Legende; Webseite: Seite downloads; Webseite: Seite quellen; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief SW |
| OpenStreetMap | 58 | 12 | Klartexte: plain_language.yaml; Webseite: Ebene/Legende; Webseite: Seite impressum; Webseite: Seite methode; Webseite: Seite quellen; Webseite: Seite radnetz; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief Knoten; Webseite: Steckbrief SW |
| OSM | 52 | 6 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Seite quellen; Webseite: Steckbrief SW |
| Abschnitt | 50 | 15 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite downloads; Webseite: Seite karte; Webseite: Seite methode; Webseite: Seite quellen; Webseite: Seite radnetz; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief SW |
| GOW50 | 33 | 8 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite karte; Webseite: Seite methode; Webseite: Steckbrief GOW50 |
| ODbL | 31 | 8 | Webseite: Seite downloads; Webseite: Seite impressum; Webseite: Seite quellen; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief SW |
| RSV | 31 | 7 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite radnetz; Webseite: Steckbrief Knoten |
| HAUPT | 26 | 10 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite radnetz; Webseite: Steckbrief ETW30; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief Knoten |
| DTV | 26 | 4 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml |
| GOW | 24 | 5 | Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Steckbrief ETW30; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50 |
| SW | 22 | 7 | Klartexte: plain_language.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite karte; Webseite: Seite methode; Webseite: Steckbrief SW |
| Radfahrstreifen | 19 | 8 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite methode; Webseite: Seite radnetz; Webseite: Steckbrief GOW30 |
| Mischverkehr | 19 | 8 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief Knoten |
| Fahrradstraße | 19 | 8 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite radnetz; Webseite: Steckbrief ETW30; Webseite: Steckbrief Knoten |
| Annahme | 18 | 5 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Seite radnetz |
| Querschnitt | 18 | 11 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: rules.yaml; Webseite: Seite downloads; Webseite: Seite karte; Webseite: Seite radnetz; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief SW |
| Schwelle | 18 | 8 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: rules.yaml; Webseite: Seite methode; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief SW |
| BASIS | 17 | 7 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite radnetz; Webseite: Steckbrief Knoten |
| ALKIS | 17 | 9 | Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Seite quellen; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief SW |
| Stadtmagistrale | 17 | 7 | Klartexte: plain_language.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite karte; Webseite: Seite methode; Webseite: Seite radnetz; Webseite: Steckbrief GOW50 |
| Quartiersstraße | 15 | 7 | Klartexte: plain_language.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite karte; Webseite: Seite methode; Webseite: Seite radnetz; Webseite: Steckbrief ETW30 |
| CROW | 15 | 4 | Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Seite radnetz |
| Ebene | 15 | 5 | Regeldatei: cycling_rules.yaml; Regeldatei: rules.yaml; Webseite: Seite karte; Webseite: Seite quellen; Webseite: Seite radnetz |
| ETW_ERF | 14 | 9 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite karte; Webseite: Seite methode; Webseite: Seite tabelle; Webseite: Steckbrief ETW_ERF |
| Soll-Kategorie | 14 | 9 | Klartexte: plain_language.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite karte; Webseite: Seite methode; Webseite: Seite radnetz; Webseite: Steckbrief ETW30; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50 |
| Straßenraumbreite | 14 | 9 | Klartexte: plain_language.yaml; Webseite: Seite karte; Webseite: Seite methode; Webseite: Seite quellen; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief SW |
| GTFS | 13 | 9 | Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Seite quellen; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief SW |
| Kürzel MB | 13 | 1 | Webseite: Seite downloads |
| Priorität | 13 | 11 | Klartexte: plain_language.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Seite methode; Webseite: Seite tabelle; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief Knoten; Webseite: Steckbrief SW |
| Verkehrsfläche | 12 | 8 | Klartexte: plain_language.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief Knoten |
| Diskrepanz | 12 | 8 | Klartexte: plain_language.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite karte; Webseite: Seite methode; Webseite: Seite tabelle; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF |
| confidence | 12 | 3 | Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml |
| Datenunsicherheit | 12 | 9 | Klartexte: plain_language.yaml; Webseite: Seite methode; Webseite: Seite tabelle; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief Knoten; Webseite: Steckbrief SW |
| Unfallatlas | 11 | 9 | Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Seite quellen; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief SW |
| Stadtstraße 30 | 11 | 7 | Klartexte: plain_language.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite karte; Webseite: Seite methode; Webseite: Seite radnetz; Webseite: Steckbrief GOW30 |
| Steckbrief | 11 | 5 | Regeldatei: cycling_rules.yaml; Regeldatei: rules.yaml; Webseite: Seite methode; Webseite: Seite radnetz; Webseite: Seite tabelle |
| Kaskade | 10 | 2 | Klartexte: plain_language.yaml; Regeldatei: rules.yaml |
| Fallback | 10 | 4 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml |
| Kürzel HVV | 10 | 8 | Klartexte: plain_language.yaml; Regeldatei: rules.yaml; Webseite: Seite quellen; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief SW |
| Schnellverkehrsstraße | 9 | 6 | Klartexte: plain_language.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite karte; Webseite: Seite methode; Webseite: Steckbrief SW |
| Knotenpunkt | 9 | 4 | Klartexte: plain_language.yaml; Regeldatei: design_rules.yaml; Webseite: Seite quellen; Webseite: Steckbrief Knoten |
| Spitzenstunde | 9 | 4 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml |
| HVS | 9 | 4 | Klartexte: plain_language.yaml; Regeldatei: rules.yaml; Webseite: Seite methode; Webseite: Seite quellen |
| Verbindungswert | 9 | 4 | Klartexte: plain_language.yaml; Webseite: Seite methode; Webseite: Steckbrief ETW30; Webseite: Steckbrief GOW50 |
| Score | 9 | 2 | Regeldatei: cycling_rules.yaml; Regeldatei: rules.yaml |
| Aufenthaltsstraße | 9 | 6 | Klartexte: plain_language.yaml; Regeldatei: rules.yaml; Webseite: Ebene/Legende; Webseite: Seite karte; Webseite: Seite methode; Webseite: Steckbrief ETW_ERF |
| LSA | 9 | 2 | Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml |
| Masche | 8 | 1 | Regeldatei: cycling_rules.yaml |
| WFS | 8 | 7 | Regeldatei: rules.yaml; Webseite: Seite quellen; Webseite: Steckbrief ETW30; Webseite: Steckbrief ETW_ERF; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50; Webseite: Steckbrief SW |
| ETW | 8 | 4 | Regeldatei: cycling_rules.yaml; Regeldatei: design_rules.yaml; Regeldatei: rules.yaml; Webseite: Steckbrief ETW30 |
| conn_score | 8 | 2 | Klartexte: plain_language.yaml; Regeldatei: rules.yaml |
| BVM | 8 | 5 | Klartexte: plain_language.yaml; Webseite: Ebene/Legende; Webseite: Seite quellen; Webseite: Steckbrief GOW30; Webseite: Steckbrief GOW50 |
| FGSV | 8 | 3 | Klartexte: plain_language.yaml; Regeldatei: cycling_rules.yaml; Webseite: Seite radnetz |
| Straßenzug | 7 | 3 | Klartexte: plain_language.yaml; Regeldatei: rules.yaml; Webseite: Seite methode |
<!-- /table:terms -->

<!-- table:rule_ids_on_site -->
9 verschiedene Regel-IDs (ohne die Diskrepanztypen D1–D3) erscheinen in den erfassten Webseitentexten: C-G30-02 (7), C-GOW-01 (6), C-G30-01 (6), C-ERF-01 (1), J-05 (1), N4 (1), C-ETW-01 (1), C-G50-01 (1), C-SW-01 (1).
<!-- /table:rule_ids_on_site -->

## A1.4 Sprache der Regeldateien

<!-- table:rule_language -->
| Art | verständlich: ja | teilweise | nein | gesamt |
|---|---|---|---|---|
| Kategorie | 4 | 3 | 0 | 7 |
| Regel | 23 | 104 | 69 | 196 |
| Schwelle | 0 | 56 | 2 | 58 |
| Regel – cycling_rules.yaml | 8 | 48 | 23 | 79 |
| Regel – design_rules.yaml | 9 | 23 | 20 | 52 |
| Regel – rules.yaml | 6 | 33 | 26 | 65 |
<!-- /table:rule_language -->

Kriterien (mechanisch, `analysis/redesign/rule_language.py`): Haupttext der Regel ist description, rule, check, metric
oder note. Fehlerpunkte gibt es für:

- keinen Text
- Code im Text (Variablennamen mit Unterstrich, Punkt-Schlüssel, Operatoren)
- mehr als einen Fachbegriff oder ein Kürzel
- Sätze im Mittel über 15 Wörter
- mehr als 10 % lange Substantive

„ja“ heißt kein Fehlerpunkt, „teilweise“ heißt 1–2, „nein“ heißt 3 und mehr oder kein Text. Die Bezeichnung einer Regel
ist nur ihre ID und deshalb nie selbsterklärend. Schwellen haben englische Schlüssel (`conn_gow`, `access_radius`). 56 von
58 haben eine Notiz oder Einheit, eine allgemeinverständliche Bezeichnung hat keine. Beispiele:

<!-- table:rule_language_examples -->
| Regel | Urteil | Text (Anfang) | Gründe |
|---|---|---|---|
| C-G30-01 | ja | GOW30-Auslöser a: Umfeld spricht für 30 (Schule/Kita am Abschnitt, Leben, Querbarkeit) | Bezeichnung ist nur die ID |
| C-G30-02 | ja | GOW30-Auslöser b: 50 nicht sicher gestaltbar (kein ausreichender getrennter Radweg möglich) | Bezeichnung ist nur die ID |
| S-NET-02 | ja | Abschnittsende an Knoten mit Grad 2, an denen sich die highway-Klasse ändert | Bezeichnung ist nur die ID |
| S-CONF-03 | ja | Zeitlich begrenzte Regelungen (sonderregelung) getrennt speichern, nie als Regeltempo | Bezeichnung ist nur die ID |
| C-SW-01 | teilweise | Stroomwegen nur anbaufrei; in Hamburg v. a. Autobahnen. | Bezeichnung ist nur die ID; 2 Fachbegriffe/Kürzel (Stroomwegen, anbaufrei) |
| C-GOW-01 | teilweise | Verbindungsfunktion hoch → Gebiedsontsluitingsweg | Bezeichnung ist nur die ID; 2 Fachbegriffe/Kürzel (Verbindungsfunktion, Gebiedsontsluitingsweg) |
| C-MISS-01 | teilweise | Fehlende Werte: dreiwertige Logik (Kleene). Ein Vergleich mit einem fehlenden Wert ist unbekannt; „oder“ ist wahr, sobald ein Teil wahr ist, | Bezeichnung ist nur die ID; 4 Fachbegriffe/Kürzel (confidence, dreiwertige Logik, Kleene, Regel-ID C-CONF-01) |
| S-NET-01 | teilweise | Abschnittsende an jedem Knoten mit Grad != 2 (Kreuzung, Einmündung, Sackgassenende) | Bezeichnung ist nur die ID; Code im Text (!=); 11 % lange Substantive |
| C-RUR-01 | nein | Inaktiv seit 0.17.0 (F28): Für outside_builtup_area gibt es keine Datenquelle (C-MISS-01); die Regel greift nie und senkt confidence nicht.  | Bezeichnung ist nur die ID; Code im Text (conn_score, in_hvs, outside_builtup_area); 7 Fachbegriffe/Kürzel (GOW, ETW60, HVS, confidence); Sätze im Mittel 19.0 Wörter |
| C-ERF-01 | nein |  | Bezeichnung ist nur die ID; kein Text |
| C-G50-01 | nein |  | Bezeichnung ist nur die ID; kein Text |
| C-ETW-01 | nein |  | Bezeichnung ist nur die ID; kein Text |
<!-- /table:rule_language_examples -->

Die Kategorien sind gut benannt (`label_de` und Klartext in `plain_language.yaml`), etwa „Stadtstraße 30 – verbindet
Quartiere, Tempo 30 …“. Drei Klartexte gelten als „teilweise“, weil sie Radverkehrsbegriffe ohne Erklärung nennen
(Radfahrstreifen, baulicher Radweg).

## A1.5 Regelinventar

Vollständig, eine Zeile je Regel: [`01_rules_inventory.csv`](01_rules_inventory.csv). Die Spalten sind ID, Datei,
Pfad, status, source_type, Zweck, Eingänge, Einheit, greift (Anzahl, km), entscheidet (Anzahl, km, Messweise),
Überschneidungen, goldene Fälle, Testdateien, Vorschlag und Begründung.

<!-- table:rules_summary -->
| Datei | Regeln | inaktiv | greift im Lauf nie | entscheidet etwas | ohne Test | assumption | Vorschlag |
|---|---|---|---|---|---|---|---|
| cycling_rules.yaml | 79 | 0 | 35 | 9 | 23 | 67 | keep 71, merge 4, simplify 3, remove 1 |
| design_rules.yaml | 52 | 1 | 17 | 28 | 12 | 32 | keep 46, merge 4, remove 2 |
| rules.yaml | 65 | 1 | 29 | 10 | 6 | 48 | keep 62, merge 2, remove 1 |
<!-- /table:rules_summary -->

**Wie „entscheidet“ gemessen wird** (aus den Traces des aktuellen Laufs in `data/interim`):

- **Kategorie:** letzte C-Stufe in `rule_path`, H-STR-01, wenn es im Pfad steht
- **Knoten:** `decision_rule`, JC-Regeln aus `cyclist_treatment`
- **Radanlage:** letzte Stufe, deren Ergebnis der Soll-Führungsform entspricht
- **Radnetz:** letzte Stufe, deren Ergebnis der Radnetzkategorie entspricht
- **Fahrstreifen:** letzte L-Regel mit Ergebnis
- **Rückbauschritte D1–D7:** angewendet
- **Diskrepanz:** Regel, deren Ergebnis `disc_max` ist

Merkmals-, Abgleichs-, Graph-, Nachfrage-, Prinzipien- und Validierungsregeln sind Vorverarbeitung oder Prüfung. Sie
greifen, entscheiden aber nichts allein. N1–N7 setzen nur Hinweise (N7 ist ein Vorschlag, der nur über Overrides wirkt).

**„Greift im Lauf nie“** heißt: Die Regel steht in keinem Trace. Das liegt meist am Typ der Regel, nicht an einem Fehler.
Betroffen sind Netzaufbau (S-NET), Abgleich (S-CONF), Merkmale ohne Trace-Eintrag, Validierung (V-*),
Bewertungsverfahren (C-PRI, C-GRAPH, C-DEM, C-NET-01/07/13) und reine Gestaltungsgrundsätze (PL-04 bis PL-06, PRF-01/02).

<!-- table:rules_never -->
- **C-DEM**: C-DEM-01, C-DEM-02, C-DEM-03
- **C-FAC**: C-FAC-03
- **C-GRAPH**: C-GRAPH-01, C-GRAPH-02, C-GRAPH-04, C-GRAPH-05, C-GRAPH-06
- **C-NET**: C-NET-01, C-NET-07, C-NET-13
- **C-PRI**: C-PRI-01, C-PRI-02, C-PRI-03, C-PRI-04, C-PRI-05, C-PRI-06, C-PRI-07, C-PRI-08, C-PRI-09, C-PRI-10, C-PRI-11, C-PRI-12, C-PRI-13, C-PRI-14, C-PRI-15, C-PRI-16
- **C-RUR**: C-RUR-01
- **J**: J-10, J-15, J-11
- **J-M**: J-M-01, J-M-02, J-M-03, J-M-05, J-M-07
- **L**: L-05
- **N**: N6
- **P-ATT**: P-ATT-02
- **P-COH**: P-COH-03
- **P-COM**: P-COM-03
- **P-SAF**: P-SAF-02
- **PL**: PL-02, PL-04, PL-05, PL-06
- **PRF**: PRF-01, PRF-02, PRF-04, PRF-07
- **S**: S-01, S-02, S-03
- **S-CONF**: S-CONF-02, S-CONF-03, S-CONF-04
- **S-FEAT**: S-FEAT-01, S-FEAT-04, S-FEAT-07, S-FEAT-10
- **S-NET**: S-NET-01, S-NET-02, S-NET-04
- **S-XS**: S-XS-01, S-XS-05, S-XS-06
- **V-DQ**: V-DQ-01
- **V-INV**: V-INV-01, V-INV-02, V-INV-03, V-INV-04, V-INV-05, V-INV-06, V-INV-07, V-INV-08, V-INV-09
- **V-SAMP**: V-SAMP-01
- **V-SENS**: V-SENS-01, V-SENS-02
- **V-UNC**: V-UNC-01
<!-- /table:rules_never -->

**Kandidaten** (Einzelheiten, Probeläufe und Wirkung in `06_rule_consolidation.md`):

<!-- table:rules_candidates -->
| Regel | Vorschlag | Einheit | greift | entscheidet | km entschieden | goldene Fälle | source_type | Begründung |
|---|---|---|---|---|---|---|---|---|
| N2 | merge | Abschnitte | 74 | 0 | 0,0 | 0 | assumption | Nimmt N7 auf (siehe N7). |
| N6 | remove | – | 0 | 0 | 0,0 | 0 | swov_crow | Seit Review 2026-11 F09 nur noch ein Verweis auf design_rules.junctions; greift im Lauf nie selbst. category_rank zu J-M-04 verschieben, der Berichtsteil bleibt in reports/junctions.md. |
| N7 | merge | Abschnitte | 74 | 0 | 0,0 | 0 | assumption | Markiert genau dieselben 74 Abschnitte wie N2 (Jaccard 1,00); N7 ist nur der Glättungsvorschlag zur N2-Insel. Zusammenlegen: N2 meldet die Insel samt vorgeschlagener Kategorie. |
| P-COM-03 | simplify | – | 0 | 0 | 0,0 | 0 | assumption | Ohne Datengrundlage (kein Höhenmodell, C-PRI-16 unavailable); wird nie berechnet. status inactive statt draft, auf der Webseite nicht als Prüfung zeigen. |
| P-ATT-02 | simplify | – | 0 | 0 | 0,0 | 0 | assumption | Ohne Datengrundlage (keine Lärmkarte, C-PRI-16 unavailable); wird nie berechnet. status inactive statt draft. |
| C-IMP-05 | merge | Kanten | 52 | 0 | 0,0 | 0 | assumption | Nimmt C-IMP-06 auf (siehe C-IMP-06). |
| C-IMP-06 | merge | Kanten | 259 | 0 | 0,0 | 0 | assumption | Gleicher Faktor wie C-IMP-05 (gow30_cycle_lane); die Notiz nennt C-IMP-06 selbst eine vorläufige Kopie. Eine Regel ‚Hauptstraße bis Tempo 30‘ mit und ohne Radstreifen. |
| C-NET-10 | simplify | Kanten | 20 | 10 | 1,3 | 0 | assumption | Parallelregel: entscheidet an 10 Kanten (1,3 km), feuert an 20; aufwendiger Wegsuch-Code. Vorschlag: nur noch melden (Flag), nicht mehr umlegen. |
| C-NET-11 | remove | Kanten | 5 | 5 | 0,1 | 0 | assumption | Entscheidet an 5 Kanten (0,1 km) die Radnetzkategorie; eigener Code und Test. Kontinuität (P-COH-04) wird weiter gemessen und gemeldet. |
| S-04 | merge | Abschnitte | 13539 | 0 | 0,0 | 0 | de_regelwerk | Nimmt C-FAC-03 auf (siehe C-FAC-03). |
| C-FAC-03 | merge | – | 0 | 0 | 0,0 | 0 | assumption | Beschreibt nur, wie S-04 geprüft wird (Spitzenstundenanteil); erscheint nie in rule_trace, dort steht immer S-04. Wert motor_peak_hour_share zu S-04 verschieben. |
| PRF-07 | remove | – | 0 | 0 | 0,0 | 0 | assumption | Keine Regel, sondern ein Hinweis, dass PL-02 und PL-05 nicht prüfbar sind; PL-02 ist inaktiv, das Flag pl02_unchecked tritt nie auf. Hinweis in die note von PL-05 verschieben. |
| J-01 | merge | Knoten | 830 | 220 | 0,0 | 7 | swov_crow | Nimmt J-02 auf (siehe J-02). |
| J-02 | merge | Knoten | 522 | 522 | 0,0 | 1 | swov_crow | same_as J-01 und in evaluation_order direkt nach J-01; nur das Armpaar unterscheidet sich (GOW50+GOW30). Als legs 'GOW50+GOW50|GOW30' in J-01 aufnehmen. |
| J-11 | remove | – | 0 | 0 | 0,0 | 1 | swov_crow | Hamburg hat keine Straßenbahn (GTFS ohne Straßenbahnrouten, reports/junctions.md); greift nie (0 Knoten). Ohne Straßenbahn auch kein Bedarf an der Zeile. |
| JC-02 | merge | Knoten | 840 | 840 | 0,0 | 0 | swov_crow | Nimmt JC-05 auf (siehe JC-05). |
| JC-05 | merge | Knoten | 840 | 840 | 0,0 | 0 | assumption | Gleiches applies_to wie JC-02 (signal_protected); an allen 840 Knoten gemeinsam vergeben (Jaccard 1,00). Als Baustein der geschützten Kreuzung in JC-02 aufnehmen; source_type des Bausteins bleibt assumption. |
<!-- /table:rules_candidates -->

Bewusst behalten, obwohl sie selten oder nie greifen:

- **C-RUR-01, PL-02:** außerorts, inaktiv, gewollt für GOW80/ETW60
- **J-08, J-09, J-10, J-15:** sicherheitsrelevante Sonderfälle an Knoten

## Wie gemessen

| Schritt | Skript | Ausgabe |
|---|---|---|
| Inhalte, Bildschirmfotos | `node analysis/redesign/ui/capture.mjs` | `data/scenarios/redesign/ui/content.json`, `img/c-*.jpg` |
| Aufgabentest | `node analysis/redesign/ui/tasks.mjs` | `data/scenarios/redesign/ui/tasks.json`, `img/t*.jpg` |
| Lesbarkeit | `uv run --with textstat --with pyphen python -m analysis.redesign.readability` | `readability_units.csv`, `readability_terms.csv`, `readability_summary.json` |
| Sprache der Regeldateien | `uv run --with textstat --with pyphen python -m analysis.redesign.rule_language` | `rule_language.csv` |
| Regelinventar | `uv run python -m analysis.redesign.rule_inventory` | `01_rules_inventory.csv` |
| Tabellen in diesem Dokument | `uv run --with textstat --with pyphen python -m analysis.redesign.fill_tables docs/redesign/01_inventory.md` | – |

Für die Lesbarkeit wurde `textstat` 0.7 mit `set_lang("de")` verwendet. Die Silben zählt pyphen (de_DE). Passiv und lange
Substantive werden mit Heuristiken erkannt. Eine Handprüfung von je 40 zufälligen Treffern (`--check`, Seed 24) ergab:

- **Passiv:** 38 von 40 sind Vorgangspassiv. Ein falscher Treffer: „gehört“ wurde als Partizip gelesen. Ein Treffer ist
  unklar.
- **Lange Substantive:** 39 von 40 sind Komposita. Ausnahme: „Verbesserung“.

Die Anteile sind darum leicht überschätzt. Grenzen der Messung:

- Erfasst ist nur, was ohne Klick sichtbar ist, dazu je Kategorie ein Steckbrief und ein Knoten-Steckbrief.
- Hinweistexte, die nur bei bestimmten Flags erscheinen, fehlen teilweise. Die Klartexte in `plain_language.yaml` sind
  aber vollständig bewertet.
