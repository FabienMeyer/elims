# Backend configuration

Runtime settings are defined in `app/config.py` and supplied through environment variables. `.env.example` documents safe development defaults; production secrets are supplied outside version control.

Configuration additions require validation, documentation, and a secure default.

## Environment

`ENVIRONMENT` is required and must be `development`, `test`, or `production`. The backend and Alembic refuse to start without it, so a deployment that omits it cannot fall back to development, where business routes are open. `production` keeps business routes closed until authentication is integrated, and rejects SQLite, `change-me` credentials, and `APP_DEBUG=true`.

Validation errors name the invalid setting but never print the supplied values, because the database URL contains credentials.

## Proxy headers

The frontend Nginx proxy forwards the client's `Host` header, including its port, and an `X-Forwarded-Proto` header. Behind Traefik, that header carries Traefik's `https`; without Traefik, Nginx sends its own scheme. Uvicorn applies `X-Forwarded-Proto` and `X-Forwarded-For` only from the addresses listed in `FORWARDED_ALLOW_IPS`, which defaults to loopback. Both Compose files set it to `*` so that URLs the backend builds, such as trailing-slash redirects, keep the public host, port, and scheme.

Set `FORWARDED_ALLOW_IPS=*` only where clients cannot reach the backend directly. Otherwise a client can choose the scheme and client address the backend sees.
