# Nexy Roadmap — Task Board

This directory contains the structured plan to evolve Nexy into a world-class framework.

## Vision & Objectives
Nexy must surpass Django, Next.js, and Astro in **DX** and **Performance**.
- **KISS** (Keep It Simple, Stupid)
- **TDD** (Test-Driven Development)
- **SOLID** (Clean Architecture)

## Architecture Roadmap

*(Phases 00 to 04 have been completed and cleaned up)*

### [05. The Next.js Killer (Road to 10/10)](./05-nextjs-killer/)
These are the advanced architectural changes required to bring Nexy from an 8.5/10 to a perfect 10/10, enabling true Serverless deployment and instant HMR.

1. **[AST Template Compiler](./05-nextjs-killer/01-ast-template-compiler.md)**: Replace regex parsing with a robust HTML AST to handle deeply nested components safely.
2. **[In-Memory VFS](./05-nextjs-killer/02-in-memory-vfs.md)**: Eliminate physical disk writes (`__nexy__/`). Compile Python and HTML directly into RAM for Serverless compatibility.
3. **[True Python HMR](./05-nextjs-killer/03-true-hmr-reload.md)**: Stop cold-killing Uvicorn. Invalidate `sys.modules` in real-time to preserve Vite WebSocket connections and achieve sub-100ms hot reloads.

### [06. CLI Quality Commands](./06-cli-quality-commands/)
Unified CLI commands for type checking, formatting, and testing across Python and frontend files.

1. **[`nexy check`](./06-cli-quality-commands/01-check.md)**: Run mypy, tsc, and compile+check for .nexy/.mdx
2. **[`nexy format`](./06-cli-quality-commands/02-format.md)**: Format .py, .ts, .vue, .svelte, .nexy/.mdx
3. **[`nexy test`](./06-cli-quality-commands/03-test.md)**: Run pytest (--server) and/or vitest (--client)
4. **[Register in CLI](./06-cli-quality-commands/04-register.md)**: Wire up commands + update welcome banner

## Quality Gates (Mandatory)
Before completing any task, ensure:
```bash
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict
python -m pytest tests/ -v
```
All tasks must maintain 100% backward compatibility with native Nexy functionality.
