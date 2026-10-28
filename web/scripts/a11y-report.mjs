// Writes reports/web_accessibility.md from the axe results of `npm run a11y` (test-results/axe-*.json).
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const axeVersion = require("axe-core/package.json").version;
const projects = ["desktop", "mobile"].filter((p) => existsSync(`test-results/axe-${p}.json`));
const rows = projects.flatMap((p) => JSON.parse(readFileSync(`test-results/axe-${p}.json`, "utf8")));
const count = (impact) => rows.reduce((n, r) => n + r.violations.filter((v) => v.impact === impact).length, 0);
const cell = (r) => (r.violations.length
  ? r.violations.map((v) => `${v.id} (${v.impact}, ${v.nodes}×)`).join("; ") : "keine");
const lines = [
  "# Barrierefreiheit der Webseite (axe-core)", "",
  `Erzeugt: ${new Date().toISOString().slice(0, 19)}Z mit \`npm --prefix web run a11y\` (Playwright, axe-core ${axeVersion}, `
  + "Regeln WCAG 2.0/2.1/2.2 A und AA) gegen `vite preview` mit den Daten aus data/out. Geräte: Desktop Chrome und "
  + "Pixel 7 (emuliert).", "",
  `Ergebnis: **${count("critical")} kritisch, ${count("serious")} schwerwiegend, ${count("moderate")} mittel, `
  + `${count("minor")} gering.**`, "",
  "| Gerät | Seite | Verstöße | bestanden | manuell prüfen |", "| --- | --- | --- | ---: | ---: |",
  ...rows.map((r) => `| ${r.project} | ${r.name} | ${cell(r)} | ${r.passes} | ${r.incomplete} |`),
  "", "## Nicht automatisch prüfbar (offen)", "",
  "- Bedienung mit Bildschirmleser (VoiceOver, NVDA) und Test auf einem echten Smartphone.",
  "- Karteninhalte sind für Bildschirmleser über die Tabellenansicht und die Suche zugänglich; die Karte selbst ist per "
  + "Tastatur verschieb- und zoombar.",
  "- Farbkontrast der Kartenlinien: im Unit-Test geprüft (jede Farbe ≥ 3:1 gegen die weiße Kontur, web/test/unit.test.js); "
  + "Kategorien unterscheiden sich zusätzlich in Breite und Strichmuster.",
  "- HTTP-Range-Anfragen: lokal mit `vite preview` geprüft (206 für beide PMTiles-Dateien); beim Hosting nach dem ersten "
  + "Deployment mit `web/scripts/check-range.sh <URL>` prüfen.", "",
];
writeFileSync("../reports/web_accessibility.md", lines.join("\n"));
console.log(`a11y report: ${rows.length} page checks, critical ${count("critical")}, serious ${count("serious")}`);
