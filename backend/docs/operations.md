# Backend operations

The backend exposes liveness, readiness, and metrics endpoints used by Docker health checks and Prometheus. Database migrations complete before the backend starts in the Compose stack.

Operational changes must document deployment order, migration behavior, monitoring signals, failure modes, and recovery steps.
