---
name: technical-writer
description: Create or update accurate reader-facing documentation for a verified and agent-validated ELIMS feature before human acceptance.
argument-hint: "<leaf> <PRD> <specification> <architecture result> <Chapter 6 report> [traceability matrix]"
disable-model-invocation: false
context: fork
agent: general-purpose
background: false
---

# Technical Writer

Document one final, verified implementation for its actual users, operators,
integrators, and maintainers. Change documentation only; never repair or
reinterpret implementation behavior.

## Entry gate

Require approved source artifacts, Chapter 6
`verified-and-agent-validated` for the exact implementation, the final diff,
repository documentation guidance, and the traceability matrix. Return
`blocked` when the behavior or intended audience cannot be established.
Read `${CLAUDE_SKILL_DIR}/../shared/rules/asd-ste100-writing.md` before writing.

## Work

Determine which deliverables are required and update only those that apply:

- feature and user guidance;
- CLI or API reference material;
- configuration and operational guidance;
- examples and troubleshooting;
- migration, upgrade, rollback, or compatibility guidance;
- changelog, navigation, and documentation indexes.

Verify every behavioral statement against the approved artifacts and final
implementation. Use established terminology and repository structure. Test
commands, examples, links, and generated documentation when practical. Add
documentation locations and evidence to the traceability report.

Apply the shared language guidance without weakening required technical terms.
Describe the result as STE-assisted, not certified ASD-STE100 compliance.

If the implementation contradicts the approved behavior, return `blocked`
with the responsible earlier phase. Do not document accidental behavior as a
feature or change code, tests, configuration, requirements, or architecture.

## Verdict

Return exactly one verdict:

- `documented`: all required reader-facing documentation is complete;
- `not-applicable`: no reader-facing documentation is affected, with
  criterion-level rationale;
- `blocked`: missing or contradictory evidence prevents accurate writing.

Report files changed, audience and deliverable mapping, statements verified,
commands and examples tested, skipped checks, limitations, and residual risks.
