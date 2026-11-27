---
name: specification-shaper
description: Question the user about observable system behavior and write or revise a specification that traces to an approved ELIMS PRD. Use after PRD approval and before architecture shaping.
argument-hint: "<approved PRD path> [existing specification path]"
disable-model-invocation: true
model: sonnet
---

# Specification Shaper

Turn an approved PRD into a precise, testable behavioral specification through an interactive conversation with the human decision-maker.

## Entry gate

Use `$ARGUMENTS` to locate the PRD and optional existing specification. Confirm that the PRD metadata says `status: approved`. If it is not approved, stop and return the work to Idea Shaper or the human approval gate.

Canonical resources:

- Specification template: `${CLAUDE_SKILL_DIR}/../shared/templates/specification-template.md`
- Language guidance: `${CLAUDE_SKILL_DIR}/../shared/rules/asd-ste100-writing.md`
- Context reporting: `${CLAUDE_SKILL_DIR}/../shared/rules/context-reporting.md`

Read all three files and the minimum repository documentation needed to understand affected behavior.

## Workflow

1. Build a working list of every PRD requirement and quality expectation in scope.
2. Question the user about workflows, state transitions, business rules, inputs, outputs, validation, permissions, failures, edge cases, data effects, migration needs, security, privacy, user-visible behavior, compatibility, and verification.
3. Identify contradictions and underspecified behavior. Do not silently select a behavior or technical solution.
4. Keep a traceability matrix from PRD requirement IDs to specification sections and acceptance criteria.
5. Propose a specification identifier, title, and path under the applicable `specifications/proposed/` directory.
6. Write or revise the specification after the user confirms that the answers are sufficient for a proposal.
7. Set `status: proposed`. Do not set approval fields or move the document unless a human explicitly approves it.
8. Report open questions, uncovered PRD requirements, and the next gate: human specification approval.
9. Append the required context report to the task result and each specification created or revised.

## Boundaries

- Specify externally observable behavior and verification. Do not repeat the PRD's product rationale.
- Do not select architecture, dependencies, vendors, frameworks, or persistence strategies. Record choices that need architecture shaping.
- Do not create an ADR, implementation plan, task list, estimate, code, or test implementation.
- Do not approve your own specification.

## Language

Apply `${CLAUDE_SKILL_DIR}/../shared/rules/asd-ste100-writing.md`, especially to normative requirements and acceptance criteria. Use `must` for mandatory behavior, `should` for recommendations, and `may` for permission. Do not use these terms interchangeably.

## Handoff

After explicit human approval, the next stage is `/architecture-shaper <approved-prd-path> <approved-specification-path>`.
