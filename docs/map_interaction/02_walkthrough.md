# Walkthrough der heutigen Oberfläche (vorher)

Stand: 22.11.2026, Prompt 28, Phase 1.2. Durchgeführt vom Agenten `usability-walkthrough` (sonnet) mit Playwright
gegen `vite preview` (Stand main). Modi: Desktop 1440 × 900 mit Maus, nur Tastatur, Mobil 390 × 844 mit Touch.
Jeder Schritt am DOM bzw. an der URL geprüft. Gezählt werden Nutzeraktionen; Tippen eines Suchbegriffs = 1,
jedes Tab = 1.

## Schrittzahlen

| Aufgabe | Desktop | Tastatur | Mobil |
| --- | --- | --- | --- |
| T1 Ziel-Steckbrief „Osterstraße“ | 3 | 10 (Tab ×8, Tippen, Enter) | 3 |
| T2 Bedeutung einer Linienfarbe | 0 (Legende lesen) / 5 (eine Straße prüfen) | auf der Karte **nicht möglich**; 10 über die Suche | 5 (Legende unter dem Falz) |
| T3 Busrouten an und wieder aus | 3 (+ Scrollen) | 26 an + 1 aus, danach Fokus verloren (Tab ×21 erneut) | 4 an + 1 aus, Karte dabei nicht sichtbar |
| T4 Besonderer Ort Schanze öffnen | 1 (Checkbox) bzw. 2 (über „Orte“) | 20 (Tab ×19, Leertaste) | 2, Karte zoomt außerhalb des Bildschirms |
| T5 Kreuzung heute/Ziel vergleichen (Schlump) | 3 (nur über Suche, Eintrag 2) | 11 (Tab ×8, Tippen, ↓, Enter) | 3 (+1 „Mehr erfahren“) |
| T6 Link auf einen Abschnitt teilen | 3 + Adresszeile kopieren | 10 + Strg+L, Strg+C | 3 + Teilen des Browsers |

## Sackgassen und unklare Stellen

| # | Problem | Aufgaben | Fundstelle |
| --- | --- | --- | --- |
| 1 | **Bedienbereich klappt zu, Fokus geht verloren:** Wird der letzte Filter/die letzte Ebene abgewählt, schließt sich „Mehr Ansichten und Filter“, der Fokus fällt auf `<body>`; mobil springt die Seite 439 px. | T3 | main.js:80, 128 |
| 2 | **Mobil verdeckt das Steckbrief-Panel das Ergebnis:** Der gewählte Abschnitt wird in die Kartenmitte gesetzt – genau unter das Panel (70 vh). | T1, T5 | style.css:249, main.js:357-360 |
| 3 | **Mobil liegen alle Schalter unter der Karte:** Bus oder Schanze einschalten passiert, während die Karte außerhalb des Bildschirms ist; keine sichtbare Rückmeldung. | T3, T4 | style.css:241-249 |
| 4 | **Zusatzebenen sind versteckt und unerklärt:** „Busverkehr“ steckt im zugeklappten „Mehr Ansichten und Filter“, heißt nicht „Buslinien“, hat keinen Legendeneintrag; Linien #4a4a4a auf grauer Karte schwer lesbar; Checkbox mobil 17 px. | T3 | main.js:80-86, layers.js:349, palette.js:64 |
| 5 | **Kein Tastaturweg zu einem Abschnitt auf der Karte:** Auswahl nur per Mausklick; das Canvas-Label verspricht eine „Tabellenansicht“, die es auf der Seite nicht gibt; Zoomknöpfe englisch beschriftet, ohne sichtbaren Fokus. | T2 | map.js:88, 111 |
| 6 | **Kein „Link kopieren“:** Die URL funktioniert (geprüft), aber man muss wissen, dass man die Adresszeile kopiert. | T6 | profile.js:89 |
| 7 | **Themenleiste mobil seitlich scrollend ohne Hinweis;** „Ziel/heute“ liegt bei x = 880 px. „Heute und Ziel“ ist ein Thema, „Ziel“/„heute“ sind Ansichten. | T2 | style.css:243, state.js:29 |
| 8 | **Suche: Enter wählt die Straße, nicht die Kreuzung;** geöffnet wird das erste von 18 Stücken (13 m) ohne Hinweis auf die übrigen. | T1, T5 | search.js:44, main.js:354-360 |
| 9 | Besonderer Ort per Checkbox: Karte zoomt, aber keine Beschreibung öffnet sich; „Auf der Karte zeigen“ bedeutet in Orte-Seite und Steckbrief Verschiedenes. | T4 | main.js:122 |
| 10 | Kreuzungen: Auf der Karte gibt es nur „Ziel“, keinen Vergleich mit heute; Soll-Bezeichnung ohne „Ziel:“-Präfix, „heute:“ mit. | T5 | state.js:28 |
| 11 | Desktop: Das Steckbrief-Panel verdeckt Suche, Spenden-Knopf und Zoomknöpfe. | T1 | style.css:184 |
| 12 | Intro beim ersten Besuch: Fokus bleibt auf `<body>`; „Verstanden“ setzt den Fokus in die Suche (öffnet mobil die Tastatur). | – | main.js:152 |

Außerhalb des Auftrags gefunden (nicht Darstellung, nur notiert): Der „Warum?“-Text kann der Überschrift
widersprechen („Darum Wohnstraße“ bei einer Hauptstraße, Abgleich über Nachbarn) – profile.js:11; „Parkplätze:
keine Daten. (keine Daten)“ doppelt. → docs/open_questions.md.

## Folgerungen für das Konzept

- Mobil: Karte bildschirmfüllend, alles Weitere in **einem** Bottom Sheet; Auswahl so einpassen, dass sie über
  dem Sheet liegt (Padding unten = Sheet-Höhe).
- Ebenen nicht verstecken: eigener Bereich „Ebenen“, Chips auf der Karte, jede Ebene mit Legende.
- Panel nie komplett neu aufbauen, ohne Fokus und offene Aufklapper zu erhalten.
- Tastatur: Liste „Straßen im Kartenausschnitt“ als Alternative zum Klick auf die Karte; Canvas-Label je Thema.
- „Link kopieren“ im Steckbrief und in der Vorschau.
- Suche: Kreuzungstreffer klar trennen und Enter-Verhalten prüfen (kleiner Eingriff, im Auftrag „nur
  umgestalten“ enthalten).
