# Redesign 2026-11 · A4 Einfache Sprache

Ziel ist Einfache Sprache (etwa Stufe B1), nicht die geregelte „Leichte Sprache“. Fachbegriffe bleiben auf Ebene 3
sichtbar, mit Erklärung aus dem Glossar. Entscheidung: `decisions.md`, Zeile E4.

## Regeln für alle Texte der Seite

1. **Kurze Sätze:** meist unter 15 Wörter, ein Gedanke je Satz.
2. **Aktiv statt Passiv:** „Das Programm prüft …“ statt „Es wird geprüft …“.
3. **Verben statt Hauptwörter:** „Autos fahren 30 statt 50“ statt „Reduktion der zulässigen Höchstgeschwindigkeit“.
4. **Jeder Fachbegriff wird beim ersten Mal erklärt oder ersetzt.** Die Ersatzwörter stehen im Glossar und sind
   verbindlich: überall dasselbe Wort, zum Beispiel immer „Ziel“, nie abwechselnd „Soll“ und „Planung“.
5. **Keine Kürzel und IDs auf Ebene 1 und 2:** GOW30, D1, C-G30-01, Kfz und DTV nur auf Ebene 3.
6. **Zahlen mit Einheit und Bezug:** „41 000 Autos am Tag“, „30,0 m nötig, 31,1 m vorhanden“, „in 62 von 100
   Gebäuden“ statt „62 % (ab 40 %)“.
7. **Erst die Antwort, dann der Grund:** Ebene 1 sagt, was ist. Ebene 2 sagt, warum und was sich ändert.
8. **Gründe dafür und dagegen getrennt:** „Warum?“ nennt nur Prüfungen, die zutreffen. „Trifft nicht zu“ steht auf
   Ebene 3. Heute stehen beide gemischt in 92 % der Steckbriefe (`01_inventory.md`).
9. **Ruhiger Ton bei Unsicherheit:** „Diese Einstufung ist unsicher … Bitte prüfen.“ Keine roten Ampeln, keine
   Warnsymbole.
10. **Ein Text, eine Stelle:** Jeder Text steht genau einmal in einer Quelle (Regeldatei, `plain_language.yaml` oder
    Glossar). Heute stehen Texte an vier Stellen, und die Ist-Aussage zum Radverkehr widerspricht sich bei 93
    Abschnitten.

**Zielwerte (Annahme, nicht genormt):** Wiener Sachtextformel ≤ 8 und Flesch-Amstad ≥ 60 für Ebene 1 und 2. Die
Formeln sind für längere Prosa gemacht. Bei Legenden und Texten unter 30 Wörtern zählen wir stattdessen Fachbegriffe und
Kürzel.

## Glossar

[`glossary.yaml`](glossary.yaml) enthält rund 90 Begriffe in fünf Gruppen: Kategorien, allgemeine Begriffe, Radverkehr,
Kreuzungen, Daten. Jeder Eintrag hat:

- **plain:** der Name in Einfacher Sprache, verbindlich
- **explain:** ein Satz Erklärung
- **level:** Auf welcher Ebene darf der Fachbegriff noch stehen? 1/2 heißt ersetzt, 3 heißt bleibt sichtbar mit
  Erklärung.
- **found:** Fundstellen aus A1.3

Die wichtigsten Ersetzungen:

| Fachbegriff | Einfache Sprache |
|---|---|
| Soll / Ist | Ziel / heute |
| SW · GOW50 · GOW30 · ETW30 · ETW_ERF | Schnellstraße · Hauptstraße mit Tempo 50 · Hauptstraße mit Tempo 30 · Wohnstraße mit Tempo 30 · Fußgängerzone oder Spielstraße |
| Soll-Kategorie | Aufgabe der Straße |
| Diskrepanz | Abweichung zwischen heute und Ziel |
| Priorität | Dringlichkeit |
| Querschnitt / Soll-Querschnitt | Aufteilung der Straße / Aufteilung im Ziel |
| Machbarkeit | Passt das Ziel in die Straße? |
| Straßenraumbreite | Breite der Straße |
| Abschnitt | Straßenstück |
| Kfz, DTV | Autoverkehr, Autos pro Tag |
| Knotenpunkt, Knotentyp | Kreuzung, Art der Kreuzung |
| Gehwegüberfahrt | durchgehender Gehweg |
| RSV · HAUPT · BASIS · ERSCHL | Radschnellweg · Radroute · Bezirksroute · übrige Wege |
| Führungsform, Mischverkehr | Art des Radwegs, Rad auf der Fahrbahn |
| Datenunsicherheit, Robustheit | Wie sicher ist das?, hängt an Annahmen |
| Schwelle, Fallback | Grenzwert, Ersatzwert |

Die Kategorienamen weichen bewusst von `plain_language.yaml` ab (heute „Stadtmagistrale“, „Stadtstraße 30“, „Quartiersstraße“,
„Aufenthaltsstraße“). „Hauptstraße/Wohnstraße mit Tempo …“ sagt Aufgabe und Tempo in einem Wort, und „Quartier“ und
„Magistrale“ sind Fachwörter der Planung. Die heutigen Namen bleiben als Synonym im Glossar (Ebene 3).

## Vorher und nachher

Gemessen mit denselben Formeln wie in A1.3 (`analysis/redesign/language_scores.py`). „vorher“ ist der Text der heutigen
Seite aus der Erfassung, „nachher“ der Vorschlag in [`analysis/redesign/language_samples.yaml`](../../analysis/redesign/language_samples.yaml).
Die Fakten sind dieselben, es kommt nichts hinzu. „–“ bei WSTF und FRE heißt: weniger als 30 Wörter in ganzen Sätzen,
die Formel ist dann nicht aussagekräftig.

<!-- table:language_scores -->
| Beispiel | Wörter vorher | nachher | WSTF vorher | nachher | FRE vorher | nachher | Ø Satzlänge vorher | nachher | Fachbegriffe/Kürzel (Liste A1.3) vorher | nachher |
|---|---|---|---|---|---|---|---|---|---|---|
| Einleitung (heute Methodenseite, oben) | 75 | 80 | 6,2 | 5,5 | 69,8 | 73,3 | 10,7 | 7,3 | 2 | 0 |
| Legende Aufgabe der Straße | 26 | 40 | – | – | – | – | 7,5 | 6,8 | 11 | 0 |
| Legende Abweichung | 43 | 31 | – | – | – | – | 6,5 | 7,3 | 7 | 0 |
| Legende Passt das Ziel? | 50 | 38 | 12,0 | 4,1 | 57,1 | 81,1 | 8,6 | 7,0 | 1 | 0 |
| Legende Radnetz | 41 | 23 | – | – | – | – | 9,7 | 7,5 | 8 | 1 |
| Legende Kreuzungen | 69 | 35 | 11,1 | – | 50,5 | – | 9,3 | 6,0 | 3 | 0 |
| Steckbrief Schnellstraße (Deckel Stellingen) | 60 | 38 | – | 4,1 | – | 74,1 | 9,7 | 6,2 | 12 | 0 |
| Steckbrief Hauptstraße mit Tempo 50 (Farnhornstieg) | 143 | 81 | 7,8 | 2,7 | 56,2 | 79,3 | 8,3 | 8,4 | 20 | 0 |
| Steckbrief Hauptstraße mit Tempo 30 (Kieler Straße) | 160 | 70 | 8,5 | 2,7 | 61,6 | 84,0 | 8,0 | 7,4 | 20 | 0 |
| Steckbrief Wohnstraße mit Tempo 30 (Schippelsweg) | 145 | 70 | 11,2 | 2,1 | 44,1 | 83,9 | 7,1 | 7,5 | 19 | 0 |
| Steckbrief Fußgängerzone oder Spielstraße (Alte Elbgaustraße) | 63 | 35 | – | – | – | – | 6,5 | 6,8 | 10 | 0 |
| Steckbrief Kreuzung (Altonaer Straße / Max-Brauer-Allee / Schulterblatt) | 66 | 71 | 5,6 | 4,6 | 60,0 | 69,8 | 8,8 | 8,1 | 13 | 0 |
| Methode – Zusammenfassung (neu; vorher Einleitung und „Grenzen“) | 136 | 111 | 7,9 | 2,3 | 61,9 | 84,3 | 9,1 | 7,5 | 4 | 1 |
| Methode – Kapitel „Wie die Aufgabe entsteht“ | 187 | 135 | 7,0 | 4,9 | 56,4 | 73,4 | 9,8 | 7,4 | 10 | 2 |
| Methode – Kapitel „Wie sicher ist das?“ | 115 | 113 | 10,5 | 5,4 | 48,8 | 71,9 | 13,4 | 7,4 | 6 | 1 |
| **alle Beispiele zusammen** | 1379 | 971 | 9,2 | 3,7 | 54,1 | 77,9 | 9,0 | 7,4 | – | – |
<!-- /table:language_scores -->

Die verbliebenen Treffer nachher sind Glossarbegriffe, die auf Ebene 1/2 erlaubt sind: Bezirksroute, OpenStreetMap,
Verbindungswert, Steckbrief. „Ist“ im Kapitel zur Aufgabe ist das Fragewort („Ist die Straße …?“), ein Fehltreffer der
Zählung.

Alle Beispiele zusammen:

- **Wiener Sachtextformel:** von 9,2 auf 3,7. Das ist ungefähr die Lesestufe einer Zeitung für Kinder statt Klasse 9.
- **Flesch-Amstad:** von 54,1 auf 77,9.
- **Sätze über 15 Wörter:** von 6 % auf 0.
- **Passiv:** von 5 % auf 0.
- **Lange Substantive:** von 6,5 % auf 1,2 %.
- **Kategorie-Kürzel und Regel-IDs:** keine mehr.
- **Wörter:** 30 % weniger (1 379 → 971), bei gleichem Inhalt.

### Die Texte im Einzelnen

<!-- table:language_samples -->
#### Einleitung (heute Methodenseite, oben)

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Dieser Entwurf ordnet jeder Straße in Hamburg (7 Bezirke) eine Aufgabe zu: Soll sie Verkehr verbinden, oder soll sie ein Quartier erschließen? Daraus folgt, wie schnell gefahren werden soll und wie die Straße gestaltet sein sollte. Die Idee kommt aus den Niederlanden und heißt „Duurzaam Veilig“ (nachhaltig sicher).<br>Wichtig: Das ist ein Vorschlag zur Diskussion. Die Stadt Hamburg hat ihn nicht beschlossen. Ein Computerprogramm macht den ersten Vorschlag. Menschen prüfen ihn und korrigieren ihn, wenn nötig.

</td><td>

Dieser Entwurf schlägt für jede Straße in Hamburg eine Aufgabe vor.<br>Manche Straßen sollen Stadtteile verbinden. Andere führen nur zu den Häusern im Viertel.<br>Aus der Aufgabe folgt, wie schnell Autos fahren sollen. Sie zeigt auch, wie die Straße aussehen sollte.<br>Die Idee kommt aus den Niederlanden. Dort heißt sie „nachhaltig sicher“.<br>Wichtig: Das ist ein Vorschlag zur Diskussion. Die Stadt Hamburg hat ihn nicht beschlossen.<br>Ein Computerprogramm macht den ersten Vorschlag. Fachleute prüfen ihn und korrigieren ihn, wo nötig.

</td></tr></table>

Fachbegriffe und Kürzel vorher: Duurzaam Veilig, Soll. Nachher: –.

#### Legende Aufgabe der Straße

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Welche Funktion die Straße nach Duurzaam Veilig haben soll (Vorschlag).<br>SW – Schnellverkehrsstraße<br>GOW50 – Stadtmagistrale<br>GOW30 – Stadtstraße 30<br>ETW30 – Quartiersstraße<br>ETW_ERF – Aufenthaltsstraße<br>außerorts – nicht bewertet (ländliche Stadtteile)

</td><td>

Welche Aufgabe jede Straße haben soll. Die Farbe zeigt das Tempo im Ziel. Die Breite zeigt, wie stark die Straße verbindet.<br>Schnellstraße<br>Hauptstraße mit Tempo 50<br>Hauptstraße mit Tempo 30<br>Wohnstraße mit Tempo 30<br>Fußgängerzone oder Spielstraße<br>Grau: auf dem Land, nicht bewertet

</td></tr></table>

Fachbegriffe und Kürzel vorher: SW, GOW50, GOW30, ETW30, ETW_ERF, Duurzaam Veilig, Stadtmagistrale, Stadtstraße 30, Quartiersstraße, Aufenthaltsstraße, Schnellverkehrsstraße. Nachher: –.

#### Legende Abweichung

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Wo heutiges Tempo, Gestaltung oder Verkehrsmenge nicht zur Soll-Kategorie passen. Breitere Linie = stärkere Diskrepanz.<br>D1 – Erschließungsfunktion, aber Durchfluss-Gestaltung<br>D2 – Verbindungsfunktion, sparsame Gestaltung (z. B. Radverkehr auf Fahrbahn bei 50)<br>D3 – Mischform mit Merkmalen beider Kategorien<br>keine Diskrepanz<br>nicht prüfbar<br>außerorts – nicht bewertet (ländliche Stadtteile)

</td><td>

Wo die Straße heute nicht zu ihrer Aufgabe passt. Zum Beispiel ist das Tempo zu hoch. Eine breite Linie heißt: große Abweichung.<br>große Abweichung<br>kleine Abweichung<br>passt zum Ziel<br>nicht prüfbar

</td></tr></table>

Fachbegriffe und Kürzel vorher: Diskrepanz, Soll, Soll-Kategorie, Verbindungsfunktion, D1, D2, D3. Nachher: –.

#### Legende Passt das Ziel?

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Passen Gehwege, Radanlage, Fahrbahn, Bäume und Parken des Soll-Querschnitts in den Straßenraum?<br>passt in den Straßenraum<br>passt nach Abstrichen<br>passt nicht in den Straßenraum<br>nicht bewertet (keine Breite oder kein Soll-Profil)<br>außerorts – nicht bewertet (ländliche Stadtteile)<br>Radnetz, Radanlagen, Querschnitte und Knotenpunkte sind ein nicht amtlicher Entwurf – nicht das Radnetz Hamburg

</td><td>

Passt das Ziel in die Straße? Wir prüfen Gehwege, Radweg, Fahrbahn, Bäume und Parken.<br>passt<br>passt mit Abstrichen, zum Beispiel weniger Parkplätze<br>passt nicht<br>nicht prüfbar, weil die Breite fehlt<br>Das ist ein Entwurf, keine Planung der Stadt.

</td></tr></table>

Fachbegriffe und Kürzel vorher: Soll. Nachher: –.

#### Legende Radnetz

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Vorgeschlagenes Radnetz in vier Ebenen: Radvorrangroute, Radroute, Bezirksroute und Quartiersnetz.<br>RSV – Radvorrangroute / Radroute+<br>HAUPT – Radroute (Hauptnetz)<br>BASIS – Bezirksroute (Basisnetz)<br>ERSCHL – Quartiersnetz (Erschließung)<br>außerorts – nicht bewertet (ländliche Stadtteile)<br>Radnetz, Radanlagen, Querschnitte und Knotenpunkte sind ein nicht amtlicher Entwurf – nicht das Radnetz Hamburg

</td><td>

Das vorgeschlagene Radnetz. Eine breite Linie heißt: wichtige Route.<br>Radschnellweg<br>Radroute<br>Bezirksroute<br>übrige Wege<br>Das ist ein Entwurf, nicht das Radnetz der Stadt.

</td></tr></table>

Fachbegriffe und Kürzel vorher: RSV, HAUPT, BASIS, ERSCHL, Radvorrangroute, Bezirksroute, Quartiersnetz, Erschließung. Nachher: Bezirksroute.

#### Legende Kreuzungen

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Vorgeschlagener Knotentyp; Form und Farbe zeigen den Typ, größere Zeichen: Umbau nötig. Sichtbar ab Zoomstufe 12.<br>Kreisverkehr<br>Ampel<br>Vorfahrt mit Aufpflasterung, Furt oder Querung mit Mittelinsel<br>durchgehender Gehweg<br>rechts vor links<br>Brücke oder Tunnel<br>kein Soll-Typ (Autobahnknoten oder keine Regel passt)<br>außerorts – nicht bewertet (ländliche Stadtteile)<br>Radnetz, Radanlagen, Querschnitte und Knotenpunkte sind ein nicht amtlicher Entwurf – nicht das Radnetz Hamburg<br>Größere Zeichen: heutiger Knoten passt nicht zum Soll (Umbau nötig).

</td><td>

Welche Art Kreuzung das Ziel ist. Die Form zeigt die Art. Orange heißt: Hier ist ein Umbau nötig.<br>Kreisverkehr<br>Ampel<br>Vorfahrt mit erhöhter Fahrbahn<br>durchgehender Gehweg<br>rechts vor links<br>Brücke oder Tunnel<br>kein Ziel festgelegt

</td></tr></table>

Fachbegriffe und Kürzel vorher: Soll, Furt, Knotentyp. Nachher: –.

#### Steckbrief Schnellstraße (Deckel Stellingen)

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Soll-Kategorie<br>Schnellverkehrsstraße (SW)<br>Schnellverkehrsstraße – anbaufrei, nur für Kraftfahrzeuge; Fuß- und Radverkehr getrennt geführt<br>Begründung<br>Autobahn oder Kraftfahrstraße nur für Kraftfahrzeuge (OSM highway=motorway) (C-SW-01)<br>Ist-Zustand<br>Tempo<br>80 km/h (OpenStreetMap)<br>Radverkehr<br>baulicher Radweg<br>Busfahrten je Werktag<br>0<br>Verkehrsmenge<br>131.000 Kfz/Tag (2019)<br>Hauptverkehrsstraße<br>nein<br>Radnetz<br>nein<br>Querschnitt<br>Straßenraum (Median)<br>51,6 m<br>Straßenraum an Engstellen<br>50,3 m<br>Soll-Querschnitt<br>Kein Soll-Profil (Straßenkategorie ohne Profilregeln oder Breite nicht gemessen).

</td><td>

Schnellstraße. Ohne Tempo-Ziel.<br>Warum? Die Straße ist eine Autobahn. Hier fahren nur Autos und Lastwagen.<br>Was ändert sich? Für die Aufgabe ist kein Umbau nötig. Fuß- und Radverkehr haben eigene Wege daneben.<br>Heute fahren hier 131 000 Autos am Tag.

</td></tr></table>

Fachbegriffe und Kürzel vorher: SW, Soll, Ist, Soll-Kategorie, Querschnitt, Soll-Querschnitt, Kfz, Schnellverkehrsstraße, OSM, OpenStreetMap, anbaufrei, C-SW-01. Nachher: –.

#### Steckbrief Hauptstraße mit Tempo 50 (Farnhornstieg)

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Soll-Kategorie<br>Stadtmagistrale (GOW50)<br>Stadtmagistrale – verbindet Stadtteile, Tempo 50, Radverkehr auf baulich getrenntem Radweg<br>Begründung<br>Hauptverkehrsstraße der BVM; hohe Verbindungsfunktion: Verbindungswert 0,89 (ab 0,87) (C-GOW-01)<br>keine Schule oder Kita direkt an der Straße und wenig Publikumsverkehr (C-G30-01)<br>Platz für einen baulichen Radweg neben der Busfahrbahn: Straßenraum 31,1 m (nötig 17,5 m) (C-G30-02)<br>kein Grund für Tempo 30 auf dieser Verbindungsstraße gefunden (C-G50-01)<br>Ist-Zustand<br>Tempo<br>50 km/h (amtlich (Zulässige Höchstgeschwindigkeiten))<br>Radverkehr<br>baulicher Radweg<br>Busfahrten je Werktag<br>591<br>Verkehrsmenge<br>29.000 Kfz/Tag (2019)<br>Hauptverkehrsstraße<br>ja<br>Radnetz<br>nein<br>Querschnitt<br>Straßenraum (Median)<br>32,0 m<br>Straßenraum an Engstellen<br>31,1 m<br>nötig für die Soll-Kategorie<br>17,0 m<br>Machbarkeit<br>passt<br>vorhanden 31,1 m (Engstelle)<br>nötig 17,0 m<br>Soll-Querschnitt<br>passt in den Straßenraum – Bedarf 30,0 m, verfügbar 31,1 m.<br>Gehweg 3,0<br>Radweg 2,5<br>Trennstreifen 0,8<br>Baumstreifen 2,0<br>Bus 3,5<br>Fahrbahn 6,5<br>Bus 3,5<br>Baumstreifen 2,0<br>Trennstreifen 0,8<br>Radweg 2,5<br>Gehweg 3,0<br>Soll-Bedarf 30,0 m<br>verfügbar 31,1 m (Verkehrsfläche an Engstellen)<br>Fünf Prinzipien, Punkte von 100 (Radroute HAUPT an diesem Abschnitt)<br>Prinzip	heute	nach Umbau (Soll)<br>Zusammenhang	74	75<br>Direktheit	75	75<br>Sicherheit	69	86<br>Komfort	0	100<br>Attraktivität	48	48<br>gesamt (gewichtet)	59	79

</td><td>

Hauptstraße mit Tempo 50. Tempo 50, wie heute.<br>Warum? Die Straße verbindet Stadtteile. Sie steht auf der Liste der Hauptverkehrsstraßen.<br>Für Tempo 30 gibt es keinen Grund. Keine Schule liegt direkt an der Straße. Es gibt genug Platz für einen eigenen Radweg.<br>Was ändert sich? Heute gibt es mehrere Fahrstreifen je Richtung ohne Trennung in der Mitte.<br>Im Ziel hat jede Richtung einen Fahrstreifen und eine Busspur. Auf beiden Seiten gibt es einen eigenen Radweg.<br>Das passt in die Straße: 30,0 m nötig, 31,1 m vorhanden.

</td></tr></table>

Fachbegriffe und Kürzel vorher: GOW, GOW50, Soll, Ist, Soll-Kategorie, Querschnitt, Soll-Querschnitt, Machbarkeit, Kfz, BVM, HAUPT, Verbindungswert, Stadtmagistrale, Verkehrsfläche, Engstelle, Verbindungsfunktion, C-GOW-01, C-G30-01, C-G30-02, C-G50-01. Nachher: –.

#### Steckbrief Hauptstraße mit Tempo 30 (Kieler Straße)

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Soll-Kategorie<br>Stadtstraße 30 (GOW30)<br>Stadtstraße 30 – verbindet Quartiere, Tempo 30, Radverkehr auf Radfahrstreifen, bei viel Kfz-Verkehr auf baulichem Radweg<br>Begründung<br>Hauptverkehrsstraße der BVM (C-GOW-01)<br>viele Gebäude mit Läden oder Publikumsverkehr: 62 % (ab 40 %) (C-G30-01)<br>Platz für einen baulichen Radweg neben der Busfahrbahn: Straßenraum 29,3 m (nötig 17,5 m) (C-G30-02)<br>Ist-Zustand<br>Tempo<br>50 km/h (amtlich (Zulässige Höchstgeschwindigkeiten))<br>Radverkehr<br>baulicher Radweg<br>Busfahrten je Werktag<br>207<br>Verkehrsmenge<br>41.000 Kfz/Tag (2019)<br>Hauptverkehrsstraße<br>ja<br>Radnetz<br>nein<br>Querschnitt<br>Straßenraum (Median)<br>30,0 m<br>Straßenraum an Engstellen<br>29,3 m<br>nötig für die Soll-Kategorie<br>10,8 m<br>Machbarkeit<br>passt<br>vorhanden 29,3 m (Engstelle)<br>nötig 10,8 m<br>Soll-Querschnitt<br>passt in den Straßenraum – Bedarf 24,8 m, verfügbar 29,3 m.<br>Gehweg 3,0<br>Radweg 2,5<br>Trennstreifen 0,8<br>Baumstreifen 2,0<br>Fahrbahn 5,8<br>Ladezone 2,5<br>Baumstreifen 2,0<br>Trennstreifen 0,8<br>Radweg 2,5<br>Gehweg 3,0<br>Soll-Bedarf 24,8 m<br>verfügbar 29,3 m (Verkehrsfläche an Engstellen)<br>Hinweise<br>viel Kfz-Verkehr für Tempo 30 – Radweg statt Radfahrstreifen<br>heutige Breite in OpenStreetMap nicht erfasst<br>mehr Kfz-Verkehr als ein Fahrstreifen je Richtung trägt – Verkehrsmenge senken<br>Kfz-Menge über dem breiten Profil für Tempo 30<br>Fünf Prinzipien, Punkte von 100 (Radroute HAUPT an diesem Abschnitt)<br>Prinzip	heute	nach Umbau (Soll)<br>Zusammenhang	75	72<br>Direktheit	78	78<br>Sicherheit	86	86<br>Komfort	0	100<br>Attraktivität	7	7<br>gesamt (gewichtet)	61	76

</td><td>

Hauptstraße mit Tempo 30. Heute 50 km/h, Ziel 30 km/h.<br>Warum? Die Straße verbindet Stadtteile. In vielen Häusern sind Läden: in 62 von 100 Gebäuden. Darum soll Tempo 30 gelten.<br>Was ändert sich? Autos fahren 30 statt 50. Den eigenen Radweg auf beiden Seiten gibt es weiter.<br>Das passt in die Straße: 24,8 m nötig, 29,3 m vorhanden.<br>Hinweis: Hier fahren 41 000 Autos am Tag. Das ist mehr, als ein Fahrstreifen je Richtung schafft. Der Autoverkehr müsste weniger werden.

</td></tr></table>

Fachbegriffe und Kürzel vorher: GOW, GOW30, Soll, Ist, Soll-Kategorie, Querschnitt, Soll-Querschnitt, Machbarkeit, Kfz, BVM, HAUPT, Radfahrstreifen, Stadtstraße 30, OpenStreetMap, Verkehrsfläche, Engstelle, Ladezone, C-GOW-01, C-G30-01, C-G30-02. Nachher: –.

#### Steckbrief Wohnstraße mit Tempo 30 (Schippelsweg)

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Soll-Kategorie<br>Quartiersstraße (ETW30)<br>Quartiersstraße – erschließt das Quartier, Tempo 30, Radverkehr gemeinsam mit dem Kfz-Verkehr<br>Begründung<br>geringe Verbindungsfunktion: Verbindungswert 0,33 (unter 0,87), keine Hauptverkehrsstraße (C-GOW-01)<br>darum Quartiersstraße: Die Straße erschließt das Quartier (C-ETW-01)<br>Ist-Zustand<br>Tempo<br>30 km/h (amtlich (Zulässige Höchstgeschwindigkeiten))<br>Radverkehr<br>keine Radverkehrsanlage (Radverkehr auf der Fahrbahn)<br>Busfahrten je Werktag<br>0<br>Verkehrsmenge<br>nur auf Hauptverkehrsstraßen erfasst<br>Hauptverkehrsstraße<br>nein<br>Radnetz<br>nein<br>Querschnitt<br>Straßenraum (Median)<br>12,0 m<br>Straßenraum an Engstellen<br>12,0 m<br>nötig für die Soll-Kategorie<br>9,8 m<br>Machbarkeit<br>passt<br>vorhanden 12,0 m (Engstelle)<br>nötig 9,8 m<br>Soll-Querschnitt<br>passt nach Abstrichen – Bedarf 10,8 m, verfügbar 12,0 m.<br>Gehweg 3,0<br>Fahrbahn 4,8<br>Gehweg 3,0<br>Soll-Bedarf 10,8 m<br>verfügbar 12,0 m (Verkehrsfläche an Engstellen)<br>Damit es passt, schlägt der Entwurf vor:<br>Parken entfernen (Ladezonen behalten, wenn Geschäftsnutzung) (D1)<br>Hinweise<br>Kfz-Menge nicht gezählt – Bedingung vorläufig als erfüllt angenommen<br>Kfz-Menge nicht gezählt, aber Durchgangsverkehr wahrscheinlich – Filter prüfen<br>Fünf Prinzipien, Punkte von 100 (Radroute HAUPT an diesem Abschnitt)<br>Prinzip	heute	nach Umbau (Soll)<br>Zusammenhang	47	67<br>Direktheit	30	30<br>Sicherheit	55	72<br>Komfort	100	100<br>Attraktivität	50	50<br>gesamt (gewichtet)	53	62

</td><td>

Wohnstraße mit Tempo 30. Tempo 30, wie heute.<br>Warum? Die Straße führt vor allem zu den Häusern im Viertel. Für Wege quer durch die Stadt ist sie nicht wichtig.<br>Was ändert sich? Räder fahren wie heute auf der Fahrbahn. Für Gehwege von 3 m Breite fallen Parkplätze weg.<br>Dann passt es: 10,8 m nötig, 12,0 m vorhanden.<br>Hinweis: Wahrscheinlich fahren hier Autos durch. Eine Sperre für den Durchgangsverkehr könnte helfen. Das ist noch zu prüfen.

</td></tr></table>

Fachbegriffe und Kürzel vorher: GOW, ETW, ETW30, Soll, Ist, Soll-Kategorie, Querschnitt, Soll-Querschnitt, Machbarkeit, Kfz, HAUPT, Verbindungswert, Quartiersstraße, Verkehrsfläche, Engstelle, Verbindungsfunktion, C-GOW-01, C-ETW-01, D1. Nachher: –.

#### Steckbrief Fußgängerzone oder Spielstraße (Alte Elbgaustraße)

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Soll-Kategorie<br>Aufenthaltsstraße (ETW_ERF)<br>Aufenthaltsstraße – Schrittgeschwindigkeit, Aufenthalt und Fußverkehr haben Vorrang<br>Begründung<br>heute Fußgängerzone (C-ERF-01)<br>Ist-Zustand<br>Tempo<br>unbekannt<br>Radverkehr<br>keine Radverkehrsanlage (Radverkehr auf der Fahrbahn)<br>Busfahrten je Werktag<br>0<br>Verkehrsmenge<br>nur auf Hauptverkehrsstraßen erfasst<br>Hauptverkehrsstraße<br>nein<br>Radnetz<br>nein<br>Querschnitt<br>Straßenraum (Median)<br>18,2 m<br>Straßenraum an Engstellen<br>18,0 m<br>Soll-Querschnitt<br>passt in den Straßenraum – Bedarf 7,3 m, verfügbar 18,0 m.<br>Mischfläche 4,8<br>Ladezone 2,5<br>Soll-Bedarf 7,3 m<br>verfügbar 18,0 m (Verkehrsfläche an Engstellen)

</td><td>

Fußgängerzone oder Spielstraße. Schritttempo.<br>Warum? Die Straße ist heute schon eine Fußgängerzone. Hier haben Menschen zu Fuß Vorrang.<br>Was ändert sich? Für die Aufgabe ist kein Umbau nötig. Platz ist genug: 7,3 m nötig, 18,0 m vorhanden.

</td></tr></table>

Fachbegriffe und Kürzel vorher: ETW_ERF, Soll, Ist, Soll-Kategorie, Querschnitt, Soll-Querschnitt, Aufenthaltsstraße, Verkehrsfläche, Ladezone, C-ERF-01. Nachher: –.

#### Steckbrief Kreuzung (Altonaer Straße / Max-Brauer-Allee / Schulterblatt)

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Soll-Knotentyp<br>durchgehender Gehweg (Gehwegüberfahrt)<br>Regel J-05 (Kategoriepaar GOW30+ETW30) ergibt hier: durchgehender Gehweg (Gehwegüberfahrt).<br>Zufluss Kfz<br>15.000 Kfz/Tag (geschätzt)<br>Platz<br>Kreis mit 30,3 m Radius in der Verkehrsfläche<br>Heute<br>Ist-Knotentyp (OpenStreetMap)<br>Ampel<br>Vergleich<br>Umbau nötig<br>Priorität<br>Rang 3 unter den Knoten mit Umbaubedarf<br>Unfälle mit Radbeteiligung<br>14, davon 1 mit Getöteten/Schwerverletzten (5 Jahre, Summe)<br>Radverkehrsführung<br>Mittelinsel für die Querung der Hauptstraße durch die Radroute (≥ 4,00 m RSV, ≥ 3,00 m HAUPT, ≥ 2,50 m BASIS).

</td><td>

Durchgehender Gehweg. Heute: Ampel. Ein Umbau ist nötig.<br>Was ist hier? Max-Brauer-Allee und Altonaer Straße sind Hauptstraßen mit Tempo 30. Das Schulterblatt ist eine Wohnstraße und mündet hier ein.<br>Heute regelt eine Ampel die Kreuzung.<br>Was ändert sich? Im Ziel läuft der Gehweg über die Einmündung durch. Autos fahren langsam darüber und lassen Fußgänger vor.<br>Für Radfahrende gibt es eine Insel in der Mitte der Hauptstraße. Dort können sie beim Queren warten.

</td></tr></table>

Fachbegriffe und Kürzel vorher: GOW30, ETW30, Soll, Ist, Kfz, RSV, HAUPT, BASIS, Gehwegüberfahrt, Priorität, OpenStreetMap, Verkehrsfläche, J-05. Nachher: –.

#### Methode – Zusammenfassung (neu; vorher Einleitung und „Grenzen“)

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Dieser Entwurf ordnet jeder Straße in Hamburg (7 Bezirke) eine Aufgabe zu: Soll sie Verkehr verbinden, oder soll sie ein Quartier erschließen? Daraus folgt, wie schnell gefahren werden soll und wie die Straße gestaltet sein sollte. Die Idee kommt aus den Niederlanden und heißt „Duurzaam Veilig“ (nachhaltig sicher).<br>Wichtig: Das ist ein Vorschlag zur Diskussion. Die Stadt Hamburg hat ihn nicht beschlossen. Ein Computerprogramm macht den ersten Vorschlag. Menschen prüfen ihn und korrigieren ihn, wenn nötig.<br>Viele Gestaltungsmerkmale stammen aus OpenStreetMap und fehlen dort oft. Fehlende Angaben zählen als „unbekannt“.<br>Verkehrsmengen gibt es nur für Hauptverkehrsstraßen und nur bis 2019.<br>Unfälle: nur polizeilich erfasste Unfälle mit Personenschaden. Wir zeigen nur Summen je Abschnitt.<br>Die Straßenraumbreite ist aus Katasterdaten geschätzt, nicht vor Ort gemessen.<br>Gewichte und viele Schwellen sind Annahmen. Sie sind im Regelwerk gekennzeichnet und werden fachlich geprüft.

</td><td>

Was ist das? Ein Vorschlag, welche Aufgabe jede Straße in Hamburg hat. Er zeigt auch, was sich dafür ändern müsste.<br>Ein Programm macht den Vorschlag nach festen Regeln. Fachleute prüfen ihn.<br>Was zeigt es? Für jede Straße die Aufgabe und das Tempo im Ziel. Wo die Straße heute nicht dazu passt. Ob das Ziel in die Straße passt.<br>Dazu kommen ein Radnetz und die Art jeder Kreuzung.<br>Was zeigt es nicht? Es ist keine Planung der Stadt. Niemand hat vor Ort gemessen.<br>Viele Angaben stammen aus OpenStreetMap. Dort fehlen manche Angaben.<br>Die Zahl der Autos kennen wir nur für Hauptstraßen, Stand 2019.<br>Viele Grenzwerte sind Annahmen. Wir kennzeichnen sie und prüfen sie.

</td></tr></table>

Fachbegriffe und Kürzel vorher: Duurzaam Veilig, Soll, Straßenraumbreite, OpenStreetMap. Nachher: OpenStreetMap.

#### Methode – Kapitel „Wie die Aufgabe entsteht“

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Ist die Straße eine Autobahn oder Kraftfahrstraße? Dann ist sie eine Schnellverkehrsstraße.<br>Ist sie heute schon ein verkehrsberuhigter Bereich oder eine Fußgängerzone? Dann ist sie eine Aufenthaltsstraße.<br>Verbindet sie wichtige Orte (hoher Verbindungswert oder Hauptverkehrsstraße)? Dann ist sie eine Verbindungsstraße.<br>Liegt eine Schule oder Kita direkt an der Straße, oder gibt es viele Läden? Oder ist kein Platz für einen ausreichend breiten eigenen Radweg? Dann soll dort Tempo 30 gelten: Stadtstraße 30.<br>Sonst bleibt sie eine Stadtmagistrale mit Tempo 50 und eigenem Radweg.<br>Alle anderen Straßen erschließen das Quartier: Quartiersstraße mit Tempo 30.<br>Danach wird jeder Straßenzug geglättet: Kurze Stücke unter 200 m, die anders eingestuft sind als die Straße davor und dahinter, werden angeglichen. Treffen Tempo 50 und Tempo 30 aufeinander, gewinnt Tempo 30. So wechselt die Kategorie nicht alle paar Meter. Liegt zwischen zwei Tempo-30-Stücken nur ein kurzes Stück Tempo 50, wird die Lücke geschlossen.<br>Eingestuft werden Straßen für den Kfz-Verkehr und benannte Zufahrten. Fußwege, Wege in Parks und Kleingärten sowie Parkplatzgassen haben keine Kategorie, auch wenn die Hintergrundkarte ihren Namen zeigt.<br>Jeder Steckbrief zeigt, welche Regeln gegriffen haben und mit welchen Werten. Die Regeln und alle Schwellenwerte stehen im Regelwerk (rules.yaml).

</td><td>

Das Programm prüft jede Straße in fünf Schritten. Die erste Antwort mit Ja entscheidet.<br>1. Ist die Straße eine Autobahn? Dann ist sie eine Schnellstraße.<br>2. Ist sie heute eine Fußgängerzone oder Spielstraße? Dann bleibt sie das.<br>3. Verbindet sie Stadtteile? Das gilt, wenn sie auf der Liste der Hauptverkehrsstraßen steht. Es gilt auch, wenn ihr Verbindungswert hoch ist. Dann ist sie eine Hauptstraße.<br>4. Liegt an dieser Hauptstraße eine Schule oder Kita? Gibt es viele Läden? Fehlt Platz für einen eigenen Radweg? Dann gilt Tempo 30. Sonst gilt Tempo 50.<br>5. Alle anderen Straßen sind Wohnstraßen mit Tempo 30.<br>Danach gleicht das Programm kurze Stücke an. Ein Stück unter 200 m bekommt die Aufgabe der Straße davor und dahinter.<br>Treffen Tempo 50 und Tempo 30 aufeinander, gilt Tempo 30. So wechselt die Aufgabe nicht alle paar Meter.<br>Fußwege, Wege in Parks und Parkplätze bekommen keine Aufgabe.

</td></tr></table>

Fachbegriffe und Kürzel vorher: Ist, Kfz, Verbindungswert, Stadtmagistrale, Stadtstraße 30, Quartiersstraße, Aufenthaltsstraße, Schnellverkehrsstraße, Steckbrief, Straßenzug. Nachher: Ist, Verbindungswert.

#### Methode – Kapitel „Wie sicher ist das?“

<table><tr><th>vorher (heutige Seite)</th><th>nachher (Vorschlag)</th></tr><tr><td>

Zwei Hinweise im Steckbrief helfen beim Einordnen. Die Datenunsicherheit (Ampel) zeigt, ob entscheidende Werte fehlen, aus einer Ersatzquelle stammen oder nahe an einer Schwelle liegen. Die Robustheit zeigt, wie stark die Kategorie an gesetzten Annahmen hängt: Wir rechnen den Entwurf 500-mal mit zufällig veränderten Schwellen und Gewichten (jeweils bis zu 20 % mehr oder weniger). Wechselt die Kategorie in mindestens 30 % der Läufe, ist der Abschnitt als unsicher markiert und sollte fachlich geprüft werden.<br>Diese Vorbehalte gelten für alle Abschnitte gleich und senken die Ampel darum nicht:<br>Lage inner-/außerorts (keine Datenquelle, Standardwert innerorts)<br>Schulstraße (nur über Korrekturen, Standardwert nein)<br>Querungsbedarf (stillgelegt, nicht erhoben)<br>Hauptverkehrsstraße (Verkehrsmengenkarte 2019 statt HVS-Karte 2023)<br>Abstand zum Grundstück einer Schule/Kita (aus OpenStreetMap statt amtlich)

</td><td>

Zwei Dinge können ein Ergebnis unsicher machen.<br>Erstens die Daten. Manchmal fehlt ein wichtiger Wert. Oder er stammt aus einer Ersatzquelle. Oder er liegt knapp an einem Grenzwert.<br>Zweitens die Annahmen. Viele Grenzwerte hat das Projekt selbst gesetzt.<br>Darum rechnen wir den Entwurf 500-mal. Jedes Mal ändern wir die Grenzwerte zufällig um bis zu 20 Prozent.<br>Wechselt die Aufgabe einer Straße in mindestens 30 von 100 Läufen, gilt sie als unsicher.<br>Beides zusammen betrifft 7 von 100 Kilometern. Bei diesen Straßen steht im Steckbrief ein Hinweis. Fachleute sollten sie prüfen.<br>Manche Lücken gelten für alle Straßen gleich. Zum Beispiel stammen die Hauptverkehrsstraßen aus einer Karte von 2019.<br>Diese Lücken nennen wir einmal hier. Sie machen kein einzelnes Ergebnis unsicher.

</td></tr></table>

Fachbegriffe und Kürzel vorher: HVS, Robustheit, Datenunsicherheit, Schwelle, Steckbrief, OpenStreetMap. Nachher: Steckbrief.
<!-- /table:language_samples -->

## Was das für die Umsetzung heißt

- Die neuen Texte gehören in die Quellen, aus denen die Seite liest:
  - Kategorienamen und Erklärungen in `plain_language.yaml` bzw. in die neuen Felder der Regeldateien (A5)
  - Seitentexte in eine Textdatei statt in `web/src/pages.js`
- Ein Test kann die Regeln mechanisch prüfen: Ebene 1 und 2 ohne Kürzel aus der Kürzelliste, Sätze unter 20 Wörter,
  WSTF ≤ 8 für Prosa über 30 Wörter. Er läuft wie `language_scores.py` auf den exportierten Texten (Teil B, Paket 2).
