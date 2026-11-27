// Must stay first: it configures Zod before any module builds a schema.
import "@/app/zod-config"
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"

import { App } from "@/App"
import { AppProviders } from "@/app/providers/app-providers"
import "@/styles.css"

const rootElement = document.getElementById("root")
if (!rootElement) throw new Error("Root element not found")

createRoot(rootElement).render(
  <StrictMode>
    <AppProviders>
      <App />
    </AppProviders>
  </StrictMode>,
)
