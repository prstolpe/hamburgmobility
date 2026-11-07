// Prototype B – Ist/Soll comparison: two synchronised maps, the right one clipped at a draggable divider.
// Modes: speed today vs. Soll, cycling facility today vs. Soll, published category vs. scenario "GOW50-Kompromiss".
// The profile shows the cross-section today (schematic) and Soll.
import { BZ, fmt, junction, loadAll, profile } from "../shared/data.js";
import { createMap, legendHtml } from "../shared/map.js";
import { junctionBriefHtml, steckbriefHtml } from "../shared/steckbrief.js";

const $ = (s) => document.querySelector(s);
const { meta, kpi, scenario } = await loadAll();
const MODES = {
  tempo: { label: "Tempo", a: ["speed", "Heute zulässig"], b: ["soll_speed", "Soll nach Entwurf"],
    note: "Gleiche Farben, gleiche Bedeutung: links das heutige Tempolimit, rechts das Tempo der Soll-Kategorie." },
  rad: { label: "Radanlagen", a: ["fac_ist", "Radanlage heute (OpenStreetMap)"], b: ["fac_soll", "Radanlage Soll (Entwurf)"],
    note: "Links die heutige Radanlage, rechts die vorgeschlagene. Grau dünn: Radverkehr auf der Fahrbahn." },
  szenario: { label: "Szenario Verkehrsmenge", a: ["cat", "Veröffentlicht (Regelwerk 0.16.0)"], b: ["scenario", "Szenario „GOW50-Kompromiss“"],
    note: `Im Szenario bestimmt die heutige Verkehrsmenge mit: ${fmt(scenario.pairs_km["GOW30->GOW50"], 1)} km Stadtstraße 30 würden Stadtmagistrale (Tempo 50). Insgesamt ändern sich ${fmt(scenario.km_changed, 1)} km.` },
};
let mode = MODES[location.hash.slice(1)] ? location.hash.slice(1) : "tempo";

const opts = { meta, kpi, bz: BZ, scenario, onSelect: (id) => openSeg(id), onSelectJunction: (id) => openJct(id) };
const a = createMap($("#map-a"), { ...opts, interactive: false });
const b = createMap($("#map-b"), opts);
const sync = () => a.map.jumpTo({ center: b.map.getCenter(), zoom: b.map.getZoom(), bearing: b.map.getBearing(), pitch: b.map.getPitch() });
b.map.on("move", sync);
b.map.on("load", sync);

function render() {
  const m = MODES[mode];
  $("#modes").innerHTML = Object.entries(MODES).map(([k, v]) => `<button aria-pressed="${k === mode}" data-mode="${k}">${v.label}</button>`).join("");
  $("#tag-a").textContent = `◀ ${m.a[1]}`;
  $("#tag-b").textContent = `${m.b[1]} ▶`;
  a.show(m.a[0]);
  b.show(m.b[0]);
  // both sides share colours; the legend of the right side covers both (scenario: categories)
  $("#legend").innerHTML = `<p>${m.note}</p>${legendHtml(m.b[0] === "scenario" ? "cat" : m.b[0], meta)}`;
  history.replaceState(null, "", `#${mode}`);
}

async function openSeg(id) {
  $("#sheet").hidden = false;
  $("#sheet-body").innerHTML = "<p>Lade …</p>";
  $("#sheet-body").innerHTML = steckbriefHtml(await profile(id), meta, { compare: true, scenarioCat: scenario.segments[id] ?? null });
  $("#sheet").focus();
}
async function openJct(id) {
  $("#sheet").hidden = false;
  $("#sheet-body").innerHTML = junctionBriefHtml(await junction(id), meta);
}

$("#split").addEventListener("input", (ev) => $("#stage").style.setProperty("--split", `${ev.target.value}%`));
document.addEventListener("click", (ev) => {
  const t = ev.target.closest("button");
  if (t?.dataset.mode) { mode = t.dataset.mode; render(); }
  if (t?.id === "close") $("#sheet").hidden = true;
});
document.addEventListener("keydown", (ev) => { if (ev.key === "Escape") $("#sheet").hidden = true; });
render();

// test hook for the screenshot script (analysis/review_2026_11/ui/prototypes.mjs)
window.proto = { openSeg, openJct, get map() { return b.map; } };
