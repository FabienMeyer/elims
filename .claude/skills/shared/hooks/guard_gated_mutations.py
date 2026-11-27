"""PreToolUse guard that enforces ELIMS delivery gates on shell commands.

Claude Code runs this hook before every Bash or PowerShell tool call. The hook
reads the tool input from stdin and prints a permission decision:

- ``deny``: the action is never an agent action in the ELIMS workflow, such as
  merging a pull request, force-pushing, pushing to the default branch, or
  changing the ``rdy-to-implement`` label directly.
- ``ask``: the action mutates GitHub or a remote and needs explicit human
  authorization, such as ``git push``, ``gh pr create``, or a bundled script
  run with ``--apply``. In a headless run with no human, the call is refused.
- no output: the command is not gated.

The guard is a deterministic backstop for the skill instructions, not a
sandbox. It inspects the command text, so a program that starts ``gh`` or
``git`` itself (for example ``python -c "subprocess.run(...)"``) is not seen.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from collections.abc import Iterator

READY_LABEL = "rdy-to-implement"
DEFAULT_BRANCHES = frozenset({"main", "master"})
MAX_NESTING = 3

SHELL_WRAPPERS = frozenset({"bash", "sh", "zsh", "pwsh", "powershell", "cmd"})
SHELL_COMMAND_FLAGS = frozenset({"-c", "-command", "/c", "-encodedcommand"})
PREFIX_WORDS = frozenset({"sudo", "command", "exec", "env", "nohup", "time", "&"})

GIT_OPTIONS_WITH_VALUE = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"})
GH_OPTIONS_WITH_VALUE = frozenset({"-R", "--repo", "--hostname"})

GH_API_FIELD_FLAGS = frozenset({"-f", "-F", "--field", "--raw-field", "--input"})

# gh subcommands that never belong to an agent in the ELIMS workflow.
GH_DENY = {
    ("pr", "merge"): "Merging is a separate human gate. Merge the pull request yourself.",
    ("issue", "delete"): "Deleting an issue is irreversible and outside the ELIMS workflow.",
    ("issue", "transfer"): "Transferring an issue is outside the ELIMS workflow.",
    ("repo", "delete"): "Deleting a repository is outside the ELIMS workflow.",
    ("repo", "archive"): "Archiving a repository is outside the ELIMS workflow.",
    ("repo", "rename"): "Renaming a repository is outside the ELIMS workflow.",
    ("release", "delete"): "Deleting a release is outside the ELIMS workflow.",
    ("secret", "set"): "Secrets must be managed by a human in GitHub settings.",
    ("secret", "delete"): "Secrets must be managed by a human in GitHub settings.",
    ("variable", "set"): "Actions variables must be managed by a human in GitHub settings.",
    ("variable", "delete"): "Actions variables must be managed by a human in GitHub settings.",
    ("auth", "token"): "Printing a GitHub token would expose a credential in the transcript.",
}

# gh subcommands that mutate GitHub and need explicit human authorization.
GH_ASK = {
    "pr": {"create", "edit", "ready", "close", "reopen", "comment", "review", "lock", "unlock", "update-branch"},
    "issue": {"create", "edit", "close", "reopen", "comment", "lock", "unlock", "pin", "unpin", "develop"},
    "label": {"create", "edit", "delete", "clone"},
    "release": {"create", "edit", "upload"},
    "project": {
        "create",
        "edit",
        "close",
        "delete",
        "copy",
        "link",
        "unlink",
        "mark-template",
        "field-create",
        "field-delete",
        "item-add",
        "item-archive",
        "item-create",
        "item-delete",
        "item-edit",
    },
    "repo": {"create", "edit", "fork", "sync", "set-default"},
    "workflow": {"run", "enable", "disable"},
    "run": {"rerun", "cancel", "delete"},
    "ruleset": {"create", "edit", "delete"},
}

GIT_FORCE_FLAGS = frozenset({"-f", "--force", "--mirror", "--delete", "-d", "--prune", "--force-if-includes"})

Decision = tuple[str, str]


def tokenize(command: str) -> list[str] | None:
    """Split a command into words and shell operators. Return None if unparseable."""
    text = command.replace("`\r\n", " ").replace("`\n", " ").replace("\r\n", "\n").replace("\n", " ; ")
    lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:
        return None


def segments(tokens: list[str]) -> Iterator[list[str]]:
    """Yield the simple commands between shell operators such as ``&&`` and ``|``."""
    current: list[str] = []
    for word in tokens:
        if word and all(character in "();<>|&" for character in word):
            if current:
                yield current
            current = ["&"] if word == "&" else []
            continue
        current.append(word)
    if current:
        yield current


def program_name(word: str) -> str:
    name = re.split(r"[\\/]", word)[-1].lower()
    return name.removesuffix(".exe")


def strip_prefix(words: list[str]) -> list[str]:
    """Remove environment assignments and wrapper words before the program name."""
    index = 0
    while index < len(words):
        word = words[index]
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", word) or word.lower() in PREFIX_WORDS:
            index += 1
            continue
        break
    return words[index:]


def skip_options(words: list[str], with_value: frozenset[str]) -> list[str]:
    """Remove leading global options so that the subcommand comes first."""
    index = 0
    while index < len(words) and words[index].startswith("-"):
        option = words[index].split("=", 1)[0]
        index += 2 if option in with_value and "=" not in words[index] else 1
    return words[index:]


def mentions_ready_label(words: list[str]) -> bool:
    return any(READY_LABEL in word for word in words)


def current_branch() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],  # noqa: S607 - git is resolved from PATH
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
            cwd=os.environ.get("CLAUDE_PROJECT_DIR") or None,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def check_git(args: list[str]) -> Decision | None:
    args = skip_options(args, GIT_OPTIONS_WITH_VALUE)
    if not args or args[0] != "push":
        return None
    push_args = args[1:]
    for word in push_args:
        option = word.split("=", 1)[0]
        if option in GIT_FORCE_FLAGS or option.startswith("--force-with-lease"):
            return "deny", f"`git push {word}` can rewrite or delete remote history. Run it yourself if it is intended."
    positional = [word for word in push_args if not word.startswith("-")]
    refspecs = positional[1:]
    for refspec in refspecs:
        if refspec.startswith(("+", ":")):
            return "deny", f"Refspec `{refspec}` force-updates or deletes a remote branch."
        target = refspec.split(":")[-1].removeprefix("refs/heads/")
        if target in DEFAULT_BRANCHES:
            return "deny", f"Pushing to `{target}` bypasses the pull-request gate. Push a work branch instead."
    if not refspecs:
        branch = current_branch()
        if branch is None or branch in DEFAULT_BRANCHES:
            shown = branch or "an unknown branch"
            return "deny", f"`git push` from {shown} could update the default branch. Push a named work branch."
    return "ask", "`git push` publishes commits to the remote. It needs explicit human authorization."


def check_gh_api(args: list[str]) -> Decision | None:
    method = None
    has_fields = False
    for index, word in enumerate(args):
        option, _, inline = word.partition("=")
        if option in {"-X", "--method"}:
            method = (inline or (args[index + 1] if index + 1 < len(args) else "")).upper()
        elif option in GH_API_FIELD_FLAGS:
            has_fields = True
    text = " ".join(args)
    is_graphql = any(word.strip("/") == "graphql" for word in args if not word.startswith("-"))
    if is_graphql:
        mutating = re.search(r"\bmutation\b", text) is not None
    else:
        mutating = (method or ("POST" if has_fields else "GET")) != "GET"
    if not mutating:
        return None
    if READY_LABEL in text:
        return "deny", f"Only the issue publisher script may apply `{READY_LABEL}`, after review and human approval."
    if is_graphql and "mergePullRequest" in text:
        return "deny", "Merging is a separate human gate. Merge the pull request yourself."
    if re.search(r"/pulls/\d+/merge\b", text):
        return "deny", "Merging is a separate human gate. Merge the pull request yourself."
    return "ask", "`gh api` with a mutating request changes GitHub state. It needs explicit human authorization."


def check_gh(args: list[str]) -> Decision | None:
    args = skip_options(args, GH_OPTIONS_WITH_VALUE)
    if not args:
        return None
    if args[0] == "api":
        return check_gh_api(args[1:])
    if len(args) < 2:
        return None
    group, action = args[0], args[1]
    if (group, action) in GH_DENY:
        return "deny", GH_DENY[(group, action)]
    if group in {"issue", "pr"} and action == "edit" and mentions_ready_label(args):
        return "deny", f"Only the issue publisher script may apply `{READY_LABEL}`, after review and human approval."
    if group == "label" and action == "delete" and mentions_ready_label(args):
        return "deny", f"`{READY_LABEL}` is a workflow gate label. Do not delete it."
    if action in GH_ASK.get(group, set()):
        return "ask", f"`gh {group} {action}` changes GitHub state. It needs explicit human authorization."
    return None


def check_script(words: list[str]) -> Decision | None:
    if "--apply" not in words:
        return None
    scripts = [word for word in words if word.lower().endswith(".py")]
    if not scripts:
        return None
    name = program_name(scripts[0])
    return "ask", f"`{name} --apply` mutates GitHub state. It needs explicit human authorization."


def check_segment(words: list[str], depth: int) -> Decision | None:
    words = strip_prefix(words)
    if not words:
        return None
    program = program_name(words[0])
    args = words[1:]
    if program in SHELL_WRAPPERS and depth < MAX_NESTING:
        for index, word in enumerate(args[:-1]):
            if word.lower() in SHELL_COMMAND_FLAGS:
                return evaluate(args[index + 1], depth + 1)
    if program == "git":
        return check_git(args)
    if program == "gh":
        return check_gh(args)
    return check_script(words)


def fallback(command: str) -> Decision | None:
    """Judge a command that could not be tokenized, erring towards a decision."""
    if re.search(r"\bgh\s+pr\s+merge\b", command) or re.search(r"--(add|remove)-label\W+" + READY_LABEL, command):
        return "deny", "The command could not be parsed and contains a denied ELIMS action."
    if re.search(r"\b(git\s+push|gh\s+(pr|issue|label|release|project|api)\b)|--apply\b", command):
        return "ask", "The command could not be parsed and may change remote state. Confirm it explicitly."
    return None


def evaluate(command: str, depth: int = 0) -> Decision | None:
    """Return the strictest decision for any simple command in ``command``."""
    tokens = tokenize(command)
    if tokens is None:
        return fallback(command)
    result: Decision | None = None
    for words in segments(tokens):
        decision = check_segment(words, depth)
        if decision is None:
            continue
        if decision[0] == "deny":
            return decision
        result = result or decision
    return result


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    command = payload.get("tool_input", {}).get("command")
    if not isinstance(command, str) or not command.strip():
        return 0
    decision = evaluate(command)
    if decision is None:
        return 0
    verdict, reason = decision
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": verdict,
            "permissionDecisionReason": f"ELIMS gate: {reason}",
        }
    }
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
