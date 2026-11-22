# Product definition skills

The project uses five Claude Code skills to shape, independently review, and decompose product work.

## Workflow

1. `/idea-shaper <idea>` questions the human and writes a draft PRD.
2. After human PRD approval, `/specification-shaper <prd-path>` questions the human and writes a proposed behavioral specification.
3. After human specification approval, `/architecture-shaper <prd-path> <specification-path>` writes a proposed ADR or a no-ADR assessment.
4. After human architecture approval, `/product-reviewer <prd-path> <specification-path> <decision-path>` performs a fresh-context, read-only review.
5. A human gives final approval only after the independent review passes.
6. `/issue-shaper <prd-path> <specification-path> <decision-path> [review-path]` creates a traceable hierarchy of sized issue drafts.

The reviewer can request revision or restart of the PRD, specification, architecture result, or both the specification and architecture. Revised artifacts must pass independent review again.

## Boundaries

- Shapers ask questions and write only their assigned artifact.
- No skill approves its own output.
- Product Reviewer starts without shaping-conversation context and does not edit files.
- Issue Shaper creates tracking issues and independently verifiable leaf issues only after final product-package approval.
- All documents use ASD-STE100-assisted language. Model output is not certified ASD-STE100 compliance.
