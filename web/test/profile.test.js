import { describe, expect, it } from "vitest";
import { certainty, junctionHtml, segmentHtml } from "../src/profile.js";

const meta = {
  categories: { GOW30: { label: "Stadtstraße 30" }, ETW30: { label: "Wohnstraße 30" }, ETW_ERF: { label: "Erlebnisstraße" }, SW: { label: "Schnellstraße" } },
  cycling: { elements: { carriageway: { label: "Fahrbahn", color: "#888" } } },
  feedback_email: "x@example.org",
  github_repo: null,
};
const seg = () => ({
  id: "seg_5a4361a0331e0791", name: "Max-Brauer-Allee", bezirk: "Altona", length_m: 320, version: "0.21.0+2026-10-28",
  category: { code: "GOW30", label: "Stadtstraße 30" }, rule_path: "C-GOW-01 → C-G30-01",
  ist: { speed_kmh: 50, cycling: "keine Radverkehrsanlage" },
  reasons: [
    { rule: "C-GOW-01", passed: true, text: "Hauptverkehrsstraße der BVM" },
    { rule: "C-G30-01", passed: true, text: "Schule oder Kita direkt an der Straße (C-G30-01)" },
    { rule: "C-G30-02", passed: false, text: "Platz für einen baulichen Radweg: Straßenraum 22,9 m" },
  ],
  confidence: { level: "hoch", summary: "Alle Werte stammen aus Primärquellen.", reasons: [] },
  sensitivity: { uncertain: false, text: "In 7 % der Läufe andere Kategorie.", triggers: ["Abstand zur Schule niedriger"] },
  discrepancy: { speed: 2, design: 1, use: 3, type: "D3", type_text: "Mischform", crashes: { ped_cyc: 9, years: "2021–2025" }, priority: 2.9 },
  crosssection: { feasibility_text: "passt" },
  cycling: {
    cycle_cat: { label: "Bezirksroute (Basisnetz)" },
    facility: { ist_text: "Radfahrstreifen", soll_text: "Radweg auf beiden Seiten", gap: "wrong_type" },
    width: { soll_m: 2.0, ist_m: null }, lanes: { ist: 2, soll: "1", change: "fewer", change_text: "weniger Fahrstreifen" },
    profile: { required_m: 21.3, available_m: 22.91, fit: "fits", fit_text: "passt in den Straßenraum", elements: [{ element: "carriageway", width_m: 6.5 }] },
    flags: ["Kfz-Verkehr senken"], principles: { ist: { score: 0.55 }, soll: { score: 0.65 } },
  },
  sources: [{ title: "OSM-Auszug", as_of: "2026-10-28", license: "ODbL-1.0", purpose: "Netz" }],
});
const split = (h) => {
  const i2 = h.indexOf('<details class="level l2"'), i3 = h.indexOf('<details class="level l3"');
  return { l1: h.slice(0, i2), l12: h.slice(0, i3), l2: h.slice(i2, i3), l3: h.slice(i3) };
};
const visible = (h) => h.replace(/<svg[\s\S]*?<\/svg>/g, "").replace(/<[^>]*>/g, " ");
const CODES = /\b(SW|GOW50|GOW30|ETW30|ETW_ERF)\b|[A-Z]{1,5}-[A-Z0-9]+-\d+|seg_[0-9a-f]+/;

describe("certainty", () => {
  it("maps sensitivity and confidence", () => {
    expect(certainty({ confidence: { level: "hoch" } })).toEqual({ lvl: "sicher", uncertain: false });
    expect(certainty({ confidence: { level: "mittel" } })).toEqual({ lvl: "eher sicher", uncertain: false });
    expect(certainty({ confidence: { level: "niedrig" } }).lvl).toBe("unsicher");
    expect(certainty({ confidence: { level: "hoch" }, sensitivity: { uncertain: true } }).uncertain).toBe(true);
  });
});

describe("segmentHtml", () => {
  it("level 1 has title, plain category, key line and no codes", () => {
    const { l1 } = split(segmentHtml(seg(), meta, "https://x/#a"));
    expect(l1).toContain('<h2 id="panel-title">Max-Brauer-Allee</h2>');
    expect(l1).toContain("Altona · 320 m");
    expect(l1).toContain("cat cat-GOW30");
    expect(l1).toContain("Stadtstraße 30");
    expect(l1).toContain("Heute 50 km/h → Ziel 30 km/h");
    expect(visible(l1)).not.toMatch(CODES);
  });

  it("uses glossary plain name when present", () => {
    const m = { ...meta, glossary: { categories: { GOW30: { plain: "Straße zwischen Stadtteilen" } } } };
    expect(segmentHtml(seg(), m, "u")).toContain("Straße zwischen Stadtteilen");
  });

  it("key line variants", () => {
    const k = (code, speed) => { const p = seg(); p.category.code = code; p.ist.speed_kmh = speed; return split(segmentHtml(p, meta, "u")).l1; };
    expect(k("GOW30", 30)).toContain("Tempo 30 km/h, wie heute");
    expect(k("GOW50", 50)).toContain("Tempo 50 km/h, wie heute");
    expect(k("ETW_ERF", 30)).toContain("Ziel Schritttempo");
    expect(k("SW", 50)).toContain("ohne Tempo-Ziel");
  });

  it("level 2 is open by default, closable, and free of codes", () => {
    const h = segmentHtml(seg(), meta, "u");
    expect(h).toContain('<details class="level l2" open><summary>Mehr erfahren</summary>');
    expect(segmentHtml(seg(), meta, "u", { level2Open: false })).toContain('<details class="level l2"><summary>');
    expect(visible(split(h).l2)).not.toMatch(CODES);
  });

  it("why lists only passed reasons as sentences without rule IDs", () => {
    const { l2 } = split(segmentHtml(seg(), meta, "u"));
    expect(l2).toContain('<h3 id="h-why">Warum?</h3>');
    expect(l2).toContain("Hauptverkehrsstraße der BVM.");
    expect(l2).toContain("Schule oder Kita direkt an der Straße.");
    expect(l2).not.toContain("Platz für einen baulichen Radweg");
  });

  it("changes use cycling.facility.ist_text, never ist.cycling", () => {
    const h = segmentHtml(seg(), meta, "u");
    const { l2 } = split(h);
    expect(l2).toContain("Radverkehr: heute Radfahrstreifen → Radweg auf beiden Seiten");
    expect(l2).toContain("Tempo 50 → 30 km/h");
    expect(l2).toContain("Kfz-Fahrstreifen je Richtung: 2 → 1");
    expect(h).not.toContain("keine Radverkehrsanlage");
  });

  it("no change entry for cycling gap none", () => {
    const p = seg(); p.cycling.facility.gap = "none"; p.cycling.lanes.change = "same";
    expect(split(segmentHtml(p, meta, "u")).l2).not.toContain("Radverkehr: heute");
  });

  it("one fit statement with drawing; falls back to crosssection without cycling profile", () => {
    const l2 = split(segmentHtml(seg(), meta, "u")).l2;
    expect(l2).toContain("Passt in den Straßenraum: 21,3 m nötig, 22,9 m vorhanden.");
    expect(l2).toContain("<svg");
    expect((l2.match(/class="fit"/g) ?? []).length).toBe(1);
    const p = seg(); delete p.cycling.profile;
    const l2b = split(segmentHtml(p, meta, "u")).l2;
    expect(l2b).toContain("Passt.");
    expect(l2b).not.toContain("<svg");
  });

  it("shows the uncertainty note only when uncertain", () => {
    expect(segmentHtml(seg(), meta, "u")).not.toContain("Diese Einstufung ist unsicher");
    const p = seg(); p.confidence.level = "niedrig";
    expect(split(segmentHtml(p, meta, "u")).l2).toContain('<p class="note">Diese Einstufung ist unsicher:');
  });

  it("feedback link by mailto or github issue", () => {
    expect(split(segmentHtml(seg(), meta, "u")).l2).toContain('href="mailto:x@example.org');
    expect(split(segmentHtml(seg(), { ...meta, github_repo: "a/b" }, "u")).l2).toContain("github.com/a/b/issues/new");
    expect(segmentHtml(seg(), { ...meta, feedback_email: null }, "u")).not.toContain("Stimmt etwas nicht?");
    expect(split(segmentHtml(seg(), meta, "u")).l2).toContain("Stimmt etwas nicht?");
  });

  it("level 3 is closed and has all details", () => {
    const { l3 } = split(segmentHtml(seg(), meta, "u"));
    expect(l3).toContain('<details class="level l3"><summary>Details und Quellen</summary>');
    expect(l3).not.toMatch(/level l3"[^>]* open/);
    for (const s of ["C-G30-02</code></a> trifft nicht zu", "C-GOW-01</code></a> trifft zu", "<code>GOW30</code>",
      "Wie sicher ist das?", "Alle Werte stammen aus Primärquellen.", "Abstand zur Schule niedriger", "D3 Mischform",
      "Tempo 2, Gestaltung 1, Nutzung 3", "Bezirksroute (Basisnetz)", "Fünf Prinzipien", "OSM-Auszug", "ODbL-1.0",
      "seg_5a4361a0331e0791", "0.21.0+2026-10-28"]) expect(l3).toContain(s);
  });

  it("escapes text", () => {
    const p = seg(); p.name = "<img onerror=x>";
    const h = segmentHtml(p, meta, "u");
    expect(h).not.toContain("<img");
    expect(h).toContain("&lt;img");
  });
});

describe("junctionHtml", () => {
  const j = () => ({
    id: "8541215407", names: "Altonaer Straße / Schulterblatt", bezirk: "Altona", version: "0.21.0",
    legs: [
      { name: "Max-Brauer-Allee", cat: "GOW30", cycle_cat: { label: "Radroute (Hauptnetz)" }, facility_text: "Radweg", dtv: 15000 },
      { name: "Schulterblatt", cat: "ETW30", cycle_cat: { label: "Bezirksroute" }, facility_text: "Mischverkehr", dtv: null },
      { name: "Schulterblatt", cat: "ETW30", cycle_cat: { label: "Radroute" }, facility_text: "Fahrradstraße", dtv: null },
    ],
    entering_dtv: 15000, space_radius_m: 30.3, soll: { code: "continuous_footway_exit", text: "durchgehender Gehweg" },
    ist: { text: "Ampel" }, action_needed: true, priority_rank: 3, rule: { id: "J-05", text: "Regel J-05 ergibt hier: Gehwegüberfahrt" },
    treatment: "Mittelinsel für die Querung.", confidence: { code: "high", text: "hoch" }, crashes: { cyc: 14 },
  });

  it("level 1 shows target type and status", () => {
    const { l1 } = split(junctionHtml(j(), meta, "u"));
    expect(l1).toContain('<h2 id="panel-title">Altonaer Straße / Schulterblatt</h2>');
    expect(l1).toContain("Durchgehender Gehweg");
    expect(l1).toContain("heute: Ampel · Umbau nötig");
    const p = j(); p.action_needed = false;
    expect(split(junctionHtml(p, meta, "u")).l1).toContain("heute: Ampel · passt");
  });

  it("level 2 names unique streets with plain category and the treatment", () => {
    const { l2 } = split(junctionHtml(j(), meta, "u"));
    expect(l2).toContain("Max-Brauer-Allee (Stadtstraße 30), Schulterblatt (Wohnstraße 30).");
    expect((visible(l2).match(/Schulterblatt/g) ?? []).length).toBe(1);
    expect(l2).toContain("Ziel: durchgehender Gehweg.");
    expect(l2).toContain("Mittelinsel für die Querung.");
    expect(visible(l2)).not.toMatch(CODES);
  });

  it("level 3 has legs with codes and numbers", () => {
    const { l3 } = split(junctionHtml(j(), meta, "u"));
    for (const s of ["<code>GOW30</code>", "Regel J-05", "15.000 Kfz/Tag", "30,3 m Radius", "14 (5 Jahre)", "<dd>3</dd>", "hoch", "8541215407", "0.21.0"]) expect(l3).toContain(s);
  });
});

describe("rule links", () => {
  it("level 3 links every rule ID and every step of the rule path to the reference", () => {
    const html = segmentHtml(seg(), meta, "https://x.test/", {});
    expect(html).toContain('<a href="#methode/regeln?regel=C-G30-02"><code>C-G30-02</code></a>');
    expect(html).toContain('<a href="#methode/regeln?regel=C-GOW-01"><code>C-GOW-01</code></a> → <a href="#methode/regeln?regel=C-G30-01">');
  });
});

// prompt 26: special places
describe("special place in the profile", () => {
  const sp = { place: "schanze_verkehrsberuhigt", band: "Besonderer Ort: Verkehrsberuhigte Schanze – Vorschlag des Bürgerbegehrens: Fahrradstraße",
    status_line: "Stand 25.09.2026: Unterschriften werden gesammelt", colour: "#cc0070",
    compare: "Unser Entwurf sieht hier auch eine Fahrradstraße vor.", notes: ["Heute gilt hier Tempo 50."] };

  it("shows the band below level 1 and the comparison after the rule text", () => {
    const html = segmentHtml({ ...seg(), special_place: sp }, meta, "https://x", { level2Open: true });
    const band = html.indexOf("place-band");
    expect(band).toBeGreaterThan(html.indexOf('class="key"'));
    expect(band).toBeLessThan(html.indexOf("Mehr erfahren"));
    expect(html).toContain("Stand 25.09.2026");
    expect(html.indexOf("Vorschlag für diesen Ort")).toBeGreaterThan(html.indexOf('id="h-why"'));
    expect(html).toContain("Heute gilt hier Tempo 50.");
  });

  it("keeps the rule explanation unchanged", () => {
    const norm = (h) => h.replace(/\s+/g, "").replace(/xs-[a-z0-9]+/g, "xs-id"); // random id of the cross-section drawing
    const strip = (h) => h.replace(/<divclass="place-band"[\s\S]*?<\/div>/, "").replace(/<h3>Vorschlagfürdiesen.*?<\/p>/, "");
    const without = segmentHtml(seg(), meta, "https://x");
    const withPlace = segmentHtml({ ...seg(), special_place: sp }, meta, "https://x");
    expect(strip(norm(withPlace))).toBe(norm(without));
  });

  it("draws the proposal's cross section after ours, or says it stays the same", () => {
    const profile = { elements: [{ element: "shared_surface", width_m: 4.75, side: "centre" }], available_m: 13.2, fit: "fits", fit_text: "passt in die Straße", same_as_soll: false };
    const m = { ...meta, special_places: { texts: { profile_title: "Querschnitt im Vorschlag", profile_same: "Der Querschnitt bleibt wie in unserem Ziel." } } };
    const html = segmentHtml({ ...seg(), special_place: { ...sp, profile, profile_note: "Ohne Parken am Rand." } }, m, "https://x");
    expect(html).toContain("Querschnitt im Vorschlag:");
    expect(html).toContain("Passt in die Straße.");
    expect(html).toContain("Ohne Parken am Rand.");
    const same = segmentHtml({ ...seg(), special_place: { ...sp, profile: { ...profile, same_as_soll: true } } }, m, "https://x");
    expect(same).toContain("Der Querschnitt bleibt wie in unserem Ziel.");
    expect(same).not.toContain("Querschnitt im Vorschlag:");
  });

  it("shows trees and parking on level 2, 'keine Daten' when unknown", () => {
    const t = { profile_title: "Bäume und Parkplätze", profile_parking: "Parkplätze: heute etwa {today}, im Ziel etwa {target}.",
      profile_parking_partial: "Parkplätze: auf einer Seite etwa {today}.", profile_parking_none: "Parkplätze: keine Daten.",
      profile_trees: "Straßenbäume: {n}, davon möglicherweise betroffen {affected}, neu möglich etwa {new}.",
      profile_trees_none: "Straßenbäume: keine.", profile_source: { official: "amtlich erfasste Stellplätze", none: "keine Daten" }, profile_note: "Schätzung." };
    const m = { ...meta, trees_parking: { texts: t } };
    const tp = { parking: { complete: true, today: 26.5, today_known: 26.5, target_min: 0, target_max: 0, src_left: "official", src_right: "official" },
      trees: { n: 7, affected_min: 1, affected_max: 4, new: 2.4 } };
    const html = segmentHtml({ ...seg(), trees_parking: tp }, m, "https://x");
    expect(html).toContain("Parkplätze: heute etwa 27, im Ziel etwa 0.");
    expect(html).toContain("(amtlich erfasste Stellplätze)");
    expect(html).toContain("Straßenbäume: 7, davon möglicherweise betroffen 1–4, neu möglich etwa 2.");
    const none = segmentHtml({ ...seg(), trees_parking: { parking: { complete: false, today_known: null, src_left: "none", src_right: "none" }, trees: { n: 0 } } }, m, "https://x");
    expect(none).toContain("Parkplätze: keine Daten.");
  });

  it("shows nothing without a special place", () => {
    expect(segmentHtml(seg(), meta, "https://x")).not.toContain("place-band");
  });
});
