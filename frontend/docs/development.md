# Frontend development

Use Node.js 24. `.nvmrc` pins the major version for CI and version managers, `package.json` declares it in `engines`, and the Docker build stage uses the same major version. Change all three together.

From `frontend/`:

```bash
npm ci
npm run lint
npm run test
npm run build
```

`npm run build` type-checks three TypeScript projects before bundling. They share `tsconfig.base.json`, which enables `strict` and `noUncheckedIndexedAccess`, so indexing an array or record yields a possibly `undefined` value.

- `tsconfig.app.json` checks `src` with browser types only, so Node and test globals are errors in application code.
- `tsconfig.test.json` checks `tests` with Node and Testing Library matcher types.
- `tsconfig.node.json` checks `vite.config.ts` and `playwright.config.ts`.

Run the standalone documentation from the same directory with `uv run mkdocs build --strict` when the repository documentation dependencies are installed.
