"""Exercise a running disposable stack through its public frontend proxy."""

import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen
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


def main() -> None:
    """Verify migrations, routing, validation and persistent item creation."""
    checks = [request("/api/health")[0] == 200, request("/api/ready")[0] == 200]
    status, item = request("/api/v1/items/", {"name": "smoke-" + str(uuid4())})
    checks.append(status == 201 and isinstance(item, dict) and "id" in item)
    checks.append(request("/api/v1/items/", {"name": ""})[0] == 422)
    checks.append(request("/api/v1/items/?limit=101")[0] == 422)
    checks.append(request("/api/v1/items/?limit=1")[0] == 200)
    if not all(checks):
        raise RuntimeError(f"Stack checks failed: {checks}")
    print("Proxy, migrations, database readiness, item creation and validation passed.")


if __name__ == "__main__":
    main()
