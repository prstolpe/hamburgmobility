# QA Bäume und Parkplätze (Stufe c09) – unabhängige Prüfung, 2026-11-17

Alle Projektdateien nur gelesen. Orthophotos und Straßenbilder konnte ich **nicht** ansehen (kein geprüfter Bilddienst); alle Aussagen beruhen auf Neuberechnung aus den Rohdaten. Prüfskripte: `scratchpad/q1..q11.py`.

## Ergebnisse je Prüfpunkt
1. **Einheiten:** keine negativen Werte, nutzbare Bordlänge nie über der Länge. 353 (links) bzw. 354 (rechts) Seiten (je ca. 1 %) haben mehr als 1 Platz je 4,5 m, fast alle amtlich (Quer-/Schrägparken, Plätze, z. B. Eimsbütteler Marktplatz 54 auf 59 m): plausibel. Plätze je km (amtlich, Median): ETW30 208, GOW50 118, GOW30 130. OSM-Median 0 (viele „kein Parken“).
2. **Doppelzählung:** Zuordnung ist je Fläche/Baum eindeutig. Meine Neuableitung (strikt nächster Abschnitt, dann Abstandsgrenze): Bäume 188 459 statt 190 567 (−1,1 %; Bezirke −0,3 bis −1,1 %), Flächen 194 286 statt 194 535 (−0,13 %). Die Differenz stammt aus der großzügigeren Regel im Code (nächster Abschnitt innerhalb *seiner* Grenze). An Kreuzungen keine Doppelzählung (2,0 % der Flächen liegen ≤ 5 m vor einem Knotenende, zählen aber nur einmal und ohne Abstandsabzug).
3. **Fehlend ≠ 0:** 19 361 Abschnitte ohne Daten haben NaN. Bezirkssummen = Summe der Abschnitte (exakt). Dokumentiert: 3 065 Abschnitte setzen die Gegenseite auf 0 („official_zero“), davon 293 kürzer als 30 m (Risiko an Kurzabschnitten). Undokumentiert, klein: 7 vollständige Abschnitte ohne Ziel (5 Plätze) fehlen in den Zielsummen.
4. **Spannen:** keine Verletzung (Min ≤ Max, Bäume Min ≤ Mitte ≤ Max ≤ n). Aber: untere Zahl „betroffen“ nur in 893 von 33 712 Abschnitten > 0. Meine Neurechnung: 3 553 / 21 233 / 159 138 (Code 3 557 / 21 286 / 159 600): Spanne bis 84 % aller Bäume, weil „Gehweg“ als unsicher gilt. Mit Gehweg = bleibt: Obergrenze 59 866.
5. **Handprüfung TP-T-02 (5 Straßen):** Osterstraße, Heimfelder Straße, Walddörferstraße, Hohe Straße, Ernst-August-Stieg: Bänder und Klassen folgen der Regel; Zahlen stimmen mit meinem Nachbau überein (z. B. Heimfelder 35 von 36 „möglicherweise“, Hohe Straße Radweg-Band 6,0–8,5 m mit 7 Bäumen betroffen).

## 30 Stichproben (Schätzung → meine Zählung)
Parken: amtlich = LBV-Flächen im Straßenraum (ohne Haltverbot), eindeutig zugeordnet. Bäume: Katasterstraße gleich Abschnittsname, im Straßenraum (Breite/2+2 m), ohne Zuordnungsregel.

| Straße | Parken | Bäume | Grund bei Abweichung |
| --- | --- | --- | --- |
| Große Bergstraße | 0 → 0 | 2 → 6 (+4) | 19 m kurz, Bäume nahe Nachbarabschnitt |
| Regerstraße | 17 → 17 | 5 → 5 | |
| Rissener Busch | 16 OSM, nicht prüfbar | 0 → 0 | |
| Beselerstraße | 5,6 → 2 Flächen (+3,6) | 2 → 2 | Schräg-Fläche 13,9 m als 3,6 Plätze |
| Weidemoor | keine Daten | 3 → 3 | |
| Oberer Landweg | keine Daten | 4 → 6 (+2) | Nachbarabschnitt |
| Eppendorfer Weg | 0 → 0 | 0 → 2 (+2) | Nachbarabschnitt |
| Lokstedter Holt | keine Daten | 1 → 1 | |
| Osterstraße | 25 → 25 | 21 → 23 | ok |
| Jungfrauenthal | 31,7 → 12 Flächen (+19,7) | 11 → 12 | Quer-Flächen 8,5–16,5 m als 3–6 Plätze gewichtet |
| Saling | 0 → 0 | 0 → 0 | |
| Horst-Böttjer-Weg | keine Daten | 12 → 8 (−4) | Kataster nennt anderen Straßennamen |
| Bremer Reihe | 49 → 49 | 7 → 9 (+2) | Nachbarabschnitt |
| Simon-von-Utrecht-Str. | 13,6 → 13 | 1 → 1 | ok |
| Tinnumer Weg | keine Daten | 1 → 1 | |
| Ernst-August-Stieg | 31 OSM, nicht prüfbar | 18 → 16 | ok |
| Barmbeker Markt | 0 → 0 | 0 → 0 | |
| Nirrnheimweg/Dannmeyerstr. | keine Daten | 15 → 15 | |
| Braamkamp | 0 → 0 | 0 → 0 | |
| Anita-Sellenschloh-Ring | 42 → 42 | 2 → 2 | |
| Kellinghusenstraße | 0 → 0 | 0 → 6 (+6) | 16 m kurz, Nachbarabschnitt |
| Beim Bergwerk | keine Daten | 5 → 7 (+2) | Nachbarabschnitt |
| Hohe Straße | 0 OSM → 0 | 12 → 18 (+6) | Nachbarabschnitt |
| Heimfelder Straße | 63 OSM, nicht prüfbar | 36 → 36 | |
| Kupferdamm | keine Daten | 5 → 6 | ok |
| Kielbarg | keine Daten | 10 → 9 | ok |
| Hochstraße | 24 → 24 | 3 → 3 | |
| Walddörferstraße | keine Daten | 14 → 16 | ok |
| Sedenkamp | keine Daten | 9 → 9 | |
| Hülsdornweg | keine Daten | 2 → 2 | |

## Fehlerquote
- **Parken:** 2 von 8 prüfbaren (25 %) weichen um > 20 % oder > 3 Plätze ab (Beselerstraße, Jungfrauenthal), beide wegen der Gewichtung langer Flächen. 22 von 30 sind mit LBV nicht prüfbar (12 + 8 ohne Daten bzw. nur OSM).
- **Bäume:** 8 von 30 (27 %) weichen ab (> 20 % oder > 2). Sieben liegen an meiner nicht ausschließlichen Zählung (Nachbarabschnitte), einer am Straßennamen. Gegen die eindeutige Zuordnung stimmen 30 von 30 exakt.
- Die wahre Fehlerquote gegen die Wirklichkeit ist ohne Bilder unbekannt.

## Hauptfehlerquellen und Anpassungen
1. **Schrägflächen:** 3 798 Flächen mit langer Seite > 7,8 m zählen als L/3,9, Mediannfläche 16,8 m² entspricht einem Platz. Überzählung ca. 2 900 Plätze (+1,1 %). Anpassung: Gewichtung nach Fläche/Einzelfläche je Aufstellart.
2. **„Absolutes Haltverbot“:** 1 984 Flächen zählen als Plätze (+0,8 %). Anpassung: zu `exclude_management` oder als unsicher.
3. **Spanne Bäume:** Obergrenze 159 600 aussagelos. Anpassung: Gehweg = bleibt (Obergrenze ca. 59 900).
4. **Hochrechnung** 1 225–576 381 (Faktor 470) ohne Aussage. Anpassung: nur aus Abschnitten desselben Bezirks mit amtlichen Daten.
5. **`official_zero`** an Kurzabschnitten (< 30 m): als „unbekannt“ statt 0 führen.

## Fünf Stichproben für die Sichtprüfung
1. Jungfrauenthal: [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565099,5937381]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968), [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.581238/9.983298): 12 Flächen, 31,7 Plätze?
2. Beselerstraße: [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[558308,5935485]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968), [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.564997/9.880379): Schräg 5,6 oder 2?
3. Ernst-August-Stieg: [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[565216,5930676]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968), [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.520961/9.983670): 31 OSM-Plätze, Profil stark gekürzt (8,5 von 17 m).
4. Heimfelder Straße: [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[562415,5923960]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968), [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.460944/9.940084): 63 OSM-Plätze auf einer Seite.
5. Hohe Straße: [Luftbild](https://geoportal-hamburg.de/?MAP/PROJECTION=EPSG:25832&MAP/CENTER=[564418,5922844]&MAP/ZOOMLEVEL=10&MAP/LAYERIDS=19968), [Panoramax](https://api.panoramax.xyz/#focus=map&map=18/53.450670/9.970025): Radweg-Band über Baumstandorten, 12 vs. 18 Bäume.
