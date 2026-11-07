# Varianten

Alternative Stände des Entwurfs, die fachlich interessant sind, aber nicht der aktuelle Stand des Regelwerks.
Je Variante: Regeländerung, Kennzahlen, wo sie liegt und wie man sie wiederherstellt.

## Kompromiss Hamburg: GOW50 statt GOW30 auf stark belasteten Hauptverkehrsstraßen (2026-11-07)

**Regelwerk:** rules.yaml 0.14.0. C-G30-01 (Schule/Kita, Publikumsnutzung, Querungsbedarf → GOW30) gilt auf
Hauptverkehrsstraßen nur bis 10 000 Kfz/24h (gow30_max_dtv, gleich dem CROW-GOW30-Profil „wide“); darüber
C-G50-02: GOW50 mit Hinweis „Tempo-30-Abschnitt vor Ort prüfen“. Fehlt der Platz für einen baulichen Radweg, bleibt
GOW30 (C-G30-02). Aktueller Stand (rules.yaml 0.15.0 ff.) hat diese Obergrenze nicht: Umfeld vor heutiger Verkehrsmenge
(Entscheidung prstolpe 2026-11-07).

**Einschätzung prstolpe (2026-11-07):** sieht in der Karte sauber aus und könnte als Kompromiss in Hamburg gut
funktionieren. Als Alternative behalten.

**Kennzahlen (ganz Hamburg):**

| | Variante 0.14.0 | Stand 0.13.0/0.15.0 |
|---|---:|---:|
| Hauptverkehrsstraßen als GOW30 | 93 km | 453 km |
| Hauptverkehrsstraßen als GOW50 | 555 km | 195 km |
| davon über C-G50-02 (Hinweis Tempo-30-Abschnitt) | 358 km | – |

Übrige Regelwerke dieses Stands: cycling_rules.yaml 0.7.0, design_rules.yaml 0.5.0, sources.yaml 0.1.12.

**Wo:**
- Git-Tag `variante-gow50-kompromiss` (Commit be9629a) – Regelwerk und Code dieses Stands.
- Gebaute Seite (nicht in Git): `data/variants/2026-11-07_gow50-kompromiss/site`. Ansehen:
  `cd web && npx vite preview --outDir "$PWD/../data/variants/2026-11-07_gow50-kompromiss/site" --port 4174`,
  dann http://localhost:4174/

**Wiederherstellen im aktuellen Code:** C-G30-01-Bedingung, Schwelle gow30_max_dtv und Regel C-G50-02 aus dem Tag
übernehmen (`git show variante-gow50-kompromiss:config/rules.yaml`), Texte aus plain_language.yaml 0.4.2, Schema-Prüfung
und goldene Fälle 28–30 aus dem Tag; neue Version in rules.yaml und CHANGELOG, dann `make rerun FROM=classify`.
Besser auf Dauer: als umschaltbare Variante im Regelwerk führen (offene Frage).

**Bezug:** offene Fragen „HVS in Eimsbüttel: 60 % der HVS-km werden GOW30“ und „Prompt 19: 362 von 523 km GOW30“
(docs/open_questions.md); Zielszenario prompts/22 (mit weniger Kfz-Verkehr fällt die Obergrenze seltener ins Gewicht).
