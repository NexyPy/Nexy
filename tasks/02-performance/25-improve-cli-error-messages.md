# Task 25: Structured CLI error messages with suggestions

## Problem
Nexy CLI shows generic errors:
- `"Error compiling file"` — no hint about what kind of error
- `"Import not found"` — no "did you mean?" suggestion
- Config loading errors are silently ignored (`except: pass` in 7 places)

## Target: Vite-quality error output
- Structured: [ERROR] Title → Message → File:Line → Suggestion
- Colorized per severity
- Actionable: every error includes a fix suggestion
- No emoji, no French — symbols from codebase (✘, !)

## Implementation

### Step 1: Create `nexy/utils/cli_errors.py`

```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NexyError:
    title: str
    message: str
    suggestion: str = ""
    file: str = ""
    line: Optional[int] = None
    column: Optional[int] = None


ERROR_STYLES = {
    "config": {"title": "Configuration Error", "icon": "[red]✘[/red]"},
    "compile": {"title": "Compilation Error", "icon": "[red]✘[/red]"},
    "import": {"title": "Import Error", "icon": "[red]✘[/red]"},
    "build": {"title": "Build Error", "icon": "[red]✘[/red]"},
    "runtime": {"title": "Runtime Error", "icon": "[red]✘[/red]"},
    "warning": {"title": "Warning", "icon": "[yellow]![/yellow]"},
}


def format_nexy_error(err: NexyError, style_key: str = "build") -> str:
    """Format a NexyError for colored terminal output.

    Returns a Rich-compatible string with markup tags.
    """
    style = ERROR_STYLES.get(style_key, ERROR_STYLES["build"])
    parts: list[str] = [f"{style['icon']} [bold]{style['title']}[/bold]: {err.title}"]

    if err.file:
        loc = f"  [dim]File:[/dim] {err.file}"
        if err.line:
            loc += f":{err.line}"
            if err.column:
                loc += f":{err.column}"
        parts.append(loc)

    parts.append(f"  [dim]Message:[/dim] {err.message}")

    if err.suggestion:
        parts.append(f"  [yellow]Suggestion:[/yellow] {err.suggestion}")

    return "\n".join(parts)
```

### Step 2: Add suggestion logic

Add a helper to find "did you mean?" suggestions:

```python
def find_similar_name(name: str, candidates: list[str], max_suggestions: int = 3) -> list[str]:
    """Find similar names using simple Levenshtein-like scoring."""
    results = []
    name_lower = name.lower()
    for c in candidates:
        c_lower = c.lower()
        # Simple prefix/dice coefficient comparison
        if c_lower.startswith(name_lower) or name_lower.startswith(c_lower):
            results.append(c)
        elif _dice_coefficient(name_lower, c_lower) > 0.5:
            results.append(c)
    return results[:max_suggestions]


def _dice_coefficient(a: str, b: str) -> float:
    """Compute Dice coefficient for two strings."""
    if not a or not b:
        return 0.0
    # Bigram overlap
    bigrams_a = {a[i:i+2] for i in range(len(a)-1)}
    bigrams_b = {b[i:i+2] for i in range(len(b)-1)}
    if not bigrams_a or not bigrams_b:
        return 0.0
    overlap = len(bigrams_a & bigrams_b)
    return 2.0 * overlap / (len(bigrams_a) + len(bigrams_b))
```

### Step 3: Replace silent `except: pass` instances

Find all instances:
```bash
git grep -n 'except.*:\s*\n\s*pass' -- '*.py'
git grep -n 'except:.*pass' -- '*.py'
```

Replace each with proper error logging. For example:

```python
# Before:
try:
    ...
except:
    pass

# After:
try:
    ...
except Exception as _ex:
    logger.warning("silenced error: %s", _ex)
```

### Step 4: Modify `nexy/core/config.py` — add error context

Find the config loading code and wrap with `NexyError`:

```python
try:
    config_module = importlib.import_module("nexyconfig")
except Exception as e:
    raise NexyError(
        title="Failed to load nexyconfig.py",
        message=str(e),
        suggestion="Ensure nexyconfig.py exists at the project root and extends NexyConfigModel.",
    ) from e
```

### Step 5: Modify `nexy/compiler/parser/validator.py`

Find import validation and add "did you mean?":

```python
if not resolved_path.exists():
    similar = find_similar_name(
        import_path,
        [str(f.relative_to(self.project_root)) for f in self.project_root.rglob("*.nexy")]
    )
    hint = f" Did you mean: {similar[0]}?" if similar else ""
    raise NexyError(
        title="Component import not found",
        message=f"'{import_path}' referenced from '{source_file}' does not exist",
        suggestion=hint,
        file=source_file,
    )
```

### Step 6: Modify `nexy/cli/commands/dev.py`, `build.py`, `start.py`

Wrap main logic in error-handling that uses `format_nexy_error`:

```python
try:
    Builder().build(showlog=True)
except NexyError as e:
    console.print(format_nexy_error(e, "build"))
    raise typer.Exit(code=1)
except Exception as e:
    console.print(format_nexy_error(
        NexyError(title="Unexpected error", message=str(e)),
        "runtime",
    ))
    raise typer.Exit(code=1)
```

### Step 7: Replace `⚠️` emoji in console output (see Task 27)

Remove emoji from error/status output. Use `✘` or `!` instead.

## Write tests in `tests/unit/nexy/utils/test_cli_errors.py`

```python
import pytest
from nexy.utils.cli_errors import NexyError, format_nexy_error


def test_format_nexy_error_basic():
    err = NexyError(title="Test", message="Something failed")
    formatted = format_nexy_error(err, "build")
    assert "Test" in formatted
    assert "Something failed" in formatted


def test_format_nexy_error_with_file():
    err = NexyError(title="Test", message="Failed", file="src/test.nexy", line=5)
    formatted = format_nexy_error(err)
    assert "src/test.nexy" in formatted
    assert ":5" in formatted


def test_format_nexy_error_with_suggestion():
    err = NexyError(title="Import missing", message="x not found", suggestion="Did you mean: y?")
    formatted = format_nexy_error(err)
    assert "Did you mean: y?" in formatted


def test_format_nexy_error_style_key():
    err = NexyError(title="Config", message="bad")
    formatted = format_nexy_error(err, "config")
    assert "Configuration Error" in formatted
```

## Verify commands

```bash
# Run the new tests
python -m pytest tests/unit/nexy/utils/test_cli_errors.py -v

# Test with a real error scenario:
# 1. Create a .nexy file that imports a non-existent component
# 2. Run nx dev
# 3. Should see: "✘ Import Error: Component import not found"
#    "  File: src/foo.nexy"
#    "  Message: 'parts/bar' does not exist"
#    "  Suggestion: Did you mean: parts/button?"

# Check no emoji in output
git grep -n '⚠\|‼\|➜\|⊕\|⊛\|△\|🞫' -- '*.py'

python -m pytest tests/ -v
```

## Definition of Done
- [ ] `NexyError` dataclass with title, message, suggestion, file, line
- [ ] `format_nexy_error()` returns colored, structured output
- [ ] `find_similar_name()` returns relevant suggestions
- [ ] All 7 `except: pass` instances are replaced with `logger.warning` or `NexyError`
- [ ] Config loading errors show actionable suggestion
- [ ] Import errors show "Did you mean: ...?" when possible
- [ ] Compilation errors show file + line + specific message
- [ ] Build errors are caught and displayed via `format_nexy_error()`
- [ ] No emoji in console output
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — all pass
