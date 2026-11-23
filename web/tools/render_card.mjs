// Image renderer (prompt 28, docs/map_interaction/05_renderer.md): renders segments, junctions and special places
// as cards with our own map style and data – locally with Playwright and headless MapLibre, no external service.
// Usage (from the repository root):
//   tools/render_card seg seg_0001c1adcd739b24 [--format og,portrait,a4] [--out data/cards] [--base http://localhost:4173/]
//   tools/render_card node 1026524904 --format og
//   tools/render_card place schanze_verkehrsberuhigt
//   tools/render_card --list items.txt            (one "<seg|node|place> <id>" per line, # comments allowed)
// Without --base a `vite preview` of web/dist is started on port 4179 (build first: npm --prefix web run build).
// Output per item and format: <seg_id|node_id|place_id>_<format>.png, plus .alt.txt and .json per item.
// Deterministic: fixed viewport and scale, software WebGL (SwiftShader), no animation, no date except the data date.
import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "@playwright/test";

export const FORMATS = { og: { width: 1200, height: 630, scale: 1 }, portrait: { width: 1080, height: 1350, scale: 1 }, a4: { width: 827, height: 591, scale: 2 } };
const KINDS = { seg: (id) => `seg=${id}`, node: (id) => `node=${id}`, place: (id) => `place=${id}` };
const ID = { seg: /^seg_[0-9a-f]+$/, node: /^[0-9]+$/, place: /^[a-z0-9_]+$/ };
const fileStem = (kind, id) => (kind === "seg" ? id : `${kind}_${id}`); // segment ids already start with seg_
const WEB = resolve(fileURLToPath(import.meta.url), "../..");

function parseArgs(argv) {
  const o = { items: [], formats: ["og", "portrait", "a4"], out: "data/cards", base: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--format") o.formats = argv[++i].split(",");
    else if (a === "--out") o.out = argv[++i];
    else if (a === "--base") o.base = argv[++i].replace(/\/?$/, "/");
    else if (a === "--list") {
      for (const line of readFileSync(argv[++i], "utf8").split("\n").map((l) => l.replace(/#.*/, "").trim()).filter(Boolean)) o.items.push(line.split(/\s+/));
    } else if (KINDS[a]) o.items.push([a, argv[++i]]);
    else throw new Error(`unbekanntes Argument: ${a}`);
  }
  for (const f of o.formats) if (!FORMATS[f]) throw new Error(`unbekanntes Format: ${f} (og, portrait, a4)`);
  for (const [k, id] of o.items) if (!KINDS[k] || !ID[k].test(id ?? "")) throw new Error(`ungültiges Element: ${k} ${id}`);
  if (!o.items.length) throw new Error("kein Element angegeben (seg|node|place <id> oder --list <datei>)");
  return o;
}

async function startPreview() {
  const port = 4179;
  // node + vite directly (not npx): kill() then reaches the server itself, no orphan holding the port
  const p = spawn(process.execPath, [join(WEB, "node_modules/vite/bin/vite.js"), "preview", "--port", String(port), "--strictPort"], { cwd: WEB, stdio: ["ignore", "pipe", "pipe"] });
  const base = `http://localhost:${port}/`;
  for (let i = 0; i < 100; i++) {
    try { if ((await fetch(base)).ok) return { base, stop: () => p.kill() }; } catch { /* not up yet */ }
    await new Promise((r) => setTimeout(r, 200));
  }
  p.kill();
  throw new Error("vite preview startet nicht (erst bauen: npm --prefix web run build)");
}

/** Render one card; returns the PNG buffer and the page's report ({alt, title, …}). */
export async function renderCard(browser, base, kind, id, format) {
  const f = FORMATS[format];
  const ctx = await browser.newContext({ viewport: { width: f.width, height: f.height }, deviceScaleFactor: f.scale, reducedMotion: "reduce" });
  try {
    const page = await ctx.newPage();
    await page.goto(`${base}card.html#karte?v=2&${KINDS[kind](id)}&format=${format}`);
    await page.waitForFunction(() => window.cardReady, null, { timeout: 60_000 });
    const info = await page.evaluate(() => window.cardReady);
    if (info.error) throw new Error(`${kind} ${id}: ${info.error}`);
    const png = await page.locator("#card").screenshot({ type: "png", animations: "disabled" });
    return { png, info };
  } finally {
    await ctx.close();
  }
}

export const launch = () => chromium.launch({ args: ["--use-angle=swiftshader", "--use-gl=angle", "--enable-unsafe-swiftshader", "--font-render-hinting=none"] });

async function main() {
  const o = parseArgs(process.argv.slice(2));
  const server = o.base ? { base: o.base, stop() {} } : await startPreview();
  const browser = await launch();
  mkdirSync(o.out, { recursive: true });
  try {
    for (const [kind, id] of o.items) {
      const record = { kind, id, formats: {} };
      for (const format of o.formats) {
        const { png, info } = await renderCard(browser, server.base, kind, id, format);
        const file = join(o.out, `${fileStem(kind, id)}_${format}.png`);
        writeFileSync(file, png);
        record.formats[format] = { file, sha256: createHash("sha256").update(png).digest("hex") };
        record.alt = info.alt;
        record.title = info.title;
        console.log(file);
      }
      writeFileSync(join(o.out, `${fileStem(kind, id)}.alt.txt`), `${record.alt}\n`);
      writeFileSync(join(o.out, `${fileStem(kind, id)}.json`), `${JSON.stringify(record, null, 1)}\n`);
    }
  } finally {
    await browser.close();
    server.stop();
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((err) => { console.error(`render_card: ${err.message}`); process.exit(1); });
}
