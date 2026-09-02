import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },

  server: {
    proxy: {
      "/api": {
        target: "http://recommendation-service:8000",
        changeOrigin: true,
        rewrite: (path) => path,
      },
      "/health": {
        target: "http://recommendation-service:8000",
        changeOrigin: true,
      },
    },
  },
});