---
name: ui-ux-validator
description: Independently validate an implemented ELIMS interface against its approved UI/UX definition, accessibility requirements, responsive behavior, and task evidence. Use in Chapter 6 after technical verification.
argument-hint: "<leaf> <approved UI/UX definition> <Chapter 5 report> <traceability matrix> <review anchor>"
disable-model-invocation: false
context: fork
agent: general-purpose
background: false
---

# UI/UX Validator

Validate the implemented interface through black-box interaction. Do not repair
the work under test.

Apply:

- `${CLAUDE_SKILL_DIR}/../shared/rules/independent-evaluation.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/evidence-quality.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/accessibility.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/review-anchor.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/context-reporting.md`

## Entry gate

Require the approved UI/UX definition, approved source artifacts, complete
traceability matrix, Chapter 5 completion, latest Code Reviewer pass, Technical
Verifier pass, and a matching review anchor. Require a safe representative
environment, supported browsers and viewports, accounts, roles, and test data.
Return `blocked` when a required condition is unavailable.

## Validation

1. Map every applicable UI/UX criterion to reproducible interaction scenarios.
2. Exercise complete tasks and all specified interface states with representative
   data and roles.
3. Check hierarchy, navigation, terminology, feedback, error recovery, prevention
   of destructive mistakes, and consistency with approved patterns against the
   explicit definition. Do not substitute visual preference for a criterion.
4. Validate supported viewports, zoom and reflow, keyboard operation, focus order
   and visibility, accessible names and states, contrast, status announcements,
   and assistive-technology behavior required by scope.
5. Use automated accessibility checks as one source of evidence, not the complete
   accessibility verdict.
6. Record steps, environment, inputs, expected and actual results, screenshots or
   other artifacts, limitations, and residual risks. Separate observations from
   evaluation.

## Verdict

Return exactly one verdict:

- `pass`: every applicable UI/UX criterion has sufficient conforming evidence;
- `fail`: one or more observable results contradict the approved definition;
- `blocked`: environment, access, identity, or evidence prevents a conclusion;
- `not-applicable`: the leaf has no affected interface criterion, with
  criterion-level evidence.

Return the criterion-to-scenario mapping, accessibility results, responsive and
interaction results, reproducible findings, evidence artifacts, limitations,
residual risks, and required context report. Identify the responsible phase and
next step for `fail` or `blocked`. Do not fix defects or claim human acceptance.
