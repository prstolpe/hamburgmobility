import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { dataHtml } from "../src/datapage.js";

const meta = {
  area_label: "Hamburg",
  n_segments: 12345,
  version: "0.12.0",
  downloads: [
    { file: "segments.geojson", bytes: 2500000, text: "Abschnitte" },
    { file: "segments.parquet", bytes: 1200000, text: "Abschnitte (GeoParquet)" },
  ],
  cycling: null,
  sources: [
    { title: "Straßennetz OSM", purpose: "Geometrie", as_of: "2026-10-01", license: "ODbL 1.0", attribution: "© OpenStreetMap" },
  ],
  basemap: {
    tiles: { title: "Protomaps Basemap", license: "ODbL 1.0", attribution: "© Protomaps" },
  },
};

describe("dataHtml", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn(async () => ({ ok: true, text: async () => "## Lizenzen\n\nODbL 1.0." })));
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("has exactly one h1", async () => {
    const html = await dataHtml(meta);
    expect(html.match(/<h1[\s>]/g)).toHaveLength(1);
    expect(html).toContain("<h1>Daten</h1>");
  });

  it("contains both sections with their ids", async () => {
    const html = await dataHtml(meta);
    expect(html).toContain('<section id="daten-downloads"');
    expect(html).toContain('<section id="daten-quellen"');
  });

  it("lists download file names from the meta", async () => {
    const html = await dataHtml(meta);
    expect(html).toContain("segments.geojson");
    expect(html).toContain("segments.parquet");
  });

  it("merges the sources page without a second h1 and renders the licence markdown", async () => {
    const html = await dataHtml(meta);
    expect(html).not.toContain("Quellen und Lizenzen</h1>");
    expect(html).toContain("<h2>Datenquellen</h2>");
    expect(html).toContain("Protomaps Basemap");
    expect(html).toContain("<h2>Lizenzen</h2>");
  });
});
