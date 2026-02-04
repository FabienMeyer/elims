import { useMemo, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/temperatures")({
  component: TemperaturesView,
  head: () => ({
    meta: [
      {
        title: "Temperature Graph",
      },
    ],
  }),
})

type TemperatureItem = {
  id: number
  device_id: string
  temperature: number
  timestamp: string
}

function TemperaturesView() {
  const [selectedDevice, setSelectedDevice] = useState<string | "all">("all")

  const { data, isLoading, isError } = useQuery({
    queryKey: ["temperatures"],
    queryFn: async () => {
      const response = await fetch("/api/v1/temperatures")
      if (!response.ok) {
        throw new Error("Failed to load temperatures")
      }
      return (await response.json()) as TemperatureItem[]
    },
  })

  const devices = useMemo(() => {
    if (!data) {
      return []
    }
    return Array.from(new Set(data.map((item) => item.device_id))).sort()
  }, [data])

  const filtered = useMemo(() => {
    if (!data) {
      return []
    }
    const rows = selectedDevice === "all" ? data : data.filter((item) => item.device_id === selectedDevice)
    return [...rows].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
  }, [data, selectedDevice])

  const stats = useMemo(() => {
    if (filtered.length === 0) {
      return { latest: null, min: null, max: null }
    }
    const temps = filtered.map((item) => item.temperature)
    const latest = filtered[filtered.length - 1]
    return {
      latest,
      min: Math.min(...temps),
      max: Math.max(...temps),
    }
  }, [filtered])

  const chart = useMemo(() => {
    if (filtered.length === 0) {
      return null
    }

    const width = 1000
    const height = 320
    const padding = { top: 24, right: 24, bottom: 36, left: 48 }

    const times = filtered.map((item) => new Date(item.timestamp).getTime())
    const temps = filtered.map((item) => item.temperature)

    const minX = Math.min(...times)
    const maxX = Math.max(...times)
    const minY = Math.min(...temps)
    const maxY = Math.max(...temps)

    const xRange = maxX - minX || 1
    const yRange = maxY - minY || 1

    const points = filtered.map((item) => {
      const x = ((new Date(item.timestamp).getTime() - minX) / xRange) * (width - padding.left - padding.right) + padding.left
      const y = height - padding.bottom - ((item.temperature - minY) / yRange) * (height - padding.top - padding.bottom)
      return { x, y, item }
    })

    const path = points
      .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`)
      .join(" ")

    return { width, height, padding, points, path, minY, maxY }
  }, [filtered])

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-slate-500">Telemetry</p>
          <h1 className="text-3xl font-semibold text-slate-900">Temperature Timeline</h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-600">
            Live history of sensor readings over time. Filter by device and inspect the latest data points.
          </p>
        </div>
        <Link
          to="/"
          className="inline-flex items-center justify-center rounded-full border border-slate-200 px-4 py-2 text-sm text-slate-600 transition hover:border-slate-400 hover:text-slate-900"
        >
          Back to dashboard
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-white/70 p-4 shadow-sm">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Latest</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {stats.latest ? `${stats.latest.temperature.toFixed(1)} deg C` : "--"}
          </p>
          <p className="text-xs text-slate-500">
            {stats.latest ? new Date(stats.latest.timestamp).toLocaleString() : "No data"}
          </p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white/70 p-4 shadow-sm">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Range</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {stats.min !== null && stats.max !== null ? `${stats.min.toFixed(1)} deg C → ${stats.max.toFixed(1)} deg C` : "--"}
          </p>
          <p className="text-xs text-slate-500">Last {filtered.length} records</p>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white/70 p-4 shadow-sm">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Devices</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">{devices.length || "--"}</p>
          <p className="text-xs text-slate-500">Reporting sensors</p>
        </div>
      </div>

      <div className="rounded-[32px] border border-slate-200 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.2),_transparent_60%),_radial-gradient(circle_at_bottom,_rgba(14,116,144,0.25),_transparent_55%)] p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Temperature chart</p>
            <h2 className="text-xl font-semibold text-slate-900">Readings over time</h2>
          </div>
          <label className="flex items-center gap-2 text-sm text-slate-600">
            Device
            <select
              className="rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-sm text-slate-700 shadow-sm"
              value={selectedDevice}
              onChange={(event) => setSelectedDevice(event.target.value as "all" | string)}
            >
              <option value="all">All devices</option>
              {devices.map((device) => (
                <option key={device} value={device}>
                  {device}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="mt-6 rounded-2xl bg-white/80 p-4 shadow-sm">
          {isLoading && <p className="text-sm text-slate-500">Loading temperature data...</p>}
          {isError && <p className="text-sm text-rose-600">Unable to load temperature data.</p>}
          {!isLoading && !isError && filtered.length === 0 && (
            <p className="text-sm text-slate-500">No data available for the selected device.</p>
          )}
          {!isLoading && !isError && chart && (
            <div className="w-full overflow-x-auto">
              <svg
                viewBox={`0 0 ${chart.width} ${chart.height}`}
                className="h-[320px] w-full"
                role="img"
                aria-label="Temperature timeline"
              >
                <defs>
                  <linearGradient id="tempLine" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#0ea5e9" />
                    <stop offset="100%" stopColor="#14b8a6" />
                  </linearGradient>
                </defs>

                <rect x="0" y="0" width={chart.width} height={chart.height} fill="transparent" />

                <path d={chart.path} fill="none" stroke="url(#tempLine)" strokeWidth="3" />

                {chart.points.map((point) => (
                  <circle key={point.item.id} cx={point.x} cy={point.y} r="4" fill="#0f172a" />
                ))}

                <text x={chart.padding.left} y={chart.padding.top} fill="#64748b" fontSize="12">
                  {chart.maxY.toFixed(1)} deg C
                </text>
                <text x={chart.padding.left} y={chart.height - chart.padding.bottom + 20} fill="#64748b" fontSize="12">
                  {chart.minY.toFixed(1)} deg C
                </text>
              </svg>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
