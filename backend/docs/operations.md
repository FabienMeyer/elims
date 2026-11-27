# Backend operations

The backend exposes liveness, readiness, and metrics endpoints used by Docker health checks and Prometheus. Database migrations complete before the backend starts in the Compose stack.

Operational changes must document deployment order, migration behavior, monitoring signals, failure modes, and recovery steps.

## Readiness

`/ready`, also served as `/api/ready` through the frontend proxy, returns `200` only when the database is reachable and records exactly the migration revisions shipped in the running image. It does not query application tables. It returns `503` with `Database is not ready` when the database is unreachable, has not been migrated, is behind the image, or was migrated by a newer release.

The last case affects rollbacks: an older image stays unready against a database that a newer release migrated. Recover by redeploying the newer image, or by downgrading the database to the older image's revision after reviewing the downgrade for data loss.
