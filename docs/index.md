# ELIMS documentation

This site is the system-level documentation portal for ELIMS. Backend, frontend, and Python package documentation is owned beside the code and included here during the build.

## Documentation ownership

- Product direction and cross-component specifications live in this root documentation.
- Backend behavior is canonical in `backend/docs/`.
- Frontend behavior is canonical in `frontend/docs/`.
- Reusable package behavior is canonical in `packages/<package>/docs/`.
- System-wide architecture decisions live in `docs/decisions/`; component decisions live with their component.

Start with the [product vision](product/vision.md), review the [architecture](architecture.md), or browse the [components](components/index.md).

## Quick start

```bash
cp .env.example .env
docker compose up --build
```
