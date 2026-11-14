// "Bezirke" page: district chooser and the overview of one district (sentence, three key figures,
// three top lists, comparison table). Texts come from meta.overview.texts; no codes are shown.
import { esc, num } from "./util.js";

const TARGET_SPEED = { GOW50: 50, GOW30: 30, ETW30: 30, ETW_ERF: "Schritttempo" };

/** Replace {key} in a template; numbers are formatted German, missing keys stay empty. */
export function fill(template, values = {}) {
  return String(template ?? "").replace(/\{(\w+)\}/g, (_, k) => {
    const v = values[k];
    if (v === null || v === undefined) return "";
    return typeof v === "number" ? num(v, Number.isInteger(v) ? 0 : 1) : String(v);
  });
}

const fillEsc = (template, values) => esc(fill(template, values));

function streetSentence(texts, s) {
  const target = TARGET_SPEED[s.cat];
  const parts = [];
  if (typeof target === "number" && s.speed_ist > target) {
    parts.push(fill(texts.street_speed, { speed_ist: s.speed_ist, target }));
  } else if (target === "Schritttempo" && s.speed_ist > 7) {
    parts.push(fill(texts.street_speed, { speed_ist: s.speed_ist, target }));
  }
  if (s.crashes > 0) parts.push(fill(texts.street_crashes, { crashes: s.crashes }));
  return parts.join("; ");
}

function junctionSentence(meta, texts, j) {
  const c = meta.cycling ?? {};
  const parts = [fill(texts.junction, {
    ist: c.junction_ist?.[j.ist] ?? "",
    soll: c.junction_type?.[j.soll] ?? "",
  })];
  if (j.crashes > 0) parts.push(fill(texts.junction_crashes, { crashes: j.crashes }));
  return parts.join("; ");
}

function gapSentence(meta, texts, g) {
  return fill(texts.gap, { km: g.km, cycle_cat: meta.cycling?.cycle_categories?.[g.cycle_cat] ?? "", demand: g.demand });
}

function entry(kind, x, sentence) {
  const attr = kind === "jct" ? "data-open-jct" : "data-open-seg";
  const at = Array.isArray(x.at) ? ` data-lon="${esc(x.at[0])}" data-lat="${esc(x.at[1])}"` : "";
  return `<li><button type="button" ${attr}="${esc(x.id)}"${at}>${esc(x.name)}</button>`
    + (sentence ? ` <span class="entry-note">${esc(sentence)}</span>` : "") + `</li>`;
}

const list = (items, kind, sentenceOf) =>
  `<ol class="top-list">${(items ?? []).map((x) => entry(kind, x, sentenceOf(x))).join("")}</ol>`;

export function districtListHtml(meta) {
  const o = meta.overview;
  const cards = Object.entries(o.figures).map(([name, f]) => `<li><button type="button" class="bz-card" data-bz="${esc(name)}">
    <span class="bz-name">${esc(name)}</span>
    <span class="bz-fig">${num(f.km_need)} km große Abweichung</span>
    <span class="bz-fig">${num(f.junctions_rebuild)} Kreuzungen mit Umbau</span>
    <span class="bz-fig">${num(f.km_cycle_missing)} km Radnetz ohne Radweg</span></button></li>`).join("");
  return `<h1>Bezirke</h1><ul class="bz-cards">${cards}</ul>`;
}

export function districtHtml(meta, d) {
  const o = meta.overview;
  const t = o.texts;
  const f = d.figures;
  const rows = Object.entries(o.figures).map(([name, v]) => `<tr${name === d.name ? ' class="current"' : ""}>
    <th scope="row">${esc(name)}</th><td class="n">${num(v.km_total)}</td><td class="n">${num(v.km_need)}</td>
    <td class="n">${num(v.km_profile_no_fit)}</td><td class="n">${num(v.km_cycle_missing)}</td><td class="n">${num(v.junctions_rebuild)}</td></tr>`).join("");
  const kpi = (value, label) => `<div role="listitem"><p class="kpi-value">${value}</p><p class="kpi-label">${esc(label)}</p></div>`;
  return `<div class="intro-l1"><h1>${esc(d.name)}</h1><p>${fillEsc(t.intro, f)}</p></div>
  <div class="kpis" role="list">
    ${kpi(`${num(f.km_need)} km`, t.figures.km_need)}
    ${kpi(num(f.junctions_rebuild), t.figures.junctions_rebuild)}
    ${kpi(`${num(f.km_cycle_missing)} km`, t.figures.km_cycle_missing)}
  </div>
  <details class="level l2" open><summary>Wo ist der Handlungsbedarf am größten?</summary>
    <div class="lists">
      <section><h2>Straßen</h2>${list(d.top?.streets, "seg", (s) => streetSentence(t, s))}</section>
      <section><h2>Kreuzungen</h2>${list(d.top?.junctions, "jct", (j) => junctionSentence(meta, t, j))}</section>
      <section><h2>Radnetz-Lücken</h2>${list(d.top?.gaps, "seg", (g) => gapSentence(meta, t, g))}</section>
    </div>
    <p class="lists-note">${esc(t.lists_note)}</p>
  </details>
  <details class="level l3"><summary>Details und Quellen: alle Bezirke im Vergleich</summary>
    <table class="data"><caption class="visually-hidden">Kennzahlen je Bezirk</caption>
      <thead><tr><th scope="col">Bezirk</th><th scope="col" class="n">Straßen km</th><th scope="col" class="n">große Abweichung km</th>
        <th scope="col" class="n">Ziel passt nicht km</th><th scope="col" class="n">Radnetz ohne Radweg km</th><th scope="col" class="n">Kreuzungen mit Umbau</th></tr></thead>
      <tbody>${rows}</tbody></table>
    <p><button type="button" data-show-table>Alle Straßenstücke als Tabelle</button></p>
  </details>`;
}

/** One delegated click handler on root (assigned to root.onclick, so rebinding replaces it). */
export function bindDistrictPage(root, { onPickDistrict, onOpenSegment, onOpenJunction, onShowTable } = {}) {
  root.onclick = (ev) => {
    const hit = (sel) => ev.target?.closest?.(sel);
    const at = (b) => (b.dataset.lon != null && b.dataset.lat != null ? [Number(b.dataset.lon), Number(b.dataset.lat)] : null);
    let b;
    if ((b = hit("[data-bz]"))) onPickDistrict?.(b.dataset.bz);
    else if ((b = hit("[data-open-seg]"))) onOpenSegment?.(b.dataset.openSeg, at(b));
    else if ((b = hit("[data-open-jct]"))) onOpenJunction?.(b.dataset.openJct, at(b));
    else if (hit("[data-show-table]")) onShowTable?.();
  };
}
