# Task 05: Remove `useRoute` alias

## Problem
In `nexy/decorators.py`, `useRoute` (around line 173) is an **identical pass-through** to `UseRoute` (around line 145):

```python
def useRoute(
    path: str = "",
    method: str = "GET",
    template: Optional[str] = None,
    layout: Optional[str] = None,
    guards: Optional[list[type]] = None,
) -> Callable:
    return UseRoute(path, method, template, layout, guards)
```

Two public APIs doing the same thing violates KISS.

## Step 1: Find usages
```bash
rg "useRoute" nexy/ tests/
```

Look for:
- `from nexy.decorators import useRoute`
- `from nexy import useRoute`
- `@useRoute(...)` decorator usage

## Step 2: Replace the oldString with empty newString

Find the exact `useRoute` function definition (starting from `def useRoute(` through its `return UseRoute(...)` line) in `nexy/decorators.py` and delete it.

The exact block to delete:
```python
def useRoute(
    path: str = "",
    method: str = "GET",
    template: Optional[str] = None,
    layout: Optional[str] = None,
    guards: Optional[list[type]] = None,
) -> Callable:
    return UseRoute(path, method, template, layout, guards)
```

Also check if `useRoute` is exported in `nexy/__init__.py`:
```bash
rg "useRoute" nexy/__init__.py
```
If found, replace with `UseRoute`.

## Verify commands

```bash
# No remaining useRoute
rg "useRoute" nexy/  # Should only show in comments or not at all

ruff check nexy/
python -m mypy nexy --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] `useRoute` function removed from `nexy/decorators.py`
- [ ] All imports updated to `UseRoute` (PascalCase)
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
