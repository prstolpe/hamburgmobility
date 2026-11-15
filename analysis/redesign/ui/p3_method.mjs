// Screenshots of the method page, Part B package 3 (prompt 24): summary, one chapter, the rule reference with one rule
// open, on desktop (1440 px) and mobile (390 px). Output: docs/redesign/img/p3-*.jpg.
import { chromium, newPage, open, shot } from "./lib.mjs";

const VIEWS = [["methode", "#methode"], ["kapitel", "#methode/radnetz"], ["regel", "#methode/regeln?regel=C-G30-02"]];
// "Was ist neu" (#methode/neu) was removed in prompt 25
const browser = await chromium.launch();
const errors = [];
for (const kind of ["desktop", "mobile"]) {
  const page = await newPage(browser, kind);
  await page.addInitScript(() => { try { localStorage.setItem("sfp-intro-seen", "1"); } catch {} });
  for (const [name, hash] of VIEWS) {
    await open(page, hash, { settle: 800 });
    const target = name === "regel" ? page.locator("#regel-C-G30-02") : null;
    console.log(await shot(page, `p3-${name}-${kind}`, target ? {} : { fullPage: kind === "mobile" ? false : false }));
  }
  errors.push(...page.errors, ...[...page.external].map((h) => `external: ${h}`));
}
await browser.close();
console.log(errors.length ? errors : "no console errors, no external requests");
