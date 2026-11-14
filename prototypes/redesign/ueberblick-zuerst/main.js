// Variant B "Überblick zuerst" (prompt 24, A3): the Bezirk overview is the start. Level 1: one sentence and three key
// figures (one per theme); level 2: three top-5 lists; level 3: all Bezirke as a table. Every entry opens the map
// with the profile (same map view as variant A).
import { esc } from "../../../web/src/util.js";
import { bindSearch, loadData, mountMapView } from "../shared/mapview.js";

const { meta, district, search } = await loadData();
const bz = district.focus;
const k = district.per_bezirk[bz];
const de = (v, d = 0) => Number(v).toLocaleString("de-DE", { minimumFractionDigits: d, maximumFractionDigits: d });
document.querySelector("#datestand").textContent = `Datenstand ${new Date(meta.data_date).toLocaleDateString("de-DE")}`;

const list = (items, kind) => `<ol class="toplist">${items.map((x, i) =>
  `<li><button type="button" data-kind="${kind}" data-i="${i}">${esc(x.name)}</button><p>${esc(x.sentence)}</p></li>`).join("")}</ol>`;
const rows = Object.entries(district.per_bezirk).map(([name, v]) => `<tr${name === bz ? ' style="font-weight:700"' : ""}>
  <th scope="row">${esc(name)}</th><td class="n">${de(v.km_total)}</td><td class="n">${de(v.km_need)}</td><td class="n">${de(v.km_profile_no_fit)}</td>
  <td class="n">${de(v.km_cycle_missing)}</td><td class="n">${de(v.junctions_rebuild)}</td></tr>`).join("");

document.querySelector("#overview").innerHTML = `
  <div class="intro-l1">
    <h1 id="h-bz">${esc(bz)}</h1>
    <p>Auf ${de(k.km_need)} von ${de(k.km_total)} km Straße passt der heutige Zustand nicht zur Aufgabe der Straße.
      ${de(k.junctions_rebuild)} Kreuzungen brauchen einen Umbau.</p>
  </div>
  <div class="bz-pick"><label for="bz">Bezirk</label><select id="bz">${Object.keys(district.per_bezirk).map((n) =>
    `<option ${n === bz ? "selected" : "disabled"}>${esc(n)}${n === bz ? "" : " (im Prototyp nicht verfügbar)"}</option>`).join("")}</select></div>
  <div class="kpis" role="list">
    <div role="listitem"><p class="t-display">${de(k.km_need)} km</p><p class="t-small">Straßen mit großer Abweichung zwischen heute und Ziel</p></div>
    <div role="listitem"><p class="t-display">${de(k.junctions_rebuild)}</p><p class="t-small">Kreuzungen, die umgebaut werden müssten</p></div>
    <div role="listitem"><p class="t-display">${de(k.km_cycle_missing)} km</p><p class="t-small">Radnetz ohne passenden Radweg</p></div>
  </div>
  <details class="level l2" open><summary>Wo ist der Handlungsbedarf am größten?</summary>
    <div class="lists">
      <section><h2>Straßen</h2>${list(district.top.streets, "streets")}</section>
      <section><h2>Kreuzungen</h2>${list(district.top.junctions, "junctions")}</section>
      <section><h2>Radnetz-Lücken</h2>${list(district.top.gaps, "gaps")}</section>
    </div>
    <p class="t-small muted" style="margin-top:16px">Straßen nach Dringlichkeit (Abweichung und Unfälle, Schulen, Radverkehr), Kreuzungen nach Rang beim Umbaubedarf,
      Lücken nach Länge mal Radverkehr (Modell). Alle Werte aus dem Entwurf, nicht amtlich.</p>
  </details>
  <div class="actions"><button type="button" class="btn" id="open-map">Karte von ${esc(bz)} öffnen</button></div>
  <details class="level l3"><summary>Details und Quellen: alle Bezirke im Vergleich</summary>
    <table class="data"><caption class="visually-hidden">Kennzahlen je Bezirk</caption>
      <thead><tr><th scope="col">Bezirk</th><th scope="col" class="n">Straßen km</th><th scope="col" class="n">große Abweichung km</th>
        <th scope="col" class="n">Ziel passt nicht km</th><th scope="col" class="n">Radnetz ohne Radweg km</th><th scope="col" class="n">Kreuzungen mit Umbau</th></tr></thead>
      <tbody>${rows}</tbody></table>
    <p class="t-small muted" style="margin-top:8px">Quelle: ${esc(district.source)}. Alle Abschnitte als Tabelle (heute Seite „Tabelle“) stünden hier.</p>
  </details>`;

let view = null;
function openMap(theme) {
  document.body.classList.add("map-open");
  if (!view) view = mountMapView(document.querySelector("#mapview"), { meta, district, page: "#bezirke/Eimsbüttel" });
  if (theme) view.setTheme(theme);
  view.map.map.resize();
  return view;
}
document.querySelector("#open-map").addEventListener("click", () => openMap("abweichung"));
document.querySelector("#back").addEventListener("click", () => { document.body.classList.remove("map-open"); history.replaceState(null, "", "#bezirke/Eimsbüttel"); });
document.querySelector("#overview").addEventListener("click", (ev) => {
  const b = ev.target.closest("button[data-kind]");
  if (!b) return;
  const x = district.top[b.dataset.kind][Number(b.dataset.i)];
  if (b.dataset.kind === "junctions") openMap("knoten").openJunction(x.id, { fly: true, at: x.at });
  else openMap(b.dataset.kind === "gaps" ? "rad" : "abweichung").openSegment(x.id, { fly: true, at: x.at });
  if (b.dataset.kind === "gaps") view.setTheme("rad", "luecken");
});
bindSearch(document.querySelector("#q"), document.querySelector("#q-list"), search, (h) => {
  const [w, s, e, n] = h.bbox;
  openMap().openSegment(h.ids[0], { fly: true, at: [(w + e) / 2, (s + n) / 2] });
});
window.proto = { get view() { return view; }, openMap, meta, district };
