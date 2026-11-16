// URL state with themes and views (redesign 2026-11, package 2; docs/redesign/02_information_architecture.md,
// table "Alte Links bleiben gültig"): one test per row of the redirect table.
import { describe, expect, it } from "vitest";
import { DEFAULTS, layerOf, parseHash, THEMES, toHash, viewsOf } from "../src/state.js";

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
    const s = { ...DEFAULTS, page: "karte", theme: "abweichung", view: "prio", layer: "prio", overlays: ["acc"], cats: ["GOW30"],
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

// prompt 25: views switched off by configuration (enabled: false), not deleted
describe("disabled views", () => {
  const disabled = [["rad", "luecken"], ["rad", "radweg"], ["platz", "ziel"], ["platz", "breite"], ["platz", "regelprofil"]];

  it("every theme keeps at least one enabled view", () => {
    for (const t of Object.keys(THEMES)) expect(viewsOf(t).length, t).toBeGreaterThan(0);
  });

  it("are kept in THEMES but not offered", () => {
    for (const [t, v] of disabled) {
      expect(THEMES[t].views[v].enabled, `${t}/${v}`).toBe(false);
      expect(viewsOf(t).map(([k]) => k)).not.toContain(v);
    }
    expect(viewsOf("platz").map(([k]) => k)).toEqual(["fahrstreifen"]);
    expect(viewsOf("rad").map(([k]) => k)).toEqual(["ziel", "amtlich"]);
  });

  it("shared links fall back to the theme's default view", () => {
    for (const [t, v] of disabled) {
      const s = parseHash(`#karte?theme=${t}&view=${v}`);
      expect([s.theme, s.view], `${t}/${v}`).toEqual([t, viewsOf(t)[0][0]]);
    }
    expect(toHash(parseHash("#karte?theme=platz&view=ziel"))).toBe("#karte?theme=platz");
    expect(parseHash("#karte?theme=platz").layer).toBe("lanes");
  });
});

describe("old links are rewritten", () => {
  const rows = [
    ["#karte?layer=cat", "aufgabe", "ziel"],
    ["#karte?layer=speed", "aufgabe", "heute"],
    ["#karte?layer=hvs", "aufgabe", "hvs"],
    ["#karte?layer=disc", "abweichung", "ziel"],
    ["#karte?layer=width", "platz", "fahrstreifen"], // view disabled (prompt 25)
    ["#karte?layer=feas", "platz", "fahrstreifen"], // view disabled
    ["#karte?layer=cfit", "platz", "fahrstreifen"], // view disabled
    ["#karte?layer=lanes", "platz", "fahrstreifen"],
    ["#karte?layer=cnet", "rad", "ziel"],
    ["#karte?layer=cfac", "rad", "ziel"], // view disabled
    ["#karte?layer=cgap", "rad", "ziel"], // view disabled
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
    expect(parseHash("#radnetz")).toMatchObject({ page: "methode", sub: "radnetz" });
    expect(toHash(parseHash("#radnetz"))).toBe("#methode/radnetz");
  });
});

describe("method sub pages", () => {
  it("parses chapters and the reference; unknown sub (also the removed news page) falls back to the summary", () => {
    expect(parseHash("#methode")).toMatchObject({ page: "methode", sub: null, rule: null });
    expect(parseHash("#methode/platz").sub).toBe("platz");
    expect(parseHash("#methode/regeln").sub).toBe("regeln");
    expect(parseHash("#methode/neu").sub).toBeNull(); // news page removed (prompt 25)
    expect(parseHash("#methode/gibtesnicht").sub).toBeNull();
  });

  it("parses the regel parameter and rejects odd values", () => {
    expect(parseHash("#methode/regeln?regel=C-G30-02")).toMatchObject({ sub: "regeln", rule: "C-G30-02" });
    expect(parseHash("#methode/regeln?regel=a%22b").rule).toBeNull();
  });

  it("round-trips sub and rule", () => {
    for (const h of ["#methode", "#methode/knoten", "#methode/regeln", "#methode/regeln?regel=C-G30-02"]) {
      expect(toHash(parseHash(h))).toBe(h);
    }
  });

  it("does not put sub or rule into other pages", () => {
    expect(parseHash("#daten/aufgabe").sub).toBeNull();
    expect(toHash({ ...DEFAULTS, page: "daten", sub: "aufgabe", rule: "X-1" })).toBe("#daten");
  });
});

// prompt 26: special places
describe("special place parameter", () => {
  it("round-trips ?place= and keeps other parameters", () => {
    const s = parseHash("#karte?place=schanze_verkehrsberuhigt&seg=seg_00ab");
    expect([s.place, s.seg]).toEqual(["schanze_verkehrsberuhigt", "seg_00ab"]);
    expect(toHash(s)).toBe("#karte?seg=seg_00ab&place=schanze_verkehrsberuhigt");
  });

  it("ignores invalid place ids and has no place by default", () => {
    expect(parseHash("#karte?place=<x>").place).toBeNull();
    expect(parseHash("#karte").place).toBeNull();
  });

  it("knows the page Besondere Orte", () => {
    expect(parseHash("#orte").page).toBe("orte");
  });
});
