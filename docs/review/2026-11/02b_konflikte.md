# Review 2026-11 · Phase 2b: Konflikte Radnetz ↔ Straßennetz

Stand A = Produktivstand (rules.yaml 0.16.0, cycling_rules.yaml 0.7.0, design_rules.yaml 0.6.0). Skripte:
`analysis/review_2026_11/conflicts_2b.py` (Zählung), `iterate_2b.py` (Iteration im Worktree). Ergebnisse:
`data/scenarios/review_static/conflicts_A.json`, `data/scenarios/B_gow30_cap/conflicts_B.json`,
`data/scenarios/iter_2b/rounds.json`.

## Kurzfassung

- Die beiden Netze werden nacheinander berechnet (Straße → Radnetz → Querschnitt → Knoten). **Rückmeldungen gibt es nur
  als Flags:** D5 (Kategorie GOW30 vorschlagen), D6 (Durchfahrt prüfen), D7 (Route verlegen). Keine Stufe liest sie wieder
  ein.
- **Größter Konflikt:** 304 km Soll-Fahrradstraße liegen auf Straßen mit Linienbus, 183 km davon mit ≥ 100 Fahrten/
  Werktag. Das ist dasselbe Straßenbündel wie Fehlerbild E1 in 2a (Sammelstraßen als ETW30).
- **Knoten:** An 55 Knoten quert eine RSV/HAUPT-Route eine GOW50; Soll-Typ ist „Gehwegüberfahrt“. Mit Szenario B
  (DTV-Obergrenze) wären es 219.
- Ein **abgestimmter Ablauf** (Abschnitt 3) löst die Bus-Fahrradstraßen-Konflikte über die Straßenkategorie und übernimmt
  die D5-Vorschläge. Was danach bleibt, sind Zielkonflikte zur Entscheidung (Abschnitt 4).

## 1 Konflikttypologie und Zählung

| Typ | Beschreibung | A (heute) | B (DTV-Obergrenze) |
|---|---|---:|---:|
| K1 | RSV/HAUPT an GOW50 ohne Platz für getrennte Radwege (fit_class does_not_fit) | 9,6 km (44 Abschnitte) von 103 km RSV/HAUPT an GOW50 | 22,8 km (138) von 319 km |
| K2 | Soll-Fahrradstraße auf ETW30 mit zu viel Kfz-Verkehr | 304 km mit Bus (183 km ≥ 100 Fahrten); DTV über 2 500 nachweisbar: 0 km, weil DTV auf allen 1 325 km fehlt | 303 km / 183 km |
| K3 | RSV/HAUPT quert GOW50 ohne geeigneten Knotentyp | 55 von 264 Querungen (alle „Gehwegüberfahrt“) | 219 von 377 |
| K4 | Kategoriewechsel GOW30 ↔ GOW50 entlang RSV/HAUPT-Routen | 174 von 2 134 Routen, 332 Wechsel, 34 Routen mit ≥ 3 | 190 von 2 106, 393, 54 |
| K5 | Umweg über P-DIR-01 | 1 468 Routen (HAUPT 934, BASIS 527, RSV 7) | 1 466 |
| K5a | davon Korridorrouten | 22 | — |
| K5b | P-ATT-03-Alternativen übernommen | 20 Kanten | 11 |
| K6 | Abbaukaskade D7 (Route verlegen) auf dem Radnetz / D5 (GOW30 vorschlagen) | D7 84 km, davon RSV/HAUPT 42 km; D5 26 km, davon RSV/HAUPT 12 km | — |
| K7 | Ist-Radweg an ETW30-Hauptroute (Flag track_on_access_road) | 233 km (1 732 Abschnitte) | — |

**Hinweise zur Zählung:**
- **K2:** Kfz-DTV fehlt auf 99,9 % der ETW30 (C-FAC-02 gilt dann als erfüllt). Der Linienbus ist der einzige vorhandene
  Hinweis auf zu viel Verkehr. Szenario D (Modell) ergibt 184 km Soll-Fahrradstraße über 2 500 Kfz/Tag heute; Annahme,
  nicht Messung.
- **K3:** Nur Querungen, bei denen mindestens zwei Nicht-GOW50-Arme RSV/HAUPT tragen (die Route geht über die GOW50,
  nicht nur an ihr entlang). Die Entscheidungstabelle hat keine Zeile „Radroute quert GOW50“, wenn die Route auf ETW30
  liegt; J-06/J-07 vergeben die Gehwegüberfahrt der Nebenstraße.
- **K5:**
  - 1 446 der 1 468 Überschreitungen sind Maschenrouten (mesh_haupt 919, mesh_basis 527), 1 108 davon kürzer als 1 km.
  - Der Umwegfaktor ist dort Routenlänge / Luftweg der Enden. Bei Ringen und Schleifen liegen die Enden nah beieinander
    (Median 2,6, Maximum 1 062).
  - Das ist ein **Messfehler der Prüfung**, kein Netzfehler: P-DIR-01 auf Maschenrouten nur über OD-Paare messen (wie
    P-DIR-01 b).
- **K6:** D5 wird von PRF-06 als Vorschlag in `cat_change_proposal` geschrieben (137 Abschnitte), D7 als Flag (534
  Abschnitte).

## 2 Wo die Konflikte herkommen

| Konflikt | Ursache in der Kette | Auflösung über |
|---|---|---|
| K2 Bus auf Fahrradstraße | Straße als ETW30 eingestuft (2a E1), Radroute HAUPT darauf → S-02 macht sie zur Fahrradstraße | Straßenkategorie (S-1 Busregel) **oder** Führungsform (Radweg statt Fahrradstraße) **oder** Buslinie verlegen |
| K1 HAUPT an GOW50 ohne Platz | Kategorie GOW50 verlangt getrennte Radwege; Straßenraum zu schmal | D5 (GOW30), D7 (Route verlegen) oder Abbau (D1–D4) |
| K3 ungeschützte Querung | fehlende Tabellenzeile | neue Zeile J-14 (Radroute quert GOW50 → cycle_crossing_signal oder Mittelinsel) |
| K4 Wechsel entlang Routen | GOW30/GOW50 abschnittsweise nach Umfeld | Harmonisierung (S-5/S-6 in 2a) |
| K7 Radweg an ETW30 | Straße ETW30, Ist baulicher Radweg | Kategorie prüfen (häufig E1-Straßen) oder Radweg als gleichwertig (Entscheidung 2026-11-07: Teilerfüllung) |

## 3 Abgestimmter Iterationsablauf (Vorschlag)

```
Runde 0  Straßenkategorie (s05–s06b) → Radnetz (c01–c03) → Führungsform (c05) → Querschnitt (c06) → Knoten (c07)
Runde k  Rückkopplung:
         a) Querschnitt → Kategorie: D5-Vorschläge (GOW50 passt nicht → GOW30, C-G30-02) als Kategorie übernehmen
         b) Radnetz → Kategorie: Fahrradstraße mit Linienbus → Straße GOW30 (über S-1, einmalig als Regel)
         c) Querschnitt → Radnetz: D7-Flags bleiben Flags (Verlegen ist Entwurfsarbeit) → Liste Zielkonflikte
         neu rechnen ab coherence (a) bzw. classify (b), dann Konflikte zählen
Abbruch  keine neuen D5-Vorschläge oder 3 Runden; danach verbleibende K1/K2/K3/D7 = Zielkonflikte zur Entscheidung
```

Technisch nutzt der Ablauf nur vorhandene Mechanismen (Regel in rules.yaml, Kategorie-Overrides), keine neuen Stufen.
Im Produktivbetrieb wären die übernommenen D5-Fälle eine eigene Regel (H-XS-01 „Kategorie aus Querschnitt“) statt
Overrides, damit sie nachvollziehbar bleiben.

### Trockenlauf (Worktree, Runden 1–3)

Worktree `SFP_wt_iter_2b` (gelöscht nach dem Lauf), Ergebnisse `data/scenarios/iter_2b/`. Runde 1 = voller Lauf ab
`classify` mit Busregel S-1 (≥ 100 Fahrten/Werktag); Runde 2 = 282 D5-Vorschläge (47,6 km) als Kategorie-Overrides
(Autor `review-2026-11-dryrun`), Neurechnung coherence → junctions; Runde 3 = Abbruch, keine neuen D5-Vorschläge.

| Konflikt | Runde 0 (A) | Runde 1 (Busregel) | Runde 2 (D5 übernommen) |
|---|---:|---:|---:|
| K1 RSV/HAUPT an GOW50 ohne Platz | 9,6 km | 16,1 km | **0 km** |
| K2 Soll-Fahrradstraße mit Bus | 304 km | 116 km | 116 km |
| K2 davon ≥ 100 Fahrten/Werktag | 183 km | 0,6 km | 0,6 km |
| K3 Radroute quert GOW50 ohne geeigneten Knoten | 55 | 56 | 44 |
| K4 Routen mit Wechsel GOW30 ↔ GOW50 | 174 | 269 | 259 |
| K6 D7 (Route verlegen) gesamt / RSV/HAUPT | 84 / 42 km | 166 / 91 km | 166 / 91 km |
| K6 D5-Vorschläge | 26 km | 48 km | 0 km |
| K7 Ist-Radweg an ETW30-Hauptroute | 233 km | 147 km | 147 km |

**Kategorien nach Runde 2** (gegenüber A): GOW30 817 km (A 528), GOW50 262 km (A 223), ETW30 3 001 km (A 3 329).
Wechsel: ETW30 → GOW30 261 km, ETW30 → GOW50 67 km, GOW50 → GOW30 29 km.

**Lesart:**
- Die Busregel löst K2 fast vollständig für dichte Buslinien, erzeugt aber neue GOW50 ohne Platz (K1 steigt, D7
  verdoppelt sich).
- Die Rückkopplung D5 holt K1 auf null zurück.
- Abbruch nach zwei Runden; die Kette konvergiert, weil D5 nur in eine Richtung wirkt (GOW50 → GOW30).
- K4 steigt durch die neuen GOW-Abschnitte. Die Harmonisierung (2a S-5/S-6) würde das teilweise ausgleichen; im
  Trockenlauf nicht enthalten.

**Nebenbefund:** Nach Kategorie-Overrides meldet `make validate` „Basislauf reproduziert cat_proposed: False (6
Abweichungen)“ und bricht ab. Die Radkette läuft trotzdem durch. Ursache nicht geklärt; vor Umsetzung von E4 prüfen
(validate vergleicht den Basislauf mit `cat_proposed` nach Overrides).

## 4 Bewusste Zielkonflikte (zur Entscheidung)

Nach der Iteration bleiben (Liste `data/scenarios/iter_2b/remaining.parquet`):

| Zielkonflikt | Umfang | Optionen |
|---|---|---|
| RSV/HAUPT an GOW50 ohne Platz, D7 „Route verlegen“ | 91 km (gesamt 166 km); längste: Elbchaussee 4,6 km, Rissener Landstraße 1,8, Baron-Voght-Straße 1,4, Leuschnerstraße 1,4, Rahlstedter Straße 1,3 km | Route verlegen (Entwurf); Kategorie GOW30 trotz Bedarf an Verbindungsfunktion; Parken/Bäume opfern (D1/D2 bereits geprüft) |
| Soll-Fahrradstraße mit wenig Bus (Median 50 Fahrten/Werktag) | 116 km | Bus akzeptieren (CROW: Fahrradstraße mit Bus nur ausnahmsweise); Busregel tiefer setzen; Radweg statt Fahrradstraße |
| Radroute quert GOW50 ohne geeigneten Knoten | 44 Knoten | Tabellenzeile J-14 (KF-1) |
| Querschnitt passt nicht (alle Kategorien) | 1 047 km, davon ETW30 873 km (D6: Einbahn oder Durchfahrtsunterbrechung prüfen), GOW30 169 km | Einbahnregelung, Parken entfallen lassen; Entscheidung je Straße |

Diese Liste ist das, was ein abgestimmter Ablauf nicht automatisch lösen kann und soll: Es sind Abwägungen zwischen
Verbindungsfunktion, Radnetz und Straßenraum.

## 5 Weitere Vorschläge

Struktur je Vorschlag: Problem · Beleg · Vorschlag · Wirkung · Risiken · Aufwand · source_type.

### KF-1 Knotenzeile „Radroute quert GOW50“

- **Problem:** K3.
- **Beleg:** 55 Knoten (B: 219).
- **Vorschlag:**
  ```yaml
  # design_rules.yaml junctions.decision_table
  + - {id: J-14, legs: 'GOW50+ETW30', if: 'cycle_route_crosses and top_cycle_cat in [RSV, HAUPT]',
  +    then: cycle_crossing_signal, else_if: 'entering_dtv_sum <= crossing_island_max_dtv', else_then: cycle_crossing_island, status: draft}
  + crossing_island_max_dtv: {value: TODO, source_type: assumption}
  ```
- **Wirkung:** 55 Knoten erhalten eine Radquerung statt Gehwegüberfahrt.
- **Risiken:** neue Zielwerte ohne Quelle (TODO).
- **Aufwand:** mittel.
- **source_type:** swov_crow (Regel), assumption (Schwelle).

### KF-2 Umwegprüfung auf Maschenrouten

- **Problem:** K5.
- **Beleg:** 1 446 Messfehler.
- **Vorschlag:** P-DIR-01 (a) nur für Korridorrouten; Maschenrouten über (b) OD-Paare.
- **Wirkung:** K5 sinkt auf rund 22 Routen.
- **Aufwand:** klein.
- **source_type:** keine neue Schwelle.

### KF-3 D5/D7 als Rückkopplung im Regelwerk

- **Problem:** Flags ohne Wirkung.
- **Vorschlag:** neue Regel H-XS-01 in rules.yaml: „GOW50 mit fit_class does_not_fit und D5-Vorschlag → GOW30“ (wirkt
  nach c06, ein zweiter Durchlauf s06b–c07); D7 bleibt Flag, wird aber im Steckbrief und in einer Zielkonfliktliste
  gezeigt.
- **Wirkung:** siehe Trockenlauf.
- **Risiken:** Zirkularität (Kategorie hängt am Querschnitt, der an der Kategorie hängt). Durch das Abbruchkriterium
  begrenzt; nur Richtung GOW50 → GOW30 zulassen.
- **Aufwand:** mittel.
- **source_type:** swov_crow (C-G30-02).
