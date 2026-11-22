# System specifications

Use this area for changes that affect multiple components or the whole product. A change isolated to one component belongs in that component's `docs/specifications/` directory.

## Lifecycle

1. Use `/specification-shaper` to create a document in `proposed/` from the canonical template in `.claude/skills/shared/templates/`.
2. Resolve open business and technical questions.
3. Record human approval and move it to `approved/`.
4. Implement and verify against its acceptance criteria.
5. Add evidence and move it to `implemented/`.
6. Move replaced specifications to `superseded/` and link their successor.

Directory moves are reviewable state transitions; an agent must not approve its own specification.
