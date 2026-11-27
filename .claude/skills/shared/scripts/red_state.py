"""Record and verify the Red state of an ELIMS leaf issue.

``record`` runs after ``/tdd-engineer`` returns ``red`` and before any
production change. It computes the working-tree anchor, confirms that the
change against the base touches test files only, and pins the tree under the
local ref ``refs/elims/red/<leaf>`` so that Git garbage collection keeps it.

``verify`` lets ``/technical-verifier`` confirm that Red came before Green. It
checks that the recorded tree exists, matches the pinned ref and base, and
changes test files only. With a command after ``--``, it also materializes the
Red tree in a temporary directory, runs the command there, and confirms that
the command fails.

Exit codes: 0 success, 2 usage or Git error, 3 non-test change in the Red
state, 4 missing or mismatched Red evidence, 5 the Red command passed.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))

from review_anchor import anchored_tree_id, git

REF_PREFIX = "refs/elims/red/"
TEST_DIRECTORIES = frozenset({"tests", "__tests__"})
TEST_FILE_PATTERNS = ("conftest.py", "test_*.py", "*_test.py", "*.test.*", "*.spec.*")
TOOL_IDENTITY = {
    "GIT_AUTHOR_NAME": "ELIMS red state",
    "GIT_AUTHOR_EMAIL": "red-state@elims.invalid",
    "GIT_COMMITTER_NAME": "ELIMS red state",
    "GIT_COMMITTER_EMAIL": "red-state@elims.invalid",
}
OUTPUT_TAIL_LINES = 40


def is_test_path(path: str, extra_patterns: list[str]) -> bool:
    posix = PurePosixPath(path)
    if any(part in TEST_DIRECTORIES for part in posix.parts[:-1]):
        return True
    if any(fnmatch.fnmatch(posix.name, pattern) for pattern in TEST_FILE_PATTERNS):
        return True
    return any(fnmatch.fnmatch(path, pattern) for pattern in extra_patterns)


def changed_paths(root: Path, base_tree: str, red_tree: str) -> list[str]:
    output = git("diff", "--name-only", "--no-renames", base_tree, red_tree, cwd=root)
    return [line for line in output.splitlines() if line]


def non_test_paths(paths: list[str], extra_patterns: list[str]) -> list[str]:
    return [path for path in paths if not is_test_path(path, extra_patterns)]


def leaf_ref(leaf: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", leaf) or ".." in leaf or leaf.endswith((".", ".lock")):
        raise SystemExit(f"invalid leaf identifier for a ref name: {leaf!r}")
    return REF_PREFIX + leaf


def emit(payload: dict[str, object]) -> None:
    print(json.dumps(payload, indent=2))


def record(root: Path, args: argparse.Namespace) -> int:
    base = git("rev-parse", "--verify", f"{args.base}^{{commit}}", cwd=root)
    tree = anchored_tree_id(root, "HEAD", include_working_tree=True)
    paths = changed_paths(root, f"{base}^{{tree}}", tree)
    offenders = non_test_paths(paths, args.test_path)
    result: dict[str, object] = {"base": base, "source": "working-tree", "tree": tree, "changed_paths": paths}
    if not paths:
        result["error"] = "The Red state has no change against the base."
        emit(result)
        return 4
    if offenders:
        result["error"] = "The Red state changes files that are not tests."
        result["non_test_paths"] = offenders
        emit(result)
        return 3
    env = {**os.environ, **TOOL_IDENTITY}
    message = f"ELIMS red state for {args.leaf}"
    commit = git("commit-tree", tree, "-p", base, "-m", message, cwd=root, env=env)
    ref = leaf_ref(args.leaf)
    git("update-ref", ref, commit, cwd=root)
    result.update({"ref": ref, "commit": commit})
    emit(result)
    return 0


def object_type(root: Path, name: str) -> str | None:
    result = subprocess.run(  # noqa: S603 - arguments are passed without a shell
        ["git", "cat-file", "-t", name],  # noqa: S607 - git is resolved from PATH
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def materialize(root: Path, tree: str, destination: Path) -> None:
    env = {**os.environ, "GIT_INDEX_FILE": str(destination.parent / "red-index")}
    git("read-tree", tree, cwd=root, env=env)
    git("checkout-index", "--all", "--force", f"--prefix={destination.as_posix()}/", cwd=root, env=env)


def replay(root: Path, tree: str, command: list[str]) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="elims-red-", ignore_cleanup_errors=True) as directory:
        workspace = Path(directory) / "tree"
        workspace.mkdir()
        materialize(root, tree, workspace)
        completed = subprocess.run(  # noqa: S603 - the verifier supplies the test command
            command,
            cwd=workspace,
            capture_output=True,
            text=True,
            check=False,
        )
    lines = (completed.stdout + completed.stderr).splitlines()
    return {"command": command, "exit_code": completed.returncode, "output_tail": lines[-OUTPUT_TAIL_LINES:]}


def verify(root: Path, args: argparse.Namespace) -> int:
    base = git("rev-parse", "--verify", f"{args.base}^{{commit}}", cwd=root)
    result: dict[str, object] = {"base": base, "red_tree": args.red_tree}
    if object_type(root, args.red_tree) != "tree":
        result["error"] = "The Red tree object does not exist. Red evidence cannot be verified."
        emit(result)
        return 4
    if args.leaf:
        ref = leaf_ref(args.leaf)
        result["ref"] = ref
        if object_type(root, ref) != "commit":
            result["error"] = f"The pinned Red ref {ref} does not exist."
            emit(result)
            return 4
        pinned_tree = git("rev-parse", f"{ref}^{{tree}}", cwd=root)
        pinned_base = git("rev-parse", f"{ref}^", cwd=root)
        if pinned_tree != args.red_tree or pinned_base != base:
            result.update({"pinned_tree": pinned_tree, "pinned_base": pinned_base})
            result["error"] = "The pinned Red ref does not match the supplied tree and base."
            emit(result)
            return 4
    paths = changed_paths(root, f"{base}^{{tree}}", args.red_tree)
    result["changed_paths"] = paths
    offenders = non_test_paths(paths, args.test_path)
    if offenders:
        result["error"] = "The Red state changes files that are not tests."
        result["non_test_paths"] = offenders
        emit(result)
        return 3
    if args.command:
        outcome = replay(root, args.red_tree, args.command)
        result["replay"] = outcome
        if outcome["exit_code"] == 0:
            result["error"] = "The Red command passed. The Red state does not demonstrate a failure."
            emit(result)
            return 5
    emit(result)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse options. Everything after a literal ``--`` is the Red test command for ``verify``."""
    command: list[str] = []
    if "--" in argv:
        separator = argv.index("--")
        argv, command = argv[:separator], argv[separator + 1 :]
    parser = argparse.ArgumentParser(
        description="Record or verify the Red state of an ELIMS leaf issue.",
        epilog="verify: put the test command to replay in the Red tree after a literal --.",
    )
    subcommands = parser.add_subparsers(dest="action", required=True)

    record_parser = subcommands.add_parser("record", help="Pin the current working tree as the Red state.")
    record_parser.add_argument("--base", required=True, help="Revision the change is measured against")
    record_parser.add_argument("--leaf", required=True, help="Leaf issue identifier, such as ISSUE-001 or 42")

    verify_parser = subcommands.add_parser("verify", help="Verify a recorded Red state.")
    verify_parser.add_argument("--base", required=True, help="Revision the change is measured against")
    verify_parser.add_argument("--red-tree", required=True, help="Red anchor tree from the traceability matrix")
    verify_parser.add_argument("--leaf", help="Leaf issue identifier whose pinned ref must match")

    for sub in (record_parser, verify_parser):
        sub.add_argument(
            "--test-path",
            action="append",
            default=[],
            help="Additional glob for test-support paths, such as 'frontend/src/testing/*'",
        )
    args = parser.parse_args(argv)
    if command and args.action != "verify":
        parser.error("a command after -- is only valid for verify")
    args.command = command
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = Path(git("rev-parse", "--show-toplevel"))
    return record(root, args) if args.action == "record" else verify(root, args)


if __name__ == "__main__":
    sys.exit(main())
