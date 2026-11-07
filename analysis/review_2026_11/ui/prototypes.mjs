// Screenshots and checks of the three prototypes (prompt 21b, phase 3.2): key states on desktop and smartphone,
// console errors, axe-core. Needs the prototype server: cd web && npx vite --config ../prototypes/vite.config.mjs
// Output: data/scenarios/review_ui/prototypes.json, screenshots docs/review/2026-11/img/p-*.jpg.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { AxeBuilder } from "../../../web/node_modules/@axe-core/playwright/dist/index.mjs";
import { chromium, newPage, OUT, shot, writeJson } from "./lib.mjs";

const PBASE = process.env.SFP_PROTO_URL || "http://localhost:5180/";
const FX = JSON.parse(readFileSync(join(OUT, "fixtures.json")));
const SEG = FX.segment.id; // Hallerstraße, GOW30 (GOW50 in the scenario)
const JCT = "8541215407";

async function go(page, path, settle = 5000) {
  await page.goto(new URL(path, PBASE).href);
  await page.waitForFunction(() => window.proto, null, { timeout: 30_000 });
  await page.waitForTimeout(settle);
}
const openSeg = async (page, id = SEG) => { await page.evaluate((id) => window.proto.openSeg(id), id); await page.waitForTimeout(1200); };
const jumpTo = async (page, lon, lat, zoom) => { await page.evaluate(([lo, la, z]) => window.proto.map.jumpTo({ center: [lo, la], zoom: z }), [lon, lat, zoom]); await page.waitForTimeout(2500); };

const STATES = [
  ["themen", "Start: Straßenfunktion", "themen/#funktion/cat", null],
  ["themen", "Handlungsbedarf mit Liste und Steckbrief", "themen/#bedarf/need", async (p) => { await p.locator(".t-list button").nth(1).click(); await p.waitForTimeout(3000); }],
  ["themen", "Radnetz mit Netzlücken", "themen/#radnetz/cnet", null],
  ["themen", "Datenqualität", "themen/#qualitaet/conf", null],
  ["vergleich", "Tempo heute / Soll", "vergleich/#tempo", null],
  ["vergleich", "Radanlagen heute / Soll (Ausschnitt)", "vergleich/#rad", async (p) => jumpTo(p, 9.975, 53.572, 14.5)],
  ["vergleich", "Szenario mit Steckbrief und Querschnitt", "vergleich/#szenario", async (p) => { await jumpTo(p, FX.segment.lon, FX.segment.lat, 14.5); await openSeg(p); }],
  ["gefuehrt", "Schritt 1", "gefuehrt/#schritt1", null],
  ["gefuehrt", "Schritt 2", "gefuehrt/#schritt2", null],
  ["gefuehrt", "Bezirksübersicht", "gefuehrt/#schritt3", null],
  ["gefuehrt", "Karte nach Klick auf eine Kreuzung", "gefuehrt/#schritt3", async (p) => { await p.locator(`button[data-jct="${JCT}"]`).click(); await p.waitForTimeout(5000); }],
];

const browser = await chromium.launch();
const res = [];
for (const kind of ["desktop", "mobile"]) {
  for (const [concept, label, path, act] of STATES) {
    const page = await newPage(browser, kind);
    await go(page, path);
    if (act) await act(page);
    const name = `p-${concept}-${kind}-${label.toLowerCase().replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/ß/g, "ss").replace(/[^a-z0-9]+/g, "-").replace(/-$/, "")}`;
    const full = concept === "gefuehrt" && label === "Bezirksübersicht";
    const image = await shot(page, name, full ? { fullPage: true } : {});
    let axe = null;
    if (kind === "desktop" || label.includes("Steckbrief")) {
      const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
      axe = r.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length }));
    }
    // profile metrics (when open): position of the short answer and total length
    const sb = await page.evaluate(() => {
      const s = document.querySelector("#sheet");
      if (!s || s.hidden) return null;
      const t = s.querySelector("#sheet-body").innerText;
      const vis = innerWidth <= 760 ? s.getBoundingClientRect().height : s.clientHeight;
      return { words: (t.match(/\S+/g) ?? []).length, screens: +(s.scrollHeight / vis).toFixed(1), answer_bottom_px: Math.round(s.querySelector(".sb-answer")?.getBoundingClientRect().bottom ?? 0),
        change_bottom_px: Math.round(s.querySelector("#sb-h-change")?.closest("section").getBoundingClientRect().bottom ?? 0), viewport: innerHeight };
    });
    res.push({ concept, kind, label, path, image, errors: page.errors, axe, steckbrief: sb });
    console.log(kind, concept, label, "errors", page.errors.length, "axe", axe?.length ?? "-", sb ? JSON.stringify(sb) : "");
    await page.context().close();
  }
}
await browser.close();
writeJson("prototypes.json", { base: PBASE, generated: new Date().toISOString(), results: res });
