---
name: human-e2e-test-author
description: Create a human-executable E2E acceptance plan for a verified, documented ELIMS feature without claiming that the plan was executed.
argument-hint: "<leaf> <PRD> <specification> <architecture result> [UI/UX definition] <Chapter 7 report> [traceability matrix]"
disable-model-invocation: false
context: fork
agent: general-purpose
background: false
---

# Human E2E Test Author

Create the Chapter 8 procedure that a designated human will execute against an
approved pull-request build or preview environment. Author the plan; do not
execute it or infer acceptance.

## Entry gate

Require approved artifacts, Chapter 6 pass, Chapter 7
`documentation-complete`, the exact candidate commit, available environment
guidance, and the traceability matrix. Return `blocked` when a safe,
human-executable plan cannot be specified.

## Plan requirements

Map every human-observable specification and applicable UI/UX acceptance
criterion to one or more numbered scenarios. For each scenario specify:

- purpose and criterion identifiers;
- environment, candidate commit, accounts, roles, devices, integrations, and
  representative test data;
- preconditions and setup;
- numbered actions a human can follow without implementation knowledge;
- expected observable results and resulting state;
- evidence to capture;
- pass, fail, and blocked recording fields;
- cleanup or restoration steps.

Include relevant happy paths, permissions, negative behavior, boundaries,
recovery, interruption, and high-risk journeys. Keep agent system-validation
evidence as context, not as a substitute for execution by a human.

## Verdict

Return exactly one verdict:

- `plan-ready`: the complete human E2E plan is ready for execution;
- `not-applicable`: human E2E acceptance has no meaningful applicable
  scenario, with criterion-level rationale requiring human confirmation;
- `blocked`: evidence, environment, or decisions prevent a usable plan.

Do not mark any scenario passed, change code or documentation, approve the
feature, or record a human decision.
