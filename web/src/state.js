// App state <-> URL hash, e.g. #karte?theme=rad&view=luecken&bz=Altona&seg=seg_x&map=14/53.57/9.95
// Redesign 2026-11 (package 2): five themes with views instead of 13 layers; each view maps to one map layer of
// layers.js (state.layer is derived). Old links (?layer=…, #tabelle, #downloads, #quellen) are rewritten on load,
// see docs/redesign/02_information_architecture.md. Defaults are left out of the URL so shared links stay short.

export const PAGES = ["karte", "bezirke", "methode", "daten", "impressum"];
const PAGE_ALIASES = { tabelle: "bezirke", downloads: "daten", quellen: "daten" };
export const CYCLING_LAYER_KEYS = ["cnet", "cfac", "cgap", "lanes", "cfit", "jct", "coff"];
export const LAYERS = ["cat", "speed", "disc", "prio", "width", "feas", "hvs", ...CYCLING_LAYER_KEYS];
// sub pages of "methode": chapters (keys as in meta.method.chapters) and the rule reference; the news page
// (#methode/neu) was removed in prompt 25, old links fall back to the summary
export const METHOD_SUBS = ["aufgabe", "abweichung", "platz", "radnetz", "knoten", "sicherheit", "daten", "regeln"];
export const OVERLAYS = ["bus", "cyc", "fac", "acc"];

// theme -> {title, views: {view: {label, layer, level, enabled}}}; level 3 views are offered under "Mehr Ansichten".
// enabled: false switches a view off without deleting it (prompt 25): no button, no data, links fall back to the
// theme's first enabled view. To switch a view back on, delete its `enabled: false`.
export const THEMES = {
  aufgabe: { title: "Aufgabe und Tempo", views: {
    ziel: { label: "Ziel", layer: "cat" }, heute: { label: "heute", layer: "speed" },
    hvs: { label: "Hauptverkehrsstraßen (Vergleich)", layer: "hvs", level: 3 } } },
  abweichung: { title: "Heute und Ziel", views: {
    ziel: { label: "Abweichung", layer: "disc" }, prio: { label: "Dringlichkeit", layer: "prio" } } },
  platz: { title: "Fahrstreifen", views: {
    ziel: { label: "Passt das Ziel?", layer: "cfit", enabled: false },
    fahrstreifen: { label: "Fahrstreifen", layer: "lanes" },
    breite: { label: "Breite der Straße", layer: "width", level: 3, enabled: false },
    regelprofil: { label: "Regelprofil der Aufgabe", layer: "feas", level: 3, enabled: false } } },
  rad: { title: "Radnetz", views: {
    ziel: { label: "Ziel", layer: "cnet" },
    radweg: { label: "Radweg", layer: "cfac", enabled: false },
    luecken: { label: "Lücken", layer: "cgap", enabled: false },
    amtlich: { label: "amtliches Netz", layer: "coff", level: 3 } } },
  knoten: { title: "Kreuzungen", views: { ziel: { label: "Ziel", layer: "jct" } } },
};
/** Enabled views of a theme as [id, view] pairs, in order. */
export const viewsOf = (theme) => Object.entries(THEMES[theme]?.views ?? {}).filter(([, v]) => v.enabled !== false);
const firstView = (theme) => viewsOf(theme)[0]?.[0] ?? null; // every theme keeps one enabled view (test/state.test.js)
const isEnabled = (theme, view) => viewsOf(theme).some(([v]) => v === view);
export const layerOf = (theme, view) => THEMES[theme]?.views[view]?.layer ?? null;
// old ?layer= links: also map disabled views, withView() then falls back to the theme's first enabled view
const OLD_LAYER = Object.fromEntries(Object.entries(THEMES).flatMap(([t, th]) =>
  Object.entries(th.views).map(([v, x]) => [x.layer, [t, v]])));

export const DEFAULTS = Object.freeze({
  page: "karte", theme: "aufgabe", view: "ziel", layer: "cat", overlays: [], cats: [], dts: [], prmin: 0, bz: "",
  seg: null, jct: null, table: false, map: null, sub: null, rule: null,
});

const list = (v, allowed) => (v ? v.split(",").filter((x) => !allowed || allowed.includes(x)) : []);

/** Set theme/view (falling back to valid values) and the derived map layer. */
export function withView(state, theme, view) {
  const t = THEMES[theme] ? theme : DEFAULTS.theme;
  const v = isEnabled(t, view) ? view : firstView(t);
  return { ...state, theme: t, view: v, layer: layerOf(t, v) };
}

export function parseHash(hash) {
  const raw = (hash || "").replace(/^#\/?/, "");
  const [pathPart, query = ""] = raw.split("?");
  const [pagePart, subPart = ""] = pathPart.split("/");
  const p = new URLSearchParams(query);
  let state = { ...DEFAULTS, overlays: [], cats: [], dts: [] };
  const page = PAGE_ALIASES[pagePart] ?? pagePart;
  if (PAGES.includes(page)) state.page = page;
  if (pagePart === "radnetz") { state.page = "methode"; state.sub = "radnetz"; }  // old link
  else if (state.page === "methode" && METHOD_SUBS.includes(subPart)) state.sub = subPart;
  state.rule = /^[A-Za-z0-9-]+$/.test(p.get("regel") || "") ? p.get("regel") : null;
  state.overlays = list(p.get("ov"), OVERLAYS);
  let theme = p.get("theme");
  let view = p.get("view");
  if (!THEMES[theme] && OLD_LAYER[p.get("layer")]) [theme, view] = OLD_LAYER[p.get("layer")];
  if (!THEMES[theme] && state.overlays.includes("cyc")) {
    [theme, view] = ["rad", "amtlich"];  // the old overlay "Radnetz Hamburg" is now a view of the theme Radnetz
    state.overlays = state.overlays.filter((o) => o !== "cyc");
  }
  state = withView(state, theme, view);
  state.cats = list(p.get("cat"));
  state.dts = list(p.get("dt"));
  const pr = Number(p.get("pr"));
  state.prmin = Number.isFinite(pr) && pr > 0 ? Math.min(pr, 3) : 0;
  state.bz = p.get("bz") || "";
  state.table = state.page === "bezirke" && Boolean(state.bz) && (pagePart === "tabelle" || p.get("tabelle") === "1");
  state.seg = /^seg_[0-9a-f]+$/.test(p.get("seg") || "") ? p.get("seg") : null;
  state.jct = /^[0-9]+$/.test(p.get("jct") || "") ? p.get("jct") : null;
  const m = (p.get("map") || "").split("/").map(Number);
  if (m.length === 3 && m.every(Number.isFinite)) state.map = { zoom: m[0], lat: m[1], lon: m[2] };
  return state;
}

export function toHash(state) {
  const p = new URLSearchParams();
  if (state.theme !== DEFAULTS.theme) p.set("theme", state.theme);
  if (THEMES[state.theme] && state.view !== firstView(state.theme)) p.set("view", state.view);
  if (state.overlays.length) p.set("ov", state.overlays.join(","));
  if (state.cats.length) p.set("cat", state.cats.join(","));
  if (state.dts.length) p.set("dt", state.dts.join(","));
  if (state.prmin > 0) p.set("pr", String(state.prmin));
  if (state.bz) p.set("bz", state.bz);
  if (state.table) p.set("tabelle", "1");
  if (state.seg) p.set("seg", state.seg);
  if (state.jct) p.set("jct", state.jct);
  if (state.page === "methode" && state.sub === "regeln" && state.rule) p.set("regel", state.rule);
  if (state.map) p.set("map", `${state.map.zoom.toFixed(2)}/${state.map.lat.toFixed(5)}/${state.map.lon.toFixed(5)}`);
  const q = p.toString().replaceAll("%2C", ",").replaceAll("%2F", "/");
  const path = state.page === "methode" && state.sub ? `methode/${state.sub}` : state.page;
  return `#${path}${q ? `?${q}` : ""}`;
}

/** Does a table row pass the current filters? (same logic as the map filter in layers.js) */
export function rowMatches(row, state) {
  if (state.cats.length && !state.cats.includes(row.cat)) return false;
  if (state.dts.length && !state.dts.includes(row.dt ?? "keine")) return false;
  if (state.prmin > 0 && !((row.pr ?? 0) >= state.prmin)) return false;
  if (state.bz && row.bz && row.bz !== state.bz) return false;
  return true;
}
