// Shared helpers for the redesign analysis (prompt 24, A1). Same approach as analysis/review_2026_11/ui/lib.mjs:
// Playwright from web/node_modules, nothing in web/ is changed; base URL = built site via `vite preview` or SFP_BASE_URL.
// Viewports as the prompt asks: desktop 1440 px, mobile 390 px.
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "../../../web/node_modules/playwright/index.mjs";

export { chromium };
export const ROOT = join(dirname(fileURLToPath(import.meta.url)), "../../..");
export const IMG = join(ROOT, "docs/redesign/img");
export const OUT = join(ROOT, "data/scenarios/redesign/ui");
export const BASE = process.env.SFP_BASE_URL || "http://localhost:4173/";
mkdirSync(IMG, { recursive: true });
mkdirSync(OUT, { recursive: true });

export const VIEWPORTS = {
  desktop: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
  mobile: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 1.5, isMobile: true, hasTouch: true },
};

export async function newPage(browser, kind) {
  const ctx = await browser.newContext({ ...VIEWPORTS[kind], locale: "de-DE" });
  const page = await ctx.newPage();
  page.errors = [];
  page.on("pageerror", (e) => page.errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") page.errors.push(m.text()); });
  return page;
}

/** Load a hash route and wait until meta.json is loaded and (on the map page) the canvas exists. */
export async function open(page, hash = "#karte", { settle = 2500 } = {}) {
  await page.goto(new URL(hash, BASE).href);
  await page.waitForFunction(() => document.querySelector("#banner-text")?.textContent.includes("Datenstand"), null, { timeout: 30_000 });
  if (hash.startsWith("#karte")) await page.waitForFunction(() => document.querySelector("#map canvas"), null, { timeout: 30_000 });
  await page.waitForTimeout(settle);
}

/** Screenshot as JPEG; returns the path relative to docs/redesign. */
export async function shot(page, name, opts = {}) {
  await page.screenshot({ path: join(IMG, `${name}.jpg`), type: "jpeg", quality: 72, ...opts });
  return `img/${name}.jpg`;
}

export function writeJson(name, data) {
  const file = join(OUT, name);
  writeFileSync(file, JSON.stringify(data, null, 2));
  return file;
}

export const words = (t) => (t.match(/\S+/g) ?? []).length;
