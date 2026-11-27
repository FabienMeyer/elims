# GitHub setup for ELIMS skills

This guide connects a local ELIMS checkout to GitHub and prepares the ELIMS
skills to manage GitHub Projects, issues, labels, and pull requests.

Repository and Project identifiers are not secrets and can be stored in the
repository. Access tokens, passwords, and private keys must not be committed.

## Prerequisites

Install the following tools and make sure that they are available on `PATH`:

- [Git](https://git-scm.com/downloads)
- [GitHub CLI](https://cli.github.com/)

Verify the installation:

```powershell
git --version
gh --version
```

## Connect the local repository

Check whether an `origin` remote already exists:

```powershell
git remote -v
```

Add the GitHub repository when no `origin` exists:

```powershell
git remote add origin https://github.com/OWNER/REPOSITORY.git
```

If `origin` points to the wrong repository, inspect it before changing it, then
set the intended URL:

```powershell
git remote get-url origin
git remote set-url origin https://github.com/OWNER/REPOSITORY.git
```

Verify the result:

```powershell
git remote get-url origin
```

Replace `OWNER` and `REPOSITORY` with the GitHub organization or user and the
repository name.

## Authenticate the GitHub CLI

Use the browser login flow. GitHub CLI stores the resulting credential in the
operating-system credential store when one is available.

```powershell
gh auth login --hostname github.com --web --git-protocol https
```

Grant the additional scopes required to manage repositories and Projects:

```powershell
gh auth refresh --hostname github.com --scopes repo,project,read:org
```

Verify the account and scopes:

```powershell
gh auth status --hostname github.com
```

If the stored token is invalid, log in again with `gh auth login`. Do not put a
personal access token in a tracked file, a command-line argument, or the Git
remote URL.

## Select the GitHub Project

List the Projects that belong to the organization or user:

```powershell
gh project list --owner OWNER
```

Record these non-secret values for automation:

- repository: `OWNER/REPOSITORY`
- Project owner: `OWNER`
- Project number: the number returned by `gh project list`
- status field: `Status`

The repository and Project 14 identifiers, expected statuses, and view definitions
are versioned in `.github/elims-project.yml`.

Do not add a token or another credential to this file.

The authenticated account needs access to the repository and Project. Test the
configuration by listing the Project fields and items:

```powershell
gh project field-list 1 --owner OWNER
gh project item-list 1 --owner OWNER
```

Replace `1` with the selected Project number.

## Configure the Project workflow

Create a single-select `Status` field with the following values:

1. `Backlog`
2. `Ready to implement`
3. `Implementation`
4. `Technical verification`
5. `Agent system validation`
6. `Technical documentation`
7. `Human acceptance`
8. `Ready to merge`
9. `Done`
10. `Blocked`

Use the issue as the primary Project item. Link the pull request to the issue
instead of adding both as duplicate progress items.

In the Project **Workflows** settings, enable the built-in workflows that:

- add matching repository issues to the Project;
- set newly added issues to `Backlog` or `Ready to implement`;
- set closed issues and merged pull requests to `Done` where applicable.

Custom transitions can be made by a script with `gh project item-edit`. For
example:

```powershell
python .claude/skills/06-verification-and-validation-orchestrator/scripts/github_project.py `
  --project 1 --owner OWNER --url https://github.com/OWNER/REPOSITORY/issues/123 `
  --from-status Implementation --to "Technical verification"
```

Project status changes must follow the implementation gates. A script must
verify the current status before changing it and must not claim human
acceptance automatically.

## Delivery chapters

The delivery skills are organized as follows:

- Chapter 5 — implementation through independent code review;
- Chapter 6 — technical verification and agent system validation;
- Chapter 7 — technical writing and independent documentation review;
- Chapter 8 — human E2E plan, human execution, and acceptance recording.

Chapter 6 opens the draft pull request when authorized. Chapter 7 adds the
reviewed documentation. Chapter 8 marks the pull request ready when authorized
and then stops for real human execution. Only an explicitly supplied human
result can produce `human-accepted`, `human-rejected`, or `human-blocked`.

## Configure GitHub Actions credentials

Prefer the workflow-provided `GITHUB_TOKEN` for repository operations. Give it
only the permissions required by the workflow, for example:

```yaml
permissions:
  contents: read
  issues: write
  pull-requests: write
```

Project operations may require a GitHub App token or a separate, narrowly
scoped token. Store such a credential in GitHub, not in this repository:

1. Open the repository on GitHub.
2. Open **Settings**.
3. Select **Secrets and variables**, then **Actions**.
4. Create a repository secret such as `ELIMS_PROJECT_TOKEN`.
5. Limit the token to the required repository and Project permissions.

Reference the secret only from a workflow environment or action input:

```yaml
env:
  GH_TOKEN: ${{ secrets.ELIMS_PROJECT_TOKEN }}
```

Use an organization-level secret when several repositories need the same
automation, and restrict its repository access policy.

## Audit the live configuration

Run `uv run --group quality python .claude/skills/shared/scripts/configure.py` at the repository root.
The audit checks the declared labels, repository link, statuses, view filters,
visible fields, grouping and enabled workflow names. Exit code 2 reports drift.
Entries for grouping or built-in workflows require the Project settings UI.
For **Item added to project**, select **Backlog**. Name the repository auto-add
workflow **Auto-add ELIMS issues**, select `FabienMeyer/elims`, and set its
filter to `is:issue`. Verify that filter in the Project UI.

After the first architecture PR runs, configure the main branch ruleset to
require a pull request and the GitHub Actions checks `python`, `frontend`,
`stack`, `infrastructure`, and `audit`. Use the check names recorded on that PR.

## Verification checklist

- `git remote get-url origin` returns the expected repository.
- `gh auth status` reports a valid account.
- The authenticated token includes the `project` scope.
- `gh project field-list` can read the selected Project.
- The Project contains the expected `Status` values.
- Repository and Project identifiers contain no credentials.
- Required Actions secrets exist in GitHub and are not present locally.
- A test issue can be added to the Project and moved between non-gated statuses.
- Human acceptance and merge remain explicit, authorized actions.

## Troubleshooting

### `git` is not recognized

Install Git for Windows, reopen the terminal, and run `git --version`. If Git is
already installed, add its command directory to the user `PATH`.

### GitHub CLI reports an invalid token

Authenticate again:

```powershell
gh auth login --hostname github.com --web
gh auth refresh --hostname github.com --scopes repo,project,read:org
```

### Project commands return a permission error

Confirm that the selected GitHub account can access the Project and that the
CLI token has the `project` scope. Organization policy or single sign-on may
also require separate authorization.

### A workflow cannot update the Project

Check the workflow permissions and whether `GITHUB_TOKEN` can access the
target Project. For an organization-level Project, use a narrowly scoped
GitHub App or Actions secret when the default token is insufficient.
