# URL-Schema des Kartenzustands (Version 2)

Stand: 22.11.2026, Prompt 28 (umgesetzt in Phase 2).
Umsetzung: `web/src/state.js` (`parseHash`, `toHash`), Tests: `web/test/url_scheme.test.js`.

## Grundsätze

1. **Alles, was man teilen will, steht in der URL:** Thema, Ansicht, Ebenen, Auswahl, Filter, Kartenausschnitt.
   Nicht in der URL: offene Aufklapper, Höhe des mobilen Panels, Hervorhebung aus der Legende (das ist
   Bedienzustand, kein geteilter Inhalt).
2. **Der Zustand steht im Hash** (`#karte?…`), wie bisher. Die Seite ist statisch (GitHub Pages); der Hash
   erreicht keinen Server, es gibt also kein Tracking über die URL.
3. **Alte Links bleiben gültig.** Fehlt `v`, gilt Version 1; alte Namen werden auf die neuen abgebildet (Tabelle
   unten). Beim Laden schreibt die Seite die URL einmal in die neue Form um (`history.replaceState`, wie heute).
4. **Unbekannte Parameter werden ignoriert** und beim Umschreiben weggelassen. Unbekannte Werte fallen auf den
   Standard zurück (unbekanntes Thema → „Aufgabe und Tempo“, ausgeblendete Ansicht → erste Ansicht des Themas).
5. **Standardwerte werden nicht geschrieben**, damit Links kurz bleiben.
6. **Round-Trip ohne Verlust:** `parseHash(toHash(s))` ergibt `s` für jeden normalisierten Zustand, und
   `toHash(parseHash(h))` ergibt die kanonische Form von `h`. Kamerawerte werden beim Schreiben gerundet
   (siehe unten); der normalisierte Zustand enthält die gerundeten Werte.
7. **Neue Ansichten, Ebenen und Orte brauchen keine Schemaänderung:** gültige Werte kommen aus den Registern
   (`THEMES` in `state.js`, Ebenen-Register der Legende, `meta.special_places`), nicht aus dem Parser.

## Aufbau

```
#<seite>[/<unterseite>]?v=2&theme=…&view=…&layers=…&seg=…|node=…&place=…&bz=…&cat=…&dt=…&pr=…&z=…&lat=…&lon=…&pitch=…&bearing=…
```

Reihenfolge beim Schreiben ist fest, damit gleiche Zustände gleiche Links ergeben:
`v, theme, view, layers, seg|node, place, bz, cat, dt, pr, tabelle, regel, z, lat, lon, pitch, bearing`.
`v=2` steht nur auf der Kartenseite (die übrigen Seiten haben keinen Kartenzustand).

| Parameter | Bedeutung | Werte | Standard (nicht geschrieben) |
| --- | --- | --- | --- |
| Seite | Pfad vor `?` | `karte`, `bezirke`, `orte`, `methode[/kapitel]`, `daten`, `impressum` | `karte` |
| `v` | Version des Schemas | `2` | – (wird immer geschrieben, sobald ein weiterer Parameter folgt) |
| `theme` | Thema der Karte | Schlüssel aus `THEMES`: `aufgabe`, `rad`, `knoten`, `abweichung`, `platz` | `aufgabe` |
| `view` | Ansicht im Thema | Schlüssel aus `THEMES[theme].views`, z. B. `ziel`, `heute`, später `moeglich` | erste eingeschaltete Ansicht |
| `layers` | zusätzliche Ebenen, kommagetrennt, feste Reihenfolge | Schlüssel aus dem Ebenen-Register: heute `bus`, `fac`, `acc`; später z. B. `quartiere`, `baeume`, `parken`; `orte` (alle besonderen Orte ohne Auswahl) ist reserviert, sobald es mehr als einen Ort gibt | leer |
| `seg` | ausgewählter Straßenabschnitt | `seg_` + Hex (`segment_id`) | – |
| `node` | ausgewählte Kreuzung | Ziffern (`node_id`) | – |
| `place` | ausgewählter besonderer Ort | `[a-z0-9_]+` (id aus `config/special_places.yaml`) | – |
| `bz` | Bezirk | Name wie in `meta.districts` | ganz Hamburg |
| `cat` | Filter Aufgabe | kommagetrennte Kategorien | leer |
| `dt` | Filter Art der Abweichung | kommagetrennte Typen, `keine` | leer |
| `pr` | Dringlichkeit mindestens | 0–3 in Schritten von 0,25 | 0 |
| `z` | Zoomstufe | Zahl, 2 Nachkommastellen | – (ganz Hamburg bzw. Ort) |
| `lat`, `lon` | Kartenmitte (WGS84) | Zahl, 5 Nachkommastellen (≈ 1 m) | – |
| `pitch` | Neigung in Grad | 0–60, ganze Zahl | 0 |
| `bearing` | Drehung in Grad | −180 bis 180, ganze Zahl | 0 |
| `tabelle` | Tabelle auf der Bezirksseite | `1` | aus |
| `regel` | Regel auf `#methode/regeln` | Regel-ID | – |

Regeln für die Auswahl:
- Höchstens eins von `seg` und `node`. Stehen beide in der URL, gilt `node` (wie heute, Kreuzung vor Abschnitt).
- `place` darf zusätzlich zu `seg`/`node` stehen. `place=<id>` schaltet den Ort ein und zoomt auf ihn, wenn
  keine Kamera in der URL steht.
- `z`, `lat`, `lon` gelten nur zusammen. Fehlt einer, wird die Kamera ignoriert.

## Zukunft ohne Schemaänderung

- **„Heute schon möglich“** wird eine Ansicht `view=moeglich` in den Themen, für die es sie gibt. Der Parser kennt
  die Ansicht über `THEMES`; ein Link auf ein Thema ohne diese Ansicht fällt auf die erste Ansicht zurück.
- **Weitere besondere Orte:** neue id in `config/special_places.yaml` → `place=<id>` funktioniert.
- **Weitere Ebenen** (Ruhige Quartiere, Bäume und Parkplätze): neuer Eintrag im Ebenen-Register → `layers=…`
  funktioniert; die Legende zeigt den Eintrag automatisch.
- Erst eine echte Bedeutungsänderung eines bestehenden Parameters erhöht `v`.

## Alte Parameter → neue Parameter

| Alt (Version 1 und älter) | Neu (Version 2) | Seit |
| --- | --- | --- |
| kein `v` | Version 1 | – |
| `ov=bus,fac,acc` | `layers=bus,fac,acc` | Prompt 24 |
| `ov=cyc` | `theme=rad&view=amtlich` (Ebene entfällt) | Redesign 2026-11 |
| `layer=<schlüssel>` | `theme`/`view` laut `THEMES` (ausgeblendete Ansicht → erste Ansicht) | Redesign 2026-11 |
| `jct=<id>` | `node=<id>` | Prompt 28 |
| `map=<z>/<lat>/<lon>` | `z=<z>&lat=<lat>&lon=<lon>` | Prompt 28 |
| `place=<id>` | `place=<id>` (unverändert) | Prompt 26 |
| `#tabelle?bz=X` | `#bezirke?bz=X&tabelle=1` | Redesign 2026-11 |
| `#downloads`, `#quellen` | `#daten` | Redesign 2026-11 |
| `#radnetz` | `#methode/radnetz` | Redesign 2026-11 |
| `#methode/neu` | `#methode` | Prompt 25 |

Weiterleitungen von Kreuzungen, die durch die Armfilterung (J-M-01) zusammengelegt wurden
(`junction_redirects.json`), bleiben unverändert und greifen auch für `node=`.

## Tests

`web/test/url_scheme.test.js`: 25 alte Linkmuster, 300 zufällige Zustände (fester Startwert) im Round-Trip,
unbekannte Parameter, kanonische Reihenfolge, Neigung/Drehung. Ursprünglicher Plan:

- Round-Trip für zufällige gültige Zustände (alle Themen/Ansichten, Ebenen, Auswahl, Kamera mit und ohne
  Neigung/Drehung).
- Mindestens 20 alte Linkmuster aus den Abschnitten oben, jeweils mit dem erwarteten Zustand
  (z. B. `#karte?layer=cgap&map=14/53.57/9.95`, `#karte?ov=cyc,bus`, `#karte?place=schanze_verkehrsberuhigt`,
  `#karte?jct=123&theme=knoten`, `#tabelle?bz=Altona`, `#methode/neu`, `#karte?seg=seg_…&ov=acc&pr=1.5`).
- Unbekannte Parameter (`?foo=1&utm_source=x`) werden ignoriert und nicht zurückgeschrieben.
- Kanonische Reihenfolge: gleicher Zustand → gleiche Zeichenkette.
