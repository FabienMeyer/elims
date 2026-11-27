import { delay, HttpResponse, http } from "msw"
import { setupServer } from "msw/node"
import { afterAll, afterEach, beforeAll, expect, it, vi } from "vitest"
import { z } from "zod"

import { apiGet } from "@/lib/api"

const server = setupServer()
beforeAll(() => server.listen({ onUnhandledFrame: "error" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

const schema = z.object({ status: z.literal("healthy") })
const neverAnswers = http.get("*/api/health", async () => {
  await delay("infinite")
  return HttpResponse.json({ status: "healthy" })
})

it("asks the API for JSON", async () => {
  server.use(
    http.get("*/api/health", ({ request }) =>
      request.headers.get("Accept") === "application/json"
        ? HttpResponse.json({ status: "healthy" })
        : new HttpResponse(null, { status: 406 }),
    ),
  )
  await expect(apiGet("/health", schema)).resolves.toEqual({
    status: "healthy",
  })
})

it("cancels the request when the caller aborts", async () => {
  server.use(neverAnswers)
  const controller = new AbortController()
  const request = apiGet("/health", schema, { signal: controller.signal })
  controller.abort()
  await expect(request).rejects.toMatchObject({ name: "AbortError" })
})

it("reports a timeout while reading the body as a timeout", async () => {
  // Stubbed: aborting a streamed MSW body trips an undici assertion in Node.
  const timedOut = new DOMException("The operation timed out.", "TimeoutError")
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => ({ ok: true, json: () => Promise.reject(timedOut) })),
  )
  await expect(apiGet("/health", schema)).rejects.toBe(timedOut)
})

it("gives up when the API does not answer in time", async () => {
  server.use(neverAnswers)
  await expect(
    apiGet("/health", schema, { timeoutMs: 20 }),
  ).rejects.toMatchObject({ name: "TimeoutError" })
})
