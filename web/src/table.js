// Table view per district: sortable, paginated, keyboard operable; alternative to the map (WCAG 2.2).
import { rowMatches } from "./state.js";
import { esc, num } from "./util.js";

const PAGE_SIZE = 100;
// Robustness from the sensitivity analysis: true = unsicher, false = robust, null = not computed.
export const robust = (un) => (un === true ? "unsicher" : un === false ? "robust" : "–");
const COLUMNS = [
  { key: "name", label: "Straße", type: "text" },
  { key: "cat", label: "Soll", type: "text" },
  { key: "spd", label: "Ist-Tempo km/h", type: "num" },
  { key: "dt", label: "Diskrepanz", type: "text" },
  { key: "dm", label: "Stärke", type: "num" },
  { key: "acc", label: "Unfälle Fuß/Rad", type: "num" },
  { key: "pr", label: "Priorität", type: "num" },
  { key: "conf", label: "Datenunsicherheit", type: "text" },
  { key: "un", label: "Robustheit", type: "text" },
  { key: "len", label: "Länge m", type: "num" },
];

export function renderTable(root, rows, getState, { onOpen }) {
  let sort = { key: "pr", dir: "descending" };
  let page = 0;

  function sorted() {
    const f = rows.filter((r) => rowMatches(r, getState()));
    const col = COLUMNS.find((c) => c.key === sort.key);
    const sign = sort.dir === "ascending" ? 1 : -1;
    return f.sort((a, b) => {
      const x = a[sort.key], y = b[sort.key];
      if (x == null && y == null) return 0;
      if (x == null) return 1;
      if (y == null) return -1;
      return sign * (col.type === "num" ? x - y : String(x).localeCompare(String(y), "de"));
    });
  }

  function draw(focusKey) {
    const all = sorted();
    const pages = Math.max(1, Math.ceil(all.length / PAGE_SIZE));
    page = Math.min(page, pages - 1);
    const slice = all.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
    root.innerHTML = `
      <p id="table-summary">${num(all.length)} Abschnitte (Filter wie auf der Karte). Seite ${page + 1} von ${pages}.</p>
      <div class="table-wrap" tabindex="0" role="region" aria-labelledby="table-caption">
      <table>
        <caption id="table-caption">Abschnitte im Bezirk – sortierbar über die Spaltenköpfe</caption>
        <thead><tr>${COLUMNS.map((c) => `<th scope="col" aria-sort="${sort.key === c.key ? sort.dir : "none"}">
          <button type="button" data-sort="${c.key}">${esc(c.label)}</button></th>`).join("")}<th scope="col">Steckbrief</th></tr></thead>
        <tbody>${slice.map((r) => `<tr>
          <td>${esc(r.name ?? "–")}</td><td>${esc(r.cat)}</td><td>${num(r.spd)}</td><td>${esc(r.dt ?? (r.dm === null ? "nicht prüfbar" : "keine"))}</td>
          <td>${num(r.dm)}</td><td>${num(r.acc)}</td><td>${num(r.pr, 2)}</td><td>${esc(r.conf)}</td><td>${robust(r.un)}</td><td>${num(r.len)}</td>
          <td><button type="button" class="link" data-open="${esc(r.id)}">öffnen<span class="visually-hidden"> ${esc(r.name ?? r.id)}</span></button></td></tr>`).join("")}
        </tbody></table></div>
      <nav class="pager" aria-label="Seiten der Tabelle">
        <button type="button" data-page="prev" ${page === 0 ? "disabled" : ""}>Vorherige Seite</button>
        <button type="button" data-page="next" ${page >= pages - 1 ? "disabled" : ""}>Nächste Seite</button>
      </nav>`;
    if (focusKey) root.querySelector(`[data-sort="${focusKey}"]`)?.focus();
  }

  root.onclick = (ev) => {
    const b = ev.target.closest("button");
    if (!b) return;
    if (b.dataset.sort) {
      const key = b.dataset.sort;
      sort = { key, dir: sort.key === key && sort.dir === "descending" ? "ascending" : "descending" };
      page = 0;
      draw(key);
    } else if (b.dataset.page) {
      page += b.dataset.page === "next" ? 1 : -1;
      draw();
      root.querySelector("#table-summary")?.focus();
    } else if (b.dataset.open) {
      onOpen(b.dataset.open);
    }
  };
  draw();
  return { redraw: () => { page = 0; draw(); } };
}
