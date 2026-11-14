// Page "Methode" (redesign 2026-11, package 3): summary, chapters, rule reference, news.
// Three levels: L1 at a glance, L2 explanation, L3 "Details und Quellen". Pure functions returning HTML strings.
import { marked } from "marked";
import { esc, num } from "./util.js";

export const SOURCE_TYPE_TEXT = {
  assumption: "Annahme (vom Projekt gesetzt, ohne veröffentlichte Quelle)",
  swov_crow: "niederländische Quelle (SWOV/CROW)",
  de_regelwerk: "deutsches Regelwerk",
  hamburg: "Hamburger Vorgabe",
};
export const sourceTypeText = (t) => SOURCE_TYPE_TEXT[t] ?? t ?? "–";

const STATUS_TEXT = { draft: "Entwurf", reviewed: "geprüft", approved: "freigegeben", inactive: "nicht aktiv" };

// --- placeholders {name} -> vars[name] ------------------------------------------------------

function varText(v) {
  if (v === null || v === undefined) return "–";
  return typeof v === "number" ? num(v, Number.isInteger(v) ? 0 : 1) : String(v);
}

/** Replaces {name} with vars[name]; returns plain text (not escaped). */
export function fill(text, vars = {}) {
  return String(text ?? "").replace(/\{([A-Za-z0-9_]+)\}/g, (_, k) => varText(vars[k]));
}
const plain = (text, vars) => esc(fill(text, vars));

/** Markdown with placeholders filled first; tables get the scroll wrapper. */
export function mdHtml(text, vars = {}) {
  const filled = String(text ?? "").replace(/\{([A-Za-z0-9_]+)\}/g, (_, k) => esc(varText(vars[k])));
  return marked.parse(filled)
    .replaceAll("<table>", '<div class="table-wrap" tabindex="0" role="region" aria-label="Tabelle"><table>')
    .replaceAll("</table>", "</table></div>");
}

const chapters = (method) => method.chapters ?? [];

// --- summary -----------------------------------------------------------------------------------

const pointList = (items, vars) => `<ul class="plain points">${(items ?? []).map((i) =>
  `<li><strong>${plain(i.title, vars)}</strong><p>${plain(i.text, vars)}</p></li>`).join("")}</ul>`;

export function summaryHtml(method, meta = {}) {
  const s = method.summary ?? {};
  const v = method.vars ?? {};
  return `
  <h1>${plain(method.title, v)}</h1>
  ${meta.disclaimer ? `<p class="note"><strong>Wichtig:</strong> ${esc(meta.disclaimer)}.</p>` : ""}
  <section aria-labelledby="m-what"><h2 id="m-what">${plain(s.what_title, v)}</h2><p class="lead">${plain(s.what, v)}</p></section>
  <section aria-labelledby="m-shows"><h2 id="m-shows">${plain(s.shows_title, v)}</h2>${pointList(s.shows, v)}</section>
  <section aria-labelledby="m-not"><h2 id="m-not">${plain(s.not_title, v)}</h2>${pointList(s.not, v)}</section>
  ${s.assumptions ? `<p>${plain(s.assumptions, v)}</p>` : ""}
  <section aria-labelledby="m-chapters"><h2 id="m-chapters">Die Kapitel</h2>
    <ol class="chapter-list">${chapters(method).map((c) => `<li><a href="#methode/${esc(c.key)}"><strong>${plain(c.title, v)}</strong></a>
      <p>${plain(c.l1, v)}</p></li>`).join("")}</ol></section>
  <p class="method-links"><a href="#methode/regeln">Alle Regeln</a> · <a href="#methode/neu">Was ist neu</a></p>`;
}

// --- rule details (level 3) ----------------------------------------------------------------

function valueText(v) {
  if (v === null || v === undefined) return "–";
  if (typeof v === "number") return v.toLocaleString("de-DE", { maximumFractionDigits: 3 });
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

export function ruleDetailsHtml(rule, repo = null) {
  const src = rule.source ?? [];
  const th = rule.thresholds ?? [];
  const tech = rule.technical ?? [];
  const d = rule.decides;
  return `
    ${rule.why ? `<h4>Warum?</h4><p>${esc(rule.why)}</p>` : ""}
    <p class="t-small">Regel <code>${esc(rule.id)}</code>${rule.aliases?.length ? ` (früher auch ${rule.aliases.map((x) => `<code>${esc(x)}</code>`).join(", ")})` : ""} · Datei ${esc(rule.file)}, Abschnitt ${esc(rule.section)} · Status: ${esc(STATUS_TEXT[rule.status] ?? rule.status)}</p>
    <p class="t-small">Art der Quelle: ${esc(sourceTypeText(rule.source_type))}</p>
    ${src.length ? `<h4>Quellen</h4><ul class="t-small sources">${src.map((s) => {
      const label = `${esc(s.title ?? s.key)}${s.date ? ` (${esc(s.date)})` : ""}`;
      return `<li>${s.url ? `<a href="${esc(s.url)}" rel="noopener">${label}</a>` : label}</li>`;
    }).join("")}</ul>` : ""}
    ${th.length ? `<h4>Werte</h4><div class="table-wrap" tabindex="0" role="region" aria-label="Werte der Regel ${esc(rule.id)}"><table class="t-small">
      <thead><tr><th scope="col">Wert</th><th scope="col">Größe</th><th scope="col">Prüfung</th></tr></thead><tbody>${th.map((t) => `<tr>
        <th scope="row">${esc(t.label_plain ?? t.key)}<br><code>${esc(t.key)}</code></th>
        <td>${esc(valueText(t.value))}${t.unit ? ` ${esc(t.unit)}` : ""}${t.source_type === "assumption" ? ' <span class="tag">Annahme</span>' : ""}</td>
        <td>${esc(t.check ?? "–")}</td></tr>`).join("")}</tbody></table></div>` : ""}
    ${rule.description || rule.note || tech.length ? `<h4>Technisch</h4>
      ${rule.description ? `<p class="t-small">${esc(rule.description)}</p>` : ""}
      ${rule.note ? `<p class="t-small">${esc(rule.note)}</p>` : ""}
      ${tech.length ? `<dl class="t-small tech">${tech.map(([k, val]) => `<dt>${esc(k)}</dt><dd><code>${esc(val)}</code></dd>`).join("")}</dl>` : ""}` : ""}
    ${rule.history?.length ? `<h4>Geschichte</h4><ul class="t-small">${rule.history.map((h) => `<li>${esc(h)}</li>`).join("")}</ul>` : ""}
    ${d ? `<p class="t-small">Entscheidet im aktuellen Lauf: ${d.unit === "Kreuzungen" ? `${num(d.n)} Kreuzungen` : `${num(d.n)} ${esc(d.unit ?? "Abschnitte")}, ${num(d.km, 1)} km`}</p>` : ""}
    ${repo ? `<p class="t-small"><a href="https://github.com/${esc(repo)}/blob/main/config/${esc(rule.file)}" rel="noopener">Regeldatei ${esc(rule.file)} auf GitHub</a></p>` : ""}`;
}

const ruleItem = (rule, repo, withId = false) => `<li class="rule"${withId ? ` id="regel-${esc(rule.id)}"` : ""}>
  <strong>${esc(rule.label_plain ?? rule.id)}</strong>${rule.source_type === "assumption" ? ' <span class="tag">Annahme</span>' : ""}
  <p>${esc(rule.explain_plain ?? "")}</p>
  <details class="level l3"><summary>Details und Quellen</summary>${ruleDetailsHtml(rule, repo)}</details></li>`;

// --- chapter ---------------------------------------------------------------------------------

export function chapterHtml(method, key, rules = [], meta = {}) {
  const list = chapters(method);
  const i = list.findIndex((c) => c.key === key);
  if (i < 0) return summaryHtml(method, meta);
  const c = list[i];
  const v = method.vars ?? {};
  const mine = rules.filter((r) => r.chapter === key);
  const prev = list[i - 1];
  const next = list[i + 1];
  const note = key === "radnetz" && meta.cycling?.disclaimer ? `<p class="note"><strong>Wichtig:</strong> ${esc(meta.cycling.disclaimer)}.</p>` : "";
  return `
  <p class="crumb"><a href="#methode">← ${plain(method.title, v)}</a></p>
  <h1>${plain(c.title, v)}</h1>
  <p class="lead">${plain(c.l1, v)}</p>
  ${note}
  ${mdHtml(c.l2, v)}
  <section aria-labelledby="m-rules"><h2 id="m-rules">Regeln in diesem Kapitel</h2>
    ${mine.length ? `<ul class="rules plain">${mine.map((r) => ruleItem(r, meta.github_repo)).join("")}</ul>` : "<p>Zu diesem Kapitel gibt es keine eigenen Regeln.</p>"}
    <p class="t-small"><a href="#methode/regeln">Alle Regeln</a></p></section>
  <nav class="chapter-nav" aria-label="Kapitel">
    ${prev ? `<a href="#methode/${esc(prev.key)}" rel="prev">← ${plain(prev.title, v)}</a>` : "<span></span>"}
    ${next ? `<a href="#methode/${esc(next.key)}" rel="next">${plain(next.title, v)} →</a>` : "<span></span>"}
  </nav>`;
}

/** A rule id or a former id (alias of a merged rule) -> the current rule id. */
export function resolveRule(rules, id) {
  if (rules.some((r) => r.id === id)) return id;
  return rules.find((r) => r.aliases?.includes(id))?.id ?? id;
}

// --- reference -------------------------------------------------------------------------------

export function filterRules(rules, { q = "", onlyAssumption = false } = {}) {
  const needle = String(q ?? "").trim().toLowerCase();
  return rules.filter((r) => {
    if (onlyAssumption && r.source_type !== "assumption") return false;
    if (!needle) return true;
    return [r.id, r.label_plain, r.explain_plain].some((x) => String(x ?? "").toLowerCase().includes(needle));
  });
}

/** The grouped list only (re-rendered while typing). */
export function referenceListHtml(method, rules, opts = {}, repo = null) {
  const shown = filterRules(rules, opts);
  const v = method.vars ?? {};
  const groups = chapters(method).map((c) => ({ c, items: shown.filter((r) => r.chapter === c.key) })).filter((g) => g.items.length);
  const known = new Set(chapters(method).map((c) => c.key));
  const rest = shown.filter((r) => !known.has(r.chapter));
  if (rest.length) groups.push({ c: { key: "sonst", title: "Weitere Regeln" }, items: rest });
  if (!groups.length) return "<p>Keine Regel gefunden.</p>";
  return `<p class="t-small" role="status">${num(shown.length)} von ${num(rules.length)} Regeln</p>${groups.map((g) => `
    <section aria-labelledby="g-${esc(g.c.key)}"><h2 id="g-${esc(g.c.key)}">${plain(g.c.title, v)}</h2>
    <ul class="rules plain">${g.items.map((r) => ruleItem(r, repo, true)).join("")}</ul></section>`).join("")}`;
}

export function referenceHtml(method, rules, opts = {}, versions = {}, repo = null) {
  const ref = method.reference ?? {};
  const v = method.vars ?? {};
  const names = { "rules.yaml": "Regelwerk", "cycling_rules.yaml": "Radnetz", "design_rules.yaml": "Querschnitt und Kreuzungen" };
  const ver = Object.entries(names).filter(([f]) => versions[f]).map(([f, n]) => `${n} ${esc(versions[f])}`).join(" · ");
  return `
  <p class="crumb"><a href="#methode">← ${plain(method.title, v)}</a></p>
  <h1>${plain(ref.title, v)}</h1>
  <p class="lead">${plain(ref.intro, v)}</p>
  ${ver ? `<p class="t-small">Stand: ${ver}</p>` : ""}
  <p class="t-small"><a href="#daten">Regeldateien herunterladen</a></p>
  <form class="rule-filter" role="search" onsubmit="return false">
    <label for="rule-q">Regeln durchsuchen (Nummer, Name oder Text)</label>
    <input id="rule-q" type="search" value="${esc(opts.q ?? "")}" autocomplete="off">
    <label class="opt"><input id="rule-assume" type="checkbox"${opts.onlyAssumption ? " checked" : ""}> nur Annahmen</label>
  </form>
  <div id="rule-list">${referenceListHtml(method, rules, opts, repo)}</div>`;
}

// --- news ------------------------------------------------------------------------------------

export function newsHtml(method, meta, changelogMd = "") {
  const v = method.vars ?? {};
  const news = method.news ?? [];
  const date = (d) => (d && !Number.isNaN(Date.parse(d)) ? new Date(d).toLocaleDateString("de-DE") : d);
  return `
  <p class="crumb"><a href="#methode">← ${plain(method.title, v)}</a></p>
  <h1>Was ist neu</h1>
  <p>Aktuelle Version: ${esc(meta.version)} (Regelwerk ${esc(meta.rules_version)}, Datenstand ${esc(date(meta.data_date))})</p>
  ${news.length ? `<ul class="news plain">${news.map((n) => `<li><h2>${esc(n.title)}</h2>
    <p class="t-small">${esc(date(n.date))}${n.version ? ` · Regelwerk ${esc(n.version)}` : ""}</p>
    ${n.text ? `<p>${esc(n.text)}</p>` : ""}
    ${n.items?.length ? `<ul>${n.items.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>` : ""}</li>`).join("")}</ul>` : "<p>Noch keine Einträge.</p>"}
  <details class="level l3"><summary>Alle Änderungen (CHANGELOG)</summary><div class="changelog">${marked.parse(changelogMd || "")}</div></details>`;
}
