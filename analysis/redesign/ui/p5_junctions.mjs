// Screenshot of the junction view after the arm filter (Part B package 5): An der Verbindungsbahn / Rentzelstraße /
// Schröderstiftstraße, which had five junction symbols before (four carriageway split points), desktop and mobile.
// Output: docs/redesign/img/p5-knoten-*.jpg.
import { chromium, newPage, open, shot } from "./lib.mjs";

const browser = await chromium.launch();
for (const kind of ["desktop", "mobile"]) {
  const page = await newPage(browser, kind);
  await page.addInitScript(() => { try { localStorage.setItem("sfp-intro-seen", "1"); } catch {} });
  await open(page, "#karte?theme=knoten&map=17.00/53.56429/9.97732", { settle: 4000 });
  console.log(await shot(page, `p5-knoten-${kind}`), page.errors);
}
await browser.close();
