// Shared helpers for the UI review (prompt 21b, phase 3). Playwright and axe come from web/node_modules;
// nothing in web/ is changed. Base URL: the built site served by `vite preview` (default) or SFP_BASE_URL.
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium, devices } from "../../../web/node_modules/playwright/index.mjs";

export { chromium, devices };
export const ROOT = join(dirname(fileURLToPath(import.meta.url)), "../../..");
export const IMG = join(ROOT, "docs/review/2026-11/img");
export const OUT = join(ROOT, "data/scenarios/review_ui");
export const BASE = process.env.SFP_BASE_URL || "http://localhost:4173/";
mkdirSync(IMG, { recursive: true });
mkdirSync(OUT, { recursive: true });

export const VIEWPORTS = {
  desktop: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
  mobile: { ...devices["Pixel 7"], deviceScaleFactor: 1.5 },
};

export async function newPage(browser, kind) {
  const ctx = await browser.newContext({ ...VIEWPORTS[kind], locale: "de-DE" });
  const page = await ctx.newPage();
  page.errors = [];
  page.on("pageerror", (e) => page.errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") page.errors.push(m.text()); });
  return page;
}

/** Load a hash route and wait until meta.json, search.json and (on the map page) the canvas are ready. */
export async function open(page, hash = "#karte", { settle = 2500 } = {}) {
  await page.goto(new URL(hash, BASE).href);
  await page.waitForFunction(() => document.querySelector("#banner-text")?.textContent.includes("Datenstand"), null, { timeout: 30_000 });
  if (hash.startsWith("#karte")) await page.waitForFunction(() => document.querySelector("#map canvas"), null, { timeout: 30_000 });
  await page.waitForTimeout(settle);
}

/** Screenshot as JPEG (small enough for git); returns the path relative to docs/review/2026-11. */
export async function shot(page, name, opts = {}) {
  const file = join(IMG, `${name}.jpg`);
  await page.screenshot({ path: file, type: "jpeg", quality: 72, ...opts });
  return `img/${name}.jpg`;
}

export function writeJson(name, data) {
  const file = join(OUT, name);
  writeFileSync(file, JSON.stringify(data, null, 2));
  return file;
}

export const siteLink = (hash) => `https://hamburgmobility.de/${hash}`;
