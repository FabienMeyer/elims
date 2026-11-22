"""Verify Project transition command arguments and retry behavior without GitHub writes."""

import json
import runpy
import sys
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

SKILLS = Path(__file__).resolve().parents[3] / ".claude/skills"
PROJECT = SKILLS / "06-verification-and-validation-orchestrator/scripts/github_project.py"
ACCEPTANCE = SKILLS / "08-human-acceptance-orchestrator/scripts/github_acceptance.py"


@pytest.mark.parametrize("current", ["Technical documentation", "Human acceptance"])
def test_project_transition(current: str, monkeypatch: pytest.MonkeyPatch) -> None:
    url = "https://github.com/example/repo/issues/1"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(PROJECT),
            "--owner",
            "example",
            "--project",
            "14",
            "--url",
            url,
            "--from-status",
            "Technical documentation",
            "--to",
            "Human acceptance",
            "--apply",
        ],
    )
    main = runpy.run_path(str(PROJECT))["main"]
    responses = [
        {"items": [{"id": "item", "content": {"url": url}, "status": current}]},
        {"id": "project"},
        {"fields": [{"id": "field", "name": "Status", "options": [{"id": "option", "name": "Human acceptance"}]}]},
        {},
    ]
    with patch("subprocess.run") as runner:
        runner.side_effect = [CompletedProcess([], 0, json.dumps(value)) for value in responses]
        assert main() == 0
        if current == "Human acceptance":
            assert runner.call_count == 1
        else:
            assert runner.call_args.args[0][1:] == [
                "project",
                "item-edit",
                "--project-id",
                "project",
                "--id",
                "item",
                "--field-id",
                "field",
                "--single-select-option-id",
                "option",
            ]


def test_project_failure_keeps_pr_draft(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(ACCEPTANCE),
            "--repo",
            "example/repo",
            "--pr",
            "2",
            "--project-owner",
            "example",
            "--project",
            "14",
            "--issue-url",
            "https://github.com/example/repo/issues/1",
            "--candidate-commit",
            "abc",
            "--transition",
            "human-acceptance",
            "--apply",
        ],
    )
    main = runpy.run_path(str(ACCEPTANCE))["main"]
    with patch("subprocess.run") as runner:
        runner.side_effect = [
            CompletedProcess([], 0, json.dumps({"state": "OPEN", "headRefOid": "abc", "isDraft": True})),
            CompletedProcess([], 4, "", "Unexpected current status"),
        ]
        with pytest.raises(SystemExit, match="Unexpected current status"):
            main()
        assert runner.call_count == 2
