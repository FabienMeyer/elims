import type { z } from "zod"
import { env } from "@/app/env"

/** How long a request may take, including reading its body. */
const REQUEST_TIMEOUT_MS = 10_000

/** The API answered, but not with a response that matches its contract. */
export class ApiContractError extends Error {
  override name = "ApiContractError"
}

interface RequestOptions {
  /** Cancels the request, for example the signal TanStack Query provides. */
  signal?: AbortSignal
  timeoutMs?: number
}

export async function apiGet<T>(
  path: string,
  schema: z.ZodType<T>,
  { signal, timeoutMs = REQUEST_TIMEOUT_MS }: RequestOptions = {},
): Promise<T> {
  const timeout = AbortSignal.timeout(timeoutMs)
  const response = await fetch(`${env.VITE_API_URL}${path}`, {
    headers: { Accept: "application/json" },
    signal: signal ? AbortSignal.any([signal, timeout]) : timeout,
  })
  if (!response.ok) throw new Error(`API request failed: ${response.status}`)
  const body: unknown = await response.json().catch((cause: unknown) => {
    // An abort or timeout while the body is read is not a contract break.
    if (!(cause instanceof SyntaxError)) throw cause
    throw new ApiContractError(`Response from ${path} is not JSON`, { cause })
  })
  const result = schema.safeParse(body)
  if (!result.success) {
    throw new ApiContractError(`Response from ${path} breaks its contract`, {
      cause: result.error,
    })
  }
  return result.data
}
