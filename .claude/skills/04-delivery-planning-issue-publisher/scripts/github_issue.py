"""Idempotently inspect, create, or update an ELIMS GitHub issue."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

GH = shutil.which("gh") or "gh"


def gh(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - arguments are passed without a shell
        [GH, *args], check=False, capture_output=True, text=True
    )


def checked(*args: str) -> str:
    result = gh(*args)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or result.stdout.strip())
    return result.stdout


def find(repo: str, stable_id: str) -> list[dict[str, object]]:
    marker = f"<!-- elims-issue-id: {stable_id} -->"
    output = checked(
        "issue",
        "list",
        "--repo",
        repo,
        "--state",
        "all",
        "--limit",
        "1000",
        "--search",
        f'"{marker}" in:body',
        "--json",
        "number,title,url,state,body,labels",
    )
    return [item for item in json.loads(output) if marker in (item.get("body") or "")]


def main() -> int:
    parser = argparse.ArgumentParser(description="Find or upsert an issue by its ELIMS stable identifier.")
    parser.add_argument("--repo", required=True, help="OWNER/REPOSITORY")
    parser.add_argument("--stable-id", required=True)
    parser.add_argument("--title")
    parser.add_argument("--body-file", type=Path)
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument("--parent", type=int)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    matches = find(args.repo, args.stable_id)
    if len(matches) > 1:
        print(json.dumps({"status": "conflict", "matches": matches}))
        return 3
    if not args.title and not args.body_file:
        print(json.dumps({"status": "found" if matches else "not-found", "matches": matches}))
        return 0 if matches else 1
    if not args.title or not args.body_file:
        parser.error("--title and --body-file are both required for an upsert")

    body = args.body_file.read_text(encoding="utf-8")
    marker = f"<!-- elims-issue-id: {args.stable_id} -->"
    if marker not in body:
        body = f"{body.rstrip()}\n\n{marker}\n"

    action = "update" if matches else "create"
    plan = {"status": "planned", "action": action, "stable_id": args.stable_id}
    if not args.apply:
        print(json.dumps(plan))
        return 2

    temporary = args.body_file.with_name(f".{args.body_file.name}.elims-gh.tmp")
    try:
        temporary.write_text(body, encoding="utf-8")
        if matches:
            command = [
                "issue",
                "edit",
                str(matches[0]["number"]),
                "--repo",
                args.repo,
                "--title",
                args.title,
                "--body-file",
                str(temporary),
            ]
        else:
            command = [
                "issue",
                "create",
                "--repo",
                args.repo,
                "--title",
                args.title,
                "--body-file",
                str(temporary),
            ]
            if args.parent:
                command.extend(["--parent", str(args.parent)])
        for label in args.label:
            command.extend(["--add-label" if matches else "--label", label])
        checked(*command)
    finally:
        temporary.unlink(missing_ok=True)

    verified = find(args.repo, args.stable_id)
    if len(verified) != 1:
        raise SystemExit("Issue mutation completed but stable-marker verification failed")
    print(json.dumps({"status": "applied", "action": action, "issue": verified[0]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
