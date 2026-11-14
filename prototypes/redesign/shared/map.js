// Map for the redesign prototypes (prompt 24, A3): five themes with two to three views each instead of 13 layers,
// colours from docs/redesign/tokens.json (one meaning per colour). Same data as the website: Protomaps basemap
// (grayscale) and the SFP vector tiles in data/out, limited to the focus Bezirk. Read-only on web/src.
import { layers as basemapLayers, namedFlavor } from "@protomaps/basemaps";
import * as maplibregl from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { SHAPES } from "../../../web/src/palette.js";

maplibregl.setWorkerUrl(workerUrl);
maplibregl.addProtocol("pmtiles", new Protocol().tile);
const url = (p) => new URL(p, `${location.origin}/`).href;

export const T = {
  ink: "#111111", casing: "#ffffff", need: "#B35900", none: "#8a8a8a", unknown: "#767676", cyc: "#007A6E",
  speed: { 20: "#117733", 30: "#0077BB", 40: "#AA4499", 50: "#CC3311", 99: "#332288" },
};
const FUNCTION = { SW: { w: 7, dash: null, kmh: 99 }, GOW50: { w: 5, dash: null, kmh: 50 }, GOW30: { w: 5, dash: [3, 1.5], kmh: 30 },
  ETW30: { w: 2.5, dash: null, kmh: 30 }, ETW_ERF: { w: 2.5, dash: [0.6, 1.4], kmh: 20 } };
export const PLAIN_CAT = { SW: "Schnellstraße", GOW50: "Hauptstraße mit Tempo 50", GOW30: "Hauptstraße mit Tempo 30",
  ETW30: "Wohnstraße mit Tempo 30", ETW_ERF: "Fußgängerzone oder Spielstraße" };
const zw = (w) => ["interpolate", ["linear"], ["zoom"], 10, w * 0.4, 14, w, 17, w * 2];
const NEED = {
  strong: { color: T.need, w: 4.5, dash: null }, partial: { color: T.need, w: 3, dash: [2, 1.5] },
  none: { color: T.none, w: 1.5, dash: null }, unknown: { color: T.unknown, w: 1.5, dash: [0.6, 1.4] },
};

export const THEMES = {
  aufgabe: { title: "Aufgabe und Tempo", views: { ziel: "Ziel", heute: "heute" },
    intro: { ziel: "Welche Aufgabe jede Straße haben soll. Farbe = Tempo im Ziel, Breite = wie stark die Straße verbindet.",
      heute: "Welches Tempo heute gilt. Gleiche Farben wie im Ziel: So sieht man, wo sich das Tempo ändert." } },
  abweichung: { title: "Heute und Ziel", views: { ziel: "Abweichung", prio: "Dringlichkeit" },
    intro: { ziel: "Wo die Straße heute nicht zu ihrer Aufgabe passt: Tempo, Gestaltung oder Verkehrsmenge.",
      prio: "Wo eine Abweichung und viele Unfälle, Schulen oder Radverkehr zusammenkommen." } },
  platz: { title: "Platz in der Straße", views: { ziel: "Passt das Ziel?", fahrstreifen: "Fahrstreifen" },
    intro: { ziel: "Passen Gehwege, Radweg, Fahrbahn, Bäume und Parken des Ziels in den Straßenraum?",
      fahrstreifen: "Wo das Ziel weniger Fahrstreifen für Autos hat als heute." } },
  rad: { title: "Radnetz", views: { ziel: "Ziel", luecken: "Lücken", amtlich: "amtliches Netz" },
    intro: { ziel: "Das vorgeschlagene Radnetz in vier Stufen. Breite Linie = wichtige Route.",
      luecken: "Wo auf dem Radnetz ein passender Radweg fehlt, und wo das Netz zu weitmaschig ist.",
      amtlich: "Das amtliche Radnetz Hamburg im Vergleich zum Vorschlag." } },
  knoten: { title: "Kreuzungen", views: { ziel: "Ziel" },
    intro: { ziel: "Welche Art Kreuzung das Ziel ist. Die Form zeigt die Art, Orange: Umbau nötig." } },
};

/** Legend groups of a theme view: [{label, color, w, dash, filter, src, sl, kind?, shape?}] */
export function groups(theme, view, meta) {
  const seg = (g) => ({ src: "sfp", sl: "segments", ...g });
  const cyc = (g) => ({ src: "cyc", sl: "cycle_segments", ...g });
  const present = (meta.categories_present ?? Object.keys(FUNCTION)).filter((k) => FUNCTION[k]);
  if (theme === "aufgabe" && view === "ziel") {
    return present.map((k) => seg({ label: PLAIN_CAT[k], color: T.speed[FUNCTION[k].kmh], w: FUNCTION[k].w, dash: FUNCTION[k].dash,
      filter: ["==", ["get", "cat"], k] }));
  }
  if (theme === "aufgabe" && view === "heute") {
    const cls = [[20, "bis 20 km/h"], [30, "30 km/h"], [40, "40 km/h"], [50, "50 km/h"], [99, "über 50 km/h"]];
    const lower = { 20: 0, 30: 20, 40: 30, 50: 40, 99: 50 };
    const style = { 20: [2, [0.6, 1.4]], 30: [2.5, null], 40: [3, [3, 1.5]], 50: [4, null], 99: [5.5, null] }; // tokens.json speed.*.width/dash
    const out = cls.map(([k, label]) => seg({ label, color: T.speed[k], w: style[k][0], dash: style[k][1],
      filter: ["all", ["has", "spd"], [">", ["get", "spd"], lower[k]], ["<=", ["get", "spd"], k === 99 ? 999 : k]] }));
    out.push(seg({ label: "Tempo unbekannt", color: T.unknown, w: 1.5, dash: [1, 1.5], filter: ["!", ["has", "spd"]] }));
    return out;
  }
  if (theme === "abweichung" && view === "ziel") {
    return [
      seg({ label: "große Abweichung", ...NEED.strong, filter: [">=", ["coalesce", ["get", "dm"], 0], 2] }),
      seg({ label: "kleine Abweichung", ...NEED.partial, filter: ["all", [">=", ["coalesce", ["get", "dm"], 0], 1], ["<", ["get", "dm"], 2]] }),
      seg({ label: "passt zum Ziel", ...NEED.none, filter: ["<", ["coalesce", ["get", "dm"], 0], 1] }),
    ];
  }
  if (theme === "abweichung" && view === "prio") {
    return [
      seg({ label: "dringend", ...NEED.strong, filter: [">=", ["coalesce", ["get", "pr"], 0], 2] }),
      seg({ label: "mittel", ...NEED.partial, filter: ["all", [">=", ["coalesce", ["get", "pr"], 0], 1], ["<", ["get", "pr"], 2]] }),
      seg({ label: "gering oder keine", ...NEED.none, filter: ["<", ["coalesce", ["get", "pr"], 0], 1] }),
    ];
  }
  if (theme === "platz" && view === "ziel") {
    return [
      cyc({ label: "passt nicht", ...NEED.strong, filter: ["==", ["get", "fit"], "does_not_fit"] }),
      cyc({ label: "passt mit Abstrichen (z. B. weniger Parkplätze)", ...NEED.partial, filter: ["==", ["get", "fit"], "fits_after_degrade"] }),
      cyc({ label: "passt", ...NEED.none, filter: ["==", ["get", "fit"], "fits"] }),
      cyc({ label: "nicht prüfbar (Breite fehlt)", ...NEED.unknown, filter: ["!", ["in", ["get", "fit"], ["literal", ["fits", "fits_after_degrade", "does_not_fit"]]]] }),
    ];
  }
  if (theme === "platz" && view === "fahrstreifen") {
    return [
      cyc({ label: "weniger Fahrstreifen als heute", ...NEED.strong, filter: ["==", ["get", "ld"], "fewer"] }),
      cyc({ label: "mehr Fahrstreifen als heute", ...NEED.partial, filter: ["==", ["get", "ld"], "more"] }),
      cyc({ label: "wie heute", ...NEED.none, filter: ["in", ["get", "ld"], ["literal", ["same", "shared"]]] }),
      cyc({ label: "heute unbekannt", ...NEED.unknown, filter: ["==", ["get", "ld"], "ist_unknown"] }),
    ];
  }
  if (theme === "rad" && view === "ziel") {
    const lab = meta.cycling.cycle_categories;
    return [
      { label: lab.RSV, color: T.cyc, w: 6, dash: null, filter: ["==", ["get", "cc"], "RSV"], src: "cyc", sl: "cycle_network" },
      { label: lab.HAUPT, color: T.cyc, w: 4.5, dash: null, filter: ["==", ["get", "cc"], "HAUPT"], src: "cyc", sl: "cycle_network" },
      { label: lab.BASIS, color: T.cyc, w: 3, dash: [3, 1.5], filter: ["==", ["get", "cc"], "BASIS"], src: "cyc", sl: "cycle_network" },
      { label: "übrige Wege", color: T.none, w: 1.2, dash: null, filter: ["==", ["get", "cc"], "ERSCHL"], src: "cyc", sl: "cycle_network" },
    ];
  }
  if (theme === "rad" && view === "luecken") {
    return [
      { label: "Netz zu weitmaschig (Fläche)", kind: "fill", color: T.need, filter: null, src: "gaps" },
      cyc({ label: "Radweg fehlt", ...NEED.strong, filter: ["==", ["get", "gap"], "missing"] }),
      cyc({ label: "anderer oder zu schmaler Radweg", ...NEED.partial, filter: ["in", ["get", "gap"], ["literal", ["wrong_type", "too_narrow", "partial"]]] }),
      cyc({ label: "passt", ...NEED.none, filter: ["==", ["get", "gap"], "none"] }),
    ];
  }
  if (theme === "rad" && view === "amtlich") {
    return [
      { label: "Vorschlag (Radroute und Radschnellweg)", color: T.cyc, w: 3, dash: null, filter: ["in", ["get", "cc"], ["literal", ["RSV", "HAUPT"]]], src: "cyc", sl: "cycle_network", opacity: 0.45 },
      { label: "amtliches Radnetz Hamburg", color: T.ink, w: 2, dash: [2, 2], filter: null, src: "cyc", sl: "cycle_official", noBz: true },
    ];
  }
  if (theme === "knoten") {
    const grp = meta.cycling.junction_group;
    const shape = { roundabout: "circle", signal: "square", priority: "triangle", continuous: "diamond", equal: "ring", grade_separated: "bar", none: "cross" };
    return [
      ...Object.entries(shape).filter(([k]) => k !== "none").map(([k, s]) => ({ label: grp[k] ?? k, kind: "symbol", shape: s, color: T.ink, group: k, src: "jct", sl: "junctions" })),
      { label: "Orange: Umbau nötig", kind: "symbol", shape: "square", color: T.need, group: null, src: "jct", sl: "junctions", legendOnly: true },
    ];
  }
  return [];
}

function icons(map) {
  for (const [name, s] of Object.entries(SHAPES)) {
    for (const [suffix, color] of [["keep", T.ink], ["act", T.need]]) {
      const id = `j-${name}-${suffix}`;
      if (map.hasImage(id)) continue;
      const c = document.createElement("canvas");
      c.width = c.height = 40;
      const ctx = c.getContext("2d");
      ctx.scale(2.5, 2.5);
      const path = new Path2D(s.d);
      if (s.mode === "fill") { ctx.fillStyle = color; ctx.fill(path); ctx.strokeStyle = T.casing; ctx.lineWidth = 1.4; ctx.stroke(path); }
      else { ctx.strokeStyle = T.casing; ctx.lineWidth = 4.5; ctx.stroke(path); ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke(path); }
      map.addImage(id, ctx.getImageData(0, 0, 40, 40), { pixelRatio: 2 });
    }
  }
}

export function createMap(container, { meta, district, bz, onSelect, onSelectJunction, interactive = true }) {
  const [w, s, e, n] = district.bbox;
  const map = new maplibregl.Map({
    container, bounds: [[w, s], [e, n]], fitBoundsOptions: { padding: 24 }, minZoom: 10.5, maxZoom: 18, interactive,
    maxBounds: [[w - 0.1, s - 0.06], [e + 0.1, n + 0.06]], attributionControl: { compact: true },
    style: {
      version: 8,
      glyphs: url("basemap/fonts/{fontstack}/{range}.pbf").replace("%7Bfontstack%7D", "{fontstack}").replace("%7Brange%7D", "{range}"),
      sprite: url("basemap/sprites/light"),
      sources: {
        protomaps: { type: "vector", url: `pmtiles://${url("basemap/basemap.pmtiles")}`, attribution: "© OpenStreetMap-Mitwirkende (ODbL) · Protomaps" },
        sfp: { type: "vector", url: `pmtiles://${url("tiles/segments.pmtiles")}`, promoteId: "id", attribution: "Entwurf, nicht amtlich" },
        cyc: { type: "vector", url: `pmtiles://${url("tiles/cycling.pmtiles")}`, promoteId: "id" },
        jct: { type: "vector", url: `pmtiles://${url("tiles/junctions.pmtiles")}`, promoteId: "id" },
        gaps: { type: "geojson", data: url("redesign/data/mesh_gaps.geojson") },
        district: { type: "geojson", data: url("districts.geojson") },
      },
      layers: basemapLayers("protomaps", namedFlavor("grayscale"), { lang: "de" }),
    },
  });
  if (interactive) map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
  // the container grows when the web font has loaded and the header reflows; keep the drawing buffer in step
  new ResizeObserver(() => map.resize()).observe(container);
  // a resize in the same frame as the layout change can leave a stale drawing area (seen at 390 px width):
  // resize once more after the web font has loaded and after the first rendered frame
  document.fonts?.ready.then(() => requestAnimationFrame(() => map.resize()));
  map.once("idle", () => map.resize());
  const bzF = ["==", ["get", "bz"], bz];
  let current = [];
  let pending = null;
  let selected = null;

  function build(theme, view) {
    const gs = groups(theme, view, meta);
    const out = [];
    for (const g of gs.filter((x) => x.kind === "fill")) {
      out.push({ id: "gaps-fill", type: "fill", source: "gaps", paint: { "fill-color": g.color, "fill-opacity": 0.14 } });
      out.push({ id: "gaps-line", type: "line", source: "gaps", paint: { "line-color": g.color, "line-width": 1, "line-dasharray": [3, 2] } });
    }
    const lines = gs.filter((g) => !g.kind);
    for (const key of new Set(lines.map((g) => `${g.src}|${g.sl}`))) {
      const [src, sl] = key.split("|");
      const any = lines.find((g) => `${g.src}|${g.sl}` === key);
      out.push({ id: `casing-${sl}`, type: "line", source: src, "source-layer": sl, filter: any.noBz ? ["all"] : bzF,
        layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": T.casing, "line-width": zw(7) } });
    }
    // draw from the last group (thin, "no need") to the first (strong), so strong colours stay on top
    [...lines].reverse().forEach((g) => {
      const i = lines.indexOf(g);
      out.push({ id: `main-${i}`, type: "line", source: g.src, "source-layer": g.sl,
        filter: ["all", ...(g.filter ? [g.filter] : []), ...(g.noBz ? [] : [bzF])],
        layout: { "line-cap": g.dash ? "butt" : "round", "line-join": "round" },
        paint: { "line-color": g.color, "line-width": zw(g.w), "line-opacity": g.opacity ?? 1, ...(g.dash ? { "line-dasharray": g.dash } : {}) } });
    });
    const sym = gs.filter((g) => g.kind === "symbol" && !g.legendOnly);
    if (sym.length) {
      const shapeOf = ["match", ["get", "grp"], ...sym.flatMap((g) => [g.group, g.shape]), "cross"];
      out.push({ id: "main-jct", type: "symbol", source: "jct", "source-layer": "junctions", minzoom: 12, filter: bzF,
        layout: { "icon-image": ["concat", "j-", shapeOf, "-", ["case", ["==", ["get", "act"], 1], "act", "keep"]],
          "icon-allow-overlap": true, "icon-size": ["case", ["==", ["get", "act"], 1], 1, 0.7],
          "symbol-sort-key": ["get", "act"] } });
    } else {
      // junctions stay tappable in every theme from zoom 14 (small dots)
      out.push({ id: "main-jct-dot", type: "circle", source: "jct", "source-layer": "junctions", minzoom: 14, filter: bzF,
        paint: { "circle-radius": 3.5, "circle-color": T.ink, "circle-stroke-color": T.casing, "circle-stroke-width": 1.5 } });
    }
    out.push({ id: "district-line", type: "line", source: "district", filter: ["==", ["get", "name"], bz],
      paint: { "line-color": T.ink, "line-width": 1.5, "line-dasharray": [4, 2] } });
    if (selected) out.push({ id: "selected", type: "line", source: "sfp", "source-layer": "segments", filter: ["==", ["get", "id"], selected],
      paint: { "line-color": T.ink, "line-width": zw(12), "line-opacity": 0.25 } });
    return out;
  }

  function apply(theme, view) {
    for (const id of current) if (map.getLayer(id)) map.removeLayer(id);
    icons(map);
    const ls = build(theme, view);
    for (const l of ls) map.addLayer(l);
    current = ls.map((l) => l.id);
  }

  // the container may get its final size only after the stylesheet and the grid have settled: refit on load
  map.on("load", () => {
    map.resize();
    const legend = container.parentElement?.querySelector(".legend");
    const overlay = legend && getComputedStyle(legend).position === "absolute" ? legend.getBoundingClientRect().height : 0;
    map.fitBounds([[w, s], [e, n]], { padding: { top: 24, left: 24, right: 24, bottom: 24 + overlay }, animate: false });
    if (pending) apply(...pending);
  });
  map.on("click", (ev) => {
    const ids = current.filter((id) => id.startsWith("main-") || id.startsWith("casing-"));
    const hits = map.queryRenderedFeatures([[ev.point.x - 8, ev.point.y - 8], [ev.point.x + 8, ev.point.y + 8]], { layers: ids });
    const hit = hits.find((h) => h.sourceLayer === "junctions") ?? hits[0];
    if (!hit) return;
    if (hit.sourceLayer === "junctions") onSelectJunction?.(String(hit.properties.id));
    else if (hit.sourceLayer === "cycle_network") { if (hit.properties.seg) onSelect?.(hit.properties.seg); }
    else if (hit.sourceLayer !== "cycle_official") onSelect?.(String(hit.properties.id));
  });
  map.on("mousemove", (ev) => {
    const ids = current.filter((id) => id.startsWith("main-") || id.startsWith("casing-"));
    map.getCanvas().style.cursor = map.queryRenderedFeatures(ev.point, { layers: ids }).length ? "pointer" : "";
  });
  return {
    map,
    show(theme, view) { pending = [theme, view]; if (map.isStyleLoaded()) apply(theme, view); },
    select(id) { selected = id; if (pending && map.isStyleLoaded()) apply(...pending); },
    flyTo([lon, lat], zoom = 16) { map.flyTo({ center: [lon, lat], zoom, duration: matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 800 }); },
  };
}

/** Legend in words next to the map. */
export function legendHtml(theme, view, meta) {
  const items = groups(theme, view, meta).map((g) => {
    if (g.kind === "symbol") {
      const s = SHAPES[g.shape];
      const paint = s.mode === "fill" ? `fill="${g.color}" stroke="#fff"` : `fill="none" stroke="${g.color}" stroke-width="2.5"`;
      return `<li><svg aria-hidden="true" width="36" height="18" viewBox="-10 0 36 16"><path d="${s.d}" ${paint}/></svg><span>${g.label}</span></li>`;
    }
    if (g.kind === "fill") return `<li><svg aria-hidden="true" width="36" height="14"><rect x="2" y="1" width="32" height="12" fill="${g.color}" fill-opacity=".2" stroke="${g.color}" stroke-dasharray="4 2"/></svg><span>${g.label}</span></li>`;
    const dash = g.dash ? `stroke-dasharray="${g.dash.map((d) => d * 4).join(" ")}"` : "";
    const w = Math.max(1.5, Math.min(g.w, 7));
    return `<li><svg aria-hidden="true" width="36" height="14"><line x1="2" y1="7" x2="34" y2="7" stroke="#fff" stroke-width="${w + 3}" stroke-linecap="round"/><line x1="2" y1="7" x2="34" y2="7" stroke="${g.color}" stroke-width="${w}" ${dash} opacity="${g.opacity ?? 1}"/></svg><span>${g.label}</span></li>`;
  });
  return `<h2>Was die Farben bedeuten</h2><p class="intro">${THEMES[theme].intro[view]}</p><ul>${items.join("")}</ul>`;
}
