# Task 38: Write root-level project documentation

## Problem

The project root lacks proper documentation. There is no `README.md`, `CONTRIBUTING.md`, or `CHANGELOG.md` at the root level. While `tasks/README.md` has internal task documentation, end users and contributors need framework-level docs.

## What to create

### 1. `README.md` (root) — Framework overview

```markdown
# Nexy

**Python full-stack framework** — FastAPI + Jinja2 + Vite + multi-framework islands.

Nexy combines FastAPI's backend power with modern frontend tooling. Write components
in `.nexy` (Python + Jinja2) or `.mdx` files, use your favorite UI framework (React,
Vue, Svelte, Solid, Preact) for interactive islands, and get production builds via Vite.

## Quick start

```bash
pip install nexy
nx init
nx dev
```

## Features

- **File-based routing**: Drop `.nexy`, `.mdx`, or `.py` files in `src/routes/`
- **Multi-framework islands**: React, Vue, Svelte, Solid, Preact — mix freely
- **FastAPI backend**: Full async support, dependency injection, OpenAPI docs
- **Vite integration**: HMR, CSS preprocessing, TypeScript, production bundling
- **Markdown + MDX**: Write content pages in Markdown with Nexy component imports
- **SPA navigation**: `<Link>` component with client-side routing
- **SSG ready**: Static site generation via `nx build`

## Project structure

```
├── src/routes/         # File-based routes (.nexy, .mdx, .py)
├── public/             # Static files (served at /)
├── nexyconfig.py       # Framework configuration
├── __nexy__/           # Build output (gitignored)
└── vite.config.ts      # Vite configuration
```
```

### 2. `CONTRIBUTING.md` — For contributors

```markdown
# Contributing to Nexy

Nexy follows **KISS · TDD · SOLID** principles:
- **KISS**: Simplest working code. Functions < 20 lines, classes < 10 methods.
- **TDD**: Write test first (red) → minimal code (green) → refactor.
- **SOLID**: One responsibility per file/class.

## Development setup

```bash
git clone https://github.com/nexy/nexy
cd nexy
uv sync
```

## Quality gates

```bash
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict
python -m pytest tests/ -v
```

## Task workflow

See `tasks/README.md` for the current refactoring plan.
```

### 3. `CHANGELOG.md` — Starting from version 2.0.8

```markdown
# Changelog

## [2.0.8] - Unreleased

### Added
- `<Link>` component with SPA navigation
- `nexy/runtime/injection.py` — DI container via ServiceProvider
- Root documentation (README, CONTRIBUTING, CHANGELOG)

### Fixed
- Static files now served at root `/` (Vercel-compatible)
- `nexy/core/__init__.py` naming (was `__init.py`)
- All print statements unified via rich console

### Changed
- Frontmatter `---` is now optional for .nexy/.mdx files
- Router structure improved for SOLID compliance
- Utils organized into module-specific subdirectories
```

## Verify

- [ ] `README.md` exists at project root
- [ ] `CONTRIBUTING.md` exists at project root
- [ ] `CHANGELOG.md` exists at project root
- [ ] All docs are in English
- [ ] No broken links or placeholders
