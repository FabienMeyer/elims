import { expect, test } from "@playwright/test"

test("shows the template home page", async ({ page }) => {
  await page.route("**/api/health", (route) =>
    route.fulfill({ json: { status: "healthy" } }),
  )
  await page.goto("/")
  await expect(
    page.getByRole("heading", { name: "Base full-stack" }),
  ).toBeVisible()
  await expect(page.getByText("API healthy")).toBeVisible()
  await expect(
    page.getByText("React, TypeScript, FastAPI, and MariaDB."),
  ).toBeVisible()
})
