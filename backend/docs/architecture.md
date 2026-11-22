# Backend architecture

The backend uses a FastAPI application factory and separates HTTP routes from persistence and domain concerns.

```text
HTTP request -> FastAPI route -> domain/package boundary -> SQLModel session -> database
```

Configuration is loaded through Pydantic settings. Alembic owns schema migrations. Structured logging and Prometheus instrumentation provide operational evidence.
