import "./style.css";
import { dataHtml } from "./datapage.js";
import { bindDistrictPage, districtHtml, districtListHtml } from "./districts.js";
import { placeOf } from "./layers.js";
import { copyLink, createMapPanel } from "./map_panel.js";
import { chapterHtml, referenceHtml, referenceListHtml, resolveRule, summaryHtml } from "./method.js";
import { imprintHtml } from "./pages.js";
import { placesHtml } from "./places.js";
import { junctionHtml, segmentHtml } from "./profile.js";
import { setupSearch } from "./search.js";
import { DEFAULTS, parseHash, toHash, withView } from "./state.js";
import { renderTable } from "./table.js";
import { esc } from "./util.js";

// Redesign 2026-11 (package 2): map as start page with five themes, legend in words next to the map, profiles in
// three levels, district page, data page; navigation Karte · Bezirke · Methode · Daten.

const $ = (sel) => document.querySelector(sel);
const INTRO_KEY = "sfp-intro-seen";
const mobile = () => matchMedia("(max-width: 760px)").matches;
let state = parseHash(location.hash);
let meta, mapView, table, tableBz, lastFocus;
let panel = null; // map panel (prompt 28)
const idToStreet = new Map();
const junctionAt = new Map(); // node id -> [lon, lat] (search_junctions.json)

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
  if ("theme" in patch || "view" in patch) state = withView(state, state.theme, state.view);
  writeUrl(push);
  render();
}

// --- map panel (prompt 28): theme, legend, layers, filters on the left; bottom sheet on phones ------------------

/** Link to one segment or junction (version 2 URL, no camera: it zooms to the item). */
function shareUrl({ kind, id }) {
  return `${location.origin}${location.pathname}${toHash({ ...DEFAULTS, page: "karte", ...(kind === "jct" ? { jct: id } : { seg: id }) })}`;
}

/** Switch a special place on (and zoom to it) or off. */
function showPlace(id, { push = false } = {}) {
  const fromOtherPage = state.page !== "karte";
  setState({ page: "karte", place: id }, { push });
  const p = placeOf(state, meta);
  if (p?.bbox) setTimeout(() => mapView?.fitBbox(p.bbox), 50);
  if (fromOtherPage && id) setTimeout(() => $(`#map-chips [data-remove="place:${CSS.escape(id)}"]`)?.focus({ preventScroll: true }), 60);
}

// --- intro box on the first visit -----------------------------------------------------------

function storage(op, key, value) {
  try { return op === "get" ? localStorage.getItem(key) : localStorage.setItem(key, value); } catch { return null; }
}

function renderIntro() {
  const box = $("#intro");
  const t = meta.site_texts;
  if (!t || state.page !== "karte" || storage("get", INTRO_KEY) || state.seg || state.jct) { box.hidden = true; return; }
  box.innerHTML = `<h2 id="intro-title">${esc(t.intro_title)}</h2><p>${esc(t.intro)}</p><p>${esc(t.intro_hint)}</p>
    <p><a href="#methode">${esc(t.intro_more)}</a></p><button type="button" id="intro-close">Verstanden</button>`;
  box.hidden = false;
  // focus goes to the map panel, not to the search (on phones that would open the keyboard; walkthrough finding 12)
  $("#intro-close").onclick = () => { storage("set", INTRO_KEY, "1"); box.hidden = true; $("#map-panel [data-theme][aria-checked='true']")?.focus(); };
}

// --- panel -----------------------------------------------------------------------------------

let redirects = null;
async function junctionRedirects() {
  redirects ??= await json("junction_redirects.json").catch(() => ({}));
  return redirects;
}

async function openPanel(id, kind = "seg") {
  const panel = $("#panel");
  const body = $("#panel-body");
  lastFocus = document.activeElement;
  panel.hidden = false;
  document.body.classList.add("panel-open");
  body.innerHTML = "<p>Lade Steckbrief …</p>";
  $("#panel-copy-status").textContent = "";
  const opts = { level2Open: !mobile() };
  try {
    if (kind === "jct") {
      body.innerHTML = junctionHtml(await json(`junctions/${id}.json`), meta, location.href, opts);
      $("#panel-show").hidden = true;
    } else {
      body.innerHTML = segmentHtml(await json(`segments/${id}.json`), meta, location.href, opts);
      $("#panel-show").hidden = !idToStreet.get(id);
    }
  } catch {
    // a pseudo-junction joined by the arm filter (J-M-01) redirects to its junction; a dropped one gets a note
    const to = kind === "jct" ? (await junctionRedirects())[id] : null;
    if (to) { setState({ jct: to, seg: null }); return; }
    body.innerHTML = `<p>${esc(kind === "jct" ? meta.site_texts?.junction_gone ?? "Steckbrief nicht gefunden." : "Steckbrief nicht gefunden.")}</p>`;
  }
  panel.focus();
  mapView?.resize();
  if (mobile()) mapView?.setBottomPadding(panel.offsetHeight); // keep the selection above the profile sheet
}

function closePanel() {
  $("#panel").hidden = true;
  document.body.classList.remove("panel-open");
  mapView?.setBottomPadding(0);
  mapView?.resize();
  // on phones not back into the search (it would open the keyboard)
  const back = lastFocus && document.contains(lastFocus) && !(mobile() && lastFocus.id === "search") ? lastFocus : $("#map-panel [data-theme][aria-checked='true']");
  back?.focus?.({ preventScroll: true });
}

// A sketch in the panel (cross section, junction) opens enlarged in a modal dialog; focus returns to its button.
function initSketchDialog() {
  const dialog = $("#sketch-dialog");
  const body = dialog.querySelector(".sketch-dialog-body");
  let opener = null;
  $("#panel-body").addEventListener("click", (ev) => {
    const btn = ev.target.closest(".sketch-zoom");
    if (!btn) return;
    const svg = btn.querySelector("svg").cloneNode(true);
    const t = svg.querySelector("title");
    if (t) { t.id = `${t.id}-zoom`; svg.setAttribute("aria-labelledby", t.id); }
    body.replaceChildren(svg);
    opener = btn;
    dialog.showModal();
  });
  $("#sketch-close").onclick = () => dialog.close();
  dialog.addEventListener("click", (ev) => { if (ev.target === dialog) dialog.close(); }); // backdrop
  dialog.addEventListener("close", () => { body.replaceChildren(); opener?.focus(); opener = null; });
}

// --- district page -----------------------------------------------------------------------------

async function renderDistricts() {
  const root = $("#bezirke-root");
  const tableRoot = $("#table-root");
  if (!meta.overview) { root.innerHTML = "<h1>Bezirke</h1><p>Die Bezirksübersicht ist in diesem Datenstand nicht enthalten.</p>"; return; }
  if (!state.bz || !meta.overview.files[state.bz]) {
    root.innerHTML = districtListHtml(meta);
    tableRoot.innerHTML = "";
    table = tableBz = null;
  } else {
    root.innerHTML = districtHtml(meta, await json(`districts/${meta.overview.files[state.bz]}`));
    if (state.table) {
      if (state.bz !== tableBz) {
        const rows = await json(`table/${meta.tables[state.bz]}`);
        tableBz = state.bz;
        table = renderTable(tableRoot, rows, () => state, {
          onOpen: (id) => setState({ seg: id }), onOtherDistrict: () => setState({ bz: "", table: false }),
          caption: `Alle Straßenstücke im Bezirk ${state.bz}`, meta,
        });
      } else {
        table.redraw();
      }
    } else {
      tableRoot.innerHTML = "";
      table = tableBz = null;
    }
  }
  bindDistrictPage(root, {
    onPickDistrict: (bz) => setState({ bz, table: false }, { push: true }),
    onOpenSegment: (id, at) => { setState({ page: "karte", seg: id, jct: null }, { push: true }); if (at) setTimeout(() => mapView?.flyTo(at, 16), 50); },
    onOpenJunction: (id, at) => { setState({ page: "karte", jct: id, seg: null }, { push: true }); if (at) setTimeout(() => mapView?.flyTo(at, 17), 50); },
    onShowTable: () => setState({ table: true }),
  });
}

const ORG_NAME = "Hamburg Mobility Revolution";

// --- method page ------------------------------------------------------------------------------

let rulesData;
let ruleQuery = { q: "", onlyAssumption: false };

async function loadRules() {
  rulesData ??= await json("rules.json");
  return rulesData;
}

async function renderMethod() {
  const sec = $('[data-page="methode"]');
  const method = meta.method;
  if (!method) { sec.innerHTML = "<h1>Methode</h1><p>Die Methodenseite ist in diesem Datenstand nicht enthalten.</p>"; return; }
  const sub = state.sub;
  const key = `${sub ?? ""}|${state.rule ?? ""}`;
  if (sec.dataset.loaded === key) return;
  sec.dataset.loaded = key;
  if (!state.rule) window.scrollTo(0, 0);
  try {
    if (!sub) sec.innerHTML = summaryHtml(method, meta);
    else if (sub === "regeln") {
      const data = await loadRules();
      if (state.rule) ruleQuery = { q: "", onlyAssumption: false };
      sec.innerHTML = referenceHtml(method, data.rules, ruleQuery, data.versions, meta.github_repo);
      bindReference(sec, data);
      if (state.rule) {
        const li = document.getElementById(`regel-${resolveRule(data.rules, state.rule)}`);
        if (li) { li.querySelector("details")?.setAttribute("open", ""); li.scrollIntoView(); }
      }
    } else sec.innerHTML = chapterHtml(method, sub, (await loadRules()).rules, meta);
  } catch (err) {
    sec.dataset.loaded = "";
    sec.innerHTML = `<p role="alert">Die Seite konnte nicht geladen werden (${esc(err.message)}).</p>`;
  }
}

function bindReference(sec, data) {
  const list = sec.querySelector("#rule-list");
  const update = () => {
    ruleQuery = { q: sec.querySelector("#rule-q").value, onlyAssumption: sec.querySelector("#rule-assume").checked };
    list.innerHTML = referenceListHtml(meta.method, data.rules, ruleQuery, meta.github_repo);
  };
  sec.querySelector("#rule-q").oninput = update;
  sec.querySelector("#rule-assume").onchange = update;
}

// --- render ----------------------------------------------------------------------------------

async function render() {
  for (const sec of document.querySelectorAll("[data-page]")) sec.hidden = sec.dataset.page !== state.page;
  for (const a of document.querySelectorAll("nav.main a")) {
    if (a.getAttribute("href") === `#${state.page}`) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  }
  const titles = { bezirke: "Bezirke", orte: "Besondere Orte", methode: "Methode", daten: "Daten", impressum: "Impressum" };
  const chapter = meta.method?.chapters?.find((c) => c.key === state.sub);
  const subTitle = state.page !== "methode" ? null : state.sub === "regeln" ? "Alle Regeln" : chapter?.title;
  document.title = `${meta.site_title}${titles[state.page] ? ` – ${subTitle ? `${titles.methode}: ${subTitle}` : titles[state.page]}` : ""} · ${ORG_NAME}`;
  document.body.classList.toggle("on-karte", state.page === "karte");
  setHeaderHeight();
  if (state.page === "karte") {
    renderIntro();
    if (!mapView) {
      const { createMap } = await import("./map.js");
      mapView = createMap($("#map"), meta, state, {
        onSelect: (id) => panel.onFeature("seg", id) || setState({ seg: id, jct: null }, { push: true }),
        onSelectJunction: (id) => panel.onFeature("jct", id) || setState({ jct: id, seg: null }, { push: true }),
        onMove: (m) => { state = { ...state, map: m }; writeUrl(); },
      });
      const p = placeOf(state, meta);
      // a link without a camera (e.g. from "Link kopieren"): zoom to the selection, else to the place
      if (!state.map && state.jct && junctionAt.has(state.jct)) mapView.flyTo(junctionAt.get(state.jct), 17);
      else if (!state.map && state.seg && idToStreet.get(state.seg)) mapView.fitBbox(idToStreet.get(state.seg).bbox);
      else if (p?.bbox && !state.map) mapView.fitBbox(p.bbox);
    } else {
      mapView.resize();
    }
    mapView.update(state);
    panel.render();
  }
  if (state.page === "bezirke") await renderDistricts();
  if (state.page === "methode") await renderMethod();
  else {
    const pages = { daten: async () => dataHtml(meta), impressum: async () => imprintHtml(meta), orte: async () => placesHtml(meta) };
    const sec = $(`[data-page="${state.page}"]`);
    if (pages[state.page] && !sec.dataset.loaded) {
      sec.innerHTML = await pages[state.page]();
      sec.dataset.loaded = "1";
    }
  }
  const panelId = $("#panel").dataset.id;
  const want = state.jct ? `jct:${state.jct}` : state.seg ? `seg:${state.seg}` : "";
  if (want && want !== panelId) { $("#panel").dataset.id = want; openPanel(state.jct ?? state.seg, state.jct ? "jct" : "seg"); }
  if (!want && !$("#panel").hidden) { $("#panel").dataset.id = ""; closePanel(); }
}

// the map page fills the viewport below the header (style.css --hdr); the compact phone header changes its height
function setHeaderHeight() {
  document.documentElement.style.setProperty("--hdr", `${document.querySelector("header.site").offsetHeight}px`);
}

async function init() {
  addEventListener("resize", () => { setHeaderHeight(); });
  meta = await json("meta.json");
  const streets = await json("search.json");
  const junctions = meta.overview ? await json("search_junctions.json").catch(() => []) : [];
  for (const s of streets) for (const id of s.ids) idToStreet.set(id, s);
  for (const j of junctions) junctionAt.set(String(j.id), [j.lon, j.lat]);
  $("#foot-version").textContent = `Version ${meta.version} · Datenstand ${new Date(meta.data_date).toLocaleDateString("de-DE")}`;
  if (!meta.special_places?.places?.length) document.querySelector('nav.main a[href="#orte"]')?.remove();  // older data
  const entries = [...streets.map((s) => ({ ...s, kind: "seg" })), ...junctions.map((j) => ({ ...j, kind: "jct" }))];
  setupSearch($("#search"), $("#search-list"), entries, (s) => {
    if (s.kind === "jct") {
      setState({ page: "karte", jct: s.id, seg: null }, { push: true });
      setTimeout(() => mapView?.flyTo([s.lon, s.lat], 17), 50);
    } else {
      setState({ page: "karte", seg: s.ids[0], jct: null }, { push: true });
      setTimeout(() => mapView?.fitBbox(s.bbox), 50);
    }
  });
  $("#panel-close").onclick = () => setState({ seg: null, jct: null });
  $("#panel-show").onclick = () => {
    const s = idToStreet.get(state.seg);
    setState({ page: "karte" }, { push: true });
    if (s) setTimeout(() => mapView?.fitBbox(s.bbox), 50);
  };
  initSketchDialog();
  if (mobile()) $("#search").placeholder = "Suchen …"; // the long placeholder is cut off in the compact header
  panel = createMapPanel({
    root: $("#map-panel"), chipsRoot: $("#map-chips"), tipRoot: $("#map-tip"), meta, getState: () => state, setState,
    getMap: () => mapView?.map, showPlace, shareUrl, junctionNames: new Map(junctions.map((j) => [String(j.id), j.name])),
  });
  $("#panel-copy").onclick = () => copyLink(shareUrl(state.jct ? { kind: "jct", id: state.jct } : { kind: "seg", id: state.seg }), $("#panel-copy-status"));
  $("#menu-btn").onclick = () => {
    const open = $("header.site").classList.toggle("menu-open");
    $("#menu-btn").setAttribute("aria-expanded", String(open));
  };
  document.addEventListener("keydown", (ev) => {
    if (ev.key !== "Escape" || $("#sketch-dialog").open) return;
    if ($("header.site").classList.contains("menu-open")) { $("#menu-btn").click(); $("#menu-btn").focus(); return; }
    if (!$("#panel").hidden) setState({ seg: null, jct: null });
    else if (state.page === "karte") panel.onEscape();
  });
  for (const a of document.querySelectorAll("nav.main a[href^='#'], a.home, .site-foot a[href^='#']")) {
    a.addEventListener("click", (ev) => {
      ev.preventDefault();
      $("header.site").classList.remove("menu-open");
      $("#menu-btn").setAttribute("aria-expanded", "false");
      const page = a.getAttribute("href").slice(1);
      setState({ page, sub: null, rule: null, ...(page === "bezirke" ? { table: false } : {}) }, { push: true });
      if (a.dataset.anchor) setTimeout(() => document.getElementById(a.dataset.anchor)?.scrollIntoView(), 100);
      else $("#main").focus();
    });
  }
  // "Auf der Karte zeigen" on the page Besondere Orte
  $('[data-page="orte"]').addEventListener("click", (ev) => {
    const b = ev.target.closest("[data-show-place]");
    if (b) showPlace(b.dataset.showPlace, { push: true });
  });
  window.addEventListener("popstate", () => { state = parseHash(location.hash); render(); });
  window.addEventListener("hashchange", () => { state = parseHash(location.hash); render(); });
  writeUrl();  // rewrite old links (?layer=, #tabelle, #downloads, #quellen) to the new parameters
  await render();
}

init().catch((err) => {
  $("#main").innerHTML = `<p role="alert">Die Daten konnten nicht geladen werden (${esc(err.message)}).</p>`;
});
