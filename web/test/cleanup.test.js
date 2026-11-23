// Prompt 25 (cleanup 2026-11): legend of "Abweichung" (variant a), labels above the data layers.
import { describe, expect, it } from "vitest";
import { beforeIdFor, firstSymbolId, groups, sfpLayers, tuneLabels } from "../src/layers.js";
import { legendFor } from "../src/legend_registry.js";
import { layerLegendHtml } from "../src/map_panel.js";
import { DEFAULTS as D0 } from "../src/state.js";

const UI = { inView: null, highlight: null, openWhat: new Set() };
const legendHtml = (layer, meta) => layerLegendHtml(legendFor({ ...D0, layer }, meta)[0], UI);
import { DEFAULTS, withView } from "../src/state.js";

const META = { categories: {}, discrepancy_types: { D1: "a", D2: "b", D3: "c" }, glossary: { terms: {} } };

describe("legend Abweichung (variant a)", () => {
  it("one statement per type, strength as width, link to the explanation", () => {
    const html = legendHtml("disc", META);
    expect(html).toContain("Heute zu schnell");
    expect(html).toContain("passt bereits");
    expect(html).toContain("breiter = größere Abweichung");
    expect(html).toContain('href="#methode/abweichung"');
    expect(html).toContain("Was heißt"); // prompt 28: "?" per entry
    // types differ by dash, not by colour alone
    const dashes = groups("disc", META).slice(0, 3).map((g) => JSON.stringify(g.dash));
    expect(new Set(dashes).size).toBe(3);
  });

  it("strength: three widths, steps at 1.5 and 2.5", () => {
    const w = JSON.stringify(groups("disc", META)[0].width);
    expect(w).toContain('"step"');
    expect(w).toContain(",1.5,");
    expect(w).toContain(",2.5,");
  });

  it("every view links to its method chapter (prompt 28: not only Abweichung)", () => {
    expect(legendHtml("speed", META)).toContain('href="#methode/aufgabe"');
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
