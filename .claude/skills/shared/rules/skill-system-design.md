# Skill system design

Centralize identity-critical standards: rules whose independent interpretation
could make delivery stages disagree. Keep role behavior and contextual judgment
local to each skill.

Create or retain a shared rule only when all of these statements are true:

- The rule is authoritative across more than one delivery role.
- Different interpretations could produce incompatible gates, evidence, or
  verdicts.
- Every referencing skill needs the complete invariant.
- The invariant can change as one unit without forcing unrelated role behavior
  to change.

Repetition is a reason to inspect instructions, not sufficient reason to share
them. Keep entry gates, workflows, questions, tools, verdicts, output contracts,
and correction routing in the responsible skill unless their identity must be
the same across roles.
