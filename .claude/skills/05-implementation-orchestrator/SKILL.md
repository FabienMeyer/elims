---
name: implementation-orchestrator
description: Orchestrate one approved ELIMS leaf issue through TDD, Green implementation, refactoring, independent code review, correction loops, and implementation traceability.
argument-hint: "<approved leaf issue path or identifier> <approved PRD path> <approved specification path> <approved ADR or assessment path>"
disable-model-invocation: true
model: sonnet
---

# Implementation Orchestrator

Deliver the Chapter 5 implementation for one approved leaf issue. Coordinate
dedicated phase skills, own gates and correction routing, and finish only when
independent code review passes. Do not perform Chapter 6 verification or
validation, Chapter 7 documentation review, or Chapter 8 human acceptance.

Read `docs/contributing/issues-and-branches.md` before creating or validating a
work branch. Use the approved leaf's issue number, primary scope, and type to
apply the canonical branch convention. Do not create a branch for a tracking
issue or unapproved work.

Work in one dedicated Git worktree per leaf, on the leaf's work branch. The
AFK launcher creates it under `<repository>-worktrees/`. In an interactive
session, create it with `git worktree add -b <branch> <path> origin/main` or
reuse the leaf's existing worktree. Do not implement in a checkout that
contains changes unrelated to the leaf: they enter the diff under review and
the review anchor. If you find such changes at start, return
`implementation-blocked` and name them. Use the fork point of the work branch
from the default branch as the review-anchor base, and record it as
`base_commit` in the traceability matrix.

## Entry gate

Use `$ARGUMENTS` to locate the leaf issue and its approved PRD, specification,
and ADR or no-ADR assessment. Require:

1. Human approval of the leaf issue and source product package.
2. Product Reviewer `pass` for that exact package.
3. Issue Reviewer `pass` for the exact hierarchy containing the leaf.
4. No unresolved product, behavioral, or architectural decision.
5. Observable completion criteria small enough for one focused change.
6. The exact leaf issue has the authoritative `rdy-to-implement` label.

Verify the label on the authoritative GitHub issue through a read-only tracker
query. Local issue files, plan metadata, and planned labels are not evidence.
Do not infer it or add it. Return `implementation-blocked` when a gate is missing.

## Traceability ownership

Create one bidirectional implementation traceability matrix from
`${CLAUDE_SKILL_DIR}/../shared/templates/traceability-matrix-template.md` at
`docs/product/traceability/<leaf issue identifier>.md`. If the file exists,
continue it; do not create a second matrix for the same leaf. For every
in-scope criterion record the approved behavior, architecture constraints,
Red evidence, production locations, Green evidence, refactor verdict,
code-review verdict, and required documentation, configuration, migration,
security, privacy, or operational effects.

Every production change must map to an approved criterion, accepted
architecture constraint, or necessary technical support. Record each phase
verdict with the anchor it examined in the Phase verdicts table. The anchor
excludes `docs/product/traceability/`, so updating the matrix does not
invalidate a pass. Commit the matrix with the work branch and preserve it for
Chapters 6–8. Pass the matrix path to every later phase.

## Context isolation

Invoke `/tdd-engineer`, `/implementation-engineer`, `/refactor-engineer`, and
`/code-reviewer` sequentially in fresh contexts. Give independent review only
approved artifacts, repository guidance, the final diff, the review anchor, and
the matrix path with the instruction to read only its Mapping and Reverse
mapping sections. Withhold implementation rationale and prior conclusions.

Follow `${CLAUDE_SKILL_DIR}/../shared/rules/review-anchor.md`. Record the review
anchor in the matrix before invoking `/code-reviewer`, and again after every
production or test change.

## Workflow

### 0. Start

When the issue Project status is `Ready to implement`, plan the transition to
`Implementation` with `${CLAUDE_SKILL_DIR}/../06-verification-and-validation-orchestrator/scripts/github_project.py`
(`--from-status "Ready to implement" --to Implementation`). Run it without
`--apply` first. Apply it only with explicit authorization. If the status is
already `Implementation`, continue. If the status is any other value, return
`implementation-blocked`. After a Chapter 6 or Chapter 8 rejection, the
responsible chapter moves the issue back to `Implementation`.

### 1. Red

Invoke `/tdd-engineer` with the approved artifacts.

- `red`: record criterion-to-test mappings and expected failures. Before any
  production change, run
  `uv run python ${CLAUDE_SKILL_DIR}/../shared/scripts/red_state.py record --base <base> --leaf <leaf>`.
  Record its `tree`, `ref`, and the exact focused test command in the matrix
  Red row. Exit code 3 means that the Red phase changed non-test files: route
  the result back to `/tdd-engineer` and do not start Green.
- `already-implemented`: stop for a human decision.
- `blocked`: resolve the reported gate or stop.

### 2. Green

Invoke `/implementation-engineer` only after valid Red evidence.

- `green`: record production mappings and focused evidence.
- `blocked`: resolve the reported gap or stop.

### 3. Refactor

Invoke `/refactor-engineer` only after Green passes.

- `pass` or `no-change`: record rationale and behavior-preservation evidence.
- `blocked`: resolve the reported gap or stop.

### 4. Code review

Invoke `/code-reviewer` against the complete current diff.

- `pass`: Chapter 5 is complete for that exact diff.
- `findings`: route required findings to `/implementation-engineer`; repeat
  affected refactor checks and independent review.
- `blocked`: resolve the evidence or environment gap or stop.

Route missing or contradictory product and architecture decisions back to the
responsible shaper. Any production correction invalidates the prior review.

## Completion report

Return `implementation-complete` only after the latest `/code-reviewer` passes
the exact final diff. Report the review anchor that received the pass, changed files, the traceability matrix, Red and
Green evidence, refactor evidence, review findings and resolutions, skipped
checks, environmental limitations, and residual risks.

The next eligible command is
`/verification-and-validation-orchestrator` with the approved artifacts,
Chapter 5 report, and traceability matrix.

Do not open or ready a pull request, mutate Project status (except the
authorized start transition above), merge, deploy,
close issues, or claim technical verification, system validation,
documentation completeness, or human acceptance.
