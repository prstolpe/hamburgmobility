# 21 – Review: Analyse und Optionen (nichts umsetzen)

**Ziel:** Bestandsaufnahme von Klassifikation, Radnetz, Knoten, Datenpräsentation und Oberfläche; daraus ein Optionenpapier mit konkreten, bewerteten Lösungsvorschlägen, über die ich entscheide. **In diesem Prompt wird nichts am Produktivstand geändert.**
**Ergebnis:** Ordner `docs/review/2026-11/` mit Analyseberichten, Optionenpapier `optionen.md`, Entscheidungsvorlage `entscheidungen.md`, Szenarioläufen unter `data/scenarios/` und klickbaren Prototypen unter `prototypes/` (nicht veröffentlicht).
**Prüfschritt:** Ich lese `optionen.md`, sehe die Prototypen an und fülle `entscheidungen.md` aus. Erst danach folgt Prompt 22.

## Ausgangslage (von mir)

- Pipeline, Radnetz-Erweiterung (Prompts 12b–20) und Webseite https://hamburgmobility.de (GitHub Pages) laufen für ganz Hamburg.
- In `docs/open_questions.md` stehen rund 100 Fragen; einige habe ich beantwortet. Teile des Codes wurden parallelisiert.
- Mein Eindruck: Radnetz und Straßennetz geraten in Konflikt.
- Nach Ergänzung der Verkehrsdaten wurden in einer Version substanzielle Teile von GOW30 zu GOW50. Ich bin unentschieden: Als Kompromiss ist das tragfähig, aber die Verkehrsmengen ändern sich, wenn Straßen umgestaltet werden – das bleibt derzeit unberücksichtigt.
- Oberfläche und Karte sollen intuitiver werden, Daten besser präsentiert, und die Klassifikation von Straßen, Kreuzungen und Radwegen soll besser werden.
- Meine Anforderungen sind bewusst unscharf. Schärfe sie mit Belegen und lege mir Alternativen vor.

## Arbeitsregeln

- Arbeite auf einem Branch `review/2026-11`. Ändere **nicht** `config/`, `overrides/`, `pipeline/`-Logik, `web/` oder die veröffentlichten Daten. Erlaubt sind: Analyse-Skripte unter `analysis/review_2026_11/`, Szenarioläufe nach `data/scenarios/<name>/`, Prototypen unter `prototypes/`, Berichte unter `docs/review/2026-11/`.
- Kein Deployment. Prototypen nur lokal oder als Screenshots.
- Halte `docs/source_policy.md` ein. Jede vorgeschlagene Regel oder Schwelle hat `source_type`; Annahmen sind als solche benannt.
- Belege jede Aussage mit Zahlen, Karten oder Beispielen (Abschnitts-/Knoten-IDs mit Link auf die Seite und auf OSM/Orthophoto). Keine Vermutung als Befund ausgeben.
- Nutze den Planungsmodus. Zeige mir zuerst den Arbeitsplan für Phasen 1–4 mit grober Laufzeit.
- Wenn eine Phase etwas zutage fördert, das den Plan grundlegend ändert, halte an und frage.

## Phase 1 – Bestandsaufnahme (nur lesen und messen)

1. **Code und Reproduzierbarkeit nach der Parallelisierung**
   - Läuft die Pipeline deterministisch? Zwei vollständige Läufe mit gleichem Datenstand; vergleiche Ausgaben (Hashes, Anzahl, Kategorien je segment_id/node_id). Unterschiede auflisten und Ursachen benennen (Reihenfolge, Zufall ohne Seed, Race Conditions, Gleitkomma).
   - Testabdeckung je Stufe, langsame Stufen, doppelte Logik, toter Code, Inkonsistenzen zwischen `rules.yaml`, `cycling_rules.yaml`, `design_rules.yaml` und Code (Schwellen im Code, nicht genutzte Regeln, Regeln ohne Test).
2. **Offene Fragen**
   - Klassifiziere alle Einträge in `docs/open_questions.md`: beantwortet und eingearbeitet / beantwortet, aber nicht eingearbeitet / offen. Ordne jeder offenen Frage zu, welche Regel oder Ausgabe sie betrifft und wie stark (km, Knoten).
   - Liste die beantworteten, noch nicht eingearbeiteten Antworten mit dem nötigen Änderungsvorschlag.
3. **Der Wechsel GOW30 → GOW50**
   - Finde die Version bzw. den Commit, in dem er stattfand, und die Regel(n), die ihn auslösen (rule_trace auswerten). Quantifiziere: km und Abschnitte je Bezirk, typische Straßen, betroffene Radrouten und Knoten.
   - Erkläre den Mechanismus in zwei, drei Sätzen: Wird hier die Nutzung (Ist-DTV) zur Bestimmung der Funktion (Soll) verwendet?
4. **Rückmeldungen**: Werte vorhandene Rückmeldungen (GitHub-Issues o. ä.) aus und ordne sie Fehlertypen zu.

Ergebnis: `docs/review/2026-11/01_bestand.md`.

## Phase 2 – Fachliche Analyse und Verbesserungsvorschläge

Für **jeden** Vorschlag in dieser Phase dieselbe Struktur:
Problem · Beleg (Zahlen, Beispiele) · Vorschlag (konkrete Regel- oder Codeänderung als Diff-Skizze) · erwartete Wirkung aus einem **Trockenlauf** (km/Knoten, die sich ändern, nach Bezirk und Kategorie; Karte) · Risiken und Nebenwirkungen · Aufwand · `source_type` der neuen Werte.

### 2a Straßenklassifikation

- Fehleranalyse: Vergleiche mit Hauptverkehrsstraßennetz, Ist-Tempo, Rückmeldungen und Stichproben. Finde systematische Fehler (z. B. Randeffekte, Brücken, Einbahnpaare, zweibahnige Straßen, Gewerbegebiete, Außenbereiche Vier- und Marschlande, Hafen).
- **Umgang mit Verkehrsmengen** – rechne folgende Varianten als Szenarien unter `data/scenarios/` durch und stelle sie nebeneinander:
  - **A Funktion zuerst:** DTV bestimmt nicht die Kategorie, sondern nur Diskrepanz und Machbarkeit (Duurzaam-Veilig-Logik: Funktion → Gestaltung → Nutzung).
  - **B Status quo:** DTV als harte Grenze (heutige Version).
  - **C GOW30 unter Auflagen:** Kategorie bleibt GOW30, aber mit Kennzeichnung „Verkehrsreduktion nötig“ und der rechnerisch nötigen Reduktion in Kfz/Tag bis zur CROW-Profilgrenze (6.000/10.000 Kfz/Tag); Steckbrief zeigt, welche Maßnahmen dafür infrage kommen (Filter, Netzänderung).
  - **D Netzwirkung:** einfache Umlegung des Kfz-Verkehrs auf das Soll-Netz (Widerstand nach Soll-Tempo, kapazitätsabhängig, Quell-Ziel-Matrix aus heutigen Belastungen rückgeschätzt oder als Gravitationsmodell) mit einem Parameter für Verkehrsverdampfung als Spanne (z. B. 0 %, 10 %, 20 %; ausdrücklich `assumption`, Literatur wie Cairns/Atkins/Goodwin 2002 als zu prüfende Quelle nennen). Zeige, welche GOW30-Kandidaten unter welchen Annahmen tragfähig sind und wohin der Verkehr ausweicht (Mehrbelastung auf GOW50 und, wichtig, auf ETW30 als Schleichverkehr).
  - Gib eine begründete Empfehlung, aber entscheide nicht.
- Weitere Verbesserungen: z. B. Kalibrierung `conn_score`, Umgang mit fehlenden DTV, Glättung kurzer Kategoriewechsel, Außerorts-Kategorien, Sonderfälle.

### 2b Konflikte Radnetz ↔ Straßennetz

- Entwickle eine Konflikttypologie und zähle die Fälle, z. B.:
  - Radroute HAUPT/RSV an GOW50 ohne Platz für getrennte Radwege (fit_class does_not_fit);
  - Fahrradstraße auf ETW30 mit zu viel Kfz-Verkehr;
  - Radroute quert GOW50 ohne geeigneten Knotentyp;
  - Kategoriewechsel GOW30 → GOW50 auf Radrouten;
  - Parallelregel P-ATT-03 erzeugt Umwege über dem Grenzwert;
  - Abbaukaskade D5/D7 widerspricht dem Radnetzentwurf.
- Schlage einen **abgestimmten Iterationsablauf** vor (Radnetz → Querschnitt → Rückkopplung an Kategorie oder Route → erneute Prüfung, mit Abbruchkriterium), damit beide Netze konsistent werden. Zeige im Trockenlauf, wie viele Konflikte er löst und welche bewusst als Zielkonflikt bleiben und mir vorgelegt werden müssen.

### 2c Kreuzungen

- Qualitätsprüfung: Clustering komplexer Knoten (zu viele/zu wenige zusammengefasst), fehlende Arme, falsche Kategoriepaare, implausible Typen (z. B. Kreisverkehr ohne Platz, Ampel an ETW×ETW), Ist-Typ-Erkennung aus OSM.
- Vorschläge für bessere Regeln und Eingangsdaten; Stichprobe von 50 Knoten mit Bewertung richtig/falsch/unsicher.

### 2d Radanlagen

- Prüfe Führungsform, Breite und Lage: Kontinuität entlang von Routen, Seitenwechsel, Zweirichtungsradwege, Bushaltestellen, Einbahnstraßen, Brücken, Abgleich mit Ist (OSM) und amtlichem Radnetz.
- Vorschläge mit Trockenlauf wie oben.

Ergebnisse: `docs/review/2026-11/02a_strassen.md`, `02b_konflikte.md`, `02c_knoten.md`, `02d_radanlagen.md`.

## Phase 3 – Oberfläche und Datenpräsentation

1. **Bewertung des Ist-Zustands** der Webseite (Desktop und Smartphone, Screenshots per Playwright):
   - Aufgabenbasiert, mit fünf typischen Fragen von Laien und Fachleuten, z. B.:
     „Welche Kategorie hat meine Straße und warum?“ · „Was soll sich hier ändern und passt das in den Straßenraum?“ · „Wo ist in meinem Bezirk der größte Handlungsbedarf?“ · „Wie sieht das Radnetz aus und wo sind Lücken?“ · „Was wird aus dieser Kreuzung?“
     Für jede Aufgabe: Klickpfad, Stolpersteine, Zeitbedarf geschätzt.
   - Heuristiken: Verständlichkeit der Begriffe (GOW/ETW-Kürzel vs. Klartext), Zahl und Logik der Ebenen, Legenden, Farben (Farbsehschwäche, Kontrast, Bedeutungskonsistenz zwischen Ebenen), Zoomverhalten, Steckbrief-Aufbau, Ladezeit und Dateigrößen, Barrierefreiheit (axe-core), Kennzeichnung als Entwurf.
2. **Zwei bis drei alternative Konzepte**, deutlich unterschiedlich, zum Beispiel:
   - **Themen statt Ebenen:** wenige Einstiege („Straßenfunktion“, „Radnetz“, „Handlungsbedarf“, „Kreuzungen“, „Datenqualität“) mit vorkonfigurierten Ebenen und erklärender Kurztext;
   - **Ist/Soll-Vergleich:** Schieberegler oder geteilte Karte, Querschnitt vorher/nachher im Steckbrief;
   - **Geführter Einstieg:** kurze Einführung in drei Schritten, Bezirksübersicht mit Kennzahlen, dann Karte.
   Für jedes Konzept: klickbarer Prototyp unter `prototypes/<konzept>/` auf echten Daten eines Bezirks, Screenshots Desktop/Mobil, Vor- und Nachteile, Aufwand.
3. **Datenpräsentation:** Vorschläge für Steckbrief (Kurzantwort zuerst, dann Begründung, dann Details und Quellen), Klartext statt Regel-IDs, Darstellung von Unsicherheit und Annahmen, Bezirkskennzahlen, Downloads und Datenbeschreibung, Darstellung der Szenarien aus 2a.

Ergebnis: `docs/review/2026-11/03_oberflaeche.md` mit eingebetteten Screenshots.

## Phase 4 – Optionenpapier und Entscheidungsvorlage, dann STOPP

1. `docs/review/2026-11/optionen.md`: eine Seite Zusammenfassung, dann höchstens 15 Entscheidungen, priorisiert nach Nutzen/Aufwand. Je Entscheidung: Frage, Optionen (inkl. „nichts tun“), Wirkung in Zahlen, Empfehlung mit Begründung, Abhängigkeiten zu anderen Entscheidungen und zu offenen Fragen.
2. `docs/review/2026-11/entscheidungen.md`: Vorlage zum Ausfüllen mit einer Zeile je Entscheidung (ID, gewählte Option, Anmerkung) und vorgeschlagener Umsetzungsreihenfolge in Paketen.
3. Liste der offenen Fragen, die **vor** einer Entscheidung beantwortet sein müssen (maximal 15, mit Begründung).
4. Committe alles auf `review/2026-11`, fasse mir im Chat in zehn Zeilen zusammen, was ich lesen und entscheiden muss, und **halte an**. Setze nichts davon im Produktivstand um.
