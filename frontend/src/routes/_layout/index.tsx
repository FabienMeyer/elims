import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
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
    </div>
  )
}
