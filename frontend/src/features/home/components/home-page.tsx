import { HealthCard } from "@/features/health/components/health-card"

export function HomePage() {
  return (
    <div className="stack">
      <div>
        <h1>ELIMS</h1>
        {/* From docs/product/vision.md; change it there first. */}
        <p>A dependable foundation for laboratory information workflows.</p>
      </div>
      <HealthCard />
    </div>
  )
}
