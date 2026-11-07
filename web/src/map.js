// MapLibre map with the self-hosted Protomaps basemap and the SFP vector tiles (pmtiles protocol, no tile server).
import { layers as basemapLayers, namedFlavor } from "@protomaps/basemaps";
import * as maplibregl from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { sfpLayers } from "./layers.js";
import { CASING, JUNCTION_STYLE, RURAL_FILL, SHAPES } from "./palette.js";
import { dataUrl } from "./util.js";

maplibregl.setWorkerUrl(workerUrl);
const protocol = new Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

const INTERACTIVE_PREFIX = "main-";
const ICON_PX = 40; // icon bitmap size (pixelRatio 2 -> 20 px on the map)

/** Junction symbols as map images, drawn from the same shapes as the legend (palette.js SHAPES). */
function addJunctionIcons(map) {
  for (const [grp, st] of Object.entries(JUNCTION_STYLE)) {
    const id = `jct-${grp}`;
    if (map.hasImage(id)) continue;
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = ICON_PX;
    const ctx = canvas.getContext("2d");
    ctx.scale(ICON_PX / 16, ICON_PX / 16);
    const path = new Path2D(SHAPES[st.shape].d);
    if (SHAPES[st.shape].mode === "fill") {
      ctx.fillStyle = st.color; ctx.fill(path);
      ctx.strokeStyle = CASING; ctx.lineWidth = 1.2; ctx.stroke(path);
    } else {
      ctx.strokeStyle = CASING; ctx.lineWidth = 4.5; ctx.stroke(path);
      ctx.strokeStyle = st.color; ctx.lineWidth = 2.5; ctx.stroke(path);
    }
    map.addImage(id, ctx.getImageData(0, 0, ICON_PX, ICON_PX), { pixelRatio: 2 });
  }
}

/** Cycling tile sources, added the first time a cycling layer is shown (lazy loading per theme). */
function ensureSources(map, meta, layers, tilesBase) {
  const urls = { cyc: meta.cycling?.tiles?.cycling, jct: meta.cycling?.tiles?.junctions };
  for (const l of layers) {
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
    layers: basemapLayers("protomaps", flavor, { lang: "de" }),
  };
}

export function createMap(container, meta, state, { onSelect, onSelectJunction, onMove }) {
  const tilesBase = meta.tiles_base_url || import.meta.env.VITE_TILES_BASE_URL || null;
  const [w, s, e, n] = meta.bbox;
  const map = new maplibregl.Map({
    container, style: style(meta, tilesBase),
    bounds: state.map ? undefined : [[w, s], [e, n]],
    center: state.map ? [state.map.lon, state.map.lat] : undefined,
    zoom: state.map ? state.map.zoom : undefined,
    minZoom: 10, maxZoom: 18, maxBounds: [[w - 0.15, s - 0.08], [e + 0.15, n + 0.08]],
    attributionControl: { compact: false }, cooperativeGestures: false,
  });
  map.addControl(new maplibregl.NavigationControl({ visualizePitch: false, showCompass: false }), "top-right");
  map.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");
  map.getCanvas().setAttribute("aria-label",
    "Karte der Soll-Kategorien. Mit Pfeiltasten verschieben, Plus und Minus zoomen. Alle Inhalte auch in der Tabellenansicht.");

  let current = [];
  function apply(st) {
    for (const id of current) if (map.getLayer(id)) map.removeLayer(id);
    const ls = sfpLayers(st, meta);
    ensureSources(map, meta, ls, tilesBase);
    for (const l of ls) map.addLayer(l);
    current = ls.map((l) => l.id);
  }

  map.on("load", () => {
    map.addSource("district", { type: "geojson", data: dataUrl("districts.geojson") });
    map.addLayer({ id: "district-line", type: "line", source: "district",
      paint: { "line-color": "#333333", "line-width": 1.5, "line-dasharray": [4, 2] } });
    // Rural Stadtteile: not classified (config/project.yaml, rural_exclude)
    map.addSource("rural", { type: "geojson", data: dataUrl("rural_excluded.geojson") });
    map.addLayer({ id: "rural-fill", type: "fill", source: "rural", paint: { "fill-color": RURAL_FILL, "fill-opacity": 0.18 } });
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
    const ids = current.filter((id) => id.startsWith("casing") || (id.startsWith(INTERACTIVE_PREFIX) && id.includes("grp-")));
    map.getCanvas().style.cursor = map.queryRenderedFeatures(ev.point, { layers: ids }).length ? "pointer" : "";
  });
  map.on("moveend", () => {
    const c = map.getCenter();
    onMove({ zoom: map.getZoom(), lat: c.lat, lon: c.lng });
  });

  return {
    map,
    update(st) { if (map.isStyleLoaded()) apply(st); else map.once("load", () => apply(st)); },
    fitBbox(b) { map.fitBounds([[b[0], b[1]], [b[2], b[3]]], { padding: 60, maxZoom: 17 }); },
    resize() { map.resize(); },
  };
}
