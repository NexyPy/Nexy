---
name: "ci-bootstrap"
description: "Generates CI pipelines for lint/typecheck/test/perf gates. Invoke when setting up or updating continuous integration."
---

# CI Bootstrap

Purpose

- Provide a standard CI pipeline that enforces quality and performance gates.

When to Invoke

- Initial project industrialization or CI updates.

Pipeline Stages

- Lint: Python (ruff), TS (eslint).
- Typecheck: mypy strict; tsc --noEmit.
- Test: pytest and extension tests if present.
- Perf: make perf with ≤5% regression gate.

Guidelines

- Cache dependencies; run on Linux, Windows if needed.
- Fail fast and keep jobs parallel for speed.

Examples

- "Add GitHub Actions workflow running make lint/typecheck/test/perf."

