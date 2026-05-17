# Task 28: Use Astral toolchain fully (uv + ruff format)

## Goal
Nexy should leverage the Astral ecosystem (https://astral.sh/) for maximum performance and DX:
- **uv** — Python package manager (replaces pip, ~10-100x faster)
- **Ruff** — linter + formatter (replaces black, isort, flake8)

## Step 1: Update `pyproject.toml`

### Add ruff format configuration:

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM", "ARG"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
```

### Remove unnecessary dev dependencies:

Ruff replaces: black, isort, flake8, pyflakes, pycodestyle (none of which are currently listed, but ensure no legacy ones remain).

Replace `pip install` instructions with `uv pip install`:
```toml
[tool.uv]
dev-dependencies = [
    "mypy>=1.19.1",
    "pytest>=9.0.2",
    "ruff>=0.14.11",
    "types-jinja2>=2.11.9",
]
```

### Verify `[dependency-groups]` is named correctly

Hatchling uses `[dependency-groups]` not `[tool.uv.dev-dependencies]`. Let's keep the current format but add `uv`-specific speed:

```toml
[dependency-groups]
dev = [
    "mypy>=1.19.1",
    "pytest>=9.0.2",
    "ruff>=0.14.11",
    "types-jinja2>=2.11.9",
]
```

## Step 2: Update `AGENTS.md`

Replace all `pip` commands with `uv`:

```markdown
# Quality gates (run in this order: lint → format → typecheck → test)
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict
python -m pytest tests/ -v

# Auto-fix
ruff check nexy/ --fix
ruff format nexy/

# Install
uv pip install -e ".[dev]"

# Single test
python -m pytest tests/unit/nexy/parser/test_scanner.py -v
```

## Step 3: Run `ruff format` on the codebase

```bash
ruff format nexy/
```

This auto-formats all Python files to ruff's standard. Since this is a one-time format change, it will touch many files. That's expected.

## Step 4: Verify no formatting issues

```bash
ruff format nexy/ --check  # Should pass after step 3
ruff check nexy/            # Should pass (lint)
python -m mypy nexy --strict  # Should pass (typecheck)
python -m pytest tests/ -v    # Should pass (tests)
```

## Step 5: Update install script in README/AGENTS

Ensure all developer docs reference `uv`:

| Before | After |
|--------|-------|
| `pip install -e ".[dev]"` | `uv pip install -e ".[dev]"` |
| `pip install -e .` | `uv pip install -e .` |

## Definition of Done
- [ ] `ruff format nexy/` passes (all files formatted)
- [ ] `ruff format nexy/ --check` returns clean
- [ ] `ruff check nexy/` passes with no lint errors
- [ ] `python -m mypy nexy --strict` passes
- [ ] `python -m pytest tests/ -v` passes
- [ ] `AGENTS.md` references `uv` instead of `pip`
- [ ] `pyproject.toml` has fully configured `[tool.ruff]` section
