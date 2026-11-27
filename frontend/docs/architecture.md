# Frontend architecture

```text
app -> providers and environment
features -> APIs, hooks, and domain components
components/layout -> persistent application shell
components/ui -> primitives without domain logic
lib -> technical adapters
tests/unit -> Vitest and Testing Library
tests/e2e -> Playwright
```

UI components do not communicate with the backend directly. Server calls live behind feature boundaries and use TanStack Query for server state.

`apiGet` in `src/lib/api.ts` validates every response against a Zod schema. It raises `ApiContractError` when a response is not JSON or does not match its schema, so features can tell a contract break from an unavailable API. Any other failure, such as a network error or an unsuccessful HTTP status, is a plain `Error`.

No routing or styling library is adopted yet. When a feature first needs one, choose it through `/architecture-shaper` and record it in the [frontend decisions](decisions/index.md).
