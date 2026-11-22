# Command reference

Run commands from the repository root unless a section says otherwise. The GitHub Actions workflows remain authoritative for required verification.

## Prerequisites

- Python 3.13 or newer
- uv 0.13.7 (the version used in CI)
- Node.js 24 and npm
- Docker with Docker Compose
- Git and GitHub CLI for repository workflows

Install Claude Code to run the repository's delivery skills.

## Claude Code agents

After Claude Code is installed, start it in the repository root:

```powershell
claude
```

Start the Idea Shaper in the conversation:

```text
/idea-shaper <rough idea>
```

The skill asks about the idea and prepares a draft PRD for human review. See the [product definition workflow](../agents/idea-shaper.md) for the approval gates.

## Install dependencies

```powershell
uv sync --locked --all-packages --all-extras --group dev --group docs --group quality
npm ci --prefix frontend
Copy-Item .env.example .env
```

## Python tests

```powershell
# Entire Python workspace
uv run pytest

# Required coverage check
uv run pytest --cov --cov-report=term-missing

# CI coverage artifact
uv run pytest --cov --cov-report=xml --cov-report=term-missing

# Individual components
uv run pytest backend/tests
uv run pytest packages/elims-cli/tests
uv run pytest packages/elims-utils/tests
uv run pytest packages/elims-com/tests
uv run pytest packages/elims-database/tests
uv run pytest packages/elims-instruments/tests

# One file or one test
uv run pytest backend/tests/test_items.py
uv run pytest backend/tests/test_items.py::test_name
```

## Python linting, formatting, and typing

```powershell
uv run ruff check backend packages scripts docs/hooks.py .claude/skills
uv run ruff check --fix backend packages scripts docs/hooks.py .claude/skills
uv run ruff format --check backend packages scripts docs/hooks.py .claude/skills
uv run ruff format backend packages scripts docs/hooks.py .claude/skills

uv run mypy backend/app packages/elims-cli/src packages/elims-utils/src packages/elims-com/src packages/elims-database/src packages/elims-instruments/src
```

## Backend development

```powershell
uv run --package elims-backend uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

Useful endpoints:

- API: <http://localhost:8000>
- OpenAPI: <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>
- Readiness: <http://localhost:8000/ready>
- Metrics: <http://localhost:8000/metrics>

## Database migrations

Run Alembic commands from `backend/`:

```powershell
Set-Location backend
uv run alembic current
uv run alembic history
uv run alembic upgrade head
uv run alembic downgrade -1
uv run alembic revision --autogenerate -m "describe change"
uv run alembic revision -m "describe change"
Set-Location ..
```

Review generated migrations and their data-loss implications before applying them.

## Frontend development

```powershell
npm --prefix frontend run dev
npm --prefix frontend run build
npm --prefix frontend run lint
npm --prefix frontend run format
```

## Frontend tests

```powershell
npm --prefix frontend run test
npm --prefix frontend run test:watch
npm --prefix frontend run test:coverage

npm --prefix frontend exec playwright install chrome
npm --prefix frontend run test:e2e
npm --prefix frontend run test:e2e:ui
npm --prefix frontend exec playwright test tests/e2e/home.spec.ts
npm --prefix frontend exec playwright test --headed
npm --prefix frontend exec playwright show-report
```

## Documentation

```powershell
# Aggregate site
uv run mkdocs build --strict
uv run mkdocs serve

# Deployable components
uv run mkdocs build --strict --config-file backend/mkdocs.yml
uv run mkdocs build --strict --config-file frontend/mkdocs.yml

# Python packages
uv run mkdocs build --strict --config-file packages/elims-cli/mkdocs.yml
uv run mkdocs build --strict --config-file packages/elims-utils/mkdocs.yml
uv run mkdocs build --strict --config-file packages/elims-com/mkdocs.yml
uv run mkdocs build --strict --config-file packages/elims-database/mkdocs.yml
uv run mkdocs build --strict --config-file packages/elims-instruments/mkdocs.yml
```

## Markdown and YAML

```powershell
npm --prefix frontend exec markdownlint-cli2 --config ../.markdownlint-cli2.jsonc '../docs/**/*.md' '../backend/docs/**/*.md' '../frontend/docs/**/*.md' '../packages/*/docs/**/*.md'

uv run --group quality yamllint .github config compose.yml compose.traefik.yml compose.production.yml mkdocs.yml backend/mkdocs.yml frontend/mkdocs.yml packages
```

## Build Python packages

```powershell
uv build --all-packages
uv run --locked python scripts/check_wheels.py

uv build --package elims-cli
uv build --package elims-utils
uv build --package elims-com
uv build --package elims-database
uv build --package elims-instruments
```

Build artifacts are written to `dist/`.

## ELIMS CLI

```powershell
uv run elims --help
uv tool install ./packages/elims-cli
uv tool install --force ./packages/elims-cli
elims --help
uv tool uninstall elims-cli
```

## Docker development stack

```powershell
docker compose config
docker compose config --services
docker compose config --profiles
docker compose build
docker compose --env-file .env up --build
docker compose --env-file .env up --build -d --wait
docker compose ps
docker compose logs --follow
docker compose logs --follow backend
docker compose stop
docker compose down
```

This destructive variant also removes local database and observability volumes:

```powershell
docker compose down --volumes
```

## Observability

```powershell
docker compose --env-file .env --profile observability up --build -d --wait
docker compose logs --follow prometheus grafana
```

- Frontend: <http://localhost:8080>
- Backend: <http://localhost:8000>
- Grafana: <http://localhost:3000>
- Prometheus: <http://localhost:9090>

## Local Traefik proxy

```powershell
docker compose -f compose.yml -f compose.traefik.yml --env-file .env up --build -d --wait
```

The proxy listens on <http://localhost:8088>.

## Disposable smoke test

```powershell
docker compose --env-file .env.example -p elims-smoke up --build -d --wait --wait-timeout 120
python scripts/smoke.py
docker compose --env-file .env.example -p elims-smoke logs --tail=100
docker compose --env-file .env.example -p elims-smoke down --volumes
```

## Production Compose

`compose.production.yml` is standalone and must not be merged with the development Compose file.

```powershell
$env:BACKEND_IMAGE = "ghcr.io/owner/repository-backend@sha256:..."
$env:FRONTEND_IMAGE = "ghcr.io/owner/repository-frontend@sha256:..."
$env:DATABASE_URL = "mysql+aiomysql://..."
$env:DOMAIN = "elims.example.com"
$env:ACME_EMAIL = "admin@example.com"

docker compose -f compose.production.yml config
docker compose -f compose.production.yml up -d --wait
```

Use only reviewed image digests and production secrets supplied outside version control.

## Pre-commit

```powershell
uv run --group quality pre-commit install
uv run --group quality pre-commit run
uv run --group quality pre-commit run --all-files
uv run --group quality pre-commit autoupdate
```

The staged-secrets hook runs the pinned Gitleaks image and requires a running Docker engine.

## Security checks

```powershell
uv audit
npm audit --prefix frontend --audit-level=high

docker run --rm -v "${PWD}:/repo:ro" aquasec/trivy:0.76.2 fs /repo --severity HIGH,CRITICAL --exit-code 1 --scanners vuln,secret,misconfig

docker run --rm -v "${PWD}:/repo:ro" ghcr.io/gitleaks/gitleaks:v8.30.1 git /repo --redact
```

## Infrastructure checks

```powershell
docker run --rm -v "${PWD}:/repo:ro" -w /repo rhysd/actionlint:1.7.12 -color

docker run --rm -v "${PWD}:/repo:ro" -w /repo hadolint/hadolint:v2.15.1 hadolint backend/Dockerfile frontend/Dockerfile
```

## GitHub CLI

```powershell
gh auth status
gh auth login
gh workflow list
gh run list
gh run view --log
gh pr list
gh issue list
```

These commands require Git, an initialized repository, a configured remote, and GitHub authentication.

## Complete local verification

```powershell
uv run ruff check backend packages scripts docs/hooks.py .claude/skills
uv run ruff format --check backend packages scripts docs/hooks.py .claude/skills
uv run mypy backend/app packages/elims-cli/src packages/elims-utils/src packages/elims-com/src packages/elims-database/src packages/elims-instruments/src
uv run pytest --cov --cov-report=term-missing
uv build --all-packages
uv run python scripts/check_wheels.py
uv run mkdocs build --strict

npm --prefix frontend run lint
npm --prefix frontend run test:coverage
npm --prefix frontend run build
npm --prefix frontend run test:e2e
```

The full-stack, security, and infrastructure CI jobs provide additional evidence beyond this sequence.
