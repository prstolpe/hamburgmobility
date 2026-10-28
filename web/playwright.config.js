import { defineConfig, devices } from "@playwright/test";

// Runs against `vite preview` (built site incl. data/out). `npm run build` first.
export default defineConfig({
  testDir: "e2e",
  timeout: 60_000,
  workers: 1,
  reporter: [["list"]],
  use: { baseURL: "http://localhost:4173/" },
  webServer: { command: "npm run preview", url: "http://localhost:4173/", reuseExistingServer: true, timeout: 60_000 },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
});
