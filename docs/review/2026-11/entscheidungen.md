# Review 2026-11 · Entscheidungsvorlage

Zum Ausfüllen durch prstolpe. Optionen und Wirkung: `optionen.md`. Bitte je Zeile die gewählte Option (Buchstabe) und
eine Anmerkung eintragen. Leer = nicht entschieden; „nichts tun“ ist immer möglich.

| ID | Frage | Optionen | Empfehlung | gewählte Option | Anmerkung |
|---|---|---|---|---|---|
| E1 | Prüfung gegen die Wirklichkeit | a nichts · b Prüflisten (Luftbild) · c b + Ortsbegehung 2 Bezirke · d externe Prüfung | b sofort, c vor nächster Regelrunde | | |
| E2 | Umgang mit Verkehrsmengen | A heute · B Obergrenze 0.14.0 · C A + Kennzeichnung „Reduktion nötig“ · D C + Umlegung als Prüfung · nichts | C (+ D als Prüfwerkzeug) | | |
| E3 | Sammelstraßen mit Linienbus | a nichts · b Busregel 100 · c Busregel 200 · d conn_gow 0,5 · e in_hvs aus Score | b | | |
| E4 | Rückkopplung Querschnitt → Kategorie | a nichts · b D5 als Regel, D7 als Liste · c auch D7 automatisch | b | | |
| E5 | Knotenzeile „Radroute quert GOW50“ | a nichts · b J-14 | b | | |
| E6 | Ist-Knotentyp | a nichts · b Ampel am eigenen Arm + Minikreisel · c b + amtliche LSA-Daten | b, c anfragen | | |
| E7 | Richtungsfahrbahnen, kurze Inseln | a nichts · b gemeinsam einstufen + glätten | b | | |
| E8 | Randbereich außerhalb Hamburgs | a nichts · b nicht einstufen | b | | |
| E9 | Zweirichtungsradwege, Lage | a nichts · b S-3 + Lage je Seite · c nur Lage | b | | |
| E10 | Amtliches Radnetz | a nichts · b Mindestnetz BASIS (Bestand + Planung) · c nur Bestand | b | | |
| E11 | Haltestellen, Einbahnstraßen | a nichts · b prüfbare Flags | b | | |
| E12 | Umwegprüfung Maschenrouten | a nichts · b über OD-Paare | b | | |
| E13 | Oberflächenkonzept | siehe 03_oberflaeche.md | siehe dort | | |
| E14 | Export und Formalia | a nichts · b sofort | b | | |
| E15 | Varianten auf der Seite | a nichts · b B als zweite Ansicht · c + D-Varianten | b nach E2 | | |

## Vorgeschlagene Umsetzungsreihenfolge (Pakete)

Jedes Paket = ein Prompt bzw. ein Commit-Stapel mit neuer meta.version und CHANGELOG-Eintrag; `make test` grün.

| Paket | Inhalt | Voraussetzung | Neurechnung | grob |
|---|---|---|---|---|
| P0 Sofort | E14 (Kachel-Metadaten, Formalia, source_policy) | — | Export | 1 h |
| P1 Prüfen | E1 b: Prüflisten ausfüllen (Werkzeug: Liste mit Links, Spalten reviewer/assessment) | — | keine | 10 h Prüfzeit |
| P2 Straßenregeln | E2 (C: Reduktionszahl + Steckbrieftext), E3, E7, E8 | E1 b für die Schwellen wünschenswert | ab classify (≈ 18 min) | 1 Tag |
| P3 Rückkopplung | E4, E5, E12 | P2 | ab coherence, zweiter Durchlauf | 1 Tag |
| P4 Knoten-Eingangsdaten | E6 | — | ab junctions | ½ Tag |
| P5 Radanlagen | E9, E10, E11 | P2 | ab cycle-network | 1–2 Tage |
| P6 Oberfläche | E13, E15 | P2 (Kennzeichnung), Phase-3-Konzept | Export + Web | nach Konzept |
| danach | Prompt 22 (Zielszenario, gerichtete Umlegung auf Basis Szenario D) und Prompt 23 | P2, P3 | — | — |

## Vor einer Entscheidung zu klären

Siehe `optionen.md`, Abschnitt „Offene Fragen, die vor einer Entscheidung beantwortet sein müssen“ (13 Punkte); die
dringlichsten: CROW-Profil mit Radweg (E2), Quelle für die Busregel (E3), Prüfer für die Stichproben (E1).
