# AFK implementation workflow

The AFK launcher runs one approved leaf issue through Chapter 5:

```text
TDD -> Green implementation -> Refactor -> Code review
```

Each phase uses its dedicated fresh-context agent. The implementation
orchestrator owns sequencing, correction loops, traceability, and the
`implementation-complete` result. Chapters 6–8 run through their own
orchestrators:

```text
Technical verification -> Agent system validation
-> Technical documentation -> Human E2E acceptance
```

## Prerequisites

- Claude Code must be installed and authenticated.
- The launcher uses `claude` on `PATH` or the native Windows installation in `%USERPROFILE%\.local\bin`.
- The leaf issue, PRD, specification, and architecture result must satisfy every approval gate required by `/implementation-orchestrator`.
- The exact leaf issue must have the `rdy-to-implement` label. The label is verified on the authoritative GitHub issue through `gh issue view`. A local issue file or plan metadata is not evidence.
- The PRD, specification, architecture result, ELIMS skills, and `.claude/settings.json` must be committed at the base revision. The run uses only committed content.
- `uv` must be on `PATH`. The launcher runs `uv sync --locked` in the worktree, so `uv.lock` must match `pyproject.toml` at the base revision.
- Run the launcher from the repository root.

## Start a run

```powershell
.\.claude\skills\05-implementation-orchestrator\scripts\start-afk-implementation.ps1 `
  -Issue 42 `
  -Branch "feat/42-backend-example-outcome" `
  -Prd "docs/product/requirements/approved/example.md" `
  -Specification "docs/specifications/approved/example.md" `
  -ArchitectureResult "docs/decisions/accepted/example.md"
```

`-Issue` is a GitHub issue number or URL in the current repository. The GitHub CLI must be installed and authenticated. The check is read-only; the launcher never adds the label.

`-Branch` must follow `<type>/<issue-number>-<scope>-<short-slug>` from
`docs/contributing/issues-and-branches.md`, and its issue number must match
`-Issue`.

| Parameter | Default | Purpose |
| --- | --- | --- |
| `-BaseRef` | `origin/main` | Revision that a new work branch starts from. The launcher fetches it first. |
| `-WorktreeRoot` | `<repository>-worktrees` next to the repository | Directory that holds one worktree per leaf. |
| `-InstallFrontend` | off | Also run `npm ci --prefix frontend` in the worktree. Use it when the leaf changes frontend code. |
| `-PrepareOnly` | off | Create or reuse the worktree and install dependencies, then stop before Claude Code starts. |
| `-MaxTurns` | `200` | Maximum Claude Code turns. |

The launcher uses Claude Code auto permission mode and streams JSON events to `artifacts/afk-implementation/`. It does not enable unrestricted permission bypass.

The run stops when independent code review passes, a human decision or
additional authority is required, the maximum turn count is reached, or Claude
Code exits with an error. Continue with
`/verification-and-validation-orchestrator`; the AFK launcher does not cross
the Chapter 5 boundary automatically.

## Safety boundary

The launcher explicitly prohibits merging, pushing, deploying, publishing, changing secrets, accessing production, and mutating external issue trackers. Those actions require separate user authorization. The gate-enforcement hook enforces the GitHub and Git part of this boundary.

## Gate enforcement

The project settings file `.claude/settings.json` registers a `PreToolUse`
hook. Before Claude Code runs a Bash or PowerShell command, the hook
`.claude/skills/shared/hooks/guard_gated_mutations.py` examines the command.
The hook applies to the main session and to every subagent that a skill
starts.

The hook gives one of three results:

| Result | Effect | Commands |
| --- | --- | --- |
| Deny | Claude Code does not run the command. | `gh pr merge` and merge requests through `gh api`; adding, removing, or deleting the `rdy-to-implement` label directly; `git push` with `--force`, `--force-with-lease`, `--delete`, `--mirror`, or a `+` or `:` refspec; `git push` to `main` or `master`; `git push` without a refspec from `main`, `master`, or an unknown branch; `gh issue delete` and `gh issue transfer`; `gh repo delete`, `archive`, and `rename`; `gh release delete`; `gh secret` and `gh variable` changes; `gh auth token`. |
| Ask | Claude Code shows a permission prompt. A person must approve the command. | `git push` of a work branch; `gh pr`, `gh issue`, `gh label`, `gh release`, `gh project`, `gh repo`, `gh workflow`, `gh run`, and `gh ruleset` subcommands that change GitHub state; `gh api` requests that use a method other than `GET` or a GraphQL mutation; a Python script started with `--apply`. |
| None | The normal permission rules apply. | Read-only commands, such as `gh issue view`, `gh pr view`, and `git status`, and local commands. |

When one command line contains several commands, the strictest result
applies. The hook also examines commands inside `bash -c`, `sh -c`, and
`pwsh -Command`.

The `rdy-to-implement` label remains available through the approved path.
`/github-issue-publisher` applies it with `github_issue.py --apply`, and the
hook asks for approval before that script runs.

### Behavior in an AFK run

An AFK run has no person to answer a permission prompt. Claude Code therefore
refuses every command with the Ask result. Chapter 5 does not need these
commands, except the optional Project status transition from
`Ready to implement` to `Implementation`. Make that transition before you
start the launcher, or let the orchestrator report it as not applied.

### Failure behavior

The hook is fail-closed. If the hook cannot start, exceeds its 15-second
timeout, or fails, Claude Code refuses the command. The hook requires `uv` on
`PATH` and adds approximately 0.1 seconds to each shell command.

### Limits

The hook examines the command text only. It does not detect a program that
starts `git` or `gh` itself, for example `python -c` with `subprocess`. The
hook is a deterministic backstop for the skill instructions. It is not a
sandbox, and it does not replace branch protection or the main-branch
ruleset.

### Change the hook

The tests in `.claude/skills/shared/tests/test_guard_gated_mutations.py`
define the expected result for each command. Add a test case before you
change the command lists. To review or disable hooks in a session, open
`/hooks` in Claude Code.

## Worktrees

Each AFK run works in a dedicated Git worktree for its leaf, at
`<WorktreeRoot>/<branch with / replaced by ->`. The main checkout is not
changed, so unrelated work in it stays out of the diff under review and out
of the review anchor.

The launcher does these steps in order:

1. It verifies the `rdy-to-implement` label and the branch name.
2. It confirms that the skills, the gate hook, and the approved artifacts are
   committed at the revision it will use. If one is missing, it stops before it
   creates a branch or a worktree.
3. It reuses the worktree when it already exists on the same branch. Otherwise
   it adds a worktree for the existing branch, or creates the branch at
   `-BaseRef`.
4. It runs `uv sync --locked` in the worktree, and `npm ci` when you specify
   `-InstallFrontend`.
5. It starts Claude Code in the worktree. The prompt gives the fork point of
   the branch as the review-anchor base.

Run the launcher again with the same `-Branch` to continue an interrupted run.
Independent leaf issues can run in parallel because each one has its own
worktree. Do not start two runs for the same leaf at the same time.

The worktree uses the hook and skills committed on its branch. A change to
`.claude/` in the main checkout has no effect on a worktree until you commit it
and the branch contains it. The launcher warns when the main checkout has
uncommitted changes under `.claude/`.

After the work merges, remove the worktree and the Red-state ref:

```powershell
git worktree remove <worktree path>
git update-ref -d refs/elims/red/<leaf identifier>
```
