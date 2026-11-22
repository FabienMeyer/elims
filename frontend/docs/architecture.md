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
