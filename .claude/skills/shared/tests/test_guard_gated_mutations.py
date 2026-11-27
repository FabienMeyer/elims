"""Tests for the ELIMS PreToolUse guard on shell commands."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "guard_gated_mutations.py"
SPEC = importlib.util.spec_from_file_location("guard_gated_mutations", HOOK)
assert SPEC is not None and SPEC.loader is not None
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


@pytest.fixture(autouse=True)
def work_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(guard, "current_branch", lambda: "feat/42-sample-change")


def verdict(command: str) -> str | None:
    decision = guard.evaluate(command)
    return None if decision is None else decision[0]


@pytest.mark.parametrize(
    "command",
    [
        "gh pr merge 12 --squash",
        "gh -R FabienMeyer/elims pr merge 12",
        "git status && gh pr merge 12",
        "gh issue edit 7 --add-label rdy-to-implement",
        "gh issue edit 7 --add-label=bug,rdy-to-implement",
        "gh issue edit 7 --remove-label rdy-to-implement",
        "gh label delete rdy-to-implement --yes",
        "gh api repos/o/r/issues/7/labels -f 'labels[]=rdy-to-implement'",
        "gh api -X PUT repos/o/r/pulls/3/merge",
        "gh api graphql -f query='mutation { mergePullRequest(input: {}) { clientMutationId } }'",
        "git push --force origin feat/x",
        "git push -f",
        "git push --force-with-lease origin feat/x",
        "git push origin +feat/x",
        "git push origin :feat/x",
        "git push --delete origin feat/x",
        "git push origin main",
        "git push origin HEAD:main",
        "git -C backend push origin refs/heads/master",
        "gh auth token",
        "gh secret set ELIMS_PROJECT_TOKEN",
        "gh issue delete 7 --yes",
        'bash -c "gh pr merge 12"',
        "pwsh -Command 'gh pr merge 12'",
        "GH_TOKEN=x gh pr merge 12",
        "& gh.exe pr merge 12",
        "C:/tools/gh.exe pr merge 12",
    ],
)
def test_denies_actions_reserved_for_humans(command: str) -> None:
    assert verdict(command) == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "git push origin feat/42-sample-change",
        "git push -u origin feat/42-sample-change",
        "git push",
        "gh pr create --draft --title t --body b",
        "gh pr ready 12",
        "gh issue create --title t",
        "gh issue edit 7 --add-label bug",
        "gh issue close 7",
        "gh project item-edit --id X --field-id Y",
        "gh release create v1.0.0",
        "gh api repos/o/r/issues -f title=t",
        "gh api graphql -f query='mutation { addProjectV2ItemById(input: {}) { item { id } } }'",
        "python .claude/skills/06-verification-and-validation-orchestrator/scripts/github_project.py --apply",
        "uv run python .claude/skills/04-delivery-planning-issue-publisher/scripts/github_issue.py --apply",
        "git add -A; git commit -m wip; git push origin feat/x",
    ],
)
def test_asks_before_authorized_mutations(command: str) -> None:
    assert verdict(command) == "ask"


@pytest.mark.parametrize(
    "command",
    [
        "git status",
        "git log --oneline -5",
        "git commit -m 'docs: explain why agents never run gh pr merge'",
        "gh pr view 12 --json state",
        "gh issue view 7 --json labels",
        "gh issue list --label rdy-to-implement",
        "gh api repos/o/r/issues/7",
        "gh api graphql -f query='query { viewer { login } }'",
        "gh project item-list 14 --owner FabienMeyer",
        "python .claude/skills/06-verification-and-validation-orchestrator/scripts/github_project.py",
        "uv run pytest --cov",
        "echo push",
    ],
)
def test_allows_read_only_and_local_commands(command: str) -> None:
    assert verdict(command) is None


def test_push_without_refspec_on_default_branch_is_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(guard, "current_branch", lambda: "main")
    assert verdict("git push") == "deny"


def test_push_without_refspec_on_unknown_branch_is_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(guard, "current_branch", lambda: None)
    assert verdict("git push") == "deny"


def test_deny_wins_over_ask_in_one_command() -> None:
    assert verdict("gh pr create --draft && gh pr merge 12") == "deny"


def test_unparseable_command_uses_fallback() -> None:
    assert verdict("gh pr merge 12 'unterminated") == "deny"
    assert verdict("git push origin feat/x 'unterminated") == "ask"
    assert verdict("echo 'unterminated") is None


def test_powershell_backtick_continuation() -> None:
    assert verdict("gh pr merge `\n  12") == "deny"


def run_hook(payload: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed interpreter and script path
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )


def test_hook_prints_permission_decision() -> None:
    result = run_hook({"tool_name": "Bash", "tool_input": {"command": "gh pr merge 1"}})
    assert result.returncode == 0
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "PreToolUse"
    assert output["permissionDecision"] == "deny"
    assert output["permissionDecisionReason"].startswith("ELIMS gate:")


def test_hook_is_silent_for_ungated_commands() -> None:
    result = run_hook({"tool_name": "PowerShell", "tool_input": {"command": "Get-ChildItem"}})
    assert result.returncode == 0
    assert result.stdout == ""
