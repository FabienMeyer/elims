---
name: human-acceptance-orchestrator
description: Prepare and gate human E2E acceptance for one verified and documented ELIMS feature, then route an explicitly supplied human result.
argument-hint: "<leaf> <approved artifacts> <Chapter 7 report> [traceability matrix]"
disable-model-invocation: true
model: sonnet
---

# Human Acceptance Orchestrator

Run Chapter 8. Prepare the human E2E plan, stop for real human execution, and
record only an explicitly supplied result.

## Entry gate

Require Chapter 6 `verified-and-agent-validated`, Chapter 7
`documentation-complete`, the exact candidate commit, the current draft pull
request, and a complete traceability matrix. Return
`human-acceptance-blocked` when any gate is missing.

## Workflow

Use `scripts/github_acceptance.py` to inspect the pull request and plan the
Chapter 8 Project transition. Run it without `--apply` first. Use `--apply`
only after explicit authorization; credentials must come from GitHub CLI or
the workflow environment.

1. Invoke `/human-e2e-test-author` in a fresh context.
2. On `plan-ready`, add the plan to the delivery evidence.
3. Plan the pull-request ready-state and Project transition to
   `Human acceptance`. Apply either external mutation only with explicit
   authorization.
4. Return `ready-for-human-acceptance` and stop. State the exact plan,
   environment, and candidate commit the human must test.
5. After a human supplies results, invoke `/acceptance-result-recorder` in a
   fresh context.
6. For `human-rejected`, route each defect to the responsible chapter and
   repeat every invalidated downstream gate before requesting a new human run.
7. For `human-blocked`, preserve the blocker and stop.
8. For `human-accepted`, plan the Project transition to `Ready to merge` and
   apply it only with explicit authorization.

Human execution is a hard gate. Neither this orchestrator nor another agent
may simulate the human, infer missing results, or convert a rejection or
blocker to acceptance.

## Completion report

Return `human-accepted`, `human-rejected`, `human-blocked`, or
`ready-for-human-acceptance`. Include the plan revision, candidate commit,
human-supplied evidence when available, traceability, pull-request state,
Project state, defects, limitations, and next authorized action.

Even after `human-accepted`, do not merge, deploy, close issues, or claim those
actions occurred. Final CI, required reviews, and merge authorization remain
separate gates.
