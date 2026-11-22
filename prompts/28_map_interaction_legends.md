# 28 – Map interaction and legends

**Goal:** Make the map easier and more dynamic to use:
- a legend that shows only what is switched on and explains it right there,
- a clear panel for views and layers,
- better tap/hover feedback,
- good mobile behaviour.

Along the way, build two shared foundations that later prompts (more special places, legal-maximum mode, letters, social media) will reuse:
- a **stable URL scheme** for the map state,
- a **renderer** that turns a segment, intersection or special place into a static image.

**Approval:** Two stops (marked STOP). Nothing is merged or deployed without my OK.
**Language:** website text in German plain language (as in Prompt 23); code, keys and file names in English.

## Ground rules

- Plan mode first. Show the plan, the agent split and your questions to me.
- Branch `feature/map-interaction`. Production stays unchanged until I approve.
- This prompt changes presentation only. Rule output, `segment_id`/`node_id`, overrides and data exports stay unchanged.
- All existing shareable URLs keep working, including `?place=` from Prompt 25 and any parameters from Prompt 26. Old links must open the same view as before.
- Follow the current design system (Swiss design tokens, grid, typography), the three-level pattern (auf einen Blick / Erklärung / Details), `docs/source_policy.md`, WCAG 2.2 AA, no tracking, no external services at runtime.
- Respect existing features: the bus-route filter, the "Besondere Orte" overlay and, if merged, "Ruhige Quartiere" and the tree/parking layers.

## Agents and models (save cost)

Delegate mechanical work to subagents on cheaper models. Keep design decisions, wording and judgement in the main session. Define agents in `.claude/agents/` (frontmatter `name`, `description`, `tools`, `model`), or pass a model when spawning a subagent.

| Agent | Model | Task | Tools |
| --- | --- | --- | --- |
| `ui-inventory` | haiku | list every map layer, legend entry, control, filter, URL parameter and colour token, with file locations and which view uses them | Read, Grep, Glob |
| `usability-walkthrough` | sonnet | run the task list in 1.2 against the old and the new UI; record steps, dead ends and unclear labels | Read, Bash |
| `screenshot-runner` | haiku | Playwright screenshots desktop 1440 px / mobile 390 px, before/after, open and closed panels | Bash |
| `a11y-perf-check` | haiku | axe-core, keyboard-only walkthrough, screen-reader labels, console errors, bundle size, time to interactive, frame rate on a mid-range mobile profile | Bash |
| `review` | sonnet | independent review of the final diff against this prompt | Read |

Run independent tasks in parallel. In the report, list which agent did what.

## Questions to ask me before building

1. **Known problems:** there is no analytics, so ask me which complaints or confusions I already know about.
2. **Legend behaviour:** show all entries of the active layers, or only those visible in the current map view? My expectation: all entries of the active layers, with entries that are not in view dimmed. Propose and confirm.
3. **Mobile pattern:** bottom sheet with several heights or a full-screen panel?
4. **Image renderer:** render images for all segments at build time (state the storage size), or on demand with a CLI for selected items only? Do I want per-link preview images (Open Graph), which need pre-rendered pages?
5. **Search:** is street/address search in scope here, or a later prompt?

## Phase 1 – Inventory and concept

### 1.1 Inventory (`ui-inventory`, `screenshot-runner`)

- Make a table of all layers, legend entries, controls and URL parameters. Mark duplicates, inconsistent symbols or labels, and entries without an explanation.
- Take screenshots of the current state on desktop and mobile.

### 1.2 Walkthrough of the current UI (`usability-walkthrough`)

Run these tasks and count the steps:
- Find the target profile of a named street.
- Find out what a given line colour means.
- Turn on the bus routes and then turn them off again.
- Open the Schanze special place.
- Compare the current state and the target state for one intersection.
- Share a link to one segment.
- Do all of the above with the keyboard only.
- Do all of the above on mobile.

Report the steps, the dead ends and the unclear labels for each task.

### 1.3 Concept – build 2–3 options as a clickable preview (not a full build)

**Legend**
- One legend component, driven by a single registry. Propose the location (e.g. `map/legend_registry.ts`).
- Each layer declares its own entries: symbol, `label_plain`, a level-2 explanation and a link to the methodology (level 3).
- Layers that are off do not appear in the legend.
- Tapping an entry highlights the matching features or filters to them.
- Each entry has a "Was heißt das?" explanation inline.
- Later views and layers must plug into the registry without code changes elsewhere.

**Views and layers panel**
- Separate **"Ansicht"** (Ist / Ziel, later "Heute schon möglich") from **"Ebenen"** (Busrouten, Besondere Orte, Ruhige Quartiere, Bäume und Parkplätze, …), grouped by theme.
- Show active layers as chips on the map, each removable with one tap.
- Propose a limit for the number of overlays shown at the same time, if readability needs one.

**Feature interaction**
- Hover (desktop) or tap (mobile) opens a small preview with level 1 (one sentence) and a button to open the profile ("Steckbrief").
- Highlight the selected segment or node clearly.
- Esc or the back button closes the preview.
- Provide a keyboard-navigable list of the features in the current view, as an accessible alternative to clicking on the map.

**Mobile**
- Legend, preview and profile share one panel; no stacked overlays.
- Controls are reachable with the thumb.

**Motion**
- Short transitions only, and none under `prefers-reduced-motion`.

### 1.4 URL scheme

Write `docs/url_scheme.md`. It defines:
- parameters for view, layers, selection (`seg`, `node`, `place`) and camera (`z`, `lat`, `lon`, `pitch`, `bearing`),
- a version parameter.

Rules:
- Every state that matters for sharing is in the URL.
- Old parameters map to the new ones.
- Unknown parameters are ignored.
- Parsing and serialising round-trip without loss, with tests.

The scheme must cover the planned "Heute schon möglich" view and further special places without changes.

### 1.5 Image renderer concept

**Tool and constraints**
- A CLI `tools/render_card` that renders with our own map style and data locally (e.g. Playwright with headless MapLibre).
- No external tile or rendering service.

**Output formats**
- 1200×630 px for link previews,
- 1080×1350 px portrait for social media,
- an A4 inset at 300 dpi for letters.

**Card content**
- a map extract,
- the current vs. target cross-section where available,
- a title and one plain-language sentence,
- source and status date,
- the project URL with a deep link.

**Rules**
- Layout uses the design tokens.
- Output is deterministic: the same input gives the same image.
- An alt text is generated for each image.

**STOP 1:** Show the inventory, the walkthrough results, the options with screenshots, the URL scheme draft and the renderer concept. Wait for my choice.

## Phase 2 – Build

1. Implement the chosen option. Migrate all existing layers to the legend registry and remove the old legend code.
2. Implement the URL scheme with tests. Test that a sample of at least 20 old link patterns resolves to the same view.
3. Implement the renderer CLI with the three formats and tests. Render samples for 5 segments, 3 intersections and the Schanze place.
4. Performance budget: state the extra KB, the time to interactive before and after, and the frame rate on mobile. Propose a limit and stay within it.
5. Checks:
   - `a11y-perf-check`;
   - `usability-walkthrough` on the new UI, comparing step counts with 1.2;
   - `screenshot-runner` on desktop and mobile;
   - `review` against this prompt.
6. Write the report `docs/map_interaction/bericht.md`: before/after screenshots, walkthrough comparison, performance numbers, which agent did what, open points.

**STOP 2:** Show the preview and the report. After my OK: open the pull request, merge and deploy. Then run a quick live check with `screenshot-runner`, including 10 old shared links.
