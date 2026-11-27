# ELIMS project instructions

## Repository

ELIMS is a full-stack monorepo. `backend/` contains the FastAPI application
and Alembic migrations. `frontend/` contains the React and TypeScript
application. `packages/` contains independently buildable Python packages.
`docs/` contains aggregate documentation, and `config/` contains deployment
and observability configuration.

Use Python 3.13, uv 0.13.7, and Node.js 24. Run commands from the repository
root unless the command reference says otherwise. Treat
`docs/operations/command-reference.md` and GitHub Actions as the authoritative
sources for commands and required checks.

## Software factory

Use the delivery skills in `.claude/skills/` for product changes. Start a new
or materially changed product behavior with `/idea-shaper`. Follow the skill
handoffs and approval gates in order. Do not bypass human approval, independent
review, issue-label, verification, documentation, or acceptance gates.

Do not infer `rdy-to-implement`, add it, or begin Chapter 5 implementation
without the evidence required by the implementation skill. Do not mutate
GitHub issues, Projects, pull requests, branches, or releases unless the user
explicitly authorizes that mutation. Inspect or dry-run first when a bundled
script supports it.

Follow `docs/contributing/issues-and-branches.md` for issue, label, branch, and
pull-request conventions. Keep product requirements, behavioral
specifications, architecture decisions, implementation, verification,
documentation, and human acceptance as separate evidence.

Shared delivery rules are authoritative only for the roles they name. Every
delivery role must read and apply `.claude/skills/shared/rules/evidence-quality.md`
and `.claude/skills/shared/rules/context-reporting.md`. Every orchestrator and
role whose work spans a fresh-context handoff must also apply
`.claude/skills/shared/rules/context-resilience.md`. A role that verifies human
approval must also apply
`.claude/skills/shared/rules/approval-evidence.md`; an independent reviewer,
verifier, or validator must apply
`.claude/skills/shared/rules/independent-evaluation.md`; and a role that can
mutate external state must apply
`.claude/skills/shared/rules/external-mutation-safety.md`. Keep each skill's
entry gates, workflow, verdicts, and correction routing local.

When creating or refactoring skills, apply
`.claude/skills/shared/rules/skill-system-design.md`: centralize
identity-critical standards whose independent interpretation could make stages
disagree, and keep role behavior and contextual judgment local.

## Engineering rules

- Preserve unrelated work in a dirty worktree.
- Do not guess. Calculate deterministic claims and evaluate empirical claims
  from evidence. State uncertainty, assumptions, and the method needed to
  resolve incomplete evidence.
- Make the smallest cohesive change that satisfies approved behavior.
- Use TDD when the applicable implementation skill requires it.
- Keep FastAPI routes thin and put use-case behavior in services or domain
  packages. Alembic owns database schema changes.
- Keep credentials, tokens, private request data, and production secrets out of
  source control, logs, tests, and generated evidence.
- Keep production business routes fail-closed until authentication and
  authorization are configured and verified.
- Document behavior, configuration, migration, security, privacy, and
  operational effects when a change introduces them.

## Verification

Run focused checks while developing and proportionate regression checks before
reporting completion. The core Python checks are:

```powershell
uv run ruff check backend packages scripts docs/hooks.py .claude/skills
uv run ruff format --check backend packages scripts docs/hooks.py .claude/skills
uv run mypy backend/app packages/elims-cli/src packages/elims-utils/src packages/elims-com/src packages/elims-database/src packages/elims-instruments/src
uv run pytest --cov --cov-report=term-missing
```

For frontend changes, run the applicable npm lint, test, build, and Playwright
commands from `docs/operations/command-reference.md`. Run strict MkDocs builds
for documentation changes. Use the Docker stack or relevant integration job
when behavior depends on MariaDB, Nginx, Traefik, or another service boundary.

Report exact commands, results, skipped checks, environmental limitations, and
residual risks. Never claim human acceptance, deployment, or merge completion
without explicit evidence.
