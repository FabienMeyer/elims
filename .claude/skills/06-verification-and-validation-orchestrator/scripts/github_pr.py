"""Inspect, open, or promote the pull request for one GitHub issue."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

GH = shutil.which("gh") or "gh"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - arguments are passed without a shell
        [GH, *args], check=False, capture_output=True, text=True
    )


def checked(*args: str) -> str:
    result = run(*args)
    if result.returncode:
        raise SystemExit(result.stderr.strip() or result.stdout.strip())
    return result.stdout


def view(repo: str, branch: str) -> dict[str, object] | None:
    result = run(
        "pr",
        "view",
        branch,
        "--repo",
        repo,
        "--json",
        "number,title,url,state,isDraft,headRefName,statusCheckRollup,reviewDecision",
    )
    if result.returncode:
        return None
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect or mutate a pull request. Mutation requires --apply.")
    parser.add_argument("--repo", required=True, help="OWNER/REPOSITORY")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--open-draft", action="store_true")
    parser.add_argument("--ready", action="store_true")
    parser.add_argument("--title")
    parser.add_argument("--body-file", type=Path)
    parser.add_argument("--base")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if args.open_draft and args.ready:
        parser.error("choose either --open-draft or --ready")
    current = view(args.repo, args.branch)
    if not args.open_draft and not args.ready:
        print(json.dumps({"status": "found" if current else "not-found", "pull_request": current}))
        return 0 if current else 1

    if args.open_draft:
        if current:
            print(json.dumps({"status": "matched", "pull_request": current}))
            return 0
        if not args.title or not args.body_file or not args.base:
            parser.error("--open-draft requires --title, --body-file, and --base")
        if not args.apply:
            print(json.dumps({"status": "planned", "action": "open-draft"}))
            return 2
        checked(
            "pr",
            "create",
            "--repo",
            args.repo,
            "--head",
            args.branch,
            "--base",
            args.base,
            "--title",
            args.title,
            "--body-file",
            str(args.body_file),
            "--draft",
        )
    else:
        if not current:
            raise SystemExit("No pull request exists for the supplied branch")
        if not current.get("isDraft"):
            print(json.dumps({"status": "matched", "pull_request": current}))
            return 0
        if not args.apply:
            print(json.dumps({"status": "planned", "action": "mark-ready", "pull_request": current}))
            return 2
        checked("pr", "ready", str(current["number"]), "--repo", args.repo)

    updated = view(args.repo, args.branch)
    print(json.dumps({"status": "applied", "pull_request": updated}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
