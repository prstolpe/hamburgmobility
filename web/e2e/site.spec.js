// Smoke tests and accessibility check (axe-core) of the built site; scripts/a11y-report.mjs writes reports/web_accessibility.md.
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { AxeBuilder } from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const search = JSON.parse(readFileSync(new URL("../../data/out/search.json", import.meta.url)));
const SEG = search.find((s) => s.name === "Hallerstraße")?.ids[0] ?? search[0].ids[0];
const meta = JSON.parse(readFileSync(new URL("../../data/out/meta.json", import.meta.url)));
const JCT = meta.cycling ? readdirSync(new URL("../../data/out/junctions/", import.meta.url)).sort()[0].replace(".json", "") : null;
const CYCLING_LAYERS = { cnet: "Radnetz (Soll)", cfac: "Radanlagen (Soll)", cgap: "Radanlagen Soll/Ist", lanes: "Fahrstreifen Soll/Ist",
  cfit: "Querschnitt passt?", jct: "Knotenpunkte", coff: "Radnetz Hamburg (amtlich)" };
const PAGES = {
  "Karte": "#karte",
  "Karte mit Steckbrief": `#karte?seg=${SEG}`,
  "Tabelle (Bezirk wählen)": "#tabelle",
  "Tabelle": "#tabelle?bz=Eimsb%C3%BCttel",
  "Methode": "#methode",
  "Radnetz": "#radnetz",
  "Karte Radanlagen Soll/Ist": "#karte?layer=cgap",
  "Karte Knotenpunkte mit Steckbrief": `#karte?layer=jct&jct=${JCT}&map=15/53.56/9.99`,
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
  await expect(page.locator("#banner-text")).toContainText("Datenstand"); // set after meta.json and search.json
  return errors;
}

test("map loads basemap and segment tiles without errors", async ({ page }) => {
  const errors = await ready(page, "#karte");
  await page.waitForFunction(() => document.querySelector("#map canvas"));
  await page.waitForTimeout(3000);
  await expect(page.locator("#legend li")).toHaveCount(6); // 5 categories in the data + rural Stadtteile
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
  await ready(page, "#tabelle?bz=Eimsb%C3%BCttel");
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

test("cycling layers switch without errors and show the draft note", async ({ page }) => {
  test.skip(!meta.cycling, "no cycling layers in this export");
  const errors = await ready(page, "#karte?map=14/53.57/9.97");
  await page.waitForFunction(() => document.querySelector("#map canvas"));
  for (const [key, label] of Object.entries(CYCLING_LAYERS)) {
    await page.getByLabel(label, { exact: true }).check();
    await expect(page).toHaveURL(new RegExp(`layer=${key}`));
    await expect(page.locator("#legend .note")).toContainText("nicht amtlich");
    await page.waitForTimeout(800);
  }
  await page.screenshot({ path: `test-results/karte-radnetz-${test.info().project.name}.png` });
  expect(errors).toEqual([]);
});

test("segment profile shows the cycling section with the cross-section sketch", async ({ page }) => {
  test.skip(!meta.cycling, "no cycling layers in this export");
  await ready(page, `#karte?seg=${SEG}`);
  const panel = page.locator("#panel");
  await expect(panel.locator("#h-rad")).toBeVisible();
  await expect(panel.locator("#h-rad")).toContainText("Radverkehr");
});

test("junction profile opens from the URL", async ({ page }) => {
  test.skip(!meta.cycling, "no cycling layers in this export");
  await ready(page, `#karte?layer=jct&jct=${JCT}`);
  const panel = page.locator("#panel");
  await expect(panel.locator("#h-jsoll")).toBeVisible();
  await expect(panel).toContainText("nicht amtlich");
  await page.screenshot({ path: `test-results/knoten-${test.info().project.name}.png` });
  await page.keyboard.press("Escape");
  await expect(page).not.toHaveURL(/jct=/);
});

test("tiles are served with HTTP range requests", async ({ request }) => {
  const files = ["tiles/segments.pmtiles", "basemap/basemap.pmtiles"];
  if (meta.cycling) files.push(meta.cycling.tiles.cycling, meta.cycling.tiles.junctions);
  for (const f of files) {
    const r = await request.get(`/${f}`, { headers: { Range: "bytes=0-126" } });
    expect(r.status(), f).toBe(206);
    expect((await r.body()).length).toBe(127);
  }
});

for (const [name, hash] of Object.entries(PAGES)) {
  test(`axe: ${name}`, async ({ page }) => {
    await ready(page, hash);
    if (hash.includes("seg=") || hash.includes("jct=")) await expect(page.locator("#panel-title")).toBeVisible();
    if (hash === "#tabelle") await expect(page.locator("#table-root button[data-bz]").first()).toBeVisible();
    if (hash.startsWith("#tabelle?")) await expect(page.locator("#table-root tbody tr").first()).toBeVisible();
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
