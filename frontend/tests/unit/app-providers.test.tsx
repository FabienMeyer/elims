import { useQueryClient } from "@tanstack/react-query"
import { render, screen } from "@testing-library/react"
import { expect, it } from "vitest"

import { AppProviders } from "@/app/providers/app-providers"

function QueryDefaults() {
  const queries = useQueryClient().getDefaultOptions().queries
  return (
    <p>{`retry ${queries?.retry}, stale ${queries?.staleTime}ms, refetch on focus ${queries?.refetchOnWindowFocus}`}</p>
  )
}

it("provides the application query client and its defaults", () => {
  render(
    <AppProviders>
      <QueryDefaults />
    </AppProviders>,
  )
  expect(
    screen.getByText("retry 1, stale 30000ms, refetch on focus false"),
  ).toBeInTheDocument()
})
