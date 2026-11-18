# 27 – Durchgangsverkehr in Wohnstraßen verhindern: Modalfilter und gegenläufige Einbahnstraßen

**Ziel:** Für jedes Wohnquartier (von Hauptstraßen umschlossene Fläche) automatisch prüfen, ob Wohnstraßen als Abkürzung missbraucht werden können, und Maßnahmen vorschlagen, die das verhindern – vor allem **Modalfilter** (Durchfahrt nur für Fuß, Rad, Rettung) und **gegenläufige Einbahnstraßen/Einbahnschleifen**. Die Regeln werden dafür erweitert. Ändert sich durch die Maßnahmen der Straßenquerschnitt, werden alle abhängigen Ergebnisse neu berechnet: Kategorie und Diskrepanz, Radnetz, Führungsform, Knotentyp, Bäume und Parkplätze, Webseite.
**Freigaben:** Vier Haltepunkte (unten mit STOPP markiert). Regeländerungen brauchen meine ausdrückliche Freigabe. Nichts wird ohne mein OK veröffentlicht.
**Sprache:** Webseitentexte auf Deutsch in einfacher Sprache; Code, Schlüssel und Dateinamen auf Englisch.

## Arbeitsregeln

- Zuerst Planungsmodus: Plan, Agenten-Aufteilung und Rückfragen an mich vorlegen.
- Branch `feature/quartiere-durchgangsverkehr`. Produktivstand, veröffentlichte Daten und Regeldateien bleiben bis zu meiner Freigabe unverändert; Zwischenergebnisse nach `data/scenarios/quartiere/`.
- Bestehende Struktur respektieren: getrennte `config/*.yaml` oder vereinheitlichtes `rules/`, Design-Tokens (Swiss Design), Drei-Ebenen-Muster (auf einen Blick / Erklärung / Details), `docs/source_policy.md`. Jeder neue Zahlenwert hat `source_type`, Unbekanntes ist `assumption`.
- Stabil halten: `segment_id`, `node_id`, Overrides, teilbare Links.
- Belege mit Zahlen, Karten, Beispiel-IDs. Vorschläge sind Diskussionsangebote, keine Anordnungen.

## Agenten und Modelle

Mechanische Aufgaben an Subagenten mit günstigeren Modellen; Methodik, Regelentwürfe, Bewertung und Texte in der Hauptsitzung. Agenten in `.claude/agents/` (Frontmatter `name`, `description`, `tools`, `model`) oder Modellparameter beim Start des Subagenten.

| Agent | Modell | Aufgabe |
| --- | --- | --- |
| `osm-extractor` | haiku | Ist-Einbahnstraßen (`oneway`, `oneway:bicycle`), vorhandene Sperren (`barrier=bollard|gate|…`, `motor_vehicle=no`), Abbiegeverbote (Relationen `restriction`), Feuerwachen, Wertstoffhöfe, Busrouten als Tabellen aufbereiten |
| `cell-reviewer` | haiku | je Pilotquartier Orthophoto/Straßenbilder an den vorgeschlagenen Filterstandorten sichten (Platz, Zufahrten, Bäume) und kurz bewerten; parallel je Quartier |
| `screenshot-runner` | haiku | Screenshots Desktop/Mobil, vorher/nachher |
| `a11y-perf-check` | haiku | axe-core, Konsolenfehler, Ladezeit |
| `legal-research` | sonnet | aktuelle Rechtslage zu Modalfiltern und Einbahnregelungen in Deutschland/Hamburg zusammenfassen, nur mit geöffneten Primärquellen und Datum |
| `impact-qa` | sonnet | unabhängige Prüfung der Wirkungsrechnung (Umwege, Verlagerung, Erreichbarkeit) an Stichproben |
| `review` | sonnet | unabhängige Prüfung des Gesamt-Diffs gegen diesen Prompt |

Unabhängige Aufgaben parallel starten; im Bericht nennen, welcher Agent was erledigt hat.

## Rückfragen an mich vor dem Start

1. Welche drei bis fünf **Pilotquartiere** sollen zuerst gerechnet werden? Mache einen Vorschlag mit Begründung (z. B. hoher modellierter Schleichverkehr, unterschiedliche Stadtstrukturen, eines mit Busroute, eines mit Radroute HAUPT).
2. Gibt es Quartiere, die ausgenommen werden sollen, oder bereits bekannte Planungen (z. B. Besondere Orte wie die Schanze), die als gesetzt gelten?
3. Soll ein **Kfz-Umlegungsmodell** neu gebaut werden, oder existiert bereits eines (z. B. aus Prompt 21, Variante D), auf dem aufgebaut werden kann?

## Phase 1 – Grundlagen und Regelentwurf

### 1.1 Fachliche Grundlagen (Agent `legal-research` für 1.1 c, Hauptsitzung für den Rest)

- a) **Netzprinzip:** Duurzaam Veilig und SWOV verlangen möglichst große zusammenhängende Wohnbereiche ohne Durchgangsverkehr (bestehende Regeln N3/N4). Vorbilder: Gent (Verkehrszirkulationsplan seit April 2017: sechs Sektoren, Fahrten zwischen Sektoren nur über den Ring, Fahrtrichtung in 77 Straßen geändert, Kameras an Schlüsselstellen; [EU Urban Mobility Observatory](https://urban-mobility-observatory.transport.ec.europa.eu/resources/case-studies/gents-traffic-circulation-plan-belgium_en)), Barcelona (Superilles), London (Low Traffic Neighbourhoods; Begleitforschung u. a. der LSHTM/Westminster-Gruppe), Berlin (Kiezblocks). Öffne die Primärquellen und übernimm nur belegte Aussagen mit Datum.
- b) **Wirkung:** Was sagen Evaluationen zu Verkehr im Quartier, auf den Randstraßen, zu Unfällen und zur Erreichbarkeit? Nur geöffnete Quellen, Zahlen mit Kontext, Unsicherheit benennen.
- c) **Recht (Hamburg/Deutschland):** Welche Grundlagen gibt es für Modalfilter (straßenverkehrsrechtliche Anordnung nach StVO, straßenrechtliche Teileinziehung nach HWG) und für Einbahnstraßen mit Radverkehr in Gegenrichtung? Wichtig: Das VG Berlin hat am 12.07.2024 im Eilverfahren einen Modalfilter in der Tucholskystraße beanstandet, weil keine konkrete, mit Verkehrs- und Unfalldaten belegte Gefahrenlage nachgewiesen war ([Pressemitteilung 21/2024](https://www.berlin.de/gerichte/verwaltungsgericht/presse/pressemitteilungen/2024/pressemitteilung.1467347.php)). Prüfe Folgeentscheidungen und den aktuellen Stand nach der StVG/StVO-Reform. Ergebnis: welche **Nachweise** ein Vorschlag mitbringen sollte (z. B. Anteil Durchgangsverkehr, Unfälle, Schulwege) – das Projekt kann solche Nachweise vorbereiten.

### 1.2 Maßnahmenbaukasten

| Code | Maßnahme | Wirkung | Bedingungen |
| --- | --- | --- | --- |
| F1 | Modalfilter auf der Strecke (Poller, Pflanzkübel) | trennt Durchfahrt, Rad/Fuß frei | Wendemöglichkeit, Rettungszufahrt (umlegbarer Poller), keine Buslinie |
| F2 | Diagonalsperre am Knoten | lenkt Kfz um die Ecke, keine Geradeausfahrt | Platz am Knoten, Schleppkurven Müll/Rettung |
| F3 | Busschleuse / Kamera-Filter | nur Bus, Taxi, Rettung frei | Buslinie, rechtliche Grundlage prüfen |
| E1 | Gegenläufige Einbahnstraßen | Abschnitte zeigen gegeneinander, keine durchgehende Fahrt | Radverkehr in Gegenrichtung frei, Fahrbahnbreite für Gegenrichtungsradverkehr |
| E2 | Einbahnschleife | Ein- und Ausfahrt am selben Randabschnitt | erschließt alle Adressen |
| A1 | Abbiegegebot/-verbot am Randknoten | verhindert Einfahrt in Abkürzung | Knotentyp, Ersatzroute |
| Z1 | zeitweise Sperre (Schulstraße) | Schutz zu Schulzeiten | Schule im Abschnitt |

### 1.3 Regelentwurf (noch nicht anwenden)

Schreibe einen Entwurf `docs/quartiere/regelentwurf.yaml` (später in die Regeldateien) mit `source`/`source_type`, z. B.:
- **Q-01 Quartiere bilden:** Flächen, die von GOW/SW/Bahn/Wasser umschlossen sind; Mindestgröße und Umgang mit sehr großen Zellen (Unterteilung) als `assumption`.
- **Q-02 Durchgangsverkehr erkennen:** Erweiterung von N4. Eine Wohnstraße ist gefährdet, wenn der kürzeste Kfz-Weg zwischen zwei verschiedenen Randabschnitten durch das Quartier führt und gegenüber dem Weg über die Randstraßen Zeit spart (Schwelle `assumption`). Zusätzlich modellierter Durchgangsanteil, falls ein Umlegungsmodell vorhanden ist.
- **Q-03 Ziel:** Kein Kfz-Weg von einem Randabschnitt zu einem anderen durch das Quartier; jede Adresse bleibt mit dem Kfz erreichbar.
- **Q-04 Randbedingungen:** Rettung, Müllabfuhr, Lieferverkehr, Busrouten (nur F3), Grundstückszufahrten, Wendemöglichkeiten, maximale Umweglänge für Anwohnende (`assumption`), keine neue Sackgasse ohne Wendemöglichkeit.
- **Q-05 Bevorzugung:** Erst Filter an Stellen mit Rad-/Fußnutzen (Radroute, Schulweg, Platzgewinn), dann Einbahnlösungen; möglichst wenige Maßnahmen; Filter an Quartiersgrenzen statt mitten im Quartier, wenn gleichwertig.
- **Q-06 Randstraßen:** Mehrverkehr auf GOW abschätzen und gegen Kapazität (Regel L-02) prüfen; Mehrverkehr auf anderen Wohnstraßen ist ein Fehler.
- **Q-07 Rückkopplung:** Wenn Maßnahmen den Verkehr in einer Straße senken oder Fahrtrichtungen ändern, gelten die neuen Werte für alle abhängigen Regeln (siehe Phase 3).

Ergebnis: `docs/quartiere/01_grundlagen.md` und `regelentwurf.yaml`.

**STOPP 1:** Plan, Grundlagen, Baukasten und Regelentwurf vorlegen. Warten auf meine Freigabe und meine Wahl der Pilotquartiere.

## Phase 2 – Lösungen für Pilotquartiere

### 2.1 Verfahren

1. Je Quartier einen gerichteten Kfz-Graphen mit Ist-Einbahnstraßen, Abbiegeverboten und vorhandenen Sperren aufbauen (Daten von `osm-extractor`).
2. Randzugänge (Ein- und Ausfahrten an den umgebenden Hauptstraßen) bestimmen und nach Randabschnitten gruppieren.
3. Varianten erzeugen, die Q-03 erfüllen:
   - **V1 nur Filter:** minimale gewichtete Schnittmenge, sodass zwischen verschiedenen Randabschnitten kein Weg durch das Quartier bleibt. Kosten je Standort: Buslinie (verboten außer F3), wichtige Zufahrten, Platz, Nutzen für Radroute und Schulweg.
   - **V2 nur Einbahn:** Orientierung der Wohnstraßen so wählen, dass keine gerichtete Durchfahrt bleibt und alle Adressen erreichbar sind (Optimierung, z. B. ILP mit OR-Tools oder PuLP, mit Zeitlimit; Ansatz dokumentieren).
   - **V3 Mix:** Filter und Einbahn kombiniert mit möglichst wenigen Maßnahmen.
4. Für jede Variante bewerten:
   - verhinderter Durchgangsverkehr (Wege, Modellmengen);
   - Umwege für Anwohnende (Median, Maximum);
   - Erreichbarkeit für Rettung und Müllabfuhr (Fahrzeit, Wendemöglichkeiten);
   - Mehrverkehr auf Randstraßen und Kapazität;
   - Anzahl Maßnahmen;
   - Gewinn für Rad und Fuß (z. B. Fahrradstraße wird zulässig);
   - Platzgewinn im Querschnitt;
   - Nachweise im Sinne von 1.1 c.
5. `cell-reviewer` prüft jeden vorgeschlagenen Standort im Orthophoto und in Straßenbildern auf Machbarkeit; `impact-qa` prüft die Wirkungsrechnung an Stichproben.

### 2.2 Ergebnis

`docs/quartiere/02_pilot.md` je Quartier mit:
- Karte Ist (gefährdete Abkürzungen, Ist-Einbahn, vorhandene Sperren);
- je Variante eine Karte (Filtersymbol, Einbahnpfeile, Rad frei);
- Bewertungstabelle der Varianten;
- Empfehlung mit Begründung;
- offene Punkte.

**STOPP 2:** Varianten und Empfehlungen vorlegen. Ich wähle je Pilotquartier eine Variante oder bitte um Änderungen.

## Phase 3 – Rückkopplung auf Querschnitt, Radnetz und alle abhängigen Ergebnisse

Berechne für die gewählten Varianten ein Szenario und zeige die Änderungen gegenüber heute:

1. **Verkehrsmengen:** neue DTV-Schätzung je Abschnitt nach Umlegung (oder Regelannahme, wenn kein Modell vorhanden ist; dann ausdrücklich als `assumption`).
2. **Straßenkategorie und Diskrepanz:** Wohnstraßen ohne Durchgangsfunktion bestätigen ETW30; Diskrepanz „Nutzung“ und N4-Flags neu berechnen; Randstraßen auf Kategoriewechsel prüfen.
3. **Querschnitt:** Einbahnstraßen brauchen weniger Fahrbahn (Fahrstreifenbreite plus Gegenrichtungsradverkehr nach Regelwerk). Die frei werdende Breite geht nach `fill_order` in Gehweg, Grün, Radverkehr, Laden, Parken; Abbaustufen neu bewerten (`fit_class`).
4. **Radnetz:**
   - Filter machen Routen durch Quartiere attraktiver (Widerstand sinkt); Fahrradstraßen werden zulässig, wenn die Kfz-Grenze nun eingehalten ist.
   - Die Parallelregel P-ATT-03 kann ruhigere Routen finden; Prinzipien-Scores neu berechnen.
   - Netzentwurf erneut laufen lassen und Änderungen der Radkategorien zeigen.
   - Prüfe, dass kein Filter eine Radroute blockiert und dass Gegenrichtungsradverkehr überall frei ist.
5. **Knoten:** gefilterte Knoten erhalten eigene Typen (z. B. `modal_filter_diagonal`, `modal_filter_through`), Randknoten mit Abbiegeregeln neu bewerten; Entscheidungstabelle entsprechend erweitern (Entwurf).
6. **Bäume und Parkplätze:** Statistik aus Prompt 26 für das Szenario neu berechnen, falls vorhanden.
7. **Konsistenz:** alle Ergebnisse deterministisch (zwei Läufe gleich), Tests für die neuen Regeln (goldene Quartiere: einfache Raster mit bekanntem Ergebnis), Determinismus und Laufzeit dokumentieren.

Ergebnis: `docs/quartiere/03_wirkungen.md` mit Vorher/Nachher-Tabellen und -Karten je Bereich.

**STOPP 3:** Wirkungen und den endgültigen **Regelvorschlag** (Diff gegen die Regeldateien, Versionssprung, CHANGELOG-Text) vorlegen. Regeln werden erst nach meiner ausdrücklichen Freigabe übernommen.

## Phase 4 – Übernahme, gesamtstädtischer Lauf, Webseite

1. Freigegebene Regeln übernehmen; Tests zuerst; neue Overrides-Datei `overrides/filter_overrides.csv` (Standort, Maßnahme, Begründung, Autor, Datum, Status) für fachliche Korrekturen.
2. Gesamtstadt rechnen (Quartiere parallel im Code). Quartiere, für die keine Lösung die Randbedingungen erfüllt, als „manuelle Prüfung nötig“ markieren statt zu raten.
3. Webseite (Swiss Design, einfache Sprache, drei Ebenen):
   - Neue Ansicht oder neues Thema „Ruhige Quartiere“: Quartiere mit Schleichverkehrs-Gefährdung (heute), vorgeschlagene Filter als klare Symbole, Einbahnpfeile erst ab höherem Zoom, Rad-frei-Kennzeichnung.
   - Steckbrief Straße: „Diese Straße wird heute als Abkürzung genutzt / nicht genutzt“, Maßnahme, Wirkung, Änderungen am Querschnitt und am Radnetz.
   - Steckbrief Filterstandort: Zweck, Ausnahmen (Rettung, Müll), Umweg für Anwohnende, Nachweise.
   - Quartierskarte in der Bezirksstatistik: Anzahl Quartiere, Anteil ohne Durchgangsverkehr, Maßnahmen gesamt.
   - Methodikkapitel „Ruhige Quartiere“ mit Grenzen: Modellannahmen, Rechtslage, Beteiligung vor Ort nötig.
   - Bestehende Legenden und Texte, die von den Änderungen betroffen sind, anpassen.
4. Prüfung: Screenshots, axe-core, Ladezeit, `review`-Agent gegen diesen Prompt.

**STOPP 4:** Vorschau und Bericht `docs/quartiere/bericht.md` vorlegen. Nach meinem OK: Pull Request, Merge, Deployment, kurzer Live-Check.
