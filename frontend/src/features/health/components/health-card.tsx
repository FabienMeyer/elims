import { Card } from "@/components/ui/card"
import { useHealthQuery } from "@/features/health/api/use-health-query"
import { ApiContractError } from "@/lib/api"

export function HealthCard() {
  const query = useHealthQuery()
  return (
    <Card>
      <h2>Backend</h2>
      {/* One live region that stays mounted, so each change is announced. */}
      <p role="status">{healthMessage(query)}</p>
    </Card>
  )
}

function healthMessage(query: ReturnType<typeof useHealthQuery>): string {
  if (query.status === "pending") return "Connecting…"
  // A failed refetch keeps the old data; the latest check is what counts.
  if (query.status === "error") {
    return query.error instanceof ApiContractError
      ? "Unexpected API response"
      : "API unavailable"
  }
  return `API ${query.data.status}`
}
