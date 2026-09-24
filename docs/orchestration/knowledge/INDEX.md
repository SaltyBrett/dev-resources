# Resource Knowledge — Index

Reference knowledge that belongs to no one project: machines, tools and workflows, never a
project's decisions. Every entry declares `source: dev-resources` and `teaches: []` in its
frontmatter; a project pulls these through its `scripts/resources_sync.py`, which merges the rows
below into the project's own index by slug (agentic-dev-template decision 2026-09-23-007). The
`kb-frontmatter-scan` hook consumed from the template keeps every entry indexed and readable.

## Entries

| Slug | Summary | Type |
|------|---------|------|
| [reference_macos_toolchain](reference_macos_toolchain.md) | Silent macOS defects: per-clone pre-commit hook with a baked-in interpreter path, Windows git config, case-insensitive APFS vs case-sensitive git, Microsoft fonts absent, and the per-app consent gate on Downloads/Desktop/Documents that presents as a hung command. | reference |
<!-- Add one row per knowledge entry above this line, newest first -->
