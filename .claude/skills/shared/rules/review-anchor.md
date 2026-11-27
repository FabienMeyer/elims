# Review anchor

A review anchor identifies the exact content that a phase examined. Every
verdict that depends on "the exact diff" must cite the anchor it examined.

Compute it from the repository root:

```powershell
uv run python .claude/skills/shared/scripts/review_anchor.py --base <default-branch>
uv run python .claude/skills/shared/scripts/review_anchor.py --base <default-branch> --head <commit>
```

The first command anchors the working tree, including untracked files that Git
does not ignore. The second anchors a commit. The result has three fields:
`base` (the commit that the change is measured against), `source`, and `tree`
(the content identifier). Two anchors are equal when `base` and `tree` are
equal. A working tree and a commit that contain the same files have the same
`tree`, so committing the change does not alter the anchor.

The anchor excludes `docs/product/traceability/`. The traceability matrix in
that directory records anchors and phase evidence, so a change to it does not
alter an anchor. A review, verification, or validation pass therefore does
not cover the matrix content.

## Red state

The Red state is the anchor after `/tdd-engineer` returns `red` and before any
production change. `.claude/skills/shared/scripts/red_state.py record` computes
it, rejects it when the change against the base touches non-test files, and
pins it under the local ref `refs/elims/red/<leaf>`. The ref keeps the tree
from Git garbage collection. A branch push does not send it. Delete the ref
with `git update-ref -d refs/elims/red/<leaf>` after the work merges.

`red_state.py verify` checks the recorded tree and replays the focused tests
in a temporary copy of it. The technical verifier uses it to confirm that Red
came before Green.

Rules:

- The implementation orchestrator records the anchor after every production or
  test change and before every independent review.
- A reviewer, verifier, or validator recomputes the anchor and returns `blocked`
  when it differs from the supplied anchor.
- A pass applies only to its recorded anchor. Any later change creates a new
  anchor and invalidates the earlier passes that the change affects.
- Chapter 7 may change documentation files only. List the changed paths with
  `git diff --name-only <Chapter 6 tree> <final tree>` and confirm that every
  path is documentation.
- The candidate commit for human acceptance must have the same anchor as the
  final Chapter 7 anchor.
- The script writes unreferenced Git objects only. It does not change the index,
  the working tree, or any ref.
