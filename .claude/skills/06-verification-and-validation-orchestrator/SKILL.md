---
name: verification-and-validation-orchestrator
description: Coordinate independent technical verification and agent system validation for one implementation-complete ELIMS leaf issue, including correction routing and draft pull-request preparation.
argument-hint: "<leaf> <PRD> <specification> <architecture result> <Chapter 5 report> [traceability matrix]"
disable-model-invocation: true
model: sonnet
---

# Verification and Validation Orchestrator

Run Chapter 6 for one implementation-complete leaf issue. Verification asks
whether the feature was built correctly; system validation asks whether the
completed system exhibits the approved observable behavior.

## Entry gate

Require the approved source artifacts, Chapter 5
`implementation-complete`, the latest `/code-reviewer` `pass` for the exact
diff, the review anchor of that pass (see
`${CLAUDE_SKILL_DIR}/../shared/rules/review-anchor.md`), and a complete bidirectional
traceability matrix. Pass the anchor to `/technical-verifier` and
`/system-validator`. Stop with
`verification-and-validation-blocked` when evidence, independence, or the
required environment is unavailable.

## GitHub operations

Use the bundled `scripts/github_project.py` and `scripts/github_pr.py` for
read-only inspection and planned mutations. Run without `--apply` first.
Opening a draft pull request or changing Project status requires explicit
authorization and `--apply`. Never pass credentials to scripts.

## Workflow

1. Move the issue to `Technical verification` when authorized.
2. Invoke `/technical-verifier` in a fresh context.
3. On `fail`, route the exact finding to Chapter 5 and repeat every invalidated
   Chapter 5 check before starting a new verifier context. Move the issue back
   to `Implementation` when authorized.
4. After verifier `pass`, move to `Agent system validation` when authorized.
5. Invoke `/system-validator` in a fresh context.
6. On `fail`, route reproducible defects to the responsible phase. Any code
   correction requires new refactor consideration, code review, technical
   verification, and system validation.
7. Record criterion-level verification and validation evidence in the matrix.
8. After Chapter 6 passes, commit and push the work branch only with explicit
   authorization. Confirm that the pushed head commit has the same review
   anchor as both passes (`review_anchor.py --head <commit>`). Then plan or open
   one draft pull request when authorized and move the issue to
   `Technical documentation`.

Never treat technical verification as a substitute for system validation or
system validation as human acceptance. A justified `not-applicable` system
validation verdict must explain every affected criterion.

## Completion report

Return `verified-and-agent-validated` only when `/technical-verifier` returns
`pass` and `/system-validator` returns `pass` or justified `not-applicable` for
the same final diff and review anchor. Report the anchor, commands, scenario evidence, defects and
resolutions, traceability, draft pull-request state, Project state, skipped
checks, limitations, and residual risks.

The next eligible command is `/technical-documentation-orchestrator`.

Do not mark a pull request ready, merge, deploy, close issues, or claim
documentation completeness or human acceptance.
