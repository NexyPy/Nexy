# Task 03: Deduplicate port-finding logic

## Problem
Three separate port-finding implementations exist:
1. `nexy/utils/ports.py` — `_find_port(start, host, limit)` — bare socket bind loop
2. `nexy/cli/commands/utilities/find_port.py` — `find_port(start, host, limit)` — **identical logic** to #1
3. `nexy/cli/commands/utilities/server.py` — `_is_port_available(host, port)` + `find_available_port(start, host, max_attempts)` — different connect+bind strategy

## Step 1: Search for imports
```bash
rg "find_port" nexy/
```

## Step 2: Verify `find_port.py` is identical to `ports.py`

Read both files:
```bash
Get-Content -LiteralPath "nexy/utils/ports.py"
Get-Content -LiteralPath "nexy/cli/commands/utilities/find_port.py"
```

If the logic is identical:
- Remove any imports of `find_port` from `nexy.cli.commands.utilities.find_port`
- Replace with `from nexy.utils.ports import find_port` (or `_find_port` depending on the public API)

## Step 3: Delete the duplicate file
```bash
Remove-Item -LiteralPath "nexy/cli/commands/utilities/find_port.py"
```

## Step 4: Update imports in affected files

If any file imports `find_port` from `nexy.cli.commands.utilities.find_port`, update to `nexy.utils.ports`.

Also check `server.py` — it has its own `_is_port_available` and `find_available_port` which use a different strategy (connect+bind vs socket bind). Keep those since they serve a different purpose. But ensure no cross-dependency on the now-deleted `find_port.py`.

```bash
rg "from nexy.cli.commands.utilities.find_port" nexy/
```

## Verify commands
```bash
# File should be deleted
Test-Path -LiteralPath "nexy/cli/commands/utilities/find_port.py"  # Should output False

# No dangling imports
rg "nexy.cli.commands.utilities.find_port" nexy/  # Should be empty

ruff check nexy/
python -m mypy nexy --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] `nexy/cli/commands/utilities/find_port.py` deleted
- [ ] Zero imports reference the deleted module
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
