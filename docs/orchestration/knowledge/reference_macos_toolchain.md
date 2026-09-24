---
name: macOS toolchain constraints for this framework
description: 'Silent portability and environment defects that surface when this framework is cloned on macOS: the per-clone pre-commit hook with a baked-in interpreter path, Windows-originated git config, case-insensitive APFS versus case-sensitive git, Microsoft fonts absent, and the per-app consent gate on Downloads/Desktop/Documents that presents as a hung command. Read before the first clone on any new machine.'
teaches: []
verified: 2026-09-23
source: dev-resources
metadata:
  type: reference
---

# Reference: macOS toolchain constraints for this framework

> Durable learning. Captured when the framework moved from Windows to macOS (Apple Silicon).
> Wikilink: `[[reference_macos_toolchain]]`

## Why this entry exists

The framework was authored on Windows, and portability defects surfaced on the first macOS clone.
They share a failure mode: nothing errors. The output is just wrong, the gate quietly stops
protecting you, or a command never returns. Recording them so they cannot recur on the next machine.

## 1. The pre-commit hook is per-clone, and it bakes in an interpreter path

`.git/hooks/` is never committed. A clone has no hook until
`pre-commit install --hook-type pre-commit --hook-type commit-msg` runs. Worse, the
generated hook hardcodes the absolute interpreter path of the machine that generated it:

    INSTALL_PYTHON='C:\Users\<user>\AppData\Local\...\python.exe'

On macOS that path fails the `-x` test and the hook falls through to `command -v pre-commit`. It
degrades rather than dying, but only when `pre-commit` is on PATH. **The compliance gate must not
depend on a fallback branch.**

**Rule:** `pre-commit install --hook-type pre-commit --hook-type commit-msg` is a mandatory step in
every clone, on every machine. Both flags: plain `pre-commit install` writes only
`.git/hooks/pre-commit`, leaving every commit-msg-stage gate inert
([[reference_commit_attribution_gate]]). Verify with `pre-commit run --all-files` before the first
commit, not after — and note that it exercises only the pre-commit stage, so a commit-msg gate needs
`pre-commit run --hook-stage commit-msg --commit-msg-filename <file>` or a real trial commit.

## 2. Windows-originated git config travels in the clone

A repo cloned on Windows carries `filemode = false`, `symlinks = false`, `ignorecase = true`.

- `filemode = false` masks executable-bit changes. On macOS this hides `chmod +x` on `scripts/`.
- `ignorecase = true` is correct for default APFS, which is case-insensitive. Leave it.

**Rule:** set `core.fileMode true` and `core.autocrlf input` on macOS clones.

## 3. macOS is case-insensitive and git is not

APFS defaults to case-insensitive. A rename that only changes case may silently no-op. This is
sharpest in projects where filenames map to object names downstream, for example dbt models mapping
to relation names.

**Rule:** case-only renames use `git mv --force old.sql New.sql`, never a plain `mv`.

## 4. Microsoft fonts are absent on macOS

`scripts/md_to_docx.py` originally emitted Calibri, Calibri Light, and Consolas. None ship with
macOS. Without Microsoft Office installed, every generated `.docx` renders with substituted fonts,
which breaks the house style without any error.

**Current pairing:** Titillium Web (headings) / Catamaran (body) / Menlo (code). The first two are
free Google Fonts; Menlo ships with macOS.

**Rule:** any font named in a generator must be verified present on every OS that will render the
output. Prefer fonts that are free and installable over fonts that happen to be on one machine.
Install on macOS with:

    brew install --cask font-titillium-web font-catamaran

## 5. Downloads, Desktop and Documents are gated per app, and the gate looks like a hang

macOS gates access to `~/Downloads`, `~/Desktop` and `~/Documents` per *application*, not per user.
The first time a given terminal app (Terminal, iTerm2, VS Code, the Claude Code host) tries to read a
file in one of those folders, macOS suspends the call and raises a consent dialog. Until someone
answers it, the command sits there. **It is not slow I/O and it is not a broken script — it is a
dialog waiting for a click**, and it is routinely invisible: behind the frontmost window, or on
another Space or display entirely.

The diagnostic that identifies it in one step is the difference between two commands on the same path:

    ls ~/Downloads/file.csv      # returns immediately
    cp ~/Downloads/file.csv .    # hangs

`ls` only **stats** the file — metadata, which the gate permits. `cp` **reads its contents**, which is
what the gate covers. So a listing that works is no evidence of access. Anything that opens the file
blocks: `cp`, `cat`, `python open()`, `git add` of a file under one of those folders.

**Rule:** if a file operation under Downloads, Desktop or Documents does not return, do not kill it
and do not start debugging the script. Cycle through Spaces and displays and look for the consent
dialog first. Grant standing access in **System Settings → Privacy & Security → Files and Folders**,
under the terminal app's own entry — each app is authorized separately, so approving Terminal does
nothing for VS Code.

Keep project work out of those three folders where you can. A repo cloned under `~/code` is subject to
none of this.

## 6. Symlinks are not a substitute for the CLAUDE.md import

Do not replace `CLAUDE.md` with a symlink to `AGENTS.md`. Two reasons: Claude Code's Edit and Write
tools refuse to write through a symlink, and Git checks committed symlinks out as plain text files
on Windows without `core.symlinks`, leaving collaborators with a one-line CLAUDE.md in place of the
governance bridge. The `@AGENTS.md` import in `CLAUDE.md` is the portable pattern and is already in
place. Keep it.

## 7. The shell is zsh, and sed and awk are BSD

Three probe commands in one session failed on shell syntax rather than on the gate they were
testing, and each failure looked like the gate had not run:

- `${PIPESTATUS[0]}` prints nothing in zsh; the array is `${pipestatus[1]}`, one-indexed. An
  empty exit code after a pipe is the shell, not the gate.
- BSD `sed` has no `0,/re/` address form, and BSD `awk -v` refuses a multi-line string. Both
  fail with a one-line error that is easy to read past.

**Rule:** capture a gate's exit code without a pipe: redirect its output to a file and echo `$?`
on the next line. For multi-line file surgery in a probe, write a short `python3` heredoc rather
than reaching for sed or awk. Plain `sed -i '' 's/a/b/'` substitutions are fine.
