# Register CLI Commands

## Goal
Wire up the three new commands (`check`, `format`, `test`) into the Typer CLI and update the welcome banner.

## Details

### Files to modify

| File | Change |
|------|--------|
| `nexy/cli/__init__.py` | Import the 3 commands, register via `CLI.command()`, update banner `commands` list |
| `nexy/cli/commands/__init__.py` | Add `from .check import check` etc., update `__all__` |

### Welcome Banner Update

Add to the commands list:
```python
("check", "Run type checking across all project files"),
("format", "Auto-format all project files"),
("test", "Run tests (--server / --client)"),
```

### Dependencies

All 4 tasks in this group (01–04) must be completed before this one.

## Success Criteria
- `nexy check --help`, `nexy format --help`, `nexy test --help` all show proper usage
- Commands appear in `nexy --help` welcome banner
- No import errors
