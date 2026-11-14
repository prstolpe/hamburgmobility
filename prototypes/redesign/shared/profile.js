// Profile ("Steckbrief") in three levels for the redesign prototypes (prompt 24, A2/A3): level 1 at a glance,
// level 2 explanation ("Mehr erfahren"), level 3 details and sources. Works on the existing profile JSON in
// data/out (segments/*.json, junctions/*.json); rule IDs and codes only on level 3. Plain names follow
// config/glossary.yaml.
import { crossSectionSvg } from "../../../web/src/panel.js";
import { esc, num } from "../../../web/src/util.js";
import { changes, fitAnswer } from "../../shared/steckbrief.js";
import { PLAIN_CAT, T } from "./map.js";

const TARGET_KMH = { SW: null, GOW50: 50, GOW30: 30, ETW30: 30, ETW_ERF: 20 };
const COLOR_OF = { SW: T.speed[99], GOW50: T.speed[50], GOW30: T.speed[30], ETW30: T.speed[30], ETW_ERF: T.speed[20] };
const WHY_INTRO = {
  SW: "Die Straße ist eine Autobahn oder Kraftfahrstraße.",
  GOW50: "Die Straße verbindet Stadtteile.",
  GOW30: "Die Straße verbindet Stadtteile.",
  ETW30: "Die Straße erschließt vor allem das Wohngebiet.",
  ETW_ERF: "Hier haben Menschen zu Fuß Vorrang.",
};
const sentence = (t) => { const s = String(t).trim().replace(/\s*\([A-Z]{1,5}-[A-Z0-9-]+\)\s*$/, ""); return s ? s[0].toUpperCase() + s.slice(1) + (/[.!?]$/.test(s) ? "" : ".") : ""; };

/** One plain answer to "how sure is this?": unsicher only if data are missing/near a threshold or the category flips. */
export function certainty(p) {
  const uncertain = p.sensitivity?.uncertain || p.confidence?.level === "niedrig";
  const lvl = uncertain ? "unsicher" : p.confidence?.level === "mittel" ? "eher sicher" : "sicher";
  return { lvl, uncertain };
}

function keyNumber(p) {
  const tk = TARGET_KMH[p.category.code];
  const ist = p.ist.speed_kmh;
  if (tk && ist && ist > tk) return `Heute ${ist} km/h → Ziel ${tk === 20 ? "Schritttempo" : `${tk} km/h`}`;
  if (tk && ist) return `Tempo ${tk === 20 ? "Schritttempo" : `${tk} km/h`}, wie heute`;
  if (!tk) return "ohne Tempo-Ziel";
  return `Ziel ${tk} km/h`;
}

export function segmentHtml(p, meta, { level2Open = true } = {}) {
  const cat = p.category.code;
  const c = certainty(p);
  const yes = p.reasons.filter((r) => r.passed !== false).map((r) => sentence(r.text));
  const no = p.reasons.filter((r) => r.passed === false);
  const ch = changes(p).map((x) => x.replace(p.category.label, PLAIN_CAT[cat] ?? p.category.label));
  const fit = fitAnswer(p);
  const pr = p.cycling?.profile;
  const measures = (p.cycling?.flags ?? []).filter((f) => /senken|reduzieren|verlegen|Filter/i.test(f));
  const xs = pr?.elements?.length ? crossSectionSvg(pr.elements, pr.available_m, meta) : "";
  const mail = meta.feedback_email ? `mailto:${meta.feedback_email}?subject=${encodeURIComponent(`Rückmeldung ${p.name ?? p.id}`)}` : null;

  const l1 = `
    <p class="meta">${esc(p.bezirk)} · ${num(p.length_m)} m</p>
    <h2 class="t-title" id="panel-title">${esc(p.name ?? "Straße ohne Namen")}</h2>
    <div class="l1" style="border-left-color:${COLOR_OF[cat] ?? T.unknown}">
      <p class="label">${esc(PLAIN_CAT[cat] ?? p.category.label)}</p>
      <p class="key">${esc(keyNumber(p))}</p>
    </div>`;

  const l2 = `
    <details class="level l2" ${level2Open ? "open" : ""}><summary>Mehr erfahren</summary>
      <h3>Warum?</h3>
      <p>${esc(WHY_INTRO[cat] ?? "")} ${yes.map(esc).join(" ")}</p>
      <h3>Was ändert sich?</h3>
      ${ch.length ? `<ul>${ch.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : "<p>Für die Aufgabe der Straße ist kein Umbau nötig.</p>"}
      ${xs ? `<figure class="xs-figure">${xs}<figcaption><strong>Passt ${fit.ok === "ja" ? "" : fit.ok === "nein" ? "nicht" : "knapp"}:</strong> ${esc(fit.text.replace(/^[^:]*:\s*/, ""))}</figcaption></figure>` : `<p class="muted">${esc(fit.text)}</p>`}
      ${measures.length ? `<p class="note">${esc(measures[0][0].toUpperCase() + measures[0].slice(1))}.</p>` : ""}
      ${c.uncertain ? '<p class="note">Diese Einstufung ist unsicher: Ein entscheidender Wert fehlt oder liegt nahe an einer Grenze. Bitte prüfen.</p>' : ""}
      ${mail ? `<p class="t-small" style="margin-top:16px"><a href="${mail}">Stimmt etwas nicht? Rückmeldung geben</a></p>` : ""}
    </details>`;

  const rules = p.reasons.map((r) => `<li><code>${esc(r.rule)}</code> ${r.passed === false ? "trifft nicht zu:" : "trifft zu:"} ${esc(r.text)}</li>`).join("");
  const l3 = `
    <details class="level l3"><summary>Details und Quellen</summary>
      <h3>Regeln mit Werten</h3>
      <p class="t-small">Entscheidungsweg: <code>${esc(p.rule_path ?? "–")}</code> · Kategorie <code>${esc(cat)}</code></p>
      <ul class="t-small">${rules}</ul>
      ${no.length ? `<p class="t-small muted">„Trifft nicht zu“ erklärt, warum eine andere Kategorie nicht gewählt wurde.</p>` : ""}
      <h3>Wie sicher ist das?</h3>
      <dl><dt>Gesamt</dt><dd>${esc(c.lvl)}</dd>
        <dt>Daten</dt><dd>${esc(p.confidence.summary)}</dd>
        <dt>Annahmen</dt><dd>${esc(p.sensitivity?.text ?? "nicht berechnet")}</dd></dl>
      <h3>Heute und Ziel</h3>
      <dl><dt>Tempo heute</dt><dd>${p.ist.speed_kmh ?? "unbekannt"} km/h (${esc(p.ist.speed_source ?? "")})</dd>
        <dt>Abweichung</dt><dd>${esc(p.discrepancy.type_text ?? "keine")}${p.discrepancy.causes?.length ? `: ${esc(p.discrepancy.causes.join(", "))}` : ""}</dd>
        <dt>Unfälle</dt><dd>${p.discrepancy.crashes?.ped_cyc ?? 0} mit Fuß- oder Radbeteiligung (${esc(p.discrepancy.crashes?.years ?? "")})</dd>
        ${p.cycling?.cycle_cat ? `<dt>Radnetz</dt><dd>${esc(p.cycling.cycle_cat.label)}</dd>` : ""}
        ${p.cycling?.facility ? `<dt>Radweg</dt><dd>heute ${esc(p.cycling.facility.ist_text ?? "unbekannt")}, Ziel ${esc(p.cycling.facility.soll_text ?? "–")}</dd>` : ""}</dl>
      <h3>Daten</h3>
      <ul class="t-small">${p.sources.map((s) => `<li>${esc(s.title)} (${esc(s.as_of)}, ${esc(s.license)}): ${esc(s.purpose)}</li>`).join("")}</ul>
      <p class="t-small muted">Abschnitt <code>${esc(p.id)}</code> · Version ${esc(p.version)}</p>
    </details>`;
  return `<article class="profile" aria-labelledby="panel-title">${l1}${l2}${l3}</article>`;
}

export function junctionHtml(j, meta, { level2Open = true } = {}) {
  const legs = j.legs.map((l) => `${esc(l.name ?? "Weg")} (${esc(PLAIN_CAT[l.cat] ?? "Radweg")})`);
  const uniq = [...new Set(legs)];
  const l1 = `
    <p class="meta">Kreuzung · ${esc(j.bezirk)}</p>
    <h2 class="t-title" id="panel-title">${esc(j.names ?? "Kreuzung")}</h2>
    <div class="l1" style="border-left-color:${j.action_needed ? T.need : T.ink}">
      <p class="label">${esc(j.soll.text[0].toUpperCase() + j.soll.text.slice(1))}</p>
      <p class="key">heute: ${esc(j.ist.text)}${j.action_needed ? " · Umbau nötig" : " · passt"}</p>
    </div>`;
  const l2 = `
    <details class="level l2" ${level2Open ? "open" : ""}><summary>Mehr erfahren</summary>
      <h3>Was ist hier?</h3>
      <p>Hier treffen sich ${uniq.join(", ")}. Heute: ${esc(j.ist.text)}.</p>
      <h3>Was ändert sich?</h3>
      <p>Ziel: ${esc(j.soll.text)}.${j.action_needed ? " Dafür muss die Kreuzung umgebaut werden." : ""}</p>
      ${j.treatment ? `<p>Für Radfahrende: ${esc(j.treatment)}</p>` : ""}
      ${j.confidence?.code === "low" ? '<p class="note">Diese Einstufung ist unsicher: Werte fehlen. Bitte prüfen.</p>' : ""}
    </details>`;
  const l3 = `
    <details class="level l3"><summary>Details und Quellen</summary>
      <h3>Arme</h3>
      <ul class="t-small">${j.legs.map((l) => `<li>${esc(l.name ?? "–")}: <code>${esc(l.cat ?? "Radweg")}</code>, ${esc(l.cycle_cat?.label ?? "kein Radnetz")}, ${esc(l.facility_text ?? "")}${l.dtv ? `, ${num(l.dtv)} Kfz/Tag` : ""}</li>`).join("")}</ul>
      <dl><dt>Regel</dt><dd>${esc(j.rule?.text ?? "–")}</dd>
        <dt>Zufluss</dt><dd>${j.entering_dtv ? `${num(j.entering_dtv)} Kfz/Tag` : "unbekannt"}</dd>
        <dt>Platz</dt><dd>${j.space_radius_m ? `Kreis mit ${num(j.space_radius_m, 1)} m Radius` : "unbekannt"}</dd>
        <dt>Radunfälle</dt><dd>${j.crashes?.cyc ?? 0} (5 Jahre)</dd>
        <dt>Rang Umbau</dt><dd>${j.priority_rank ?? "–"}</dd>
        <dt>Daten</dt><dd>${esc(j.confidence?.text ?? "–")}</dd></dl>
      <p class="t-small muted">Kreuzung <code>${esc(j.id)}</code> · Version ${esc(j.version)}</p>
    </details>`;
  return `<article class="profile" aria-labelledby="panel-title">${l1}${l2}${l3}</article>`;
}
