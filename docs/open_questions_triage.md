# Offene Fragen – Sortierung (Stand 2026-11-07)

Sortierung der 145 offenen Punkte aus docs/open_questions.md (Stand nach Prompt 21). Nummern = Reihenfolge der
offenen Punkte in open_questions.md vor dieser Sortierung. Der Wortlaut steht dort; hier nur Kurzform.

| Gruppe | Anzahl |
|---|---|
| A Erledigt/doppelt – geschlossen | 9 |
| B Formales Aufräumen (keine Werte ändern sich) | 5 |
| C Jetzt entscheiden (Projektleitung) | 57 |
| D Fachplaner*in (Original prüfen, Annahmen freigeben) | 37 |
| E Aufgaben (Prüflisten, Daten, Organisation) | 33 |
| F Zurückstellen (betrifft derzeit nichts) | 4 |

## A Erledigt oder doppelt (2026-11-07 geschlossen)
72 Range-Prüfung (doppelt zu 145) · 76 R2 (510 MB reichen) · 77 Soll-Skizze im Steckbrief (Prompt 21) ·
81 Amselweg (nur Info) · 98 Seitengröße ganz Hamburg · 110 J-01 „space ok“ (Prompt 20) ·
zusammengeführt: 48 → 93 · 62 → 46 · 63 → 89

## B Formales Aufräumen
Erledigt Claude Code in einem Schritt (rules.yaml-Version + CHANGELOG), sobald freigegeben.
- 8 `status`-Freitext bei sidewalk_m/carriageway_2lane_m → status draft + note
- 9 Einheit Kfz/24h bei GOW30 `max_dtv`
- 10 `source_type: assumption` als Feld statt Kommentar (scores, risk_weights)
- 12 guide.md 3.3: Merkmalsnamen an rules.yaml angleichen
- 49 guide.md: `cat_confidence` → `confidence`

## C Jetzt entscheiden
**Hohe Wirkung – zuerst** (Stapel 1–4):
1. Radnetzumfang: 126 HAUPT auf ETW30 = 1 383 km Soll-Fahrradstraße · 114 Delfter Maschenweiten (2 000 km HAUPT
   gegenüber 371 km amtlich) · 125 Radweg an ETW30 statt Fahrradstraße gleichwertig (248 km) · 115 P-ATT-03 Teilverlegung
2. Knotenpunkte: 133 fehlende Zeilen (412 Knoten `no_rule`) · 134 J-03 ohne DTV-Grenze (232 Kreisverkehre) ·
   135 eigene Zeilen ETW_ERF · 137 LSA-Radius für Ist-Typ
3. GOW30 und Querschnitt: 46 + 130 HVS als GOW30 (60 % der HVS-km; 362 km GOW30 über 10 000 Kfz/Tag) ·
   131 Mindestfahrbahn 5,80 m in schmalen Wohnstraßen (31 % passt nicht) · 108 Breite eigener Radtrassen
4. Veröffentlichung: 71 Impressum (Name/Anschrift) · 70 Rückmelde-E-Mail oder nur GitHub ·
   112 Kalibrierung Nachfrage (Faktor Hauptstraße ohne Radweg 2,0 → 1,5?)

**Geringe Wirkung – als Sammelfreigabe mit Empfehlung von Claude Code:**
- Netz/Segmentierung: 14, 15, 16, 17, 24
- Conflation/Merkmale: 19, 21, 23, 28, 29, 30, 32, 33, 35, 36
- Querschnitt/Klassifikation: 39, 41, 42, 43, 45, 47
- Kohärenz/Diskrepanz: 52, 53, 54, 65, 68
- Harmonisierung/Validierung: 78, 80, 84, 85, 87, 91, 92
- Gebiet: 95 ländliche Stadtteile, 96 Hafenstraßen
- Radnetz: 105, 116, 121, 122, 128, 129, 140

## D Fachplaner*in
Original prüfen oder Annahmen freigeben; gesammelt für einen Termin mit Verkehrsplaner*in bzw. den externen Review.
- Regelwerk Straßen: 1, 2, 3, 4, 6, 7, 11, 13, 18, 26, 27, 31, 40, 44, 50, 51, 55, 56, 57, 66, 79, 82, 83, 86
- Radnetz: 100, 101, 102, 103, 104 (Vorrang am Kreisverkehr, Rechtsprüfung), 107, 111, 113, 118, 124, 127, 132, 141

## E Aufgaben
- **Dringend:** 37 GTFS-Fahrplan endet 2026-12-12 → neuen Feed abrufen · 74 Lizenz der Tempo-/DTV-Daten klären
  (vor Veröffentlichung) · 145 Veröffentlichung (nur mit OK)
- Prüflisten ausfüllen: 38, 59, 60, 61, 93, 123, 139, 143
- Daten beschaffen/klären (GIS): 20, 22, 25, 34, 58, 64, 67, 88, 89, 90, 106, 117, 119 (Knotentyp für P-SAF-02 jetzt
  aus Prompt 20 verfügbar), 120, 142
- Organisation: 5, 69, 73, 75, 94, 99, 144

## F Zurückstellen
97 Neuwerk/Scharhörn · 109 ETW60 außerorts · 136 Kreisverkehr mit Wartepflicht außerorts (GOW80/ETW60 kommen in
cat_final nicht vor, solange ländliche Stadtteile ausgeschlossen sind) · 138 Straßenbahn (keine in Hamburg)
