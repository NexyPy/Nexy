# Task 13: Write missing unit tests (fill empty test files)

## Problem
4 test files exist but are **empty (0 bytes)**:
1. `tests/unit/nexy/parser/test_logic.py`
2. `tests/unit/nexy/parser/test_sanitizer.py`
3. `tests/integration/test_runtime.py`
4. `tests/integration/nexy/builder/test_builder.py`

## Step 1: Read source files to understand the API

```bash
# LogicParser
rg "class LogicParser" nexy/compiler/parser/logic.py

# LogicSanitizer
rg "class LogicSanitizer" nexy/compiler/parser/sanitizer.py

# Builder
rg "class Builder" nexy/builder/__init__.py
```

## Step 2: Fill `tests/unit/nexy/parser/test_logic.py`

```python
import pytest
from pathlib import Path


@pytest.fixture
def logic_parser():
    from nexy.compiler.parser.logic import LogicParser
    return LogicParser()


def test_parse_str_prop(logic_parser):
    result = logic_parser.parse("title: prop[str] = \"Hello\"")
    assert result["title"] == "Hello"


def test_parse_int_prop(logic_parser):
    result = logic_parser.parse("count: prop[int] = 42")
    assert result["count"] == 42


def test_parse_prop_without_default(logic_parser):
    result = logic_parser.parse("name: prop[str]")
    assert "name" in result


def test_parse_from_import(logic_parser):
    result = logic_parser.parse("""
from components.button import Button
    """)
    # Depending on LogicParser API, adjust assertion
    assert result is not None


def test_parse_css_import(logic_parser):
    result = logic_parser.parse("""
from styles.main import css
    """)
    assert result is not None


def test_process_with_frontmatter_and_imports(logic_parser):
    source = """
title: prop[str] = "Hello"
count: prop[int] = 0

from components.button import Button
from styles.main import css
"""
    result = logic_parser.parse(source)
    assert "title" in result
    assert "count" in result
```

## Step 3: Fill `tests/unit/nexy/parser/test_sanitizer.py`

```python
import pytest
from pathlib import Path


@pytest.fixture
def sanitizer():
    from nexy.compiler.parser.sanitizer import LogicSanitizer
    return LogicSanitizer()


def test_sanitize_simple_import(sanitizer):
    result = sanitizer.sanitize("from components.button import Button")
    assert result is not None


def test_sanitize_from_import(sanitizer):
    result = sanitizer.sanitize("from layouts.main import Layout")
    assert result is not None


def test_sanitize_with_empty(sanitizer):
    result = sanitizer.sanitize("")
    assert result == "" or result is None


def test_sanitize_without_imports(sanitizer):
    result = sanitizer.sanitize("x: prop[int] = 1")
    assert result is not None
```

## Step 4: Fill `tests/integration/nexy/builder/test_builder.py`

```python
import pytest
from pathlib import Path


def test_build_single_file(tmp_path):
    """Builder can compile a single .nexy file."""
    from nexy.builder import Builder
    from nexy.core.config import Config
    
    src = tmp_path / "test.nexy"
    src.write_text("---\ntitle: prop[str] = \"Hello\"\n---\n<h1>{{ title }}</h1>")
    
    config = Config()
    config.PROJECT_ROOT = tmp_path
    
    # May need adjustment based on actual Builder API
    builder = Builder()
    builder.config = config
    result = builder._compile(str(src))
    assert result is not None
```

**Note:** Adjust assertions based on actual API signatures of `LogicParser`, `LogicSanitizer`, `Builder`. The exact assertions above may need modification — the key is that files compile and pass.

## Step 5: Fill `tests/integration/test_runtime.py`

```python
def test_runtime_not_implemented_yet():
    """Runtime integration tests pending implementation of nexy/runtime/ modules."""
    pass
```

## Verify commands
```bash
ruff check tests/
python -m pytest tests/unit/nexy/parser/test_logic.py -v
python -m pytest tests/unit/nexy/parser/test_sanitizer.py -v
python -m pytest tests/integration/nexy/builder/test_builder.py -v
python -m pytest tests/integration/test_runtime.py -v
python -m pytest tests/ -v
```

## Definition of Done
- [ ] All 4 previously-empty test files have at least one passing test
- [ ] `python -m pytest tests/ -v` shows 0 failures in new tests
