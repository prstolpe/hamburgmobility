// Page "Besondere Orte" (prompts/26): one card per place from meta.special_places, in three levels –
// level 1 one sentence, status and date; level 2 what is proposed and why; level 3 sources and the comparison with
// the rule result. New places come from config/special_places.yaml only; this file has no place-specific text.
import { esc, num } from "./util.js";

const dateDe = (iso) => new Date(iso).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" });

function placeCard(p) {
  const measures = p.measures.map((m) => `<li><strong>${esc(m.label)}:</strong> ${esc(m.streets.join(", "))}
    <span class="muted">(${num(m.km, 1)} km)</span></li>`).join("");
  const compare = p.measures.map((m) => `<h4>${esc(m.label)}</h4><ul>${m.compare.map((c) =>
    `<li>${esc(c.text)} <span class="muted">(${num(c.n)} ${c.n === 1 ? "Abschnitt" : "Abschnitte"})</span></li>`).join("")}</ul>`).join("");
  return `<article class="place-card" aria-labelledby="place-${esc(p.id)}" style="--place:${esc(p.theme.palette.main)}">
    <p class="meta">${esc(p.kind_plain)} · ${esc(p.initiator)}</p>
    <h2 id="place-${esc(p.id)}">${esc(p.title)}</h2>
    <p class="lead">${esc(p.texts.glance)}</p>
    <p><strong>Stand ${esc(dateDe(p.status_date))}:</strong> ${esc(p.status)}.${p.status_note ? ` ${esc(p.status_note)}` : ""}</p>
    <p><button type="button" data-show-place="${esc(p.id)}">Auf der Karte zeigen</button></p>
    <details class="level l2"><summary>Was wird vorgeschlagen?</summary>
      <p>${esc(p.texts.explain)}</p>
      <ul>${measures}</ul>
      ${p.exceptions?.length ? `<p>Ausnahmen laut Vorschlag:</p><ul>${p.exceptions.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : ""}
    </details>
    <details class="level l3"><summary>Quellen und Vergleich mit unserem Regelwerk</summary>
      <p>${esc(p.texts.details)}</p>
      <h3>Vergleich je Straßenabschnitt</h3>
      ${compare}
      <h3>Quellen</h3>
      <ul>${p.sources.map((s) => `<li><a href="${esc(s.url)}" rel="noopener" target="_blank">${esc(s.title)}<span class="visually-hidden"> (öffnet in neuem Tab)</span></a></li>`).join("")}</ul>
    </details>
  </article>`;
}

export function placesHtml(meta) {
  const sp = meta.special_places;
  if (!sp?.places?.length) return "<h1>Besondere Orte</h1><p>In diesem Datenstand gibt es keine besonderen Orte.</p>";
  return `<h1>${esc(sp.texts.page_title)}</h1><p class="lead">${esc(sp.texts.page_intro)}</p>${sp.places.map(placeCard).join("")}`;
}
