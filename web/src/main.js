import "./style.css";
import { dataHtml } from "./datapage.js";
import { bindDistrictPage, districtHtml, districtListHtml } from "./districts.js";
import { isCyclingLayer, LAYER_INFO, legendHtml, OVERLAY_INFO } from "./layers.js";
import { chapterHtml, referenceHtml, referenceListHtml, resolveRule, summaryHtml } from "./method.js";
import { imprintHtml } from "./pages.js";
import { junctionHtml, segmentHtml } from "./profile.js";
import { setupSearch } from "./search.js";
import { parseHash, THEMES, toHash, viewsOf, withView } from "./state.js";
import { renderTable } from "./table.js";
import { esc } from "./util.js";

// Redesign 2026-11 (package 2): map as start page with five themes, legend in words next to the map, profiles in
// three levels, district page, data page; navigation Karte · Bezirke · Methode · Daten.

const $ = (sel) => document.querySelector(sel);
const INTRO_KEY = "sfp-intro-seen";
const mobile = () => matchMedia("(max-width: 760px)").matches;
let state = parseHash(location.hash);
let meta, mapView, table, tableBz, lastFocus;
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
  if ("theme" in patch || "view" in patch) state = withView(state, state.theme, state.view);
  writeUrl(push);
  render();
}

// --- map controls: themes above the map, legend and further views next to it ------------------

function themesHtml() {
  const views = viewsOf(state.theme).filter(([, v]) => !v.level);
  return `${Object.entries(THEMES).map(([k, t]) => `<button type="button" data-theme="${k}" aria-pressed="${k === state.theme}">${esc(t.title)}</button>`).join("")}
    ${views.length > 1 ? `<span class="views" role="group" aria-label="Ansicht"><span class="views-label">Ansicht:</span>${views.map(([k, v]) =>
      `<button type="button" data-view="${k}" aria-pressed="${k === state.view}">${esc(v.label)}</button>`).join("")}</span>` : ""}`;
}

function controlsHtml() {
  const more = Object.entries(THEMES).flatMap(([t, th]) => viewsOf(t).filter(([, v]) => v.level === 3)
    .map(([v, x]) => `<li><button type="button" class="link" data-theme-view="${t}:${v}" aria-pressed="${state.theme === t && state.view === v}">${esc(th.title)}: ${esc(x.label)}</button></li>`)).join("");
  const overlays = Object.entries(OVERLAY_INFO).map(([k, v]) => `<label class="opt">
    <input type="checkbox" name="ov" value="${k}" ${state.overlays.includes(k) ? "checked" : ""}> ${esc(v)}</label>`).join("");
  const cats = Object.entries(meta.categories).filter(([k]) => !meta.categories_present || meta.categories_present.includes(k)).map(([k, c]) => `<label class="opt">
    <input type="checkbox" name="cat" value="${k}" ${state.cats.includes(k) ? "checked" : ""}> ${esc(c.label)}</label>`).join("");
  const dtLabel = (k) => (k === "keine" ? "keine Abweichung" : meta.glossary?.terms?.[k]?.plain ?? meta.discrepancy_types[k]);
  const dts = [...Object.keys(meta.discrepancy_types), "keine"].map((k) => `<label class="opt">
    <input type="checkbox" name="dt" value="${k}" ${state.dts.includes(k) ? "checked" : ""}> ${esc(dtLabel(k))}</label>`).join("");
  return `
    <h2 class="legend-title">Was die Farben bedeuten</h2>
    <p id="layer-text">${esc(LAYER_INFO[state.layer].text)}</p>
    <div id="legend" aria-live="polite">${legendHtml(state.layer, meta)}</div>
    <label for="f-bz" class="bz-label">Bezirk</label>
    <select id="f-bz" name="bz"><option value="">ganz Hamburg</option>${meta.districts.map((b) =>
      `<option value="${esc(b)}" ${state.bz === b ? "selected" : ""}>${esc(b)}</option>`).join("")}</select>
    <details class="level l3" ${state.cats.length || state.dts.length || state.prmin || state.overlays.length || THEMES[state.theme].views[state.view].level ? "open" : ""}>
      <summary>Mehr Ansichten und Filter</summary>
      <h3>Weitere Ansichten</h3><ul class="plain">${more}</ul>
      <fieldset><legend>Zusätzlich anzeigen</legend>${overlays}</fieldset>
      ${isCyclingLayer(state.layer) ? '<p class="muted">Bei den Radverkehrs-Ansichten gilt nur der Bezirk.</p>' : ""}
      <fieldset><legend>Aufgabe der Straße</legend>${cats}</fieldset>
      <fieldset><legend>Art der Abweichung</legend>${dts}</fieldset>
      <label for="f-pr">Dringlichkeit mindestens: <output id="f-pr-out">${state.prmin.toLocaleString("de-DE")}</output></label>
      <input id="f-pr" name="pr" type="range" min="0" max="3" step="0.25" value="${state.prmin}">
      <button type="button" id="f-reset" class="secondary">Filter zurücksetzen</button>
    </details>`;
}

function bindControls() {
  $("#themes").onclick = (ev) => {
    const t = ev.target.closest("[data-theme]");
    const v = ev.target.closest("[data-view]");
    if (t) setState({ theme: t.dataset.theme, view: null });
    else if (v) setState({ view: v.dataset.view });
  };
  const root = $("#controls-body");
  root.onchange = (ev) => {
    const t = ev.target;
    const checked = (name) => [...root.querySelectorAll(`input[name="${name}"]:checked`)].map((i) => i.value);
    if (t.name === "ov") setState({ overlays: checked("ov") });
    else if (t.name === "cat") setState({ cats: checked("cat") });
    else if (t.name === "dt") setState({ dts: checked("dt") });
    else if (t.name === "bz") setState({ bz: t.value });
    else if (t.name === "pr") setState({ prmin: Number(t.value) });
  };
  root.oninput = (ev) => {
    if (ev.target.name === "pr") $("#f-pr-out").textContent = Number(ev.target.value).toLocaleString("de-DE");
  };
  root.onclick = (ev) => {
    if (ev.target.id === "f-reset") setState({ cats: [], dts: [], prmin: 0, bz: "", overlays: [] });
    const tv = ev.target.closest("[data-theme-view]");
    if (tv) { const [theme, view] = tv.dataset.themeView.split(":"); setState({ theme, view }); }
  };
}

function renderControls() {
  const focusName = document.activeElement?.name;
  const focusValue = document.activeElement?.value;
  const focusTheme = document.activeElement?.dataset?.theme ?? document.activeElement?.dataset?.view;
  $("#themes").innerHTML = themesHtml();
  $("#controls-body").innerHTML = controlsHtml();
  if (focusTheme) $(`[data-theme="${focusTheme}"], [data-view="${focusTheme}"]`)?.focus();
  else if (focusName) $("#controls-body").querySelector(`[name="${focusName}"][value="${CSS.escape(focusValue ?? "")}"], [name="${focusName}"]`)?.focus();
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
  $("#intro-close").onclick = () => { storage("set", INTRO_KEY, "1"); box.hidden = true; $("#search").focus(); };
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
}

function closePanel() {
  $("#panel").hidden = true;
  document.body.classList.remove("panel-open");
  mapView?.resize();
  lastFocus?.focus?.();
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
  const titles = { bezirke: "Bezirke", methode: "Methode", daten: "Daten", impressum: "Impressum" };
  const chapter = meta.method?.chapters?.find((c) => c.key === state.sub);
  const subTitle = state.page !== "methode" ? null : state.sub === "regeln" ? "Alle Regeln" : chapter?.title;
  document.title = `${meta.site_title}${titles[state.page] ? ` – ${subTitle ? `${titles.methode}: ${subTitle}` : titles[state.page]}` : ""} · ${ORG_NAME}`;
  if (state.page === "karte") {
    renderControls();
    renderIntro();
    if (!mapView) {
      const { createMap } = await import("./map.js");
      mapView = createMap($("#map"), meta, state, {
        onSelect: (id) => setState({ seg: id, jct: null }),
        onSelectJunction: (id) => setState({ jct: id, seg: null }),
        onMove: (m) => { state = { ...state, map: m }; writeUrl(); },
      });
    } else {
      mapView.resize();
    }
    mapView.update(state);
  }
  if (state.page === "bezirke") await renderDistricts();
  if (state.page === "methode") await renderMethod();
  else {
    const pages = { daten: async () => dataHtml(meta), impressum: async () => imprintHtml(meta) };
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

async function init() {
  meta = await json("meta.json");
  const streets = await json("search.json");
  const junctions = meta.overview ? await json("search_junctions.json").catch(() => []) : [];
  for (const s of streets) for (const id of s.ids) idToStreet.set(id, s);
  $("#foot-version").textContent = `Version ${meta.version} · Datenstand ${new Date(meta.data_date).toLocaleDateString("de-DE")}`;
  bindControls();
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
  document.addEventListener("keydown", (ev) => {
    if (ev.key === "Escape" && !$("#panel").hidden) setState({ seg: null, jct: null });
  });
  for (const a of document.querySelectorAll("nav.main a, a.home, .site-foot a[href^='#']")) {
    a.addEventListener("click", (ev) => {
      ev.preventDefault();
      const page = a.getAttribute("href").slice(1);
      setState({ page, sub: null, rule: null, ...(page === "bezirke" ? { table: false } : {}) }, { push: true });
      if (a.dataset.anchor) setTimeout(() => document.getElementById(a.dataset.anchor)?.scrollIntoView(), 100);
      else $("#main").focus();
    });
  }
  window.addEventListener("popstate", () => { state = parseHash(location.hash); render(); });
  window.addEventListener("hashchange", () => { state = parseHash(location.hash); render(); });
  writeUrl();  // rewrite old links (?layer=, #tabelle, #downloads, #quellen) to the new parameters
  await render();
}

init().catch((err) => {
  $("#main").innerHTML = `<p role="alert">Die Daten konnten nicht geladen werden (${esc(err.message)}).</p>`;
});
