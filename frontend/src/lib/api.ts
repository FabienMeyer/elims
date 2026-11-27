import type { z } from "zod"
import { env } from "@/app/env"

/** The API answered, but not with a response that matches its contract. */
export class ApiContractError extends Error {
  override name = "ApiContractError"
}

export async function apiGet<T>(
  path: string,
  schema: z.ZodType<T>,
): Promise<T> {
  const response = await fetch(`${env.VITE_API_URL}${path}`)
  if (!response.ok) throw new Error(`API request failed: ${response.status}`)
  const body: unknown = await response.json().catch((cause: unknown) => {
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
