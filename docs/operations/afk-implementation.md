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
- The exact leaf issue must have the `rdy-to-implement` label. A local issue file must declare `labels: [rdy-to-implement]` in its metadata; a GitHub issue is verified through `gh issue view`.
- Run the launcher from the repository root.

## Start a run

```powershell
.\scripts\start-afk-implementation.ps1 `
  -Issue "docs/product/issues/approved/example.md" `
  -Prd "docs/product/requirements/approved/example.md" `
  -Specification "docs/specifications/approved/example.md" `
  -ArchitectureResult "docs/decisions/accepted/example.md"
```

For a GitHub issue in the current repository, `-Issue` may instead be an issue number or URL. The GitHub CLI must be installed and authenticated. The check is read-only; the launcher never adds the label.

The launcher uses Claude Code auto permission mode and streams JSON events to `artifacts/afk-implementation/`. It does not enable unrestricted permission bypass.

The run stops when independent code review passes, a human decision or
additional authority is required, the maximum turn count is reached, or Claude
Code exits with an error. Continue with
`/verification-and-validation-orchestrator`; the AFK launcher does not cross
the Chapter 5 boundary automatically.

## Safety boundary

The launcher explicitly prohibits merging, pushing, deploying, publishing, changing secrets, accessing production, and mutating external issue trackers. Those actions require separate user authorization.

Do not run multiple implementation orchestrators in the same working tree. For independent leaf issues, use a separate Git worktree for each run to avoid conflicting edits.
