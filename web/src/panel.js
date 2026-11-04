// Segment profile ("Steckbrief") as side panel / bottom sheet (guide 5.3).
import { issueUrl, mailtoUrl } from "./feedback.js";
import { esc, num, yesNo } from "./util.js";

const LIGHT = { hoch: "Ampel grün: hoch", mittel: "Ampel gelb: mittel", niedrig: "Ampel rot: niedrig" };

function sketch(cs) {
  // Bars to scale: available street space (p10) vs required width of the Soll category.
  if (cs.width_p10_m == null || cs.required_m == null) return "";
  const max = Math.max(cs.width_p10_m, cs.required_m) * 1.05;
  const w = (x) => ((x / max) * 260).toFixed(1);
  return `<figure class="sketch">
    <svg viewBox="0 0 300 62" role="img" aria-labelledby="sk-t">
      <title id="sk-t">Straßenraum ${num(cs.width_p10_m, 1)} m, nötig ${num(cs.required_m, 1)} m</title>
      <rect x="0" y="6" width="${w(cs.width_p10_m)}" height="18" fill="#0077BB"/>
      <text x="4" y="40" font-size="11">vorhanden ${num(cs.width_p10_m, 1)} m (Engstelle)</text>
      <rect x="0" y="44" width="${w(cs.required_m)}" height="6" fill="#333333"/>
      <text x="4" y="61" font-size="11">nötig ${num(cs.required_m, 1)} m</text>
    </svg></figure>`;
}

function robustness(s) {
  // Result of the sensitivity analysis (make validate): how often the category changes with other assumptions.
  if (!s) return "";
  const tag = s.uncertain ? '<strong class="tag-uncertain">unsicher</strong> ' : "";
  return `<h4>Robustheit der Einstufung</h4>
    <p>${tag}${esc(s.text)}</p>
    ${s.uncertain_text ? `<p class="note">${esc(s.uncertain_text)}</p>` : ""}
    ${s.triggers?.length ? `<p>${esc(s.oat_intro)}</p><ul>${s.triggers.map((t) => `<li>${esc(t)}</li>`).join("")}</ul>` : ""}`;
}

function dl(rows) {
  return `<dl>${rows.filter(([, v]) => v !== null && v !== undefined && v !== "")
    .map(([k, v]) => `<dt>${esc(k)}</dt><dd>${v}</dd>`).join("")}</dl>`;
}

export function profileHtml(p, meta, pageUrl) {
  const c = p.category;
  const d = p.discrepancy;
  const issue = issueUrl(meta.github_repo, p, pageUrl);
  const mail = mailtoUrl(meta.feedback_email, p, pageUrl);
  const reasons = p.reasons.map((r) => `<li>${esc(r.text)} <span class="rule">(${esc(r.rule)})</span></li>`).join("");
  const sev = (v) => (v === null ? "nicht prüfbar" : `${v} von 3`);
  return `
  <header class="panel-head">
    <h2 id="panel-title">${esc(p.name ?? "Abschnitt ohne Namen")}</h2>
    <p class="muted">${esc(p.bezirk)} · ${num(p.length_m)} m · <code>${esc(p.id)}</code></p>
  </header>
  <section aria-labelledby="h-soll">
    <h3 id="h-soll">Soll-Kategorie</h3>
    <p class="cat cat-${esc(c.code)}"><strong>${esc(c.label)}</strong> (${esc(c.code)})</p>
    <p>${esc(c.text)}</p>
    ${c.cascade ? `<p class="muted">An den Straßenzug angeglichen (Vorschlag der Regeln: ${esc(c.cascade)}).</p>` : ""}
    ${c.corrected ? `<p class="note">Fachlich korrigiert (Vorschlag der Automatik: ${esc(c.proposed)}): ${esc(c.override?.reason)}</p>` : ""}
  </section>
  <section aria-labelledby="h-why">
    <h3 id="h-why">Begründung</h3>
    <ul>${reasons}</ul>
  </section>
  <section aria-labelledby="h-conf">
    <h3 id="h-conf">Datenunsicherheit</h3>
    <p><span class="light light-${esc(p.confidence.level)}" aria-hidden="true"></span> ${esc(LIGHT[p.confidence.level] ?? p.confidence.level)}.
      ${esc(p.confidence.summary)}</p>
    ${p.confidence.reasons.length ? `<ul>${p.confidence.reasons.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>` : ""}
    ${robustness(p.sensitivity)}
  </section>
  <section aria-labelledby="h-ist">
    <h3 id="h-ist">Ist-Zustand</h3>
    ${dl([
      ["Tempo", p.ist.speed_kmh != null ? `${num(p.ist.speed_kmh)} km/h (${esc(p.ist.speed_source)})` : "unbekannt"],
      ["Radverkehr", esc(p.ist.cycling)],
      ["Busfahrten je Werktag", num(p.ist.bus_trips_weekday)],
      ["Verkehrsmenge", p.ist.dtv != null ? `${num(p.ist.dtv)} Kfz/Tag (${p.ist.dtv_year})` : "nur auf Hauptverkehrsstraßen erfasst"],
      ["Hauptverkehrsstraße", yesNo(p.ist.in_hvs)],
      ["Radnetz", yesNo(p.ist.in_cycle_network)],
    ])}
  </section>
  <section aria-labelledby="h-qs">
    <h3 id="h-qs">Querschnitt</h3>
    ${p.crosssection.width_p10_m == null ? "<p>Straßenraumbreite nicht gemessen.</p>" : dl([
      ["Straßenraum (Median)", `${num(p.crosssection.width_median_m, 1)} m`],
      ["Straßenraum an Engstellen", `${num(p.crosssection.width_p10_m, 1)} m`],
      ["nötig für die Soll-Kategorie", p.crosssection.required_m != null ? `${num(p.crosssection.required_m, 1)} m` : null],
      ["Machbarkeit", p.crosssection.feasibility_text ? esc(p.crosssection.feasibility_text) : null],
    ])}
    ${sketch(p.crosssection)}
  </section>
  <section aria-labelledby="h-disc">
    <h3 id="h-disc">Diskrepanz und Priorität</h3>
    ${dl([
      ["Typ", d.type ? `${esc(d.type)} – ${esc(d.type_text)}` : (d.max === null ? "nicht prüfbar" : "keine Diskrepanz")],
      ["Tempo", sev(d.speed)], ["Gestaltung", sev(d.design)], ["Nutzung", sev(d.use)],
      ["Unfälle mit Fuß-/Radbeteiligung", `${num(d.crashes.ped_cyc)} in ${esc(d.crashes.years)}${d.crashes.severe_fatal ? `, davon ${num(d.crashes.severe_fatal)} mit Getöteten/Schwerverletzten` : ""}`],
      ["Priorität", d.priority != null ? `${num(d.priority, 2)} von 3` : "–"],
    ])}
    <p>${esc(d.text)}.</p>
    ${d.unknown_checks.length ? `<p class="muted">Nicht prüfbar (Merkmal in OpenStreetMap nicht erfasst): ${esc(d.unknown_checks.join(", "))}</p>` : ""}
  </section>
  ${p.coherence.length ? `<section aria-labelledby="h-net"><h3 id="h-net">Hinweise der Netzprüfung</h3><ul>${p.coherence.map((f) => `<li>${esc(f.text)} (${esc(f.rule)})</li>`).join("")}</ul></section>` : ""}
  <section aria-labelledby="h-src">
    <h3 id="h-src">Datenquellen</h3>
    <ul class="sources">${p.sources.map((s) => `<li><strong>${esc(s.title)}</strong> – ${esc(s.purpose)}. Stand ${esc(s.as_of)}; ${esc(s.license)}</li>`).join("")}</ul>
    <p class="muted">Regelwerk und Datenstand: ${esc(p.version)}</p>
  </section>
  <section aria-labelledby="h-fb">
    <h3 id="h-fb">Rückmeldung zu diesem Abschnitt</h3>
    ${issue || mail ? `<p class="actions">
      ${issue ? `<a class="button" href="${esc(issue)}" target="_blank" rel="noopener">Rückmeldung auf GitHub</a>` : ""}
      ${mail ? `<a class="button secondary" href="${esc(mail)}">Rückmeldung per E-Mail</a>` : ""}</p>
      <p class="muted">Rückmeldungen werden fachlich geprüft; sie ändern die Karte nicht automatisch.</p>`
      : "<p class=\"muted\">Der Rückmeldekanal wird noch eingerichtet.</p>"}
  </section>`;
}
