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

// --- cycling (prompt 21) ----------------------------------------------------------------------

const PX_PER_M = 22;
const LIGHT_TEXT = new Set(["carriageway", "bus_lane", "cycle_track", "tree_strip", "tram"]);
const m1 = (v) => `${num(v, 1)} m`;
const m2 = (v) => `${num(v, 2)} m`;

/** Soll cross section to scale (port of pipeline/lib/profile.py profile_svg): one bar per element, required and
 * available width. Responsive (viewBox), with a text alternative in <title>. */
export function crossSectionSvg(elements, available, meta) {
  const shown = (elements ?? []).filter((e) => e.width_m > 0);
  if (!shown.length) return "";
  const total = shown.reduce((a, e) => a + e.width_m, 0);
  const span = Math.max(total, available ?? 0, 1);
  const margin = 8, top = 6, band = 84;
  const width = span * PX_PER_M + 2 * margin;
  const height = top + band + (available != null ? 62 : 36);
  const x0 = margin + ((span - total) * PX_PER_M) / 2;
  const el = meta.cycling?.elements ?? {};
  const title = `Soll-Querschnitt: ${shown.map((e) => `${el[e.element]?.label ?? e.element} ${num(e.width_m, 2)} m`).join(", ")}. `
    + `Soll-Bedarf ${num(total, 1)} m${available != null ? `, verfügbar ${num(available, 1)} m` : ""}.`;
  const id = `xs-${Math.random().toString(36).slice(2, 8)}`;
  const out = [`<figure class="sketch xs"><svg viewBox="0 0 ${width.toFixed(0)} ${height.toFixed(0)}" role="img" aria-labelledby="${id}" font-size="11">`,
    `<title id="${id}">${esc(title)}</title>`];
  let x = x0;
  for (const e of shown) {
    const w = e.width_m * PX_PER_M;
    const label = `${el[e.element]?.label ?? e.element} ${num(e.width_m, 1)}`;
    out.push(`<rect x="${x.toFixed(1)}" y="${top}" width="${w.toFixed(1)}" height="${band}" fill="${el[e.element]?.color ?? "#cccccc"}" stroke="#ffffff" stroke-width="1"/>`);
    const cx = x + w / 2, cy = top + band / 2;
    const fill = LIGHT_TEXT.has(e.element) ? "#ffffff" : "#222222";
    out.push(w >= 70
      ? `<text x="${cx.toFixed(1)}" y="${cy.toFixed(1)}" text-anchor="middle" dominant-baseline="middle" fill="${fill}">${esc(label)}</text>`
      : `<text transform="translate(${cx.toFixed(1)},${cy.toFixed(1)}) rotate(-90)" text-anchor="middle" dominant-baseline="middle" fill="${fill}" font-size="10">${esc(label)}</text>`);
    x += w;
  }
  const y = top + band + 12;
  out.push(`<line x1="${x0.toFixed(1)}" y1="${y}" x2="${(x0 + total * PX_PER_M).toFixed(1)}" y2="${y}" stroke="#222222" stroke-width="2"/>`);
  out.push(`<text x="${x0.toFixed(1)}" y="${y + 16}" fill="#222222">Soll-Bedarf ${num(total, 1)} m</text>`);
  if (available != null) {
    const ax = margin + ((span - available) * PX_PER_M) / 2;
    const y2 = y + 28;
    out.push(`<line x1="${ax.toFixed(1)}" y1="${y2}" x2="${(ax + available * PX_PER_M).toFixed(1)}" y2="${y2}" stroke="#1f6fb2" stroke-width="2" stroke-dasharray="6 3"/>`);
    out.push(`<text x="${ax.toFixed(1)}" y="${y2 + 16}" fill="#1f5f99">verfügbar ${num(available, 1)} m (Verkehrsfläche an Engstellen)</text>`);
  }
  out.push("</svg></figure>");
  return out.join("");
}

function principlesTable(pr, meta) {
  if (!pr) return "";
  const names = meta.cycling?.principles ?? {};
  const pts = (v) => (v == null ? "–" : num(v * 100));
  const rows = [...Object.keys(names), "score"].map((k) => `<tr><th scope="row">${k === "score" ? "<strong>gesamt (gewichtet)</strong>" : esc(names[k])}</th>
    <td>${pts(pr.ist?.[k])}</td><td>${pts(pr.soll?.[k])}</td></tr>`).join("");
  return `<div class="table-wrap"><table class="compact"><caption>Fünf Prinzipien, Punkte von 100 (Radroute ${esc(pr.category)} an diesem Abschnitt)</caption>
    <thead><tr><th scope="col">Prinzip</th><th scope="col">heute</th><th scope="col">nach Umbau (Soll)</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

function robustnessCycling(r, what) {
  if (!r || !r.n_runs) return "";
  const pct = num(r.delta * 100);
  const parts = what.map(([k, label]) => (r[k] ? `${label}: ${r[k]} von ${r.n_runs} Läufen` : null)).filter(Boolean);
  const trig = Object.values(r.triggers ?? {}).flat();
  return parts.length
    ? `<p>Wir haben jede Annahme einzeln um ${pct} % verändert. ${esc(parts.join("; "))} ändern das Ergebnis.</p>${trig.length ? `<ul>${trig.map((t) => `<li><code>${esc(t)}</code></li>`).join("")}</ul>` : ""}`
    : `<p>Robust: In allen ${r.n_runs} Rechenläufen mit einzeln um ${pct} % veränderten Annahmen bleibt das Ergebnis gleich.</p>`;
}

export function cyclingHtml(c, meta) {
  if (!c || !meta.cycling) return "";
  const f = c.facility, w = c.width, l = c.lanes, pr = c.profile;
  const widthText = w.soll_m != null
    ? `${m2(w.soll_m)}${w.de_m != null || w.nl_m != null ? ` (Vergleich: ${[w.de_m != null ? `DE-Regelmaß ${m2(w.de_m)}` : null, w.nl_m != null ? `NL-Hauptnetz ${m2(w.nl_m)}` : null].filter(Boolean).join(", ")})` : ""}`
    : null;
  const lanesText = l.soll ? `${l.soll === "shared" ? "keine Markierung" : esc(l.soll)} (heute ${l.ist ?? "unbekannt"})${l.change_text ? ` – ${esc(l.change_text)}` : ""}` : null;
  return `
  <section aria-labelledby="h-rad">
    <h3 id="h-rad">Radverkehr und Soll-Querschnitt</h3>
    <p class="note">${esc(meta.cycling.disclaimer)}</p>
    ${dl([
      ["Radnetz (Soll)", `${esc(c.cycle_cat.label)}${c.cycle_cat.code !== "none" ? ` (${esc(c.cycle_cat.code)})` : ""}`],
      ["Radanlage Soll", f.soll_text ? `${esc(f.soll_text)}${f.fallback_used ? " – Ersatzlösung, weil der Platz für die bevorzugte nicht reicht" : ""}` : "kein Soll"],
      ["Radanlage heute", f.ist_text ? `${esc(f.ist_text)}${f.osm_ist_text ? ` (OpenStreetMap: ${esc(f.osm_ist_text)})` : ""}` : null],
      ["Soll/Ist", f.gap_text ? esc(f.gap_text) : null],
      ["Breite Soll", widthText],
      ["Breite heute", w.ist_m != null ? m2(w.ist_m) : (f.soll && f.soll !== "mixed" ? "in OpenStreetMap nicht erfasst" : null)],
      ["Lage", c.side_text ? esc(c.side_text) : null],
      ["Kfz-Fahrstreifen je Richtung", lanesText],
      ["Busfahrstreifen", l.bus_lane ? "ja (Soll)" : null],
    ])}
    <h4>Soll-Querschnitt</h4>
    ${pr.fit_text ? `<p><strong>${esc(pr.fit_text)}</strong>${pr.required_m != null ? ` – Bedarf ${m1(pr.required_m)}` : ""}${pr.available_m != null ? `, verfügbar ${m1(pr.available_m)}` : ""}.</p>` : "<p>Kein Soll-Profil (Straßenkategorie ohne Profilregeln oder Breite nicht gemessen).</p>"}
    ${crossSectionSvg(pr.elements, pr.available_m, meta)}
    ${pr.steps.length ? `<p>Damit es passt, schlägt der Entwurf vor:</p><ol>${pr.steps.map((s) => `<li>${esc(s.text)} <span class="rule">(${esc(s.step)})</span></li>`).join("")}</ol>` : ""}
    ${pr.cat_change_proposal ? `<p class="note">Vorschlag: Straßenkategorie ${esc(pr.cat_change_proposal)} prüfen (Platz reicht nicht für die heutige Soll-Kategorie).</p>` : ""}
    ${c.flags.length ? `<h4>Hinweise</h4><ul>${c.flags.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : ""}
    ${principlesTable(c.principles, meta)}
    ${c.robustness ? `<h4>Robustheit</h4>${robustnessCycling(c.robustness, [["facility_changes", "Radanlage"], ["lanes_changes", "Fahrstreifen"]])}` : ""}
    <p class="muted">Datenunsicherheit: Radanlage ${esc(c.confidence.facility ?? "–")}, Querschnitt ${esc(c.confidence.profile ?? "–")}.</p>
  </section>`;
}

/** Junction profile ("Steckbrief Knoten"). */
export function junctionHtml(j, meta, pageUrl) {
  const legs = j.legs.map((leg) => `<li>${esc(leg.name ?? "ohne Namen")} – ${esc(leg.cat)}${leg.cycle_cat?.code && leg.cycle_cat.code !== "none" ? `, ${esc(leg.cycle_cat.label)}` : ""}${leg.facility_text ? `, ${esc(leg.facility_text)}` : ""}${leg.dtv != null ? `, ${num(leg.dtv)} Kfz/Tag` : ""}</li>`).join("");
  const corrected = j.override && j.proposed?.code !== j.soll.code;
  return `
  <header class="panel-head">
    <h2 id="panel-title">${esc(j.names ?? "Knotenpunkt ohne Namen")}</h2>
    <p class="muted">Knotenpunkt · ${esc(j.bezirk ?? "–")} · <code>${esc(j.id)}</code></p>
  </header>
  <p class="note">${esc(meta.cycling?.disclaimer ?? "Nicht amtlicher Entwurf")}</p>
  <section aria-labelledby="h-jsoll">
    <h3 id="h-jsoll">Soll-Knotentyp</h3>
    <p><strong>${esc(j.soll.text ?? "kein Soll-Typ (keine Regel passt)")}</strong></p>
    ${corrected ? `<p class="note">Fachlich korrigiert (Vorschlag der Automatik: ${esc(j.proposed.text)}): ${esc(j.override.reason)}</p>` : ""}
    ${j.rule ? `<p>${esc(j.rule.text)}.</p>` : ""}
    ${dl([["Zufluss Kfz", j.entering_dtv != null ? `${num(j.entering_dtv)} Kfz/Tag (geschätzt)` : "unbekannt"],
      ["Platz", j.space_radius_m != null ? `Kreis mit ${num(j.space_radius_m, 1)} m Radius in der Verkehrsfläche` : "unbekannt"],
      ["Straßenbahn", j.tram ? "ja" : null]])}
  </section>
  <section aria-labelledby="h-jist">
    <h3 id="h-jist">Heute</h3>
    ${dl([["Ist-Knotentyp (OpenStreetMap)", esc(j.ist.text ?? "–")], ["Vergleich", esc(j.result.text ?? "–")],
      ["Priorität", j.action_needed && j.priority_rank ? `Rang ${num(j.priority_rank)} unter den Knoten mit Umbaubedarf` : null],
      ["Unfälle mit Radbeteiligung", `${num(j.crashes.cyc)}${j.crashes.cyc_severe ? `, davon ${num(j.crashes.cyc_severe)} mit Getöteten/Schwerverletzten` : ""} (5 Jahre, Summe)`]])}
  </section>
  <section aria-labelledby="h-jrad">
    <h3 id="h-jrad">Radverkehrsführung</h3>
    <p>${esc(j.treatment ?? "Keine besondere Führung vorgesehen.")}</p>
  </section>
  ${j.conflicts.length ? `<section aria-labelledby="h-jcon"><h3 id="h-jcon">Zielkonflikte und Hinweise</h3><ul>${j.conflicts.map((c) => `<li>${esc(c)}</li>`).join("")}</ul></section>` : ""}
  <section aria-labelledby="h-jarm">
    <h3 id="h-jarm">Arme (${j.legs.length})</h3>
    <ul>${legs}</ul>
  </section>
  ${j.robustness ? `<section aria-labelledby="h-jrob"><h3 id="h-jrob">Robustheit</h3>${robustnessCycling(j.robustness, [["type_changes", "Knotentyp"]])}</section>` : ""}
  <p class="muted">Datenunsicherheit: ${esc(j.confidence.text ?? "–")} · Regelwerk und Datenstand: ${esc(j.version)} · <a href="${esc(pageUrl)}">Link zu diesem Knoten</a></p>`;
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
  ${cyclingHtml(p.cycling, meta)}
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
