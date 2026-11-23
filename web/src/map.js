// MapLibre map with the self-hosted Protomaps basemap and the SFP vector tiles (pmtiles protocol, no tile server).
import { layers as basemapLayers, namedFlavor } from "@protomaps/basemaps";
import * as maplibregl from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { beforeIdFor, firstSymbolId, LAYER_INFO, sfpLayers, tuneLabels } from "./layers.js";
import { CASING, JUNCTION_REBUILD, JUNCTION_STYLE, RURAL_FILL, SHAPES } from "./palette.js";
import { dataUrl } from "./util.js";

maplibregl.setWorkerUrl(workerUrl);
const protocol = new Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

const INTERACTIVE_PREFIX = "main-";
const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
const ICON_PX = 40; // icon bitmap size (pixelRatio 2 -> 20 px on the map)
// German labels of the MapLibre controls (walkthrough: they were English)
const LOCALE = {
  "NavigationControl.ZoomIn": "Hineinzoomen", "NavigationControl.ZoomOut": "Herauszoomen",
  "NavigationControl.ResetBearing": "Karte nach Norden drehen und Neigung zurücksetzen",
  "ScaleControl.Meters": "m", "ScaleControl.Kilometers": "km",
  "AttributionControl.ToggleAttribution": "Quellen ein- und ausblenden", "Map.Title": "Karte",
};
const canvasLabel = (layer) => `Karte: ${LAYER_INFO[layer]?.title ?? "Straßenfunktionsplan"}. Mit Pfeiltasten verschieben, Plus und Minus zoomen. `
  + "Die Straßen im Kartenausschnitt gibt es als Liste im Bereich „Karte einstellen“.";

/** Junction symbols as map images, drawn from the same shapes as the legend (palette.js SHAPES). */
function addJunctionIcons(map) {
  for (const [grp, st] of Object.entries(JUNCTION_STYLE)) for (const [id, color] of [[`jct-${grp}`, st.color], [`jct-${grp}-act`, JUNCTION_REBUILD]]) {
    if (map.hasImage(id)) continue;
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = ICON_PX;
    const ctx = canvas.getContext("2d");
    ctx.scale(ICON_PX / 16, ICON_PX / 16);
    const path = new Path2D(SHAPES[st.shape].d);
    if (SHAPES[st.shape].mode === "fill") {
      ctx.fillStyle = color; ctx.fill(path);
      ctx.strokeStyle = CASING; ctx.lineWidth = 1.2; ctx.stroke(path);
    } else {
      ctx.strokeStyle = CASING; ctx.lineWidth = 4.5; ctx.stroke(path);
      ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke(path);
    }
    map.addImage(id, ctx.getImageData(0, 0, ICON_PX, ICON_PX), { pixelRatio: 2 });
  }
}

/** Cycling tile sources, added the first time a cycling layer is shown (lazy loading per theme). */
function ensureSources(map, meta, layers, tilesBase) {
  const urls = { cyc: meta.cycling?.tiles?.cycling, jct: meta.cycling?.tiles?.junctions };
  for (const l of layers) {
    // special places (prompts/26): small GeoJSON, loaded the first time a place is switched on
    if (l.source === "places" && !map.getSource("places")) {
      map.addSource("places", { type: "geojson", data: dataUrl(meta.special_places.file),
        attribution: "Besondere Orte: Vorschläge Dritter" });
    }
    if (l.source === "gaps" && !map.getSource("gaps")) map.addSource("gaps", { type: "geojson", data: dataUrl("cycle_mesh_gaps.geojson") });
    if (map.getSource(l.source) || !urls[l.source]) continue;
    map.addSource(l.source, { type: "vector", url: `pmtiles://${dataUrl(urls[l.source], tilesBase)}`, promoteId: "id",
      attribution: l.source === "cyc"
        ? "Radnetz-Entwurf (nicht amtlich) · Radnetz Hamburg © FHH/BVM, dl-de/by-2.0"
        : "Knotenpunkte-Entwurf (nicht amtlich)" });
    if (l.source === "jct") addJunctionIcons(map);
  }
}

function style(meta, tilesBase) {
  const flavor = namedFlavor("grayscale");
  return {
    version: 8,
    glyphs: dataUrl("basemap/fonts/{fontstack}/{range}.pbf").replace("%7Bfontstack%7D", "{fontstack}").replace("%7Brange%7D", "{range}"),
    sprite: dataUrl("basemap/sprites/light"),
    sources: {
      protomaps: { type: "vector", url: `pmtiles://${dataUrl("basemap/basemap.pmtiles", tilesBase)}`,
        attribution: "© <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap-Beitragende</a> · Protomaps" },
      sfp: { type: "vector", url: `pmtiles://${dataUrl("tiles/segments.pmtiles", tilesBase)}`, promoteId: "id",
        attribution: "Straßenfunktionsplan (Entwurf, nicht amtlich) · Datenstand " + meta.data_date },
    },
    layers: tuneLabels(basemapLayers("protomaps", flavor, { lang: "de" })),
  };
}

/**
 * @param opts.static true for the image renderer (tools/render_card): no interaction, no controls, no fading, drawing
 *   buffer kept so a screenshot is complete; the card prints the sources itself.
 */
export function createMap(container, meta, state, { onSelect, onSelectJunction, onMove }, opts = {}) {
  const tilesBase = meta.tiles_base_url || import.meta.env.VITE_TILES_BASE_URL || null;
  const [w, s, e, n] = meta.bbox;
  const map = new maplibregl.Map({
    container, style: style(meta, tilesBase),
    bounds: state.map ? undefined : [[w, s], [e, n]],
    center: state.map ? [state.map.lon, state.map.lat] : undefined,
    zoom: state.map ? state.map.zoom : undefined,
    pitch: state.map?.pitch ?? 0, bearing: state.map?.bearing ?? 0,
    minZoom: 10, maxZoom: 18, maxPitch: 60, maxBounds: [[w - 0.15, s - 0.08], [e + 0.15, n + 0.08]],
    attributionControl: opts.static ? false : { compact: matchMedia("(max-width: 760px)").matches }, cooperativeGestures: false, locale: LOCALE,
    ...(opts.static ? { interactive: false, fadeDuration: 0, canvasContextAttributes: { preserveDrawingBuffer: true, antialias: true } } : {}),
  });
  // the compass appears only when the map is turned or tilted (pitch and bearing are in the URL, prompt 28)
  if (!opts.static) map.addControl(new maplibregl.NavigationControl({ visualizePitch: true, showCompass: true }), "top-right");
  map.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");
  const compass = () => map.getContainer().querySelector(".maplibregl-ctrl-compass");
  const showCompass = () => { const c = compass(); if (c) c.hidden = Math.abs(map.getBearing()) < 0.5 && map.getPitch() < 0.5; };
  map.on("load", showCompass);
  // phones: compact source credit starts closed (MapLibre opens it until the first interaction; it covered the map)
  map.on("load", () => map.getContainer().querySelector(".maplibregl-ctrl-attrib.maplibregl-compact-show")?.classList.remove("maplibregl-compact-show"));
  map.on("rotate", showCompass);
  map.on("pitch", showCompass);

  let current = [];
  let bottomPad = 0; // px of map covered from below (profile sheet on phones)
  let labelId;
  function apply(st) {
    map.getCanvas().setAttribute("aria-label", canvasLabel(st.layer));
    for (const id of current) if (map.getLayer(id)) map.removeLayer(id);
    const ls = sfpLayers(st, meta);
    ensureSources(map, meta, ls, tilesBase);
    for (const l of ls) map.addLayer(l, beforeIdFor(l, labelId));
    current = ls.map((l) => l.id);
  }

  map.on("load", () => {
    labelId = firstSymbolId(map.getStyle().layers);
    // Rural Stadtteile: not classified (config/project.yaml, rural_exclude); under the district line
    map.addSource("rural", { type: "geojson", data: dataUrl("rural_excluded.geojson") });
    map.addLayer({ id: "rural-fill", type: "fill", source: "rural", paint: { "fill-color": RURAL_FILL, "fill-opacity": 0.18 } }, labelId);
    map.addSource("district", { type: "geojson", data: dataUrl("districts.geojson") });
    map.addLayer({ id: "district-line", type: "line", source: "district",
      paint: { "line-color": "#333333", "line-width": 1.5, "line-dasharray": [4, 2] } }, labelId);
    apply(state);
  });
  map.on("click", (ev) => {
    const ids = current.filter((id) => id.startsWith(INTERACTIVE_PREFIX) || id.startsWith("casing"));
    const hit = map.queryRenderedFeatures([[ev.point.x - 6, ev.point.y - 6], [ev.point.x + 6, ev.point.y + 6]], { layers: ids })[0];
    if (!hit) return;
    const layer = hit.sourceLayer;
    if (layer === "junctions") onSelectJunction(hit.properties.id);
    else if (layer === "cycle_network") { if (hit.properties.seg) onSelect(hit.properties.seg); }
    else if (layer !== "cycle_official") onSelect(hit.properties.id);
  });
  map.on("mousemove", (ev) => {
    const ids = current.filter((id) => id.startsWith("casing") || (id.startsWith(INTERACTIVE_PREFIX) && (id.includes("grp-") || id.startsWith("main-place-"))));
    map.getCanvas().style.cursor = map.queryRenderedFeatures(ev.point, { layers: ids }).length ? "pointer" : "";
  });
  map.on("moveend", () => {
    const c = map.getCenter();
    onMove({ zoom: map.getZoom(), lat: c.lat, lon: c.lng, pitch: map.getPitch(), bearing: map.getBearing() });
  });

  return {
    map,
    update(st) { if (map.isStyleLoaded()) apply(st); else map.once("load", () => apply(st)); },
    fitBbox(b, padding = 60) {
      map.fitBounds([[b[0], b[1]], [b[2], b[3]]], { padding: { top: padding, left: padding, right: padding, bottom: padding + bottomPad },
        maxZoom: 17, ...(reducedMotion() || opts.static ? { duration: 0 } : {}) });
    },
    flyTo([lon, lat], zoom = 16) {
      map.flyTo({ center: [lon, lat], zoom, padding: { top: 0, left: 0, right: 0, bottom: bottomPad }, duration: reducedMotion() || opts.static ? 0 : 800 });
    },
    resize() { map.resize(); },
    /** Keep the map centre above a sheet that covers the lower part of the map (phones, open profile). Waits for a
     * running camera move (search: fitBbox/flyTo) instead of cancelling it; later moves include the padding. */
    setBottomPadding(px) {
      bottomPad = px;
      const go = () => map.easeTo({ padding: { top: 0, right: 0, left: 0, bottom: px }, duration: reducedMotion() ? 0 : 300 });
      if (map.isMoving()) map.once("moveend", go); else go();
    },
  };
}
