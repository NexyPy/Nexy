# Task 08: Remove redundant `ComponentString` class

## Problem
`nexy/core/string.py:122-130` has `ComponentString.get_name()` which is a simplified duplicate of `StringTransform.get_component_name()` (lines 105-118).

Both extract the last path segment and capitalize. `ComponentString` doesn't handle dynamic segments (`[param]`), while `StringTransform` does.

## Step 1: Read the file
```bash
Get-Content -LiteralPath "nexy/core/string.py" | Select-Object -Index (120..135)
```

Find the `ComponentString` class.

## Step 2: Find usages
```bash
rg "ComponentString" nexy/ tests/
```

## Step 3: Delete the class

Use `edit` tool with:

**oldString:** (exact from the file)
```python
class ComponentString:
    @staticmethod
    def get_name(pathname: str) -> str:
        return pathname.split("/")[-1][0].upper() + pathname.split("/")[-1][1:]
```

**newString:** (empty — delete it)

## Step 4: Update imports

If any file imports `ComponentString`, replace with `StringTransform().get_component_name(path)`:

| Old | New |
|-----|-----|
| `from nexy.core.string import ComponentString` | `from nexy.core.string import StringTransform` |
| `ComponentString.get_name(path)` | `StringTransform().get_component_name(path)` |

## Verify commands

```bash
# No remaining ComponentString
rg "ComponentString" nexy/  # Should return nothing

ruff check nexy/
python -m mypy nexy --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] `ComponentString` class removed from `nexy/core/string.py`
- [ ] All usages replaced with `StringTransform().get_component_name()`
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
