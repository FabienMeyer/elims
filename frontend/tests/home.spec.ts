import { expect, test } from "@playwright/test"

test.describe("Home Page", () => {
  test("should display welcome message", async ({ page }) => {
    await page.goto("/")

    // Check for welcome heading
    await expect(page.getByRole("heading", { name: /Welcome to ELIMS/i })).toBeVisible()

    // Check for subtitle
    await expect(page.getByText(/Lab Instrument Management System/i)).toBeVisible()
  })

  test("should show backend connection status", async ({ page }) => {
    await page.goto("/")

    // Check for backend status section
    await expect(page.getByRole("heading", { name: /Backend Status/i })).toBeVisible()

    // Wait for connection check to complete
    await page.waitForTimeout(2000)

    // Should show either connected or error state
    const statusText = await page.locator("text=/Connected|Cannot connect/i").textContent()
    expect(statusText).toBeTruthy()
  })

  test("should have proper page title", async ({ page }) => {
    await page.goto("/")

    // Check page title
    await expect(page).toHaveTitle(/ELIMS/)
  })
})
