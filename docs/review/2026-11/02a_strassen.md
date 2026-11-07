# Review 2026-11 · Phase 2a: Straßenklassifikation

Stand: rules.yaml 0.16.0 (= Szenario A). Skripte unter `analysis/review_2026_11/`: `errors_2a.py` (Fehlerbilder),
`dryrun.py` + `variants_2a.py` (Trockenläufe der Kaskade), `make_patch_B.py` + `run_worktree.sh` (Szenario B, voller
Lauf im Worktree), `scenario_c.py`, `scenario_d.py` + `scenario_d_eval.py`, `compare_scenarios.py`. Ergebnisse unter
`data/scenarios/` (nicht in Git).

**Trockenlauf:** `dryrun.py` rechnet die Kaskade (s05) mit einer geänderten Kopie von rules.yaml auf den gespeicherten
Merkmalen, in 8 s. Die Basis ist geprüft identisch mit `classified.parquet` (34 702 Abschnitte); der Probelauf aus
open_questions.md Zeile 124 (+430 km GOW ohne `in_hvs` im `conn_score`) wird exakt reproduziert (430,0 km).
Harmonisierung, Kohärenz und Radkette sind im Trockenlauf nicht enthalten. Szenario B ist ein voller Lauf ab `classify`.

## Kurzfassung

1. **Hauptfehlerbild: Sammelstraßen mit Bus als Quartiersstraße.** 442 km `primary/secondary/tertiary` sind ETW30,
   310 km davon mit Linienbus (Median 176 Fahrten/Werktag), 392 km heute mit 50 km/h. Drei voneinander unabhängige
   Stellschrauben (Busregel, `conn_gow`, `in_hvs` im Score) verschieben denselben Kern von rund 190 km.
2. **Verkehrsmengen:** Die vier Varianten A–D unterscheiden sich vor allem auf rund 380 km Hauptverkehrsstraße
   (GOW30 ↔ GOW50). Szenario D (einfache Umlegung) zeigt: Tempo 30 allein senkt die Belastung dieser Straßen kaum unter
   die CROW-Grenze. Ohne Schutz der Wohngebiete weicht Verkehr auf ETW30 aus (178 km mit mehr als 2 500 Kfz/Tag
   zusätzlich); mit Schutz bleibt er auf GOW30/GOW50.
3. **Empfehlung (nicht entschieden):** Variante **C** (Funktion zuerst, GOW30 mit Kennzeichnung „Verkehrsreduktion nötig“)
   als Standard. **D** ist als Prüfwerkzeug für die Kennzeichnung zu verwenden, nicht als Kategorie-Regel. B nur als
   gespeicherter Vergleichsstand.
4. **Weitere Fehlerbilder:** 206 Paare von Richtungsfahrbahnen mit unterschiedlicher Kategorie; 345 kurze
   Kategorie-Inseln (21 km); 180 km klassifiziertes Netz außerhalb Hamburgs mit halbiertem `conn_score` (Randeffekt);
   252 km ohne Ist-Tempo.

---

## 1 Fehleranalyse

Vergleichsgrundlagen: HVS-Netz (`in_hvs`, DTV-Zählkarte 2019), Ist-Tempo (`speed_ist_kmh`), OSM-Straßenklasse,
Busfahrten (GTFS). Rückmeldungen und Stichproben gibt es nicht (`01_bestand.md`, Abschnitt 4).

### Straßenklasse gegen Soll-Kategorie (km)

| highway | ETW30 | ETW_ERF | GOW30 | GOW50 | SW |
|---|---:|---:|---:|---:|---:|
| motorway | 0 | 0 | 0 | 0 | 111,1 |
| trunk | 0,1 | 0 | 0,9 | 3,6 | 35,1 |
| primary | **14,0** | 0 | 192,8 | 83,4 | 0 |
| secondary | **37,2** | 0 | 263,9 | 108,5 | 0 |
| tertiary | **390,9** | 0 | 55,6 | 18,8 | 0 |
| unclassified | 248,5 | 0 | 0,8 | 1,9 | 0 |
| residential | 2 339,2 | 9,8 | 11,2 | 2,7 | 0 |

### Ist-Tempo gegen Soll-Kategorie (km)

| Soll | ≤ 20 | 30 | 40–50 | > 50 |
|---|---:|---:|---:|---:|
| ETW30 | 67,0 | 2 186,5 | **845,7** | 31,8 |
| ETW_ERF | 86,2 | 2,5 | 1,2 | 0 |
| GOW30 | 0,4 | 17,4 | 500,6 | 8,7 |
| GOW50 | 0 | 5,1 | 169,7 | 47,3 |
| SW | 0 | 0 | 13,3 | 151,7 |

Ohne Ist-Tempo: 252 km (5,7 % der Länge).

### Fehlerbilder

| # | Fehlerbild | Umfang | systematisch? | Beispiele |
|---|---|---|---|---|
| E1 | Sammelstraßen mit Bus als ETW30 | 442 km primary/secondary/tertiary als ETW30; 310 km mit Bus; alle ETW30 mit Bus 610 km, mit ≥ 100 Fahrten/Werktag 329 km | ja: `conn_score` 0,47 im Median (Schwelle 0,6), `in_hvs` false, weil keine DTV-Zählung | [Reclamstraße](https://hamburgmobility.de/#karte?seg=seg_e7d085cbb1283597), [Heegbarg](https://hamburgmobility.de/#karte?seg=seg_6db74f26243f9cac), [Dammtorstraße](https://hamburgmobility.de/#karte?seg=seg_099ca33334dc8281); längste: Wiesendamm 3,6 km, Peutestraße 3,2 km, Alsterdorfer Straße 3,2 km, Walddörferstraße 3,0 km, Rübenkamp 2,4 km |
| E2 | ETW30 mit Ist 40–50 km/h | 846 km (tertiary 329, residential 265, unclassified 137) | überwiegend E1; dazu Landstraßen am Stadtrand (Elbuferstraße, Wiemerskamper Weg, Glashütter Landstraße) | [Wiemerskamper Weg](https://hamburgmobility.de/#karte?seg=seg_94c8273025255714), [Glashütter Landstraße](https://hamburgmobility.de/#karte?seg=seg_aff09d1500cad217) |
| E3 | Richtungsfahrbahnen mit verschiedener Kategorie | 206 Paare (GOW30/GOW50 104, ETW30/GOW30 63, ETW30/GOW50 35); 14 km | ja: C-G30-01 wertet Schule/Läden je Fahrbahn, H-STR-01 harmonisiert nur entlang eines Zuges | Friedrich-Ebert-Damm: [GOW30](https://hamburgmobility.de/#karte?seg=seg_0cda7fe5a634615f) gegenüber [GOW50](https://hamburgmobility.de/#karte?seg=seg_32ae10a3aa8e3490); Finkenwerder Straße: [ETW30](https://hamburgmobility.de/#karte?seg=seg_55ebdb094e709647) gegenüber [GOW50](https://hamburgmobility.de/#karte?seg=seg_edb6b130bc49f117) |
| E4 | kurze Kategorie-Inseln (< 200 m, N2 min_run_m) zwischen gleichen Nachbarn | 345 Abschnitte, 20,7 km (ETW30 11,3, ETW_ERF 7,4, GOW50 1,4, GOW30 0,6) | teilweise: H-STR-01 glättet nur GOW30 | [Bramfelder Straße](https://hamburgmobility.de/#karte?seg=seg_4c17a21bd813d5f3), [Thüreystraße](https://hamburgmobility.de/#karte?seg=seg_9c531027ac5eb40b) |
| E5 | Randeffekt am Netzrand | 180 km klassifiziert außerhalb Hamburgs (ETW30 169 km); `conn_score` secondary dort 0,38 statt 0,70–0,75 | ja, aber nur außerhalb der Stadtgrenze; innerhalb kein Abfall zum Rand | — |
| E6 | Brücken | 290 Abschnitte, 43,7 km (GOW50 17,0, ETW30 17,3, GOW30 8,9); Breite unbekannt 7,8 km; GOW30 nur wegen fehlender Breite (C-G30-02) 0,8 km | nein | — |
| E7 | GOW30 über Publikumsnutzung mit < 50 Einwohnern im Umfeld | 34,3 km, davon Hamburg-Mitte 20,9 km | nein: Innenstadt (Mönckebergstraße, Wallringtunnel); Hafen ohne Auffälligkeit | [Wallringtunnel](https://hamburgmobility.de/#karte?seg=seg_f114bbaf73979996) |
| E8 | fehlende Daten | Ist-Tempo fehlt auf 252 km; DTV nur auf 763 von 4 387 km | Datenlücke | — |

**Außerbereiche Vier- und Marschlande:** nicht klassifiziert (17 ländliche Stadtteile, `rural_exclude` approved). GOW80/
ETW60 kommen in `cat_final` nicht vor. Kein Befund möglich, solange die Ortsgrenze fehlt (offene Frage Zeile 51).

## 2 Umgang mit Verkehrsmengen: Szenarien A–D

| | A Funktion zuerst | B Status quo 0.14.0 | C GOW30 unter Auflagen | D Netzwirkung |
|---|---|---|---|---|
| Regel | Umfeld entscheidet GOW30/GOW50; DTV nur Diskrepanz/Flag (heute 0.16.0) | DTV > 10 000 auf HVS → GOW50 (C-G50-02) | wie A, plus Kennzeichnung und nötige Reduktion | wie A/C, Prüfung mit Umlegung auf dem Soll-Netz |
| Rechnung | Produktivstand | voller Lauf ab classify im Worktree | Nachrechnung auf A | Modell `scenario_d.py`, 9 Varianten |
| GOW30 | 528 km | 144 km | 528 km | 528 km |
| GOW50 | 223 km | 607 km | 223 km | 223 km |
| HVS als GOW30 / GOW50 | 467 / 201 km | 87 / 581 km | 467 / 201 km | 467 / 201 km |
| GOW30 über 10 000 Kfz/Tag ohne baulichen Radweg | 106 km | 23 km | 106 km, davon „Reduktion nötig“ 106 km | 15–41 km werden tragfähig (je nach Annahme) |
| Soll-Einrichtungsradweg / Radfahrstreifen | 400 / 351 km | 589 / 162 km | wie A | wie A |
| Knoten mit Handlungsbedarf | 2 619 | 2 712 | wie A | wie A |
| RSV/HAUPT auf GOW50 ohne Platz (K1) | 9,6 km | 22,8 km | wie A | wie A |
| Radroute quert GOW50 ohne geeigneten Knoten (K3) | 55 | 219 | wie A | wie A |
| Diskrepanz Stärke 2/3 | 1 335 / 82 km | 1 056 / 51 km | wie A | — |

### Szenario C im Einzelnen

Von 453 km GOW30 mit DTV liegen 401 km über dem breiten CROW-Profil (10 000 Kfz/Tag). **296 km davon haben einen
baulichen Radweg**; dafür hat CROW kein Profil mit DTV-Grenze, D-USE-01 wertet sie nicht als Verstoß. Es bleiben
**106 km (1 015 Abschnitte), auf denen eine Verkehrsreduktion nötig ist**:

| nötige Reduktion (Anteil am DTV) | km |
|---|---:|
| bis 25 % | 14,5 |
| 25–50 % | 47,7 |
| 50–75 % | 36,0 |
| über 75 % | 7,7 |

Reduktion in Kfz/Tag: Quartile 4 000 / 10 000 / 17 000. Je Bezirk: Wandsbek 20,3, Hamburg-Mitte 23,4, Altona 20,5,
Hamburg-Nord 18,3, Eimsbüttel 11,9, Harburg 7,1, Bergedorf 4,4 km. Straßenliste:
`data/scenarios/C_gow30_reduction/scenario_c_streets.csv`.

**Steckbrief-Vorschlag** (für Phase 3): Kurzantwort „Stadtstraße 30 – setzt weniger Kfz-Verkehr voraus“, dann „heute
24 000 Kfz/Tag, tragfähig bis 10 000 (CROW), nötig −14 000“, dann Maßnahmenkandidaten: (1) Durchfahrtsunterbrechung
oder modaler Filter, wenn D eine Ausweichroute auf GOW50/SW zeigt; (2) Netzänderung im Korridor (Fahrstreifenabbau auf
einer Parallelstrecke), wenn nicht; (3) Fahrstreifenabbau auf der Straße selbst (L-02). Keine Automatik, nur Hinweise.

### Szenario D im Einzelnen

**Modell** (alle Werte außerhalb der Regelwerke sind `assumption`, Liste in `scenario_d_meta.json`):
- Netz: 34 702 Kfz-Abschnitte, ungerichtet.
- Zonen: 858 Zonen (1 km) aus Zensus und ALKIS-Geschossfläche, dazu 61 Einfahrpunkte an der Landesgrenze mit DTV 2019.
- Verteilung: Schwerkraftmodell exp(−β t).
- Umlegung: inkrementell in 4 Stufen, BPR-Widerstand.
- Kapazität: Fahrstreifen × 900 Kfz/h (L-02) / (0,10 × 0,55).

**Kalibrierung** an 5 180 gezählten Abschnitten:
- Spearman 0,53, 53 % innerhalb Faktor 2, GEH < 10 nur 6 %; Pegel im Median 0,53 der Zählung.
- β = 0,07/min gewählt aus 0,04/0,07/0,10/0,14 (Spearman 0,52–0,53, kaum Unterschied).
- Die Güte entspricht etwa dem Radmodell (Spearman 0,53, 41 % in Faktor 2).

Für die Soll-Werte wird deshalb der Quotient Soll/Ist auf die Zählung angewendet (Pivot), nicht der Modellwert.

**Soll-Netz:**
- Tempo je Kategorie, Fahrstreifen Soll aus dem Querschnitt.
- ETW-Widerstand ×1,0 (nur Tempo), ×1,5 (Gestaltung nach DV) oder ×3,0 (Näherung für Filter).
- Verdampfung 0/10/20 % (`assumption`; Cairns, Atkins, Goodwin 2002 als zu prüfende Quelle).

| ETW-Faktor | Verdampfung | Kfz-km GOW30 | Kfz-km GOW50 | Kfz-km ETW30 | GOW30-Kandidaten tragfähig (von 106 km) | alle GOW30 > 10 000 tragfähig (von 401 km) | ETW mit +2 500 Kfz/Tag | Soll-Fahrradstraße > 2 500 Kfz/Tag (Modell; heute 184 km) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,0 | 0 % | −33 % | +12 % | **+11 %** | 29 km | 87 km | **178 km** | 237 km |
| 1,0 | 10 % | −39 % | +2 % | −3 % | 34 km | 105 km | 149 km | 209 km |
| 1,0 | 20 % | −46 % | −9 % | −17 % | 41 km | 125 km | 121 km | 177 km |
| 1,5 | 0 % | −12 % | +19 % | −46 % | 16 km | 48 km | 47 km | 110 km |
| 1,5 | 10 % | −20 % | +9 % | −54 % | 20 km | 60 km | 36 km | 94 km |
| 1,5 | 20 % | −29 % | −3 % | −60 % | 24 km | 72 km | 25 km | 76 km |
| 3,0 | 0 % | −1 % | +22 % | −67 % | 15 km | 42 km | 30 km | 73 km |
| 3,0 | 10 % | −11 % | +10 % | −71 % | 16 km | 50 km | 21 km | 61 km |
| 3,0 | 20 % | −21 % | −2 % | −75 % | 21 km | 66 km | 16 km | 51 km |

**Lesart:**
- **Nur Tempo 30 auf den GOW30 (Faktor 1,0):** Verkehr weicht auf GOW50, SW und **Quartiersstraßen** aus. Beispiele mit
  Mehrbelastung > 1 000 Kfz/Tag: Isestraße, Bundesstraße, Walddörferstraße, Lottbeker Weg, Böttcherkamp, Tegelweg (Liste
  `D_assignment/scenario_d_ratrun_streets.csv`). Viele GOW30 werden leichter, aber die Wohngebiete tragen die Last.
- **Wohngebiete geschützt (1,5 oder Filter 3,0):** Der Schleichverkehr verschwindet weitgehend. Der Verkehr bleibt dann
  auf den Hauptstraßen; GOW30 werden kaum leichter, GOW50 und Autobahnen schwerer. Von den 106 km Kandidaten werden nur
  15–24 km tragfähig.
- **Verdampfung** hilft gleichmäßig, aber in der geprüften Spanne (bis 20 %) nicht ausreichend.
- **Folgerung:** Die meisten GOW30-Kandidaten über 10 000 Kfz/Tag sind nur mit Netzmaßnahmen auf Korridorebene
  tragfähig (Kapazität der Parallelstrecke, Fahrstreifenabbau), nicht mit Tempo und Gestaltung allein. Das ist die
  Aufgabe von Prompt 22 (Zielszenario).

**Grenzen:** ungerichtet (keine Einbahnstraßen, keine Abbiegeverbote); kein Wirtschaftsverkehr gesondert; keine
Moduswahl (Verdampfung pauschal); Kalibrierung mäßig. Das Ergebnis taugt für Richtung und Größenordnung, nicht für
einzelne Abschnitte.

### Empfehlung (begründet, nicht entschieden)

**C als Regel, D als Prüfung:**
- **DV-konform:** C folgt Funktion → Gestaltung → Nutzung. Die heutige Belastung macht keine Straße zur Magistrale,
  sondern zeigt, was sich ändern muss.
- **Ehrlich:** C kennzeichnet die 106 km, die nur mit weniger Verkehr funktionieren, und nennt die Größe der Aufgabe in
  Kfz/Tag.
- **Kleiner Aufwand:** Die Kennzeichnung gibt es fast schon (Flag `gow30_dtv_above_profile`); es fehlen die Reduktionszahl
  und der Text im Steckbrief.
- **D zeigt Grenzen:** Ohne Netzmaßnahmen erreicht nur ein Viertel der Kandidaten das Profil. Das sollte auf der Seite
  stehen (als Annahme gekennzeichnet), damit GOW30 nicht als „nur Schild tauschen“ gelesen wird.
- **Gegen B:**
  - Mit B wird die heutige Menge zur Funktion. Die Radkonflikte steigen (K1 ×2,4, K3 ×4).
  - B verschiebt 380 km HVS zu GOW50, wo baulich getrennte Radwege nötig werden: 589 statt 400 km Einrichtungsradweg.
  - Als „Kompromiss Hamburg“ bleibt B gespeichert (Tag `variante-gow50-kompromiss`) und kann als zweite Ansicht auf der
    Seite gezeigt werden (offene Frage Zeile 71).

## 3 Weitere Verbesserungen (Trockenläufe)

Struktur je Vorschlag: Problem · Beleg · Vorschlag · Wirkung (Trockenlauf) · Risiken · Aufwand · source_type.

### S-1 Linienbus als Verbindungsfunktion

- **Problem:** E1, Sammelstraßen mit Bus als ETW30.
- **Beleg:** 610 km ETW30 mit Bus, 329 km mit ≥ 100 Fahrten/Werktag.
- **Vorschlag:**
  ```yaml
  # rules.yaml C-GOW-01
  - if: "conn_score >= thresholds.conn_gow or in_hvs"
  + if: "conn_score >= thresholds.conn_gow or in_hvs or bus_trips_weekday >= thresholds.bus_gow"
  + bus_gow: {value: 100, unit: "Busfahrten je Werktag", source_type: assumption}
  ```
- **Wirkung (Trockenlauf):**

  | Schwelle | Änderung | ETW30 → GOW30 | ETW30 → GOW50 | Bezirke (km) |
  |---|---:|---:|---:|---|
  | 100 Fahrten | 3 334 Abschnitte, 330 km | 225 km | 105 km | Wandsbek 74, Mitte 62, Altona 47, Nord 43, Eimsbüttel 40, Bergedorf 31, Harburg 24 |
  | 200 Fahrten | 1 980 Abschnitte, 186 km | 137 km | 49 km | Wandsbek 36, Mitte 32, Altona 32, Nord 27, Eimsbüttel 24 |

  Beispiele: [Poppenbütteler Straße](https://hamburgmobility.de/#karte?seg=seg_7eba63965a884180), [Berzeliusstraße](https://hamburgmobility.de/#karte?seg=seg_2d7801fd9c99a1ab), [Suurheid](https://hamburgmobility.de/#karte?seg=seg_8e2507a69e36963d).
- **Risiken:**
  - Busse auf Erschließungsstraßen sind in DV unerwünscht, aber üblich (Quartiersbusse). Die Regel macht aus der
    heutigen Linienführung eine Funktion. Das ist Nutzung → Funktion, abgeschwächt durch die Planungsentscheidung der
    Linie.
  - Löst K2 (Fahrradstraße mit Bus).
- **Aufwand:** klein (eine Bedingung, golden case, CHANGELOG).
- **source_type:** assumption. CROW-Grundsatz „ÖV auf GOW“ als Quelle prüfen.

### S-2 Alternative: `conn_gow` kalibrieren

- **Problem:** wie S-1, über den Score.
- **Vorschlag:** 0,6 → 0,5.
- **Wirkung:** 2 474 Abschnitte, 266 km (ETW30 → GOW30 177 km, → GOW50 90 km). Überschneidung mit S-1: 190 km gemeinsam.
- **Risiken:** wirkt auch auf Straßen ohne Bus (Betweenness).
- **Aufwand:** klein.
- **source_type:** assumption (Kalibrierung, offene Frage Zeile 123).

### S-3 Alternative: `in_hvs` aus dem `conn_score` nehmen

- **Problem:** Abzug für Nicht-HVS.
- **Wirkung:** 3 889 Abschnitte, 430 km (→ GOW30 271 km, → GOW50 159 km). Überschneidung mit S-1 262 km.
- **Risiken:** größter Eingriff. HVS sind ohnehin GOW; der Vorschlag wirkt nur auf Nicht-HVS.
- **Aufwand:** klein; s04 neu rechnen.
- **source_type:** assumption.

**Empfehlung:** S-1 mit 100 Fahrten, weil sie den Mechanismus benennt (Linienbus = Verbindungsfunktion) und mit 330 km
den gemeinsamen Kern von S-2/S-3 trifft. S-2/S-3 bleiben Kalibrierungsfragen für die Fachplanung.

### S-4 Randbereich außerhalb Hamburgs nicht einstufen

- **Problem:** E5. 180 km außerhalb der Landesgrenze sind klassifiziert, mit halbiertem `conn_score`.
- **Vorschlag:** `cat_final` nur innerhalb der Bezirke; der Ring bleibt Rechennetz (Betweenness, Radnetz).
- **Wirkung:** 180 km entfallen auf der Karte und in den Kennzahlen „ohne Bezirk“.
- **Risiken:** keine fachlichen.
- **Aufwand:** klein.
- **source_type:** keine neue Schwelle.

### S-5 Richtungsfahrbahnen gemeinsam einstufen

- **Problem:** E3, 206 Paare mit verschiedener Kategorie.
- **Vorschlag:** neue Harmonisierungsregel: parallele Abschnitte gleichen Namens (Hausdorff-Abstand < 60 m) erhalten die
  höhere Kategorie des Paares (H-STR-02).
- **Wirkung:** 206 Paare, 14 km (Mindestseite) ändern die Kategorie.
- **Risiken:** Straßen mit echter Seitenungleichheit (Schule nur auf einer Seite) verlieren das GOW30 auf einer Seite. Die
  höhere Kategorie ist hier die vorsichtige Wahl, weil eine Straße nur ein Tempo haben kann.
- **Aufwand:** mittel.
- **source_type:** assumption.

### S-6 Glättung kurzer Inseln

- **Problem:** E4.
- **Vorschlag:** H-STR-01 auf ETW30/ETW_ERF und GOW50 ausweiten: Inseln < 200 m (N2) zwischen gleichen Nachbarn bekommen
  die Nachbarkategorie. Ausnahme ETW_ERF aus amtlichem verkehrsberuhigtem Bereich.
- **Wirkung:** bis zu 345 Abschnitte, 20,7 km.
- **Risiken:** ETW_ERF-Abschnitte (Spielstraßen) verschwinden. Deshalb die Ausnahme.
- **Aufwand:** klein.
- **source_type:** assumption (N2 vorhanden).

### S-7 Fehlende DTV und fehlendes Ist-Tempo

- **Problem:** DTV auf 17 % der Länge; Ist-Tempo fehlt auf 252 km.
- **Vorschlag:** keine Imputation in der Klassifikation (Gewicht wird umgelegt, Entscheidung 2026-11-07). Stattdessen den
  Modellwert aus Szenario D nur als Prüfgröße für ETW30 (Schleichverkehr) und Fahrradstraßen (2 500 Kfz/Tag) zeigen, als
  Annahme gekennzeichnet.
- **Wirkung:** 184 km Soll-Fahrradstraße liegen heute im Modell über 2 500 Kfz/Tag. Das ist ein Hinweis, kein Verstoß.
- **Risiken:** Modellgüte.
- **Aufwand:** mittel.
- **source_type:** assumption.

### S-8 Außerorts-Kategorien

- **Problem:** GOW80/ETW60 kommen nicht vor.
- **Vorschlag:** keiner, solange die Ortsgrenze fehlt. Zuerst die Datenquelle beschaffen (offene Frage Zeile 51).
- **Wirkung:** —.

## 4 Offene Punkte aus dieser Phase

- Schwelle `bus_gow` ist eine Annahme; Quelle für „ÖV auf GOW“ in CROW prüfen.
- Szenario D braucht einen gerichteten Graphen (Einbahnstraßen) und eine bessere Kalibrierung, bevor Zahlen je Abschnitt
  auf die Seite kommen (Prompt 22 Stufe B).
- CROW-Profil mit baulichem Radweg: ob GOW30 mit Radweg wirklich ohne DTV-Grenze gilt (296 km), am Original prüfen.
