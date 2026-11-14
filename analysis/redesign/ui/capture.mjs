// Content inventory of the current website (prompt 24, A1.1): visible text of every page, every map layer (layer
// description + legend), the controls and filters, one street profile per category and one junction profile,
// with screenshots on desktop (1440 px) and mobile (390 px).
// Output: data/scenarios/redesign/ui/content.json, screenshots docs/redesign/img/c-*.jpg.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { chromium, newPage, open, OUT, shot, words, writeJson } from "./lib.mjs";

const FX = JSON.parse(readFileSync(join(OUT, "fixtures.json")));
const PAGES = ["karte", "tabelle", "methode", "radnetz", "downloads", "quellen", "impressum"];

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

const browser = await chromium.launch();
const result = { generated: new Date().toISOString(), pages: {}, layers: {}, profiles: {}, junction: null, chrome: {} };

for (const kind of ["desktop", "mobile"]) {
  const page = await newPage(browser, kind);

  // pages
  for (const p of PAGES) {
    await open(page, `#${p}`, { settle: p === "karte" ? 3000 : 1500 });
    if (p === "tabelle") {
      await page.click('button[data-bz="Eimsbüttel"]').catch(() => {});
      await page.waitForTimeout(1500);
    }
    const img = await shot(page, `c-${p}-${kind}`);
    const full = p === "karte" ? null : await shot(page, `c-${p}-${kind}-full`, { fullPage: true, quality: 60 });
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
      banner: await page.textContent(".banner"),
      title: await page.textContent(".site-title"),
      nav: await page.$$eval("nav.main a", (as) => as.map((a) => a.innerText.trim())),
      controls_summary: await page.textContent("details.controls > summary"),
      fieldsets: await page.$$eval("#controls-body fieldset > legend", (ls) => ls.map((l) => l.innerText.trim())),
      layer_options: await page.$$eval('#controls-body input[name="layer"]', (is) => is.map((i) => i.parentElement.innerText.trim())),
      overlay_options: await page.$$eval('#controls-body input[name="ov"]', (is) => is.map((i) => i.parentElement.innerText.trim())),
      filter_text: await page.evaluate(() => document.querySelector("#controls-body details")?.innerText ?? ""),
      controls_height_desktop: await page.evaluate(() => document.querySelector("details.controls").scrollHeight),
    };
  }

  // layers: description + legend
  const layers = await page.$$eval('#controls-body input[name="layer"]', (is) => is.map((i) => i.value));
  for (const l of layers) {
    await open(page, `#karte?layer=${l}`, { settle: 3000 });
    const img = await shot(page, `c-layer-${l}-${kind}`);
    if (kind === "desktop") {
      const text = await page.textContent("#layer-text");
      const legend = await page.$$eval("#legend li", (lis) => lis.map((li) => li.innerText.trim()));
      const notes = await page.$$eval("#legend p", (ps) => ps.map((p) => p.innerText.trim()));
      const legendTop = await page.evaluate(() => Math.round(document.querySelector("#legend").getBoundingClientRect().top));
      result.layers[l] = { title: await page.evaluate((v) => document.querySelector(`input[name="layer"][value="${v}"]`).parentElement.innerText.trim(), l),
        text, legend, notes, words: words([text, ...legend, ...notes].join(" ")), legend_top_px: legendTop, image: img };
    } else {
      result.layers[l].image_mobile = img;
      result.layers[l].legend_visible_mobile = await page.evaluate(() => {
        const r = document.querySelector("#legend").getBoundingClientRect();
        return r.top < innerHeight && r.bottom > 0;
      });
    }
  }

  // profiles: one per category and the junction
  for (const [cat, p] of Object.entries(FX.profiles)) {
    await open(page, `#karte?seg=${p.id}&map=16/${p.lat}/${p.lon}`, { settle: 3500 });
    await page.waitForSelector("#panel-title", { timeout: 15_000 });
    const img = await shot(page, `c-profile-${cat}-${kind}`);
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
  await open(page, `#karte?layer=jct&jct=${j.id}&map=17/${j.lat}/${j.lon}`, { settle: 3500 });
  await page.waitForSelector("#panel-title", { timeout: 15_000 });
  const jimg = await shot(page, `c-junction-${kind}`);
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
writeJson("content.json", result);
for (const [k, v] of Object.entries(result.pages)) console.log(`page ${k.padEnd(10)} ${v.words} words, ${v.sections.length} sections`);
for (const [k, v] of Object.entries(result.layers)) console.log(`layer ${k.padEnd(6)} ${v.words} words, legend ${v.legend.length} items, mobile legend visible ${v.legend_visible_mobile}`);
for (const [k, v] of Object.entries(result.profiles)) console.log(`profile ${k.padEnd(8)} ${v.words} words, ${v.sections.length} sections, ${v.panel_height_px}px`);
console.log(`junction ${result.junction.words} words`);
console.log("errors", result.errors_desktop.length, result.errors_mobile.length);
