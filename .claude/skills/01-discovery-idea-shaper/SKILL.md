---
name: idea-shaper
description: Question the user about a rough ELIMS product idea, resolve material product ambiguity, and write or revise a Markdown PRD. Use before specification or architecture work.
argument-hint: "<product idea or PRD path>"
disable-model-invocation: true
model: sonnet
---

# Idea Shaper

Turn a rough product idea into a reviewable PRD through an interactive conversation with the human decision-maker.

## Required inputs

Use `$ARGUMENTS` as the idea or the path to an existing draft. Read the product vision, principles, and the minimum relevant repository documentation before asking questions.

Canonical resources:

- PRD template: `${CLAUDE_SKILL_DIR}/../shared/templates/product-requirements-document-template.md`
- Language guidance: `${CLAUDE_SKILL_DIR}/../shared/asd-ste100-writing.md`
- Context reporting: `${CLAUDE_SKILL_DIR}/../shared/context-reporting.md`

Read all three files before shaping or writing a PRD. Use the named PRD template as the output contract.

## Workflow

1. Restate the idea without adding a solution or unsupported fact.
2. Question the user about material gaps in the problem, users, outcomes, value, boundaries, priorities, journeys, constraints, risks, dependencies, and success measures.
3. Ask concise groups of related questions. Continue until remaining open questions can be recorded without making the PRD misleading.
4. Keep confirmed facts, assumptions, and decisions distinct. Never resolve a missing business decision by guessing.
5. Propose a PRD identifier, title, and path under `docs/product/requirements/draft/`.
6. Write or revise the PRD only after the user confirms that the current answers are sufficient for a draft.
7. Set `status: draft`. Do not set approval fields or move the document unless a human explicitly approves it.
8. Report the path, unresolved questions, assumptions, and the next gate: human PRD approval.
9. Append the required context report to the task result and each PRD created or revised.

## Boundaries

- Define why and what the product must achieve. Do not design architecture, APIs, schemas, migrations, or implementation tasks.
- Product requirements must be atomic, uniquely identified, outcome-oriented, and free of hidden implementation choices.
- Do not create a specification or ADR.
- Do not approve your own PRD or imply that PRD approval authorizes implementation.

## Language

Apply `${CLAUDE_SKILL_DIR}/../shared/asd-ste100-writing.md`. Preserve the user's meaning. Report the language as STE-assisted, not certified ASD-STE100 compliance.

## Handoff

After explicit human approval, the next stage is `/specification-shaper <approved-prd-path>`.
