FROM python:3.13-alpine3.24 AS build
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /usr/local/bin/uv
ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
COPY pyproject.toml uv.lock ./
COPY backend ./backend
COPY packages ./packages
RUN uv sync --locked --package elims-backend --no-dev --no-editable

FROM python:3.13-alpine3.24 AS runtime
WORKDIR /app/backend
ENV PATH="/app/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=build /app/.venv /app/.venv
COPY backend/alembic.ini ./
COPY backend/app ./app
RUN /usr/local/bin/python -m pip uninstall --yes pip \
    && addgroup -S -g 10001 elims \
    && adduser -S -D -H -u 10001 -G elims elims
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
