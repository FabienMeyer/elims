import type { PropsWithChildren } from "react"

export function AppShell({ children }: PropsWithChildren) {
  return (
    <div className="shell">
      <header className="shell-header">
        <a href="/" className="brand">
          ELIMS
        </a>
      </header>
      <main className="shell-main">{children}</main>
    </div>
  )
}
