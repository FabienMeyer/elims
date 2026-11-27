# Design system

Reusable visual primitives live in `src/components/ui`; persistent structural components live in `src/components/layout`. Domain behavior belongs in features rather than generic UI primitives.

`src/styles.css` defines one dark theme. Its colors are custom properties on `:root` (`--color-surface`, `--color-surface-raised`, `--color-border`, `--color-text`), and `color-scheme: dark` makes browser-drawn controls and scrollbars match. Use the properties rather than literal colors. Layout styles go on classes such as `.shell-header` and `.shell-main`; only base typography targets bare elements. A light theme would be a new pattern and needs its own design decision.

New patterns must document states, responsive behavior, keyboard behavior, validation feedback, and any generated-asset provenance.
