# Frontend Testing Workflow (Playwright)

## Overview

The frontend testing workflow (`test-frontend.yml`) runs end-to-end tests using Playwright. It sets up a complete test environment with MariaDB and Redis services, starts the backend API, and runs Playwright tests in parallel using sharding.

## Trigger Events

This workflow runs on:

- **Push** to `main` or `master` branches
- **Pull Request** events (opened, synchronized)

## Jobs

### Test Job

**Runner**: `ubuntu-latest`
**Timeout**: 30 minutes
**Strategy**: Matrix with sharding (4 parallel runners)

#### Matrix Configuration

```yaml
strategy:
  fail-fast: false
  matrix:
    shardIndex: [1, 2, 3, 4]
    shardTotal: [4]
```

This configuration runs tests in 4 parallel shards for faster execution.

#### Services

Two services are configured to run alongside the test job:

##### MariaDB Service

- **Image**: `mariadb:11`
- **Port**: 3306
- **Environment Variables**:
  - `MARIADB_ROOT_PASSWORD`: Root password (from secrets or default)
  - `MARIADB_DATABASE`: Database name (default: `elims_test`)
  - `MARIADB_USER`: Database user (default: `elims`)
  - `MARIADB_PASSWORD`: User password (from secrets or default)
- **Health Check**: Checks that database is initialized and ready

##### Redis Service

- **Image**: `redis:7-alpine`
- **Port**: 6379
- **Health Check**: Uses `redis-cli ping`

#### Steps

1. **Checkout Code**

   - Uses: `actions/checkout@v6`

1. **Set up Python**

   - Uses: `actions/setup-python@v6`
   - Python version: `3.13`
   - Required for running the backend API

1. **Install uv**

   - Uses: `astral-sh/setup-uv@v7`
   - Installs the `uv` package manager

1. **Install Backend Dependencies**

   - Working directory: `./backend`
   - Command: `uv sync`

1. **Install Bun**

   - Uses: `oven-sh/setup-bun@v2`
   - Installs the Bun JavaScript runtime

1. **Install Frontend Dependencies**

   - Working directory: `./frontend`
   - Command: `bun install`

1. **Install Playwright Browsers**

   - Working directory: `./frontend`
   - Command: `bunx playwright install chromium --with-deps`
   - Installs Chromium browser for testing

1. **Start Backend Server**

   - Working directory: `./backend`
   - Command: `uv run fastapi dev app/main.py &`
   - Runs the backend API in the background
   - Waits 5 seconds for startup
   - **Environment Variables**:
     - `MARIADB_HOST`: localhost
     - `MARIADB_PORT`: 3306
     - `MARIADB_USER`: From secrets or default
     - `MARIADB_PASSWORD`: From secrets or default
     - `MARIADB_DATABASE`: elims_test
     - `REDIS_HOST`: localhost
     - `REDIS_PORT`: 6379
     - `REDIS_PASSWORD`: From secrets or default

1. **Run Playwright Tests**

   - Working directory: `./frontend`
   - Command: `bunx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}`
   - Runs tests for the current shard
   - **Environment Variables**:
     - `VITE_API_URL`: http://localhost:8000
     - `CI`: true

1. **Upload Blob Report**

   - Uses: `actions/upload-artifact@v6`
   - Uploads test reports as artifacts
   - Runs even if tests fail (`if: always()`)

1. **Upload Playwright Report** (if tests fail)

   - Uploads full Playwright HTML report
   - Only runs if tests failed

### Merge Reports Job

**Runs**: After all test jobs complete
**Condition**: Always runs, even if tests fail

This job merges test reports from all shards into a single report.

#### Steps

1. **Download Blob Reports**

   - Downloads all blob report artifacts

1. **Merge Reports**

   - Merges all shard reports into one
   - Generates HTML report

1. **Upload HTML Report**

   - Uploads merged report as artifact

## Environment Variables

### Required During Test Execution

- `MARIADB_HOST`: localhost
- `MARIADB_PORT`: 3306
- `MARIADB_USER`: Database user
- `MARIADB_PASSWORD`: Database password
- `MARIADB_DATABASE`: Database name
- `REDIS_HOST`: localhost
- `REDIS_PORT`: 6379
- `REDIS_PASSWORD`: Redis password
- `VITE_API_URL`: Backend API URL
- `CI`: Set to true for CI environment

## Secrets

### Optional Secrets

If not provided, defaults are used:

- `MARIADB_ROOT_PASSWORD`: MariaDB root password (default: `testpassword`)
- `MARIADB_DATABASE`: Database name (default: `elims_test`)
- `MARIADB_USER`: Database user (default: `elims`)
- `MARIADB_PASSWORD`: User password (default: `testpassword`)
- `REDIS_PASSWORD`: Redis password (default: `testpassword`)

Configure these in: `Settings > Secrets and variables > Actions`

## Test Sharding

Sharding splits tests across multiple runners for parallel execution:

- **Benefits**: Faster test execution, efficient resource usage
- **Current Configuration**: 4 shards
- **Adjust Sharding**: Modify the `shardTotal` value in the matrix

Example for 8 shards:

```yaml
matrix:
  shardIndex: [1, 2, 3, 4, 5, 6, 7, 8]
  shardTotal: [8]
```

## Artifacts

### Test Reports

- **Blob Reports**: Individual shard reports (intermediate format)
- **HTML Report**: Merged final report (downloadable from workflow run)
- **Retention**: 30 days (default GitHub Actions setting)

Access reports:

1. Go to workflow run
1. Scroll to "Artifacts" section
1. Download `playwright-report`

## Configuration

### Playwright Configuration

Configure Playwright in `frontend/playwright.config.ts`:

```typescript
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.VITE_API_URL || 'http://localhost:8000',
    trace: 'on-first-retry',
  },
});
```

### Timeout

Adjust workflow timeout if tests take longer:

```yaml
jobs:
  test:
    timeout-minutes: 30  # Increase if needed
```

## Troubleshooting

### Tests Timing Out

1. Check backend logs for startup issues
1. Verify database connection
1. Increase sleep time after backend start:
   ```yaml
   sleep 10  # Increase from 5
   ```

### Service Connection Issues

1. Verify service health checks are passing
1. Check service logs in workflow output
1. Ensure correct ports and hostnames

### Browser Installation Failures

1. Check Playwright version compatibility
1. Verify system dependencies:
   ```bash
   bunx playwright install --with-deps chromium
   ```

### Sharding Issues

1. Ensure tests are independent (no shared state)
1. Check for test dependencies or ordering
1. Review shard-specific failures in artifacts

## Best Practices

1. **Write Independent Tests**: Each test should be self-contained
1. **Use Page Objects**: Organize selectors and actions
1. **Handle Timing**: Use proper waits instead of sleep
1. **Clean Up**: Reset state between tests
1. **Meaningful Assertions**: Use descriptive assertion messages
1. **Test Data**: Use factories or fixtures for test data
1. **Visual Testing**: Consider screenshot comparisons for UI tests

## Local Development

Run tests locally to debug before pushing:

```bash
# Start services
docker compose up mariadb redis -d

# Start backend
cd backend
uv run fastapi dev app/main.py

# Run tests (in another terminal)
cd frontend
bun run test

# Run tests with UI
bun run test --ui

# Run specific test
bun run test tests/home.spec.ts
```

## Related Workflows

- [Lint Frontend](lint-frontend.md) - Frontend linting checks
- [Test Backend](test-backend.md) - Backend unit tests
- [Test Docker Compose](test-docker-compose.md) - Full stack integration tests
