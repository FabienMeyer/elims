import { readFileSync } from "node:fs"
import path from "node:path"
import react from "@vitejs/plugin-react-swc"
import { defineConfig } from "vitest/config"

// Nginx owns the production Content-Security-Policy. The preview server reuses
// it so end-to-end tests fail when the bundle needs something it forbids.
const nginxConfig = readFileSync(path.resolve(__dirname, "nginx.conf"), "utf8")
const contentSecurityPolicy =
  /add_header Content-Security-Policy "([^"]+)"/.exec(nginxConfig)?.[1]
if (!contentSecurityPolicy) {
  throw new Error("nginx.conf must define a Content-Security-Policy header")
}

export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
  preview: { headers: { "Content-Security-Policy": contentSecurityPolicy } },
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    include: ["./tests/unit/**/*.test.{ts,tsx}"],
    unstubGlobals: true,
    coverage: {
      reporter: ["text", "html", "lcov"],
      include: ["src/lib/**", "src/features/**"],
    },
  },
})
