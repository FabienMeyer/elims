# CI/CD Setup for ELIMS

This document explains the CI/CD workflows configured for the ELIMS project.

## Table of Contents

- [Workflows Overview](#workflows-overview)
- [Required Secrets](#required-secrets)
- [Workflow Details](#workflow-details)
- [Setting Up Deployment](#setting-up-deployment)
- [Badges](#badges)

## Workflows Overview

### Test & Lint Workflows (Run on PR and Push)

1. **Test Backend** ([test-backend.yml](.github/workflows/test-backend.yml))

   - Runs on: Push to main/master, Pull Requests
   - Python 3.13 + uv
   - Lints with mypy, ruff
   - Runs pytest with coverage
   - Uploads coverage to Smokeshow

1. **Test Frontend (Playwright)** ([test-frontend.yml](.github/workflows/test-frontend.yml))

   - Runs on: Push to main/master, Pull Requests
   - Sharded tests (4 parallel runners)
   - E2E tests with Playwright
   - Uses MariaDB and Redis services
   - Merges test reports

1. **Lint Backend** ([lint-backend.yml](.github/workflows/lint-backend.yml))

   - Runs on: Push to main/master, Pull Requests
   - Checks code quality with mypy, ruff

1. **Lint Frontend** ([lint-frontend.yml](.github/workflows/lint-frontend.yml))

   - Runs on: Push to main/master, Pull Requests
   - Checks code quality with Biome

1. **Test Docker Compose** ([test-docker-compose.yml](.github/workflows/test-docker-compose.yml))

   - Runs on: Push to main/master, Pull Requests
   - Tests full stack deployment
   - Verifies all services start correctly

1. **Pre-commit** ([pre-commit.yml](.github/workflows/pre-commit.yml))

   - Runs on: Pull Requests
   - Validates pre-commit hooks

### Deployment Workflows

7. **Deploy to Staging** ([deploy-staging.yml](.github/workflows/deploy-staging.yml))

   - Runs on: Push to main/master branch
   - Requires: Self-hosted runner with 'staging' label
   - Environment: staging

1. **Deploy to Production** ([deploy-production.yml](.github/workflows/deploy-production.yml))

   - Runs on: Release published
   - Requires: Self-hosted runner with 'production' label
   - Environment: production

### Automation Workflows

9. **Issue Manager** ([issue-manager.yml](.github/workflows/issue-manager.yml))

   - Automatically manages stale issues
   - Closes answered issues after 10 days
   - Closes waiting issues after 30 days

1. **Labeler** ([labeler.yml](.github/workflows/labeler.yml))

   - Automatically labels PRs based on changed files
   - Configuration in [labeler.yml](.github/labeler.yml)

1. **Latest Changes** ([latest-changes.yml](.github/workflows/latest-changes.yml))

   - Automatically updates [release notes](docs/release-notes.md)
   - Runs when PRs are merged

1. **Add to Project** ([add-to-project.yml](.github/workflows/add-to-project.yml))

   - Automatically adds issues and PRs to GitHub Projects

1. **Deploy Documentation** ([deploy-docs.yml](.github/workflows/deploy-docs.yml))

   - Deploys versioned docs to GitHub Pages
   - Auto-deploys on push to main (dev/latest)
   - Auto-deploys on release (stable)

## Required Secrets

Configure these secrets in your GitHub repository settings (`Settings > Secrets and variables > Actions`):

### Database Secrets

- `MARIADB_ROOT_PASSWORD` - MariaDB root password
- `MARIADB_DATABASE` - Database name (e.g., `elims`)
- `MARIADB_USER` - Database user (e.g., `elims`)
- `MARIADB_PASSWORD` - Database user password

### Redis Secrets

- `REDIS_PASSWORD` - Redis password

### MQTT Secrets

- `MQTT_USERNAME` - MQTT broker username
- `MQTT_PASSWORD` - MQTT broker password

### Backend Secrets

- `BACKEND_SECRET_KEY` - Secret key for JWT tokens (generate with: `openssl rand -hex 32`)
- `FIRST_SUPERUSER` - Admin email address
- `FIRST_SUPERUSER_PASSWORD` - Admin password

### Grafana Secrets

- `GRAFANA_ADMIN_USER` - Grafana admin username
- `GRAFANA_ADMIN_PASSWORD` - Grafana admin password

### Deployment Secrets

- `DOMAIN_STAGING` - Staging domain (e.g., `staging.example.com`)
- `DOMAIN_PRODUCTION` - Production domain (e.g., `example.com`)
- `STACK_NAME_STAGING` - Docker Compose stack name for staging (e.g., `elims-staging`)
- `STACK_NAME_PRODUCTION` - Docker Compose stack name for production (e.g., `elims-prod`)

### Optional Secrets

- `LATEST_CHANGES` - GitHub personal access token for automatic release notes
- `SMOKESHOW_AUTH_KEY` - Smokeshow key for coverage reports ([Get one here](https://smokeshow.helpmanual.io/))

## 📚 Workflow Details

### Test Backend

**Purpose**: Ensures backend code quality and test coverage

**Steps**:

1. Checkout code
1. Setup Python 3.13 and uv
1. Install dependencies
1. Run linting (mypy, ruff)
1. Run tests with coverage
1. Upload coverage report to Smokeshow

**Local equivalent**:

```bash
cd backend
uv sync
uv run mypy app
uv run ruff check app
uv run ruff format app --check
uv run coverage run -m pytest tests/
uv run coverage report
```

### Test Frontend (Playwright)

**Purpose**: Runs end-to-end tests for the frontend

**Features**:

- **Sharded tests**: Runs tests in parallel across 4 workers for faster execution
- **Service containers**: Automatically starts MariaDB and Redis
- **Report merging**: Combines results from all shards

**Local equivalent**:

```bash
docker compose up -d mariadb redis backend
cd frontend
bun install
bunx playwright install chromium --with-deps
bunx playwright test
```

### Test Docker Compose

**Purpose**: Validates that the full stack can be deployed successfully

**Steps**:

1. Creates .env file with test configuration
1. Builds all Docker images
1. Starts all services
1. Waits for services to be healthy
1. Checks backend and frontend health endpoints
1. Shows logs if anything fails

### Deployment Workflows

**Prerequisites**:

1. Set up a self-hosted GitHub Actions runner on your server
1. Configure the runner with appropriate labels (`staging` or `production`)
1. Ensure the runner has Docker installed
1. Configure all required secrets

**Staging Deployment**:

- Triggers on every push to main/master
- Good for testing changes before production
- URL: `https://dashboard.staging.{DOMAIN_STAGING}`

**Production Deployment**:

- Triggers when you publish a GitHub release
- URL: `https://dashboard.{DOMAIN_PRODUCTION}`

## 🚀 Setting Up Deployment

### Step 1: Install GitHub Actions Runner

On your server:

```bash
# Create a user for GitHub Actions
sudo adduser github

# Add Docker permissions
sudo usermod -aG docker github

# Switch to github user
sudo su - github

# Follow GitHub's instructions to install the runner
# Settings > Actions > Runners > New self-hosted runner
```

### Step 2: Install Runner as a Service

```bash
# Exit github user
exit

# Become root
sudo su

# Go to runner directory
cd /home/github/actions-runner

# Install service
./svc.sh install github

# Start service
./svc.sh start

# Check status
./svc.sh status
```

### Step 3: Configure Secrets

Go to your repository `Settings > Secrets and variables > Actions` and add all required secrets listed above.

### Step 4: Deploy

**Staging**: Push to main/master branch

```bash
git push origin main
```

**Production**: Create and publish a release

```bash
# Create a tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Then publish the release on GitHub
```

## 📊 Badges

Add these badges to your README:

```markdown
[![Test Backend](https://github.com/YOUR_USERNAME/elims2/workflows/Test%20Backend/badge.svg)](https://github.com/YOUR_USERNAME/elims2/actions?query=workflow%3A%22Test+Backend%22)
[![Test Frontend](https://github.com/YOUR_USERNAME/elims2/workflows/Test%20Frontend%20(Playwright)/badge.svg)](https://github.com/YOUR_USERNAME/elims2/actions?query=workflow%3A%22Test+Frontend+(Playwright)%22)
[![Test Docker Compose](https://github.com/YOUR_USERNAME/elims2/workflows/Test%20Docker%20Compose/badge.svg)](https://github.com/YOUR_USERNAME/elims2/actions?query=workflow%3A%22Test+Docker+Compose%22)
```

For coverage badge (requires Smokeshow setup):

```markdown
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/redirect/YOUR_USERNAME/elims2)](https://coverage-badge.samuelcolvin.workers.dev/YOUR_USERNAME/elims2.svg)
```

## 🔧 Customization

### Adjusting Test Shards

In [test-frontend.yml](.github/workflows/test-frontend.yml), modify the matrix:

```yaml
strategy:
  matrix:
    shardIndex: [1, 2, 3, 4]  # Increase for more parallelization
    shardTotal: [4]           # Must match number of shards
```

### Adding More Environments

Copy `deploy-staging.yml` and modify:

- Workflow name
- Trigger conditions
- Secrets used
- Runner labels

### Modifying Auto-labeling

Edit [.github/labeler.yml](.github/labeler.yml) to change which files trigger which labels.

## 🐛 Troubleshooting

### Tests failing locally but passing in CI (or vice versa)

- Check Python/Node versions match
- Verify all dependencies are installed
- Check environment variables

### Deployment fails

- Verify secrets are set correctly
- Check runner has Docker installed
- Ensure runner has proper permissions
- Check server has enough disk space

### Coverage not uploading

- Ensure `SMOKESHOW_AUTH_KEY` secret is set
- Check that tests actually ran
- Verify coverage files were generated

## 📖 Further Reading

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Playwright Documentation](https://playwright.dev/)
- [Smokeshow Documentation](https://smokeshow.helpmanual.io/)
- [Self-hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners)
