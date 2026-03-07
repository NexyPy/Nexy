---
name: "perf-guard"
description: "Runs perf benchmarks and enforces ≤5% regression gate. Invoke before merges, in CI, or after performance-sensitive changes."
---

# Performance Guard

Purpose

- Execute performance benchmarks and compare against baseline.
- Fail the task if regression exceeds 5%.

When to Invoke

- Pre-merge checks, CI pipelines, or after optimizing/altering hot paths.

Inputs

- scripts/perf.py, docs/perf/baseline.json

Outputs

- docs/perf/latest.json with metrics (cli_cold_ms, template_gen_ms)
- Non-zero exit on regression > 5%

Guidelines

- Use `make perf` to run the suite.
- Update baseline only when improvements are consistent and expected.

Examples

- "Run perf guard after changing builder caching strategy."

