"""Inspect or apply authorized GitHub transitions for human acceptance."""

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


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect or apply an authorized Chapter 8 GitHub transition.")
    parser.add_argument("--repo", required=True, help="OWNER/REPOSITORY")
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--project-owner")
    parser.add_argument("--project", type=int)
    parser.add_argument("--issue-url")
    parser.add_argument("--candidate-commit")
    parser.add_argument(
        "--human-outcome",
        choices=["human-accepted", "human-rejected", "human-blocked"],
    )
    parser.add_argument("--transition", choices=["human-acceptance", "ready-to-merge"])
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    pull_request = json.loads(
        checked(
            "pr",
            "view",
            str(args.pr),
            "--repo",
            args.repo,
            "--json",
            "number,url,state,isDraft,headRefOid,statusCheckRollup,reviewDecision",
        )
    )
    if not args.transition:
        print(json.dumps({"status": "read", "pull_request": pull_request}))
        return 0
    if not all([args.project_owner, args.project, args.issue_url, args.candidate_commit]):
        parser.error("a transition requires Project arguments, --issue-url, and --candidate-commit")
    if pull_request["headRefOid"] != args.candidate_commit:
        raise SystemExit("Candidate commit does not match the pull-request head")
    if args.transition == "ready-to-merge" and (args.human_outcome != "human-accepted"):
        raise SystemExit("Ready to merge requires --human-outcome human-accepted")

    desired = "Human acceptance" if args.transition == "human-acceptance" else "Ready to merge"
    if pull_request["state"] != "OPEN" or (args.transition == "ready-to-merge" and pull_request["isDraft"]):
        raise SystemExit("The transition requires an open PR in the expected ready state")
    helper = (
        Path(__file__).resolve().parents[2] / "06-verification-and-validation-orchestrator/scripts/github_project.py"
    )
    project_command = [
        sys.executable,
        str(helper),
        "--owner",
        args.project_owner,
        "--project",
        str(args.project),
        "--url",
        args.issue_url,
        "--to",
        desired,
        "--from-status",
        "Technical documentation" if args.transition == "human-acceptance" else "Human acceptance",
    ]
    # Move the Project first. A retry recognizes the destination and can finish marking the PR ready.
    result = subprocess.run(project_command + (["--apply"] if args.apply else []), capture_output=True, text=True)  # noqa: S603
    if result.returncode not in ({0} if args.apply else {0, 2}):
        raise SystemExit(result.stderr.strip() or result.stdout.strip())
    if not args.apply and json.loads(result.stdout)["status"] not in {"matched", "planned"}:
        raise SystemExit("Project transition could not be planned")
    plan = {
        "status": "planned",
        "pull_request": args.pr,
        "mark_ready": args.transition == "human-acceptance" and pull_request["isDraft"],
        "project_status": desired,
    }
    if not args.apply:
        print(json.dumps(plan))
        return 2

    if args.transition == "human-acceptance" and pull_request["isDraft"]:
        checked("pr", "ready", str(args.pr), "--repo", args.repo)
    print(json.dumps({**plan, "status": "applied"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
