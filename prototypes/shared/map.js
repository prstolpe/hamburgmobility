// Map for the prototypes: Protomaps basemap + SFP tiles, limited to one Bezirk. Reuses the colours and legend
// groups of the website (web/src/palette.js, web/src/layers.js), read-only. Adds the views the prototypes need:
// Soll-Tempo, scenario, data quality, Radanlage heute, network gaps.
import { layers as basemapLayers, namedFlavor } from "@protomaps/basemaps";
import * as maplibregl from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { groups as siteGroups } from "../../web/src/layers.js";
import { CASING, CATEGORY_STYLE, FACILITY_STYLE, JUNCTION_STYLE, SHAPES, SPEED_CLASSES, UNKNOWN } from "../../web/src/palette.js";

maplibregl.setWorkerUrl(workerUrl);
maplibregl.addProtocol("pmtiles", new Protocol().tile);

const url = (p) => new URL(p, `${location.origin}/`).href; // data/out and prototypes/ are both served from the root
export const dataUrl = url;

export const SOLL_SPEED = { SW: "über 50 km/h", GOW50: "50 km/h", GOW30: "30 km/h", ETW30: "30 km/h", ETW_ERF: "Schrittgeschwindigkeit bis 20 km/h" };
const speedColor = (max) => SPEED_CLASSES.find((c) => c.max === max).color;
const zoomWidth = (w) => ["interpolate", ["linear"], ["zoom"], 10, w * 0.4, 14, w, 17, w * 2];

/** Legend groups of a view: [{key,label,filter,color,width,dash,src,srcLayer,kind?,fill?}] */
export function viewGroups(view, meta, extra = {}) {
  const seg = (g) => ({ src: "sfp", srcLayer: "segments", ...g });
  const cats = (meta.categories_present ?? Object.keys(CATEGORY_STYLE)).filter((k) => CATEGORY_STYLE[k]);
  switch (view) {
    case "cat":
      // plain language: name and speed instead of codes
      return cats.map((k) => seg({ key: k, label: `${meta.categories[k].label} (${SOLL_SPEED[k]})`, filter: ["==", ["get", "cat"], k], ...CATEGORY_STYLE[k] }));
    case "scenario": {
      const ids = {};
      for (const [id, c] of Object.entries(extra.scenario?.segments ?? {})) (ids[c] ??= []).push(id);
      const expr = ["match", ["get", "id"], ...Object.entries(ids).flatMap(([c, l]) => [l, c]), ["get", "cat"]];
      if (!Object.keys(ids).length) expr.splice(0, expr.length, "get", "cat");
      return cats.map((k) => seg({ key: `sc-${k}`, label: `${meta.categories[k].label} (${SOLL_SPEED[k]})`, filter: ["==", expr, k], ...CATEGORY_STYLE[k] }));
    }
    case "soll_speed":
      return [
        seg({ key: "ss20", label: "bis 20 km/h (Aufenthaltsstraße)", color: speedColor(20), width: 3, dash: null, filter: ["==", ["get", "cat"], "ETW_ERF"] }),
        seg({ key: "ss30", label: "30 km/h", color: speedColor(30), width: 3, dash: null, filter: ["in", ["get", "cat"], ["literal", ["GOW30", "ETW30"]]] }),
        seg({ key: "ss50", label: "50 km/h", color: speedColor(50), width: 3, dash: null, filter: ["==", ["get", "cat"], "GOW50"] }),
        seg({ key: "ssx", label: "über 50 km/h (Schnellverkehrsstraße)", color: speedColor(Infinity), width: 3, dash: null, filter: ["==", ["get", "cat"], "SW"] }),
      ];
    case "speed":
      return siteGroups("speed", meta).map(seg);
    case "disc":
      return siteGroups("disc", meta).map((g) => seg({ ...g, label: g.label.replace(/^D\d – /, "") }));
    case "need":
      // Handlungsbedarf: priority classes (priority = strongest discrepancy x risk, 0–3)
      return [
        seg({ key: "p3", label: "dringend (Priorität ab 2)", color: "#CC3311", width: 5, dash: null, filter: [">=", ["coalesce", ["get", "pr"], 0], 2] }),
        seg({ key: "p2", label: "mittel (1 bis unter 2)", color: "#EE7733", width: 3.5, dash: null, filter: ["all", [">=", ["coalesce", ["get", "pr"], 0], 1], ["<", ["get", "pr"], 2]] }),
        seg({ key: "p1", label: "gering (unter 1)", color: "#BBBBBB", width: 2, dash: null, filter: ["all", [">", ["coalesce", ["get", "pr"], 0], 0], ["<", ["get", "pr"], 1]] }),
        seg({ key: "p0", label: "kein Handlungsbedarf erkannt", color: "#DDDDDD", width: 1, dash: null, filter: ["!", [">", ["coalesce", ["get", "pr"], 0], 0]] }),
      ];
    case "conf":
      return [
        seg({ key: "un", label: "unsicher: Ergebnis kippt bei anderen Annahmen", color: "#EE7733", width: 6, dash: null, filter: ["==", ["get", "un"], true] }),
        seg({ key: "c-niedrig", label: "Datenlage lückenhaft", color: "#CC3311", width: 3, dash: [0.6, 1.4], filter: ["all", ["!=", ["get", "un"], true], ["==", ["get", "conf"], "niedrig"]] }),
        seg({ key: "c-mittel", label: "Datenlage mittel (Ersatzwerte)", color: "#BBBBBB", width: 1.5, dash: null, filter: ["all", ["!=", ["get", "un"], true], ["==", ["get", "conf"], "mittel"]] }),
        seg({ key: "c-hoch", label: "Datenlage gut", color: "#0077BB", width: 2.5, dash: null, filter: ["all", ["!=", ["get", "un"], true], ["==", ["get", "conf"], "hoch"]] }),
      ];
    case "cnet":
      return siteGroups("cnet", meta).map((g) => ({ ...g, label: g.label.replace(/^[A-Z]+ – /, "") }));
    case "cgap":
      return siteGroups("cgap", meta);
    case "fac_soll":
    case "fac_ist": {
      const attr = view === "fac_soll" ? "fs" : "fi";
      const labels = meta.cycling.facility;
      return Object.entries(FACILITY_STYLE).map(([k, s]) => ({ key: `${attr}-${k}`, label: labels[k] ?? k, src: "cyc", srcLayer: "cycle_segments",
        filter: ["==", ["get", attr], k], ...s }));
    }
    case "jct":
      return siteGroups("jct", meta);
    default:
      return [];
  }
}

function junctionIcons(map) {
  for (const [grp, st] of Object.entries(JUNCTION_STYLE)) {
    const id = `jct-${grp}`;
    if (map.hasImage(id)) continue;
    const c = document.createElement("canvas");
    c.width = c.height = 40;
    const ctx = c.getContext("2d");
    ctx.scale(2.5, 2.5);
    const path = new Path2D(SHAPES[st.shape].d);
    if (SHAPES[st.shape].mode === "fill") { ctx.fillStyle = st.color; ctx.fill(path); ctx.strokeStyle = CASING; ctx.lineWidth = 1.2; ctx.stroke(path); }
    else { ctx.strokeStyle = CASING; ctx.lineWidth = 4.5; ctx.stroke(path); ctx.strokeStyle = st.color; ctx.lineWidth = 2.5; ctx.stroke(path); }
    map.addImage(id, ctx.getImageData(0, 0, 40, 40), { pixelRatio: 2 });
  }
}

/**
 * createMap(container, {meta, kpi, bz, scenario, onSelect, onSelectJunction, interactive})
 * returns {map, show(view, opts), fit(bbox), flyTo(lon, lat, zoom)}
 */
export function createMap(container, { meta, kpi, bz, scenario, onSelect, onSelectJunction, interactive = true }) {
  const [w, s, e, n] = kpi.bbox;
  const map = new maplibregl.Map({
    container, bounds: [[w, s], [e, n]], fitBoundsOptions: { padding: 20 }, minZoom: 11, maxZoom: 18,
    maxBounds: [[w - 0.08, s - 0.05], [e + 0.08, n + 0.05]], attributionControl: { compact: true }, interactive,
    style: {
      version: 8,
      glyphs: url("basemap/fonts/{fontstack}/{range}.pbf").replace("%7Bfontstack%7D", "{fontstack}").replace("%7Brange%7D", "{range}"),
      sprite: url("basemap/sprites/light"),
      sources: {
        protomaps: { type: "vector", url: `pmtiles://${url("basemap/basemap.pmtiles")}`, attribution: "© OpenStreetMap-Beitragende · Protomaps" },
        sfp: { type: "vector", url: `pmtiles://${url("tiles/segments.pmtiles")}`, promoteId: "id", attribution: "Straßenfunktionsplan – Entwurf, nicht amtlich" },
        cyc: { type: "vector", url: `pmtiles://${url("tiles/cycling.pmtiles")}`, promoteId: "id" },
        jct: { type: "vector", url: `pmtiles://${url("tiles/junctions.pmtiles")}`, promoteId: "id" },
        gaps: { type: "geojson", data: url("shared/mesh_gaps_eimsbuettel.geojson") },
        district: { type: "geojson", data: url("districts.geojson") },
      },
      layers: basemapLayers("protomaps", namedFlavor("grayscale"), { lang: "de" }),
    },
  });
  if (interactive) map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
  const bzFilter = ["==", ["get", "bz"], bz];
  let current = [];
  let pending = null;

  function build(view, { gaps = false, selected = null } = {}) {
    const gs = viewGroups(view, meta, { scenario });
    const out = [];
    if (gaps) {
      out.push({ id: "gaps-fill", type: "fill", source: "gaps", paint: { "fill-color": "#EE7733", "fill-opacity": 0.18 } });
      out.push({ id: "gaps-line", type: "line", source: "gaps", paint: { "line-color": "#B35900", "line-width": 1.5, "line-dasharray": [2, 1] } });
    }
    const lines = gs.filter((g) => g.kind !== "symbol");
    for (const key of new Set(lines.map((g) => `${g.src}|${g.srcLayer}`))) {
      const [src, sl] = key.split("|");
      out.push({ id: `casing-${sl}`, type: "line", source: src, "source-layer": sl, filter: bzFilter,
        layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": CASING, "line-width": zoomWidth(7) } });
    }
    // draw thin "unimportant" groups first, so strong colours stay on top
    for (const g of [...lines].reverse()) {
      out.push({ id: `main-${g.key}`, type: "line", source: g.src, "source-layer": g.srcLayer, filter: ["all", g.filter, bzFilter],
        layout: { "line-cap": g.dash ? "butt" : "round", "line-join": "round" },
        paint: { "line-color": g.color, "line-width": typeof g.width === "number" ? zoomWidth(g.width) : g.width, ...(g.dash ? { "line-dasharray": g.dash } : {}) } });
    }
    for (const g of gs.filter((x) => x.kind === "symbol")) {
      out.push({ id: `main-${g.key}`, type: "symbol", source: "jct", "source-layer": "junctions", minzoom: 12, filter: ["all", g.filter, bzFilter],
        layout: { "icon-image": g.icon, "icon-allow-overlap": true, "icon-size": ["case", ["==", ["get", "act"], 1], 1, 0.7] } });
    }
    out.push({ id: "district-line", type: "line", source: "district", filter: ["==", ["get", "name"], bz],
      paint: { "line-color": "#333333", "line-width": 1.5, "line-dasharray": [4, 2] } });
    if (selected) out.push({ id: "selected", type: "line", source: "sfp", "source-layer": "segments", filter: ["==", ["get", "id"], selected],
      paint: { "line-color": "#000000", "line-width": zoomWidth(11), "line-opacity": 0.3 } });
    return out;
  }

  function apply(view, opts) {
    for (const id of current) if (map.getLayer(id)) map.removeLayer(id);
    junctionIcons(map);
    const ls = build(view, opts);
    for (const l of ls) map.addLayer(l);
    current = ls.map((l) => l.id);
  }

  map.on("load", () => { if (pending) apply(...pending); });
  map.on("click", (ev) => {
    const ids = current.filter((id) => id.startsWith("main-") || id.startsWith("casing-"));
    const hit = map.queryRenderedFeatures([[ev.point.x - 7, ev.point.y - 7], [ev.point.x + 7, ev.point.y + 7]], { layers: ids })[0];
    if (!hit) return;
    if (hit.sourceLayer === "junctions") onSelectJunction?.(String(hit.properties.id));
    else if (hit.sourceLayer === "cycle_network") { if (hit.properties.seg) onSelect?.(hit.properties.seg); }
    else onSelect?.(hit.properties.id);
  });
  map.on("mousemove", (ev) => {
    const ids = current.filter((id) => id.startsWith("casing-") || id.startsWith("main-grp"));
    map.getCanvas().style.cursor = map.queryRenderedFeatures(ev.point, { layers: ids }).length ? "pointer" : "";
  });

  return {
    map,
    show(view, opts = {}) { pending = [view, opts]; if (map.isStyleLoaded()) apply(view, opts); },
    fit(b) { map.fitBounds([[b[0], b[1]], [b[2], b[3]]], { padding: 60, maxZoom: 17 }); },
    flyTo(lon, lat, zoom = 16) { map.flyTo({ center: [lon, lat], zoom }); },
  };
}

/** Legend as HTML: line sample + plain text (no codes). */
export function legendHtml(view, meta, { gaps = false } = {}) {
  const items = viewGroups(view, meta).map((g) => {
    if (g.kind === "symbol") {
      const s = SHAPES[g.shape];
      const paint = s.mode === "fill" ? `fill="${g.color}" stroke="#fff"` : `fill="none" stroke="${g.color}" stroke-width="2.5"`;
      return `<li><svg aria-hidden="true" width="18" height="18" viewBox="0 0 16 16"><path d="${s.d}" ${paint}/></svg><span>${g.label}</span></li>`;
    }
    const dash = g.dash ? `stroke-dasharray="${g.dash.map((d) => d * 4).join(" ")}"` : "";
    const w = typeof g.width === "number" ? Math.max(2, Math.min(g.width, 6)) : 4;
    return `<li><svg aria-hidden="true" width="36" height="14"><line x1="2" y1="7" x2="34" y2="7" stroke="#fff" stroke-width="${w + 4}" stroke-linecap="round"/><line x1="2" y1="7" x2="34" y2="7" stroke="${g.color}" stroke-width="${w}" ${dash}/></svg><span>${g.label}</span></li>`;
  });
  if (gaps) items.unshift(`<li><svg aria-hidden="true" width="36" height="14"><rect x="2" y="1" width="32" height="12" fill="#EE7733" fill-opacity=".25" stroke="#B35900" stroke-dasharray="4 2"/></svg><span>Netzlücke: Masche größer als vorgesehen</span></li>`);
  return `<ul class="legend">${items.join("")}</ul>`;
}

export { UNKNOWN };
