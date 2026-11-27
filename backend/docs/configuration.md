# Backend configuration

Runtime settings are defined in `app/config.py` and supplied through environment variables. `.env.example` documents safe development defaults; production secrets are supplied outside version control.

Configuration additions require validation, documentation, and a secure default.

## Environment

`ENVIRONMENT` is required and must be `development`, `test`, or `production`. The backend and Alembic refuse to start without it, so a deployment that omits it cannot fall back to development, where business routes are open. `production` keeps business routes closed until authentication is integrated, and rejects SQLite, `change-me` credentials, and `APP_DEBUG=true`.

Validation errors name the invalid setting but never print the supplied values, because the database URL contains credentials.
