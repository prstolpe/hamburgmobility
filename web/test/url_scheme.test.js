// URL scheme version 2 (prompt 28, docs/url_scheme.md): old links resolve to the same view, round trip without loss,
// unknown parameters are ignored, canonical order.
import { describe, expect, it } from "vitest";
import { DEFAULTS, normalizeCamera, OVERLAYS, parseHash, THEMES, toHash, viewsOf } from "../src/state.js";

// What a shared link opens: everything that decides the view (page, theme/view, layers, selection, filters, camera).
const view = (s) => ({
  page: s.page, sub: s.sub, theme: s.theme, view: s.view, layer: s.layer, overlays: s.overlays, seg: s.seg, jct: s.jct,
  place: s.place, bz: s.bz, cats: s.cats, dts: s.dts, prmin: s.prmin, table: s.table, rule: s.rule, map: s.map,
});
const cam = (zoom, lat, lon, pitch = 0, bearing = 0) => ({ zoom, lat, lon, pitch, bearing });

// At least 20 old link patterns (version 1 and older) with the view they must open.
const OLD_LINKS = [
  ["#karte", { theme: "aufgabe", view: "ziel" }],
  ["#karte?map=14/53.57/9.95", { map: cam(14, 53.57, 9.95) }],
  ["#karte?map=12.50/53.55123/10.00456&seg=seg_0a1b", { seg: "seg_0a1b", map: cam(12.5, 53.55123, 10.00456) }],
  ["#karte?ov=bus", { overlays: ["bus"] }],
  ["#karte?ov=acc,bus", { overlays: ["bus", "acc"] }],
  ["#karte?ov=fac,acc,bus,xyz", { overlays: ["bus", "fac", "acc"] }],
  ["#karte?ov=cyc", { theme: "rad", view: "amtlich", overlays: [] }],
  ["#karte?ov=cyc,bus", { theme: "rad", view: "amtlich", overlays: ["bus"] }],
  ["#karte?layer=cgap&map=14/53.57/9.95", { theme: "rad", view: "ziel", map: cam(14, 53.57, 9.95) }],
  ["#karte?layer=speed&bz=Altona", { theme: "aufgabe", view: "heute", bz: "Altona" }],
  ["#karte?layer=prio&pr=1.5&dt=D1,D3", { theme: "abweichung", view: "prio", prmin: 1.5, dts: ["D1", "D3"] }],
  ["#karte?layer=disc&cat=GOW30,ETW30", { theme: "abweichung", view: "ziel", cats: ["GOW30", "ETW30"] }],
  ["#karte?layer=jct&jct=1026524904", { theme: "knoten", view: "ziel", jct: "1026524904" }],
  ["#karte?theme=knoten&jct=123&map=16/53.56/9.96", { theme: "knoten", jct: "123", map: cam(16, 53.56, 9.96) }],
  ["#karte?jct=55&seg=seg_ff", { jct: "55", seg: null }],
  ["#karte?place=schanze_verkehrsberuhigt", { place: "schanze_verkehrsberuhigt", map: null }],
  ["#karte?place=schanze_verkehrsberuhigt&ov=bus&seg=seg_00ab", { place: "schanze_verkehrsberuhigt", overlays: ["bus"], seg: "seg_00ab" }],
  ["#karte?theme=platz&view=ziel", { theme: "platz", view: "fahrstreifen" }],
  ["#karte?theme=rad&view=luecken&bz=Wandsbek", { theme: "rad", view: "ziel", bz: "Wandsbek" }],
  ["#karte?seg=seg_00ab&ov=acc&pr=1.5", { seg: "seg_00ab", overlays: ["acc"], prmin: 1.5 }],
  ["#tabelle?bz=Altona", { page: "bezirke", bz: "Altona", table: true }],
  ["#downloads", { page: "daten" }],
  ["#radnetz", { page: "methode", sub: "radnetz" }],
  ["#methode/neu", { page: "methode", sub: null }],
  ["#methode/regeln?regel=C-G30-02", { page: "methode", sub: "regeln", rule: "C-G30-02" }],
];

describe("old links open the same view", () => {
  it("has at least 20 patterns", () => expect(OLD_LINKS.length).toBeGreaterThanOrEqual(20));
  for (const [hash, want] of OLD_LINKS) {
    it(hash, () => {
      const s = parseHash(hash);
      expect(s).toMatchObject(want);
      // the rewritten (version 2) link opens exactly the same view
      expect(view(parseHash(toHash(s)))).toEqual(view(s));
      for (const old of ["ov=", "jct=", "map=", "layer="]) expect(toHash(s)).not.toContain(old);
    });
  }
});

describe("version 2", () => {
  it("writes v=2 first on the map page, nothing for the default state", () => {
    expect(toHash({ ...DEFAULTS })).toBe("#karte");
    expect(toHash({ ...DEFAULTS, overlays: ["bus"] })).toBe("#karte?v=2&layers=bus");
    expect(toHash({ ...DEFAULTS, page: "bezirke", bz: "Altona" })).toBe("#bezirke?bz=Altona");
  });

  it("writes the camera as z, lat, lon and pitch/bearing only when set", () => {
    expect(toHash({ ...DEFAULTS, map: cam(14, 53.57, 9.95) })).toBe("#karte?v=2&z=14.00&lat=53.57000&lon=9.95000");
    expect(toHash({ ...DEFAULTS, map: cam(15.256, 53.5, 10, 45, -30) })).toBe("#karte?v=2&z=15.26&lat=53.50000&lon=10.00000&pitch=45&bearing=-30");
  });

  it("parses pitch and bearing and keeps them in range", () => {
    expect(parseHash("#karte?v=2&z=14&lat=53.5&lon=10&pitch=90&bearing=200").map).toEqual(cam(14, 53.5, 10, 60, -160));
    expect(parseHash("#karte?v=2&z=14&lat=53.5").map).toBeNull(); // z, lat, lon only together
  });

  it("canonical order: the same state gives the same string", () => {
    const a = parseHash("#karte?bz=Altona&layers=acc,bus&theme=rad&v=2&seg=seg_0a");
    const b = parseHash("#karte?v=2&seg=seg_0a&theme=rad&layers=bus,acc&bz=Altona");
    expect(toHash(a)).toBe(toHash(b));
    expect(toHash(a)).toBe("#karte?v=2&theme=rad&layers=bus,acc&seg=seg_0a&bz=Altona");
  });

  it("ignores unknown parameters and does not write them back", () => {
    const s = parseHash("#karte?v=2&foo=1&utm_source=x&layers=bus,unbekannt&theme=nichts&view=x");
    expect(view(s)).toEqual(view({ ...DEFAULTS, overlays: ["bus"] }));
    expect(toHash(s)).toBe("#karte?v=2&layers=bus");
  });

  it("a future view (e.g. 'moeglich') falls back without a scheme change", () => {
    expect(parseHash("#karte?v=2&theme=aufgabe&view=moeglich").view).toBe("ziel");
  });
});

describe("round trip without loss", () => {
  // small deterministic generator (no Math.random: the test must be reproducible)
  let seed = 28;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  const pick = (xs) => xs[Math.floor(rnd() * xs.length)];
  const sub = (xs) => xs.filter(() => rnd() < 0.4);

  it("parseHash(toHash(s)) equals s for 300 random valid states", () => {
    for (let i = 0; i < 300; i++) {
      const theme = pick(Object.keys(THEMES));
      const [view, v] = pick(viewsOf(theme));
      const node = rnd() < 0.3 ? String(Math.floor(rnd() * 1e9)) : null;
      const s = {
        ...DEFAULTS, theme, view, layer: v.layer, overlays: OVERLAYS.filter((o) => o !== "cyc" && rnd() < 0.4),
        jct: node, seg: node ? null : rnd() < 0.5 ? `seg_${Math.floor(rnd() * 1e12).toString(16)}` : null,
        place: rnd() < 0.2 ? "schanze_verkehrsberuhigt" : null, bz: rnd() < 0.3 ? pick(["Altona", "Eimsbüttel", "Hamburg-Nord"]) : "",
        cats: sub(["SW", "GOW50", "GOW30", "ETW30", "ETW_ERF"]), dts: sub(["D1", "D2", "D3", "keine"]), prmin: pick([0, 0.25, 1.5, 3]),
        map: rnd() < 0.7 ? normalizeCamera({ zoom: 10 + rnd() * 8, lat: 53.4 + rnd() * 0.4, lon: 9.7 + rnd() * 0.6,
          pitch: rnd() < 0.5 ? rnd() * 60 : 0, bearing: rnd() < 0.5 ? rnd() * 360 - 180 : 0 }) : null,
      };
      expect(parseHash(toHash(s)), toHash(s)).toEqual(s);
    }
  });
});
