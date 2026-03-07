# Nexy

Nexy is a modular meta-framework combining Python (FastAPI, Jinja2) and modern Frontend frameworks (React, Vue, Svelte) with a file‑based component system (.nexy/.mdx) and a developer‑friendly CLI.

Badges

- CI: coming soon
- Coverage: coming soon
- License: MIT

Quick Start

1. Create and activate a Python 3.12+ environment.
2. Install dependencies:

   pip install -e .[dev]

3. Run dev server:

   nx dev

4. Build components:

   nx build

Makefile

- Lint: make lint
- Type check: make typecheck
- Tests: make test
- Performance: make perf

Project Structure

- nexy/ Python framework (CLI, builder, compiler, router)
- extensions/vscode/ VS Code extension for .nexy
- docs/ Documentation and performance reports

Design Principles

- SOLID and KISS by construction (post‑refactor plan in .rapport/summary.md).
- Strict typing (mypy, TypedDict, Enums, Pydantic at boundaries).
- i18n: English by default, strings extracted to i18n/en.json.

Contributing

See CONTRIBUTING.md for the style guide, commit conventions and development workflow.

Architecture Decisions

ADR records will be added under docs/adr as features evolve.

## Release Tag Planning

| Version | Target Date | Status   |
|--------:|-------------|----------|
| 2.0.0   | 2026-03-31  | Planned  |
| 2.0.1   | 2026-04-15  | Planned  |
| 2.1.0   | 2026-05-15  | Planned  |

Run check:

  make docs.check
