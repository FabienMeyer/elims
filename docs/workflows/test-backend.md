# Backend Testing Workflow

## Overview

The backend testing workflow (`test-backend.yml`) runs automated tests for the FastAPI backend application. It performs linting, type checking, and unit tests with coverage reporting.

## Trigger Events

This workflow runs on:

- **Push** to `main` or `master` branches
- **Pull Request** events (opened, synchronized)

## Jobs

### Test Job

**Runner**: `ubuntu-latest`
**Timeout**: 15 minutes

#### Steps

1. **Checkout Code**

   - Uses: `actions/checkout@v6`
   - Checks out the repository code

1. **Set up Python**

   - Uses: `actions/setup-python@v6`
   - Python version: `3.13`
   - Installs the required Python version

1. **Install uv**

   - Uses: `astral-sh/setup-uv@v7`
   - Enables caching for faster subsequent runs
   - Installs the `uv` package manager

1. **Install Dependencies**

   - Working directory: `./backend`
   - Command: `uv sync`
   - Installs all backend dependencies from pyproject.toml

1. **Lint**

   - Working directory: `./backend`
   - Runs three linting tools:
     - `mypy`: Type checking for the `app` directory
     - `ruff check`: Linting with Ruff
     - `ruff format --check`: Checks code formatting

1. **Run Tests**

   - Working directory: `./backend`
   - Commands:
     ```bash
     uv run coverage run -m pytest tests/
     uv run coverage report
     uv run coverage html --title "Backend Coverage"
     ```
   - Runs pytest with coverage tracking
   - Generates HTML coverage report

1. **Store Coverage Files**

   - Uses: `actions/upload-artifact@v6`
   - Uploads the `htmlcov` directory as an artifact
   - Artifact name: `coverage-html`

### Coverage Job

**Runs**: After test job completes (always runs, even if tests fail)

#### Steps

1. **Checkout Code**

   - Uses: `actions/checkout@v6`

1. **Download Artifact**

   - Uses: `actions/download-artifact@v7`
   - Downloads the coverage HTML artifact

1. **Smokeshow**

   - Uses: `samuelcolvin/smokeshow-action@v1`
   - Only runs if coverage files exist
   - Publishes coverage report to Smokeshow

## Environment Variables

No special environment variables required. The workflow uses the default Python and test environment.

## Secrets

No secrets required for this workflow.

## Configuration

### Python Version

Currently configured for Python 3.13. Update the version in the workflow file:

```yaml
- name: Set up Python
  uses: actions/setup-python@v6
  with:
    python-version: "3.13"
```

### Timeout

The test job has a 15-minute timeout. Adjust if needed:

```yaml
jobs:
  test:
    timeout-minutes: 15
```

## Coverage Reporting

Coverage reports are generated in two formats:

1. **Console Output**: Shows coverage percentage in workflow logs
1. **HTML Report**: Detailed HTML coverage report uploaded as artifact and to Smokeshow

Access coverage reports:

- **GitHub Actions**: Download `coverage-html` artifact from workflow run
- **Smokeshow**: Check workflow logs for Smokeshow URL

## Troubleshooting

### Tests Failing

1. Check the test logs in the workflow run
1. Ensure all tests pass locally: `uv run pytest tests/`
1. Verify dependencies are up to date: `uv sync`

### Linting Errors

1. Run linting locally:
   ```bash
   uv run mypy app
   uv run ruff check app
   uv run ruff format app --check
   ```
1. Fix any issues reported
1. Auto-fix formatting: `uv run ruff format app`

### Coverage Issues

1. Ensure pytest-cov is installed
1. Check that tests are in the `tests/` directory
1. Verify test discovery: `uv run pytest --collect-only`

## Best Practices

1. **Write Tests**: Maintain high test coverage (aim for >80%)
1. **Type Hints**: Use type hints for better mypy analysis
1. **Format Code**: Run `ruff format` before committing
1. **Fix Warnings**: Address linting warnings promptly
1. **Review Coverage**: Check coverage reports after changes

## Related Workflows

- [Lint Backend](lint-backend.md) - Additional linting checks
- [Pre-commit](pre-commit.md) - Pre-commit hook validation
- [Test Docker Compose](test-docker-compose.md) - Full stack integration tests
