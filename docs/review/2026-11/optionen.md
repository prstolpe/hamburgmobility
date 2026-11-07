# Review 2026-11 · Optionenpapier

Entwurf, nicht amtlich. Grundlage: `01_bestand.md`, `02a_strassen.md`, `02b_konflikte.md`, `02c_knoten.md`,
`02d_radanlagen.md`, `03_oberflaeche.md`. Nichts davon ist im Produktivstand umgesetzt. Entscheidungen bitte in
`entscheidungen.md` eintragen.

## Zusammenfassung (eine Seite)

**Was gut ist.**
- Die Pipeline ist deterministisch: zwei vollständige Läufe sind byte-gleich.
- Die Rechenkerne sind zu 91–100 % getestet (1 280 Tests grün).
- Es gibt keine fachlichen Schwellen im Code; jede Regel hat source_type und status.
- Die Rechenzeit für eine Regeländerung liegt bei rund 18 min.

**Was fehlt.**
- **Prüfung gegen die Wirklichkeit:** Alle 176 Regeln sind `draft`, alle Prüflisten leer (0 von 520 Zeilen), es gibt
  keine Rückmeldungen. Jede weitere Regelverfeinerung ohne Stichprobe bleibt ungeprüft (Entscheidung E1).
- **Nebenbefund:** Die veröffentlichten Kacheln enthalten den lokalen Pfad mit Benutzernamen (E14).

**Der Kern der fachlichen Fragen ist ein Bündel von rund 300–400 km Straßen**, an dem Straßen- und Radnetz kollidieren:
- **Hauptverkehrsstraßen mit Umfeld für Tempo 30, aber 11 000–110 000 Kfz/Tag:** Die Frage GOW30 oder GOW50 betrifft
  358 km. Heute GOW30 (A), mit der Obergrenze aus 0.14.0 GOW50 (B).
  - Von den 401 km GOW30 über 10 000 Kfz/Tag haben 296 km schon einen baulichen Radweg. Echte Reduktion nötig ist auf
    106 km.
  - Die einfache Umlegung (D) zeigt: Tempo 30 allein bringt nur ein Viertel davon unter die CROW-Grenze und drückt ohne
    Schutz der Wohngebiete Verkehr in Quartiersstraßen (178 km mit +2 500 Kfz/Tag).
  - B dagegen vervierfacht die ungeschützten Radquerungen an GOW50 (55 → 219) und verdoppelt die Radrouten an GOW50 ohne
    Platz.
- **Sammelstraßen mit Linienbus, die als Quartiersstraße (ETW30) gelten:** 310 km. Auf 304 km wird daraus eine
  Soll-Fahrradstraße mit Busverkehr. Drei unabhängige Stellschrauben treffen denselben Kern; die einfachste und
  begründbarste ist eine Busregel (330 km werden GOW).

**Empfehlung in einem Satz:** erst Stichproben organisieren (E1), dann Funktion zuerst mit Kennzeichnung „weniger
Verkehr nötig“ (E2 = C), Busregel (E3) und Rückkopplung Querschnitt → Kategorie (E4); dazu ein neuer Steckbrief mit
Kurzantwort zuerst (E13).

## Entscheidungen

Priorisiert nach Nutzen/Aufwand. „Wirkung“ aus Trockenläufen bzw. Szenarioläufen; Abhängigkeiten in Klammern.

| ID | Frage | Nutzen | Aufwand | Empfehlung |
|---|---|---|---|---|
| E1 | Wie wird der Entwurf gegen die Wirklichkeit geprüft? | sehr hoch | mittel (Arbeitszeit) | Stichproben mit Ortskundigen, 2 h je Bezirk |
| E2 | Umgang mit Verkehrsmengen | sehr hoch | klein | C (Funktion zuerst + Kennzeichnung), D als Prüfwerkzeug |
| E3 | Sammelstraßen mit Bus | hoch | klein | Busregel 100 Fahrten/Werktag |
| E4 | Rückkopplung Querschnitt → Kategorie | hoch | mittel | D5 als Regel übernehmen, D7 als Zielkonfliktliste |
| E5 | Knotenzeile „Radroute quert GOW50“ | hoch | mittel | ja (J-14) |
| E6 | Ist-Knotentyp verbessern | mittel | klein | Ampel nur am eigenen Arm, Minikreisel lesen |
| E7 | Richtungsfahrbahnen und kurze Inseln | mittel | klein | gemeinsam einstufen, Inseln glätten |
| E8 | Randbereich außerhalb Hamburgs | mittel | klein | nicht mehr einstufen |
| E9 | Zweirichtungsradwege und Lage | mittel | mittel | S-3 umsetzen, Lage je Seite |
| E10 | Amtliches Radnetz | mittel | klein | als Mindestnetz BASIS |
| E11 | Haltestellen und Einbahnstraßen im Profil | mittel | mittel | prüfbar machen (Flags) |
| E12 | Umwegprüfung auf Maschenrouten | klein | klein | über OD-Paare messen |
| E13 | Oberflächenkonzept | hoch | groß | neuer Steckbrief sofort, dann Themen-Gerüst (A) |
| E14 | Export, Formalia, Bedienfehler der Seite | mittel | klein | sofort |
| E15 | Varianten auf der Seite zeigen | mittel | mittel | B als zweite Ansicht, nach E2 |

---

### E1 Prüfung gegen die Wirklichkeit

**Frage:** Wie kommt der Entwurf von „draft“ zu einer belegten Trefferquote?

| Option | Wirkung | Aufwand |
|---|---|---|
| a) nichts tun | Regeln bleiben ungeprüft; jede weitere Verfeinerung ist Kalibrierung ohne Ziel | 0 |
| b) vorhandene Prüflisten ausfüllen (520 Zeilen, Luftbild am Schreibtisch) | Trefferquote je Kategorie und Knotentyp | rund 10 h (1 min/Zeile, Annahme) |
| c) b + Ortsbegehung mit Ortskundigen in 2 Bezirken (30 Abschnitte je Kategorie, guide.md Teil 7) | Fehlerrate mit Ortswissen; Grundlage für Freigabe von Annahmen | rund 2 Tage |
| d) externe Fachprüfung (Hochschule/Büro) | Freigabe der Regeln (status reviewed) | Organisation, extern |

**Empfehlung: b sofort, c vor der nächsten Regelrunde.** Begründung: Alle offenen Kalibrierungsfragen (conn_gow,
Busschwelle, Knoten) sind ohne Stichprobe nicht entscheidbar. Die 50-Knoten-Stichprobe aus 2c konnte auf Daten keinen
einzigen Knoten als richtig bestätigen.

**Abhängigkeiten:** Voraussetzung für die Freigabe von E3, E6, E7 (Schwellen); offene Fragen Zeilen 73, 130, 183, 216, 220.

### E2 Umgang mit Verkehrsmengen

**Frage:** Darf die heutige Verkehrsmenge die Kategorie bestimmen?

| Option | GOW30 / GOW50 | HVS als GOW30 | Radroute an GOW50 ohne Platz (K1) | ungeschützte GOW50-Querungen (K3) | Bemerkung |
|---|---:|---:|---:|---:|---|
| A Funktion zuerst (heute) | 528 / 223 km | 467 km | 9,6 km | 55 | DTV nur als Flag |
| B Status quo 0.14.0 | 144 / 607 km | 87 km | 22,8 km | 219 | Nutzung bestimmt Funktion |
| C A + Kennzeichnung „Verkehrsreduktion nötig“ mit Zahl | wie A | 467 km | 9,6 km | 55 | 106 km mit nötiger Reduktion (Median −10 000 Kfz/Tag) |
| D A/C + Umlegung als Prüfung | wie A | 467 km | — | — | tragfähig 15–41 von 106 km; ohne ETW-Schutz +178 km Schleichverkehr |
| nichts tun | wie A | | | | |

**Empfehlung: C, mit D als Prüfwerkzeug.**
- C ist DV-konform und kennzeichnet ehrlich, wo Tempo 30 nur mit weniger Verkehr funktioniert.
- D gehört nicht in die Kategorie-Regel (Modellgüte Spearman 0,53), aber als Hinweis in den Steckbrief und als Größe der
  Aufgabe in Prompt 22.
- B bleibt als gespeicherte Ansicht (E15).

**Vor der Entscheidung klären:** Gilt das CROW-GOW30-Profil mit baulichem Radweg tatsächlich ohne DTV-Grenze? Davon
hängen 296 km ab.

**Abhängigkeiten:** Prompt 22 (Zielszenario) baut darauf auf; E4, E15; offene Fragen Zeilen 70, 201.

### E3 Sammelstraßen mit Linienbus

**Frage:** Sollen Straßen mit regelmäßigem Linienbus Verbindungsfunktion (GOW) haben?

| Option | Wirkung (Trockenlauf) | Risiko |
|---|---|---|
| a) nichts tun | 610 km ETW30 mit Bus; 304 km Soll-Fahrradstraße mit Bus | Fahrradstraße mit Linienbus |
| b) Busregel ≥ 100 Fahrten/Werktag | +330 km GOW (225 GOW30, 105 GOW50) | Linienführung bestimmt Funktion |
| c) Busregel ≥ 200 | +186 km GOW | weniger Konflikte gelöst |
| d) `conn_gow` 0,6 → 0,5 | +266 km GOW, 190 km gemeinsam mit b | wirkt auch ohne Bus |
| e) `in_hvs` aus dem Score | +430 km GOW | größter Eingriff |

**Empfehlung: b.** Die Regel benennt den Mechanismus und trifft den gemeinsamen Kern von d und e. Die Schwelle ist eine
Annahme (Quelle CROW „ÖV auf GOW“ prüfen).

**Abhängigkeiten:** löst K2 überwiegend (Trockenlauf 2b); E1 für die Schwelle; offene Fragen Zeilen 123, 124.

### E4 Rückkopplung Querschnitt → Kategorie

**Frage:** Sollen Vorschläge aus dem Soll-Querschnitt die Kategorie ändern?

| Option | Wirkung |
|---|---|
| a) nichts tun | D5/D7 bleiben Flags (137 bzw. 534 Abschnitte) |
| b) D5 als Regel (GOW50 passt nicht → GOW30), D7 als Liste | Trockenlauf mit E3: K1 16,1 → 0 km, K3 56 → 44 Knoten; 282 Abschnitte (48 km) GOW50 → GOW30; konvergiert nach 2 Runden; bleibt: 91 km D7 auf RSV/HAUPT (z. B. Elbchaussee) als Zielkonflikt |
| c) b + D7 automatisch (Route verlegen) | nicht empfohlen: Verlegung ist Entwurfsarbeit |

**Empfehlung: b**, mit Abbruchkriterium (keine neuen Vorschläge oder 3 Runden) und nur Richtung GOW50 → GOW30.

**Abhängigkeiten:** E2; E3 (in der Iteration zuerst angewendet).

### E5 Knotenzeile „Radroute quert GOW50“

**Optionen:** a) nichts tun (55 Querungen mit Gehwegüberfahrt); b) neue Zeile J-14 (LSA-Furt bzw. Mittelinsel).

**Empfehlung: b.** Die Schwelle für die Mittelinsel fehlt (TODO, offene Frage).

**Abhängigkeiten:** E2 (mit B wären es 219).

### E6 Ist-Knotentyp

**Optionen:** a) nichts tun (432 Ist-Ampeln an ETW×ETW, 83 Kreisverkehre); b) Ampel nur am eigenen Arm (K-1) und
Minikreisel/`junction=circular` lesen (K-2); c) b + amtliche LSA-Daten beschaffen.

**Empfehlung: b, c anfragen.** Bis zu 432 falsche Ist-Ampeln entfallen.

**Abhängigkeiten:** offene Fragen Zeilen 85, 214.

### E7 Richtungsfahrbahnen und kurze Inseln

**Optionen:** a) nichts tun (206 Paare mit verschiedener Kategorie, 345 Inseln, 21 km); b) gemeinsame Einstufung (höhere
Kategorie, H-STR-02) und Glättung aller Kategorien außer amtlichem ETW_ERF.

**Empfehlung: b.**

### E8 Randbereich außerhalb Hamburgs

**Optionen:** a) nichts tun (180 km eingestuft, Randeffekt im `conn_score`); b) nur innerhalb der Bezirke einstufen.

**Empfehlung: b.**

### E9 Zweirichtungsradwege und Lage

**Optionen:** a) nichts tun (242 km Ist-Zweirichtung immer „teilweise“, keine Seitenprüfung); b) S-3 umsetzen und Lage je
Seite führen; c) nur Lage je Seite.

**Empfehlung: b.** Die Schwelle für die Knotendichte fehlt (TODO).

**Abhängigkeiten:** E11.

### E10 Amtliches Radnetz

**Optionen:** a) nichts tun (454 km amtlich → Soll Erschließung); b) amtliches Netz mindestens BASIS; c) nur Bestand,
nicht Planung.

**Empfehlung: b** (source_type hamburg). Der Netzumfang wächst, aber der Entwurf widerspricht nicht dem Beschluss der
Stadt.

### E11 Haltestellen und Einbahnstraßen

**Optionen:** a) nichts tun; b) Haltestellen (1 028 Punkte an Soll-Radwegen) und Gegenrichtung (204 km Einbahn-ETW30 im
Netz) als prüfbare Flags.

**Empfehlung: b.**

### E12 Umwegprüfung

**Optionen:** a) nichts tun (1 468 Überschreitungen, davon 1 446 Messfehler); b) Maschenrouten über OD-Paare.

**Empfehlung: b.**

### E13 Oberflächenkonzept

**Frage:** Wie soll die Seite aufgebaut sein, damit Laien und Fachleute ihre Fragen beantworten?

Befund aus Phase 3:
- **Steckbrief zu lang:** Median 538 Wörter; „Was soll sich ändern?“ erst nach rund 1 490 px.
- **Unübersichtliches Bedienfeld:** 13 Ebenen, 4 Overlays und 11 Filter in einem Panel; Rot hat 10 Bedeutungen.
- **Steckbrief widerspricht sich:** 188 km mit „passt“ (Straßenprofil) gegenüber „passt nicht“ (Radprofil), 129 km
  „keine Radanlage“ gegenüber vorhandener Radanlage.
- **Technisch solide:** axe-core 0 Verstöße.

Drei klickbare Prototypen auf Eimsbüttel-Daten (`prototypes/`).

| Option | Wirkung | Aufwand |
|---|---|---|
| a) nichts tun (nur Fehlerkorrekturen aus E14) | Aufgaben bleiben langsam (z. B. T2 rund 83 s, 4–5 Scrolls) | 0 |
| b) neuer Steckbrief „Kurzantwort zuerst“ (134–196 Wörter), Widersprüche auflösen, Farbpalette bereinigen | T2 ohne Scrollen; ein Profil, eine Machbarkeit | 3–4 Personentage + Datenentscheidung |
| c) b + Konzept A „Themen statt Ebenen“ als Gerüst (Straßenfunktion, Radnetz, Handlungsbedarf, Kreuzungen, Datenqualität; Netzlücken und Ranglisten) | T3–T5 mit 1 Klick | groß |
| d) c + Konzept B als Vergleichsmodus (Szenarien, E15) + Konzept C als Startseite mit Bezirkskennzahlen | vollständig | sehr groß, gestaffelt |

**Empfehlung: b sofort, c als nächstes Paket, d gestaffelt.**
- Der Steckbrief ist der größte Hebel und unabhängig vom Gerüst.
- **Vorher zu entscheiden:** welche Machbarkeit gilt, das Radprofil (c06) oder das Straßenprofil (s07). Vorschlag: c06
  ersetzt s07 im Steckbrief, weil es Radnetz und Fahrstreifen kennt. Außerdem die Quelle für das Ist der Radanlage:
  c05 (OSM inkl. begleitender Wege) statt s04.
- Rot nur für „passt nicht/fehlt“ verwenden, nicht für GOW50 und das Hauptradnetz; `#B35900` ersetzen
  (Deuteranopie, ΔE 0,3).

**Abhängigkeiten:** E2 (Kennzeichnung „Reduktion nötig“ im Steckbrief), E15 (Szenarien = Konzept B), E9 (Lage im Profil).

Hinweis zu Zahlen: `03_oberflaeche.md` nennt für den Wechsel 0.14.0 → heute 367 km. Darin sind 44 km aus Stapel 5
enthalten; der Wechsel selbst umfasst 358 km über C-G50-02, davon 324 km in beiden Ständen getrennt einer Kategorie
zugeordnet (`01_bestand.md`, Abschnitt 3).

### E14 Export und Formalia

- **Kachel-Metadaten:** tippecanoe mit `--name`/`--description` und relativen Pfaden aufrufen; Kacheln neu veröffentlichen.
  Die heutigen Kacheln zeigen `/Users/raphael/...`.
- **Formalia:** Gruppe B der offenen Fragen (5 Punkte: Einheiten, status-Freitext, Feldnamen in guide.md) freigeben.
- **`docs/source_policy.md`:** fehlt; anlegen oder den Verweis im Prompt streichen.
- **Bedienfehler der Seite** (Phase 3, je unter 1 Stunde):
  - `.table-wrap { position: relative; }`: Der Steckbrief aus der Tabelle ist auf dem Smartphone heute nicht schließbar.
  - Die Suche öffnet den Steckbrief, und das Bedienfeld klappt auf dem Smartphone danach zu.
  - `search.json` (586 KB, 41 % der Startdaten mobil) erst bei Bedarf laden.

**Empfehlung:** sofort, kein fachlicher Wert ändert sich.

### E15 Varianten auf der Seite

**Optionen:** a) nichts tun; b) B als zweite Ansicht („Kompromiss Hamburg“) mit Umschalter; c) zusätzlich D-Varianten.

**Empfehlung: b nach E2, c erst nach Prompt 22.**

**Abhängigkeiten:** E2, E13; offene Frage Zeile 71.

## Offene Fragen, die vor einer Entscheidung beantwortet sein müssen

| # | Frage | für | warum vorher |
|---:|---|---|---|
| 1 | Gilt das CROW-GOW30-Profil mit baulichem Radweg ohne DTV-Grenze? (Original CROW 2023) | E2 | 296 km hängen daran |
| 2 | Quelle für „Linienbus auf GOW“ und eine begründete Schwelle | E3 | sonst reine Annahme |
| 3 | Wer prüft die Stichproben (Personen, Termine)? | E1 | ohne Prüfer keine Trefferquote |
| 4 | Sollen Kategorie-Änderungen aus dem Querschnitt als Regel oder als Overrides geführt werden? | E4 | Nachvollziehbarkeit |
| 5 | Schwelle für die Mittelinsel bzw. LSA-Furt an GOW50-Querungen | E5 | Wert fehlt (TODO) |
| 6 | Gibt es amtliche Daten zu Lichtsignalanlagen (BVM/LSBG)? | E6 | ersetzt OSM-Schätzung |
| 7 | Knotendichte-Schwelle für Zweirichtungsradwege (CROW) | E9 | Wert fehlt (TODO) |
| 8 | Amtliches Radnetz: Bestand und Planung oder nur Bestand? | E10 | Umfang |
| 9 | Ortsgrenze/Ortsdurchfahrten (Quelle) | E2, E8 | Außerorts-Kategorien |
| 10 | Kfz-Zählungen auf Bezirksstraßen (Transparenzanfrage) | E2, E3, K2 | Fahrradstraßen-Prüfung ohne DTV |
| 11 | Einbahn-/Abbiegeinformation für einen gerichteten Graphen | E2 (D), Prompt 22 | Modellgüte |
| 12 | Wie stark darf der Radnetzumfang wachsen (heute rund 1 940 km RSV/HAUPT)? | E10 | Abwägung |
| 13 | Soll die Seite Modellwerte (Szenario D) zeigen dürfen? | E15 | Kalibrierung mäßig |
| 14 | Welche Machbarkeit gilt im Steckbrief: Radprofil (c06) oder Straßenprofil (s07)? Welche Quelle für das Ist der Radanlage? | E13 | 188 km bzw. 129 km widersprüchliche Aussagen |
