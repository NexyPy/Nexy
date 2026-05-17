# Task 29: Make `---` frontmatter optional for .nexy/.mdx

## Problem

Nexy components (`.nexy` and `.mdx`) currently require `---` frontmatter delimiters to define Python logic. However, many components need **no logic at all** — pure template components with only HTML/Jinja2. The scanner currently handles this gracefully (no `---` = empty logic), but the full pipeline (`Parser` → `LogicParser` → `Generator`) doesn't explicitly support or document this.

## Changes

### 1. `nexy/compiler/parser/logic.py` — handle empty logic_block

Ensure `LogicParser.process()` returns a valid `LogicResult` with empty fields when given empty source.

```python
# Before (line ~20):
def process(self, logic_block: str, current_file: str) -> LogicResult:
    # ... processes logic_block

# After — return early empty LogicResult:
def process(self, logic_block: str, current_file: str) -> LogicResult:
    if not logic_block or not logic_block.strip():
        return LogicResult()
    # ... rest of processing
```

### 2. `nexy/compiler/parser/__init__.py` — handle no-import components

In `Parser.process()` around line 38-43, ensure `known_components` is empty when there are no imports, and the template parser doesn't fail:

```python
# After line 43, ensure set() is fine:
known_components: set[str] = set()
# ... current logic (which may add nothing)

# Template parser should work with empty known_components
jinja_code = self.template_parser.parse(blocks.template_block, known_components=known_components or None)
```

### 3. `nexy/compiler/generator/logic.py` — generate valid module from empty frontmatter

Ensure when `frontmatter` is empty, the generated Python module is still valid:

```python
# Before: may generate broken Python if frontmatter is empty
# After: generate a minimal valid component function
```

### 4. `nexy/compiler/scanner.py` — add docstring clarifying optional markers

Update docstring of `Scanner` class to explicitly state that `---` markers are optional.

## Search commands

```bash
rg "logic_block" nexy/compiler/parser/logic.py
rg "PaserModel" nexy/compiler/ --include "*.py"
```

## Verify

- [ ] A `.nexy` file with only HTML/Jinja2 (no `---` markers) compiles successfully
- [ ] A `.nexy` file with `---` markers + logic continues to work
- [ ] A `.mdx` file with no frontmatter compiles successfully
- [ ] `python -m pytest tests/ -v` — no regressions
- [ ] `ruff check nexy/` — no lint errors
