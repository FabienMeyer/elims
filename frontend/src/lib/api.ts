import type { z } from "zod"
import { env } from "@/app/env"

export async function apiGet<T>(
  path: string,
  schema: z.ZodType<T>,
): Promise<T> {
  const response = await fetch(`${env.VITE_API_URL}${path}`)
  if (!response.ok) throw new Error(`API request failed: ${response.status}`)
  return schema.parse(await response.json())
}
