# Ruhige Quartiere – Grundlagen (Prompt 27, Phase 1)

Stand: 18.11.2026. Entwurf, nicht amtlich. Die Vorschläge sind Diskussionsangebote und keine Anordnungen. Alle Quellen wurden am 18.11.2026 abgerufen, soweit nichts anderes steht.

## 1. Das Wichtigste

- **Die Wirkung ist gut belegt, aber nicht überall gleich.** In London gingen die Verletzten in verkehrsberuhigten Quartieren um 35 % zurück, auf den Randstraßen änderte sich ihre Zahl nicht erkennbar. In Gent nahm der Verkehr auf dem Ring dagegen deutlich zu (+14 % in den Spitzenstunden).
- **Verlagerung muss je Quartier geprüft werden.** Gent und Berlin zeigen, dass sich Verkehr auf einzelnen Achsen sammeln kann. Regel Q-06 prüft das deshalb ausdrücklich.
- **Der Tucholskystraßen-Beschluss gilt nicht mehr.** Das OVG Berlin-Brandenburg hat ihn am 30.09.2024 abgeändert, das VG Berlin hat die Klage am 05.05.2025 abgewiesen. Die Nachweispflicht bleibt trotzdem wichtig.
- **Die Rechtslage ist seit Oktober 2024 günstiger, aber nicht eindeutig.** Ob ein Modalfilter ohne Fahrradstraße unter die neuen Anordnungsgründe fällt, ist nicht geklärt.
- **Acht Schwellenwerte fehlen noch.** Sie sind im Regelentwurf offen gelassen und werden bei STOPP 1 entschieden (Abschnitt 6).

## 2. Netzprinzip

Das Projekt setzt die Netzanforderungen von SWOV bereits um: große zusammenhängende Wohngebiete, wenig Fahrleistung auf unsichereren Straßen, kurze Wege, und der kürzeste Weg ist auch der sicherste (`docs/guide.md`, Regeln N3 und N4). Die SWOV-Seiten ließen sich bei dieser Recherche nicht neu öffnen, weil eine Bot-Sperre den Abruf verhindert. Die Aussage stützt sich daher auf den bestehenden Eintrag im Regelwerk (`SWOV_FS_2023`).

N4 erkennt Abkürzungen heute ohne Fahrtrichtungen. Regel Q-02 erweitert das um Einbahnstraßen, Abbiegeverbote und Sperren.

## 3. Vorbilder und gemessene Wirkung

| Ort | Maßnahme | Ergebnis im Quartier | Ergebnis am Rand | Einordnung |
|---|---|---|---|---|
| **Gent**, seit 03.04.2017 | Sektoren; Fahrten zwischen Sektoren über den Ring R40 | 17 % weniger Kfz in die Innenstadt und hinaus (Spitzenstunden), 36 % weniger zum Zentrum hin; Unfälle −25 %, Verunglückte −33 % (2018 gegen das Jahr vor dem Plan) | R40 +14 % in den Spitzenstunden, Achse N430 +40 % | Vorher-Nachher-Werte der städtischen Evaluation; andere Einflüsse sind nicht herausgerechnet [1] |
| **London**, 113 Quartiere, 2015–2024 | Low Traffic Neighbourhoods | Verletzte −35 % (95 %-KI 29–40 %), schwer oder tödlich Verletzte −37 % (KI 24–48 %) | Verletzte −2 % (KI −5 bis +2 %), schwer oder tödlich Verletzte 0 % (KI −7 bis +8 %) | Kontrollierte Vorher-Nachher-Studie; gelesen wurde nur die Zusammenfassung [2] |
| **London**, 72 Quartiere, 2020 | Low Traffic Neighbourhoods | Verletzte etwa halbiert gegenüber dem übrigen London (Verhältnis 0,51) | Keine signifikante Änderung (Verhältnis 1,05; p = 0,35) | Nur drei Monate Nachlauf, Pandemiezeit, kleine Fallzahlen [3] |
| **Barcelona**, Sant Antoni | Superilla | NO₂ −25 % (−14,6 µg/m³), PM10 −17 % (−4,1 µg/m³) an einer Messstelle | Nicht gemessen | Kurze Messzeiträume 2017 und 2018 [4] |
| **Barcelona**, Horta | Superilla | Mobile Messung ohne signifikante Änderung; Passivsammler −17 % und −27 % an zwei Punkten eines Teilgebiets | Anstieg an einigen Kontrollpunkten | Vorher und nachher nicht exakt am selben Punkt gemessen [4] |
| **Berlin**, Bellermannkiez, 2022–2024 | Kiezblock mit Modalfiltern | Kfz-Verkehr im Kiez −23 %, an den Zählknoten −37 % | Spanheimstraße: ein Drittel mehr Durchgangsverkehr als erwartet | Je eine Spitzenstunde gezählt; ein Filter wurde illegal befahren [5] |

Für Gent nennt der Bericht außerdem rund 10 % längere Autowege bei manchen Fahrten [1]. Verkehrsmengen aus Barcelona liegen in den geöffneten Quellen nicht vor.

**Was daraus für das Projekt folgt**

1. Die Wirkung am Rand hängt vom Netz ab. Sie wird je Quartier gerechnet und nicht pauschal angenommen.
2. Filter brauchen dauerhafte Bauweise. Im Bellermannkiez wurden provisorische Poller umfahren oder entfernt [5].
3. Verkehr kann sich auf die letzte offene Route verlagern. Jede Variante muss deshalb alle Durchfahrten schließen oder die verbleibende Route ausweisen.

## 4. Rechtslage in Kürze

Die ausführliche Fassung mit allen Fundstellen steht in [`01c_recht.md`](01c_recht.md). Sie ist keine Rechtsberatung.

- **Anordnung nach StVO:** Seit dem 11.10.2024 sind Umwelt, Klima, Gesundheit und städtebauliche Entwicklung eigene Anordnungsgründe (§ 45 Abs. 1 Satz 2 Nr. 7), aber nur für Busspuren und für Flächen für Rad- und Fußverkehr. Dafür ist keine qualifizierte Gefahrenlage nötig (§ 45 Abs. 10 Nr. 2).
- **Fahrradstraßen:** Auch für sie entfällt die qualifizierte Gefahrenlage (§ 45 Abs. 9 Satz 4 Nr. 2). Ein Filter als flankierende Maßnahme braucht nach dem VG Berlin nur eine einfache Gefahrenlage.
- **Teileinziehung:** Sollen Verkehrsarten dauerhaft weitgehend ausgeschlossen werden, ist sie im Regelfall nötig (VwV-StVO Rn. 45a). Das Hamburgische Wegegesetz konnte im Wortlaut nicht geöffnet werden.
- **Radverkehr gegen die Einbahnstraße:** Bei höchstens Tempo 30 soll er zugelassen werden, wenn die Begegnungsbreite reicht. Bei Linienbus oder stärkerem Lkw-Verkehr sind mindestens 3,5 m nötig (VwV-StVO zu Zeichen 220).
- **Tucholskystraße:** Das VG Berlin beanstandete den Filter am 12.07.2024 im Eilverfahren (VG 11 L 495/24). Das OVG änderte das am 30.09.2024 ab (OVG 1 S 54/24, unanfechtbar). Im Hauptverfahren wies das VG die Klage am 05.05.2025 ab (VG 11 K 799/24).

**Nachweise für jeden Vorschlag:** Anteil Durchgangsverkehr, Verkehrsmenge, Radverkehr und Netzbedeutung, Unfälle, Schulwege, Umleitung und Erreichbarkeit, Rettung und Müllabfuhr, Busverkehr, Breiten, Datenstand. Das Projekt kann viele davon vorbereiten, ersetzt aber keine Zählung vor Ort (Tabelle in `01c_recht.md`, Abschnitt 6).

## 5. Maßnahmenbaukasten

| Code | Maßnahme | Wirkung | Bedingungen | Rechtlicher Hinweis |
|---|---|---|---|---|
| F1 | Modalfilter auf der Strecke | Trennt die Durchfahrt, Rad und Fuß frei | Wendemöglichkeit, Rettungszufahrt, keine Buslinie | § 45 StVO; Teileinziehung prüfen |
| F2 | Diagonalsperre am Knoten | Lenkt Kfz um die Ecke | Platz am Knoten, Schleppkurven für Müll und Rettung | Wie F1 |
| F3 | Busschleuse oder Kamera-Filter | Nur Bus, Taxi und Rettung frei | Buslinie, Rechtsgrundlage klären | **Keine Rechtsgrundlage belegt** |
| E1 | Gegenläufige Einbahnstraßen | Keine durchgehende Fahrt | Radverkehr in Gegenrichtung, ausreichende Breite | VwV-StVO zu Zeichen 220 |
| E2 | Einbahnschleife | Ein- und Ausfahrt am selben Randabschnitt | Alle Adressen erreichbar | Wie E1 |
| A1 | Abbiegegebot oder -verbot am Rand | Verhindert die Einfahrt in die Abkürzung | Knotentyp, Ersatzroute | § 45 StVO |
| Z1 | Zeitweise Sperre (Schulstraße) | Schutz zu Schulzeiten | Schule im Abschnitt | Hamburg erprobt das an fünf Standorten; **keine Norm genannt** |

## 6. Regelentwurf und offene Entscheidungen

Der Entwurf steht in [`regelentwurf.yaml`](regelentwurf.yaml). Er enthält Q-01 bis Q-07 und wird von keiner Pipeline-Stufe gelesen.

| Regel | Schwelle | Stand |
|---|---|---|
| Q-01 | Kleinste Quartiersfläche (ha) | **offen** |
| Q-01 | Fläche, ab der unterteilt wird (ha) | **offen** |
| Q-02 | Kleinster Zeitgewinn einer Abkürzung (s) | **offen** |
| Q-02 | Kürzeste Strecke durch Wohnstraßen: 300 m | aus N4 übernommen |
| Q-04 | Größter Umweg als Faktor | **offen** |
| Q-04 | Größter Umweg in Metern | **offen** |
| Q-04 | Zusätzliche Fahrzeit für die Rettung (s) | **offen** |
| Q-04 | Kleinster Wendekreis (m) | **offen**, RASt 06 liegt nicht offen vor |
| Q-04 | Mindestbreite für Gegenrichtungsradverkehr bei Linienbus oder stärkerem Lkw-Verkehr: 3,5 m | VwV-StVO zu Zeichen 220 |
| Q-06 | Kapazität 900 Kfz/h, Auslastung 0,85 | aus L-02 übernommen |
| Q-06 | Toleranz für Mehrverkehr auf Wohnstraßen | **offen**, erst nach der Modellkalibrierung |

Q-05 ist als Rangfolge formuliert, damit keine Gewichte erfunden werden müssen.

## 7. Datenlage für Phase 2

Alle Tabellen stammen aus dem OSM-Abzug vom 28.10.2026 und liegen unter `data/scenarios/quartiere/osm/` (nicht in Git).

| Tabelle | Gesamt | Im Arbeitsgebiet | Hinweis |
|---|---:|---:|---|
| Befahrbare Wege | 102.884 | 99.363 | Bei 79.758 Wegen fehlt `oneway`; das heißt unbekannt |
| Barrieren | 44.850 | 43.920 | Darunter 4.703 Poller und 9.805 Tore |
| Knoten mit Zufahrtsregeln | 9.859 | 9.742 | |
| Abbiegeverbote | 4.544 | 4.484 | 37 unvollständig, davon 30 im Arbeitsgebiet |
| Feuerwachen | 118 | 114 | |
| Wertstoffhöfe | 22 | 21 | Enthält private Betreiber, muss noch gefiltert werden |
| Busrouten | 729 | – | Viele Mitglieder fehlen im Abzug, deshalb bleibt GTFS die Quelle für Buslinien |

- Einbahnstraßen mit Radverkehr in Gegenrichtung: 1.545 Wege (`oneway=yes`, `oneway:bicycle=no`).
- Gegen die Zeichenrichtung (`oneway=-1`): 18 Wege. Die Richtung bleibt jetzt erhalten.
- 8.546 Barrieren auf befahrbaren Wegen haben keine Zufahrtsangabe. Ob sie Kfz sperren, ist je Typ zu entscheiden.
- **Annahme bei der Auswahl:** Fuß- und Radwege, Treppen und Ähnliches zählen nur als befahrbar, wenn `motor_vehicle` oder `vehicle` gesetzt und nicht `no` ist.

## 8. Lücken im Bestand

Diese Punkte müssen vor Phase 3 gelöst werden:

1. `fill_order` wird geladen, aber nicht ausgewertet (`pipeline/lib/profile.py`). Phase 3 setzt diese Reihenfolge voraus.
2. Der Querschnitt erkennt Einbahnstraßen nur mit amtlichen Fahrstreifendaten, und `oneway=-1` verliert in `pipeline/lib/features.py` die Richtung.
3. Regel PL-06 (Gegenrichtungsradverkehr) ist nicht im Code umgesetzt. Das Radnetz erlaubt Gegenrichtung nur bei `oneway:bicycle=no`.
4. Die Pipeline hat keinen Szenario-Mechanismus. Die Stufennummer `c09` ist bereits vergeben.
5. Szenario D eignet sich nicht als Grundlage: Es rechnet ohne Fahrtrichtungen und zeigt auf 55 % der Abschnitte keinen Verkehr. Für Phase 2 wird ein neues gerichtetes Modell gebaut.

## 9. Pilotquartiere

| Quartier | Stadtstruktur | Fläche | Einwohner | Wohnstraßen | davon N4 | Bus auf Wohnstraßen | Radnetz HAUPT |
|---|---|---:|---:|---:|---:|---:|---:|
| Hoheluft-Ost/Eppendorf | Gründerzeit | 57 ha | 9.786 | 7,3 km | 47 % | 0 km | 3,2 km |
| Wilhelmsburg | Bus-Pilot | 174 ha | 13.059 | 13,7 km | 53 % | 4,9 km | 5,6 km |
| Fuhlsbüttel/Ohlsdorf/Langenhorn | HAUPT-Pilot | 189 ha | 11.190 | 17,4 km | 41 % | 2,3 km | 7,7 km |
| Horn | Nachkriegszeit | 83 ha | 7.333 | 6,8 km | 41 % | unter 0,1 km | 2,0 km |
| Tonndorf/Rahlstedt/Farmsen-Berne | Locker bebaut | 100 ha | 4.025 | 7,3 km | 55 % | 0,8 km | 4,2 km |

N4 ist ein Modellhinweis ohne Fahrtrichtungen und keine gemessene Verkehrsmenge. Die Stadtstruktur ist eine eigene Einschätzung. Die Schanze wird wie jedes andere Quartier behandelt und erst im gesamtstädtischen Lauf gerechnet.

## 10. Nicht geprüft

- **SWOV:** Die Faktenblätter ließen sich nicht öffnen (Bot-Sperre).
- **Thomas & Aldred 2024** (Verkehrsmengen in Londoner Quartieren): Der Volltext war nicht abrufbar, deshalb sind die Zahlen hier nicht verwendet.
- **Samariterkiez:** Die Pressemitteilung nennt keine Zählergebnisse.
- **Hamburgisches Wegegesetz, Hamburger Zuständigkeiten, Urteilstexte:** nicht geöffnet. Die Gerichtsentscheidungen sind nur aus Pressemitteilungen bekannt.

Die offenen Punkte stehen in `docs/open_questions.md`, Abschnitt „Ruhige Quartiere“.

## Quellen

1. IVA Mobiliteitsbedrijf, Transport & Mobility Leuven: [Evaluatie Circulatieplan Gent, tweede periode april–november 2018](https://www.stad.gent/sites/default/files/onepager/cta/Evaluatierapport%20Circulatieplan%20Gent%202019%20finaal.pdf), Mai 2019, S. 140–141 und 163–167.
2. Furlong, Fevyer, Armstrong, Edwards, Aldred, Goodman: [Low Traffic Neighbourhoods in London reduce road traffic injuries](https://researchonline.lshtm.ac.uk/id/eprint/4676732), Injury Prevention, 2025, DOI 10.1136/ip-2024-045571.
3. Goodman, Furlong, Laverty, Thomas, Aldred: [Impacts of 2020 Low Traffic Neighbourhoods in London on Road Traffic Injuries](https://findingspress.org/article/25633), Findings, 23.07.2021, DOI 10.32866/001c.25633.
4. Agència de Salut Pública de Barcelona: [Salut als Carrers, Results Report](https://www.aspb.cat/wp-content/uploads/2021/10/English-ASPB_salut-carrers-resultsreport-Superblocks.pdf), 2021, S. 33–34 und 39–41.
5. Bezirksamt Mitte von Berlin: [Kiezblock Bellermannkiez, Evaluation der Zählungen](https://www.berlin.de/ba-mitte/politik-und-verwaltung/aemter/strassen-und-gruenflaechenamt/planung-entwurf-neubau/pdf/bellermannkiez-evaluation-zaehlung-online.pdf), ohne Datum. Die Folie zur Nachher-Zählung nennt den 24.04.2022, gemeint ist nach dem Zusammenhang April 2024.
6. EU Urban Mobility Observatory: [Ghent's traffic circulation plan](https://urban-mobility-observatory.transport.ec.europa.eu/resources/case-studies/gents-traffic-circulation-plan-belgium_en), 19.10.2017 (sechs Sektoren, 77 Straßen mit geänderter Fahrtrichtung, Kameras an drei Schlüsselstellen).
