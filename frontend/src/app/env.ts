import { z } from "zod"

export const env = z
  .object({ VITE_API_URL: z.literal("/api").default("/api") })
  .parse(import.meta.env)
