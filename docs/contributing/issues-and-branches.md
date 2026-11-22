# Issue, label, and branch conventions

Use these conventions for all ELIMS work. The conventions make component
ownership visible without duplicating workflow state across issue titles,
labels, branches, and the GitHub Project.

## Issue titles

Use this format for implementation issues:

```text
[scope] Imperative outcome
```

Use one primary scope in the title. Add labels for other affected areas.
Describe an observable outcome, not an implementation step. Do not include
priority, status, assignee, or iteration in the title. Keep titles near 80
characters or fewer when practical.

Examples:

```text
[frontend] Show validation errors on the item form
[backend] Reject duplicate instrument identifiers
[database] Add instrument calibration records
[cli] Export instrument configurations
[instruments] Add balance connection protocol
[infra] Add backend readiness monitoring
[ci] Run migration checks in CI
```

Use `[tracking]` for parent issues that contain no implementation work.

Canonical scopes are `frontend`, `backend`, `database`, `cli`, `com`,
`instruments`, `utils`, `docs`, `infra`, `ci`, `repository`, and `tracking`.
Use `repository` only for genuinely repository-wide work.

## Labels

Assign exactly one type label:

```text
type:feature
type:bug
type:refactor
type:maintenance
type:documentation
type:security
type:performance
type:migration
type:tracking
```

Assign one or more precise area labels:

```text
area:frontend
area:backend
area:database
area:cli
area:com
area:instruments
area:utils
area:documentation
area:infrastructure
area:ci
area:repository
```

Assign exactly one risk label to each implementation leaf:

```text
risk:low
risk:medium
risk:high
risk:critical
```

- `risk:low`: isolated and easy to reverse.
- `risk:medium`: normal application behavior with contained consequences.
- `risk:high`: authentication, migration, compatibility, sensitive-data, or
  operational risk.
- `risk:critical`: plausible data loss, security exposure, or system-wide
  outage.

Add impact labels only when applicable:

```text
impact:breaking
impact:migration
impact:security
impact:privacy
impact:accessibility
impact:operations
impact:documentation
```

Keep the exact `rdy-to-implement` label as the implementation authorization
gate. Apply it only to an approved implementation leaf after independent issue
review and explicit human approval. Use `blocked` or `needs-decision` only for
exceptional states.

The GitHub Project `Status` field is the source of truth for normal workflow
state. Do not duplicate its values as labels.

## Branch names

Create one branch per approved implementation leaf:

```text
<type>/<issue-number>-<scope>-<short-slug>
```

Allowed branch types are `feat`, `fix`, `refactor`, `docs`, `test`, `chore`,
`security`, `perf`, and `migration`.

Examples:

```text
feat/142-frontend-item-validation
fix/157-backend-duplicate-instrument-id
migration/163-database-calibration-records
security/184-backend-session-validation
chore/201-ci-migration-checks
```

Use the GitHub issue number and the primary issue scope. Use lowercase ASCII
letters, numbers, and hyphens. Keep the slug to approximately two to five
words and the complete name below 60 characters when practical. Do not create
branches for tracking issues.

Work without an issue must be exceptional. When authorized, use
`chore/no-issue-<short-slug>`.

## Pull-request titles

Use a Conventional Commit title. The scope identifies the primary affected
area and the description states the outcome:

```text
feat(frontend): show validation errors on the item form
fix(backend): reject duplicate instrument identifiers
docs(infra): document GHCR authentication
```

Allowed types are `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`,
`ci`, `chore`, and `revert`. Allowed scopes are `frontend`, `backend`,
`database`, `cli`, `com`, `instruments`, `utils`, `docs`, `infra`, `ci`,
`repository`, `release`, `deps`, `deps-dev`, `security`, and `docker`.

Add `!` before the colon for a breaking change, for example
`feat(backend)!: replace the sample response schema`. Link the pull request to
its approved leaf issue in the body and do not use a tracking issue as the
implementation target. Squash merging preserves the validated pull-request
title as the commit Release Please reads from `main`.
