import "./style.css";
import { LAYER_INFO, legendHtml, OVERLAY_INFO } from "./layers.js";
import { profileHtml } from "./panel.js";
import { downloadsHtml, imprintHtml, methodHtml, sourcesHtml } from "./pages.js";
import { setupSearch } from "./search.js";
import { parseHash, toHash } from "./state.js";
import { renderTable } from "./table.js";
import { esc } from "./util.js";

const $ = (sel) => document.querySelector(sel);
let state = parseHash(location.hash);
let meta, search, mapView, table, lastFocus;
const idToStreet = new Map();

async function json(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
  return r.json();
}

function writeUrl(push = false) {
  const h = toHash(state);
  if (h !== location.hash) history[push ? "pushState" : "replaceState"](null, "", h);
}

function setState(patch, { push = false } = {}) {
  state = { ...state, ...patch };
  writeUrl(push);
  render();
}

// --- controls --------------------------------------------------------------------------------

function controlsHtml() {
  const layerRadios = Object.entries(LAYER_INFO).map(([k, v]) => `<label class="opt">
    <input type="radio" name="layer" value="${k}" ${state.layer === k ? "checked" : ""}> ${esc(v.title)}</label>`).join("");
  const overlays = Object.entries(OVERLAY_INFO).map(([k, v]) => `<label class="opt">
    <input type="checkbox" name="ov" value="${k}" ${state.overlays.includes(k) ? "checked" : ""}> ${esc(v)}</label>`).join("");
  const cats = Object.entries(meta.categories).map(([k, c]) => `<label class="opt">
    <input type="checkbox" name="cat" value="${k}" ${state.cats.includes(k) ? "checked" : ""}> ${esc(c.label)} (${k})</label>`).join("");
  const dts = [...Object.keys(meta.discrepancy_types), "keine"].map((k) => `<label class="opt">
    <input type="checkbox" name="dt" value="${k}" ${state.dts.includes(k) ? "checked" : ""}> ${k === "keine" ? "keine Diskrepanz" : esc(k)}</label>`).join("");
  return `
    <fieldset><legend>Ebene</legend>${layerRadios}</fieldset>
    <p class="muted" id="layer-text">${esc(LAYER_INFO[state.layer].text)}</p>
    <div id="legend" aria-live="polite">${legendHtml(state.layer, meta)}</div>
    <fieldset><legend>Zusätzlich anzeigen</legend>${overlays}</fieldset>
    <details ${state.cats.length || state.dts.length || state.prmin || state.bz ? "open" : ""}><summary>Filter</summary>
      <label for="f-bz">Bezirk</label>
      <select id="f-bz" name="bz"><option value="">alle</option><option value="${esc(meta.pilot)}" ${state.bz === meta.pilot ? "selected" : ""}>${esc(meta.pilot)}</option></select>
      <fieldset><legend>Soll-Kategorie</legend>${cats}</fieldset>
      <fieldset><legend>Diskrepanztyp</legend>${dts}</fieldset>
      <label for="f-pr">Priorität mindestens: <output id="f-pr-out">${state.prmin.toLocaleString("de-DE")}</output></label>
      <input id="f-pr" name="pr" type="range" min="0" max="3" step="0.25" value="${state.prmin}">
      <button type="button" id="f-reset" class="secondary">Filter zurücksetzen</button>
    </details>`;
}

function bindControls(root) {
  root.onchange = (ev) => {
    const t = ev.target;
    const checked = (name) => [...root.querySelectorAll(`input[name="${name}"]:checked`)].map((i) => i.value);
    if (t.name === "layer") setState({ layer: t.value });
    else if (t.name === "ov") setState({ overlays: checked("ov") });
    else if (t.name === "cat") setState({ cats: checked("cat") });
    else if (t.name === "dt") setState({ dts: checked("dt") });
    else if (t.name === "bz") setState({ bz: t.value });
    else if (t.name === "pr") setState({ prmin: Number(t.value) });
  };
  root.oninput = (ev) => {
    if (ev.target.name === "pr") $("#f-pr-out").textContent = Number(ev.target.value).toLocaleString("de-DE");
  };
  root.onclick = (ev) => {
    if (ev.target.id === "f-reset") setState({ cats: [], dts: [], prmin: 0, bz: "" });
  };
}

function renderControls() {
  const root = $("#controls-body");
  const focusName = document.activeElement?.name;
  const focusValue = document.activeElement?.value;
  root.innerHTML = controlsHtml();
  if (focusName) root.querySelector(`[name="${focusName}"][value="${CSS.escape(focusValue ?? "")}"], [name="${focusName}"]`)?.focus();
}

// --- panel -----------------------------------------------------------------------------------

async function openPanel(id) {
  const panel = $("#panel");
  const body = $("#panel-body");
  lastFocus = document.activeElement;
  panel.hidden = false;
  document.body.classList.add("panel-open");
  body.innerHTML = "<p>Lade Steckbrief …</p>";
  try {
    const p = await json(`segments/${id}.json`);
    body.innerHTML = profileHtml(p, meta, location.href);
    const street = idToStreet.get(id);
    $("#panel-show").hidden = !street;
  } catch {
    body.innerHTML = "<p>Steckbrief nicht gefunden.</p>";
  }
  panel.focus();
  mapView?.resize();
}

function closePanel() {
  $("#panel").hidden = true;
  document.body.classList.remove("panel-open");
  mapView?.resize();
  lastFocus?.focus?.();
}

// --- render ----------------------------------------------------------------------------------

async function render() {
  for (const sec of document.querySelectorAll("[data-page]")) sec.hidden = sec.dataset.page !== state.page;
  for (const a of document.querySelectorAll("nav.main a")) {
    if (a.getAttribute("href") === `#${state.page}`) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  }
  document.title = `${meta.site_title}${state.page === "karte" ? "" : ` – ${$(`nav.main a[href="#${state.page}"]`)?.textContent}`}`;
  if (state.page === "karte") {
    renderControls();
    if (!mapView) {
      const { createMap } = await import("./map.js");
      mapView = createMap($("#map"), meta, state, {
        onSelect: (id) => setState({ seg: id }),
        onMove: (m) => { state = { ...state, map: m }; writeUrl(); },
      });
    } else {
      mapView.resize();
    }
    mapView.update(state);
  }
  if (state.page === "tabelle") {
    if (!table) {
      const rows = await json("table.json");
      table = renderTable($("#table-root"), rows, () => state, { onOpen: (id) => setState({ seg: id }) });
    } else {
      table.redraw();
    }
  }
  const pages = { methode: async () => methodHtml(meta, await (await fetch("changelog.md")).text()),
    downloads: async () => downloadsHtml(meta), quellen: () => sourcesHtml(meta), impressum: async () => imprintHtml(meta) };
  const sec = $(`[data-page="${state.page}"]`);
  if (pages[state.page] && !sec.dataset.loaded) {
    sec.innerHTML = await pages[state.page]();
    sec.dataset.loaded = "1";
  }
  const panelId = $("#panel").dataset.id;
  if (state.seg && state.seg !== panelId) { $("#panel").dataset.id = state.seg; openPanel(state.seg); }
  if (!state.seg && !$("#panel").hidden) { $("#panel").dataset.id = ""; closePanel(); }
}

async function init() {
  meta = await json("meta.json");
  search = await json("search.json");
  for (const s of search) for (const id of s.ids) idToStreet.set(id, s);
  $("#banner-text").textContent = `${meta.disclaimer}. Datenstand ${new Date(meta.data_date).toLocaleDateString("de-DE")}, Regelwerk ${meta.rules_version}.`;
  bindControls($("#controls-body"));
  setupSearch($("#search"), $("#search-list"), search, (s) => {
    setState({ page: "karte" }, { push: true });
    mapView?.fitBbox(s.bbox);
  });
  $("#panel-close").onclick = () => setState({ seg: null });
  $("#panel-show").onclick = () => {
    const s = idToStreet.get(state.seg);
    setState({ page: "karte" }, { push: true });
    if (s) setTimeout(() => mapView?.fitBbox(s.bbox), 50);
  };
  document.addEventListener("keydown", (ev) => {
    if (ev.key === "Escape" && !$("#panel").hidden) setState({ seg: null });
  });
  for (const a of document.querySelectorAll("nav.main a")) {
    a.addEventListener("click", (ev) => {
      ev.preventDefault();
      setState({ page: a.getAttribute("href").slice(1) }, { push: true });
      $("#main").focus();
    });
  }
  window.addEventListener("popstate", () => { state = parseHash(location.hash); render(); });
  window.addEventListener("hashchange", () => { state = parseHash(location.hash); render(); });
  await render();
}

init().catch((err) => {
  $("#main").innerHTML = `<p role="alert">Die Daten konnten nicht geladen werden (${esc(err.message)}).</p>`;
});
