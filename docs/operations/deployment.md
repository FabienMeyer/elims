# Deployment and recovery

Docker Compose defines the local and production-oriented service topology. Deployments must account for database migration order, application readiness, observability, rollback constraints, and data recovery.

The frontend image sets its own caching, compression, and Content-Security-Policy. See [frontend configuration](../components/frontend/configuration.md) before changing the Nginx or Traefik headers.

Release-specific instructions belong in an approved specification and its implementation evidence.
