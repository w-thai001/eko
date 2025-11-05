import { defineConfig } from "vite";
import webExtension from "vite-plugin-web-extension";

export default defineConfig({
  plugins: [
    webExtension({
      manifest: "./manifest.json",
      browser: "chrome",
    }),
  ],
  build: {
    outDir: "dist",
    rollupOptions: {
      input: {
        background: "src/background/index.ts",
        popup: "src/popup/popup.html",
        options: "src/options/options.html",
        content: "src/content/index.ts",
      },
    },
  },
});
