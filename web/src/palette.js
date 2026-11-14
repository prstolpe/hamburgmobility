// Display colours and line styles. Colour-blind safe (Paul Tol "bright", dark variants), every colour with at least
// 3:1 contrast against the white casing under each line (WCAG 2.2, 1.4.11). Groups of one legend differ in width or
// dash as well, so they stay apart without colour vision.

export const CASING = "#ffffff";
export const UNKNOWN = "#767676";
export const RURAL_FILL = "#767676"; // rural Stadtteile, not classified (area, not a line: no casing contrast needed)

// Redesign 2026-11 (docs/redesign/tokens.json): one meaning per data colour across the site.
// Tempo (today and target) has its own scale; a category is drawn in the colour of its target speed, its function by
// line width and dash. Need for action is one orange; cycling one petrol; reference and comparison lines are ink.
export const SPEED = { le20: "#117733", t30: "#0077BB", t40: "#AA4499", t50: "#CC3311", gt50: "#332288" };
export const NEED = "#B35900";
export const NONE = "#8a8a8a"; // "fits / no need / other ways": thin and grey, not green
export const INK = "#111111";
export const CYCLING = "#007A6E";
export const COLOR_CONCEPTS = {
  speed: Object.values(SPEED),
  need: [NEED],
  cycling: [CYCLING],
  neutral: [INK, NONE, "#4a4a4a"],
  unknown: [UNKNOWN],
};

export const CATEGORY_STYLE = {
  SW: { color: SPEED.gt50, width: 7, dash: null },
  GOW50: { color: SPEED.t50, width: 5, dash: null },
  GOW30: { color: SPEED.t30, width: 5, dash: [3, 1.5] },
  ETW30: { color: SPEED.t30, width: 2.5, dash: null },
  ETW_ERF: { color: SPEED.le20, width: 2.5, dash: [0.6, 1.4] },
  // außerorts (inaktiv, C-RUR-01)
  GOW80: { color: SPEED.gt50, width: 5, dash: [6, 2] },
  ETW60: { color: SPEED.gt50, width: 2.5, dash: [1.5, 1.5] },
};

export const SPEED_CLASSES = [
  { max: 20, label: "bis 20 km/h (auch Schrittgeschwindigkeit)", color: SPEED.le20, width: 2, dash: [0.6, 1.4] },
  { max: 30, label: "30 km/h", color: SPEED.t30, width: 2.5, dash: null },
  { max: 40, label: "40 km/h", color: SPEED.t40, width: 3, dash: [3, 1.5] },
  { max: 50, label: "50 km/h", color: SPEED.t50, width: 4, dash: null },
  { max: Infinity, label: "über 50 km/h", color: SPEED.gt50, width: 5.5, dash: null },
];

// Discrepancy: strength = width (in layers.js), type = dash, all in the need colour
export const DISC_TYPE_STYLE = {
  D1: { color: NEED, dash: null },
  D2: { color: NEED, dash: [2, 1] },
  D3: { color: NEED, dash: [0.6, 1.4] },
};

export const FEASIBILITY_STYLE = {
  fits: { color: NONE, width: 1.5, dash: null },
  tight: { color: NEED, width: 3, dash: [3, 1.5] },
  does_not_fit: { color: NEED, width: 4.5, dash: null },
};

// Street width is a measurement, not a judgement: ink, wider line = wider street
export const WIDTH_STYLE = {
  narrow: { color: INK, width: 1.5, dash: null },
  middle: { color: INK, width: 3, dash: null },
  wide: { color: INK, width: 5, dash: null },
};

export const OVERLAY_COLORS = { bus: "#4a4a4a", cyc: CYCLING, fac: INK, acc: INK };

// --- cycling layers: one colour, hierarchy by width, type by dash -----------------------------

export const CYCLE_CAT_STYLE = {
  RSV: { color: CYCLING, width: 6, dash: null },
  HAUPT: { color: CYCLING, width: 4.5, dash: null },
  BASIS: { color: CYCLING, width: 3, dash: [3, 1.5] },
  ERSCHL: { color: NONE, width: 1.2, dash: null },
};

export const FACILITY_STYLE = {
  separated_oneway_both: { color: CYCLING, width: 4.5, dash: null },
  separated_twoway: { color: CYCLING, width: 4, dash: [4, 1.5] },
  cycle_lane: { color: CYCLING, width: 3, dash: [2, 1] },
  cycle_street: { color: CYCLING, width: 3.5, dash: [0.6, 1.4] },
  own_path: { color: CYCLING, width: 2.5, dash: [1, 2] },
  mixed: { color: NONE, width: 1.5, dash: null },
};

export const GAP_STYLE = {
  missing: { color: NEED, width: 4.5, dash: null },
  wrong_type: { color: NEED, width: 3.5, dash: [3, 1.5] },
  partial: { color: NEED, width: 3, dash: [1.5, 1] },
  too_narrow: { color: NEED, width: 3.5, dash: [0.6, 1.4] },
  none: { color: NONE, width: 1.5, dash: null },
};

export const LANES_STYLE = {
  fewer: { color: NEED, width: 4.5, dash: null },
  same: { color: NONE, width: 1.5, dash: null },
  more: { color: NEED, width: 3, dash: [2, 1.5] },
  shared: { color: NONE, width: 1.2, dash: [2, 2] },
};

export const FIT_STYLE = {
  fits: { color: NONE, width: 1.5, dash: null },
  fits_after_degrade: { color: NEED, width: 3, dash: [2, 1.5] },
  does_not_fit: { color: NEED, width: 4.5, dash: null },
};

export const OFFICIAL_STYLE = {
  Bestand: { color: INK, width: 3, dash: null },
  "In Arbeit": { color: INK, width: 2.5, dash: [3, 1.5] },
  planned: { color: INK, width: 2, dash: [0.6, 1.4] },
};
export const REFERENCE_COLOR = CYCLING; // Soll network under the official one (comparison only, drawn transparent)

// Symbol shapes in a 16 x 16 box (legend SVG and map icons). fill = filled shape, stroke = outline only.
export const SHAPES = {
  circle: { d: "M8 2a6 6 0 1 0 0.01 0z", mode: "fill" },
  square: { d: "M2.5 2.5h11v11h-11z", mode: "fill" },
  triangle: { d: "M8 1.5l6.5 12h-13z", mode: "fill" },
  diamond: { d: "M8 1l7 7-7 7-7-7z", mode: "fill" },
  ring: { d: "M8 3a5 5 0 1 0 0.01 0z", mode: "stroke" },
  bar: { d: "M1 5h14v6H1z", mode: "fill" },
  cross: { d: "M3 3L13 13M13 3L3 13", mode: "stroke" },
};

export const JUNCTION_STYLE = {
  roundabout: { color: INK, shape: "circle" },
  signal: { color: INK, shape: "square" },
  priority: { color: INK, shape: "triangle" },
  continuous: { color: INK, shape: "diamond" },
  equal: { color: INK, shape: "ring" },
  grade_separated: { color: INK, shape: "bar" },
  none: { color: UNKNOWN, shape: "cross" },
};
export const JUNCTION_REBUILD = NEED; // same shape, need colour: rebuild needed

// --- WCAG contrast -------------------------------------------------------------------------

function channel(c) {
  const s = c / 255;
  return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
}

export function luminance(hex) {
  const n = parseInt(hex.replace("#", ""), 16);
  return 0.2126 * channel((n >> 16) & 255) + 0.7152 * channel((n >> 8) & 255) + 0.0722 * channel(n & 255);
}

export function contrast(a, b) {
  const [l1, l2] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
}

export function allColors() {
  return [
    ...Object.values(CATEGORY_STYLE).map((s) => s.color),
    ...SPEED_CLASSES.map((s) => s.color),
    ...Object.values(DISC_TYPE_STYLE).map((s) => s.color),
    ...Object.values(FEASIBILITY_STYLE).map((s) => s.color),
    ...Object.values(WIDTH_STYLE).map((s) => s.color),
    ...Object.values(OVERLAY_COLORS),
    ...[CYCLE_CAT_STYLE, FACILITY_STYLE, GAP_STYLE, LANES_STYLE, FIT_STYLE, OFFICIAL_STYLE, JUNCTION_STYLE]
      .flatMap((st) => Object.values(st).map((x) => x.color)),
    REFERENCE_COLOR,
    JUNCTION_REBUILD,
    UNKNOWN,
  ];
}
