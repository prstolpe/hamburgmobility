// Text pages: method (plain language), downloads, sources & licences, imprint (guide 5.5).
import { marked } from "marked";
import { CATEGORY_STYLE } from "./palette.js";
import { esc, num } from "./util.js";

async function text(url) {
  const r = await fetch(url);
  return r.ok ? r.text() : "";
}

export function methodHtml(meta, changelog) {
  const cats = Object.entries(meta.categories).filter(([k]) => CATEGORY_STYLE[k]);
  return `
  <h1>So funktioniert der Entwurf</h1>
  <p class="lead">Dieser Entwurf ordnet jeder Straße in ${esc(meta.area_label)} eine Aufgabe zu: Soll sie Verkehr
  verbinden, oder soll sie ein Quartier erschließen? Daraus folgt, wie schnell gefahren werden soll und wie die Straße
  gestaltet sein sollte. Die Idee kommt aus den Niederlanden und heißt „Duurzaam Veilig“ (nachhaltig sicher).</p>
  <p><strong>Wichtig:</strong> Das ist ein Vorschlag zur Diskussion. Die Stadt Hamburg hat ihn nicht beschlossen.
  Ein Computerprogramm macht den ersten Vorschlag. Menschen prüfen ihn und korrigieren ihn, wenn nötig.</p>

  <h2>Die fünf Kategorien</h2>
  <ul class="cat-list">${cats.map(([k, c]) => `<li><strong>${esc(c.label)}</strong> (${esc(k)}): ${esc(c.text.split(" – ")[1] ?? c.text)}</li>`).join("")}</ul>

  <h2>Wie die Kategorie entsteht</h2>
  <ol>
    <li>Ist die Straße eine Autobahn oder Kraftfahrstraße? Dann ist sie eine <em>Schnellverkehrsstraße</em>.</li>
    <li>Ist sie heute schon ein verkehrsberuhigter Bereich oder eine Fußgängerzone? Dann ist sie eine <em>Aufenthaltsstraße</em>.</li>
    <li>Verbindet sie wichtige Orte (hoher Verbindungswert oder Hauptverkehrsstraße)? Dann ist sie eine Verbindungsstraße.
      <ul>
        <li>Liegt eine Schule oder Kita in der Nähe, oder gibt es viele Läden? Oder ist kein Platz für einen eigenen Radweg?
          Dann soll dort Tempo 30 gelten: <em>Stadtstraße 30</em>.</li>
        <li>Sonst bleibt sie eine <em>Stadtmagistrale</em> mit Tempo 50 und eigenem Radweg.</li>
      </ul></li>
    <li>Alle anderen Straßen erschließen das Quartier: <em>Quartiersstraße</em> mit Tempo 30.</li>
  </ol>
  <p>Danach wird jeder Straßenzug geglättet: Kurze Stücke unter 200 m, die anders eingestuft sind als die Straße davor
  und dahinter, werden angeglichen. Treffen Tempo 50 und Tempo 30 aufeinander, gewinnt Tempo 30. So wechselt die
  Kategorie nicht alle paar Meter.</p>
  <p>Eingestuft werden Straßen für den Kfz-Verkehr und benannte Zufahrten. Fußwege, Wege in Parks und
  Kleingärten sowie Parkplatzgassen haben keine Kategorie, auch wenn die Hintergrundkarte ihren Namen zeigt.</p>
  <p>Jeder Steckbrief zeigt, welche Regeln gegriffen haben und mit welchen Werten. Die Regeln und alle Schwellenwerte
  stehen im <a href="#downloads">Regelwerk (rules.yaml)</a>.</p>

  <h2>Wie sicher ist die Einstufung?</h2>
  <p>Zwei Hinweise im Steckbrief helfen beim Einordnen. Die <strong>Datenunsicherheit</strong> (Ampel) zeigt, ob
  entscheidende Werte fehlen, aus einer Ersatzquelle stammen oder nahe an einer Schwelle liegen. Die
  <strong>Robustheit</strong> zeigt, wie stark die Kategorie an gesetzten Annahmen hängt: Wir rechnen den Entwurf
  ${meta.sensitivity ? esc(String(meta.sensitivity.runs)) : "viele"}-mal mit zufällig veränderten Schwellen und Gewichten
  (jeweils bis zu ${meta.sensitivity ? num(meta.sensitivity.delta * 100) : "20"} % mehr oder weniger). Wechselt die
  Kategorie in mindestens ${meta.sensitivity ? num(meta.sensitivity.min_change_rate * 100) : "30"} % der Läufe, ist der
  Abschnitt als <em>unsicher</em> markiert und sollte fachlich geprüft werden.</p>

  <h2>Diskrepanz: wo Soll und Ist nicht zusammenpassen</h2>
  <p>Wir vergleichen die Soll-Kategorie mit dem heutigen Zustand: dem Tempolimit, der Gestaltung (zum Beispiel
  Radweg, Mittelstreifen, Parken) und der Verkehrsmenge. Passt etwas nicht, ist die Straße eine „graue Straße“.
  Die Priorität verbindet die Stärke der Diskrepanz mit dem Risiko: Unfälle mit Fuß- oder Radbeteiligung, Radnetz,
  Einwohner und Schulen oder Kitas in der Nähe.</p>

  <h2>Grenzen</h2>
  <ul>
    <li>Viele Gestaltungsmerkmale stammen aus OpenStreetMap und fehlen dort oft. Fehlende Angaben zählen als „unbekannt“.</li>
    <li>Verkehrsmengen gibt es nur für Hauptverkehrsstraßen und nur bis 2019.</li>
    <li>Unfälle: nur polizeilich erfasste Unfälle mit Personenschaden. Wir zeigen nur Summen je Abschnitt.</li>
    <li>Die Straßenraumbreite ist aus Katasterdaten geschätzt, nicht vor Ort gemessen.</li>
    <li>Gewichte und viele Schwellen sind Annahmen. Sie sind im Regelwerk gekennzeichnet und werden fachlich geprüft.</li>
  </ul>

  <h2>Änderungen</h2>
  <p>Aktuelle Version: ${esc(meta.version)} (Regelwerk ${esc(meta.rules_version)}, Datenstand ${esc(meta.data_date)}).</p>
  <details><summary>Änderungshistorie anzeigen</summary><div class="md">${marked.parse(changelog)}</div></details>`;
}

export function downloadsHtml(meta) {
  const rows = (meta.downloads ?? []).map((d) => `<tr><td><a href="downloads/${esc(d.file)}" download>${esc(d.file)}</a></td>
    <td>${esc(d.text)}</td><td>${num(d.bytes / 1e6, 1)} MB</td></tr>`).join("");
  return `
  <h1>Daten herunterladen</h1>
  <p>Alle Abschnitte in ${esc(meta.area_label)} (${num(meta.n_segments)} Abschnitte), Version ${esc(meta.version)}.
  Koordinaten in WGS 84. Lizenz des Abschnittsdatensatzes: ODbL 1.0. Quellenvermerke auf der
  <a href="#quellen">Quellenseite</a>.</p>
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
  Noto Sans (SIL Open Font License), Symbole nach tangrams/icons (MIT). Selbst gehostet.</p>`;
}
