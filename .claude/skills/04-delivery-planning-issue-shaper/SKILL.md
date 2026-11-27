---
name: issue-shaper
description: Question the user about delivery boundaries and turn an approved ELIMS product package, including applicable UI/UX definition, into a traceable hierarchy of small tracking and implementation issues. Use only after independent product review and final human approval.
argument-hint: "<approved PRD path> <approved specification path> <approved ADR or assessment path> [approved UI/UX definition path] [review report path]"
disable-model-invocation: true
model: sonnet
---

# Issue Shaper

Turn a final-approved product package into a reviewable issue hierarchy. Do not implement the work.

## Entry gate

Use `$ARGUMENTS` to locate the PRD, specification, architecture result,
applicable UI/UX definition, and optional product-review report.

Before planning issues, confirm that:

1. The PRD, specification, and ADR or no-ADR assessment have human-approved status.
2. Product Reviewer returned `pass` after its most recent review.
3. A human gave final approval to the complete product package.
4. For a human-facing interface, UI/UX Reviewer passed the exact approved UI/UX
   definition included in that package.

If evidence is missing, stop with `issue-planning-blocked` and identify the missing gate. Do not infer approval from document completeness.

## Canonical resources

- Issue-plan template: `${CLAUDE_SKILL_DIR}/../shared/templates/issue-plan-template.md`
- Language guidance: `${CLAUDE_SKILL_DIR}/../shared/rules/asd-ste100-writing.md`
- Context reporting: `${CLAUDE_SKILL_DIR}/../shared/rules/context-reporting.md`
- Issue, label, and branch conventions: `docs/contributing/issues-and-branches.md`

Read all canonical resources and approved input artifacts before questioning the user.

## Workflow

1. Build a list of every approved specification and applicable UI/UX acceptance
   criterion and required verification outcome.
2. Question the user about delivery boundaries, sequencing constraints, release constraints, ownership boundaries, migration order, rollout needs, and issue-tracker conventions that materially affect decomposition.
3. Propose one main tracking issue for the approved product outcome. The main issue must not contain implementation work.
4. Decompose the work into vertical, independently verifiable leaf issues. Add a tracking child only when its work must be decomposed into a second level of leaf issues.
5. Map every specification and applicable UI/UX acceptance criterion to one
   primary leaf issue. Record supporting issues where necessary. Report
   duplicates and uncovered criteria.
6. Identify dependencies and order constraints. Do not create dependency cycles.
7. Apply the size gate to every leaf issue. Split any issue that fails before presenting the plan.
8. Declare `rdy-to-implement` as a planned label on every implementation leaf intended for publication. Leave it off tracking-only, blocked, and unresolved issues. A planned label in the local plan does not make a leaf eligible; eligibility begins only when `/github-issue-publisher` applies the label to the authoritative GitHub issue after Issue Reviewer `pass` and explicit human approval.
   Apply the canonical title and label conventions to every issue.
9. Write the proposed plan under `docs/product/issues/proposed/` from `issue-plan-template.md` after the user confirms the decomposition is ready for a draft.
10. Present the hierarchy, traceability matrix, dependencies, labels, and all issue bodies for review.
11. Before the fresh-context handoff, apply the context-resilience rule and
    confirm that the proposed plan and approved source paths contain the complete
    review checkpoint. Invoke `/issue-reviewer` with those identified revisions.
12. Resolve `revise-issue-plan` findings and repeat independent review until it passes. Route source-artifact findings to the identified shaper.
13. Present the passing review report and proposed plan for human approval.
14. After explicit human approval, give the user the command `/github-issue-publisher <approved-plan> <passing-review-report> <owner/repository>` to publish the approved hierarchy. Include the verified repository identity.
15. Record the returned local-identifier-to-GitHub-URL mapping in the issue plan. For `partial` or `blocked`, stop and present the exact reconciliation or authorization required; do not continue to implementation.
16. Append the required context report to the task result and each issue plan created or revised.

## Hierarchy rules

Use no more than two levels below the main issue:

```text
Main issue — tracking only
|-- Leaf implementation issue
|-- Child tracking issue
|   |-- Leaf implementation issue
|   `-- Leaf implementation issue
`-- Leaf implementation issue
```

- A non-leaf issue is tracking-only and closes when all its children close.
- A leaf issue contains implementation and verification work.
- Do not create sub-issues merely to separate frontend, backend, database, tests, or documentation when those parts cannot deliver value independently.
- Prefer vertical slices that produce observable behavior.
- Use checklists inside a leaf issue for small internal steps. Do not create sub-issues for trivial tasks.

## Leaf issue size gate

A leaf issue passes only when all statements are true:

- It produces one clear outcome.
- It maps to a small, explicit set of acceptance criteria.
- It can be completed in one focused pull request under normal conditions.
- It can be verified independently.
- It has no unresolved product, behavioral, or architectural decision.
- It has one clear ownership boundary.
- It does not combine unrelated components or migration stages.
- It can be reverted or deferred without invalidating unrelated completed issues.

If a leaf fails a statement, split it by user journey, business rule, state transition, failure mode, migration stage, or independently releasable capability. Do not split only by technical layer unless the layer is independently deliverable.

## Issue content

Every leaf issue must include:

- Outcome and value.
- Parent issue.
- PRD requirements and specification acceptance criteria addressed.
- Included and excluded scope.
- Dependencies.
- Implementation constraints from accepted ADRs.
- Observable completion criteria.
- Verification evidence required.
- Planned labels. Use `rdy-to-implement` for implementation leaves intended to become eligible after review, human approval, and verified GitHub publication. Never use it for tracking issues.
- Documentation, migration, security, privacy, and rollout effects when applicable.

Do not copy the entire PRD or specification into an issue. Use stable identifiers and links.

## Boundaries

- Do not reopen approved product or architecture decisions during decomposition. If decomposition exposes a real contradiction or missing decision, stop and route the package back to the appropriate shaper and Product Reviewer.
- Do not estimate duration unless the user explicitly requests estimation and supplies the team's estimation method.
- Do not assign people, priorities, milestones, or releases without human input.
- Do not write code, modify implementation files, approve the issue plan, or start implementation. GitHub publication is permitted only through `/github-issue-publisher` after the review and human-approval gates pass.

## Language

Apply `${CLAUDE_SKILL_DIR}/../shared/rules/asd-ste100-writing.md`. Keep issue titles concise and make completion criteria atomic and testable. Label the result STE-assisted, not certified ASD-STE100 compliance.

## Completion

The skill is complete when the human has a traceable, dependency-aware issue plan in which every leaf passes the size gate, Issue Reviewer returned `pass`, the human approved the plan, and GitHub publication returned `published` or `already-published`. A leaf becomes eligible for implementation only when its authoritative GitHub issue has the exact `rdy-to-implement` label.

After a leaf issue and its source product package receive explicit human approval, hand the user `/implementation-orchestrator` with the approved leaf issue, PRD, specification, and ADR or architecture-assessment paths.
