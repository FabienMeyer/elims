# Frontend testing

- Biome checks source quality and formatting.
- Vitest and Testing Library verify components and user interactions. Vitest globals are disabled, so import `describe`, `it`, and `expect` from `vitest`. Testing Library cleanup and `vi.stubGlobal` stubs reset after every test.
- Playwright builds the production bundle and serves it with `vite preview` on loopback port 4173, under the Content-Security-Policy from `nginx.conf`. Set `PLAYWRIGHT_PORT` to use another available port. The policy test fails on any browser console error, including a policy violation.
- Axe integration checks accessibility of supported pages.
- `scripts/smoke.py` checks the disposable Docker stack through Nginx: the API behind the proxy, plus caching, compression, the Content-Security-Policy, and 404 handling for the built frontend.

Specifications must identify the smallest relevant checks plus any full-stack evidence required by the risk of the change.
