# Nexy Roadmap — Task Board

This directory contains the structured plan to evolve Nexy into a world-class framework.

## Vision & Objectives
Nexy must surpass Django, Next.js, and Astro in **DX** and **Performance**.
- **KISS** (Keep It Simple, Stupid)
- **TDD** (Test-Driven Development)
- **SOLID** (Clean Architecture)

## Architecture Roadmap

### [00. Foundation](./00-foundation/)
Establishing an international, professional baseline.
- **I18n**: Full English translation of code and comments.
- **Clean Console**: Zero noise, zero emojis, structured timings.

### [01. Clean Code](./01-clean-code/)
Applying KISS and SOLID principles to the core codebase.
- **Refactoring**: Deduplication of logic and consolidation of utilities.
- **Bug Fixes**: Resolving existing test failures in Scanner and Template Parser.
- **Typing**: Reaching 100% `mypy --strict` compliance.

### [02. Performance](./02-performance/)
Optimizing startup and development cycles.
- **HMR**: Intelligent hot-reloading for `.nexy` files.
- **Startup**: Target <100ms startup for small projects.
- **Incremental Compilation**: Only rebuild what changed.

### [03. Architecture](./03-architecture/)
Advanced features and modular structure.
- **Modular Router**: Improved organization for large-scale apps.
- **Runtime Modules**: Extensible system for framework features.
- **Built-in Components**: High-performance Link and Image components.

### [04. Toolchain](./04-toolchain/)
Final polish and strict quality gates.
- **Astral Toolchain**: Global formatting and linting with Ruff.
- **Test Infra**: Comprehensive conftest and integration test suite.

## Quality Gates (Mandatory)
Before completing any task, ensure:
```bash
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict
python -m pytest tests/ -v
```
All tasks must maintain 100% backward compatibility with native Nexy functionality.
