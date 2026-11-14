// Merged page "Daten": downloads and sources & licences under one h1 (redesign).
import { downloadsHtml, sourcesHtml } from "./pages.js";

/** Removes the leading <h1>…</h1> of a fragment so the merged page keeps a single h1. */
function withoutH1(html) {
  return html.replace(/^\s*<h1>[\s\S]*?<\/h1>/, "");
}

export async function dataHtml(meta) {
  const downloads = withoutH1(downloadsHtml(meta));
  const sources = withoutH1(await sourcesHtml(meta));
  return `
  <h1>Daten</h1>
  <p>Hier können Sie alle Daten des Entwurfs herunterladen. Darunter steht, woher die Daten kommen und unter welcher Lizenz sie stehen.</p>
  <section id="daten-downloads" aria-labelledby="h-dl"><h2 id="h-dl">Herunterladen</h2>${downloads}</section>
  <section id="daten-quellen" aria-labelledby="h-src"><h2 id="h-src">Quellen und Lizenzen</h2>${sources}</section>`;
}
