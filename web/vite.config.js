import { readFileSync } from "node:fs";
import { defineConfig } from "vite";

// The site data (data/out from `make export` and `make basemap`) is the public directory: served by
// `vite dev`/`vite preview` (with HTTP Range support for PMTiles) and copied into dist/ by `vite build`.
// SITE_DATA_DIR lets the CI workflow point to the unpacked data release.
// The Open Graph image needs a fixed, unhashed URL: it is emitted as dist/og-image.png.
const ogImage = {
  name: "og-image",
  generateBundle() {
    this.emitFile({ type: "asset", fileName: "og-image.png", source: readFileSync(new URL("./src/brand/og-image.png", import.meta.url)) });
  },
};

export default defineConfig({
  base: "./",
  publicDir: process.env.SITE_DATA_DIR || "../data/out",
  // card.html: image renderer page for tools/render_card (prompt 28), not linked from the site
  build: { outDir: "dist", emptyOutDir: true, chunkSizeWarningLimit: 1500,
    rollupOptions: { input: { main: new URL("./index.html", import.meta.url).pathname, card: new URL("./card.html", import.meta.url).pathname } } },
  plugins: [ogImage],
  test: { include: ["test/**/*.test.js"] },
});
