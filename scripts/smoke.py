"""Exercise a running disposable stack through its public frontend proxy."""

import json
import os
import re
from email.message import Message
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen
from uuid import uuid4

base = os.environ.get("SMOKE_URL", "http://127.0.0.1:8080")
if not base.startswith(("http://127.0.0.1:", "http://localhost:")):
    raise ValueError("Smoke checks may only target a local disposable stack")


def request(path: str, payload: dict[str, str] | None = None) -> tuple[int, object]:
    """Send a local HTTP request and decode JSON responses."""
    data = json.dumps(payload).encode() if payload is not None else None
    req = Request(base + path, data=data, headers={"Content-Type": "application/json"})  # noqa: S310
    try:
        with urlopen(req, timeout=10) as response:  # noqa: S310
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, json.load(error)


def fetch(path: str, headers: dict[str, str] | None = None) -> tuple[int, Message, bytes]:
    """Send a local GET request and return the raw status, headers, and body."""
    req = Request(base + path, headers=headers or {})  # noqa: S310
    try:
        with urlopen(req, timeout=10) as response:  # noqa: S310
            return response.status, response.headers, response.read()
    except HTTPError as error:
        return error.code, error.headers, error.read()


class KeepRedirect(HTTPRedirectHandler):
    """Surface redirects as responses instead of following them."""

    def redirect_request(self, *args: object, **kwargs: object) -> None:
        return None


def redirect_location(path: str, headers: dict[str, str] | None = None) -> str | None:
    """Return the Location header of a redirect without following it."""
    try:
        build_opener(KeepRedirect).open(Request(base + path, headers=headers or {}), timeout=10)  # noqa: S310
    except HTTPError as error:
        return error.headers.get("Location")
    return None


def api_checks() -> dict[str, bool]:
    """Verify migrations, routing, validation, persistent item creation and proxy-built URLs."""
    health = request("/api/health")[0] == 200
    readiness = request("/api/ready")[0] == 200
    status, item = request("/api/v1/items/", {"name": "smoke-" + str(uuid4())})
    # Redirects must keep the public host, port and scheme. Traefik terminates TLS and sends X-Forwarded-Proto.
    secure_base = base.replace("http://", "https://", 1)
    forwarded = redirect_location("/api/v1/items?limit=1", {"X-Forwarded-Proto": "https"})
    return {
        "api health": health,
        "api readiness": readiness,
        "item creation": status == 201 and isinstance(item, dict) and "id" in item,
        "empty item name rejected": request("/api/v1/items/", {"name": ""})[0] == 422,
        "oversized limit rejected": request("/api/v1/items/?limit=101")[0] == 422,
        "item listing": request("/api/v1/items/?limit=1")[0] == 200,
        "redirect keeps public host": redirect_location("/api/v1/items?limit=1") == f"{base}/api/v1/items/?limit=1",
        "redirect keeps forwarded scheme": forwarded == f"{secure_base}/api/v1/items/?limit=1",
    }


def frontend_checks() -> dict[str, bool]:
    """Verify how Nginx serves the built application shell and its hashed assets."""
    status, headers, body = fetch("/")
    script = re.search(r'src="(/assets/[\w.-]+\.js)"', body.decode())
    asset_status, asset_headers, _ = fetch(script.group(1) if script else "/assets/", {"Accept-Encoding": "gzip"})
    route_status, route_headers, _ = fetch("/client-side/route")
    return {
        "shell served": status == 200 and headers.get_content_type() == "text/html",
        "shell revalidated": headers.get("Cache-Control") == "no-cache",
        "shell content security policy": "default-src 'self'" in headers.get("Content-Security-Policy", ""),
        "shell references a hashed script": script is not None,
        "asset served": asset_status == 200,
        "asset cached immutably": "immutable" in asset_headers.get("Cache-Control", ""),
        "asset compressed": asset_headers.get("Content-Encoding") == "gzip",
        "missing asset not found": fetch("/assets/missing-smoke-asset.js")[0] == 404,
        "client route falls back to shell": route_status == 200 and route_headers.get_content_type() == "text/html",
    }


def main() -> None:
    """Verify the public proxy, the API behind it, and the frontend delivery policy."""
    checks = api_checks() | frontend_checks()
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Stack checks failed: {', '.join(failed)}")
    print("Proxy, migrations, database readiness, item creation, validation, redirects and frontend delivery passed.")


if __name__ == "__main__":
    main()
