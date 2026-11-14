// Task test of the current website for the redesign (prompt 24, A1.2), adapted from analysis/review_2026_11/ui/tasks.mjs:
// the five tasks of the prompt as click paths on desktop (1440 px) and smartphone (390 px). Each step records KLM
// operators (Card/Moran/Newell 1983), screenshots, measurements and the text the reader has to read (for the
// blocking-word analysis in analysis/redesign/readability.py).
// Output: data/scenarios/redesign/ui/tasks.json, screenshots in docs/redesign/img/t*.jpg.
//
// Time estimate (assumption, source_type assumption): KLM operator times K 0.28 s (desktop) / 0.5 s (touch),
// P 1.1 s, B 0.2 s, H 0.4 s, M 1.35 s; scrolling S 1.0 s per gesture; reading 200 words per minute.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { BASE, chromium, newPage, open, OUT, shot, writeJson } from "./lib.mjs";

const FX = JSON.parse(readFileSync(join(OUT, "fixtures.json")));
const OP_S = { desktop: { K: 0.28, P: 1.1, B: 0.2, H: 0.4, M: 1.35, S: 1.0 }, mobile: { K: 0.5, P: 1.1, B: 0.2, H: 0, M: 1.35, S: 1.0 } };
const WPM = 200;
const JCT = FX.junction;

// --- helpers ---------------------------------------------------------------------------------

/** Pixel of a lon/lat on the map canvas, from the map=z/lat/lon state the site writes into the URL (Web Mercator, 512 px tiles). */
async function pixelOf(page, lon, lat) {
  return page.evaluate(([lon, lat]) => {
    const m = new URLSearchParams(location.hash.split("?")[1] ?? "").get("map");
    if (!m) return null;
    const [z, clat, clon] = m.split("/").map(Number);
    const size = 512 * 2 ** z;
    const x = (lo) => ((lo + 180) / 360) * size;
    const y = (la) => { const r = (la * Math.PI) / 180; return ((1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2) * size; };
    const rect = document.querySelector("#map canvas").getBoundingClientRect();
    return { x: rect.left + rect.width / 2 + (x(lon) - x(clon)), y: rect.top + rect.height / 2 + (y(lat) - y(clat)), zoom: z };
  }, [lon, lat]);
}

async function inViewport(page, selector) {
  // Visible in the window and not hidden inside a scrolled container (controls panel).
  return page.locator(selector).first().evaluate((el) => {
    const r = el.getBoundingClientRect();
    if (!(r.top >= 0 && r.bottom <= innerHeight && r.height > 0)) return false;
    const c = el.closest(".controls");
    if (!c) return true;
    const cr = c.getBoundingClientRect();
    return r.top >= cr.top && r.bottom <= cr.bottom;
  }).catch(() => false);
}

const words = (t) => (t.match(/\S+/g) ?? []).length;

async function panelSection(page, headingId) {
  // Text of the panel section with this heading, and how far the reader has to scroll inside the panel to reach it.
  return page.evaluate((id) => {
    const panel = document.querySelector("#panel");
    const h = panel.querySelector(`#${id}`);
    if (!h) return null;
    const sec = h.closest("section") ?? h.parentElement;
    const mobile = innerWidth <= 760;
    const visibleH = mobile ? panel.getBoundingClientRect().height : panel.clientHeight;
    const top = h.offsetTop;
    return { text: sec.innerText, top, visibleH, scrollHeight: panel.scrollHeight,
      scrolls: Math.max(0, Math.ceil((top - visibleH * 0.6) / (visibleH * 0.8))) };
  }, headingId);
}

async function mapVisibleShare(page) {
  return page.evaluate(() => {
    const r = document.querySelector("#map").getBoundingClientRect();
    const vis = Math.max(0, Math.min(innerHeight, r.bottom) - Math.max(0, r.top));
    return { share: +(vis / innerHeight).toFixed(2), top: Math.round(r.top), viewport: innerHeight };
  });
}

class Run {
  constructor(page, task, kind) { Object.assign(this, { page, task, kind, steps: [], notes: [], n: 0 }); }
  async step(desc, ops, fn, { read = 0, img = true } = {}) {
    const extra = fn ? (await fn()) ?? {} : {};
    const opList = ops.split(/\s+/).filter(Boolean).flatMap((o) => { const [k, n] = o.split("*"); return Array(Number(n ?? 1)).fill(k); });
    const t = opList.reduce((a, o) => a + OP_S[this.kind][o], 0) + ((read + (extra.read ?? 0)) / WPM) * 60;
    this.n += 1;
    const name = `${this.task}-${this.kind}-${String(this.n).padStart(2, "0")}`;
    const image = img ? await shot(this.page, name) : null;
    this.steps.push({ n: this.n, desc, ops: opList.join(" "), words_read: read + (extra.read ?? 0), seconds: +t.toFixed(1), image, ...extra.info && { info: extra.info }, ...extra.text && { text: extra.text } });
  }
  note(text) { this.notes.push(text); }
  summary() {
    const ops = this.steps.flatMap((s) => s.ops.split(" ").filter(Boolean));
    const c = (k) => ops.filter((o) => o === k).length;
    return { task: this.task, device: this.kind, steps: this.steps.length, clicks: c("B"), keystrokes: c("K"), scrolls: c("S"),
      decisions: c("M"), words_read: this.steps.reduce((a, s) => a + s.words_read, 0),
      seconds: +this.steps.reduce((a, s) => a + s.seconds, 0).toFixed(0), errors: this.page.errors.slice(), notes: this.notes, path: this.steps };
  }
}

async function searchStreet(run, q, pick) {
  const { page, kind } = run;
  const typed = q.length;
  await run.step(`Suchfeld antippen, „${q}" tippen`, `M ${kind === "desktop" ? "H " : ""}P B K*${typed}`, async () => {
    await page.click("#search");
    await page.keyboard.type(q, { delay: 20 });
    await page.waitForSelector("#search-list li");
    const opts = await page.$$eval("#search-list li", (lis) => lis.map((l) => l.innerText.replace(/\s+/g, " ")));
    return { info: { suggestions: opts } };
  });
  await run.step(`Vorschlag „${pick}" wählen – Karte zoomt auf die Straße`, "M P B", async () => {
    await page.locator("#search-list li", { hasText: pick }).first().click();
    await page.waitForTimeout(3500);
    return { info: { panel_open: await page.isVisible("#panel"), map: await mapVisibleShare(page) } };
  });
}

/** Tap a map feature; on mobile the map may lie partly below the fold (counts a scroll). */
async function tapFeature(run, desc, lon, lat, expect) {
  const { page } = run;
  let scrolled = false;
  let panned = false;
  let px = await pixelOf(page, lon, lat);
  const vh = page.viewportSize().height;
  // usable map area: canvas inside the window, minus the open profile panel on desktop
  const area = async () => page.evaluate(() => {
    const r = document.querySelector("#map canvas").getBoundingClientRect();
    const p = document.querySelector("#panel");
    const right = !p.hidden && innerWidth > 760 ? Math.min(r.right, p.getBoundingClientRect().left) : r.right;
    return { left: r.left + 20, right: right - 20, top: Math.max(0, r.top) + 20, bottom: Math.min(innerHeight, r.bottom) - 20,
      cx: (r.left + right) / 2, cy: (Math.max(0, r.top) + Math.min(innerHeight, r.bottom)) / 2 };
  });
  if (px && (px.y > vh - 20 || px.y < 0) && run.kind === "mobile") {
    // the reader swipes the page (not the map) until the map is in view
    await page.evaluate((dy) => window.scrollBy(0, dy), px.y - vh / 2);
    await page.waitForTimeout(600);
    scrolled = true;
    px = await pixelOf(page, lon, lat);
  }
  let a = await area();
  const outside = (p, b) => p && (p.x < b.left || p.x > b.right || p.y < b.top || p.y > b.bottom);
  for (let i = 0; i < 4 && outside(px, a); i++) {
    // a reader drags the map until the place is visible (each drag stays inside the map area)
    const cap = (v, h) => Math.max(-h, Math.min(h, v));
    const dx = cap(a.cx - px.x, (a.right - a.left) / 2 - 10);
    const dy = cap(a.cy - px.y, (a.bottom - a.top) / 2 - 10);
    await page.mouse.move(a.cx - dx / 2, a.cy - dy / 2);
    await page.mouse.down();
    await page.mouse.move(a.cx + dx / 2, a.cy + dy / 2, { steps: 12 });
    await page.mouse.up();
    await page.waitForTimeout(1500);
    panned = true;
    px = await pixelOf(page, lon, lat);
    a = await area();
  }
  await run.step(desc, `${scrolled ? "S " : ""}${panned ? "M P B " : ""}M P B`, async () => {
    if (px && (px.x < a.left - 20 || px.x > a.right + 20 || px.y < a.top - 20 || px.y > a.bottom + 20)) {
      return { info: { error: "target outside the map area", px } };
    }
    if (!px) return { info: { error: "no map state in URL" } };
    await page.mouse.click(px.x, px.y);
    await page.waitForTimeout(1500);
    const ok = await page.isVisible(expect);
    return { info: { clicked_at: { x: Math.round(px.x), y: Math.round(px.y), zoom: +px.zoom.toFixed(2) }, opened: ok,
      title: ok ? await page.textContent("#panel-title").catch(() => null) : null, scrolled_page_first: scrolled } };
  });
}

async function chooseLayer(run, label) {
  const { page } = run;
  const sel = `#controls-body label.opt:has-text("${label}") input`;
  const visible = await inViewport(page, sel);
  await run.step(`Ebene „${label}" wählen${visible ? "" : " (erst im Bedienfeld scrollen)"}`, `${visible ? "" : "S "}M P B`, async () => {
    await page.locator(sel).check();
    await page.waitForTimeout(2500);
    const legend = await page.$$eval("#legend li", (lis) => lis.map((l) => l.innerText.trim()));
    const legendVisible = await inViewport(page, "#legend");
    const layerText = await page.textContent("#layer-text");
    return { read: words(legend.join(" ")) + words(layerText), text: [layerText, ...legend].join("\n"), info: { legend, legend_in_viewport: legendVisible } };
  });
}

// --- the five tasks --------------------------------------------------------------------------

async function t1t2(browser, kind) {
  const page = await newPage(browser, kind);
  const r1 = new Run(page, "t1", kind);
  await open(page, "#karte");
  await r1.step("Startseite: Karte von Hamburg", "M", async () => ({ info: { map: await mapVisibleShare(page) } }));
  await searchStreet(r1, "Hallerstr", "Hallerstraße");
  const afterSearch = r1.steps.at(-1).info;
  if (!afterSearch.panel_open) r1.note("Die Suche zoomt nur auf die Straße; der Steckbrief öffnet sich nicht. Man muss die Linie auf der Karte treffen.");
  if (kind === "mobile" && afterSearch.map.share < 0.6) r1.note(`Nach der Suche zeigt der Bildschirm nur ${Math.round(afterSearch.map.share * 100)} % Karte (Kartenoberkante bei ${afterSearch.map.top} px von ${afterSearch.map.viewport} px); das aufgeklappte Bedienfeld liegt darüber.`);
  await tapFeature(r1, "Linie der Hallerstraße antippen", FX.segment.lon, FX.segment.lat, "#panel");
  const soll = await panelSection(page, "h-soll");
  const why = await panelSection(page, "h-why");
  await r1.step("Steckbrief lesen: Soll-Kategorie und Begründung", why?.scrolls ? `S*${why.scrolls} M` : "M", async () => {
    const rules = await page.$$eval("#panel .rule", (els) => els.map((e) => e.textContent));
    const codes = (soll?.text.match(/\b(GOW50|GOW30|ETW30|ETW_ERF|SW)\b/g) ?? []).length;
    return { read: words(soll?.text ?? "") + words(why?.text ?? ""), text: [soll?.text, why?.text].filter(Boolean).join("\n"), info: { rule_ids_in_panel: rules.length, category_codes_in_answer: codes,
      begruendung_top_px: why?.top, panel_visible_px: why?.visibleH, panel_total_px: soll?.scrollHeight } };
  });
  const s1 = r1.summary();

  // T2 continues in the open profile
  const r2 = new Run(page, "t2", kind);
  const disc = await panelSection(page, "h-disc");
  const qs = await panelSection(page, "h-qs");
  const rad = await panelSection(page, "h-rad");
  await page.evaluate((top) => { document.querySelector("#panel").scrollTop = top - 10; }, disc?.top ?? 0);
  await page.waitForTimeout(300);
  await r2.step("Zur Diskrepanz scrollen und lesen", `S*${Math.max(1, disc?.scrolls ?? 1)} M`, async () => ({ read: words(disc?.text ?? ""), text: disc?.text,
    info: { section_top_px: disc?.top } }));
  await page.evaluate((top) => { document.querySelector("#panel").scrollTop = top - 10; }, qs?.top ?? 0);
  await page.waitForTimeout(300);
  await r2.step("Querschnitt (Straße) lesen", "S M", async () => ({ read: words(qs?.text ?? ""), text: qs?.text, info: { section_top_px: qs?.top } }));
  await page.evaluate((top) => { document.querySelector("#panel").scrollTop = top - 10; }, rad?.top ?? 0);
  await page.waitForTimeout(300);
  const fitTexts = await page.evaluate(() => {
    const dd = [...document.querySelectorAll("#panel dt")].find((d) => d.textContent === "Machbarkeit")?.nextElementSibling?.textContent;
    const fit = document.querySelector("#h-rad")?.closest("section")?.querySelector("h4 + p strong")?.textContent;
    return { street_feasibility: dd ?? null, cycling_fit: fit ?? null };
  });
  await r2.step("Radverkehr und Soll-Querschnitt lesen (zweite Querschnitts-Angabe)", `S*${Math.max(1, (rad?.scrolls ?? 1) - (qs?.scrolls ?? 0))} M M`,
    async () => ({ read: words(rad?.text ?? ""), text: rad?.text, info: { section_top_px: rad?.top, panel_total_px: rad?.scrollHeight, ...fitTexts } }));
  if (fitTexts.street_feasibility && fitTexts.cycling_fit) r2.note(`Zwei Machbarkeitsaussagen im selben Steckbrief: „${fitTexts.street_feasibility}" (Querschnitt) und „${fitTexts.cycling_fit}" (Soll-Querschnitt Radverkehr).`);
  const s2 = r2.summary();
  await page.context().close();
  return [s1, s2];
}

async function t3(browser, kind) {
  const page = await newPage(browser, kind);
  const r = new Run(page, "t3", kind);
  await open(page, "#karte");
  await r.step("Startseite", "M");
  await r.step("„Tabelle\" wählen", "M P B", async () => { await page.click('nav.main a[href="#tabelle"]'); await page.waitForTimeout(800); });
  await r.step("Bezirk „Eimsbüttel\" wählen", "M P B", async () => {
    await page.click('button[data-bz="Eimsbüttel"]');
    await page.waitForSelector("table tbody tr");
    const head = await page.$$eval("table thead th", (ths) => ths.map((t) => t.innerText.trim()));
    const rows = await page.$$eval("table tbody tr", (trs) => trs.slice(0, 10).map((tr) => [...tr.cells].map((c) => c.innerText.trim())));
    const fits = await page.evaluate(() => { const w = document.querySelector(".table-wrap"); return { scrollW: w.scrollWidth, clientW: w.clientWidth }; });
    return { read: words(rows.slice(0, 5).flat().join(" ")), text: [head.join(" | "), ...rows.slice(0, 5).map((r) => r.join(" | "))].join("\n"), info: { columns: head, top10: rows, table_wider_than_screen: fits.scrollW > fits.clientW + 2 } };
  });
  const info = r.steps.at(-1).info;
  r.note(`Die Tabelle ist nach Priorität sortiert, zeigt aber Kürzel (${[...new Set(info.top10.map((x) => x[1]))].join(", ")}, ${[...new Set(info.top10.map((x) => x[3]))].join(", ")}) und keine Ortsangabe außer dem Straßennamen.`);
  if (info.table_wider_than_screen) r.note("Die Tabelle ist breiter als der Bildschirm (waagerecht scrollen).");
  await r.step("Obersten Eintrag öffnen", `${info.table_wider_than_screen ? "S " : ""}M P B`, async () => {
    await page.locator("table tbody tr").first().locator("button[data-open]").click();
    await page.waitForSelector("#panel-title");
    await page.waitForTimeout(800);
    return { info: { title: await page.textContent("#panel-title") } };
  });
  await r.step("„Auf der Karte zeigen\"", "M P B", async () => {
    const vis = await page.isVisible("#panel-show");
    const layout = await page.evaluate(() => {
      const b = document.querySelector("#panel-show").getBoundingClientRect();
      const p = document.querySelector("#panel").getBoundingClientRect();
      return { doc_width: document.documentElement.scrollWidth, window_width: Math.round(visualViewport.width), scroll_x: scrollX,
        panel: { left: Math.round(p.left), right: Math.round(p.right) }, button: { left: Math.round(b.left), right: Math.round(b.right) } };
    });
    let clicked = false;
    let clickError = null;
    if (vis) clicked = await page.click("#panel-show", { timeout: 5000 }).then(() => true).catch((e) => { clickError = e.message.split("\n").slice(0, 8).join(" | "); return false; });
    await page.waitForTimeout(3000);
    return { info: { button_available: vis, clicked, clickError, layout, panel_still_open: await page.isVisible("#panel") } };
  });
  const show = r.steps.at(-1).info;
  if (!show.clicked) r.note(`„Auf der Karte zeigen" ist nicht bedienbar: Die Seite ist ${show.layout.doc_width} px breit bei ${show.layout.window_width} px sichtbarer Breite (breite Tabelle); der Steckbrief reicht von ${show.layout.panel.left} bis ${show.layout.panel.right} px, die Schaltfläche liegt bei ${show.layout.button.left}–${show.layout.button.right} px und damit außerhalb des sichtbaren Bereichs.`);
  r.note("Handlungsbedarf beim Radverkehr (Radanlagen fehlen, Querschnitt passt nicht) und an Knoten (Rangliste priority_rank) fehlt in der Tabelle; sie enthält nur Straßenabschnitte und ihre Diskrepanz.");
  const s = r.summary();
  await page.context().close();
  return s;
}

async function t4(browser, kind) {
  const page = await newPage(browser, kind);
  const r = new Run(page, "t4", kind);
  await open(page, "#karte");
  await r.step("Startseite", "M");
  await chooseLayer(r, "Radnetz (Soll)");
  await chooseLayer(r, "Radanlagen Soll/Ist");
  await r.step("Kartenausschnitt Eimsbüttel heranzoomen (zweimal +)", "M P B P B", async () => {
    await page.evaluate(() => { location.hash = location.hash.replace(/map=[^&]*/, "").replace(/[?&]$/, "") + (location.hash.includes("?") ? "&" : "?") + "map=13.5/53.575/9.955"; });
    await page.waitForTimeout(3500);
  });
  const titles = await page.$$eval('#controls-body input[name="layer"]', (is) => is.map((i) => i.parentElement.innerText.trim()));
  const gapLayer = titles.filter((t) => /Lücke|Masche/i.test(t));
  r.note(gapLayer.length ? `Ebene für Netzlücken: ${gapLayer.join(", ")}.` :
    `Keine Ebene zeigt Lücken im Netz (fehlende Verbindungen, Maschen); Ebenen: ${titles.join(", ")}. „Radanlagen Soll/Ist" zeigt nur fehlende oder abweichende Radanlagen auf vorhandenen Abschnitten. Es ist immer nur eine Ebene sichtbar.`);
  const s = r.summary();
  await page.context().close();
  return s;
}

async function t5(browser, kind) {
  const page = await newPage(browser, kind);
  const r = new Run(page, "t5", kind);
  await open(page, "#karte");
  await r.step("Startseite", "M");
  await searchStreet(r, "Schulterbl", "Schulterblatt");
  // A first try in the default layer: tapping the junction does not open anything
  await tapFeature(r, "Kreuzung in der Standard-Ebene antippen (öffnet einen Straßen-Steckbrief, keinen Knoten)", JCT.lon, JCT.lat, "#panel");
  const first = r.steps.at(-1).info;
  r.note(`In der Standard-Ebene öffnet ein Tipp auf die Kreuzung ${first.opened ? `den Straßen-Steckbrief „${first.title}"` : "nichts"}; Knoten sind nur in der Rad-Ebene „Knotenpunkte" anklickbar, die Suche findet keine Knoten.`);
  if (await page.isVisible("#panel")) { await page.click("#panel-close"); await page.waitForTimeout(500); }
  await chooseLayer(r, "Knotenpunkte");
  await tapFeature(r, "Knotensymbol Altonaer Straße / Max-Brauer-Allee / Schulterblatt antippen", JCT.lon, JCT.lat, "#h-jsoll");
  const soll = await panelSection(page, "h-jsoll");
  await r.step("Knoten-Steckbrief lesen: Soll-Knotentyp", soll?.scrolls ? `S*${soll.scrolls} M` : "M", async () => ({ read: words(soll?.text ?? ""), text: soll?.text,
    info: { text: soll?.text?.slice(0, 300) } }));
  const s = r.summary();
  await page.context().close();
  return s;
}

const browser = await chromium.launch();
const results = [];
for (const kind of ["desktop", "mobile"]) {
  results.push(...(await t1t2(browser, kind)));
  results.push(await t3(browser, kind));
  results.push(await t4(browser, kind));
  results.push(await t5(browser, kind));
}
await browser.close();
writeJson("tasks.json", { base: BASE, generated: new Date().toISOString(), op_seconds: OP_S, wpm: WPM, results });
for (const s of results) console.log(`${s.task} ${s.device.padEnd(7)} steps ${s.steps} clicks ${s.clicks} keys ${s.keystrokes} scrolls ${s.scrolls} words ${s.words_read} ~${s.seconds}s errors ${s.errors.length}`);
for (const s of results) for (const n of s.notes) console.log(`  [${s.task}/${s.device}] ${n}`);
