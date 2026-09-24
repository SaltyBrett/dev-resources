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
| `scripts/` | The one gate this repo needs (see below) |

## Why only two gates

A private repository on a free GitHub account gets **no** secret scanning and no push
protection — those run on public repositories only. Local `pre-commit` is therefore the
only such control here, which is why it is not optional:

```bash
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type commit-msg
```

**Both `--hook-type` flags are required.** Plain `pre-commit install` registers only the
pre-commit hook, leaving the commit-msg gate present in config and inert in practice.

| Gate | Stage | Blocks |
| --- | --- | --- |
| `gitleaks` | `pre-commit` | a hardcoded secret |
| `commit_attribution_scan.py` | `commit-msg` | an AI attribution trailer in a commit message |

`scripts/commit_attribution_scan.py` is a copy from the template rather than a shared
dependency. That is a known duplication: the template publishes no
`.pre-commit-hooks.yaml`, so it cannot yet be consumed as a hook repository. One small
file, rarely changed — revisit if it drifts.

## What stays out

Anything CUI or ITAR/EAR controlled. Source code written on the clock. Customer, program
or contract identifiers. Connection strings, tenant and subscription IDs, internal
hostnames. GitHub.com commercial is not an authorized environment for CUI regardless of
repository visibility — "I made it private" is not a compliance argument.
