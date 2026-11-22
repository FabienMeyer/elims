import { useQuery } from "@tanstack/react-query"
import { z } from "zod"

import { apiGet } from "@/lib/api"

const healthSchema = z.object({ status: z.literal("healthy") })

export function useHealthQuery() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => apiGet("/health", healthSchema),
  })
}
