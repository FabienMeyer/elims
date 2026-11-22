# Backend security

The backend container runs without additional Linux capabilities, uses a read-only filesystem, and exposes its development port only on loopback by default.

New endpoints must document authentication, authorization, validation, sensitive-data handling, audit requirements, and abuse cases. Secrets must come from runtime configuration and must never enter the repository or generated evidence.
