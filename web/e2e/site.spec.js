// Smoke tests and accessibility check (axe-core) of the built site; scripts/a11y-report.mjs writes reports/web_accessibility.md.
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { AxeBuilder } from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const search = JSON.parse(readFileSync(new URL("../../data/out/search.json", import.meta.url)));
const SEG = search.find((s) => s.name === "Hallerstraße")?.ids[0] ?? search[0].ids[0];
const meta = JSON.parse(readFileSync(new URL("../../data/out/meta.json", import.meta.url)));
const JCT = meta.cycling ? readdirSync(new URL("../../data/out/junctions/", import.meta.url)).sort()[0].replace(".json", "") : null;
const PLACE = meta.special_places?.places?.[0];  // prompts/26
const PLACE_SEG = PLACE ? JSON.parse(readFileSync(new URL(`../../data/out/${meta.special_places.file}`, import.meta.url)))
  .features.find((f) => f.properties.place === PLACE.id)?.properties.id ?? SEG : SEG;
const PAGES = {
  "Karte": "#karte",
  "Karte mit Steckbrief": `#karte?seg=${SEG}`,
  "Bezirke": "#bezirke",
  "Bezirk Eimsbüttel": "#bezirke?bz=Eimsb%C3%BCttel",
  "Bezirk mit Tabelle": "#bezirke?bz=Eimsb%C3%BCttel&tabelle=1",
  "Methode": "#methode",
  "Methode Kapitel Radnetz": "#methode/radnetz",
  "Methode Regeln": "#methode/regeln",
  "Karte Radnetz": "#karte?theme=rad",
  "Karte Fahrstreifen": "#karte?theme=platz",
  "Karte Abweichung": "#karte?theme=abweichung",
  "Karte Kreuzungen mit Steckbrief": `#karte?theme=knoten&jct=${JCT}&map=15/53.56/9.99`,
  "Besondere Orte": "#orte",
  "Karte besonderer Ort mit Steckbrief": `#karte?place=${PLACE?.id}&seg=${PLACE_SEG}`,
  "Daten": "#daten",
  "Impressum": "#impressum",
};
const results = [];

/** On mobile the level-2 details are closed: open the one holding "Warum?". */
async function openWhy(page) {
  const d = page.locator("#panel details.l2", { has: page.locator("#h-why") });
  await d.waitFor();
  if (!(await d.evaluate((e) => e.open))) await d.locator("summary").first().click();
}

async function ready(page, hash) {
  const errors = [];
  await page.addInitScript(() => { try { localStorage.setItem("sfp-intro-seen", "1"); } catch {} });
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  await page.goto(`/${hash}`);
  await expect(page.locator("#foot-version")).toContainText("Datenstand"); // set after meta.json and search.json
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
  await openWhy(page);
  await expect(panel.locator("#h-why")).toBeVisible();
  await expect(panel.locator("#panel-title")).not.toHaveText("");
  await page.screenshot({ path: `test-results/steckbrief-${test.info().project.name}.png` });
  await page.keyboard.press("Escape");
  await expect(panel).toBeHidden();
  await expect(page).not.toHaveURL(/seg=/);
});

test("theme and view switch are reflected in the URL", async ({ page }) => {
  await ready(page, "#karte");
  await page.locator('#themes button[data-theme="abweichung"]').click();
  await expect(page).toHaveURL(/theme=abweichung/);
  await page.locator('button[data-view="prio"]').click();
  await expect(page).toHaveURL(/view=prio/);
});

test("old layer link is rewritten", async ({ page }) => {
  await ready(page, "#karte?layer=prio");
  await expect(page).toHaveURL(/theme=abweichung/);
  await expect(page).toHaveURL(/view=prio/);
  await expect(page).not.toHaveURL(/layer=/);
});

test("links to switched-off views open the theme's default view (prompt 25)", async ({ page }) => {
  await ready(page, "#karte?theme=rad&view=luecken");
  await expect(page).toHaveURL(/theme=rad/);
  await expect(page).not.toHaveURL(/view=/);
  await ready(page, "#karte?layer=cfit");
  await page.reload(); // a hash-only goto does not reload; old links are rewritten on load
  await expect(page).toHaveURL(/theme=platz/);
  await expect(page).not.toHaveURL(/view=/);
  await expect(page.locator("#themes .views")).toHaveCount(0); // one view left: no view switcher
  await expect(page.locator("#layer-text")).toContainText("Fahrstreifen");
});

test("no draft banner, no news page; draft note in title and footer (prompt 25)", async ({ page }) => {
  await ready(page, "#karte");
  await expect(page.locator(".banner")).toHaveCount(0);
  await expect(page.locator(".site-title")).toContainText("Entwurf");
  await expect(page.locator(".site-foot")).toContainText("nicht amtlich");
  await expect(page.locator(".site-title img")).toHaveAttribute("alt", "HMR – Hamburg Mobility Revolution");
  await expect(page.locator('a[href="#methode/neu"]')).toHaveCount(0);
  await ready(page, "#methode/neu");
  await page.reload();
  await expect(page).toHaveURL(/#methode$/);
});

test("district page lists 7 districts and opens Eimsbüttel", async ({ page }) => {
  await ready(page, "#bezirke");
  await expect(page.locator("#bezirke-root button[data-bz]")).toHaveCount(7);
  await page.locator('#bezirke-root button[data-bz="Eimsbüttel"]').click();
  await expect(page).toHaveURL(/bz=Eimsb/);
  await expect(page.locator("#bezirke-root h1")).toContainText("Eimsbüttel");
});

test("district table on level 3 sorts by a column and opens a profile", async ({ page }) => {
  await ready(page, "#bezirke?bz=Eimsb%C3%BCttel");
  await page.locator("details.l3", { has: page.locator("button[data-show-table]") }).locator("summary").click();
  await page.locator("button[data-show-table]").click();
  await expect(page).toHaveURL(/tabelle=1/);
  const th = page.locator('th:has(button[data-sort="len"])');
  await th.locator("button").click();
  await expect(th).toHaveAttribute("aria-sort", "descending");
  await th.locator("button").press("Enter");
  await expect(th).toHaveAttribute("aria-sort", "ascending");
  await page.locator("table tbody button[data-open]").first().click();
  await expect(page.locator("#panel-title")).not.toHaveText("");
});

test("method: summary, chapter and rule details", async ({ page }) => {
  await ready(page, "#methode");
  await expect(page.locator('[data-page="methode"] h1')).not.toHaveText("");
  await page.locator('a[href="#methode/platz"]').first().click();
  await expect(page).toHaveURL(/#methode\/platz/);
  const d = page.locator('[data-page="methode"] details', { hasText: "Details und Quellen" }).first();
  await d.locator("summary").click();
  await expect(d).toHaveJSProperty("open", true);
  await expect(d.locator("code").first()).toBeVisible();
});

test("method: rule link opens the rule in the reference", async ({ page }) => {
  await ready(page, "#methode/regeln?regel=C-G30-02");
  const item = page.locator("#regel-C-G30-02");
  await expect(item).toBeVisible();
  await expect(item.locator("details")).toHaveJSProperty("open", true);
  await page.locator("#rule-q").fill("autobahn");
  await expect(page.locator("#rule-list li.rule")).not.toHaveCount(0);
  await expect(page.locator("#regel-C-G30-02")).toHaveCount(0);
});

test("old #radnetz link opens the method chapter", async ({ page }) => {
  await ready(page, "#radnetz");
  await expect(page).toHaveURL(/#methode\/radnetz/);
  await expect(page.locator('[data-page="methode"] h1')).toContainText("Radnetz");
});

test("search suggests streets and junctions and jumps to the map", async ({ page }) => {
  await ready(page, "#methode");
  await page.locator("#search").fill("Schulterblatt");
  await expect(page.locator("#search-list li").first()).toContainText("Schulterblatt");
  await expect(page.locator("#search-list li", { hasText: "Kreuzung" }).first()).toBeVisible();
  await page.locator("#search").press("Enter");
  await expect(page).toHaveURL(/#karte/);
});

test("cycling layers switch without errors and show the draft note", async ({ page }) => {
  test.skip(!meta.cycling, "no cycling layers in this export");
  const errors = await ready(page, "#karte?map=14/53.57/9.97");
  await page.waitForFunction(() => document.querySelector("#map canvas"));
  for (const theme of ["rad", "platz"]) {
    await page.locator(`#themes button[data-theme="${theme}"]`).click();
    await expect(page).toHaveURL(new RegExp(`theme=${theme}`));
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
  await panel.locator("details").evaluateAll((ds) => ds.forEach((d) => { d.open = true; }));
  await expect(panel.getByRole("heading", { name: "Radverkehr", includeHidden: true })).toHaveCount(1);
});

test("junction profile opens from the URL", async ({ page }) => {
  test.skip(!meta.cycling, "no cycling layers in this export");
  await ready(page, `#karte?theme=knoten&jct=${JCT}`);
  const panel = page.locator("#panel");
  await panel.locator("details").evaluateAll((ds) => ds.forEach((d) => { d.open = true; }));
  await expect(panel.getByRole("heading", { name: "Was ändert sich?", includeHidden: true })).toHaveCount(1);
  await expect(panel).toContainText("Kreuzung");
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
    if (hash === "#bezirke") await expect(page.locator("#bezirke-root button[data-bz]").first()).toBeVisible();
    if (hash.includes("tabelle=1")) await expect(page.locator("#table-root tbody tr").first()).toBeVisible();
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

test("arm filter: old link to a lane-split point opens its junction, a dropped one explains why", async ({ page }) => {
  // 53120722 (Rentzelstraße, carriageway split) joined 16334337 An der Verbindungsbahn / Rentzelstraße (J-M-01)
  await ready(page, "#karte?theme=knoten&jct=53120722");
  await expect(page).toHaveURL(/jct=16334337/);
  await expect(page.locator("#panel-title")).toContainText("Rentzelstraße");
  await page.goto("/#karte?theme=knoten&jct=10031912535");
  await expect(page.locator("#panel-body")).toContainText("gibt es im Entwurf nicht mehr");
});
