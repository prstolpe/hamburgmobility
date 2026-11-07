// App state <-> URL hash, e.g. #karte?layer=disc&cat=GOW30,ETW30&dt=D1&pr=1&seg=seg_x&map=14/53.57/9.95
// Cycling layers (prompt 21): layer=cnet|cfac|cgap|lanes|cfit|jct|coff, jct=<node_id> opens a junction profile.
// Defaults are left out of the URL so that shared links stay short.

export const PAGES = ["karte", "tabelle", "methode", "radnetz", "downloads", "quellen", "impressum"];
export const CYCLING_LAYER_KEYS = ["cnet", "cfac", "cgap", "lanes", "cfit", "jct", "coff"];
export const LAYERS = ["cat", "speed", "disc", "width", "feas", "hvs", ...CYCLING_LAYER_KEYS];
export const OVERLAYS = ["bus", "cyc", "fac", "acc"];

export const DEFAULTS = Object.freeze({
  page: "karte", layer: "cat", overlays: [], cats: [], dts: [], prmin: 0, bz: "", seg: null, jct: null, map: null,
});

const list = (v, allowed) => (v ? v.split(",").filter((x) => !allowed || allowed.includes(x)) : []);

export function parseHash(hash) {
  const raw = (hash || "").replace(/^#\/?/, "");
  const [pagePart, query = ""] = raw.split("?");
  const p = new URLSearchParams(query);
  const state = { ...DEFAULTS, overlays: [], cats: [], dts: [] };
  if (PAGES.includes(pagePart)) state.page = pagePart;
  if (LAYERS.includes(p.get("layer"))) state.layer = p.get("layer");
  state.overlays = list(p.get("ov"), OVERLAYS);
  state.cats = list(p.get("cat"));
  state.dts = list(p.get("dt"));
  const pr = Number(p.get("pr"));
  state.prmin = Number.isFinite(pr) && pr > 0 ? Math.min(pr, 3) : 0;
  state.bz = p.get("bz") || "";
  state.seg = /^seg_[0-9a-f]+$/.test(p.get("seg") || "") ? p.get("seg") : null;
  state.jct = /^[0-9]+$/.test(p.get("jct") || "") ? p.get("jct") : null;
  const m = (p.get("map") || "").split("/").map(Number);
  if (m.length === 3 && m.every(Number.isFinite)) state.map = { zoom: m[0], lat: m[1], lon: m[2] };
  return state;
}

export function toHash(state) {
  const p = new URLSearchParams();
  if (state.layer !== DEFAULTS.layer) p.set("layer", state.layer);
  if (state.overlays.length) p.set("ov", state.overlays.join(","));
  if (state.cats.length) p.set("cat", state.cats.join(","));
  if (state.dts.length) p.set("dt", state.dts.join(","));
  if (state.prmin > 0) p.set("pr", String(state.prmin));
  if (state.bz) p.set("bz", state.bz);
  if (state.seg) p.set("seg", state.seg);
  if (state.jct) p.set("jct", state.jct);
  if (state.map) p.set("map", `${state.map.zoom.toFixed(2)}/${state.map.lat.toFixed(5)}/${state.map.lon.toFixed(5)}`);
  const q = p.toString().replaceAll("%2C", ",").replaceAll("%2F", "/");
  return `#${state.page}${q ? `?${q}` : ""}`;
}

/** Does a table row pass the current filters? (same logic as the map filter in layers.js) */
export function rowMatches(row, state) {
  if (state.cats.length && !state.cats.includes(row.cat)) return false;
  if (state.dts.length && !state.dts.includes(row.dt ?? "keine")) return false;
  if (state.prmin > 0 && !((row.pr ?? 0) >= state.prmin)) return false;
  if (state.bz && row.bz && row.bz !== state.bz) return false;
  return true;
}
