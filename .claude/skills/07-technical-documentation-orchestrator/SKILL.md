---
name: technical-documentation-orchestrator
description: Coordinate reader-facing technical documentation and independent documentation review for one verified and agent-validated ELIMS leaf issue.
argument-hint: "<leaf> <PRD> <specification> <architecture result> [UI/UX definition] <Chapter 6 report> [traceability matrix]"
disable-model-invocation: true
model: sonnet
---

# Technical Documentation Orchestrator

Run Chapter 7 after Chapter 6 passes. Own documentation scope, independent
review loops, traceability, and the handoff to human acceptance.

## Entry gate

Require approved source artifacts, the final implementation state, Chapter 6
`verified-and-agent-validated` for that exact diff, a traceability matrix, and
the draft pull request when one is used. Return `documentation-blocked` when a
gate or required documentation environment is unavailable.

Documentation needed for technical operation—schemas, inline help,
configuration definitions, migrations, and generated interfaces—belongs to
implementation and must already exist. Chapter 7 produces and reviews the
complete reader-facing documentation set.

## Workflow

1. Derive the required audiences and deliverables from the approved artifacts,
   implementation effects, and repository documentation structure.
2. Invoke `/technical-writer` with the final implementation and matrix.
3. Invoke `/documentation-reviewer` in a fresh, read-only context.
4. Route `findings` to a new writer context, then repeat independent review.
5. If documentation exposes incorrect or undocumented product behavior, route
   it to the responsible earlier chapter rather than documenting the defect.
6. Add documentation evidence to every applicable matrix row.
7. Confirm the documentation changes belong to the existing draft pull
   request and correspond to the verified implementation diff. Compute the
   final review anchor (`${CLAUDE_SKILL_DIR}/../shared/rules/review-anchor.md`) and
   confirm that `git diff --name-only <Chapter 6 tree> <final tree>` lists
   only documentation files. Report both anchors.

## Completion report

Return `documentation-complete` only when `/technical-writer` returns
`documented` or justified `not-applicable` and `/documentation-reviewer`
returns `pass` for the final documentation diff. Report deliverables,
criterion mappings, review findings and resolutions, commands and examples
tested, limitations, and residual risks.

The next eligible command is `/human-acceptance-orchestrator`.

Do not change product behavior, mark the pull request ready, merge, deploy,
close issues, or claim human acceptance.
