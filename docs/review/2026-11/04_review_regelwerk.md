# Review Straßenfunktionsplan Hamburg – Regelwerk 2026-11

Nov 8, 2026 · @Raphael Stolpe

## 1. Kurzfassung

Das Regelwerk ist für einen zivilgesellschaftlichen Entwurf ungewöhnlich sauber: jede Regel hat ID, Herkunft und Status, die Kaskade ist deterministisch, fehlende Werte werden dreiwertig behandelt, und Annahmen sind offen als solche markiert. Geprüft wurden rules.yaml 0.16.0, cycling\_rules.yaml 0.7.0 und design\_rules.yaml 0.6.0 (176 Regeln, davon 128 `assumption`, alle Prüfstatus „offen“).

Die größte Schwäche liegt nicht in einzelnen Werten, sondern an den Nahtstellen der drei Dateien. Die Klassifikation stuft rund 360 km hoch belastete Hauptverkehrsstraßen als GOW30 ein, die Führungsregeln geben dort Radfahrstreifen und ein CROW-Fahrbahnprofil, das CROW selbst nur bis 10 000 Kfz/Tag vorsieht. Das ist der einzige Befund mit unmittelbarer Sicherheitsrelevanz in großem Umfang.

Zweitens gibt es zwei Machbarkeitsrechnungen mit verschiedenen Maßen (rules.yaml `required_width` gegen design\_rules-Profil), die sich auf der Webseite widersprechen. Drittens wird der Soll-Knotentyp zweimal bestimmt (N6 und Entscheidungstabelle J), und die Tabelle hat sicherheitsrelevante Lücken: Radrouten queren GOW50 ohne Signal, Turbokreisverkehre geben Radfahrenden Vorrang, und jede Autobahnrampe verlangt eine planfreie Radquerung.

Dringendster Handlungsbedarf, in dieser Reihenfolge:

1. GOW30 über dem CROW-Profil in der Trennungsmatrix auf baulich getrennte Radwege umstellen (F01) – unabhängig davon, wie E2 entschieden wird.
2. Knotenregeln für Turbokreisverkehr, Radroute × GOW50 und Rampen korrigieren (F02, F03, F08).
3. Eine einzige Machbarkeitsrechnung aus design\_rules ableiten und die Doppelzählung der Radfahrstreifen im GOW30-Profil beheben (F04, F05).

Viele Befunde decken sich mit Punkten der Entscheidungsvorlage E1–E15; sie sind in der Befundliste markiert und werden hier nicht neu verhandelt, sondern fachlich untermauert. Die vier Wertfragen sind am 08.11.2026 entschieden (Abschnitt 8); alle Vorschläge ab „mittel“ sind damit umsetzungsreif.

## 2. Verständnis der Intention

Das System schlägt für jeden Hamburger Straßenabschnitt eine Soll-Funktion nach Duurzaam Veilig vor, legt ein hierarchisches Radnetz darüber und leitet daraus Soll-Querschnitt und Knotentyp ab. Es ist ausdrücklich ein nicht amtlicher Diskussionsentwurf: Automatik schlägt vor, Menschen entscheiden (Overrides), jede Einstufung ist über `rule_trace` erklärbar.

**Zweck.** Eine prüfbare Netzlogik sichtbar machen und Diskrepanzen zwischen Soll-Funktion und heutiger Gestaltung („graue Straßen“) priorisieren. Ergebnis ist kein Plan, sondern eine Verhandlungsgrundlage für Verwaltung und Politik.

**Planungsphilosophie.**

- Verkehrssicherheit nach Safe-System-Logik (SWOV/CROW): Funktionstrennung, Homogenität, Erkennbarkeit; bei 50 km/h immer baulich getrennter Radverkehr.
- Umfeld vor Verkehrsmenge: Schule, Kita, Geschäftsnutzung oder fehlender Raum für einen Radweg machen eine Verbindungsstraße zur GOW30, auch bei hoher heutiger Belastung (Entscheidung zu C-G30-01, 2026-11-07).
- Flächenvorrang des Umweltverbunds: so wenige Kfz-Fahrstreifen wie möglich, Busstreifen vor zweitem Kfz-Streifen, Parken wird zuerst abgebaut.
- Radnetz nach den fünf CROW-Prinzipien mit Delfter Maschenweiten (dichteabhängig), deutlich dichter als das amtliche Radnetz.

**Eingangsdaten.** OSM (Netz, Gestaltung, Radwege), amtliches Tempo (OGC API), DTV nur auf Hauptverkehrsstraßen (2019), HVS-Zugehörigkeit über diese DTV-Linien, ALKIS (Gebäude, Nutzung, Verkehrsfläche), GTFS, Zensus 2022, Unfallatlas, Rad-Zählstellen. Kfz-Mengen auf Erschließungsstraßen, Ortsgrenze und Ist-Knotengestaltung fehlen.

**Ausgaben.** Je Abschnitt `cat_final`, confidence, Diskrepanztyp und Priorität; Radnetzkategorie, Soll-Führung und -Breite, Soll-Profil mit Abbaustufen und Passung; je Knotenpunkt Soll-/Ist-Typ und Radführung; Webkarte mit Steckbriefen.

**Bewusste Abweichungen von deutschen Regelwerken.**

| Thema | System | Deutsches Regelwerk | Begründung im System |
| --- | --- | --- | --- |
| Netzkategorien | 5 NL-Kategorien (SW, GOW50, GOW30, ETW30, ETW\_ERF) | RIN: Kategoriengruppen und Verbindungsfunktionsstufen | Safe System; RIN nur als Näherung |
| GOW30 auf Hauptverkehrsstraßen | Umfeld entscheidet, keine DTV-Obergrenze | StVO § 45 (9): Tempo 30 auf HVS nur mit Einzelbegründung | Entwurf, keine Anordnung |
| Radführung an 50 | nur baulicher Radweg, keine Rad-/Schutzstreifen | ERA: Radfahrstreifen je nach Belastungsbereich zulässig | CROW-Verschärfung |
| Fahrradstraße | jede Hauptroute auf ETW30 | VwV-StVO zu Z. 244.1 | CROW S-02 |
| Knoten | Kreisverkehr vor LSA, geschützte Kreuzung, Rad-Vorrang am Kreisel | Merkblatt Kreisverkehre, ERA | SWOV/CROW |
| Radwegbreiten | Projekt-Soll zwischen ERA und NL-Hauptnetz | ERA-Regelmaße | Komfort, Zukunftsnachfrage |

Maßstab der Prüfung ist daher nicht nur die Regelwerkskonformität, sondern ob eine Regel diese Philosophie widerspruchsfrei und sicher umsetzt.

## 3. Gesamtbewertung

Schwach sind die Nahtstellen (Konsistenz zwischen den Dateien, Widerspruchsfreiheit, Sicherheit an Knoten); stark sind Determinismus und Nachvollziehbarkeit. Skala 1 = gravierende Mängel bis 5 = ohne Beanstandung.

| Nr. | Dimension | Note | Begründung |
| --- | --- | --: | --- |
| 1 | Fachliche Richtigkeit | 3 | Quellen ehrlich gekennzeichnet, aber Doppelzählung im CROW-GOW30-Profil, RSV-Begriff ohne FGSV-Kriterien und Rad-Vorrang am Turbokreisel (F02, F04, F12). |
| 2 | Innere Widerspruchsfreiheit | 2 | Zwei Machbarkeitsrechnungen, zwei Knotentyp-Ableitungen, Soll-Profil baut Parken, das die Diskrepanzregel als Verstoß zählt (F05, F09, F11). |
| 3 | Eindeutigkeit und Determinismus | 4 | Erste-Treffer-Kaskade, `evaluation_order`, Kleene-Logik und Fallback-Regeln sind vorbildlich; nur Intervallgrenzen sind teils doppelt belegt (F27). |
| 4 | Vollständigkeit | 3 | Knotentabelle mit `no_rule`-Lücken, toter Auslöser `crossing_demand`, außerorts-Zweig ohne Daten (F10, F25, F28). |
| 5 | Grenzwerte und Kanten | 3 | Gemischte Bezugsgrößen (DTV, Spitzenstunde je Richtung bzw. beide Richtungen) sind dokumentiert, aber absolute Schwellen auf mod. Radmengen sind instabil (F12, F27). |
| 6 | Redundanz | 3 | N6/J-Tabelle, N7/H-STR-01, `requirements`/`widths_m` doppelt; `place_score` definiert, aber nirgends genutzt (F09, F25, F30, F32). |
| 7 | Konsistenz zwischen den Dateien | 2 | Breiten, Parken, Ist-Radweg-Definition und Machbarkeit weichen zwischen rules, cycling\_rules und design\_rules ab (F05, F11, F18, F26). |
| 8 | Netzlogik | 3 | Harmonisierung und N1–N5 tragen; GOW-Netz ist faktisch das HVS-Netz 2019 plus Score-Ergänzung, anbaufreie Hauptstraßen fehlen als Kategorie (F13, F23). |
| 9 | Radverkehrsführung | 3 | Matrix klar und CROW-konform innerorts, aber GOW30 ohne Belastungsbezug und Fahrradstraßen-Prüfung faktisch abgeschaltet (F01, F19). |
| 10 | Verkehrssicherheit | 2 | Radfahrstreifen bei 20 000–40 000 Kfz/Tag, unsignalisierte Querung von GOW50 durch Hauptrouten, Rad-Vorrang am Turbokreisel (F01–F03). |
| 11 | Praxistauglichkeit | 3 | Datenlücken offen benannt; confidence ist aber fast überall „mittel“ und trägt kaum Information (F14). |
| 12 | Übereinstimmung mit der Intention | 4 | Regeln dienen der erklärten Philosophie; Ausnahmen sind Abbaureihenfolge Bäume vor 2. Fahrstreifen und Parken im GOW50-Profil (F11, F17). |

## 4. Befundliste

38 Befunde: 3 kritisch, 9 hoch, 14 mittel, 8 gering, 4 Hinweise. Spalte „E“ verweist auf die Entscheidungsvorlage, wo der Befund dort schon angelegt ist. Abkürzungen: R = rules.yaml, C = cycling\_rules.yaml, D = design\_rules.yaml; Art: RW = Regelwerksabweichung, FS = fachliche Schwäche, LF = logischer Fehler, FH = formaler Hinweis. Mit „(A)“ markierte Befunde hängen an einer Annahme aus Abschnitt 7.

| Nr. | Regel-Referenz | Dimension | Art | Schweregrad | Befund | Begründung / Quelle | Vorschlag (Kurzform) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F01 | R C-G30-01; C separation\_matrix.GOW30, C-FAC-01; D PRF-04 | 9, 10, 7 | RW, FS | kritisch | GOW30 ohne DTV-Grenze erhält Radfahrstreifen und CROW-Fahrbahn 5,80/8,40 m; 362 von 523 km GOW30 liegen über 10 000 Kfz/Tag. E2 | CROW GOW30 2023: schmales/breites Profil nur bis 6 000/10 000 Kfz/Tag, darüber nur Profil mit Fietspad; Radfahrstreifen bei 20–40 Tsd. Kfz inkl. Bus/Lkw sicherheitlich nicht vertretbar | GOW30-Zelle belastungsabhängig: über `profiles.wide.max_dtv` Soll `separated_oneway_both` (CROW-Profil track); Flag `capacity_reduction_needed` |
| F02 | D JC-01, J-01/J-02/J-03 (`turbo_roundabout`) | 10, 1 | RW, FS | kritisch | Rad-Vorrang gilt auch am Turbokreisverkehr; Typ `roundabout_single_lane_cycle_yield` wird nie vergeben. | Zweistreifige Ein-/Ausfahrten: Kfz übersehen bevorrechtigte Radfahrende; NL-Praxis führt Rad am Turbokreisel wartepflichtig oder planfrei (A3). Turbokreisel sind kein deutsches Regelwerkselement | JC-01 nur einstreifig; neue JC-06: Turbokreisel Rad wartepflichtig, RSV/HAUPT planfrei prüfen |
| F03 | D J-04, JC-04 (Fahrradstraße/Hauptroute auf ETW30 quert GOW50) | 10, 4 | FS | kritisch | Eine Hauptroute auf ETW30 quert eine GOW50 über Gehwegüberfahrt plus Mittelinsel, ohne Belastungs- oder Fahrstreifengrenze, auch bei 2×2 Fahrstreifen. E5 | Unsignalisierte Querung von 2 Fahrstreifen je Richtung = Verdeckungskonflikt; ERA/RASt sehen dort LSA bzw. Querungshilfe nur bei niedriger Belastung vor | J-14 (E5 b) mit Bedingung: `lanes_per_direction >= 2 or entering_dtv_sum > crossing_signal_min_dtv` → `cycle_crossing_signal` |
| F04 | D PRF-04 (GOW30-Fahrbahn), lane\_width\_m.GOW30\_*; R required\_width.GOW30\_* | 1, 7 | LF, RW | hoch | PRF-04 legt Radfahrstreifen zusätzlich auf die CROW-Spanne 5,80–8,40 m; diese Spanne enthält die Fietsstroken bereits (Hinweis: `centre_runner_max_m`, `avoid_runner_m`). (A2) | Doppelzählung von rund 4,5 m → GOW30 „passt nicht“ zu häufig, D6-Flags unbegründet | Fahrbahn inkl. Radfahrstreifen: max(Profiluntergrenze, Kernfahrbahn + 2 × Radfahrstreifenbreite) |
| F05 | R required\_width, S-XS-06, C-G30-02; D PRF-05, lane\_width\_m.ETW30\_mixed, PL-04 | 2, 7 | LF | hoch | Zwei Machbarkeiten: R rechnet GOW50 16,50 m (Trennstreifen 0,50, Radweg 2,00) und ETW30 10,80 m (Fahrbahn 5,80), D rechnet mit 0,75 m, Projekt-Sollbreiten und 4,75 m. Webebenen „Machbarkeit“ und „Querschnitt passt?“ widersprechen sich. E4 | Eine Größe darf nur eine Definition haben | `required_width` aus D-Mindestprofil ableiten: GOW50 17,00 m (Bus 17,50), ETW30 9,75 m |
| F06 | R C-G30-02 | 1, 10, 12 | FS | hoch | Jeder vorhandene Radweg macht 50 „sicher gestaltbar“, auch Hamburger Hochbordradwege mit 1,0–1,6 m. | CROW-Auslöser b fragt, ob ein ausreichender Radweg realisierbar ist, nicht ob irgendeiner existiert; Ist-Breite ist in OSM nur auf 119 km bekannt | Bedingung nur über Raum: `width_p10_m < required_width.GOW50`; vorhandener Radweg nur, wenn Breite ≥ Untergrenze bekannt |
| F07 | R C-G30-01 (`sensitive_radius` 150 m), H-STR-01 (4) | 1, 12, 11 | RW, FS | hoch | Jede Schule oder Kita im Umkreis 150 m löst GOW30 aus; das trägt den Großteil der 61 % HVS-km als GOW30. (A4) | StVO § 45 (9) S. 4 Nr. 6 erlaubt Tempo 30 auf HVS im „unmittelbaren Bereich“ von Schulen/Kitas; Kitas sind in Hamburg sehr dicht verteilt | Auslöser auf Einrichtungen mit Zugang am Abschnitt (≤ 50 m) begrenzen; Lückenschluss bis 500 m in H-STR-01 (Fassung StVO prüfen). Entschieden: Q2 b |
| F08 | D J-10 (`any+SW` → `grade_separated_cycle`) | 1, 8 | FS | hoch | Jedes Rampenende einer Autobahn oder Kraftfahrstraße wird als planfreie Radquerung gefordert (N6 zählt 50 SW–GOW50-Knoten); Ist ist dort immer „Handlungsbedarf“. | Rampenknoten sind plangleiche Knoten mit LSA oder Kreisel; planfreie Radquerung nur bei Hauptroute sinnvoll | J-10 teilen: Rampe (`*_link`) + GOW → Regeln J-01; planfrei nur \`cycle\_path(RSV |
| F09 | R N6 (node\_types, ist\_check, signal\_radius\_m); D junctions, J-M-06 | 6, 2 | LF | hoch | Soll-Knotentyp wird zweimal mit verschiedenem Vokabular und verschiedener Ist-Logik bestimmt (N6: GOW30+GOW30 immer Kreisel, Ampel „any within 30 m“; J-03 mit DTV-Grenzen, Ampel „nearest“). | Zwei Wahrheiten für dieselbe Frage; Steckbrief und Kohärenzbericht widersprechen sich | N6 liest `junction_type_soll` aus c07 und meldet nur noch Abweichungen; `node_types` streichen |
| F10 | D decision\_table, J-M-05 | 4 | LF | hoch | `no_rule` für \`cycle\_path(BASIS | ERSCHL)+GOW50` ,  `cycle\_path(ERSCHL)+ETW30\` (412 Knoten); SW-Paare nur über J-10. | Jeder Knoten braucht einen definierten Typ |
| F11 | D PRF-03 (`parking_positions`); R requirements.GOW50.parking\_along\_carriageway, GOW30.parking\_on\_carriageway, D-DES-01 | 2, 7, 12 | LF | hoch | Soll-Profil baut Längsparken an GOW50 und auf der Fahrbahn der GOW30, wo es heute Parken gibt; dieselbe Gestaltung zählt D-DES-01 als Verstoß. | Soll darf nicht verletzen, was die Kategorie verbietet | Parken nur nach Kategorie: GOW50 keins, GOW30 nur Parkstreifen mit Trennstreifen, ETW30 wie Ist |
| F12 | C cycle\_categories.RSV, C-NET-06 | 1, 5 | RW, FS | hoch | RSV = Korridorlauf ≥ 2 000 Rad/Werktag (Modell) und ≥ 5 km; Kalibrierung Spearman 0,56, 52 % innerhalb Faktor 2. | FGSV-Hinweise zu Radschnellverbindungen setzen u. a. ca. 10 km Länge an (A5); absolute Schwelle auf schwach kalibrierte Modellwerte macht RSV-Zuordnung instabil | Kategorie umbenennen („Radvorrangroute / Radroute+“) oder FGSV-Kriterien übernehmen; RSV nur mit Sensitivitätsband |
| F13 | R scores.conn\_score (in\_hvs 0,25), C-GOW-01 | 6, 8, 11 | LF, FS | mittel | in\_hvs wirkt doppelt: als eigener Auslöser und im Score. Für Nicht-HVS liegt das erreichbare Maximum bei 0,69; conn\_gow 0,6 verlangt dort faktisch Spitzenwerte (≈ oberste 13 %) bei Betweenness und Bus. | Rechnung: Gewichte ohne DTV 0,35/0,25/0,20 → umgelegt 0,44/0,31/0,25, in\_hvs = 0 | in\_hvs aus dem Score nehmen und conn\_gow so kalibrieren, dass Nicht-HVS-GOW-km gleich bleiben; entschieden: Q3 b |
| F14 | R C-CONF-01, C-MISS-01 | 11 | FS | mittel | 89 % der Länge „mittel“, weil Defaults ohne jede Datenquelle (Ortsgrenze, Schulstraße) jeden Abschnitt herabsetzen. | Eine überall gleiche Einschränkung unterscheidet nichts | Strukturelle Defaults als globalen Vorbehalt führen, nicht je Abschnitt |
| F15 | C separation\_matrix.ETW\_ERF.HAUPT, C-NET-03 soll\_factors.ETW\_ERF | 9, 10 | RW, FS | mittel | Hauptrouten laufen im Mischverkehr durch Fußgängerzonen und verkehrsberuhigte Bereiche; Soll-Widerstand 1,05 ignoriert Schrittgeschwindigkeit. | StVO: Schrittgeschwindigkeit, Fußverkehr vorrangig; widerspricht HAUPT-Zielgeschwindigkeit 20 km/h | HAUPT wie RSV: preferred own\_path; Soll-Faktor ETW\_ERF ≈ 2,1 (15/7 km/h) |
| F16 | C C-NET-03 soll\_factors | 7, 9 | LF | mittel | Soll-Widerstand nach Kategorie, nicht nach Soll-Führung: GOW30-Hauptroute (Soll Radweg) wird mit 1,25 statt 1,0/1,1 gerechnet. | Soll-Netz bestraft Korridore, die laut Matrix getrennt ausgebaut würden | Faktor aus der `preferred`-Führung der Matrixzelle ableiten |
| F17 | D degrade\_cascade D1/D2/D3, PRF-06 | 2, 12 | LF, FS | mittel | D2 reduziert Bäume auf „Baumscheiben in der Parkreihe“, die D1 schon entfernt hat; Bäume fallen vor dem zweiten Kfz-Fahrstreifen (D3). | Widerspricht „so wenige Fahrstreifen wie möglich“; Bestandsbäume sind kein frei verfügbarer Raum | D3 vor D2; D2 als „Baumscheiben im Trennstreifen“; Bestandsbäume nur Flag. Entschieden: Q1 b |
| F18 | C project\_target.cycle\_street\_carriageway 4,00; D ETW30\_mixed 4,75, PRF-04 | 7, 9 | LF | mittel | Fahrradstraße (Kfz frei) ist schmaler als eine gewöhnliche Quartiersstraße; Begegnung Lkw/Pkw nicht möglich. | RASt 06 Bild 17 (laut D, am Original prüfen) | Fahrbahn Fahrradstraße = max(4,00; ETW30\_mixed) bei Kfz frei |
| F19 | C C-FAC-02, C-FAC-03 (`dtv_missing_counts_as_met`) | 4, 9, 11 | FS | mittel | Kfz-DTV fehlt auf 99,9 % der ETW30; Fahrradstraßen- und S-04-Prüfung sind dort faktisch aus; 1 423 km Soll-Fahrradstraße ungeprüft. | Ohne Proxy keine Aussage, ob Filter nötig sind | Proxy: N4-Schleichverkehrsflag oder Betweenness-Perzentil → Flag `filter_needed` statt „erfüllt“ |
| F20 | C C-FAC-04 floor (separated\_twoway, own\_path) | 1, 9 | RW | mittel | Untergrenze einseitiger Zweirichtungsradweg und eigener Trasse 2,00 m. | ERA unterscheidet einseitig (höher) und beidseitig (A6) | `de.separated_twoway.oneside_min` ergänzen und als floor nutzen |
| F21 | R D-DES-01 (Parallelroute), S-FEAT-11; C C-FAC-01 | 2, 7 | LF, FS | mittel | Diskrepanz akzeptiert jeden Radweg im 200-m-Puffer als Ersatz, Soll-Führung plant an GOW50 trotzdem Radwege; Puffer zu großzügig (Parkweg). | Parallelroute ersetzt nur, wenn sie Ziele bedient und direkt ist | Parallel nur Radnetz HAUPT/BASIS mit Umweg ≤ P-DIR-01; in C-FAC-01 gleich auswerten |
| F22 | R requirements.GOW50.cycling (`separated_mandatory_track_or_parallel_route`) | 1 | RW, FH | mittel | Benutzungspflicht ist eine Anordnung nach § 45 (9) StVO, kein Gestaltungsmerkmal. | VwV-StVO zu § 2 Abs. 4 | Wert `separated_track_or_parallel_route`, Benutzungspflicht nicht Gegenstand |
| F23 | R categories, C-SW-01 | 8, 4 | FS | mittel | Anbaufreie Hauptverkehrsstraßen innerorts mit 60/70 km/h (RIN VS II–III), die keine Kraftfahrstraße sind, werden GOW50 mit Gehwegüberfahrten und Tempo-Diskrepanz. | RIN unterscheidet anbaufrei/angebaut | Attribut `anbaufrei` und Flag; keine Kategorie (entschieden: Q4 a) |
| F24 | D JC-04 median\_width\_m; J-M-05 fallback\_if | 4, 1 | LF | mittel | JC-04 gilt für RSV, `median_width_m` kennt RSV nicht; Turbokreisel nutzt denselben Platzradius wie der einstreifige. | Fehlender Wert bzw. zu kleiner Platz | RSV 4,00 m; `turbo_min_radius` ergänzen |
| F25 | R C-G30-01 (`crossing_demand`), scores.place\_score | 4, 6 | LF | mittel | `crossing_demand` ist nie bewertet, `place_score` ist definiert, aber von keiner Regel gelesen. | Totes Kriterium und tote Größe; guide 1.2 sieht zwei Scores vor | `crossing_demand` = high bei `place_score >= thresholds.place_high`, zurückgestellt; bis zur Kalibrierung `status: inactive` (Q2 b) |
| F26 | R S-FEAT-10; C C-PRI-02, C-FAC-05 | 7 | LF | mittel | Drei Definitionen von „Ist-Radweg“ (Diskrepanz, Führung, Prinzipien). E9 | Gleicher Abschnitt kann je Ebene anders bewertet werden | Eine Ist-Führung je Abschnitt in einer Stufe berechnen, alle lesen sie |
| F27 | R feasibility\_classes; C intensity\_classes, intensity\_upgrade | 5 | LF | gering | Intervallgrenzen doppelt belegt (0,85; 1,00; 150; 750). | ≥/> nicht festgelegt | Halboffene Intervalle `[min, max)` vereinbaren |
| F28 | R C-RUR-01; C separation\_matrix.rural; R N5 (GOW80) | 4, 6 | FH | gering | Außerorts-Zweig ist ohne Datenquelle tot; C-RUR-01 ignoriert in\_hvs. E8 | Totes Regelwerk erzeugt Scheinvollständigkeit | `status: inactive`; bei Aktivierung `or in_hvs` |
| F29 | R C-ERF-01 vor C-GOW-01 | 3 | LF | gering | HVS kann ETW\_ERF werden (7 Fälle per Override gelöst). | Reihenfolge bleibt für künftige Daten offen | Validierungsregel V-CONS-01 statt Regeländerung |
| F30 | R N7, H-STR-01 | 6 | FH | gering | N7 schlägt Glättung vor, die H-STR-01 schon angewandt hat. | Redundanz | N7 auf gesperrte Kategorien beschränken |
| F31 | R S-FEAT-04, S-FEAT-08 (note) | – | FH | gering | Notizen „liegt noch nicht in data/raw“ sind veraltet (Zensus, GTFS werden genutzt). | Dokumentation | Notizen aktualisieren |
| F32 | R requirements; C widths\_m | 6, 7 | FH | gering | Breiten doppelt geführt (Radfahrstreifen 1,70/2,20 und 1,85; Radweg 2,00). | Eine Quelle der Wahrheit | `requirements` verweist per Pfad auf `widths_m` |
| F33 | D PL-02, PRF-07; C S-03 | 6 | FH | gering | Innerorts vergibt die Matrix nie `separated_twoway`; PL-02/S-03 greifen nur außerorts. | Totes Regelwerk | als außerorts kennzeichnen |
| F34 | C C-IMP-06 | 9 | FH | gering | Kein Faktor für Hauptstraße T30 ohne Radstreifen (bekannt). | – | eigener Faktor 1,35 (Annahme) |
| F35 | D L-02 | 5 | – | Hinweis | Schwelle entspricht ≈ 13 900 Kfz/24h (765 / 0,055); plausibel für LSA-Strecken. | HBS prüfen | keine Änderung |
| F36 | D J-07 | 1 | RW | Hinweis | Vorfahrt der Fahrradstraße braucht Beschilderung; in Tempo-30-Zonen gilt grundsätzlich rechts vor links. | VwV-StVO zu § 45, Fassung prüfen | Notiz ergänzen |
| F37 | D roundabout\_max\_dtv | 1 | – | Hinweis | 25 000 Kfz/24h ist gängiger Faustwert für einstreifige Kreisel; Rad-Vorrang mindert Leistungsfähigkeit. | Merkblatt Kreisverkehre (FGSV) | Abschlag bei hohem Radverkehr prüfen |
| F38 | R N4 | 8 | – | Hinweis | Gleiches Soll-Tempo GOW30/ETW30 macht N4 unscharf (bekannt, Prompt 22). | – | Widerstandsfaktor statt Tempo |

## 5. Änderungsvorschläge

Je Befund ab „mittel“ ein konkreter Vorschlag; IDs und Struktur bleiben erhalten, neue Werte sind `source_type: assumption` und `status: draft`. Jede Übernahme braucht neue `meta.version`, CHANGELOG-Eintrag und grünes `make test`. Die Vorschläge sind gegeneinander geprüft; verbleibende Wechselwirkungen stehen jeweils unter „Auswirkungen“.

### F01 – GOW30 über dem CROW-Profil (kritisch)

Datei/Regel: cycling\_rules.yaml `separation_matrix.GOW30`, C-FAC-01; design\_rules.yaml PRF-04, neue L-07.

Bisher:

```yaml
  GOW30:
    RSV: separated_oneway_both
    HAUPT: {preferred: separated_oneway_both, fallback: cycle_lane}
    BASIS: cycle_lane
    ERSCHL: cycle_lane
    none: cycle_lane
```

Vorschlag:

```yaml
  GOW30:
    RSV: separated_oneway_both
    HAUPT: {preferred: separated_oneway_both, fallback: cycle_lane}
    BASIS: cycle_lane
    ERSCHL: cycle_lane
    none: cycle_lane
    high_volume:   # vor der Radkategorie, wenn dtv_official > rules.yaml requirements.GOW30.profiles.wide.max_dtv
      all: separated_oneway_both
      fallback: null          # kein Rückfall auf Radfahrstreifen
      flag: gow30_high_volume
      source: CROW_GOW30_2023
      source_type: swov_crow
      note: 'CROW: über 10 000 Kfz/Tag nur Profil mit Radweg (requirements.GOW30.profiles.track)'
# design_rules.yaml lanes.rules
    - id: L-07
      status: draft
      rule: 'GOW30: Flag capacity_reduction_needed, wenn peak_h_dir > lane_capacity_veh_h * target_vc (Werte aus L-02); reduction_dtv = DTV - (lane_capacity_veh_h * target_vc / peak_h_dir_from_dtv.factor)'
      source_type: assumption
```

PRF-04 ergänzen: „GOW30 mit `gow30_high_volume`: Fahrbahn = `requirements.GOW30.profiles.track.carriageway_min_m`, Radwege nach PL-01.“

Begründung: Die Entscheidung „Umfeld vor Verkehrsmenge“ bleibt unberührt; korrigiert wird nur die Führungsform, die bei hoher Belastung sicher sein muss. CROW sieht für GOW30 über 10 000 Kfz/Tag ausdrücklich das Profil mit Radweg vor. L-07 setzt E2 Option C als Rechenregel um (Reduktionszahl). Bei 0,85 × 900 / 0,055 liegt die Grenze bei rund 13 900 Kfz/Tag je Fahrstreifen und Richtung.

Auswirkungen: GOW30 mit hoher Belastung braucht mehr Breite, „passt nicht“ steigt dort; ohne Platz greift D6 (Verkehrsmenge senken), was der Intention entspricht. C-PRI-03 und C-FAC-06 brauchen keine neuen Einträge. D-USE-01 bleibt, sein Verweis auf Profil `track` wird erst mit Soll-Radweg schlüssig.

### F02 – Rad-Vorrang am Turbokreisverkehr (kritisch)

Datei/Regel: design\_rules.yaml JC-01, neue JC-06.

Bisher:

```yaml
    - {id: JC-01, ..., applies_to: [{types: [roundabout_single_lane_cycle_priority, turbo_roundabout]}]}
```

Vorschlag:

```yaml
    - {id: JC-01, ..., applies_to: [{types: [roundabout_single_lane_cycle_priority]}]}
    - {id: JC-06, rule: 'Turbokreisverkehr: umlaufender Radweg abgesetzt, Radverkehr wartepflichtig; im RSV/HAUPT-Netz planfreie Querung prüfen (Flag turbo_grade_sep_check)', source_type: assumption, status: draft,
       applies_to: [{types: [turbo_roundabout]}]}
```

Begründung: An zweistreifigen Ein- und Ausfahrten verdeckt ein Fahrzeug das andere; bevorrechtigte Radfahrende werden übersehen. Annahme A3. Der Typ `roundabout_single_lane_cycle_yield` bleibt für außerorts reserviert.

Auswirkungen: Nur Steckbrieftext und `cyclist_treatment`; P-DIR-02 zählt an Turbokreiseln künftig einen Halt (C-PRI-05 nach Prompt 23).

### F03 – Hauptroute quert GOW50 ohne Signal (kritisch)

Datei/Regel: design\_rules.yaml decision\_table, J-M-05; entspricht E5 b mit Bedingung.

Bisher: J-04 `GOW50+ETW30` → `continuous_footway_exit`, auch wenn auf dem ETW30-Arm eine Hauptroute die GOW50 quert.

Vorschlag:

```yaml
      - {id: J-14, legs: 'GOW50+ETW30', cycle_crossing: [RSV, HAUPT, BASIS],
         if: 'lanes_per_direction_max >= 2 or entering_dtv_sum > crossing_signal_min_dtv',
         then: cycle_crossing_signal, otherwise: continuous_footway_exit,
         note: 'Radroute quert den Zug (Arme beidseits außerhalb des Zugs in der Radkategorie); sonst J-04', status: draft}
  thresholds:
    crossing_signal_min_dtv: {value: 12000, source_type: assumption, note: 'Summe Zufluss; ≈ 1 200 Kfz/h bei 10 % Spitzenstunde, zweistufige Querung über Mittelinsel bis etwa dahin'}
# J-M-05
      evaluation_order: [J-10, J-11, J-09, J-08, J-12, J-07, J-13, J-14, J-01, J-02, J-03, J-04, J-05, J-06]
```

Begründung: Querungen von zwei Fahrstreifen je Richtung ohne Signal sind ein bekannter Unfalltyp (zweites Fahrzeug verdeckt). JC-04 (Mittelinsel) bleibt für den `otherwise`-Fall.

Auswirkungen: Mehr LSA im Soll, mehr Halte im Radnetz (P-DIR-02); J-14 braucht `lanes_per_direction_max` am Knoten aus PRF-01 (Soll).

### F04 – Doppelzählung Radfahrstreifen im GOW30-Profil (hoch)

Datei/Regel: design\_rules.yaml PRF-04, `lane_width_m.GOW30_*`. Annahme A2.

Bisher (PRF-04): „GOW30 = untere Grenze von GOW30\_narrow\_profile …; Radfahrstreifen kommen zur GOW30-Fahrbahn hinzu“.

Vorschlag:

```yaml
    GOW30_narrow_profile: {carriageway_range: [5.80, 8.40], max_dtv: 6000, includes_cycle_lanes: true, ...}
    GOW30_wide_profile:   {carriageway_range: [8.40, 10.70], max_dtv: 10000, includes_cycle_lanes: true, ...}
# PRF-04, Text GOW30 neu:
#   GOW30 mit Radfahrstreifen = max(untere Profilgrenze, Kernfahrbahn + 2 x Radfahrstreifen-Sollbreite);
#   Kernfahrbahn schmales Profil <= requirements.GOW30.profiles.narrow.centre_runner_max_m, Bereich avoid_runner_m meiden
#   (sonst breites Profil mit Kernfahrbahn >= 4,80 m). GOW30 mit Radweg: profiles.track.carriageway_min_m.
```

Beispiel: BASIS 3,80 + 2 × 2,25 = 8,30 m (schmal); HAUPT-Fallback 4,80 + 2 × 2,50 = 9,80 m (breit). Bisher 5,80 + 2 × 2,25 = 10,30 m.

Auswirkungen: GOW30-Profile werden rund 2–4,5 m schmaler, D6-Flags sinken; rules.yaml `required_width.GOW30_*` (10,80–13,40 m) rechnet bereits so und wird dadurch konsistent.

### F05 – Eine Machbarkeitsrechnung (hoch)

Datei/Regel: rules.yaml `required_width`; Zusammenhang E4.

Bisher:

```yaml
  GOW50: {value: 16.50, formula: "2*sidewalk + 2*cycle_track + 2*0.50 + carriageway_2lane", source_type: assumption}
  GOW50_bus: {value: 17.00, source_type: assumption}
  ETW30: {value: 10.80, source_type: assumption}
```

Vorschlag:

```yaml
  GOW50: {value: 17.00, source_type: assumption,
          formula: "2*D.elements_min_m.sidewalk.min + 2*C.widths_m.de.separated_oneway.standard + 2*D.elements_min_m.buffer_cycle_carriageway + D.lane_width_m.GOW50_2x1_carriageway.value"}
  GOW50_bus: {value: 17.50, source_type: assumption, formula: "wie GOW50 mit D.lane_width_m.GOW50_bus_carriageway.value"}
  ETW30: {value: 9.75, source_type: assumption, formula: "2*D.elements_min_m.sidewalk.min + D.lane_width_m.ETW30_mixed.value"}
```

Dazu ein Schema-Test: `value` muss der berechneten `formula` entsprechen. Begründung: Die Klassifikation fragt „ist ein sicherer Radweg überhaupt möglich“ (Mindestprofil mit ERA-Regelmaß), das Soll-Profil startet mit Regelmaßen und baut bis D4 ab. Damit gilt: passt GOW50 in S-XS-06, passt das c06-Profil spätestens nach D4.

Auswirkungen: Schwelle C-G30-02 steigt um 0,50 m (69 Abschnitte liegen heute ± 10 % an der Schwelle); V-SENS-01 neu rechnen.

### F06 – C-G30-02 ohne Ist-Radweg (hoch)

Datei/Regel: rules.yaml C-G30-02; beantwortet zugleich die offene Frage GOW50\_bus.

Bisher:

```yaml
    if: "not separated_cycle_track_present and width_p10_m < required_width.GOW50"
```

Vorschlag:

```yaml
    if: "(not bus_route and width_p10_m < required_width.GOW50) or (bus_route and width_p10_m < required_width.GOW50_bus)"
    note: "bus_route = bus_per_peak_h_dir >= 1 (PRF-02). Ein vorhandener Radweg zählt nicht; Flag existing_track_below_floor, wenn Ist-Breite bekannt und < C-FAC-04 floor"
```

Begründung: CROW-Auslöser b fragt nach der Realisierbarkeit eines ausreichenden Radwegs. Ein schmaler Bestandsradweg in zu engem Raum belegt das Gegenteil.

Auswirkungen: Mehr GOW30 auf engen Straßen mit Altradweg; Umfang per Probelauf bestimmen. Goldene Fälle mit `separated_cycle_track_present: true` und schmalem Raum anpassen.

### F07 – Schul-/Kita-Auslöser (hoch, entschieden: Q2 b)

Datei/Regel: rules.yaml C-G30-01, H-STR-01. Annahme A4.

Bisher:

```yaml
    if: "schools_or_kitas_within_m <= thresholds.sensitive_radius or shop_frontage_share >= thresholds.frontage or crossing_demand == high"
      sensitive_radius: {value: 150, unit: m, source_type: assumption}
```

Vorschlag:

```yaml
    if: "school_or_kita_access_m <= thresholds.access_radius or shop_frontage_share >= thresholds.frontage or crossing_demand == high"
      access_radius: {value: 50, unit: m, source_type: assumption,
                      note: "Abstand Grundstück der Einrichtung (allgemeinbildende Schule, Kita) zum Abschnitt; StVO § 45 (9) S. 4 Nr. 6 'unmittelbarer Bereich'"}
# H-STR-01
      gap_close_m: {value: 500, unit: m, source_type: de_regelwerk, note: "Lückenschluss zwischen Tempo-30-Strecken (StVO-Novelle 2024, Fassung prüfen); ersetzt min_run_from N2 für Regel (4)"}
```

Begründung: Der Auslöser wird damit rechtlich anschlussfähig, und H-STR-01 schließt Abschnitte zwischen zwei Einrichtungen zu einer durchgehenden GOW30 zusammen, wie es die StVO für Tempo 30 auf HVS erlaubt.

Auswirkungen: GOW30-Anteil der HVS-km sinkt, Top 30 der Priorität ändern sich; `sensitive_radius` bleibt für P-RISK-01 (`school_kita_radius_m`) erhalten.

### F08 – Rampenknoten (hoch)

Datei/Regel: design\_rules.yaml J-10.

Bisher:

```yaml
      - {id: J-10, legs: 'any+SW', then: grade_separated_cycle, status: draft}
```

Vorschlag:

```yaml
      - {id: J-10, legs: 'cycle_path(RSV|HAUPT)+SW', then: grade_separated_cycle, status: draft}
      - {id: J-10b, legs: 'SW+GOW50|GOW30', same_as: J-01, note: 'Rampenknoten (*_link) plangleich; Radquerung nach JC-02/JC-03', status: draft}
      - {id: J-10c, legs: 'SW+ETW30|ETW_ERF', then: signal_protected, note: 'Rampe an Erschließungsstraße, Flag N5 sw_to_etw', status: draft}
      - {id: J-10d, legs: 'SW+SW|cycle_path(BASIS|ERSCHL)+SW', then: not_applicable, note: 'Autobahnknoten ohne Rad-/Fußverkehr; BASIS-Weg an SW: Lage prüfen', status: draft}
```

`not_applicable` in `types` und `ist_check` (`ok: [roundabout, signal, signal_plateau, none_mapped]`) aufnehmen; `evaluation_order` beginnt mit J-10, J-10d, J-10c, J-10b.

Auswirkungen: Weniger planfreie Querungen im Soll; Prioritätsliste J-M-07 verliert unbegründete Einträge.

### F09 – Ein Soll-Knotentyp (hoch)

Datei/Regel: rules.yaml N6.

Vorschlag:

```yaml
  - id: N6
    rule: "Soll-Knotentyp aus design_rules.junctions (c07, junction_type_soll); N6 listet nur Knotenpunkte ohne Soll-Typ und Übergänge nach N5"
    source_of_truth: design_rules.junctions.decision_table
    category_rank: [SW, GOW80, GOW50, GOW30, ETW60, ETW30, ETW_ERF]   # bleibt, J-M-04 verweist darauf
    # node_types, ist_check, thresholds.signal_radius_m entfallen (0.17.0)
```

Auswirkungen: Der Kohärenzbericht liest das Ergebnis von c07; die N6-Spalten auf der Webseite entfallen. Reihenfolge der Stufen: N6-Teil des Berichts nach c07.

### F10 – Lücken der Knotentabelle (hoch)

Datei/Regel: design\_rules.yaml decision\_table, `types`.

Vorschlag:

```yaml
  types: [..., cycle_crossing_refuge]   # Rad wartepflichtig, Mittelinsel nach JC-04
      - {id: J-15, legs: 'cycle_path(BASIS|ERSCHL)+GOW50',
         if: 'lanes_per_direction_max >= 2 or entering_dtv_sum > crossing_signal_min_dtv',
         then: cycle_crossing_signal, otherwise: cycle_crossing_refuge, status: draft}
      - {id: J-16, legs: 'cycle_path(ERSCHL)+ETW30', then: equal_right_before_left,
         note: 'Rechtslage selbständiger Radweg an Straße prüfen (wie J-12)', status: draft}
# ist_check
        cycle_crossing_refuge: {ok: [], not_checkable: [none_mapped, plateau]}
```

Auswirkungen: `no_rule` sollte auf null fallen; Test „jeder Knotenpunkt hat einen Soll-Typ oder not\_applicable“ ergänzen.

### F11 – Parken im Soll-Profil nach Kategorie (hoch)

Datei/Regel: design\_rules.yaml PRF-03.

Vorschlag:

```yaml
      parking_positions: [lane, street_side, on_kerb, half_on_kerb, shoulder]
      parking_by_category:
        GOW50: none            # rules.yaml requirements.GOW50.parking_along_carriageway: false
        GOW30: [street_side]   # nur Parkstreifen mit buffer_to_parking; requirements.GOW30.parking_on_carriageway: false
        ETW30: as_ist
        ETW_ERF: none
```

Auswirkungen: GOW50-Profile passen häufiger, D1 wird dort wirkungslos; Ladezonen bleiben. Kein Widerspruch mehr zu D-DES-01.

### F12 – RSV-Kategorie (hoch)

Datei/Regel: cycling\_rules.yaml `cycle_categories.RSV`, C-NET-06. Annahme A5.

Vorschlag:

```yaml
  RSV:
    label_de: 'Radvorrangroute / Radroute+'
    fgsv_rsv_candidate: {rule: 'Lauf >= 10 km und cyc_calibrated >= demand_trigger_cyclists_weekday auf dem überwiegenden Teil', source_type: assumption,
                         note: 'FGSV-Hinweise zu Radschnellverbindungen am Original prüfen'}
# C-NET-06
      demand_band_factor: {value: 2.0, source_type: assumption,
                           note: 'RSV-Lauf mit cyc_calibrated < trigger x factor: rsv_confidence low (Kalibrierung: 52 % der Querschnitte innerhalb Faktor 2)'}
```

Auswirkungen: Keine Ergebnisänderung, aber ehrlichere Bezeichnung; Steckbrief zeigt FGSV-Kandidat und Unsicherheit.

### F13 – in\_hvs im conn\_score (mittel, entschieden: Q3 b)

Datei/Regel: rules.yaml `scores.conn_score`, C-GOW-01.

Bisher:

```yaml
    weights: {betweenness_norm: 0.35, in_hvs: 0.25, bus_trips_weekday_norm: 0.20, dtv_norm: 0.20}
```

Vorschlag:

```yaml
    weights: {betweenness_norm: 0.45, bus_trips_weekday_norm: 0.30, dtv_norm: 0.25, source_type: assumption}
    note: "in_hvs nur noch als eigener Auslöser in C-GOW-01; conn_gow neu kalibrieren: Ziel Nicht-HVS-GOW-km etwa wie Lauf 0.16.0 (78 km), dann Stichprobe"
```

Begründung: Heute rechnet der Score für Nicht-HVS mit einem festen Abzug (in\_hvs = 0); die Schwelle 0,6 bedeutet dort etwas anderes als auf HVS. Der Probelauf vom 07.11. (430 km mehr GOW bei unverändertem conn\_gow) zeigt, dass die Schwelle mitgezogen werden muss.

Auswirkungen: V-SENS-01 und V-UNC-01 neu; die Wirkung von conn\_gow wird erstmals fachlich lesbar („oberste x % nach Durchgang und Bus“).

### F14 – confidence mit Aussagekraft (mittel)

Datei/Regel: rules.yaml C-CONF-01.

Vorschlag (Ergänzung):

```yaml
    global_caveats: [outside_builtup_area, override_school_street, crossing_demand, in_hvs, schools_or_kitas_within_m]
    global_caveats_note: "Defaults und Fallbacks, die für alle Abschnitte gleich gelten, senken confidence nicht; sie stehen einmal im Steckbrief und auf der Methodenseite"
```

Auswirkungen: confidence unterscheidet dann nach fehlenden Werten, Nähe zur Schwelle, umgelegtem Gewicht (conn\_score) und Nachbarbreite; der Anteil „hoch“ steigt deutlich. Goldene Fälle zur confidence anpassen.

### F15 – Hauptrouten durch Fußgängerzonen (mittel)

Datei/Regel: cycling\_rules.yaml `separation_matrix.ETW_ERF`, `routing_impedance.factors`, C-NET-03, C-IMP-04.

Vorschlag:

```yaml
  ETW_ERF:
    RSV: {preferred: own_path, fallback: mixed, note: 'RSV möglichst nicht durch Fußgängerzonen'}
    HAUPT: {preferred: own_path, fallback: mixed, flag: haupt_through_pedestrian_area}
  factors:
    walking_pace_area: 2.1   # 15 km/h / 7 km/h; assumption
  # C-NET-03 soll_factors: ETW_ERF: walking_pace_area
  # C-IMP-04: living_street und pedestrian mit Faktor walking_pace_area statt etw30_mixed
```

Auswirkungen: Netzentwurf (c03) und Umlegung neu; Hauptrouten weichen Fußgängerzonen aus, wo eine Alternative besteht.

### F16 – Soll-Widerstand nach Soll-Führung (mittel)

Datei/Regel: cycling\_rules.yaml C-NET-03.

Vorschlag:

```yaml
      soll_factor_by_facility: {separated_oneway_both: gow50_separated_track, separated_twoway: gow50_separated_track,
                                cycle_lane: gow30_cycle_lane, cycle_street: separated_track_or_cycle_street,
                                mixed: etw30_mixed, own_path: separated_track_or_cycle_street}
      facility_level_note: 'Führung = preferred der Matrixzelle für die Ebene, die gerade entworfen wird (HAUPT-Zelle für RSV/HAUPT, BASIS-Zelle für die Verdichtung)'
```

Auswirkungen: GOW30-Korridore werden für das Hauptnetz günstiger; Netzentwurf neu rechnen.

### F17 – Abbaureihenfolge (mittel, entschieden: Q1 b)

Datei/Regel: design\_rules.yaml `degrade_cascade_if_not_fit` D2, PRF-06.

Bisher:

```yaml
    - {step: D2, action: 'Baumstreifen auf Baumscheiben in Parkreihe reduzieren'}
      cascade_order: [D1, D2, fallback, D3, D4, D5, D6, D7]
```

Vorschlag:

```yaml
    - {step: D2, action: 'Neuen Baumstreifen auf Baumscheiben im Trenn- oder Seitenraum reduzieren; Bestandsbäume nicht entfernen (Flag existing_trees_conflict, sobald Baumdaten vorliegen)'}
      cascade_order: [D1, D3, D2, fallback, D4, D5, D6, D7]
```

Begründung: D1 entfernt die Parkreihe, in die D2 heute die Baumscheiben legt. Und „so wenige Fahrstreifen wie möglich“ verlangt, dass der zweite Kfz-Streifen vor dem Grün fällt.

Auswirkungen: Nur GOW50 mit zwei Fahrstreifen je Richtung betroffen; mehr Profile ohne zweiten Fahrstreifen, weniger Baumverluste.

### F18 – Fahrbahn der Fahrradstraße (mittel)

Datei/Regel: cycling\_rules.yaml `widths_m.project_target.cycle_street_carriageway`; design\_rules.yaml PRF-04.

Vorschlag:

```yaml
    cycle_street_carriageway: {value: 4.00, with_motor_traffic: 4.75,
      note: 'Kfz frei: mindestens design_rules lane_width_m.ETW30_mixed (Begegnung Lkw/Pkw); ohne Kfz 4,00 m'}
```

Auswirkungen: Fahrradstraßen-Profile 0,75 m breiter; C-PRI-08 `required_by_facility.cycle_street` liest künftig `with_motor_traffic`.

### F19 – Fahrradstraße ohne Kfz-Zählung (mittel)

Datei/Regel: cycling\_rules.yaml C-FAC-02, C-FAC-03.

Bisher:

```yaml
      dtv_missing_counts_as_met: true
```

Vorschlag:

```yaml
      dtv_missing_counts_as_met: true
      dtv_proxy:
        rule: 'DTV fehlt und (Flag N4_shortcut oder betweenness_norm >= proxy_betweenness): Bedingung unbekannt, Flag filter_needed („Durchgangsverkehr wahrscheinlich, Filter prüfen“)'
        proxy_betweenness: {value: 0.8, source_type: assumption}
```

Begründung: Die Entscheidung vom 06.11. (schwach belastet bis zum Beweis des Gegenteils) bleibt, aber Abschnitte mit klaren Hinweisen auf Durchgangsverkehr werden sichtbar. Die VwV-StVO zu Z. 244.1 lässt Fahrradstraßen auch bei hoher Netzbedeutung zu; die Spitzenstunden-Bedingung ist strenger als nötig (Fassung prüfen, Annahme A7).

Auswirkungen: Neues Flag im Steckbrief, Liste für modale Filter; keine Kategorieänderung.

### F20 – Untergrenze einseitiger Zweirichtungsradweg (mittel)

Datei/Regel: cycling\_rules.yaml `widths_m.de.separated_twoway`, C-FAC-04 `floor`. Annahme A6.

Vorschlag:

```yaml
    separated_twoway: {standard: 2.50, min: 2.00, oneside_standard: 3.00, oneside_min: 2.50}
  # C-FAC-04
      floor: {separated_oneway_both: de.separated_oneway.min, separated_twoway: de.separated_twoway.oneside_min,
              cycle_lane: gow30_cycle_lane.min, own_path: de.separated_twoway.oneside_min}
```

Auswirkungen: Nur außerorts und eigene Trassen; D4 baut dort weniger weit ab.

### F21 – Parallelroute an GOW50 (mittel)

Datei/Regel: rules.yaml D-DES-01, S-FEAT-11.

Bisher:

```yaml
      - {check: cycling, requirement: separated_mandatory_track_or_parallel_route,
         violated_if: "not separated_cycle_track_present and not parallel_cycle_route_present", ...}
```

Vorschlag:

```yaml
      - {check: cycling, requirement: separated_track_or_parallel_route,
         violated_if: "not separated_cycle_track_present",
         severity_if: {parallel_cycle_route_present: 0.5},
         note: "Ziele liegen an der Magistrale (guide_radnetz 3.2): Parallelroute mildert, ersetzt aber nicht"}
# S-FEAT-11
      qualifying_cycle_categories: [RSV, HAUPT, BASIS]   # Soll-Radnetz statt jeder Weg mit Radfreigabe
```

Auswirkungen: Mehr GOW50-Diskrepanzen „kein baulicher Radweg“; D-DES-01 und C-FAC-01 erzählen dieselbe Geschichte. `severity_if` braucht eine kleine Erweiterung in s08.

### F22 – Benutzungspflicht (mittel)

Datei/Regel: rules.yaml `requirements.GOW50.cycling`.

Vorschlag:

```yaml
    cycling: {value: separated_track_or_parallel_route, source: CROW_GOW30_2023, source_type: swov_crow,
              note: "Benutzungspflicht ist eine Anordnung (§ 45 Abs. 9 StVO, VwV zu § 2 Abs. 4), nicht Gegenstand des Plans"}
```

Auswirkungen: Wert muss in D-DES-01 `requirement` gleich lauten (siehe F21).

### F23 – Anbaufreie Hauptverkehrsstraßen (mittel, entschieden: Q4 a)

Datei/Regel: rules.yaml `features`, neue S-FEAT-12.

Vorschlag:

```yaml
    - id: S-FEAT-12
      description: "anbaufrei: Anteil der Abschnittslänge ohne Gebäude (ALKIS, S-FEAT-03) und ohne Einmündung im Puffer buffer_m >= min_share"
      thresholds:
        buffer_m: {value: 30, unit: m, source_type: assumption}
        min_share: {value: 0.8, unit: "Anteil 0-1", source_type: assumption}
      source_type: assumption
      status: draft
```

Nutzung zunächst nur als Flag `gow50_anbaufrei` im Steckbrief und in D-SPD-01 (Hinweis statt Stärke bei Ist 60). Keine eigene Kategorie (Q4 a, 08.11.2026).

### F24 – Mittelinsel RSV, Platz Turbokreisel (mittel)

Datei/Regel: design\_rules.yaml JC-04, J-M-05 `fallback_if`, `thresholds`.

Vorschlag:

```yaml
       median_width_m: {RSV: 4.00, HAUPT: 3.00, BASIS: 2.50}   # RSV: assumption (Lastenrad mit Anhänger)
    turbo_min_radius: {value: 30, unit: m, source_type: assumption, note: 'Turbokreisel mit Radring; am Original prüfen'}
# J-01 else_if: 'entering_dtv_sum <= turbo_max_dtv and space_radius_m >= turbo_min_radius'
```

Auswirkungen: Weniger Turbokreisel im Soll, mehr `signal_protected`.

### F25 – crossing\_demand und place\_score (mittel, entschieden: Q2 b)

Datei/Regel: rules.yaml C-G30-01, C-MISS-01, `scores.place_score`.

Vorschlag (Q2 b, 08.11.2026 – Auslöser vorerst stilllegen):

```yaml
# C-G30-01: Bedingung bleibt unverändert, der Teil crossing_demand ist bis auf Weiteres stillgelegt
# C-MISS-01 defaults:
      crossing_demand: {value: not_assessed, status: inactive,
                        note: "Q2 b (2026-11-08): place_score als Auslöser erst nach Kalibrierung an den E1-Stichproben prüfen"}
# scores.place_score:
    note: "derzeit von keiner Regel gelesen; Kandidat für crossing_demand (F25 Option a)"
```

Später (Option a): `crossing_demand` = high bei `place_score >= thresholds.place_high` (0,8, assumption), gemeinsam mit `access_radius` aus F07 an den E1-Stichproben kalibrieren. Auswirkungen jetzt: keine Ergebnisänderung; der tote Auslöser ist als solcher gekennzeichnet und zählt in Berichten nicht als abgedeckt.

### F26 – Eine Ist-Führung (mittel)

Datei/Regel: rules.yaml S-FEAT-10; cycling\_rules.yaml C-PRI-02, C-FAC-05; entspricht E9.

Vorschlag:

```yaml
    - id: S-FEAT-13
      description: "ist_facility je Abschnitt einmal berechnen (Regeln von C-FAC-05 inkl. begleitender Radwege je Seite, E9); separated_cycle_track_present = ist_facility in [separated_oneway_both, separated_twoway]; C-PRI-02 übernimmt ist_facility für Straßenkanten"
      source_type: assumption
      status: draft
```

Auswirkungen: Diskrepanz (s08) hängt dann vom Radgraphen ab; Stufenfolge s04 → c01 prüfen. Die 83 km „Tag ja, Radgraph nein“ werden in einer Liste sichtbar.

## 6. Strukturelle Empfehlungen

Der wichtigste strukturelle Schritt ist, Querbeziehungen zwischen den drei Dateien als ausführbare Invarianten zu prüfen; fast alle Befunde der Klassen „hoch“ und „mittel“ wären damit beim Commit aufgefallen.

**1. Eine Quelle für Maße.** Alle Breiten (Gehweg, Radweg, Trennstreifen, Fahrbahnen) stehen genau einmal, z. B. in design\_rules `elements_min_m` und cycling\_rules `widths_m`. `requirements.*` und `required_width.*` verweisen nur per Pfad und tragen eine `formula`, die der Schema-Test nachrechnet (F05, F32).

**2. Klassifikation und Querschnitt bewusst koppeln.** Die Klassifikation prüft mit dem Mindestprofil, der Soll-Querschnitt mit dem Regelprofil und baut bis zum Mindestprofil ab. Dann gilt die Implikation „passt in S-XS-06 ⇒ passt nach spätestens D4“, und D5 tritt nur noch bei Fahrstreifen- oder Busbedarf auf (Grundlage für E4 b).

**3. Gemeinsames Begriffsverzeichnis.** Ein Abschnitt `glossary` (oder `config/terms.yaml`) mit: Ist-Führung, Radweg, Kategorie-Codes (ETW\_ERF statt ETW-ERF in guide.md), DTV (Kfz/24 h, Querschnitt), Spitzenstunde (Anteil, je Richtung oder beide). Pflichtfeld `unit` für jeden Zahlenwert, auch `max_dtv`.

**4. Intervallkonvention.** Klassen sind halboffen `[min, max)`; der Validator prüft Lückenlosigkeit und Überlappungsfreiheit aller Klassentabellen (F27).

**5. Status `inactive`.** Regeln ohne Datengrundlage (C-RUR-01, außerorts-Matrix, PL-02, `crossing_demand` bis zur Entscheidung) erhalten `status: inactive`; Berichte zählen sie nicht als abgedeckt (F25, F28, F33).

**6. Ausführbare Invarianten (neuer Block `validation.invariants`).**

| ID | Invariante | Prüft Befund |
| --- | --- | --- |
| V-INV-01 | Jede `cat_final` hat eine Matrixzeile und Profilregel oder steht in `no_profile_categories` | F28 |
| V-INV-02 | Kein Knotenpunkt mit `no_rule` | F10 |
| V-INV-03 | Soll-Profil enthält kein Element, das `requirements[cat]` verbietet (Parken GOW50, Radfahrstreifen GOW50, Mittellinie GOW30) | F11 |
| V-INV-04 | Keine Soll-Führung `cycle_lane` an GOW30 mit DTV über `profiles.wide.max_dtv` | F01 |
| V-INV-05 | `fits` in S-XS-06 ⇒ c06 `fits` oder `fits_after_degrade` bis D4 | F05 |
| V-INV-06 | `value` = berechnete `formula` für alle `required_width.*` | F05 |
| V-INV-07 | Rad-Vorrang (`cyclist_treatment` JC-01) nur an einstreifigen Kreiseln | F02 |
| V-INV-08 | Ist-Führung in s08, c04 und c05 identisch | F26 |
| V-INV-09 | HVS nie ETW30/ETW\_ERF ohne approved Override (Test besteht, als Regel führen) | F29 |

**7. Testfälle für Grenzkonstellationen (goldene Fälle).**

| Fall | Eingang | Erwartung |
| --- | --- | --- |
| G01 | GOW30, BASIS, DTV 10 000 / 10 001 | `cycle_lane` / `separated_oneway_both` + `gow30_high_volume` |
| G02 | GOW-Kandidat, kein Bus, width\_p10 17,00 / 16,99 m | GOW50 / GOW30 |
| G03 | Bestandsradweg 1,20 m, width\_p10 15,0 m | GOW30 (C-G30-02) |
| G04 | Kita-Grundstück 50 / 51 m vom Abschnitt | GOW30 / weiter mit C-G30-02 |
| G05 | HAUPT auf ETW30 quert GOW50 2×2, Zufluss 8 000 Kfz/24h | `cycle_crossing_signal` (J-14) |
| G06 | Turbokreisel im HAUPT-Netz | JC-06, kein JC-01 |
| G07 | motorway\_link + GOW50, Zufluss 20 000 | `roundabout_single_lane_cycle_priority` bei Platz, sonst `signal_protected` |
| G08 | ERSCHL-Weg trifft ETW30 | `equal_right_before_left` (J-16) |
| G09 | HAUPT auf ETW\_ERF | `own_path` mit Flag `fallback_check_p19` |
| G10 | GOW50, DTV 13 900 / 14 000, Ist 2 Fahrstreifen | Soll 1 / 2 je Richtung (L-02) |
| G11 | width\_ratio 0,85 / 1,00 | `tight` / `fits` |
| G12 | GOW50 mit Ist-Parken | Soll-Profil ohne Parken |

**8. Stufenfolge.** N6-Bericht nach c07 (F09); `ist_facility` (S-FEAT-13) vor s08 und c04 (F26).

**9. Prüfreihenfolge im Regelregister.** Statt 176 Regeln gleichrangig zuerst die Werte mit der größten Wirkung: `conn_gow`, `sensitive_radius`/`access_radius`, `frontage`, `required_width.GOW50`, `elements_min_m.sidewalk.standard`, `cycle_street_carriageway`, `roundabout_max_dtv`, RSV-Auslöser, Maschenweiten. Das deckt sich mit E1 b (Prüflisten) und macht 10 h Prüfzeit wirksamer.

**10. Varianten als Schalter.** Die GOW30-Obergrenze (Variante „Kompromiss“) und künftige Wertentscheidungen (Q1–Q4) als benannte Schalter in rules.yaml führen, damit Ergebnisse vergleichbar bleiben (E15).

## 7. Getroffene Annahmen

Regelwerkswerte aus dem Gedächtnis sind als solche markiert und vor Übernahme am Original zu prüfen; ich hatte keinen Zugriff auf FGSV-Originale oder die CROW-Handreiking.

| Nr. | Annahme | Begründung | Betroffene Befunde |
| --- | --- | --- | --- |
| A1 | „Umfeld vor Verkehrsmenge“ (Entscheidung 07.11.) bleibt; Arbeitsbasis ist E2 Option C (Kennzeichnung „Reduktion nötig“). | Empfehlung der Entscheidungsvorlage; F01 korrigiert nur die Führungsform und gilt bei jeder E2-Option. | F01, F07 |
| A2 | Die CROW-Spannen 5,80–8,40 m und 8,40–10,70 m enthalten die Fietsstroken. | Abgeleitet aus `centre_runner_max_m` und `avoid_runner_m` in rules.yaml und aus `required_width.GOW30_*`, das ebenfalls so rechnet. Original nicht geprüft. | F04 |
| A3 | An Turbokreiseln führt die NL-Praxis Radfahrende wartepflichtig oder planfrei; in deutschen Regelwerken sind Turbokreisel kein Regelelement. | Fachpraxis; Quelle (CROW/Fietsberaad) ergänzen. | F02 |
| A4 | StVO § 45 (9) S. 4 Nr. 6 erlaubt Tempo 30 auf HVS im „unmittelbaren Bereich“ von Schulen und Kitas; die StVO-Novelle 2024 erlaubt Lückenschlüsse bis 500 m. | Aus dem Gedächtnis; Wortlaut und Fassung prüfen. 50 m ist eigene Setzung. | F07, F25 |
| A5 | Die FGSV-Hinweise zu Radschnellverbindungen und Radvorrangrouten setzen für RSV rund 10 km Länge und ≥ 2 000 Rad/24 h an. | Aus dem Gedächtnis; am Original prüfen. | F12 |
| A6 | ERA 2010: Mindestmaß einseitiger Zweirichtungsradweg höher als beidseitiger (2,50 gegen 2,00 m). | Aus dem Gedächtnis; am Original prüfen. | F20 |
| A7 | VwV-StVO zu Z. 244.1 lässt Fahrradstraßen seit 2021 auch bei hoher Netzbedeutung für den Radverkehr zu. | Aus dem Gedächtnis; Fassung prüfen. | F19, F36 |
| A8 | Neue Zahlenwerte sind eigene Setzungen: `crossing_signal_min_dtv` 12 000, `proxy_betweenness` 0,8, `place_high` 0,8, `turbo_min_radius` 30 m, Mittelinsel RSV 4,00 m, Faktor Schrittgeschwindigkeit 2,1, `access_radius` 50 m. | Plausible Startwerte, alle `assumption`, in V-SENS-01 aufnehmen. | F03, F07, F10, F15, F19, F24, F25 |
| A9 | Die E-Nummern ordne ich nur nach den Titeln in entscheidungen.md zu; optionen.md lag nicht vor. | Datei fehlte im Material. | Spalte „E“ in Abschnitt 4 |
| A10 | Das Verhalten der Pipeline leite ich aus den Regeltexten und Berichten ab; der Code wurde nicht gelesen. | Material umfasst nur YAML und md. | F09, F16, F26 |
| A11 | Mengenangaben (362 km GOW30 über Profil, 61 % HVS-km als GOW30, 1 423 km Soll-Fahrradstraße, 412 Knoten ohne Regel) stammen aus open\_questions.md und classification.md. | Nicht nachgerechnet. | F01, F07, F10, F19 |

## 8. Entscheidungen zu den offenen Fragen

Alle vier Fragen sind am 08.11.2026 entschieden, jeweils für die empfohlene Option (Q1 b, Q2 b, Q3 b, Q4 a). Damit sind alle Vorschläge aus Abschnitt 5 umsetzungsreif; nur der Auslöser `place_score` (F25 Option a) bleibt bis zur Kalibrierung an den E1-Stichproben zurückgestellt. Die Fragen stehen unten mit ihren Optionen, damit die Entscheidung nachvollziehbar bleibt.

**Q1 – Abbaureihenfolge im Soll-Querschnitt (F17, design\_rules D1–D3, PRF-06).** Worum es geht: Reicht der Raum nicht, fallen heute erst Parken, dann Bäume, dann der zweite Kfz-Fahrstreifen. Das ist eine Abwägung zwischen Grün, Kfz-Leistungsfähigkeit und Radqualität.

- a) wie heute (Bäume vor 2. Fahrstreifen): Kfz-Kapazität bleibt eher erhalten, Grün verliert.
- b) D3 vor D2: zweiter Fahrstreifen fällt vor neuem Baumstreifen; Bestandsbäume nur als Flag. Passt zu „so wenige Fahrstreifen wie möglich“.
- c) wie b, zusätzlich Radweg-Fallback erst nach D2: Radqualität vor Grün.
- Empfehlung: **b**, weil sie die erklärte Philosophie am direktesten umsetzt und Bestandsbäume rechtlich ohnehin geschützt sind.

**Entscheidung 08.11.2026: b.** F17 wird wie vorgeschlagen umgesetzt: `cascade_order: [D1, D3, D2, fallback, D4, D5, D6, D7]`, D2 nur für neue Baumstreifen, Bestandsbäume als Flag.

**Q2 – Schul- und Kita-Auslöser für GOW30 (F07, F25, rules.yaml C-G30-01, H-STR-01).** Worum es geht: Der Umkreis von 150 m trägt den größten Teil der 61 % HVS-km, die GOW30 werden. Die Wahl bestimmt das Ergebnis und die öffentliche Debatte stärker als jede andere Schwelle.

- a) 150 m wie heute: größter GOW30-Anteil, rechtlich schwerer anschlussfähig.
- b) Zugang am Abschnitt ≤ 50 m plus Lückenschluss bis 500 m: näher an StVO § 45 (9), durchgehende Tempo-30-Strecken statt Flickenteppich; GOW30-Anteil sinkt.
- c) wie b, zusätzlich `place_score` als dritter Auslöser (F25 a): fängt dichte Wohn- und Geschäftslagen ohne Einrichtung auf.
- Empfehlung: **b** sofort, **c** nach Kalibrierung an den E1-Stichproben.

**Entscheidung 08.11.2026: b.** F07 wird umgesetzt (`access_radius` 50 m, `gap_close_m` 500 m in H-STR-01). Option c ist zurückgestellt: `crossing_demand` erhält `status: inactive`, `place_score` bleibt definiert, wird aber erst nach Kalibrierung an den E1-Stichproben als Auslöser geprüft (F25).

**Q3 – in\_hvs im Verbindungsscore (F13, rules.yaml `scores.conn_score`; offene Frage 124, für den Fachplaner-Termin zurückgestellt).** Worum es geht: in\_hvs zählt doppelt und verschiebt die Bedeutung von `conn_gow` für Nicht-HVS.

- a) belassen, aber dokumentieren: keine Ergebnisänderung, Schwelle bleibt schwer erklärbar.
- b) herausnehmen und `conn_gow` so kalibrieren, dass die Nicht-HVS-GOW-km etwa gleich bleiben: gleiches Ergebnis, saubere Logik.
- c) herausnehmen ohne Neukalibrierung: rund 430 km mehr GOW (Probelauf 07.11.).
- Empfehlung: **b**.

**Entscheidung 08.11.2026: b.** F13 wird umgesetzt: in\_hvs aus `conn_score`, `conn_gow` per Probelauf so kalibrieren, dass die Nicht-HVS-GOW-km etwa beim Stand 0.16.0 bleiben (rund 78 km); offene Frage 124 damit erledigt.

**Q4 – Anbaufreie Hauptverkehrsstraßen (F23, rules.yaml `categories`).** Worum es geht: Anbaufreie Abschnitte mit heute 60/70 km/h, die keine Kraftfahrstraße sind, werden GOW50 und erhalten Anforderungen einer angebauten Magistrale. Eine eigene Kategorie wäre ein größerer Umbau (Matrix, Profile, Knoten, Diskrepanz).

- a) nur Attribut und Flag `gow50_anbaufrei` (S-FEAT-12): kleiner Eingriff, Steckbrief erklärt den Sonderfall.
- b) eigene Kategorie (z. B. GOW50A, Soll-Tempo 50, Radweg abgesetzt, keine Gehwegüberfahrten): fachlich genauer, großer Umbau.
- c) nichts.
- Empfehlung: **a**, und nach den E1-Stichproben entscheiden, ob der Umfang b rechtfertigt.

**Entscheidung 08.11.2026: a.** F23 wird als Attribut S-FEAT-12 mit Flag `gow50_anbaufrei` umgesetzt; keine neue Kategorie. Nach den E1-Stichproben erneut prüfen, ob der Umfang eine Kategorie rechtfertigt.
