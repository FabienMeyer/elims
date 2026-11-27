---
id: TRACE-000
title: Replace with the leaf issue title
status: in-progress
leaf_issue: ISSUE-000
github_issue: null
issue_plan: ISSUE-PLAN-000
related_prd: PRD-000
related_specifications: [SPEC-000]
related_ui_ux_definitions: []
related_decisions: []
branch: null
base_commit: null
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

<!--
Location: docs/product/traceability/<leaf issue identifier>.md, committed with
the work branch. review_anchor.py excludes docs/product/traceability/, so
recording evidence here does not change a review anchor.

status values: in-progress, implementation-complete,
verified-and-agent-validated, documentation-complete, ready-for-human-acceptance,
human-accepted, human-rejected, human-blocked, blocked.

Owners: Chapter 5 orchestrator creates the file and owns Mapping, Reverse
mapping, and the Chapter 5 evidence. Each later orchestrator adds only its own
evidence columns and verdict rows. A phase skill reports evidence; the
responsible orchestrator writes it here.

Write a reference, not a summary: a file and symbol, a test node ID, an exact
command with its result, or a report path. Write "n/a" with a reason when a
cell does not apply. Never leave an applicable cell empty at a phase verdict.
-->

## Mapping

<!--
Independent reviewers, verifiers, and validators receive this section and
Reverse mapping only. Do not add verdicts, rationale, or conclusions here.
Add one row for every in-scope issue completion criterion, specification
acceptance criterion, and applicable UI/UX acceptance criterion.
-->

| Criterion | Approved behavior | Architecture constraints | Test locations | Production locations |
| --- | --- | --- | --- | --- |

## Reverse mapping

<!--
Add one row for every changed production file or symbol. A change without an
approved criterion, accepted constraint, or necessary technical support is
out of scope and must be removed.
-->

| Production change | Justification type | Criterion or constraint | Reason |
| --- | --- | --- | --- |

<!-- Justification type: criterion, architecture-constraint, or technical-support. -->

## Criterion evidence

| Criterion | Red evidence | Green evidence | Technical verification | UI/UX validation | System validation | Documentation | Human E2E scenario | Human E2E result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

<!--
Red evidence: the test node ID and the expected failure message.
Green evidence: the focused command and its passing result.
System validation: the scenario ID and result, or the not-applicable reason.
Human E2E result: copy the human-supplied result exactly. Only
/acceptance-result-recorder writes this column.
-->

## Cross-cutting effects

| Effect | Required | Location | Evidence |
| --- | --- | --- | --- |
| Documentation | | | |
| Configuration | | | |
| Migration and rollback | | | |
| Security | | | |
| Privacy | | | |
| Operations and observability | | | |

<!-- Required: yes, no, or the reason that the effect does not apply. -->

## Phase verdicts

<!--
Add one row for each phase run, including every repeated run. Record the
anchor tree that the phase examined. A pass applies only to its anchor. Record
the Red anchor after /tdd-engineer returns red and before any production
change, so that a verifier can confirm that Red came before Green. For the
tdd-engineer row, record the output of red_state.py record: its tree in Anchor
tree, and its ref and the exact focused test command in Report. The technical
verifier replays that command in the Red tree.
-->

| Chapter | Phase | Run | Verdict | Anchor base | Anchor tree | Report | Date |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | tdd-engineer | 1 | | | | ref: refs/elims/red/ISSUE-000; command: | |
| 5 | implementation-engineer | 1 | | | | | |
| 5 | refactor-engineer | 1 | | | | | |
| 5 | code-reviewer | 1 | | | | | |
| 6 | technical-verifier | 1 | | | | | |
| 6 | ui-ux-validator | 1 | | | | | |
| 6 | system-validator | 1 | | | | | |
| 7 | technical-writer | 1 | | | | | |
| 7 | documentation-reviewer | 1 | | | | | |
| 8 | human-e2e-test-author | 1 | | | | | |
| 8 | acceptance-result-recorder | 1 | | | | | |

## Correction log

<!--
Add one row for each required finding or failure. List every earlier pass
that the correction invalidates; those phases must run again.
-->

| Finding | Source phase | Severity | Routed to | Resolution | Invalidated passes |
| --- | --- | --- | --- | --- | --- |

## Skipped checks and limitations

## Residual risks
