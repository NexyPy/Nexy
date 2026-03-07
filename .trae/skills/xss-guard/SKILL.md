---
name: "xss-guard"
description: "Prevents XSS with safe defaults and compatibility toggles. Invoke when touching template rendering or exposing user content."
---

# XSS Guard

Purpose

- Apply XSS protections that do not break existing components or outputs.
- Provide a compatibility layer: safe-by-default with explicit opt-outs.

When to Invoke

- Editing template generation/parsing, rendering HTML/MD, or exposing user content in UI.

Approach

- Safe defaults: enable autoescape for HTML contexts.
- Compatibility: support explicit `|safe` or whitelisting of trusted fragments to preserve component behavior.
- Boundary validation: sanitize and normalize inputs before rendering.

Guidelines

- Do not change semantics of existing components without a flag or migration note.
- Prefer contextual escaping over blanket stripping.
- Add tests that assert both safety and unchanged output for trusted cases.

Examples

- "Introduce autoescape with a whitelist for pre-rendered components to avoid breaking them."
- "Sanitize markdown HTML while preserving intended custom components."

