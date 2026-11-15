# Quellenpolitik

Diese Seite fasst zusammen, was für Quellen im Projekt bereits festgelegt ist. Sie führt keine neuen Regeln ein. Zu jeder Aussage steht, wo sie herkommt.

## Zweck
Jede Zahl, Regel und Karte soll erklärbar und reproduzierbar sein (CLAUDE.md, „Ziel“). Darum ist festgelegt, woher Daten und Regeln stammen dürfen und wie das gekennzeichnet wird.

## Welche Quellen zulässig sind
- Es gelten nur Endpunkte, die in `config/sources.yaml` stehen (CLAUDE.md, „Wo was steht“).
- Endpunkte, Datensätze, Schwellenwerte und Attributnamen werden nicht erfunden. Unbekanntes wird als TODO markiert, in `docs/open_questions.md` eingetragen und nachgefragt (CLAUDE.md, „Fachliche Regeln“; docs/guide.md, Abschnitt zu Regeln und Konventionen).
- Steht bei einer Quelle `url: null`, ist der Endpunkt noch nicht bestätigt. Er muss vor der Nutzung ermittelt werden (config/sources.yaml, Kopfkommentar).
- Bei Netzwerkfehlern oder nicht erreichbaren Endpunkten wird abgebrochen und berichtet. Es gibt keine Ersatzquellen (CLAUDE.md, „Qualitätsregeln“).

## Herkunft jeder Regel
- Jede neue Regel braucht `id`, `source`, `source_type` und `status` (CLAUDE.md, „Fachliche Regeln“). Das gilt auch für die Radnetz- und Querschnittsregeln (CLAUDE.md, „Radnetz und Soll-Querschnitt“).
- `source_type` ist einer von: `swov_crow` (niederländische Primärquelle), `de_regelwerk` (FGSV, StVO/VwV), `hamburg` (ReStra, Hamburger Daten), `assumption` (eigene Annahme, zu prüfen) (docs/guide.md, Abschnitt „Regelwerk“).
- Annahmen werden als `assumption` gekennzeichnet und von einer Verkehrsplaner*in geprüft (docs/guide.md, Abschnitt zu Annahmen; docs/open_questions.md, „Fachlich“).
- Schwellen ändert man nicht, um Tests grün zu bekommen. Änderungen brauchen eine Begründung, eine neue `meta.version` und einen Eintrag in CHANGELOG.md (CLAUDE.md, „Fachliche Regeln“).

## Rohdaten
Rohdaten liegen in `data/raw`. Zu jeder Quelle gehören Quelle, Abrufdatum und Hash in `data/manifest.json` (CLAUDE.md, „Konventionen“; docs/guide.md, Datenbeschaffung). In Git liegen nur kleine Testfixtures und das Manifest (CLAUDE.md, „Qualitätsregeln“).

## Lizenzen
- Amtliche Hamburger Daten stehen unter dl-de/by-2.0 und brauchen einen Quellenvermerk.
- OSM steht unter ODbL. Daten, die aus OSM abgeleitet sind, stehen deshalb ebenfalls unter ODbL.
- Die Quellenvermerke und Lizenzen je Quelle stehen in `docs/licenses.md`. Die Lizenz je Quelle steht auch in `config/sources.yaml`. (CLAUDE.md, „Qualitätsregeln“; docs/guide.md, Abschnitt „Lizenzen in einem Satz“.)
- Die juristische Prüfung vor der Veröffentlichung steht noch aus (docs/licenses.md, Kopfzeile: „Entwurf, vor Veröffentlichung juristisch prüfen“).

## Unfalldaten
Unfalldaten werden nur aggregiert je Abschnitt gespeichert und dargestellt, bei Knotenpunkten aggregiert je Knoten (CLAUDE.md, „Qualitätsregeln“; docs/licenses.md, Schluss).

## Darstellung auf der Webseite
In der Regelübersicht der Methodenseite steht „Annahme“ bei Werten, die das Projekt ohne Quelle gesetzt hat. Alle Quellen, Stände und Lizenzen stehen auf der Seite „Daten“ (config/plain_language.yaml, `method.reference.intro` und Methodenzusammenfassung).

## Offen
- Die genaue Stelle, an der die Annahmen in `rules.yaml` auf Prüfung und Freigabe stehen, ist nur als Sammelfrage in `docs/open_questions.md` („Fachlich“) geführt. Ein eigener Freigabeprozess ist offen.
- Lizenz mehrerer Quellen ist `unknown` oder „je Landing Page prüfen“ (config/sources.yaml; docs/licenses.md, Zeile „Weitere“). Wie damit bis zur Prüfung umzugehen ist, steht nirgends. Offen.
