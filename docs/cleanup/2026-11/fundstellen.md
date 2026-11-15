# Fundstellen – Aufräumen 2026-11 (prompts/25_cleanup_logo.md, Schritt 0)

Erhoben von den Agenten `fundstellen-suche` (haiku, Kopfband/Changelog/Kopf/Tokens) und einer zweiten Lese-Suche
(Karten, Ansichten, Legenden, Ebenen). Spalte „Stand“: was mit der Fundstelle passiert ist. Zeilennummern beziehen sich
auf den Stand vor der Änderung (Branch `redesign/2026-11`, Commit 0dc2b7c).

## Zuordnung der Namen zu den IDs im Code

Die Karten heißen im Code „Themen“ (`THEMES` in `web/src/state.js`). Jede Ansicht zeigt genau eine Kartenebene (`layer`).

| Name | Thema | Ansicht | Ebene | Stand |
| --- | --- | --- | --- | --- |
| Radnetz | `rad` | – | – | Titel bleibt |
| Lücken | `rad` | `luecken` | `cgap` | `enabled: false` |
| Radweg | `rad` | `radweg` | `cfac` | `enabled: false` |
| Platz in der Straße | `platz` | – | – | Titel jetzt „Fahrstreifen“, ID bleibt `platz` |
| Passt das Ziel | `platz` | `ziel` | `cfit` | `enabled: false` |
| Fahrstreifen | `platz` | `fahrstreifen` | `lanes` | einzige Ansicht, kein Umschalter |
| Breite, Regelprofil (Ebene 3) | `platz` | `breite`, `regelprofil` | `width`, `feas` | `enabled: false` |
| Heute und Ziel | `abweichung` | – | – | bleibt |
| Abweichung | `abweichung` | `ziel` | `disc` | neue Legende (zwei Varianten) |

## 1. Kopfband „Entwurf …“

| Fundstelle | Art | Stand |
| --- | --- | --- |
| `web/index.html:12` (`div.banner`, `#banner-text`) | Markup | entfernt |
| `web/src/main.js:309` (Text aus `meta.disclaimer`) | Code | entfernt; Datenstand jetzt in `#foot-version` |
| `web/src/style.css:49-51` (`.banner`) | CSS | entfernt |
| `web/e2e/site.spec.js:41-42` (`ready()` wartet auf `#banner-text`) | Test | wartet auf `#foot-version`; neuer Test „kein Band“ |
| `analysis/redesign/ui/lib.mjs:36`, `analysis/review_2026_11/ui/lib.mjs:33` | Analyse-Skripte | warten auf Fußzeile (Fallback Band) |
| `analysis/review_2026_11/ui/heuristics.mjs:196-214` (Prüfung „Band sichtbar“) | Analyse | übersprungen, wenn kein Band |
| `analysis/redesign/ui/capture.mjs:78-82`, `analysis/redesign/readability.py:149` | Analyse | Band optional |
| `analysis/review_2026_11/ui/heuristics.mjs:278` (Ladezeitmessung wartet auf `#banner-text`) | Analyse | wartet auf Fußzeile (Nachtrag nach Review) |
| `docs/redesign/tokens.json:40, 86` (`notice`) | Leitlinie | als „entfallen“ markiert, Token `logo` ergänzt |
| `docs/redesign/03_design_system.md:120` | Leitlinie | „kein Kopfband mehr, nicht wieder einbauen“ |
| `docs/redesign/02_information_architecture.md:36, 170-171` | Leitlinie | angepasst |
| `prompts/24_redesign_swiss_plain_language.md:12, 60` | Auftrag | angepasst, damit spätere Läufe das Band nicht zurückbringen |
| `docs/redesign/01_inventory.md:53, 67, 93`, `docs/review/2026-11/03_oberflaeche.md:272-274, 482` | Bestandsaufnahme/Review (historisch) | unverändert (beschreiben den damaligen Stand) |
| `prototypes/redesign/**` (`.notice`) | Prototypen (nicht live) | unverändert |

Erhalten bleibt die Kennzeichnung: Titelzusatz „– Entwurf“ (`web/index.html`, `config/project.yaml:27`), neue Zeile in
der Fußzeile, `meta.disclaimer` in der Methoden-Zusammenfassung (`web/src/method.js:48`) und im Impressum
(`web/src/pages.js:42`), Kartenzuschreibung (`web/src/map.js:46-47, 62`), Hinweis in Radnetz-Legenden.

## 2. Changelog / „Was ist neu“

| Fundstelle | Art | Stand |
| --- | --- | --- |
| `web/src/method.js:57` (Link), `:180-192` (`newsHtml`) | Code | entfernt |
| `web/src/main.js:5, 213, 241-243, 271` | Code | entfernt |
| `web/src/state.js:11` (`METHOD_SUBS` mit `neu`) | Code | `neu` gestrichen; `#methode/neu` → `#methode` |
| `web/src/style.css:223, 236` (`ul.news`, `.changelog`) | CSS | entfernt |
| `pipeline/s09_export.py:10, 610` (Kopie `CHANGELOG.md` → `data/out/changelog.md`) | Export | entfernt; `data/out/changelog.md` lokal gelöscht |
| `config/plain_language.yaml:587-599` (`method.news`) | Texte | entfernt, Version 0.12.0 |
| `web/test/method.test.js:114-127` und „news placeholders“ | Test | entfernt; Test „kein Link auf #methode/neu“ |
| `web/test/state.test.js` (Unterseite `neu`) | Test | erwartet Rückfall auf Zusammenfassung |
| `web/e2e/site.spec.js:20` (axe-Seite „Methode Neu“) | Test | entfernt |
| `analysis/redesign/ui/p3_method.mjs:6`, `analysis/redesign/p3_readability.py:55` | Analyse | `neu` bzw. `news` optional (Nachtrag nach Review) |
| `prompts/24…:114` („Was ist neu“-Eintrag verlangt) | Auftrag | jetzt `CHANGELOG.md` |
| `docs/redesign/impl_method.md:14`, `02_information_architecture.md:135`, `decisions.md:60` | Leitlinie | als entfallen markiert (decisions.md: Paketbeschreibung historisch, unverändert) |
| `CHANGELOG.md` | Repository | bleibt, neuer Eintrag |

## 3. und 4. Ausgeblendete Ansichten

| Fundstelle | Art | Stand |
| --- | --- | --- |
| `web/src/state.js:15-33` (`THEMES`, `firstView`, `withView`, `OLD_LAYER`) | Konfiguration | `enabled: false`, `viewsOf()`; alte `?layer=`-Links und `view=` fallen auf die erste aktive Ansicht |
| `web/src/main.js:43-53, 68` (Umschalter, „Weitere Ansichten“) | Code | nutzt `viewsOf()`; Umschalter entfällt bei einer Ansicht (vorhandene Logik) |
| `web/src/map.js:39-50` (`ensureSources`, `cycle_mesh_gaps.geojson` nur bei `cgap`) | Daten | unverändert: Daten ausgeblendeter Ansichten werden nicht geladen |
| `web/src/layers.js:243-252` (`LAYER_INFO`) | Texte | `lanes` neu formuliert; `cfit`, `cfac`, `cgap`, `feas` bleiben für das Wiedereinschalten |
| `web/src/profile.js:75-82, 110` (Machbarkeit im Steckbrief) | Steckbrief | bleibt, mit Überschrift „Hat das Ziel Platz?“ und einem erklärenden Satz |
| `web/src/districts.js:82-89` („Ziel passt nicht km“, „Radnetz ohne Radweg km“) | Bezirksseite | unverändert (Kennzahlen, kein Verweis auf eine Ansicht) |
| `config/plain_language.yaml:455-500` (Methodenkapitel) | Texte | geprüft: keine Verweise auf Ansichten |
| `config/glossary.yaml:33` („Machbarkeit“) | Glossar | unverändert (Begriff, keine Ansicht) |
| `web/test/state.test.js`, `web/e2e/site.spec.js:10, 21, 76-81, 141-155` | Tests | angepasst, neue Tests für Weiterleitungen |
| `docs/redesign/02_information_architecture.md:59-61`, `decisions.md:17` | Leitlinie | Nachtrag |

## 5. Legende „Abweichung“

| Fundstelle | Art | Stand |
| --- | --- | --- |
| `web/src/layers.js:98-107` (Gruppen `disc`) | Code | `discGroups()` mit Varianten a/b, Stärke in drei Breiten |
| `web/src/layers.js:271-292` (`legendHtml`) | Code | Breiten-Muster, Frage (b), Link „Was heißt das?“ |
| `web/src/palette.js:45-49` (`DISC_TYPE_STYLE`) | Stil | unverändert |
| `config/glossary.yaml:25-27` (D1–D3) | Glossar | unverändert (Filter „Art der Abweichung“ nutzt es weiter) |
| `docs/redesign/04_language.md:138-146` (geplante Formulierung) | Leitlinie | Variante b setzt sie um |
| `pipeline/lib/discrepancy.py`, `config/rules.yaml:926-1021` | Regeln | unverändert (nur Darstellung) |

## 6. Ebenen und Beschriftungen

| Fundstelle | Art | Stand |
| --- | --- | --- |
| `web/src/map.js:52-66, 85-99` (`addLayer` ohne `beforeId`) | Code | `beforeId` = erste Symbolebene der Grundkarte (`address_label`), Kreuzungssymbole bleiben oben |
| Grundkarte `places_subplace`, `places_locality`, `roads_labels_*` (@protomaps/basemaps 5.7.2) | Stil | Halo weiß; Stadtteilnamen dunkler; Nebenstraßennamen weiter ab Zoom 15 |

## 7. und 8. Logo und Name

| Fundstelle | Art | Stand |
| --- | --- | --- |
| `web/index.html:6, 8, 13-14` (Meta, `<title>`, Kopf) | Markup | Logo, Varianten A/B, Favicons, Open Graph |
| `web/src/main.js:272` (`document.title`) | Code | „· Hamburg Mobility Revolution“ angehängt |
| `web/src/style.css:53-58, 69-74` (Kopfraster) | CSS | Titel 5 Spalten, Navigation 4, Suche 3; mobil kurzer Titel |
| `web/vite.config.js` | Build | `og-image.png` mit festem Pfad |
| `web/index.html:50-55` (Fußzeile) | Markup | Name und „unabhängiges, nicht amtliches Projekt“ |
| Keine früheren Fundstellen für „Hamburg Mobility Revolution“ oder „HMR“ im Repository. | | |
