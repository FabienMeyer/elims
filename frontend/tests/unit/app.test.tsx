import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"

import { App } from "@/App"

describe("App", () => {
  it("renders the ELIMS shell and home page", () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => new Promise(() => undefined)),
    )
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    render(
      <QueryClientProvider client={client}>
        <App />
      </QueryClientProvider>,
    )
    expect(screen.getByRole("link", { name: "ELIMS" })).toHaveAttribute(
      "href",
      "/",
    )
    expect(
      screen.getByRole("heading", { level: 1, name: "ELIMS" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        "A dependable foundation for laboratory information workflows.",
      ),
    ).toBeInTheDocument()
    expect(screen.queryByRole("contentinfo")).not.toBeInTheDocument()
  })
})
