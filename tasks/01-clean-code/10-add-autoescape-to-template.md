# Task 10: Enable Jinja2 autoescape (XSS fix)

## Problem
`nexy/template.py:24-28`: `Environment()` is created without `autoescape=True`. Jinja2 defaults to `autoescape=False` with `FileSystemLoader`. This means:

```python
self.env = Environment(
    loader=FileSystemLoader("."),
    auto_reload=True,
)
```

If a template renders `{{ "<script>alert(1)</script>" }}`, it outputs raw `<script>` tags → **XSS vulnerability**.

## Step 1: Read the file
```bash
Get-Content -LiteralPath "nexy/template.py"
```

## Step 2: Add `autoescape=True`

Find the `Environment(...)` constructor. Add `autoescape=True`.

Use `edit` tool:

**oldString:**
```python
        self.env = Environment(
            loader=FileSystemLoader("."),
            auto_reload=True,
        )
```

**newString:**
```python
        self.env = Environment(
            loader=FileSystemLoader("."),
            autoescape=True,
            auto_reload=True,
        )
```

## Step 3: Remove unused `select_autoescape` import

Line 2 likely has:
```python
from jinja2 import Environment, FileSystemLoader, select_autoescape
```

Use `edit` tool:
**oldString:** `from jinja2 import Environment, FileSystemLoader, select_autoescape`
**newString:** `from jinja2 import Environment, FileSystemLoader`

If the import doesn't exist, skip this step.

## Verify commands

```bash
# Check autoescape is set
rg "autoescape" nexy/template.py
# Should show: autoescape=True

# Test: render a template with HTML content
python -c "
from nexy.template import Template
t = Template()
result = t.render_string('{{ x }}', {'x': '<script>alert(1)</script>'})
assert '&lt;script&gt;' in result, f'XSS! Got: {result}'
print('PASS: autoescape works')
"

ruff check nexy/template.py
python -m mypy nexy/template.py --strict
python -m pytest tests/ -v
```

## Definition of Done
- [ ] `autoescape=True` set in `Environment()` constructor
- [ ] Unused `select_autoescape` import removed (if present)
- [ ] `{{ "<script>" }}` renders as `&lt;script&gt;` (escaped)
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — no regressions
