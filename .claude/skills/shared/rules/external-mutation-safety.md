# External mutation safety

External state mutations require an exact target, a complete planned operation,
and explicit authorization for that operation.

- Inspect current state and use a dry run when supported.
- Report the target and complete intended operation list before applying it.
- Apply only the authorized operations to the authorized target.
- Obtain credentials from the approved credential provider or environment. Never
  put credentials in arguments, tracked files, logs, or generated evidence.
- Verify resulting state through a read-only query.
- If only part of an operation succeeds, stop and report completed and remaining
  operations. Do not retry creation or another non-idempotent mutation blindly.
- Do not infer authorization for related mutations, retries, cleanup, merge,
  deployment, closure, or deletion.

The responsible skill retains its operation-specific permissions, prohibitions,
idempotency keys, and stopping conditions.
