import { expect, it } from "vitest"
import { z } from "zod"
import "@/app/zod-config"

it("turns off the Zod fast path that the Content-Security-Policy blocks", () => {
  expect(z.config().jitless).toBe(true)
})
