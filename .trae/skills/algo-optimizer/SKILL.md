---
name: "algo-optimizer"
description: "Optimizes hot paths to ≤ O(n log n), removes N+1, adds LRU cache/streaming. Invoke after profiling or when performance targets are set."
---

# Algorithm Optimizer

Purpose

- Identify and optimize hot paths in Python and TypeScript.
- Ensure complexity targets and remove unnecessary nested loops.
- Replace N+1 with batched operations and add local LRU caches.
- Stream large assets where applicable.

When to Invoke

- Performance goals are defined or regressions detected.
- Profiling reveals hotspots or redundant computations.

Guidelines

- Start with measurement; protect outcomes with perf tests (`make perf`).
- Keep behavior identical; document trade-offs.
- Use standard library tools first; avoid heavy deps.

Examples

- "Batch router discovery I/O and memoize introspection results."
- "Add functools.lru_cache for repeated template parsing metadata."

