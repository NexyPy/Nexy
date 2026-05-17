# Task 11: Fix Config singleton — remove dual class/instance state

## Problem
`nexy/core/config.py` uses **class-level mutable attributes** that are **mutated** on every `_get_config()` call. Both `self.X = val` AND `Config.X = val` are set. This creates two sources of truth.

Example pattern (repeated for every config field):
```python
aliases = getattr(nexy_config, "useAliases", None)
if aliases is not None:
    self.ALIASES = aliases      # instance attribute
    Config.ALIASES = aliases    # class attribute (redundant!)
```

## Step 1: Read the file
```bash
Get-Content -LiteralPath "nexy/core/config.py"
```

## Step 2: Replace the class pattern

**oldString:** (find the exact class definition — may look different from below, adjust based on actual file)
```python
class Config:
    ALIASES: bool = ...
    ...
    _instance = None

    def __new__(cls) -> Config:
        ...
    
    def __init__(self) -> None:
        ...
    
    def _get_config(self) -> None:
        ...
        if aliases is not None:
            self.ALIASES = aliases
            Config.ALIASES = aliases
        ...
```

**Replace all `Config.X = val` lines with just `self.X = val`.** Strategy:

1. Keep class-level constants (never mutated) at class level as defaults
2. Remove all `Config.X = val` mutation lines
3. Use `__new__` for proper singleton pattern

Example of the fix for each mutated attribute:

| Old (2 lines) | New (1 line) |
|---------------|---------------|
| `self.ALIASES = aliases; Config.ALIASES = aliases` | `self.ALIASES = aliases` |
| `self.NAMESPACE = namespace; Config.NAMESPACE = namespace` | `self.NAMESPACE = namespace` |

Use `rg "Config\.[A-Z_]+ =" nexy/core/config.py` to find every class-level mutation in `_get_config()`.

## Step 3: Find all external reads of class attributes
```bash
rg "Config\.(ALIASES|NAMESPACE|MARKDOWN_EXTENSIONS|FF_REGISTRY|ROUTE_FILE|PROJECT_ROOT|ROUTER_PATH|WATCH_|FRONTEND_EXTENSIONS)" nexy/
```

Each `Config.X` read must become `Config().X` (instance access) — or a local `config` variable if already instantiated.

## Verify commands

```bash
# No class-level mutations in _get_config()
rg "Config\.[A-Z_]+ =" nexy/core/config.py  # Should be empty

ruff check nexy/core/config.py
python -m mypy nexy/core/config.py --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] Zero `Config.X = val` writes in `_get_config()` (class-level mutation removed)
- [ ] All config reads use instance access (`Config().X` or `config.X`, not `Config.X`)
- [ ] Singleton properly implemented via `__new__`
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
- [ ] `nx dev` still works end-to-end
