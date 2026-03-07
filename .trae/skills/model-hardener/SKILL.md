---
name: "model-hardener"
description: "Refactors data to immutable dataclasses, TypedDicts, Enums, Pydantic at boundaries. Invoke during model/schema changes or validation tasks."
---

# Model Hardener

Purpose

- Improve type safety and invariants for core models and configs.
- Validate inputs/outputs at boundaries with Pydantic.

When to Invoke

- Refactoring models, adding fields, or tightening contracts.
- Before exposing/consuming external interfaces.

Targets

- Dataclasses `frozen=True` where feasible.
- Replace raw dict/any with TypedDict/Enum/Typed structures.
- Pydantic models for CLI/config/HTTP boundaries.

Guidelines

- Maintain backward compatibility or provide MIGRATION notes.
- Update tests and type checks (mypy strict).

Examples

- "Harden NexyConfigModel and parsing results; remove raw dicts."

