import { describe, expect, it, vi } from "vitest";
import { bindDistrictPage, districtHtml, districtListHtml, fill, treesParkingHtml } from "../src/districts.js";

const fig = (n) => ({ km_total: 100 * n, km_need: 12.5 * n, km_speed_down: 3, km_cycle_main: 20, km_cycle_missing: 4.2 * n,
  km_profile_no_fit: 7, junctions: 50, junctions_rebuild: 3 * n });
const names = ["Hamburg-Mitte", "Altona", "Eimsbüttel", "Hamburg-Nord", "Wandsbek", "Bergedorf", "Harburg"];
const meta = {
  categories: { GOW50: { speed_kmh: 50 }, GOW30: { speed_kmh: 30 }, ETW30: { speed_kmh: 30 }, ETW_ERF: { speed_kmh: 7 } },
  cycling: { junction_ist: { signal: "Ampel" }, junction_type: { roundabout: "Kreisverkehr" }, cycle_categories: { main: "Hauptroute" } },
  overview: {
    figures: Object.fromEntries(names.map((n, i) => [n, fig(i + 1)])),
    files: {},
    params: { need_min_disc: 1, top_n: 5 },
    texts: {
      intro: "Auf {km_need} von {km_total} km Straße passt nicht. {junctions_rebuild} Kreuzungen müssten umgebaut werden.",
      figures: { km_need: "Straßen mit Abweichung", junctions_rebuild: "Kreuzungen", km_cycle_missing: "Radnetz ohne Radweg" },
      street_speed: "heute {speed_ist} km/h, Ziel {target} km/h",
      street_crashes: "{crashes} Unfälle mit Fuß- oder Radbeteiligung in 5 Jahren",
      junction: "heute {ist}, Ziel {soll}",
      junction_crashes: "{crashes} Unfälle mit Radbeteiligung in 5 Jahren",
      gap: "{km} km {cycle_cat} ohne passenden Radweg, bis {demand} Radfahrten am Tag (Modell)",
      lists_note: "Hinweis zu den Listen.",
    },
  },
};
const d = {
  name: "Altona", figures: fig(2),
  top: {
    streets: [
      { name: "Elbchaussee", id: "s1", priority: 9, cat: "GOW30", speed_ist: 50, crashes: 4, km_need: 1, at: [9.9, 53.54] },
      { name: "Ruhige Straße", id: "s2", priority: 5, cat: "GOW30", speed_ist: 30, crashes: 0, km_need: 1, at: [9.8, 53.5] },
    ],
    junctions: [{ name: "Kreuzung A", id: "j1", rank: 1, ist: "signal", soll: "roundabout", crashes: 2, at: [9.95, 53.55] }],
    gaps: [{ name: "Lücke B", id: "g1", km: 1.5, cycle_cat: "main", demand: 800, at: [9.7, 53.6] }],
  },
};

describe("districts", () => {
  it("fill formats numbers German", () => {
    expect(fill("{a} von {b}", { a: 1234.5, b: 7 })).toBe("1.234,5 von 7");
  });
  it("page shows intro, figures and no codes", () => {
    const h = districtHtml(meta, d);
    expect(h).toContain("<h1>Altona</h1>");
    expect(h).toContain("Auf 25 von 200 km");
    expect(h).toContain("Straßen mit Abweichung");
    for (const code of ["GOW30", "signal", "roundabout", "ETW", "main<"]) expect(h).not.toContain(code);
  });
  it("lists come from the fixture with labels", () => {
    const h = districtHtml(meta, d);
    expect(h).toContain("Elbchaussee");
    expect(h).toContain("heute Ampel, Ziel Kreisverkehr");
    expect(h).toContain("1,5 km Hauptroute ohne passenden Radweg");
    expect(h).toContain('<details class="level l2" open>');
    expect(h).toContain('<details class="level l3">');
  });
  it("buttons carry data attributes", () => {
    const h = districtHtml(meta, d);
    expect(h).toContain('data-open-seg="s1" data-lon="9.9" data-lat="53.54"');
    expect(h).toContain('data-open-jct="j1"');
    expect(h).toContain("data-show-table");
  });
  it("speed part only when too fast", () => {
    const h = districtHtml(meta, d);
    expect(h).toContain("heute 50 km/h, Ziel 30 km/h; 4 Unfälle");
    expect(h).not.toContain("heute 30 km/h");
  });
  it("comparison table marks current district", () => {
    const h = districtHtml(meta, d);
    expect(h).toMatch(/<tr class="current">\s*<th scope="row">Altona/);
    expect(h.match(/<tr class="current"/g)).toHaveLength(1);
  });
  it("chooser has one button per district", () => {
    const h = districtListHtml(meta);
    expect(h.match(/data-bz="/g)).toHaveLength(7);
  });
  it("click handler calls callbacks", () => {
    const cb = { onPickDistrict: vi.fn(), onOpenSegment: vi.fn(), onOpenJunction: vi.fn(), onShowTable: vi.fn() };
    const root = {};
    bindDistrictPage(root, cb);
    const click = (sel, dataset) => root.onclick({ target: { closest: (s) => (s === sel ? { dataset } : null) } });
    click("[data-bz]", { bz: "Altona" });
    click("[data-open-seg]", { openSeg: "s1", lon: "9.9", lat: "53.5" });
    click("[data-open-jct]", { openJct: "j1" });
    click("[data-show-table]", {});
    expect(cb.onPickDistrict).toHaveBeenCalledWith("Altona");
    expect(cb.onOpenSegment).toHaveBeenCalledWith("s1", [9.9, 53.5]);
    expect(cb.onOpenJunction).toHaveBeenCalledWith("j1", null);
    expect(cb.onShowTable).toHaveBeenCalledOnce();
  });
});

// prompt 26 Teil 2: trees and parking cards

describe("trees and parking cards", () => {
  const texts = {
    parking_title: "Parkplätze am Straßenrand", parking_card: "heute ≈ {today}, im Ziel ≈ {target}",
    parking_less: "{n} weniger als heute", parking_more: "{n} mehr als heute",
    parking_l2: "Daten auf {share_known} %.", parking_l3: "amtlich {share_official} %, gezählt {counted}.",
    trees_title: "Straßenbäume", trees_card: "{keep} bleiben, {affected} möglicherweise betroffen, {new} neu möglich",
    trees_l2: "Erklärung.", trees_l3: "Spanne {affected_lo} bis {affected_hi} von {n}.",
  };
  const summary = { share_complete: 0.39, share_official: 0.245, share_osm: 0.148, share_none: 0.607, park_today_complete: 252479,
    park_target_lo: 134368, park_target_hi: 138310, park_change_lo: -118105, park_change_hi: -114164,
    park_counted: 258430, trees_n: 190567, trees_affected_lo: 3557, trees_affected_mid: 21286,
    trees_affected_hi: 159600, trees_new: 61945 };
  const meta = { trees_parking: { texts, summary: { Hamburg: summary } } };

  it("words rounded estimates and ranges", () => {
    const html = treesParkingHtml(meta, "Hamburg");
    expect(html).toContain("heute ≈ 252.000, im Ziel ≈ 134.000–138.000");
    expect(html).toContain("114.000–118.000 weniger als heute");
    expect(html).toContain("169.000 bleiben, 21.000 möglicherweise betroffen, 62.000 neu möglich");
    expect(html).toContain("Spanne 3.600 bis 160.000 von 191.000.");
  });

  it("shows nothing without data", () => {
    expect(treesParkingHtml({}, "Hamburg")).toBe("");
    expect(treesParkingHtml(meta, "Altona")).toBe("");
  });
});
