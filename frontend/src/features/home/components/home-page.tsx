import { HealthCard } from "@/features/health/components/health-card"

export function HomePage() {
  return (
    <div className="stack">
      <div>
        <h1>Base full-stack</h1>
        <p>React, TypeScript, FastAPI, and MariaDB.</p>
      </div>
      <HealthCard />
    </div>
  )
}
