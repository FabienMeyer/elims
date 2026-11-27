# Releases and GitHub packages

ELIMS uses one synchronized version for its applications and public Python
packages. Release Please reads Conventional Commit messages on `main` and
maintains a release pull request containing the changelog and version updates.
Merging that pull request creates the Git tag and GitHub Release.

For a release such as `v0.1.0`, the workflow publishes:

- `ghcr.io/fabienmeyer/elims-backend:v0.1.0`
- `ghcr.io/fabienmeyer/elims-frontend:v0.1.0`
- `elims-cli==0.1.0` on PyPI
- `elims-com==0.1.0` on PyPI
- `elims-database==0.1.0` on PyPI
- `elims-instruments==0.1.0` on PyPI
- `elims-utils==0.1.0` on PyPI

## Prepare a release

1. Merge pull requests with titles in `type(scope): description` format.
2. Review the release pull request maintained by Release Please.
3. For a major version, raise the `elims-utils` upper bound in
   `packages/elims-com/pyproject.toml` on the release pull request, for example
   from `<2` to `<3`. Release Please does not update that bound, and the
   workspace lockfile does not enforce it. `scripts/check_wheels.py` installs
   the built wheels together, so it fails in CI and in the **Release** workflow,
   before PyPI publication, until the bound allows the new `elims-utils`
   version.
4. Merge the release pull request when its changelog and calculated version are
   correct.
5. Confirm that the **Release** workflow publishes both container images and
   all five Python packages.

Do not edit generated version sections in `CHANGELOG.md` separately. Correct
the source commit or edit the open release pull request when release notes need
adjustment.

## PyPI trusted publishing setup

PyPI publication uses OpenID Connect and does not store an API token. Pending
publishers cannot reuse one identical identity for several new project names,
so each package has a dedicated GitHub environment. Before the first release,
configure these pending Trusted Publishers on PyPI:

| PyPI project | GitHub environment |
| --- | --- |
| `elims-cli` | `pypi-elims-cli` |
| `elims-com` | `pypi-elims-com` |
| `elims-database` | `pypi-elims-database` |
| `elims-instruments` | `pypi-elims-instruments` |
| `elims-utils` | `pypi-elims-utils` |

Use the following shared values for every publisher:

- Owner: `FabienMeyer`
- Repository: `elims`
- Workflow: `release.yml`
- Environment: the package-specific value from the table

Create all five environments in the GitHub repository. Requiring a reviewer
provides a manual approval gate immediately before each package publication.

## Release Please authentication

The workflow falls back to `GITHUB_TOKEN`, which is enough to maintain the
release pull request and create releases. GitHub does not start new workflow
runs for pull requests created with that token. If branch protection requires
CI checks on the release pull request, add a `RELEASE_PLEASE_TOKEN` Actions
secret containing a fine-grained token that can write repository contents,
issues, and pull requests. Release Please will use it automatically.

GHCR publication uses the repository `GITHUB_TOKEN`; no personal access token
is required. Repository Actions must have permission to create packages.
Container visibility and access are managed in each package's settings on
GitHub.

Use immutable image digests in production after the published images have been
reviewed.
