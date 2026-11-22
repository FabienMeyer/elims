# Backend vision

The backend provides a stable, secure, observable boundary around ELIMS domain capabilities and persistence.

## Responsibilities

- Validate and serve HTTP contracts.
- Coordinate domain and persistence operations.
- Apply explicit, reviewable schema migrations.
- Expose meaningful readiness and operational signals.

## Non-goals

- Rendering the browser interface
- Hiding domain behavior inside transport handlers
- Introducing undocumented persistence side effects
