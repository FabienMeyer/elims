"""Verify Project Status transitions and the transition table without GitHub access."""

import json
import runpy
import sys
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

PROJECT = Path(__file__).resolve().parents[1] / "scripts" / "github_project.py"
legal_transition = runpy.run_path(str(PROJECT))["legal_transition"]

FORWARD = [
    ("Backlog", "Ready to implement"),
    ("Ready to implement", "Implementation"),
    ("Implementation", "Technical verification"),
    ("Technical verification", "Agent system validation"),
    ("Agent system validation", "Technical documentation"),
    ("Technical documentation", "Human acceptance"),
    ("Human acceptance", "Ready to merge"),
    ("Ready to merge", "Done"),
]


@pytest.mark.parametrize(("current", "target"), FORWARD)
def test_each_next_step_is_legal(current: str, target: str) -> None:
    assert legal_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("Backlog", "Implementation"),
        ("Implementation", "Human acceptance"),
        ("Technical verification", "Technical documentation"),
        ("Human acceptance", "Done"),
        ("Technical documentation", "Technical verification"),
        ("Implementation", "Backlog"),
    ],
)
def test_skipping_forward_or_moving_backward_is_illegal(current: str, target: str) -> None:
    assert not legal_transition(current, target)


@pytest.mark.parametrize(
    "current",
    [
        "Technical verification",
        "Agent system validation",
        "Technical documentation",
        "Human acceptance",
        "Ready to merge",
    ],
)
def test_rework_returns_to_implementation_from_any_later_status(current: str) -> None:
    assert legal_transition(current, "Implementation")


def test_done_cannot_return_to_implementation() -> None:
    assert not legal_transition("Done", "Implementation")


@pytest.mark.parametrize("current", ["Backlog", "Implementation", "Human acceptance", "Ready to merge"])
def test_any_pipeline_status_can_become_blocked(current: str) -> None:
    assert legal_transition(current, "Blocked")


def test_blocked_resumes_to_any_status_except_done() -> None:
    assert legal_transition("Blocked", "Implementation")
    assert legal_transition("Blocked", "Human acceptance")
    assert not legal_transition("Blocked", "Done")


@pytest.mark.parametrize(
    ("current", "target"),
    [(None, "Implementation"), ("Unknown", "Implementation"), ("Implementation", "Unknown"), (None, "Blocked")],
)
def test_unknown_or_missing_status_is_illegal(current: str | None, target: str) -> None:
    assert not legal_transition(current, target)


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
