---
name: "release-orchestrator"
description: "Prepares CHANGELOG, version bump, MIGRATION.md, and perf report. Invoke when cutting a release."
---

# Release Orchestrator

Purpose

- Coordinate release artifacts without changing runtime behavior.
- Ensure docs and performance evidence are up-to-date.

When to Invoke

- Before tagging a new version or publishing to a registry/marketplace.

Outputs

- CHANGELOG updates (Conventional Commits).
- MIGRATION.md for breaking changes with safe migration steps.
- docs/perf updated with before/after benchmarks.

Guidelines

- Keep runtime untouched; changes are docs, metadata, and tagging.
- Cross-check CI status (lint/typecheck/test/perf) is green.

Examples

- "Draft release notes with perf deltas and migration steps."

