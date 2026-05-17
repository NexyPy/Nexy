# Task 14: Make Builder propagate compilation errors

## Problem
`nexy/builder/__init__.py` swallows compilation errors:
```python
except Exception as e:
    console.print(f"[red]nsc[/red] » error compiling ...")
    # silently continues to next file, never raises
```

The CLI never knows if the build succeeded or failed. `nx build` always exits with code 0.

## Step 1: Read the file
```bash
Get-Content -LiteralPath "nexy/builder/__init__.py"
```

## Step 2: Modify `Builder.build()` to collect + propagate errors

Find the `build()` method. Locate the `try/except` block around the compile call.

**oldString (approximate — verify actual file):**
```python
        try:
            self.compiler.compile(input=input_path)
            if showlog:
                console.print(f"[green]nsc[/green] » compiled ...")
        except Exception as e:
            console.print(f"[red]nsc[/red] » error compiling ...")
```

**newString:**
```python
        try:
            self.compiler.compile(input=input_path)
            if showlog:
                console.print(f"[green]nsc[/green] » compiled ...")
        except Exception as e:
            errors.append((input_path, str(e)))
            if showlog:
                console.print(f"[red]nsc[/red] » error compiling {input_path} ✗")
```

Also add at the top of the method:
```python
errors: list[tuple[str, str]] = []
```

And at the end of `build()`, after the loop:
```python
    if errors:
        msg = f"Build failed: {len(errors)} error(s)"
        for path, err in errors[:5]:
            msg += f"\n  {path}: {err}"
        if len(errors) > 5:
            msg += f"\n  ... and {len(errors) - 5} more"
        raise RuntimeError(msg)
```

## Step 3: Update `nexy/cli/commands/build.py`

Find the `build` command function. Wrap `Builder().build(showlog=True)` in try/except to exit with non-zero code:

**oldString (approximate):**
```python
def build(...):
    ...
    Builder().build(showlog=True)
    console.print("[green]Build complete[/green]")
```

**newString:**
```python
def build(...):
    ...
    try:
        Builder().build(showlog=True)
        console.print("[green]Build complete[/green]")
    except RuntimeError as e:
        console.print(f"[red]✘ Build failed:[/red] {e}")
        raise typer.Exit(code=1)
```

## Step 4: Write test for error propagation

In `tests/unit/nexy/builder/test_builder.py`:
```python
import pytest


def test_builder_propagates_errors(tmp_path):
    """Builder raises on invalid .nexy file."""
    from nexy.builder import Builder
    from nexy.core.config import Config

    # Create an invalid .nexy file (no '---' delimiter)
    bad_file = tmp_path / "bad.nexy"
    bad_file.write_text("<h1>No frontmatter</h1>")

    config = Config()
    config.PROJECT_ROOT = tmp_path
    config.SOURCE_DIR = tmp_path

    builder = Builder()
    builder.config = config

    with pytest.raises(RuntimeError, match="Build failed"):
        builder.build(showlog=False)
```

## Verify commands
```bash
ruff check nexy/builder/__init__.py
python -m mypy nexy/builder/__init__.py --strict
python -m pytest tests/unit/nexy/builder/test_builder.py -v
python -m pytest tests/ -v

# Also verify nx build exits with non-zero on failure
# nx build 2>&1; $LASTEXITCODE -gt 0
```

## Definition of Done
- [ ] `Builder.build()` raises `RuntimeError` when compilation fails
- [ ] `nx build` exits with non-zero code on build failure
- [ ] All existing builder tests still pass
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
