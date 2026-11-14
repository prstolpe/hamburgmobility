// Map view shared by both redesign prototypes: theme switcher, legend in words next to the map, map, profile panel
// (desktop: right column; mobile: sheet from below with the heights closed/half/full). State in the URL hash
// (theme, view, seg, jct); old links with ?layer= are rewritten (docs/redesign/02_information_architecture.md).
import { esc } from "../../../web/src/util.js";
import { createMap, legendHtml, THEMES } from "./map.js";
import { junctionHtml, segmentHtml } from "./profile.js";

const root = (p) => new URL(p, `${location.origin}/`).href;
const json = async (p) => { const r = await fetch(root(p)); if (!r.ok) throw new Error(`${p}: ${r.status}`); return r.json(); };

export const OLD_LAYER = { cat: ["aufgabe", "ziel"], speed: ["aufgabe", "heute"], hvs: ["aufgabe", "ziel"], disc: ["abweichung", "ziel"],
  width: ["platz", "ziel"], feas: ["platz", "ziel"], cfit: ["platz", "ziel"], lanes: ["platz", "fahrstreifen"], cnet: ["rad", "ziel"],
  cfac: ["rad", "ziel"], cgap: ["rad", "luecken"], coff: ["rad", "amtlich"], jct: ["knoten", "ziel"] };

export function readState() {
  const q = new URLSearchParams(location.hash.split("?")[1] ?? "");
  let theme = q.get("theme"); let view = q.get("view");
  if (!theme && q.get("layer") && OLD_LAYER[q.get("layer")]) [theme, view] = OLD_LAYER[q.get("layer")];
  theme = THEMES[theme] ? theme : "aufgabe";
  view = THEMES[theme].views[view] ? view : Object.keys(THEMES[theme].views)[0];
  return { theme, view, seg: q.get("seg"), jct: q.get("jct") };
}

export async function loadData() {
  const [meta, district, search] = await Promise.all([json("meta.json"), json("redesign/data/districts.json"), json("search.json")]);
  return { meta, district, search: search.filter((s) => s.bezirk === district.focus) };
}

export function mountMapView(el, { meta, district, page = "#karte", onChange }) {
  const mobile = () => matchMedia("(max-width: 767px)").matches;
  el.innerHTML = `
    <div class="themes" role="toolbar" aria-label="Thema der Karte">
      ${Object.entries(THEMES).map(([k, t]) => `<button type="button" data-theme="${k}" aria-pressed="false">${esc(t.title)}</button>`).join("")}
      <span class="views" role="group" aria-label="Ansicht"></span>
    </div>
    <div class="mapgrid">
      <aside class="legend" aria-live="polite" tabindex="0" aria-label="Legende"></aside>
      <div class="map" id="map" role="region" aria-label="Karte ${esc(district.focus)}"></div>
      <aside class="panel" hidden tabindex="-1"><button type="button" class="close">Schließen</button><div class="panel-body"></div></aside>
    </div>`;
  const legend = el.querySelector(".legend");
  const panel = el.querySelector(".panel");
  const body = el.querySelector(".panel-body");
  let state = readState();
  const m = createMap(el.querySelector("#map"), { meta, district, bz: district.focus,
    onSelect: (id) => openSegment(id), onSelectJunction: (id) => openJunction(id) });

  function writeState() {
    const q = new URLSearchParams({ theme: state.theme, view: state.view });
    if (state.seg) q.set("seg", state.seg);
    if (state.jct) q.set("jct", state.jct);
    history.replaceState(null, "", `${page}?${q}`);
    onChange?.(state);
  }
  function render() {
    for (const b of el.querySelectorAll("[data-theme]")) b.setAttribute("aria-pressed", String(b.dataset.theme === state.theme));
    const views = THEMES[state.theme].views;
    el.querySelector(".views").innerHTML = Object.keys(views).length > 1 ? `<span>Ansicht:</span>${Object.entries(views).map(([k, v]) =>
      `<button type="button" data-view="${k}" aria-pressed="${k === state.view}">${esc(v)}</button>`).join("")}` : "";
    for (const b of el.querySelectorAll("[data-view]")) b.style.cssText = b.dataset.view === state.view ? "background:#111;color:#fff" : "";
    legend.innerHTML = legendHtml(state.theme, state.view, meta) + `<p>Nur ${esc(district.focus)} · Grau: nicht bewertet. Kreuzungen ab Zoom 14 antippen.</p>`;
    m.show(state.theme, state.view);
    writeState();
  }
  el.querySelector(".themes").addEventListener("click", (ev) => {
    const t = ev.target.closest("[data-theme]");
    const v = ev.target.closest("[data-view]");
    if (t) { state.theme = t.dataset.theme; state.view = Object.keys(THEMES[state.theme].views)[0]; render(); }
    if (v) { state.view = v.dataset.view; render(); }
  });
  function showPanel(html) {
    body.innerHTML = html;
    panel.hidden = false;
    el.classList.add("with-panel");
    panel.scrollTop = 0;
    panel.classList.toggle("half", mobile());
    panel.focus({ preventScroll: true });
    body.querySelector("details.l2")?.addEventListener("toggle", (e) => { if (e.target.open) panel.classList.remove("half"); });
  }
  async function openSegment(id, { fly = false, at = null } = {}) {
    try {
      const p = await json(`segments/${id}.json`);
      state.seg = id; state.jct = null;
      m.select(id);
      showPanel(segmentHtml(p, meta, { level2Open: !mobile() }));
      if (fly && at) m.flyTo(at, 16);
      writeState();
    } catch (e) { console.error(e); }
  }
  async function openJunction(id, { fly = false, at = null } = {}) {
    try {
      const j = await json(`junctions/${id}.json`);
      state.jct = id; state.seg = null;
      m.select(null);
      showPanel(junctionHtml(j, meta, { level2Open: !mobile() }));
      if (fly && at) m.flyTo(at, 17);
      writeState();
    } catch (e) { console.error(e); }
  }
  el.querySelector(".close").addEventListener("click", () => {
    panel.hidden = true; el.classList.remove("with-panel"); state.seg = state.jct = null; m.select(null); writeState();
  });
  render();
  if (state.seg) openSegment(state.seg);
  if (state.jct) openJunction(state.jct);
  return { map: m, openSegment, openJunction,
    setTheme(theme, view) { state.theme = theme; state.view = view ?? Object.keys(THEMES[theme].views)[0]; render(); } };
}

/** Street search over search.json (focus Bezirk): suggestion list, Enter or click opens the longest segment. */
export function bindSearch(input, list, search, onPick) {
  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    const hits = q.length < 2 ? [] : search.filter((s) => s.name.toLowerCase().includes(q)).slice(0, 8);
    list.innerHTML = hits.map((h, i) => `<li role="option" id="opt-${i}" data-i="${i}">${esc(h.name)}</li>`).join("");
    list.hidden = !hits.length;
    list._hits = hits;
  });
  list.addEventListener("click", (ev) => {
    const li = ev.target.closest("li");
    if (!li) return;
    const h = list._hits[Number(li.dataset.i)];
    list.hidden = true; input.value = h.name;
    onPick(h);
  });
  input.addEventListener("keydown", (ev) => { if (ev.key === "Enter" && list._hits?.length) { list.querySelector("li").click(); } });
}
