// Image card (prompt 28, docs/map_interaction/05_renderer.md): one segment, junction or special place as a static
// picture – map extract with our own style and data, cross-section or junction sketch, title, one plain sentence,
// source and status date, deep link. Rendered by tools/render_card (Playwright); this page only lays it out and
// reports `window.cardReady = { alt, title }` when the map is idle and the fonts are loaded.
// Hash: URL scheme v2 (#karte?v=2&seg=…|node=…|place=…) plus `format` = og | portrait | a4.
import "./card.css";
import { altText, cardHtml, FORMATS, junctionCard, placeCard, segmentCard } from "./card_content.js";
import { placeOf } from "./layers.js";
import { parseHash } from "./state.js";
import { esc } from "./util.js";

const json = async (url) => { const r = await fetch(url); if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`); return r.json(); };

/** Bounding box of a segment from the rendered vector tiles, or null. */
function segmentBbox(map, id) {
  const fs = map.querySourceFeatures("sfp", { sourceLayer: "segments", filter: ["==", ["get", "id"], id] });
  const pts = fs.flatMap((f) => (f.geometry.type === "LineString" ? f.geometry.coordinates : f.geometry.coordinates.flat()));
  if (!pts.length) return null;
  const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
}

/** Grow a bbox to at least `d` degrees latitude (and the same distance in longitude) around its centre. */
function minExtent([w, s, e, n], d) {
  const cx = (w + e) / 2, cy = (s + n) / 2;
  const dx = Math.max(e - w, d / Math.cos((cy * Math.PI) / 180)) / 2, dy = Math.max(n - s, d) / 2;
  return [cx - dx, cy - dy, cx + dx, cy + dy];
}

async function main() {
  const q = new URLSearchParams((location.hash.split("?")[1] ?? ""));
  const format = FORMATS[q.get("format")] ? q.get("format") : "og";
  const f = FORMATS[format];
  const root = document.getElementById("card");
  root.className = `card ${format}`;
  root.style.width = `${f.width}px`;
  root.style.height = `${f.height}px`;
  const state = { ...parseHash(location.hash), page: "karte", map: null };
  const meta = await json("meta.json");
  let c, fit;
  if (state.jct) {
    const j = await json(`junctions/${state.jct}.json`);
    c = junctionCard(j, meta);
    const hit = (await json("search_junctions.json")).find((x) => String(x.id) === state.jct);
    if (hit) fit = { center: [hit.lon, hit.lat], zoom: 17 };
  } else if (state.seg) {
    const p = await json(`segments/${state.seg}.json`);
    c = segmentCard(p, meta);
    const street = (await json("search.json")).find((s) => s.ids.includes(state.seg));
    if (street) fit = { bbox: street.bbox };
  } else if (state.place) {
    const p = placeOf(state, meta);
    if (!p) throw new Error(`unbekannter Ort ${state.place}`);
    c = placeCard(p);
    fit = { bbox: p.bbox };
  } else throw new Error("seg, node oder place fehlt");
  root.innerHTML = cardHtml(c, meta, format);
  document.title = `${c.title} – Karte als Bild`;
  const { createMap } = await import("./map.js");
  const view = createMap(document.getElementById("card-map"), meta, state, { onSelect() {}, onSelectJunction() {}, onMove() {} }, { static: true });
  await new Promise((resolve) => view.map.once("load", resolve));
  if (fit?.bbox) view.fitBbox(fit.bbox, 40);
  else if (fit?.center) view.flyTo(fit.center, fit.zoom);
  view.update(state);
  await new Promise((resolve) => view.map.once("idle", resolve));
  if (state.seg) {
    // fit to the piece itself (at least ~350 m across), so the highlighted segment is visible
    const b = segmentBbox(view.map, state.seg);
    if (b) {
      view.fitBbox(minExtent(b, 0.0032), 40);
      await new Promise((resolve) => view.map.once("idle", resolve));
    }
  }
  await document.fonts.ready;
  window.cardReady = { alt: altText(c, meta), title: c.title, format, width: f.width * f.scale, height: f.height * f.scale };
}

main().catch((err) => {
  document.getElementById("card").innerHTML = `<p role="alert">${esc(err.message)}</p>`;
  window.cardReady = { error: err.message };
});
