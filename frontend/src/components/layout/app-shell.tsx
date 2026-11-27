import type { PropsWithChildren } from "react"

export function AppShell({ children }: PropsWithChildren) {
  return (
    <div className="shell">
      <header>
        <a href="/" className="brand">
          ELIMS
        </a>
      </header>
      <main>{children}</main>
    </div>
  )
}
