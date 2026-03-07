Nexy Performance Benchmarks

- Metrics
  - cli_cold_ms: Time to import and initialize Nexy CLI (cold start).
  - template_gen_ms: Synthetic time to trigger a minimal compile.
- Files
  - baseline.json: Stored baseline; updated on first run.
  - latest.json: Latest run results.

Run:

  make perf

Policy:
- The CI should fail if regression > 5% on any metric.

