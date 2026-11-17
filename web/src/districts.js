// "Bezirke" page: district chooser and the overview of one district (sentence, three key figures,
// three top lists, comparison table). Texts come from meta.overview.texts; no codes are shown.
import { approx, approxRange, esc, num } from "./util.js";

// Target speed per category from meta.categories[*].speed_kmh (rules.yaml categories; ETW_ERF 7 = walking pace as a
// calculation value, shown as "Schritttempo").
const WALKING = "ETW_ERF";

/** Replace {key} in a template; numbers are formatted German, missing keys stay empty. */
export function fill(template, values = {}) {
  return String(template ?? "").replace(/\{(\w+)\}/g, (_, k) => {
    const v = values[k];
    if (v === null || v === undefined) return "";
    return typeof v === "number" ? num(v, Number.isInteger(v) ? 0 : 1) : String(v);
  });
}

const fillEsc = (template, values) => esc(fill(template, values));

function streetSentence(meta, texts, s) {
  const kmh = meta.categories?.[s.cat]?.speed_kmh;
  const parts = [];
  if (typeof kmh === "number" && s.speed_ist > kmh) {
    parts.push(fill(texts.street_speed, { speed_ist: s.speed_ist, target: s.cat === WALKING ? "Schritttempo" : kmh }));
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

/** Trees and parking (prompts/26 Teil 2): two cards with levels 2 and 3, for a Bezirk or "Hamburg". */
export function treesParkingHtml(meta, name, heading = "h2") {
  const tp = meta.trees_parking;
  const d = tp?.summary?.[name];
  if (!d) return "";
  const t = tp.texts;
  const pct = (x) => num(100 * x, 0);
  const change = d.park_change_hi <= 0 ? fill(t.parking_less, { n: approxRange(-d.park_change_hi, -d.park_change_lo) })
    : d.park_change_lo >= 0 ? fill(t.parking_more, { n: approxRange(d.park_change_lo, d.park_change_hi) }) : null;
  const parking = fill(t.parking_card, { today: approx(d.park_today_complete), target: approxRange(d.park_target_lo, d.park_target_hi) });
  const keep = approx(d.trees_n - d.trees_affected_mid);
  const trees = fill(t.trees_card, { keep, affected: approx(d.trees_affected_mid), new: approx(d.trees_new) });
  const card = (title, sentence, extra, l2, l3) => `<article class="tp-card">
      <${heading}>${esc(title)}</${heading}>
      <p class="tp-figure">${esc(sentence)}</p>${extra ? `<p class="tp-extra">${esc(extra)}</p>` : ""}
      <details class="level l2"><summary>Was heißt das?</summary><p>${esc(l2)}</p></details>
      <details class="level l3"><summary>Methode, Spannen und Daten</summary><p>${esc(l3)}</p>
        <p><a href="#methode/baeume_parken">Methode: Bäume und Parkplätze</a></p></details>
    </article>`;
  return `<section class="tp-cards" aria-label="Bäume und Parkplätze${name === "Hamburg" ? " in ganz Hamburg" : ` in ${esc(name)}`}">
    ${card(t.parking_title, parking, change, fill(t.parking_l2, { share_known: pct(d.share_complete) }),
      fill(t.parking_l3, { share_official: pct(d.share_official), share_osm: pct(d.share_osm), share_none: pct(d.share_none),
        counted: approx(d.park_counted) }))}
    ${card(t.trees_title, trees, null, t.trees_l2,
      fill(t.trees_l3, { affected_lo: approx(d.trees_affected_lo), affected_hi: approx(d.trees_affected_hi), n: approx(d.trees_n) }))}
  </section>`;
}

export function districtListHtml(meta) {
  const o = meta.overview;
  const cards = Object.entries(o.figures).map(([name, f]) => `<li><button type="button" class="bz-card" data-bz="${esc(name)}">
    <span class="bz-name">${esc(name)}</span>
    <span class="bz-fig">${num(f.km_need)} km: ${esc(o.texts.figures.km_need)}</span>
    <span class="bz-fig">${num(f.junctions_rebuild)}: ${esc(o.texts.figures.junctions_rebuild)}</span>
    <span class="bz-fig">${num(f.km_cycle_missing)} km: ${esc(o.texts.figures.km_cycle_missing)}</span></button></li>`).join("");
  const hh = treesParkingHtml(meta, "Hamburg");
  return `<h1>Bezirke</h1><ul class="bz-cards">${cards}</ul>${hh ? `<h2 class="tp-head">Bäume und Parkplätze in ganz Hamburg</h2>${treesParkingHtml(meta, "Hamburg", "h3")}` : ""}`;
}

export function districtHtml(meta, d) {
  const o = meta.overview;
  const t = o.texts;
  const f = d.figures;
  const rows = Object.entries(o.figures).map(([name, v]) => `<tr${name === d.name ? ' class="current"' : ""}>
    <th scope="row">${esc(name)}</th><td class="n">${num(v.km_total)}</td><td class="n">${num(v.km_need)}</td>
    <td class="n">${num(v.km_profile_no_fit)}</td><td class="n">${num(v.km_cycle_missing)}</td><td class="n">${num(v.junctions_rebuild)}</td></tr>`).join("");
  const kpi = (value, label) => `<div role="listitem"><p class="kpi-value">${value}</p><p class="kpi-label">${esc(label)}</p></div>`;
  return `<div class="intro-l1"><h1>${esc(d.name)}</h1><p>${fillEsc(t.intro, Object.fromEntries(Object.entries(f).map(([k, v]) => [k, Math.round(v)])))}</p></div>
  <div class="kpis" role="list">
    ${kpi(`${num(f.km_need)} km`, t.figures.km_need)}
    ${kpi(num(f.junctions_rebuild), t.figures.junctions_rebuild)}
    ${kpi(`${num(f.km_cycle_missing)} km`, t.figures.km_cycle_missing)}
  </div>
  ${treesParkingHtml(meta, d.name)}
  <details class="level l2" open><summary>Wo ist der Handlungsbedarf am größten?</summary>
    <div class="lists">
      <section><h2>Straßen</h2>${list(d.top?.streets, "seg", (s) => streetSentence(meta, t, s))}</section>
      <section><h2>Kreuzungen</h2>${list(d.top?.junctions, "jct", (j) => junctionSentence(meta, t, j))}</section>
      <section><h2>Radnetz-Lücken</h2>${list(d.top?.gaps, "seg", (g) => gapSentence(meta, t, g))}</section>
    </div>
    <p class="lists-note">${esc(t.lists_note)}</p>
  </details>
  <details class="level l3"><summary>Details und Quellen: alle Bezirke im Vergleich</summary>
    <div class="table-wrap" tabindex="0" role="region" aria-label="Kennzahlen je Bezirk"><table class="data"><caption class="visually-hidden">Kennzahlen je Bezirk</caption>
      <thead><tr><th scope="col">Bezirk</th><th scope="col" class="n">Straßen km</th><th scope="col" class="n">große Abweichung km</th>
        <th scope="col" class="n">Ziel passt nicht km</th><th scope="col" class="n">Radnetz ohne Radweg km</th><th scope="col" class="n">Kreuzungen mit Umbau</th></tr></thead>
      <tbody>${rows}</tbody></table></div>
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
