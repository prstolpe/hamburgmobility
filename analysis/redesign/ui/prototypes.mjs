// Screenshots and checks of the two redesign prototypes (prompt 24, A3): key states on desktop (1440) and mobile (390),
// console errors, axe-core (WCAG 2.2 AA tags), words and height of profile levels. Needs the prototype server:
//   cd web && npx vite --config ../prototypes/vite.config.mjs
// Output: data/scenarios/redesign/ui/prototypes.json, screenshots docs/redesign/img/p-*.jpg.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { AxeBuilder } from "../../../web/node_modules/@axe-core/playwright/dist/index.mjs";
import { chromium, newPage, OUT, shot, words, writeJson } from "./lib.mjs";

const PBASE = process.env.SFP_PROTO_URL || "http://localhost:5180/redesign/";
const FX = JSON.parse(readFileSync(join(OUT, "fixtures.json")));
const SEG = FX.segment.id; // Hallerstraße
const JCT = FX.junction.id;

async function go(page, path, settle = 4500) {
  await page.goto(new URL(path, PBASE).href);
  await page.waitForFunction(() => window.proto, null, { timeout: 30_000 });
  await page.waitForTimeout(settle);
}
const A = (fn) => async (p) => { await p.evaluate(fn); await p.waitForTimeout(3500); };

const STATES = [
  ["a", "Start Aufgabe und Tempo", "karte-zuerst/", null],
  ["a", "Tempo heute", "karte-zuerst/#karte?theme=aufgabe&view=heute", null],
  ["a", "Steckbrief Hallerstrasse", `karte-zuerst/#karte?theme=aufgabe&seg=${SEG}`, A(() => window.proto.view.map.flyTo([9.9874, 53.5726], 15.5))],
  ["a", "Steckbrief Ebene 3 offen", `karte-zuerst/#karte?theme=aufgabe&seg=${SEG}`, async (p) => { await p.locator("details.l3 > summary").click(); await p.waitForTimeout(800); }],
  ["a", "Radnetz Luecken", "karte-zuerst/#karte?theme=rad&view=luecken", null],
  ["a", "Kreuzung", `karte-zuerst/#karte?theme=knoten&jct=${JCT}`, A(() => window.proto.view.map.flyTo([9.9601, 53.5637], 16.5))],
  ["a", "alter Link layer=cgap", "karte-zuerst/#karte?layer=cgap", null],
  ["b", "Start Bezirk", "ueberblick-zuerst/", null],
  ["b", "Top-Liste Kreuzung geoeffnet", "ueberblick-zuerst/", async (p) => { await p.locator('button[data-kind="junctions"]').nth(2).click(); await p.waitForTimeout(4500); }],
  ["b", "Ebene 3 Bezirksvergleich", "ueberblick-zuerst/", async (p) => { await p.locator("details.l3 > summary").click(); await p.waitForTimeout(600); }],
];

const browser = await chromium.launch();
const res = [];
for (const kind of ["desktop", "mobile"]) {
  for (const [variant, label, path, act] of STATES) {
    const page = await newPage(browser, kind);
    await go(page, path);
    if (act) await act(page);
    const name = `p-${variant}-${kind}-${label.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/-$/, "")}`;
    const full = label.startsWith("Start Bezirk") || label.startsWith("Ebene 3 Bezirk");
    const image = await shot(page, name, full ? { fullPage: true, quality: 62 } : {});
    const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
    const axe = r.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help }));
    const prof = await page.evaluate(() => {
      const panel = document.querySelector(".panel");
      if (!panel || panel.hidden) return null;
      const txt = (sel) => panel.querySelector(sel)?.innerText ?? "";
      const l1 = [...panel.querySelectorAll(".meta, #panel-title, .l1")].map((e) => e.innerText).join(" ");
      const l2 = panel.querySelector("details.l2");
      const vis = panel.getBoundingClientRect().height;
      return { l1: l1, l2: l2?.open ? txt("details.l2") : "", l3_open: !!panel.querySelector("details.l3")?.open,
        l1_bottom_px: Math.round(panel.querySelector(".l1")?.getBoundingClientRect().bottom ?? 0), panel_visible_px: Math.round(vis),
        panel_scroll_px: panel.scrollHeight, map_visible: (() => { const m = document.querySelector(".map").getBoundingClientRect(); return Math.round(Math.max(0, Math.min(innerHeight, m.bottom) - Math.max(0, m.top))); })() };
    });
    const legendVisible = await page.evaluate(() => { const l = document.querySelector(".legend"); if (!l || l.offsetParent === null) return null; const r = l.getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; });
    const url = await page.evaluate(() => location.hash);
    res.push({ variant, kind, label, path, url, image, errors: page.errors, external_hosts: [...page.external], axe, legend_visible: legendVisible,
      profile: prof && { l1_words: words(prof.l1), l2_words: words(prof.l2), l1_bottom_px: prof.l1_bottom_px, panel_visible_px: prof.panel_visible_px,
        panel_scroll_px: prof.panel_scroll_px, map_visible_px: prof.map_visible, l3_open: prof.l3_open } });
    await page.context().close();
  }
}
await browser.close();
writeJson("prototypes.json", { base: PBASE, generated: new Date().toISOString(), results: res });
console.log("external hosts:", [...new Set(res.flatMap((r) => r.external_hosts))]);
for (const r of res) console.log(`${r.variant} ${r.kind.padEnd(7)} ${r.label.padEnd(30)} errors ${r.errors.length} axe ${r.axe.map((a) => `${a.id}:${a.impact}:${a.nodes}`).join(",") || "0"} legend ${r.legend_visible} ${r.profile ? `L1 ${r.profile.l1_words}w L2 ${r.profile.l2_words}w` : ""} ${r.url}`);
