import type { PropsWithChildren } from "react"

export function AppShell({ children }: PropsWithChildren) {
  return (
    <div className="shell">
      <header>
        <a href="/" className="brand">
          Full-stack Template
        </a>
      </header>
      <main>{children}</main>
      <footer>Minimal architecture, ready to extend.</footer>
    </div>
  )
}
