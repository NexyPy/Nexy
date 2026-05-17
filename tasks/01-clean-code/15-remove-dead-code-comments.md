# Task 15: Remove dead code and commented-out imports

## Problem
8 instances of dead/commented-out code that should be removed:

| # | File | Line(s) | Content |
|---|------|---------|---------|
| 1 | `nexy/routers/app.py` | ~10 | `# from nexy.cli.commands.utilities.pycache import pycache` |
| 2 | `nexy/routers/app.py` | ~127 | `# pycache()` |
| 3 | `nexy/core/config.py` | ~112-113 | `# traceback.print_exc()` / `# print(...)` |
| 4 | `nexy/hooks.py` | ~80 | `# return HTMLResponse(Vite() + func_name)` |
| 5 | `nexy/vite.py` | ~39 | `# src = f"/__nexy__/client/{file_rel}"` |
| 6 | `nexy/vite.py` | ~43 | `# f"<link rel=\"stylesheet\"..."` |
| 7 | `nexy/compiler/__init__.py` | ~66-72 | multi-line commented block |
| 8 | `nexy/compiler/__init__.py` | ~11 | `# class Config(NexyConfigModel):` |

## Step 1: Find all instances
```bash
rg "^#" nexy/ --include "*.py" | Select-String -Pattern "(from nexy|return HTMLResponse|pycache|traceback|src =|stylesheet|compiled_module|class Config)" | Select-Object -First 20
```

## Step 2: Delete each commented line

For each of the 8 instances, use `edit` tool with:
- **oldString:** the exact commented line(s) as read from the file
- **newString:** (empty string)

**Example for instance #1 (nexy/routers/app.py):**
```
oldString: # from nexy.cli.commands.utilities.pycache import pycache
newString:
```

**Example for instance #5 (nexy/vite.py):**
```
oldString:             # src = f"/__nexy__/client/{file_rel}"
newString:
```

## Verify commands

```bash
# None of the known dead patterns should remain
rg "^#.*from nexy.cli.commands.utilities" nexy/  # Empty
rg "^#.*pycache" nexy/  # Empty
rg "^#.*traceback" nexy/  # Empty
rg "^#.*return HTMLResponse" nexy/  # Empty
rg "^#.*compiled_module" nexy/  # Empty
rg "^#.*class Config" nexy/compiler/  # Empty

ruff check nexy/
python -m mypy nexy --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] All 8 instances of commented-out code removed
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
