# Task 09: Move CLI utilities to `nexy/utils/`

## Problem
6 utility modules live in `nexy/cli/commands/utilities/` but are **not CLI-specific**. They should be in `nexy/utils/` so non-CLI code can reuse them (KISS, single source of truth).

## Move list

| From `nexy/cli/commands/utilities/` | To `nexy/utils/` |
|-------------------------------------|------------------|
| `console.py` | `cli_console.py` |
| `watcher.py` | `watcher.py` |
| `server.py` | `server.py` |
| `uvicorn_config.py` | `uvicorn_config.py` |
| `constants.py` | `constants.py` |
| `pycache.py` | `pycache.py` |
| ~~`find_port.py`~~ | ~~deleted in task 03~~ |

## Step 1: Read all 6 files (understand imports)

```bash
Get-Content -LiteralPath "nexy/cli/commands/utilities/console.py"
Get-Content -LiteralPath "nexy/cli/commands/utilities/watcher.py"
Get-Content -LiteralPath "nexy/cli/commands/utilities/server.py"
Get-Content -LiteralPath "nexy/cli/commands/utilities/uvicorn_config.py"
Get-Content -LiteralPath "nexy/cli/commands/utilities/constants.py"
Get-Content -LiteralPath "nexy/cli/commands/utilities/pycache.py"
```

Also read files that import from these to know what needs updating:
```bash
rg "from nexy.cli.commands.utilities" nexy/
```

## Step 2: Copy each file

```powershell
Copy-Item -LiteralPath "nexy/cli/commands/utilities/console.py"      -Destination "nexy/utils/cli_console.py"
Copy-Item -LiteralPath "nexy/cli/commands/utilities/watcher.py"      -Destination "nexy/utils/watcher.py"
Copy-Item -LiteralPath "nexy/cli/commands/utilities/server.py"       -Destination "nexy/utils/server.py"
Copy-Item -LiteralPath "nexy/cli/commands/utilities/uvicorn_config.py" -Destination "nexy/utils/uvicorn_config.py"
Copy-Item -LiteralPath "nexy/cli/commands/utilities/constants.py"    -Destination "nexy/utils/constants.py"
Copy-Item -LiteralPath "nexy/cli/commands/utilities/pycache.py"     -Destination "nexy/utils/pycache.py"
```

## Step 3: Fix internal imports in the COPIES

Each copied file may reference other files in `nexy.cli.commands.utilities`. Update those:

**In `nexy/utils/server.py`:**
- `from nexy.cli.commands.utilities.uvicorn_config import NEXY_LOG_CONFIG` → `from nexy.utils.uvicorn_config import NEXY_LOG_CONFIG`
- `from nexy.cli.commands.utilities.console import console` → `from nexy.utils.cli_console import console`
- `from nexy.cli.commands.utilities.constants import *` → `from nexy.utils.constants import *`
- Any other `nexy.cli.commands.utilities` imports → `nexy.utils`

**In `nexy/utils/watcher.py`:**
- Same pattern — replace `nexy.cli.commands.utilities` → `nexy.utils` in imports

## Step 4: Update all OTHER files that import from `nexy.cli.commands.utilities`

```bash
rg "from nexy.cli.commands.utilities" nexy/ --include "*.py"
```

For each match, update the import path from `nexy.cli.commands.utilities.X` → `nexy.utils.X`.

Note: for `console.py` specifically → the new location is `nexy.utils.cli_console`.

Files likely affected:
- `nexy/cli/commands/dev.py`
- `nexy/cli/commands/build.py`
- `nexy/cli/commands/start.py`
- `nexy/routers/app.py`
- `nexy/cli/commands/init/project.py` (if it exists)

## Step 5: Delete old files

```powershell
Remove-Item -LiteralPath "nexy/cli/commands/utilities/console.py"
Remove-Item -LiteralPath "nexy/cli/commands/utilities/watcher.py"
Remove-Item -LiteralPath "nexy/cli/commands/utilities/server.py"
Remove-Item -LiteralPath "nexy/cli/commands/utilities/uvicorn_config.py"
Remove-Item -LiteralPath "nexy/cli/commands/utilities/constants.py"
Remove-Item -LiteralPath "nexy/cli/commands/utilities/pycache.py"
```

If `nexy/cli/commands/utilities/__init__.py` exists and only re-exports these, delete or empty it.

## Step 6: Create backward-compat stubs (optional safety)

In each original location, leave a single-line re-export:
```python
from nexy.utils.server import *  # noqa: F401, F403
```

But better to fully remove and update all imports. No backward stubs needed.

## Verify commands

```bash
# No remaining old location imports
rg "from nexy.cli.commands.utilities" nexy/  # Should be empty

# New location files exist
Test-Path -LiteralPath "nexy/utils/server.py"
Test-Path -LiteralPath "nexy/utils/watcher.py"
Test-Path -LiteralPath "nexy/utils/uvicorn_config.py"
Test-Path -LiteralPath "nexy/utils/constants.py"
Test-Path -LiteralPath "nexy/utils/pycache.py"
Test-Path -LiteralPath "nexy/utils/cli_console.py"

# Old location files removed
Test-Path -LiteralPath "nexy/cli/commands/utilities/server.py"  # False

ruff check nexy/
python -m mypy nexy --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] All 6 files moved from `nexy/cli/commands/utilities/` to `nexy/utils/`
- [ ] Zero imports reference `nexy.cli.commands.utilities`
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
- [ ] `nx dev` / `nx build` / `nx start` still work
