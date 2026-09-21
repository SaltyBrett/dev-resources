#!/usr/bin/env python3
"""
commit_attribution_scan.py — no AI tool signs its name to a commit in this repo.

THE FAILURE THIS CLOSES
-----------------------
Coding agents append attribution trailers to commit messages by default:

    Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
    Claude-Session: https://...
    🤖 Generated with [Claude Code](https://claude.com/claude-code)

The repository's own standard forbids self-referential attribution. Left to a
convention, this recurs on every commit any agent makes, and is caught only when
a human happens to read the trailer before pushing. It is precisely the class of
drift the mechanical gates exist to remove: correct behavior that depends on
somebody remembering.

This runs at the `commit-msg` stage, not `pre-commit`, because the message does
not exist when pre-commit hooks fire.

WHAT IT CHECKS
--------------
The commit message, minus comment lines, against BANNED_ATTRIBUTION below.
Matching is case-insensitive. Exit 1 blocks the commit.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
It does not strip the trailer. Rewriting a human's commit message silently is
worse than refusing it: the author should see what was added and remove it, so
the agent's default becomes visible rather than laundered.

INSTALL (per clone, both hook types)
------------------------------------
    pre-commit install --hook-type pre-commit --hook-type commit-msg

`pre-commit install` alone installs only the pre-commit hook. Without the
commit-msg hook this gate is present in config and absent in practice.

Usage:  pre-commit run --hook-stage commit-msg --commit-msg-filename <file> --all-files
        python3 scripts/commit_attribution_scan.py <commit-msg-file>

`pre-commit run --all-files` does NOT exercise this gate — it covers the pre-commit stage only, so it
reports a clean suite on a machine where this hook was never installed. Test the commit-msg stage
explicitly, in both directions: a message with a trailer must fail, a clean one must pass.

Direct invocation takes `python3` on macOS/Linux and `python` on Windows; there is no portable bare
name (docs/orchestration/knowledge/reference_precommit_interpreter.md).

Exit 0 = clean, 1 = attribution found (blocks the commit).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ==============================================================================
# CUSTOMIZE FOR YOUR PROJECT
# ==============================================================================

BANNED_ATTRIBUTION = {
    "AI co-author trailer": [
        r"^\s*co-authored-by:\s*.*\b(claude|codex|cline|copilot|cursor|gpt|gemini|grok|devin|kilo|windsurf|aider|opencode)\b",
        r"^\s*co-authored-by:\s*.*@(anthropic|openai)\.com",
    ],
    "Agent session trailer": [
        r"^\s*(claude|codex|cline|copilot)[-_]session:",
        r"^\s*generated[-_]?(with|by):",
    ],
    "Generated-with advertisement": [
        r"generated with \[?(claude|codex|cline|copilot|cursor|devin)",
        r"\bco-?authored\b.*\bai\b",
    ],
    "Robot emoji": [
        r"\U0001F916",
    ],
}

# ==============================================================================


# `git commit --verbose` appends the staged diff below a scissors line. Those diff lines are NOT
# comment-prefixed, so scanning the whole file reads the DIFF as if it were the message: staging any
# change that touches an attribution example — AGENTS.md's prime directive contains one — blocked the
# commit and told the author to remove a line they never wrote. The message is the region above the
# scissors; everything below it is git's, and git discards it.
SCISSORS = re.compile(r"^\s*#\s*-+\s*>8\s*-+\s*$")


def message_region(text: str) -> str:
    """The commit message proper — everything above the --verbose scissors line."""
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if SCISSORS.match(line):
            return "\n".join(lines[:idx])
    return text


def scan(text: str) -> list[tuple[int, str, str]]:
    """Return (line_no, category, line) for each violation."""
    violations: list[tuple[int, str, str]] = []
    for idx, line in enumerate(message_region(text).splitlines(), start=1):
        if line.lstrip().startswith("#"):
            continue  # git's own comment lines are stripped before commit
        for category, patterns in BANNED_ATTRIBUTION.items():
            for pattern in patterns:
                if re.search(pattern, line, flags=re.IGNORECASE):
                    violations.append((idx, category, line.strip()))
                    break
            else:
                continue
            break
    return violations


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: commit_attribution_scan.py <commit-msg-file>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    if not path.is_file():
        print(f"commit message file not found: {path}", file=sys.stderr)
        return 2

    violations = scan(path.read_text(encoding="utf-8"))

    if not violations:
        print("COMMIT ATTRIBUTION GATE: PASS")
        return 0

    print("COMMIT ATTRIBUTION GATE: BLOCKED", file=sys.stderr)
    for line_no, category, line in violations:
        print(f"  line {line_no}  [{category}]  {line}", file=sys.stderr)
    print(
        "\nThis repository does not carry AI attribution in commit messages.\n"
        "Remove the offending line(s) and commit again. Do not use --no-verify.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
