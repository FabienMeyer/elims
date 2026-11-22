import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen } from "@testing-library/react"
import { HttpResponse, http } from "msw"
import { setupServer } from "msw/node"
import { afterAll, afterEach, beforeAll, expect, it } from "vitest"
import { HealthCard } from "@/features/health/components/health-card"

const server = setupServer()
beforeAll(() => server.listen({ onUnhandledRequest: "error" }))
afterEach(() => {
  cleanup()
  server.resetHandlers()
})
afterAll(() => server.close())

function renderHealth() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  render(
    <QueryClientProvider client={client}>
      <HealthCard />
    </QueryClientProvider>,
  )
}

it("displays a successful backend response", async () => {
  server.use(
    http.get("*/api/health", () => HttpResponse.json({ status: "healthy" })),
  )
  renderHealth()
  expect(await screen.findByText("API healthy")).toBeInTheDocument()
})

it("displays a failed backend response", async () => {
  server.use(
    http.get("*/api/health", () => new HttpResponse(null, { status: 503 })),
  )
  renderHealth()
  expect(await screen.findByRole("alert")).toHaveTextContent("API unavailable")
})

it("rejects a response that violates the API contract", async () => {
  server.use(http.get("*/api/health", () => HttpResponse.json({ status: 42 })))
  renderHealth()
  expect(await screen.findByRole("alert")).toHaveTextContent("API unavailable")
})
