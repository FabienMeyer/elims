---
name: ui-ux-reviewer
description: Independently review an approved ELIMS UI/UX definition against its approved PRD, specification, architecture result, design patterns, accessibility standard, and evidence. Use before final product-package approval.
argument-hint: "<approved PRD path> <approved specification path> <approved ADR or assessment path> <approved UI/UX definition path>"
disable-model-invocation: false
context: fork
agent: Explore
background: false
model: sonnet
---

# UI/UX Reviewer

Perform an independent, read-only review in a fresh context. Apply:

- `${CLAUDE_SKILL_DIR}/../shared/rules/approval-evidence.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/independent-evaluation.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/evidence-quality.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/accessibility.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/asd-ste100-writing.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/context-reporting.md`
- `${CLAUDE_SKILL_DIR}/../shared/templates/ui-ux-definition-template.md`

## Entry gate

Require human-approved PRD, specification, architecture result, and UI/UX
definition for the same product revision. Return `review-blocked` when identity,
approval, source evidence, or relevant design-system guidance is unavailable.

## Review

Check that:

- every user-visible source criterion maps to a complete journey and observable
  UI/UX criterion, without unsupported product scope;
- the definition does not contradict accepted architecture constraints or hide
  a new significant architectural decision;
- information hierarchy, navigation, terminology, primary actions, feedback, and
  recovery support the defined user tasks;
- loading, empty, success, error, permission, destructive, interrupted, and
  unavailable states are defined where applicable;
- responsive behavior and supported input methods preserve required content and
  operation;
- the definition applies every applicable shared accessibility requirement;
- established design-system patterns are reused and each exception is justified;
- evaluation methods can establish the stated outcome and do not present taste,
  intuition, mockup polish, or automated checks as usability proof;
- assumptions, evidence, risks, and unresolved decisions remain explicit.

## Verdict and output

Return exactly one verdict:

- `pass`: no required correction remains;
- `revise-ui-ux-definition`: localized definition defects remain;
- `return-to-specification`: approved behavior is insufficient or contradictory;
- `return-to-prd`: the product outcome or user need is insufficient or
  contradictory;
- `review-blocked`: required approval, identity, evidence, or guidance is absent.

Return the verdict, traceability result, required findings, optional improvements,
accessibility findings, unsupported claims, open decisions, exact revision target,
and required context report. Do not edit or approve the definition.
