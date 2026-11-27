# Accessibility

Accessibility is part of acceptance, not a later refinement. Components and journeys must use semantic HTML, keyboard-accessible interactions, visible focus, understandable labels, and sufficient contrast.

Announce a changing status through one `role="status"` element that stays mounted, and change only its text. Screen readers often skip a live region that is inserted together with its content. Show the outcome of the latest request, not an earlier success alongside a newer failure.

Unit tests cover component behavior. Playwright and axe checks cover complete supported journeys.
