# Konzept Karteninteraktion – drei Varianten (Vorschau)

Stand: 22.11.2026, Prompt 28, Phase 1.3. Zur Entscheidung bei Haltepunkt 1.

## Vorschau ansehen

Die Varianten sind eine **klickbare Vorschau, kein fertiger Umbau**. Sie laufen auf der echten Karte mit echten Daten.
Eingeschaltet wird sie mit einem Schalter vor dem Hash; ohne Schalter sieht die Seite aus wie bisher, und der
Vorschau-Code wird nicht geladen.

```
npm --prefix web run build && npm --prefix web run preview
http://localhost:4173/?vorschau=a#karte          A – Seitenleiste
http://localhost:4173/?vorschau=b#karte          B – Karte vorn
http://localhost:4173/?vorschau=c#karte          C – Ebenen = Legende
…&ecken=rund                                     zusätzlich: runde Ecken (Test, siehe unten)
```

Code: `web/src/legend_registry.js` (gemeinsames Register, wird in Phase 2 übernommen), `web/src/preview/`
(nur Vorschau, wird in Phase 2 durch den Umbau ersetzt), drei geschützte Einhängepunkte in `web/src/main.js`.
Screenshots: `img/options/`.

## Was alle drei Varianten gemeinsam haben

| Baustein | Umsetzung in der Vorschau | Antwort auf |
| --- | --- | --- |
| **Ein Legendenregister** (`legend_registry.js`) | Jede Ansicht und jede Ebene meldet ihre Einträge: Zeichen, `label_plain`, Erklärung (Ebene 2), Methodenlink (Ebene 3), MapLibre-Layer. Neue Ebene = ein Eintrag im Register; Legende, Chips, Hervorhebung und „im Ausschnitt“ folgen von selbst. Erklärungen kommen aus dem Glossar des Exports (`meta.glossary`), fehlende stehen vorerst im Register (Phase 2: nach `config/plain_language.yaml`). | Inventur 1, 3, 6 |
| **Nur Eingeschaltetes in der Legende** | Ansicht + eingeschaltete Ebenen + Ort + „Außerdem auf der Karte“ (ländliche Gebiete, Kreuzungspunkte). Bus, Unfälle, Schulen/Kitas haben jetzt eigene Einträge. | Inventur 1, Walkthrough 4 |
| **Gedimmt, was nicht im Ausschnitt ist** (Ihre Wahl) | 150 ms nach `idle` eine Abfrage `queryRenderedFeatures` über die Legendenlayer; Einträge ohne Treffer grau mit „– nicht im Ausschnitt“ (auch für Screenreader). Gemessen 4–33 ms je Abfrage (Desktop, ungedrosselt), nie während einer Bewegung. | Frage 2 |
| **Antippen = hervorheben** | Eintrag antippen: alle anderen Linien auf 12 % Deckkraft (Screenshot `pv-a-desktop-highlight.jpg`); nochmal antippen oder Esc hebt auf. Knopf mit `aria-pressed`. | 1.3 Legende |
| **„Was heißt das?“ direkt am Eintrag** | Kleiner „?“-Knopf in der Zeile, klappt einen Satz auf (`aria-expanded`); „Mehr dazu“ je Ebene mit Methodenlink. | Inventur 3 |
| **Chips auf der Karte** | Thema/Ansicht als schwarzes Etikett, jede Ebene, der Ort, Bezirk und „Filter aktiv“ als Chip mit ✕ (ein Tipp zum Entfernen). | 1.3 Panel |
| **Höchstens 3 Ebenen gleichzeitig** | Vorschlag: ab drei Ebenen sind weitere Schalter gesperrt, mit Hinweis. Bus + Unfälle + Schulen sind heute alle Ebenen; die Grenze greift erst, wenn Quartiere/Bäume/Parken dazukommen. | 1.3 Panel |
| **Vorschau beim Überfahren (Desktop)** | Name + ein Satz (Ziel, Tempo heute bzw. Kreuzungsart, Umbau nötig) + „Klicken öffnet den Steckbrief“ (`pv-a-desktop-hover.jpg`). Klick öffnet weiter direkt den Steckbrief – kein zusätzlicher Schritt. | 1.3 Feature |
| **Vorschau beim Antippen (Mobil)** | Erster Tipp zeigt Name + Satz im Sheet mit „Steckbrief öffnen“, „Link kopieren“, „Zurück zur Legende“ (`pv-a-mobile-tap.jpg`). | 1.3 Feature, Walkthrough 6 |
| **Liste „Straßen im Kartenausschnitt“** | Tastatur-Alternative zum Klick auf die Karte: benannte Straßen (und im Thema Kreuzungen die Kreuzungen) im Ausschnitt als Knöpfe, alphabetisch, höchstens 80. | Walkthrough 5 |
| **Esc / Zurück** | Esc schließt nacheinander Tooltip, Ebenen-Panel, Vorschau, Hervorhebung, volles Sheet; Auswahl auf der Karte erzeugt einen Verlaufseintrag, „Zurück“ schließt den Steckbrief. | 1.3 Feature |
| **Bottom Sheet (Mobil, Ihre Wahl)** | Drei Höhen: Griff (Titelzeile), halb (55 % der Kartenfläche), voll (Kartenstreifen von 72 px bleibt). Das Sheet ist eine Zeile **unter** der Karte, kein Überlagern: die Karte wird kleiner, nichts liegt verdeckt darunter (behebt Walkthrough 2). Der Steckbrief ersetzt das Sheet, solange er offen ist – nie zwei Ebenen übereinander. | Frage 3, Walkthrough 2, 3 |
| **Panel nie neu aufbauen ohne Fokus** | Fokus und offene Erklärungen bleiben beim Neuzeichnen erhalten; nichts klappt von selbst zu. | Walkthrough 1 |
| **Bewegung** | Keine Animation in der Vorschau: Das Sheet springt zwischen den Höhen, weil die Karte bei jeder Größenänderung neu zeichnet (eine animierte Höhe über dem WebGL-Canvas ließ die Karte im Test leer). Kamerafahrten (`flyTo`, `fitBounds`) sind kurz und unter `prefers-reduced-motion` aus (wie heute). | 1.3 Motion |
| **Thema als Radiogruppe** | `role="radiogroup"` statt `toolbar` ohne Pfeiltasten; Vergleichsansichten (Ebene 3) als „Zum Vergleich: …“ statt als gleichrangige dritte Ansicht. | Inventur 8, 5 |

## Die drei Varianten

### A – Seitenleiste
Links eine Spalte (3 von 12) mit Thema, Ansicht, Legende, Ebenen, Liste – von oben nach unten. Am nächsten am
heutigen Aufbau, Legende immer neben der Karte. Nachteil: Ebenen stehen unter der Legende, bei langen Legenden
(Kreuzungen, Radnetz) muss man scrollen.
Bilder: `pv-a-desktop-bus.jpg`, `pv-a-desktop-highlight.jpg`, `pv-a-mobile-half.jpg`.

### B – Karte vorn
Karte über die ganze Breite. Die Legende ist eine Karte-auf-der-Karte unten links; „Thema und Ebenen“ öffnet ein
Panel rechts. Am meisten Karte, aber Legende und Panel verdecken auf 1440 px zusammen ein Drittel der Karte, und
das Steckbrief-Panel (rechts) konkurriert mit dem Ebenen-Panel.
Bilder: `pv-b-desktop-bus.jpg`, `pv-b-desktop-layers.jpg`, `pv-b-mobile-half.jpg`.

### C – Ebenen = Legende
Eine Liste: oben Thema und Ansicht mit ihrer Legende, darunter jede Ebene als Schalter – eingeschaltet klappt ihre
Legende direkt darunter auf. Wer etwas einschaltet, sieht sofort, was es bedeutet; Ausgeschaltetes taucht nicht auf.
Die wenigsten Begriffe. In der Vorschau rechts; dort deckt der Steckbrief sie zu.
Bilder: `pv-c-desktop-bus.jpg`, `pv-c-desktop-place.jpg`, `pv-c-mobile-half.jpg`.

### Empfehlung
**Aufbau von C in der Position von A (links).** C beantwortet „Legende unklar“ am direktesten: Ebene und Erklärung
stehen am selben Ort, und die Legende enthält nie etwas, das man nicht eingeschaltet hat. Links bleibt der
Steckbrief rechts frei. Mobil sind alle drei Varianten gleich (ein Sheet); dort entscheidet nur die Reihenfolge im
Sheet, und die von C ist die kürzeste.

## Runde Ecken (Test, auf Ihren Wunsch)

`&ecken=rund` an jede Vorschau-URL hängen (oder im schwarzen Vorschau-Etikett auf „runde Ecken“ klicken).
Radien auf dem 4-px-Raster: Bedienelemente 8 px, Karten und Sheet 12 px (mobil nur oben), Chips ganz rund, „?“
kreisrund. Kartendaten, Legendenzeichen und Querschnitte bleiben eckig – Rundung nur an Bedienelementen.
Bilder: `pv-*-round-*.jpg`. Das wäre eine bewusste Ausnahme von „keine Rundungen“ in
`docs/redesign/03_design_system.md`; bei Zustimmung trage ich sie dort mit Begründung ein.

## Was die Vorschau noch nicht kann (Phase 2)

- URL-Schema v2 (`docs/url_scheme.md`) – die Vorschau nutzt noch das alte Schema.
- Getippte Straße wird in der Vorschau noch nicht hervorgehoben, erst nach „Steckbrief öffnen“.
- Auswahl beim Einpassen über dem Sheet (Padding) und „Link kopieren“ im Steckbrief selbst.
- Filter (Aufgabe, Art der Abweichung, Dringlichkeit) und Bezirk sind in der Vorschau nur über Chips entfernbar,
  nicht neu einstellbar; im Umbau kommen sie als „Filter“ unter die Ebenen.
- Canvas-Label je Thema, deutsche Beschriftung der Zoomknöpfe, kompakte Quellenzeile mobil.

## Offene Entscheidungen für Haltepunkt 1

1. Variante (Empfehlung: C-Aufbau links).
2. Runde Ecken ja/nein.
3. **Mobiler Kopf:** Auf 390 px belegen Logo, Navigation und Suche ≈ 190 px – bei halbem Sheet bleibt wenig Karte
   (`pv-a-mobile-tap.jpg`). Vorschlag: auf der Kartenseite mobil ein einzeiliger Kopf (Logo, Suche als Lupe,
   Menü) – spart ≈ 110 px. Gehört zur Karteninteraktion, ändert aber den Seitenkopf.
4. Busfarbe (heute #4a4a4a, schwer von Straßenrändern zu unterscheiden): eigene Farbe?
5. Grenze von 3 Ebenen gleichzeitig.
