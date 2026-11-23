// Content of an image card (prompt 28): pure functions, no DOM (tested in test/card.test.js). Layout: card.css.
import logoUrl from "./brand/hmr-header@2x.png";
import { junctionSvg } from "./junction_sketch.js";
import { crossSectionSvg } from "./panel.js";
import { fitStatement } from "./profile.js";
import { DEFAULTS, toHash } from "./state.js";
import { esc, num } from "./util.js";

export const FORMATS = {
  og: { width: 1200, height: 630, scale: 1, label: "Linkvorschau" },
  portrait: { width: 1080, height: 1350, scale: 1, label: "Social Media hochkant" },
  a4: { width: 827, height: 591, scale: 2, label: "Einklinker A4 (140 × 100 mm, 300 dpi)" },
};
const SITE = "hamburgmobility.de";
const dateDe = (d) => new Date(d).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" });

/** Card content of a segment (pure, exported for tests). */
export function segmentCard(p, meta) {
  const code = p.category.code;
  const cat = meta.categories[code]?.label ?? p.category.label;
  const ist = p.ist ?? {};
  const today = [ist.speed_kmh ? `Tempo ${ist.speed_kmh}` : "Tempo unbekannt", ist.cycling ? `Rad: ${ist.cycling}` : null].filter(Boolean).join(", ");
  const pr = p.cycling?.profile;
  const fit = fitStatement(p);
  const elements = fit?.drawing && pr?.elements?.length ? pr.elements.filter((e) => e.width_m > 0) : [];
  const label = (e) => meta.cycling?.elements?.[e.element]?.label ?? e.element;
  return {
    kind: "seg", title: p.name ?? "Straße ohne Namen", sub: `${p.bezirk} · ${num(p.length_m)} m`,
    sentence: `Ziel: ${cat}. Heute: ${today}.`,
    sketch: elements.length ? crossSectionSvg(pr.elements, pr.available_m, meta) : "",
    sketchCaption: elements.length ? `Querschnitt im Ziel${fit?.text ? ` – ${fit.text}` : ""}` : "",
    todayLine: p.crosssection?.width_median_m ? `Heute ${num(p.crosssection.width_median_m, 1)} m von Grundstück zu Grundstück.` : "",
    altSketch: elements.length ? `Querschnitt im Ziel: ${elements.map((e) => `${label(e)} ${num(e.width_m, 1)} m`).join(", ")}.` : "",
    link: toHash({ ...DEFAULTS, seg: p.id }),
  };
}

/** Card content of a junction. */
export function junctionCard(j, meta) {
  const title = `Kreuzung ${j.names ?? ""}`.trim();
  return {
    kind: "jct", title, sub: j.bezirk ?? "",
    sentence: `Ziel: ${j.soll?.text ?? "kein Ziel festgelegt"}. Heute: ${j.ist?.text ?? "unbekannt"}.${j.action_needed ? " Umbau nötig." : ""}`,
    sketch: junctionSvg(j, meta, { title: `Skizze ${title}` }), sketchCaption: "Skizze der Kreuzung im Ziel", todayLine: "",
    altSketch: j.soll?.text ? `Skizze der Kreuzung im Ziel: ${j.soll.text}.` : "",
    link: toHash({ ...DEFAULTS, jct: String(j.id) }),
  };
}

/** Card content of a special place (prompts/26). */
export function placeCard(p) {
  const dashed = (m) => p.theme?.pattern?.[m.measure] === "dashed";
  const measures = [...new Map(p.measures.map((m) => [m.label, `${m.label}${dashed(m) ? " (gestrichelt)" : ""}`])).values()].join(", ");
  return {
    kind: "place", title: p.title, sub: `${p.kind_plain} · ${p.initiator}`,
    sentence: `${measures}. Stand ${dateDe(p.status_date)}: ${p.status}.`,
    sketch: "", sketchCaption: "", todayLine: "", altSketch: "",
    link: toHash({ ...DEFAULTS, place: p.id }),
  };
}

/** Alt text of the whole image, from the data (no "undefined", no layout words). */
export function altText(c, meta) {
  return [`Karte: ${c.title}${c.sub ? ` (${c.sub})` : ""}, hervorgehoben.`, c.sentence, c.altSketch,
    `Straßenfunktionsplan Hamburg, nicht amtlicher Entwurf, Datenstand ${dateDe(meta.data_date)}.`].filter(Boolean).join(" ");
}

export function cardHtml(c, meta, format) {
  // the junction sheet is too small to read in the 1200 × 630 link preview: there the text carries it
  const xs = c.sketch && !(format === "og" && c.kind === "jct") ? `<figure class="card-sketch">${c.sketch}<figcaption>${esc(c.sketchCaption)}</figcaption></figure>` : "";
  return `<div class="card-map" id="card-map"></div>
    <div class="card-text">
      <p class="card-kicker">Straßenfunktionsplan Hamburg – Entwurf</p>
      <h1 class="card-title">${esc(c.title)}</h1>
      ${c.sub ? `<p class="card-sub">${esc(c.sub)}</p>` : ""}
      <p class="card-sentence">${esc(c.sentence)}</p>
      ${c.todayLine ? `<p class="card-today">${esc(c.todayLine)}</p>` : ""}
      ${format === "portrait" ? "" : xs}
    </div>
    ${format === "portrait" ? xs : ""}
    <footer class="card-foot">
      <p>Nicht amtlicher Entwurf · Datenstand ${esc(dateDe(meta.data_date))} · Kartendaten © OpenStreetMap-Beitragende (ODbL) · Protomaps · Quellen: ${SITE}/#daten</p>
      <p class="card-link">${esc(SITE)}/${esc(c.link)}</p>
      <img class="card-logo" src="${logoUrl}" alt="" width="99" height="28">
    </footer>`;
}

