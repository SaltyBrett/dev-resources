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

This repository is public (template decision 2026-09-25-001), so GitHub's own secret scanning
runs on it; local `pre-commit` is still the control that refuses the commit rather than
reporting it afterwards, which is why it is not optional:

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
so nothing here is a copy (its decision 2026-09-23-005). The template is public, so the config
pins it by a plain https URL that needs no credential, from `~/.cache/pre-commit` and from the
`gates` workflow alike (`.github/workflows/gates.yml` runs the same suite on every push). While
the template was private the pin had to name the `github.com-personal` ssh alias, because
pre-commit's cache sits outside the `includeIf` that routes `~/code/personal` through the
personal identity; the template's `reference_published_hooks` entry keeps that measurement.
The two content gates judge `docs/personas/` and `docs/orchestration/knowledge/`, the layout
the template's gates expect.

## What stays out

Anything CUI or ITAR/EAR controlled. Source code written on the clock. Customer, program
or contract identifiers. Connection strings, tenant and subscription IDs, internal
hostnames. GitHub.com commercial is not an authorized environment for CUI regardless of
repository visibility — "I made it private" is not a compliance argument.
