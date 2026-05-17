# Nexy Refactor Tasks

## Philosophy

- **Better than Vite DX**: Nexy aims to beat Vite on developer experience. That means:
  - Sub-second startup (target: <500ms for small projects)
  - Sub-100ms HMR for `.nexy` changes  
  - Browser error overlay styled like Vite/Nuxt
  - Clean terminal output with timings, no noise
  - Actionable error messages with fix suggestions
- **Zero emoji in console**: Only simple ASCII symbols already present (`✓`, `✗`, `✘`, `↺`). No emoji (🚀, 😊, ⚠️, etc.), no Unicode art.
- **All code in English**: No French comments, variable names, or console strings. This is an international framework.
- **TDD**: RED (test fails) → GREEN (make it pass) → REFACTOR (clean up). One assertion per test.

## Task quality for AI agents

Each task must include:
1. **Exact file paths and line numbers** — the agent doesn't need to search
2. **Before/after code snippets** — exact oldString → newString for `edit` tool
3. **Search commands** — so the agent can verify its own work
4. **Test/Vet commands** — `ruff check`, `mypy`, `pytest`
5. **Clear Definition of Done** — binary pass/fail checklist

## Execution order

```
# Phase 0: Internationalization (high priority, no deps)
  26-translate-french-to-english    (no deps)
  27-clean-console-output-no-emoji  (no deps)

# Phase 1: Clean code (parallel-safe)
  01-fix-scanner-invalid-tests      (no deps)
  02-deduplicate-normalize          (no deps)
  03-deduplicate-port-finding       (no deps)
  04-merge-file-folder-path         (no deps)
  05-remove-useroute-alias          (no deps)
  06-fix-task-job-stubs             (no deps)
  07-rename-pasermodel              (no deps)
  08-remove-componentstring         (no deps)
  10-add-autoescape                 (no deps)
  12-merge-error-modules            (no deps)
  15-remove-dead-code               (no deps)
  16-fix-except-silent              (no deps)
  17-write-conftest                 (no deps)

  09-move-cli-utilities             (depends on: 03, 04)
  11-fix-config-singleton           (depends on: 26, 07)
  13-write-missing-tests            (depends on: 17)
  14-builder-propagate-errors       (depends on: 13)

# Phase 2: DX & HMR (sequential — each builds on the previous)
  23-optimize-dev-startup           (depends on: 19, 26)
  19-incremental-compilation        (depends on: 14)
  18-hmr-uvicorn-reload             (depends on: 09, 27)
  20-faster-import-hot-reload       (depends on: 18)
  24-vite-hmr-coordination          (depends on: 20)
  21-browser-error-overlay          (depends on: 14)
  22-dev-server-status-bar          (depends on: 09)
  25-improve-cli-error-messages     (depends on: 16, 27)
  20-faster-import-hot-reload       (depends on: 18)
  24-vite-hmr-coordination          (depends on: 20)
  22-dev-server-status-bar          (depends on: 09)

# Phase 3: Astral toolchain (final polish — must run last)
  28-astral-toolchain-integration   (depends on: all of Phase 1 + 2)
```

## Quality gates (every task)

```bash
# Run in order — stop on first failure
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict
python -m pytest tests/ -v
```

Run Phase 0 first (26, 27) so all subsequent tasks work with English-only, emoji-free code. Then do Phase 1 parallel-safe tasks, then dependent tasks, then Phase 2. Phase 3 (28) must run last — after all code changes are done, as it applies `ruff format` globally.

## Principles
- **KISS**: simplest working code. No premature abstraction. Functions < 20 lines, classes < 10 methods.
- **SOLID**: one responsibility per file. Depend on abstractions (`Protocol`), inject via `nexy/runtime/injection.py`.
- **Zero regressions**: full test suite must pass after each task.
