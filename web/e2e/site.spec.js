// Smoke tests and accessibility check (axe-core) of the built site; scripts/a11y-report.mjs writes reports/web_accessibility.md.
import { readFileSync, writeFileSync } from "node:fs";
import { AxeBuilder } from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const search = JSON.parse(readFileSync(new URL("../../data/out/search.json", import.meta.url)));
const SEG = search.find((s) => s.name === "Hallerstraße")?.ids[0] ?? search[0].ids[0];
const PAGES = {
  "Karte": "#karte",
  "Karte mit Steckbrief": `#karte?seg=${SEG}`,
  "Tabelle": "#tabelle",
  "Methode": "#methode",
  "Downloads": "#downloads",
  "Quellen und Lizenzen": "#quellen",
  "Impressum": "#impressum",
};
const results = [];

async function ready(page, hash) {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  await page.goto(`/${hash}`);
  await expect(page.locator("#banner-text")).toContainText("Nicht amtlicher Diskussionsentwurf");
  return errors;
}

test("map loads basemap and segment tiles without errors", async ({ page }) => {
  const errors = await ready(page, "#karte");
  await page.waitForFunction(() => document.querySelector("#map canvas"));
  await page.waitForTimeout(3000);
  await expect(page.locator("#legend li")).toHaveCount(5);
  await page.screenshot({ path: `test-results/karte-${test.info().project.name}.png` });
  expect(errors).toEqual([]);
});

test("profile opens from the URL and shows reasons and feedback note", async ({ page }) => {
  await ready(page, `#karte?seg=${SEG}`);
  const panel = page.locator("#panel");
  await expect(panel).toBeVisible();
  await expect(panel.locator("#h-why")).toBeVisible();
  await expect(panel.locator("#panel-title")).not.toHaveText("");
  await page.screenshot({ path: `test-results/steckbrief-${test.info().project.name}.png` });
  await page.keyboard.press("Escape");
  await expect(panel).toBeHidden();
  await expect(page).not.toHaveURL(/seg=/);
});

test("layer switch and filter are reflected in the URL", async ({ page }) => {
  await ready(page, "#karte");
  await page.getByLabel("Diskrepanz", { exact: true }).check();
  await expect(page).toHaveURL(/layer=disc/);
  await page.getByText("Filter", { exact: true }).click();
  await page.getByLabel("Stadtstraße 30 (GOW30)").check();
  await expect(page).toHaveURL(/cat=GOW30/);
});

test("table is sortable and opens a profile", async ({ page }) => {
  await ready(page, "#tabelle");
  await expect(page.locator("#table-root tbody tr")).toHaveCount(100);
  await page.getByRole("button", { name: "Straße", exact: true }).click();
  await expect(page.locator("th[aria-sort='descending'] button")).toHaveText("Straße");
  await page.locator("#table-root tbody button[data-open]").first().click();
  await expect(page.locator("#panel")).toBeVisible();
});

test("search suggests streets and jumps to the map", async ({ page }) => {
  await ready(page, "#methode");
  await page.locator("#search").fill("Hallerstr");
  await expect(page.locator("#search-list li").first()).toContainText("Hallerstraße");
  await page.locator("#search").press("Enter");
  await expect(page).toHaveURL(/#karte/);
});

test("tiles are served with HTTP range requests", async ({ request }) => {
  for (const f of ["tiles/segments.pmtiles", "basemap/basemap.pmtiles"]) {
    const r = await request.get(`/${f}`, { headers: { Range: "bytes=0-126" } });
    expect(r.status(), f).toBe(206);
    expect((await r.body()).length).toBe(127);
  }
});

for (const [name, hash] of Object.entries(PAGES)) {
  test(`axe: ${name}`, async ({ page }) => {
    await ready(page, hash);
    if (hash.includes("seg=")) await expect(page.locator("#panel-title")).toBeVisible();
    if (hash === "#tabelle") await expect(page.locator("#table-root tbody tr").first()).toBeVisible();
    if (hash.startsWith("#karte")) await page.waitForTimeout(1500);
    const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze();
    results.push({ project: test.info().project.name, name, violations: r.violations.map((v) => ({
      id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length, target: v.nodes[0]?.target?.join(" ") })),
    passes: r.passes.length, incomplete: r.incomplete.length });
    expect(r.violations.filter((v) => ["critical", "serious"].includes(v.impact)), JSON.stringify(r.violations, null, 1)).toEqual([]);
  });
}

test.afterAll(async ({}, info) => {
  if (!results.length) return;
  const path = new URL(`../test-results/axe-${info.project.name}.json`, import.meta.url);
  writeFileSync(path, JSON.stringify(results, null, 1));
});
