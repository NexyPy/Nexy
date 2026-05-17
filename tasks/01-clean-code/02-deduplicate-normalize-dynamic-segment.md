# Task 02: Remove duplicate `_normalize_dynamic_segment`

## Problem
In `nexy/core/string.py`, `_normalize_dynamic_segment` is defined **twice**:

**First definition** (around line 56):
```python
@staticmethod
def _normalize_dynamic_segment(segment: str) -> str:
    name = segment.strip("[]").lstrip("...")
    return f"{{{name}}}"
```

**Second definition** (around line 69) — overwrites the first at runtime:
```python
@staticmethod
def _normalize_dynamic_segment(segment: str) -> str:
    return f"{{{segment.strip('[]').lstrip('...')}}}"
```

The second is identical in behavior but more concise (no intermediate `name` variable). The first silently never runs.

## Step 1: Read the file
```bash
Get-Content -LiteralPath "nexy/core/string.py"
```

## Step 2: Delete the first definition

Find lines:
```python
    @staticmethod
    def _normalize_dynamic_segment(segment: str) -> str:
        name = segment.strip("[]").lstrip("...")
        return f"{{{name}}}"
```

Use `edit` tool with `oldString` set to the above block and `newString` set to empty string.

## Step 3: Verify
```bash
# Only one definition should remain
rg "_normalize_dynamic_segment" nexy/core/string.py
# Should show 2 matches: 1 definition + 1 call site
# Not: 2 definitions + 1 call site
```

## Verify commands
```bash
ruff check nexy/core/string.py
python -m mypy nexy/core/string.py --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] Only one `_normalize_dynamic_segment` function definition in `nexy/core/string.py`
- [ ] File length reduced by ~11 lines
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
