# Task 37: Organize utils into module-specific subdirectories

## Problem

`nexy/utils/` currently has a flat structure with some module-specific utilities mixed with general ones:

```
nexy/utils/
├── console.py        # General: shared console
├── ports.py          # General: port finding
├── file.py           # Deprecated (task 04 deletes)
├── folder.py         # Deprecated (task 04 deletes)
├── pathname.py       # Deprecated (task 04 deletes)
└── imports/          # Module-specific: import handlers
    ├── css.py
    ├── images.py
    ├── json.py
    └── ncc.py
```

Module-specific utilities (those only used by one module) should live in subdirectories named after that module. General utilities stay in `utils/` root.

## Changes

### 1. Move module-specific utils to subdirectories

| Current path | Target path | Reason |
|---|---|---|
| `nexy/utils/ports.py` | `nexy/utils/server/ports.py` | Only used by server/cli modules |
| `nexy/utils/imports/` | `nexy/compiler/imports/` | Only used by compiler/parser |
| `nexy/utils/console.py` | **Stays at root** | Used everywhere — general utility |

**But only if the utility is *exclusively* used by one module.** KISS says: don't move files just for the sake of nesting. Only move when it improves clarity.

### 2. Determine what belongs where

```bash
# Check who uses ports.py
rg "from nexy.utils.ports" nexy/ --include "*.py"

# Check who uses console
rg "from nexy.utils.console" nexy/ --include "*.py"

# Check who uses imports
rg "from nexy.utils.imports" nexy/ --include "*.py"
```

### 3. Decision matrix

| Utility | Used by | Verdict |
|---------|---------|---------|
| `console.py` | 10+ files across CLI, Compiler, Router | **Keep at root** |
| `ports.py` | `cli/commands/dev.py`, `cli/commands/utilities/server.py`, `template.py`, `vite.py` | **Keep at root** (used by multiple modules) |
| `imports/` | Only `nexy/_import.py` | **Move** to `nexy/compiler/imports/` or keep as `nexy/imports/` |
| `file.py` | Only `nexy/_import.py` | **Delete** (task 04) |
| `folder.py` | No current imports | **Delete** (task 04) |
| `pathname.py` | Only `nexy/utils/folder.py` | **Delete** (task 04) |

### 4. Move `imports/` if only used by compiler

If `rg` confirms it's only used by compiler:

```powershell
New-Item -ItemType Directory -Path "nexy/compiler/imports" -Force
Move-Item -Path "nexy/utils/imports/*" -Destination "nexy/compiler/imports/"
Remove-Item -LiteralPath "nexy/utils/imports" -Recurse
```

Update imports in `nexy/_import.py`:
```python
# Before:
from nexy.utils.imports.css import CSSImport
# After:
from nexy.compiler.imports.css import CSSImport
```

## Search commands

```bash
rg "from nexy\.utils\.(ports|console|imports|file|folder|pathname)" nexy/
rg "from nexy\.utils" nexy/ --include "*.py"
```

## Verify

- [ ] Only utilities used by multiple modules remain in `nexy/utils/` root
- [ ] Module-specific utilities are in subdirectories named after their module
- [ ] All import paths updated
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
