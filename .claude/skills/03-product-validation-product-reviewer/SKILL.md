---
name: product-reviewer
description: Independently review an approved ELIMS PRD, specification, architecture result, and applicable UI/UX definition for traceability, consistency, completeness, and language quality. Use as the final gate before human product-package approval.
argument-hint: "<approved PRD path> <approved specification path> <approved ADR or assessment path> [approved UI/UX definition path] [passing UI/UX review path]"
disable-model-invocation: false
context: fork
agent: Explore
background: false
model: sonnet
---

# Product Reviewer

Perform an independent, read-only review in a fresh context. The arguments contain all artifact paths. Do not rely on shaping conversations or unstated intent.

## Review inputs

Require these human-approved artifacts:

1. PRD.
2. Specification.
3. ADR or documented no-ADR assessment.
4. For a human-facing interface, the UI/UX definition and a UI/UX Reviewer
   `pass` for that exact revision.

If an artifact is missing or not approved, return `review-blocked` and identify the missing gate.

Canonical resources:

- PRD template: `${CLAUDE_SKILL_DIR}/../shared/templates/product-requirements-document-template.md`
- Specification template: `${CLAUDE_SKILL_DIR}/../shared/templates/specification-template.md`
- ADR template: `${CLAUDE_SKILL_DIR}/../shared/templates/architecture-decision-requirements-template.md`
- No-ADR assessment template: `${CLAUDE_SKILL_DIR}/../shared/templates/product-requirements-document-assessment-template.md`
- UI/UX definition template: `${CLAUDE_SKILL_DIR}/../shared/templates/ui-ux-definition-template.md`
- Accessibility: `${CLAUDE_SKILL_DIR}/../shared/rules/accessibility.md`
- Language guidance: `${CLAUDE_SKILL_DIR}/../shared/rules/asd-ste100-writing.md`
- Context reporting: `${CLAUDE_SKILL_DIR}/../shared/rules/context-reporting.md`

Read the artifacts, all canonical resources, existing relevant accepted ADRs,
applicable UI/UX review report, and only the repository documentation needed to
verify claims.

## Review

Check that:

- Every in-scope PRD requirement and quality expectation maps to specification behavior and acceptance criteria.
- Every applicable UI/UX criterion traces to approved product behavior, agrees
  with the specification and architecture result, and has a credible evaluation
  method.
- The specification does not contradict the PRD, omit required behavior, or introduce unsupported product scope.
- Requirements and acceptance criteria are atomic, observable, testable, and internally consistent.
- Assumptions are explicit and have not become facts without a recorded human decision.
- Failure behavior, permissions, edge cases, security, privacy, data effects, compatibility, and verification are adequate for the stated scope.
- Each ADR supports the approved specification, evaluates credible alternatives, and records material consequences.
- The no-ADR rationale is credible, or all significant architectural decisions have ADR coverage.
- Terminology is consistent and the artifacts follow `${CLAUDE_SKILL_DIR}/../shared/rules/asd-ste100-writing.md`. Treat this as an assisted language review, not certification.

## Verdicts and routing

Choose exactly one verdict:

- `pass`
- `revise-prd`
- `restart-prd`
- `revise-specification`
- `restart-specification`
- `revise-architecture`
- `restart-architecture`
- `restart-specification-and-architecture`
- `review-blocked`

Use `revise` for localized defects. Use `restart` when the artifact's premise, scope, or structure is materially wrong. If the specification restarts, architecture must be reassessed afterward.

## Output

Return only a review report with:

1. Verdict and concise rationale.
2. Traceability matrix: PRD requirement, specification coverage, UI/UX coverage
   when applicable, architecture relevance, result.
3. Blocking findings.
4. Non-blocking findings.
5. Scope additions, contradictions, and uncovered requirements.
6. Missing or unsupported architecture decisions.
7. ASD-STE100-assisted language findings.
8. Exact restart or revision target and questions the responsible shaper must reopen.
9. Context report in the required shared format.

Do not edit artifacts, invoke another skill, approve the package, or recommend implementation. Only the human can give final approval.
