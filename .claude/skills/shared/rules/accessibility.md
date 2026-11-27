# Interface accessibility

Interface behavior must meet WCAG 2.2 Level AA for applicable web content unless
an approved requirement establishes a stricter standard or documents a justified
exception.

- Every interactive control has a programmatically determinable accessible name,
  role, value, and state where applicable.
- Complete workflows are operable by keyboard, with logical focus order and
  visible focus indication. Focus is not trapped except by an intentional modal
  interaction with an accessible escape path.
- Information, status, and validation do not rely on color, position, shape, or
  sound alone.
- Text and meaningful non-text content meet applicable contrast requirements.
- Structure, headings, landmarks, labels, instructions, errors, and status
  changes expose the relationships needed by assistive technology.
- Layout and operation remain usable at 200% zoom and across approved viewport
  sizes without loss of required content or functionality.
- Motion, timing, drag, pointer target, authentication, and media behavior meet
  applicable WCAG requirements.

Automated checks are necessary but not sufficient. Combine static or Axe results
with keyboard operation, focus behavior, zoom or reflow, and assistive-technology
checks appropriate to the affected journey. Record the rule, method, environment,
expected result, actual result, and evidence for each finding.
