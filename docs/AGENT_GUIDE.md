# Nexy — Agent Guide (Technical & Functional)

This document is the "Source of Truth" for AI Agents working on the Nexy framework. It details the architecture, mechanisms, and quality standards of the project.

## 1. Project Vision
Nexy aims to be the fastest Fullstack Python framework, outperforming Django, Next.js, and Astro in both DX (Developer Experience) and production performance.
- **KISS**: Keep It Simple, Stupid. Minimal abstractions.
- **TDD**: Test-Driven Development. Tests first.
- **SOLID**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.

## 2. Core Architecture

Nexy follows a layered architecture:

| Layer | Directory | Description |
| :--- | :--- | :--- |
| **CLI** | `nexy/cli/` | Entry point for users (`nx dev`, `nx build`, etc.). |
| **App Server** | `nexy/routers/app.py` | Assembler of the FastAPI application. |
| **Router** | `nexy/routers/` | Handles request dispatching. Includes `FBRouter` (File-Based) and `Actions`. |
| **Compiler** | `nexy/compiler/` | Transforms `.nexy` and `.mdx` files into Python/HTML/JS. |
| **Frontend** | `nexy/frontend/` | Integration with Vite and JS frameworks (React, Vue, Svelte, etc.). |
| **Runtime** | `nexy/runtime/` | Core execution logic and dependency injection. |
| **Core** | `nexy/core/` | Base models, configuration, and shared types. |
| **Utils** | `nexy/utils/` | Shared utilities organized in subdirectories. |

### 2.1. The Compiler Flow
1. **Scanner** (`nexy/compiler/parser/scanner.py`): Splits `.nexy` files into `logic` (Python) and `template` (HTML-like).
   - **Optional Frontmatter**: The `---` delimiters are optional. If missing, the whole file is treated as a template.
2. **Parser** (`nexy/compiler/parser/`):
   - `logic.py`: Parses Python logic via AST.
   - `template.py`: Parses the HTML-like syntax.
   - `validator.py`: Ensures syntax correctness.
3. **Generator** (`nexy/compiler/generator/`): Produces the final Python code and assets.

### 2.2. Routing Mechanisms
- **File-Based Routing (FBRouter)**: Scans `src/routes/` and maps file paths to URLs.
  - `index.nexy` -> `/`
  - `[id].py` -> `/{id}`
  - `(group)/path.nexy` -> `/path`
- **Actions**: Server-side functions callable from the client via a hashed POST endpoint.
  - Registered via `@action` decorator.
  - Managed by `ActionEngine`.

### 2.3. Frontend Integration
- **Vite Integration**: Nexy uses Vite for HMR and asset bundling.
- **SSR/SSG**: Nexy supports Server-Side Rendering and Static Site Generation.
- **Framework Agnostic**: Supports React, Vue, Svelte, Solid, and Preact.

### 2.4. Utils Organization
Utilities are grouped by responsibility in subdirectories of `nexy/utils/`:
- `common/`: Global constants and console logging.
- `server/`: Server lifecycle, ports management, and Uvicorn configuration.
- `dev/`: Development-only tools like file watchers and cache management.
- `fs/`: File system abstractions.
- `init/`: Project scaffolding and template cloning logic.
- `imports/`: Specialized import handling for the framework.

## 3. Implementation Rules for Agents

### 3.1. Coding Standards
- **Language**: ALL code (variables, comments, logs) MUST be in English.
- **No Emojis**: Terminal output must be clean and professional.
- **Type Safety**: `mypy --strict` compliance is mandatory.
- **Formatting**: Use `ruff format` (100 characters line length).
- **Linting**: Use `ruff check`.

### 3.2. Testing Strategy (TDD)
1. **Unit Tests**: Place in `tests/unit/`. One file per module.
2. **Integration Tests**: Place in `tests/integration/`.
3. **Verification**: Run `python -m pytest tests/ -v` before submitting any change.

### 3.3. File Structure Conventions
- **Single Responsibility**: One class per file if possible, or tightly related functions.
- **Imports**: Clean, absolute imports. Avoid circular dependencies.
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes.

## 4. Key Files to Know
- [app.py](file:///d:/dev/python/nexy/nexy/app.py): The main FastAPI entry point.
- [config.py](file:///d:/dev/python/nexy/nexy/core/config.py): Singleton configuration manager.
- [fbrouter/__init__.py](file:///d:/dev/python/nexy/nexy/routers/fbrouter/__init__.py): Logic for file-based routing.
- [scanner.py](file:///d:/dev/python/nexy/nexy/compiler/parser/scanner.py): Entry point for the compiler.

## 5. Development Workflow
1. **Identify Task**: Read `tasks/` or user input.
2. **Analyze State**: Run tests and linters.
3. **Draft Plan**: Use `TodoWrite` to list steps.
4. **Implement**: Small, incremental changes.
5. **Verify**: Run `pytest`, `mypy`, and `ruff`.
6. **Document**: Update this guide if architecture changes.
