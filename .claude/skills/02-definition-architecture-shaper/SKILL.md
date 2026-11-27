---
name: architecture-shaper
description: Assess an approved ELIMS specification for significant architectural decisions, question the user about tradeoffs, and write an ADR or a no-ADR assessment. Use before independent product review.
argument-hint: "<approved PRD path> <approved specification path> [approved UI/UX definition path] [existing ADR path]"
disable-model-invocation: true
model: sonnet
---

# Architecture Shaper

Determine whether an approved specification requires an ADR. When it does, shape the decision with the human and write a proposed ADR.

## Entry gate

Use `$ARGUMENTS` to locate the PRD, specification, applicable UI/UX definition,
and optional ADR. Confirm that the PRD and specification are human-approved.
When the specification has a human-facing interface, also require the approved
UI/UX definition or a justified `not-applicable` result. Stop if a required
artifact is not approved.

Canonical resources:

- ADR template: `${CLAUDE_SKILL_DIR}/../shared/templates/architecture-decision-requirements-template.md`
- No-ADR assessment template: `${CLAUDE_SKILL_DIR}/../shared/templates/product-requirements-document-assessment-template.md`
- Language guidance: `${CLAUDE_SKILL_DIR}/../shared/rules/asd-ste100-writing.md`
- Context reporting: `${CLAUDE_SKILL_DIR}/../shared/rules/context-reporting.md`

Read these files, all applicable approved artifacts, existing relevant ADRs,
and only the architecture documentation needed for the decision.

## ADR decision test

An ADR is normally required for a decision that is significant, cross-cutting, costly to reverse, or likely to affect future work. Examples include component boundaries, persistence strategy, protocols, integration patterns, security models, deployment topology, or major dependencies.

Do not create an ADR for routine implementation detail or a decision already governed by an accepted ADR.

## Workflow

1. State each candidate architectural decision and why it is or is not significant.
2. If no ADR is required, question the user about any uncertain classification. After confirmation, write a short assessment under `docs/decisions/assessments/` using `product-requirements-document-assessment-template.md` from the canonical resources.
3. If an ADR is required, question the user about context, constraints, decision drivers, viable alternatives, tradeoffs, consequences, reversibility, compatibility, security, operations, migration, and verification.
4. Do not select an alternative when the human has not made the material decision.
5. Propose an ADR identifier, title, and path under `docs/decisions/proposed/`.
6. Write the ADR with `status: proposed`. Do not accept it or move it unless a human explicitly approves it.
7. Report unresolved decisions and the next gate: human approval of the ADR or no-ADR assessment.
8. Append the required context report to the task result and each ADR or assessment created or revised.

## Boundaries

- Do not change product scope or silently compensate for an incomplete specification.
- Return product ambiguity to Idea Shaper and behavioral ambiguity to Specification Shaper.
- Do not create implementation plans, tasks, estimates, code, tests, or configuration.
- Do not approve your own architecture result.

## Language

Apply `${CLAUDE_SKILL_DIR}/../shared/rules/asd-ste100-writing.md`. Keep alternatives and consequences precise without removing necessary technical terms.

## Handoff

After human approval, invoke `/ui-ux-reviewer` for an applicable approved UI/UX
definition. After that review passes, invoke `/product-reviewer` with the
approved PRD, specification, ADR or architecture-assessment, UI/UX definition,
and UI/UX review paths. Omit the UI/UX inputs only with a justified
`not-applicable` result.
