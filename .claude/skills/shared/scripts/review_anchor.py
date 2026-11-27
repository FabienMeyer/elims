"""Print the review anchor (base commit and content tree) for a change under review.

The anchor identifies the exact content that a reviewer, verifier, or validator
examined. Two anchors are equal only when the base and the full file content
are equal. A working tree and a commit that contain the same files produce the
same tree identifier, so the anchor survives committing the change.

Paths in ``EXCLUDED_PATHS`` are left out of every anchor. They hold delivery
evidence, such as the traceability matrix, that records anchors. Including
them would make recording an anchor change the anchor.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

EXCLUDED_PATHS = ("docs/product/traceability",)


def git(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(  # noqa: S603 - arguments are passed without a shell
        ["git", *args],  # noqa: S607
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
    )
    if result.returncode:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or "git failed")
    return result.stdout.strip()


def anchored_tree_id(root: Path, revision: str, *, include_working_tree: bool) -> str:
    """Return the tree identifier of ``revision``, optionally with the working tree, without excluded paths."""
    with tempfile.TemporaryDirectory() as directory:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(directory) / "index")}
        git("read-tree", revision, cwd=root, env=env)
        if include_working_tree:
            git("add", "-A", cwd=root, env=env)
        git("rm", "-r", "--cached", "--quiet", "--ignore-unmatch", "--", *EXCLUDED_PATHS, cwd=root, env=env)
        return git("write-tree", cwd=root, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the review anchor for a working tree or commit.")
    parser.add_argument("--base", required=True, help="Revision the change is measured against, such as origin/main")
    parser.add_argument("--head", help="Commit to anchor. Default: the current working tree")
    args = parser.parse_args()

    root = Path(git("rev-parse", "--show-toplevel"))
    base = git("rev-parse", "--verify", f"{args.base}^{{commit}}", cwd=root)
    if args.head:
        source = git("rev-parse", "--verify", f"{args.head}^{{commit}}", cwd=root)
        tree = anchored_tree_id(root, source, include_working_tree=False)
    else:
        source = "working-tree"
        tree = anchored_tree_id(root, "HEAD", include_working_tree=True)
    print(json.dumps({"base": base, "source": source, "tree": tree}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
