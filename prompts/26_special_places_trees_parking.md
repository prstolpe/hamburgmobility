# 26 – Special places (starting with "Verkehrsberuhigte Schanze") and tree/parking statistics

**Goal:**
- **Part 1, exploratory, separate branch:** add a reusable "Besondere Orte" (special places) feature and use it first for the Bürgerbegehren "Verkehrsberuhigte Schanze": colourful, playful map styling on the affected streets, optionally a 3D element, a filter/overlay like the bus routes, and an extra explanation in the street profile ("Steckbrief") next to the rule-based text.
- **Part 2:** estimate how many street trees and parking spaces would be affected, removed or added by the target cross-sections, and show this in the Bezirke statistics and wherever else it fits.

**Approval:** Before building, ask me the open questions below. After each part, stop and show me a preview and a short report; nothing is merged or deployed without my OK.
**Language:** website text in German plain language (as in Prompt 23); code, keys and file names in English.

## Ground rules

- Plan mode first. Show the plan for Part 1 and Part 2, the agent split (see below) and your questions to me.
- Part 1 on branch `explore/special-places-schanze`; Part 2 on branch `feature/trees-parking-stats`. Do not touch production until I approve.
- Follow the current design system (Swiss design tokens, grid, typography), `docs/source_policy.md` (every new number has a `source_type`; unknown = `assumption`), WCAG 2.2 AA, no tracking, no external services at runtime. Keep `segment_id`/`node_id`, overrides and shareable URLs stable.
- Respect the current rule-file structure (separate `config/*.yaml` or unified `rules/`).

## Agents and models (save cost)

Delegate mechanical work to subagents on cheaper models; keep judgement, design and wording in the main session. Define agents in `.claude/agents/` (frontmatter `name`, `description`, `tools`, `model`), or pass a model when spawning a subagent if your version works that way.

| Agent | Model | Task | Tools |
| --- | --- | --- | --- |
| `street-matcher` | haiku | match street names/sections to `segment_id`s via OSM and the segment table; list ambiguities | Read, Grep, Bash |
| `data-extractor` | haiku | collect parking tags, tree points, offsets; produce intermediate tables | Bash |
| `screenshot-runner` | haiku | Playwright screenshots desktop 1440 px / mobile 390 px, pitch 0° and 45° for 3D | Bash |
| `a11y-perf-check` | haiku | axe-core, console errors, bundle size, frame rate with 3D on a mid-range mobile profile | Bash |
| `stats-qa` | sonnet | independent check of the tree/parking estimates: plausibility, double counting, units, sample review | Read, Bash |
| `review` | sonnet | independent review of the final diff against this prompt | Read |

Run independent tasks in parallel. In the report, list which agent did what.

## Questions to ask me before building

1. **Colours:** which colours of the initiative should be used (hex codes or a style sheet), and may I use them? If you can read them from the initiative's public website, propose them and wait for my confirmation. Do not use their logo unless I confirm that's allowed.
2. **Street extents:** the initiative names whole streets. Show me the matched sections on a map (from `street-matcher`) and ask me to confirm start/end points, especially for long streets such as Schanzenstraße and Lerchenstraße.
3. **3D:** do I want a 3D element at all, and which of the options below?
4. **Part 2 placement:** confirm where the tree/parking statistics should appear (your recommendation below).

## Part 1 – "Besondere Orte" feature

### 1.1 Content of the first place (facts to use; verify links still work)

- Proposal: Bürgerbegehren "Verkehrsberuhigte Schanze" in Bezirk Altona, linked to the Hamburger Zukunftsentscheid. Source: https://zukunftsentscheid-hamburg.de/verkehrsberuhigteschanze
- Fahrradstraßen: Schanzenstraße, Schulterblatt, Susannenstraße, Kampstraße, Ludwigstraße, Lerchenstraße, Juliusstraße.
- Pedestrian zones with "Fahrrad frei": Bartelsstraße, Rosenhofstraße.
- Exceptions named by the initiative: emergency vehicles, refuse collection, delivery traffic to certain destinations, residents with private parking, trades, care services, removals.
- Status as of 25 Sept 2026: signature collection running; the Bezirksamt Altona declared the Bürgerbegehren admissible; 3 % of eligible voters in Altona needed within six months (https://radioreeperbahn.de/2026/09/25/buergerbegehren-fuer-autofreies-schanzenviertel-gestartet/). Check for a newer status and ask me if unsure. Always show the status date.
- Present it as the initiative's proposal, not as an adopted plan, and credit the source. Do not copy their map image; build our own geometry from the street list and OSM.

### 1.2 Data model (reusable for more places)

Create `special_places/` (or a section in the rule files, if that fits the current structure better – propose which):

```yaml
- id: schanze_verkehrsberuhigt
  title: 'Verkehrsberuhigte Schanze'
  kind: proposal            # proposal | decided | built
  initiator: 'Bürgerbegehren, Bezirk Altona'
  status: 'Unterschriftensammlung läuft'
  status_date: 2026-09-25
  sources: [{title: ..., url: ...}]
  theme: {palette: [...], pattern: ..., use_3d: ...}
  segments:
    - {segment_ids: [...], measure: cycle_street, label_plain: 'Fahrradstraße'}
    - {segment_ids: [...], measure: pedestrian_zone_bikes_allowed, label_plain: 'Fußgängerzone, Rad frei'}
  texts: {glance: ..., explain: ..., details: ...}
```

- A JSON-schema/pydantic check and tests (every place has sources, a status date and valid segment IDs).
- Export to a small GeoJSON/PMTiles layer `special_places`, loaded only when the overlay is on.

### 1.3 Map presentation – build 2–3 options as a preview and let me choose

The special-place layer may deliberately stand out from the restrained base design, but it must remain readable and accessible.
- **A Colour and pattern:** thick lines in the initiative's palette, gradient along the line (`line-gradient`) or two-tone dashes, a soft glow; street labels stay readable.
- **B Low 3D "ribbons":** street area as `fill-extrusion` (e.g. 2–4 m high, semi-transparent, in palette colours) that shows up when the map is tilted; flat lines in 2D.
- **C Landmark:** a single 3D object or extruded label at the centre of the area (e.g. "Schanze" letters or a simple glTF model via a MapLibre custom layer or deck.gl) – only if it loads fast and has a 2D fallback.
- For all options: respect `prefers-reduced-motion` (no animation), a 2D fallback, a colour-blind-safe encoding (pattern/width, not colour alone), a legend entry "Vorschlag Bürgerbegehren" and a performance budget (state the extra KB and the frame rate on mobile).

### 1.4 Overlay and section

- Overlay "Besondere Orte" in the same way as the bus-route filter (toggle and list), with a URL parameter (`?place=schanze_verkehrsberuhigt`) that zooms to the place.
- A small section/page "Besondere Orte": one card per place (level 1: one sentence, status, date; level 2: what is proposed and why; level 3: sources and comparison with our rules), so that I can add more places later just by adding config entries.

### 1.5 Profile ("Steckbrief") text

- When a segment belongs to a special place, the profile shows an extra block **above or next to** the rule-based explanation (propose the order): "Besonderer Ort: Verkehrsberuhigte Schanze – Vorschlag des Bürgerbegehrens: Fahrradstraße".
- Generate the text **deterministically from templates plus data** (no runtime AI): the proposal for this street, its status and date, and a short comparison with our rule-based result, for example:
  - "Unser Regelwerk sieht hier eine Wohnstraße mit Tempo 30 vor. Eine Fahrradstraße passt dazu, wenn wenig Autoverkehr bleibt."
  - "Hier weicht der Vorschlag vom Regelwerk ab, weil …"
  Write the templates in plain German, list all generated variants in the report for my review, and keep the rule explanation unchanged.
- Optional, as a proposal only: run our cross-section and junction logic in a scenario with the proposal's measures (`data/scenarios/schanze/`) and show the effect (e.g. through traffic shifting to neighbouring streets). Ask me before adding this to the profile.

### 1.6 Stop

Report `docs/special_places/bericht.md` with screenshots of all options (2D and tilted), performance numbers, generated texts and open points. **Stop** and wait for my choice.

## Part 2 – Trees and parking spaces

### 2.1 Method (propose, then implement after my OK)

**Parking spaces**
- Today: kerbside parking from OSM street-parking tags (`parking:left/right/both`, orientation, restrictions); check coverage per Bezirk and report it. Look for an official Hamburg parking dataset and add it to `sources.yaml` only with a verified URL.
- Count spaces from usable kerb length divided by space length per orientation, minus driveways, crossings and no-parking areas near junctions. All lengths and setbacks are `assumption` with a note; check the legal setback in the StVO.
- Target: spaces kept, removed or added from the target cross-section (`profile_elements`, degrade steps D1/D2) and from special places.
- Where OSM has no parking data: give an estimate with a wide range, or "keine Daten". Never treat missing as zero.

**Street trees**
- Use the Straßenbaumkataster points. Compute each tree's side and lateral offset from the street centreline.
- Compare with the positions of the elements in the target profile:
  - **bleibt** (in a tree strip, verge or kept parking row),
  - **möglicherweise betroffen** (in the space of a new or widened cycle track, footway or carriageway),
  - **neu möglich** (new tree strip length divided by tree spacing; spacing as `assumption`).
- Wording: "möglicherweise betroffen", never "wird gefällt". Show ranges and the uncertainty from position accuracy and profile simplification.

**QA:** `stats-qa` checks 30 sample streets against orthophotos and street images. Report the error rate and adjust the method before publishing. Write all new values to the rule files following the source policy.

### 2.2 Presentation – my recommendation, confirm with me

- **Bezirke statistics:** two new cards in the existing style per Bezirk and for Hamburg as a whole:
  - "Parkplätze: heute ≈ X, im Ziel ≈ Y (−Z)",
  - "Straßenbäume: X bleiben, Y möglicherweise betroffen, Z neu möglich".
  Each card gets level 2 (what it means, in one or two sentences) and level 3 (method, ranges, data coverage).
- **Street profile:** the same three numbers for the street section, at level 2 or 3.
- **Methodology:** a short chapter "Bäume und Parkplätze" in three levels.
- **Downloads:** a column per segment in the data export.
- Also add a statement for the special place (e.g. "Im Vorschlag Schanze entfallen ≈ X Parkplätze"), if Part 1 is approved.

### 2.3 Stop

Report `docs/trees_parking/bericht.md` with method, coverage, QA results, screenshots and a list of all new assumptions. **Stop** for my OK, then open the pull request, merge and deploy. Run a quick live check with `screenshot-runner`.
