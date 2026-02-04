import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { client } from "@/client"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "Home Page",
      },
    ],
  }),
})

function Dashboard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const response = await client.GET("/health")
      return response.data
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold truncate max-w-sm">
          Welcome to ELIMS 👋
        </h1>
        <p className="text-muted-foreground">
          Lab Instrument Management System
        </p>
      </div>

      <div className="border rounded-lg p-4">
        <h2 className="text-lg font-semibold mb-2">Backend Status</h2>
        {isLoading && <p className="text-muted-foreground">Checking connection...</p>}
        {isError && (
          <div className="text-red-500">
            ❌ Cannot connect to backend
          </div>
        )}
        {data && (
          <div className="text-green-600">
            ✅ Connected - Status: {JSON.stringify(data)}
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
        <h2 className="text-lg font-semibold text-slate-900">Temperature Graph</h2>
        <p className="mt-2 text-sm text-slate-600">
          Explore sensor readings over time with a dedicated timeline view.
        </p>
        <div className="mt-4">
          <Link
            to="/temperatures"
            className="inline-flex items-center rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
          >
            Open temperature view
          </Link>
        </div>
      </div>
    </div>
  )
}
