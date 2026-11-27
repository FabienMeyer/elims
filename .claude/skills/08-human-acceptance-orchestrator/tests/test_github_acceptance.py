"""Verify the human-acceptance transition keeps the pull request draft when the Project move fails."""

import json
import runpy
import sys
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

ACCEPTANCE = Path(__file__).resolve().parents[1] / "scripts" / "github_acceptance.py"


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
