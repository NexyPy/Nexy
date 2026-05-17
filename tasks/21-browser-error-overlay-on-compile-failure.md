# Task 21: Browser error overlay on compilation failure

## Problem
When a `.nexy` file has a syntax error, user sees only a terminal error. Browser shows 500 or stale content. Nuxt/Vite/Astro show a beautiful **in-browser error overlay** — Nexy should too.

## Target: Vite-quality error overlay
- Styled HTML with error details
- File path, line number, column number
- Error message clearly highlighted
- Dismissable (click to close)
- Auto-shown on compile failure
- Auto-dismissed on successful recompile

## Implementation

### Step 1: Create `nexy/utils/error_overlay.py`

```python
from html import escape


def render_error_overlay(
    source_path: str,
    message: str,
    line: int | None = None,
    column: int | None = None,
    error_type: str = "Compilation Error",
) -> str:
    """Render a dismissable in-browser error overlay.

    Styled like Vite/Nuxt error overlays: dark theme, monospace,
    clear file location, dismissable, auto-refresh hint.
    """
    location = ""
    if line is not None:
        location = f" at line {line}"
        if column is not None:
            location += f", column {column}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Nexy - {escape(error_type)}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
      background: #0a0a1a;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 2rem;
    }}
    .overlay {{
      background: #12122a;
      border: 1px solid #e94560;
      border-radius: 12px;
      max-width: 720px;
      width: 100%;
      padding: 2rem;
      box-shadow: 0 24px 80px rgba(233, 69, 96, 0.15);
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid #1e1e3a;
    }}
    .header-left {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}
    .error-badge {{
      background: #e94560;
      color: #fff;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      letter-spacing: 0.05em;
    }}
    h1 {{
      color: #e94560;
      font-size: 1.1rem;
      font-weight: 600;
    }}
    .close-btn {{
      background: none;
      border: none;
      color: #555;
      cursor: pointer;
      font-size: 1.3rem;
      line-height: 1;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      transition: all 0.15s;
    }}
    .close-btn:hover {{
      color: #fff;
      background: #1e1e3a;
    }}
    .file-path {{
      color: #8899bb;
      font-size: 0.8rem;
      margin-bottom: 0.25rem;
      word-break: break-all;
    }}
    .file-location {{
      color: #e94560;
      font-size: 0.8rem;
      margin-bottom: 1rem;
      font-weight: 500;
    }}
    .error-message {{
      background: #0d0d24;
      padding: 1rem 1.25rem;
      border-radius: 8px;
      border-left: 3px solid #e94560;
      color: #ffd369;
      font-size: 0.9rem;
      line-height: 1.6;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    .hint {{
      color: #556;
      font-size: 0.75rem;
      margin-top: 1rem;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="overlay" id="nexy-error-overlay">
    <div class="header">
      <div class="header-left">
        <span class="error-badge">ERROR</span>
        <h1>{escape(error_type)}</h1>
      </div>
      <button class="close-btn" onclick="this.closest('#nexy-error-overlay').remove()"
              title="Dismiss">&times;</button>
    </div>
    <div class="file-path">{escape(source_path)}</div>
    <div class="file-location">{escape(location.strip())}</div>
    <div class="error-message">{escape(message)}</div>
    <div class="hint">Fix the error and save — the page will reload automatically</div>
  </div>
</body>
</html>"""
```

### Step 2: Modify `nexy/builder/__init__.py`

**Add a class-level error store:**

```python
class Builder:
    last_error: "tuple[str, str, int | None, int | None] | None" = None
    
    def build(self, showlog: bool = False, incremental: bool = True) -> None:
        ...
        try:
            # Compile call
            ...
            # On success, clear last_error
            Builder.last_error = None
        except Exception as e:
            Builder.last_error = (
                input_path,
                str(e),
                getattr(e, 'lineno', None) or getattr(e, 'line', None),
                getattr(e, 'column', None),
            )
            ...
```

### Step 3: Modify `nexy/routers/app.py`

**Add error overlay endpoint for dev mode:**

Find the `AppServer` class and its route setup. Add a `/_nexy/error` endpoint:

```python
from nexy.utils.error_overlay import render_error_overlay
if self.config.DEV_MODE:
    @self.server.get("/_nexy/error", include_in_schema=False)
    async def nexy_error():
        from nexy.builder import Builder
        if Builder.last_error is not None:
            path, msg, line, col = Builder.last_error
            html = render_error_overlay(
                source_path=path,
                message=msg,
                line=line,
                column=col,
                error_type="Compilation Error",
            )
            return HTMLResponse(content=html, status_code=200)
        return HTMLResponse(content="", status_code=204)
```

### Step 4: Inject error-checking script in dev mode

In the same `app.py`, when in dev mode, inject a small script into every HTML response that polls `/_nexy/error`:

Find where responses are served. In the `FBRouter` or `app.py`, modify the response to inject the script:

```python
# In the main response handler for HTML pages in dev mode:
if self.config.DEV_MODE and isinstance(response, HTMLResponse):
    body = response.body.decode()
    # Check if we should inject the overlay script
    inject = (
        '<script>\n'
        ';(function(){const e=document.createElement("div");\n'
        'async function c(){try{const r=await fetch("/_nexy/error");\n'
        'if(r.status===200){document.body.prepend(e);\n'
        'e.innerHTML=await r.text()}else if(r.status===204&&e.parentNode)\n'
        'e.remove()}catch{}}\n'
        'setInterval(c,1500);c()\n'
        '})();\n'
        '</script>'
    )
    if "</body>" in body:
        body = body.replace("</body>", inject + "</body>")
        response = HTMLResponse(content=body, status_code=response.status_code)
```

### Step 5: Wire error overlay clearing on successful build

In `dev.py`, after a successful build triggered by file change:
```python
# Clear any previous error overlay
builder.last_error = None
```

## Write tests in `tests/unit/nexy/utils/test_error_overlay.py`

```python
import pytest
from nexy.utils.error_overlay import render_error_overlay


def test_render_error_overlay_returns_html():
    html = render_error_overlay("test.nexy", "Something went wrong")
    assert "<!DOCTYPE html>" in html
    assert "test.nexy" in html
    assert "Something went wrong" in html
    assert "ERROR" in html


def test_render_error_overlay_includes_line_column():
    html = render_error_overlay("test.nexy", "Bad syntax", line=5, column=12)
    assert "line 5" in html
    assert "column 12" in html


def test_render_error_overlay_escapes_html():
    html = render_error_overlay("<script>alert(1)</script>", "<b>bold</b>")
    assert "&lt;script&gt;" in html
    assert "&lt;b&gt;" in html
    assert "<script>" not in html


def test_render_error_overlay_uses_error_type():
    html = render_error_overlay("test.nexy", "msg", error_type="ImportError")
    assert "ImportError" in html
```

## Verify commands

```bash
# Test the error overlay rendering
python -m pytest tests/unit/nexy/utils/test_error_overlay.py -v

# Simulate a compile error:
# 1. Create a .nexy file with bad syntax
# 2. Run nx dev
# 3. Open browser → should see error overlay
# 4. Fix the file and save → overlay disappears

python -m pytest tests/ -v
```

## Definition of Done
- [ ] `render_error_overlay()` returns valid HTML with all fields
- [ ] HTML is properly escaped (no XSS)
- [ ] `/_nexy/error` endpoint serves error overlay HTML when build fails
- [ ] Browser page shows error overlay in dev mode on compile failure
- [ ] Fixing error and saving clears overlay
- [ ] Error overlay only active in dev mode (not production)
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
- [ ] `python -m pytest tests/ -v` — all pass
