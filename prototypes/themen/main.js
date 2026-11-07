// Prototype A – "Themen statt Ebenen": five entry points, each with prepared views, a two-sentence explanation,
// a plain-language legend and a few district figures. State in the URL hash (#thema/ansicht).
import { BZ, fmt, junction, loadAll, profile } from "../shared/data.js";
import { createMap, legendHtml } from "../shared/map.js";
import { junctionBriefHtml, steckbriefHtml } from "../shared/steckbrief.js";

const $ = (s) => document.querySelector(s);
const { meta, kpi, scenario } = await loadAll();
const K = kpi.per_bezirk[BZ];
const pct = (a, b) => `${fmt((100 * a) / b)} %`;
const t30 = K.km_by_cat.GOW30 + K.km_by_cat.ETW30 + K.km_by_cat.ETW_ERF;

const THEMES = {
  funktion: {
    tab: "Straßenfunktion", title: "Welche Aufgabe hat die Straße?",
    lead: "Jede Straße soll entweder Verkehr verbinden oder ein Quartier erschließen. Daraus folgen Tempo und Gestaltung – so wie in den Niederlanden („Duurzaam Veilig“).",
    views: [["cat", "Aufgabe (Soll)"], ["speed", "Tempo heute"], ["soll_speed", "Tempo Soll"]],
    kpis: [[`${pct(t30, K.km_total)}`, "der Straßen sollen Tempo 30 oder weniger haben"], [`${fmt(K.km_speed_too_high)} km`, "heute schneller als im Soll"]],
  },
  radnetz: {
    tab: "Radnetz", title: "Wie sieht das Radnetz aus – und wo fehlt etwas?",
    lead: "Der Entwurf schlägt ein Radnetz in Ebenen vor. Orange Flächen sind Netzlücken: Dort sind die Maschen größer als vorgesehen.",
    views: [["cnet", "Netz und Lücken"], ["cgap", "Radwege heute vs. Soll"]],
    kpis: [[`${fmt(K.km_cycle_network.HAUPT + K.km_cycle_network.RSV)} km`, "Radrouten im Entwurf"], [`${fmt(K.km_cycle_facility_missing)} km`, "davon ohne passende Radanlage"], [`${fmt(K.mesh_gaps)}`, "Netzlücken"]],
  },
  bedarf: {
    tab: "Handlungsbedarf", title: "Wo ist der Handlungsbedarf am größten?",
    lead: "Dringend heißt: Die Straße weicht stark vom Soll ab, und es gibt ein hohes Risiko (Unfälle, Radnetz, Schulen, Einwohner).",
    views: [["need", "Straßen nach Dringlichkeit"]],
    kpis: [[`${fmt(K.km_disc_strong)} km`, "weichen deutlich vom Soll ab"], [`${fmt(K.junctions_rebuild)}`, "Kreuzungen mit Umbaubedarf"]],
    list: "bedarf",
  },
  knoten: {
    tab: "Kreuzungen", title: "Was wird aus den Kreuzungen?",
    lead: "Form und Farbe zeigen den vorgeschlagenen Kreuzungstyp; große Zeichen bedeuten: Umbau nötig. Tippen Sie auf ein Zeichen.",
    views: [["jct", "Vorgeschlagener Typ"]], zoom: 14,
    kpis: [[`${fmt(K.junctions)}`, "Kreuzungen bewertet"], [`${fmt(K.junctions_rebuild)}`, "brauchen einen Umbau"]],
    list: "knoten",
  },
  qualitaet: {
    tab: "Datenqualität", title: "Wie sicher ist der Entwurf?",
    lead: "Orange: Die Einstufung kippt, wenn man Annahmen verändert – hier sollte fachlich geprüft werden. Rot gepunktet: Ein entscheidender Wert fehlt.",
    views: [["conf", "Sicherheit der Einstufung"]],
    kpis: [[`${fmt(K.km_uncertain)} km`, "unsicher"], [`${fmt(K.km_low_confidence)} km`, "mit lückenhafter Datenlage"]],
  },
};

let [theme, view] = location.hash.slice(1).split("/");
if (!THEMES[theme]) theme = "funktion";
if (!THEMES[theme].views.some(([v]) => v === view)) view = THEMES[theme].views[0][0];

const mv = createMap($("#map"), { meta, kpi, bz: BZ, scenario, onSelect: (id) => openSeg(id), onSelectJunction: (id) => openJct(id) });

function listHtml(kind) {
  if (kind === "bedarf") {
    return `<h2 class="t-hint">Die dringendsten Straßen</h2><ol class="t-list">${kpi.top_streets.slice(0, 8).map((s, i) => `<li><button data-seg="${s.seg}" data-bbox="${s.bbox}">
      ${i + 1}. ${s.name} <small>· ${meta.categories[s.cat].label} · ${fmt(s.crashes)} Unfälle Fuß/Rad</small></button></li>`).join("")}</ol>`;
  }
  return `<h2 class="t-hint">Kreuzungen mit dem größten Umbaubedarf</h2><ol class="t-list">${kpi.top_junctions.slice(0, 8).map((j) => `<li><button data-jct="${j.id}" data-ll="${j.lon},${j.lat}">
    ${j.names} <small>· ${fmt(j.crashes_cyc)} Radunfälle</small></button></li>`).join("")}</ol>`;
}

function render() {
  const t = THEMES[theme];
  $("#tabs").innerHTML = Object.entries(THEMES).map(([k, v]) => `<button role="tab" aria-selected="${k === theme}" data-theme="${k}">${v.tab}</button>`).join("");
  $("#side").innerHTML = `
    <h1>${t.title}</h1>
    <p class="lead">${t.lead}</p>
    ${t.views.length > 1 ? `<div class="t-views" role="group" aria-label="Ansicht">${t.views.map(([k, l]) => `<button aria-pressed="${k === view}" data-view="${k}">${l}</button>`).join("")}</div>` : ""}
    ${legendHtml(view, meta, { gaps: view === "cnet" })}
    <div class="t-kpis">${t.kpis.map(([v, l]) => `<div class="t-kpi"><b>${v}</b><span>${l}</span></div>`).join("")}</div>
    ${t.list ? listHtml(t.list) : ""}
    <p class="t-hint">Tippen Sie auf eine Straße für den Steckbrief.</p>`;
  mv.show(view, { gaps: view === "cnet" });
  if (t.zoom && mv.map.getZoom() < t.zoom - 1) mv.map.easeTo({ zoom: t.zoom, center: [9.965, 53.575] });
  history.replaceState(null, "", `#${theme}/${view}`);
}

async function openSeg(id) {
  $("#sheet").hidden = false;
  $("#sheet-body").innerHTML = "<p>Lade …</p>";
  $("#sheet-body").innerHTML = steckbriefHtml(await profile(id), meta);
  mv.show(view, { gaps: view === "cnet", selected: id });
  $("#sheet").focus();
}
async function openJct(id) {
  $("#sheet").hidden = false;
  $("#sheet-body").innerHTML = junctionBriefHtml(await junction(id), meta);
  $("#sheet").focus();
}

document.addEventListener("click", (ev) => {
  const b = ev.target.closest("button");
  if (!b) return;
  if (b.dataset.theme) { theme = b.dataset.theme; view = THEMES[theme].views[0][0]; render(); }
  else if (b.dataset.view) { view = b.dataset.view; render(); }
  else if (b.dataset.seg) { mv.fit(b.dataset.bbox.split(",").map(Number)); openSeg(b.dataset.seg); }
  else if (b.dataset.jct) { const [lo, la] = b.dataset.ll.split(",").map(Number); mv.flyTo(lo, la, 17); openJct(b.dataset.jct); }
  else if (b.id === "close") { $("#sheet").hidden = true; mv.show(view, { gaps: view === "cnet" }); }
});
document.addEventListener("keydown", (ev) => { if (ev.key === "Escape") $("#sheet").hidden = true; });
render();

// test hook for the screenshot script (analysis/review_2026_11/ui/prototypes.mjs)
window.proto = { openSeg, openJct, get map() { return mv.map; } };
