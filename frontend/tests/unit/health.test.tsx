import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { act, render, screen, waitFor } from "@testing-library/react"
import { HttpResponse, http } from "msw"
import { setupServer } from "msw/node"
import { afterAll, afterEach, beforeAll, expect, it } from "vitest"
import { HealthCard } from "@/features/health/components/health-card"

const server = setupServer()
beforeAll(() => server.listen({ onUnhandledFrame: "error" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const healthy = http.get("*/api/health", () =>
  HttpResponse.json({ status: "healthy" }),
)
const unavailable = http.get(
  "*/api/health",
  () => new HttpResponse(null, { status: 503 }),
)

function renderHealth() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  render(
    <QueryClientProvider client={client}>
      <HealthCard />
    </QueryClientProvider>,
  )
  return client
}

async function expectStatus(text: string) {
  await waitFor(() =>
    expect(screen.getByRole("status")).toHaveTextContent(text),
  )
}

it("displays a successful backend response", async () => {
  server.use(healthy)
  renderHealth()
  await expectStatus("API healthy")
})

it("displays a failed backend response", async () => {
  server.use(unavailable)
  renderHealth()
  await expectStatus("API unavailable")
})

it("distinguishes a response that violates the API contract", async () => {
  server.use(http.get("*/api/health", () => HttpResponse.json({ status: 42 })))
  renderHealth()
  await expectStatus("Unexpected API response")
})

it("treats a response that is not JSON as a contract violation", async () => {
  server.use(
    http.get("*/api/health", () => HttpResponse.html("<!doctype html>")),
  )
  renderHealth()
  await expectStatus("Unexpected API response")
})

it("announces every state change through one live region", async () => {
  server.use(healthy)
  renderHealth()
  const status = screen.getByRole("status")
  expect(status).toHaveTextContent("Connecting…")
  await waitFor(() => expect(status).toHaveTextContent("API healthy"))
  expect(screen.getAllByRole("status")).toHaveLength(1)
})

it("reports a failed refetch instead of the earlier success", async () => {
  server.use(healthy)
  const client = renderHealth()
  await expectStatus("API healthy")

  server.use(unavailable)
  await act(() => client.refetchQueries())

  await expectStatus("API unavailable")
  expect(screen.queryByText("API healthy")).not.toBeInTheDocument()
})
