// Map layers on the vector tiles (source "sfp", layers "segments" and "facilities"), legends and filters.
import {
  CASING, CATEGORY_STYLE, RURAL_FILL, DISC_TYPE_STYLE, FEASIBILITY_STYLE, OVERLAY_COLORS, SPEED_CLASSES, UNKNOWN, WIDTH_STYLE,
} from "./palette.js";

const SRC = "sfp";
const SEG = "segments";

/** MapLibre filter from the state (same logic as rowMatches in state.js). */
export function segmentFilter(state) {
  const f = ["all"];
  if (state.cats.length) f.push(["in", ["get", "cat"], ["literal", state.cats]]);
  if (state.dts.length) f.push(["in", ["coalesce", ["get", "dt"], "keine"], ["literal", state.dts]]);
  if (state.prmin > 0) f.push([">=", ["coalesce", ["get", "pr"], 0], state.prmin]);
  if (state.bz) f.push(["==", ["get", "bz"], state.bz]);
  return f;
}

const zoomWidth = (w) => ["interpolate", ["linear"], ["zoom"], 10, w * 0.4, 14, w, 17, w * 2];

/** Thematic groups of the active layer: [{key, label, filter, color, width, dash}] */
export function groups(layer, meta) {
  const known = (attr) => ["has", attr];
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
    id, type: "line", source: SRC, "source-layer": SEG, filter: ["all", g.filter, filter],
    layout: { "line-cap": g.dash ? "butt" : "round", "line-join": "round" },
    paint: { "line-color": g.color, "line-width": width, ...(g.dash ? { "line-dasharray": g.dash } : {}), ...extra },
  };
}

/** All SFP layers for the state, drawn in this order. */
export function sfpLayers(state, meta) {
  const filter = segmentFilter(state);
  const out = [];
  if (state.overlays.includes("acc")) {
    out.push({ id: "ov-acc", type: "line", source: SRC, "source-layer": SEG, filter: ["all", [">", ["get", "acc"], 0], filter],
      layout: { "line-cap": "round" },
      paint: { "line-color": OVERLAY_COLORS.acc, "line-opacity": 0.45,
        "line-width": ["interpolate", ["linear"], ["get", "acc"], 1, 8, 10, 22] } });
  }
  out.push({ id: "casing", type: "line", source: SRC, "source-layer": SEG, filter,
    layout: { "line-cap": "round", "line-join": "round" },
    paint: { "line-color": CASING, "line-width": zoomWidth(8) } });
  for (const g of groups(state.layer, meta)) out.push(lineLayer(`main-${g.key}`, g, filter));
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
  out.push({ id: "selected", type: "line", source: SRC, "source-layer": SEG, filter: ["==", ["get", "id"], state.seg ?? ""],
    paint: { "line-color": "#000000", "line-width": zoomWidth(10), "line-opacity": 0.35 } });
  return out;
}

export const LAYER_INFO = {
  cat: { title: "Soll-Kategorie", text: "Welche Funktion die Straße nach Duurzaam Veilig haben soll (Vorschlag)." },
  speed: { title: "Ist-Tempo", text: "Heute zulässige Höchstgeschwindigkeit (amtlich, sonst OpenStreetMap)." },
  disc: { title: "Diskrepanz", text: "Wo heutiges Tempo, Gestaltung oder Verkehrsmenge nicht zur Soll-Kategorie passen. Breitere Linie = stärkere Diskrepanz." },
  width: { title: "Straßenraumbreite", text: "Breite von Grundstücksgrenze zu Grundstücksgrenze an Engstellen." },
  feas: { title: "Machbarkeit", text: "Passt der Soll-Querschnitt der eigenen Kategorie in den Straßenraum?" },
  hvs: { title: "Hauptverkehrsstraßen (Vergleich)", text: "Hauptverkehrsstraßennetz der BVM zum Vergleich mit der Soll-Kategorie." },
};

export const OVERLAY_INFO = {
  bus: "Busverkehr (Fahrten je Werktag, Linienbreite)",
  cyc: "Radnetz Hamburg",
  fac: "Schulen und Kitas",
  acc: "Unfälle mit Fuß-/Radbeteiligung (Summe je Abschnitt, 5 Jahre)",
};

/** Legend as HTML (line samples as inline SVG, decorative; the text carries the meaning). */
export function legendHtml(layer, meta) {
  const items = groups(layer, meta).map((g) => {
    const dash = g.dash ? `stroke-dasharray="${g.dash.map((d) => d * 4).join(" ")}"` : "";
    const w = typeof g.width === "number" ? Math.max(2, Math.min(g.width, 6)) : 4;
    return `<li><svg aria-hidden="true" width="36" height="14"><line x1="2" y1="7" x2="34" y2="7" stroke="${CASING}" stroke-width="${w + 4}" stroke-linecap="round"/><line x1="2" y1="7" x2="34" y2="7" stroke="${g.color}" stroke-width="${w}" ${dash}/></svg><span>${g.label}</span></li>`;
  });
  if (meta.rural_excluded?.length) {
    items.push(`<li><svg aria-hidden="true" width="36" height="14"><rect x="2" y="1" width="32" height="12" fill="${RURAL_FILL}" fill-opacity="0.35" stroke="${RURAL_FILL}"/></svg><span>außerorts – nicht bewertet (ländliche Stadtteile)</span></li>`);
  }
  return `<ul class="legend">${items.join("")}</ul>`;
}
