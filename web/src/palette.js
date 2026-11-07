// Display colours and line styles. Colour-blind safe (Paul Tol "vibrant"/"bright", dark variants), every colour
// with at least 3:1 contrast against the white casing under each line (WCAG 2.2, 1.4.11). Categories differ in
// colour, width and dash pattern, so they stay apart without colour vision.

export const CASING = "#ffffff";
export const UNKNOWN = "#767676";
export const RURAL_FILL = "#767676"; // rural Stadtteile, not classified (area, not a line: no casing contrast needed)

export const CATEGORY_STYLE = {
  SW: { color: "#332288", width: 6, dash: null },
  GOW50: { color: "#CC3311", width: 5, dash: null },
  GOW30: { color: "#AA4499", width: 4, dash: [3, 1.5] },
  ETW30: { color: "#0077BB", width: 2.5, dash: null },
  ETW_ERF: { color: "#117733", width: 3, dash: [0.6, 1.4] },
  // außerorts (Regel S-FEAT-BUA-01, Entwurf)
  GOW80: { color: "#882255", width: 5, dash: [6, 2] },
  ETW60: { color: "#007A6E", width: 2.5, dash: [1.5, 1.5] },
};

export const SPEED_CLASSES = [
  { max: 20, label: "bis 20 km/h (auch Schrittgeschwindigkeit)", color: "#117733" },
  { max: 30, label: "30 km/h", color: "#0077BB" },
  { max: 40, label: "40 km/h", color: "#AA4499" },
  { max: 50, label: "50 km/h", color: "#CC3311" },
  { max: Infinity, label: "über 50 km/h", color: "#332288" },
];

export const DISC_TYPE_STYLE = {
  D1: { color: "#CC3311", dash: null },
  D2: { color: "#0077BB", dash: [2, 1] },
  D3: { color: "#AA4499", dash: [0.6, 1.4] },
};

export const FEASIBILITY_STYLE = {
  fits: { color: "#117733", dash: null },
  tight: { color: "#B35900", dash: [3, 1.5] },
  does_not_fit: { color: "#CC3311", dash: [0.6, 1.4] },
};

export const WIDTH_STYLE = {
  narrow: { color: "#CC3311", dash: [0.6, 1.4] },
  middle: { color: "#AA4499", dash: [3, 1.5] },
  wide: { color: "#0077BB", dash: null },
};

export const OVERLAY_COLORS = { bus: "#004949", cyc: "#117733", fac: "#332288", acc: "#000000" };

// --- cycling layers (prompt 21): colour plus line style or symbol shape ----------------------

export const CYCLE_CAT_STYLE = {
  RSV: { color: "#332288", width: 6, dash: null },
  HAUPT: { color: "#CC3311", width: 4.5, dash: null },
  BASIS: { color: "#0077BB", width: 3, dash: [3, 1.5] },
  ERSCHL: { color: "#007A6E", width: 1.5, dash: [1, 1.5] },
};

export const FACILITY_STYLE = {
  separated_oneway_both: { color: "#117733", width: 4.5, dash: null },
  separated_twoway: { color: "#007A6E", width: 4, dash: [4, 1.5] },
  cycle_lane: { color: "#0077BB", width: 3.5, dash: [2, 1] },
  cycle_street: { color: "#AA4499", width: 3.5, dash: null },
  own_path: { color: "#332288", width: 3, dash: [0.6, 1.4] },
  mixed: { color: "#555555", width: 1.5, dash: null },
};

export const GAP_STYLE = {
  missing: { color: "#CC3311", width: 4.5, dash: null },
  wrong_type: { color: "#B35900", width: 3.5, dash: [3, 1.5] },
  too_narrow: { color: "#AA4499", width: 3.5, dash: [0.6, 1.4] },
  none: { color: "#117733", width: 2, dash: null },
};

export const LANES_STYLE = {
  fewer: { color: "#117733", width: 4.5, dash: null },
  same: { color: "#0077BB", width: 3, dash: [3, 1.5] },
  more: { color: "#CC3311", width: 4.5, dash: [0.6, 1.4] },
  shared: { color: "#555555", width: 1.2, dash: null },
};

export const FIT_STYLE = {
  fits: { color: "#117733", width: 3.5, dash: null },
  fits_after_degrade: { color: "#B35900", width: 3.5, dash: [3, 1.5] },
  does_not_fit: { color: "#CC3311", width: 3.5, dash: [0.6, 1.4] },
};

export const OFFICIAL_STYLE = {
  Bestand: { color: "#117733", width: 4.5, dash: null },
  "In Arbeit": { color: "#0077BB", width: 3.5, dash: [3, 1.5] },
  planned: { color: "#AA4499", width: 3, dash: [0.6, 1.4] },
};
export const REFERENCE_COLOR = "#767676"; // Soll network under the official one (comparison only)

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
  roundabout: { color: "#0077BB", shape: "circle" },
  signal: { color: "#CC3311", shape: "square" },
  priority: { color: "#AA4499", shape: "triangle" },
  continuous: { color: "#117733", shape: "diamond" },
  equal: { color: "#332288", shape: "ring" },
  grade_separated: { color: "#B35900", shape: "bar" },
  none: { color: UNKNOWN, shape: "cross" },
};

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
    UNKNOWN,
  ];
}
