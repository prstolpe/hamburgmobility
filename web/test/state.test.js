// URL state with themes and views (redesign 2026-11, package 2; docs/redesign/02_information_architecture.md,
// table "Alte Links bleiben gültig"): one test per row of the redirect table.
import { describe, expect, it } from "vitest";
import { DEFAULTS, layerOf, parseHash, THEMES, toHash } from "../src/state.js";

describe("themes and views", () => {
  it("every theme view maps to a map layer", () => {
    for (const [t, th] of Object.entries(THEMES)) for (const v of Object.keys(th.views)) expect(layerOf(t, v), `${t}/${v}`).toBeTruthy();
  });

  it("defaults: map page, theme Aufgabe und Tempo, view Ziel", () => {
    const s = parseHash("");
    expect([s.page, s.theme, s.view, s.layer]).toEqual(["karte", "aufgabe", "ziel", "cat"]);
    expect(toHash({ ...DEFAULTS })).toBe("#karte");
  });

  it("round-trips theme, view and the other fields", () => {
    const s = { ...DEFAULTS, page: "karte", theme: "rad", view: "luecken", layer: "cgap", overlays: ["acc"], cats: ["GOW30"],
      dts: ["D1"], prmin: 1, bz: "Altona", seg: "seg_00ab", jct: null, table: false, map: { zoom: 14, lat: 53.57, lon: 9.95 } };
    expect(parseHash(toHash(s))).toEqual(s);
  });

  it("leaves the default view of a theme out of the URL", () => {
    expect(toHash({ ...DEFAULTS, theme: "knoten", view: "ziel", layer: "jct" })).toBe("#karte?theme=knoten");
  });

  it("ignores unknown themes and views", () => {
    const s = parseHash("#karte?theme=foo&view=bar");
    expect([s.theme, s.view]).toEqual(["aufgabe", "ziel"]);
    expect(parseHash("#karte?theme=rad&view=bar").view).toBe("ziel");
  });
});

describe("old links are rewritten", () => {
  const rows = [
    ["#karte?layer=cat", "aufgabe", "ziel"],
    ["#karte?layer=speed", "aufgabe", "heute"],
    ["#karte?layer=hvs", "aufgabe", "hvs"],
    ["#karte?layer=disc", "abweichung", "ziel"],
    ["#karte?layer=width", "platz", "breite"],
    ["#karte?layer=feas", "platz", "regelprofil"],
    ["#karte?layer=cfit", "platz", "ziel"],
    ["#karte?layer=lanes", "platz", "fahrstreifen"],
    ["#karte?layer=cnet", "rad", "ziel"],
    ["#karte?layer=cfac", "rad", "radweg"],
    ["#karte?layer=cgap", "rad", "luecken"],
    ["#karte?layer=coff", "rad", "amtlich"],
    ["#karte?layer=jct", "knoten", "ziel"],
  ];
  for (const [hash, theme, view] of rows) {
    it(`${hash} → theme=${theme}&view=${view}`, () => {
      const s = parseHash(hash);
      expect([s.theme, s.view]).toEqual([theme, view]);
      expect(toHash(s)).not.toContain("layer=");
    });
  }

  it("ov=cyc without a theme opens the official cycle network", () => {
    const s = parseHash("#karte?ov=cyc");
    expect([s.theme, s.view, s.overlays]).toEqual(["rad", "amtlich", []]);
    expect(parseHash("#karte?theme=aufgabe&ov=cyc").overlays).toEqual(["cyc"]);
  });

  it("keeps cat, dt, pr, bz, seg, jct and map", () => {
    const s = parseHash("#karte?layer=disc&cat=GOW30&dt=D1&pr=2&bz=Altona&seg=seg_0a&map=14/53.5/9.9");
    expect([s.cats, s.dts, s.prmin, s.bz, s.seg]).toEqual([["GOW30"], ["D1"], 2, "Altona", "seg_0a"]);
    expect(s.map).toEqual({ zoom: 14, lat: 53.5, lon: 9.9 });
    expect(parseHash("#karte?layer=jct&jct=123").jct).toBe("123");
  });

  it("#tabelle becomes the district page with the table open", () => {
    expect(parseHash("#tabelle")).toMatchObject({ page: "bezirke", table: false });
    expect(parseHash("#tabelle?bz=Eimsb%C3%BCttel")).toMatchObject({ page: "bezirke", bz: "Eimsbüttel", table: true });
    expect(toHash(parseHash("#tabelle?bz=Altona"))).toBe("#bezirke?bz=Altona&tabelle=1");
  });

  it("#downloads and #quellen become #daten", () => {
    expect(parseHash("#downloads").page).toBe("daten");
    expect(parseHash("#quellen").page).toBe("daten");
    expect(parseHash("#impressum").page).toBe("impressum");
    expect(parseHash("#radnetz").page).toBe("radnetz");
  });
});
