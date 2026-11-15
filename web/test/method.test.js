import { describe, expect, it } from "vitest";
import { chapterHtml, filterRules, fill, referenceHtml, ruleDetailsHtml, SOURCE_TYPE_TEXT, summaryHtml } from "../src/method.js";

const method = {
  title: "So entsteht der Entwurf",
  summary: { what_title: "Was ist das?", what: "Aufgabe für {area_label}.", shows_title: "Zeigt", shows: [{ title: "Eins", text: "Text <b>1</b>" }],
    not_title: "Zeigt nicht", not: [{ title: "Zwei", text: "Text 2" }], assumptions: "{n_a} von {n_b} sind Annahmen." },
  chapters: [
    { key: "aufgabe", title: "Aufgabe", l1: "Ein Satz.", l2: "Es gibt {n_rules} Regeln.\n\n| A | B |\n|---|---|\n| 1 | 2 |" },
    { key: "radnetz", title: "Radnetz", l1: "Rad.", l2: "Text." },
  ],
  reference: { title: "Alle Regeln", intro: "Intro." }, news: [],
  vars: { area_label: "Hamburg & Umland", n_rules: 1196, n_a: 5, n_b: null },
};
const rule = (o = {}) => ({ id: "C-G30-02", file: "rules.yaml", section: "classification", chapter: "aufgabe", label_plain: "Platz für Radweg",
  explain_plain: "Erklärung", why: "Weil <x>", description: "desc", note: "note", history: ["seit 0.18.0"], technical: [["if", "a < b"]],
  thresholds: [{ key: "w", label_plain: "Breite", value: 2.5, unit: "m", source_type: "assumption", check: "Stichprobe" }],
  source: [{ key: "S", title: "Quelle A", date: "2023-04", url: "https://x.test/a" }], source_type: "assumption", status: "draft",
  decides: { n: 1200, km: 12.5, unit: "Abschnitte" }, ...o });
const rules = [rule(), rule({ id: "C-SW-01", label_plain: "Autobahn", explain_plain: "Schnellstraße", source_type: "swov_crow", decides: null, history: null, thresholds: [] }),
  rule({ id: "L-01", chapter: "radnetz", label_plain: "Rad", decides: { n: 3, km: 0, unit: "Kreuzungen" } })];

describe("fill", () => {
  it("formats numbers German, null as dash", () => {
    expect(fill("{n_rules} / {n_b}", method.vars)).toBe("1.196 / –");
  });
});

describe("summaryHtml", () => {
  const html = summaryHtml(method, { disclaimer: "Nicht amtlich" });
  it("fills placeholders and escapes", () => {
    expect(html).toContain("Aufgabe für Hamburg &amp; Umland.");
    expect(html).toContain("5 von – sind Annahmen.");
    expect(html).toContain("Text &lt;b&gt;1&lt;/b&gt;");
    expect(html).not.toContain("{");
  });
  it("links chapters and the reference (no news page) and shows the disclaimer", () => {
    for (const h of ["#methode/aufgabe", "#methode/radnetz", "#methode/regeln"]) expect(html).toContain(`href="${h}"`);
    expect(html).not.toContain("#methode/neu");
    expect(html).toContain("Nicht amtlich");
    expect(html.match(/<h1>/g)).toHaveLength(1);
  });
});

describe("chapterHtml", () => {
  it("renders markdown after filling, wraps tables, lists only rules of the chapter", () => {
    const html = chapterHtml(method, "aufgabe", rules, {});
    expect(html).toContain("Es gibt 1.196 Regeln.");
    expect(html).toContain('class="table-wrap"');
    expect(html).toContain("Platz für Radweg");
    expect(html).not.toContain("<code>L-01</code>");
    expect(html).toContain("Details und Quellen");
    expect(html).toContain('href="#methode/radnetz"');
    expect(html).toContain('href="#methode"');
  });
  it("shows the cycling disclaimer on chapter radnetz only", () => {
    const meta = { cycling: { disclaimer: "Radnetz-Entwurf nicht amtlich" } };
    expect(chapterHtml(method, "radnetz", rules, meta)).toContain("Radnetz-Entwurf nicht amtlich");
    expect(chapterHtml(method, "aufgabe", rules, meta)).not.toContain("Radnetz-Entwurf");
  });
  it("unknown chapter falls back to the summary", () => {
    expect(chapterHtml(method, "nix", rules, {})).toContain("Was ist das?");
  });
});

describe("ruleDetailsHtml", () => {
  it("shows all level 3 facts, escaped", () => {
    const html = ruleDetailsHtml(rule(), "owner/name");
    expect(html).toContain("Weil &lt;x&gt;");
    expect(html).toContain("<code>C-G30-02</code>");
    expect(html).toContain(SOURCE_TYPE_TEXT.assumption);
    expect(html).toContain('<a href="https://x.test/a"');
    expect(html).toContain("2,5 m");
    expect(html).toContain("Annahme</span>");
    expect(html).toContain("<code>a &lt; b</code>");
    expect(html).toContain("Geschichte");
    expect(html).toContain("Entscheidet im aktuellen Lauf: 1.200 Abschnitte, 12,5 km");
    expect(html).toContain("https://github.com/owner/name/blob/main/config/rules.yaml");
  });
  it("omits optional parts", () => {
    const html = ruleDetailsHtml(rule({ decides: null, history: null, thresholds: [], source: [] }));
    for (const x of ["Entscheidet", "Geschichte", "<table", "Quellen", "github.com"]) expect(html).not.toContain(x);
  });
  it("junction counts", () => {
    expect(ruleDetailsHtml(rule({ decides: { n: 3, km: 0, unit: "Kreuzungen" } }))).toContain("3 Kreuzungen");
  });
  it("maps all source types to words", () => {
    expect(Object.keys(SOURCE_TYPE_TEXT).sort()).toEqual(["assumption", "de_regelwerk", "hamburg", "swov_crow"]);
  });
});

describe("filterRules / referenceHtml", () => {
  it("filters by id, label and explanation, case-insensitive", () => {
    expect(filterRules(rules, { q: "c-sw" }).map((r) => r.id)).toEqual(["C-SW-01"]);
    expect(filterRules(rules, { q: "AUTOBAHN" })).toHaveLength(1);
    expect(filterRules(rules, { q: "schnellstraße" })).toHaveLength(1);
    expect(filterRules(rules, {})).toHaveLength(3);
  });
  it("only assumptions", () => {
    expect(filterRules(rules, { onlyAssumption: true }).map((r) => r.id)).toEqual(["C-G30-02", "L-01"]);
  });
  it("groups by chapter, anchors every rule, shows versions", () => {
    const html = referenceHtml(method, rules, {}, { "rules.yaml": "0.21.1", "cycling_rules.yaml": "0.11.2", "design_rules.yaml": "0.9.1" });
    expect(html).toContain('id="regel-C-G30-02"');
    expect(html).toContain("Regelwerk 0.21.1 · Radnetz 0.11.2 · Querschnitt und Kreuzungen 0.9.1");
    expect(html).toContain('href="#daten"');
    expect(html).toContain('id="rule-q"');
    expect(html.indexOf("<h2 id=\"g-aufgabe\">")).toBeLessThan(html.indexOf("<h2 id=\"g-radnetz\">"));
  });
  it("says so when nothing matches", () => {
    expect(referenceHtml(method, rules, { q: "zzz" })).toContain("Keine Regel gefunden");
  });
});

describe("former rule ids", () => {
  it("resolves an alias to the rule that took it over", async () => {
    const { resolveRule, ruleDetailsHtml } = await import("../src/method.js");
    const rules = [{ id: "J-01", aliases: ["J-02"] }, { id: "J-03" }];
    expect(resolveRule(rules, "J-02")).toBe("J-01");
    expect(resolveRule(rules, "J-03")).toBe("J-03");
    expect(resolveRule(rules, "X-9")).toBe("X-9");
    expect(ruleDetailsHtml({ id: "J-01", aliases: ["J-02"], file: "design_rules.yaml", section: "junctions" })).toContain("früher auch <code>J-02</code>");
  });
});
