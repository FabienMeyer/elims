import { Card } from "@/components/ui/card"
import { useHealthQuery } from "@/features/health/api/use-health-query"

export function HealthCard() {
  const query = useHealthQuery()
  return (
    <Card>
      <h2>Backend</h2>
      {query.isPending && <p role="status">Connecting…</p>}
      {query.isError && <p role="alert">API unavailable</p>}
      {query.data && <p role="status">API {query.data.status}</p>}
    </Card>
  )
}
