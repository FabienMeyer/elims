import AxeBuilder from "@axe-core/playwright"
import { expect, test } from "@playwright/test"

test("home page has no automatically detectable accessibility violations", async ({
  page,
}) => {
  await page.route("**/api/health", (route) =>
    route.fulfill({ json: { status: "healthy" } }),
  )
  await page.goto("/")
  await expect(page.getByText("API healthy")).toBeVisible()
  const results = await new AxeBuilder({ page }).analyze()
  expect(results.violations).toEqual([])
})
