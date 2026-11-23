// Image renderer (prompt 28): the three formats have the right pixel size, every card has an alt text, and the same
// input gives the same image (byte-identical PNG). Uses the renderer of tools/render_card against the preview server.
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";
import { FORMATS, launch, renderCard } from "../tools/render_card.mjs";

const meta = JSON.parse(readFileSync(new URL("../../data/out/meta.json", import.meta.url)));
const SEG = "seg_fa69d3625e877ae8"; // Hoheluftchaussee (docs/map_interaction/cards_samples.txt)
const BASE = "http://localhost:4173/";
const size = (png) => [png.readUInt32BE(16), png.readUInt32BE(20)]; // PNG IHDR width, height
const sha = (b) => createHash("sha256").update(b).digest("hex");

test.describe.configure({ mode: "serial" });
test.beforeEach(({}, info) => test.skip(info.project.name !== "desktop", "renderer runs once, not per viewport project"));

test("three formats with the right size and an alt text", async () => {
  test.setTimeout(120_000);
  const browser = await launch();
  try {
    for (const [format, f] of Object.entries(FORMATS)) {
      const { png, info } = await renderCard(browser, BASE, "seg", SEG, format);
      expect(size(png), format).toEqual([f.width * f.scale, f.height * f.scale]);
      expect(info.alt).toContain("Hoheluftchaussee");
      expect(info.alt).not.toContain("undefined");
    }
    const place = meta.special_places?.places?.[0];
    if (place) expect((await renderCard(browser, BASE, "place", place.id, "og")).info.alt).toContain(place.title);
  } finally {
    await browser.close();
  }
});

test("deterministic: the same input gives the same image", async () => {
  test.setTimeout(120_000);
  const browser = await launch();
  try {
    const a = await renderCard(browser, BASE, "seg", SEG, "og");
    const b = await renderCard(browser, BASE, "seg", SEG, "og");
    expect(sha(b.png)).toBe(sha(a.png));
  } finally {
    await browser.close();
  }
});
