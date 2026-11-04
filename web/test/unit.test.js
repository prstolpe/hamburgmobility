import { describe, expect, it } from "vitest";
import { issueUrl, mailtoUrl } from "../src/feedback.js";
import { allColors, CASING, CATEGORY_STYLE, contrast } from "../src/palette.js";
import { profileHtml } from "../src/panel.js";
import { DEFAULTS, parseHash, rowMatches, toHash } from "../src/state.js";
import { robust } from "../src/table.js";

describe("URL state", () => {
  it("round-trips all fields", () => {
    const s = {
      ...DEFAULTS, page: "tabelle", layer: "disc", overlays: ["bus", "acc"], cats: ["GOW30", "ETW30"], dts: ["D1"],
      prmin: 1.5, bz: "Eimsbüttel", seg: "seg_00ab", map: { zoom: 14, lat: 53.57, lon: 9.95 },
    };
    expect(parseHash(toHash(s))).toEqual(s);
  });

  it("keeps defaults out of the URL", () => {
    expect(toHash({ ...DEFAULTS })).toBe("#karte");
  });

  it("ignores invalid values", () => {
    const s = parseHash("#nirgends?layer=foo&ov=bus,xyz&pr=-2&seg=<script>&map=a/b/c");
    expect(s.page).toBe("karte");
    expect(s.layer).toBe("cat");
    expect(s.overlays).toEqual(["bus"]);
    expect(s.prmin).toBe(0);
    expect(s.seg).toBeNull();
    expect(s.map).toBeNull();
  });

  it("filters table rows like the map", () => {
    const st = { ...DEFAULTS, cats: ["GOW30"], dts: ["keine"], prmin: 0 };
    expect(rowMatches({ cat: "GOW30", dt: null, pr: 0 }, st)).toBe(true);
    expect(rowMatches({ cat: "GOW30", dt: "D1", pr: 1 }, st)).toBe(false);
    expect(rowMatches({ cat: "ETW30", dt: null }, st)).toBe(false);
    expect(rowMatches({ cat: "GOW30", dt: "D1", pr: null }, { ...DEFAULTS, prmin: 1 })).toBe(false);
  });
});

describe("feedback links", () => {
  const profile = { id: "seg_1", name: "Hallerstraße", bezirk: "Eimsbüttel", version: "0.10.1+2026-10-28",
    category: { code: "GOW30", label: "Stadtstraße 30" } };

  it("builds a prefilled GitHub issue", () => {
    const url = new URL(issueUrl("owner/repo", profile, "https://x.test/#karte?seg=seg_1"));
    expect(url.pathname).toBe("/owner/repo/issues/new");
    expect(url.searchParams.get("title")).toContain("seg_1");
    expect(url.searchParams.get("body")).toContain("Soll-Kategorie: GOW30");
  });

  it("returns null without configuration", () => {
    expect(issueUrl(null, profile, "")).toBeNull();
    expect(issueUrl("not a repo", profile, "")).toBeNull();
    expect(mailtoUrl(null, profile, "")).toBeNull();
  });

  it("builds a mailto link", () => {
    expect(mailtoUrl("team@example.org", profile, "u")).toMatch(/^mailto:team@example\.org\?subject=/);
  });
});

describe("palette", () => {
  it("every colour has at least 3:1 contrast against the casing", () => {
    for (const c of allColors()) expect(contrast(c, CASING), c).toBeGreaterThanOrEqual(3);
  });

  it("categories differ in width or dash pattern, not only in colour", () => {
    const keys = Object.values(CATEGORY_STYLE).map((s) => `${s.width}|${JSON.stringify(s.dash)}`);
    expect(new Set(keys).size).toBe(keys.length);
  });
});

describe("robustness", () => {
  const base = {
    id: "seg_1", name: "Lohkampstraße", bezirk: "Eimsbüttel", length_m: 120, version: "0.11.0+2026-10-28",
    category: { code: "ETW30", label: "Quartiersstraße", text: "x", proposed: "ETW30", corrected: false },
    reasons: [], confidence: { level: "hoch", summary: "", reasons: [] },
    ist: {}, crosssection: { width_p10_m: null }, coherence: [], sources: [],
    discrepancy: { type: null, max: 0, speed: 0, design: 0, use: null, priority: 0, text: "keine", unknown_checks: [],
      crashes: { ped_cyc: 0, severe_fatal: 0, years: "2021–2025" } },
  };
  const meta = { github_repo: null, feedback_email: null };

  it("marks uncertain segments in the profile", () => {
    const p = { ...base, sensitivity: { uncertain: true, text: "In 42 % von 500 Rechenläufen …", uncertain_text: "Unsicher: …",
      oat_intro: "Die Kategorie wechselt schon …:", triggers: ["Schwelle für den Verbindungswert niedriger"] } };
    const html = profileHtml(p, meta, "https://example.org/");
    expect(html).toContain('class="tag-uncertain">unsicher');
    expect(html).toContain("Schwelle für den Verbindungswert niedriger");
  });

  it("shows no mark for robust segments or without data", () => {
    const stable = { ...base, sensitivity: { uncertain: false, text: "In allen 500 …", uncertain_text: null, oat_intro: null, triggers: [] } };
    expect(profileHtml(stable, meta, "https://example.org/")).not.toContain("tag-uncertain");
    expect(profileHtml({ ...base }, meta, "https://example.org/")).not.toContain("Robustheit");
  });

  it("notes harmonised categories", () => {
    const p = { ...base, category: { ...base.category, cascade: "GOW50" } };
    expect(profileHtml(p, meta, "https://example.org/")).toContain("Vorschlag der Regeln: GOW50");
    expect(profileHtml(base, meta, "https://example.org/")).not.toContain("angeglichen");
  });

  it("labels the table column", () => {
    expect([true, false, null, undefined].map(robust)).toEqual(["unsicher", "robust", "–", "–"]);
  });
});
