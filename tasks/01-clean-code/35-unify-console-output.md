# Task 35: Unify console output using rich library

## Problem

There are two separate console instances:
1. `nexy/utils/console.py` — shared `RichConsole` instance
2. `nexy/cli/commands/utilities/console.py` — CLI-specific duplicate

Commands `build.py` and `start.py` import from `cli.commands.utilities.console` while `dev.py` and `init.py` use `nexy.utils.console`. This inconsistency must be unified.

## Changes

### Step 1: Redirect all imports to `nexy.utils.console`

**`nexy/cli/commands/build.py`** (line 4):
```python
# Before:
from nexy.cli.commands.utilities.console import console
# After:
from nexy.utils.console import console
```

**`nexy/cli/commands/start.py`** (line 5):
```python
# Before:
from nexy.cli.commands.utilities.console import console
# After:
from nexy.utils.console import console
```

### Step 2: Delete duplicate console

```powershell
Remove-Item -LiteralPath "nexy/cli/commands/utilities/console.py"
```

### Step 3: Add color constants to `nexy/utils/console.py`

Make common color patterns available:

```python
# Add to nexy/utils/console.py:
from typing import Any

console: RichConsole = RichConsole()

def _safe_print(*args: Any, **kwargs: Any) -> None:
    console.print(*args, **kwargs)

# Color constants for consistent styling
class C:
    info = "bold blue"
    success = "bold green"
    warning = "bold yellow"
    error = "bold red"
    dim = "dim"
    reset = "reset"
```

### Step 4: Standardize console.print calls

Adopt a consistent format across the codebase:

| Context | Format |
|---------|--------|
| Info | `console.print(f"[blue]nex[/blue] » {msg}")` |
| Success | `console.print(f"[green]nex[/green] » {msg} [green]✓[/green]")` |
| Warning | `console.print(f"[yellow]nex[/yellow] » {msg}")` |
| Error | `console.print(f"[red]nex[/red] » {msg} [red]✗[/red]")` |
| Timing | `console.print(f"[dim]{timer}[/dim]")` |

Replace inconsistent prefixes like `[red]nsc[/red]` with `[red]nex[/red]`.

## Search commands

```bash
rg "from nexy\.cli\.commands\.utilities\.console import" nexy/
rg "\[red\]nsc" nexy/
rg "\[green\]nsc" nexy/
Test-Path -LiteralPath "nexy/cli/commands/utilities/console.py"
```

## Verify

- [ ] Only one console instance exists: `nexy/utils/console.py`
- [ ] `nexy/cli/commands/utilities/console.py` deleted
- [ ] All `.py` files import `console` from `nexy.utils.console`
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m pytest tests/ -v` — no regressions
