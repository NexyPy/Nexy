---
name: "init-templates"
description: "Implements nexy init: interactive survey, registry fetch, and silent template cloning. Invoke when enhancing project scaffolding."
---

# Init Templates

Purpose

- Provide invisible-to-user flow for `nexy init`:
  - Ask language/stack/license via interactive survey.
  - List available templates via REST registry.
  - Silent git clone of chosen template branch.

When to Invoke

- User requests template-based initialization or scaffolding improvements.

Outputs

- CLI flags: -t/--template to pick template.
- Registry integration and graceful error handling/rollback.
- MIGRATION notes if behavior changes.

Guidelines

- Non-interactive mode should be supported for CI (env vars/flags).
- Validate inputs; log concise progress in English.

Examples

- "Add --template with REST listing and clone selected branch."

