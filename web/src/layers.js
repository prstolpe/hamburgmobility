// Map layers, legends and filters. Street function layers use source "sfp" (layers "segments" and "facilities");
// cycling layers (prompt 21) use source "cyc" (tiles/cycling.pmtiles: cycle_network, cycle_segments, cycle_official)
// and "jct" (tiles/junctions.pmtiles: junctions). map.js adds the cycling sources only when such a layer is shown.
import {
  CASING, CATEGORY_STYLE, CYCLE_CAT_STYLE, DISC_TYPE_STYLE, FACILITY_STYLE, FEASIBILITY_STYLE, FIT_STYLE, GAP_STYLE,
  JUNCTION_STYLE, LANES_STYLE, OFFICIAL_STYLE, OVERLAY_COLORS, REFERENCE_COLOR, RURAL_FILL, SHAPES, SPEED_CLASSES, UNKNOWN,
  WIDTH_STYLE,
} from "./palette.js";
import { CYCLING_LAYER_KEYS } from "./state.js";
import { esc } from "./util.js";

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
      return at(styled(CYCLE_CAT_STYLE, "cc", c.cycle_categories).map((g) => ({ ...g, label: `${g.key.slice(3)} – ${g.label}` })));
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
        { key: "ref", label: "Soll-Radnetz RSV/HAUPT (Entwurf, zum Vergleich)", color: REFERENCE_COLOR, width: 2, dash: null,
          reference: true, src: "cyc", srcLayer: "cycle_network", filter: ["in", ["get", "cc"], ["literal", ["RSV", "HAUPT"]]] },
        ...at(styled(OFFICIAL_STYLE, "grp", c.official_status)),
      ];
    default:
      return [];
  }
}

/** Thematic groups of the active layer: [{key, label, filter, color, width, dash, src?, srcLayer?, kind?, reference?}] */
export function groups(layer, meta) {
  if (CYCLING_LAYERS.includes(layer)) return cyclingGroups(layer, meta);
  switch (layer) {
    case "cat":
      // only categories that occur in the data (GOW80/ETW60 stay out while rural Stadtteile are not classified)
      return Object.entries(CATEGORY_STYLE).filter(([cat]) => !meta.categories_present || meta.categories_present.includes(cat)).map(([cat, s]) => ({
        key: cat, label: `${cat} – ${meta.categories[cat]?.label ?? cat}`, filter: ["==", ["get", "cat"], cat], ...s,
      }));
    case "speed": {
      let lower = -Infinity;
      const out = SPEED_CLASSES.map((c) => {
        const g = { key: `s${c.max}`, label: c.label, color: c.color, width: 3, dash: null,
          filter: ["all", known("spd"), [">", ["get", "spd"], lower], ["<=", ["get", "spd"], c.max === Infinity ? 999 : c.max]] };
        lower = c.max;
        return g;
      });
      out.push({ key: "s_unknown", label: "unbekannt", color: UNKNOWN, width: 1.5, dash: [1, 1.5], filter: ["!", known("spd")] });
      return out;
    }
    case "disc":
      return [
        ...Object.entries(DISC_TYPE_STYLE).map(([t, s]) => ({
          key: t, label: `${t} – ${meta.discrepancy_types[t]}`, filter: ["==", ["get", "dt"], t], color: s.color, dash: s.dash,
          width: ["match", ["get", "dm"], 3, 6, 2, 4.5, 3],
        })),
        { key: "none", label: "keine Diskrepanz", color: UNKNOWN, width: 1.2, dash: null,
          filter: ["all", ["!", known("dt")], known("dm")] },
        { key: "unchecked", label: "nicht prüfbar", color: UNKNOWN, width: 1.2, dash: [1, 1.5], filter: ["!", known("dm")] },
      ];
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
    case "hvs":
      return [
        { key: "hvs1", label: "Hauptverkehrsstraße (BVM, Verkehrsmengenkarte 2019)", color: "#332288", width: 5, dash: null,
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
    layout: { "icon-image": g.icon, "icon-allow-overlap": true, "icon-ignore-placement": true,
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
      paint: { "line-color": OVERLAY_COLORS.acc, "line-opacity": 0.45,
        "line-width": ["interpolate", ["linear"], ["get", "acc"], 1, 8, 10, 22] } });
  }
  if (cycling) {
    const gs = groups(state.layer, meta);
    for (const g of gs.filter((x) => x.reference)) out.push(lineLayer(`ref-${g.key}`, g, cyclingFilter(state, g.srcLayer)));
    const lines = gs.filter((x) => !x.reference && x.kind !== "symbol");
    const casings = [...new Set(lines.map((g) => `${g.src}|${g.srcLayer}`))];
    for (const key of casings) {
      const [src, srcLayer] = key.split("|");
      out.push({ id: `casing-${srcLayer}`, type: "line", source: src, "source-layer": srcLayer, filter: cyclingFilter(state, srcLayer),
        layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": CASING, "line-width": zoomWidth(7) } });
    }
    for (const g of lines) out.push(lineLayer(`main-${g.key}`, g, cyclingFilter(state, g.srcLayer)));
    for (const g of gs.filter((x) => x.kind === "symbol")) out.push(symbolLayer(`main-${g.key}`, g, cyclingFilter(state, g.srcLayer)));
  } else {
    out.push({ id: "casing", type: "line", source: SRC, "source-layer": SEG, filter,
      layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": CASING, "line-width": zoomWidth(8) } });
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
      paint: { "circle-color": OVERLAY_COLORS.fac, "circle-radius": 5, "circle-stroke-color": CASING, "circle-stroke-width": 2 } });
  }
  const segLayer = cycling && CYCLING_SOURCE[state.layer][1] === "cycle_segments" ? ["cyc", "cycle_segments"] : [SRC, SEG];
  out.push({ id: "selected", type: "line", source: segLayer[0], "source-layer": segLayer[1], filter: ["==", ["get", "id"], state.seg ?? ""],
    paint: { "line-color": "#000000", "line-width": zoomWidth(10), "line-opacity": 0.35 } });
  if (cycling && state.layer === "jct") {
    out.push({ id: "selected-jct", type: "circle", source: "jct", "source-layer": "junctions", filter: ["==", ["get", "id"], state.jct ?? ""],
      paint: { "circle-radius": 14, "circle-color": "rgba(0,0,0,0)", "circle-stroke-color": "#000000", "circle-stroke-width": 3 } });
  }
  return out;
}

export const LAYER_INFO = {
  cat: { title: "Soll-Kategorie", text: "Welche Funktion die Straße nach Duurzaam Veilig haben soll (Vorschlag)." },
  speed: { title: "Ist-Tempo", text: "Heute zulässige Höchstgeschwindigkeit (amtlich, sonst OpenStreetMap)." },
  disc: { title: "Diskrepanz", text: "Wo heutiges Tempo, Gestaltung oder Verkehrsmenge nicht zur Soll-Kategorie passen. Breitere Linie = stärkere Diskrepanz." },
  width: { title: "Straßenraumbreite", text: "Breite von Grundstücksgrenze zu Grundstücksgrenze an Engstellen." },
  feas: { title: "Machbarkeit", text: "Passt der Soll-Querschnitt der eigenen Kategorie in den Straßenraum?" },
  hvs: { title: "Hauptverkehrsstraßen (Vergleich)", text: "Hauptverkehrsstraßennetz der BVM zum Vergleich mit der Soll-Kategorie." },
  cnet: { title: "Radnetz (Soll)", cycling: true,
    text: "Vorgeschlagenes Radnetz in vier Ebenen: Radschnellverbindung, Radroute, Bezirksroute und Quartiersnetz." },
  cfac: { title: "Radanlagen (Soll)", cycling: true,
    text: "Welche Radverkehrsanlage der Abschnitt nach dem Entwurf haben soll – nach der Prüfung, ob der Platz reicht." },
  cgap: { title: "Radanlagen Soll/Ist", cycling: true,
    text: "Wo die heutige Radanlage (aus OpenStreetMap) fehlt, eine andere ist als im Soll oder zu schmal ist." },
  lanes: { title: "Fahrstreifen Soll/Ist", cycling: true,
    text: "Kfz-Fahrstreifen je Richtung im Soll-Querschnitt im Vergleich zu heute." },
  cfit: { title: "Querschnitt passt?", cycling: true,
    text: "Passen Gehwege, Radanlage, Fahrbahn, Bäume und Parken des Soll-Querschnitts in den Straßenraum?" },
  jct: { title: "Knotenpunkte", cycling: true,
    text: "Vorgeschlagener Knotentyp; Form und Farbe zeigen den Typ, größere Zeichen: Umbau nötig. Sichtbar ab Zoomstufe 12." },
  coff: { title: "Radnetz Hamburg (amtlich)", cycling: true,
    text: "Amtliches Radnetz Hamburg zum Vergleich; grau darunter das vorgeschlagene Soll-Radnetz (Radschnellverbindungen und Radrouten)." },
};

export const OVERLAY_INFO = {
  bus: "Busverkehr (Fahrten je Werktag, Linienbreite)",
  cyc: "Radnetz Hamburg",
  fac: "Schulen und Kitas",
  acc: "Unfälle mit Fuß-/Radbeteiligung (Summe je Abschnitt, 5 Jahre)",
};

/** Symbol of a shape as inline SVG (decorative). */
export function shapeSvg(shape, color, size = 16) {
  const s = SHAPES[shape];
  const paint = s.mode === "fill" ? `fill="${color}" stroke="${CASING}" stroke-width="1"` : `fill="none" stroke="${color}" stroke-width="2.5"`;
  return `<svg aria-hidden="true" width="${size}" height="${size}" viewBox="0 0 16 16"><path d="${s.d}" ${paint}/></svg>`;
}

/** Legend as HTML (line samples as inline SVG, decorative; the text carries the meaning). */
export function legendHtml(layer, meta) {
  const items = groups(layer, meta).map((g) => {
    if (g.kind === "symbol") return `<li>${shapeSvg(g.shape, g.color, 18)}<span>${esc(g.label)}</span></li>`;
    const dash = g.dash ? `stroke-dasharray="${g.dash.map((d) => d * 4).join(" ")}"` : "";
    const w = typeof g.width === "number" ? Math.max(2, Math.min(g.width, 6)) : 4;
    return `<li><svg aria-hidden="true" width="36" height="14"><line x1="2" y1="7" x2="34" y2="7" stroke="${CASING}" stroke-width="${w + 4}" stroke-linecap="round"/><line x1="2" y1="7" x2="34" y2="7" stroke="${g.color}" stroke-width="${w}" ${dash}/></svg><span>${esc(g.label)}</span></li>`;
  });
  if (meta.rural_excluded?.length) {
    items.push(`<li><svg aria-hidden="true" width="36" height="14"><rect x="2" y="1" width="32" height="12" fill="${RURAL_FILL}" fill-opacity="0.35" stroke="${RURAL_FILL}"/></svg><span>außerorts – nicht bewertet (ländliche Stadtteile)</span></li>`);
  }
  const notes = [];
  if (isCyclingLayer(layer) && meta.cycling) {
    notes.push(`<p class="note">${esc(meta.cycling.disclaimer)}</p>`);
    if (layer === "jct") notes.push('<p class="muted">Größere Zeichen: heutiger Knoten passt nicht zum Soll (Umbau nötig).</p>');
    if (layer === "coff") notes.push(`<p class="muted">${esc(meta.cycling.official_attribution ?? "")}</p>`);
  }
  return `${notes.join("")}<ul class="legend">${items.join("")}</ul>`;
}
