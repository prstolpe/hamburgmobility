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
  build: { outDir: "dist", emptyOutDir: true, chunkSizeWarningLimit: 1500 },
  plugins: [ogImage],
  test: { include: ["test/**/*.test.js"] },
});
