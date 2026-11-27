import { expect, test } from "@playwright/test"

test("home page runs under the production Content-Security-Policy", async ({
  page,
}) => {
  const problems: string[] = []
  page.on("console", (message) => {
    if (message.type() === "error") problems.push(message.text())
  })
  page.on("pageerror", (error) => problems.push(error.message))
  await page.route("**/api/health", (route) =>
    route.fulfill({ json: { status: "healthy" } }),
  )

  const response = await page.goto("/")

  expect(response?.headers()["content-security-policy"]).toContain(
    "default-src 'self'",
  )
  await expect(page.getByText("API healthy")).toBeVisible()
  expect(problems).toEqual([])
})
