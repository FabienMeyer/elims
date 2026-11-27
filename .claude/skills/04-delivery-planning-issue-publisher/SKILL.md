---
name: github-issue-publisher
description: Publish a passing, human-approved ELIMS issue plan to GitHub with native sub-issues, exact labels, and idempotent stable identifiers.
argument-hint: "<approved issue plan path> <passing issue-review report path> <owner/repository>"
disable-model-invocation: true
context: fork
agent: general-purpose
background: false
---

# GitHub Issue Publisher

Publish an approved ELIMS issue hierarchy to GitHub. This skill mutates only issues and the required workflow label in the explicitly supplied repository.

Read `${CLAUDE_SKILL_DIR}/../shared/rules/context-reporting.md` before publication and append its context report to every task result. This skill never edits local files. Issue Shaper records the returned mapping in the issue plan.
Read `docs/contributing/issues-and-branches.md` and reject publication when an approved title or label set does not follow its canonical convention.

## Entry gate

Use `$ARGUMENTS` to locate the issue plan, passing Issue Reviewer report, and exact `owner/repository` target. Require:

1. Human-approved PRD, specification, and architecture result.
2. Product Reviewer `pass` for that exact product package.
3. Issue Reviewer `pass` for the exact issue plan revision.
4. Explicit human approval of the complete issue plan after that review.
5. One main tracking issue and complete definitions for every child tracking issue and leaf.
6. Every issue has a unique stable identifier.
7. Every approved implementation leaf declares `rdy-to-implement` in its planned labels; no tracking issue declares it.
8. GitHub CLI is installed, authenticated, and authorized for the target repository.

Return `blocked` when a gate, target, permission, or required issue definition is missing. Do not infer the repository from an unrelated remote or publish before human approval.

## Safety and idempotency

Use the bundled scripts in `scripts/` for label reconciliation and stable-ID
issue lookup or upsert. Run them without `--apply` to inspect or report the
planned mutation. Add `--apply` only after the complete operation list has been
reported and the mutation is authorized. Do not copy credentials into script
arguments or local files.

Before creating an issue, search the target repository for its stable marker:

```text
<!-- elims-issue-id: ISSUE-001 -->
```

Use the issue-plan identifier for the main issue and each issue's own identifier for descendants. If exactly one matching issue exists, reconcile it instead of creating a duplicate. If several issues use the same marker, return `blocked` and report the conflict.

Before mutation, build and report the complete intended operation list. Then:

- create or update only issues in the approved plan;
- preserve approved titles, bodies, labels, and parent relationships;
- build native hierarchy through the GitHub REST sub-issues endpoint (`POST /repos/{owner}/{repo}/issues/{parent}/sub_issues` with the child's numeric `sub_issue_id`), which `scripts/github_issue.py --parent` wraps; `gh issue create` and `gh issue edit` have no parent option. Never reparent an issue that already has a different parent; return `blocked` instead;
- ensure the `rdy-to-implement` label exists, creating only that workflow label when absent;
- assign `rdy-to-implement` only to approved leaf implementation issues;
- never add it to the main issue, child tracking issues, blocked leaves, or unresolved work;
- do not assign people, milestones, projects, issue types, or extra labels unless the approved plan explicitly supplies them;
- do not close, delete, transfer, or reorder unrelated issues.

If a command fails after some mutations succeed, stop. Return `partial` with the exact completed operations and remaining reconciliation steps. Never retry creation blindly.

## Publication order

1. Verify authentication, target repository, plan revision, approvals, review verdict, identifiers, labels, and hierarchy.
2. Reconcile stable identifiers against existing GitHub issues.
3. Ensure the `rdy-to-implement` workflow label exists.
4. Create or update the main tracking issue without `rdy-to-implement`.
5. Create or update child tracking issues under their approved parent without `rdy-to-implement`.
6. Create or update approved leaf issues under their approved parent with their declared labels.
7. Verify every title, stable marker, label, open state, and native parent relationship through read-only GitHub queries.
8. Return the mapping from local identifier to GitHub issue number and URL.

## Verdict

Return exactly one verdict:

- `published`: all approved issues and relationships were created or reconciled and verified;
- `already-published`: GitHub already matched the complete approved plan and no mutation was necessary;
- `partial`: some authorized mutations succeeded but publication did not complete;
- `blocked`: no safe mutation could start or a conflict requires human direction.

Return the target repository, plan revision, verdict, operation log, identifier-to-URL mapping, label verification, hierarchy verification, failures, and remaining actions.

End the result with the required context report.

Do not implement issues, modify local artifacts, approve the plan, merge, deploy, or change unrelated GitHub state.
