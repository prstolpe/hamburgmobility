# Inventur der Karten-Oberfläche (vorher)

Stand: 22.11.2026, Prompt 28, Phase 1.1. Erstellt vom Agenten `ui-inventory` (haiku, nur lesend); Befunde in der
Hauptsitzung stichprobenartig geprüft (`--need` ungenutzt, Overlay `cyc` ohne Bedienelement, Kommentar
palette.js:11 – bestätigt) und um Sichtprüfung der Screenshots ergänzt (`img/before/`).
Texte aus `meta.json` (Kategorie-, Knoten-, Radnetz-Labels) wurden nicht inventarisiert.

## Wichtigste Befunde

| # | Befund | Fundstelle | Folge für Prompt 28 |
| --- | --- | --- | --- |
| 1 | **Zusatzebenen (Bus, Schulen/Kitas, Unfälle) haben keine Legende.** Bei eingeschaltetem Bus erklärt nichts die grauen, versetzten Linien (Screenshot `before-desktop-bus-z13.jpg`). | layers.js:328-332, legendHtml layers.js:349 | Registry: jede Ebene bringt eigene Einträge mit. |
| 2 | **Mobil steht die Legende unter der Karte**, nicht auf ihr; Kopf, Suche und Themenleiste belegen ~45 % der Höhe; die Themenleiste läuft rechts aus dem Bild („Kreuzu…“). „Mehr Ansichten und Filter“ aufgeklappt lässt ~57 px Karte übrig. | style.css (≤ 760 px), `before-mobile-*.jpg` | Bottom Sheet mit drei Höhen. |
| 3 | **Nur „Abweichung“ hat „Was heißt das?“.** Alle anderen Ansichten haben nur den einen Satz aus `LAYER_INFO`; Radverkehr verlinkt das Kapitel `#methode/radnetz` nicht. | layers.js:311-326, 371 | Jeder Eintrag: Ebene-2-Erklärung + Methodenlink. |
| 4 | **Gleiche Zeichen, verschiedene Bedeutung:** schwarzer Kreis = Schule/Kita (`ov-fac`) und = Kreuzung (`main-jctdot`); `#767676` = „unbekannt“ und = „andere Straße“ (hvs) und = „keine Kreuzung“; Strich [3,1.5] = Tempo 30 Hauptstraße, Tempo 40, falscher Radweg-Typ, amtlich „in Arbeit“. | palette.js:6,64,130; layers.js:160,244 | Registry prüft Symbol-Kollisionen innerhalb gleichzeitig sichtbarer Ebenen (Test). |
| 5 | **Gleiche Wörter, verschiedene Dinge:** „Ziel“ ist Ansicht in drei Themen; Thema „Heute und Ziel“ hat die Ansicht „Abweichung“; „Fahrstreifen“ ist Thema und Ansicht. | state.js:19-36 | Trennung Thema / Ansicht / Ebenen im Panel (Konzept). |
| 6 | **Zwei Texte für dasselbe:** Filter „keine Abweichung“ vs. Legende „passt bereits“; D1–D3 in der Legende aus `DISC_TEXT`, im Filter aus dem Glossar. | main.js:69, layers.js:86-98 | Eine Quelle je Begriff: `label_plain` aus der Registry auch für Filter. |
| 7 | Overlay `cyc` wird gezeichnet, hat aber weder Label noch Schalter (nur alte URL; wird beim Laden auf `theme=rad&view=amtlich` umgeschrieben). | state.js:14, 75-78; layers.js:232 | Altlast; im URL-Schema als Weiterleitung, Zeichen-Code entfällt. |
| 8 | `role="toolbar"` an der Themenleiste ohne Pfeiltasten-Steuerung (ARIA-Muster passt nicht). | index.html:55, main.js:44 | Neues Panel: Radiogruppe bzw. echte Toolbar. |
| 9 | „Filter zurücksetzen“ setzt Ebenen zurück, aber nicht den besonderen Ort. | main.js:115 | Chips: jede Ebene einzeln entfernbar; Reset klar benennen. |
| 10 | Kreuzungs-Punkte erscheinen in anderen Themen erst ab Zoom 14, nirgends erklärt. | layers.js:240-245 | Registry-Eintrag „Kreuzung (antippen für Steckbrief)“ mit Zoomhinweis. |
| 11 | Token `--need` ist definiert, aber ungenutzt; Farben doppelt in style.css und palette.js; harte Hexwerte (#333, #000, #4a4a4a). | style.css:20, map.js:107, layers.js:249 | Registry zieht Farben nur aus palette.js. |
| 12 | Schließen-Knöpfe: sichtbar „Schließen ✕“, Name „Steckbrief schließen“ – Label-in-Name knapp. | index.html:70,75 | Im neuen Panel angleichen. |
| 13 | Bäume und Parkplätze: keine Kartenebene (nur Steckbrief/Bezirksseite); Ruhige Quartiere: nicht gemergt. | districts.js:73 | Registry so bauen, dass beide später ohne Codeänderung andocken. |

## 1. Kartenebenen

| Schlüssel | Label (Ansicht) | Thema / Ansicht | Status | MapLibre-Layer (Quelle) |
| --- | --- | --- | --- | --- |
| cat | „Ziel“ (Aufgabe der Straße) | aufgabe / ziel | an | main-SW … main-ETW_ERF, casing (sfp/segments) |
| speed | „heute“ | aufgabe / heute | an | main-s20 … main-s_unknown (sfp) |
| hvs | „Hauptverkehrsstraßen (Vergleich)“ (Ebene 3) | aufgabe / hvs | an | main-hvs1, main-hvs0 (sfp) |
| disc | „Abweichung“ | abweichung / ziel | an | main-D1..D3, main-none, main-unchecked (sfp) |
| prio | „Dringlichkeit“ | abweichung / prio | an | main-p1..p3 (sfp) |
| width | „Breite der Straße“ | platz / breite | `enabled: false` | main-narrow … (sfp) |
| feas | „Regelprofil der Aufgabe“ | platz / regelprofil | `enabled: false` | main-fits … (sfp) |
| cnet | „Ziel“ | rad / ziel | an | main-cc-RSV(+inner), HAUPT, BASIS, ERSCHL (cyc/cycle_network) |
| cfac | „Radweg“ | rad / radweg | `enabled: false` | main-fs-* (cyc/cycle_segments) |
| cgap | „Lücken“ | rad / luecken | `enabled: false` | main-gap-*, gaps-fill/line |
| lanes | „Fahrstreifen“ | platz / fahrstreifen | an | main-ld-* (cyc/cycle_segments) |
| cfit | „Passt das Ziel?“ | platz / ziel | `enabled: false` | main-fit-* |
| jct | „Ziel“ | knoten / ziel | an (ab Zoom 12) | main-grp-* Symbole, selected-jct (jct/junctions) |
| coff | „amtliches Netz“ (Ebene 3) | rad / amtlich | an | ref-ref, main-grp-Bestand/In Arbeit/planned (cyc/cycle_official) |

Zusatzebenen: `bus` (ov-bus, #4a4a4a, Versatz +5), `fac` (ov-fac, schwarzer Kreis), `acc` (ov-acc, schwarz 45 %),
`cyc` (nur Alt-URL). Weitere: Besondere Orte (place-casing, main-place-<measure>, #235753; durchgezogen =
Fahrradstraße, gestrichelt = Fußgängerzone), Kreuzungspunkte `main-jctdot` (ab Zoom 14), Auswahl `selected` /
`selected-jct`, Grundkarte `rural-fill`, `district-line`.

## 2. Legendeneinträge

| Ebene | Zeichen / Farbe | Label | Erklärung |
| --- | --- | --- | --- |
| cat | Tempo-Farben: SW #332288 b7, GOW50 #CC3311 b5, GOW30 #0077BB gestrichelt, ETW30 #0077BB b2,5, ETW_ERF #117733 gepunktet | meta.categories | LAYER_INFO-Satz; kein Link |
| speed | #117733 / #0077BB / #AA4499 gestr. / #CC3311 / #332288; unbekannt #767676 gepunktet | fest | Satz |
| hvs | #111 b5 / #767676 b1,2 | fest | Satz |
| disc | #B35900, Typ = Strich, Stärke = Breite; passt #8a8a8a; nicht prüfbar #767676 gepunktet | DISC_TEXT | Satz + „Was heißt das?“ → #methode/abweichung |
| prio | #B35900 b4,5 / gestr. b3 / #8a8a8a | fest | Satz |
| cnet | #007A6E RSV (Doppellinie), HAUPT, BASIS gestr.; ERSCHL #8a8a8a | meta.cycling | Satz + Hinweis Entwurf |
| lanes | weniger #B35900 b4,5; gleich #8a8a8a; mehr #B35900 gestr.; gemeinsam #8a8a8a gestr.; unbekannt | meta.cycling | Satz + Hinweis |
| jct | schwarze Formen (Kreis, Quadrat, Dreieck, Raute, Ring, Balken), keine #767676; Umbau = Form in #B35900, größer | meta.cycling | Satz + Hinweis „Orange und größer …“ |
| coff | Entwurf #007A6E 45 %; amtlich #111 durchgezogen/gestr./gepunktet | meta.cycling | Satz + Quellenvermerk |
| Besondere Orte | #235753 auf weißem Rand, durchgezogen/gestrichelt | Maßnahme + „(gestrichelt)“ | Link „Was sind besondere Orte?“ im Schalterbereich |
| bus, fac, acc | – | **keine Legende** | nur Text am Schalter |
| ländlich | Fläche #767676 | „auf dem Land – nicht bewertet“ | – |

## 3. Bedienelemente (Kartenseite)

Themenleiste (5 Knöpfe, `aria-pressed`), Ansichts-Knöpfe (nur bei > 1 Ansicht der Ebene 1), Überschrift „Was die
Farben bedeuten“, Erklärsatz, Legende (`aria-live`), Bezirk-Auswahl, Fieldset Besondere Orte (Checkbox je Ort),
Aufklapper „Mehr Ansichten und Filter“ (Weitere Ansichten, „Zusätzlich anzeigen“ bus/fac/acc, Filter Aufgabe,
Art der Abweichung, Dringlichkeit-Regler, „Filter zurücksetzen“), Suche (Combobox, Straßen und Kreuzungen),
Zoomknöpfe (MapLibre), Intro-Box „Verstanden“, Steckbrief-Panel („Auf der Karte zeigen“, „Schließen ✕“),
Skizzen-Dialog. Fundstellen: main.js:44-126, index.html:37-75, map.js:85.

## 4. URL-Parameter

`#seite[/kapitel]`, `theme`, `view`, `ov` (bus, cyc, fac, acc), `cat`, `dt`, `pr` (0–3), `bz`, `tabelle`, `seg`
(`seg_[0-9a-f]+`), `jct` (Ziffern), `place` (`[a-z0-9_]+`), `map` (z/lat/lon), `regel`; Altlasten `layer`,
`ov=cyc`, `#tabelle`, `#downloads`, `#quellen`, `#radnetz`, `#methode/neu` (state.js:60-112). Kein Parameter für
Neigung/Drehung (die Karte erlaubt beides heute nicht: NavigationControl ohne Kompass, map.js:85).
Neues Schema: [docs/url_scheme.md](../url_scheme.md).

## 5. Farb-Tokens

CSS: `--ink #111`, `--text2 #4a4a4a`, `--muted #6b6b6b`, `--line #c8c8c8`, `--surface #f2f2f2`, `--bg #fff`,
`--focus #ffbf47`, `--need #B35900` (ungenutzt). palette.js: CASING, UNKNOWN #767676, RURAL_FILL #767676, SPEED
(5), NEED #B35900, NONE #8a8a8a, INK, CYCLING #007A6E, OVERLAY_COLORS, REFERENCE_COLOR = CYCLING (Kommentar
Zeile 11 sagt „ink“ – veraltet). Harte Werte: map.js:107 #333333, layers.js:249/252 #000000, special_places.yaml
#235753.
