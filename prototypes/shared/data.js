// Data loading for the prototypes (export data/out + small files in prototypes/shared).
export const BZ = "Eimsbüttel";
const root = (p) => new URL(p, `${location.origin}/`).href;

export async function json(p) {
  const r = await fetch(root(p));
  if (!r.ok) throw new Error(`${p}: HTTP ${r.status}`);
  return r.json();
}

export async function loadAll() {
  const [meta, kpi, scenario] = await Promise.all([json("meta.json"), json("shared/kpi.json"), json("shared/scenario_eimsbuettel.json")]);
  return { meta, kpi, scenario };
}

export const profile = (id) => json(`segments/${id}.json`);
export const junction = (id) => json(`junctions/${id}.json`);
export const fmt = (v, d = 0) => (v == null ? "–" : Number(v).toLocaleString("de-DE", { minimumFractionDigits: d, maximumFractionDigits: d }));
