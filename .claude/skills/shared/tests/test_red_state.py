"""Verify Red-state recording and verification against a throwaway Git repository."""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "red_state.py"
module = runpy.run_path(str(SCRIPT))
main = module["main"]
is_test_path = module["is_test_path"]

FAIL_IF_RED_TEST_EXISTS = "import pathlib, sys; sys.exit(1 if pathlib.Path('tests/test_red.py').exists() else 0)"


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)  # noqa: S603, S607
    return result.stdout.strip()


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    git(tmp_path, "init", "--quiet", "--initial-branch=main")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "config", "user.email", "test@example.invalid")
    git(tmp_path, "config", "commit.gpgsign", "false")
    (tmp_path / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "--quiet", "-m", "base")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def run(capsys: pytest.CaptureFixture[str], *args: str) -> tuple[int, dict[str, object]]:
    code = main(list(args))
    return code, json.loads(capsys.readouterr().out)


def add_red_test(repo: Path) -> None:
    (repo / "tests").mkdir(exist_ok=True)
    (repo / "tests" / "test_red.py").write_text("def test_red():\n    assert False\n", encoding="utf-8")


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("backend/tests/test_items.py", True),
        ("packages/elims-cli/tests/fixtures/data.json", True),
        ("frontend/tests/unit/app.test.tsx", True),
        ("frontend/tests/e2e/home.spec.ts", True),
        ("backend/conftest.py", True),
        ("frontend/src/form.test.ts", True),
        ("backend/app/main.py", False),
        ("backend/app/testing.py", False),
        ("docs/product/vision.md", False),
    ],
)
def test_classifies_test_paths(path: str, expected: bool) -> None:
    assert is_test_path(path, []) is expected


def test_record_pins_a_test_only_red_state(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    add_red_test(repo)
    code, result = run(capsys, "record", "--base", "main", "--leaf", "ISSUE-001")
    assert code == 0
    assert result["changed_paths"] == ["tests/test_red.py"]
    assert result["ref"] == "refs/elims/red/ISSUE-001"
    assert git(repo, "rev-parse", "refs/elims/red/ISSUE-001^{tree}") == result["tree"]
    assert git(repo, "rev-parse", "refs/elims/red/ISSUE-001^") == git(repo, "rev-parse", "main")
    assert git(repo, "rev-parse", "HEAD") == git(repo, "rev-parse", "main")
    assert git(repo, "status", "--porcelain") == "?? tests/"


def test_record_rejects_a_production_change(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    add_red_test(repo)
    (repo / "app.py").write_text("VALUE = 2\n", encoding="utf-8")
    code, result = run(capsys, "record", "--base", "main", "--leaf", "ISSUE-001")
    assert code == 3
    assert result["non_test_paths"] == ["app.py"]
    assert git(repo, "for-each-ref", "refs/elims") == ""


def test_record_rejects_an_empty_red_state(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, _ = run(capsys, "record", "--base", "main", "--leaf", "ISSUE-001")
    assert code == 4


def test_record_accepts_declared_test_support(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    add_red_test(repo)
    (repo / "testing_support.py").write_text("FIXTURE = 1\n", encoding="utf-8")
    code, _ = run(capsys, "record", "--base", "main", "--leaf", "ISSUE-001", "--test-path", "testing_support.py")
    assert code == 0


def test_record_rejects_an_unsafe_leaf_identifier(repo: Path) -> None:
    add_red_test(repo)
    with pytest.raises(SystemExit):
        main(["record", "--base", "main", "--leaf", "../main"])


def test_verify_replays_the_red_tree_after_green(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    add_red_test(repo)
    _, recorded = run(capsys, "record", "--base", "main", "--leaf", "ISSUE-001")
    (repo / "app.py").write_text("VALUE = 2\n", encoding="utf-8")
    code, result = run(
        capsys,
        "verify",
        "--base",
        "main",
        "--red-tree",
        str(recorded["tree"]),
        "--leaf",
        "ISSUE-001",
        "--",
        sys.executable,
        "-c",
        FAIL_IF_RED_TEST_EXISTS,
    )
    assert code == 0
    replay = result["replay"]
    assert isinstance(replay, dict)
    assert replay["exit_code"] == 1


def test_verify_reports_a_red_command_that_passes(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    add_red_test(repo)
    _, recorded = run(capsys, "record", "--base", "main", "--leaf", "ISSUE-001")
    red_tree = str(recorded["tree"])
    code, _ = run(capsys, "verify", "--base", "main", "--red-tree", red_tree, "--", sys.executable, "-c", "0")
    assert code == 5


def test_verify_rejects_a_red_tree_with_production_changes(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (repo / "app.py").write_text("VALUE = 2\n", encoding="utf-8")
    add_red_test(repo)
    tree = _working_tree(repo)
    code, result = run(capsys, "verify", "--base", "main", "--red-tree", tree)
    assert code == 3
    assert result["non_test_paths"] == ["app.py"]


def test_verify_rejects_a_missing_tree(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, _ = run(capsys, "verify", "--base", "main", "--red-tree", "0" * 40)
    assert code == 4


def test_verify_rejects_a_tree_that_differs_from_the_pinned_ref(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    add_red_test(repo)
    run(capsys, "record", "--base", "main", "--leaf", "ISSUE-001")
    (repo / "tests" / "test_other.py").write_text("def test_other():\n    pass\n", encoding="utf-8")
    other = _working_tree(repo)
    code, result = run(capsys, "verify", "--base", "main", "--red-tree", other, "--leaf", "ISSUE-001")
    assert code == 4
    assert "does not match" in str(result["error"])


def _working_tree(repo: Path) -> str:
    anchor = runpy.run_path(str(SCRIPT.parent / "review_anchor.py"))["anchored_tree_id"]
    return str(anchor(repo, "HEAD", include_working_tree=True))
