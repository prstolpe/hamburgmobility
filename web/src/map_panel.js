// Map panel (prompt 28, variant C on the left, decision 22.11.2026): theme and view with their legend on top, then
// every additional layer as a switch – switched on, its legend unfolds right below it ("Ebenen = Legende"). Below:
// special places, filters, always-on entries and the list of streets in view (keyboard alternative to the map).
// The legend comes from legend_registry.js: only what is switched on, entries without features in view dimmed,
// tap = highlight, "?" = explanation. Chips on the map remove a layer with one tap. Desktop: hover preview on the map.
// Phones: the panel is a bottom sheet with three heights (a grid row under the map, never over it); a tap on the map
// first shows a one-sentence preview in the sheet; the profile replaces the sheet while open.
import { LAYER_INFO, shapeSvg } from "./layers.js";
import { legendFor, MAX_OVERLAYS, overlayGroups, overlayTitle, symbolSvg } from "./legend_registry.js";
import { THEMES, viewsOf } from "./state.js";
import { esc } from "./util.js";

const isPhone = () => matchMedia("(max-width: 760px)").matches;
const canHover = () => matchMedia("(hover: hover) and (pointer: fine)").matches;
const MAX_LIST = 80;
const SHEET_TITLE = { peek: "Legende, Ebenen und Filter", open: "Einklappen" };

// ---- pure HTML (exported for tests) -------------------------------------------------------------

/** ui: {inView: Set|null, highlight: key|null, openWhat: Set, filtersOpen, listOpen, listHtml, preview} */
export function entryHtml(e, ui) {
  const on = ui.highlight === e.key;
  const dim = Boolean(ui.inView && e.layer && !ui.inView.has(e.layer));
  const open = ui.openWhat.has(e.key);
  const id = `what-${e.key.replace(/[^A-Za-z0-9_-]/g, "_")}`;
  const label = `${esc(e.label)}${dim ? '<span class="dimnote"> – nicht im Ausschnitt</span>' : ""}`;
  const main = e.layer
    ? `<button type="button" class="entry-btn" data-hl="${esc(e.layer)}" data-key="${esc(e.key)}" aria-pressed="${on}">${symbolSvg(e.symbol, shapeSvg)}<span>${label}</span></button>`
    : `<span class="entry-btn is-static">${symbolSvg(e.symbol, shapeSvg)}<span>${label}</span></span>`;
  const q = e.explain ? `<button type="button" class="q" data-what="${esc(e.key)}" aria-expanded="${open}" aria-controls="${id}"><span aria-hidden="true">?</span><span class="visually-hidden">Was heißt „${esc(e.label)}“?</span></button>
    <p class="what-text" id="${id}"${open ? "" : " hidden"}>${esc(e.explain)}</p>` : "";
  return `<li class="entry${dim ? " is-dim" : ""}${on ? " is-on" : ""}">${main}${q}</li>`;
}

export function layerLegendHtml(l, ui, { heading = false } = {}) {
  const notes = l.notes.map((n) => `<p class="${n.kind === "note" ? "note" : "muted t-small"}">${esc(n.text)}</p>`).join("");
  const more = l.explain || l.method ? `<details class="more" data-k="more-${esc(l.id)}"${ui.openWhat.has(`more-${l.id}`) ? " open" : ""}>
      <summary>Mehr dazu<span class="visually-hidden">: ${esc(l.title)}</span></summary>${l.explain ? `<p>${esc(l.explain)}</p>` : ""}
      ${l.method ? `<p><a href="${l.method}">So haben wir das ermittelt (Methode)</a></p>` : ""}</details>` : "";
  return `<div class="legend-layer" data-layer="${esc(l.id)}">${heading ? `<h3 class="legend-head">${esc(l.title)}</h3>` : ""}
    ${l.text ? `<p class="legend-text">${esc(l.text)}</p>` : ""}${notes}<ul class="legend">${l.entries.map((e) => entryHtml(e, ui)).join("")}</ul>${more}</div>`;
}

function themeHtml(st) {
  const opts = Object.entries(THEMES).map(([k, t]) =>
    `<button type="button" role="radio" aria-checked="${k === st.theme}" tabindex="${k === st.theme ? 0 : -1}" data-theme="${k}">${esc(t.title)}</button>`).join("");
  const views = viewsOf(st.theme).filter(([, v]) => !v.level);
  const cmp = viewsOf(st.theme).filter(([, v]) => v.level === 3);
  const vs = views.length > 1 ? `<h2 class="panel-h" id="h-view">Ansicht</h2><div class="views" role="radiogroup" aria-labelledby="h-view">${views.map(([k, v]) =>
    `<button type="button" role="radio" aria-checked="${k === st.view}" tabindex="${k === st.view ? 0 : -1}" data-view="${k}">${esc(v.label)}</button>`).join("")}</div>` : "";
  const more = cmp.length ? `<p class="compare t-small">Zum Vergleich: ${cmp.map(([k, v]) =>
    `<button type="button" class="link" data-view="${k}" aria-pressed="${k === st.view}">${esc(v.label)}</button>`).join(" · ")}${
    THEMES[st.theme].views[st.view]?.level ? ` · <button type="button" class="link" data-view="${viewsOf(st.theme)[0][0]}">zurück</button>` : ""}</p>` : "";
  return `<div class="block"><h2 class="panel-h" id="h-theme">Thema</h2><div class="themes" role="radiogroup" aria-labelledby="h-theme">${opts}</div>${vs}${more}</div>`;
}

function layersHtml(st, meta, legend, ui) {
  const byId = Object.fromEntries(legend.map((l) => [l.id, l]));
  const full = st.overlays.filter((o) => !byId[`layer:${o}`]?.legacy).length >= MAX_OVERLAYS;
  const row = (id, name, value, title, text, on, lockable) => `<li class="layer-row${on ? " is-on" : ""}">
    <label class="switch"><input type="checkbox" name="${name}" value="${esc(value)}"${on ? " checked" : ""}${full && !on && lockable ? " disabled" : ""}>
      <span><b>${esc(title)}</b>${on ? "" : `<br><span class="t-small muted">${esc(text)}</span>`}</span></label>
    ${on && byId[id] ? layerLegendHtml(byId[id], ui) : ""}</li>`;
  const groups = overlayGroups().map((g) => `<h3 class="panel-h3">${esc(g.group)}</h3><ul class="layer-rows">${g.items.map((i) =>
    row(`layer:${i.key}`, "ov", i.key, i.title, i.text, st.overlays.includes(i.key), true)).join("")}</ul>`).join("");
  const legacy = legend.filter((l) => l.kind === "overlay" && l.legacy).map((l) => `<div class="legend-legacy">
    <div class="legend-row-head"><h3 class="panel-h3">${esc(l.title)}</h3><button type="button" class="x" data-remove="${esc(l.id)}" aria-label="${esc(l.title)} ausblenden">✕</button></div>
    ${layerLegendHtml(l, ui)}</div>`).join("");
  const sp = meta.special_places;
  const places = (sp?.places ?? []).map((p) => row(`place:${p.id}`, "place", p.id, p.title,
    `${p.kind_plain}, Stand ${new Date(p.status_date).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" })}`, st.place === p.id, false)).join("");
  return `<div class="block" id="panel-layers" tabindex="-1"><h2 class="panel-h">Ebenen dazuschalten</h2>
    ${places ? `<h3 class="panel-h3">${esc(sp.texts.overlay)}</h3><ul class="layer-rows">${places}</ul><p class="t-small"><a href="#orte">Was sind besondere Orte?</a></p>` : ""}${groups}${legacy}
    ${full ? `<p class="t-small muted" role="status">Höchstens ${MAX_OVERLAYS} Ebenen gleichzeitig, damit die Karte lesbar bleibt.</p>` : ""}</div>`;
}

function filtersHtml(st, meta, ui) {
  const n = st.cats.length + st.dts.length + (st.prmin ? 1 : 0) + (st.bz ? 1 : 0);
  const cats = Object.entries(meta.categories).filter(([k]) => !meta.categories_present || meta.categories_present.includes(k)).map(([k, c]) =>
    `<label class="opt"><input type="checkbox" name="cat" value="${k}"${st.cats.includes(k) ? " checked" : ""}> ${esc(c.label)}</label>`).join("");
  // same words as the legend of "Abweichung" (one source per term, inventory finding 6)
  const discLegend = legendFor({ ...st, layer: "disc", overlays: [], place: null }, meta)[0].entries;
  const dtLabel = (k) => discLegend.find((e) => e.key === (k === "keine" ? "none" : k))?.label ?? meta.discrepancy_types[k] ?? k;
  const dts = [...Object.keys(meta.discrepancy_types), "keine"].map((k) =>
    `<label class="opt"><input type="checkbox" name="dt" value="${k}"${st.dts.includes(k) ? " checked" : ""}> ${esc(dtLabel(k))}</label>`).join("");
  return `<details class="block filters" data-k="filters"${ui.filtersOpen ? " open" : ""}><summary>Filter${n ? ` (${n} aktiv)` : ""}</summary>
    <label for="f-bz" class="bz-label">Bezirk</label>
    <select id="f-bz" name="bz"><option value="">ganz Hamburg</option>${meta.districts.map((b) => `<option value="${esc(b)}"${st.bz === b ? " selected" : ""}>${esc(b)}</option>`).join("")}</select>
    ${LAYER_INFO[st.layer]?.cycling ? '<p class="muted t-small">Bei den Radverkehrs-Ansichten gilt nur der Bezirk.</p>' : ""}
    <fieldset><legend>Aufgabe der Straße</legend>${cats}</fieldset>
    <fieldset><legend>Art der Abweichung</legend>${dts}</fieldset>
    <label for="f-pr">Dringlichkeit mindestens: <output id="f-pr-out">${st.prmin.toLocaleString("de-DE")}</output></label>
    <input id="f-pr" name="pr" type="range" min="0" max="3" step="0.25" value="${st.prmin}">
    ${n ? '<button type="button" id="f-reset" class="secondary">Filter zurücksetzen</button>' : ""}</details>`;
}

export function chipsHtml(st, meta) {
  const chips = [];
  for (const k of st.overlays) chips.push([`layer:${k}`, overlayTitle(k)]);
  if (st.place) chips.push([`place:${st.place}`, meta.special_places?.places?.find((p) => p.id === st.place)?.title ?? st.place]);
  if (st.bz) chips.push(["bz", `Bezirk ${st.bz}`]);
  if (st.cats.length || st.dts.length || st.prmin) chips.push(["filter", "Filter"]);
  const t = THEMES[st.theme];
  const view = viewsOf(st.theme).length > 1 ? ` · ${t.views[st.view]?.label}` : "";
  return `<span class="chip chip-view">${esc(t.title)}${esc(view)}</span>${chips.map(([id, label]) =>
    `<button type="button" class="chip" data-remove="${esc(id)}" aria-label="${esc(label)} ausblenden">${esc(label)} <span aria-hidden="true">✕</span></button>`).join("")}`;
}

/** Whole panel body for a state. */
export function panelHtml(st, meta, ui) {
  if (ui.preview) return previewHtml(ui.preview);
  const legend = legendFor(st, meta);
  const view = legend[0];
  const base = legend.find((l) => l.kind === "base");
  return `<p class="skip-links"><a href="#panel-layers" data-skip="panel-layers">Zu den Ebenen</a> <a href="#list-btn" data-skip="list-btn">Zur Liste der Straßen im Ausschnitt</a></p>
    ${themeHtml(st)}
    <div class="block"><h2 class="panel-h">Was die Farben bedeuten</h2>${layerLegendHtml(view, ui, { heading: true })}
      <p class="hint t-small">Eintrag antippen: nur diese Linien hervorheben. „?“: Was heißt das? Grau: gerade nicht im Kartenausschnitt.</p></div>
    ${layersHtml(st, meta, legend, ui)}
    ${filtersHtml(st, meta, ui)}
    ${base ? `<div class="block">${layerLegendHtml(base, ui, { heading: true })}</div>` : ""}
    <div class="block"><button type="button" class="secondary list-btn" id="list-btn" aria-expanded="${ui.listOpen}" aria-controls="feature-list">Straßen im Kartenausschnitt als Liste</button>
      <div id="feature-list"${ui.listOpen ? "" : " hidden"}>${ui.listOpen ? ui.listHtml : ""}</div></div>`;
}

function previewHtml(p) {
  return `<div class="block preview"><p class="preview-title">${esc(p.title)}</p>${p.text ? `<p>${esc(p.text)}</p>` : ""}
    <div class="btn-row"><button type="button" id="preview-open">Steckbrief öffnen</button>
    <button type="button" class="secondary" id="preview-copy">Link kopieren</button>
    <button type="button" class="secondary" id="preview-close">Zurück zur Legende</button></div>
    <p class="t-small muted" id="preview-status" role="status"></p></div>`;
}

/** One sentence for a rendered feature (hover and tap preview). */
export function featureSentence(f, meta, junctionNames) {
  const p = f.properties;
  if (f.sourceLayer === "junctions") {
    const n = junctionNames.get(String(p.id));
    const grp = meta.cycling?.junction_group?.[p.grp];
    return { kind: "jct", id: String(p.id), title: n ? `Kreuzung ${n}` : "Kreuzung",
      text: `${grp ? `Ziel: ${grp}.` : ""}${Number(p.act) === 1 ? " Umbau nötig." : ""}`.trim() };
  }
  if (f.source === "places") return { kind: "seg", id: p.id, title: p.name ?? "Besonderer Ort", text: p.label ?? "" };
  const id = p.seg ?? p.id;
  const cat = meta.categories[p.cat]?.label;
  const spd = p.spd ? `heute Tempo ${p.spd}` : "Tempo heute unbekannt";
  return { kind: "seg", id, title: p.name ?? "Straße ohne Namen", text: cat ? `Ziel: ${cat}, ${spd}.` : "" };
}

// ---- DOM -----------------------------------------------------------------------------------------

export function createMapPanel({ root, chipsRoot, tipRoot, meta, getState, setState, getMap, showPlace, junctionNames, shareUrl }) {
  const ui = { inView: null, highlight: null, highlightLayer: null, openWhat: new Set(), filtersOpen: false, listOpen: false, listHtml: "", preview: null };
  // phones: the whole bar opens and closes the sheet (tap again = close); a small button switches half / full height
  root.innerHTML = `<div class="sheet-bar"><button type="button" class="sheet-handle" id="sheet-handle" aria-expanded="false" aria-controls="map-panel-body">
      <span class="grip" aria-hidden="true"></span><span class="sheet-label"><svg class="chev" viewBox="0 0 12 8" width="12" height="8" aria-hidden="true"><path d="M1 7l5-5 5 5" fill="none" stroke="currentColor" stroke-width="2"/></svg><span id="sheet-title">${SHEET_TITLE.peek}</span></span></button>
    <button type="button" class="sheet-size" id="sheet-size" aria-controls="map-panel-body">Größer</button></div>
    <div class="map-panel-body" id="map-panel-body"></div>`;
  root.dataset.size = "peek";
  const body = root.querySelector("#map-panel-body");

  function render() {
    const st = getState();
    const active = document.activeElement;
    const chipFocus = active && chipsRoot.contains(active) ? active.dataset.remove : null;
    chipsRoot.innerHTML = chipsHtml(st, meta);
    if (chipFocus) chipsRoot.querySelector(`[data-remove="${CSS.escape(chipFocus)}"]`)?.focus({ preventScroll: true });
    const focus = active && root.contains(active) ? focusKey(active) : null;
    const scroll = body.scrollTop;
    if (ui.listOpen) ui.listHtml = featureListHtml();
    body.innerHTML = panelHtml(st, meta, ui);
    body.scrollTop = scroll;
    sheetTitle();
    if (focus) restoreFocus(focus);
    applyHighlight();
  }

  const FOCUS_ATTRS = ["data-theme", "data-view", "data-key", "data-what", "data-remove", "data-open", "id"];
  function focusKey(el) {
    const a = FOCUS_ATTRS.find((x) => el.getAttribute(x));
    if (a) return [a, el.getAttribute(a)];
    return el.name ? ["name", el.name, el.value] : el.tagName === "SUMMARY" ? ["summary", el.parentElement.dataset.k] : null;
  }
  function restoreFocus([attr, v, value]) {
    let el;
    if (attr === "name") el = body.querySelector(`[name="${v}"][value="${CSS.escape(value)}"]`) ?? body.querySelector(`[name="${v}"]`);
    else if (attr === "summary") el = body.querySelector(`details[data-k="${CSS.escape(v)}"] > summary`);
    else el = root.querySelector(`[${attr}="${CSS.escape(v)}"]`);
    el?.focus({ preventScroll: true });
  }

  // ---- map coupling: highlight, in view, hover, tap ----------------------------------------------

  const OPACITY = { line: ["line-opacity"], circle: ["circle-opacity", "circle-stroke-opacity"], symbol: ["icon-opacity"], fill: ["fill-opacity"] };
  const original = new Map(); // layer|prop -> paint value before dimming
  let dimmedLayer = null; // highlight currently applied to the map (null = map untouched)
  /** Dim all lines but the highlighted entry. Touches the map only when the highlight changes (each paint change
   * redraws the map; prompt 28 performance check). */
  function applyHighlight(force = false) {
    const map = getMap();
    if (!map?.isStyleLoaded() || (!force && dimmedLayer === ui.highlightLayer)) return;
    const layers = map.getStyle().layers.filter((x) => /^(main-|ref-|ov-|casing|place-casing|gaps-)/.test(x.id));
    for (const l of layers) for (const prop of OPACITY[l.type] ?? []) {
      const k = `${l.id}|${prop}`;
      if (ui.highlightLayer && !original.has(k)) original.set(k, map.getPaintProperty(l.id, prop));
      const keep = !ui.highlightLayer || l.id === ui.highlightLayer || l.id === `${ui.highlightLayer}-inner`;
      const value = keep ? (original.has(k) ? original.get(k) : map.getPaintProperty(l.id, prop)) : l.id.startsWith("casing") ? 0.3 : 0.12;
      if (map.getPaintProperty(l.id, prop) !== value) map.setPaintProperty(l.id, prop, value);
    }
    dimmedLayer = ui.highlightLayer;
    if (!ui.highlightLayer) original.clear();
  }

  let idleTimer = 0;
  function updateInView() {
    const map = getMap();
    if (!map?.isStyleLoaded()) return;
    const want = legendFor(getState(), meta).flatMap((l) => l.entries.map((e) => e.layer)).filter((id) => id && map.getLayer(id));
    const found = new Set(map.queryRenderedFeatures({ layers: want }).map((f) => f.layer.id));
    const changed = !ui.inView || found.size !== ui.inView.size || [...found].some((x) => !ui.inView.has(x));
    ui.inView = found;
    if (changed || ui.listOpen) render();
  }

  function featureAt(point) {
    const map = getMap();
    const ids = map.getStyle().layers.map((l) => l.id).filter((id) => id.startsWith("main-") || id.startsWith("casing"));
    return map.queryRenderedFeatures([[point.x - 6, point.y - 6], [point.x + 6, point.y + 6]], { layers: ids })
      .find((f) => f.sourceLayer !== "cycle_official") ?? null;
  }

  function featureListHtml() {
    const map = getMap();
    if (!map?.isStyleLoaded()) return "";
    const ids = map.getStyle().layers.map((l) => l.id).filter((id) => id.startsWith("main-") && id !== "main-jctdot");
    const byName = new Map();
    for (const f of map.queryRenderedFeatures({ layers: ids })) {
      const p = f.properties;
      if (f.sourceLayer === "junctions") {
        const n = junctionNames.get(String(p.id));
        if (n && !byName.has(`Kreuzung ${n}`)) byName.set(`Kreuzung ${n}`, { kind: "jct", id: String(p.id), sub: "" });
        continue;
      }
      const id = p.seg ?? p.id;
      if (p.name && /^seg_/.test(id ?? "") && !byName.has(p.name)) byName.set(p.name, { kind: "seg", id, sub: meta.categories[p.cat]?.label ?? "" });
    }
    const items = [...byName].sort(([a], [b]) => a.localeCompare(b, "de")).slice(0, MAX_LIST);
    if (!items.length) return '<p class="muted">Hier sind keine benannten Straßen zu sehen. Hineinzoomen oder die Karte verschieben.</p>';
    return `<p class="t-small muted">${items.length}${items.length === MAX_LIST ? " (die ersten)" : ""} Einträge, alphabetisch. Enter öffnet den Steckbrief.</p>
      <ul class="feature-list">${items.map(([name, i]) => `<li><button type="button" class="link" data-open="${i.kind}:${esc(i.id)}">${esc(name)}</button>${i.sub ? ` <span class="t-small muted">${esc(i.sub)}</span>` : ""}</li>`).join("")}</ul>`;
  }

  let bound = false;
  function bindMap() {
    const map = getMap();
    if (!map || bound) return;
    bound = true;
    map.on("idle", () => { clearTimeout(idleTimer); idleTimer = setTimeout(updateInView, 150); });
    // layers are rebuilt on every theme/view/filter change: re-apply a running highlight to the new layers
    map.on("styledata", () => { if (ui.highlightLayer) { original.clear(); applyHighlight(true); } else dimmedLayer = null; });
    let raf = 0;
    map.on("mousemove", (ev) => {
      if (!canHover()) return;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const f = featureAt(ev.point);
        if (!f) { tipRoot.hidden = true; return; }
        const s = featureSentence(f, meta, junctionNames);
        tipRoot.innerHTML = `<b>${esc(s.title)}</b>${s.text ? `<br>${esc(s.text)}` : ""}<br><span class="t-small muted">Klicken öffnet den Steckbrief</span>`;
        tipRoot.hidden = false;
        const c = map.getContainer(); // tooltip and map share the positioned .map-page
        tipRoot.style.left = `${Math.min(c.offsetLeft + ev.point.x + 14, c.offsetLeft + c.offsetWidth - 300)}px`;
        tipRoot.style.top = `${c.offsetTop + ev.point.y + 14}px`;
      });
    });
    map.on("mouseout", () => { tipRoot.hidden = true; });
    map.on("movestart", () => { tipRoot.hidden = true; });
    map.getContainer().addEventListener("pointerup", (ev) => {
      const r = map.getContainer().getBoundingClientRect();
      lastTap = { x: ev.clientX - r.left, y: ev.clientY - r.top };
    }, true);
  }
  let lastTap = null;

  /** Map tap on a phone: one-sentence preview in the sheet first. Returns true when handled. */
  function onFeature(kind, id) {
    if (!isPhone() || document.body.classList.contains("panel-open")) return false; // profile open: select directly
    const map = getMap();
    const f = map && lastTap ? featureAt(lastTap) : null;
    const s = f ? featureSentence(f, meta, junctionNames) : null;
    ui.preview = { kind, id, title: s?.title ?? (kind === "jct" ? "Kreuzung" : "Straße"), text: s?.text ?? "" };
    setSize("half");
    render();
    body.querySelector("#preview-open")?.focus({ preventScroll: true });
    return true;
  }

  // ---- sheet (phones) --------------------------------------------------------------------------------

  function sheetTitle() {
    const open = root.dataset.size !== "peek";
    root.querySelector("#sheet-title").textContent = open ? SHEET_TITLE.open : ui.preview ? "Vorschau" : SHEET_TITLE.peek;
    root.querySelector("#sheet-size").textContent = root.dataset.size === "full" ? "Kleiner" : "Größer";
  }
  function setSize(size) {
    root.dataset.size = size;
    root.querySelector("#sheet-handle").setAttribute("aria-expanded", String(size !== "peek"));
    sheetTitle();
    requestAnimationFrame(() => getMap()?.resize()); // the map row shrinks or grows with the sheet
  }
  root.querySelector("#sheet-handle").onclick = () => setSize(root.dataset.size === "peek" ? "half" : "peek");
  root.querySelector("#sheet-size").onclick = () => setSize(root.dataset.size === "full" ? "half" : "full");

  // ---- events ----------------------------------------------------------------------------------------

  function removeLayer(id) {
    const st = getState();
    if (id.startsWith("layer:")) setState({ overlays: st.overlays.filter((o) => o !== id.slice(6)) });
    else if (id.startsWith("place:")) showPlace(null);
    else if (id === "bz") setState({ bz: "" });
    else if (id === "filter") setState({ cats: [], dts: [], prmin: 0 });
    // focus: the switch of the removed layer, else the next chip, else the checked theme
    const sw = id.startsWith("layer:") ? root.querySelector(`input[name="ov"][value="${CSS.escape(id.slice(6))}"]`)
      : id.startsWith("place:") ? root.querySelector('input[name="place"]') : null;
    (sw ?? chipsRoot.querySelector("button.chip") ?? root.querySelector("[data-theme][aria-checked='true']"))?.focus({ preventScroll: true });
  }
  const select = (kind, id) => setState(kind === "jct" ? { jct: id, seg: null } : { seg: id, jct: null }, { push: true });

  function onClick(ev) {
    const t = ev.target;
    const at = (sel) => t.closest(sel);
    if (at("[data-theme]")) { ui.highlight = ui.highlightLayer = null; setState({ theme: at("[data-theme]").dataset.theme, view: null }); }
    else if (at("[data-view]")) { ui.highlight = ui.highlightLayer = null; setState({ view: at("[data-view]").dataset.view }); }
    else if (at("[data-what]")) { const k = at("[data-what]").dataset.what; if (!ui.openWhat.delete(k)) ui.openWhat.add(k); render(); }
    else if (at("[data-hl]")) {
      const b = at("[data-hl]");
      const off = ui.highlight === b.dataset.key;
      ui.highlight = off ? null : b.dataset.key;
      ui.highlightLayer = off ? null : b.dataset.hl;
      render();
    } else if (at("[data-remove]")) removeLayer(at("[data-remove]").dataset.remove);
    else if (at("[data-open]")) { const [kind, id] = at("[data-open]").dataset.open.split(":"); select(kind, id); }
    else if (at("[data-skip]")) { ev.preventDefault(); root.querySelector(`#${at("[data-skip]").dataset.skip}`)?.focus(); }
    else if (t.id === "list-btn") { ui.listOpen = !ui.listOpen; render(); }
    else if (t.id === "f-reset") setState({ cats: [], dts: [], prmin: 0, bz: "" });
    else if (t.id === "preview-open") { const p = ui.preview; ui.preview = null; setSize("peek"); select(p.kind, p.id); }
    else if (t.id === "preview-close") { ui.preview = null; render(); }
    else if (t.id === "preview-copy") copyLink(shareUrl(ui.preview), body.querySelector("#preview-status"));
  }
  root.addEventListener("click", onClick);
  chipsRoot.addEventListener("click", onClick);
  root.addEventListener("toggle", (ev) => {
    const d = ev.target;
    if (d.dataset?.k === "filters") ui.filtersOpen = d.open;
    else if (d.dataset?.k) { if (d.open) ui.openWhat.add(d.dataset.k); else ui.openWhat.delete(d.dataset.k); }
  }, true);
  root.addEventListener("change", (ev) => {
    const t = ev.target;
    const st = getState();
    const checked = (name) => [...root.querySelectorAll(`input[name="${name}"]:checked`)].map((i) => i.value);
    if (t.name === "ov") setState({ overlays: t.checked ? [...st.overlays, t.value] : st.overlays.filter((o) => o !== t.value) });
    else if (t.name === "place") showPlace(t.checked ? t.value : null);
    else if (t.name === "cat") setState({ cats: checked("cat") });
    else if (t.name === "dt") setState({ dts: checked("dt") });
    else if (t.name === "bz") setState({ bz: t.value });
    else if (t.name === "pr") setState({ prmin: Number(t.value) });
  });
  root.addEventListener("input", (ev) => {
    if (ev.target.name === "pr") root.querySelector("#f-pr-out").textContent = Number(ev.target.value).toLocaleString("de-DE");
  });
  // radio groups: arrow keys move the choice (WAI-ARIA radio group)
  root.addEventListener("keydown", (ev) => {
    const r = ev.target.closest('[role="radio"]');
    if (!r || !["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp"].includes(ev.key)) return;
    const all = [...r.parentElement.querySelectorAll('[role="radio"]')];
    const next = all[(all.indexOf(r) + (ev.key === "ArrowRight" || ev.key === "ArrowDown" ? 1 : all.length - 1)) % all.length];
    ev.preventDefault();
    next.focus();
    next.click();
  });

  /** Esc: closes the innermost thing that is open. Returns true when it handled the key. */
  function onEscape() {
    if (!tipRoot.hidden) { tipRoot.hidden = true; return true; }
    if (ui.preview) { ui.preview = null; setSize("peek"); render(); return true; }
    if (ui.highlight) { ui.highlight = ui.highlightLayer = null; render(); return true; }
    if (root.dataset.size === "full") { setSize("half"); return true; }
    return false;
  }

  return { render: () => { bindMap(); render(); }, onFeature, onEscape };
}

/** Copy a link; shows the link itself if the clipboard is not available. */
export function copyLink(url, status) {
  const done = (msg) => { if (status) status.textContent = msg; };
  if (navigator.clipboard?.writeText) navigator.clipboard.writeText(url).then(() => done("Link kopiert."), () => done(url));
  else done(url);
}
