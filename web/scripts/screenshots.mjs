// Screenshots of maps and pages for review reports (prompt 25): desktop 1440 px and mobile 390 px, map zoom 11/13/15.
// Usage: node scripts/screenshots.mjs <out-dir> <prefix> [base-url] [only]   (needs a running `npm run preview`)
// base-url may carry preview switches, e.g. http://localhost:4173/?kopf=A&legende=b; only = comma list of names.
// JPEG (quality 75) keeps the report images small enough for git.
import { mkdirSync } from "node:fs";
import { chromium } from "@playwright/test";

const [outDir, prefix = "shot", base = "http://localhost:4173/", only] = process.argv.slice(2);
if (!outDir) { console.error("usage: node scripts/screenshots.mjs <out-dir> <prefix> [base-url]"); process.exit(1); }
mkdirSync(outDir, { recursive: true });

const CENTER = "53.5560/9.9700"; // Altona/St. Pauli/Eimsbüttel: many Stadtteil labels
const MAPS = {
  aufgabe: "theme=aufgabe",
  abweichung: "theme=abweichung",
  platz: "theme=platz",
  "platz-fahrstreifen": "theme=platz&view=fahrstreifen",
  rad: "theme=rad",
  "rad-radweg": "theme=rad&view=radweg",
  "rad-luecken": "theme=rad&view=luecken",
  knoten: "theme=knoten",
};
const ZOOMS = [11, 13, 15];
const PAGES = { methode: "#methode", "methode-neu": "#methode/neu", impressum: "#impressum" };
const VIEWPORTS = { desktop: { width: 1440, height: 900 }, mobile: { width: 390, height: 844 } };

const browser = await chromium.launch();
const errors = [];
for (const [vp, size] of Object.entries(VIEWPORTS)) {
  const ctx = await browser.newContext({ viewport: size, deviceScaleFactor: vp === "mobile" ? 2 : 1 });
  await ctx.addInitScript(() => { try { localStorage.setItem("sfp-intro-seen", "1"); } catch {} });
  const shots = [
    ...Object.entries(MAPS).flatMap(([name, q]) => ZOOMS.map((z) => [`${name}-z${z}`, `#karte?${q}&map=${z}/${CENTER}`])),
    ...Object.entries(PAGES),
  ].filter(([name]) => !only || only.split(",").some((o) => name.startsWith(o)));
  for (const [name, hash] of shots) {
    const page = await ctx.newPage();
    page.on("pageerror", (e) => errors.push(`${vp} ${name}: ${e.message}`));
    page.on("console", (m) => { if (m.type() === "error") errors.push(`${vp} ${name}: ${m.text()}`); });
    await page.goto(`${base}${hash}`);
    await page.waitForLoadState("networkidle").catch(() => {});
    await page.waitForTimeout(hash.startsWith("#karte") ? 2500 : 800);
    const file = `${outDir}/${prefix}-${vp}-${name}.jpg`;
    await page.screenshot({ path: file, type: "jpeg", quality: 75 });
    console.log(file);
    await page.close();
  }
  await ctx.close();
}
await browser.close();
if (errors.length) { console.log("\nConsole errors:"); for (const e of errors) console.log(e); }
