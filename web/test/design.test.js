// Design system rules (redesign 2026-11, package 1; docs/redesign/03_design_system.md, tokens.json):
// one meaning per data colour, categories in the colour of their target speed, redundant encoding (width/dash),
// self-hosted Inter without external services, no ornament (no shadows, no radius).
import { readFileSync, statSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  allColors, CATEGORY_STYLE, COLOR_CONCEPTS, CYCLE_CAT_STYLE, FACILITY_STYLE, FEASIBILITY_STYLE, FIT_STYLE, GAP_STYLE,
  JUNCTION_REBUILD, JUNCTION_STYLE, LANES_STYLE, SPEED, SPEED_CLASSES,
} from "../src/palette.js";

const TARGET = { SW: "gt50", GOW50: "t50", GOW30: "t30", ETW30: "t30", ETW_ERF: "le20", GOW80: "gt50", ETW60: "gt50" };
const up = (c) => c.toUpperCase();
const conceptOf = (c) => Object.entries(COLOR_CONCEPTS).filter(([, cs]) => cs.map(up).includes(up(c))).map(([k]) => k);
const key = (s) => `${s.width}|${JSON.stringify(s.dash ?? null)}`;

describe("one meaning per colour", () => {
  it("no colour belongs to two concepts", () => {
    const all = Object.values(COLOR_CONCEPTS).flat().map(up);
    expect(new Set(all).size).toBe(all.length);
  });

  it("every colour on the map belongs to exactly one concept", () => {
    for (const c of allColors()) expect(conceptOf(c), c).toHaveLength(1);
  });

  it("categories are drawn in the colour of their target speed", () => {
    for (const [k, s] of Object.entries(CATEGORY_STYLE)) expect(up(s.color), k).toBe(up(SPEED[TARGET[k]]));
  });

  it("evaluative layers use only need, neutral and unknown colours (no green for 'fits')", () => {
    for (const table of [FEASIBILITY_STYLE, GAP_STYLE, LANES_STYLE, FIT_STYLE]) {
      for (const [k, s] of Object.entries(table)) expect(["need", "neutral", "unknown"], k).toContain(conceptOf(s.color)[0]);
    }
  });

  it("cycling layers use the cycling colour or neutral grey", () => {
    for (const table of [CYCLE_CAT_STYLE, FACILITY_STYLE]) {
      for (const [k, s] of Object.entries(table)) expect(["cycling", "neutral"], k).toContain(conceptOf(s.color)[0]);
    }
  });

  it("junction type is shown by shape, rebuild by the need colour", () => {
    for (const s of Object.values(JUNCTION_STYLE)) expect(conceptOf(s.color)[0]).toMatch(/neutral|unknown/);
    expect(conceptOf(JUNCTION_REBUILD)[0]).toBe("need");
  });
});

describe("redundant encoding", () => {
  it("Radvorrangroute is a double line (white centre stripe), Radroute solid, Bezirksroute dashed", () => {
    expect(CYCLE_CAT_STYLE.RSV.inner).toMatchObject({ color: "#ffffff" });
    expect(CYCLE_CAT_STYLE.RSV.inner.width).toBeLessThan(CYCLE_CAT_STYLE.RSV.width / 2);
    expect(CYCLE_CAT_STYLE.HAUPT.inner).toBeUndefined();
    expect(CYCLE_CAT_STYLE.BASIS.dash).toBeTruthy();
  });

  it("speed classes differ in width or dash, not only in colour", () => {
    const keys = SPEED_CLASSES.map(key);
    expect(new Set(keys).size).toBe(keys.length);
  });

  it("evaluative and cycling tables differ in width or dash within each table", () => {
    for (const table of [FEASIBILITY_STYLE, GAP_STYLE, LANES_STYLE, FIT_STYLE, CYCLE_CAT_STYLE, FACILITY_STYLE]) {
      const keys = Object.values(table).map(key);
      expect(new Set(keys).size).toBe(keys.length);
    }
  });
});

describe("typography and objectivity", () => {
  const css = readFileSync(new URL("../src/style.css", import.meta.url), "utf8");

  it("self-hosts Inter (relative url, no external font service)", () => {
    expect(css).toMatch(/@font-face\s*{[^}]*font-family:\s*"Inter"[^}]*url\("\.\/fonts\/InterVariable\.woff2"\)/);
    expect(css).not.toMatch(/url\(["']?https?:/);
    expect(css).not.toMatch(/@import/);
  });

  it("ships the font with its licence, subset to a small file", () => {
    expect(statSync(new URL("../src/fonts/InterVariable.woff2", import.meta.url)).size).toBeLessThan(150_000);
    expect(readFileSync(new URL("../src/fonts/OFL-Inter.txt", import.meta.url), "utf8")).toContain("SIL Open Font License");
  });

  it("uses no shadows and no rounded corners (focus ring excepted)", () => {
    const val = (v) => v.replace("!important", "").trim();
    const shadows = [...css.matchAll(/box-shadow:\s*([^;]+);/g)].map((m) => val(m[1])).filter((v) => !/var\(--ink\)/.test(v) && v !== "none");
    expect(shadows).toEqual([]);
    // the round traffic light (.light) is replaced in package 2 (decision E3c)
    const radius = [...css.replace(/\.light \{[^}]*\}/, "").matchAll(/border-radius:\s*([^;]+);/g)].map((m) => val(m[1])).filter((v) => v !== "0");
    expect(radius).toEqual([]);
  });

  it("uses tabular figures in tables", () => {
    expect(css).toMatch(/table\s*{[^}]*font-variant-numeric:\s*tabular-nums/);
  });
});
