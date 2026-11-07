// New profile ("Steckbrief") for the prototypes: short answer first, then reasons in plain language, then details
// and sources. Rule IDs only in a collapsible part. Works on the existing profile JSON (data/out/segments/*.json),
// so it could replace web/src/panel.js without pipeline changes.
import { crossSectionSvg } from "../../web/src/panel.js";
import { esc, num } from "../../web/src/util.js";
import { SOLL_SPEED } from "./map.js";

const SOLL_KMH = { SW: 80, GOW50: 50, GOW30: 30, ETW30: 30, ETW_ERF: 20 };
const NEED = (pr) => (pr == null || pr <= 0 ? ["kein", "Kein Handlungsbedarf erkannt"] : pr >= 2 ? ["hoch", "Dringender Handlungsbedarf"]
  : pr >= 1 ? ["mittel", "Mittlerer Handlungsbedarf"] : ["gering", "Geringer Handlungsbedarf"]);
const LANE_W = 3.25; // assumption for the schematic "today" cross-section (source_type: assumption)
const SIDEWALK_W = 2.5; // assumption
const TRACK_W = 1.6; // assumption

/** What should change, as short plain sentences (from fields that exist in the profile JSON). */
export function changes(p) {
  const out = [];
  const soll = SOLL_KMH[p.category.code];
  if (p.ist.speed_kmh != null && soll != null && p.ist.speed_kmh > soll) out.push(`Tempo ${p.ist.speed_kmh} → ${soll === 20 ? "Schrittgeschwindigkeit" : soll} km/h`);
  const f = p.cycling?.facility;
  if (f && f.gap && !["none", "not_assessed"].includes(f.gap) && f.soll_text) out.push(`Radverkehr: heute ${f.ist_text ? f.ist_text.toLowerCase() : "keine Radanlage"} → ${f.soll_text}`);
  const l = p.cycling?.lanes;
  if (l?.change === "fewer") out.push(`Kfz-Fahrstreifen je Richtung: ${l.ist} → ${l.soll}`);
  if (l?.change === "shared" && Number(l.ist) >= 1) out.push("Fahrstreifen-Markierung entfällt (Mischverkehr)");
  if (p.discrepancy.causes?.some((c) => c.startsWith("Verkehrsmenge"))) {
    out.push(`Verkehrsmenge: heute ${num(p.ist.dtv)} Kfz/Tag – mehr als für eine ${p.category.label} vorgesehen; Verkehr müsste sich verlagern oder abnehmen`);
  }
  return out;
}

/** Does the Soll fit? One answer: the detailed cycling Soll profile wins over the coarse street check. */
export function fitAnswer(p) {
  const pr = p.cycling?.profile;
  if (pr?.fit_text) {
    const steps = pr.steps?.length ? ` – mit ${pr.steps.length} Abstrich${pr.steps.length === 1 ? "" : "en"}` : "";
    return { ok: pr.fit === "fits" ? "ja" : pr.fit === "does_not_fit" ? "nein" : "knapp",
      text: `${pr.fit_text}${steps}: ${num(pr.required_m, 1)} m nötig, ${num(pr.available_m, 1)} m vorhanden` };
  }
  const cs = p.crosssection;
  if (cs.feasibility_text) return { ok: cs.feasibility === "fits" ? "ja" : cs.feasibility === "does_not_fit" ? "nein" : "knapp",
    text: `${cs.feasibility_text}: ${num(cs.required_m, 1)} m nötig, ${num(cs.width_p10_m, 1)} m an der engsten Stelle` };
  return { ok: "?", text: "Straßenraumbreite nicht gemessen" };
}

function certainty(p) {
  if (p.sensitivity?.uncertain) return ["unsicher", `Unsicher: ${p.sensitivity.uncertain_text ?? p.sensitivity.text}`];
  const lvl = p.confidence.level;
  const txt = { hoch: "Gute Datenlage", mittel: "Mittlere Datenlage: einzelne Werte sind Ersatz- oder Standardwerte", niedrig: "Lückenhafte Datenlage: ein entscheidender Wert fehlt oder liegt knapp an einer Grenze" }[lvl];
  return [lvl, `${txt}. ${p.sensitivity?.change_rate === 0 ? "Die Einstufung bleibt bei veränderten Annahmen gleich." : ""}`];
}

/** Schematic cross-section today from lanes and cycling facility (widths assumed, see constants). */
export function istElements(p) {
  const l = p.cycling?.lanes;
  const fi = p.cycling?.facility?.ist;
  const lanes = Number(l?.ist);
  if (!Number.isFinite(lanes) || lanes < 1) return null;
  const side = [{ element: "sidewalk", width_m: SIDEWALK_W }];
  if (fi === "separated_oneway_both") side.push({ element: "cycle_track", width_m: TRACK_W });
  if (fi === "cycle_lane") side.push({ element: "cycle_lane", width_m: 1.5 });
  const left = side, right = [...side].reverse();
  return [...left, { element: "carriageway", width_m: lanes * 2 * LANE_W }, ...right];
}

export function steckbriefHtml(p, meta, { compare = false, scenarioCat = null } = {}) {
  const c = p.category;
  const [needKey, needText] = NEED(p.discrepancy.priority);
  const ch = changes(p);
  const fit = fitAnswer(p);
  const [certKey, certText] = certainty(p);
  const label = (k) => meta.categories[k]?.label ?? k;
  const ist = istElements(p);
  const siteLink = `https://hamburgmobility.de/#karte?seg=${p.id}`;
  return `
  <header class="sb-head">
    <p class="sb-draft">Entwurf · nicht amtlich</p>
    <h2 id="panel-title">${esc(p.name ?? "Abschnitt ohne Namen")}</h2>
    <p class="muted">${esc(p.bezirk)} · ${num(p.length_m)} m</p>
  </header>
  <section class="sb-answer cat-border-${esc(c.code)}" aria-label="Kurzantwort">
    <p class="sb-kicker">Diese Straße soll sein</p>
    <p class="sb-cat">${esc(c.label)}</p>
    <p>${esc(c.text.split(" – ")[1] ?? c.text)}. Tempo: ${esc(SOLL_SPEED[c.code] ?? "–")}.</p>
    ${scenarioCat && scenarioCat !== c.code ? `<p class="sb-scen">Im Szenario „GOW50-Kompromiss“: <strong>${esc(label(scenarioCat))}</strong> (${esc(SOLL_SPEED[scenarioCat])}).</p>` : ""}
  </section>
  <section aria-labelledby="sb-h-change">
    <h3 id="sb-h-change">Was sich ändern soll</h3>
    ${ch.length ? `<ul class="sb-changes">${ch.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : "<p>Heute passt die Straße weitgehend zum Soll.</p>"}
    <p class="sb-row"><span class="pill pill-fit-${fit.ok === "ja" ? "ok" : fit.ok === "nein" ? "no" : "mid"}">Passt in den Straßenraum: ${esc(fit.ok)}</span> ${esc(fit.text)}</p>
    <p class="sb-row"><span class="pill pill-need-${needKey}">${esc(needText)}</span>
      ${p.discrepancy.crashes.ped_cyc ? `${num(p.discrepancy.crashes.ped_cyc)} Unfälle mit Fuß- oder Radbeteiligung (${esc(p.discrepancy.crashes.years)})` : "keine Unfälle mit Fuß- oder Radbeteiligung erfasst"}</p>
  </section>
  ${compare && p.cycling?.profile?.elements?.length ? `
  <section aria-labelledby="sb-h-xs">
    <h3 id="sb-h-xs">Querschnitt heute und Soll</h3>
    ${ist ? `<p class="sb-xs-label">Heute (schematisch: ${esc(String(p.cycling.lanes.ist))} Fahrstreifen je Richtung, ${esc(p.cycling.facility.ist_text ?? "keine Radanlage")}; Breiten angenommen)</p>${crossSectionSvg(ist, p.cycling.profile.available_m, meta)}` : "<p class=\"muted\">Heutiger Querschnitt: Fahrstreifenzahl unbekannt.</p>"}
    <p class="sb-xs-label">Soll</p>${crossSectionSvg(p.cycling.profile.elements, p.cycling.profile.available_m, meta)}
  </section>` : ""}
  <section aria-labelledby="sb-h-why">
    <h3 id="sb-h-why">Warum diese Einstufung?</h3>
    <ul>${p.reasons.map((r) => `<li class="${r.passed ? "" : "sb-notmet"}">${r.passed ? "" : "<span class=\"visually-hidden\">nicht erfüllt: </span>"}${esc(r.text)}</li>`).join("")}</ul>
    ${c.cascade ? `<p class="muted">An den Straßenzug angeglichen; die Regeln allein ergäben ${esc(label(c.cascade))}.</p>` : ""}
    ${c.corrected ? `<p class="note">Fachlich korrigiert: ${esc(c.override?.reason)}</p>` : ""}
    <p class="sb-row"><span class="pill pill-cert-${certKey}">${certKey === "unsicher" ? "unsicher" : `Datenlage ${certKey === "hoch" ? "gut" : certKey === "niedrig" ? "lückenhaft" : "mittel"}`}</span> ${esc(certText)}</p>
  </section>
  <details class="sb-more">
    <summary>Details, Messwerte und Quellen</summary>
    <dl>
      <dt>Tempo heute</dt><dd>${p.ist.speed_kmh != null ? `${num(p.ist.speed_kmh)} km/h (${esc(p.ist.speed_source)})` : "unbekannt"}</dd>
      <dt>Verkehrsmenge</dt><dd>${p.ist.dtv != null ? `${num(p.ist.dtv)} Kfz/Tag (${p.ist.dtv_year})` : "nur auf Hauptverkehrsstraßen erfasst"}</dd>
      <dt>Busfahrten je Werktag</dt><dd>${num(p.ist.bus_trips_weekday)}</dd>
      <dt>Straßenraum</dt><dd>${p.crosssection.width_p10_m != null ? `${num(p.crosssection.width_p10_m, 1)} m an der engsten Stelle, ${num(p.crosssection.width_median_m, 1)} m im Mittel` : "nicht gemessen"}</dd>
      <dt>Radnetz (Entwurf)</dt><dd>${esc(p.cycling?.cycle_cat?.label ?? "–")}</dd>
      <dt>Abweichung heute/Soll</dt><dd>${esc(p.discrepancy.text)}</dd>
    </dl>
    <details><summary>Regeln (für Fachleute)</summary>
      <ul class="rule-list">${p.reasons.map((r) => `<li><code>${esc(r.rule)}</code> ${r.passed ? "erfüllt" : "nicht erfüllt"}</li>`).join("")}</ul>
      <p class="muted">Regelwerk und Datenstand ${esc(p.version)} · Abschnitt <code>${esc(p.id)}</code></p>
    </details>
    <p class="muted">Quellen: ${p.sources.map((s) => esc(s.title)).join(" · ")}</p>
    <p><a href="${esc(siteLink)}" target="_blank" rel="noopener">Vollständiger Steckbrief auf hamburgmobility.de</a></p>
  </details>`;
}

export function junctionBriefHtml(j, meta) {
  const conflict = j.result?.code === "mismatch";
  return `
  <header class="sb-head">
    <p class="sb-draft">Entwurf · nicht amtlich</p>
    <h2 id="panel-title">${esc(j.names ?? "Kreuzung ohne Namen")}</h2>
    <p class="muted">Kreuzung · ${esc(j.bezirk ?? "–")}</p>
  </header>
  <section class="sb-answer" aria-label="Kurzantwort">
    <p class="sb-kicker">Diese Kreuzung soll werden</p>
    <p class="sb-cat">${esc(j.soll.text ?? "kein Vorschlag")}</p>
    <p>Heute: ${esc(j.ist.text ?? "unbekannt")}. ${conflict ? "<strong>Umbau nötig.</strong>" : "Passt bereits."}</p>
  </section>
  <section aria-labelledby="sb-h-jwhy">
    <h3 id="sb-h-jwhy">Warum?</h3>
    <p>Hier treffen ${j.legs.length} Straßenarme zusammen: ${j.legs.filter((l) => l.name).map((l) => `${esc(l.name)} (${esc(meta.categories[l.cat]?.label ?? "Radweg")})`).join(", ")}.
      ${j.entering_dtv != null ? `Zusammen fahren etwa ${num(j.entering_dtv)} Kfz am Tag hinein.` : ""}</p>
    <p>${esc(j.treatment ?? "")}</p>
    ${j.crashes?.cyc ? `<p>${num(j.crashes.cyc)} Unfälle mit Radbeteiligung in fünf Jahren${j.crashes.cyc_severe ? `, davon ${num(j.crashes.cyc_severe)} schwer` : ""}.</p>` : ""}
  </section>
  <details class="sb-more"><summary>Details und Regel</summary>
    <p>${esc(j.rule?.text ?? "")}</p>
    ${j.conflicts?.length ? `<ul>${j.conflicts.map((c) => `<li>${esc(c)}</li>`).join("")}</ul>` : ""}
    <p class="muted">Knoten <code>${esc(j.id)}</code> · ${esc(j.version)}</p>
  </details>`;
}
