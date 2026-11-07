// Prototype C – guided start: three short steps (idea, street types, district), a district overview with figures
// and top lists, then the map. Figures from prototypes/shared/kpi.json (district_kpi.py), all seven Bezirke for comparison.
import { BZ, fmt, junction, loadAll, profile } from "../shared/data.js";
import { createMap, legendHtml, SOLL_SPEED } from "../shared/map.js";
import { junctionBriefHtml, steckbriefHtml } from "../shared/steckbrief.js";
import { CATEGORY_STYLE } from "../../web/src/palette.js";

const $ = (s) => document.querySelector(s);
const { meta, kpi, scenario } = await loadAll();
const CATS = ["SW", "GOW50", "GOW30", "ETW30", "ETW_ERF"];
const STEPS = ["Worum geht es?", "Fünf Straßentypen", "Ihr Bezirk"];
let step = Number(location.hash.match(/schritt(\d)/)?.[1] ?? 1);
let mv = null;
let mapView = "need";

const stepsNav = () => `<ol class="g-steps">${STEPS.map((s, i) => `<li ${i + 1 === step ? 'aria-current="step"' : ""}>${i + 1}. ${s}</li>`).join("")}</ol>`;
const nav = (next) => `<div class="g-nav">${step > 1 ? '<button class="btn secondary" data-step="back">Zurück</button>' : ""}
  ${next ? `<button class="btn" data-step="next">${next}</button>` : ""}<button class="btn link" data-go="map">Direkt zur Karte</button></div>`;

function lineSvg(s) {
  const dash = s.dash ? `stroke-dasharray="${s.dash.map((d) => d * 4).join(" ")}"` : "";
  return `<svg aria-hidden="true" width="40" height="14"><line x1="2" y1="7" x2="38" y2="7" stroke="#fff" stroke-width="${Math.min(s.width, 6) + 4}" stroke-linecap="round"/><line x1="2" y1="7" x2="38" y2="7" stroke="${s.color}" stroke-width="${Math.min(s.width, 6)}" ${dash}/></svg>`;
}

function step1() {
  return `${stepsNav()}
  <h1>Welche Aufgabe hat Ihre Straße?</h1>
  <p class="lead">Dieser Entwurf ordnet jeder Straße in Hamburg eine Aufgabe zu und zeigt, wo die Straße heute nicht dazu passt. Die Idee stammt aus den Niederlanden („Duurzaam Veilig“, nachhaltig sicher).</p>
  <div class="g-cards">
    <div class="g-card"><span class="n">1</span><b>Aufgabe</b>Soll die Straße Stadtteile verbinden oder ein Quartier erschließen?</div>
    <div class="g-card"><span class="n">2</span><b>Gestaltung</b>Daraus folgen Tempo, Radweg, Gehweg und Kreuzungen.</div>
    <div class="g-card"><span class="n">3</span><b>Heute</b>Wo Tempo, Gestaltung oder Verkehr nicht passen, besteht Handlungsbedarf.</div>
  </div>
  <p class="note"><strong>Entwurf:</strong> ${meta.disclaimer}. Ein Programm macht den ersten Vorschlag, Menschen prüfen ihn.</p>
  ${nav("Weiter: die fünf Straßentypen")}`;
}

function step2() {
  const cats = CATS.map((k) => `<li>${lineSvg(CATEGORY_STYLE[k])}<span><strong>${meta.categories[k].label}</strong> – ${meta.categories[k].text.split(" – ")[1]}. <span class="muted">${SOLL_SPEED[k]}.</span></span></li>`).join("");
  return `${stepsNav()}
  <h1>Fünf Straßentypen</h1>
  <p>Auf der Karte hat jeder Typ eine eigene Farbe und Linienform – so bleiben sie auch ohne Farbsehen unterscheidbar.</p>
  <ul class="g-types">${cats}</ul>
  ${nav("Weiter: Ihr Bezirk")}`;
}

function overview(bz) {
  const K = kpi.per_bezirk[bz];
  const tot = CATS.reduce((a, k) => a + K.km_by_cat[k], 0);
  const t30 = K.km_by_cat.GOW30 + K.km_by_cat.ETW30 + K.km_by_cat.ETW_ERF;
  const stack = CATS.map((k) => `<div style="width:${(100 * K.km_by_cat[k]) / tot}%;background:${CATEGORY_STYLE[k].color}" title="${meta.categories[k].label}: ${fmt(K.km_by_cat[k])} km"></div>`).join("");
  const stackLabels = CATS.map((k) => `<li><i style="background:${CATEGORY_STYLE[k].color}"></i>${meta.categories[k].label} ${fmt(K.km_by_cat[k])} km (${fmt((100 * K.km_by_cat[k]) / tot)} %)</li>`).join("");
  // comparison of the seven Bezirke: one measure per column, values normalised so Bezirke of different size compare
  const rows = Object.entries(kpi.per_bezirk).map(([name, k]) => ({ name,
    fast: (100 * k.km_speed_too_high) / k.km_total,
    miss: (100 * k.km_cycle_facility_missing) / Math.max(1, k.km_cycle_network.RSV + k.km_cycle_network.HAUPT + k.km_cycle_network.BASIS),
    jct: (100 * k.junctions_rebuild) / Math.max(1, k.junctions) }));
  const max = { fast: Math.max(...rows.map((r) => r.fast)), miss: Math.max(...rows.map((r) => r.miss)), jct: Math.max(...rows.map((r) => r.jct)) };
  const cell = (r, key) => `<td class="num">${fmt(r[key])} %</td><td style="width:16%"><div class="bar" style="width:${(100 * r[key]) / max[key]}%"></div></td>`;
  return `
  <h2>Bezirk ${bz}</h2>
  <div class="g-kpis">
    <div class="g-kpi"><b>${fmt((100 * t30) / tot)} %</b><span>der Straßen sollen Tempo 30 oder weniger haben</span></div>
    <div class="g-kpi"><b>${fmt(K.km_speed_too_high)} km</b><span>sind heute schneller als im Soll</span></div>
    <div class="g-kpi"><b>${fmt(K.km_cycle_facility_missing)} km</b><span>Radrouten ohne passende Radanlage</span></div>
    <div class="g-kpi"><b>${fmt(K.junctions_rebuild)}</b><span>Kreuzungen brauchen einen Umbau (von ${fmt(K.junctions)})</span></div>
    <div class="g-kpi"><b>${fmt(K.mesh_gaps)}</b><span>Lücken im Radnetz</span></div>
    <div class="g-kpi"><b>${fmt(K.km_uncertain)} km</b><span>unsicher eingestuft – fachlich prüfen</span></div>
  </div>
  <h3>So verteilen sich die ${fmt(tot)} km Straßen</h3>
  <div class="g-stack" role="img" aria-label="Anteile der Straßentypen, Werte in der Liste darunter">${stack}</div>
  <ul class="g-stack-labels">${stackLabels}</ul>
  <div class="g-two">
    <div><h3>Die dringendsten Straßen</h3><ol class="g-list">${kpi.top_streets.slice(0, 5).map((s) => `<li><button data-seg="${s.seg}" data-bbox="${s.bbox}">${s.name}</button> <span class="muted">· ${meta.categories[s.cat].label}, ${fmt(s.crashes)} Unfälle Fuß/Rad</span></li>`).join("")}</ol></div>
    <div><h3>Kreuzungen mit größtem Umbaubedarf</h3><ol class="g-list">${kpi.top_junctions.slice(0, 5).map((j) => `<li><button data-jct="${j.id}" data-ll="${j.lon},${j.lat}">${j.names}</button></li>`).join("")}</ol></div>
  </div>
  <h3>Im Vergleich der Bezirke</h3>
  <div class="table-wrap" style="overflow:auto;position:relative"><table>
    <caption class="muted" style="text-align:left">Anteile in Prozent; Straßen und Radrouten nach Länge, Kreuzungen nach Anzahl</caption>
    <thead><tr><th scope="col">Bezirk</th><th scope="col" colspan="2">Straßen heute zu schnell</th><th scope="col" colspan="2">Radrouten ohne passende Radanlage</th><th scope="col" colspan="2">Kreuzungen mit Umbaubedarf</th></tr></thead>
    <tbody>${rows.map((r) => `<tr class="${r.name === bz ? "focus" : ""}"><th scope="row">${r.name}</th>${cell(r, "fast")}${cell(r, "miss")}${cell(r, "jct")}</tr>`).join("")}</tbody>
  </table></div>
  <p class="muted">Quelle: Export ${meta.version}. Zahlen aus dem Entwurf, nicht amtlich.</p>`;
}

function step3() {
  return `${stepsNav()}
  <h1>Ihr Bezirk</h1>
  <div class="g-bz" role="group" aria-label="Bezirk">${meta.districts.map((b) => `<button class="btn ${b === BZ ? "" : "secondary"}" ${b === BZ ? 'aria-pressed="true"' : 'disabled title="im Prototyp nur Eimsbüttel"'}>${b}</button>`).join("")}</div>
  <p class="muted">Im Prototyp ist nur Eimsbüttel auswählbar.</p>
  ${overview(BZ)}
  <div class="g-nav"><button class="btn secondary" data-step="back">Zurück</button><button class="btn" data-go="map">Karte von ${BZ} öffnen</button></div>`;
}

const MAPVIEWS = [["need", "Handlungsbedarf"], ["cat", "Aufgabe der Straßen"], ["cnet", "Radnetz"], ["jct", "Kreuzungen"]];
function showMap(open) {
  $("#page").hidden = true;
  $("#mapview").classList.add("on");
  if (!mv) mv = createMap($("#map"), { meta, kpi, bz: BZ, scenario, onSelect: (id) => openSeg(id), onSelectJunction: (id) => openJct(id) });
  $("#mapbar").innerHTML = `<button data-go="overview">← Bezirksübersicht</button>${MAPVIEWS.map(([k, l]) => `<button aria-pressed="${k === mapView}" data-mapview="${k}">${l}</button>`).join("")}`;
  mv.show(mapView, { gaps: mapView === "cnet" });
  $("#legend").innerHTML = legendHtml(mapView, meta, { gaps: mapView === "cnet" });
  if (mapView === "jct" && mv.map.getZoom() < 13) mv.map.easeTo({ zoom: 14, center: [9.965, 53.575] });
  mv.map.resize();
  open?.();
  history.replaceState(null, "", "#karte");
}

async function openSeg(id) {
  $("#sheet").hidden = false;
  $("#sheet-body").innerHTML = steckbriefHtml(await profile(id), meta);
  $("#sheet").focus();
}
async function openJct(id) {
  $("#sheet").hidden = false;
  $("#sheet-body").innerHTML = junctionBriefHtml(await junction(id), meta);
}

function render() {
  $("#page").hidden = false;
  $("#mapview").classList.remove("on");
  $("#wrap").innerHTML = [step1, step2, step3][step - 1]();
  history.replaceState(null, "", `#schritt${step}`);
  $("#page").scrollTop = 0;
}

document.addEventListener("click", (ev) => {
  const b = ev.target.closest("button");
  if (!b) return;
  if (b.dataset.step === "next") { step = Math.min(3, step + 1); render(); }
  else if (b.dataset.step === "back") { step = Math.max(1, step - 1); render(); }
  else if (b.dataset.go === "map") showMap();
  else if (b.dataset.go === "overview") { step = 3; render(); }
  else if (b.dataset.mapview) { mapView = b.dataset.mapview; showMap(); }
  else if (b.dataset.seg) { mapView = "need"; showMap(() => { mv.fit(b.dataset.bbox.split(",").map(Number)); openSeg(b.dataset.seg); }); }
  else if (b.dataset.jct) { mapView = "jct"; showMap(() => { const [lo, la] = b.dataset.ll.split(",").map(Number); mv.flyTo(lo, la, 17); openJct(b.dataset.jct); }); }
  else if (b.id === "close") $("#sheet").hidden = true;
});
document.addEventListener("keydown", (ev) => { if (ev.key === "Escape") $("#sheet").hidden = true; });
if (location.hash === "#karte") showMap(); else render();

// test hook for the screenshot script (analysis/review_2026_11/ui/prototypes.mjs)
window.proto = { openSeg, openJct, get map() { return mv?.map; } };
