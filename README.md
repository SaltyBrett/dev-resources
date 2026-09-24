# dev-resources

Durable development resources shared across every project: the persona registry, runbooks, and
reference knowledge. Renamed from `dev-handbook` on 2026-09-23; how projects consume it is decided
in the template (`agentic-dev-template`, decision 2026-09-23-002).

Prose, not code. Anything that needs governance, sprint state or a compliance gate
belongs in a project created from
[`agentic-dev-template`](https://github.com/SaltyBrett/agentic-dev-template), not here —
this repository is deliberately small.

## Contents

| Path | What it holds |
| --- | --- |
| `runbooks/` | Step-by-step procedures, each verified by execution rather than planned |
| `docs/personas/` | The persona registry every project syncs from (template decision 2026-09-23-007); append-only by version, held to it by `persona-lint` on every commit here. Grown only through a project's `resources_sync.py --publish` |

## Gates

A private repository on a free GitHub account gets **no** secret scanning and no push
protection — those run on public repositories only. Local `pre-commit` is therefore the
only such control here, which is why it is not optional:

```bash
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

**Both `--hook-type` flags are required.** Plain `pre-commit install` registers only the
pre-commit hook, leaving the commit-msg gate present in config and inert in practice.

| Gate | From | Stage | Blocks |
| --- | --- | --- | --- |
| `gitleaks` | its upstream repository | `pre-commit` | a hardcoded secret |
| `persona-lint` | the template, by `rev` | `pre-commit` | a persona without the required frontmatter keys, a slug that differs from its filename, or sections other than the three |
| `kb-frontmatter-scan` | the template, by `rev` | `pre-commit` | a knowledge entry whose frontmatter is unreadable, or read differently by the two gates that consume it, or missing from the index |
| `commit-attribution` | the template, by `rev` | `commit-msg` | an AI attribution trailer in a commit message |

The three template gates are consumed from `agentic-dev-template`'s `.pre-commit-hooks.yaml`,
so nothing here is a copy (its decision 2026-09-23-005). The template is private, and
pre-commit clones it into `~/.cache/pre-commit`, outside the `includeIf` that routes
`~/code/personal` through the personal identity, so the config names the `github.com-personal`
ssh alias from `runbooks/Mac_Dev_Environment_Setup_Runbook.md` directly. A GitHub Actions run
would need a deploy key or token secret to clone it, which is why there is none here yet. The
two content gates are skipped until this repository holds `docs/personas/` and
`docs/orchestration/knowledge/`, the layout the template's gates judge.

## What stays out

Anything CUI or ITAR/EAR controlled. Source code written on the clock. Customer, program
or contract identifiers. Connection strings, tenant and subscription IDs, internal
hostnames. GitHub.com commercial is not an authorized environment for CUI regardless of
repository visibility — "I made it private" is not a compliance argument.
