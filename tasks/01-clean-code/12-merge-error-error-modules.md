# Task 12: Merge `error.py` into `errors.py`

## Problem
Two error modules in `nexy/` root with confusing names:
- `nexy/error.py` — `NotFound()`, `InternalServerError()` (HTML response generators)
- `nexy/errors.py` — `NexyCompileError` (compile error exception)

## Step 1: Read both files
```bash
Get-Content -LiteralPath "nexy/error.py"
Get-Content -LiteralPath "nexy/errors.py"
```

## Step 2: Move content from `error.py` into `errors.py`

Append the functions `NotFound()` and `InternalServerError()` from `nexy/error.py` into `nexy/errors.py`. If `not_found_html` or other helpers are used by those functions, include them too.

## Step 3: Find all imports
```bash
rg "from nexy.error import" nexy/ tests/
```

## Step 4: Update each import

For each file found in step 3, replace:
```python
from nexy.error import NotFound, InternalServerError
```
with:
```python
from nexy.errors import NotFound, InternalServerError
```

## Step 5: Delete `nexy/error.py`
```powershell
Remove-Item -LiteralPath "nexy/error.py"
```

## Verify commands

```bash
# Old file deleted
Test-Path -LiteralPath "nexy/error.py"  # False

# No remaining imports to nexy.error
rg "from nexy.error import" nexy/  # Empty

ruff check nexy/
python -m mypy nexy --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] `nexy/error.py` deleted
- [ ] All imports updated to `nexy.errors`
- [ ] `NotFound()` and `InternalServerError()` accessible from `nexy.errors`
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
