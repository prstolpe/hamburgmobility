// Small helpers shared by the views.

export function esc(v) {
  return String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

export function num(v, digits = 0) {
  if (v === null || v === undefined || Number.isNaN(v)) return "–";
  return Number(v).toLocaleString("de-DE", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

export function yesNo(v) {
  if (v === null || v === undefined) return "unbekannt";
  return v ? "ja" : "nein";
}

/** Rounded estimate for text: 2 to 3 significant digits (trees and parking, prompts/26); null stays null. */
export function approx(v) {
  if (v === null || v === undefined || Number.isNaN(v)) return null;
  const a = Math.abs(v);
  const step = a >= 10000 ? 1000 : a >= 1000 ? 100 : a >= 100 ? 10 : 1;
  return num(Math.round(v / step) * step);
}

/** "a–b" from two estimates, one value when they round to the same. */
export function approxRange(lo, hi) {
  const a = approx(lo);
  const b = approx(hi);
  if (a === null) return b ?? "–";
  return b === null || a === b ? a : `${a}–${b}`;
}

/** URL of a data file next to the page (or below tiles_base_url for tiles). */
export function dataUrl(path, base = null) {
  return new URL(path, base ?? document.baseURI).href;
}
