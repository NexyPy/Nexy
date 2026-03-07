---
name: "audit-technical"
description: "Audits codebase for SOLID/KISS/TDD and debt scoring. Invoke when user asks for audits, quality reports, or refactor prioritization."
---

# Technical Audit

Purpose

- Scan Python/TypeScript modules, packages, classes, methods and functions.
- Detect SOLID, KISS, and TDD violations; compute technical debt scores.
- Output a consolidated report under .rapport with priorities and next steps.

When to Invoke

- User requests a codebase audit, quality assessment, or refactor roadmap.
- Before large refactors, or to track improvements over time.

Inputs

- Repository root, languages: Python 3.12+, TypeScript.

Outputs

- .rapport/summary.md and per-module sections with:
  - Violations found and rationale
  - Debt score and priority
  - Suggested refactors and complexity targets

Guidelines

- Prefer static analysis and repository-native tools (mypy, ruff, eslint, tsc).
- Use repository tests to validate changes; never commit in this skill.
- Keep descriptions precise, action-oriented, and reproducible.

Examples

- "Audit Nexy framework focusing on compiler and router."
- "Generate a prioritized list of modules exceeding 150 LOC."

