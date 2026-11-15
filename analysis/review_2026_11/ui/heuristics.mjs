// Heuristic evaluation of the current website (prompt 21b, phase 3.1): terms, layers and legends, colours
// (colour-vision simulation, meaning across layers), zoom behaviour, profile structure, load time and file sizes,
// accessibility (axe-core) for states the existing report does not cover, draft marking.
// Output: data/scenarios/review_ui/heuristics.json, screenshots docs/review/2026-11/img/h-*.jpg.
// Usage: node heuristics.mjs [--live]  (--live: load-time measurement also against https://hamburgmobility.de)
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { AxeBuilder } from "../../../web/node_modules/@axe-core/playwright/dist/index.mjs";
import * as PAL from "../../../web/src/palette.js";
import { BASE, chromium, newPage, open, OUT, ROOT, shot, writeJson } from "./lib.mjs";

const FX = JSON.parse(readFileSync(join(OUT, "fixtures.json")));
const LIVE = process.argv.includes("--live");
const ONLY = process.argv.find((a) => a.startsWith("--only="))?.slice(7).split(",") ?? null;
const want = (k) => !ONLY || ONLY.includes(k);
const CENTER_EIMS = { lat: 53.5745, lon: 9.955 };
const CODE_RE = /\b(SW|GOW50|GOW30|ETW30|ETW_ERF|GOW80|ETW60|D[1-3]|RSV|HAUPT|BASIS|ERSCHL)\b/g;
const RULE_RE = /\b[A-Z]{1,4}(?:-[A-Z0-9]{1,6}){1,3}\b/g;
const out = {};

// --- 1. colours: meaning across layers and distinguishability under colour-vision deficiency ----

const LAYER_TABLES = {
  "Soll-Kategorie": PAL.CATEGORY_STYLE,
  "Ist-Tempo": Object.fromEntries(PAL.SPEED_CLASSES.map((c) => [c.label, c])),
  Diskrepanz: PAL.DISC_TYPE_STYLE,
  Machbarkeit: PAL.FEASIBILITY_STYLE,
  Straßenraumbreite: PAL.WIDTH_STYLE,
  "Radnetz (Soll)": PAL.CYCLE_CAT_STYLE,
  "Radanlagen (Soll)": PAL.FACILITY_STYLE,
  "Radanlagen Soll/Ist": PAL.GAP_STYLE,
  "Fahrstreifen Soll/Ist": PAL.LANES_STYLE,
  "Querschnitt passt?": PAL.FIT_STYLE,
  "Radnetz amtlich": PAL.OFFICIAL_STYLE,
  Knotenpunkte: PAL.JUNCTION_STYLE,
};
const byColor = {};
for (const [layer, table] of Object.entries(LAYER_TABLES)) {
  for (const [k, s] of Object.entries(table)) (byColor[s.color.toUpperCase()] ??= []).push(`${layer}: ${k}`);
}
out.color_meanings = Object.entries(byColor).sort((a, b) => b[1].length - a[1].length).map(([color, uses]) => ({ color, n: uses.length, uses }));

// Machado, Oliveira & Fernandes (2009), severity 1.0, applied in linear RGB
const MACHADO = {
  protanopia: [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
  deuteranopia: [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.01182, 0.04294, 0.968881]],
  tritanopia: [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.3039]],
};
const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
const rgb = (hex) => { const n = parseInt(hex.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map(lin); };
function lab([r, g, b]) {
  const f = (t) => (t > 216 / 24389 ? Math.cbrt(t) : (24389 / 27 * t + 16) / 116);
  const x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047, y = 0.2126 * r + 0.7152 * g + 0.0722 * b, z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883;
  return [116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))];
}
const sim = (c, m) => (m ? m.map((row) => Math.min(1, Math.max(0, row[0] * c[0] + row[1] * c[1] + row[2] * c[2]))) : c);
const dE = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
out.cvd_min_pairs = {};
for (const [layer, table] of Object.entries(LAYER_TABLES)) {
  const entries = Object.entries(table);
  const res = {};
  for (const [kind, m] of [["normal", null], ...Object.entries(MACHADO)]) {
    let best = null;
    for (let i = 0; i < entries.length; i++) for (let j = i + 1; j < entries.length; j++) {
      const d = dE(lab(sim(rgb(entries[i][1].color), m)), lab(sim(rgb(entries[j][1].color), m)));
      if (!best || d < best.dE) best = { pair: `${entries[i][0]} / ${entries[j][0]}`, dE: +d.toFixed(1),
        same_dash: JSON.stringify(entries[i][1].dash ?? null) === JSON.stringify(entries[j][1].dash ?? null) };
    }
    res[kind] = best;
  }
  out.cvd_min_pairs[layer] = res;
}

// --- browser part ------------------------------------------------------------------------------

const words = (t) => (t.match(/\S+/g) ?? []).length;
function lix(text) {
  // LIX (Björnsson 1968): words per sentence + percentage of words longer than 6 letters
  const w = text.match(/[A-Za-zÄÖÜäöüß]+/g) ?? [];
  const sentences = Math.max(1, (text.match(/[.!?:]+(\s|$)|\n/g) ?? []).length);
  const long = w.filter((x) => x.length > 6).length;
  return w.length ? +(w.length / sentences + (100 * long) / w.length).toFixed(0) : null;
}

const browser = await chromium.launch();

// 2. controls: layers, overlays, filters, legend position
if (want("controls")) {
  const res = {};
  for (const kind of ["desktop", "mobile"]) {
    const page = await newPage(browser, kind);
    await open(page, "#karte");
    res[kind] = await page.evaluate(() => {
      const c = document.querySelector("#controls-body");
      const lg = document.querySelector("#legend").getBoundingClientRect();
      const map = document.querySelector("#map").getBoundingClientRect();
      return { layers: c.querySelectorAll('input[name="layer"]').length, overlays: c.querySelectorAll('input[name="ov"]').length,
        filter_controls: c.querySelectorAll('input[name="cat"], input[name="dt"], select, input[type="range"]').length,
        legend_top_px: Math.round(lg.top), legend_bottom_px: Math.round(lg.bottom), viewport_h: innerHeight,
        legend_items_visible: [...document.querySelectorAll("#legend li")].filter((li) => li.getBoundingClientRect().bottom <= Math.min(innerHeight, c.closest(".controls").getBoundingClientRect().bottom)).length,
        legend_items: document.querySelectorAll("#legend li").length, map_top_px: Math.round(map.top), map_height_px: Math.round(map.height) };
    });
    // legend length and codes per layer
    if (kind === "desktop") {
      res.per_layer = [];
      for (const v of await page.$$eval('input[name="layer"]', (is) => is.map((i) => i.value))) {
        await page.locator(`input[name="layer"][value="${v}"]`).check();
        await page.waitForTimeout(400);
        const t = await page.evaluate(() => ({ title: document.querySelector('input[name="layer"]:checked').parentElement.innerText.trim(),
          legend: [...document.querySelectorAll("#legend li")].map((l) => l.innerText.trim()), intro: document.querySelector("#layer-text").innerText,
          notes: [...document.querySelectorAll("#legend .note, #legend .muted")].map((n) => n.innerText) }));
        const all = [t.legend.join(" "), t.intro].join(" ");
        res.per_layer.push({ key: v, ...t, legend_items: t.legend.length, codes: (all.match(CODE_RE) ?? []).length });
      }
    }
    await page.context().close();
  }
  out.controls = res;
}

// 3. zoom behaviour (Soll-Kategorie and Knotenpunkte)
if (want("zoom")) {
  const page = await newPage(browser, "desktop");
  out.zoom = [];
  for (const [layer, z] of [["cat", 10], ["cat", 12], ["cat", 14], ["cat", 16], ["jct", 11.5], ["jct", 13]]) {
    await open(page, `#karte?${layer === "cat" ? "" : `layer=${layer}&`}map=${z}/${CENTER_EIMS.lat}/${CENTER_EIMS.lon}`, { settle: 3500 });
    const img = await shot(page, `h-zoom-${layer}-z${String(z).replace(".", "_")}`, { clip: { x: 320, y: 95, width: 1120, height: 805 } });
    out.zoom.push({ layer, zoom: z, image: img });
  }
  await page.context().close();
}

// 4. colour-vision simulation screenshots (Chromium Emulation.setEmulatedVisionDeficiency)
if (want("cvd")) {
  const page = await newPage(browser, "desktop");
  const cdp = await page.context().newCDPSession(page);
  out.cvd_images = [];
  for (const [layer, z] of [["cat", 14.5], ["cgap", 14], ["disc", 14.5]]) {
    await open(page, `#karte?${layer === "cat" ? "" : `layer=${layer}&`}map=${z}/${CENTER_EIMS.lat}/${CENTER_EIMS.lon}`, { settle: 3500 });
    for (const type of ["none", "deuteranopia", "protanopia", "tritanopia", "achromatopsia"]) {
      await cdp.send("Emulation.setEmulatedVisionDeficiency", { type });
      await page.waitForTimeout(400);
      out.cvd_images.push({ layer, type, image: await shot(page, `h-cvd-${layer}-${type}`, { clip: { x: 520, y: 300, width: 640, height: 420 } }) });
    }
    await cdp.send("Emulation.setEmulatedVisionDeficiency", { type: "none" });
  }
  await page.context().close();
}

// 5. profiles: structure, length, terms, readability (30 random segments, seed in fixtures.py)
if (want("profiles")) {
  const res = [];
  for (const kind of ["desktop", "mobile"]) {
    const page = await newPage(browser, kind);
    for (const id of FX.sample_segments) {
      await open(page, `#karte?seg=${id}`, { settle: 300 });
      await page.waitForSelector("#panel-title", { timeout: 15_000 });
      const m = await page.evaluate(() => {
        const p = document.querySelector("#panel");
        const body = document.querySelector("#panel-body");
        const hs = [...body.querySelectorAll("h3")].map((h) => ({ t: h.textContent, top: h.offsetTop }));
        const why = body.querySelector("#h-why");
        const visible = innerWidth <= 760 ? p.getBoundingClientRect().height : p.clientHeight;
        return { text: body.innerText, sections: hs.map((h) => h.t), h4: body.querySelectorAll("h4").length, total_px: p.scrollHeight, visible_px: Math.round(visible),
          why_top: why?.offsetTop ?? null, disc_top: body.querySelector("#h-disc")?.offsetTop ?? null, rad_top: body.querySelector("#h-rad")?.offsetTop ?? null,
          src_top: body.querySelector("#h-src")?.offsetTop ?? null, rule_spans: body.querySelectorAll(".rule").length, svgs: body.querySelectorAll("svg").length,
          has_cycling: !!body.querySelector("#h-rad") };
      });
      res.push({ kind, id, words: words(m.text), lix: lix(m.text), codes: (m.text.match(CODE_RE) ?? []).length, rule_ids: (m.text.match(RULE_RE) ?? []).length,
        draft_mentions: (m.text.match(/Entwurf|nicht amtlich/g) ?? []).length, screens: +(m.total_px / m.visible_px).toFixed(1), ...m, text: undefined });
    }
    await page.context().close();
  }
  const med = (k, kind) => { const v = res.filter((r) => r.kind === kind && r[k] != null).map((r) => r[k]).sort((a, b) => a - b); return v[Math.floor(v.length / 2)]; };
  out.profiles = { n: FX.sample_segments.length, rows: res,
    median: Object.fromEntries(["desktop", "mobile"].map((kind) => [kind, Object.fromEntries(["words", "lix", "codes", "rule_ids", "screens", "total_px", "why_top", "disc_top", "rad_top", "draft_mentions"].map((k) => [k, med(k, kind)]))])),
    with_cycling: res.filter((r) => r.kind === "desktop" && r.has_cycling).length,
    without_draft_mention: res.filter((r) => r.kind === "desktop" && r.draft_mentions === 0).length,
    section_order: res.find((r) => r.kind === "desktop" && r.has_cycling)?.sections };
  // one long profile as screenshot sequence (mobile)
  const page = await newPage(browser, "mobile");
  await open(page, `#karte?seg=${FX.segment.id}`, { settle: 800 });
  await page.waitForSelector("#panel-title");
  out.profiles.example_images = [];
  const total = await page.evaluate(() => document.querySelector("#panel").scrollHeight);
  const vis = await page.evaluate(() => document.querySelector("#panel").getBoundingClientRect().height);
  for (let i = 0, y = 0; y < total && i < 12; i++, y += vis * 0.95) {
    await page.evaluate((y) => { document.querySelector("#panel").scrollTop = y; }, y);
    await page.waitForTimeout(150);
    out.profiles.example_images.push(await shot(page, `h-steckbrief-mobile-${String(i + 1).padStart(2, "0")}`));
  }
  out.profiles.example_screens = +(total / vis).toFixed(1);
  await page.context().close();
}

async function hasBanner(browser) {
  const page = await newPage(browser, "desktop");
  await open(page, "#karte", { settle: 500 });
  return (await page.$(".banner")) !== null;
}

// 6. draft marking: banner visible in the first screen of each view. Obsolete since prompt 25 (no banner; title suffix
// and footer instead): the check is skipped when the page has no banner.
if (want("draft") && await hasBanner(browser)) {
  const res = [];
  for (const kind of ["desktop", "mobile"]) {
    const page = await newPage(browser, kind);
    for (const hash of ["#karte", `#karte?seg=${FX.segment.id}`, "#tabelle?bz=Eimsb%C3%BCttel", "#methode", "#radnetz", "#downloads"]) {
      await open(page, hash, { settle: 1200 });
      await page.evaluate(() => window.scrollTo(0, 0)); // hash-only navigation keeps the previous scroll position
      const r = await page.evaluate(() => {
        const b = document.querySelector(".banner").getBoundingClientRect();
        const p = document.querySelector("#panel");
        const pr = p.hidden ? null : p.getBoundingClientRect();
        const covered = pr && pr.left < b.right && pr.top < b.bottom && pr.bottom > b.top;
        return { banner_in_view: b.bottom > 0 && b.top < innerHeight, banner_partly_covered_by_panel: !!covered, banner_sticky: getComputedStyle(document.querySelector(".banner")).position !== "static" };
      });
      // after scrolling the page down by one screen
      await page.evaluate(() => window.scrollTo(0, innerHeight));
      const afterScroll = await page.evaluate(() => document.querySelector(".banner").getBoundingClientRect().bottom > 0);
      res.push({ kind, hash, ...r, banner_in_view_after_scroll: afterScroll });
    }
    await page.context().close();
  }
  out.draft_marking = res;
}

// 7. accessibility: axe-core on states the existing report (reports/web_accessibility.md) does not cover, reflow at 320 px
if (want("axe")) {
  const res = [];
  const states = [
    ["mobile", "Tabelle mit geöffnetem Steckbrief", "#tabelle?bz=Eimsb%C3%BCttel", async (p) => { await p.locator("table tbody tr").first().locator("button[data-open]").click(); await p.waitForSelector("#panel-title"); }],
    ["desktop", "Filter geöffnet", "#karte?layer=disc&pr=1", null],
    ["desktop", "Suchvorschläge offen", "#karte", async (p) => { await p.click("#search"); await p.keyboard.type("Haller"); await p.waitForSelector("#search-list li"); }],
    ["mobile", "Karte Radnetz (Soll) mit Steckbrief", `#karte?layer=cnet&seg=${FX.segment.id}`, null],
  ];
  for (const [kind, label, hash, act] of states) {
    const page = await newPage(browser, kind);
    await open(page, hash, { settle: 1500 });
    if (act) await act(page);
    await page.waitForTimeout(500);
    const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
    res.push({ kind, label, violations: r.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help })), passes: r.passes.length, incomplete: r.incomplete.map((v) => v.id) });
    await page.context().close();
  }
  out.axe = res;
  // WCAG 1.4.10 reflow: no horizontal scrolling at 320 CSS px
  const ctx = await browser.newContext({ viewport: { width: 320, height: 640 }, locale: "de-DE" });
  const page = await ctx.newPage();
  out.reflow_320 = [];
  for (const hash of ["#karte", `#karte?seg=${FX.segment.id}`, "#tabelle?bz=Eimsb%C3%BCttel", "#methode", "#radnetz"]) {
    await open(page, hash, { settle: 1200 });
    const w = await page.evaluate(() => ({ doc: document.documentElement.scrollWidth, win: innerWidth }));
    out.reflow_320.push({ hash, doc_width: w.doc, window: w.win, horizontal_scroll: w.doc > 322 });
    if (hash.startsWith("#tabelle")) {
      await shot(page, "h-reflow-320-tabelle");
      await page.addStyleTag({ content: ".table-wrap { position: relative; }" }); // visually-hidden spans (absolute) escape the scroll container
      await page.waitForTimeout(300);
      const fixed = await page.evaluate(() => document.documentElement.scrollWidth);
      out.reflow_320.at(-1).doc_width_with_table_wrap_relative = fixed;
    }
  }
  await ctx.close();
}

// 8. load time and transferred bytes (CDP network throttling; Lighthouse "Slow 4G": 1.6 Mbit/s, 150 ms RTT)
async function loadRun(base, kind, profile) {
  const page = await newPage(browser, kind);
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Network.enable");
  await cdp.send("Network.setCacheDisabled", { cacheDisabled: true });
  if (profile === "slow4g") await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 150, downloadThroughput: (1.6 * 1024 * 1024) / 8, uploadThroughput: (750 * 1024) / 8 });
  const reqs = new Map();
  cdp.on("Network.responseReceived", (e) => reqs.set(e.requestId, { url: e.response.url, mime: e.response.mimeType, status: e.response.status, enc: e.response.headers["content-encoding"] ?? e.response.headers["Content-Encoding"] ?? null }));
  cdp.on("Network.loadingFinished", (e) => { const r = reqs.get(e.requestId); if (r) r.bytes = e.encodedDataLength; });
  const t0 = Date.now();
  await page.goto(new URL("#karte", base).href);
  await page.waitForFunction(() => (document.querySelector("#foot-version") ?? document.querySelector("#banner-text"))?.textContent.includes("Datenstand"), null, { timeout: 120_000 });
  const tMeta = Date.now() - t0;
  await page.waitForFunction(() => document.querySelector("#map canvas"), null, { timeout: 120_000 });
  const tCanvas = Date.now() - t0;
  // map is "complete" when no request finished for 1.5 s
  let last = Date.now();
  cdp.on("Network.loadingFinished", () => { last = Date.now(); });
  while (Date.now() - last < 1500 && Date.now() - t0 < 120_000) await page.waitForTimeout(250);
  const tIdle = last - t0;
  // profile: time from navigation to a profile until its title is shown
  const t1 = Date.now();
  await page.goto(new URL(`#karte?seg=${FX.segment.id}`, base).href);
  await page.waitForSelector("#panel-title", { timeout: 120_000 });
  const tProfile = Date.now() - t1;
  const list = [...reqs.values()].filter((r) => r.bytes != null);
  const group = (r) => (r.url.includes(".pmtiles") ? (r.url.includes("basemap") ? "Grundkarte (PMTiles)" : "Fachdaten (PMTiles)") : r.url.endsWith(".js") || r.url.endsWith(".mjs") ? "JavaScript"
    : r.url.includes("search.json") ? "search.json" : r.url.includes(".json") ? "JSON (meta, Steckbrief)" : r.url.includes(".pbf") ? "Schriften" : r.url.includes("sprite") ? "Sprites" : r.url.includes(".geojson") ? "GeoJSON (Bezirke)" : r.url.endsWith(".css") ? "CSS" : "sonstige");
  const byGroup = {};
  for (const r of list) { const g = group(r); byGroup[g] ??= { requests: 0, kb: 0 }; byGroup[g].requests += 1; byGroup[g].kb += r.bytes / 1024; }
  for (const g of Object.values(byGroup)) g.kb = +g.kb.toFixed(0);
  const sj = list.find((r) => r.url.includes("search.json"));
  await page.context().close();
  return { base, kind, profile, t_meta_ms: tMeta, t_canvas_ms: tCanvas, t_idle_ms: tIdle, t_profile_ms: tProfile, requests: list.length,
    kb_total: +(list.reduce((a, r) => a + r.bytes, 0) / 1024).toFixed(0), by_group: byGroup, search_json_encoding: sj?.enc ?? null, search_json_kb: sj ? +(sj.bytes / 1024).toFixed(0) : null };
}
if (want("load")) {
out.load = [];
out.load.push(await loadRun(BASE, "mobile", "slow4g"));
out.load.push(await loadRun(BASE, "desktop", "none"));
}
if (want("load") && LIVE) {
  for (const [kind, profile] of [["mobile", "slow4g"], ["desktop", "none"]]) {
    out.load.push(await loadRun("https://hamburgmobility.de/", kind, profile).catch((e) => ({ base: "https://hamburgmobility.de/", kind, profile, error: e.message.split("\n")[0] })));
  }
}

await browser.close();
let prev = {};
try { prev = ONLY ? JSON.parse(readFileSync(join(OUT, "heuristics.json"))) : {}; } catch { prev = {}; }
writeJson("heuristics.json", { ...prev, base: BASE, generated: new Date().toISOString(), ...out });
console.log(JSON.stringify({ controls: out.controls?.desktop, profiles: out.profiles?.median, load: out.load?.map((l) => ({ base: l.base, kind: l.kind, profile: l.profile, t_meta: l.t_meta_ms, t_idle: l.t_idle_ms, kb: l.kb_total, err: l.error })), axe: out.axe?.map((a) => [a.label, a.violations.length]), reflow: out.reflow_320, draft: out.draft_marking }, null, 1));
