# Frontend configuration

Build-time environment values are validated in `src/app/env.ts`. Client-visible configuration must never contain secrets.

Configuration additions require a documented default, validation, and deployment guidance.

## Production serving

Nginx serves the production build using `nginx.conf` and `nginx-main.conf`. Both Compose files mark the container healthy once `wget --spider http://127.0.0.1:8080/` succeeds inside it, so `docker compose up --wait` also waits for the frontend. Each check adds one line to the Nginx access log.

- Vite fingerprints every file under `/assets/`, so Nginx serves them with `Cache-Control: public, max-age=31536000, immutable`. A missing asset returns 404 rather than the application shell.
- Every other frontend response, including the shell returned for client-side routes, carries `Cache-Control: no-cache`. Browsers revalidate it and pick up a new deployment on the next load.
- Nginx gzip-compresses CSS, JavaScript, and SVG. It does not compress JSON API responses, so secrets and reflected input are never compressed together.
- Every response carries this Content-Security-Policy:

  ```text
  default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'
  ```

The policy allows same-origin resources only. It blocks inline `<script>` and `<style>` elements, `eval`, and third-party origins. Zod runs in `jitless` mode (`src/app/zod-config.ts`) because its schema compiler otherwise probes `new Function`, which the browser reports as a policy violation.

To allow a new source, edit the policy in `nginx.conf` only and record why the source is needed. `vite.config.ts` reads the policy from that file for `vite preview`, so the Playwright suite runs under the same policy as production.
