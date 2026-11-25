import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// /bank/* → credit-risk API (README: uvicorn api.main:app --port 8000)
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5173, proxy: { "/bank": process.env.API_URL ?? "http://127.0.0.1:8000" } },
});
