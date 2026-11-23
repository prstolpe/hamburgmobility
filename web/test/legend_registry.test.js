// Legend registry and map panel (prompt 28): one registry drives the legend; only switched-on layers appear; every
// entry is drawn on the map; every view links to its method; a new layer plugs in without code changes elsewhere.
import { describe, expect, it } from "vitest";
import { sfpLayers } from "../src/layers.js";
import { legendFor, MAX_OVERLAYS, OVERLAY_LAYERS, overlayGroups } from "../src/legend_registry.js";
import { chipsHtml, featureSentence, panelHtml } from "../src/map_panel.js";
import { BUS, CRASH, OVERLAY_COLORS } from "../src/palette.js";
import { DEFAULTS, THEMES, viewsOf, withView } from "../src/state.js";

const META = {
  categories: { SW: { label: "Schnellstraße" }, GOW50: { label: "Hauptstraße mit Tempo 50" }, GOW30: { label: "Hauptstraße mit Tempo 30" },
    ETW30: { label: "Wohnstraße mit Tempo 30" }, ETW_ERF: { label: "Fußgängerzone oder Spielstraße" } },
  categories_present: ["SW", "GOW50", "GOW30", "ETW30", "ETW_ERF"],
  discrepancy_types: { D1: "a", D2: "b", D3: "c" }, width_classes_m: { ETW30: 10, GOW50: 20 }, feasibility: { fits: "passt", tight: "knapp", does_not_fit: "passt nicht" },
  districts: ["Altona", "Eimsbüttel"], rural_excluded: ["Kirchwerder"],
  glossary: { categories: { GOW30: { explain: "Verbindet Stadtteile, Tempo 30." } }, cycling: { RSV: { explain: "Wichtigste Route." } }, terms: {} },
  cycling: {
    disclaimer: "Radnetz-Entwurf – nicht amtlich", official_attribution: "Radnetz Hamburg © FHH/BVM",
    cycle_categories: { RSV: "Radvorrangroute", HAUPT: "Radroute", BASIS: "Bezirksroute", ERSCHL: "Quartiersnetz" },
    facility: { separated_oneway_both: "a", separated_twoway: "b", cycle_lane: "c", cycle_street: "d", mixed: "e", own_path: "f" },
    gap: { none: "a", missing: "b", wrong_type: "c", partial: "d", too_narrow: "e", not_assessed: "f" },
    fit: { fits: "a", fits_after_degrade: "b", does_not_fit: "c" }, lanes: { shared: "a", fewer: "b", same: "c", more: "d", ist_unknown: "e" },
    junction_group: { roundabout: "Kreisverkehr", signal: "Ampel", priority: "Vorfahrt", continuous: "Gehweg", equal: "rechts vor links", grade_separated: "Brücke", none: "kein" },
    official_status: { Bestand: "Bestand", "In Arbeit": "in Arbeit", planned: "geplant" },
    tiles: { cycling: "tiles/cycling.pmtiles", junctions: "tiles/junctions.pmtiles" },
  },
  special_places: { file: "special_places.geojson", texts: { overlay: "Besondere Orte", legend: "Vorschlag" },
    places: [{ id: "schanze_verkehrsberuhigt", title: "Verkehrsberuhigte Schanze", kind_plain: "Vorschlag", status_date: "2026-09-25",
      theme: { palette: { main: "#235753", casing: "#ffffff" }, pattern: { pedestrian_zone: "dashed" } },
      measures: [{ measure: "cycle_street", label: "Fahrradstraße" }, { measure: "pedestrian_zone", label: "Fußgängerzone" }] }] },
};
const st = (patch = {}) => ({ ...withView({ ...DEFAULTS }, patch.theme ?? "aufgabe", patch.view ?? "ziel"), ...patch });
const UI = { inView: null, highlight: null, openWhat: new Set(), filtersOpen: false, listOpen: false, listHtml: "", preview: null };
const allViews = Object.keys(THEMES).flatMap((t) => viewsOf(t).map(([v]) => [t, v]));

describe("legend registry", () => {
  it("every enabled view has entries with label, symbol and a method link", () => {
    for (const [theme, view] of allViews) {
      const l = legendFor(st({ theme, view }), META)[0];
      expect(l.entries.length, `${theme}/${view}`).toBeGreaterThan(0);
      expect(l.method, `${theme}/${view}`).toMatch(/^#methode\//);
      for (const e of l.entries) { expect(e.label, e.key).toBeTruthy(); expect(e.symbol?.type, e.key).toBeTruthy(); }
    }
  });

  it("every entry points to a layer that is drawn for that state", () => {
    for (const [theme, view] of allViews) {
      const s = st({ theme, view, overlays: ["bus", "fac", "acc"], place: "schanze_verkehrsberuhigt" });
      const drawn = new Set(sfpLayers(s, META).map((l) => l.id));
      for (const l of legendFor(s, META)) for (const e of l.entries) {
        if (!e.layer || e.layer === "rural-fill" || e.layer === "gaps-fill") continue; // base layers of map.js / mesh gaps only with data
        expect(drawn.has(e.layer), `${theme}/${view}: ${e.layer}`).toBe(true);
      }
    }
  });

  it("layers that are off do not appear", () => {
    const ids = legendFor(st(), META).map((l) => l.id);
    expect(ids).toEqual(["view:cat", "base"]);
    const on = legendFor(st({ overlays: ["bus"], place: "schanze_verkehrsberuhigt" }), META).map((l) => l.id);
    expect(on).toEqual(["view:cat", "layer:bus", "place:schanze_verkehrsberuhigt", "base"]);
  });

  it("bus, crashes and schools have legend entries (they had none before prompt 28)", () => {
    for (const k of ["bus", "acc", "fac"]) expect(OVERLAY_LAYERS[k].entries.length, k).toBeGreaterThan(0);
  });

  it("bus and crashes have their own colours; schools are a ring, not the junction dot", () => {
    expect(OVERLAY_COLORS.bus).toBe(BUS);
    expect(OVERLAY_COLORS.acc).toBe(CRASH);
    expect(OVERLAY_LAYERS.fac.entries[0].symbol.type).toBe("ring");
    const fac = sfpLayers(st({ overlays: ["fac"] }), META).find((l) => l.id === "ov-fac");
    expect(fac.paint["circle-color"]).toBe("#ffffff");
  });

  it("no two entries shown together share the same symbol", () => {
    for (const [theme, view] of allViews) {
      const s = st({ theme, view, overlays: ["bus", "fac", "acc"], place: "schanze_verkehrsberuhigt" });
      const seen = new Map();
      for (const l of legendFor(s, META)) for (const e of l.entries) {
        const k = JSON.stringify(e.symbol);
        expect(seen.has(k) && seen.get(k) !== e.label, `${theme}/${view}: ${e.label} = ${seen.get(k)}`).toBe(false);
        seen.set(k, e.label);
      }
    }
  });

  it("explanations come from the export glossary where it has one", () => {
    const e = legendFor(st(), META)[0].entries.find((x) => x.key === "GOW30");
    expect(e.explain).toBe("Verbindet Stadtteile, Tempo 30.");
    const rsv = legendFor(st({ theme: "rad" }), META)[0].entries.find((x) => x.key === "cc-RSV");
    expect(rsv.explain).toBe("Wichtigste Route.");
  });

  it("keeps the notes of the old legend: draft note, rebuild note, official attribution, width scale", () => {
    expect(legendFor(st({ theme: "rad" }), META)[0].notes.map((n) => n.text)).toContain("Radnetz-Entwurf – nicht amtlich");
    expect(legendFor(st({ theme: "knoten" }), META)[0].notes.map((n) => n.text).join()).toContain("Umbau nötig");
    expect(legendFor(st({ theme: "rad", view: "amtlich" }), META)[0].notes.map((n) => n.text)).toContain("Radnetz Hamburg © FHH/BVM");
    expect(legendFor(st({ theme: "abweichung" }), META)[0].entries.map((e) => e.key)).toContain("disc-scale");
  });

  it("a new layer plugs in through the registry alone", () => {
    OVERLAY_LAYERS.test_layer = { group: "Test", title: "Testebene", text: "t", method: "#methode", entries: [
      { key: "t1", layer: "ov-test", label: "Testeintrag", symbol: { type: "line", color: "#000000", width: 3 } }] };
    try {
      expect(overlayGroups().find((g) => g.group === "Test").items[0].title).toBe("Testebene");
      expect(legendFor(st({ overlays: ["test_layer"] }), META).map((l) => l.id)).toContain("layer:test_layer");
      expect(panelHtml(st({ overlays: ["test_layer"] }), META, UI)).toContain("Testeintrag");
    } finally { delete OVERLAY_LAYERS.test_layer; }
  });

  it("the old overlay cyc stays explained but gets no switch", () => {
    expect(overlayGroups().flatMap((g) => g.items.map((i) => i.key))).not.toContain("cyc");
    expect(legendFor(st({ overlays: ["cyc"] }), META).map((l) => l.id)).toContain("layer:cyc");
  });
});

describe("map panel", () => {
  it("shows the view legend, the layer switches and the filters", () => {
    const html = panelHtml(st(), META, UI);
    expect(html).toContain("Was die Farben bedeuten");
    expect(html).toContain('name="ov" value="bus"');
    expect(html).toContain("Filter");
    expect(html).toContain('role="radiogroup"');
  });

  it("a switched-on layer unfolds its legend right below its switch", () => {
    const html = panelHtml(st({ overlays: ["bus"] }), META, UI);
    const row = html.slice(html.indexOf('value="bus"'), html.indexOf('value="acc"'));
    expect(row).toContain("viele Busse");
  });

  it(`locks further switches at ${MAX_OVERLAYS} layers`, () => {
    const html = panelHtml(st({ overlays: ["bus", "acc", "fac"] }), META, UI);
    expect(html).toContain(`Höchstens ${MAX_OVERLAYS} Ebenen`);
  });

  it("dims entries that are not in view and says so in text", () => {
    const html = panelHtml(st(), META, { ...UI, inView: new Set(["main-GOW50"]) });
    expect(html).toContain("nicht im Ausschnitt");
    expect((html.match(/nicht im Ausschnitt/g) ?? []).length).toBeGreaterThan(2);
  });

  it("highlight and explanation state are reflected with aria attributes", () => {
    const html = panelHtml(st(), META, { ...UI, highlight: "GOW30", openWhat: new Set(["GOW30"]) });
    expect(html).toMatch(/data-key="GOW30" aria-pressed="true"/);
    expect(html).toMatch(/data-what="GOW30" aria-expanded="true"/);
  });

  it("chips: the view as a label, every layer, place, district and filter removable", () => {
    const html = chipsHtml(st({ overlays: ["bus"], place: "schanze_verkehrsberuhigt", bz: "Altona", cats: ["GOW30"] }), META);
    for (const id of ["layer:bus", "place:schanze_verkehrsberuhigt", "bz", "filter"]) expect(html).toContain(`data-remove="${id}"`);
    expect(html).toContain("Aufgabe und Tempo");
  });

  it("one-sentence preview of a segment and a junction", () => {
    const seg = featureSentence({ sourceLayer: "segments", source: "sfp", properties: { id: "seg_1", name: "Osterstraße", cat: "GOW30", spd: 50 } }, META, new Map());
    expect(seg).toEqual({ kind: "seg", id: "seg_1", title: "Osterstraße", text: "Ziel: Hauptstraße mit Tempo 30, heute Tempo 50." });
    const jct = featureSentence({ sourceLayer: "junctions", source: "jct", properties: { id: 7, grp: "signal", act: 1 } }, META, new Map([["7", "Schlump"]]));
    expect(jct).toEqual({ kind: "jct", id: "7", title: "Kreuzung Schlump", text: "Ziel: Ampel. Umbau nötig." });
  });

  it("filter words for Abweichung are the legend words (one source per term)", () => {
    const html = panelHtml(st(), META, { ...UI, filtersOpen: true });
    expect(html).toContain("passt bereits");
    expect(html).not.toContain("keine Abweichung");
  });
});
