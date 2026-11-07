// Local prototypes of the UI review (prompt 21b, phase 3.2). Not deployed.
// Start from web/ (uses its node_modules):  cd web && npx vite --config ../prototypes/vite.config.mjs
// Data: the export in data/out (tiles, profiles) is served as public directory, nothing is copied.
// No import of "vite" here, so the config also loads from outside web/.
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const nm = (p) => resolve(here, "../web/node_modules", p);

export default {
  root: here,
  base: "./",
  publicDir: resolve(here, "../data/out"),
  cacheDir: nm(".vite-prototypes"),
  resolve: {
    alias: {
      "maplibre-gl": nm("maplibre-gl"),
      pmtiles: nm("pmtiles"),
      "@protomaps/basemaps": nm("@protomaps/basemaps"),
    },
  },
  optimizeDeps: { exclude: ["maplibre-gl"] }, // keeps the ?url worker import a plain URL in dev mode
  server: { port: 5180, strictPort: true, fs: { allow: [resolve(here, "..")] } },
  preview: { port: 5180, strictPort: true },
};
