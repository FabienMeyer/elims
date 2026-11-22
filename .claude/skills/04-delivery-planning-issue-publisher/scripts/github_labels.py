"""Inspect or reconcile one GitHub label through the GitHub CLI."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

GH = shutil.which("gh") or "gh"


def gh(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - arguments are passed without a shell
        [GH, *args], check=False, capture_output=True, text=True
    )


def fail(result: subprocess.CompletedProcess[str]) -> None:
    message = result.stderr.strip() or result.stdout.strip() or "GitHub CLI failed"
    raise SystemExit(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify or reconcile a repository label. Mutation requires --apply.")
    parser.add_argument("--repo", required=True, help="OWNER/REPOSITORY")
    parser.add_argument("--name", required=True)
    parser.add_argument("--color", default="1D76DB", help="Six-digit hex without #")
    parser.add_argument("--description", default="")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    result = gh(
        "label",
        "list",
        "--repo",
        args.repo,
        "--limit",
        "1000",
        "--json",
        "name,color,description",
    )
    if result.returncode:
        fail(result)
    labels = json.loads(result.stdout)
    current = next((item for item in labels if item["name"] == args.name), None)
    desired = {
        "name": args.name,
        "color": args.color.upper(),
        "description": args.description,
    }

    if (
        current
        and current["color"].upper() == desired["color"]
        and (current.get("description") or "") == desired["description"]
    ):
        print(json.dumps({"status": "matched", "label": current}))
        return 0

    action = "edit" if current else "create"
    if not args.apply:
        print(json.dumps({"status": "planned", "action": action, "desired": desired}))
        return 2

    command = ["label", action]
    if action == "edit":
        command.extend([args.name, "--repo", args.repo])
    else:
        command.extend([args.name, "--repo", args.repo])
    command.extend(["--color", args.color, "--description", args.description])
    result = gh(*command)
    if result.returncode:
        fail(result)
    print(json.dumps({"status": "applied", "action": action, "label": desired}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
