# Redesign 2026-11 · Entscheidungen

Zum Ausfüllen durch prstolpe. Optionen, Wirkung und Aufwand stehen in [`proposals.md`](proposals.md). Bitte je Zeile
die gewählte Option (Buchstabe) und eine Anmerkung eintragen. Leer heißt nicht entschieden. „a“ heißt immer: so lassen
wie heute.

Teil B setzt nur Zeilen mit gewählter Option um, in den Paketen am Ende. Eine neue Sitzung kann von dieser Datei aus
weitermachen.

## Oberfläche, Inhalte, Sprache

| ID | Frage | Optionen | Empfehlung | gewählte Option | Anmerkung |
|---|---|---|---|---|---|
| E1 | Startseite und Varianten | a so lassen · b Variante A „Karte zuerst“ · c Variante B „Überblick zuerst“ · d B als Startseite, A als Karte | d | b| |
| E2 | Informationsarchitektur | a so lassen · b drei Ebenen überall, 5 Menüpunkte (Start, Karte, Bezirke, Methode, Daten), Impressum im Fuß · c wie b, aber ohne Startseite | b | b| da a für E1 gewählt wurde, checken, ob karte benötigt wird. **Geklärt 14.11.2026:** Karte ist die Startseite, Menü mit 4 Punkten (Karte · Bezirke · Methode · Daten), keine eigene Startseite; beim ersten Besuch ein schließbarer Kasten „Was ist das?“ (2 Sätze, Suche, Link zur Methode) auf der Karte; Logo führt zur Karte.|
| E3 | Kartenebenen | a 13 Ebenen wie heute · b 5 Themen mit je 2–3 Ansichten · c wie b und dazu „alle Ebenen“ auf Ebene 3 für Fachleute | b |b | Nachtrag 2026-11 (prompts/25): „Passt das Ziel?“ ausgeblendet (verwirrt); die Machbarkeit steht nur noch im Steckbrief. |
| E3b | Zwei Machbarkeitsaussagen | a beide zeigen · b nur „Passt das Ziel?“ (Querschnitt mit Radweg) sichtbar, Regelprofil auf Ebene 3 | b |b | |
| E3c | Unsicherheit | a Ampel und zwei Robustheits-Abschnitte wie heute · b ein Merkmal „Wie sicher ist das?“, nur „unsicher“ (7,3 % der km) erscheint auf Ebene 2 | b |b | |
| E4 | Einfache Sprache und Glossar | a so lassen · b Regeln aus `04_language.md` und `glossary.yaml` überall · c wie b, aber heutige Kategorienamen (Stadtmagistrale …) behalten | b |b | |
| E5 | Sprache der Regeldateien | a so lassen · b Felder `label_plain`, `explain_plain`, `why` ergänzen (Bedeutung unverändert, Nachweis in `05_rule_language.md`) · c wie b und Geschichte aus `description`/`note` in ein Feld `history` | c |c | |
| E6 | Farbkonzept der Karte | a Palette wie heute · b eine Bedeutung je Farbe: Tempo-Farbe für Kategorien, Orange für Handlungsbedarf, Petrol für Radverkehr | b |b | |
| E7 | Schrift | a Systemschrift wie heute · b Inter selbst gehostet (SIL OFL) für die Seite · c wie b und auch Kartenbeschriftung in Inter (PBF-Glyphen) | b | b| |

## Regeln zusammenlegen, vereinfachen, streichen (je Regel einzeln)

Wirkung und Begründung: [`06_rule_consolidation.md`](06_rule_consolidation.md). Alte IDs bleiben als Alias.

| ID | Vorschlag | Wirkung auf Ergebnisse | Empfehlung | freigeben / ablehnen / überarbeiten | Anmerkung |
|---|---|---|---|---|---|
| K1 | N7 in N2 aufnehmen | keine | freigeben | freigeben| |
| K2 | JC-05 in JC-02 aufnehmen | keine (nur Kennung an 840 Knoten) | freigeben |freigeben | |
| K3 | J-02 in J-01 aufnehmen | siehe Probelauf K3 | freigeben |freigeben | |
| K4 | C-IMP-06 in C-IMP-05 aufnehmen | keine | freigeben | freigeben| |
| K5 | C-FAC-03 in S-04 aufnehmen | keine | freigeben | freigeben| |
| K6 | N6 streichen (category_rank zu J-M-04) | keine | freigeben |freigeben | |
| K7 | PRF-07 streichen (Hinweis zu PL-05) | keine | freigeben | freigeben| |
| K8 | J-11 streichen (keine Straßenbahn) | siehe Probelauf K8 | freigeben | freigeben| |
| K9 | P-COM-03, P-ATT-02 auf inaktiv | keine | freigeben | freigeben| |
| K10 | C-NET-11 streichen | siehe Probelauf K10 | ablehnen | ablehnen| |
| K11 | C-NET-10 nur noch als Hinweis | siehe Probelauf K11 | ablehnen | ablehnen| |

## Nebenbefunde (nicht Teil des Redesigns, zur Weitergabe)

| ID | Befund | Optionen | Empfehlung | gewählte Option | Anmerkung |
|---|---|---|---|---|---|
| X1 | 743 Knoten mit heutiger Ampel bekommen J-05 „durchgehender Gehweg“, 589 davon mit ≥ 10 000 Kfz/Tag Zufluss, zusammen 1 306 Radunfälle. 4 der Top-5-Kreuzungen in Eimsbüttel bekommen J-05, 3 davon haben heute eine Ampel (z. B. Grindelberg / Hoheluftchaussee, 30 000 Kfz/Tag). Eine Zeile wie J-14 (Radroute quert) fehlt für GOW30. | a so lassen · b als offene Frage in `docs/open_questions.md` und in die nächste Regelrunde | b | b| |
| X2 | Die Begründung im Steckbrief zeigt nicht zutreffende Prüfungen wie Gründe (92 % der Steckbriefe) | a so lassen · b in Paket 2 trennen („Warum?“ / Ebene 3 „trifft nicht zu“) | b |b | |
| X3 | Zwei widersprüchliche Ist-Angaben zum Radverkehr im Steckbrief (93 Abschnitte) | a so lassen · b in Paket 2 nur noch die Ist-Führung S-FEAT-13 zeigen | b |b | |
| X4 | `docs/source_policy.md` fehlt weiterhin | a so lassen · b anlegen aus CLAUDE.md und guide.md · c Verweis im Prompt streichen | b | b| |

## Pakete für Teil B

Jedes Paket hat einen eigenen Branch und läuft so: Tests grün, Determinismus (zwei Läufe gleich), Vorschau (nicht live),
Bilder Desktop und Smartphone, axe, Lesbarkeit, Bericht `docs/redesign/impl_<paket>.md`, dann Halt für dein OK.

| Paket | Inhalt | aus Zeilen | Voraussetzung | grob |
|---|---|---|---|---|
| 1 Design-System und Layout | Tokens, Inter, Raster, Komponenten, Kartenstil | E1, E6, E7 | – | 2–3 Tage |
| 2 Inhalte und Texte | drei Ebenen, Themen, Steckbriefe, Bezirksseite, Startseite, Glossar, Weiterleitung alter Links | E1–E4, X2, X3 | Paket 1 | 5–7 Tage |
| 3 Methode | Zusammenfassung, Kapitel in drei Ebenen, Regelreferenz aus den Regeldateien, „Was ist neu“ | E2, E5 | Paket 2 (und 4 für die Referenz) | 2–3 Tage |
| 4 Sprache der Regeldateien | Felder ergänzen, `why` für alle Regeln, klarere Beschreibungen; Hash-Nachweis, Patch-Version, CHANGELOG | E5 | – | 1–2 Tage |
| 5 Regeln zusammenlegen | nur freigegebene K-Zeilen; erst Tests, dann YAML und Code; Aliase in `rule_trace`; Minor-Version; Bericht mit km/Knoten und Karte | K1–K11 | Paket 4 | 1–2 Tage |
