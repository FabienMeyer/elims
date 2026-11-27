# Backend security

The backend container runs without additional Linux capabilities, uses a read-only filesystem, and exposes its development port only on loopback by default.

The backend trusts forwarded headers from any address in the Compose stacks because only the frontend proxy can reach it there. Keep the backend unreachable from clients wherever `FORWARDED_ALLOW_IPS` is `*`; see [configuration](configuration.md#proxy-headers).

New endpoints must document authentication, authorization, validation, sensitive-data handling, audit requirements, and abuse cases. Secrets must come from runtime configuration and must never enter the repository or generated evidence.
