# Task 16: Replace silent `except: pass` in parser

## Problem
`nexy/compiler/parser/__init__.py:55`:
```python
except SyntaxError:
    pass
```

This swallows Python syntax errors in `.nexy` frontmatter, producing silently broken output. The user never knows their Python code is invalid.

## Step 1: Read the file
```bash
Get-Content -LiteralPath "nexy/compiler/parser/__init__.py"
```

Find the `except SyntaxError: pass` block. Read surrounding context to understand what variable holds the current file path.

## Step 2: Replace with proper error propagation

Use `edit` tool:

**oldString (approximate — adjust based on actual file):**
```python
        except SyntaxError:
            pass
```

**newString:**
```python
        except SyntaxError as e:
            raise NexyCompileError(
                source_path=getattr(locals().get('file_path'), 'as_posix', lambda: str(file_path))() if 'file_path' in locals() else "unknown",
                message=f"Python syntax error in frontmatter: {e}",
                line=e.lineno,
                column=e.offset,
            ) from e
```

**If `NexyCompileError` is not already imported:**
```python
from nexy.errors import NexyCompileError
```

## Step 3: Write test

In `tests/unit/nexy/parser/test_parser.py`:
```python
import pytest


def test_parser_invalid_python_frontmatter_raises():
    """Invalid Python in frontmatter raises NexyCompileError."""
    from nexy.errors import NexyCompileError
    from nexy.compiler.parser import Parser
    
    parser = Parser()
    invalid_source = """---
invalid python syntax!!!
---
<h1>Test</h1>"""
    
    with pytest.raises(NexyCompileError, match="Python syntax error"):
        parser.parse(invalid_source)
```

## Verify commands
```bash
# The except:pass should be gone
rg "except.*pass" nexy/compiler/parser/__init__.py  # Empty

python -m pytest tests/unit/nexy/parser/test_parser.py -v
ruff check nexy/compiler/parser/
python -m mypy nexy/compiler/parser/ --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] `except SyntaxError: pass` replaced with `raise NexyCompileError(...)`
- [ ] Invalid Python in frontmatter raises clear error with file, line, column
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
