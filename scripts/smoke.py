"""Exercise a running disposable stack through its public frontend proxy."""

import json
import os
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


def main() -> None:
    """Verify migrations, routing, validation, persistent item creation and proxy-built URLs."""
    checks = [request("/api/health")[0] == 200, request("/api/ready")[0] == 200]
    status, item = request("/api/v1/items/", {"name": "smoke-" + str(uuid4())})
    checks.append(status == 201 and isinstance(item, dict) and "id" in item)
    checks.append(request("/api/v1/items/", {"name": ""})[0] == 422)
    checks.append(request("/api/v1/items/?limit=101")[0] == 422)
    checks.append(request("/api/v1/items/?limit=1")[0] == 200)
    # Redirects must keep the public host, port and scheme. Traefik terminates TLS and sends X-Forwarded-Proto.
    checks.append(redirect_location("/api/v1/items?limit=1") == f"{base}/api/v1/items/?limit=1")
    secure_base = base.replace("http://", "https://", 1)
    forwarded = redirect_location("/api/v1/items?limit=1", {"X-Forwarded-Proto": "https"})
    checks.append(forwarded == f"{secure_base}/api/v1/items/?limit=1")
    if not all(checks):
        raise RuntimeError(f"Stack checks failed: {checks}")
    print("Proxy, migrations, database readiness, item creation, validation and redirects passed.")


if __name__ == "__main__":
    main()
