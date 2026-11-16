// Text pages: method (plain language), downloads, sources & licences, imprint (guide 5.5).
import { marked } from "marked";
import { esc, num } from "./util.js";

async function text(url) {
  const r = await fetch(url);
  return r.ok ? r.text() : "";
}

export function downloadsHtml(meta) {
  const rows = (meta.downloads ?? []).map((d) => `<tr><td><a href="downloads/${esc(d.file)}" download>${esc(d.file)}</a></td>
    <td>${esc(d.text)}</td><td>${num(d.bytes / 1e6, 1)}&nbsp;MB</td></tr>`).join("");
  return `
  <h1>Daten herunterladen</h1>
  <p>Alle Abschnitte in ${esc(meta.area_label)} (${num(meta.n_segments)} Abschnitte), Version ${esc(meta.version)}.
  Koordinaten in WGS 84. Lizenz des Abschnittsdatensatzes: ODbL 1.0. Quellenvermerke auf der
  <a href="#quellen">Quellenseite</a>.</p>
  ${meta.cycling ? `<p>Radnetz, Querschnitt und Knotenpunkte: nicht amtlicher Entwurf, ODbL 1.0; der Vergleich mit dem
  amtlichen Radnetz nutzt ${esc(meta.cycling.official_attribution)}. Spalten erklärt die Datenbeschreibung.</p>` : ""}
  <table><caption>Dateien</caption><thead><tr><th scope="col">Datei</th><th scope="col">Inhalt</th><th scope="col">Größe</th></tr></thead>
  <tbody>${rows}</tbody></table>`;
}

export async function sourcesHtml(meta) {
  const licenses = await text("licenses.md");
  const src = meta.sources.map((s) => `<tr><td>${esc(s.title)}</td><td>${esc(s.purpose)}</td><td>${esc(s.as_of)}</td>
    <td>${esc(s.license)}</td><td>${esc(s.attribution ?? "–")}</td></tr>`).join("");
  const bm = Object.values(meta.basemap).map((b) => `<li>${esc(b.title)} – ${esc(b.license)}${b.attribution ? ` (${esc(b.attribution)})` : ""}</li>`).join("");
  return `
  <h1>Quellen und Lizenzen</h1>
  <h2>Datenquellen</h2>
  <div class="table-wrap" tabindex="0" role="region" aria-label="Datenquellen">
  <table><thead><tr><th scope="col">Quelle</th><th scope="col">wofür</th><th scope="col">Stand</th><th scope="col">Lizenz</th><th scope="col">Quellenvermerk</th></tr></thead>
  <tbody>${src}</tbody></table></div>
  <h2>Hintergrundkarte und Schriften</h2><ul>${bm}</ul>
  <div class="md">${marked.parse(licenses)}</div>`;
}

export function imprintHtml(meta) {
  return `
  <h1>Impressum und Datenschutz</h1>
  <p><strong>${esc(meta.disclaimer)}.</strong> Keine Behördenseite.</p>
  <h2>Verantwortlich</h2>
  ${meta.imprint?.name
    ? `<p>${esc(meta.imprint.name)}<br>${(meta.imprint.address ?? []).map(esc).join("<br>")}</p>
  ${meta.imprint.email ? `<p>E-Mail: <a href="mailto:${esc(meta.imprint.email)}">${esc(meta.imprint.email)}</a></p>` : ""}`
    : "<p>Wird vom Projektteam vor der Veröffentlichung eingetragen.</p>"}
  <h2>Datenschutz</h2>
  <ul>
    <li>Kein Tracking, keine Cookies, keine Analysewerkzeuge.</li>
    <li>Karte, Hintergrundkarte und Schriften liegen auf demselben Server wie diese Seite. Es werden keine Daten an
      Kartendienste Dritter übertragen.</li>
    <li>Der Hostinganbieter (GitHub Pages) speichert technisch notwendige Zugriffsdaten (z. B. IP-Adresse) in Server-Protokollen.</li>
    <li>Rückmeldungen über GitHub oder E-Mail sind freiwillig; es gelten die Bedingungen des jeweiligen Dienstes.</li>
  </ul>
  <h2>Hintergrundkarte</h2>
  <p>Protomaps Basemap aus OpenStreetMap-Daten (ODbL), Kartenstil @protomaps/basemaps (BSD-3-Clause), Schrift
  Noto Sans (SIL Open Font License), Symbole nach tangrams/icons (MIT). Selbst gehostet.</p>
  <h2>Schrift</h2>
  <p>Inter (SIL Open Font License 1.1, © The Inter Project Authors). Selbst gehostet, ohne Schriftdienst.</p>`;
}
