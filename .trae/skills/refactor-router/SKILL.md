---
name: "refactor-router"
description: "Splits file-based router into cohesive modules and registers routes safely. Invoke when router grows >150 LOC or mixes concerns."
---

# Router Refactor

Purpose

- Decompose file-based routing into discovery, introspection, and registration layers.
- Reduce module size, improve testability and maintainability.

When to Invoke

- Router monolith exceeds 150 LOC or mixes discovery/introspection/binding.
- Tests are hard to write due to tight coupling.

Outputs

- New modules (proposal):
  - route_discovery.py
  - route_introspection.py
  - route_registration.py
  - http_map.py
- Interfaces
  - discover_routes(root) -> Iterable[RouteSpec]
  - introspect(spec) -> HandlerSpec
  - register(app, spec) -> None

Guidelines

- Preserve external API. Write migration notes if symbols change.
- Add unit tests for each new module. Keep behavior identical.
- Ensure complexity targets and remove duplication.

Examples

- "Refactor file_based_routing/__init__.py into 4 modules with tests."

