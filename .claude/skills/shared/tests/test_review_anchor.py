"""Verify the review anchor against a throwaway Git repository."""

import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "review_anchor.py"
main = runpy.run_path(str(SCRIPT))["main"]


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)  # noqa: S603, S607
    return result.stdout.strip()


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    git(tmp_path, "init", "--quiet", "--initial-branch=main")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "config", "commit.gpgsign", "false")
    (tmp_path / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
    (tmp_path / "a.txt").write_text("one\n", encoding="utf-8")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "--quiet", "-m", "base")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def anchor(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], *args: str) -> dict[str, str]:
    monkeypatch.setattr(sys, "argv", ["review_anchor.py", *args])
    assert main() == 0
    return json.loads(capsys.readouterr().out)


def test_clean_working_tree_matches_head(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    working = anchor(monkeypatch, capsys, "--base", "HEAD")
    committed = anchor(monkeypatch, capsys, "--base", "HEAD", "--head", "HEAD")
    assert working["source"] == "working-tree"
    assert working["tree"] == committed["tree"]
    assert working["base"] == git(repo, "rev-parse", "HEAD")


def test_committing_the_change_keeps_the_anchor(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    base = git(repo, "rev-parse", "HEAD")
    (repo / "a.txt").write_text("two\n", encoding="utf-8")
    (repo / "new.txt").write_text("new\n", encoding="utf-8")
    before = anchor(monkeypatch, capsys, "--base", base)
    git(repo, "add", "-A")
    git(repo, "commit", "--quiet", "-m", "change")
    after = anchor(monkeypatch, capsys, "--base", base, "--head", "HEAD")
    assert before["tree"] == after["tree"]
    assert before["base"] == after["base"] == base


def test_modified_tracked_file_changes_the_anchor(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    clean = anchor(monkeypatch, capsys, "--base", "HEAD")
    (repo / "a.txt").write_text("changed\n", encoding="utf-8")
    assert anchor(monkeypatch, capsys, "--base", "HEAD")["tree"] != clean["tree"]


def test_untracked_file_changes_the_anchor_but_ignored_file_does_not(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    clean = anchor(monkeypatch, capsys, "--base", "HEAD")
    (repo / "ignored.txt").write_text("x\n", encoding="utf-8")
    assert anchor(monkeypatch, capsys, "--base", "HEAD")["tree"] == clean["tree"]
    (repo / "untracked.txt").write_text("x\n", encoding="utf-8")
    assert anchor(monkeypatch, capsys, "--base", "HEAD")["tree"] != clean["tree"]


def test_anchor_leaves_index_and_working_tree_unchanged(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "untracked.txt").write_text("x\n", encoding="utf-8")
    before = git(repo, "status", "--porcelain")
    anchor(monkeypatch, capsys, "--base", "HEAD")
    assert git(repo, "status", "--porcelain") == before == "?? untracked.txt"


def write_matrix(repo: Path, text: str) -> None:
    matrix = repo / "docs" / "product" / "traceability" / "ISSUE-001.md"
    matrix.parent.mkdir(parents=True, exist_ok=True)
    matrix.write_text(text, encoding="utf-8")


def test_recording_evidence_in_the_traceability_matrix_keeps_the_anchor(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo / "a.txt").write_text("implementation\n", encoding="utf-8")
    reviewed = anchor(monkeypatch, capsys, "--base", "HEAD")
    write_matrix(repo, f"code-review anchor: {reviewed['tree']}\n")
    assert anchor(monkeypatch, capsys, "--base", "HEAD")["tree"] == reviewed["tree"]


def test_committed_traceability_matrix_keeps_the_anchor(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    base = git(repo, "rev-parse", "HEAD")
    (repo / "a.txt").write_text("implementation\n", encoding="utf-8")
    reviewed = anchor(monkeypatch, capsys, "--base", base)
    write_matrix(repo, "evidence\n")
    git(repo, "add", "-A")
    git(repo, "commit", "--quiet", "-m", "change with evidence")
    assert anchor(monkeypatch, capsys, "--base", base, "--head", "HEAD")["tree"] == reviewed["tree"]


def test_code_change_still_changes_the_anchor_when_a_matrix_exists(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    write_matrix(repo, "evidence\n")
    before = anchor(monkeypatch, capsys, "--base", "HEAD")
    (repo / "a.txt").write_text("changed\n", encoding="utf-8")
    assert anchor(monkeypatch, capsys, "--base", "HEAD")["tree"] != before["tree"]


def test_unknown_base_is_rejected(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["review_anchor.py", "--base", "no-such-revision"])
    with pytest.raises(SystemExit):
        main()
