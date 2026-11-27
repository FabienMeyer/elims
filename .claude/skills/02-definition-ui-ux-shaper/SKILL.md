---
name: ui-ux-shaper
description: Shape user journeys, interaction behavior, interface states, responsive behavior, and accessibility for an approved ELIMS specification that has a user interface. Use before architecture shaping.
argument-hint: "<approved PRD path> <approved specification path> [existing UI/UX definition path]"
disable-model-invocation: true
model: sonnet
---

# UI/UX Shaper

Turn approved product behavior into a reviewable UI/UX definition through an
interactive conversation with the human decision-maker. Do not create visual
decoration or implementation architecture.

## Entry gate and resources

Require a human-approved PRD and specification for the same revision. Apply:

- `${CLAUDE_SKILL_DIR}/../shared/rules/approval-evidence.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/evidence-quality.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/accessibility.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/asd-ste100-writing.md`
- `${CLAUDE_SKILL_DIR}/../shared/rules/context-reporting.md`
- `${CLAUDE_SKILL_DIR}/../shared/templates/ui-ux-definition-template.md`

Read the approved sources, established frontend design patterns, and only the
repository guidance needed to define the affected experience. If the work has no
human-facing interface, report `not-applicable` with criterion-level evidence;
do not create an empty artifact.

## Workflow

1. Map every user-visible requirement and acceptance criterion to affected users,
   contexts, journeys, tasks, and interface states.
2. Question the user about information hierarchy, navigation, terminology,
   interaction patterns, feedback, loading, empty, success, error, permission,
   destructive, recovery, interruption, and responsive behavior.
3. Identify accessibility needs, assistive-technology interactions, localization,
   device constraints, and usability risks. Apply the shared accessibility rule.
4. Reuse established design-system patterns. Record each necessary exception and
   the evidence or decision that justifies it.
5. Define observable UI/UX acceptance criteria and their evaluation methods. Do
   not use `intuitive`, `clean`, `modern`, or `user-friendly` without measurable
   criteria.
6. Keep a traceability matrix from approved requirements and specification
   criteria to UI/UX criteria.
7. Write the proposal under `docs/product/ui-ux/proposed/` after the user confirms
   that material decisions are resolved. Set `status: proposed`.
8. Report open questions and the next gate: human approval followed by independent
   `/ui-ux-reviewer` review.

## Boundaries

- Define the experience and observable interface behavior. Do not choose frontend
  frameworks, component internals, APIs, persistence, or implementation tasks.
- Do not contradict or silently extend the approved PRD or specification. Return
  behavioral ambiguity to Specification Shaper and product ambiguity to Idea
  Shaper.
- Wireframes or prototypes are evidence aids, not approval by themselves. Label
  their fidelity and unresolved behavior.
- Do not approve the definition or claim usability without evaluation evidence.

Append the required context report to the task result and artifact.
