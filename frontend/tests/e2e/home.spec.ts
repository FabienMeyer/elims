import { expect, test } from "@playwright/test"

test("shows the ELIMS home page in English", async ({ page }) => {
  await page.route("**/api/health", (route) =>
    route.fulfill({ json: { status: "healthy" } }),
  )
  await page.goto("/")
  await expect(page).toHaveTitle("ELIMS")
  await expect(page.locator("html")).toHaveAttribute("lang", "en")
  await expect(
    page.getByRole("heading", { level: 1, name: "ELIMS" }),
  ).toBeVisible()
  await expect(
    page.getByText(
      "A dependable foundation for laboratory information workflows.",
    ),
  ).toBeVisible()
  await expect(page.getByText("API healthy")).toBeVisible()
})
