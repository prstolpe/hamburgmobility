// Cycling layers, legends, profiles and URL state (prompts/21_web_validation_cycling.md).
import { describe, expect, it } from "vitest";
import { CYCLING_LAYERS, groups, LAYER_INFO, legendHtml, sfpLayers } from "../src/layers.js";
import { allColors, CASING, contrast, JUNCTION_STYLE, SHAPES } from "../src/palette.js";
import { crossSectionSvg, junctionHtml, profileHtml } from "../src/panel.js";
import { DEFAULTS, LAYERS, parseHash, toHash } from "../src/state.js";

const META = {
  categories: {}, discrepancy_types: {}, width_classes_m: {}, feasibility: {}, github_repo: null, feedback_email: null,
  cycling: {
    disclaimer: "Radnetz-Entwurf – nicht amtlich",
    cycle_categories: { RSV: "Radschnellverbindung", HAUPT: "Radroute", BASIS: "Bezirksroute", ERSCHL: "Quartiersnetz" },
    no_cycle_category: "nicht im Soll-Radnetz",
    facility: { separated_oneway_both: "Radweg beidseitig", separated_twoway: "Zweirichtungsradweg", cycle_lane: "Radfahrstreifen",
      cycle_street: "Fahrradstraße", mixed: "Mischverkehr", own_path: "eigene Trasse" },
    gap: { none: "passt", missing: "fehlt", wrong_type: "anderer Typ", partial: "teilweise", too_narrow: "zu schmal", not_assessed: "nicht bewertet" },
    fit: { fits: "passt", fits_after_degrade: "passt nach Abstrichen", does_not_fit: "passt nicht" },
    lanes: { shared: "Mischverkehr", fewer: "weniger", same: "gleich", more: "mehr", ist_unknown: "unbekannt" },
    junction_group: { roundabout: "Kreisverkehr", signal: "Ampel", priority: "Vorfahrt", continuous: "Gehweg", equal: "rechts vor links",
      grade_separated: "Brücke", none: "kein Typ" },
    official_status: { Bestand: "Bestand", "In Arbeit": "in Arbeit", planned: "geplant" },
    principles: { cohesion: "Zusammenhang", directness: "Direktheit", safety: "Sicherheit", comfort: "Komfort", attractiveness: "Attraktivität" },
    elements: { sidewalk: { label: "Gehweg", color: "#d9d4c7" }, cycle_track: { label: "Radweg", color: "#c0392b" },
      carriageway: { label: "Fahrbahn", color: "#555b61" } },
    tiles: { cycling: "tiles/cycling.pmtiles", junctions: "tiles/junctions.pmtiles" },
    sensitivity: { runs: 82, delta: 0.2 },
  },
};

describe("URL state for cycling", () => {
  it("knows the cycling layers and the Radnetz page", () => {
    for (const l of CYCLING_LAYERS) expect(LAYERS).toContain(l);
    expect(parseHash("#radnetz").page).toBe("radnetz");
  });

  it("round-trips a junction id", () => {
    const s = { ...DEFAULTS, layer: "jct", jct: "1026524904" };
    expect(parseHash(toHash(s))).toEqual(s);
    expect(toHash(s)).toContain("jct=1026524904");
  });

  it("rejects invalid junction ids", () => {
    expect(parseHash("#karte?jct=<x>").jct).toBeNull();
  });
});

describe("cycling layers", () => {
  it("each layer has a title and explanatory text", () => {
    for (const l of CYCLING_LAYERS) {
      expect(LAYER_INFO[l].title).toBeTruthy();
      expect(LAYER_INFO[l].text).toBeTruthy();
    }
  });

  it("line groups differ in dash or width, not only colour (colour-blind safe)", () => {
    for (const l of CYCLING_LAYERS.filter((x) => x !== "jct")) {
      const gs = groups(l, META).filter((g) => !g.reference);
      const keys = gs.map((g) => `${g.width}|${JSON.stringify(g.dash)}`);
      expect(new Set(keys).size, l).toBe(keys.length);
    }
  });

  it("junction groups have distinct shapes", () => {
    const shapes = Object.values(JUNCTION_STYLE).map((s) => s.shape);
    expect(new Set(shapes).size).toBe(shapes.length);
    for (const s of shapes) expect(SHAPES[s]).toBeTruthy();
  });

  it("new colours keep 3:1 contrast against the casing", () => {
    for (const c of allColors()) expect(contrast(c, CASING), c).toBeGreaterThanOrEqual(3);
  });

  it("uses the cycling tile sources and the Bezirk filter", () => {
    const ls = sfpLayers({ ...DEFAULTS, layer: "cfac", bz: "Altona" }, META);
    const main = ls.filter((l) => l.id.startsWith("main-"));
    expect(main.length).toBeGreaterThan(0);
    for (const l of main) {
      expect(l.source).toBe("cyc");
      expect(l["source-layer"]).toBe("cycle_segments");
      expect(JSON.stringify(l.filter)).toContain("Altona");
    }
    const jct = sfpLayers({ ...DEFAULTS, layer: "jct" }, META).filter((l) => l.id.startsWith("main-"));
    expect(jct.every((l) => l.source === "jct" && l.type === "symbol")).toBe(true);
  });

  it("the official layer shows the Soll network as grey reference", () => {
    const gs = groups("coff", META);
    expect(gs.some((g) => g.reference && g.srcLayer === "cycle_network")).toBe(true);
    expect(gs.filter((g) => g.srcLayer === "cycle_official").length).toBe(3);
  });

  it("legend carries the draft note and shapes for junctions", () => {
    const html = legendHtml("jct", META);
    expect(html).toContain("Radnetz-Entwurf – nicht amtlich");
    expect(html).toContain("<path");
    expect(legendHtml("cnet", META)).toContain("Radroute");
    expect(legendHtml("cat", META)).not.toContain("Radnetz-Entwurf");
  });
});

describe("cross-section sketch", () => {
  const elements = [{ element: "sidewalk", width_m: 2.5 }, { element: "cycle_track", width_m: 2.0 },
    { element: "carriageway", width_m: 6.5 }, { element: "cycle_track", width_m: 0 }];

  it("draws one bar per element with width, scaled, with an accessible title", () => {
    const svg = crossSectionSvg(elements, 12.0, META);
    expect((svg.match(/<rect /g) || []).length).toBe(3);
    expect(svg).toContain('role="img"');
    expect(svg).toContain("Soll-Bedarf 11,0 m");
    expect(svg).toContain("verfügbar 12,0 m");
    expect(svg).toContain("Gehweg 2,5");
  });

  it("returns nothing without elements", () => {
    expect(crossSectionSvg([], null, META)).toBe("");
  });
});

const CYCLING_BLOCK = {
  cycle_cat: { code: "HAUPT", label: "Radroute" },
  facility: { soll: "separated_oneway_both", soll_text: "Radweg beidseitig", ist: "cycle_lane", ist_text: "Radfahrstreifen",
    osm_ist_text: "Radfahr- oder Schutzstreifen", gap: "wrong_type", gap_text: "anderer Typ", fallback_used: false },
  width: { soll_m: 2.5, ist_m: null, de_m: 2.0, nl_m: 3.0 },
  side: "both", side_text: "auf beiden Straßenseiten",
  lanes: { soll: "1", ist: 2, change: "fewer", change_text: "weniger Kfz-Fahrstreifen als heute", bus_lane: false, median: false },
  profile: { elements: [{ element: "sidewalk", width_m: 3.0 }, { element: "carriageway", width_m: 6.5 }], required_m: 9.5,
    available_m: 12.0, fit: "fits_after_degrade", fit_text: "passt nach Abstrichen",
    steps: [{ step: "D1", text: "Parken entfernen" }], cat_change_proposal: null },
  flags: ["Bäume in Baumscheiben"], confidence: { facility: "mittel", profile: "mittel" },
  principles: { category: "HAUPT", ist: { cohesion: 1, directness: 0.5, safety: 0.25, comfort: 0.75, attractiveness: 0.5, score: 0.55 },
    soll: { cohesion: 1, directness: 0.5, safety: 1, comfort: 1, attractiveness: 0.5, score: 0.85 } },
  robustness: { n_runs: 82, facility_changes: 2, lanes_changes: 0, type_changes: 0, delta: 0.2,
    triggers: { facility: ["widths_m.project_target.separated_oneway.HAUPT −20%"], lanes: [] } },
};

describe("segment profile with cycling block", () => {
  const base = {
    id: "seg_1", name: "Hallerstraße", bezirk: "Eimsbüttel", length_m: 120, version: "v",
    category: { code: "GOW50", label: "Stadtmagistrale", text: "x", proposed: "GOW50", corrected: false },
    reasons: [], confidence: { level: "hoch", summary: "", reasons: [] }, ist: {}, crosssection: { width_p10_m: null },
    coherence: [], sources: [],
    discrepancy: { type: null, max: 0, speed: 0, design: 0, use: null, priority: 0, text: "keine", unknown_checks: [],
      crashes: { ped_cyc: 0, severe_fatal: 0, years: "2021–2025" } },
  };

  it("shows category, facility with DE/NL widths, lanes, sketch, steps, principles, robustness", () => {
    const html = profileHtml({ ...base, cycling: CYCLING_BLOCK }, META, "https://example.org/");
    expect(html).toContain('id="h-rad"');
    expect(html).toContain("Radroute");
    expect(html).toContain("Radweg beidseitig");
    expect(html).toContain("DE-Regelmaß 2,00 m");
    expect(html).toContain("NL-Hauptnetz 3,00 m");
    expect(html).toContain("weniger Kfz-Fahrstreifen als heute");
    expect(html).toContain("<svg");
    expect(html).toContain("Parken entfernen");
    expect(html).toContain("<caption>");
    expect(html).toContain("Sicherheit");
    expect(html).toContain("2 von 82");
    expect(html).toContain("Radnetz-Entwurf – nicht amtlich");
  });

  it("leaves the section out without cycling data", () => {
    expect(profileHtml(base, META, "u")).not.toContain('id="h-rad"');
    expect(profileHtml({ ...base, cycling: CYCLING_BLOCK }, { ...META, cycling: null }, "u")).not.toContain('id="h-rad"');
  });
});

describe("junction profile", () => {
  const j = {
    id: "123", names: "Hauptstraße / <Nebenweg>", bezirk: "Altona", pair: "GOW50+ETW30",
    legs: [{ name: "Hauptstraße", cat: "GOW50", cycle_cat: { code: "HAUPT", label: "Radroute" }, facility_text: "Radweg beidseitig", dtv: 30000 }],
    entering_dtv: 15000, space_radius_m: 12.5, tram: false, signal_ist: false,
    soll: { code: "continuous_footway_exit", text: "durchgehender Gehweg", group: "continuous" },
    proposed: { code: "continuous_footway_exit", text: "durchgehender Gehweg" },
    ist: { code: "none_mapped", text: "nichts erfasst" }, result: { code: "not_checkable", text: "nicht prüfbar" },
    action_needed: false, priority_rank: null, rule: { id: "J-04", text: "Regel J-04 ergibt hier: durchgehender Gehweg" },
    treatment: "Mittelinsel für die Querung.", treatment_ids: ["JC-04"], conflicts: ["Kfz-Menge fehlt an einem Arm"],
    confidence: { code: "medium", text: "mittel" }, top_cycle_cat: { code: "HAUPT", label: "Radroute" },
    crashes: { cyc: 2, cyc_severe: 1 }, override: null, version: "v",
    robustness: { n_runs: 82, facility_changes: 0, lanes_changes: 0, type_changes: 0, delta: 0.2, triggers: { type: [] } },
  };

  it("shows Soll and Ist type, treatment, reason and conflicts, escaped", () => {
    const html = junctionHtml(j, META, "https://example.org/");
    expect(html).toContain("durchgehender Gehweg");
    expect(html).toContain("nichts erfasst");
    expect(html).toContain("Mittelinsel für die Querung.");
    expect(html).toContain("Regel J-04");
    expect(html).toContain("Kfz-Menge fehlt an einem Arm");
    expect(html).toContain("&lt;Nebenweg&gt;");
    expect(html).not.toContain("<Nebenweg>");
    expect(html).toContain("Radnetz-Entwurf – nicht amtlich");
    expect(html).toContain('id="panel-title"');
  });

  it("names corrections and the need for reconstruction", () => {
    const html = junctionHtml({ ...j, action_needed: true, priority_rank: 7, result: { code: "mismatch", text: "Umbau nötig" },
      soll: { ...j.soll, code: "signal_protected", text: "Ampel" }, override: { reason: "Straßenbahn", author: "Team", date: "2026-11-07" } }, META, "u");
    expect(html).toContain("Umbau nötig");
    expect(html).toContain("Rang 7");
    expect(html).toContain("Fachlich korrigiert");
    expect(html).toContain("Straßenbahn");
  });
});

describe("Radnetz method page", () => {
  it("explains the five principles, the draft status and the limits", async () => {
    const { radnetzHtml } = await import("../src/pages.js");
    const html = radnetzHtml({ ...META, cycling: { ...META.cycling, stats: { km_by_category: { HAUPT: 2027.1 }, n_junctions: 16285, n_junctions_action: 3076 } } });
    for (const p of Object.values(META.cycling.principles)) expect(html).toContain(p);
    expect(html).toContain("Radnetz-Entwurf – nicht amtlich");
    expect(html).toContain("Grenzen");
    expect(html).toContain("2.027 km");
    expect(html).toContain("16.285 Knotenpunkte");
  });

  it("works without cycling data", async () => {
    const { radnetzHtml } = await import("../src/pages.js");
    expect(radnetzHtml({ cycling: null })).toContain("noch nicht enthalten");
  });
});
