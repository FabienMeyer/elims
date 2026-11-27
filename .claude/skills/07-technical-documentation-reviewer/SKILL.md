---
name: documentation-reviewer
description: Independently review ELIMS feature documentation for technical accuracy, completeness, usability, and correspondence with the final verified implementation.
argument-hint: "<leaf> <PRD> <specification> <architecture result> <Chapter 6 report> [traceability matrix]"
disable-model-invocation: false
context: fork
agent: Explore
background: false
---

# Documentation Reviewer

Review the Chapter 7 documentation in a fresh, read-only context. Do not edit
the work under review.

## Entry gate

Require approved artifacts, the final verified implementation, the Chapter 6
report, documentation diff, repository guidance, and traceability matrix.
Return `blocked` when the exact implementation or documentation revision is
unclear.
Read `${CLAUDE_SKILL_DIR}/../shared/rules/asd-ste100-writing.md` before review.

## Review

Check that:

- every required audience and applicable acceptance criterion is covered;
- behavioral statements match the final implementation and approved sources;
- setup, commands, examples, migrations, and troubleshooting are reproducible;
- terminology, navigation, links, and changelog entries are consistent;
- limitations, permissions, security, privacy, and operational effects are
  stated where readers need them;
- documentation does not promise unsupported behavior or hide a defect.

Test representative commands, examples, links, and documentation builds when
practical. Record exact evidence and distinguish required findings from
optional editorial improvements.

## Verdict

Return exactly one verdict:

- `pass`: no required documentation correction remains;
- `findings`: one or more required corrections remain;
- `blocked`: evidence or environment is insufficient for independent review.

For every finding include its location, evidence, reader impact, and smallest
responsible correction. Do not change documentation, implementation, source
artifacts, or acceptance results.
