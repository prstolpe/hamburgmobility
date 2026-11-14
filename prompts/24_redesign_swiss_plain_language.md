# 24 – Redesign: Swiss design, plain language, layered detail, leaner rules

**Goal:** Make hamburgmobility.de much easier to understand without losing depth. Redesign the website following the principles of Swiss (International Typographic Style) design, rethink what is shown and what is explained, rewrite all texts for non-experts, make the language in the rule files understandable, and assess whether rules can be combined or removed.
**Approval:** Part A only analyses and proposes. Nothing in production changes until I have approved the proposals in `docs/redesign/decisions.md`. Merging or removing rules needs my **explicit, separate approval per rule**.
**Language:** All website text and all plain-language fields in the rule files are in German. Code, file names, keys and comments stay in English.

## Ground rules

- Work in plan mode first. Show me the plan for Part A with a rough time estimate before starting.
- Branch `redesign/2026-11`. In Part A, do not change `web/`, the rule files, `overrides/` or published data. Allowed: `analysis/redesign/`, `prototypes/redesign/`, `docs/redesign/`, dry runs to `data/scenarios/redesign/`.
- Detect the current rule structure (`config/*.yaml` or a unified `rules/` folder, if Prompt 22 introduced one) and work with what exists.
- Keep stable: `segment_id`, `node_id`, rule IDs (merged rules keep their old IDs as aliases), overrides, shareable URLs (old parameters redirect), the permanent notice "nicht amtlicher Diskussionsentwurf", `docs/source_policy.md`, WCAG 2.2 AA, no tracking, no external font or script services (self-host fonts).
- Back every finding with evidence: screenshots, counts, example IDs, readability scores. No guesses presented as findings.

## Part A – Analyse and propose (then STOP)

### A1 Inventory

1. **Website content inventory:** every page, map layer, legend, filter, panel, popup/profile ("Steckbrief"), tooltip, the methodology section, the download and licence pages. For each item: what it shows, what it explains, who it is for, word count, jargon used.
2. **Task test** with screenshots (Playwright, desktop 1440 px and mobile 390 px) for five tasks:
   - "What is planned for my street, and why?"
   - "Does the planned layout fit into the street?"
   - "Where does my district need action most?"
   - "What does the cycle network look like, and where are the gaps?"
   - "What will change at this junction?"
   Record click path, sticking points and the words that block understanding.
3. **Readability:** score all German texts (website and rule-file descriptions) with the Wiener Sachtextformel and the German Flesch reading-ease score (Amstad), e.g. via `textstat` with German settings. Also report sentence length, share of passive voice and compound nouns, and a list of every technical term and abbreviation (GOW, ETW, Diskrepanz, Conflation, Entwurfssituation, rule IDs …) with where it appears.
4. **Rule-file language:** for every rule, category, threshold and description, note whether a non-expert would understand the label and the explanation.
5. **Rule inventory** (all rule files), one row per rule:
   ID · purpose in one sentence · inputs · how often it decides the outcome (from `rule_trace` of the current run) · km/nodes affected · overlaps with other rules · tests covering it · `source_type` · candidate action (keep / simplify / merge / remove) with reasoning.

Output: `docs/redesign/01_inventory.md`, `01_rules_inventory.csv`, screenshots in `docs/redesign/img/`.

### A2 Information architecture: at a glance, then detail on demand

Propose one consistent three-level pattern for **every** part of the site (map, profile per street section and junction, district overview, cycle network, methodology, data/downloads):

| Level | Question it answers | Form |
| --- | --- | --- |
| 1 At a glance | What is it? | One sentence, one label/colour, at most one key number. Readable in 5 seconds. |
| 2 Explanation | Why? What changes? | 3–5 short sentences in plain language, one small visual (cross-section before/after, mini map, bar). |
| 3 Details | How exactly? What is the source? | Rules that fired with their values, data sources and dates, uncertainty, assumptions, links to the rule file and downloads. |

Specify:
- what is shown by default and what moves to level 2 or 3 or is dropped,
- how the number of map layers can be reduced (e.g. a few themes with preset layers instead of many toggles),
- how assumptions and uncertainty are shown honestly but calmly,
- the structure of the new methodology section: a one-page summary first ("Was ist das, was zeigt es, was zeigt es nicht"), then one chapter per topic, each again in three levels, ending in the technical rule reference generated from the rule files.

Output: `docs/redesign/02_information_architecture.md` with a sitemap and wireframes (simple SVG or HTML).

### A3 Swiss design system

Translate Swiss design principles into concrete, documented design tokens and components:
- **Grid:** a modular grid (e.g. 12 columns on desktop, 4 on mobile), fixed baseline, consistent margins; asymmetric layouts aligned to the grid.
- **Typography:** one sans-serif grotesque family, self-hosted with an open licence (e.g. Inter, or another with a suitable licence, checked and documented); a strict type scale with few sizes; flush-left, ragged-right text; hierarchy by size and weight, not decoration; generous line height; numbers in tabular figures for tables.
- **Colour:** neutral base (black, white, greys) and few functional accents; one colour meaning per concept across the whole site; colour-blind safe palettes for the map with redundant encoding (line style, width, symbol); contrast ≥ 4.5:1 for text.
- **Map styling:** muted greyscale base map so the data stands out; line width shows hierarchy; legends written in plain words next to the map, not hidden.
- **Objectivity and white space:** no ornament, no shadows or gradients, content first; clear alignment; restrained motion.
- **Components:** header, theme switcher, legend, profile panel (desktop side panel, mobile bottom sheet), level-2/3 disclosure ("Mehr erfahren", "Details und Quellen"), district cards, tables, cross-section drawing, notice banner.

Build **two variants** within these principles (e.g. "map-first" vs. "overview-first"), each as a clickable prototype in `prototypes/redesign/<variant>/` on real data for one district, with desktop and mobile screenshots, pros and cons and effort.

Output: `docs/redesign/03_design_system.md`, `tokens.json`, prototypes.

### A4 Plain language

- Target: German plain language ("einfache Sprache", roughly level B1), not the regulated "Leichte Sprache".
- Rules: sentences mostly under 15 words; active voice; verbs instead of nominal style; one idea per sentence; explain each technical term at first use or replace it; numbers with units; consistent terms throughout.
- Create a **glossary** (`docs/redesign/glossary.yaml`) mapping each technical term to a plain German name and a one-sentence explanation, e.g. GOW50 → "Hauptstraße mit Tempo 50", ETW30 → "Wohnstraße mit Tempo 30", Diskrepanz → "Abweichung zwischen heute und Ziel". Technical terms stay available on level 3.
- Rewrite samples before/after for: home page intro, five map legends, one profile per category, one junction profile, the methodology summary and two methodology chapters. Show readability scores before and after.

Output: `docs/redesign/04_language.md`, glossary.

### A5 Rule files: understandable language (no change in meaning)

- Propose additional plain-language fields for every rule, category and threshold, e.g. `label_plain` (a few words), `explain_plain` (1–2 sentences), `why` (why the rule exists), next to the existing technical fields. Existing keys, IDs and values stay unchanged.
- Propose clearer wording for existing `description`/`note` fields where they are hard to read.
- The website and the methodology rule reference must read these fields directly, so texts exist in one place only.
- Show a diff sketch for 10 representative rules.
- Proof of no semantic change: a dry run with the proposed text changes must produce identical classification outputs (hash comparison of all non-text columns).

Output: `docs/redesign/05_rule_language.md`.

### A6 Fewer rules? (needs my separate approval)

For every candidate from the rule inventory marked simplify / merge / remove:
- problem (redundant, rarely decisive, overlapping, untestable, unclear source),
- proposal (new combined rule or removal, as a YAML diff sketch),
- **dry-run effect:** km and nodes whose category, facility, lane count or junction type change, by district, with a map and examples,
- what is lost (explainability, sensitivity to special cases),
- `source_type` of any new or changed value.
Also report the overall effect if all proposals were accepted. Do not apply anything.

Output: `docs/redesign/06_rule_consolidation.md`, dry-run results in `data/scenarios/redesign/`.

### A7 Decisions, then STOP

- `docs/redesign/proposals.md`: one-page summary, then the decisions in priority order (design variant, information architecture, layer/theme concept, glossary, rule-file language fields, each rule consolidation proposal individually), each with options including "keep as is", impact, recommendation and effort.
- `docs/redesign/decisions.md`: a table to fill in, one row per decision (ID, chosen option, my comment). Rule consolidation proposals each get their own row with the choices "approve / reject / revise".
- Commit everything to `redesign/2026-11`, summarise in chat in at most ten lines what I need to look at, and **stop**.

## Part B – Implement approved decisions only

Start Part B only after `docs/redesign/decisions.md` is filled in (a new session can resume from that file). Implement only rows with a chosen option. Ask first if anything is unclear or contradictory.

Work in packages, each on its own branch, in this order:
1. **Design system and layout** (tokens, fonts, grid, components, map style).
2. **Content and texts** (three-level pattern everywhere, glossary applied, legends, profiles, district overview, downloads).
3. **Methodology section** (summary, chapters in three levels, rule reference generated from the rule files).
4. **Rule-file language** (new plain-language fields, clearer descriptions). Prove identical classification outputs (hash comparison); bump patch version; CHANGELOG entry.
5. **Rule consolidation**, only for rules marked "approve": tests first, then YAML and code; keep old IDs as aliases in `rule_trace`; bump minor version; full before/after report (`docs/redesign/impl_rule_consolidation.md`) with changed km/nodes and a map; check overrides for orphans (report, don't delete).

For each package: tests green, determinism check (two runs, identical output), preview build (not the live site), desktop and mobile screenshots, axe-core result, readability scores for changed texts, a short report in `docs/redesign/impl_<package>.md`. Then **stop for my OK** before merge and deployment to GitHub Pages. Finally add a "Was ist neu" entry with date and version to the website.
