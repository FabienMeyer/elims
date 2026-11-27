# Context resilience

Do not treat conversation memory, a compacted summary, or an earlier agent's
recollection as authoritative delivery evidence. Preserve continuity through
identified artifacts, exact revisions, review anchors, and persisted phase
results.

## Triggers

Create or refresh a checkpoint before consequential work when any of these
conditions applies:

- the runtime reports compaction, truncation, or authoritative low remaining
  context;
- the role cannot identify the source of a decision, approval, requirement,
  finding, or verdict;
- recalled state conflicts with an artifact or more than one artifact revision
  could be authoritative;
- required evidence exists only in conversation history or transient tool output;
- a long-running orchestration hands work to a fresh context and its inputs are
  not already complete in persisted artifacts.

Do not invent a context percentage or infer remaining capacity from file bytes,
message length, or estimated tokens. The context report measures disclosed file
inputs and outputs; it is not a runtime context-capacity meter.

## Checkpoint

Use an existing traceability matrix, phase report, or approved delivery artifact
when it is the canonical owner. Do not create a parallel source of truth. Record:

- objective, delivery chapter, phase, and responsible role;
- authoritative artifact paths, identifiers, revisions, and approval evidence;
- applicable review anchor, branch, commit, issue, and candidate environment;
- confirmed decisions and latest gate or verdict for each completed phase;
- completed mutations and current external state when applicable;
- open findings, questions, blockers, limitations, and residual risks;
- exact next permitted action and the evidence that the next context must reload.

Separate verified facts from assumptions and unresolved state. Never promote a
summary or checkpoint to approval evidence unless the approval rule explicitly
recognizes the underlying record.

## Recovery

When continuity is uncertain, stop consequential conclusions and mutations.
Start a fresh context when available, reload the checkpoint and its authoritative
sources, verify their identities and revisions, and recompute deterministic state
such as review anchors or current external status. Resume only after contradictions
are resolved. Otherwise return the responsible role's blocked verdict with the
exact evidence needed to continue.
