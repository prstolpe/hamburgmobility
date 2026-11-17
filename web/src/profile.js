// Profile ("Steckbrief") in three levels: level 1 at a glance, level 2 explanation ("Mehr erfahren"),
// level 3 details and sources. Rule IDs, category codes and segment ids appear only on level 3.
// Port of prototypes/redesign/shared/profile.js to the website code style.
import { junctionSvg } from "./junction_sketch.js";
import { crossSectionSvg } from "./panel.js";
import { issueUrl, mailtoUrl } from "./feedback.js";
import { approx, approxRange, esc, num } from "./util.js";

const TARGET_KMH = { SW: null, GOW50: 50, GOW30: 30, ETW30: 30, ETW_ERF: 7 };
const WALK = "Schritttempo";
const WHY_INTRO = {
  SW: "Die Straße ist eine Autobahn oder Kraftfahrstraße.",
  GOW50: "Die Straße verbindet Stadtteile.",
  GOW30: "Die Straße verbindet Stadtteile.",
  ETW30: "Die Straße erschließt vor allem das Wohngebiet.",
  ETW_ERF: "Hier haben Menschen zu Fuß Vorrang.",
};
const MEASURE = /senken|reduzieren|verlegen|Filter/i;

const cap = (t) => (t ? t[0].toUpperCase() + t.slice(1) : "");
const sentence = (t) => {
  const s = String(t ?? "").trim().replace(/\s*\([A-Z]{1,5}-[A-Z0-9-]+\)\s*$/, "").replace(/[.!?]+$/, "");
  return s ? `${cap(s)}.` : "";
};

function plainName(code, meta, fallback = "Radweg") {
  return meta.glossary?.categories?.[code]?.plain ?? meta.categories?.[code]?.label ?? fallback;
}

/** One plain answer to "how sure is this?". */
/** Rule ID as a link to the rule reference (level 3). */
export function ruleLink(id) {
  const code = `<code>${esc(id)}</code>`;
  return /^[A-Za-z0-9-]+$/.test(String(id ?? "")) ? `<a href="#methode/regeln?regel=${esc(id)}">${code}</a>` : code;
}

function rulePathHtml(path) {
  if (!path) return "<code>–</code>";
  return String(path).split("→").map((x) => ruleLink(x.trim())).join(" → ");
}

export function certainty(p) {
  const uncertain = !!(p.sensitivity?.uncertain || p.confidence?.level === "niedrig");
  const lvl = uncertain ? "unsicher" : p.confidence?.level === "mittel" ? "eher sicher" : "sicher";
  return { lvl, uncertain };
}

function keyLine(p) {
  const code = p.category.code;
  const tk = TARGET_KMH[code];
  const ist = p.ist?.speed_kmh;
  if (tk === null || tk === undefined) return "ohne Tempo-Ziel";
  const target = code === "ETW_ERF" ? WALK : `${tk} km/h`;
  if (code === "ETW_ERF") return ist ? `Heute ${ist} km/h → Ziel ${WALK}` : `Ziel ${WALK}`;
  if (ist && ist > tk) return `Heute ${ist} km/h → Ziel ${target}`;
  if (ist) return `Tempo ${target}, wie heute`;
  return `Ziel ${target}`;
}

/** What should change, as short plain sentences. Current-state cycling only from cycling.facility.ist_text (X3). */
function changes(p) {
  const out = [];
  const code = p.category.code;
  const tk = TARGET_KMH[code];
  const ist = p.ist?.speed_kmh;
  if (tk && ist && ist > tk) out.push(`Tempo ${ist} → ${code === "ETW_ERF" ? WALK : `${tk} km/h`}`);
  const f = p.cycling?.facility;
  if (f?.soll_text && f.gap && !["none", "not_assessed"].includes(f.gap)) {
    out.push(`Radverkehr: heute ${f.ist_text ?? "kein Radweg"} → ${f.soll_text}`);
  }
  const l = p.cycling?.lanes;
  if (l?.change === "fewer") out.push(`Kfz-Fahrstreifen je Richtung: ${l.ist} → ${l.soll}`);
  return out;
}

// the map view "Passt das Ziel?" is switched off (prompt 25): the profile explains the feasibility on its own
const FIT_EXPLAIN = "Gezählt sind Gehwege, Radweg, Fahrbahn, Bäume und Parken des Ziels nebeneinander, an der engsten Stelle der Straße.";

function fitStatement(p) {
  const pr = p.cycling?.profile;
  if (pr?.fit_text) {
    return { text: `${cap(pr.fit_text)}: ${num(pr.required_m, 1)} m nötig, ${num(pr.available_m, 1)} m vorhanden.`, drawing: true };
  }
  const t = p.crosssection?.feasibility_text;
  return t ? { text: `${cap(t)}.`, drawing: false } : null;
}

function feedback(p, meta, pageUrl) {
  const url = issueUrl(meta.github_repo, p, pageUrl) ?? mailtoUrl(meta.feedback_email, p, pageUrl);
  return url ? `<p class="t-small"><a href="${esc(url)}" rel="noopener">Stimmt etwas nicht?</a></p>` : "";
}

const UNSURE = '<p class="note">Diese Einstufung ist unsicher: Ein entscheidender Wert fehlt oder liegt nahe an einer Grenze. Bitte prüfen.</p>';

function cyclingDetails(p) {
  const c = p.cycling;
  if (!c) return "";
  const rows = [];
  if (c.cycle_cat?.label) rows.push(["Radnetz", c.cycle_cat.label]);
  if (c.facility) rows.push(["Radanlage", `heute ${c.facility.ist_text ?? "unbekannt"}, Ziel ${c.facility.soll_text ?? "–"}`]);
  if (c.width?.soll_m != null) rows.push(["Breite Soll", `${num(c.width.soll_m, 2)} m${c.width.ist_m != null ? `, heute ${num(c.width.ist_m, 2)} m` : ""}`]);
  if (c.lanes) rows.push(["Fahrstreifen je Richtung", `heute ${c.lanes.ist ?? "?"}, Ziel ${c.lanes.soll ?? "?"}${c.lanes.change_text ? ` (${c.lanes.change_text})` : ""}`]);
  const pr = c.principles;
  if (pr?.ist && pr?.soll) rows.push(["Fünf Prinzipien", `Wertung heute ${num(pr.ist.score, 2)}, Ziel ${num(pr.soll.score, 2)}`]);
  return `<h3>Radverkehr</h3><dl>${rows.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl>`;
}

/** Special place (prompts/26): a band right below level 1 (one sentence, status with date); the comparison with the
 * rule result follows the rule explanation on level 2. The rule text itself stays unchanged. */
function placeBand(sp) {
  if (!sp) return "";
  return `<div class="place-band" style="--place:${esc(sp.colour)}">
      <p class="place-title">${esc(sp.band)}</p>
      <p class="t-small">${esc(sp.status_line)} · <a href="#orte">Mehr zum Vorschlag</a></p>
    </div>`;
}

/** Cross section with the proposal's measure (computed in the export with our cross-section logic), after our own. */
function placeProfile(sp, meta) {
  const pr = sp?.profile;
  if (!pr?.elements?.length) return "";
  const t = meta.special_places?.texts ?? {};
  const title = t.profile_title ?? "Querschnitt im Vorschlag";
  if (pr.same_as_soll) return `<h3>${esc(title)}</h3><p>${esc(t.profile_same ?? "")}</p>`;
  return `<h3>${esc(title)}</h3>
      ${pr.fit_text ? `<p class="fit">${esc(cap(pr.fit_text))}.</p>` : ""}
      ${crossSectionSvg(pr.elements, pr.available_m, meta, { title, need: "Bedarf im Vorschlag" })}
      ${sp.profile_note ? `<p class="t-small">${esc(sp.profile_note)}</p>` : ""}`;
}

/** Trees and parking of the segment (prompts/26 Teil 2), level 2; estimates, missing data stays "keine Daten". */
function treesParking(tp, meta) {
  const t = meta.trees_parking?.texts;
  if (!tp || !t) return "";
  const f = (tpl, v) => String(tpl ?? "").replace(/\{(\w+)\}/g, (_, k) => v[k] ?? "");
  const pk = tp.parking;
  let parking;
  if (pk.complete) parking = f(t.profile_parking, { today: approx(pk.today), target: approxRange(pk.target_min, pk.target_max) });
  else if (pk.today_known != null) parking = f(t.profile_parking_partial, { today: approx(pk.today_known) });
  else parking = t.profile_parking_none;
  const src = [...new Set([pk.src_left, pk.src_right])].map((s) => t.profile_source?.[s]).filter(Boolean).join(", ");
  const tr = tp.trees;
  const trees = tr.n ? f(t.profile_trees, { n: num(tr.n), affected: approxRange(tr.affected_min, tr.affected_max), new: approx(tr.new) })
    : t.profile_trees_none;
  return `<h3>${esc(t.profile_title)}</h3>
      <p>${esc(parking)}${src ? ` <span class="t-small muted">(${esc(src)})</span>` : ""}</p>
      <p>${esc(trees)}</p>
      <p class="t-small">${esc(t.profile_note)}</p>`;
}

function placeCompare(sp) {
  if (!sp) return "";
  return `<h3>Vorschlag für diesen Ort</h3>
      <p>${esc(sp.compare)}${(sp.notes ?? []).map((n) => ` ${esc(n)}`).join("")}</p>`;
}

export function segmentHtml(p, meta, pageUrl, { level2Open = true } = {}) {
  const code = p.category.code;
  const c = certainty(p);
  const reasons = p.reasons ?? [];
  const yes = reasons.filter((r) => r.passed !== false).map((r) => sentence(r.text)).filter(Boolean);
  const ch = changes(p);
  const fit = fitStatement(p);
  const pr = p.cycling?.profile;
  const xs = fit?.drawing && pr?.elements?.length ? crossSectionSvg(pr.elements, pr.available_m, meta) : "";
  const measure = (p.cycling?.flags ?? []).find((f) => MEASURE.test(f));
  const name = plainName(code, meta, p.category.label);

  const l1 = `
    <p class="meta">${esc(p.bezirk)} · ${num(p.length_m)} m</p>
    <h2 id="panel-title">${esc(p.name ?? "Straße ohne Namen")}</h2>
    <div class="l1 cat cat-${esc(code)}">
      <p class="label">${esc(name)}</p>
      <p class="key">${esc(keyLine(p))}</p>
    </div>${placeBand(p.special_place)}`;

  const l2 = `
    <details class="level l2"${level2Open ? " open" : ""}><summary>Mehr erfahren</summary>
      <h3 id="h-why">Warum?</h3>
      <p>${esc(WHY_INTRO[code] ?? "")} ${yes.map(esc).join(" ")}</p>
      ${placeCompare(p.special_place)}
      <h3>Was ändert sich?</h3>
      ${ch.length ? `<ul>${ch.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : "<p>Für die Aufgabe der Straße ist kein Umbau nötig.</p>"}
      ${fit ? `<h3>Hat das Ziel Platz?</h3><p class="fit">${esc(fit.text)}</p>${fit.drawing ? `<p class="t-small">${FIT_EXPLAIN}</p>` : ""}` : ""}
      ${xs}
      ${placeProfile(p.special_place, meta)}
      ${treesParking(p.trees_parking, meta)}
      ${measure ? `<p class="note">${esc(sentence(measure))}</p>` : ""}
      ${c.uncertain ? UNSURE : ""}
      ${feedback(p, meta, pageUrl)}
    </details>`;

  const rules = reasons.map((r) => `<li>${ruleLink(r.rule)} ${r.passed === false ? "trifft nicht zu" : "trifft zu"}: ${esc(r.text)}</li>`).join("");
  const d = p.discrepancy ?? {};
  const cr = d.crashes;
  const conf = p.confidence ?? {};
  const sens = p.sensitivity ?? {};
  const l3 = `
    <details class="level l3"><summary>Details und Quellen</summary>
      <h3>Regeln mit Werten</h3>
      <p class="t-small">Entscheidungsweg: ${rulePathHtml(p.rule_path)} · Kategorie <code>${esc(code)}</code></p>
      <ul class="t-small">${rules}</ul>
      <h3>Wie sicher ist das?</h3>
      <dl><dt>Gesamt</dt><dd>${esc(c.lvl)}</dd>
        <dt>Daten</dt><dd>${esc(conf.summary ?? "–")}${conf.reasons?.length ? `<ul>${conf.reasons.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : ""}</dd>
        <dt>Annahmen</dt><dd>${esc(sens.text ?? "nicht berechnet")}${sens.triggers?.length ? `<ul>${sens.triggers.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : ""}</dd></dl>
      <h3>Abweichung vom Soll</h3>
      <dl><dt>Art</dt><dd>${esc(d.type ?? "–")} ${esc(d.type_text ?? "keine")}</dd>
        <dt>Stufen</dt><dd>Tempo ${esc(d.speed ?? "–")}, Gestaltung ${esc(d.design ?? "–")}, Nutzung ${esc(d.use ?? "–")}</dd>
        <dt>Unfälle</dt><dd>${num(cr?.ped_cyc ?? 0)} mit Fuß- oder Radbeteiligung${cr?.years ? ` (${esc(cr.years)})` : ""}</dd>
        <dt>Priorität</dt><dd>${d.priority != null ? num(d.priority, 1) : "–"}</dd></dl>
      ${cyclingDetails(p)}
      <h3>Daten</h3>
      <ul class="t-small">${(p.sources ?? []).map((s) => `<li>${esc(s.title)} (${esc(s.as_of)}, ${esc(s.license)}): ${esc(s.purpose)}</li>`).join("")}</ul>
      <p class="t-small muted">Abschnitt <code>${esc(p.id)}</code> · Version ${esc(p.version)}</p>
      ${feedback(p, meta, pageUrl)}
    </details>`;
  return `<article class="profile" aria-labelledby="panel-title">${l1}${l2}${l3}</article>`;
}

export function junctionHtml(j, meta, pageUrl, { level2Open = true } = {}) {
  const need = j.action_needed;
  const sollText = j.soll?.text ?? "kein Soll-Typ";
  const names = [...new Map((j.legs ?? []).filter((l) => l.name).map((l) => [`${l.name}|${l.cat}`, `${l.name} (${plainName(l.cat, meta)})`])).values()];
  const uniq = [...new Set(names)];
  const code = j.soll?.code ?? "";
  const conf = j.confidence;
  const fb = feedback({ id: j.id, name: j.names, bezirk: j.bezirk, version: j.version, category: { code, label: sollText } }, meta, pageUrl);

  const l1 = `
    <p class="meta">Kreuzung · ${esc(j.bezirk)}</p>
    <h2 id="panel-title">${esc(j.names ?? "Kreuzung")}</h2>
    <div class="l1">
      <p class="label">${esc(cap(sollText))}</p>
      <p class="key">heute: ${esc(j.ist?.text ?? "unbekannt")}${need ? " · Umbau nötig" : " · passt"}</p>
    </div>`;
  const l2 = `
    <details class="level l2"${level2Open ? " open" : ""}><summary>Mehr erfahren</summary>
      <h3>Was ist hier?</h3>
      <p>Hier treffen sich ${uniq.map(esc).join(", ")}. Heute: ${esc(j.ist?.text ?? "unbekannt")}.</p>
      <h3>Was ändert sich?</h3>
      <p>Ziel: ${esc(sollText)}.${need ? " Dafür muss die Kreuzung umgebaut werden." : " Die Kreuzung passt schon."}</p>
      ${j.treatment ? `<p>Für Radfahrende: ${esc(j.treatment)}</p>` : ""}
      ${junctionSvg(j, meta)}
      ${conf?.code === "low" ? '<p class="note">Diese Einstufung ist unsicher: Werte fehlen. Bitte prüfen.</p>' : ""}
      ${fb}
    </details>`;
  const l3 = `
    <details class="level l3"><summary>Details und Quellen</summary>
      <h3>Arme</h3>
      <ul class="t-small">${(j.legs ?? []).map((l) => `<li>${esc(l.name ?? "–")}: <code>${esc(l.cat ?? "–")}</code>, ${esc(l.cycle_cat?.label ?? "kein Radnetz")}${l.facility_text ? `, ${esc(l.facility_text)}` : ""}${l.dtv ? `, ${num(l.dtv)} Kfz/Tag` : ""}</li>`).join("")}</ul>
      <dl><dt>Regel</dt><dd>${esc(j.rule?.text ?? "–")}${j.rule?.id ? ` (${ruleLink(j.rule.id)})` : ""}</dd>
        <dt>Zufluss</dt><dd>${j.entering_dtv ? `${num(j.entering_dtv)} Kfz/Tag` : "unbekannt"}</dd>
        <dt>Platz</dt><dd>${j.space_radius_m ? `Kreis mit ${num(j.space_radius_m, 1)} m Radius` : "unbekannt"}</dd>
        <dt>Radunfälle</dt><dd>${num(j.crashes?.cyc ?? 0)} (5 Jahre)</dd>
        <dt>Rang Umbau</dt><dd>${j.priority_rank ?? "–"}</dd>
        <dt>Daten</dt><dd>${esc(conf?.text ?? "–")}</dd></dl>
      <p class="t-small muted">Kreuzung <code>${esc(j.id)}</code> · Version ${esc(j.version)}</p>
      ${fb}
    </details>`;
  return `<article class="profile" aria-labelledby="panel-title">${l1}${l2}${l3}</article>`;
}
