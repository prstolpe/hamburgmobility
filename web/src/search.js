// Street search with autocomplete (WAI-ARIA combobox pattern) over search.json.
import Fuse from "fuse.js";
import { esc } from "./util.js";

const MAX = 8;

export function setupSearch(input, listbox, entries, onPick) {
  const fuse = new Fuse(entries, { keys: ["name"], threshold: 0.3, ignoreLocation: true });
  let results = [];
  let active = -1;

  function close() {
    listbox.hidden = true;
    input.setAttribute("aria-expanded", "false");
    input.removeAttribute("aria-activedescendant");
    active = -1;
  }

  function render() {
    listbox.innerHTML = results.map((r, i) => `<li id="opt-${i}" role="option" aria-selected="${i === active}"
      data-i="${i}">${esc(r.name)} <span class="muted">${esc(r.bezirk)}, ${r.n} Abschnitt${r.n === 1 ? "" : "e"}</span></li>`).join("");
    listbox.hidden = results.length === 0;
    input.setAttribute("aria-expanded", String(results.length > 0));
    if (active >= 0) input.setAttribute("aria-activedescendant", `opt-${active}`);
  }

  function pick(i) {
    const r = results[i];
    if (!r) return;
    input.value = r.name;
    close();
    onPick(r);
  }

  input.addEventListener("input", () => {
    const q = input.value.trim();
    results = q.length < 2 ? [] : fuse.search(q, { limit: MAX }).map((x) => x.item);
    active = -1;
    render();
  });
  input.addEventListener("keydown", (ev) => {
    if (ev.key === "ArrowDown" && results.length) { active = (active + 1) % results.length; render(); ev.preventDefault(); }
    else if (ev.key === "ArrowUp" && results.length) { active = (active - 1 + results.length) % results.length; render(); ev.preventDefault(); }
    else if (ev.key === "Enter") { pick(active >= 0 ? active : 0); ev.preventDefault(); }
    else if (ev.key === "Escape") close();
  });
  listbox.addEventListener("mousedown", (ev) => {
    const li = ev.target.closest("li[data-i]");
    if (li) { pick(Number(li.dataset.i)); ev.preventDefault(); }
  });
  input.addEventListener("blur", () => setTimeout(close, 100));
}
