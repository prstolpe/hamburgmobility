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

/** URL of a data file next to the page (or below tiles_base_url for tiles). */
export function dataUrl(path, base = null) {
  return new URL(path, base ?? document.baseURI).href;
}
