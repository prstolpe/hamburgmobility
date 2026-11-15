// Prompt 25 (cleanup 2026-11): legend variants of "Abweichung", labels above the data layers.
import { afterEach, describe, expect, it } from "vitest";
import { beforeIdFor, firstSymbolId, groups, legendHtml, setDiscLegend, sfpLayers, tuneLabels } from "../src/layers.js";
import { DEFAULTS, withView } from "../src/state.js";

const META = { categories: {}, discrepancy_types: { D1: "a", D2: "b", D3: "c" }, glossary: { terms: {} } };

describe("legend Abweichung", () => {
  afterEach(() => setDiscLegend("a"));

  it("variant a: one statement per type, strength as width, link to the explanation", () => {
    const html = legendHtml("disc", META);
    expect(html).toContain("Heute zu schnell");
    expect(html).toContain("breiter = größere Abweichung");
    expect(html).toContain('href="#methode/abweichung"');
    expect(html).toContain("Was heißt das?");
    // types differ by dash, not by colour alone
    const dashes = groups("disc", META).slice(0, 3).map((g) => JSON.stringify(g.dash));
    expect(new Set(dashes).size).toBe(3);
  });

  it("variant b: a question and a scale from passt to große Abweichung", () => {
    setDiscLegend("b");
    const html = legendHtml("disc", META);
    expect(html).toContain("Wie weit ist die Straße heute vom Ziel entfernt?");
    const labels = groups("disc", META).map((g) => g.label);
    expect(labels.slice(0, 4)).toEqual(["große Abweichung", "mittlere Abweichung", "kleine Abweichung", "passt"]);
    // strength differs by width (and the smallest class also by dash)
    const widths = groups("disc", META).slice(0, 3).map((g) => g.width);
    expect(widths[0]).toBeGreaterThan(widths[1]);
    expect(widths[1]).toBeGreaterThan(widths[2]);
  });

  it("ignores unknown variants", () => {
    setDiscLegend("x");
    expect(legendHtml("disc", META)).toContain("Heute zu schnell");
  });

  it("only the disc legend has the explanation link", () => {
    expect(legendHtml("speed", META)).not.toContain("Was heißt das?");
  });
});

describe("labels above the data", () => {
  const base = [
    { id: "earth", type: "fill" }, { id: "roads", type: "line" }, { id: "address_label", type: "symbol" },
    { id: "places_subplace", type: "symbol", paint: { "text-color": "#7a7a7a", "text-halo-width": 1 } },
    { id: "roads_labels_minor", type: "symbol", minzoom: 15, paint: {} },
  ];

  it("finds the first basemap label layer", () => {
    expect(firstSymbolId(base)).toBe("address_label");
  });

  it("inserts line, fill and circle layers below the labels, junction symbols on top", () => {
    expect(beforeIdFor({ type: "line" }, "address_label")).toBe("address_label");
    expect(beforeIdFor({ type: "circle" }, "address_label")).toBe("address_label");
    expect(beforeIdFor({ type: "symbol" }, "address_label")).toBeUndefined();
    const st = withView({ ...DEFAULTS }, "abweichung", "ziel");
    for (const l of sfpLayers(st, META)) expect(beforeIdFor(l, "x"), l.id).toBe("x");
  });

  it("gives Stadtteil names a white halo and keeps minor street names from zoom 15", () => {
    const t = tuneLabels(base);
    const sub = t.find((l) => l.id === "places_subplace");
    expect(sub.paint["text-halo-color"]).toBe("#ffffff");
    expect(sub.paint["text-halo-width"]).toBeGreaterThanOrEqual(1.5);
    expect(t.find((l) => l.id === "roads_labels_minor").minzoom).toBe(15);
    expect(t.find((l) => l.id === "earth")).toBe(base[0]);
  });
});
