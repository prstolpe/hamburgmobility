// Map layers and filters (the legend is built from legend_registry.js, prompt 28). Street function layers use source "sfp" (layers "segments" and "facilities");
// cycling layers (prompt 21) use source "cyc" (tiles/cycling.pmtiles: cycle_network, cycle_segments, cycle_official)
// and "jct" (tiles/junctions.pmtiles: junctions). map.js adds the cycling sources only when such a layer is shown.
// Special places (prompts/26) use the GeoJSON source "places" (special_places.geojson), loaded when a place is on.
import {
  CASING, CATEGORY_STYLE, CYCLE_CAT_STYLE, DISC_TYPE_STYLE, FACILITY_STYLE, FEASIBILITY_STYLE, FIT_STYLE, GAP_STYLE,
  INK, JUNCTION_STYLE, NEED, NONE, LANES_STYLE, OFFICIAL_STYLE, OVERLAY_COLORS, REFERENCE_COLOR, SHAPES, SPEED_CLASSES, UNKNOWN,
  WIDTH_STYLE,
} from "./palette.js";
import { CYCLING_LAYER_KEYS } from "./state.js";

const SRC = "sfp";
const SEG = "segments";
export const CYCLING_LAYERS = CYCLING_LAYER_KEYS;
// Source and source layer of each cycling layer (the official layer adds a reference group from cycle_network).
const CYCLING_SOURCE = {
  cnet: ["cyc", "cycle_network"], cfac: ["cyc", "cycle_segments"], cgap: ["cyc", "cycle_segments"],
  lanes: ["cyc", "cycle_segments"], cfit: ["cyc", "cycle_segments"], jct: ["jct", "junctions"], coff: ["cyc", "cycle_official"],
};
const JUNCTION_MIN_ZOOM = 12;

/** MapLibre filter from the state (same logic as rowMatches in state.js). */
export function segmentFilter(state) {
  const f = ["all"];
  if (state.cats.length) f.push(["in", ["get", "cat"], ["literal", state.cats]]);
  if (state.dts.length) f.push(["in", ["coalesce", ["get", "dt"], "keine"], ["literal", state.dts]]);
  if (state.prmin > 0) f.push([">=", ["coalesce", ["get", "pr"], 0], state.prmin]);
  if (state.bz) f.push(["==", ["get", "bz"], state.bz]);
  return f;
}

/** Cycling layers only filter by Bezirk (the official network has no Bezirk attribute). */
function cyclingFilter(state, srcLayer) {
  return state.bz && srcLayer !== "cycle_official" ? ["==", ["get", "bz"], state.bz] : ["all"];
}

const zoomWidth = (w) => ["interpolate", ["linear"], ["zoom"], 10, w * 0.4, 14, w, 17, w * 2];
// the same zoom scaling for a data-driven width expression (zoom must be the outermost input)
const zoomWidthExpr = (e) => ["interpolate", ["linear"], ["zoom"], 10, ["*", 0.4, e], 14, e, 17, ["*", 2, e]];
const known = (attr) => ["has", attr];
const notAssessed = (attr, label) => ({ key: `${attr}_unknown`, label, color: UNKNOWN, width: 1.2, dash: [1, 1.5], filter: ["!", known(attr)] });

function styled(table, attr, labels, fallback = (k) => k) {
  return Object.entries(table).map(([k, s]) => ({ key: `${attr}-${k}`, label: labels?.[k] ?? fallback(k), filter: ["==", ["get", attr], k], ...s }));
}

function cyclingGroups(layer, meta) {
  const c = meta.cycling ?? {};
  const [src, srcLayer] = CYCLING_SOURCE[layer];
  const at = (gs) => gs.map((g) => ({ src, srcLayer, ...g }));
  switch (layer) {
    case "cnet":
      return at(styled(CYCLE_CAT_STYLE, "cc", c.cycle_categories));
    case "cfac":
      return at(styled(FACILITY_STYLE, "fs", c.facility));
    case "cgap":
      return at([...styled(GAP_STYLE, "gap", c.gap), notAssessed("gap", c.gap?.not_assessed ?? "nicht bewertet")]
        .map((g) => (g.key === "gap_unknown" ? { ...g, filter: ["any", ["!", known("gap")], ["==", ["get", "gap"], "not_assessed"]] } : g)));
    case "lanes":
      return at([...styled(LANES_STYLE, "ld", c.lanes),
        { key: "ld-ist_unknown", label: c.lanes?.ist_unknown ?? "heute unbekannt", color: UNKNOWN, width: 1.5, dash: [1, 1.5],
          filter: ["==", ["get", "ld"], "ist_unknown"] }]);
    case "cfit":
      return at([...styled(FIT_STYLE, "fit", c.fit), notAssessed("fit", "nicht bewertet (keine Breite oder kein Soll-Profil)")]);
    case "jct":
      return at(Object.entries(JUNCTION_STYLE).map(([k, s]) => ({
        key: `grp-${k}`, label: c.junction_group?.[k] ?? k, kind: "symbol", icon: `jct-${k}`, filter: ["==", ["get", "grp"], k], ...s,
      })));
    case "coff":
      return [
        { key: "ref", label: "Radnetz im Ziel: Radvorrangrouten und Radrouten (Entwurf, zum Vergleich)", color: REFERENCE_COLOR, width: 2, dash: null,
          reference: true, src: "cyc", srcLayer: "cycle_network", filter: ["in", ["get", "cc"], ["literal", ["RSV", "HAUPT"]]] },
        ...at(styled(OFFICIAL_STYLE, "grp", c.official_status)),
      ];
    default:
      return [];
  }
}

// Legend of "Abweichung" (prompt 25, item 5, variant a chosen): one statement per type (dash), the strength as width.
// Display only: the strength classes group disc_max (0.5 steps) into three widths, rules and data unchanged.
export const DISC_WIDTH = { small: 2.5, medium: 4.5, large: 7 }; // below 1.5, 1.5 to below 2.5, from 2.5
const dm = ["coalesce", ["get", "dm"], 0];
const discWidth = zoomWidthExpr(["step", dm, DISC_WIDTH.small, 1.5, DISC_WIDTH.medium, 2.5, DISC_WIDTH.large]);
const DISC_TEXT = {
  D1: "Heute zu schnell oder gebaut wie eine Hauptstraße",
  D2: "Hauptstraße, aber es fehlt Gestaltung, z. B. ein Radweg",
  D3: "beides",
};

function discGroups(meta) {
  return [
    ...Object.entries(DISC_TYPE_STYLE).map(([t, s]) => ({
      key: t, label: DISC_TEXT[t] ?? meta.glossary?.terms?.[t]?.plain ?? meta.discrepancy_types[t], filter: ["==", ["get", "dt"], t],
      color: s.color, dash: s.dash, width: discWidth, legendWidth: 4,
    })),
    { key: "none", label: "passt bereits", color: NONE, width: 1.2, dash: null, filter: ["all", ["!", known("dt")], known("dm")] },
    { key: "unchecked", label: "nicht prüfbar (Angaben fehlen)", color: UNKNOWN, width: 1.2, dash: [1, 1.5], filter: ["!", known("dm")] },
  ];
}

/** Thematic groups of the active layer: [{key, label, filter, color, width, dash, src?, srcLayer?, kind?, reference?}] */
export function groups(layer, meta) {
  if (CYCLING_LAYERS.includes(layer)) return cyclingGroups(layer, meta);
  switch (layer) {
    case "cat":
      // only categories that occur in the data (GOW80/ETW60 stay out while rural Stadtteile are not classified)
      return Object.entries(CATEGORY_STYLE).filter(([cat]) => !meta.categories_present || meta.categories_present.includes(cat)).map(([cat, s]) => ({
        key: cat, label: meta.categories[cat]?.label ?? cat, filter: ["==", ["get", "cat"], cat], ...s,
      }));
    case "speed": {
      let lower = -Infinity;
      const out = SPEED_CLASSES.map((c) => {
        const g = { key: `s${c.max}`, label: c.label, color: c.color, width: c.width, dash: c.dash,
          filter: ["all", known("spd"), [">", ["get", "spd"], lower], ["<=", ["get", "spd"], c.max === Infinity ? 999 : c.max]] };
        lower = c.max;
        return g;
      });
      out.push({ key: "s_unknown", label: "unbekannt", color: UNKNOWN, width: 1.5, dash: [1, 1.5], filter: ["!", known("spd")] });
      return out;
    }
    case "disc":
      return discGroups(meta);
    case "width": {
      const lo = meta.width_classes_m.ETW30;
      const hi = meta.width_classes_m.GOW50;
      const fmt = (x) => x.toLocaleString("de-DE", { maximumFractionDigits: 1 });
      return [
        { key: "narrow", label: `unter ${fmt(lo)} m (weniger als eine Quartiersstraße braucht)`, width: 3, ...WIDTH_STYLE.narrow,
          filter: ["all", known("w"), ["<", ["get", "w"], lo]] },
        { key: "middle", label: `${fmt(lo)} bis unter ${fmt(hi)} m`, width: 3, ...WIDTH_STYLE.middle,
          filter: ["all", known("w"), [">=", ["get", "w"], lo], ["<", ["get", "w"], hi]] },
        { key: "wide", label: `ab ${fmt(hi)} m (Platz für eine Stadtmagistrale mit Radweg)`, width: 3, ...WIDTH_STYLE.wide,
          filter: ["all", known("w"), [">=", ["get", "w"], hi]] },
        { key: "w_unknown", label: "nicht gemessen", color: UNKNOWN, width: 1.2, dash: [1, 1.5], filter: ["!", known("w")] },
      ];
    }
    case "feas":
      return [
        ...Object.entries(FEASIBILITY_STYLE).map(([k, s]) => ({
          key: k, label: `Soll-Querschnitt ${meta.feasibility[k]}`, filter: ["==", ["get", "fe"], k], width: 3.5, ...s,
        })),
        { key: "fe_unknown", label: "nicht bewertet", color: UNKNOWN, width: 1.2, dash: [1, 1.5], filter: ["!", known("fe")] },
      ];
    case "prio": {
      // display classes from config/project.yaml web.overview.prio_classes (priority 0–3 = deviation x risk)
      const [lo, hi] = meta.overview?.params?.prio_classes ?? [1, 2];
      const pr = ["coalesce", ["get", "pr"], 0];
      return [
        { key: "p3", label: "dringend", color: NEED, width: 4.5, dash: null, filter: [">=", pr, hi] },
        { key: "p2", label: "mittel", color: NEED, width: 3, dash: [2, 1.5], filter: ["all", [">=", pr, lo], ["<", pr, hi]] },
        { key: "p1", label: "gering oder keine", color: NONE, width: 1.5, dash: null, filter: ["<", pr, lo] },
      ];
    }
    case "hvs":
      return [
        { key: "hvs1", label: "Hauptverkehrsstraße (BVM, Verkehrsmengenkarte 2019)", color: INK, width: 5, dash: null,
          filter: ["==", ["get", "hvs"], 1] },
        { key: "hvs0", label: "andere Straße", color: UNKNOWN, width: 1.2, dash: null, filter: ["!=", ["get", "hvs"], 1] },
      ];
    default:
      return [];
  }
}

function lineLayer(id, g, filter, extra = {}) {
  const width = typeof g.width === "number" ? zoomWidth(g.width) : g.width;
  return {
    id, type: "line", source: g.src ?? SRC, "source-layer": g.srcLayer ?? SEG, filter: ["all", g.filter, filter],
    layout: { "line-cap": g.dash ? "butt" : "round", "line-join": "round" },
    paint: { "line-color": g.color, "line-width": width, ...(g.dash ? { "line-dasharray": g.dash } : {}), ...extra },
  };
}

function symbolLayer(id, g, filter) {
  return {
    id, type: "symbol", source: g.src, "source-layer": g.srcLayer, minzoom: JUNCTION_MIN_ZOOM, filter: ["all", g.filter, filter],
    layout: { "icon-image": ["case", ["==", ["get", "act"], 1], `${g.icon}-act`, g.icon], "icon-allow-overlap": true, "icon-ignore-placement": true,
      "icon-size": ["case", ["==", ["get", "act"], 1], 1, 0.7] },
  };
}

/** Is the layer drawn from the cycling tiles? */
export const isCyclingLayer = (layer) => CYCLING_LAYERS.includes(layer);

/** All map layers for the state, drawn in this order. */
export function sfpLayers(state, meta) {
  const filter = segmentFilter(state);
  const out = [];
  const cycling = isCyclingLayer(state.layer) && meta.cycling;
  if (state.overlays.includes("acc")) {
    out.push({ id: "ov-acc", type: "line", source: SRC, "source-layer": SEG, filter: ["all", [">", ["get", "acc"], 0], filter],
      layout: { "line-cap": "round" },
      paint: { "line-color": OVERLAY_COLORS.acc, "line-opacity": 0.5,
        "line-width": ["interpolate", ["linear"], ["get", "acc"], 1, 8, 10, 22] } });
  }
  if (cycling && state.layer === "cgap" && meta.overview?.mesh_gaps) {
    // network gaps: meshes wider than planned (data/out/cycle_mesh_gaps.geojson), under the lines
    out.push({ id: "gaps-fill", type: "fill", source: "gaps", filter: state.bz ? ["==", ["get", "bezirk"], state.bz] : ["all"],
      paint: { "fill-color": NEED, "fill-opacity": 0.14 } });
    out.push({ id: "gaps-line", type: "line", source: "gaps", filter: state.bz ? ["==", ["get", "bezirk"], state.bz] : ["all"],
      paint: { "line-color": NEED, "line-width": 1, "line-dasharray": [3, 2] } });
  }
  if (cycling) {
    const gs = groups(state.layer, meta);
    for (const g of gs.filter((x) => x.reference)) out.push(lineLayer(`ref-${g.key}`, g, cyclingFilter(state, g.srcLayer), { "line-opacity": 0.45 }));
    const lines = gs.filter((x) => !x.reference && x.kind !== "symbol");
    const casings = [...new Set(lines.map((g) => `${g.src}|${g.srcLayer}`))];
    for (const key of casings) {
      const [src, srcLayer] = key.split("|");
      out.push({ id: `casing-${srcLayer}`, type: "line", source: src, "source-layer": srcLayer, filter: cyclingFilter(state, srcLayer),
        layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": CASING, "line-width": zoomWidth(7) } });
    }
    for (const g of lines) {
      out.push(lineLayer(`main-${g.key}`, g, cyclingFilter(state, g.srcLayer)));
      // Radvorrangroute: white centre stripe on top (double line), so the level does not depend on width alone
      if (g.inner) out.push(lineLayer(`main-${g.key}-inner`, { ...g, color: g.inner.color, width: g.inner.width, dash: null }, cyclingFilter(state, g.srcLayer)));
    }
    for (const g of gs.filter((x) => x.kind === "symbol")) out.push(symbolLayer(`main-${g.key}`, g, cyclingFilter(state, g.srcLayer)));
  } else {
    out.push({ id: "casing", type: "line", source: SRC, "source-layer": SEG, filter,
      layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": CASING, "line-width": zoomWidth(state.layer === "disc" ? 10 : 8) } }); // disc: up to 7 px lines
    for (const g of groups(state.layer, meta)) out.push(lineLayer(`main-${g.key}`, g, filter));
  }
  if (state.overlays.includes("bus")) {
    out.push({ id: "ov-bus", type: "line", source: SRC, "source-layer": SEG, filter: ["all", [">", ["get", "bus"], 0], filter],
      paint: { "line-color": OVERLAY_COLORS.bus, "line-offset": 5,
        "line-width": ["interpolate", ["linear"], ["get", "bus"], 1, 1, 300, 5] } });
  }
  if (state.overlays.includes("cyc")) {
    out.push({ id: "ov-cyc", type: "line", source: SRC, "source-layer": SEG, filter: ["all", ["==", ["get", "cyc"], 1], filter],
      paint: { "line-color": OVERLAY_COLORS.cyc, "line-offset": -5, "line-width": 2, "line-dasharray": [2, 1] } });
  }
  if (state.overlays.includes("fac")) {
    out.push({ id: "ov-fac", type: "circle", source: SRC, "source-layer": "facilities",
      paint: { "circle-color": CASING, "circle-radius": 4.5, "circle-stroke-color": OVERLAY_COLORS.fac, "circle-stroke-width": 2.5 } }); // ring
  }
  if (meta.cycling && state.layer !== "jct") {
    // junctions stay tappable in every theme from zoom 14 (small dots)
    out.push({ id: "main-jctdot", type: "circle", source: "jct", "source-layer": "junctions", minzoom: 14,
      filter: cyclingFilter(state, "junctions"),
      paint: { "circle-radius": 3.5, "circle-color": INK, "circle-stroke-color": CASING, "circle-stroke-width": 1.5 } });
  }
  if (state.place) out.push(...placeLayers(state, meta));
  const segLayer = cycling && CYCLING_SOURCE[state.layer][1] === "cycle_segments" ? ["cyc", "cycle_segments"] : [SRC, SEG];
  // selection (prompt 28): a dark halo under the lines plus a thin ink core on top – clear in every theme
  const selFilter = ["==", ["get", "id"], state.seg ?? ""];
  out.unshift({ id: "selected-halo", type: "line", source: segLayer[0], "source-layer": segLayer[1], filter: selFilter,
    layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": INK, "line-width": zoomWidth(18), "line-opacity": 0.3 } });
  out.push({ id: "selected", type: "line", source: segLayer[0], "source-layer": segLayer[1], filter: selFilter,
    layout: { "line-cap": "round" }, paint: { "line-color": INK, "line-width": zoomWidth(2.5), "line-opacity": 0.9 } });
  if (meta.cycling) {
    out.push({ id: "selected-jct", type: "circle", source: "jct", "source-layer": "junctions", filter: ["==", ["get", "id"], state.jct ?? ""],
      paint: { "circle-radius": 14, "circle-color": "rgba(0,0,0,0)", "circle-stroke-color": INK, "circle-stroke-width": 3 } });
  }
  return out;
}

/** The place of the state from meta.special_places, or null. */
export const placeOf = (state, meta) => meta.special_places?.places?.find((p) => p.id === state.place) ?? null;

/** Special place (prompts/26): a line in the colour of the place on a white casing – solid for a cycle street, dashed
 * for a pedestrian zone (the measure is told by pattern, not colour alone). No glow, no 3D, no animation. */
export function placeLayers(state, meta) {
  const p = placeOf(state, meta);
  if (!p) return [];
  const c = p.theme.palette;
  const own = ["==", ["get", "place"], p.id];
  const out = [{ id: "place-casing", type: "line", source: "places", filter: own, layout: { "line-cap": "round", "line-join": "round" },
    paint: { "line-color": c.casing ?? CASING, "line-width": zoomWidth(11) } }];
  for (const m of [...new Set(p.measures.map((x) => x.measure))]) {
    const dashed = p.theme.pattern?.[m] === "dashed";
    out.push({ id: `main-place-${m}`, type: "line", source: "places", filter: ["all", own, ["==", ["get", "measure"], m]],
      layout: { "line-cap": dashed ? "butt" : "round", "line-join": "round" },
      paint: { "line-color": c.main, "line-width": zoomWidth(7), ...(dashed ? { "line-dasharray": [1.5, 1] } : {}) } });
  }
  return out;
}

// Basemap labels above the data (prompt 25): Stadtteil and place names get a white halo and darker text, minor
// street names only from zoom 15 so they do not cover the data lines.
const LABEL_TUNING = {
  places_subplace: { paint: { "text-color": "#4a4a4a" /* token text2 */, "text-halo-color": CASING, "text-halo-width": 2 } },
  places_locality: { paint: { "text-halo-color": CASING, "text-halo-width": 2 } },
  roads_labels_minor: { minzoom: 15, paint: { "text-halo-color": CASING, "text-halo-width": 1.5 } },
  roads_labels_major: { paint: { "text-halo-color": CASING, "text-halo-width": 1.5 } },
};

export function tuneLabels(layers) {
  return layers.map((l) => {
    const t = LABEL_TUNING[l.id];
    return t ? { ...l, ...(t.minzoom ? { minzoom: Math.max(t.minzoom, l.minzoom ?? 0) } : {}), paint: { ...l.paint, ...t.paint } } : l;
  });
}

/** Id of the first basemap label layer: data layers are inserted below it, so names stay readable. */
export const firstSymbolId = (layers) => layers.find((l) => l.type === "symbol")?.id;

/** Junction symbols stay on top of the labels (they are the data of the junction view). */
export const beforeIdFor = (layer, labelId) => (layer.type === "symbol" ? undefined : labelId);

// One sentence per view, plain language (docs/redesign/04_language.md); titles of the views are in state.js THEMES.
export const LAYER_INFO = {
  cat: { title: "Aufgabe der Straße", text: "Welche Aufgabe jede Straße haben soll. Die Farbe zeigt das Tempo im Ziel, die Breite, wie stark die Straße verbindet." },
  speed: { title: "Tempo heute", text: "Welches Tempo heute gilt (amtlich, sonst OpenStreetMap). Gleiche Farben wie im Ziel: So sieht man, wo sich das Tempo ändert." },
  disc: { title: "Abweichung", text: "Wo die Straße heute nicht zu ihrer Aufgabe passt, zum Beispiel weil das Tempo zu hoch ist." },
  prio: { title: "Dringlichkeit", text: "Wo eine Abweichung und viele Unfälle, Schulen oder Radverkehr zusammenkommen." },
  width: { title: "Breite der Straße", text: "Breite von Grundstück zu Grundstück an der engsten Stelle. Breite Linie heißt: breite Straße." },
  feas: { title: "Regelprofil der Aufgabe", text: "Passt die Regel-Aufteilung der Aufgabe in die Straße? Ohne Radweg-Details." },
  hvs: { title: "Hauptverkehrsstraßen (Vergleich)", text: "Die amtliche Liste der Hauptverkehrsstraßen zum Vergleich mit der Aufgabe im Entwurf." },
  cnet: { title: "Radnetz im Ziel", cycling: true, text: "Das vorgeschlagene Radnetz. Eine breite Linie heißt: wichtige Route." },
  cfac: { title: "Radweg im Ziel", cycling: true, text: "Welche Art Radweg die Straße im Ziel haben soll – nach der Prüfung, ob der Platz reicht." },
  cgap: { title: "Lücken", cycling: true, text: "Wo auf dem Radnetz ein passender Radweg fehlt, und wo das Netz zu weitmaschig ist." },
  lanes: { title: "Fahrstreifen", cycling: true, text: "Wie viele Fahrstreifen für Autos die Straße im Ziel hat – und wo es weniger sind als heute." },
  cfit: { title: "Passt das Ziel?", cycling: true, text: "Passen Gehwege, Radweg, Fahrbahn, Bäume und Parken des Ziels in die Straße?" },
  jct: { title: "Kreuzungen", cycling: true, text: "Welche Art Kreuzung das Ziel ist. Die Form zeigt die Art, Orange heißt: Umbau nötig. Sichtbar ab Zoomstufe 12." },
  coff: { title: "Amtliches Radnetz", cycling: true, text: "Das amtliche Radnetz Hamburg zum Vergleich; darunter hell das vorgeschlagene Radnetz." },
};

/** Symbol of a shape as inline SVG (decorative). */
export function shapeSvg(shape, color, size = 16) {
  const s = SHAPES[shape];
  const paint = s.mode === "fill" ? `fill="${color}" stroke="${CASING}" stroke-width="1"` : `fill="none" stroke="${color}" stroke-width="2.5"`;
  return `<svg aria-hidden="true" width="${size}" height="${size}" viewBox="0 0 16 16"><path d="${s.d}" ${paint}/></svg>`;
}
