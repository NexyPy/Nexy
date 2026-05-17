# Nexy — Agent Guide

## Philosophy (KISS · TDD · SOLID)

- **KISS**: simplest working code wins. No premature abstraction, no clever one-liners. Functions < 20 lines, classes < 10 methods.
- **TDD**: write the test first (red), minimal code to pass (green), then refactor. One assertion per test. Name: `test_<thing>_<scenario>`.
- **SOLID**: one responsibility per class/file. `TemplateParser` parses, `Builder` builds, `Router` routes. Depend on abstractions (`Protocol`), inject via `nexy/runtime/injection.py`.

## Commands (Astral toolchain — no Makefile)

```bash
# Quality gates (run in this order: lint → format → typecheck → test)
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict
python -m pytest tests/ -v

# Auto-fix
ruff check nexy/ --fix
ruff format nexy/

# Single test
python -m pytest tests/unit/nexy/parser/test_scanner.py -v

# Install dev deps
uv pip install -e ".[dev]"
```

## Architecture

| Layer | Dir | Key files |
|-------|-----|-----------|
| CLI | `nexy/cli/` | `__init__.py` (Typer app), `commands/{dev,start,build,init}.py` |
| Router | `nexy/routers/` | `app.py` (AppServer assembly), `fbrouter/` (file-based), `actions/` |
| Compiler | `nexy/compiler/` | `parser/{scanner,sanitizer,template,validator,logic}.py`, `generator/` |
| Frontend | `nexy/frontend/` | `{react,vue,svelte,solid,preact}.py` + `runtime.ts`, `vite.ts` |
| Core | `nexy/core/` | `config.py`, `models.py`, `types.py` |
| Entry | `nexy/app.py` | exports `app: FastAPI` = `AppServer().run()` |
| pkg init | `nexy/__init__.py` | exports `Audio`, `Video`, `Form`, `Import`, `Template`, `Vite` |

## Toolchain

- **Python**: hatchling build, uv for deps, >=3.12 (`.python-version` = 3.13)
- **JS/TS**: pnpm (root + `extensions/vscode/` + `packages/react/`), vite 7, eslint
- **Lint/format**: ruff for both (line-length=100, target-version=py312). No black/isort.
- **Typecheck**: mypy --strict on `nexy/` + `tsc -b` for TS
- **CLI binary**: `nx` or `nexy` → `nexy.cli:CLI`

## Gotchas

- `test_config.py` uses `hasattr` pattern — watch for config API changes.
- Integration tests (`tests/integration/`) may require project scaffolding or a temp workspace.
- `docs/` is a **separate Nexy app** with its own `.git` — do not treat as monorepo child.
- `skills/` dir contains project philosophy docs (KISS, SOLID, TDD, framework-dev).
- `nexyconfig.py` at root is the user-facing config (not `pyproject.toml`).
- `.nexy` files use `---` frontmatter delimiter for Python logic.

## Conventions

- **Branches**: `feature/*`, `fix/*`, `docs/*`, `perf/*`
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `perf:`, `test:`, `chore:`)
- **i18n**: English default; extract strings to `nexy/i18n/en/`
- **Coverage target**: ≥95% per module (CONTRIBUTING.md)
