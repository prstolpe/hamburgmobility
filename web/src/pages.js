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

/** Method page "Radnetz" in plain language (from docs/guide_radnetz.md). */
export function radnetzHtml(meta) {
  const c = meta.cycling;
  if (!c) return "<h1>Radnetz</h1><p>Die Radnetz-Ebenen sind in dieser Version noch nicht enthalten.</p>";
  const km = c.stats?.km_by_category ?? {};
  const cats = Object.entries(c.cycle_categories).map(([k, label]) => `<li><strong>${esc(label)}</strong> (${esc(k)})${km[k] != null ? `: ${num(km[k])} km im Entwurf` : ""}</li>`).join("");
  const sens = c.sensitivity?.runs ? `${num(c.sensitivity.runs)} Rechenläufe, jede Annahme einzeln um ${num(c.sensitivity.delta * 100)} % verändert` : null;
  return `
  <h1>Radnetz, Radanlagen und Knotenpunkte</h1>
  <p class="lead">Dieser Teil des Entwurfs legt ein Radnetz über den Straßenfunktionsplan. Er zeigt, wo Radrouten
  verlaufen sollten, welche Radanlage jede Straße braucht, wie viele Kfz-Fahrstreifen bleiben und wie Kreuzungen
  gestaltet sein sollten. Vorbild ist die Radverkehrsplanung in den Niederlanden.</p>
  <p class="note"><strong>Wichtig:</strong> ${esc(c.disclaimer)}. Das amtliche „Radnetz Hamburg“ der Stadt ist eine
  eigene Ebene auf der Karte – zum Vergleich.</p>

  <h2>Fünf Prinzipien</h2>
  <p>Ein gutes Radnetz erfüllt fünf Anforderungen. Sie stammen aus dem niederländischen Regelwerk (CROW) und werden
  im Entwurf je Route gemessen:</p>
  <div class="table-wrap" tabindex="0" role="region" aria-label="Fünf Prinzipien">
  <table><thead><tr><th scope="col">Prinzip</th><th scope="col">Worum es geht</th><th scope="col">Wie der Entwurf es misst</th></tr></thead><tbody>
    <tr><th scope="row">${esc(c.principles.cohesion)}</th><td>Ein lückenloses Netz verbindet alle wichtigen Ziele.</td><td>Maschenweite, zusammenhängende Netzteile, erreichte Ziele, durchgehende Führung</td></tr>
    <tr><th scope="row">${esc(c.principles.directness)}</th><td>Kurze Wege, wenige Umwege und Halte.</td><td>Umweg gegenüber der Luftlinie, Halte und Zeitverlust je km</td></tr>
    <tr><th scope="row">${esc(c.principles.safety)}</th><td>Getrennt vom schnellen Kfz-Verkehr, sichere Kreuzungen.</td><td>Radanlage passend zur Straße, Knotentyp, Beleuchtung, Unfälle</td></tr>
    <tr><th scope="row">${esc(c.principles.comfort)}</th><td>Genug Breite, glatter Belag, wenig Anhalten.</td><td>Breite, Belag (Steigung fehlt noch)</td></tr>
    <tr><th scope="row">${esc(c.principles.attractiveness)}</th><td>Grün und ruhig statt neben lauten Hauptstraßen.</td><td>Grünanteil, Abstand zu stark befahrenen Straßen (Lärm fehlt noch)</td></tr>
  </tbody></table></div>
  <p>Im Steckbrief eines Abschnitts stehen die Punkte heute und nach dem Umbau. Die Differenz zeigt, wie viel ein
  Umbau bringen würde.</p>

  <h2>Vier Ebenen des Radnetzes</h2>
  <ul>${cats}</ul>
  <p>So entsteht das Netz: Ein einfaches Verkehrsmodell schätzt, wie viele Menschen auf welcher Straße Rad fahren
  würden – von Wohnorten zu Arbeitsplätzen, Läden, Schulen, Hochschulen und Bahnhöfen. Das Modell ist an Hamburger
  Zählstellen angepasst. Stark genutzte Verbindungen zwischen Zentren werden Radschnellverbindung oder Radroute.
  Danach werden zu große Lücken im Netz geschlossen; Schulen und Nahversorgung werden angebunden. Das amtliche
  Radnetz bekommt einen Vorrang, ist aber nicht das Ziel. Alle übrigen befahrbaren Straßen und Wege bilden das
  Quartiersnetz.</p>

  <h2>Welche Radanlage?</h2>
  <p>Die Radanlage folgt aus zwei Fragen: Welche Aufgabe hat die Straße (Soll-Kategorie), und welche Ebene des
  Radnetzes liegt auf ihr? Vereinfacht:</p>
  <ul>
    <li><strong>Stadtmagistrale (Tempo 50):</strong> Radwege auf beiden Seiten, baulich von der Fahrbahn getrennt.</li>
    <li><strong>Stadtstraße 30:</strong> Radfahrstreifen; für Radrouten möglichst getrennte Radwege.</li>
    <li><strong>Quartiersstraße (Tempo 30):</strong> Radverkehr auf der Fahrbahn; Radrouten als Fahrradstraße, wenn
      wenig Autoverkehr fährt.</li>
  </ul>
  <p>Die Breite richtet sich nach der Netzebene und dem erwarteten Radverkehr. Im Steckbrief steht zum Vergleich das
  deutsche Regelmaß und der niederländische Wert für Hauptrouten. Die heutige Radanlage stammt aus OpenStreetMap;
  dort fehlt oft die Breite.</p>

  <h2>Passt das in die Straße?</h2>
  <p>Für jeden Abschnitt baut der Entwurf einen Soll-Querschnitt aus Bausteinen, in fester Reihenfolge: Gehwege,
  Radanlage, Bus und Bahn, Kfz-Fahrbahn, Sicherheitsabstände, Bäume, Ladezonen und zuletzt Parken. Kfz-Fahrstreifen
  gibt es so wenige wie möglich; ein zweiter nur bei rechnerischer Überlastung, und nie mehr als heute. Reicht der
  Platz nicht, macht der Entwurf schrittweise Abstriche: zuerst Parken, dann Bäume in Baumscheiben statt Baumstreifen,
  dann eine einfachere Radanlage, dann der zweite Fahrstreifen, dann Mindestbreiten. Hilft das nicht, schlägt er
  Einbahnverkehr, eine Durchfahrtssperre für Autos oder eine andere Route vor. Die Skizze im Steckbrief zeigt das
  Ergebnis maßstäblich.</p>

  <h2>Knotenpunkte</h2>
  <p>Kreuzungen sind die gefährlichsten Stellen. Der Entwurf wählt den Knotentyp nach den beteiligten Straßen,
  dem Autoverkehr und dem verfügbaren Platz:</p>
  <ul>
    <li><strong>Kreisverkehr</strong>, wo zwei Hauptstraßen sich kreuzen und Platz ist – er hat die wenigsten
      Konfliktpunkte. Ob Radfahrende im Kreisverkehr Vorrang haben, ist umstritten (niederländische Empfehlung gegen
      Unfallforschung und deutsches Recht); der Steckbrief nennt diesen Zielkonflikt.</li>
    <li><strong>Ampel</strong> nur bei sehr viel Verkehr oder Straßenbahn, dann geschützt gestaltet.</li>
    <li><strong>Durchgehender Gehweg</strong> oder <strong>Aufpflasterung</strong>, wo eine Quartiersstraße auf eine
      Hauptstraße trifft; <strong>rechts vor links</strong> zwischen Quartiersstraßen.</li>
    <li><strong>Brücke oder Tunnel</strong>, wo eine wichtige Radroute eine Schnellstraße oder sehr belastete Straße quert.</li>
  </ul>
  ${c.stats ? `<p>Im Entwurf: ${num(c.stats.n_junctions)} Knotenpunkte, davon ${num(c.stats.n_junctions_action)} mit Umbaubedarf.</p>` : ""}

  <h2>Wie sicher sind die Ergebnisse?</h2>
  <p>Viele Werte im Regelwerk sind Annahmen. Wir haben geprüft, wie stark die Ergebnisse an ihnen hängen${sens ? ` (${esc(sens)})` : ""}.
  Jeder Steckbrief sagt, ob sich Radanlage, Fahrstreifen oder Knotentyp dabei ändern. Außerdem vergleichen wir das
  Netz mit dem amtlichen Radnetz und mit den Zählstellen. Den vollständigen Bericht finden Sie im
  Projekt-Repository (reports/validation_cycling.md).</p>

  <h2>Grenzen</h2>
  <ul>
    <li>Radverkehrsstärken sind geschätzt, nicht gezählt. Das Modell trifft die Zählstellen nur mäßig.</li>
    <li>Autoverkehr ist nur auf Hauptverkehrsstraßen gezählt (Stand 2019). Wo Zahlen fehlen, nimmt der Entwurf an,
      dass eine Fahrradstraße möglich ist – das muss vor Ort geprüft werden.</li>
    <li>Heutige Radanlagen, Breiten und Kreuzungen stammen aus OpenStreetMap und sind dort nicht immer erfasst.</li>
    <li>Der Platz ist aus Katasterdaten geschätzt, nicht gemessen. Kreisverkehre und Ampeln brauchen eine genaue Planung.</li>
    <li>Viele Breiten und Schwellen stammen aus Sekundärquellen; die Neufassung der deutschen Radverkehrsrichtlinie
      (ERA) kann sie ändern.</li>
    <li>Der Entwurf ersetzt keine Planung. Er macht Netzlogik und Platzbedarf sichtbar.</li>
  </ul>
  <p>Regelwerke zum Nachlesen: <a href="#downloads">cycling_rules.yaml und design_rules.yaml</a>.
  Stand: Radnetz-Regeln ${esc(c.cycling_rules_version ?? "–")}, Querschnitt und Knoten ${esc(c.design_rules_version ?? "–")}.</p>`;
}

export function downloadsHtml(meta) {
  const rows = (meta.downloads ?? []).map((d) => `<tr><td><a href="downloads/${esc(d.file)}" download>${esc(d.file)}</a></td>
    <td>${esc(d.text)}</td><td>${num(d.bytes / 1e6, 1)} MB</td></tr>`).join("");
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
  Noto Sans (SIL Open Font License), Symbole nach tangrams/icons (MIT). Selbst gehostet.</p>`;
}
