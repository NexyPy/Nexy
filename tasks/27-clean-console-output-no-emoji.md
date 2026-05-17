# Task 27: Clean console output — zero emoji, clean text only

## Rule
Nexy console output must be **clean, professional, emoji-free**. Only use simple ASCII indicators already present in the codebase (`✓`, `✗`, `✘`, `↺`). No emoji (🚀, 😊, ⚠️, etc.), no Unicode art.

## Problem
The file `nexy/cli/commands/utilities/uvicorn_config.py:31-39` uses non-standard Unicode symbols as HTTP status indicators:

```python
status_indicators = {
    200: "✓",    # Keep: checkmark (already used in builder)
    201: "⊕",    # Replace: → "⊕" is OK (simple math symbol)
    304: "⊛",    # Replace: → "○" (simple circle)
    307: "➜",    # Replace: → "→" (simple arrow)
    400: "△",    # Replace: → "▲" or keep (simple triangle)
    404: "○",    # Keep: simple circle
    422: "🞫",    # REPLACE: → "✗" (use the cross already in codebase)
    500: "‼",    # Replace: → "✗" (use the cross already in codebase)
}
```

## Action

### 1. Standardize `status_indicators` in `uvicorn_config.py:31-39`

Use only symbols that already exist in the codebase:
```python
status_indicators = {
    200: "✓",
    201: "✓",
    304: "○",
    307: "→",
    400: "△",
    404: "○",
    422: "✗",
    500: "✗",
}
```

### 2. Replace `⚠️` on line 89
```python
# Before:
indicator = status_indicators.get(status_code, "⚠️")

# After: use the default indicator as a simple symbol
indicator = status_indicators.get(status_code, "○")
```

### 3. Fix `server.py:142` — already has ✘ which is fine, but French text:
```python
# Before:
print_console.print(f"[red]✘ Échec du lancement du serveur :[/red] {exc}")

# After:
print_console.print(f"[red]✘ Failed to start server:[/red] {exc}")
```

### 4. Verify builder output — already uses ✓ and ✗, these are fine.

### 5. Check CLI output in `dev.py`, `build.py`, `start.py`, `init.py`:

```bash
git grep -n '[🚀😊⚠️🎉✅❌🔥💀💪]' -- '*.py'
```
(Should return nothing after cleanup.)

## Philosophy
Vite's console output is minimal and clean. Nexy should follow the same standard:
- `[green]✓[/green]` for success
- `[red]✗[/red]` for failure
- `[blue]→[/blue]` for progress/info
- No emoji, no Unicode art, no decorative characters

## Verify
- [ ] No emoji characters in any `nexy/*.py` file
- [ ] `status_indicators` uses only symbols already in codebase
- [ ] `⚠️` replaced with simple symbol
- [ ] `python -m pytest tests/ -v` — no regressions
