# Context reporting

Add a context report to the end of every task result and every Markdown artifact
that the skill creates or revises. If the artifact has a required final section,
place the context report after that section.

Use this format:

```yaml
context-report:
  input-files: <number of source files read>
  input-bytes: <total bytes of those files, when measurable>
  estimated-input-tokens: <input-bytes divided by 4, rounded up>
  output-bytes: <bytes in the generated content, excluding this report, when measurable>
  estimated-output-tokens: <output-bytes divided by 4, rounded up>
  exact-context-used: unavailable
```

This report describes measurable file inputs and generated outputs. It is not a
measure of total runtime context, remaining context capacity, or model attention.
Do not derive a context-pressure warning or continuation decision from these byte
or token estimates. Apply `context-resilience.md` when continuity becomes
uncertain.

For a report embedded in an artifact, `output-bytes` excludes the context-report
block itself to avoid a self-referential file-size calculation. For a task
result that also writes or revises files, include one `output-file` entry for
each completed artifact with its path, final byte count (including the embedded
report), and estimated token count.
Do not count the same input file more than once. Do not include files merely
discovered or listed but not read.

Use exact byte counts when tools expose the content or file size. If a value
cannot be measured, use `unavailable`; do not invent a value. Token counts are
estimates, not tokenizer results. The runtime context can also contain system
instructions, conversation history, and tool results that this report cannot
measure, so always keep `exact-context-used: unavailable` unless the runtime
directly supplies an authoritative value.
