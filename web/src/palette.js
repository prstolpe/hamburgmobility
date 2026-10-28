// Display colours and line styles. Colour-blind safe (Paul Tol "vibrant"/"bright", dark variants), every colour
// with at least 3:1 contrast against the white casing under each line (WCAG 2.2, 1.4.11). Categories differ in
// colour, width and dash pattern, so they stay apart without colour vision.

export const CASING = "#ffffff";
export const UNKNOWN = "#767676";

export const CATEGORY_STYLE = {
  SW: { color: "#332288", width: 6, dash: null },
  GOW50: { color: "#CC3311", width: 5, dash: null },
  GOW30: { color: "#AA4499", width: 4, dash: [3, 1.5] },
  ETW30: { color: "#0077BB", width: 2.5, dash: null },
  ETW_ERF: { color: "#117733", width: 3, dash: [0.6, 1.4] },
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
    UNKNOWN,
  ];
}
