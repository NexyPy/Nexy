# Task 32: Fix `nexy/core/__init.py` → `__init__.py`

## Problem

The core package initialization file is named `nexy/core/__init.py` (single `_` on each side) instead of the standard `__init__.py` (double `_`). This means `core` is not a proper Python package and cannot be imported as `from nexy.core import ...`.

However, since other modules import from `nexy.core.config`, `nexy.core.models`, etc., Python must be finding these modules through some other mechanism (likely because `nexy/` itself is a package and `core` directory has `__init.py` that acts as a namespace). This is fragile and non-standard.

## Changes

### Step 1: Rename the file

```powershell
Move-Item -Path "nexy/core/__init.py" -Destination "nexy/core/__init__.py"
```

### Step 2: Check all imports

Verify all imports from `nexy.core` work correctly:

```bash
rg "from nexy\.core" nexy/ tests/
```

Expected patterns:
```python
from nexy.core.config import Config
from nexy.core.models import PaserModel, ScanResult, ...
from nexy.core.string import StringTransform, Pathname
```

These should all continue to work after rename since Python resolves both `__init__` and namespace packages.

### Step 3: Verify the renamed file is a proper package init

Read `nexy/core/__init__.py` after rename — if it's empty, that's fine. A package init can be empty.

## Search commands

```bash
# Confirm the file exists with wrong name
Test-Path -LiteralPath "nexy/core/__init.py"
# Confirm the correct name doesn't exist
Test-Path -LiteralPath "nexy/core/__init__.py"
# Find all imports from nexy.core
rg "from nexy\.core" nexy/ tests/
```

## Verify

- [ ] `nexy/core/__init.py` renamed to `nexy/core/__init__.py`
- [ ] `python -c "from nexy.core.config import Config"` works
- [ ] `python -c "from nexy.core.models import PaserModel"` works
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m pytest tests/ -v` — no regressions
