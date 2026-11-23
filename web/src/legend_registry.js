// Legend registry (prompt 28): one place that knows, for every view and every additional layer, which entries it
// shows on the map – symbol, plain label, a level-2 explanation ("Was heißt das?") and a link to the method (level 3).
// The legend, the layer switches, the chips, the highlight and the "in view" check all read from here.
// A new view plugs in through THEMES (state.js) + groups()/LAYER_INFO (layers.js); a new additional layer through one
// entry in OVERLAY_LAYERS below (plus its drawing in layers.js sfpLayers). Nothing else has to change.
// Display only: colours come from palette.js; rule output is not touched.
import { CASING, INK, NEED, OVERLAY_COLORS, RURAL_FILL } from "./palette.js";
import { DISC_WIDTH, groups, isCyclingLayer, LAYER_INFO, placeOf } from "./layers.js";

// method chapter of each view (level 3)
const METHOD = {
  cat: "#methode/aufgabe", speed: "#methode/aufgabe", hvs: "#methode/aufgabe", disc: "#methode/abweichung",
  prio: "#methode/abweichung", width: "#methode/platz", feas: "#methode/platz", cnet: "#methode/radnetz",
  cfac: "#methode/radnetz", cgap: "#methode/radnetz", lanes: "#methode/platz", cfit: "#methode/platz",
  jct: "#methode/knoten", coff: "#methode/radnetz",
};

// Explanations the export glossary (meta.glossary) does not have; plain language (docs/redesign/04_language.md).
const EXTRA_EXPLAIN = {
  disc: {
    D1: "Die Straße soll nur das Viertel erschließen, ist aber schnell oder breit gebaut wie eine Hauptstraße.",
    D2: "Die Straße soll Stadtteile verbinden, aber es fehlt etwas, das dazu gehört – meist ein sicherer Radweg.",
    D3: "Beides trifft zu: zu schnell gebaut, und es fehlt Gestaltung.",
    none: "Tempo und Gestaltung passen heute schon zur Aufgabe.",
    unchecked: "Für diese Straße fehlen Angaben, zum Beispiel das heutige Tempo. Wir können sie nicht prüfen.",
  },
  prio: {
    p3: "Hier kommen eine große Abweichung und viele Unfälle, Schulen oder viel Radverkehr zusammen.",
    p2: "Eine Abweichung mit einigen dieser Gründe.",
    p1: "Kleine oder keine Abweichung.",
  },
  lanes: {
    fewer: "Im Ziel gibt es weniger Fahrstreifen für Autos. Der Platz geht an Gehweg, Radweg, Bäume oder Bus.",
    more: "Im Ziel gibt es mehr Fahrstreifen als heute markiert, meist weil heute ein Streifen nicht markiert ist.",
  },
  speed: { s_unknown: "Für diese Straße kennen wir das heutige Tempo nicht: weder amtlich noch aus OpenStreetMap." },
  jct: { "grp-none": "Für Autobahnknoten legen wir kein Ziel fest; bei einigen Kreuzungen passt keine Regel." },
};

/** Level-2 text of one entry: export glossary first, then EXTRA_EXPLAIN, else null (the layer sentence stands). */
function explainOf(layer, key, meta) {
  const g = meta.glossary ?? {};
  const k = key.replace(/^(cc|fs|gap|ld|fit)-/, "");
  const hit = g.categories?.[k] ?? g.cycling?.[k] ?? g.terms?.[k] ?? null;
  if (hit?.explain && !/^siehe /.test(hit.explain)) return hit.explain;
  return EXTRA_EXPLAIN[layer]?.[k] ?? EXTRA_EXPLAIN[layer]?.[key] ?? null;
}

// Additional layers (Ebenen): key = URL value in layers=. group = heading in the panel.
// entries: what is drawn; layer = MapLibre layer id; symbol = how the legend draws it.
export const OVERLAY_LAYERS = {
  bus: {
    group: "Verkehr heute", title: "Buslinien",
    text: "Straßen mit Buslinien. Je breiter die Linie neben der Straße, desto mehr Busse fahren an einem Werktag.",
    explain: "Grundlage sind die Fahrplandaten des HVV (Fahrten je Werktag). Die Linie liegt neben der Straßenlinie, damit beides sichtbar bleibt.",
    method: "#methode/daten",
    entries: [
      { key: "bus-few", label: "wenige Busse (ab 1 Fahrt am Tag)", symbol: { type: "line", color: OVERLAY_COLORS.bus, width: 1.5 } },
      { key: "bus-many", label: "viele Busse (300 Fahrten und mehr am Tag)", symbol: { type: "line", color: OVERLAY_COLORS.bus, width: 5 } },
    ].map((e) => ({ ...e, layer: "ov-bus" })),
  },
  acc: {
    group: "Verkehr heute", title: "Unfälle",
    text: "Unfälle, an denen Menschen zu Fuß oder auf dem Rad beteiligt waren, in 5 Jahren – zusammengezählt je Straßenstück.",
    explain: "Quelle: Unfallatlas der Statistischen Ämter. Wir zeigen nur Summen je Straßenstück, keine einzelnen Unfälle.",
    method: "#methode/sicherheit",
    entries: [
      { key: "acc-few", label: "1 Unfall", symbol: { type: "line", color: OVERLAY_COLORS.acc, width: 4, opacity: 0.5, casing: "none" } },
      { key: "acc-many", label: "10 und mehr Unfälle", symbol: { type: "line", color: OVERLAY_COLORS.acc, width: 11, opacity: 0.5, casing: "none" } },
    ].map((e) => ({ ...e, layer: "ov-acc" })),
  },
  fac: {
    group: "Orte im Viertel", title: "Schulen und Kitas",
    text: "Schulen und Kitas. In ihrer Nähe soll eine Straße ruhig und sicher sein.",
    explain: "Aus OpenStreetMap, solange die amtlichen Daten fehlen. Schulen und Kitas sind ein Grund, warum eine Hauptstraße Tempo 30 bekommen kann.",
    method: "#methode/aufgabe",
    entries: [{ key: "fac", layer: "ov-fac", label: "Schule oder Kita (Ring)", symbol: { type: "ring", color: OVERLAY_COLORS.fac } }],
  },
  // old links only (?ov=cyc together with a theme): still drawn and explained, but no switch in the panel
  cyc: {
    group: "Radverkehr", title: "Radnetz Hamburg (amtlich)", legacy: true,
    text: "Straßen im amtlichen Radnetz Hamburg. Das ganze amtliche Netz zeigt das Thema Radnetz, Ansicht „amtliches Netz“.",
    method: "#methode/radnetz",
    entries: [{ key: "cyc", layer: "ov-cyc", label: "im amtlichen Radnetz", symbol: { type: "line", color: OVERLAY_COLORS.cyc, width: 2, dash: [2, 1] } }],
  },
};
export const MAX_OVERLAYS = 3; // readability (prompt 28, confirmed 22.11.2026)

const lineSymbol = (g) => ({ type: "line", color: g.color, width: g.legendWidth ?? (typeof g.width === "number" ? g.width : 4), dash: g.dash, inner: g.inner });

/** Registry entry of a view (the map layer of theme/view). */
function viewLayer(layer, meta) {
  const info = LAYER_INFO[layer];
  const entries = groups(layer, meta).map((g) => ({
    key: g.key, label: g.label, layer: g.reference ? `ref-${g.key}` : `main-${g.key}`,
    symbol: g.kind === "symbol" ? { type: "shape", shape: g.shape, color: g.color } : lineSymbol(g),
    explain: explainOf(layer, g.key, meta),
  }));
  if (layer === "disc") {
    entries.push({ key: "disc-scale", label: "breiter = größere Abweichung", layer: null,
      symbol: { type: "scale", color: NEED, widths: [DISC_WIDTH.small, DISC_WIDTH.large] } });
  }
  if (layer === "cgap" && meta.overview?.mesh_gaps) {
    entries.unshift({ key: "gap-mesh", label: "Netz zu weitmaschig (Fläche)", layer: "gaps-fill", symbol: { type: "fill", color: NEED, dash: true } });
  }
  const notes = [];
  if (isCyclingLayer(layer) && meta.cycling?.disclaimer) notes.push({ kind: "note", text: meta.cycling.disclaimer });
  if (layer === "jct") notes.push({ kind: "muted", text: "Orange und größer: heutige Kreuzung passt nicht zum Ziel (Umbau nötig)." });
  if (layer === "coff" && meta.cycling?.official_attribution) notes.push({ kind: "muted", text: meta.cycling.official_attribution });
  return { id: `view:${layer}`, kind: "view", title: info.title, text: info.text, method: METHOD[layer], notes, entries };
}

/** Registry entry of an additional layer. */
export function overlayLayer(key) {
  const o = OVERLAY_LAYERS[key];
  return o ? { id: `layer:${key}`, kind: "overlay", key, removable: true, notes: [], ...o } : null;
}

/** Registry entry of a special place (prompts/26). */
function placeLayer(p, meta) {
  const c = p.theme.palette;
  return {
    id: `place:${p.id}`, kind: "place", key: p.id, group: "Besondere Orte", title: p.title, removable: true, notes: [],
    text: `${meta.special_places.texts.legend}. ${p.status_line ?? ""}`.trim(), method: "#orte",
    entries: [...new Map(p.measures.map((m) => [m.measure, m])).values()].map((m) => {
      const dashed = p.theme.pattern?.[m.measure] === "dashed";
      return { key: `place-${m.measure}`, layer: `main-place-${m.measure}`, label: `${m.label}${dashed ? " (gestrichelt)" : ""}`,
        symbol: { type: "line", color: c.main, casing: c.casing ?? CASING, width: 7, dash: dashed ? [1.5, 1] : null } };
    }),
  };
}

/** Always-on entries (rural areas, junction dots). */
function baseLayer(state, meta) {
  const entries = [];
  if (meta.rural_excluded?.length) {
    entries.push({ key: "rural", layer: "rural-fill", label: "auf dem Land – nicht bewertet", symbol: { type: "fill", color: RURAL_FILL },
      explain: "Die ländlichen Stadtteile haben wir nicht bewertet. Für Straßen außerorts gelten andere Regeln." });
  }
  if (meta.cycling && state.layer !== "jct") {
    entries.push({ key: "jctdot", layer: "main-jctdot", label: "Kreuzung (in diesem Thema ab Zoomstufe 14; antippen öffnet den Steckbrief)",
      symbol: { type: "circle", color: INK } });
  }
  return entries.length ? { id: "base", kind: "base", title: "Außerdem auf der Karte", notes: [], entries } : null;
}

/**
 * Everything the legend shows for a state, in drawing order: the view, then the additional layers, the special place,
 * the always-on entries. Layers that are off do not appear.
 * @returns {{id, kind, title, text, method, explain?, removable?, notes, entries: {key, label, layer, symbol, explain?}[]}[]}
 */
export function legendFor(state, meta) {
  const out = [viewLayer(state.layer, meta)];
  for (const k of state.overlays) { const o = overlayLayer(k); if (o) out.push(o); }
  const p = placeOf(state, meta);
  if (p) out.push(placeLayer(p, meta));
  const base = baseLayer(state, meta);
  if (base) out.push(base);
  return out;
}

/** Additional layers for the panel, grouped: [{group, items: [{key, title, text}]}]. */
export function overlayGroups() {
  const by = new Map();
  for (const [key, o] of Object.entries(OVERLAY_LAYERS)) {
    if (o.legacy) continue;
    if (!by.has(o.group)) by.set(o.group, []);
    by.get(o.group).push({ key, title: o.title, text: o.text });
  }
  return [...by].map(([group, items]) => ({ group, items }));
}

export const overlayTitle = (key) => OVERLAY_LAYERS[key]?.title ?? key;

/** Legend symbol as inline SVG (decorative: the text carries the meaning). */
export function symbolSvg(s, shapeSvg) {
  if (s.type === "shape") return shapeSvg(s.shape, s.color, 18);
  if (s.type === "fill") return `<svg aria-hidden="true" width="36" height="14"><rect x="2" y="1" width="32" height="12" fill="${s.color}" fill-opacity="${s.dash ? 0.2 : 0.35}" stroke="${s.color}"${s.dash ? ' stroke-dasharray="4 2"' : ""}/></svg>`;
  if (s.type === "circle") return `<svg aria-hidden="true" width="36" height="14"><circle cx="18" cy="7" r="3.5" fill="${s.color}" stroke="${CASING}" stroke-width="1.5"/></svg>`;
  if (s.type === "ring") return `<svg aria-hidden="true" width="36" height="14"><circle cx="18" cy="7" r="4.5" fill="${CASING}" stroke="${s.color}" stroke-width="2.5"/></svg>`;
  if (s.type === "scale") return s.widths.map((w) => `<svg aria-hidden="true" width="36" height="14"><line x1="2" y1="7" x2="34" y2="7" stroke="${CASING}" stroke-width="${w + 4}"/><line x1="2" y1="7" x2="34" y2="7" stroke="${s.color}" stroke-width="${w}"/></svg>`).join("");
  const w = Math.max(1.5, Math.min(s.width ?? 4, 11));
  const dash = s.dash ? ` stroke-dasharray="${s.dash.map((d) => d * 4).join(" ")}"` : "";
  const casing = s.casing === "none" ? "" : `<line x1="2" y1="7" x2="34" y2="7" stroke="${s.casing ?? CASING}" stroke-width="${w + 4}" stroke-linecap="round"/>`;
  const inner = s.inner ? `<line x1="2" y1="7" x2="34" y2="7" stroke="${s.inner.color}" stroke-width="${Math.max(1, s.inner.width)}"/>` : "";
  return `<svg aria-hidden="true" width="36" height="14">${casing}<line x1="2" y1="7" x2="34" y2="7" stroke="${s.color}" stroke-width="${w}"${s.opacity ? ` stroke-opacity="${s.opacity}"` : ""}${dash}/>${inner}</svg>`;
}
