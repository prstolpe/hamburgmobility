// Content inventory of the current website (prompt 24, A1.1): visible text of every page, every map layer (layer
// description + legend), the controls and filters, one street profile per category and one junction profile,
// with screenshots on desktop (1440 px) and mobile (390 px).
// Output: data/scenarios/redesign/ui/content.json, screenshots docs/redesign/img/c-*.jpg.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { chromium, newPage, open, OUT, shot, words, writeJson } from "./lib.mjs";

const FX = JSON.parse(readFileSync(join(OUT, "fixtures.json")));
// IMG_PREFIX: screenshot prefix (default "c-" = state before the redesign; e.g. "p1-" for package 1 of Part B)
const PREFIX = process.env.IMG_PREFIX || "c-";
const PAGES = ["karte", "bezirke", "methode", "radnetz", "daten", "impressum"];
// the intro box ("Was ist das?") is shown once; all captures except the dedicated intro screenshot mark it as seen
const SEEN = () => { try { localStorage.setItem("sfp-intro-seen", "1"); } catch {} };

/** Text of an element split into sections by headings h1–h4 (heading, text, words). */
async function sections(page, selector) {
  return page.evaluate((sel) => {
    const root = document.querySelector(sel);
    if (!root) return [];
    const out = [];
    let cur = { heading: "(Anfang)", level: 0, parts: [] };
    const walk = (node) => {
      for (const el of node.children) {
        if (el.hidden || getComputedStyle(el).display === "none") continue;
        if (/^H[1-4]$/.test(el.tagName)) {
          if (cur.parts.length) out.push(cur);
          cur = { heading: el.innerText.trim(), level: Number(el.tagName[1]), parts: [] };
        } else if (el.querySelector("h1,h2,h3,h4")) {
          walk(el);
        } else {
          const t = el.innerText?.trim();
          if (t) cur.parts.push(t);
        }
      }
    };
    walk(root);
    if (cur.parts.length) out.push(cur);
    return out.map((s) => ({ heading: s.heading, level: s.level, text: s.parts.join("\n") }));
  }, selector);
}

const withWords = (secs) => secs.map((s) => ({ ...s, words: (s.text.match(/\S+/g) ?? []).length }));

/** Open all details in the panel so that their texts are captured. */
const openDetails = (page) => page.evaluate(() => document.querySelectorAll("#panel details").forEach((d) => { d.open = true; }));

const browser = await chromium.launch();
const result = { intro: null, generated: new Date().toISOString(), pages: {}, layers: {}, profiles: {}, junction: null, chrome: {} };

for (const kind of ["desktop", "mobile"]) {
  const page = await newPage(browser, kind);
  // first visit: intro box visible (own context without the seen flag)
  const first = await newPage(browser, kind);
  await open(first, "#karte", { settle: 2500 });
  const introImg = await shot(first, `${PREFIX}intro-${kind}`);
  if (kind === "desktop") result.intro = { text: await first.evaluate(() => document.querySelector("#intro")?.innerText ?? ""), image: introImg };
  else result.intro.image_mobile = introImg;
  await first.context().close();
  await page.addInitScript(SEEN);

  // pages
  for (const p of PAGES) {
    await open(page, p === "bezirke" ? "#bezirke?bz=Eimsb%C3%BCttel" : `#${p}`, { settle: p === "karte" ? 3000 : 1500 });
    const img = await shot(page, `${PREFIX}${p}-${kind}`);
    const full = p === "karte" ? null : await shot(page, `${PREFIX}${p}-${kind}-full`, { fullPage: true, quality: 60 });
    if (kind === "desktop") {
      const sel = p === "karte" ? "#controls-body" : `section[data-page="${p}"]`;
      const secs = withWords(await sections(page, sel));
      result.pages[p] = { sections: secs, words: secs.reduce((a, s) => a + s.words, 0), image: img, image_full: full };
    } else {
      result.pages[p].image_mobile = img;
      result.pages[p].image_mobile_full = full;
      result.pages[p].page_height_mobile = await page.evaluate(() => document.documentElement.scrollHeight);
    }
  }

  // site chrome (banner, header, nav) once
  if (kind === "desktop") {
    await open(page, "#karte");
    result.chrome = {
      banner: (await page.$(".banner")) ? await page.textContent(".banner") : null, // no banner since prompt 25
      title: await page.textContent(".site-title"),
      nav: await page.$$eval("nav.main a", (as) => as.map((a) => a.innerText.trim())),
      controls_summary: await page.evaluate(() => document.querySelector("#controls-body summary")?.innerText ?? ""),
      fieldsets: await page.$$eval("#controls-body fieldset > legend", (ls) => ls.map((l) => l.innerText.trim())),
      themes: await page.$$eval("#themes button[data-theme]", (bs) => bs.map((b) => b.innerText.trim())),
      views: await page.$$eval("#controls-body [data-view], #controls-body [data-theme-view]", (bs) => bs.map((b) => b.innerText.trim())),
      overlay_options: await page.$$eval('#controls-body input[name="ov"]', (is) => is.map((i) => i.parentElement.innerText.trim())),
      filter_text: await page.evaluate(() => { const d = document.querySelector("#controls-body details"); if (d) d.open = true; return d?.innerText ?? ""; }),
      controls_height_desktop: await page.evaluate(() => document.querySelector("#controls-body").scrollHeight),
    };
  }

  // layers: every theme/view (key "theme/view"), description + legend
  await open(page, "#karte", { settle: 1500 });
  // level 3 "Mehr Ansichten" lists every theme:view pair
  const pairs = await page.evaluate(() => {
    document.querySelectorAll("#controls-body details").forEach((d) => { d.open = true; });
    return [...document.querySelectorAll("#controls-body [data-theme-view]")].map((b) => b.dataset.themeView.split(":"));
  });
  // plus the level-1/2 view buttons of every theme (first view = theme default)
  const themes = await page.$$eval("#themes button[data-theme]", (bs) => bs.map((b) => b.dataset.theme));
  for (const t of themes) {
    await open(page, `#karte?theme=${t}`, { settle: 500 });
    const vs = await page.$$eval("#themes button[data-view]", (bs) => bs.map((b) => b.dataset.view));
    pairs.push(...(vs.length ? vs : ["ziel"]).map((v) => [t, v]));
  }
  const done = new Set();
  for (const [t, v] of pairs) {
    if (done.has(`${t}-${v}`)) continue;
    done.add(`${t}-${v}`);
    const key = `${t}-${v}`;
    await open(page, `#karte?theme=${t}&view=${v}`, { settle: 3000 });
    const img = await shot(page, `${PREFIX}layer-${key}-${kind}`);
    if (kind === "desktop") {
      const text = (await page.textContent("#layer-text").catch(() => "")) ?? "";
      const legend = await page.$$eval("#legend li", (lis) => lis.map((li) => li.innerText.trim()));
      const notes = await page.$$eval("#legend p", (ps) => ps.map((p) => p.innerText.trim()));
      const legendTop = await page.evaluate(() => Math.round(document.querySelector("#legend").getBoundingClientRect().top));
      const title = await page.evaluate(() => document.querySelector("#controls-body [data-theme-view][aria-pressed=true]")?.textContent.trim() ?? "");
      result.layers[key] = { theme: t, view: v, title,
        text, legend, notes, words: words([text, ...legend, ...notes].join(" ")), legend_top_px: legendTop, image: img };
    } else {
      result.layers[key].image_mobile = img;
      result.layers[key].legend_visible_mobile = await page.evaluate(() => {
        const r = document.querySelector("#legend").getBoundingClientRect();
        return r.top < innerHeight && r.bottom > 0;
      });
    }
  }

  // profiles: one per category and the junction
  for (const [cat, p] of Object.entries(FX.profiles)) {
    await open(page, `#karte?seg=${p.id}&map=16/${p.lat}/${p.lon}`, { settle: 3500 });
    await page.waitForSelector("#panel-title", { timeout: 15_000 });
    await openDetails(page);
    const img = await shot(page, `${PREFIX}profile-${cat}-${kind}`);
    if (kind === "desktop") {
      const secs = withWords(await sections(page, "#panel-body"));
      result.profiles[cat] = { id: p.id, name: p.name, title: await page.textContent("#panel-title"), sections: secs,
        words: secs.reduce((a, s) => a + s.words, 0), panel_height_px: await page.evaluate(() => document.querySelector("#panel").scrollHeight), image: img };
    } else {
      result.profiles[cat].image_mobile = img;
      result.profiles[cat].panel_height_mobile = await page.evaluate(() => document.querySelector("#panel").scrollHeight);
    }
  }
  const j = FX.junction;
  await open(page, `#karte?theme=knoten&jct=${j.id}&map=17/${j.lat}/${j.lon}`, { settle: 3500 });
  await page.waitForSelector("#panel-title", { timeout: 15_000 });
  await openDetails(page);
  const jimg = await shot(page, `${PREFIX}junction-${kind}`);
  if (kind === "desktop") {
    const secs = withWords(await sections(page, "#panel-body"));
    result.junction = { id: j.id, title: await page.textContent("#panel-title"), sections: secs, words: secs.reduce((a, s) => a + s.words, 0), image: jimg };
  } else {
    result.junction.image_mobile = jimg;
  }
  result[`errors_${kind}`] = page.errors.slice();
  await page.context().close();
}
await browser.close();
writeJson(PREFIX === "c-" ? "content.json" : `content-${PREFIX.replace(/-$/, "")}.json`, result);
for (const [k, v] of Object.entries(result.pages)) console.log(`page ${k.padEnd(10)} ${v.words} words, ${v.sections.length} sections`);
for (const [k, v] of Object.entries(result.layers)) console.log(`layer ${k.padEnd(6)} ${v.words} words, legend ${v.legend.length} items, mobile legend visible ${v.legend_visible_mobile}`);
for (const [k, v] of Object.entries(result.profiles)) console.log(`profile ${k.padEnd(8)} ${v.words} words, ${v.sections.length} sections, ${v.panel_height_px}px`);
console.log(`junction ${result.junction.words} words`);
console.log("errors", result.errors_desktop.length, result.errors_mobile.length);
