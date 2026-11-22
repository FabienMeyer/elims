"""Structured request logs without credentials, query strings or request bodies."""

import logging
from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import uuid4

import structlog
from fastapi import Request, Response


def configure_logging() -> None:
    """Write JSON events to stdout with request-local context."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


async def log_request(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Log bounded metadata and return a generated correlation ID."""
    structlog.contextvars.clear_contextvars()
    request_id = str(uuid4())
    structlog.contextvars.bind_contextvars(request_id=request_id)
    started = perf_counter()
    logger = structlog.get_logger()
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        # Route templates avoid logging sensitive path parameters and unbounded URLs.
        route = getattr(request.scope.get("route"), "path", "unmatched")
        logger.info(
            "http_request",
            method=request.method,
            route=route,
            status=response.status_code,
            duration_ms=round((perf_counter() - started) * 1000, 2),
        )
        return response
    except Exception as error:
        # Exception messages can contain SQL parameters, connection URLs or tokens.
        logger.error("request_failed", error_type=type(error).__name__)
        return Response(status_code=500, content="Internal server error", headers={"X-Request-ID": request_id})
    finally:
        structlog.contextvars.clear_contextvars()
