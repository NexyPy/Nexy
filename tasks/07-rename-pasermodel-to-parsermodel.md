# Task 07: Rename `PaserModel` → `ParserModel`

## Problem
Typo in `nexy/core/models.py:110`: class name is `PaserModel` (missing `r`). Should be `ParserModel`.

## Step 1: Find all occurrences
```bash
rg "PaserModel" nexy/ tests/
```

Expected files:
- `nexy/core/models.py` — class definition + any internal references
- `nexy/compiler/__init__.py` — imports and usage
- `nexy/compiler/parser/__init__.py` — imports and usage
- `nexy/compiler/generator/__init__.py` — imports and usage
- Possibly `tests/` files that reference `PaserModel`

## Step 2: Rename in each file

For each file found in step 1:

**2a. `nexy/core/models.py`** — class definition:
```python
# oldString:
class PaserModel(BaseModel):
# newString:
class ParserModel(BaseModel):
```

**2b. All import/usage files** — use the `replaceAll` option in `edit`:

For each file, replace all occurrences of `PaserModel` → `ParserModel`.

```bash
# Example for each file:
# nexy/compiler/__init__.py
# nexy/compiler/parser/__init__.py
# nexy/compiler/generator/__init__.py
```

## Step 3: Add an alias for backward compatibility (optional)

In `nexy/core/models.py`, add at the end:
```python
# Backward compatibility alias
PaserModel = ParserModel
```

Close after all code is migrated. Ensure it maps to the new name for any third-party references.

## Verify commands

```bash
# No remaining PaserModel
rg "PaserModel" nexy/  # Should return nothing (or only the backward-compat alias)

ruff check nexy/
python -m mypy nexy --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] Class name is `ParserModel` in `nexy/core/models.py`
- [ ] All imports throughout codebase use `ParserModel`
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
