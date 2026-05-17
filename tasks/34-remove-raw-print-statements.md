# Task 34: Remove all raw `print()` statements, use rich

## Problem

Several files use raw Python `print()` instead of the rich-based `console.print()` from `nexy/utils/console.py`. Raw `print()` produces unstyled output and breaks the unified console UX.

Files with raw `print()`:

| File | Line | Code |
|------|------|------|
| `nexy/audio.py` | 5 | `print("Audio called with args:", args, "and kwargs:", kwargs)` |
| `nexy/decorators.py` | 268 | `print(f"{ctrl_cls.__name__} has multiple handlers for HTTP method {method_upper} ")` |
| `nexy/decorators.py` | 113 | `print(f"Internal Server Error: {exc.detail}")` |
| `nexy/decorators.py` | 120 | `print(f"Internal Server Error: {exc.detail}")` |
| `nexy/routers/app.py` | 113 | `print(f"Internal Server Error: {exc.detail}")` |
| `nexy/routers/app.py` | 120 | `print(f"Internal Server Error: {exc.detail}")` |
| `nexy/frontend/__init__.py` | 28 | `print(f"[nexy] Error copying scripts: {e}")` |
| `nexy/cli/commands/add.py` | 3 | `print("> nexy add")` |
| `nexy/utils/file.py` | 21 | `print(f"File {self.path} not exists")` |
| `nexy/utils/file.py` | 28 | `print(f"File {self.path} already exists")` |
| `nexy/utils/folder.py` | 15 | `print(f"Folder {self.path} already exists")` |
| `nexy/utils/folder.py` | 22 | `print(f"Folder {self.path} not exists")` |

## Changes

### 1. `nexy/audio.py`

```python
# Before:
print("Audio called with args:", args, "and kwargs:", kwargs)

# After (needs import):
from nexy.utils.console import console
console.print(f"[dim]Audio[/dim] called with args: {args} and kwargs: {kwargs}")
```

### 2. `nexy/decorators.py`

Replace both `print(f"Internal Server Error: {exc.detail}")` with console.print:

```python
# After (needs import):
from nexy.utils.console import console
# Replace:
# print(f"Internal Server Error: {exc.detail}")
# → 
console.print(f"[red]Internal Server Error:[/red] {exc.detail}")
```

For the duplicate method error:
```python
# Before:
print(f"{ctrl_cls.__name__} has multiple handlers for HTTP method {method_upper} ")
# After:
console.print(f"[yellow]{ctrl_cls.__name__}[/yellow] has multiple handlers for HTTP method [bold]{method_upper}[/bold]")
```

### 3. `nexy/routers/app.py`

Replace print statements with console.print. Already imports `console` at line 15.

### 4. `nexy/frontend/__init__.py`

Replace print with console.print. Already imports `console` at line 3.

### 5. `nexy/cli/commands/add.py`

Replace raw `print()` with console.print (which uses rich markup).

### 6. `nexy/utils/file.py` and `nexy/utils/folder.py`

These files are targeted for deletion in **Task 04** — skip if task 04 has been run, otherwise use `console.print` as a temporary fix.

## Search command

```bash
# Find all raw print statements (not in comments, not in test files)
rg "^[^#]*\bprint\(" nexy/ --include "*.py" -n
rg "^[^#]*\bprint\(" tests/ --include "*.py" -n
```

## Verify

- [ ] Zero raw `print(` calls remain in `nexy/*.py` files that aren't deleted by other tasks
- [ ] All console output uses `console.print()` from `nexy/utils/console.py`
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m pytest tests/ -v` — no regressions
