"""Read or safely transition the Status field of a GitHub Project item."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

GH = shutil.which("gh") or "gh"


def checked(*args: str) -> str:
    result = subprocess.run(  # noqa: S603 - arguments are passed without a shell
        [GH, *args], check=False, capture_output=True, text=True
    )
    if result.returncode:
        raise SystemExit(result.stderr.strip() or result.stdout.strip())
    return result.stdout


PIPELINE = (
    "Backlog",
    "Ready to implement",
    "Implementation",
    "Technical verification",
    "Agent system validation",
    "Technical documentation",
    "Human acceptance",
    "Ready to merge",
    "Done",
)
REWORK = "Implementation"
BLOCKED = "Blocked"


def legal_transition(current: str | None, target: str) -> bool:
    """Allow the next pipeline step, rework to Implementation, or entering and leaving Blocked."""
    if target == BLOCKED:
        return current in PIPELINE
    if current == BLOCKED:
        return target in PIPELINE and target != "Done"
    if current not in PIPELINE or target not in PIPELINE:
        return False
    current_index, target_index = PIPELINE.index(current), PIPELINE.index(target)
    if target == REWORK and target_index < current_index:
        return current != "Done"
    return target_index == current_index + 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Read or transition Project Status. Mutation requires --apply.")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--project", required=True, type=int)
    parser.add_argument("--url", required=True, help="Issue or pull-request URL")
    parser.add_argument("--to", help="Desired Status option")
    parser.add_argument("--from-status", help="Required current Status before mutation")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    output = checked(
        "project",
        "item-list",
        str(args.project),
        "--owner",
        args.owner,
        "--limit",
        "1000",
        "--format",
        "json",
    )
    data = json.loads(output)
    items = data if isinstance(data, list) else data.get("items", [])
    matches = [item for item in items if item.get("content", {}).get("url") == args.url]
    if len(matches) != 1:
        print(json.dumps({"status": "not-found" if not matches else "conflict"}))
        return 1 if not matches else 3
    item = matches[0]
    current = item.get("status") or item.get("Status")
    if not args.to:
        print(json.dumps({"status": "read", "current": current, "item": item}))
        return 0
    if current == args.to:
        print(json.dumps({"status": "matched", "current": current}))
        return 0
    if not args.from_status:
        parser.error("--to requires --from-status")
    if current != args.from_status:
        print(json.dumps({"status": "rejected", "expected": args.from_status, "current": current}))
        return 4
    if not legal_transition(current, args.to):
        print(json.dumps({"status": "rejected", "reason": "illegal-transition", "from": current, "to": args.to}))
        return 4
    scope = (str(args.project), "--owner", args.owner)
    project = json.loads(checked("project", "view", *scope, "--format", "json"))
    fields = json.loads(checked("project", "field-list", *scope, "--limit", "100", "--format", "json"))["fields"]
    status_fields = [field for field in fields if field["name"] == "Status"]
    if len(status_fields) != 1:
        raise SystemExit("Expected one Status field")
    field = status_fields[0]
    options = [option["id"] for option in field.get("options", []) if option["name"] == args.to]
    if len(options) != 1:
        raise SystemExit("Expected one matching Status option")
    edit = (
        "--project-id",
        project["id"],
        "--id",
        item["id"],
        "--field-id",
        field["id"],
        "--single-select-option-id",
        options[0],
    )
    if not args.apply:
        print(json.dumps({"status": "planned", "from": current, "to": args.to}))
        return 2
    checked(
        "project",
        "item-edit",
        *edit,
    )
    print(json.dumps({"status": "applied", "from": current, "to": args.to}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
