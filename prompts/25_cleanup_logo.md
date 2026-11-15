# 25 – Webseite aufräumen, Karten verständlicher machen, Logo HMR einbauen

**Ziel:** hamburgmobility.de verschlanken und klarer machen: Kopfband und Changelog entfernen, einzelne Kartenansichten vorläufig ausblenden, die Legende „Abweichung“ verständlich machen, Stadtteilnamen über die Linien legen und das Logo „HMR“ (Hamburg Mobility Revolution) im Kopfbereich einbauen – weiterhin nach den Prinzipien des Swiss Web Designs.
**Ergebnis:** Branch `cleanup/2026-11` mit allen Änderungen, Vorschau-Build, Screenshots Desktop/Mobil, Bericht `docs/cleanup/2026-11/bericht.md`.
**Prüfschritt:** Ich sehe mir Vorschau und Bericht an und wähle bei Legende und Kopfbereich eine Variante. Erst nach meinem OK: Merge und Deployment auf GitHub Pages.

## Arbeitsweise

- Zuerst Planungsmodus: Zeige mir den Plan mit der Liste aller Fundstellen (Schritt 0) und der vorgesehenen Agenten-Aufteilung. Dann umsetzen.
- Arbeite auf dem Branch `cleanup/2026-11`. Kein Deployment ohne mein OK.
- Ausgeblendetes wird **nicht gelöscht**, sondern per Konfiguration abgeschaltet (z. B. `enabled: false` in der Ansichts-/Themenkonfiguration), damit es später mit einer Zeile wieder aktiviert werden kann. Daten für ausgeblendete Ansichten werden nicht geladen.
- Stabil halten: teilbare Links (URL-Parameter ausgeblendeter Ansichten leiten auf die Standardansicht der jeweiligen Karte weiter), `segment_id`/`node_id`, Barrierefreiheit (WCAG 2.2 AA), keine externen Dienste.
- Die Begriffe unten sind meine Namen für die Karten und Ansichten („Radnetz“, „Platz in der Straße“, „Heute und Ziel“, „Lücken“, „Radweg“, „Passt das Ziel“, „Fahrstreifen“, „Abweichung“). Ordne sie den tatsächlichen IDs im Code zu und nenne die Zuordnung im Plan.

## Agenten und Modelle (Kosten sparen)

Nutze Subagenten mit günstigeren Modellen für mechanische Aufgaben und behalte Urteils- und Gestaltungsfragen in der Hauptsitzung. Lege dafür bei Bedarf Agenten in `.claude/agents/` an (Frontmatter mit `name`, `description`, `tools`, `model`). Falls deine Version das so nicht unterstützt, nutze den Modellparameter beim Starten eines Subagenten.

| Agent | Modell | Aufgabe | Werkzeuge |
| --- | --- | --- | --- |
| `fundstellen-suche` | haiku | alle Verweise auf Kopfband, Changelog, betroffene Ansichten, Legenden, URL-Parameter, Texte in Methodik/Hilfe, Tests finden | nur lesen (Read, Grep, Glob) |
| `screenshot-runner` | haiku | Playwright-Screenshots Desktop 1440 px und Mobil 390 px, Zoomstufen 11/13/15, vorher und nachher | Bash |
| `asset-processor` | haiku | Logo zuschneiden und Varianten exportieren | Bash (Python/Pillow) |
| `link-und-a11y-check` | haiku | Linkprüfung, axe-core, Konsolenfehler | Bash |
| `review` | sonnet | unabhängige Prüfung des Gesamt-Diffs gegen diese Liste und gegen die Swiss-Design-Regeln, ohne die Umsetzung gesehen zu haben | nur lesen |

Unabhängige Aufgaben parallel starten. Die Hauptsitzung formuliert Legendentexte, entscheidet Layout und Kartenstil und fasst zusammen. Nenne im Bericht, welcher Agent was erledigt hat.

## Schritt 0 – Fundstellen und Auswirkungen (Agent `fundstellen-suche`)

Liste für jede Änderung 1–8 alle betroffenen Stellen: Komponenten, Konfiguration, Texte (inkl. Methodikseite, Hilfe, Glossar, Steckbriefe), Exporte, Tests, `CLAUDE.md` und Leitlinien in `docs/`, die eine Änderung festschreiben (z. B. eine Regel „dauerhafter Entwurfshinweis“ oder „Was ist neu anzeigen“). Ergebnis: `docs/cleanup/2026-11/fundstellen.md`. **Alle Fundstellen werden mit angepasst**, damit nichts auf Entferntes verweist und spätere Prompts es nicht wieder einbauen.

## Änderungen

1. **Kopfband „Entwurf …“ entfernen.**
   - Das Band oben auf allen Seiten entfällt.
   - Die Kennzeichnung als unabhängiges, nicht amtliches Projekt bleibt unaufdringlich erhalten: durch den Titelzusatz „Entwurf“ und eine Zeile in der Fußzeile sowie auf der Methodik-/Über-Seite.
   - Passe `CLAUDE.md` und Leitlinien an, die das Band vorschreiben.
2. **Changelog nicht mehr anzeigen.**
   - Seite, Menüpunkt und Verweise auf „Was ist neu“/Changelog von der Webseite entfernen.
   - `CHANGELOG.md` im Repository bleibt bestehen; Versionsnummer und Datenstand dürfen unauffällig in der Fußzeile stehen.
   - Leitlinien anpassen, die einen Changelog-Eintrag auf der Webseite verlangen.
3. **Radnetzkarten: Ansichten „Lücken“ und „Radweg“ vorläufig ausblenden.** Per Konfiguration abschalten; Umschalter, Legenden und Texte, die darauf verweisen, anpassen.
4. **„Platz in der Straße“: nur noch die Ansicht „Fahrstreifen“.**
   - Die Ansicht „Passt das Ziel“ ausblenden, weil sie verwirrt.
   - Hat die Karte danach nur eine Ansicht, entfällt der Umschalter.
   - Titel, Erklärtext und Legende auf „Fahrstreifen“ zuschneiden.
   - Steckbriefe, die auf „Passt das Ziel“ verweisen, anpassen; die Information zur Machbarkeit darf im Steckbrief auf Detailebene bleiben, sofern sie dort verständlich erklärt ist.
5. **„Heute und Ziel“: Legende der Ansicht „Abweichung“ verständlich machen.**
   - Analysiere zuerst, was die Ansicht genau zeigt (Datenfelder, Klassen, Farben).
   - Erstelle zwei Varianten in einfacher Sprache, z. B.:
     - (a) Klassen als kurze Aussagen („Heute schneller als geplant“, „Gestaltung passt nicht zur Funktion“, „passt bereits“);
     - (b) eine Frage als Überschrift („Wie weit ist die Straße heute vom Ziel entfernt?“) mit einer Skala von „passt“ bis „große Abweichung“ und einem Satz Erklärung.
   - Je Variante: höchstens eine Zeile pro Klasse, Farben mit zusätzlicher Kodierung (Linienstil oder -breite) für Farbsehschwäche, ein Link „Was heißt das?“ auf die Erklärung.
   - Prüfe, ob die Klassen zu fein sind, und schlage bei Bedarf eine Zusammenfassung vor (nur Darstellung, keine Änderung an Regeln oder Daten).
6. **Stadtteilnamen sichtbar machen.**
   - Ursache prüfen; vermutlich liegen die Datenlinien über den Beschriftungsebenen der Grundkarte.
   - Lösung: Datenebenen in MapLibre **unterhalb** der ersten Symbol-/Beschriftungsebene der Grundkarte einfügen (`beforeId`), Ortsnamen mit Halo in Hintergrundfarbe, Kollisionsregeln prüfen.
   - Bei Bedarf Linien bei kleinen Zoomstufen dünner oder leicht transparent darstellen.
   - Für alle Karten umsetzen und mit Screenshots bei Zoom 11, 13 und 15 belegen.
   - Achte darauf, dass Straßennamen-Beschriftungen die Datenlinien nicht unlesbar machen; bei Konflikten Straßennamen der Grundkarte dezenter oder erst ab höherem Zoom zeigen.
7. **Logo „HMR“ oben links einbauen.**
   - Quelle: Ich lege eine JPG-Datei unter `assets/brand/hmr-logo-source.jpg` ab. **Fehlt sie, halte an und frage nach**, statt ein Logo zu erfinden.
   - Zuschnitt (Agent `asset-processor`): Rand automatisch auf den Inhalt trimmen, gleichmäßigen Schutzraum ergänzen, Seitenverhältnis erhalten, nicht verzerren.
   - Hintergrund: Ist er einfarbig weiß und die Kopfzeile ebenfalls weiß, bleibt er; sonst sauber freistellen und als PNG mit Transparenz speichern – nur wenn das ohne Artefakte gelingt, sonst nachfragen.
   - Exporte: Kopfzeile in 1× und 2× (PNG oder WebP), Favicon-Satz (16, 32, 180 px Apple Touch Icon), Open-Graph-Bild 1200 × 630 mit Logo und Seitentitel.
   - Originaldatei nicht verändern.
   - Platzierung links neben „Straßenfunktionsplan Hamburg – Entwurf“, ausgerichtet am Raster: Logohöhe passend zur Typoskala (z. B. Versalhöhe bzw. Zeilenhöhe des Titels), Abstand in Rastereinheiten, linksbündig an Spalte 1, keine Schatten, keine Rahmen.
   - Mobil: Logo bleibt, der Titel darf kürzer werden („Straßenfunktionsplan“).
   - Logo verlinkt auf die Startseite; Alternativtext „HMR – Hamburg Mobility Revolution“.
   - Biete zusätzlich als Option an, „HMR“ als SVG in der Hausschrift nachzubauen (schärfer, kleiner). Das nur als Vorschlag mit Vergleichsscreenshot, nicht ohne mein OK verwenden.
8. **Name „Hamburg Mobility Revolution“ auf der Webseite.** Zwei Varianten im Swiss-Stil zeigen:
   - (A) im Kopf: Logo, daneben zweizeilig „Hamburg Mobility Revolution“ (klein, Grau) über „Straßenfunktionsplan Hamburg – Entwurf“ (Titelgröße);
   - (B) im Kopf nur Logo und Titel, der Name in Fußzeile, auf der Über-/Methodikseite, im Seitentitel (`<title>`) und in den Meta-/Open-Graph-Angaben.
   - Typografie und Abstände ausschließlich aus den vorhandenen Design-Tokens. Keine neuen Farben ohne Begründung.

## Prüfung und Bericht

- Tests anpassen (Ansichten, URL-Weiterleitungen, Legenden) und grün halten; Build ohne Warnungen.
- Agent `screenshot-runner`: vorher/nachher für alle betroffenen Karten und Seiten, Desktop und Mobil, Zoom 11/13/15.
- Agent `link-und-a11y-check`: keine toten Links, keine Konsolenfehler, axe-core ohne kritische Befunde, Kontrast des Logos und der Legenden geprüft.
- Agent `review` (sonnet): prüft den Diff gegen die Liste 1–8 und gegen die Fundstellenliste; meldet Lücken.
- Bericht `docs/cleanup/2026-11/bericht.md`:
  - je Änderung, was geändert wurde und wo;
  - Screenshots;
  - die Varianten für Legende (5) und Kopfbereich (7/8) nebeneinander mit Empfehlung;
  - Liste der per Konfiguration ausgeblendeten Ansichten mit der Zeile zum Wiedereinschalten;
  - welcher Agent mit welchem Modell was erledigt hat.
- Dann **anhalten**. Nach meiner Wahl der Varianten und meinem OK: gewählte Varianten finalisieren, Pull Request, Merge, Deployment, kurzer Abschlusscheck der Live-Seite (Agent `screenshot-runner`).
