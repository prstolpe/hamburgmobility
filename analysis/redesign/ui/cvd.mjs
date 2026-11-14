// Colour-vision check of the proposed tokens (prompt 24, A3), same method as analysis/review_2026_11/ui/heuristics.mjs:
// smallest CIELAB distance (ΔE76) between the colours of one legend, normal and simulated protan/deutan/tritan
// (Machado, Oliveira & Fernandes 2009, severity 1.0); plus Chromium vision-deficiency screenshots of prototype A.
// Output: data/scenarios/redesign/cvd_tokens.json, docs/redesign/img/p-cvd-*.jpg (needs the prototype server).
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { chromium, newPage, OUT, ROOT, shot, writeJson } from "./lib.mjs";

const T = JSON.parse(readFileSync(join(ROOT, "docs/redesign/tokens.json"))).color;
const LEGENDS = {
  "Aufgabe/Tempo (Ziel)": Object.fromEntries(Object.entries(T.function).filter(([k]) => !k.startsWith("$")).map(([k, v]) => [k, { color: T.speed[v.speedToken].value, dash: v.dash, width: v.width }])),
  "Tempo heute": Object.fromEntries(Object.entries(T.speed).filter(([k]) => !k.startsWith("$")).map(([k, v]) => [k, { color: v.value, dash: v.dash ?? null, width: v.width ?? 3 }])),
  "Handlungsbedarf": Object.fromEntries(Object.entries(T.need).filter(([k]) => !k.startsWith("$")).map(([k, v]) => [k, { color: v.value, dash: v.dash, width: v.width }])),
  "Radnetz": { netz: { color: T.cycling.base.value, dash: null, width: 4.5 }, uebrige: { color: T.cycling.ERSCHL.value, dash: null, width: 1.2 }, amtlich: { color: T.cycling.official.value, dash: [2, 2], width: 2 } },
};
const MACHADO = {
  protanopia: [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
  deuteranopia: [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.01182, 0.04294, 0.968881]],
  tritanopia: [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.3039]],
};
const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
const rgb = (hex) => { const n = parseInt(hex.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map(lin); };
function lab([r, g, b]) {
  const f = (t) => (t > 216 / 24389 ? Math.cbrt(t) : (24389 / 27 * t + 16) / 116);
  const x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047, y = 0.2126 * r + 0.7152 * g + 0.0722 * b, z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883;
  return [116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))];
}
const sim = (c, m) => (m ? m.map((row) => Math.min(1, Math.max(0, row[0] * c[0] + row[1] * c[1] + row[2] * c[2]))) : c);
const dE = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

const out = {};
for (const [name, table] of Object.entries(LEGENDS)) {
  const e = Object.entries(table);
  out[name] = {};
  for (const [kind, m] of [["normal", null], ...Object.entries(MACHADO)]) {
    let best = null;
    for (let i = 0; i < e.length; i++) for (let j = i + 1; j < e.length; j++) {
      if (e[i][1].color.toUpperCase() === e[j][1].color.toUpperCase()) continue; // same colour on purpose: told apart by width/dash
      const d = dE(lab(sim(rgb(e[i][1].color), m)), lab(sim(rgb(e[j][1].color), m)));
      const redundant = JSON.stringify(e[i][1].dash) !== JSON.stringify(e[j][1].dash) || e[i][1].width !== e[j][1].width;
      if (!best || d < best.dE) best = { pair: `${e[i][0]} / ${e[j][0]}`, dE: +d.toFixed(1), also_width_or_dash: redundant };
    }
    out[name][kind] = best;
  }
}

const images = [];
if (!process.argv.includes("--no-browser")) {
  const browser = await chromium.launch();
  const page = await newPage(browser, "desktop");
  await page.goto("http://localhost:5180/redesign/karte-zuerst/#karte?theme=aufgabe&view=ziel");
  await page.waitForFunction(() => window.proto, null, { timeout: 30_000 });
  await page.evaluate(() => window.proto.view.map.flyTo([9.955, 53.575], 13.5));
  await page.waitForTimeout(5000);
  const cdp = await page.context().newCDPSession(page);
  for (const type of ["none", "deuteranopia", "protanopia", "achromatopsia"]) {
    await cdp.send("Emulation.setEmulatedVisionDeficiency", { type });
    await page.waitForTimeout(400);
    images.push({ type, image: await shot(page, `p-cvd-aufgabe-${type}`, { clip: { x: 0, y: 150, width: 1060, height: 560 } }) });
  }
  await browser.close();
}
writeJson("../cvd_tokens.json", { min_pairs: out, images });
for (const [n, v] of Object.entries(out)) console.log(n, Object.entries(v).map(([k, b]) => `${k} ${b.pair} ΔE ${b.dE}${b.also_width_or_dash ? " (+Breite/Strich)" : ""}`).join(" | "));
