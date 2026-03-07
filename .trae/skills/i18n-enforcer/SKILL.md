---
name: "i18n-enforcer"
description: "Enforces English-by-default and extracts strings to i18n JSON. Invoke when adding/modifying CLI/UX messages or localizing modules."
---

# i18n Enforcer

Purpose

- Ensure all user-facing strings default to English.
- Centralize messages under i18n JSON files for future localization.

When to Invoke

- Introducing new CLI prompts, logs, or UI strings.
- Converting existing FR strings to EN default.

Outputs

- i18n/en.json populated with new keys.
- Code updated to reference i18n helper (e.g., t(\"...\")).

Guidelines

- Keep keys namespaced (e.g., cli.*, init.*, router.*).
- Avoid concatenation; use placeholders and format safely.
- Do not change behavior; only externalize strings.

Examples

- "Extract all strings from CLI init flow to i18n/en.json."

